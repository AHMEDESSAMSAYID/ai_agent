# agents/base.py

import json
from db.memory_dal import MemoryDAL, EpisodicDAL, LongTermDAL


class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    # ======================================================
    # SHORT-TERM MEMORY
    # ======================================================
    async def remember_message(self, role: str, content: str):
        await MemoryDAL.add_short_term(
            agent_name=self.name,
            role=role,
            content=content,
            kind="message",
            metadata={}
        )

    async def get_recent_messages(self, limit: int = 5):
        return await MemoryDAL.get_recent_short_term(limit=limit)

    # ======================================================
    # EPISODIC MEMORY
    # ======================================================
    async def remember_event(self, episode_id: str, content: str, kind: str):
        await EpisodicDAL.add_event(
            agent_name=self.name,
            episode_id=episode_id,
            content=content,
            kind=kind
        )

    async def remember_tool_output(self, episode_id: str, output: dict):
        await EpisodicDAL.add_event(
            agent_name=self.name,
            episode_id=episode_id,
            content=json.dumps(output, ensure_ascii=False),
            kind="tool_output"
        )

    # ======================================================
    # LONG-TERM MEMORY
    # ======================================================
    async def remember_knowledge(self, content: str, category: str):
        await LongTermDAL.add_knowledge(
            agent_name=self.name,
            content=content,
            category=category
        )

    async def get_knowledge(self, category: str):
        rows = await LongTermDAL.get_knowledge(
            agent_name=self.name,
            category=category
        )

        return [
            {
                "id": r["id"],
                "kind": r["kind"],
                "content": r["content"],
                "created_at": r["created_at"]
            }
            for r in rows
        ]
