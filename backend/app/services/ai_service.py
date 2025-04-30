# app/services/ai_service.py
import os
import google.generativeai as genai
from PIL import Image
import re
from dotenv import load_dotenv
from typing import List, Dict, Optional
from app.models.receipt_model import ReceiptItem
from datetime import datetime, timedelta
from app.database import get_database

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')
text_model = genai.GenerativeModel('gemini-pro')

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/jpg'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_image(image_path: str) -> bool:
    """Validate image type and size."""
    try:
        # Check file size
        if os.path.getsize(image_path) > MAX_IMAGE_SIZE:
            return False
        
        # Check file type
        with Image.open(image_path) as img:
            if img.format.lower() not in ['jpeg', 'png', 'jpg']:
                return False
        
        return True
    except Exception:
        return False

async def extract_text_from_image(image_path: str) -> str:
    """Extract text from receipt image using Gemini AI."""
    if not await validate_image(image_path):
        raise ValueError("Invalid image format or size")
    
    try:
        # Open image
        img = Image.open(image_path)
        
        # Prepare prompt
        prompt = """
        Please extract all items from this receipt image. 
        For each item, provide the name, price, and quantity if available.
        Format the output as a list with each item on a new line in this format:
        - Item name: $price (quantity: X)
        If you can't read some items clearly, make your best guess and mark it with (uncertain).
        Also extract the store name and total amount if visible.
        """
        
        # Generate content with Gemini
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

async def categorize_items(items_text: str) -> List[ReceiptItem]:
    """Parse and categorize receipt items using Gemini AI."""
    try:
        # Extract items from the text
        item_pattern = r"- (.*?): \$([\d.]+)(?: \(quantity: (\d+)\))?"
        extracted_items = re.findall(item_pattern, items_text)
        
        if not extracted_items:
            raise Exception("Failed to extract any items from the receipt")
        
        # Prepare items for categorization
        items_for_categorization = "\n".join([f"{item[0]}" for item in extracted_items])
        
        # Prepare prompt for categorization
        categorize_prompt = f"""
        Please categorize these items into common budget categories like:
        - Groceries
        - Dining Out
        - Entertainment
        - Transportation
        - Shopping
        - Utilities
        - Health
        - Education
        - Travel
        - Other
        
        For each item, provide a category.
        Format the output as a list with each item on a new line in this format:
        - Item name: Category
        
        Here are the items:
        {items_for_categorization}
        """
        
        # Generate categorization with Gemini
        category_response = text_model.generate_content(categorize_prompt)
        
        # Extract categorizations
        category_pattern = r"- (.*?): ([\w\s]+)"
        categorizations = dict(re.findall(category_pattern, category_response.text))
        
        # Create receipt items with categories
        receipt_items = []
        for name, price, quantity in extracted_items:
            receipt_items.append(ReceiptItem(
                name=name.strip(),
                price=float(price),
                quantity=float(quantity) if quantity else 1.0,
                category=categorizations.get(name.strip(), "Other")
            ))
        
        return receipt_items
    except Exception as e:
        raise Exception(f"Error categorizing items: {str(e)}")

async def generate_saving_tips(user_id: str) -> List[Dict]:
    """Generate personalized saving tips based on user's spending patterns."""
    try:
        db = await get_database()
        
        # Get user's recent spending data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        receipts = await db.receipts.find({
            "user_id": user_id,
            "date": {"$gte": thirty_days_ago}
        }).to_list(length=None)
        
        # Analyze spending patterns
        category_spending = {}
        for receipt in receipts:
            for item in receipt["items"]:
                category = item["category"]
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += item["price"]
        
        # Prepare data for AI analysis
        spending_analysis = "\n".join([
            f"{category}: ${amount:.2f}"
            for category, amount in category_spending.items()
        ])
        
        # Generate personalized tips
        tips_prompt = f"""
        Based on the following spending patterns over the last 30 days:
        {spending_analysis}
        
        Please provide 5 personalized saving tips. For each tip:
        1. Reference the specific spending category
        2. Provide actionable advice
        3. Include potential savings estimate
        4. Make it specific to the user's spending habits
        
        Format each tip as a JSON object with:
        - category: the spending category it addresses
        - tip: the saving advice
        - potential_savings: estimated monthly savings
        - action_items: list of specific actions to take
        """
        
        response = text_model.generate_content(tips_prompt)
        
        # Parse the response into structured tips
        tips = []
        tip_pattern = r'\{.*?\}'
        for tip_json in re.findall(tip_pattern, response.text):
            try:
                tip = eval(tip_json)  # Safe in this context as we control the input
                tips.append(tip)
            except:
                continue
        
        return tips
    except Exception as e:
        raise Exception(f"Error generating saving tips: {str(e)}")

async def track_tip_effectiveness(user_id: str, tip_id: str, implemented: bool, savings: float):
    """Track the effectiveness of implemented tips."""
    try:
        db = await get_database()
        await db.tip_effectiveness.insert_one({
            "user_id": user_id,
            "tip_id": tip_id,
            "implemented": implemented,
            "savings": savings,
            "date": datetime.now()
        })
    except Exception as e:
        raise Exception(f"Error tracking tip effectiveness: {str(e)}")