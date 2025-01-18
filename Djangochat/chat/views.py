

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message  # Correct import
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})

@login_required
def chat_view(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/chat.html', {'users': users})

@login_required
def get_messages(request, user_id):
    print(f"Fetching messages for users {request.user.id} and {user_id}")
    other_user = User.objects.get(id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    message_list = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for msg in messages]
    
    print(f"Found {len(message_list)} messages")
    return JsonResponse(message_list, safe=False)













