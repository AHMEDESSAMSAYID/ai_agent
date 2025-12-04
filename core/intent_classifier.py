# nlp/intent_classifier.py

import json
from typing import Dict

from core.llm_client import call_llm

INTENT_SYSTEM_PROMPT = """
أنت مصنف نوايا (Intent Classifier) في نظام لوجيستي.

المخرجات يجب أن تكون JSON فقط بدون أي نص إضافي.

احتمالات الـ intent (واختر واحد فقط):
- create_mission        → إنشاء/إرسال مهمة أو شحنة أو طلب توصيل
- driver_status         → حالة السائق أو مكانه أو تأخيره
- city_summary          → تقرير أو ملخص عن مدينة
- driver_report         → تقرير عن سائق
- delay_report          → تقرير عن التأخيرات
- tracking_question     → سؤال عن تتبع شحنة (tracking)
- order_status          → سؤال عن حالة طلب (order id)
- generic_support       → استفسار عام / شكوى / محادثة خدمة عملاء
- unknown               → غير واضح

احتمالات الـ agent:
- support
- operations

أرجع JSON بالصيغة:
{
  "intent": "<واحدة من القائمة>",
  "agent": "<support أو operations>"
}
"""

class IntentClassifier:
    async def classify(self, message: str) -> Dict[str, str]:
        raw = await call_llm(
            system_prompt=INTENT_SYSTEM_PROMPT,
            user_message=message,
        )

        raw = raw.strip()

        # محاولات parsing آمنة
        try:
            data = json.loads(raw)
            intent = data.get("intent", "unknown")
            agent = data.get("agent", "support")
        except Exception:
            # fallback بسيط
            intent = "unknown"
            agent = "support"

        return {
            "intent": intent,
            "agent": agent,
        }
