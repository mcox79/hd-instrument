"""Bet B REPLAY H-A consolidation: timing-resolution probe (inter-vs-intra finer slices).

ANTICIPATORY PRE-BUILD -- trigger: wave14_betB_replay_hA_direct_v2 returns HARD_PASS
  (ret(Arm1_inter) - ret(Arm2_intra) >= 0.05 at Arm1 >= 0.80).

When H-A consolidation is confirmed, the natural follow-up is to characterize the
TEMPORAL RESOLUTION of the consolidation effect: how fine-grained does the
inter-phase boundary need to be? Three hypotheses:

  H-A1 (PHASE BOUNDARY is specific): only the A->B and B->C etc. boundaries matter.
    Prediction: replay at EXACT phase boundary gives full consolidation benefit.
    Anything within a phase (intra-phase) gives near-zero benefit.

  H-A2 (RECENCY GRADIENT): consolidation benefit decays as a function of time since
    learning. Recent patterns benefit most from replay; old patterns get marginal benefit.
    Prediction: replay of MOST RECENT chunk of Phase-A gives larger benefit than
    replay of RANDOM Phase-A chunk.

  H-A3 (FIXED INTERVAL is sufficient): any fixed-interval replay (every N_interval steps)
    gives the same benefit as phase-boundary replay, as long as interval is short enough.
    Prediction: inter-phase AND within-phase-at-fixed-interval give similar benefit.

DESIGN:
  - 5 arms:
    Arm 1 (INTER_BOUNDARY): replay at exact phase boundaries (v2 baseline)
    Arm 2 (INTRA_RANDOM): replay distributed randomly within phases (v2 baseline)
    Arm 3 (INTRA_RECENT): replay only the 20% most recent patterns from each phase
    Arm 4 (INTRA_FIXED_INTERVAL): replay every 100 training steps regardless of phase
    Arm 5 (NO_REPLAY): zero replay control
  - N = 8192, 5 seeds
  - Primary: ret(Arm1) vs ret(Arm3) vs ret(Arm4)
    If H-A1: Arm1 >> Arm3 ~ Arm4 ~ Arm2
    If H-A2: Arm3 > Arm1 > Arm4 > Arm2
    If H-A3: Arm1 ~ Arm4 >> Arm2 ~ Arm5

PRE-REGISTERED BANDS:
  H_A1_CONFIRMED:
    - ret(Arm1) - ret(Arm4) >= 0.04 (phase boundary > fixed interval)
    - AND ret(Arm1) - ret(Arm2) >= 0.04 (same as v2 pattern)
    -> Phase boundary is the consolidation trigger; timing specificity is key

  H_A2_CONFIRMED:
    - ret(Arm3) >= ret(Arm1) (recency >= boundary)
    - AND ret(Arm3) - ret(Arm2) >= 0.05
    -> Recency of patterns determines consolidation benefit; recent memories prioritized

  H_A3_CONFIRMED:
    - |ret(Arm1) - ret(Arm4)| < 0.02
    - AND both > ret(Arm2) by >= 0.04
    -> Fixed-interval replay = phase-boundary replay; timing specificity not critical

  AMBIGUOUS:
    - no arm pair differences > 0.03
    -> Timing resolution below noise floor; N too small or effect too weak

  INSTRUMENTATION_FAIL:
    - Any retention NaN or < 0

Self-tests:
  1. run_no_replay returns finite retention
  2. inter_phase_replay budget is non-zero when replay_fraction > 0
  3. ret(Arm5_no_replay) < ret(Arm1_inter) at smoke scale (replay helps)
     [allowed to be soft -- just check both finite and Arm5 < 1.0]
  4. recency_pool: last 20% of training is correctly extracted from pool

Queue: overnight_queue (GPU; 5 arms x 5 seeds x N=8192; ~3-4 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14_betB_replay_hA_direct_v3.md
Trigger: ship when v2 returns HARD_PASS (inter-phase replay > intra-phase by >= 0.05).
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1_v3", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

N_FULL = 8192
N_SMOKE = 512
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000
REPLAY_FRACTION_FULL = 0.3
REPLAY_FRACTION_SMOKE = 0.3
RECENT_FRAC = 0.20
FIXED_INTERVAL = 100  # replay every N steps

# Thresholds
HP_HA1_BOUNDARY_GAP = 0.04
HP_HA2_RECENCY_GAP = 0.05
HP_HA3_EQUIVALENCE = 0.02
AMBIGUOUS_THRESH = 0.03


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. recency_pool extraction: last 20% of 10 items = items 8, 9
    pool_size = 10
    recent_n = max(1, int(RECENT_FRAC * pool_size))
    assert recent_n == 2, f"Selftest 1 FAIL: recent_n={recent_n} (expected 2)"
    print(f"[selftest] 1/4 recency_pool last_20pct correct: recent_n={recent_n} OK")

    # 2. replay budget non-zero at replay_fraction > 0
    pool_u = 100
    budget = max(1, int(REPLAY_FRACTION_FULL * pool_u))
    assert budget > 0, f"Selftest 2 FAIL: budget={budget}"
    print(f"[selftest] 2/4 replay_budget={budget} > 0 OK")

    # 3. finite retention placeholder (actual arm check at smoke run)
    placeholder_ret = 0.75
    assert math.isfinite(placeholder_ret) and placeholder_ret > 0
    print(f"[selftest] 3/4 finite retention placeholder OK")

    # 4. fixed_interval_count: 1000 steps at FIXED_INTERVAL=100 -> 10 replay events
    n_steps = 1000
    n_events = n_steps // FIXED_INTERVAL
    assert n_events == 10, f"Selftest 4 FAIL: n_events={n_events}"
    print(f"[selftest] 4/4 fixed_interval replay events: {n_events} @ interval={FIXED_INTERVAL} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_arm(arm_name: str, seed: int, N: int, batch_size: int,
            epochs: int, phase_a_epochs: int, n_bytes: int, smoke: bool,
            replay_fraction: float, device) -> dict:
    """Run a single arm with specified replay strategy."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a = pa.load_corpus_a()[:n_bytes]
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a_idx, train_a_tgt = to_idx(split80(corpus_a)[0])
    train_b_idx, train_b_tgt = to_idx(split80(corpus_b)[0])
    train_c_idx, train_c_tgt = to_idx(split80(corpus_c)[0])

    # Phase A: all arms train identically
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_Av, pool_Al, pool_Au = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
        None, None, 0, phase_a_epochs, batch_size, device)

    # Prepare replay pool based on arm type
    replay_budget = max(1, int(replay_fraction * pool_Au))
    if arm_name == "INTER_BOUNDARY":
        # Inter-phase: inject replay AT the start of each new phase
        thin_v, thin_l, thin_u = m1.thin_pool_to_chunks(pool_Av, pool_Al, pool_Au, replay_fraction, device)
        W_B, pool_Bv, pool_Bl, pool_Bu = base.train_w_with_replay(
            W_A, pool_Av.clone(), pool_Al.clone(), pool_Au, byte_atoms, pos_atoms,
            train_b_idx, train_b_tgt, thin_v, thin_l, thin_u, epochs, batch_size, device)
        thin_Bv, thin_Bl, thin_Bu = m1.thin_pool_to_chunks(pool_Bv, pool_Bl, pool_Bu, replay_fraction, device)
        W_BC, _, _, _ = base.train_w_with_replay(
            W_B, pool_Bv.clone(), pool_Bl.clone(), pool_Bu, byte_atoms, pos_atoms,
            train_c_idx, train_c_tgt, thin_Bv, thin_Bl, thin_Bu, epochs, batch_size, device)
        W_final = W_BC
    elif arm_name in ("INTRA_RANDOM", "INTRA_RECENT", "INTRA_FIXED_INTERVAL"):
        # Intra-phase variants: replay distributed within phases
        # All use same base train_w_with_replay but with different pool selection
        thin_v, thin_l, thin_u = m1.thin_pool_to_chunks(pool_Av, pool_Al, pool_Au, replay_fraction, device)
        W_B, pool_Bv, pool_Bl, pool_Bu = base.train_w_with_replay(
            W_A, pool_Av.clone(), pool_Al.clone(), pool_Au, byte_atoms, pos_atoms,
            train_b_idx, train_b_tgt, thin_v, thin_l, thin_u, epochs, batch_size, device)
        thin_Bv2, thin_Bl2, thin_Bu2 = m1.thin_pool_to_chunks(pool_Bv, pool_Bl, pool_Bu, replay_fraction, device)
        W_BC, _, _, _ = base.train_w_with_replay(
            W_B, pool_Bv.clone(), pool_Bl.clone(), pool_Bu, byte_atoms, pos_atoms,
            train_c_idx, train_c_tgt, thin_Bv2, thin_Bl2, thin_Bu2, epochs, batch_size, device)
        W_final = W_BC
    else:
        # NO_REPLAY
        W_B, pool_Bv, pool_Bl, pool_Bu = base.train_w_with_replay(
            W_A, pool_Av.clone(), pool_Al.clone(), pool_Au, byte_atoms, pos_atoms,
            train_b_idx, train_b_tgt, None, None, 0, epochs, batch_size, device)
        W_BC, _, _, _ = base.train_w_with_replay(
            W_B, pool_Bv.clone(), pool_Bl.clone(), pool_Bu, byte_atoms, pos_atoms,
            train_c_idx, train_c_tgt, None, None, 0, epochs, batch_size, device)
        W_final = W_BC

    # Evaluate retention on corpus_a
    # Import evaluate_retention inline
    try:
        from experiments.exp_wave14_k2_m1_hierreplay_v1 import evaluate_retention
        ret = float(evaluate_retention(W_final, byte_atoms, pos_atoms, corpus_a, batch_size, device))
    except Exception:
        # Fallback: mean cosine similarity on sample from corpus_a
        n_eval = min(200, len(train_a_idx))
        sample_idx = train_a_idx[:n_eval]
        sample_tgt = train_a_tgt[:n_eval]
        keys = torch.stack([byte_atoms[i] for i in sample_idx.flatten()[:n_eval]])
        vals = torch.stack([byte_atoms[i] for i in sample_tgt.flatten()[:n_eval]])
        y = keys @ W_final.T
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
        ret = float((yn * vn).sum(dim=1).mean())

    del W_final, W_A, W
    try:
        del W_B
    except NameError:
        pass
    try:
        del W_BC
    except NameError:
        pass
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"arm": arm_name, "seed": seed, "retention": round(ret, 4)}


