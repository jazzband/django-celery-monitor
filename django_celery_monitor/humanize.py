"""Some helpers to humanize values."""

from datetime import datetime

from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.utils.translation import ngettext


def pluralize_year(n):
    """Return a string with the number of yeargs ago."""
    return ngettext("{num} year ago", "{num} years ago", n)


def pluralize_month(n):
    """Return a string with the number of months ago."""
    return ngettext("{num} month ago", "{num} months ago", n)


def pluralize_week(n):
    """Return a string with the number of weeks ago."""
    return ngettext("{num} week ago", "{num} weeks ago", n)


def pluralize_day(n):
    """Return a string with the number of days ago."""
    return ngettext("{num} day ago", "{num} days ago", n)


OLDER_CHUNKS = (
    (365.0, pluralize_year),
    (30.0, pluralize_month),
    (7.0, pluralize_week),
    (1.0, pluralize_day),
)


def naturaldate(date, include_seconds=False):
    """Convert datetime into a human natural date string."""
    if not date:
        return ""

    right_now = now()
    today = datetime(
        right_now.year, right_now.month, right_now.day, tzinfo=right_now.tzinfo
    )
    delta = right_now - date
    delta_midnight = today - date

    days = delta.days
    hours = delta.seconds // 3600
    minutes = delta.seconds // 60
    seconds = delta.seconds

    if days < 0:
        return _("just now")

    if days == 0:
        if hours == 0:
            if minutes > 0:
                return ngettext(
                    "{minutes} minute ago",
                    "{minutes} minutes ago",
                    minutes,
                ).format(minutes=minutes)
            else:
                if include_seconds and seconds:
                    return ngettext(
                        "{seconds} second ago",
                        "{seconds} seconds ago",
                        seconds,
                    ).format(seconds=seconds)
                return _("just now")
        else:
            return ngettext(
                "{hours} hour ago",
                "{hours} hours ago",
                hours,
            ).format(hours=hours)

    if delta_midnight.days == 0:
        return _("yesterday at {time}").format(time=date.strftime("%H:%M"))

    count = 0
    for chunk, pluralizefun in OLDER_CHUNKS:
        if days >= chunk:
            count = int(round((delta_midnight.days + 1) / chunk, 0))
            fmt = pluralizefun(count)
            return fmt.format(num=count)
