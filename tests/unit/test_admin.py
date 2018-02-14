from __future__ import absolute_import, unicode_literals

from datetime import datetime
from unittest import TestCase
from mock import Mock

from freezegun import freeze_time

from django_celery_monitor.admin import colored_state, node_state, eta,\
    tstamp, name


class ColoredStateTest(TestCase):
    def test_success(self):
        """Rendering of a sucessful task's state."""
        mock_task = Mock()
        mock_task.state = 'SUCCESS'
        expected_html = '<b><span style="color: green;">SUCCESS</span></b>'
        assert colored_state(mock_task) == expected_html


class NodeStateTest(TestCase):
    def test_online(self):
        """Rendering of an online node's state."""
        mock_node = Mock()
        mock_node.is_alive.return_value = True
        expected_html = '<b><span style="color: green;">ONLINE</span></b>'
        assert node_state(mock_node) == expected_html


class ETATest(TestCase):
    def test_eta_value_not_set(self):
        """Rendering when no ETA is specified by the task."""
        mock_task = Mock()
        mock_task.eta = None
        expected_html = '<span style="color: gray;">none</span>'
        assert eta(mock_task) == expected_html

    def test_eta_value_set(self):
        """Rendering when an ETA value is set by the task."""
        mock_task = Mock()
        mock_task.eta = datetime(2020, 1, 2, 8, 35)
        expected_html = '2020-01-02 08:35:00+00:00'
        assert eta(mock_task) == expected_html


class TStampTest(TestCase):
    def test_time_difference_of_roughly_two_years(self):
        """Timestamp is roughly two years into the past."""
        mock_task = Mock()
        mock_task.tstamp = datetime(2015, 8, 5, 17, 3)
        expected_html = '<div title="2015-08-05 17:03:00+00:00">2 years ago' \
                        '</div>'
        with freeze_time(datetime(2017, 8, 6)):
            assert tstamp(mock_task) == expected_html


class NameTest(TestCase):
    def test_no_more_than_16_characters(self):
        """
        No truncation should happen on names that are at most 16 characters in
        length.
        """
        mock_task = Mock()
        mock_task.name = '1234567890123456'
        expected_html = '<div title="1234567890123456"><b>1234567890123456' \
                        '</b></div>'
        assert name(mock_task) == expected_html

    def test_more_than_16_characters(self):
        """Truncation should happen above 16 characters."""
        mock_task = Mock()
        mock_task.name = '12345678901234567'
        expected_html = '<div title="12345678901234567"><b>123456789012345' \
                        '&hellip;</b></div>'
        assert name(mock_task) == expected_html
