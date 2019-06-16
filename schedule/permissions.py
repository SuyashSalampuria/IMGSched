from rest_framework import permissions
from .models import meeting, comment, participant
from django.contrib.auth.models import User

def show_meeting(request,  meeting_obj):
    if meeting_obj.private==False:
        return True
    if meeting_obj.creator == request.user:
        return True
    elif request.user.is_staff:
        return True
    else:
        spec_users = participant.objects.filter(meeting=meeting_obj)
        for spec_user in spec_users:
            if spec_user == request.user:
                return True
    return False

def add_invite(request, meeting_obj, user_obj):
    spec_users = participant.objects.filter(meeting=meeting_obj) #if user was already invited return false
    for spec_user in spec_users:
        if User.objects.get(pk=spec_user.user_id) == user_obj:
            return False

    if meeting_obj.creator == request.user:
        return True
    elif request.user.is_staff:
        return True
    else:
        return False