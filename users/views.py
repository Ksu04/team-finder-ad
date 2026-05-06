from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from projects.utils import paginate_queryset

from .forms import EditProfileForm, LoginForm, PasswordChangeForm, RegisterForm
from .models import User


def user_list(request):
    """Страница со списком всех пользователей"""
    users = User.objects.all()

    users_page = paginate_queryset(users, request, items_per_page=12)

    return render(request, "users/participants.html", {"participants": users_page})


def user_detail(request, user_id):
    """Страница пользователя"""
    user = get_object_or_404(User, id=user_id)
    return render(request, "users/user-details.html", {"user": user})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("project_list")
    else:
        form = RegisterForm()

    return render(request, "users/register.html", {"form": form})


def user_login(request):
    """Авторизация пользователя"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect("project_list")
            form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    """Выход из системы"""
    logout(request)
    return redirect("project_list")


@login_required
def edit_profile(request):
    """Редактирование профиля"""
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("user_detail", user_id=request.user.id)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("user_detail", user_id=request.user.id)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/change_password.html", {"form": form})
