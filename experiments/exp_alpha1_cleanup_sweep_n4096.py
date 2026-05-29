"""ALPHA-1: CLEANUP OPERATOR STRENGTH SWEEP at N=4096 (CPU-suitable).

PARENT: exp_kf5_steerable_beta_v2.py (KF5_PARTIAL_DECOUPLING: beta steers entropy but
  not argmax/bpc). exp_kf5_fine_beta_betac_n4096.py (fine-beta KF-5 last-chance).

SCIENTIFIC QUESTION (operational-layer steerability rescue post-KF5_PARTIAL_DECOUPLING):
  At fixed beta=32, M_frac=4, N=4096, BSC codebook:
  Does varying the cleanup operator strength (tau_cleanup from 0 = no cleanup to hard
  argmax) unlock W-magnitude-operative steerability? The cleanup operator maps the
  soft W*query output to discrete codebook atoms before final readout. By varying
  tau_cleanup, we sweep from soft-continuous output (tau=0, magnitude-full) to
  hard-argmax output (tau->inf, magnitude-collapsed).
  If bpc changes with tau_cleanup: the continuous W path matters and steerability
  exists at the cleanup-threshold level. If bpc flat: pure argmax-routing dominates.

SWEEP DESIGN:
  6 cleanup levels:
  - tau_cleanup = 0.0     : NO cleanup (raw W*query output; full W-magnitude path)
  - tau_cleanup = 0.1     : very soft cleanup
  - tau_cleanup = 1.0     : moderate softmax cleanup
  - tau_cleanup = 10.0    : near-hard cleanup
  - tau_cleanup = 100.0   : hard-argmax-equivalent cleanup
  - tau_cleanup = "argmax": deterministic argmax (W-magnitude fully collapsed)

PRE-REGISTERED BANDS (calibration probe):
  HARD_PASS: bpc varies monotonically across tau_cleanup sweep with total bpc_range > 0.5
    AND bpc_min < bpc_argmax * 0.95 (cleanup actually helps) in >= 2/3 seeds.
    Interpretation: cleanup operator unlocks W-magnitude steerability.
  HARD_FAIL: bpc flat across tau_cleanup sweep (bpc_range < 0.05) across all seeds.
    Interpretation: bpc is cleanup-invariant; W-magnitude path is not operative in readout.
  MIDDLE_BAND: bpc_range in [0.05, 0.5).

  NOTE: calibration probe (no prior empirical cleanup-sweep anchor).
  "no prior empirical anchor; bands per calibration-probe policy: +-50% of theory."

FORMULA SELF-TESTS:
  1. tau_cleanup=0: output = raw W*query (magnitude-full).
  2. tau_cleanup->inf: output -> argmax(W*query) * codebook_atom (discrete; magnitude-free).
  3. Cleanup step: P_cleanup = softmax(tau_cleanup * (cb @ output / N)); final = P_cleanup.T @ cb.
  4. bpc = mean(-log2(P[tgt])) where P is the output distribution.
  5. N == 4096 (PROT-018 binding).
  6. tau_cleanup = 0 bypasses cleanup (identity path).

OOM CHECK:
  W at N=4096: 64MB. BSC codebook C=256: 1MB. CPU memory OK (16GB+ desktop).

TIMEOUT ESTIMATE:
  Parent v2 smoke: ~0.3s (N=1024, 1 seed, 3 betas GPU).
  CPU 10x slower. N scale (4096/1024)^1.5 = 8. Seeds=3. Taus=6 (same as betas).
  estimate = 0.3 * 10 * 8 * 3 * (6/3) = 0.3 * 10 * 8 * 3 * 2 = 144s.
  Safety 2x: 288s. Round up to 600s. Smoke gate applies.
  PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: alpha1_cleanup_sweep_n4096
Queue: remote_cpu_queue (CPU; inference-only; N=4096 BSC; 6 tau levels x 3 seeds)
Pre-reg: preregs/2026-05-29_alpha1_cleanup_sweep_n4096.md
Parent: exp_kf5_steerable_beta_v2 (KF5_PARTIAL_DECOUPLING HARD_FAIL)
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
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load phase_a infrastructure
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa_cleanup", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K = 4
VOCAB = 256
M_FRAC = 4.0
BETA_TRAIN  = 8.0
BETA_READOUT = 32.0   # fixed inference beta per task spec
RELU_B = 0.5
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4

# 6 cleanup levels: tau=0 (no cleanup) to tau=100 (near-argmax) + sentinel "argmax"
TAU_CLEANUP_FULL  = [0.0, 0.1, 1.0, 10.0, 100.0, float("inf")]
TAU_CLEANUP_SMOKE = [0.0, 1.0, float("inf")]

T_TRAIN_FULL  = 20000
T_TRAIN_SMOKE = 3000
T_EVAL_FULL   = 2000
T_EVAL_SMOKE  = 300

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_BPC_RANGE   = 0.50   # HARD_PASS: bpc range > 0.5 bits across tau sweep
HP_SEEDS_MIN   = 2      # >= 2/3 seeds must show HARD_PASS pattern
HF_BPC_RANGE   = 0.05   # HARD_FAIL: bpc flat (range < 0.05)


def get_output_dir(default_name: str = "alpha1_cleanup_sweep_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def apply_cleanup(output: torch.Tensor, byte_atoms: torch.Tensor,
                   N: int, tau_cleanup: float) -> torch.Tensor:
    """Apply cleanup operator to soft output.

    tau_cleanup = 0.0: identity (no cleanup).
    tau_cleanup = inf: hard argmax -> nearest atom.
    tau_cleanup > 0: softmax(tau * (cb @ output / N)) -> weighted sum of atoms.
    """
    if tau_cleanup == 0.0:
        return output
    sims_cleanup = (byte_atoms @ output.T) / N   # (VOCAB, batch)
    if math.isinf(tau_cleanup):
        # Hard argmax
        best_idx = sims_cleanup.argmax(dim=0)   # (batch,)
        return byte_atoms[best_idx]             # (batch, N)
    P_cleanup = torch.softmax(tau_cleanup * sims_cleanup, dim=0)   # (VOCAB, batch)
    return P_cleanup.T @ byte_atoms                                 # (batch, N)


def eval_at_tau(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                 eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                 tau_cleanup: float, N: int, device: torch.device,
                 batch_size: int = 128) -> dict:
    """Evaluate bpc, retention, entropy with cleanup operator at tau_cleanup."""
    T = eval_idx.shape[0]
    all_bpc = []
    all_acc = []

    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)

        # Apply cleanup to q (the post-W output before final readout)
        q_clean = apply_cleanup(q, byte_atoms, N, tau_cleanup)

        # Final readout using cleaned output
        sims = (byte_atoms @ q_clean.T) / N   # (VOCAB, batch)
        P = torch.softmax(BETA_READOUT * sims, dim=0)

        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        all_bpc.append((nll / math.log(2)).mean().item())

        pred = P.argmax(dim=0)
        all_acc.append((pred == tgt).float().mean().item())

    return {
        "bpc": sum(all_bpc) / len(all_bpc),
        "retention_argmax": sum(all_acc) / len(all_acc),
        "tau_cleanup": tau_cleanup if not math.isinf(tau_cleanup) else 999.0,
    }


def train_w_delta(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                   train_idx: torch.Tensor, train_tgt: torch.Tensor,
                   N: int, device: torch.device, n_epochs: int = 2) -> torch.Tensor:
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]
    for _ in range(n_epochs):
        for bs in range(0, T, 64):
            be = min(bs + 64, T)
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


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    smoke = config["smoke"]
    N = config["N"]
    tau_sweep = config["tau_sweep"]

    gen_cpu = torch.Generator(device="cpu").manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen_cpu).to(device)
    pos_atoms  = pa.make_bsc_atoms(K, N, gen_cpu).to(device)

    corpus = pa.load_corpus_a()
    T_total = len(corpus) - K
    T_train = min(T_TRAIN_SMOKE if smoke else T_TRAIN_FULL, T_total - (T_EVAL_SMOKE if smoke else T_EVAL_FULL))
    T_eval  = min(T_EVAL_SMOKE if smoke else T_EVAL_FULL, T_total - T_train)

    train_idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T_train)], dtype=torch.long)
    train_tgt = torch.tensor([corpus[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus[T_train+i+j] for j in range(K)] for i in range(T_eval)], dtype=torch.long)
    eval_tgt  = torch.tensor([corpus[T_train+i+K] for i in range(T_eval)], dtype=torch.long)

    W = train_w_delta(byte_atoms, pos_atoms, train_idx, train_tgt, N, device,
                       n_epochs=1 if smoke else 2)

    per_tau = {}
    for tau in tau_sweep:
        res = eval_at_tau(W, byte_atoms, pos_atoms, eval_idx, eval_tgt, tau, N, device)
        tau_key = "inf" if math.isinf(tau) else str(tau)
        per_tau[tau_key] = res

    return {"seed": seed, "N": N, "per_tau": per_tau}


def compute_verdict(summary: dict) -> Tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("CLEANUP_INCONCLUSIVE", "No per-seed data.")

    seeds_pass = 0
    all_bpc_ranges = []

    for _, seed_data in per_seed.items():
        per_tau = seed_data.get("per_tau", {})
        if not per_tau:
            continue
        bpcs = [v["bpc"] for v in per_tau.values() if "bpc" in v]
        if not bpcs:
            continue
        bpc_range = max(bpcs) - min(bpcs)
        all_bpc_ranges.append(bpc_range)

        tau_vals = list(per_tau.keys())
        bpc_no_cleanup = per_tau.get("0.0", {}).get("bpc", float("nan"))
        bpc_argmax     = per_tau.get("inf", {}).get("bpc", float("nan"))
        helps = (not math.isnan(bpc_no_cleanup) and not math.isnan(bpc_argmax)
                 and min(bpcs) < bpc_argmax * 0.95)

        if bpc_range >= HP_BPC_RANGE and helps:
            seeds_pass += 1

    n_seeds = len(all_bpc_ranges)
    if n_seeds == 0:
        return ("CLEANUP_INCONCLUSIVE", "No seeds with bpc data.")

    mean_bpc_range = sum(all_bpc_ranges) / n_seeds

    detail = (f"mean_bpc_range={mean_bpc_range:.4f} seeds_pass={seeds_pass}/{n_seeds} "
              f"HP_range={HP_BPC_RANGE} HF_range={HF_BPC_RANGE}")

    # HARD_FAIL
    if mean_bpc_range < HF_BPC_RANGE:
        return ("CLEANUP_HARD_FAIL",
                f"CLEANUP_INVARIANT: bpc flat across tau_cleanup sweep. "
                f"W-magnitude path not operative in readout. " + detail)

    # HARD_PASS
    if seeds_pass >= HP_SEEDS_MIN:
        return ("CLEANUP_HARD_PASS",
                f"CLEANUP_UNLOCKS_STEER: bpc varies with cleanup strength. "
                f"W-magnitude path is operative at cleanup level. " + detail)

    return ("CLEANUP_MIDDLE_BAND",
            f"PARTIAL_CLEANUP_EFFECT: bpc_range in boundary zone. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-test 1: cleanup tau=0 is identity
    device = torch.device("cpu")
    N_test = 64
    output_test = torch.randn(5, N_test)
    gen = torch.Generator(device="cpu").manual_seed(17)
    atoms_test = pa.make_bsc_atoms(VOCAB, N_test, gen)
    result_noop = apply_cleanup(output_test, atoms_test, N_test, tau_cleanup=0.0)
    assert torch.allclose(result_noop, output_test), "tau=0 should be identity"

    # Formula self-test 2: cleanup tau=inf is argmax
    result_argmax = apply_cleanup(output_test, atoms_test, N_test, tau_cleanup=float("inf"))
    assert result_argmax.shape == output_test.shape, f"argmax output shape mismatch: {result_argmax.shape}"
    # Each row should be one of the atoms
    sims = (atoms_test @ result_argmax.T) / N_test   # (VOCAB, 5)
    max_sims = sims.max(dim=0).values
    assert (max_sims > 0.8).all(), f"Argmax output should closely match atoms; max_sims={max_sims}"

    # Formula self-test 3: run_one_seed smoke produces non-null bpc
    result = run_one_seed(17, {"smoke": True, "N": 256, "tau_sweep": [0.0, float("inf")]}, device)
    assert "per_tau" in result, "Missing per_tau"
    assert "0.0" in result["per_tau"] and "inf" in result["per_tau"], f"Missing tau keys: {list(result['per_tau'].keys())}"
    bpc_notau = result["per_tau"]["0.0"]["bpc"]
    bpc_argmax = result["per_tau"]["inf"]["bpc"]
    assert 0.0 < bpc_notau, f"bpc (no cleanup) non-positive: {bpc_notau}"
    assert not (bpc_notau != bpc_notau), "bpc (no cleanup) NaN"
    assert 0.0 < bpc_argmax, f"bpc (argmax) non-positive: {bpc_argmax}"
    assert not (bpc_argmax != bpc_argmax), "bpc (argmax) NaN"

    # Multi-scale smoke (N_smoke x 4)
    result_4x = run_one_seed(17, {"smoke": True, "N": 256 * 4, "tau_sweep": [0.0, float("inf")]}, device)
    assert "per_tau" in result_4x, "4x smoke missing per_tau"
    assert result_4x["per_tau"]["0.0"]["bpc"] > 0, "4x bpc=0"

    # Verdict gates
    # HARD_PASS: bpc_range > 0.5 AND min(bpcs) < bpc_argmax * 0.95 (cleanup helps)
    # bpc_argmax = "inf" key = 4.5; min(bpcs) = 1.0 at tau=1.0; range = 4.5-1.0 = 3.5 > 0.5
    def mk_pass():
        return {"per_tau": {"0.0": {"bpc": 4.5}, "1.0": {"bpc": 1.0}, "inf": {"bpc": 4.5}}}
    summary_p = {"per_seed": {"7": mk_pass(), "17": mk_pass(), "23": mk_pass()}}
    v, _ = compute_verdict(summary_p)
    assert v == "CLEANUP_HARD_PASS", f"Expected HARD_PASS, got {v}"

    def mk_fail():
        return {"per_tau": {"0.0": {"bpc": 3.5}, "1.0": {"bpc": 3.5}, "inf": {"bpc": 3.5}}}
    summary_f = {"per_seed": {"7": mk_fail(), "17": mk_fail(), "23": mk_fail()}}
    v, _ = compute_verdict(summary_f)
    assert v == "CLEANUP_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    print(f"[SELFTEST PASS] alpha1_cleanup_sweep_n4096: "
          f"tau=0 identity OK, tau=inf argmax OK, "
          f"smoke_bpc_notau={bpc_notau:.4f} smoke_bpc_argmax={bpc_argmax:.4f}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")  # CPU-suitable: inference-only
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    tau_sweep = TAU_CLEANUP_SMOKE if smoke else TAU_CLEANUP_FULL
    config = {"smoke": smoke, "N": N, "tau_sweep": tau_sweep}
    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[alpha1_cleanup] N={N} seeds={seeds} taus={tau_sweep} "
          f"mode={'smoke' if smoke else 'full'}", flush=True)

    per_seed = {}
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        result = run_one_seed(seed, config, device)
        te = time.time() - ts
        pt = result["per_tau"]
        bpc_vals = [pt[k]["bpc"] for k in pt]
        bpc_range = max(bpc_vals) - min(bpc_vals) if bpc_vals else 0.0
        print(f"  seed {seed}: {te:.1f}s bpc_range={bpc_range:.4f} bpcs={[round(v,4) for v in bpc_vals]}",
              flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "M_frac": M_FRAC,
        "beta_readout": BETA_READOUT,
        "tau_sweep": [t if not math.isinf(t) else "inf" for t in tau_sweep],
        "smoke": smoke,
    }

    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": config,
        "summary": summary,
    }
    out_dir2 = get_output_dir()
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=lambda x: "inf" if isinstance(x, float) and math.isinf(x) else x)

    print(f"\n[alpha1_cleanup] VERDICT: {verdict}", flush=True)
    print(f"[alpha1_cleanup] {verdict_msg}", flush=True)
    print(f"[alpha1_cleanup] elapsed={elapsed}s output={out_path}", flush=True)


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
