from django import forms
from .models import Appointment
from apps.accounts.models import User
from django.utils import timezone

class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_time', 'reason_for_visit']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason_for_visit': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.patient = user
        # Filter doctors only
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        
    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        if scheduled_time:
             if scheduled_time < timezone.now():
                raise forms.ValidationError("Cannot book appointments in the past.")
             
             # Check for overlapping appointments (PENDING or CONFIRMED) for this doctor
             doctor = self.cleaned_data.get('doctor')
             if doctor:
                 # Check if any appointment exists for this doctor at this time
                 # Note: self.cleaned_data.get('doctor') might be missing if field validation failed? 
                 # But doctor is required field.
                 exists = Appointment.objects.filter(
                     doctor=doctor,
                     scheduled_time=scheduled_time,
                     status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
                 ).exists()
                 if exists:
                     raise forms.ValidationError("This time slot is already booked.")
        return scheduled_time
