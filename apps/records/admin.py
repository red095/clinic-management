from django.contrib import admin
from .models import MedicalRecord

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'patient', 'doctor', 'get_status_display')
    search_fields = ('patient__email', 'patient__last_name', 'doctor__last_name', 'diagnosis')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    # Read-only fields to enforce immutability context in Admin
    # Though admins *can* usually do anything, it's good practice to mark critical audit info as read-only
    readonly_fields = ('created_at', 'patient', 'doctor', 'appointment')

    def get_status_display(self, obj):
        return "Finalized" # Records are created only when finalized/completed
    get_status_display.short_description = "Status"

    def has_delete_permission(self, request, obj=None):
        # Optional: Prevent admins from deleting records easily if strict compliance needed
        # But for now allow it usually
        return True
