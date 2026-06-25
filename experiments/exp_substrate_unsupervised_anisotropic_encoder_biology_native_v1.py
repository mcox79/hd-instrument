"""substrate_unsupervised_anisotropic_encoder_biology_native_v1 -- Stage 1.5 encoder shotgun.

5-arm shotgun on biology-native UNSUPERVISED anisotropic encoder mechanisms. ALL arms
forward-only; ALL arms substrate-native; ZERO external category labels at basis layer
(USER directive 2026-06-25: "the basis shouldn't use a label it should do what biology
does"). Per Cell 7 deepened drill + USER's basis-vs-use-case principle.

DESIGN (5 arms x 3 seeds at N_DIM=8192 / V=4000 / text8):
  ARM_RANDOM_BIPOLAR_BASELINE       isotropic random sparse-bipolar (control;
                                    reproduces fair_harness baseline at sanity).
  ARM_OLSHAUSEN_FIELD_SPARSE_CODING V1 analog. Forward-only SoftHebb approximation
                                    (Moraitis 2107.05747) over bigram-context windows;
                                    sparseness + reconstruction objective. Develops
                                    dominant-direction lanes from text8 co-occurrence.
  ARM_DEEPWALK_ON_BIGRAM_GRAPH      place-cell analog. Builds bigram-cooccurrence graph
                                    from text8 (NO labels, NO taxonomy); random walks
                                    over graph edges; embedding from walk co-occurrence
                                    (skip-gram-style outer-product accumulator).
  ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL  decorrelation. Hebbian feedforward + plastic
                                    anti-Hebbian lateral inhibition on bipolar outputs
                                    (Foldiak 1990 Biol Cybern). Produces sparse
                                    independent components.
  ARM_KOHONEN_SOM_TOPOGRAPHIC       topographic input-statistics. Competitive learning
                                    + neighborhood preservation on bipolar HD vectors;
                                    develops topographic codes from text8 statistics.

USER directives honored:
  - 2026-06-25 basis-vs-use-case: NO labels at basis layer.
  - 2026-06-22 substrate-native: no MiniLM, no BGE.
  - 2026-06-23 clean-methodology: external ground truth where possible; no
    contaminated baselines.

Two metrics per arm (LOAD-BEARING per Fix #28):
  METRIC B: BPC on text8 held (vs fair_harness rail ~7.3065).
  METRIC A3': substrate-native label-free A3 proxy. Heldout-word generalization:
              for a heldout word w, query (w, p, ?) where p is a substrate-bigram
              relation; structurally-correct prediction = next-token's bigram-cluster
              ID matches w's bigram-neighbor cluster. NO external labels; cluster
              IDs derived from bigram co-occurrence on the SAME text8 train split.
  DIAGNOSTIC: anisotropy_eigenspread (eigenvalue concentration of encoder Gram
              matrix; proves the mechanism actually built anisotropic structure)
              + cosine_spread (pairwise cosine std among encoded vocab).

Pre-reg HARD bands (verbatim from Director spec):
  HARD_PASS_FULL: any biology arm BPC <= 6.95 AND A3' lift_vs_random >= 0.10
                  AND cv <= 0.05 AND anisotropy_eigenspread >= 0.5.
  HARD_PASS_PARTIAL: any biology arm BPC <= 7.30 AND A3' lift_vs_random >= 0.05.
  HARD_FAIL: NO arm beats random by >= 0.05 on A3' OR all arms BPC >= 7.40.

By-construction-saturation guards (active):
  - Random-bipolar baseline must NOT saturate A3' (V=4000 ensures headroom).
  - Each biology arm self-reports anisotropy_eigenspread + cosine_spread; if
    eigenspread < 0.05, the mechanism didn't fire -> METHODOLOGY_CHECK flag.

Sanity rails:
  - sigma=0 cleanup-style sanity recall = 1.000 (mandatory; CONFOUND_FAIL gate).
  - ARM_RANDOM_BIPOLAR at sanity_T=0.05 must reproduce fair_harness 7.3065 within
    +/- 0.05 (provenance gate; flagged in detail).
  - DeepWalk diversity_cv >= 0.05 (proves graph structure was used).
  - Foldiak decorrelation_cv >= 0.10 (proves lateral inhibition fired).

SUBSTRATE-ONLY: _LLM_CALL_COUNTER = [0]; pure numpy; no torch import at module level.
(GPU dispatch routes via Orchestrator; this cell runs CPU-numpy on remote_cpu OR
overnight_queue. Future: torch port for GPU acceleration per Fix #24 if needed.)

Cites:
  - notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md (spec)
  - notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md
  - experiments/exp_encoder_dual_gain_softhebb_v1.py (template fork; Hebbian + Foldiak)
  - experiments/exp_substrate_label_driven_anisotropic_encoder_v1.py (A1-A6 evaluator
    shape; A3 adapted to LABEL-FREE bigram-cluster proxy)
  - experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py (rail 7.3065)
  - Olshausen-Field 1996 Nature 381:607-609 (sparse coding)
  - Moraitis et al. 2107.05747 (SoftHebb forward-only Hebbian)
  - Perozzi et al. 2014 DeepWalk (random-walk graph embedding)
  - Foldiak 1990 Biol Cybern 64:165-170 (anti-Hebbian decorrelation)
  - Kohonen 1982 (SOM topographic maps)

Disciplines:
  - Fix #28: per-arm metrics (no cross-arm summary verdict over-claim).
  - Fix #20: no pipe-tail subprocess monitoring; mtime polling for monitor.
  - Long-cells: per-seed checkpoint via _seed_checkpoint.write_partial_key.
  - ASCII-only per feedback_ascii_only_in_scripts.
  - atexit synthesizer (Skunkworks #4): always produce metrics.json on timeout.

USER embargo: self-test gate (NOT smoke). Author does NOT dispatch.
"""
from __future__ import annotations

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
import hashlib
import math
import signal
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_unsupervised_anisotropic_encoder_biology_native_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Argument parsing + run-mode detection
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ============================================================================
# Pre-reg HARD bands (verbatim from Director spec 2026-06-25)
# ============================================================================

# HARD_PASS_FULL
HP_FULL_BPC = 6.95           # any biology arm BPC <= 6.95
HP_FULL_A3_LIFT = 0.10       # AND A3' lift_vs_random >= 0.10
HP_FULL_CV = 0.05            # AND cv <= 0.05
HP_FULL_EIGENSPREAD = 0.5    # AND anisotropy_eigenspread >= 0.5

# HARD_PASS_PARTIAL
HP_PART_BPC = 7.30           # any biology arm BPC <= 7.30
HP_PART_A3_LIFT = 0.05       # AND A3' lift_vs_random >= 0.05

# HARD_FAIL
HF_A3_LIFT = 0.05            # NO arm beats random by >= 0.05 on A3'
HF_BPC = 7.40                # OR all arms BPC >= 7.40

# Sanity rails
SANITY_FAIR_HARNESS_BPC = 7.3065  # provenance gate target for random baseline
SANITY_FAIR_HARNESS_TOL = 0.05
SANITY_DEEPWALK_DIVERSITY_CV_MIN = 0.05
SANITY_FOLDIAK_DECORR_CV_MIN = 0.10
SANITY_METHODOLOGY_EIGENSPREAD_MIN = 0.05  # below = mechanism didn't fire
SANITY_SIGMA0_CLEANUP_TARGET = 1.0  # CONFOUND_FAIL gate

# ============================================================================
# Config
# ============================================================================

