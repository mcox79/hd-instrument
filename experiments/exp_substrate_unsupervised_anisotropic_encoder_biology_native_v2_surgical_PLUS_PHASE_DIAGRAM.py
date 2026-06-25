"""substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.

Cell H' v2 = surgical FOLDIAK fix + V phase-diagram scan over 5 arms.

Forks v1 (substrate_unsupervised_anisotropic_encoder_biology_native_v1) with:
  1. SURGICAL FOLDIAK FIX (the only genuine bug per drill 2026-06-25 section 3.1):
     add per-neuron homeostatic firing-rate target
         theta_i += eta * (y_i - rho_target)
     where rho_target = SPARSE_F (~0.02). Without this, anti-Hebbian lateral
     inhibition has no stable fixed point and collapses to rank-1 (v1 metric
     signature: anisotropy_eigenspread=0.9999 + cosine_spread=0.6707 + sigma0=0.0).
  2. PHASE DIAGRAM SCAN over V_GRID = [200, 1000, 4000, 10000]:
     - N_DIM=8192 fixed
     - SPARSE_F=0.02 fixed
     - N_TRAIN = V * 100 (per-vocab training budget; matches Cell 7 + Cell H' v1)
     - 3 seeds per (V, arm) cell -> 60 sub-runs total
  3. PER-(V, arm) classification using random_BPC AT THAT V as the reference:
     HARD_PASS_CHAIN_GRADE: arm_bpc <= rand_bpc - 0.20 AND sigma0 >= 0.95
                            AND cv <= 0.05
     HARD_PASS: arm_bpc <= rand_bpc - 0.10 AND sigma0 >= 0.90
     HARD_FAIL_NULL: |arm_bpc - rand_bpc| < 0.05 AND sigma0 >= 0.90 (legit null)
     CONFOUND_FAIL: sigma0 < 0.90 (cleanup-integrity gate per Skunkworks META)
     HARD_FAIL_HURTS: arm_bpc >= rand_bpc + 0.10 (engineering hurts)
  4. PER-(V, seed) checkpoint via _seed_checkpoint write_partial_key("V<V>_seed<seed>").
  5. OLSHAUSEN provenance investigation: v1 had +0.56 BPC drift vs fair_harness
     rail 7.3065. Logged explicitly in detail (provenance_diagnostic block) per
     N1 verify-referent.
  6. Top-5 alongside top-1 for argmax-noise robustness at V=200 (saturation regime
     per Q discipline; substrate's V=200 small-grid is below JL-margin where
     random saturates).

Per-arm correction (drill 2026-06-25 section 3.1-3.4):
  FOLDIAK:  ONLY genuine bug; fix via homeostatic threshold.
  DEEPWALK: NOT a bug; tail-node degree-1 is graph-structural (brain-prior aligned;
            DG-CA3 partial-recall for sparsely-encoded items). Re-run unchanged.
  KOHONEN:  genuine HARD_FAIL_NULL (sigma0=1.0; no lift). Keep as control.
  OLSHAUSEN: works mechanically; tied with random at V=4000 (per-arm negative
             in regime atom). Provenance rail FAILED in v1 (+0.56 vs fair_harness
             7.3065); v2 investigates.

Cell verdict (cell-level):
  HARD_PASS_CHAIN_GRADE if ANY arm hits HARD_PASS_CHAIN_GRADE at ANY V.
  HARD_PASS if any arm HARD_PASS at any V.
  HARD_FAIL_NULL if ALL arms HARD_FAIL_NULL across all V (informative negative;
                  substrate-product wants LESS anisotropy at this regime).
  CONFOUND_FAIL if multiple (V, arm) cells still have sigma0 issues.
  MIDDLE_BAND otherwise.

USER directives honored:
  - 2026-06-25 basis-vs-use-case: NO labels at basis layer.
  - 2026-06-22 substrate-native: no MiniLM, no BGE.
  - 2026-06-23 clean-methodology.
  - 2026-06-22 brain prior +0.10 for biology-grounded mechanisms.
  - Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm: cleanup
    integrity is FIRST gate before mechanism claims.

Operating disciplines:
  - D1 roofline probe (60 sub-runs); doc'd in prereg + heads-up.
  - D2 atexit + per-(V, arm) checkpoint MANDATORY (don't lose 3h work).
  - Per Fix #28: per-(arm, V) metrics in detail.by_arm_V_agg; verdict_msg cites.
  - Per Fix #17: timeout estimation per-V; full sweep budget 10800s.
  - Fix #20: no pipe-tail subprocess monitoring (use file-redirect + mtime).
  - ASCII-only per feedback_ascii_only_in_scripts.
  - atexit synthesizer (Skunkworks #4): always produce metrics.json on timeout.

Cites:
  - notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md
    (per-negative correction; FOLDIAK = only genuine bug)
  - experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py
    (forked base; v1 had 5-arm shotgun at V=4000 only)
  - experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py
    (rail 7.3065 BPC reference)
  - Foldiak 1990 PNAS Biol Cybern 64:165-170 (lateral inhibition + firing-rate
    target; Section "Adaptive threshold" - THE fix for rank-1 collapse)
  - Olshausen-Field 1996 Nature 381:607-609 (V1 sparse coding)
  - Moraitis 2107.05747 (SoftHebb forward-only Hebbian)
  - Perozzi 2014 (DeepWalk)
  - Kohonen 1982 (SOM)

SUBSTRATE-ONLY: _LLM_CALL_COUNTER = [0]; pure numpy; no torch import.
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

ANCHOR_NAME = "substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM"
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
# Pre-reg HARD bands (per-arm-at-V; vs random_BPC AT THAT V)
# ============================================================================

# Per-arm at each V: relative to random_BPC at THAT V
HP_CHAIN_GRADE_BPC_LIFT = 0.20   # arm_bpc <= rand_bpc - 0.20
HP_CHAIN_GRADE_SIGMA0 = 0.95
HP_CHAIN_GRADE_CV = 0.05

HP_BPC_LIFT = 0.10               # arm_bpc <= rand_bpc - 0.10
HP_SIGMA0 = 0.90

HF_NULL_BPC_BAND = 0.05          # |arm_bpc - rand_bpc| < 0.05
HF_NULL_SIGMA0 = 0.90            # AND sigma0 >= 0.90 (legit null)

CONFOUND_SIGMA0 = 0.90           # sigma0 < 0.90 = cleanup-integrity fail

HF_HURTS_BPC_GAIN = 0.10         # arm_bpc >= rand_bpc + 0.10

# Provenance rail (for V=4000 RANDOM_BIPOLAR only; v1 was +0.56 off; we
# investigate why)
SANITY_FAIR_HARNESS_BPC = 7.3065
SANITY_FAIR_HARNESS_TOL = 0.20   # Loose tolerance per N1 (v1 was +0.56 off so
                                  # exposes the gap rather than fail-hard;
                                  # provenance_diagnostic block records the drift)

# Mechanism-fired diagnostic
SANITY_METHODOLOGY_EIGENSPREAD_MIN = 0.05

# ============================================================================
# Config
# ============================================================================

N_DIM = 8192
SPARSE_F = 0.02
K_WTA = 5
INGEST_CHUNK = 8192
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]

# Phase-diagram V grid (per spec)
V_GRID_FULL = [200, 1000, 4000, 10000]
V_GRID_SMOKE = [200, 400]

# N_TRAIN scaling: V * 100 per Cell 7 + v1 conventions
def _n_train_for_V(V: int) -> int:
    return V * 100

def _n_held_for_V(V: int) -> int:
    return max(1000, V * 20)

def _n_heldout_words_for_V(V: int) -> int:
    return max(20, min(V // 10, 250))

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    V_GRID = V_GRID_FULL
    N_OLSHAUSEN_BATCHES = 80
    N_FOLDIAK_ITER = 30
    N_SOM_EPOCHS = 12
    N_BIGRAM_WALKS = 4000
    WALK_LEN = 12
else:
    SEEDS = [7]
    V_GRID = V_GRID_SMOKE
    N_OLSHAUSEN_BATCHES = 6
    N_FOLDIAK_ITER = 4
    N_SOM_EPOCHS = 2
    N_BIGRAM_WALKS = 200
    WALK_LEN = 8

ARMS = [
    "ARM_RANDOM_BIPOLAR_BASELINE",
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING",
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH",
    "ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC",  # v2 SURGICAL FIX
    "ARM_KOHONEN_SOM_TOPOGRAPHIC",
]

CONFIG_VERSION = (
    "subUnsupAnisBio-v2-SURGICAL_PLUS_PHASE_DIAGRAM: N_DIM=%d SPARSE_F=%.3f K_WTA=%d "
    "V_GRID=%s arms=%s seeds=%s mode=%s; bands HP_CHAIN_LIFT>=%.3f sigma0>=%.3f "
    "HP_LIFT>=%.3f sigma0>=%.3f HF_NULL_BAND<=%.3f CONFOUND_SIGMA0<%.3f"
) % (
    N_DIM, SPARSE_F, K_WTA, V_GRID, ARMS, SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_BPC_LIFT, HP_CHAIN_GRADE_SIGMA0,
    HP_BPC_LIFT, HP_SIGMA0, HF_NULL_BPC_BAND, CONFOUND_SIGMA0,
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

    UNCHANGED from v1; mechanism works at scale (no NaN). v1 negative-in-regime
    atom: tied with random at V=4000 (per Skunkworks). v2 just probes other V.
    """
    g = np.random.default_rng(seed * 17 + 2)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
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
    nan_detected = False
    for cs in range(0, n_train_effective, batch_size):
        ce = min(cs + batch_size, n_train_effective)
        js = sub_idx[cs:ce]
        X = E_in[idx_train[js]]
        Z = X @ W.T
        if K_WTA < n_dim:
            abs_Z = np.abs(Z)
            thresh = np.partition(abs_Z, -K_WTA, axis=1)[:, -K_WTA:].min(axis=1, keepdims=True)
            mask = (abs_Z >= thresh).astype(np.float32)
            Y = Z * mask
        else:
            Y = Z
        B_eff = max(X.shape[0], 1)
        update = (eta / B_eff) * (Y.T @ X)
        update = np.clip(update, -1.0, 1.0)
        W += update
        W *= (1.0 - decay)
        W_norm = np.linalg.norm(W)
        if W_norm > 100.0 * math.sqrt(n_dim):
            W *= (100.0 * math.sqrt(n_dim) / W_norm)
        if not np.isfinite(W).all():
            nan_detected = True
            sys.stderr.write("[OLSHAUSEN_NAN] W non-finite at batch %d; falling back\n" % cs)
            sys.stderr.flush()
            break
    if nan_detected:
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    E_out = (E_in @ W.T).astype(np.float32)
    if not np.isfinite(E_out).all():
        sys.stderr.write("[OLSHAUSEN_NAN] final E_out non-finite; falling back\n")
        sys.stderr.flush()
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
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
    top_k = 20
    out: Dict[int, List[int]] = {}
    for s, c in adj.items():
        out[s] = [n for n, _ in c.most_common(top_k)]
    return out


