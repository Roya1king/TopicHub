from django.contrib import admin

# Register your models here.

from .models import Profile, Room,Topic,Message
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Profile)