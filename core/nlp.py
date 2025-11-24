# ai_agent/core/nlp.py

import json
from typing import Dict, Any
from core.llm_client import call_llm

EXTRACTION_PROMPT = """
أنت مسؤول عن تحليل طلبات تخص عمليات شركة لوجستيات.

من الرسالة القادمة، استخرج المعلومات التالية إن وجدت:
- intent: نوع الطلب. واحد من:
  - delay_report
  - city_summary
  - driver_report
  - status_list
  - area_heatmap
  - failure_reasons
- city: اسم المدينة إن وجد (مثال: Jeddah, Riyadh, جدة، الرياض)
- driver: اسم السائق إن وجد
- status: حالة الشحنات إن وجدت (delayed, delivered, any)
- time_range: فترة زمنية إن وجدت (today, yesterday, last_week, last_7_days)
- tracking: رقم شحنة إن وجد

أرجع النتيجة بصيغة JSON فقط، بدون أي نص إضافي.
مثال:
{"intent": "delay_report", "city": "Jeddah", "driver": null, "status": "delayed", "time_range": "last_week", "tracking": null}
"""

async def extract_entities(text: str) -> Dict[str, Any]:
    raw = await call_llm(
        system_prompt=EXTRACTION_PROMPT,
        user_message=text,
        extra_context=""
    )

    # نحاول نقرأ JSON من الرد
    try:
        # لو الـ model رجع كلام قبل/بعد JSON، نحاول نلقط أول { لآخر }
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw = raw[start : end + 1]

        data = json.loads(raw)
        if not isinstance(data, dict):
            return {}
        return data
    except Exception as e:
        print("❗ NLP parsing error:", e, "| raw:", raw)
        return {}