def encoder_deepwalk_on_bigram(vocab: List[str], n_dim: int, seed: int,
                                idx_train: np.ndarray) -> np.ndarray:
    """ARM 3: DeepWalk-on-bigram-graph. UNCHANGED from v1.

    Per drill section 3.2: tail-node degree-1 in bigram graph is STRUCTURAL +
    brain-prior aligned (DG-CA3 partial-recall for sparsely-encoded items).
    sigma0=0.94 at V=4000 in v1 is the expected non-tail-fraction.
    """
    g = np.random.default_rng(seed * 19 + 3)
    V = len(vocab)
    if len(idx_train) < 2:
        return encoder_random_bipolar(vocab, n_dim, seed, idx_train)
    adj = _build_bigram_graph(idx_train, V)
    nodes = [s for s in adj if adj[s]]
    if not nodes:
        return encoder_random_bipolar(vocab, n_dim, seed, idx_train)
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
        for i, wi in enumerate(walk):
            lo = max(0, i - window)
            hi = min(len(walk), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                cooc[wi][walk[j]] += 1
    R = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32) / math.sqrt(n_dim)
    E = np.zeros((V, n_dim), dtype=np.float32)
    for v in range(V):
        c = cooc.get(v)
        if not c:
            E[v] = char_trigram_encode(vocab[v], n_dim, seed)
            continue
        idxs = np.array(list(c.keys()), dtype=np.int64)
        wts = np.array(list(c.values()), dtype=np.float32)
        E[v] = wts @ R[idxs]
    E = sparse_bipolar_from_dense(E, SPARSE_F)
    return _l2_normalize(E)


