import os
import requests

def get_risu_response(user_message):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.environ['ANTHROPIC_API_KEY'],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        content_items = response_data.get('content', [])
        if content_items and isinstance(content_items, list):
            return content_items[0].get('text', '[No text in content]')
        else:
            return '[No content provided]'
    else:
        return f"[Error: {response.status_code}]"
