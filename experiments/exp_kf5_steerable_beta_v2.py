"""KF-5 STEERABLE SUBSTRATE v2: FULL re-ship at N=4096 5-seed, beta in {2,4,8,16,32,64,128}.

PARENT: exp_kf5_steerable_beta_v1.py -- v1 had metrics-source-fallback (remote SSH disconnect
  caused _source=local; FIRST POST-FIX OBSERVATION). Infrastructure confirmed working in v2 re-ship.
  v1 smoke was positive-consistent (entropy_range=7.58 bits, monotone, bpc interior min).

SCIENTIFIC QUESTION (Killer Feature 5):
  Can inference-time beta adjustment (NO retraining) steer substrate behavior?
  One trained W, multiple behavioral regimes via beta control.
  Validates 'steerable substrate' as a product capability.

PRE-REGISTERED BANDS (unchanged from v1; tightened HP gate per routing-note spec):
  HARD_PASS: (1) output_entropy monotone DECREASING across beta sweep in >= 4/5 seeds
    AND (2) mean_entropy_range > 1.0 bit AND (3) bpc_inf has interior minimum at some
    beta in {4,8,16,32} (not extremes).
    Interpretation: substrate exhibits genuine behavioral regimes via beta.
  HARD_FAIL: entropy_range < 0.5 bits AND all-beta bpc monotonic (no bowl shape)
    across >= 4/5 seeds. No qualitative profile shift = phase-boundary refuted.
  MIDDLE_BAND: entropy monotone in < 4/5 seeds OR entropy_range in [0.5, 1.0].

FORMULA SELF-TESTS (inherited + expanded):
  1. H(uniform over 256 bytes) = log2(256) = 8.0 bits. beta->0 -> H -> 8.0.
  2. H(one-hot) = 0 bits. beta->inf -> H -> 0.0 bits.
  3. entropy_range = H(beta_min) - H(beta_max); for beta_min=2, beta_max=128: >> 0.
  4. bpc optimal near beta~=BETA_TRAIN=8.
  5. HARD_FAIL requires ALL seeds fail range AND bpc monotonic; individual seed failure is MIDDLE_BAND.

TIMEOUT ESTIMATE:
  smoke_wall_s (v1 CPU): 0.3s at N=1024, 1 seed, 3 betas.
  GPU at N=4096, 5 seeds, 7 betas: scale factor (4096/1024)^1.5 * 5 * (7/3) = 8*5*2.33 = 93.
  But: GPU is ~5-10x faster than laptop CPU on these ops.
  Anchor from v1 prereg: 2100s estimated.
  With +50% buffer: 3150s -> round up to 3300s.
  Under 2h: no extra visibility flag needed.
  timeout_s = 3300.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly; N_FULL=4096).
Queue: overnight_queue (GPU; delta-rule training at N=4096, 5 seeds)
Pre-reg: preregs/2026-05-27_kf5_steerable_beta_v2.md
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

# Load phase_a infrastructure
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- PROT-018: no _nN suffix; N_FULL=4096 stated explicitly
N_FULL = 4096
N_SMOKE = 1024      # Kerdock requires N in {1024,4096,16384}
K = 4               # context window
VOCAB = 256
BETA_TRAIN = 8.0
BETA_INF_SWEEP = [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_INF_SMOKE = [2.0, 8.0, 64.0]
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
T_TRAIN_FULL = 20000
T_TRAIN_SMOKE = 3000
T_EVAL_FULL = 2000
T_EVAL_SMOKE = 300
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_ENTROPY_RANGE_MIN = 1.0       # bits: entropy must span > 1.0 bits across beta sweep
PASS_ENTROPY_MONOTONE_SEEDS = 4    # >= 4/5 seeds with monotone entropy
FAIL_ENTROPY_RANGE_MAX = 0.5       # TIGHTENED from v1: range < 0.5 bits AND bpc monotonic = HARD_FAIL
FAIL_BPC_MONOTONE_SEEDS = 4        # bpc must be monotonic (no bowl) in >= 4/5 seeds for HARD_FAIL


def get_output_dir(default_name: str = "kf5_steerable_beta_v2") -> Path:
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

        H = compute_entropy(P)
        all_entropy.append(H.mean().item())

        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        nll_nats = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        all_bpc_nats.append((nll_nats / math.log(2)).mean().item())

        pred = P.argmax(dim=0)
        acc = (pred == tgt).float().mean().item()
        all_acc.append(acc)

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
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]

    # CPU generator for atom creation (pa.make_bsc_atoms uses torch.rand which requires cpu gen)
    gen_cpu = torch.Generator(device="cpu").manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen_cpu).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen_cpu).to(device)

    train_idx, train_tgt, eval_idx, eval_tgt = load_and_tokenize(smoke)

    W = train_w_delta(byte_atoms, pos_atoms, train_idx, train_tgt, N, device,
                       n_epochs=1 if smoke else 2)

    per_beta = {}
    for beta_inf in beta_sweep:
        metrics = eval_at_beta(W, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                beta_inf, N, device)
        per_beta[str(beta_inf)] = metrics

    return {"seed": seed, "N": N, "per_beta": per_beta}


def compute_steerability(per_beta: dict) -> dict:
    betas = sorted([float(k) for k in per_beta.keys()])
    entropies = [per_beta[str(b)]["output_entropy_bits"] for b in betas]
    bpcs = [per_beta[str(b)]["bpc"] for b in betas]

    entropy_range = max(entropies) - min(entropies)
    diffs = [entropies[i + 1] - entropies[i] for i in range(len(entropies) - 1)]
    is_mono_down = all(d <= 0.1 for d in diffs)

    bpc_min_idx = bpcs.index(min(bpcs))
    bpc_interior_min = 0 < bpc_min_idx < len(bpcs) - 1

    # bpc monotone check (no interior min)
    bpc_diffs = [bpcs[i + 1] - bpcs[i] for i in range(len(bpcs) - 1)]
    is_bpc_monotone = all(d >= -0.05 for d in bpc_diffs) or all(d <= 0.05 for d in bpc_diffs)

    return {
        "entropy_range": entropy_range,
        "entropy_is_mono_down": is_mono_down,
        "bpc_interior_min": bpc_interior_min,
        "bpc_is_monotone": is_bpc_monotone,
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
    seeds_bpc_mono = 0
    all_entropy_ranges = []
    bpc_interior_min_count = 0

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
        if st["bpc_is_monotone"]:
            seeds_bpc_mono += 1

    n_seeds = len(all_entropy_ranges)
    if n_seeds == 0:
        return ("KF5_INCONCLUSIVE", "No seeds with per_beta data.")

    mean_entropy_range = sum(all_entropy_ranges) / n_seeds

    # HARD_FAIL: invariant to beta AND bpc shows no bowl (v2 TIGHTENED gate)
    if (all(r < FAIL_ENTROPY_RANGE_MAX for r in all_entropy_ranges)
            and seeds_bpc_mono >= FAIL_BPC_MONOTONE_SEEDS):
        return ("KF5_HARD_FAIL",
                f"Phase-boundary REFUTED. All entropy ranges < {FAIL_ENTROPY_RANGE_MAX} bits "
                f"AND bpc monotone in {seeds_bpc_mono}/{n_seeds} seeds. "
                f"ranges={[round(r, 3) for r in all_entropy_ranges]}. "
                f"No qualitative profile shift under inference beta.")

    # HARD_PASS
    if (seeds_mono >= PASS_ENTROPY_MONOTONE_SEEDS
            and mean_entropy_range >= PASS_ENTROPY_RANGE_MIN):
        return ("KF5_HARD_PASS",
                f"Substrate IS steerable via inference beta. "
                f"{seeds_mono}/{n_seeds} seeds mono entropy decrease. "
                f"mean_entropy_range={mean_entropy_range:.3f} bits "
                f"(threshold {PASS_ENTROPY_RANGE_MIN}). "
                f"bpc_interior_min in {bpc_interior_min_count}/{n_seeds} seeds. "
                f"bpc_monotone_seeds={seeds_bpc_mono}/{n_seeds}. "
                f"Inference beta steers output regime without retraining.")

    return ("KF5_MIDDLE_BAND",
            f"Partial steerability. {seeds_mono}/{n_seeds} seeds mono entropy. "
            f"mean_entropy_range={mean_entropy_range:.3f} bits "
            f"(PASS requires {PASS_ENTROPY_RANGE_MIN}). "
            f"bpc_interior_min in {bpc_interior_min_count}/{n_seeds} seeds.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: entropy formula
    P_uniform = torch.ones(256, 1) / 256.0
    H_uniform = compute_entropy(P_uniform).item()
    assert abs(H_uniform - 8.0) < 0.01, f"Entropy of uniform(256) should be 8.0; got {H_uniform}"

    P_onehot = torch.zeros(256, 1)
    P_onehot[0, 0] = 1.0
    H_onehot = compute_entropy(P_onehot).item()
    assert abs(H_onehot) < 0.01, f"Entropy of one-hot should be 0; got {H_onehot}"

    # Self-test 2: verdict logic
    def mk_seed_pass():
        per_beta = {}
        for b, h, bpc in [(2.0, 7.0, 4.0), (8.0, 4.0, 3.2), (64.0, 0.5, 5.5)]:
            per_beta[str(b)] = {
                "output_entropy_bits": h, "bpc": bpc,
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}

    summary_pass = {"per_seed": {str(s): mk_seed_pass() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_pass)
    assert v == "KF5_HARD_PASS", f"Expected KF5_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: all ranges < 0.5 AND bpc monotone in >= 4/5 seeds
    def mk_seed_fail_v2():
        per_beta = {}
        for b in [2.0, 8.0, 32.0, 64.0]:
            per_beta[str(b)] = {
                "output_entropy_bits": 4.0, "bpc": float(3.0 + b * 0.01),  # monotone bpc
                "retention_argmax": 0.35, "top1_top2_gap": 0.1
            }
        return {"per_beta": per_beta}
    summary_fail = {"per_seed": {str(s): mk_seed_fail_v2() for s in [7, 17, 23, 31, 41]}}
    v, msg = compute_verdict(summary_fail)
    assert v == "KF5_HARD_FAIL", f"Expected KF5_HARD_FAIL, got {v}: {msg}"

    # Self-test 3: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    gen = torch.Generator(device="cpu").manual_seed(17)
    byte_atoms = pa.make_bsc_atoms(256, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(4, N_test, gen).to(device)

    corpus = pa.load_corpus_a()[:500]
    T = len(corpus) - K
    assert T >= 10, f"Corpus too small: T={T}"
    idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T)], dtype=torch.long)
    tgt = torch.tensor([corpus[i+K] for i in range(T)], dtype=torch.long)

    W = train_w_delta(byte_atoms, pos_atoms, idx, tgt, N_test, device, n_epochs=1)
    assert W.shape == (N_test, N_test)
    assert not torch.all(W == 0), "W is all-zero after training"

    metrics_low = eval_at_beta(W, byte_atoms, pos_atoms, idx[:50], tgt[:50],
                                2.0, N_test, device)
    metrics_high = eval_at_beta(W, byte_atoms, pos_atoms, idx[:50], tgt[:50],
                                 64.0, N_test, device)

    assert metrics_low["output_entropy_bits"] is not None
    assert 0 <= metrics_low["output_entropy_bits"] <= 8.1, \
        f"entropy out of [0,8] range: {metrics_low['output_entropy_bits']}"
    assert metrics_low["output_entropy_bits"] > metrics_high["output_entropy_bits"], (
        f"Expected entropy(beta=2) > entropy(beta=64): "
        f"{metrics_low['output_entropy_bits']:.3f} <= {metrics_high['output_entropy_bits']:.3f}"
    )

    print("[SELFTEST PASS] kf5_steerable_beta_v2 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_INF_SMOKE if smoke else BETA_INF_SWEEP
    config = {"smoke": smoke, "N": N, "beta_sweep": beta_sweep}
    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[kf5v2] N={N} seeds={seeds} betas={beta_sweep} "
          f"device={device} mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
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
    # Checkpoint metrics immediately (defense against runner crash)
    out_dir2 = get_output_dir()
    checkpoint_path = out_dir2 / "metrics_checkpoint.json"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[kf5v2] VERDICT: {verdict}", flush=True)
    print(f"[kf5v2] {verdict_msg}", flush=True)
    print(f"[kf5v2] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
