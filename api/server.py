from fastapi import FastAPI
from pydantic import BaseModel
from core.orchestrator import Orchestrator

app = FastAPI(title="AI Ops Backend")

orch = Orchestrator()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_role: str | None = "guest"
    metadata: dict | None = {}

class ChatResponse(BaseModel):
    agent: str
    reply: str
    tool_result: dict | list | None = None
    entities: dict | None = None
  

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):

    context = {
        "session_id": req.session_id,
        "user_role": req.user_role,
        "metadata": req.metadata,
    }

    result = await orch.handle(req.message, context)

    return ChatResponse(
        agent=result.get("agent"),
        reply=result.get("reply"),
        tool_result=result.get("tool_result"),
        entities=result.get("entities"),
    )
print(" fd AI Ops Backend is running..." )