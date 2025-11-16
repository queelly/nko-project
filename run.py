#!/usr/bin/env python3
"""
Точка входа для запуска бота Добробот
"""

import asyncio
import os
import sys

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    print("🚀 Запускаем Добробота...")
    print("🐱 Кот-помощник для НКО готов к работе!")
    asyncio.run(main())