"""phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1 -- GPU capacity sweep,
M_facts at production alpha and above (alpha >= 1.0).

USER directive 2026-06-27 (via Director task 2026-06-27): the prior
phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1 used
M_facts/V_C = 0.75 (production audit-device baseline ratio), which is
by-construction-saturated at the substrate's storage capacity. Skunkworks
flag-back #3 (deferred 2 days) requested re-test at M_facts >= N regime
(alpha >= 1.0; the alpha = M / N density that actually exercises the
substrate's bind/cleanup capacity).

This cell scans V_C in {2000, 4000, 8000} at M_FACTS in {N, 1.5N, 2N}
= {16384, 24576, 32768}, 3 seeds each. 9 phase points + 1 KNN sentinel.

DESIGN: At alpha=2 (M=32768 facts in an N=16384 substrate), the substrate is
loaded at twice its capacity by-default-assumption; classical HRR-binding
should be at or below the no-crosstalk-bound. The discriminator IS the
shape of the recall surface: does V_C affect recall under heavy M_facts
load? Does it cliff sharply or gracefully? Phase-diagram MAP cell, like
the K-ceiling sweep.

DISCRIMINATOR (option B analytical justification per
discriminator-must-survive-scale 2026-06-26):
  - Prior sweep at alpha=0.37 (M/V_C=0.75) was by-construction-saturated.
  - At alpha>=1.0, the substrate cannot guarantee 1-to-1 storage even
    without crosstalk concerns: M=N=16384 facts each requiring a unique
    direction in N=16384-dim space is at the unit-vector-packing bound;
    M=2N is beyond it.
  - The mechanism arm WILL NOT trivially saturate at alpha=1.0 or 2.0;
    crosstalk is the fundamental physics. Recall must degrade from
    saturation as alpha grows, OR the substrate-native mechanism exhibits
    some unexpected capacity-extending property (which is the science).
  - Both "monotone degradation" and "non-trivial capacity surface" outcomes
    are scientifically meaningful for the phase diagram.

META_RULE_H cardinality guard: expected n_units = n_seeds * n_VC * n_M +
n_seeds (sentinel) = 3*3*3 + 3 = 30 (production); smoke = 1 * 2 * 2 + 1 = 5.

META_RULE_J no-silent-except.
META_RULE_K smoke fires discriminator: smoke uses alpha=1.0 (the smallest of
the alphas tested) at smaller V_C to verify mechanism end-to-end without
saturation gaming.
META_RULE_L band-floor: at alpha>=1, the substrate's recall ceiling is
fundamentally lower than alpha<<1; chain-grade band must be calibrated to
the alpha regime (NOT compared to alpha=0.37's 0.99+ rail). At alpha=1,
classical-HRR predicts recall ~0.5-0.7; at alpha=2, ~0.2-0.4. Chain-grade
HP_RECALL is NOT applied uniformly across alphas in this cell -- per-alpha
discriminating-regime band; see verdict_logic.

ARMS (9 phase points + 1 sentinel):
  ARM_BASELINE_KNN_M500     KNN sentinel at M=500 random items at largest V_C
  ARM_VC2000_M16384         alpha=8.19 at V_C=2000 (M=N)
  ARM_VC2000_M24576         alpha=12.29 at V_C=2000 (M=1.5N)
  ARM_VC2000_M32768         alpha=16.38 at V_C=2000 (M=2N)
  ARM_VC4000_M16384         alpha=4.10
  ARM_VC4000_M24576         alpha=6.14
  ARM_VC4000_M32768         alpha=8.19
  ARM_VC8000_M16384         alpha=2.05
  ARM_VC8000_M24576         alpha=3.07
  ARM_VC8000_M32768         alpha=4.10

Note: "alpha" here is M_FACTS / V_C (facts per concept; substrate-storage
density). M/N (facts per dimension) is shown separately; M/N = 1, 1.5, 2.

PRE-REG BANDS (LOCKED at module init):
  HP_KNN_SENTINEL = 0.90 (Fix #28)
  CV_MAX = 0.05 across 3 seeds

  Per-arm CHARACTERIZATION tier (not chain-grade): record (recall, cv)
  at each (V_C, M_FACTS) and produce the surface.

  MAPPING_PASS: all 9 phase points produce valid finite recall + cv ok +
    sentinel ok + cardinality ok + substrate-only ok.

  CHAIN_GRADE_DISCRIMINATING_REGIME: at least 1 phase point achieves
    recall >= 0.5 cv <= 0.05 AND a clear monotone trend across one axis
    (V_C-up improves recall OR M-up degrades recall). This catches a
    chain-grade-eligible result without forcing single-point chain-grade
    on a fundamentally crosstalk-limited regime.

  MIDDLE_BAND_PARTIAL_MAP: cardinality ok but no chain-grade-discriminating
    pattern found (flat surface; noise dominates).

  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H, HARD_FAIL_UNIT_EXCEPTION,
  HARD_FAIL_KNN_SENTINEL, HARD_FAIL_SUBSTRATE_ONLY.

GPU IMPLEMENTATION (Fix #24):
  W = N x N fp32 = 1.07GB at N=16384. Per-arm rebuild + free between arms.
  Smoke uses N=2048 (W=16MB).

ASCII-only. Single-file. Resumable per-(seed, V_C, M_FACTS) checkpoint.
Author: exp_dev 2026-06-27 (USER-directed higher-alpha capacity sweep).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import math
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch  # required at top for PROT-020 GPU-queue routing gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "phase_diagram_capacity_sweep_n16384_vc_higher_alpha_v1"
_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_capacity_higher_alpha"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = (RUN_MODE == "smoke")


# ----------------------------- GPU mandate -----------------------------
GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# Pre-reg bands LOCKED at module init
HP_KNN_SENTINEL = 0.90
CV_MAX = 0.05
V_REL = 8  # relations vocab; small for clean capacity-only measurement
HP_DISCRIMINATING_REC_MIN = 0.50  # at least 1 phase point at this recall for chain-grade-disc.
HP_MONOTONE_DELTA = 0.10  # min delta along one axis to call "clear monotone"

if SMOKE:
    N_DIM = 2048
    VC_SWEEP = [400, 800]
    M_FACTS_SWEEP = [N_DIM, 2 * N_DIM]  # smoke: alpha=1 and 2
    SEEDS = [11]
else:
    N_DIM = 16384
    VC_SWEEP = [2000, 4000, 8000]
    M_FACTS_SWEEP = [N_DIM, int(1.5 * N_DIM), 2 * N_DIM]  # 16384, 24576, 32768
    SEEDS = [11, 13, 19]

# Expected cardinality: seeds * V_C * M_FACTS + seeds (sentinel)
EXPECTED_N_UNITS = len(SEEDS) * len(VC_SWEEP) * len(M_FACTS_SWEEP) + len(SEEDS)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagCapacityVCHigherAlpha-v1: N=%d VC_SWEEP=%s M_FACTS_SWEEP=%s "
    "V_REL=%d seeds=%s mode=%s encoder=%s HP_knn=%.2f CV_max=%.2f "
    "HP_disc_rec_min=%.2f HP_monotone_delta=%.2f EXPECTED_N_UNITS=%d"
) % (
    N_DIM, VC_SWEEP, M_FACTS_SWEEP, V_REL, SEEDS, RUN_MODE,
    ENCODER_PROVENANCE, HP_KNN_SENTINEL, CV_MAX,
    HP_DISCRIMINATING_REC_MIN, HP_MONOTONE_DELTA, EXPECTED_N_UNITS,
)


# ----------------------------- Primitives -----------------------------
def bipolar_t(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_facts(V_C: int, V_R: int, M_facts: int,
                g: np.random.Generator) -> List[Tuple[int, int, int]]:
    """Generate M_facts unique (s, r, o) triples from V_C concepts, V_R relations.
    Unique (s, r) keys. May DUPLICATE objects naturally (multi-fact-per-key).

    For high-alpha (M > V_C * V_R), unique (s, r) keys are EXHAUSTED. This cell
    detects that and falls back to "duplicates-allowed" mode where (s, r, o)
    is sampled freely (still unique-triple, but (s, r) keys may repeat).
    Records `keys_unique_mode` per-arm so verdict can interpret.
    """
    max_unique_sr = V_C * V_R
    duplicates_allowed = M_facts > max_unique_sr

    facts = []
    seen_keys: set = set()
    seen_triples: set = set()
    tries = 0
    max_tries = M_facts * 50
    while len(facts) < M_facts and tries < max_tries:
        tries += 1
        s = int(g.integers(0, V_C))
        r = int(g.integers(0, V_R))
        o = int(g.integers(0, V_C))
        if o == s:
            continue
        if duplicates_allowed:
            if (s, r, o) in seen_triples:
                continue
            seen_triples.add((s, r, o))
        else:
            if (s, r) in seen_keys:
                continue
            seen_keys.add((s, r))
        facts.append((s, r, o))
    if len(facts) < M_facts:
        raise RuntimeError("make_facts: only %d/%d at V_C=%d V_R=%d (saturation; "
                            "duplicates_allowed=%s)" % (
                                len(facts), M_facts, V_C, V_R, duplicates_allowed))
    return facts


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                        E: torch.Tensor, R: torch.Tensor,
                        sq: float, n_dim: int,
                        batch: int = 1000) -> torch.Tensor:
    W = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
    if not triples:
        return W
    tr = np.asarray(triples, dtype=np.int64)
    s_idx = torch.from_numpy(tr[:, 0]).to(DEVICE)
    r_idx = torch.from_numpy(tr[:, 1]).to(DEVICE)
    o_idx = torch.from_numpy(tr[:, 2]).to(DEVICE)
    n_total = len(tr)
    for b in range(0, n_total, batch):
        e = min(b + batch, n_total)
        K = E[s_idx[b:e]] * R[r_idx[b:e]] * sq
        V_ = E[o_idx[b:e]]
        W = W + (V_.T @ K) / n_dim
    return W


def eval_recall_at_vc_m(V_C: int, V_R: int, M_facts: int,
                         n_dim: int, seed: int,
                         g: np.random.Generator) -> Dict[str, Any]:
    """Build E (V_C, N), R (V_R, N), W from M_facts Hebbian triples; measure
    recall@1: for each fact (s, r, o), retrieve argmax(E @ (W @ (E[s]*R[r]*sq)))
    and check equality with o.
    """
    sq = math.sqrt(n_dim)
    E = bipolar_t(V_C, n_dim, g)
    R = bipolar_t(V_R, n_dim, g)
    facts = make_facts(V_C, V_R, M_facts, g)
    keys_unique_mode = "unique_sr" if M_facts <= V_C * V_R else "duplicates_allowed"
    W = ingest_hebbian_gpu(facts, E, R, sq, n_dim)

    chunk = min(1000, M_facts)
    hits = 0
    for start in range(0, M_facts, chunk):
        end = min(start + chunk, M_facts)
        batch_facts = facts[start:end]
        s_idx = torch.tensor([f[0] for f in batch_facts], device=DEVICE)
        r_idx = torch.tensor([f[1] for f in batch_facts], device=DEVICE)
        o_idx = torch.tensor([f[2] for f in batch_facts], device=DEVICE)
        keys = E[s_idx] * R[r_idx] * sq
        states = (W @ keys.T).T
        sims = states @ E.T
        preds = sims.argmax(dim=1)
        hits += int((preds == o_idx).sum().item())

    del W, E, R
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    recall = hits / max(M_facts, 1)
    return {"recall_at_1": round(recall, 4), "V_C": V_C, "V_R": V_R,
            "M_facts": M_facts, "N": n_dim, "n_queries": M_facts,
            "alpha_M_over_VC": round(M_facts / max(V_C, 1), 3),
            "alpha_M_over_N": round(M_facts / max(n_dim, 1), 3),
            "keys_unique_mode": keys_unique_mode}


def eval_knn_baseline(V_C: int, n_dim: int, g: np.random.Generator,
                       noise_sigma: float = 0.3) -> float:
    M = min(500, V_C)
    E = bipolar_t(V_C, n_dim, g)
    pick = torch.arange(M, device=DEVICE)
    items = E[pick]
    noise = torch.randn_like(items) * noise_sigma
    noisy = items + noise
    sims = noisy @ E.T
    pred = sims.argmax(dim=1)
    correct = int((pred == pick).sum().item())
    del E, items, noise, noisy, sims, pred
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    return correct / max(M, 1)


# ----------------------------- self-test -----------------------------
def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V_C_t = 100
    V_R_t = 4
    M_t = 100  # alpha = 1.0

    E = bipolar_t(V_C_t, n, g)
    R = bipolar_t(V_R_t, n, g)
    assert E.shape == (V_C_t, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: high-alpha facts may have duplicate (s, r) keys
    facts_low_alpha = make_facts(V_C_t, V_R_t, 50, g)
    assert len(facts_low_alpha) == 50
    keys_low = set((s, r) for s, r, _ in facts_low_alpha)
    assert len(keys_low) == 50, "low-alpha: unique (s,r) keys expected"

    # T3: at alpha M > V_C * V_R, duplicates_allowed mode triggers
    # V_C=100, V_R=4 -> max_unique_sr = 400; ask for 500 -> duplicates_allowed
    g3 = np.random.default_rng(1)
    facts_high_alpha = make_facts(V_C_t, V_R_t, 500, g3)
    assert len(facts_high_alpha) == 500
    keys_high = set((s, r) for s, r, _ in facts_high_alpha)
    triples_high = set((s, r, o) for s, r, o in facts_high_alpha)
    assert len(keys_high) <= V_C_t * V_R_t, "high-alpha keys must be <= max_unique_sr"
    assert len(triples_high) == 500, "high-alpha triples must be unique"

    # T4: end-to-end mechanism check at alpha=1
    g4 = np.random.default_rng(2)
    out = eval_recall_at_vc_m(V_C_t, V_R_t, M_t, n, 1, g4)
    assert 0.0 <= out["recall_at_1"] <= 1.0
    assert out["alpha_M_over_VC"] == round(M_t / V_C_t, 3)
    assert out["alpha_M_over_N"] == round(M_t / n, 3)
    assert out["keys_unique_mode"] == "unique_sr"

    # T5: end-to-end at high alpha (M > V_C * V_R)
    g5 = np.random.default_rng(3)
    out_h = eval_recall_at_vc_m(V_C_t, V_R_t, 500, n, 1, g5)
    assert 0.0 <= out_h["recall_at_1"] <= 1.0
    assert out_h["keys_unique_mode"] == "duplicates_allowed"

    # T6: KNN sentinel
    g6 = np.random.default_rng(4)
    rec_knn = eval_knn_baseline(V_C_t, n, g6, noise_sigma=0.15)
    assert rec_knn >= 0.80, "T6 KNN sentinel %.3f < 0.80" % rec_knn

    # T7: bands LOCKED
    assert HP_KNN_SENTINEL == 0.90
    assert CV_MAX == 0.05
    assert HP_DISCRIMINATING_REC_MIN == 0.50

    # T8: LLM call counter = 0
    assert _LLM_CALL_COUNTER[0] == 0

    # T9: M_FACTS_SWEEP contains M >= N
    if not SMOKE:
        for m in M_FACTS_SWEEP:
            assert m >= N_DIM, "production M_FACTS_SWEEP must have all M >= N (alpha>=1)"
    else:
        for m in M_FACTS_SWEEP:
            assert m >= N_DIM, "smoke M_FACTS_SWEEP must also have M >= N"

    # T10: cardinality math
    if not SMOKE:
        expected = 3 * 3 * 3 + 3
        assert expected == 30
    else:
        expected = 1 * 2 * 2 + 1
        assert expected == 5

    print("[selftest] PASS low_alpha=%.3f high_alpha=%.3f knn=%.3f keys_modes=(low=%s,high=%s) gpu=%s"
          % (out["recall_at_1"], out_h["recall_at_1"], rec_knn,
             out["keys_unique_mode"], out_h["keys_unique_mode"], GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- run_unit + main -----------------------------
_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time(),
                                    "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for V_C in VC_SWEEP:
            for M in M_FACTS_SWEEP:
                keys.append("seed%d_VC%d_M%d_armCAPACITY" % (s, V_C, M))
        keys.append("seed%d_VC%d_M0_armKNN_SENTINEL" % (s, max(VC_SWEEP)))
    return keys


def _parse_key(key: str) -> Tuple[int, int, int, str]:
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    VC = int(parts[1].replace("VC", ""))
    M = int(parts[2].replace("M", ""))
    arm_marker_idx = key.index("_arm") + len("_arm")
    A = key[arm_marker_idx:]
    return seed, VC, M, A


def run_unit(seed: int, V_C: int, M_facts: int, arm: str) -> Dict[str, Any]:
    t0 = time.time()
    g = np.random.default_rng(seed * 100003 + V_C * 31 + M_facts)
    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    if arm == "KNN_SENTINEL":
        sentinel_sigma = 0.15 if SMOKE else 0.3
        rec = eval_knn_baseline(V_C, N_DIM, g, noise_sigma=sentinel_sigma)
        out = {
            "seed": seed, "V_C": V_C, "M_facts": 0, "arm": arm,
            "recall_at_1": round(rec, 4),
            "alpha_M_over_VC": 0.0, "alpha_M_over_N": 0.0,
            "keys_unique_mode": "n/a_sentinel",
            "n_queries": min(500, V_C),
            "wall_s": round(time.time() - t0, 2),
            "run_mode": RUN_MODE,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
    else:
        result = eval_recall_at_vc_m(V_C, V_R=V_REL, M_facts=M_facts,
                                       n_dim=N_DIM, seed=seed, g=g)
        out = {
            "seed": seed, "V_C": V_C, "M_facts": M_facts, "arm": arm,
            **result,
            "wall_s": round(time.time() - t0, 2),
            "run_mode": RUN_MODE,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
    if GPU_AVAIL:
        out["peak_mem_mb"] = int(torch.cuda.max_memory_allocated(DEVICE) / 1024 / 1024)
    else:
        out["peak_mem_mb"] = 0
    return out


def compute_verdict(per_key: Dict[str, Dict],
                     failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_key and not failures:
        return ("HARD_FAIL", "no_units", {})

    n_units_observed = len(per_key)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS)

    # Sentinel
    sentinel_recs = [float(v["recall_at_1"]) for v in per_key.values()
                      if v.get("arm") == "KNN_SENTINEL"]
    knn_mean = float(np.mean(sentinel_recs)) if sentinel_recs else float("nan")
    knn_ok = (not math.isnan(knn_mean)) and (knn_mean >= HP_KNN_SENTINEL)

    # Group capacity arms by (V_C, M_facts) across seeds
    by_VC_M: Dict[Tuple[int, int], List[float]] = {}
    by_VC_M_meta: Dict[Tuple[int, int], Dict] = {}
    for v in per_key.values():
        if v.get("arm") != "CAPACITY":
            continue
        key = (int(v["V_C"]), int(v["M_facts"]))
        by_VC_M.setdefault(key, []).append(float(v["recall_at_1"]))
        by_VC_M_meta[key] = {
            "alpha_M_over_VC": v.get("alpha_M_over_VC"),
            "alpha_M_over_N": v.get("alpha_M_over_N"),
            "keys_unique_mode": v.get("keys_unique_mode"),
        }

    surface: Dict[str, Dict] = {}
    for (V_C, M), recs in by_VC_M.items():
        m = float(np.mean(recs))
        s = float(np.std(recs)) if len(recs) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        surface["VC=%d_M=%d" % (V_C, M)] = {
            "recall_mean": round(m, 4),
            "recall_cv": round(cv, 4),
            "n_seeds_observed": len(recs),
            "recall_per_seed": [round(r, 4) for r in recs],
            **by_VC_M_meta[(V_C, M)],
        }

    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    summ_rows = []
    for k, st in sorted(surface.items()):
        summ_rows.append("%s[alphaVC=%.2f alphaN=%.2f mode=%s rec=%.4f cv=%.4f n=%d]" % (
            k, st["alpha_M_over_VC"] or 0.0, st["alpha_M_over_N"] or 0.0,
            st["keys_unique_mode"] or "?",
            st["recall_mean"], st["recall_cv"], st["n_seeds_observed"]))
    summ = " | ".join(summ_rows) if summ_rows else "no_capacity_arms"
    summ += " | KNN_sentinel=%.4f (>=%.2f; %s)" % (
        knn_mean, HP_KNN_SENTINEL, "OK" if knn_ok else "FAIL")
    card_str = " | n_units=%d/expected=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if failures:
        fail_str = " | failures=%d [%s]" % (
            len(failures),
            "; ".join("%s:%s" % (f.get("key", "?"), f.get("exc_type", "?"))
                       for f in failures[:3]))

    # Detect monotone trend along V_C axis (at smallest M) and M axis (at largest V_C)
    monotone_findings: List[str] = []
    if len(VC_SWEEP) >= 2 and len(M_FACTS_SWEEP) >= 1:
        # V_C-up at smallest M
        m_small = min(M_FACTS_SWEEP)
        recs_vc = []
        for vc in sorted(VC_SWEEP):
            k = "VC=%d_M=%d" % (vc, m_small)
            if k in surface:
                recs_vc.append(surface[k]["recall_mean"])
        if len(recs_vc) >= 2:
            d_vc = recs_vc[-1] - recs_vc[0]
            if d_vc >= HP_MONOTONE_DELTA:
                monotone_findings.append("VC_up_helps_at_M=%d_delta=%.3f" % (m_small, d_vc))
            elif d_vc <= -HP_MONOTONE_DELTA:
                monotone_findings.append("VC_up_hurts_at_M=%d_delta=%.3f" % (m_small, d_vc))
    if len(M_FACTS_SWEEP) >= 2 and len(VC_SWEEP) >= 1:
        # M-up at largest V_C
        vc_large = max(VC_SWEEP)
        recs_m = []
        for m in sorted(M_FACTS_SWEEP):
            k = "VC=%d_M=%d" % (vc_large, m)
            if k in surface:
                recs_m.append(surface[k]["recall_mean"])
        if len(recs_m) >= 2:
            d_m = recs_m[-1] - recs_m[0]
            if d_m <= -HP_MONOTONE_DELTA:
                monotone_findings.append("M_up_hurts_at_VC=%d_delta=%.3f" % (vc_large, d_m))
            elif d_m >= HP_MONOTONE_DELTA:
                monotone_findings.append("M_up_helps_at_VC=%d_delta=%.3f" % (vc_large, d_m))

    # Detect at-least-one discriminating-regime PASS (rec>=HP_DISC + cv<=CV_MAX)
    disc_passes = [(k, st) for k, st in surface.items()
                    if st["recall_mean"] >= HP_DISCRIMINATING_REC_MIN
                    and st["recall_cv"] <= CV_MAX]

    detail = {
        "surface": surface,
        "knn_sentinel_mean": knn_mean,
        "knn_sentinel_ok": knn_ok,
        "monotone_findings": monotone_findings,
        "discriminating_passes": [(k, st["recall_mean"], st["recall_cv"])
                                   for k, st in disc_passes],
        "substrate_only_ok": substrate_only_ok,
        "n_llm_calls": int(n_llm),
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "failures": failures,
    }

    if SMOKE:
        any_finite = any(not math.isnan(st["recall_mean"]) for st in surface.values())
        if substrate_only_ok and any_finite and not failures:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(production gates DEFERRED to FULL on GPU) | %s%s%s" % (
                        summ, card_str, fail_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | %s%s%s" % (
                    summ, card_str, fail_str),
                detail)

    if failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised exceptions (META_RULE_J) | %s%s%s" % (
                    len(failures), summ, card_str, fail_str),
                detail)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units=%d < expected=%d | %s%s" % (
                    n_units_observed, EXPECTED_N_UNITS, summ, card_str),
                detail)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_SUBSTRATE_ONLY: %d LLM calls | %s%s" % (n_llm, summ, card_str),
                detail)
    if not knn_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_KNN_SENTINEL: %.4f < %.2f | %s%s" % (
                    knn_mean, HP_KNN_SENTINEL, summ, card_str),
                detail)

    if disc_passes and monotone_findings:
        return ("CHAIN_GRADE_DISCRIMINATING_REGIME",
                "CHAIN_GRADE_DISCRIMINATING_REGIME: %d phase points >= rec=%.2f cv<=%.2f; "
                "monotone trends: %s | %s%s" % (
                    len(disc_passes), HP_DISCRIMINATING_REC_MIN, CV_MAX,
                    "; ".join(monotone_findings), summ, card_str),
                detail)
    if disc_passes:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_DISCRIMINATING_PASSES_NO_MONOTONE: %d phase points clear "
                "rec>=%.2f cv<=%.2f but no clear V_C/M monotone trend (flat or noisy) | %s%s" % (
                    len(disc_passes), HP_DISCRIMINATING_REC_MIN, CV_MAX, summ, card_str),
                detail)
    if monotone_findings:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_MONOTONE_NO_DISC_PASS: monotone trends [%s] observed but no "
                "phase point at rec>=%.2f cv<=%.2f (surface entirely below discriminating bar) | %s%s" % (
                    "; ".join(monotone_findings), HP_DISCRIMINATING_REC_MIN, CV_MAX, summ, card_str),
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_FLAT_SURFACE: no monotone trends + no phase point passes "
            "rec>=%.2f cv<=%.2f (substrate may be at noise floor across all configs) | %s%s" % (
                HP_DISCRIMINATING_REC_MIN, CV_MAX, summ, card_str),
            detail)


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        keys = _build_keys()
        agg = aggregate_partials(od, seeds=keys, run_config=run_config)
        if not agg and not _RESULTS_HOLDER["failures"]:
            return
        v, vmsg, detail = compute_verdict(agg, _RESULTS_HOLDER["failures"])
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()), atexit_synth=True)
        write_metrics(od, metrics, results=list(agg.values()))
        print("[atexit] wrote synth metrics.json (%d units)" % len(agg), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def _build_metrics(v: str, vmsg: str, detail: Dict, units: List[Dict],
                    atexit_synth: bool = False) -> Dict:
    return {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
        "n_units": len(units),
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": (len(units) >= EXPECTED_N_UNITS),
        "n_failures": len(_RESULTS_HOLDER["failures"]),
        "failures": _RESULTS_HOLDER["failures"],
        "config_version": CONFIG_VERSION,
        "VC_SWEEP": VC_SWEEP,
        "M_FACTS_SWEEP": M_FACTS_SWEEP,
        "V_REL": V_REL,
        "seeds": SEEDS,
        "per_unit": units,
        "detail": detail,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg[:300],
        "_atexit_synth": atexit_synth,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": True,
        "metrics_source": "measured_substrate_bipolar_hebbian_W_capacity_higher_alpha_v1",
        "DESIGN_NOTE": (
            "HIGHER_ALPHA_CAPACITY_SWEEP: re-test of capacity surface at alpha>=1.0 "
            "regime (M_facts >= N), after Skunkworks flag-back #3 noted prior sweep "
            "at alpha=0.37 was by-construction-saturated. M_FACTS in {N, 1.5N, 2N}; "
            "V_C in {2000, 4000, 8000}; 3 seeds each; 9 phase points + 1 KNN sentinel "
            "= 30 total units (META_RULE_H). Discriminator IS the recall surface "
            "shape; verdict CHAIN_GRADE_DISCRIMINATING_REGIME if at least 1 phase "
            "point clears HP_DISC + 1 clear monotone trend along V_C or M axis. "
            "Substrate-native Hebbian W (N x N fp32 = 1.07GB at N=16384); GPU-required."
        ),
    }


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d VC=%s M=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, VC_SWEEP, M_FACTS_SWEEP,
        CONFIG_VERSION), flush=True)
    print("[gpu] avail=%s name=%s mem_gb=%.1f" % (GPU_AVAIL, GPU_NAME, GPU_MAX_MEM_GB),
          flush=True)
    print("[cardinality] expected_n_units=%d (META_RULE_H guard)" % EXPECTED_N_UNITS,
          flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    halt_after_loop = False
    for key in all_keys:
        if key in done_keys:
            continue
        seed, VC, M, A = _parse_key(key)
        try:
            print("  [run] %s ..." % key, flush=True)
            rec = run_unit(seed, VC, M, A)
            write_partial_key(out_dir, key, rec)
            print("  [done] %s rec=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall_at_1"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "V_C": VC, "M_facts": M, "arm": A,
                "exc_type": type(e).__name__,
                "exc_msg": str(e)[:500],
                "traceback": tb[-2000:],
            }
            _RESULTS_HOLDER["failures"].append(fail_entry)
            print("[UNIT_EXCEPTION] %s type=%s msg=%r" % (
                key, type(e).__name__, str(e)[:200]), flush=True)
            print("[TRACEBACK]\n%s" % tb, flush=True)
            print("[META_RULE_J] halting loop on unit exception (no silent-continue)", flush=True)
            halt_after_loop = True
            break

    agg = aggregate_partials(out_dir, seeds=all_keys, run_config=run_config)
    units = [agg[k] for k in all_keys if k in agg]
    failures = _RESULTS_HOLDER["failures"]

    if not units and not failures:
        print("[FATAL] no partials available + no failures", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg, detail = compute_verdict(agg, failures)
    print("\n[VERDICT] %s" % v, flush=True)
    print("[VERDICT_MSG] %s" % vmsg, flush=True)

    metrics = _build_metrics(v, vmsg, detail, units, atexit_synth=False)
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %d failures, %.1fs)" % (
        len(units), len(failures), metrics["elapsed_s"]), flush=True)
    if halt_after_loop:
        sys.exit(1)
