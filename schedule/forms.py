from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import meeting,comment, participant
import datetime

class UserRegisterForm(UserCreationForm):
    email=forms.EmailField()
    first_name= forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    class Meta:
        model=User
        fields=['username','email','password1','password2','first_name','last_name']
        
class meetingForm(forms.ModelForm):
    purpose = forms.CharField(label='purpose', max_length=255)
    venue= forms.CharField(label='venue', max_length=255)
    meet_time= forms.DateTimeField(initial=datetime.date.today)
    private = forms.BooleanField(required=False)
    class Meta:
        model= meeting
        fields=['purpose','venue','meet_time','private']

