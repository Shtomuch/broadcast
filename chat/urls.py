from django.urls import path
from .views import RoomListView, RoomDetailView, upload_attachment

app_name = "chat"

urlpatterns = [
    path("rooms/", RoomListView.as_view(), name="rooms"),
    path("rooms/<slug:slug>/", RoomDetailView.as_view(), name="room_detail"),
    path("rooms/<slug:slug>/upload/", upload_attachment, name="upload_attachment"),
]
