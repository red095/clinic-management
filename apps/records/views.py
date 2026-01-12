from django.views.generic import CreateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied, ValidationError
from apps.core.mixins import DoctorRequiredMixin
from apps.appointments.models import Appointment
from .models import MedicalRecord
from .forms import MedicalRecordForm

class CreateMedicalRecordView(DoctorRequiredMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'records/create_record.html'
    success_url = reverse_lazy('doctor_dashboard')

    def dispatch(self, request, *args, **kwargs):
        self.appointment = get_object_or_404(Appointment, pk=self.kwargs['appointment_id'])
        
        # Verify Doctor Ownership
        if self.appointment.doctor != request.user:
            raise PermissionDenied("You can only create records for your own appointments.")
            
        # Verify Appointment Status
        if self.appointment.status != Appointment.STATUS_COMPLETED:
             # Ideally show a message, but for now redirect or 403
             # Redirecting prevents crash if user navigates via history
             return redirect('doctor_dashboard')
             
        # Check if record already exists
        if hasattr(self.appointment, 'medical_record'):
             return redirect('doctor_dashboard')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.appointment = self.appointment
        form.instance.patient = self.appointment.patient
        form.instance.doctor = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['appointment'] = self.appointment
        return context

from django.views.generic import DetailView

class MedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = 'records/detail.html'
    context_object_name = 'record'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_viewable_by(self.request.user):
            raise PermissionDenied("You do not have permission to view this record.")
        return obj
