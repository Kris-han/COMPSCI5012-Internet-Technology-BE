from django.urls import path
from .views import login, register,logout,reset_password

urlpatterns = [
    path('login', login),
    path('register', register),
    path('logout', logout),
    path('resetPassword', reset_password),
]
