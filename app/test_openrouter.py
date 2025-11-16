#!/usr/bin/env python3
"""
Тест OpenRouter с гарантированно работающей моделью
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_openrouter():
    """Тестируем OpenRouter с разными моделями"""
    from app.services.ai_text import generate_text
    
    test_models = [
        "meta-llama/llama-3.3-70b-instruct:free"
    ]
    
    for model in test_models:
        print(f"\n🔍 Тестируем модель: {model}")
        
        # Временно меняем модель в конфиге
        from app.config import Config
        original_model = Config.OPENROUTER_MODEL
        Config.OPENROUTER_MODEL = model
        
        try:
            result = await generate_text("тестовый пост о благотворительности", "разговорный", {})
            print(f"✅ {model} - РАБОТАЕТ!")
            print(f"Результат: {result[:200]}...")
        except Exception as e:
            print(f"❌ {model} - ошибка: {e}")
        
        # Возвращаем оригинальную модель
        Config.OPENROUTER_MODEL = original_model

if __name__ == "__main__":
    asyncio.run(test_openrouter())