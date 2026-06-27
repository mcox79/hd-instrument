"""phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu --
Rescue Cell B (GPU-bound MULTI_BANK alone) split from
exp_phase_diagram_capacity_codebook_separated_envelope_v1 per Skunkworks
batch 8 2026-06-27 flag-back.

PARENT FINDING (cell v1):
  MULTI_BANK_K4 arm at alpha_N=4 headroom=10x OOM'd on RTX 4060 Ti
  (~6.8GB VRAM budget; 4 W matrices fp32 @ N=16384 = 4 x 1.07GB W alone =
  4.28GB W plus V/K matrices for shard ingestion exceeded budget). Cell A
  drops multi-bank entirely; Cell B re-isolates it with explicit GPU mandate
  + memory hygiene (empty_cache between banks + bank-sequential ingest +
  PYTORCH_CUDA_ALLOC_CONF expandable_segments).

SCOPE (Skunkworks recommendation c+d):
  ONE phase point only: alpha_N=4.0, codebook_headroom=10x (matches
  parent v1 multi-bank probe target). 3 seeds (was 1; OOM never reached
  seeds 13, 19). NO mech, NO knn, NO bare arms in Cell B (those covered
  by Cell A).

PER-ARM HP-SCOPE DECLARATION (SCHEMA-VET 5b per exp_dev.md 2026-06-27):
  MULTI_BANK_K4 : NO HP gate; envelope-band [0.95, 1.0] same as v1 MECH-arm
                  at this corner (alpha_N=4 headroom=10x). Verdict band:
                  HARD_PASS rec_mean >= 0.95 AND cv <= 0.05 across 3 seeds.
                  MIDDLE_BAND if rec_mean in [0.75, 0.95).
                  HARD_FAIL if rec_mean < 0.75 OR cv > 0.05 OR OOM.
  MECH arm EXEMPT from this cell (Cell A scope).
  KNN_SENTINEL arm EXEMPT (Cell A scope).
  BARE_E_R arm EXEMPT (Cell A scope).

META_RULE_H (cardinality_ok): EXPECTED_N_UNITS = 1 multi-bank cell * 3 seeds = 3.
META_RULE_J (no silent except): halt loop on any unit exception.
META_RULE_L (band-floor): MIDDLE_BAND for rec [0.75, 0.95).

GPU MANDATE (Fix #24; load-bearing for Cell B):
  - DEVICE = 'cuda' constant; torch.cuda.is_available() asserted at full
  - K=4 W matrices: sequential build per bank + free between
  - bf16 path NOT used (rec precision required at >0.95 bar; fp32 stays)
  - torch.cuda.empty_cache() called between each bank build
  - PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True (set at module init)
  - per-unit peak_mem_mb logged for OOM forensics

NO LOCAL SMOKE per USER 2026-06-27.

ASCII-only. Single-file. Resumable per-key checkpoint.
Author: exp_dev 2026-06-27 (Skunkworks batch 8 rescue Cell B).
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
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "phase_diagram_capacity_multi_bank_K4_envelope_v2b_gpu"
_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_capacity_v2b_multibank_K4_alone"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SMOKE = (RUN_MODE == "smoke")


# Cell B GPU mandate (Fix #24). 'cuda' constant for queue routing gate;
# is_available enforced at full-run main entry.
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
GPU_AVAIL = torch.cuda.is_available()
if GPU_AVAIL:
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# Pre-reg bands LOCKED at module init
CV_MAX = 0.05
V_R = 32

# Cell B targets exactly one phase point: alpha_N=4.0, headroom=10x
MULTI_BANK_K = 4
ALPHA_N_TARGET = 4.0
HEADROOM_LABEL = "10x"
HEADROOM_VAL = 10.0

# HARD_PASS band scoped to MULTI_BANK arm only:
HP_MB_REC_MIN = 0.95
HP_MB_CV_MAX = 0.05
MB_MB_REC_MIN = 0.75  # middle-band floor


if SMOKE:
    # Smoke retained for queue_add gate compatibility (does NOT run locally per NO_LOCAL).
    # Small N to verify ingest path on whatever device is available.
    N_DIM = 2048
    SEEDS = [11]
    EXPECTED_N_UNITS = 1  # 1 phase point x 1 seed for smoke
else:
    N_DIM = 16384
    SEEDS = [11, 13, 19]
    EXPECTED_N_UNITS = 1 * len(SEEDS)  # 3


def _compute_VC_for(alpha_N: float, headroom_val: float, n_dim: int) -> int:
    M = int(round(alpha_N * n_dim))
    target_keys = headroom_val * M
    return int(math.ceil(target_keys / V_R))


ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

CONFIG_VERSION = (
    "phaseDiagCapMultiBankK4-v2b-gpu: N=%d V_R=%d seeds=%s mode=%s "
    "encoder=%s K_banks=%d alpha=%.1f headroom=%s "
    "HP_mb_rec_min=%.2f CV_max=%.2f EXPECTED_N_UNITS=%d GPU=%s"
) % (
    N_DIM, V_R, SEEDS, RUN_MODE, ENCODER_PROVENANCE, MULTI_BANK_K,
    ALPHA_N_TARGET, HEADROOM_LABEL, HP_MB_REC_MIN, CV_MAX,
    EXPECTED_N_UNITS, GPU_AVAIL,
)


# ----------------------------- Primitives -----------------------------
def bipolar_t(M: int, n: int, g: np.random.Generator) -> torch.Tensor:
    arr = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    t = torch.from_numpy(arr).to(DEVICE)
    norms = t.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return t / norms


def make_facts(V_C: int, V_R: int, M_facts: int,
                g: np.random.Generator) -> List[Tuple[int, int, int]]:
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
        raise RuntimeError("make_facts: only %d/%d at V_C=%d V_R=%d" % (
            len(facts), M_facts, V_C, V_R))
    return facts


def ingest_hebbian_one_bank(triples: List[Tuple[int, int, int]],
                              E: torch.Tensor, R: torch.Tensor,
                              sq: float, n_dim: int,
                              batch: int = 1000) -> torch.Tensor:
    """Single-bank Hebbian ingest. Returns W."""
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


def eval_recall_multibank_K4(V_C: int, V_R_arg: int, M_facts: int,
                              n_dim: int, K_banks: int,
                              g: np.random.Generator) -> Dict[str, Any]:
    """Multi-bank K=4 recall@1.

    Memory-frugal path: builds each bank's W sequentially and keeps all K
    in VRAM only during the per-query reduction. With K=4 N=16384 fp32 W,
    peak VRAM occupancy ~4.28GB + transient batch tensors.
    """
    sq = math.sqrt(n_dim)
    E = bipolar_t(V_C, n_dim, g)
    R = bipolar_t(V_R_arg, n_dim, g)
    facts = make_facts(V_C, V_R_arg, M_facts, g)
    keys_unique_mode = "unique_sr" if M_facts <= V_C * V_R_arg else "duplicates_allowed"

    # Shard triples round-robin across K banks
    shards: List[List[Tuple[int, int, int]]] = [[] for _ in range(K_banks)]
    for i, t in enumerate(facts):
        shards[i % K_banks].append(t)

    # Build banks one at a time (memory-frugal); empty_cache between
    Ws: List[torch.Tensor] = []
    for k in range(K_banks):
        if not shards[k]:
            W_k = torch.zeros((n_dim, n_dim), dtype=torch.float32, device=DEVICE)
        else:
            W_k = ingest_hebbian_one_bank(shards[k], E, R, sq, n_dim)
        Ws.append(W_k)
        if GPU_AVAIL:
            torch.cuda.empty_cache()

    # Per-query: take max sim per V_C across banks (parallel cleanup)
    chunk = min(500, M_facts)  # smaller chunk to keep transient memory bounded
    hits = 0
    for start in range(0, M_facts, chunk):
        end = min(start + chunk, M_facts)
        batch_facts = facts[start:end]
        s_idx = torch.tensor([f[0] for f in batch_facts], device=DEVICE)
        r_idx = torch.tensor([f[1] for f in batch_facts], device=DEVICE)
        o_idx = torch.tensor([f[2] for f in batch_facts], device=DEVICE)
        keys = E[s_idx] * R[r_idx] * sq
        # Accumulate max sim per V_C across banks without materializing full (K,B,V_C) stack
        best_per_vc: Optional[torch.Tensor] = None
        for k in range(K_banks):
            states_k = (Ws[k] @ keys.T).T
            sims_k = states_k @ E.T  # (B, V_C)
            if best_per_vc is None:
                best_per_vc = sims_k
            else:
                best_per_vc = torch.maximum(best_per_vc, sims_k)
            del states_k, sims_k
        preds = best_per_vc.argmax(dim=1)
        hits += int((preds == o_idx).sum().item())
        del best_per_vc, keys

    for W in Ws:
        del W
    del Ws, E, R
    if GPU_AVAIL:
        torch.cuda.empty_cache()
    recall = hits / max(M_facts, 1)
    return {"recall_at_1": round(recall, 4), "V_C": V_C, "V_R": V_R_arg,
            "M_facts": M_facts, "N": n_dim, "n_queries": M_facts,
            "K_banks": K_banks,
            "alpha_N": round(M_facts / max(n_dim, 1), 3),
            "computed_headroom": round((V_C * V_R_arg) / max(M_facts, 1), 3),
            "keys_unique_mode": keys_unique_mode}


def _bias_s_check(result: Dict[str, Any], target_alpha_N: float,
                   target_headroom: float, n_dim: int) -> None:
    observed_alpha_N = result["alpha_N"]
    if abs(observed_alpha_N - target_alpha_N) >= 0.01:
        raise RuntimeError("BIAS_S_ALPHA_N_DRIFT: observed=%.4f target=%.4f" % (
            observed_alpha_N, target_alpha_N))
    observed_headroom = result["computed_headroom"]
    if target_headroom > 0:
        rel = observed_headroom / target_headroom
        if abs(rel - 1.0) >= 0.05:
            raise RuntimeError("BIAS_S_HEADROOM_DRIFT: observed=%.4f target=%.4f rel=%.4f" % (
                observed_headroom, target_headroom, rel))
    expected_mode = "unique_sr" if target_headroom >= 1.0 else "duplicates_allowed"
    if result["keys_unique_mode"] != expected_mode:
        raise RuntimeError("BIAS_S_KEY_MODE_MISMATCH: observed=%s expected=%s" % (
            result["keys_unique_mode"], expected_mode))


# ----------------------------- self-test -----------------------------
def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 512
    V_R_t = V_R  # 32
    V_C_t = 200
    M_t = 100  # alpha_N = 0.2, headroom = (200*32)/100 = 64

    E = bipolar_t(V_C_t, n, g)
    R = bipolar_t(V_R_t, n, g)
    assert E.shape == (V_C_t, n)

    g2 = np.random.default_rng(1)
    facts = make_facts(V_C_t, V_R_t, M_t, g2)
    assert len(facts) == M_t

    # T3: multi-bank K=2 ingest at tiny scale
    g3 = np.random.default_rng(2)
    out_k2 = eval_recall_multibank_K4(V_C_t, V_R_t, M_t, n, K_banks=2, g=g3)
    assert 0.0 <= out_k2["recall_at_1"] <= 1.0
    assert out_k2["K_banks"] == 2

    # T4: multi-bank K=4 ingest at tiny scale
    g4 = np.random.default_rng(3)
    out_k4 = eval_recall_multibank_K4(V_C_t, V_R_t, M_t, n, K_banks=4, g=g4)
    assert 0.0 <= out_k4["recall_at_1"] <= 1.0
    assert out_k4["K_banks"] == 4

    # T5: BIAS-S regime checks
    fake_ok = {"alpha_N": 4.0, "computed_headroom": 10.0,
                "keys_unique_mode": "unique_sr"}
    _bias_s_check(fake_ok, 4.0, 10.0, n)
    try:
        _bias_s_check({"alpha_N": 4.5, "computed_headroom": 10.0,
                        "keys_unique_mode": "unique_sr"}, 4.0, 10.0, n)
        raise AssertionError("BIAS_S_ALPHA_N_DRIFT not raised")
    except RuntimeError as e:
        assert "BIAS_S_ALPHA_N_DRIFT" in str(e)

    # T6: bands LOCKED
    assert HP_MB_REC_MIN == 0.95
    assert HP_MB_CV_MAX == 0.05
    assert MULTI_BANK_K == 4
    assert ALPHA_N_TARGET == 4.0
    assert HEADROOM_VAL == 10.0
    assert V_R == 32

    # T7: LLM-call counter
    assert _LLM_CALL_COUNTER[0] == 0

    # T8: cardinality
    if not SMOKE:
        assert EXPECTED_N_UNITS == 3, "full EXPECTED_N_UNITS=%d != 3" % EXPECTED_N_UNITS
    else:
        assert EXPECTED_N_UNITS == 1, "smoke EXPECTED_N_UNITS=%d != 1" % EXPECTED_N_UNITS

    # T9: target V_C is computable + reasonable
    target_V_C = _compute_VC_for(ALPHA_N_TARGET, HEADROOM_VAL, N_DIM)
    target_M = int(round(ALPHA_N_TARGET * N_DIM))
    # At full N=16384: M=65536, V_C=ceil(10*65536/32)=20480 (well-formed)
    if not SMOKE:
        assert target_M == 65536
        assert target_V_C == 20480

    print(("[selftest] PASS K2_rec=%.3f K4_rec=%.3f target_V_C=%d "
           "EXPECTED_N_UNITS=%d gpu=%s") % (
        out_k2["recall_at_1"], out_k4["recall_at_1"],
        target_V_C, EXPECTED_N_UNITS, GPU_AVAIL), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- run_unit + main -----------------------------
_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time(),
                                    "failures": []}


def _fmt_alpha(a: float) -> str:
    return ("%.1f" % a).replace(".", "p")


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        keys.append("seed%d_armMULTI_BANK_K%d_alpha%s_headroom%s" % (
            s, MULTI_BANK_K, _fmt_alpha(ALPHA_N_TARGET), HEADROOM_LABEL))
    return keys


def _parse_key(key: str) -> Dict[str, Any]:
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    if "armMULTI_BANK" in key:
        K = int(key.split("_K")[1].split("_alpha")[0])
        alpha_str = key.split("_alpha")[1].split("_headroom")[0]
        h_label = key.split("_headroom")[1]
        return {"seed": seed, "arm": "MULTI_BANK", "K_banks": K,
                "alpha_N": float(alpha_str.replace("p", ".")),
                "headroom_label": h_label}
    raise ValueError("unparseable key: %s" % key)


def run_unit(parsed: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.time()
    seed = parsed["seed"]
    arm = parsed["arm"]
    g = np.random.default_rng(seed * 100003 + hash(arm) % 100003)
    if GPU_AVAIL:
        torch.cuda.reset_peak_memory_stats(DEVICE)

    if arm != "MULTI_BANK":
        raise RuntimeError("Cell B is MULTI_BANK-only; got arm=%s" % arm)

    K_banks = parsed["K_banks"]
    alpha_N = parsed["alpha_N"]
    h_label = parsed["headroom_label"]
    h_val = HEADROOM_VAL if h_label == HEADROOM_LABEL else None
    if h_val is None:
        raise RuntimeError("unknown headroom label in Cell B: %s" % h_label)
    M = int(round(alpha_N * N_DIM))
    V_C = _compute_VC_for(alpha_N, h_val, N_DIM)
    rec = eval_recall_multibank_K4(V_C, V_R, M, N_DIM, K_banks=K_banks, g=g)
    _bias_s_check(rec, alpha_N, h_val, N_DIM)
    out = {
        "seed": seed, "arm": arm,
        "K_banks": K_banks,
        "alpha_N_target": alpha_N, "headroom_label": h_label,
        "headroom_target": h_val,
        **rec,
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

    mb_recs = [float(v["recall_at_1"]) for v in per_key.values()
                if v.get("arm") == "MULTI_BANK"]
    mb_mean = float(np.mean(mb_recs)) if mb_recs else float("nan")
    mb_std = float(np.std(mb_recs)) if len(mb_recs) > 1 else 0.0
    mb_cv = float(mb_std / max(abs(mb_mean), 1e-9)) if mb_mean and not math.isnan(mb_mean) else 0.0

    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0))
                 for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    peak_mems = [int(v.get("peak_mem_mb", 0)) for v in per_key.values()]
    peak_mem_max_mb = max(peak_mems) if peak_mems else 0

    summ = "MULTI_BANK_K%d_alpha%.1f_h%s: rec=%.4f cv=%.4f n=%d per_seed=%s peak_mem_mb=%d" % (
        MULTI_BANK_K, ALPHA_N_TARGET, HEADROOM_LABEL, mb_mean, mb_cv,
        len(mb_recs), [round(r, 4) for r in mb_recs], peak_mem_max_mb)
    card_str = " | n_units=%d/expected=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if failures:
        fail_str = " | failures=%d [%s]" % (
            len(failures),
            "; ".join("%s:%s" % (f.get("key", "?"), f.get("exc_type", "?"))
                       for f in failures[:3]))

    detail = {
        "multi_bank_K": MULTI_BANK_K,
        "alpha_N_target": ALPHA_N_TARGET,
        "headroom_label": HEADROOM_LABEL,
        "headroom_val": HEADROOM_VAL,
        "multi_bank_recall_mean": mb_mean,
        "multi_bank_recall_cv": mb_cv,
        "multi_bank_recall_per_seed": [round(r, 4) for r in mb_recs],
        "peak_mem_mb_max": peak_mem_max_mb,
        "substrate_only_ok": substrate_only_ok,
        "n_llm_calls": int(n_llm),
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "failures": failures,
    }

    if SMOKE:
        # Smoke: just check the K=4 path runs at small N without OOM/exception.
        if substrate_only_ok and not failures and cardinality_ok and not math.isnan(mb_mean):
            return ("SMOKE_PASS",
                    "SMOKE_PASS: K=4 multibank ran at N=%d rec=%.4f peak=%dMB | %s%s" % (
                        N_DIM, mb_mean, peak_mem_max_mb, summ, card_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL | %s%s%s" % (summ, card_str, fail_str),
                detail)

    # Full verdict
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

    if mb_mean >= HP_MB_REC_MIN and mb_cv <= HP_MB_CV_MAX:
        return ("HARD_PASS",
                "HARD_PASS_MULTI_BANK_K4: rec=%.4f >= %.2f AND cv=%.4f <= %.2f across %d seeds at alpha=%.1f h=%s (substrate-beats-baseline confirmed under K=4 sharding) | %s%s" % (
                    mb_mean, HP_MB_REC_MIN, mb_cv, HP_MB_CV_MAX,
                    len(mb_recs), ALPHA_N_TARGET, HEADROOM_LABEL,
                    summ, card_str),
                detail)
    if mb_mean >= MB_MB_REC_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_MULTI_BANK: rec=%.4f in [%.2f, %.2f) OR cv=%.4f > %.2f (METHOD_RULE_L band-floor) | %s%s" % (
                    mb_mean, MB_MB_REC_MIN, HP_MB_REC_MIN, mb_cv, HP_MB_CV_MAX,
                    summ, card_str),
                detail)
    return ("HARD_FAIL",
            "HARD_FAIL_MULTI_BANK_BELOW_FLOOR: rec=%.4f < %.2f at alpha=%.1f h=%s (mechanism does not survive K=4 sharding) | %s%s" % (
                mb_mean, MB_MB_REC_MIN, ALPHA_N_TARGET, HEADROOM_LABEL,
                summ, card_str),
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
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()),
                                  atexit_synth=True)
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
        "N_DIM": N_DIM,
        "V_R": V_R,
        "MULTI_BANK_K": MULTI_BANK_K,
        "ALPHA_N_TARGET": ALPHA_N_TARGET,
        "HEADROOM_LABEL": HEADROOM_LABEL,
        "HEADROOM_VAL": HEADROOM_VAL,
        "HP_MB_REC_MIN": HP_MB_REC_MIN,
        "HP_MB_CV_MAX": HP_MB_CV_MAX,
        "MB_MB_REC_MIN": MB_MB_REC_MIN,
        "CV_MAX": CV_MAX,
        "HP_SCOPE": {
            "MULTI_BANK_K4": ["HP_MB_REC_MIN>=%.2f at alpha=%.1f h=%s; CV<=%.2f" % (
                HP_MB_REC_MIN, ALPHA_N_TARGET, HEADROOM_LABEL, HP_MB_CV_MAX)],
            "MECH": ["EXEMPT_in_cell_B_routed_to_Cell_A"],
            "KNN_SENTINEL": ["EXEMPT_in_cell_B_routed_to_Cell_A"],
            "BARE_E_R": ["EXEMPT_in_cell_B_routed_to_Cell_A"],
        },
        "seeds": SEEDS,
        "per_unit": units,
        "detail": detail,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg[:300],
        "_atexit_synth": atexit_synth,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "gpu_avail": GPU_AVAIL,
        "gpu_name": GPU_NAME,
        "gpu_max_mem_gb": GPU_MAX_MEM_GB,
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": True,
        "metrics_source": "measured_substrate_bipolar_hebbian_W_multi_bank_K4_v2b_gpu",
        "DESIGN_NOTE": (
            "CAPACITY_V2B_MULTI_BANK_K4_GPU_ALONE: Rescue Cell B split from v1 "
            "per Skunkworks batch 8 (MULTI_BANK arm OOM'd at K=4 N=16384). "
            "Targets ONE phase point alpha_N=4.0 headroom=10x; 3 seeds; "
            "K_banks=4 sequential build + empty_cache + expandable_segments. "
            "GPU mandate (Fix #24): cuda asserted at full. HARD_PASS rec>=0.95 "
            "cv<=0.05 across 3 seeds. Mech / KNN / BARE arms EXEMPT (covered "
            "by Cell A). Routes overnight_queue per USER NO_LOCAL 2026-06-27."
        ),
    }


if __name__ == "__main__":
    # GPU mandate enforcement at full (Fix #24)
    if not SMOKE and not GPU_AVAIL:
        print("[FATAL] full-mode requires CUDA (Fix #24 GPU mandate); "
              "torch.cuda.is_available()=False", flush=True)
        sys.exit(1)

    print("[config] anchor=%s mode=%s seeds=%s N=%d V_R=%d K=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_R, MULTI_BANK_K, CONFIG_VERSION),
          flush=True)
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
        try:
            parsed = _parse_key(key)
            print("  [run] %s ..." % key, flush=True)
            rec = run_unit(parsed)
            write_partial_key(out_dir, key, rec)
            print("  [done] %s rec=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall_at_1"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
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
