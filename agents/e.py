import json
from dataclasses import dataclass
from typing import List, Optional

from asyncpg.pool import Pool
from connection import get_pool


@dataclass
class Entity:
    id: int
    type: str
    normalized_value: str
    synonyms: list
    embedding: Optional[list]
    metadata: dict


class EntitiesRepository:

    async def get_by_type(self, entity_type: str) -> List[Entity]:
        pool: Pool = await get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, typee, normalized_data, synonyms, embeding, metadata
                FROM entities
                WHERE typee = $1
                """,
                entity_type,
            )

            result = []
            for row in rows:
                raw_emb = row["embeding"]
                if raw_emb is None:
                    emb = None
                else:
                    try:
                        emb = list(raw_emb)
                    except Exception:
                        emb = None

                result.append(
                    Entity(
                        id=row["id"],
                        type=row["typee"],
                        normalized_value=row["normalized_data"],
                        synonyms=row["synonyms"] or [],
                        embedding=emb,
                        metadata=row["metadata"] or {},
                    )
                )

            return result

    async def all(self) -> List[Entity]:
        pool: Pool = await get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, typee, normalized_data, synonyms, embeding, metadata
                FROM entities
                """
            )

            result = []
            for row in rows:
                raw_emb = row["embeding"]
                if raw_emb is None:
                    emb = None
                else:
                    try:
                        emb = list(raw_emb)
                    except Exception:
                        emb = None

                result.append(
                    Entity(
                        id=row["id"],
                        type=row["typee"],
                        normalized_value=row["normalized_data"],
                        synonyms=row["synonyms"] or [],
                        embedding=emb,
                        metadata=row["metadata"] or {},
                    )
                )
            return result

    async def update_embedding(self, entity_id: int, embedding: list[float]):
        pool: Pool = await get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE entities
                SET embeding = $1, updated = NOW()
                WHERE id = $2
                """,
                embedding,
                entity_id,
            )
