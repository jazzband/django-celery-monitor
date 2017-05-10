"""Utilities."""
# -- XXX This module must not use translation as that causes
# -- a recursive loader import!
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from pprint import pformat

from django.conf import settings
from django.db.models import DateTimeField, Func
from django.utils import timezone
from django.utils.html import escape

try:
    from django.db.models.functions import Now
except ImportError:

    class Now(Func):
        """A backport of the Now function from Django 1.9.x."""

        template = 'CURRENT_TIMESTAMP'

        def __init__(self, output_field=None, **extra):
            if output_field is None:
                output_field = DateTimeField()
            super(Now, self).__init__(output_field=output_field, **extra)

        def as_postgresql(self, compiler, connection):
            # Postgres' CURRENT_TIMESTAMP means "the time at the start of the
            # transaction". We use STATEMENT_TIMESTAMP to be cross-compatible
            # with other databases.
            self.template = 'STATEMENT_TIMESTAMP()'
            return self.as_sql(compiler, connection)


def make_aware(value):
    """Make the given datetime aware of a timezone."""
    if settings.USE_TZ:
        # naive datetimes are assumed to be in UTC.
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        # then convert to the Django configured timezone.
        default_tz = timezone.get_default_timezone()
        value = timezone.localtime(value, default_tz)
    return value


def correct_awareness(value):
    """Fix the given datetime timezone awareness."""
    if isinstance(value, datetime):
        if settings.USE_TZ:
            return make_aware(value)
        elif timezone.is_aware(value):
            default_tz = timezone.get_default_timezone()
            return timezone.make_naive(value, default_tz)
    return value


def fromtimestamp(value):
    """Return an aware or naive datetime from the given timestamp."""
    if settings.USE_TZ:
        return make_aware(datetime.utcfromtimestamp(value))
    else:
        return datetime.fromtimestamp(value)


FIXEDWIDTH_STYLE = '''\
<span title="{0}" style="font-size: {1}pt; \
font-family: Menlo, Courier; ">{2}</span> \
'''


def _attrs(**kwargs):
    def _inner(fun):
        for attr_name, attr_value in kwargs.items():
            setattr(fun, attr_name, attr_value)
        return fun
    return _inner


def display_field(short_description, admin_order_field,
                  allow_tags=True, **kwargs):
    """Set some display_field attributes."""
    return _attrs(short_description=short_description,
                  admin_order_field=admin_order_field,
                  allow_tags=allow_tags, **kwargs)


def action(short_description, **kwargs):
    """Set some admin action attributes."""
    return _attrs(short_description=short_description, **kwargs)


def fixedwidth(field, name=None, pt=6, width=16, maxlen=64, pretty=False):
    """Render a field with a fixed width."""
    @display_field(name or field, field)
    def f(task):
        val = getattr(task, field)
        if pretty:
            val = pformat(val, width=width)
        if val.startswith("u'") or val.startswith('u"'):
            val = val[2:-1]
        shortval = val.replace(',', ',\n')
        shortval = shortval.replace('\n', '|br/|')

        if len(shortval) > maxlen:
            shortval = shortval[:maxlen] + '...'
        styled = FIXEDWIDTH_STYLE.format(
            escape(val[:255]), pt, escape(shortval),
        )
        return styled.replace('|br/|', '<br/>')
    return f
