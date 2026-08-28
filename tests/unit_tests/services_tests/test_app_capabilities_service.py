from types import SimpleNamespace
from unittest.mock import Mock

from sqlalchemy.orm import Session

from mealie.services.app_capabilities_service import AppCapabilitiesService


def test_app_capabilities_use_persisted_installation_profile() -> None:
    session = Mock(spec=Session)
    session.get.return_value = SimpleNamespace(
        id=1,
        guides=True,
        legacy_recipes=False,
        meal_planning=False,
        shopping_lists=False,
        nutrition=False,
    )

    capabilities = AppCapabilitiesService(session).get()

    assert capabilities.guides is True
    assert capabilities.legacy_recipes is False
    assert capabilities.meal_planning is False
    assert capabilities.shopping_lists is False
    assert capabilities.nutrition is False


def test_app_capabilities_operator_override_controls_only_legacy_features() -> None:
    session = Mock(spec=Session)
    session.get.return_value = SimpleNamespace(
        id=1,
        guides=True,
        legacy_recipes=True,
        meal_planning=True,
        shopping_lists=True,
        nutrition=True,
    )

    capabilities = AppCapabilitiesService(session, legacy_features_override=False).get()

    assert capabilities.guides is True
    assert capabilities.legacy_recipes is False
    assert capabilities.meal_planning is False
    assert capabilities.shopping_lists is False
    assert capabilities.nutrition is False


def test_app_capabilities_fail_open_for_pre_migration_database() -> None:
    session = Mock(spec=Session)
    session.get.return_value = None

    capabilities = AppCapabilitiesService(session).get()

    assert capabilities.legacy_recipes is True
    assert capabilities.meal_planning is True
    assert capabilities.shopping_lists is True
    assert capabilities.nutrition is True
