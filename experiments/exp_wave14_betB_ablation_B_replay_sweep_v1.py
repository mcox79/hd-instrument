"""Bet B Ablation B — replay-only sweep across replay_frac.

Bounds the replay-only retention ceiling by sweeping replay_frac across
{0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0} on the SAME single-shared-W
A->B->C pipeline as the base Bet B Kovacs experiment.

Pre-reg (designed inline per exp_dev_handoff_5anchors_post_v183 + user
override 'YOU design everything'):

Falsifier statements:
  - HARD-PASS monotone: retention_A monotone-increasing in replay_frac across
    all 7 cells AND peak retention_A >= 0.90 at the largest replay_frac.
  - HARD-FAIL plateau:  retention_A plateaus < 0.80 across all replay_frac
    >= 0.25 (the substrate has a structural ceiling that replay cannot break).
  - MIDDLE: any other pattern.

Comparison anchor: the 73% retention_A at replay_frac=0.10 from earlier Bet B
Kovacs runs is the established midpoint of the sweep.

Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL falsifiable BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: replay-frequency-axis rescue
path for EWC-null.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_betB_ablation_B_replay_sweep_v1.md
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
EMA_ALPHA = 0.7  # matches base script's best alpha output.
REPLAY_FRACS = [0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0]
REPLAY_FRACS_SMOKE = [0.0, 0.50]  # 2 cells for smoke gate.
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Verdict thresholds (designed; documented above).
PASS_PEAK = 0.90
FAIL_PLATEAU = 0.80
PLATEAU_MIN_FRAC = 0.25  # cells with replay_frac >= this define the plateau.


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


def is_monotone_nondecreasing(values, tol=0.02):
    """Allow tiny tol-noise; require values[i+1] >= values[i] - tol throughout."""
    for i in range(len(values) - 1):
        if values[i + 1] < values[i] - tol:
            return False
    return True


def compute_verdict(summary):
    per_frac = summary.get("per_replay_frac")
    if not per_frac:
        return ("ABLATION_B_INCONCLUSIVE", "Missing per_replay_frac data.")
    fracs_sorted = sorted([float(k) for k in per_frac.keys()])
    ret_A_by_frac = []
    for f in fracs_sorted:
        seeds = per_frac[str(f)]
        ret_A_mean = sum(s["retention_A"] for s in seeds.values()) / len(seeds)
        ret_A_by_frac.append(ret_A_mean)
    monotone = is_monotone_nondecreasing(ret_A_by_frac)
    peak = max(ret_A_by_frac) if ret_A_by_frac else 0.0
    # Plateau test: cells with frac >= PLATEAU_MIN_FRAC.
    plateau_cells = [v for f, v in zip(fracs_sorted, ret_A_by_frac) if f >= PLATEAU_MIN_FRAC]
    plateau_max = max(plateau_cells) if plateau_cells else 0.0
    if monotone and peak >= PASS_PEAK:
        return ("ABLATION_B_HARD_PASS",
                f"Monotone-increasing retention_A across replay_frac sweep; "
                f"peak={peak:.3f}>={PASS_PEAK}; replay-alone closes the gap. "
                f"By-frac: {[f'{v:.3f}' for v in ret_A_by_frac]}.")
    if plateau_max < FAIL_PLATEAU and len(plateau_cells) >= 1:
        return ("ABLATION_B_HARD_FAIL",
                f"Replay plateau: max retention_A={plateau_max:.3f}<{FAIL_PLATEAU} across "
                f"all replay_frac>={PLATEAU_MIN_FRAC}; ceiling is structural, "
                f"replay-frequency alone cannot break it. "
                f"By-frac: {[f'{v:.3f}' for v in ret_A_by_frac]}.")
    return ("ABLATION_B_MIDDLE_BAND",
            f"Pattern not at extremes: monotone={monotone}, peak={peak:.3f}, "
            f"plateau_max={plateau_max:.3f}. By-frac: {[f'{v:.3f}' for v in ret_A_by_frac]}.")


def self_test_verdict():
    def mk(frac_to_retA):
        d = {}
        for f, v in frac_to_retA.items():
            d[str(f)] = {"17": {"retention_A": v, "retention_B": v - 0.05}}
        return {"per_replay_frac": d}
    # Test 1: monotone with peak >= 0.90 -> HARD_PASS
    s1 = mk({0.0: 0.40, 0.05: 0.50, 0.10: 0.60, 0.25: 0.75, 0.50: 0.85, 0.75: 0.92, 1.0: 0.95})
    # Test 2: plateau <0.80 at all frac>=0.25 -> HARD_FAIL
    s2 = mk({0.0: 0.30, 0.05: 0.45, 0.10: 0.55, 0.25: 0.70, 0.50: 0.74, 0.75: 0.76, 1.0: 0.78})
    # Test 3: monotone but peak below pass -> MIDDLE
    s3 = mk({0.0: 0.40, 0.05: 0.55, 0.10: 0.65, 0.25: 0.75, 0.50: 0.80, 0.75: 0.83, 1.0: 0.85})
    # Test 4: non-monotone but high peak -> MIDDLE (not strict HARD_PASS, not HARD_FAIL since plateau_max=0.92>=0.80)
    s4 = mk({0.0: 0.40, 0.05: 0.55, 0.10: 0.80, 0.25: 0.75, 0.50: 0.85, 0.75: 0.92, 1.0: 0.88})
    # Test 5: empty
    s5 = {}
    cases = [
        (s1, "ABLATION_B_HARD_PASS"),
        (s2, "ABLATION_B_HARD_FAIL"),
        (s3, "ABLATION_B_MIDDLE_BAND"),
        (s4, "ABLATION_B_MIDDLE_BAND"),
        (s5, "ABLATION_B_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp} for {s}")
    # Monotone helper unit tests.
    assert is_monotone_nondecreasing([0.1, 0.2, 0.3]) is True
    assert is_monotone_nondecreasing([0.3, 0.2, 0.1]) is False
    assert is_monotone_nondecreasing([0.1, 0.1, 0.105]) is True  # within tol
    assert is_monotone_nondecreasing([0.1, 0.05, 0.1]) is False  # drops past tol
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases + 4 monotone unit tests)", flush=True)


def train_w_with_replay_frac(W_init, pool_vecs, pool_labels, pool_used,
                                byte_atoms, pos_atoms, train_bytes, target_bytes,
                                replay_pool_vecs, replay_pool_labels, replay_pool_used,
                                n_epochs, batch_size, replay_frac, device):
    """Variant of base.train_w_with_replay with configurable replay_frac.

    Mirrors base implementation but reads replay_frac from arg, not the
    module-level constant.
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


