from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from app.utils.states import PostCreationStates, TemplateStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_post_creation_keyboard,
    get_template_types_keyboard,
    get_back_keyboard,
    get_skip_keyboard,
    get_story_styles_keyboard,
    get_after_post_keyboard
)
from app.services.ai_text_sync import generate_text_sync
from app.services.async_ai_image import generate_image_async
from app.services.favorites import favorites_service
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = Router()

# Глобальный словарь для хранения последних постов пользователей
user_last_posts = {}

# Глобальный обработчик для кнопки "Главное меню" - должен быть ПЕРВЫМ
@router.message(F.text == "🔙 ГЛАВНОЕ МЕНЮ")
@router.message(F.text == "📋 ГЛАВНОЕ МЕНЮ")
async def handle_global_main_menu(message: types.Message, state: FSMContext):
    """Обработка кнопки Главное меню из любого состояния"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())

# Глобальный обработчик для кнопки "Сохранить в избранное" - должен быть ВТОРЫМ
@router.message(F.text == "⭐ СОХРАНИТЬ В ИЗБРАННОЕ")
async def handle_global_save_to_favorites(message: types.Message, state: FSMContext):
    """Глобальный обработчик сохранения в избранное"""
    try:
        user_id = message.from_user.id
        logger.info(f"Глобальный обработчик сохранения для пользователя {user_id}")
        
        # Пробуем сначала найти пост
        post_data = user_last_posts.get(user_id)
        if post_data:
            logger.info(f"Найден пост для сохранения: {post_data.get('title', 'Без названия')}")
            await save_post_to_favorites_internal(message, state, post_data)
            return
        
        # Если поста нет, пробуем найти изображение
        from app.handlers.image_gen import user_last_images
        image_data = user_last_images.get(user_id)
        if image_data:
            logger.info(f"Найдено изображение для сохранения: {image_data.get('title', 'Без названия')}")
            await save_image_to_favorites_internal(message, state, image_data)
            return
        
        # Если ничего не найдено
        await message.answer(
            "❌ Сначала создайте пост или картинку!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        
    except Exception as e:
        logger.error(f"❌ Ошибка в глобальном обработчике избранного: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )

@router.message(F.text == "📝 СОЗДАТЬ ПОСТ С КАРТИНКОЙ")
async def start_post_creation(message: types.Message, state: FSMContext):
    """Начало создания поста с картинкой"""
    # Очищаем состояние при входе в функцию
    await state.clear()
    
    start_text = (
        "**Выберите, как хотите создать пост?**"
    )
    
    await message.answer(start_text, reply_markup=get_post_creation_keyboard())
    await state.set_state(PostCreationStates.waiting_for_creation_method)

@router.message(PostCreationStates.waiting_for_creation_method)
async def process_creation_method(message: types.Message, state: FSMContext):
    """Обработка выбора метода создания поста"""
    if message.text == "🎯 БЫСТРЫЙ ШАБЛОН":
        await start_template_selection(message, state)
    elif message.text == "💫 УЛУЧШИТЬ ИДЕЮ":
        await start_idea_improvement(message, state)
    elif message.text == "🎭 ГЕНЕРАТОР ИСТОРИЙ":
        await start_story_generator(message, state)
    elif message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer("Пожалуйста, выберите вариант из меню:")

async def start_template_selection(message: types.Message, state: FSMContext):
    """Начало выбора шаблона"""
    template_text = (
        "**Я буду мурчать вам вопросы, а вы — отвечать!**\n\n"
        "На основе ваших ответов я сделаю крутой пост с картинкой! 🎨"
    )
    
    await message.answer(template_text, reply_markup=get_template_types_keyboard())
    await state.set_state(TemplateStates.waiting_for_template_type)

# Улучшение идеи - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ
async def start_idea_improvement(message: types.Message, state: FSMContext):
    """Начало улучшения идеи"""
    idea_text = (
        "**Расскажите свою идею для поста, а я:**\n"
        "✨ Разовью её в полноценный текст\n"
        "💖 Добавлю эмоций и структуры\n"  
        "🎨 Подберу цепляющую картинку\n"
        "🚀 Создам готовый к публикации пост\n\n"
        "👇 **Опишите вашу идею: о чём пост, для кого, ключевые моменты и т.д.**"
    )
    
    await message.answer(idea_text, reply_markup=get_back_keyboard())
    await state.set_state(PostCreationStates.waiting_for_idea_to_improve)

@router.message(PostCreationStates.waiting_for_idea_to_improve)
async def process_idea_improvement(message: types.Message, state: FSMContext):
    """Обработка идеи для улучшения - РЕАЛЬНАЯ РЕАЛИЗАЦИЯ"""
    if message.text == "🔙 НАЗАД":
        await start_post_creation(message, state)
        return
    
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    await message.answer("**⏳ Совсем чуть-чуть — и будет готово...**")
    
    try:
        # Получаем данные об НКО из состояния (если есть)
        user_data = await state.get_data()
        nko_data = user_data.get('nko_data', {})
        user_idea = message.text
        
        # Создаем промпт для улучшения идеи
        improvement_prompt = create_improvement_prompt(user_idea, nko_data)
        
        # Генерируем улучшенный текст
        generated_text = await asyncio.to_thread(
            generate_text_sync, improvement_prompt, "разговорный", nko_data
        )
        
        # Создаем промпт для картинки на основе идеи
        image_prompt = create_idea_image_prompt(user_idea, nko_data)
        
        # Генерируем картинку
        image_path = await generate_image_async(image_prompt)
        
        # Форматируем финальный текст и обрезаем если нужно
        final_text = format_improved_post(generated_text, user_idea, nko_data)
        
        # Проверяем длину текста для подписи (макс 1024 символа)
        if len(final_text) > 1024:
            logger.warning(f"Текст слишком длинный ({len(final_text)} символов), обрезаем до 1024")
            final_text = final_text[:1020] + "..."
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=final_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные для возможного сохранения в избранное
        post_data = {
            'type': 'improved_idea',
            'title': f"Улучшенная идея: {user_idea[:30]}..." if user_idea else "Улучшенная идея",
            'text': final_text,
            'image_path': image_path,
            'created_at': datetime.now().isoformat(),
            'original_idea': user_idea
        }
        
        # Сохраняем пост в глобальном хранилище
        user_last_posts[message.from_user.id] = post_data
        logger.info(f"✅ Пост с улучшенной идеей создан и сохранен для пользователя {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка улучшения идеи: {e}")
        await message.answer(
            f"❌ Произошла ошибка при улучшении идеи: {str(e)}\n"
            f"Попробуйте еще раз или используйте другой метод создания поста.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        return
    
    # НЕ очищаем состояние, чтобы кнопки работали
    await state.set_state(PostCreationStates.waiting_for_post_action)

def create_improvement_prompt(user_idea: str, nko_data: dict) -> str:
    """Создает промпт для улучшения идеи"""
    nko_context = ""
    if nko_data and nko_data.get('nko_name'):
        nko_context = f" Учти, что это пост для организации '{nko_data['nko_name']}'."
        if nko_data.get('nko_mission'):
            nko_context += f" Миссия организации: {nko_data['nko_mission']}."
        if nko_data.get('nko_activities'):
            nko_context += f" Деятельность: {nko_data['nko_activities']}."
    
    return (
        f"Разработай полноценный пост для социальных сетей на основе этой идеи: \"{user_idea}\". "
        f"{nko_context}\n\n"
        f"Требования к посту:\n"
        f"1. Сделай текст эмоциональным и вовлекающим\n"
        f"2. Добавь призыв к действию\n"
        f"3. Используй эмодзи для визуального оформления\n"
        f"4. Включи 3-5 релевантных хештегов\n"
        f"5. Сделай текст лаконичным (3-5 предложений)\n"
        f"6. Убери любые технические пояснения - только готовый пост\n"
        f"7. Длина текста не должна превышать 800 символов"
    )

def create_idea_image_prompt(user_idea: str, nko_data: dict) -> str:
    """Создает промпт для генерации картинки на основе идеи"""
    # Базовый промпт на основе идеи пользователя
    base_prompt = user_idea
    
    # Добавляем контекст НКО если есть
    if nko_data and nko_data.get('nko_activities'):
        activities = nko_data['nko_activities']
        # Извлекаем ключевые слова из деятельности
        keywords = extract_keywords_from_activities(activities)
        if keywords:
            base_prompt += f", {keywords}"
    
    # Добавляем общий контекст благотворительности
    base_prompt += ", благотворительность, помощь, добро, социальный проект"
    
    return base_prompt

def extract_keywords_from_activities(activities: str) -> str:
    """Извлекает ключевые слова из описания деятельности"""
    if not activities:
        return ""
    
    keywords = []
    activity_words = ['помощь', 'поддержка', 'защита', 'спасение', 'решение', 'борьба', 
                     'лечение', 'образование', 'развитие', 'поддержка']
    
    words = activities.lower().split()
    for word in words:
        clean_word = ''.join(char for char in word if char.isalnum())
        if any(aw in clean_word for aw in activity_words) and len(clean_word) > 4:
            keywords.append(clean_word)
    
    return ", ".join(keywords[:3]) if keywords else "социальная помощь"

def format_improved_post(generated_text: str, original_idea: str, nko_data: dict) -> str:
    """Форматирует улучшенный пост для отправки"""
    nko_info = ""
    if nko_data and nko_data.get('nko_name'):
        nko_info = f" для {nko_data['nko_name']}"
    
    return f"""✨ <b>Улучшенная идея поста{nko_info}</b>

