from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Appointment

@shared_task
def send_appointment_confirmation_email(appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        subject = 'Appointment Confirmation'
        message = f'Hello {appointment.patient.username},\n\nYour appointment with Dr. {appointment.doctor.username} has been scheduled for {appointment.scheduled_time}.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [appointment.patient.email]
        
        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent to {appointment.patient.email}"
    except Appointment.DoesNotExist:
        return "Appointment not found"
    except Exception as e:
        return f"Failed to send email: {str(e)}"
