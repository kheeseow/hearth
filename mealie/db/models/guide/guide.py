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


guides_to_tags = sa.Table(
    "guides_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("guide_id", GUID, sa.ForeignKey("guides.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("tag_id", GUID, sa.ForeignKey("guide_tags.id", ondelete="CASCADE"), primary_key=True),
)


class GuideCategoryModel(SqlAlchemyBase):
    __tablename__ = "guide_categories"
    __table_args__ = (sa.UniqueConstraint("group_id", "normalized_name", name="guide_category_group_name_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)

    @auto_init()
    def __init__(self, name: str = "", **_) -> None:
        self.name = name.strip()
        self.normalized_name = self.normalize(name)


class GuideTagModel(SqlAlchemyBase):
    __tablename__ = "guide_tags"
    __table_args__ = (sa.UniqueConstraint("group_id", "normalized_name", name="guide_tag_group_name_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    normalized_name: Mapped[str] = mapped_column(sa.String(50), nullable=False)

    @auto_init()
    def __init__(self, name: str = "", **_) -> None:
        self.name = name.strip()
        self.normalized_name = self.normalize(name)


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


class GuideCalloutModel(SqlAlchemyBase):
    __tablename__ = "guide_callouts"
    __table_args__ = (sa.CheckConstraint("kind IN ('warning', 'avoid')", name="guide_callout_kind_check"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    guide_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("guides.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    kind: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    text: Mapped[str] = mapped_column(sa.Text, nullable=False)

    model_config = ConfigDict(exclude={"id", "guide_id", "position"})

    @auto_init()
    def __init__(self, **_) -> None: ...


class GuideModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "guides"
    __table_args__ = (
        sa.UniqueConstraint("slug", "group_id", name="guide_slug_group_id_key"),
        sa.CheckConstraint(
            "guide_type IS NULL OR guide_type IN "
            "('cleaning', 'maintenance', 'setup', 'emergency', 'troubleshooting', 'care_instructions')",
            name="guide_type_check",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="guide_difficulty_check",
        ),
        sa.CheckConstraint(
            "preparation_minutes IS NULL OR preparation_minutes >= 0",
            name="guide_preparation_minutes_check",
        ),
        sa.CheckConstraint(
            "execution_minutes IS NULL OR execution_minutes >= 0",
            name="guide_execution_minutes_check",
        ),
    )

    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    household_id: FilterableColumn[GUID] = mapped_column(
        GUID, sa.ForeignKey("households.id"), nullable=False, index=True
    )
    author_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("users.id"), nullable=False, index=True)
    category_id: FilterableColumn[GUID | None] = mapped_column(
        GUID,
        sa.ForeignKey("guide_categories.id", name="fk_guides_category_id_guide_categories", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    group: Mapped["Group"] = orm.relationship("Group")
    household: Mapped["Household"] = orm.relationship("Household")
    author: Mapped["User"] = orm.relationship("User")
    category: Mapped[GuideCategoryModel | None] = orm.relationship(GuideCategoryModel)

    slug: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    title: FilterableColumn[str] = mapped_column(sa.String, nullable=False)
    description: FilterableColumn[str] = mapped_column(sa.Text, nullable=False, default="")
    guide_type: FilterableColumn[str | None] = mapped_column(sa.String(30), nullable=True, index=True)
    difficulty: FilterableColumn[str | None] = mapped_column(sa.String(20), nullable=True, index=True)
    preparation_minutes: FilterableColumn[int | None] = mapped_column(sa.Integer, nullable=True)
    execution_minutes: FilterableColumn[int | None] = mapped_column(sa.Integer, nullable=True)
    title_normalized: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    description_normalized: FilterableColumn[str] = mapped_column(sa.String, nullable=False, index=True)
    search_document_normalized: FilterableColumn[str] = mapped_column(sa.Text, nullable=False, default="")

    steps: Mapped[list[GuideStepModel]] = orm.relationship(
        GuideStepModel,
        cascade="all, delete-orphan",
        order_by=GuideStepModel.position,
        collection_class=ordering_list("position"),
    )
    callouts: Mapped[list[GuideCalloutModel]] = orm.relationship(
        GuideCalloutModel,
        cascade="all, delete-orphan",
        order_by=GuideCalloutModel.position,
        collection_class=ordering_list("position"),
    )
    tags: Mapped[list[GuideTagModel]] = orm.relationship(GuideTagModel, secondary=guides_to_tags)

    model_config = ConfigDict(exclude={"group", "household", "author"})

    @auto_init()
    def __init__(self, title: str = "", description: str = "", **_) -> None:
        self.title_normalized = self.normalize(title)
        self.description_normalized = self.normalize(description)
