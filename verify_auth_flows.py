
import os
import django
from django.test import Client
from django.urls import reverse


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from apps.accounts.models import User

def verify_auth():
    print("Verifying Authentication Flows...\n")
    client = Client()

    # 1. Test Patient Registration
    print("1. Testing Patient Registration")
    register_url = reverse('register')
    
    # Valid Data
    valid_data = {
        'email': 'new_patient@test.com',
        'first_name': 'New',
        'last_name': 'Patient',
        'phone_number': '555-0123',
        'date_of_birth': '1990-01-01',
        'address': '123 Test St',
        'gender': 'Male',
        'password1': 'StrongPassword123!',
        'password2': 'StrongPassword123!',
    }
    
    # Post request
    response = client.post(register_url, {
        'email': 'post_patient@test.com',
        'first_name': 'Post',
        'last_name': 'Patient',
        'phone_number': '555-0199',
        'date_of_birth': '1995-01-01',
        'address': '456 Web St',
        'gender': 'Female',
        'password1': 'StrongPassword123!',
        'password2': 'StrongPassword123!',
    })
    
    if response.status_code == 302:
        print("PASS: Registration redirected (Success)")
        # Verify User Created
        user = User.objects.get(email='post_patient@test.com')
        print(f"PASS: User created with role: {user.role}")
        if user.role != 'patient':
             print("FAIL: Role is not patient!")
    else:
        print(f"FAIL: Registration failed with status {response.status_code}")
        # Print form errors from context if available
        if 'form' in response.context:
            print(f"Errors: {response.context['form'].errors}")

    # 2. Test Login
    print("\n2. Testing Login")
    login_url = reverse('login')
    response = client.post(login_url, {
        'username': 'post_patient@test.com', # LoginView uses 'username' field to look up USERNAME_FIELD
        'password': 'StrongPassword123!'
    })
    
    if response.status_code == 302:
        print("PASS: Login redirected (Success)")
    else:
        print(f"FAIL: Login failed with status {response.status_code}")
        if 'form' in response.context:
             print(f"Errors: {response.context['form'].errors}")

    # Cleanup
    User.objects.filter(email__in=['new_patient@test.com', 'post_patient@test.com']).delete()

if __name__ == "__main__":
    verify_auth()
