from django.urls import path
from . import views

urlpatterns = [
    path('', views.role, name='role'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('experts/', views.experts, name='experts'),
]
