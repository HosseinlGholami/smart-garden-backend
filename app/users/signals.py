from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
 
# This file can be used to handle post-save actions
# For example, creating a user profile when a user is created 