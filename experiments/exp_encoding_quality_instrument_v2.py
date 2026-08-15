"""exp_encoding_quality_instrument_v2 -- PLAN STEP 2: score the PRODUCTION encoding.

Pre-reg: preregs/exp_encoding_quality_instrument_v2.md (thresholds fixed BEFORE any v2 run).
Parent:  preregs/exp_encoding_quality_instrument_v1.md (FROZEN; every v1 threshold carried
         forward VERBATIM so the v1 gate set is a clean REGRESSION CHECK on the two fixes).

WHAT CHANGED FROM v1, and why (both defects were disclosed by v1 about itself):

  FIX (a) M4 STAGE-CHAIN USED TWO CRITERIA. v1 measured S0/S1/S2 with a top-1 criterion
      (chance 1/1024) and S3/S4 with a top-8 bundle criterion (chance 8/1024), then subtracted
      Fano bits across the S2->S3 boundary as if commensurable. Signature: A_COLLAPSE showed
      destroyed_bits = -0.35, a null arm apparently GAINING information. v2 uses ONE criterion
      for the whole chain -- top-B with B = BUNDLE_B = 8 -- and the LIST-DECODING Fano bound
      fano_bits_list(p, n, B). Ceiling is now log2(n/B) = 7 bits, not 10.
      >>> v1 and v2 stage bits are on DIFFERENT SCALES and must never be quoted side by side.

  FIX (b) THE HEADLINE sigma=1.0 WAS SATURATED. Every non-degenerate arm scores 1.000 there, so
      the metric cannot separate two GOOD encoders. v2's headline is the SIGMA CURVE at
      HEADLINE_SIGMAS = [4, 8, 16] plus a non-saturating scalar sigma_half (the sigma at which
      recoverability crosses 0.50, interpolated in log2 sigma). sigma=1.0 is RETAINED as the gate
      point for every v1 gate, unchanged, precisely so the regression check stays clean.

THE PRODUCTION ENCODER, established by RUNTIME evidence (prereg section 1). 147 hdlab modules on
disk; 12 are encoder-named; importing the two live entry points loads 40 hdlab modules and NONE of
the 12 is among them. The registry agrees (every encoder-named row is
WIRED_BUT_NOT_PIPELINE_REACHABLE) and no registry row names the live one. The production word code
is INLINED in grounding_acquisition_loop.context_vector and exposed as
reading_grounding_loop.symbol_vector:  sha256(w)[:8] -> seed -> default_rng(seed).choice([-1,+1], d).
Live constants observed at runtime: CTX_D = 256, GRADED_COMPARATOR = True.

  P_LIVE_WORD      the primitive per-word code (literally encode(word) -> vector on the live path)
  P_LIVE_CONCEPT   the learned per-lemma profile canonicalize_fast actually reads, i.e.
                   ConceptSpace.bundle(lemma) with GRADED_COMPARATOR=True = the accumulated raw
                   sum of context_vector_masked over every corpus sentence containing the lemma
  C_CONCEPT_SHUFFLED  MANDATORY control: P_LIVE_CONCEPT rows permuted across words. Preserves
                   identity and norms exactly, destroys structure. Without it any lift measured on
                   P_LIVE_CONCEPT is unfalsifiable.

TWO AXES, REPORTED SEPARATELY, NEVER AVERAGED. A random encoding is near-OPTIMAL on IDENTITY and
near-CHANCE on STRUCTURE, so any single scalar mixing them is unfalsifiable. Scoring high on
IDENTITY is NOT a win.

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
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units
from tools import saturation_negative_control as SNC
from hdlab.char_trigram_encoder import CharTrigramEncoder

# THE LIVE PATH, imported so the production arms CALL it rather than reimplement it.
from hdlab.grounding_acquisition_loop import content_words, context_vector
from hdlab.reading_grounding_loop import (
    normalize_lemma, context_vector_masked, symbol_vector, CTX_D, GRADED_COMPARATOR,
)

ANCHOR_NAME = "encoding_quality_instrument_v2"

CORPUS = REPO / "data" / "corpora" / "simplewiki" / "simplewiki_clean_v1.txt"
SIMLEX = REPO / "data" / "encoder_eval_benchmarks" / "simlex999.txt"

# ----------------------------------------------------------------------------------
# PRE-REGISTERED CONFIG (v1 sections 3-5 carried forward verbatim; v2 additions marked)
# ----------------------------------------------------------------------------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

if SMOKE:
    V = 512
    D_GATE = 256
    D_SWEEP = [256]
    CORPUS_BYTES = 8_000_000
    N_SWEEP = [64, 128, 512]
    N_GATE = 512
    SIGMAS = [1.0, 8.0, 32.0]
    AP_PROBES = 128
    SEEDS = [7]
else:
    V = 4096
    D_GATE = 1024
    D_SWEEP = [1024, 256]          # v2: 256 is the PRODUCTION-NATIVE d (CTX_D), 1024 the v1 D
    CORPUS_BYTES = 64_000_000
    N_SWEEP = [128, 512, 1024, 4096]
    N_GATE = 1024
    SIGMAS = [1.0, 4.0, 8.0, 16.0, 32.0]
    AP_PROBES = 1024
    SEEDS = [7, 17, 23]

TOP_DROP = 100
MIN_LEN = 3
K_DISTRACT = 31
BUNDLE_B = 8
N_PLANTED_GROUPS = 32
PLANTED_NOISE = 0.3
SIGMA_GATE = 1.0                  # v1 gate point, UNCHANGED (regression check)
SIGMA_HIGH = 32.0
HEADLINE_SIGMAS = [4.0, 8.0, 16.0]   # v2 fix (b): the headline is the CURVE, not sigma=1
HEADLINE_SIGMA = 8.0

# v1 thresholds -- carried forward VERBATIM. Do not edit.
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
# v2 thresholds (prereg section 3b)
T_M1_MIN_DESTROYED_BITS = -0.25
T_M2_ORACLE_S0_BITS_TOL = 0.01
T_M3_COLLAPSE_S1_BITS_MAX = 0.20
T_SEP1_GOOD_ARM_GAP_MIN = 0.20

SYNTHETIC_ARMS = [
    "A_ORACLE_ONEHOT",
    "A_RANDOM_IID",
    "A_COLLAPSE",
    "A_ORTHOGRAPHIC",
    "A_PLANTED_STRUCTURE",
    "A_SHUFFLED_PLANTED",
    "A_PLANTED_SEMANTIC",
]
PRODUCTION_ARMS = ["P_LIVE_WORD", "P_LIVE_CONCEPT", "C_CONCEPT_SHUFFLED"]
# P_LIVE_CONCEPT / C_CONCEPT_SHUFFLED run at the production-native d only (prereg amendment A3).
CONCEPT_ONLY_D = 256
ARMS = SYNTHETIC_ARMS + PRODUCTION_ARMS


def arms_for_d(d: int) -> List[str]:
    if d == CONCEPT_ONLY_D:
        return ARMS
    return SYNTHETIC_ARMS + ["P_LIVE_WORD"]


# ----------------------------------------------------------------------------------
# vocabulary + golds -- IDENTICAL to v1 (byte-for-byte functions)
# ----------------------------------------------------------------------------------
def build_vocab(corpus_path: Path, n_bytes: int, v: int) -> Tuple[List[str], np.ndarray]:
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
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    sel = ordered[TOP_DROP:TOP_DROP + v]
    if len(sel) < v:
        raise SystemExit(f"[fatal] corpus yielded only {len(sel)} words, need {v}")
    return [w for w, _ in sel], np.array([c for _, c in sel], dtype=np.float64)


def _trigram_set(w: str) -> set:
    t = " " + w + " "
    return {t[i:i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def build_ortho_neighbours(words: Sequence[str], k: int) -> np.ndarray:
    sets = [_trigram_set(w) for w in words]
    n = len(words)
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
            scored.append((-(c / float(li + len(sets[j]) - c)), j))
        scored.sort()
        cand = [j for _, j in scored[:k]]
        if len(cand) < k:
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
    lc = np.log(counts + 1.0)
    order = np.argsort(lc, kind="stable")
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
        while len(picked) < k:
            for j in range(n):
                if j not in banned:
                    picked.append(j)
                    banned.add(j)
                    break
        out[i] = np.array(picked[:k], dtype=np.int64)
    return out


def gold_ortho(words: Sequence[str]) -> np.ndarray:
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
    n = len(counts)
    order = np.argsort(-counts, kind="stable")
    lab = np.empty(n, dtype=np.int64)
    lab[order] = (np.arange(n) * 10) // n
    return lab


def gold_planted(n: int) -> np.ndarray:
    return np.arange(n, dtype=np.int64) % N_PLANTED_GROUPS


# ----------------------------------------------------------------------------------
# synthetic encoders -- IDENTICAL to v1
# ----------------------------------------------------------------------------------
def _l2n(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _hash_seed(s: str, seed: int) -> int:
    return int.from_bytes(hashlib.blake2b(f"{seed}:{s}".encode("utf-8"), digest_size=8).digest(),
                          "big")


def enc_oracle_onehot(words, d, seed):
    return np.eye(len(words), dtype=np.float32)


def enc_random_iid(words, d, seed):
    X = np.zeros((len(words), d), dtype=np.float32)
    for i, w in enumerate(words):
        X[i] = np.random.default_rng(_hash_seed(w, seed)).standard_normal(d)
    return _l2n(X)


def enc_collapse(words, d, seed):
    base = np.random.default_rng(seed).standard_normal(d).astype(np.float32)
    X = np.tile(base, (len(words), 1))
    for i, w in enumerate(words):
        X[i] += 1e-3 * np.random.default_rng(_hash_seed(w, seed) ^ 0xABCD).standard_normal(d)
    return _l2n(X)


def enc_orthographic(words, d, seed):
    enc = CharTrigramEncoder(n_dim=d)
    return _l2n(np.stack([np.asarray(enc.encode(w), dtype=np.float32) for w in words]))


def enc_planted_structure(words, d, seed):
    lab = gold_planted(len(words))
    g = np.random.default_rng(seed ^ 0x5EED)
    basis = _l2n(g.standard_normal((N_PLANTED_GROUPS, d)))
    X = np.zeros((len(words), d), dtype=np.float32)
    for i, w in enumerate(words):
        eps = np.random.default_rng(_hash_seed(w, seed) ^ 0x1234).standard_normal(d)
        X[i] = basis[lab[i]] + PLANTED_NOISE * (eps / (np.linalg.norm(eps) + 1e-8))
    return _l2n(X)


def enc_shuffled_planted(words, d, seed):
    X = enc_planted_structure(words, d, seed)
    return X[np.random.default_rng(seed ^ 0xF00D).permutation(len(words))]


# ----------------------------------------------------------------------------------
# v2: THE PRODUCTION ARMS. These CALL the live path, they do not reimplement it.
# ----------------------------------------------------------------------------------
def enc_live_word(words: Sequence[str], d: int, seed: int) -> np.ndarray:
    """P_LIVE_WORD: the production per-word code, obtained by CALLING the live function.

    grounding_acquisition_loop.context_vector(w, d) on a single content word IS the inlined
    sha256 -> bipolar symbol draw (asserted equal to reading_grounding_loop.symbol_vector in
    self-test #10). SEED-INDEPENDENT by construction: the live code is a pure hash of the
    string, with no seed and no training. That is itself a finding, not an oversight."""
    X = np.zeros((len(words), d), dtype=np.float32)
    n_empty = 0
    for i, w in enumerate(words):
        v = context_vector(w, d=d)          # THE LIVE FUNCTION
        if not np.any(v):                   # word filtered out by the live stopword/len rule
            v = symbol_vector(w, d=d)       # still the live codebook; recorded below
            n_empty += 1
        X[i] = v
    enc_live_word.last_n_empty = n_empty
    return _l2n(X)


enc_live_word.last_n_empty = 0


class ConceptProfileBuilder:
    """P_LIVE_CONCEPT: the live per-lemma concept profile = ConceptSpace.bundle(lemma) with
    GRADED_COMPARATOR=True, i.e. the raw accumulated sum of context_vector_masked(sentence,
    lemma) over every corpus sentence whose content_lemmas contain that lemma.

    Built vectorised for tractability (748k sentences x 6.2M content tokens), then ASSERTED
    BYTE-IDENTICAL to the live context_vector_masked on a sample of real (sentence, lemma)
    pairs before it is used. If the assertion fails the run aborts -- a reimplementation that
    silently diverges from the live path would make every production number meaningless."""

    def __init__(self, corpus_path: Path, n_bytes: int, d: int) -> None:
        self.corpus_path = corpus_path
        self.n_bytes = n_bytes
        self.d = d
        self.stats: Dict = {}

    def _read_lines(self) -> List[str]:
        with open(self.corpus_path, "rb") as f:
            raw = f.read(self.n_bytes)
        cut = raw.rfind(b"\n")
        if cut > 0:
            raw = raw[:cut]
        return raw.decode("utf-8", errors="ignore").split("\n")

    def build(self, words: Sequence[str], out_dir: Path) -> Tuple[np.ndarray, Dict]:
        cache = out_dir / f"concept_profiles_d{self.d}_V{len(words)}_B{self.n_bytes}.npz"
        if cache.exists():
            z = np.load(cache, allow_pickle=True)
            self.stats = json.loads(str(z["stats"]))
            print(f"[concept] resumed from {cache.name}", flush=True)
            return z["profiles"], self.stats

        t0 = time.time()
        lines = self._read_lines()
        # ---- pass 1: tokenise, id-map every content word, cache its lemma
        word_id: Dict[str, int] = {}
        lemma_of_id: List[int] = []
        lemma_id: Dict[str, int] = {}
        tok_ids: List[int] = []
        offs: List[int] = [0]
        for ln in lines:
            for u in content_words(ln):
                j = word_id.get(u)
                if j is None:
                    j = len(word_id)
                    word_id[u] = j
                    lm = normalize_lemma(u)
                    li = lemma_id.get(lm)
                    if li is None:
                        li = len(lemma_id)
                        lemma_id[lm] = li
                    lemma_of_id.append(li)
                tok_ids.append(j)
            offs.append(len(tok_ids))
        tok = np.array(tok_ids, dtype=np.int32)
        off = np.array(offs, dtype=np.int64)
        lem_of = np.array(lemma_of_id, dtype=np.int32)
        U = len(word_id)
        print(f"[concept] d={self.d} lines={len(lines)} tokens={len(tok)} "
              f"unique_content_words={U} unique_lemmas={len(lemma_id)} "
              f"({time.time() - t0:.0f}s)", flush=True)

        # ---- the LIVE symbol codebook, one draw per unique content word
        S = np.zeros((U, self.d), dtype=np.float32)
        for u, j in word_id.items():
            sd = int.from_bytes(hashlib.sha256(u.encode("utf-8")).digest()[:8], "big") % (2 ** 32)
            S[j] = np.random.default_rng(sd).choice([-1.0, 1.0], size=self.d)

        # ---- target rows: one per vocabulary word, keyed by its LEMMA (as the live path does)
        tgt_lemma = [normalize_lemma(w) for w in words]
        lem_to_row: Dict[int, List[int]] = {}
        n_lemma_unmapped = 0
        for r, lm in enumerate(tgt_lemma):
            li = lemma_id.get(lm)
            if li is None:
                n_lemma_unmapped += 1
                continue
            lem_to_row.setdefault(li, []).append(r)
        profiles = np.zeros((len(words), self.d), dtype=np.float64)
        n_hits = np.zeros(len(words), dtype=np.int64)

        # ---- pass 2: accumulate.  profile[t] += ctx_sum(sentence) - sum(S[u] : lemma(u) == t)
        for i in range(len(lines)):
            a, b = off[i], off[i + 1]
            if b <= a:
                continue
            ids = tok[a:b]
            lems = lem_of[ids]
            present = np.unique(lems)
            rows_here = [(li, lem_to_row[int(li)]) for li in present if int(li) in lem_to_row]
            if not rows_here:
                continue
            ctx = S[ids].sum(axis=0, dtype=np.float64)
            for li, rows in rows_here:
                own = S[ids[lems == li]].sum(axis=0, dtype=np.float64)
                masked = ctx - own
                for r in rows:
                    profiles[r] += masked
                    n_hits[r] += 1
            if (i % 100000) == 0 and i:
                print(f"[concept]   line {i}/{len(lines)} ({time.time() - t0:.0f}s)", flush=True)

        # ---- BYTE-EQUALITY ASSERTION against the live function
        rng = np.random.default_rng(20260815)
        n_checked, n_eq = 0, 0
        tries = 0
        while n_checked < 200 and tries < 20000:
            tries += 1
            i = int(rng.integers(0, len(lines)))
            a, b = off[i], off[i + 1]
            if b <= a:
                continue
            ids = tok[a:b]
            lems = lem_of[ids]
            li = int(lems[int(rng.integers(0, len(lems)))])
            lm = None
            for k, vv in lemma_id.items():
                if vv == li:
                    lm = k
                    break
            if lm is None:
                continue
            mine = S[ids].sum(axis=0, dtype=np.float64) - S[ids[lems == li]].sum(axis=0,
                                                                                dtype=np.float64)
            live = context_vector_masked(lines[i], lm, d=self.d)   # THE LIVE FUNCTION
            n_checked += 1
            n_eq += int(np.array_equal(mine, np.asarray(live, dtype=np.float64)))
        if n_checked == 0 or n_eq != n_checked:
            raise SystemExit(f"[fatal] concept profile construction is NOT byte-identical to "
                             f"reading_grounding_loop.context_vector_masked "
                             f"({n_eq}/{n_checked} matched). Aborting: a production number from a "
                             f"diverging reimplementation would be meaningless.")

        # ---- lemma collisions: two vocab words sharing a lemma get the SAME production code
        from collections import Counter
        lc = Counter(tgt_lemma)
        collide = np.array([lc[t] > 1 for t in tgt_lemma], dtype=bool)
        self.stats = {
            "d": self.d,
            "corpus_lines": len(lines),
            "content_tokens": int(len(tok)),
            "unique_content_words": U,
            "unique_lemmas": len(lemma_id),
            "byte_equality_vs_live_context_vector_masked": f"{n_eq}/{n_checked}",
            "graded_comparator_live_default": bool(GRADED_COMPARATOR),
            "n_vocab_words": len(words),
            "n_lemma_unmapped": int(n_lemma_unmapped),
            "n_zero_profile": int((n_hits == 0).sum()),
            "n_lemma_collisions": int(collide.sum()),
            "n_distinct_lemmas_in_vocab": int(len(set(tgt_lemma))),
            "collision_free_mask_sum": int((~collide).sum()),
            "build_s": round(time.time() - t0, 1),
        }
        np.savez_compressed(cache, profiles=profiles.astype(np.float32),
                            collide=collide, stats=json.dumps(self.stats))
        print(f"[concept] built d={self.d} in {self.stats['build_s']}s; "
              f"byte-equal {n_eq}/{n_checked}; collisions={self.stats['n_lemma_collisions']}; "
              f"zero-profile={self.stats['n_zero_profile']}", flush=True)
        return profiles.astype(np.float32), self.stats


_CONCEPT_CACHE: Dict[int, Tuple[np.ndarray, np.ndarray, Dict]] = {}


def get_concept(words, d, out_dir):
    if d not in _CONCEPT_CACHE:
        b = ConceptProfileBuilder(CORPUS, CORPUS_BYTES, d)
        prof, st = b.build(words, out_dir)
        cache = out_dir / f"concept_profiles_d{d}_V{len(words)}_B{CORPUS_BYTES}.npz"
        collide = np.load(cache, allow_pickle=True)["collide"]
        _CONCEPT_CACHE[d] = (prof, collide, st)
    return _CONCEPT_CACHE[d]


# ----------------------------------------------------------------------------------
# SimLex + planted-semantic known-answer arm -- IDENTICAL to v1
# ----------------------------------------------------------------------------------
def load_simlex(path: Path):
    pairs = []
    if not path.exists():
        return pairs
    with open(path, "r", encoding="utf-8") as f:
        f.readline()
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


def simlex_rho(codes, w2i, pairs):
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


def enc_planted_semantic(words, d, seed, pairs, steps=400, lr=0.5):
    w2i = {w: i for i, w in enumerate(words)}
    idx_a, idx_b, tgt = [], [], []
    for a, b, s in pairs:
        ia, ib = w2i.get(a), w2i.get(b)
        if ia is None or ib is None:
            continue
        idx_a.append(ia)
        idx_b.append(ib)
        tgt.append(s / 10.0 * 2.0 - 1.0)
    X = enc_random_iid(words, d, seed).astype(np.float64)
    if not idx_a:
        return _l2n(X)
    ia, ib, t = np.array(idx_a), np.array(idx_b), np.array(tgt)
    for _ in range(steps):
        U, W = X[ia], X[ib]
        r = (np.einsum("ij,ij->i", U, W) - t)[:, None]
        G = np.zeros_like(X)
        np.add.at(G, ia, 2.0 * r * W)
        np.add.at(G, ib, 2.0 * r * U)
        X -= lr * G
        X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    return _l2n(X)


# ----------------------------------------------------------------------------------
# THE MEASURES
# ----------------------------------------------------------------------------------
def _tiebreak(S, rng):
    S = np.asarray(S, dtype=np.float64)
    return S + rng.random(S.shape) * 1e-12


def _noisy_probe(codes, idx, sigma, rng):
    P = codes[idx].astype(np.float32).copy()
    n = rng.standard_normal(P.shape).astype(np.float32)
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-8)
    return P + sigma * n


def recoverability(codes, n_store, sigma, seed, n_probe=512, mask=None):
    """M2 (top-1). `mask` optionally restricts which items may be PROBED (the store is
    unchanged), used for the collision-free diagnostic."""
    rng = np.random.default_rng(seed ^ int(sigma * 1000) ^ n_store)
    store = _l2n(codes[:n_store])
    elig = np.arange(n_store) if mask is None else np.where(mask[:n_store])[0]
    if len(elig) == 0:
        return float("nan")
    m = min(n_probe, len(elig))
    idx = np.sort(rng.choice(elig, size=m, replace=False))
    P = _l2n(_noisy_probe(store, idx, sigma, rng))
    return float(np.mean(np.argmax(_tiebreak(P @ store.T, rng), axis=1) == idx))


def recoverability_topb(codes, n_store, sigma, seed, b, n_probe=512):
    """v2 FIX (a): the SAME top-B list criterion the bundle stages use, so the whole M4 chain
    shares ONE criterion and ONE chance level (B/n)."""
    rng = np.random.default_rng(seed ^ int(sigma * 1000) ^ n_store ^ 0x70B)
    store = _l2n(codes[:n_store])
    m = min(n_probe, n_store)
    idx = np.sort(rng.choice(n_store, size=m, replace=False))
    P = _l2n(_noisy_probe(store, idx, sigma, rng))
    sims = _tiebreak(P @ store.T, rng)
    part = np.argpartition(-sims, kth=min(b, n_store) - 1, axis=1)[:, :b]
    return float(np.mean([idx[r] in part[r] for r in range(m)]))


def discriminability(codes, pool, sigma, seed, n_probe=512):
    rng = np.random.default_rng(seed ^ int(sigma * 1000) ^ 0x0D15C)
    v = codes.shape[0]
    m = min(n_probe, v)
    idx = np.sort(rng.choice(v, size=m, replace=False))
    C = _l2n(codes)
    P = _l2n(_noisy_probe(C, idx, sigma, rng))
    hits = 0
    for r, i in enumerate(idx):
        cand = np.concatenate(([i], pool[i]))
        hits += int(cand[int(np.argmax(_tiebreak(C[cand] @ P[r], rng)))] == i)
    return hits / float(m)


def fano_bits(p, n):
    """v1's top-1 Fano lower bound. Retained ONLY as the B=1 reduction case of the list bound."""
    if n <= 1:
        return 0.0
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    hb = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return max(0.0, math.log2(n) - hb - (1 - p) * math.log2(n - 1))


def fano_bits_list(p, n, b):
    """v2 FIX (a): LIST-DECODING Fano lower bound for a decoder that outputs B candidates.

        I >= log2(n) - H_b(p) - (1-p)*log2(n-B) - p*log2(B)

    B=1 reduces EXACTLY to fano_bits. p=1 gives log2(n/B) (7 bits at n=1024, B=8), NOT log2(n).
    p=B/n (chance) gives ~0. Asserted in self-tests #11-#14 before any run."""
    if n <= 1 or b < 1 or b >= n:
        return 0.0
    p = min(max(p, 1e-12), 1.0 - 1e-12)
    hb = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    return max(0.0, math.log2(n) - hb - (1 - p) * math.log2(n - b) - p * math.log2(b))


def bundle_survival(codes, n_store, b, sign_it, seed, n_probe=512):
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
    sims = _tiebreak(B[idx // b] @ store.T, rng)
    part = np.argpartition(-sims, kth=b - 1, axis=1)[:, :b]
    return float(np.mean([idx[r] in part[r] for r in range(m)]))


AP_RAND_REPEATS = 4


def _ap_one(scores, same, self_i, n_same):
    s = scores.copy()
    s[self_i] = -np.inf
    order = np.argsort(-s, kind="stable")[:len(s) - 1]
    rel = same[order].astype(np.float64)
    prec = np.cumsum(rel) / np.arange(1, len(rel) + 1)
    return float((prec * rel).sum() / n_same)


def structure_ap(codes, labels, n_probe, seed):
    C = _l2n(codes)
    v = C.shape[0]
    elig = np.where(labels >= 0)[0]
    if len(elig) == 0:
        return float("nan"), float("nan"), float("nan"), 0
    rng = np.random.default_rng(seed ^ 0xA9)
    m = min(n_probe, len(elig))
    probes = np.sort(rng.choice(elig, size=m, replace=False))
    S = _tiebreak(C[probes] @ C.T, rng)
    rrng = np.random.default_rng(seed ^ 0x5A5A)
    aps, rands = [], []
    for r, i in enumerate(probes):
        same = (labels == labels[i])
        same[i] = False
        n_same = int(same.sum())
        if n_same == 0:
            continue
        aps.append(_ap_one(S[r], same, i, n_same))
        rands.append(float(np.mean([_ap_one(rrng.random(v), same, i, n_same)
                                    for _ in range(AP_RAND_REPEATS)])))
    if not aps:
        return float("nan"), float("nan"), float("nan"), 0
    ap = float(np.mean(aps))
    ch = float(np.mean(rands))
    return ap, ch, (ap / ch if ch > 0 else float("nan")), len(aps)


def sigma_half(recov_at_n: Dict[str, float], sigmas: Sequence[float]) -> Optional[float]:
    """v2 FIX (b): the non-saturating headline scalar. The sigma at which recoverability crosses
    0.50, interpolated in log2(sigma). None if it never crosses within the grid."""
    xs = sorted(sigmas)
    ys = [recov_at_n.get(f"{s:g}", float("nan")) for s in xs]
    if any(y != y for y in ys):
        return None
    if ys[0] < 0.5:
        return float(xs[0])                       # already below at the smallest sigma
    for i in range(len(xs) - 1):
        if ys[i] >= 0.5 > ys[i + 1]:
            l0, l1 = math.log2(xs[i]), math.log2(xs[i + 1])
            f = (ys[i] - 0.5) / (ys[i] - ys[i + 1])
            return float(2 ** (l0 + f * (l1 - l0)))
    return None                                    # never falls below 0.50 on the grid


# ----------------------------------------------------------------------------------
# one (arm, d, seed) unit
# ----------------------------------------------------------------------------------
def build_codes(arm, d, seed, words, pairs, out_dir):
    if arm == "A_ORACLE_ONEHOT":
        return enc_oracle_onehot(words, d, seed), None
    if arm == "A_RANDOM_IID":
        return enc_random_iid(words, d, seed), None
    if arm == "A_COLLAPSE":
        return enc_collapse(words, d, seed), None
    if arm == "A_ORTHOGRAPHIC":
        return enc_orthographic(words, d, seed), None
    if arm == "A_PLANTED_STRUCTURE":
        return enc_planted_structure(words, d, seed), None
    if arm == "A_SHUFFLED_PLANTED":
        return enc_shuffled_planted(words, d, seed), None
    if arm == "A_PLANTED_SEMANTIC":
        return enc_planted_semantic(words, d, seed, pairs), None
    if arm == "P_LIVE_WORD":
        return enc_live_word(words, d, seed), None
    if arm in ("P_LIVE_CONCEPT", "C_CONCEPT_SHUFFLED"):
        prof, collide, _ = get_concept(words, d, out_dir)
        X = _l2n(prof)
        if arm == "C_CONCEPT_SHUFFLED":
            X = X[np.random.default_rng(seed ^ 0xC0FFEE).permutation(len(words))]
            return X, None
        return X, ~collide                          # collision-free mask, diagnostic only
    raise SystemExit(f"[fatal] unknown arm {arm}")


def run_unit(arm, d, seed, words, ortho_pool, freq_pool, golds, pairs, w2i, out_dir):
    t0 = time.time()
    codes, cf_mask = build_codes(arm, d, seed, words, pairs, out_dir)
    d_eff = int(codes.shape[1])
    codes = _l2n(codes)

    recov = {}
    for n in N_SWEEP:
        if n > len(words):
            continue
        recov[str(n)] = {f"{s:g}": recoverability(codes, n, s, seed) for s in SIGMAS}

    disc = {
        "disc_ortho": {f"{s:g}": discriminability(codes, ortho_pool, s, seed) for s in SIGMAS},
        "disc_freq": {f"{s:g}": discriminability(codes, freq_pool, s, seed) for s in SIGMAS},
    }

    ng = min(N_GATE, len(words))
    recov_cf = None
    if cf_mask is not None:
        recov_cf = {f"{s:g}": recoverability(codes, ng, s, seed, mask=cf_mask) for s in SIGMAS}

    # ---- M4, v2 FIX (a): ONE criterion (top-B) for all five stages
    onehot = np.eye(len(words), dtype=np.float32)
    signed = _l2n(np.sign(codes).astype(np.float32))
    stages = [
        ("S0_ORACLE", recoverability_topb(onehot, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S1_ENCODE", recoverability_topb(codes, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S2_ENCODE_SIGN", recoverability_topb(signed, ng, SIGMA_GATE, seed, BUNDLE_B)),
        ("S3_BUNDLE", bundle_survival(codes, ng, BUNDLE_B, False, seed)),
        ("S4_BUNDLE_SIGN", bundle_survival(codes, ng, BUNDLE_B, True, seed)),
    ]
    chain, prev = [], None
    for name, acc in stages:
        bits = fano_bits_list(acc, ng, BUNDLE_B) if acc == acc else float("nan")
        chain.append({"stage": name, "accuracy": acc, "info_bits_lower_bound": bits,
                      "criterion": f"top-{BUNDLE_B} of {ng}",
                      "destroyed_bits_vs_prev": (None if prev is None else prev - bits)})
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
        "arm": arm, "d": d, "seed": seed, "d_eff": d_eff,
        "recoverability": recov, "recoverability_collisionfree": recov_cf,
        "sigma_half_at_N_GATE": sigma_half(recov.get(str(ng), {}), SIGMAS),
        "knee_N": knee, "discriminability": disc, "stage_chain": chain,
        "structure": struct, "simlex_rho": rho, "simlex_pairs_covered": n_pairs,
        "elapsed_s": time.time() - t0,
    }


# ----------------------------------------------------------------------------------
# gates
# ----------------------------------------------------------------------------------
def _mean(vals):
    vals = [v for v in vals if v is not None and v == v]
    return float(np.mean(vals)) if vals else float("nan")


def evaluate(by_d: Dict[int, Dict[str, Dict]]) -> Tuple[str, List[Dict], Dict]:
    """v1 gates evaluated at D_GATE, sigma=SIGMA_GATE, N_GATE -- IDENTICAL to v1.
    v2 gates (CHAIN, SEP) added."""
    per_arm = by_d.get(D_GATE, {})
    ng = str(min(N_GATE, V))
    sg = f"{SIGMA_GATE:g}"
    sh = f"{SIGMA_HIGH:g}"
    shl = f"{HEADLINE_SIGMA:g}"

    def recov(arm, n=ng, s=sg, pa=None):
        return (pa or per_arm).get(arm, {}).get("recoverability", {}).get(n, {}).get(s, float("nan"))

    def lift(arm, gold):
        return per_arm.get(arm, {}).get("structure", {}).get(gold, {}).get("lift", float("nan"))

    def disc(arm, kind, s=sg):
        return per_arm.get(arm, {}).get("discriminability", {}).get(kind, {}).get(s, float("nan"))

    def rho(arm):
        return per_arm.get(arm, {}).get("simlex_rho", float("nan"))

    # v1's spread gates ranged over the v1 ARM LIST ONLY -- keep it that way so S1/S3 are the
    # same statistic v1 computed and the regression check is exact.
    recov_all = [r for r in (recov(a) for a in SYNTHETIC_ARMS if a in per_arm) if r == r]
    lifts_all = [l for l in (lift(a, "GOLD_ORTHO") for a in SYNTHETIC_ARMS if a in per_arm)
                 if l == l]

    snc_ok, snc_ref = True, {}
    try:
        SNC._selftest()
        K = SNC.iid_gaussian_keys(512, 256, 11)
        snc_ref = {"nn_recall_at_1_on_iid_gaussian_keys_noise0.1": float(SNC.nn_recall_at_1(K, 0.1)),
                   "nn_recall_at_1_on_iid_gaussian_keys_noise1.0": float(SNC.nn_recall_at_1(K, 1.0))}
    except Exception as e:                                     # noqa: BLE001 - recorded, not swallowed
        snc_ok = False
        snc_ref = {"error": repr(e)}

    # ---- v2 CHAIN statistics, over EVERY arm at EVERY d
    worst_destroyed, worst_where = float("inf"), None
    for dd, pa in by_d.items():
        for a, agg in pa.items():
            for st in agg.get("stage_chain", []):
                v = st.get("destroyed_bits_vs_prev")
                if v is not None and v == v and v < worst_destroyed:
                    worst_destroyed, worst_where = v, f"{a}@d{dd}:{st['stage']}"
    if worst_where is None:
        worst_destroyed = float("nan")

    def stage_bits(arm, stage):
        for st in per_arm.get(arm, {}).get("stage_chain", []):
            if st["stage"] == stage:
                return st.get("info_bits_lower_bound", float("nan"))
        return float("nan")

    chain_ceiling = math.log2(min(N_GATE, V) / float(BUNDLE_B))
    oracle_s0 = stage_bits("A_ORACLE_ONEHOT", "S0_ORACLE")

    # ---- v2 SEP: can the instrument separate TWO GOOD encoders?
    sep_hi = recov("A_ORACLE_ONEHOT", ng, shl) - recov("A_PLANTED_STRUCTURE", ng, shl)
    sep_lo = recov("A_ORACLE_ONEHOT", ng, sg) - recov("A_PLANTED_STRUCTURE", ng, sg)

    G = [
        ("N1", "NULL", "A_COLLAPSE recoverability <= 0.05", recov("A_COLLAPSE"), "<=",
         T_N1_COLLAPSE_RECOV_MAX),
        ("N2", "NULL", "A_RANDOM_IID GOLD_ORTHO lift <= 1.15", lift("A_RANDOM_IID", "GOLD_ORTHO"),
         "<=", T_N2_N3_LIFT_MAX),
        ("N3", "NULL", "A_RANDOM_IID GOLD_FREQBAND lift <= 1.15",
         lift("A_RANDOM_IID", "GOLD_FREQBAND"), "<=", T_N2_N3_LIFT_MAX),
        ("N4", "NULL", "A_RANDOM_IID |simlex_rho| <= 0.10", abs(rho("A_RANDOM_IID")), "<=",
         T_N4_SIMLEX_ABS_MAX),
        ("N5a", "NULL", "A_SHUFFLED_PLANTED GOLD_PLANTED lift <= 1.15",
         lift("A_SHUFFLED_PLANTED", "GOLD_PLANTED"), "<=", T_N5_LIFT_MAX),
        ("N5b", "NULL", "A_SHUFFLED_PLANTED recoverability >= 0.90", recov("A_SHUFFLED_PLANTED"),
         ">=", T_N5_RECOV_MIN),
        ("N6a", "NULL", "A_COLLAPSE disc_ortho <= 0.10", disc("A_COLLAPSE", "disc_ortho"), "<=",
         T_N6_DISC_MAX),
        ("N6b", "NULL", "A_COLLAPSE disc_freq <= 0.10", disc("A_COLLAPSE", "disc_freq"), "<=",
         T_N6_DISC_MAX),
        ("K1", "KNOWN", "A_ORACLE_ONEHOT recoverability >= 0.95", recov("A_ORACLE_ONEHOT"), ">=",
         T_K1_ORACLE_RECOV_MIN),
        ("K2", "KNOWN", "A_ORTHOGRAPHIC GOLD_ORTHO lift >= 3.0", lift("A_ORTHOGRAPHIC",
                                                                      "GOLD_ORTHO"),
         ">=", T_K2_ORTHO_LIFT_MIN),
        ("K3", "KNOWN", "A_PLANTED_STRUCTURE GOLD_PLANTED lift >= 5.0",
         lift("A_PLANTED_STRUCTURE", "GOLD_PLANTED"), ">=", T_K3_PLANTED_LIFT_MIN),
        ("K5", "KNOWN", "A_RANDOM_IID recoverability >= 0.90", recov("A_RANDOM_IID"), ">=",
         T_K5_RANDOM_RECOV_MIN),
        ("S1", "SAT", "recoverability spread across arms >= 0.50",
         (max(recov_all) - min(recov_all)) if recov_all else float("nan"), ">=",
         T_S1_RECOV_SPREAD_MIN),
        ("S2", "SAT", "A_ORACLE_ONEHOT recoverability at sigma=32 <= 0.80",
         recov("A_ORACLE_ONEHOT", ng, sh), "<=", T_S2_ORACLE_HIGHSIGMA_MAX),
        ("S3", "SAT", "GOLD_ORTHO lift spread across arms >= 2.0",
         (max(lifts_all) - min(lifts_all)) if lifts_all else float("nan"), ">=",
         T_S3_LIFT_SPREAD_MIN),
        ("S4", "SAT", "saturation_negative_control self-test exits 0", 1.0 if snc_ok else 0.0,
         ">=", 1.0),
        # ---- v2 additions
        ("M1", "CHAIN", "min destroyed_bits_vs_prev over ALL arms/d/stages >= -0.25",
         worst_destroyed, ">=", T_M1_MIN_DESTROYED_BITS),
        ("M2", "CHAIN", f"A_ORACLE_ONEHOT S0 bits == log2(N_GATE/B) = {chain_ceiling:.3f}",
         -abs(oracle_s0 - chain_ceiling), ">=", -T_M2_ORACLE_S0_BITS_TOL),
        ("M3", "CHAIN", "A_COLLAPSE S1 bits <= 0.20", stage_bits("A_COLLAPSE", "S1_ENCODE"), "<=",
         T_M3_COLLAPSE_S1_BITS_MAX),
        ("SEP1", "SEP", "ORACLE minus PLANTED_STRUCTURE recoverability at sigma=8 >= 0.20",
         sep_hi, ">=", T_SEP1_GOOD_ARM_GAP_MIN),
    ]
    claims = []
    for gid, fam, desc, val, op, thr in G:
        ok = (val == val) and ((val <= thr) if op == "<=" else (val >= thr))
        claims.append({"gate_id": gid, "family": fam, "claim": desc,
                       "observed": (None if val != val else float(val)),
                       "op": op, "threshold": thr, "passed": bool(ok)})

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
    elif failed("CHAIN"):
        verdict = "INSTRUMENT_CHAIN_DEFECT"
    elif failed("SEP"):
        verdict = "INSTRUMENT_CANNOT_SEPARATE_TWO_GOOD_ENCODERS"
    else:
        verdict = "INSTRUMENT_VALIDATED"

    extra = {
        "semantic_readout_validated": bool(k4_ok),
        "saturation_negative_control": {"self_test_ok": snc_ok, "reference": snc_ref},
        "failed_gates": {f: failed(f) for f in ("NULL", "KNOWN", "SAT", "CHAIN", "SEP")},
        "v2_fix_a_chain": {
            "criterion": f"top-{BUNDLE_B} at every stage (v1 mixed top-1 and top-8)",
            "bound": "fano_bits_list(p, n, B) -- list-decoding Fano",
            "ceiling_bits": chain_ceiling,
            "v1_ceiling_bits_for_reference_NOT_COMPARABLE": math.log2(min(N_GATE, V)),
            "worst_destroyed_bits_vs_prev": (None if worst_destroyed != worst_destroyed
                                             else worst_destroyed),
            "worst_destroyed_where": worst_where,
        },
        "v2_fix_b_saturation": {
            "headline_sigmas": HEADLINE_SIGMAS,
            "headline_sigma": HEADLINE_SIGMA,
            "SEP1_gap_at_sigma8": (None if sep_hi != sep_hi else float(sep_hi)),
            "SEP2_DIAG_gap_at_sigma1": (None if sep_lo != sep_lo else float(sep_lo)),
            "SEP2_DIAG_note": ("DIAGNOSTIC, not a verdict gate. A gap of ~0 at sigma=1 is the "
                               "EVIDENCE that v1's headline point was saturated -- both arms sit "
                               "at 1.000 there, so the metric cannot separate two GOOD encoders."),
        },
    }
    return verdict, claims, extra


# ----------------------------------------------------------------------------------
# formula self-tests
# ----------------------------------------------------------------------------------
def selftest() -> None:
    # 1-9: v1's checks, carried forward VERBATIM (regression on the shared machinery)
    assert abs(fano_bits(1.0 - 1e-12, 1024) - 10.0) < 0.01, "fano ceiling"
    assert fano_bits(1.0 / 1024, 1024) < 0.05, "fano at chance"
    I = np.eye(64, dtype=np.float32)
    assert recoverability(I, 64, 0.01, 7) == 1.0, "recov ceiling"
    same = _l2n(np.tile(np.random.default_rng(0).standard_normal(64).astype(np.float32), (64, 1)))
    assert recoverability(same, 64, 1.0, 7) <= 0.10, "recov collapse floor"
    lab = np.arange(128) % 8
    g = np.random.default_rng(1)
    basis = _l2n(g.standard_normal((8, 32)))
    X = _l2n(basis[lab] + 0.2 * g.standard_normal((128, 32)))
    ap, ch, lift, ns = structure_ap(X, lab, 128, 7)
    assert lift > 5.0 and ns == 128, f"structure lift on planted = {lift}"
    perm = g.permutation(128)
    _, _, lift_s, _ = structure_ap(X[perm], lab, 128, 7)
    assert lift_s < 1.5, f"structure lift on shuffled = {lift_s}"
    a = np.arange(20.0)
    assert abs(_spearman(a, a) - 1.0) < 1e-9 and abs(_spearman(a, -a) + 1.0) < 1e-9, "spearman"
    pool = np.stack([np.array([j for j in range(64) if j != i][:K_DISTRACT]) for i in range(64)])
    assert discriminability(same, pool, 1.0, 7) <= 0.10, "disc collapse floor"
    rng = np.random.default_rng(3)
    P = _noisy_probe(I, np.arange(8), 2.0, rng)
    assert abs(float(np.linalg.norm(P[0] - I[0])) - 2.0) < 1e-4, "probe noise norm"
    assert bundle_survival(np.eye(64, dtype=np.float32), 64, 8, False, 7) == 1.0, "bundle"
    _, _, lift_c, _ = structure_ap(same, np.arange(64) % 8, 64, 7)
    assert lift_c < 1.5, f"collapse structure lift = {lift_c} (tie-break regression)"
    assert bundle_survival(same, 64, 8, False, 7) <= 0.30, "collapse bundle (tie-break regression)"
    SNC._selftest()

    # ---- v2 FIX (a) checks -------------------------------------------------------
    # 11. B=1 reduces EXACTLY to v1's top-1 Fano
    for p in (0.001, 0.1, 0.5, 0.9, 0.999):
        assert abs(fano_bits_list(p, 1024, 1) - fano_bits(p, 1024)) < 1e-9, "list-Fano B=1 reduction"
    # 12. ceiling is log2(n/B), NOT log2(n)
    assert abs(fano_bits_list(1.0 - 1e-12, 1024, 8) - 7.0) < 0.01, "list-Fano ceiling log2(n/B)"
    # 13. chance for a top-B decoder is B/n and must give ~0 bits
    assert fano_bits_list(8.0 / 1024, 1024, 8) < 0.05, "list-Fano at top-B chance"
    # 14. monotone non-decreasing in p
    prev = -1.0
    for p in (0.01, 0.05, 0.2, 0.5, 0.8, 0.99):
        cur = fano_bits_list(p, 1024, 8)
        assert cur >= prev - 1e-9, "list-Fano monotonicity"
        prev = cur
    # 15. THE DEFECT ITSELF: v1's mixed-criterion chain manufactures NEGATIVE destroyed bits on a
    #     null arm; the single-criterion v2 chain must not. Reproduced here on collapse codes.
    n, b = 64, 8
    acc_top1 = recoverability(same, n, 1.0, 7)
    acc_bund = bundle_survival(same, n, b, False, 7)
    v1_step = fano_bits(acc_top1, n) - fano_bits(acc_bund, n)          # the v1 (wrong) subtraction
    v2_step = (fano_bits_list(recoverability_topb(same, n, 1.0, 7, b), n, b)
               - fano_bits_list(acc_bund, n, b))                        # the v2 (right) one
    assert v1_step < -0.05, f"v1 defect should reproduce as negative destroyed bits, got {v1_step}"
    assert v2_step > -0.05, f"v2 chain still manufactures negative destroyed bits: {v2_step}"
    # 16. top-B recoverability is >= top-1 and hits the ceiling on orthogonal codes
    assert recoverability_topb(I, 64, 0.01, 7, 8) == 1.0, "top-B ceiling"
    assert recoverability_topb(same, 64, 1.0, 7, 8) <= 0.30, "top-B collapse floor"

    # ---- v2 FIX (b) checks -------------------------------------------------------
    # 17. sigma_half interpolates, and returns None when the curve never crosses
    assert sigma_half({"1": 1.0, "4": 1.0, "8": 1.0}, [1.0, 4.0, 8.0]) is None, "sigma_half none"
    sh = sigma_half({"1": 1.0, "4": 1.0, "8": 0.0}, [1.0, 4.0, 8.0])
    assert sh is not None and 4.0 < sh < 8.0, f"sigma_half interpolation = {sh}"

    # ---- v2 PRODUCTION-ARM checks -------------------------------------------------
    # 18. the live per-word code IS the live symbol code (the arm calls the live path)
    for w in ("aardvark", "water", "government"):
        assert np.array_equal(np.asarray(context_vector(w, d=64)),
                              np.asarray(symbol_vector(w, d=64))), "live word code mismatch"
    # 19. the live word code is BIPOLAR and SEED-FREE (a pure hash; no training, no seed)
    A = enc_live_word(["water", "river", "waters"], 64, 7)
    B = enc_live_word(["water", "river", "waters"], 64, 999)
    assert np.array_equal(A, B), "live word code must be seed-independent"
    # 20. and it is ORTHOGRAPHICALLY BLIND: water/waters are as unrelated as water/river
    c_ws = abs(float(A[0] @ A[2]))
    c_wr = abs(float(A[0] @ A[1]))
    assert c_ws < 0.35 and c_wr < 0.35, f"live codes unexpectedly correlated {c_ws} {c_wr}"
    print("[selftest] PASS (20 formula checks + saturation_negative_control)", flush=True)


# ----------------------------------------------------------------------------------
def main() -> int:
    if _ARGS.self_test:
        selftest()
        return 0
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} V={V} D_SWEEP={D_SWEEP} D_GATE={D_GATE} N_SWEEP={N_SWEEP} "
          f"SIGMAS={SIGMAS} SEEDS={SEEDS} out={out_dir}", flush=True)
    print(f"[live] CTX_D={CTX_D} GRADED_COMPARATOR={GRADED_COMPARATOR}", flush=True)
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
    print(f"[gold] simlex pairs={len(pairs)} covered={cov}", flush=True)

    done = completed_units(str(out_dir))
    for d in D_SWEEP:
        for arm in arms_for_d(d):
            for seed in SEEDS:
                key = unit_key(arm, d, seed, RUN_MODE, V)
                if key in done:
                    print(f"[skip] {key}", flush=True)
                    continue
                r = run_unit(arm, d, seed, words, ortho_pool, freq_pool, golds, pairs, w2i, out_dir)
                record_unit(str(out_dir), key, r)
                ngk = str(min(N_GATE, V))
                print(f"[unit] {arm:20s} d={d:5d} seed={seed} "
                      f"recov(s=1)={r['recoverability'][ngk]['1']:.4f} "
                      f"recov(s=8)={r['recoverability'][ngk].get('8', float('nan')):.4f} "
                      f"ortho_lift={r['structure']['GOLD_ORTHO']['lift']:.3f} "
                      f"freq_lift={r['structure']['GOLD_FREQBAND']['lift']:.3f} "
                      f"rho={r['simlex_rho']:.4f} ({r['elapsed_s']:.1f}s)", flush=True)

    units = load_units(str(out_dir))
    rows = [u for u in units.values() if u.get("arm") in ARMS]

    by_d: Dict[int, Dict[str, Dict]] = {}
    for d in D_SWEEP:
        per_arm: Dict[str, Dict] = {}
        for arm in arms_for_d(d):
            rs = [r for r in rows if r["arm"] == arm and r.get("d") == d]
            if not rs:
                continue
            agg: Dict = {"n_seeds": len(rs), "d_eff": rs[0]["d_eff"]}
            agg["recoverability"] = {
                n: {s: _mean([r["recoverability"][n][s] for r in rs if n in r["recoverability"]])
                    for s in rs[0]["recoverability"][n]} for n in rs[0]["recoverability"]}
            if rs[0].get("recoverability_collisionfree"):
                agg["recoverability_collisionfree"] = {
                    s: _mean([r["recoverability_collisionfree"][s] for r in rs])
                    for s in rs[0]["recoverability_collisionfree"]}
            agg["discriminability"] = {
                k: {s: _mean([r["discriminability"][k][s] for r in rs])
                    for s in rs[0]["discriminability"][k]} for k in rs[0]["discriminability"]}
            agg["structure"] = {
                g: {f: _mean([r["structure"][g][f] for r in rs]) for f in ("ap", "chance", "lift")}
                for g in rs[0]["structure"]}
            agg["simlex_rho"] = _mean([r["simlex_rho"] for r in rs])
            agg["simlex_pairs_covered"] = rs[0]["simlex_pairs_covered"]
            agg["knee_N"] = rs[0]["knee_N"]
            agg["sigma_half_at_N_GATE"] = rs[0]["sigma_half_at_N_GATE"]
            agg["stage_chain"] = [
                {"stage": rs[0]["stage_chain"][i]["stage"],
                 "criterion": rs[0]["stage_chain"][i]["criterion"],
                 "accuracy": _mean([r["stage_chain"][i]["accuracy"] for r in rs]),
                 "info_bits_lower_bound": _mean([r["stage_chain"][i]["info_bits_lower_bound"]
                                                 for r in rs]),
                 "destroyed_bits_vs_prev": _mean([r["stage_chain"][i]["destroyed_bits_vs_prev"]
                                                  for r in rs])}
                for i in range(len(rs[0]["stage_chain"]))]
            per_arm[arm] = agg
        by_d[d] = per_arm

    verdict, claims, extra = evaluate(by_d)
    failed = [c["gate_id"] for c in claims if not c["passed"]]

    # ---- THE TWO AXES, REPORTED SEPARATELY. NEVER AVERAGED.
    def axis_rows(d):
        pa = by_d.get(d, {})
        out = {}
        ngk = str(min(N_GATE, V))
        for a, agg in pa.items():
            out[a] = {
                "IDENTITY": {
                    "recoverability_curve_at_N_GATE": agg["recoverability"].get(ngk, {}),
                    "recoverability_collisionfree": agg.get("recoverability_collisionfree"),
                    "sigma_half": agg.get("sigma_half_at_N_GATE"),
                    "disc_ortho_headline": agg["discriminability"]["disc_ortho"].get(
                        f"{HEADLINE_SIGMA:g}"),
                    "disc_freq_headline": agg["discriminability"]["disc_freq"].get(
                        f"{HEADLINE_SIGMA:g}"),
                    "knee_N": agg.get("knee_N"),
                    "NOTE": ("a RANDOM encoding is near-OPTIMAL on this axis by design; scoring "
                             "high here is NOT a win"),
                },
                "STRUCTURE": {
                    "GOLD_ORTHO_lift": agg["structure"]["GOLD_ORTHO"]["lift"],
                    "GOLD_FREQBAND_lift": agg["structure"]["GOLD_FREQBAND"]["lift"],
                    "GOLD_PLANTED_lift": agg["structure"]["GOLD_PLANTED"]["lift"],
                    "simlex_rho": agg["simlex_rho"],
                    "NOTE": ("a RANDOM encoding must sit at lift ~1.0 / rho ~0.0 here; any real "
                             "lift IS the signal"),
                },
                "TRADEOFF": {
                    "stage_chain_bits": {st["stage"]: st["info_bits_lower_bound"]
                                         for st in agg["stage_chain"]},
                    "bits_destroyed_by_bundling_S2_to_S3": next(
                        (st["destroyed_bits_vs_prev"] for st in agg["stage_chain"]
                         if st["stage"] == "S3_BUNDLE"), None),
                    "chain_ceiling_bits": math.log2(min(N_GATE, V) / float(BUNDLE_B)),
                },
            }
        return out

    axes = {str(d): axis_rows(d) for d in D_SWEEP}
    concept_stats = _CONCEPT_CACHE.get(CONCEPT_ONLY_D, (None, None, {}))[2]

    msg = (f"{verdict}: {len(claims) - len(failed)}/{len(claims)} pre-registered gates passed"
           + (f"; FAILED={failed}" if failed else "")
           + ". PRODUCTION ARMS SCORED: P_LIVE_WORD, P_LIVE_CONCEPT, C_CONCEPT_SHUFFLED. "
             "TWO AXES REPORTED SEPARATELY AND DELIBERATELY NOT AVERAGED.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": time.time() - t_start,
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "prereg": "preregs/exp_encoding_quality_instrument_v2.md",
        "parent_prereg": "preregs/exp_encoding_quality_instrument_v1.md",
        "config": {"V": V, "D_SWEEP": D_SWEEP, "D_GATE": D_GATE, "N_SWEEP": N_SWEEP,
                   "N_GATE": N_GATE, "SIGMAS": SIGMAS, "HEADLINE_SIGMAS": HEADLINE_SIGMAS,
                   "SEEDS": SEEDS, "K_DISTRACT": K_DISTRACT, "BUNDLE_B": BUNDLE_B,
                   "AP_PROBES": AP_PROBES, "CORPUS_BYTES": CORPUS_BYTES,
                   "N_PLANTED_GROUPS": N_PLANTED_GROUPS},
        "production_encoder_identification": {
            "method": ("RUNTIME: imported the two live entry points and diffed sys.modules; then "
                       "reconciled to data/capability_registry.jsonl. Never the reverse, and never "
                       "from grep."),
            "hdlab_modules_on_disk": 147,
            "encoder_named_candidates": 12,
            "hdlab_modules_loaded_by_live_entry_points": 40,
            "encoder_named_candidates_on_live_path": 0,
            "live_word_encoder": ("INLINED in hdlab/grounding_acquisition_loop.context_vector and "
                                  "exposed as hdlab/reading_grounding_loop.symbol_vector: "
                                  "sha256(w)[:8] -> seed -> default_rng(seed).choice([-1,+1], d)"),
            "live_concept_encoder": ("hdlab/reading_grounding_loop.ConceptSpace.bundle(lemma) with "
                                     "GRADED_COMPARATOR=True = accumulated raw sum of "
                                     "context_vector_masked over the corpus"),
            "live_constants_observed": {"CTX_D": CTX_D, "GRADED_COMPARATOR": bool(GRADED_COMPARATOR)},
            "registry_agreement": ("every encoder-named registry row is "
                                   "WIRED_BUT_NOT_PIPELINE_REACHABLE; NO registry row names the "
                                   "live word encoder at all"),
        },
        "concept_profile_build": concept_stats,
        "TWO_AXES": axes,
        "axes_note": ("REPORTED SEPARATELY BY DESIGN. Any single scalar mixing IDENTITY and "
                      "STRUCTURE is unfalsifiable because a random encoding is near-optimal on "
                      "IDENTITY and at chance on STRUCTURE. This cell refuses to average them."),
        "scope_disclaimer": (
            "v2 fixes v1's mixed-criterion M4 chain (now top-8 at every stage, list-Fano bound, "
            "ceiling log2(N/B)=7 bits -- NOT comparable to v1's 10-bit numbers) and retires "
            "sigma=1.0 as the HEADLINE (kept as the GATE point). A_ORACLE_ONEHOT runs at d=V and "
            "is NOT dimension-matched. Fano numbers are LOWER BOUNDS. P_LIVE_CONCEPT is the "
            "production ALGORITHM run on the instrument's corpus, not a snapshot of any persisted "
            "store; data/foundation/** is never opened."),
        "gates": claims,
        "per_arm_by_d": {str(k): v for k, v in by_d.items()},
        "vocab_sample": words[:20],
        "simlex_pairs_covered": cov,
        **extra,
    }
    write_metrics(out_dir, metrics, results=rows, gate_claims=None)
    print("\n" + msg, flush=True)
    for c in claims:
        print(f"  [{'PASS' if c['passed'] else 'FAIL'}] {c['gate_id']:5s} {c['claim']:62s} "
              f"observed={c['observed']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
