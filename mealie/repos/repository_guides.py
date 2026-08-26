from pydantic import UUID4, BaseModel

from mealie.db.models.guide import GuideModel, GuideStepModel
from mealie.repos.repository_generic import HouseholdRepositoryGeneric
from mealie.schema.guide import GuideRead


class RepositoryGuides(HouseholdRepositoryGeneric[GuideRead, GuideModel]):
    """Guide persistence that preserves ordered child IDs during mixed edits."""

    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> GuideRead:
        data = new_data if isinstance(new_data, dict) else new_data.model_dump()
        step_data = data.pop("steps", [])
        entry = self._query_one(match_value=match_value)

        existing_steps = {str(step.id): step for step in entry.steps}
        ordered_steps: list[GuideStepModel] = []
        for step in step_data:
            step_id = step.get("id")
            if step_id and (existing := existing_steps.get(str(step_id))):
                existing.text = step["text"]
                ordered_steps.append(existing)
            else:
                ordered_steps.append(GuideStepModel(session=self.session, text=step["text"]))

        try:
            entry.update(session=self.session, **data)
            entry.steps = ordered_steps
            for position, step in enumerate(entry.steps):
                step.position = position
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return self.schema.model_validate(entry)
