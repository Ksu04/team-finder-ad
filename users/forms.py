from django import forms
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    
    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Email',
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'GitHub URL',
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
            # Переопределяем виджет для avatar, чтобы убрать ссылку на текущий файл
            'avatar': forms.ClearableFileInput(attrs={'class': 'avatar-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем текст "Currently" и ссылку на файл
        if self.fields['avatar'].widget:
            self.fields['avatar'].widget.template_name = 'django/forms/widgets/clearable_file_input.html'
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Приводим к формату +7XXXXXXXXXX
            if phone.startswith('8'):
                phone = '+7' + phone[1:]
            elif not phone.startswith('+7'):
                raise forms.ValidationError('Номер должен начинаться с 8 или +7')
            
            # Проверяем, что остальные символы - цифры
            if not phone[2:].isdigit() or len(phone) != 12:
                raise forms.ValidationError('Номер должен быть в формате +7XXXXXXXXXX (10 цифр после +7)')
            
            # Проверка уникальности
            user_id = self.instance.id if self.instance else None
            if User.objects.exclude(id=user_id).filter(phone=phone).exists():
                raise forms.ValidationError('Этот номер телефона уже используется')
        return phone
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and 'github.com' not in url:
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class PasswordChangeForm(BasePasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Текущий пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')
    
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']