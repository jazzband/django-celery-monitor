"""The Cloudwatch Celery events camera."""
from __future__ import absolute_import, unicode_literals

from django_celery_monitor.camera import Camera

from celery.utils.log import get_logger


logger = get_logger(__name__)


try:
    import boto3
except ImportError:
    raise ImportError(
        "cloudwatch_camera module requires boto3 library, install it via "
        "django-celery-monitor[boto3]."
    )


class Metric:
    """Single record of cloudwatch metrics."""

    def __init__(
            self, name, unit=None, value=None, dimensions=None):
        self.name = name
        self.unit = unit
        self.value = value
        self.dimensions = dimensions or {}

    def serialize(self):
        """Serialize metric data to cloudwatch format, return json."""
        metric_data = {
            "MetricName": self.name,
            "Unit": self.unit,
            "Value": self.value,
        }
        if self.dimensions:
            metric_data["Dimensions"] = [
                {
                    "Name": name, "Value": value
                } for name, value in self.dimensions.items()
            ]
        return metric_data


class MetricsContainer:
    """Container for Metric records."""

    def __init__(self, state):
        self.state = state
        self._metrics = []

    def __len__(self):
        return len(self._metrics)

    def __iter__(self):
        return iter(self._metrics)

    def __contains__(self, item):
        return item in self._metrics

    def add(self, metric: Metric):
        """Add Metric object."""
        self._metrics.append(metric)

    def _check_queue(self, connection, queue_name):
        """Return size of the queue by connection and queue_name."""
        channel = connection.channel()
        queue_length = channel.client.llen(queue_name)
        channel.close()
        return queue_length or 0

    def prepare_metrics(self):
        """Gather waiting tasks by queues and worker specific metrics."""
        with self.state.app.pool.acquire(block=False) as connection:
            # waiting in the queue
            for queue in self.state.app.conf.CELERY_QUEUES:
                self.add(
                    Metric(
                        name="QueueWaitingTasks",
                        dimensions={
                            "QueueName": queue.name,
                        },
                        unit="Count",
                        value=self._check_queue(connection, queue.name)
                    )
                )
        # worker specific
        inspect = self.state.app.control.inspect()
        workers_tasks_map = {
            "WorkerActiveTasks": inspect.active() or {},
            "WorkerReservedTasks": inspect.reserved() or {},
            "WorkerScheduledTasks": inspect.scheduled() or {},
            "WorkerRevokedTasks": inspect.revoked() or {},
        }
        for metric, worker_tasks in workers_tasks_map.items():
            for worker, tasks in worker_tasks.items():
                self.add(
                    Metric(
                        name=metric,
                        dimensions={
                            "WorkerName": worker,
                        },
                        unit="Count",
                        value=len(tasks),
                    )
                )
        # completed tasks
        stats = inspect.stats() or {}
        for worker, statistics in stats.items():
            self.add(
                Metric(
                    name="WorkerCompletedTasks",
                    dimensions={
                        "WorkerName": worker,
                    },
                    unit="Count",
                    value=sum(statistics.get("total", {}).values()),
                )
            )


class CloudwatchCamera(Camera):
    """Camera that sends metrics to cloudwatch."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app.add_defaults({
            "cloudwatch_metrics_enabled": False,
            "cloudwatch_metrics_region_name": None,
        })

    def send_metrics(self, state, data):
        """Serialize metrics to json, then send if those are enabled."""
        if state.app.conf.cloudwatch_metrics_enabled:
            cloudwatch_client = boto3.client(
                "cloudwatch",
                region_name=state.app.conf.cloudwatch_metrics_region_name,
            )
            cloudwatch_client.put_metric_data(
                Namespace="Celery",
                MetricData=data,
            )
        else:
            logger.debug(data)

    def on_shutter(self, state):
        """Prepare metrics and send the snapshotted state."""
        metrics = MetricsContainer(state=state)
        metrics.prepare_metrics()
        super().on_shutter(state)
        self.send_metrics(
            state=state,
            data=[metric.serialize() for metric in metrics],
        )
