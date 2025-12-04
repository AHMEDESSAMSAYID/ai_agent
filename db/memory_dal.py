import json
from connection import get_pool


# ======================================================
# SHORT-TERM MEMORY DAL
# ======================================================
class MemoryDAL:

    @staticmethod
    async def add_short_term(agent_name: str, role: str, content: str,
                             kind: str = "message", metadata=None):

        if metadata is None:
            metadata = {}

        metadata_json = json.dumps(metadata, ensure_ascii=False)

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO short_term_messages (agent_name, role, content, kind, metadata)
                VALUES ($1, $2, $3, $4, $5::jsonb)
                """,
                agent_name,
                role,
                content,
                kind,
                metadata_json,
            )

    @staticmethod
    async def get_recent_short_term(limit: int = 5):
        pool = await get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, agent_name, role, content, kind, metadata, created_at
                FROM short_term_messages
                ORDER BY id DESC
                LIMIT $1
                """,
                limit
            )

        result = []
        for r in rows:
            row = dict(r)
            try:
                row["metadata"] = json.loads(row["metadata"]) if row["metadata"] else {}
            except:
                row["metadata"] = {}
            result.append(row)
        return result


# ======================================================
# LONG-TERM MEMORY DAL
# ======================================================
class LongTermDAL:

    @staticmethod
    async def add_knowledge(agent_name: str, content, category: str):

        # حول المحتوى دائماً إلى JSON
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO long_term_knowledge (agent_name, category, content)
                VALUES ($1, $2, $3::jsonb)
                """,
                agent_name,
                category,
                content
            )

    @staticmethod
    async def get_knowledge(agent_name: str, category: str):
        pool = await get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, agent_name, category, content, meta, timestamp
                FROM long_term_knowledge
                WHERE agent_name = $1 AND category = $2
                ORDER BY id DESC
                """,
                agent_name,
                category
            )

        result = []
        for r in rows:
            item = dict(r)
            try:
                item["content"] = json.loads(item["content"])
            except:
                pass
            result.append(item)

        return result


# ======================================================
# EPISODIC MEMORY DAL
# ======================================================
class EpisodicDAL:

    @staticmethod
    async def add_event(agent_name: str, episode_id: str, content, kind: str):

        # حول content إلى JSON دائماً
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        else:
            content = json.dumps({"text": content}, ensure_ascii=False)

        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO episodic_events (agent_name, episode_id, content, kind)
                VALUES ($1, $2, $3::jsonb, $4)
                """,
                agent_name,
                episode_id,
                content,
                kind
            )

    @staticmethod
    async def get_events(episode_id: str):
        pool = await get_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, agent_name, episode_id, content, kind, created_at
                FROM episodic_events
                WHERE episode_id = $1
                ORDER BY id ASC
                """,
                episode_id
            )

        return [dict(r) for r in rows]
