"""exp_encoding_quality_instrument_v1 -- PLAN STEP 1: an ISOLATED word-encoding quality instrument.

Pre-reg: preregs/exp_encoding_quality_instrument_v1.md (thresholds fixed BEFORE any run).

WHAT THIS IS. An instrument that answers "is a word encoded well?" with NOTHING downstream:
no store, no reader, no selection stage, no retrieval index. It is a pure function of an
encoder `encode(word) -> vector` and a fixed real-word vocabulary.

WHAT THIS IS NOT. It does NOT score our production encoding. Every arm here is a SYNTHETIC
encoder whose true quality is known by construction, because an instrument can only be
validated against arms whose answer is already known. Scoring our encoder is STEP 2.

THE LOAD-BEARING DESIGN DECISION. A random encoding is near-OPTIMAL on identity metrics and
near-CHANCE on structure metrics (random indexing works BECAUSE iid codes are near-orthogonal).
Any single "encoding quality" number that mixes the two is unfalsifiable -- its null sits near
the ceiling on half the metric. That is the mechanism behind "a random decoy scored 0.76 where
it should have been near zero". So this instrument reports TWO AXES, each with its own matched
null AND its own known-answer arm:

  IDENTITY  null = A_COLLAPSE (chance)         ceiling = A_ORACLE_ONEHOT
  STRUCTURE null = A_RANDOM_IID (chance)       ceiling = A_PLANTED_STRUCTURE / A_ORTHOGRAPHIC
                   A_SHUFFLED_PLANTED (chance)

A_RANDOM_IID is gated in BOTH directions: near-ceiling on IDENTITY (K5) and at chance on
STRUCTURE (N2/N3/N4). An instrument that cannot reproduce that split is not measuring two things.

MEASURES: M1 discriminability (vs orthographic near-neighbours + frequency-matched controls),
M2 recoverability (round-trip identity), M3 stability under store-size load, M4 information
destroyed per pipeline stage (Fano lower bound), M5 structure (group AP lift + SimLex rho).

REUSED, NOT REIMPLEMENTED (WIRE DON'T ISLAND): hdlab.char_trigram_encoder.CharTrigramEncoder;
tools.saturation_negative_control (nn_recall_at_1, iid_gaussian_keys, _selftest);
experiments._seed_checkpoint (get_output_dir, write_metrics); tools.exp_checkpoint (per-unit
resume); data/encoder_eval_benchmarks/simlex999.txt (SimLex-999, Hill et al. 2015);
data/corpora/simplewiki/simplewiki_clean_v1.txt (real word frequencies).

VERDICTS: INSTRUMENT_STILL_LOOSE (null gate failed -- publish no quality number)
        > INSTRUMENT_CANNOT_DETECT_QUALITY (known-answer gate failed)
        > INSTRUMENT_SATURATED (metric cannot go down)
        > INSTRUMENT_VALIDATED

ASCII-only. CPU/numpy. No network. No data/foundation read.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units
from tools import saturation_negative_control as SNC
from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "encoding_quality_instrument_v1"

CORPUS = REPO / "data" / "corpora" / "simplewiki" / "simplewiki_clean_v1.txt"
SIMLEX = REPO / "data" / "encoder_eval_benchmarks" / "simlex999.txt"

# ----------------------------------------------------------------------------------
# PRE-REGISTERED CONFIG (preregs/exp_encoding_quality_instrument_v1.md sections 3-5)
# ----------------------------------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

if SMOKE:
    V = 512
    D = 256
    CORPUS_BYTES = 8_000_000
    N_SWEEP = [64, 128, 512]
    N_GATE = 512
    SIGMAS = [1.0, 8.0, 32.0]
    AP_PROBES = 128
    SEEDS = [7]
else:
    V = 4096
    D = 1024
    CORPUS_BYTES = 64_000_000
    N_SWEEP = [128, 512, 1024, 4096]
    N_GATE = 1024
    SIGMAS = [1.0, 4.0, 8.0, 16.0, 32.0]
    AP_PROBES = 1024
    SEEDS = [7, 17, 23]

TOP_DROP = 100          # drop the 100 most frequent tokens (function words)
MIN_LEN = 3
K_DISTRACT = 31         # pool size 32 -> chance 1/32
BUNDLE_B = 8
N_PLANTED_GROUPS = 32
PLANTED_NOISE = 0.3
SIGMA_GATE = 1.0
SIGMA_HIGH = 32.0

# Pre-registered thresholds (section 5b/5c/5d). Frozen; do not edit after a run.
T_N1_COLLAPSE_RECOV_MAX = 0.05
T_N2_N3_LIFT_MAX = 1.15
T_N4_SIMLEX_ABS_MAX = 0.10
T_N5_LIFT_MAX = 1.15
T_N5_RECOV_MIN = 0.90
T_N6_DISC_MAX = 0.10
T_K1_ORACLE_RECOV_MIN = 0.95
T_K2_ORTHO_LIFT_MIN = 3.0
T_K3_PLANTED_LIFT_MIN = 5.0
T_K4_SIMLEX_RHO_MIN = 0.50
T_K5_RANDOM_RECOV_MIN = 0.90
T_S1_RECOV_SPREAD_MIN = 0.50
T_S2_ORACLE_HIGHSIGMA_MAX = 0.80
T_S3_LIFT_SPREAD_MIN = 2.0

ARMS = [
    "A_ORACLE_ONEHOT",
    "A_RANDOM_IID",
    "A_COLLAPSE",
    "A_ORTHOGRAPHIC",
    "A_PLANTED_STRUCTURE",
    "A_SHUFFLED_PLANTED",
    "A_PLANTED_SEMANTIC",
]


# ----------------------------------------------------------------------------------
# vocabulary + golds (all computed from strings / corpus counts; never from any code)
# ----------------------------------------------------------------------------------
def build_vocab(corpus_path: Path, n_bytes: int, v: int) -> Tuple[List[str], np.ndarray]:
    """Return (words, counts) -- the v most frequent [a-z]{MIN_LEN,} tokens after dropping
    the TOP_DROP most frequent, counted over the first n_bytes of the corpus."""
    with open(corpus_path, "rb") as f:
        raw = f.read(n_bytes)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    text = raw.decode("utf-8", errors="ignore").lower()
    counts: Dict[str, int] = {}
    for tok in re.findall(r"[a-z]+", text):
        if len(tok) >= MIN_LEN:
            counts[tok] = counts.get(tok, 0) + 1
    # deterministic order: count desc, then token asc
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    sel = ordered[TOP_DROP:TOP_DROP + v]
    if len(sel) < v:
        raise SystemExit(f"[fatal] corpus yielded only {len(sel)} words, need {v}")
    words = [w for w, _ in sel]
    cnts = np.array([c for _, c in sel], dtype=np.float64)
    return words, cnts


def _trigram_set(w: str) -> set:
    t = " " + w + " "
    return {t[i:i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def build_ortho_neighbours(words: Sequence[str], k: int) -> np.ndarray:
    """[V, k] indices of the k most orthographically similar words (trigram Jaccard),
    computed FROM THE STRINGS ONLY. Ties broken by index for determinism."""
    sets = [_trigram_set(w) for w in words]
    n = len(words)
    # inverted index over trigrams -> candidate generation (V=4096 makes O(V^2) fine too,
    # but the inverted index keeps this near-instant and is exact for Jaccard>0)
    inv: Dict[str, List[int]] = {}
    for i, s in enumerate(sets):
        for t in s:
            inv.setdefault(t, []).append(i)
    out = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        inter: Dict[int, int] = {}
        for t in sets[i]:
            for j in inv[t]:
                if j != i:
                    inter[j] = inter.get(j, 0) + 1
        scored = []
        li = len(sets[i])
        for j, c in inter.items():
            jac = c / float(li + len(sets[j]) - c)
            scored.append((-jac, j))
        scored.sort()
        cand = [j for _, j in scored[:k]]
        if len(cand) < k:  # pad deterministically with nearest indices not already used
            used = set(cand) | {i}
            for j in range(n):
                if len(cand) >= k:
                    break
                if j not in used:
                    cand.append(j)
                    used.add(j)
        out[i] = np.array(cand[:k], dtype=np.int64)
    return out


def build_freq_controls(counts: np.ndarray, ortho: np.ndarray, k: int) -> np.ndarray:
    """[V, k] indices of the k words nearest in log-count, excluding self and any word
    already in that row's orthographic pool."""
    lc = np.log(counts + 1.0)
    order = np.argsort(lc, kind="stable")     # positions sorted by log-count
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    n = len(counts)
    out = np.zeros((n, k), dtype=np.int64)
    for i in range(n):
        banned = set(ortho[i].tolist())
        banned.add(i)
        r = rank[i]
        picked: List[int] = []
        step = 1
        while len(picked) < k and step < n:
            for rr in (r - step, r + step):
                if 0 <= rr < n:
                    j = int(order[rr])
                    if j not in banned:
                        picked.append(j)
                        banned.add(j)
                        if len(picked) >= k:
                            break
            step += 1
        while len(picked) < k:                # degenerate tiny-vocab fallback
            for j in range(n):
                if j not in banned:
                    picked.append(j)
                    banned.add(j)
                    break
        out[i] = np.array(picked[:k], dtype=np.int64)
    return out