def encoder_foldiak_anti_hebbian_v2_homeostatic(vocab: List[str], n_dim: int, seed: int,
                                                 idx_train: np.ndarray) -> np.ndarray:
    """ARM 4 (v2 SURGICAL FIX): Foldiak 1990 anti-Hebbian lateral inhibition
    WITH homeostatic firing-rate target (the missing component that collapsed
    v1 to rank-1).

    THE FIX (per Foldiak 1990 Section "Adaptive threshold" + drill 2026-06-25):
      Each neuron i has an adaptive threshold theta_i. After each iteration:
          theta_i += eta_theta * (y_i - rho_target)
      where rho_target = SPARSE_F (~0.02; matches output target sparsity).
      Then in next iteration: y_i = nonlin(W @ x - theta_i).

      WITHOUT this: strongest unit suppresses all others -> cascade to rank-1
                    (v1 metric: eigenspread=0.9999, cosine_spread=0.6707, sigma0=0.0).
      WITH this:    threshold rises for over-active units, falls for under-active;
                    stable fixed point at target rate sparse_f.

    Substrate-native recipe:
      1. Input = char-trigram encoding (substrate-baseline).
      2. Codebook = vocab encoding; lateral W_lat [V_sub x V_sub] inhibitory.
      3. Per-neuron threshold theta [V] for homeostatic firing-rate target.
      4. Iterate:
         a. y = (codebook - inhibition) - theta (post-inhibition raw activations)
         b. y_binarized = (y > 0)  # firing indicator for theta update
         c. theta += eta_theta * (mean_pairwise_firing_rate - rho_target)
         d. codebook = _l2_normalize(codebook - inhibition)
         e. W_lat += eta * cross-correlation (anti-Hebb)
      5. Output = sparse-bipolarized decorrelated codebook.

    rho_target = SPARSE_F = 0.02. eta_theta tuned so theta tracks rate slowly.
    """
    g = np.random.default_rng(seed * 23 + 4)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    codebook = E_in.copy()
    # V x V lateral; for V=10000 this is 400MB; acceptable on CPU
    # (will warn but not abort; if memory crit, the OOM is informative bound)
    W_lat = np.zeros((V, V), dtype=np.float32)
    eta = 0.01
    decay = 1e-4
    # SURGICAL FIX: per-neuron threshold for homeostatic firing-rate target
    theta = np.zeros(V, dtype=np.float32)
    eta_theta = 0.05  # threshold adaptation rate; slow vs eta
    rho_target = SPARSE_F  # 0.02 = target firing rate matching output sparsity
    nan_detected = False
    for it in range(N_FOLDIAK_ITER):
        np.fill_diagonal(W_lat, 0.0)
        inhibition = W_lat @ codebook
        # Compute post-inhibition activations adjusted by adaptive threshold
        post = codebook - inhibition - theta[:, None]
        # Firing indicator: fraction of dims firing per-row (used for homeostasis)
        # We use a thresholded indicator -- (post > 0) is the binary firing pattern.
        firing = (post > 0).astype(np.float32)
        actual_rate = firing.mean(axis=1)  # per-neuron mean firing rate, shape [V]
        # SURGICAL FIX: homeostatic threshold update
        # If actual_rate > rho_target, theta increases (suppress over-active)
        # If actual_rate < rho_target, theta decreases (promote under-active)
        theta += eta_theta * (actual_rate - rho_target)
        # Apply post-threshold codebook update + normalize
        codebook = post  # signed post-threshold activations
        codebook = _l2_normalize(codebook)
        # Anti-Hebb on cross-correlation (V x V)
        Y = codebook @ codebook.T
        np.fill_diagonal(Y, 0.0)
        W_lat += eta * Y
        W_lat *= (1.0 - decay)
        W_lat = np.clip(W_lat, -1.0, 1.0)
        if not np.isfinite(codebook).all() or not np.isfinite(theta).all():
            nan_detected = True
            sys.stderr.write("[FOLDIAK_v2_NAN] codebook/theta non-finite at iter %d; falling back\n" % it)
            sys.stderr.flush()
            return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    if nan_detected or not np.isfinite(codebook).all():
        sys.stderr.write("[FOLDIAK_v2_NAN] final codebook non-finite; falling back\n")
        sys.stderr.flush()
        return _l2_normalize(sparse_bipolar_from_dense(E_in, SPARSE_F))
    E_out = sparse_bipolar_from_dense(codebook, SPARSE_F)
    return _l2_normalize(E_out)


