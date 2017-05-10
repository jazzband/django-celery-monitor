from django.db.models import DateTimeField, Func

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
