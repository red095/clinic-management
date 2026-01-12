from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import PatientRegistrationForm

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.role == 'doctor':
             return reverse_lazy('doctor_dashboard')
        elif user.role == 'patient':
             return reverse_lazy('patient_dashboard')
        elif user.is_superuser or user.is_staff:
             return '/admin/'
        return reverse_lazy('home')

def register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'patient'
            user.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})
