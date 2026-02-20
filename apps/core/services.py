from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def log_action(user, action, instance, metadata=None):
    """
    Logs an action performed by a user on a specific object instance.
    """
    if metadata is None:
        metadata = {}

    content_type = ContentType.objects.get_for_model(instance)
    
    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=str(instance.pk),
        metadata=metadata
    )
