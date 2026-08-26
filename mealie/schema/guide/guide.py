from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import UUID4, ConfigDict, Field, StringConstraints, field_validator
from sqlalchemy.orm import selectinload

from mealie.db.models.guide import GuideModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase

GuideCategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
GuideTagName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class GuideType(StrEnum):
    cleaning = "cleaning"
    maintenance = "maintenance"
    setup = "setup"
    emergency = "emergency"
    troubleshooting = "troubleshooting"
    care_instructions = "care_instructions"


class GuideDifficulty(StrEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class GuideCalloutKind(StrEnum):
    warning = "warning"
    avoid = "avoid"


class GuideStepIn(MealieModel):
    id: UUID4 | None = None
    text: str = Field(min_length=1)


class GuideStepOut(MealieModel):
    id: UUID4
    position: int
    text: str

    model_config = ConfigDict(from_attributes=True)


class GuideCalloutIn(MealieModel):
    id: UUID4 | None = None
    kind: GuideCalloutKind
    text: str = Field(min_length=1)


class GuideCalloutOut(MealieModel):
    id: UUID4
    position: int
    kind: GuideCalloutKind
    text: str

    model_config = ConfigDict(from_attributes=True)


class GuideCategoryOut(MealieModel):
    id: UUID4
    name: str

    model_config = ConfigDict(from_attributes=True)


class GuideTagOut(MealieModel):
    id: UUID4
    name: str

    model_config = ConfigDict(from_attributes=True)


class GuideCreate(MealieModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    guide_type: GuideType | None = None
    difficulty: GuideDifficulty | None = None
    preparation_minutes: int | None = Field(default=None, ge=0, le=10080)
    execution_minutes: int | None = Field(default=None, ge=0, le=10080)
    category: GuideCategoryName | None = None
    tags: list[GuideTagName] = Field(default_factory=list)
    steps: list[GuideStepIn] = Field(default_factory=list)
    callouts: list[GuideCalloutIn] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, tags: list[str]) -> list[str]:
        if len(tags) > 20:
            raise ValueError("A guide can have at most 20 tags")
        return tags


class GuideUpdate(GuideCreate):
    pass


class GuidePatch(MealieModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    guide_type: GuideType | None = None
    difficulty: GuideDifficulty | None = None
    preparation_minutes: int | None = Field(default=None, ge=0, le=10080)
    execution_minutes: int | None = Field(default=None, ge=0, le=10080)
    category: GuideCategoryName | None = None
    tags: list[GuideTagName] | None = None
    steps: list[GuideStepIn] | None = None
    callouts: list[GuideCalloutIn] | None = None

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is not None and len(tags) > 20:
            raise ValueError("A guide can have at most 20 tags")
        return tags


class GuideSave(GuideCreate):
    group_id: UUID4
    household_id: UUID4
    author_id: UUID4
    slug: str


class GuideSummary(MealieModel):
    id: UUID4
    group_id: UUID4
    household_id: UUID4
    author_id: UUID4
    slug: str
    title: str
    description: str
    guide_type: GuideType | None = None
    difficulty: GuideDifficulty | None = None
    preparation_minutes: int | None = None
    execution_minutes: int | None = None
    category: GuideCategoryOut | None = None
    tags: list[GuideTagOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime = UpdatedAtField()

    _normalize_search = True
    _searchable_properties = ["search_document_normalized"]
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls):
        return [selectinload(GuideModel.category), selectinload(GuideModel.tags)]


class GuideRead(GuideSummary):
    steps: list[GuideStepOut] = Field(default_factory=list)
    callouts: list[GuideCalloutOut] = Field(default_factory=list)

    @classmethod
    def loader_options(cls):
        return [
            selectinload(GuideModel.category),
            selectinload(GuideModel.tags),
            selectinload(GuideModel.steps),
            selectinload(GuideModel.callouts),
        ]


class GuidePagination(PaginationBase[GuideSummary]):
    pass
