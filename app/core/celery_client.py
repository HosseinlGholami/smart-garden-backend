import os
from celery import Celery
from celery.signals import task_failure, worker_ready
from celery.result import AsyncResult
from kombu import Exchange, Queue
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery app
app = Celery('core')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Set up task queues
task_queues = [
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('high_priority', Exchange('high_priority'), routing_key='high_priority'),
    Queue('low_priority', Exchange('low_priority'), routing_key='low_priority'),
]

app.conf.task_queues = task_queues

# Task routing
app.conf.task_routes = {
    'tasks.*': {'queue': 'default'},
}

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Configure the Celery beat schedule (empty)
app.conf.beat_schedule = {}

@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """Handle task failures by logging them."""
    import logging
    logger = logging.getLogger(__name__)
    error_msg = f"Task {task_id} failed: {str(exception)}"
    logger.error(error_msg)

@worker_ready.connect
def worker_ready_handler(**kwargs):
    """Log when a worker is ready."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Celery worker is ready and connected to RabbitMQ")

def get_task_state(task_id):
    """Get the current state of a task."""
    try:
        result = AsyncResult(task_id)
        return {
            'state': result.state,
            'info': result.info,
            'task_id': task_id,
            'result': result.result if result.ready() else None,
        }
    except Exception as e:
        return {
            'state': 'ERROR',
            'info': str(e),
            'task_id': task_id,
            'result': None
        }

def celery_terminate_task(task_id):
    """Terminate a running Celery task."""
    try:
        app.control.revoke(task_id, terminate=True, signal='SIGTERM')
        return {'status': 'success', 'message': f'Task {task_id} terminated'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def purge_queue(queue_name):
    """Purge all messages from a specific queue."""
    try:
        with app.connection_for_write() as conn:
            queue = Queue(queue_name, Exchange(queue_name), queue_name)
            queue(conn).purge()
        return {'status': 'success', 'message': f'Queue {queue_name} purged'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
