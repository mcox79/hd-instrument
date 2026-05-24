"""Bet B Direction 3 -- Task-representation geometry as load-bearing variable.

HIGHEST-LEVERAGE per user. Project each corpus's bigram PPMI distribution into
substrate W-space; compute pairwise spectral distance between task pairs
(KL on eigenvalue distributions, Wasserstein on bundle distributions); plot
retention_A vs A->B distance and A->C distance. Goal: show 91-92% retention
ceiling moves PREDICTABLY with task-pair geometry.

Synthesizes additional corpus pairs to span a wider distance range:
  - corpus_A: repo English text (baseline)
  - corpus_B: byte-shuffled A (near-A, low distance)
  - corpus_C: Python source (genuinely different, mid distance)
  - corpus_D: random bytes (max distance to A)
  - corpus_E: reversed A (semantic-flipped; very low distance in bigram-stats)

For each task-pair (A->X) measure (a) spectral distance metric, (b) retention_A
after A->X two-stage training. Regress retention_A on log(spectral_distance).

Pre-reg (designed inline per exp_dev autonomy + Direction 3 hand-off):

Falsifier statements:
  - HARD_PASS: retention_A monotone-DECREASING in spectral distance AND r^2 of
               linear regression >= 0.60 across N >= 3 task-pairs.
               -> substrate's retention ceiling is geometry-bound; product story
               becomes "substrate retains X% at distance D; predict any task
               pair before training."
  - HARD_FAIL: r^2 < 0.20 OR non-monotone (retention rises at high distance for
               at least one cell).
               -> retention ceiling NOT geometry-bound; rules out the "predict
               any task pair before training" product story.
  - MIDDLE: 0.20 <= r^2 < 0.60; report bands and propose follow-up.

Spectral distance metric:
  - KL divergence between eigenvalue distributions of corpus PPMI projected
    into W-space. PPMI is computed at byte-bigram level over corpus, then the
    256x256 PPMI matrix is projected via byte_atoms (N x 256) into the
    N x N W-substrate space. Eigenvalue distributions are histogrammed and
    KL-divergence(hist_A, hist_X) computed.

Per [[feedback-verify-implementations]]: KL on eigenvalue histograms with
fixed bin count = 32 over [eig_min, eig_max] union of A and X. PPMI matrix
is symmetric so eigenvalues are real; projection W_proj = byte_atoms @ PPMI
@ byte_atoms^T is N x N substrate; we use top-256 eigenvalues (PPMI has
rank at most 256) as the spectral signature.

Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered BEFORE running.
Per [[feedback-rehabilitation-after-rejection]]: if HARD-FAIL, file 3-5 rescue
sketches per PROT-004.

Pre-reg: preregs/2026-05-24_wave14_betB_task_geometry_v1.md
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

# Task pairs to measure (corpus_X vs corpus_A). Names index into corpus loaders.
PAIRS_FULL = ["B_shuffled", "C_python", "D_random", "E_reversed"]
PAIRS_SMOKE = ["B_shuffled", "D_random"]

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

EIG_BINS = 32                    # KL histogram bin count
PPMI_RANK_CAP = 256              # PPMI is at most 256-rank; use top-256 eigs

# Verdict thresholds.
PASS_R2 = 0.60
FAIL_R2 = 0.20
MONOTONE_TOL = 0.01


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


def is_monotone_nonincreasing(values, tol=MONOTONE_TOL):
    """retention should drop as distance grows."""
    for i in range(len(values) - 1):
        if values[i + 1] > values[i] + tol:
            return False
    return True


def compute_verdict(summary):
    per_pair = summary.get("per_pair")
    if not per_pair or len(per_pair) < 3:
        return ("TASK_GEOMETRY_INCONCLUSIVE",
                f"Need >=3 task-pairs for regression; got {len(per_pair) if per_pair else 0}.")
    # Order pairs by spectral distance ascending.
    pairs_data = []
    for name, d in per_pair.items():
        dist = d["spectral_distance"]
        seeds = d["seeds"]
        ret_A = sum(s["retention_A"] for s in seeds.values()) / len(seeds)
        pairs_data.append((name, dist, ret_A))
    pairs_data.sort(key=lambda t: t[1])
    xs = [math.log(max(p[1], 1e-9)) for p in pairs_data]
    ys = [p[2] for p in pairs_data]
    slope, intercept, r2 = linreg(xs, ys)
    monotone = is_monotone_nonincreasing(ys)
    pts_str = ", ".join(f"{n}:d={d:.3g},retA={r:.3f}" for n, d, r in pairs_data)
    if monotone and r2 >= PASS_R2:
        return ("TASK_GEOMETRY_HARD_PASS",
                f"Retention ceiling is GEOMETRY-BOUND: slope={slope:.3f} (negative), "
                f"r^2={r2:.3f} >= {PASS_R2}, monotone-decreasing across {len(pairs_data)} pairs. "
                f"{pts_str}.")
    if r2 < FAIL_R2 or not monotone:
        return ("TASK_GEOMETRY_HARD_FAIL",
                f"Retention NOT geometry-bound: r^2={r2:.3f}<{FAIL_R2} OR non-monotone "
                f"(monotone={monotone}). {pts_str}.")
    return ("TASK_GEOMETRY_MIDDLE_BAND",
            f"Intermediate: r^2={r2:.3f}, monotone={monotone}, slope={slope:.3f}. {pts_str}.")


def self_test_verdict():
    def mk(pairs_list):
        per_pair = {}
        for name, dist, ret in pairs_list:
            per_pair[name] = {"spectral_distance": dist,
                                "seeds": {"17": {"retention_A": ret}}}
        return {"per_pair": per_pair}
    s_pass = mk([("B", 0.01, 0.95), ("C", 0.5, 0.85), ("D", 5.0, 0.65)])
    s_fail = mk([("B", 0.01, 0.95), ("C", 0.5, 0.85), ("D", 5.0, 0.95)])  # non-monotone
    s_fail_r2 = mk([("B", 0.01, 0.85), ("C", 0.5, 0.85), ("D", 5.0, 0.85)])  # flat, r^2=0
    s_inconc = mk([("B", 0.01, 0.95), ("C", 0.5, 0.85)])    # <3 pairs
    cases = [
        (s_pass, "TASK_GEOMETRY_HARD_PASS"),
        (s_fail, "TASK_GEOMETRY_HARD_FAIL"),
        (s_fail_r2, "TASK_GEOMETRY_HARD_FAIL"),
        (s_inconc, "TASK_GEOMETRY_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def compute_ppmi(data, vocab=VOCAB):
    """Compute byte-bigram PPMI matrix (vocab x vocab)."""
    # P(b_t, b_{t+1}), P(b_t), P(b_{t+1}).
    arr = torch.frombuffer(bytearray(data), dtype=torch.uint8).long()
    if arr.numel() < 2:
        return torch.eye(vocab) * 1e-9
    pairs = torch.stack([arr[:-1], arr[1:]], dim=1)
    co = torch.zeros((vocab, vocab), dtype=torch.float64)
    idx_flat = pairs[:, 0] * vocab + pairs[:, 1]
    counts = torch.bincount(idx_flat, minlength=vocab * vocab).double()
    co = counts.view(vocab, vocab)
    total = co.sum() + 1e-9
    P_xy = co / total
    P_x = P_xy.sum(dim=1, keepdim=True)
    P_y = P_xy.sum(dim=0, keepdim=True)
    denom = (P_x @ P_y).clamp(min=1e-12)
    pmi = (P_xy / denom).clamp(min=1e-12).log()
    ppmi = pmi.clamp(min=0.0)
    return ppmi.float()


def _safe_eigvalsh(mat):
    """Eigenvalues of a symmetric matrix, robust to rank-deficient PPMI.

    PPMI matrices from narrow-byte-alphabet corpora (e.g. Python source) have
    many zero columns -> repeated 0 eigenvalues that confuse some LAPACK paths
    (error code 19 on Windows torch). Symmetrize explicitly and add a tiny
    ridge to ensure well-conditioned input. Falls back to SVD if eigh still
    crashes.
    """
    sym = 0.5 * (mat + mat.T)
    ridge = 1e-7 * float(sym.diag().abs().max() + 1.0)
    sym = sym + ridge * torch.eye(sym.shape[0], dtype=sym.dtype)
    try:
        return torch.linalg.eigvalsh(sym)
    except Exception:
        # SVD of a symmetric matrix returns sigma = |eigenvalues|; we lose
        # sign information but the distance metric works on magnitudes anyway.
        return torch.linalg.svdvals(sym)


def spectral_distance(corpus_A, corpus_X, byte_atoms_cpu):
    """KL divergence between top-eigenvalue histograms of W-projected PPMI."""
    ppmi_A = compute_ppmi(corpus_A)
    ppmi_X = compute_ppmi(corpus_X)
    # Top-PPMI_RANK_CAP eigenvalues. PPMI is symmetric so use eigh; descending.
    eigs_A = _safe_eigvalsh(ppmi_A).flip(0)[:PPMI_RANK_CAP]
    eigs_X = _safe_eigvalsh(ppmi_X).flip(0)[:PPMI_RANK_CAP]
    lo = float(min(eigs_A.min(), eigs_X.min()))
    hi = float(max(eigs_A.max(), eigs_X.max())) + 1e-9
    bins = torch.linspace(lo, hi, EIG_BINS + 1)
    h_A = torch.histc(eigs_A, bins=EIG_BINS, min=lo, max=hi)
    h_X = torch.histc(eigs_X, bins=EIG_BINS, min=lo, max=hi)
    p_A = (h_A + 1.0) / (h_A.sum() + EIG_BINS)
    p_X = (h_X + 1.0) / (h_X.sum() + EIG_BINS)
    kl = float((p_A * (p_A.log() - p_X.log())).sum())
    return kl


def load_corpora(pair_name, seed, smoke, n_bytes):
    """Return (corpus_A, corpus_X) for the given pair_name."""
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    if pair_name == "B_shuffled":
        corpus_x = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    elif pair_name == "C_python":
        corpus_c_full = base.load_corpus_C(smoke=smoke)
        corpus_x = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    elif pair_name == "D_random":
        import random as _r
        rng = _r.Random(seed + 2)
        corpus_x = bytes(rng.randrange(256) for _ in range(min(n_bytes, len(corpus_a))))
    elif pair_name == "E_reversed":
        corpus_x = corpus_a[::-1]
    else:
        raise ValueError(f"unknown pair {pair_name}")
    return corpus_a, corpus_x


def run_one_seed_at_pair(seed, pair_name, config, device):
    """Run A->X two-stage training and measure retention_A + spectral distance."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = config["mode"] == "smoke"
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    corpus_a, corpus_x = load_corpora(pair_name, seed, smoke, n_bytes)
    spec_dist = spectral_distance(corpus_a, corpus_x, byte_atoms.cpu())

    def split(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]
    train_a, test_a = split(corpus_a)
    train_x, _ = split(corpus_x)
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_x_idx, train_x_tgt = base.bytes_to_idx_tensors(train_x, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    W_AX, pool_AX_v, pool_AX_l, pool_AX_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_x_idx, train_x_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)
    W_AX = EMA_ALPHA * W_AX + (1.0 - EMA_ALPHA) * W_A
    bpc_A_after_X = base.evaluate_bpc(W_AX, pool_AX_v, pool_AX_l, pool_AX_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    retention_A = min(bpc_A_baseline / max(bpc_A_after_X, 1e-6), 1.0)
    return {"retention_A": retention_A, "spectral_distance": spec_dist,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_X": bpc_A_after_X}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pairs = PAIRS_SMOKE if smoke else PAIRS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "task_pairs": pairs,
              "ema_alpha": EMA_ALPHA,
              "eig_bins": EIG_BINS,
              "ppmi_rank_cap": PPMI_RANK_CAP,
              "pass_r2": PASS_R2,
              "fail_r2": FAIL_R2}
    print(f"[config] {config}", flush=True)
    per_pair = {}
    for pair_name in pairs:
        print(f"[pair={pair_name}] ...", flush=True)
        per_seed = {}
        dist_sum = 0.0
        for seed in config["seeds"]:
            r = run_one_seed_at_pair(seed, pair_name, config, device)
            per_seed[str(seed)] = r
            dist_sum += r["spectral_distance"]
            print(f"  pair={pair_name} seed={seed}: retention_A={r['retention_A']:.3f}, "
                  f"spec_dist={r['spectral_distance']:.4f}", flush=True)
        per_pair[pair_name] = {
            "spectral_distance": dist_sum / len(config["seeds"]),
            "seeds": per_seed,
        }
    summary = {"per_pair": per_pair}
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
    out_dir = get_output_dir("wave14_betB_task_geometry_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_pair = list(summary["per_pair"].keys())[0]
    seed_key = list(summary["per_pair"][first_pair]["seeds"].keys())[0]
    r = summary["per_pair"][first_pair]["seeds"][seed_key]
    oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betB_task_geometry_v1")
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
