from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
import uuid  
import requests  
import time
from django.conf import settings 
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt    
from django.db.models import Sum, Avg
from django.utils import timezone

from .models import (
    User,
    LawyerProfile,
    Wallet,
    ConsultationRequest,
    ServiceCategory,
    Rating
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

    # 1. Requests Logic
    incoming_requests = ConsultationRequest.objects.filter(
        lawyer=request.user, 
        status="pending"
    ).order_by('-created_at')

    total_consultations = ConsultationRequest.objects.filter(
        lawyer=request.user, status="accepted"
    ).count()

    # 2. Earnings Logic
    today = timezone.now().date()
    earnings_data = ConsultationRequest.objects.filter(
        lawyer=request.user,
        status='completed',
        created_at__date=today
    ).aggregate(total=Sum('amount_paid'))
    today_earnings = earnings_data['total'] or 0

    # 3. RATING LOGIC (THE FIX)
    # We fetch all ratings for this lawyer and calculate the average
    ratings_data = Rating.objects.filter(lawyer=request.user).aggregate(avg=Avg('score'))
    average_rating = ratings_data['avg'] or 0.0

    return render(request, "accounts/lawyer/lawyer_dashboard.html", {
        "profile": profile,
        "today_earnings": today_earnings,
        "total_consultations": total_consultations,
        "average_rating": round(average_rating, 1), # <--- Pass the real number
        "incoming_requests": incoming_requests,
    })

@login_required
def lawyer_consultations(request):
    requests = ConsultationRequest.objects.filter(lawyer=request.user).order_by("-created_at")
    return render(request, "accounts/lawyer/consultations.html", {"requests": requests})

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
# UPDATE CONSULTATION (ACCEPT/REJECT + GENERATE ROOM ID)
# =========================
@login_required
def update_consultation_status(request, request_id, action):
    consultation = get_object_or_404(
        ConsultationRequest,
        id=request_id,
        lawyer=request.user
    )

    if consultation.status != "pending":
        return redirect("lawyer_dashboard")

    if action == "accept":
        consultation.status = "accepted"
        # Generate Unique Room ID
        consultation.room_id = f"consultation-{str(uuid.uuid4())[:8]}"
        consultation.save()

    elif action == "reject":
        consultation.status = "rejected"
        consultation.save()

    # Redirect back to dashboard to see the change
    return redirect("lawyer_dashboard")


# =========================
# WALLET VIEWS
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
        amount_str = request.POST.get("amount")
        try:
            # Use Decimal for financial calculations
            amount = Decimal(amount_str)
            if amount > 0:
                request.user.wallet.credit(amount, description="Added funds via Bank")
                messages.success(request, f"Successfully added ₹{amount}")
            else:
                messages.error(request, "Enter a valid amount")
        except:
            messages.error(request, "Invalid input")
    return redirect("wallet")


# =========================
# VIDEO ROOM LOGIC (THE BRIDGE)
# =========================
# accounts/views.py

# accounts/views.py

@login_required
def join_room(request, room_id):
    # 1. Verify this room exists in our DB
    consultation = get_object_or_404(ConsultationRequest, room_id=room_id)

    # 2. Setup Daily API
    headers = {
        "Authorization": f"Bearer {settings.DAILY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Create/Verify Room (Silent fail if exists is handled by logic flow)
    try:
        requests.post(
            "https://api.daily.co/v1/rooms",
            headers=headers,
            json={
                "name": room_id,
                "properties": {
                    "enable_chat": True, "start_video_off": False, "start_audio_off": False,
                    "exp": int(time.time() + 7200) 
                }
            }
        )
    except:
        pass # If room exists, we just proceed

    daily_url = f"https://{settings.DAILY_SUBDOMAIN}.daily.co/{room_id}"

    # 3. STRICT ROUTING LOGIC
    # Check if the logged-in user is specifically the LAWYER for this case
    if request.user == consultation.lawyer:
        template = "accounts/video/lawyer_room.html"
        context = {
            "room_url": daily_url,
            "session_id": room_id
        }
    
    # Check if the logged-in user is specifically the CLIENT for this case
    elif request.user == consultation.client:
        template = "accounts/video/client_room.html"
        context = {
            "room_url": daily_url,
            "session_id": room_id,
            "balance": request.user.wallet.balance, 
            "rate": 100 
        }
        
    else:
        # If user is neither (hacking attempt), kick them out
        return redirect("home")

    return render(request, template, context)

# ... (Previous imports remain) ...

# =========================
# END SESSION & TRANSFER MONEY
# =========================
@csrf_exempt  # We exempt CSRF for simplicity in this fetch request, or pass token in JS
@login_required
def end_consultation_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            amount = Decimal(data.get('amount'))

            # 1. Get the Consultation Request
            consultation = get_object_or_404(ConsultationRequest, room_id=room_id)

            # 2. Verify: Only the Client can trigger the payment (Security)
            if request.user != consultation.client:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

            # 3. Perform the Transaction
            client_wallet = consultation.client.wallet
            lawyer_wallet = consultation.lawyer.wallet

            if client_wallet.debit(amount, description=f"Consultation Fee: {consultation.lawyer.get_full_name()}"):
                lawyer_wallet.credit(amount, description=f"Earnings: {consultation.client.get_full_name()}")
                
                # Mark as Completed
                consultation.status = "completed"
                consultation.amount_paid = amount
                consultation.save()
                
                return JsonResponse({"status": "success", "new_balance": client_wallet.balance})
            else:
                return JsonResponse({"status": "error", "message": "Insufficient Balance"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid Method"}, status=405)


# accounts/views.py

# accounts/views.py

@csrf_exempt
@login_required
def rate_lawyer_api(request):
    if request.method == "POST":
        try:
            # ... (Existing code for getting data) ...
            data = json.loads(request.body)
            room_id = data.get('room_id')
            score = int(data.get('score'))
            review = data.get('review', "")
            
            consultation = get_object_or_404(ConsultationRequest, room_id=room_id)

            # 1. Create the Rating
            Rating.objects.create(
                client=request.user,
                lawyer=consultation.lawyer,
                score=score,
                review=review
            )

            # 2. Calculate New Average
            ratings = Rating.objects.filter(lawyer=consultation.lawyer)
            avg_rating = sum(r.score for r in ratings) / len(ratings)
            
            # 3. Save to Profile (THE FIX)
            profile = LawyerProfile.objects.get(user=consultation.lawyer)
            profile.rating = round(avg_rating, 1) 
            profile.save()  # <--- THIS WAS MISSING!
            
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=400)

@login_required
def view_case_brief(request, request_id):
    # 1. Get the request (Ensure it belongs to the logged-in lawyer)
    consultation_req = get_object_or_404(
        ConsultationRequest, 
        id=request_id, 
        lawyer=request.user
    )

    # 2. Render the detail template
    return render(request, "accounts/lawyer/request_detail.html", {
        "req": consultation_req
    })