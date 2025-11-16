from aiogram.fsm.state import State, StatesGroup

class StartStates(StatesGroup):
    """Состояния стартового экрана"""
    waiting_for_start_choice = State()
    waiting_for_about_bot_choice = State()
    waiting_for_nko_choice = State()

class NKOStates(StatesGroup):
    """Состояния для сбора информации об НКО"""
    waiting_for_nko_choice = State()
    waiting_for_nko_name = State()
    waiting_for_nko_mission = State()
    waiting_for_nko_activities = State()
    waiting_for_nko_audience = State()

class PostCreationStates(StatesGroup):
    """Состояния для создания поста"""
    waiting_for_creation_method = State()
    waiting_for_idea_to_improve = State()
    waiting_for_post_action = State()  # Новое состояние для действий после создания поста
    
    # Генератор историй
    waiting_for_story_keywords = State()
    waiting_for_story_style = State()

class TextGenStates(StatesGroup):
    """Состояния для генерации текста"""
    waiting_for_text_topic = State()

class TemplateStates(StatesGroup):
    """Состояния для шаблонов постов"""
    waiting_for_template_type = State()
    
    # Анонс
    announce_event = State()
    announce_date = State()
    announce_place = State()
    announce_audience = State()
    announce_benefits = State()
    announce_registration = State()
    
    # Новости
    news_event = State()
    news_date = State()
    news_place = State()
    news_participants = State()
    news_significance = State()
    
    # История
    story_subject = State()
    story_situation = State()
    story_changes = State()
    story_ending = State()
    story_message = State()
    
    # Поиск волонтеров
    volunteers_event = State()
    volunteers_date = State()
    volunteers_place = State()
    volunteers_tasks = State()
    volunteers_requirements = State()
    volunteers_benefits = State()
    volunteers_registration = State()
    
    # Отчет
    report_period = State()
    report_results = State()
    report_finance = State()
    report_volunteers = State()
    report_events = State()
    report_plans = State()
    
    # Срочный сбор
    emergency_situation = State()
    emergency_deadline = State()
    emergency_needs = State()
    emergency_finance = State()
    emergency_contacts = State()
    emergency_help_types = State()
    emergency_phone = State()
    
    # Поздравление
    congrats_who = State()
    congrats_occasion = State()
    congrats_thanks = State()
    congrats_achievements = State()
    congrats_wishes = State()

class ImageGenStates(StatesGroup):
    """Состояния для генерации изображений"""
    waiting_for_image_method = State()
    waiting_for_image_text = State()
    waiting_for_image_file = State()
    waiting_for_image_style = State()
    waiting_for_image_action = State()  # Новое состояние для действий после генерации

class TextEditStates(StatesGroup):
    """Состояния для редактора текста"""
    waiting_for_text = State()

class ContentPlanStates(StatesGroup):
    """Состояния для контент-плана"""
    waiting_for_period = State()

class FavoritesStates(StatesGroup):
    """Состояния для избранного"""
    browsing_favorites = State()

class FeedbackStates(StatesGroup):
    """Состояния для обратной связи"""
    waiting_for_feedback = State()