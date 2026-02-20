from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .appointments.views import PatientAppointmentViewSet, DoctorAppointmentViewSet
from .analytics.views import AnalyticsOverviewView

router = DefaultRouter()
router.register(r'patient/appointments', PatientAppointmentViewSet, basename='patient-appointments')
router.register(r'doctor/appointments', DoctorAppointmentViewSet, basename='doctor-appointments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/analytics/overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
]
