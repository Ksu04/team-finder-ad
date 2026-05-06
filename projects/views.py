import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN, Project, Skill
from .utils import paginate_queryset


def project_list(request):
    """Главная страница со списком проектов и фильтром по навыкам"""
    projects = Project.objects.filter(status=PROJECT_STATUS_OPEN)

    active_skill = request.GET.get("skill")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    projects_page = paginate_queryset(projects, request, items_per_page=12)

    all_skills = Skill.objects.values_list("name", flat=True).distinct()

    context = {
        "projects": projects_page,
        "all_skills": all_skills,
        "active_skill": active_skill,
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, project_id):
    """Страница проекта"""
    project = get_object_or_404(Project, id=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    """Создание проекта"""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("project_detail", project_id=project.id)
    else:
        form = ProjectForm()

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project(request, project_id):
    """Редактирование проекта"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return redirect("project_detail", project_id=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_detail", project_id=project_id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
            "project": project,
        },
    )


@login_required
@require_POST
def complete_project(request, project_id):
    """Завершение проекта (меняем статус на closed)"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )

    # Используем константу статуса
    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже завершён"},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = PROJECT_STATUS_CLOSED
    project.save()

    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate(request, project_id):
    """Участие/отказ от участия в проекте"""
    project = get_object_or_404(Project, id=project_id)

    is_participant = project.participants.filter(id=request.user.id).exists()

    if is_participant:
        project.participants.remove(request.user)
        is_participant = False
    else:
        project.participants.add(request.user)
        is_participant = True

    return JsonResponse(
        {
            "status": "ok",
            "participant": is_participant,
        }
    )


def skill_autocomplete(request):
    """Автодополнение навыков (для skills.js)"""
    q = request.GET.get("q", "")
    skills = Skill.objects.filter(name__istartswith=q)[:10]
    data = [{"id": s.id, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, project_id):
    """Добавление навыка к проекту"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON"},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_id = data.get("skill_id")
    skill_name = data.get("name")

    if skill_id:
        skill = get_object_or_404(Skill, id=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse(
            {"status": "error", "message": "skill_id or name required"},
            status=HTTPStatus.BAD_REQUEST,
        )

    has_skill = project.skills.filter(id=skill.id).exists()

    if not has_skill:
        project.skills.add(skill)
        added = True
    else:
        added = False

    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "added": added,
            "created": skill_id is None and added,
        }
    )


@login_required
@require_POST
def remove_project_skill(request, project_id, skill_id):
    """Удаление навыка из проекта"""
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "message": "Нет прав"}, status=HTTPStatus.FORBIDDEN
        )

    skill = get_object_or_404(Skill, id=skill_id)

    has_skill = project.skills.filter(id=skill.id).exists()

    if has_skill:
        project.skills.remove(skill)

    return JsonResponse({"status": "ok"})
