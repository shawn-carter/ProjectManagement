from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin
from safedelete.models import SafeDeleteModel, SafeDeleteManager
from django.db import models as django_models  # Correctly import Django model fields
from .models import Project, Task, Asset, Category, TaskStatus, ProjectStatus, Skill, Team, DayOfWeek

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


class AssetAdmin(SafeDeleteAdminExtended):
    list_display = ('name', 'email', 'normal_work_week', 'deleted')  # Display work_days
    list_filter = ('skills', 'teams', 'work_days')  # Add work_days to the list_filter

# Register the models using SafeDeleteAdminExtended and automatically show all fields
#admin.site.register(Project, SafeDeleteAdminExtended)
#admin.site.register(Task, SafeDeleteAdminExtended)
admin.site.register(Asset, AssetAdmin)
#admin.site.register(Category, SafeDeleteAdminExtended)
#admin.site.register(TaskStatus, SafeDeleteAdminExtended)
#admin.site.register(ProjectStatus, SafeDeleteAdminExtended)
admin.site.register(Skill, SafeDeleteAdminExtended)
admin.site.register(Team, SafeDeleteAdminExtended)

#admin.site.register(DayOfWeek, SafeDeleteAdminExtended)  # Register DayOfWeek model

