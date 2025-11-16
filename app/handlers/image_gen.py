from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from app.utils.states import ImageGenStates
from app.utils.keyboards import (
    get_main_menu_keyboard,
    get_image_creation_keyboard,
    get_image_styles_keyboard,
    get_back_keyboard,
    get_after_image_keyboard
)
from app.services.async_ai_image import generate_image_async
from app.services.favorites import favorites_service
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = Router()

# Глобальный словарь для хранения последних изображений пользователей
user_last_images = {}

@router.message(F.text == "🎨 СОЗДАТЬ КАРТИНКУ")
async def start_image_creation(message: types.Message, state: FSMContext):
    """Начало создания картинки"""
    # Очищаем состояние при входе в функцию
    await state.clear()
    
    start_text = (
        "**🎨 МАСТЕРСКАЯ КОТО-ХУДОЖНИКА!**\n\n"
        "Создам уникальную картину по вашему тексту! Она:\n"
        "📖 Передаст суть и эмоции\n"
        "🐱 Будет в фирменном кото-стиле\n"  
        "📱 Подойдет для соцсетей\n"
        "❤️ Вызовет отклик у аудитории"
    )
    
    await message.answer(start_text, reply_markup=get_image_creation_keyboard())
    await state.set_state(ImageGenStates.waiting_for_image_method)

@router.message(ImageGenStates.waiting_for_image_method)
async def process_image_method(message: types.Message, state: FSMContext):
    """Обработка выбора метода создания картинки"""
    if message.text == "📖 ВСТАВИТЬ ТЕКСТ":
        await start_text_input(message, state)
    elif message.text == "📄 ЗАГРУЗИТЬ ФАЙЛ":
        await start_file_upload(message, state)
    elif message.text == "⭐ ВЫБРАТЬ ИЗ ИЗБРАННОГО":
        await choose_from_favorites(message, state)
    elif message.text == "🔙 ГЛАВНОЕ МЕНЮ":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer("Пожалуйста, выберите вариант из меню:")

async def start_text_input(message: types.Message, state: FSMContext):
    """Начало ввода текста для картинки"""
    text_input_prompt = (
        "**📝 Введите текст для картинки:**\n\n"
        "Опишите что хотите увидеть на изображении. "
        "Будьте максимально конкретны!\n\n"
        "_Пример: \"Дети играют в парке, солнечный день, мультяшный стиль\"_"
    )
    
    await message.answer(text_input_prompt, reply_markup=get_back_keyboard())
    await state.set_state(ImageGenStates.waiting_for_image_text)

@router.message(ImageGenStates.waiting_for_image_text)
async def process_image_text(message: types.Message, state: FSMContext):
    """Обработка текста для картинки"""
    if message.text == "🔙 НАЗАД":
        await start_image_creation(message, state)
        return
    
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text == "🔙 ГЛАВНОЕ МЕНЮ":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    await state.update_data(image_text=message.text)
    await state.set_state(ImageGenStates.waiting_for_image_style)
    
    analysis_text = (
        "**Проанализировал ваш текст!** А теперь выберите стиль картинки:"
    )
    
    await message.answer(analysis_text, reply_markup=get_image_styles_keyboard())

