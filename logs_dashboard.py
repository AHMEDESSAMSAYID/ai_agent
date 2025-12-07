# logs_dashboard.py
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import live_log_bus

router = APIRouter()

@router.websocket("/logs/ws")
async def logs_ws(ws: WebSocket):
    await ws.accept()
    await live_log_bus.register(ws)

    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await live_log_bus.unregister(ws)


LOGS_PAGE = """
<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="UTF-8" />
  <title>Agent Logs Dashboard</title>
  <style>
    body { font-family: sans-serif; direction: rtl; }
    #log { white-space: pre-wrap; background: #111; color: #0f0; padding: 10px; height: 90vh; overflow-y: scroll; }
    .line { margin-bottom: 6px; }
  </style>
</head>
<body>

  <h2>📊 Agent Logs (Realtime)</h2>
  <div id="log"></div>

<script>
  const logDiv = document.getElementById("log");

  function appendLine(text) {
      const div = document.createElement("div");
      div.className = "line";
      div.textContent = text;
      logDiv.appendChild(div);
      logDiv.scrollTop = logDiv.scrollHeight;
  }

  function formatEvent(ev) {
      try {
          if (ev.type === "orchestrator_event") {
              return `[ORCH] intent=${ev.intent} | agent=${ev.selected_agent} | text="${ev.message}"`;
          }
          if (ev.type === "nlp_slots") {
              return "[NLP] slots: " + JSON.stringify(ev.slots);
          }
          if (ev.type === "voice_input") {
              return `[VOICE] "${ev.text}"`;
          }
          if (ev.type === "agent_response") {
              return "[AGENT] reply: " + ev.reply;
          }
          return JSON.stringify(ev);
      } catch (e) {
          return JSON.stringify(ev);
      }
  }

  function start() {
      const wsLogs = new WebSocket(`ws://${location.host}/logs/ws`);

      wsLogs.onopen = () => appendLine("✅ Connected to logs stream...");

      wsLogs.onmessage = (msg) => {
          try {
              const data = JSON.parse(msg.data);
              appendLine(formatEvent(data));
          } catch {
              appendLine(msg.data);
          }
      };

      wsLogs.onclose = () => appendLine("❌ Disconnected.");
  }

  start();
</script>

</body>
</html>
"""


@router.get("/logs", response_class=HTMLResponse)
async def logs_page():
    return LOGS_PAGE
