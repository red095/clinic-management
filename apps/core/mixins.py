from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin

class PatientRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a patient."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_patient:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class DoctorRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is a doctor."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_doctor:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an admin."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_admin and not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
