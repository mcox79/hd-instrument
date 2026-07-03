"""Bet B Direction 1 -- Sample-complexity / storage-capacity M-sweep.

Holds task count fixed at the A->B->C Bet B Kovacs pipeline. Sweeps M
(substrate width) over 2x-4x the current baseline (N_baseline=4096) plus
sub-baseline points to anchor the lower end. Measures retention_A at each M.

Per [[feedback-verify-implementations]]: M here = SUBSTRATE WIDTH N (the
dimensionality of the BSC code vectors and the W matrix), NOT pool size.
Documented choice (autonomy declaration covers it).

Goal: determine if Bet B's 91-92% ceiling is capacity-bound (rises with M)
or interference-bound (plateaus).

Pre-reg (designed inline per exp_dev autonomy + Direction 1 hand-off):

Falsifier statements:
  - HARD_PASS capacity-bound: retention_A monotone-increasing in M across the
                              sweep AND retention_A(M_max) - retention_A(M_min)
                              >= 0.10 (10 percentage points). Product story:
                              "retention scales with substrate size."
  - HARD_FAIL interference-bound: retention_A plateaus across M-sweep within
                                  +/- 0.03 (3 pp). Product story: "70-92%
                                  retention is what this substrate does."
  - MIDDLE: any intermediate scaling; report bands.

M-sweep (substrate width N):
  - Full: [1024, 2048, 4096, 8192, 16384]  -- 0.25x, 0.5x, 1x, 2x, 4x baseline
  - Smoke: [1024, 4096]                    -- 2 cells

Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered BEFORE running.
Per [[feedback-pipeline-pacing]]: this is the single most informative empirical for
Bet B characterization (per user leverage ranking).
Per [[feedback-rehabilitation-after-rejection]]: if HARD-FAIL, retention ceiling
is interference-bound -- accept-91pct rescoping option becomes the product story.

Adjacent theory: PAC-Bayes bound (research_5_directions_math_drill_2026-05-24.md
Drill 1) predicts NO M-dependence; this empirical IS the discriminator.

Pre-reg: preregs/2026-05-24_wave14_betB_M_sweep_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

K = base.K
BETA = base.BETA
POOL_SIZE = base.POOL_SIZE
ALPHA_RETR = base.ALPHA_RETR
DELTA_ALPHA = base.DELTA_ALPHA
DELTA_DECAY = base.DELTA_DECAY
RELU_B = base.RELU_B
VOCAB = base.VOCAB
PAD_BYTE = base.PAD_BYTE
REPLAY_FRAC = base.REPLAY_FRAC

# M-sweep (substrate width N). exp_dev autonomy choice.
M_SWEEP_FULL = [1024, 2048, 4096, 8192, 16384]
M_SWEEP_SMOKE = [1024, 4096]

BATCH_SIZE = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_PER_CORPUS_FULL = 200000
BYTES_PER_CORPUS_SMOKE = 5000
EMA_ALPHA = 0.7

SEEDS_FULL = [7, 17, 23]   # 3 seeds for the M-sweep (M=16384 dominates compute)
SEEDS_SMOKE = [17]

# Verdict thresholds.
PASS_LIFT = 0.10              # retention_A spread across sweep
PLATEAU_BAND = 0.03           # +/- pp on either side of mean
MONOTONE_TOL = 0.01           # tolerate this much noise in monotonicity


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def is_monotone_nondecreasing(values, tol=0.01):
    for i in range(len(values) - 1):
        if values[i + 1] < values[i] - tol:
            return False
    return True


def compute_verdict(summary):
    per_m = summary.get("per_substrate_width")
    if not per_m:
        return ("MSWEEP_INCONCLUSIVE", "Missing per_substrate_width data.")
    ms_sorted = sorted([int(k) for k in per_m.keys()])
    rets = []
    for m in ms_sorted:
        seeds = per_m[str(m)]
        ret_A_mean = sum(s["retention_A"] for s in seeds.values()) / len(seeds)
        rets.append(ret_A_mean)
    if len(rets) < 2:
        return ("MSWEEP_INCONCLUSIVE",
                f"Need >= 2 M-points for sweep; got {len(rets)}.")
    monotone = is_monotone_nondecreasing(rets, MONOTONE_TOL)
    lift = max(rets) - min(rets)
    mean_ret = sum(rets) / len(rets)
    max_dev = max(abs(r - mean_ret) for r in rets)
    pts_str = ", ".join(f"M={m}:retA={r:.3f}" for m, r in zip(ms_sorted, rets))
    if monotone and lift >= PASS_LIFT:
        return ("MSWEEP_HARD_PASS_CAPACITY_BOUND",
                f"Capacity-bound: retention_A monotone-increasing in M; "
                f"lift={lift:.3f} >= {PASS_LIFT}. {pts_str}.")
    if max_dev <= PLATEAU_BAND:
        return ("MSWEEP_HARD_FAIL_INTERFERENCE_BOUND",
                f"Interference-bound: retention_A plateaus within +/-{PLATEAU_BAND} "
                f"across all M; max_dev={max_dev:.3f}. {pts_str}.")
    return ("MSWEEP_MIDDLE_BAND",
            f"Intermediate scaling: monotone={monotone}, lift={lift:.3f}, "
            f"max_dev_from_mean={max_dev:.3f}. {pts_str}.")


def self_test_verdict():
    def mk(m_to_ret):
        return {"per_substrate_width": {str(m): {"17": {"retention_A": v}}
                                          for m, v in m_to_ret.items()}}
    s_cap = mk({1024: 0.60, 2048: 0.70, 4096: 0.80, 8192: 0.85, 16384: 0.92})
    s_int = mk({1024: 0.90, 2048: 0.91, 4096: 0.91, 8192: 0.92, 16384: 0.91})
    s_mid = mk({1024: 0.70, 2048: 0.72, 4096: 0.76, 8192: 0.80, 16384: 0.78})
    s_inconc = {}
    cases = [
        (s_cap, "MSWEEP_HARD_PASS_CAPACITY_BOUND"),
        (s_int, "MSWEEP_HARD_FAIL_INTERFERENCE_BOUND"),
        (s_mid, "MSWEEP_MIDDLE_BAND"),
        (s_inconc, "MSWEEP_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed_at_m(seed, N_substrate, config, device):
    """Run A->B->C Bet B Kovacs pipeline at substrate width N_substrate."""
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N_substrate, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N_substrate, gen).to(device)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]
    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)

    W_zero = torch.zeros((N_substrate, N_substrate), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_u = combined_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_v, combined_l, combined_u, n_epochs, batch_size, device)
    W_ABC = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
    bpc_A_after_C = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    return {"retention_A": retention_A,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "N_substrate": N_substrate}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ms = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    config = {"mode": "smoke" if smoke else "full",
              "M_sweep": ms,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "ema_alpha": EMA_ALPHA,
              "pass_lift": PASS_LIFT,
              "plateau_band": PLATEAU_BAND}
    print(f"[config] {config}", flush=True)
    per_m = {}
    for m in ms:
        print(f"[M={m}] sweep ...", flush=True)
        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed_at_m(seed, m, config, device)
            per_seed[str(seed)] = r
            print(f"  M={m} seed={seed}: retention_A={r['retention_A']:.3f}", flush=True)
        per_m[str(m)] = per_seed
    summary = {"per_substrate_width": per_m}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betB_M_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_m = list(summary["per_substrate_width"].keys())[0]
    seed_key = list(summary["per_substrate_width"][first_m].keys())[0]
    r = summary["per_substrate_width"][first_m][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_M_sweep_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
