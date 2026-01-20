from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('scheduled_time', 'patient', 'doctor', 'status')
    list_filter = ('status', 'scheduled_time')
    search_fields = ('patient__email', 'patient__last_name', 'doctor__last_name', 'reason_for_visit')
    date_hierarchy = 'scheduled_time'
    ordering = ('-scheduled_time',)
