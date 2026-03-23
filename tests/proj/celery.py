import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.proj.settings")

app = Celery("tests.proj")

# Using a string here means the worker doesn't have to serialize
# the configuration object.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
