# collaboration/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/collaborate/<int:doc_id>/', consumers.DocumentConsumer.as_asgi()),
]
