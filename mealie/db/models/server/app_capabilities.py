from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from .._model_utils.auto_init import auto_init


class AppCapabilitiesModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "app_capabilities"

    guides: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    legacy_recipes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    meal_planning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    shopping_lists: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    nutrition: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
