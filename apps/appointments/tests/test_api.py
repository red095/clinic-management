import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.appointments.models import Appointment

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

class TestAppointmentAPI:
    def test_list_appointments_patient(self, api_client, patient_user, appointment_factory):
        # Create appointments for this patient
        appointment_factory(patient=patient_user)
        appointment_factory(patient=patient_user)
        
        api_client.force_authenticate(user=patient_user)
        url = reverse('patient-appointments-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_appointments_doctor(self, api_client, doctor_user, appointment_factory):
        # Create appointments for this doctor
        appointment_factory(doctor=doctor_user)
        
        api_client.force_authenticate(user=doctor_user)
        url = reverse('doctor-appointments-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_appointment_patient(self, api_client, patient_user, doctor_user, future_date):
        api_client.force_authenticate(user=patient_user)
        url = reverse('patient-appointments-list')
        data = {
            'doctor': doctor_user.id,
            'scheduled_time': future_date,
            'reason_for_visit': 'Test Visit'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Appointment.objects.count() == 1
        assert Appointment.objects.first().patient == patient_user

    def test_confirm_appointment_doctor(self, api_client, doctor_user, appointment_factory):
        appointment = appointment_factory(doctor=doctor_user, status=Appointment.STATUS_PENDING)
        
        api_client.force_authenticate(user=doctor_user)
        url = reverse('doctor-appointments-confirm', args=[appointment.id])
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        appointment.refresh_from_db()
        assert appointment.status == Appointment.STATUS_CONFIRMED

    def test_cancel_appointment_patient(self, api_client, patient_user, appointment_factory):
        appointment = appointment_factory(patient=patient_user, status=Appointment.STATUS_PENDING)
        
        api_client.force_authenticate(user=patient_user)
        url = reverse('patient-appointments-cancel', args=[appointment.id])
        data = {'reason': 'Changed mind'}
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        appointment.refresh_from_db()
        assert appointment.status == Appointment.STATUS_CANCELLED
