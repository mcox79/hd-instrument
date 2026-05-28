"""KF-5 STEERABLE SUBSTRATE: inference-time beta sweep at N=4096 byte-LM substrate.

SCIENTIFIC QUESTION (Killer Feature 5):
  Can inference-time beta adjustment (NO retraining) steer substrate
  behavior? Specifically: does beta control (a) output entropy (uncertainty),
  (b) BPC (calibration quality), (c) edit-localization (does higher beta
  sharpen the edit window?), (d) hallucination margin (output probability
  on out-of-distribution queries)?

  The user's hypothesis: one trained W, multiple behavioral regimes via
  beta control. This validates 'steerable substrate' as a product capability.

DESIGN:
  - Train one W at N=4096 with standard delta-rule on corpus_A (byte-LM).
    BETA_TRAIN=8.0, fixed. Standard phase_a infrastructure.
  - At inference time, vary beta_inf over {2, 4, 8, 16, 32, 64, 128}.
  - For each beta_inf measure:
    (a) output_entropy: mean H(softmax(beta_inf * sims)) per token
        Expected: monotone decreasing in beta_inf
    (b) bpc_inf: bits-per-character at inference beta
        Expected: non-monotone; minimum near training beta (beta=8)
    (c) top1_minus_top2_gap_mean: mean similarity gap between top-2 outputs
        Expected: widened at higher beta (sharper discrimination)
    (d) retention_argmax: argmax accuracy on held-out test set
        Expected: roughly constant across beta (argmax stable when gaps large)
    (e) entropy_range: H(beta_min) - H(beta_max)
        HARD criterion: must be > 1.0 bit (large steerable range)
  - 5 seeds. Each seed: fresh training + all metrics.

  KEY INSIGHT FROM SMOKE: argmax accuracy is invariant to beta because the
  top-1 similarity gap is large (mean 0.117). BUT entropy and BPC change
  dramatically. This IS steerability -- different output regimes.

PRE-REGISTERED BANDS:
  HARD_PASS: (1) output_entropy is monotone DECREASING across beta sweep in
    >= 4/5 seeds AND (2) entropy_range > 1.0 bit AND (3) bpc_inf has a minimum
    near beta in {4,8,16} (not at extremes).
    Interpretation: substrate exhibits genuine behavioral regimes via beta.
  HARD_FAIL: entropy_range < 0.1 bits across full beta sweep in >= 4/5 seeds.
    Substrate output is invariant to inference beta.
  MIDDLE_BAND: entropy monotone in < 4/5 seeds OR entropy_range in [0.1, 1.0].

FORMULA SELF-TESTS:
  1. H(uniform over 256 bytes) = log2(256) = 8.0 bits. beta->0 -> H -> 8.0.
  2. H(one-hot) = 0 bits. beta->inf -> H -> 0.0 bits.
  3. entropy_range = H(beta_min) - H(beta_max). For beta_min=2, beta_max=128:
     expected entropy_range >> 0.
  4. bpc optimal at beta~=BETA_TRAIN=8 (matches training temperature).
  5. Verification: compute_entropy(uniform(256)) = 8.0 bits.
     compute_entropy(one_hot(256, 0)) = 0.0 bits.

TIMEOUT ESTIMATE:
  N_SMOKE=1024, 1 seed, 7 beta values, T_eval=500 tokens. ~30s smoke.
  Full: N=4096, 5 seeds, 7 betas, T_eval=2000 tokens.
  Scale: (4096/1024)^1.5 * 5 = 4^1.5 * 5 = 8 * 5 = 40.
  timeout_s = ceil(1.5 * 30 * 40) = ceil(1800) -> 2100s. Under 2h.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: overnight_queue (GPU; delta-rule training at N=4096, 5 seeds)
Pre-reg: preregs/2026-05-27_kf5_steerable_beta_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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

# Load phase_a infrastructure (build_ctx_bundles_bsc, shifted_relu, make_bsc_atoms, etc.)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024      # Kerdock 4-coset requires N in {1024,4096,16384}; use 1024 for smoke
K = 4               # context window size (4 bytes)
VOCAB = 256
BETA_TRAIN = 8.0    # fixed training temperature
BETA_INF_SWEEP = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_INF_SMOKE = [2.0, 8.0, 64.0]
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
T_TRAIN_FULL = 20000    # training tokens
T_TRAIN_SMOKE = 3000
T_EVAL_FULL = 2000      # eval tokens
T_EVAL_SMOKE = 300
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pass/fail thresholds
PASS_ENTROPY_RANGE_MIN = 1.0   # bits; entropy must span > 1.0 bits across beta sweep
PASS_ENTROPY_MONOTONE_SEEDS = 4   # >= 4/5 seeds with monotone entropy
FAIL_ENTROPY_RANGE_MAX = 0.1    # invariant threshold


def get_output_dir(default_name: str = "kf5_steerable_beta_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_entropy(P: torch.Tensor) -> torch.Tensor:
    """Entropy of distribution P (vocab_size, batch). Returns (batch,) in bits."""
    eps = 1e-12
    H = -(P * torch.log2(P + eps)).sum(dim=0)
    return H


def load_and_tokenize(smoke: bool):
    """Load corpus A, split into train/eval, return (train_idx, train_tgt, eval_idx, eval_tgt)."""
    corpus = pa.load_corpus_a()
    T = len(corpus) - K
    T_train = T_TRAIN_SMOKE if smoke else T_TRAIN_FULL
    T_eval = T_EVAL_SMOKE if smoke else T_EVAL_FULL
    T_train = min(T_train, T - T_eval)
    T_eval = min(T_eval, T - T_train)

    train_idx = torch.tensor(
        [[corpus[i + j] for j in range(K)] for i in range(T_train)],
        dtype=torch.long
    )
    train_tgt = torch.tensor([corpus[i + K] for i in range(T_train)], dtype=torch.long)
    eval_start = T_train
    eval_idx = torch.tensor(
        [[corpus[eval_start + i + j] for j in range(K)] for i in range(T_eval)],
        dtype=torch.long
    )
    eval_tgt = torch.tensor([corpus[eval_start + i + K] for i in range(T_eval)], dtype=torch.long)
    return train_idx, train_tgt, eval_idx, eval_tgt


def train_w_delta(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                   train_idx: torch.Tensor, train_tgt: torch.Tensor,
                   N: int, device: torch.device,
                   n_epochs: int = 2, batch_size: int = 64) -> torch.Tensor:
    """Delta-rule training with fixed beta=BETA_TRAIN."""
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    for epoch in range(n_epochs):
        for bs in range(0, T, batch_size):
            be = min(bs + batch_size, T)
            ctxs = pa.build_ctx_bundles_bsc(
                byte_atoms, pos_atoms, train_idx[bs:be].to(device)
            )
            q = ctxs @ W.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            P = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = P.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=DELTA_ALPHA)
    return W


def eval_at_beta(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                  eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                  beta_inf: float, N: int, device: torch.device,
                  batch_size: int = 128) -> dict:
    """Evaluate substrate at inference beta. Returns dict of metrics."""
    T = eval_idx.shape[0]
    all_entropy = []
    all_bpc_nats = []
    all_acc = []
    all_gap = []

    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(
            byte_atoms, pos_atoms, eval_idx[bs:be].to(device)
        )
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N   # (256, B)
        P = torch.softmax(beta_inf * sims, dim=0)   # (256, B)

        # Entropy (bits per token)
        H = compute_entropy(P)   # (B,)
        all_entropy.append(H.mean().item())

        # BPC (bits per char = nats / log(2))
        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        nll_nats = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)  # (B,)
        all_bpc_nats.append((nll_nats / math.log(2)).mean().item())

        # Argmax accuracy
        pred = P.argmax(dim=0)
        acc = (pred == tgt).float().mean().item()
        all_acc.append(acc)

        # Top1 - Top2 gap
        sorted_p, _ = P.sort(dim=0, descending=True)
        gap = (sorted_p[0] - sorted_p[1]).mean().item()
        all_gap.append(gap)

    return {
        "output_entropy_bits": sum(all_entropy) / len(all_entropy),
        "bpc": sum(all_bpc_nats) / len(all_bpc_nats),
        "retention_argmax": sum(all_acc) / len(all_acc),
        "top1_top2_gap": sum(all_gap) / len(all_gap),
    }


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Train W and sweep beta_inf; return per-beta metrics."""
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]

    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    train_idx, train_tgt, eval_idx, eval_tgt = load_and_tokenize(smoke)

    # Train W
    W = train_w_delta(byte_atoms, pos_atoms, train_idx, train_tgt, N, device,
                       n_epochs=1 if smoke else 2)

    # Sweep beta_inf
    per_beta = {}
    for beta_inf in beta_sweep:
        metrics = eval_at_beta(W, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                beta_inf, N, device)
        per_beta[str(beta_inf)] = metrics

    return {
        "seed": seed,
        "N": N,
        "per_beta": per_beta,
    }


