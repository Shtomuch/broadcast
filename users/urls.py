from django import views
from django.urls import path
from .views import (
    UserSignUpView, UserLoginView,
    UserLogoutView, ProfileView,
)
from django.urls import path
from . import views
app_name = 'users'

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),  # Новий шлях

]
