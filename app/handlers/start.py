from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from app.utils.keyboards import (
    get_start_keyboard, 
    get_nko_intro_keyboard,
    get_main_menu_keyboard,
    get_about_bot_keyboard
)
from app.utils.states import StartStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Обработчик команды /start - стартовый экран с котом"""
    await state.clear()
    
    # Очищаем предыдущие данные НКО при новом старте
    await state.update_data(nko_data=None)
    
    welcome_text = (
        "**Мяу! 🐱** Я кот Добробот — ваш личный копирайтер и дизайнер для "
        "добрых дел! Давайте вместе создавать крутой контент, который поможет "
        "вашему НКО делать мир лучше!"
    )
    
    await message.answer(welcome_text, reply_markup=get_start_keyboard())
    await state.set_state(StartStates.waiting_for_start_choice)

@router.message(StartStates.waiting_for_start_choice)
async def process_start_choice(message: types.Message, state: FSMContext):
    """Обработка выбора на стартовом экране"""
    if message.text == "🏠 НАЧНЁМ!":
        await show_nko_intro(message, state)
    elif message.text == "ℹ️ О БОТЕ":
        await show_about_bot(message, state)
    else:
        await message.answer("Пожалуйста, выберите действие из меню ниже:")

async def show_nko_intro(message: types.Message, state: FSMContext):
    """Показ введения после нажатия НАЧНЁМ!"""
    intro_text = (
        "**Мур-мур!** Я очень рад, что вы выбрали меня в помощники! "
        "Давайте создадим вашу уникальную историю с НКО? "
        "Всего 2 минуты — и я стану вашим персональным SMM-гением! 🚀\n\n"
        
        "Я научусь:\n"
        "🎯 Говорить голосом вашей организации\n"
        "🎨 Создавать контент, который цепляет за душу\n"  
        "👥 Привлекать волонтеров и доноров\n"
        "💫 Выделять вас среди других НКО"
    )
    
    await message.answer(intro_text, reply_markup=get_nko_intro_keyboard())
    await state.set_state(StartStates.waiting_for_nko_choice)

# ... остальной код start.py без изменений ...

async def show_about_bot(message: types.Message, state: FSMContext):
    """Показ информации о боте"""
    about_text = (
        "**Мяу! Давайте познакомимся поближе!** Я — ваш пушистый помощник, "
        "созданный специально для НКО!\n\n"
        
        "**Что я умею:**\n"
        "📝 **Создавать посты** — от анонсов до трогательных историй с картинками! 🎨\n"
        "✏️ **Проверять тексты** — как котик с красной ручкой! 🖊️\n"  
        "📅 **Составлять контент-планы** — чтобы ничего не забыть!\n"
        "⭐ **Сохранять лучшее** — в нашу кото-коллекцию!\n\n"
        
        "**Почему я особенный?** 🌟\n"
        "🐾 Работаю в **Telegram** — удобно и привычно!\n"
        "❤️ Понимаю **вашу миссию** — становлюсь частью команды!\n"
        "🚀 Делаю всё **быстро** — от идеа до поста за 1 минуту!\n"
        "🎨 Добавляю **котиков** — потому что без них грустно!\n\n"
        
        "**Кто меня создал?**\n"
        "Такие же энтузиасты, которые хотят помочь НКО делать мир лучше!\n"
        "Бот не работает или возникли вопросы / предложения по улучшению, пиши @elizacrai\n\n"
        
        "**Ну что, попробуем?**"
    )
    
    await message.answer(about_text, reply_markup=get_about_bot_keyboard())
    await state.set_state(StartStates.waiting_for_about_bot_choice)

@router.message(StartStates.waiting_for_about_bot_choice)
async def process_about_choice(message: types.Message, state: FSMContext):
    """Обработка выбора в разделе О БОТЕ"""
    if message.text == "🚀 ПОПРОБОВАТЬ":
        await show_nko_intro(message, state)
    elif message.text == "📚 ПРИМЕРЫ РАБОТ":
        await show_examples(message)
    elif message.text == "🐱 МОИ КОТО-ФИШКИ":
        await show_cat_features(message)
    elif message.text == "🔙 НАЗАД":
        await cmd_start(message, state)
    else:
        await message.answer("Пожалуйста, выберите действие из меню:")

async def show_examples(message: types.Message):
    """Показ примеров работ"""
    examples_text = (
        "**📚 Примеры моих работ:**\n\n"
        "✨ **Анонс мероприятия:**\n"
        "Приглашаем на эко-субботник! 🌿\n"
        "Когда: 15 мая, 11:00-14:00\n"
        "Где: Парк Смолинка\n"
        "Ждём всех, кто хочет сделать город чище! 🧹\n\n"
        
        "❤️ **Трогательная история:**\n"  
        "История кота Барсика: от улицы к любящей семье...\n"
        "Теперь у него есть дом! 🏠\n\n"
        
        "📊 **Отчет о работе:**\n"
        "За апрель помогли 25 семьям! 💫\n"
        "Собрано: 500,000 руб\n"
        "Волонтеры: 50 человек\n\n"
        
        "И многое другое! 🎨"
    )
    await message.answer(examples_text)

async def show_cat_features(message: types.Message):
    """Показ кото-фишек"""
    features_text = (
        "**🎩 Мои кото-суперсилы!**\n\n"
        "🐾 **Кото-мотиватор** — всегда поддерживаю вас мурлыканием!\n"
        "🎭 **Кото-стилист** — подбираю идеальный стиль для каждого поста!\n"  
        "📊 **Кото-аналитик** — оцениваю посты до публикации!\n"
        "🔔 **Кото-напоминалка** — не дам забыть о важных публикациях!\n"
        "💾 **Кото-коллекционер** — бережно храню все ваши лучшие работы!\n"
        "👥 **Кото-команда** — работаю с целыми группами волонтёров!"
    )
    await message.answer(features_text)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "**📋 Доступные функции:**\n\n"
        "📝 **Создать пост с картинкой** — полные посты с визуалом\n"
        "🎨 **Создать картинку** — только визуальный контент\n"  
        "✍️ **Создать текст для поста** — текстовый контент\n"
        "✏️ **Проверить текст** — редактор и улучшение текстов\n"
        "📅 **Контент-план** — планирование публикаций\n"
        "⭐ **Избранное** — сохраненные работы\n"
        "⚙️ **Настройки** — настройки бота\n"
        "💬 **Поддержка** — помощь и обратная связь\n\n"
        
        "<i>Бот работает в личных и групповых чатах!</i>"
    )
    await message.answer(help_text)

@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Отмена текущей операции"""
    await state.clear()
    await message.answer(
        "Операция отменена. Возвращаюсь в главное меню!",
        reply_markup=get_main_menu_keyboard()
    )

# Глобальный обработчик для кнопки "Главное меню"
@router.message(F.text == "🔙 ГЛАВНОЕ МЕНЮ")
async def handle_global_main_menu(message: types.Message, state: FSMContext):
    """Обработка кнопки Главное меню из любого состояния"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())