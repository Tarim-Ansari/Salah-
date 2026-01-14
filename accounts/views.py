from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, LawyerProfile, Wallet , ConsultationRequest , ServiceCategory

User = get_user_model()

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

    if request.method == "POST":
        role = request.POST.get("role")
        full_name = request.POST.get("name").strip()
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        # 🔒 Split full name safely
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        # ❗ Prevent duplicate email / username
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect(f"/signup/?role={role}")

        # ✅ Create user
        user = User.objects.create_user(
            username=request.POST["email"],   # keep email as username (good practice)
            email=request.POST["email"],
            password=request.POST["password"],
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        # ✅ Lawyer-specific profile
        if role == "lawyer":
            LawyerProfile.objects.create(
                user=user,
                experience_years=0,
                bar_council_id=request.POST.get("bar_id") or None,
                is_available=True,
            )

        messages.success(request, "Account created successfully. Please login.")
        return redirect(f"/login/?role={role}")

    return render(request, "accounts/common/signup.html", {"role": role})

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

    if request.method == "POST":
        if request.FILES.get("profile_photo"):
            profile.profile_photo = request.FILES["profile_photo"]

        profile.experience_years = request.POST.get("experience_years", 0)
        profile.save()

        return redirect("lawyer_profile")

    return render(request, "accounts/lawyer/profile.html", {
        "profile": profile
    })

@login_required
def request_consultation(request, lawyer_id):
    lawyer_profile = get_object_or_404(LawyerProfile, id=lawyer_id)
    lawyer_user = lawyer_profile.user

    categories = ServiceCategory.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        subject = request.POST.get("subject")
        description = request.POST.get("description")

        category = get_object_or_404(ServiceCategory, id=category_id)

        ConsultationRequest.objects.create(
            client=request.user,
            lawyer=lawyer_user,        # ✅ User, not LawyerProfile
            category=category,         # ✅ ServiceCategory instance
            subject=subject,
            description=description
        )

        return redirect("home")

    return render(
        request,
        "accounts/client/case_brief.html",
        {
            "lawyer": lawyer_profile,
            "categories": categories,
        }
    )



@login_required
def lawyer_consultations(request):
    requests = ConsultationRequest.objects.filter(
        lawyer=request.user
    ).order_by("-created_at")

    return render(
        request,
        "accounts/lawyer/consultations.html",
        {"requests": requests},
    )

