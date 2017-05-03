.. _changelog:

================
 Change history
================

.. _version-1.0.1:

:release-date: 2017-05-03 10:17 a.m. UTC+2
:release-by: Jannis Leidel

- Fix the Python package manifest.

- Fix README rendering.

.. _version-1.0.0:

1.0.0
=====
:release-date: 2017-05-03 08:35 a.m. UTC+2
:release-by: Jannis Leidel

- Initial release by extracting the monitor code from the old django-celery app.

- Add ability to override the expiry timedelta for the task monitor via the
  Celery configuration.

- Add Python 3.6 and Django 1.11 to text matrix. Supported versions of Django
  1.8 LTS, 1.9, 1.10 and 1.11 LTS. Supported versions of Python are 2.7, 3.4,
  3.5 and 3.6 (for Django 1.11).
