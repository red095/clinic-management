from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AnalyticsOverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        
        # 1. Appointments Today
        appointments_today = Appointment.objects.filter(
            scheduled_time__date=today
        ).count()

        # 2. Total Patients
        total_patients = User.objects.filter(role='patient').count()

        # 3. Doctor Workload (Top 5 doctors by confirmed appointments)
        doctor_workload = Appointment.objects.filter(
            status=Appointment.STATUS_CONFIRMED
        ).values(
            doctor_name=F('doctor__email')
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # 4. Status Breakdown
        status_breakdown = Appointment.objects.values('status').annotate(count=Count('id'))

        data = {
            'appointments_today': appointments_today,
            'total_patients': total_patients,
            'doctor_workload': doctor_workload,
            'status_breakdown': status_breakdown,
        }
        return Response(data)
