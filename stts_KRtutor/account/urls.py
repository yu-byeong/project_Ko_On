from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_view
from .views import register

app_name = "account"

urlpatterns = [
    path('login/', auth_view.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('register/', register, name='register')
]
