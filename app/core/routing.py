from django.urls import path, include

from asyncio import sleep

from channels.generic.websocket import AsyncWebsocketConsumer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
from enum import Enum


class WebSocConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("live", self.channel_name)
        await self.accept()

    async def disconnect(self, event):
        await self.channel_layer.group_discard("live", self.channel_name)

    async def send_data(self, event):
        text_message = event.get("text", "")
        await self.send(text_data=json.dumps({"message": text_message}))


class WebSocConsumerNotif(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notif", self.channel_name)
        await self.accept()

    async def disconnect(self, event):
        await self.channel_layer.group_discard("notif", self.channel_name)

    async def send_data(self, event):
        text_message = event.get("text", "")
        await self.send(text_data=json.dumps({"message": text_message}))


ws_urlpatterns = [
    path('ws/live', WebSocConsumer.as_asgi()),
    path('ws/notif', WebSocConsumerNotif.as_asgi()),

]


# websoc credentials
# to send data on /ws/camera/
###################
channel_layer = get_channel_layer()


# user
class webSocTag(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    LIGHT = "light"
    DARK = "dark"


def send_data_on_ws_live(tag, pigeon, data):
    meta = {"tag": tag.value,"pigeon":pigeon ,"data": data}
    async_to_sync(channel_layer.group_send)(
        'live', {'type': "send_data", "text": meta})


def send_data_on_ws_notif(pigeon, data):
    meta = {"tag": pigeon, "data": data}
    async_to_sync(channel_layer.group_send)(
        'notif', {'type': "send_data", "text": meta})
