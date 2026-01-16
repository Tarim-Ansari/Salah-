from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal 

from .models import (
    User,
    LawyerProfile,
    Wallet,
    ConsultationRequest,
    ServiceCategory,
    Transaction, # Added this import
)

User = get_user_model()

# =========================
# ROLE SELECTION
# =========================
def role_select(request):
    return render(request, "accounts/role.html")

# =========================
# SIGNUP
# =========================
def signup_view(request):
    role = request.GET.get("role")
    if request.method == "POST":
        role = request.POST.get("role")
        full_name = request.POST.get("name").strip()
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect(f"/signup/?role={role}")

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name, role=role,
        )

        if role == "lawyer":
            LawyerProfile.objects.create(
                user=user, experience_years=0,
                bar_council_id=request.POST.get("bar_id") or None, is_available=True,
            )

        messages.success(request, "Account created successfully.")
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
        user = authenticate(request, username=email, password=password)

        if user and user.role == role:
            login(request, user)
            return redirect("lawyer_dashboard" if role == "lawyer" else "home")

        messages.error(request, "Invalid credentials")
    return render(request, "accounts/common/login.html", {"role": role})

# =========================
# LOGOUT
# =========================
@login_required
def logout_view(request):
    logout(request)
    return redirect("role")

# =========================
# CLIENT VIEWS
# =========================
@login_required
def home(request):
    if request.user.role != "client":
        return redirect("lawyer_dashboard")
    return render(request, "accounts/client/home.html")

@login_required
def services(request):
    return render(request, "accounts/client/services.html")

@login_required
def experts(request):
    lawyers = LawyerProfile.objects.filter(is_available=True)
    return render(request, "accounts/client/experts.html", {"lawyers": lawyers})

@login_required
def request_consultation(request, lawyer_id):
    lawyer_profile = get_object_or_404(LawyerProfile, id=lawyer_id)
    categories = ServiceCategory.objects.all()

    if request.method == "POST":
        category_id = request.POST.get("category")
        subject = request.POST.get("subject")
        description = request.POST.get("description")
        category = get_object_or_404(ServiceCategory, id=category_id)

        ConsultationRequest.objects.create(
            client=request.user, lawyer=lawyer_profile.user,
            category=category, subject=subject, description=description,
        )
        return redirect("client_consultations")

    return render(request, "accounts/client/case_brief.html", {
        "lawyer": lawyer_profile, "categories": categories,
    })

@login_required
def client_consultations(request):
    requests = ConsultationRequest.objects.filter(client=request.user).order_by("-created_at")
    return render(request, "accounts/client/client_consultations.html", {"requests": requests})

# =========================
# LAWYER VIEWS
# =========================
@login_required
def lawyer_dashboard(request):
    if request.user.role != "lawyer":
        return redirect("home")
    profile = get_object_or_404(LawyerProfile, user=request.user)
    return render(request, "accounts/lawyer/lawyer_dashboard.html", {
        "profile": profile, "today_earnings": 0,
        "total_consultations": ConsultationRequest.objects.filter(lawyer=request.user, status="accepted").count(),
        "average_rating": 0,
    })

@login_required
def lawyer_consultations(request):
    requests = ConsultationRequest.objects.filter(lawyer=request.user).order_by("-created_at")
    return render(request, "accounts/lawyer/consultations.html", {"requests": requests})

@login_required
def update_consultation_status(request, request_id, action):
    consultation = get_object_or_404(ConsultationRequest, id=request_id, lawyer=request.user)
    if consultation.status != "pending":
        return redirect("lawyer_consultations")
    
    if action == "accept":
        consultation.status = "accepted"
        consultation.save()
    elif action == "reject":
        consultation.status = "rejected"
        consultation.save()
    return redirect("lawyer_consultations")

@login_required
def lawyer_profile(request):
    profile = get_object_or_404(LawyerProfile, user=request.user)
    if request.method == "POST":
        if request.FILES.get("profile_photo"):
            profile.profile_photo = request.FILES["profile_photo"]
        profile.experience_years = request.POST.get("experience_years", 0)
        profile.save()
        return redirect("lawyer_profile")
    return render(request, "accounts/lawyer/profile.html", {"profile": profile})

@login_required
def lawyer_earnings(request):
    return render(request, "accounts/lawyer/earnings.html")

# =========================
# WALLET VIEWS (Added)
# =========================
@login_required
def wallet_view(request):
    # Ensure wallet exists
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')
    return render(request, "accounts/wallet.html", {
        "wallet": wallet, "transactions": transactions
    })

@login_required
def add_funds(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount = float(amount)
            if amount > 0:
                request.user.wallet.credit(amount, description="Added funds via Bank")
                messages.success(request, f"Successfully added ₹{amount}")
            else:
                messages.error(request, "Enter a valid amount")
        except ValueError:
            messages.error(request, "Invalid input")
    return redirect("wallet")

# =========================
# ADD FUNDS (FIXED)
# =========================
@login_required
def add_funds(request):
    if request.method == "POST":
        amount_str = request.POST.get("amount")
        try:
            # 2. CHANGE THIS LINE: Use Decimal() instead of float()
            amount = Decimal(amount_str)
            
            if amount > 0:
                request.user.wallet.credit(amount, description="Added funds via Bank")
                messages.success(request, f"Successfully added ₹{amount}")
            else:
                messages.error(request, "Enter a valid amount")
        except:
            # This catches both ValueError and Decimal's InvalidOperation
            messages.error(request, "Invalid input")
    
    return redirect("wallet")