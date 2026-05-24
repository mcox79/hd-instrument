"""Bet B Direction 5 -- Allen-Cahn t^(1/2) coarsening retention_A(t) probe.

Tests R29's substrate-novel prediction that retention_A as a function of
Phase-C training duration t follows Allen-Cahn t^(1/2) coarsening:

    1 - retention_A(t) ~ c * t^(1/2)

implemented as a Phase-C epoch sweep (t = number of Phase-C training epochs)
on the same A->B->C Bet B Kovacs pipeline as the base script.

Pre-reg (designed inline per exp_dev autonomy + Direction 5 hand-off):

Falsifier statements:
  - HARD_PASS: log-log regression of (1 - retention_A) vs t has slope in
               [0.40, 0.60] with r^2 >= 0.70 across the t-sweep.
               -> substrate-as-disordered-magnet coarsening prediction validated;
               addresses Bet M's first multi-probe criterion.
  - HARD_FAIL: slope outside [0.30, 0.70] OR r^2 < 0.40.
               -> Allen-Cahn coarsening NOT the right scaling law; Bet M
               multi-probe criterion #1 unsatisfied.
  - MIDDLE:    slope in [0.30, 0.40] or [0.60, 0.70] with r^2 >= 0.40; report.

Comparison anchor:
  - Bet B Kovacs at Phase-C-epochs=5 retention_A ~ 0.91-0.92 (per cycle 188).
  - Allen-Cahn theory: domain coarsening at t^(1/2); retention decay ~ t^(1/2).

Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: R29 substrate-as-magnet test;
if HARD-FAIL the dynamical-system framing for retention is rejected at this axis.
Per [[feedback-verify-implementations]]: slope is the Allen-Cahn signature; r^2
is the goodness of fit. Both must pass for HARD_PASS.

Reference: notes/research_R29_ferromagnetism_domains_2026-05-21.md

Pre-reg: preregs/2026-05-24_wave14_betB_allen_cahn_tsweep_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

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

# Full-scale config (designed by exp_dev per autonomy declaration).
N_FULL = 4096
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_AB_FULL = 5
EPOCHS_AB_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_PER_CORPUS_FULL = 200000
BYTES_PER_CORPUS_SMOKE = 5000
EMA_ALPHA = 0.7

# t-sweep on Phase-C epochs (the "duration t" in Allen-Cahn).
PHASE_C_EPOCHS_FULL = [1, 2, 3, 5, 8, 13, 21]   # geometric-ish; 7 points for fit
PHASE_C_EPOCHS_SMOKE = [1, 5]

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Verdict thresholds (Allen-Cahn slope 1/2 +/- band).
PASS_SLOPE_LO = 0.40
PASS_SLOPE_HI = 0.60
PASS_R2 = 0.70
FAIL_SLOPE_LO = 0.30
FAIL_SLOPE_HI = 0.70
FAIL_R2 = 0.40


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def linreg(xs, ys):
    """Simple OLS slope, intercept, r^2 for paired xs, ys (lists)."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    sx = sum(xs); sy = sum(ys)
    mx = sx / n; my = sy / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0.0 or syy == 0.0:
        return 0.0, my, 0.0
    slope = sxy / sxx
    intercept = my - slope * mx
    r2 = (sxy * sxy) / (sxx * syy)
    return slope, intercept, r2


def compute_verdict(summary):
    per_t = summary.get("per_phase_c_epochs")
    if not per_t:
        return ("ALLEN_CAHN_INCONCLUSIVE", "Missing per_phase_c_epochs data.")
    ts_sorted = sorted([int(k) for k in per_t.keys()])
    if len(ts_sorted) < 3:
        return ("ALLEN_CAHN_INCONCLUSIVE",
                f"Need >=3 t-points for regression; got {len(ts_sorted)}.")
    xs = []; ys = []
    by_t_ret = []
    for t in ts_sorted:
        seeds = per_t[str(t)]
        ret_A_mean = sum(s["retention_A"] for s in seeds.values()) / len(seeds)
        by_t_ret.append((t, ret_A_mean))
        decay = max(1.0 - ret_A_mean, 1e-6)
        xs.append(math.log(t))
        ys.append(math.log(decay))
    slope, intercept, r2 = linreg(xs, ys)
    in_pass_band = PASS_SLOPE_LO <= slope <= PASS_SLOPE_HI and r2 >= PASS_R2
    in_fail_band = (slope < FAIL_SLOPE_LO or slope > FAIL_SLOPE_HI) or r2 < FAIL_R2
    in_middle = not in_pass_band and not in_fail_band
    pts_str = ", ".join(f"t={t}:retA={r:.3f}" for t, r in by_t_ret)
    if in_pass_band:
        return ("ALLEN_CAHN_HARD_PASS",
                f"Allen-Cahn t^(1/2) coarsening VALIDATED: slope={slope:.3f} in "
                f"[{PASS_SLOPE_LO},{PASS_SLOPE_HI}], r^2={r2:.3f}>={PASS_R2}. {pts_str}.")
    if in_fail_band:
        return ("ALLEN_CAHN_HARD_FAIL",
                f"Allen-Cahn t^(1/2) REJECTED: slope={slope:.3f} outside "
                f"[{FAIL_SLOPE_LO},{FAIL_SLOPE_HI}] OR r^2={r2:.3f}<{FAIL_R2}. {pts_str}.")
    return ("ALLEN_CAHN_MIDDLE_BAND",
            f"Allen-Cahn partial: slope={slope:.3f}, r^2={r2:.3f}; outside HARD-PASS "
            f"band [{PASS_SLOPE_LO},{PASS_SLOPE_HI}]+r^2>={PASS_R2} but within "
            f"HARD-FAIL safety [{FAIL_SLOPE_LO},{FAIL_SLOPE_HI}]+r^2>={FAIL_R2}. {pts_str}.")


