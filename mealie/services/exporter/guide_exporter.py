from collections.abc import Iterator
from uuid import UUID

from mealie.repos.all_repositories import AllRepositories
from mealie.schema.guide import GuideRead

from ._abc_exporter import ABCExporter, ExportedItem


class GuideExporter(ABCExporter):
    """Export portable Guide JSON and its self-contained media directory."""

    def __init__(self, db: AllRepositories, group_id: UUID, guide_ids: list[UUID]) -> None:
        super().__init__(db, group_id)
        self.guide_ids = guide_ids

    @property
    def destination_dir(self) -> str:
        return "guides"

    def items(self) -> Iterator[ExportedItem]:
        for guide_id in self.guide_ids:
            guide = self.db.guides.get_one(guide_id, key="id")
            if guide:
                yield ExportedItem(name=guide.slug, model=guide)

    def serialize_item(self, item: ExportedItem) -> str:
        return item.model.model_dump_json(by_alias=True, indent=2)

    def _post_export_hook(self, item: GuideRead) -> None:
        from mealie.services.guide.guide_data_service import GuideDataService

        guide_dir = GuideDataService(item.id).guide_dir
        if guide_dir.exists() and self.write_dir_to_zip:
            self.write_dir_to_zip(guide_dir, f"{self.destination_dir}/{item.slug}/media", set())
