# app/services/tip_service.py
from datetime import datetime
from typing import List, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.config.mongodb import get_database
from app.models.tip_model import TipCreate, TipInDB, TipResponse
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai_model = genai.GenerativeModel('gemini-pro')

async def get_general_tips(category: Optional[str] = None, limit: int = 5) -> List[TipResponse]:
    """
    Get general money-saving tips, optionally filtered by category.
    
    Args:
        category: Optional category to filter tips by
        limit: Maximum number of tips to return
        
    Returns:
        List of tips
    """
    db = get_database()
    
    # Build query
    query = {"is_personalized": False}
    if category:
        query["category"] = category
    
    # Get tips from database
    cursor = db.tips.find(query).sort("created_at", -1).limit(limit)
    tips = await cursor.to_list(length=limit)
    
    # If we don't have enough tips in the database, generate some
    if len(tips) < limit:
        needed_tips = limit - len(tips)
        generated_tips = await generate_general_tips(category, needed_tips)
        
        # Save generated tips to database
        if generated_tips:
            tip_docs = []
            for tip in generated_tips:
                tip_dict = {
                    "title": tip["title"],
                    "content": tip["content"],
                    "category": category if category else tip["category"],
                    "tags": tip.get("tags", []),
                    "is_personalized": False,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                tip_docs.append(tip_dict)
                
            if tip_docs:
                await db.tips.insert_many(tip_docs)
                
            # Get the newly inserted tips
            new_tips_cursor = db.tips.find(query).sort("created_at", -1).limit(limit)
            tips = await new_tips_cursor.to_list(length=limit)
    
    return tips

async def get_personalized_tips(user_id: str, category: Optional[str] = None, limit: int = 5) -> List[TipResponse]:
    """
    Get personalized money-saving tips based on user's spending patterns.
    
    Args:
        user_id: Firebase user ID
        category: Optional category to filter tips by
        limit: Maximum number of tips to return
        
    Returns:
        List of personalized tips
    """
    db = get_database()
    
    # First, get user's spending patterns from recent receipts
    spending_patterns = await analyze_user_spending(user_id)
    
    # Generate personalized tips based on spending patterns
    generated_tips = await generate_personalized_tips(user_id, spending_patterns, category, limit)
    
    # Save generated tips to database (if they don't already exist)
    tip_responses = []
    for tip in generated_tips:
        # Check if this exact tip already exists
        existing_tip = await db.tips.find_one({
            "title": tip["title"],
            "user_id": user_id,
            "is_personalized": True
        })
        
        if not existing_tip:
            tip_dict = {
                "title": tip["title"],
                "content": tip["content"],
                "category": category if category else tip["category"],
                "tags": tip.get("tags", []),
                "is_personalized": True,
                "user_id": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            result = await db.tips.insert_one(tip_dict)
            tip_dict["_id"] = result.inserted_id
            tip_responses.append(tip_dict)
        else:
            tip_responses.append(existing_tip)
    
    # If we don't have enough personalized tips, supplement with general tips
    if len(tip_responses) < limit:
        general_tips = await get_general_tips(category, limit - len(tip_responses))
        tip_responses.extend(general_tips)
    
    return tip_responses[:limit]

async def analyze_user_spending(user_id: str):
    """
    Analyze user's spending patterns to identify areas for improvement.
    
    Args:
        user_id: Firebase user ID
        
    Returns:
        Dictionary with spending pattern analysis
    """
    db = get_database()
    
    # Get user's recent receipts (last 30 days)
    thirty_days_ago = datetime.now() - datetime.timedelta(days=30)
    query = {
        "user_id": user_id,
        "date": {"$gte": thirty_days_ago}
    }
    
    receipts_cursor = db.receipts.find(query)
    receipts = await receipts_cursor.to_list(length=100)  # Limit to last 100 receipts for performance
    
    # Process receipts to extract spending patterns
    spending_by_category = {}
    frequent_stores = {}
    
    for receipt in receipts:
        # Track spending by category
        for item in receipt.get("items", []):
            category = item.get("category", "Uncategorized")
            if category not in spending_by_category:
                spending_by_category[category] = 0
            spending_by_category[category] += item.get("price", 0)
        
        # Track frequent stores
        store = receipt.get("store_name", "Unknown")
        if store not in frequent_stores:
            frequent_stores[store] = 0
        frequent_stores[store] += 1
    
    # Identify top spending categories
    top_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)
    
    # Identify most frequent stores
    top_stores = sorted(frequent_stores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "top_spending_categories": top_categories[:5],
        "frequent_stores": top_stores[:5],
        "total_spending": sum(spending_by_category.values())
    }

async def generate_general_tips(category: Optional[str] = None, count: int = 5):
    """
    Generate general money-saving tips using Gemini AI.
    
    Args:
        category: Optional category to focus tips on
        count: Number of tips to generate
        
    Returns:
        List of generated tips
    """
    try:
        category_prompt = f" for {category}" if category else ""
        
        prompt = f"""
        Generate {count} practical money-saving tips{category_prompt}. 
        For each tip, provide:
        1. A concise, actionable title (less than 10 words)
        2. Detailed advice (2-3 sentences)
        3. The relevant category (e.g., Groceries, Dining, Entertainment, Travel)
        4. 2-3 relevant tags
        
        Format the response as JSON array with this structure:
        [
          {{
            "title": "Tip title",
            "content": "Detailed advice",
            "category": "Category",
            "tags": ["tag1", "tag2"]
          }}
        ]
        
        Focus on practical, actionable advice that people can implement immediately.
        """
        
        response = genai_model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        json_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            tips = json.loads(json_str)
            return tips
        else:
            # Fallback to default tips if parsing fails
            return generate_fallback_tips(category, count)
    except Exception as e:
        print(f"Error generating tips: {str(e)}")
        return generate_fallback_tips(category, count)

async def generate_personalized_tips(user_id: str, spending_patterns: dict, category: Optional[str] = None, count: int = 5):
    """
    Generate personalized money-saving tips based on user's spending patterns.
    
    Args:
        user_id: Firebase user ID
        spending_patterns: Dictionary with user's spending analysis
        category: Optional category to focus tips on
        count: Number of tips to generate
        
    Returns:
        List of generated personalized tips
    """
    try:
        # Extract useful information from spending patterns
        top_categories = spending_patterns.get("top_spending_categories", [])
        frequent_stores = spending_patterns.get("frequent_stores", [])
        total_spending = spending_patterns.get("total_spending", 0)
        
        # Format data for the prompt
        top_categories_str = "\n".join([f"- {cat}: ${amount:.2f}" for cat, amount in top_categories[:3]])
        frequent_stores_str = ", ".join([store for store, _ in frequent_stores[:3]])
        
        category_prompt = f" for {category}" if category else ""
        
        prompt = f"""
        Generate {count} personalized money-saving tips{category_prompt} based on this spending data:
        
        Top spending categories:
        {top_categories_str}
        
        Frequent stores: {frequent_stores_str}
        
        Total monthly spending: ${total_spending:.2f}
        
        For each tip, provide:
        1. A concise, actionable title (less than 10 words)
        2. Personalized advice (2-3 sentences) referring to the specific spending patterns
        3. The relevant category (use one from the user's top categories if possible)
        4. 2-3 relevant tags
        
        Format the response as JSON array with this structure:
        [
          {{
            "title": "Tip title",
            "content": "Personalized advice",
            "category": "Category",
            "tags": ["tag1", "tag2"]
          }}
        ]
        
        Focus on practical, actionable advice that addresses the specific spending patterns.
        """
        
        response = genai_model.generate_content(prompt)
        
        # Extract JSON from response
        import json
        import re
        
        json_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            tips = json.loads(json_str)
            return tips
        else:
            # Fallback to general tips if parsing fails
            return await generate_general_tips(category, count)
    except Exception as e:
        print(f"Error generating personalized tips: {str(e)}")
        return await generate_general_tips(category, count)

def generate_fallback_tips(category: Optional[str] = None, count: int = 5):
    """
    Generate fallback tips when AI generation fails.
    
    Args:
        category: Optional category to filter tips by
        count: Number of tips to generate
        
    Returns:
        List of fallback tips
    """
    fallback_tips = {
        "Groceries": [
            {
                "title": "Plan Meals Around Weekly Sales",
                "content": "Check store flyers and plan your meals around discounted items. This simple habit can save you 20-30% on your grocery bill.",
                "category": "Groceries",
                "tags": ["meal planning", "discounts", "food"]
            },
            {
                "title": "Buy Seasonal Produce",
                "content": "Fruits and vegetables in season are typically cheaper and more flavorful. Shop at farmers' markets near closing time for additional discounts.",
                "category": "Groceries",
                "tags": ["produce", "seasonal", "shopping"]
            },
            {
                "title": "Use a Grocery List and Stick to It",
                "content": "Create a detailed shopping list before going to the store and commit to buying only what's on it. This prevents impulse purchases that can add up quickly.",
                "category": "Groceries",
                "tags": ["planning", "discipline", "shopping"]
            }
        ],
        "Dining": [
            {
                "title": "Pack Lunch Instead of Eating Out",
                "content": "Bringing lunch from home can save $50-$100 per week compared to buying daily. Prep multiple meals on weekends to make it convenient.",
                "category": "Dining",
                "tags": ["meal prep", "lunch", "work"]
            },
            {
                "title": "Use Restaurant Loyalty Programs",
                "content": "Sign up for loyalty programs at places you frequent. Many offer free items after a certain number of purchases or birthday rewards.",
                "category": "Dining",
                "tags": ["loyalty", "rewards", "discounts"]
            }
        ],
        "Entertainment": [
            {
                "title": "Explore Free Community Events",
                "content": "Check local community calendars for free concerts, festivals, and activities. Many museums also offer free admission days each month.",
                "category": "Entertainment",
                "tags": ["free", "community", "activities"]
            },
            {
                "title": "Rotate Streaming Services",
                "content": "Instead of subscribing to multiple streaming platforms simultaneously, rotate them monthly based on what you want to watch. This can cut your streaming costs by up to 75%.",
                "category": "Entertainment",
                "tags": ["streaming", "subscriptions", "media"]
            }
        ],
        "Shopping": [
            {
                "title": "Implement the 24-Hour Rule",
                "content": "For non-essential purchases over $50, wait 24 hours before buying. This cooling-off period often reduces impulse spending significantly.",
                "category": "Shopping",
                "tags": ["impulse control", "mindful spending", "discipline"]
            },
            {
                "title": "Use Price Tracking Tools",
                "content": "Apps like CamelCamelCamel or Honey can track price history and alert you to drops. Timing your purchases can save 10-40% on many items.",
                "category": "Shopping",
                "tags": ["tools", "price tracking", "timing"]
            }
        ],
        "General": [
            {
                "title": "Track Every Expense for One Month",
                "content": "Record every single purchase for 30 days to identify spending patterns. Most people find they can immediately cut 10-15% after seeing where their money goes.",
                "category": "General",
                "tags": ["awareness", "tracking", "budgeting"]
            },
            {
                "title": "Automate Savings Transfers",
                "content": "Set up automatic transfers to your savings account on payday. Treating savings as a non-negotiable expense ensures you consistently build your financial cushion.",
                "category": "General",
                "tags": ["automation", "savings", "habits"]
            },
            {
                "title": "Do a Subscription Audit",
                "content": "Review all your recurring subscriptions and cancel those you rarely use. Many people save $50-$100 monthly by eliminating forgotten or underused services.",
                "category": "General",
                "tags": ["subscriptions", "recurring costs", "audit"]
            }
        ]
    }
    
    # Select appropriate category tips
    if category and category in fallback_tips:
        tips = fallback_tips[category]
    else:
        # Combine tips from all categories
        tips = []
        for cat_tips in fallback_tips.values():
            tips.extend(cat_tips)
    
    # Ensure we don't return more than requested
    return tips[:count]