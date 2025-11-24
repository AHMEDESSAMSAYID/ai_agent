import asyncio
from core.orchestrator import Orchestrator

async def start():
    orch = Orchestrator()

    print("🟦 تجربة خدمة العملاء:")
    res1 = await orch.handle("فين شحنتي رقم 123و456", {"user_role": "support"})
    print(res1, "\n")

    print("🟧 تجربة العمليات:")
    res2 = await orch.handle("عايز تقرير عن التأخير في جدة", {"user_role": "operations"})
    print(res2, "\n")

asyncio.run(start())