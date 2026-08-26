from collections.abc import Iterable

from pydantic import UUID4, BaseModel
from sqlalchemy import Select, select

from mealie.db.models.guide import (
    GuideCalloutModel,
    GuideCategoryModel,
    GuideModel,
    GuideRequirementModel,
    GuideStepModel,
    GuideTagModel,
)
from mealie.repos.repository_generic import HouseholdRepositoryGeneric
from mealie.schema.guide import GuideRead
from mealie.schema.response import PaginationBase, PaginationQuery


class RepositoryGuides(HouseholdRepositoryGeneric[GuideRead, GuideModel]):
    """Guide persistence for ordered children and group-scoped metadata labels."""

    def create(self, data: GuideRead | BaseModel | dict) -> GuideRead:
        payload = data if isinstance(data, dict) else data.model_dump()
        category_name = payload.pop("category", None)
        tag_names = payload.pop("tags", [])
        step_data = payload.pop("steps", [])
        callout_data = payload.pop("callouts", [])
        requirement_data = payload.pop("requirements", [])
        payload["title_normalized"] = GuideModel.normalize(payload["title"])
        payload["description_normalized"] = GuideModel.normalize(payload.get("description", ""))
        payload["search_document_normalized"] = self._search_document(
            payload, category_name, tag_names, step_data, callout_data, requirement_data
        )

        document = GuideModel(session=self.session, **payload)
        document.category = self._resolve_category(category_name)
        document.tags = self._resolve_tags(tag_names)
        document.steps = [
            GuideStepModel(session=self.session, text=step["text"], tip=step.get("tip")) for step in step_data
        ]
        document.callouts = [
            GuideCalloutModel(session=self.session, kind=callout["kind"], text=callout["text"])
            for callout in callout_data
        ]
        document.requirements = [
            GuideRequirementModel(
                session=self.session,
                kind=requirement["kind"],
                name=requirement["name"],
                note=requirement.get("note"),
            )
            for requirement in requirement_data
        ]
        try:
            self.session.add(document)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return self.schema.model_validate(document)

    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> GuideRead:
        data = new_data if isinstance(new_data, dict) else new_data.model_dump()
        category_name = data.pop("category", None)
        tag_names = data.pop("tags", [])
        step_data = data.pop("steps", [])
        callout_data = data.pop("callouts", [])
        requirement_data = data.pop("requirements", [])
        entry = self._query_one(match_value=match_value)

        entry.steps = self._merge_ordered_children(entry.steps, step_data, GuideStepModel)
        entry.callouts = self._merge_ordered_children(entry.callouts, callout_data, GuideCalloutModel)
        entry.requirements = self._merge_ordered_children(entry.requirements, requirement_data, GuideRequirementModel)
        entry.category = self._resolve_category(category_name)
        entry.tags = self._resolve_tags(tag_names)
        data["title_normalized"] = GuideModel.normalize(data["title"])
        data["description_normalized"] = GuideModel.normalize(data.get("description", ""))
        data["search_document_normalized"] = self._search_document(
            data, category_name, tag_names, step_data, callout_data, requirement_data
        )

        try:
            entry.update(session=self.session, **data)
            for position, step in enumerate(entry.steps):
                step.position = position
            for position, callout in enumerate(entry.callouts):
                callout.position = position
            for position, requirement in enumerate(entry.requirements):
                requirement.position = position
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        return self.schema.model_validate(entry)

    def page_filtered(
        self,
        pagination: PaginationQuery,
        *,
        search: str | None = None,
        guide_type: str | None = None,
        difficulty: str | None = None,
        frequency: str | None = None,
        category: str | None = None,
        tag: str | None = None,
    ) -> PaginationBase[GuideRead]:
        pagination_result = pagination.model_copy()
        query: Select = self._query(with_options=False).filter_by(**self._filter_builder())
        if search:
            query = self.add_search_to_query(query, self.schema, search)
        if guide_type:
            query = query.where(GuideModel.guide_type == guide_type)
        if difficulty:
            query = query.where(GuideModel.difficulty == difficulty)
        if frequency:
            query = query.where(GuideModel.frequency == frequency)
        if category:
            query = query.join(GuideModel.category).where(
                GuideCategoryModel.normalized_name == GuideModel.normalize(category)
            )
        if tag:
            query = query.join(GuideModel.tags).where(GuideTagModel.normalized_name == GuideModel.normalize(tag))
        if not pagination_result.order_by and not search:
            pagination_result.order_by = "created_at"
        query, count, total_pages = self.add_pagination_to_query(query, pagination_result)
        query = query.options(*self.schema.loader_options())
        items = self.session.execute(query).unique().scalars().all()
        return PaginationBase(
            page=pagination_result.page,
            per_page=pagination_result.per_page,
            total=count,
            total_pages=total_pages,
            items=[self.schema.model_validate(item) for item in items],
        )

    def _resolve_category(self, name: str | None) -> GuideCategoryModel | None:
        if not name:
            return None
        normalized = GuideModel.normalize(name)
        category = self.session.scalar(
            select(GuideCategoryModel).where(
                GuideCategoryModel.group_id == self.group_id,
                GuideCategoryModel.normalized_name == normalized,
            )
        )
        if category:
            return category
        return GuideCategoryModel(session=self.session, group_id=self.group_id, name=name)

    def _resolve_tags(self, names: Iterable[str]) -> list[GuideTagModel]:
        tags: list[GuideTagModel] = []
        seen: set[str] = set()
        for name in names:
            normalized = GuideModel.normalize(name)
            if normalized in seen:
                continue
            seen.add(normalized)
            tag = self.session.scalar(
                select(GuideTagModel).where(
                    GuideTagModel.group_id == self.group_id,
                    GuideTagModel.normalized_name == normalized,
                )
            )
            tags.append(tag or GuideTagModel(session=self.session, group_id=self.group_id, name=name))
        return tags

    def _merge_ordered_children(self, existing, incoming: list[dict], model_type):
        existing_by_id = {str(item.id): item for item in existing}
        merged = []
        for item_data in incoming:
            item_id = item_data.get("id")
            if item_id and (item := existing_by_id.get(str(item_id))):
                for key, value in item_data.items():
                    if key != "id":
                        setattr(item, key, value)
                merged.append(item)
            else:
                values = {key: value for key, value in item_data.items() if key != "id"}
                merged.append(model_type(session=self.session, **values))
        return merged

    @staticmethod
    def _search_document(
        data: dict,
        category: str | None,
        tags: Iterable[str],
        steps: Iterable[dict],
        callouts: Iterable[dict],
        requirements: Iterable[dict],
    ) -> str:
        parts = [
            data.get("title", ""),
            data.get("description", ""),
            data.get("guide_type") or "",
            data.get("difficulty") or "",
            data.get("frequency") or "",
            category or "",
            *(str(tag) for tag in tags),
            *(step.get("text", "") for step in steps),
            *(step.get("tip") or "" for step in steps),
            *(callout.get("text", "") for callout in callouts),
            *(requirement.get("name", "") for requirement in requirements),
            *(requirement.get("note") or "" for requirement in requirements),
        ]
        return " ".join(GuideModel.normalize(str(part)) for part in parts if part)
