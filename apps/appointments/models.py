import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Appointment(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'patient'}
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reason_for_visit = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional cancellation details
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments'
    )
    cancellation_reason = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['doctor']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['doctor', 'scheduled_time']),
        ]
        ordering = ['-scheduled_time']

    def __str__(self):
        return f"{self.patient} with {self.doctor} at {self.scheduled_time}"

    def clean(self):
        # 1. Enforce Role Validation (Double check strictly)
        if self.patient.role != 'patient':
            raise ValidationError({'patient': 'Selected user is not a patient.'})
        if self.doctor.role != 'doctor':
            raise ValidationError({'doctor': 'Selected user is not a doctor.'})

        # 2. Time Validation
        if self.scheduled_time:
            now = timezone.now()
            if self.scheduled_time < now:
                raise ValidationError({'scheduled_time': 'Appointments cannot be scheduled in the past.'})
            
            future_window = now + timedelta(days=90)
            if self.scheduled_time > future_window:
                raise ValidationError({'scheduled_time': 'Appointments must be within the next 90 days.'})

        # 3. Double Booking Check (Only for CONFIRMED appointments)
        # Check against existing CONFIRMED appointments for the same doctor at the same time
        # Exclude self if editing
        
        # Note: We are checking for EXACT time match as per "A doctor cannot have two CONFIRMED appointments at the same time"
        # In a real scheduling system, we might check for time slots/duration overlap.
        # Assuming appointments are point-in-time or we rely on exact match for now based on requirement "at the same time".
        
        overlapping = Appointment.objects.filter(
            doctor=self.doctor,
            scheduled_time=self.scheduled_time,
            status=self.STATUS_CONFIRMED
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
            
        if overlapping.exists():
             # If THIS appointment is also being set to CONFIRMED (or is already), it's a conflict
             if self.status == self.STATUS_CONFIRMED:
                 raise ValidationError("This doctor already has a confirmed appointment at this time.")

    def can_be_cancelled(self):
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]

    def can_be_completed(self):
        return self.status == self.STATUS_CONFIRMED

    def is_editable(self):
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]