"""Bet B compound — per-task sub-substrate + cross-task replay axis stacking.

v185 pre-registered axis-stacking probe. Ablation A (v185) confirmed per-task
sub-substrate gives +9pp retention_A above baseline (0.821 in MIDDLE band).
Ablation B (parallel ship) bounds replay-only ceiling.

This compound script tests whether stacking the two structural-separation axes
(per-task substrates AND cross-task replay) clears the HARD-PASS 0.95 gate that
neither axis alone could clear.

Mechanism:
  - Train W_A on Phase A with NO replay (zero-init, no shared params).
  - Train W_B on Phase B with replay_frac=REPLAY_FRAC against the Phase A pool.
  - Train W_C on Phase C with replay_frac=REPLAY_FRAC against the (A+B) pool.
  - At retrieval, predict-byte uses average of (W_A @ ctx, W_B @ ctx, W_C @ ctx)
    -> per-task substrate concatenation (same as Ablation A) PLUS cross-task
    replay during B and C training.

Pre-reg (designed inline; v185 axis-stacking pre-registered untested):

Falsifier statements:
  - HARD-PASS:  mean retention_A >= 0.95 across 5 seeds. Compound axis-stacking
                CLEARS the HARD-PASS gate; both per-task substrates AND replay
                are required for full retention.
  - HARD-FAIL:  mean retention_A <= 0.821 (the v185 Ablation A point estimate).
                Cross-task replay does NOT add anything on top of per-task
                substrates -- the +9pp lift is the structural ceiling.
  - MIDDLE:     0.821 < mean retention_A < 0.95. Partial stacking benefit:
                replay adds something but compound still does not clear HARD-PASS.

Comparison anchors:
  - Bet B Kovacs baseline (single shared W + replay): ~73% retention_A.
  - Ablation A (per-task, no replay): 82.1% retention_A (v185 verdict).
  - Ablation B (single W, replay sweep): pending verdict (parallel ship).
  - This compound: TBD; pre-reg says HARD-PASS at 95%, HARD-FAIL at <=82.1%.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: axis-stacking rescue path
for the v185-confirmed conditional structural-separation axis.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_betB_compound_pertask_replay_v1.md
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

# Reuse base Kovacs + Ablation A modules.
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec_b = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec_b)
_spec_b.loader.exec_module(base)
pa = base.pa

_aa_path = REPO / "experiments" / "exp_wave14_betB_ablation_A_per_task_v1.py"
_spec_aa = importlib.util.spec_from_file_location("aa", _aa_path)
aa = importlib.util.module_from_spec(_spec_aa)
_spec_aa.loader.exec_module(aa)

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

# Full-scale config (designed by exp_dev; matches Ablation A protocol).
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
REPLAY_FRAC = 0.5  # axis-stacking ON: cross-task replay during B and C.
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Verdict thresholds (designed; documented above).
PASS_RETENTION = 0.95
FAIL_RETENTION = 0.821  # v185 Ablation A point estimate; compound must beat this.


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
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("COMPOUND_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    ret_A_mean = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B_mean = sum(s["retention_B"] for s in seeds) / len(seeds)
    if ret_A_mean >= PASS_RETENTION:
        return ("COMPOUND_HARD_PASS",
                f"Axis-stacking PASSES: per-task substrates + cross-task replay "
                f"recover retention_A={ret_A_mean:.3f}>={PASS_RETENTION}; both axes "
                f"required for full retention. retention_B={ret_B_mean:.3f}.")
    if ret_A_mean <= FAIL_RETENTION:
        return ("COMPOUND_HARD_FAIL",
                f"Cross-task replay adds nothing on top of per-task substrates: "
                f"retention_A={ret_A_mean:.3f}<={FAIL_RETENTION} (v185 Ablation A point); "
                f"+9pp lift is the structural ceiling. retention_B={ret_B_mean:.3f}.")
    return ("COMPOUND_MIDDLE_BAND",
            f"retention_A={ret_A_mean:.3f} in ({FAIL_RETENTION},{PASS_RETENTION}); "
            f"partial axis-stacking benefit; replay adds something but compound "
            f"still does NOT clear HARD-PASS. retention_B={ret_B_mean:.3f}.")


def self_test_verdict():
    def mk(ra, rb):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb}}}
    cases = [
        (mk(0.96, 0.93), "COMPOUND_HARD_PASS"),
        (mk(0.95, 0.90), "COMPOUND_HARD_PASS"),
        (mk(0.87, 0.85), "COMPOUND_MIDDLE_BAND"),
        (mk(0.85, 0.80), "COMPOUND_MIDDLE_BAND"),
        (mk(0.821, 0.70), "COMPOUND_HARD_FAIL"),
        (mk(0.80, 0.70), "COMPOUND_HARD_FAIL"),
        (mk(0.40, 0.30), "COMPOUND_HARD_FAIL"),
        ({}, "COMPOUND_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed_compound(seed, config, device):
    """Compound: per-task W matrices WITH cross-task replay during B and C training."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    replay_frac = config["replay_frac"]
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

    # Phase A: zero-init, no replay (no prior pool).
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)

    # Phase B: zero-init W_B, but USE replay against Phase A's pool (axis-stacking).
    W_B, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt, pool_A_v, pool_A_l, pool_A_u,
        n_epochs, batch_size, device)

    # Combined (A+B) pool for Phase C replay source.
    combined_AB_v = torch.cat([pool_A_v[:pool_A_u], pool_B_v[:pool_B_u]], dim=0)
    combined_AB_l = torch.cat([pool_A_l[:pool_A_u], pool_B_l[:pool_B_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]

    # Phase C: zero-init W_C, replay against (A+B) combined pool.
    W_C, pool_C_v, pool_C_l, pool_C_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_c_idx, train_c_tgt, combined_AB_v, combined_AB_l, combined_AB_u,
        n_epochs, batch_size, device)

    # Full combined pool for retrieval (union of A/B/C task pools).
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_B_v[:pool_B_u], pool_C_v[:pool_C_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_B_l[:pool_B_u], pool_C_l[:pool_C_u]], dim=0)
    combined_u = combined_v.shape[0]

    # Baselines.
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_B, pool_B_v, pool_B_l, pool_B_u,
                                          byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                          batch_size, device)
    bpc_zero_on_C = base.evaluate_bpc(W_zero, None, None, 0, byte_atoms, pos_atoms,
                                         test_c_idx, test_c_tgt, batch_size, device)

    # Concat readout on each task's test split (reuse Ablation A's evaluator).
    bpc_A_concat = aa.evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
                                              byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                              batch_size, device)
    bpc_B_concat = aa.evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
                                              byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                              batch_size, device)
    bpc_C_concat = aa.evaluate_bpc_concat(W_A, W_B, W_C, combined_v, combined_l, combined_u,
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
        r = run_one_seed_compound(seed, config, device)
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
    out_dir = get_output_dir("wave14_betB_compound_pertask_replay_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    seed_key = list(summary["per_seed"].keys())[0]
    r = summary["per_seed"][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_compound_pertask_replay_v1")
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
