import requests
import json
import urllib3
import time
import hashlib
from datetime import datetime, timedelta
from app.config import Config

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TextCache:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
    
    def get_cache_key(self, prompt: str, style: str, nko_data: dict) -> str:
        data_string = f"{prompt}_{style}_{json.dumps(nko_data, sort_keys=True) if nko_data else '{}'}"
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def get(self, key: str):
        if key in self.cache:
            cached_data = self.cache[key]
            if datetime.now() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['result']
        return None
    
    def set(self, key: str, result: str):
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }

text_cache = TextCache()

def generate_text_sync(prompt: str, style: str = "разговорный", nko_data: dict = None) -> str:
    """Синхронная версия генерации текста через OpenRouter API"""
    
    # Проверяем кэш
    cache_key = text_cache.get_cache_key(prompt, style, nko_data or {})
    cached_result = text_cache.get(cache_key)
    
    if cached_result:
        print("✅ Использован кэшированный результат")
        return cached_result
    
    if not Config.OPENROUTER_API_KEY:
        result = generate_fallback_text(prompt, style, nko_data)
        text_cache.set(cache_key, result)
        return result
    
    system_prompt = create_system_prompt(style, nko_data)
    
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/nko-bot",
        "X-Title": "NKO Content Bot"
    }
    
    # Сначала пробуем основную модель, потом резервные
    models_to_try = [Config.OPENROUTER_MODEL] + Config.FALLBACK_MODELS
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
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
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                response = requests.post(openrouter_url, headers=headers, json=data, timeout=30, verify=False)
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result['choices'][0]['message']['content']
                    print(f"✅ Успешная генерация с моделью: {model}")
                    
                    # Очищаем текст от возможных технических пояснений
                    cleaned_text = clean_generated_text(generated_text, prompt)
                    
                    formatted_text = format_generated_text(cleaned_text, prompt, nko_data, model)
                    text_cache.set(cache_key, formatted_text)
                    return formatted_text
                else:
                    print(f"❌ Модель {model} недоступна: {response.status_code}")
                    if "non-serverless" in response.text:
                        print(f"⚠️ Модель {model} требует dedicated endpoint, пробуем следующую...")
                    continue
                    
            except requests.exceptions.ConnectionError as e:
                print(f"❌ Ошибка соединения с моделью {model} (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except requests.exceptions.Timeout as e:
                print(f"❌ Таймаут с моделью {model} (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            except Exception as e:
                print(f"❌ Ошибка с моделью {model}: {e}")
                continue
    
    # Если все модели не сработали
    print("❌ Все модели недоступны, используем fallback")
    result = generate_fallback_text(prompt, style, nko_data)
    text_cache.set(cache_key, result)
    return result

def clean_generated_text(generated_text: str, original_prompt: str) -> str:
    """Очищает сгенерированный текст от технических пояснений и исходного промпта"""
    # Удаляем упоминания исходного промпта
    lines = generated_text.split('\n')
    cleaned_lines = []
    
    skip_next = False
    for line in lines:
        # Пропускаем строки, которые содержат технические пояснения
        if any(phrase in line.lower() for phrase in [
            'на основе запроса', 
            'исходный текст',
            'текст для проверки',
            'анализ должен включать',
            'формат ответа',
            'исправленный текст:',
            'орфографические ошибки:',
            'грамматические ошибки:',
            'стилистические улучшения:',
            'рекомендации по структуре:',
            'подходящие хештеги:'
        ]):
            continue
        
        # Пропускаем строки с исходным промптом
        if original_prompt and original_prompt[:50] in line:
            continue
            
        # Пропускаем строки после определенных маркеров
        if 'запрос:' in line.lower() or 'prompt:' in line.lower():
            skip_next = True
            continue
            
        if skip_next and line.strip() == '':
            skip_next = False
            continue
            
        if not skip_next:
            cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Удаляем двойные переносы строк
    while '\n\n\n' in cleaned_text:
        cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
    
    return cleaned_text

def translate_text_sync(text: str) -> str:
    """Синхронный перевод текста с русского на английский"""
    if not Config.OPENROUTER_API_KEY:
        return None
    
    # Сначала пробуем основную модель, потом резервные
    translation_models = [Config.OPENROUTER_MODEL] + Config.FALLBACK_MODELS
    
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/nko-bot",
        "X-Title": "NKO Content Bot"
    }
    
    system_prompt = """You are a professional translator. 
Translate the following Russian text to English accurately while preserving the meaning and context. 
Return ONLY the translation without any additional text, explanations, or notes."""
    
    # Пробуем модели по порядку
    for model in translation_models:
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
                        "content": text
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(openrouter_url, headers=headers, json=data, timeout=30, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result['choices'][0]['message']['content'].strip()
                print(f"✅ Успешный перевод с моделью {model}: {translated_text}")
                return translated_text
            else:
                print(f"❌ Модель {model} недоступна для перевода: {response.status_code}")
                continue
                
        except Exception as e:
            print(f"❌ Ошибка перевода с моделью {model}: {e}")
            continue
    
    return None

def create_system_prompt(style: str, nko_data: dict) -> str:
    """Создает системный промпт на основе стиля и данных НКО"""
    
    style_descriptions = {
        "разговорный": "Неформальный, дружелюбный стиль, как в личном общении",
        "официальный": "Официально-деловой стиль, вежливый и структурированный", 
        "художественный": "Творческий, образный стиль с эмоциональной окраской",
        "эмоциональный": "Эмоциональный, выразительный стиль с акцентом на чувства"
    }
    
    nko_context = ""
    if nko_data and nko_data.get('has_nko_info'):
        nko_context = f"""
КОНТЕКСТ НКО ДЛЯ ПЕРСОНАЛИЗАЦИИ КОНТЕНТА:
- Название организации: {nko_data.get('nko_name', 'Не указано')}
- Миссия и цель: {nko_data.get('nko_mission', 'Не указано')}
- Основные направления деятельности: {nko_data.get('nko_activities', 'Не указано')}
- Целевая аудитория: {nko_data.get('nko_audience', 'Не указано')}

ИСПОЛЬЗУЙ ЭТУ ИНФОРМАЦИЮ ДЛЯ:
1. Упоминания названия организации в подходящем контексте
2. Связи контента с миссией организации
3. Адаптации стиля под целевую аудиторию
4. Использования релевантной терминологии
5. Создания персонализированных примеров и кейсов

"""
    
    system_prompt = f"""Ты помощник по созданию контента для некоммерческих организаций (НКО). 

{nko_context}

ВАЖНЫЕ ПРАВИЛА:
1. НИКОГДА не включай в ответ исходный запрос пользователя
2. НИКОГДА не упоминай промпт или инструкции в ответе
3. НИКОГДА не добавляй технические пояснения типа "На основе вашего запроса"
4. Отвечай ТОЛЬКО готовым контентом без лишних комментариев

ОБЩИЕ ТРЕБОВАНИЯ К ТЕКСТУ:
1. Стиль: {style_descriptions.get(style, 'разговорный')}
2. Текст должен быть лаконичным и читаемым
3. Добавь 3-5 релевантных хештегов в конце
4. Текст должен вызывать доверие и эмоциональный отклик
5. Избегай сложных терминов, объясняй простыми словами
6. Используй эмодзи для визуального оформления (2-4 эмодзи)
7. Сделай текст готовым к публикации в социальных сетях
8. Добавь призыв к действию, где это уместно

Формат ответа: готовый текст поста без дополнительных пояснений."""
    
    return system_prompt

def format_generated_text(text: str, original_prompt: str, nko_data: dict, model: str = None) -> str:
    """Форматирует сгенерированный текст для отправки пользователю"""
    
    nko_info = ""
    if nko_data and nko_data.get('has_nko_info'):
        nko_name = nko_data.get('nko_name', '')
        nko_info = f" для {nko_name}"
    
    personalized_note = ""
    if nko_data and nko_data.get('has_nko_info'):
        personalized_note = f"\n🎯 <i>Контент персонализирован под вашу НКО!</i>"
    else:
        personalized_note = f"\n💡 <i>Для персонализации контента расскажите о вашей НКО в настройках</i>"
    
    model_info = f"\n🤖 <i>Сгенерировано с помощью AI</i>" if model else ""
    
    # Убираем упоминание исходного запроса из финального текста
    final_text = text
    if original_prompt and original_prompt[:100] in final_text:
        final_text = final_text.replace(original_prompt[:100], "").strip()
    
    return f"""📝 <b>Сгенерированный текст{nko_info}</b>

{final_text}

{personalized_note}{model_info}"""

def generate_fallback_text(prompt: str, style: str, nko_data: dict) -> str:
    """Качественная заглушка на случай ошибки API"""
    
    nko_info = ""
    if nko_data and nko_data.get('has_nko_info'):
        nko_name = nko_data.get('nko_name', 'ваша организация')
        nko_mission = nko_data.get('nko_mission', 'ваша миссия')
        nko_activities = nko_data.get('nko_activities', 'ваша деятельность')
        
        # Создаем персонализированный текст на основе данных НКО
        personalized_content = create_personalized_fallback(prompt, nko_name, nko_mission, nko_activities, style)
    else:
        personalized_content = create_general_fallback(prompt, style)
    
    return personalized_content

def create_personalized_fallback(prompt: str, nko_name: str, nko_mission: str, nko_activities: str, style: str) -> str:
    """Создает персонализированный fallback текст"""
    
    styles = {
        "разговорный": "💬",
        "официальный": "🏢", 
        "художественный": "🎨",
        "эмоциональный": "❤️"
    }
    
    style_emoji = styles.get(style, "💬")
    
    # Базовый шаблон с персонализацией
    base_content = f"""
{style_emoji} <b>Сгенерированный текст для {nko_name}</b>

🌟 <b>{nko_name}</b> продолжает свою важную работу!
🎯 <b>Наша миссия:</b> {nko_mission}
🛠️ <b>Что мы делаем:</b> {nko_activities}

💫 Благодаря вашей поддержке мы можем делать мир лучше каждый день!
🤝 Присоединяйтесь к нам — вместе мы сможем больше!

"""
    
    # Добавляем контекст из промпта
    if "анонс" in prompt.lower() or "мероприятие" in prompt.lower():
        base_content += "📅 <b>Ближайшее мероприятие:</b> скоро анонсируем!\n"
    elif "новость" in prompt.lower() or "событие" in prompt.lower():
        base_content += "📢 <b>Последние новости:</b> следите за обновлениями!\n"
    elif "отчет" in prompt.lower() or "итоги" in prompt.lower():
        base_content += "📊 <b>Наши достижения:</b> благодаря вам мы помогаем каждый день!\n"
    elif "история" in prompt.lower() or "случай" in prompt.lower():
        base_content += "❤️ <b>История помощи:</b> каждый день мы видим, как ваша поддержка меняет жизни!\n"
    
    base_content += """
🏷️ <b>Хештеги:</b> #НКО #Помощь #СоциальныйПроект #Добро

<i>Это пример контента, адаптированный под вашу организацию. Для AI-генерации проверьте настройки API.</i>"""
    
    return base_content

def create_general_fallback(prompt: str, style: str) -> str:
    """Создает общий fallback текст"""
    
    styles = {
        "разговорный": "💬",
        "официальный": "🏢", 
        "художественный": "🎨",
        "эмоциональный": "❤️"
    }
    
    style_emoji = styles.get(style, "💬")
    
    base_content = f"""
{style_emoji} <b>Сгенерированный текст</b>

🌟 Пример контента для вашей НКО!
💫 Расскажите о вашей организации, чтобы я мог создавать персонализированные посты!

"""
    
    # Добавляем контекст из промпта
    if "анонс" in prompt.lower():
        base_content += "📅 <b>Анонс мероприятия:</b> Приглашаем всех на наше следующее событие!\n"
    elif "новость" in prompt.lower():
        base_content += "📢 <b>Новость:</b> У нас есть важные обновления!\n"
    elif "отчет" in prompt.lower():
        base_content += "📊 <b>Отчет:</b> Подводим итоги нашей работы\n"
    elif "история" in prompt.lower():
        base_content += "❤️ <b>История:</b> Каждый день мы видим, как помощь меняет жизни\n"
    else:
        base_content += "📝 <b>Пост:</b> Делимся с вами важной информацией\n"
    
    base_content += """
🏷️ <b>Хештеги:</b> #НКО #Помощь #СоциальныйПроект #Добро

<i>Это пример контента. Для AI-генерации проверьте настройки API и расскажите о вашей НКО.</i>"""
    
    return base_content