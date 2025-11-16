import torch
from diffusers import DiffusionPipeline
import os
import asyncio
from datetime import datetime
from PIL import Image, ImageDraw
import requests
import json
import urllib3
from app.config import Config

# Отключаем предупреждения о SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def generate_image_async(prompt: str) -> str:
    """
    Асинхронная генерация изображения с использованием Dreamlike Photoreal 2.0
    """
    try:
        # Переводим промпт на английский с использованием вашей основной модели
        english_prompt = await translate_to_english_reliable(prompt)
        print(f"🔄 Переведенный промпт: {english_prompt}")
        
        # Запускаем тяжелую генерацию в отдельном потоке
        image_path = await asyncio.get_event_loop().run_in_executor(
            None, 
            _generate_image_sync, 
            english_prompt
        )
        return image_path
        
    except Exception as e:
        print(f"Ошибка при асинхронной генерации изображения: {e}")
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            _create_fallback_image, 
            prompt
        )

async def translate_to_english_reliable(text: str) -> str:
    """Надежный перевод русскоязычного текста на английский"""
    try:
        # Сначала пробуем через OpenRouter с вашей основной моделью
        translated = await translate_with_openrouter(text)
        if translated:
            return translated
        
        # Если OpenRouter не сработал, используем простой словарь
        return simple_translate(text)
        
    except Exception as e:
        print(f"❌ Ошибка при переводе: {e}")
        return simple_translate(text)

async def translate_with_openrouter(text: str) -> str:
    """Перевод через OpenRouter API с вашей основной моделью"""
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

# Функции simple_translate, _generate_image_sync, _generate_with_alternative_model, _create_fallback_image
# остаются без изменений

def simple_translate(text: str) -> str:
    """Простой перевод с использованием расширенного словаря"""
    translation_dict = {
        # Основные термины НКО
        "нко": "non-profit organization",
        "благотворительность": "charity",
        "помощь": "help",
        "волонтеры": "volunteers",
        "добро": "kindness",
        "миссия": "mission",
        "помогать": "help",
        "спасать": "save",
        "защищать": "protect",
        "поддержка": "support",
        "развитие": "development",
        "проект": "project",
        "программа": "program",
        
        # Социальные темы
        "дети": "children",
        "животные": "animals",
        "пожилые": "elderly",
        "семьи": "families",
        "бездомные": "homeless",
        "инвалиды": "disabled people",
        "сироты": "orphans",
        "беженцы": "refugees",
        "малоимущие": "low-income",
        
        # Мероприятия
        "мероприятие": "event",
        "концерт": "concert",
        "фестиваль": "festival",
        "субботник": "cleanup event",
        "сбор": "fundraising",
        "акция": "campaign",
        "встреча": "meeting",
        "семинар": "seminar",
        "тренинг": "training",
        
        # Эмоции и стили
        "радостный": "joyful",
        "трогательный": "touching", 
        "вдохновляющий": "inspiring",
        "эмоциональный": "emotional",
        "добрый": "kind",
        "теплый": "warm",
        "яркий": "bright",
        "красивый": "beautiful",
        "позитивный": "positive",
        "оптимистичный": "optimistic",
        
        # Визуальные элементы
        "солнечный": "sunny",
        "светлый": "light", 
        "цветы": "flowers",
        "природа": "nature",
        "город": "city",
        "парк": "park",
        "улица": "street",
        "дом": "house",
        "здание": "building",
        
        # Стили изображений
        "мультяшный": "cartoon",
        "реалистичный": "realistic",
        "художественный": "artistic",
        "фотореалистичный": "photorealistic",
        "инфографика": "infographic",
        "абстрактный": "abstract",
        "минимализм": "minimalism",
        
        # Действия
        "помощь": "helping",
        "работа": "working",
        "встреча": "meeting",
        "обучение": "learning",
        "лечение": "healing",
        "строительство": "building",
        "уборка": "cleaning",
        "посадка": "planting",
        
        # Качества
        "качественный": "high quality",
        "профессиональный": "professional",
        "дружелюбный": "friendly",
        "заботливый": "caring",
        "ответственный": "responsible"
    }
    
    # Простой перевод слов с учетом некоторых грамматических особенностей
    words = text.lower().split()
    translated_words = []
    
    for word in words:
        # Убираем знаки препинания
        clean_word = ''.join(char for char in word if char.isalnum())
        
        # Пробуем найти точное совпадение
        if clean_word in translation_dict:
            translated_words.append(translation_dict[clean_word])
        else:
            # Пробуем найти частичное совпадение
            found = False
            for russian, english in translation_dict.items():
                if russian in clean_word and len(russian) > 3:
                    translated_words.append(english)
                    found = True
                    break
            
            if not found:
                # Оставляем слово как есть, если не нашли перевода
                translated_words.append(clean_word)
    
    result = " ".join(translated_words)
    
    # Добавляем общий контекст для улучшения генерации
    result += ", charity, non-profit organization, social work, helping people"
    
    print(f"🔄 Простой перевод: {result}")
    return result

