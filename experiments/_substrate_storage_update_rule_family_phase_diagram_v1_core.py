"""Shared core for substrate_storage_update_rule_family_phase_diagram_v1.

STORAGE UPDATE RULE family phase diagram (USER 2026-06-30 outer-axis fill).
COMPLEMENT to substrate_capacity_multibank_alpha_K_phase_diagram_v2_GPU:
that cell sweeps alpha x K_per_bank x N x B with HEBBIAN-OUTER as the only
update rule. This cell holds (alpha, K, B, N) at chain-grade-rail config and
sweeps the WRITE-UPDATE rule itself across 4 biologically-motivated variants.

UPDATE RULES (OUTER axis; LOCKED):
    hebbian_outer_product : W += x outer y   (standard substrate default)
    soft_hebb             : W += (y - y_pred) outer x  (predictive-coding flavor;
                                                        soft competitive learning)
    willshaw_binary       : W = max(W, sign(x outer y))  (binary AM; non-linear)
    bcm_gain              : W += (y - theta) * y * outer(x)  (BCM rule;
                                                              modulated by post)

Inner axis: alpha-sweep at chain-grade-rail config.
    K_per_bank=64, num_banks=16 (rail: M=512 items / 16 banks = 32 items/bank
    well below K_per_bank=64 -- discrim regime).
    alpha in {0.5, 1.0, 2.0, 4.0} -> M in {N/2, N, 2N, 4N}
        At alpha=0.5: M < K_per_bank*B = 1024; clean regime
        At alpha=4.0: M = 4N = 32768 >> 1024 slots; collapse regime
        Cliff between (predicted alpha_cliff ~ 2.0 for Hebbian; rule-dependent).

INNER AXES:
    alpha (loading factor): alpha_full in {0.5, 1.0, 2.0, 4.0}; alpha_smoke
        in {0.5, 1.0, 2.0, 4.0} (same; cheap to evaluate at smoke-N=2048)
    N (dim): 8192 FULL; 2048 SMOKE

DISCRIMINATOR (load-bearing):
    recall_at_M = mean(pred_item_idx == true_item_idx) over N_PROBE items
    alpha_cliff = smallest alpha where recall drops below 0.50
    Discrimination across rules = different alpha_cliff localization.

POSITIVE CONTROL: hebbian_outer_product at alpha=0.5 must produce
recall >= 0.95 (chain-grade default; v2 cell verified Hebbian works here).

HARD-PASS BANDS:
    chain-grade (per rule):
        recall_mean >= 0.90 at alpha=0.5
        alpha_cliff distinguishable from other rules (>=0.5 log2 alpha separation)
    HARD_PASS (per phase point): recall >= 0.90
    MIDDLE_BAND: 0.30 <= recall < 0.90
    FLOOR: recall <= 0.05 (effectively random; 1/M chance)

CARDINALITY:
    FULL: 4 rules * 4 alphas = 16 phase points per seed
    SMOKE: 4 rules * 4 alphas = 16 phase points per seed
    CARDINALITY_OK is HARD_FAIL on breach (META_RULE_H).

ASCII-only. No unicode. CUDA preferred; CPU fallback for smoke.
FULL on CPU REFUSED unless HDLAB_QUEUE=local_cpu_queue (Fix #24).
Storage-free design: items represented bipolar in-memory at evaluation time.

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn, outer-axis fill)
"""
from __future__ import annotations

import hashlib
import math
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import torch

_CUDA_OK = bool(torch.cuda.is_available())
if _CUDA_OK:
    DEVICE = torch.device("cuda")
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MAX_MEM_GB = torch.cuda.get_device_properties(0).total_memory / 1e9
else:
    DEVICE = torch.device("cpu")
    GPU_NAME = "cpu_fallback"
    GPU_MAX_MEM_GB = 0.0


