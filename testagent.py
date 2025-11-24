import asyncio
from core.orchestrator import Orchestrator

async def test():
    orch = Orchestrator()

    print("🟦 اختبار خدمة العملاء:")
    res1 = await orch.handle("فين شحنتي رقم 123؟", {"user_role": "support"})
    print(res1, "\n")

    print("🟧 اختبار العمليات:")
    res2 = await orch.handle("عايز تقرير عن التأخير في جدة", {"user_role": "operations"})
    print(res2, "\n")

asyncio.run(test())
