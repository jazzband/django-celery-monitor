# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from sphinx_celery import conf

globals().update(conf.build_config(
    'django_celery_monitor', __file__,
    project='django_celery_monitor',
    version_dev='1.1.0',
    version_stable='1.0.2',
    canonical_url='http://django-celery-monitor.readthedocs.io',
    webdomain='',
    github_project='jezdez/django-celery-monitor',
    copyright='2009-2017',
    django_settings='proj.settings',
    include_intersphinx={'python', 'sphinx', 'django', 'celery'},
    path_additions=[os.path.join(os.pardir, 'tests')],
    extra_extensions=['sphinx.ext.napoleon'],
    html_logo='images/logo.png',
    html_favicon='images/favicon.ico',
    html_prepend_sidebars=[],
    apicheck_ignore_modules=[
        'django_celery_monitor',
        'django_celery_monitor.apps',
        'django_celery_monitor.admin',
        r'django_celery_monitor.migrations.*',
    ],
    suppress_warnings=['image.nonlocal_uri'],
))