{generated_text}

💡 <i>На основе вашей идеи: "{original_idea}"</i>"""

# Генератор историй
async def start_story_generator(message: types.Message, state: FSMContext):
    """Начало генератора историй"""
    story_text = (
        "**Вспомню историю из своей жизни или напишу реалистичную для вашего канала!**\n\n"
        "Просто введите 3-5 ключевых слов.\n"
        "_Пример: Котёнок, улица, голодный, выздоровление_"
    )
    
    await message.answer(story_text, reply_markup=get_back_keyboard())
    await state.set_state(PostCreationStates.waiting_for_story_keywords)

@router.message(PostCreationStates.waiting_for_story_keywords)
async def process_story_keywords(message: types.Message, state: FSMContext):
    """Обработка ключевых слов для истории"""
    if message.text == "🔙 НАЗАД":
        await start_post_creation(message, state)
        return
    
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    await state.update_data(story_keywords=message.text)
    await state.set_state(PostCreationStates.waiting_for_story_style)
    
    await message.answer(
        "**Отлично! Теперь выберите стиль истории:**",
        reply_markup=get_story_styles_keyboard()
    )

@router.message(PostCreationStates.waiting_for_story_style)
async def process_story_style(message: types.Message, state: FSMContext):
    """Обработка стиля истории"""
    style_map = {
        "💬 РЕАЛИСТИЧНЫЙ": "реалистичный",
        "✨ ВДОХНОВЛЯЮЩИЙ": "вдохновляющий", 
        "😢 ЭМОЦИОНАЛЬНЫЙ": "эмоциональный",
        "🎪 ДРАМАТИЧНЫЙ": "драматичный"
    }
    
    if message.text == "🔙 НАЗАД":
        await state.set_state(PostCreationStates.waiting_for_story_keywords)
        await message.answer("Введите ключевые слова:", reply_markup=get_back_keyboard())
        return
    
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    if message.text not in style_map:
        await message.answer("Пожалуйста, выберите стиль из предложенных вариантов:")
        return
    
    data = await state.get_data()
    keywords = data.get('story_keywords', '')
    style = style_map[message.text]
    
    await message.answer("**Муууур! Создаю для вашего канала интересную историю...**")
    
    try:
        # Создаем промпт для генерации истории с ограничением длины
        story_prompt = create_story_prompt(keywords, style)
        nko_data = await state.get_data()
        
        # Генерируем историю
        generated_story = await asyncio.to_thread(
            generate_text_sync, story_prompt, "художественный", nko_data
        )
        
        # Генерируем картинку для истории
        image_prompt = create_story_image_prompt(keywords, style)
        image_path = await generate_image_async(image_prompt)
        
        # Форматируем историю и проверяем длину
        formatted_story = format_story_post(generated_story, keywords, style, nko_data)
        
        # Проверяем длину текста для подписи (макс 1024 символа)
        if len(formatted_story) > 1024:
            logger.warning(f"Текст истории слишком длинный ({len(formatted_story)} символов), обрезаем до 1024")
            formatted_story = formatted_story[:1020] + "..."
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=formatted_story,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные для возможного сохранения в избранное
        post_data = {
            'type': 'story',
            'title': f"История: {keywords[:30]}..." if keywords else "История",
            'text': formatted_story,
            'image_path': image_path,
            'created_at': datetime.now().isoformat(),
            'keywords': keywords,
            'style': style
        }
        
        # Сохраняем пост в глобальном хранилище
        user_last_posts[message.from_user.id] = post_data
        logger.info(f"✅ История создана и сохранена для пользователя {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации истории: {e}")
        await message.answer(
            "❌ Произошла ошибка при генерации истории. Попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        return
    
    # НЕ очищаем состояние, чтобы кнопки работали
    await state.set_state(PostCreationStates.waiting_for_post_action)

def create_story_prompt(keywords: str, style: str) -> str:
    """Создает промпт для генерации истории с ограничением длины"""
    style_descriptions = {
        "реалистичный": "реалистичный, правдоподобный, жизненный",
        "вдохновляющий": "вдохновляющий, мотивирующий, позитивный", 
        "эмоциональный": "эмоциональный, трогательный, чувственный",
        "драматичный": "драматичный, напряженный, с интригой"
    }
    
    return (
        f"Напиши {style_descriptions.get(style, 'трогательную')} историю для социальных сетей "
        f"на основе ключевых слов: {keywords}. "
        f"Сделай историю короткой (3-4 предложения), эмоциональной и с хорошим финалом. "
        f"Добавь 2-3 эмодзи и 2-3 релевантных хештега. "
        f"История должна быть готова к публикации без дополнительных пояснений. "
        f"Общая длина текста не должна превышать 500 символов."
    )

def create_story_image_prompt(keywords: str, style: str) -> str:
    """Создает промпт для генерации картинки истории"""
    return f"{keywords}, эмоциональная история, {style} стиль, социальная тематика"

def format_story_post(generated_story: str, keywords: str, style: str, nko_data: dict) -> str:
    """Форматирует историю для отправки"""
    nko_info = ""
    if nko_data and nko_data.get('nko_name'):
        nko_info = f" для {nko_data['nko_name']}"
    
    style_emoji = {
        "реалистичный": "💬",
        "вдохновляющий": "✨",
        "эмоциональный": "😢", 
        "драматичный": "🎪"
    }
    
    emoji = style_emoji.get(style, "📖")
    
    return f"""{emoji} <b>История{nko_info}</b>

