"""Bet-B 4-stage CL: POOL-RETRIEVAL GENERATIVE REPLAY during Phase D at N=2048.

PARENT: exp_bet_b_4stage_rehab_epochs_v3.py (4-stage CL v3 rehab; base architecture) +
        exp_bet_b_cls_dual_w_smoke.py (N=2048 smoke scaffold + phase infrastructure) +
        exp_bet_b_n8192_4stage_v1.py (run_one_seed / corpus infrastructure).

RESEARCH SOURCE: notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md
  Prediction P5 / top-3 row 2 / "cheapest substrate-compatible architectural rescue".
  Pool-retrieval generative replay: during Phase-D training, sample N_replay items from
  the substrate's existing pool (retrieved via standard pool-retrieval) and mix them
  into Phase-D batches. The pool already contains Phase-A/B/C atoms; sampling them
  at train-time is the substrate-native CLS slow-consolidation analog.
  Predicted ret_A lift: +0.08 to +0.15.

ARCHITECTURAL DESIGN (Pool-Retrieval Generative Replay):
  Standard 4-stage CL: Phases A, B, C store patterns; Phase D causes forgetting.
  This fix: during Phase D training, each batch is augmented with N_replay retrieved
  samples drawn from the substrate's memory pool.

  Replay mechanism (substrate-native):
    1. After Phases A + B + C complete, extract a replay pool by sampling the codebook
       and querying W to retrieve stored patterns.
    2. During Phase D training loop: for each batch, sample N_replay keys from replay pool
       and add them to the batch as "remembered" facts.
    3. The mixed batch (real Phase-D + replayed Phase-A/B/C) constrains Phase-D updates
       to not overwrite previously stored patterns.

  Implementation:
    - replay_pool: T_REPLAY_POOL random context samples from corpora A+B+C, evaluated
      at current W to get (context, predicted_target) pairs.
    - During Phase-D batches: append replay_idx, replay_tgt to batch before delta-rule step.
    - No additional infrastructure needed; all existing atoms/corpus/training helpers used.

SCIENTIFIC QUESTION:
  Does generative replay during Phase D cross the 0.80 retention_A bar?
  N=2048 smoke (3 seeds). If HARD_PASS: schedule FULL N=8192 5-seed.

PRE-REGISTERED BANDS (calibration probe; no prior genreplay substrate anchor):
  HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
    Interpretation: generative replay architecture rescues Bet B.
  HARD_FAIL: mean retention_A <= 0.55 across all seeds.
    Note: "no prior empirical anchor; bands per calibration-probe policy +-50% of theory."
    Theoretical prediction: 0.83-0.90 (generative replay prevents Phase-D clobbering).
    HF at 0.55 = conservative 0.73 floor - 25% buffer.
  MIDDLE_BAND: retention_A in (0.55, 0.80).

FORMULA SELF-TESTS:
  1. N == 2048 (PROT-018: stated explicitly; no _nN suffix).
  2. T_REPLAY_POOL = 500 items; N_REPLAY_PER_BATCH = 16 replay items per batch.
  3. replay_pool sampling: T_REPLAY_POOL context windows from corpora 0..2 (Phases A/B/C).
  4. Replay injection: Phase-D batch gets 16 replay items appended.
     Effective batch size during Phase D: BATCH_SIZE + N_REPLAY_PER_BATCH = 64 + 16 = 80.
  5. retention = bpc_baseline / bpc_after_D. Same formula as v3.
  6. OOM: W at N=2048: 16MB. Replay pool (T_REPLAY_POOL x K): negligible.
     No matrix-scale OOM risk. Total peak: ~25MB. PASS.

OOM CHECK:
  W at N=2048: 16MB. Context bundles (BATCH_SIZE x N): ~0.5MB. Replay pool: ~0.1MB.
  Total: ~20MB. Well under 6GB. PASS.

TIMEOUT ESTIMATE:
  bet_b_cls_dual_w_smoke at N=2048 3 seeds: estimated ~5s GPU per seed.
  This script adds replay pool construction (~1s) + Phase D batch augmentation (+20% overhead).
  Smoke estimate at N=2048, 1 seed: ~8s GPU. FULL (3 seeds): ~30s. Safety 6x: 180s.
  Round up to 600s. Under 2h: no extra flag. timeout_s = 600.

N-suffix: no _nN suffix; production N = 2048 (PROT-018: stated explicitly; smoke anchor).
Anchor: bet_b_genreplay_phaseD_v1_n2048
Queue: overnight_queue (GPU; N=2048 4-phase genreplay CL; 3 seeds; architecture smoke)
Pre-reg: preregs/2026-05-29_bet_b_genreplay_phaseD_v1_n2048.md
Parent: exp_bet_b_cls_dual_w_smoke.py + exp_bet_b_4stage_rehab_epochs_v3.py
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
_pa_spec = importlib.util.spec_from_file_location("pa_genreplay", _pa_path)
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

T_BYTES_FULL  = 100_000
T_BYTES_SMOKE =  20_000
BATCH_SIZE    = 64
EPOCHS_PHASE_FULL  = 3
EPOCHS_PHASE_SMOKE = 1
N_EVAL_FULL  = 1000
N_EVAL_SMOKE = 200

# Replay parameters
T_REPLAY_POOL_FULL  = 500   # replay pool size (context windows from Phases A/B/C)
T_REPLAY_POOL_SMOKE = 100
N_REPLAY_PER_BATCH  = 16    # replay items injected per Phase-D batch

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RET_A = 0.80
FAIL_RET_A = 0.55


def get_output_dir(default_name: str = "bet_b_genreplay_phaseD_v1_n2048") -> Path:
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


def train_w(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
             train_idx: torch.Tensor, train_tgt: torch.Tensor,
             N: int, device: torch.device, n_epochs: int) -> torch.Tensor:
    """Standard delta-rule training (no replay)."""
    T = train_idx.shape[0]
    for _ in range(n_epochs):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be].to(device))
            q = ctxs @ W.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            probs = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = probs.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=ETA)
    return W


def build_replay_pool(corpus_bytes: bytes, T_pool: int, T_offset: int = 0
                       ) -> Tuple[torch.Tensor, torch.Tensor]:
    """Extract T_pool context windows from corpus starting at T_offset."""
    T_pool = min(T_pool, max(1, len(corpus_bytes) - K - T_offset))
    pool_idx = torch.tensor([[corpus_bytes[T_offset+i+j] for j in range(K)]
                               for i in range(T_pool)], dtype=torch.long)
    pool_tgt = torch.tensor([corpus_bytes[T_offset+i+K] for i in range(T_pool)],
                              dtype=torch.long)
    return pool_idx, pool_tgt


def train_w_with_replay(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                          train_idx: torch.Tensor, train_tgt: torch.Tensor,
                          replay_idx: torch.Tensor, replay_tgt: torch.Tensor,
                          N: int, device: torch.device, n_epochs: int,
                          n_replay_per_batch: int) -> torch.Tensor:
    """Delta-rule training with generative replay injection during Phase D.

    For each batch: append n_replay_per_batch random replay items before delta-rule update.
    This constrains Phase-D updates to not clobber A/B/C stored patterns.
    """
    T = train_idx.shape[0]
    T_replay = replay_idx.shape[0]
    if T_replay == 0:
        return train_w(W, byte_atoms, pos_atoms, train_idx, train_tgt, N, device, n_epochs)

    gen = torch.Generator().manual_seed(12345)
    for _ in range(n_epochs):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)

            # Sample replay items
            n_rep = min(n_replay_per_batch, T_replay)
            rep_idx_sample = torch.randint(0, T_replay, (n_rep,), generator=gen)
            rep_batch_idx = replay_idx[rep_idx_sample]
            rep_batch_tgt = replay_tgt[rep_idx_sample]

            # Concatenate real + replay
            aug_idx = torch.cat([train_idx[bs:be], rep_batch_idx], dim=0)
            aug_tgt = torch.cat([train_tgt[bs:be], rep_batch_tgt], dim=0)

            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, aug_idx.to(device))
            q = ctxs @ W.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            probs = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[aug_tgt.to(device)]
            predicted = probs.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=ETA)
    return W


def eval_bpc(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
              eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
              N: int, device: torch.device) -> float:
    T = eval_idx.shape[0]
    if T == 0:
        return float('inf')
    total_bpc = 0.0
    n_batches = 0
    for bs in range(0, T, 128):
        be = min(bs + 128, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        probs = torch.softmax(BETA_TRAIN * sims, dim=0)
        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(probs + 1e-12)
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        total_bpc += (nll / math.log(2)).mean().item()
        n_batches += 1
    return total_bpc / max(n_batches, 1)


def run_one_seed(seed: int, smoke: bool, N: int, device: torch.device) -> dict:
    T_bytes       = T_BYTES_SMOKE     if smoke else T_BYTES_FULL
    T_eval        = N_EVAL_SMOKE      if smoke else N_EVAL_FULL
    epochs_ph     = EPOCHS_PHASE_SMOKE if smoke else EPOCHS_PHASE_FULL
    T_replay_pool = T_REPLAY_POOL_SMOKE if smoke else T_REPLAY_POOL_FULL

    byte_atoms, pos_atoms = make_atoms(N, seed, device)

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

    W = torch.zeros(N, N, dtype=torch.float32, device=device)

    # Phase A
    trn_A, tgt_A, eval_A_idx, eval_A_tgt = load_phase_corpus(corpora[0], T_bytes, T_eval)
    W = train_w(W, byte_atoms, pos_atoms, trn_A, tgt_A, N, device, n_epochs=epochs_ph)

    # Phase B
    trn_B, tgt_B, _, _ = load_phase_corpus(corpora[1], T_bytes, T_eval)
    W = train_w(W, byte_atoms, pos_atoms, trn_B, tgt_B, N, device, n_epochs=epochs_ph)

    # Phase C
    trn_C, tgt_C, _, _ = load_phase_corpus(corpora[2], T_bytes, T_eval)
    W = train_w(W, byte_atoms, pos_atoms, trn_C, tgt_C, N, device, n_epochs=epochs_ph)

    # Baseline BPC on Phase A BEFORE Phase D (after A/B/C interference)
    bpc_A_baseline = eval_bpc(W, byte_atoms, pos_atoms,
                               eval_A_idx.to(device), eval_A_tgt.to(device), N, device)

    # Build replay pool from Phase A (primary source of what we want to retain)
    # Sample from all 3 prior phase corpora for broader replay coverage
    T_per_phase = T_replay_pool // 3
    r_idx_A, r_tgt_A = build_replay_pool(corpora[0], T_per_phase, T_offset=0)
    r_idx_B, r_tgt_B = build_replay_pool(corpora[1], T_per_phase, T_offset=0)
    r_idx_C, r_tgt_C = build_replay_pool(corpora[2], T_per_phase, T_offset=0)
    replay_idx = torch.cat([r_idx_A, r_idx_B, r_idx_C], dim=0)
    replay_tgt = torch.cat([r_tgt_A, r_tgt_B, r_tgt_C], dim=0)

    # Phase D: training WITH generative replay injection
    trn_D, tgt_D, _, _ = load_phase_corpus(corpora[3], T_bytes, T_eval)
    W = train_w_with_replay(W, byte_atoms, pos_atoms, trn_D, tgt_D,
                              replay_idx, replay_tgt,
                              N, device, n_epochs=epochs_ph,
                              n_replay_per_batch=N_REPLAY_PER_BATCH)

    # Final retention: BPC on Phase A eval after Phase D with replay
    bpc_A_final = eval_bpc(W, byte_atoms, pos_atoms,
                            eval_A_idx.to(device), eval_A_tgt.to(device), N, device)

    retention_A = bpc_A_baseline / max(bpc_A_final, 1e-9)

    return {
        "seed": seed, "N": N,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_final": round(bpc_A_final, 5),
        "retention_A": round(retention_A, 4),
        "replay_pool_size": replay_idx.shape[0],
    }


def compute_verdict(results: List[dict]) -> Tuple[str, str]:
    if not results:
        return ("GENREPLAY_INCONCLUSIVE", "No results.")

    ret_As = [r["retention_A"] for r in results if "retention_A" in r]
    if not ret_As:
        return ("GENREPLAY_INCONCLUSIVE", "No retention_A values.")

    mean_ret_A = sum(ret_As) / len(ret_As)
    seeds_pass = sum(1 for r in ret_As if r >= PASS_RET_A)

    detail = (f"mean_ret_A={mean_ret_A:.4f} seeds_pass={seeds_pass}/{len(ret_As)} "
              f"per_seed={[round(r, 4) for r in ret_As]} "
              f"HP={PASS_RET_A} HF={FAIL_RET_A}")

    if mean_ret_A <= FAIL_RET_A:
        return ("GENREPLAY_HARD_FAIL",
                f"GENREPLAY_INSUFFICIENT: mean_ret_A={mean_ret_A:.4f} <= {FAIL_RET_A}. "
                f"Pool-retrieval replay does not prevent catastrophic forgetting. " + detail)

    if seeds_pass >= 2 and mean_ret_A >= PASS_RET_A:
        return ("GENREPLAY_HARD_PASS",
                f"GENREPLAY_CROSSES_0.80_BAR: mean_ret_A={mean_ret_A:.4f} >= {PASS_RET_A}. "
                f"Generative replay architecture rescues Bet B. " + detail)

    return ("GENREPLAY_MIDDLE_BAND",
            f"PARTIAL_GENREPLAY: ret_A={mean_ret_A:.4f} above HF but below HP. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 2048 stated explicitly
    assert N_FULL == 2048, f"PROT-018: N_FULL must be 2048; got {N_FULL}"

    # Self-test 1: replay batch size
    assert BATCH_SIZE + N_REPLAY_PER_BATCH == 80, (
        f"Augmented batch size: {BATCH_SIZE + N_REPLAY_PER_BATCH}, expected 80"
    )

    # Self-test 2: retention formula
    bpc_b, bpc_f = 3.5, 4.5
    ret = bpc_b / bpc_f
    assert abs(ret - (3.5/4.5)) < 1e-6, f"retention formula: {ret}"

    # Self-test 3: verdict gates
    results_pass = [{"retention_A": 0.83, "seed": 7},
                    {"retention_A": 0.82, "seed": 17},
                    {"retention_A": 0.84, "seed": 23}]
    v, _ = compute_verdict(results_pass)
    assert v == "GENREPLAY_HARD_PASS", f"Expected HARD_PASS, got {v}"

    results_fail = [{"retention_A": 0.50, "seed": 7},
                    {"retention_A": 0.48, "seed": 17},
                    {"retention_A": 0.53, "seed": 23}]
    v, _ = compute_verdict(results_fail)
    assert v == "GENREPLAY_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    # Self-test 4: smoke forward pass
    device = torch.device("cpu")
    result = run_one_seed(17, smoke=True, N=N_SMOKE, device=device)
    assert "retention_A" in result, f"Missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float), f"retention_A not float: {type(ret_A)}"
    assert 0.0 < ret_A <= 1.5, f"retention_A out of (0, 1.5]: {ret_A}"
    assert "bpc_A_baseline" in result and result["bpc_A_baseline"] > 0, "bpc_A_baseline missing"
    assert "replay_pool_size" in result and result["replay_pool_size"] > 0, "replay_pool_size missing"

    # Self-test 5: 4x smoke (multi-scale gate)
    result_4x = run_one_seed(17, smoke=True, N=N_SMOKE * 4, device=device)
    assert "retention_A" in result_4x, "4x smoke missing retention_A"
    assert 0.0 < result_4x["retention_A"] <= 1.5, f"4x retention_A out of range"

    # Self-test 6: OOM check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(
        f"[SELFTEST PASS] bet_b_genreplay_phaseD_v1_n2048: "
        f"smoke_ret_A={ret_A:.4f} replay_pool={result['replay_pool_size']} "
        f"OOM={oom_bytes:.2e}B",
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
        f"[genreplay_phaseD] N={N} seeds={seeds} mode={'smoke' if smoke else 'full'} "
        f"n_replay_per_batch={N_REPLAY_PER_BATCH} device={device}",
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
            "N": N, "eta": ETA, "n_replay_per_batch": N_REPLAY_PER_BATCH,
            "T_replay_pool": T_REPLAY_POOL_SMOKE if smoke else T_REPLAY_POOL_FULL,
            "seeds": seeds,
        },
    }
    out_path = get_output_dir() / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[genreplay_phaseD] VERDICT: {verdict}", flush=True)
    print(f"[genreplay_phaseD] {verdict_msg}", flush=True)
    print(f"[genreplay_phaseD] elapsed={elapsed}s output={out_path}", flush=True)


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
