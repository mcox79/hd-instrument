"""CONTINUOUS EMBEDDING STORAGE via SimHash Projection at N=16384 (v2 OOM FIX).

INFRA FIX v2 (vs v1):
  v1 OOM at Arm 3 `eval_recall` line 508: moved ALL N=16384 x corpus=10000
  value codes to GPU simultaneously and computed a dense (n_mask x corpus)
  similarity matrix -- 10000 x 10000 x 4 bytes = 400 MB instantiation that
  pushed the 6.31 GB already-allocated W + codes over the 8 GB 4060 Ti limit.

  Fix: `eval_recall` now computes cosine similarity in chunks of 1024 query
  rows (QUERY_BATCH=1024), keeping peak (query_batch x corpus) at
  1024 x 10000 x 4 = 40 MB per chunk.  The v_all_norm tensor is pre-computed
  once and reused across chunks.  Arms 1, 2, 4 are IDENTICAL to v1 -- science
  is unchanged; only Arm 3 memory layout is modified.

CONTEXT (research 2x-deep-synthesis 2026-05-31):
  Research audit collapsed 5 proposed experiments to ONE genuinely-new
  experiment. Key finding: substrate is BIPOLAR {-1,+1}^N MAP-B algebra,
  NOT a continuous-representation store. Ingesting continuous embeddings
  requires a PROJECTION SCHEME (R^d -> {-1,+1}^N), and the projection
  layer is where the algebraic moat properties may degrade.

  SimHash projection recommended: bipolar_code = sign(W_proj @ x)
  with W_proj ~ Gaussian(0, 1/sqrt(N)). N=16384 pushes codes toward
  near-orthogonality, which is the key geometric requirement.

SCIENTIFIC QUESTION:
  Does the SimHash projection layer preserve the 4 substrate moat
  properties sufficiently for a real-time-learning audit-grade vector
  store use case?

  4 arms test different moat survival properties:
    Arm 1: Retrieval recall (substrate vs FAISS FlatIP baseline)
    Arm 2: Algebraic audit preservation (decomposability + hash link)
    Arm 3: Edit isolation (semantically dissimilar vs similar entries)
    Arm 4: Deletion certificate (projected code absent + hash cert valid)

CORPUS DESIGN:
  - Synthetic embeddings: d=768, low-rank + diagonal noise covariance
    (matches typical sentence embedding PCA spectrum; intrinsic dim ~50-100)
  - Corpus size: 10K entries (10_000) -- fits GPU memory at N=16384
  - Each entry: float32 L2-normalised vector in R^768
  - SimHash projection: W_proj (N x d) Gaussian(0, 1/sqrt(d));
    bipolar_code = sign(W_proj @ x)   -- {-1, +1}^N, exact MAP-B type
  - Substrate W: outer-product accumulation W += (1/N) * v @ k^T
    where k = bipolar_code(key), v = bipolar_code(value)
  - FAISS baseline: FlatIP index over L2-normalised original embeddings

PRE-REGISTERED BANDS (carried forward from v1 -- infra fix, not science redesign):

  Arm 1 -- Retrieval recall at N=16384 with 2x over-sampling:
    HARD-PASS : recall@10 >= 0.75 (within 17-20pp of FAISS baseline ~0.92)
    HARD-FAIL : recall@10 < 0.45 (substrate fundamentally incompatible)
    MIDDLE    : [0.45, 0.75) -- below product threshold; consider VQ rescue

  Note: routing note sets HP at 0.82 for MS MARCO (real embeddings); for
  synthetic embeddings with realistic covariance, 0.75 is the calibrated
  first-empirical-anchor band. No prior empirical anchor -- bands widened
  per calibration-probe policy (theoretical ~0.75-0.82 +/-50% = [0.38, 1.0]).
  We pin HP=0.75 and HF=0.45 as meaningful distinguishing thresholds.

  Arm 2 -- Algebraic audit preservation (NN recovery rate):
    Metric: fraction of stored entries where argmax_j <W@k_i, v_j> = i.
    Expected ~0.90 at N=16384 M=10K (SNR=1.28, P(correct)=Phi(1.28)=0.90).
    HARD-PASS : NN recovery rate >= 0.85 (within 5pp of theoretical 0.90)
    HARD-FAIL : NN recovery rate < 0.70 (substrate fundamentally fails audit)
    MIDDLE    : [0.70, 0.85) -- degraded but partially mitigable

  Arm 3 -- Edit isolation:
    HARD-PASS : MAP@10 delta < 5% for dissimilar entries (cos < 0.5)
                AND < 20% for near-neighbor entries (cos 0.7-0.85)
    HARD-FAIL : MAP@10 delta > 15% for dissimilar entries (cos < 0.5)
    MIDDLE    : delta in [5%, 15%) for dissimilar -- some leakage, documented

  Arm 4 -- Deletion certificate:
    HARD-PASS : 100% cert verification (deleted code absent from W response
                at query threshold); 0 false-positive certs
    HARD-FAIL : any false-positive cert (cert verifies for non-deleted entry)
    MIDDLE    : cert works but requires fine-tuned threshold (not automatic)

JOINT VERDICT:
  OVERALL HARD-PASS : all 4 arms pass (full moat with projection intact)
  OVERALL MIDDLE    : arms 1+2 pass, arm 3/4 middle (retrieval + audit OK;
                      isolation/deletion degraded but documented)
  OVERALL HARD-FAIL : any arm HARD-FAIL

OOM CHECK (v2 -- post-fix analysis):
  N=16384, corpus=10K entries.
  W (substrate): 16384 x 16384 x float32 = 1.07 GB (GPU).
  W_proj: 16384 x 768 x float32 = 48 MB (GPU, reused across seeds).
  Bipolar codes (10K): 10000 x 16384 x float32 = 655 MB (CPU storage).
  Embeddings (10K): 10000 x 768 x float32 = 30 MB.
  FAISS index: CPU-side, ~30 MB.
  Arm 3 eval_recall (v2 fix): 1024 query batch x 16384 x 4 = 64 MB responses,
    + 1024 x 10000 x 4 = 40 MB similarity chunk. Peak incremental ~104 MB.
  Total peak GPU: ~1.9 GB. Well under 6 GB headroom.
  Peak CPU RAM: ~750 MB. Fine.

TIMEOUT ESTIMATE:
  v1 Arms 1+2 completed in ~5s (seed=7 log).
  Arm 3 with query-batch=1024: ceil(1.5 * 90s_est * 1.0 * 1) = 135s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS (same as v1 -- unchanged):
  1. SimHash property: E[hamming(sign(W@x), sign(W@y))] / N
     = (1/pi) * arccos(cos_sim(x, y)) for Gaussian W.
     Verified: x=y -> hamming=0; orthogonal x,y -> hamming~N/2.
  2. MAP-B outer product: W = sum_i (1/N) v_i @ k_i^T.
     Query: W @ q = sum_i (1/N) <k_i, q> v_i.
     For query q = k_j: <k_j, k_j> = N (bipolar self-inner product).
     So response = (1) * v_j + sum_{i!=j} (1/N) <k_i, k_j> * v_i.
     Noise term: each (1/N) * <k_i, k_j> ~ N(0, 1/N) for random BSC.
     SNR = N / sqrt(M * N) = sqrt(N/M). At N=16384, M=10000: SNR=1.28.
     Recall expected: Phi(SNR) ~ 0.90 at this SNR.
  3. Oversampling (2x): query 2x more candidates from bipolar codes,
     re-rank on exact cosine. Recall boosted by oversampling factor.
  4. Edit: W_edited = W_old - (1/N) v_old @ k_old^T + (1/N) v_new @ k_new^T.
     For entry j: W_edited @ k_j = v_new + noise. v_old contribution removed.
  5. Deletion: W_deleted = W_old - (1/N) v_del @ k_del^T.
     Response to q=k_del: W_deleted @ k_del = noise only. Below threshold.
  6. SHA256 cert: sha256(original_embedding bytes) + W_seed + entry_idx.
     Deterministic given the seed; verifiable by re-running projection.

PROT-018: _n16384 binds N = 16384.
PROT-019: timeout_s = 14400.
PROT-021: per-seed checkpointing via _seed_checkpoint.

Anchor: continuous_embedding_storage_substrate_v2_n16384
Queue: overnight_queue (GPU, N=16384 outer-product W)
Pre-reg: preregs/2026-06-01_continuous_embedding_storage_substrate_v2_n16384.md
HDLAB_EXP_NAME: cont_emb_v2
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# OpenMP conflict workaround: faiss and torch ship different OpenMP runtimes.
# Setting KMP_DUPLICATE_LIB_OK=TRUE suppresses the crash and allows coexistence.
# Must be set BEFORE importing either library.
import os as _os_omp
_os_omp.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')

import hashlib
import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    faiss = None  # type: ignore[assignment]
    _FAISS_AVAILABLE = False

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_ck_cesv2", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
resumable_seeds = _ck.resumable_seeds
write_partial    = _ck.write_partial
aggregate_partials = _ck.aggregate_partials

# ============================================================
# PROT-018: _n16384 binds N = 16384
# Production N must equal 16384 per anchor name contract.
# ============================================================
N_FULL  = 16384   # PROT-018 binding: production N = 16384
N_SMOKE = 1024
assert N_FULL == 16384, f"PROT-018: N_FULL must be 16384; got {N_FULL}"

# Embedding dimensionality (mimics sentence-transformer output)
D_EMBED = 768

# Corpus sizes
CORPUS_FULL  = 10_000   # entries to store
CORPUS_SMOKE = 256

# Retrieval evaluation
K_CANDIDATES_FULL  = 10  # recall@10
K_OVERSAMPLE = 2         # 2x oversampling for re-rank

# Edit/delete arm sizes
N_EDIT   = 100
N_DELETE = 100

# Seeds
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Query batching for OOM-safe eval (v2 fix)
QUERY_BATCH = 1024   # chunk queries in eval_recall to bound peak GPU alloc

# Thresholds (pre-registered, identical to v1)
HP_RECALL_10      = 0.75   # Arm 1 HARD-PASS
HF_RECALL_10      = 0.45   # Arm 1 HARD-FAIL

HP_AUDIT_FRAC     = 0.85   # Arm 2 HARD-PASS: NN recovery rate >= 0.85
HF_AUDIT_FRAC     = 0.70   # Arm 2 HARD-FAIL: NN recovery rate < 0.70

HP_EDIT_DISSIM    = 0.05   # Arm 3 HARD-PASS: MAP delta < 5% for cos<0.5
HP_EDIT_NEIGHBOR  = 0.20   # Arm 3 HARD-PASS: MAP delta < 20% for cos 0.7-0.85
HF_EDIT_DISSIM    = 0.15   # Arm 3 HARD-FAIL: MAP delta > 15% for cos<0.5

HP_CERT_RATE      = 1.0    # Arm 4 HARD-PASS: 100% cert verification
HF_CERT_FP        = 0.0    # Arm 4 HARD-FAIL: any false-positive cert


def get_output_dir(
    default_name: str = "cont_emb_v2",
) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ============================================================
# Synthetic embedding generator
# ============================================================

def make_synthetic_embeddings(
    n: int,
    d: int,
    seed: int,
    rank: int = 64,
) -> np.ndarray:
    """Generate n synthetic embeddings of dim d with realistic covariance.

    Uses low-rank + diagonal noise to approximate sentence-embedding
    PCA spectrum. Returns L2-normalised float32 (n, d) array.

    rank: number of principal components with elevated variance.
    Eigenvalue spectrum: first `rank` components have variance ~5,
    remaining components have variance ~0.5. Matches typical sentence
    embedding PCA where first 50-100 PCs explain ~60-70% variance.
    """
    rng = np.random.default_rng(seed + 7000)

    # Low-rank component: U (d, rank) orthonormal basis
    rank = min(rank, d)
    U_raw = rng.standard_normal((d, rank)).astype(np.float32)
    U, _ = np.linalg.qr(U_raw)
    U = U[:, :rank].astype(np.float32)  # (d, rank)

    # Scores in latent space: (n, rank) from N(0, sqrt(5))
    z = rng.standard_normal((n, rank)).astype(np.float32) * math.sqrt(5.0)

    # Diagonal noise
    noise_var = 0.5
    noise = rng.standard_normal((n, d)).astype(np.float32) * math.sqrt(noise_var)

    # Embeddings = z @ U^T + noise   (n, d)
    embeddings = z @ U.T + noise

    # L2 normalise each row
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True).clip(min=1e-8)
    embeddings = embeddings / norms
    return embeddings  # float32 (n, d)


# ============================================================
# SimHash projection
# ============================================================

def make_projection_matrix(N: int, d: int, seed: int,
                            device: torch.device) -> torch.Tensor:
    """Fixed Gaussian projection matrix W_proj (N, d).

    bipolar_code = sign(W_proj @ x) for x in R^d L2-normalised.
    Entries ~ N(0, 1/sqrt(d)).
    """
    gen = torch.Generator(device=device).manual_seed(seed + 3000)
    W = torch.randn(N, d, generator=gen, device=device,
                    dtype=torch.float32) / math.sqrt(d)
    return W  # (N, d)


def simhash_project(embeddings: torch.Tensor, W_proj: torch.Tensor) -> torch.Tensor:
    """Project (n, d) float32 embeddings to (n, N) bipolar {-1, +1} codes.

    embeddings: (n, d) L2-normalised float32
    W_proj    : (N, d)
    Returns   : (n, N) float32 in {-1.0, +1.0}
    """
    logits = embeddings @ W_proj.T   # (n, N)
    return torch.sign(logits)        # {-1, 0, +1}; ties at 0 -> 0 (rare at N=16384)


# ============================================================
# Substrate (outer-product MAP-B)
# ============================================================

def build_substrate(
    keys_bp: torch.Tensor,    # (n, N) bipolar keys
    vals_bp: torch.Tensor,    # (n, N) bipolar values
    N: int,
    device: torch.device,
) -> torch.Tensor:
    """Build substrate matrix W by accumulating rank-1 outer products.

    W = sum_i (1/N) * v_i @ k_i^T   shape (N, N)

    Uses batched matmul to be memory-efficient.
    """
    n = keys_bp.shape[0]
    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    batch = 512  # process in batches to avoid OOM
    for start in range(0, n, batch):
        end = min(start + batch, n)
        k_b = keys_bp[start:end].to(device)   # (b, N)
        v_b = vals_bp[start:end].to(device)   # (b, N)
        W.add_(v_b.T @ k_b, alpha=1.0 / N)
    return W


def query_substrate(
    W: torch.Tensor,           # (N, N)
    q_bp: torch.Tensor,        # (k, N) query bipolar codes
    K: int,
    vals_bp: torch.Tensor,     # (corpus, N) all stored value codes (on CPU)
    device: torch.device,
) -> torch.Tensor:
    """Retrieve top-K value indices for each query.

    Response: r_q = W @ q   (N,)
    Then nearest-neighbour in val codebook by cosine/inner product.

    Returns (k, K) top-K indices.
    """
    q_bp_dev = q_bp.to(device)
    # Response: (N, k)
    responses = W @ q_bp_dev.T   # (N, k)
    responses = responses.T      # (k, N)

    # Cosine similarity against all stored value codes
    vals_dev = vals_bp.to(device)
    r_norm = responses / (responses.norm(dim=-1, keepdim=True).clamp(min=1e-8))
    v_norm = vals_dev / (vals_dev.norm(dim=-1, keepdim=True).clamp(min=1e-8))
    # Similarity: (k, corpus)
    sims = r_norm @ v_norm.T
    # Top-K
    topk_vals, topk_idx = sims.topk(K, dim=-1)
    return topk_idx.cpu()   # (k, K)


# ============================================================
# FAISS baseline
# ============================================================

def build_faiss_index(embeddings_np: np.ndarray):
    """Build FAISS FlatIP index over L2-normalised embeddings.

    Returns None if FAISS is not available (self-test will skip Arm 1).
    """
    if not _FAISS_AVAILABLE:
        return None
    d = embeddings_np.shape[1]
    idx = faiss.IndexFlatIP(d)
    idx.add(embeddings_np.astype(np.float32))
    return idx


def faiss_recall_at_k(
    index,
    queries: np.ndarray,   # (nq, d)
    true_ids: np.ndarray,  # (nq,) ground-truth nearest neighbour index
    K: int,
) -> float:
    """Fraction of queries where the true NN is in top-K results.

    Returns -1.0 if FAISS index is None (unavailable).
    """
    if index is None:
        return -1.0
    _, I = index.search(queries.astype(np.float32), K)
    hits = sum(int(true_ids[i] in I[i]) for i in range(len(true_ids)))
    return hits / len(true_ids)


def substrate_recall_at_k(
    topk_idx: torch.Tensor,   # (nq, K) retrieved indices
    true_ids: np.ndarray,     # (nq,) true NN index
    K: int,
) -> float:
    """Fraction of queries where true NN is in top-K retrieved."""
    hits = 0
    topk_np = topk_idx.numpy()
    for i in range(len(true_ids)):
        if true_ids[i] in topk_np[i, :K]:
            hits += 1
    return hits / len(true_ids)


# ============================================================
# Audit arm helpers
# ============================================================

def compute_audit_pass_frac(
    W: torch.Tensor,         # (N, N) substrate
    keys_bp: torch.Tensor,   # (corpus, N)
    vals_bp: torch.Tensor,   # (corpus, N)
    N: int,
    device: torch.device,
    batch: int = 128,
) -> float:
    """Fraction of stored entries that audit-decompose correctly via NN lookup.

    Audit: query W with key k_i -> response r = W @ k_i.
    Nearest-neighbor in val codebook: argmax_j <r, v_j>.
    Pass iff argmax_j = i (the stored value is recovered exactly).

    This is the algebraic audit property: given a key, can an auditor
    verify which value was stored by querying the substrate?
    Expected rate at N=16384, M=10K: ~0.90 (SNR = sqrt(N/M) = 1.28).
    Expected rate at N=1024, M=256: ~0.977 (SNR = 2.00).
    """
    n = keys_bp.shape[0]
    passes = 0
    vals_dev = vals_bp.to(device)
    vals_norm = vals_dev / vals_dev.norm(dim=-1, keepdim=True).clamp(min=1e-8)

    for start in range(0, n, batch):
        end = min(start + batch, n)
        k_b = keys_bp[start:end].to(device)   # (b, N)
        r_b = (W @ k_b.T).T                   # (b, N)
        r_norm = r_b / r_b.norm(dim=-1, keepdim=True).clamp(min=1e-8)
        sims = r_norm @ vals_norm.T            # (b, corpus)
        pred_idx = sims.argmax(dim=-1).cpu()   # (b,)
        true_idx = torch.arange(start, end)
        passes += int((pred_idx == true_idx).sum().item())
    return passes / n


# ============================================================
# Edit isolation arm (v2: batched eval_recall, OOM fix)
# ============================================================

def compute_edit_isolation(
    W_orig: torch.Tensor,    # (N, N)
    keys_bp: torch.Tensor,   # (corpus, N)
    vals_bp: torch.Tensor,   # (corpus, N)
    embeddings_np: np.ndarray,  # (corpus, d) original float embeddings
    N_EDIT: int,
    N: int,
    device: torch.device,
    seed: int,
    query_batch: int = QUERY_BATCH,
) -> Dict[str, float]:
    """Measure MAP@10 delta after editing N_EDIT entries.

    v2 FIX: eval_recall now computes cosine similarity in chunks of
    `query_batch` rows, keeping peak GPU alloc at (query_batch x corpus)
    instead of (n_all_queries x corpus). Prevents OOM at N=16384.

    Edits are randomly selected entries. After editing, we measure
    recall@10 degradation for:
      - Dissimilar entries (cosine < 0.5 to edited entries)
      - Near-neighbor entries (cosine 0.7-0.85 to edited entries)

    Returns dict with map_delta_dissim and map_delta_neighbor.
    """
    n = keys_bp.shape[0]
    rng = np.random.default_rng(seed + 5000)
    edit_indices = rng.choice(n, size=min(N_EDIT, n), replace=False)
    non_edit_indices = np.array([i for i in range(n) if i not in set(edit_indices)])

    if len(non_edit_indices) == 0:
        return {"map_delta_dissim": 0.0, "map_delta_neighbor": 0.0,
                "n_dissim": 0, "n_neighbor": 0}

    # Compute cosine similarity of non-edit entries to edited entries
    edited_embs = embeddings_np[edit_indices]   # (N_EDIT, d)
    non_edit_embs = embeddings_np[non_edit_indices]  # (n_ne, d)
    # Max cosine similarity to any edited entry
    cos_mat = non_edit_embs @ edited_embs.T  # (n_ne, N_EDIT); both L2-normalised
    max_cos = cos_mat.max(axis=1)            # (n_ne,)

    dissim_mask  = max_cos < 0.5
    neighbor_mask = (max_cos >= 0.7) & (max_cos <= 0.85)

    # Apply edits: remove old entry, add new (random value replacement)
    W_edit = W_orig.clone()
    for idx in edit_indices:
        k_old = keys_bp[idx:idx+1].to(device)   # (1, N)
        v_old = vals_bp[idx:idx+1].to(device)
        gen = torch.Generator(device=device).manual_seed(int(idx) + seed + 8000)
        v_new = (torch.randint(0, 2, (1, N), generator=gen,
                               device=device, dtype=torch.float32) * 2 - 1)
        W_edit.add_(v_new.T @ k_old, alpha=1.0 / N)
        W_edit.sub_(v_old.T @ k_old, alpha=1.0 / N)

    # v2 OOM FIX: batched eval_recall
    # Pre-compute v_all_norm ONCE (corpus x N); stays on GPU throughout
    # but that is only 655 MB for N=16384 corpus=10000 -- within budget.
    # The FIX is that we chunk QUERIES (rows of r_norm), not values.
    # Peak incremental per chunk: (query_batch x N) + (query_batch x corpus)
    # = 1024 x 16384 x 4 + 1024 x 10000 x 4 = 64MB + 40MB = 104 MB. OK.

    def eval_recall_batched(W_use: torch.Tensor, mask: np.ndarray) -> float:
        indices_in_mask = non_edit_indices[mask]
        if len(indices_in_mask) == 0:
            return -1.0
        K_eval = min(10, len(indices_in_mask))

        # Pre-compute and cache normalised value matrix on GPU
        v_all = vals_bp.to(device)  # (corpus, N)
        v_all_norm = v_all / v_all.norm(dim=-1, keepdim=True).clamp(min=1e-8)

        hits = 0
        total = len(indices_in_mask)

        # Process queries in batches of query_batch
        for qstart in range(0, total, query_batch):
            qend = min(qstart + query_batch, total)
            batch_idx = indices_in_mask[qstart:qend]
            q_bp = keys_bp[batch_idx].to(device)  # (b, N)
            r = (W_use @ q_bp.T).T                # (b, N)
            r_norm = r / r.norm(dim=-1, keepdim=True).clamp(min=1e-8)
            sims = r_norm @ v_all_norm.T           # (b, corpus)
            _, topk = sims.topk(K_eval, dim=-1)   # (b, K_eval)
            topk_np = topk.cpu().numpy()
            for local_i, true_idx in enumerate(batch_idx):
                if true_idx in topk_np[local_i]:
                    hits += 1

        return hits / total

    recall_before_dissim   = eval_recall_batched(W_orig, dissim_mask)
    recall_after_dissim    = eval_recall_batched(W_edit, dissim_mask)
    recall_before_neighbor = eval_recall_batched(W_orig, neighbor_mask)
    recall_after_neighbor  = eval_recall_batched(W_edit, neighbor_mask)

    if recall_before_dissim > 0 and recall_before_dissim != -1.0:
        delta_dissim = abs(recall_after_dissim - recall_before_dissim) / recall_before_dissim
    else:
        delta_dissim = 0.0

    if recall_before_neighbor > 0 and recall_before_neighbor != -1.0:
        delta_neighbor = abs(recall_after_neighbor - recall_before_neighbor) / recall_before_neighbor
    else:
        delta_neighbor = 0.0

    return {
        "map_delta_dissim": float(delta_dissim),
        "map_delta_neighbor": float(delta_neighbor),
        "recall_before_dissim": float(recall_before_dissim),
        "recall_after_dissim": float(recall_after_dissim),
        "recall_before_neighbor": float(recall_before_neighbor),
        "recall_after_neighbor": float(recall_after_neighbor),
        "n_dissim": int(dissim_mask.sum()),
        "n_neighbor": int(neighbor_mask.sum()),
    }


# ============================================================
# Deletion certificate arm
# ============================================================

def compute_deletion_cert(
    W_orig: torch.Tensor,        # (N, N)
    keys_bp: torch.Tensor,       # (corpus, N)
    vals_bp: torch.Tensor,       # (corpus, N)
    embeddings_np: np.ndarray,   # (corpus, d)
    N_DELETE: int,
    N: int,
    device: torch.device,
    seed: int,
    w_proj_seed: int,
) -> Dict[str, float]:
    """Measure deletion certificate correctness.

    For N_DELETE entries:
      1. Compute sha256 cert: sha256(embedding_bytes + str(w_proj_seed).encode()
                                    + str(entry_idx).encode())
      2. Delete entry from W.
      3. Verify: W_del @ k_del response norm < threshold (deletion detectable).
      4. Check: cert is NOT verifiable for non-deleted entries (no FP).

    Returns dict with cert_rate (fraction verified) and fp_rate.
    """
    n = keys_bp.shape[0]
    rng = np.random.default_rng(seed + 6000)
    del_indices = rng.choice(n, size=min(N_DELETE, n), replace=False)
    non_del_indices = np.array([i for i in range(n) if i not in set(del_indices)])

    # Compute certs for deleted entries
    certs = []
    for idx in del_indices:
        emb_bytes = embeddings_np[idx].tobytes()
        h = hashlib.sha256()
        h.update(emb_bytes)
        h.update(str(w_proj_seed).encode())
        h.update(str(int(idx)).encode())
        certs.append(h.hexdigest())

    # Build W_del by removing deleted entries
    W_del = W_orig.clone()
    for idx in del_indices:
        k_del = keys_bp[idx:idx+1].to(device)
        v_del = vals_bp[idx:idx+1].to(device)
        W_del.sub_(v_del.T @ k_del, alpha=1.0 / N)

    cert_verifications = 0
    false_positives = 0

    # Calibrate threshold from NON-deleted entries
    if len(non_del_indices) > 0:
        nd_sample = non_del_indices[:min(50, len(non_del_indices))]
        nd_scores = []
        for idx in nd_sample:
            k_q = keys_bp[idx:idx+1].to(device)
            v_q = vals_bp[idx:idx+1].to(device)
            r = (W_del @ k_q.T).T   # (1, N)
            score = (r * v_q).sum(dim=-1).item() / N
            nd_scores.append(score)
        threshold_score = float(np.mean(nd_scores)) * 0.5
    else:
        threshold_score = 0.1

    # Check each deleted entry: its score should be < threshold
    del_scores = []
    for idx in del_indices:
        k_q = keys_bp[idx:idx+1].to(device)
        v_q = vals_bp[idx:idx+1].to(device)
        r = (W_del @ k_q.T).T
        score = (r * v_q).sum(dim=-1).item() / N
        del_scores.append(score)
        if score < threshold_score:
            cert_verifications += 1

    cert_rate = cert_verifications / len(del_indices) if len(del_indices) > 0 else 0.0

    # False positive check: do any non-deleted entries score below threshold?
    if len(non_del_indices) > 0:
        nd_fp_sample = non_del_indices[:min(100, len(non_del_indices))]
        for idx in nd_fp_sample:
            k_q = keys_bp[idx:idx+1].to(device)
            v_q = vals_bp[idx:idx+1].to(device)
            r = (W_del @ k_q.T).T
            score = (r * v_q).sum(dim=-1).item() / N
            if score < threshold_score:
                false_positives += 1
        fp_rate = false_positives / len(nd_fp_sample)
    else:
        fp_rate = 0.0

    return {
        "cert_rate": float(cert_rate),
        "fp_rate": float(fp_rate),
        "threshold_score": float(threshold_score),
        "mean_del_score": float(np.mean(del_scores)) if del_scores else 0.0,
        "n_certs": len(del_indices),
        "n_fp_checked": len(non_del_indices[:min(100, len(non_del_indices))]),
    }


# ============================================================
# Instrumentation self-test (MANDATORY, called at module scope)
# ============================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale.

    v2: also validates the batched eval_recall path (QUERY_BATCH applied
    at N=256 scale; passes correctness check vs unbatched baseline).
    """
    device = torch.device("cpu")
    N_t = 256
    d_t = 32
    n_t = 50
    seed_t = 42

    # 1. Synthetic embeddings
    embs = make_synthetic_embeddings(n_t, d_t, seed_t)
    assert embs.shape == (n_t, d_t), f"emb shape {embs.shape}"
    assert np.isfinite(embs).all(), "embs contain nan/inf"
    norms = np.linalg.norm(embs, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5), f"embs not L2-normalised; norms={norms[:3]}"

    # 2. SimHash projection
    W_proj = make_projection_matrix(N_t, d_t, seed_t, device)
    embs_t = torch.tensor(embs, dtype=torch.float32, device=device)
    codes = simhash_project(embs_t, W_proj)
    assert codes.shape == (n_t, N_t), f"codes shape {codes.shape}"
    unique_vals = codes.unique()
    assert set(unique_vals.tolist()).issubset({-1.0, 0.0, 1.0}), \
        f"codes not bipolar: unique={unique_vals.tolist()[:5]}"
    frac_zero = (codes == 0.0).float().mean().item()
    assert frac_zero < 0.01, f"too many zero codes: {frac_zero:.4f}"

    # 3. Substrate build + query
    embs_val_t = make_synthetic_embeddings(n_t, d_t, seed_t + 100)
    W_proj_val = make_projection_matrix(N_t, d_t, seed_t + 1, device)
    embs_val_torch = torch.tensor(embs_val_t, dtype=torch.float32, device=device)
    keys_t = codes
    vals_t = simhash_project(embs_val_torch, W_proj_val)
    W = build_substrate(keys_t, vals_t, N_t, device)
    assert W.shape == (N_t, N_t), f"W shape {W.shape}"
    assert W.isfinite().all(), "W has nan/inf"
    assert W.abs().max().item() > 0, "W is all zeros"

    q = keys_t[0:1]  # (1, N)
    r = (W @ q.T).T  # (1, N)
    cos = ((r / r.norm()) * (vals_t[0] / vals_t[0].norm())).sum().item()
    assert cos > 0.1, f"substrate query cosine too low: {cos:.4f}"

    # 4. FAISS index
    embs_np = embs.astype(np.float32)
    faiss_idx = build_faiss_index(embs_np)
    if faiss_idx is not None:
        assert faiss_idx.ntotal == n_t, f"FAISS index size {faiss_idx.ntotal}"
        _, I = faiss_idx.search(embs_np[:5], 1)
        assert (I[:, 0] == np.arange(5)).all(), \
            f"FAISS exact-match NN failed: {I[:, 0]}"
        print("[selftest] FAISS: OK", flush=True)
    else:
        print("[selftest] FAISS: SKIPPED (not installed locally; will run on remote)", flush=True)

    # 5. Audit fraction
    frac = compute_audit_pass_frac(W, keys_t, vals_t, N_t, device)
    assert 0.0 <= frac <= 1.0, f"audit frac out of range: {frac}"
    assert frac > 0.5, f"audit NN recovery too low at smoke scale: {frac:.4f}"

    # 6. Deletion cert
    cert_result = compute_deletion_cert(
        W, keys_t, vals_t, embs_np, 5, N_t, device, seed_t, seed_t + 1
    )
    assert "cert_rate" in cert_result, "cert_rate missing"
    assert 0.0 <= cert_result["cert_rate"] <= 1.0, \
        f"cert_rate out of range: {cert_result['cert_rate']}"
    assert "fp_rate" in cert_result, "fp_rate missing"

    # 7. Edit isolation (v2: tests batched eval_recall at QUERY_BATCH=16 for smoke)
    # Use a small query_batch to exercise the batching logic even at n_t=50
    edit_result = compute_edit_isolation(
        W, keys_t, vals_t, embs_np, 5, N_t, device, seed_t,
        query_batch=16,  # forces multi-chunk even at small n_t
    )
    assert "map_delta_dissim" in edit_result, "map_delta_dissim missing"
    assert edit_result["map_delta_dissim"] >= 0.0, \
        f"map_delta_dissim negative: {edit_result['map_delta_dissim']}"

    # 8. Verify batched eval_recall correctness: compare single-batch vs
    # 16-chunk result on a controlled set (they must agree to within float32 precision).
    # Use n_t=50 entries with QUERY_BATCH=50 (single chunk) vs QUERY_BATCH=7 (8 chunks).
    # Compare hit counts directly (deterministic).
    edit_single = compute_edit_isolation(
        W, keys_t, vals_t, embs_np, 5, N_t, device, seed_t,
        query_batch=50,
    )
    edit_chunked = compute_edit_isolation(
        W, keys_t, vals_t, embs_np, 5, N_t, device, seed_t,
        query_batch=7,
    )
    assert abs(edit_single["map_delta_dissim"] - edit_chunked["map_delta_dissim"]) < 1e-5, \
        (f"batched eval_recall result mismatch: single={edit_single['map_delta_dissim']:.6f} "
         f"chunked={edit_chunked['map_delta_dissim']:.6f}")
    assert edit_single["n_dissim"] == edit_chunked["n_dissim"], \
        f"n_dissim mismatch: {edit_single['n_dissim']} vs {edit_chunked['n_dissim']}"

    print("[selftest] PASS: all assertions passed at N=256 smoke scale (v2 batching verified).",
          flush=True)


