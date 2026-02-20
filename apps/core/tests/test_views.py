import pytest
from django.urls import reverse
from django.test import Client
from apps.appointments.models import Appointment

pytestmark = pytest.mark.django_db

class TestDashboardViews:
    def test_doctor_dashboard_access(self, client, doctor_user):
        client.force_login(user=doctor_user)
        url = reverse('doctor_dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'todays_appointments' in response.context
        assert 'pending_appointments' in response.context

    def test_admin_dashboard_access(self, client, admin_user):
        client.force_login(user=admin_user)
        url = reverse('admin_dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'appointments_today' in response.context
        assert 'doctor_workload' in response.context

    def test_patient_dashboard_access(self, client, patient_user):
        client.force_login(user=patient_user)
        url = reverse('patient_dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'upcoming_appointments' in response.context
