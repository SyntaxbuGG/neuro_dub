
from modules.video_processor import VideoProcessor
from modules.audio_separator.mdx_audio_sep_process import AudioSep
from modules.transcriber import FasterWhisperTranscriber
from modules.save_text import save_to_json_file, load_segments_from_json, save_metadata_json
from modules.translator import translate_gpt_api_structured_output
from modules.schemas import Segment
from pathlib import Path
from settings import source, target_lang, translated, TRANSLATE_MODEL
from modules.tools import ProjectContext
import logging

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, output_dir_audio: Path, model_audio_sep: str, transcribe_model: str, device: str, ):
        self._init_models(output_dir_audio, model_audio_sep,
                          transcribe_model, device)

    def _init_models(self, output_dir: Path, model_audio_sep: str, transcribe_model: str, device: str):
        logger.info("Инициализация моделей ... Это может занять время")
        self.transcriber = FasterWhisperTranscriber(
            device=device, model_size=transcribe_model)
        self.audio_rep = AudioSep(model=model_audio_sep, output_dir=output_dir)

    def _step_1_extract_audio(self, video_path_obj: Path, audio_path_out: Path) -> list[Path]:
        audio_proc = VideoProcessor()
        extracted_path = audio_proc.extract_full_audio(
            video_path_obj, audio_path_out)
        return extracted_path

    def _step_2_separate_vocal(self, audio_path: list[Path]):

        audio_sep = self.audio_rep.separate_aud(audio_path)
        return audio_sep

    def _step_3_transcribe_batch(self, vocal_paths, base_text_dir: Path, clean_filename: str, source: str) -> list[Segment]:
        results = []
        orig_json_path = base_text_dir / f"{source}_original.json"
        for path in vocal_paths:

            if orig_json_path.exists():
                logger.info(
                    f"Skipping: transcription already exists for {clean_filename}")
                segments_orig = load_segments_from_json(orig_json_path)
                results.append(segments_orig)
                continue

            segments = self.transcriber.transcribe(audio_path=path)
            save_to_json_file(
                segments=segments[0], json_dir=base_text_dir, stage=source)
            save_metadata_json(base_text_dir, **segments[1])
            results.append(segments[0])

        return results

    def _step_4_translate(self, source_segment: list[Segment], target_lang: str,  base_text_dir: Path, translate_model: str):
        trans_json_path = base_text_dir / f"{target_lang}_{translated}.json"
        if trans_json_path.exists():
            logger.info(f"Skipping translation {trans_json_path}")
            segments_trans = load_segments_from_json(trans_json_path)
            return segments_trans
        gpt = translate_gpt_api_structured_output(
            source_segment, model=translate_model, target_lang=target_lang)
        segments_trans = gpt.output_parsed.model_dump()["translated"]
        save_to_json_file(segments=segments_trans, json_dir=base_text_dir,
                          stage=translated, lang=target_lang)
        save_metadata_json(
            base_text_dir, target_lang=target_lang, translation_status="completed", translation_model=translate_model)

    def run(self, ctx: ProjectContext):
        logger.info(f"--- [START] Project ID: {ctx.project_name_id} ---")
        extr_audio = self._step_1_extract_audio(
            ctx.video_path, ctx.audio_dir)
        sep_audio = self._step_2_separate_vocal(extr_audio)
        transcribe = self._step_3_transcribe_batch(
            sep_audio, ctx.text_dir, ctx.clean_name, source)
        translate = self._step_4_translate(
            transcribe, target_lang, ctx.text_dir, TRANSLATE_MODEL)
        return translate
