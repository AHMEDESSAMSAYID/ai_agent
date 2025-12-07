from typing import Dict, Any
from agents.support_agent import SupportAgent
from agents.operations_agent import OperationsAgent
from core.nlp import extract_entities  # 👈 مهم
import live_log_bus


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

        # 🔴 broadcast: nlp slots
        await live_log_bus.broadcast({
            "type": "nlp_slots",
            "slots": slots,
        })
         # 🔴 broadcast: orchestrator event (قبل ما ننادي الـ agent)
        await live_log_bus.broadcast({
            "type": "orchestrator_event",
            "message": message,
            "intent": slots.get("intent"),
            "selected_agent": agent_name,
        })

        result = await agent.handle(message, context)
        
        # 🔴 broadcast: agent response
        await live_log_bus.broadcast({
            "type": "agent_response",
            "reply": result.get("reply"),
            "raw": result,
        })

        return {
            "selected_agent": agent_name,
            "slots": slots,
            **result
        }
