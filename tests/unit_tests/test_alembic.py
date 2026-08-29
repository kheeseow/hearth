import pathlib

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from pydantic import BaseModel

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


class AlembicMigration(BaseModel):
    path: pathlib.Path
    revision: str | None = None
    down_revision: str | None = None


def test_alembic_revisions_are_in_order() -> None:
    # read all files
    paths = sorted(ALEMBIC_MIGRATIONS.glob("*.py"))

    # convert to sorted list of AlembicMigration
    migrations: list[AlembicMigration] = []

    for path in paths:
        mod = import_file("alembic_version", path)

        revision = getattr(mod, "revision", None)
        down_revision = getattr(mod, "down_revision", None)

        migrations.append(
            AlembicMigration(
                path=path,
                revision=revision,
                down_revision=down_revision,
            )
        )

    # step through each migration and check
    #   - revision is in order
    #   - down_revision is in order
    #   - down_revision is the previous revision
    last = None
    for migration in migrations:
        if last is not None:
            assert last.revision == migration.down_revision, (
                f"{last.revision} != {migration.down_revision} for {migration.path}"
            )

        last = migration
        last = migration


@pytest.mark.parametrize("existing_users", [0, 1], ids=["fresh Hearth", "upgraded Mealie"])
def test_app_capability_migration_preserves_installation_profile(existing_users: int) -> None:
    migration_path = next(ALEMBIC_MIGRATIONS.glob("*add_app_capabilities.py"))
    migration = import_file("app_capability_migration", migration_path)
    engine = sa.create_engine("sqlite://")

    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
        if existing_users:
            connection.execute(sa.text("INSERT INTO users (id) VALUES (1)"))

        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()

        capabilities = connection.execute(sa.text("SELECT * FROM app_capabilities WHERE id = 1")).mappings().one()

    legacy_features = bool(existing_users)
    assert capabilities["guides"] is True or capabilities["guides"] == 1
    assert bool(capabilities["legacy_recipes"]) is legacy_features
    assert bool(capabilities["meal_planning"]) is legacy_features
    assert bool(capabilities["shopping_lists"]) is legacy_features
    assert bool(capabilities["nutrition"]) is legacy_features


def test_guide_notifier_event_migration_is_reversible() -> None:
    migration_path = next(ALEMBIC_MIGRATIONS.glob("*add_guide_notifier_events.py"))
    migration = import_file("guide_notifier_event_migration", migration_path)
    engine = sa.create_engine("sqlite://")

    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE group_events_notifier_options (id INTEGER PRIMARY KEY)"))
        connection.execute(sa.text("INSERT INTO group_events_notifier_options (id) VALUES (1)"))

        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()

        columns = {column["name"] for column in sa.inspect(connection).get_columns("group_events_notifier_options")}
        assert {"guide_created", "guide_updated", "guide_deleted"} <= columns
        options = (
            connection.execute(sa.text("SELECT * FROM group_events_notifier_options WHERE id = 1")).mappings().one()
        )
        assert not options["guide_created"]
        assert not options["guide_updated"]
        assert not options["guide_deleted"]

        with Operations.context(context):
            migration.downgrade()

        columns = {column["name"] for column in sa.inspect(connection).get_columns("group_events_notifier_options")}
        assert columns == {"id"}
