# import json
# import jwt
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from orders.models import Order
# from orders.serializers import OrderSerializer
# from django.contrib.auth.models import AnonymousUser
# from django.conf import settings
# from users.models import CustomUser
# from django.utils import timezone

# class OrderConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.group_name = f'user_{self.user_id}' if self.user_id.isdigit() else 'user_admin'

#         query_string = self.scope.get('query_string', b'').decode()
#         print(f"WebSocket connect attempt: user_id={self.user_id}, query={query_string}, path={self.scope['path']}")
#         token_key = None
#         for param in query_string.split('&'):
#             if param.startswith('token='):
#                 token_key = param.split('=')[1]
#                 break

#         if not token_key:
#             print(f"WebSocket rejected: No token provided for user_id={self.user_id}")
#             await self.close(code=4001, reason="No token provided")
#             return

#         user = await self.get_user_from_jwt(token_key)
#         if not user or user.is_anonymous:
#             print(f"WebSocket rejected: Invalid token or anonymous user for user_id={self.user_id}, token={token_key[:10]}...")
#             await self.close(code=4002, reason="Invalid token")
#             return

#         self.scope['user'] = user
#         print(f"WebSocket connected: user={user.username}, user_id={user.id}, group={self.group_name}, channel={self.channel_name}")

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         await self.accept()

#     @database_sync_to_async
#     def get_user_from_jwt(self, token_key):
#         try:
#             payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
#             user_id = payload.get('user_id')
#             print(f"JWT payload: user_id={user_id}, exp={payload.get('exp')}, jti={payload.get('jti')}")
#             user = CustomUser.objects.get(id=user_id)
#             print(f"JWT token valid: user={user.username}, user_id={user_id}")
#             return user
#         except jwt.ExpiredSignatureError:
#             print(f"JWT token expired: token={token_key[:10]}...")
#             return AnonymousUser()
#         except (jwt.InvalidTokenError, CustomUser.DoesNotExist) as e:
#             print(f"JWT token invalid: error={str(e)}, token={token_key[:10]}...")
#             return AnonymousUser()

#     async def disconnect(self, close_code):
#         print(f"WebSocket disconnected: user_id={self.user_id}, group={self.group_name}, code={close_code}, reason={self.scope.get('close_reason', 'unknown')}")
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         print(f"WebSocket received data: user_id={self.user_id}, data={text_data}")
#         pass

#     async def order_notification(self, event):
#         print(f"Sending notification to {self.group_name}: order_id={event['order']['id']}, status={event['order']['status']}, message={event.get('message')}")
#         await self.send(text_data=json.dumps({
#             'type': event['type'],
#             'order_id': event['order']['id'],
#             'message': event.get('message'),
#             'status': event['order']['status'],
#             'timestamp': event.get('timestamp', event['order']['updated_at']),
#             'order': event['order'],
#         }))



import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from orders.models import Order
from orders.serializers import OrderSerializer
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from users.models import CustomUser
from django.utils import timezone
from decimal import Decimal

# Decimal ko float me convert karne ke liye helper function
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope['url_route']['kwargs'].get('user_id', 'admin')
        self.group_name = 'user_admin' if user_id == 'admin' else f'user_{user_id}'
        query_string = self.scope.get('query_string', b'').decode()
        print(f"WebSocket connect attempt: user_id={user_id}, query={query_string}, path={self.scope['path']}")

        token_key = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token_key = param.split('=')[1]
                break

        if not token_key:
            print(f"WebSocket rejected: No token provided for user_id={user_id}")
            await self.close(code=4001, reason="No token provided")
            return

        user = await self.get_user_from_jwt(token_key)
        if not user or user.is_anonymous:
            print(f"WebSocket rejected: Invalid or expired token for user_id={user_id}, token={token_key[:10]}...")
            await self.close(code=4002, reason="Invalid or expired token")
            return

        self.scope['user'] = user
        print(f"WebSocket connected: user={user.username}, user_id={user.id}, group={self.group_name}, channel={self.channel_name}")

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def get_user_from_jwt(self, token_key):
        try:
            payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            print(f"JWT payload: user_id={user_id}, exp={payload.get('exp')}, jti={payload.get('jti')}")
            user = CustomUser.objects.get(id=user_id)
            print(f"JWT token valid: user={user.username}, user_id={user_id}")
            return user
        except jwt.ExpiredSignatureError:
            print(f"JWT token expired: token={token_key[:10]}...")
            return AnonymousUser()
        except (jwt.InvalidTokenError, CustomUser.DoesNotExist) as e:
            print(f"JWT token invalid: error={str(e)}, token={token_key[:10]}...")
            return AnonymousUser()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected: group={self.group_name}, code={close_code}, reason={self.scope.get('close_reason', 'unknown')}")
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"WebSocket received data: group={self.group_name}, data={text_data}")
        pass

    async def order_notification(self, event):
        """Handle order notification and send item names and prices to client."""
        print(f"Order notification received: group={self.group_name}, event={event}")
        await self.send(text_data=json.dumps({
            'type': 'order_notification',
            'order_id': event['order_id'],
            'message': event['message'],
            'items': [
                {
                    'menu_item_name': item['menu_item_name'],
                    'price': float(item['price']),
                    'quantity': item['quantity']
                } for item in event['items']
            ]
        }))