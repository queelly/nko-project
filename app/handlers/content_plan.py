from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.states import ContentPlanStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_content_plan_period_keyboard,
    get_back_keyboard
)

router = Router()

@router.message(F.text == "📅 КОНТЕНТ-ПЛАН")
async def start_content_plan(message: types.Message, state: FSMContext):
    """Начало создания контент-плана"""
    # В будущем здесь будет картинка кота с календарем
    start_text = (
        "**📅 Планируем контент!** Выберите период:"
    )
    
    await message.answer(start_text, reply_markup=get_content_plan_period_keyboard())
    await state.set_state(ContentPlanStates.waiting_for_period)

@router.message(ContentPlanStates.waiting_for_period)
async def process_content_plan_period(message: types.Message, state: FSMContext):
    """Обработка выбора периода для контент-плана"""
    period_handlers = {
        "📌 НА ДЕНЬ": generate_daily_plan,
        "🗓️ НА НЕДЕЛЮ": generate_weekly_plan, 
        "📆 НА МЕСЯЦ": generate_monthly_plan,
        "🔔 НАСТРОИТЬ НАПОМИНАНИЯ": setup_reminders
    }
    
    if message.text in period_handlers:
        await period_handlers[message.text](message, state)
    elif message.text == "🔙 НАЗАД":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer("Пожалуйста, выберите период из меню:")

async def generate_daily_plan(message: types.Message, state: FSMContext):
    """Генерация контент-плана на день"""
    await message.answer("🔄 Создаю контент-план на день...")
    
    # TODO: Реализовать генерацию реального контент-плана
    daily_plan = (
        "**📌 Контент-план на день:**\n\n"
        "🌅 **Утро (9:00):**\n"
        "• Мотивационный пост с красивой картинкой\n"
        "• Хештеги: #доброеутро #мотивация\n\n"
        "🌞 **День (13:00):**\n"  
        "• Информационный пост о деятельности НКО\n"
        "• Хештеги: #нашаработа #помощь\n\n"
        "🌇 **Вечер (18:00):**\n"
        "• История успеха или благодарность волонтерам\n"
        "• Хештеги: #историяуспеха #спасибо\n\n"
        "💡 <i>В будущей версии план будет адаптироваться под вашу НКО!</i>"
    )
    
    await message.answer(daily_plan, reply_markup=get_main_menu_keyboard())
    await state.clear()

async def generate_weekly_plan(message: types.Message, state: FSMContext):
    """Генерация контент-плана на неделю"""
    await message.answer("🔄 Создаю контент-план на неделю...")
    
    weekly_plan = (
        "**🗓️ Контент-план на неделю:**\n\n"
        "📅 **Понедельник:** Анонс недели, планы и цели\n"
        "📅 **Вторник:** Информационный пост о проблеме\n"
        "📅 **Среда:** История успеха или кейс\n"
        "📅 **Четверг:** Призыв к действию или сбор\n"
        "📅 **Пятница:** Отчет о работе или благодарности\n"
        "📅 **Суббота:** Мотивационный пост, цитаты\n"
        "📅 **Воскресенье:** Итоги недели, интерактив\n\n"
        "💡 <i>Каждый день в 10:00 - лучшее время для публикаций!</i>"
    )
    
    await message.answer(weekly_plan, reply_markup=get_main_menu_keyboard())
    await state.clear()

async def generate_monthly_plan(message: types.Message, state: FSMContext):
    """Генерация контент-плана на месяц"""
    await message.answer("🔄 Создаю контент-план на месяц...")
    
    monthly_plan = (
        "**📆 Контент-план на месяц:**\n\n"
        "🎯 **1 неделя:** Знакомство с организацией\n"
        "• Презентация НКО, миссия, команда\n\n"
        "📊 **2 неделя:** Проблематика и решения\n"  
        "• О проблеме, которую решаем, наши методы\n\n"
        "❤️ **3 неделя:** Истории и результаты\n"
        "• Реальные кейсы, успехи, благодарности\n\n"
        "🚀 **4 неделя:** Призывы и участие\n"
        "• Волонтерство, донаты, мероприятия\n\n"
        "📈 **Рекомендации:**\n"
        "• 3-5 постов в неделю\n"
        "• Чередуйте типы контента\n"
        "• Используйте визуал\n"
        "• Вовлекайте аудиторию вопросами"
    )
    
    await message.answer(monthly_plan, reply_markup=get_main_menu_keyboard())
    await state.clear()

async def setup_reminders(message: types.Message, state: FSMContext):
    """Настройка напоминаний"""
    # TODO: Реализовать настройку напоминаний
    reminders_text = (
        "**🔔 Настройка напоминаний**\n\n"
        "В будущей версии здесь можно будет настроить:\n"
        "⏰ Напоминания о публикациях\n"
        "📅 Уведомления о события\n"
        "🎯 Советы по контенту\n\n"
        "А пока контент-план готов к использованию! 📋"
    )
    
    await message.answer(reminders_text, reply_markup=get_main_menu_keyboard())
    await state.clear()