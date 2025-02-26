# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum


class UserRole(models.Model):
    name = models.CharField(max_length=255, unique=True)
    home_access = models.BooleanField(default=True, null=False)
    config_access = models.BooleanField(default=True, null=False)
    advance_control = models.BooleanField(default=True)  # Fixed typo

    def __str__(self) -> str:
        return self.name

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    user_role = models.ForeignKey(
        UserRole, on_delete=models.PROTECT, null=True, blank=True)  # Added blank=True for optional values


class TRFProject(models.Model):
    project_version = models.CharField(max_length=36, default="V.1")
    sensor_task_id = models.CharField(max_length=36)


    def __str__(self) -> str:
        return self.project_version


class TRFParam(models.Model):
    param_name = models.CharField(max_length=255)
    param_id = models.PositiveIntegerField(null=True, default=1)  # Fixed default value type
    is_advance = models.BooleanField(default=True, null=False)
    default_value = models.CharField(max_length=255, default='1')  # Add this field
    is_settable = models.BooleanField(default=True)  # Add this field
    detail = models.TextField(default='')  # Add this field
    
    def __str__(self) -> str:
        return self.param_name

class SensorPlace(models.Model):
    device_id = models.CharField(max_length=255,default="def")
    pin_num = models.ForeignKey(
        TRFParam, on_delete=models.PROTECT, null=True)
    section = models.CharField(max_length=255,default="def")
    def __str__(self) -> str:
        return f"{self.section}"

class TRFUserConfig(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    device_id = models.CharField(max_length=255)
    parameter_id = models.CharField(max_length=255)
    command_type = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.device_id}-{self.parameter_id}"


class GeneralError(models.Model):
    time = models.DateTimeField(auto_now=True)
    error = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.error

    class Meta:
        ordering = ["time"]


# def raise_error_and_save_on_db(txt):
#     err = GeneralError()
#     err.error = txt[:255]
#     err.save()
#     raise ValueError(txt)

def raise_error_and_save_on_db(txt):
    print(f"txt: {txt}, type:{type(txt)}")
    text = str(txt)
    try:
        err = GeneralError()
        err.error = text[:255]
        err.save()
    except Exception as e:
        # Log the exception or print it out
        print(f"Failed to save error to the database: {e}")
        raise e  # Optionally re-raise the original exception
    raise ValueError(txt)
