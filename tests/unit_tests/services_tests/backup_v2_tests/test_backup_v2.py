import shutil
import statistics
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

import tests.data as test_data
from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models.group import Group
from mealie.db.models.household.cookbook import CookBook
from mealie.db.models.household.household import Household
from mealie.db.models.household.household_to_recipe import HouseholdToRecipe
from mealie.db.models.household.mealplan import GroupMealPlanRules
from mealie.db.models.household.shopping_list import ShoppingList
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.labels import MultiPurposeLabel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.db.models.users.users import User
from mealie.repos.all_repositories import get_repositories
from mealie.schema.guide import GuideSave
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.backups_v2.backup_file import BackupFile
from mealie.services.backups_v2.backup_v2 import BackupV2
from mealie.services.guide import GuideDataService
from tests.utils.fixture_schemas import TestUser


def dict_sorter(d: dict) -> Any:
    possible_keys = {"created_at", "id"}

    return next((d[key] for key in possible_keys if d.get(key)), 1)


def test_database_backup():
    backup_v2 = BackupV2()
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()

    backup = BackupFile(path_to_backup)

    with backup as contents:
        assert contents.validate()


def test_database_restore():
    settings = get_app_settings()

    # Capture existing database snapshot
    original_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_1 = original_exporter.dump()

    # Create Backup
    backup_v2 = BackupV2(settings.DB_URL)
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()
    backup_v2.restore(path_to_backup)

    new_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_2 = new_exporter.dump()

    for s1, s2 in zip(snapshop_1, snapshop_2, strict=False):
        assert snapshop_1[s1].sort(key=dict_sorter) == snapshop_2[s2].sort(key=dict_sorter)


def test_guide_backup_restore_preserves_fields_and_media(unique_user_fn_scoped: TestUser, tmp_path: Path) -> None:
    backup_v2 = BackupV2()
    baseline_generated = backup_v2.backup()
    baseline_backup = Path(shutil.copy(baseline_generated, tmp_path / "baseline.zip"))
    guide_backup: Path | None = None
    guide_generated: Path | None = None

    try:
        repos = unique_user_fn_scoped.repos
        related = repos.guides.create(
            GuideSave(
                title="Check the stop valve",
                group_id=unique_user_fn_scoped.group_id,
                household_id=unique_user_fn_scoped.household_id,
                author_id=unique_user_fn_scoped.user_id,
                slug=f"check-stop-valve-{uuid4()}",
            )
        )
        guide = repos.guides.create(
            GuideSave(
                title="Prepare the house for travel",
                description="A complete backup round-trip Guide",
                guide_type="maintenance",
                difficulty="intermediate",
                frequency="as_needed",
                preparation_minutes=15,
                execution_minutes=45,
                notes="Leave the checklist with the house sitter.",
                last_reviewed="2026-07-15",
                category="Travel",
                tags=["Home A"],
                steps=[{"text": "Turn off the water", "tip": "Photograph the valve position"}],
                callouts=[{"kind": "warning", "text": "Keep fire suppression active"}],
                requirements=[{"kind": "tool", "name": "Valve key", "note": "Stored near the meter"}],
                sources=[{"label": "Utility guidance", "url": "https://example.com/water"}],
                related_guide_ids=[related.id],
                group_id=unique_user_fn_scoped.group_id,
                household_id=unique_user_fn_scoped.household_id,
                author_id=unique_user_fn_scoped.user_id,
                slug=f"prepare-house-for-travel-{uuid4()}",
            )
        )

        guide_data = GuideDataService(guide.id)
        guide_data.write_cover(test_data.images_test_image_1.read_bytes(), "jpg")
        repos.guides.set_cover_image(guide.slug, "cover-version")
        image_id = uuid4()
        guide_data.write_step_image(image_id, test_data.images_test_image_2.read_bytes(), "png")
        guide = repos.guides.create_step_image(
            guide.id,
            guide.steps[0].id,
            image_id,
            "step-version",
            "Valve location",
            "Blue valve beside the meter",
        )

        expected_document = guide.model_dump(mode="json")
        expected_media = {
            path.relative_to(guide_data.guide_dir): path.read_bytes()
            for path in guide_data.guide_dir.glob("**/*")
            if path.is_file()
        }

        guide_generated = backup_v2.backup()
        guide_backup = Path(shutil.copy(guide_generated, tmp_path / "guide.zip"))

        repos.guides.delete(guide.slug)
        GuideDataService(guide.id).delete_all_data()
        repos.session.close()
        backup_v2.restore(guide_backup)

        with session_context() as session:
            restored_repos = get_repositories(
                session,
                group_id=unique_user_fn_scoped.group_id,
                household_id=None,
            )
            restored = restored_repos.guides.get_one(guide.id, key="id")
            assert restored is not None
            assert restored.model_dump(mode="json") == expected_document

        restored_data = GuideDataService(guide.id)
        restored_media = {
            path.relative_to(restored_data.guide_dir): path.read_bytes()
            for path in restored_data.guide_dir.glob("**/*")
            if path.is_file()
        }
        assert restored_media == expected_media
    finally:
        unique_user_fn_scoped.repos.session.close()
        backup_v2.restore(baseline_backup)
        baseline_generated.unlink(missing_ok=True)
        if guide_generated:
            guide_generated.unlink(missing_ok=True)


