from enum import StrEnum
from functools import cached_property
from pathlib import Path

from fastapi import Depends, File, Form, HTTPException, Query, status
from pydantic import UUID4
from starlette.responses import FileResponse

from mealie.core.dependencies.dependencies import get_temporary_zip_path
from mealie.core.security import create_file_token
from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.guide import (
    GuideCreate,
    GuideDifficulty,
    GuideExportRequest,
    GuideFrequency,
    GuidePagination,
    GuidePatch,
    GuideRead,
    GuideStepImageOrder,
    GuideStepImageUpdate,
    GuideType,
    GuideUpdate,
)
from mealie.schema.response import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_types import EventGuideData, EventOperation, EventTypes
from mealie.services.guide import GuideExportService, GuideService

router = UserAPIRouter(prefix="/guides", tags=["Guides"], route_class=MealieCrudRoute)


class GuideImageSize(StrEnum):
    original = "original"
    small = "small"
    tiny = "tiny"


@controller(router)
class GuideController(BaseCrudController):
    @cached_property
    def service(self) -> GuideService:
        return GuideService(self.session, self.user)

    @cached_property
    def export_service(self) -> GuideExportService:
        return GuideExportService(self.session, self.user)

    @router.get("", response_model=GuidePagination)
    def get_all(
        self,
        q: PaginationQuery = Depends(),
        search: str | None = Query(default=None),
        guide_type: GuideType | None = Query(default=None, alias="guideType"),
        difficulty: GuideDifficulty | None = Query(default=None),
        frequency: GuideFrequency | None = Query(default=None),
        category: str | None = Query(default=None),
        tag: str | None = Query(default=None),
    ) -> GuidePagination:
        response = self.service.list(q, search, guide_type, difficulty, frequency, category, tag)
        response.set_pagination_guides(
            router.url_path_for("get_all"),
            {
                **q.model_dump(),
                "search": search,
                "guideType": guide_type,
                "difficulty": difficulty,
                "frequency": frequency,
                "category": category,
                "tag": tag,
            },
        )
        return GuidePagination.model_validate(response.model_dump())

    @router.post("", response_model=GuideRead, status_code=status.HTTP_201_CREATED)
    def create(self, data: GuideCreate) -> GuideRead:
        guide = self.service.create(data)
        self.publish_event(
            event_type=EventTypes.guide_created,
            document_data=EventGuideData(operation=EventOperation.create, guide_slug=guide.slug),
            group_id=guide.group_id,
            household_id=guide.household_id,
            message=self.t(
                "notifications.generic-created-with-url",
                name=guide.title,
                url=urls.guide_url(self.group.slug, guide.slug, self.settings.BASE_URL),
            ),
        )
        return guide

    @router.post("/export", response_model=GroupDataExport, status_code=status.HTTP_201_CREATED)
    def export_guides(self, data: GuideExportRequest) -> GroupDataExport:
        with get_temporary_zip_path() as temp_path:
            return self.export_service.export_guides(temp_path, data.guide_ids)

    @router.get("/export/{export_id}/download")
    def get_export_download_token(self, export_id: UUID4) -> dict[str, str]:
        export = self.export_service.get_export(export_id)
        if not export:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Export not found")
        return {"fileToken": create_file_token(Path(export.path).resolve())}

    @router.get("/{slug_or_id}", response_model=GuideRead)
    def get_one(self, slug_or_id: str) -> GuideRead:
        return self.service.get(slug_or_id)

    @router.put("/{slug_or_id}", response_model=GuideRead)
    def update(self, slug_or_id: str, data: GuideUpdate) -> GuideRead:
        guide = self.service.update(slug_or_id, data)
        self._publish_guide_updated(guide)
        return guide

    @router.patch("/{slug_or_id}", response_model=GuideRead)
    def patch(self, slug_or_id: str, data: GuidePatch) -> GuideRead:
        guide = self.service.patch(slug_or_id, data)
        self._publish_guide_updated(guide)
        return guide

    @router.delete("/{slug_or_id}", response_model=GuideRead)
    def delete(self, slug_or_id: str) -> GuideRead:
        guide = self.service.delete(slug_or_id)
        self.publish_event(
            event_type=EventTypes.guide_deleted,
            document_data=EventGuideData(operation=EventOperation.delete, guide_slug=guide.slug),
            group_id=guide.group_id,
            household_id=guide.household_id,
            message=self.t("notifications.generic-deleted", name=guide.title),
        )
        return guide

    @router.put("/{slug_or_id}/image", response_model=GuideRead)
    def update_cover_image(self, slug_or_id: str, image: bytes = File(...), extension: str = Form(...)) -> GuideRead:
        try:
            guide = self.service.update_cover_image(slug_or_id, image, extension)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        self._publish_guide_updated(guide)
        return guide

    @router.delete("/{slug_or_id}/image", response_model=GuideRead)
    def delete_cover_image(self, slug_or_id: str) -> GuideRead:
        guide = self.service.delete_cover_image(slug_or_id)
        self._publish_guide_updated(guide)
        return guide

    @router.get("/{slug_or_id}/image/{size}", response_class=FileResponse)
    def get_cover_image(self, slug_or_id: str, size: GuideImageSize = GuideImageSize.original) -> FileResponse:
        return FileResponse(self.service.cover_image_path(slug_or_id, size.value), media_type="image/webp")

    @router.post("/{slug_or_id}/steps/{step_id}/images", response_model=GuideRead)
    def add_step_image(
        self,
        slug_or_id: str,
        step_id: UUID4,
        image: bytes = File(...),
        extension: str = Form(...),
        caption: str | None = Form(default=None),
        alt_text: str | None = Form(default=None),
    ) -> GuideRead:
        metadata = GuideStepImageUpdate(caption=caption, alt_text=alt_text)
        try:
            guide = self.service.add_step_image(
                slug_or_id, step_id, image, extension, metadata.caption, metadata.alt_text
            )
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        self._publish_guide_updated(guide)
        return guide

    @router.patch("/{slug_or_id}/steps/{step_id}/images/{image_id}", response_model=GuideRead)
    def update_step_image(
        self,
        slug_or_id: str,
        step_id: UUID4,
        image_id: UUID4,
        data: GuideStepImageUpdate,
    ) -> GuideRead:
        guide = self.service.update_step_image(slug_or_id, step_id, image_id, data)
        self._publish_guide_updated(guide)
        return guide

    @router.put("/{slug_or_id}/steps/{step_id}/images/{image_id}/file", response_model=GuideRead)
    def replace_step_image(
        self,
        slug_or_id: str,
        step_id: UUID4,
        image_id: UUID4,
        image: bytes = File(...),
        extension: str = Form(...),
    ) -> GuideRead:
        try:
            guide = self.service.replace_step_image(slug_or_id, step_id, image_id, image, extension)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
        self._publish_guide_updated(guide)
        return guide

    @router.put("/{slug_or_id}/steps/{step_id}/images/order", response_model=GuideRead)
    def reorder_step_images(self, slug_or_id: str, step_id: UUID4, data: GuideStepImageOrder) -> GuideRead:
        guide = self.service.reorder_step_images(slug_or_id, step_id, data)
        self._publish_guide_updated(guide)
        return guide

    @router.delete("/{slug_or_id}/steps/{step_id}/images/{image_id}", response_model=GuideRead)
    def delete_step_image(self, slug_or_id: str, step_id: UUID4, image_id: UUID4) -> GuideRead:
        guide = self.service.delete_step_image(slug_or_id, step_id, image_id)
        self._publish_guide_updated(guide)
        return guide

    def _publish_guide_updated(self, guide: GuideRead) -> None:
        self.publish_event(
            event_type=EventTypes.guide_updated,
            document_data=EventGuideData(operation=EventOperation.update, guide_slug=guide.slug),
            group_id=guide.group_id,
            household_id=guide.household_id,
            message=self.t(
                "notifications.generic-updated-with-url",
                name=guide.title,
                url=urls.guide_url(self.group.slug, guide.slug, self.settings.BASE_URL),
            ),
        )

    @router.get(
        "/{slug_or_id}/steps/{step_id}/images/{image_id}/{size}",
        response_class=FileResponse,
    )
    def get_step_image(
        self,
        slug_or_id: str,
        step_id: UUID4,
        image_id: UUID4,
        size: GuideImageSize = GuideImageSize.original,
    ) -> FileResponse:
        return FileResponse(
            self.service.step_image_path(slug_or_id, step_id, image_id, size.value),
            media_type="image/webp",
        )
