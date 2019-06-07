from django.urls import path, include
from . import views
urlpatterns=[
    path('<int:meeting_id>/add/<int:user_id>/',views.addPartcipant),
    
    path('<int:meeting_id>/',views.detailed_Meeting),
    
    path('new/',views.newMeeting),
    path('',views.allMeeting),
]