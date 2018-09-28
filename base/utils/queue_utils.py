from django.conf import settings


def get_timeout_or_default(queue_name):
    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        return settings.QUEUES.get("QUEUES_TIMEOUT").get(queue_name)
    return settings.DEFAULT_QUEUE_TIMEOUT
