"""exp_storage_quality_instrument_v1 -- an isolated, VALIDATED instrument for COMPONENT #2 (STORAGE).

Pre-reg: preregs/exp_storage_quality_instrument_v1.md (thresholds fixed before any arm was scored).

THE DISCRIMINATOR: WITHIN-ITEM FACET SCORING. Ask the store for ONE facet of an item; the candidate
pool is that item's OWN other facets' golds. A blended sum answers (near) the same thing whatever
facet is asked for, so its argmax is (near) constant in k -> 1/F = chance. A store keeping separate
addresses returns facet k -> 1.0. Same scorer, two architectures, cleanly separated. Plus
delta_key = S3(true key) - S3(deranged key), the single-number architecture discriminator.

WHAT THIS CELL CORRECTS IN THE DRAFT SPEC (measured, not read): the SHIPPED live store accumulates
BARE symbol vectors (context_vector -> `acc += rng.choice([-1,1], d)` per content word), NOT
bind(REL:k, filler). The role-bound StructuralEncoder path exists but is opt-in and default-OFF.
So "degraded address" and "absent address" are TWO DIFFERENT STORES and both are scored here
(A2_BAG = shipped, A2R_ROLEBOUND = opt-in).

THE LOAD AXIS THAT ACTUALLY BITES (found by smoke, and the reason the first cut of this cell was
invalid): with a coherently-repeated gold, MORE occurrences HELP -- signal accumulates linearly and
crosstalk only as sqrt -- so T and junk-per-occurrence alone leave every non-degenerate arm pinned
at 1.000. The defect the live store actually has is SAME-KEY COLLISION: T occurrences summed with
no occurrence index, each writing a DIFFERENT filler under the SAME relation. `p_collide` is that
axis, and it is where the arms spread. In the LIVE regime it happens for free on real text.

Discipline: OMP/OPENBLAS pinned before numpy; ASCII only; sorted(set()) determinism; per-seed
resume via experiments/_seed_checkpoint.py *_config entry points (config-hashed keys that RAISE on
mismatch, fixed at ee7c42c0f). tools/exp_checkpoint.py is deliberately NOT used, so its unfixed
unit_key-ignores-N defect cannot apply. data/foundation/** is opened read-only and never written.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(_HERE))

from _seed_checkpoint import (  # noqa: E402
    aggregate_partials_config,
    get_output_dir,
    record_gate,
    resumable_seeds_config,
    write_metrics,
    write_partial_config,
)

ANCHOR_NAME = "storage_quality_instrument_v1"

# ------------------------------------------------------------------ config ---
F_FACETS = 4                 # chance = 1/F = 0.25
D_LIVE = 256                 # the live dimensionality
N_BOOT = 10000               # bootstrap resamples over ITEMS
SEEDS_FULL = [7, 11, 13, 19, 23]
SEEDS_SMOKE = [7]

T_GRID_FULL = [1, 4, 16, 64]
T_GRID_SMOKE = [1, 16]
NEXTRA_GRID_FULL = [0, 8, 64]
NEXTRA_GRID_SMOKE = [0, 8]
COLLIDE_GRID_FULL = [0.0, 0.5, 0.9]
COLLIDE_GRID_SMOKE = [0.0, 0.9]

SYN_ITEMS_FULL = 400
SYN_ITEMS_SMOKE = 120
LIVE_ITEMS_FULL = 300
LIVE_ITEMS_SMOKE = 60
LIVE_SCAN_LINES_FULL = 400000
LIVE_SCAN_LINES_SMOKE = 60000

# IV4 ladder. AMENDMENT 2026-08-15 (smoke-driven, before any scientific verdict): the
# pre-registered 6-level ladder topped out at sigma=4, where A1_SLOTTED still read 0.9854, and a
# first extension to sigma=32 still only reached 0.4021 while plainly still descending -- the
# ladder was too short to answer the question IV4 asks ("can this metric go down at all"), which is
# a defect in the CONTROL, not evidence about the store. Extended until it moves; the gate itself
# (monotone rho <= -0.8 AND reaching chance+0.10 at the top) is UNCHANGED.
NOISE_LADDER = [0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, 256.0]
FREQ_RATIO_MAX = 4.0        # within-item gold fillers must sit in one frequency stratum
CHANCE_S3 = 1.0 / F_FACETS
# Power floor for GATE EVALUATION. AMENDMENT 2026-08-15 (smoke-driven, before any scientific
# verdict). Requiring all F facets to be written makes some grid cells INFEASIBLE (at T=1 with
# p_collide=0.9, the chance all four golds are written is 1e-4, so the cell is empty). Such cells
# are REPORTED with their n and the reason, and are not gated -- a gate evaluated on n=0 or n=12 is
# not a test of anything. Points at or above this n are gated exactly as pre-registered.
MIN_ITEMS_FOR_GATE = 30

# HEADLINE operating point, pre-registered. IV8 may MOVE it if the arms do not spread there, and
# both points are then reported.
HEADLINE_T = 16
HEADLINE_NEXTRA = 8
HEADLINE_COLLIDE = 0.5

# ------------------------------------------------------------ live imports ---
import hdlab.grounding_acquisition_loop as gal  # noqa: E402
import hdlab.reading_grounding_loop as rgl  # noqa: E402

SYMVEC = rgl.symbol_vector
BIND = rgl._bipolar_bind


# ================================================================ utilities ==
def _unit(x: np.ndarray) -> np.ndarray:
    """Row-normalise; a zero row stays zero (cosine against it is then 0, never NaN)."""
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / np.where(n < 1e-12, 1.0, n)


def _sign1(x: np.ndarray) -> np.ndarray:
    """np.sign with the live zero convention (0 -> +1), matching context_vector."""
    out = np.sign(x)
    out[out == 0] = 1.0
    return out


def score_predictions(pred: np.ndarray, written: np.ndarray) -> np.ndarray:
    """pred (n_items, F) -> per-item accuracy over the facets ACTUALLY WRITTEN at this load.

    `written[i,k]` is a property of the WORLD, not of any arm, so every arm is scored on the
    identical query set. Restricting to written facets is what keeps this a ROUND TRIP ("did what
    went in come back out") rather than a test of whether the store can invent content that was
    never put in it -- at T=1 on real text most facet golds have simply not been written yet.
    The candidate POOL stays all F golds, so chance stays 1/F.
    """
    k = np.arange(pred.shape[1])[None, :]
    ok = ((pred == k) & written).sum(axis=1)
    cnt = written.sum(axis=1)
    return ok / np.maximum(cnt, 1)


_TIE_RNG = np.random.default_rng(20260815)


def predict_from_probes(probes: np.ndarray, golds: np.ndarray) -> np.ndarray:
    """THE ONE SCORER. probes (n,F,d), golds (n,F,d) -> argmax over the item's OWN F golds.

    Every probe-producing arm goes through this identical function; arms differ ONLY in what they
    put in `probes`. That is the one-variable discipline of the whole instrument.
    """
    P = _unit(probes.astype(np.float64))
    G = _unit(golds.astype(np.float64))
    sims = np.einsum("ikd,ijd->ikj", P, G)
    # Break EXACT ties uniformly at random rather than by index order. A zero-norm probe (the
    # store returned nothing) otherwise always predicts facet 0, which correlates with the gold
    # index and manufactures above-chance accuracy out of an empty answer.
    sims = sims + _TIE_RNG.uniform(0.0, 1e-9, size=sims.shape)
    return np.argmax(sims, axis=2)


def derangement(F: int, rng: np.random.Generator) -> np.ndarray:
    """A permutation of range(F) with no fixed point (rejection sampling; F>=2)."""
    while True:
        p = rng.permutation(F)
        if not np.any(p == np.arange(F)):
            return p


def bootstrap_ci(per_item: np.ndarray, boot_idx: np.ndarray) -> Tuple[float, float, float]:
    """(mean, ci_lo, ci_hi) resampling ITEMS (never queries; within-item queries are dependent)."""
    if per_item.size == 0:
        return float("nan"), float("nan"), float("nan")
    draws = per_item[boot_idx].mean(axis=1)
    return (float(per_item.mean()),
            float(np.percentile(draws, 2.5)),
            float(np.percentile(draws, 97.5)))


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rho without scipy (ties averaged)."""
    def rank(v):
        v = np.asarray(v, dtype=np.float64)
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=np.float64)
        r[order] = np.arange(len(v), dtype=np.float64)
        for val in np.unique(v):
            m = v == val
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r
    a, b = rank(x), rank(y)
    a = a - a.mean()
    b = b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


