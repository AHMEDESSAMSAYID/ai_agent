from typing import Any, Dict, List
from connection import get_pool
import json


class MemoryDAL:

    # --------------------------------
    # SHORT TERM MEMORY
    # --------------------------------
    @staticmethod
    async def add_short_term(agent_name: str, item: Dict[str, Any]):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO short_term_messages (agent_name, role, content, kind, meta)
                VALUES ($1, $2, $3, $4, $5)
                """,
                agent_name,
                item["role"],
                item["content"],
                item["kind"],
                item["meta"],
            )

    @staticmethod
    async def get_recent(agent_name: str, n: int = 5):
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT role, content, kind, meta, timestamp
                FROM short_term_messages
                WHERE agent_name = $1
                ORDER BY id DESC
                LIMIT $2
                """,
                agent_name, n
            )
        return [dict(r) for r in rows]

    # --------------------------------
    # EPISODIC MEMORY
    # --------------------------------
    @staticmethod
    async def add_event(episode_id: str, agent_name: str, item: Dict[str, Any]):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO episodic_events (episode_id, agent_name, kind, content, meta)
                VALUES ($1, $2, $3, $4, $5)
                """,
                episode_id,
                agent_name,
                item["kind"],
                item["content"],
                item["meta"],
            )

    @staticmethod
    async def get_events(episode_id: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT kind, content, meta, timestamp
                FROM episodic_events
                WHERE episode_id = $1
                ORDER BY id ASC
                """,
                episode_id
            )
        return [dict(r) for r in rows]

    # --------------------------------
    # LONG TERM KNOWLEDGE
    # --------------------------------
    @staticmethod
    async def add_long_term(agent_name: str, category: str, content: str, meta: Dict[str, Any]):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO long_term_knowledge (agent_name, category, content, meta)
                VALUES ($1, $2, $3, $4)
                """,
                agent_name, category, content, meta
            )

    @staticmethod
    async def get_long_term(agent_name: str, category: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT category, content, meta, timestamp
                FROM long_term_knowledge
                WHERE agent_name = $1 AND category = $2
                ORDER BY id ASC
                """,
                agent_name, category
            )
        return [dict(r) for r in rows]

    # --------------------------------
    # NLP CACHE
    # --------------------------------
        # --------------------------------
    # NLP CACHE
    # --------------------------------
    @staticmethod
    async def get_nlp_cache(input_text: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT entities
                FROM nlp_cache
                WHERE input_text = $1
                ORDER BY id DESC
                LIMIT 1
                """,
                input_text,
            )
        if not row:
            return None

        entities_json = row["entities"]

    # لو اللي راجع string → نحوله dict
        if isinstance(entities_json, str):

            try:
               return json.loads(entities_json)
            except:
               return None

    # لو asyncpg رجع JSONB جاهز
        return entities_json


    @staticmethod
    async def save_nlp_cache(input_text: str, entities_json: str):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO nlp_cache (input_text, entities)
                VALUES ($1, $2::jsonb)
                """,
                input_text,
                entities_json,
            )
