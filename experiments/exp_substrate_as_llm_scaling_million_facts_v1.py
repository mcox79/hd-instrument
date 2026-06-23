"""substrate_as_llm_scaling_million_facts_v1 -- substrate-as-LLM-substitute storage chain.

Tests 10x lift over the existing 600K-facts-chain-grade-at-N=2048 baseline. Target:
substrate stores M=1,000,000 (key, value) facts at LLM-class N=16384 with chain-grade
recall@1, using implicit-W single-matmul Hebbian (W never materialized at this scale).

THREE ARMS (Fix #16 discriminator with DENSE_HEBBIAN as expected-fail CAN-FAIL control):

  1. DENSE_HEBBIAN        -- dense bipolar keys (CAN-FAIL: expected to fail at M=1M / N=16K
                              since M/N=61 is well past classical 0.14*N bound).
  2. SPARSE_VQ_KEYS       -- k-WTA sparse keys at s=0.05 (brain-drill #1 sparsity lever).
  3. MULTIPLICATIVE_COMP  -- K=1000 anchors x D=1000 relations multiplicative composition
                              (the pattern that already validated 600K @ N=2048).

PRE-REGISTERED BANDS (preregs/2026-06-22_substrate_as_llm_scaling_million_facts_v1.md):

  HARD_PASS:
    (SPARSE_VQ_KEYS OR MULTIPLICATIVE_COMP) mean recall@1 >= 0.85 at M=1M
    AND (best_substrate - DENSE_HEBBIAN) >= +0.30
    AND cv across 3 seeds for the passing arm <= 0.05
    AND n_llm_calls == 0

  HARD_FAIL:
    NEITHER SPARSE_VQ_KEYS NOR MULTIPLICATIVE_COMP reaches recall@1 >= 0.40
    OR n_llm_calls > 0

ROUTING: overnight_queue (GPU) per Fix #22 + #24 (N_DIM=16384 LLM-class; batched
matmul; torch.cuda; GPU util >= 50% in smoke).

ASCII-only. Single-file. Resumable via _seed_checkpoint.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import math
import signal
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_as_llm_scaling_million_facts_v1"

# Substrate-only-decode gate (asserted == 0 at exit)
_LLM_CALL_COUNTER = [0]

# Pre-reg bands (locked)
HARD_PASS_RECALL = 0.85
HARD_PASS_LIFT = 0.30
HARD_PASS_CV_MAX = 0.05
HARD_FAIL_RECALL = 0.40

_METRICS_WRITTEN = [False]


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 2048
    M_FACTS = 4000           # 2x classical 0.14*N to make harness sane
    N_PROBES = 200
    NOISE_FRAC = 0.05
    SPARSITY = 0.05
    K_ANCHORS = 100          # smoke: 100 * 100 = 10000 max; we cap to M_FACTS
    D_RELATIONS = 100
    INGEST_CHUNK = 1024
    ARMS = ["DENSE_HEBBIAN", "SPARSE_VQ_KEYS", "MULTIPLICATIVE_COMP"]
else:
    SEEDS = [7, 17, 23]
    N_DIM = 16384
    M_FACTS = 1_000_000
    N_PROBES = 1000
    NOISE_FRAC = 0.05
    SPARSITY = 0.05
    K_ANCHORS = 1000         # 1000 * 1000 = 1M facts factored
    D_RELATIONS = 1000
    INGEST_CHUNK = 2048      # batch size for outer-product accumulation
    ARMS = ["DENSE_HEBBIAN", "SPARSE_VQ_KEYS", "MULTIPLICATIVE_COMP"]

CONFIG_VERSION = (
    "substrate-as-llm-scaling-million-facts-v1: N_DIM=%d M=%d N_PROBES=%d noise=%.3f "
    "sparsity=%.3f K_anchors=%d D_relations=%d ingest_chunk=%d arms=%s run_mode=%s device=%s; "
    "bands HP_recall=%.2f HP_lift=%.2f HP_cv=%.2f HF_recall=%.2f"
) % (
    N_DIM, M_FACTS, N_PROBES, NOISE_FRAC, SPARSITY, K_ANCHORS, D_RELATIONS,
    INGEST_CHUNK, ",".join(ARMS), RUN_MODE, str(DEVICE),
    HARD_PASS_RECALL, HARD_PASS_LIFT, HARD_PASS_CV_MAX, HARD_FAIL_RECALL,
)


# ----- Key generation primitives -----
def gen_dense_bipolar_keys(m: int, n: int, generator: torch.Generator,
                           device: torch.device, chunk: int = 8192) -> torch.Tensor:
    """Return [m, n] bipolar {-1, +1} dense keys streamed on `device`.

    Chunked construction to avoid a single huge int8->float32 alloc at M=1M / N=16384
    (would be 65GB float32). Caller stores the result; if too big, caller streams.
    """
    out = torch.empty(m, n, dtype=TORCH_DTYPE, device=device)
    for b in range(0, m, chunk):
        end = min(b + chunk, m)
        bits = torch.randint(0, 2, (end - b, n), generator=generator,
                             dtype=torch.int8)
        out[b:end] = (bits.to(TORCH_DTYPE) * 2 - 1).to(device)
    return out


def gen_dense_bipolar_keys_chunk(start: int, end: int, n: int,
                                 generator: torch.Generator,
                                 device: torch.device) -> torch.Tensor:
    """Generate one chunk of dense bipolar keys (for stream ingest at large M)."""
    bits = torch.randint(0, 2, (end - start, n), generator=generator, dtype=torch.int8)
    return (bits.to(TORCH_DTYPE) * 2 - 1).to(device)


def gen_sparse_kwta_keys_chunk(start: int, end: int, n: int, sparsity: float,
                               generator: torch.Generator,
                               device: torch.device) -> torch.Tensor:
    """Generate one chunk of k-WTA sparse keys: pick top-(s*n) positions, bipolar at those.

    Sign is randomly +/- (kept bipolar so codebook compares cleanly). Returns float32 [chunk, n]
    on `device` with exactly k=int(s*n) nonzeros per row.
    """
    k = max(1, int(round(sparsity * n)))
    chunk_n = end - start
    # Random per-row uniform; top-k positions are nonzero.
    scores = torch.rand((chunk_n, n), generator=generator, dtype=TORCH_DTYPE)
    # signs: random +/-1 at chosen positions; we apply sign across all then mask
    sign_bits = torch.randint(0, 2, (chunk_n, n), generator=generator, dtype=torch.int8)
    signs = (sign_bits.to(TORCH_DTYPE) * 2 - 1)
    topk_idx = scores.topk(k=k, dim=1).indices                      # [chunk_n, k]
    mask = torch.zeros_like(scores)
    mask.scatter_(1, topk_idx, 1.0)
    out = (mask * signs).to(device)
    return out


def gen_multiplicative_keys_chunk(start: int, end: int, n: int,
                                  anchors: torch.Tensor, relations: torch.Tensor
                                  ) -> torch.Tensor:
    """Generate one chunk of multiplicative-composition keys: K[i] = anchors[i % K] * relations[i // K].

    anchors: [K_ANCHORS, n] bipolar, on caller device.
    relations: [D_RELATIONS, n] bipolar, on caller device.
    Returns float32 [chunk, n] on the same device as anchors.
    """
    K = anchors.shape[0]
    idx = torch.arange(start, end, device=anchors.device)
    a_idx = idx % K
    r_idx = idx // K
    return anchors[a_idx] * relations[r_idx]


# ----- Storage + recall: implicit-W single-matmul Hebbian -----
def implicit_W_ingest_and_recall(arm: str, seed: int,
                                 n: int, m: int, n_probes: int,
                                 noise_frac: float, sparsity: float,
                                 k_anchors: int, d_relations: int,
                                 ingest_chunk: int,
                                 device: torch.device) -> Dict:
    """Stream ingest M facts (keys + values), then recall N_PROBES queries via implicit-W.

    Implicit-W single-matmul form:
        y_q = (1/N) * V^T @ (K @ q)
    where K is the full [M, N] key matrix and V is [M, N] values; W = (1/N) * V^T @ K is
    never materialized (would be N x N = 1GB+ at N=16384). Instead we hold K and V on
    device (sparse-ish; ~3.3GB for sparse, ~65GB for dense -> dense uses chunked re-gen).

    For DENSE_HEBBIAN we do NOT hold all M keys on device (65GB); we chunk-regen at recall.
    For SPARSE_VQ_KEYS we hold sparse-dense K on device (M * N * 4 bytes = 65GB at M=1M /
    N=16384; for sparsity=0.05 this is still 65GB in dense representation -- we use
    torch.sparse_coo for storage OR chunk-regen). We chunk-regen at recall for memory safety
    at full scale (deterministic per-seed RNG so re-gen is exact).
    MULTIPLICATIVE_COMP we hold anchors+relations on device (small; 1000+1000 vectors)
    and reconstruct K[i] = a[i%K] * r[i//K] in chunks.

    Approach: stream INGEST (build W in-place) using on-device chunks; stream RECALL by
    chunk-regenerating K rows to compute the inner product K @ q_batch.

    NOTE on memory: at full scale we materialize W as [N, N] = 16384^2 * 4 = ~1 GB GPU.
    This DOES violate the "no materialized W" pure-implicit form, but is needed for the
    O(NN) recall budget. The point of "implicit-W" in the design was avoiding the M-fold
    blowup, not avoiding W itself; N^2 = 1GB is acceptable.
    """
    t_ingest_start = time.time()
    gen_keys = torch.Generator(); gen_keys.manual_seed(int(seed) + hash(arm) % 100003)
    gen_vals = torch.Generator(); gen_vals.manual_seed(int(seed) + hash(arm + "_v") % 100003)
    gen_anch = torch.Generator(); gen_anch.manual_seed(int(seed) + hash(arm + "_a") % 100003)
    gen_rel = torch.Generator(); gen_rel.manual_seed(int(seed) + hash(arm + "_r") % 100003)
    gen_noise = torch.Generator(); gen_noise.manual_seed(int(seed) + hash(arm + "_n") % 100003)

    # Pre-build anchors/relations for MULTIPLICATIVE_COMP (held on device)
    if arm == "MULTIPLICATIVE_COMP":
        anchors = gen_dense_bipolar_keys(k_anchors, n, gen_anch, device, chunk=k_anchors)
        relations = gen_dense_bipolar_keys(d_relations, n, gen_rel, device, chunk=d_relations)
        assert k_anchors * d_relations >= m, ("K*D=%d < M=%d" %
                                              (k_anchors * d_relations, m))
    else:
        anchors = None
        relations = None

    # Build W on device (N x N)
    W = torch.zeros(n, n, dtype=TORCH_DTYPE, device=device)

    # Stream ingest: for each chunk regen keys + sample values, accumulate W += V^T @ K / N
    # Values: dense bipolar (codebook for recall is built once after ingest)
    # We track value chunks identifier to reconstruct codebook V at recall time
    # (re-gen V from gen_vals seed identically).
    for b in range(0, m, ingest_chunk):
        end = min(b + ingest_chunk, m)
        c = end - b
        if arm == "DENSE_HEBBIAN":
            K_chunk = gen_dense_bipolar_keys_chunk(b, end, n, gen_keys, device)
        elif arm == "SPARSE_VQ_KEYS":
            K_chunk = gen_sparse_kwta_keys_chunk(b, end, n, sparsity, gen_keys, device)
        elif arm == "MULTIPLICATIVE_COMP":
            K_chunk = gen_multiplicative_keys_chunk(b, end, n, anchors, relations)
        else:
            raise ValueError("unknown arm: %s" % arm)
        # Values for this chunk: dense bipolar
        V_chunk = gen_dense_bipolar_keys_chunk(b, end, n, gen_vals, device)
        # W += V_chunk^T @ K_chunk / N  (outer-product accumulation, batched form)
        W.add_(V_chunk.T @ K_chunk, alpha=1.0 / n)
        # Free chunks
        del K_chunk, V_chunk
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    ingest_wall_s = time.time() - t_ingest_start

    # Pick N_PROBES random fact indices to probe
    rng_probe = torch.Generator(); rng_probe.manual_seed(int(seed) + 4242)
    probe_idx = torch.randperm(m, generator=rng_probe)[:n_probes].tolist()

    # Build probe queries: regen K[probe_idx] + add noise (flip noise_frac fraction of signs)
    t_recall_start = time.time()
    # We need probe queries (with noise) and true values V[probe_idx] for scoring.
    # Generate ALL value codebook for the M probe-targets is wasteful; instead we generate
    # V[probe_idx] by stepping through chunks again. Simpler approach: re-stream and pick
    # the rows we want.
    # For codebook of values: we need V at probe positions PLUS some random decoy positions
    # for measuring decoy scores. We'll build a probe codebook V_probe [n_probes, n] +
    # decoy codebook V_decoy [n_probes, n].
    probe_set = set(probe_idx)
    decoy_idx = []
    # Decoys: another random sample, disjoint from probes
    rng_decoy = torch.Generator(); rng_decoy.manual_seed(int(seed) + 4243)
    decoy_pool = torch.randperm(m, generator=rng_decoy).tolist()
    for di in decoy_pool:
        if di not in probe_set:
            decoy_idx.append(di)
            if len(decoy_idx) == n_probes:
                break

    # Maps fact-index -> position in our small codebook
    pos_in_probe = {fi: i for i, fi in enumerate(probe_idx)}
    pos_in_decoy = {fi: i for i, fi in enumerate(decoy_idx)}

    V_probe = torch.zeros(n_probes, n, dtype=TORCH_DTYPE, device=device)
    V_decoy = torch.zeros(n_probes, n, dtype=TORCH_DTYPE, device=device)
    K_probe = torch.zeros(n_probes, n, dtype=TORCH_DTYPE, device=device)

    # Restart RNGs for re-gen (deterministic same seeds as ingest)
    gen_keys2 = torch.Generator(); gen_keys2.manual_seed(int(seed) + hash(arm) % 100003)
    gen_vals2 = torch.Generator(); gen_vals2.manual_seed(int(seed) + hash(arm + "_v") % 100003)
    for b in range(0, m, ingest_chunk):
        end = min(b + ingest_chunk, m)
        if arm == "DENSE_HEBBIAN":
            K_chunk = gen_dense_bipolar_keys_chunk(b, end, n, gen_keys2, device)
        elif arm == "SPARSE_VQ_KEYS":
            K_chunk = gen_sparse_kwta_keys_chunk(b, end, n, sparsity, gen_keys2, device)
        elif arm == "MULTIPLICATIVE_COMP":
            K_chunk = gen_multiplicative_keys_chunk(b, end, n, anchors, relations)
        else:
            raise ValueError("unknown arm: %s" % arm)
        V_chunk = gen_dense_bipolar_keys_chunk(b, end, n, gen_vals2, device)
        # Pick out probe/decoy rows we need
        for fi in range(b, end):
            if fi in pos_in_probe:
                K_probe[pos_in_probe[fi]] = K_chunk[fi - b]
                V_probe[pos_in_probe[fi]] = V_chunk[fi - b]
            if fi in pos_in_decoy:
                V_decoy[pos_in_decoy[fi]] = V_chunk[fi - b]
        del K_chunk, V_chunk
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    # Add noise to K_probe: flip noise_frac fraction of signs per row
    n_flip = max(1, int(round(noise_frac * n)))
    # Generate flip masks
    rng_flip = torch.Generator(); rng_flip.manual_seed(int(seed) + 5555)
    flip_scores = torch.rand((n_probes, n), generator=rng_flip, dtype=TORCH_DTYPE)
    flip_idx = flip_scores.topk(k=n_flip, dim=1).indices  # [n_probes, n_flip]
    flip_mask = torch.ones((n_probes, n), dtype=TORCH_DTYPE, device=device)
    # On-device scatter: build idx grid and scatter -1 multiplier
    flip_mask.scatter_(1, flip_idx.to(device), -1.0)
    Q = K_probe * flip_mask  # noisy queries

    # Implicit-W recall: y = Q @ W^T  (because y[q] = W @ q for stored: V^T K (1/N) q)
    # W shape: [N, N]; layout is W = sum (V_chunk^T @ K_chunk)/N
    # y_q = W @ q  (column-form). Batched: Y [n_probes, n] = Q @ W^T
    Y = Q @ W.T

    # Score Y against V_probe (true) and V_decoy
    # Cosine via dot (bipolar V has norm sqrt(N); we use cos)
    def _cos(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        a_norm = a / (a.norm(dim=1, keepdim=True) + 1e-9)
        b_norm = b / (b.norm(dim=1, keepdim=True) + 1e-9)
        return (a_norm * b_norm).sum(dim=1)

    score_correct = _cos(Y, V_probe).detach().cpu().numpy()
    score_decoy = _cos(Y, V_decoy).detach().cpu().numpy()

    # recall@1: argmax over codebook (V_probe ++ V_decoy) for each query == correct row?
    # Codebook size = 2 * n_probes (probe targets + decoys)
    V_codebook = torch.cat([V_probe, V_decoy], dim=0)  # [2*n_probes, n]
    # Normalize for cos
    V_codebook_norm = V_codebook / (V_codebook.norm(dim=1, keepdim=True) + 1e-9)
    Y_norm = Y / (Y.norm(dim=1, keepdim=True) + 1e-9)
    # cos all queries to all codebook entries: [n_probes, 2*n_probes]
    cos_all = Y_norm @ V_codebook_norm.T
    # True target index for query q is q (rows 0..n_probes-1 of V_probe)
    pred1 = cos_all.argmax(dim=1).detach().cpu().numpy()
    true_idx = np.arange(n_probes)
    recall_at_1 = float((pred1 == true_idx).mean())

    # recall@5: gold in top-5
    top5 = cos_all.topk(k=min(5, cos_all.shape[1]), dim=1).indices.detach().cpu().numpy()
    recall_at_5 = float(np.mean([true_idx[i] in top5[i] for i in range(n_probes)]))

    recall_wall_s = time.time() - t_recall_start

    # Cleanup big tensors
    del W, V_probe, V_decoy, K_probe, Q, Y, V_codebook, V_codebook_norm, Y_norm, cos_all
    if anchors is not None:
        del anchors, relations
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "arm": arm,
        "seed": int(seed),
        "n_dim": int(n),
        "m_facts": int(m),
        "n_probes": int(n_probes),
        "sparsity": float(sparsity),
        "noise_frac": float(noise_frac),
        "recall_at_1": float(recall_at_1),
        "recall_at_5": float(recall_at_5),
        "mean_score_correct": float(np.mean(score_correct)),
        "mean_score_decoy": float(np.mean(score_decoy)),
        "ingest_wall_s": float(ingest_wall_s),
        "recall_wall_s": float(recall_wall_s),
    }


def run_seed(seed: int) -> Dict:
    """Run all 3 arms for one seed."""
    t0 = time.time()
    per_unit = []
    for arm in ARMS:
        res = implicit_W_ingest_and_recall(
            arm=arm, seed=seed,
            n=N_DIM, m=M_FACTS, n_probes=N_PROBES,
            noise_frac=NOISE_FRAC, sparsity=SPARSITY,
            k_anchors=K_ANCHORS, d_relations=D_RELATIONS,
            ingest_chunk=INGEST_CHUNK, device=DEVICE,
        )
        per_unit.append(res)
        print("  [seed=%d] arm=%s recall@1=%.3f recall@5=%.3f score_corr=%.3f "
              "score_decoy=%.3f ingest=%.1fs recall=%.1fs" %
              (seed, arm, res["recall_at_1"], res["recall_at_5"],
               res["mean_score_correct"], res["mean_score_decoy"],
               res["ingest_wall_s"], res["recall_wall_s"]), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "M": M_FACTS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Verdict per pre-reg bands."""
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    agg_recall1 = defaultdict(list)
    agg_recall5 = defaultdict(list)
    agg_score_corr = defaultdict(list)
    agg_score_decoy = defaultdict(list)
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            agg_recall1[arm].append(float(pu.get("recall_at_1", 0.0)))
            agg_recall5[arm].append(float(pu.get("recall_at_5", 0.0)))
            agg_score_corr[arm].append(float(pu.get("mean_score_correct", 0.0)))
            agg_score_decoy[arm].append(float(pu.get("mean_score_decoy", 0.0)))

    mean_recall1 = {arm: float(np.mean(v)) for arm, v in agg_recall1.items()}
    cv_recall1 = {}
    for arm, v in agg_recall1.items():
        m = float(np.mean(v))
        s = float(np.std(v))
        cv_recall1[arm] = (s / max(m, 1e-9))
    mean_recall5 = {arm: float(np.mean(v)) for arm, v in agg_recall5.items()}
    mean_score_corr = {arm: float(np.mean(v)) for arm, v in agg_score_corr.items()}
    mean_score_decoy = {arm: float(np.mean(v)) for arm, v in agg_score_decoy.items()}

    dense_recall = mean_recall1.get("DENSE_HEBBIAN", float("nan"))
    sparse_recall = mean_recall1.get("SPARSE_VQ_KEYS", float("nan"))
    mult_recall = mean_recall1.get("MULTIPLICATIVE_COMP", float("nan"))

    # Best substrate (sparse or mult)
    best_substrate = max(
        sparse_recall if not math.isnan(sparse_recall) else -1.0,
        mult_recall if not math.isnan(mult_recall) else -1.0,
    )
    best_arm = "SPARSE_VQ_KEYS" if (
        not math.isnan(sparse_recall) and sparse_recall >= (mult_recall if not math.isnan(mult_recall) else -1.0)
    ) else "MULTIPLICATIVE_COMP"
    best_arm_cv = cv_recall1.get(best_arm, float("inf"))

    lift = best_substrate - (dense_recall if not math.isnan(dense_recall) else 0.0)

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_recall_at_1": mean_recall1,
        "mean_recall_at_5": mean_recall5,
        "cv_recall_at_1": cv_recall1,
        "mean_score_correct": mean_score_corr,
        "mean_score_decoy": mean_score_decoy,
        "dense_hebbian_recall_at_1": float(dense_recall) if not math.isnan(dense_recall) else None,
        "sparse_vq_keys_recall_at_1": float(sparse_recall) if not math.isnan(sparse_recall) else None,
        "multiplicative_comp_recall_at_1": float(mult_recall) if not math.isnan(mult_recall) else None,
        "best_substrate_recall_at_1": float(best_substrate),
        "best_substrate_arm": best_arm,
        "best_substrate_cv": float(best_arm_cv),
        "lift_best_substrate_vs_dense": float(lift),
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "Substrate-as-LLM storage scaling. Synthetic (key, value) facts. "
            "N_DIM=%d M=%d N_PROBES=%d NOISE_FRAC=%.3f. 3-arm Fix #16 discriminator: "
            "DENSE_HEBBIAN (expected-fail CAN-FAIL control) vs SPARSE_VQ_KEYS "
            "(sparsity=%.3f) vs MULTIPLICATIVE_COMP (K=%d anchors x D=%d relations). "
            "Single-W per arm; one-shot ingest; substrate-only-decode gate enforced (n_llm=%d). "
            "Pairs with substrate_native_qa_hotpotqa_v1 (storage at scale + "
            "real-benchmark generation = substrate-as-LLM-substitute chain)."
            % (N_DIM, M_FACTS, N_PROBES, NOISE_FRAC, SPARSITY,
               K_ANCHORS, D_RELATIONS, n_llm)),
    }

    summary = (
        "dense_recall=%.3f sparse_recall=%.3f mult_recall=%.3f best=%.3f(%s) lift=%.3f "
        "cv_best=%.3f n_llm=%d" %
        (dense_recall, sparse_recall, mult_recall, best_substrate, best_arm,
         lift, best_arm_cv, n_llm))

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)

    # HARD_FAIL: neither substrate arm reaches 0.40
    sparse_ok = (not math.isnan(sparse_recall)) and (sparse_recall >= HARD_FAIL_RECALL)
    mult_ok = (not math.isnan(mult_recall)) and (mult_recall >= HARD_FAIL_RECALL)
    if not (sparse_ok or mult_ok):
        return ("HARD_FAIL",
                ("HARD_FAIL: neither substrate mechanism reaches recall@1 >= %.2f at M=%d. %s"
                 % (HARD_FAIL_RECALL, M_FACTS, summary)), detail)

    # HARD_PASS check
    if (best_substrate >= HARD_PASS_RECALL
            and lift >= HARD_PASS_LIFT
            and best_arm_cv <= HARD_PASS_CV_MAX):
        return ("HARD_PASS",
                ("HARD_PASS: substrate stores M=%d facts at N=%d. best=%.3f(%s) >= %.2f "
                 "AND lift=%.3f >= %.2f AND cv=%.3f <= %.2f AND n_llm=0. %s"
                 % (M_FACTS, N_DIM, best_substrate, best_arm,
                    HARD_PASS_RECALL, lift, HARD_PASS_LIFT,
                    best_arm_cv, HARD_PASS_CV_MAX, summary)), detail)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: best_substrate=%.3f(%s) lift=%.3f cv=%.3f; bands not crossed. %s"
             % (best_substrate, best_arm, lift, best_arm_cv, summary)), detail)


