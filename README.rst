================================================
 Celery Monitor for the Django admin framework.
================================================

|build-status| |coverage| |license| |wheel| |pyversion| |pyimp|

:Version: 1.0.0
:Web: http://django-celery-monitor.readthedocs.io/
:Download: http://pypi.python.org/pypi/django-celery-monitor
:Source: http://github.com/jezdez/django-celery-monitor
:Keywords: django, celery, events, monitoring

About
=====

This extension enables you to monitor Celery tasks and workers.

It defines two models (``django_celery_monitor.models.WorkerState`` and
``django_celery_monitor.models.TaskState``) used to store worker and task states
and you can query this database table like any other Django model.
It provides a Camera class (``django_celery_monitor.camera.Camera``) to be
used with the Celery events command line tool to automatically populate the
two models with the current state of the Celery workers and tasks.

Configuration
=============

There are a few settings that regulate how long the task monitor should keep
state entries in the database. Either of the three should be a
``datetime.timedelta`` value or ``None``.

- ``monitor_task_success_expires`` -- Defaults to ``timedelta(days=1)`` (1 day)

  The period of time to retain monitoring information about tasks with a
  ``SUCCESS`` result.

- ``monitor_task_error_expires`` -- Defaults to ``timedelta(days=3)`` (3 days)

  The period of time to retain monitoring information about tasks with an
  errornous result (one of the following event states: ``RETRY``, ``FAILURE``,
  ``REVOKED``.

- ``monitor_task_pending_expires`` -- Defaults to ``timedelta(days=5)`` (5 days)

  The period of time to retain monitoring information about tasks with a
  pending result (one of the following event states: ``PENDING``, ``RECEIVED``,
  ``STARTED``, ``REJECTED``, ``RETRY``.

In your Celery configuration simply set them to override the defaults, e.g.::

    from datetime import timedelta

    monitor_task_success_expires = timedelta(days=7)

.. _installation:

Installation
============

You can install django-celery-monitor either via the Python Package Index (PyPI)
or from source.

To install using `pip`,::

    $ pip install -U django-celery-monitor

.. _installing-from-source:

Downloading and installing from source
--------------------------------------

Download the latest version of django-celery-monitor from
http://pypi.python.org/pypi/django-celery-monitor

You can install it by doing the following,::

    $ tar xvfz django-celery-monitor-0.0.0.tar.gz
    $ cd django-celery-monitor-0.0.0
    $ python setup.py build
    # python setup.py install

The last command must be executed as a privileged user if
you are not currently using a virtualenv.

.. |build-status| image:: https://secure.travis-ci.org/jezdez/django-celery-monitor.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/jezdez/django-celery-monitor

.. |coverage| image:: https://codecov.io/github/jezdez/django-celery-monitor/coverage.svg?branch=master
    :target: https://codecov.io/github/jezdez/django-celery-monitor?branch=master

.. |license| image:: https://img.shields.io/pypi/l/django-celery-monitor.svg
    :alt: BSD License
    :target: https://opensource.org/licenses/BSD-3-Clause

.. |wheel| image:: https://img.shields.io/pypi/wheel/django-celery-monitor.svg
    :alt: django-celery-monitor can be installed via wheel
    :target: http://pypi.python.org/pypi/django-celery-monitor/

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/django-celery-monitor.svg
    :alt: Supported Python versions.
    :target: http://pypi.python.org/pypi/django-celery-monitor/

.. |pyimp| image:: https://img.shields.io/pypi/implementation/django-celery-monitor.svg
    :alt: Support Python implementations.
    :target: http://pypi.python.org/pypi/django-celery-monitor/

