from django.urls import path
from . import views

urlpatterns = [
    path("", views.role_select, name="role"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home, name="home"),
    path("lawyer/dashboard/", views.lawyer_dashboard, name="lawyer_dashboard"),
    path("experts/", views.experts, name="experts"),
]
