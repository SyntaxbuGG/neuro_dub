
import re
from pathlib import Path
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def clean_file_name(vid_path_obj: Path) -> str:
    clean_filename = re.sub(r'[^\w\s-]', '', vid_path_obj.stem).strip()[:50]
    clean_filename = re.sub(r'[-\s]+', '_', clean_filename)
    if not clean_filename:
        clean_filename = "unknown_name_video"
    return clean_filename


def build_audio_dir_filename(vid_path_obj: Path, audio_base_dir: Path) -> Path:
    filename = clean_file_name(vid_path_obj)
    audio_dir_filename = audio_base_dir / filename
    audio_dir_filename.mkdir(parents=True, exist_ok=True)
    return audio_dir_filename


class ProjectContext:
    def __init__(self, video_file: Path | str, base_storage: Path):
        self.id = str(uuid.uuid4())[:8]  # Уникальный ID проекта
        self.video_path = (video_file)
        self.clean_name = clean_file_name(self.video_path)
        self.project_name_id = f"{self.clean_name}_{self.id}"
        self.project_root = base_storage / "projects" / self.project_name_id

        self.raw_uploads = base_storage / "raw_uploads"
        self.source_dir = self.project_root / "input"
        self.audio_dir = self.project_root / "audio"
        self.text_dir = self.project_root / "text"
        self.final_dir = self.project_root / "final"

        self._create_dirs()

        logger.info(f"Project context initialized: {self.project_root}")

    def _create_dirs(self):
        """Внутренний метод для создания структуры."""
        for folder in [self.raw_uploads, self.source_dir, self.audio_dir, self.text_dir, self.final_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _prepare_name(raw_name: str) -> str:
        name = re.sub(r'[^\w\s-]', '', raw_name).strip().lower()
        name = re.sub(r'[-\s]+', '_', name)[:50]
        return name if name else "unknown_video"
