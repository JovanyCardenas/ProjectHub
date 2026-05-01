from django.contrib import admin
from .models import Project, Technology, ProjectTechnology, Feature


class ProjectTechnologyInline(admin.TabularInline):
    model = ProjectTechnology
    extra = 1


class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "priority", "category", "updated_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("name", "description", "github_url")
    inlines = [ProjectTechnologyInline, FeatureInline]


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "tech_type", "website_url")
    list_filter = ("tech_type",)
    search_fields = ("name",)


@admin.register(ProjectTechnology)
class ProjectTechnologyAdmin(admin.ModelAdmin):
    list_display = ("project", "technology")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "priority", "difficulty")
    list_filter = ("status", "priority", "difficulty")
    search_fields = ("title", "description")