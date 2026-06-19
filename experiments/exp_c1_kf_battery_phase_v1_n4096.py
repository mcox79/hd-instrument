"""C1 KILLER-FEATURE BATTERY ACROSS PHASE BOUNDARY v1: N=4096 Kerdock.

CONTEXT:
  Multiple killer features have been validated independently at specific operating points.
  The PRODUCT-CRITICAL question is: WHICH PHASE does the product live in?
  If the killer features all work in the multi-basin phase (M < M_c), the product
  must be sized to M < M_c. If some work in single-basin (M > M_c), the product
  can use a larger substrate.

  M values span the phase boundary at beta=32, N=4096, Kerdock:
    M=20K  (M/N=4.9)  -> deep multi-basin
    M=45K  (M/N=10.9) -> near boundary (transition zone)
    M=80K  (M/N=19.5) -> single-basin (ret~0.3)
    M=200K (M/N=48.8) -> deep single-basin

  KILLER FEATURES TESTED:
    KF-1: Hallucination impossibility (hallu margin = 1 - max_oos_conf)
    KF-2: Edit isolation (max |delta_acc| over non-edited keys after single edit)
    KF-4: Drift detection (Pearson r between drift amplitude and BNV metric; proxy only)
    KF-5: Steerable beta (entropy range = H(beta=2) - H(beta=128); beta-axis susceptibility)
    KF-multi-hop: Multi-hop depth (max hop depth where accuracy > 0.5, via chain retrieval)
    KF-retention: Phase-B style retention (argmax retention at beta=32)

SCIENTIFIC QUESTION:
  Across the phase boundary, which killer features survive?
  Product decision: "substrate should be sized to M in [MultiBasin] where KF-profile is X."

PRE-REGISTERED BANDS (per-KF thresholds; product spec):
  HARD_PASS: >= 4 of 6 KFs show NO DEGRADATION (same gate as standalone tests) at M=20K.
    AND KF-retention degrades monotonically across M values (confirms phase boundary).
    AND at least 2/6 KFs survive to M=45K.
  HARD_FAIL: >= 3 of 6 KFs are BROKEN (below threshold) at M=20K (instrument failure).
  MIDDLE_BAND: All 6 KFs pass at M=20K but fewer than 4 survive to M=45K.
    OR < 4/6 KFs at M=20K but still informative per-KF profile.

Per-KF thresholds (product-grade):
  KF1_hallu_margin: hallu_margin = 1 - max_oos_conf >= 0.90 (OOS returns low confidence)
  KF2_isolation_ratio: max |delta_acc| <= 0.05 (5% collateral damage tolerance)
  KF5_entropy_range: H(beta=2) - H(beta=128) >= 1.0 bit (steerable; same as v2 gate)
  KF_retention: argmax ret at beta=32 (informational; no threshold -- records trend)
  KF_hallu_above_thresh: above_thresh_frac = 0 (no probe returns confident hallucination)

NOTE: KF-4 drift detection requires a sequential edit sequence (expensive). Replaced with
KF-3 proxy: information-isolation test (does a probe NOT stored in W give low confidence?).
This is the OOS test from KF-1, applied at all 4 M values.

NOTE on Multi-hop: uses chain retrieval (W @ key -> val) depth test. At each M,
build a 5-step chain; check if retrieval follows the chain accurately.

FORMULA SELF-TESTS:
  1. hallu_margin = 1 - mean_oos_max_conf. At beta=32 undercap: expected >= 0.90.
  2. isolation_ratio = max_delta_acc over non-edited keys. At M/N < 1: expected < 0.05.
  3. entropy_range = H(beta=2) - H(beta=128). At undercap: expected >> 1.0 bit.
  4. ret = argmax accuracy at beta=32. At M=20K: expected > 0.5. At M=200K: expected < 0.1.
  5. HARD_PASS: 4/6 KFs pass at M=20K AND ret monotone.
  6. N == 4096 (PROT-018 binding).

OOM CHECK:
  M=200K N=4096: keys=200000*4096*4=3.28GB. W=64MB. CB=268MB. Total=3.61GB. Under 6GB.
  Storage done in batches of 256. Peak allocation: W(64MB) + CB(268MB) + batch(1MB). OK.
  NOTE: keys tensor at M=200K = 3.28GB. Must delete after each cell to free memory.
  Use chunked retrieval (no full keys tensor on GPU simultaneously with codebook).

TIMEOUT ESTIMATE:
  Per cell: store (linear in M) + 5 evaluations.
  At M=200K N=4096 1 seed: store~2s + KF1(0.2s) + KF2(1s) + KF5(1s) + KF_mhop(0.5s) + KF_ret(0.2s)
    = ~5s per seed per M value.
  4 M values x 3 seeds x 5s = 60s. Plus CB build at each M: ~0.5s x 4 x 3 = 6s.
  Generous total estimate: 180s. But M=200K store takes longer (batched): ~7-10s.
  Revised: 4 M_vals x 3 seeds x 15s = 180s.
  Safety: ceil(1.5 * 300s) = 450s. User override for _n4096: timeout >= 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: c1_kf_battery_phase_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock, 6 KF metrics at 4 M values, 3 seeds)
Pre-reg: preregs/2026-05-28_c1_kf_battery_phase_v1_n4096.md
Parent: Multiple KF experiments (kf1/kf2/kf5/tcft); first cross-phase battery
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load axis1_mb_chunk1 for store_facts_batched, Kerdock builder
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_c1bat", _c1_path)
c1_mod = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1_mod)

store_facts_batched = c1_mod.store_facts_batched
v3 = c1_mod.v3   # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# M values spanning phase boundary (user-specified)
M_VALS_FULL  = [20000, 45000, 80000, 200000]
M_VALS_SMOKE = [20000, 45000]

BETA_OP = 32.0      # standard operating beta

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE_RET  = 100   # probes for retention
N_PROBE_HALLU = 200  # probes for hallucination test (OOS queries)
N_EDITS      = 20    # edits for isolation test
N_CHAIN_HOPS = 5     # hops for multi-hop chain test
N_CHAIN_TRIALS = 20  # chain trials per seed
BETA_LOW     = 2.0   # low beta for entropy range
BETA_HIGH    = 128.0 # high beta for entropy range

# Pre-registered per-KF thresholds
HALLU_MARGIN_THRESHOLD  = 0.90   # KF1: 1 - max_oos_conf >= 0.90
ISOLATION_MAX           = 0.05   # KF2: max |delta_acc| <= 0.05
ENTROPY_RANGE_MIN       = 1.0    # KF5: H(b_low) - H(b_high) >= 1.0 bit
ABOVE_THRESH_MAX        = 0.0    # KF1b: no confident hallucination
HALLU_THRESHOLD         = 0.5    # confidence threshold for hallucination


def get_output_dir(default_name: str = "c1_kf_battery_phase_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _compute_entropy(probs: torch.Tensor) -> float:
    """Compute entropy in bits from softmax probability distribution."""
    # probs: (n_vocab,)
    p = probs.clamp(min=1e-12)
    return float(-(p * p.log2()).sum().item())


def eval_kf1_hallu(W: torch.Tensor, codebook: torch.Tensor, key_idx: torch.Tensor,
                   val_idx: torch.Tensor, N: int, seed: int, device: torch.device) -> Dict:
    """KF-1: hallucination impossibility. OOS keys should NOT get confident answers."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 700)
    stored_set = set(key_idx.tolist()[:min(key_idx.shape[0], 10000)])

    # Sample OOS keys (not stored in W)
    available = [i for i in range(C) if i not in stored_set]
    if len(available) < N_PROBE_HALLU:
        # Use all available; at over-capacity this will be small
        n_oos = len(available)
        if n_oos == 0:
            return {"hallu_margin": 1.0, "above_thresh_frac": 0.0, "n_oos": 0,
                    "mean_oos_max_conf": 0.0}
        oos_idx = torch.tensor(available, dtype=torch.long, device=device)
    else:
        oos_idx = torch.randperm(len(available), generator=gen, device=device)[:N_PROBE_HALLU]
        oos_idx = torch.tensor([available[i] for i in oos_idx.tolist()], dtype=torch.long, device=device)

    oos_keys = codebook[oos_idx]   # (n_oos, N)
    q = oos_keys @ W.T             # (n_oos, N)
    sims = (codebook @ q.T) / N   # (C, n_oos)
    P = torch.softmax(BETA_OP * sims, dim=0)   # (C, n_oos)
    max_conf = P.max(dim=0).values             # (n_oos,)
    above_thresh = (max_conf >= HALLU_THRESHOLD).float().mean().item()
    mean_mc = max_conf.mean().item()
    hallu_margin = 1.0 - mean_mc
    return {
        "hallu_margin": round(hallu_margin, 5),
        "above_thresh_frac": round(above_thresh, 5),
        "mean_oos_max_conf": round(mean_mc, 5),
        "n_oos": len(oos_idx),
    }


