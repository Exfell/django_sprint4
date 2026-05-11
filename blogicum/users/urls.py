from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('<slug:username>/', views.ProfileView.as_view(), name='profile'),
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
]