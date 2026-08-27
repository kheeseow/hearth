import shutil
from pathlib import Path
from uuid import UUID

from mealie.core.config import get_app_dirs
from mealie.pkgs import img
from mealie.services._base_service import BaseService


class GuideDataService(BaseService):
    """Stores Guide-owned images without depending on the Recipe domain."""

    def __init__(self, guide_id: UUID | str) -> None:
        super().__init__()
        self.guide_id = guide_id
        self.guide_dir = get_app_dirs().GUIDE_DATA_DIR.joinpath(str(guide_id))
        self.cover_dir = self.guide_dir.joinpath("cover")
        self.step_images_dir = self.guide_dir.joinpath("step-images")
        self.minifier = img.PillowMinifier(purge=True, logger=self.logger)

    def write_cover(self, file_data: bytes, extension: str) -> Path:
        return self._write_image(file_data, extension, self.cover_dir)

    def write_step_image(self, image_id: UUID | str, file_data: bytes, extension: str) -> Path:
        return self._write_image(file_data, extension, self.step_image_dir(image_id))

    def cover_image_path(self, size: str = "original") -> Path:
        return self.cover_dir.joinpath(self._file_name(size))

    def step_image_path(self, image_id: UUID | str, size: str = "original") -> Path:
        return self.step_image_dir(image_id).joinpath(self._file_name(size))

    def step_image_dir(self, image_id: UUID | str) -> Path:
        return self.step_images_dir.joinpath(str(image_id))

    def delete_cover(self) -> None:
        shutil.rmtree(self.cover_dir, ignore_errors=True)

    def delete_step_image(self, image_id: UUID | str) -> None:
        shutil.rmtree(self.step_image_dir(image_id), ignore_errors=True)

    def delete_all_data(self) -> None:
        shutil.rmtree(self.guide_dir, ignore_errors=True)

    def _write_image(self, file_data: bytes, extension: str, image_dir: Path) -> Path:
        normalized_extension = extension.lower().lstrip(".")
        if f".{normalized_extension}" not in img.IMAGE_EXTENSIONS:
            raise ValueError("Unsupported image type")

        image_dir.mkdir(parents=True, exist_ok=True)
        upload_path = image_dir.joinpath(f"upload.{normalized_extension}")
        upload_path.write_bytes(file_data)
        try:
            self.minifier.minify(upload_path)
        except Exception:
            shutil.rmtree(image_dir, ignore_errors=True)
            raise
        return image_dir.joinpath("original.webp")

    @staticmethod
    def _file_name(size: str) -> str:
        return {
            "original": "original.webp",
            "small": "min-original.webp",
            "tiny": "tiny-original.webp",
        }[size]
