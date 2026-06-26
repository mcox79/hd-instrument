"""substrate_partition_routing_hierarchical_2level_v1 -- Cell E for M=10M.

EXTENSION TARGET (per Research drill 2026-06-25): Cell 1
(substrate_partition_routing_10M_full_v2) chain-grade @ M=1M via single-level
partition routing (500 partitions * 2000 each). M=10M would need 5000
partitions; routing accuracy is predicted to cliff because FHRR pair-space
caps at ~500 partitions for N=8192 (per Frady-Sommer + Cell 1's M=1M
saturation observed today).

THIS CELL tests hierarchical 2-level routing for M=10M:
  - ARM_SINGLE_LEVEL: flat 5000 partitions at M=10M (predicted cliff)
  - ARM_2LEVEL_HIERARCHICAL: 10 coarse x 1000 fine = 10000 partitions of 1000
    each (avoids FHRR pair-space cliff)
  - ARM_FLAT_KV_REFERENCE: flat KV at M=10M (predicted to collapse;
    reference rail)

M-sweep: {1M (rail; reproduces Cell 1), 10M}

CONFIG:
  d=768, sigma=0.1 (matches Cell 1 envelope)
  partition_size_single = 2000 (matches Cell 1)
  partition_size_2level = (coarse=10, fine=1000) -> 10000 fine partitions of 1000 each
  Seeds [11, 13, 19] (cross-cell consistent)

PRE-REG BANDS (LOCKED at module init):

  HARD_PASS_M_10M_VIA_HIERARCHICAL:
    ARM_2LEVEL routed recall@10 >= 0.80 at M=10M
    AND ARM_SINGLE routed recall@10 cliffs (<= 0.50) at M=10M
    AND ARM_FLAT_KV collapses (<= 0.10) at M=10M
    AND cv <= 0.05 across seeds for ARM_2LEVEL
    (substrate KG extends to M=10M chain-grade via 2-level routing;
     single-level + flat both fail confirming the mechanism story)

  CHAIN_GRADE_AT_M_10M:
    ARM_2LEVEL routed recall@10 >= 0.70 at M=10M
    (lift over ARM_SINGLE at M=10M; not full chain-grade)

  HARD_FAIL_HIERARCHICAL_DOESNT_HELP:
    ARM_2LEVEL recall@10 < 0.50 at M=10M
    OR ARM_2LEVEL <= ARM_SINGLE at M=10M
    (hierarchical doesn't avoid the FHRR pair-space cliff)

  MIDDLE_BAND:
    ARM_2LEVEL recall@10 in [0.50, 0.70] at M=10M

GPU routing: overnight_queue per Fix #24 (M=10M needs GPU memory + torch
identity-chunk regeneration).

Author: exp_dev 2026-06-25 (Cell E hierarchical routing).
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial,
    aggregate_partials,
)

ANCHOR_NAME = "substrate_partition_routing_hierarchical_2level_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

DI = 1024
DC = 256
DC_COARSE = 256
PART_SIZE_SINGLE = 2000
PART_SIZE_FINE = 1000
N_COARSE = 10
N_FINE_PER_COARSE = 1000  # so 10 * 1000 = 10000 fine partitions at M=10M
TARGET_COS = 0.133
CAT_COS = 0.70
CAT_COS_COARSE = 0.80  # coarse routing slightly cleaner (semantic top-level)
N_SWEEP = [1_000_000, 10_000_000] if not SMOKE else [100_000, 1_000_000]
N_QUERIES = 200 if not SMOKE else 60
CHUNK = 250_000
SEEDS_FULL = [11, 13, 19]
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL

# PROSPECTIVE BANDS (LOCKED)
BAND_HARD_PASS_M10M_2LEVEL = 0.80
BAND_HARD_PASS_M10M_SINGLE_CLIFF = 0.50  # ARM_SINGLE must cliff AT/BELOW this
BAND_HARD_PASS_M10M_FLAT_COLLAPSE = 0.10  # ARM_FLAT must collapse AT/BELOW this
BAND_CHAIN_GRADE_M10M_2LEVEL = 0.70
BAND_HARD_FAIL_M10M_2LEVEL = 0.50
BAND_HARD_PASS_CV = 0.05
BAND_Q_SUSPECT_SATURATION = 0.995

assert BAND_HARD_PASS_M10M_2LEVEL > BAND_CHAIN_GRADE_M10M_2LEVEL > BAND_HARD_FAIL_M10M_2LEVEL
assert BAND_HARD_PASS_M10M_SINGLE_CLIFF > BAND_HARD_PASS_M10M_FLAT_COLLAPSE


def _np_unit(M):
    return M / (np.linalg.norm(M, axis=-1, keepdims=True) + 1e-12)


def _retrieval_noise(target_cos):
    return math.sqrt(max(0.0, 1.0 / (target_cos * target_cos) - 1.0))


# ---------- pure-numpy core (used by self-test) ----------
def identity_chunk_np(g0, n, di, seed):
    rng = np.random.default_rng((seed * 2_654_435_761 + g0) & ((1 << 63) - 1))
    return _np_unit(rng.standard_normal((n, di)).astype(np.float32))


def _selftest():
    di = 128
    seed = 7
    # determinism
    assert np.allclose(identity_chunk_np(0, 5, di, seed), identity_chunk_np(0, 5, di, seed))
    print("[selftest] T1 PASS: identity_chunk_np deterministic")

    # T2: 2-level routing routes to a fine partition reliably at clean coarse cue
    rng_c = np.random.default_rng(3)
    Cc = _np_unit(rng_c.standard_normal((N_COARSE, DC_COARSE)).astype(np.float32))
    Cf_per_coarse = _np_unit(rng_c.standard_normal((N_FINE_PER_COARSE, DC)).astype(np.float32))
    coarse_true = 5
    fine_true_within = 200
    # Coarse cue: clean
    qc_coarse = _np_unit(CAT_COS_COARSE * Cc[coarse_true]
                          + math.sqrt(1 - CAT_COS_COARSE**2) * _np_unit(
                              rng_c.standard_normal(DC_COARSE).astype(np.float32)))
    assert int(np.argmax(Cc @ qc_coarse)) == coarse_true
    # Fine cue: clean
    qc_fine = _np_unit(CAT_COS * Cf_per_coarse[fine_true_within]
                        + math.sqrt(1 - CAT_COS**2) * _np_unit(
                            rng_c.standard_normal(DC).astype(np.float32)))
    assert int(np.argmax(Cf_per_coarse @ qc_fine)) == fine_true_within
    print("[selftest] T2 PASS: 2-level coarse-then-fine routing routes correctly clean")

    # T3: retrieval noise -> target cos correct
    r = _retrieval_noise(0.133)
    assert abs(1.0 / math.sqrt(1 + r * r) - 0.133) < 1e-6
    print("[selftest] T3 PASS: retrieval_noise inverse correct")

    # T4: bands locked
    assert BAND_HARD_PASS_M10M_2LEVEL > BAND_CHAIN_GRADE_M10M_2LEVEL
    assert BAND_HARD_PASS_M10M_SINGLE_CLIFF < BAND_HARD_PASS_M10M_2LEVEL
    print("[selftest] T4 PASS: bands locked")

    # T5: hierarchical partition geometry math
    # M=10M with 10 coarse and 1000 fine per coarse + 1000 per partition = 10M total
    assert N_COARSE * N_FINE_PER_COARSE * PART_SIZE_FINE == 10_000_000, \
        "T5 hierarchical partition geometry wrong"
    print("[selftest] T5 PASS: 10 * 1000 * 1000 = 10M atoms fit hierarchy")
    print("[selftest] PASS: substrate_partition_routing_hierarchical_2level_v1 ALL")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)

try:
    import torch
except Exception as e:
    print("[FATAL] torch: %s" % e, flush=True)
    sys.exit(1)
DEV = "cuda" if torch.cuda.is_available() else "cpu"
GPU_AVAIL = torch.cuda.is_available()
GPU_NAME = torch.cuda.get_device_name(0) if GPU_AVAIL else "cpu"
print("[device] %s gpu_avail=%s name=%s" % (DEV, GPU_AVAIL, GPU_NAME), flush=True)


def identity_chunk_t(g0, n, di, seed):
    gen = torch.Generator(device=DEV)
    gen.manual_seed((seed * 2_654_435_761 + g0) & ((1 << 63) - 1))
    A = torch.randn(n, di, generator=gen, device=DEV)
    return A / (A.norm(dim=1, keepdim=True) + 1e-12)


def target_identity_t(g, di, seed):
    return identity_chunk_t(g, 1, di, seed)[0]


def flat_recall_at(N, di, seed, queries_t, target_g, target_score, k=10):
    """ARM_FLAT_KV_REFERENCE: scan ALL N identities for each query."""
    Q = queries_t.shape[0]
    beats = torch.zeros(Q, device=DEV)
    for g0 in range(0, N, CHUNK):
        n = min(CHUNK, N - g0)
        A = identity_chunk_t(g0, n, di, seed)
        sims = queries_t @ A.T
        beats += (sims > target_score[:, None]).sum(dim=1).float()
        del A, sims
    if DEV == "cuda":
        torch.cuda.empty_cache()
    return (beats < k).float().mean().item()


def run_seed_for_M(seed: int, N: int, di: int) -> Dict[str, Any]:
    """Run all 3 arms at one M = N atoms; return per-arm results."""
    print("\n[seed=%d M=%d] starting" % (seed, N), flush=True)
    r_noise = _retrieval_noise(TARGET_COS)
    rng = np.random.default_rng(seed ^ 0xA11CE ^ N)

    # ============================================================================
    # ARM_SINGLE_LEVEL setup: flat partitions of PART_SIZE_SINGLE
    # ============================================================================
    P_single = N // PART_SIZE_SINGLE
    Cc_single = _np_unit(rng.standard_normal((P_single, DC)).astype(np.float32))
    Cc_single_t = torch.from_numpy(Cc_single).to(DEV)

    # ============================================================================
    # ARM_2LEVEL_HIERARCHICAL setup
    # ============================================================================
    # M=10M = 10 coarse * 1000 fine * 1000 atoms = 10M
    # M=1M  = 10 coarse * 100 fine * 1000 atoms (auto-derived)
    P_fine_per_coarse = (N // (N_COARSE * PART_SIZE_FINE))
    Cc_coarse = _np_unit(rng.standard_normal((N_COARSE, DC_COARSE)).astype(np.float32))
    Cc_coarse_t = torch.from_numpy(Cc_coarse).to(DEV)
    # Each coarse partition has its own fine-codebook
    Cc_fine = _np_unit(rng.standard_normal((N_COARSE, P_fine_per_coarse, DC)).astype(np.float32))
    Cc_fine_t = torch.from_numpy(Cc_fine).to(DEV)

    # ============================================================================
    # Generate target atoms + cues (shared across arms for apples-to-apples)
    # ============================================================================
    tgt_g = rng.integers(0, N, N_QUERIES).astype(np.int64)
    q_id = np.zeros((N_QUERIES, di), dtype=np.float32)
    q_cat_single = np.zeros((N_QUERIES, DC), dtype=np.float32)
    q_cat_coarse = np.zeros((N_QUERIES, DC_COARSE), dtype=np.float32)
    q_cat_fine = np.zeros((N_QUERIES, DC), dtype=np.float32)

    for j, g in enumerate(tgt_g):
        idg = target_identity_t(int(g), di, seed).cpu().numpy()
        q_id[j] = _np_unit(idg + r_noise * _np_unit(
            rng.standard_normal(di).astype(np.float32)))
        # Single-level partition assignment
        p_single = int(g) // PART_SIZE_SINGLE
        q_cat_single[j] = _np_unit(CAT_COS * Cc_single[p_single]
                                    + math.sqrt(1 - CAT_COS**2) * _np_unit(
                                        rng.standard_normal(DC).astype(np.float32)))
        # 2-level partition assignment
        # Each atom is assigned: coarse_id = g // (N_FINE_PER_COARSE * PART_SIZE_FINE)
        # fine_id_within = (g // PART_SIZE_FINE) % N_FINE_PER_COARSE
        atoms_per_coarse = P_fine_per_coarse * PART_SIZE_FINE
        coarse_id = int(g) // atoms_per_coarse
        fine_id = (int(g) // PART_SIZE_FINE) % P_fine_per_coarse
        q_cat_coarse[j] = _np_unit(CAT_COS_COARSE * Cc_coarse[coarse_id]
                                    + math.sqrt(1 - CAT_COS_COARSE**2) * _np_unit(
                                        rng.standard_normal(DC_COARSE).astype(np.float32)))
        q_cat_fine[j] = _np_unit(CAT_COS * Cc_fine[coarse_id, fine_id]
                                  + math.sqrt(1 - CAT_COS**2) * _np_unit(
                                      rng.standard_normal(DC).astype(np.float32)))

    q_id_t = torch.from_numpy(q_id).to(DEV)
    q_cat_single_t = torch.from_numpy(q_cat_single).to(DEV)
    q_cat_coarse_t = torch.from_numpy(q_cat_coarse).to(DEV)
    q_cat_fine_t = torch.from_numpy(q_cat_fine).to(DEV)
    tgt_score = torch.stack([q_id_t[j] @ target_identity_t(int(tgt_g[j]), di, seed)
                             for j in range(N_QUERIES)])

    # ============================================================================
    # ARM_SINGLE_LEVEL: route + recall within partition
    # ============================================================================
    print("  [seed=%d M=%d] ARM_SINGLE_LEVEL: P_single=%d" % (seed, N, P_single), flush=True)
    t0 = time.time()
    routes_single = torch.argmax(q_cat_single_t @ Cc_single_t.T, dim=1).cpu().numpy()
    true_p_single = (tgt_g // PART_SIZE_SINGLE)
    route_acc_single = float(np.mean(routes_single == true_p_single))
    single_hits = 0
    for j in range(N_QUERIES):
        rp = int(routes_single[j])
        g0 = rp * PART_SIZE_SINGLE
        A = identity_chunk_t(g0, PART_SIZE_SINGLE, di, seed)
        beats = int((A @ q_id_t[j] > tgt_score[j]).sum().item())
        del A
        single_hits += 1 if (rp == int(true_p_single[j]) and beats < 10) else 0
    single_recall = single_hits / N_QUERIES
    single_t = time.time() - t0
    if DEV == "cuda":
        torch.cuda.empty_cache()
    print("    ARM_SINGLE_LEVEL routed_recall=%.4f route_acc=%.4f t=%.1fs"
          % (single_recall, route_acc_single, single_t), flush=True)

    # ============================================================================
    # ARM_2LEVEL_HIERARCHICAL: coarse route -> fine route -> recall within fine
    # ============================================================================
    print("  [seed=%d M=%d] ARM_2LEVEL: %d coarse x %d fine per coarse"
          % (seed, N, N_COARSE, P_fine_per_coarse), flush=True)
    t0 = time.time()
    # Stage 1: route to coarse
    routes_coarse = torch.argmax(q_cat_coarse_t @ Cc_coarse_t.T, dim=1).cpu().numpy()
    atoms_per_coarse = P_fine_per_coarse * PART_SIZE_FINE
    true_coarse = (tgt_g // atoms_per_coarse)
    route_acc_coarse = float(np.mean(routes_coarse == true_coarse))
    # Stage 2: route to fine within the routed coarse
    routes_fine = np.zeros(N_QUERIES, dtype=np.int64)
    for j in range(N_QUERIES):
        c = int(routes_coarse[j])
        # Cc_fine[c] is shape (P_fine_per_coarse, DC); use TORCH for batched
        # Use the corresponding coarse's fine codebook
        cf = Cc_fine_t[c]  # (P_fine_per_coarse, DC) on DEV
        sims = cf @ q_cat_fine_t[j]  # (P_fine_per_coarse,)
        routes_fine[j] = int(sims.argmax().item())
    true_fine_within = (tgt_g // PART_SIZE_FINE) % P_fine_per_coarse
    route_acc_fine = float(np.mean(routes_fine == true_fine_within))
    # Stage 3: recall within fine partition (size PART_SIZE_FINE)
    two_hits = 0
    for j in range(N_QUERIES):
        c = int(routes_coarse[j])
        f = int(routes_fine[j])
        # Global g0 of this fine partition: c * atoms_per_coarse + f * PART_SIZE_FINE
        g0 = c * atoms_per_coarse + f * PART_SIZE_FINE
        if g0 + PART_SIZE_FINE > N:
            chunk_n = N - g0
            if chunk_n <= 0:
                continue
        else:
            chunk_n = PART_SIZE_FINE
        A = identity_chunk_t(g0, chunk_n, di, seed)
        beats = int((A @ q_id_t[j] > tgt_score[j]).sum().item())
        del A
        route_correct = (c == int(true_coarse[j])) and (f == int(true_fine_within[j]))
        two_hits += 1 if (route_correct and beats < 10) else 0
    two_recall = two_hits / N_QUERIES
    two_t = time.time() - t0
    if DEV == "cuda":
        torch.cuda.empty_cache()
    print("    ARM_2LEVEL routed_recall=%.4f coarse_acc=%.4f fine_acc=%.4f t=%.1fs"
          % (two_recall, route_acc_coarse, route_acc_fine, two_t), flush=True)

    # ============================================================================
    # ARM_FLAT_KV_REFERENCE: flat scan all N
    # ============================================================================
    print("  [seed=%d M=%d] ARM_FLAT_KV_REFERENCE: flat scan all N=%d" % (seed, N, N),
          flush=True)
    t0 = time.time()
    flat_recall = flat_recall_at(N, di, seed, q_id_t, tgt_g, tgt_score)
    flat_t = time.time() - t0
    print("    ARM_FLAT_KV_REFERENCE recall=%.4f t=%.1fs" % (flat_recall, flat_t),
          flush=True)

    return {
        "M": N,
        "arm_single_level": {
            "routed_recall_at_10": round(single_recall, 4),
            "route_acc": round(route_acc_single, 4),
            "P_single": P_single,
            "elapsed_s": round(single_t, 2),
        },
        "arm_2level_hierarchical": {
            "routed_recall_at_10": round(two_recall, 4),
            "route_acc_coarse": round(route_acc_coarse, 4),
            "route_acc_fine": round(route_acc_fine, 4),
            "N_COARSE": N_COARSE,
            "P_fine_per_coarse": P_fine_per_coarse,
            "elapsed_s": round(two_t, 2),
        },
        "arm_flat_kv_reference": {
            "recall_at_10": round(flat_recall, 4),
            "elapsed_s": round(flat_t, 2),
        },
    }


def run_one_seed(seed: int) -> Dict:
    print("\n=== [seed %d] starting at %s ===" % (seed, time.strftime("%H:%M:%S")), flush=True)
    t0_seed = time.time()
    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": DI,
        "n_sweep_M": N_SWEEP,
        "part_size_single": PART_SIZE_SINGLE,
        "part_size_fine": PART_SIZE_FINE,
        "n_coarse": N_COARSE,
        "target_cos": TARGET_COS,
        "cat_cos": CAT_COS,
        "cat_cos_coarse": CAT_COS_COARSE,
        "per_M": {},
    }
    for N in N_SWEEP:
        out["per_M"][str(N)] = run_seed_for_M(seed, N, DI)
    out["elapsed_s_seed"] = round(time.time() - t0_seed, 1)
    return out


def aggregate_per_M(per_seed: List[Dict]) -> Dict:
    agg = {}
    for N in N_SWEEP:
        arms = {}
        for arm_name in ["arm_single_level", "arm_2level_hierarchical", "arm_flat_kv_reference"]:
            recall_key = ("routed_recall_at_10" if arm_name != "arm_flat_kv_reference"
                          else "recall_at_10")
            vals = []
            for s in per_seed:
                v = s["per_M"].get(str(N), {}).get(arm_name, {}).get(recall_key)
                if v is not None and not (isinstance(v, float) and math.isnan(v)):
                    vals.append(float(v))
            m = float(np.mean(vals)) if vals else float("nan")
            cv = float(np.std(vals) / max(abs(m), 1e-9)) if len(vals) >= 2 else 0.0
            arms[arm_name] = {
                "recall_mean": round(m, 4),
                "recall_cv": round(cv, 4),
                "per_seed_recall": [round(v, 4) for v in vals],
            }
        agg[str(N)] = arms
    return agg


def verdict(agg: Dict) -> Tuple[str, str]:
    M10M = str(10_000_000)
    if M10M not in agg:
        return ("UNKNOWN", "M=10M not in sweep")
    a = agg[M10M]
    r_2level = a["arm_2level_hierarchical"]["recall_mean"]
    cv_2level = a["arm_2level_hierarchical"]["recall_cv"]
    r_single = a["arm_single_level"]["recall_mean"]
    r_flat = a["arm_flat_kv_reference"]["recall_mean"]

    summ_pieces = []
    for N in N_SWEEP:
        b = agg[str(N)]
        summ_pieces.append(
            "M=%d: 2LEVEL=%.4f (cv=%.3f) SINGLE=%.4f FLAT=%.4f" % (
                N, b["arm_2level_hierarchical"]["recall_mean"],
                b["arm_2level_hierarchical"]["recall_cv"],
                b["arm_single_level"]["recall_mean"],
                b["arm_flat_kv_reference"]["recall_mean"]))
    summ = " | ".join(summ_pieces)

    # HARD_FAIL: 2-level doesn't help
    if r_2level < BAND_HARD_FAIL_M10M_2LEVEL or r_2level <= r_single:
        return ("HARD_FAIL_HIERARCHICAL_DOESNT_HELP",
                "HARD_FAIL_HIERARCHICAL_DOESNT_HELP at M=10M: 2LEVEL=%.4f SINGLE=%.4f | %s"
                % (r_2level, r_single, summ))

    # Q-discipline
    sat = ""
    if r_2level >= BAND_Q_SUSPECT_SATURATION:
        sat = " [Q-DISCIPLINE: suspect saturation -- 2LEVEL >= %.3f]" % BAND_Q_SUSPECT_SATURATION

    # HARD_PASS
    if (r_2level >= BAND_HARD_PASS_M10M_2LEVEL
            and r_single <= BAND_HARD_PASS_M10M_SINGLE_CLIFF
            and r_flat <= BAND_HARD_PASS_M10M_FLAT_COLLAPSE
            and cv_2level <= BAND_HARD_PASS_CV):
        return ("HARD_PASS_M_10M_VIA_HIERARCHICAL",
                "HARD_PASS_M_10M_VIA_HIERARCHICAL_ROUTING (2-level lifts M=10M, single cliffs, flat collapses) | %s%s"
                % (summ, sat))

    # CHAIN_GRADE
    if r_2level >= BAND_CHAIN_GRADE_M10M_2LEVEL:
        return ("CHAIN_GRADE_AT_M_10M",
                "CHAIN_GRADE_AT_M_10M_HIERARCHICAL: 2LEVEL=%.4f >= %.2f at M=10M | %s%s"
                % (r_2level, BAND_CHAIN_GRADE_M10M_2LEVEL, summ, sat))

    return ("MIDDLE_BAND",
            "MIDDLE_BAND_HIERARCHICAL_PARTIAL_LIFT: 2LEVEL=%.4f at M=10M | %s%s"
            % (r_2level, summ, sat))


# ============================================================================
# atexit + main
# ============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg_partials = aggregate_partials(od, SEEDS,
                                           run_config={"N": DI, "run_mode": RUN_MODE})
        per_seed = list(agg_partials.values())
        if not per_seed:
            return
        agg = aggregate_per_M(per_seed)
        v, vmsg = verdict(agg)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "per_seed": per_seed, "aggregate": agg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "gpu_available": GPU_AVAIL, "gpu_name": GPU_NAME,
        }
        write_metrics(od, metrics, per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


print("[config] anchor=%s mode=%s di=%d dc=%d N_sweep=%s seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, DI, DC, N_SWEEP, SEEDS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
_RESULTS_HOLDER["out_dir"] = out_dir
t0 = time.time()
run_config = {"N": DI, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining),
      flush=True)
for seed in remaining:
    res = run_one_seed(seed)
    write_partial(out_dir, seed, res)

per_seed = list(aggregate_partials(out_dir, SEEDS,
                                    run_config=run_config).values())
agg = aggregate_per_M(per_seed)
v, vmsg = verdict(agg)
print("\n[VERDICT] " + vmsg, flush=True)
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
    "summary": vmsg, "headline": vmsg,
    "run_mode": RUN_MODE, "n_seeds": len(per_seed),
    "seeds": [s["seed"] for s in per_seed],
    "aggregate": agg, "per_seed": per_seed,
    "elapsed_s": time.time() - t0,
    "gpu_available": GPU_AVAIL, "gpu_name": GPU_NAME,
    "bands": {
        "HARD_PASS_M10M_2LEVEL": BAND_HARD_PASS_M10M_2LEVEL,
        "HARD_PASS_M10M_SINGLE_CLIFF": BAND_HARD_PASS_M10M_SINGLE_CLIFF,
        "HARD_PASS_M10M_FLAT_COLLAPSE": BAND_HARD_PASS_M10M_FLAT_COLLAPSE,
        "CHAIN_GRADE_M10M_2LEVEL": BAND_CHAIN_GRADE_M10M_2LEVEL,
        "HARD_FAIL_M10M_2LEVEL": BAND_HARD_FAIL_M10M_2LEVEL,
        "HARD_PASS_CV": BAND_HARD_PASS_CV,
        "Q_SUSPECT_SATURATION": BAND_Q_SUSPECT_SATURATION,
    },
    "config_version": "v1_2level_hierarchical_n_coarse_10_part_fine_1000_seeds_11_13_19",
    "DESIGN_NOTE": (
        "Hierarchical 2-level partition routing for M=10M. 3 arms: SINGLE_LEVEL "
        "(Cell 1's flat 5000 partitions at M=10M; predicted to cliff via FHRR "
        "pair-space at N=8192), 2LEVEL_HIERARCHICAL (10 coarse * 1000 fine = "
        "10000 partitions of 1000 each), FLAT_KV_REFERENCE (flat scan all N; "
        "predicted to collapse). Brain analog: hippocampal indexing into "
        "cortical regions (Goyal/Buzsaki 2021)."
    ),
}
write_metrics(out_dir, metrics, per_seed)
print("[metrics] written", flush=True)