def encoder_kohonen_som(vocab: List[str], n_dim: int, seed: int,
                         idx_train: np.ndarray) -> np.ndarray:
    """ARM 5: Kohonen SOM. UNCHANGED from v1.

    Per drill section 3.3: pristine sigma0=1.0; genuine HARD_FAIL_NULL (no lift).
    Kept as clean null control across V phase diagram.
    """
    g = np.random.default_rng(seed * 29 + 5)
    V = len(vocab)
    E_in = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_in = _l2_normalize(E_in)
    codebook = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    codebook = _l2_normalize(codebook)
    pos_tag = (g.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    n_pairs = len(idx_train)
    if n_pairs <= 0:
        out_bipolar = np.sign(codebook * pos_tag).astype(np.float32)
        out_bipolar[out_bipolar == 0] = 1.0
        E_out = sparse_bipolar_from_dense(out_bipolar, SPARSE_F)
        return _l2_normalize(E_out)
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
    out_bipolar = np.sign(codebook * pos_tag).astype(np.float32)
    out_bipolar[out_bipolar == 0] = 1.0
    E_out = sparse_bipolar_from_dense(out_bipolar, SPARSE_F)
    return _l2_normalize(E_out)


ENCODERS = {
    "ARM_RANDOM_BIPOLAR_BASELINE":                          encoder_random_bipolar,
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING":                    encoder_olshausen_field,
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH":                         encoder_deepwalk_on_bigram,
    "ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC":      encoder_foldiak_anti_hebbian_v2_homeostatic,
    "ARM_KOHONEN_SOM_TOPOGRAPHIC":                          encoder_kohonen_som,
}


# ============================================================================
# Metric B: BPC on text8 held (per arm; top-1 + top-5 robustness)
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
    """Hebbian-substrate LM BPC with log-linear unigram interpolation; reports
    BPC top-1, BPC raw, plus top-1 and top-5 argmax accuracies for the per-V
    saturation-regime robustness check (Q discipline)."""
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
                "best_lambda": 1.0, "n_eval": 0,
                "top1_acc": 0.0, "top5_acc": 0.0}
    sub_logits = np.zeros((n_eval, V), dtype=np.float32)
    chunk = 1024
    for b in range(0, n_eval, chunk):
        end = min(b + chunk, n_eval)
        pred_vec = E[ctx[b:end]] @ W.T
        pn = np.linalg.norm(pred_vec, axis=1, keepdims=True)
        pn[pn < 1e-9] = 1e-9
        pred_vec = pred_vec / pn
        sub_logits[b:end] = pred_vec @ E.T
    # top-1 + top-5 argmax accuracy (Q discipline; robust at saturation)
    top1 = np.argmax(sub_logits, axis=1)
    top1_acc = float((top1 == nxt).mean())
    # top-5 via argpartition
    k5 = min(5, V)
    top5_idx = np.argpartition(-sub_logits, k5 - 1, axis=1)[:, :k5]
    top5_hits = (top5_idx == nxt[:, None]).any(axis=1)
    top5_acc = float(top5_hits.mean())
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
        "top1_acc": round(top1_acc, 4),
        "top5_acc": round(top5_acc, 4),
    }


# ============================================================================
# Anisotropy diagnostic (eigenspread + cosine-spread)
# ============================================================================

def anisotropy_diagnostic(E: np.ndarray, seed: int, sample_cap: int = 1000) -> dict:
    g = np.random.default_rng(seed * 41 + 11)
    V = E.shape[0]
    n_sample = min(sample_cap, V)
    idx = g.choice(V, size=n_sample, replace=False)
    Es = E[idx]
    cov = Es.T @ Es / max(n_sample, 1)
    try:
        eigs = np.linalg.eigvalsh(cov)
    except Exception:
        eigs = np.zeros(cov.shape[0])
    eigs = np.clip(eigs, 0.0, None)
    s = eigs.sum()
    if s <= 0:
        return {"anisotropy_eigenspread": 0.0, "cosine_spread": 0.0, "eff_rank_norm": 0.0,
                "mechanism_fired": False}
    pr = (s * s) / max(float((eigs * eigs).sum()), 1e-12)
    eff_rank_norm = pr / max(eigs.shape[0], 1)
    eigenspread = 1.0 - eff_rank_norm
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
# sigma=0 cleanup sanity (CONFOUND_FAIL detector; Skunkworks META rule)
# ============================================================================

def cleanup_sigma0_sanity(E: np.ndarray, seed: int, n_eval: int = 100) -> float:
    g = np.random.default_rng(seed * 43 + 13)
    V = E.shape[0]
    n = min(n_eval, V)
    idx = g.choice(V, size=n, replace=False)
    E_n = _l2_normalize(E)
    cues = E_n[idx]
    scores = cues @ E_n.T
    pred = np.argmax(scores, axis=1)
    return float((pred == idx).sum()) / max(n, 1)


# ============================================================================
# Per-(V, seed) unit -- runs all 5 arms at one V at one seed
# ============================================================================

