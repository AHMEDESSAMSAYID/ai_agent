import asyncio
from core.orchestrator import Orchestrator
from core.entity_normalizer import EntityNormalizer

# ---------------------------
# Test Sentences
# ---------------------------

TEST_CASES = [
    "ابعت عمرو على القاهرة بكرة",
    "فين السواق خالد؟",
    "عايز تقرير عن السواق عمرو",
    "عايز اعرف الشحنة رقم 445 وصلت ولا لا",
    "اعمل تقرير عن مدينة الجيزة",
    "ايه التأخيرات اللي حصلت امبارح؟",
    "اتابع شحنتي 99887",
]

async def test_agents():
    orch = Orchestrator()
    nlp = EntityNormalizer()

    print("\n====================")
    print("🔍 NLP ONLY TEST")
    print("====================\n")

    for text in TEST_CASES:
        slots = await nlp.parse_all(text)
        print(f"📝 نص: {text}")
        print(f"🎯 Slots: {slots}")
        print("-" * 40)

    print("\n====================")
    print("🤖 AGENT ROUTING TEST")
    print("====================\n")

    context = {"episode_id": "test_episode", "user_role": "user"}

    for text in TEST_CASES:
        print(f"\n====================")
        print(f"📝 الرسالة: {text}")
        print("====================")

        result = await orch.handle(text, context)

        print(f"🤖 الوكيل المختار: {result['selected_agent']}")
        print(f"🎯 Entities: {result['slots']}")
        print(f"🛠 Tool Result: {result.get('tool_result')}")
        print(f"💬 Reply: {result['reply']}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(test_agents())
