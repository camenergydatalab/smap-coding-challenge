from django.utils import timezone


def get_local_time():
    return timezone.localtime(timezone.now())
