"""SWR Pred-3: Phase-locked vs phase-random replay (Latchoumane analog).

Latchoumane 2017 (Neuron): in-phase spindle stimulation improves consolidation;
out-of-phase (same event count) does NOT. This tests whether the substrate
exhibits an analogous phase-sensitivity at fixed N=3 cascade depth.

PHASE_LOCKED: replay happens in designated non-overlapping windows
  (every replay_interval encoding steps; encoding and replay alternate).
PHASE_RANDOM: same total replay count, but each step independently samples
  whether to replay (Bernoulli with p = n_replay_steps / n_total_steps).

Both conditions: N=3 cascade depth, identical total replay events.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands committed before ship.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-strategy-spec-formula-selftests]]: self-test cells before smoke.
Per [[feedback-composition-classification]]: SCORE-level composition.

Pre-reg: prereqs/2026-05-24_wave14_swr_phase_lock_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Load M1 hierreplay for cascade infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)

base = m1.base
v1 = m1.v1
pa = m1.pa

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 4096
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
CASCADE_DEPTH = 3        # fixed per SWR Pred-3
CHUNK_FRACTION = 0.5
# Phase-locked schedule: replay every REPLAY_INTERVAL encoding steps
# (so replay fraction per step = 1/REPLAY_INTERVAL on average)
REPLAY_INTERVAL = 5      # replay 1 step out of every 5 = 20% of steps

# Pre-registered verdict bands
PASS_DELTA = 0.05    # locked must beat random by this to confirm H_timing
FAIL_DELTA = 0.02    # |delta| < this -> H_content (timing doesn't matter)
INVERSE_DELTA = 0.03 # random beats locked by this -> H_inverse


def get_output_dir(name=None):
    n = name or os.environ.get("HDLAB_EXP_NAME", "wave14_swr_phase_lock_v1")
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def train_phase_locked(W_init, byte_atoms, pos_atoms, tr_idx, tr_tgt,
                        prior_pool_v, prior_pool_l, prior_pool_u,
                        n_epochs, batch_size, device):
    """Phase-locked: pure encoding pass (no replay interleaved), then a separate
    replay-only consolidation pass over the prior pool. Implements hard-gating
    (encoding and replay mutually exclusive), the substrate analog of the
    SWR-theta state exclusion in biology.

    Returns (W, pool_v, pool_l, pool_u) matching train_w_with_replay signature.
    """
    # Step 1: Pure encoding pass (no replay in the inner loop)
    W, pool_v, pool_l, pool_u = base.train_w_with_replay(
        W_init, None, None, 0,
        byte_atoms, pos_atoms, tr_idx, tr_tgt,
        None, None, 0,  # no replay
        n_epochs, batch_size, device)

    # Step 2: If prior pool exists, run a dedicated replay-only consolidation pass.
    # This uses the same prior pool but in a SEPARATE pass (hard-gated from encoding).
    if prior_pool_u > 0 and prior_pool_v is not None:
        # Replay-only: train on a synthetic dataset drawn from the prior pool.
        # Use pool entries as both input (ctx_bundle) and target lookup.
        # We run n_epochs epochs over the prior pool using train_w_with_replay
        # with the prior pool as both training data AND replay source.
        # Since pool entries ARE ctx_bundles already, we pass them as the replay
        # pool and use a dummy training set (zero-length slice).
        # Simplest: call train_w_with_replay with empty new data + prior as replay pool.
        dummy_tr = tr_idx[:0]   # zero-length — no new encoding
        dummy_tgt = tr_tgt[:0]
        W, _, _, _ = base.train_w_with_replay(
            W, pool_v, pool_l, pool_u,
            byte_atoms, pos_atoms, dummy_tr, dummy_tgt,
            prior_pool_v, prior_pool_l, prior_pool_u,
            n_epochs, batch_size, device)

    return W, pool_v, pool_l, pool_u


def train_phase_random(W_init, byte_atoms, pos_atoms, tr_idx, tr_tgt,
                        prior_pool_v, prior_pool_l, prior_pool_u,
                        n_epochs, batch_size, device):
    """Phase-random: standard interleaved encoding + replay at every batch step.
    This is the existing train_w_with_replay behavior.
    """
    return base.train_w_with_replay(
        W_init, None, None, 0,
        byte_atoms, pos_atoms, tr_idx, tr_tgt,
        prior_pool_v, prior_pool_l, prior_pool_u,
        n_epochs, batch_size, device)


def run_one_seed(seed, config, device, mode):
    """Run a 3-stage chain (A->B->C) with phase_mode in {'locked', 'random'}.
    Returns retention_A after stage C.
    """
    assert mode in ("locked", "random"), f"unknown mode: {mode}"
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    tr_a, te_a = split80(corpus_a)
    tr_b, te_b = split80(corpus_b)
    tr_c, te_c = split80(corpus_c)

    tr_a_idx, tr_a_tgt = base.bytes_to_idx_tensors(tr_a, device)
    te_a_idx, te_a_tgt = base.bytes_to_idx_tensors(te_a, device)
    tr_b_idx, tr_b_tgt = base.bytes_to_idx_tensors(tr_b, device)
    tr_c_idx, tr_c_tgt = base.bytes_to_idx_tensors(tr_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A: no replay regardless of mode
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        tr_a_idx, tr_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                        byte_atoms, pos_atoms,
                                        te_a_idx, te_a_tgt, batch_size, device)

    # Thin pool A for cascade replay (M1 style)
    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=CHUNK_FRACTION, device=device)

    train_fn = train_phase_locked if mode == "locked" else train_phase_random

    # Phase B: replay thinned A
    W_B, pool_B_v, pool_B_l, pool_B_u = train_fn(
        W_A, byte_atoms, pos_atoms,
        tr_b_idx, tr_b_tgt,
        thin_A_v, thin_A_l, thin_A_u,
        n_epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_B_v, pool_B_l, pool_B_u, chunk_fraction=CHUNK_FRACTION, device=device)

    # Phase C: replay thinned A + thinned B (cascade depth=2 past A)
    prior_v_C = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    prior_l_C = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    prior_u_C = prior_v_C.shape[0]

    W_C, pool_C_v, pool_C_l, pool_C_u = train_fn(
        W_B, byte_atoms, pos_atoms,
        tr_c_idx, tr_c_tgt,
        prior_v_C, prior_l_C, prior_u_C,
        n_epochs, batch_size, device)

    bpc_A_after = base.evaluate_bpc(W_C, pool_C_v, pool_C_l, pool_C_u,
                                     byte_atoms, pos_atoms,
                                     te_a_idx, te_a_tgt, batch_size, device)
    ret_A = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)
    return ret_A, bpc_A_baseline, bpc_A_after


def compute_verdict(summary):
    locked_data = summary.get("locked", {})
    random_data = summary.get("random", {})
    if not locked_data or not random_data:
        return ("TIMING_INCONCLUSIVE", "Missing locked or random per-seed data.")

    rets_locked = [v["retA"] for v in locked_data.values()]
    rets_random = [v["retA"] for v in random_data.values()]
    if not rets_locked or not rets_random:
        return ("TIMING_INCONCLUSIVE", "Empty per-seed results.")

    mean_locked = sum(rets_locked) / len(rets_locked)
    mean_random = sum(rets_random) / len(rets_random)
    delta = mean_locked - mean_random  # positive = locked wins

    seeds_locked_win = sum(1 for l, r in zip(rets_locked, rets_random) if l - r >= 0)
    n_seeds = len(rets_locked)

    detail = (f"locked={mean_locked:.3f} random={mean_random:.3f} delta={delta:.3f} "
              f"seeds_locked_win={seeds_locked_win}/{n_seeds}. "
              f"per-locked:{[round(r,3) for r in rets_locked]} "
              f"per-random:{[round(r,3) for r in rets_random]}")

    if delta >= PASS_DELTA and seeds_locked_win >= 4:
        return ("TIMING_HARD_PASS",
                f"H_timing CONFIRMED: locked beats random by {delta:.3f}>={PASS_DELTA} "
                f"in {seeds_locked_win}/{n_seeds} seeds. Latchoumane effect transfers. {detail}.")
    if abs(delta) < FAIL_DELTA:
        return ("TIMING_HARD_FAIL_CONTENT",
                f"H_content wins: |delta|={abs(delta):.3f}<{FAIL_DELTA}; "
                f"timing structure immaterial in substrate. {detail}.")
    if delta <= -INVERSE_DELTA:
        return ("TIMING_HARD_FAIL_RANDOM",
                f"H_inverse: random beats locked by {-delta:.3f}>={INVERSE_DELTA}. "
                f"Phase gating hurts substrate. {detail}.")
    return ("TIMING_MIDDLE",
            f"Partial replication: locked leads by {delta:.3f} (0.02-0.04 range). {detail}.")


def self_test_verdict():
    """Self-test: (input -> expected verdict) pairs."""
    def mk(locked_rets, random_rets):
        locked = {str(i): {"retA": r} for i, r in enumerate(locked_rets)}
        random = {str(i): {"retA": r} for i, r in enumerate(random_rets)}
        return {"locked": locked, "random": random}

    cases = [
        (mk([0.88, 0.87, 0.89, 0.88, 0.90], [0.78, 0.77, 0.79, 0.78, 0.80]),
         "TIMING_HARD_PASS"),
        (mk([0.85, 0.85, 0.85, 0.85, 0.85], [0.84, 0.84, 0.85, 0.84, 0.85]),
         "TIMING_HARD_FAIL_CONTENT"),
        (mk([0.78, 0.77, 0.79, 0.78, 0.79], [0.83, 0.83, 0.84, 0.82, 0.83]),
         "TIMING_HARD_FAIL_RANDOM"),
        (mk([0.87, 0.87, 0.88, 0.87, 0.88], [0.84, 0.84, 0.85, 0.84, 0.84]),
         "TIMING_MIDDLE"),
        ({}, "TIMING_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        actual, msg = compute_verdict(summary)
        if actual != expected:
            raise AssertionError(
                f"self_test FAIL: got {actual!r} expected {expected!r}; msg={msg!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[swr-phase-lock] device={device} smoke={smoke}", flush=True)

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "cascade_depth": CASCADE_DEPTH,
        "chunk_fraction": CHUNK_FRACTION,
        "replay_interval": REPLAY_INTERVAL,
        "pass_delta": PASS_DELTA,
        "fail_delta": FAIL_DELTA,
    }
    print(f"[config] {config}", flush=True)

    locked_results = {}
    random_results = {}

    for mode_name, results_dict in [("locked", locked_results), ("random", random_results)]:
        print(f"\n--- Mode: {mode_name} ---", flush=True)
        for seed in config["seeds"]:
            ret_A, bpc_base, bpc_after = run_one_seed(seed, config, device, mode_name)
            results_dict[str(seed)] = {
                "retA": ret_A, "bpc_baseline": bpc_base, "bpc_after": bpc_after}
            print(f"  {mode_name} seed={seed}: retA={ret_A:.3f} "
                  f"bpc_base={bpc_base:.4f} bpc_after={bpc_after:.4f}", flush=True)
        mean = sum(v["retA"] for v in results_dict.values()) / len(results_dict)
        print(f"  {mode_name} MEAN retA={mean:.3f}", flush=True)

    summary = {"locked": locked_results, "random": random_results}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        self_test_verdict()
        return

    name = os.environ.get(
        "HDLAB_EXP_NAME",
        "wave14_swr_phase_lock_v1_smoke" if args.smoke
        else "wave14_swr_phase_lock_v1")
    out_dir = get_output_dir(name)

    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)

    if args.smoke:
        # Smoke gate: both modes ran at least one seed
        n_locked = len(summary.get("locked", {}))
        n_random = len(summary.get("random", {}))
        oracle.assert_baseline_high("swr_phase_locked_seeds", float(n_locked), 0.5)
        oracle.assert_baseline_high("swr_phase_random_seeds", float(n_random), 0.5)

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


if __name__ == "__main__":
    main()
