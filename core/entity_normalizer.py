import os
import numpy as np
from typing import Optional, List, Dict
from openai import AsyncOpenAI

from db.entities_repo import EntitiesRepository, Entity


OPENAI_MODEL = "text-embedding-3-small"


def fix_encoding(s: str) -> str:
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        return s


class EntityNormalizer:
    def __init__(self, repo: Optional[EntitiesRepository] = None):
        self.repo = repo or EntitiesRepository()
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def _embed(self, text: str) -> List[float]:
        resp = await self.client.embeddings.create(
            model=OPENAI_MODEL,
            input=text,
        )
        return resp.data[0].embedding

    def _cosine_sim(self, v1, v2) -> float:
        v1 = np.array(v1)
        v2 = np.array(v2)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return -1.0
        return float(np.dot(v1, v2) / denom)

    async def normalize(self, text: str, entity_type: str) -> Optional[Entity]:
        text = text.strip()
        candidates = await self.repo.get_by_type(entity_type)

        # 1) exact match
        for ent in candidates:
            if text == ent.normalized_value:
                return ent

        # 2) synonym match
        for ent in candidates:
            if text in (ent.synonyms or []):
                return ent

        # 3) embedding match
        input_emb = await self._embed(text)

        best_ent = None
        best_score = -1.0

        for ent in candidates:
            if not ent.embedding:
                continue

            score = self._cosine_sim(input_emb, ent.embedding)

            if score > best_score:
                best_score = score
                best_ent = ent

        if best_ent and best_score > 0.70:
            return best_ent

        return None

    async def parse_all(self, text: str) -> dict:
        """
        1) يحاول يطابق synonyms داخل النص
        2) لو مفيش → يسقط على embeddings
        """

        result = {
            "intent": None,
            "city": None,
            "driver": None,
            "status": None,
            "time_range": None,
            "tracking": None,
        }

        types = ["intent", "city", "driver", "status", "time_range"]
        text_lower = text.lower()

        # ------------------ 1) synonym match ------------------
        for t in types:
            candidates = await self.repo.get_by_type(t)

            for ent in candidates:
                for syn in (ent.synonyms or []):
                    if syn.lower() in text_lower:
                        result[t] = ent.normalized_value
                        break
                if result[t]:
                    break

        # ------------------ 2) embedding fallback ------------------
        for t in types:
            if result[t] is None:
                ent = await self.normalize(text, t)
                if ent:
                    result[t] = ent.normalized_value

        return result
