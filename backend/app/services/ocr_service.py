import base64
import os
from typing import Dict, Any
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API with your API key - load from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

async def process_receipt_image(image_data: str) -> Dict[str, Any]:
    """
    Process receipt image using Gemini Vision API
    
    Args:
        image_data: Base64 encoded image string
        
    Returns:
        Extracted receipt data
    """
    try:
        # Decode base64 image if it contains the data URL prefix
        if ',' in image_data:
            image_bytes = base64.b64decode(image_data.split(',')[1])
        else:
            image_bytes = base64.b64decode(image_data)
        
        # Initialize Gemini Pro Vision model
        model = genai.GenerativeModel('gemini-pro-vision')
        
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
        
        # Generate content with the image
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_bytes}])
        
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
        print(f"Error processing receipt with Gemini: {str(e)}")
        return {
            "error": str(e),
            "store_name": None,
            "date": datetime.now(),
            "total_amount": 0,
            "items": []
        }