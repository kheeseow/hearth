from uuid import UUID

from fastapi import HTTPException, status
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.orm import Session

from mealie.db.models.guide import GuideStepModel
from mealie.repos.all_repositories import AllRepositories, get_repositories
from mealie.schema.guide import GuideCreate, GuidePatch, GuideRead, GuideSave, GuideUpdate
from mealie.schema.response import PaginationBase, PaginationQuery
from mealie.schema.user import PrivateUser


class GuideService:
    def __init__(self, session: Session, user: PrivateUser) -> None:
        self.session = session
        self.user = user
        self.household_repos = get_repositories(session, group_id=user.group_id, household_id=user.household_id)
        self.group_repos = get_repositories(session, group_id=user.group_id, household_id=None)

    def list(self, pagination: PaginationQuery, search: str | None = None) -> PaginationBase[GuideRead]:
        return self.group_repos.guides.page_all(pagination, search=search)

    def get(self, slug_or_id: str) -> GuideRead:
        guide = self._find(self.group_repos, slug_or_id)
        if not guide:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide not found")
        return guide

    def create(self, data: GuideCreate) -> GuideRead:
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
        payload = data.model_dump()
        payload.update(
            group_id=guide.group_id,
            household_id=guide.household_id,
            author_id=guide.author_id,
            slug=guide.slug,
        )
        return self.household_repos.guides.update(guide.slug, payload)

    def patch(self, slug_or_id: str, data: GuidePatch) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        merged = GuideUpdate.model_validate(
            {
                **guide.model_dump(include={"title", "description", "steps"}),
                **data.model_dump(exclude_unset=True, exclude_none=True),
            }
        )
        return self.update(guide.slug, merged)

    def delete(self, slug_or_id: str) -> GuideRead:
        guide = self._get_owned(slug_or_id)
        return self.household_repos.guides.delete(guide.slug)

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
