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

@login_required
@require_POST
def send_message(request):
    data = json.loads(request.body)
    character_id = data.get('character_id')
    message_content = data.get('message')
    character = get_object_or_404(Character, id=character_id, user=request.user)

    # Save user message
    user_message = ChatMessage.objects.create(
        character=character,
        user=request.user,
        content=message_content,
        is_user=True
    )

    # Get Claude response
    reply = get_risu_response(message_content)

    # Save Claude reply
    character_message = ChatMessage.objects.create(
        character=character,
        user=request.user,
        content=reply,
        is_user=False
    )

    # Only create new options if not in custom chat mode
    if not request.session.get('custom_chat_mode', False):
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
            content="메시지 직접 입력하기",
            order=2
        )

    return JsonResponse({"reply": reply})

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

    custom_chat_mode = request.session.get('custom_chat_mode', False)

    # If no messages exist and not in custom chat mode, create initial system message and options
    if not messages.exists() and not custom_chat_mode:
        initial_message = ChatMessage.objects.create(
            character=character,
            user=request.user,
            content="Choose how to start the conversation.",
            is_user=False
        )
        ResponseOption.objects.create(
            message=initial_message,
            content="New Option 1: Continue the conversation",
            order=0
        )
        ResponseOption.objects.create(
            message=initial_message,
            content="New Option 2: Take a different approach",
            order=1
        )
        ResponseOption.objects.create(
            message=initial_message,
            content="메시지 직접 입력하기",
            order=2
        )
        messages = ChatMessage.objects.filter(character=character)

    # Get the last message's response options, if any
    response_options = []
    if messages.exists() and not custom_chat_mode:
        last_message = messages.last()
        if not last_message.is_user:
            response_options = last_message.response_options.all()

    return render(request, 'chat/chat_room.html', {
        'character': character,
        'messages': messages,
        'response_options': response_options,
        'custom_chat_mode': custom_chat_mode,
    })

@login_required
@require_POST
def send_response(request):
    data = json.loads(request.body)
    option_id = data.get('option_id')
    character_id = data.get('character_id')
    option = get_object_or_404(ResponseOption, id=option_id)
    character = get_object_or_404(Character, id=character_id, user=request.user)

    # Save user message
    user_message = ChatMessage.objects.create(
        character=character,
        user=request.user,
        content=option.content,
        is_user=True
    )

    if option.content == '메시지 직접 입력하기':
        request.session['custom_chat_mode'] = True
        return JsonResponse({'status': 'success'})
    else:
        # Use the preset response (simulate or fetch from PreMadeResponse if needed)
        character_message = ChatMessage.objects.create(
            character=character,
            user=request.user,
            content="This is a sample response to your choice.",
            is_user=False
        )
        # Create new response options as before, only if not in custom chat mode
        if not request.session.get('custom_chat_mode', False):
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
                content="메시지 직접 입력하기",
                order=2
            )
        return JsonResponse({'status': 'success'})