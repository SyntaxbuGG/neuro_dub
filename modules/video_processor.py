import logging
from pathlib import Path
import subprocess


logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, temp_audio_dir="storage/audio", audio_format='.wav'):
        self.temp_audio_dir = Path(temp_audio_dir)
        self.audio_format = audio_format
        self.temp_audio_dir.mkdir(parents=True, exist_ok=True)

    def extract_audio(self, video_path: str | Path, segment_sec: int = 600, use_chunks: bool = False) -> list[Path]:
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"{video_path} not found")

        output_subdir = self.temp_audio_dir / video_path.stem
        output_subdir.mkdir(parents=True, exist_ok=True)

        if not use_chunks:
            audio_path = output_subdir / \
                f"{video_path.stem}{self.audio_format}"
            if not audio_path.exists():
                command = [
                    "ffmpeg",
                    '-y',
                    "-i", str(video_path),
                    "-vn",
                    "-acodec", "pcm_s16le",  # wav format
                    "-ar", "44100",
                    str(audio_path)
                ]
                subprocess.run(command, check=True)
            else:
                logger.info(f"Audio file already exists: {audio_path}")

            return [audio_path]

        # деление на чанки
        chunks_dir = output_subdir / "chunks_wav"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        chunk_files = sorted(chunks_dir.glob("*.wav"))
        if chunk_files:
            logger.info(
                f"Chunk files already exist: {len(chunk_files)} chunks found")
            return chunk_files

        subprocess.run(["ffmpeg", "-y",
                        "-i", str(video_path),
                        "-vn",
                        "-acodec", "pcm_s16le",  # wav format
                        "-ar", "44100",  # demucs в этом частоте работает
                        "-f", "segment",
                        "-segment_time", str(segment_sec),
                        str(chunks_dir / "chunk_%03d.wav")], check=True)
        chunk_files = sorted(chunks_dir.glob("*.wav"))
        return chunk_files
