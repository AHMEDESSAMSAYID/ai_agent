# ============================
# multilingual normalizer layer
# ============================

import os
import re
from langdetect import detect
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# تأكد إن عندك key في environment
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_basic(text: str) -> str:
    """تنظيف بسيط قبل إرسال النص للموديل"""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


async def translate_to_english(text: str) -> str:
    """ترجمة النص إلى الإنجليزية باستخدام موديل خفيف"""
    try:
        response = await client.chat.completions.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Translate the following text to English ONLY."},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content.strip()
    except:

        return text  # fallback لو حصل خطأ


async def semantic_normalize(text: str) -> str:
    """
    - يكشف اللغة
    - يترجم العربي
    - يرجّع نص جاهز لعمل embeddings
    """

    text = clean_basic(text)

    try:
        lang = detect(text)
    except:
        lang = "en"

    if lang == "ar":
        translated = await translate_to_english(text)
        return translated
    else:
        return text
