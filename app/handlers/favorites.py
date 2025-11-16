from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from app.utils.states import FavoritesStates
from app.utils.keyboards import get_main_menu_keyboard, get_back_keyboard
from app.services.favorites import favorites_service
import os
from datetime import datetime
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

# Глобальный обработчик для кнопки "Удалить из избранного"
@router.message(F.text == "❌ УДАЛИТЬ ИЗ ИЗБРАННОГО")
async def handle_global_delete_favorite(message: types.Message, state: FSMContext):
    """Глобальный обработчик удаления из избранного"""
    try:
        data = await state.get_data()
        post_id = data.get('selected_favorite_id')
        
        logger.info(f"Глобальный обработчик удаления для пользователя {message.from_user.id}, post_id: {post_id}")
        
        if not post_id:
            await message.answer(
                "❌ Сначала выберите пост из избранного!",
                reply_markup=get_back_to_favorites_keyboard()
            )
            return
        
        # Удаляем пост из избранного
        success = await favorites_service.delete_favorite(message.from_user.id, post_id)
        
        if success:
            await message.answer(
                "✅ Пост успешно удален из избранного!",
                reply_markup=get_main_menu_keyboard()
            )
            logger.info(f"✅ Пост {post_id} удален из избранного пользователя {message.from_user.id}")
            await state.clear()
        else:
            await message.answer(
                "❌ Не удалось удалить пост из избранного. Попробуйте еще раз.",
                reply_markup=get_back_to_favorites_keyboard()
            )
            logger.error(f"❌ Ошибка удаления поста {post_id} из избранного")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при удалении из избранного: {e}")
        await message.answer(
            "❌ Произошла ошибка при удалении. Попробуйте еще раз.",
            reply_markup=get_back_to_favorites_keyboard()
        )

