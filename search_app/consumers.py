# search_app/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Product

class SearchConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive_json(self, content):
        query = content.get('query', '')
        products = Product.objects.filter(name__icontains=query)  # 部分一致検索
        await self.send_json({
            'results': [{'name': product.name, 'price': product.price} for product in products]
        })
