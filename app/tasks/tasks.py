"""
Celery tasks for the smart garden backend.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from celery import shared_task
from django.db import connection
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

@shared_task
def example_task():
    """
    Example task that logs a message.
    """
    logger.info("Example task executed successfully")
    return "Task completed"

@shared_task
def periodic_task():
    """
    Periodic task example.
    """
    logger.info(f"Periodic task executed at {datetime.now()}")
    return f"Periodic task completed at {datetime.now()}" 