from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),  
    path('messages/<int:user_id>/', views.get_messages, name='get_messages'),
]