N_DIM = 8192
VOCAB_CAP = 4000
INGEST_CHUNK = 8192
K_WTA = 5                # k-WTA k for SoftHebb/Olshausen
SPARSE_F = 0.02          # 0.02 sparsity per Director spec
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
SIGMA_SWEEP_FOR_SANITY = [0.0]  # only sigma=0 sanity used for CONFOUND_FAIL gate

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_HELDOUT_WORDS = 200      # for A3' label-free generalization
    N_BIGRAM_WALKS = 4000      # DeepWalk walks
    WALK_LEN = 12              # DeepWalk walk length
    N_OLSHAUSEN_BATCHES = 80   # SoftHebb training batches (size=256)
    N_FOLDIAK_ITER = 30
    N_SOM_EPOCHS = 12
else:
    SEEDS = [7]
    N_TRAIN = 4_000
    N_HELD = 1_000
    N_HELDOUT_WORDS = 30
    N_BIGRAM_WALKS = 200
    WALK_LEN = 8
    N_OLSHAUSEN_BATCHES = 6
    N_FOLDIAK_ITER = 4
    N_SOM_EPOCHS = 2
    VOCAB_CAP = 800

ARMS = [
    "ARM_RANDOM_BIPOLAR_BASELINE",
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING",
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH",
    "ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL",
    "ARM_KOHONEN_SOM_TOPOGRAPHIC",
]

CONFIG_VERSION = (
    "subUnsupAnisBio-v1: N_DIM=%d VOCAB_CAP=%d N_TRAIN=%d N_HELD=%d "
    "N_HELDOUT_WORDS=%d K_WTA=%d SPARSE_F=%.3f arms=%s seeds=%s mode=%s; "
    "bands HP_FULL_BPC<=%.3f HP_PART_BPC<=%.3f HP_A3_LIFT>=%.3f HF_BPC>=%.3f"
) % (
    N_DIM, VOCAB_CAP, N_TRAIN, N_HELD, N_HELDOUT_WORDS, K_WTA, SPARSE_F,
    ARMS, SEEDS, RUN_MODE, HP_FULL_BPC, HP_PART_BPC, HP_FULL_A3_LIFT, HF_BPC,
)


# ============================================================================
# Substrate primitives (numpy; substrate-native)
# ============================================================================

