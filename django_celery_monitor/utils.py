"""Utilities."""
# -- XXX This module must not use translation as that causes
# -- a recursive loader import!
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.conf import settings
from django.utils import timezone

# see Issue celery/django-celery#222
now_localtime = getattr(timezone, 'template_localtime', timezone.localtime)


def now():
    """Return the current date and time."""
    if getattr(settings, 'USE_TZ', False):
        return now_localtime(timezone.now())
    else:
        return timezone.now()


def make_aware(value):
    """Make the given datetime aware of a timezone."""
    if settings.USE_TZ:
        # naive datetimes are assumed to be in UTC.
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        # then convert to the Django configured timezone.
        default_tz = timezone.get_default_timezone()
        value = timezone.localtime(value, default_tz)
    return value


def correct_awareness(value):
    """Fix the given datetime timezone awareness."""
    if isinstance(value, datetime):
        if settings.USE_TZ:
            return make_aware(value)
        elif timezone.is_aware(value):
            default_tz = timezone.get_default_timezone()
            return timezone.make_naive(value, default_tz)
    return value


def fromtimestamp(value):
    """Return an aware or naive datetime from the given timestamp."""
    if settings.USE_TZ:
        return make_aware(datetime.utcfromtimestamp(value))
    else:
        return datetime.fromtimestamp(value)
