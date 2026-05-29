"""QE-1 SUBSTRATE ANNEALING v1 N=4096: quantum-annealer-analog beta-schedule retrieval.

PARENT: exp_kf1_hallu_rescue_v2_n4096.py -- KF-1 reformulated Tier-1 rescue at N=4096.
  We reuse the BSC-style Kerdock-codebook retrieval pipeline (store_facts_outer,
  argmax retrieval over codebook) but instead of a single fixed inverse temperature
  BETA_INF=32.0 we sweep an annealing SCHEDULE over multiple retrieval iterations.

SCIENTIFIC QUESTION:
  Does a beta-annealing schedule during retrieval improve accuracy on hard, borderline
  M_frac cases (near the capacity boundary M_c) vs a single fixed-beta argmax pass?

  Quantum-annealer analog: starting low beta = high "temperature" lets the substrate
  explore basins broadly; ramping beta = cooling concentrates onto the deepest basin.
  This is the QHO / D-Wave protocol re-cast as a retrieval schedule.

PRE-REGISTERED BANDS (envelope-fail-bands; HP/HF/MIDDLE explicitly pre-committed):
  Baseline = fixed-beta retrieval at beta=32 on borderline M_frac=4 cells (near capacity).
  Schedules tested:
    SCHED_LIN  : linear ramp     beta_t = 2 + (62 * t / (T-1))         for t = 0..T-1 (T=5)
    SCHED_EXP  : exponential     beta_t = 2 * 2^t                       for t = 0..T-1 (T=5; ends 32)
    SCHED_INV  : inverse-linear  1/beta_t = lin from 1/2 to 1/64        for t = 0..T-1 (T=5)

  For each schedule: at end of iteration T-1 we read out final argmax. Score is
  retrieval accuracy on the borderline-M_frac probe set.

  HARD_PASS: at least ONE schedule shows mean_acc_delta >= 0.05 absolute vs fixed-beta
    baseline, across >= 2/3 seeds. Substrate genuinely benefits from annealing.
  HARD_FAIL: NO schedule shows mean_acc_delta >= 0.02 absolute on >= 2/3 seeds.
    Substrate is already operating near saturation under fixed-beta argmax.
  MIDDLE_BAND: some schedule shows mean_acc_delta in [0.02, 0.05) on >= 2/3 seeds.
    Marginal benefit; not product-grade.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018: _n4096 anchor).
  2. C = 4*N = 16384 (Kerdock 4-coset codebook).
  3. SCHED_LIN at t=0 -> beta=2; at t=T-1=4 -> beta = 2 + 62*4/4 = 64.
  4. SCHED_EXP at t=0 -> beta=2; at t=4 -> beta = 2 * 16 = 32.
  5. SCHED_INV: 1/beta at t=0 = 0.5, at t=4 = 1/64 = 0.015625; beta_t at t=0 = 2, at t=4 = 64.
  6. mean_acc_delta = baseline_acc - schedule_acc when schedule is BETTER reported as positive.
     SIGN CONVENTION: delta = schedule_acc - baseline_acc (positive = annealing helps).

TIMEOUT ESTIMATE:
  Smoke 0.5s/cell at N=1024; FULL at N=4096 5x retrieval iters per cell scales as
    0.5 * (4096/1024)^1.5 * (5_iter / 1_iter) ~= 20s/cell.
  9 cells (3 schedules x 3 seeds; baseline absorbed by no-sched first iter) ~= 180s.
  Plus baseline 3 seeds x ~4s = 12s. Total ~200s wall.
  Safety x10 for GPU cold start + codebook reuse + probe-set build: 2000s.
  PROT-019 floor _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: qe1_substrate_annealing_v1_n4096
Queue: overnight_queue (GPU; quantum-annealer-analog beta-schedule probe)
Pre-reg: preregs/2026-05-29_qe1_substrate_annealing_v1_n4096.md
Parent: kf1_hallu_rescue_v2_n4096
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

# Load Kerdock substrate (codebook builder)
_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_v3_spec = importlib.util.spec_from_file_location("kerdock_v3_qe1", _v3_path)
v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3)

# Load v2 store_facts_outer (BSC-style outer-product W) from KF-1 v2 import chain.
# KF-1 v2 itself loads v1 + v3; we mirror that import chain for production-codepath audit
# (per Section 3k of post-compaction brief: smoke must use the same import chain as FULL).
_kf1v2_path = REPO / "experiments" / "exp_kf1_hallu_impossibility_v2.py"
_kf1v2_spec = importlib.util.spec_from_file_location("kf1v2_qe1", _kf1v2_path)
kf1v2 = importlib.util.module_from_spec(_kf1v2_spec)
_kf1v2_spec.loader.exec_module(kf1v2)
store_facts_outer = kf1v2.store_facts_outer

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Borderline M_frac = 4 (near-capacity / over-capacity per parent kf1_hallu_impossibility findings).
M_FRAC_FULL  = 4.0
M_FRAC_SMOKE = 1.0

# Probe set: enough to get a stable retrieval-accuracy estimate on borderline cells.
N_PROBES_FULL  = 500
N_PROBES_SMOKE = 50

# Annealing schedule length (number of retrieval iterations per probe).
T_FULL  = 5
T_SMOKE = 3

# Baseline fixed-beta (matches KF-1 v2 BETA_INF=32.0).
BETA_FIXED = 32.0

SEEDS_FULL  = [7, 17, 23]   # 3 seeds (per spec)
SEEDS_SMOKE = [17]

# Pre-registered envelope-fail-bands.
HP_DELTA_THRESHOLD = 0.05   # mean_acc_delta >= 0.05 = HARD_PASS (substrate benefits)
HF_DELTA_THRESHOLD = 0.02   # no schedule >= 0.02 = HARD_FAIL (no benefit)
MIN_SEEDS_FOR_BAND = 2      # need >= 2/3 seeds at threshold for HP/MIDDLE


def get_output_dir(default_name: str = "qe1_substrate_annealing_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_beta_schedule(name: str, T: int) -> List[float]:
    """Return a list of T inverse temperatures for the named schedule."""
    if name == "fixed":
        return [BETA_FIXED] * T
    if name == "linear":
        # beta_t = 2 + 62 * t/(T-1), t = 0..T-1; ends at beta=64
        if T == 1:
            return [2.0]
        return [2.0 + 62.0 * t / (T - 1) for t in range(T)]
    if name == "exponential":
        # beta_t = 2 * 2^t, t = 0..T-1
        return [2.0 * (2.0 ** t) for t in range(T)]
    if name == "inverse_linear":
        # 1/beta_t linearly decreases from 1/2 to 1/64; beta_t increases from 2 to 64
        if T == 1:
            return [2.0]
        inv_lo, inv_hi = 1.0 / 64.0, 1.0 / 2.0
        return [1.0 / (inv_hi - (inv_hi - inv_lo) * t / (T - 1)) for t in range(T)]
    raise ValueError(f"Unknown schedule: {name}")


def run_one_cell(
    schedule_name: str,
    seed: int,
    M_frac: float,
    device: torch.device,
    N: int,
    n_probes: int,
    T: int,
) -> Dict:
    """One (schedule, seed) cell. Returns retrieval accuracy on borderline M_frac probes.

    Pipeline per probe:
      1. Build Kerdock codebook (C = 4*N).
      2. Store M = M_frac * N (key, value) pairs into W (outer-product BSC-style).
      3. For each probe key (drawn from the stored keys with index q_i):
         - Run T retrieval iterations with the schedule's beta_t.
         - At each iter: q_new = softmax(beta_t * (codebook @ W.T @ q_curr) / N) -> argmax codebook row.
         - The fixed-beta "baseline" schedule has length T but all entries = BETA_FIXED.
      4. Accuracy = fraction of probes where final argmax matches stored val_idx.
    """
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook.shape[0]

    gen = torch.Generator(device="cpu").manual_seed(seed + 7919)
    M = int(M_frac * N)
    if M > C:
        # When M > C, sample with replacement (over-capacity regime is what we want).
        key_idx = torch.randint(0, C, (M,), generator=gen)
        val_idx = torch.randint(0, C, (M,), generator=gen)
    else:
        key_idx = torch.randint(0, C, (M,), generator=gen)
        val_idx = torch.randint(0, C, (M,), generator=gen)
    keys = codebook[key_idx].to(device)
    values = codebook[val_idx].to(device)

    W = store_facts_outer(keys, values, N)

    # Probe subset of stored keys (we are testing retrieval-of-stored, not OOS).
    n_probes_actual = min(n_probes, M)
    probe_order = torch.randperm(M, generator=gen)[:n_probes_actual]
    probe_keys = keys[probe_order]                                              # (P, N)
    probe_target_idx = val_idx[probe_order].to(device)                          # (P,)

    schedule = make_beta_schedule(schedule_name, T)

    # Iterated retrieval. State at iter 0 = probe_key @ W.T (one retrieval pass).
    q = probe_keys.clone()                                                      # (P, N)
    for t, beta_t in enumerate(schedule):
        readout = q @ W.T                                                        # (P, N)
        sims = (codebook @ readout.T) / N                                        # (C, P)
        P_dist = torch.softmax(beta_t * sims, dim=0)                             # (C, P)
        # For iterated retrieval, we read out the soft-argmax codebook vector as the
        # new query. At final iteration we take the hard argmax for accuracy.
        if t < T - 1:
            q = (P_dist.T @ codebook)                                            # (P, N) soft readout
        else:
            pred_idx = P_dist.argmax(dim=0)                                      # (P,)

    acc = (pred_idx == probe_target_idx).float().mean().item()

    return {
        "schedule": schedule_name,
        "seed": seed,
        "M_frac": M_frac,
        "M": M,
        "C": C,
        "N": N,
        "T": T,
        "betas": schedule,
        "n_probes": n_probes_actual,
        "accuracy": acc,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    """Compute QE-1 verdict from cells dict keyed by schedule -> seed -> accuracy."""
    cells = summary.get("cells", [])
    if not cells:
        return ("QE1_INCONCLUSIVE", "No cells.")

    # Aggregate per schedule, per seed.
    by_sched: Dict[str, Dict[int, float]] = {}
    for c in cells:
        s = c["schedule"]
        by_sched.setdefault(s, {})[c["seed"]] = c["accuracy"]

    if "fixed" not in by_sched:
        return ("QE1_INCONCLUSIVE", "Baseline (fixed-beta) missing.")

    baseline_per_seed = by_sched["fixed"]
    seeds_present = sorted(baseline_per_seed.keys())

    # For each non-fixed schedule, compute per-seed delta = sched_acc - baseline_acc.
    sched_deltas: Dict[str, List[float]] = {}
    for s, per_seed in by_sched.items():
        if s == "fixed":
            continue
        deltas = []
        for seed in seeds_present:
            if seed in per_seed:
                deltas.append(per_seed[seed] - baseline_per_seed[seed])
        sched_deltas[s] = deltas

    # Hard-pass check: any schedule with >= MIN_SEEDS_FOR_BAND seeds at >= HP threshold.
    best_sched_hp = None
    best_mean_hp = 0.0
    for s, deltas in sched_deltas.items():
        if not deltas:
            continue
        seeds_hp = sum(1 for d in deltas if d >= HP_DELTA_THRESHOLD)
        mean_d = sum(deltas) / len(deltas)
        if seeds_hp >= MIN_SEEDS_FOR_BAND and mean_d > best_mean_hp:
            best_sched_hp = s
            best_mean_hp = mean_d

    if best_sched_hp is not None:
        return ("QE1_HARD_PASS",
                f"ANNEALING BENEFIT CONFIRMED at N={N_FULL} M_frac={M_FRAC_FULL}: "
                f"schedule={best_sched_hp} mean_delta={best_mean_hp:.4f} >= "
                f"{HP_DELTA_THRESHOLD} on >= {MIN_SEEDS_FOR_BAND}/{len(seeds_present)} seeds. "
                f"Quantum-annealer-analog beta schedule improves borderline retrieval.")

    # MIDDLE_BAND check: any schedule with >= MIN_SEEDS_FOR_BAND seeds at HF threshold.
    best_sched_mid = None
    best_mean_mid = 0.0
    for s, deltas in sched_deltas.items():
        if not deltas:
            continue
        seeds_mid = sum(1 for d in deltas if d >= HF_DELTA_THRESHOLD)
        mean_d = sum(deltas) / len(deltas)
        if seeds_mid >= MIN_SEEDS_FOR_BAND and mean_d > best_mean_mid:
            best_sched_mid = s
            best_mean_mid = mean_d

    if best_sched_mid is not None:
        return ("QE1_MIDDLE_BAND",
                f"Marginal annealing benefit: best schedule={best_sched_mid} "
                f"mean_delta={best_mean_mid:.4f} in [{HF_DELTA_THRESHOLD}, "
                f"{HP_DELTA_THRESHOLD}) on >= {MIN_SEEDS_FOR_BAND}/{len(seeds_present)} seeds. "
                f"Substrate benefits but below product-grade threshold.")

    return ("QE1_HARD_FAIL",
            f"NO ANNEALING BENEFIT at N={N_FULL}: every schedule mean_delta < "
            f"{HF_DELTA_THRESHOLD} on >= {MIN_SEEDS_FOR_BAND}/{len(seeds_present)} seeds. "
            f"Substrate is operating at saturation under fixed-beta argmax; "
            f"beta-schedule does not unlock borderline-case accuracy.")


def _instrumentation_selftest() -> None:
    """Assert all formulas + verdict gates work BEFORE production sweep."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: schedule formulas
    sched_lin = make_beta_schedule("linear", 5)
    assert abs(sched_lin[0] - 2.0) < 1e-9, f"linear t=0: {sched_lin[0]}"
    assert abs(sched_lin[-1] - 64.0) < 1e-9, f"linear t=4: {sched_lin[-1]}"

    sched_exp = make_beta_schedule("exponential", 5)
    assert abs(sched_exp[0] - 2.0) < 1e-9, f"exp t=0: {sched_exp[0]}"
    assert abs(sched_exp[-1] - 32.0) < 1e-9, f"exp t=4: {sched_exp[-1]}"

    sched_inv = make_beta_schedule("inverse_linear", 5)
    assert abs(sched_inv[0] - 2.0) < 1e-9, f"inv t=0: {sched_inv[0]}"
    assert abs(sched_inv[-1] - 64.0) < 1e-6, f"inv t=4: {sched_inv[-1]}"

    sched_fix = make_beta_schedule("fixed", 5)
    assert all(abs(b - BETA_FIXED) < 1e-9 for b in sched_fix), f"fixed: {sched_fix}"

    # Self-test 2: codebook size formula
    # C = 4*N at N=4096 -> 16384
    C_expected = 4 * 4096
    assert C_expected == 16384, f"C formula: {C_expected}"

    # Self-test 3: verdict HARD_PASS path (linear schedule gives +0.10 on 3 seeds)
    cells_hp = [
        {"schedule": "fixed", "seed": 7, "accuracy": 0.40},
        {"schedule": "fixed", "seed": 17, "accuracy": 0.42},
        {"schedule": "fixed", "seed": 23, "accuracy": 0.38},
        {"schedule": "linear", "seed": 7, "accuracy": 0.50},
        {"schedule": "linear", "seed": 17, "accuracy": 0.52},
        {"schedule": "linear", "seed": 23, "accuracy": 0.48},
        {"schedule": "exponential", "seed": 7, "accuracy": 0.41},
        {"schedule": "exponential", "seed": 17, "accuracy": 0.43},
        {"schedule": "exponential", "seed": 23, "accuracy": 0.39},
    ]
    v, msg = compute_verdict({"cells": cells_hp})
    assert "HARD_PASS" in v, f"HP self-test failed: {v}: {msg}"

    # Self-test 4: verdict HARD_FAIL path (all schedules within +0.01 of baseline)
    cells_hf = [
        {"schedule": "fixed", "seed": 7, "accuracy": 0.40},
        {"schedule": "fixed", "seed": 17, "accuracy": 0.42},
        {"schedule": "fixed", "seed": 23, "accuracy": 0.38},
        {"schedule": "linear", "seed": 7, "accuracy": 0.405},
        {"schedule": "linear", "seed": 17, "accuracy": 0.415},
        {"schedule": "linear", "seed": 23, "accuracy": 0.380},
        {"schedule": "exponential", "seed": 7, "accuracy": 0.41},
        {"schedule": "exponential", "seed": 17, "accuracy": 0.42},
        {"schedule": "exponential", "seed": 23, "accuracy": 0.38},
    ]
    v2, msg2 = compute_verdict({"cells": cells_hf})
    assert "HARD_FAIL" in v2, f"HF self-test failed: {v2}: {msg2}"

    # Self-test 5: verdict MIDDLE_BAND path (linear +0.03 on 3 seeds)
    cells_mid = [
        {"schedule": "fixed", "seed": 7, "accuracy": 0.40},
        {"schedule": "fixed", "seed": 17, "accuracy": 0.42},
        {"schedule": "fixed", "seed": 23, "accuracy": 0.38},
        {"schedule": "linear", "seed": 7, "accuracy": 0.43},
        {"schedule": "linear", "seed": 17, "accuracy": 0.45},
        {"schedule": "linear", "seed": 23, "accuracy": 0.41},
        {"schedule": "exponential", "seed": 7, "accuracy": 0.41},
        {"schedule": "exponential", "seed": 17, "accuracy": 0.43},
        {"schedule": "exponential", "seed": 23, "accuracy": 0.39},
    ]
    v3v, msg3 = compute_verdict({"cells": cells_mid})
    assert "MIDDLE_BAND" in v3v, f"MID self-test failed: {v3v}: {msg3}"

    # Self-test 6: smoke cell forward pass at N=1024
    device = torch.device("cpu")
    cell = run_one_cell(
        schedule_name="linear",
        seed=17,
        M_frac=1.0,
        device=device,
        N=N_SMOKE,
        n_probes=20,
        T=3,
    )
    assert "accuracy" in cell and 0.0 <= cell["accuracy"] <= 1.0, \
        f"accuracy sentinel: {cell.get('accuracy')}"
    assert not math.isnan(cell["accuracy"]), "accuracy NaN"
    assert cell["N"] == N_SMOKE, f"N mismatch: {cell['N']}"

    # Self-test 7: OOM pre-check at N=4096 float32
    oom_W = N_FULL * N_FULL * 4
    assert oom_W < 6e9, f"OOM: W at N=4096 = {oom_W:.2e} >= 6GB"

    print(f"[SELFTEST PASS] qe1_substrate_annealing_v1_n4096: N_FULL={N_FULL} "
          f"C={C_expected} sched_lin={sched_lin[0]:.1f}->{sched_lin[-1]:.1f} "
          f"sched_exp={sched_exp[0]:.1f}->{sched_exp[-1]:.1f} "
          f"verdict_gates=3/3 smoke_acc={cell['accuracy']:.3f}", flush=True)


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
    parser.add_argument("--beta_schedule", type=str, default=None,
                        help="Comma-separated subset of: fixed,linear,exponential,inverse_linear "
                             "(default: all four).")
    parser.add_argument("--timeout", type=int, default=14400)
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    if not smoke:
        assert args.N == N_FULL, f"PROT-018: FULL run requires --N {N_FULL}; got {args.N}"

    N_cfg = N_SMOKE if smoke else args.N
    M_frac = args.m_frac if args.m_frac is not None else (M_FRAC_SMOKE if smoke else M_FRAC_FULL)
    T = T_SMOKE if smoke else T_FULL
    n_probes = N_PROBES_SMOKE if smoke else N_PROBES_FULL

    if args.seeds is not None:
        seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    else:
        seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    if args.beta_schedule is not None:
        schedules = [s.strip() for s in args.beta_schedule.split(",") if s.strip()]
    else:
        schedules = ["fixed", "linear", "exponential", "inverse_linear"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"[qe1] N={N_cfg} M_frac={M_frac} T={T} seeds={seeds} schedules={schedules} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    out_dir = get_output_dir()
    t0 = time.time()
    cells = []

    for sched_name in schedules:
        for seed in seeds:
            ts = time.time()
            cell = run_one_cell(
                schedule_name=sched_name,
                seed=seed,
                M_frac=M_frac,
                device=device,
                N=N_cfg,
                n_probes=n_probes,
                T=T,
            )
            cells.append(cell)
            te = time.time() - ts
            print(f"  sched={sched_name} seed={seed} acc={cell['accuracy']:.4f} "
                  f"elapsed_cell={te:.1f}s", flush=True)

    elapsed_s = round(time.time() - t0, 2)
    summary = {"cells": cells, "N": N_cfg, "M_frac": M_frac, "T": T,
               "seeds": seeds, "schedules": schedules, "smoke": smoke}
    verdict, verdict_msg = compute_verdict(summary)

    metrics = {
        "anchor": "qe1_substrate_annealing_v1_n4096",
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "verdict_tag": verdict,  # parallel field for new-schema consumers
        "elapsed_s": elapsed_s,
        "config": {
            "N": N_cfg, "M_frac": M_frac, "T": T,
            "seeds": seeds, "schedules": schedules, "smoke": smoke,
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
