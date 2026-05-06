import random
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 100
AVATAR_FONT_SIZE = 50
DEFAULT_AVATAR_FONT = "arial.ttf"

COLOR_RED = "#FF6B6B"
COLOR_TEAL = "#4ECDC4"
COLOR_BLUE = "#45B7D1"
COLOR_GREEN = "#96CEB4"
COLOR_YELLOW = "#FFEAA7"
COLOR_PURPLE = "#DDA0DD"
COLOR_MINT = "#98D8C8"
COLOR_PINK = "#F7CAC9"
COLOR_LIGHT_GREEN = "#B5EAD7"
COLOR_LAVENDER = "#C7CEEA"

AVATAR_COLORS = [
    COLOR_RED,
    COLOR_TEAL,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_PURPLE,
    COLOR_MINT,
    COLOR_PINK,
    COLOR_LIGHT_GREEN,
    COLOR_LAVENDER,
]


def get_random_avatar_color():
    """Возвращает случайный цвет из списка цветов для аватара"""
    return random.choice(AVATAR_COLORS)


def generate_avatar_from_letter(letter, size=AVATAR_SIZE, font_size=AVATAR_FONT_SIZE):
    """
    Генерирует аватар с заданной буквой.

    Args:
        letter: Буква для отображения на аватаре
        size: Размер аватара в пикселях
        font_size: Размер шрифта

    Returns:
        ContentFile: Файл с изображением аватара
    """
    color = get_random_avatar_color()

    image = Image.new("RGB", (size, size), color)
    draw = ImageDraw.Draw(image)

    letter = letter.upper() if letter else "?"

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size
        )
    except (OSError, IOError):
        try:
            font = ImageFont.truetype(DEFAULT_AVATAR_FONT, font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(letter, font=font)

    position = ((size - text_width) // 2, (size - text_height) // 2)

    draw.text(position, letter, fill="white", font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return ContentFile(buffer.read(), name=f"avatar_{letter}.png")


def validate_and_normalize_phone(phone, user_id=None):
    """
    Валидация и нормализация номера телефона.

    Args:
        phone: Номер телефона для проверки
        user_id: ID пользователя (для проверки уникальности при редактировании)

    Returns:
        str: Нормализованный номер телефона в формате +7XXXXXXXXXX

    Raises:
        ValidationError: Если номер не проходит валидацию
    """
    import re

    from django.core.exceptions import ValidationError

    from .models import User

    if not phone:
        return phone

    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif not phone.startswith("+7"):
        raise ValidationError("Номер должен начинаться с 8 или +7")

    if not re.match(r"^\+7\d{10}$", phone):
        raise ValidationError(
            "Номер должен быть в формате +7XXXXXXXXXX (10 цифр после +7)"
        )

    queryset = User.objects.filter(phone=phone)
    if user_id:
        queryset = queryset.exclude(id=user_id)

    if queryset.exists():
        raise ValidationError("Этот номер телефона уже используется")

    return phone


def validate_github_url(url):
    """
    Валидация GitHub URL.

    Args:
        url: URL для проверки

    Returns:
        str: URL, если валидация пройдена

    Raises:
        ValidationError: Если URL не ведёт на GitHub
    """
    from django.core.exceptions import ValidationError

    if url and "github.com" not in url:
        raise ValidationError("Ссылка должна вести на GitHub")
    return url
