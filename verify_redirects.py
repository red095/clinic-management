
import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from apps.accounts.models import User

def verify_redirects():
    print("Verifying Auth Redirects...\n")
    client = Client()

    # Create Users if not exist
    patient_email = 'pat_dash@test.com'
    doctor_email = 'doc_dash@test.com'
    admin_email = 'admin_dash@test.com'
    password = 'StrongPassword123!'

    if not User.objects.filter(email=patient_email).exists():
        User.objects.create_user(email=patient_email, password=password, role='patient', first_name='Pat', last_name='Dash')
    if not User.objects.filter(email=doctor_email).exists():
        User.objects.create_user(email=doctor_email, password=password, role='doctor', first_name='Doc', last_name='Dash', license_number='D123')
    if not User.objects.filter(email=admin_email).exists():
        User.objects.create_superuser(email=admin_email, password=password, role='admin', first_name='Adm', last_name='Dash')

    login_url = reverse('login')

    # 1. Test Patient Redirect
    print("1. Testing Patient Login Redirect")
    client.login(email=patient_email, password=password) # Using client.login for session
    # Actually, we want to test the VIEW redirect logic, so we should POST to login view.
    client.logout()
    
    response = client.post(login_url, {'username': patient_email, 'password': password})
    if response.status_code == 302:
        if '/patient-dashboard/' in response.url:
            print("PASS: Patient redirected to /patient-dashboard/")
        else:
            print(f"FAIL: Patient redirected to {response.url}")
    else:
        print(f"FAIL: Login not redirected (Status {response.status_code})")

    # 2. Test Doctor Redirect
    print("\n2. Testing Doctor Login Redirect")
    client.logout()
    response = client.post(login_url, {'username': doctor_email, 'password': password})
    if response.status_code == 302:
        if '/doctor-dashboard/' in response.url:
            print("PASS: Doctor redirected to /doctor-dashboard/")
        else:
            print(f"FAIL: Doctor redirected to {response.url}")
    else:
        print(f"FAIL: Login not redirected (Status {response.status_code})")

    # 3. Test Admin Redirect
    print("\n3. Testing Admin Login Redirect")
    client.logout()
    response = client.post(login_url, {'username': admin_email, 'password': password})
    if response.status_code == 302:
        if '/admin/' in response.url:
            print("PASS: Admin redirected to /admin/")
        else:
            print(f"FAIL: Admin redirected to {response.url}")
    else:
        print(f"FAIL: Login not redirected (Status {response.status_code})")

    # Cleanup
    User.objects.filter(email__in=[patient_email, doctor_email, admin_email]).delete()

if __name__ == "__main__":
    verify_redirects()
