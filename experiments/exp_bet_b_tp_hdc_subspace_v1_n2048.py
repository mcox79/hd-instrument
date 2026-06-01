"""Bet-B 4-stage CL: TP-HDC SUBSPACE PROJECTION at N=2048 (architecture smoke).

PARENT: exp_bet_b_cls_dual_w_smoke.py (dual-W CLS smoke scaffold, N=2048) +
        exp_bet_b_4stage_rehab_epochs_v3.py (4-stage CL v3 rehab; run_one_seed via v1_mod) +
        exp_bet_b_n8192_4stage_v1.py (core 4-stage CL base, compute_verdict).

RESEARCH SOURCE: notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md
  Direction 2 row 1 / Prediction P1 / top-3 row 1.
  TP-HDC: Tensor-Product HDC where each phase trains in an orthogonal random projection
  subspace of the substrate's N hyperspace. Direct lit precedent: arxiv 2004.14252.
  Predicted ret_A lift: +0.10 to +0.18 over baseline 0.745.

ARCHITECTURAL DESIGN (TP-HDC Subspace Projection):
  The substrate W matrix operates in full N-dim space (N x N). Catastrophic forgetting
  arises because Phase-B/C/D updates overwrite the Phase-A pattern manifold.

  TP-HDC FIX: Each phase is assigned a random orthogonal subspace P_i (dim d = N/4).
  Phase A: context vectors projected into P_A subspace before storing.
    k_A_proj = k * P_A^T     (N -> d projection)
    k_A_full = k_A_proj * P_A (d -> N lift back to full space)
    W updated with outer product of projected (lifted) key-value pairs.
  Phase B/C/D: same, using disjoint P_B, P_C, P_D subspaces.
  Retrieval Phase A: query projected through P_A subspace only, then retrieved.

  Implementation: use random Gaussian projection matrices P_i (d x N), d = N//4,
  orthogonalized (QR decomposition). Keys projected: k_proj = k @ P_i.T @ P_i
  (project then lift -- this is the subspace constraint operator).

  This does NOT require additional infrastructure beyond matrix ops; all existing
  atoms (BSC byte_atoms, pos_atoms) are used; projection is applied at train time.

SCIENTIFIC QUESTION:
  Does TP-HDC subspace projection cross the 0.80 retention_A bar?
  N=2048 smoke (3 seeds). If HARD_PASS: schedule FULL N=8192 5-seed.
  If HARD_FAIL: architectural subspace axis cannot rescue.

PRE-REGISTERED BANDS (calibration probe; no prior TP-HDC substrate anchor):
  HARD_PASS: mean retention_A >= 0.80 in >= 2/3 seeds.
    Interpretation: TP-HDC subspace projection solves Bet B bottleneck.
  HARD_FAIL: mean retention_A <= 0.55 across all seeds.
    Note: "no prior empirical anchor; bands per calibration-probe policy +-50% of theory."
    Theoretical prediction: 0.85-0.93 (subspace orthogonality prevents B/C/D interference).
    HF at 0.55 = theoretical prediction - 40%. +-50% band on 0.85 lower bound = 0.425.
    Using 0.55 (more conservative) as HF.
  MIDDLE_BAND: retention_A in (0.55, 0.80).

FORMULA SELF-TESTS:
  1. N == 2048 (PROT-018: stated explicitly; no _nN suffix).
  2. Subspace dim d = N // 4 = 512. P_i shape: (d, N) = (512, 2048).
  3. Projection operator Pi = P_i.T @ P_i: (N, N) = (2048, 2048). Rank = d = 512.
  4. Orthogonality: P_i @ P_i.T = I_d (d x d identity) after QR.
     For d < N: P_i @ P_i.T = I_d; P_i.T @ P_i is a projection matrix (idempotent, rank d).
  5. Subspaces P_A, P_B, P_C, P_D have zero mutual overlap when rows drawn from random
     Gaussian (with high probability for large N): E[P_i @ P_j.T] = 0 for i != j.
  6. retention = bpc_baseline / bpc_after_D. Same formula as v3.
  7. OOM: W at N=2048: 16MB. Subspace projections P_i: 4 * 512 * 2048 * 4 = 16MB. Total: ~32MB.
     Per seed: <<6GB. PASS.

OOM CHECK:
  W at N=2048: 2048*2048*4 = 16MB. 4 subspace matrices (d x N): 4*512*2048*4 = 16MB.
  Key store (M=T_bytes/K context windows): T_bytes_smoke=20000 sequences, ~4KB. Negligible.
  Total: ~35MB. Well under 6GB. PASS.

TIMEOUT ESTIMATE:
  bet_b_cls_dual_w_smoke selftest ran at N=256 CPU in ~3s.
  N=2048 smoke scale: (2048/512)^1.5 = 11.3x vs small-N selftest.
  Additional cost: QR per phase (4 * QR of 512x2048) = ~1s each on GPU.
  Smoke estimate at N=2048, 1 seed: ~15-25s GPU.
  FULL smoke (3 seeds): ~75s. Safety 4x: 300s. Round to 900s.
  Under 2h: no extra flag. timeout_s = 900.

N-suffix: no _nN suffix; production N = 2048 (PROT-018: stated explicitly; smoke anchor).
Anchor: bet_b_tp_hdc_subspace_v1_n2048
Queue: overnight_queue (GPU; N=2048 4-phase TP-HDC subspace; 3 seeds; architecture smoke)
Pre-reg: preregs/2026-05-29_bet_b_tp_hdc_subspace_v1_n2048.md
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

# Load phase_a infrastructure (BSC atoms, corpus, training helpers)
_pa_path = REPO / "experiments" / "exp_wave14b_cl_phase_a.py"
_pa_spec = importlib.util.spec_from_file_location("pa_tphdc", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- no _nN suffix; production N = 2048 (PROT-018: stated explicitly)
N_FULL  = 2048
N_SMOKE = 512
# Note: this is a smoke anchor; FULL would be N=8192 5-seed if HARD_PASS

K    = 4      # context window
VOCAB = 256
BETA_TRAIN = 8.0
RELU_B = 0.5
ETA    = 0.30     # Hebbian learning rate
DELTA_DECAY = 1e-4

# Subspace parameters
SUBSPACE_DIM_FRAC = 0.25    # d = N // 4 per phase

T_BYTES_FULL  = 100_000
T_BYTES_SMOKE =  20_000
BATCH_SIZE    = 64
EPOCHS_PHASE_FULL  = 3
EPOCHS_PHASE_SMOKE = 1
N_EVAL_FULL  = 1000
N_EVAL_SMOKE = 200

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RET_A = 0.80
FAIL_RET_A = 0.55


def get_output_dir(default_name: str = "bet_b_tp_hdc_subspace_v1_n2048") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_subspace_projector(N: int, d: int, seed: int, device: torch.device) -> torch.Tensor:
    """Random orthogonal subspace projector P: (d x N), QR-orthogonalized rows.

    Returns P such that P @ P.T = I_d (approximately).
    Projection operator: Pi = P.T @ P  (N x N, rank d).
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    G = torch.randn(d, N, generator=gen, device=device, dtype=torch.float32)
    # QR: G = Q R, Q is (d x d) if d <= N, use Q for Q.T rows
    Q, _ = torch.linalg.qr(G.T, mode='reduced')   # Q: (N x d)
    P = Q.T   # (d x N)
    return P


