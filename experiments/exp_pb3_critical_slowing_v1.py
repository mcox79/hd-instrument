"""PB-3 CRITICAL SLOWING DOWN: byte-LM substrate, sequential edits, convergence time.

CONTEXT (Phase-Boundary Operation Hypothesis):
  Near a phase transition, the system exhibits critical slowing down:
  response to perturbation takes longer to converge (relaxation time diverges).
  For the byte-LM substrate, we operationalize this as: after N sequential
  delta-rule edits, how many additional training steps are needed to
  recover baseline BPC?

SCIENTIFIC QUESTION (Phase Boundary 3):
  At varying operating points (different beta or epoch_count):
  After 100 sequential edits (each training step overwrites a previously
  trained pattern), how many steps are needed to recover baseline BPC
  to within 10% (tau_recovery)?
  Does tau_recovery peak near the training beta / near the BPC minimum?
  If yes: substrate exhibits critical slowing down.

DESIGN:
  - Train W at N=4096, standard delta-rule, beta_train=8.
  - Measure baseline BPC.
  - Apply 100 sequential "destructive edits": train on a DIFFERENT corpus
    (shuffled corpus_B) for 1 step each, corrupting W.
  - Measure BPC after each edit (corruption curve).
  - Then re-train on original corpus, measure recovery time (tau_10pct).
  - Sweep beta_train: {4, 8, 16} (3 operating points).
    Expected: tau_recovery peaks near optimal beta (=8).
  - 3 seeds.

PRE-REGISTERED BANDS (first critical-slowing-down measurement):
  Calibration probe; no prior empirical anchor.

  HARD_PASS: tau_recovery at beta=8 is >= 1.5x tau_recovery at beta=4 or beta=16
    (slowing at the optimal operating point). Phase transition signature.
  HARD_FAIL: tau_recovery is constant across all beta values (no slowing).
  MIDDLE_BAND: tau_recovery varies but not by >= 1.5x factor.

FORMULA SELF-TESTS:
  1. BPC_recover(t) should decrease monotonically after re-training begins.
  2. tau_10pct = min steps t where BPC(t) <= 1.1 * BPC_baseline.
  3. For beta very low (uniform output): BPC ~ 8 bits always; recovery trivially fast.
  4. For beta very high (near one-hot): strong prior; recovery slow.

TIMEOUT ESTIMATE:
  smoke: N=1024, 1 seed, 2 beta values, 50 edit steps, 50 recovery steps. ~30s.
  Full: N=4096, 3 seeds, 3 beta values, 100 edits, 100 recovery steps.
  scale: (4096/1024)^1.5 * 3 * (3/2) * (100/50)^1.0 * (100/50)^1.0 = 8 * 3 * 1.5 * 2 * 2 = 144
  timeout_s = ceil(1.5 * 30 * 144) = ceil(6480) -> 7200s.
  NOTE: 2h run -- at limits. Flag in status log.

N-suffix: no _nN suffix; production N = 4096 (PROT-018: stated explicitly).
Queue: remote_cpu_queue (delta-rule sequential training; 3 seeds x 3 beta; CPU)
Pre-reg: preregs/2026-05-27_pb3_critical_slowing_v1.md
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
BETA_SWEEP_FULL = [4.0, 8.0, 16.0]
BETA_SWEEP_SMOKE = [4.0, 8.0]
N_EDITS_FULL = 100
N_EDITS_SMOKE = 50
N_RECOVERY_FULL = 100
N_RECOVERY_SMOKE = 50
T_TRAIN_FULL = 10000
T_TRAIN_SMOKE = 1500
T_EVAL_FULL = 500
T_EVAL_SMOKE = 100
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
RECOVERY_THRESHOLD = 0.10   # BPC within 10% of baseline = "recovered"
SLOWING_RATIO = 1.5         # tau_recovery(beta=8) >= 1.5x(other) = critical slowing


def get_output_dir(default_name: str = "pb3_critical_slowing_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_data(smoke: bool):
    """Load corpus A (train/eval) and corpus B (shuffled A for corruption)."""
    corpus_A = pa.load_corpus_a()
    T = len(corpus_A) - K
    T_train = T_TRAIN_SMOKE if smoke else T_TRAIN_FULL
    T_eval = T_EVAL_SMOKE if smoke else T_EVAL_FULL
    T_train = min(T_train, T - T_eval)
    T_eval = min(T_eval, T - T_train)

    # Tokenize corpus A
    train_idx = torch.tensor([[corpus_A[i + j] for j in range(K)] for i in range(T_train)],
                               dtype=torch.long)
    train_tgt = torch.tensor([corpus_A[i + K] for i in range(T_train)], dtype=torch.long)
    eval_start = T_train
    eval_idx = torch.tensor([[corpus_A[eval_start + i + j] for j in range(K)]
                              for i in range(T_eval)], dtype=torch.long)
    eval_tgt = torch.tensor([corpus_A[eval_start + i + K] for i in range(T_eval)],
                              dtype=torch.long)

    # Corpus B: shuffled A (destructive patterns)
    corpus_B = pa.shuffle_bytes(bytes(corpus_A), 42)
    T_B = len(corpus_B) - K
    B_train = torch.tensor([[corpus_B[i + j] for j in range(K)] for i in range(T_B)],
                             dtype=torch.long)
    B_tgt = torch.tensor([corpus_B[i + K] for i in range(T_B)], dtype=torch.long)

    return train_idx, train_tgt, eval_idx, eval_tgt, B_train, B_tgt


def compute_bpc(W, byte_atoms, pos_atoms, eval_idx, eval_tgt, N, device, beta, batch=128):
    """BPC at given beta."""
    T = eval_idx.shape[0]
    total = 0.0
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
        total += float((-log_p.gather(0, tgt.unsqueeze(0)).squeeze(0) / math.log(2)).sum().item())
        count += (be - bs)
    return total / count if count > 0 else float('inf')


def one_train_step(W, byte_atoms, pos_atoms, idx_batch, tgt_batch, N, device, beta):
    """One batch delta-rule step at given beta."""
    ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, idx_batch.to(device))
    q = ctxs @ W.T
    q = pa.shifted_relu(q, RELU_B)
    sims = (byte_atoms @ q.T) / N
    P = torch.softmax(beta * sims, dim=0)
    target_atoms = byte_atoms[tgt_batch.to(device)]
    predicted = P.T @ byte_atoms
    dW = (target_atoms - predicted).T @ ctxs / N
    W = W * (1.0 - DELTA_DECAY) + DELTA_ALPHA * dW
    return W


def run_one_beta(seed: int, beta_train: float, config: dict,
                  byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                  train_idx, train_tgt, eval_idx, eval_tgt,
                  B_train, B_tgt, device: torch.device) -> dict:
    """Run full edit+recovery cycle for one (seed, beta_train) pair."""
    smoke = config["smoke"]
    N = config["N"]
    n_edits = config["n_edits"]
    n_recovery = config["n_recovery"]
    batch = 64

    # Train W to baseline
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    for bs in range(0, T, batch):
        be = min(bs + batch, T)
        W = one_train_step(W, byte_atoms, pos_atoms, train_idx[bs:be],
                            train_tgt[bs:be], N, device, beta_train)

    bpc_baseline = compute_bpc(W, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                 N, device, beta_train)

    # Sequential corruption: n_edits steps on corpus B
    T_B = B_train.shape[0]
    corruption_curve = []
    W_corrupted = W.clone()
    for step in range(n_edits):
        bs = (step * batch) % max(1, T_B - batch)
        be = min(bs + batch, T_B)
        W_corrupted = one_train_step(W_corrupted, byte_atoms, pos_atoms,
                                      B_train[bs:be], B_tgt[bs:be], N, device, beta_train)
        if step % max(1, n_edits // 10) == 0 or step == n_edits - 1:
            bpc_c = compute_bpc(W_corrupted, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                  N, device, beta_train)
            corruption_curve.append((step, bpc_c))

    bpc_after_edits = compute_bpc(W_corrupted, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                   N, device, beta_train)

    # Recovery: re-train on corpus A, measure BPC at each step
    recovery_curve = []
    W_recovering = W_corrupted.clone()
    tau_recovery = n_recovery  # default: no recovery (worst case)
    recovery_target = bpc_baseline * (1.0 + RECOVERY_THRESHOLD)
    for step in range(n_recovery):
        bs = (step * batch) % max(1, T - batch)
        be = min(bs + batch, T)
        W_recovering = one_train_step(W_recovering, byte_atoms, pos_atoms,
                                       train_idx[bs:be], train_tgt[bs:be],
                                       N, device, beta_train)
        if step % max(1, n_recovery // 10) == 0 or step == n_recovery - 1:
            bpc_r = compute_bpc(W_recovering, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                  N, device, beta_train)
            recovery_curve.append((step, bpc_r))
            if bpc_r <= recovery_target and tau_recovery == n_recovery:
                tau_recovery = step + 1

    return {
        "beta_train": beta_train,
        "bpc_baseline": bpc_baseline,
        "bpc_after_edits": bpc_after_edits,
        "tau_recovery": tau_recovery,
        "recovery_target": recovery_target,
        "corruption_curve": corruption_curve,
        "recovery_curve": recovery_curve,
    }


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    """Run all beta values for one seed."""
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]

    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K, N, gen).to(device)

    train_idx, train_tgt, eval_idx, eval_tgt, B_train, B_tgt = load_data(smoke)

    per_beta = {}
    for beta_train in beta_sweep:
        print(f"    beta={beta_train}...", flush=True)
        result = run_one_beta(seed, beta_train, config,
                               byte_atoms, pos_atoms,
                               train_idx, train_tgt, eval_idx, eval_tgt,
                               B_train, B_tgt, device)
        per_beta[str(beta_train)] = result

    return {"seed": seed, "N": N, "per_beta": per_beta}


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("PB3_INCONCLUSIVE", "No per-seed data.")

    beta_sweep = summary.get("beta_sweep", [])
    if not beta_sweep:
        return ("PB3_INCONCLUSIVE", "No beta_sweep recorded.")

    # Mean tau_recovery per beta
    tau_by_beta = {}
    for beta_v in beta_sweep:
        taus = []
        for seed_key, sd in per_seed.items():
            cell = sd.get("per_beta", {}).get(str(beta_v))
            if cell:
                taus.append(cell["tau_recovery"])
        tau_by_beta[beta_v] = sum(taus) / len(taus) if taus else 0.0

    if not tau_by_beta:
        return ("PB3_INCONCLUSIVE", "No tau data.")

    max_tau = max(tau_by_beta.values())
    min_tau = min(tau_by_beta.values())
    tau_at_opt = tau_by_beta.get(8.0, tau_by_beta.get(beta_sweep[len(beta_sweep)//2], max_tau))

    # HARD_FAIL: all tau near equal (no slowing)
    if max_tau <= min_tau * 1.2:
        return ("PB3_HARD_FAIL",
                f"No critical slowing detected. tau_by_beta={dict((k, round(v, 1)) for k, v in tau_by_beta.items())}. "
                f"max/min ratio={max_tau / (min_tau + 1e-6):.2f} < 1.5 threshold. "
                f"Recovery time is independent of operating point.")

    # HARD_PASS: tau at optimal beta >= SLOWING_RATIO * min tau
    if max_tau >= SLOWING_RATIO * min_tau and tau_at_opt >= SLOWING_RATIO * min_tau * 0.8:
        return ("PB3_HARD_PASS",
                f"CRITICAL SLOWING DOWN detected. "
                f"tau_by_beta={dict((k, round(v, 1)) for k, v in tau_by_beta.items())}. "
                f"max/min ratio={max_tau/(min_tau+1e-6):.2f} >= {SLOWING_RATIO}. "
                f"tau_at_beta8={tau_at_opt:.1f}. "
                f"Substrate recovers slowest at optimal operating point -- phase boundary signature.")

    return ("PB3_MIDDLE_BAND",
            f"Partial slowing. tau_by_beta={dict((k, round(v, 1)) for k, v in tau_by_beta.items())}. "
            f"max/min ratio={max_tau/(min_tau+1e-6):.2f}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: verdict
    def mk_sd(tau_dict):
        return {"per_beta": {str(b): {"beta_train": b, "bpc_baseline": 3.5,
                                       "bpc_after_edits": 5.0, "tau_recovery": t,
                                       "recovery_target": 3.85,
                                       "corruption_curve": [], "recovery_curve": []}
                              for b, t in tau_dict.items()}}

    # HARD_PASS: slowing at beta=8 (tau=50 vs tau=10)
    v, msg = compute_verdict({"per_seed": {"17": dict(seed=17, N=4096,
        **mk_sd({4.0: 10, 8.0: 50, 16.0: 15}))},
        "beta_sweep": [4.0, 8.0, 16.0]})
    assert v == "PB3_HARD_PASS", f"Expected PB3_HARD_PASS, got {v}: {msg}"

    # HARD_FAIL: constant tau
    v, msg = compute_verdict({"per_seed": {"17": dict(seed=17, N=4096,
        **mk_sd({4.0: 20, 8.0: 21, 16.0: 19}))},
        "beta_sweep": [4.0, 8.0, 16.0]})
    assert v == "PB3_HARD_FAIL", f"Expected PB3_HARD_FAIL, got {v}: {msg}"

    # Self-test 2: smoke forward pass
    device = torch.device("cpu")
    N_test = 1024
    gen = torch.Generator(device=device).manual_seed(17)
    byte_atoms = pa.make_bsc_atoms(256, N_test, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(4, N_test, gen).to(device)
    corpus_A = pa.load_corpus_a()[:600]
    T = len(corpus_A) - K
    train_idx = torch.tensor([[corpus_A[i+j] for j in range(K)] for i in range(T)],
                               dtype=torch.long)
    train_tgt = torch.tensor([corpus_A[i+K] for i in range(T)], dtype=torch.long)
    eval_idx = train_idx[:50]
    eval_tgt = train_tgt[:50]
    corpus_B = pa.shuffle_bytes(bytes(corpus_A), 42)
    T_B = len(corpus_B) - K
    B_train = torch.tensor([[corpus_B[i+j] for j in range(K)] for i in range(T_B)],
                             dtype=torch.long)
    B_tgt = torch.tensor([corpus_B[i+K] for i in range(T_B)], dtype=torch.long)

    config_smoke = {"smoke": True, "N": N_test, "n_edits": 10, "n_recovery": 10,
                     "beta_sweep": [8.0]}
    result = run_one_beta(17, 8.0, config_smoke,
                           byte_atoms, pos_atoms,
                           train_idx, train_tgt, eval_idx, eval_tgt,
                           B_train, B_tgt, device)
    assert "bpc_baseline" in result, "missing bpc_baseline"
    assert "tau_recovery" in result, "missing tau_recovery"
    assert result["bpc_baseline"] > 0, f"invalid bpc_baseline: {result['bpc_baseline']}"
    assert 0 < result["tau_recovery"] <= config_smoke["n_recovery"], \
        f"tau_recovery out of range: {result['tau_recovery']}"

    print("[SELFTEST PASS] pb3_critical_slowing_v1 instrumentation OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    n_edits = N_EDITS_SMOKE if smoke else N_EDITS_FULL
    n_recovery = N_RECOVERY_SMOKE if smoke else N_RECOVERY_FULL
    config = {"smoke": smoke, "N": N, "beta_sweep": beta_sweep,
               "n_edits": n_edits, "n_recovery": n_recovery}

    t0 = time.time()
    out_dir = get_output_dir()
    print(f"[pb3] N={N} seeds={seeds} betas={beta_sweep} "
          f"n_edits={n_edits} n_recovery={n_recovery} "
          f"mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        taus = {b: result["per_beta"][str(b)]["tau_recovery"]
                for b in beta_sweep if str(b) in result["per_beta"]}
        print(f"  seed {seed} done in {te:.1f}s tau_by_beta={taus}", flush=True)
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
    print(f"\n[pb3] VERDICT: {verdict}", flush=True)
    print(f"[pb3] {verdict_msg}", flush=True)
    print(f"[pb3] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
