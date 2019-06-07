from django.contrib import admin
from .models import meeting, comment,participant
# Register your models here.
admin.site.register(meeting)
admin.site.register(participant)
admin.site.register(comment)
