# D:\ai_agent\voice_demo.py

import os
import json
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.orchestrator import Orchestrator
import live_log_bus
from logs_dashboard import router  # ⬅ داشبورد اللوجز

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY missing!")

orch = Orchestrator()

app = FastAPI(title="Voice Demo")
print("VOICE_DEMO APP LOADED:", id(app))

# نركّب الراوتر بتاع اللوجز
app.include_router(router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------
# API: ربط الصوت مع الـ Orchestrator
# ---------------------------------
# ---------------------------------
# API: ربط الصوت مع الـ Orchestrator
# ---------------------------------
# D:\ai_agent\voice_demo.py (الكود المُحدَّث)

# ---------------------------------
# API: ربط الصوت مع الـ Orchestrator
# ---------------------------------
@app.post("/orchestrate")
async def orchestrate(payload: dict):
    text = payload["text"]

    # 1) لوج: العميل قال إيه (من STT)
    await live_log_bus.broadcast({
        "type": "voice_input",
        "text": text,
    })

    # 2) شغّل الأوركستريتور
    result = await orch.handle(text, context={})

    # ⛔ تم حذف لوج orchestration (مكرر)

    # ⛔ تم حذف لوج ردّ الوكيل (مكرر)

    return {
        "reply": result["reply"],
        "agent": result["selected_agent"],
        "slots": result["slots"],
    }
# ---------------------------------
# صفحة WebRTC (الفرونت)
# ---------------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="UTF-8" />
  <title>Voice Agent Realtime (OpenAI WebRTC)</title>
</head>
<body>

<h2>🎙️ Voice Agent Realtime (OpenAI WebRTC)</h2>
<button id="startBtn">▶ ابدأ</button>

<script>
let dc; // DataChannel

async function start() {

    const pc = new RTCPeerConnection({
        iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }]
    });

    const audio = new Audio();
    audio.autoplay = true;

    pc.ontrack = (e) => {
        audio.srcObject = e.streams[0];
    };

    // -----------------------------
    // Create DataChannel
    // -----------------------------
    dc = pc.createDataChannel("oai-events");

    // -----------------------------
    // Receive events from OpenAI
    // -----------------------------
    dc.onmessage = (ev) => {
        try {
            const data = JSON.parse(ev.data);
            handleEvent(data);
        } catch (err) {
            console.error("Invalid JSON:", ev.data);
        }
    };

    // -----------------------------
    // Microphone
    // -----------------------------
    const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
    mic.getTracks().forEach(t => pc.addTrack(t, mic));

    pc.addTransceiver("audio", { direction: "sendrecv" });

    // -----------------------------
    // Send SDP → Backend
    // -----------------------------
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const resp = await fetch("/realtime/session", {
        method: "POST",
        headers: { "Content-Type": "application/sdp" },
        body: offer.sdp,
    });

    const answerSdp = await resp.text();
    await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });

    console.log("WEBRTC CONNECTED!");

    // -----------------------------
    // Wait for DC to be open
    // -----------------------------
    let tries = 0;
    const waitDC = setInterval(() => {

        console.log("DC STATE:", dc.readyState);

        if (dc.readyState === "open") {
            clearInterval(waitDC);

            dc.send(JSON.stringify({
                type: "session.update",
                session: {
                    modalities: ["audio", "text"],
                    input_text: { enabled: true },
                    input_speech: { enabled: true }
                }
            }));

            console.log("session.update SENT!");
        }

        if (++tries > 40) {
            console.error("DC FAILED TO OPEN");
            clearInterval(waitDC);
        }

    }, 200);
}


// --------------------------------------------
// Handle Realtime Events from OpenAI
// --------------------------------------------
async function handleEvent(ev) {
    console.log("EVENT:", ev);

    if (ev.type === "input_text") {
        const userText = ev.text;

        console.log("USER SAID:", userText);

        const r = await fetch("/orchestrate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: userText })
        });

        const data = await r.json();
        dc.send(JSON.stringify({
            type: "response.create",
            response: {
                modalities: ["audio"],
                instructions: data.reply,
                voice: "alloy",
                language: "ar"
            }
        }));
    }
}

document.getElementById("startBtn").onclick = start;

</script>

</body>
</html>
"""


# ---------------------------------
# WebRTC → OpenAI (SDP exchange)
# ---------------------------------
@app.post("/realtime/session")
async def realtime_session(request: Request):
    offer_sdp = (await request.body()).decode("utf-8")

    if not offer_sdp.strip():
        raise HTTPException(status_code=400, detail="Empty SDP")

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/sdp",
                "OpenAI-Beta": "realtime=v1",
            },
            params={
                "model": "gpt-4o-realtime-preview",
            },
            content=offer_sdp,
        )

    if res.status_code != 201:
        print("OpenAI error:", res.status_code, res.text)
        raise HTTPException(res.status_code, res.text)

    return Response(res.text, media_type="application/sdp")


# صفحة الـ WebRTC
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE
