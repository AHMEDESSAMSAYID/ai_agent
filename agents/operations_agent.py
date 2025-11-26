# ai_agent/agents/operations_agent.py

from typing import Dict, Any
import json
from core.normalizer import ‎semantic_normalize


from agents.base import BaseAgent
from core.llm_client import call_llm
from core.nlp import extract_entities
from tools.operations import (
    get_delayed_shipments,
    get_city_summary,
    get_driver_performance,
    list_shipments_by_status,
    get_area_heatmap,
    analyze_failure_reasons,
)


OPERATIONS_PROMPT = """
أنت وكيل عمليات (Operations Agent) في شركة لوجستيات.

❗ مهم:
- لا تخترع أرقام غير موجودة في البيانات.
- اعتمد فقط على البيانات القادمة في extra_context.
- اعرض النتائج بشكل منظم (نِقَاط أو فقرات قصيرة).
- لو لا توجد بيانات، وضّح ذلك واقترح إجراءات بسيطة.

استخدم لغة عربية مهنية، مختصرة وواضحة.
"""

class OperationsAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="operations")

    async def handle(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # 1) استخرج النوايا والكيانات
        entities = await extract_entities(message)

        intent      = entities.get("intent")
        city        = normalize_city(entities.get("city"))
        driver      = entities.get("driver")
        status      = entities.get("status")
        time_range  = entities.get("time_range")
        tracking    = entities.get("tracking")

        tool_result: Any = None

        # 2) اختيار الأداة المناسبة حسب intent
        if intent == "delay_report":
            tool_result = get_delayed_shipments(
                city=city,
                driver=driver,
                time_range=time_range,
            )

        elif intent == "city_summary":
            if city:
                tool_result = get_city_summary(city)

        elif intent == "driver_report":
            if driver:
                tool_result = get_driver_performance(driver)

        elif intent == "status_list":
            # لو مفيش status، نخليه any
            tool_result = list_shipments_by_status(
                status=status or "any",
                city=city,
            )

        elif intent == "area_heatmap":
            tool_result = get_area_heatmap(city=city)

        elif intent == "failure_reasons":
            tool_result = analyze_failure_reasons(
                city=city,
                time_range=time_range,
            )

        # 3) تجهيز الـ context للـ LLM
        extra_context = {
            "intent": intent,
            "entities": entities,
            "tool_result": tool_result,
        }

        reply = await call_llm(
            system_prompt=OPERATIONS_PROMPT,
            user_message=message,
            extra_context=json.dumps(extra_context, ensure_ascii=False),
        )

        return {
            "agent": self.name,
            "reply": reply,
            "entities": entities,
            "tool_result": tool_result,
        }