# ====================================================== world construction ===
class World:
    """Items, facets, keys, golds and per-occurrence payloads. Shared by EVERY arm.

    Representation is index-based so the store builders are vectorised:
      pool        (P, d)   filler content vectors
      keyset      (K, d)   key vectors (each item names its own F facet keys by index)
      per item i: kidx (m,) into keyset, fidx (m,) into pool, occ_ptr (T,) reduceat offsets,
                  facet_keys (F,) into keyset, gold_fids (F,) into pool
      bag_occ[i]  (T, d)   what the BAG encoder wrote at each occurrence
    """

    def __init__(self, d: int) -> None:
        self.d = d
        self.regime = ""
        self.names: List[str] = []
        self.pool = np.zeros((0, d))
        self.keyset = np.zeros((0, d))
        self.pool_names: List[str] = []
        self.key_names: List[str] = []
        self.kidx: List[np.ndarray] = []
        self.fidx: List[np.ndarray] = []
        self.occ_ptr: List[np.ndarray] = []
        self.facet_keys: List[np.ndarray] = []
        self.gold_fids: List[np.ndarray] = []
        self.bag_occ: List[np.ndarray] = []
        self.written = np.zeros((0, F_FACETS), dtype=bool)
        self.filler_freq: Dict[str, int] = {}
        self.notes: Dict[str, object] = {}

    def compute_written(self) -> None:
        """written[i,k] = facet k's GOLD filler was actually written under facet k's key at
        this load. Property of the world; every arm is scored on the identical query set."""
        w = np.zeros((self.n, F_FACETS), dtype=bool)
        for i in range(self.n):
            ki, fi = self.kidx[i], self.fidx[i]
            for k in range(F_FACETS):
                w[i, k] = bool(np.any((ki == self.facet_keys[i][k])
                                      & (fi == self.gold_fids[i][k])))
        self.written = w

    def drop_unwritten_items(self) -> int:
        """Remove items unless ALL F facet golds were written. Returns the number dropped.

        AMENDMENT 2026-08-15 (smoke-driven, made BEFORE any scientific verdict was read; the smoke
        published INSTRUMENT_STILL_LOOSE and no quality number). The first cut required only that
        SOME facet be written, which left the candidate pool containing golds that had never been
        written -- so an arm could score far above chance by detecting mere PRESENCE rather than
        ADDRESS. Measured leak: A2U_BAG_UNKEYED, an arm with no key at all, reached 0.932 against
        chance 0.250 at the low-coverage points, and A1_SLOTTED under a DERANGED key reached 0.541
        where it must be ~0. That is the exact failure IV5 exists to catch, so the construction is
        fixed rather than the threshold. With all F written, coverage is 1.0 by construction and
        the pool is uniform in writtenness, so presence carries no information."""
        keep = [i for i in range(self.n) if self.written[i].all()]
        if len(keep) == self.n:
            return 0
        dropped = self.n - len(keep)
        self.names = [self.names[i] for i in keep]
        for attr in ("kidx", "fidx", "occ_ptr", "facet_keys", "gold_fids", "bag_occ"):
            setattr(self, attr, [getattr(self, attr)[i] for i in keep])
        self.written = self.written[keep]
        return dropped

    @property
    def n(self) -> int:
        return len(self.names)

    def golds(self) -> np.ndarray:
        return np.stack([self.pool[g] for g in self.gold_fids])

    def gold_names(self, i: int) -> List[str]:
        return [self.pool_names[j] for j in self.gold_fids[i]]

    def facet_key_names(self, i: int) -> List[str]:
        return [self.key_names[j] for j in self.facet_keys[i]]

    def facet_key_vecs(self, i: int) -> np.ndarray:
        return self.keyset[self.facet_keys[i]]


class _Interner:
    def __init__(self, d: int, prefix: str = ""):
        self.d, self.prefix = d, prefix
        self.names: List[str] = []
        self.idx: Dict[str, int] = {}
        self.vecs: List[np.ndarray] = []

    def get(self, name: str) -> int:
        j = self.idx.get(name)
        if j is None:
            j = len(self.names)
            self.idx[name] = j
            self.names.append(name)
            self.vecs.append(SYMVEC(self.prefix + name, self.d))
        return j

    def mat(self) -> np.ndarray:
        return (np.stack(self.vecs) if self.vecs
                else np.zeros((0, self.d)))


def build_world_syn(seed: int, n_items: int, T: int, n_extra: int, p_collide: float,
                    d: int) -> World:
    """Synthetic world drawn with the LIVE symbol_vector convention, so the geometry is production
    geometry (bipolar, sha256-seeded, near-orthogonal) and not a lookalike.

    p_collide = P(an occurrence writes a DIFFERENT filler under a facet key instead of the gold).
    This is the occurrence-indexing defect: T occurrences summed with no index. The gold remains
    the DOMINANT filler for that key, exactly as it is derived in the LIVE regime.
    """
    rng = np.random.default_rng(seed * 1000003 + 17)
    w = World(d)
    w.regime = "SYN"
    P = _Interner(d)
    K = _Interner(d, prefix="REL:")
    facet_key_ids = np.array([K.get("synrel%02d" % k) for k in range(F_FACETS)])
    junk_key_ids = np.array([K.get("synjunkrel%03d" % j) for j in range(64)])
    N_POOL = 40000

    for i in range(n_items):
        w.names.append("synitem%05d" % i)
        gold_names = ["synfil%06d" % int(x) for x in
                      rng.choice(N_POOL, F_FACETS, replace=False)]
        gold_fids = np.array([P.get(g) for g in gold_names])
        kk, ff, ptr = [], [], []
        for _t in range(T):
            _start = len(kk)
            for k in range(F_FACETS):
                collide = rng.random() < p_collide
                if collide:
                    fid = P.get("synfil%06d" % int(rng.integers(N_POOL)))
                else:
                    fid = gold_fids[k]
                kk.append(facet_key_ids[k])
                ff.append(fid)
            for _e in range(n_extra):
                kk.append(int(junk_key_ids[int(rng.integers(len(junk_key_ids)))]))
                ff.append(P.get("synfil%06d" % int(rng.integers(N_POOL))))
            if len(kk) > _start:          # never emit an empty reduceat group
                ptr.append(_start)
        w.kidx.append(np.asarray(kk, dtype=np.int64))
        w.fidx.append(np.asarray(ff, dtype=np.int64))
        w.occ_ptr.append(np.asarray(ptr, dtype=np.int64))
        w.facet_keys.append(facet_key_ids.copy())
        w.gold_fids.append(gold_fids)

    w.pool, w.pool_names = P.mat(), P.names
    w.keyset, w.key_names = K.mat(), K.names
    # SYN bag = the occurrence's raw filler content, no key ever applied (the shipped semantics)
    for i in range(w.n):
        terms = w.pool[w.fidx[i]]
        w.bag_occ.append(np.add.reduceat(terms, w.occ_ptr[i], axis=0))
    w.filler_freq = {nm: 1 for nm in w.pool_names}   # flat by construction; recorded, not assumed
    w.compute_written()
    n_drop = w.drop_unwritten_items()
    w.notes = {"p_collide": p_collide, "T": T, "n_extra": n_extra,
               "facet_coverage": float(w.written.mean()) if w.n else 0.0,
               "n_items_dropped_nothing_written": n_drop, "n_items": w.n}
    return w


