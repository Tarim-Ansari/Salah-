from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    User,
    LawyerProfile,
    Wallet,
    ConsultationRequest,
    ServiceCategory,
)



# -------------------------
# ROLE SELECT
# -------------------------
def role_select(request):
    if request.method == "POST":
        request.session["role"] = request.POST.get("role")
        return redirect("signup")
    return render(request, "accounts/role.html")


# -------------------------
# SIGNUP
# -------------------------
def signup_view(request):
    role = request.session.get("role")
    if not role:
        return redirect("role")

    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST["email"],
            email=request.POST["email"],
            password=request.POST["password"],
            role=role,
        )

        Wallet.objects.create(user=user)

        if role == "lawyer":
            profile = LawyerProfile.objects.create(
                user=user,
                experience_years=request.POST.get("experience", 0),
                bar_council_id=request.POST.get("bar_id", ""),
            )
            categories = request.POST.getlist("specialization")
            profile.specialization.set(ServiceCategory.objects.filter(id__in=categories))

        login(request, user)
        return redirect("home")

    return render(request, "accounts/signup.html")


# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["email"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return redirect("lawyer_dashboard" if user.role == "lawyer" else "home")
        messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")


# -------------------------
# CLIENT HOME
# -------------------------
@login_required
def home(request):
    return render(request, "accounts/home.html")


# -------------------------
# LAWYER DASHBOARD
# -------------------------
@login_required
def lawyer_dashboard(request):
    profile = LawyerProfile.objects.get(user=request.user)
    requests = ConsultationRequest.objects.filter(lawyer=request.user)
    return render(request, "accounts/lawyer_dashboard.html", {
        "profile": profile,
        "requests": requests,
    })


# -------------------------
# EXPERT LIST
# -------------------------
@login_required
def experts(request):
    lawyers = LawyerProfile.objects.filter(is_verified=True, is_available=True)
    return render(request, "accounts/experts.html", {"lawyers": lawyers})
