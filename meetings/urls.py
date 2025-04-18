
from django.urls import path
from .views import (
    MeetingListView, MeetingCreateView,
    MeetingDetailView, MeetingJoinView
)

app_name = 'meetings'

urlpatterns = [
    path('', MeetingListView.as_view(), name='list'),
    path('create/', MeetingCreateView.as_view(), name='create'),
    path('<slug:slug>/', MeetingDetailView.as_view(), name='detail'),
    path('<slug:slug>/join/', MeetingJoinView.as_view(), name='join'),
]
