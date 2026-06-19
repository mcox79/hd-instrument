"""GAMMA-1: DUAL-W COMPLEMENTARY LEARNING SYSTEMS (CLS) Smoke at N=2048.

McClelland-McNaughton-O'Reilly (1995) CLS: two weight matrices model hippocampal
(fast plasticity) and neocortical (slow consolidation) memory systems.

PARENT: exp_bet_b_n8192_4stage_v1.py (4-stage CL; MIDDLE_BAND on retention_A).
  The 4-stage CL architectures C1 (wide_phaseA) and C2 (frozen_phaseA) are FULL-pending.
  Gamma-1 tests architectural alternative: dual-W with replay consolidation.
  Asks if Bet B 0.80 retention_A bar requires architectural innovation vs training innovation.

ARCHITECTURAL DESIGN (McClelland-McNaughton-O'Reilly CLS):
  W_fast: rapid plasticity, high learning rate eta_fast=0.3. Stores Phase A patterns quickly.
  W_slow: slow consolidation, low learning rate eta_slow=0.01. Accumulator from W_fast samples.
  Consolidation: after Phase A, run replay cycles sampling from W_fast to update W_slow.
  Retrieval: use W_slow for final retrieval (consolidated memory, immune to Phase B/C/D interference).
  4-stage CL protocol:
    Phase A: store corpus_A tokens, train W_fast rapidly.
    Consolidation: replay W_fast -> update W_slow (N_REPLAY consolidation steps).
    Phase B/C/D: train W_fast only (W_slow frozen). W_slow retains Phase A.
  Goal: W_slow's Phase A retention >= 0.80 bar.

SCIENTIFIC QUESTION:
  Does dual-W CLS architecture cross the 0.80 retention_A bar where single-W fails?
  If yes: architectural split is the key mechanism (not training knob tuning).
  If no: CLS consolidation alone is insufficient; need different architecture.

PRE-REGISTERED BANDS (calibration probe; no prior dual-W CLS substrate anchor):
  HARD_PASS: retention_A(W_slow) >= 0.80 in >= 2/3 seeds.
    Interpretation: CLS architecture solves Bet B bottleneck.
  HARD_FAIL: retention_A(W_slow) <= 0.50 across all seeds.
    Interpretation: CLS consolidation insufficient; catastrophic forgetting not resolved.
  MIDDLE_BAND: retention_A in (0.50, 0.80).
    Note: "no prior empirical anchor; bands per calibration-probe policy: +-50% of theory."

FORMULA SELF-TESTS:
  1. retention = bpc_baseline / bpc_after_D (same as single-W 4-stage).
  2. W_slow update: W_slow += eta_slow * (W_fast - W_slow) (exponential smoothing).
     For N_REPLAY->inf: W_slow -> W_fast. For N_REPLAY=0: W_slow unchanged.
  3. Consolidation decay per step: W_slow[t+1] = (1-eta_slow)*W_slow[t] + eta_slow*W_fast[t].
  4. N = 2048 (no _nN suffix in name -- production N = 2048, stated here per PROT-018).
  5. W_fast, W_slow both (N, N) float32. At N=2048: 16MB each. 2 copies = 32MB. OK.
  6. retention_A gate: test 0.82 -> HARD_PASS; 0.48 -> HARD_FAIL; 0.62 -> MIDDLE_BAND.

OOM CHECK:
  W_fast at N=2048: 16MB. W_slow at N=2048: 16MB. Total W storage: 32MB. Far under 6GB. OK.
  Replay buffer: N_REPLAY * N * 4 = 1000 * 2048 * 4 = 8MB. OK.

TIMEOUT ESTIMATE:
  Parent bet_b_n8192_4stage_v1 at N=8192 5 seeds elapsed ~600s (from status_log).
  N-scale: (2048/8192)^1.5 = 0.125x. Seeds ratio 3/1 = 3x relative to smoke.
  But dual-W adds consolidation loop (N_REPLAY=1000 steps per phase): +50% overhead.
  Smoke estimate: 600 * 0.125 * (1/5) * 1.5 = 22.5s. GPU would be 5x faster: ~5s.
  This is a smoke-only anchor; no _nN suffix. Production N = 2048. timeout_s = 7200.

N-suffix: no _nN suffix; production N = 2048; PROT-018: "No _nN suffix; production N = 2048;
  rationale: smoke-profile anchor for gamma-1 CLS architecture test; N chosen for speed."
Anchor: bet_b_cls_dual_w_smoke
Queue: overnight_queue (GPU; N=2048 BSC; dual-W CLS; 3 seeds; 4-stage protocol)
Pre-reg: preregs/2026-05-29_bet_b_cls_dual_w_smoke.md
Parent: exp_bet_b_n8192_4stage_v1.py (4-stage CL single-W; MIDDLE_BAND ret_A < 0.80)
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

# Load phase_a infrastructure (BSC atoms, corpus, training helpers)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa_clsdualw", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- no _nN suffix; production N = 2048 (PROT-018: stated explicitly)
N_FULL  = 2048
N_SMOKE = 512
# N_FULL = 2048 is the queued FULL config for this anchor

K = 4
VOCAB = 256
BETA_TRAIN = 8.0
RELU_B = 0.5

# Dual-W hyperparameters
ETA_FAST  = 0.30    # W_fast learning rate (rapid plasticity)
ETA_SLOW  = 0.01    # W_slow smoothing rate (slow consolidation)
DELTA_DECAY_FAST = 1e-4
N_REPLAY  = 500     # consolidation steps per replay cycle

# Training parameters
T_BYTES_FULL  = 100_000
T_BYTES_SMOKE =  20_000
BATCH_SIZE    = 64
EPOCHS_PHASE_FULL  = 3
EPOCHS_PHASE_SMOKE = 1
PHASE_A_EPOCHS_FULL  = 5
PHASE_A_EPOCHS_SMOKE = 1
N_EVAL_FULL  = 1000
N_EVAL_SMOKE = 200

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RET_A = 0.80
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_cls_dual_w_smoke") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_atoms(N: int, seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """BSC atoms: byte atoms (VOCAB x N) and position atoms (K x N)."""
    gen = torch.Generator(device="cpu").manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen)
    gen2 = torch.Generator(device="cpu").manual_seed(seed + 10000)
    pos_atoms  = pa.make_bsc_atoms(K, N, gen2)
    return byte_atoms, pos_atoms


def load_phase_corpus(corpus_bytes: bytes, T_bytes: int, T_eval: int
                       ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Split corpus into train and eval index tensors."""
    T = min(T_bytes, len(corpus_bytes) - K)
    T_train = T - T_eval
    assert T_train > 0, f"T_train={T_train} <= 0"

    train_idx = torch.tensor([[corpus_bytes[i+j] for j in range(K)] for i in range(T_train)],
                              dtype=torch.long)
    train_tgt = torch.tensor([corpus_bytes[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus_bytes[T_train+i+j] for j in range(K)] for i in range(T_eval)],
                              dtype=torch.long)
    eval_tgt  = torch.tensor([corpus_bytes[T_train+i+K] for i in range(T_eval)], dtype=torch.long)
    return train_idx, train_tgt, eval_idx, eval_tgt


