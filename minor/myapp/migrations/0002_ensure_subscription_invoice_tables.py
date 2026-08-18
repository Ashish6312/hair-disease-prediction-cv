from django.db import migrations


def create_tables_if_missing(apps, schema_editor):
    """
    0001_initial was hand-rewritten in commit 07da9f3 to fold two later
    migrations (0002_delete_user, 0003_initial — since deleted) into a
    single squashed file. Django's migration tracking is by (app, name)
    pair, not content hash: production's django_migrations table already
    had a row for "myapp.0001_initial" from before the rewrite, so
    `migrate` saw it as already-applied and skipped it — meaning the
    Subscription/Invoice tables this rewritten file declares never
    actually got created in production, even though Django's migration
    *state* (and the ORM) believe they exist. Every query touching
    request.user.subscription then raises a raw
    `relation "myapp_subscription" does not exist` ProgrammingError,
    surfacing as a 500 on login, profile, and check-auth.

    Fix forward without knowing production's exact current state: create
    each table via the real schema editor (so the DDL exactly matches
    what CreateModel would have produced) only if it isn't already there.
    Idempotent either way — safe whether this table is fully missing or
    was already created by some other path.
    """
    existing_tables = set(schema_editor.connection.introspection.table_names())

    Subscription = apps.get_model('myapp', 'Subscription')
    if Subscription._meta.db_table not in existing_tables:
        schema_editor.create_model(Subscription)

    Invoice = apps.get_model('myapp', 'Invoice')
    if Invoice._meta.db_table not in existing_tables:
        schema_editor.create_model(Invoice)


def noop_reverse(apps, schema_editor):
    # Deliberately not dropping tables on reverse — this migration only
    # ever fills in a gap left by a previous history rewrite; reversing it
    # should not destroy real subscription/invoice data.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_tables_if_missing, noop_reverse),
    ]
