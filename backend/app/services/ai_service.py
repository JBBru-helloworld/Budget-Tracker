# backend/app/services/ai_service.py
import google.generativeai as genai
from fastapi import UploadFile
from ..config import settings
from ..models.models import ReceiptItem, Category
from datetime import datetime
import json
import io
import base64
from PIL import Image

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

async def process_receipt_image(receipt_image: UploadFile, store_name: str, date: datetime) -> dict:
    """
    Process an uploaded receipt image using Google's Gemini API
    
    Args:
        receipt_image: Uploaded receipt image file
        store_name: Name of the store
        date: Date of the receipt
        
    Returns:
        dict: Processed receipt data including items, total amount, and raw text
    """
    try:
        # Read image file
        contents = await receipt_image.read()
        image = Image.open(io.BytesIO(contents))
        
        # Reset file position for future reads
        await receipt_image.seek(0)
        
        # Create a Gemini model instance
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Prepare the image for the model
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=image.format)
        image_bytes = image_bytes.getvalue()
        
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt for Gemini with clear instructions
        prompt = f"""
        Please analyze this receipt image from {store_name} dated {date.strftime('%Y-%m-%d')}.
        
        Extract the following information in JSON format:
        1. List of items (products/services) with their:
           - name: Full product name or description
           - price: Price in numeric format (e.g., 12.99 not $12.99)
           - quantity: Number of items (default to 1 if not specified)
           - category: Categorize into one of: food, clothing, recreation, transportation, housing, utilities, healthcare, education, personal, other
        2. total_amount: Total amount of the receipt (numeric format)
        
        Format the response as valid JSON with this structure:
        {{
            "items": [
                {{
                    "name": "item name",
                    "price": price,
                    "quantity": quantity,
                    "category": "category"
                }}
            ],
            "total_amount": total,
            "raw_text": "full text from receipt"
        }}
        
        Important: Ensure the JSON is valid, with numbers as numeric values (not strings).
        Include the raw text found on the receipt in the raw_text field.
        """
        
        # Generate content
        response = model.generate_content([prompt, {
            "mime_type": f"image/{receipt_image.content_type.split('/')[-1]}",
            "data": image_base64
        }])
        
        # Parse the response
        ai_response = response.text
        
        # Try to find and extract the JSON part
        try:
            # Extract JSON content (between triple backticks if present)
            if "```json" in ai_response and "```" in ai_response.split("```json")[1]:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response and "```" in ai_response.split("```")[1]:
                json_str = ai_response.split("```")[1].split("```")[0].strip()
            else:
                json_str = ai_response.strip()
                
            receipt_data = json.loads(json_str)
            
            # Ensure proper data structure
            if "items" not in receipt_data or "total_amount" not in receipt_data:
                raise ValueError("Invalid receipt data format")
                
            # Convert categories to enum values
            for item in receipt_data["items"]:
                item["category"] = item["category"].lower()
                if item["category"] not in [cat.value for cat in Category]:
                    item["category"] = Category.OTHER.value
            
            return receipt_data
        
        except json.JSONDecodeError:
            # If JSON parsing fails, try another approach with a more structured prompt
            model = genai.GenerativeModel('gemini-pro-vision')
            
            structured_prompt = f"""
            Analyze this receipt image and extract items, prices, and total amount.
            
            For each item line on the receipt, provide:
            1. Item name
            2. Item price (as a number)
            3. Quantity (default to 1)
            4. Category (one of: food, clothing, recreation, transportation, housing, utilities, healthcare, education, personal, other)
            
            Also extract the total amount.
            
            Format your response as a list of items with their details, followed by the total amount.
            """
            
            raw_response = model.generate_content([structured_prompt, {
                "mime_type": f"image/{receipt_image.content_type.split('/')[-1]}",
                "data": image_base64
            }])
            
            # Process the raw response into structured data
            raw_text = raw_response.text
            
            # Use a third prompt to process the raw text into proper JSON format
            text_model = genai.GenerativeModel('gemini-pro')
            json_prompt = f"""
            Convert the following receipt text into a valid JSON structure:
            
            {raw_text}
            
            Format as:
            {{
                "items": [
                    {{
                        "name": "item name",
                        "price": price,
                        "quantity": quantity,
                        "category": "category"
                    }}
                ],
                "total_amount": total,
                "raw_text": "{raw_text}"
            }}
            
            Important: Ensure the JSON is valid, with numbers as numeric values (not strings).
            """
            
            json_response = text_model.generate_content(json_prompt)
            
            # Try to extract and parse the JSON
            try:
                if "```json" in json_response.text:
                    json_str = json_response.text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_response.text:
                    json_str = json_response.text.split("```")[1].split("```")[0].strip
                    json_str = json_response.text.split("```")[1].split("```")[0].strip()
                else:
                    json_str = json_response.text.strip()
                    
                receipt_data = json.loads(json_str)
                
                # Validate the data structure
                if "items" not in receipt_data or "total_amount" not in receipt_data:
                    raise ValueError("Invalid receipt data format")
                    
                # Make sure raw_text is included
                if "raw_text" not in receipt_data:
                    receipt_data["raw_text"] = raw_text
                
                # Convert categories to enum values
                for item in receipt_data["items"]:
                    item["category"] = item["category"].lower()
                    if item["category"] not in [cat.value for cat in Category]:
                        item["category"] = Category.OTHER.value
                
                return receipt_data
                
            except (json.JSONDecodeError, ValueError) as e:
                # As a last resort, create a minimally structured response
                return {
                    "items": [
                        {
                            "name": "Unspecified Item",
                            "price": 0.0,
                            "quantity": 1,
                            "category": Category.OTHER.value
                        }
                    ],
                    "total_amount": 0.0,
                    "raw_text": raw_text
                }
    
    except Exception as e:
        raise Exception(f"Error processing receipt with Gemini AI: {str(e)}")

