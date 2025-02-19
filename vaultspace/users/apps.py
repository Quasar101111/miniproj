from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # def ready(self):
    #     # Initialize model loader when app is ready
    #     from .ml_model import model_loader
    #     if model_loader.model is None:
    #         model_loader.load_model()