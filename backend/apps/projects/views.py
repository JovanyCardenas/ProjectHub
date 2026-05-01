from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm, FeatureForm, TechnologyForm, ProjectTechnologyForm
from .models import Project, Feature, Technology, ProjectTechnology

from django.views.decorators.http import require_POST
from django.db import models
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse

from .github import parse_github_repo_url, fetch_repo_issues

@login_required
def project_list(request):
    show_archived = request.GET.get("show_archived", "")

    projects = Project.objects.filter(created_by=request.user)

    if not show_archived:
        projects = projects.exclude(status=Project.Status.ARCHIVED)

    search = request.GET.get("q", "")
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    category = request.GET.get("category", "")

    if search:
        projects = projects.filter(
            models.Q(name__icontains=search) |
            models.Q(description__icontains=search) |
            models.Q(category__icontains=search)
        )

    if status:
        projects = projects.filter(status=status)

    if priority:
        projects = projects.filter(priority=priority)

    if category:
        projects = projects.filter(category__icontains=category)

    return render(request, "projects/project_list.html", {
        "projects": projects,
        "search": search,
        "status": status,
        "priority": priority,
        "category": category,
        "status_choices": Project.Status.choices,
        "priority_choices": Project.Priority.choices,
        "show_archived": show_archived,
    })


@login_required
@require_POST
def feature_reorder(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    updates = data.get("updates", [])

    for update in updates:
        feature = Feature.objects.filter(
            pk=update.get("id"),
            project=project,
        ).first()

        if feature:
            feature.status = update.get("status", feature.status)
            feature.sort_order = update.get("sort_order", feature.sort_order)
            feature.save(update_fields=["status", "sort_order", "updated_at"])

    return JsonResponse({"ok": True})

@login_required
def project_dashboard(request):
    projects = Project.objects.filter(created_by=request.user)
    features = Feature.objects.filter(project__created_by=request.user)

    total_projects = projects.count()
    active_projects = projects.exclude(status__in=[
        Project.Status.ARCHIVED,
        Project.Status.PAUSED,
    ]).count()

    features_in_progress = features.filter(status=Feature.Status.IN_PROGRESS).count()
    completed_features = features.filter(status=Feature.Status.DONE).count()

    recent_projects = projects.order_by("-updated_at")[:5]
    high_priority_projects = projects.filter(
        priority__in=[Project.Priority.HIGH, Project.Priority.URGENT]
    )[:5]

    return render(request, "projects/project_dashboard.html", {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "features_in_progress": features_in_progress,
        "completed_features": completed_features,
        "recent_projects": recent_projects,
        "high_priority_projects": high_priority_projects,
    })

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)

    features = project.features.all()
    project_technologies = project.project_technologies.select_related("technology")

    tech_groups = {}
    for item in project_technologies:
        tech_type = item.technology.get_tech_type_display()
        tech_groups.setdefault(tech_type, []).append(item)

    total_features = features.count()
    done_features = features.filter(status=Feature.Status.DONE).count()

    progress_percent = 0
    if total_features > 0:
        progress_percent = round((done_features / total_features) * 100)

    return render(request, "projects/project_detail.html", {
        "project": project,
        "features": features,
        "project_technologies": project_technologies,
        "tech_groups": tech_groups,
        "total_features": total_features,
        "done_features": done_features,
        "progress_percent": progress_percent,
    })


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, "projects/project_form.html", {
        "form": form,
        "title": "Create Project",
    })


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/project_form.html", {
        "form": form,
        "title": "Edit Project",
        "project": project,
    })


@login_required
def feature_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)

    if request.method == "POST":
        form = FeatureForm(request.POST)

        if form.is_valid():
            feature = form.save(commit=False)
            feature.project = project
            feature.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = FeatureForm()

    return render(request, "projects/feature_form.html", {
        "form": form,
        "project": project,
        "title": "Add Feature",
    })


@login_required
def technology_create(request):
    if request.method == "POST":
        form = TechnologyForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("projects:project_list")
    else:
        form = TechnologyForm()

    return render(request, "projects/technology_form.html", {
        "form": form,
        "title": "Add Technology",
    })


@login_required
def project_technology_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)

    if request.method == "POST":
        form = ProjectTechnologyForm(request.POST)

        if form.is_valid():
            project_technology = form.save(commit=False)
            project_technology.project = project
            project_technology.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectTechnologyForm()

    return render(request, "projects/project_technology_form.html", {
        "form": form,
        "project": project,
        "title": "Add Technology to Project",
    })