async def generate_saving_tips(user_id: str, spending_data: dict) -> list:
    """
    Generate personalized money-saving tips based on user's spending patterns
    
    Args:
        user_id: User ID
        spending_data: User's spending data by category
        
    Returns:
        list: List of money-saving tips
    """
    try:
        # Create a Gemini model instance
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare the prompt
        categories_str = ""
        for category, amount in spending_data.items():
            categories_str += f"- {category}: ${amount:.2f}\n"
        
        prompt = f"""
        Based on the following spending pattern, generate 3-5 personalized money-saving tips:
        
        {categories_str}
        
        For each tip, provide:
        1. A relevant category (one of: food, clothing, recreation, transportation, housing, utilities, healthcare, education, personal, other)
        2. A short, catchy title (5-7 words)
        3. A helpful, actionable description (1-3 sentences)
        
        Format your response as valid JSON with this structure:
        [
            {{
                "category": "category_name",
                "title": "Tip title",
                "description": "Detailed tip description"
            }}
        ]
        
        Important: Ensure the JSON is valid. Make tips specific and actionable.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Try to extract and parse the JSON
        try:
            if "```json" in response.text:
                json_str = response.text.split("```json")[1].split("```")[0].strip()
            elif "```" in response.text:
                json_str = response.text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.text.strip()
                
            tips_data = json.loads(json_str)
            
            # Validate the tips
            for tip in tips_data:
                if not all(key in tip for key in ["category", "title", "description"]):
                    continue
                    
                # Convert category to lowercase and validate
                tip["category"] = tip["category"].lower()
                if tip["category"] not in [cat.value for cat in Category]:
                    tip["category"] = Category.OTHER.value
            
            return tips_data
            
        except json.JSONDecodeError:
            # Return a default tip if JSON parsing fails
            return [
                {
                    "category": Category.OTHER.value,
                    "title": "Track Your Daily Expenses",
                    "description": "Keep a daily record of all expenses to identify unnecessary spending patterns."
                },
                {
                    "category": Category.FOOD.value,
                    "title": "Plan Meals to Reduce Food Waste",
                    "description": "Creating a weekly meal plan can save money by reducing food waste and preventing impulse purchases."
                }
            ]
    
    except Exception as e:
        raise Exception(f"Error generating saving tips with Gemini AI: {str(e)}")