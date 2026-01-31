import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ChatRoom
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'join_room':
            self.room_id = data['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        elif msg_type == 'chat_message':
            message = data['message']
            room_id = data['room_id']
            await self.save_message(room_id, message)

            await self.channel_layer.group_send(
                f'chat_{room_id}',
                {
                    'type': 'chat_payload_handler',
                    'message': message,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                }
            )

    async def chat_payload_handler(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_payload',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
        }))

    @database_sync_to_async
    def save_message(self, room_id, content):
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=self.user, content=content)