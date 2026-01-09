
import os
import django
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from datetime import timedelta
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.records.models import MedicalRecord

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
    if not created and user.role != role:
        user.role = role
        user.save()
    return user

def str_err(e):
    if hasattr(e, 'message_dict'):
        return str(e.message_dict)
    return str(e)

def verify_records():
    print("Verifying Medical Record Constraints...\n")

    # Setup Users and Appointments
    doctor = create_user('doc_rec@test.com', 'doctor', license_number='LICREC')
    patient = create_user('pat_rec@test.com', 'patient', phone_number='123456')
    other_patient = create_user('pat_other@test.com', 'patient', phone_number='654321')
    
    # 1. Successful Creation
    print("1. Successful Creation (COMPLETED Appointment)")
    completed_appt = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_time=timezone.now() - timedelta(hours=1),
        status=Appointment.STATUS_COMPLETED,
        reason_for_visit="Checkup"
    )
    
    try:
        record = MedicalRecord(
            patient=patient,
            doctor=doctor,
            appointment=completed_appt,
            diagnosis="Healthy",
            notes="All good."
        )
        record.save()
        print(f"PASS: Created record {record.id}")
    except Exception as e:
        print(f"FAIL: Creation failed: {e}")

    # 2. Status Validation (CONFIRMED Appointment)
    print("\n2. Status Validation (CONFIRMED Appointment)")
    confirmed_appt = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        scheduled_time=timezone.now() + timedelta(days=1),
        status=Appointment.STATUS_CONFIRMED,
        reason_for_visit="Future"
    )
    
    try:
        record = MedicalRecord(
            patient=patient,
            doctor=doctor,
            appointment=confirmed_appt,
            diagnosis="Premature",
            notes="Too early"
        )
        record.full_clean()
        record.save()
        print("FAIL: Allowed record for CONFIRMED appointment")
    except ValidationError as e:
        print(f"PASS: Caught invalid status: {str_err(e)}")

    # 3. Relationship Mismatch
    print("\n3. Relationship Mismatch")
    try:
        record = MedicalRecord(
            patient=other_patient, # Wrong patient
            doctor=doctor,
            appointment=completed_appt, # Linked to 'patient'
            diagnosis="Wrong patient",
            notes="Error"
        )
        record.full_clean()
        print("FAIL: Allowed mismtached patient")
    except ValidationError as e:
        print(f"PASS: Caught mismatch: {str_err(e)}")

    # 4. Immutability - Update
    print("\n4. Immutability - Update Check")
    record_to_edit = MedicalRecord.objects.first()
    try:
        record_to_edit.diagnosis = "Changed Diagnosis"
        record_to_edit.save()
        print("FAIL: Allowed update to existing record")
    except ValidationError as e:
        print(f"PASS: Caught update attempt: {str_err(e)}")

    # 5. Immutability - Delete
    print("\n5. Immutability - Delete Check")
    try:
        record_to_edit.delete()
        print("FAIL: Allowed deletion")
    except PermissionDenied as e:
        print(f"PASS: Caught delete attempt: {e}")

    # 6. Access Control
    print("\n6. Access Control")
    if record_to_edit.is_viewable_by(doctor):
        print("PASS: Doctor can view")
    else:
        print("FAIL: Doctor cannot view")
        
    if record_to_edit.is_viewable_by(patient):
        print("PASS: Patient can view")
    else:
        print("FAIL: Patient cannot view")
        
    if not record_to_edit.is_viewable_by(other_patient):
        print("PASS: Other patient cannot view")
    else:
        print("FAIL: Other patient CAN view (Security Issue)")

    # Cleanup
    Appointment.objects.all().delete()
    if MedicalRecord.objects.all().count() > 0:
         # Need to bypass delete check for cleanup??
         # Since we overrode delete, we might need to use queryset delete?
         # Django querysets generally bypass model.delete() method unless check is in signals or DB constraints.
         # But let's see. logic is in model.delete(). QuerySet.delete() might still work.
         pass
         
    MedicalRecord.objects.all().delete()
    User.objects.filter(email__in=['doc_rec@test.com', 'pat_rec@test.com', 'pat_other@test.com']).delete()

if __name__ == "__main__":
    verify_records()
