


from faster_whisper import WhisperModel
from abc import ABC, abstractmethod
from modules.schemas import Segment, TranscriptionMetadata


class BaseTranscriber(ABC):

    @abstractmethod
    def transcribe(self, audio_path: str):
        pass


class FasterWhisperTranscriber(BaseTranscriber):
    def __init__(self, device: str, model_size: str = "large-v3", compute_type: str = "auto"):
        self.model = WhisperModel(
            model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> tuple[list[Segment], TranscriptionMetadata]:
        segments_generator, info = self.model.transcribe(
            audio_path, vad_filter=True, word_timestamps=False)

        segments: list[Segment] = [
            {"start": s.start, "end": s.end, "text": s.text} for s in segments_generator
        ]

        metadata: TranscriptionMetadata = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "duration_after_vad": info.duration_after_vad,
            "all_language_probs": info.all_language_probs[:3]
        }
        return segments, metadata
