from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
from . import models

# Register your models here.


@admin.register(models.CustomUser)
class UserAdmin(BaseUserAdmin):
    list_display = ['username',
                    'email', 'first_name', 'last_name',  'user_role']
    list_editable = ['email', 'user_role']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name',
                       'user_role')
        }),
    )

@admin.register(models.UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'home_access', 'config_access', 'advance_control']


@admin.register(models.TRFProject)
class TRFProjectAdmin(admin.ModelAdmin):
    list_display = ['project_version', 'sensor_task_id']



@admin.register(models.SensorPlace)
class SensorPlaceAdmin(admin.ModelAdmin):
    
    list_display = ['device_id', 'pin_num','section']


@admin.register(models.TRFParam)
class TRFParamAdmin(admin.ModelAdmin):
    list_display = ['param_name', 'param_id', 'is_advance','default_value','is_settable','detail']


@admin.register(models.TRFUserConfig)
class TRFUserConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'parameter_id', "command_type","value"]


@admin.register(models.GeneralError)
class GeneralErrorAdmin(admin.ModelAdmin):
    list_display = ['time', 'error']

