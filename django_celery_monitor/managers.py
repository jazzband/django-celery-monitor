"""The model managers."""
from __future__ import absolute_import, unicode_literals
from datetime import timedelta

from celery import states
from celery.events.state import Task
from celery.utils.time import maybe_timedelta
from django.db import models, router, transaction
from django.utils import timezone

from .utils import Now


class ExtendedQuerySet(models.QuerySet):
    """A custom model queryset that implements a few helpful methods."""

    def select_for_update_or_create(self, defaults=None, **kwargs):
        """Extend update_or_create with select_for_update.

        Look up an object with the given kwargs, updating one with defaults
        if it exists, otherwise create a new one.
        Return a tuple (object, created), where created is a boolean
        specifying whether an object was created.

        This is a backport from Django 1.11
        (https://code.djangoproject.com/ticket/26804) to support
        select_for_update when getting the object.
        """
        defaults = defaults or {}
        lookup, params = self._extract_model_params(defaults, **kwargs)
        self._for_write = True
        with transaction.atomic(using=self.db):
            try:
                obj = self.select_for_update().get(**lookup)
            except self.model.DoesNotExist:
                obj, created = self._create_object_from_params(lookup, params)
                if created:
                    return obj, created
            for k, v in defaults.items():
                setattr(obj, k, v() if callable(v) else v)
            obj.save(using=self.db)
        return obj, False


class WorkerStateQuerySet(ExtendedQuerySet):
    """A custom model queryset for the WorkerState model with some helpers."""

    def update_heartbeat(self, hostname, heartbeat, update_freq):
        with transaction.atomic():
            # check if there was an update in the last n seconds?
            interval = timezone.now() - timedelta(seconds=update_freq)
            recent_worker_updates = self.filter(
                hostname=hostname,
                last_update__gte=interval,
            )
            if recent_worker_updates.exists():
                # if yes, get the latest update and move on
                obj = recent_worker_updates.get()
            else:
                # if no, update the worker state and move on
                obj, _ = self.select_for_update_or_create(
                    hostname=hostname,
                    defaults={'last_heartbeat': heartbeat},
                )
        return obj


class TaskStateQuerySet(ExtendedQuerySet):
    """A custom model queryset for the TaskState model with some helpers."""

    def active(self):
        """Return all active task states."""
        return self.filter(hidden=False)

    def expired(self, states, expires):
        """Return all expired task states."""
        return self.filter(
            state__in=states,
            tstamp__lte=Now() - maybe_timedelta(expires),
        )

    def expire_by_states(self, states, expires):
        """Expire task with one of the given states."""
        if expires is not None:
            return self.expired(states, expires).update(hidden=True)

    def purge(self):
        """Purge all expired task states."""
        with transaction.atomic():
            self.using(
                router.db_for_write(self.model)
            ).filter(hidden=True).delete()

    def update_state(self, state, task_id, defaults):
        with transaction.atomic():
            obj, created = self.select_for_update_or_create(
                task_id=task_id,
                defaults=defaults,
            )
            if created:
                return obj

            if states.state(state) < states.state(obj.state):
                keep = Task.merge_rules[states.RECEIVED]
            else:
                keep = {}
            for key, value in defaults.items():
                if key not in keep:
                    setattr(obj, key, value)
            obj.save(update_fields=tuple(defaults.keys()))
            return obj
