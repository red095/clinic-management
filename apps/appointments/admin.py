from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_time', 'status')
    list_filter = ('status', 'doctor')
    search_fields = ('patient__email', 'doctor__email')
    readonly_fields = ('created_at', 'updated_at')
