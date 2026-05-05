import random
from io import BytesIO

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=124, verbose_name='Имя')
    surname = models.CharField(max_length=124, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    phone = models.CharField(max_length=12, verbose_name='Телефон', blank=True, default='')
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub')
    about = models.TextField(max_length=256, blank=True, null=True, verbose_name='О себе')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        """Генерирует аватар с первой буквой имени"""
        size = 100
        color = self._get_random_color()

        image = Image.new('RGB', (size, size), color)
        draw = ImageDraw.Draw(image)

        letter = self.name[0].upper() if self.name else '?'

        # Пытаемся загрузить шрифт, если не получается - используем стандартный
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
        except (OSError, IOError):
            try:
                # Для Windows
                font = ImageFont.truetype("arial.ttf", 50)
            except (OSError, IOError):
                font = ImageFont.load_default()

        # Получаем размер текста
        try:
            bbox = draw.textbbox((0, 0), letter, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Для старых версий PIL
            text_width, text_height = draw.textsize(letter, font=font)

        position = ((size - text_width) // 2, (size - text_height) // 2)

        draw.text(position, letter, fill='white', font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        return ContentFile(buffer.read(), name=f'avatar_{self.email}.png')

    def _get_random_color(self):
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7CAC9',
            '#B5EAD7', '#C7CEEA'
        ]
        return random.choice(colors)