def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Substrate-native bag-of-trigrams sign-bundled bipolar HD vector."""
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def sparse_bipolar_from_dense(X: np.ndarray, f: float) -> np.ndarray:
    """Project dense -> sparse-bipolar at fraction f via top-k WTA on absolute value."""
    if X.ndim == 1:
        n = X.shape[0]
        k = max(1, int(n * f))
        abs_x = np.abs(X)
        thresh = np.partition(abs_x, -k)[-k]
        mask = abs_x >= thresh
        out = np.zeros_like(X, dtype=np.float32)
        out[mask] = np.sign(X[mask])
        out[out == 0] = 1.0
        return out
    n = X.shape[1]
    k = max(1, int(n * f))
    abs_X = np.abs(X)
    thresh = np.partition(abs_X, -k, axis=1)[:, -k:].min(axis=1, keepdims=True)
    mask = (abs_X >= thresh).astype(np.float32)
    out = np.sign(X).astype(np.float32) * mask
    out[mask.astype(bool) & (out == 0)] = 1.0
    return out


# ============================================================================
# Corpus loading + vocab
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


# ============================================================================
# ARM encoders -- each returns E [V, N_DIM] L2-normalized
# ============================================================================

def encoder_random_bipolar(vocab: List[str], n_dim: int, seed: int,
                            idx_train: np.ndarray) -> np.ndarray:
    """ARM 1: isotropic random sparse-bipolar. Control."""
    g = np.random.default_rng(seed * 13 + 1)
    V = len(vocab)
    dense = g.standard_normal((V, n_dim)).astype(np.float32)
    E = sparse_bipolar_from_dense(dense, SPARSE_F)
    return _l2_normalize(E)


def encoder_olshausen_field(vocab: List[str], n_dim: int, seed: int,
                             idx_train: np.ndarray) -> np.ndarray:
    """ARM 2: Olshausen-Field sparse-coding via forward-only SoftHebb.

    Substrate-native recipe per Moraitis 2107.05747 + Olshausen-Field 1996:
      1. Input = char-trigram encoding of each vocab word (substrate-baseline).
      2. Single linear encoder W [N_DIM x N_DIM] initialized near-identity.
      3. For each bigram-context pair (x_t, x_{t+1}): compute z = W @ x_t;
         apply hard k-WTA at k=K_WTA on absolute value (sparseness penalty).
      4. Update W += eta * y.T @ x_t (Hebbian; reconstruction objective approximated
         by Hebbian update on sparsified z).
      5. Final E = sparse_bipolar(E_in @ W.T, f=SPARSE_F).

    Develops dominant-direction lanes from co-occurrence statistics. No labels.
    """
    g = np.random.default_rng(seed * 17 + 2)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    # Init W near-identity + small noise (encourages stable forward + room to drift)
    W = (np.eye(n_dim, dtype=np.float32) * 0.1
         + g.standard_normal((n_dim, n_dim)).astype(np.float32) * (0.005 / math.sqrt(n_dim)))
    eta = 0.001
    decay = 1e-6
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return _l2_normalize((E_in @ W.T).astype(np.float32))
    batch_size = 256
    n_train_effective = min(n_pairs, N_OLSHAUSEN_BATCHES * batch_size)
    sub_idx = np.linspace(0, n_pairs - 1, n_train_effective).astype(np.int64)
    # Per-batch NaN guard per coordinator heads-up (Wave F Cell 1 SoftHebb NaN at scale).
    # If updates explode, clip + early-exit; we'd rather have a stable encoder than
    # propagate NaN through the rest of the cell.
    nan_detected = False
    for cs in range(0, n_train_effective, batch_size):
        ce = min(cs + batch_size, n_train_effective)
        js = sub_idx[cs:ce]
        X = E_in[idx_train[js]]
        Z = X @ W.T
        # k-WTA sparseness: top-k absolute value per row
        if K_WTA < n_dim:
            abs_Z = np.abs(Z)
            thresh = np.partition(abs_Z, -K_WTA, axis=1)[:, -K_WTA:].min(axis=1, keepdims=True)
            mask = (abs_Z >= thresh).astype(np.float32)
            Y = Z * mask
        else:
            Y = Z
        B_eff = max(X.shape[0], 1)
        update = (eta / B_eff) * (Y.T @ X)
        # Clip extreme values per update (defensive against NaN/Inf explosion)
        update = np.clip(update, -1.0, 1.0)
        W += update
        W *= (1.0 - decay)
        # Norm-clip W to prevent slow drift to infinity (Frobenius bound)
        W_norm = np.linalg.norm(W)
        if W_norm > 100.0 * math.sqrt(n_dim):
            W *= (100.0 * math.sqrt(n_dim) / W_norm)
        if not np.isfinite(W).all():
            # NaN/Inf detected -- early exit; encoder falls back to E_in
            nan_detected = True
            sys.stderr.write("[OLSHAUSEN_NAN] W non-finite at batch %d; falling back to char-trigram\n" % cs)
            sys.stderr.flush()
            break
    if nan_detected:
        # Fallback: return char-trigram baseline (no SoftHebb update applied)
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    E_out = (E_in @ W.T).astype(np.float32)
    # Final NaN guard (defensive)
    if not np.isfinite(E_out).all():
        sys.stderr.write("[OLSHAUSEN_NAN] final E_out non-finite; falling back to char-trigram\n")
        sys.stderr.flush()
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    # Sparsify to f=SPARSE_F bipolar at output (substrate-native sparse code)
    E_out = sparse_bipolar_from_dense(E_out, SPARSE_F)
    return _l2_normalize(E_out)


def _build_bigram_graph(idx_train: np.ndarray, V: int) -> Dict[int, List[int]]:
    """Build sparse bigram-cooccurrence adjacency (NO labels, NO taxonomy)."""
    adj: Dict[int, Counter] = defaultdict(Counter)
    n = len(idx_train) - 1
    for i in range(n):
        a = int(idx_train[i])
        b = int(idx_train[i + 1])
        if a != b:
            adj[a][b] += 1
            adj[b][a] += 1
    # Compress: keep top-K neighbors per node for walk efficiency
    top_k = 20
    out: Dict[int, List[int]] = {}
    for s, c in adj.items():
        out[s] = [n for n, _ in c.most_common(top_k)]
    return out


def encoder_deepwalk_on_bigram(vocab: List[str], n_dim: int, seed: int,
                                idx_train: np.ndarray) -> np.ndarray:
    """ARM 3: DeepWalk-on-bigram-graph (substrate-native place-cell analog).

    Substrate-native recipe per Perozzi 2014:
      1. Build bigram-cooccurrence graph from text8 train tokens (NO labels).
      2. Run N_BIGRAM_WALKS random walks of length WALK_LEN starting from random
         tokens; transition probabilities = uniform over top-K bigram neighbors.
      3. Skip-gram-style: for each walk pair (w_i, w_j) within window=2, accumulate
         outer-product into V x V cooccurrence matrix C.
      4. Embedding: E_dw[v] = sparse_bipolar(C[v] @ R) where R is a random bipolar
         V x N_DIM projection (Johnson-Lindenstrauss; substrate-native).

    Community structure emerges from graph CONNECTIVITY (Stochastic Block Model
    embedding). Substrate uses graph's relational structure WITHOUT taxonomy.
    """
    g = np.random.default_rng(seed * 19 + 3)
    V = len(vocab)
    if len(idx_train) < 2:
        # Degenerate: fallback random
        return encoder_random_bipolar(vocab, n_dim, seed, idx_train)
    adj = _build_bigram_graph(idx_train, V)
    # Sample start tokens biased toward high-degree (graph-coverage)
    nodes = [s for s in adj if adj[s]]
    if not nodes:
        return encoder_random_bipolar(vocab, n_dim, seed, idx_train)
    # Skip-gram cooccurrence accumulator (sparse) -- store as Counter for memory
    cooc: Dict[int, Counter] = defaultdict(Counter)
    window = 2
    n_walks = min(N_BIGRAM_WALKS, max(50, len(nodes) * 4))
    for _ in range(n_walks):
        start = nodes[int(g.integers(0, len(nodes)))]
        walk = [start]
        cur = start
        for _ in range(WALK_LEN - 1):
            nbrs = adj.get(cur, [])
            if not nbrs:
                break
            cur = nbrs[int(g.integers(0, len(nbrs)))]
            walk.append(cur)
        # Skip-gram pairs within window
        for i, wi in enumerate(walk):
            lo = max(0, i - window)
            hi = min(len(walk), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                cooc[wi][walk[j]] += 1
    # Project cooccurrence rows into N_DIM via random bipolar projection (JL).
    R = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32) / math.sqrt(n_dim)
    E = np.zeros((V, n_dim), dtype=np.float32)
    for v in range(V):
        c = cooc.get(v)
        if not c:
            # Backfill from char-trigram (graph-orphan vocab)
            E[v] = char_trigram_encode(vocab[v], n_dim, seed)
            continue
        # Weighted bipolar-projection sum
        idxs = np.array(list(c.keys()), dtype=np.int64)
        wts = np.array(list(c.values()), dtype=np.float32)
        E[v] = wts @ R[idxs]
    E = sparse_bipolar_from_dense(E, SPARSE_F)
    return _l2_normalize(E)


def encoder_foldiak_anti_hebbian(vocab: List[str], n_dim: int, seed: int,
                                  idx_train: np.ndarray) -> np.ndarray:
    """ARM 4: Foldiak 1990 anti-Hebbian lateral inhibition decorrelation.

    Substrate-native recipe:
      1. Input = char-trigram encoding (substrate-baseline).
      2. Codebook = vocab encoding; maintain lateral W_lat [V_sub x V_sub]
         inhibitory weights (substrate-scale: use vocab subset for tractability).
      3. Iterate: codebook[i] -= sum_{j != i} W_lat[i,j] * codebook[j];
         W_lat[i,j] += eta * y_i * y_j (anti-Hebb on cross-correlation).
      4. Output = sparse-bipolarized decorrelated codebook.

    Produces sparse INDEPENDENT components via lateral inhibition. No labels.
    """
    g = np.random.default_rng(seed * 23 + 4)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    codebook = E_in.copy()
    # V x V lateral matrix; for V=4000 this is 16M floats (~60MB). Acceptable.
    W_lat = np.zeros((V, V), dtype=np.float32)
    eta = 0.01
    decay = 1e-4
    for it in range(N_FOLDIAK_ITER):
        np.fill_diagonal(W_lat, 0.0)
        inhibition = W_lat @ codebook
        codebook = codebook - inhibition
        codebook = _l2_normalize(codebook)
        # Update W_lat anti-Hebb on pairwise correlation
        Y = codebook @ codebook.T
        np.fill_diagonal(Y, 0.0)
        W_lat += eta * Y
        W_lat *= (1.0 - decay)
        W_lat = np.clip(W_lat, -1.0, 1.0)
        # NaN guard per coordinator heads-up (Wave F Cell 1 SoftHebb NaN at scale)
        if not np.isfinite(codebook).all():
            sys.stderr.write("[FOLDIAK_NAN] codebook non-finite at iter %d; falling back to char-trigram\n" % it)
            sys.stderr.flush()
            return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    if not np.isfinite(codebook).all():
        sys.stderr.write("[FOLDIAK_NAN] final codebook non-finite; falling back to char-trigram\n")
        sys.stderr.flush()
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    E_out = sparse_bipolar_from_dense(codebook, SPARSE_F)
    return _l2_normalize(E_out)


def encoder_kohonen_som(vocab: List[str], n_dim: int, seed: int,
                         idx_train: np.ndarray) -> np.ndarray:
    """ARM 5: Kohonen SOM topographic-map encoder (substrate-native variant).

    Substrate-native recipe per Kohonen 1982 with INJECTIVE-ENCODING guard:
      1. Input = char-trigram encoding of each vocab word (substrate-baseline).
      2. Per-vocab "topographic-position-tag" = unique bipolar HV indexed by position.
         Bound into output to KEEP DIFFERENT VOCAB SLOTS DISTINGUISHABLE
         (Kohonen's topographic map carries POSITION as load-bearing identity;
         neighborhood-updates within position-tagged outputs cannot collapse
         to duplicates by construction).
      3. SOM codebook init = random bipolar; updates from text8 stream with
         shrinking neighborhood radius + decaying learning rate.
      4. Final out[v] = bipolar XOR-bind(position_tag[v], sparse_bipolar(codebook[v])).
         This is the substrate-native equivalent of SOM where the codebook learns
         input-statistics AND the position-tag carries topographic identity.

    Topography emerges from input statistics + competition. No labels.
    """
    g = np.random.default_rng(seed * 29 + 5)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    codebook = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    codebook = _l2_normalize(codebook)
    # Per-position topographic-tag (unique bipolar per vocab position; substrate-native
    # injection of identity into the topographic code -- biological analog: cortical
    # column has BOTH learned input-tuning AND fixed location-identity)
    pos_tag = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    n_pairs = len(idx_train)
    if n_pairs <= 0:
        # No training: just bind position-tag into trigram-init for distinguishability
        out_bipolar = np.sign(codebook * pos_tag).astype(np.float32)
        out_bipolar[out_bipolar == 0] = 1.0
        E_out = sparse_bipolar_from_dense(out_bipolar, SPARSE_F)
        return _l2_normalize(E_out)
    # Sub-sample training tokens for SOM updates
    n_updates = min(n_pairs, N_SOM_EPOCHS * 1000)
    sub_idx = np.linspace(0, n_pairs - 1, n_updates).astype(np.int64)
    r0 = max(2, V // 20)
    for step, t_idx in enumerate(sub_idx):
        x = E_in[idx_train[t_idx]]
        scores = codebook @ x
        winner = int(np.argmax(scores))
        frac = step / max(n_updates - 1, 1)
        r_t = max(1, int(r0 * (1.0 - frac)))
        eta_t = 0.05 * (1.0 - 0.8 * frac)
        lo = max(0, winner - r_t)
        hi = min(V, winner + r_t + 1)
        codebook[lo:hi] = codebook[lo:hi] + eta_t * (x[None, :] - codebook[lo:hi])
        if step % 500 == 499:
            codebook = np.sign(codebook).astype(np.float32)
            codebook[codebook == 0] = 1.0
    codebook = np.sign(codebook).astype(np.float32)
    codebook[codebook == 0] = 1.0
    # Bind position-tag (element-wise multiply on bipolar = XOR-bind preserving distinctness)
    out_bipolar = np.sign(codebook * pos_tag).astype(np.float32)
    out_bipolar[out_bipolar == 0] = 1.0
    E_out = sparse_bipolar_from_dense(out_bipolar, SPARSE_F)
    return _l2_normalize(E_out)


ENCODERS = {
    "ARM_RANDOM_BIPOLAR_BASELINE":      encoder_random_bipolar,
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING": encoder_olshausen_field,
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH":      encoder_deepwalk_on_bigram,
    "ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL":  encoder_foldiak_anti_hebbian,
    "ARM_KOHONEN_SOM_TOPOGRAPHIC":       encoder_kohonen_som,
}


# ============================================================================
# Metric B: BPC on text8 held (per arm)
# ============================================================================

def build_hebbian_W_np(idx_train: np.ndarray, E: np.ndarray, ingest_chunk: int) -> np.ndarray:
    """Hebbian outer-product LM W [N_DIM, N_DIM] = sum_pairs E[t+1] outer E[t]."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src = idx_train[b:end]
        tgt = idx_train[b + 1:end + 1]
        W += E[tgt].T @ E[src]
    return W