def run_unit_at_V(V_cap: int, seed: int) -> Dict:
    t0 = time.time()
    n_train = _n_train_for_V(V_cap)
    n_held = _n_held_for_V(V_cap)
    print("\n[V=%d seed=%d] loading text8 (N_TRAIN=%d N_HELD=%d)" % (
        V_cap, seed, n_train, n_held), flush=True)
    toks = load_text8_tokens(n_train + n_held)
    if len(toks) < n_train + n_held:
        print("[WARN] corpus too small: %d vs %d" % (len(toks), n_train + n_held), flush=True)
    train_toks = toks[:n_train]
    held_toks = toks[n_train:n_train + n_held]
    vocab, w2i = build_vocab(train_toks, cap=V_cap)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[V=%d seed=%d] V_actual=%d N_DIM=%d" % (V_cap, seed, V, N_DIM), flush=True)

    by_arm = {}
    for arm_label in ARMS:
        t_arm = time.time()
        print("  [V=%d seed=%d arm=%s] encoding..." % (V_cap, seed, arm_label), flush=True)
        fn = ENCODERS[arm_label]
        E_full = fn(vocab, N_DIM, seed, idx_train)
        t_enc = time.time() - t_arm
        t_s = time.time()
        sigma0_recall = cleanup_sigma0_sanity(E_full, seed, n_eval=100)
        t_sanity = time.time() - t_s
        t_a = time.time()
        ani = anisotropy_diagnostic(E_full, seed, sample_cap=min(500, V))
        t_ani = time.time() - t_a
        t_b = time.time()
        bpc = path_a_bpc(E_full, vocab, idx_train, idx_held, LAMBDA_GRID, seed)
        t_bpc = time.time() - t_b
        by_arm[arm_label] = {
            "bpc_raw": bpc["bpc_raw"],
            "bpc_best_calibrated": bpc["bpc_best_calibrated"],
            "best_lambda": bpc["best_lambda"],
            "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_n_eval": bpc["n_eval"],
            "top1_acc": bpc["top1_acc"],
            "top5_acc": bpc["top5_acc"],
            "anisotropy_eigenspread": ani["anisotropy_eigenspread"],
            "cosine_spread": ani["cosine_spread"],
            "eff_rank_norm": ani["eff_rank_norm"],
            "mechanism_fired": ani["mechanism_fired"],
            "sigma0_recall": round(sigma0_recall, 4),
            "wall_encode_s": round(t_enc, 2),
            "wall_sanity_s": round(t_sanity, 2),
            "wall_anisotropy_s": round(t_ani, 2),
            "wall_bpc_s": round(t_bpc, 2),
        }
        a = by_arm[arm_label]
        print("    [V=%d s=%d %s] bpc_best=%.3f top1=%.3f top5=%.3f eigsprd=%.3f "
              "cosstd=%.3f sigma0=%.3f fired=%s (enc=%.1fs bpc=%.1fs)" % (
                  V_cap, seed, arm_label, a["bpc_best_calibrated"], a["top1_acc"],
                  a["top5_acc"], a["anisotropy_eigenspread"], a["cosine_spread"],
                  a["sigma0_recall"], a["mechanism_fired"], t_enc, t_bpc), flush=True)

    return {
        "V_cap": V_cap,
        "seed": seed,
        "by_arm": by_arm,
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": n_train,
        "N_HELD": n_held,
        "V_actual": V,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_unit": round(time.time() - t0, 2),
    }


# ============================================================================
# Verdict (per-(V, arm); Fix #28 compliant)
# ============================================================================

def _classify_arm_at_V(arm_metrics: dict, random_bpc: float) -> dict:
    """Per-(V, arm) classification using random_bpc AT THAT V as reference."""
    bpc = float(arm_metrics["bpc_best_calibrated_mean"])
    bpc_cv = float(arm_metrics["bpc_best_calibrated_cv"])
    sigma0 = float(arm_metrics["sigma0_recall_mean"])
    eig = float(arm_metrics["anisotropy_eigenspread_mean"])
    lift_bpc = random_bpc - bpc  # positive = arm beats random; negative = arm hurts

    # CONFOUND_FAIL gate FIRST (Skunkworks META rule)
    if sigma0 < CONFOUND_SIGMA0:
        return {"classification": "CONFOUND_FAIL", "lift_bpc": lift_bpc,
                "sigma0_confound": True,
                "mechanism_fired": eig >= SANITY_METHODOLOGY_EIGENSPREAD_MIN}
    # HARD_PASS_CHAIN_GRADE: arm beats random by >= 0.20 AND sigma0 >= 0.95 AND cv tight
    if (lift_bpc >= HP_CHAIN_GRADE_BPC_LIFT
            and sigma0 >= HP_CHAIN_GRADE_SIGMA0
            and bpc_cv <= HP_CHAIN_GRADE_CV):
        cl = "HARD_PASS_CHAIN_GRADE"
    elif lift_bpc >= HP_BPC_LIFT and sigma0 >= HP_SIGMA0:
        cl = "HARD_PASS"
    elif abs(lift_bpc) < HF_NULL_BPC_BAND and sigma0 >= HF_NULL_SIGMA0:
        cl = "HARD_FAIL_NULL"
    elif lift_bpc <= -HF_HURTS_BPC_GAIN:
        cl = "HARD_FAIL_HURTS"
    else:
        cl = "MIDDLE_BAND"

    return {"classification": cl, "lift_bpc": lift_bpc,
            "sigma0_confound": False,
            "mechanism_fired": eig >= SANITY_METHODOLOGY_EIGENSPREAD_MIN}