@router.message(ImageGenStates.waiting_for_image_style)
async def process_image_style(message: types.Message, state: FSMContext):
    """Обработка выбора стиля картинки"""
    # Проверяем, не пытается ли пользователь выйти в главное меню
    if message.text == "🔙 ГЛАВНОЕ МЕНЮ":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
        return
    
    style_map = {
        "🐱 МИЛЫЙ КОТО-СТИЛЬ": "милый кото-стиль, аниме, каваий, милые животные",
        "🎨 ХУДОЖЕСТВЕННЫЙ": "художественный стиль, картина, живопись, арт",
        "📊 ИНФОГРАФИКА": "инфографика, схема, диаграмма, информационный стиль",
        "❤️ ЭМОЦИОНАЛЬНЫЙ": "эмоциональный, глубокая атмосфера, чувства, настроение", 
        "🌿 РЕАЛИСТИЧНЫЙ": "реалистичный, фотореализм, высокое качество, детализация"
    }
    
    if message.text == "🔙 ИЗМЕНИТЬ ТЕКСТ":
        await state.set_state(ImageGenStates.waiting_for_image_text)
        await message.answer("Введите новый текст для картинки:", reply_markup=get_back_keyboard())
        return
    
    if message.text not in style_map:
        await message.answer("Пожалуйста, выберите стиль из предложенных вариантов:")
        return
    
    data = await state.get_data()
    base_prompt = data.get('image_text', '')
    style_prompt = style_map[message.text]
    
    # Объединяем основной промпт со стилем
    full_prompt = f"{base_prompt}, {style_prompt}"
    
    await message.answer("**Мур! Рисую вашу картинку...**")
    
    try:
        # Отправляем сообщение о начале генерации
        status_message = await message.answer(
            "🔄 Генерирую изображение... Это может занять 1-2 минуты.\n"
            "⏳ Вы можете продолжать пользоваться другими функциями бота!"
        )
        
        # Запускаем асинхронную генерацию
        image_path = await generate_image_async(full_prompt)
        
        # Редактируем статус сообщения
        await status_message.edit_text("✅ Изображение готово! Отправляю...")
        
        # Создаем FSInputFile для отправки
        photo = FSInputFile(image_path)
        
        # Отправляем изображение
        await message.answer_photo(
            photo=photo,
            caption="🎨 **Ваша сгенерированная картинка!**",
            reply_markup=get_after_image_keyboard()
        )
        
        # Сохраняем данные для возможного сохранения в избранное
        post_data = {
            'type': 'image',
            'title': f"Картинка: {base_prompt[:30]}..." if base_prompt else "Сгенерированная картинка",
            'text': None,
            'image_path': image_path,
            'created_at': datetime.now().isoformat(),
            'prompt': full_prompt,
            'style': message.text
        }
        
        # Сохраняем изображение в глобальном хранилище
        user_last_images[message.from_user.id] = post_data
        logger.info(f"✅ Изображение сгенерировано и сохранено для пользователя {message.from_user.id}")
        
        # Удаляем статус сообщение
        await status_message.delete()
            
    except Exception as e:
        logger.error(f"❌ Ошибка генерации изображения: {e}")
        await message.answer(
            f"❌ Произошла ошибка при генерации изображения: {str(e)}\n"
            f"Попробуйте изменить описание или стиль.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        return
    
    # Переходим в состояние ожидания действий с изображением
    await state.set_state(ImageGenStates.waiting_for_image_action)

async def start_file_upload(message: types.Message, state: FSMContext):
    """Начало загрузки файла"""
    upload_text = (
        "**📄 Загрузка файлов**\n\n"
        "В будущей версии здесь можно будет загружать файлы для анализа "
        "и создания картинок на их основе.\n\n"
        "А пока используйте текстовый ввод! 📝"
    )
    
    await message.answer(upload_text, reply_markup=get_back_to_main_keyboard())

async def choose_from_favorites(message: types.Message, state: FSMContext):
    """Выбор из избранного"""
    favorites_text = (
        "**⭐ Выбор из избранного**\n\n"
        "В будущей версии здесь можно будет выбирать из сохраненных работ "
        "для создания новых картинок на их основе.\n\n"
        "А пока создайте новую картинку! 🎨"
    )
    
    await message.answer(favorites_text, reply_markup=get_back_to_main_keyboard())

# Обработчики действий после генерации картинки
@router.message(ImageGenStates.waiting_for_image_action)
async def handle_image_actions(message: types.Message, state: FSMContext):
    """Обработка действий после генерации картинки"""
    if message.text == "🎨 СОЗДАТЬ ДРУГУЮ КАРТИНКУ":
        await create_another_image(message, state)
    elif message.text == "🖌️ ИЗМЕНИТЬ СТИЛЬ":
        await change_image_style(message, state)
    elif message.text == "📝 СОЗДАТЬ ПОСТ С ЭТОЙ КАРТИНКОЙ":
        await create_post_with_image(message, state)
    elif message.text == "⭐ СОХРАНИТЬ В ИЗБРАННОЕ":
        await save_image_to_favorites(message, state)
    elif message.text == "🔙 ГЛАВНОЕ МЕНЮ":
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())
    else:
        await message.answer("Пожалуйста, выберите действие из меню:")

