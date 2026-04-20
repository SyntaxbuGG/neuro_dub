

from modules.schemas import Segment, TranscriptionMetadata

from typing import Any
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def save_to_json_file(segments: list[Segment], file_name: str, stage: str, lang: str | None = None, metadata: TranscriptionMetadata | None = None):

    try:
        base_dir = Path(f"storage/text")/file_name
        base_dir.mkdir(exist_ok=True, parents=True)
        full_path = base_dir / \
            f"{file_name}_{metadata.get('language', "unknown") if metadata else lang}_{stage}.json"

        data_to_save = {
            "metadata": metadata,
            "segments": segments
        }

        with open(full_path, "w", encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error saving json file: {e}")


def load_segments_from_json(json_path: Path) -> list[Segment]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["segments"]

# def save_as_json(transcription_data: tuple[list[Segment], TranscriptionMetadata]):
#     segments, info = transcription_data
#     data_to_save = {
#         "segments": segments
#     }
#     try:
#         file_path = Path("data_result.json")
#         with open(file_path, "w", encoding='utf-8') as f:
#             json.dumps(data_to_save, ensure_ascii=False, separators=(",", ":"))
#         print(f"Готово! Результат сохранен в {file_path}")
#     except Exception as e:
#         print(f"Ошибка при сохранении файла: {e}")