_LIVE_CACHE: Dict[Tuple[int, int], object] = {}


def _scan_corpus(n_lines: int) -> Tuple[List[str], Dict[str, List[int]], Dict[str, int]]:
    """Cheap (no-parse) pass: sentences, lemma -> sentence indices, lemma -> corpus count."""
    path = REPO / "data" / "corpora" / "simplewiki" / "simplewiki_clean_v1.txt"
    sents: List[str] = []
    index: Dict[str, List[int]] = {}
    freq: Dict[str, int] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for li, line in enumerate(fh):
            if li >= n_lines:
                break
            s = line.strip()
            if not (40 <= len(s) <= 240):
                continue
            si = len(sents)
            sents.append(s)
            for lm in sorted(set(rgl.normalize_lemma(x) for x in gal.content_words(s))):
                if not lm:
                    continue
                freq[lm] = freq.get(lm, 0) + 1
                b = index.setdefault(lm, [])
                if len(b) < 200:
                    b.append(si)
    return sents, index, freq


_LIVE_ITEMS_CACHE: Dict[Tuple[int, int, int, int], object] = {}


def _select_live_items(seed: int, n_items: int, T_max: int, d: int, scan_lines: int):
    """Select items ONCE at T_max and parse their sentences ONCE, so the T sweep is a clean
    one-variable truncation of the SAME items rather than a different population per T."""
    ck = (seed, n_items, T_max, scan_lines)
    if ck in _LIVE_ITEMS_CACHE:
        return _LIVE_ITEMS_CACHE[ck]
    sk = (scan_lines, d)
    if sk not in _LIVE_CACHE:
        t0 = time.time()
        sents, index, freq = _scan_corpus(scan_lines)
        enc = rgl.StructuralEncoder(str(REPO), d=d)
        _LIVE_CACHE[sk] = (sents, index, freq, enc)
        print("[live] scanned %d sentences, %d lemmas in %.1fs"
              % (len(sents), len(index), time.time() - t0), flush=True)
    sents, index, freq, enc = _LIVE_CACHE[sk]

    rng = np.random.default_rng(seed * 7919 + 3)
    cands = sorted([lm for lm, ix in index.items()
                    if len(ix) >= T_max and 40 <= freq[lm] <= 50000 and len(lm) >= 3])
    rng.shuffle(cands)

    rows = []
    n_drop_freq = n_drop_facets = 0
    t0 = time.time()
    for lm in cands:
        if len(rows) >= n_items:
            break
        occ = index[lm][:T_max]
        per_occ = [enc.features(sents[si], lm) for si in occ]
        rel_fill: Dict[str, Dict[str, int]] = {}
        for fs in per_occ:
            for rel, fil in fs:
                rel_fill.setdefault(rel, {})[fil] = rel_fill.setdefault(rel, {}).get(fil, 0) + 1
        ranked = sorted(rel_fill.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))
        # Gather a CANDIDATE SET (not just the top F), then SEARCH it for an F-subset that is
        # frequency-matched. Choosing top-F-then-reject discarded 91% of otherwise-usable items at
        # smoke scale, at full parse cost each; this finds the matched subset at zero extra parses.
        pool_cands: List[Tuple[str, str, int, int]] = []   # (rel, filler, support, corpus_freq)
        used = set()
        for rel, fills in ranked:
            best = sorted(fills.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            if best in used or freq.get(best, 0) < 5:
                continue
            used.add(best)
            pool_cands.append((rel, best, sum(fills.values()), freq.get(best, 1)))
            if len(pool_cands) >= 16:
                break
        if len(pool_cands) < F_FACETS:
            n_drop_facets += 1
            continue
        by_freq = sorted(pool_cands, key=lambda c: (c[3], c[0]))
        best_win = None
        for a in range(len(by_freq) - F_FACETS + 1):
            win = by_freq[a:a + F_FACETS]
            if win[-1][3] / max(1.0, float(win[0][3])) > FREQ_RATIO_MAX:
                continue
            sup = sum(c[2] for c in win)
            if best_win is None or sup > best_win[0]:
                best_win = (sup, win)
        if best_win is None:
            n_drop_freq += 1
            continue
        chosen = [(c[0], c[1]) for c in sorted(best_win[1], key=lambda c: c[0])]
        rows.append((lm, chosen, per_occ, occ))
    print("[live] selected %d items (dropped %d too-few-facets, %d freq-stratum) in %.1fs"
          % (len(rows), n_drop_facets, n_drop_freq, time.time() - t0), flush=True)
    out = (rows, sents, freq, {"n_dropped_too_few_facets": n_drop_facets,
                               "n_dropped_freq_stratum": n_drop_freq})
    _LIVE_ITEMS_CACHE[ck] = out
    return out


def build_world_live(seed: int, n_items: int, T: int, d: int, scan_lines: int,
                     T_max: int) -> World:
    """REAL corpus, REAL code. Items are real lemmas; facets are real UD relation labels from
    StructuralEncoder.features; the BAG store is built by calling rgl.context_vector_masked and
    the ROLE-BOUND store by re-applying the encoder's own bind, both verified byte-identical to
    the live functions in selftest(). Gold for facet k = the DOMINANT filler for relation k;
    occurrences supplying a different filler for the same relation are left in as real same-key
    collisions, because that is the live situation."""
    rows, sents, freq, drops = _select_live_items(seed, n_items, T_max, d, scan_lines)
    w = World(d)
    w.regime = "LIVE"
    P = _Interner(d)
    K = _Interner(d, prefix="REL:")

    for lm, chosen, per_occ, occ in rows:
        gold_fids = np.array([P.get(f) for _r, f in chosen])
        fkeys = np.array([K.get(r) for r, _f in chosen])
        relpos = {r: k for k, (r, _f) in enumerate(chosen)}
        kk, ff, ptr = [], [], []
        for fs in per_occ[:T]:
            _start = len(kk)
            for rel, fil in fs:
                kk.append(K.get(rel))
                ff.append(P.get(fil))
            if len(kk) > _start:          # an unparseable / featureless occurrence adds no group
                ptr.append(_start)
        if not kk:
            continue
        w.names.append(lm)
        w.kidx.append(np.asarray(kk, dtype=np.int64))
        w.fidx.append(np.asarray(ff, dtype=np.int64))
        w.occ_ptr.append(np.asarray(ptr, dtype=np.int64))
        w.facet_keys.append(fkeys)
        w.gold_fids.append(gold_fids)
        # THE SHIPPED ENCODER, called for real, once per occurrence
        w.bag_occ.append(np.stack([rgl.context_vector_masked(sents[si], lm) for si in occ[:T]]))
        _ = relpos

    w.pool, w.pool_names = P.mat(), P.names
    w.keyset, w.key_names = K.mat(), K.names
    w.filler_freq = {nm: freq.get(nm, 1) for nm in w.pool_names}
    w.compute_written()
    n_drop_unwritten = w.drop_unwritten_items()
    ratios = [max(w.filler_freq[n] for n in w.gold_names(i))
              / max(1.0, min(w.filler_freq[n] for n in w.gold_names(i))) for i in range(w.n)]         or [float("nan")]
    w.notes = dict(drops, n_items=w.n, T=T,
                   facet_coverage=(float(w.written.mean()) if w.n else 0.0),
                   n_items_dropped_nothing_written=n_drop_unwritten,
                   mean_gold_freq_ratio_within_item=float(np.mean(ratios)),
                   max_gold_freq_ratio_within_item=float(np.max(ratios)),
                   mean_terms_per_item=(float(np.mean([len(x) for x in w.kidx]))
                                        if w.n else 0.0),
                   n_distinct_relations=len(w.key_names))
    return w


# ================================================================ the STORES ==
def store_bag(w: World, sign_occ: bool, sign_store: bool) -> np.ndarray:
    """THE SHIPPED STORE. ConceptSpace._sums semantics: `_sums[lemma] += ctx_vec` where ctx_vec is
    a BARE bag of content-word symbol vectors. No key is ever applied at write time."""
    out = np.zeros((w.n, w.d))
    for i in range(w.n):
        occ = w.bag_occ[i]
        acc = (_sign1(occ) if sign_occ else occ).sum(axis=0)
        out[i] = _sign1(acc) if sign_store else acc
    return out


def store_rolebound(w: World, sign_occ: bool, sign_store: bool) -> np.ndarray:
    """The opt-in StructuralEncoder path: `_sums[lemma] += sum_k bind(REL:k, filler_k)`."""
    out = np.zeros((w.n, w.d))
    for i in range(w.n):
        terms = w.keyset[w.kidx[i]] * w.pool[w.fidx[i]]
        if sign_occ:
            acc = _sign1(np.add.reduceat(terms, w.occ_ptr[i], axis=0)).sum(axis=0)
        else:
            acc = terms.sum(axis=0)
        out[i] = _sign1(acc) if sign_store else acc
    return out


def store_slotted(w: World) -> np.ndarray:
    """The ARCHITECTURE REFERENCE ("spokes"): one accumulator per (item, facet). A real
    superposing store, not an oracle: each slot still bundles EVERY term written under its own
    key, including same-key collisions, so it degrades under the same load the blend does."""
    out = np.zeros((w.n, F_FACETS, w.d))
    for i in range(w.n):
        ki, fi = w.kidx[i], w.fidx[i]
        for k in range(F_FACETS):
            m = ki == w.facet_keys[i][k]
            if m.any():
                out[i, k] = w.pool[fi[m]].sum(axis=0)
    return out


def probes_unbind(store: np.ndarray, w: World, key_perm: Optional[np.ndarray]) -> np.ndarray:
    """probe(i, k) = unbind(store[i], key[perm(k)]). Bipolar unbind == bind == elementwise mul."""
    perm = np.arange(F_FACETS) if key_perm is None else key_perm
    out = np.zeros((w.n, F_FACETS, w.d))
    for i in range(w.n):
        out[i] = store[i][None, :] * w.facet_key_vecs(i)[perm]
    return out


def probes_slotted(slots: np.ndarray, key_perm: Optional[np.ndarray]) -> np.ndarray:
    perm = np.arange(F_FACETS) if key_perm is None else key_perm
    return slots[:, perm, :]


def probes_oracle(w: World, key_perm: Optional[np.ndarray]) -> np.ndarray:
    perm = np.arange(F_FACETS) if key_perm is None else key_perm
    return w.golds()[:, perm, :]


def probes_unkeyed(store: np.ndarray) -> np.ndarray:
    """The bag's BEST SHOT: the raw sum, no unbind. Constant in k by construction."""
    return np.repeat(store[:, None, :], F_FACETS, axis=1)


def store_factstore(w: World, seed: int, n_dim: int) -> Tuple[np.ndarray, np.ndarray]:
    """The REAL HDFactStore. item = subject; the F facets map onto its own roles
    (REL, ARG1, SOURCE, TRUST). Facts are held as SEPARATE vectors, so the read path is per-role
    unbind of ONE fact vector, not of a blend. Golds come from the store's OWN codec."""
    import hdlab.hd_fact_store as hfs
    roles = ["REL", "ARG1", "SOURCE", "TRUST"][:F_FACETS]
    st = hfs.HDFactStore(n_dim=n_dim, seed=seed)
    probes = np.zeros((w.n, F_FACETS, n_dim))
    golds = np.zeros((w.n, F_FACETS, n_dim))
    for i in range(w.n):
        f = w.gold_names(i)
        vec = st._encode_fact(w.names[i], f[0], f[1], f[2], f[3])
        for k, role in enumerate(roles):
            probes[i, k] = hfs._bipolar_bind(vec, st.codec.role_key(role)).numpy()
            golds[i, k] = st.codec._sym_vec(f[k]).numpy()
    return probes, golds


# ================================================================ the FLOORS ==
def pred_orthographic(w: World) -> np.ndarray:
    """ZERO store signal: char-trigram cosine between the RELATION LABEL string and each candidate
    filler string. An orthographic channel cannot vary its answer with k in any informed way."""
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=1024)
    cache: Dict[str, np.ndarray] = {}

    def ev(s: str) -> np.ndarray:
        if s not in cache:
            cache[s] = np.asarray(enc.encode(s), dtype=np.float64)
        return cache[s]

    pred = np.zeros((w.n, F_FACETS), dtype=int)
    for i in range(w.n):
        kv = _unit(np.stack([ev(r) for r in w.facet_key_names(i)]))
        gv = _unit(np.stack([ev(f) for f in w.gold_names(i)]))
        pred[i] = np.argmax(kv @ gv.T, axis=1)
    return pred


