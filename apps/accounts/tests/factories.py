import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'patient'
    phone_number = '+251912345678'
    license_number = factory.LazyAttribute(lambda o: 'LIC-{}'.format(o.email.split('@')[0]) if o.role == 'doctor' else '')
    speciality = factory.LazyAttribute(lambda o: 'General' if o.role == 'doctor' else '')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
