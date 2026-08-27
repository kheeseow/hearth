from datetime import date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import UUID4, ConfigDict, Field, HttpUrl, StringConstraints, field_validator
from sqlalchemy.orm import selectinload

from mealie.db.models.guide import GuideModel, GuideStepModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase

GuideCategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
GuideTagName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
GuideRequirementName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
GuideRequirementNote = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
GuideStepTip = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
GuideImageCaption = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
GuideImageAltText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
GuideSourceLabel = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
GuideSourceUrl = Annotated[HttpUrl, Field(max_length=2000)]


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


class GuideFrequency(StrEnum):
    one_time = "one_time"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"
    as_needed = "as_needed"


class GuideCalloutKind(StrEnum):
    warning = "warning"
    avoid = "avoid"


class GuideStepIn(MealieModel):
    id: UUID4 | None = None
    text: str = Field(min_length=1)
    tip: GuideStepTip | None = None

    @field_validator("tip", mode="before")
    @classmethod
    def empty_tip_is_none(cls, tip: str | None) -> str | None:
        if not isinstance(tip, str):
            return tip
        return tip.strip() or None


class GuideStepImageOut(MealieModel):
    id: UUID4
    position: int
    version: str
    caption: str | None = None
    alt_text: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GuideStepImageUpdate(MealieModel):
    caption: GuideImageCaption | None = None
    alt_text: GuideImageAltText | None = None

    @field_validator("caption", "alt_text", mode="before")
    @classmethod
    def empty_text_is_none(cls, value: str | None) -> str | None:
        if not isinstance(value, str):
            return value
        return value.strip() or None


class GuideStepImageOrder(MealieModel):
    image_ids: list[UUID4] = Field(max_length=20)


class GuideStepOut(MealieModel):
    id: UUID4
    position: int
    text: str
    tip: str | None = None
    images: list[GuideStepImageOut] = Field(default_factory=list)

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


class GuideRequirementKind(StrEnum):
    tool = "tool"
    material = "material"


class GuideRequirementIn(MealieModel):
    id: UUID4 | None = None
    kind: GuideRequirementKind
    name: GuideRequirementName
    note: GuideRequirementNote | None = None

    @field_validator("note", mode="before")
    @classmethod
    def empty_note_is_none(cls, note: str | None) -> str | None:
        if not isinstance(note, str):
            return note
        return note.strip() or None


class GuideRequirementOut(MealieModel):
    id: UUID4
    position: int
    kind: GuideRequirementKind
    name: str
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GuideSourceIn(MealieModel):
    id: UUID4 | None = None
    label: GuideSourceLabel
    url: GuideSourceUrl


class GuideSourceOut(MealieModel):
    id: UUID4
    position: int
    label: str
    url: str

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
    frequency: GuideFrequency | None = None
    preparation_minutes: int | None = Field(default=None, ge=0, le=10080)
    execution_minutes: int | None = Field(default=None, ge=0, le=10080)
    notes: str | None = None
    last_reviewed: date | None = None
    category: GuideCategoryName | None = None
    tags: list[GuideTagName] = Field(default_factory=list)
    steps: list[GuideStepIn] = Field(default_factory=list)
    callouts: list[GuideCalloutIn] = Field(default_factory=list)
    requirements: list[GuideRequirementIn] = Field(default_factory=list)
    sources: list[GuideSourceIn] = Field(default_factory=list, max_length=50)
    related_guide_ids: list[UUID4] = Field(default_factory=list)

    @field_validator("notes", mode="before")
    @classmethod
    def empty_notes_are_none(cls, notes: str | None) -> str | None:
        if not isinstance(notes, str):
            return notes
        return notes.strip() or None

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, tags: list[str]) -> list[str]:
        if len(tags) > 20:
            raise ValueError("A guide can have at most 20 tags")
        return tags

    @field_validator("requirements")
    @classmethod
    def limit_requirements(cls, requirements: list[GuideRequirementIn]) -> list[GuideRequirementIn]:
        if len(requirements) > 50:
            raise ValueError("A guide can have at most 50 requirements")
        return requirements

    @field_validator("related_guide_ids")
    @classmethod
    def limit_related_guides(cls, guide_ids: list[UUID4]) -> list[UUID4]:
        if len(guide_ids) > 20:
            raise ValueError("A guide can have at most 20 related guides")
        return guide_ids


class GuideUpdate(GuideCreate):
    pass


class GuidePatch(MealieModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    guide_type: GuideType | None = None
    difficulty: GuideDifficulty | None = None
    frequency: GuideFrequency | None = None
    preparation_minutes: int | None = Field(default=None, ge=0, le=10080)
    execution_minutes: int | None = Field(default=None, ge=0, le=10080)
    notes: str | None = None
    last_reviewed: date | None = None
    category: GuideCategoryName | None = None
    tags: list[GuideTagName] | None = None
    steps: list[GuideStepIn] | None = None
    callouts: list[GuideCalloutIn] | None = None
    requirements: list[GuideRequirementIn] | None = None
    sources: list[GuideSourceIn] | None = None
    related_guide_ids: list[UUID4] | None = None

    @field_validator("notes", mode="before")
    @classmethod
    def empty_notes_are_none(cls, notes: str | None) -> str | None:
        if not isinstance(notes, str):
            return notes
        return notes.strip() or None

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is not None and len(tags) > 20:
            raise ValueError("A guide can have at most 20 tags")
        return tags

    @field_validator("requirements")
    @classmethod
    def limit_requirements(cls, requirements: list[GuideRequirementIn] | None) -> list[GuideRequirementIn] | None:
        if requirements is not None and len(requirements) > 50:
            raise ValueError("A guide can have at most 50 requirements")
        return requirements

    @field_validator("related_guide_ids")
    @classmethod
    def limit_related_guides(cls, guide_ids: list[UUID4] | None) -> list[UUID4] | None:
        if guide_ids is not None and len(guide_ids) > 20:
            raise ValueError("A guide can have at most 20 related guides")
        return guide_ids


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
    frequency: GuideFrequency | None = None
    preparation_minutes: int | None = None
    execution_minutes: int | None = None
    last_reviewed: date | None = None
    cover_image_version: str | None = None
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


class GuideRelatedOut(MealieModel):
    id: UUID4
    slug: str
    title: str
    guide_type: GuideType | None = None
    difficulty: GuideDifficulty | None = None
    cover_image_version: str | None = None

    model_config = ConfigDict(from_attributes=True)


class GuideRead(GuideSummary):
    notes: str | None = None
    steps: list[GuideStepOut] = Field(default_factory=list)
    callouts: list[GuideCalloutOut] = Field(default_factory=list)
    requirements: list[GuideRequirementOut] = Field(default_factory=list)
    sources: list[GuideSourceOut] = Field(default_factory=list)
    related_guides: list[GuideRelatedOut] = Field(default_factory=list)

    @classmethod
    def loader_options(cls):
        return [
            selectinload(GuideModel.category),
            selectinload(GuideModel.tags),
            selectinload(GuideModel.steps),
            selectinload(GuideModel.steps).selectinload(GuideStepModel.images),
            selectinload(GuideModel.callouts),
            selectinload(GuideModel.requirements),
            selectinload(GuideModel.sources),
            selectinload(GuideModel.related_guides),
        ]


class GuidePagination(PaginationBase[GuideSummary]):
    pass