def pred_frequency(w: World) -> np.ndarray:
    """The HARDER frequency floor: always answer the globally commonest candidate. Constant in k,
    so it can only beat chance if the within-item golds are NOT frequency-matched (gate IV5)."""
    pred = np.zeros((w.n, F_FACETS), dtype=int)
    for i in range(w.n):
        c = [w.filler_freq.get(f, 1) for f in w.gold_names(i)]
        pred[i, :] = int(np.argmax(c))
    return pred


# ============================================================== ARM ASSEMBLY ==
def run_arms(w: World, seed: int, noise_sigma: float = 0.0,
             with_factstore: bool = True) -> Dict[str, Dict[str, np.ndarray]]:
    """Every arm, both key conditions, on ONE world. Arms differ ONLY in the store; the scorer is
    predict_from_probes for all of them."""
    rng = np.random.default_rng(seed * 104729 + 11)
    perm = derangement(F_FACETS, rng)
    G = w.golds()

    def noisy(x: np.ndarray) -> np.ndarray:
        if noise_sigma <= 0.0:
            return x
        scale = np.linalg.norm(x, axis=-1, keepdims=True) / np.sqrt(x.shape[-1])
        return x + noise_sigma * scale * rng.standard_normal(x.shape)

    s_bag = noisy(store_bag(w, False, False))
    s_bag_sign = noisy(store_bag(w, True, True))
    s_rb = noisy(store_rolebound(w, False, False))
    s_rb_sign = noisy(store_rolebound(w, True, True))
    slots = noisy(store_slotted(w))

    out: Dict[str, Dict[str, np.ndarray]] = {}

    W = w.written

    def add(name, p_true, p_der, golds=None):
        gg = G if golds is None else golds
        out[name] = {"true": score_predictions(predict_from_probes(p_true, gg), W),
                     "derange": score_predictions(predict_from_probes(p_der, gg), W)}

    add("A0_ORACLE_DICT", probes_oracle(w, None), probes_oracle(w, perm))
    add("A1_SLOTTED", probes_slotted(slots, None), probes_slotted(slots, perm))
    add("A2_BAG", probes_unbind(s_bag, w, None), probes_unbind(s_bag, w, perm))
    add("A2R_ROLEBOUND", probes_unbind(s_rb, w, None), probes_unbind(s_rb, w, perm))
    add("A3_BAG_SIGN", probes_unbind(s_bag_sign, w, None), probes_unbind(s_bag_sign, w, perm))
    add("A3R_ROLEBOUND_SIGN", probes_unbind(s_rb_sign, w, None),
        probes_unbind(s_rb_sign, w, perm))

    pu = probes_unkeyed(s_bag)
    add("A2U_BAG_UNKEYED", pu, pu)

    rnd = rng.standard_normal(s_rb.shape)
    rnd = rnd / np.linalg.norm(rnd, axis=1, keepdims=True) * np.linalg.norm(
        s_rb, axis=1, keepdims=True)
    add("A5_NULL_CONTENT", probes_unbind(rnd, w, None), probes_unbind(rnd, w, perm))

    sp = rng.permutation(w.n)
    add("A7_SCRAMBLE", probes_unbind(s_rb[sp], w, None), probes_unbind(s_rb[sp], w, perm))

    if with_factstore:
        for nd, tag in ((w.d, "A4_FACTSTORE_d%d" % w.d), (8192, "A4_FACTSTORE_d8192")):
            try:
                fp, fg = store_factstore(w, seed, nd)
                out[tag] = {"true": score_predictions(predict_from_probes(fp, fg), W),
                            "derange": score_predictions(
                                predict_from_probes(fp[:, perm, :], fg), W)}
            except Exception as exc:  # noqa: BLE001
                print("[warn] %s unavailable: %s" % (tag, exc), flush=True)

    if w.regime == "LIVE":
        po = pred_orthographic(w)
        out["A8_ORTHOGRAPHIC"] = {"true": score_predictions(po, W),
                                  "derange": score_predictions(po[:, perm], W)}
        pf = pred_frequency(w)
        out["A9_FREQUENCY"] = {"true": score_predictions(pf, W),
                               "derange": score_predictions(pf[:, perm], W)}
    return out