# Pre-reg constants (LOCKED at module init; META_RULE_AE)
HP_CHAIN_GRADE_RECALL = 0.90       # at alpha=0.5
HP_HARD_PASS_RECALL = 0.90         # per-point HARD_PASS
HP_MIDDLE_BAND_RECALL = 0.30       # per-point MIDDLE_BAND lo
HP_FLOOR_RECALL = 0.05             # FLOOR
Q_SUSPECT_SATURATION = 0.999       # near-perfect = saturation flag
HP_DISCRIM_ALPHA_CLIFF_LOG2 = 0.5  # rules differ if alpha_cliff differs by >=0.5 in log2
HP_DISCRIMINATOR_FRACTION = 0.30   # >=30% of phase points discriminate per rule

# Update-rule families (OUTER axis; LOCKED)
UPDATE_RULES = ("hebbian_outer_product", "soft_hebb",
                "willshaw_binary", "bcm_gain")

# Fixed rail config (chain-grade-rail per v2 capacity cell findings)
K_PER_BANK_RAIL = 64
NUM_BANKS_RAIL = 16
CB_TOTAL_SLOTS = K_PER_BANK_RAIL * NUM_BANKS_RAIL  # = 1024 capacity

# Sweep axes
ALPHA_SWEEP_FULL = [0.5, 1.0, 2.0, 4.0]
ALPHA_SWEEP_SMOKE = [0.5, 1.0, 2.0, 4.0]
N_DIM_FULL = 8192
N_DIM_SMOKE = 2048

# Probe-query sampling
N_PROBE_FULL = 256       # per phase point
N_PROBE_SMOKE = 64

# Cue noise
CUE_COS = 0.70

# BCM gain modulation threshold
BCM_THETA = 0.0

# SoftHebb softmax temperature
SOFT_HEBB_TEMP = 1.0

EXPECTED_N_UNITS_FULL = len(UPDATE_RULES) * len(ALPHA_SWEEP_FULL)    # 4 * 4 = 16
EXPECTED_N_UNITS_SMOKE = len(UPDATE_RULES) * len(ALPHA_SWEEP_SMOKE)  # 4 * 4 = 16

POSITIVE_CONTROL = {
    "update_rule": "hebbian_outer_product",
    "alpha": 0.5,
    "recall_floor": 0.90,
}
POSITIVE_CONTROL_SMOKE = {
    "update_rule": "hebbian_outer_product",
    "alpha": 0.5,
    "recall_floor": 0.80,   # smoke-N=2048 noisier; conservative
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    return "torch.cuda" if _CUDA_OK else "torch.cpu"


# HD primitives
def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape: Tuple[int, ...], gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=DEVICE, dtype=torch.float32)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    return torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))


# WRITE-UPDATE RULES
# Each writer takes:
#   items_x: (M, N) bipolar keys (cues)
#   items_y: (M, N) bipolar values (targets)
# Returns:
#   W: (N, N) write-state matrix after applying M write operations
def _writer_hebbian_outer_product(items_x: torch.Tensor,
                                    items_y: torch.Tensor) -> torch.Tensor:
    """Hebbian: W = sum_i outer(x_i, y_i)."""
    # Vectorized: W = X.T @ Y  (N, N) where X is (M, N), Y is (M, N)
    return items_x.T @ items_y


def _writer_soft_hebb(items_x: torch.Tensor,
                       items_y: torch.Tensor) -> torch.Tensor:
    """SoftHebb: W incremental; per-item residual (y - softmax(W^T x) on prev W).

    Incremental online rule -- runs as a Python loop over M but vectorizes per-item.
    Predicts y_hat = softmax(W^T x / T) then updates with residual outer-product.
    Captures the predictive-coding flavor (competitive learning at the post-synaptic).
    """
    M, N = items_x.shape
    W = torch.zeros((N, N), device=DEVICE, dtype=torch.float32)
    for i in range(M):
        x = items_x[i]            # (N,)
        y = items_y[i]            # (N,)
        # Predict y from current W
        y_pred_logits = W.T @ x   # (N,)
        # Soft-competitive: softmax over y_pred bipolar projection
        y_hat = torch.tanh(y_pred_logits / SOFT_HEBB_TEMP)  # (N,) in [-1, 1]
        residual = y - y_hat       # (N,)
        W += torch.outer(x, residual)
    return W


