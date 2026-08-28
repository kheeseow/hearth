from sqlalchemy.orm import Session

from mealie.db.models.server.app_capabilities import AppCapabilitiesModel
from mealie.schema.admin.about import AppCapabilities


class AppCapabilitiesService:
    """Resolve the persisted installation profile with an optional operator override."""

    def __init__(self, session: Session, legacy_features_override: bool | None = None) -> None:
        self.session = session
        self.legacy_features_override = legacy_features_override

    def get(self) -> AppCapabilities:
        persisted = self.session.get(AppCapabilitiesModel, 1)
        capabilities = (
            AppCapabilities(
                guides=persisted.guides,
                legacy_recipes=persisted.legacy_recipes,
                meal_planning=persisted.meal_planning,
                shopping_lists=persisted.shopping_lists,
                nutrition=persisted.nutrition,
            )
            if persisted
            else AppCapabilities(
                guides=True,
                legacy_recipes=True,
                meal_planning=True,
                shopping_lists=True,
                nutrition=True,
            )
        )

        if self.legacy_features_override is None:
            return capabilities

        return capabilities.model_copy(
            update={
                "legacy_recipes": self.legacy_features_override,
                "meal_planning": self.legacy_features_override,
                "shopping_lists": self.legacy_features_override,
                "nutrition": self.legacy_features_override,
            }
        )
