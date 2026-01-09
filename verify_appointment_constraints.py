
import os
import django
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.appointments.models import Appointment

def create_user(email, role, **kwargs):
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'role': role,
            'first_name': 'Test',
            'last_name': 'User',
            **kwargs
        }
    )
    if not created: 
        # Ensure role is correct if user exists
        user.role = role
        user.save()
    return user

def str_err(e):
    if hasattr(e, 'message_dict'):
        return str(e.message_dict)
    return str(e)

def test_constraints():
    print("Verifying Appointment Constraints...\n")

    # Setup Users
    doctor1 = create_user('doc1@test.com', 'doctor', license_number='LIC001')
    doctor2 = create_user('doc2@test.com', 'doctor', license_number='LIC002')
    patient1 = create_user('pat1@test.com', 'patient', phone_number='1234567890')
    patient2 = create_user('pat2@test.com', 'patient', phone_number='0987654321')
    admin = create_user('admin@test.com', 'admin')

    # 1. Role Validation
    print("1. Role Validation")
    
    # Invalid Patient (using doctor as patient)
    try:
        appt = Appointment(
            patient=doctor1, # Wrong role
            doctor=doctor1,
            scheduled_time=timezone.now() + timedelta(days=1),
            reason_for_visit="Checkup"
        )
        appt.clean()
        print("FAIL: Allowed doctor as patient")
    except ValidationError as e:
        print(f"PASS: Caught invalid patient role: {str_err(e)}")

    # Invalid Doctor (using patient as doctor)
    try:
        appt = Appointment(
            patient=patient1,
            doctor=patient1, # Wrong role
            scheduled_time=timezone.now() + timedelta(days=1),
            reason_for_visit="Checkup"
        )
        appt.clean()
        print("FAIL: Allowed patient as doctor")
    except ValidationError as e:
        print(f"PASS: Caught invalid doctor role: {str_err(e)}")

    # 2. Time Validation
    print("\n2. Time Validation")
    
    # Past Appointment
    try:
        appt = Appointment(
            patient=patient1,
            doctor=doctor1,
            scheduled_time=timezone.now() - timedelta(days=1),
            reason_for_visit="Back to the future"
        )
        appt.clean()
        print("FAIL: Allowed past appointment")
    except ValidationError as e:
        print(f"PASS: Caught past appointment: {str_err(e)}")

    # Too far future (91 days)
    try:
        appt = Appointment(
            patient=patient1,
            doctor=doctor1,
            scheduled_time=timezone.now() + timedelta(days=91),
            reason_for_visit="Far future"
        )
        appt.clean()
        print("FAIL: Allowed appointment > 90 days")
    except ValidationError as e:
        print(f"PASS: Caught future limit: {str_err(e)}")

    # 3. Double Booking
    print("\n3. Double Booking Validation")
    
    confirm_time = timezone.now() + timedelta(days=2)
    
    # Create valid initial appointment
    appt1 = Appointment.objects.create(
        patient=patient1,
        doctor=doctor1,
        scheduled_time=confirm_time,
        status=Appointment.STATUS_CONFIRMED,
        reason_for_visit="Initial"
    )
    print("Created initial CONFIRMED appointment.")

    # Attempt overlapping CONFIRMED appointment
    try:
        appt2 = Appointment(
            patient=patient2,
            doctor=doctor1, # Same doctor
            scheduled_time=confirm_time, # Same time
            status=Appointment.STATUS_CONFIRMED, # Both Confirmed
            reason_for_visit="Overlap"
        )
        appt2.clean()
        print("FAIL: Allowed double booking for doctor")
    except ValidationError as e:
        print(f"PASS: Caught double booking: {str_err(e)}")

    # Overlapping but PENDING (Should allow)
    try:
        appt3 = Appointment(
            patient=patient2,
            doctor=doctor1,
            scheduled_time=confirm_time,
            status=Appointment.STATUS_PENDING,
            reason_for_visit="Overlap Pending"
        )
        appt3.clean()
        print("PASS: Allowed overlapping PENDING appointment (Expected)")
    except ValidationError as e:
        print(f"FAIL: Blocked overlapping PENDING appointment: {str_err(e)}")

    # Clean up
    Appointment.objects.all().delete()
    User.objects.filter(email__in=['doc1@test.com', 'doc2@test.com', 'pat1@test.com', 'pat2@test.com', 'admin@test.com']).delete()

if __name__ == "__main__":
    test_constraints()
