"""KF-5 MULTI-OUTPUT STEERABILITY TEST: top-k diversity + entropy sweep at N=4096.

PARENT: exp_kf5_steerable_beta_v2.py -- v2 HARD_FAIL (PARTIAL_DECOUPLING: entropy changes
  with beta but argmax/bpc show no steerability). v2 tested argmax-level steerability.
  This script tests multi-output diversity: does top-k output distribution CHANGE with beta
  even though the argmax label does not? If yes, KF-5 reformulates from 'argmax steerability'
  to 'output-distribution steerability'.

SCIENTIFIC QUESTION (KF-5 post-PARTIAL_DECOUPLING):
  At fixed M_frac=4, N=4096, BSC codebook:
  - Do top-k output indices (k in {1,5,10}) CHANGE across beta in {2,8,16,32,64,128}?
  - Does output distribution entropy vary with beta (as seen in v2) but at a RANK level
    (top-5 set changes) rather than only at a probability magnitude level?
  - Does mean output entropy change by >1 bit across beta sweep?
  If top-5 set changes substantially: steerability EXISTS at multi-output level.
  If top-1 set changes but top-5 set doesn't: argmax-level steerability only.
  If neither: KF-5 collapses to 1D (only entropy changes, not output set).

PRE-REGISTERED BANDS:
  HARD_PASS: mean_topk_jaccard_change(k=5) >= 0.30 across beta sweep in >= 3/5 seeds
    AND mean_entropy_range >= 1.0 bit.
    Interpretation: multi-output distribution IS steerable; KF-5 reformulation valid.
  HARD_FAIL: mean_topk_jaccard_change(k=5) < 0.10 across all betas and all seeds
    AND entropy_range < 0.5 bits.
    Interpretation: no multi-output steerability; KF-5 collapses to entropy-only.
  MIDDLE_BAND: topk_jaccard_change in [0.10, 0.30) OR entropy_range in [0.5, 1.0).
    Interpretation: partial multi-output steerability; refine KF-5 scope.

  NOTE: calibration probe (no prior empirical multi-output diversity anchor).
  Bands per calibration-probe policy: "no prior empirical anchor; HARD-PASS at 0.30
  Jaccard change (+-50% of theoretical expectation ~0.20-0.40 for beta sweep)."

FORMULA SELF-TESTS:
  1. Jaccard similarity J(A,B) = |A intersect B| / |A union B|. Range [0,1].
  2. Jaccard CHANGE = 1 - J(topk(beta_ref), topk(beta_test)). Range [0,1].
  3. At beta->0: top-k is near-random (high change vs any reference). At beta->inf: deterministic (low change).
  4. entropy = -sum_i p_i log2(p_i). Range [0, log2(VOCAB)].
  5. N == 4096 (PROT-018 binding).
  6. BSC codebook: safe at any N (not Kerdock, no even-log2 constraint).
  7. mean_topk_jaccard_change = mean over probe positions of (1 - J(topk_beta_ref, topk_beta)).

OOM CHECK:
  W at N=4096 float32: 64MB. BSC codebook C=256: 1MB. No OOM risk. OK.

TIMEOUT ESTIMATE:
  Parent v2 smoke at N=1024, 1 seed, 3 betas: ~0.3s.
  This script: N=4096, 5 seeds, 6 betas, top-k eval. Extra metric overhead ~2x.
  N-scale: (4096/1024)^1.5 = 8x. seed: 5. beta: 6/3 = 2x. metric 2x.
  timeout_s = ceil(1.5 * 0.3 * 8 * 5 * 2 * 2) = ceil(72) -> 300s minimum.
  GPU speedup ~10x over CPU: 300 / 10 = 30s. Add safety margin. Estimate: 600s.
  PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.
  (floor applies; N=4096 deep probe with 5 seeds + 6 betas)

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf5_multi_output_steer_n4096
Queue: overnight_queue (GPU; N=4096 BSC; 5 seeds x 6 betas x top-k)
Pre-reg: preregs/2026-05-29_kf5_multi_output_steer_n4096.md
Parent: exp_kf5_steerable_beta_v2 (KF5_PARTIAL_DECOUPLING HARD_FAIL: entropy-only)
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
from typing import Dict, List, Set, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load phase_a infrastructure (BSC atoms, corpus, train, eval helpers)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa_msteer", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K = 4
VOCAB = 256
M_FRAC = 4.0         # fixed per task spec
BETA_TRAIN = 8.0

BETA_SWEEP_FULL  = [2.0, 8.0, 16.0, 32.0, 64.0, 128.0]
BETA_SWEEP_SMOKE = [2.0, 32.0, 128.0]

TOP_K_VALUES = [1, 5, 10]
BETA_REF = 32.0      # reference beta for Jaccard change calculation

DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4
RELU_B = 0.5
T_TRAIN_FULL  = 20000
T_TRAIN_SMOKE = 3000
T_EVAL_FULL   = 2000
T_EVAL_SMOKE  = 300

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_JACCARD_CHANGE_K5 = 0.30   # HARD_PASS: top-5 Jaccard change >= 0.30
HP_ENTROPY_RANGE     = 1.0    # HARD_PASS: entropy range >= 1.0 bit
HP_SEEDS_MIN         = 3      # >= 3/5 seeds must show HARD_PASS pattern
HF_JACCARD_MAX       = 0.10   # HARD_FAIL: change < 0.10 AND entropy_range < 0.5
HF_ENTROPY_RANGE_MAX = 0.5


def get_output_dir(default_name: str = "kf5_multi_output_steer_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compute_entropy(P: torch.Tensor) -> torch.Tensor:
    """Entropy of distribution P (vocab_size, batch). Returns (batch,) in bits."""
    eps = 1e-12
    return -(P * torch.log2(P + eps)).sum(dim=0)


def topk_set(P: torch.Tensor, k: int) -> List[Set[int]]:
    """Get top-k indices for each position in P (vocab, batch). Returns list of sets."""
    _, indices = torch.topk(P, k, dim=0)  # (k, batch)
    return [set(indices[:, j].tolist()) for j in range(P.shape[1])]


def jaccard_change(set_ref: List[Set[int]], set_test: List[Set[int]]) -> float:
    """Mean Jaccard change (1 - J) between two lists of sets."""
    changes = []
    for a, b in zip(set_ref, set_test):
        union_sz = len(a | b)
        inter_sz = len(a & b)
        if union_sz > 0:
            changes.append(1.0 - inter_sz / union_sz)
        else:
            changes.append(0.0)
    return sum(changes) / len(changes) if changes else 0.0


def train_w_delta(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                   train_idx: torch.Tensor, train_tgt: torch.Tensor,
                   N: int, device: torch.device,
                   n_epochs: int = 2, batch_size: int = 64) -> torch.Tensor:
    """Train W using delta rule. Adapted from exp_kf5_steerable_beta_v2."""
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


def eval_multi_output(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                       eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                       beta_inf: float, N: int, device: torch.device,
                       batch_size: int = 128) -> dict:
    """Evaluate at given beta; return entropy + top-k index sets."""
    T = eval_idx.shape[0]
    all_entropy = []
    topk_sets: Dict[int, List[Set[int]]] = {k: [] for k in TOP_K_VALUES}
    all_bpc = []

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
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        all_bpc.append((nll / math.log(2)).mean().item())

        for k_val in TOP_K_VALUES:
            k_actual = min(k_val, VOCAB)
            topk_sets[k_actual].extend(topk_set(P, k_actual))

    return {
        "output_entropy_bits": sum(all_entropy) / len(all_entropy),
        "bpc": sum(all_bpc) / len(all_bpc),
        "topk_sets": {k: v for k, v in topk_sets.items()},
    }


def run_one_seed(seed: int, config: dict, device: torch.device) -> dict:
    smoke = config["smoke"]
    N = config["N"]
    beta_sweep = config["beta_sweep"]

    gen_cpu = torch.Generator(device="cpu").manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen_cpu).to(device)
    pos_atoms  = pa.make_bsc_atoms(K, N, gen_cpu).to(device)

    corpus = pa.load_corpus_a()
    T_total = len(corpus) - K
    T_train = min(T_TRAIN_SMOKE if smoke else T_TRAIN_FULL, T_total - (T_EVAL_SMOKE if smoke else T_EVAL_FULL))
    T_eval  = min(T_EVAL_SMOKE if smoke else T_EVAL_FULL, T_total - T_train)

    train_idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T_train)], dtype=torch.long)
    train_tgt = torch.tensor([corpus[i+K] for i in range(T_train)], dtype=torch.long)
    eval_start = T_train
    eval_idx  = torch.tensor([[corpus[eval_start+i+j] for j in range(K)] for i in range(T_eval)], dtype=torch.long)
    eval_tgt  = torch.tensor([corpus[eval_start+i+K] for i in range(T_eval)], dtype=torch.long)

    W = train_w_delta(byte_atoms, pos_atoms, train_idx, train_tgt, N, device,
                       n_epochs=1 if smoke else 2)

    per_beta = {}
    for beta_inf in beta_sweep:
        res = eval_multi_output(W, byte_atoms, pos_atoms, eval_idx, eval_tgt,
                                 beta_inf, N, device)
        # Summarize top-k sets -> Jaccard change vs BETA_REF
        # Store only the per-beta aggregate metrics (not full set lists -- too large)
        per_beta[str(beta_inf)] = {
            "output_entropy_bits": res["output_entropy_bits"],
            "bpc": res["bpc"],
            "n_eval": T_eval,
        }
        # Store topk_sets temporarily in res for cross-beta comparison
        per_beta[str(beta_inf) + "_topk_sets"] = res["topk_sets"]

    # Compute Jaccard changes vs reference beta
    ref_key = str(BETA_REF) + "_topk_sets"
    ref_sets = per_beta.get(ref_key, {})

    for beta_inf in beta_sweep:
        if beta_inf == BETA_REF:
            for k_val in TOP_K_VALUES:
                per_beta[str(beta_inf)][f"jaccard_change_k{k_val}"] = 0.0
            continue
        test_key = str(beta_inf) + "_topk_sets"
        test_sets = per_beta.get(test_key, {})
        for k_val in TOP_K_VALUES:
            ref_k = ref_sets.get(k_val, [])
            test_k = test_sets.get(k_val, [])
            if ref_k and test_k:
                jc = jaccard_change(ref_k[:len(test_k)], test_k[:len(ref_k)])
            else:
                jc = 0.0
            per_beta[str(beta_inf)][f"jaccard_change_k{k_val}"] = round(jc, 5)

    # Remove temp topk_sets entries (too large to store)
    for beta_inf in beta_sweep:
        per_beta.pop(str(beta_inf) + "_topk_sets", None)

    return {"seed": seed, "N": N, "per_beta": per_beta}


def compute_verdict(summary: dict) -> Tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("KF5_MSTEER_INCONCLUSIVE", "No per-seed data.")

    # Per seed: compute entropy_range and max jaccard_change_k5
    seeds_pass_jc = 0
    all_entropy_ranges = []
    all_jc_k5 = []

    for seed_key, seed_data in per_seed.items():
        per_beta = seed_data.get("per_beta", {})
        if not per_beta:
            continue

        betas = sorted([float(k) for k in per_beta.keys()])
        entropies = [per_beta[str(b)]["output_entropy_bits"] for b in betas]
        entropy_range = max(entropies) - min(entropies) if entropies else 0.0
        all_entropy_ranges.append(entropy_range)

        jc_k5_vals = [per_beta[str(b)].get("jaccard_change_k5", 0.0) for b in betas]
        max_jc_k5 = max(jc_k5_vals) if jc_k5_vals else 0.0
        all_jc_k5.append(max_jc_k5)

        if max_jc_k5 >= HP_JACCARD_CHANGE_K5 and entropy_range >= HP_ENTROPY_RANGE:
            seeds_pass_jc += 1

    n_seeds = len(all_entropy_ranges)
    if n_seeds == 0:
        return ("KF5_MSTEER_INCONCLUSIVE", "No seeds with data.")

    mean_entropy_range = sum(all_entropy_ranges) / n_seeds
    mean_jc_k5 = sum(all_jc_k5) / n_seeds

    detail = (f"mean_jc_k5={mean_jc_k5:.3f} mean_entropy_range={mean_entropy_range:.3f}bits "
              f"seeds_pass={seeds_pass_jc}/{n_seeds} "
              f"HP_jc={HP_JACCARD_CHANGE_K5} HP_entropy={HP_ENTROPY_RANGE} "
              f"HF_jc={HF_JACCARD_MAX} HF_entropy={HF_ENTROPY_RANGE_MAX}")

    # HARD_FAIL: no multi-output steerability
    if mean_jc_k5 < HF_JACCARD_MAX and mean_entropy_range < HF_ENTROPY_RANGE_MAX:
        return ("KF5_MSTEER_HARD_FAIL",
                f"NO_MULTI_OUTPUT_STEER: top-5 set static across beta. "
                f"KF-5 collapses to 1D (entropy-only but no set change). " + detail)

    # HARD_PASS
    if seeds_pass_jc >= HP_SEEDS_MIN:
        return ("KF5_MSTEER_HARD_PASS",
                f"MULTI_OUTPUT_STEER_CONFIRMED: top-5 output set changes with beta. "
                f"KF-5 reformulation valid: steerability at multi-output layer. " + detail)

    return ("KF5_MSTEER_MIDDLE_BAND",
            f"PARTIAL_MSTEER: some diversity change but below threshold. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-test 1: entropy formula
    P_uniform = torch.ones(VOCAB, 1) / float(VOCAB)
    H_u = compute_entropy(P_uniform).item()
    assert abs(H_u - math.log2(VOCAB)) < 0.01, f"H(uniform) should be {math.log2(VOCAB):.2f}; got {H_u}"

    # Formula self-test 2: Jaccard change
    set_a = [frozenset([1, 2, 3, 4, 5])]
    set_b = [frozenset([1, 2, 3, 4, 5])]
    jc_same = jaccard_change([set(s) for s in set_a], [set(s) for s in set_b])
    assert abs(jc_same) < 0.01, f"Identical sets should have 0 change; got {jc_same}"

    set_c = [frozenset([6, 7, 8, 9, 10])]
    jc_disjoint = jaccard_change([set(s) for s in set_a], [set(s) for s in set_c])
    assert abs(jc_disjoint - 1.0) < 0.01, f"Disjoint sets should have 1.0 change; got {jc_disjoint}"

    # Formula self-test 3: HARD_PASS verdict
    def mk_pass_seed():
        pb = {}
        for b, h, jc5 in [(2.0, 7.0, 0.50), (8.0, 4.0, 0.0), (32.0, 3.5, 0.0), (128.0, 0.5, 0.35)]:
            pb[str(b)] = {"output_entropy_bits": h, "bpc": 4.0, "jaccard_change_k5": jc5, "n_eval": 100}
        return {"per_beta": pb}
    summary_p = {"per_seed": {str(s): mk_pass_seed() for s in [7, 17, 23, 31, 41]}}
    v, _ = compute_verdict(summary_p)
    assert v == "KF5_MSTEER_HARD_PASS", f"Expected HARD_PASS, got {v}"

    # Formula self-test 4: HARD_FAIL verdict
    def mk_fail_seed():
        pb = {}
        for b in [2.0, 8.0, 32.0, 128.0]:
            pb[str(b)] = {"output_entropy_bits": 4.0, "bpc": 3.5, "jaccard_change_k5": 0.02, "n_eval": 100}
        return {"per_beta": pb}
    summary_f = {"per_seed": {str(s): mk_fail_seed() for s in [7, 17, 23, 31, 41]}}
    v, _ = compute_verdict(summary_f)
    assert v == "KF5_MSTEER_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    # Smoke forward pass: run one seed at tiny scale
    device = torch.device("cpu")
    N_test = 512
    result = run_one_seed(17, {"smoke": True, "N": N_test, "beta_sweep": [2.0, 32.0]}, device)
    assert "per_beta" in result, "Missing per_beta"
    beta_keys = list(result["per_beta"].keys())
    assert len(beta_keys) >= 2, f"Expected >= 2 beta keys; got {len(beta_keys)}"
    for bk in beta_keys:
        cell = result["per_beta"][bk]
        assert "output_entropy_bits" in cell, f"Missing output_entropy_bits in {bk}"
        H = cell["output_entropy_bits"]
        assert 0.0 <= H <= math.log2(VOCAB) + 0.01, f"Entropy out of range: {H}"
        assert "jaccard_change_k5" in cell, f"Missing jaccard_change_k5 in {bk}"
        jc = cell["jaccard_change_k5"]
        assert 0.0 <= jc <= 1.0, f"Jaccard change out of [0,1]: {jc}"

    # 4x smoke scale test (multi-scale gate)
    result_4x = run_one_seed(17, {"smoke": True, "N": N_test * 4, "beta_sweep": [2.0, 32.0]}, device)
    assert "per_beta" in result_4x, "4x smoke missing per_beta"

    print("[SELFTEST PASS] kf5_multi_output_steer_n4096: entropy OK, Jaccard OK, "
          f"smoke_entropy={result['per_beta']['2.0']['output_entropy_bits']:.3f}bits", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    config = {"smoke": smoke, "N": N, "beta_sweep": beta_sweep}
    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[kf5_msteer] N={N} seeds={seeds} betas={beta_sweep} "
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
        max_jc = max(pb[str(b)].get("jaccard_change_k5", 0.0) for b in betas)
        print(f"  seed {seed}: {te:.1f}s entropy_range={e_range:.3f}bits max_jc_k5={max_jc:.3f}",
              flush=True)
        per_seed[str(seed)] = result

    summary = {
        "per_seed": per_seed,
        "N_full": N_FULL,
        "N_used": N,
        "M_frac": M_FRAC,
        "beta_sweep": beta_sweep,
        "beta_ref": BETA_REF,
        "smoke": smoke,
    }

    out_dir2 = get_output_dir()
    checkpoint_path = out_dir2 / "metrics_checkpoint.json"
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    verdict, verdict_msg = compute_verdict(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 2),
        "config": config,
        "summary": summary,
    }
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[kf5_msteer] VERDICT: {verdict}", flush=True)
    print(f"[kf5_msteer] {verdict_msg}", flush=True)
    print(f"[kf5_msteer] elapsed={elapsed:.1f}s output={out_path}", flush=True)


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
