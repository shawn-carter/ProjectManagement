from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from safedelete.models import SafeDeleteModel, SafeDeleteManager
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Project, Task, Asset, Category, TaskStatus, ProjectStatus,
    Skill, Team, DayOfWeek, Risk, Assumption, Issue,
    Dependency, Stakeholder, Comment
)

# Extended SafeDeleteAdmin model to include undelete functionality for all models
class SafeDeleteAdminExtended(SafeDeleteAdmin):
    actions = ['undelete_selected']

    def undelete_selected(self, request, queryset):
        for obj in queryset:
            obj.undelete()
        self.message_user(request, "Successfully undeleted selected records.")

    undelete_selected.short_description = "Undelete selected records"

    def get_list_display(self, request):
        # Dynamically get all fields for the model
        fields = [field.name for field in self.model._meta.fields]

        # Remove default fields if present in the list
        if 'id' in fields:
            fields.remove('id')

        # Define the preferred order of fields
        preferred_order = ['team_name', 'name']  # Add any field that you want to appear first
        ending_fields = ['deleted', 'deleted_by_cascade']

        # Create a new field order based on the preferred order and ending fields
        ordered_fields = [field for field in preferred_order if field in fields]
        middle_fields = [field for field in fields if field not in ordered_fields + ending_fields]
        final_order = ordered_fields + middle_fields + ending_fields

        return final_order

    # Add custom button to change form view to undelete an item
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        # Add a flag to determine if the object is deleted
        extra_context['show_undelete_button'] = self.get_object(request, object_id).deleted is not None
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/undelete/', self.admin_site.admin_view(self.undelete_view), name='model-undelete')
        ]
        return custom_urls + urls

    def undelete_view(self, request, object_id):
        obj = self.get_object(request, object_id)
        if obj:
            obj.undelete()
            self.message_user(request, f"{obj} has been undeleted successfully.")
        return self.response_post_save_change(request, obj)

# Custom admin classes for each model

class AssetAdmin(SafeDeleteAdminExtended):
    list_display = ('asset_id', 'name', 'email', 'normal_work_week', 'deleted')
    list_filter = ('skills', 'teams', 'work_days', 'deleted')

class SkillAdmin(SafeDeleteAdminExtended):
    list_display = ('skill_id', 'skill_name', 'deleted')
    list_filter = ('deleted',)

class TeamAdmin(SafeDeleteAdminExtended):
    list_display = ('team_id', 'team_name', 'deleted')
    list_filter = ('deleted',)

class CategoryAdmin(SafeDeleteAdminExtended):
    list_display = ('category_id', 'category_name', 'deleted')
    list_filter = ('deleted',)

class TaskStatusAdmin(SafeDeleteAdminExtended):
    list_display = ('status_id', 'status_name', 'description', 'deleted')
    list_filter = ('deleted',)

class ProjectStatusAdmin(SafeDeleteAdminExtended):
    list_display = ('status_id', 'status_name', 'description', 'deleted')
    list_filter = ('deleted',)

class DayOfWeekAdmin(SafeDeleteAdminExtended):
    list_display = ('day_name', 'abbreviation', 'deleted')
    list_filter = ('deleted',)

class CommentAdmin(SafeDeleteAdminExtended):
    list_display = ('user', 'get_content_object', 'comment_text', 'created_datetime', 'deleted')
    list_filter = ('user', 'content_type', 'deleted')

    def get_content_object(self, obj):
        return obj.content_object
    get_content_object.short_description = 'Content Object'

# Existing admin classes for other models

class ProjectAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'project_name', 'project_status', 'created_datetime', 'deleted')
    list_filter = ('project_status', 'deleted')
    actions = ['undelete_selected']

admin.site.register(Project, ProjectAdmin)

class TaskAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'task_name', 'get_project_name', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'project__category', 'deleted')
    actions = ['undelete_selected', highlight_deleted]

    def get_project_name(self, obj):
        return obj.project.project_name

    def get_queryset(self, request):
        # Use the all_objects manager to include soft-deleted objects
        qs = self.model.all_objects.all()
        # Apply default ordering if necessary
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Task, TaskAdmin)

class RiskAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'risk_details', 'get_project_name', 'created_by', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'deleted')
    actions = ['undelete_selected']

    def get_project_name(self, obj):
        return obj.project.project_name

admin.site.register(Risk, RiskAdmin)

class AssumptionAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'assumption_details', 'get_project_name', 'created_by', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'deleted')
    actions = ['undelete_selected']

    def get_project_name(self, obj):
        return obj.project.project_name

admin.site.register(Assumption, AssumptionAdmin)

class IssueAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'issue_details', 'get_project_name', 'created_by', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'deleted')
    actions = ['undelete_selected']

    def get_project_name(self, obj):
        return obj.project.project_name

admin.site.register(Issue, IssueAdmin)

class DependencyAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('id', 'dependency_details', 'get_project_name', 'created_by', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'deleted')
    actions = ['undelete_selected']

    def get_project_name(self, obj):
        return obj.project.project_name

admin.site.register(Dependency, DependencyAdmin)

class StakeholderAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    list_display = ('stakeholder_id', 'name', 'get_project_name', 'created_by', 'created_datetime', 'deleted')
    list_filter = ('project__project_status', 'deleted')
    actions = ['undelete_selected']

    def get_project_name(self, obj):
        return obj.project.project_name

admin.site.register(Stakeholder, StakeholderAdmin)

# Register the custom admin classes with the models

admin.site.register(Asset, AssetAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(TaskStatus, TaskStatusAdmin)
admin.site.register(ProjectStatus, ProjectStatusAdmin)
admin.site.register(DayOfWeek, DayOfWeekAdmin)
admin.site.register(Comment, CommentAdmin)
