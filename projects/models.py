from django.conf import settings
from django.db import models

# Константы
SKILL_NAME_MAX_LENGTH = 124
PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6

# Статусы проектов
PROJECT_STATUS_OPEN = "open"
PROJECT_STATUS_CLOSED = "closed"

PROJECT_STATUS_CHOICES = [
    (PROJECT_STATUS_OPEN, "Открыт"),
    (PROJECT_STATUS_CLOSED, "Закрыт"),
]


class Skill(models.Model):
    """Навык (для проектов, вариант 3)"""

    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH, unique=True, verbose_name="Название навыка"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LENGTH, verbose_name="Название проекта"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    github_url = models.URLField(blank=True, null=True, verbose_name="GitHub ссылка")
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name="Статус",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )
    skills = models.ManyToManyField(
        Skill, related_name="projects", blank=True, verbose_name="Необходимые навыки"
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]  # Сортировка по умолчанию: от новых к старым

    def __str__(self):
        return self.name
