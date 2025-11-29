import asyncio
from core.nlp import extract_entities
from db.memory_dal import MemoryDAL


async def main():
    text = "عاوز تقرير عن التأخير خلال الأسبوع الماضي"

    print("\n=== CALL 1 (Should be LLM) ===")
    result1 = await extract_entities(text)
    print("Result 1:", result1)

    print("\n=== CALL 2 (Should be CACHE) ===")
    result2 = await extract_entities(text)
    print("Result 2:", result2)

    print("\n=== CHECK DIRECT DATABASE CACHE ===")
    cached = await MemoryDAL.get_nlp_cache(text)
    print("Cached in DB:", cached)


if __name__ == "__main__":
    asyncio.run(main())
