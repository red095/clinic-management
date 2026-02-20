import pytest
from django.core.exceptions import ValidationError
from apps.appointments.models import Appointment

pytestmark = pytest.mark.django_db

class TestAppointmentStateMachine:
    def test_initial_status_is_pending(self, appointment_factory):
        appointment = appointment_factory(status=Appointment.STATUS_PENDING)
        assert appointment.status == Appointment.STATUS_PENDING

    def test_allowed_transition_pending_to_confirmed(self, appointment_factory):
        appointment = appointment_factory(status=Appointment.STATUS_PENDING)
        appointment.transition_to(Appointment.STATUS_CONFIRMED)
        assert appointment.status == Appointment.STATUS_CONFIRMED

    def test_allowed_transition_confirmed_to_completed(self, appointment_factory):
        appointment = appointment_factory(status=Appointment.STATUS_CONFIRMED)
        appointment.transition_to(Appointment.STATUS_COMPLETED)
        assert appointment.status == Appointment.STATUS_COMPLETED

    def test_invalid_transition_pending_to_completed(self, appointment_factory):
        appointment = appointment_factory(status=Appointment.STATUS_PENDING)
        with pytest.raises(ValidationError) as exc:
            appointment.transition_to(Appointment.STATUS_COMPLETED)
        assert "Invalid state transition" in str(exc.value)

    def test_invalid_transition_completed_to_confirmed(self, appointment_factory):
        # Create confirmed first, then transition to completed, then try to go back
        appointment = appointment_factory(status=Appointment.STATUS_CONFIRMED)
        appointment.transition_to(Appointment.STATUS_COMPLETED)
        
        with pytest.raises(ValidationError) as exc:
            appointment.transition_to(Appointment.STATUS_CONFIRMED)
        assert "Invalid state transition" in str(exc.value)
