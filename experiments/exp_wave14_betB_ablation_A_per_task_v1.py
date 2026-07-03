"""Bet B Ablation A — per-task sub-substrate (structural-separation rescue).

Tests whether per-corpus W matrices (one W per task A/B/C) concatenated at
retrieval recover retention_A vs the 73% replay-driven ceiling of the
single-shared-W baseline (exp_wave14d_betB_kovacs_v1.py).

Mechanism:
  - Train W_A on Phase A (zero init).
  - Train W_B on Phase B (zero init; no shared params with W_A).
  - Train W_C on Phase C (zero init).
  - At retrieval, predict-byte uses average of (W_A @ ctx, W_B @ ctx, W_C @ ctx)
    -> structural separation via per-task substrate concatenation.

Pre-reg (designed inline per exp_dev_handoff_5anchors_post_v183 + user
override 'YOU design everything'):

Falsifier statements:
  - HARD-PASS:  mean retention_A >= 0.95 across 5 seeds at alpha=0.7 (matches
                base script's best-alpha output choice).
  - HARD-FAIL:  mean retention_A < 0.80 across 5 seeds.
  - MIDDLE:     0.80 <= mean retention_A < 0.95.

Comparison anchor: baseline = single-W A->B->C with replay_frac=0.5 gives
~73% retention_A (per base script Bet B Kovacs prior result).

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL bands both falsifiable
BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: structural-separation-axis
rescue path for EWC-null.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_betB_ablation_A_per_task_v1.md
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

# Reuse base script utilities.
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa  # phase_a builder module

# Inherit constants from base.
K = base.K
BETA = base.BETA
POOL_SIZE = base.POOL_SIZE
ALPHA_RETR = base.ALPHA_RETR
DELTA_ALPHA = base.DELTA_ALPHA
DELTA_DECAY = base.DELTA_DECAY
RELU_B = base.RELU_B
VOCAB = base.VOCAB
PAD_BYTE = base.PAD_BYTE

# Full-scale config (designed by exp_dev per user override).
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
REPLAY_FRAC = 0.0  # ablation: no replay within each per-task substrate
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Verdict thresholds (designed; documented above).
PASS_RETENTION = 0.95
FAIL_RETENTION = 0.80


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
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("ABLATION_A_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    ret_A_mean = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B_mean = sum(s["retention_B"] for s in seeds) / len(seeds)
    if ret_A_mean >= PASS_RETENTION:
        return ("ABLATION_A_HARD_PASS",
                f"Per-task sub-substrate concatenation recovers retention_A={ret_A_mean:.3f}>={PASS_RETENTION}; "
                f"structural-separation IS the load-bearing axis for Bet B retention. "
                f"retention_B={ret_B_mean:.3f}.")
    if ret_A_mean < FAIL_RETENTION:
        return ("ABLATION_A_HARD_FAIL",
                f"retention_A={ret_A_mean:.3f}<{FAIL_RETENTION}; structural-separation NOT load-bearing. "
                f"73% replay ceiling bounded by something other than parameter-importance OR "
                f"structural-separation. retention_B={ret_B_mean:.3f}.")
    return ("ABLATION_A_MIDDLE_BAND",
            f"retention_A={ret_A_mean:.3f} in [{FAIL_RETENTION},{PASS_RETENTION}); "
            f"partial structural-separation effect. retention_B={ret_B_mean:.3f}.")


def self_test_verdict():
    def mk(ra, rb):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb}}}
    cases = [
        (mk(0.96, 0.93), "ABLATION_A_HARD_PASS"),
        (mk(0.95, 0.90), "ABLATION_A_HARD_PASS"),
        (mk(0.85, 0.70), "ABLATION_A_MIDDLE_BAND"),
        (mk(0.80, 0.70), "ABLATION_A_MIDDLE_BAND"),
        (mk(0.79, 0.50), "ABLATION_A_HARD_FAIL"),
        (mk(0.40, 0.30), "ABLATION_A_HARD_FAIL"),
        ({}, "ABLATION_A_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def evaluate_bpc_concat(W_A, W_B, W_C, pool_v, pool_l, pool_u,
                         byte_atoms, pos_atoms, eval_bytes, eval_targets,
                         batch_size, device):
    """Multi-W readout: average the predict-byte distribution across W_A/W_B/W_C."""
    N = W_A.shape[0]
    T = eval_bytes.shape[0]
    total_bits = 0.0
    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_bytes[bs:be])
        P_W_A = pa.predict_W(W_A, ctxs, byte_atoms, BETA, N)
        P_W_B = pa.predict_W(W_B, ctxs, byte_atoms, BETA, N)
        P_W_C = pa.predict_W(W_C, ctxs, byte_atoms, BETA, N)
        P_W = (P_W_A + P_W_B + P_W_C) / 3.0
        P_retr = pa.predict_pool(ctxs, pool_v, pool_l, pool_u, BETA, N)
        P = ALPHA_RETR * P_retr + (1.0 - ALPHA_RETR) * P_W
        tgts = eval_targets[bs:be]
        p_true = P.gather(0, tgts.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total_bits += float(-torch.log2(p_true).sum())
    return total_bits / max(T, 1)


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

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)

    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx, test_b_tgt = base.bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt = base.bytes_to_idx_tensors(test_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Train 3 separate W matrices: no shared params, no cross-task replay.
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt, None, None, 0,
        n_epochs, batch_size, device)

    W_C, pool_C_v, pool_C_l, pool_C_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_c_idx, train_c_tgt, None, None, 0,
        n_epochs, batch_size, device)

    # Combined pool for retrieval (union of A/B/C task pools).
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_B_v[:pool_B_u], pool_C_v[:pool_C_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_B_l[:pool_B_u], pool_C_l[:pool_C_u]], dim=0)
    combined_u = combined_v.shape[0]

    # Baselines: single-W on each corpus alone (matches base script's bpc_*_baseline).
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_B, pool_B_v, pool_B_l, pool_B_u,
                                          byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                          batch_size, device)
    bpc_zero_on_C = base.evaluate_bpc(W_zero, None, None, 0, byte_atoms, pos_atoms,
                                         test_c_idx, test_c_tgt, batch_size, device)

    # Concat readout on each task's test split.
    bpc_A_concat = evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_B_concat = evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
                                          byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                          batch_size, device)
    bpc_C_concat = evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
                                          byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                          batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_concat, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_concat, 1e-6), 1.0)
    gain_C = bpc_zero_on_C - bpc_C_concat
    return {"retention_A": retention_A, "retention_B": retention_B, "gain_C": gain_C,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_concat": bpc_A_concat,
             "bpc_B_baseline": bpc_B_baseline, "bpc_B_concat": bpc_B_concat,
             "bpc_zero_on_C": bpc_zero_on_C, "bpc_C_concat": bpc_C_concat}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "replay_frac": REPLAY_FRAC,
              "pass_retention": PASS_RETENTION,
              "fail_retention": FAIL_RETENTION}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} "
              f"retention_B={r['retention_B']:.3f} gain_C={r['gain_C']:.4f}", flush=True)
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
    out_dir = get_output_dir("wave14_betB_ablation_A_per_task_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    seed_key = list(summary["per_seed"].keys())[0]
    r = summary["per_seed"][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_ablation_A_per_task_v1")
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
