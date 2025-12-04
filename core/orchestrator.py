from typing import Dict, Any
from agents.support_agent import SupportAgent
from agents.operations_agent import OperationsAgent
from core.nlp import extract_entities  # 👈 مهم

class Orchestrator:
    def __init__(self):
        self.agents = {
            "support": SupportAgent(),
            "operations": OperationsAgent()
        }

    async def handle(self, message: str, context: Dict[str, Any]):
        # NLP كامل
        slots = await extract_entities(message)

        # اختيار الوكيل
        agent_name = slots.get("agent") or "support"
        agent = self.agents.get(agent_name, self.agents["support"])

        # مرّر الـ slots في context
        context = dict(context)
        context["slots"] = slots

        result = await agent.handle(message, context)

        return {
            "selected_agent": agent_name,
            "slots": slots,
            **result
        }
