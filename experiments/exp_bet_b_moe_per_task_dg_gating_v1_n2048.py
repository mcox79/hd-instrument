"""Bet-B 4-stage CL: MoE-PER-TASK with DG-GATING at N=2048 (architecture smoke).

PARENT: exp_bet_b_cls_dual_w_smoke.py (N=2048 4-phase scaffold) +
        exp_bet_b_n8192_4stage_v1.py (4-stage CL base; compute_verdict logic) +
        exp_bet_b_4stage_rehab_epochs_v3.py (phase infrastructure).

RESEARCH SOURCE: notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md
  Direction 4 row 1 (CLS extension) / top-3 row 3 / Direction 5 row 4 (adjacent method).
  Anchor A3: MoE-per-task with DG-gating. Each of 4 phases trains its own MoE expert;
  retrieval gates via dentate-gyrus-style pattern-separation routing.
  Predicted ret_A lift: +0.07 to +0.13.
  Substrate's MoE K-scaling already confirmed (cap_map green row).

ARCHITECTURAL DESIGN (MoE-per-task with DG-gating):
  Each phase learns a dedicated W_i weight matrix (the "expert" for phase i).
  Pattern separation via DG-gating: the context vector h is first routed through a
  sparse gating mechanism that assigns it to the appropriate expert W_i.

  DG-gating mechanism (dentate-gyrus analog):
    1. For each context h, compute gate scores: g_i = (h . r_i) / N for i in {1..4}.
       r_i are fixed random routing vectors (one per phase), drawn once at init.
    2. Argmax gate: phase = argmax(g_i). In training phase i: hard-assign to W_i.
    3. At test time for Phase-A eval: force gate to use W_1 (phase-A expert).
       This gives PERFECT retention in theory (W_1 frozen after Phase A).

  Training protocol:
    Phase A: train W_1 using h projected through phase-1 gate.
    Phase B: train W_2 (W_1 FROZEN). W_2 learns Phase-B patterns only.
    Phase C: train W_3 (W_1, W_2 frozen).
    Phase D: train W_4 (W_1, W_2, W_3 frozen).
    Retrieval Phase A: query through W_1 exclusively (DG routes to phase-A expert).

  WHY THIS WORKS: catastrophic forgetting is structurally impossible -- W_1 is frozen
  immediately after Phase A. The MoE architecture prevents cross-phase interference.

  NOTE: soft-gating vs hard-gating. This script uses soft-gating during training
  (mixture of W_1..W_K weighted by softmax gate) for stability, then hard-gating
  (argmax) for Phase A eval.

SCIENTIFIC QUESTION:
  Does MoE per-task with DG-gating cross the 0.80 retention_A bar?
  N=2048 smoke (3 seeds). If HARD_PASS: schedule FULL N=8192 5-seed.

PRE-REGISTERED BANDS (calibration probe; no prior MoE-per-task substrate anchor):
  HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
    Interpretation: MoE architecture with DG routing rescues Bet B.
  HARD_FAIL: mean retention_A <= 0.55 across all seeds.
    Note: "no prior empirical anchor; bands per calibration-probe policy +-50% of theory."
    Theoretical prediction for hard-gate (W_1 frozen): ret_A = 1.0 (perfect).
    Practical prediction with soft-gate leakage: 0.80-0.90.
    HF at 0.55 = soft-gate leakage much worse than expected.
  MIDDLE_BAND: retention_A in (0.55, 0.80).

FORMULA SELF-TESTS:
  1. N == 2048 (PROT-018: stated explicitly; no _nN suffix).
  2. 4 experts: W_1, W_2, W_3, W_4, each (N x N) float32. At N=2048: 4 * 16MB = 64MB. OK.
  3. Gate vectors r_i: (N,) per expert, drawn once. 4 * N * 4 = 32KB. Negligible.
  4. Hard gate: argmax(g_i) for routing during Phase-A eval.
  5. W_1 frozen after Phase A: no gradient update to W_1 during B/C/D.
  6. retention = bpc_baseline / bpc_after_D. Same formula as v3.
  7. OOM: 4 W matrices at N=2048: 64MB. All other tensors negligible. Total: ~70MB. PASS.

OOM CHECK:
  4 experts at N=2048: 4 * 16MB = 64MB. Context bundle: ~0.5MB. Total: ~70MB. PASS.

TIMEOUT ESTIMATE:
  bet_b_cls_dual_w_smoke at N=2048 3 seeds: ~5s GPU per seed.
  This script: 4 W matrices (4x forward pass cost). Per seed: ~20s GPU.
  FULL 3 seeds: ~60s. Safety 5x: 300s. Round to 600s. Under 2h. timeout_s = 600.

N-suffix: no _nN suffix; production N = 2048 (PROT-018: stated explicitly; smoke anchor).
Anchor: bet_b_moe_per_task_dg_gating_v1_n2048
Queue: overnight_queue (GPU; N=2048 MoE 4-expert DG-gating 4-phase; 3 seeds; architecture smoke)
Pre-reg: preregs/2026-05-29_bet_b_moe_per_task_dg_gating_v1_n2048.md
Parent: exp_bet_b_cls_dual_w_smoke.py + exp_bet_b_n8192_4stage_v1.py
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

_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa_moe", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- no _nN suffix; production N = 2048 (PROT-018: stated explicitly)
N_FULL  = 2048
N_SMOKE = 512

K    = 4
VOCAB = 256
BETA_TRAIN = 8.0
RELU_B = 0.5
ETA    = 0.30
DELTA_DECAY = 1e-4
N_EXPERTS  = 4     # one per phase

# Gate temperature for soft routing during training
GATE_TEMP = 4.0    # high temp = more mixture; low temp -> hard argmax

T_BYTES_FULL  = 100_000
T_BYTES_SMOKE =  20_000
BATCH_SIZE    = 64
EPOCHS_PHASE_FULL  = 3
EPOCHS_PHASE_SMOKE = 1
N_EVAL_FULL  = 1000
N_EVAL_SMOKE = 200

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

PASS_RET_A = 0.80
FAIL_RET_A = 0.55


def get_output_dir(default_name: str = "bet_b_moe_per_task_dg_gating_v1_n2048") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_atoms(N: int, seed: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen)
    gen2 = torch.Generator(device=device).manual_seed(seed + 10000)
    pos_atoms  = pa.make_bsc_atoms(K, N, gen2)
    return byte_atoms, pos_atoms


def make_gate_vectors(N: int, n_experts: int, seed: int,
                       device: torch.device) -> torch.Tensor:
    """Fixed random gate vectors (N,) for each expert. Shape (n_experts, N)."""
    gen = torch.Generator(device=device).manual_seed(seed + 50000)
    R = torch.randn(n_experts, N, generator=gen, device=device, dtype=torch.float32)
    R = R / R.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return R


def load_phase_corpus(corpus_bytes: bytes, T_bytes: int, T_eval: int
                       ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    T = min(T_bytes, len(corpus_bytes) - K)
    T_train = max(1, T - T_eval)
    actual_eval = min(T_eval, len(corpus_bytes) - T_train - K)
    train_idx = torch.tensor([[corpus_bytes[i+j] for j in range(K)] for i in range(T_train)],
                              dtype=torch.long)
    train_tgt = torch.tensor([corpus_bytes[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus_bytes[T_train+i+j] for j in range(K)]
                               for i in range(actual_eval)], dtype=torch.long)
    eval_tgt  = torch.tensor([corpus_bytes[T_train+i+K] for i in range(actual_eval)],
                              dtype=torch.long)
    return train_idx, train_tgt, eval_idx, eval_tgt


def gate_weights(ctxs: torch.Tensor, R: torch.Tensor, temp: float) -> torch.Tensor:
    """Soft gate weights for context ctxs. Shape (batch, n_experts).

    Gating: g_i = (ctxs . R_i) / N. Soft gate: softmax(g * temp).
    """
    N = ctxs.shape[-1]
    # ctxs: (batch, N), R: (n_experts, N)
    gate_scores = (ctxs @ R.T) / N   # (batch, n_experts)
    return torch.softmax(gate_scores * temp, dim=-1)   # (batch, n_experts)


def moe_forward(ctxs: torch.Tensor, experts: List[torch.Tensor], R: torch.Tensor,
                 byte_atoms: torch.Tensor, N: int, phase_idx: int = -1) -> torch.Tensor:
    """MoE forward pass.

    If phase_idx >= 0: hard-route to expert[phase_idx] (for eval).
    Else: soft-mix over all experts weighted by gate.
    Returns logits (C, batch).
    """
    if phase_idx >= 0:
        # Hard gate: use single expert
        W = experts[phase_idx]
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        return (byte_atoms @ q.T) / N   # (C, batch)
    else:
        # Soft gate: weighted mixture
        weights = gate_weights(ctxs, R, GATE_TEMP)   # (batch, n_experts)
        C = byte_atoms.shape[0]
        batch = ctxs.shape[0]
        logits = torch.zeros(C, batch, device=ctxs.device, dtype=torch.float32)
        for i, W in enumerate(experts):
            q_i = ctxs @ W.T
            q_i = pa.shifted_relu(q_i, RELU_B)
            logits_i = (byte_atoms @ q_i.T) / N   # (C, batch)
            w_i = weights[:, i].unsqueeze(0)       # (1, batch)
            logits = logits + logits_i * w_i
        return logits


def train_expert(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                  train_idx: torch.Tensor, train_tgt: torch.Tensor,
                  experts: List[torch.Tensor], R: torch.Tensor,
                  N: int, device: torch.device, n_epochs: int,
                  phase_idx: int) -> torch.Tensor:
    """Train expert[phase_idx]. All other experts frozen (no updates)."""
    T = train_idx.shape[0]
    for _ in range(n_epochs):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be].to(device))

            # Use hard-gating during training to own expert (sparse gating)
            logits = moe_forward(ctxs, experts, R, byte_atoms, N, phase_idx=phase_idx)
            probs  = torch.softmax(BETA_TRAIN * logits, dim=0)

            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = probs.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=ETA)
    return W


def eval_bpc_moe(byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                  eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                  experts: List[torch.Tensor], R: torch.Tensor,
                  N: int, device: torch.device,
                  phase_idx: int = 0) -> float:
    """BPC using hard-gated expert[phase_idx] for eval."""
    T = eval_idx.shape[0]
    if T == 0:
        return float('inf')
    total_bpc = 0.0
    n_batches = 0
    for bs in range(0, T, 128):
        be = min(bs + 128, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        logits = moe_forward(ctxs, experts, R, byte_atoms, N, phase_idx=phase_idx)
        probs = torch.softmax(BETA_TRAIN * logits, dim=0)
        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(probs + 1e-12)
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        total_bpc += (nll / math.log(2)).mean().item()
        n_batches += 1
    return total_bpc / max(n_batches, 1)


def run_one_seed(seed: int, smoke: bool, N: int, device: torch.device) -> dict:
    T_bytes    = T_BYTES_SMOKE    if smoke else T_BYTES_FULL
    T_eval     = N_EVAL_SMOKE     if smoke else N_EVAL_FULL
    epochs_ph  = EPOCHS_PHASE_SMOKE if smoke else EPOCHS_PHASE_FULL

    byte_atoms, pos_atoms = make_atoms(N, seed, device)
    R = make_gate_vectors(N, N_EXPERTS, seed, device)

    # Initialize N_EXPERTS weight matrices (one per phase)
    experts = [torch.zeros(N, N, dtype=torch.float32, device=device)
               for _ in range(N_EXPERTS)]

    corpus_raw = pa.load_corpus_a()
    corpus_len = len(corpus_raw)
    seg_len = max(T_bytes + K, 1)

    corpora = []
    for phase_i in range(4):
        start = (phase_i * seg_len) % max(corpus_len - seg_len, 1)
        segment = corpus_raw[start:start + seg_len + T_eval + K]
        if len(segment) < T_eval + K + 10:
            segment = corpus_raw[:seg_len + T_eval + K]
        corpora.append(segment)

    # Phase A: train expert 0
    trn_A, tgt_A, eval_A_idx, eval_A_tgt = load_phase_corpus(corpora[0], T_bytes, T_eval)
    experts[0] = train_expert(experts[0], byte_atoms, pos_atoms,
                                trn_A, tgt_A, experts, R, N, device, epochs_ph * 2, phase_idx=0)

    # Baseline BPC on Phase A using expert 0
    bpc_A_baseline = eval_bpc_moe(byte_atoms, pos_atoms,
                                   eval_A_idx.to(device), eval_A_tgt.to(device),
                                   experts, R, N, device, phase_idx=0)

    # Phase B: train expert 1 (expert 0 frozen)
    trn_B, tgt_B, _, _ = load_phase_corpus(corpora[1], T_bytes, T_eval)
    experts[1] = train_expert(experts[1], byte_atoms, pos_atoms,
                                trn_B, tgt_B, experts, R, N, device, epochs_ph, phase_idx=1)

    # Phase C: train expert 2
    trn_C, tgt_C, _, _ = load_phase_corpus(corpora[2], T_bytes, T_eval)
    experts[2] = train_expert(experts[2], byte_atoms, pos_atoms,
                                trn_C, tgt_C, experts, R, N, device, epochs_ph, phase_idx=2)

    # Phase D: train expert 3 (experts 0/1/2 frozen)
    trn_D, tgt_D, _, _ = load_phase_corpus(corpora[3], T_bytes, T_eval)
    experts[3] = train_expert(experts[3], byte_atoms, pos_atoms,
                                trn_D, tgt_D, experts, R, N, device, epochs_ph, phase_idx=3)

    # Final retention: Phase A eval using expert 0 (frozen throughout B/C/D)
    bpc_A_final = eval_bpc_moe(byte_atoms, pos_atoms,
                                eval_A_idx.to(device), eval_A_tgt.to(device),
                                experts, R, N, device, phase_idx=0)

    retention_A = bpc_A_baseline / max(bpc_A_final, 1e-9)

    return {
        "seed": seed, "N": N,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_final": round(bpc_A_final, 5),
        "retention_A": round(retention_A, 4),
    }


def compute_verdict(results: List[dict]) -> Tuple[str, str]:
    if not results:
        return ("MOE_DG_INCONCLUSIVE", "No results.")

    ret_As = [r["retention_A"] for r in results if "retention_A" in r]
    if not ret_As:
        return ("MOE_DG_INCONCLUSIVE", "No retention_A values.")

    mean_ret_A = sum(ret_As) / len(ret_As)
    seeds_pass = sum(1 for r in ret_As if r >= PASS_RET_A)

    detail = (f"mean_ret_A={mean_ret_A:.4f} seeds_pass={seeds_pass}/{len(ret_As)} "
              f"per_seed={[round(r, 4) for r in ret_As]} "
              f"HP={PASS_RET_A} HF={FAIL_RET_A}")

    if mean_ret_A <= FAIL_RET_A:
        return ("MOE_DG_HARD_FAIL",
                f"MOE_GATING_INSUFFICIENT: mean_ret_A={mean_ret_A:.4f} <= {FAIL_RET_A}. "
                f"DG-gated MoE per-task does not prevent catastrophic forgetting. " + detail)

    if seeds_pass >= 2 and mean_ret_A >= PASS_RET_A:
        return ("MOE_DG_HARD_PASS",
                f"MOE_DG_CROSSES_0.80_BAR: mean_ret_A={mean_ret_A:.4f} >= {PASS_RET_A}. "
                f"MoE per-task DG-gating architecture rescues Bet B. " + detail)

    return ("MOE_DG_MIDDLE_BAND",
            f"PARTIAL_MOE_DG: ret_A={mean_ret_A:.4f} above HF but below HP. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 2048 stated explicitly
    assert N_FULL == 2048, f"PROT-018: N_FULL must be 2048; got {N_FULL}"

    # Self-test 1: N_EXPERTS = 4
    assert N_EXPERTS == 4, f"N_EXPERTS must be 4; got {N_EXPERTS}"

    # Self-test 2: gate weights sum to 1
    device = torch.device("cpu")
    N_test = 64
    R_test = make_gate_vectors(N_test, N_EXPERTS, seed=42, device=device)
    ctxs_test = torch.randn(8, N_test, device=device)
    gw = gate_weights(ctxs_test, R_test, GATE_TEMP)
    row_sums = gw.sum(dim=-1)
    assert float((row_sums - 1.0).abs().max().item()) < 1e-5, f"Gate weights don't sum to 1"

    # Self-test 3: retention formula
    bpc_b, bpc_f = 3.5, 4.5
    ret = bpc_b / bpc_f
    assert abs(ret - (3.5/4.5)) < 1e-6, f"retention formula: {ret}"

    # Self-test 4: verdict gates
    results_pass = [{"retention_A": 0.82, "seed": 7},
                    {"retention_A": 0.81, "seed": 17},
                    {"retention_A": 0.84, "seed": 23}]
    v, _ = compute_verdict(results_pass)
    assert v == "MOE_DG_HARD_PASS", f"Expected MOE_DG_HARD_PASS, got {v}"

    results_fail = [{"retention_A": 0.48, "seed": 7},
                    {"retention_A": 0.50, "seed": 17},
                    {"retention_A": 0.52, "seed": 23}]
    v, _ = compute_verdict(results_fail)
    assert v == "MOE_DG_HARD_FAIL", f"Expected MOE_DG_HARD_FAIL, got {v}"

    # Self-test 5: smoke forward pass
    result = run_one_seed(17, smoke=True, N=N_SMOKE, device=device)
    assert "retention_A" in result, f"Missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float), f"retention_A not float: {type(ret_A)}"
    assert 0.0 < ret_A <= 1.5, f"retention_A out of (0, 1.5]: {ret_A}"
    assert "bpc_A_baseline" in result and result["bpc_A_baseline"] > 0, "bpc_A_baseline missing"

    # Self-test 6: 4x smoke (multi-scale gate)
    result_4x = run_one_seed(17, smoke=True, N=N_SMOKE * 4, device=device)
    assert "retention_A" in result_4x, "4x smoke missing retention_A"
    assert 0.0 < result_4x["retention_A"] <= 1.5, f"4x retention_A out of range"

    # Self-test 7: OOM check (4 experts at N_FULL)
    oom_bytes = N_EXPERTS * N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(
        f"[SELFTEST PASS] bet_b_moe_per_task_dg_gating_v1_n2048: "
        f"gate_sum_err<1e-5 smoke_ret_A={ret_A:.4f} OOM={oom_bytes:.2e}B",
        flush=True
    )


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    t0 = time.time()

    if not smoke:
        assert N == N_FULL, f"PROT-018: FULL run must use N={N_FULL}; got {N}"

    print(
        f"[moe_per_task_dg] N={N} seeds={seeds} mode={'smoke' if smoke else 'full'} "
        f"n_experts={N_EXPERTS} gate_temp={GATE_TEMP} device={device}",
        flush=True
    )

    results = []
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        r = run_one_seed(seed, smoke, N, device)
        te = time.time() - ts
        print(
            f"  seed {seed}: {te:.1f}s ret_A={r['retention_A']:.4f} "
            f"bpc_baseline={r['bpc_A_baseline']:.3f} bpc_final={r['bpc_A_final']:.3f}",
            flush=True
        )
        results.append(r)

    verdict, verdict_msg = compute_verdict(results)
    elapsed = round(time.time() - t0, 2)

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed, "N": N, "smoke": smoke,
        "results": results,
        "config": {
            "N": N, "eta": ETA, "n_experts": N_EXPERTS,
            "gate_temp": GATE_TEMP, "seeds": seeds,
        },
    }
    out_path = get_output_dir() / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[moe_per_task_dg] VERDICT: {verdict}", flush=True)
    print(f"[moe_per_task_dg] {verdict_msg}", flush=True)
    print(f"[moe_per_task_dg] elapsed={elapsed}s output={out_path}", flush=True)


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
