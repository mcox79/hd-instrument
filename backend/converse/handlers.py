"""
Per-intent handlers invoked by the cascade router.

Each handler returns a dict:
  {
    "text": str,                  # response text
    "source": str,                # "substrate-direct" / "substrate+template" / "llm-mediated"
    "audit_chain": dict | None,
    "confidence": float,
    "facts_used": list,
    "latency_ms": float,
    "metadata": dict,
  }

Substrate-direct handlers MUST NOT call an LLM. LLM-mediated handlers should be the last
resort (CREATIVE / synthesis / open-ended).
"""
from __future__ import annotations
import re
import time
from typing import Optional

from substrate.audit import AuditChain
from backend.converse import templates


# ============================================================
# Substrate-direct handlers (PP-187 templated; sub-ms)
# ============================================================

def handle_greeting(message: str, session, **kwargs) -> dict:
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:greeting:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "greeting", "message": message[:80]})
    chain.append("template_render", {"template_category": "greeting"})
    text = templates.render("greeting", seed=hash(session.session_id) % 1000)
    return {
        "text": text,
        "source": "substrate-direct (PP-187 templated; no LLM call)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.95,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187"},
    }


def handle_farewell(message: str, session, **kwargs) -> dict:
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:farewell:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "farewell"})
    chain.append("template_render", {"template_category": "farewell"})
    text = templates.render("farewell", seed=hash(session.session_id) % 1000, turn_count=len(session.turns))
    return {
        "text": text,
        "source": "substrate-direct (PP-187 templated; no LLM call)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.95,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187"},
    }


def handle_ack(message: str, session, **kwargs) -> dict:
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:ack:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "acknowledgment"})
    chain.append("template_render", {"template_category": "acknowledgment"})
    return {
        "text": templates.render("acknowledgment", seed=hash(session.session_id) % 1000),
        "source": "substrate-direct (PP-187 templated; no LLM call)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.95,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187"},
    }


def handle_clarification(message: str, session, **kwargs) -> dict:
    t0 = time.perf_counter()
    last_resp = session.last_assistant()
    last_text = last_resp.text[:120] if last_resp else "(no prior response)"
    chain = AuditChain(chain_id=f"converse:clarif:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "clarification"})
    chain.append("template_render", {"template_category": "clarification", "had_prior": last_resp is not None})
    return {
        "text": templates.render("clarification", seed=0, last_response=last_text),
        "source": "substrate-direct (PP-187 templated; PP-195 multi-turn state)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.85,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187+PP-195"},
    }


# ============================================================
# Substrate-retrieval handlers (PP-107 confidence-gated)
# ============================================================

def handle_factual(message: str, session, kv=None, **kwargs) -> dict:
    """Substrate retrieve + template; abstain if confidence below PP-107 threshold."""
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:factual:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "factual", "query": message[:80]})

    if kv is None or len(kv) == 0:
        chain.append("kv_unavailable", {})
        return {
            "text": templates.render("abstention", seed=0),
            "source": "substrate-direct (abstention; no KB loaded)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.0,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-107 abstention"},
        }

    retrieved = kv.retrieve(message, top_k=5)
    chain.append("retrieve", {"top_k": 5, "kb_size": len(kv),
                              "scores": [round(s, 4) for _, s in retrieved]})

    if not retrieved:
        return {
            "text": templates.render("abstention", seed=1),
            "source": "substrate-direct (no matches)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.0,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-107"},
        }

    top_fact, top_score = retrieved[0]

    # PP-107 confidence gate
    HIGH_CONF = 0.40   # bge-large + 169-fact KB; tuned to match cycle 187 abstention regime
    LOW_CONF = 0.15

    if top_score >= HIGH_CONF:
        chain.append("confidence_gate", {"threshold": HIGH_CONF, "passed": True, "top_score": top_score})
        chain.append("template_render", {"template_category": "factual_single"})
        text = templates.render("factual_single", seed=0, fact=top_fact)
        return {
            "text": text,
            "source": "substrate+template (PP-187 + PP-107 high confidence)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": top_score,
            "facts_used": [{"fact": f, "score": s} for f, s in retrieved[:3]],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-187+PP-107"},
        }
    if top_score >= LOW_CONF:
        # Medium-confidence: return the top fact but flag confidence
        chain.append("confidence_gate", {"threshold": HIGH_CONF, "passed": False, "top_score": top_score})
        chain.append("template_render", {"template_category": "factual_multi"})
        fact_list = "\n".join(f"- {f}" for f, _ in retrieved[:3])
        text = templates.render("factual_multi", seed=0, n=len(retrieved[:3]), fact_list=fact_list)
        return {
            "text": text,
            "source": "substrate+template (PP-187 + PP-107 medium confidence)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": top_score,
            "facts_used": [{"fact": f, "score": s} for f, s in retrieved[:3]],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-187+PP-107"},
        }

    # Low confidence: honest abstention
    chain.append("abstention", {"reason": "below_threshold", "top_score": top_score, "threshold": LOW_CONF})
    return {
        "text": templates.render("abstention", seed=0),
        "source": "substrate-direct (PP-107 abstention)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": top_score,
        "facts_used": [{"fact": f, "score": s} for f, s in retrieved[:3]],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-107"},
    }


