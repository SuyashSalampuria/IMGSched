from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class meeting(models.Model):
    creator = models.ForeignKey('auth.User',related_name='creator', on_delete=models.CASCADE)
    time_created = models.DateTimeField(default=timezone.now)
    purpose = models.CharField(max_length=255)
    venue= models.CharField(max_length=255)
    private=models.BooleanField(default=True)
    participants=models.ManyToManyField(User, related_name='participants', through='participant')
    meet_time= models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.purpose


class participant(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    meeting=models.ForeignKey(meeting,on_delete=models.CASCADE)
    joined=models.BooleanField(default=False)

class comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.PROTECT, default=0)
    meeting=models.ForeignKey(meeting, on_delete=models.CASCADE)
    time=models.DateTimeField(default=timezone.now)
    Comment=models.TextField()
    def __str__(self):
        return self.Comment