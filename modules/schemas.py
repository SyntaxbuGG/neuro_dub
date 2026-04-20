from typing import TypedDict
from pydantic import BaseModel, RootModel


class Segment(TypedDict):
    start: float
    end: float
    text: str


class TranscriptionMetadata(TypedDict):
    language: str
    language_probability: float
    duration: float
    duration_after_vad: float
    all_language_probs: list[tuple[str, float]]


class SubtitleList(BaseModel):
    translated: list[Segment]
