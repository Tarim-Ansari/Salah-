from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
# --------------------
# Custom User
# --------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("lawyer", "Lawyer"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.email or self.username

# --------------------
# Service Categories
# --------------------
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# --------------------
# Lawyer Profile
# --------------------
class LawyerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    experience_years = models.IntegerField(default=0)
    bar_council_id = models.CharField(max_length=50, blank=True, null=True)
    is_available = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to="lawyers/", blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.get_full_name() or self.user.email

# --------------------
# Consultation Request
# --------------------
class ConsultationRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"), # Added completed status
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_requests")
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lawyer_requests")
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    # 2. NEW DETAILED CASE BRIEF FIELDS (Added to match the HTML form)
    issue_start = models.DateField(blank=True, null=True)
    opposing_party = models.CharField(max_length=255, blank=True, null=True)
    current_status = models.CharField(max_length=255, blank=True, null=True)
    desired_outcome = models.CharField(max_length=255, blank=True, null=True)
    documents = models.FileField(upload_to="case_docs/", blank=True, null=True)

    # 3. METADATA
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    room_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    # 4. PHASE 1 (PRE-CALL) AI FIELDS
    ai_refined_description = models.TextField(blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=10, null=True, blank=True, decimal_places=2)
    estimated_duration = models.IntegerField(blank=True, null=True)
    ai_client_checklist = models.JSONField(blank=True, null=True)

    # 5. PHASE 3 (POST-CALL) AI FIELDS
    call_transcript = models.TextField(blank=True, null=True)
    transcript_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    ai_call_summary = models.TextField(blank=True, null=True)
    ai_execution_plan = models.JSONField(blank=True, null=True)
    ai_drafted_document = models.TextField(blank=True, null=True)
    case_milestone = models.CharField(max_length=100, default="Pending Consultation")

    def __str__(self):
        return f"{self.subject} ({self.client.username} -> {self.lawyer.username})"
    
# --------------------
# Rating
# --------------------
class Rating(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_ratings")
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_ratings")
    score = models.IntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lawyer.username} - {self.score}⭐"

# --------------------
# WALLET SYSTEM 
# --------------------
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - ₹{self.balance}"

    def credit(self, amount, description=""):
        self.balance += amount
        self.save()
        Transaction.objects.create(
            wallet=self, amount=amount, transaction_type='credit', description=description
        )

    def debit(self, amount, description=""):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            Transaction.objects.create(
                wallet=self, amount=amount, transaction_type='debit', description=description
            )
            return True
        return False

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit (Added)'),
        ('debit', 'Debit (Spent)'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_type.title()}: ₹{self.amount}"