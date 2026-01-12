from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, LawyerProfile, Wallet


# =========================
# ROLE SELECTION
# =========================
def role_select(request):
    return render(request, "accounts/role.html")


# =========================
# SIGNUP (CLIENT + LAWYER)
# =========================
def signup_view(request):
    role = request.GET.get("role")

    if role not in ["client", "lawyer"]:
        return redirect("role")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        name = request.POST.get("name")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect(request.path + f"?role={role}")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role=role,
        )

        # Wallet for both
        Wallet.objects.create(user=user)

        # Extra fields only for lawyer
        if role == "lawyer":
            LawyerProfile.objects.create(
                user=user,
                bar_council_id=request.POST.get("bar_id", ""),
                experience_years=request.POST.get("experience", 0),
                is_available=True,
            )

        login(request, user)

        return redirect(
            "lawyer_dashboard" if role == "lawyer" else "home"
        )

    return render(
        request,
        "accounts/common/signup.html",
        {"role": role}
    )


# =========================
# LOGIN
# =========================
def login_view(request):
    role = request.GET.get("role")

    if role not in ["client", "lawyer"]:
        return redirect("role")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user and user.role == role:
            login(request, user)
            return redirect(
                "lawyer_dashboard" if role == "lawyer" else "home"
            )

        messages.error(request, "Invalid credentials")

    return render(
        request,
        "accounts/common/login.html",
        {"role": role}
    )


# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect("role")


# =========================
# CLIENT HOME
# =========================
@login_required
def home(request):
    if request.user.role != "client":
        return redirect("lawyer_dashboard")

    return render(request, "accounts/client/home.html")


# =========================
# SERVICES (CLIENT)
# =========================
@login_required
def services(request):
    return render(request, "accounts/client/services.html")


# =========================
# EXPERTS (CLIENT)
# =========================
@login_required
def experts(request):
    lawyers = LawyerProfile.objects.filter(is_available=True)
    return render(
        request,
        "accounts/client/experts.html",
        {"lawyers": lawyers}
    )


# =========================
# LAWYER DASHBOARD
# =========================
@login_required
def lawyer_dashboard(request):
    if request.user.role != "lawyer":
        return redirect("home")

    profile = LawyerProfile.objects.get(user=request.user)

    context = {
        "profile": profile,
        "today_earnings": 12480,      # dummy
        "total_consultations": 18,    # dummy
        "average_rating": 4.9,        # dummy
        "requests": [],               # will add later
    }

    return render(
        request,
        "accounts/lawyer/lawyer_dashboard.html",
        context
    )


# =========================
# LAWYER CONSULTATIONS
# =========================
@login_required
def consultations(request):
    return render(request, "accounts/lawyer/consultations.html")


# =========================
# LAWYER EARNINGS
# =========================
@login_required
def lawyer_earnings(request):
    return render(request, "accounts/lawyer/earnings.html")


# =========================
# LAWYER PROFILE
# =========================
@login_required
def lawyer_profile(request):
    profile = LawyerProfile.objects.get(user=request.user)
    return render(
        request,
        "accounts/lawyer/profile.html",
        {"profile": profile}
    )
