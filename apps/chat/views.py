import os
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # For quick testing, not recommended in production
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Character, ChatMessage, ResponseOption
from django.views.decorators.http import require_POST
from django.urls import reverse
from .services.risu_api import get_risu_response

def chat_page(request):
    """Renders the main chat UI."""
    return render(request, 'chat/chat.html')

@csrf_exempt  # For simplicity; otherwise you'll need to handle CSRF tokens in JS
def send_message(request):
    """Handles the AJAX/Fetch request to call Anthropic's API."""
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')
        reply = get_risu_response(user_message)
        return JsonResponse({"reply": reply})
    else:
        return JsonResponse({"error": "Invalid request method. POST expected."}, status=400)

@login_required
def profile(request):
    characters = Character.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {
        'characters': characters
    })

@login_required
def character_list(request):
    characters = Character.objects.filter(user=request.user)
    return render(request, 'character/list.html', {'characters': characters})

@login_required
def character_create_background(request):
    if request.method == 'POST':
        request.session['character_background'] = request.POST.get('background')
        return redirect('character_create_relationship')
    backgrounds = [
        ('real_life', 'Real Life'),
        ('fantasy', 'Fantasy'),
        ('school', 'School'),
    ]
    return render(request, 'character/create_background.html', {'backgrounds': backgrounds})

@login_required
def character_create_relationship(request):
    if request.method == 'POST':
        request.session['character_relationship'] = request.POST.get('relationship')
        return redirect('character_create_dynamic')
    relationships = [
        ('bully', 'Bully Girl'),
        ('stepmom', 'Stepmom'),
        ('stepsister', 'Step-sister'),
        ('best_friend', 'Best Friend'),
        ('girlfriend', 'Girlfriend'),
        ('ex_girlfriend', 'Ex-girlfriend'),
        ('streamer', 'Streamer'),
    ]
    return render(request, 'character/create_relationship.html', {'relationships': relationships})

@login_required
def character_create_dynamic(request):
    if request.method == 'POST':
        request.session['character_dynamic'] = request.POST.get('dynamic')
        return redirect('character_create_species')
    dynamics = [
        ('submissive', 'Submissive'),
        ('tsundere', 'Tsundere'),
        ('dominant', 'Dominant'),
        ('monster_girl', 'Monster girl'),
        ('exhibitionist', 
         "Doesn't mind exposing herself"),
    ]
    return render(request, 'character/create_dynamic.html', {'dynamics': dynamics})

@login_required
def character_create_species(request):
    if request.method == 'POST':
        request.session['character_species'] = request.POST.get('species')
        request.session['character_appearance'] = request.POST.get('appearance')
        return redirect('character_create_confirm')
    # Example species and placeholder images
    species_tabs = [
        ('human', 'Human'),
        ('elf', 'Elf'),
        ('vampire', 'Vampire'),
        ('monster', 'Monster Girl'),
    ]
    # Each species has 4 placeholder appearances
    appearances = {
        'human': [
            ('appearance1', 'Appearance 1'),
            ('appearance2', 'Appearance 2'),
            ('appearance3', 'Appearance 3'),
            ('appearance4', 'Appearance 4'),
        ],
        'elf': [
            ('appearance1', 'Appearance 1'),
            ('appearance2', 'Appearance 2'),
            ('appearance3', 'Appearance 3'),
            ('appearance4', 'Appearance 4'),
        ],
        'vampire': [
            ('appearance1', 'Appearance 1'),
            ('appearance2', 'Appearance 2'),
            ('appearance3', 'Appearance 3'),
            ('appearance4', 'Appearance 4'),
        ],
        'monster': [
            ('appearance1', 'Appearance 1'),
            ('appearance2', 'Appearance 2'),
            ('appearance3', 'Appearance 3'),
            ('appearance4', 'Appearance 4'),
        ],
    }
    selected_species = request.GET.get('species', 'human')
    return render(request, 'character/create_species.html', {
        'species_tabs': species_tabs,
        'appearances': appearances,
        'selected_species': selected_species,
    })

@login_required
def character_create_confirm(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        character = Character.objects.create(
            user=request.user,
            name=name,
            species=request.session.get('character_species'),
            appearance='testplaceholder.png',  # Always use placeholder for now
            background=request.session.get('character_background'),
            relationship=request.session.get('character_relationship'),
            dynamic=request.session.get('character_dynamic'),
        )
        # Clear session data
        for key in [
            'character_species', 'character_appearance', 'character_background',
            'character_relationship', 'character_dynamic']:
            if key in request.session:
                del request.session[key]
        return redirect('chat_room', character_id=character.id)
    # Show summary and ask for name
    context = {
        'species': request.session.get('character_species'),
        'appearance': request.session.get('character_appearance'),
        'background': request.session.get('character_background'),
        'relationship': request.session.get('character_relationship'),
        'dynamic': request.session.get('character_dynamic'),
    }
    return render(request, 'character/create_confirm.html', context)

@login_required
def chat_room(request, character_id):
    character = get_object_or_404(Character, id=character_id, user=request.user)
    messages = ChatMessage.objects.filter(character=character)
    
    # Get the last message's response options, if any
    response_options = []
    if messages.exists():
        last_message = messages.last()
        if not last_message.is_user:  # If last message was from character
            response_options = last_message.response_options.all()
    
    return render(request, 'chat/chat_room.html', {
        'character': character,
        'messages': messages,
        'response_options': response_options,
    })

@login_required
@require_POST
def send_response(request):
    try:
        data = json.loads(request.body)
        option_id = data.get('option_id')
        character_id = data.get('character_id')
        
        option = get_object_or_404(ResponseOption, id=option_id)
        character = get_object_or_404(Character, id=character_id, user=request.user)
        
        # Create user message from selected option
        user_message = ChatMessage.objects.create(
            character=character,
            user=request.user,
            content=option.content,
            is_user=True
        )
        
        # Create character response (this would be replaced with AI generation)
        character_message = ChatMessage.objects.create(
            character=character,
            user=request.user,
            content="This is a sample response to your choice.",
            is_user=False
        )
        
        # Create new response options
        ResponseOption.objects.create(
            message=character_message,
            content="New Option 1: Continue the conversation",
            order=0
        )
        ResponseOption.objects.create(
            message=character_message,
            content="New Option 2: Take a different approach",
            order=1
        )
        ResponseOption.objects.create(
            message=character_message,
            content="New Option 3: Express your feelings",
            order=2
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})