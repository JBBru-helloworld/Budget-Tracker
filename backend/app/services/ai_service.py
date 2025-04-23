# app/services/ai_service.py
import os
import google.generativeai as genai
from PIL import Image
import re
from dotenv import load_dotenv
from typing import List
from app.models.receipt_model import ReceiptItem

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')

async def extract_text_from_image(image_path):
    """Extract text from receipt image using Gemini AI."""
    try:
        # Open image
        img = Image.open(image_path)
        
        # Prepare prompt
        prompt = """
        Please extract all items from this receipt image. 
        For each item, provide the name and price. 
        Format the output as a list with each item on a new line in this format:
        - Item name: $price
        If you can't read some items clearly, make your best guess and mark it with (uncertain).
        """
        
        # Generate content with Gemini
        response = model.generate_content([prompt, img])
        
        return response.text
    except Exception as e:
        raise Exception(f"Error extracting text from image: {str(e)}")

async def categorize_items(items_text):
    """Parse and categorize receipt items using Gemini AI."""
    try:
        # Extract items from the text
        item_pattern = r"- (.*?): \$([\d.]+)"
        extracted_items = re.findall(item_pattern, items_text)
        
        if not extracted_items:
            raise Exception("Failed to extract any items from the receipt")
        
        # Prepare items for categorization
        items_for_categorization = "\n".join([f"{item[0]}" for item in extracted_items])
        
        # Prepare prompt for categorization
        categorize_prompt = f"""
        Please categorize these items into common budget categories like Groceries, Dining, Entertainment, etc.
        For each item, provide a category.
        Format the output as a list with each item on a new line in this format:
        - Item name: Category
        
        Here are the items:
        {items_for_categorization}
        """
        
        # Generate categorization with Gemini
        categorization_model = genai.GenerativeModel('gemini-pro')
        category_response = categorization_model.generate_content(categorize_prompt)
        
        # Extract categorizations
        category_pattern = r"- (.*?): ([\w\s]+)"
        categorizations = dict(re.findall(category_pattern, category_response.text))
        
        # Create receipt items with categories
        receipt_items = []
        for name, price in extracted_items:
            receipt_items.append(ReceiptItem(
                name=name.strip(),
                price=float(price),
                category=categorizations.get(name.strip(), "Uncategorized")
            ))
        
        return receipt_items
    except Exception as e:
        raise Exception(f"Error categorizing items: {str(e)}")