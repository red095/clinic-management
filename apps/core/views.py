from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from .mixins import PatientRequiredMixin, DoctorRequiredMixin, AdminRequiredMixin
from apps.appointments.models import Appointment

def home(request):
    return render(request, 'core/home.html')

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = 'dashboards/patient.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch data for dashboard
        user = self.request.user
        context['upcoming_appointments'] = Appointment.objects.filter(
            patient=user, 
            status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
        ).order_by('scheduled_time')
        context['past_appointments'] = Appointment.objects.filter(
            patient=user,
            status__in=[Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED]
        ).order_by('-scheduled_time')
        context['medical_records'] = user.medical_records.all().order_by('-created_at')
        return context

class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'dashboards/doctor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Base queryset
        qs = Appointment.objects.filter(doctor=user)

        context['todays_appointments'] = qs.filter(
            scheduled_time__range=(today_start, today_end),
            status=Appointment.STATUS_CONFIRMED
        ).order_by('scheduled_time')

        context['upcoming_appointments'] = qs.filter(
            scheduled_time__gt=today_end,
            status=Appointment.STATUS_CONFIRMED
        ).order_by('scheduled_time')

        context['pending_appointments'] = qs.filter(
            status=Appointment.STATUS_PENDING,
            scheduled_time__gte=now
        ).order_by('scheduled_time')

        context['completed_appointments'] = qs.filter(
            status=Appointment.STATUS_COMPLETED
        ).order_by('-scheduled_time')[:10] # Limit to recent 10

        return context
