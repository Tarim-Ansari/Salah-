from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


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

    # ✅ ADD THIS
    profile_photo = models.ImageField(
        upload_to="lawyers/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.email





# --------------------
# Consultation Request
# --------------------
class ConsultationRequest(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_requests")
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lawyer_requests")

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)




# --------------------
# Rating (CLIENT ONLY)
# --------------------
class Rating(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_ratings"
    )
    lawyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_ratings"
    )
    score = models.IntegerField()  # 1–5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lawyer.username} - {self.score}⭐"


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.email} - ₹{self.balance}"



