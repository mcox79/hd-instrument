"""
POST /converse - substrate-first cascade routing.

Receives user message + session_id. Classifies intent via PP-198. Routes through PP-123
cascade: substrate-direct templates first (PP-187 / PP-188); LLM (PP-123 fallback) only
for genuinely creative / open-ended requests.

Per strategic reframe: substrate IS the AI; LLM is the language tool when needed.
Expected: ~70% substrate-direct (sub-ms / $0); ~30% LLM-mediated.
"""
from __future__ import annotations
import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.converse import handlers
from backend.converse.intent import Intent, classify
from backend.converse.state import Session, Turn, get_or_create_session, list_sessions

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/converse", tags=["converse"])


# Dispatch table: intent -> handler function
INTENT_TO_HANDLER = {
    Intent.GREETING: handlers.handle_greeting,
    Intent.FAREWELL: handlers.handle_farewell,
    Intent.ACK: handlers.handle_ack,
    Intent.CLARIFICATION: handlers.handle_clarification,
    Intent.FACTUAL: handlers.handle_factual,
    Intent.COMPOSITIONAL: handlers.handle_compositional,
    Intent.COUNTERFACTUAL: handlers.handle_counterfactual,
    Intent.COMPUTATION: handlers.handle_computation,
    Intent.CREATIVE: handlers.handle_creative,
    Intent.UNCERTAIN: handlers.handle_uncertain,
}


class ConverseRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="optional; created if absent")


class ConverseResponse(BaseModel):
    session_id: str
    turn_index: int
    intent: str
    intent_confidence: float
    text: str
    source: str
    audit_chain_root: str
    audit_chain: dict
    confidence: float
    facts_used: list
    latency_ms: float
    metadata: dict


def _get_kv():
    """Lazy access to the substrate-KV (shared with /query/tier5a). Returns None if not loaded."""
    try:
        from backend.routes.query_tier5a import _kv
        return _kv
    except Exception:
        return None


def _get_llm():
    """Lazy access to Qwen client (shared with /query/tier5a)."""
    try:
        from backend.llm.pythia_client import get_client
        return get_client()
    except Exception:
        return None


@router.post("", response_model=ConverseResponse)
async def converse(req: ConverseRequest):
    """Main /converse endpoint - substrate-first cascade routing."""
    session_id = req.session_id or str(uuid.uuid4())
    session = get_or_create_session(session_id)

    # Record user turn
    user_turn = Turn(role="user", text=req.message)
    session.add_turn(user_turn)

    # Classify intent (PP-198 / PP-212 fast tier)
    classification = classify(req.message)
    intent = classification.intent
    handler = INTENT_TO_HANDLER.get(intent, handlers.handle_uncertain)

    kv = _get_kv()
    # Only load LLM for CREATIVE intent (avoid Qwen GPU load when not needed)
    llm_client = _get_llm() if intent == Intent.CREATIVE else None

    try:
        result = handler(
            message=req.message,
            session=session,
            kv=kv,
            llm_client=llm_client,
        )
    except Exception as e:
        logger.exception("/converse handler failed")
        raise HTTPException(status_code=500, detail=f"handler failure: {type(e).__name__}: {e}")

    # Record assistant turn
    assistant_turn = Turn(
        role="assistant",
        text=result["text"],
        intent=intent.value,
        source=result["source"],
        audit_root=result.get("audit_chain_root"),
    )
    session.add_turn(assistant_turn)

    return ConverseResponse(
        session_id=session_id,
        turn_index=len(session.turns) - 1,
        intent=intent.value,
        intent_confidence=classification.confidence,
        text=result["text"],
        source=result["source"],
        audit_chain_root=result.get("audit_chain_root", ""),
        audit_chain=result.get("audit_chain", {}),
        confidence=result.get("confidence", 0.0),
        facts_used=result.get("facts_used", []),
        latency_ms=result.get("latency_ms", 0.0),
        metadata=result.get("metadata", {}),
    )


@router.get("/sessions")
async def list_sessions_endpoint():
    """List active sessions (debug / monitoring)."""
    return {"sessions": list_sessions()}


@router.get("/sessions/{session_id}")
async def get_session_endpoint(session_id: str):
    """Get a session's turn history."""
    from backend.converse.state import get_session
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session.to_dict()
