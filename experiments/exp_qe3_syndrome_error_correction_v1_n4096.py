"""QE-3 SYNDROME ERROR CORRECTION v1 N=4096: Kerdock parity-check active correction.

PARENT: exp_kf2_isolation_proof_v2_n4096_audit.py -- KF-2 isolation proof Kerdock-safe at N=4096.
  We reuse the Kerdock codebook + outer-product W substrate but add a
  syndrome-measurement / parity-check layer that detects retrieval inconsistency
  and runs a masked re-retrieval correction step.

SCIENTIFIC QUESTION:
  Quantum-error-correction analog: after retrieval, measure Kerdock parity-check
  observables on the retrieved codeword. If the parity is violated (codeword does NOT
  satisfy the stored Kerdock structure within the syndrome threshold), run a correction
  step (re-retrieve with the violating cell index masked from the codebook).

  Does syndrome-driven active correction reduce operational error rate (mismatched
  retrieval against stored val) at borderline M_frac vs uncorrected baseline?

PRE-REGISTERED BANDS (envelope-fail-bands; HP/HF/MIDDLE explicitly pre-committed):
  Baseline = single-pass Kerdock retrieval at M_frac=4 (borderline / over-capacity).
  Corrected = same retrieval + syndrome check + 1 masked re-retrieve on violation.

  Operational error rate = fraction of probes where final argmax codeword != stored val.

  HARD_PASS: syndrome correction reduces operational error rate by >= 0.50 absolute
    averaged across >= 2/3 seeds (e.g. baseline err=0.60 -> corrected err <= 0.10).
  HARD_FAIL: < 0.10 absolute reduction on >= 2/3 seeds (correction barely helps).
  MIDDLE_BAND: reduction in [0.10, 0.50) on >= 2/3 seeds (partial benefit).

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding). C = 4*N = 16384.
  2. Kerdock parity-check observable = inner-product agreement between retrieved
     codeword and codebook row at predicted index: <pred_vec, codebook[pred_idx]> / N.
     For a clean Kerdock 4-coset codeword this = 1.0. Threshold (default 0.95) signals
     violation when below.
  3. Operational error rate formula: err = 1 - acc = mean(pred_idx != val_idx).
  4. delta_err = err_baseline - err_corrected (positive = correction helps).
  5. Mask correction: re-run argmax over codebook[:, mask] where the violating index is
     removed; choose 2nd-best honest match.

TIMEOUT ESTIMATE:
  KF-2 v2_n4096_audit elapsed ~30s for 5 seeds x 5 M_fracs.
  We run 3 seeds x 2 modes (baseline + corrected) at single M_frac=4.0 with parity
  check + masked re-retrieve. Per-cell cost ~5s; 6 cells ~30s.
  Safety x10 for codebook reuse + GPU cold start: 300s.
  PROT-019 floor _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: qe3_syndrome_error_correction_v1_n4096
Queue: overnight_queue (GPU; Kerdock parity-check active correction probe)
Pre-reg: preregs/2026-05-29_qe3_syndrome_error_correction_v1_n4096.md
Parent: kf2_isolation_proof_v2_n4096_audit
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

# Load Kerdock substrate (codebook builder).
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_v3_spec = importlib.util.spec_from_file_location("kerdock_v3_qe3", _v3_path)
v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRAC_FULL  = 4.0
M_FRAC_SMOKE = 2.0

N_PROBES_FULL  = 500
N_PROBES_SMOKE = 50

SEEDS_FULL  = [7, 17, 23]   # 3 seeds (per spec)
SEEDS_SMOKE = [17]

# Kerdock parity-check threshold: cosine-style inner-product on normalized codewords.
# Kerdock rows are +-1 valued with row-norm sqrt(N); <a,b>/N is in [-1, 1] with 1
# being perfect match. Default threshold 0.95 = "near-perfect codeword alignment".
SYNDROME_THRESHOLD_DEFAULT = 0.95

BETA_INF = 32.0

# Pre-registered envelope-fail-bands (delta_err = err_baseline - err_corrected; positive = help).
HP_DELTA_THRESHOLD = 0.50   # absolute reduction in error rate
HF_DELTA_THRESHOLD = 0.10
MIN_SEEDS_FOR_BAND = 2      # need >= 2/3 seeds at threshold


def get_output_dir(default_name: str = "qe3_syndrome_error_correction_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_facts_outer(keys: torch.Tensor, values: torch.Tensor, N: int) -> torch.Tensor:
    """Outer-product W := sum_i (value_i outer key_i) / N. BSC-style.

    Local copy mirroring kf1v2 to keep this script's import surface minimal at FULL run."""
    M = keys.shape[0]
    device = keys.device
    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    batch = 256
    for start in range(0, M, batch):
        k_b = keys[start:start + batch]
        v_b = values[start:start + batch]
        W = W + (v_b.T @ k_b) / N
    return W


