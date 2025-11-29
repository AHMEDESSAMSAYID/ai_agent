import json
from typing import Dict, Any
from core.llm_client import call_llm


CORRECTION_PROMPT = """
أنت نظام متخصص في اكتشاف التصحيحات من نصوص المستخدم.

إذا كانت الرسالة تحتوي على "تصحيح" لمعلومة أو قاعدة أو أسلوب، استخرجها.

أنواع التصحيحات:
- rule: قاعدة جديدة (مثال: "COD يعني الدفع عند الاستلام")
- mapping: تعديل أو إضافة خريطة تحويل (مثال: "جده = Jeddah")
- style: تعديل أسلوب الرد (مثال: "رد عليّ بلهجة رسمية" أو "رد مختصر")

❗ مهم جداً:
- لا تستخرج تصحيحات تخص حالات الشحن أو بيانات متغيرة.
- لا تعتبر التذمر أو النقاش تصحيحاً.
- يجب الاعتماد فقط على التصحيحات الحقيقية.

أرجع JSON فقط بهذا الشكل:
{
  "is_correction": true/false,
  "type": "rule/mapping/style",
  "key": "...",
  "value": "..."
}
"""

async def detect_correction(message: str) -> Dict[str, Any]:
    raw = await call_llm(
        system_prompt=CORRECTION_PROMPT,
        user_message=message
    )

    # إزالة أي code blocks
    raw = raw.replace("```json", "").replace("```", "").strip()

    # محاولة التقاط JSON
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        return {"is_correction": False}

    try:
        data = json.loads(raw[start:end+1])
    except:
        return {"is_correction": False}

    # تأكيد وجود المفاتيح
    data.setdefault("is_correction", False)
    data.setdefault("type", None)
    data.setdefault("key", None)
    data.setdefault("value", None)

    return data