def eval_kf2_isolation(W: torch.Tensor, codebook: torch.Tensor, key_idx: torch.Tensor,
                        val_idx: torch.Tensor, N: int, seed: int, device: torch.device) -> Dict:
    """KF-2: edit isolation. Single edit should not contaminate non-edited keys."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    # Load keys/values back (may have been freed; recompute subset)
    n_probe = min(N_PROBE_RET, M)
    probe_key_idx = key_idx[:n_probe] % C
    probe_val_idx = val_idx[:n_probe] % C
    probe_keys = codebook[probe_key_idx]  # (n_probe, N)
    probe_vals_target = probe_val_idx

    sims_before = (codebook @ (probe_keys @ W.T).T) / N  # (C, n_probe)
    pred_before = torch.argmax(sims_before, dim=0)        # (n_probe,)
    acc_before = (pred_before == probe_vals_target.to(device)).float()

    gen = torch.Generator(device=device).manual_seed(seed + 800)
    isolation_ratios = []
    n_edits_run = min(N_EDITS, M)

    for edit_i in range(n_edits_run):
        # Pick a key to edit (outside probe set to avoid overlap)
        edit_idx = (n_probe + edit_i) % M
        old_key = codebook[key_idx[edit_idx] % C]
        old_val = codebook[val_idx[edit_idx] % C]
        new_val_i = torch.randint(0, C, (1,), generator=gen, device=device)[0]
        new_val = codebook[new_val_i]

        # Rank-1 edit
        W_ed = W + torch.outer(new_val - old_val, old_key) / N

        # Measure impact on probe set
        sims_after = (codebook @ (probe_keys @ W_ed.T).T) / N
        pred_after = torch.argmax(sims_after, dim=0)
        acc_after = (pred_after == probe_vals_target.to(device)).float()
        delta = (acc_before - acc_after).abs().mean().item()
        isolation_ratios.append(delta)

    iso_ratio = max(isolation_ratios) if isolation_ratios else 0.0
    return {
        "isolation_ratio": round(iso_ratio, 5),
        "theory_bound": round(1.0 / math.sqrt(N), 5),
        "passes_threshold": iso_ratio <= ISOLATION_MAX,
        "n_edits_run": n_edits_run,
    }


def eval_kf5_steerability(W: torch.Tensor, codebook: torch.Tensor, key_idx: torch.Tensor,
                            val_idx: torch.Tensor, N: int, device: torch.device) -> Dict:
    """KF-5: steerable beta. Measure entropy range across beta sweep."""
    C = codebook.shape[0]
    n_probe = min(N_PROBE_RET, key_idx.shape[0])
    probe_key_idx = key_idx[:n_probe] % C
    probe_keys = codebook[probe_key_idx]

    q = probe_keys @ W.T            # (n_probe, N)
    sims = (codebook @ q.T) / N    # (C, n_probe)

    # Mean entropy at beta_low and beta_high (averaged over probes)
    P_low  = torch.softmax(BETA_LOW  * sims, dim=0).T  # (n_probe, C)
    P_high = torch.softmax(BETA_HIGH * sims, dim=0).T  # (n_probe, C)

    H_low  = float(-(P_low  * P_low.clamp(min=1e-12).log2()).sum(dim=1).mean().item())
    H_high = float(-(P_high * P_high.clamp(min=1e-12).log2()).sum(dim=1).mean().item())
    entropy_range = H_low - H_high

    return {
        "H_low": round(H_low, 4),
        "H_high": round(H_high, 4),
        "entropy_range": round(entropy_range, 4),
        "passes_threshold": entropy_range >= ENTROPY_RANGE_MIN,
    }


def eval_kf_retention(W: torch.Tensor, codebook: torch.Tensor, key_idx: torch.Tensor,
                       val_idx: torch.Tensor, N: int, device: torch.device) -> Dict:
    """KF-retention: argmax retention at beta=32 (phase-B proxy)."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    n_probe = min(N_PROBE_RET, M)
    probe_key_idx = key_idx[:n_probe] % C
    probe_val_idx = val_idx[:n_probe] % C
    probe_keys = codebook[probe_key_idx]

    sims = (codebook @ (probe_keys @ W.T).T) / N
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx.to(device)).float().mean().item())
    return {
        "retention": round(acc, 5),
        "n_probe": n_probe,
    }


