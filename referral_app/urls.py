from django.urls import path
from django.views.generic.base import RedirectView

from referral_app.views import AuthView, ProfileView, SetInvitationView, ListProfileView


app_name = 'referral_app'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='referral_app:login')),
    path('login', AuthView.as_view(), name='login'),
    path('profile', ProfileView.as_view()),
    path('profile/<int:pk>', ProfileView.as_view()),
    path('profile/invitation', SetInvitationView.as_view()),
    path('profiles', ListProfileView.as_view())
]