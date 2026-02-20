import pytest
from unittest.mock import patch
from django.core.exceptions import ValidationError, PermissionDenied
from apps.appointments.services import book_appointment, confirm_appointment
from apps.appointments.models import Appointment
from apps.core.models import AuditLog

pytestmark = pytest.mark.django_db

class TestAppointmentServices:
    def test_book_appointment_creates_pending_appointment(self, patient_user, doctor_user, future_date):
        with patch('apps.appointments.services.send_appointment_confirmation_email.delay') as mock_task:
            appointment = book_appointment(patient_user, doctor_user, future_date, "Checkup")
            
            assert appointment.status == Appointment.STATUS_PENDING
            assert appointment.patient == patient_user
            assert appointment.doctor == doctor_user
            
            # Check Log
            assert AuditLog.objects.filter(action='created_appointment', object_id=str(appointment.id)).exists()
            
            # Check Task Triggered
            mock_task.assert_called_once()

    def test_book_appointment_fails_if_past(self, patient_user, doctor_user, past_date):
        with pytest.raises(ValidationError) as exc:
            book_appointment(patient_user, doctor_user, past_date, "Checkup")
        assert "past" in str(exc.value)

    def test_confirm_appointment_transitions_status(self, appointment_factory, doctor_user):
        appointment = appointment_factory(status=Appointment.STATUS_PENDING, doctor=doctor_user)
        
        confirm_appointment(appointment, doctor_user)
        
        assert appointment.status == Appointment.STATUS_CONFIRMED
        assert AuditLog.objects.filter(action='confirmed_appointment', object_id=str(appointment.id)).exists()

    def test_confirm_appointment_wrong_doctor_raises_permission_denied(self, appointment_factory, doctor_user, another_doctor_user):
        appointment = appointment_factory(status=Appointment.STATUS_PENDING, doctor=doctor_user)
        
        with pytest.raises(PermissionDenied):
            confirm_appointment(appointment, another_doctor_user)
