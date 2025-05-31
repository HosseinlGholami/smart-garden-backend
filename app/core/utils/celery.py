"""
Utility functions for Celery task management and monitoring.
"""

import requests
import logging
from typing import Optional, Literal
from django.conf import settings

logger = logging.getLogger(__name__)

TaskStatus = Literal['SUCCESS', 'FAILURE', 'PENDING', 'STARTED', 'RETRY', 'REVOKED', 'NOTEXIST']

def get_flower_task_url(task_id: str) -> str:
    """Get the Flower API URL for a specific task."""
    return f"{settings.FLOWER_BASE_URL}/task/{task_id}"

def get_flower_tasks_url() -> str:
    """Get the Flower API URL for all tasks."""
    return f"{settings.FLOWER_BASE_URL}/api/tasks"

def check_task_status(task_id: str) -> TaskStatus:
    """
    Check the status of a Celery task using Flower's API.
    
    Args:
        task_id: The ID of the task to check
        
    Returns:
        The status of the task as a string
    """
    try:
        response = requests.get(get_flower_task_url(task_id))
        response_text = str(response.content)
        
        # Extract status from HTML response
        start_pattern = "<td>State</td>"
        start_index = response_text.find(start_pattern) + len(start_pattern)
        
        end_pattern = "</span>"
        end_index = response_text.find(end_pattern, start_index)
        
        status_pattern = "\">"
        status_start = response_text.find(status_pattern, start_index, end_index) + len(status_pattern)
        status = response_text[status_start:end_index]
        
        return 'NOTEXIST' if len(status) > 10 else status
    except Exception as e:
        logger.error(f"Error checking task status: {e}")
        return 'NOTEXIST'

def check_beat_is_active() -> bool:
    """
    Check if Celery Beat is active by looking for scheduled tasks.
    
    Returns:
        True if Beat is active, False otherwise
    """
    try:
        response = requests.get(get_flower_tasks_url())
        return 'reset_worker_task_for_problem_case' in str(response.content)
    except Exception as e:
        logger.error(f"Error checking Beat status: {e}")
        return False

def purge_rabbitmq_queue(
    queue_name: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: int = 15672,
    vhost: str = '/'
) -> bool:
    """
    Purge a RabbitMQ queue using the management API.
    
    Args:
        queue_name: Name of the queue to purge
        username: RabbitMQ management username (defaults to settings)
        password: RabbitMQ management password (defaults to settings)
        host: RabbitMQ host (defaults to settings)
        port: RabbitMQ management port
        vhost: RabbitMQ virtual host
        
    Returns:
        True if purge was successful, False otherwise
    """
    try:
        username = username or settings.RABBITMQ_USER
        password = password or settings.RABBITMQ_PASS
        host = host or settings.RABBITMQ_HOST
        
        url = f'http://{host}:{port}/rabbit/api/queues/{vhost}/{queue_name}/contents'
        
        response = requests.delete(url, auth=(username, password))
        
        if response.status_code == 204:
            logger.info(f"Successfully purged queue '{queue_name}' in vhost '{vhost}'")
            return True
        else:
            logger.error(f"Failed to purge queue '{queue_name}'. Status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error purging queue '{queue_name}': {e}")
        return False 