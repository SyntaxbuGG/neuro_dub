from enum import Enum
from pathlib import Path
import re
import uuid


video_path = r"storage/video/В погоне за счастьем- золотые слова из фильма.mp4"

target_langs = ["ru", "en", "uz"]
target_lang = target_langs[1]


BASE_DIR = Path(__file__).resolve().parent


# use_chunks = True
CHUNK_DUR = 500

BASE_STORAGE = BASE_DIR / "storage"

video_path_obj = BASE_DIR / video_path
audio_path_out = BASE_DIR / "storage" / "audio"

text_path_out = BASE_DIR / "storage" / "text"

AUDIO_MODEL = "vocals_mel_band_roformer.ckpt"
WHISPER_MODEL = "large-v3"
DEVICE = "cuda"

TRANSLATE_MODEL = "gpt-4.1-nano"

file_name = video_path_obj.stem

source = "source"
translated = "translated"


class AudioFormat(str, Enum):
    WAV = ".wav"
    MP3 = ".mp3"
    FLAC = ".flac"

    @property
    def codec(self) -> str:
        mapping = {
            AudioFormat.WAV: "pcm_s16le",
            AudioFormat.MP3: "libmp3lame",
            AudioFormat.FLAC: "flac",
        }
        return mapping[self]


CURRENT_FORMAT_AUDIO = AudioFormat.WAV


class ProjectContext:
    def __init__(self, video_file: Path, base_storage: Path):
        self.id = str(uuid.uuid4())[:8]  # Уникальный ID проекта
        self.original_video = Path(video_file)
        self.clean_name = self._prepare_name(video_file)

        self.project_root = base_storage / "projects" / \
            f"{self.clean_name}_{self.id}"

        self.source_dir = self.project_root / "source"
        self.audio_dir = self.project_root / "audio"
        self.text_dir = self.project_root / "text"
        self.final_dir = self.project_root / "final"

        self._create_dirs()

        # Путь к оригинальному видео (копируем или ссылаемся)
        self.video_path = video_file

    def _create_dirs(self):
        """Внутренний метод для создания структуры."""
        for folder in [self.source_dir, self.audio_dir, self.text_dir, self.final_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _prepare_name(raw_name: str) -> str:
        """Очистка имени файла от спецсимволов (бывшая clean_file_name)."""
        # Убираем всё кроме букв, цифр, пробелов и дефисов
        name = re.sub(r'[^\w\s-]', '', raw_name).strip().lower()
        # Заменяем пробелы и дефисы на нижнее подчеркивание
        name = re.sub(r'[-\s]+', '_', name)
        # Обрезаем длину (50 символов достаточно)
        name = name[:50]
        return name if name else "unknown_video"
