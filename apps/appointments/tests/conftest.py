import pytest
from pytest_factoryboy import register
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')

@pytest.fixture
def patient_user(db):
    return UserFactory(role='patient')

@pytest.fixture
def doctor_user(db):
    return UserFactory(role='doctor')

@pytest.fixture
def another_doctor_user(db):
    return UserFactory(role='doctor')

@pytest.fixture
def future_date():
    return timezone.now() + timedelta(days=1)

@pytest.fixture
def past_date():
    return timezone.now() - timedelta(days=1)

class AppointmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Appointment
    
    patient = factory.SubFactory(UserFactory, role='patient')
    doctor = factory.SubFactory(UserFactory, role='doctor')
    scheduled_time = factory.LazyFunction(lambda: timezone.now() + timedelta(days=2))
    reason_for_visit = "General Checkup"
    status = Appointment.STATUS_PENDING

register(AppointmentFactory)
