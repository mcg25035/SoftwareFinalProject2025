from django.contrib import admin
from .models import AdministratorProfile, SystemLog


@admin.register(AdministratorProfile)
class AdministratorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'phone', 'created_at']
    search_fields = ['user__username', 'department']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'ip_address', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'model_name', 'description']
    readonly_fields = ['created_at']