async def create_another_image(message: types.Message, state: FSMContext):
    """Создание другой картинки"""
    await state.clear()
    await start_image_creation(message, state)

async def change_image_style(message: types.Message, state: FSMContext):
    """Изменение стиля текущей картинки"""
    data = await state.get_data()
    if not data.get('image_text'):
        await message.answer("Сначала создайте картинку!", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return
    
    await state.set_state(ImageGenStates.waiting_for_image_style)
    await message.answer(
        "Выберите новый стиль для картинки:",
        reply_markup=get_image_styles_keyboard()
    )

async def create_post_with_image(message: types.Message, state: FSMContext):
    """Создание поста с текущей картинкой"""
    user_id = message.from_user.id
    image_data = user_last_images.get(user_id)
    
    if not image_data or not image_data.get('image_path'):
        await message.answer("Сначала создайте картинку!", reply_markup=get_main_menu_keyboard())
        await state.clear()
        return
    
    # Сохраняем путь к изображению для использования в создании поста
    await state.update_data(post_image_path=image_data['image_path'])
    
    from app.handlers.post_creation import start_post_creation
    await start_post_creation(message, state)

async def save_image_to_favorites(message: types.Message, state: FSMContext):
    """Сохранение картинки в избранное"""
    try:
        user_id = message.from_user.id
        
        # Получаем изображение из глобального хранилища
        image_data = user_last_images.get(user_id)
        
        if not image_data:
            await message.answer("❌ Сначала создайте картинку!", reply_markup=get_main_menu_keyboard())
            await state.clear()
            return
        
        logger.info(f"Попытка сохранения картинки в избранное для пользователя {user_id}")
        logger.info(f"Данные изображения: {image_data}")
        
        # Сохраняем картинку в избранное
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
                reply_markup=get_after_image_keyboard()
            )
            logger.error(f"❌ Ошибка сохранения картинки в избранное для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при сохранении картинки: {e}")
        await message.answer(
            "❌ Произошла ошибка при сохранении. Попробуйте еще раз.",
            reply_markup=get_after_image_keyboard()
        )

# Обработчик для кнопки "Назад" в любом состоянии
@router.message(F.text == "🔙 НАЗАД")
async def handle_back_button(message: types.Message, state: FSMContext):
    """Обработка кнопки Назад"""
    current_state = await state.get_state()
    
    if current_state == ImageGenStates.waiting_for_image_text:
        await start_image_creation(message, state)
    elif current_state == ImageGenStates.waiting_for_image_style:
        await state.set_state(ImageGenStates.waiting_for_image_text)
        await message.answer("Введите текст для картинки:", reply_markup=get_back_keyboard())
    else:
        # Если непонятно откуда "Назад", идем в главное меню
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())

# Обработчик для кнопки "Главное меню" в любом состоянии
@router.message(F.text == "🔙 ГЛАВНОЕ МЕНЮ")
async def handle_main_menu_button(message: types.Message, state: FSMContext):
    """Обработка кнопки Главное меню из любого состояния"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=get_main_menu_keyboard())

# Вспомогательные функции для клавиатур
def get_back_to_main_keyboard():
    """Клавиатура для возврата в главное меню"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]],
        resize_keyboard=True
    )

@router.message(F.text == "📏 УВЕЛИЧИТЬ/УМЕНЬШИТЬ ТЕКСТ")
async def resize_text(message: types.Message, state: FSMContext):
    """Изменение размера текста - заглушка"""
    await message.answer(
        "В будущей версии здесь можно будет изменять размер текста в посте. "
        "А пока используйте текущую версию!",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()