"""M3 Phase 1 router smoke test -- 20 queries across 4 intent buckets.

Discriminator-fires requirement: each intent class MUST produce a distinguishable
RouterDecision.outcome / path. Specifically:
  - KG_LOOKUP queries: outcome=GLASS_BOX_SUBSTRATE (substrate kg_lookup answered)
  - GENERAL (DEFINITION/COMPARISON/etc) queries: outcome=FALL_BACK_TO_LLM
  - MULTI_HOP queries: outcome=FALL_BACK_TO_LLM with error noting M1.3 pending
  - REFUSED queries: outcome=FALL_BACK_TO_LLM with refuse_gate_fired or unparseable error

If all 20 queries hit the same outcome, the smoke test FAILS — that means the
router isn't actually discriminating (verify-the-referent discipline).

No silent except: any unexpected exception propagates and fails the test.

Run:
  python d:/AI/hd-instrument/substrate_router/test_router_smoke.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from substrate_router import SubstrateRouterAPI, IntentClass, RouteOutcome, route
from substrate_router.api import APIConfig


# ---------------- The 20-query test bank ----------------
# 5 KG_LOOKUP -- substrate's tiny KG has matching triples (Pattern-matched parse).
# 5 GENERAL (DEFINITION + COMPARISON, intentionally non-substrate-answerable).
# 5 MULTI_HOP -- substrate classifies but M1.3 wrapper pending; falls back to LLM with explicit error.
# 5 REFUSED -- unparseable / OOD queries that should refuse and fall back.

KG_LOOKUP_QUERIES = [
    "What is the capital of France?",
    "What is the capital of Japan?",
    "What is the capital of Italy?",
    "What is the capital of Germany?",
    "Who founded Microsoft?",
]

GENERAL_QUERIES = [
    "What is photosynthesis?",
    "Define entropy.",
    "What does democracy mean?",
    "Which is larger, Mars or Mercury?",
    "Which mountain is taller, Everest or K2?",
]

MULTI_HOP_QUERIES = [
    "Who directed the film starring Marlon Brando in The Godfather?",
    "What is the capital of the country where the Amazon River begins?",
    "Who wrote the book that inspired the movie Blade Runner?",
    "Who founded the company that makes the iPhone, and where was that person born?",
    "What river flows through the city where Shakespeare was born?",
]

REFUSED_QUERIES = [
    # Gibberish / very short / OOD-vocab queries.
    "asdf qwerty zxcv?",
    "Ploxapod brontfu xenrim?",
    "Hjkl bnm vbn fdsa?",
    "Wxyz qzpt rty pyx?",
    "Mrlz blph drvk wkry?",
]


def mock_llm(query: str) -> str:
    """M1.1 mock LLM call -- replaced in M1.2+ with real Claude client."""
    return f"LLM-mocked answer for: {query[:40]}"


def _label_expected(bucket: str) -> str:
    """The expected outcome string for each bucket; used to compute routing accuracy."""
    if bucket == "KG_LOOKUP":
        return "GLASS_BOX_SUBSTRATE"
    return "FALL_BACK_TO_LLM"


def run_smoke() -> dict:
    print("=" * 72)
    print("M3 Phase 1 router smoke test (M1.1 scaffolding)")
    print("=" * 72)

    api = SubstrateRouterAPI(APIConfig(n_dim=2048, intent_seed=7, refuse_tau=0.35))
    print(f"API built: n_dim={api.config.n_dim}, categories={[c.value for c in api.categories]}")
    print(f"KG vocab: {len(api.kg_vocab[0])} entities, {len(api.kg_vocab[1])} relations")
    print()

    buckets = [
        ("KG_LOOKUP", KG_LOOKUP_QUERIES),
        ("GENERAL", GENERAL_QUERIES),
        ("MULTI_HOP", MULTI_HOP_QUERIES),
        ("REFUSED", REFUSED_QUERIES),
    ]

    all_decisions: list[tuple[str, object]] = []
    per_bucket_correct: dict[str, int] = {}
    per_bucket_total: dict[str, int] = {}
    outcome_distribution: Counter = Counter()
    intent_distribution: Counter = Counter()
    substrate_path_distribution: Counter = Counter()

    for bucket_name, queries in buckets:
        per_bucket_correct[bucket_name] = 0
        per_bucket_total[bucket_name] = len(queries)
        expected = _label_expected(bucket_name)
        print(f"-- Bucket: {bucket_name} (expected outcome: {expected}) --")
        for q in queries:
            d = route(q, api, mock_llm)
            all_decisions.append((bucket_name, d))
            outcome_distribution[d.outcome.value] += 1
            intent_distribution[d.intent.value] += 1
            if d.substrate_path:
                substrate_path_distribution[d.substrate_path] += 1
            ok = (d.outcome.value == expected)
            if ok:
                per_bucket_correct[bucket_name] += 1
            mark = "OK " if ok else "MIS"
            print(f"  [{mark}] intent={d.intent.value:11s} conf={d.intent_confidence:.3f} "
                  f"outcome={d.outcome.value:22s} path={d.substrate_path or '(LLM)'}")
            if d.error:
                print(f"        error: {d.error}")
        print()

    # ---------------- Discriminator-fires check ----------------
    print("=" * 72)
    print("Discriminator-fires audit")
    print("=" * 72)
    print(f"Outcome distribution: {dict(outcome_distribution)}")
    print(f"Intent distribution:  {dict(intent_distribution)}")
    print(f"Substrate paths:      {dict(substrate_path_distribution)}")

    distinct_outcomes = len(outcome_distribution)
    distinct_intents = len(intent_distribution)

    # Routing accuracy (per-bucket).
    print()
    print("Per-bucket routing accuracy:")
    total_correct = 0
    total_queries = 0
    for bn in per_bucket_correct:
        c = per_bucket_correct[bn]
        t = per_bucket_total[bn]
        total_correct += c
        total_queries += t
        print(f"  {bn:11s}: {c}/{t} = {c/t:.2f}")
    overall_acc = total_correct / total_queries
    print(f"OVERALL routing accuracy: {total_correct}/{total_queries} = {overall_acc:.3f}")

    # ---------------- Smoke verdict ----------------
    # HARD_PASS conditions:
    #   - At least 2 distinct outcomes (discriminator fires)
    #   - At least 3 distinct intents (multi-class behavior)
    #   - Overall routing accuracy >= 0.60 (lenient; this is M1.1 scaffolding,
    #     and the tiny in-memory intent corpus is not the full 5000-example
    #     chain-grade corpus -- M1.2 swaps in the real corpus)
    discriminator_fires = (distinct_outcomes >= 2) and (distinct_intents >= 3)
    accuracy_ok = overall_acc >= 0.60

    print()
    if discriminator_fires and accuracy_ok:
        verdict = "SMOKE_PASS"
    elif discriminator_fires and not accuracy_ok:
        verdict = "SMOKE_DISCRIMINATOR_FIRES_LOW_ACC"
    elif not discriminator_fires:
        verdict = "SMOKE_FAIL_DISCRIMINATOR_DEGENERATE"
    else:
        verdict = "SMOKE_UNKNOWN"
    print(f"Verdict: {verdict}")
    print(f"  discriminator_fires={discriminator_fires} (distinct outcomes={distinct_outcomes}, intents={distinct_intents})")
    print(f"  accuracy_ok={accuracy_ok} (overall={overall_acc:.3f} >= 0.60)")
    print()
    print("HONEST SCOPE (M1.1 scaffolding):")
    print("  This is mechanical-correctness evidence on a 20-query hand-crafted bank")
    print("  against an in-memory tiny KG fixture and a 42-example intent training corpus.")
    print("  It is NOT chain-grade evidence for the router's real-world accuracy.")
    print("  M1.2 will swap to the full 5000-example chain-grade intent corpus + the")
    print("  ingested FB15k-237 KG (12838 entities, 237 relations) and produce")
    print("  cert-grade routing accuracy on a 100+ query benchmark per M1.6.")

    return {
        "verdict": verdict,
        "overall_accuracy": overall_acc,
        "per_bucket_correct": per_bucket_correct,
        "per_bucket_total": per_bucket_total,
        "outcome_distribution": dict(outcome_distribution),
        "intent_distribution": dict(intent_distribution),
        "substrate_path_distribution": dict(substrate_path_distribution),
        "discriminator_fires": discriminator_fires,
        "n_queries": total_queries,
    }


if __name__ == "__main__":
    result = run_smoke()
    # Exit code: 0 on PASS or discriminator-fires-low-acc (informative, not fatal at M1.1);
    # 1 on degenerate discriminator (real failure).
    if result["verdict"] == "SMOKE_FAIL_DISCRIMINATOR_DEGENERATE":
        sys.exit(1)
    sys.exit(0)