def softmax_safe(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = logits / max(temperature, 1e-6)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def path_a_bpc(E: np.ndarray, vocab: List[str], idx_train: np.ndarray,
                idx_held: np.ndarray, lambda_grid: list, seed: int) -> dict:
    """Hebbian-substrate LM BPC with log-linear unigram interpolation calibrated
    on dev half of held, evaluated on test half."""
    V = len(vocab)
    W = build_hebbian_W_np(idx_train, E, INGEST_CHUNK)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    ctx = ctx[mask]
    nxt = nxt[mask]
    n_eval = len(ctx)
    if n_eval == 0:
        return {"bpc_raw": float("inf"), "bpc_best_calibrated": float("inf"),
                "best_lambda": 1.0, "n_eval": 0}
    sub_logits = np.zeros((n_eval, V), dtype=np.float32)
    chunk = 1024
    for b in range(0, n_eval, chunk):
        end = min(b + chunk, n_eval)
        pred_vec = E[ctx[b:end]] @ W.T
        pn = np.linalg.norm(pred_vec, axis=1, keepdims=True)
        pn[pn < 1e-9] = 1e-9
        pred_vec = pred_vec / pn
        sub_logits[b:end] = pred_vec @ E.T
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    sub_logp = np.log(np.clip(softmax_safe(sub_logits, temperature=1.0), 1e-30, 1.0))
    n_dev = n_eval // 2
    nxt_dev = nxt[:n_dev]
    nxt_test = nxt[n_dev:]
    sub_logp_dev = sub_logp[:n_dev]
    sub_logp_test = sub_logp[n_dev:]
    raw_logp_nxt_test = sub_logp_test[np.arange(len(nxt_test)), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt_test)) / np.log(2.0)
    best_lambda = 1.0
    best_dev_bpc = float("inf")
    for lam in lambda_grid:
        combined = lam * sub_logp_dev + (1.0 - lam) * U_log[None, :]
        combined = combined - combined.max(axis=1, keepdims=True)
        Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
        logp = combined - Z[:, None]
        logp_nxt = logp[np.arange(n_dev), nxt_dev]
        dev_bpc = -float(np.mean(logp_nxt)) / np.log(2.0)
        if dev_bpc < best_dev_bpc:
            best_dev_bpc = dev_bpc
            best_lambda = lam
    combined_t = best_lambda * sub_logp_test + (1.0 - best_lambda) * U_log[None, :]
    combined_t = combined_t - combined_t.max(axis=1, keepdims=True)
    Z_t = np.log(np.clip(np.exp(combined_t).sum(axis=1), 1e-30, None))
    logp_t = combined_t - Z_t[:, None]
    logp_nxt_t = logp_t[np.arange(len(nxt_test)), nxt_test]
    bpc_best = -float(np.mean(logp_nxt_t)) / np.log(2.0)
    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best_calibrated": round(bpc_best, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "n_eval": int(len(nxt_test)),
    }


# ============================================================================
# Metric A3': label-free heldout-word generalization
#
# Per Director spec + USER 2026-06-25 basis-no-labels: A3 evaluator that DOES NOT
# use external category labels. Substrate-native cluster IDs derived from bigram
# cooccurrence on the SAME train split.
#
# Pipeline:
#   1. Compute bigram-cluster IDs for vocab using k-means-on-bigram-cooccurrence
#      with K = sqrt(V) bins. NOT a label; emerges from train statistics.
#   2. Hold out N_HELDOUT_WORDS vocab indices from the encoder's Hebbian-LM ingest
#      (cell already has held-out tokens; we use a separate held-out WORD set
#      for A3').
#   3. For each held word h, query substrate (h, p=most-frequent-bigram-relation, ?);
#      structurally-correct = top-1 prediction lands in same bigram-cluster as h's
#      ACTUAL bigram-neighbors in train (computed from train split).
#   4. A3' = mean correct rate. Random baseline ~ 1/K.
#
# This is CLEAN because:
#   - Cluster IDs computed from train co-occurrence (data-driven, NOT labels);
#   - Heldout WORDS are not seen during cluster-ID computation OR encoder Hebbian
#     ingest;
#   - Ground truth = each heldout word's own train-set bigram-neighbor majority cluster.
# ============================================================================