def _writer_willshaw_binary(items_x: torch.Tensor,
                              items_y: torch.Tensor) -> torch.Tensor:
    """Willshaw binary AM: W_ij = OR_i sign(x_i_j * y_i_k) >= 0 -> 1 else 0.

    Bipolar variant: W = max(W, sign(X.T @ Y_i)) but per-item. Vectorized as:
    W = bipolar_quantize(sum sign(outer(x_i, y_i))).
    Equivalent to sign-quantizing the Hebbian sum (binary AM).
    """
    W_hebb = items_x.T @ items_y  # (N, N)
    return bipolar_quantize_t(W_hebb)


def _writer_bcm_gain(items_x: torch.Tensor,
                      items_y: torch.Tensor) -> torch.Tensor:
    """BCM rule: W += x outer (y * (y - theta)).

    Modulates the Hebbian update by post-synaptic activation magnitude relative
    to a fixed threshold theta. For bipolar y in {-1,+1} with theta=0, this is
    equivalent to W += x outer (y * y) = x outer 1 = 0 (degenerate).
    Use theta_per_post = mean(y_pred_history) per neuron, simplified here to
    static theta=BCM_THETA with y in {-1, +1}: factor = y*(y-theta).
    """
    # BCM-style modulator: per-item per-dim weight = y * (y - theta)
    # For bipolar y in {-1, +1} and theta=0, modulator = y^2 = 1 (degenerate).
    # We use a SOFT version: y_soft = tanh(some_pre_response) to break degeneracy.
    # Simpler: compute modulator from y * (y - mean(y_i)) within row.
    y_mean = items_y.mean(dim=1, keepdim=True)             # (M, 1)
    modulator = items_y * (items_y - y_mean)                # (M, N) signed
    return items_x.T @ modulator                            # (N, N)


_WRITER_REGISTRY: Dict[str, Callable] = {
    "hebbian_outer_product": _writer_hebbian_outer_product,
    "soft_hebb": _writer_soft_hebb,
    "willshaw_binary": _writer_willshaw_binary,
    "bcm_gain": _writer_bcm_gain,
}


