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

