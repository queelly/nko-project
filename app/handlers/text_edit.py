from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from app.utils.states import TextEditStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_back_keyboard,
    get_text_edit_keyboard
)
from app.services.ai_text_sync import generate_text_sync
import asyncio
import logging

logger = logging.getLogger(__name__)

router = Router()

# Глобальный обработчик для кнопки "Главное меню" - должен быть ПЕРВЫМ
@router.message(F.text == "🔙 ГЛАВНОЕ МЕНЮ")
@router.message(F.text == "📋 ГЛАВНОЕ МЕНЮ")
async def handle_global_main_menu(message: types.Message, state: FSMContext):
    """Обработка кнопки Главное меню из любого состояния"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())

@router.message(F.text == "✏️ ПРОВЕРИТЬ ТЕКСТ")
async def start_text_edit(message: types.Message, state: FSMContext):
    """Начало проверки текста"""
    # Очищаем состояние при входе
    await state.clear()
    
    start_text = (
        "**Пришлите текст, который нужно проверить!**\n\n"
        "Я исправлю ошибки и дам советы по улучшению. 📝"
    )
    
    await message.answer(start_text, reply_markup=get_back_keyboard())
    await state.set_state(TextEditStates.waiting_for_text)

@router.message(TextEditStates.waiting_for_text)
async def process_text_edit(message: types.Message, state: FSMContext):
    """Обработка текста для проверки"""
    if message.text == "🔙 НАЗАД":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text in ["🔙 ГЛАВНОЕ МЕНЮ", "📋 ГЛАВНОЕ МЕНЮ"]:
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    await message.answer("**✏️ Проверяю ваш текст...**")
    
    try:
        # Получаем данные об НКО для контекста
        user_data = await state.get_data()
        nko_data = user_data.get('nko_data', {})
        
        # Создаем промпт для проверки текста
        check_prompt = create_check_prompt(message.text, nko_data)
        
        # Используем AI для проверки текста
        checked_text = await asyncio.to_thread(
            generate_text_sync, check_prompt, "официальный", nko_data
        )
        
        await message.answer(checked_text, reply_markup=get_text_edit_keyboard())
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки текста: {e}")
        await message.answer(
            f"❌ Произошла ошибка при проверке текста: {str(e)}\nПопробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )
    
    await state.clear()

def create_check_prompt(text: str, nko_data: dict) -> str:
    """Создает промпт для проверки текста"""
    
    nko_context = ""
    if nko_data and nko_data.get('has_nko_info'):
        nko_context = f"""
Контекст организации:
- Название: {nko_data.get('nko_name', '')}
- Деятельность: {nko_data.get('nko_activities', '')}

"""
    
    return f"""{nko_context}
Проверь следующий текст и предоставь подробный анализ:

ТЕКСТ ДЛЯ ПРОВЕРКИ:
"{text}"

АНАЛИЗ ДОЛЖЕН ВКЛЮЧАТЬ:
1. **Исправленный текст** (исправь все ошибки)
2. **Орфографические ошибки** - список найденных и исправленных
3. **Грамматические ошибки** - объяснение и исправление
4. **Стилистические улучшения** - как сделать текст лучше
5. **Рекомендации по структуре** - если нужно улучшить композицию
6. **Подходящие хештеги** - 3-5 релевантных хештегов

Формат ответа:
Сначала исправленный текст, затем подробный анализ по пунктам."""

@router.message(F.text == "✏️ ПРОВЕРИТЬ ЕЩЕ ТЕКСТ")
async def edit_another_text(message: types.Message, state: FSMContext):
    """Проверка еще одного текста"""
    await start_text_edit(message, state)

@router.message(F.text == "📝 СОЗДАТЬ ТЕКСТ ДЛЯ ПОСТА")
async def create_text_from_edit(message: types.Message, state: FSMContext):
    """Переход к созданию текста из редактора"""
    from app.handlers.text_gen import start_text_creation
    await start_text_creation(message, state)