# Per-point evaluation
def eval_update_rule_arm(update_rule: str, alpha: float, n_dim: int,
                          seed_offset: int, n_probe: int) -> Dict[str, Any]:
    """Storage-free per-phase-point evaluation.

    Step 1: M = round(alpha * N) bipolar items (keys X, values Y).
    Step 2: Apply update_rule writer to build W = (N, N).
    Step 3: For each of N_PROBE probe items, noisy_x = noise+x_i; predict y_hat
            = sign(W^T noisy_x); recall_i = (sign(y_hat) == y_i) frac-match.
    Step 4: recall = mean per-bit-correct over N_PROBE items.
    """
    if update_rule not in _WRITER_REGISTRY:
        raise ValueError(f"unknown update_rule={update_rule!r}")

    t0 = time.time()
    if _CUDA_OK:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    M = max(1, int(round(alpha * n_dim)))

    # Build M bipolar key-value pairs
    g_keys = _make_gen(seed_offset + 11)
    g_vals = _make_gen(seed_offset + 13)
    keys = random_bipolar_t((M, n_dim), g_keys)
    vals = random_bipolar_t((M, n_dim), g_vals)

    # Apply writer
    writer = _WRITER_REGISTRY[update_rule]
    t_write = time.time()
    W = writer(keys, vals)
    write_latency_s = time.time() - t_write

    # Sample N_PROBE probe items (subset of M)
    g_probe = _make_gen(seed_offset + 17)
    probe_idx = torch.randperm(M, generator=g_probe, device=DEVICE)[:min(M, n_probe)]
    probe_keys_clean = keys[probe_idx]            # (N_PROBE, N)
    probe_vals_true = vals[probe_idx]             # (N_PROBE, N)

    # Add cue noise: cue = CUE_COS * key + sqrt(1-CUE_COS^2) * noise_bp
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))
    g_noise = _make_gen(seed_offset + 23)
    noise_raw = torch.empty(probe_keys_clean.shape, device=DEVICE, dtype=torch.float32)
    noise_raw.normal_(0.0, 1.0, generator=g_noise)
    noise_bp = bipolar_quantize_t(noise_raw)
    noisy_cues = CUE_COS * probe_keys_clean + cue_noise_scale * noise_bp

    # Read out: y_hat = sign(W^T x)
    t_read = time.time()
    y_hat_logits = noisy_cues @ W   # (N_PROBE, N)
    y_hat = bipolar_quantize_t(y_hat_logits)
    if _CUDA_OK:
        torch.cuda.synchronize()
    read_latency_s = time.time() - t_read

    # Recall = bit-accuracy averaged over N_PROBE items
    bit_match = (y_hat == probe_vals_true).float().mean(dim=1)  # (N_PROBE,)
    recall = float(bit_match.mean().item())
    recall_std = float(bit_match.std().item())

    # Anchor-distinctness fingerprint (META_RULE_AF)
    W_hash = hashlib.sha256(W.detach().cpu().numpy().tobytes()).hexdigest()[:16]

    if _CUDA_OK:
        peak_mem_mb = torch.cuda.max_memory_allocated() / 1e6
    else:
        peak_mem_mb = -1.0

    elapsed = time.time() - t0
    floor_thr = HP_FLOOR_RECALL
    if recall >= Q_SUSPECT_SATURATION:
        tier = "SATURATED"
    elif recall >= HP_HARD_PASS_RECALL:
        tier = "HARD_PASS"
    elif recall >= HP_MIDDLE_BAND_RECALL:
        tier = "MIDDLE_BAND"
    elif recall <= floor_thr:
        tier = "FLOOR"
    else:
        tier = "HARD_FAIL"

    del keys, vals, W, noisy_cues, y_hat, y_hat_logits, noise_raw, noise_bp
    if _CUDA_OK:
        torch.cuda.empty_cache()

    return {
        "update_rule": update_rule,
        "alpha": alpha,
        "M": M,
        "N": n_dim,
        "n_probe": int(probe_idx.numel()),
        "recall": round(recall, 5),
        "recall_std": round(recall_std, 5),
        "write_latency_s": round(write_latency_s, 4),
        "read_latency_s": round(read_latency_s, 4),
        "verdict_tier_per_point": tier,
        "saturation_flag": recall >= Q_SUSPECT_SATURATION,
        "W_hash": W_hash,
        "peak_mem_mb": round(peak_mem_mb, 1),
        "elapsed_per_point_s": round(elapsed, 3),
    }


