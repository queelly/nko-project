import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import Config
from app.handlers import (
    start, 
    nko_info, 
    text_gen, 
    image_gen, 
    text_edit, 
    content_plan,
    post_creation,
    post_templates,
    favorites
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

async def main():
    try:
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        # Регистрация роутеров в правильном порядке
        dp.include_router(start.router)
        dp.include_router(nko_info.router)
        dp.include_router(post_creation.router)
        dp.include_router(post_templates.router)
        dp.include_router(text_gen.router)
        dp.include_router(image_gen.router)
        dp.include_router(text_edit.router)
        dp.include_router(content_plan.router)
        dp.include_router(favorites.router)
        
        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Добробот запущен и готов к работе! Мяу! 🐱")
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())