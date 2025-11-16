import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FavoritesService:
    """Сервис для работы с избранными постами"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.favorites_file = os.path.join(data_dir, "favorites.json")
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Создает директорию для данных если ее нет"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def save_post(self, user_id: int, post_data: Dict) -> bool:
        """Сохраняет пост в избранное"""
        try:
            logger.info(f"Сохранение поста для пользователя {user_id}: {post_data.get('title', 'Без названия')}")
            
            favorites = await self._load_favorites()
            
            if str(user_id) not in favorites:
                favorites[str(user_id)] = []
            
            # Создаем уникальный ID и добавляем timestamp
            post_data['id'] = str(uuid.uuid4())[:8]  # Короткий уникальный ID
            post_data['saved_at'] = datetime.now().isoformat()
            post_data['user_id'] = user_id
            
            # Убедимся, что все необходимые поля есть
            required_fields = ['type', 'title', 'text', 'image_path', 'created_at']
            for field in required_fields:
                if field not in post_data:
                    post_data[field] = ''
                    logger.warning(f"Отсутствует поле {field} в post_data")
            
            # Добавляем пост в избранное
            favorites[str(user_id)].append(post_data)
            
            # Сохраняем обратно
            success = await self._save_favorites(favorites)
            
            if success:
                logger.info(f"✅ Пост успешно сохранен в избранное для пользователя {user_id}")
            else:
                logger.error(f"❌ Ошибка сохранения файла избранного для пользователя {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в избранное: {e}")
            return False
    
    async def get_favorites(self, user_id: int) -> List[Dict]:
        """Получает список избранных постов пользователя"""
        try:
            favorites = await self._load_favorites()
            user_favorites = favorites.get(str(user_id), [])
            logger.info(f"Загружено {len(user_favorites)} избранных постов для пользователя {user_id}")
            return user_favorites
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки избранного: {e}")
            return []
    
    async def delete_favorite(self, user_id: int, post_id: str) -> bool:
        """Удаляет пост из избранного"""
        try:
            favorites = await self._load_favorites()
            user_key = str(user_id)
            
            if user_key not in favorites:
                logger.warning(f"Пользователь {user_id} не имеет избранных постов")
                return False
            
            user_favorites = favorites[user_key]
            initial_count = len(user_favorites)
            
            # Ищем пост по ID
            user_favorites = [post for post in user_favorites if post.get('id') != post_id]
            
            if len(user_favorites) == initial_count:
                logger.warning(f"Пост с ID {post_id} не найден у пользователя {user_id}")
                return False
            
            favorites[user_key] = user_favorites
            success = await self._save_favorites(favorites)
            
            if success:
                logger.info(f"✅ Пост {post_id} удален из избранного пользователя {user_id}")
            else:
                logger.error(f"❌ Ошибка сохранения после удаления поста {post_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из избранного: {e}")
            return False
    
    async def _load_favorites(self) -> Dict:
        """Загружает данные избранного из файла"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Файл избранного загружен, пользователей: {len(data)}")
                    return data
            logger.info("Файл избранного не существует, создаем новый")
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла избранного: {e}")
            return {}
    
    async def _save_favorites(self, favorites: Dict) -> bool:
        """Сохраняет данные избранного в файл"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            logger.info("✅ Файл избранного успешно сохранен")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения файла избранного: {e}")
            return False

# Создаем глобальный экземпляр сервиса
favorites_service = FavoritesService()