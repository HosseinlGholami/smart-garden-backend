from __future__ import absolute_import, unicode_literals
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery_client import app as celery_app

#TODO:
from nd.util import purge_rabbitmq_queue
import os


# purge_rabbitmq_queue(username='celery', password='celery', rabbitmq_address=os.environ['LOCAL_IP'],
#                      virtual_host='wvh', queue_name='celery')

__all__ = ('celery_app')
