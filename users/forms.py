from django import forms
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm

from .models import User
from .utils import validate_and_normalize_phone, validate_github_url


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub URL",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем текст "Currently" и ссылку на файл для поля avatar
        if self.fields.get("avatar"):
            self.fields[
                "avatar"
            ].widget.template_name = "django/forms/widgets/clearable_file_input.html"

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        # Используем вынесенную функцию валидации
        return validate_and_normalize_phone(phone, user_id=self.instance.id)

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        # Используем вынесенную функцию валидации
        return validate_github_url(url)


class PasswordChangeForm(BasePasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль")
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(
        widget=forms.PasswordInput, label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]
