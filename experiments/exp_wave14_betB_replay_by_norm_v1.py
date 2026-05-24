"""Bet B Direction 2 -- Replay weighted by bundle-norm (high-density regions of W).

Substrate-specific replay scheme. Weights Phase A replay samples by their
bundle-norm (||ctx||_2 in W-space), drawing more frequently from high-density
regions. Compares against uniform/random replay (the existing Bet B mechanism).

Pre-reg (designed inline per exp_dev autonomy + Direction 2 hand-off):

Falsifier statements:
  - HARD_PASS: bundle-norm weighted replay achieves retention_A >= 0.80 at the
               same replay_frac=0.50 as random replay. This closes the 7pp gap
               from the 73% baseline and beats random replay's empirical ~91-92%
               ceiling by being at least neutral. Replay-by-vulnerability
               validated.
               NOTE: revised against actual baseline -- current compound is
               already at 91-92%, so HARD_PASS for "closes 7pp gap" is now
               re-framed as "matches OR beats compound at 91-92% AT WEIGHTED
               (i.e., >= 0.91 retention_A)".
  - HARD_FAIL: bundle-norm weighted replay falls more than 2pp below uniform
               replay across the A->B->C pipeline; norm-weighting hurts.
               Bundle-norm NOT the load-bearing weighting axis.
  - MIDDLE: weighted within +/- 2pp of uniform; report.

Comparison anchor: uniform/random replay at replay_frac=0.50 with current
compound mechanism gives retention_A ~ 0.91-0.92 (v189 4-stage probe partial).

Two replay modes compared:
  - 'uniform': existing replay (samples drawn uniformly from pool)
  - 'norm_weighted': samples drawn with probability proportional to ||ctx||_2

Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: substrate-novel replay scheme;
if HARD-FAIL, bundle-norm is closed as the weighting axis (other candidates
remain: per-stage W-distance, gradient-norm, vulnerability-score).
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_betB_replay_by_norm_v1.md
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
REPLAY_FRAC_FIXED = 0.50

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

MODES_FULL = ["uniform", "norm_weighted"]
MODES_SMOKE = ["uniform", "norm_weighted"]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Verdict thresholds.
PASS_RETENTION = 0.91
DELTA_FAIL = 0.02     # weighted falls this far below uniform -> HARD_FAIL
DELTA_TIE = 0.02      # within +/- this of uniform -> MIDDLE


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
    by_mode = summary.get("per_mode")
    if not by_mode or "uniform" not in by_mode or "norm_weighted" not in by_mode:
        return ("REPLAY_NORM_INCONCLUSIVE",
                f"Missing per_mode data; keys={list(by_mode.keys()) if by_mode else None}.")
    def mean_ret(d):
        return sum(s["retention_A"] for s in d.values()) / len(d)
    ret_uniform = mean_ret(by_mode["uniform"])
    ret_weighted = mean_ret(by_mode["norm_weighted"])
    delta = ret_weighted - ret_uniform
    msg_anchor = f"ret_uniform={ret_uniform:.3f}, ret_weighted={ret_weighted:.3f}, delta={delta:+.3f}"
    if ret_weighted >= PASS_RETENTION and delta >= -DELTA_TIE:
        return ("REPLAY_NORM_HARD_PASS",
                f"Norm-weighted replay matches-or-beats uniform at {PASS_RETENTION}+; "
                f"{msg_anchor}. Replay-by-vulnerability validated.")
    if delta <= -DELTA_FAIL:
        return ("REPLAY_NORM_HARD_FAIL",
                f"Norm-weighted replay falls >={DELTA_FAIL} below uniform; "
                f"{msg_anchor}. Bundle-norm NOT the load-bearing weighting axis.")
    return ("REPLAY_NORM_MIDDLE_BAND",
            f"Norm-weighted within +/-{DELTA_TIE} of uniform; {msg_anchor}.")


def self_test_verdict():
    def mk(u_ret, w_ret):
        return {"per_mode": {"uniform": {"17": {"retention_A": u_ret}},
                              "norm_weighted": {"17": {"retention_A": w_ret}}}}
    cases = [
        (mk(0.91, 0.92), "REPLAY_NORM_HARD_PASS"),
        (mk(0.91, 0.85), "REPLAY_NORM_HARD_FAIL"),
        (mk(0.91, 0.90), "REPLAY_NORM_MIDDLE_BAND"),
        ({"per_mode": {}}, "REPLAY_NORM_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def train_w_with_norm_weighted_replay(
        W_init, pool_vecs, pool_labels, pool_used,
        byte_atoms, pos_atoms, train_bytes, target_bytes,
        replay_pool_vecs, replay_pool_labels, replay_pool_used,
        n_epochs, batch_size, mode, device):
    """Same as base.train_w_with_replay BUT replay sampling depends on `mode`:
    'uniform'       -- randperm (existing behavior)
    'norm_weighted' -- prob proportional to ||ctx||_2 over the active replay pool.
    """
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

    # Precompute replay sampling weights if norm_weighted.
    replay_probs = None
    if replay_pool_vecs is not None and replay_pool_used > 0 and mode == "norm_weighted":
        active = replay_pool_vecs[:replay_pool_used]
        norms = torch.norm(active, dim=1) + 1e-9   # avoid /0 on zero-rows
        replay_probs = norms / norms.sum()

    for epoch in range(n_epochs):
        for batch_start in range(0, T, batch_size):
            be = min(batch_start + batch_size, T)
            idx_batch = train_bytes[batch_start:be]
            tgt_batch = target_bytes[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch)
            if replay_pool_vecs is not None and replay_pool_used > 0:
                n_replay = max(1, int(REPLAY_FRAC_FIXED * B))
                if mode == "norm_weighted" and replay_probs is not None:
                    replay_idx = torch.multinomial(replay_probs, n_replay, replacement=True)
                else:
                    replay_idx = torch.randperm(replay_pool_used, device=device)[:n_replay]
                replay_ctxs = replay_pool_vecs[replay_idx]
                replay_tgts = replay_pool_labels[replay_idx]
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


def run_one_seed_at_mode(seed, mode, config, device):
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

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]
    train_a, test_a = split(corpus_a)
    train_b, _ = split(corpus_b)
    train_c, _ = split(corpus_c)
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_norm_weighted_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, mode, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_norm_weighted_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, mode, device)
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_u = combined_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_norm_weighted_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_v, combined_l, combined_u, n_epochs, batch_size, mode, device)
    W_ABC = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
    bpc_A_after_C = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    return {"retention_A": retention_A,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "mode": mode}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    modes = MODES_SMOKE if smoke else MODES_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "replay_modes": modes,
              "replay_frac": REPLAY_FRAC_FIXED,
              "ema_alpha": EMA_ALPHA,
              "pass_retention": PASS_RETENTION,
              "delta_fail": DELTA_FAIL,
              "delta_tie": DELTA_TIE}
    print(f"[config] {config}", flush=True)
    per_mode = {}
    for mode in modes:
        print(f"[mode={mode}] ...", flush=True)
        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed_at_mode(seed, mode, config, device)
            per_seed[str(seed)] = r
            print(f"  mode={mode} seed={seed}: retention_A={r['retention_A']:.3f}", flush=True)
        per_mode[mode] = per_seed
    summary = {"per_mode": per_mode}
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
    out_dir = get_output_dir("wave14_betB_replay_by_norm_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_mode = list(summary["per_mode"].keys())[0]
    seed_key = list(summary["per_mode"][first_mode].keys())[0]
    r = summary["per_mode"][first_mode][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_replay_by_norm_v1")
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
