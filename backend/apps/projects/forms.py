from django import forms
from .models import Project, Feature, Technology, ProjectTechnology


BASE_INPUT_CLASSES = (
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-3 "
    "text-gray-900 shadow-sm placeholder:text-gray-400 "
    "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
)

SELECT_CLASSES = (
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-3 "
    "text-gray-900 shadow-sm focus:border-blue-500 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500/20"
)

TEXTAREA_CLASSES = (
    "w-full rounded-lg border border-gray-300 bg-white px-4 py-3 "
    "text-gray-900 shadow-sm placeholder:text-gray-400 "
    "focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "status",
            "priority",
            "category",
            "github_url",
            "live_url",
            "docs_url",
            "start_date",
            "target_launch_date",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "Project name"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4, "placeholder": "Describe this project..."}),
            "status": forms.Select(attrs={"class": SELECT_CLASSES}),
            "priority": forms.Select(attrs={"class": SELECT_CLASSES}),
            "category": forms.TextInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "SaaS, AI, CRM, Event, etc."}),
            "github_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "https://github.com/username/repo"}),
            "live_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "https://example.com"}),
            "docs_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "https://docs.example.com"}),
            "start_date": forms.DateInput(attrs={"class": BASE_INPUT_CLASSES, "type": "date"}),
            "target_launch_date": forms.DateInput(attrs={"class": BASE_INPUT_CLASSES, "type": "date"}),
        }


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "difficulty",
            "github_issue_url",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "Enter feature title"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4, "placeholder": "Describe this feature in detail..."}),
            "status": forms.Select(attrs={"class": SELECT_CLASSES}),
            "priority": forms.Select(attrs={"class": SELECT_CLASSES}),
            "difficulty": forms.Select(attrs={"class": SELECT_CLASSES}),
            "github_issue_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "https://github.com/owner/repo/issues/123"}),
        }


class TechnologyForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = ["name", "tech_type", "website_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "Django, React, Stripe, etc."}),
            "tech_type": forms.Select(attrs={"class": SELECT_CLASSES}),
            "website_url": forms.URLInput(attrs={"class": BASE_INPUT_CLASSES, "placeholder": "https://example.com"}),
        }


class ProjectTechnologyForm(forms.ModelForm):
    class Meta:
        model = ProjectTechnology
        fields = ["technology", "notes"]
        widgets = {
            "technology": forms.Select(attrs={"class": SELECT_CLASSES}),
            "notes": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 3, "placeholder": "How is this used in the project?"}),
        }