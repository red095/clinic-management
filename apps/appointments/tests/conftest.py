import pytest
from pytest_factoryboy import register
import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from apps.accounts.tests.factories import UserFactory



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
