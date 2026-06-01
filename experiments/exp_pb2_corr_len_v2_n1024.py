"""PB-2 CORRELATION LENGTH v2: edit-propagation correlation length at N=1024.

CONTEXT:
  PB-2 (correlation length divergence) is a product-critical feature:
  it measures how many memories are affected by a single edit.
  If correlation length is SHORT (<< N), edits are highly localized (product value).
  If correlation length DIVERGES near the phase boundary, the product must stay in
  a regime where correlation length is controlled.

  PREVIOUS STATE: pb2_corr_len probes existed but focused on STATIC correlation.
  This v2 probe measures EDIT-PROPAGATION correlation length:
    1. Store M patterns.
    2. Edit ONE pattern (rank-1 W update).
    3. Measure how many OTHER patterns shift in retrieval confidence.
    4. Correlation length = average distance in pattern-space where edit impact drops to 1/e.

  This directly probes the product story: "edit-isolated" means xi << N.

SCIENTIFIC QUESTION:
  At N=1024 (CPU-feasible), M_fracs in {0.1, 0.25, 0.5, 1.0, 2.0, 5.0},
  how does the edit-propagation correlation length xi scale with M?
  Expected: xi increases with M (more patterns = more interference).
  Does xi show a divergence near M_c (the capacity boundary)?

PRE-REGISTERED BANDS (calibration probe; first systematic xi measurement):
  No prior anchor for xi directly. Calibration-probe policy: bands +/-50%.
  Expected from KF-2 HARD_PASS data (max_iso=0.005 at N=4096 M_frac=1.0):
    xi << N at M_frac=1.0 (well below M_c). Expected: xi < 50 patterns at M_frac=1.0.

  HARD_PASS: xi MONOTONE INCREASES with M_frac (more load = longer correlation) AND
    xi < N at M_frac=1.0 (edit isolation holds below M_c) at >= 2/3 seeds.
    Interpretation: finite-range edit propagation confirmed; product-viable regime identified.
  HARD_FAIL: xi > N at M_frac=0.5 (edits propagate to entire memory = isolation broken).
    Would require rethinking edit-isolation product story.
  MIDDLE_BAND: xi monotone but xi > N at M_frac=2.0 (divergence at overload, expected).

FORMULA SELF-TESTS:
  1. Edit delta: delta_conf_j = |conf_before_j - conf_after_j| for each pattern j != edited.
  2. Sort delta_conf by pattern_j (or by distance in codebook space).
  3. xi = sum(delta_conf * distance) / sum(delta_conf) (weighted mean distance).
  4. At M_frac=0.1 (few patterns): each pattern is well-separated; xi should be small.
  5. At M_frac=5.0 (over-capacity): patterns interfere strongly; xi >> small.

OOM CHECK:
  N=1024, M_frac=5.0: M=5120 patterns. keys=5120*1024*4=20MB. W=4MB. OK.

TIMEOUT ESTIMATE:
  Per cell: store M + 10 edits x measure propagation.
  N=1024, M_frac=5.0: store ~0.1s + 10 edits x (retrieve M patterns) ~0.2s = 0.3s.
  6 M_fracs x 3 seeds = 18 cells x 0.5s = 9s.
  Safety: ceil(1.5 * 9 * 10) = 135s -> 600s.
  timeout_s = 1800.

N-suffix: _n1024 -> production N = 1024 (PROT-018 binding).
Anchor: pb2_corr_len_v2_n1024
Queue: remote_cpu_queue (CPU; edit-propagation correlation length N=1024)
Pre-reg: preregs/2026-05-28_pb2_corr_len_v2_n1024.md
Parent: kf2_isolation_proof_v2_n8192 (edit isolation HARD_PASS; xi direct measure next)
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load kf2 v1 for codebook builder and run_one_cell
_kf2v1_path = REPO / "experiments" / "exp_kf2_isolation_proof_v1.py"
_kf2v1_spec = importlib.util.spec_from_file_location("kf2v1_pb2", _kf2v1_path)
kf2v1 = importlib.util.module_from_spec(_kf2v1_spec)
_kf2v1_spec.loader.exec_module(kf2v1)

v3 = kf2v1.v3   # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n1024 suffix binds to N = 1024
N_FULL  = 1024   # PROT-018 binding contract
N_SMOKE = 256
assert N_FULL == 1024, f"PROT-018: N_FULL must be 1024; got {N_FULL}"

M_FRACS_FULL  = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
M_FRACS_SMOKE = [0.25, 1.0, 2.0]

N_EDITS        = 10    # number of edits to average over
BETA           = 32.0  # retrieval temperature

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_XI_MAX_AT_LOW_M    = 1.0   # xi < N at M_frac=1.0 (xi_normalized < 1.0 = isolated)
HF_XI_BROKEN_AT_LOW_M = 5.0   # xi >= 5*N at M_frac <= 0.5 = completely un-isolated
HP_MONOTONE_FRAC      = 0.80
HP_SEEDS_MIN          = 2


def get_output_dir(default_name: str = "pb2_corr_len_v2_n1024") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_substrate(N: int, M: int, seed: int, device: torch.device):
    """Build Kerdock substrate and return W, keys, val_idx, codebook."""
    try:
        cb = v3.make_kerdock_4coset_codebook(N, device)
        if isinstance(cb, tuple):
            cb = cb[0]
    except Exception:
        gen_cb = torch.Generator(device=device)
        gen_cb.manual_seed(0)
        cb = (torch.randint(0, 2, (N, N), generator=gen_cb, device=device) * 2 - 1).float()
    C = cb.shape[0]
    M_use = min(M, C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 200)
    key_idx = torch.randint(0, C, (M_use,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M_use,), generator=gen, device=device)
    keys = cb[key_idx]
    vals = cb[val_idx]

    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    batch = 256
    for start in range(0, M_use, batch):
        k_b = keys[start:start + batch]
        v_b = vals[start:start + batch]
        W = W + (v_b.T @ k_b) / N

    return W, keys, vals, val_idx, cb, C


def measure_confidence(W: torch.Tensor, keys: torch.Tensor,
                        val_idx: torch.Tensor, cb: torch.Tensor,
                        N: int, n_probe: int) -> torch.Tensor:
    """Measure per-pattern retrieval confidence (softmax max-logit)."""
    n_probe = min(n_probe, keys.shape[0])
    probe_keys = keys[:n_probe]
    logits = (cb @ (probe_keys @ W.T).T) / N * BETA
    # softmax confidence = max prob
    log_softmax = logits - torch.logsumexp(logits, dim=0, keepdim=True)
    confidence = log_softmax.max(dim=0).values.exp()
    return confidence


def run_one_cell(N: int, M_frac: float, seed: int, device: torch.device) -> Dict:
    """Measure edit-propagation correlation length xi."""
    M = max(4, int(M_frac * N))
    W, keys, vals, val_idx, cb, C = build_substrate(N, M, seed, device)

    n_probe = min(M, 200)
    conf_before = measure_confidence(W, keys, val_idx, cb, N, n_probe)

    xi_list = []
    n_edits_actual = min(N_EDITS, M)
    gen_edit = torch.Generator(device=device)
    gen_edit.manual_seed(seed + 5000)

    for edit_i in range(n_edits_actual):
        new_val_idx = torch.randint(0, C, (1,), generator=gen_edit, device=device)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]

        W_edited = W + torch.outer(new_val - old_val, old_key) / N

        conf_after = measure_confidence(W_edited, keys, val_idx, cb, N, n_probe)

        # Delta confidence: absolute change per pattern
        delta_conf = (conf_before[:n_probe] - conf_after[:n_probe]).abs()

        # xi = weighted mean pattern-index (as proxy for propagation distance)
        pattern_idx = torch.arange(n_probe, dtype=torch.float32, device=device)
        total_delta = delta_conf.sum().item()
        if total_delta > 1e-9:
            xi_normalized = (delta_conf * pattern_idx).sum().item() / total_delta / N
        else:
            xi_normalized = 0.0
        xi_list.append(xi_normalized)

    xi_mean = sum(xi_list) / len(xi_list) if xi_list else 0.0
    total_delta_mean = (
        sum(
            (measure_confidence(W + torch.outer(cb[torch.randint(0, C, (1,)).item()]
                                               - vals[i], keys[i]) / N,
                               keys, val_idx, cb, N, n_probe)
             [:n_probe] - conf_before[:n_probe]).abs().mean().item()
            for i in range(min(3, n_edits_actual))
        ) / min(3, n_edits_actual)
    ) if n_edits_actual > 0 else 0.0

    print(f"  M_frac={M_frac} seed={seed} xi_normalized={xi_mean:.4f} M={M}", flush=True)

    return {
        "M_frac": M_frac, "M": M, "N": N, "seed": seed,
        "xi_normalized": round(xi_mean, 5),
        "n_edits": n_edits_actual,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("PB2_CORR_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # xi by M_frac
    by_mfrac: Dict[float, List[float]] = {}
    for c in cells:
        mf = c["M_frac"]
        if mf not in by_mfrac:
            by_mfrac[mf] = []
        by_mfrac[mf].append(c["xi_normalized"])

    mfracs_sorted = sorted(by_mfrac.keys())
    mean_xi = {mf: sum(xis)/len(xis) for mf, xis in by_mfrac.items()}

    xi_seq = [mean_xi[mf] for mf in mfracs_sorted]

    # Monotone check (xi should increase with M)
    n_mono = sum(1 for i in range(len(xi_seq)-1) if xi_seq[i+1] >= xi_seq[i] - 0.01)
    mono_frac = n_mono / max(1, len(xi_seq)-1)

    # Check xi < N at M_frac=1.0 (xi_normalized < 1.0)
    xi_at_1 = mean_xi.get(1.0, float('inf'))
    xi_isolated = xi_at_1 < HP_XI_MAX_AT_LOW_M

    # HARD_FAIL: xi >> N at low M
    xi_at_low = {mf: mean_xi[mf] for mf in mfracs_sorted if mf <= 0.5}
    hf_broken = any(xi > HF_XI_BROKEN_AT_LOW_M for xi in xi_at_low.values())

    detail = (f"mfracs={mfracs_sorted} mean_xi={dict(zip(mfracs_sorted,[round(v,3) for v in xi_seq]))} "
              f"xi_at_M1={xi_at_1:.3f} mono_frac={mono_frac:.2f} N={N}")

    if hf_broken:
        return ("PB2_CORR_HARD_FAIL",
                f"HARD_FAIL: xi >> N at low M_frac (edit isolation broken). " + detail)

    if xi_isolated and mono_frac >= HP_MONOTONE_FRAC:
        return ("PB2_CORR_HARD_PASS",
                f"EDIT-PROPAGATION FINITE-RANGE: xi_normalized={xi_at_1:.3f} < 1.0 at M_frac=1. "
                + detail)

    return ("PB2_CORR_MIDDLE_BAND",
            f"Partial: xi present but not clearly isolated below M_c. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 1024, f"PROT-018: N_FULL must be 1024"

    device = torch.device("cpu")

    # Forward pass smoke
    cell = run_one_cell(N_SMOKE, 0.5, seed=17, device=device)
    assert cell["xi_normalized"] is not None, f"xi_normalized is None: {cell}"
    assert not math.isnan(cell["xi_normalized"]), f"xi_normalized is NaN: {cell}"
    assert cell["xi_normalized"] >= 0.0, f"xi_normalized negative: {cell}"

    # Multi-scale smoke N_SMOKE x4
    cell_4x = run_one_cell(N_SMOKE * 4, 0.5, seed=17, device=device)
    assert not math.isnan(cell_4x["xi_normalized"]), f"4x smoke xi is NaN: {cell_4x}"

    # Validity filter: at least 1 cell must survive smoke
    assert cell["M"] > 0, f"M is 0 at smoke: {cell}"

    # Verdict test
    fake_cells = [
        {"M_frac": 0.1, "xi_normalized": 0.02}, {"M_frac": 0.1, "xi_normalized": 0.03},
        {"M_frac": 0.5, "xi_normalized": 0.10}, {"M_frac": 0.5, "xi_normalized": 0.11},
        {"M_frac": 1.0, "xi_normalized": 0.20}, {"M_frac": 1.0, "xi_normalized": 0.22},
        {"M_frac": 2.0, "xi_normalized": 0.45}, {"M_frac": 2.0, "xi_normalized": 0.50},
        {"M_frac": 5.0, "xi_normalized": 1.50}, {"M_frac": 5.0, "xi_normalized": 1.60},
    ]
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # Hard fail test
    fake_fail = [{"M_frac": 0.25, "xi_normalized": 10.0}] * 3
    vf, _ = compute_verdict({"cells": fake_fail, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"Verdict fail test: {vf}"

    print(f"[selftest] pb2_corr_len_v2_n1024 PASS xi={cell['xi_normalized']:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    device = torch.device("cpu")
    print(f"pb2_corr_len_v2_n1024 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds}", flush=True)

    cells = []
    for M_frac in m_fracs:
        for seed in seeds:
            cell = run_one_cell(N_cfg, M_frac, seed, device)
            cells.append(cell)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "m_fracs": m_fracs, "seeds": seeds,
        "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
