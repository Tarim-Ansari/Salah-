from django.contrib import admin
from .models import (
    User,
    LawyerProfile,
    Wallet,
    ConsultationRequest,
    ServiceCategory,
    Rating,
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "role", "is_active")
    search_fields = ("email", "first_name", "last_name")


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bar_council_id", "experience_years", "is_available")
    list_filter = ("is_available",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ("client", "lawyer", "status", "created_at")
    list_filter = ("status",)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("lawyer", "client", "score", "created_at")
    list_filter = ("score",)
    search_fields = ("lawyer__username", "client__username")

