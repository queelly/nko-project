from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_support_keyboard,
    get_back_keyboard
)

router = Router()

@router.message(F.text == "💬 ПОДДЕРЖКА")
async def show_support(message: types.Message, state: FSMContext):
    """Показ раздела поддержки"""
    support_text = (
        "**💬 ПОДДЕРЖКА ДОБРОБОТА**\n\n"
        "Мы всегда готовы помочь! Выберите нужный раздел:\n\n"
        "📞 **Связаться с поддержкой** - прямая связь с разработчиками\n"
        "📝 **Оставить отзыв** - поделитесь впечатлениями и идеями\n\n"
        "**Часто задаваемые вопросы:**\n"
        "❓ **Как работает генерация контента?**\n"
        "→ Используются современные AI-модели для создания уникального контента\n\n"
        "❓ **Можно ли использовать бот для коммерческих организаций?**\n"
        "→ Бот создан специально для НКО, но может использоваться любыми организациями\n\n"
        "❓ **Сохраняются ли мои данные?**\n"
        "→ Данные хранятся локально и используются только для персонализации контента"
    )
    
    await message.answer(support_text, reply_markup=get_support_keyboard())

@router.message(F.text == "📞 СВЯЗАТЬСЯ С ПОДДЕРЖКОЙ")
async def contact_support(message: types.Message, state: FSMContext):
    """Связь с поддержкой"""
    contact_text = (
        "**📞 СВЯЗЬ С ПОДДЕРЖКОЙ**\n\n"
        "По всем вопросам работы бота обращайтесь:\n\n"
        "👤 **Разработчик:** @elizacrai\n"
        "💬 **Telegram канал:** скоро будет\n"
        "📧 **Email:** скоро будет\n\n"
        "**Время ответа:**\n"
        "• Обычно в течение 24 часов\n"
        "• В экстренных случаях быстрее\n\n"
        "При обращении укажите:\n"
        "1. Ваш вопрос или проблему\n"
        "2. Шаги для воспроизведения (если есть баг)\n"
        "3. Скриншоты (если нужно)\n\n"
        "Мы ценим каждого пользователя и постараемся помочь максимально быстро! 🐱"
    )
    
    await message.answer(contact_text, reply_markup=get_back_keyboard())

@router.message(F.text == "📝 ОСТАВИТЬ ОТЗЫВ")
async def leave_feedback(message: types.Message, state: FSMContext):
    """Оставить отзыв"""
    feedback_text = (
        "**📝 ОСТАВИТЬ ОТЗЫВ**\n\n"
        "Мы будем рады услышать ваше мнение о Доброботе!\n\n"
        "Расскажите:\n"
        "• Что вам нравится в боте?\n"
        "• Что можно улучшить?\n"
        "• Какие функции хотели бы видеть?\n"
        "• Общие впечатления от использования\n\n"
        "Отправьте ваш отзыв сообщением в этот чат, и мы его обязательно учтем при дальнейшей разработке!\n\n"
        "**Спасибо, что помогаете нам становиться лучше!** ❤️"
    )
    
    await message.answer(feedback_text, reply_markup=get_back_keyboard())
    
    # Устанавливаем состояние для получения отзыва
    from app.utils.states import FeedbackStates
    await state.set_state(FeedbackStates.waiting_for_feedback)

@router.message(F.text == "🔙 НАЗАД В ПОДДЕРЖКУ")
async def back_to_support(message: types.Message, state: FSMContext):
    """Возврат к поддержке"""
    await show_support(message, state)