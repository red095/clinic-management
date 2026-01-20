from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Appointment

User = get_user_model()

class AppointmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup Users
        self.patient = User.objects.create_user(email='pat@test.com', password='pw', role='patient', first_name='P', last_name='Test')
        self.doctor = User.objects.create_user(email='doc@test.com', password='pw', role='doctor', first_name='D', last_name='Test')
        self.other_patient = User.objects.create_user(email='other@test.com', password='pw', role='patient')
        
        self.future_time = timezone.now() + timedelta(days=1, hours=10) # Tomorrow 10 AM (ensuring future)
        # Ensure minutes are clean for easier matching if needed, though exact time is fine
        self.future_time = self.future_time.replace(minute=0, second=0, microsecond=0)

    def test_booking_success(self):
        """Test successful appointment booking"""
        self.client.login(email=self.patient.email, password='pw')
        data = {
            'doctor': self.doctor.pk,
            'scheduled_time': self.future_time.strftime('%Y-%m-%dT%H:%M'), # Format for datetime-local often
            'reason_for_visit': 'Checkup'
        }
        # In form submission, datetime format depends on input type. 
        # Django forms usually handle standard formats.
        response = self.client.post(reverse('book_appointment'), data)
        self.assertEqual(response.status_code, 302) # Success redirect
        
        # Verify DB
        self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_double_booking_prevention(self):
        """Test system rejects double booking for same doctor at same time"""
        # Create existing appointment
        Appointment.objects.create(
            patient=self.other_patient,
            doctor=self.doctor,
            scheduled_time=self.future_time,
            status=Appointment.STATUS_CONFIRMED,
            reason_for_visit="Existing"
        )
        
        self.client.login(email=self.patient.email, password='pw')
        data = {
            'doctor': self.doctor.pk,
            'scheduled_time': self.future_time.strftime('%Y-%m-%d %H:%M:%S'), 
            'reason_for_visit': 'Double Book'
        }
        response = self.client.post(reverse('book_appointment'), data)
        
        self.assertEqual(response.status_code, 200)
        # Manual check for form errors
        form = response.context['form']
        self.assertTrue(form.errors)
        # Check field error
        self.assertTrue('scheduled_time' in form.errors)
        self.assertTrue("This time slot is already booked" in str(form.errors['scheduled_time']))

    def test_past_date_prevention(self):
        """Test rejection of past dates"""
        self.client.login(email=self.patient.email, password='pw')
        past_time = timezone.now() - timedelta(days=1)
        data = {
            'doctor': self.doctor.pk,
            'scheduled_time': past_time.strftime('%Y-%m-%d %H:%M:%S'),
            'reason_for_visit': 'Time Travel'
        }
        response = self.client.post(reverse('book_appointment'), data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue('scheduled_time' in form.errors)
        self.assertTrue("Cannot book appointments in the past" in str(form.errors['scheduled_time']))

    def test_doctor_action_confirm(self):
        """Test doctor confirming an appointment"""
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=self.future_time,
            status=Appointment.STATUS_PENDING
        )
        
        self.client.login(email=self.doctor.email, password='pw')
        # Fix URL: include 'confirm' action in reverse args
        url = reverse('appointment_action', args=[appt.pk, 'confirm'])
        response = self.client.post(url) # POST no data needed effectively or action param if used in view?
        # View def: post(self, request, pk, action) -> action comes from URL.
        
        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.STATUS_CONFIRMED)
        self.assertRedirects(response, reverse('doctor_dashboard'))

    def test_doctor_action_invalid_access(self):
        """Test doctor cannot act on another doctor's appointment"""
        other_doc = User.objects.create_user(email='doc2@test.com', password='pw', role='doctor')
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=other_doc,
            scheduled_time=self.future_time,
            status=Appointment.STATUS_PENDING
        )
        
        self.client.login(email=self.doctor.email, password='pw')
        # Fix URL: include 'confirm' action
        url = reverse('appointment_action', args=[appt.pk, 'confirm'])
        response = self.client.post(url)
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)