def compute_verdict(units):
    """Cell-level verdict from per-(V, seed) units.

    units is a list of dicts each shaped per run_unit_at_V output (contains
    V_cap, seed, by_arm).

    Aggregation: group by V_cap, then per arm across 3 seeds at THAT V.
    Then per-arm classification using random_BPC at that V.
    Then cell-level rollup.
    """
    if not units:
        return ("HARD_FAIL", "no results", {})
    # Group by V_cap
    by_V: Dict[int, List[dict]] = defaultdict(list)
    for u in units:
        by_V[int(u["V_cap"])].append(u)
    by_arm_V_agg: Dict[str, Dict[int, dict]] = {al: {} for al in ARMS}
    classifications: Dict[str, Dict[int, dict]] = {al: {} for al in ARMS}

    # Provenance diagnostic: track V=4000 random BPC drift vs fair_harness rail
    provenance = {}

    for V_cap in sorted(by_V.keys()):
        V_units = by_V[V_cap]
        # Aggregate per-arm at this V across seeds
        for arm_label in ARMS:
            bpc_vals = [u["by_arm"][arm_label]["bpc_best_calibrated"] for u in V_units]
            top1_vals = [u["by_arm"][arm_label]["top1_acc"] for u in V_units]
            top5_vals = [u["by_arm"][arm_label]["top5_acc"] for u in V_units]
            eig_vals = [u["by_arm"][arm_label]["anisotropy_eigenspread"] for u in V_units]
            cos_vals = [u["by_arm"][arm_label]["cosine_spread"] for u in V_units]
            sigma0_vals = [u["by_arm"][arm_label]["sigma0_recall"] for u in V_units]
            b_mean = float(np.mean(bpc_vals)); b_std = float(np.std(bpc_vals))
            b_cv = b_std / max(abs(b_mean), 1e-6)
            t1_mean = float(np.mean(top1_vals))
            t5_mean = float(np.mean(top5_vals))
            e_mean = float(np.mean(eig_vals))
            c_mean = float(np.mean(cos_vals))
            s_mean = float(np.mean(sigma0_vals))
            by_arm_V_agg[arm_label][V_cap] = {
                "bpc_best_calibrated_mean": round(b_mean, 4),
                "bpc_best_calibrated_std": round(b_std, 4),
                "bpc_best_calibrated_cv": round(b_cv, 4),
                "top1_acc_mean": round(t1_mean, 4),
                "top5_acc_mean": round(t5_mean, 4),
                "anisotropy_eigenspread_mean": round(e_mean, 4),
                "cosine_spread_mean": round(c_mean, 4),
                "sigma0_recall_mean": round(s_mean, 4),
                "n_seeds": len(V_units),
            }
        # Per-V classifications using random_BPC AT THIS V
        rand_bpc_V = by_arm_V_agg["ARM_RANDOM_BIPOLAR_BASELINE"][V_cap]["bpc_best_calibrated_mean"]
        for arm_label in ARMS:
            classifications[arm_label][V_cap] = _classify_arm_at_V(
                by_arm_V_agg[arm_label][V_cap], rand_bpc_V)
        # Provenance check: V=4000 random BPC vs fair_harness 7.3065
        if V_cap == 4000:
            drift = rand_bpc_V - SANITY_FAIR_HARNESS_BPC
            provenance["random_bpc_at_V4000"] = round(rand_bpc_V, 4)
            provenance["fair_harness_target"] = SANITY_FAIR_HARNESS_BPC
            provenance["drift_vs_fair_harness"] = round(drift, 4)
            provenance["within_tol"] = abs(drift) <= SANITY_FAIR_HARNESS_TOL
            provenance["tol"] = SANITY_FAIR_HARNESS_TOL
            provenance["note"] = (
                "v1 had +0.56 BPC drift; v2 records honestly. Drift may stem from "
                "different fair_harness config (vocab, sparse_f, temperature, ingest path)."
            )

    # Cell-level rollup
    biology_arms = [al for al in ARMS if al != "ARM_RANDOM_BIPOLAR_BASELINE"]
    any_chain_grade = []
    any_hard_pass = []
    confound_cells = []
    null_cells = []
    middle_cells = []
    hurts_cells = []
    for arm_label in biology_arms:
        for V_cap in sorted(by_V.keys()):
            cl = classifications[arm_label][V_cap]["classification"]
            label = "%s@V=%d" % (arm_label, V_cap)
            if cl == "HARD_PASS_CHAIN_GRADE":
                any_chain_grade.append(label)
            elif cl == "HARD_PASS":
                any_hard_pass.append(label)
            elif cl == "CONFOUND_FAIL":
                confound_cells.append(label)
            elif cl == "HARD_FAIL_NULL":
                null_cells.append(label)
            elif cl == "HARD_FAIL_HURTS":
                hurts_cells.append(label)
            else:
                middle_cells.append(label)

    detail = {
        "by_arm_V_agg": {al: {str(V): by_arm_V_agg[al][V] for V in by_arm_V_agg[al]}
                          for al in ARMS},
        "classifications": {al: {str(V): classifications[al][V]["classification"]
                                  for V in classifications[al]} for al in ARMS},
        "lift_bpc": {al: {str(V): round(classifications[al][V]["lift_bpc"], 4)
                          for V in classifications[al]} for al in ARMS},
        "any_chain_grade_cells": any_chain_grade,
        "any_hard_pass_cells": any_hard_pass,
        "confound_cells": confound_cells,
        "null_cells": null_cells,
        "hurts_cells": hurts_cells,
        "middle_cells": middle_cells,
        "V_grid_actual": sorted(by_V.keys()),
        "n_total_V_seed_units": len(units),
        "provenance_diagnostic": provenance,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "5-arm biology-native UNSUPERVISED anisotropic encoder phase-diagram scan "
            "across V in %s at N_DIM=%d; per-(V, arm) classification using random_BPC "
            "AT THAT V as the reference; FOLDIAK has SURGICAL homeostatic firing-rate "
            "target fix per drill 2026-06-25 section 3.1"
        ) % (sorted(by_V.keys()), N_DIM),
        "cites": [
            "notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md",
            "experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py",
            "experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py",
            "Foldiak_1990_PNAS_64_165_AdaptiveThreshold",
            "Olshausen_Field_1996_Nature_381_607",
            "Moraitis_2107_05747_SoftHebb",
            "Perozzi_2014_DeepWalk",
            "Kohonen_1982_SOM",
        ],
    }

    # Summary (per-(V, arm) terse)
    parts = []
    for V_cap in sorted(by_V.keys()):
        rand_bpc_V = by_arm_V_agg["ARM_RANDOM_BIPOLAR_BASELINE"][V_cap]["bpc_best_calibrated_mean"]
        for arm_label in biology_arms:
            a = by_arm_V_agg[arm_label][V_cap]
            cl = classifications[arm_label][V_cap]["classification"]
            lift = classifications[arm_label][V_cap]["lift_bpc"]
            parts.append("%s@V=%d=bpc%.3f(lift%+.3f vs rand%.3f)/sig0%.3f[%s]" % (
                arm_label.replace("ARM_", "")[:14], V_cap,
                a["bpc_best_calibrated_mean"], lift, rand_bpc_V,
                a["sigma0_recall_mean"], cl))
    summary = "BIO5xV: " + " | ".join(parts)

    # Cell-level verdict
    if any_chain_grade:
        msg = ("HARD_PASS_CHAIN_GRADE: %s; biology-native unsupervised encoder is "
               "chain-grade-eligible at production scale. " % any_chain_grade) + summary
        return ("HARD_PASS", msg, detail)
    if any_hard_pass:
        msg = ("HARD_PASS: %s; biology-native lift present but not chain-grade. " %
               any_hard_pass) + summary
        return ("HARD_PASS", msg, detail)
    # Check ALL biology cells HARD_FAIL_NULL
    total_bio_cells = len(biology_arms) * len(by_V)
    if len(null_cells) == total_bio_cells:
        msg = ("HARD_FAIL_NULL: ALL biology arms across ALL V are within +/-%.3f of "
               "random_BPC at their V; informative negative -- substrate-product wants "
               "LESS anisotropy at this regime; Mu-Viswanath-aligned. " %
               HF_NULL_BPC_BAND) + summary
        return ("HARD_FAIL", msg, detail)
    if len(confound_cells) >= 3:
        msg = ("CONFOUND_FAIL: %d (V, arm) cells failed sigma0 cleanup-integrity gate; "
               "implementation bugs suspected: %s. " % (
                   len(confound_cells), confound_cells)) + summary
        return ("CONFOUND_FAIL", msg, detail)
    # MIDDLE_BAND otherwise
    msg = ("MIDDLE_BAND: mixed outcomes across (V, arm) grid; %d null, %d hurts, "
           "%d middle, %d confound. " % (
               len(null_cells), len(hurts_cells), len(middle_cells),
               len(confound_cells))) + summary
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
        # All (V, seed) keys -- recover whatever is present
        all_keys = ["V%d_seed%d" % (V, sd) for V in V_GRID for sd in SEEDS]
        partials = aggregate_partials(out_dir, all_keys)
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synth: compute_verdict failed: %s" % e,
                                     {"n_units_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_N%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "V_grid": V_GRID,
            "n_units": len(units),
            "n_units_expected": len(V_GRID) * len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_" + ANCHOR_NAME,
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d units] %s" % (
                len(units), len(V_GRID) * len(SEEDS), msg),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d units\n" % (
            len(units), len(V_GRID) * len(SEEDS)))
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
    nnz_per_row = (sp != 0).sum(axis=1)
    assert (nnz_per_row >= 8).all() and (nnz_per_row <= 14).all(), \
        "T2 sparse fraction: nnz=%s" % nnz_per_row
    nonzero = sp[sp != 0]
    assert set(np.unique(nonzero).tolist()).issubset({-1.0, 1.0}), "T2 not bipolar"

    # T3: each encoder produces shape (V, N_DIM); sigma=0 self-cleanup OK; no NaN/Inf
    vocab_t = ["w%d" % i for i in range(20)]
    idx_t = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3] * 50, dtype=np.int64)
    for arm_name, fn in ENCODERS.items():
        E_t = fn(vocab_t, 128, seed=0, idx_train=idx_t)
        assert E_t.shape == (20, 128), "T3 %s shape: %s" % (arm_name, E_t.shape)
        assert np.isfinite(E_t).all(), \
            "T3 %s produced non-finite values: n_bad=%d / %d" % (
                arm_name, int((~np.isfinite(E_t)).sum()), E_t.size)
        sr = cleanup_sigma0_sanity(E_t, seed=0, n_eval=20)
        # Foldiak v2 should now satisfy sigma0 >= 0.90 (the surgical fix); other
        # arms remain pristine. Small-V cleanup may dip due to top-k aliasing;
        # require >= 0.90 (the v2 HP_SIGMA0 threshold).
        assert sr >= 0.90, "T3 %s sigma=0 sanity recall=%.3f < 0.90" % (arm_name, sr)

    # T3b: SURGICAL FOLDIAK FIX -- v2 must NOT collapse to rank-1 at small scale
    # (v1 hit eigenspread=0.9999 + sigma0=0.0 in the same regime; v2 must not).
    print("[selftest] T3b: SURGICAL FOLDIAK FIX validation...", flush=True)
    vocab_fb = ["w%d" % i for i in range(40)]
    idx_fb = np.tile(np.arange(40, dtype=np.int64), 20)  # 800 tokens
    E_fb = encoder_foldiak_anti_hebbian_v2_homeostatic(vocab_fb, 256, seed=11, idx_train=idx_fb)
    sigma0_fb = cleanup_sigma0_sanity(E_fb, seed=11, n_eval=40)
    ani_fb = anisotropy_diagnostic(E_fb, seed=11, sample_cap=40)
    # Asserts: sigma0 >= 0.90 (was 0.0 in v1) + eigenspread NOT at extreme (was 0.9999)
    assert sigma0_fb >= 0.90, \
        "T3b FOLDIAK_v2 sigma0=%.3f still below 0.90; surgical fix INSUFFICIENT" % sigma0_fb
    assert ani_fb["anisotropy_eigenspread"] < 0.99, \
        "T3b FOLDIAK_v2 eigenspread=%.4f still at rank-1 extreme; surgical fix INSUFFICIENT" % (
            ani_fb["anisotropy_eigenspread"])
    print("[selftest] T3b PASS: FOLDIAK v2 sigma0=%.3f eigsprd=%.4f (v1 had sigma0=0.0 eigsprd=0.9999)" % (
        sigma0_fb, ani_fb["anisotropy_eigenspread"]), flush=True)

    # T4: anisotropy diagnostic returns dict with required keys
    g2 = np.random.default_rng(0)
    E_iso = _l2_normalize(g2.standard_normal((50, 128)).astype(np.float32))
    ani = anisotropy_diagnostic(E_iso, seed=0, sample_cap=40)
    for k in ("anisotropy_eigenspread", "cosine_spread", "eff_rank_norm", "mechanism_fired"):
        assert k in ani, "T4 missing key: %s" % k

    # T5: build_hebbian_W_np correct + bpc finite + top-1/top-5 in [0, 1]
    E_small = _l2_normalize(g2.standard_normal((20, 128)).astype(np.float32))
    W = build_hebbian_W_np(idx_t, E_small, ingest_chunk=64)
    assert W.shape == (128, 128), "T5 W shape: %s" % (W.shape,)
    bpc = path_a_bpc(E_small, vocab_t, idx_t, idx_t[:60], LAMBDA_GRID, seed=0)
    assert np.isfinite(bpc["bpc_best_calibrated"]), "T5 BPC not finite: %s" % bpc
    assert bpc["bpc_best_calibrated"] > 0.0, "T5 BPC non-positive: %s" % bpc
    assert 0.0 <= bpc["top1_acc"] <= 1.0, "T5 top1_acc out of [0,1]: %s" % bpc["top1_acc"]
    assert 0.0 <= bpc["top5_acc"] <= 1.0, "T5 top5_acc out of [0,1]: %s" % bpc["top5_acc"]
    assert bpc["top5_acc"] >= bpc["top1_acc"], "T5 top5 < top1: %s" % bpc

    # T6: verdict-shape -- HARD_PASS_CHAIN_GRADE when one arm clears at one V
    def _mk_arm(bpc, sigma0, eig, top1=0.05, top5=0.20):
        return {"bpc_raw": bpc + 0.5, "bpc_best_calibrated": bpc,
                "best_lambda": 0.5, "best_dev_bpc": bpc, "bpc_n_eval": 100,
                "top1_acc": top1, "top5_acc": top5,
                "anisotropy_eigenspread": eig, "cosine_spread": 0.2,
                "eff_rank_norm": 0.5, "mechanism_fired": eig >= 0.05,
                "sigma0_recall": sigma0,
                "wall_encode_s": 0.0, "wall_sanity_s": 0.0, "wall_anisotropy_s": 0.0,
                "wall_bpc_s": 0.0}

    def _mk_unit(V_cap, bpcs, sigmas):
        ba = {al: _mk_arm(b, s, 0.3) for al, b, s in zip(ARMS, bpcs, sigmas)}
        return {"V_cap": V_cap, "seed": 0, "by_arm": ba, "N_DIM": 128, "N": 128,
                "N_TRAIN": 100, "N_HELD": 50, "V_actual": 20, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_unit": 0.01}

    # All near-random null at 2 V's -> HARD_FAIL_NULL
    u1 = _mk_unit(200, [7.50, 7.51, 7.49, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0, 1.0])
    u2 = _mk_unit(1000, [7.50, 7.49, 7.51, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0, 1.0])
    # 3 seeds each
    v_n, m_n, _ = compute_verdict([u1, u1, u1, u2, u2, u2])
    assert v_n == "HARD_FAIL", "T6a expected HARD_FAIL (NULL) got %s msg=%s" % (v_n, m_n[:300])

    # FOLDIAK_v2 at V=200 clears HARD_PASS_CHAIN_GRADE: rand=7.50, foldiak=7.25 (lift=0.25)
    u3 = _mk_unit(200, [7.50, 7.50, 7.50, 7.25, 7.50], [1.0, 1.0, 1.0, 1.0, 1.0])
    v_h, m_h, _ = compute_verdict([u3, u3, u3])
    assert v_h == "HARD_PASS", "T6b expected HARD_PASS got %s msg=%s" % (v_h, m_h[:300])

    # CONFOUND_FAIL: 3+ cells with sigma0 < 0.90 (v1-style FOLDIAK collapse)
    u4 = _mk_unit(200, [7.50, 7.50, 7.50, 8.50, 7.50], [1.0, 1.0, 1.0, 0.0, 1.0])
    u5 = _mk_unit(1000, [7.50, 7.50, 7.50, 8.50, 7.50], [1.0, 1.0, 1.0, 0.0, 1.0])
    u6 = _mk_unit(4000, [7.50, 7.50, 7.50, 8.50, 7.50], [1.0, 1.0, 1.0, 0.0, 1.0])
    v_c, m_c, _ = compute_verdict([u4, u4, u4, u5, u5, u5, u6, u6, u6])
    assert v_c == "CONFOUND_FAIL", "T6c expected CONFOUND_FAIL got %s msg=%s" % (v_c, m_c[:300])

    # T7: per-V provenance diagnostic recorded when V=4000 present
    u_p1 = _mk_unit(4000, [7.50, 7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0, 1.0])
    _, _, det = compute_verdict([u_p1, u_p1, u_p1])
    assert "provenance_diagnostic" in det, "T7 missing provenance block: %s" % list(det.keys())
    assert det["provenance_diagnostic"]["random_bpc_at_V4000"] == 7.50, \
        "T7 provenance bpc mismatch: %s" % det["provenance_diagnostic"]

    # T8: band ordering well-formed
    assert HP_CHAIN_GRADE_BPC_LIFT > HP_BPC_LIFT, "T8 chain_grade lift > hp lift"
    assert HP_CHAIN_GRADE_SIGMA0 > HF_NULL_SIGMA0 > CONFOUND_SIGMA0 - 1e-9, "T8 sigma0 bands"

    # T9: per-(V, seed) checkpoint key shape  -- "V<V>_seed<seed>" composes correctly
    key_test = "V%d_seed%d" % (200, 17)
    assert key_test == "V200_seed17", "T9 key shape: %s" % key_test

    print("[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 5-arms shape+sigma0 + "
          "T3b SURGICAL FOLDIAK FIX validated + T4 anisotropy + T5 BPC+top1/top5 + "
          "T6 verdict-shape (NULL/HP/CONFOUND) + T7 provenance + T8 band ordering + "
          "T9 ckpt-key shape OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d V_GRID=%s seeds=%s arms=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_GRID, SEEDS, ARMS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "substrate-unsupervised-anisotropic-encoder-biology-native-v2-surgical-PLUS-PHASE-DIAGRAM"}
    t0 = time.time()
    _T0_REF[0] = t0
    # Outer loop: V; inner loop: seed. Per-(V, seed) checkpoint.
    for V_cap in V_GRID:
        for seed in SEEDS:
            key = "V%d_seed%d" % (V_cap, seed)
            existing = aggregate_partials(out_dir, [key], run_config=run_cfg)
            if key in existing:
                print("[ckpt] %s done; skip" % key, flush=True)
                continue
            unit = run_unit_at_V(V_cap, seed)
            write_partial_key(out_dir, key, unit)
    all_keys = ["V%d_seed%d" % (V, sd) for V in V_GRID for sd in SEEDS]
    units = list(aggregate_partials(out_dir, all_keys, run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "V_grid": V_GRID,
        "n_units": len(units),
        "n_units_expected": len(V_GRID) * len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_" + ANCHOR_NAME,
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
