# apps/chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.character_list, name='character_list'),
    path('profile/', views.profile, name='profile'),
    # Multi-step character creation wizard
    path('character/create/background/', views.character_create_background, name='character_create_background'),
    path('character/create/relationship/', views.character_create_relationship, name='character_create_relationship'),
    path('character/create/dynamic/', views.character_create_dynamic, name='character_create_dynamic'),
    path('character/create/species/', views.character_create_species, name='character_create_species'),
    path('character/create/confirm/', views.character_create_confirm, name='character_create_confirm'),
    path('character/<int:character_id>/', views.chat_room, name='chat_room'),
    path('send_message/', views.send_message, name='send_message'),
    path('send_response/', views.send_response, name='send_response'),
]