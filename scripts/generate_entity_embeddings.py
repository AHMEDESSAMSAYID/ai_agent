# scripts/generate_entity_embeddings.py

import asyncio
import os
import sys
from pathlib import Path

# إضافة مسار المشروع إلى sys.path قبل استيراد الحزم المحلية
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from openai import AsyncOpenAI
from db.entities_repo import EntitiesRepository



MODEL = "text-embedding-3-small"


async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY env var is not set")

    client = AsyncOpenAI(api_key=api_key)
    repo = EntitiesRepository()

    entities = await repo.all()
    if not entities:
        print("⚠️ لا توجد أي كيانات في جدول entities. أضف بيانات أولاً.")
        return

    print(f"🔎 Found {len(entities)} entities, generating embeddings...")

    for ent in entities:
        # لو عنده embedding بالفعل نعدّيه (تقدر تشيل الشرط لو عايز تعيد التوليد)
        if ent.embedding:
            print(f"⏭️  Skipping id={ent.id} ({ent.type}:{ent.normalized_value}) – already has embedding")
            continue

        text = ent.normalized_value
        if ent.synonyms:
            text += " " + " ".join(ent.synonyms)

        print(f"🧠 Embedding id={ent.id} ({ent.type}:{ent.normalized_value}) ...")

        resp = await client.embeddings.create(
            model=MODEL,
            input=text,
        )
        embedding = resp.data[0].embedding

        await repo.update_embedding(ent.id, embedding)

    print("✅ Done generating embeddings.")


if __name__ == "__main__":
    asyncio.run(main())
