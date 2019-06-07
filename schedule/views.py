from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from .serializers import MeetingSerializer, CommentSerializer
from .forms import UserRegisterForm, meetingForm
from .models import meeting, comment, participant
from django.contrib.auth.models import User
import requests

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
def newMeeting(request):
        if request.method == 'POST':
                form1=meetingForm(request.POST)
                form1.instance.creator = request.user
                if form1.is_valid():
                        form1.save()
                        return redirect('meeting/')
                else:
                        return HttpResponse("meeting/new")
        else:
                form = meetingForm()
                return render(request, 'schedule/new.html',{'form':form})
    
@login_required
def allMeeting(request):
        meetings = meeting.objects.order_by('time_created')[:5]
        context = {'meetings': meetings}
        return render(request, 'schedule/all.html', context)

def detailed_Meeting(request, meeting_id):
        
        try:
                meet=meeting.objects.get(pk=meeting_id)
                users1=User.objects.all()
        except meeting.DoesNotExist:
                raise Http404("Meeting does not exist")

        return render(request, 'schedule/details.html',{'meet':meet,'users1':users1}) 

@login_required
def addPartcipant(request, meeting_id, user_id):
        
        meet=meeting.objects.get(pk=meeting_id)
        user1=User.objects.get(pk=user_id)
        p1=participant(meeting=meet , user=user1)
        p1.save()
        return redirect("/meeting/")
         