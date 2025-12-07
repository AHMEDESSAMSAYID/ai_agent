import os
import json
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import time
import jwt
from fastapi.staticfiles import StaticFiles




load_dotenv()

app = FastAPI(title="AI Ops Backend")
app.mount("/", StaticFiles(directory="api", html=True), name="static")
print("OTHER FILE APP LOADED:", id(app))
# ------------------------------------------
# CORS
# ------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------
# REALTIME CONFIG
# ------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY missing!")

REALTIME_SESSION_CONFIG = {
    "type": "realtime",
    "model": "gpt-realtime-mini",
    "instructions": "انت مساعد صوتي عربي.",
    "output_modalities": ["audio", "text"],
    "audio": {
        "input": {
            "format": {"type": "audio/pcm", "rate": 24000},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 350,
                "create_response": True,
                "interrupt_response": True,
            },
        },
        "output": {
            "format": {"type": "audio/pcm", "rate": 24000},
            "voice": "alloy",
        }
    }
}


# ------------------------------------------
# REALTIME SESSION ENDPOINT (FINAL, FULLY WORKING)
# ------------------------------------------
from fastapi.responses import JSONResponse

@app.post("/realtime/session")
async def realtime_session(request: Request):

    # احصل على SDP الخام من الفرونت
    offer_sdp = (await request.body()).decode("utf-8")

    if not offer_sdp.strip():
        raise HTTPException(status_code=400, detail="Empty SDP")

    # أرسل نفس الـ SDP كما هو إلى OpenAI
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/sdp",
            },
            content=offer_sdp,  # ← لازم يكون SDP فقط
        )

    if res.status_code != 201:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    answer_sdp = res.text

    return Response(content=answer_sdp, media_type="application/sdp")


@app.get("/realtime-token")
async def realtime_token():

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.openai.com/v1/realtime/sessions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "gpt-4o-realtime-preview"}
        )

    session = res.json()

    return {"token": session["client_secret"]["value"]}
