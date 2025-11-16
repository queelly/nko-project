from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_settings_keyboard,
    get_back_keyboard
)

router = Router()

@router.message(F.text == "⚙️ НАСТРОЙКИ")
async def show_settings(message: types.Message, state: FSMContext):
    """Показ настроек"""
    # Получаем текущие данные пользователя
    user_data = await state.get_data()
    nko_data = user_data.get('nko_data', {})
    
    if nko_data and nko_data.get('has_nko_info'):
        nko_info = f"""
**🏢 Информация об НКО:**
• **Название:** {nko_data.get('nko_name', 'Не указано')}
• **Миссия:** {nko_data.get('nko_mission', 'Не указано')}
• **Деятельность:** {nko_data.get('nko_activities', 'Не указано')}
• **Аудитория:** {nko_data.get('nko_audience', 'Не указано')}
"""
    else:
        nko_info = "**🏢 Информация об НКО:** Не настроено\n\nРасскажите о вашей организации для персонализации контента!"
    
    settings_text = (
        "**⚙️ НАСТРОЙКИ ДОБРОБОТА**\n\n"
        f"{nko_info}\n\n"
        "Выберите раздел для настройки:"
    )
    
    await message.answer(settings_text, reply_markup=get_settings_keyboard())

@router.message(F.text == "🏢 ИНФОРМАЦИЯ ОБ НКО")
async def show_nko_settings(message: types.Message, state: FSMContext):
    """Настройки информации об НКО"""
    user_data = await state.get_data()
    nko_data = user_data.get('nko_data', {})
    
    if nko_data and nko_data.get('has_nko_info'):
        nko_text = (
            f"**Текущие данные вашей НКО:**\n\n"
            f"• **Название:** {nko_data.get('nko_name')}\n"
            f"• **Миссия:** {nko_data.get('nko_mission')}\n"
            f"• **Деятельность:** {nko_data.get('nko_activities')}\n"
            f"• **Аудитория:** {nko_data.get('nko_audience')}\n\n"
            f"Хотите изменить информацию?"
        )
    else:
        nko_text = (
            "**Информация об НКО не настроена.**\n\n"
            "Расскажите о вашей организации, чтобы я мог создавать персонализированный контент!"
        )
    
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    nko_settings_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✏️ ИЗМЕНИТЬ ИНФОРМАЦИЮ"), KeyboardButton(text="❌ ОЧИСТИТЬ ДАННЫЕ")],
            [KeyboardButton(text="🔙 НАЗАД В НАСТРОЙКИ")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(nko_text, reply_markup=nko_settings_keyboard)

@router.message(F.text == "✏️ ИЗМЕНИТЬ ИНФОРМАЦИЮ")
async def edit_nko_info(message: types.Message, state: FSMContext):
    """Изменение информации об НКО"""
    from app.handlers.nko_info import show_nko_info_start
    await show_nko_info_start(message, state)

@router.message(F.text == "❌ ОЧИСТИТЬ ДАННЫЕ")
async def clear_nko_data(message: types.Message, state: FSMContext):
    """Очистка данных об НКО"""
    await state.update_data(nko_data=None)
    await message.answer(
        "✅ Данные об НКО успешно очищены!\n\n"
        "Теперь контент будет создаваться в общем стиле. "
        "Вы всегда можете снова рассказать о вашей организации.",
        reply_markup=get_settings_keyboard()
    )

@router.message(F.text == "🎨 НАСТРОЙКИ СТИЛЯ")
async def show_style_settings(message: types.Message, state: FSMContext):
    """Настройки стиля контента"""
    style_text = (
        "**🎨 НАСТРОЙКИ СТИЛЯ КОНТЕНТА**\n\n"
        "Здесь вы можете настроить предпочтительный стиль для генерируемого контента.\n\n"
        "**Доступные стили:**\n"
        "• 💬 **Разговорный** - неформальный, дружелюбный\n"
        "• 🏢 **Официальный** - структурированный, деловой\n"
        "• 🎨 **Художественный** - творческий, образный\n"
        "• ❤️ **Эмоциональный** - выразительный, чувственный\n\n"
        "Стиль можно выбрать при создании каждого поста."
    )
    
    await message.answer(style_text, reply_markup=get_back_keyboard())

@router.message(F.text == "🔔 УВЕДОМЛЕНИЯ")
async def show_notification_settings(message: types.Message, state: FSMContext):
    """Настройки уведомлений"""
    notification_text = (
        "**🔔 НАСТРОЙКИ УВЕДОМЛЕНИЙ**\n\n"
        "В будущих версиях здесь можно будет настроить:\n\n"
        "⏰ **Напоминания о публикациях**\n"
        "📅 **Уведомления о событиях**\n"
        "🎯 **Советы по контенту**\n"
        "📊 **Отчеты о активности**\n\n"
        "Следите за обновлениями!"
    )
    
    await message.answer(notification_text, reply_markup=get_back_keyboard())

@router.message(F.text == "📊 СТАТИСТИКА")
async def show_statistics(message: types.Message, state: FSMContext):
    """Показ статистики"""
    # В реальном приложении здесь была бы статистика из базы данных
    stats_text = (
        "**📊 ВАША СТАТИСТИКА**\n\n"
        "🔄 **Создано постов:** 15\n"
        "🎨 **Сгенерировано изображений:** 8\n"
        "⭐ **Сохранено в избранное:** 5\n"
        "📅 **Контент-планов создано:** 3\n\n"
        "**Активность за месяц:**\n"
        "• Наиболее популярный тип постов: 📢 Анонсы\n"
        "• Чаще всего используется стиль: 💬 Разговорный\n"
        "• Среднее время создания поста: 2 минуты\n\n"
        "Статистика обновляется в реальном времени!"
    )
    
    await message.answer(stats_text, reply_markup=get_back_keyboard())

@router.message(F.text == "🔙 НАЗАД В НАСТРОЙКИ")
async def back_to_settings(message: types.Message, state: FSMContext):
    """Возврат к настройкам"""
    await show_settings(message, state)