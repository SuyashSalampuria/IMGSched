from django.shortcuts import render, redirect
from rest_framework import permissions, status
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from .serializers import MeetingSerializer, CommentSerializer
from .forms import UserRegisterForm, meetingForm
from .models import meeting, comment, participant
from django.contrib.auth.models import User
import requests
from schedule.permissions import show_meeting, add_invite

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("<h1>Your form was saved</h1>")
            
    form = UserRegisterForm()
    return render(request, 'schedule/register.html',{'form':form})

@csrf_exempt
@login_required
def newMeeting(request):
        if request.method == 'POST':
                form1=meetingForm(request.POST)
                form1.instance.creator = request.user
                if form1.is_valid():
                        form1.save()
                        return redirect('/meeting/')
                else:
                        return HttpResponse("fill form correctly")
        else:
                form = meetingForm()
                return render(request, 'schedule/new.html',{'form':form})
    
@login_required
def allMeeting(request):
        
        meetings1 = meeting.objects.order_by('time_created')[:5]
        meetings2 = []
        for meet in meetings1:
                if show_meeting(request,meet):
                        meetings2.append(meet)
        return render(request, 'schedule/all.html', {'meetings': meetings2, 'request':request})

@login_required
def detailed_Meeting(request, meeting_id):
        invited=[]
        to_invite=[] 
        meet=meeting.objects.get(pk=meeting_id)
        to_invite=User.objects.order_by('id')[:5]
        spec_users = participant.objects.filter(meeting_id=meeting_id)
        for spec_user in spec_users:
        
                        invited.append(User.objects.get(pk=spec_user.user_id))
                        to_invite.filter(pk=spec_user.user_id).delete()
                
        if show_meeting(request, meet):
                return render(request, 'schedule/details.html',{'meet':meet,'invited':invited, 'to_invite':to_invite}) 
        else:
                return HttpResponse("Not accecible to you")
                
@login_required
def addPartcipant(request, meeting_id, user_id):
        
        meet=meeting.objects.get(pk=meeting_id)
        user1=User.objects.get(pk=user_id)
        if add_invite(request, meet, user1):
                
                p1=participant(meeting=meet , user=user1)
                p1.save()
        return redirect("/meeting/")
         