# ============================================================
# Compositional algebra handlers (substrate AND/NOT/COUNT/counterfactual)
# ============================================================

def handle_compositional(message: str, session, kv=None, **kwargs) -> dict:
    """Detect AND / NOT / COUNT intent and dispatch to substrate algebra."""
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:comp:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "compositional", "query": message[:80]})

    msg = message.lower()
    facts = kv.facts if kv else []

    # COUNT pattern
    count_match = re.search(r"(?:how\s+many|count|number\s+of)\s+(?:facts?\s+(?:mention(?:ing)?|about|containing|with))?\s*['\"]?([^'\"?.!]+?)['\"]?\s*[?.!]?$", msg)
    if count_match:
        term = count_match.group(1).strip()
        n = sum(1 for f in facts if term in f.lower())
        chain.append("op", {"op": "COUNT", "term": term, "result": n, "kb_size": len(facts)})
        return {
            "text": templates.render("compositional_count", seed=0, term=term, count=n, kb_size=len(facts)),
            "source": "substrate-direct (set cardinality; no LLM)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 1.0,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.count"},
        }

    # NOT pattern: "X but not Y" / "X without Y" / "X excluding Y"
    not_match = re.search(r"(?:facts?\s+(?:about|mentioning|containing)\s+)?['\"]?([^'\"]+?)['\"]?\s+(?:but\s+not|without|excluding|except)\s+['\"]?([^'\"?.!]+?)['\"]?\s*[?.!]?$", msg)
    if not_match:
        inc = not_match.group(1).strip()
        exc = not_match.group(2).strip()
        hits = [f for f in facts if inc in f.lower() and exc not in f.lower()][:5]
        chain.append("op", {"op": "NOT", "include": inc, "exclude": exc, "matches": len(hits)})
        fact_list = "\n".join(f"- {f}" for f in hits) or "(no matches)"
        return {
            "text": templates.render("compositional_not", seed=0,
                                     included=inc, excluded=exc, count=len(hits), fact_list=fact_list),
            "source": "substrate-direct (set difference; Datalog-neg)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 1.0,
            "facts_used": [{"fact": h, "score": None} for h in hits],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.set_diff"},
        }

    # AND pattern: "X and Y" / "both X and Y"
    and_match = re.search(r"(?:both\s+)?['\"]?([^'\"]+?)['\"]?\s+and\s+['\"]?([^'\"?.!]+?)['\"]?\s*[?.!]?$", msg)
    if and_match:
        a = and_match.group(1).strip()
        b = and_match.group(2).strip()
        hits = [f for f in facts if a in f.lower() and b in f.lower()][:5]
        chain.append("op", {"op": "AND", "terms": [a, b], "matches": len(hits)})
        fact_list = "\n".join(f"- {f}" for f in hits) or "(no matches)"
        return {
            "text": templates.render("compositional_and", seed=0,
                                     term_a=a, term_b=b, count=len(hits), fact_list=fact_list),
            "source": "substrate-direct (set intersection; categorical)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 1.0,
            "facts_used": [{"fact": h, "score": None} for h in hits],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.set_inter"},
        }

    # Fall back to factual retrieval if pattern not recognized
    return handle_factual(message, session, kv=kv, **kwargs)


def handle_computation(message: str, session, **kwargs) -> dict:
    """Pure-Python eval for simple arithmetic. Production: route to SymPy."""
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:compute:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "computation"})

    # Extract arithmetic expression
    expr_match = re.search(r"([-+]?\d+(?:\.\d+)?\s*(?:[+\-*/]\s*[-+]?\d+(?:\.\d+)?)+)", message)
    if not expr_match:
        chain.append("parse_failure", {})
        return {
            "text": "I can only handle simple arithmetic expressions right now (e.g. '2 + 2'). For more complex math, route to SymPy (not yet wired).",
            "source": "substrate-direct (computation; parse failed)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.5,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.compute"},
        }

    expr = expr_match.group(1)
    try:
        # Safe eval: only allow digits + operators
        if not re.match(r"^[\d\s+\-*/().]+$", expr):
            raise ValueError("unsafe expression")
        result = eval(expr, {"__builtins__": {}}, {})
        chain.append("eval", {"expression": expr, "result": str(result)})
        return {
            "text": templates.render("computation", seed=0, expression=expr.strip(), result=result),
            "source": "substrate-direct (safe arithmetic eval)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 1.0,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.compute"},
        }
    except Exception as e:
        chain.append("eval_error", {"expression": expr, "error": str(e)})
        return {
            "text": f"Could not compute '{expr}': {e}. Try a simpler arithmetic expression.",
            "source": "substrate-direct (computation; eval failed)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.3,
            "facts_used": [],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "substrate.compute"},
        }


