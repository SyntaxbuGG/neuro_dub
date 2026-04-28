

from settings import BASE_DIR, audio_path_out, video_path_obj, CHUNK_DUR, AudioFormat, CURRENT_FORMAT_AUDIO
from modules.tools import build_audio_dir_filename, clean_file_name
from audio_separator.separator import Separator
from pathlib import Path
import logging


logger = logging.getLogger(__name__)

custom_model_dir = BASE_DIR / "audio-sep-models"
custom_model_dir.mkdir(parents=True, exist_ok=True)


class AudioSep:
    def __init__(self, model: str, output_dir: Path):
        self.output_dir = output_dir / "audio_sep"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.separator = Separator(
            chunk_duration=CHUNK_DUR, model_file_dir=custom_model_dir, output_dir=self.output_dir, use_soundfile=True, use_autocast=True, output_single_stem="Vocals")
        self.separator.load_model(model)

    def separate_aud(self, audio_files_path: list[Path], audio_format: AudioFormat = CURRENT_FORMAT_AUDIO) -> list[str]:
        final_res = []
        for p in audio_files_path:
            try:
                clean_filename = clean_file_name(p)
                vocal_path = self.output_dir / \
                    f"(vocals)_output{audio_format.value}"

                if vocal_path.exists():
                    logger.info(
                        f"Skipping separation: {clean_filename} already processed.")
                    final_res.append(str(vocal_path))
                    continue

                output_names = {
                    "Vocals": f"(vocals)_output",
                }
                self.separator.separate(
                    str(p), custom_output_names=output_names)

                final_res.append(str(vocal_path))
            except Exception as e:
                logger.warning((f"Skip broken chunk: {p} | {e}"))

        return final_res
