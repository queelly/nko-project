import aiohttp
import json
import ssl
import urllib3
from app.config import Config

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def generate_text(prompt: str, style: str = "разговорный", nko_data: dict = None) -> str:
    """Генерация текста через OpenRouter API с основной моделью"""
    return await generate_with_openrouter(prompt, style, nko_data)

async def generate_with_openrouter(prompt: str, style: str, nko_data: dict) -> str:
    """Генерация через OpenRouter API с основной моделью"""
    
    if not Config.OPENROUTER_API_KEY or Config.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        return generate_fallback_text(prompt, style, nko_data)
    
    # Сначала пробуем основную модель, потом резервные
    models_to_try = [Config.OPENROUTER_MODEL] + Config.FALLBACK_MODELS
    
    # Формируем системный промпт с учетом стиля и данных НКО
    system_prompt = create_system_prompt(style, nko_data)
    
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/nko-bot",
        "X-Title": "NKO Content Bot"
    }
    
    # Пробуем модели по порядку
    for model in models_to_try:
        try:
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            # Создаем SSL контекст который игнорирует ошибки сертификатов
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(openrouter_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        generated_text = result['choices'][0]['message']['content']
                        print(f"✅ Успешная генерация с моделью: {model}")
                        return format_generated_text(generated_text, prompt, nko_data)
                    else:
                        print(f"❌ Модель {model} недоступна: {response.status}")
                        continue
                        
        except Exception as e:
            print(f"❌ Ошибка с моделью {model}: {e}")
            continue
    
    # Если все модели не сработали
    print("❌ Все модели недоступны, используем fallback")
    return generate_fallback_text(prompt, style, nko_data)

# Остальные функции (create_system_prompt, format_generated_text, generate_fallback_text)
# остаются без изменений

def create_system_prompt(style: str, nko_data: dict) -> str:
    """Создает системный промпт на основе стиля и данных НКО"""
    
    style_descriptions = {
        "разговорный": "Неформальный, дружелюбный стиль, как в личном общении",
        "официальный": "Официально-деловой стиль, вежливый и структурированный", 
        "художественный": "Творческий, образный стиль с эмоциональной окраской"
    }
    
    nko_context = ""
    if nko_data and nko_data.get('has_nko_info'):
        nko_context = f"""
Контекст организации:
- Название: {nko_data.get('nko_name', 'Не указано')}
- Деятельность: {nko_data.get('nko_description', 'Не указано')}
- Направления: {nko_data.get('nko_activities', 'Не указано')}
"""
    
    system_prompt = f"""Ты помощник по созданию контента для некоммерческих организаций (НКО). 

Требования к тексту:
1. Стиль: {style_descriptions.get(style, 'разговорный')}
2. Текст должен быть лаконичным и читаемым
3. Добавь 3-5 релевантных хештегов в конце
4. Текст должен вызывать доверие и эмоциональный отклик
5. Избегай сложных терминов, объясняй простыми словами

{nko_context}

Формат ответа: готовый текст поста без дополнительных пояснений."""
    
    return system_prompt

def format_generated_text(text: str, original_prompt: str, nko_data: dict) -> str:
    """Форматирует сгенерированный текст для отправки пользователю"""
    
    nko_info = ""
    if nko_data and nko_data.get('nko_name'):
        nko_info = f" для {nko_data['nko_name']}"
    
    return f"""📝 <b>Сгенерированный текст{nko_info}</b>

{text}

💡 <i>На основе запроса: "{original_prompt}"</i>"""

def generate_fallback_text(prompt: str, style: str, nko_data: dict) -> str:
    """Качественная заглушка на случай ошибки API"""
    from app.services.ai_text_sync import generate_fallback_text as sync_fallback
    return sync_fallback(prompt, style, nko_data)