import logging
from itertools import count
from mock import patch
from time import time

import pytest

from celery.events import Event as _Event
from celery.events.state import State, Task
from celery.utils import gen_unique_id
from kombu import Exchange, Queue

from django_celery_monitor import cloudwatch_camera


class test_Metrics:
    def test_init(self):
        metric_object = cloudwatch_camera.Metric(
            name="SomeMetric",
            unit="Count",
            value=5,
        )
        assert metric_object.name == "SomeMetric"
        assert metric_object.unit == "Count"
        assert metric_object.value == 5
        assert metric_object.dimensions == {}

    def test_serialize(self):
        metric_object = cloudwatch_camera.Metric(
            name="SomeMetric",
            unit="Count",
            value=5,
        )
        serialized = metric_object.serialize()
        expected = {
            "MetricName": "SomeMetric",
            "Unit": "Count",
            "Value": 5,
        }
        assert serialized == expected

    def test_serialize_dimensions(self):
        metric_object = cloudwatch_camera.Metric(
            name="AnotherMetric",
            unit="Count",
            value=10,
            dimensions={
                "SomeKey": "Value",
            }
        )
        serialized = metric_object.serialize()
        expected = {
            "MetricName": "AnotherMetric",
            "Unit": "Count",
            "Value": 10,
            "Dimensions": [
                {
                    "Name": "SomeKey",
                    "Value": "Value",
                }
            ]
        }
        assert serialized == expected


@pytest.mark.usefixtures('depends_on_current_app')
class test_MetricsContainer:
    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        self.app = app
        self.app.add_defaults({
            "cloudwatch_metrics_enabled": False,
        })
        self.state = State()
        self.state.app = self.app

    def test_add(self):
        metrics_container = cloudwatch_camera.MetricsContainer(self.state)
        assert metrics_container._metrics == []
        metrics_container.add(
            cloudwatch_camera.Metric(
                name="TestMetric", unit="SomeUnit", value=12
            )
        )
        assert len(metrics_container._metrics) == 1

    def test_container_methods(self):
        metrics_container = cloudwatch_camera.MetricsContainer(self.state)
        assert len(metrics_container) == 0

        example_metric = cloudwatch_camera.Metric(
            name="TestMetric", unit="SomeUnit", value=12
        )
        metrics_container.add(example_metric)
        assert example_metric in metrics_container
        assert len(metrics_container) == 1
        for metric in metrics_container:
            assert isinstance(metric, cloudwatch_camera.Metric)


_ids = count(0)
_clock = count(1)


def Event(*args, **kwargs):
    kwargs.setdefault('clock', next(_clock))
    kwargs.setdefault('local_received', time())
    return _Event(*args, **kwargs)


@pytest.mark.django_db
@pytest.mark.usefixtures('depends_on_current_app')
class test_CloudwatchCamera:
    Camera = cloudwatch_camera.CloudwatchCamera

    def create_task(self, worker, **kwargs):
        d = dict(uuid=gen_unique_id(),
                 name='django_celery_monitor.test.task{0}'.format(next(_ids)),
                 worker=worker)
        return Task(**dict(d, **kwargs))

    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        self.app = app
        self.app.add_defaults({
            "cloudwatch_metrics_enabled": False,
            "CELERY_QUEUES": (
                Queue(
                    "default",
                    Exchange("default"),
                    routing_key="default",
                ),
            )

        })
        self.state = State()
        self.state.app = self.app
        self.cam = self.Camera(self.state)

    def test_on_shutter(self, caplog):
        state = self.state
        cam = self.cam

        ws = ['worker1.ex.com', 'worker2.ex.com', 'worker3.ex.com']
        uus = [gen_unique_id() for i in range(50)]

        events = [Event('worker-online', hostname=ws[0]),
                  Event('worker-online', hostname=ws[1]),
                  Event('worker-online', hostname=ws[2]),
                  Event('task-received',
                        uuid=uus[0], name='A', hostname=ws[0]),
                  Event('task-started',
                        uuid=uus[0], name='A', hostname=ws[0]),
                  Event('task-received',
                        uuid=uus[1], name='B', hostname=ws[1]),
                  Event('task-revoked',
                        uuid=uus[2], name='C', hostname=ws[2])]

        for event in events:
            event['local_received'] = time()
            state.event(event)
        with patch(
            "django_celery_monitor.cloudwatch_camera."
            "MetricsContainer._check_queue"
        ) as mocked_check_queue:
            mocked_check_queue.return_value = 2
            with caplog.at_level(logging.DEBUG):
                cam.on_shutter(state)
                assert "QueueWaitingTasks" in caplog.text
                assert "default" in caplog.text
                assert "'Value': 2" in caplog.text
