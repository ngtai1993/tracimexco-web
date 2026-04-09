from django.contrib import admin
from .models import PasswordResetToken


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "is_used", "created_at"]
    list_filter = ["is_used"]
    search_fields = ["user__email"]
    readonly_fields = ["token", "created_at"]