def self_test_verdict():
    # Perfect t^(1/2): retention_A = 1 - c*sqrt(t) -> log(decay) = log(c) + 0.5*log(t)
    def mk_pow(c, exponent, ts):
        return {"per_phase_c_epochs": {str(t): {
            "17": {"retention_A": 1.0 - c * (t ** exponent)}} for t in ts}}
    ts = [1, 2, 5, 10, 20]
    s_pass = mk_pow(0.05, 0.5, ts)               # slope=0.5, r^2=1.0 -> PASS
    s_fail_slope = mk_pow(0.05, 1.0, ts)         # slope=1.0 -> FAIL
    s_fail_lowdecay = mk_pow(0.001, 0.5, ts)     # slope=0.5 still but decay tiny -> still PASS-shaped
    s_inconc = {"per_phase_c_epochs": {"1": {"17": {"retention_A": 0.9}}}}  # <3 ts
    cases = [
        (s_pass, "ALLEN_CAHN_HARD_PASS"),
        (s_fail_slope, "ALLEN_CAHN_HARD_FAIL"),
        (s_inconc, "ALLEN_CAHN_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp} for {s}")
    # linreg helper sanity
    sl, ic, r2 = linreg([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
    assert abs(sl - 2.0) < 1e-9 and abs(r2 - 1.0) < 1e-9
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases + linreg sanity)", flush=True)


def run_one_seed_at_t(seed, phase_c_epochs, config, device):
    """Run one A->B->C with Phase-C using `phase_c_epochs` epochs of training."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs_ab"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)
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
    train_c_idx, _ = base.bytes_to_idx_tensors(train_c, device)
    train_c_idx_full, train_c_tgt_full = base.bytes_to_idx_tensors(train_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
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
    # Phase C with VARIABLE epochs (the t-sweep).
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_u = combined_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx_full, train_c_tgt_full,
        combined_v, combined_l, combined_u, phase_c_epochs, batch_size, device)
    W_ABC = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
    bpc_A_after_C = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    return {"retention_A": retention_A,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "phase_c_epochs": phase_c_epochs}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ts = PHASE_C_EPOCHS_SMOKE if smoke else PHASE_C_EPOCHS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs_ab": EPOCHS_AB_SMOKE if smoke else EPOCHS_AB_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "phase_c_epochs_sweep": ts,
              "ema_alpha": EMA_ALPHA,
              "pass_slope_band": [PASS_SLOPE_LO, PASS_SLOPE_HI],
              "pass_r2": PASS_R2,
              "fail_slope_band": [FAIL_SLOPE_LO, FAIL_SLOPE_HI],
              "fail_r2": FAIL_R2}
    print(f"[config] {config}", flush=True)
    per_t = {}
    for t in ts:
        print(f"[phase_c_epochs={t}] ...", flush=True)
        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed_at_t(seed, t, config, device)
            per_seed[str(seed)] = r
            print(f"  t={t} seed={seed}: retention_A={r['retention_A']:.3f}", flush=True)
        per_t[str(t)] = per_seed
    summary = {"per_phase_c_epochs": per_t}
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
    out_dir = get_output_dir("wave14_betB_allen_cahn_tsweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_t = list(summary["per_phase_c_epochs"].keys())[0]
    seed_key = list(summary["per_phase_c_epochs"][first_t].keys())[0]
    r = summary["per_phase_c_epochs"][first_t][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_allen_cahn_tsweep_v1")
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
