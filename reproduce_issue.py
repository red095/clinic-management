
import os
import django
from django.core.exceptions import ValidationError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User

def test_validation():
    print("Testing User Model Validation...")

    # Test Doctor without license
    print("\n1. Testing Doctor without license number (Should Fail)")
    doctor = User(
        email='doctor_no_license@example.com',
        role='doctor',
        first_name='Doc',
        last_name='NoLicense'
    )
    try:
        doctor.clean()
        print("FAIL: Doctor without license was allowed!")
    except ValidationError as e:
        print(f"PASS: Caught expected error: {e}")

    # Test Patient without phone
    print("\n2. Testing Patient without phone number (Should Fail)")
    patient = User(
        email='patient_no_phone@example.com',
        role='patient',
        first_name='Pat',
        last_name='NoPhone'
    )
    try:
        patient.clean()
        print("FAIL: Patient without phone was allowed!")
    except ValidationError as e:
        print(f"PASS: Caught expected error: {e}")

    # Test Admin (Should Pass without these fields)
    print("\n3. Testing Admin validation (Should Pass)")
    admin = User(
        email='admin_valid@example.com',
        role='admin',
        first_name='Admin',
        last_name='User'
    )
    try:
        admin.clean()
        print("PASS: Admin validation successful")
    except ValidationError as e:
        print(f"FAIL: Admin raised error: {e}")

    # Test Valid Doctor
    print("\n4. Testing Valid Doctor (Should Pass)")
    valid_doctor = User(
        email='doctor_valid@example.com',
        role='doctor',
        first_name='Doc',
        last_name='Valid',
        license_number='LIC12345'
    )
    try:
        valid_doctor.clean()
        print("PASS: Valid Doctor validation successful")
    except ValidationError as e:
        print(f"FAIL: Valid Doctor raised error: {e}")

    # Test Valid Patient
    print("\n5. Testing Valid Patient (Should Pass)")
    valid_patient = User(
        email='patient_valid@example.com',
        role='patient',
        first_name='Pat',
        last_name='Valid',
        phone_number='1234567890'
    )
    try:
        valid_patient.clean()
        print("PASS: Valid Patient validation successful")
    except ValidationError as e:
        print(f"FAIL: Valid Patient raised error: {e}")

if __name__ == "__main__":
    test_validation()
