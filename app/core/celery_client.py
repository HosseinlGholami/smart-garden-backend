import os
from celery import Celery
# from celery.schedules import crontab
from celery.result import AsyncResult

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# add beat scheduler
app.conf.beat_schedule = {
    '_reset_worker_task_for_problem_case': {
        'task': 'nd.tasks.reset_worker_task_for_problem_case',
        # crontab(minute='*/1'), #https://crontab.guru/every-minute
        'schedule': 30,
        'args': [],
    },

}


def celery_terminate_task(task_id):
    print(f"task_id---------->{task_id}")
    # res = app.control.terminate(f"camera_hdlr.tasks.camera_connection[{task_id}]")
    res = app.control.terminate(task_id, terminated=True)
    print(f"result---------->{res}")
    return res


def get_task_state(task_id):
    result = AsyncResult(task_id)
    return result.state