{generated_story}

💡 <i>На основе ключевых слов: "{keywords}"</i>"""

# Обработчики для шаблонов
@router.message(TemplateStates.waiting_for_template_type)
async def process_template_type(message: types.Message, state: FSMContext):
    """Обработка выбора типа шаблона"""
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    template_handlers = {
        "📢 АНОНС": start_announce_template,
        "📰 НОВОСТИ": start_news_template,
        "❤️ ИСТОРИЯ": start_story_template,
        "👥 ПОИСК ВОЛОНТЕРОВ": start_volunteers_template,
        "📊 ОТЧЁТ": start_report_template,
        "🚨 СРОЧНЫЙ СБОР": start_emergency_template,
        "🎊 ПОЗДРАВЛЕНИЕ": start_congrats_template
    }
    
    if message.text in template_handlers:
        await template_handlers[message.text](message, state)
    elif message.text == "🔙 НАЗАД":
        await start_post_creation(message, state)
    else:
        await message.answer("Пожалуйста, выберите тип поста из меню:")

# Заглушки для шаблонов (они реализованы в post_templates.py)
async def start_announce_template(message: types.Message, state: FSMContext):
    """Шаблон анонса"""
    await state.set_state(TemplateStates.announce_event)
    await message.answer(
        "**🎪 Как называется ваше мероприятие?**\n"
        "_Пример: Эко-субботник в парке_",
        reply_markup=get_skip_keyboard()
    )

async def start_news_template(message: types.Message, state: FSMContext):
    """Шаблон новостей"""
    await state.set_state(TemplateStates.news_event)
    await message.answer(
        "**📢 Расскажите, что произошло? Опишите основное событие.**\n"
        "_Пример: Мы открыли новый центр помощи бездомным животным_",
        reply_markup=get_skip_keyboard()
    )

async def start_story_template(message: types.Message, state: FSMContext):
    """Шаблон истории"""
    await state.set_state(TemplateStates.story_subject)
    await message.answer(
        "**👤 О ком эта история?**\n"
        "_Пример: О коте Барсике, которого нашли на улице_",
        reply_markup=get_skip_keyboard()
    )

async def start_volunteers_template(message: types.Message, state: FSMContext):
    """Шаблон поиска волонтеров"""
    await state.set_state(TemplateStates.volunteers_event)
    await message.answer(
        "**🎪 Для какого мероприятия/проекта нужны волонтеры?**\n"
        "_Пример: Для субботника в парке_",
        reply_markup=get_skip_keyboard()
    )

async def start_report_template(message: types.Message, state: FSMContext):
    """Шаблон отчета"""
    await state.set_state(TemplateStates.report_period)
    await message.answer(
        "**📅 За какой период составляем отчет?**\n"
        "_Пример: Апрель 2024 года_",
        reply_markup=get_skip_keyboard()
    )

async def start_emergency_template(message: types.Message, state: FSMContext):
    """Шаблон срочного сбора"""
    await state.set_state(TemplateStates.emergency_situation)
    await message.answer(
        "**🚨 Что случилось? Опишите ситуацию.**\n"
        "_Пример: Пожар в приюте для животных, срочно нужна помощь для пострадавших_",
        reply_markup=get_skip_keyboard()
    )

async def start_congrats_template(message: types.Message, state: FSMContext):
    """Шаблон поздравления"""
    await state.set_state(TemplateStates.congrats_who)
    await message.answer(
        "**🎉 Кого мы поздравляем?**\n"
        "_Пример: Наших дорогих волонтеров_",
        reply_markup=get_skip_keyboard()
    )

# Обработчики действий после создания поста
@router.message(PostCreationStates.waiting_for_post_action)
async def handle_post_actions(message: types.Message, state: FSMContext):
    """Обработка действий после создания поста"""
    if message.text == "🔄 СОЗДАТЬ ЕЩЕ ПОСТ":
        await create_another_post(message, state)
    elif message.text == "🎨 СОЗДАТЬ КАРТИНКУ":
        await create_another_image(message, state)
    elif message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        # Для кнопки "⭐ СОХРАНИТЬ В ИЗБРАННОЕ" работает глобальный обработчик
        await message.answer("Пожалуйста, выберите действие из меню:")

async def save_post_to_favorites_internal(message: types.Message, state: FSMContext, post_data: dict):
    """Внутренняя функция сохранения поста в избранное"""
    try:
        user_id = message.from_user.id
        
        logger.info(f"Попытка сохранения поста в избранное для пользователя {user_id}")
        logger.info(f"Данные поста: {post_data}")
        
        # Сохраняем пост в избранное
        success = await favorites_service.save_post(
            user_id=user_id,
            post_data=post_data
        )
        
        if success:
            await message.answer(
                "✅ Пост сохранен в избранное! 📌\n"
                "Можно посмотреть в разделе \"⭐ ИЗБРАННОЕ\"",
                reply_markup=get_main_menu_keyboard()
            )
            logger.info(f"✅ Пост успешно сохранен в избранное для пользователя {user_id}")
            
            # Очищаем состояние после успешного сохранения
            await state.clear()
        else:
            await message.answer(
                "❌ Не удалось сохранить пост. Попробуйте еще раз.",
                reply_markup=get_after_post_keyboard()
            )
            logger.error(f"❌ Ошибка сохранения поста в избранное для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при сохранении поста: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте еще раз.",
            reply_markup=get_after_post_keyboard()
        )

async def save_image_to_favorites_internal(message: types.Message, state: FSMContext, image_data: dict):
    """Внутренняя функция сохранения изображения в избранное"""
    try:
        user_id = message.from_user.id
        
        logger.info(f"Попытка сохранения изображения в избранное для пользователя {user_id}")
        
        # Сохраняем изображение в избранное
        success = await favorites_service.save_post(
            user_id=user_id,
            post_data=image_data
        )
        
        if success:
            await message.answer(
                "✅ Картинка сохранена в избранное! 📌\n"
                "Можно посмотреть в разделе \"⭐ ИЗБРАННОЕ\"",
                reply_markup=get_main_menu_keyboard()
            )
            logger.info(f"✅ Картинка успешно сохранена в избранное для пользователя {user_id}")
            
            # Очищаем состояние после успешного сохранения
            await state.clear()
        else:
            await message.answer(
                "❌ Не удалось сохранить картинку. Попробуйте еще раз.",
                reply_markup=get_after_post_keyboard()
            )
            logger.error(f"❌ Ошибка сохранения картинки в избранное для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при сохранении картинки: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте еще раз.",
            reply_markup=get_after_post_keyboard()
        )

async def create_another_post(message: types.Message, state: FSMContext):
    """Создание еще одного поста"""
    await state.clear()
    await start_post_creation(message, state)

async def create_another_image(message: types.Message, state: FSMContext):
    """Создание картинки"""
    from app.handlers.image_gen import start_image_creation
    await state.clear()
    await start_image_creation(message, state)