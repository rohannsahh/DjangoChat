
# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get users from URL route
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        current_user = self.scope['user'].id
        
        # Create a unique room name for the chat between these two users
        # Sort IDs to ensure same room name regardless of who connected first
        users = sorted([int(self.user_id), current_user])
        self.room_group_name = f'chat_{users[0]}_{users[1]}'
        
        print(f"Connecting to room: {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"Disconnecting from room: {self.room_group_name}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        receiver_id = data['receiver_id']
        
        print(f"Received message in room {self.room_group_name}: {message}")

        # Save message to database
        await self.save_message(
            sender=self.scope["user"],
            receiver_id=receiver_id,
            message=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope["user"].username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        
        print(f"Broadcasting in room {self.room_group_name}: {message}")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def save_message(self, sender, receiver_id, message):
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message
        )        