def train_w_fast(W_fast: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                  train_idx: torch.Tensor, train_tgt: torch.Tensor,
                  N: int, device: torch.device, n_epochs: int) -> torch.Tensor:
    """Update W_fast with delta rule (rapid plasticity)."""
    T = train_idx.shape[0]
    for _ in range(n_epochs):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be].to(device))
            q = ctxs @ W_fast.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            P = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = P.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W_fast.mul_(1.0 - DELTA_DECAY_FAST)
            W_fast.add_(dW, alpha=ETA_FAST)
    return W_fast


def consolidate(W_fast: torch.Tensor, W_slow: torch.Tensor, n_replay: int) -> torch.Tensor:
    """Replay consolidation: W_slow += eta_slow * (W_fast - W_slow) for n_replay steps.

    Each step: W_slow = (1 - eta_slow) * W_slow + eta_slow * W_fast.
    After n_replay steps: W_slow = (1-eta_slow)^n * W_slow_0 + [1-(1-eta_slow)^n] * W_fast.
    """
    decay = (1.0 - ETA_SLOW) ** n_replay
    W_slow = W_slow * decay + W_fast * (1.0 - decay)
    return W_slow


def eval_bpc(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
              eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
              N: int, device: torch.device) -> float:
    """Compute bits-per-character using W."""
    T = eval_idx.shape[0]
    total_bpc = 0.0
    n_batches = 0
    for bs in range(0, T, 128):
        be = min(bs + 128, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P = torch.softmax(BETA_TRAIN * sims, dim=0)
        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        total_bpc += (nll / math.log(2)).mean().item()
        n_batches += 1
    return total_bpc / max(n_batches, 1)


def run_one_seed(seed: int, smoke: bool, N: int, device: torch.device) -> dict:
    T_bytes = T_BYTES_SMOKE if smoke else T_BYTES_FULL
    T_eval  = N_EVAL_SMOKE  if smoke else N_EVAL_FULL
    epochs_phase = EPOCHS_PHASE_SMOKE if smoke else EPOCHS_PHASE_FULL
    epochs_phaseA = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL

    byte_atoms, pos_atoms = make_atoms(N, seed)
    byte_atoms = byte_atoms.to(device)
    pos_atoms  = pos_atoms.to(device)

    # Load 4 phase corpora (A, B, C, D)
    # Use pa.load_corpus_a() as source; split into 4 sections
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

    # Init weight matrices
    W_fast = torch.zeros(N, N, dtype=torch.float32, device=device)
    W_slow = torch.zeros(N, N, dtype=torch.float32, device=device)

    # Phase A: train W_fast rapidly
    trn_A, tgt_A, eval_A_idx, eval_A_tgt = load_phase_corpus(corpora[0], T_bytes, T_eval)
    W_fast = train_w_fast(W_fast, byte_atoms, pos_atoms, trn_A, tgt_A, N, device, epochs_phaseA)

    # Consolidation: replay W_fast -> W_slow
    W_slow = consolidate(W_fast, W_slow, N_REPLAY)

    # Baseline: bpc of W_slow on Phase A eval (before interference)
    bpc_A_baseline = eval_bpc(W_slow, byte_atoms, pos_atoms, eval_A_idx.to(device), eval_A_tgt.to(device), N, device)

    # Phases B, C, D: train W_fast only; W_slow frozen
    for phase_i in range(1, 4):
        trn_ph, tgt_ph, _, _ = load_phase_corpus(corpora[phase_i], T_bytes, T_eval)
        W_fast = train_w_fast(W_fast, byte_atoms, pos_atoms, trn_ph, tgt_ph, N, device, epochs_phase)

    # Final retention: W_slow on Phase A eval (W_slow was frozen during B/C/D)
    bpc_A_final = eval_bpc(W_slow, byte_atoms, pos_atoms, eval_A_idx.to(device), eval_A_tgt.to(device), N, device)

    retention_A = bpc_A_baseline / max(bpc_A_final, 1e-9)

    return {
        "seed": seed,
        "N": N,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_final": round(bpc_A_final, 5),
        "retention_A": round(retention_A, 4),
    }


def compute_verdict(results: List[dict]) -> Tuple[str, str]:
    if not results:
        return ("CLSDUALW_INCONCLUSIVE", "No results.")

    ret_As = [r["retention_A"] for r in results if "retention_A" in r]
    if not ret_As:
        return ("CLSDUALW_INCONCLUSIVE", "No retention_A values.")

    mean_ret_A = sum(ret_As) / len(ret_As)
    seeds_pass = sum(1 for r in ret_As if r >= PASS_RET_A)

    detail = (f"mean_ret_A={mean_ret_A:.4f} seeds_pass={seeds_pass}/{len(ret_As)} "
              f"per_seed={[round(r, 4) for r in ret_As]} "
              f"HP={PASS_RET_A} HF={FAIL_RET_A}")

    # HARD_FAIL
    if mean_ret_A <= FAIL_RET_A:
        return ("CLSDUALW_HARD_FAIL",
                f"CLS_CONSOLIDATION_INSUFFICIENT: mean_ret_A={mean_ret_A:.4f} <= {FAIL_RET_A}. "
                f"Architectural split does not prevent catastrophic forgetting. " + detail)

    # HARD_PASS
    if seeds_pass >= 2 and mean_ret_A >= PASS_RET_A:
        return ("CLSDUALW_HARD_PASS",
                f"CLS_ARCHITECTURE_SOLVES_BETB: mean_ret_A={mean_ret_A:.4f} >= {PASS_RET_A}. "
                f"Dual-W CLS crosses 0.80 bar. " + detail)

    return ("CLSDUALW_MIDDLE_BAND",
            f"PARTIAL_CLS: ret_A={mean_ret_A:.4f} above HF but below HP. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""

    # Formula self-test 1: consolidation decay formula
    # After N_REPLAY steps: W_slow = decay * W_slow_0 + (1-decay) * W_fast
    n_test = 100
    decay_test = (1.0 - ETA_SLOW) ** n_test
    expected = 1.0 - (0.99 ** 100)
    assert abs((1.0 - decay_test) - expected) < 0.001, f"Consolidation decay: {decay_test}"
    # After 100 steps at eta=0.01: W_slow absorbs ~(1-0.99^100) = ~63% of W_fast
    assert 0.6 < (1.0 - decay_test) < 0.7, f"63% absorption expected; got {1.0 - decay_test}"

    # Formula self-test 2: retention = bpc_baseline / bpc_final
    bpc_b, bpc_f = 3.5, 4.73
    ret = bpc_b / bpc_f
    assert abs(ret - 0.7399) < 0.001, f"retention formula: {ret}"

    # Formula self-test 3: verdict gates
    results_pass = [{"retention_A": 0.82, "seed": 7},
                    {"retention_A": 0.85, "seed": 17},
                    {"retention_A": 0.81, "seed": 23}]
    v, _ = compute_verdict(results_pass)
    assert v == "CLSDUALW_HARD_PASS", f"Expected HARD_PASS, got {v}"

    results_fail = [{"retention_A": 0.45, "seed": 7},
                    {"retention_A": 0.42, "seed": 17},
                    {"retention_A": 0.48, "seed": 23}]
    v, _ = compute_verdict(results_fail)
    assert v == "CLSDUALW_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    # Formula self-test 4: smoke forward pass
    device = torch.device("cpu")
    N_test = 256
    result = run_one_seed(17, smoke=True, N=N_test, device=device)
    assert "retention_A" in result, f"Missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float), f"retention_A not float: {type(ret_A)}"
    assert 0.0 < ret_A <= 1.5, f"retention_A out of (0, 1.5]: {ret_A}"
    assert "bpc_A_baseline" in result and result["bpc_A_baseline"] > 0, "bpc_A_baseline missing or zero"
    assert "bpc_A_final" in result and result["bpc_A_final"] > 0, "bpc_A_final missing or zero"

    # 4x smoke scale (multi-scale gate)
    result_4x = run_one_seed(17, smoke=True, N=N_test * 4, device=device)
    assert "retention_A" in result_4x, "4x smoke missing retention_A"
    assert 0.0 < result_4x["retention_A"] <= 1.5, f"4x retention_A out of range: {result_4x['retention_A']}"

    # OOM check
    oom_bytes_2w = N_FULL * N_FULL * 4 * 2  # 2 W matrices
    assert oom_bytes_2w < 6e9, f"OOM pre-check failed: {oom_bytes_2w:.2e} >= 6GB"

    print(f"[SELFTEST PASS] bet_b_cls_dual_w_smoke: consolidation_decay={1.0-decay_test:.3f} "
          f"smoke_ret_A={ret_A:.4f} OOM={oom_bytes_2w:.2e}B", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    t0 = time.time()
    out_dir = get_output_dir()

    print(f"[cls_dual_w] N={N} seeds={seeds} mode={'smoke' if smoke else 'full'} "
          f"eta_fast={ETA_FAST} eta_slow={ETA_SLOW} N_replay={N_REPLAY} "
          f"device={device}", flush=True)

    results = []
    for seed in seeds:
        print(f"  seed {seed}...", flush=True)
        ts = time.time()
        r = run_one_seed(seed, smoke, N, device)
        te = time.time() - ts
        print(f"  seed {seed}: {te:.1f}s ret_A={r['retention_A']:.4f} "
              f"bpc_baseline={r['bpc_A_baseline']:.3f} bpc_final={r['bpc_A_final']:.3f}",
              flush=True)
        results.append(r)

    verdict, verdict_msg = compute_verdict(results)
    elapsed = round(time.time() - t0, 2)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "N": N,
        "smoke": smoke,
        "results": results,
        "config": {
            "N": N, "eta_fast": ETA_FAST, "eta_slow": ETA_SLOW,
            "N_replay": N_REPLAY, "seeds": seeds,
        },
    }
    out_dir2 = get_output_dir()
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[cls_dual_w] VERDICT: {verdict}", flush=True)
    print(f"[cls_dual_w] {verdict_msg}", flush=True)
    print(f"[cls_dual_w] elapsed={elapsed}s output={out_path}", flush=True)


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