@router.message(F.text == "⭐ ИЗБРАННОЕ")
async def show_favorites(message: types.Message, state: FSMContext):
    """Показ избранного"""
    await state.set_state(FavoritesStates.browsing_favorites)
    
    favorites = await favorites_service.get_favorites(message.from_user.id)
    
    if not favorites:
        empty_text = (
            "**⭐ Ваши сохранённые работы:**\n\n"
            "Пока здесь пусто... 😿\n\n"
            "Сохраняйте понравившиеся посты с помощью кнопки "
            "\"⭐ СОХРАНИТЬ В ИЗБРАННОЕ\" после их создания!"
        )
        await message.answer(empty_text, reply_markup=get_back_to_main_keyboard())
        return
    
    # Создаем клавиатуру с сохраненными постами
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = []
    for favorite in favorites[:8]:  # Показываем до 8 постов
        title = favorite.get('title', f"Пост #{favorite.get('id', '?')}")
        # Обрезаем длинные названия
        display_title = title[:30] + "..." if len(title) > 30 else title
        keyboard.append([KeyboardButton(text=f"📌 {display_title}")])
    
    keyboard.append([KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")])
    
    favorites_keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
    
    favorites_text = (
        "**⭐ Ваши сохранённые работы:**\n\n"
        f"Всего сохранено постов: {len(favorites)}\n\n"
        "Выберите пост для просмотра:"
    )
    
    await message.answer(favorites_text, reply_markup=favorites_keyboard)

@router.message(FavoritesStates.browsing_favorites)
async def process_favorite_selection(message: types.Message, state: FSMContext):
    """Обработка выбора сохраненного поста"""
    if message.text == "🔙 ГЛАВНОЕ МЕНЮ":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    if message.text.startswith("📌 "):
        # Получаем название поста из кнопки
        post_title = message.text[2:]  # Убираем "📌 "
        
        # Ищем пост в избранном
        favorites = await favorites_service.get_favorites(message.from_user.id)
        selected_post = None
        
        for favorite in favorites:
            title = favorite.get('title', '')
            display_title = title[:30] + "..." if len(title) > 30 else title
            if display_title == post_title:
                selected_post = favorite
                break
        
        if selected_post:
            await show_selected_favorite(message, selected_post, state)
        else:
            await message.answer("❌ Пост не найден.", reply_markup=get_back_to_favorites_keyboard())

async def show_selected_favorite(message: types.Message, post: dict, state: FSMContext):
    """Показ выбранного сохраненного поста"""
    post_type = post.get('type', 'post')
    title = post.get('title', 'Без названия')
    text = post.get('text', '')
    image_path = post.get('image_path', '')
    created_at = post.get('created_at', '')
    post_id = post.get('id')
    
    # Сохраняем ID поста для возможных действий
    await state.update_data(selected_favorite_id=post_id)
    
    # Форматируем дату
    try:
        date_obj = datetime.fromisoformat(created_at)
        formatted_date = date_obj.strftime("%d.%m.%Y %H:%M")
    except:
        formatted_date = "неизвестно"
    
    # Формируем caption в зависимости от типа контента
    if text and text != "None":
        caption = (
            f"**{title}**\n\n"
            f"{text}\n\n"
            f"💾 Сохранено: {formatted_date}"
        )
    else:
        caption = (
            f"**{title}**\n\n"
            f"💾 Сохранено: {formatted_date}"
        )
    
    # Отправляем контент
    if image_path and os.path.exists(image_path):
        # Отправляем изображение если оно существует
        try:
            photo = FSInputFile(image_path)
            await message.answer_photo(photo=photo, caption=caption)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки изображения: {e}")
            await message.answer(caption)
    else:
        # Или просто текст
        await message.answer(caption)
    
    # Предлагаем действия с постом
    await message.answer(
        "**Что хотите сделать с этим постом?**\n\n"
        "🔄 **Использовать шаблон** - создать новый пост на основе этого\n"
        "❌ **Удалить из избранного** - убрать из сохраненных\n"
        "📋 **В избранное** - вернуться к списку\n"
        "🔙 **Главное меню** - выйти в главное меню",
        reply_markup=get_favorite_actions_keyboard()
    )

@router.message(F.text == "🔄 ИСПОЛЬЗОВАТЬ ШАБЛОН")
async def use_favorite_template(message: types.Message, state: FSMContext):
    """Использование сохраненного поста как шаблона"""
    data = await state.get_data()
    post_id = data.get('selected_favorite_id')
    
    if not post_id:
        await message.answer("❌ Сначала выберите пост из избранного!", 
                           reply_markup=get_back_to_favorites_keyboard())
        return
    
    favorites = await favorites_service.get_favorites(message.from_user.id)
    selected_post = None
    
    for favorite in favorites:
        if favorite.get('id') == post_id:
            selected_post = favorite
            break
    
    if not selected_post:
        await message.answer("❌ Пост не найден!", 
                           reply_markup=get_back_to_favorites_keyboard())
        return
    
    # Используем текст поста как основу для нового
    original_text = selected_post.get('text', '')
    if original_text and original_text != "None":
        # Очищаем текст от хештегов для нового использования
        lines = original_text.split('\n')
        clean_text = '\n'.join([line for line in lines if not line.strip().startswith('#')])
        
        await state.update_data(template_text=clean_text)
        await message.answer(
            f"**🔄 Текст шаблона готов к использованию!**\n\n"
            f"Текст из сохраненного поста:\n\"{clean_text[:100]}...\"\n\n"
            f"Теперь создайте новый пост и используйте этот текст как основу!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    else:
        await message.answer(
            "❌ У этого сохраненного поста нет текста для использования как шаблона.",
            reply_markup=get_back_to_favorites_keyboard()
        )

@router.message(F.text == "📋 В ИЗБРАННОЕ")
async def back_to_favorites(message: types.Message, state: FSMContext):
    """Возврат к списку избранного"""
    await show_favorites(message, state)

# Вспомогательные функции для клавиатур
def get_back_to_main_keyboard():
    """Клавиатура для возврата в главное меню"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]],
        resize_keyboard=True
    )

def get_back_to_favorites_keyboard():
    """Клавиатура для возврата к избранному"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 В ИЗБРАННОЕ")],
            [KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_favorite_actions_keyboard():
    """Клавиатура действий с избранным постом"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ УДАЛИТЬ ИЗ ИЗБРАННОГО"), KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )