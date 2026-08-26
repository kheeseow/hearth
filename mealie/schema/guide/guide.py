from datetime import datetime

from pydantic import UUID4, ConfigDict, Field
from sqlalchemy.orm import selectinload

from mealie.db.models.guide import GuideModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase


class GuideStepIn(MealieModel):
    id: UUID4 | None = None
    text: str = Field(min_length=1)


class GuideStepOut(MealieModel):
    id: UUID4
    position: int
    text: str

    model_config = ConfigDict(from_attributes=True)


class GuideCreate(MealieModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    steps: list[GuideStepIn] = Field(default_factory=list)


class GuideUpdate(GuideCreate):
    pass


class GuidePatch(MealieModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    steps: list[GuideStepIn] | None = None


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
    created_at: datetime
    updated_at: datetime = UpdatedAtField()

    _normalize_search = True
    _searchable_properties = ["title_normalized", "description_normalized"]
    model_config = ConfigDict(from_attributes=True)


class GuideRead(GuideSummary):
    steps: list[GuideStepOut] = Field(default_factory=list)

    @classmethod
    def loader_options(cls):
        return [selectinload(GuideModel.steps)]


class GuidePagination(PaginationBase[GuideSummary]):
    pass