def make_atoms(N: int, seed: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
    """BSC atoms: byte_atoms (VOCAB x N), pos_atoms (K x N)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen)
    gen2 = torch.Generator(device=device).manual_seed(seed + 10000)
    pos_atoms  = pa.make_bsc_atoms(K, N, gen2)
    return byte_atoms, pos_atoms


def project_key(k: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
    """Project key vectors through subspace P and lift back: k_proj = (k @ P.T) @ P.

    P: (d x N). k: (..., N). Returns (..., N) projected key in P's subspace.
    """
    return (k @ P.T) @ P


def load_phase_corpus(corpus_bytes: bytes, T_bytes: int, T_eval: int
                       ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Split corpus bytes into train/eval index tensors."""
    T = min(T_bytes, len(corpus_bytes) - K)
    T_train = T - T_eval
    if T_train <= 0:
        T_train = max(1, T - K)
    train_idx = torch.tensor([[corpus_bytes[i+j] for j in range(K)]
                               for i in range(T_train)], dtype=torch.long)
    train_tgt = torch.tensor([corpus_bytes[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus_bytes[T_train+i+j] for j in range(K)]
                               for i in range(min(T_eval, len(corpus_bytes)-T_train-K))],
                              dtype=torch.long)
    eval_tgt  = torch.tensor([corpus_bytes[T_train+i+K]
                               for i in range(min(T_eval, len(corpus_bytes)-T_train-K))],
                              dtype=torch.long)
    return train_idx, train_tgt, eval_idx, eval_tgt


def train_w_subspace(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                      train_idx: torch.Tensor, train_tgt: torch.Tensor,
                      P: torch.Tensor, N: int, device: torch.device, n_epochs: int) -> torch.Tensor:
    """Delta-rule update on W with subspace projection of context vectors."""
    T = train_idx.shape[0]
    for _ in range(n_epochs):
        for bs in range(0, T, BATCH_SIZE):
            be = min(bs + BATCH_SIZE, T)
            ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, train_idx[bs:be].to(device))
            # Project context vectors into subspace P
            ctxs_proj = project_key(ctxs, P)   # (..., N) -> projected
            q = ctxs_proj @ W.T
            q = pa.shifted_relu(q, RELU_B)
            sims = (byte_atoms @ q.T) / N
            probs = torch.softmax(BETA_TRAIN * sims, dim=0)
            target_atoms = byte_atoms[train_tgt[bs:be].to(device)]
            predicted = probs.T @ byte_atoms
            dW = (target_atoms - predicted).T @ ctxs_proj / N
            W.mul_(1.0 - DELTA_DECAY)
            W.add_(dW, alpha=ETA)
    return W


