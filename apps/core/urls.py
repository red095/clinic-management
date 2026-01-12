from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('patient-dashboard/', views.PatientDashboardView.as_view(), name='patient_dashboard'),
    path('doctor-dashboard/', views.DoctorDashboardView.as_view(), name='doctor_dashboard'),
]
