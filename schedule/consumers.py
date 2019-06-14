from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import comment,User,meeting,participant
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user1=self.scope["user"]
        meet = meeting.objects.get(id=self.room_name)
        comment1=comment(user=user1, meeting=meet, Comment=message)
        comment1.save()
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user1=self.scope["user"]
        message=user1.username +" - "+message
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))