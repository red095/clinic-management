from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import PatientRegistrationForm
from .models import User
from apps.core.mixins import AdminRequiredMixin
from django.views.generic import View, TemplateView


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def get_success_url(self):
        user = self.request.user
        # Redirect to password reset if first-time login
        if getattr(user, 'must_reset_password', False):
            return reverse_lazy('set_password')
        if user.role == 'doctor':
            return reverse_lazy('doctor_dashboard')
        elif user.role == 'patient':
            return reverse_lazy('patient_dashboard')
        elif user.is_superuser or user.role == 'admin':
            return reverse_lazy('admin_dashboard')
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


@login_required
def set_password_view(request):
    """Forces a user to reset their OTP password before accessing the system."""
    if not request.user.must_reset_password:
        return redirect('home')

    error = None
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if len(new_password) < 8:
            error = "Password must be at least 8 characters."
        elif new_password != confirm_password:
            error = "Passwords do not match."
        else:
            request.user.set_password(new_password)
            request.user.must_reset_password = False
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep session alive
            messages.success(request, "Password updated successfully!")
            return redirect('doctor_dashboard')

    return render(request, 'accounts/set_password.html', {'error': error})


class AdminCreateDoctorView(AdminRequiredMixin, View):
    """Allows admin to create a doctor account; OTP email is sent automatically."""

    def get(self, request):
        return render(request, 'dashboards/admin_create_doctor.html')

    def post(self, request):
        from .services import create_doctor_with_otp
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        speciality = request.POST.get('speciality', '').strip()
        license_number = request.POST.get('license_number', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not all([email, first_name, last_name, speciality, license_number]):
            messages.error(request, "All fields are required.")
            return render(request, 'dashboards/admin_create_doctor.html', {'post': request.POST})

        try:
            doctor, otp_password = create_doctor_with_otp(
                email=email,
                first_name=first_name,
                last_name=last_name,
                speciality=speciality,
                license_number=license_number,
                phone_number=phone_number,
                created_by=request.user,
            )
            messages.success(
                request,
                "Doctor account created for {}. "
                "Login credentials have been sent to their email.".format(email)
            )
            return redirect('admin_dashboard')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'dashboards/admin_create_doctor.html', {'post': request.POST})