def gold_ortho(words: Sequence[str]) -> np.ndarray:
    """Label = shared first 3 characters. Groups with < 3 members get label -1 (excluded
    from AP scoring but retained in the ranking pool)."""
    lab: Dict[str, int] = {}
    raw = np.empty(len(words), dtype=np.int64)
    for i, w in enumerate(words):
        key = w[:3]
        if key not in lab:
            lab[key] = len(lab)
        raw[i] = lab[key]
    counts = np.bincount(raw, minlength=len(lab))
    out = raw.copy()
    out[counts[raw] < 3] = -1
    return out


def gold_freqband(counts: np.ndarray) -> np.ndarray:
    """Label = frequency decile (10 equal-count bands by rank)."""
    n = len(counts)
    order = np.argsort(-counts, kind="stable")
    lab = np.empty(n, dtype=np.int64)
    lab[order] = (np.arange(n) * 10) // n
    return lab


def gold_planted(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.int64) % N_PLANTED_GROUPS


# ----------------------------------------------------------------------------------
# encoders (synthetic arms; each returns an L2-normalised [V, d] float32 code matrix)
# ----------------------------------------------------------------------------------
def _l2n(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _hash_seed(s: str, seed: int) -> int:
    h = hashlib.blake2b(f"{seed}:{s}".encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "big")


def enc_oracle_onehot(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    """One-hot over the vocabulary; d is IGNORED (runs at d = V). Information-theoretic
    reference, NOT dimension-matched to the other arms (pre-reg section 6)."""
    n = len(words)
    return np.eye(n, dtype=np.float32)


def enc_random_iid(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    X = np.zeros((len(words), d), dtype=np.float32)
    for i, w in enumerate(words):
        X[i] = np.random.default_rng(_hash_seed(w, seed)).standard_normal(d)
    return _l2n(X)


def enc_collapse(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    base = np.random.default_rng(seed).standard_normal(d).astype(np.float32)
    X = np.tile(base, (len(words), 1))
    for i, w in enumerate(words):
        X[i] += 1e-3 * np.random.default_rng(_hash_seed(w, seed) ^ 0xABCD).standard_normal(d)
    return _l2n(X)


def enc_orthographic(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    enc = CharTrigramEncoder(n_dim=d)
    X = np.stack([np.asarray(enc.encode(w), dtype=np.float32) for w in words])
    return _l2n(X)


def enc_planted_structure(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    lab = gold_planted(len(words))
    g = np.random.default_rng(seed ^ 0x5EED)
    basis = _l2n(g.standard_normal((N_PLANTED_GROUPS, d)))
    X = np.zeros((len(words), d), dtype=np.float32)
    for i, w in enumerate(words):
        eps = np.random.default_rng(_hash_seed(w, seed) ^ 0x1234).standard_normal(d)
        X[i] = basis[lab[i]] + PLANTED_NOISE * (eps / (np.linalg.norm(eps) + 1e-8))
    return _l2n(X)


def enc_shuffled_planted(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    """The permutation control: the SAME code set, reassigned to words. Identity quality is
    untouched; the planted structure must go to chance."""
    X = enc_planted_structure(words, d, seed)
    perm = np.random.default_rng(seed ^ 0xF00D).permutation(len(words))
    return X[perm]


ENCODERS: Dict[str, Callable[[Sequence[str], int, int], np.ndarray]] = {
    "A_ORACLE_ONEHOT": enc_oracle_onehot,
    "A_RANDOM_IID": enc_random_iid,
    "A_COLLAPSE": enc_collapse,
    "A_ORTHOGRAPHIC": enc_orthographic,
    "A_PLANTED_STRUCTURE": enc_planted_structure,
    "A_SHUFFLED_PLANTED": enc_shuffled_planted,
}


# ----------------------------------------------------------------------------------
# SimLex + the planted-semantic known-answer arm
# ----------------------------------------------------------------------------------
def load_simlex(path: Path) -> List[Tuple[str, str, float]]:
    pairs: List[Tuple[str, str, float]] = []
    if not path.exists():
        return pairs
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            try:
                pairs.append((p[0].lower(), p[1].lower(), float(p[3])))
            except ValueError:
                continue
    return pairs


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")

    def rank(x):
        order = np.argsort(x, kind="stable")
        r = np.empty(len(x), dtype=np.float64)
        r[order] = np.arange(len(x), dtype=np.float64)
        # average ties
        xs = x[order]
        i = 0
        while i < len(xs):
            j = i
            while j + 1 < len(xs) and xs[j + 1] == xs[i]:
                j += 1
            if j > i:
                r[order[i:j + 1]] = np.mean(r[order[i:j + 1]])
            i = j + 1
        return r

    ra, rb = rank(np.asarray(a, dtype=np.float64)), rank(np.asarray(b, dtype=np.float64))
    ra -= ra.mean()
    rb -= rb.mean()
    den = math.sqrt(float(ra @ ra) * float(rb @ rb))
    return float(ra @ rb / den) if den > 0 else float("nan")


def simlex_rho(codes: np.ndarray, w2i: Dict[str, int],
               pairs: Sequence[Tuple[str, str, float]]) -> Tuple[float, int]:
    cs, gs = [], []
    for a, b, s in pairs:
        ia, ib = w2i.get(a), w2i.get(b)
        if ia is None or ib is None:
            continue
        cs.append(float(codes[ia] @ codes[ib]))
        gs.append(s)
    if len(cs) < 3:
        return float("nan"), len(cs)
    return _spearman(np.array(cs), np.array(gs)), len(cs)


def enc_planted_semantic(words: Sequence[str], d: int, seed: int,
                         pairs: Sequence[Tuple[str, str, float]],
                         steps: int = 400, lr: float = 0.5) -> np.ndarray:
    """KNOWN-ANSWER arm for the semantic readout: codes fitted BY GRADIENT DESCENT to the
    SimLex gold, so they trivially carry the answer. Words with no SimLex pair keep a random
    code (they are pool only). This arm is CONSTRUCTED FROM THE GOLD by design -- that is
    what a known-answer arm is, and it is why it may never be quoted as a quality result."""
    w2i = {w: i for i, w in enumerate(words)}
    idx_a, idx_b, tgt = [], [], []
    for a, b, s in pairs:
        ia, ib = w2i.get(a), w2i.get(b)
        if ia is None or ib is None:
            continue
        idx_a.append(ia)
        idx_b.append(ib)
        tgt.append(s / 10.0 * 2.0 - 1.0)     # SimLex 0..10 -> cosine target -1..1
    X = enc_random_iid(words, d, seed).astype(np.float64)
    if not idx_a:
        return _l2n(X)
    ia = np.array(idx_a)
    ib = np.array(idx_b)
    t = np.array(tgt)
    for _ in range(steps):
        U, W = X[ia], X[ib]
        c = np.einsum("ij,ij->i", U, W)
        r = (c - t)[:, None]
        gU = 2.0 * r * W
        gW = 2.0 * r * U
        G = np.zeros_like(X)
        np.add.at(G, ia, gU)
        np.add.at(G, ib, gW)
        X -= lr * G
        X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return _l2n(X)


# ----------------------------------------------------------------------------------
# THE FOUR MEASURES
# ----------------------------------------------------------------------------------
def _tiebreak(S: np.ndarray, rng) -> np.ndarray:
    """Break EXACT ties uniformly at random.

    Load-bearing, and found by this cell's own self-test: with a degenerate encoder every
    code is bit-identical, every similarity is exactly equal, and np.argmax then returns
    index 0 deterministically. Because the target sits at candidate position 0 in the
    discriminability pool, the NULL arm scored 1.0000 -- a metric pinned at the ceiling with
    no information anywhere in the path. Magnitude 1e-12 on float64 sims breaks exact ties
    without touching any real difference (float32 cosine resolution is ~1e-7)."""
    S = np.asarray(S, dtype=np.float64)
    return S + rng.random(S.shape) * 1e-12


def _noisy_probe(codes: np.ndarray, idx: np.ndarray, sigma: float, rng) -> np.ndarray:
    """probe = code + n, with ||n||_2 == sigma exactly (norm-matched to unit codes)."""
    P = codes[idx].astype(np.float32).copy()
    n = rng.standard_normal(P.shape).astype(np.float32)
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-8)
    return P + sigma * n


def recoverability(codes: np.ndarray, n_store: int, sigma: float, seed: int,
                   n_probe: int = 512) -> float:
    """M2: argmax cosine of a noise-corrupted probe over the WHOLE store of n_store codes.
    No reader, no selection. Chance = 1/n_store."""
    rng = np.random.default_rng(seed ^ int(sigma * 1000) ^ n_store)
    store = _l2n(codes[:n_store])
    m = min(n_probe, n_store)
    idx = np.sort(rng.choice(n_store, size=m, replace=False))
    P = _l2n(_noisy_probe(store, idx, sigma, rng))
    pred = np.argmax(_tiebreak(P @ store.T, rng), axis=1)
    return float(np.mean(pred == idx))


def discriminability(codes: np.ndarray, pool: np.ndarray, sigma: float, seed: int,
                     n_probe: int = 512) -> float:
    """M1: argmax cosine of a noise-corrupted probe for w against {w} + K distractors.
    Chance = 1/(K+1)."""
    rng = np.random.default_rng(seed ^ int(sigma * 1000) ^ 0x0D15C)
    v = codes.shape[0]
    m = min(n_probe, v)
    idx = np.sort(rng.choice(v, size=m, replace=False))
    C = _l2n(codes)
    P = _l2n(_noisy_probe(C, idx, sigma, rng))
    hits = 0
    for r, i in enumerate(idx):
        cand = np.concatenate(([i], pool[i]))
        sims = _tiebreak(C[cand] @ P[r], rng)
        hits += int(cand[int(np.argmax(sims))] == i)
    return hits / float(m)


def fano_bits(p: float, n: int) -> float:
    """Lower bound on the information (bits) about identity retained at accuracy p over n
    classes: log2(n) - H_b(p) - (1-p) log2(n-1). Clipped at 0. LOWER BOUND, not an estimate."""
    if n <= 1:
        return 0.0
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    hb = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return max(0.0, math.log2(n) - hb - (1 - p) * math.log2(n - 1))


def bundle_survival(codes: np.ndarray, n_store: int, b: int, sign_it: bool,
                    seed: int, n_probe: int = 512) -> float:
    """M4 stages S3/S4: sum codes in groups of b; w counts as recovered iff it is in the
    top-b of cosine against the bundle that contains it."""
    rng = np.random.default_rng(seed ^ (0xB0 if not sign_it else 0xB1) ^ n_store)
    store = _l2n(codes[:n_store])
    n_bundles = n_store // b
    if n_bundles < 1:
        return float("nan")
    usable = n_bundles * b
    B = store[:usable].reshape(n_bundles, b, -1).sum(axis=1)
    if sign_it:
        B = np.sign(B).astype(np.float32)
    B = _l2n(B)
    m = min(n_probe, usable)
    idx = np.sort(rng.choice(usable, size=m, replace=False))
    sims = _tiebreak(B[idx // b] @ store.T, rng)       # [m, n_store]
    part = np.argpartition(-sims, kth=b - 1, axis=1)[:, :b]
    return float(np.mean([idx[r] in part[r] for r in range(m)]))


AP_RAND_REPEATS = 4


def _ap_one(scores: np.ndarray, same: np.ndarray, self_i: int, n_same: int) -> float:
    s = scores.copy()
    s[self_i] = -np.inf                                # never rank self
    order = np.argsort(-s, kind="stable")[:len(s) - 1]
    rel = same[order].astype(np.float64)
    cum = np.cumsum(rel)
    prec = cum / np.arange(1, len(rel) + 1)
    return float((prec * rel).sum() / n_same)


def structure_ap(codes: np.ndarray, labels: np.ndarray, n_probe: int,
                 seed: int) -> Tuple[float, float, float, int]:
    """M5: mean average precision of same-label words when all others are ranked by cosine.
    Returns (ap, chance, lift, n_scored). Label -1 = excluded from scoring, kept in pool.

    `chance` is the EMPIRICAL random-ranking AP on the identical probes and labels, averaged
    over AP_RAND_REPEATS random score draws -- NOT the same-label base rate. Amendment made
    before any run (pre-reg section 8): the base rate systematically UNDERSTATES the AP a
    random ranking achieves on short lists, so base-rate lift for a genuinely null encoder
    came out at 1.51 rather than 1.00 in this cell's own self-test. Normalising by the
    permutation baseline makes a null encoder score 1.00 by construction, which is the
    property the null gates depend on."""
    C = _l2n(codes)
    v = C.shape[0]
    elig = np.where(labels >= 0)[0]
    if len(elig) == 0:
        return float("nan"), float("nan"), float("nan"), 0
    rng = np.random.default_rng(seed ^ 0xA9)
    m = min(n_probe, len(elig))
    probes = np.sort(rng.choice(elig, size=m, replace=False))
    S = _tiebreak(C[probes] @ C.T, rng)                # [m, v]
    rrng = np.random.default_rng(seed ^ 0x5A5A)
    aps, rands = [], []
    for r, i in enumerate(probes):
        same = (labels == labels[i])
        same[i] = False
        n_same = int(same.sum())
        if n_same == 0:
            continue
        aps.append(_ap_one(S[r], same, i, n_same))
        rands.append(float(np.mean([
            _ap_one(rrng.random(v), same, i, n_same) for _ in range(AP_RAND_REPEATS)])))
    if not aps:
        return float("nan"), float("nan"), float("nan"), 0
    ap = float(np.mean(aps))
    ch = float(np.mean(rands))
    return ap, ch, (ap / ch if ch > 0 else float("nan")), len(aps)


# ----------------------------------------------------------------------------------
# one (arm, seed) unit
# ----------------------------------------------------------------------------------
def run_unit(arm: str, seed: int, words: List[str], counts: np.ndarray,
             ortho_pool: np.ndarray, freq_pool: np.ndarray,
             golds: Dict[str, np.ndarray], pairs, w2i) -> Dict:
    t0 = time.time()
    if arm == "A_PLANTED_SEMANTIC":
        codes = enc_planted_semantic(words, D, seed, pairs)
    else:
        codes = ENCODERS[arm](words, D, seed)
    d_eff = int(codes.shape[1])
    codes = _l2n(codes)

    recov: Dict[str, Dict[str, float]] = {}
    for n in N_SWEEP:
        if n > len(words):
            continue
        recov[str(n)] = {f"{s:g}": recoverability(codes, n, s, seed) for s in SIGMAS}

    disc = {
        "disc_ortho": {f"{s:g}": discriminability(codes, ortho_pool, s, seed) for s in SIGMAS},
        "disc_freq": {f"{s:g}": discriminability(codes, freq_pool, s, seed) for s in SIGMAS},
    }

    # M4: the fixed 5-stage chain, all at SIGMA_GATE / N_GATE
    ng = min(N_GATE, len(words))
    onehot = np.eye(len(words), dtype=np.float32)
    signed = _l2n(np.sign(codes).astype(np.float32))
    stages = [
        ("S0_ORACLE", recoverability(onehot, ng, SIGMA_GATE, seed)),
        ("S1_ENCODE", recoverability(codes, ng, SIGMA_GATE, seed)),
        ("S2_ENCODE_SIGN", recoverability(signed, ng, SIGMA_GATE, seed)),
        ("S3_BUNDLE", bundle_survival(codes, ng, BUNDLE_B, False, seed)),
        ("S4_BUNDLE_SIGN", bundle_survival(codes, ng, BUNDLE_B, True, seed)),
    ]
    chain, prev = [], None
    for name, acc in stages:
        bits = fano_bits(acc, ng) if acc == acc else float("nan")
        chain.append({
            "stage": name, "accuracy": acc, "info_bits_lower_bound": bits,
            "destroyed_bits_vs_prev": (None if prev is None else prev - bits),
        })
        prev = bits
    knee = None
    for n in sorted((int(k) for k in recov), reverse=True):
        if recov[str(n)][f"{SIGMA_GATE:g}"] >= 0.50:
            knee = n
            break

    struct = {}
    for gname, lab in golds.items():
        ap, ch, lift, ns = structure_ap(codes, lab, AP_PROBES, seed)
        struct[gname] = {"ap": ap, "chance": ch, "lift": lift, "n_scored": ns}
    rho, n_pairs = simlex_rho(codes, w2i, pairs)

    return {
        "arm": arm, "seed": seed, "d_eff": d_eff,
        "recoverability": recov, "knee_N": knee,
        "discriminability": disc, "stage_chain": chain,
        "structure": struct, "simlex_rho": rho, "simlex_pairs_covered": n_pairs,
        "elapsed_s": time.time() - t0,
    }


# ----------------------------------------------------------------------------------
# gate evaluation
# ----------------------------------------------------------------------------------
def _mean(vals):
    vals = [v for v in vals if v is not None and v == v]
    return float(np.mean(vals)) if vals else float("nan")


def evaluate(per_arm: Dict[str, Dict]) -> Tuple[str, List[Dict], Dict]:
    ng = str(min(N_GATE, V))
    sg = f"{SIGMA_GATE:g}"
    sh = f"{SIGMA_HIGH:g}"

    def recov(arm, n=ng, s=sg):
        return per_arm.get(arm, {}).get("recoverability", {}).get(n, {}).get(s, float("nan"))

    def lift(arm, gold):
        return per_arm.get(arm, {}).get("structure", {}).get(gold, {}).get("lift", float("nan"))

    def disc(arm, kind, s=sg):
        return per_arm.get(arm, {}).get("discriminability", {}).get(kind, {}).get(s, float("nan"))

    def rho(arm):
        return per_arm.get(arm, {}).get("simlex_rho", float("nan"))

    recov_all = [recov(a) for a in ARMS if a in per_arm]
    recov_all = [r for r in recov_all if r == r]
    lifts_all = [lift(a, "GOLD_ORTHO") for a in ARMS if a in per_arm]
    lifts_all = [l for l in lifts_all if l == l]

    snc_ok, snc_ref = True, {}
    try:
        SNC._selftest()
        K = SNC.iid_gaussian_keys(512, 256, 11)
        snc_ref = {"nn_recall_at_1_on_iid_gaussian_keys_noise0.1": float(SNC.nn_recall_at_1(K, 0.1)),
                   "nn_recall_at_1_on_iid_gaussian_keys_noise1.0": float(SNC.nn_recall_at_1(K, 1.0))}
    except Exception as e:                                     # noqa: BLE001 - recorded, not swallowed
        snc_ok = False
        snc_ref = {"error": repr(e)}

    G = [
        ("N1", "NULL", "A_COLLAPSE recoverability <= 0.05", recov("A_COLLAPSE"),
         "<=", T_N1_COLLAPSE_RECOV_MAX),
        ("N2", "NULL", "A_RANDOM_IID GOLD_ORTHO lift <= 1.15",
         lift("A_RANDOM_IID", "GOLD_ORTHO"), "<=", T_N2_N3_LIFT_MAX),
        ("N3", "NULL", "A_RANDOM_IID GOLD_FREQBAND lift <= 1.15",
         lift("A_RANDOM_IID", "GOLD_FREQBAND"), "<=", T_N2_N3_LIFT_MAX),
        ("N4", "NULL", "A_RANDOM_IID |simlex_rho| <= 0.10",
         abs(rho("A_RANDOM_IID")), "<=", T_N4_SIMLEX_ABS_MAX),
        ("N5a", "NULL", "A_SHUFFLED_PLANTED GOLD_PLANTED lift <= 1.15",
         lift("A_SHUFFLED_PLANTED", "GOLD_PLANTED"), "<=", T_N5_LIFT_MAX),
        ("N5b", "NULL", "A_SHUFFLED_PLANTED recoverability >= 0.90",
         recov("A_SHUFFLED_PLANTED"), ">=", T_N5_RECOV_MIN),
        ("N6a", "NULL", "A_COLLAPSE disc_ortho <= 0.10",
         disc("A_COLLAPSE", "disc_ortho"), "<=", T_N6_DISC_MAX),
        ("N6b", "NULL", "A_COLLAPSE disc_freq <= 0.10",
         disc("A_COLLAPSE", "disc_freq"), "<=", T_N6_DISC_MAX),
        ("K1", "KNOWN", "A_ORACLE_ONEHOT recoverability >= 0.95",
         recov("A_ORACLE_ONEHOT"), ">=", T_K1_ORACLE_RECOV_MIN),
        ("K2", "KNOWN", "A_ORTHOGRAPHIC GOLD_ORTHO lift >= 3.0",
         lift("A_ORTHOGRAPHIC", "GOLD_ORTHO"), ">=", T_K2_ORTHO_LIFT_MIN),
        ("K3", "KNOWN", "A_PLANTED_STRUCTURE GOLD_PLANTED lift >= 5.0",
         lift("A_PLANTED_STRUCTURE", "GOLD_PLANTED"), ">=", T_K3_PLANTED_LIFT_MIN),
        ("K5", "KNOWN", "A_RANDOM_IID recoverability >= 0.90",
         recov("A_RANDOM_IID"), ">=", T_K5_RANDOM_RECOV_MIN),
        ("S1", "SAT", "recoverability spread across arms >= 0.50",
         (max(recov_all) - min(recov_all)) if recov_all else float("nan"),
         ">=", T_S1_RECOV_SPREAD_MIN),
        ("S2", "SAT", "A_ORACLE_ONEHOT recoverability at sigma=32 <= 0.80",
         recov("A_ORACLE_ONEHOT", ng, sh), "<=", T_S2_ORACLE_HIGHSIGMA_MAX),
        ("S3", "SAT", "GOLD_ORTHO lift spread across arms >= 2.0",
         (max(lifts_all) - min(lifts_all)) if lifts_all else float("nan"),
         ">=", T_S3_LIFT_SPREAD_MIN),
        ("S4", "SAT", "saturation_negative_control self-test exits 0",
         1.0 if snc_ok else 0.0, ">=", 1.0),
    ]
    claims = []
    for gid, fam, desc, val, op, thr in G:
        ok = (val == val) and ((val <= thr) if op == "<=" else (val >= thr))
        claims.append({"gate_id": gid, "family": fam, "claim": desc,
                       "observed": (None if val != val else float(val)),
                       "op": op, "threshold": thr, "passed": bool(ok)})

    # K4 gates the SEMANTIC READOUT ONLY (pre-reg 5e.4)
    k4_val = rho("A_PLANTED_SEMANTIC")
    k4_ok = (k4_val == k4_val) and k4_val >= T_K4_SIMLEX_RHO_MIN
    claims.append({"gate_id": "K4", "family": "KNOWN_SEMANTIC_READOUT_ONLY",
                   "claim": "A_PLANTED_SEMANTIC simlex_rho >= 0.50",
                   "observed": (None if k4_val != k4_val else float(k4_val)),
                   "op": ">=", "threshold": T_K4_SIMLEX_RHO_MIN, "passed": bool(k4_ok)})

    def failed(fam):
        return [c["gate_id"] for c in claims if c["family"] == fam and not c["passed"]]

    if failed("NULL"):
        verdict = "INSTRUMENT_STILL_LOOSE"
    elif failed("KNOWN"):
        verdict = "INSTRUMENT_CANNOT_DETECT_QUALITY"
    elif failed("SAT"):
        verdict = "INSTRUMENT_SATURATED"
    else:
        verdict = "INSTRUMENT_VALIDATED"

    extra = {
        "semantic_readout_validated": bool(k4_ok),
        "saturation_negative_control": {"self_test_ok": snc_ok, "reference": snc_ref},
        "failed_gates": {f: failed(f) for f in ("NULL", "KNOWN", "SAT")},
    }
    return verdict, claims, extra


# ----------------------------------------------------------------------------------
# formula self-tests
# ----------------------------------------------------------------------------------
def selftest() -> None:
    # 1. fano_bits: perfect accuracy over n classes == log2(n); chance == 0
    assert abs(fano_bits(1.0 - 1e-12, 1024) - 10.0) < 0.01, "fano ceiling"
    assert fano_bits(1.0 / 1024, 1024) < 0.05, "fano at chance"
    # 2. recoverability: orthogonal codes at tiny noise -> 1.0; identical codes -> chance
    I = np.eye(64, dtype=np.float32)
    assert recoverability(I, 64, 0.01, 7) == 1.0, "recov ceiling"
    same = _l2n(np.tile(np.random.default_rng(0).standard_normal(64).astype(np.float32), (64, 1)))
    assert recoverability(same, 64, 1.0, 7) <= 0.10, "recov collapse floor"
    # 3. structure_ap: planted labels -> high lift; shuffled -> ~1.0
    lab = np.arange(128) % 8
    g = np.random.default_rng(1)
    basis = _l2n(g.standard_normal((8, 32)))
    X = _l2n(basis[lab] + 0.2 * g.standard_normal((128, 32)))
    ap, ch, lift, ns = structure_ap(X, lab, 128, 7)
    assert lift > 5.0 and ns == 128, f"structure lift on planted = {lift}"
    perm = g.permutation(128)
    _, _, lift_s, _ = structure_ap(X[perm], lab, 128, 7)
    assert lift_s < 1.5, f"structure lift on shuffled = {lift_s}"
    # 4. spearman: monotone -> 1.0, reversed -> -1.0
    a = np.arange(20.0)
    assert abs(_spearman(a, a) - 1.0) < 1e-9 and abs(_spearman(a, -a) + 1.0) < 1e-9, "spearman"
    # 5. discriminability chance: collapse codes over a K+1 pool -> ~1/(K+1)
    pool = np.stack([np.array([j for j in range(64) if j != i][:K_DISTRACT]) for i in range(64)])
    dv = discriminability(same, pool, 1.0, 7)
    assert dv <= 0.10, f"disc collapse floor = {dv}"
    # 6. noisy probe norm is exactly sigma
    rng = np.random.default_rng(3)
    P = _noisy_probe(I, np.arange(8), 2.0, rng)
    assert abs(float(np.linalg.norm(P[0] - I[0])) - 2.0) < 1e-4, "probe noise norm"
    # 7. bundle_survival: orthogonal codes survive their own bundle
    assert bundle_survival(np.eye(64, dtype=np.float32), 64, 8, False, 7) == 1.0, "bundle"
    # 8. REGRESSION GUARD for the tie-break bug this self-test caught on 2026-08-15:
    #    bit-identical codes must NOT let any readout reach the ceiling via argmax index-0.
    _, _, lift_c, _ = structure_ap(same, np.arange(64) % 8, 64, 7)
    assert lift_c < 1.5, f"collapse structure lift = {lift_c} (tie-break regression)"
    assert bundle_survival(same, 64, 8, False, 7) <= 0.30, "collapse bundle (tie-break regression)"
    # 9. the reused saturation control still self-tests
    SNC._selftest()
    print("[selftest] PASS (9 formula checks + saturation_negative_control)", flush=True)


# ----------------------------------------------------------------------------------
def main() -> int:
    if _ARGS.self_test:
        selftest()
        return 0
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} V={V} D={D} N_SWEEP={N_SWEEP} SIGMAS={SIGMAS} "
          f"SEEDS={SEEDS} out={out_dir}", flush=True)
    selftest()

    words, counts = build_vocab(CORPUS, CORPUS_BYTES, V)
    w2i = {w: i for i, w in enumerate(words)}
    print(f"[vocab] {len(words)} words, e.g. {words[:8]} ... {words[-4:]}", flush=True)
    ortho_pool = build_ortho_neighbours(words, K_DISTRACT)
    freq_pool = build_freq_controls(counts, ortho_pool, K_DISTRACT)
    golds = {"GOLD_ORTHO": gold_ortho(words),
             "GOLD_FREQBAND": gold_freqband(counts),
             "GOLD_PLANTED": gold_planted(len(words))}
    pairs = load_simlex(SIMLEX)
    cov = sum(1 for a, b, _ in pairs if a in w2i and b in w2i)
    print(f"[gold] simlex pairs={len(pairs)} covered={cov} "
          f"ortho_groups_scored={(golds['GOLD_ORTHO'] >= 0).sum()}", flush=True)

    done = completed_units(str(out_dir))
    for arm in ARMS:
        for seed in SEEDS:
            key = unit_key(arm, seed, RUN_MODE, V, D)
            if key in done:
                print(f"[skip] {key}", flush=True)
                continue
            r = run_unit(arm, seed, words, counts, ortho_pool, freq_pool, golds, pairs, w2i)
            record_unit(str(out_dir), key, r)
            print(f"[unit] {arm} seed={seed} recov@{N_GATE},s=1 -> "
                  f"{r['recoverability'].get(str(min(N_GATE, V)), {}).get('1', float('nan')):.4f} "
                  f"ortho_lift={r['structure']['GOLD_ORTHO']['lift']:.3f} "
                  f"planted_lift={r['structure']['GOLD_PLANTED']['lift']:.3f} "
                  f"rho={r['simlex_rho']:.4f} ({r['elapsed_s']:.1f}s)", flush=True)

    units = load_units(str(out_dir))
    rows = [u for u in units.values() if u.get("arm") in ARMS]

    # seed-mean per arm (gates are evaluated on seed means, pre-reg 5a)
    per_arm: Dict[str, Dict] = {}
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        if not rs:
            continue
        agg: Dict = {"n_seeds": len(rs), "d_eff": rs[0]["d_eff"]}
        agg["recoverability"] = {
            n: {s: _mean([r["recoverability"][n][s] for r in rs if n in r["recoverability"]])
                for s in rs[0]["recoverability"][n]}
            for n in rs[0]["recoverability"]}
        agg["discriminability"] = {
            k: {s: _mean([r["discriminability"][k][s] for r in rs])
                for s in rs[0]["discriminability"][k]}
            for k in rs[0]["discriminability"]}
        agg["structure"] = {
            g: {f: _mean([r["structure"][g][f] for r in rs]) for f in ("ap", "chance", "lift")}
            for g in rs[0]["structure"]}
        agg["simlex_rho"] = _mean([r["simlex_rho"] for r in rs])
        agg["simlex_pairs_covered"] = rs[0]["simlex_pairs_covered"]
        agg["knee_N"] = rs[0]["knee_N"]
        agg["stage_chain"] = [
            {"stage": rs[0]["stage_chain"][i]["stage"],
             "accuracy": _mean([r["stage_chain"][i]["accuracy"] for r in rs]),
             "info_bits_lower_bound": _mean([r["stage_chain"][i]["info_bits_lower_bound"] for r in rs]),
             "destroyed_bits_vs_prev": _mean([r["stage_chain"][i]["destroyed_bits_vs_prev"] for r in rs])}
            for i in range(len(rs[0]["stage_chain"]))]
        per_arm[arm] = agg

    verdict, claims, extra = evaluate(per_arm)
    failed = [c["gate_id"] for c in claims if not c["passed"]]
    msg = (f"{verdict}: {len(claims) - len(failed)}/{len(claims)} pre-registered gates passed"
           + (f"; FAILED={failed}" if failed else "")
           + (". NO ENCODING-QUALITY NUMBER IS PUBLISHED (STEP 1 validates the instrument only; "
              "our production encoder is NOT an arm here)."))

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": time.time() - t_start,
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "prereg": "preregs/exp_encoding_quality_instrument_v1.md",
        "config": {"V": V, "D": D, "N_SWEEP": N_SWEEP, "N_GATE": N_GATE, "SIGMAS": SIGMAS,
                   "SEEDS": SEEDS, "K_DISTRACT": K_DISTRACT, "BUNDLE_B": BUNDLE_B,
                   "AP_PROBES": AP_PROBES, "CORPUS_BYTES": CORPUS_BYTES,
                   "N_PLANTED_GROUPS": N_PLANTED_GROUPS},
        "scope_disclaimer": (
            "This cell VALIDATES an instrument against synthetic arms whose quality is known by "
            "construction. It does NOT score our production encoding (STEP 2). A_ORACLE_ONEHOT "
            "runs at d=V and is NOT dimension-matched. Fano numbers are LOWER BOUNDS. The only "
            "semantic gold is SimLex-999 pair similarity, gated separately as K4."),
        "gates": claims,
        "per_arm": per_arm,
        "vocab_sample": words[:20],
        "simlex_pairs_covered": cov,
        **extra,
    }
    write_metrics(out_dir, metrics, results=rows, gate_claims=None)
    print("\n" + msg, flush=True)
    for c in claims:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['gate_id']:4s} {c['claim']:55s} "
              f"observed={c['observed']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
