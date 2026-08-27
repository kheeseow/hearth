from collections.abc import Sequence
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from mealie.db.models.guide import (
    GuideCalloutModel,
    GuideModel,
    GuideRequirementModel,
    GuideSourceModel,
    GuideStepModel,
)
from mealie.pkgs import cache
from mealie.repos.all_repositories import AllRepositories, get_repositories
from mealie.schema.guide import (
    GuideCreate,
    GuidePatch,
    GuideRead,
    GuideSave,
    GuideStepImageOrder,
    GuideStepImageUpdate,
    GuideUpdate,
)
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.user import PrivateUser

from .guide_data_service import GuideDataService


class GuideService:
    def __init__(self, session: Session, user: PrivateUser) -> None:
        self.session = session
        self.user = user
        self.household_repos = get_repositories(session, group_id=user.group_id, household_id=user.household_id)
        self.group_repos = get_repositories(session, group_id=user.group_id, household_id=None)

    def list(
        self,
        pagination: PaginationQuery,
        search: str | None = None,
        guide_type: str | None = None,
        difficulty: str | None = None,
        frequency: str | None = None,
        category: str | None = None,
        tag: str | None = None,
    ) -> PaginationBase[GuideRead]:
        return self.group_repos.guides.page_filtered(
            pagination,
            search=search,
            guide_type=guide_type,
            difficulty=difficulty,
            frequency=frequency,
            category=category,
            tag=tag,
        )

    def get(self, slug_or_id: str) -> GuideRead:
        guide = self._find(self.group_repos, slug_or_id)
        if not guide:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide not found")
        return guide

    def create(self, data: GuideCreate) -> GuideRead:
        self._validate_related_guide_ids(None, data.related_guide_ids)
        slug = self._unique_slug(data.title)
        return self.household_repos.guides.create(
            GuideSave(
                **data.model_dump(),
                group_id=self.user.group_id,
                household_id=self.user.household_id,
                author_id=self.user.id,
                slug=slug,
            )
        )

    def update(self, slug_or_id: str, data: GuideUpdate) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        self._validate_step_ids(guide, data)
        self._validate_callout_ids(guide, data)
        self._validate_requirement_ids(guide, data)
        self._validate_source_ids(guide, data)
        self._validate_related_guide_ids(guide.id, data.related_guide_ids)
        payload = data.model_dump()
        payload.update(
            group_id=guide.group_id,
            household_id=guide.household_id,
            author_id=guide.author_id,
            slug=guide.slug,
        )
        retained_step_ids = {step.id for step in data.steps if step.id}
        removed_image_ids = [
            image.id for step in guide.steps if step.id not in retained_step_ids for image in step.images
        ]
        updated = self.household_repos.guides.update(guide.slug, payload)
        data_service = GuideDataService(guide.id)
        for image_id in removed_image_ids:
            data_service.delete_step_image(image_id)
        return updated

    def patch(self, slug_or_id: str, data: GuidePatch) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        existing = {
            "title": guide.title,
            "description": guide.description,
            "guide_type": guide.guide_type,
            "difficulty": guide.difficulty,
            "frequency": guide.frequency,
            "preparation_minutes": guide.preparation_minutes,
            "execution_minutes": guide.execution_minutes,
            "notes": guide.notes,
            "last_reviewed": guide.last_reviewed,
            "category": guide.category.name if guide.category else None,
            "tags": [tag.name for tag in guide.tags],
            "steps": [step.model_dump(include={"id", "text", "tip"}) for step in guide.steps],
            "callouts": [callout.model_dump(include={"id", "kind", "text"}) for callout in guide.callouts],
            "requirements": [
                requirement.model_dump(include={"id", "kind", "name", "note"}) for requirement in guide.requirements
            ],
            "sources": [source.model_dump(include={"id", "label", "url"}) for source in guide.sources],
            "related_guide_ids": [related.id for related in guide.related_guides],
        }
        changes = data.model_dump(exclude_unset=True)
        for required_field in (
            "title",
            "description",
            "tags",
            "steps",
            "callouts",
            "requirements",
            "sources",
            "related_guide_ids",
        ):
            if changes.get(required_field) is None:
                changes.pop(required_field, None)
        merged = GuideUpdate.model_validate({**existing, **changes})
        return self.update(guide.slug, merged)

    def delete(self, slug_or_id: str) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        deleted = self.household_repos.guides.delete(guide.slug)
        GuideDataService(guide.id).delete_all_data()
        return deleted

    def update_cover_image(self, slug_or_id: str, image: bytes, extension: str) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        GuideDataService(guide.id).write_cover(image, extension)
        return self.household_repos.guides.set_cover_image(guide.slug, cache.new_key())

    def delete_cover_image(self, slug_or_id: str) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        updated = self.household_repos.guides.set_cover_image(guide.slug, None)
        GuideDataService(guide.id).delete_cover()
        return updated

    def add_step_image(
        self,
        slug_or_id: str,
        step_id: UUID,
        image: bytes,
        extension: str,
        caption: str | None,
        alt_text: str | None,
    ) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        step = self._get_step(guide, step_id)
        if len(step.images) >= 20:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A step can have at most 20 images")
        image_id = uuid4()
        data_service = GuideDataService(guide.id)
        data_service.write_step_image(image_id, image, extension)
        try:
            return self.household_repos.guides.create_step_image(
                guide.id, step.id, image_id, cache.new_key(), caption, alt_text
            )
        except Exception:
            data_service.delete_step_image(image_id)
            raise

    def update_step_image(
        self, slug_or_id: str, step_id: UUID, image_id: UUID, data: GuideStepImageUpdate
    ) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        self._get_step_image(guide, step_id, image_id)
        return self.household_repos.guides.update_step_image(guide.id, step_id, image_id, data.caption, data.alt_text)

    def replace_step_image(
        self, slug_or_id: str, step_id: UUID, image_id: UUID, image: bytes, extension: str
    ) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        self._get_step_image(guide, step_id, image_id)
        GuideDataService(guide.id).write_step_image(image_id, image, extension)
        return self.household_repos.guides.set_step_image_version(guide.id, step_id, image_id, cache.new_key())

    def reorder_step_images(self, slug_or_id: str, step_id: UUID, data: GuideStepImageOrder) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        step = self._get_step(guide, step_id)
        if set(data.image_ids) != {image.id for image in step.images} or len(data.image_ids) != len(step.images):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Image order must contain every step image exactly once")
        return self.household_repos.guides.reorder_step_images(guide.id, step_id, data.image_ids)

    def delete_step_image(self, slug_or_id: str, step_id: UUID, image_id: UUID) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        self._get_step_image(guide, step_id, image_id)
        updated = self.household_repos.guides.delete_step_image(guide.id, step_id, image_id)
        GuideDataService(guide.id).delete_step_image(image_id)
        return updated

    def cover_image_path(self, slug_or_id: str, size: str) -> Path:
        guide = self.get(slug_or_id)
        if not guide.cover_image_version:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide cover image not found")
        path = GuideDataService(guide.id).cover_image_path(size)
        if not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide cover image not found")
        return path

    def step_image_path(self, slug_or_id: str, step_id: UUID, image_id: UUID, size: str) -> Path:
        guide = self.get(slug_or_id)
        self._get_step_image(guide, step_id, image_id)
        path = GuideDataService(guide.id).step_image_path(image_id, size)
        if not path.exists():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide step image not found")
        return path

    def _find(self, repos: AllRepositories, slug_or_id: str) -> GuideRead | None:
        try:
            guide_id = UUID(slug_or_id)
        except ValueError:
            return repos.guides.get_one(slug_or_id)
        return repos.guides.get_one(guide_id, key="id")

    def _get_owned(self, slug_or_id: str) -> GuideRead:
        guide = self._find(self.group_repos, slug_or_id)
        if not guide:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide not found")
        if guide.household_id != self.user.household_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the owning household can change this guide")
        return guide

    @staticmethod
    def _get_step(guide: GuideRead, step_id: UUID):
        step = next((step for step in guide.steps if step.id == step_id), None)
        if not step:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide step not found")
        return step

    def _get_step_image(self, guide: GuideRead, step_id: UUID, image_id: UUID):
        step = self._get_step(guide, step_id)
        image = next((image for image in step.images if image.id == image_id), None)
        if not image:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide step image not found")
        return image

    def _unique_slug(self, title: str) -> str:
        base = slugify(title) or "guide"
        candidate = base
        suffix = 2
        while self.group_repos.guides.get_one(candidate):
            candidate = f"{base}-{suffix}"
            suffix += 1
        return candidate

    def _validate_step_ids(self, guide: GuideRead, data: GuideUpdate) -> None:
        for step in data.steps:
            if not step.id:
                continue
            owner_id = self.session.scalar(select(GuideStepModel.guide_id).where(GuideStepModel.id == step.id))
            if owner_id != guide.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guide step does not belong to this guide")

    def _validate_callout_ids(self, guide: GuideRead, data: GuideUpdate) -> None:
        for callout in data.callouts:
            if not callout.id:
                continue
            owner_id = self.session.scalar(select(GuideCalloutModel.guide_id).where(GuideCalloutModel.id == callout.id))
            if owner_id != guide.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guide callout does not belong to this guide")

    def _validate_requirement_ids(self, guide: GuideRead, data: GuideUpdate) -> None:
        for requirement in data.requirements:
            if not requirement.id:
                continue
            owner_id = self.session.scalar(
                select(GuideRequirementModel.guide_id).where(GuideRequirementModel.id == requirement.id)
            )
            if owner_id != guide.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guide requirement does not belong to this guide")

    def _validate_source_ids(self, guide: GuideRead, data: GuideUpdate) -> None:
        for source in data.sources:
            if not source.id:
                continue
            owner_id = self.session.scalar(select(GuideSourceModel.guide_id).where(GuideSourceModel.id == source.id))
            if owner_id != guide.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guide source does not belong to this guide")

    def _validate_related_guide_ids(self, guide_id: UUID | None, related_guide_ids: Sequence[UUID]) -> None:
        if len(related_guide_ids) != len(set(related_guide_ids)):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Related guides must be unique")
        if guide_id and guide_id in related_guide_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "A guide cannot relate to itself")
        if not related_guide_ids:
            return
        found_ids = set(
            self.session.scalars(
                select(GuideModel.id).where(
                    GuideModel.group_id == self.user.group_id,
                    GuideModel.id.in_(related_guide_ids),
                )
            ).all()
        )
        if found_ids != set(related_guide_ids):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Related guide not found in this group")
