from django.urls import path

from users.views import (EmailVerificationView, LoginUserView, ProfileView,
                         RegisterUserView, logoutuser)

app_name = 'users'

urlpatterns = [
    path('login/', LoginUserView.as_view(), name='login'),
    path('registration/', RegisterUserView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('logout/', logoutuser, name='logout'),
    path('verify/<str:email>/<uuid:code>/', EmailVerificationView.as_view(), name='email_verification'),
]
