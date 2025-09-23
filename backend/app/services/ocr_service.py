import base64
import os
import time
import asyncio
from typing import Dict, Any
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API with your API key - load from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

async def process_receipt_image(image_data: str, is_base64: bool = False) -> Dict[str, Any]:
    """
    Process receipt image using Gemini Vision API with retry logic
    
    Args:
        image_data: Base64 encoded image string or file path
        is_base64: If True, treat image_data as base64, otherwise as file path
        
    Returns:
        Extracted receipt data
    """
    max_retries = 3
    base_delay = 1  # Start with 1 second delay
    
    for attempt in range(max_retries):
        try:
            if is_base64:
                # Handle base64 image data
                if ',' in image_data:
                    image_bytes = base64.b64decode(image_data.split(',')[1])
                else:
                    image_bytes = base64.b64decode(image_data)
            else:
                # Handle file path
                with open(image_data, 'rb') as image_file:
                    image_bytes = image_file.read()
            
            # Initialize Gemini Pro Flash model (faster than pro-vision)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Create prompt for receipt extraction
            prompt = """
            Analyze this receipt image and extract the following information:
            - Store name
            - Date (in YYYY-MM-DD format)
            - Total amount
            - List of items with their names, prices, and if possible categories
            
            Format your response as a JSON object with these keys:
            {
              "store_name": "Store Name",
              "date": "YYYY-MM-DD",
              "total_amount": 123.45,
              "items": [
                {
                  "name": "Item name",
                  "price": 12.34,
                  "quantity": 1,
                  "category": "groceries"
                },
                ...
              ]
            }
            Return only the JSON object, nothing else.
            """
            
            # Generate content with the image (shorter timeout)
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        model.generate_content,
                        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
                    ),
                    timeout=30.0  # Reduced timeout to 30 seconds
                )
            except asyncio.TimeoutError:
                raise Exception("Request timed out after 30 seconds")
            
            # Parse the response text as JSON
            import json
            result_text = response.text
            # Clean the response to handle potential formatting issues
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0].strip()
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(result_text)
            
            # Convert date string to datetime
            if 'date' in result and result['date']:
                try:
                    result['date'] = datetime.fromisoformat(result['date'])
                except ValueError:
                    # Handle different date formats
                    from dateutil import parser
                    result['date'] = parser.parse(result['date'])
            
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Error processing receipt with Gemini (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            # Check if it's a retryable error
            if any(keyword in error_msg for keyword in ['overloaded', '503', 'deadline', 'timeout', 'rate limit']):
                if attempt < max_retries - 1:  # Don't wait after the last attempt
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
            
            # For non-retryable errors or after max retries, return fallback data
            print(f"Providing fallback data due to persistent errors")
            return {
                "error": f"AI service temporarily unavailable. Please enter receipt details manually.",
                "store_name": "Unknown Store",
                "date": datetime.now(),
                "total_amount": 0,
                "items": [
                    {
                        "name": "Please add items manually",
                        "price": 0.0,
                        "quantity": 1,
                        "category": "other"
                    }
                ],
                "manual_entry_required": True
            }
    
    # If we somehow exit the loop without returning, provide fallback
    return {
        "error": "Unexpected error occurred",
        "store_name": "Unknown Store", 
        "date": datetime.now(),
        "total_amount": 0,
        "items": [],
        "manual_entry_required": True
    }