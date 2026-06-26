"""substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure.

Cell H' v2c = v2b structurally-identical fork; SCOPE NARROWED to V=10000 ONLY.

Forked from v2b (substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak)
to close the V=10000 phase-diagram point. The v2b cell completed 9/12 phase points
(V=200, V=1000, V=4000 x 3 seeds) before timing out at the 3h cap; the V=10000
phase point did not complete on any seed. v2c addresses ONLY the missing
V=10000 phase point at the same 4 arms x 3 seeds (12 new partials), to be
merged with v2b's 9 surviving partials for a 12-point phase diagram closure.

What changed from v2b (substantive):

  1. V_GRID = [10000] ONLY (no phase scan; single V value).
  2. N_TRAIN locked to 400000 (NOT V*100 = 1M; per user spec for bounded wall).
     Rationale: v2b at V=4000 used N_TRAIN=400000 by the V*100 rule; at V=10000
     v2b's V*100 rule would have requested 1M which was the dominant cost in
     the 3h timeout. v2c holds N_TRAIN=400000 to keep wall <= 4h on 3 seeds.
     This makes V=10000 in v2c moderately less data-rich per encoder than
     v2b's V=200/1000/4000, but the production-scale capacity-tight regime
     (N/V=0.82 here vs 2.0 at v2b's V=4000) is the load-bearing question.
  3. CONFIG_VERSION schema retagged: subUnsupAnisBio-v2c-V10000_ONLY_CLOSURE.
  4. summary prefix retagged: BIO4xV10K (was BIO4xV).
  5. honest_scope updated: "v2c V=10000-only closure of v2b 9/12 partials".
  6. Bands LOCKED at module init via assert (load-bearing prospective).

What is PRESERVED (load-bearing; structurally-identical to v2b):

  - 4 arms (RANDOM_BIPOLAR / OLSHAUSEN / DEEPWALK / KOHONEN).
  - N_DIM=8192, SPARSE_F=0.02, K_WTA=5, INGEST_CHUNK=8192.
  - Seeds [7, 17, 23] (apples-to-apples with v2b for merge).
  - All encoder functions UNCHANGED (literal copy of v2b sources).
  - All metric / sigma0 / anisotropy diagnostics UNCHANGED.
  - All self-test gates (T1, T2, T3, T4, T5, T6, T7, T8, T9) UNCHANGED.
  - atexit + per-(V, seed) checkpoint + write_partial_key UNCHANGED.
  - Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm honored.
  - Top-1 + top-5 argmax accuracy (Q discipline).
  - Per-(V, arm) classification using random_BPC AT THAT V as reference.
  - All HARD-band thresholds UNCHANGED (per-arm-at-V classifier identical).

Pre-reg HARD bands at V=10000 (PROSPECTIVE; locked at module init):

  - HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED: at V=10000, DeepWalk top1
    <= RANDOM_top1 - 0.005 AND |OLSHAUSEN_top1 - RANDOM_top1| <= 0.005 AND
    top1_cv <= 0.05 across 3 seeds.
  - HARD_PASS_BIOLOGY_ARM_REVIVAL: 1+ biology arm BEATS RANDOM by >= 0.005
    absolute on top1 AND cv <= 0.05 -> Wave D revival angle at production V.
  - MIDDLE_BAND_ALL_CONVERGE: all 4 arms within +/- 0.005 top1 (capacity
    exhausted; structure no longer discriminates).
  - HARD_FAIL_NULL_AT_V10000: all arms collapse to noise floor
    (random_chance = 1/10000 = 0.0001; if all arms < 0.001 -> capacity
    exhausted before mechanism matters).
  - HARD_FAIL_CELL_BREAKS: NaN at production matmul OR sigma0_recall < 0.5
    on any arm.

Substrate-product significance:

  If v2c V=10000 shows the capacity-dependent trend continues (biology arms
  hurt at V=10000 like at V=4000), Wave D encoder upgrade closes at production
  V as informative negative -- Mu-Viswanath confirmed at capacity-tight regime;
  biology arms work only in capacity-rich regime where substrate-product won't
  operate.

  If v2c V=10000 shows surprising biology arm lift at production V, Wave D
  revival angle opens for Path C anisotropic encoder for Barrier 1.

  Either outcome closes the encoder question definitively.

Operating disciplines (UNCHANGED from v2b):
  - D2 atexit + per-(V, seed) checkpoint MANDATORY (recover partial work).
  - Per Fix #28: per-(arm, V) metrics in detail.by_arm_V_agg; verdict_msg cites.
  - Per Fix #17: timeout = 14400s (4h; generous buffer; 1-2h/seed x 3 seeds).
  - Fix #20: no pipe-tail subprocess monitoring (atexit + mtime).
  - ASCII-only per feedback_ascii_only_in_scripts.
  - atexit synthesizer (Skunkworks #4): always produce metrics.json on timeout.
  - Substrate-only: _LLM_CALL_COUNTER = [0]; pure numpy; no torch import.

Cites:
  - experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py
    (immediate parent; structurally identical except V_GRID + N_TRAIN scope).
  - preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md
    (parent prereg; bands ported verbatim per-arm-at-V).
  - Mu-Viswanath spectrum-of-decisions framework (capacity-tight regime
    expected to suppress anisotropy lift).

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

ANCHOR_NAME = "substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only_closure"
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
# Pre-reg HARD bands at V=10000 (PROSPECTIVE; locked at module init)
# ============================================================================

# Per-arm-at-V classification thresholds (per-arm, per-V; vs random_BPC at THAT V)
# UNCHANGED from v2b (load-bearing for verdict computation).
HP_CHAIN_GRADE_BPC_LIFT = 0.20   # arm_bpc <= rand_bpc - 0.20
HP_CHAIN_GRADE_SIGMA0 = 0.95
HP_CHAIN_GRADE_CV = 0.05

HP_BPC_LIFT = 0.10               # arm_bpc <= rand_bpc - 0.10
HP_SIGMA0 = 0.90

HF_NULL_BPC_BAND = 0.05          # |arm_bpc - rand_bpc| < 0.05
HF_NULL_SIGMA0 = 0.90            # AND sigma0 >= 0.90 (legit null)

CONFOUND_SIGMA0 = 0.90           # sigma0 < 0.90 = cleanup-integrity fail

HF_HURTS_BPC_GAIN = 0.10         # arm_bpc >= rand_bpc + 0.10

# v2c-NEW top1 bands at V=10000 (apply on top of per-arm BPC bands).
# These are CAPACITY-TIGHT regime bands per user spec; load-bearing for
# whether biology arms revive or stay aligned with v2b's V=4000 trend.
V10K_PHASE_TRANSITION_LIFT_NEG = 0.005   # DeepWalk top1 <= RANDOM - 0.005
V10K_PHASE_TRANSITION_TIE_BAND = 0.005   # |OLSHAUSEN_top1 - RANDOM_top1| <= 0.005
V10K_REVIVAL_LIFT_POS = 0.005            # arm top1 >= RANDOM + 0.005
V10K_CONVERGE_BAND = 0.005               # all arms within +/- 0.005 of RANDOM top1
V10K_NULL_NOISE_FLOOR = 0.001            # all arms < 0.001 top1 (random_chance = 1e-4)
V10K_TOP1_CV_MAX = 0.05                  # cv <= 0.05 for chain-grade claim

# Band-ordering invariants (load-bearing self-test gate)
assert V10K_PHASE_TRANSITION_LIFT_NEG > 0
assert V10K_PHASE_TRANSITION_TIE_BAND > 0
assert V10K_REVIVAL_LIFT_POS > 0
assert V10K_CONVERGE_BAND > 0
assert V10K_NULL_NOISE_FLOOR > 0
assert V10K_TOP1_CV_MAX > 0
assert HP_CHAIN_GRADE_BPC_LIFT > HP_BPC_LIFT
assert HP_CHAIN_GRADE_SIGMA0 > HF_NULL_SIGMA0

# Provenance rail (unchanged from v2b; only fires if V=4000 ever included; v2c
# does not include V=4000, so this is dormant in v2c. Kept for verdict symmetry.)
SANITY_FAIR_HARNESS_BPC = 7.3065
SANITY_FAIR_HARNESS_TOL = 0.20

# Mechanism-fired diagnostic
SANITY_METHODOLOGY_EIGENSPREAD_MIN = 0.05

# Cell-break gates
HF_CELL_BREAKS_SIGMA0_FLOOR = 0.5

# ============================================================================
# Config
# ============================================================================

N_DIM = 8192
SPARSE_F = 0.02
K_WTA = 5
INGEST_CHUNK = 8192
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]

# v2c scope: V_GRID = [10000] ONLY (no phase scan; closure of v2b's missing point).
V_GRID_FULL = [10000]
# Smoke uses a smaller V to verify scale-up infrastructure without paying the
# V=10000 wall. V=2000 is in the middle of v2b's V=1000 / V=4000 partials so it
# exercises the same code paths at lower cost.
V_GRID_SMOKE = [2000]

# N_TRAIN locked at 400000 (NOT V*100; per user spec for bounded wall).
N_TRAIN_FIXED = 400000
# Smoke N_TRAIN is intentionally tiny -- smoke is a scale-up infrastructure test
# (NaN-free at matmul + sigma0 + verdict-shape) NOT a science run. Bounded at
# 20000 per Skunkworks smoke discipline; <30s wall total per user spec.
N_TRAIN_SMOKE = 20000

def _n_train_for_V(V: int) -> int:
    # v2c: fixed 400K in full mode; small 20K in smoke mode (infra-only).
    if RUN_MODE == "full":
        return N_TRAIN_FIXED
    return N_TRAIN_SMOKE

def _n_held_for_V(V: int) -> int:
    return max(1000, V * 20)


def _n_heldout_words_for_V(V: int) -> int:
    return max(20, min(V // 10, 250))


if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    V_GRID = V_GRID_FULL
    N_OLSHAUSEN_BATCHES = 80
    N_SOM_EPOCHS = 12
    N_BIGRAM_WALKS = 4000
    WALK_LEN = 12
else:
    SEEDS = [7]
    V_GRID = V_GRID_SMOKE
    N_OLSHAUSEN_BATCHES = 6
    N_SOM_EPOCHS = 2
    N_BIGRAM_WALKS = 200
    WALK_LEN = 8

# v2b/v2c: FOLDIAK arm DROPPED (algorithmic axis-flip bug; v3 redesign filed
# with Research). 4 arms remain (Olshausen + DeepWalk + Kohonen + random).
ARMS = [
    "ARM_RANDOM_BIPOLAR_BASELINE",
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING",
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH",
    "ARM_KOHONEN_SOM_TOPOGRAPHIC",
]

CONFIG_VERSION = (
    "subUnsupAnisBio-v2c-V10000_ONLY_CLOSURE: N_DIM=%d SPARSE_F=%.3f K_WTA=%d "
    "V_GRID=%s arms=%s seeds=%s mode=%s N_TRAIN_FIXED=%d; bands HP_CHAIN_LIFT>=%.3f "
    "sigma0>=%.3f HP_LIFT>=%.3f sigma0>=%.3f HF_NULL_BAND<=%.3f CONFOUND_SIGMA0<%.3f "
    "V10K_PHASE_TRANS_NEG<=%.4f V10K_TIE_BAND<=%.4f V10K_REVIVAL_POS>=%.4f "
    "V10K_CONVERGE<=%.4f V10K_NOISE_FLOOR<%.4f V10K_TOP1_CV<=%.4f"
) % (
    N_DIM, SPARSE_F, K_WTA, V_GRID, ARMS, SEEDS, RUN_MODE, N_TRAIN_FIXED,
    HP_CHAIN_GRADE_BPC_LIFT, HP_CHAIN_GRADE_SIGMA0,
    HP_BPC_LIFT, HP_SIGMA0, HF_NULL_BPC_BAND, CONFOUND_SIGMA0,
    V10K_PHASE_TRANSITION_LIFT_NEG, V10K_PHASE_TRANSITION_TIE_BAND,
    V10K_REVIVAL_LIFT_POS, V10K_CONVERGE_BAND, V10K_NULL_NOISE_FLOOR,
    V10K_TOP1_CV_MAX,
)


# ============================================================================
# Substrate primitives (numpy; substrate-native) -- UNCHANGED from v2b
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
# Corpus loading + vocab -- UNCHANGED from v2b
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
# ARM encoders -- UNCHANGED literal copy from v2b
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
    """ARM 2: Olshausen-Field sparse-coding via forward-only SoftHebb."""
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
    """ARM 3: DeepWalk-on-bigram-graph. UNCHANGED from v2b."""
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


# --- FOLDIAK encoder DROPPED in v2b/v2c (algorithmic axis-flip bug; v3 deferred) ---


def encoder_kohonen_som(vocab: List[str], n_dim: int, seed: int,
                         idx_train: np.ndarray) -> np.ndarray:
    """ARM 4: Kohonen SOM. UNCHANGED from v2b."""
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
    "ARM_RANDOM_BIPOLAR_BASELINE":         encoder_random_bipolar,
    "ARM_OLSHAUSEN_FIELD_SPARSE_CODING":   encoder_olshausen_field,
    "ARM_DEEPWALK_ON_BIGRAM_GRAPH":        encoder_deepwalk_on_bigram,
    "ARM_KOHONEN_SOM_TOPOGRAPHIC":         encoder_kohonen_som,
}


# ============================================================================
# Metric B: BPC on text8 held -- UNCHANGED from v2b
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
    """Hebbian-substrate LM BPC + top-1 + top-5 argmax accuracy."""
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
    top1 = np.argmax(sub_logits, axis=1)
    top1_acc = float((top1 == nxt).mean())
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
# Anisotropy diagnostic -- UNCHANGED from v2b
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
# sigma=0 cleanup sanity (CONFOUND_FAIL detector) -- UNCHANGED from v2b
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
# Per-(V, seed) unit -- UNCHANGED from v2b
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
# Verdict -- per-(V, arm) classifier UNCHANGED from v2b; cell-level adds
#           v2c-specific V=10000 top1 phase-transition + revival + converge bands
# ============================================================================

def _classify_arm_at_V(arm_metrics: dict, random_bpc: float) -> dict:
    """Per-(V, arm) classification using random_bpc AT THAT V as reference.

    UNCHANGED from v2b -- BPC-based classifier (load-bearing for cross-cell
    cert compatibility). v2c top1-based bands layer ON TOP for cell-level rollup.
    """
    bpc = float(arm_metrics["bpc_best_calibrated_mean"])
    bpc_cv = float(arm_metrics["bpc_best_calibrated_cv"])
    sigma0 = float(arm_metrics["sigma0_recall_mean"])
    eig = float(arm_metrics["anisotropy_eigenspread_mean"])
    lift_bpc = random_bpc - bpc

    if sigma0 < CONFOUND_SIGMA0:
        return {"classification": "CONFOUND_FAIL", "lift_bpc": lift_bpc,
                "sigma0_confound": True,
                "mechanism_fired": eig >= SANITY_METHODOLOGY_EIGENSPREAD_MIN}
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


def _classify_v10k_top1(by_arm_V_agg: dict, top1_seeds: dict) -> dict:
    """v2c-NEW cell-level top1 classification at V=10000.

    Returns one of:
      - HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED
      - HARD_PASS_BIOLOGY_ARM_REVIVAL
      - MIDDLE_BAND_ALL_CONVERGE
      - HARD_FAIL_NULL_AT_V10000
      - HARD_FAIL_CELL_BREAKS
      - MIDDLE_BAND (catch-all)

    top1_seeds is {arm_label: [top1_seed1, top1_seed2, top1_seed3]} for CV calc.
    """
    V = 10000
    rand_t1 = by_arm_V_agg["ARM_RANDOM_BIPOLAR_BASELINE"][V]["top1_acc_mean"]
    olsh_t1 = by_arm_V_agg["ARM_OLSHAUSEN_FIELD_SPARSE_CODING"][V]["top1_acc_mean"]
    deep_t1 = by_arm_V_agg["ARM_DEEPWALK_ON_BIGRAM_GRAPH"][V]["top1_acc_mean"]
    koh_t1 = by_arm_V_agg["ARM_KOHONEN_SOM_TOPOGRAPHIC"][V]["top1_acc_mean"]

    # HARD_FAIL_CELL_BREAKS: NaN at production matmul OR sigma0 < 0.5
    for al in ARMS:
        s0 = by_arm_V_agg[al][V]["sigma0_recall_mean"]
        bpc = by_arm_V_agg[al][V]["bpc_best_calibrated_mean"]
        if not (np.isfinite(bpc) and np.isfinite(s0)):
            return {"v10k_class": "HARD_FAIL_CELL_BREAKS",
                    "reason": "non-finite metric on arm=%s" % al,
                    "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                    "deep_t1": deep_t1, "koh_t1": koh_t1}
        if s0 < HF_CELL_BREAKS_SIGMA0_FLOOR:
            return {"v10k_class": "HARD_FAIL_CELL_BREAKS",
                    "reason": "sigma0=%.3f < %.3f on arm=%s" % (
                        s0, HF_CELL_BREAKS_SIGMA0_FLOOR, al),
                    "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                    "deep_t1": deep_t1, "koh_t1": koh_t1}

    # HARD_FAIL_NULL_AT_V10000: all arms collapse to noise floor (< 0.001)
    if (rand_t1 < V10K_NULL_NOISE_FLOOR and olsh_t1 < V10K_NULL_NOISE_FLOOR
            and deep_t1 < V10K_NULL_NOISE_FLOOR and koh_t1 < V10K_NULL_NOISE_FLOOR):
        return {"v10k_class": "HARD_FAIL_NULL_AT_V10000",
                "reason": "all 4 arms top1 < %.4f (capacity exhausted)" % V10K_NULL_NOISE_FLOOR,
                "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                "deep_t1": deep_t1, "koh_t1": koh_t1}

    # Compute per-arm top1 CV across seeds (load-bearing for chain-grade gating)
    def _cv(vals):
        m = float(np.mean(vals))
        s = float(np.std(vals))
        return s / max(abs(m), 1e-6)

    rand_cv = _cv(top1_seeds.get("ARM_RANDOM_BIPOLAR_BASELINE", [rand_t1]))
    olsh_cv = _cv(top1_seeds.get("ARM_OLSHAUSEN_FIELD_SPARSE_CODING", [olsh_t1]))
    deep_cv = _cv(top1_seeds.get("ARM_DEEPWALK_ON_BIGRAM_GRAPH", [deep_t1]))
    koh_cv = _cv(top1_seeds.get("ARM_KOHONEN_SOM_TOPOGRAPHIC", [koh_t1]))
    cv_ok = (rand_cv <= V10K_TOP1_CV_MAX and olsh_cv <= V10K_TOP1_CV_MAX
             and deep_cv <= V10K_TOP1_CV_MAX and koh_cv <= V10K_TOP1_CV_MAX)

    # HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED:
    #   DeepWalk top1 <= RANDOM - 0.005 AND |Olshausen - RANDOM| <= 0.005 AND cv_ok
    # (epsilon tolerance for fp-roundoff at band boundaries: 1e-9)
    EPS_BAND = 1e-9
    deep_lift = deep_t1 - rand_t1   # negative = DeepWalk hurts (predicted)
    olsh_tie = abs(olsh_t1 - rand_t1)
    if (deep_lift <= -V10K_PHASE_TRANSITION_LIFT_NEG + EPS_BAND
            and olsh_tie <= V10K_PHASE_TRANSITION_TIE_BAND + EPS_BAND
            and cv_ok):
        return {"v10k_class": "HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED",
                "reason": ("DeepWalk lift=%.4f (<=%.4f) AND Olshausen tie=%.4f (<=%.4f) "
                           "AND all-arm cv<=%.3f (rand=%.3f olsh=%.3f deep=%.3f koh=%.3f)") % (
                    deep_lift, -V10K_PHASE_TRANSITION_LIFT_NEG,
                    olsh_tie, V10K_PHASE_TRANSITION_TIE_BAND,
                    V10K_TOP1_CV_MAX, rand_cv, olsh_cv, deep_cv, koh_cv),
                "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                "deep_t1": deep_t1, "koh_t1": koh_t1,
                "deep_lift": deep_lift, "olsh_tie": olsh_tie,
                "top1_cv": {"rand": rand_cv, "olsh": olsh_cv,
                            "deep": deep_cv, "koh": koh_cv}}

    # HARD_PASS_BIOLOGY_ARM_REVIVAL: 1+ biology arm beats RANDOM by >= 0.005 AND cv_ok
    bio_lifts = {
        "OLSHAUSEN": olsh_t1 - rand_t1,
        "DEEPWALK":  deep_t1 - rand_t1,
        "KOHONEN":   koh_t1 - rand_t1,
    }
    revivers = [(name, lift) for name, lift in bio_lifts.items()
                if lift >= V10K_REVIVAL_LIFT_POS - EPS_BAND]
    if revivers and cv_ok:
        return {"v10k_class": "HARD_PASS_BIOLOGY_ARM_REVIVAL",
                "reason": ("biology arms beating RANDOM by >=%.4f: %s (cv all <=%.3f)") % (
                    V10K_REVIVAL_LIFT_POS, revivers, V10K_TOP1_CV_MAX),
                "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                "deep_t1": deep_t1, "koh_t1": koh_t1,
                "bio_lifts": bio_lifts,
                "top1_cv": {"rand": rand_cv, "olsh": olsh_cv,
                            "deep": deep_cv, "koh": koh_cv}}

    # MIDDLE_BAND_ALL_CONVERGE: all 4 arms within +/- 0.005 of RANDOM top1
    spans = [abs(t - rand_t1) for t in (olsh_t1, deep_t1, koh_t1)]
    if all(s <= V10K_CONVERGE_BAND + EPS_BAND for s in spans):
        return {"v10k_class": "MIDDLE_BAND_ALL_CONVERGE",
                "reason": ("all biology arms within +/-%.4f of RANDOM top1 (spans=%s); "
                           "capacity exhausted, structure no longer discriminates") % (
                    V10K_CONVERGE_BAND, [round(s, 4) for s in spans]),
                "rand_t1": rand_t1, "olsh_t1": olsh_t1,
                "deep_t1": deep_t1, "koh_t1": koh_t1,
                "spans": spans}

    # MIDDLE_BAND (catch-all): mixed signals or cv too high
    return {"v10k_class": "MIDDLE_BAND",
            "reason": ("no v10k-prereg band fired cleanly; rand=%.4f olsh=%.4f deep=%.4f "
                       "koh=%.4f bio_lifts=%s cv_ok=%s") % (
                rand_t1, olsh_t1, deep_t1, koh_t1, bio_lifts, cv_ok),
            "rand_t1": rand_t1, "olsh_t1": olsh_t1,
            "deep_t1": deep_t1, "koh_t1": koh_t1,
            "top1_cv": {"rand": rand_cv, "olsh": olsh_cv,
                        "deep": deep_cv, "koh": koh_cv}}


def compute_verdict(units):
    """Cell-level verdict from per-(V, seed) units."""
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_V: Dict[int, List[dict]] = defaultdict(list)
    for u in units:
        by_V[int(u["V_cap"])].append(u)
    by_arm_V_agg: Dict[str, Dict[int, dict]] = {al: {} for al in ARMS}
    classifications: Dict[str, Dict[int, dict]] = {al: {} for al in ARMS}
    # Track per-arm per-seed top1 for v10k CV computation
    top1_seeds_by_arm_V: Dict[int, Dict[str, list]] = defaultdict(dict)

    provenance = {}

    for V_cap in sorted(by_V.keys()):
        V_units = by_V[V_cap]
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
            top1_seeds_by_arm_V[V_cap][arm_label] = list(top1_vals)
        rand_bpc_V = by_arm_V_agg["ARM_RANDOM_BIPOLAR_BASELINE"][V_cap]["bpc_best_calibrated_mean"]
        for arm_label in ARMS:
            classifications[arm_label][V_cap] = _classify_arm_at_V(
                by_arm_V_agg[arm_label][V_cap], rand_bpc_V)
        if V_cap == 4000:
            drift = rand_bpc_V - SANITY_FAIR_HARNESS_BPC
            provenance["random_bpc_at_V4000"] = round(rand_bpc_V, 4)
            provenance["fair_harness_target"] = SANITY_FAIR_HARNESS_BPC
            provenance["drift_vs_fair_harness"] = round(drift, 4)
            provenance["within_tol"] = abs(drift) <= SANITY_FAIR_HARNESS_TOL
            provenance["tol"] = SANITY_FAIR_HARNESS_TOL
            provenance["note"] = "v2c does NOT run V=4000; dormant block."

    # v2c-NEW: V=10000 top1 cell-level classifier (load-bearing)
    v10k_block = None
    if 10000 in by_V:
        v10k_block = _classify_v10k_top1(by_arm_V_agg, top1_seeds_by_arm_V[10000])

    # Per-(arm, V) BPC-based rollup (preserved from v2b for cross-cert continuity)
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
        "v10k_top1_classification": v10k_block,
        "honest_scope": (
            "v2c V=10000-only closure cell: 4-arm biology-native UNSUPERVISED "
            "anisotropic encoder at N_DIM=%d, N_TRAIN_FIXED=%d, seeds=%s. Designed to "
            "merge with v2b 9/12 partials (V=200/1000/4000 x 3 seeds) for a "
            "12-point phase-diagram analysis. v2c bands at V=10000 are PROSPECTIVE "
            "top1-based (capacity-tight regime); v2b BPC-based per-arm classifier "
            "preserved for cross-cert continuity."
        ) % (N_DIM, N_TRAIN_FIXED, SEEDS),
        "cites": [
            "experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py",
            "preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.md",
            "preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v2c_V10000_only.md",
            "Olshausen_Field_1996_Nature_381_607",
            "Moraitis_2107_05747_SoftHebb",
            "Perozzi_2014_DeepWalk",
            "Kohonen_1982_SOM",
            "Mu_Viswanath_spectrum_of_decisions_capacity_tight_regime",
        ],
    }

    parts = []
    for V_cap in sorted(by_V.keys()):
        rand_bpc_V = by_arm_V_agg["ARM_RANDOM_BIPOLAR_BASELINE"][V_cap]["bpc_best_calibrated_mean"]
        for arm_label in biology_arms:
            a = by_arm_V_agg[arm_label][V_cap]
            cl = classifications[arm_label][V_cap]["classification"]
            lift = classifications[arm_label][V_cap]["lift_bpc"]
            parts.append("%s@V=%d=bpc%.3f(lift%+.3f vs rand%.3f)/sig0%.3f[%s]/top1%.4f" % (
                arm_label.replace("ARM_", "")[:14], V_cap,
                a["bpc_best_calibrated_mean"], lift, rand_bpc_V,
                a["sigma0_recall_mean"], cl, a["top1_acc_mean"]))
    summary = "BIO4xV10K: " + " | ".join(parts)
    if v10k_block:
        summary += " || V10K_top1: rand=%.4f olsh=%.4f deep=%.4f koh=%.4f -> %s" % (
            v10k_block["rand_t1"], v10k_block["olsh_t1"], v10k_block["deep_t1"],
            v10k_block["koh_t1"], v10k_block["v10k_class"])

    # v2c cell-level verdict: V=10000 top1 classifier takes precedence; BPC-based
    # per-arm rollup remains in detail for v2b-compat.
    if v10k_block is not None:
        v10k_cl = v10k_block["v10k_class"]
        if v10k_cl == "HARD_FAIL_CELL_BREAKS":
            msg = ("HARD_FAIL_CELL_BREAKS at V=10000: %s. " % v10k_block["reason"]) + summary
            return ("HARD_FAIL", msg, detail)
        if v10k_cl == "HARD_FAIL_NULL_AT_V10000":
            msg = ("HARD_FAIL_NULL_AT_V10000: %s. " % v10k_block["reason"]) + summary
            return ("HARD_FAIL", msg, detail)
        if v10k_cl == "HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED":
            msg = ("HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED at V=10000: %s. "
                   "Wave D revival angle CLOSED; substrate-product locks in WITHOUT "
                   "biology-native anisotropic encoder upgrade. " % v10k_block["reason"]) + summary
            return ("HARD_PASS", msg, detail)
        if v10k_cl == "HARD_PASS_BIOLOGY_ARM_REVIVAL":
            msg = ("HARD_PASS_BIOLOGY_ARM_REVIVAL at V=10000: %s. "
                   "Wave D revival angle OPENS for Path C. " % v10k_block["reason"]) + summary
            return ("HARD_PASS", msg, detail)
        if v10k_cl == "MIDDLE_BAND_ALL_CONVERGE":
            msg = ("MIDDLE_BAND_ALL_CONVERGE at V=10000: %s. " % v10k_block["reason"]) + summary
            return ("MIDDLE_BAND", msg, detail)
        # MIDDLE_BAND catch-all
        msg = ("MIDDLE_BAND at V=10000: %s. " % v10k_block["reason"]) + summary
        return ("MIDDLE_BAND", msg, detail)

    # If V=10000 missing entirely (degenerate; shouldn't happen for v2c),
    # fall back to v2b-style rollup.
    if any_chain_grade:
        return ("HARD_PASS",
                ("HARD_PASS_CHAIN_GRADE: %s. " % any_chain_grade) + summary, detail)
    if any_hard_pass:
        return ("HARD_PASS",
                ("HARD_PASS: %s. " % any_hard_pass) + summary, detail)
    total_bio_cells = len(biology_arms) * len(by_V)
    if len(null_cells) == total_bio_cells:
        return ("HARD_FAIL",
                ("HARD_FAIL_NULL: all biology arms null. ") + summary, detail)
    if len(confound_cells) >= 3:
        return ("CONFOUND_FAIL",
                ("CONFOUND_FAIL: %d cells. " % len(confound_cells)) + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND fallback. " + summary, detail)


# ============================================================================
# atexit synthesizer (Skunkworks #4) -- UNCHANGED from v2b
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
# Self-test (mechanism + verdict shape + v2c-NEW V=10000 top1 classifier)
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
    assert len(ENCODERS) == 4, "T3 v2c expected 4 arms; got %d" % len(ENCODERS)
    for arm_name, fn in ENCODERS.items():
        E_t = fn(vocab_t, 128, seed=0, idx_train=idx_t)
        assert E_t.shape == (20, 128), "T3 %s shape: %s" % (arm_name, E_t.shape)
        assert np.isfinite(E_t).all(), \
            "T3 %s produced non-finite values" % arm_name
        sr = cleanup_sigma0_sanity(E_t, seed=0, n_eval=20)
        assert sr >= 0.90, "T3 %s sigma=0 sanity recall=%.3f < 0.90" % (arm_name, sr)

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

    # T6: verdict-shape -- v2b-compat per-arm BPC classifier
    def _mk_arm(bpc, sigma0, eig, top1=0.05, top5=0.20):
        return {"bpc_raw": bpc + 0.5, "bpc_best_calibrated": bpc,
                "best_lambda": 0.5, "best_dev_bpc": bpc, "bpc_n_eval": 100,
                "top1_acc": top1, "top5_acc": top5,
                "anisotropy_eigenspread": eig, "cosine_spread": 0.2,
                "eff_rank_norm": 0.5, "mechanism_fired": eig >= 0.05,
                "sigma0_recall": sigma0,
                "wall_encode_s": 0.0, "wall_sanity_s": 0.0, "wall_anisotropy_s": 0.0,
                "wall_bpc_s": 0.0}

    def _mk_unit(V_cap, bpcs, sigmas, top1s=None):
        if top1s is None:
            top1s = [0.05] * len(ARMS)
        ba = {al: _mk_arm(b, s, 0.3, top1=t1)
              for al, b, s, t1 in zip(ARMS, bpcs, sigmas, top1s)}
        return {"V_cap": V_cap, "seed": 0, "by_arm": ba, "N_DIM": 128, "N": 128,
                "N_TRAIN": 100, "N_HELD": 50, "V_actual": 20, "run_mode": "smoke",
                "config_version": "selftest", "elapsed_s_unit": 0.01}

    # T6a: v2c V=10000 HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED:
    # RANDOM top1=0.0150, OLSHAUSEN=0.0152 (tie within 0.005), DEEPWALK=0.0090 (-0.006 lift),
    # KOHONEN=0.0150. All sigma0=1.0. Margin-of-0.001 inside band to avoid boundary fp.
    u_pt = _mk_unit(10000, [7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0],
                    top1s=[0.0150, 0.0152, 0.0090, 0.0150])
    v_pt, m_pt, det_pt = compute_verdict([u_pt, u_pt, u_pt])
    assert v_pt == "HARD_PASS" and "PHASE_TRANSITION_CONFIRMED" in m_pt, \
        "T6a expected HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED got v=%s msg=%s" % (
            v_pt, m_pt[:400])
    assert det_pt["v10k_top1_classification"]["v10k_class"] == \
        "HARD_PASS_CAPACITY_PHASE_TRANSITION_CONFIRMED", \
        "T6a v10k_class wrong: %s" % det_pt["v10k_top1_classification"]

    # T6b: v2c V=10000 HARD_PASS_BIOLOGY_ARM_REVIVAL: OLSHAUSEN beats RANDOM by 0.01
    u_rev = _mk_unit(10000, [7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0],
                     top1s=[0.0150, 0.0250, 0.0150, 0.0150])
    v_rev, m_rev, det_rev = compute_verdict([u_rev, u_rev, u_rev])
    assert v_rev == "HARD_PASS" and "REVIVAL" in m_rev, \
        "T6b expected HARD_PASS_BIOLOGY_ARM_REVIVAL got v=%s msg=%s" % (v_rev, m_rev[:400])

    # T6c: v2c V=10000 MIDDLE_BAND_ALL_CONVERGE: all 4 arms within 0.005 of RANDOM
    u_conv = _mk_unit(10000, [7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0],
                      top1s=[0.0150, 0.0153, 0.0148, 0.0151])
    v_conv, m_conv, det_conv = compute_verdict([u_conv, u_conv, u_conv])
    assert v_conv == "MIDDLE_BAND" and "ALL_CONVERGE" in m_conv, \
        "T6c expected MIDDLE_BAND_ALL_CONVERGE got v=%s msg=%s" % (v_conv, m_conv[:400])

    # T6d: v2c V=10000 HARD_FAIL_NULL_AT_V10000: all arms collapse to noise floor (<0.001)
    u_null = _mk_unit(10000, [7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 1.0, 1.0],
                      top1s=[0.0005, 0.0005, 0.0005, 0.0005])
    v_null, m_null, det_null = compute_verdict([u_null, u_null, u_null])
    assert v_null == "HARD_FAIL" and "NULL_AT_V10000" in m_null, \
        "T6d expected HARD_FAIL_NULL_AT_V10000 got v=%s msg=%s" % (v_null, m_null[:400])

    # T6e: v2c V=10000 HARD_FAIL_CELL_BREAKS: sigma0 < 0.5 on any arm
    u_break = _mk_unit(10000, [7.50, 7.50, 7.50, 7.50], [1.0, 1.0, 0.3, 1.0],
                       top1s=[0.0150, 0.0150, 0.0150, 0.0150])
    v_break, m_break, det_break = compute_verdict([u_break, u_break, u_break])
    assert v_break == "HARD_FAIL" and "CELL_BREAKS" in m_break, \
        "T6e expected HARD_FAIL_CELL_BREAKS got v=%s msg=%s" % (v_break, m_break[:400])

    # T7: band ordering well-formed (v2c v10k bands)
    assert V10K_PHASE_TRANSITION_LIFT_NEG == V10K_PHASE_TRANSITION_TIE_BAND == \
        V10K_REVIVAL_LIFT_POS == V10K_CONVERGE_BAND == 0.005, \
        "T7 v10k bands all 0.005 by spec"
    assert V10K_NULL_NOISE_FLOOR == 0.001, "T7 noise floor 0.001"
    assert V10K_TOP1_CV_MAX == 0.05, "T7 cv max 0.05"
    assert HF_CELL_BREAKS_SIGMA0_FLOOR == 0.5, "T7 sigma0 floor 0.5"

    # T8: ckpt-key shape composes
    key_test = "V%d_seed%d" % (10000, 17)
    assert key_test == "V10000_seed17", "T8 key shape: %s" % key_test

    # T9: V_GRID_FULL = [10000] only (v2c scope lock)
    assert V_GRID_FULL == [10000], "T9 V_GRID_FULL must be [10000] only in v2c: %s" % V_GRID_FULL
    assert N_TRAIN_FIXED == 400000, "T9 N_TRAIN_FIXED must be 400000 per user spec: %d" % N_TRAIN_FIXED

    print("[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 4-arms shape+sigma0 + "
          "T4 anisotropy + T5 BPC+top1/top5 + T6a/b/c/d/e v10k cell-level classifier "
          "(PHASE_TRANS/REVIVAL/CONVERGE/NULL/BREAKS) + T7 band ordering + "
          "T8 ckpt-key shape + T9 v2c scope-lock OK", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d V_GRID=%s seeds=%s arms=%s N_TRAIN_FIXED=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V_GRID, SEEDS, ARMS, N_TRAIN_FIXED, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "substrate-unsupervised-anisotropic-encoder-biology-native-v2c-V10000-only"}
    t0 = time.time()
    _T0_REF[0] = t0
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