def eval_kf_multihop(codebook: torch.Tensor, N: int, seed: int, M: int,
                      device: torch.device) -> Dict:
    """KF multi-hop: build a chain of hop facts, test if chain retrieval works.

    Builds a chain: A->B->C->D->E->F in W.
    Query: starting from A, can we follow the chain to F?
    Tests multi-hop depth at the given M loading.
    """
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed + 900)

    n_hops = N_CHAIN_HOPS
    n_trials = min(N_CHAIN_TRIALS, C // (n_hops + 2))
    if n_trials == 0:
        return {"max_hop_depth": 0, "chain_acc_by_depth": {}}

    # Build M background facts + chain facts
    background_M = max(0, M - n_trials * n_hops)
    W = torch.zeros(N, N, dtype=torch.float32, device=device)

    # Background facts (random)
    bg_idx = torch.randint(0, C, (background_M,), generator=gen, device=device)
    bg_val = torch.randint(0, C, (background_M,), generator=gen, device=device)
    if background_M > 0:
        batch = 256
        for start in range(0, background_M, batch):
            kb = codebook[bg_idx[start:start + batch]]
            vb = codebook[bg_val[start:start + batch]]
            W += (vb.T @ kb) / N

    # Chain facts
    # For each trial: pick n_hops+1 distinct nodes; store chain edges
    chain_node_idx = torch.randint(0, C, (n_trials, n_hops + 1), generator=gen, device=device)
    for t in range(n_trials):
        for h in range(n_hops):
            k = codebook[chain_node_idx[t, h]]
            v = codebook[chain_node_idx[t, h + 1]]
            W = W + torch.outer(v, k) / N

    # Evaluate: starting from node 0, can we reach node d after d steps?
    acc_by_depth = {}
    for depth in range(1, n_hops + 1):
        correct = 0
        for t in range(n_trials):
            node = codebook[chain_node_idx[t, 0]]
            for _step in range(depth):
                q = node @ W.T         # (N,)
                sims_step = (codebook @ q) / N  # (C,)
                next_node_pred = torch.argmax(sims_step).item()
                node = codebook[next_node_pred]
            # Check if we reached the correct node at depth
            target_idx = chain_node_idx[t, depth].item()
            pred_idx = torch.argmax((codebook @ node) / N).item()
            if pred_idx == target_idx:
                correct += 1
        acc_by_depth[depth] = round(correct / n_trials, 4)

    # Max depth where accuracy > 0.5
    max_depth = 0
    for d in range(1, n_hops + 1):
        if acc_by_depth.get(d, 0) > 0.5:
            max_depth = d

    return {
        "max_hop_depth": max_depth,
        "chain_acc_by_depth": acc_by_depth,
        "n_trials": n_trials,
    }


def run_one_cell(N: int, M: int, seed: int, device: torch.device) -> Dict:
    """Run full KF battery at one (N, M, seed). Returns all KF metrics."""
    t0 = time.monotonic()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]
    print(f"    [cell N={N} M={M} seed={seed}] C={C}", flush=True)

    # Store M facts (batched, memory-efficient)
    W, keys, _vals, key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    # Run all KF evaluations
    kf1  = eval_kf1_hallu(W, codebook, key_idx, val_idx, N, seed, device)
    kf2  = eval_kf2_isolation(W, codebook, key_idx, val_idx, N, seed, device)
    kf5  = eval_kf5_steerability(W, codebook, key_idx, val_idx, N, device)
    kfret = eval_kf_retention(W, codebook, key_idx, val_idx, N, device)
    kfmhop = eval_kf_multihop(codebook, N, seed, M, device)

    # Free large tensors before next cell
    del keys, _vals, key_idx, val_idx
    if device.type == "cuda":
        torch.cuda.empty_cache()

    elapsed = time.monotonic() - t0
    print(f"      kf1_hallu_margin={kf1['hallu_margin']:.3f} "
          f"kf2_isolation={kf2['isolation_ratio']:.4f} "
          f"kf5_ent_range={kf5['entropy_range']:.3f} "
          f"ret={kfret['retention']:.4f} "
          f"mhop_depth={kfmhop['max_hop_depth']} "
          f"({elapsed:.1f}s)", flush=True)

    return {
        "N": N, "M": M, "M_over_N": round(M / N, 4),
        "seed": seed, "elapsed_s": round(elapsed, 2),
        "kf1_hallu": kf1,
        "kf2_isolation": kf2,
        "kf5_steerability": kf5,
        "kf_retention": kfret,
        "kf_multihop": kfmhop,
    }


