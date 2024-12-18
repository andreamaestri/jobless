import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from django.conf import settings

@login_required
def ai_assistant(request):
    response_content = None
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        cv_content = request.POST.get('cv_content', '')
        
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=settings.GITHUB_TOKEN,
        )

        messages = [
            {
                "role": "system",
                "content": "You are a helpful, professional CV assistant. You help users improve their CVs and provide professional feedback.",
            },
            {
                "role": "user",
                "content": f"Here is my CV content:\n{cv_content}\n\nUser question: {user_input} please don't use markdown in your response"
            }
        ]

        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            stream=True
        )

        response_content = ""
        for update in response:
            if update.choices[0].delta.content:
                response_content += update.choices[0].delta.content

    return render(request, 'ai_assistant/assistant.html', {
        'response': response_content
    })