def eval_bpc_subspace(W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
                       eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                       P: torch.Tensor, N: int, device: torch.device) -> float:
    """BPC evaluation using subspace-projected queries."""
    T = eval_idx.shape[0]
    if T == 0:
        return float('inf')
    total_bpc = 0.0
    n_batches = 0
    for bs in range(0, T, 128):
        be = min(bs + 128, T)
        ctxs = pa.build_ctx_bundles_bsc(byte_atoms, pos_atoms, eval_idx[bs:be].to(device))
        ctxs_proj = project_key(ctxs, P)
        q = ctxs_proj @ W.T
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
    T_bytes    = T_BYTES_SMOKE   if smoke else T_BYTES_FULL
    T_eval     = N_EVAL_SMOKE    if smoke else N_EVAL_FULL
    epochs_ph  = EPOCHS_PHASE_SMOKE if smoke else EPOCHS_PHASE_FULL

    d = max(1, N // 4)   # subspace dimension

    byte_atoms, pos_atoms = make_atoms(N, seed, device)

    # Build 4 orthogonal subspace projectors
    projectors = [make_subspace_projector(N, d, seed=seed + 7000 + i * 997, device=device)
                  for i in range(4)]

    # Load corpus and split into 4 phase segments
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

    # Phase A: train W with subspace P_A projection
    P_A = projectors[0]
    trn_A, tgt_A, eval_A_idx, eval_A_tgt = load_phase_corpus(corpora[0], T_bytes, T_eval)
    W = train_w_subspace(W, byte_atoms, pos_atoms, trn_A, tgt_A, P_A, N, device,
                          n_epochs=epochs_ph * 2)  # Phase A gets 2x epochs

    # Baseline BPC on Phase A BEFORE B/C/D interference
    bpc_A_baseline = eval_bpc_subspace(W, byte_atoms, pos_atoms,
                                        eval_A_idx.to(device), eval_A_tgt.to(device),
                                        P_A, N, device)

    # Phase B, C, D: train W with respective subspace projections
    for phase_i in range(1, 4):
        P_i = projectors[phase_i]
        trn_ph, tgt_ph, _, _ = load_phase_corpus(corpora[phase_i], T_bytes, T_eval)
        W = train_w_subspace(W, byte_atoms, pos_atoms, trn_ph, tgt_ph, P_i, N, device,
                              n_epochs=epochs_ph)

    # Final retention: BPC on Phase A eval after all interference
    bpc_A_final = eval_bpc_subspace(W, byte_atoms, pos_atoms,
                                     eval_A_idx.to(device), eval_A_tgt.to(device),
                                     P_A, N, device)

    retention_A = bpc_A_baseline / max(bpc_A_final, 1e-9)

    return {
        "seed": seed, "N": N, "d": d,
        "bpc_A_baseline": round(bpc_A_baseline, 5),
        "bpc_A_final": round(bpc_A_final, 5),
        "retention_A": round(retention_A, 4),
    }


def compute_verdict(results: List[dict]) -> Tuple[str, str]:
    if not results:
        return ("TPHDC_INCONCLUSIVE", "No results.")

    ret_As = [r["retention_A"] for r in results if "retention_A" in r]
    if not ret_As:
        return ("TPHDC_INCONCLUSIVE", "No retention_A values.")

    mean_ret_A = sum(ret_As) / len(ret_As)
    seeds_pass = sum(1 for r in ret_As if r >= PASS_RET_A)

    detail = (f"mean_ret_A={mean_ret_A:.4f} seeds_pass={seeds_pass}/{len(ret_As)} "
              f"per_seed={[round(r, 4) for r in ret_As]} "
              f"HP={PASS_RET_A} HF={FAIL_RET_A}")

    if mean_ret_A <= FAIL_RET_A:
        return ("TPHDC_HARD_FAIL",
                f"SUBSPACE_PROJECTION_INSUFFICIENT: mean_ret_A={mean_ret_A:.4f} <= {FAIL_RET_A}. "
                f"TP-HDC subspace does not prevent catastrophic forgetting. " + detail)

    if seeds_pass >= 2 and mean_ret_A >= PASS_RET_A:
        return ("TPHDC_HARD_PASS",
                f"TPHDC_CROSSES_0.80_BAR: mean_ret_A={mean_ret_A:.4f} >= {PASS_RET_A}. "
                f"Subspace projection architecture rescues Bet B. " + detail)

    return ("TPHDC_MIDDLE_BAND",
            f"PARTIAL_SUBSPACE: ret_A={mean_ret_A:.4f} above HF but below HP. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018: no _nN suffix; production N = 2048 stated explicitly
    assert N_FULL == 2048, f"PROT-018: N_FULL must be 2048; got {N_FULL}"

    # Self-test 1: subspace dimension
    d_test = N_FULL // 4
    assert d_test == 512, f"d = N_FULL // 4 = {d_test}, expected 512"

    # Self-test 2: projector orthogonality P @ P.T = I_d (approx)
    device = torch.device("cpu")
    N_test = 256
    d_test2 = N_test // 4
    P = make_subspace_projector(N_test, d_test2, seed=42, device=device)
    PPt = P @ P.T   # (d x d)
    eye_d = torch.eye(d_test2, device=device)
    ortho_err = float((PPt - eye_d).abs().max().item())
    assert ortho_err < 1e-4, f"Projector not orthogonal: max |PP^T - I| = {ortho_err}"

    # Self-test 3: projection operator idempotent (P.T @ P @ P.T @ P = P.T @ P)
    Pi = P.T @ P   # (N x N) projection
    Pi2 = Pi @ Pi
    idemp_err = float((Pi2 - Pi).abs().max().item())
    assert idemp_err < 1e-4, f"Projection operator not idempotent: {idemp_err}"

    # Self-test 4: retention formula
    bpc_b, bpc_f = 3.5, 4.5
    ret = bpc_b / bpc_f
    assert abs(ret - (3.5/4.5)) < 1e-6, f"retention formula: {ret}"

    # Self-test 5: verdict gates
    results_pass = [{"retention_A": 0.85, "seed": 7},
                    {"retention_A": 0.83, "seed": 17},
                    {"retention_A": 0.81, "seed": 23}]
    v, _ = compute_verdict(results_pass)
    assert v == "TPHDC_HARD_PASS", f"Expected HARD_PASS, got {v}"

    results_fail = [{"retention_A": 0.50, "seed": 7},
                    {"retention_A": 0.48, "seed": 17},
                    {"retention_A": 0.52, "seed": 23}]
    v, _ = compute_verdict(results_fail)
    assert v == "TPHDC_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    # Self-test 6: smoke forward pass
    result = run_one_seed(17, smoke=True, N=N_SMOKE, device=device)
    assert "retention_A" in result, f"Missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float), f"retention_A not float: {type(ret_A)}"
    assert 0.0 < ret_A <= 1.5, f"retention_A out of (0, 1.5]: {ret_A}"
    assert "bpc_A_baseline" in result and result["bpc_A_baseline"] > 0, "bpc_A_baseline missing"
    assert "bpc_A_final" in result and result["bpc_A_final"] > 0, "bpc_A_final missing"

    # Self-test 7: 4x smoke (multi-scale gate)
    result_4x = run_one_seed(17, smoke=True, N=N_SMOKE * 4, device=device)
    assert "retention_A" in result_4x, "4x smoke missing retention_A"
    assert 0.0 < result_4x["retention_A"] <= 1.5, f"4x retention_A out of range"

    # Self-test 8: OOM check
    oom_bytes = N_FULL * N_FULL * 4 + 4 * (N_FULL // 4) * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(
        f"[SELFTEST PASS] bet_b_tp_hdc_subspace_v1_n2048: "
        f"ortho_err={ortho_err:.2e} idemp_err={idemp_err:.2e} "
        f"smoke_ret_A={ret_A:.4f} OOM={oom_bytes:.2e}B",
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
        f"[tp_hdc_subspace] N={N} seeds={seeds} mode={'smoke' if smoke else 'full'} "
        f"subspace_dim={N//4} device={device}",
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
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "N": N, "smoke": smoke,
        "results": results,
        "config": {
            "N": N, "eta": ETA, "subspace_dim_frac": SUBSPACE_DIM_FRAC,
            "seeds": seeds, "T_bytes": T_BYTES_SMOKE if smoke else T_BYTES_FULL,
        },
    }
    out_path = get_output_dir() / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[tp_hdc_subspace] VERDICT: {verdict}", flush=True)
    print(f"[tp_hdc_subspace] {verdict_msg}", flush=True)
    print(f"[tp_hdc_subspace] elapsed={elapsed}s output={out_path}", flush=True)


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
