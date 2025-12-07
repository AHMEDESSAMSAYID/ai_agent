# voice_agent.py
import asyncio
import io
import os
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI

from core.orchestrator import Orchestrator

# ------------------------------------------------------
# Load environment variables
# ------------------------------------------------------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. تأكد إنك حاطط المفتاح في ملف .env")

client = AsyncOpenAI(api_key=api_key
                     
                     )


# ------------------------------------------------------
# SPEECH-TO-TEXT (Whisper)
# ------------------------------------------------------
class SpeechToText:

    async def transcribe(self, audio_bytes: bytes) -> str:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "chunk.webm"

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ar"
        )

        return response.text.strip()


# ------------------------------------------------------
# TEXT-TO-SPEECH (OpenAI Realtime TTS)
# ------------------------------------------------------
class TextToSpeech:

    async def synthesize(self, text: str) -> bytes:
        response = await client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",       # أفضل صوت – قابل للتغيير لاحقًا
            input=text,
            response_format="wav"
        )
        audio_bytes = await response.aread()
        return audio_bytes


# ------------------------------------------------------
# FULL VOICE SESSION (MAIN ENGINE)
# ------------------------------------------------------
class VoiceSession:
    """
    يمثل جلسة اتصال صوتي واحدة. 
    تُستخدم لكل مستخدم أثناء مكالمة WebRTC.
    """

    def __init__(self, caller_id: str, episode_id: Optional[str] = None):
        self.caller_id = caller_id
        self.episode_id = episode_id or caller_id

        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.orch = Orchestrator()

    async def process_audio_turn(self, audio_bytes: bytes) -> dict:
        # -----------------------------
        # 1) Speech → Text
        # -----------------------------
        user_text = await self.stt.transcribe(audio_bytes)

        if not user_text:
            user_text = "… (لم يُفهم الصوت)"

        # -----------------------------
        # 2) AI Reasoning via Orchestrator
        # -----------------------------
        context = {
            "caller_id": self.caller_id,
            "episode_id": self.episode_id,
            "channel": "voice_call",
        }

        agent_reply = await self.orch.handle(user_text, context)

        # extract text from dict if needed:
        if isinstance(agent_reply, dict) and "reply" in agent_reply:
            reply_text = agent_reply["reply"]
        else:
            reply_text = str(agent_reply)

        reply_text = self._qatari_style(reply_text)

        # -----------------------------
        # 3) Text → Voice
        # -----------------------------
        reply_audio = await self.tts.synthesize(reply_text)

        return {
            "user_text": user_text,
            "reply_text": reply_text,
            "reply_audio": reply_audio,
        }

    # --------------------------------------------------
    # OPTIONAL: Make AI's Arabic feel Qatari/Gulf
    # --------------------------------------------------
    @staticmethod
    def _qatari_style(text: str) -> str:
        custom = {
            "مرحبا": "مرحبا فيك",
            "كيف أساعدك": "شلون أقدر أساعدك",
            "صديقنا": "خويّنا",
            "عزيزي": "يابو فلان",
        }
        for k, v in custom.items():
            text = text.replace(k, v)
        return text
