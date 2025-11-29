# ai_agent/agents/support_agent.py

import asyncio
import json
import re
from typing import Any, Dict

from agents.base import BaseAgent
from core.llm_client import call_llm
from tools.shipments import get_shipment_status


SUPPORT_PROMPT = """
أنت وكيل خدمة عملاء محترف في شركة لوجستيات.

القواعد:
- إذا ذكر المستخدم رقم شحنة، استخرج الرقم وتحقق من حالتها.
- لا تخترع بيانات غير موجودة في extra_context.
- إذا كانت الشحنة موجودة: اشرح حالتها بلطف وبشكل مهني.
- إذا لم تكن موجودة: اعتذر باحترام.
- الرد يجب أن يكون مختصر وواضح.
"""


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="support")

    async def handle(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:

        # ============ Short-Term Memory ============
        await self.remember_message(role="user", content=message)
        recent = await self.get_recent_messages(3)
        recent_msgs = [
            f"{m['role']}: {m['content']}"
            for m in (recent or [])
        ]

        # ============ Episode ID ============
        episode_id = context.get("episode_id", "default")

        # سجل رسالة المستخدم داخل الأحداث
        await self.remember_event(
            episode_id=episode_id,
            content=message,
            kind="user_message"
        )

        # ============ استخراج Tracking Numbers ============
        tracking_numbers = re.findall(r"\d+", message)
        tool_results = []

        if tracking_numbers:
            for number in tracking_numbers:
                status = await asyncio.to_thread(get_shipment_status, number)

                tool_results.append({
                    "tracking_number": number,
                    "status": status
                })

        # سجل tracking numbers
        await self.remember_event(
            episode_id=episode_id,
            content=json.dumps(tracking_numbers, ensure_ascii=False),
            kind="tracking_detected"
        )

        # سجل tool output
        await self.remember_event(
            episode_id=episode_id,
            content=json.dumps(tool_results, ensure_ascii=False),
            kind="tool_output"
        )

        # ============ Long-Term Memory ============
        rules = await self.get_knowledge("rule")
        styles = await self.get_knowledge("style")

        long_term_text = "\n".join(
            f"[{item['kind']}] {item['content']}"
            for item in (rules + styles)
        )

        # ============ LLM Preparation ============
        extra_context = {
            "tracking_results": tool_results,
            "recent_messages": recent_msgs,
            "long_term_memory": long_term_text,
        }

        reply = await call_llm(
            system_prompt=SUPPORT_PROMPT,
            user_message=message,
            extra_context=json.dumps(extra_context, ensure_ascii=False),
        )

        # سجل رد الوكيل
        await self.remember_event(
            episode_id=episode_id,
            content=reply,
            kind="agent_reply"
        )

        await asyncio.sleep(0)

        return {
            "agent": self.name,
            "reply": reply,
            "tool_result": tool_results,
            "episode_id": episode_id
        }
