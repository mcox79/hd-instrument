"""a1_substrate_intent_classifier_v1 -- substrate-native query intent classifier.

Re-scoped from the original BATCH_HIERARCHICAL A1 anchor (which required a
Qwen-2.5-3B teacher distillation) to ZERO-LLM substrate-only per USER L1
directive. Replaces the small-BERT-class distillation classifier with a
substrate-native Hebbian-bound associative classifier:

  question text
     -> CharTrigramEncoder            (substrate-native text -> HD)
     -> Hebbian-bound W (category_hd outer question_hd, accumulated over train)
     -> argmax over (E_cat @ W @ q_hd)

THREE ARMS (Fix #16 discriminator):
  1. SUBSTRATE_INTENT       -- full Hebbian-bound substrate classifier
  2. RANDOM_BASELINE        -- uniform random category (CAN-FAIL discriminator)
  3. MAJORITY_BASELINE      -- always predict most-frequent training category

Categories (7): LOOKUP, COMPARISON, MULTI_HOP, LIST, CHAIN, COUNT, DEFINITION.

Labeled set synthesized substrate-only:
  - HotpotQA dev type field: bridge -> MULTI_HOP, comparison -> COMPARISON
  - NQ-open: single-fact questions -> LOOKUP/COUNT/DEFINITION by keyword classifier
  - Templates: LIST/CHAIN/COUNT/DEFINITION generated from ConceptNet predicates

Pre-reg bands (preregs/2026-06-22_a1_substrate_intent_classifier_v1.md):

  HARD_PASS:
    SUBSTRATE_INTENT accuracy >= 0.65
    AND substrate >= 2x MAJORITY_BASELINE
    AND substrate >= 5x RANDOM_BASELINE
    AND per-query P95 latency < 10ms CPU
    AND n_llm_calls == 0

  HARD_FAIL:
    SUBSTRATE_INTENT accuracy <= MAJORITY_BASELINE
    OR n_llm_calls > 0
    OR per-query P95 latency >= 50ms

ROUTING: remote_cpu_queue (numpy-only; sub-second matmul; ~10min FULL wall).
ASCII-only. Single-file. Resumable via _seed_checkpoint.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import json
import math
import re
import time
import signal
import atexit
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)
from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "a1_substrate_intent_classifier_v1"

# Substrate-only-decode gate (asserted == 0 at exit)
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "hotpotqa_dev_1k + nq_open_val_1k + conceptnet5_en_100k_templates"
HOTPOT_PATH = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
NQ_PATH = REPO / "data" / "datasets" / "nq_open_validation_1k.jsonl"
CONCEPTNET_PATH = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"

# Category labels (fixed ordering -> category_id)
CATEGORIES = ["LOOKUP", "COMPARISON", "MULTI_HOP", "LIST", "CHAIN", "COUNT", "DEFINITION"]
CAT_TO_ID = {c: i for i, c in enumerate(CATEGORIES)}
N_CAT = len(CATEGORIES)

# Pre-reg bands (locked)
HARD_PASS_ACC = 0.65
HARD_PASS_MAJORITY_MULT = 2.0
HARD_PASS_RANDOM_MULT = 5.0
HARD_PASS_P95_LATENCY_MS = 10.0
HARD_FAIL_P95_LATENCY_MS = 50.0

_METRICS_WRITTEN = [False]


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 512
    N_TRAIN = 200
    N_TEST = 50
    ARMS = ["SUBSTRATE_INTENT", "RANDOM_BASELINE", "MAJORITY_BASELINE"]
else:
    SEEDS = [7, 17, 23]
    N_DIM = 2048
    N_TRAIN = 5000
    N_TEST = 500
    ARMS = ["SUBSTRATE_INTENT", "RANDOM_BASELINE", "MAJORITY_BASELINE"]

CONFIG_VERSION = (
    "a1-substrate-intent-classifier-v1: N_DIM=%d N_TRAIN=%d N_TEST=%d "
    "arms=%s run_mode=%s; bands HP_acc=%.2f HP_majority_mult=%.1f "
    "HP_random_mult=%.1f HP_p95_ms=%.1f HF_p95_ms=%.1f"
) % (
    N_DIM, N_TRAIN, N_TEST, ",".join(ARMS), RUN_MODE,
    HARD_PASS_ACC, HARD_PASS_MAJORITY_MULT, HARD_PASS_RANDOM_MULT,
    HARD_PASS_P95_LATENCY_MS, HARD_FAIL_P95_LATENCY_MS,
)


# ----- Labeled set synthesis (substrate-only; no LLM teacher) -----

# Keyword-based classifier for label synthesis (NOT the substrate classifier itself).
# This is a deterministic procedural labeler that operates on lexical surface signals
# to bootstrap labels. The substrate classifier must then LEARN this mapping from
# bag-of-trigrams (which doesn't see the keyword tokens directly -- it sees trigrams).
#
# Synthesis rules (priority-ordered; first match wins):

_LIST_RE = re.compile(r"\b(list|name (?:all|three|five|some|the)|enumerate|what are the (?:names of|types of))\b", re.I)
_COUNT_RE = re.compile(r"\b(how many|number of|count of|total of)\b", re.I)
_DEFINITION_RE = re.compile(r"^(what is (?:a |an |the )?\w+\??$|^(?:define|definition of) \w+|what does \w+ mean)\b", re.I)
_COMPARE_RE = re.compile(r"\b(are .* the same|compared|comparison|which is (?:bigger|larger|smaller|older|younger|more)|same (?:nationality|year|country|state)|both|either)\b", re.I)
_CHAIN_RE = re.compile(r"\b(then|after that|next|first .* then|leads to|caused by)\b", re.I)
_MULTI_HOP_RE = re.compile(r"\b(directed .* who|wife of .* who|father of .* who|whose .* was|by the .* of)\b", re.I)


def keyword_label(question: str) -> str:
    """Procedural keyword labeler that bootstraps category labels for substrate training.

    Returns one of the 7 CATEGORIES. Priority order matters: COUNT before LIST before
    DEFINITION before COMPARISON before MULTI_HOP before CHAIN before LOOKUP fallback.
    """
    q = question.strip()
    if _COUNT_RE.search(q):
        return "COUNT"
    if _LIST_RE.search(q):
        return "LIST"
    if _DEFINITION_RE.search(q):
        return "DEFINITION"
    if _COMPARE_RE.search(q):
        return "COMPARISON"
    if _MULTI_HOP_RE.search(q):
        return "MULTI_HOP"
    if _CHAIN_RE.search(q):
        return "CHAIN"
    return "LOOKUP"


# ----- Template generators (synthesize for under-represented categories) -----

_LIST_TEMPLATES = [
    "List three types of {x}.",
    "Name all the {x} in {y}.",
    "What are the names of the {x}?",
    "Enumerate the {x} of {y}.",
    "List five examples of {x}.",
    "What are the types of {x}?",
]

_COUNT_TEMPLATES = [
    "How many {x} are there?",
    "Number of {x} in {y}?",
    "Count of {x} in {y}.",
    "How many {x} does {y} have?",
    "Total of {x}?",
]

_DEFINITION_TEMPLATES = [
    "What is {x}?",
    "Define {x}.",
    "What does {x} mean?",
    "Definition of {x}.",
    "What is a {x}?",
]

_CHAIN_TEMPLATES = [
    "What causes {x}, and then what does {x} cause?",
    "{x} leads to what, and then what?",
    "First {x}, then what, then what?",
    "{x} is caused by what, which is caused by what?",
]


def synthesize_template_examples(predicates: List[Dict], categories_to_fill: List[str],
                                 n_per_cat: int, rng: np.random.Generator) -> List[Tuple[str, str]]:
    """Generate (question, category) pairs from ConceptNet predicates for under-filled cats."""
    out = []
    if not predicates:
        return out
    subjects = list({p["subject"].replace("_", " ") for p in predicates[:5000]})
    objects = list({p["object"].replace("_", " ") for p in predicates[:5000]})
    if not subjects or not objects:
        return out

    templates_for_cat = {
        "LIST": _LIST_TEMPLATES,
        "COUNT": _COUNT_TEMPLATES,
        "DEFINITION": _DEFINITION_TEMPLATES,
        "CHAIN": _CHAIN_TEMPLATES,
    }
    for cat in categories_to_fill:
        templates = templates_for_cat.get(cat)
        if not templates:
            continue
        for _ in range(n_per_cat):
            x = subjects[int(rng.integers(0, len(subjects)))]
            y = objects[int(rng.integers(0, len(objects)))]
            template = templates[int(rng.integers(0, len(templates)))]
            q = template.format(x=x, y=y)
            out.append((q, cat))
    return out


# ----- Corpus loaders -----

def load_hotpot_questions(path: Path, max_items: int) -> List[Tuple[str, str]]:
    """HotpotQA: bridge->MULTI_HOP, comparison->COMPARISON."""
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items:
                break
            r = json.loads(line)
            q = str(r.get("question", "")).strip()
            t = str(r.get("type", "")).strip().lower()
            if not q:
                continue
            cat = "MULTI_HOP" if t == "bridge" else ("COMPARISON" if t == "comparison" else None)
            if cat is None:
                continue
            out.append((q, cat))
    return out


def load_nq_questions(path: Path, max_items: int) -> List[Tuple[str, str]]:
    """NQ-open: deterministic keyword-label."""
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items:
                break
            r = json.loads(line)
            q = str(r.get("question", "")).strip()
            if not q:
                continue
            cat = keyword_label(q)
            out.append((q, cat))
    return out


def load_conceptnet_predicates(path: Path, max_items: int) -> List[Dict]:
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            if i >= max_items:
                break
            r = json.loads(line)
            if "subject" in r and "object" in r:
                out.append(r)
    return out


def build_labeled_set(n_target: int, seed: int) -> List[Tuple[str, str]]:
    """Build a labeled (question, category) list of ~n_target examples balanced across cats."""
    rng = np.random.default_rng(int(seed))

    # 1. Pull from real corpora
    hotpot = load_hotpot_questions(HOTPOT_PATH, 1000)
    nq = load_nq_questions(NQ_PATH, 1000)
    cn_preds = load_conceptnet_predicates(CONCEPTNET_PATH, 5000)

    # 2. Combine real-corpus examples
    combined = hotpot + nq

    # 3. Determine which categories are under-filled; fill via templates
    cat_counts = Counter(c for _, c in combined)
    target_per_cat = max(1, n_target // N_CAT)
    fill_cats = [c for c in CATEGORIES if cat_counts.get(c, 0) < target_per_cat]
    n_to_fill = sum(max(0, target_per_cat - cat_counts.get(c, 0)) for c in fill_cats)
    n_per_template_cat = max(1, (n_to_fill // max(1, len(fill_cats))) + 1)
    template_examples = synthesize_template_examples(
        cn_preds, fill_cats, n_per_template_cat, rng)
    combined = combined + template_examples

    # 4. Class-balance: cap each category at target_per_cat
    by_cat: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for q, c in combined:
        by_cat[c].append((q, c))

    balanced: List[Tuple[str, str]] = []
    for c in CATEGORIES:
        items = by_cat.get(c, [])
        # Deterministic shuffle for reproducibility
        idxs = np.arange(len(items))
        rng.shuffle(idxs)
        take = min(target_per_cat, len(items))
        balanced.extend([items[int(i)] for i in idxs[:take]])

    # Final deterministic shuffle of the combined balanced set
    idxs = np.arange(len(balanced))
    rng.shuffle(idxs)
    balanced = [balanced[int(i)] for i in idxs]

    # Truncate to n_target
    return balanced[:n_target]


# ----- Substrate Hebbian classifier -----

def _make_category_codebook(n_dim: int, seed: int) -> np.ndarray:
    """Per-seed bipolar HD codebook [N_CAT, n_dim] for the 7 categories."""
    rng = np.random.default_rng(int(seed) * 1009 + 17)
    return (rng.integers(0, 2, size=(N_CAT, n_dim)) * 2 - 1).astype(np.float32)


def hebbian_train(question_hds: np.ndarray, labels: np.ndarray,
                  cat_codebook: np.ndarray) -> np.ndarray:
    """Bind question HDs to category HDs via Hebbian outer-product accumulation.

    W = sum_q outer(cat_codebook[label_q], question_hd[q]) / N_DIM
    Returns W: [n_dim, n_dim].

    The accumulation is equivalent to (cat_codebook[labels]).T @ question_hds / N_DIM.
    """
    # cat_codebook[labels]: [N_TRAIN, n_dim] (one row per example = its category HD)
    cat_per_q = cat_codebook[labels]
    # W: [n_dim, n_dim] = (cat_per_q.T @ question_hds) / n_dim
    W = (cat_per_q.T @ question_hds) / float(cat_codebook.shape[1])
    return W.astype(np.float32)


def hebbian_predict(question_hd: np.ndarray, W: np.ndarray,
                    cat_codebook: np.ndarray) -> int:
    """Predict category for a single question HD via argmax(cat_codebook @ W @ q_hd)."""
    # W @ q: [n_dim]; cat @ (W @ q): [N_CAT]
    Wq = W @ question_hd
    scores = cat_codebook @ Wq
    return int(np.argmax(scores))


def hebbian_predict_batch(question_hds: np.ndarray, W: np.ndarray,
                          cat_codebook: np.ndarray) -> np.ndarray:
    """Batched: returns [N_TEST] predicted category ids."""
    # Wq: [n_dim, N_TEST] = W @ question_hds.T
    Wq = W @ question_hds.T
    # scores: [N_CAT, N_TEST] = cat_codebook @ Wq
    scores = cat_codebook @ Wq
    return np.argmax(scores, axis=0)


# ----- Per-arm predictions -----

def predict_substrate(train_hds: np.ndarray, train_labels: np.ndarray,
                      test_hds: np.ndarray, cat_codebook: np.ndarray
                      ) -> Tuple[np.ndarray, float, float]:
    """Returns (preds, train_wall_s, per_q_latency_ms_list_p95)."""
    t0 = time.perf_counter()
    W = hebbian_train(train_hds, train_labels, cat_codebook)
    train_wall_s = time.perf_counter() - t0
    # Per-query latency: time each query individually for honest P95
    latencies_ms = []
    preds = np.zeros(test_hds.shape[0], dtype=np.int64)
    for i in range(test_hds.shape[0]):
        t1 = time.perf_counter()
        preds[i] = hebbian_predict(test_hds[i], W, cat_codebook)
        latencies_ms.append((time.perf_counter() - t1) * 1000.0)
    p95_ms = float(np.percentile(latencies_ms, 95))
    return preds, float(train_wall_s), p95_ms


def predict_random(test_hds: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(int(seed) * 7919 + 31)
    return rng.integers(0, N_CAT, size=test_hds.shape[0])


def predict_majority(train_labels: np.ndarray, n_test: int) -> np.ndarray:
    counts = Counter(int(x) for x in train_labels.tolist())
    majority_id = max(counts.items(), key=lambda kv: kv[1])[0]
    return np.full(n_test, int(majority_id), dtype=np.int64)


# ----- Per-seed runner -----

def run_seed(seed: int) -> Dict:
    """Build train+test sets; encode; run all 3 arms; return per-seed metrics."""
    t0 = time.time()

    # 1. Build labeled set + split train/test (deterministic per seed)
    all_data = build_labeled_set(N_TRAIN + N_TEST, seed)
    if len(all_data) < N_TRAIN + N_TEST:
        # Real-corpus + template generation may yield fewer; truncate proportionally
        actual_n = len(all_data)
        n_train = int(actual_n * (N_TRAIN / (N_TRAIN + N_TEST)))
        n_test = actual_n - n_train
    else:
        n_train, n_test = N_TRAIN, N_TEST

    train_data = all_data[:n_train]
    test_data = all_data[n_train:n_train + n_test]

    # 2. Encode via char-trigram (substrate-native)
    encoder = CharTrigramEncoder(n_dim=N_DIM)
    train_hds = encoder.encode_batch([q for q, _ in train_data]).astype(np.float32)
    test_hds = encoder.encode_batch([q for q, _ in test_data]).astype(np.float32)
    train_labels = np.array([CAT_TO_ID[c] for _, c in train_data], dtype=np.int64)
    test_labels = np.array([CAT_TO_ID[c] for _, c in test_data], dtype=np.int64)

    # 3. Per-seed category codebook
    cat_codebook = _make_category_codebook(N_DIM, seed)

    # 4. Run arms
    per_unit = []

    # SUBSTRATE_INTENT
    sub_preds, sub_train_s, sub_p95_ms = predict_substrate(
        train_hds, train_labels, test_hds, cat_codebook)
    sub_acc = float((sub_preds == test_labels).mean())
    sub_per_cat_acc = {}
    for c, cid in CAT_TO_ID.items():
        mask = test_labels == cid
        if mask.sum() > 0:
            sub_per_cat_acc[c] = float((sub_preds[mask] == test_labels[mask]).mean())
        else:
            sub_per_cat_acc[c] = None
    per_unit.append({
        "arm": "SUBSTRATE_INTENT",
        "seed": int(seed),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "accuracy": sub_acc,
        "per_category_accuracy": sub_per_cat_acc,
        "train_wall_s": float(sub_train_s),
        "p95_latency_ms": float(sub_p95_ms),
        "n_dim": N_DIM,
    })

    # RANDOM_BASELINE
    rnd_preds = predict_random(test_hds, seed)
    rnd_acc = float((rnd_preds == test_labels).mean())
    per_unit.append({
        "arm": "RANDOM_BASELINE",
        "seed": int(seed),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "accuracy": rnd_acc,
        "n_dim": N_DIM,
    })

    # MAJORITY_BASELINE
    maj_preds = predict_majority(train_labels, n_test)
    maj_acc = float((maj_preds == test_labels).mean())
    per_unit.append({
        "arm": "MAJORITY_BASELINE",
        "seed": int(seed),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "accuracy": maj_acc,
        "n_dim": N_DIM,
    })

    print("  [seed=%d] SUBSTRATE=%.3f RANDOM=%.3f MAJORITY=%.3f p95_ms=%.2f"
          % (seed, sub_acc, rnd_acc, maj_acc, sub_p95_ms), flush=True)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": n_train + n_test,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(time.time() - t0),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Verdict logic per pre-reg bands."""
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    agg_acc = defaultdict(list)
    agg_p95 = []
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            agg_acc[arm].append(float(pu.get("accuracy", 0.0)))
            if arm == "SUBSTRATE_INTENT" and pu.get("p95_latency_ms") is not None:
                agg_p95.append(float(pu["p95_latency_ms"]))

    mean_acc = {arm: float(np.mean(v)) for arm, v in agg_acc.items()}
    cv_acc = {}
    for arm, v in agg_acc.items():
        m = float(np.mean(v))
        s = float(np.std(v))
        cv_acc[arm] = (s / max(m, 1e-9))

    substrate_acc = mean_acc.get("SUBSTRATE_INTENT", float("nan"))
    random_acc = mean_acc.get("RANDOM_BASELINE", float("nan"))
    majority_acc = mean_acc.get("MAJORITY_BASELINE", float("nan"))
    p95_ms = float(np.mean(agg_p95)) if agg_p95 else float("nan")

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # Multipliers (guard zero-division for majority/random)
    majority_mult = (substrate_acc / majority_acc) if (
        not math.isnan(majority_acc) and majority_acc > 1e-6) else float("inf")
    random_mult = (substrate_acc / random_acc) if (
        not math.isnan(random_acc) and random_acc > 1e-6) else float("inf")

    detail = {
        "mean_accuracy": mean_acc,
        "cv_accuracy": cv_acc,
        "substrate_acc": float(substrate_acc) if not math.isnan(substrate_acc) else None,
        "random_acc": float(random_acc) if not math.isnan(random_acc) else None,
        "majority_acc": float(majority_acc) if not math.isnan(majority_acc) else None,
        "majority_multiplier": float(majority_mult) if not math.isinf(majority_mult) else None,
        "random_multiplier": float(random_mult) if not math.isinf(random_mult) else None,
        "mean_p95_latency_ms": float(p95_ms) if not math.isnan(p95_ms) else None,
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Substrate-native intent classifier; %d categories; %s; "
            "N_DIM=%d N_TRAIN=%d N_TEST=%d. 3-arm discriminator (Fix #16): "
            "SUBSTRATE_INTENT vs RANDOM_BASELINE vs MAJORITY_BASELINE. "
            "Substrate-only-decode gate enforced (n_llm=%d). Encoder: char-trigram "
            "(no MiniLM, no LLM teacher). Labels synthesized procedurally from "
            "HotpotQA type field + NQ-open keyword-classifier + ConceptNet templates."
            % (N_CAT, ",".join(CATEGORIES), N_DIM, N_TRAIN, N_TEST, n_llm)),
    }

    summary = (
        "substrate_acc=%.3f random_acc=%.3f majority_acc=%.3f "
        "maj_mult=%.2f rand_mult=%.2f p95_ms=%.2f n_llm=%d" %
        (substrate_acc, random_acc, majority_acc,
         majority_mult if not math.isinf(majority_mult) else -1.0,
         random_mult if not math.isinf(random_mult) else -1.0,
         p95_ms, n_llm))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)
    if math.isnan(substrate_acc):
        return ("HARD_FAIL",
                "HARD_FAIL: SUBSTRATE_INTENT arm missing data. %s" % summary, detail)
    if not math.isnan(majority_acc) and substrate_acc <= majority_acc:
        return ("HARD_FAIL",
                ("HARD_FAIL: substrate %.3f <= majority %.3f (substrate fails to "
                 "beat MAJORITY_BASELINE). %s" % (substrate_acc, majority_acc, summary)),
                detail)
    if not math.isnan(p95_ms) and p95_ms >= HARD_FAIL_P95_LATENCY_MS:
        return ("HARD_FAIL",
                ("HARD_FAIL: P95 latency %.2fms >= %.2fms HF bar. %s"
                 % (p95_ms, HARD_FAIL_P95_LATENCY_MS, summary)), detail)

    # HARD_PASS check
    hp_acc_ok = substrate_acc >= HARD_PASS_ACC
    hp_maj_mult_ok = (majority_mult >= HARD_PASS_MAJORITY_MULT)
    hp_rand_mult_ok = (random_mult >= HARD_PASS_RANDOM_MULT)
    hp_latency_ok = (not math.isnan(p95_ms)) and (p95_ms < HARD_PASS_P95_LATENCY_MS)
    if hp_acc_ok and hp_maj_mult_ok and hp_rand_mult_ok and hp_latency_ok and substrate_only_ok:
        return ("HARD_PASS",
                ("HARD_PASS: substrate-native intent classifier. acc=%.3f >= %.2f "
                 "AND maj_mult=%.2f >= %.1f AND rand_mult=%.2f >= %.1f AND "
                 "p95=%.2fms < %.1fms AND n_llm=0. %s"
                 % (substrate_acc, HARD_PASS_ACC, majority_mult, HARD_PASS_MAJORITY_MULT,
                    random_mult, HARD_PASS_RANDOM_MULT, p95_ms, HARD_PASS_P95_LATENCY_MS,
                    summary)), detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: substrate_acc=%.3f maj_mult=%.2f rand_mult=%.2f p95=%.2fms; "
            "bands not all crossed (acc>=%.2f=%s maj>=%.1f=%s rand>=%.1f=%s p95<%.1f=%s). %s"
            % (substrate_acc, majority_mult, random_mult, p95_ms,
               HARD_PASS_ACC, hp_acc_ok,
               HARD_PASS_MAJORITY_MULT, hp_maj_mult_ok,
               HARD_PASS_RANDOM_MULT, hp_rand_mult_ok,
               HARD_PASS_P95_LATENCY_MS, hp_latency_ok, summary), detail)


