import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AudioSeparator:

    def separate(self, audio_file: list[Path], demucs_model="htdemucs") -> list[dict]:

        if not audio_file:
            raise FileNotFoundError(f"No .wav files found in {audio_file}")

        output_dir = audio_file[0].parent

        to_process = []

        for file in audio_file:
            stem_dir = output_dir / demucs_model / file.stem
            vocal_path = stem_dir / "vocals.wav"
            if not vocal_path.exists():
                to_process.append(file)

            else:
                logger.info(
                    f" Skipping /{file.name} file already exists at {vocal_path}")

        if to_process:
            command = [
                "demucs",
                "-n", demucs_model,
                "-d", "cuda",
                "-o", str(output_dir),
                "--segment", "5",
                "--two-stems", "vocals",
                *map(str, to_process)
            ]
            # Добавляем переменную окружения прямо в запуск, чтобы PyTorch не кэшировал лишнего
            import os
            env = os.environ.copy()
            env["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
            try:
                subprocess.run(command, check=True)

            except subprocess.CalledProcessError as e:
                logger.error(f"Ошибка Demucs: {e}")
                raise

        results = []

        for file in audio_file:
            stem_dir = output_dir / demucs_model / file.stem
            results.append({
                "vocals": stem_dir / "vocals.wav",
                "no_vocals": stem_dir / "no_vocals.wav",
                "file_name": str(file.stem)
            })
        return results
