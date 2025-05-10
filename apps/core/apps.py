from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready
        """
        # Import signals to register them
        try:
            import apps.core.signals
        except ImportError:
            pass
