import re
from typing import Any, Dict
from agents.base import BaseAgent
from core.llm_client import call_llm
from tools.shipments import get_shipment_status

SUPPORT_PROMPT = """
أنت وكيل خدمة عملاء محترف في شركة لوجستيات.

- إذا ذكر المستخدم رقم شحنة، قم باستخراج الرقم.
- استخدم أداة get_shipment_status للحصول على حالتها.
- لو الشحنة موجودة، اشرح حالتها بشكل لطيف وواضح.
- لو الشحنة غير موجودة، اعتذر ولكن بشكل مهني.
- جاوب بشكل مختصر وواضح.
"""

class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="support")

    async def handle(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:

        # استخراج كل أرقام الشحنات من الرسالة
        tracking_numbers = re.findall(r"\d+", message)
        tool_results = []

        if tracking_numbers:
            for number in tracking_numbers:
                status = get_shipment_status(number)
                tool_results.append({
                    "tracking_number": number,
                    "status": status
                })

        # تجهيز المعلومات للـ LLM
        extra_context = {
            "tracking_results": tool_results
        }

        reply = await call_llm(
            system_prompt=SUPPORT_PROMPT,
            user_message=message,
            extra_context=str(extra_context)
        )

        return {
            "agent": self.name,
            "reply": reply,
            "tool_result": tool_results
        }
