import logging
from pathlib import Path
import subprocess

from settings import AudioFormat, CHUNK_DUR, CURRENT_FORMAT_AUDIO
import re
from modules.tools import build_audio_dir_filename

logger = logging.getLogger(__name__)


class VideoProcessor:

    def extract_full_audio(self, video_path: Path | str, output_audio_dir: Path, audio_format: AudioFormat = CURRENT_FORMAT_AUDIO) -> list[Path]:
        video_path = self._validate(video_path)
        output_subdir = output_audio_dir
        audio_path = output_subdir / f"{video_path.stem}{audio_format.value}"

        if audio_path.exists():
            logger.info(f"Audio file already exists: {audio_path}")
            return [audio_path]

        args = [
            "-i", str(video_path),
            "-vn",
            "-acodec", audio_format.codec,
        ]

        # Когда надо добавить тишину к аудио и увеличить длительность
        # duration_mov = self._get_duration(video_path)
        # remainder = float(duration_mov) % CHUNK_DUR
        # if 0 < remainder <= 50:
        #     target_duration = float(duration_mov) + 50
        #     logger.info(
        #         f"Short tail detected ({remainder:.2f}s). full_duration: {duration_mov}. Adding 10s padding.")
        #     args.extend(["-af", "apad", "-t", str(target_duration)])

        args.append(str(audio_path))
        self._run_ffmpeg(video_path, audio_path, args)
        return [audio_path]

    def extract_chunks_audio(self, video_path: str | Path, output_audio_dir: Path | str, segment_sec: int = CHUNK_DUR, audio_format: AudioFormat = CURRENT_FORMAT_AUDIO) -> list[Path]:
        video_path = self._validate(video_path)
        output_subdir = build_audio_dir_filename(output_audio_dir, video_path)
        chunks_dir = output_subdir / f"chunks_{audio_format.value}"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        chunk_files = sorted(chunks_dir.glob(f"*{audio_format.value}"))
        if chunk_files:
            logger.info(
                f"Chunk files already exist: {len(chunk_files)} chunks found")
            return chunk_files

        self._run_ffmpeg(video_path, chunks_dir, ["-i", str(video_path),
                                                  "-vn",
                                                  "-acodec", audio_format.codec,
                                                  "-ar", "44100",
                                                  "-f", "segment",
                                                  "-segment_time", str(segment_sec),
                                                  "-reset_timestamps", "1",
                                                  str(chunks_dir / f"chunk_%03d{audio_format.value}")])

        return sorted(chunks_dir.glob(f"*{audio_format.value}"))

    def _run_ffmpeg(self, video_path: Path, audio_output_path, args: list[str]):
        try:
            logger.info(f"Starting audio extraction: {video_path.name}")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "warning"] + args, check=True,
                           #    stderr=subprocess.PIPE,text=True
                           )
            logger.info(f"Successfully extracted: {audio_output_path.name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise

    def _validate(self, video_path: str | Path) -> Path:
        path = Path(video_path)
        if not path.exists():
            raise FileNotFoundError(path)
        return path

    def _get_duration(self, file_path: Path) -> float:

        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    #