def _5ab195a474eb_add_normalized_search_properties(session: Session):
    recipes = session.query(RecipeModel).all()

    for recipe in recipes:
        if recipe.name:
            assert recipe.name_normalized
        if recipe.description:
            assert recipe.description_normalized

        for ingredient in recipe.recipe_ingredient:
            if ingredient.note:
                assert ingredient.note_normalized
            if ingredient.original_text:
                assert ingredient.original_text_normalized


def _b04a08da2108_added_shopping_list_label_settings(session: Session):
    shopping_lists = session.query(ShoppingList).all()
    labels = session.query(MultiPurposeLabel).all()

    for shopping_list in shopping_lists:
        group_labels = [label for label in labels if label.group_id == shopping_list.group_id]
        assert len(shopping_list.label_settings) == len(group_labels)
        for label_setting, label in zip(
            sorted(shopping_list.label_settings, key=lambda x: x.label.id),
            sorted(group_labels, key=lambda x: x.id),
            strict=True,
        ):
            assert label_setting.label == label


def _04ac51cbe9a4_added_group_slug(session: Session):
    groups = session.query(Group).all()

    for group in groups:
        assert group.slug


def _0341b154f79a_added_normalized_unit_and_food_names(session: Session):
    foods = session.query(IngredientFoodModel).all()
    units = session.query(IngredientUnitModel).all()

    for food in foods:
        if food.name:
            assert food.name_normalized

    for unit in units:
        assert unit.name_normalized
        if unit.abbreviation:
            assert unit.abbreviation_normalized


def _d7c6efd2de42_migrate_favorites_and_ratings_to_user_ratings(session: Session):
    recipes = session.query(RecipeModel).all()

    users_by_group_id: dict[GUID, list[User]] = {}
    for recipe in recipes:
        users = users_by_group_id.get(recipe.group_id)
        if users is None:
            users = session.query(User).filter(User.group_id == recipe.group_id).all()
            users_by_group_id[recipe.group_id] = users

        user_to_recipes = session.query(UserToRecipe).filter(UserToRecipe.recipe_id == recipe.id).all()
        user_ratings = [x.rating for x in user_to_recipes if x.rating]
        assert recipe.rating == (statistics.mean(user_ratings) if user_ratings else None)


def _86054b40fd06_added_query_filter_string_to_cookbook_and_mealplan(session: Session):
    cookbooks = session.query(CookBook).all()
    mealplan_rules = session.query(GroupMealPlanRules).all()

    for cookbook in cookbooks:
        parts = []
        if cookbook.categories:
            relop = "CONTAINS ALL" if cookbook.require_all_categories else "IN"
            vals = ",".join([f'"{cat.id}"' for cat in cookbook.categories])
            parts.append(f"recipe_category.id {relop} [{vals}]")
        if cookbook.tags:
            relop = "CONTAINS ALL" if cookbook.require_all_tags else "IN"
            vals = ",".join([f'"{tag.id}"' for tag in cookbook.tags])
            parts.append(f"tags.id {relop} [{vals}]")
        if cookbook.tools:
            relop = "CONTAINS ALL" if cookbook.require_all_tools else "IN"
            vals = ",".join([f'"{tool.id}"' for tool in cookbook.tools])
            parts.append(f"tools.id {relop} [{vals}]")

        expected_query_filter_string = " AND ".join(parts)
        assert cookbook.query_filter_string == expected_query_filter_string

    for rule in mealplan_rules:
        parts = []
        if rule.categories:
            vals = ",".join([f'"{cat.id}"' for cat in rule.categories])
            parts.append(f"recipe_category.id CONTAINS ALL [{vals}]")
        if rule.tags:
            vals = ",".join([f'"{tag.id}"' for tag in rule.tags])
            parts.append(f"tags.id CONTAINS ALL [{vals}]")
        if rule.households:
            vals = ",".join([f'"{household.id}"' for household in rule.households])
            parts.append(f"household_id IN [{vals}]")

        expected_query_filter_string = " AND ".join(parts)
        assert rule.query_filter_string == expected_query_filter_string


