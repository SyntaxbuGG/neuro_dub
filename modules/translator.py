import json
import os

from openai import OpenAI
from dotenv import load_dotenv

from modules.schemas import SubtitleList, Segment

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def translate_gpt_api(text: list[dict]):

#     response = client.responses.create(

#         model="gpt-4.1 nano",
#         instructions="""
# You are a professional subtitle translator.
# Rules:
# - Translate ONLY the "text" field to English
# - DO NOT change "start" or "end"
# - DO NOT remove or add items
# - Keep JSON structure EXACTLY the same
# - Return valid JSON only
# """,
#         input=text,
#         text_format=SubtitleList
#     return response


def translate_gpt_api_structured_output(text: list[Segment], target_lang: str = "en"):
    payload = {"translated": text}
    response = client.responses.parse(
        model="gpt-4.1-nano",
        instructions=f"""
You are a professional subtitle translator.

Rules:
- Translate ONLY the "text" field to {target_lang}
- Preserve meaning, tone, and emotion (NOT literal word-by-word translation)
- DO NOT change "start" or "end"
- DO NOT remove or add items
- Do not paraphrase or improve meaning beyond translation.
- Keep JSON structure EXACTLY the same
- Return valid JSON only
- Keep sentences natural and fluent in spoken English
""",
        text_format=SubtitleList,
        store=False,
        input=[
            {"role": "user",
             "content": json.dumps(text,ensure_ascii=False,separators=(",",":"))}
        ]
    )

    return response
