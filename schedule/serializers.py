from rest_framework import serializers
from .models import comment, meeting, participant
from django.contrib.auth.models import User

class MeetingSerializer(serializers.ModelSerializer):
	class Meta:
		model = meeting
		fields = ('creator', 'time_created', 'purpose', 'private', 'venue', 'participants','meet_time')

class CommentSerializer(serializers.ModelSerializer):
	class Meta:		
		model = comment
		fields = ('user', 'meeting', 'time', 'Comment')
