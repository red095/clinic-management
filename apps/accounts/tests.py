from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient_password = 'Password123!'
        self.patient = User.objects.create_user(
            email='patient@test.com', 
            password=self.patient_password, 
            role='patient',
            first_name='Test',
            last_name='Patient'
        )
        
        self.doctor_password = 'Password123!'
        self.doctor = User.objects.create_user(
            email='doctor@test.com', 
            password=self.doctor_password, 
            role='doctor',
            first_name='Dr',
            last_name='Test'
        )

    def test_login_redirect_patient(self):
        """Test that patients are redirected to patient dashboard after login"""
        response = self.client.post(reverse('login'), {
            'username': self.patient.email, # Custom user uses email as username usually, or LoginForm handles it
            'password': self.patient_password
        })
        # Expect 302 redirect
        self.assertEqual(response.status_code, 302)
        # Check chain for target.
        # Note: LoginView redirects. 
        self.assertRedirects(response, reverse('patient_dashboard'))

    def test_login_redirect_doctor(self):
        """Test that doctors are redirected to doctor dashboard after login"""
        response = self.client.post(reverse('login'), {
            'username': self.doctor.email,
            'password': self.doctor_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doctor_dashboard'))

    def test_unauthorized_access_dashboard(self):
        """Test that unauthenticated users cannot access dashboards"""
        response = self.client.get(reverse('patient_dashboard'))
        # Should redirect to login
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue('/login/' in response.url)

    def test_role_mismatch_access(self):
        """Test that a doctor cannot access patient dashboard and vice versa"""
        # Doctor tries Patient Dashboard
        self.client.login(email=self.doctor.email, password=self.doctor_password)
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Patient tries Doctor Dashboard
        self.client.logout()
        self.client.login(email=self.patient.email, password=self.patient_password)
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 403)
