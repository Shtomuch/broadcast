from django.urls import path
from .views import (
    UserSignUpView, UserLoginView,
    UserLogoutView, ProfileView,
)

app_name = 'users'

urlpatterns = [
    path('signup/', UserSignUpView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
