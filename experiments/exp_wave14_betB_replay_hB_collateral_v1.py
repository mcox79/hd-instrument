"""Replay mechanism H-B collateral probe: does replay protect non-replayed items?

H-B (interference-reduction): replay reduces interference between learning epochs
by protecting the substrate's representational capacity -- predict that HELD-OUT
items (never directly replayed) ALSO show higher retention than the no-replay
baseline, because replay suppresses global interference, not just item-specific
forgetting.

H-A (consolidation) prediction: only DIRECTLY REPLAYED items benefit; held-out
items show the same retention as no-replay baseline.

Design: split corpus_A into two equal halves:
  replay_half  -- items that ARE included in the replay pool during Phase B/C
  held_out_half -- items from corpus_A that are NEVER replayed

Conditions:
  REPLAY:    Phase B/C trains with replay_pool built from replay_half only
  NO_REPLAY: Phase B/C trains with no replay at all (baseline)

Metrics:
  retention_A_replayed:  bpc on replay_half test set after Phase C
  retention_A_held_out:  bpc on held_out_half test set after Phase C
  retention_A_no_replay: bpc on ALL of corpus_A held-out, no replay baseline

H-B confirmed:  retention_A_held_out > retention_A_no_replay + COLLATERAL_THRESHOLD
H-A only:       retention_A_held_out ~= retention_A_no_replay (no collateral benefit)
H-B refuted:    retention_A_held_out <= retention_A_no_replay

Pre-reg: preregs/2026-05-25_wave14_betB_replay_hB_collateral_v1.md
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
BYTES_PER_CORPUS_FULL = 200000
BYTES_PER_CORPUS_SMOKE = 5000
EMA_ALPHA = 0.7

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
COLLATERAL_THRESHOLD = 0.03    # H-B confirmed if held_out > no_replay + this
COLLATERAL_HARD_PASS = 0.05    # strong collateral: +5pp lift on held-out
COLLATERAL_HARD_FAIL = 0.00    # H-B refuted: held-out no better than baseline
REPLAY_DIRECT_MIN = 0.15       # direct-replay items must show substantial lift


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


def compute_verdict(summary):
    """Classify H-B vs H-A from per-seed collateral metrics."""
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("HB_INCONCLUSIVE", "Missing per-seed data.")

    seeds = list(seeds_data.values())
    n = len(seeds)

    # Average across seeds
    collateral_lift = sum(s["collateral_lift"] for s in seeds) / n
    direct_lift = sum(s["direct_lift"] for s in seeds) / n
    ret_held = sum(s["retention_held_out"] for s in seeds) / n
    ret_noreplay = sum(s["retention_no_replay"] for s in seeds) / n
    ret_direct = sum(s["retention_direct_replay"] for s in seeds) / n

    if direct_lift < REPLAY_DIRECT_MIN:
        return ("HB_INCONCLUSIVE",
                f"Direct replay lift={direct_lift:.3f} < {REPLAY_DIRECT_MIN}; "
                f"replay mechanism not active at this scale. Cannot discriminate H-A vs H-B.")

    if collateral_lift >= COLLATERAL_HARD_PASS:
        return ("HB_HARD_PASS",
                f"H-B CONFIRMED: collateral_lift={collateral_lift:.3f} >= {COLLATERAL_HARD_PASS}. "
                f"Held-out retention={ret_held:.3f} >> no-replay={ret_noreplay:.3f}. "
                f"Direct replay lift={direct_lift:.3f}. "
                f"Interference-reduction is a REAL mechanism beyond just re-presentation.")

    if collateral_lift <= COLLATERAL_HARD_FAIL:
        return ("HB_HARD_FAIL",
                f"H-A ONLY: collateral_lift={collateral_lift:.3f} <= {COLLATERAL_HARD_FAIL}. "
                f"Held-out retention={ret_held:.3f} ~= no-replay={ret_noreplay:.3f}. "
                f"Direct replay lift={direct_lift:.3f}. "
                f"Replay benefits only directly replayed items (consolidation H-A, not H-B interference-reduction).")

    if collateral_lift > COLLATERAL_THRESHOLD:
        return ("HB_MIDDLE_POSITIVE",
                f"Weak H-B signal: collateral_lift={collateral_lift:.3f} in "
                f"({COLLATERAL_THRESHOLD:.2f}, {COLLATERAL_HARD_PASS:.2f}). "
                f"Held-out={ret_held:.3f} vs no-replay={ret_noreplay:.3f}. "
                f"Direct lift={direct_lift:.3f}. "
                f"Some interference-reduction but below hard-pass bar.")

    return ("HB_MIDDLE_NEUTRAL",
            f"Ambiguous: collateral_lift={collateral_lift:.3f} in "
            f"({COLLATERAL_HARD_FAIL:.2f}, {COLLATERAL_THRESHOLD:.2f}). "
            f"Held-out={ret_held:.3f} vs no-replay={ret_noreplay:.3f}. "
            f"Direct lift={direct_lift:.3f}.")


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Synthetic: build 3 retention values and verify verdict logic
    # Test 1: strong collateral -- H-B HARD PASS
    s1 = {"per_seed": {"17": {
        "collateral_lift": 0.08,
        "direct_lift": 0.16,
        "retention_held_out": 0.76,
        "retention_no_replay": 0.68,
        "retention_direct_replay": 0.84,
    }}}
    v1, _ = compute_verdict(s1)
    assert v1 == "HB_HARD_PASS", f"selftest 1 failed: {v1}"

    # Test 2: zero collateral -- H-A ONLY (HARD FAIL)
    s2 = {"per_seed": {"17": {
        "collateral_lift": -0.01,
        "direct_lift": 0.16,
        "retention_held_out": 0.67,
        "retention_no_replay": 0.68,
        "retention_direct_replay": 0.84,
    }}}
    v2, _ = compute_verdict(s2)
    assert v2 == "HB_HARD_FAIL", f"selftest 2 failed: {v2}"

    # Test 3: direct lift too small -- INCONCLUSIVE
    s3 = {"per_seed": {"17": {
        "collateral_lift": 0.06,
        "direct_lift": 0.01,
        "retention_held_out": 0.74,
        "retention_no_replay": 0.68,
        "retention_direct_replay": 0.69,
    }}}
    v3, _ = compute_verdict(s3)
    assert v3 == "HB_INCONCLUSIVE", f"selftest 3 failed: {v3}"

    # Test 4: weak positive -- MIDDLE_POSITIVE
    s4 = {"per_seed": {"17": {
        "collateral_lift": 0.04,
        "direct_lift": 0.16,
        "retention_held_out": 0.72,
        "retention_no_replay": 0.68,
        "retention_direct_replay": 0.84,
    }}}
    v4, _ = compute_verdict(s4)
    assert v4 == "HB_MIDDLE_POSITIVE", f"selftest 4 failed: {v4}"

    print("_instrumentation_selftest passed (4/4 verdict cases)", flush=True)


_instrumentation_selftest()


def train_w_with_replay_explicit(W_init, pool_vecs, pool_labels, pool_used,
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
    n_bytes = config["bytes_per_corpus"]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    # Split corpus_A into two equal halves for H-B probe
    half = len(corpus_a) // 2
    corpus_a_replay_half = corpus_a[:half]    # items that CAN be in replay pool
    corpus_a_held_out_half = corpus_a[half:]   # items that are NEVER replayed

    def split80(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a_r, test_a_r = split80(corpus_a_replay_half)      # replay half splits
    train_a_h, test_a_h = split80(corpus_a_held_out_half)    # held-out half splits
    train_b, test_b = split80(corpus_b)
    train_c, test_c = split80(corpus_c)

    # Convert all to idx tensors
    train_a_r_idx, train_a_r_tgt = base.bytes_to_idx_tensors(train_a_r, device)
    test_a_r_idx, test_a_r_tgt = base.bytes_to_idx_tensors(test_a_r, device)
    train_a_h_idx, train_a_h_tgt = base.bytes_to_idx_tensors(train_a_h, device)
    test_a_h_idx, test_a_h_tgt = base.bytes_to_idx_tensors(test_a_h, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)

    # Combine both halves for full Phase-A training
    train_a_full_idx = torch.cat([train_a_r_idx, train_a_h_idx], dim=0)
    train_a_full_tgt = torch.cat([train_a_r_tgt, train_a_h_tgt], dim=0)
    test_a_all_idx = torch.cat([test_a_r_idx, test_a_h_idx], dim=0)
    test_a_all_tgt = torch.cat([test_a_r_tgt, test_a_h_tgt], dim=0)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # --- Train Phase A on FULL corpus_A ---
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay_explicit(
        W_zero, None, None, 0,
        byte_atoms, pos_atoms, train_a_full_idx, train_a_full_tgt,
        None, None, 0, phase_a_epochs, batch_size, 0.0, device)

    # Baseline bpc measurements after Phase A
    bpc_A_r_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, test_a_r_idx, test_a_r_tgt, batch_size, device)
    bpc_A_h_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, test_a_h_idx, test_a_h_tgt, batch_size, device)
    bpc_A_all_baseline = base.evaluate_bpc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        byte_atoms, pos_atoms, test_a_all_idx, test_a_all_tgt, batch_size, device)

    def run_phase_bc(W_A, pool_A_v, pool_A_l, pool_A_u, replay_frac, replay_pool_v, replay_pool_l, replay_pool_u):
        """Run Phase B then Phase C, return final W."""
        W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay_explicit(
            W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
            byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
            replay_pool_v, replay_pool_l, replay_pool_u,
            n_epochs, batch_size, replay_frac, device)

        # For Phase C replay: combine phase A replay pool and phase AB pool
        if replay_pool_v is not None and replay_pool_u > 0:
            combined_v = torch.cat([replay_pool_v[:replay_pool_u], pool_AB_v[:pool_AB_u]], dim=0)
            combined_l = torch.cat([replay_pool_l[:replay_pool_u], pool_AB_l[:pool_AB_u]], dim=0)
            combined_u = combined_v.shape[0]
        else:
            combined_v, combined_l, combined_u = None, None, 0

        W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay_explicit(
            W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
            byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
            combined_v, combined_l, combined_u,
            n_epochs, batch_size, replay_frac, device)

        W_final = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
        return W_final, pool_ABC_v, pool_ABC_l, pool_ABC_u

    # Build replay pool from ONLY the replay_half of corpus_A
    # (phase A pool built above contains both halves; re-build from replay half only)
    W_A2, pool_replay_v, pool_replay_l, pool_replay_u = train_w_with_replay_explicit(
        W_zero, None, None, 0,
        byte_atoms, pos_atoms, train_a_r_idx, train_a_r_tgt,
        None, None, 0, phase_a_epochs, batch_size, 0.0, device)
    # We use W_A (trained on full corpus) but replay pool only from replay_half
    # This correctly tests: replay pool contains only replay_half items
    del W_A2

    # Condition 1: REPLAY -- play back only replay_half items
    W_replay, pool_r_v, pool_r_l, pool_r_u = run_phase_bc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        REPLAY_FRAC, pool_replay_v, pool_replay_l, pool_replay_u)

    # Condition 2: NO REPLAY baseline
    W_noreplay, pool_nr_v, pool_nr_l, pool_nr_u = run_phase_bc(
        W_A, pool_A_v, pool_A_l, pool_A_u,
        0.0, None, None, 0)

    # Measure retention in each condition
    bpc_replay_r_after = base.evaluate_bpc(
        W_replay, pool_r_v, pool_r_l, pool_r_u,
        byte_atoms, pos_atoms, test_a_r_idx, test_a_r_tgt, batch_size, device)
    bpc_replay_h_after = base.evaluate_bpc(
        W_replay, pool_r_v, pool_r_l, pool_r_u,
        byte_atoms, pos_atoms, test_a_h_idx, test_a_h_tgt, batch_size, device)
    bpc_noreplay_all_after = base.evaluate_bpc(
        W_noreplay, pool_nr_v, pool_nr_l, pool_nr_u,
        byte_atoms, pos_atoms, test_a_all_idx, test_a_all_tgt, batch_size, device)

    retention_direct = min(bpc_A_r_baseline / max(bpc_replay_r_after, 1e-6), 1.0)
    retention_held_out = min(bpc_A_h_baseline / max(bpc_replay_h_after, 1e-6), 1.0)
    retention_no_replay = min(bpc_A_all_baseline / max(bpc_noreplay_all_after, 1e-6), 1.0)

    collateral_lift = retention_held_out - retention_no_replay
    direct_lift = retention_direct - retention_no_replay

    print(f"  seed={seed}: direct_lift={direct_lift:.3f} collateral_lift={collateral_lift:.3f} "
          f"ret_direct={retention_direct:.3f} ret_held={retention_held_out:.3f} "
          f"ret_noreplay={retention_no_replay:.3f}", flush=True)

    return {
        "retention_direct_replay": float(retention_direct),
        "retention_held_out": float(retention_held_out),
        "retention_no_replay": float(retention_no_replay),
        "direct_lift": float(direct_lift),
        "collateral_lift": float(collateral_lift),
        "bpc_A_r_baseline": float(bpc_A_r_baseline),
        "bpc_A_h_baseline": float(bpc_A_h_baseline),
        "bpc_replay_r_after": float(bpc_replay_r_after),
        "bpc_replay_h_after": float(bpc_replay_h_after),
        "bpc_noreplay_all_after": float(bpc_noreplay_all_after),
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
        "collateral_hard_pass": COLLATERAL_HARD_PASS,
        "collateral_hard_fail": COLLATERAL_HARD_FAIL,
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
    out_dir = get_output_dir("wave14_betB_replay_hB_collateral_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Validate at least one seed produced non-null collateral_lift
    seeds_data = summary["per_seed"]
    assert len(seeds_data) > 0, "No seed data"
    s = list(seeds_data.values())[0]
    assert s["retention_direct_replay"] is not None and s["retention_direct_replay"] > 0, \
        f"retention_direct_replay null or zero: {s['retention_direct_replay']}"
    assert s["retention_held_out"] is not None and s["retention_held_out"] > 0, \
        f"retention_held_out null or zero: {s['retention_held_out']}"
    assert s["retention_no_replay"] is not None and s["retention_no_replay"] > 0, \
        f"retention_no_replay null or zero: {s['retention_no_replay']}"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_replay_hB_collateral_v1")
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
