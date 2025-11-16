from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.states import TextGenStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard
)
from app.services.ai_text_sync import generate_text_sync
import asyncio

router = Router()

@router.message(F.text == "✍️ СОЗДАТЬ ТЕКСТ ДЛЯ ПОСТА")
async def start_text_creation(message: types.Message, state: FSMContext):
    """Начало создания текста для поста"""
    start_text = (
        "**✍️ СОЗДАЕМ ТЕКСТ ДЛЯ ПОСТА!**\n\n"
        "Расскажите, о чем должен быть текст, и я создам:\n"
        "📝 Готовый пост для соцсетей\n"
        "🎯 Релевантные хештеги\n"  
        "💫 Уникальный контент под ваш стиль\n"
        "🚀 Текст, который цепляет аудиторию\n\n"
        "👇 **Опишите тему поста, ключевые моменты, целевую аудиторию:**"
    )
    
    await message.answer(start_text, reply_markup=get_back_keyboard())
    await state.set_state(TextGenStates.waiting_for_text_topic)

@router.message(TextGenStates.waiting_for_text_topic)
async def process_text_creation(message: types.Message, state: FSMContext):
    """Обработка запроса на создание текста"""
    if message.text == "🔙 НАЗАД":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    await message.answer("🔄 Создаю текст для поста...")
    
    try:
        # Получаем данные об НКО из состояния
        user_data = await state.get_data()
        nko_data = user_data.get('nko_data', {})
        
        # Запускаем синхронную функцию в отдельном потоке
        generated_text = await asyncio.to_thread(
            generate_text_sync, 
            message.text, 
            "разговорный",  # Стандартный стиль для текстовых постов
            nko_data
        )
        
        # Добавляем пояснение про картинку
        personalization_note = ""
        if nko_data and nko_data.get('has_nko_info'):
            personalization_note = "🎯 <i>Текст персонализирован под вашу НКО!</i>\n\n"
        else:
            personalization_note = "💡 <i>Для персонализации текста расскажите о вашей НКО в настройках</i>\n\n"
        
        final_text = (
            f"{generated_text}\n\n"
            f"{personalization_note}"
            f"💡 <i>Этот текст готов к использованию! "
            f"Хотите добавить картинку? Используйте функцию \"📝 СОЗДАТЬ ПОСТ С КАРТИНКОЙ\"</i>"
        )
        
        await message.answer(final_text, reply_markup=get_main_menu_keyboard())
        
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при создании текста. Попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )
        print(f"Ошибка создания текста: {e}")
    
    await state.clear()