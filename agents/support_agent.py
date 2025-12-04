# agents/support_agent.py

import asyncio
import json
import re
from typing import Any, Dict

from core.corrections import detect_correction
from agents.base import BaseAgent
from core.llm_client import call_llm
from core.nlp import extract_entities
from tools.shipments import get_shipment_status

SUPPORT_PROMPT = """
أنت وكيل خدمة عملاء محترف.

القواعد:
- إذا وجد نظام الشحنة رقم تتبع أو رقم أوردر → اعرض حالتها بدقة.
- لا تخمن معلومات غير موجودة في extra_context.
- الرد مهني ومختصر وواضح.
"""


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="support")

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

        # =============== Corrections ===============
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

        # =============== Long-Term Memory ===============
        rules = await self.get_knowledge("rule")
        styles = await self.get_knowledge("style")

        long_term_text = "\n".join(
            f"[{item['kind']}] {item['content']}" for item in (rules + styles)
        )

        # =============== Slots ===============
        slots = context.get("slots") or (await extract_entities(message))

        intent = slots.get("intent")
        tracking = slots.get("tracking")
        order_id = slots.get("order_id")

        tool_results = []

        # =============== Fallback Regex Detection ===============
        if not tracking and not order_id:
            nums = re.findall(r"\d{3,}", message)
            if nums:
                order_id = nums[0]

        # =============== Tool Call ===============
        number = tracking or order_id
        if number:
            status = await get_shipment_status(number)
            tool_results.append({
                "number": number,
                "status": status,
                "is_tracking": bool(tracking),
                "is_order_id": bool(order_id)
            })

        await self.remember_tool_output(
            episode_id=episode_id,
            output=tool_results,
        )

        # =============== LLM ===============
        extra_context = {
            "intent": intent,
            "slots": slots,
            "tracking_results": tool_results,
            "recent_messages": recent_msgs,
            "long_term_memory": long_term_text,
        }

        reply = await call_llm(
            system_prompt=SUPPORT_PROMPT,
            user_message=message,
            extra_context=json.dumps(extra_context, ensure_ascii=False),
        )

        await self.remember_event(
            episode_id=episode_id,
            content=reply,
            kind="agent_reply",
        )

        return {
            "agent": self.name,
            "reply": reply,
            "slots": slots,
            "tool_result": tool_results,
            "episode_id": episode_id,
        }
