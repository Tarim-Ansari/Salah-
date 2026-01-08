from django.contrib import admin
from .models import (
    User,
    LawyerProfile,
    Wallet,
    ConsultationRequest,
    ServiceCategory,
    Rating,
)


# -----------------------------
# USER ADMIN
# -----------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role",)
    search_fields = ("username", "email")


# -----------------------------
# SERVICE CATEGORY
# -----------------------------
@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -----------------------------
# LAWYER PROFILE
# -----------------------------
@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "experience_years", "is_verified", "is_available")
    list_filter = ("is_verified", "is_available")
    filter_horizontal = ("categories",)


# -----------------------------
# WALLET
# -----------------------------
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
    search_fields = ("user__username",)


# -----------------------------
# CONSULTATION REQUEST
# -----------------------------
@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("client", "lawyer", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("client__username", "lawyer__username")


# -----------------------------
# RATINGS
# -----------------------------
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("lawyer", "client", "rating", "created_at")
    list_filter = ("rating",)
