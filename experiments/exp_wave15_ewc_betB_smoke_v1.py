"""Wave 15: EWC (Kirkpatrick 2017) for Bet B retention — first-probe smoke.

Target: lift Bet B retention from 73% baseline toward 80% threshold by adding
Fisher-information-weighted quadratic penalty to W updates during Phase-B.

Mechanism (substrate-adapted EWC):
  1. Phase-A: train W_A via standard delta-rule on corpus A.
  2. Compute Fisher diagonal F_ij = E_A[(d log p(y|x;W) / d W_ij)^2]
     over Phase-A retrieval samples (next-byte prediction loss).
  3. Phase-B: standard delta-rule update PLUS quadratic penalty
     dW_penalty = -2 * lam * F * (W - W_A)
     applied per batch. lam swept in {0, 1e-2, 1e-1, 1.0, 10.0}.
  4. Compare retention_A on held-out A after Phase-B across lam values.
     lam=0 is the no-EWC baseline (random replay only).

Hypothesis (one-line): at the best lam, retention_A on held-out A is at least
5pp higher than at lam=0, with no more than 3pp degradation on Phase-B fit.

Pre-reg: preregs/2026-05-24_wave15_ewc_betB_smoke_v1.md

Substrate: BSC N=4096 bipolar (matches Cap 5 / Bet B v153 reference).
Cost target: ~45 min CPU smoke (subset alphas, single seed) // full = ~3hr CPU
(5 lam x 5 seeds x 3 epochs).

Lit anchor:
  - Kirkpatrick et al. 2017 PNAS 'Overcoming catastrophic forgetting in neural
    networks' — original EWC.
  - Zenke, Poole, Ganguli 2017 — Synaptic Intelligence; alternative path penalty.
  - Aljundi et al. 2018 — Memory-Aware Synapses; gradient-free importance.

This script implements vanilla EWC (Fisher-diagonal); SI and MAS variants are
follow-on probes if EWC clears the 5pp threshold.

Per [[feedback-no-smoke]]: this is a rescue probe for Bet B, NOT a new
capability. If EWC works, Bet B row flips from 73%→>80%. If EWC fails,
the row stays at 73% and rescue burden shifts to other angles (replay
schedule, K nearest neighbour gating, hypernetwork).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent

# ASCII-only output per [[feedback-ascii-only-in-scripts]]
torch.set_float32_matmul_precision("high")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED_SMOKE = 17
SEEDS_FULL = [7, 17, 23, 31, 41]

N_SMOKE = 1024
N_FULL = 4096
K = 4
BETA = 8.0
VOCAB = 256
PAD_BYTE = 0
BATCH_SIZE_SMOKE = 32
BATCH_SIZE_FULL = 64
RELU_B = 0.5
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4

# EWC sweep
LAMBDAS_SMOKE = [0.0, 1.0]              # 2 values for smoke (baseline + reasonable)
LAMBDAS_FULL = [0.0, 1e-2, 1e-1, 1.0, 10.0]

EPOCHS_A_SMOKE = 2
EPOCHS_A_FULL = 5
EPOCHS_B_SMOKE = 1
EPOCHS_B_FULL = 3
BYTES_PER_CORPUS_SMOKE = 3000
BYTES_PER_CORPUS_FULL = 100000

# Verdict thresholds
PASS_DELTA_RETENTION = 0.05   # lift over lam=0
PARTIAL_DELTA_RETENTION = 0.02
PASS_MAX_PHASE_B_DEGRADATION = 0.03  # bpc on B may not degrade more than this


def _say(msg):
    print(msg, flush=True)


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


# ----- corpus -----
def load_corpus_a():
    repo = REPO
    files = ["PLAN.md", "NEXT_PHASE.md", "README.md", "PROGRESS.md", "RESULTS.md", "CLAUDE.md"]
    parts = []
    for f in files:
        p = repo / f
        if p.exists():
            parts.append(p.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def load_corpus_b():
    """Python source from a few experiment files. Distinct distribution from A."""
    exp_dir = REPO / "experiments"
    parts = []
    candidates = sorted(exp_dir.glob("exp_wave14b*.py"))[:8]
    for f in candidates:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    if not parts:
        # Fallback: any python files
        for f in sorted(exp_dir.glob("exp_*.py"))[:6]:
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


# ----- substrate primitives -----
def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx_bundles_bsc(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = ctxs @ W.T
    q = shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def bpc_from_probs(probs, targets):
    """probs: (V, B) softmax dist; targets: (B,) byte indices."""
    eps = 1e-9
    p = probs.gather(0, targets.unsqueeze(0)).clamp_min(eps)
    return float((-torch.log2(p).mean()).item())


def prep_indices(corpus_bytes, n_bytes, gen):
    data = corpus_bytes[:n_bytes]
    arr = torch.tensor(list(data), dtype=torch.long)
    T = arr.shape[0] - K - 1
    if T < 32:
        raise RuntimeError(f"corpus too short: {T}")
    starts = torch.arange(T)
    ctxs = arr[starts.unsqueeze(1) + torch.arange(K).unsqueeze(0)]  # (T, K)
    tgts = arr[starts + K]                                          # (T,)
    return ctxs, tgts


# ----- training -----
def train_delta_no_ewc(W, byte_atoms, pos_atoms, ctxs, tgts, batch_size, n_epochs):
    """Standard delta-rule, no EWC."""
    N = W.shape[0]
    T = ctxs.shape[0]
    for epoch in range(n_epochs):
        idx = torch.randperm(T)
        for b0 in range(0, T - batch_size, batch_size):
            b_idx = idx[b0:b0 + batch_size]
            x = build_ctx_bundles_bsc(byte_atoms, pos_atoms, ctxs[b_idx])  # (B, N)
            y_atoms = byte_atoms[tgts[b_idx]]                              # (B, N)
            # delta rule on W (with current W prediction)
            q = shifted_relu(x @ W.T, RELU_B)
            target = y_atoms
            pred = q
            err = target - pred  # (B, N)
            # outer-product update
            dW = (err.T @ x) / batch_size
            W = (1.0 - DELTA_DECAY) * W + DELTA_ALPHA * dW
    return W


def compute_fisher_diagonal(W, byte_atoms, pos_atoms, ctxs, tgts, batch_size, n_batches):
    """Fisher-diagonal F_ij = E_A[(d log p(y|x) / d W_ij)^2].

    log p depends on W via q = relu(x W^T - b); sims = atoms @ q.T / N;
    log p = log softmax(beta * sims).

    Analytical gradient is complex; use stochastic estimator: enable
    autograd, sum -log p over a batch, backprop, accumulate squared grad.
    """
    N = W.shape[0]
    T = ctxs.shape[0]
    F = torch.zeros_like(W)
    W = W.detach().clone().requires_grad_(True)
    count = 0
    perm = torch.randperm(T)
    for b0 in range(0, min(T - batch_size, batch_size * n_batches), batch_size):
        b_idx = perm[b0:b0 + batch_size]
        x = build_ctx_bundles_bsc(byte_atoms, pos_atoms, ctxs[b_idx])  # (B, N)
        y = tgts[b_idx]                                                # (B,)
        probs = predict_W(W, x, byte_atoms, BETA, N)                   # (V, B)
        log_p = torch.log(probs.clamp_min(1e-12))                       # (V, B)
        nll = -log_p.gather(0, y.unsqueeze(0)).mean()                  # scalar
        if W.grad is not None:
            W.grad.zero_()
        nll.backward()
        F = F + W.grad.detach() ** 2
        count += 1
    if count > 0:
        F = F / count
    return F.detach()


def train_delta_with_ewc(W, W_A, F, byte_atoms, pos_atoms, ctxs, tgts,
                            batch_size, n_epochs, lam):
    """Delta rule + EWC quadratic penalty.

    Per-batch:
       delta_W (data)    = (DELTA_ALPHA/batch) * err.T @ x
       delta_W (penalty) = -2 * lam * F * (W - W_A) * DELTA_ALPHA / batch
       W <- (1 - DELTA_DECAY) * W + delta_W(data) + delta_W(penalty)
    Penalty pulls W back toward W_A in proportion to F (importance for A).
    """
    N = W.shape[0]
    T = ctxs.shape[0]
    for epoch in range(n_epochs):
        idx = torch.randperm(T)
        for b0 in range(0, T - batch_size, batch_size):
            b_idx = idx[b0:b0 + batch_size]
            x = build_ctx_bundles_bsc(byte_atoms, pos_atoms, ctxs[b_idx])
            y_atoms = byte_atoms[tgts[b_idx]]
            q = shifted_relu(x @ W.T, RELU_B)
            err = y_atoms - q
            dW_data = (err.T @ x) / batch_size
            dW_pen = -2.0 * lam * F * (W - W_A) / batch_size if lam > 0 else 0.0
            W = (1.0 - DELTA_DECAY) * W + DELTA_ALPHA * dW_data
            if lam > 0:
                W = W + DELTA_ALPHA * dW_pen
    return W


def eval_bpc(W, byte_atoms, pos_atoms, ctxs, tgts, batch_size, max_batches=64):
    N = W.shape[0]
    T = ctxs.shape[0]
    total_bpc = 0.0
    count = 0
    for b0 in range(0, min(T - batch_size, batch_size * max_batches), batch_size):
        b_idx = torch.arange(b0, b0 + batch_size)
        x = build_ctx_bundles_bsc(byte_atoms, pos_atoms, ctxs[b_idx])
        probs = predict_W(W, x, byte_atoms, BETA, N)
        bpc = bpc_from_probs(probs, tgts[b_idx])
        total_bpc += bpc
        count += 1
    return total_bpc / max(count, 1)


# ----- experiment -----
def run_one_seed_one_lam(seed, lam, config, device):
    n = config["N"]
    batch_size = config["batch_size"]
    bytes_per = config["bytes_per_corpus"]
    epochs_a = config["epochs_a"]
    epochs_b = config["epochs_b"]

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB, n, gen).to(device)
    pos_atoms = make_bsc_atoms(K, n, gen).to(device)
    W = torch.zeros((n, n), device=device)

    corpus_a = load_corpus_a()
    corpus_b = load_corpus_b()

    ctxs_a, tgts_a = prep_indices(corpus_a, bytes_per, gen)
    ctxs_b, tgts_b = prep_indices(corpus_b, bytes_per, gen)
    # Held-out splits
    T_a = ctxs_a.shape[0]
    train_a = (ctxs_a[:int(0.8 * T_a)].to(device), tgts_a[:int(0.8 * T_a)].to(device))
    test_a = (ctxs_a[int(0.8 * T_a):].to(device), tgts_a[int(0.8 * T_a):].to(device))
    T_b = ctxs_b.shape[0]
    train_b = (ctxs_b[:int(0.8 * T_b)].to(device), tgts_b[:int(0.8 * T_b)].to(device))
    test_b = (ctxs_b[int(0.8 * T_b):].to(device), tgts_b[int(0.8 * T_b):].to(device))

    # Phase A
    W_A = train_delta_no_ewc(W, byte_atoms, pos_atoms, train_a[0], train_a[1],
                                 batch_size, epochs_a)
    bpc_A_baseline = eval_bpc(W_A, byte_atoms, pos_atoms, test_a[0], test_a[1], batch_size)

    # Fisher (on a subset of Phase-A train data)
    F = compute_fisher_diagonal(W_A, byte_atoms, pos_atoms, train_a[0], train_a[1],
                                       batch_size, n_batches=16)

    # Phase B with EWC at this lam
    W_B = train_delta_with_ewc(W_A.clone(), W_A, F, byte_atoms, pos_atoms,
                                   train_b[0], train_b[1], batch_size, epochs_b, lam)

    bpc_A_after_B = eval_bpc(W_B, byte_atoms, pos_atoms, test_a[0], test_a[1], batch_size)
    bpc_B_after_B = eval_bpc(W_B, byte_atoms, pos_atoms, test_b[0], test_b[1], batch_size)
    # Reference: B-only baseline from W_A (no Phase-B training) to compute gain
    bpc_B_pre_phase = eval_bpc(W_A, byte_atoms, pos_atoms, test_b[0], test_b[1], batch_size)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_B, 1e-6), 1.0)
    gain_B = bpc_B_pre_phase - bpc_B_after_B  # positive = improved on B
    return {
        "retention_A": retention_A,
        "gain_B": gain_B,
        "bpc_A_baseline": bpc_A_baseline,
        "bpc_A_after_B": bpc_A_after_B,
        "bpc_B_pre_phase": bpc_B_pre_phase,
        "bpc_B_after_B": bpc_B_after_B,
        "fisher_mean": float(F.mean().item()),
        "fisher_max": float(F.max().item()),
    }


def compute_verdict(summary):
    per_lam = summary.get("per_lam") or {}
    if not per_lam:
        return ("EWC_INCONCLUSIVE", "Missing per-lam results.")
    # Baseline = lam=0
    baseline = per_lam.get("0.0")
    if not baseline:
        return ("EWC_INCONCLUSIVE", "Missing lam=0 baseline.")
    # Compute mean over seeds for each lam
    def mean_field(d, field):
        vals = [s[field] for s in d.values()]
        return sum(vals) / len(vals) if vals else 0.0
    base_ret = mean_field(baseline, "retention_A")
    base_gain_b = mean_field(baseline, "gain_B")
    best_lam = None
    best_delta = -1e9
    for lam_str, seed_dict in per_lam.items():
        if lam_str == "0.0":
            continue
        ret = mean_field(seed_dict, "retention_A")
        gain_b = mean_field(seed_dict, "gain_B")
        delta = ret - base_ret
        b_degrade = base_gain_b - gain_b  # positive = EWC hurts B fit
        # Eligible if Phase-B fit not degraded beyond PASS_MAX_PHASE_B_DEGRADATION
        if b_degrade <= PASS_MAX_PHASE_B_DEGRADATION and delta > best_delta:
            best_delta = delta
            best_lam = lam_str
    if best_lam is None:
        return ("EWC_KILLED",
                  f"No lam>0 cleared Phase-B degradation cap "
                  f"({PASS_MAX_PHASE_B_DEGRADATION}). Best degrade across lam>0: "
                  f"see per_lam table; EWC penalty too aggressive at all settings.")
    if best_delta >= PASS_DELTA_RETENTION:
        return ("EWC_PASS",
                  f"lam={best_lam}: retention_A lift +{best_delta:.3f} over baseline "
                  f"(base={base_ret:.3f}); Phase-B fit within "
                  f"{PASS_MAX_PHASE_B_DEGRADATION}. Fisher-diagonal EWC rescues Bet B.")
    if best_delta >= PARTIAL_DELTA_RETENTION:
        return ("EWC_PARTIAL",
                  f"lam={best_lam}: retention_A lift +{best_delta:.3f} (>= partial "
                  f"{PARTIAL_DELTA_RETENTION} but < pass {PASS_DELTA_RETENTION}); "
                  f"signal present but insufficient for 80% threshold.")
    return ("EWC_INCONCLUSIVE",
              f"Best lift +{best_delta:.3f} below partial threshold "
              f"{PARTIAL_DELTA_RETENTION}; Fisher-diagonal weighting not effective "
              f"at tested lam grid.")


def self_test_verdict():
    def mk(lam_results):
        return {"per_lam": {lam: {"0": d} for lam, d in lam_results.items()}}
    cases = [
        (mk({"0.0": {"retention_A": 0.73, "gain_B": 0.10},
              "1.0": {"retention_A": 0.82, "gain_B": 0.09}}), "EWC_PASS"),
        (mk({"0.0": {"retention_A": 0.73, "gain_B": 0.10},
              "1.0": {"retention_A": 0.76, "gain_B": 0.09}}), "EWC_PARTIAL"),
        (mk({"0.0": {"retention_A": 0.73, "gain_B": 0.10},
              "1.0": {"retention_A": 0.74, "gain_B": 0.09}}), "EWC_INCONCLUSIVE"),
        (mk({"0.0": {"retention_A": 0.73, "gain_B": 0.10},
              "1.0": {"retention_A": 0.85, "gain_B": 0.04}}), "EWC_KILLED"),
        ({}, "EWC_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict self-test fail: got {a}, expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = DEVICE
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs_a": EPOCHS_A_SMOKE if smoke else EPOCHS_A_FULL,
        "epochs_b": EPOCHS_B_SMOKE if smoke else EPOCHS_B_FULL,
        "bytes_per_corpus": BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL,
        "lambdas": LAMBDAS_SMOKE if smoke else LAMBDAS_FULL,
        "seeds": [SEED_SMOKE] if smoke else SEEDS_FULL,
    }
    _say(f"[config] {config}")
    per_lam = {}
    for lam in config["lambdas"]:
        _say(f"[lam={lam}] sweep ...")
        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed_one_lam(seed, lam, config, device)
            per_seed[str(seed)] = r
            _say(f"  lam={lam} seed={seed}: retention_A={r['retention_A']:.3f} "
                  f"gain_B={r['gain_B']:.3f} bpc_A_after={r['bpc_A_after_B']:.3f}")
        per_lam[str(lam)] = per_seed
    summary = {"per_lam": per_lam}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    _say(f"\nVERDICT: {verdict}\n  {msg}")
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave15_ewc_betB_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    _say(f"\nSMOKE OK: {verdict}")


def run_main():
    out_dir = get_output_dir("wave15_ewc_betB_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    _say(f"\nDONE: {verdict}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
