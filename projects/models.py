from django.db import models
from django.conf import settings


class Skill(models.Model):
    """Навык (для проектов, вариант 3)"""
    name = models.CharField(max_length=124, unique=True, verbose_name='Название навыка')
    
    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    github_url = models.URLField(blank=True, null=True, verbose_name='GitHub ссылка')
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open', verbose_name='Статус')
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )
    skills = models.ManyToManyField(
        Skill,
        related_name='projects',
        blank=True,
        verbose_name='Необходимые навыки'
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name