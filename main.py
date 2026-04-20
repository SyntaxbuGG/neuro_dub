import json

from settings import use_chunks, video_path, video_path_obj, target_langs, source_langs

from modules.video_processor import VideoProcessor
from modules.audio_separator import AudioSeparator
from modules.transcriber import FasterWhisperTranscriber
from modules.save_text import save_to_json_file, load_segments_from_json
from modules.translator import translate_gpt_api_structured_output
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO)


source = "source"
translated = "translated"
target_lang = target_langs[0]
source_lang = source_langs[0]

video_proc = VideoProcessor()
audio_path = video_proc.extract_audio(
    f"{video_path}", use_chunks=use_chunks)


separator = AudioSeparator()
stems = separator.separate(audio_path)

file_name = stems[0]["file_name"]

# путь где сохраняешь оригинал текст аудио
orig_json_path = Path("storage/text") / file_name / \
    f"{file_name}_{source_lang}_{source}.json"
if not orig_json_path.exists():
    transcriber = FasterWhisperTranscriber(device="cuda")
    fastwhisper = transcriber.transcribe(stems[0]["vocals"])
    save_to_json_file(
        segments=fastwhisper[0], stage=source, metadata=fastwhisper[1], file_name=stems[0]["file_name"])
    segments_orig = fastwhisper[0]
else:
    logging.info(f"Skipping {orig_json_path} file  already exists")
    segments_orig = load_segments_from_json(orig_json_path)

# путь где сохраняешь перевод текст аудио
trans_json_path = Path("storage/text")/file_name / \
    f"{file_name}_{target_lang}_{translated}.json"
if not trans_json_path.exists():
    gpt = translate_gpt_api_structured_output(
        segments_orig, target_lang=target_lang)
    segments_trans = gpt.output_parsed.model_dump()["translated"]
    save_to_json_file(segments=segments_trans,
                      file_name=stems[0]["file_name"], stage=translated, lang=target_lang)
else:
    logging.info(f"Skipping translation {trans_json_path}")
    segments_trans = load_segments_from_json(trans_json_path)

