from __future__ import absolute_import, unicode_literals

from datetime import datetime
from itertools import count
from time import time

import pytest

from celery import states
from celery.events import Event as _Event
from celery.events.state import State, Worker, Task
from celery.utils import gen_unique_id

from django.test.utils import override_settings
from django.utils import timezone

from django_celery_monitor import camera, models
from django_celery_monitor.utils import make_aware, now


_ids = count(0)
_clock = count(1)


def Event(*args, **kwargs):
    kwargs.setdefault('clock', next(_clock))
    kwargs.setdefault('local_received', time())
    return _Event(*args, **kwargs)


@pytest.mark.django_db()
@pytest.mark.usefixtures('depends_on_current_app')
class test_Camera:
    Camera = camera.Camera

    def create_task(self, worker, **kwargs):
        d = dict(uuid=gen_unique_id(),
                 name='django_celery_monitor.test.task{0}'.format(next(_ids)),
                 worker=worker)
        return Task(**dict(d, **kwargs))

    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        self.app = app
        self.state = State()
        self.cam = self.Camera(self.state)

    def test_constructor(self):
        cam = self.Camera(State())
        assert cam.state
        assert cam.freq
        assert cam.cleanup_freq
        assert cam.logger

    def test_get_heartbeat(self):
        worker = Worker(hostname='fuzzie')
        assert self.cam.get_heartbeat(worker) is None
        t1 = time()
        t2 = time()
        t3 = time()
        for t in t1, t2, t3:
            worker.event('heartbeat', t, t, {})
        self.state.workers[worker.hostname] = worker
        assert (
            self.cam.get_heartbeat(worker) ==
            make_aware(datetime.fromtimestamp(t3))
        )

    def test_handle_worker(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam._last_worker_write.clear()
        m = self.cam.handle_worker((worker.hostname, worker))
        assert m
        assert m.hostname
        assert m.last_heartbeat
        assert m.is_alive()
        assert str(m) == str(m.hostname)
        assert repr(m)

    def test_handle_task_received(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam.handle_worker((worker.hostname, worker))

        task = self.create_task(worker)
        task.event('received', time(), time(), {})
        assert task.state == states.RECEIVED
        mt = self.cam.handle_task((task.uuid, task))
        assert mt.name == task.name
        assert str(mt)
        assert repr(mt)
        mt.eta = now()
        assert 'eta' in str(mt)
        assert mt in models.TaskState.objects.active()

    def test_handle_task(self):
        worker1 = Worker(hostname='fuzzie')
        worker1.event('online', time(), time(), {})
        mw = self.cam.handle_worker((worker1.hostname, worker1))
        task1 = self.create_task(worker1)
        task1.event('received', time(), time(), {})
        mt = self.cam.handle_task((task1.uuid, task1))
        assert mt.worker == mw

        worker2 = Worker(hostname=None)
        task2 = self.create_task(worker2)
        task2.event('received', time(), time(), {})
        mt = self.cam.handle_task((task2.uuid, task2))
        assert mt.worker is None

        task1.event('succeeded', time(), time(), {'result': 42})
        assert task1.state == states.SUCCESS
        assert task1.result == 42
        mt = self.cam.handle_task((task1.uuid, task1))
        assert mt.name == task1.name
        assert mt.result == 42

        task3 = self.create_task(worker1, name=None)
        task3.event('revoked', time(), time(), {})
        mt = self.cam.handle_task((task3.uuid, task3))
        assert mt is None

    def test_handle_task_timezone(self):
        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        self.cam.handle_worker((worker.hostname, worker))

        tstamp = 1464793200.0  # 2016-06-01T15:00:00Z

        with override_settings(USE_TZ=True, TIME_ZONE='Europe/Helsinki'):
            task = self.create_task(
                worker,
                eta='2016-06-01T15:16:17.654321+00:00',
                expires='2016-07-01T15:16:17.765432+03:00',
            )
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            assert (
                mt.tstamp ==
                datetime(2016, 6, 1, 15, 0, 0, tzinfo=timezone.utc)
            )
            assert (
                mt.eta ==
                datetime(2016, 6, 1, 15, 16, 17, 654321, tzinfo=timezone.utc)
            )
            assert (
                mt.expires ==
                datetime(2016, 7, 1, 12, 16, 17, 765432, tzinfo=timezone.utc)
            )

            task = self.create_task(worker, eta='2016-06-04T15:16:17.654321')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            assert (
                mt.eta ==
                datetime(2016, 6, 4, 15, 16, 17, 654321, tzinfo=timezone.utc)
            )

        with override_settings(USE_TZ=False, TIME_ZONE='Europe/Helsinki'):
            task = self.create_task(
                worker,
                eta='2016-06-01T15:16:17.654321+00:00',
                expires='2016-07-01T15:16:17.765432+03:00',
            )
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            assert mt.tstamp == datetime(2016, 6, 1, 18, 0, 0)
            assert mt.eta == datetime(2016, 6, 1, 18, 16, 17, 654321)
            assert mt.expires == datetime(2016, 7, 1, 15, 16, 17, 765432)

            task = self.create_task(worker, eta='2016-06-04T15:16:17.654321')
            task.event('received', tstamp, tstamp, {})
            mt = self.cam.handle_task((task.uuid, task))
            assert mt.eta == datetime(2016, 6, 4, 15, 16, 17, 654321)

    def assert_expires(self, dec, expired, tasks=10):
        # Cleanup leftovers from previous tests
        self.cam.on_cleanup()

        worker = Worker(hostname='fuzzie')
        worker.event('online', time(), time(), {})
        for total in range(tasks):
            task = self.create_task(worker)
            task.event('received', time() - dec, time() - dec, {})
            task.event('succeeded', time() - dec, time() - dec, {'result': 42})
            assert task.name
            assert self.cam.handle_task((task.uuid, task))
        assert self.cam.on_cleanup() == expired

    def test_on_cleanup_expires(self, dec=332000):
        self.assert_expires(dec, 10)

    def test_on_cleanup_does_not_expire_new(self, dec=0):
        self.assert_expires(dec, 0)

    def test_on_shutter(self):
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
        cam.on_shutter(state)

        for host in ws:
            worker = models.WorkerState.objects.get(hostname=host)
            assert worker.is_alive()

        t1 = models.TaskState.objects.get(task_id=uus[0])
        assert t1.state == states.STARTED
        assert t1.name == 'A'
        t2 = models.TaskState.objects.get(task_id=uus[1])
        assert t2.state == states.RECEIVED
        t3 = models.TaskState.objects.get(task_id=uus[2])
        assert t3.state == states.REVOKED

        events = [Event('task-succeeded',
                        uuid=uus[0], hostname=ws[0], result=42),
                  Event('task-failed',
                        uuid=uus[1], exception="KeyError('foo')",
                        hostname=ws[1]),
                  Event('worker-offline', hostname=ws[0])]
        list(map(state.event, events))
        cam._last_worker_write.clear()
        cam.on_shutter(state)

        w1 = models.WorkerState.objects.get(hostname=ws[0])
        assert not w1.is_alive()

        t1 = models.TaskState.objects.get(task_id=uus[0])
        assert t1.state == states.SUCCESS
        assert t1.result == '42'
        assert t1.worker == w1

        t2 = models.TaskState.objects.get(task_id=uus[1])
        assert t2.state == states.FAILURE
        assert t2.result == "KeyError('foo')"
        assert t2.worker.hostname == ws[1]

        cam.on_shutter(state)
