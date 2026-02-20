from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
from .models import Appointment
from apps.core.services import log_action
from .tasks import send_appointment_confirmation_email

def book_appointment(patient, doctor, scheduled_time, reason_for_visit):
    """
    Handles the logic for booking a new appointment.
    """
    # 1. Enforce Role Validation
    if patient.role != 'patient':
        raise ValidationError({'patient': 'Selected user is not a patient.'})
    if doctor.role != 'doctor':
        raise ValidationError({'doctor': 'Selected user is not a doctor.'})

    # 2. Time Validation
    now = timezone.now()
    if scheduled_time < now:
        raise ValidationError({'scheduled_time': 'Appointments cannot be scheduled in the past.'})
    
    future_window = now + timedelta(days=90)
    if scheduled_time > future_window:
        raise ValidationError({'scheduled_time': 'Appointments must be within the next 90 days.'})

    # 3. Double Booking Check (Only for CONFIRMED appointments)
    
    overlapping = Appointment.objects.filter(
        doctor=doctor,
        scheduled_time=scheduled_time,
        status=Appointment.STATUS_CONFIRMED
    )
    if overlapping.exists():
         raise ValidationError({'scheduled_time': "This doctor already has a confirmed appointment at this time."})

    # Create the appointment
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_time=scheduled_time,
        reason_for_visit=reason_for_visit,
        status=Appointment.STATUS_PENDING
    )
    # Ensure it's saved before passing ID (create saves it, but good to be explicit if logic changes)
    
    log_action(patient, 'created_appointment', appointment)
    
    # Trigger Celery Task
    send_appointment_confirmation_email.delay(appointment.id)
    
    return appointment

def confirm_appointment(appointment, doctor):
    """
    Transitions an appointment from PENDING to CONFIRMED.
    """
    # Validate Doctor Ownership
    if appointment.doctor != doctor:
        raise PermissionDenied("You can only confirm your own appointments.")

    # Validate State Transition
    if appointment.status != Appointment.STATUS_PENDING:
        raise ValidationError("Only pending appointments can be confirmed.")

    # Validate Double Booking again before confirming
    overlapping = Appointment.objects.filter(
        doctor=appointment.doctor,
        scheduled_time=appointment.scheduled_time,
        status=Appointment.STATUS_CONFIRMED
    ).exclude(pk=appointment.pk)
    
    if overlapping.exists():
        raise ValidationError("This doctor already has a confirmed appointment at this time.")

    appointment.transition_to(Appointment.STATUS_CONFIRMED)
    # appointment.save() is called inside transition_to
    log_action(doctor, 'confirmed_appointment', appointment)
    return appointment

def complete_appointment(appointment, doctor):
    """
    Transitions an appointment from CONFIRMED to COMPLETED.
    """
    # Validate Doctor Ownership
    if appointment.doctor != doctor:
        raise PermissionDenied("You can only complete your own appointments.")

    # Validate State Transition
    if appointment.status != Appointment.STATUS_CONFIRMED:
        raise ValidationError("Only confirmed appointments can be completed.")

    appointment.transition_to(Appointment.STATUS_COMPLETED)
    # appointment.save() is called inside transition_to
    log_action(doctor, 'completed_appointment', appointment)
    return appointment

def cancel_appointment(appointment, user, reason=""):
    """
    Cancels an appointment.
    """
    # Validate Accessibility
    if not appointment.is_accessible_by(user):
        raise PermissionDenied("You do not have permission to cancel this appointment.")

    # Validate State Transition
    if not appointment.can_be_cancelled():
         raise ValidationError("This appointment cannot be cancelled.")

    appointment.cancelled_by = user
    appointment.cancellation_reason = reason
    appointment.transition_to(Appointment.STATUS_CANCELLED)
    # appointment.save() is called inside transition_to
    log_action(user, 'cancelled_appointment', appointment, metadata={'reason': reason})
    return appointment
