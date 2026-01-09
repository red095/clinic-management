from django.contrib import admin
from .models import MedicalRecord

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'patient', 'doctor', 'created_at')
    search_fields = ('patient__email', 'doctor__email')
    readonly_fields = ('patient', 'doctor', 'appointment', 'diagnosis', 'notes', 'created_at')
    
    def has_add_permission(self, request):
        # Allow adding new records (usually done via custom views or doctor interface, but admin okay for dev)
        # But fields like patient, doctor, appointment should be set carefully. 
        # Actually, for admin creation, we might want to allow writing initially?
        # Requirement says "Lock admin form fields as read-only". 
        # Usually this implies for existing records.
        return True

    def has_change_permission(self, request, obj=None):
        # Strict immutability - no changing existing records
        if obj:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Strict immutability - no deleting
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
             # Everything read-only for existing object
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields
