from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.states import NKOStates, StartStates
from app.utils.keyboards import (
    get_main_menu_keyboard
)

router = Router()

# Обработчики для кнопок в состоянии выбора НКО
@router.message(StartStates.waiting_for_nko_choice, F.text == "✍️ РАССКАЗАТЬ О НКО")
@router.message(StartStates.waiting_for_nko_choice, F.text == "🚀 ПРОПУСТИТЬ")
async def process_nko_choice(message: types.Message, state: FSMContext):
    """Обработка выбора рассказать о НКО или пропустить (из стартового меню)"""
    if message.text == "✍️ РАССКАЗАТЬ О НКО":
        await start_nko_info(message, state)
    else:  # ПРОПУСТИТЬ
        await state.clear()
        await show_main_menu_after_skip(message)

# Обработчик для кнопки из главного меню
@router.message(F.text == "🏢 Информация об НКО")
async def start_nko_info_from_menu(message: types.Message, state: FSMContext):
    """Начало сбора информации об НКО из главного меню"""
    await start_nko_info(message, state)

# Функция для вызова из настроек
async def show_nko_info_start(message: types.Message, state: FSMContext):
    """Старт сбора информации об НКО (для вызова из настроек)"""
    await start_nko_info(message, state)

async def start_nko_info(message: types.Message, state: FSMContext):
    """Начало сбора информации об НКО"""
    # Сразу начинаем с названия НКО
    await state.set_state(NKOStates.waiting_for_nko_name)
    
    start_text = (
        "**🔍 Расскажите о вашей НКО**\n\n"
        "Шаг 1/4: **Введите название вашей НКО**\n\n"
        "_Можете просто скопировать его из официальных документов или придумать краткое описание._"
    )
    
    keyboard = get_nko_name_keyboard()
    await message.answer(start_text, reply_markup=keyboard)

def get_nko_name_keyboard():
    """Клавиатура для ввода названия НКО"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ ПРОПУСТИТЬ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_nko_mission_keyboard():
    """Клавиатура для ввода миссии НКО"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ ПРОПУСТИТЬ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_nko_activities_keyboard():
    """Клавиатура для ввода деятельности НКО"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ ПРОПУСТИТЬ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_nko_audience_keyboard():
    """Клавиатура для ввода аудитории НКО"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ ПРОПУСТИТЬ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

@router.message(NKOStates.waiting_for_nko_name)
async def process_nko_name(message: types.Message, state: FSMContext):
    """Обработка названия НКО"""
    if message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(nko_name="")
        await ask_nko_mission(message, state)
    elif message.text == "🔙 НАЗАД":
        # Возврат в стартовое меню
        from app.handlers.start import show_nko_intro
        await show_nko_intro(message, state)
    else:
        await state.update_data(nko_name=message.text)
        await ask_nko_mission(message, state)

async def ask_nko_mission(message: types.Message, state: FSMContext):
    """Запрос миссии НКО"""
    await state.set_state(NKOStates.waiting_for_nko_mission)
    
    question_text = (
        "**🎯 Шаг 2/4: Расскажите о миссии вашей НКО**\n\n"
        "_Чем занимаетесь? Кому помогаете? Какую проблему решаете?_"
    )
    
    keyboard = get_nko_mission_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

@router.message(NKOStates.waiting_for_nko_mission)
async def process_nko_mission(message: types.Message, state: FSMContext):
    """Обработка миссии НКО"""
    if message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(nko_mission="")
        await ask_nko_activities(message, state)
    elif message.text == "🔙 НАЗАД":
        await state.set_state(NKOStates.waiting_for_nko_name)
        await ask_nko_name_again(message, state)
    else:
        await state.update_data(nko_mission=message.text)
        await ask_nko_activities(message, state)

async def ask_nko_name_again(message: types.Message, state: FSMContext):
    """Повторный запрос названия НКО"""
    question_text = (
        "**🔍 Шаг 1/4: Введите название вашей НКО**\n\n"
        "_Можете просто скопировать его из официальных документов._"
    )
    
    keyboard = get_nko_name_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

async def ask_nko_activities(message: types.Message, state: FSMContext):
    """Запрос направлений деятельности"""
    await state.set_state(NKOStates.waiting_for_nko_activities)
    
    question_text = (
        "**🛠️ Шаг 3/4: Что конкретно вы делаете?**\n\n"
        "_Опишите основные направления деятельности, проекты, программы:_"
    )
    
    keyboard = get_nko_activities_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

