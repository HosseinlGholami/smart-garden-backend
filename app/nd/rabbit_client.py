import pika
import struct
from enum import Enum, auto
import time

class RabbitMQClient:
    _broker_connection = None

    def __init__(self, host, port=5672, virtual_host='wvh', credentials=None):
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.credentials = credentials or pika.PlainCredentials(
            'admin', 'dk-automation')
        self.broker_channel = None
        self.connect()

    def get_broker_connection(self):
        if not self._broker_connection:
            self._broker_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.virtual_host,
                    credentials=self.credentials
                )
            )
        return self._broker_connection

    def connect(self):
        self.broker_channel = self.get_broker_connection().channel()

    def close(self):
        if self.broker_channel and self.broker_channel.is_open:
            self.broker_channel.close()

    def send_message(self, routing_key, data_dict):
        message = self._pack_message(data_dict)
        self.broker_channel.basic_publish(
            exchange="amq.topic", routing_key=routing_key, body=message)

    def _pack_message(self, data_dict):
        message = struct.pack('<BqBBi', data_dict["version"], data_dict["timestamp"],
                     data_dict["type"],data_dict["address"] ,data_dict["data"])
        return message

    def parse_message(self, body):
        packed_struct = '<BqBBi'
        data = struct.unpack(packed_struct, body)
        return {
            "version": data[0], "timestamp": data[1], "type": data[2],
            "address": data[3], "data": data[4] 
        }

    def publish_and_listen(self, send_routing_key, listen_routing_key, data_dict,queue_name):
        # create queue and binding it
        self.broker_channel.queue_declare(queue=queue_name)
        self.broker_channel.queue_bind(
            exchange="amq.topic", queue=queue_name, routing_key=listen_routing_key)
        # send message
        self.send_message(send_routing_key, data_dict)
        # prepare for receiving command
        response_received = False
        response = ""

        def on_response(ch, method, props, body):
            nonlocal response_received
            nonlocal response
            response_received = True
            response = self.parse_message(body)

        self.broker_channel.basic_consume(
            queue=queue_name, on_message_callback=on_response, auto_ack=True)

        start_time = time.time()
        timeout = 3  # Timeout in seconds
        while not response_received:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                print(
                    f"response ---------TIMOUT----in---{timeout}-----")
                break
            try:
                self.get_broker_connection().process_data_events(
                    time_limit=0.5)
            except pika.exceptions.AMQPError:
                self.broker_channel.queue_delete(queue=queue_name)
        self.broker_channel.queue_delete(queue=queue_name)
        return response

    def listen_for_messages(self, queue_name, routing_key, callback):
        self.broker_channel.queue_declare(queue=queue_name)
        self.broker_channel.queue_bind(exchange="amq.topic",
                                       queue=queue_name, routing_key=routing_key)
        self.broker_channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.broker_channel.start_consuming()

    def destination_packer(self, dest):
        for x in self.DestinationID:
            if x.name == dest.upper():
                return x.value
        return 0

    def command_packer(self, cmd):
        for x in self.CommandType:
            if x.name == cmd.upper():
                return x.value
        return 0

    def destination_parser(self, dest):
        for x in self.DestinationID:
            if x.value == dest:
                return x.name
        return 0

    def command_parser(self, cmd):
        for x in self.CommandType:
            if x.value == cmd:
                return x.name
        return 0


# if __name__ == "__main__":
#     from server_simulator import *
#     a = RabbitMQClient("172.30.33.136")

#     def on_response(ch, method, props, body):
#         x=a.parse_message(body)
#         dt = time.localtime(x['timestamp'] / 1000000)
#         date_string = time.strftime('%Y-%m-%d %H:%M:%S', dt) + f".{x['timestamp'] % 1000000:06d}"

#         cmd=get_name(PacketType,x['type'])
#         param_name=get_name_param(x['address'])
        
#         print(f"miro-time:{date_string} ===type {cmd} === param_name: {param_name} ========= value: {x['data']}")
        

#     a.listen_for_messages(queue_name= "SAKINE", routing_key=".trf.server.message.#", callback = on_response)

