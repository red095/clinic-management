from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Organize fields - add 'role' and other custom fields to fieldsets if not standard
    # Since we inherited AbstractUser and added fields, we likely want to show them.
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('role', 'phone_number', 'date_of_birth', 'gender', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Info', {'fields': ('role', 'phone_number', 'date_of_birth', 'gender', 'address')}),
    )
