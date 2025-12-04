from django.apps import AppConfig


class RecommenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommender'

    def ready(self):
        # Initialize the recommendation engine on startup
        from .engine import get_engine
        get_engine()
