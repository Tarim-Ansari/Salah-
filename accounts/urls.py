from django.urls import path
from . import views

urlpatterns = [
    path("", views.role_select, name="role"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("home/", views.home, name="home"),
    path("lawyer_dashboard/", views.lawyer_dashboard, name="lawyer_dashboard"),
    path("consultations/",views.consultations,name="lawyer_consultations"),
    path("profile/",views.lawyer_profile,name="lawyer_profile"),
    path("earnings/",views.lawyer_earnings,name="lawyer_earnings"),
    path("services/", views.services, name="services"),
    path("experts/", views.experts, name="experts"),
    path("logout/", views.logout_view, name="logout"),
    path(
        "request-consultation/<int:lawyer_id>/",
        views.request_consultation,
        name="request_consultation",
    ),
    path(
        "lawyer/consultations/",
        views.lawyer_consultations,
        name="lawyer_consultations",
    ),




    # path("experts/", views.experts, name="experts"),
]
