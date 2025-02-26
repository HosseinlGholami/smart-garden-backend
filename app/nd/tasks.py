# sorter/tasks.py

import time , datetime , os
from celery import shared_task
from .util import *
from .models import *
from .rabbit_client import RabbitMQClient
from .influx_client import InfluxDBHandler
from django.db import connection
from core.celery_client import *
from .trf_com import *

@shared_task
def sensor_task():
    influxdb_handler = InfluxDBHandler()
    try:
        print(f"=================sensor_task STARTED ... ======================")
        def callback(ch, method, properties, body):
            connection.ensure_connection()
            # pars device_id
            device_id = str(method.routing_key).split('.')[-1]
            # pars packet
            pck = rabbitmq_client.parse_message(body)
            print(f"==>{pck}<==")
            pckt_type=pck['type']

            if pckt_type == PacketType.UPLINK_REPORT_PACKET.value:
                sensor_place = SensorPlace.objects.filter(device_id=device_id, pin_num__param_id=pck['address']).first()
                if sensor_place:
                    section_name = sensor_place.section
                    value=pck['data']
                    embedd_time=pck['timestamp']/1000000
                    influxdb_handler.write_data(section_name,value, embedd_time)
                    print(f"embedd_time->>> {embedd_time} , device_id:{device_id} , {pck['address']} , ---value:{value}  , latancy ={embedd_time-time.time()} ")
                else:
                    print("No matching SensorPlace found.")
            else:
                print(f"type {get_name(PacketType,pck['type'])} === param_name: {get_name_param(pck['address'])} ========= value: {pck['data']}")

        print(f"plc_log_consumer task starting")
        rabbitmq_client = RabbitMQClient(host=os.environ['LOCAL_IP'])
        rabbitmq_client.connect()
        QUEUE_NAME = 'trf_queue'
        TOPIC = '.trf.server.message.*'
        rabbitmq_client.listen_for_messages(queue_name=QUEUE_NAME,routing_key=TOPIC,callback=callback)
    except Exception as err:
        print(f"=================WE DO HAVE EXPTION======================")
        connection.ensure_connection()
        project_queary = TRFProject.objects.first()
        celery_terminate_task(project_queary.project_queary.sensor_task_id)
        rabbitmq_client.close()
        connection.close()  # Ensure connection is closed
        raise_error_and_save_on_db(err)


FAIL_STATUS = ["NOTEXIST", "FAILURE", "REVOKED"]

TASK_TIME_OUT = 100*100*60*60
def handel_base_task_inside_beat():
    connection.ensure_connection()
    project_queary = TRFProject.objects.first()
    if (project_queary):  # in case of exists in db
        # if is activated
        # check if is activated if not reactivated
        # sensor_task
        sensor_task_status = request_flower_check_task(
            project_queary.sensor_task_id)
        if (sensor_task_status in FAIL_STATUS):
            task = sensor_task.s()
            project_queary.sensor_task_id = task.apply_async(
                time_limit=TASK_TIME_OUT*2,
                soft_time_limit=TASK_TIME_OUT,
            )
            project_queary.save()
    else:  # in case of does not exist in db
        # create one and start it
        base_general_project = TRFProject()
        # sensor_task
        task = sensor_task.s()
        base_general_project.sensor_task_id = task.apply_async(
            time_limit=TASK_TIME_OUT*2,
            soft_time_limit=TASK_TIME_OUT,
            # expires=datetime.datetime.now() + datetime.timedelta(hours=6)
        )
        base_general_project.save()


@shared_task
def reset_worker_task_for_problem_case():
    if (check_beat_is_activate()):
        print("--------------BEAT-------------------")
        # BASE TASK
        handel_base_task_inside_beat()


@shared_task
# # for get and set and defulat value setting inside param
# # we have 3 type of command GET(get the param from controller) , SET(set param on controller) , DEF(fetch value from db and put on sorter)
def process_user_config(hub_id,pckt_type, adress,value):
    print("============process_user_config================")
    hub = Traffic_Controller(host=os.environ['LOCAL_IP'],id=hub_id)
    if pckt_type ==  PacketType.UPLINK_HEARTBEAT_PACKET.value:
        return hub.hbt()
    elif pckt_type ==  PacketType.UPLINK_COMMAND_PACKET.value:
        return hub.send_command(adress,value)
    elif pckt_type ==  PacketType.UPLINK_GET_PARAM_PACKET.value:
        return hub.get_param(adress)
    elif pckt_type ==  PacketType.UPLINK_SET_PARAM_PACKET.value:
        return hub.set_param(adress,value)
    else:
        return "invalid command type"

    return str(result)
