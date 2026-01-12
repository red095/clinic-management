
import os
import django
from django.test import Client, RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.core.mixins import DoctorRequiredMixin, PatientRequiredMixin, AdminRequiredMixin
from django.views import View

# Mock View for Mixin Testing
class MockView(View):
    def get(self, request):
        return "Allowed"

class ProtectedDoctorView(DoctorRequiredMixin, MockView): pass
class ProtectedPatientView(PatientRequiredMixin, MockView): pass
class ProtectedAdminView(AdminRequiredMixin, MockView): pass

def verify_permissions():
    print("Verifying Role-Based Permissions...\n")
    factory = RequestFactory()

    # Create Users
    patient_email = 'perm_pat@test.com'
    doctor_email = 'perm_doc@test.com'
    admin_email = 'perm_adm@test.com'
    password = 'Password123!'

    if not User.objects.filter(email=patient_email).exists():
        User.objects.create_user(email=patient_email, password=password, role='patient', first_name='P', last_name='P', phone_number='123')
    if not User.objects.filter(email=doctor_email).exists():
        User.objects.create_user(email=doctor_email, password=password, role='doctor', first_name='D', last_name='D', license_number='L123')
    if not User.objects.filter(email=admin_email).exists():
        User.objects.create_superuser(email=admin_email, password=password, role='admin', first_name='A', last_name='A')

    patient = User.objects.get(email=patient_email)
    doctor = User.objects.get(email=doctor_email)
    admin = User.objects.get(email=admin_email)

    # 1. Test Helper Methods
    print("1. Testing Model Helper Methods")
    print(f"   Patient is_patient: {patient.is_patient} (Expected: True)")
    print(f"   Doctor is_doctor: {doctor.is_doctor} (Expected: True)")
    print(f"   Admin is_admin: {admin.is_admin} (Expected: True)")
    
    if not (patient.is_patient and doctor.is_doctor and admin.is_admin):
        print("FAIL: Model helpers returned incorrect values")
    else:
        print("PASS: Model helpers verified")

    # 2. Test Mixins
    print("\n2. Testing Access Mixins")

    def check_access(view_cls, user, expected_allowed):
        request = factory.get('/')
        request.user = user
        view = view_cls()
        try:
            view.dispatch(request)
            if expected_allowed:
                return True
            else:
                print(f"FAIL: {user.role} allowed in protected view")
                return False
        except PermissionDenied:
            if not expected_allowed:
                return True
            else:
                print(f"FAIL: {user.role} denied in allowed view")
                return False

    # Doctor View
    if check_access(ProtectedDoctorView, doctor, True) and \
       check_access(ProtectedDoctorView, patient, False):
        print("PASS: DoctorRequiredMixin verified")
    
    # Patient View
    if check_access(ProtectedPatientView, patient, True) and \
       check_access(ProtectedPatientView, doctor, False):
        print("PASS: PatientRequiredMixin verified")

    # Admin View
    if check_access(ProtectedAdminView, admin, True) and \
       check_access(ProtectedAdminView, doctor, False):
        print("PASS: AdminRequiredMixin verified")

    # Cleanup
    User.objects.filter(email__in=[patient_email, doctor_email, admin_email]).delete()

if __name__ == "__main__":
    verify_permissions()
