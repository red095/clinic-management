from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors_json'] = self.get_form().doctors_json
        return context

    def form_valid(self, form):
        # Use service to book appointment
        from .services import book_appointment
        
        # We need to manually call the service instead of letting the form save
        # create_view calls form.save(), so we override this
        try:
             # The form is valid, so cleaned_data is available
             # form.instance is an unsaved Appointment object with data from form
             # We need to extract the data to pass to service
             appointment = book_appointment(
                 patient=self.request.user,
                 doctor=form.cleaned_data['doctor'],
                 scheduled_time=form.cleaned_data['scheduled_time'],
                 reason_for_visit=form.cleaned_data['reason_for_visit']
             )
             # CreateView expects self.object to be set
             self.object = appointment
             return redirect(self.get_success_url())
        except ValidationError as e:
             form.add_error(None, e)
             return self.form_invalid(form)

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
            
        # Use services for actions
        from .services import confirm_appointment, complete_appointment, cancel_appointment
        from django.core.exceptions import ValidationError

        try:
            if action == 'confirm':
                confirm_appointment(appointment, request.user)
            elif action == 'cancel':
                cancel_appointment(appointment, request.user, reason="Cancelled by doctor")
            elif action == 'complete':
                complete_appointment(appointment, request.user)
        except (ValidationError, PermissionDenied):
            # For now, just redirect, avoiding crash. Ideally show message.
            pass
        
        return redirect('doctor_dashboard')
