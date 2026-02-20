import sys
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print(f"sys.path: {sys.path}")

try:
    import apps.appointments
    print("Successfully imported apps.appointments")
    print(f"apps.appointments file: {apps.appointments.__file__}")
except Exception as e:
    print(f"Failed to import apps.appointments: {e}")

from django.apps import apps
print("Installed Apps:")
for app_config in apps.get_app_configs():
    print(f"- {app_config.name} (label: {app_config.label})")
