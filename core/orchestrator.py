from typing import Dict, Any
from agents.support_agent import SupportAgent
from agents.operations_agent import OperationsAgent
from core.llm_client import call_llm
from core.normalizer import normalize_city

ROUTER_PROMPT = """
أنت وكيل متخصص في اختيار الوكيل الأنسب للرسالة.
هذه قائمة الوكلاء:

- support → للاستفسارات، العملاء، الشحنات، الشكاوي، حالة الشحنة
- operations → للتقارير، التأخير، السائقين، الأداء، التحليل، التشغيل

اختر واحد فقط بناءً على الرسالة.
أرجع كلمة واحدة فقط: support أو operations.
"""

class Orchestrator:
    def __init__(self):
        self.agents = {
            "support": SupportAgent(),
            "operations": OperationsAgent()
        }

    async def llm_route(self, message: str) -> str:
        route = await call_llm(
            system_prompt=ROUTER_PROMPT,
            user_message=normalize_city(message)
        )
        route = await route.strip().lower()

        if "operations" in route:
            return "operations"
        return "support"

    async def handle(self, message: str, context: Dict[str, Any]):
        # اختيار الذكي للوكيل
        agent_name = await self.llm_route(normalize_city(message))

        agent = self.agents.get(agent_name, self.agents["support"])
        result = await agent.handle(message, context)

        return {
            "selected_agent": agent_name,
            **result
        }
