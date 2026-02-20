from rest_framework import serializers
from apps.appointments.services import book_appointment
from apps.appointments.models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'scheduled_time', 'status', 'reason_for_visit',
            'created_at', 'updated_at', 'cancellation_reason'
        ]
        read_only_fields = ['id', 'patient', 'status', 'created_at', 'updated_at', 'cancelled_by', 'cancellation_reason']

    def create(self, validated_data):
        request = self.context.get('request')
        patient = request.user
        
        # If user is not patient, they might be admin booking for someone? 
        # For now assuming current user is patient as per requirement "Make patient read-only if role is patient"
        # If we allow doctors to book for patients, we'd need more logic.
        # But `book_appointment` service takes patient as arg.
        
        return book_appointment(
            patient=patient,
            doctor=validated_data['doctor'],
            scheduled_time=validated_data['scheduled_time'],
            reason_for_visit=validated_data.get('reason_for_visit', '')
        )