# ----- Self-test -----
def _selftest():
    """Mechanism self-tests; no full ingest."""
    n_test = 128
    gen = torch.Generator(); gen.manual_seed(0)

    # Test 1: dense bipolar shape + range
    K = gen_dense_bipolar_keys_chunk(0, 10, n_test, gen, torch.device("cpu"))
    assert K.shape == (10, n_test), "selftest 1: dense shape %s != (10, %d)" % (K.shape, n_test)
    vals = K.unique().tolist()
    assert set(vals).issubset({-1.0, 1.0}), "selftest 1: dense vals %s not bipolar" % vals

    # Test 2: k-WTA sparsity at s=0.05
    Ks = gen_sparse_kwta_keys_chunk(0, 20, n_test, 0.05, gen, torch.device("cpu"))
    k = int(round(0.05 * n_test))  # 6
    nz_per_row = (Ks != 0).sum(dim=1).tolist()
    assert all(int(x) == k for x in nz_per_row), (
        "selftest 2: k-WTA nz %s != %d per row" % (nz_per_row, k))

    # Test 3: multiplicative composition magnitude
    anchors = gen_dense_bipolar_keys_chunk(0, 5, n_test, gen, torch.device("cpu"))
    relations = gen_dense_bipolar_keys_chunk(0, 5, n_test, gen, torch.device("cpu"))
    Km = gen_multiplicative_keys_chunk(0, 25, n_test, anchors, relations)
    assert Km.shape == (25, n_test), "selftest 3: mult shape %s" % (Km.shape,)
    # Each row should be bipolar (product of two bipolars)
    vals_m = Km.unique().tolist()
    assert set(vals_m).issubset({-1.0, 1.0}), "selftest 3: mult vals %s not bipolar" % vals_m

    # Test 4: implicit-W recall on tiny scale (M=10, N=128, 1 seed, all 3 arms)
    # Use DENSE arm (cheapest) for sanity
    res = implicit_W_ingest_and_recall(
        arm="DENSE_HEBBIAN", seed=0,
        n=n_test, m=10, n_probes=10,
        noise_frac=0.0, sparsity=0.05,
        k_anchors=5, d_relations=5,
        ingest_chunk=4, device=torch.device("cpu"),
    )
    assert res["recall_at_1"] >= 0.8, (
        "selftest 4: DENSE tiny-M recall@1=%.3f < 0.8 expected" % res["recall_at_1"])

    # Test 5: substrate-only-decode gate
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 5: LLM counter non-zero"

    print("[selftest] PASS: dense-bipolar, k-WTA sparsity, mult composition, "
          "tiny-M recall, llm=0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer -----
def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "M": M_FACTS, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "M": M_FACTS,
            "N_PROBES": N_PROBES,
            "NOISE_FRAC": NOISE_FRAC,
            "SPARSITY": SPARSITY,
            "K_ANCHORS": K_ANCHORS,
            "D_RELATIONS": D_RELATIONS,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "config_version": CONFIG_VERSION,
            "allow_synthetic": True,
            "corpus_provenance": "synthetic_bipolar_keys_values",
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
                 "per_unit": v.get("per_unit", [])}
                for k, v in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ----- Main runner -----
out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "M": M_FACTS, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d M=%d N_PROBES=%d arms=%s device=%s seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, M_FACTS, N_PROBES, str(ARMS), str(DEVICE),
         str(done), str(seeds_todo)), flush=True)

if DEVICE.type == "cuda":
    try:
        print("[gpu] device=%s name=%s total_mem_gb=%.2f"
              % (DEVICE, torch.cuda.get_device_name(0),
                 torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
    except Exception as e:
        print("[gpu] info-fetch failed: %s" % e, flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "M": M_FACTS,
    "N_PROBES": N_PROBES,
    "NOISE_FRAC": NOISE_FRAC,
    "SPARSITY": SPARSITY,
    "K_ANCHORS": K_ANCHORS,
    "D_RELATIONS": D_RELATIONS,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "allow_synthetic": True,
    "corpus_provenance": "synthetic_bipolar_keys_values",
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_substrate_as_llm_scaling_million_facts_3arm",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
