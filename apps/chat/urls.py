# apps/chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),         # Renders the chat UI
    path('send_message/', views.send_message, name='send_message'),  # Handles the API call
]