# ============================================================== S1 FIDELITY ===
def s1_fidelity(w: World) -> Dict[str, float]:
    """Whole-store item recovery: read each item back, argmax over the WHOLE written pool.
    Chance = 1/n. Separate from S3 (whose pool is within-item) and reported alongside it."""
    out: Dict[str, float] = {}
    q_bag = _unit(store_bag(w, False, False))
    q_rb = _unit(store_rolebound(w, False, False))
    p_bag = _unit(np.stack([w.bag_occ[i].sum(axis=0) for i in range(w.n)]))
    p_rb = _unit(np.stack([(w.keyset[w.kidx[i]] * w.pool[w.fidx[i]]).sum(axis=0)
                           for i in range(w.n)]))
    for name, q, p in (("A2_BAG", q_bag, p_bag), ("A2R_ROLEBOUND", q_rb, p_rb)):
        pred = np.argmax(p @ q.T, axis=1)
        out[name] = float((pred == np.arange(w.n)).mean())
    out["chance"] = 1.0 / max(1, w.n)
    out["n"] = float(w.n)
    return out


# ================================================== PERSISTED-STORE PROBE P1 ==
def persisted_key_peak_probe(seed: int, n_lemmas: int = 400) -> Dict[str, object]:
    """GOLD-FREE key-sensitivity probe on the REAL persisted store (READ-ONLY).

    If the shipped store carried a latent role address, unbinding a lemma's accumulated sum by a
    REAL relation key would expose a sharper peak against the symbol codebook than unbinding by a
    RANDOM key of identical geometry. Needs no written-gold, so it is valid on a store whose input
    stream we do not have."""
    z = np.load(REPO / "data" / "foundation" / "reading_grounding_v1" / "concept_space.npz",
                allow_pickle=False)
    lem = [str(x) for x in z["lemmas"]]
    sums = np.asarray(z["sums"], dtype=np.float64)
    d = int(z["d"][0])
    rng = np.random.default_rng(seed * 31337 + 5)
    idx = rng.choice(len(lem), size=min(n_lemmas, len(lem)), replace=False)
    S = _unit(sums[idx])

    real_rels = ["^nsubj", "^obj", "^obl", "nmod", "amod", "obj", "nsubj", "~nsubj:obj"]
    real_keys = np.stack([SYMVEC("REL:" + r, d) for r in real_rels])
    rand_keys = np.stack([SYMVEC("RANDKEY:%d:%d" % (seed, j), d) for j in range(len(real_rels))])
    cb = _unit(np.stack([SYMVEC(x, d) for x in lem]))

    def peak(keys):
        return np.stack([np.max(_unit(S * kk[None, :]) @ cb.T, axis=1) for kk in keys])

    pr, pn = peak(real_keys), peak(rand_keys)
    raw = np.max(_unit(S) @ cb.T, axis=1)
    return {
        "n_lemmas_probed": int(len(idx)), "d": d,
        "real_key_peak_mean": float(pr.mean()),
        "random_key_peak_mean": float(pn.mean()),
        "delta_real_minus_random": float(pr.mean() - pn.mean()),
        "delta_ci95_over_lemmas": [
            float(np.percentile((pr.mean(0) - pn.mean(0))[
                rng.integers(0, len(idx), size=(2000, len(idx)))].mean(1), 2.5)),
            float(np.percentile((pr.mean(0) - pn.mean(0))[
                rng.integers(0, len(idx), size=(2000, len(idx)))].mean(1), 97.5))],
        "no_unbind_peak_mean": float(raw.mean()),
        "real_key_peak_per_rel": {r: float(pr[j].mean()) for j, r in enumerate(real_rels)},
        "store_norm_median": float(np.median(np.linalg.norm(sums, axis=1))),
        "reading": ("a latent role address would make the REAL-key peak exceed the RANDOM-key "
                    "peak; delta ~ 0 means no key was ever applied to this store"),
    }


# =================================================================== SELFTEST =
def selftest() -> List[str]:
    """Properties asserted BEFORE any arm is scored. A failure ABORTS the run."""
    msgs = []

    s = "The heart pumps blood through the arteries of the body."
    words = [x for x in gal.content_words(s) if rgl.normalize_lemma(x) != "heart"]
    acc = np.zeros(D_LIVE)
    for x in words:
        acc += SYMVEC(x, D_LIVE)
    assert np.array_equal(acc, rgl.context_vector_masked(s, "heart")), \
        "T1 FAIL: bag reconstruction is not context_vector_masked"
    msgs.append("T1 PASS bag encoder == rgl.context_vector_masked (byte-identical)")

    enc = rgl.StructuralEncoder(str(REPO), d=D_LIVE)
    feats = enc.features(s, "heart")
    acc2 = np.zeros(D_LIVE)
    for rel, fil in feats:
        acc2 += BIND(SYMVEC("REL:" + rel, D_LIVE), SYMVEC(fil, D_LIVE))
    assert np.array_equal(acc2, enc.vector(s, "heart")), \
        "T2 FAIL: role-bound reconstruction is not StructuralEncoder.vector"
    msgs.append("T2 PASS role-bound encoder == StructuralEncoder.vector (byte-identical)")

    a, b = SYMVEC("t3a", 64), SYMVEC("t3b", 64)
    assert np.array_equal(BIND(BIND(a, b), b), a), "T3 FAIL: bind is not self-inverse"
    msgs.append("T3 PASS bipolar bind/unbind self-inverse")

    rng = np.random.default_rng(0)
    n, d = 4000, 64
    g = rng.choice([-1.0, 1.0], size=(n, F_FACETS, d))
    const = np.repeat(rng.choice([-1.0, 1.0], size=(n, 1, d)), F_FACETS, axis=1)
    MT = np.ones((n, F_FACETS), dtype=bool)
    a4 = score_predictions(predict_from_probes(const, g), MT).mean()
    assert abs(a4 - CHANCE_S3) < 0.02, "T4 FAIL: constant probe scores %.4f not chance" % a4
    msgs.append("T4 PASS constant probe -> %.4f (chance %.4f)" % (a4, CHANCE_S3))

    a5 = score_predictions(predict_from_probes(g, g), MT).mean()
    assert a5 == 1.0, "T5 FAIL: exact probe scores %.4f" % a5
    msgs.append("T5 PASS exact probe -> 1.0000")

    p6 = derangement(F_FACETS, np.random.default_rng(1))
    a6 = score_predictions(predict_from_probes(g[:, p6, :], g), MT).mean()
    assert a6 < 0.02, "T6 FAIL: deranged exact probe scores %.4f, expected ~0" % a6
    msgs.append("T6 PASS deranged exact probe -> %.4f (below chance, as pre-registered)" % a6)

    w7 = build_world_syn(3, 40, T=1, n_extra=0, p_collide=0.0, d=D_LIVE)
    a7 = run_arms(w7, 3, with_factstore=False)
    assert a7["A2R_ROLEBOUND"]["true"].mean() > 0.9, \
        "T7 FAIL: role-bound store at minimum load scores %.4f" \
        % a7["A2R_ROLEBOUND"]["true"].mean()
    msgs.append("T7 PASS role-bound store at minimum load -> %.4f (CAN score high)"
                % a7["A2R_ROLEBOUND"]["true"].mean())

    b8 = a7["A2_BAG"]["true"].mean()
    assert abs(b8 - CHANCE_S3) < 0.10, "T8 FAIL: bag store at min load scores %.4f" % b8
    msgs.append("T8 PASS shipped bag store at minimum load -> %.4f (chance %.4f)"
                % (b8, CHANCE_S3))

    # T9 the LOAD AXIS BITES: the role-bound store must FALL under collision load, or the
    # instrument cannot separate two working stores (the saturation trap).
    w9 = build_world_syn(3, 200, T=32, n_extra=32, p_collide=0.9, d=D_LIVE)
    a9 = run_arms(w9, 3, with_factstore=False)
    r9 = a9["A2R_ROLEBOUND"]["true"].mean()
    s9 = a9["A1_SLOTTED"]["true"].mean()
    assert r9 < 0.9, "T9 FAIL: role-bound store does not degrade under load (%.4f)" % r9
    msgs.append("T9 PASS load axis bites: A2R %.4f vs A1_SLOTTED %.4f at T=32,nx=32,p=0.9"
                % (r9, s9))

    from tools.saturation_negative_control import first_noise_that_moves_it
    nz, r = first_noise_that_moves_it(256, M=400, start=0.1, growth=3.0, max_steps=8)
    assert nz is not None and r < 1.0, "T10 FAIL: saturation helper never moves"
    msgs.append("T10 PASS saturation_negative_control drops below 1.0 at noise=%.3g -> %.4f"
                % (nz, r))

    assert abs(spearman([0, 1, 2, 3, 4, 5], [1.0, .9, .7, .5, .3, .25]) + 1.0) < 1e-9, "T11 FAIL"
    msgs.append("T11 PASS spearman(-monotone) == -1.0")
    return msgs


