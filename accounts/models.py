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
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_requests")
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lawyer_requests")
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    room_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
# WALLET SYSTEM (Moved here!)
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