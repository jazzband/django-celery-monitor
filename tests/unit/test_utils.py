from __future__ import absolute_import, unicode_literals

from re import match
from unittest import TestCase

from mock import Mock

from django_celery_monitor.utils import fixedwidth


class FixedWidthTest(TestCase):
    def test_unpretty_string(self):
        """Do not request pretty printing for a string."""
        task_mock = Mock()
        task_mock.name = 'testing'
        expected_html = '<span title="testing" style="font-size: 6pt; font-' \
                        'family: Menlo, Courier; ">testing</span> '
        assert fixedwidth('name')(task_mock) == expected_html

    def test_pretty_string(self):
        """Request pretty printed value for a string."""
        task_mock = Mock()
        task_mock.name = 'testing'
        expected_html = ('<span title="testing" style="font-size:'
                         ' 6pt; font-family: Menlo, Courier; ">testing'
                         '</span> ')
        assert fixedwidth('name', pretty=True)(task_mock) == expected_html

    def test_pretty_object(self):
        """Request pretty printed value for an object."""
        task_mock = Mock()
        task_mock.name = object()
        actual_html = fixedwidth('name', pretty=True)(task_mock)
        matcher = match(
            '<span title="&lt;object object at 0x[0-9a-f]+&gt;" style="'
            'font-size: 6pt; font-family: Menlo, Courier; ">'
            '&lt;object object at 0x[0-9a-f]+&gt;</span> ',
            actual_html,
        )
        assert matcher
