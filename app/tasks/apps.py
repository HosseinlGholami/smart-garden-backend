from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Celery Tasks'

    def ready(self):
        """Import celery tasks when Django starts."""
        import tasks.tasks  # noqa 