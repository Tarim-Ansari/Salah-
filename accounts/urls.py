from django.urls import path
from . import views

urlpatterns = [
    path("", views.role_select, name="role"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("home/", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("experts/", views.experts, name="experts"),

    path("lawyer_dashboard/", views.lawyer_dashboard, name="lawyer_dashboard"),
    path("lawyer/consultations/", views.lawyer_consultations, name="lawyer_consultations"),
    path("profile/", views.lawyer_profile, name="lawyer_profile"),
    path("earnings/", views.lawyer_earnings, name="lawyer_earnings"),

    path(
        "request-consultation/<int:lawyer_id>/",
        views.request_consultation,
        name="request_consultation",
    ),

    path(
        "client/consultations/",
        views.client_consultations,
        name="client_consultations",
    ),
    path(
        "consultation/<int:request_id>/<str:action>/",
        views.update_consultation_status,
        name="update_consultation_status",
    ),
    
    path("wallet/", views.wallet_view, name="wallet"),
    path("wallet/add/", views.add_funds, name="add_funds"),
    path("consultation/<str:room_id>/", views.join_room, name="join_room"),
]
