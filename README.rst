============================
Celery Monitoring for Django
============================

:Version: 1.1.2
:Web: https://django-celery-monitor.readthedocs.io/
:Download: https://pypi.python.org/pypi/django_celery_monitor
:Source: https://github.com/jezdez/django-celery-monitor
:Keywords: django, celery, events, monitoring

|build-status| |coverage| |license| |wheel| |pyversion| |pyimp|

About
=====

This extension enables you to monitor Celery tasks and workers.

It defines two models (``django_celery_monitor.models.WorkerState`` and
``django_celery_monitor.models.TaskState``) used to store worker and task states
and you can query this database table like any other Django model.
It provides a Camera class (``django_celery_monitor.camera.Camera``) to be
used with the Celery events command line tool to automatically populate the
two models with the current state of the Celery workers and tasks.

History
=======

This package is a Celery 4 compatible port of the Django admin based
monitoring feature that was included in the old
`django-celery <https://pypi.python.org/pypi/django-celery>`_ package which
is only compatible with Celery < 4.0.
Other parts of django-celery were released as
`django-celery-beat <https://pypi.python.org/pypi/django_celery_beat>`_
(Database-backed Periodic Tasks) and
`django-celery-results <https://pypi.python.org/pypi/django_celery_results>`_
(Celery result backends for Django).

Installation
============

You can install django_celery_monitor either via the Python Package Index (PyPI)
or from source.

To install using `pip`,:

.. code-block:: console

    $ pip install -U django_celery_monitor

Usage
=====

To use this with your project you need to follow these steps:

#. Install the django_celery_monitor library:

   .. code-block:: console

      $ pip install django_celery_monitor

#. Add ``django_celery_monitor`` to ``INSTALLED_APPS`` in your
   Django project's ``settings.py``::

    INSTALLED_APPS = (
        ...,
        'django_celery_monitor',
    )

   Note that there is no dash in the module name, only underscores.

#. Create the Celery database tables by performing a database migrations:

   .. code-block:: console

      $ python manage.py migrate celery_monitor

#. Go to the Django admin of your site and look for the "Celery Monitor"
   section.

Starting the monitoring process
===============================

To enable taking snapshots of the current state of tasks and workers you'll
want to run the Celery events command with the appropriate camera class
``django_celery_monitor.camera.Camera``:

.. code-block:: console

    $ celery -A proj events -l info --camera django_celery_monitor.camera.Camera --frequency=2.0

For a complete listing of the command-line options available see:

.. code-block:: console

    $ celery events --help

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
    :target: http://pypi.python.org/pypi/django_celery_monitor/

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/django-celery-monitor.svg
    :alt: Supported Python versions.
    :target: http://pypi.python.org/pypi/django_celery_monitor/

.. |pyimp| image:: https://img.shields.io/pypi/implementation/django-celery-monitor.svg
    :alt: Support Python implementations.
    :target: http://pypi.python.org/pypi/django_celery_monitor/

