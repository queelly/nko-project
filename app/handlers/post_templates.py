from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from app.utils.states import TemplateStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_skip_keyboard,
    get_after_post_keyboard
)
from app.services.async_ai_image import generate_image_async
from app.services.ai_text_sync import generate_text_sync
import asyncio

router = Router()

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "📢 АНОНС"
# =============================================================================

@router.message(TemplateStates.announce_event)
async def process_announce_event(message: types.Message, state: FSMContext):
    """Обработка названия мероприятия для анонса"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_event="Мероприятие")
    else:
        await state.update_data(announce_event=message.text)
    
    await state.set_state(TemplateStates.announce_date)
    await message.answer(
        "**📅 Когда оно состоится? (дата и время)**\n"
        "_Пример: 15 мая с 11:00 до 14:00_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.announce_date)
async def process_announce_date(message: types.Message, state: FSMContext):
    """Обработка даты мероприятия"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.announce_event)
        await message.answer(
            "**🎪 Как называется ваше мероприятие?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_date="скоро")
    else:
        await state.update_data(announce_date=message.text)
    
    await state.set_state(TemplateStates.announce_place)
    await message.answer(
        "**📍 Где будет проходить?**\n"
        "_Пример: Парк Смолинка, г. Снежинск_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.announce_place)
async def process_announce_place(message: types.Message, state: FSMContext):
    """Обработка места мероприятия"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.announce_date)
        await message.answer(
            "**📅 Когда оно состоится?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_place="уточняется")
    else:
        await state.update_data(announce_place=message.text)
    
    await state.set_state(TemplateStates.announce_audience)
    await message.answer(
        "**🎯 Кого вы ждете на мероприятие?**\n"
        "_Пример: Волонтеров, семьи с детьми, всех желающих_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.announce_audience)
async def process_announce_audience(message: types.Message, state: FSMContext):
    """Обработка целевой аудитории"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.announce_place)
        await message.answer(
            "**📍 Где будет проходить?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_audience="всех желающих")
    else:
        await state.update_data(announce_audience=message.text)
    
    await state.set_state(TemplateStates.announce_benefits)
    await message.answer(
        "**🎁 Что получат участники?**\n"
        "_Пример: Инвентарь, обед, памятные сувениры_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.announce_benefits)
async def process_announce_benefits(message: types.Message, state: FSMContext):
    """Обработка преимуществ для участников"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.announce_audience)
        await message.answer(
            "**🎯 Кого вы ждете на мероприятие?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_benefits="хорошее настроение и новые знакомства")
    else:
        await state.update_data(announce_benefits=message.text)
    
    await state.set_state(TemplateStates.announce_registration)
    await message.answer(
        "**✅ Нужна ли регистрация?**\n"
        "_Пример: Да, по ссылке [google.forms]_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.announce_registration)
async def process_announce_registration(message: types.Message, state: FSMContext):
    """Обработка информации о регистрации"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.announce_benefits)
        await message.answer(
            "**🎁 Что получат участники?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(announce_registration="Регистрация не требуется")
    else:
        await state.update_data(announce_registration=message.text)
    
    # Все данные собраны - генерируем анонс
    await generate_announce_post(message, state)

async def generate_announce_post(message: types.Message, state: FSMContext):
    """Генерация поста-анонса"""
    data = await state.get_data()
    
    # Формируем промпт для AI
    prompt = create_announce_prompt(data)
    
    await message.answer("**Спасибо за информацию!**")
    await message.answer("**⏳ Создаю для вас самый крутой и добрый анонс...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "разговорный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_announce_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные для возможного повторного использования
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании анонса: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания анонса: {e}")
    
    await state.clear()

def create_announce_prompt(data: dict) -> str:
    """Создает промпт для генерации текста анонса"""
    event = data.get('announce_event', 'мероприятие')
    date = data.get('announce_date', 'скоро')
    place = data.get('announce_place', 'уточняется')
    audience = data.get('announce_audience', 'всех желающих')
    benefits = data.get('announce_benefits', 'хорошее настроение')
    registration = data.get('announce_registration', 'Регистрация не требуется')
    
    return (
        f"Создай анонс мероприятия для социальных сетей. "
        f"Мероприятие: {event}. "
        f"Дата и время: {date}. "
        f"Место: {place}. "
        f"Целевая аудитория: {audience}. "
        f"Что получат участники: {benefits}. "
        f"Регистрация: {registration}. "
        f"Сделай текст привлекательным, дружелюбным, с эмодзи. "
        f"Добавь призыв к действию и релевантные хештеги."
    )

def create_announce_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки анонса"""
    event = data.get('announce_event', 'мероприятие')
    return f"Анонс мероприятия {event}, социальная активность, добровольчество, яркое, привлекательное изображение, мультяшный стиль"

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "📰 НОВОСТИ"
# =============================================================================

@router.message(TemplateStates.news_event)
async def process_news_event(message: types.Message, state: FSMContext):
    """Обработка новостного события"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(news_event="важное событие")
    else:
        await state.update_data(news_event=message.text)
    
    await state.set_state(TemplateStates.news_date)
    await message.answer(
        "**📅 Когда это случилось? Укажите дату.**\n"
        "_Пример: 15 мая 2024 года_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.news_date)
async def process_news_date(message: types.Message, state: FSMContext):
    """Обработка даты новости"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.news_event)
        await message.answer(
            "**📢 Расскажите, что произошло?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(news_date="недавно")
    else:
        await state.update_data(news_date=message.text)
    
    await state.set_state(TemplateStates.news_place)
    await message.answer(
        "**📍 Где это произошло? Место события.**\n"
        "_Пример: По адресу: ул. Ленина, 15_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.news_place)
async def process_news_place(message: types.Message, state: FSMContext):
    """Обработка места события"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.news_date)
        await message.answer(
            "**📅 Когда это случилось?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(news_place="в нашем городе")
    else:
        await state.update_data(news_place=message.text)
    
    await state.set_state(TemplateStates.news_participants)
    await message.answer(
        "**🎯 Кто участвовал?**\n"
        "_Пример: Волонтеры, местные жители, представители администрации_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.news_participants)
async def process_news_participants(message: types.Message, state: FSMContext):
    """Обработка участников события"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.news_place)
        await message.answer(
            "**📍 Где это произошло?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(news_participants="наша команда и партнеры")
    else:
        await state.update_data(news_participants=message.text)
    
    await state.set_state(TemplateStates.news_significance)
    await message.answer(
        "**💫 Какое значение имеет это событие?**\n"
        "_Пример: Это позволит помочь 50 животным ежемесячно_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.news_significance)
async def process_news_significance(message: types.Message, state: FSMContext):
    """Обработка значимости события"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.news_participants)
        await message.answer(
            "**🎯 Кто участвовал?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(news_significance="Это важный шаг в нашей работе")
    else:
        await state.update_data(news_significance=message.text)
    
    # Все данные собраны - генерируем новость
    await generate_news_post(message, state)

async def generate_news_post(message: types.Message, state: FSMContext):
    """Генерация новостного поста"""
    data = await state.get_data()
    
    prompt = create_news_prompt(data)
    
    await message.answer("**Спасибо за информацию!**")
    await message.answer("**⏳ Создаю для вас интересную новость...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "разговорный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_news_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании новости: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания новости: {e}")
    
    await state.clear()

def create_news_prompt(data: dict) -> str:
    """Создает промпт для генерации новости"""
    event = data.get('news_event', 'событие')
    date = data.get('news_date', 'недавно')
    place = data.get('news_place', 'в нашем городе')
    participants = data.get('news_participants', 'наша команда')
    significance = data.get('news_significance', 'важное значение')
    
    return (
        f"Создай новостной пост для социальных сетей. "
        f"Событие: {event}. "
        f"Дата: {date}. "
        f"Место: {place}. "
        f"Участники: {participants}. "
        f"Значение: {significance}. "
        f"Сделай текст информативным, но живым и интересным. "
        f"Добавь эмодзи и релевантные хештеги."
    )

def create_news_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки новости"""
    event = data.get('news_event', 'новость')
    return f"Новостное событие {event}, позитивные изменения, социальная активность, яркое изображение, информационный стиль"

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "❤️ ИСТОРИЯ"
# =============================================================================

@router.message(TemplateStates.story_subject)
async def process_story_subject(message: types.Message, state: FSMContext):
    """Обработка субъекта истории"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(story_subject="наш подопечный")
    else:
        await state.update_data(story_subject=message.text)
    
    await state.set_state(TemplateStates.story_situation)
    await message.answer(
        "**🎭 Какая была ситуация?**\n"
        "_Пример: Он был голодный, испуганный и жил в подвале_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.story_situation)
async def process_story_situation(message: types.Message, state: FSMContext):
    """Обработка исходной ситуации"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.story_subject)
        await message.answer(
            "**👤 О ком эта история?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(story_situation="была сложная жизненная ситуация")
    else:
        await state.update_data(story_situation=message.text)
    
    await state.set_state(TemplateStates.story_changes)
    await message.answer(
        "**🔄 Что изменилось?**\n"
        "_Пример: Волонтеры забрали его в приют, вылечили и нашли семью_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.story_changes)
async def process_story_changes(message: types.Message, state: FSMContext):
    """Обработка изменений в истории"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.story_situation)
        await message.answer(
            "**🎭 Какая была ситуация?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(story_changes="ситуация улучшилась благодаря помощи")
    else:
        await state.update_data(story_changes=message.text)
    
    await state.set_state(TemplateStates.story_ending)
    await message.answer(
        "**💖 Какой финал истории?**\n"
        "_Пример: Теперь Барсик обрел дом и живет в любящей семье_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.story_ending)
async def process_story_ending(message: types.Message, state: FSMContext):
    """Обработка финала истории"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.story_changes)
        await message.answer(
            "**🔄 Что изменилось?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(story_ending="теперь всё хорошо")
    else:
        await state.update_data(story_ending=message.text)
    
    await state.set_state(TemplateStates.story_message)
    await message.answer(
        "**🎯 Какой главный посыл?**\n"
        "_Пример: Каждое животное заслуживает шанса на счастливую жизнь_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.story_message)
async def process_story_message(message: types.Message, state: FSMContext):
    """Обработка посыла истории"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.story_ending)
        await message.answer(
            "**💖 Какой финал истории?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(story_message="доброта меняет жизни")
    else:
        await state.update_data(story_message=message.text)
    
    # Все данные собраны - генерируем историю
    await generate_story_post(message, state)

async def generate_story_post(message: types.Message, state: FSMContext):
    """Генерация поста-истории"""
    data = await state.get_data()
    
    prompt = create_story_prompt(data)
    
    await message.answer("**Спасибо за информацию!**")
    await message.answer("**⏳ Создаю для вас трогательную историю...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "художественный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_story_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании истории: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания истории: {e}")
    
    await state.clear()

def create_story_prompt(data: dict) -> str:
    """Создает промпт для генерации истории"""
    subject = data.get('story_subject', 'герой')
    situation = data.get('story_situation', 'сложная ситуация')
    changes = data.get('story_changes', 'положительные изменения')
    ending = data.get('story_ending', 'счастливый финал')
    message = data.get('story_message', 'доброта важна')
    
    return (
        f"Создай трогательную историю для социальных сетей. "
        f"Главный герой: {subject}. "
        f"Исходная ситуация: {situation}. "
        f"Что изменилось: {changes}. "
        f"Финал: {ending}. "
        f"Главный посыл: {message}. "
        f"Сделай текст эмоциональным, трогательным, с элементами сторителлинга. "
        f"Добавь эмодзи и релевантные хештеги."
    )

def create_story_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки истории"""
    subject = data.get('story_subject', 'история')
    return f"Трогательная история {subject}, эмоциональное изображение, доброта, преобразование, художественный стиль"

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "👥 ПОИСК ВОЛОНТЕРОВ"
# =============================================================================

@router.message(TemplateStates.volunteers_event)
async def process_volunteers_event(message: types.Message, state: FSMContext):
    """Обработка мероприятия для поиска волонтеров"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_event="наш проект")
    else:
        await state.update_data(volunteers_event=message.text)
    
    await state.set_state(TemplateStates.volunteers_date)
    await message.answer(
        "**📅 Когда требуется помощь?**\n"
        "_Пример: 20 мая с 10:00 до 14:00_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_date)
async def process_volunteers_date(message: types.Message, state: FSMContext):
    """Обработка даты помощи"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_event)
        await message.answer(
            "**🎪 Для какого мероприятия/проекта нужны волонтеры?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_date="в ближайшее время")
    else:
        await state.update_data(volunteers_date=message.text)
    
    await state.set_state(TemplateStates.volunteers_place)
    await message.answer(
        "**📍 Где нужно помочь?**\n"
        "_Пример: г. Снежинск, парк Смолинка у центрального входа_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_place)
async def process_volunteers_place(message: types.Message, state: FSMContext):
    """Обработка места помощи"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_date)
        await message.answer(
            "**📅 Когда требуется помощь?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_place="в нашем городе")
    else:
        await state.update_data(volunteers_place=message.text)
    
    await state.set_state(TemplateStates.volunteers_tasks)
    await message.answer(
        "**🛠 Что нужно делать?**\n"
        "_Пример: Убирать мусор, сажать цветы, красить скамейки_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_tasks)
async def process_volunteers_tasks(message: types.Message, state: FSMContext):
    """Обработка задач волонтеров"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_place)
        await message.answer(
            "**📍 Где нужно помочь?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_tasks="помогать в различных задачах")
    else:
        await state.update_data(volunteers_tasks=message.text)
    
    await state.set_state(TemplateStates.volunteers_requirements)
    await message.answer(
        "**👤 Какие требования к волонтерам?**\n"
        "_Пример: Без ограничений по возрасту_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_requirements)
async def process_volunteers_requirements(message: types.Message, state: FSMContext):
    """Обработка требований к волонтерам"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_tasks)
        await message.answer(
            "**🛠 Что нужно делать?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_requirements="желание помогать")
    else:
        await state.update_data(volunteers_requirements=message.text)
    
    await state.set_state(TemplateStates.volunteers_benefits)
    await message.answer(
        "**🎁 Что получат волонтеры?**\n"
        "_Пример: Обед, сувениры, благодарственные письма_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_benefits)
async def process_volunteers_benefits(message: types.Message, state: FSMContext):
    """Обработка преимуществ для волонтеров"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_requirements)
        await message.answer(
            "**👤 Какие требования к волонтерам?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_benefits="хорошую компанию и благодарность")
    else:
        await state.update_data(volunteers_benefits=message.text)
    
    await state.set_state(TemplateStates.volunteers_registration)
    await message.answer(
        "**✅ Нужна ли регистрация?**\n"
        "_Пример: Да, по ссылке [google.forms]_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.volunteers_registration)
async def process_volunteers_registration(message: types.Message, state: FSMContext):
    """Обработка регистрации волонтеров"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.volunteers_benefits)
        await message.answer(
            "**🎁 Что получат волонтеры?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(volunteers_registration="Регистрация по телефону")
    else:
        await state.update_data(volunteers_registration=message.text)
    
    # Все данные собраны - генерируем пост
    await generate_volunteers_post(message, state)

async def generate_volunteers_post(message: types.Message, state: FSMContext):
    """Генерация поста для поиска волонтеров"""
    data = await state.get_data()
    
    prompt = create_volunteers_prompt(data)
    
    await message.answer("**Спасибо за информацию!**")
    await message.answer("**⏳ Создаю для вас самое привлекающее объявление...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "разговорный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_volunteers_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании объявления: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания объявления для волонтеров: {e}")
    
    await state.clear()

def create_volunteers_prompt(data: dict) -> str:
    """Создает промпт для генерации текста поиска волонтеров"""
    event = data.get('volunteers_event', 'проект')
    date = data.get('volunteers_date', 'скоро')
    place = data.get('volunteers_place', 'в нашем городе')
    tasks = data.get('volunteers_tasks', 'помощь в различных задачах')
    requirements = data.get('volunteers_requirements', 'желание помогать')
    benefits = data.get('volunteers_benefits', 'хорошая компания')
    registration = data.get('volunteers_registration', 'Регистрация по телефону')
    
    return (
        f"Создай призыв к волонтерской помощи для социальных сетей. "
        f"Мероприятие/проект: {event}. "
        f"Дата и время: {date}. "
        f"Место: {place}. "
        f"Задачи волонтеров: {tasks}. "
        f"Требования: {requirements}. "
        f"Что получат волонтеры: {benefits}. "
        f"Регистрация: {registration}. "
        f"Сделай текст мотивирующим, дружелюбным, с призывом к действию. "
        f"Добавь эмодзи и релевантные хештеги для привлечения волонтеров."
    )

def create_volunteers_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки поиска волонтеров"""
    event = data.get('volunteers_event', 'волонтерство')
    return f"Волонтерская помощь {event}, команда, совместная работа, позитивные эмоции, мультяшный стиль"


# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "📊 ОТЧЁТ"
# =============================================================================

@router.message(TemplateStates.report_period)
async def process_report_period(message: types.Message, state: FSMContext):
    """Обработка периода отчета"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_period="за последний период")
    else:
        await state.update_data(report_period=message.text)
    
    await state.set_state(TemplateStates.report_results)
    await message.answer(
        "**🎯 Какие самые главные результаты достигнуты?**\n"
        "_Пример: Помогли 25 семьям, нашли дом для 15 животных, посадили 100 деревьев_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.report_results)
async def process_report_results(message: types.Message, state: FSMContext):
    """Обработка результатов отчета"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.report_period)
        await message.answer(
            "**📅 За какой период составляем отчет?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_results="достигнуты значительные результаты")
    else:
        await state.update_data(report_results=message.text)
    
    await state.set_state(TemplateStates.report_finance)
    await message.answer(
        "**💰 Есть ли финансовые показатели? (Сборы и расходы)**\n"
        "_Пример: Собрано 500 000 рублей, потрачено на программы помощи 450 000 рублей_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.report_finance)
async def process_report_finance(message: types.Message, state: FSMContext):
    """Обработка финансовых показателей"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.report_results)
        await message.answer(
            "**🎯 Какие самые главные результаты достигнуты?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_finance="средства направлены на уставные цели")
    else:
        await state.update_data(report_finance=message.text)
    
    await state.set_state(TemplateStates.report_volunteers)
    await message.answer(
        "**👥 Расскажите про участие волонтеров (количество и активность)**\n"
        "_Пример: 50 волонтеров провели в сумме 200 часов работ_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.report_volunteers)
async def process_report_volunteers(message: types.Message, state: FSMContext):
    """Обработка информации о волонтерах"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.report_finance)
        await message.answer(
            "**💰 Есть ли финансовые показатели?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_volunteers="активное участие волонтеров")
    else:
        await state.update_data(report_volunteers=message.text)
    
    await state.set_state(TemplateStates.report_events)
    await message.answer(
        "**🌟 Какие самые значимые события произошли за этот период?**\n"
        "_Пример: Открыли новую программу помощи, провели 3 городских субботника_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.report_events)
async def process_report_events(message: types.Message, state: FSMContext):
    """Обработка значимых событий"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.report_volunteers)
        await message.answer(
            "**👥 Расскажите про участие волонтеров**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_events="проведены важные мероприятия")
    else:
        await state.update_data(report_events=message.text)
    
    await state.set_state(TemplateStates.report_plans)
    await message.answer(
        "**🎯 Какие планы на следующий период?**\n"
        "_Пример: Расширить помощь ещё на 10 семей, привлечь 20 новых волонтеров_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.report_plans)
async def process_report_plans(message: types.Message, state: FSMContext):
    """Обработка планов на будущее"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.report_events)
        await message.answer(
            "**🌟 Какие самые значимые события произошли?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(report_plans="продолжить и расширить деятельность")
    else:
        await state.update_data(report_plans=message.text)
    
    # Все данные собраны - генерируем отчет
    await generate_report_post(message, state)

async def generate_report_post(message: types.Message, state: FSMContext):
    """Генерация поста-отчета"""
    data = await state.get_data()
    
    prompt = create_report_prompt(data)
    
    await message.answer("**Спасибо! Всё учёл! 🐾**")
    await message.answer("**⏳ Формирую ясный и структурированный отчет...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "официальный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_report_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании отчета: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания отчета: {e}")
    
    await state.clear()

def create_report_prompt(data: dict) -> str:
    """Создает промпт для генерации текста отчета"""
    period = data.get('report_period', 'период')
    results = data.get('report_results', 'результаты')
    finance = data.get('report_finance', 'финансовые показатели')
    volunteers = data.get('report_volunteers', 'участие волонтеров')
    events = data.get('report_events', 'события')
    plans = data.get('report_plans', 'планы на будущее')
    
    return (
        f"Создай информативный отчет для социальных сетей. "
        f"Период: {period}. "
        f"Главные результаты: {results}. "
        f"Финансовые показатели: {finance}. "
        f"Участие волонтеров: {volunteers}. "
        f"Значимые события: {events}. "
        f"Планы на будущее: {plans}. "
        f"Сделай текст структурированным, информативным, но доступным для понимания. "
        f"Используй эмодзи для визуального разделения блоков. "
        f"Добавь благодарности и релевантные хештеги."
    )

def create_report_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки отчета"""
    period = data.get('report_period', 'отчет')
    return f"Инфографика отчета {period}, графики роста, статистика, достижения, профессиональный стиль"

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "🚨 СРОЧНЫЙ СБОР"
# =============================================================================

@router.message(TemplateStates.emergency_situation)
async def process_emergency_situation(message: types.Message, state: FSMContext):
    """Обработка срочной ситуации"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_situation="требуется срочная помощь")
    else:
        await state.update_data(emergency_situation=message.text)
    
    await state.set_state(TemplateStates.emergency_deadline)
    await message.answer(
        "**⏰ В какие сроки нужна помощь?**\n"
        "_Пример: Помощь нужна в течение 48 часов_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_deadline)
async def process_emergency_deadline(message: types.Message, state: FSMContext):
    """Обработка сроков помощи"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_situation)
        await message.answer(
            "**🚨 Что случилось? Опишите ситуацию.**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_deadline="срочно")
    else:
        await state.update_data(emergency_deadline=message.text)
    
    await state.set_state(TemplateStates.emergency_needs)
    await message.answer(
        "**💸 Что конкретно требуется? (Предметы, ресурсы)**\n"
        "_Пример: Корм, лекарства, стройматериалы для ремонта, переноски для животных_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_needs)
async def process_emergency_needs(message: types.Message, state: FSMContext):
    """Обработка необходимых предметов"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_deadline)
        await message.answer(
            "**⏰ В какие сроки нужна помощь?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_needs="любая помощь")
    else:
        await state.update_data(emergency_needs=message.text)
    
    await state.set_state(TemplateStates.emergency_finance)
    await message.answer(
        "**💰 Нужны ли денежные средства? Если да, укажите цель и сумму.**\n"
        "_Пример: Да, 300 000 рублей на срочный ремонт вольеров_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_finance)
async def process_emergency_finance(message: types.Message, state: FSMContext):
    """Обработка финансовых нужд"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_needs)
        await message.answer(
            "**💸 Что конкретно требуется?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_finance="финансовая помощь не требуется")
    else:
        await state.update_data(emergency_finance=message.text)
    
    await state.set_state(TemplateStates.emergency_contacts)
    await message.answer(
        "**📞 Куда/кому переводить деньги или привозить помощь? (Реквизиты, адрес)**\n"
        "_Пример: По номеру счета 8372 3990 3837 3932 в любом банке, или по адресу: ул. Пушкина, 10_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_contacts)
async def process_emergency_contacts(message: types.Message, state: FSMContext):
    """Обработка контактной информации"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_finance)
        await message.answer(
            "**💰 Нужны ли денежные средства?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_contacts="контакты будут сообщены дополнительно")
    else:
        await state.update_data(emergency_contacts=message.text)
    
    await state.set_state(TemplateStates.emergency_help_types)
    await message.answer(
        "**👥 Чья еще помощь требуется? (Волонтеры, специалисты)**\n"
        "_Пример: Нужны волонтеры для разбора завалов, водители для перевозки_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_help_types)
async def process_emergency_help_types(message: types.Message, state: FSMContext):
    """Обработка типов помощи"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_contacts)
        await message.answer(
            "**📞 Куда/кому переводить помощь?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_help_types="любая посильная помощь")
    else:
        await state.update_data(emergency_help_types=message.text)
    
    await state.set_state(TemplateStates.emergency_phone)
    await message.answer(
        "**📱 Контакты для экстренной связи**\n"
        "_Пример: +7 (999) 123-45-67 (Анна), круглосуточно_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.emergency_phone)
async def process_emergency_phone(message: types.Message, state: FSMContext):
    """Обработка телефона для связи"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.emergency_help_types)
        await message.answer(
            "**👥 Чья еще помощь требуется?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(emergency_phone="контакты в профиле организации")
    else:
        await state.update_data(emergency_phone=message.text)
    
    # Все данные собраны - генерируем срочный сбор
    await generate_emergency_post(message, state)

async def generate_emergency_post(message: types.Message, state: FSMContext):
    """Генерация поста срочного сбора"""
    data = await state.get_data()
    
    prompt = create_emergency_prompt(data)
    
    await message.answer("**Ясно! Действуем быстро! 🐾**")
    await message.answer("**⏳ Создаю максимально заметный и побуждающий к действию пост...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "эмоциональный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_emergency_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании срочного сбора: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания срочного сбора: {e}")
    
    await state.clear()

def create_emergency_prompt(data: dict) -> str:
    """Создает промпт для генерации текста срочного сбора"""
    situation = data.get('emergency_situation', 'срочная ситуация')
    deadline = data.get('emergency_deadline', 'срочно')
    needs = data.get('emergency_needs', 'помощь')
    finance = data.get('emergency_finance', 'финансовая помощь')
    contacts = data.get('emergency_contacts', 'контакты')
    help_types = data.get('emergency_help_types', 'помощь')
    phone = data.get('emergency_phone', 'телефон')
    
    return (
        f"Создай срочный призыв о помощи для социальных сетей. "
        f"Ситуация: {situation}. "
        f"Сроки: {deadline}. "
        f"Что требуется: {needs}. "
        f"Финансовая помощь: {finance}. "
        f"Куда обращаться: {contacts}. "
        f"Какая помощь нужна: {help_types}. "
        f"Контакты для связи: {phone}. "
        f"Сделай текст максимально urgent, эмоциональным, с четким призывом к действию. "
        f"Используй срочные эмодзи (🚨, ⚠️, 🔥). "
        f"Добавь релевантные хештеги для быстрого распространения."
    )

def create_emergency_image_prompt(data: dict) -> str:
    """Создает промпт для генерации картинки срочного сбора"""
    situation = data.get('emergency_situation', 'срочная помощь')
    return f"Срочный призыв о помощи {situation}, экстренная ситуация, urgency, красный цвет, тревожная атмосфера"

# =============================================================================
# ОБРАБОТЧИКИ ДЛЯ ШАБЛОНА "🎊 ПОЗДРАВЛЕНИЕ"
# =============================================================================

@router.message(TemplateStates.congrats_who)
async def process_congrats_who(message: types.Message, state: FSMContext):
    """Обработка объекта поздравления"""
    if message.text == "🔙 НАЗАД":
        from app.handlers.post_creation import start_template_selection
        await start_template_selection(message, state)
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(congrats_who="наших друзей и партнеров")
    else:
        await state.update_data(congrats_who=message.text)
    
    await state.set_state(TemplateStates.congrats_occasion)
    await message.answer(
        "**🎯 С каким событием?**\n"
        "_Пример: С Международным днем волонтера!_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.congrats_occasion)
async def process_congrats_occasion(message: types.Message, state: FSMContext):
    """Обработка повода для поздравления"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.congrats_who)
        await message.answer(
            "**🎉 Кого мы поздравляем?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(congrats_occasion="с праздником")
    else:
        await state.update_data(congrats_occasion=message.text)
    
    await state.set_state(TemplateStates.congrats_thanks)
    await message.answer(
        "**💖 Что бы вы хотели сказать, какую благодарность выразить?**\n"
        "_Пример: Огромное спасибо за ваше бесценное время, энергию и добрые сердца! Без вас ничего бы не получилось!_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.congrats_thanks)
async def process_congrats_thanks(message: types.Message, state: FSMContext):
    """Обработка благодарности"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.congrats_occasion)
        await message.answer(
            "**🎯 С каким событием?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(congrats_thanks="большое спасибо за все")
    else:
        await state.update_data(congrats_thanks=message.text)
    
    await state.set_state(TemplateStates.congrats_achievements)
    await message.answer(
        "**🌟 Какие конкретные достижения или заслуги хотите отметить?**\n"
        "_Пример: Благодаря вам мы помогли 1000+ животным за этот год и провели 50+ мероприятий!_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.congrats_achievements)
async def process_congrats_achievements(message: types.Message, state: FSMContext):
    """Обработка достижений"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.congrats_thanks)
        await message.answer(
            "**💖 Что бы вы хотели сказать?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(congrats_achievements="многочисленные достижения")
    else:
        await state.update_data(congrats_achievements=message.text)
    
    await state.set_state(TemplateStates.congrats_wishes)
    await message.answer(
        "**✨ Ваши пожелания на будущее**\n"
        "_Пример: Новых свершений, неиссякаемого вдохновения и чтобы ваша доброта возвращалась к вам сторицей!_",
        reply_markup=get_skip_keyboard()
    )

@router.message(TemplateStates.congrats_wishes)
async def process_congrats_wishes(message: types.Message, state: FSMContext):
    """Обработка пожеланий"""
    if message.text == "🔙 НАЗАД":
        await state.set_state(TemplateStates.congrats_achievements)
        await message.answer(
            "**🌟 Какие достижения хотите отметить?**",
            reply_markup=get_skip_keyboard()
        )
        return
    elif message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(congrats_wishes="всего самого наилучшего")
    else:
        await state.update_data(congrats_wishes=message.text)
    
    # Все данные собраны - генерируем поздравление
    await generate_congrats_post(message, state)

async def generate_congrats_post(message: types.Message, state: FSMContext):
    """Генерация поздравительного поста"""
    data = await state.get_data()
    
    prompt = create_congrats_prompt(data)
    
    await message.answer("**Прекрасно! Так и напишем! 😻**")
    await message.answer("**⏳ Создаю самое душевное и красивое поздравление...**")
    
    try:
        # Генерируем текст
        nko_data = await state.get_data()
        generated_text = await asyncio.to_thread(
            generate_text_sync, prompt, "художественный", nko_data
        )
        
        # Генерируем картинку
        image_prompt = create_congrats_image_prompt(data)
        image_path = await generate_image_async(image_prompt)
        
        # Отправляем результат
        photo = FSInputFile(image_path)
        await message.answer_photo(
            photo=photo,
            caption=generated_text,
            reply_markup=get_after_post_keyboard()
        )
        
        # Сохраняем данные
        await state.update_data(
            last_post_text=generated_text,
            last_image_path=image_path
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при создании поздравления: {str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания поздравления: {e}")
    
    await state.clear()

def create_congrats_prompt(data: dict) -> str:
    """Создает промпт для генерации поздравительного текста"""
    who = data.get('congrats_who', 'всех')
    occasion = data.get('congrats_occasion', 'праздником')
    thanks = data.get('congrats_thanks', 'спасибо')
    achievements = data.get('congrats_achievements', 'достижения')
    wishes = data.get('congrats_wishes', 'пожелания')
    
    return (
        f"Создай теплое поздравительное сообщение для социальных сетей. "
        f"Кого поздравляем: {who}. "
        f"Событие: {occasion}. "
        f"Благодарность: {thanks}. "
        f"Отмечаемые достижения: {achievements}. "
        f"Пожелания: {wishes}. "
        f"Сделай текст душевным, теплым, эмоциональным. "
        f"Используй праздничные эмодзи (🎉, 🎊, ❤️, ✨). "
        f"Добавь релевантные хештеги."
    )

def create_congrats_image_prompt(data: dict) -> str:
    """Создает промпт для генерации поздравительной картинки"""
    occasion = data.get('congrats_occasion', 'праздник')
    return f"Поздравительная открытка {occasion}, праздничная атмосфера, салют, конфетти, яркие цвета"