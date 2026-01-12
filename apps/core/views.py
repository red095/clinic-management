from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def home(request):
    return render(request, 'core/home.html')

@login_required
@user_passes_test(lambda u: u.role == 'patient')
def patient_dashboard(request):
    return render(request, 'core/patient_dashboard.html')

@login_required
@user_passes_test(lambda u: u.role == 'doctor')
def doctor_dashboard(request):
    return render(request, 'core/doctor_dashboard.html')
