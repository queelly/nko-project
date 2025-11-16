from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    """Стартовый экран"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 НАЧНЁМ!"), KeyboardButton(text="ℹ️ О БОТЕ")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_nko_intro_keyboard():
    """После нажатия НАЧНЁМ!"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✍️ РАССКАЗАТЬ О НКО"), KeyboardButton(text="🚀 ПРОПУСТИТЬ")]
        ],
        resize_keyboard=True
    )

def get_main_menu_keyboard():
    """Главное меню Добробота"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 СОЗДАТЬ ПОСТ С КАРТИНКОЙ"), KeyboardButton(text="🎨 СОЗДАТЬ КАРТИНКУ")],
            [KeyboardButton(text="✍️ СОЗДАТЬ ТЕКСТ ДЛЯ ПОСТА"), KeyboardButton(text="✏️ ПРОВЕРИТЬ ТЕКСТ")],
            [KeyboardButton(text="📅 КОНТЕНТ-ПЛАН"), KeyboardButton(text="⭐ ИЗБРАННОЕ")],
            [KeyboardButton(text="🏢 Информация об НКО"), KeyboardButton(text="💬 ПОДДЕРЖКА")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

# ... остальные функции клавиатур остаются без изменений ...

def get_post_creation_keyboard():
    """Создание поста с картинкой"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 БЫСТРЫЙ ШАБЛОН"), KeyboardButton(text="💫 УЛУЧШИТЬ ИДЕЮ")],
            [KeyboardButton(text="🎭 ГЕНЕРАТОР ИСТОРИЙ"), KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_template_types_keyboard():
    """Типы шаблонов постов"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 АНОНС"), KeyboardButton(text="📰 НОВОСТИ"), KeyboardButton(text="❤️ ИСТОРИЯ")],
            [KeyboardButton(text="👥 ПОИСК ВОЛОНТЕРОВ"), KeyboardButton(text="📊 ОТЧЁТ"), KeyboardButton(text="🚨 СРОЧНЫЙ СБОР")],
            [KeyboardButton(text="🎊 ПОЗДРАВЛЕНИЕ"), KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_back_keyboard():
    """Простая кнопка Назад"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 НАЗАД")]],
        resize_keyboard=True
    )

def get_skip_keyboard():
    """Кнопки Пропустить и Назад"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 НАЗАД"), KeyboardButton(text="⏩ ПРОПУСТИТЬ")]
        ],
        resize_keyboard=True
    )

def get_story_styles_keyboard():
    """Стили для генератора историй"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 РЕАЛИСТИЧНЫЙ"), KeyboardButton(text="✨ ВДОХНОВЛЯЮЩИЙ")],
            [KeyboardButton(text="😢 ЭМОЦИОНАЛЬНЫЙ"), KeyboardButton(text="🎪 ДРАМАТИЧНЫЙ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_image_creation_keyboard():
    """Создание картинки"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 ВСТАВИТЬ ТЕКСТ"), KeyboardButton(text="📄 ЗАГРУЗИТЬ ФАЙЛ")],
            [KeyboardButton(text="⭐ ВЫБРАТЬ ИЗ ИЗБРАННОГО"), KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_image_styles_keyboard():
    """Стили для картинок"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🐱 МИЛЫЙ КОТО-СТИЛЬ"), KeyboardButton(text="🎨 ХУДОЖЕСТВЕННЫЙ")],
            [KeyboardButton(text="📊 ИНФОГРАФИКА"), KeyboardButton(text="❤️ ЭМОЦИОНАЛЬНЫЙ")],
            [KeyboardButton(text="🌿 РЕАЛИСТИЧНЫЙ"), KeyboardButton(text="🔙 ИЗМЕНИТЬ ТЕКСТ")]
        ],
        resize_keyboard=True
    )

def get_content_plan_period_keyboard():
    """Периоды для контент-плана"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 НА ДЕНЬ"), KeyboardButton(text="🗓️ НА НЕДЕЛЮ")],
            [KeyboardButton(text="📆 НА МЕСЯЦ"), KeyboardButton(text="🔔 НАСТРОИТЬ НАПОМИНАНИЯ")],
            [KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_about_bot_keyboard():
    """О боте"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 ПОПРОБОВАТЬ"), KeyboardButton(text="📚 ПРИМЕРЫ РАБОТ")],
            [KeyboardButton(text="🐱 МОИ КОТО-ФИШКИ"), KeyboardButton(text="🔙 НАЗАД")]
        ],
        resize_keyboard=True
    )

def get_after_post_keyboard():
    """После создания поста - РЕАЛЬНЫЕ РАБОЧИЕ КНОПКИ"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⭐ СОХРАНИТЬ В ИЗБРАННОЕ"), KeyboardButton(text="🔄 СОЗДАТЬ ЕЩЕ ПОСТ")],
            [KeyboardButton(text="🎨 СОЗДАТЬ КАРТИНКУ"), KeyboardButton(text="📋 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_after_image_keyboard():
    """После создания картинки"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 СОЗДАТЬ ДРУГУЮ КАРТИНКУ"), KeyboardButton(text="🖌️ ИЗМЕНИТЬ СТИЛЬ")],
            [KeyboardButton(text="📝 СОЗДАТЬ ПОСТ С ЭТОЙ КАРТИНКОЙ"), KeyboardButton(text="⭐ СОХРАНИТЬ В ИЗБРАННОЕ")],
            [KeyboardButton(text="📋 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_text_edit_keyboard():
    """После проверки текста - РЕАЛЬНЫЕ РАБОЧИЕ КНОПКИ"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 СОЗДАТЬ ТЕКСТ ДЛЯ ПОСТА"), KeyboardButton(text="✏️ ПРОВЕРИТЬ ЕЩЕ ТЕКСТ")],
            [KeyboardButton(text="📋 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_settings_keyboard():
    """Клавиатура настроек"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏢 ИНФОРМАЦИЯ ОБ НКО"), KeyboardButton(text="🎨 НАСТРОЙКИ СТИЛЯ")],
            [KeyboardButton(text="🔔 УВЕДОМЛЕНИЯ"), KeyboardButton(text="📊 СТАТИСТИКА")],
            [KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_support_keyboard():
    """Клавиатура поддержки"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 СВЯЗАТЬСЯ С ПОДДЕРЖКОЙ"), KeyboardButton(text="📝 ОСТАВИТЬ ОТЗЫВ")],
            [KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]
        ],
        resize_keyboard=True
    )

def get_back_to_main_keyboard():
    """Клавиатура для возврата в главное меню"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 ГЛАВНОЕ МЕНЮ")]],
        resize_keyboard=True
    )

def get_simple_back_keyboard():
    """Простая кнопка Назад без других опций"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 НАЗАД")]],
        resize_keyboard=True
    )