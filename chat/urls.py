from django.urls import path
from .views import (
    RoomListView, RoomCreateView, RoomJoinView, LeaveRoomView,
    RoomPasswordView, RoomDeleteView, FileUploadView,
)

app_name = "chat"



urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="rooms"),
    path("rooms/new/", RoomCreateView.as_view(), name="create"),
    path("r/<slug:slug>/", RoomJoinView.as_view(), name="join"),
    path("r/<slug:slug>/leave/", LeaveRoomView.as_view(), name="leave"),
    path("r/<slug:slug>/upload/", FileUploadView.as_view(), name="upload"),
    path("r/<slug:slug>/pwd/", RoomPasswordView.as_view(), name="pwd_prompt"),
    path("r/<slug:slug>/delete/", RoomDeleteView.as_view(), name="delete"),

]
