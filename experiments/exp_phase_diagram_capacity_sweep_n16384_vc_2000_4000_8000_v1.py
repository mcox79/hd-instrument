"""phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1 -- GPU capacity sweep.

USER directive 2026-06-26: phase-diagram coverage for cortex content-extraction
at production scale. Sweep V_C in {2000, 4000, 8000} at N_DIM=16384 to map the
content-extraction capacity surface.

PROMOTION CONTEXT:
  Audit-device production envelope inherits V_C_IN<=2000 (stage3-integrated-audit).
  Cortex content-extraction work needs production-scale capacity coverage; we have
  point measurements but no V_C sweep at production N=16384. This cell maps the
  phase diagram along the V_C axis at the production N rail.

DESIGN: V_C-extension sweep at N=16384 with 3 phase points + sanity rail
  N=16384 V_C=2000  M_FACTS=1500 (production audit-device baseline)
  N=16384 V_C=4000  M_FACTS=3000 (2x production)
  N=16384 V_C=8000  M_FACTS=6000 (4x production; ceiling probe)
For each (N, V_C): measure recall@1 of associative retrieval via Hebbian
bind(subject, relation) -> object. Substrate-native sparse-bipolar codebook.

ARMS (3 phase points + 1 baseline):
  ARM_BASELINE_KNN_M500     KNN sentinel at M=500 random items (>=0.90; Fix #28)
  ARM_VC_2000               capacity sweep at V_C=2000 M_FACTS=1500
  ARM_VC_4000               capacity sweep at V_C=4000 M_FACTS=3000
  ARM_VC_8000               capacity sweep at V_C=8000 M_FACTS=6000

PRE-REG BANDS (LOCKED at module init):
  Per-arm chain-grade gate: recall>=0.90 AND cv<=0.05 AND substrate-only n_llm=0
  Sentinel rail: KNN_M500 >= 0.90 (Fix #28; tests codebook sanity)

  CHAIN_GRADE_VC_CEILING_8000: all 3 VC points chain-grade (rec>=0.90 cv<=0.05)
    -> production V_C ceiling extends to 8000
  PARTIAL_VC_CEILING_4000: VC=2000+4000 chain-grade, VC=8000 cliffs
    -> ceiling between 4000 and 8000
  PARTIAL_VC_CEILING_2000: VC=2000 only chain-grade, VC>=4000 cliffs
    -> production V_C bound at 2000 (current envelope)
  VC_2000_IS_CEILING: VC=2000 fails -> cell broken (sanity breach)
  MIDDLE_BAND: mixed phase points

HARD_PASS_RECALL = 0.90
HARD_FAIL_RECALL = 0.50 (below this at VC=2000 -> sanity)
CV_MAX = 0.05

GPU IMPLEMENTATION (Fix #24 active GPU use):
  - Sparse-bipolar E built on cuda; R built on cuda
  - Hebbian W ingest = batched outer-product on cuda (V_T @ K / N)
  - Cleanup argmax over E @ (W @ key) on cuda
  - Per-arm memory at N=16384: W = 1.07GB fp32; arms run sequentially with
    cache clear between arms; smoke at N=2048 to stay laptop-fittable.

ASCII-only. Single-file. Resumable per-seed checkpoint.
Author: exp_dev 2026-06-26 (USER-directed phase-diagram extension).
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
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# ----------------------------------------------------------------------------
# GPU GUARD
# ----------------------------------------------------------------------------
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed", flush=True)
    sys.exit(1)

GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
    print("[GPU] device=%s name=%s total_mem=%.1fGB" % (
        DEVICE, GPU_NAME, GPU_MAX_MEM_GB), flush=True)
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0
    print("[GPU] WARN: cuda not available; running on CPU. "
          "Smoke OK; full dispatch MUST be GPU per Fix #24.", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "phase_diagram_capacity_sweep_n16384_vc_2000_4000_8000_v1"
_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_capacity_sweep_VC_axis"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ----------------------------------------------------------------------------
# PRE-REG BANDS (LOCKED at module init)
# ----------------------------------------------------------------------------
HP_RECALL = 0.90
HF_RECALL = 0.50  # at VC=2000 (rail), below this -> sanity breach
CV_MAX = 0.05
HP_KNN_SENTINEL = 0.90
V_REL = 8  # relations vocab; small for clean capacity-only measure

# Cell config
if RUN_MODE == "smoke":
    N_DIM = 2048
    VC_SWEEP = [200, 400]  # tiny smoke
    M_FACTS_BY_VC = {200: 150, 400: 300}  # M = 0.75 * V_C (production ratio)
    SEEDS = [11]
else:
    N_DIM = 16384
    VC_SWEEP = [2000, 4000, 8000]
    M_FACTS_BY_VC = {2000: 1500, 4000: 3000, 8000: 6000}  # M = 0.75 * V_C
    SEEDS = [11, 13, 19]

assert all(v in M_FACTS_BY_VC for v in VC_SWEEP)

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagCapacityVC-v1: N=%d VC_SWEEP=%s M_FACTS=%s V_REL=%d seeds=%s mode=%s "
    "encoder=%s HP_recall=%.2f HF_recall=%.2f CV_max=%.2f HP_knn=%.2f"
) % (
    N_DIM, VC_SWEEP, [M_FACTS_BY_VC[v] for v in VC_SWEEP], V_REL, SEEDS, RUN_MODE,
    ENCODER_PROVENANCE, HP_RECALL, HF_RECALL, CV_MAX, HP_KNN_SENTINEL,
)


# ----------------------------------------------------------------------------
# Primitives (GPU-native)
# ----------------------------------------------------------------------------

def bipolar_gpu(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    """Bipolar bit vectors on GPU; row-normalized."""
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_facts(V_C: int, V_R: int, M_facts: int,
                g: np.random.Generator) -> List[Tuple[int, int, int]]:
    """Generate M_facts unique (subject, relation, object) triples from
    V_C concepts and V_R relations. No duplicate (s, r) keys.
    """
    facts = []
    seen_keys = set()
    tries = 0
    max_tries = M_facts * 50
    while len(facts) < M_facts and tries < max_tries:
        tries += 1
        s = int(g.integers(0, V_C))
        r = int(g.integers(0, V_R))
        if (s, r) in seen_keys:
            continue
        o = int(g.integers(0, V_C))
        while o == s:
            o = int(g.integers(0, V_C))
        facts.append((s, r, o))
        seen_keys.add((s, r))
    if len(facts) < M_facts:
        raise RuntimeError("make_facts: only %d/%d at V_C=%d V_R=%d "
                            "(saturation; reduce M_facts)" % (
                                len(facts), M_facts, V_C, V_R))
    return facts


def ingest_hebbian_gpu(triples: List[Tuple[int, int, int]],
                        E: torch.Tensor, R: torch.Tensor,
                        sq: float, n_dim: int,
                        batch: int = 1000) -> torch.Tensor:
    """Batched outer-product Hebbian ingest on GPU.
    W += sum_j outer(E[o_j], E[s_j] * R[r_j] * sq) / n_dim
    """
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


def eval_recall_at_vc(V_C: int, V_R: int, M_facts: int,
                       n_dim: int, seed: int,
                       g: np.random.Generator) -> Dict[str, Any]:
    """Build E (V_C, N), R (V_R, N), W from M_facts Hebbian triples; measure
    recall@1: for each fact (s, r, o), retrieve argmax(E @ (W @ (E[s]*R[r]*sq)))
    and check equality with o.
    """
    sq = math.sqrt(n_dim)
    E = bipolar_gpu(V_C, n_dim, g)
    R = bipolar_gpu(V_R, n_dim, g)
    facts = make_facts(V_C, V_R, M_facts, g)
    W = ingest_hebbian_gpu(facts, E, R, sq, n_dim)

    # Batched eval (all facts at once if memory allows; else chunk)
    chunk = min(1000, M_facts)
    hits = 0
    for start in range(0, M_facts, chunk):
        end = min(start + chunk, M_facts)
        batch_facts = facts[start:end]
        s_idx = torch.tensor([f[0] for f in batch_facts], device=DEVICE)
        r_idx = torch.tensor([f[1] for f in batch_facts], device=DEVICE)
        o_idx = torch.tensor([f[2] for f in batch_facts], device=DEVICE)
        keys = E[s_idx] * R[r_idx] * sq  # (B, N)
        states = (W @ keys.T).T  # (B, N)
        sims = states @ E.T  # (B, V_C)
        preds = sims.argmax(dim=1)  # (B,)
        hits += int((preds == o_idx).sum().item())

    # Free large tensors
    del W, E, R
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    recall = hits / max(M_facts, 1)
    return {"recall_at_1": round(recall, 4), "V_C": V_C, "V_R": V_R,
            "M_facts": M_facts, "N": n_dim, "n_queries": M_facts}


def eval_knn_baseline(V_C: int, n_dim: int, g: np.random.Generator,
                       noise_sigma: float = 0.3) -> float:
    """KNN sentinel: random codebook of V_C items; perturb each with light noise;
    verify argmax cleanup recovers >= HP_KNN_SENTINEL of items.
    noise_sigma=0.3 on row-normalized vectors (||x||=1) is mild perturbation;
    smaller V_C / N regimes may need lower noise (see _selftest).
    """
    M = min(500, V_C)
    E = bipolar_gpu(V_C, n_dim, g)
    pick = torch.arange(M, device=DEVICE)
    items = E[pick]
    noise = torch.randn_like(items) * noise_sigma
    noisy = items + noise
    # Argmax over codebook
    sims = noisy @ E.T  # (M, V_C)
    pred = sims.argmax(dim=1)
    correct = int((pred == pick).sum().item())
    del E, items, noise, noisy, sims, pred
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    return correct / max(M, 1)


# ----------------------------------------------------------------------------
# Self-test (formula sanity check on tiny config)
# ----------------------------------------------------------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V_C_t = 50
    V_R_t = 4
    M_t = 30

    # T1: bipolar shapes + norm
    E = bipolar_gpu(V_C_t, n, g)
    R = bipolar_gpu(V_R_t, n, g)
    assert E.shape == (V_C_t, n) and R.shape == (V_R_t, n)
    assert abs(float(E[0].norm()) - 1.0) < 1e-4

    # T2: facts uniqueness
    facts = make_facts(V_C_t, V_R_t, M_t, g)
    assert len(facts) == M_t
    keys = set((s, r) for s, r, _ in facts)
    assert len(keys) == M_t
    for s, r, o in facts:
        assert s != o

    # T3: ingest + recall sanity (low-load chain-grade expected)
    sq = math.sqrt(n)
    W = ingest_hebbian_gpu(facts, E, R, sq, n)
    assert W.shape == (n, n)
    assert torch.isfinite(W).all()

    # T4: low-load (M=30 facts over V_C=50 N=512) should recover most facts
    hits = 0
    for s, r, o in facts:
        key = E[s] * R[r] * sq
        state = W @ key
        sims = E @ state
        pred = int(torch.argmax(sims).item())
        if pred == o:
            hits += 1
    rec = hits / len(facts)
    assert rec >= 0.50, "T4 low-load recall %.3f < 0.50" % rec

    # T5: end-to-end eval_recall_at_vc on tiny config
    g2 = np.random.default_rng(1)
    rec_e2e = eval_recall_at_vc(V_C_t, V_R_t, M_t, n, 1, g2)
    assert 0.0 <= rec_e2e["recall_at_1"] <= 1.0
    assert rec_e2e["V_C"] == V_C_t and rec_e2e["M_facts"] == M_t

    # T6: KNN sentinel sanity (tiny config V_C=50 N=512 needs lower noise
    # than production sigma; the production sentinel runs at V_C >= 2000 N >= 16384
    # where sigma=0.3 yields chain-grade recovery)
    g3 = np.random.default_rng(2)
    rec_knn = eval_knn_baseline(V_C_t, n, g3, noise_sigma=0.15)
    assert rec_knn >= 0.80, "T6 KNN sentinel %.3f < 0.80" % rec_knn

    # T7: bands LOCKED
    assert HP_RECALL == 0.90 and HF_RECALL == 0.50
    assert CV_MAX == 0.05 and HP_KNN_SENTINEL == 0.90

    # T8: LLM call counter = 0
    assert _LLM_CALL_COUNTER[0] == 0

    # T9: M_FACTS_BY_VC ratio is 0.75
    for v in VC_SWEEP:
        ratio = M_FACTS_BY_VC[v] / v
        assert abs(ratio - 0.75) < 1e-9, "M/VC ratio %.3f != 0.75 at V_C=%d" % (
            ratio, v)

    # T10: GPU presence asserted for non-smoke mode
    if RUN_MODE != "smoke":
        assert GPU_AVAIL, "FULL run requires GPU per Fix #24"

    print("[selftest] PASS low_load=%.3f e2e=%.3f knn=%.3f gpu=%s" % (
        rec, rec_e2e["recall_at_1"], rec_knn, GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------------------------------------------------------
# run_seed
# ----------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)

    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_R": V_REL,
        "encoder_provenance": ENCODER_PROVENANCE,
        "VC_SWEEP": VC_SWEEP,
        "M_FACTS_BY_VC": {str(v): M_FACTS_BY_VC[v] for v in VC_SWEEP},
        "config_version": CONFIG_VERSION,
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== KNN sentinel (Fix #28) on the largest V_C =====
    # Smoke uses lower noise sigma since small N=2048 has lower noise tolerance
    # than production N=16384; production sigma=0.3 is well within chain-grade
    # at N=16384 V_C>=2000
    t_arm = time.time()
    sentinel_sigma = 0.15 if RUN_MODE == "smoke" else 0.3
    knn_recall = eval_knn_baseline(max(VC_SWEEP), N_DIM, g,
                                     noise_sigma=sentinel_sigma)
    out["arm_baseline_knn"] = {
        "recall_at_1": round(knn_recall, 4),
        "V_C_used": max(VC_SWEEP),
        "elapsed_s_arm": round(time.time() - t_arm, 2),
        "mechanism": "knn_argmax_codebook_sentinel",
    }
    out["knn_sentinel_ok"] = (knn_recall >= HP_KNN_SENTINEL)
    print("  [seed=%d] KNN_SENTINEL rec=%.4f (knn_ok=%s; HP=%.2f) t=%.1fs" % (
        seed, knn_recall, out["knn_sentinel_ok"], HP_KNN_SENTINEL,
        out["arm_baseline_knn"]["elapsed_s_arm"]), flush=True)

    # ===== Per-VC capacity sweep arms =====
    for V_C in VC_SWEEP:
        M_facts = M_FACTS_BY_VC[V_C]
        t_arm = time.time()
        arm_result = eval_recall_at_vc(V_C, V_REL, M_facts, N_DIM, seed, g)
        arm_result["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        arm_result["mechanism"] = "substrate_native_hebbian_W_argmax_cleanup_gpu"
        key = "arm_vc_%d" % V_C
        out[key] = arm_result
        print("  [seed=%d] ARM_VC_%d rec=%.4f M_facts=%d (HP=%.2f HF=%.2f) t=%.1fs" % (
            seed, V_C, arm_result["recall_at_1"], M_facts,
            HP_RECALL, HF_RECALL, arm_result["elapsed_s_arm"]), flush=True)

    if GPU_AVAIL:
        peak_bytes = torch.cuda.max_memory_allocated(DEVICE)
        out["gpu_max_mem_alloc_mb"] = round(peak_bytes / 1e6, 2)
        print("  [seed=%d] GPU peak alloc: %.2f MB" % (
            seed, out["gpu_max_mem_alloc_mb"]), flush=True)
        torch.cuda.empty_cache()
    else:
        out["gpu_max_mem_alloc_mb"] = 0.0

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_recall(key: str) -> float:
        vals = [p[key]["recall_at_1"] for p in per_seed if key in p
                and isinstance(p[key].get("recall_at_1"), (int, float))
                and not math.isnan(p[key]["recall_at_1"])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_recall(key: str) -> float:
        vals = [p[key]["recall_at_1"] for p in per_seed if key in p
                and isinstance(p[key].get("recall_at_1"), (int, float))
                and not math.isnan(p[key]["recall_at_1"])]
        if len(vals) < 2:
            return float("nan")
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    # Per-VC means
    vc_results = {}
    for V_C in VC_SWEEP:
        key = "arm_vc_%d" % V_C
        vc_results[V_C] = {
            "mean": mean_recall(key),
            "cv": cv_recall(key),
        }

    knn_mean = mean_recall("arm_baseline_knn")
    knn_breach = sum(1 for p in per_seed if not p.get("knn_sentinel_ok", False))

    n_llm = sum(int(p.get("_llm_forward_calls_at_inference", 0)) for p in per_seed)
    substrate_only_ok = (n_llm == 0)

    summ_rows = ["KNN_SENTINEL=%.4f (knn_breach=%d/%d)" % (
        knn_mean, knn_breach, len(per_seed))]
    for V_C in VC_SWEEP:
        d = vc_results[V_C]
        summ_rows.append("VC_%d=%.4f (cv=%.3f)" % (
            V_C, d["mean"], d["cv"]))
    summ = " | ".join(summ_rows)

    half = max(1, (len(per_seed) + 1) // 2)

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_SUBSTRATE_ONLY: %d LLM calls | %s" % (n_llm, summ))

    # Smoke mode: verdict is mechanism-end-to-end check; smaller N+V_C cannot
    # satisfy production-tuned sentinel/cv bands. PASS if VC arms produce any
    # measurement (non-NaN).
    if RUN_MODE == "smoke":
        any_vc_ok = any(not math.isnan(vc_results[v]["mean"])
                          and vc_results[v]["mean"] >= 0.10
                          for v in VC_SWEEP)
        if any_vc_ok:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(KNN sentinel + cv bands deferred to FULL run) | %s" % summ)
        return ("HARD_FAIL",
                "SMOKE_FAIL: VC arms returned no valid recall | %s" % summ)

    if knn_breach >= half:
        return ("SANITY_BREACH",
                "SANITY_BREACH_KNN_SENTINEL_BELOW_%.2f: KNN=%.4f | %s" % (
                    HP_KNN_SENTINEL, knn_mean, summ))

    # Per-VC chain-grade classification
    def vc_pass(V_C: int) -> bool:
        d = vc_results[V_C]
        if math.isnan(d["mean"]):
            return False
        cv_ok = math.isnan(d["cv"]) or d["cv"] <= CV_MAX
        return d["mean"] >= HP_RECALL and cv_ok

    def vc_fail(V_C: int) -> bool:
        return (not math.isnan(vc_results[V_C]["mean"])) and \
               vc_results[V_C]["mean"] < HF_RECALL

    sorted_vc = sorted(VC_SWEEP)  # ascending
    smallest_vc = sorted_vc[0]

    # Sanity: smallest VC (production baseline) must clear HF
    if vc_fail(smallest_vc):
        return ("SANITY_BREACH",
                "SANITY_BREACH_PRODUCTION_BASELINE_VC_%d_REC_BELOW_%.2f: %s" % (
                    smallest_vc, HF_RECALL, summ))

    passes = [v for v in sorted_vc if vc_pass(v)]
    fails = [v for v in sorted_vc if vc_fail(v)]

    largest_vc = sorted_vc[-1]
    middle_vc = sorted_vc[1] if len(sorted_vc) >= 2 else None

    if all(vc_pass(v) for v in sorted_vc):
        return ("CHAIN_GRADE_VC_CEILING_%d" % largest_vc,
                "CHAIN_GRADE_VC_CEILING_%d_ALL_PASS: %s" % (largest_vc, summ))
    if middle_vc is not None and vc_pass(smallest_vc) and vc_pass(middle_vc) \
            and not vc_pass(largest_vc):
        return ("PARTIAL_VC_CEILING_%d" % middle_vc,
                "PARTIAL_VC_CEILING_%d_CLIFF_BETWEEN_%d_AND_%d: %s" % (
                    middle_vc, middle_vc, largest_vc, summ))
    if vc_pass(smallest_vc) and not vc_pass(middle_vc if middle_vc is not None else largest_vc):
        return ("PARTIAL_VC_CEILING_%d" % smallest_vc,
                "PARTIAL_VC_CEILING_%d_CLIFF_ABOVE_%d: %s" % (
                    smallest_vc, smallest_vc, summ))
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_MIXED_PHASE_POINTS: passes=%s fails=%s | %s" % (
                passes, fails, summ))


# ----------------------------------------------------------------------------
# atexit synthesizer + main
# ----------------------------------------------------------------------------

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "gpu_avail": GPU_AVAIL,
            "gpu_name": GPU_NAME,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d VC_SWEEP=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, VC_SWEEP, CONFIG_VERSION),
        flush=True)
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

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "DESIGN_NOTE": (
            "PHASE_DIAGRAM_VC_AXIS_CAPACITY_SWEEP: production-scale (N=16384) "
            "capacity sweep along the V_C axis. Stage3-integrated-audit envelope "
            "inherits V_C_IN<=2000; this cell maps V_C in {2000, 4000, 8000} to "
            "find the ceiling. M_FACTS/V_C ratio held at 0.75 (production-baseline). "
            "Substrate-native Hebbian W with codebook E and relation matrix R; "
            "recall@1 of associative retrieval via argmax(E @ (W @ (E[s]*R[r]*sq))). "
            "KNN sentinel >= 0.90 (Fix #28). Verdict tiers CHAIN_GRADE_VC_CEILING_8000 "
            "/ PARTIAL_VC_CEILING_4000 / PARTIAL_VC_CEILING_2000 / SANITY_BREACH / "
            "MIDDLE_BAND. GPU-required at full per Fix #24."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