# ==================================================================== DRIVER ==
def run_seed(seed: int, cfg: dict) -> dict:
    t0 = time.time()
    res: Dict[str, object] = {"seed": seed}

    _HEADLINE_KEY = "T%d_nx%d_c%.2f" % (HEADLINE_T, HEADLINE_NEXTRA, HEADLINE_COLLIDE)
    syn: Dict[str, object] = {}
    infeasible: Dict[str, str] = {}
    syn_n: Dict[str, int] = {}
    for T in cfg["T_GRID"]:
        for nx in cfg["NEXTRA_GRID"]:
            for pc in cfg["COLLIDE_GRID"]:
                w = build_world_syn(seed, cfg["SYN_ITEMS"], T, nx, pc, D_LIVE)
                key = "T%d_nx%d_c%.2f" % (T, nx, pc)
                if w.n == 0:
                    infeasible[key] = ("no item had all %d facet golds written at T=%d, "
                                       "p_collide=%.2f" % (F_FACETS, T, pc))
                    print("[syn] %-18s INFEASIBLE (0 items with all %d golds written)"
                          % (key, F_FACETS), flush=True)
                    continue
                arms = run_arms(w, seed, with_factstore=(key == _HEADLINE_KEY))
                syn[key] = {a: {"true": v["true"].tolist(), "derange": v["derange"].tolist()}
                            for a, v in arms.items()}
                syn_n[key] = w.n
                print("[syn] %-18s A1=%.3f A2R=%.3f A2=%.3f A3R=%.3f A5=%.3f" % (
                    key, arms["A1_SLOTTED"]["true"].mean(), arms["A2R_ROLEBOUND"]["true"].mean(),
                    arms["A2_BAG"]["true"].mean(), arms["A3R_ROLEBOUND_SIGN"]["true"].mean(),
                    arms["A5_NULL_CONTENT"]["true"].mean()), flush=True)
    res["syn"] = syn
    res["infeasible_points"] = infeasible
    res["syn_n"] = syn_n

    res["s1"] = {}
    for M in cfg["S1_M_GRID"]:
        w = build_world_syn(seed, M, cfg["S1_T"], cfg["S1_NEXTRA"], cfg["S1_COLLIDE"], D_LIVE)
        res["s1"]["M%d" % M] = s1_fidelity(w)

    lad: Dict[str, object] = {}
    w_l = build_world_syn(seed, cfg["SYN_ITEMS"], HEADLINE_T, HEADLINE_NEXTRA,
                          HEADLINE_COLLIDE, D_LIVE)
    print("[ladder] world n=%d" % w_l.n, flush=True)
    for sg in NOISE_LADDER:
        arms = run_arms(w_l, seed, noise_sigma=sg, with_factstore=False)
        lad["%.2f" % sg] = {a: float(v["true"].mean()) for a, v in arms.items()}
    res["noise_ladder"] = lad

    live: Dict[str, object] = {}
    live_notes: Dict[str, object] = {}
    T_max = max(cfg["T_GRID"])
    for T in cfg["T_GRID"]:
        w = build_world_live(seed, cfg["LIVE_ITEMS"], T, D_LIVE, cfg["LIVE_SCAN"], T_max)
        if w.n == 0:
            infeasible["LIVE_T%d" % T] = ("no lemma had all %d facet golds written within its "
                                          "first %d occurrences" % (F_FACETS, T))
            print("[live] T=%-3d INFEASIBLE (0 items with all %d golds written)"
                  % (T, F_FACETS), flush=True)
            continue
        arms = run_arms(w, seed)
        live["T%d" % T] = {a: {"true": v["true"].tolist(), "derange": v["derange"].tolist()}
                           for a, v in arms.items()}
        live_notes["T%d" % T] = w.notes
        print("[live] T=%-3d n=%d A1=%.3f A2R=%.3f A2=%.3f A3R=%.3f A5=%.3f A8=%.3f A9=%.3f" % (
            T, w.n, arms["A1_SLOTTED"]["true"].mean(), arms["A2R_ROLEBOUND"]["true"].mean(),
            arms["A2_BAG"]["true"].mean(), arms["A3R_ROLEBOUND_SIGN"]["true"].mean(),
            arms["A5_NULL_CONTENT"]["true"].mean(), arms["A8_ORTHOGRAPHIC"]["true"].mean(),
            arms["A9_FREQUENCY"]["true"].mean()), flush=True)
    res["live"] = live
    res["live_notes"] = live_notes
    res["persisted"] = persisted_key_peak_probe(seed)
    res["elapsed_s"] = time.time() - t0
    return res