def handle_counterfactual(message: str, session, **kwargs) -> dict:
    """Counterfactual conversations require a structured DAG; for free-form questions,
    we explain how to use /query/tier5a/counterfactual."""
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:cf:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "counterfactual", "query": message[:80]})
    chain.append("note", {"reason": "free-form counterfactual; needs DAG specification"})
    return {
        "text": (
            "Counterfactual questions need a structured DAG to compute via Pearl-style do(). "
            "Try the algebraic playground at /playground - the 'Counterfactual do()' card "
            "lets you define base facts + derived nodes + intervention and runs it with a Merkle audit chain. "
            "For free-form counterfactuals over training facts, the LLM is invoked - say 'route to LLM' to do so."
        ),
        "source": "substrate-direct (counterfactual routing hint; no LLM)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.7,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187 routing"},
    }


# ============================================================
# LLM-mediated handler (CREATIVE / open-ended)
# ============================================================

def handle_creative(message: str, session, kv=None, llm_client=None, **kwargs) -> dict:
    """Last resort: call LLM for genuinely creative output. Substrate provides context."""
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:creative:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "creative", "query": message[:80]})

    # Substrate retrieves any related facts for grounding
    retrieved = []
    if kv is not None and len(kv) > 0:
        retrieved = kv.retrieve(message, top_k=3)
        chain.append("substrate_context", {"facts": [round(s, 3) for _, s in retrieved]})

    if llm_client is None:
        chain.append("llm_unavailable", {})
        return {
            "text": "Creative responses require LLM (Qwen-2.5-1.5B or gpt-4o-mini); none available right now. " +
                    templates.render("creative_handoff", seed=0),
            "source": "substrate-direct (LLM unavailable; handoff text only)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.5,
            "facts_used": [{"fact": f, "score": s} for f, s in retrieved],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-123 routing"},
        }

    facts_block = "\n".join(f"- {f}" for f, _ in retrieved) if retrieved else "(no substrate context)"
    system = (
        "You are a creative assistant. Use the substrate-provided facts below as grounding when relevant, "
        "but feel free to compose freely (poems, stories, opinions). Stay brief (under 100 words)."
    )
    user_prompt = f"Substrate context:\n{facts_block}\n\nUser request: {message}"
    try:
        resp = llm_client.generate(user_prompt, max_new_tokens=120, temperature=0.7, system=system)
        chain.append("llm_generate", {
            "model": resp.model,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "latency_ms": round(resp.latency_ms, 1),
        })
        return {
            "text": resp.text,
            "source": "llm-mediated (substrate context + Qwen generation)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.7,
            "facts_used": [{"fact": f, "score": s} for f, s in retrieved],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-123 LLM handoff", "llm_latency_ms": resp.latency_ms},
        }
    except Exception as e:
        chain.append("llm_error", {"error": str(e)})
        return {
            "text": "LLM call failed; falling back to substrate-direct handoff. " +
                    templates.render("creative_handoff", seed=0),
            "source": "substrate-direct (LLM error)",
            "audit_chain": chain.to_dict(),
            "audit_chain_root": chain.root,
            "confidence": 0.4,
            "facts_used": [{"fact": f, "score": s} for f, s in retrieved],
            "latency_ms": (time.perf_counter() - t0) * 1000,
            "metadata": {"primitive": "PP-123 error fallback", "error": str(e)},
        }


def handle_uncertain(message: str, session, **kwargs) -> dict:
    t0 = time.perf_counter()
    chain = AuditChain(chain_id=f"converse:uncert:{int(t0 * 1e6)}")
    chain.append("intent", {"intent": "uncertain"})
    return {
        "text": templates.render("uncertain", seed=hash(message) % 1000),
        "source": "substrate-direct (uncertain intent)",
        "audit_chain": chain.to_dict(),
        "audit_chain_root": chain.root,
        "confidence": 0.2,
        "facts_used": [],
        "latency_ms": (time.perf_counter() - t0) * 1000,
        "metadata": {"primitive": "PP-187 uncertain"},
    }


# ============================================================
# Self-test
# ============================================================

def _self_test():
    from backend.converse.state import Session, Turn
    s = Session(session_id="test")

    # Substrate-direct categories (no KV needed)
    for fn, name in [
        (handle_greeting, "greeting"),
        (handle_farewell, "farewell"),
        (handle_ack, "ack"),
        (handle_clarification, "clarification"),
        (handle_uncertain, "uncertain"),
        (handle_counterfactual, "counterfactual"),
    ]:
        result = fn("test message", s)
        assert result["text"], f"{name} empty text"
        assert "substrate-direct" in result["source"], f"{name} not labeled substrate-direct"
        assert result["audit_chain_root"], f"{name} no audit root"
        assert result["latency_ms"] < 50, f"{name} latency {result['latency_ms']}ms exceeds 50ms gate"

    # Computation
    result = handle_computation("what is 2 + 2?", s)
    assert "4" in result["text"], "compute 2+2 failed"
    assert result["latency_ms"] < 50

    # Factual without KV -> abstention
    result = handle_factual("who founded Anthropic?", s, kv=None)
    assert "do not" in result["text"].lower() or "abstention" in result["text"].lower(), "factual w/o KV should abstain"

    print(f"[converse.handlers] self-test PASS (substrate-direct latencies all < 50ms)")


if __name__ == "__main__":
    _self_test()
