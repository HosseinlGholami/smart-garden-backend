"""
Celery tasks for the smart garden backend.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from celery import shared_task
from django.db import connection
from django.conf import settings

from core.clients.rabbit_client import RabbitMQClient
from core.clients.influx_client import InfluxDBClient
from core.utils.celery import check_task_status, check_beat_is_active
from nd.models import SensorPlace, TRFProject
from nd.trf_com import Traffic_Controller, PacketType, get_name, get_name_param

import logging

logger = logging.getLogger(__name__)

TASK_TIMEOUT = 360000  # 100 hours in seconds
FAILED_STATUSES = ["NOTEXIST", "FAILURE", "REVOKED"]

@shared_task
def sensor_task():
    """
    Task to monitor sensor data from devices and store in InfluxDB.
    Listens to RabbitMQ messages and processes sensor readings.
    """
    influxdb = InfluxDBClient()
    rabbitmq = None
    
    try:
        logger.info("Starting sensor monitoring task")
        
        def handle_message(ch, method, properties, body):
            try:
                connection.ensure_connection()
                
                # Parse device ID from routing key
                device_id = str(method.routing_key).split('.')[-1]
                
                # Parse packet data
                packet = rabbitmq.parse_message(body)
                logger.debug(f"Received packet: {packet}")
                
                if packet['type'] == PacketType.UPLINK_REPORT_PACKET.value:
                    # Handle sensor reading
                    sensor = SensorPlace.objects.filter(
                        device_id=device_id,
                        pin_num__param_id=packet['address']
                    ).first()
                    
                    if sensor:
                        # Store reading in InfluxDB
                        value = packet['data']
                        embedded_time = packet['timestamp'] / 1000000
                        
                        influxdb.write_measurement(
                            measurement='sensor_reading',
                            fields={'value': value},
                            tags={
                                'section': sensor.section,
                                'device_id': device_id,
                                'pin': packet['address']
                            },
                            timestamp=datetime.fromtimestamp(embedded_time)
                        )
                        
                        latency = embedded_time - time.time()
                        logger.info(
                            f"Processed reading: device={device_id}, "
                            f"pin={packet['address']}, value={value}, "
                            f"latency={latency:.2f}s"
                        )
                    else:
                        logger.warning(f"No sensor found for device={device_id}, pin={packet['address']}")
                else:
                    # Log other packet types
                    logger.debug(
                        f"Other packet: type={get_name(PacketType, packet['type'])}, "
                        f"param={get_name_param(packet['address'])}, "
                        f"value={packet['data']}"
                    )
        
        # Set up RabbitMQ consumer
        rabbitmq = RabbitMQClient()
        rabbitmq.listen_for_messages(
            queue_name='trf_queue',
            routing_key='.trf.server.message.*',
            callback=handle_message
        )
        
    except Exception as e:
        logger.error(f"Sensor task failed: {e}")
        
        # Clean up task in database
        try:
            connection.ensure_connection()
            project = TRFProject.objects.first()
            if project and project.sensor_task_id:
                project.sensor_task_id = None
                project.save()
        except Exception as db_error:
            logger.error(f"Failed to update task status in DB: {db_error}")
        
        # Clean up connections
        if rabbitmq:
            rabbitmq.close()
        connection.close()
        raise

@shared_task
def manage_base_tasks():
    """
    Task to manage and monitor base tasks, ensuring they are running.
    Restarts failed tasks and initializes missing ones.
    """
    try:
        connection.ensure_connection()
        project = TRFProject.objects.first()
        
        if project:
            # Check and restart sensor task if needed
            sensor_status = check_task_status(project.sensor_task_id)
            if sensor_status in FAILED_STATUSES:
                task = sensor_task.apply_async(
                    time_limit=TASK_TIMEOUT * 2,
                    soft_time_limit=TASK_TIMEOUT
                )
                project.sensor_task_id = task.id
                project.save()
                logger.info(f"Restarted sensor task with ID: {task.id}")
        else:
            # Initialize project and start tasks
            project = TRFProject.objects.create()
            task = sensor_task.apply_async(
                time_limit=TASK_TIMEOUT * 2,
                soft_time_limit=TASK_TIMEOUT
            )
            project.sensor_task_id = task.id
            project.save()
            logger.info(f"Initialized project and started sensor task: {task.id}")
            
    except Exception as e:
        logger.error(f"Failed to manage base tasks: {e}")
        raise

@shared_task
def reset_worker_task():
    """
    Periodic task to check and reset worker tasks if needed.
    Ensures the task management system is running.
    """
    if check_beat_is_active():
        logger.info("Celery Beat is active, managing tasks")
        manage_base_tasks()
    else:
        logger.warning("Celery Beat is not active")

@shared_task
def process_user_config(hub_id: str, packet_type: int, address: int, value: Optional[int] = None):
    """
    Process user configuration commands for traffic controllers.
    
    Args:
        hub_id: The ID of the traffic controller hub
        packet_type: The type of packet/command to send
        address: The address to target
        value: Optional value for SET commands
    
    Returns:
        The result of the command execution
    """
    logger.info(f"Processing config: hub={hub_id}, type={packet_type}, addr={address}, value={value}")
    
    hub = Traffic_Controller(host=settings.LOCAL_IP, id=hub_id)
    
    try:
        if packet_type == PacketType.UPLINK_HEARTBEAT_PACKET.value:
            return hub.hbt()
        elif packet_type == PacketType.UPLINK_COMMAND_PACKET.value:
            return hub.send_command(address, value)
        elif packet_type == PacketType.UPLINK_GET_PARAM_PACKET.value:
            return hub.get_param(address)
        elif packet_type == PacketType.UPLINK_SET_PARAM_PACKET.value:
            return hub.set_param(address, value)
        else:
            return "Invalid command type"
    except Exception as e:
        logger.error(f"Failed to process config: {e}")
        return f"Error: {str(e)}" 