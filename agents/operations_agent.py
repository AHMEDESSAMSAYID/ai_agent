# agents/operations_agent.py

import asyncio
import json
from typing import Dict, Any

from core.corrections import detect_correction
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
- اعرض النتائج بشكل منظم وواضح.
"""


class OperationsAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="operations")

    async def handle(self, message: str, context: Dict[str, Any]):

        # =============== Short-Term Memory ===============
        await self.remember_message(role="user", content=message)

        recent = await self.get_recent_messages(3)
        recent_msgs = [f"{m['role']}: {m['content']}" for m in recent]

        # =============== Episode ID ===============
        episode_id = context.get("episode_id", "default")

        await self.remember_event(
            episode_id=episode_id,
            content=message,
            kind="user_message",
        )

        # =============== Detect Manager Corrections ===============
        correction = await detect_correction(message)

        if context.get("user_role") == "manager" and correction.get("is_correction"):

            await self.remember_knowledge(
                content=f"{correction['key']} = {correction['value']}",
                category=correction["type"],
            )

            await self.remember_event(
                episode_id=episode_id,
                content=json.dumps(correction, ensure_ascii=False),
                kind="correction_saved",
            )

        # =============== Load Long-Term Memory ===============
        rules = await self.get_knowledge("rule")
        styles = await self.get_knowledge("style")

        long_term_text = "\n".join(
            f"[{item['kind']}] {item['content']}" for item in rules + styles
        )

        # =============== Slots ===============
        slots = context.get("slots") or (await extract_entities(message))

        intent = slots.get("intent")
        city = slots.get("city")
        driver = slots.get("driver")
        status = slots.get("status")
        time_range = slots.get("time_range")
        tracking = slots.get("tracking")
        order_id = slots.get("order_id")

        tool_result = None

        # =============== Select Tool ===============
        if intent == "delay_report":
            tool_result = await get_delayed_shipments(city, driver, time_range)

        elif intent == "city_summary" and city:
            tool_result = await get_city_summary(city)

        elif intent == "driver_report" and driver:
            tool_result = await get_driver_performance(driver)

        elif intent == "status_list":
            tool_result = await list_shipments_by_status(status or "any", city)

        elif intent == "area_heatmap" and city:
            tool_result = await get_area_heatmap(city)

        elif intent == "failure_reasons":
            tool_result = await analyze_failure_reasons(city, time_range)

        # =============== Log NLP Slots ===============
        await self.remember_event(
            episode_id=episode_id,
            content=json.dumps(slots, ensure_ascii=False),
            kind="nlp_slots",
        )

        # =============== Log Tool Output ===============
        await self.remember_tool_output(
            episode_id=episode_id,
            output=tool_result or {},
        )

        # =============== LLM Response ===============
        extra_context = {
            "intent": intent,
            "slots": slots,
            "tool_result": tool_result,
            "recent_messages": recent_msgs,
            "long_term_memory": long_term_text,
        }

        reply = await call_llm(
            system_prompt=OPERATIONS_PROMPT,
            user_message=message,
            extra_context=json.dumps(extra_context, ensure_ascii=False),
        )

        # =============== Log Agent Reply ===============
        await self.remember_event(
            episode_id=episode_id,
            content=reply,
            kind="agent_reply",
        )

        return {
            "agent": self.name,
            "reply": reply,
            "slots": slots,
            "tool_result": tool_result,
            "episode_id": episode_id,
        }
