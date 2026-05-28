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
from groq import Groq


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
        
        # 1. Grab the NEW fields we added to the form
        issue_start = request.POST.get("issue_start") or None  # Handle empty dates safely
        opposing_party = request.POST.get("opposing_party")
        current_status = request.POST.get("current_status")
        desired_outcome = request.POST.get("desired_outcome")
        documents = request.FILES.get("documents")  # 📁 Handle file uploads

        category = get_object_or_404(ServiceCategory, id=category_id)

        ai_refined_description = request.POST.get("ai_refined_description")
        estimated_cost = request.POST.get("estimated_cost") or None
        estimated_duration = request.POST.get("estimated_duration") or None
        ai_client_checklist = request.POST.get("ai_client_checklist")

        # WALLET VERIFICATION: Ensure user has sufficient balance
        if estimated_cost:
            try:
                estimated_cost_decimal = Decimal(estimated_cost)
                user_balance = request.user.wallet.balance
                
                if user_balance < estimated_cost_decimal:
                    messages.error(
                        request,
                        f"Insufficient wallet balance. Required: ₹{estimated_cost_decimal}, "
                        f"Available: ₹{user_balance}. Please recharge your wallet."
                    )
                    return redirect("wallet")
            except (ValueError, AttributeError):
                pass  # If conversion fails or wallet doesn't exist, proceed anyway

        # 2. Save EVERYTHING to the database
        ConsultationRequest.objects.create(
            client=request.user, 
            lawyer=lawyer_profile.user,
            category=category, 
            subject=subject, 
            description=description,
            # Pass the new fields here:
            issue_start=issue_start,
            opposing_party=opposing_party,
            current_status=current_status,
            desired_outcome=desired_outcome,
            documents=documents,
            ai_refined_description=ai_refined_description,
            estimated_cost=estimated_cost,
            estimated_duration=estimated_duration,
            ai_client_checklist=ai_client_checklist
        )
        return redirect("client_consultations")

    return render(request, "accounts/client/case_brief.html", {
        "lawyer": lawyer_profile, 
        "categories": categories,
    })

@csrf_exempt
@login_required
def evaluate_intake(request):
    if request.method == "POST":
        try:
            body_data = json.loads(request.body)
            category = body_data.get("category", "")
            subject = body_data.get("subject", "")
            description = body_data.get("description", "")
            
            # Grab the chat history from the Javascript
            chat_history = body_data.get("chat_history", []) 
            
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            # 1. Setup the messages array with your detailed prompt
            messages = [
                {
                    "role": "system",
                    "content":'''
                    'You are the "SALAH AI Legal Intake Specialist," a high-precision paralegal system for an Indian Legal-Tech platform. Your goal is to transform raw user input into a professional, structured case brief while ensuring the user is prepared for their consultation.
                    ### OPERATIONAL RULES:
                    1. TONE: Professional, empathetic, and legally formal.
                    2. CONTEXT: Follow Indian Law (IPC, BNS, CPC) and Indian legal procedures.
                    3. COMPLETENESS THRESHOLD: You must ensure you have: (a) Clear identity of the opposing party, (b) Date or timeline of the dispute, (c) The specific "ask" or desired remedy, (d) Critical evidence status (contracts, receipts, etc.).
                    4. NO HALLUCINATION: If the user provides vague info, do not guess. Ask.
                    5. LOSSLESS SUMMARY: Your final summary must include every specific name, date, amount, and location mentioned by the user.

                    ### OUTPUT FORMAT:
                    You must ALWAYS respond in valid JSON. Do not include any text outside the JSON block.

                    ### STATE 1: If the case is VAGUE or MISSING critical details:
                    Return:
                    {
                    "status": "CLARIFYING",
                    "reason": "Explain briefly why you need more info",
                    "question": "The single most important question to ask the user next",
                    "is_required": true
                    }

                    ### STATE 2: If the case is COMPLETE:
                    Return:
                    {
                    "status": "FINALIZED",
                    "refined_description": "A lossless, 3-paragraph professional legal brief. Para 1: Facts & Parties. Para 2: Dispute Timeline & Evidence. Para 3: Legal complication & Desired Outcome.",
                    "estimated_duration": 15,
                    "recommended_questions": ["3-5 specific, strategic questions the user should ask the lawyer during the call"],
                    "relevant_statutes": ["Mention relevant Indian sections like IPC, Section 138 NI Act, etc., if applicable"]
                    }'''
                },
                {
                    "role": "user",
                    "content": f"""
                        Category: {category}, 
                        Subject: {subject}, 
                        Description: {description}
                        """
                }
            ]
            
            # 2. Append the Chat History so Groq remembers the conversation
            for chat in chat_history:
                messages.append({"role": chat["role"], "content": chat["content"]})
            
            # 3. Call Groq
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, # Safety net: forces Groq to output JSON
                messages=messages
            ) 
            
            # 4. Extract and clean the JSON response
            raw_response = completion.choices[0].message.content
            
            # Strip markdown just in case (Safety Net)
            cleaned_response = raw_response.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(cleaned_response)

            # 5. Send it back to the HTML page!
            return JsonResponse(ai_data)

        except Exception as e:
            # If the AI hallucinates or API breaks, send a safe fallback
            print(f"Groq Error: {e}")
            fallback_data = {
                "status": "FINALIZED",
                "refined_description": description, # Safe fallback using original text
                "estimated_duration": 15,
                "recommended_questions": ["What are my legal rights?", "What is the next step?"]
            }
            return JsonResponse(fallback_data)

    return JsonResponse({"error": "Invalid request method"}, status=400)

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

    # 3. RATING LOGIC (FIXED now)
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
    # 1. Ensure Wallet Exists
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    # 2. Get Transaction History
    transactions = wallet.transactions.all().order_by('-created_at')

    # 3. Calculate Today's Earnings
    today = timezone.now().date()
    today_earnings_data = ConsultationRequest.objects.filter(
        lawyer=request.user,
        status='completed',
        created_at__date=today
    ).aggregate(total=Sum('amount_paid'))
    today_sum = today_earnings_data['total'] or 0

    # 4. Calculate This Month's Earnings
    month_earnings_data = ConsultationRequest.objects.filter(
        lawyer=request.user,
        status='completed',
        created_at__year=today.year,
        created_at__month=today.month
    ).aggregate(total=Sum('amount_paid'))
    month_sum = month_earnings_data['total'] or 0

    # 5. Pass Data to Template
    return render(request, "accounts/lawyer/earnings.html", {
        "wallet": wallet,
        "transactions": transactions,
        "today_earnings": today_sum,
        "month_earnings": month_sum,
    })

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
            "rate": 20 
        }
        
    else:
        return redirect("home")

    return render(request, template, context)


# =========================
# END SESSION & TRANSFER MONEY
# =========================
@csrf_exempt  
@login_required
def end_consultation_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            room_id = data.get('room_id')
            amount = Decimal(data.get('amount'))

            consultation = get_object_or_404(ConsultationRequest, room_id=room_id)

            if request.user != consultation.client:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

            client_wallet = consultation.client.wallet
            lawyer_wallet = consultation.lawyer.wallet

            if client_wallet.debit(amount, description=f"Consultation Fee: {consultation.lawyer.get_full_name()}"):
                lawyer_wallet.credit(amount, description=f"Earnings: {consultation.client.get_full_name()}")
                
                consultation.status = "completed"
                consultation.amount_paid = amount
                consultation.save()
                
                return JsonResponse({"status": "success", "new_balance": client_wallet.balance})
            else:
                return JsonResponse({"status": "error", "message": "Insufficient Balance"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid Method"}, status=405)


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

