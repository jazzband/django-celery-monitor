"""Application configuration."""
from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

__all__ = ['CeleryMonitorConfig']


class CeleryMonitorConfig(AppConfig):
    """Default configuration for the django_celery_monitor app."""

    name = 'django_celery_monitor'
    label = 'celery_monitor'
    verbose_name = _('Celery Monitor')