@router.message(NKOStates.waiting_for_nko_activities)
async def process_nko_activities(message: types.Message, state: FSMContext):
    """Обработка направлений деятельности"""
    if message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(nko_activities="")
        await ask_nko_audience(message, state)
    elif message.text == "🔙 НАЗАД":
        await state.set_state(NKOStates.waiting_for_nko_mission)
        await ask_nko_mission_again(message, state)
    else:
        await state.update_data(nko_activities=message.text)
        await ask_nko_audience(message, state)

async def ask_nko_mission_again(message: types.Message, state: FSMContext):
    """Повторный запрос миссии НКО"""
    question_text = (
        "**🎯 Шаг 2/4: Расскажите о миссии вашей НКО**\n\n"
        "_Чем занимаетесь? Кому помогаете?_"
    )
    
    keyboard = get_nko_mission_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

async def ask_nko_audience(message: types.Message, state: FSMContext):
    """Запрос целевой аудитории"""
    await state.set_state(NKOStates.waiting_for_nko_audience)
    
    question_text = (
        "**👥 Шаг 4/4: Кто ваша целевая аудитория?**\n\n"
        "_С кем вы работаете? Кому помогаете? Кто ваши доноры/волонтеры?_"
    )
    
    keyboard = get_nko_audience_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

@router.message(NKOStates.waiting_for_nko_audience)
async def process_nko_audience(message: types.Message, state: FSMContext):
    """Обработка целевой аудитории"""
    if message.text == "⏩ ПРОПУСТИТЬ":
        await state.update_data(nko_audience="")
    elif message.text == "🔙 НАЗАД":
        await state.set_state(NKOStates.waiting_for_nko_activities)
        await ask_nko_activities_again(message, state)
        return
    else:
        await state.update_data(nko_audience=message.text)
    
    # Все данные собраны (возможно, с пропусками) - сохраняем
    nko_data = await state.get_data()
    
    # Формируем структурированные данные НКО
    structured_nko_data = {
        'nko_name': nko_data.get('nko_name', ''),
        'nko_mission': nko_data.get('nko_mission', ''),
        'nko_activities': nko_data.get('nko_activities', ''),
        'nko_audience': nko_data.get('nko_audience', ''),
        'has_nko_info': any([nko_data.get('nko_name'), nko_data.get('nko_mission'), nko_data.get('nko_activities'), nko_data.get('nko_audience')])
    }
    
    # Сохраняем в состоянии для использования в генерации
    await state.update_data(nko_data=structured_nko_data)
    await state.clear()
    
    # Показываем подтверждение и переходим в главное меню
    await show_nko_success(message, structured_nko_data)

async def ask_nko_activities_again(message: types.Message, state: FSMContext):
    """Повторный запрос деятельности НКО"""
    question_text = (
        "**🛠️ Шаг 3/4: Что конкретно вы делаете?**\n\n"
        "_Опишите основные направления деятельности:_"
    )
    
    keyboard = get_nko_activities_keyboard()
    await message.answer(question_text, reply_markup=keyboard)

async def show_nko_success(message: types.Message, nko_data: dict):
    """Показ успешного сохранения информации об НКО"""
    # Проверяем, есть ли хотя бы одно поле заполненным
    if nko_data.get('has_nko_info'):
        nko_name = nko_data.get('nko_name', 'Не указано')
        
        success_text = (
            f"**Отлично! Информация о вашей НКО сохранена!** 🎉\n\n"
            f"Теперь я буду создавать контент, учитывая особенности **{nko_name}**.\n\n"
            f"Вы всегда можете изменить эту информацию в разделе \"⚙️ Настройки\"."
        )
    else:
        success_text = (
            "**Информация об НКО не указана**\n\n"
            "Я буду создавать общие посты, которые подходят для любой НКО. "
            "Если захотите персонализировать контент — всегда можно вернуться "
            "и рассказать о вашей организации в настройках! 🐱"
        )
    
    await message.answer(success_text, reply_markup=get_main_menu_keyboard())

async def show_main_menu_after_skip(message: types.Message):
    """Показ главного меню после пропуска информации об НКО"""
    skip_text = (
        "**Понял!** Буду создавать общие посты, которые подходят для любой НКО. "
        "Если захотите персонализировать контент — всегда можно вернуться "
        "и рассказать о вашей организации в настройках! 🐱"
    )
    
    await message.answer(skip_text, reply_markup=get_main_menu_keyboard())