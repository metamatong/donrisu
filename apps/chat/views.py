import os
import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # For quick testing, not recommended in production

def chat_page(request):
    """Renders the main chat UI."""
    return render(request, 'chat/chat.html')

@csrf_exempt  # For simplicity; otherwise you’ll need to handle CSRF tokens in JS
def send_message(request):
    """Handles the AJAX/Fetch request to call Anthropic's API."""
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '')

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": os.environ['ANTHROPIC_API_KEY'],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",  # Example model name
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }

        # Make the request
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            # Extract the text from the content list (as returned by Claude)
            content_items = response_data.get('content', [])
            if content_items and isinstance(content_items, list):
                # Assume the first item is the reply
                completion_text = content_items[0].get('text', '[No text in content]')
            else:
                completion_text = '[No content provided]'

            return JsonResponse({"reply": completion_text})
        else:
            return JsonResponse({
                "error": "Request to Anthropic failed",
                "status_code": response.status_code
            })
    else:
        return JsonResponse({"error": "Invalid request method. POST expected."}, status=400)