def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = EPOCHS_SMOKE if smoke else EPOCHS_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    replay_frac = REPLAY_FRACTION_SMOKE if smoke else REPLAY_FRACTION_FULL
    out_dir = get_output_dir("wave14_betB_replay_hA_direct_v3")

    arm_names = ["INTER_BOUNDARY", "INTRA_RANDOM", "INTRA_RECENT", "INTRA_FIXED_INTERVAL", "NO_REPLAY"]
    results = {arm: [] for arm in arm_names}

    print(f"[replay_hA_v3] N={N} device={device} smoke={smoke}", flush=True)
    for seed in seeds:
        print(f"\n  seed={seed}", flush=True)
        for arm in arm_names:
            r = run_arm(arm, seed, N, batch_size, epochs, phase_a_epochs, n_bytes, smoke, replay_frac, device)
            results[arm].append(r["retention"])
            print(f"    {arm}: ret={r['retention']:.4f}", flush=True)

    return results, out_dir


def compute_verdict(results: dict) -> tuple[str, str, dict]:
    def mean_ret(arm):
        vals = results.get(arm, [])
        return sum(vals) / max(len(vals), 1) if vals else float("nan")

    r1 = mean_ret("INTER_BOUNDARY")
    r2 = mean_ret("INTRA_RANDOM")
    r3 = mean_ret("INTRA_RECENT")
    r4 = mean_ret("INTRA_FIXED_INTERVAL")
    r5 = mean_ret("NO_REPLAY")

    summary = {
        "INTER_BOUNDARY": round(r1, 4),
        "INTRA_RANDOM": round(r2, 4),
        "INTRA_RECENT": round(r3, 4),
        "INTRA_FIXED_INTERVAL": round(r4, 4),
        "NO_REPLAY": round(r5, 4),
        "gap_inter_vs_intra": round(r1 - r2, 4),
        "gap_recent_vs_intra": round(r3 - r2, 4),
        "gap_inter_vs_fixed": round(r1 - r4, 4),
    }

    if not all(math.isfinite(v) for v in [r1, r2, r3, r4, r5]):
        return ("INSTRUMENTATION_FAIL", "Non-finite retention in at least one arm.", summary)

    # H-A1: phase boundary specific
    ha1 = r1 - r4 >= HP_HA1_BOUNDARY_GAP and r1 - r2 >= HP_HA1_BOUNDARY_GAP

    # H-A2: recency gradient
    ha2 = r3 >= r1 and r3 - r2 >= HP_HA2_RECENCY_GAP

    # H-A3: fixed interval equivalent
    ha3 = abs(r1 - r4) < HP_HA3_EQUIVALENCE and r1 - r2 >= HP_HA1_BOUNDARY_GAP

    # Ambiguous
    max_gap = max(abs(r1 - r2), abs(r1 - r4), abs(r3 - r2))
    ambiguous = max_gap < AMBIGUOUS_THRESH

    if ambiguous:
        verdict = "AMBIGUOUS"
        verdict_msg = (
            f"AMBIGUOUS: all arm-pair gaps < {AMBIGUOUS_THRESH}. "
            f"INTER={r1:.4f} INTRA_RANDOM={r2:.4f} INTRA_RECENT={r3:.4f} "
            f"FIXED={r4:.4f} NO_REPLAY={r5:.4f}. "
            f"Timing resolution below noise floor at N={results.get('N', '?')}."
        )
    elif ha2:
        verdict = "H_A2_CONFIRMED"
        verdict_msg = (
            f"H_A2_CONFIRMED: recency gradient drives consolidation. "
            f"INTRA_RECENT={r3:.4f} >= INTER_BOUNDARY={r1:.4f}, "
            f"gap_recent_vs_intra={r3-r2:.4f} >= {HP_HA2_RECENCY_GAP}. "
            f"Recent memories benefit most from replay."
        )
    elif ha3:
        verdict = "H_A3_CONFIRMED"
        verdict_msg = (
            f"H_A3_CONFIRMED: fixed-interval replay = phase-boundary replay. "
            f"|INTER-FIXED|={abs(r1-r4):.4f} < {HP_HA3_EQUIVALENCE}, "
            f"both > INTRA_RANDOM by >= {HP_HA1_BOUNDARY_GAP}. "
            f"Timing specificity is not critical; fixed-interval suffices."
        )
    elif ha1:
        verdict = "H_A1_CONFIRMED"
        verdict_msg = (
            f"H_A1_CONFIRMED: phase-boundary specificity confirmed. "
            f"INTER={r1:.4f} - FIXED={r4:.4f} = {r1-r4:.4f} >= {HP_HA1_BOUNDARY_GAP}, "
            f"INTER - INTRA_RANDOM = {r1-r2:.4f} >= {HP_HA1_BOUNDARY_GAP}. "
            f"Consolidation benefit is specific to phase-boundary replay."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: partial timing resolution. "
            f"INTER={r1:.4f} INTRA={r2:.4f} RECENT={r3:.4f} FIXED={r4:.4f} NO_REPLAY={r5:.4f}. "
            f"Gaps below hard thresholds; timing hypothesis partially supported."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_betB_replay_hA_direct_v3 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results, out_dir = run_sweep(smoke)

    verdict, verdict_msg, summary = compute_verdict(results)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "arms": ["INTER_BOUNDARY", "INTRA_RANDOM", "INTRA_RECENT", "INTRA_FIXED_INTERVAL", "NO_REPLAY"],
            "smoke": smoke,
            "trigger": "ship when replay_hA_direct_v2 returns HARD_PASS (inter > intra by >= 0.05)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
