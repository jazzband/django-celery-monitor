"""The model managers."""
from __future__ import absolute_import, unicode_literals

from celery.utils.time import maybe_timedelta
from django.db import connections, models, router, transaction

from .utils import now


class TaskStateManager(models.Manager):
    """A custom models manager for the TaskState model with some helpers."""

    def connection_for_write(self):
        return connections[router.db_for_write(self.model)]

    def active(self):
        return self.filter(hidden=False)

    def expired(self, states, expires, nowfun=now):
        return self.filter(state__in=states,
                           tstamp__lte=nowfun() - maybe_timedelta(expires))

    def expire_by_states(self, states, expires):
        if expires is not None:
            return self.expired(states, expires).update(hidden=True)

    def purge(self):
        """Purge all expired events."""
        meta = self.model._meta
        with transaction.atomic():
            cursor = self.connection_for_write().cursor()
            cursor.execute(
                'DELETE FROM {0.db_table} WHERE hidden=%s'.format(meta),
                (True, ),
            )
