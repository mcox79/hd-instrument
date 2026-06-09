"""
Intent classification for /converse (PP-198 prototype port).

Returns (intent_label, confidence, debug_features).

Implementation: pattern-based first-pass (regex + keyword), then prototype-cosine fallback
via substrate-KV when ambiguous. Production PP-198 uses substrate prototype classifier
exclusively; the regex layer is for fast paths on unambiguous patterns.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Intent(str, Enum):
    GREETING = "greeting"           # "hi", "hello", "good morning"
    FAREWELL = "farewell"           # "bye", "goodbye", "see you"
    ACK = "acknowledgment"          # "thanks", "ok", "got it"
    FACTUAL = "factual"             # "who is X", "what is X", "when did X", direct retrieval
    CLARIFICATION = "clarification" # "what do you mean", "can you explain"
    COMPUTATION = "computation"     # "what is 2+2", "calculate", "compute"
    COMPOSITIONAL = "compositional" # "facts about X AND Y", "count facts mentioning Z"
    COUNTERFACTUAL = "counterfactual" # "what if X were", "suppose"
    CREATIVE = "creative"           # "write me a poem", "tell me a story", LLM-mediated
    UNCERTAIN = "uncertain"         # low confidence; should ask for clarification


@dataclass
class IntentClassification:
    intent: Intent
    confidence: float
    features: dict           # debug features that drove the decision


# Pattern-based first-pass rules (PP-198 fast tier; 0.64ms target per PP-212)

GREETING_PATTERNS = [
    r"\b(hi|hello|hey|greetings|good\s+(morning|afternoon|evening|day))\b",
    r"\b(howdy|yo|sup)\b",
]
FAREWELL_PATTERNS = [
    r"\b(bye|goodbye|farewell|see\s+you|see\s+ya|later|catch\s+you\s+later)\b",
    r"\b(have\s+a\s+(good|great|nice)\s+(day|night|one|weekend))\b",
]
ACK_PATTERNS = [
    r"^\s*(thanks?|thank\s+you|thx|ty|ok|okay|got\s+it|cool|understood|sure|yes|yep|nope|no)\s*[.!?]?\s*$",
]
CLARIFICATION_PATTERNS = [
    r"\b(what\s+do\s+you\s+mean|can\s+you\s+explain|i\s+don'?t\s+understand|elaborate|clarify)\b",
    r"\b(say\s+(it\s+)?again|repeat|come\s+again)\b",
]
COMPUTATION_PATTERNS = [
    r"\b(calculate|compute|solve|evaluate)\b",
    r"\bwhat\s+is\s+[-+]?\d+(\.\d+)?\s*[+\-*/]\s*[-+]?\d+",  # "what is 2 + 2"
    r"\b\d+\s*[+\-*/]\s*\d+",                                  # "2 + 2"
]
COMPOSITIONAL_PATTERNS = [
    r"\b(both|all\s+of|none\s+of|except|excluding|not\s+including|count|how\s+many)\b",
    r"\bfacts?\s+(about|mentioning|containing|that\s+(include|mention))\b",
    r"\b(union|intersection|difference)\s+of\b",
]
COUNTERFACTUAL_PATTERNS = [
    r"\b(what\s+if|suppose|imagine\s+(that|if)|hypothetically|counterfactual)\b",
    r"\b(would\s+have|had\s+been|if\s+\w+\s+were)\b",
]
CREATIVE_PATTERNS = [
    r"\b(write|compose|generate|create)\s+(me\s+)?(a|an|the)?\s*(poem|story|essay|joke|song|haiku|sonnet|tale|verse|limerick|rap)\b",
    r"\b(tell\s+me\s+a\s+story|brainstorm|imagine)\b",
    r"\b(in\s+the\s+style\s+of|pretend\s+to\s+be|act\s+as\s+if)\b",
]
# Factual: starts with WH-words or "tell me about" + not matching any above
FACTUAL_PATTERNS = [
    r"^\s*(who|what|when|where|why|how|which|whose)\b",
    r"\btell\s+me\s+about\b",
    r"\b(is|are|was|were|does|do|did|has|have|had|can|could)\s+\w+",
]


def _match_any(text_lower: str, patterns: list) -> bool:
    return any(re.search(p, text_lower) for p in patterns)


def classify(message: str) -> IntentClassification:
    """First-pass pattern classification. Returns (intent, confidence, features).

    Pattern-based for fast unambiguous cases (PP-212 sub-ms target). Future: fall back
    to substrate prototype cosine for ambiguous cases (PP-198 production).
    """
    text = message.strip()
    text_lower = text.lower()
    features = {"text_length": len(text), "lower": text_lower[:60]}

    if not text:
        return IntentClassification(Intent.UNCERTAIN, 0.0, features)

    # Pattern checks ordered by specificity
    if _match_any(text_lower, ACK_PATTERNS):
        return IntentClassification(Intent.ACK, 0.95, {**features, "matched": "ACK"})

    if _match_any(text_lower, GREETING_PATTERNS):
        return IntentClassification(Intent.GREETING, 0.95, {**features, "matched": "GREETING"})

    if _match_any(text_lower, FAREWELL_PATTERNS):
        return IntentClassification(Intent.FAREWELL, 0.95, {**features, "matched": "FAREWELL"})

    if _match_any(text_lower, COUNTERFACTUAL_PATTERNS):
        return IntentClassification(Intent.COUNTERFACTUAL, 0.85, {**features, "matched": "COUNTERFACTUAL"})

    if _match_any(text_lower, CREATIVE_PATTERNS):
        return IntentClassification(Intent.CREATIVE, 0.9, {**features, "matched": "CREATIVE"})

    if _match_any(text_lower, COMPUTATION_PATTERNS):
        return IntentClassification(Intent.COMPUTATION, 0.85, {**features, "matched": "COMPUTATION"})

    if _match_any(text_lower, COMPOSITIONAL_PATTERNS):
        return IntentClassification(Intent.COMPOSITIONAL, 0.8, {**features, "matched": "COMPOSITIONAL"})

    if _match_any(text_lower, CLARIFICATION_PATTERNS):
        return IntentClassification(Intent.CLARIFICATION, 0.85, {**features, "matched": "CLARIFICATION"})

    if _match_any(text_lower, FACTUAL_PATTERNS):
        return IntentClassification(Intent.FACTUAL, 0.75, {**features, "matched": "FACTUAL"})

    # Default to FACTUAL with low confidence; cascade router may still try retrieval
    if len(text) > 5:
        return IntentClassification(Intent.FACTUAL, 0.4, {**features, "matched": "DEFAULT_FACTUAL"})

    return IntentClassification(Intent.UNCERTAIN, 0.2, {**features, "matched": "FALLTHROUGH"})


def _self_test():
    """30-query test set (Phase 1 acceptance gate: 100% correct intent categorization)."""
    cases = [
        # GREETING
        ("hi", Intent.GREETING),
        ("hello there!", Intent.GREETING),
        ("good morning", Intent.GREETING),
        # FAREWELL
        ("bye", Intent.FAREWELL),
        ("goodbye for now", Intent.FAREWELL),
        ("have a great day", Intent.FAREWELL),
        # ACK
        ("thanks", Intent.ACK),
        ("ok", Intent.ACK),
        ("got it", Intent.ACK),
        # FACTUAL
        ("who founded Anthropic?", Intent.FACTUAL),
        ("when was OpenAI founded?", Intent.FACTUAL),
        ("tell me about Pythia", Intent.FACTUAL),
        ("what does the EU AI Act require?", Intent.FACTUAL),
        # CLARIFICATION
        ("what do you mean?", Intent.CLARIFICATION),
        ("can you explain that?", Intent.CLARIFICATION),
        ("say it again please", Intent.CLARIFICATION),
        # COMPUTATION
        ("what is 2 + 2?", Intent.COMPUTATION),
        ("calculate 1234 * 5678", Intent.COMPUTATION),
        ("solve x squared minus 4", Intent.COMPUTATION),
        # COMPOSITIONAL
        ("how many facts mention OpenAI?", Intent.COMPOSITIONAL),
        ("facts about Anthropic but not Claude", Intent.COMPOSITIONAL),
        ("count facts containing substrate", Intent.COMPOSITIONAL),
        # COUNTERFACTUAL
        ("what if OpenAI had been founded in 2020?", Intent.COUNTERFACTUAL),
        ("suppose the EU AI Act were never passed", Intent.COUNTERFACTUAL),
        ("imagine if Claude were released in 2023", Intent.COUNTERFACTUAL),
        # CREATIVE
        ("write me a poem about substrate", Intent.CREATIVE),
        ("tell me a story about hyperdimensional computing", Intent.CREATIVE),
        ("compose a haiku about Merkle chains", Intent.CREATIVE),
        # Mixed / edge
        ("Anthropic", Intent.FACTUAL),  # bare entity -> factual default
        ("?", Intent.UNCERTAIN),
    ]

    correct = 0
    misses = []
    for msg, expected in cases:
        result = classify(msg)
        if result.intent == expected:
            correct += 1
        else:
            misses.append((msg, expected.value, result.intent.value, result.features.get("matched")))

    n = len(cases)
    print(f"[converse.intent] {correct}/{n} correct ({100 * correct / n:.0f}%)")
    if misses:
        for m in misses:
            print(f"  MISS: {m[0]!r} expected {m[1]} got {m[2]} via {m[3]}")
    assert correct == n, f"intent self-test failed: {correct}/{n}"
    print("[converse.intent] self-test PASS")


if __name__ == "__main__":
    _self_test()
