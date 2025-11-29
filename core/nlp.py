# ai_agent/core/nlp.py

import json
import re
from typing import Dict, Any

from core.llm_client import call_llm
from db.memory_dal import MemoryDAL


CITY_MAP = {
    "جدة": "Jeddah",
    "جده": "Jeddah",
    "الرياض": "Riyadh",
    "رياض": "Riyadh",
    "دمام": "Dammam",
    "الدمام": "Dammam",
}

EXTRACTION_PROMPT = """
أنت مسؤول عن تحليل طلبات تخص عمليات شركة لوجستيات.

استخرج فقط:
intent, city, driver, status, time_range, tracking

أرجع JSON فقط بدون أي نص إضافي.
"""


async def _normalize_entities(data: Dict[str, Any]) -> Dict[str, Any]:
    """تنظيف وضبط المفاتيح"""
    city = data.get("city")
    if city:
        data["city"] = CITY_MAP.get(str(city).strip(), city)

    fields = ["intent", "city", "driver", "status", "time_range", "tracking"]
    for f in fields:
        data.setdefault(f, None)

    return data


async def extract_entities(text: str) -> Dict[str, Any]:
    """
    NLP + PostgreSQL Cache
    """

    # -----------------------------------------
    # 1) CHECK CACHE
    # -----------------------------------------
    cached = await MemoryDAL.get_nlp_cache(text)
    if cached:
        print("🔵 NLP CACHE HIT")
        return await _normalize_entities(cached)

    print("🟠 NLP CACHE MISS → calling LLM")

    # -----------------------------------------
    # 2) CALL LLM
    # -----------------------------------------
    raw = await call_llm(
        system_prompt=EXTRACTION_PROMPT,
        user_message=text,
    )

    raw = raw.replace("```json", "").replace("```", "").strip()

    # -----------------------------------------
    # 3) EXTRACT JSON
    # -----------------------------------------
    matches = re.findall(r"\{[\s\S]*?\}", raw)
    if not matches:
        print("⚠️ NLP: no JSON detected:", raw)
        return await _normalize_entities({})

    json_text = matches[0]

    json_text = (
        json_text.replace("NULL", "null")
                 .replace("TRUE", "true")
                 .replace("FALSE", "false")
    )

    try:
        data = json.loads(json_text)
    except:
        print("⚠️ JSON Parse Error:", json_text)
        data = {}

    if not isinstance(data, dict):
        data = {}

    data = await _normalize_entities(data)

    # -----------------------------------------
    # 4) SAVE TO CACHE (JSONB)
    # -----------------------------------------
    try:
        await MemoryDAL.save_nlp_cache(
            text,
            json.dumps(data, ensure_ascii=False)  # <-- IMPORTANT!
        )
        print("🟢 NLP CACHE SAVED")
    except Exception as e:
        print("⚠️ Cache Save Error:", e)

    return data
