import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _
from apps.appointments.models import Appointment

class MedicalRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships - logically read-only after creation
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT, 
        related_name='medical_records',
        editable=False
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='authored_records',
        editable=False
    )
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        related_name='medical_record',
        editable=False
    )
    
    # Clinical Data
    diagnosis = models.TextField()
    notes = models.TextField()
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    # No updated_at - records are immutable
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ("view_own_record", "Can view own medical record"),
        ]

    def __str__(self):
        return f"Record for {self.patient} by {self.doctor} on {self.created_at.date()}"

    def clean(self):
        # 1. Integrity Check against Appointment
        if not hasattr(self, 'appointment'):
            return

        # Ensure Appointment is COMPLETED
        if self.appointment.status != Appointment.STATUS_COMPLETED:
            raise ValidationError({
                'appointment': _('Medical records can only be created for COMPLETED appointments.')
            })

        # Ensure Doctor matches Appointment Doctor
        if self.doctor != self.appointment.doctor:
            raise ValidationError({
                'doctor': _('The record doctor must match the appointment doctor.')
            })

        # Ensure Patient matches Appointment Patient
        if self.patient != self.appointment.patient:
            raise ValidationError({
                'patient': _('The record patient must match the appointment patient.')
            })

    def save(self, *args, **kwargs):
        # Enforce Immutability
        if self.pk:
            # Check if record already exists in DB
            # Note: self.pk is set by UUID field generic, so we need to check DB existence safely
            # or rely on 'force_insert' concept. 
            # Better: Fetch from DB to see if it exists.
            existing = MedicalRecord.objects.filter(pk=self.pk).exists()
            if existing:
                raise ValidationError(_("Medical records are immutable and cannot be edited."))
        
        # Run clean() for new records
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied(_("Medical records cannot be deleted."))

    def is_viewable_by(self, user):
        if user == self.doctor or user == self.patient:
            return True
        if user.role == 'admin':
            return True
        return False
    
    @classmethod
    def can_be_created_by(cls, user):
        return user.role == 'doctor'
