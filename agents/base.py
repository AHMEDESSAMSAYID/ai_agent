from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def handle(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        كل Agent لازم يطبّق فانكشن handle
        """
        pass
