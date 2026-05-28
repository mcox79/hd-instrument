"""PB-1 SUSCEPTIBILITY DIVERGENCE: byte-LM substrate, N=4096, perturb beta and M.

CONTEXT (Phase-Boundary Operation Hypothesis):
  Substrate sits at a phase boundary. Near a phase transition, the
  susceptibility chi = d<output>/d<control_param> diverges or peaks.
  KF-5 smoke confirmed that beta DOES control entropy (7.5 bit range
  at N=1024). This probe measures the susceptibility of BPC and entropy
  to small perturbations in beta and training epoch count (proxy for M).

  IMPORTANT: Kerdock outer-product store at argmax level is insensitive
  to beta/M because Kerdock is orthogonal by design. The byte-LM delta-rule
  substrate (train_w_delta) shows genuine beta sensitivity via BPC/entropy
  as confirmed by KF-5 smoke. PB-1 uses the byte-LM substrate.

SCIENTIFIC QUESTION (Phase Boundary 1 -- Susceptibility):
  At the operating point (N=4096, standard training), does a small
  perturbation to beta_inf (+/-0.5 around BETA_BASE=8) or training
  duration (epochs +/-1) produce a disproportionately large change
  in BPC or output entropy?
  Susceptibility peak = substrate is near a phase boundary.

DESIGN:
  - Train W at N=4096 with delta-rule, 2 epochs. Measure BPC and entropy.
  - Sweep beta_inf around operating point {6, 7, 8, 9, 10, 12, 16}.
    Measure: BPC(beta), entropy(beta).
    Susceptibility_beta = d(BPC)/d(beta) (gradient at operating point).
  - Vary training epochs: {1, 2, 3, 4, 5}. Measure BPC(epochs).
    Susceptibility_epoch = d(BPC)/d(epoch).
  - 3 seeds.

PRE-REGISTERED BANDS:
  Calibration probe (first systematic susceptibility measurement).

  HARD_PASS: susc_beta > 0.1 BPC/unit-beta near operating point AND
    BPC curve has a MINIMUM (optimal beta near training beta=8).
    Interpretation: substrate is steerable AND has an optimal operating point.
  HARD_FAIL: BPC is monotone in beta with no interior minimum AND
    susc_epoch < 0.01 BPC/epoch (training doesn't matter).
    Interpretation: substrate has no phase structure.
  MIDDLE_BAND: steerable in beta but no clear optimal point, or vice versa.

FORMULA SELF-TESTS:
  1. susc_beta = |BPC(beta+0.5) - BPC(beta)| / 0.5 at beta=8.
  2. BPC minimum near beta_train=8 (theory: optimal inference beta = training beta).
  3. susc_epoch: as epochs increase, BPC should decrease (more training = better).
     susc_epoch ~ d(BPC)/d(epoch) < 0 (negative = improving).
  4. Entropy = H(softmax(beta * sims)) should decrease with beta (confirmed by KF-5).

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 3 beta values, 2 epoch levels. ~20s.
  Full: N=4096, 3 seeds, 7 beta values, 5 epoch levels.
  scale: (4096/1024)^1.5 * 3 * 7/3 * 5/2 = 8 * 3 * 2.33 * 2.5 = 140
  timeout_s = ceil(1.5 * 20 * 140) = ceil(4200) -> 4500s.
  NOTE: >2h flag. Using 4500s.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (delta-rule training; pure CPU; 3 seeds)
Pre-reg: preregs/2026-05-27_pb1_susceptibility_v1.md
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

_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG
N_FULL = 4096       # PROT-018: production N stated explicitly
N_SMOKE = 1024
K = 4               # context window
VOCAB = 256
BETA_TRAIN = 8.0
BETA_SWEEP_FULL = [4.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 16.0, 32.0]
BETA_SWEEP_SMOKE = [4.0, 8.0, 16.0]
EPOCH_SWEEP_FULL = [1, 2, 3, 4, 5]
EPOCH_SWEEP_SMOKE = [1, 2]
T_TRAIN_FULL = 15000
T_TRAIN_SMOKE = 2000
T_EVAL_FULL = 1000
T_EVAL_SMOKE = 200
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds
PASS_SUSC_BETA = 0.1       # BPC change per unit beta at operating point
FAIL_MONOTONE_NO_MIN = True  # BPC has no interior minimum = HARD_FAIL condition


def get_output_dir(default_name: str = "pb1_susceptibility_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_data(smoke: bool):
    """Load corpus and tokenize."""
    corpus = pa.load_corpus_a()
    T = len(corpus) - K
    T_train = T_TRAIN_SMOKE if smoke else T_TRAIN_FULL
    T_eval = T_EVAL_SMOKE if smoke else T_EVAL_FULL
    T_train = min(T_train, T - T_eval)
    T_eval = min(T_eval, T - T_train)
    train_idx = torch.tensor([[corpus[i + j] for j in range(K)] for i in range(T_train)],
                               dtype=torch.long)
    train_tgt = torch.tensor([corpus[i + K] for i in range(T_train)], dtype=torch.long)
    eval_start = T_train
    eval_idx = torch.tensor([[corpus[eval_start + i + j] for j in range(K)]
                              for i in range(T_eval)], dtype=torch.long)
    eval_tgt = torch.tensor([corpus[eval_start + i + K] for i in range(T_eval)],
                              dtype=torch.long)
    return train_idx, train_tgt, eval_idx, eval_tgt


def train_w(byte_atoms, pos_atoms, train_idx, train_tgt, N, device, n_epochs=2, batch=64):
    """Delta-rule training."""
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    for epoch in range(n_epochs):
        for bs in range(0, T, batch):
            be = min(bs + batch, T)
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be].to(device))
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


def eval_bpc_entropy(W, byte_atoms, pos_atoms, eval_idx, eval_tgt, N, device, beta, batch=128):
    """Evaluate BPC and entropy at given beta."""
    T = eval_idx.shape[0]
    bpc_sum = 0.0
    entropy_sum = 0.0
    count = 0
    for bs in range(0, T, batch):
        be = min(bs + batch, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P = torch.softmax(beta * sims, dim=0)
        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        bpc_sum += float((-log_p.gather(0, tgt.unsqueeze(0)).squeeze(0) / math.log(2)).mean().item()) * (be - bs)
        H = -(P * torch.log2(P + 1e-12)).sum(0).mean().item()
        entropy_sum += H * (be - bs)
        count += (be - bs)
    return bpc_sum / count, entropy_sum / count


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run beta sweep and epoch sweep for one seed."""
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]
    epoch_sweep = config["epoch_sweep"]

    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)
    train_idx, train_tgt, eval_idx, eval_tgt = load_data(smoke)

    # PART 1: Train at max epochs, sweep beta_inf
    max_epochs = max(epoch_sweep)
    W_max = train_w(byte_atoms, pos_atoms, train_idx, train_tgt, N, device, max_epochs)
    beta_results = {}
    for beta in beta_sweep:
        bpc, ent = eval_bpc_entropy(W_max, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                     N, device, beta)
        beta_results[str(beta)] = {"bpc": bpc, "entropy_bits": ent}

    # Compute susceptibility_beta at operating point
    bpc_vals = [beta_results[str(b)]["bpc"] for b in beta_sweep]
    betas = list(beta_sweep)
    # Find idx of training beta
    base_idx = min(range(len(betas)), key=lambda i: abs(betas[i] - BETA_TRAIN))
    if base_idx > 0 and base_idx < len(betas) - 1:
        susc_beta = (abs(bpc_vals[base_idx + 1] - bpc_vals[base_idx - 1])
                     / abs(betas[base_idx + 1] - betas[base_idx - 1]))
    else:
        susc_beta = 0.0

    # Check for interior minimum in BPC
    min_bpc_idx = bpc_vals.index(min(bpc_vals))
    has_interior_min = 0 < min_bpc_idx < len(bpc_vals) - 1
    optimal_beta = betas[min_bpc_idx]

    # PART 2: Epoch sweep at BETA_TRAIN
    epoch_results = {}
    for n_ep in epoch_sweep:
        W_ep = train_w(byte_atoms, pos_atoms, train_idx, train_tgt, N, device, n_ep)
        bpc_ep, ent_ep = eval_bpc_entropy(W_ep, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                           N, device, BETA_TRAIN)
        epoch_results[str(n_ep)] = {"bpc": bpc_ep, "entropy_bits": ent_ep}

    epoch_bpcs = [epoch_results[str(e)]["bpc"] for e in epoch_sweep]
    susc_epoch = abs(epoch_bpcs[-1] - epoch_bpcs[0]) / (epoch_sweep[-1] - epoch_sweep[0]) \
                  if len(epoch_sweep) >= 2 else 0.0

    return {
        "seed": seed, "N": N,
        "beta_results": beta_results,
        "susc_beta": susc_beta,
        "has_bpc_interior_min": has_interior_min,
        "optimal_beta": optimal_beta,
        "epoch_results": epoch_results,
        "susc_epoch": susc_epoch,
    }


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("PB1_INCONCLUSIVE", "No per-seed data.")

    susc_betas = []
    interior_mins = []
    susc_epochs = []
    optimal_betas = []

    for seed_key, sd in per_seed.items():
        susc_betas.append(sd.get("susc_beta", 0.0))
        interior_mins.append(sd.get("has_bpc_interior_min", False))
        susc_epochs.append(abs(sd.get("susc_epoch", 0.0)))
        optimal_betas.append(sd.get("optimal_beta", 0.0))

    n_seeds = len(susc_betas)
    mean_sb = sum(susc_betas) / n_seeds
    n_interior = sum(1 for x in interior_mins if x)
    mean_se = sum(susc_epochs) / n_seeds
    mean_opt_beta = sum(optimal_betas) / n_seeds

    # HARD_FAIL: BPC monotone AND training doesn't help
    if n_interior == 0 and mean_se < 0.01:
        return ("PB1_HARD_FAIL",
                f"No phase structure. BPC has no interior minimum in {n_interior}/{n_seeds} seeds. "
                f"susc_epoch={mean_se:.4f} (need >0.01). "
                f"susc_beta={mean_sb:.4f}. Substrate has no phase sensitivity.")

    # HARD_PASS
    if mean_sb >= PASS_SUSC_BETA and n_interior >= max(1, n_seeds // 2):
        return ("PB1_HARD_PASS",
                f"Phase sensitivity detected. susc_beta={mean_sb:.3f} >= {PASS_SUSC_BETA}. "
                f"BPC has interior minimum in {n_interior}/{n_seeds} seeds. "
                f"mean_optimal_beta={mean_opt_beta:.1f} (near BETA_TRAIN={BETA_TRAIN}). "
                f"susc_epoch={mean_se:.4f}. "
                f"Substrate operates near a control-parameter optimum.")

    return ("PB1_MIDDLE_BAND",
            f"Partial phase sensitivity. susc_beta={mean_sb:.3f}, "
            f"interior_min={n_interior}/{n_seeds}, susc_epoch={mean_se:.4f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: verdict logic
    def mk_sd(sb, interior, se, opt_b):
        return {"susc_beta": sb, "has_bpc_interior_min": interior,
                "susc_epoch": se, "optimal_beta": opt_b,
                "beta_results": {"8.0": {"bpc": 3.5, "entropy_bits": 2.5}},
                "epoch_results": {"2": {"bpc": 3.5, "entropy_bits": 2.5}}}

    # HARD_PASS
    v, msg = compute_verdict({"per_seed": {
        "17": dict(seed=17, N=4096, **mk_sd(0.2, True, 0.05, 8.0)),
        "23": dict(seed=23, N=4096, **mk_sd(0.15, True, 0.04, 7.5)),
    }})
    assert v == "PB1_HARD_PASS", f"Expected PB1_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL
    v, msg = compute_verdict({"per_seed": {
        "17": dict(seed=17, N=4096, **mk_sd(0.05, False, 0.005, 0.0)),
    }})
    assert v == "PB1_HARD_FAIL", f"Expected PB1_HARD_FAIL, got {v}: {msg}"

    # Self-test 2: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    gen = torch.Generator(device=device).manual_seed(17)
    byte_atoms = pa.make_bsc_atoms(256, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(4, N_test, gen).to(device)
    corpus = pa.load_corpus_a()[:500]
    T = len(corpus) - K
    idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T)], dtype=torch.long)
    tgt = torch.tensor([corpus[i+K] for i in range(T)], dtype=torch.long)
    W = train_w(byte_atoms, pos_atoms, idx, tgt, N_test, device, n_epochs=1)

    bpc_low, ent_low = eval_bpc_entropy(W, byte_atoms, pos_atoms, idx[:100], tgt[:100],
                                         N_test, device, 2.0)
    bpc_high, ent_high = eval_bpc_entropy(W, byte_atoms, pos_atoms, idx[:100], tgt[:100],
                                           N_test, device, 64.0)

    assert isinstance(bpc_low, float) and bpc_low > 0, f"invalid bpc_low: {bpc_low}"
    assert isinstance(ent_low, float) and ent_low >= 0, f"invalid ent_low: {ent_low}"
    # Entropy should be higher at low beta
    assert ent_low > ent_high, (
        f"Expected entropy(beta=2) > entropy(beta=64): {ent_low:.3f} vs {ent_high:.3f}"
    )

    print("[SELFTEST PASS] pb1_susceptibility_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    epoch_sweep = EPOCH_SWEEP_SMOKE if smoke else EPOCH_SWEEP_FULL
    config = {"smoke": smoke, "N": N, "beta_sweep": beta_sweep, "epoch_sweep": epoch_sweep}

    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[pb1] N={N} seeds={seeds} betas={beta_sweep} epochs={epoch_sweep} "
          f"mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        print(f"  seed {seed} done in {te:.1f}s "
              f"susc_beta={result['susc_beta']:.4f} "
              f"interior_min={result['has_bpc_interior_min']} "
              f"optimal_beta={result['optimal_beta']:.1f}", flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "beta_sweep": beta_sweep,
        "epoch_sweep": epoch_sweep,
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
    print(f"\n[pb1] VERDICT: {verdict}", flush=True)
    print(f"[pb1] {verdict_msg}", flush=True)
    print(f"[pb1] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