def run_one_cell(
    mode: str,
    seed: int,
    M_frac: float,
    device: torch.device,
    N: int,
    n_probes: int,
    syndrome_threshold: float,
) -> Dict:
    """One (mode, seed) cell.

    mode in {"baseline", "corrected"}:
      baseline  : single-pass Kerdock retrieval, argmax over full codebook
      corrected : same retrieval + parity check; if syndrome violated (parity < threshold),
                  re-retrieve over codebook with the violating cell index masked, then argmax.
    """
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    gen = torch.Generator(device="cpu").manual_seed(seed + 8191)
    M = int(M_frac * N)
    key_idx = torch.randint(0, C, (M,), generator=gen)
    val_idx = torch.randint(0, C, (M,), generator=gen)
    keys = codebook[key_idx].to(device)
    values = codebook[val_idx].to(device)

    W = store_facts_outer(keys, values, N)

    n_probes_actual = min(n_probes, M)
    probe_order = torch.randperm(M, generator=gen)[:n_probes_actual]
    probe_keys = keys[probe_order]                                              # (P, N)
    probe_target_idx = val_idx[probe_order].to(device)                          # (P,)

    # Single-pass retrieval.
    readout = probe_keys @ W.T                                                  # (P, N)
    sims = (codebook @ readout.T) / N                                           # (C, P)
    P_dist = torch.softmax(BETA_INF * sims, dim=0)                              # (C, P)
    pred_idx = P_dist.argmax(dim=0)                                             # (P,)

    if mode == "baseline":
        final_pred = pred_idx
        n_violations = 0
        n_corrected = 0
    elif mode == "corrected":
        # Parity check: inner-product agreement between readout and predicted codebook row.
        # Since codebook rows have +-1 values and row-norm sqrt(N), <readout, cb[pred]> / N
        # is in approximately [-1, 1]. Above threshold = parity OK.
        pred_rows = codebook[pred_idx]                                          # (P, N)
        parity = (readout * pred_rows).sum(dim=1) / N                           # (P,)
        violations = parity < syndrome_threshold                                # (P,)
        n_violations = int(violations.sum().item())

        # Correction: for each violating probe, mask the violating index and re-argmax.
        final_pred = pred_idx.clone()
        if n_violations > 0:
            viol_indices = violations.nonzero(as_tuple=True)[0]                 # (V,)
            # Per-probe masked argmax: zero out sims at the predicted index then argmax.
            sims_corrected = sims.clone()
            for j in viol_indices.tolist():
                bad_idx = int(pred_idx[j].item())
                sims_corrected[bad_idx, j] = float("-inf")
            new_pred = sims_corrected.argmax(dim=0)                             # (P,)
            final_pred[viol_indices] = new_pred[viol_indices]
            n_corrected = int((final_pred[viol_indices] != pred_idx[viol_indices]).sum().item())
        else:
            n_corrected = 0
    else:
        raise ValueError(f"Unknown mode: {mode}")

    acc = (final_pred == probe_target_idx).float().mean().item()
    err = 1.0 - acc

    return {
        "mode": mode,
        "seed": seed,
        "M_frac": M_frac,
        "M": M,
        "C": C,
        "N": N,
        "syndrome_threshold": syndrome_threshold,
        "n_probes": n_probes_actual,
        "n_violations": n_violations,
        "n_corrected": n_corrected,
        "accuracy": acc,
        "error_rate": err,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute QE-3 verdict from baseline vs corrected error rates."""
    cells = summary.get("cells", [])
    if not cells:
        return ("QE3_INCONCLUSIVE", "No cells.")

    by_mode: Dict[str, Dict[int, float]] = {}
    for c in cells:
        by_mode.setdefault(c["mode"], {})[c["seed"]] = c["error_rate"]

    if "baseline" not in by_mode or "corrected" not in by_mode:
        return ("QE3_INCONCLUSIVE", "Missing baseline or corrected cells.")

    baseline = by_mode["baseline"]
    corrected = by_mode["corrected"]
    seeds = sorted(set(baseline.keys()) & set(corrected.keys()))

    if not seeds:
        return ("QE3_INCONCLUSIVE", "No paired seeds between baseline and corrected.")

    deltas = [baseline[s] - corrected[s] for s in seeds]  # positive = correction helps
    mean_delta = sum(deltas) / len(deltas)
    mean_base = sum(baseline[s] for s in seeds) / len(seeds)
    mean_corr = sum(corrected[s] for s in seeds) / len(seeds)

    detail = (f"baseline_err={mean_base:.4f} corrected_err={mean_corr:.4f} "
              f"mean_delta={mean_delta:.4f} n_seeds={len(seeds)}")

    seeds_hp = sum(1 for d in deltas if d >= HP_DELTA_THRESHOLD)
    seeds_mid = sum(1 for d in deltas if d >= HF_DELTA_THRESHOLD)

    if seeds_hp >= MIN_SEEDS_FOR_BAND:
        return ("QE3_HARD_PASS",
                f"SYNDROME CORRECTION REDUCES ERROR by >= {HP_DELTA_THRESHOLD} absolute on "
                f"{seeds_hp}/{len(seeds)} seeds. Kerdock parity-check active-correction layer "
                f"is product-grade. " + detail)

    if seeds_mid >= MIN_SEEDS_FOR_BAND:
        return ("QE3_MIDDLE_BAND",
                f"Partial correction benefit: {seeds_mid}/{len(seeds)} seeds in "
                f"[{HF_DELTA_THRESHOLD}, {HP_DELTA_THRESHOLD}). " + detail)

    return ("QE3_HARD_FAIL",
            f"NO MEANINGFUL CORRECTION: < {HF_DELTA_THRESHOLD} absolute reduction "
            f"on >= {MIN_SEEDS_FOR_BAND}/{len(seeds)} seeds. Parity-check syndrome "
            f"does not unlock product-grade error reduction. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all formulas + verdict gates work BEFORE production sweep."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: C formula at N=4096
    C_expected = 4 * 4096
    assert C_expected == 16384, f"C formula: {C_expected}"

    # Self-test 2: error rate = 1 - accuracy identity
    acc_t = 0.37
    err_t = 1.0 - acc_t
    assert abs(err_t - 0.63) < 1e-9, f"err identity: {err_t}"

    # Self-test 3: verdict HARD_PASS path
    cells_hp = [
        {"mode": "baseline",  "seed": 7,  "error_rate": 0.60},
        {"mode": "baseline",  "seed": 17, "error_rate": 0.58},
        {"mode": "baseline",  "seed": 23, "error_rate": 0.62},
        {"mode": "corrected", "seed": 7,  "error_rate": 0.05},
        {"mode": "corrected", "seed": 17, "error_rate": 0.04},
        {"mode": "corrected", "seed": 23, "error_rate": 0.10},
    ]
    v, msg = compute_verdict({"cells": cells_hp})
    assert "HARD_PASS" in v, f"HP self-test failed: {v}: {msg}"

    # Self-test 4: verdict HARD_FAIL path
    cells_hf = [
        {"mode": "baseline",  "seed": 7,  "error_rate": 0.60},
        {"mode": "baseline",  "seed": 17, "error_rate": 0.58},
        {"mode": "baseline",  "seed": 23, "error_rate": 0.62},
        {"mode": "corrected", "seed": 7,  "error_rate": 0.55},
        {"mode": "corrected", "seed": 17, "error_rate": 0.55},
        {"mode": "corrected", "seed": 23, "error_rate": 0.58},
    ]
    v2, msg2 = compute_verdict({"cells": cells_hf})
    assert "HARD_FAIL" in v2, f"HF self-test failed: {v2}: {msg2}"

    # Self-test 5: verdict MIDDLE_BAND path
    cells_mid = [
        {"mode": "baseline",  "seed": 7,  "error_rate": 0.60},
        {"mode": "baseline",  "seed": 17, "error_rate": 0.58},
        {"mode": "baseline",  "seed": 23, "error_rate": 0.62},
        {"mode": "corrected", "seed": 7,  "error_rate": 0.40},
        {"mode": "corrected", "seed": 17, "error_rate": 0.42},
        {"mode": "corrected", "seed": 23, "error_rate": 0.45},
    ]
    v3v, msg3 = compute_verdict({"cells": cells_mid})
    assert "MIDDLE_BAND" in v3v, f"MID self-test failed: {v3v}: {msg3}"

    # Self-test 6: smoke cell forward pass at N=1024
    device = torch.device("cpu")
    cell_base = run_one_cell(
        mode="baseline",
        seed=17,
        M_frac=2.0,
        device=device,
        N=N_SMOKE,
        n_probes=20,
        syndrome_threshold=SYNDROME_THRESHOLD_DEFAULT,
    )
    assert 0.0 <= cell_base["accuracy"] <= 1.0, f"acc sentinel: {cell_base['accuracy']}"
    assert not math.isnan(cell_base["error_rate"]), "err NaN"

    cell_corr = run_one_cell(
        mode="corrected",
        seed=17,
        M_frac=2.0,
        device=device,
        N=N_SMOKE,
        n_probes=20,
        syndrome_threshold=SYNDROME_THRESHOLD_DEFAULT,
    )
    assert 0.0 <= cell_corr["accuracy"] <= 1.0, f"acc_corr sentinel: {cell_corr['accuracy']}"
    assert "n_violations" in cell_corr, "n_violations missing"

    # Self-test 7: OOM pre-check at N=4096 float32
    oom_W = N_FULL * N_FULL * 4
    assert oom_W < 6e9, f"OOM: W at N=4096 = {oom_W:.2e} >= 6GB"

    print(f"[SELFTEST PASS] qe3_syndrome_error_correction_v1_n4096: N_FULL={N_FULL} "
          f"C={C_expected} smoke_base_acc={cell_base['accuracy']:.3f} "
          f"smoke_corr_acc={cell_corr['accuracy']:.3f} "
          f"smoke_violations={cell_corr['n_violations']} verdict_gates=3/3 "
          f"OOM={oom_W:.2e}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--N", type=int, default=N_FULL)
    parser.add_argument("--seeds", type=str, default=None,
                        help="Comma-separated seed list (default: pre-registered).")
    parser.add_argument("--m_frac", type=float, default=None,
                        help="Override M_frac (default: borderline value).")
    parser.add_argument("--syndrome_threshold", type=float, default=SYNDROME_THRESHOLD_DEFAULT,
                        help="Parity-check threshold (default: 0.95).")
    parser.add_argument("--timeout", type=int, default=14400)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    if not smoke:
        assert args.N == N_FULL, f"PROT-018: FULL run requires --N {N_FULL}; got {args.N}"

    N_cfg = N_SMOKE if smoke else args.N
    M_frac = args.m_frac if args.m_frac is not None else (M_FRAC_SMOKE if smoke else M_FRAC_FULL)
    n_probes = N_PROBES_SMOKE if smoke else N_PROBES_FULL

    if args.seeds is not None:
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    else:
        seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    syndrome_threshold = args.syndrome_threshold

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"[qe3] N={N_cfg} M_frac={M_frac} seeds={seeds} syndrome_thresh={syndrome_threshold} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    out_dir = get_output_dir()
    t0 = time.time()
    cells = []

    for mode in ["baseline", "corrected"]:
        for seed in seeds:
            ts = time.time()
            cell = run_one_cell(
                mode=mode,
                seed=seed,
                M_frac=M_frac,
                device=device,
                N=N_cfg,
                n_probes=n_probes,
                syndrome_threshold=syndrome_threshold,
            )
            cells.append(cell)
            te = time.time() - ts
            print(f"  mode={mode} seed={seed} acc={cell['accuracy']:.4f} "
                  f"err={cell['error_rate']:.4f} violations={cell['n_violations']} "
                  f"corrected={cell['n_corrected']} elapsed_cell={te:.1f}s", flush=True)

    elapsed_s = round(time.time() - t0, 2)
    summary = {"cells": cells, "N": N_cfg, "M_frac": M_frac,
               "seeds": seeds, "syndrome_threshold": syndrome_threshold, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "anchor": "qe3_syndrome_error_correction_v1_n4096",
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "verdict_tag": verdict,
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_cfg, "M_frac": M_frac,
            "seeds": seeds, "syndrome_threshold": syndrome_threshold, "smoke": smoke,
            "n_probes": n_probes,
        },
        "summary": summary,
    }

    out = out_dir / "metrics.json"
    tmp = out.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s}s", flush=True)
    print(f"[output] {out}", flush=True)


if __name__ == "__main__":
    main()
