from abc import ABC, abstractmethod
from typing import Dict, Any
from db.memory_dal import MemoryDAL


class BaseAgent(ABC):

    def __init__(self, name: str):
        self.name = name

    # ---------- SHORT TERM ----------
    async def remember_message(self, role: str, content: str, kind: str = "message"):
        await MemoryDAL.add_short_term(
            agent_name=self.name,
            item={
                "role": role,
                "content": content,
                "kind": kind,
                "meta": {},
            }
        )

    async def get_recent_messages(self, n: int = 5):
        return await MemoryDAL.get_recent(self.name, n)

    # ---------- EPISODIC ----------
    async def remember_event(self, episode_id: str, content: str, kind: str, meta=None):
        await MemoryDAL.add_event(
            episode_id,
            self.name,
            {
                "content": content,
                "kind": kind,
                "meta": meta or {}
            }
        )

    async def get_episode_events(self, episode_id: str):
        return await MemoryDAL.get_events(episode_id)

    # ---------- LONG TERM ----------
    async def remember_knowledge(self, content: str, category: str):
        await MemoryDAL.add_long_term(
            agent_name=self.name,
            category=category,
            content=content,
            meta={}
        )

    async def get_knowledge(self, category: str):
        return await MemoryDAL.get_long_term(self.name, category)

    # ---------- ABSTRACT ----------
    @abstractmethod
    async def handle(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
