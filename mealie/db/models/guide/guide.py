from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pydantic import ConfigDict
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..household import Household
    from ..users import User


class GuideStepModel(SqlAlchemyBase):
    __tablename__ = "guide_steps"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    guide_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("guides.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    model_config = ConfigDict(exclude={"id", "guide_id", "position"})

    @auto_init()
    def __init__(self, **_) -> None: ...


class GuideModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "guides"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="guide_slug_group_id_key"),)

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    author_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("users.id"), nullable=False, index=True)

    group: Mapped["Group"] = orm.relationship("Group")
    household: Mapped["Household"] = orm.relationship("Household")
    author: Mapped["User"] = orm.relationship("User")

    slug: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    title: FilterableColumn[str] = mapped_column(sa.String, nullable=False)
    description: FilterableColumn[str] = mapped_column(sa.Text, nullable=False, default="")
    title_normalized: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    description_normalized: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)

    steps: Mapped[list[GuideStepModel]] = orm.relationship(
        GuideStepModel,
        cascade="all, delete-orphan",
        order_by=GuideStepModel.position,
        collection_class=ordering_list("position"),
    )

    model_config = ConfigDict(exclude={"group", "household", "author"})

    @auto_init()
    def __init__(self, title: str = "", description: str = "", **_) -> None:
        self.title_normalized = self.normalize(title)
        self.description_normalized = self.normalize(description)
