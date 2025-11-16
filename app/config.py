import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class Config:
    BOT_TOKEN = BOT_TOKEN
    OPENROUTER_API_KEY = OPENROUTER_API_KEY
    ADMIN_IDS = [799744633]  # Замени на свой ID
    
    # Основная модель
    OPENROUTER_MODEL = "qwen/qwen3-4b:free"
    
    # Резервные модели
    FALLBACK_MODELS = [
        
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "mistralai/mistral-nemo:free",             
        "qwen/qwen-2.5-72b-instruct:free",
        "deepseek/deepseek-chat-v3.1:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "mistralai/mistral-small-24b-instruct-2501:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-3-4b-it:free",
        "google/gemma-3n-e4b-it:free",
        "tngtech/deepseek-r1t2-chimera:free",
        "z-ai/glm-4.5-air:free",
        "qwen/qwen3-coder:free"
    ]
    
    # Настройки для генерации изображений
    IMAGE_SETTINGS = {
        "width": 512,
        "height": 512,
        "num_inference_steps": 25
    }
    
    # Настройки для текстовых шаблонов
    TEMPLATE_SETTINGS = {
        "max_post_length": 2000,
        "default_hashtags": ["#НКО", "#Помощь", "#Добро", "#СоциальныйПроект"]
    }
    
    # Настройки персонажа
    CHARACTER_SETTINGS = {
        "name": "Добробот",
        "emoji": "🐱",
        "default_style": "разговорный"
    }
    
    # Настройки путей
    PATHS = {
        "data": "data",
        "images": "data/images",
        "favorites": "data/favorites.json",
        "logs": "logs"
    }