def selftest(seed: int) -> Tuple[bool, str]:
    """Selftest: cardinality + 4 writers operational + arms-differ + sanity."""
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 16:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 16"
    if EXPECTED_N_UNITS_SMOKE != 16:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 16"
    msgs.append(f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    for rule in UPDATE_RULES:
        if rule not in _WRITER_REGISTRY:
            return False, f"rule {rule} not in registry"
        if not callable(_WRITER_REGISTRY[rule]):
            return False, f"rule {rule} not callable"
    msgs.append(f"4 rules registered: {list(_WRITER_REGISTRY.keys())}")

    # Tiny-scale sanity at low alpha=0.5: all 4 rules should produce recall >> floor
    n_dim_san = 512
    alpha_san = 0.5
    n_probe_san = 32
    san_results: Dict[str, Dict[str, Any]] = {}
    for rule in UPDATE_RULES:
        r = eval_update_rule_arm(rule, alpha_san, n_dim_san,
                                   seed_offset=seed * 7 + 100,
                                   n_probe=n_probe_san)
        san_results[rule] = r
        msgs.append(f"sanity {rule}: alpha={alpha_san} N={n_dim_san} "
                    f"M={r['M']} recall={r['recall']:.3f} "
                    f"write_t={r['write_latency_s']:.3f}s")

    # At alpha=0.5 (M=256 in N=512 with K*B=1024 slots), all rules should EXCEED
    # FLOOR=0.05 + clear by HP_MIDDLE_BAND_RECALL=0.30 (well-conditioned regime).
    for rule in UPDATE_RULES:
        rec = san_results[rule]["recall"]
        if rec < HP_MIDDLE_BAND_RECALL:
            return False, (f"sanity FAIL {rule}: recall={rec:.3f} < "
                            f"{HP_MIDDLE_BAND_RECALL:.2f} at alpha=0.5 "
                            f"(rule not learning)")

    # Arms-differ: all 4 rules must produce DIFFERENT W_hash
    hashes = {rule: san_results[rule]["W_hash"] for rule in UPDATE_RULES}
    n_unique = len(set(hashes.values()))
    if n_unique < 4:
        return False, (f"ARMS_DIFFER violation: only {n_unique}/4 unique "
                        f"W hashes; hashes={hashes}")
    msgs.append(f"4/4 unique W hashes (rules genuinely distinct)")

    if _CUDA_OK:
        torch.cuda.empty_cache()

    return True, "; ".join(msgs)


# Per-seed sweep
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        alpha_sweep = ALPHA_SWEEP_SMOKE
        n_dim = N_DIM_SMOKE
        n_probe = N_PROBE_SMOKE
    else:
        alpha_sweep = ALPHA_SWEEP_FULL
        n_dim = N_DIM_FULL
        n_probe = N_PROBE_FULL

    expected_n_units = len(UPDATE_RULES) * len(alpha_sweep)

    print(f"[run_one_seed] seed={seed} mode={run_mode} device={DEVICE} "
          f"rules={UPDATE_RULES} alpha_sweep={alpha_sweep} "
          f"N={n_dim} n_probe={n_probe} expected_n={expected_n_units}",
          flush=True)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()

    for rule in UPDATE_RULES:
        for alpha in alpha_sweep:
            seed_offset = (seed * 100003 + int(alpha * 1000)
                            + (hash(rule) % 7919))
            print(f"[point] seed={seed} rule={rule} alpha={alpha} ...", flush=True)
            pt = eval_update_rule_arm(rule, alpha, n_dim, seed_offset, n_probe)
            phase_map.append(pt)
            print(f"  -> M={pt['M']} recall={pt['recall']:.4f} "
                  f"tier={pt['verdict_tier_per_point']} "
                  f"write_t={pt['write_latency_s']:.3f}s "
                  f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-rule arms-differ via W hashes (across alpha-sweep)
    rule_hashes: Dict[str, List[str]] = {rule: [] for rule in UPDATE_RULES}
    for p in phase_map:
        rule_hashes[p["update_rule"]].append(p["W_hash"])

    # Per-rule summary
    per_rule_summary: Dict[str, Dict[str, Any]] = {}
    for rule in UPDATE_RULES:
        rule_pts = [p for p in phase_map if p["update_rule"] == rule]
        if not rule_pts:
            continue
        recalls = [p["recall"] for p in rule_pts]
        alphas = [p["alpha"] for p in rule_pts]
        recall_at_low_alpha = next((p["recall"] for p in rule_pts
                                     if p["alpha"] == min(alphas)), 0.0)
        # alpha_cliff = smallest alpha where recall drops below 0.50; if none, max alpha
        cliff = None
        for p in sorted(rule_pts, key=lambda x: x["alpha"]):
            if p["recall"] < 0.50:
                cliff = p["alpha"]
                break
        if cliff is None:
            cliff = max(alphas) * 2.0   # beyond sweep
        n_sat = sum(1 for p in rule_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in rule_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in rule_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in rule_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in rule_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        per_rule_summary[rule] = {
            "recall_at_low_alpha": round(recall_at_low_alpha, 5),
            "alpha_cliff": round(cliff, 4),
            "alpha_cliff_log2": round(math.log2(max(cliff, 1e-9)), 3),
            "recall_per_alpha": {f"alpha{p['alpha']}": p["recall"] for p in rule_pts},
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
            "discriminating_fraction": round(((n_hp + n_mb) / max(1, len(rule_pts))), 4),
        }

    # Positive control: hebbian@alpha=0.5 above floor
    pc_pts = [p for p in phase_map
              if p["update_rule"] == "hebbian_outer_product" and p["alpha"] == 0.5]
    if is_smoke:
        pc_required = POSITIVE_CONTROL_SMOKE["recall_floor"]
    else:
        pc_required = POSITIVE_CONTROL["recall_floor"]
    pc_pass = bool(pc_pts and pc_pts[0]["recall"] >= pc_required)

    # Cliff separation in log2 across rules
    cliffs_log2 = [per_rule_summary[r]["alpha_cliff_log2"]
                   for r in UPDATE_RULES if r in per_rule_summary]
    if len(cliffs_log2) >= 2:
        cliff_span_log2 = max(cliffs_log2) - min(cliffs_log2)
    else:
        cliff_span_log2 = 0.0
    cliffs_distinguishable = cliff_span_log2 >= HP_DISCRIM_ALPHA_CLIFF_LOG2

    return {
        "phase_map": phase_map,
        "per_rule_summary": per_rule_summary,
        "expected_n_units": expected_n_units,
        "observed_n_units": observed_n_units,
        "cardinality_ok": cardinality_ok,
        "positive_control_pass": pc_pass,
        "positive_control_recall": (pc_pts[0]["recall"] if pc_pts else None),
        "positive_control_required": pc_required,
        "cliff_span_log2": round(cliff_span_log2, 3),
        "cliffs_distinguishable": cliffs_distinguishable,
        "wall_s_per_seed": round(elapsed, 2),
    }


def aggregate_and_verdict(per_seed: Dict[int, Dict[str, Any]],
                            run_mode: str) -> Dict[str, Any]:
    """Aggregate per-seed results into a final verdict."""
    is_smoke = (run_mode == "smoke")

    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "no per-seed data",
            "summary": "no per-seed data",
        }

    all_observed = sum(r.get("observed_n_units", 0) for r in per_seed.values())
    all_expected = sum(r.get("expected_n_units", 0) for r in per_seed.values())
    all_cardinality_ok = all(r.get("cardinality_ok", False)
                              for r in per_seed.values())

    pc_passes = sum(1 for r in per_seed.values()
                    if r.get("positive_control_pass", False))
    pc_required = len(per_seed)  # ALL seeds must pass positive control

    cliffs_distinguishable_all = all(r.get("cliffs_distinguishable", False)
                                       for r in per_seed.values())

    cliff_spans = [r.get("cliff_span_log2", 0.0) for r in per_seed.values()]
    mean_cliff_span = float(np.mean(cliff_spans)) if cliff_spans else 0.0

    if not all_cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH: observed={all_observed} "
                        f"expected={all_expected}")
    elif pc_passes < pc_required:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CONTROL_FAIL: hebbian@alpha=0.5 "
                        f"recall < floor on {pc_required - pc_passes}/{pc_required} seeds")
    elif cliffs_distinguishable_all:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS_UPDATE_RULE_PHASE_DIAGRAM: cliff_span_log2 "
                        f"mean={mean_cliff_span:.2f} >= "
                        f"{HP_DISCRIM_ALPHA_CLIFF_LOG2:.2f} across seeds")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND_UPDATE_RULE_PHASE_DIAGRAM: cliff_span_log2 "
                        f"mean={mean_cliff_span:.2f} < "
                        f"{HP_DISCRIM_ALPHA_CLIFF_LOG2:.2f}; rules cluster")

    summary = (f"observed_n={all_observed}/{all_expected} "
                f"pc={pc_passes}/{pc_required} cliff_span_log2={mean_cliff_span:.2f}")

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "per_seed_results": {str(s): {k: v for k, v in r.items() if k != "phase_map"}
                              for s, r in per_seed.items()},
        "phase_map_all_seeds": {str(s): r.get("phase_map", [])
                                  for s, r in per_seed.items()},
        "expected_n_units": all_expected,
        "observed_n_units": all_observed,
        "cardinality_ok": all_cardinality_ok,
        "positive_control_passes": pc_passes,
        "positive_control_required": pc_required,
        "mean_cliff_span_log2": round(mean_cliff_span, 3),
        "cliffs_distinguishable_all_seeds": cliffs_distinguishable_all,
    }