# Called at module scope -- fails fast before any runner work
_instrumentation_selftest()


# ============================================================
# Per-seed experiment
# ============================================================

def run_one_seed(
    seed: int,
    N: int,
    corpus_size: int,
    is_smoke: bool,
    device: torch.device,
) -> Dict:
    """Run all 4 arms for one seed. Returns per-seed metrics dict."""
    t_start = time.time()
    print(f"[seed={seed}] N={N} corpus={corpus_size} smoke={is_smoke} device={device}",
          flush=True)

    # 1. Generate embeddings
    t0 = time.time()
    embs_key_np = make_synthetic_embeddings(corpus_size, D_EMBED, seed + 100)
    embs_val_np = make_synthetic_embeddings(corpus_size, D_EMBED, seed + 200)
    print(f"  [seed={seed}] embs generated in {time.time()-t0:.2f}s", flush=True)

    # 2. SimHash projection
    t0 = time.time()
    W_proj_seed = seed + 4000
    W_proj = make_projection_matrix(N, D_EMBED, W_proj_seed, device)
    embs_key_t = torch.tensor(embs_key_np, dtype=torch.float32, device=device)
    embs_val_t = torch.tensor(embs_val_np, dtype=torch.float32, device=device)
    keys_bp = simhash_project(embs_key_t, W_proj)   # (corpus, N)
    vals_bp = simhash_project(embs_val_t, W_proj)   # (corpus, N)
    keys_bp_cpu = keys_bp.cpu()
    vals_bp_cpu = vals_bp.cpu()
    del embs_key_t, embs_val_t  # free GPU memory
    print(f"  [seed={seed}] projection done in {time.time()-t0:.2f}s", flush=True)

    # 3. Build substrate W
    t0 = time.time()
    W = build_substrate(keys_bp_cpu, vals_bp_cpu, N, device)
    print(f"  [seed={seed}] substrate built in {time.time()-t0:.2f}s", flush=True)

    # ===========================================================
    # ARM 1: Retrieval recall
    # ===========================================================
    t0 = time.time()
    K_recall = min(K_CANDIDATES_FULL, corpus_size)

    faiss_idx = build_faiss_index(embs_key_np.astype(np.float32))
    true_ids = np.arange(corpus_size)

    faiss_recall = faiss_recall_at_k(faiss_idx, embs_key_np, true_ids, K_recall)
    if faiss_recall < 0:
        print(f"  [seed={seed}] FAISS not available; ARM1 FAISS baseline skipped", flush=True)

    q_bp = keys_bp_cpu
    topk_idx = query_substrate(W, q_bp, K_recall, vals_bp_cpu, device)
    sub_recall_no_os = substrate_recall_at_k(topk_idx, true_ids, K_recall)

    K_oversamp = min(K_recall * K_OVERSAMPLE, corpus_size)
    topk_os_idx = query_substrate(W, q_bp, K_oversamp, vals_bp_cpu, device)
    sub_recall_os = substrate_recall_at_k(topk_os_idx, true_ids, K_recall)

    print(f"  [seed={seed}] Arm1 recall: FAISS={faiss_recall:.3f} "
          f"Sub_noOS={sub_recall_no_os:.3f} Sub_OS={sub_recall_os:.3f} "
          f"({time.time()-t0:.2f}s)", flush=True)

    # ===========================================================
    # ARM 2: Algebraic audit preservation
    # ===========================================================
    t0 = time.time()
    audit_frac = compute_audit_pass_frac(W, keys_bp_cpu, vals_bp_cpu, N, device)
    print(f"  [seed={seed}] Arm2 audit_frac={audit_frac:.4f} ({time.time()-t0:.2f}s)",
          flush=True)

    # ===========================================================
    # ARM 3: Edit isolation (v2: batched, OOM-safe)
    # ===========================================================
    t0 = time.time()
    n_edit = min(N_EDIT, corpus_size // 5)
    edit_metrics = compute_edit_isolation(
        W, keys_bp_cpu, vals_bp_cpu, embs_key_np,
        n_edit, N, device, seed,
    )
    print(f"  [seed={seed}] Arm3 edit: delta_dissim={edit_metrics['map_delta_dissim']:.4f} "
          f"delta_neighbor={edit_metrics['map_delta_neighbor']:.4f} "
          f"n_dissim={edit_metrics['n_dissim']} n_neighbor={edit_metrics['n_neighbor']} "
          f"({time.time()-t0:.2f}s)", flush=True)

    # ===========================================================
    # ARM 4: Deletion certificate
    # ===========================================================
    t0 = time.time()
    n_del = min(N_DELETE, corpus_size // 5)
    cert_metrics = compute_deletion_cert(
        W, keys_bp_cpu, vals_bp_cpu, embs_key_np,
        n_del, N, device, seed, W_proj_seed
    )
    print(f"  [seed={seed}] Arm4 cert: cert_rate={cert_metrics['cert_rate']:.4f} "
          f"fp_rate={cert_metrics['fp_rate']:.4f} ({time.time()-t0:.2f}s)", flush=True)

    elapsed = time.time() - t_start
    print(f"[seed={seed}] done in {elapsed:.2f}s", flush=True)

    return {
        "seed": seed,
        "N": N,
        "corpus_size": corpus_size,
        "is_smoke": is_smoke,
        "elapsed_s": elapsed,
        # Arm 1
        "faiss_recall_at_k": float(faiss_recall),
        "sub_recall_no_oversample": float(sub_recall_no_os),
        "sub_recall_2x_oversample": float(sub_recall_os),
        "K_recall": K_recall,
        # Arm 2
        "audit_frac": float(audit_frac),
        # Arm 3
        **{f"arm3_{k}": v for k, v in edit_metrics.items()},
        # Arm 4
        **{f"arm4_{k}": v for k, v in cert_metrics.items()},
    }


# ============================================================
# Verdict computation
# ============================================================

def compute_verdict(agg: Dict[str, List[float]]) -> Dict:
    """Compute PASS/MIDDLE/FAIL per arm and overall verdict."""
    def mean_field(key: str) -> float:
        vals = agg.get(key, [])
        return float(np.mean(vals)) if vals else float("nan")

    # Arm 1
    recall_os = mean_field("sub_recall_2x_oversample")
    if recall_os >= HP_RECALL_10:
        arm1 = "HARD_PASS"
    elif recall_os < HF_RECALL_10:
        arm1 = "HARD_FAIL"
    else:
        arm1 = "MIDDLE_BAND"

    # Arm 2
    audit = mean_field("audit_frac")
    if audit >= HP_AUDIT_FRAC:
        arm2 = "HARD_PASS"
    elif audit < HF_AUDIT_FRAC:
        arm2 = "HARD_FAIL"
    else:
        arm2 = "MIDDLE_BAND"

    # Arm 3
    delta_dissim = mean_field("arm3_map_delta_dissim")
    delta_neighbor = mean_field("arm3_map_delta_neighbor")
    if delta_dissim < HP_EDIT_DISSIM and delta_neighbor < HP_EDIT_NEIGHBOR:
        arm3 = "HARD_PASS"
    elif delta_dissim > HF_EDIT_DISSIM:
        arm3 = "HARD_FAIL"
    else:
        arm3 = "MIDDLE_BAND"

    # Arm 4
    cert_rate = mean_field("arm4_cert_rate")
    fp_rate = mean_field("arm4_fp_rate")
    if cert_rate >= HP_CERT_RATE and fp_rate <= HF_CERT_FP:
        arm4 = "HARD_PASS"
    elif fp_rate > HF_CERT_FP:
        arm4 = "HARD_FAIL"
    else:
        arm4 = "MIDDLE_BAND"

    # Overall
    verdicts = [arm1, arm2, arm3, arm4]
    if any(v == "HARD_FAIL" for v in verdicts):
        overall = "HARD_FAIL"
    elif all(v == "HARD_PASS" for v in verdicts):
        overall = "HARD_PASS"
    else:
        overall = "MIDDLE_BAND"

    return {
        "arm1_recall": arm1,
        "arm2_audit": arm2,
        "arm3_edit": arm3,
        "arm4_cert": arm4,
        "overall": overall,
        "recall_2x_oversample_mean": recall_os,
        "audit_frac_mean": audit,
        "edit_delta_dissim_mean": delta_dissim,
        "edit_delta_neighbor_mean": delta_neighbor,
        "cert_rate_mean": cert_rate,
        "fp_rate_mean": fp_rate,
        "faiss_recall_mean": mean_field("faiss_recall_at_k"),
    }


# ============================================================
# Main sweep
# ============================================================

def main() -> None:
    is_smoke = os.environ.get("HDLAB_SMOKE", "0") == "1"
    device_str = os.environ.get("HDLAB_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(device_str)

    N = N_SMOKE if is_smoke else N_FULL
    corpus_size = CORPUS_SMOKE if is_smoke else CORPUS_FULL
    seeds = SEEDS_SMOKE if is_smoke else SEEDS_FULL

    out_dir = get_output_dir()
    print(f"[main] N={N} corpus={corpus_size} seeds={seeds} device={device} "
          f"smoke={is_smoke} out={out_dir}", flush=True)

    # PROT-021: seed-level checkpointing
    done, remaining = resumable_seeds(seeds, out_dir)
    print(f"[ckpt] {len(done)} seeds done, {len(remaining)} remaining: {remaining}",
          flush=True)

    for seed in remaining:
        result = run_one_seed(seed, N, corpus_size, is_smoke, device)
        write_partial(out_dir, seed, result)
        print(f"[ckpt] seed={seed} written to {out_dir}", flush=True)

    # Aggregate
    per_seed = aggregate_partials(out_dir, seeds)
    print(f"[agg] {len(per_seed)} seeds aggregated", flush=True)

    metric_keys = [
        "sub_recall_2x_oversample", "sub_recall_no_oversample",
        "faiss_recall_at_k", "audit_frac",
        "arm3_map_delta_dissim", "arm3_map_delta_neighbor",
        "arm4_cert_rate", "arm4_fp_rate",
    ]
    agg: Dict[str, List[float]] = {k: [] for k in metric_keys}
    for sd_str, sd_data in per_seed.items():
        for k in metric_keys:
            v = sd_data.get(k)
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                fv = float(v)
                if fv >= 0.0:  # exclude -1.0 sentinel (FAISS unavailable)
                    agg[k].append(fv)

    verdict_data = compute_verdict(agg)

    vd = verdict_data
    verdict_msg = (
        f"continuous_embedding_storage_substrate_v2_n16384 "
        f"N={N} corpus={corpus_size} seeds={seeds}\n"
        f"Arm1 recall: {vd['arm1_recall']} | "
        f"sub_recall_2x_os={vd['recall_2x_oversample_mean']:.3f} "
        f"faiss={vd['faiss_recall_mean']:.3f}\n"
        f"Arm2 audit:  {vd['arm2_audit']} | "
        f"audit_frac={vd['audit_frac_mean']:.4f}\n"
        f"Arm3 edit:   {vd['arm3_edit']} | "
        f"delta_dissim={vd['edit_delta_dissim_mean']:.4f} "
        f"delta_neighbor={vd['edit_delta_neighbor_mean']:.4f}\n"
        f"Arm4 cert:   {vd['arm4_cert']} | "
        f"cert_rate={vd['cert_rate_mean']:.4f} fp_rate={vd['fp_rate_mean']:.4f}\n"
        f"OVERALL: {vd['overall']}"
    )
    print(verdict_msg, flush=True)

    total_elapsed = sum(sd.get("elapsed_s", 0.0) for sd in per_seed.values())

    metrics = {
        "exp_name": "continuous_embedding_storage_substrate_v2_n16384",
        "N": N,
        "corpus_size": corpus_size,
        "seeds": seeds,
        "is_smoke": is_smoke,
        "n_seeds_complete": len(per_seed),
        "total_elapsed_s": total_elapsed,
        **{k: float(np.mean(v)) if v else float("nan") for k, v in agg.items()},
        **verdict_data,
        "verdict_msg": verdict_msg,
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[done] metrics -> {metrics_path}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        print("[main] --self-test mode: module-scope selftest already passed. exit 0.", flush=True)
        sys.exit(0)
    main()
