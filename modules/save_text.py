

from sympy import EX
from triton import language

from modules.schemas import Segment, TranscriptionMetadata
import time
from typing import Any
import json
import os
from pathlib import Path
import logging
from settings import text_path_out

logger = logging.getLogger(__name__)


def save_to_json_file(segments: list[Segment], json_dir: Path, stage: str, lang: str | None = None):

    try:
        file_name = f"{stage}_{lang}.json" if lang else f"{stage}_original.json"
        full_path = json_dir / file_name
        with open(full_path, "w", encoding='utf-8') as f:
            json.dump(segments, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Error saving json file: {e}")


def load_segments_from_json(json_path: Path) -> list[Segment]:
    if not json_path.exists():
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"Error reading json file: {json_path}", e)
        return {}


def save_metadata_json(output_path: Path, **kwargs):
 
    output_path = output_path / "project_info.json"
    existing_data = load_segments_from_json(output_path)

    if "target_language" in kwargs:
        # Берем старый список языков или создаем новый
        languages = existing_data.get("translated_languages", [])
        new_lang = kwargs["target_language"]

        if new_lang not in languages:
            languages.append(new_lang)

        kwargs["translated_languages"] = languages

    metadata = {
        **existing_data,
        **kwargs,
        "last_update_json": time.strftime("%Y-%m-%d %H:%M:%S"),  #
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
