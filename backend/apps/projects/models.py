from django.conf import settings
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        IDEA = "idea", "Idea"
        PLANNING = "planning", "Planning"
        BUILDING = "building", "Building"
        TESTING = "testing", "Testing"
        LAUNCHED = "launched", "Launched"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDEA,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    category = models.CharField(max_length=100, blank=True)

    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    docs_url = models.URLField(blank=True)

    start_date = models.DateField(null=True, blank=True)
    target_launch_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # If using your SaaS tenant system, add this later or now:
    # tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="projects")

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class Technology(models.Model):
    class TechType(models.TextChoices):
        FRONTEND = "frontend", "Frontend"
        BACKEND = "backend", "Backend"
        DATABASE = "database", "Database"
        AUTH = "auth", "Authentication"
        PAYMENT = "payment", "Payment"
        HOSTING = "hosting", "Hosting"
        AI = "ai", "AI"
        INTEGRATION = "integration", "Integration"
        DEVOPS = "devops", "DevOps"
        OTHER = "other", "Other"

    name = models.CharField(max_length=100)
    tech_type = models.CharField(max_length=30, choices=TechType.choices)
    website_url = models.URLField(blank=True)

    class Meta:
        ordering = ["tech_type", "name"]
        unique_together = ["name", "tech_type"]

    def __str__(self):
        return f"{self.name} ({self.get_tech_type_display()})"


class ProjectTechnology(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_technologies",
    )
    technology = models.ForeignKey(
        Technology,
        on_delete=models.CASCADE,
        related_name="project_technologies",
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ["project", "technology"]

    def __str__(self):
        return f"{self.project.name} - {self.technology.name}"


class Feature(models.Model):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        REMOVED = "removed", "Removed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"
        UNKNOWN = "unknown", "Unknown"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="features",
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.BACKLOG,
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.UNKNOWN,
    )

    github_issue_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-priority", "title"]

    def __str__(self):
        return self.title