def _generate_image_sync(prompt: str) -> str:
    """
    Синхронная генерация изображения с Dreamlike Photoreal 2.0
    """
    print(f"🔄 Начинаем генерацию изображения: {prompt}")
    
    # Определяем устройство
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ Используется MPS (Apple Silicon)")
        torch_dtype = torch.float16
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("✅ Используется CUDA")
        torch_dtype = torch.float16
    else:
        device = torch.device("cpu")
        print("⚠️ Используется CPU")
        torch_dtype = torch.float32

    try:
        # Загружаем Dreamlike Photoreal 2.0
        print("📥 Загружаем модель Dreamlike Photoreal 2.0...")
        
        pipe = DiffusionPipeline.from_pretrained(
            "dreamlike-art/dreamlike-photoreal-2.0",
            torch_dtype=torch_dtype,
            use_safetensors=True,
        )
        
        # Перемещаем на устройство
        print("🔄 Перемещаем модель на устройство...")
        pipe = pipe.to(device)
        
        # Оптимальные настройки для Dreamlike Photoreal 2.0
        print(f"🎨 Генерация фотореалистичного изображения: {prompt}")
        
        # Генерируем изображение с рекомендованными настройками
        image = pipe(
            prompt=prompt,
            num_inference_steps=20,      # Уменьшаем для скорости
            guidance_scale=7.5,          # Стандартный guidance scale
            width=512,
            height=512
        ).images[0]

        # Сохраняем изображение
        os.makedirs("data/images", exist_ok=True)
        output_filename = f"data/images/dreamlike_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(output_filename)

        print(f"✅ Фотореалистичное изображение сохранено: {output_filename}")
        
        # Очищаем память
        del pipe
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return output_filename

    except Exception as e:
        print(f"❌ Ошибка при генерации с Dreamlike: {e}")
        
        # Пробуем альтернативный способ с другой моделью
        try:
            print("🔄 Пробуем альтернативную модель...")
            return _generate_with_alternative_model(prompt, device, torch_dtype)
        except Exception as e2:
            print(f"❌ Альтернативная модель тоже не работает: {e2}")
            return _create_fallback_image(prompt)

def _generate_with_alternative_model(prompt: str, device: torch.device, torch_dtype: torch.dtype) -> str:
    """
    Альтернативная генерация с другой моделью
    """
    print("🔄 Используем альтернативную модель: runwayml/stable-diffusion-v1-5")
    
    try:
        pipe = DiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch_dtype,
            use_safetensors=True,
        )
    except:
        # Если не получается, загружаем без специфичных параметров
        pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    
    pipe = pipe.to(device)
    
    # Генерируем изображение
    image = pipe(
        prompt=prompt,
        num_inference_steps=20,
        guidance_scale=7.5,
        width=512,
        height=512
    ).images[0]

    # Сохраняем изображение
    os.makedirs("data/images", exist_ok=True)
    output_filename = f"data/images/alt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(output_filename)

    print(f"✅ Альтернативное изображение сохранено: {output_filename}")
    
    # Очищаем память
    del pipe
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return output_filename

def _create_fallback_image(prompt: str) -> str:
    """Создает качественную заглушку если генерация не удалась"""
    os.makedirs("data/images", exist_ok=True)
    filename = f"data/images/fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    # Создаем более красивую заглушку
    img = Image.new('RGB', (512, 512), color=(70, 130, 180))  # Красивый синий фон
    d = ImageDraw.Draw(img)
    
    # Добавляем декоративные элементы
    d.rectangle([50, 50, 462, 462], outline=(255, 255, 255), width=3)
    
    # Разбиваем текст на строки
    lines = []
    words = prompt.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if len(test_line) > 35:
            lines.append(line)
            line = word + " "
        else:
            line = test_line
    if line:
        lines.append(line)
    
    # Добавляем текст на изображение
    y = 150
    for i, line in enumerate(lines):
        if i < 4:  # Показываем только первые 4 строки
            d.text((256, y), line, fill=(255, 255, 255), anchor="mm")
            y += 40
    
    # Добавляем красивый заголовок
    d.text((256, 80), "🎨 Добробот", fill=(255, 255, 200), anchor="mm")
    d.text((256, 110), "Сгенерированное изображение", fill=(255, 255, 200), anchor="mm")
    
    # Информация о промпте
    if len(lines) > 4:
        d.text((256, 320), "...", fill=(255, 255, 255), anchor="mm")
    
    d.text((256, 380), "Ваше изображение готово!", fill=(255, 255, 200), anchor="mm")
    d.text((256, 410), "Используется резервный генератор", fill=(200, 255, 200), anchor="mm")

    img.save(filename)
    return filename