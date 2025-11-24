# core/llm_client.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# حمل متغيرات البيئة من ملف .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. تأكد إنك حاطط المفتاح في ملف .env")

# إنشاء العميل
client = OpenAI(api_key=api_key)

async def call_llm(system_prompt: str, user_message: str, extra_context: str = "") -> str:
    """
    دالة عامة لاستدعاء الـ LLM
    """
    # هنضمّن السياق مع رسالة المستخدم
    content = f"{system_prompt}\n\nالسياق:\n{extra_context}\n\nرسالة المستخدم:\n{user_message}"

    # استدعاء الموديل
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # استخدم موديل متاح فعلاً
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": content},
        ],
    )

    # ❗ في النسخة الجديدة من مكتبة OpenAI:
    # message مش dict، لكن object، فلازم نستخدم .content مش ["content"]
    return completion.choices[0].message.content
