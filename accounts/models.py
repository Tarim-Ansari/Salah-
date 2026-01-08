from django.db import models
from django.contrib.auth.models import AbstractUser


# -----------------------------
# Custom User Model
# -----------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("lawyer", "Lawyer"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -----------------------------
# Service Categories
# -----------------------------
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# -----------------------------
# Lawyer Profile
# -----------------------------
class LawyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    experience_years = models.PositiveIntegerField()
    categories = models.ManyToManyField(ServiceCategory)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


# -----------------------------
# Wallet
# -----------------------------
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - ₹{self.balance}"


# -----------------------------
# Consultation Request
# -----------------------------
class ConsultationRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    )

    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_requests"
    )
    lawyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lawyer_requests"
    )
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} → {self.lawyer} ({self.status})"


# -----------------------------
# Ratings (CLIENT → LAWYER)
# -----------------------------
class Rating(models.Model):
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_ratings"
    )
    lawyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_ratings"
    )
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lawyer} rated {self.rating}"