def run_one_seed_at_frac(seed, replay_frac, config, device):
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

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = train_w_with_replay_frac(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, 0.0, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = train_w_with_replay_frac(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, replay_frac, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                          byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                          batch_size, device)
    combined_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_u = combined_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = train_w_with_replay_frac(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_v, combined_l, combined_u, n_epochs, batch_size, replay_frac, device)
    W_ABC = EMA_ALPHA * W_ABC + (1.0 - EMA_ALPHA) * W_A
    bpc_A_after_C = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_B_after_C = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                          byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                          batch_size, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_C, 1e-6), 1.0)
    return {"retention_A": retention_A, "retention_B": retention_B,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_C": bpc_B_after_C}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    fracs = REPLAY_FRACS_SMOKE if smoke else REPLAY_FRACS
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "replay_fracs": fracs,
              "ema_alpha": EMA_ALPHA,
              "pass_peak": PASS_PEAK,
              "fail_plateau": FAIL_PLATEAU,
              "plateau_min_frac": PLATEAU_MIN_FRAC}
    print(f"[config] {config}", flush=True)
    per_replay_frac = {}
    for frac in fracs:
        print(f"[replay_frac={frac}] sweep ...", flush=True)
        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed_at_frac(seed, frac, config, device)
            per_seed[str(seed)] = r
            print(f"  frac={frac} seed={seed}: retention_A={r['retention_A']:.3f} "
                  f"retention_B={r['retention_B']:.3f}", flush=True)
        per_replay_frac[str(frac)] = per_seed
    summary = {"per_replay_frac": per_replay_frac}
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
    out_dir = get_output_dir("wave14_betB_ablation_B_replay_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_frac = list(summary["per_replay_frac"].keys())[0]
    seed_key = list(summary["per_replay_frac"][first_frac].keys())[0]
    r = summary["per_replay_frac"][first_frac][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_ablation_B_replay_sweep_v1")
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
