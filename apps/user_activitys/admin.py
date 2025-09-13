from django.contrib import admin
from .models import UserActivity, Badge, UserNotifications

admin.site.register(UserActivity)
admin.site.register(Badge)
admin.site.register(UserNotifications)
