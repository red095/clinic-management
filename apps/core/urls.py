from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
]
