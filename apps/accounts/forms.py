from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'date_of_birth', 
            'address', 
            'gender'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'  # Strict enforcement
        if commit:
            user.save()
        return user
