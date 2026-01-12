from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('admin', 'Admin')
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    speciality = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    
    objects = CustomUserManager()
    
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
        
    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        
        if self.role == 'doctor' and not self.license_number:
            raise ValidationError({'license_number': 'Doctors must have a license number.'})
            
        if self.role == 'patient' and not self.phone_number:
            raise ValidationError({'phone_number': 'Patients must have a phone number.'})

    @property
    def is_doctor(self):
        return self.role == 'doctor'

    @property
    def is_patient(self):
        return self.role == 'patient'

    @property
    def is_admin(self):
        return self.role == 'admin'
    