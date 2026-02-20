import pytest
from pytest_factoryboy import register
import factory
from django.contrib.auth import get_user_model

User = get_user_model()

from apps.accounts.tests.factories import UserFactory

@pytest.fixture
def patient_user(db):
    return UserFactory(role='patient')

@pytest.fixture
def doctor_user(db):
    return UserFactory(role='doctor')

@pytest.fixture
def admin_user(db):
    return UserFactory(role='admin', is_staff=True, is_superuser=True)

register(UserFactory)