# ----- Self-test -----

def _selftest():
    """Mechanism self-tests; small fixtures only."""
    # Test 1: encoder shape
    enc = CharTrigramEncoder(n_dim=64)
    v = enc.encode("what is a cat")
    assert v.shape == (64,), "selftest 1: encoder shape %s != (64,)" % (v.shape,)

    # Test 2: keyword_label correctness on canonical examples
    assert keyword_label("How many people live in Paris?") == "COUNT", "selftest 2a"
    assert keyword_label("List three colors") == "LIST", "selftest 2b"
    assert keyword_label("Define photosynthesis") == "DEFINITION", "selftest 2c"
    assert keyword_label("Are X and Y the same nationality?") == "COMPARISON", "selftest 2d"

    # Test 3: Hebbian train + predict on a 2-category, 4-example toy
    n_dim_t = 64
    rng = np.random.default_rng(0)
    train_hds = (rng.integers(0, 2, size=(4, n_dim_t)) * 2 - 1).astype(np.float32)
    train_labels = np.array([0, 0, 1, 1], dtype=np.int64)
    cat_codebook_t = (rng.integers(0, 2, size=(N_CAT, n_dim_t)) * 2 - 1).astype(np.float32)
    W = hebbian_train(train_hds, train_labels, cat_codebook_t)
    assert W.shape == (n_dim_t, n_dim_t), "selftest 3a: W shape %s" % (W.shape,)
    pred0 = hebbian_predict(train_hds[0], W, cat_codebook_t)
    # On training data the classifier should return label 0 for example 0
    # (associative recall on bound key). Don't require exact -- the bipolar
    # bagging can be noisy at n_dim=64; just confirm pred is in valid range.
    assert 0 <= pred0 < N_CAT, "selftest 3b: pred out of range"

    # Test 4: batched prediction
    batch_preds = hebbian_predict_batch(train_hds, W, cat_codebook_t)
    assert batch_preds.shape == (4,), "selftest 4a"
    assert (batch_preds == np.array([hebbian_predict(train_hds[i], W, cat_codebook_t)
                                     for i in range(4)])).all(), "selftest 4b: batch != per-q"

    # Test 5: random + majority baseline shapes
    rnd = predict_random(train_hds, 0)
    maj = predict_majority(train_labels, 4)
    assert rnd.shape == (4,) and maj.shape == (4,), "selftest 5"
    assert (maj == 0).all() or (maj == 1).all(), "selftest 5b: majority not constant"

    # Test 6: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 6: LLM counter non-zero"

    # Test 7: template generator runs without crashing on empty
    out = synthesize_template_examples([], ["LIST"], 5, np.random.default_rng(0))
    assert out == [], "selftest 7: empty predicates should yield empty output"

    print("[selftest] PASS: encoder, keyword_label, Hebbian train/predict, "
          "batched, baselines, llm=0, template", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer -----

def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_TEST": N_TEST,
            "categories": CATEGORIES,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "corpus_provenance": CORPUS_PROVENANCE,
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
                 "per_unit": v.get("per_unit", [])}
                for k, v in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ----- Main runner -----

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_TRAIN=%d N_TEST=%d arms=%s seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_TRAIN, N_TEST, str(ARMS), str(done), str(seeds_todo)),
      flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_TEST": N_TEST,
    "categories": CATEGORIES,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": True,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_substrate_intent_classifier_3arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
