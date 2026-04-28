from settings import DEVICE, video_path_obj, BASE_STORAGE, target_lang, AUDIO_MODEL, WHISPER_MODEL

from pipelines.video_pipelines import Pipeline
from modules.tools import ProjectContext
from modules.save_text import save_metadata_json
import time

import logging
logging.basicConfig(level=logging.INFO)


ctx = ProjectContext(video_path_obj, BASE_STORAGE)

save_metadata_json(ctx.text_dir, orig_filename=ctx.video_path.name, first_started_time=time.strftime("%Y-%m-%d %H:%M:%S"),
                   project_name_id=ctx.project_name_id, audio_model=AUDIO_MODEL,
                   transcribe_model=WHISPER_MODEL, device=DEVICE
                   )

run = Pipeline(model_audio_sep=AUDIO_MODEL,
               device=DEVICE, output_dir_audio=ctx.audio_dir, transcribe_model=WHISPER_MODEL)
a = run.run(ctx)
print(a)
