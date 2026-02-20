import sys
import os

print(f"sys.path: {sys.path}")

try:
    import appointments
    print("WARNING: Imported appointments directly!")
    print(f"File: {appointments.__file__}")
except ImportError:
    print("SUCCESS: Could not import appointments directly.")

try:
    import apps.appointments
    print("Imported apps.appointments")
except ImportError:
    print("Failed to import apps.appointments")
