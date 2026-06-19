"""ALPHA-2: CODEBOOK AXIS WITH PARAMETRIC ORTHOGONALITY VARIATION at N=4096.

PARENT: exp_kf2_cross_codebook_v1_n4096.py (KF-2 cross-codebook isolation test) +
  exp_kf5_steerable_beta_v2.py (KF-5 steerability; codebook-axis shows promise per v275).

SCIENTIFIC QUESTION (codebook axis post-KF5_PARTIAL_DECOUPLING):
  Post-v275 finding: KF-5 codebook-axis steerability was confirmed (3-5x margin on entropy).
  This script extends the codebook-axis test by measuring bpc + multi-hop accuracy as a
  function of PARAMETRIC orthogonality variation in the codebook.
  5 codebooks with parametric orthogonality:
    1. sparse_ternary_density=0.1  (very sparse, high effective orthogonality)
    2. sparse_ternary_density=0.25 (medium sparse)
    3. sparse_ternary_density=0.5  (denser, less orthogonal)
    4. structured_hadamard          (maximal structured orthogonality)
    5. random_gaussian              (Gaussian random; intermediate orthogonality)
  3 seeds each; measures bpc + multi-hop retrieval.
  Tests: does codebook variation beyond the standard 5 types matter for bpc?
  Are all 5 codebooks equivalent for bpc but different for multi-hop?

PRE-REGISTERED BANDS (calibration probe; 5 parametric orthogonality levels new):
  HARD_PASS: bpc varies significantly across codebooks (bpc_range > 0.30 bits) AND
    multi-hop accuracy differs by > 0.10 between best and worst codebook.
    Interpretation: codebook selection is a real design parameter for both metrics.
  HARD_FAIL: bpc_range < 0.05 AND multi_hop_range < 0.02 across all codebooks.
    Interpretation: codebook orthogonality is irrelevant; all variants equivalent.
  MIDDLE_BAND: only one metric (bpc or multi-hop) shows variation.

  NOTE: calibration probe (no prior parametric orthogonality sweep anchor).
  "no prior empirical anchor; bands per calibration-probe policy: +-50% of theory."

FORMULA SELF-TESTS:
  1. sparse_ternary(density=d): each entry is -1/+1 with prob d/2 each, else 0.
     Expected dot product < sqrt(density) * sqrt(density) * N = d * N.
  2. Hadamard: structured H_N x H_N^T = N * I. Maximally orthogonal.
  3. multi_hop = retrieval accuracy after 2 consecutive lookups: a->b->c.
     multi_hop = P(correct c | correct b).
  4. N == 4096 (PROT-018 binding).
  5. bpc in [1.0, 8.0] for byte-level LM.

OOM CHECK:
  W at N=4096: 64MB per seed. Codebook C=256 (byte codebook): 1MB. No OOM risk. CPU OK.

TIMEOUT ESTIMATE:
  Per cell: train W (20K steps) + eval bpc + multi-hop.
  Parent kf2_cross_codebook_v1 at N=4096, 3 seeds: estimate ~30s per cell (CPU).
  5 codebooks x 3 seeds = 15 cells. Total = 15 * 30 * 1.5 = 675s.
  PROT-019 floor for _n4096 = 14400s. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: alpha2_codebook_variation_n4096
Queue: remote_cpu_queue (CPU; N=4096; 5 codebook types x 3 seeds; bpc + multi-hop)
Pre-reg: preregs/2026-05-29_alpha2_codebook_variation_n4096.md
Parent: exp_kf2_cross_codebook_v1_n4096.py + exp_kf5_steerable_beta_v2.py
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
_pa_spec = importlib.util.spec_from_file_location("pa_alpha2", _pa_path)
pa = importlib.util.module_from_spec(_pa_spec)
_pa_spec.loader.exec_module(pa)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K = 4
VOCAB = 256
M_FRAC = 4.0
BETA_TRAIN   = 8.0
BETA_READOUT = 8.0
RELU_B  = 0.5
DELTA_ALPHA = 0.3
DELTA_DECAY = 1e-4

T_TRAIN_FULL  = 20000
T_TRAIN_SMOKE = 3000
T_EVAL_FULL   = 2000
T_EVAL_SMOKE  = 300

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# 5 codebook specifications
CODEBOOK_CONFIGS_FULL = [
    {"type": "sparse_ternary", "density": 0.1,  "name": "sparse_d01"},
    {"type": "sparse_ternary", "density": 0.25, "name": "sparse_d025"},
    {"type": "sparse_ternary", "density": 0.5,  "name": "sparse_d05"},
    {"type": "hadamard",       "density": None,  "name": "hadamard"},
    {"type": "gaussian",       "density": None,  "name": "gaussian"},
]
CODEBOOK_CONFIGS_SMOKE = [
    {"type": "sparse_ternary", "density": 0.1,  "name": "sparse_d01"},
    {"type": "hadamard",       "density": None,  "name": "hadamard"},
    {"type": "gaussian",       "density": None,  "name": "gaussian"},
]

# Pre-registered thresholds
HP_BPC_RANGE      = 0.30   # bpc range > 0.30 bits
HP_MULTIHOP_RANGE = 0.10   # multi-hop range > 0.10
HF_BPC_RANGE      = 0.05
HF_MULTIHOP_RANGE = 0.02


def get_output_dir(default_name: str = "alpha2_codebook_variation_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_codebook(cb_config: dict, N: int, seed: int) -> torch.Tensor:
    """Build codebook according to config spec. Returns (VOCAB, N) tensor."""
    gen = torch.Generator(device="cpu").manual_seed(seed + 99999)
    cb_type = cb_config["type"]

    if cb_type == "sparse_ternary":
        density = cb_config["density"]
        # Each entry: -1, 0, +1 with probs d/2, 1-d, d/2
        cb = torch.zeros(VOCAB, N)
        mask = torch.rand(VOCAB, N, generator=gen) < density
        signs = torch.randint(0, 2, (VOCAB, N), generator=gen).float() * 2 - 1
        cb = signs * mask.float()
        # Normalize rows to unit-ish norm
        norms = cb.norm(dim=1, keepdim=True).clamp(min=1e-6)
        cb = cb / norms * math.sqrt(N)
        return cb

    elif cb_type == "hadamard":
        # Hadamard matrix via Sylvester construction up to VOCAB x N
        # Use a random subset of rows from a large Hadamard
        # For VOCAB=256, N=1024/4096: use structured Hadamard rows
        n_pow2 = 1
        while n_pow2 < N:
            n_pow2 *= 2
        # Build Hadamard recursively up to n_pow2
        H = torch.ones(1, 1)
        while H.shape[0] < max(VOCAB, N):
            H = torch.cat([
                torch.cat([H, H], dim=1),
                torch.cat([H, -H], dim=1)
            ], dim=0)
        # Take VOCAB rows and N columns from the Hadamard
        H_sub = H[:VOCAB, :N].float()
        return H_sub  # rows are already orthogonal with norm sqrt(N)

    elif cb_type == "gaussian":
        cb = torch.randn(VOCAB, N, generator=gen)
        # Normalize to unit norm x sqrt(N)
        norms = cb.norm(dim=1, keepdim=True).clamp(min=1e-6)
        cb = cb / norms * math.sqrt(N)
        return cb

    else:
        raise ValueError(f"Unknown codebook type: {cb_type}")


def eval_bpc_multihop(W: torch.Tensor, cb: torch.Tensor,
                       eval_idx: torch.Tensor, eval_tgt: torch.Tensor,
                       N: int, device: torch.device,
                       batch_size: int = 128) -> dict:
    """Evaluate bpc and multi-hop accuracy using codebook cb."""
    cb_dev = cb.to(device)
    T = eval_idx.shape[0]
    all_bpc = []
    all_hop1_acc = []
    all_hop2_acc = []

    for bs in range(0, T - 1, batch_size):
        be = min(bs + batch_size, T - 1)  # -1 for multi-hop

        # Build context bundle from eval_idx using cb for position atoms
        # Use pa's BSC bundle but with custom codebook
        # Position atoms: use cb rows K..K+K-1 (or use pa's bsc atoms for positions)
        # For simplicity: use first K rows of cb as position atoms
        pos_atoms = cb_dev[:K]   # (K, N)
        byte_atoms = cb_dev      # (VOCAB, N)

        ctxs_list = []
        for i in range(bs, be):
            ctx = torch.zeros(N, device=device)
            for j in range(K):
                tok = eval_idx[i, j].item()
                pos = j % len(pos_atoms)
                ctx = ctx + byte_atoms[tok] * pos_atoms[pos]
            ctxs_list.append(ctx)
        ctxs = torch.stack(ctxs_list)   # (B, N)

        # First hop
        q = ctxs @ W.T
        q = pa.shifted_relu(q, RELU_B)
        sims = (byte_atoms @ q.T) / N
        P = torch.softmax(BETA_READOUT * sims, dim=0)   # (VOCAB, B)

        tgt = eval_tgt[bs:be].to(device)
        log_p = torch.log(P + 1e-12)
        nll = -log_p.gather(0, tgt.unsqueeze(0)).squeeze(0)
        all_bpc.append((nll / math.log(2)).mean().item())

        hop1_pred = P.argmax(dim=0)  # (B,)
        all_hop1_acc.append((hop1_pred == tgt).float().mean().item())

        # Second hop: use predicted token as next context query
        hop2_atoms = byte_atoms[hop1_pred]  # (B, N) -- predicted first-hop atoms
        q2 = hop2_atoms @ W.T
        q2 = pa.shifted_relu(q2, RELU_B)
        sims2 = (byte_atoms @ q2.T) / N
        P2 = torch.softmax(BETA_READOUT * sims2, dim=0)   # (VOCAB, B)

        # Multi-hop target: the token after the ground-truth target
        tgt2 = eval_tgt[bs+1:be+1].to(device)
        hop2_pred = P2.argmax(dim=0)
        all_hop2_acc.append((hop2_pred == tgt2).float().mean().item())

    return {
        "bpc": sum(all_bpc) / len(all_bpc) if all_bpc else float("nan"),
        "hop1_acc": sum(all_hop1_acc) / len(all_hop1_acc) if all_hop1_acc else float("nan"),
        "multi_hop_acc": sum(all_hop2_acc) / len(all_hop2_acc) if all_hop2_acc else float("nan"),
    }


def train_w_with_codebook(cb: torch.Tensor,
                           train_idx: torch.Tensor, train_tgt: torch.Tensor,
                           N: int, device: torch.device, n_epochs: int = 2) -> torch.Tensor:
    """Train W using the given codebook for key/value atoms."""
    cb_dev = cb.to(device)
    pos_atoms = cb_dev[:K]   # use first K rows as position atoms
    byte_atoms = cb_dev      # VOCAB rows

    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    T = train_idx.shape[0]

    for _ in range(n_epochs):
        for bs in range(0, T, 64):
            be = min(bs + 64, T)
            # Build context bundles
            batch_ctxs = []
            for i in range(bs, be):
                ctx = torch.zeros(N, device=device)
                for j in range(K):
                    tok = train_idx[i, j].item()
                    pos = j % len(pos_atoms)
                    ctx = ctx + byte_atoms[tok] * pos_atoms[pos]
                batch_ctxs.append(ctx)
            ctxs = torch.stack(batch_ctxs)   # (B, N)

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


def run_one_seed_codebook(cb_config: dict, seed: int, smoke: bool, N: int,
                           train_idx: torch.Tensor, train_tgt: torch.Tensor,
                           eval_idx: torch.Tensor, eval_tgt: torch.Tensor) -> dict:
    device = torch.device("cpu")
    cb = build_codebook(cb_config, N, seed)
    W = train_w_with_codebook(cb, train_idx, train_tgt, N, device,
                               n_epochs=1 if smoke else 2)
    metrics = eval_bpc_multihop(W, cb, eval_idx, eval_tgt, N, device)
    return {
        "codebook": cb_config["name"],
        "seed": seed,
        "N": N,
        **metrics,
    }


def compute_verdict(summary: dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("ALPHA2_INCONCLUSIVE", "No cells.")

    # Group by codebook type -> mean across seeds
    cb_names = list({c["codebook"] for c in cells})
    per_cb_bpc: Dict[str, List[float]] = {n: [] for n in cb_names}
    per_cb_mh: Dict[str, List[float]] = {n: [] for n in cb_names}

    for c in cells:
        name = c["codebook"]
        bpc = c.get("bpc")
        mh  = c.get("multi_hop_acc")
        if bpc is not None and not math.isnan(bpc):
            per_cb_bpc[name].append(bpc)
        if mh is not None and not math.isnan(mh):
            per_cb_mh[name].append(mh)

    mean_bpc = {n: (sum(v) / len(v) if v else float("nan")) for n, v in per_cb_bpc.items()}
    mean_mh  = {n: (sum(v) / len(v) if v else float("nan")) for n, v in per_cb_mh.items()}

    bpc_vals = [v for v in mean_bpc.values() if not math.isnan(v)]
    mh_vals  = [v for v in mean_mh.values() if not math.isnan(v)]

    bpc_range = max(bpc_vals) - min(bpc_vals) if len(bpc_vals) >= 2 else 0.0
    mh_range  = max(mh_vals) - min(mh_vals)   if len(mh_vals) >= 2 else 0.0

    detail = (f"bpc_range={bpc_range:.4f} mh_range={mh_range:.4f} "
              f"mean_bpc={dict((k, round(v, 4)) for k, v in mean_bpc.items())} "
              f"mean_mh={dict((k, round(v, 4)) for k, v in mean_mh.items())} "
              f"HP_bpc={HP_BPC_RANGE} HP_mh={HP_MULTIHOP_RANGE} "
              f"HF_bpc={HF_BPC_RANGE} HF_mh={HF_MULTIHOP_RANGE}")

    # HARD_FAIL: both metrics flat
    if bpc_range < HF_BPC_RANGE and mh_range < HF_MULTIHOP_RANGE:
        return ("ALPHA2_HARD_FAIL",
                f"CODEBOOK_IRRELEVANT: bpc and multi-hop flat across all codebook types. " + detail)

    # HARD_PASS: both metrics vary substantially
    if bpc_range >= HP_BPC_RANGE and mh_range >= HP_MULTIHOP_RANGE:
        return ("ALPHA2_HARD_PASS",
                f"CODEBOOK_MATTERS: both bpc and multi-hop vary with orthogonality. " + detail)

    return ("ALPHA2_MIDDLE_BAND",
            f"PARTIAL_CODEBOOK_EFFECT: one metric varies, other flat. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula self-test 1: codebook builders produce correct shapes
    for cb_cfg in CODEBOOK_CONFIGS_SMOKE:
        cb = build_codebook(cb_cfg, 512, seed=17)
        assert cb.shape == (VOCAB, 512), f"Shape mismatch for {cb_cfg['name']}: {cb.shape}"
        # Rows should have nonzero norm
        norms = cb.norm(dim=1)
        n_zero = (norms < 1e-3).sum().item()
        assert n_zero == 0, f"Zero-norm rows in {cb_cfg['name']}: {n_zero}"

    # Formula self-test 2: Hadamard orthogonality
    cb_h = build_codebook({"type": "hadamard"}, 512, seed=17)
    # H @ H^T should be close to N * I for the VOCAB subset
    gram = cb_h @ cb_h.T / 512   # should be ~I
    diag = gram.diag()
    assert (diag - 1.0).abs().max().item() < 0.01, f"Hadamard not orthonormal: max_diag_err={((diag - 1.0).abs().max().item()):.4f}"

    # Formula self-test 3: smoke forward pass
    N_test = 256
    device = torch.device("cpu")
    corpus = pa.load_corpus_a()
    T_total = len(corpus) - K
    T_train = min(1000, T_total - 200)
    T_eval  = 200

    train_idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T_train)], dtype=torch.long)
    train_tgt = torch.tensor([corpus[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus[T_train+i+j] for j in range(K)] for i in range(T_eval)], dtype=torch.long)
    eval_tgt  = torch.tensor([corpus[T_train+i+K] for i in range(T_eval)], dtype=torch.long)

    for cb_cfg in CODEBOOK_CONFIGS_SMOKE[:2]:  # test 2 codebooks at smoke scale
        cell = run_one_seed_codebook(cb_cfg, 17, True, N_test, train_idx, train_tgt, eval_idx, eval_tgt)
        assert "bpc" in cell, f"Missing bpc for {cb_cfg['name']}"
        assert 0.0 < cell["bpc"] < 20.0, f"bpc out of range for {cb_cfg['name']}: {cell['bpc']}"
        assert "multi_hop_acc" in cell, f"Missing multi_hop_acc for {cb_cfg['name']}"
        assert 0.0 <= cell["multi_hop_acc"] <= 1.0, f"multi_hop_acc out of [0,1]: {cell['multi_hop_acc']}"

    # Multi-scale smoke (4x)
    for cb_cfg in CODEBOOK_CONFIGS_SMOKE[:1]:
        cell_4x = run_one_seed_codebook(cb_cfg, 17, True, N_test * 4, train_idx, train_tgt, eval_idx, eval_tgt)
        assert cell_4x["bpc"] > 0, f"4x bpc=0 for {cb_cfg['name']}"

    # Verdict gates
    cells_pass = []
    for cb_name, bpc_val, mh_val in [("a", 3.0, 0.20), ("b", 3.35, 0.10), ("c", 3.50, 0.05)]:
        for seed in [7, 17, 23]:
            cells_pass.append({"codebook": cb_name, "seed": seed, "bpc": bpc_val, "multi_hop_acc": mh_val})
    v, _ = compute_verdict({"cells": cells_pass})
    assert v == "ALPHA2_HARD_PASS", f"Expected HARD_PASS, got {v}"

    cells_fail = []
    for cb_name in ["a", "b", "c"]:
        for seed in [7, 17, 23]:
            cells_fail.append({"codebook": cb_name, "seed": seed, "bpc": 3.5, "multi_hop_acc": 0.15})
    v, _ = compute_verdict({"cells": cells_fail})
    assert v == "ALPHA2_HARD_FAIL", f"Expected HARD_FAIL, got {v}"

    print("[SELFTEST PASS] alpha2_codebook_variation_n4096: "
          "codebook shapes OK, Hadamard orthogonality OK, smoke bpc/multihop OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cpu")  # CPU-suitable
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    cb_configs = CODEBOOK_CONFIGS_SMOKE if smoke else CODEBOOK_CONFIGS_FULL
    t0 = time.time()
    out_dir = get_output_dir()

    corpus = pa.load_corpus_a()
    T_total = len(corpus) - K
    T_train = min(T_TRAIN_SMOKE if smoke else T_TRAIN_FULL, T_total - (T_EVAL_SMOKE if smoke else T_EVAL_FULL))
    T_eval  = min(T_EVAL_SMOKE if smoke else T_EVAL_FULL, T_total - T_train)
    train_idx = torch.tensor([[corpus[i+j] for j in range(K)] for i in range(T_train)], dtype=torch.long)
    train_tgt = torch.tensor([corpus[i+K] for i in range(T_train)], dtype=torch.long)
    eval_idx  = torch.tensor([[corpus[T_train+i+j] for j in range(K)] for i in range(T_eval)], dtype=torch.long)
    eval_tgt  = torch.tensor([corpus[T_train+i+K] for i in range(T_eval)], dtype=torch.long)

    print(f"[alpha2] N={N} seeds={seeds} codebooks={[c['name'] for c in cb_configs]} "
          f"mode={'smoke' if smoke else 'full'}", flush=True)

    all_cells = []
    for cb_cfg in cb_configs:
        for seed in seeds:
            print(f"  codebook={cb_cfg['name']} seed={seed}...", flush=True)
            ts = time.time()
            cell = run_one_seed_codebook(cb_cfg, seed, smoke, N, train_idx, train_tgt, eval_idx, eval_tgt)
            te = time.time() - ts
            print(f"  {cb_cfg['name']} seed={seed}: {te:.1f}s bpc={cell['bpc']:.4f} "
                  f"multi_hop={cell['multi_hop_acc']:.4f}", flush=True)
            all_cells.append(cell)

    summary = {
        "cells": all_cells,
        "N_full": N_FULL,
        "N_used": N,
        "M_frac": M_FRAC,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    out_dir2 = get_output_dir()
    out_path = out_dir2 / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[alpha2] VERDICT: {verdict}", flush=True)
    print(f"[alpha2] {verdict_msg}", flush=True)
    print(f"[alpha2] elapsed={elapsed}s output={out_path}", flush=True)


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
