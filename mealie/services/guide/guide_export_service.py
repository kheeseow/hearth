from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import get_repositories
from mealie.schema.group.group_exports import GroupDataExport
from mealie.schema.user import PrivateUser
from mealie.services.exporter import Exporter, GuideExporter


class GuideExportService:
    """Connect Guide-specific export behavior to Mealie's group export orchestration."""

    def __init__(self, session: Session, user: PrivateUser) -> None:
        self.user = user
        self.repos = get_repositories(session, group_id=user.group_id, household_id=None)

    def export_guides(self, temp_path: Path, guide_ids: list[UUID]) -> GroupDataExport:
        if len(guide_ids) != len(set(guide_ids)):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Guides must be unique")

        guides = [self.repos.guides.get_one(guide_id, key="id") for guide_id in guide_ids]
        if any(guide is None for guide in guides):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Guide not found in this group")

        guide_exporter = GuideExporter(self.repos, self.user.group_id, guide_ids)
        exporter = Exporter(
            self.user.group_id,
            temp_path,
            [guide_exporter],
            name=f"Guide Export ({len(guide_ids)})",
        )
        return exporter.run(self.repos)

    def get_export(self, export_id: UUID4) -> GroupDataExport | None:
        return self.repos.group_exports.get_one(export_id)
