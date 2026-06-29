"""router.route(query) -- M1.1 LLM-router shell over the SubstrateRouterAPI.

The Phase 1 router. Given a USER query:
  1. classify_intent via substrate (chain-grade, ~0.5ms p95)
  2. if intent in SUBSTRATE_ANSWERABLE AND confidence >= threshold:
       -> try the matching substrate primitive (kg_lookup for KG_LOOKUP, etc.)
       -> if substrate refuses or errors: fall back to LLM
       -> else return substrate output (GLASS_BOX_SUBSTRATE outcome)
  3. else: fall back to LLM (FALL_BACK_TO_LLM outcome)

The LLM call is dependency-injected as `llm_call: Callable[[str], str]`. For
M1.1 smoke we pass a mock lambda; M1.2+ wires in the real Claude call. This
keeps the routing logic testable without LLM-API-key dependency and aligns
with the "router LLM choice is open" open question in the design sketch.

No silent except: ValueError from substrate primitives is CAUGHT (the router's
contract is to fall back to LLM on substrate failure) but logged on the
RouterDecision.error field so the caller can audit. Any other exception
propagates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from .api import IntentClass, SubstrateRouterAPI, SUBSTRATE_ANSWERABLE


# Default confidence threshold; configurable per-call.
# 0.8 is the design-sketch default; lower than that and the LLM should arbitrate.
DEFAULT_CONFIDENCE_THRESHOLD = 0.8


class RouteOutcome(str, Enum):
    """The route() result discriminator: where the answer came from."""

    GLASS_BOX_SUBSTRATE = "GLASS_BOX_SUBSTRATE"   # substrate answered (with confidence + trace)
    FALL_BACK_TO_LLM = "FALL_BACK_TO_LLM"         # LLM produced the answer
    REFUSED = "REFUSED"                            # both routes refused (e.g. unparseable + LLM gave nothing)


@dataclass
class RouterDecision:
    """Returned by router.route(); the audit-trail of a single routing call."""

    query: str
    intent: IntentClass
    intent_confidence: float
    outcome: RouteOutcome
    answer: Optional[str]
    answer_confidence: float
    # Glass-box trace (only populated when outcome == GLASS_BOX_SUBSTRATE)
    substrate_path: Optional[str] = None  # e.g. "kg_lookup(France, capital)"
    # Errors collected (caught ValueError from substrate primitives).
    error: Optional[str] = None
    # The confidence threshold that gated routing.
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD


def route(
    query: str,
    api: SubstrateRouterAPI,
    llm_call: Callable[[str], str],
    *,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> RouterDecision:
    """Route a query to substrate primitive OR fall back to LLM.

    Args:
        query: USER's question.
        api: SubstrateRouterAPI instance (wraps substrate primitives).
        llm_call: function(query: str) -> str; the LLM stub or real client.
        threshold: substrate confidence threshold for delegation (default 0.8).

    Returns:
        RouterDecision capturing the full routing trace.

    Discriminator-fires guarantee: different intent classes follow distinguishable
    code paths and produce distinguishable outcomes (verifiable in the smoke test).
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("route: query must be non-empty string")

    intent, intent_conf = api.classify_intent(query)

    # Branch 1: intent confidence below threshold -> route to LLM.
    if intent_conf < threshold:
        answer = llm_call(query)
        return RouterDecision(
            query=query,
            intent=intent,
            intent_confidence=intent_conf,
            outcome=RouteOutcome.FALL_BACK_TO_LLM,
            answer=answer,
            answer_confidence=0.0,  # LLM doesn't expose calibrated confidence in M1.1
            error=f"intent_confidence_{intent_conf:.3f}_below_threshold_{threshold:.2f}",
            threshold=threshold,
        )

    # Branch 2: intent not in substrate's answerable set -> LLM.
    if intent not in SUBSTRATE_ANSWERABLE:
        answer = llm_call(query)
        return RouterDecision(
            query=query,
            intent=intent,
            intent_confidence=intent_conf,
            outcome=RouteOutcome.FALL_BACK_TO_LLM,
            answer=answer,
            answer_confidence=0.0,
            error=f"intent_{intent.value}_not_substrate_answerable",
            threshold=threshold,
        )

    # Branch 3: refuse-gate fires -> LLM.
    try:
        refused = api.is_refused(query, intent)
    except ValueError as e:
        # If refuse-gate itself can't run, treat as refuse.
        refused = True
        refused_err = str(e)
    else:
        refused_err = None

    if refused:
        answer = llm_call(query)
        return RouterDecision(
            query=query,
            intent=intent,
            intent_confidence=intent_conf,
            outcome=RouteOutcome.FALL_BACK_TO_LLM,
            answer=answer,
            answer_confidence=0.0,
            error=refused_err or "refuse_gate_fired",
            threshold=threshold,
        )

    # Branch 4: route to substrate primitive.
    if intent == IntentClass.KG_LOOKUP:
        parse = api._try_parse_kg_query(query)
        if parse is None:
            # Parseable check happened in classify_intent's KG_LOOKUP reassignment,
            # so we should have a parse; defensive fall-back if not.
            answer = llm_call(query)
            return RouterDecision(
                query=query, intent=intent, intent_confidence=intent_conf,
                outcome=RouteOutcome.FALL_BACK_TO_LLM, answer=answer,
                answer_confidence=0.0,
                error="kg_query_unparseable_post_intent_classify",
                threshold=threshold,
            )
        entity, relation = parse
        try:
            ans, conf = api.kg_lookup(entity, relation)
        except ValueError as e:
            answer = llm_call(query)
            return RouterDecision(
                query=query, intent=intent, intent_confidence=intent_conf,
                outcome=RouteOutcome.FALL_BACK_TO_LLM, answer=answer,
                answer_confidence=0.0,
                error=f"kg_lookup_error:{e}",
                threshold=threshold,
            )
        if conf < threshold:
            answer = llm_call(query)
            return RouterDecision(
                query=query, intent=intent, intent_confidence=intent_conf,
                outcome=RouteOutcome.FALL_BACK_TO_LLM, answer=answer,
                answer_confidence=conf,
                error=f"kg_confidence_{conf:.3f}_below_threshold_{threshold:.2f}",
                threshold=threshold,
            )
        return RouterDecision(
            query=query, intent=intent, intent_confidence=intent_conf,
            outcome=RouteOutcome.GLASS_BOX_SUBSTRATE,
            answer=ans, answer_confidence=conf,
            substrate_path=f"kg_lookup({entity},{relation})",
            threshold=threshold,
        )

    # Branch 5: MULTI_HOP / CHAIN / LOOKUP-without-KG-parse.
    # M1.1 scope: these intents are answerable in principle but the M1.1
    # SubstrateRouterAPI doesn't yet wrap multi_hop primitive (M1.3 milestone).
    # For now we fall back to LLM and flag the gap.
    answer = llm_call(query)
    return RouterDecision(
        query=query, intent=intent, intent_confidence=intent_conf,
        outcome=RouteOutcome.FALL_BACK_TO_LLM,
        answer=answer, answer_confidence=0.0,
        error=f"intent_{intent.value}_substrate_wrapper_pending_M1.3",
        threshold=threshold,
    )
