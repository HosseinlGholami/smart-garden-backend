from .rabbit_client import *
import time
from enum import Enum
import struct


from enum import Enum

class TRFParameterId(Enum):
    PARAMS_TRF_ONLINE_STATE = {
        "param_id": 0,
        "param_name": "PARAMS_TRF_ONLINE_STATE",
        "default_value": 1,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_TRF_UUID = {
        "param_id": 1,
        "param_name": "PARAMS_TRF_UUID",
        "default_value": 200,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_RELAY_1_OUTPUT = {
        "param_id": 2,
        "param_name": "PARAMS_RELAY_1_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_RELAY_2_OUTPUT = {
        "param_id": 3,
        "param_name": "PARAMS_RELAY_2_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_RELAY_3_OUTPUT = {
        "param_id": 4,
        "param_name": "PARAMS_RELAY_3_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_MOSFET_1_OUTPUT = {
        "param_id": 5,
        "param_name": "PARAMS_MOSFET_1_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_MOSFET_2_OUTPUT = {
        "param_id": 6,
        "param_name": "PARAMS_MOSFET_2_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_BLINK_OUTPUT = {
        "param_id": 7,
        "param_name": "PARAMS_BLINK_OUTPUT",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_INPUT_NUM_1 = {
        "param_id": 8,
        "param_name": "PARAMS_INPUT_NUM_1",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_INPUT_NUM_2 = {
        "param_id": 9,
        "param_name": "PARAMS_INPUT_NUM_2",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_INPUT_NUM_3 = {
        "param_id": 10,
        "param_name": "PARAMS_INPUT_NUM_3",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_INPUT_NUM_4 = {
        "param_id": 11,
        "param_name": "PARAMS_INPUT_NUM_4",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_INPUT_NUM_1_HIGH_FILTER_LEN = {
        "param_id": 12,
        "param_name": "PARAMS_INPUT_NUM_1_HIGH_FILTER_LEN",
        "default_value": 5,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET HIGH"
    }
    PARAMS_INPUT_NUM_2_HIGH_FILTER_LEN = {
        "param_id": 13,
        "param_name": "PARAMS_INPUT_NUM_2_HIGH_FILTER_LEN",
        "default_value": 5,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET HIGH"
    }
    PARAMS_INPUT_NUM_3_HIGH_FILTER_LEN = {
        "param_id": 14,
        "param_name": "PARAMS_INPUT_NUM_3_HIGH_FILTER_LEN",
        "default_value": 5,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET HIGH"
    }
    PARAMS_INPUT_NUM_4_HIGH_FILTER_LEN = {
        "param_id": 15,
        "param_name": "PARAMS_INPUT_NUM_4_HIGH_FILTER_LEN",
        "default_value": 5,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET HIGH"
    }
    PARAMS_INPUT_NUM_1_LOW_FILTER_LEN = {
        "param_id": 16,
        "param_name": "PARAMS_INPUT_NUM_1_LOW_FILTER_LEN",
        "default_value": 1,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET LOW"
    }
    PARAMS_INPUT_NUM_2_LOW_FILTER_LEN = {
        "param_id": 17,
        "param_name": "PARAMS_INPUT_NUM_2_LOW_FILTER_LEN",
        "default_value": 1,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET LOW"
    }
    PARAMS_INPUT_NUM_3_LOW_FILTER_LEN = {
        "param_id": 18,
        "param_name": "PARAMS_INPUT_NUM_3_LOW_FILTER_LEN",
        "default_value": 1,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET LOW"
    }
    PARAMS_INPUT_NUM_4_LOW_FILTER_LEN = {
        "param_id": 19,
        "param_name": "PARAMS_INPUT_NUM_4_LOW_FILTER_LEN",
        "default_value": 1,
        "is_advance": True,
        "is_settable": True,
        "detail": "NUMBER OF THE SAMPLE WHICH HAVE TO BE TRIGGERED TO SET LOW"
    }
    PARAMS_DUMMY_PARAM_1 = {
        "param_id": 20,
        "param_name": "PARAMS_DUMMY_PARAM_1",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_DUMMY_PARAM_2 = {
        "param_id": 21,
        "param_name": "PARAMS_DUMMY_PARAM_2",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_DUMMY_PARAM_3 = {
        "param_id": 22,
        "param_name": "PARAMS_DUMMY_PARAM_3",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_DUMMY_PARAM_4 = {
        "param_id": 23,
        "param_name": "PARAMS_DUMMY_PARAM_4",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }
    PARAMS_DUMMY_PARAM_5 = {
        "param_id": 24,
        "param_name": "PARAMS_DUMMY_PARAM_5",
        "default_value": 0,
        "is_advance": False,
        "is_settable": False,
        "detail": ""
    }

class PacketType(Enum):
    UPLINK_HEARTBEAT_PACKET=0
    UPLINK_PING_PONG_PACKET=1
    UPLINK_REPORT_PACKET=2
    UPLINK_COMMAND_PACKET=3    
    UPLINK_GET_PARAM_PACKET=4
    UPLINK_SET_PARAM_PACKET=5

class CommandType(Enum):
    UPLINK_COMMAND_RESET_PARAM = 0
    UPLINK_COMMAND_OTA = 1


def get_name(enum_class, value):
    for member in enum_class:
        if member.value == value:
            return member.name
    return None


def get_name_param( value):
    for member in TRFParameterId:
        if member.value["param_id"] == value:
            return member.name
    return None


class Traffic_Controller:
    def __init__(self,host ,id):
        self.rabbit_client = RabbitMQClient(host=host, port=5672, virtual_host='wvh')
        self.send_routing_key = f".trf.hub.{id}"
        self.rply_routing_key = f".trf.server.*"
        self.queue_name=f"rpl-queue_{id}"

    def send_packet(self, type, address, data ):
        data_dict = {
            "version": 1,
            "timestamp": int(time.time()),
            "type": type,
            "address": address,  
            "data": data,
        }
        response = self.rabbit_client.publish_and_listen(self.send_routing_key, self.rply_routing_key, data_dict,self.queue_name)
        return response

    def hbt(self):
        res=  self.send_packet(type=PacketType.UPLINK_HEARTBEAT_PACKET.value,address=1,data=-1)
        try:
            res["version"]
            return 1
        except:
            return 0
        

    def get_param(self, address):
        response = self.send_packet(type=PacketType.UPLINK_GET_PARAM_PACKET.value, address=address,data=-1)
        try:
            result = (response["address"], response["data"])
        except:
            result = (-1, -1)
        return result
    
    def set_param(self, address,value):
        response = self.send_packet(type=PacketType.UPLINK_SET_PARAM_PACKET.value, address=address,data=value)
        try:
            result = (response["address"], response["data"])
        except:
            result = (-1, -1)
        return result

    def send_command(self, command_type,data):
        response = self.send_packet(type=PacketType.UPLINK_COMMAND_PACKET.value, address=command_type,data=data)
        try:
            result = (response["address"], response["data"])
        except:
            result = (-1, -1)
        return result
            
    def close(self):
        self.rabbit_client.close()


# if __name__ == "__main__":
#     a = Traffic_Controller("172.30.33.136",0)
#     # print(f"HBT RESULT:  {a.hbt()}")
#     # print(f"GET RESULT:  {a.get_param(12)}")
#     # print(f"SET RESULT:  {a.set_param(12,6)}")
#     # print(f"CMD RESULT:  {a.send_command(CommandType.UPLINK_COMMAND_RESET_PARAM.value)}")
#     a.close()


