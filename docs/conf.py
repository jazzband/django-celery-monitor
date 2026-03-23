import os

from sphinx_celery import conf

globals().update(
    conf.build_config(
        "django_celery_monitor",
        __file__,
        project="django_celery_monitor",
        version_dev="1.2.0",
        version_stable="1.1.2",
        canonical_url="https://django-celery-monitor.readthedocs.io",
        webdomain="",
        github_project="jazzband/django-celery-monitor",
        copyright="2009-2017",
        django_settings="tests.proj.settings",
        include_intersphinx={"python", "sphinx", "django", "celery"},
        path_additions=[os.path.join(os.pardir, "tests")],
        extra_extensions=["sphinx.ext.napoleon"],
        html_logo="images/logo.png",
        html_favicon="images/favicon.ico",
        html_prepend_sidebars=[],
        apicheck_ignore_modules=[
            "django_celery_monitor",
            "django_celery_monitor.apps",
            "django_celery_monitor.admin",
            r"django_celery_monitor.migrations.*",
        ],
        suppress_warnings=["image.nonlocal_uri"],
    )
)
