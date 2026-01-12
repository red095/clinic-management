from django.urls import path
from . import views

urlpatterns = [
    path('create/<uuid:appointment_id>/', views.CreateMedicalRecordView.as_view(), name='create_medical_record'),
    path('<uuid:pk>/', views.MedicalRecordDetailView.as_view(), name='record_detail'),
]
