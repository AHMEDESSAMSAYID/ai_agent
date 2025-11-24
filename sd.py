import asyncio
from core.llm_client import call_llm

async def test():
    reply = await call_llm(
        system_prompt="أنت مساعد بسيط للترحيب فقط.",
        user_message="هاي، عامل إيه؟",
        extra_context=""
    )
    print("رد الـ LLM:")
    print(reply)

if __name__ == "__main__":
    asyncio.run(test())
