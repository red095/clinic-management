from django.views.generic import CreateView
from django.urls import reverse_lazy
from apps.core.mixins import PatientRequiredMixin
from .models import Appointment
from .forms import AppointmentBookingForm

class BookAppointmentView(PatientRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentBookingForm
    template_name = 'appointments/book.html'
    success_url = reverse_lazy('patient_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Patient is already set in form __init__
        form.instance.status = Appointment.STATUS_PENDING
        return super().form_valid(form)

from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from apps.core.mixins import DoctorRequiredMixin

class AppointmentActionView(DoctorRequiredMixin, View):
    def post(self, request, pk, action):
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Verify Ownership
        if not appointment.is_accessible_by(request.user):
            raise PermissionDenied
            
        if action == 'confirm':
            if appointment.status == Appointment.STATUS_PENDING:
                appointment.status = Appointment.STATUS_CONFIRMED
                appointment.save()
        elif action == 'cancel':
            if appointment.can_be_cancelled():
                appointment.status = Appointment.STATUS_CANCELLED
                appointment.cancelled_by = request.user
                appointment.cancellation_reason = "Cancelled by doctor"
                appointment.save()
        elif action == 'complete':
            if appointment.can_be_completed():
                appointment.status = Appointment.STATUS_COMPLETED
                appointment.save()
        
        return redirect('doctor_dashboard')
