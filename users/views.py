from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from .forms import RegisterForm, LoginForm, EditProfileForm, PasswordChangeForm
from projects.models import Project


def user_list(request):
    """Страница со списком всех пользователей"""
    users = User.objects.all().order_by('-created_at')
    return render(request, 'users/participants.html', {'participants': users})


def user_detail(request, user_id):
    """Страница пользователя"""
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user-details.html', {'user': user})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/projects/list/')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Авторизация пользователя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('/projects/list/')
            else:
                form.add_error(None, 'Неверный email или пароль')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """Выход из системы"""
    logout(request)
    return redirect('/projects/list/')


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/users/{request.user.id}/')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})