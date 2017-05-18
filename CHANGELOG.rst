.. _changelog:

================
 Change history
================

.. _version-1.1.2:

:release-date: 2017-05-18 11:30 a.m. UTC+2
:release-by: Jannis Leidel

- More packaging fixes. Sigh.

.. _version-1.1.1:

:release-date: 2017-05-18 10:30 a.m. UTC+2
:release-by: Jannis Leidel

- Fix the folder that the extra stylesheet file was stored in.

.. _version-1.1.0:

:release-date: 2017-05-11 10:25 p.m. UTC+2
:release-by: Jannis Leidel

- Use ``SELECT FOR UPDATE`` SQL statements for updating the task and worker
  states to improve resilliance against race conditions by multiple
  simultaneously running cameras.

- Move worker state cache from in-process dictionary into database side
  timestamp to decide whether to do another worker update or not.

- Improved code structure by moving all utilities into same module.

.. _version-1.0.2:

:release-date: 2017-05-08 16:05 a.m. UTC+2
:release-by: Jannis Leidel

- Import Django models inline to prevent import time side effect.

- Run django.setup() when installing the Camera.

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
