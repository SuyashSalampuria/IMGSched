from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
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
from schedule.permissions import show_meeting, add_invite, show_invite_list
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json
import datetime
from datetime import datetime
from datetime import timedelta

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
                        meet_time=request.POST.get("meet_time")
                       
                        meet_time=meet_time.replace(" ","T")
                       
                        
                        
                        service = build_service()
                        event = {
                          'summary': request.POST.get("purpose"),
                          'location': request.POST.get("venue"),
                          'start': {
                            'dateTime': meet_time,
                            'timeZone': 'Asia/Kolkata',
                            
                          },
                          'end': {
                            'dateTime': meet_time,
                            'timeZone': 'Asia/Kolkata',
                            
                          },
                          
                          'reminders': {
                            'useDefault': False,
                            'overrides': [
                              {'method': 'email', 'minutes': 24 * 60},
                              {'method': 'popup', 'minutes': 10},
                            ],
                          },
                        }

                        event = service.events().insert(calendarId='primary', body=event).execute()
                        



                        return redirect('/meeting/')
                else:
                        return HttpResponse("fill form correctly")
        else:
                form = meetingForm()
                return render(request, 'schedule/new.html',{'form':form})
    
@login_required
def allMeeting(request):
        
        meetings1 = meeting.objects.order_by('time_created')
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
        to_invite=User.objects.order_by('id')
        spec_users = participant.objects.filter(meeting_id=meeting_id)
        for spec_user in spec_users:
        
                        invited.append(User.objects.get(pk=spec_user.user_id))
        to_invite = list(set(to_invite) - set(invited))
        if show_invite_list(request, meet) != True:
                to_invite=[]
        
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

@login_required
def delete_meeting(request, meeting_id):
        meet=meeting.objects.get(pk=meeting_id)
        if show_invite_list(request, meet ):
                meet.delete()
                return redirect("/meeting/")
        else:
                return HttpResponse("This meeting cant be deleted")

@login_required
def update_meeting(request, meeting_id):
        meet=meeting.objects.get(pk=meeting_id)
        
        now=meet.meet_time
        now=now-timedelta(hours=10)    
        now1 = now.strftime("%Y-%m-%d (%H:%M:%S.%f)")
        
        now1=now1[0:10]+"T"+now1[12:26]+'Z'
        print(now1)
        
        if request.method=='POST':
                service=build_service()
                events_result = service.events().list(calendarId='primary', timeMin=now1,
                                        maxResults=1, singleEvents=True,
                                        orderBy='startTime').execute()
                events = events_result.get('items', [])
                if not events:
                        print('No upcoming events found.')
                for event in events:
                        print(type(event))
                        print(event['summary'])
                        meet.purpose=request.POST.get("purpose")
                        meet.venue=request.POST.get("venue")
                        meet.meet_time = request.POST.get("meet_time")
                        meet.private = request.POST.get("private")
                        meet.save()
                        id1=event['id']
                        event['summary'] = meet.purpose
                        event['location'] = meet.venue
                        time1=meet.meet_time
                        event['start']['datetime'] = time1
                        event['end']['datetime'] = time1
                        updated_event = service.events().update(calendarId='primary', eventId=id1, body=event).execute()
                        print(updated_event['updated'])
                return redirect("/meeting/")


        return render(request, 'schedule/update.html',{'meeting':meet})

def build_service():
        creds=None
        if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
        if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                                'credentials.json', SCOPES)
                        creds = flow.run_local_server()
        
                with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service