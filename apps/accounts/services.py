import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import User


def _generate_otp(length=12):
    """Generate a secure random one-time password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_doctor_with_otp(email, first_name, last_name, speciality, license_number, phone_number=None, created_by=None):
    """
    Creates a doctor account, generates an OTP password, sends it via email,
    and marks must_reset_password=True so they are forced to change it on first login.
    Returns a tuple of (doctor, otp_password).
    """
    if User.objects.filter(email=email).exists():
        raise ValueError("A user with email '{}' already exists.".format(email))

    otp_password = _generate_otp()

    doctor = User.objects.create_user(
        email=email,
        password=otp_password,
        first_name=first_name,
        last_name=last_name,
        role='doctor',
        speciality=speciality,
        license_number=license_number,
        phone_number=phone_number,
        must_reset_password=True,
    )

    # Build login URL
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    login_url = "{}/accounts/login/".format(site_url)

    # Send email with OTP and login link
    subject = "Welcome to Clinic Management - Your Account Details"
    message = (
        "Dear Dr. {first} {last},\n\n"
        "Your doctor account has been created in the Clinic Management System.\n\n"
        "Login Details:\n"
        "  Email:    {email}\n"
        "  Password: {otp}\n\n"
        "IMPORTANT: You will be required to change your password on first login.\n\n"
        "Click here to login:\n"
        "  {login_url}\n\n"
        "Best regards,\n"
        "Clinic Management Team"
    ).format(
        first=first_name,
        last=last_name,
        email=email,
        otp=otp_password,
        login_url=login_url,
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return doctor, otp_password
