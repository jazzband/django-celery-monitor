"""The data models for the task and worker states."""
from __future__ import absolute_import, unicode_literals

from time import time, mktime, gmtime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from celery import states
from celery.events.state import heartbeat_expires
from celery.five import python_2_unicode_compatible

from . import managers

ALL_STATES = sorted(states.ALL_STATES)
TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))


@python_2_unicode_compatible
class WorkerState(models.Model):
    """The data model to store the worker state in."""

    #: The hostname of the Celery worker.
    hostname = models.CharField(_('hostname'), max_length=255, unique=True)
    #: A :class:`~datetime.datetime` describing when the worker was last seen.
    last_heartbeat = models.DateTimeField(_('last heartbeat'), null=True,
                                          db_index=True)

    #: A :class:`~django.db.models.Manager` instance
    #: to query the :class:`~django_celery_monitor.models.WorkerState` model.
    objects = models.Manager()

    class Meta:
        """Model meta-data."""

        verbose_name = _('worker')
        verbose_name_plural = _('workers')
        get_latest_by = 'last_heartbeat'
        ordering = ['-last_heartbeat']

    def __str__(self):
        return self.hostname

    def __repr__(self):
        return '<WorkerState: {0.hostname}>'.format(self)

    def is_alive(self):
        """Return whether the worker is currently alive or not."""
        if self.last_heartbeat:
            # Use UTC timestamp if USE_TZ is true, or else use local timestamp
            timestamp = mktime(gmtime()) if settings.USE_TZ else time()
            return timestamp < heartbeat_expires(self.heartbeat_timestamp)
        return False

    @property
    def heartbeat_timestamp(self):
        return mktime(self.last_heartbeat.timetuple())


@python_2_unicode_compatible
class TaskState(models.Model):
    """The data model to store the task state in."""

    #: The :mod:`task state <celery.states>` as returned by Celery.
    state = models.CharField(
        _('state'), max_length=64, choices=TASK_STATE_CHOICES, db_index=True,
    )
    #: The task :func:`UUID <uuid.uuid4>`.
    task_id = models.CharField(_('UUID'), max_length=36, unique=True)
    #: The :ref:`task name <celery:task-names>`.
    name = models.CharField(
        _('name'), max_length=200, null=True, db_index=True,
    )
    #: A :class:`~datetime.datetime` describing when the task was received.
    tstamp = models.DateTimeField(_('event received at'), db_index=True)
    #: The positional :ref:`task arguments <celery:calling-basics>`.
    args = models.TextField(_('Arguments'), null=True)
    #: The keyword :ref:`task arguments <celery:calling-basics>`.
    kwargs = models.TextField(_('Keyword arguments'), null=True)
    #: An optional :class:`~datetime.datetime` describing the
    #: :ref:`ETA <celery:calling-eta>` for its processing.
    eta = models.DateTimeField(_('ETA'), null=True)
    #: An optional :class:`~datetime.datetime` describing when the task
    #: :ref:`expires <celery:calling-expiration>`.
    expires = models.DateTimeField(_('expires'), null=True)
    #: The result of the task.
    result = models.TextField(_('result'), null=True)
    #: The Python error traceback if raised.
    traceback = models.TextField(_('traceback'), null=True)
    #: The task runtime in seconds.
    runtime = models.FloatField(
        _('execution time'), null=True,
        help_text=_('in seconds if task succeeded'),
    )
    #: The number of retries.
    retries = models.IntegerField(_('number of retries'), default=0)
    #: The worker responsible for the execution of the task.
    worker = models.ForeignKey(
        WorkerState, null=True, verbose_name=_('worker'),
        on_delete=models.CASCADE,
    )
    #: Whether the task has been expired and will be purged by the
    #: event framework.
    hidden = models.BooleanField(editable=False, default=False, db_index=True)

    #: A :class:`~django_celery_monitor.managers.TaskStateManager` instance
    #: to query the :class:`~django_celery_monitor.models.TaskState` model.
    objects = managers.TaskStateManager()

    class Meta:
        """Model meta-data."""

        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        get_latest_by = 'tstamp'
        ordering = ['-tstamp']

    def __str__(self):
        name = self.name or 'UNKNOWN'
        s = '{0.state:<10} {0.task_id:<36} {1}'.format(self, name)
        if self.eta:
            s += ' eta:{0.eta}'.format(self)
        return s

    def __repr__(self):
        return '<TaskState: {0.state} {1}[{0.task_id}] ts:{0.tstamp}>'.format(
            self, self.name or 'UNKNOWN',
        )