def _b9e516e2d3b3_add_household_to_recipe_last_made_household_to_foods_and_tools(session: Session):
    groups = session.query(Group).all()

    for group in groups:
        households = session.query(Household).filter(Household.group_id == group.id).all()
        household_ids = {household.id for household in households}
        recipes = session.query(RecipeModel).filter(RecipeModel.group_id == group.id).all()
        for recipe in recipes:
            for household in households:
                household_to_recipe = (
                    session.query(HouseholdToRecipe)
                    .filter(HouseholdToRecipe.recipe_id == recipe.id, HouseholdToRecipe.household_id == household.id)
                    .one_or_none()
                )

                if recipe.last_made:
                    assert household_to_recipe
                    assert household_to_recipe.last_made == recipe.last_made
                else:
                    assert not household_to_recipe

        foods = session.query(IngredientFoodModel).filter(IngredientFoodModel.group_id == group.id).all()
        for food in foods:
            if food.on_hand:
                assert {hh.id for hh in food.households_with_ingredient_food} == household_ids
            else:
                assert not food.households_with_ingredient_food

        tools = session.query(Tool).filter(Tool.group_id == group.id).all()
        for tool in tools:
            if tool.on_hand:
                assert {hh.id for hh in tool.households_with_tool} == household_ids
            else:
                assert not tool.households_with_tool


def _a39c7f1826e3_add_unit_standardization_fields(session: Session):
    groups = session.query(Group).all()

    for group in groups:
        # test_data.backup_version_1d9a002d7234_1 has a non-anonymized "pint" unit
        # and has not yet run the standardization migration.
        pint_units = (
            session.query(IngredientUnitModel)
            .filter(IngredientUnitModel.group_id == group.id, IngredientUnitModel.name == "pint")
            .all()
        )
        for unit in pint_units:
            assert unit.standard_quantity == 2
            assert unit.standard_unit == "cup"


def test_database_restore_data():
    """
    This tests real user backups to make sure the data is restored correctly. The data has been anonymized, but
    relationships and data types should be preserved.

    This test should verify all migrations that do some sort of database manipulation (e.g. populating a new column).
    If a new migration is added that does any sort of data manipulation, this test should be updated.
    """

    backup_paths = [
        test_data.backup_version_1d9a002d7234_1,
        test_data.backup_version_44e8d670719d_1,
        test_data.backup_version_44e8d670719d_2,
        test_data.backup_version_44e8d670719d_3,
        test_data.backup_version_44e8d670719d_4,
        test_data.backup_version_ba1e4a6cfe99_1,
        test_data.backup_version_bcfdad6b7355_1,
        test_data.backup_version_09aba125b57a_1,
        test_data.backup_version_86054b40fd06_1,
    ]

    migration_funcs = [
        _5ab195a474eb_add_normalized_search_properties,
        _b04a08da2108_added_shopping_list_label_settings,
        _04ac51cbe9a4_added_group_slug,
        _0341b154f79a_added_normalized_unit_and_food_names,
        _d7c6efd2de42_migrate_favorites_and_ratings_to_user_ratings,
        _86054b40fd06_added_query_filter_string_to_cookbook_and_mealplan,
        _b9e516e2d3b3_add_household_to_recipe_last_made_household_to_foods_and_tools,
        _a39c7f1826e3_add_unit_standardization_fields,
    ]

    settings = get_app_settings()
    backup_v2 = BackupV2(settings.DB_URL)

    backup_v2.directories.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    original_data_backup = backup_v2.backup()

    try:
        for backup_path in backup_paths:
            assert backup_path.exists()
            backup_v2.restore(backup_path)

            with session_context() as session:
                for migration_func in migration_funcs:
                    try:
                        migration_func(session)
                    except Exception as e:
                        session.rollback()
                        raise Exception(
                            f'Migration "{migration_func.__name__}" failed on backup "{backup_path}"'
                        ) from e

    finally:
        backup_v2.restore(original_data_backup)
