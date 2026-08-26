from functools import cached_property

from fastapi import Depends, Query, status

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.guide import (
    GuideCreate,
    GuideDifficulty,
    GuidePagination,
    GuidePatch,
    GuideRead,
    GuideType,
    GuideUpdate,
)
from mealie.schema.response import PaginationQuery
from mealie.services.guide import GuideService

router = UserAPIRouter(prefix="/guides", tags=["Guides"], route_class=MealieCrudRoute)


@controller(router)
class GuideController(BaseUserController):
    @cached_property
    def service(self) -> GuideService:
        return GuideService(self.session, self.user)

    @router.get("", response_model=GuidePagination)
    def get_all(
        self,
        q: PaginationQuery = Depends(),
        search: str | None = Query(default=None),
        guide_type: GuideType | None = Query(default=None, alias="guideType"),
        difficulty: GuideDifficulty | None = Query(default=None),
        category: str | None = Query(default=None),
        tag: str | None = Query(default=None),
    ) -> GuidePagination:
        response = self.service.list(q, search, guide_type, difficulty, category, tag)
        response.set_pagination_guides(
            router.url_path_for("get_all"),
            {
                **q.model_dump(),
                "search": search,
                "guideType": guide_type,
                "difficulty": difficulty,
                "category": category,
                "tag": tag,
            },
        )
        return GuidePagination.model_validate(response.model_dump())

    @router.post("", response_model=GuideRead, status_code=status.HTTP_201_CREATED)
    def create(self, data: GuideCreate) -> GuideRead:
        return self.service.create(data)

    @router.get("/{slug_or_id}", response_model=GuideRead)
    def get_one(self, slug_or_id: str) -> GuideRead:
        return self.service.get(slug_or_id)

    @router.put("/{slug_or_id}", response_model=GuideRead)
    def update(self, slug_or_id: str, data: GuideUpdate) -> GuideRead:
        return self.service.update(slug_or_id, data)

    @router.patch("/{slug_or_id}", response_model=GuideRead)
    def patch(self, slug_or_id: str, data: GuidePatch) -> GuideRead:
        return self.service.patch(slug_or_id, data)

    @router.delete("/{slug_or_id}", response_model=GuideRead)
    def delete(self, slug_or_id: str) -> GuideRead:
        return self.service.delete(slug_or_id)