@login_required
def feature_update(request, project_pk, feature_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    feature = get_object_or_404(Feature, pk=feature_pk, project=project)

    if request.method == "POST":
        form = FeatureForm(request.POST, instance=feature)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = FeatureForm(instance=feature)

    return render(request, "projects/feature_form.html", {
        "form": form,
        "project": project,
        "title": "Edit Feature",
    })


@login_required
def feature_delete(request, project_pk, feature_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    feature = get_object_or_404(Feature, pk=feature_pk, project=project)

    if request.method == "POST":
        feature.delete()
        return redirect("projects:project_detail", pk=project.pk)

    return render(request, "projects/feature_confirm_delete.html", {
        "project": project,
        "feature": feature,
    })


@login_required
@require_POST
def feature_mark_done(request, project_pk, feature_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    feature = get_object_or_404(Feature, pk=feature_pk, project=project)

    feature.status = Feature.Status.DONE
    feature.save(update_fields=["status", "updated_at"])

    return redirect("projects:project_detail", pk=project.pk)


@login_required
def project_technology_update(request, project_pk, project_technology_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    project_technology = get_object_or_404(
        ProjectTechnology,
        pk=project_technology_pk,
        project=project,
    )

    if request.method == "POST":
        form = ProjectTechnologyForm(request.POST, instance=project_technology)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectTechnologyForm(instance=project_technology)

    return render(request, "projects/project_technology_form.html", {
        "form": form,
        "project": project,
        "title": "Edit Project Technology",
    })


@login_required
def project_technology_delete(request, project_pk, project_technology_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    project_technology = get_object_or_404(
        ProjectTechnology,
        pk=project_technology_pk,
        project=project,
    )

    if request.method == "POST":
        project_technology.delete()
        return redirect("projects:project_detail", pk=project.pk)

    return render(request, "projects/project_technology_confirm_delete.html", {
        "project": project,
        "project_technology": project_technology,
    })

@login_required
@require_POST
def project_archive(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    project.status = Project.Status.ARCHIVED
    project.save(update_fields=["status", "updated_at"])
    return redirect("projects:project_list")


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)

    if request.method == "POST":
        project.delete()
        return redirect("projects:project_list")

    return render(request, "projects/project_confirm_delete.html", {
        "project": project,
    })

@login_required
@require_POST
def project_restore(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    project.status = Project.Status.PLANNING
    project.save(update_fields=["status", "updated_at"])
    return redirect("projects:project_detail", pk=project.pk)

from django.views.decorators.http import require_POST

@login_required
@require_POST
def feature_update_status(request, project_pk, feature_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    feature = get_object_or_404(Feature, pk=feature_pk, project=project)

    new_status = request.POST.get("status")

    if new_status in dict(Feature.Status.choices):
        feature.status = new_status
        feature.save(update_fields=["status", "updated_at"])

    return redirect("projects:project_detail", pk=project.pk)

@login_required
@require_POST
def project_sync_github_issues(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)

    owner, repo = parse_github_repo_url(project.github_url)

    if not owner or not repo:
        messages.error(request, "Please add a valid GitHub repository URL first.")
        return redirect("projects:project_detail", pk=project.pk)

    try:
        issues = fetch_repo_issues(owner, repo)
    except Exception as error:
        messages.error(request, f"Could not sync GitHub issues: {error}")
        return redirect("projects:project_detail", pk=project.pk)

    created_count = 0
    updated_count = 0

    for issue in issues:
        feature, created = Feature.objects.update_or_create(
            project=project,
            github_issue_number=issue["number"],
            defaults={
                "title": issue["title"],
                "description": issue.get("body") or "",
                "github_issue_id": issue["id"],
                "github_issue_state": issue["state"],
                "github_issue_url": issue["html_url"],
                "github_last_synced_at": timezone.now(),
                "status": Feature.Status.DONE if issue["state"] == "closed" else Feature.Status.BACKLOG,
            },
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    messages.success(
        request,
        f"GitHub sync complete. Created {created_count}, updated {updated_count}."
    )

    return redirect("projects:project_detail", pk=project.pk)

@login_required
def project_kanban(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)

    features = project.features.all()

    columns = {
        "backlog": [],
        "planned": [],
        "in_progress": [],
        "done": [],
        "removed": [],
    }

    for feature in features:
        columns[feature.status].append(feature)

    return render(request, "projects/project_kanban.html", {
        "project": project,
        "columns": columns,
    })

@login_required
@require_POST
def feature_update_status(request, project_pk, feature_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)
    feature = get_object_or_404(Feature, pk=feature_pk, project=project)

    new_status = request.POST.get("status")

    if new_status in dict(Feature.Status.choices):
        feature.status = new_status
        feature.save(update_fields=["status", "updated_at"])

    return redirect("projects:project_detail", pk=project.pk)

@login_required
@require_POST
def feature_quick_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, created_by=request.user)

    title = request.POST.get("title", "").strip()
    status = request.POST.get("status", Feature.Status.BACKLOG)

    if title and status in dict(Feature.Status.choices):
        Feature.objects.create(
            project=project,
            title=title,
            status=status,
            priority=Feature.Priority.MEDIUM,
            difficulty=Feature.Difficulty.UNKNOWN,
        )

    return redirect("projects:project_kanban", pk=project.pk)