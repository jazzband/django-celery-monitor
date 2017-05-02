# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TaskState',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('state', models.CharField(
                    choices=[('FAILURE', 'FAILURE'),
                             ('PENDING', 'PENDING'),
                             ('RECEIVED', 'RECEIVED'),
                             ('RETRY', 'RETRY'),
                             ('REVOKED', 'REVOKED'),
                             ('STARTED', 'STARTED'),
                             ('SUCCESS', 'SUCCESS')],
                    db_index=True,
                    max_length=64,
                    verbose_name='state',
                )),
                ('task_id', models.CharField(
                    max_length=36,
                    unique=True,
                    verbose_name='UUID',
                )),
                ('name', models.CharField(
                    db_index=True,
                    max_length=200,
                    null=True,
                    verbose_name='name',
                )),
                ('tstamp', models.DateTimeField(
                    db_index=True,
                    verbose_name='event received at',
                )),
                ('args', models.TextField(
                    null=True,
                    verbose_name='Arguments',
                )),
                ('kwargs', models.TextField(
                    null=True,
                    verbose_name='Keyword arguments',
                )),
                ('eta', models.DateTimeField(
                    null=True,
                    verbose_name='ETA',
                )),
                ('expires', models.DateTimeField(
                    null=True,
                    verbose_name='expires',
                )),
                ('result', models.TextField(
                    null=True,
                    verbose_name='result',
                )),
                ('traceback', models.TextField(
                    null=True,
                    verbose_name='traceback',
                )),
                ('runtime', models.FloatField(
                    help_text='in seconds if task succeeded',
                    null=True,
                    verbose_name='execution time',
                )),
                ('retries', models.IntegerField(
                    default=0,
                    verbose_name='number of retries',
                )),
                ('hidden', models.BooleanField(
                    db_index=True,
                    default=False,
                    editable=False,
                )),
            ],
            options={
                'ordering': ['-tstamp'],
                'get_latest_by': 'tstamp',
                'verbose_name_plural': 'tasks',
                'verbose_name': 'task',
            },
        ),
        migrations.CreateModel(
            name='WorkerState',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('hostname', models.CharField(
                    max_length=255,
                    unique=True,
                    verbose_name='hostname',
                )),
                ('last_heartbeat', models.DateTimeField(
                    db_index=True,
                    null=True,
                    verbose_name='last heartbeat',
                )),
            ],
            options={
                'ordering': ['-last_heartbeat'],
                'get_latest_by': 'last_heartbeat',
                'verbose_name_plural': 'workers',
                'verbose_name': 'worker',
            },
        ),
        migrations.AddField(
            model_name='taskstate',
            name='worker',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='celery_monitor.WorkerState',
                verbose_name='worker'
            ),
        ),
    ]
