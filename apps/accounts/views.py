from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import PatientRegistrationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'doctor':
            return reverse_lazy('doctor_dashboard')
        elif user.role == 'patient':
            return reverse_lazy('patient_dashboard')
        elif user.role == 'admin': # Assuming admin role string is 'admin' OR is_staff/superuser check
             # If using django admin, maybe redirect there?
             # For now, let's redirect to admin site if role is admin
             return '/admin/'
        return reverse_lazy('home')

def register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect based on role (patient)
            return redirect('patient_dashboard') 
    else:
        form = PatientRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
