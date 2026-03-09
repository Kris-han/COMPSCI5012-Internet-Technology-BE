from django.db import models
from django.contrib.auth.models import AbstractUser
class UserProfile(AbstractUser):
    """
    自定义用户模型：支持登录、注册以及额外的个人信息
    """
    # 扩展字段
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="手机号", null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="头像")
    nickname = models.CharField(max_length=50, blank=True, verbose_name="昵称")
class Gender(models.IntegerChoices):
        UNKNOWN = 0, '保密'
        MALE = 1, '男'
        FEMALE = 2, '女'
gender = models.IntegerField(choices=Gender.choices, default=Gender.UNKNOWN, verbose_name="性别")
class Meta:
        db_table = "user_profile" # 保持和你之前代码统一的命名风格
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import RegisterForm, LoginForm

# 注册视图
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # 保存用户（密码自动加密）
            user = form.save()
            # 自动登录新注册用户
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            # 注册成功后跳转到仪表盘
            return redirect('dashboard')
        else:
            # 表单验证失败，显示错误信息
            messages.error(request, "Registration failed. Please check the form and try again.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'title': 'Register'
    })

# 登录视图
def login_view(request):
    # 已登录用户直接跳转到仪表盘
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 验证用户身份
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # 跳转到之前访问的页面（若无则跳仪表盘）
                next_page = request.GET.get('next', 'dashboard')
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Login'
    })

# 登出视图
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')
    from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

# 注册表单（扩展UserCreationForm，适配自定义UserProfile）
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    nickname = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nickname'}))
    phone_number = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'nickname', 'phone_number', 'password1', 'password2', 'avatar')

    # 自定义字段样式
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.name not in ['avatar']:
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]