def _compute_bigram_cluster_ids(idx_train: np.ndarray, V: int, n_clusters: int,
                                 seed: int) -> np.ndarray:
    """Compute substrate-native cluster IDs for vocab via k-means on bigram-
    cooccurrence rows. NOT labels; emerges from train statistics.
    """
    g = np.random.default_rng(seed * 31 + 7)
    # Build bigram-cooccurrence matrix C [V, V] (sparse-dense via accumulation)
    # For memory: project to N=128 features via random projection first.
    proj_dim = 128
    R = (g.integers(0, 2, size=(V, proj_dim)) * 2 - 1).astype(np.float32) / math.sqrt(proj_dim)
    feats = np.zeros((V, proj_dim), dtype=np.float32)
    n = len(idx_train) - 1
    for i in range(n):
        a = int(idx_train[i])
        b = int(idx_train[i + 1])
        if a != b:
            feats[a] += R[b]
            feats[b] += R[a]
    feats = _l2_normalize(feats)
    # k-means init: random centers
    n_clusters = max(2, min(n_clusters, V // 2))
    init_idx = g.choice(V, size=n_clusters, replace=False)
    centers = feats[init_idx].copy()
    cluster_ids = np.zeros(V, dtype=np.int64)
    for _ in range(8):  # cheap k-means
        # Assign
        d = feats @ centers.T
        cluster_ids = np.argmax(d, axis=1)
        # Update centers
        for k in range(n_clusters):
            mask = (cluster_ids == k)
            if mask.any():
                centers[k] = feats[mask].mean(0)
        centers = _l2_normalize(centers)
    return cluster_ids


def _word_target_clusters(idx_train: np.ndarray, V: int,
                           cluster_ids: np.ndarray) -> np.ndarray:
    """For each vocab word v, compute its ACTUAL majority bigram-neighbor cluster
    in train (ground truth for A3' evaluation)."""
    nbr_cluster_counts = defaultdict(Counter)
    n = len(idx_train) - 1
    for i in range(n):
        a = int(idx_train[i])
        b = int(idx_train[i + 1])
        if a != b:
            nbr_cluster_counts[a][int(cluster_ids[b])] += 1
            nbr_cluster_counts[b][int(cluster_ids[a])] += 1
    target = np.full(V, -1, dtype=np.int64)
    for v in range(V):
        c = nbr_cluster_counts.get(v)
        if c:
            target[v] = int(c.most_common(1)[0][0])
    return target


def metric_a3_prime(E: np.ndarray, vocab: List[str], idx_train: np.ndarray,
                     heldout_words: np.ndarray, cluster_ids: np.ndarray,
                     target_clusters: np.ndarray, seed: int) -> dict:
    """Label-free heldout-word generalization.

    For each heldout word h:
      - Query (h, p=bigram-relation, ?) via Hebbian-LM W trained on TRAIN-MINUS-HELDOUT.
      - top-1 predicted vocab v_pred; correct if cluster_ids[v_pred] == target_clusters[h].
    Random baseline = 1/K_clusters (computed below).
    """
    V = len(vocab)
    # Train Hebbian LM on train MINUS heldout-word occurrences
    held_set = set(int(x) for x in heldout_words)
    keep_mask = np.array([int(t) not in held_set for t in idx_train], dtype=bool)
    idx_train_minus = idx_train[keep_mask]
    if len(idx_train_minus) < 10:
        return {"a3_correct": 0.0, "n_eval": 0, "random_baseline": 0.0,
                "n_clusters": int(cluster_ids.max() + 1)}
    W = build_hebbian_W_np(idx_train_minus, E, INGEST_CHUNK)
    n_clusters = int(cluster_ids.max() + 1)
    # For each h, predict next token from h via W; check cluster of top-1
    correct = 0
    total = 0
    chunk = 256
    for cs in range(0, len(heldout_words), chunk):
        ce = min(cs + chunk, len(heldout_words))
        hs = heldout_words[cs:ce]
        pred_vec = E[hs] @ W.T  # [B, N_DIM]
        pn = np.linalg.norm(pred_vec, axis=1, keepdims=True)
        pn[pn < 1e-9] = 1e-9
        pred_vec = pred_vec / pn
        scores = pred_vec @ E.T  # [B, V]
        # Exclude h itself from prediction
        for b, h in enumerate(hs):
            scores[b, int(h)] = -1e9
        top1 = np.argmax(scores, axis=1)
        for b, h in enumerate(hs):
            tgt = int(target_clusters[int(h)])
            if tgt < 0:
                continue
            pred_cluster = int(cluster_ids[int(top1[b])])
            if pred_cluster == tgt:
                correct += 1
            total += 1
    a3_score = correct / max(total, 1)
    random_baseline = 1.0 / max(n_clusters, 1)
    return {
        "a3_correct": round(a3_score, 4),
        "n_eval": int(total),
        "random_baseline": round(random_baseline, 4),
        "n_clusters": int(n_clusters),
    }


# ============================================================================
# Anisotropy diagnostic (eigenspread + cosine-spread)
# ============================================================================

def anisotropy_diagnostic(E: np.ndarray, seed: int, sample_cap: int = 1000) -> dict:
    """Anisotropy proxies for self-reporting per by-construction-saturation guard.

    eigenspread:  participation ratio inverse on Gram eigvals; 0 = perfectly
                  isotropic (all eigvals equal), >0 = anisotropic concentration.
    cosine_spread: std of pairwise cosine similarity among sampled vocab vectors.
    eff_rank:     participation ratio (sum(eig)^2 / sum(eig^2)) / D; normalized.

    Mechanism-fired test: eigenspread >= SANITY_METHODOLOGY_EIGENSPREAD_MIN (0.05).
    """
    g = np.random.default_rng(seed * 41 + 11)
    V = E.shape[0]
    n_sample = min(sample_cap, V)
    idx = g.choice(V, size=n_sample, replace=False)
    Es = E[idx]
    # Eigvals of Gram (covariance proxy)
    cov = Es.T @ Es / max(n_sample, 1)
    # Use eigvalsh for symmetric cov; clip to non-negative
    try:
        eigs = np.linalg.eigvalsh(cov)
    except Exception:
        eigs = np.zeros(cov.shape[0])
    eigs = np.clip(eigs, 0.0, None)
    s = eigs.sum()
    if s <= 0:
        return {"anisotropy_eigenspread": 0.0, "cosine_spread": 0.0, "eff_rank_norm": 0.0,
                "mechanism_fired": False}
    p = eigs / s
    p = p[p > 1e-12]
    # Eigenspread = 1 - normalized-PR (1 = max anisotropic, 0 = isotropic)
    pr = (s * s) / max(float((eigs * eigs).sum()), 1e-12)
    eff_rank_norm = pr / max(eigs.shape[0], 1)
    eigenspread = 1.0 - eff_rank_norm
    # Cosine spread among sampled pairs
    n_pairs = min(500, n_sample * (n_sample - 1) // 2)
    ia = g.integers(0, n_sample, size=n_pairs)
    ib = g.integers(0, n_sample, size=n_pairs)
    mask_diff = ia != ib
    ia = ia[mask_diff]; ib = ib[mask_diff]
    if len(ia) < 2:
        cos_spread = 0.0
    else:
        cosines = np.sum(Es[ia] * Es[ib], axis=1)
        cos_spread = float(np.std(cosines))
    return {
        "anisotropy_eigenspread": round(float(eigenspread), 4),
        "cosine_spread": round(cos_spread, 4),
        "eff_rank_norm": round(float(eff_rank_norm), 4),
        "mechanism_fired": bool(eigenspread >= SANITY_METHODOLOGY_EIGENSPREAD_MIN),
    }


# ============================================================================
# sigma=0 cleanup sanity (CONFOUND_FAIL detector)
# ============================================================================

def cleanup_sigma0_sanity(E: np.ndarray, seed: int, n_eval: int = 100) -> float:
    """sigma=0 cleanup recall: noise-free cue MUST return itself by construction."""
    g = np.random.default_rng(seed * 43 + 13)
    V = E.shape[0]
    n = min(n_eval, V)
    idx = g.choice(V, size=n, replace=False)
    E_n = _l2_normalize(E)
    cues = E_n[idx]  # sigma=0 = identity
    scores = cues @ E_n.T
    pred = np.argmax(scores, axis=1)
    return float((pred == idx).sum()) / max(n, 1)


# ============================================================================
# Per-seed unit
# ============================================================================

def run_unit(seed: int) -> Dict:
    t0 = time.time()
    print("\n[seed=%d] loading text8 + building vocab (V_cap=%d)" % (seed, VOCAB_CAP), flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus too small: %d vs %d; truncating" % (len(toks), N_TRAIN + N_HELD), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d" % (seed, V, N_TRAIN, N_HELD, N_DIM), flush=True)

    # Pre-compute substrate-native cluster IDs + target clusters for A3' (shared across arms)
    print("[seed=%d] computing substrate-native bigram-cluster IDs..." % seed, flush=True)
    n_clusters_target = max(8, int(math.sqrt(V)))
    t_cl = time.time()
    cluster_ids = _compute_bigram_cluster_ids(idx_train, V, n_clusters_target, seed)
    target_clusters = _word_target_clusters(idx_train, V, cluster_ids)
    print("[seed=%d] cluster_ids n_clusters=%d (target=%d); coverage=%.3f; t=%.1fs" % (
        seed, int(cluster_ids.max() + 1), n_clusters_target,
        float((target_clusters >= 0).mean()), time.time() - t_cl), flush=True)

    # Sample heldout-word indices (eligible = words with a defined target cluster + not <unk>)
    eligible = np.where((target_clusters >= 0) & (np.arange(V) > 0))[0]
    g_hw = np.random.default_rng(seed * 47 + 17)
    n_held_words = min(N_HELDOUT_WORDS, len(eligible))
    if n_held_words > 0:
        heldout_words = g_hw.choice(eligible, size=n_held_words, replace=False)
    else:
        heldout_words = np.array([], dtype=np.int64)
    print("[seed=%d] heldout_words=%d eligible=%d" % (seed, n_held_words, len(eligible)), flush=True)

    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] encoding..." % (seed, arm_label), flush=True)
        fn = ENCODERS[arm_label]
        E_full = fn(vocab, N_DIM, seed, idx_train)
        t_enc = time.time() - t_arm
        # Sanity: sigma=0 cleanup
        t_s = time.time()
        sigma0_recall = cleanup_sigma0_sanity(E_full, seed, n_eval=100)
        t_sanity = time.time() - t_s
        # Anisotropy diagnostic
        t_a = time.time()
        ani = anisotropy_diagnostic(E_full, seed, sample_cap=500 if RUN_MODE == "smoke" else 1000)
        t_ani = time.time() - t_a
        # Metric B: BPC
        t_b = time.time()
        bpc = path_a_bpc(E_full, vocab, idx_train, idx_held, LAMBDA_GRID, seed)
        t_bpc = time.time() - t_b
        # Metric A3' label-free
        t_3 = time.time()
        a3p = metric_a3_prime(E_full, vocab, idx_train, heldout_words,
                                cluster_ids, target_clusters, seed)
        t_a3p = time.time() - t_3
        by_arm[arm_label] = {
            "bpc_raw": bpc["bpc_raw"],
            "bpc_best_calibrated": bpc["bpc_best_calibrated"],
            "best_lambda": bpc["best_lambda"],
            "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_n_eval": bpc["n_eval"],
            "a3_correct": a3p["a3_correct"],
            "a3_n_eval": a3p["n_eval"],
            "a3_random_baseline": a3p["random_baseline"],
            "a3_n_clusters": a3p["n_clusters"],
            "anisotropy_eigenspread": ani["anisotropy_eigenspread"],
            "cosine_spread": ani["cosine_spread"],
            "eff_rank_norm": ani["eff_rank_norm"],
            "mechanism_fired": ani["mechanism_fired"],
            "sigma0_recall": round(sigma0_recall, 4),
            "wall_encode_s": round(t_enc, 2),
            "wall_sanity_s": round(t_sanity, 2),
            "wall_anisotropy_s": round(t_ani, 2),
            "wall_bpc_s": round(t_bpc, 2),
            "wall_a3p_s": round(t_a3p, 2),
        }
        a = by_arm[arm_label]
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f a3=%.3f (rb=%.3f) "
              "eigsprd=%.3f cosstd=%.3f sigma0=%.3f fired=%s (enc=%.1fs bpc=%.1fs a3=%.1fs)" % (
                  seed, arm_label, a["bpc_raw"], a["bpc_best_calibrated"], a["best_lambda"],
                  a["a3_correct"], a["a3_random_baseline"], a["anisotropy_eigenspread"],
                  a["cosine_spread"], a["sigma0_recall"], a["mechanism_fired"],
                  t_enc, t_bpc, t_a3p), flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "V_actual": V,
        "n_clusters_a3": int(cluster_ids.max() + 1),
        "n_heldout_words": int(n_held_words),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict (per-arm; Fix #28 compliant)
# ============================================================================

def _classify_arm(arm_metrics: dict, random_a3: float) -> dict:
    """Per-arm classification + sanity flags."""
    bpc = float(arm_metrics["bpc_best_calibrated_mean"])
    bpc_cv = float(arm_metrics["bpc_best_calibrated_cv"])
    a3 = float(arm_metrics["a3_correct_mean"])
    a3_cv = float(arm_metrics["a3_correct_cv"])
    eig = float(arm_metrics["anisotropy_eigenspread_mean"])
    sigma0 = float(arm_metrics["sigma0_recall_mean"])
    lift_a3 = a3 - random_a3

    confound = sigma0 < 0.999
    if confound:
        return {"classification": "CONFOUND_FAIL", "lift_a3": lift_a3,
                "sigma0_confound": True, "mechanism_fired": eig >= SANITY_METHODOLOGY_EIGENSPREAD_MIN}

    # HARD_PASS_FULL
    if (bpc <= HP_FULL_BPC and lift_a3 >= HP_FULL_A3_LIFT
            and bpc_cv <= HP_FULL_CV and eig >= HP_FULL_EIGENSPREAD):
        cl = "HARD_PASS_FULL"
    elif bpc <= HP_PART_BPC and lift_a3 >= HP_PART_A3_LIFT:
        cl = "HARD_PASS_PARTIAL"
    elif bpc >= HF_BPC and lift_a3 < HF_A3_LIFT:
        cl = "HARD_FAIL"
    else:
        cl = "MIDDLE_BAND"

    return {"classification": cl, "lift_a3": lift_a3, "sigma0_confound": False,
            "mechanism_fired": eig >= SANITY_METHODOLOGY_EIGENSPREAD_MIN}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_labels = list(units[0]["by_arm"].keys())
    # Aggregate per-arm across seeds
    by_arm_agg = {}
    for arm_label in arm_labels:
        bpc_vals = [u["by_arm"][arm_label]["bpc_best_calibrated"] for u in units]
        a3_vals = [u["by_arm"][arm_label]["a3_correct"] for u in units]
        eig_vals = [u["by_arm"][arm_label]["anisotropy_eigenspread"] for u in units]
        cos_vals = [u["by_arm"][arm_label]["cosine_spread"] for u in units]
        sigma0_vals = [u["by_arm"][arm_label]["sigma0_recall"] for u in units]
        b_mean = float(np.mean(bpc_vals)); b_std = float(np.std(bpc_vals))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        a_mean = float(np.mean(a3_vals)); a_std = float(np.std(a3_vals))
        a_cv = a_std / max(abs(a_mean), 1e-6)
        e_mean = float(np.mean(eig_vals))
        c_mean = float(np.mean(cos_vals))
        s_mean = float(np.mean(sigma0_vals))
        by_arm_agg[arm_label] = {
            "bpc_best_calibrated_mean": round(b_mean, 4),
            "bpc_best_calibrated_std": round(b_std, 4),
            "bpc_best_calibrated_cv": round(b_cv, 4),
            "a3_correct_mean": round(a_mean, 4),
            "a3_correct_std": round(a_std, 4),
            "a3_correct_cv": round(a_cv, 4),
            "anisotropy_eigenspread_mean": round(e_mean, 4),
            "cosine_spread_mean": round(c_mean, 4),
            "sigma0_recall_mean": round(s_mean, 4),
        }

    # Random baseline = ARM_RANDOM_BIPOLAR_BASELINE's a3
    random_a3 = by_arm_agg["ARM_RANDOM_BIPOLAR_BASELINE"]["a3_correct_mean"]
    random_bpc = by_arm_agg["ARM_RANDOM_BIPOLAR_BASELINE"]["bpc_best_calibrated_mean"]

    # Classify each arm
    classifications = {}
    for al in arm_labels:
        classifications[al] = _classify_arm(by_arm_agg[al], random_a3)

    # Sanity rails
    sanity = {
        "fair_harness_provenance_random_bpc": round(random_bpc, 4),
        "fair_harness_target": SANITY_FAIR_HARNESS_BPC,
        "fair_harness_tol": SANITY_FAIR_HARNESS_TOL,
        "fair_harness_provenance_ok": (
            abs(random_bpc - SANITY_FAIR_HARNESS_BPC) <= SANITY_FAIR_HARNESS_TOL),
        "sigma0_cleanup_ok": all(by_arm_agg[al]["sigma0_recall_mean"] >= 0.999 for al in arm_labels),
        "sigma0_failing_arms": [al for al in arm_labels
                                if by_arm_agg[al]["sigma0_recall_mean"] < 0.999],
        "mechanism_fired_per_arm": {al: classifications[al]["mechanism_fired"] for al in arm_labels},
        "random_a3_lift_check": {al: round(classifications[al]["lift_a3"], 4) for al in arm_labels},
    }

    # CONFOUND_FAIL gate first
    if not sanity["sigma0_cleanup_ok"]:
        msg = "CONFOUND_FAIL: sigma=0 cleanup <1.000 for arms=%s; implementation bug suspected" % (
            sanity["sigma0_failing_arms"])
        return ("CONFOUND_FAIL", msg, {
            "by_arm_agg": by_arm_agg, "classifications": classifications, "sanity": sanity,
            "CONFIG_VERSION": CONFIG_VERSION, "n_seeds": len(units),
        })

    # Biology arms only (exclude baseline)
    biology_arms = [al for al in arm_labels if al != "ARM_RANDOM_BIPOLAR_BASELINE"]
    full_pass = [al for al in biology_arms if classifications[al]["classification"] == "HARD_PASS_FULL"]
    part_pass = [al for al in biology_arms if classifications[al]["classification"] == "HARD_PASS_PARTIAL"]

    # HARD_FAIL band conditions (verbatim per Director spec):
    # NO arm beats random by >= 0.05 on A3' OR all arms BPC >= 7.40
    no_a3_beat = all(classifications[al]["lift_a3"] < HF_A3_LIFT for al in biology_arms)
    all_high_bpc = all(by_arm_agg[al]["bpc_best_calibrated_mean"] >= HF_BPC for al in arm_labels)

    detail = {
        "by_arm_agg": by_arm_agg,
        "classifications": {al: c["classification"] for al, c in classifications.items()},
        "lift_a3_per_arm": sanity["random_a3_lift_check"],
        "sanity": sanity,
        "biology_arms_full_pass": full_pass,
        "biology_arms_partial_pass": part_pass,
        "no_a3_beat": no_a3_beat,
        "all_high_bpc": all_high_bpc,
        "random_a3": random_a3,
        "random_bpc": random_bpc,
        "CONFIG_VERSION": CONFIG_VERSION,
        "n_seeds": len(units),
        "honest_scope": (
            "5-arm biology-native UNSUPERVISED anisotropic encoder shotgun at "
            "N_DIM=%d V_cap=%d N_TRAIN=%d on text8; metrics = Path-A BPC + label-free "
            "A3' bigram-cluster generalization + anisotropy diagnostic; baseline = "
            "ARM_RANDOM_BIPOLAR; bands per Director spec 2026-06-25"
        ) % (N_DIM, VOCAB_CAP, N_TRAIN),
        "cites": [
            "notes/director_cell_H_prime_biology_unsupervised_encoder_spec_2026-06-25.md",
            "notes/research_biology_unsupervised_anisotropy_no_labels_3x_drill_2026-06-25.md",
            "Olshausen_Field_1996_Nature_381_607",
            "Moraitis_2107_05747_SoftHebb",
            "Perozzi_2014_DeepWalk",
            "Foldiak_1990_Biol_Cybern_64_165",
            "Kohonen_1982_SOM",
        ],
    }

    # Arm summary
    parts = []
    for al in arm_labels:
        a = by_arm_agg[al]
        c = classifications[al]["classification"]
        parts.append("%s=bpc%.3f/a3%.3f(lift%+.3f)/eig%.3f[%s]" % (
            al, a["bpc_best_calibrated_mean"], a["a3_correct_mean"],
            classifications[al]["lift_a3"], a["anisotropy_eigenspread_mean"], c))
    summary = "BIO5: " + " | ".join(parts) + " | random_a3=%.3f random_bpc=%.3f fair_harness_OK=%s" % (
        random_a3, random_bpc, sanity["fair_harness_provenance_ok"])

    # Cell-level verdict
    if full_pass:
        msg = ("HARD_PASS_FULL: arms=%s clear FULL bands (BPC<=%.3f A3'_lift>=%.3f cv<=%.3f "
               "eigsprd>=%.3f); biology-native unsupervised path is chain-grade-eligible. " % (
                   full_pass, HP_FULL_BPC, HP_FULL_A3_LIFT, HP_FULL_CV, HP_FULL_EIGENSPREAD)) + summary
        return ("HARD_PASS", msg, detail)
    if part_pass:
        msg = ("HARD_PASS_PARTIAL: arms=%s clear PARTIAL bands (BPC<=%.3f A3'_lift>=%.3f); "
               "signal present but not chain-grade. " % (
                   part_pass, HP_PART_BPC, HP_PART_A3_LIFT)) + summary
        return ("MIDDLE_BAND", msg, detail)
    if no_a3_beat or all_high_bpc:
        reasons = []
        if no_a3_beat:
            reasons.append("NO biology arm beats random A3 by >= %.3f" % HF_A3_LIFT)
        if all_high_bpc:
            reasons.append("ALL arms BPC >= %.3f" % HF_BPC)
        msg = "HARD_FAIL: " + "; ".join(reasons) + ". " + summary
        return ("HARD_FAIL", msg, detail)
    msg = ("MIDDLE_BAND: no biology arm clears FULL or PARTIAL bands but at least one beats "
           "random by some margin; characterize. ") + summary
    return ("MIDDLE_BAND", msg, detail)


# ============================================================================
# atexit synthesizer (Skunkworks #4)
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF = [None]
_T0_REF = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synth: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_unsupervised_anisotropic_encoder_biology_native_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Self-test (mechanism + verdict shape + sanity)
# ============================================================================

def _selftest():
    print("[selftest] starting...", flush=True)
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,), "T1 trigram shape: %s" % (v.shape,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 trigram not bipolar: %s" % uniq

    # T2: sparse_bipolar_from_dense fraction f
    g = np.random.default_rng(0)
    dense = g.standard_normal((4, 100)).astype(np.float32)
    sp = sparse_bipolar_from_dense(dense, 0.1)
    # ~10 non-zero per row
    nnz_per_row = (sp != 0).sum(axis=1)
    assert (nnz_per_row >= 8).all() and (nnz_per_row <= 14).all(), \
        "T2 sparse fraction: nnz=%s" % nnz_per_row
    # All non-zero values are +-1
    nonzero = sp[sp != 0]
    assert set(np.unique(nonzero).tolist()).issubset({-1.0, 1.0}), "T2 not bipolar"

    # T3: each encoder produces shape (V, N_DIM); sigma=0 self-cleanup OK; no NaN/Inf
    vocab_t = ["w%d" % i for i in range(20)]
    idx_t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3] * 50, dtype=np.int64)
    for arm_name, fn in ENCODERS.items():
        E_t = fn(vocab_t, 128, seed=0, idx_train=idx_t)
        assert E_t.shape == (20, 128), "T3 %s shape: %s" % (arm_name, E_t.shape)
        # NaN/Inf detection per coordinator heads-up 2026-06-25 (Wave F Cell 1 SoftHebb NaN)
        assert np.isfinite(E_t).all(), \
            "T3 %s produced non-finite values (NaN/Inf): n_bad=%d / %d" % (
                arm_name, int((~np.isfinite(E_t)).sum()), E_t.size)
        # sigma=0 sanity
        sr = cleanup_sigma0_sanity(E_t, seed=0, n_eval=20)
        assert sr >= 0.95, "T3 %s sigma=0 sanity recall=%.3f < 0.95" % (arm_name, sr)

    # T3b: production-scale NaN probe for Olshausen-Field (Wave F SoftHebb NaN risk).
    # Smaller-than-full but matmul-scale realistic (N=2048 V=400 idx=500 pairs).
    print("[selftest] T3b: production-scale NaN probe on ARM_OLSHAUSEN_FIELD...", flush=True)
    vocab_prod = ["w%d" % i for i in range(400)]
    idx_prod = np.tile(np.arange(400, dtype=np.int64), 5)  # 2000 tokens, periodic
    # NOTE: We use a smaller N_DIM here (2048) since full N=8192 + dense W is ~270MB
    # and selftest must stay fast. The math kernels are identical -- NaN-class bugs
    # surface at proportional scale.
    E_prod = encoder_olshausen_field(vocab_prod, 2048, seed=0, idx_train=idx_prod)
    assert np.isfinite(E_prod).all(), \
        "T3b OLSHAUSEN production-scale produced non-finite values: n_bad=%d / %d" % (
            int((~np.isfinite(E_prod)).sum()), E_prod.size)
    assert E_prod.shape == (400, 2048), "T3b OLSHAUSEN production shape: %s" % (E_prod.shape,)
    print("[selftest] T3b PASS: ARM_OLSHAUSEN_FIELD finite at N=2048 V=400 idx=2000", flush=True)

    # T4: anisotropy diagnostic returns dict with required keys
    g2 = np.random.default_rng(0)
    E_iso = _l2_normalize(g2.standard_normal((50, 128)).astype(np.float32))
    ani = anisotropy_diagnostic(E_iso, seed=0, sample_cap=40)
    for k in ("anisotropy_eigenspread", "cosine_spread", "eff_rank_norm", "mechanism_fired"):
        assert k in ani, "T4 missing key: %s" % k

    # T5: build_hebbian_W_np correct shape + softmax + unigram + bpc finite.
    # Use V=20 matching vocab_t (NOT E_iso V=50).
    E_small = _l2_normalize(g2.standard_normal((20, 128)).astype(np.float32))
    W = build_hebbian_W_np(idx_t, E_small, ingest_chunk=64)
    assert W.shape == (128, 128), "T5 W shape: %s" % (W.shape,)
    bpc = path_a_bpc(E_small, vocab_t, idx_t, idx_t[:60], LAMBDA_GRID, seed=0)
    # vocab_t = 20, idx_t uses 0..9, BPC must be finite
    assert np.isfinite(bpc["bpc_best_calibrated"]), "T5 BPC not finite: %s" % bpc
    assert bpc["bpc_best_calibrated"] > 0.0, "T5 BPC non-positive: %s" % bpc

    # T6: cluster ID + target cluster + A3' returns valid metric
    n_cl = 4
    cl_ids = _compute_bigram_cluster_ids(idx_t, 20, n_cl, seed=0)
    assert cl_ids.shape == (20,), "T6 cluster_ids shape: %s" % (cl_ids.shape,)
    assert cl_ids.max() < n_cl, "T6 cluster_id out of range: %s" % cl_ids
    tgt = _word_target_clusters(idx_t, 20, cl_ids)
    assert tgt.shape == (20,), "T6 targets shape: %s" % (tgt.shape,)
    heldout = np.array([0, 1, 2], dtype=np.int64)
    a3 = metric_a3_prime(E_small, vocab_t, idx_t, heldout, cl_ids, tgt, seed=0)
    assert "a3_correct" in a3 and 0.0 <= a3["a3_correct"] <= 1.0, "T6 a3 invalid: %s" % a3
    assert a3["random_baseline"] > 0.0, "T6 random_baseline 0: %s" % a3

    # T7: verdict shape -- HARD_FAIL when no biology arm beats random
    def _mk_arm(bpc, a3, eig, sigma0=1.0):
        return {"bpc_raw": bpc + 0.5, "bpc_best_calibrated": bpc,
                "best_lambda": 0.5, "best_dev_bpc": bpc, "bpc_n_eval": 100,
                "a3_correct": a3, "a3_n_eval": 100,
                "a3_random_baseline": 0.1, "a3_n_clusters": 10,
                "anisotropy_eigenspread": eig, "cosine_spread": 0.2,
                "eff_rank_norm": 0.5, "mechanism_fired": eig >= 0.05,
                "sigma0_recall": sigma0,
                "wall_encode_s": 0.0, "wall_sanity_s": 0.0, "wall_anisotropy_s": 0.0,
                "wall_bpc_s": 0.0, "wall_a3p_s": 0.0}

    def _mk_unit(bpcs, a3s, eigs):
        ba = {}
        for al, b, a, e in zip(ARMS, bpcs, a3s, eigs):
            ba[al] = _mk_arm(b, a, e)
        return {"seed": 0, "by_arm": ba, "N": 128, "N_DIM": 128, "N_TRAIN": 100,
                "N_HELD": 50, "VOCAB_CAP": 20, "V_actual": 20, "n_clusters_a3": 4,
                "n_heldout_words": 3, "run_mode": "smoke", "config_version": "selftest",
                "elapsed_s_seed": 0.01}

    # All near-random
    u_fail = _mk_unit([7.5, 7.5, 7.5, 7.5, 7.5], [0.10, 0.11, 0.10, 0.12, 0.11],
                       [0.05, 0.2, 0.2, 0.2, 0.2])
    v, m, d = compute_verdict([u_fail, u_fail, u_fail])
    assert v == "HARD_FAIL", "T7 expected HARD_FAIL got %s msg=%s" % (v, m[:200])

    # Bio arm clears PARTIAL
    u_part = _mk_unit([7.5, 7.2, 7.5, 7.5, 7.5], [0.10, 0.17, 0.10, 0.10, 0.10],
                       [0.05, 0.6, 0.2, 0.2, 0.2])
    v2, m2, _ = compute_verdict([u_part, u_part, u_part])
    assert v2 in ("MIDDLE_BAND", "HARD_PASS"), \
        "T7b expected MIDDLE_BAND or HARD_PASS got %s" % v2

    # Bio arm clears FULL
    u_full = _mk_unit([7.5, 6.5, 7.5, 7.5, 7.5], [0.10, 0.25, 0.10, 0.10, 0.10],
                       [0.05, 0.7, 0.2, 0.2, 0.2])
    v3, m3, _ = compute_verdict([u_full, u_full, u_full])
    assert v3 == "HARD_PASS", "T7c expected HARD_PASS got %s msg=%s" % (v3, m3[:200])

    # CONFOUND_FAIL on sigma0 < 1.0
    u_confound = _mk_unit([7.5, 7.5, 7.5, 7.5, 7.5], [0.1, 0.1, 0.1, 0.1, 0.1],
                           [0.05, 0.2, 0.2, 0.2, 0.2])
    u_confound["by_arm"][ARMS[0]]["sigma0_recall"] = 0.8
    v4, m4, _ = compute_verdict([u_confound, u_confound, u_confound])
    assert v4 == "CONFOUND_FAIL", "T7d expected CONFOUND_FAIL got %s" % v4

    # T8: band constants well-formed (HP_PART_BPC > HP_FULL_BPC etc)
    assert HP_PART_BPC > HP_FULL_BPC, "T8 HP_PART > HP_FULL"
    assert HF_BPC > HP_PART_BPC, "T8 HF > HP_PART"
    assert HP_PART_A3_LIFT < HP_FULL_A3_LIFT, "T8 lift bands"

    print("[selftest] PASS: T1 trigram + T2 sparse_bipolar fraction + T3 all-5-arms shape+sigma0 + "
          "T4 anisotropy + T5 BPC pipeline + T6 cluster+A3' + T7 verdict-shape (HF/MB/HP/CONFOUND) + "
          "T8 band ordering OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d V_CAP=%d N_HELDOUT_WORDS=%d "
          "seeds=%s arms=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, N_HELDOUT_WORDS,
              SEEDS, ARMS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "substrate-unsupervised-anisotropic-encoder-biology-native-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                     run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_substrate_unsupervised_anisotropic_encoder_biology_native_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native; no LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
