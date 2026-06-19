"""Replay mechanism H-C scaling probe: does replay match 2x-data training?

H-C (effective-N-doubling): replay effectively doubles the number of training
examples, so retention curves at (1x data + replay_frac=0.5) should MATCH
retention curves at (2x data + replay_frac=0.0).

Design:
  CONDITION_REPLAY:   Phase A trained on N_BYTES bytes with 0 replay;
                      Phase B/C trained on N_BYTES bytes WITH 0.5 replay.
  CONDITION_2X:       Phase A trained on 2*N_BYTES bytes with 0 replay;
                      Phase B/C trained on 2*N_BYTES bytes with 0 replay.

H-C confirms: |retention_replay - retention_2x| < HC_MATCH_THRESHOLD (curves match)
H-C refutes:  retention_replay >> retention_2x (replay provides MORE than N-doubling)
              OR retention_replay << retention_2x (replay provides LESS than N-doubling)

Also tests: whether replay-condition retention_A is HIGHER than no-replay-at-N baseline,
confirming the 63% recovery seen in replay_structural_axis_v1.

Pre-reg: preregs/2026-05-25_wave14_betB_replay_hC_scaling_v1.md
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

from verification import oracle  # noqa: E402

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
REPLAY_FRAC = 0.50

# Full-scale config
N_FULL = 4096
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
# Note: 2X condition uses 2 * BYTES_PER_CORPUS for training; same held-out test set
BYTES_PER_CORPUS_FULL = 150000   # 1x; 2x = 300000; kept smaller than ablation sweep
BYTES_PER_CORPUS_SMOKE = 4000
EMA_ALPHA = 0.7

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HC_MATCH_THRESHOLD = 0.04   # H-C confirmed: |replay - 2x| < this
HC_HARD_PASS = 0.04         # |diff| < this = H-C scaling law holds
HC_HARD_FAIL_REPLAY_BETTER = 0.08   # replay MUCH better than 2x = H-C refuted (replay != N-doubling)
HC_HARD_FAIL_2X_BETTER = 0.08       # 2x MUCH better than replay = replay is weak, N matters more
REPLAY_MIN_LIFT = 0.10      # replay must show at least this lift over 1x-no-replay baseline


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


def compute_verdict(summary):
    """Classify H-C from per-seed retention comparison."""
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("HC_INCONCLUSIVE", "Missing per-seed data.")

    seeds = list(seeds_data.values())
    n = len(seeds)

    ret_replay = sum(s["retention_A_replay"] for s in seeds) / n
    ret_2x = sum(s["retention_A_2x"] for s in seeds) / n
    ret_baseline_1x = sum(s["retention_A_1x_noreplay"] for s in seeds) / n
    diff = ret_replay - ret_2x   # positive = replay better than 2x
    replay_lift = ret_replay - ret_baseline_1x

    if replay_lift < REPLAY_MIN_LIFT:
        return ("HC_INCONCLUSIVE",
                f"Replay lift={replay_lift:.3f} < {REPLAY_MIN_LIFT}; "
                f"mechanism not active at scale. Cannot test H-C. "
                f"ret_replay={ret_replay:.3f} ret_2x={ret_2x:.3f} "
                f"ret_1x_noreplay={ret_baseline_1x:.3f}.")

    if abs(diff) < HC_HARD_PASS:
        return ("HC_HARD_PASS",
                f"H-C CONFIRMED: |ret_replay - ret_2x| = {abs(diff):.3f} < {HC_HARD_PASS}. "
                f"ret_replay={ret_replay:.3f} ~= ret_2x={ret_2x:.3f}. "
                f"Replay DOES match effective-N-doubling (scaling-law signature). "
                f"replay_lift over 1x={replay_lift:.3f}.")

    if diff > HC_HARD_FAIL_REPLAY_BETTER:
        return ("HC_REPLAY_EXCEEDS_2X",
                f"H-C REFUTED (replay > 2x): diff={diff:.3f} > {HC_HARD_FAIL_REPLAY_BETTER}. "
                f"ret_replay={ret_replay:.3f} >> ret_2x={ret_2x:.3f}. "
                f"Replay provides MORE than N-doubling -- mechanism is NOT simple data augmentation. "
                f"H-A (consolidation) or H-B (interference) likely dominant.")

    if -diff > HC_HARD_FAIL_2X_BETTER:
        return ("HC_2X_EXCEEDS_REPLAY",
                f"H-C REFUTED (2x > replay): diff={diff:.3f} < -{HC_HARD_FAIL_2X_BETTER}. "
                f"ret_2x={ret_2x:.3f} >> ret_replay={ret_replay:.3f}. "
                f"N-doubling outperforms replay -- replay is merely recapping seen data, "
                f"true new data is strictly better (N matters more than replay rate). "
                f"replay_lift over 1x={replay_lift:.3f}.")

    return ("HC_MIDDLE_BAND",
            f"H-C ambiguous: diff={diff:.3f} in middle band. "
            f"ret_replay={ret_replay:.3f} ret_2x={ret_2x:.3f} "
            f"ret_1x_noreplay={ret_baseline_1x:.3f}. replay_lift={replay_lift:.3f}.")


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Test 1: replay ~= 2x -- H-C HARD PASS
    s1 = {"per_seed": {"17": {
        "retention_A_replay": 0.83,
        "retention_A_2x": 0.81,
        "retention_A_1x_noreplay": 0.68,
    }}}
    v1, _ = compute_verdict(s1)
    assert v1 == "HC_HARD_PASS", f"selftest 1 failed: {v1}"

    # Test 2: replay much better than 2x -- H-C REFUTED (replay exceeds 2x)
    s2 = {"per_seed": {"17": {
        "retention_A_replay": 0.86,
        "retention_A_2x": 0.77,
        "retention_A_1x_noreplay": 0.68,
    }}}
    v2, _ = compute_verdict(s2)
    assert v2 == "HC_REPLAY_EXCEEDS_2X", f"selftest 2 failed: {v2}"

    # Test 3: 2x much better -- H-C REFUTED (2x > replay)
    # diff = 0.80 - 0.91 = -0.11; -diff = 0.11 > HC_HARD_FAIL_2X_BETTER=0.08
    # replay_lift = 0.80 - 0.68 = 0.12 > REPLAY_MIN_LIFT=0.10
    s3 = {"per_seed": {"17": {
        "retention_A_replay": 0.80,
        "retention_A_2x": 0.91,
        "retention_A_1x_noreplay": 0.68,
    }}}
    v3, _ = compute_verdict(s3)
    assert v3 == "HC_2X_EXCEEDS_REPLAY", f"selftest 3 failed: {v3}"

    # Test 4: replay lift too small -- INCONCLUSIVE
    s4 = {"per_seed": {"17": {
        "retention_A_replay": 0.70,
        "retention_A_2x": 0.85,
        "retention_A_1x_noreplay": 0.68,
    }}}
    v4, _ = compute_verdict(s4)
    assert v4 == "HC_INCONCLUSIVE", f"selftest 4 failed: {v4}"

    print("_instrumentation_selftest passed (4/4 verdict cases)", flush=True)


_instrumentation_selftest()


def train_w_with_replay_frac(W_init, pool_vecs, pool_labels, pool_used,
                               byte_atoms, pos_atoms, train_bytes, target_bytes,
                               replay_pool_vecs, replay_pool_labels, replay_pool_used,
                               n_epochs, batch_size, replay_frac, device):
    """Train W with explicit replay_frac control."""
    W = W_init.clone().to(device)
    if pool_vecs is not None:
        pool_vecs = pool_vecs.to(device)
        pool_labels = pool_labels.to(device)
    if replay_pool_vecs is not None:
        replay_pool_vecs = replay_pool_vecs.to(device)
        replay_pool_labels = replay_pool_labels.to(device)
    N = W.shape[0]
    T = train_bytes.shape[0]
    arange_b = torch.arange(batch_size, device=device)
    pool_idx_local = pool_used % POOL_SIZE if pool_used else 0
    pool_used_local = pool_used or 0
    if pool_vecs is None:
        pool_vecs = torch.zeros((POOL_SIZE, N), dtype=torch.float32, device=device)
        pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=device)

    for epoch in range(n_epochs):
        for batch_start in range(0, T, batch_size):
            be = min(batch_start + batch_size, T)
            idx_batch = train_bytes[batch_start:be]
            tgt_batch = target_bytes[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)

            if replay_pool_vecs is not None and replay_pool_used > 0 and replay_frac > 0:
                n_replay = max(1, int(replay_frac * B))
                replay_perm = torch.randperm(replay_pool_used, device=device)[:n_replay]
                replay_ctxs = replay_pool_vecs[replay_perm]
                replay_tgts = replay_pool_labels[replay_perm]
                ctxs = torch.cat([ctxs, replay_ctxs], dim=0)
                tgt_batch = torch.cat([tgt_batch, replay_tgts], dim=0)
                B = ctxs.shape[0]

            with torch.no_grad():
                q = ctxs @ W.T
                q = pa.shifted_relu(q, RELU_B)
                sims = (byte_atoms @ q.T) / N
                P = torch.softmax(BETA * sims, dim=0)
                target_atoms = byte_atoms[tgt_batch]
                predicted = (P.T @ byte_atoms)
                residual = target_atoms - predicted
                dW = (residual.T @ ctxs) / N
                W.mul_(1.0 - DELTA_DECAY)
                W.add_(dW, alpha=DELTA_ALPHA)
                if epoch == 0:
                    take = min(B, batch_size)
                    if take > 0:
                        dest = (pool_idx_local + arange_b[:take]) % POOL_SIZE
                        pool_vecs.index_copy_(0, dest, ctxs[:take])
                        pool_labels.index_copy_(0, dest, tgt_batch[:take])
                        pool_idx_local = (pool_idx_local + take) % POOL_SIZE
                        pool_used_local = min(pool_used_local + take, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used_local


def run_one_seed(seed, config, device):
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]  # 1x size

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    # 1x corpus
    corpus_a_1x = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    # 2x corpus: use first 2*n_bytes (or full if smaller)
    n_bytes_2x = min(2 * n_bytes, len(corpus_a_full))
    corpus_a_2x = corpus_a_full[:n_bytes_2x]

    # Create distinct corpus_b and corpus_c (same for both conditions; fair comparison)
    corpus_b_1x = pa.shuffle_bytes(corpus_a_1x, seed=seed + 1)
    corpus_b_2x = pa.shuffle_bytes(corpus_a_2x, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c_1x = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_c_2x = corpus_c_full[:n_bytes_2x] if n_bytes_2x < len(corpus_c_full) else corpus_c_full

    def split80(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    # 1x splits
    train_a_1x, test_a_1x = split80(corpus_a_1x)
    train_b_1x, _ = split80(corpus_b_1x)
    train_c_1x, _ = split80(corpus_c_1x)

    # 2x splits (train only; evaluate on SAME held-out set as 1x for fair comparison)
    train_a_2x, _ = split80(corpus_a_2x)
    train_b_2x, _ = split80(corpus_b_2x)
    train_c_2x, _ = split80(corpus_c_2x)

    def to_idx(data):
        return base.bytes_to_idx_tensors(data, device)

    train_a_1x_idx, train_a_1x_tgt = to_idx(train_a_1x)
    test_a_1x_idx, test_a_1x_tgt = to_idx(test_a_1x)
    train_b_1x_idx, train_b_1x_tgt = to_idx(train_b_1x)
    train_c_1x_idx, train_c_1x_tgt = to_idx(train_c_1x)
    train_a_2x_idx, train_a_2x_tgt = to_idx(train_a_2x)
    train_b_2x_idx, train_b_2x_tgt = to_idx(train_b_2x)
    train_c_2x_idx, train_c_2x_tgt = to_idx(train_c_2x)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    def run_abc(train_a_idx, train_a_tgt, train_b_idx, train_b_tgt, train_c_idx, train_c_tgt,
                replay_frac, label):
        W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay_frac(
            W_zero, None, None, 0,
            byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
            None, None, 0, phase_a_epochs, batch_size, 0.0, device)

        bpc_A_baseline = base.evaluate_bpc(
            W_A, pool_A_v, pool_A_l, pool_A_u,
            byte_atoms, pos_atoms, test_a_1x_idx, test_a_1x_tgt, batch_size, device)

        W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay_frac(
            W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
            byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
            pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, replay_frac, device)

        combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
        combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
        combined_u = combined_v.shape[0]

        W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay_frac(
            W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
            byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
            combined_v if replay_frac > 0 else None,
            combined_l if replay_frac > 0 else None,
            combined_u if replay_frac > 0 else 0,
            n_epochs, batch_size, replay_frac, device)

        W_final = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
        bpc_A_after = base.evaluate_bpc(
            W_final, pool_ABC_v, pool_ABC_l, pool_ABC_u,
            byte_atoms, pos_atoms, test_a_1x_idx, test_a_1x_tgt, batch_size, device)
        retention = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)
        print(f"    {label}: bpc_baseline={bpc_A_baseline:.3f} bpc_after={bpc_A_after:.3f} "
              f"retention={retention:.3f}", flush=True)
        return float(retention)

    # Condition 1: 1x data + replay
    ret_replay = run_abc(train_a_1x_idx, train_a_1x_tgt,
                         train_b_1x_idx, train_b_1x_tgt,
                         train_c_1x_idx, train_c_1x_tgt,
                         REPLAY_FRAC, "1x+replay")

    # Condition 2: 2x data + no replay
    ret_2x = run_abc(train_a_2x_idx, train_a_2x_tgt,
                     train_b_2x_idx, train_b_2x_tgt,
                     train_c_2x_idx, train_c_2x_tgt,
                     0.0, "2x+noreplay")

    # Condition 3: 1x data + no replay (baseline)
    ret_1x_noreplay = run_abc(train_a_1x_idx, train_a_1x_tgt,
                               train_b_1x_idx, train_b_1x_tgt,
                               train_c_1x_idx, train_c_1x_tgt,
                               0.0, "1x+noreplay")

    diff = ret_replay - ret_2x
    replay_lift = ret_replay - ret_1x_noreplay
    print(f"  seed={seed}: ret_replay={ret_replay:.3f} ret_2x={ret_2x:.3f} "
          f"ret_1x_noreplay={ret_1x_noreplay:.3f} diff={diff:.3f} "
          f"replay_lift={replay_lift:.3f}", flush=True)

    return {
        "retention_A_replay": ret_replay,
        "retention_A_2x": ret_2x,
        "retention_A_1x_noreplay": ret_1x_noreplay,
        "diff_replay_minus_2x": diff,
        "replay_lift": replay_lift,
    }


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "replay_frac": REPLAY_FRAC,
        "ema_alpha": EMA_ALPHA,
        "hc_match_threshold": HC_MATCH_THRESHOLD,
    }
    print(f"[config] {config}", flush=True)

    per_seed = {}
    for seed in config["seeds"]:
        print(f"[seed={seed}]", flush=True)
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r

    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14_betB_replay_hC_scaling_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    seeds_data = summary["per_seed"]
    assert len(seeds_data) > 0, "No seed data"
    s = list(seeds_data.values())[0]
    assert s["retention_A_replay"] > 0, "retention_A_replay null"
    assert s["retention_A_2x"] > 0, "retention_A_2x null"
    assert s["retention_A_1x_noreplay"] > 0, "retention_A_1x_noreplay null"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_replay_hC_scaling_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _instrumentation_selftest()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
