from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("dashboard/", views.project_dashboard, name="project_dashboard"),
    path("create/", views.project_create, name="project_create"),
    path("technologies/create/", views.technology_create, name="technology_create"),
    
    path("<int:project_pk>/features/<int:feature_pk>/edit/",views.feature_update,name="feature_update",),
    path("<int:project_pk>/features/<int:feature_pk>/delete/",views.feature_delete,name="feature_delete",),
    path("<int:project_pk>/features/<int:feature_pk>/done/",views.feature_mark_done,name="feature_mark_done",),

    path("<int:project_pk>/technologies/<int:project_technology_pk>/edit/",views.project_technology_update,name="project_technology_update",),
    path("<int:project_pk>/technologies/<int:project_technology_pk>/delete/",views.project_technology_delete,name="project_technology_delete",),

    path("<int:pk>/", views.project_detail, name="project_detail"),
    path("<int:pk>/edit/", views.project_update, name="project_update"),

    path("<int:project_pk>/features/create/", views.feature_create, name="feature_create"),
    path("<int:project_pk>/technologies/add/", views.project_technology_create, name="project_technology_create"),

    path("<int:pk>/archive/", views.project_archive, name="project_archive"),
    path("<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("<int:pk>/restore/", views.project_restore, name="project_restore"),
    path("<int:project_pk>/features/<int:feature_pk>/status/",views.feature_update_status,name="feature_update_status",),
    path("<int:pk>/github/sync-issues/", views.project_sync_github_issues, name="project_sync_github_issues"),

    path("<int:pk>/kanban/", views.project_kanban, name="project_kanban"),
    path("<int:project_pk>/features/<int:feature_pk>/status/",views.feature_update_status,name="feature_update_status",),
    path("<int:project_pk>/features/reorder/",views.feature_reorder,name="feature_reorder",),
    path("<int:project_pk>/features/quick-create/",views.feature_quick_create,name="feature_quick_create",),
]