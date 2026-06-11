from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.services.deepseek_chat import deepseek_chat

router = APIRouter(prefix="/recipes", tags=["recipes"])

# Fallback recipes if API fails
FALLBACK_RECIPES = [
    {"name": "Pap & Chakalaka", "cost": 15, "time": 20, "ingredients": ["pap", "chakalaka", "onion"], "instructions": "Boil water, add pap. Fry onion, add chakalaka."},
    {"name": "Umngqusho (Samp & Beans)", "cost": 20, "time": 45, "ingredients": ["samp", "beans", "onion"], "instructions": "Soak overnight. Boil until soft. Fry onion, combine."},
    {"name": "Cabbage Curry", "cost": 12, "time": 25, "ingredients": ["cabbage", "onion", "tomato", "curry powder"], "instructions": "Fry onion, add cabbage, tomato, curry. Simmer 15 min."},
    {"name": "Bean Stew", "cost": 15, "time": 35, "ingredients": ["beans", "onion", "tomato"], "instructions": "Fry onion, add tomato, beans. Simmer 20 min."},
    {"name": "Potato & Egg Curry", "cost": 18, "time": 30, "ingredients": ["potatoes", "eggs", "onion", "curry powder"], "instructions": "Boil potatoes and eggs. Fry onion, add curry, potatoes, eggs."},
    {"name": "Vetkoek & Mince", "cost": 22, "time": 40, "ingredients": ["flour", "yeast", "mince", "onion"], "instructions": "Make dough, fry balls. Cook mince. Stuff vetkoek."},
    {"name": "Dumpling Soup", "cost": 10, "time": 25, "ingredients": ["flour", "water", "salt", "vegetables"], "instructions": "Make dough drops. Boil in salted water with vegetables."},
    {"name": "Pap & Gravy", "cost": 10, "time": 15, "ingredients": ["pap", "tomato", "onion"], "instructions": "Make pap. Fry onion, tomato for gravy."},
]

@router.get("/")
async def get_recipes(limit: int = 5, language: str = "english", user=Depends(get_current_user)):
    """Get budget recipes for needy tier (R19/month)"""
    # Try DeepSeek first for personalized recipes
    try:
        result = await deepseek_chat(
            f"Give me {limit} budget South African recipes under R30 using common ingredients like pap, beans, cabbage, potatoes.",
            portal="recipe_generator",
            language=language
        )
        return {"recipes": result["response"], "source": "ai"}
    except:
        return {"recipes": FALLBACK_RECIPES[:limit], "source": "fallback"}