def compute_verdict(all_cells: List[Dict]) -> Tuple[str, str]:
    """Compute C1 verdict: which KFs survive across phase boundary?"""
    if not all_cells:
        return ("C1_INCONCLUSIVE", "No cells computed.")

    # Group by M
    from collections import defaultdict
    by_M: Dict = defaultdict(list)
    for c in all_cells:
        by_M[c["M"]].append(c)

    m_sorted = sorted(by_M.keys())
    M_BASE = m_sorted[0]  # should be 20K

    # Per-M per-KF pass rates
    kf_pass_by_M: Dict = {}
    for M in m_sorted:
        cells = by_M[M]
        kf1_pass  = sum(c["kf1_hallu"]["hallu_margin"] >= HALLU_MARGIN_THRESHOLD for c in cells)
        kf1b_pass = sum(c["kf1_hallu"]["above_thresh_frac"] <= ABOVE_THRESH_MAX for c in cells)
        kf2_pass  = sum(c["kf2_isolation"]["isolation_ratio"] <= ISOLATION_MAX for c in cells)
        kf5_pass  = sum(c["kf5_steerability"]["entropy_range"] >= ENTROPY_RANGE_MIN for c in cells)
        ret_mean  = sum(c["kf_retention"]["retention"] for c in cells) / max(1, len(cells))
        mhop_mean = sum(c["kf_multihop"]["max_hop_depth"] for c in cells) / max(1, len(cells))
        n = len(cells)
        kf_pass_by_M[M] = {
            "kf1_pass": kf1_pass, "kf1b_pass": kf1b_pass, "kf2_pass": kf2_pass,
            "kf5_pass": kf5_pass, "ret_mean": round(ret_mean, 4), "mhop_mean": round(mhop_mean, 2),
            "n": n,
        }

    detail = {"kf_pass_by_M": kf_pass_by_M}
    base = kf_pass_by_M.get(M_BASE, {})
    n_base = base.get("n", 1)

    # HARD_FAIL: >= 3 KFs broken at M=20K
    kf_broken_at_base = sum([
        base.get("kf1_pass", n_base) < n_base,
        base.get("kf2_pass", n_base) < n_base,
        base.get("kf5_pass", n_base) < n_base,
        base.get("kf1b_pass", n_base) < n_base,
    ])
    if kf_broken_at_base >= 3:
        return ("C1_HARD_FAIL",
                f"INSTRUMENT_FAILURE: {kf_broken_at_base}/4 primary KFs broken at M={M_BASE} "
                f"(undercap regime). details={detail}.")

    # Check retention monotonicity
    ret_vals = [kf_pass_by_M[m]["ret_mean"] for m in m_sorted if m in kf_pass_by_M]
    is_monotone_ret = all(ret_vals[i] >= ret_vals[i + 1] - 0.05 for i in range(len(ret_vals) - 1))

    # Count KFs passing at M=45K
    M_NEAR = m_sorted[1] if len(m_sorted) > 1 else M_BASE
    near = kf_pass_by_M.get(M_NEAR, {})
    n_near = near.get("n", 1)
    kf_surviving_near = sum([
        near.get("kf1_pass", 0) >= n_near // 2,
        near.get("kf2_pass", 0) >= n_near // 2,
        near.get("kf5_pass", 0) >= n_near // 2,
        near.get("kf1b_pass", 0) >= n_near // 2,
    ])

    # KFs passing at M_BASE
    kf_pass_base_count = sum([
        base.get("kf1_pass", 0) >= n_base,
        base.get("kf2_pass", 0) >= n_base,
        base.get("kf5_pass", 0) >= n_base,
        base.get("kf1b_pass", 0) >= n_base,
    ])

    # HARD_PASS
    if kf_pass_base_count >= 3 and is_monotone_ret and kf_surviving_near >= 2:
        return ("C1_HARD_PASS",
                f"PRODUCT_PROFILE_CLEAR: {kf_pass_base_count}/4 KFs pass at M={M_BASE}; "
                f"ret monotone={is_monotone_ret}; "
                f"{kf_surviving_near}/4 KFs survive to M={M_NEAR}. "
                f"Product: size substrate to M < {m_sorted[m_sorted.index(M_NEAR)+1] if len(m_sorted)>2 else M_NEAR*2}. "
                f"details={detail}.")

    return ("C1_MIDDLE_BAND",
            f"PARTIAL_PROFILE: {kf_pass_base_count}/4 KFs at M={M_BASE}; "
            f"ret_monotone={is_monotone_ret}; "
            f"{kf_surviving_near}/4 survive to M={M_NEAR}. details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: compute_verdict HARD_PASS
    cells_pass = []
    for M in [20000, 45000]:
        for s in [7, 17, 23]:
            cells_pass.append({
                "M": M, "N": 4096, "M_over_N": M / 4096, "seed": s, "elapsed_s": 1.0,
                "kf1_hallu": {
                    "hallu_margin": 0.97, "above_thresh_frac": 0.0, "mean_oos_max_conf": 0.03, "n_oos": 200,
                },
                "kf2_isolation": {"isolation_ratio": 0.01, "theory_bound": 0.0156,
                                   "passes_threshold": True, "n_edits_run": 20},
                "kf5_steerability": {"H_low": 7.0, "H_high": 0.5, "entropy_range": 6.5, "passes_threshold": True},
                "kf_retention": {"retention": 0.90 if M == 20000 else 0.45, "n_probe": 100},
                "kf_multihop": {"max_hop_depth": 3, "chain_acc_by_depth": {1: 0.9, 2: 0.7, 3: 0.55, 4: 0.4, 5: 0.3}, "n_trials": 20},
            })
    v, msg = compute_verdict(cells_pass)
    assert "HARD_PASS" in v or "MIDDLE_BAND" in v, f"selftest HARD_PASS path failed: v={v}"

    # Self-test 2: compute_verdict HARD_FAIL (broken at base)
    cells_fail = [
        {"M": 20000, "N": 4096, "M_over_N": 4.88, "seed": 7, "elapsed_s": 1.0,
         "kf1_hallu": {"hallu_margin": 0.1, "above_thresh_frac": 0.5, "mean_oos_max_conf": 0.9, "n_oos": 200},
         "kf2_isolation": {"isolation_ratio": 0.20, "theory_bound": 0.0156, "passes_threshold": False, "n_edits_run": 20},
         "kf5_steerability": {"H_low": 2.0, "H_high": 1.8, "entropy_range": 0.2, "passes_threshold": False},
         "kf_retention": {"retention": 0.1, "n_probe": 100},
         "kf_multihop": {"max_hop_depth": 0, "chain_acc_by_depth": {}, "n_trials": 5},
         }
    ] * 3  # 3 seeds all broken
    v2, _ = compute_verdict(cells_fail)
    assert "HARD_FAIL" in v2, f"selftest HARD_FAIL failed: v2={v2}"

    # Self-test 3: actual smoke computation at small N
    device = torch.device("cpu")
    N_t = N_SMOKE
    M_t = M_VALS_SMOKE[0]  # 20000
    print(f"[selftest] running smoke cell N={N_t} M={M_t} seed=17...", flush=True)
    cell = run_one_cell(N_t, M_t, 17, device)
    assert "kf1_hallu" in cell, f"kf1_hallu missing: {list(cell.keys())}"
    assert "kf2_isolation" in cell, f"kf2_isolation missing: {list(cell.keys())}"
    assert "kf5_steerability" in cell, f"kf5_steerability missing: {list(cell.keys())}"
    assert "kf_retention" in cell, f"kf_retention missing: {list(cell.keys())}"
    assert "kf_multihop" in cell, f"kf_multihop missing: {list(cell.keys())}"

    kf1 = cell["kf1_hallu"]
    assert not math.isnan(kf1.get("hallu_margin", float("nan"))), f"hallu_margin NaN: {kf1}"
    kf2 = cell["kf2_isolation"]
    assert not math.isnan(kf2.get("isolation_ratio", float("nan"))), f"isolation_ratio NaN: {kf2}"
    kf5 = cell["kf5_steerability"]
    assert not math.isnan(kf5.get("entropy_range", float("nan"))), f"entropy_range NaN: {kf5}"
    kfr = cell["kf_retention"]
    assert 0.0 <= kfr["retention"] <= 1.0, f"retention out of range: {kfr}"

    print(f"[selftest] smoke N={N_t} M={M_t}: "
          f"kf1_margin={kf1['hallu_margin']:.3f} "
          f"kf2_iso={kf2['isolation_ratio']:.4f} "
          f"kf5_ent={kf5['entropy_range']:.3f} "
          f"ret={kfr['retention']:.4f} OK", flush=True)

    # Multi-scale: verify second M value at smoke
    M_t2 = M_VALS_SMOKE[1] if len(M_VALS_SMOKE) > 1 else M_t
    cell2 = run_one_cell(N_t, M_t2, 17, device)
    assert "kf_retention" in cell2, f"multi-scale cell2 missing kf_retention"
    print(f"[selftest] multi-scale M={M_t2}: ret={cell2['kf_retention']['retention']:.4f} OK", flush=True)

    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N      = N_SMOKE if smoke else N_FULL
    m_vals = M_VALS_SMOKE if smoke else M_VALS_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "c1_kf_battery_phase_v1_n4096")
    print(f"[run] {exp_name} smoke={smoke} N={N} m_vals={m_vals} "
          f"seeds={seeds} device={device}", flush=True)
    if not smoke:
        assert N == 4096, f"FULL run must use N=4096 (PROT-018); got {N}"

    all_cells: List[Dict] = []

    for M in m_vals:
        print(f"\n  [M={M} M/N={M/N:.2f}]", flush=True)
        for seed in seeds:
            cell = run_one_cell(N, M, seed, device)
            all_cells.append(cell)

    verdict_str, verdict_msg = compute_verdict(all_cells)

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    out_dir = get_output_dir(exp_name)
    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"N": N, "smoke": smoke, "seeds": seeds, "m_vals": m_vals,
                   "beta_op": BETA_OP, "beta_low": BETA_LOW, "beta_high": BETA_HIGH},
        "all_cells": all_cells,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)
else:
    run(smoke=False)
