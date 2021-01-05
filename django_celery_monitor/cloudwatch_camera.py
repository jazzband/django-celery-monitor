"""The Cloudwatch Celery events camera."""
from .camera import Camera, logger

try:
    import boto3
except ImportError:
    raise ImportError(
        "cloudwatch_camera module requires boto3 library, install it via "
        "django-celery-monitor[boto3]."
    )


class Metric(object):
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
            'MetricName': self.name,
        }
        if self.unit:
            metric_data['Unit'] = self.unit

        if self.dimensions:
            metric_data['Dimensions'] = [
                {
                    'Name': name, 'Value': value
                } for name, value in self.dimensions.items()
            ]
        metric_data['Value'] = self.value
        return metric_data


class MetricsContainer(object):
    """Container for Metric records."""

    def __init__(self, state):
        self.state = state
        self._metrics = []
        self.cloudwatch_client = boto3.client(
            "cloudwatch",
        ) if self.state.app.conf.cloudwatch_metrics_enabled else None

    def add(self, *args, **kwargs):
        """Add Metric object."""
        self._metrics.append(Metric(*args, **kwargs))

    def prepare_metrics(self):
        """Gather waiting tasks by queues and worker specific metrics."""
        with self.state.app.pool.acquire(block=True) as connection:
            # waiting in the queue
            for queue in self.state.app.conf.CELERY_QUEUES:
                self.add(
                    name="QueueWaitingTasks",
                    dimensions={
                        "QueueName": queue.name,
                    },
                    unit="Count",
                    value=(
                        connection.default_channel.client.llen(queue.name) or 0
                    )
                )
        # worker specific
        inspect = self.state.app.control.inspect()
        workers_tasks_map = {
            "WorkerActiveTasks": inspect.active(),
            "WorkerReservedTasks": inspect.reserved(),
            "WorkerScheduledTasks": inspect.scheduled(),
            "WorkerRevokedTasks": inspect.revoked(),
        }
        for metric, worker_tasks in workers_tasks_map.items():
            for worker, tasks in worker_tasks.items():
                self.add(
                    name=metric,
                    dimensions={
                        "WorkerName": worker,
                    },
                    unit="Count",
                    value=len(tasks),
                )
        # completed tasks
        stats = inspect.stats()
        for worker, statistics in stats.items():
            self.add(
                name="WorkerCompletedTasks",
                dimensions={
                    "WorkerName": worker,
                },
                unit="Count",
                value=sum(statistics.get("total", {}).values()),
            )

    def send(self):
        """Serialize metrics to json, then send if those are enabled."""
        metrics_data = [metric.serialize() for metric in self._metrics]
        if self.cloudwatch_client:
            self.cloudwatch_client.put_metric_data(
                Namespace="Celery",
                MetricData=metrics_data,
            )
        else:
            logger.debug(metrics_data)


class CloudwatchCamera(Camera):
    """Camera that sends metrics to cloudwatch."""

    def __init__(self, *args, **kwargs):
        super(CloudwatchCamera, self).__init__(*args, **kwargs)
        self.app.add_defaults({
            'cloudwatch_metrics_enabled': False,
        })

    def on_shutter(self, state):
        """Prepare metrics and send the snapshotted state."""
        metrics = MetricsContainer(state=state)
        metrics.prepare_metrics()
        super(CloudwatchCamera, self).on_shutter(state)
        metrics.send()
