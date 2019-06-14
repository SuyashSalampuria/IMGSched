from __future__ import print_function
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
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

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
        to_invite = list(set(to_invite) - set(invited))
        
        # if request.method == 'POST':
                
        #         Commen=request.POST['com']
        #         c1=comment(user=request.user, meeting=meet, Comment=Commen)
        #         c1.save()
        comments1=comment.objects.filter(meeting=meet)
        if show_meeting(request, meet):
                return render(request, 'schedule/details.html',{'meet':meet,'invited':invited, 'to_invite':to_invite,'comments':comments1, 'users':User, 'room_name_json': mark_safe(json.dumps(meeting_id))}) 
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

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

         