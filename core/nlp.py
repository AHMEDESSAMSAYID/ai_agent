# core/nlp.py

import re
from typing import Dict, Any

from core.entity_normalizer import EntityNormalizer
from core.intent_classifier import IntentClassifier


def extract_numbers(text: str):
    """
    تمييز:
    - tracking: يبدأ بحرف Z وطويل شوية → Z\d{3,}
    - order_id: أرقام فقط 3-10 digits
    """
    text = text.strip()

    tracking_matches = re.findall(r"\bZ\d{3,}\b", text, flags=re.IGNORECASE)
    tracking = tracking_matches[0] if tracking_matches else None

    # pure numeric order IDs
    order_matches = re.findall(r"\b\d{3,10}\b", text)

    order_id = None
    if order_matches:
        # لو عندنا tracking برقم جواه، نستبعده
        if tracking:
            order_candidates = [n for n in order_matches if n not in tracking]
        else:
            order_candidates = order_matches

        if order_candidates:
            order_id = order_candidates[0]

    return tracking, order_id


async def extract_entities(message: str) -> Dict[str, Any]:
    """
    الـ Pipeline الكامل:
    1) LLM → intent + agent
    2) Embeddings → city / driver / status / time_range
    3) Rules → tracking + order_id
    4) دمج النتيجة كلها في dict واحد جاهز للـ Agents
    """
    classifier = IntentClassifier()
    normalizer = EntityNormalizer()

    # 1) Intent & Agent من LLM
    intent_info = await classifier.classify(message)
    llm_intent = intent_info["intent"]
    agent_hint = intent_info["agent"]

    # 2) Entities من embeddings
    slots_emb = await normalizer.parse_all(message)

    # 3) Tracking + Order Id من rules
    tracking_num, order_id = extract_numbers(message)

    # لو LLM قال إن السؤال عن tracking، ومفيش ز → ناخد أول رقم كـ tracking
    if llm_intent == "tracking_question" and not tracking_num and order_id:
        tracking_num = order_id
        order_id = None

    # 4) اختيار intent النهائي:
    final_intent = llm_intent
    if final_intent == "unknown" and slots_emb.get("intent"):
        final_intent = slots_emb["intent"]

    # 5) الدمج النهائي
    result: Dict[str, Any] = {
        "intent": final_intent,
        "agent": agent_hint,
        "city": slots_emb.get("city"),
        "driver": slots_emb.get("driver"),
        "status": slots_emb.get("status"),
        "time_range": slots_emb.get("time_range"),
        "tracking": tracking_num or slots_emb.get("tracking"),
        "order_id": order_id,
    }

    return result