def summarise(per_seed: Dict[str, dict], cfg: dict) -> dict:
    rng = np.random.default_rng(20260815)

    def pool(regime: str, point: str):
        out: Dict[str, Dict[str, List[float]]] = {}
        for s in sorted(per_seed):
            blk = per_seed[s].get(regime, {}).get(point)
            if not blk:
                continue
            for arm, v in blk.items():
                o = out.setdefault(arm, {"true": [], "derange": []})
                o["true"].extend(v["true"])
                o["derange"].extend(v["derange"])
        return {a: {k: np.asarray(v) for k, v in d.items()} for a, d in out.items()}

    def stats_for(regime: str, point: str):
        p = pool(regime, point)
        if not p:
            return {}
        n = len(next(iter(p.values()))["true"])
        bi = rng.integers(0, n, size=(N_BOOT, n))
        out = {}
        for arm, d in p.items():
            m, lo, hi = bootstrap_ci(d["true"], bi)
            dm, dlo, dhi = bootstrap_ci(d["derange"], bi)
            km, klo, khi = bootstrap_ci(d["true"] - d["derange"], bi)
            out[arm] = {"s3": m, "s3_ci": [lo, hi], "s3_deranged": dm,
                        "s3_deranged_ci": [dlo, dhi], "delta_key": km,
                        "delta_key_ci": [klo, khi], "n_items": n}
        return out

    syn_points = sorted(set().union(*[set(per_seed[s]["syn"]) for s in per_seed]))
    live_points = sorted(set().union(*[set(per_seed[s]["live"]) for s in per_seed]),
                         key=lambda p: int(p[1:]))
    syn_stats_all = {pt: stats_for("syn", pt) for pt in syn_points}
    live_stats_all = {pt: stats_for("live", pt) for pt in live_points}

    def _n(v):
        return next(iter(v.values()))["n_items"] if v else 0

    # GATES are evaluated only on points with adequate power (see MIN_ITEMS_FOR_GATE). Every
    # point is REPORTED either way, with its n and, where relevant, why it is infeasible.
    syn_stats = {pt: v for pt, v in syn_stats_all.items() if _n(v) >= MIN_ITEMS_FOR_GATE}
    live_stats = {pt: v for pt, v in live_stats_all.items() if _n(v) >= MIN_ITEMS_FOR_GATE}
    ungated = {("SYN:" + pt): _n(v) for pt, v in syn_stats_all.items()
               if _n(v) < MIN_ITEMS_FOR_GATE}
    ungated.update({("LIVE:" + pt): _n(v) for pt, v in live_stats_all.items()
                    if _n(v) < MIN_ITEMS_FOR_GATE})
    syn_points = sorted(syn_stats)
    live_points = sorted(live_stats, key=lambda p: int(p[1:]))

    gates: List[dict] = []
    notes: List[str] = []
    if ungated:
        notes.append("POINTS REPORTED BUT NOT GATED (n < %d): %s"
                     % (MIN_ITEMS_FOR_GATE, ungated))

    def rng_over(stats, arm, field="s3"):
        vals = [v[arm][field] for v in stats.values() if arm in v]
        return (min(vals), max(vals)) if vals else (float("nan"), float("nan"))

    o_lo = min(rng_over(syn_stats, "A0_ORACLE_DICT")[0], rng_over(live_stats, "A0_ORACLE_DICT")[0])
    gates.append(record_gate("IV1_oracle_ceiling", o_lo, 0.99, ">=",
                             "A0_ORACLE_DICT S3 minimum over every operating point, both regimes"))

    heavy_syn = "T%d_nx%d_c%.2f" % (max(cfg["T_GRID"]), max(cfg["NEXTRA_GRID"]), 0.0)
    heavy_live = "T%d" % max(cfg["T_GRID"])
    hv = syn_stats.get(heavy_syn, {}).get("A1_SLOTTED", {}).get("s3", float("nan"))
    gates.append(record_gate("IV2_slotted_at_max_load", hv, 0.95, ">=",
                             "A1_SLOTTED at the heaviest NON-COLLIDING point %s; the colliding "
                             "points are the load axis, where every architecture must degrade"
                             % heavy_syn))

    worst = 0.0
    covers = []
    for st in (syn_stats, live_stats):
        for pt, v in st.items():
            if "A5_NULL_CONTENT" in v:
                worst = max(worst, abs(v["A5_NULL_CONTENT"]["s3"] - CHANCE_S3))
                lo, hi = v["A5_NULL_CONTENT"]["s3_ci"]
                covers.append(1.0 if lo <= CHANCE_S3 <= hi else 0.0)
    gates.append(record_gate("IV3a_null_near_chance", worst, 0.05, "<=",
                             "max |A5_NULL_CONTENT - chance| over every point, both regimes"))
    gates.append(record_gate("IV3b_null_ci_covers_chance", float(np.mean(covers or [0.0])), 1.0,
                             ">=", "fraction of points whose A5 95pct CI covers chance"))

    lad_all: Dict[str, List[float]] = {}
    for s in sorted(per_seed):
        for sg, d in per_seed[s]["noise_ladder"].items():
            lad_all.setdefault(sg, []).append(d.get("A1_SLOTTED", float("nan")))
    sgs = sorted(lad_all, key=float)
    lad_mean = [float(np.mean(lad_all[s])) for s in sgs]
    gates.append(record_gate("IV4a_saturation_monotone",
                             spearman([float(s) for s in sgs], lad_mean), -0.8, "<=",
                             "Spearman rho of A1_SLOTTED S3 vs store-noise sigma, 6 levels"))
    gates.append(record_gate("IV4b_saturation_reaches_chance",
                             lad_mean[-1] if lad_mean else 1.0, CHANCE_S3 + 0.10, "<=",
                             "A1_SLOTTED S3 at the top noise level"))

    f_worst = 0.0
    for arm in ("A8_ORTHOGRAPHIC", "A9_FREQUENCY"):
        lo, hi = rng_over(live_stats, arm)
        f_worst = max(f_worst, abs(lo - CHANCE_S3), abs(hi - CHANCE_S3))
    gates.append(record_gate("IV5_live_floors_at_chance", f_worst, 0.05, "<=",
                             "max |floor - chance| over A8_ORTHOGRAPHIC and A9_FREQUENCY"))

    d_worst = 0.0
    for st in (syn_stats, live_stats):
        for pt, v in st.items():
            for arm in ("A0_ORACLE_DICT", "A1_SLOTTED"):
                if arm in v:
                    d_worst = max(d_worst, v[arm]["s3_deranged"])
    gates.append(record_gate("IV6_null_key_collapses_A0_A1", d_worst, CHANCE_S3 + 0.05, "<=",
                             "worst deranged-key S3 over A0/A1, every point, both regimes"))

    u = max(abs(x - CHANCE_S3) for x in
            list(rng_over(syn_stats, "A2U_BAG_UNKEYED")) + list(rng_over(live_stats,
                                                                        "A2U_BAG_UNKEYED")))
    gates.append(record_gate("IV7_unkeyed_pool_balanced", u, 0.05, "<=",
                             "max |A2U_BAG_UNKEYED - chance| over every point"))

    def spread_at(stats, pt):
        v = stats.get(pt, {})
        vals = [v[a]["s3"] for a in ("A1_SLOTTED", "A2R_ROLEBOUND", "A2_BAG") if a in v]
        return (max(vals) - min(vals)) if len(vals) == 3 else float("nan")

    def sep_at(stats, pt):
        """The saturation trap the brief names: can the metric separate TWO WORKING stores?"""
        v = stats.get(pt, {})
        if "A1_SLOTTED" in v and "A2R_ROLEBOUND" in v:
            return v["A1_SLOTTED"]["s3"] - v["A2R_ROLEBOUND"]["s3"]
        return float("nan")

    hp_syn = "T%d_nx%d_c%.2f" % (HEADLINE_T, HEADLINE_NEXTRA, HEADLINE_COLLIDE)
    if hp_syn not in syn_stats:
        hp_syn = syn_points[-1]
    sp = spread_at(syn_stats, hp_syn)
    moved = False
    if not (sp >= 0.10):
        best = max(syn_points, key=lambda p: spread_at(syn_stats, p))
        if spread_at(syn_stats, best) >= 0.10:
            hp_syn, sp, moved = best, spread_at(syn_stats, best), True
    gates.append(record_gate("IV8_arm_spread_at_headline", sp, 0.10, ">=",
                             "max-min S3 over {A1_SLOTTED, A2R_ROLEBOUND, A2_BAG} at %s%s"
                             % (hp_syn, " (MOVED)" if moved else "")))

    two_working = {pt: sep_at(syn_stats, pt) for pt in syn_points}
    best_sep_pt = max(two_working, key=lambda p: two_working[p])
    gates.append(record_gate("IV8b_two_working_stores_separable",
                             float(two_working[best_sep_pt]), 0.05, ">=",
                             "best A1_SLOTTED - A2R_ROLEBOUND gap over the grid, at %s. A metric "
                             "that cannot separate two WORKING stores separates only broken from "
                             "working." % best_sep_pt))

    hp_live = ("T%d" % HEADLINE_T) if ("T%d" % HEADLINE_T) in live_stats else live_points[-1]
    iv_pass = all(g["gate_verdict"] for g in gates)

    def floors_at(stats, pt):
        v = stats.get(pt, {})
        c = [a for a in ("A5_NULL_CONTENT", "A7_SCRAMBLE", "A8_ORTHOGRAPHIC", "A9_FREQUENCY")
             if a in v]
        if not c:
            return None, None, None
        b = max(c, key=lambda a: v[a]["s3"])
        return b, v[b]["s3"], v[b]["s3_ci"][1]

    verdicts: Dict[str, dict] = {}
    if iv_pass:
        for label, stats, pt in (("SYN", syn_stats, hp_syn), ("LIVE", live_stats, hp_live)):
            fname, fval, fhi = floors_at(stats, pt)
            for arm, v in sorted(stats.get(pt, {}).items()):
                if arm.startswith(("A5", "A7", "A8", "A9", "A0")):
                    continue
                lo, hi = v["s3_ci"]
                klo, khi = v["delta_key_ci"]
                if lo > fhi and v["delta_key"] >= 0.15 and klo > 0:
                    verd = "ADDRESSED"
                elif hi < fhi + 0.05 and klo <= 0 <= khi:
                    verd = "FLAT"
                else:
                    verd = "PARTIAL"
                verdicts["%s@%s:%s" % (label, pt, arm)] = {
                    "verdict": verd, "s3": v["s3"], "s3_ci": v["s3_ci"],
                    "delta_key": v["delta_key"], "delta_key_ci": v["delta_key_ci"],
                    "max_floor": fname, "max_floor_s3": fval, "max_floor_ci_hi": fhi}
    else:
        notes.append("INSTRUMENT_STILL_LOOSE: no storage-quality number is published.")

    lad_by_arm: Dict[str, Dict[str, float]] = {}
    for sg in sgs:
        arms0 = per_seed[sorted(per_seed)[0]]["noise_ladder"][sg]
        lad_by_arm[sg] = {a: float(np.mean([per_seed[s]["noise_ladder"][sg][a]
                                            for s in sorted(per_seed)])) for a in arms0}

    return {"gates": gates, "iv_pass": iv_pass, "syn": syn_stats_all, "live": live_stats_all,
            "gated_syn_points": syn_points, "gated_live_points": live_points,
            "ungated_points_n": ungated,
            "infeasible_points": {s: per_seed[s].get("infeasible_points", {})
                                  for s in sorted(per_seed)},
            "noise_ladder": lad_by_arm, "headline_point_syn": hp_syn,
            "headline_point_live": hp_live, "headline_moved_by_IV8": moved,
            "two_working_separation_by_point": two_working,
            "verdicts": verdicts,
            "persisted": {s: per_seed[s]["persisted"] for s in sorted(per_seed)},
            "s1": {s: per_seed[s]["s1"] for s in sorted(per_seed)},
            "live_notes": {s: per_seed[s]["live_notes"] for s in sorted(per_seed)},
            "notes": notes}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else
                                                   ("full" if args.full else "self_test"))
    print("=== exp_%s  run_mode=%s ===" % (ANCHOR_NAME, run_mode), flush=True)

    t0 = time.time()
    msgs = selftest()
    for m in msgs:
        print("  " + m, flush=True)
    print("SELF-TEST: %d/%d PASS (%.1fs)" % (len(msgs), len(msgs), time.time() - t0), flush=True)
    if run_mode == "self_test":
        return

    smoke = run_mode == "smoke"
    cfg = {
        "run_mode": run_mode, "F": F_FACETS, "D": D_LIVE, "N_BOOT": N_BOOT,
        "T_GRID": T_GRID_SMOKE if smoke else T_GRID_FULL,
        "NEXTRA_GRID": NEXTRA_GRID_SMOKE if smoke else NEXTRA_GRID_FULL,
        "COLLIDE_GRID": COLLIDE_GRID_SMOKE if smoke else COLLIDE_GRID_FULL,
        "SYN_ITEMS": SYN_ITEMS_SMOKE if smoke else SYN_ITEMS_FULL,
        "LIVE_ITEMS": LIVE_ITEMS_SMOKE if smoke else LIVE_ITEMS_FULL,
        "LIVE_SCAN": LIVE_SCAN_LINES_SMOKE if smoke else LIVE_SCAN_LINES_FULL,
        "S1_M_GRID": [16, 64, 256] if smoke else [16, 64, 256, 1024],
        "S1_T": 4, "S1_NEXTRA": 4, "S1_COLLIDE": 0.5,
        "NOISE_LADDER": NOISE_LADDER, "FREQ_RATIO_MAX": FREQ_RATIO_MAX,
        "HEADLINE_T": HEADLINE_T, "HEADLINE_NEXTRA": HEADLINE_NEXTRA,
        "HEADLINE_COLLIDE": HEADLINE_COLLIDE, "anchor": ANCHOR_NAME,
    }
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if smoke else ""))
    out_dir.mkdir(parents=True, exist_ok=True)

    done, remaining = resumable_seeds_config(seeds, out_dir, cfg)
    print("[ckpt] %d of %d seeds complete; running %s" % (len(done), len(seeds), remaining),
          flush=True)
    for sd in remaining:
        r = run_seed(sd, cfg)
        write_partial_config(out_dir, sd, r, cfg)
        print("[seed %d] done in %.1fs" % (sd, r["elapsed_s"]), flush=True)

    per_seed = aggregate_partials_config(out_dir, seeds, cfg)
    summary = summarise(per_seed, cfg)
    gates = summary["gates"]
    n_pass = sum(1 for g in gates if g["gate_verdict"])

    if summary["iv_pass"]:
        hp, hl = summary["headline_point_syn"], summary["headline_point_live"]
        v, vl = summary["syn"][hp], summary["live"][hl]
        verdict = "INSTRUMENT_VALIDATED"
        msg = ("INSTRUMENT_VALIDATED %d/%d gates. SYN@%s A1_SLOTTED %.4f / A2R_ROLEBOUND %.4f / "
               "A2_BAG %.4f (chance %.4f); delta_key A1 %.4f / A2R %.4f / A2_BAG %.4f. "
               "LIVE@%s A1 %.4f / A2R %.4f / A2_BAG %.4f, floors A8 %.4f A9 %.4f."
               % (n_pass, len(gates), hp, v["A1_SLOTTED"]["s3"], v["A2R_ROLEBOUND"]["s3"],
                  v["A2_BAG"]["s3"], CHANCE_S3, v["A1_SLOTTED"]["delta_key"],
                  v["A2R_ROLEBOUND"]["delta_key"], v["A2_BAG"]["delta_key"], hl,
                  vl["A1_SLOTTED"]["s3"], vl["A2R_ROLEBOUND"]["s3"], vl["A2_BAG"]["s3"],
                  vl["A8_ORTHOGRAPHIC"]["s3"], vl["A9_FREQUENCY"]["s3"]))
    else:
        verdict = "INSTRUMENT_STILL_LOOSE"
        failed = [g["gate_name"] for g in gates if not g["gate_verdict"]]
        msg = ("INSTRUMENT_STILL_LOOSE: %d/%d gates passed; FAILED %s. NO storage-quality number "
               "is published." % (n_pass, len(gates), failed))
    print(msg, flush=True)

    write_metrics(out_dir,
                  {"verdict": verdict, "verdict_msg": msg, "anchor": ANCHOR_NAME, "config": cfg,
                   "chance_s3": CHANCE_S3, "seeds": seeds, "summary_stats": summary,
                   "prereg": "preregs/exp_storage_quality_instrument_v1.md"},
                  results=[{"elapsed_s": per_seed[s].get("elapsed_s", 0.0)} for s in per_seed],
                  gate_claims=gates)
    print("wrote %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
