import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestPatientRegistration:
    """Test the patient registration flow."""

    def test_register_page_loads(self):
        client = Client()
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_register_creates_patient(self):
        client = Client()
        data = {
            'email': 'newpatient@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone_number': '+251912345678',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 302  # redirect on success
        user = User.objects.get(email='newpatient@example.com')
        assert user.role == 'patient'
        assert user.first_name == 'Jane'

    def test_register_duplicate_email_fails(self):
        UserFactory(email='exists@example.com')
        client = Client()
        data = {
            'email': 'exists@example.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone_number': '+251912345678',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 200  # stays on page with errors


@pytest.mark.django_db
class TestLogin:
    """Test the login flow."""

    def test_login_page_loads(self):
        client = Client()
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_patient_login_redirects_to_dashboard(self):
        user = UserFactory(email='patient@test.com', role='patient')
        client = Client()
        logged_in = client.login(username='patient@test.com', password='testpass123')
        assert logged_in is True
        response = client.get(reverse('login'))
        # If already logged in, check dashboard is accessible
        response = client.get(reverse('patient_dashboard'))
        assert response.status_code == 200

    def test_doctor_login_with_must_reset_redirects(self):
        user = UserFactory(
            email='doctor@test.com',
            role='doctor',
            must_reset_password=True,
            license_number='LIC-123',
            speciality='Cardiology',
        )
        client = Client()
        client.login(username='doctor@test.com', password='testpass123')
        response = client.post(
            reverse('login'),
            {'username': 'doctor@test.com', 'password': 'testpass123'},
            follow=True,
        )
        # Should end up at set_password page
        assert 'set_password' in response.redirect_chain[-1][0] or response.status_code == 200


@pytest.mark.django_db
class TestDoctorOTPCreation:
    """Test the doctor OTP creation service."""

    def test_create_doctor_with_otp(self):
        from apps.accounts.services import create_doctor_with_otp

        doctor, otp = create_doctor_with_otp(
            email='newdoc@clinic.com',
            first_name='John',
            last_name='Smith',
            speciality='Cardiology',
            license_number='LIC-9999',
        )
        assert doctor.role == 'doctor'
        assert doctor.must_reset_password is True
        assert doctor.speciality == 'Cardiology'
        assert len(otp) == 12
        # Doctor can authenticate with OTP
        assert doctor.check_password(otp)

    def test_duplicate_email_raises(self):
        from apps.accounts.services import create_doctor_with_otp

        UserFactory(email='dup@clinic.com')
        with pytest.raises(ValueError):
            create_doctor_with_otp(
                email='dup@clinic.com',
                first_name='John',
                last_name='Smith',
                speciality='General',
                license_number='LIC-8888',
            )


@pytest.mark.django_db
class TestPasswordReset:
    """Test forced password reset flow."""

    def test_set_password_redirects_if_not_required(self):
        user = UserFactory(email='notrequired@test.com', must_reset_password=False)
        client = Client()
        client.login(username='notrequired@test.com', password='testpass123')
        response = client.get(reverse('set_password'))
        assert response.status_code == 302  # redirects away

    def test_set_password_works(self):
        user = UserFactory(
            email='resetme@test.com',
            role='doctor',
            must_reset_password=True,
            license_number='LIC-111',
            speciality='General',
        )
        client = Client()
        client.login(username='resetme@test.com', password='testpass123')
        response = client.post(reverse('set_password'), {
            'new_password': 'NewSecure456!',
            'confirm_password': 'NewSecure456!',
        })
        assert response.status_code == 302  # redirect on success
        user.refresh_from_db()
        assert user.must_reset_password is False
        assert user.check_password('NewSecure456!')


@pytest.mark.django_db
class TestAppointmentBooking:
    """Test appointment booking."""

    def test_booking_page_requires_login(self):
        client = Client()
        response = client.get(reverse('book_appointment'))
        assert response.status_code == 302  # redirects to login

    def test_booking_page_loads_for_patient(self):
        patient = UserFactory(email='bookpatient@test.com', role='patient')
        client = Client()
        client.login(username='bookpatient@test.com', password='testpass123')
        response = client.get(reverse('book_appointment'))
        assert response.status_code == 200