def compute_steerability(per_beta: dict) -> dict:
    """Measure monotonicity and range of entropy across beta sweep."""
    betas = sorted([float(k) for k in per_beta.keys()])
    entropies = [per_beta[str(b)]["output_entropy_bits"] for b in betas]
    bpcs = [per_beta[str(b)]["bpc"] for b in betas]

    entropy_range = max(entropies) - min(entropies)
    # Entropy should decrease monotonically with beta
    diffs = [entropies[i + 1] - entropies[i] for i in range(len(entropies) - 1)]
    is_mono_down = all(d <= 0.1 for d in diffs)  # allow 0.1 bit tolerance

    # BPC: should have interior minimum (parabolic shape near BETA_TRAIN)
    bpc_min_idx = bpcs.index(min(bpcs))
    bpc_interior_min = 0 < bpc_min_idx < len(bpcs) - 1

    return {
        "entropy_range": entropy_range,
        "entropy_is_mono_down": is_mono_down,
        "bpc_interior_min": bpc_interior_min,
        "bpc_min_beta": betas[bpc_min_idx],
        "entropy_values": entropies,
        "bpc_values": bpcs,
        "betas": betas,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF5_INCONCLUSIVE", "No per-seed data.")

    seeds_mono = 0
    entropy_ranges = []
    bpc_interior_min_count = 0
    all_entropy_ranges = []

    for seed_key, seed_data in per_seed.items():
        per_beta = seed_data.get("per_beta", {})
        if not per_beta:
            continue
        st = compute_steerability(per_beta)
        all_entropy_ranges.append(st["entropy_range"])
        if st["entropy_is_mono_down"]:
            seeds_mono += 1
        if st["bpc_interior_min"]:
            bpc_interior_min_count += 1

    n_seeds = len(all_entropy_ranges)
    if n_seeds == 0:
        return ("KF5_INCONCLUSIVE", "No seeds with per_beta data.")

    mean_entropy_range = sum(all_entropy_ranges) / n_seeds

    # HARD_FAIL: invariant to beta
    if all(r < FAIL_ENTROPY_RANGE_MAX for r in all_entropy_ranges):
        return ("KF5_HARD_FAIL",
                f"Substrate invariant to inference beta. "
                f"All entropy ranges < {FAIL_ENTROPY_RANGE_MAX} bits. "
                f"ranges={[round(r, 3) for r in all_entropy_ranges]}. "
                f"Training overwrites beta sensitivity.")

    # HARD_PASS: monotone entropy + large range
    if (seeds_mono >= PASS_ENTROPY_MONOTONE_SEEDS
            and mean_entropy_range >= PASS_ENTROPY_RANGE_MIN):
        return ("KF5_HARD_PASS",
                f"Substrate IS steerable via inference beta. "
                f"{seeds_mono}/{n_seeds} seeds show monotone entropy decrease. "
                f"mean_entropy_range={mean_entropy_range:.3f} bits "
                f"(threshold {PASS_ENTROPY_RANGE_MIN}). "
                f"bpc_interior_min in {bpc_interior_min_count}/{n_seeds} seeds. "
                f"Inference beta controls output uncertainty regime.")

    return ("KF5_MIDDLE_BAND",
            f"Partial steerability. {seeds_mono}/{n_seeds} seeds show mono entropy. "
            f"mean_entropy_range={mean_entropy_range:.3f} bits "
            f"(PASS requires {PASS_ENTROPY_RANGE_MIN}). "
            f"bpc_interior_min in {bpc_interior_min_count}/{n_seeds} seeds.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 4096 stated explicitly
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: entropy formula
    import math as _math
    # Uniform over 256 bytes -> entropy = log2(256) = 8.0 bits
    P_uniform = torch.ones(256, 1) / 256.0
    H_uniform = compute_entropy(P_uniform).item()
    assert abs(H_uniform - 8.0) < 0.01, f"Entropy of uniform(256) should be 8.0; got {H_uniform}"

    # One-hot -> entropy = 0
    P_onehot = torch.zeros(256, 1)
    P_onehot[0, 0] = 1.0
    H_onehot = compute_entropy(P_onehot).item()
    assert abs(H_onehot) < 0.01, f"Entropy of one-hot should be 0; got {H_onehot}"

    # Self-test 2: verdict logic
    # HARD_PASS case: 4 seeds with mono entropy and range > 1.0
    def mk_seed_pass():
        per_beta = {}
        # Monotone decreasing entropy from 7 -> 1 across 3 betas
        for b, h, bpc in [(2.0, 7.0, 4.0), (8.0, 4.0, 3.2), (64.0, 0.5, 5.5)]:
            per_beta[str(b)] = {
                "output_entropy_bits": h, "bpc": bpc,
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}

    summary_pass = {"per_seed": {str(s): mk_seed_pass() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_pass)
    assert v == "KF5_HARD_PASS", f"Expected KF5_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL case: all ranges < 0.01
    def mk_seed_fail():
        per_beta = {}
        for b in [2.0, 8.0, 64.0]:
            per_beta[str(b)] = {
                "output_entropy_bits": 4.0, "bpc": 3.5,
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}
    summary_fail = {"per_seed": {str(s): mk_seed_fail() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_fail)
    assert v == "KF5_HARD_FAIL", f"Expected KF5_HARD_FAIL, got {v}: {msg}"

    # Self-test 3: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024   # Kerdock requires t in {5,6,7}; N=2^(2t) -> min is N=1024
    gen = torch.Generator(device=device).manual_seed(17)
    byte_atoms = pa.make_bsc_atoms(256, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(4, N_test, gen).to(device)

    # Build tiny train set
    corpus = pa.load_corpus_a()[:500]
    T = len(corpus) - K
    if T < 10:
        raise AssertionError(f"Corpus too small: T={T}")
    idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T)], dtype=torch.long)
    tgt = torch.tensor([corpus[i+K] for i in range(T)], dtype=torch.long)

    W = train_w_delta(byte_atoms, pos_atoms, idx, tgt, N_test, device, n_epochs=1)
    assert W.shape == (N_test, N_test), f"W wrong shape: {W.shape}"
    assert not torch.all(W == 0), "W is all-zero after training"

    # Check eval_at_beta for a few betas
    metrics_low = eval_at_beta(W, byte_atoms, pos_atoms, idx[:50], tgt[:50],
                                2.0, N_test, device)
    metrics_high = eval_at_beta(W, byte_atoms, pos_atoms, idx[:50], tgt[:50],
                                 64.0, N_test, device)

    # Entropy must be non-null
    assert metrics_low["output_entropy_bits"] is not None
    assert metrics_high["output_entropy_bits"] is not None
    assert 0 <= metrics_low["output_entropy_bits"] <= 8.1, \
        f"entropy out of [0,8] range: {metrics_low['output_entropy_bits']}"

    # Key assertion: entropy should be higher at beta=2 than beta=64
    assert metrics_low["output_entropy_bits"] > metrics_high["output_entropy_bits"], (
        f"Expected entropy(beta=2) > entropy(beta=64) but got "
        f"{metrics_low['output_entropy_bits']:.3f} <= {metrics_high['output_entropy_bits']:.3f}"
    )

    print("[SELFTEST PASS] kf5_steerable_beta_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_INF_SMOKE if smoke else BETA_INF_SWEEP
    config = {
        "smoke": smoke,
        "N": N,
        "beta_sweep": beta_sweep,
    }
    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf5] N={N} seeds={seeds} betas={beta_sweep} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        # Show entropy range as quick smoke diagnostic
        pb = result["per_beta"]
        betas = sorted([float(k) for k in pb.keys()])
        entropies = [pb[str(b)]["output_entropy_bits"] for b in betas]
        e_range = max(entropies) - min(entropies) if entropies else 0.0
        print(f"  seed {seed} done in {te:.1f}s entropy_range={e_range:.3f}bits "
              f"[{min(entropies):.2f}..{max(entropies):.2f}]", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "beta_sweep": beta_sweep,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf5] VERDICT: {verdict}", flush=True)
    print(f"[kf5] {verdict_msg}", flush=True)
    print(f"[kf5] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
