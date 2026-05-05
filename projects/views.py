from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Project, Skill
from .forms import ProjectForm


def project_list(request):
    """Главная страница со списком проектов и фильтром по навыкам"""
    projects = Project.objects.filter(status='open').order_by('-created_at')
    
    # Фильтрация по навыкам (вариант 3)
    active_skill = request.GET.get('skill')
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    
    # Пагинация по 12 проектов
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Все навыки для фильтра
    all_skills = Skill.objects.values_list('name', flat=True).distinct()
    
    context = {
        'projects': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, project_id):
    """Страница проекта"""
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project(request):
    """Создание проекта"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Автор автоматически становится участником
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def edit_project(request, project_id):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=project_id)
    
    # Проверка прав: только владелец может редактировать
    if project.owner != request.user:
        return redirect(f'/projects/{project_id}/')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project_id}/')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
        'project': project,
    })


@login_required
@require_POST
def complete_project(request, project_id):
    """Завершение проекта (меняем статус на closed)"""
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)
    
    if project.status != 'open':
        return JsonResponse({'status': 'error', 'message': 'Проект уже завершён'}, status=400)
    
    project.status = 'closed'
    project.save()
    
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@login_required
@require_POST
def toggle_participate(request, project_id):
    """Участие/отказ от участия в проекте"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True
    
    return JsonResponse({
        'status': 'ok',
        'participant': is_participant,
    })


def skill_autocomplete(request):
    """Автодополнение навыков (для skills.js)"""
    q = request.GET.get('q', '')
    skills = Skill.objects.filter(name__istartswith=q)[:10]
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, project_id):
    """Добавление навыка к проекту"""
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    
    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse({'status': 'error', 'message': 'skill_id or name required'}, status=400)
    
    # Добавляем навык, если его ещё нет
    if skill not in project.skills.all():
        project.skills.add(skill)
        added = True
    else:
        added = False
    
    return JsonResponse({
        'id': skill.id,
        'name': skill.name,
        'added': added,
        'created': skill_id is None and added,
    })


@login_required
@require_POST
def remove_project_skill(request, project_id, skill_id):
    """Удаление навыка из проекта"""
    project = get_object_or_404(Project, id=project_id)
    
    if project.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'Нет прав'}, status=403)
    
    skill = get_object_or_404(Skill, id=skill_id)
    
    if skill in project.skills.all():
        project.skills.remove(skill)
    
    return JsonResponse({'status': 'ok'})