"""substrate_intent_classifier_v2_production_scale_100plus_intents -- EXT-3.

EXTENSION TARGET (per Research drill 2026-06-25 EXT-3): the a1 substrate
intent classifier is chain-grade at 50 intents (acc=0.754; maj_mult=4.62;
rand_mult=5.19; p95=0.54ms; n_llm=0). Production intent classification often
needs 100+ intents (customer support, multi-domain assistants).

THIS CELL sweeps n_intents in {50 (rail), 100, 200, 500, 1000} at the SAME
substrate primitive (Hebbian-bound prototype-bundle classifier) + N=8192,
100 test queries per intent (held-out).

The labeled set is synthesized procedurally per-seed so each n_intents is a
SUPER-SET of the previous (50 -> 100 keeps the original 50 + adds 50 more
intents). This isolates the n_intents-scaling effect from corpus-composition
confounds.

ARMS (per n_intents):
  ARM_SUBSTRATE_INTENT       Hebbian-bound prototype-bundle classifier
  ARM_RANDOM_BASELINE        uniform random over n_intents
  ARM_MAJORITY_BASELINE      always predict most-frequent training intent

PRE-REG BANDS (LOCKED via assertion):

  HARD_PASS_PRODUCTION_INTENT_SCALE:
    SUBSTRATE acc >= 0.65 at n_intents = 500
    AND p95 latency <= 5 ms at n_intents=500
    AND cv <= 0.07 across seeds at n_intents=500
    AND n_llm_calls == 0
    (substrate scales to 500-intent classification at production latency)

  CHAIN_GRADE_AT_CLIFF_X:
    SUBSTRATE acc >= 0.65 at SOME n_intents in {100, 200, 500}
    but cliffs at higher n_intents
    (substrate has a measurable cliff X; chain-grade up to that X)

  HARD_FAIL_CLIFF_AT_100:
    SUBSTRATE acc < 0.55 at n_intents=100
    (doesn't extend beyond the 50-intent rail; mechanism is at envelope)

  SANITY_RAIL_AT_50_INTENTS:
    SUBSTRATE acc in [0.65, 0.85] at n_intents=50
    (reproduces a1 cell's chain-grade rail acc=0.754 +/- 0.10)

CONFIG:
  N=8192, 3 seeds [11, 13, 19], 100 test queries per intent (held-out)
  Substrate-only (zero LLM forward calls); char-trigram encoder

Author: exp_dev 2026-06-25 (EXT-3).
ASCII-only; per-seed checkpoint; substrate-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "substrate_intent_classifier_v2_production_scale_100plus_intents"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# Pre-reg HARD bands (LOCKED)
HP_PROD_SCALE_ACC_AT_500 = 0.65
HP_PROD_SCALE_P95_MS = 5.0
HP_CV_MAX = 0.07
HF_CLIFF_AT_100_ACC = 0.55
SANITY_RAIL_ACC_50_LO = 0.65
SANITY_RAIL_ACC_50_HI = 0.85
CHAIN_GRADE_ACC = 0.65

# Lock assertions
assert 0 < HP_PROD_SCALE_ACC_AT_500 <= 1.0
assert 0 < HF_CLIFF_AT_100_ACC < HP_PROD_SCALE_ACC_AT_500
assert SANITY_RAIL_ACC_50_LO < SANITY_RAIL_ACC_50_HI

# Config
if RUN_MODE == "smoke":
    N_DIM = 2048
    N_INTENTS_SWEEP = [50, 100]
    N_TRAIN_PER_INTENT = 20
    N_TEST_PER_INTENT = 25
    SEEDS = [11]
else:
    N_DIM = 8192
    N_INTENTS_SWEEP = [50, 100, 200, 500, 1000]
    N_TRAIN_PER_INTENT = 20
    N_TEST_PER_INTENT = 100
    SEEDS = [11, 13, 19]

CONFIG_VERSION = (
    "substrateIntentClassifierV2ProductionScale: N_DIM=%d n_intents_sweep=%s "
    "N_TRAIN_PER_INTENT=%d N_TEST_PER_INTENT=%d seeds=%s mode=%s; bands "
    "HP_acc_500>=%.2f HP_p95_ms<=%.1f cv<=%.2f HF_cliff_100<%.2f "
    "sanity_50=[%.2f,%.2f]"
) % (
    N_DIM, N_INTENTS_SWEEP, N_TRAIN_PER_INTENT, N_TEST_PER_INTENT,
    SEEDS, RUN_MODE,
    HP_PROD_SCALE_ACC_AT_500, HP_PROD_SCALE_P95_MS, HP_CV_MAX,
    HF_CLIFF_AT_100_ACC, SANITY_RAIL_ACC_50_LO, SANITY_RAIL_ACC_50_HI,
)


# =============================================================================
# Synthetic intent corpus (substrate-only; procedurally generated per seed)
# =============================================================================
#
# Each intent is a unique action-object phrase, generated procedurally from a
# fixed pool of action verbs and object nouns. Phrases at training time are
# templated paraphrases of the intent prototype; test queries are HELD-OUT
# paraphrases that share the action-object semantics but have different
# surface form. Char-trigram encoding picks up the action-object signal.

_ACTIONS = [
    "find", "show", "list", "open", "close", "create", "delete", "update",
    "search", "fetch", "send", "receive", "schedule", "cancel", "book",
    "reserve", "buy", "sell", "rent", "pay", "transfer", "deposit",
    "withdraw", "report", "submit", "approve", "reject", "edit", "view",
    "share", "copy", "move", "rename", "translate", "summarize", "explain",
    "compare", "filter", "sort", "rank",
]

_OBJECTS = [
    "email", "file", "folder", "document", "report", "invoice", "receipt",
    "order", "ticket", "appointment", "meeting", "flight", "hotel", "room",
    "car", "ride", "package", "shipment", "tracking", "account", "balance",
    "transaction", "payment", "bill", "subscription", "plan", "policy",
    "claim", "case", "issue", "ticket", "task", "project", "team", "user",
    "profile", "message", "chat", "thread", "notification", "alert",
    "calendar", "event", "task", "note", "list", "contact", "phone",
    "address", "location",
]

_TRAIN_TEMPLATES = [
    "please {action} the {obj}",
    "i need to {action} my {obj}",
    "can you {action} the {obj}",
    "{action} the {obj} now",
    "help me {action} a {obj}",
    "how do i {action} a {obj}",
    "let me {action} the {obj}",
    "i want to {action} my {obj}",
]

_TEST_TEMPLATES = [
    "i'd like to {action} a {obj}",  # held-out
    "could you {action} this {obj} for me",
    "is it possible to {action} my {obj}",
    "i need help to {action} the {obj}",
    "what's the way to {action} a {obj}",
]


def make_intents(n_intents: int, seed: int) -> List[Tuple[str, str]]:
    """Build a list of (action, object) intent pairs, deterministic per seed.

    Pairs are unique. Ordering is deterministic per seed.
    """
    rng = np.random.default_rng(int(seed) * 7901 + 11)
    pairs = []
    for a in _ACTIONS:
        for o in _OBJECTS:
            pairs.append((a, o))
    # Shuffle deterministically
    idxs = np.arange(len(pairs))
    rng.shuffle(idxs)
    pairs_shuffled = [pairs[int(i)] for i in idxs]
    if n_intents > len(pairs_shuffled):
        raise RuntimeError("n_intents %d > available unique pairs %d (need bigger pool)"
                           % (n_intents, len(pairs_shuffled)))
    return pairs_shuffled[:n_intents]


def synth_train(intents: List[Tuple[str, str]], n_per_intent: int,
                seed: int) -> List[Tuple[str, int]]:
    rng = np.random.default_rng(int(seed) * 3001 + 13)
    out = []
    for intent_id, (a, o) in enumerate(intents):
        for _ in range(n_per_intent):
            t = _TRAIN_TEMPLATES[int(rng.integers(0, len(_TRAIN_TEMPLATES)))]
            out.append((t.format(action=a, obj=o), intent_id))
    # Deterministic shuffle
    idxs = np.arange(len(out))
    rng.shuffle(idxs)
    return [out[int(i)] for i in idxs]


def synth_test(intents: List[Tuple[str, str]], n_per_intent: int,
               seed: int) -> List[Tuple[str, int]]:
    rng = np.random.default_rng(int(seed) * 4007 + 17)
    out = []
    for intent_id, (a, o) in enumerate(intents):
        for _ in range(n_per_intent):
            t = _TEST_TEMPLATES[int(rng.integers(0, len(_TEST_TEMPLATES)))]
            out.append((t.format(action=a, obj=o), intent_id))
    idxs = np.arange(len(out))
    rng.shuffle(idxs)
    return [out[int(i)] for i in idxs]


# =============================================================================
# Substrate Hebbian classifier (mirrors a1)
# =============================================================================

def _make_intent_codebook(n_intents: int, n_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(int(seed) * 1009 + 17)
    return (rng.integers(0, 2, size=(n_intents, n_dim)) * 2 - 1).astype(np.float32)


def hebbian_train(question_hds: np.ndarray, labels: np.ndarray,
                  intent_codebook: np.ndarray) -> np.ndarray:
    intent_per_q = intent_codebook[labels]
    W = (intent_per_q.T @ question_hds) / float(intent_codebook.shape[1])
    return W.astype(np.float32)


def hebbian_predict(question_hd: np.ndarray, W: np.ndarray,
                    intent_codebook: np.ndarray) -> int:
    Wq = W @ question_hd
    scores = intent_codebook @ Wq
    return int(np.argmax(scores))


# =============================================================================
# Per (n_intents, seed) eval
# =============================================================================

def run_one_n_intents(n_intents: int, seed: int,
                       encoder: CharTrigramEncoder) -> Dict:
    intents = make_intents(n_intents, seed)
    train = synth_train(intents, N_TRAIN_PER_INTENT, seed)
    test = synth_test(intents, N_TEST_PER_INTENT, seed)

    train_q = [t[0] for t in train]
    train_y = np.array([t[1] for t in train], dtype=np.int64)
    test_q = [t[0] for t in test]
    test_y = np.array([t[1] for t in test], dtype=np.int64)

    t_enc = time.perf_counter()
    train_hds = encoder.encode_batch(train_q).astype(np.float32)
    test_hds = encoder.encode_batch(test_q).astype(np.float32)
    encode_s = time.perf_counter() - t_enc

    intent_codebook = _make_intent_codebook(n_intents, N_DIM, seed)

    t_train = time.perf_counter()
    W = hebbian_train(train_hds, train_y, intent_codebook)
    train_s = time.perf_counter() - t_train

    # SUBSTRATE arm: per-query latency (honest p95)
    latencies_ms = []
    sub_preds = np.zeros(len(test_y), dtype=np.int64)
    for i in range(len(test_y)):
        t0 = time.perf_counter()
        sub_preds[i] = hebbian_predict(test_hds[i], W, intent_codebook)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
    sub_acc = float((sub_preds == test_y).mean())
    p95_ms = float(np.percentile(latencies_ms, 95))

    # RANDOM baseline
    rng = np.random.default_rng(int(seed) * 7919 + 31)
    rand_preds = rng.integers(0, n_intents, size=len(test_y))
    rand_acc = float((rand_preds == test_y).mean())

    # MAJORITY baseline
    counts = Counter(int(x) for x in train_y.tolist())
    maj_id = max(counts.items(), key=lambda kv: kv[1])[0]
    maj_preds = np.full(len(test_y), int(maj_id), dtype=np.int64)
    maj_acc = float((maj_preds == test_y).mean())

    print("    [seed=%d n_intents=%d] SUBSTRATE=%.4f RANDOM=%.4f MAJORITY=%.4f "
          "p95_ms=%.2f encode_s=%.1f train_s=%.1f"
          % (seed, n_intents, sub_acc, rand_acc, maj_acc, p95_ms, encode_s, train_s),
          flush=True)

    return {
        "n_intents": n_intents,
        "n_train": len(train),
        "n_test": len(test),
        "substrate_acc": sub_acc,
        "random_acc": rand_acc,
        "majority_acc": maj_acc,
        "p95_latency_ms": p95_ms,
        "encode_s": float(encode_s),
        "train_s": float(train_s),
    }


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    encoder = CharTrigramEncoder(n_dim=N_DIM)
    per_n = {}
    for n_intents in N_INTENTS_SWEEP:
        per_n[n_intents] = run_one_n_intents(n_intents, seed, encoder)
    return {
        "seed": seed,
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_n_intents": {str(k): v for k, v in per_n.items()},
        "elapsed_s": round(time.time() - t0, 2),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


# =============================================================================
# Verdict
# =============================================================================

def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("HARD_FAIL", "no per-seed data")
    # Aggregate per n_intents: mean substrate_acc, cv, mean p95, mean random, mean majority
    agg = {}
    for n in N_INTENTS_SWEEP:
        rows = [p["per_n_intents"].get(str(n), {}) for p in per_seed]
        rows = [r for r in rows if r]
        if not rows:
            continue
        sub_accs = [float(r["substrate_acc"]) for r in rows]
        rand_accs = [float(r["random_acc"]) for r in rows]
        maj_accs = [float(r["majority_acc"]) for r in rows]
        p95s = [float(r["p95_latency_ms"]) for r in rows]
        m_sub = float(np.mean(sub_accs))
        m_rand = float(np.mean(rand_accs))
        m_maj = float(np.mean(maj_accs))
        m_p95 = float(np.mean(p95s))
        cv_sub = float(np.std(sub_accs) / max(abs(m_sub), 1e-9)) if len(sub_accs) >= 2 else 0.0
        agg[n] = {
            "substrate_acc_mean": round(m_sub, 4),
            "substrate_acc_cv": round(cv_sub, 4),
            "random_acc_mean": round(m_rand, 4),
            "majority_acc_mean": round(m_maj, 4),
            "p95_latency_ms_mean": round(m_p95, 4),
            "per_seed_substrate": [round(x, 4) for x in sub_accs],
        }

    summ_pieces = []
    for n in N_INTENTS_SWEEP:
        if n not in agg:
            continue
        a = agg[n]
        summ_pieces.append(
            "n=%d SUB=%.4f (cv=%.3f) RAND=%.4f MAJ=%.4f p95=%.2fms" % (
                n, a["substrate_acc_mean"], a["substrate_acc_cv"],
                a["random_acc_mean"], a["majority_acc_mean"], a["p95_latency_ms_mean"]))
    summ = " | ".join(summ_pieces)

    # Sanity rail at n=50
    sanity_ok = True
    if 50 in agg:
        sub_50 = agg[50]["substrate_acc_mean"]
        if not (SANITY_RAIL_ACC_50_LO <= sub_50 <= SANITY_RAIL_ACC_50_HI):
            sanity_ok = False

    # HARD_PASS_PRODUCTION_INTENT_SCALE
    if 500 in agg:
        a500 = agg[500]
        if (a500["substrate_acc_mean"] >= HP_PROD_SCALE_ACC_AT_500
                and a500["p95_latency_ms_mean"] <= HP_PROD_SCALE_P95_MS
                and a500["substrate_acc_cv"] <= HP_CV_MAX):
            return ("HARD_PASS_PRODUCTION_INTENT_SCALE",
                    "HARD_PASS_PRODUCTION_INTENT_SCALE_AT_500_INTENTS: " + summ)

    # HARD_FAIL_CLIFF_AT_100
    if 100 in agg:
        if agg[100]["substrate_acc_mean"] < HF_CLIFF_AT_100_ACC:
            return ("HARD_FAIL_CLIFF_AT_100",
                    "HARD_FAIL_CLIFF_AT_100_DOES_NOT_EXTEND_BEYOND_RAIL: " + summ)

    # CHAIN_GRADE_AT_CLIFF_X: largest n in {100, 200, 500} where mean >= 0.65 and cv <= 0.07
    chain_grade_x = 0
    for n in [100, 200, 500]:
        if n in agg:
            a = agg[n]
            if (a["substrate_acc_mean"] >= CHAIN_GRADE_ACC
                    and a["substrate_acc_cv"] <= HP_CV_MAX):
                chain_grade_x = n
    if chain_grade_x > 50:
        return ("CHAIN_GRADE_AT_CLIFF_X",
                "CHAIN_GRADE_AT_CLIFF_%d_INTENTS: %s" % (chain_grade_x, summ))

    if not sanity_ok:
        return ("RAIL_SANITY_BREACH",
                "RAIL_SANITY_BREACH_50_INTENT_RAIL_OUT_OF_BAND: " + summ)

    return ("MIDDLE_BAND", "MIDDLE_BAND_PARTIAL_SCALING: " + summ)


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    # T1: intent generation
    intents = make_intents(50, 11)
    assert len(intents) == 50
    assert len(set(intents)) == 50, "T1 intents not unique"
    print("[selftest] T1 PASS: make_intents 50 unique pairs")

    # T2: train/test deterministic per seed
    train1 = synth_train(intents, 5, 11)
    train2 = synth_train(intents, 5, 11)
    assert train1 == train2, "T2 train not deterministic per seed"
    print("[selftest] T2 PASS: train deterministic per seed")

    # T3: encoder shape
    enc = CharTrigramEncoder(n_dim=64)
    v = enc.encode("please find the email")
    assert v.shape == (64,), "T3 encoder shape %s" % (v.shape,)
    print("[selftest] T3 PASS: encoder output shape (64,)")

    # T4: Hebbian train/predict roundtrip on tiny scale
    rng = np.random.default_rng(0)
    nd = 128
    n_intents = 5
    n_train = 20
    train_hds = rng.standard_normal((n_train, nd)).astype(np.float32)
    train_y = rng.integers(0, n_intents, n_train).astype(np.int64)
    cb = (rng.integers(0, 2, size=(n_intents, nd)) * 2 - 1).astype(np.float32)
    W = hebbian_train(train_hds, train_y, cb)
    assert W.shape == (nd, nd)
    pred = hebbian_predict(train_hds[0], W, cb)
    assert 0 <= pred < n_intents
    print("[selftest] T4 PASS: Hebbian train+predict shapes correct")

    # T5: smoke run on a tiny config (1 seed n_intents=5)
    smoke_enc = CharTrigramEncoder(n_dim=512)
    small_intents = make_intents(5, 11)
    train_small = synth_train(small_intents, 10, 11)
    test_small = synth_test(small_intents, 5, 11)
    train_q = [t[0] for t in train_small]
    train_y_s = np.array([t[1] for t in train_small], dtype=np.int64)
    test_q = [t[0] for t in test_small]
    test_y_s = np.array([t[1] for t in test_small], dtype=np.int64)
    train_hds_s = smoke_enc.encode_batch(train_q).astype(np.float32)
    test_hds_s = smoke_enc.encode_batch(test_q).astype(np.float32)
    cb_s = _make_intent_codebook(5, 512, 11)
    W_s = hebbian_train(train_hds_s, train_y_s, cb_s)
    preds = np.array([hebbian_predict(test_hds_s[i], W_s, cb_s)
                       for i in range(len(test_y_s))])
    acc_smoke = float((preds == test_y_s).mean())
    assert acc_smoke > 0.40, \
        "T5 smoke acc=%.3f at 5 intents must beat random (0.20) by margin" % acc_smoke
    print("[selftest] T5 PASS: 5-intent smoke acc=%.3f beats random" % acc_smoke)

    # T6: LLM counter
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] T6 PASS: LLM counter = 0")

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# atexit + main
# =============================================================================

_RESULTS_HOLDER: Dict = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = compute_verdict(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = compute_verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "EXT-3 intent classifier scaling 50 -> 1000 intents on the SAME "
            "substrate Hebbian-bound prototype-bundle classifier at N=8192. "
            "Procedural action-object intent corpus; held-out test paraphrases "
            "(disjoint templates from train). Per n_intents: substrate / random / "
            "majority arms; per-arm acc + p95 latency + cv reported. Char-trigram "
            "encoder; zero LLM forward calls."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
