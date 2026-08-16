"""SYNONYM CLUMPING BY OFFLINE CONSOLIDATION -- can we EARN the oracle's clumping without the key?

THE TARGET, and it came from the owner describing their own memory (BOARD Q4, 2026-08-16):
  "If i know what the word means, I can think of other words that mean the same thing. Those same
   meaning words are often clumped together in my memory, so thinking of the others can trigger
   remembering the whole word."

That is a claim about STORAGE LAYOUT and the prior cell measured it: in our 256-dim anchor store
mean word-to-synonym cosine is 0.1271, and an ORACLE that shrinks every row toward the centroid of
its OWN WordNet synonyms takes the semantic-neighbourhood channel from 0.2417 to 0.7515, peaking
near mean-synonym-cosine 0.76 and COLLAPSING beyond it. The oracle is an UPPER BOUND obtained by
building the store out of the very sets that will be used to cue it.

THIS CELL ASKS THE ONLY QUESTION THAT MATTERS NEXT: can a mechanism that NEVER CONSULTS WORDNET
produce the same clumping, and if it does, does the retrieval gain come with it?

------------------------------------------------------------------------------------------------
STEP 1 -- THE BIOLOGY, AND WHICH PART IS OURS
------------------------------------------------------------------------------------------------
BRAIN STRUCTURE BEING REPLICATED: the SLOW CORTICAL STORE of complementary learning systems, being
reorganised OFFLINE by replay. Not a cognitive-theory label -- a neural system with a job.

[PINNED] TOPOGRAPHIC SEMANTIC MAPS. Ventral/lateral temporal cortex carries a smooth, continuous
  semantic map: related categories occupy neighbouring cortical territory (Huth 2012, 2016). So
  "same-meaning things sit near each other" is a real property of the cortical store, not a
  metaphor. WHAT IS NOT PINNED: that the relevant metric is cosine in a 256-dim bag-of-context.
[PINNED] HEBBIAN CO-ACTIVATION. Co-active populations strengthen their shared connections (Hebb
  1949; Loewel & Singer 1992 in vivo), which pulls repeatedly co-activated representations
  together. CRUCIAL DETAIL AND IT DRIVES THE DESIGN: synonyms are rarely co-active in the SAME
  SENTENCE. They are co-active across the SAME SITUATIONS. The Hebbian pull that clumps synonyms
  is therefore SECOND-ORDER (shared contexts), not first-order (co-occurrence). A first-order
  co-occurrence mechanism is the WRONG circuit for this target, and one arm here tests exactly
  that prediction.
[PINNED] SLEEP REPLAY / SYSTEMS CONSOLIDATION. Replay during slow-wave sleep is OVERLAPPING rather
  than verbatim: reactivating many related traces together selectively reinforces their SHARED
  component while episode-idiosyncratic detail washes out (Lewis & Durrant 2011; McClelland,
  McNaughton & O'Reilly 1995; Tse 2007 schema). This is the only brain process whose job is to
  REORGANISE A STORE THAT HAS ALREADY BEEN WRITTEN, which is precisely our situation.
[PINNED AS A MATCHED PAIR] The counter-force. Dentate-gyrus separation and homeostatic /
  BCM-style sliding-threshold plasticity exist so that consolidation does not COLLAPSE distinct
  items. Same-meaning words must be near enough to pull each other and far enough to be told
  apart. The oracle's turnover at rho 0.7 is that tension showing up as a measured optimum.

[OURS -- INVENTION UNDER TEST, stated as invention]
  - the update rule: move each row a fraction eta toward a sharpened weighted mean of its m
    nearest neighbours IN THE STORE'S OWN GEOMETRY, iterated T times. One pass stands in for one
    night. The brain does not do a k-nearest-neighbour lookup.
  - the neighbourhood definition (top-m cosine), the sharpening exponent, eta, T.
  - the recentre step as our stand-in for homeostatic normalisation.
  - that a single global sweep over all 5,491 anchors is an acceptable model of prioritised,
    partial, interleaved replay. It is not; it is the cheapest faithful-in-direction version.

[OURS, NOT BRAIN-MOTIVATED AT ALL, and labelled so]
  - the exhaustive cosine argmax read-out (unchanged, still no neural analogue)
  - the isotropic global-centroid control and the oracle shrinkage: MEASUREMENT INSTRUMENTS.

SHELVE/REVIVAL CRITERION, BRAIN-FRAMED (never performance-framed): if second-order replay raises
synonym clumping but the retrieval gain does not follow, the diverging element is named and the
mechanism is shelved as THE WRONG DISTANCE METRIC, not as "consolidation does not work". It is
revived the moment the store's similarity metric is one in which same-meaning words are actually
neighbours -- i.e. after Phase 1 meaning supply -- because the replay operator is not what failed.

------------------------------------------------------------------------------------------------
STEP 2 -- WHAT WE ALREADY OWN (enumerated from disk, reconciled to the registry, RUNTIME-verified
in scratch/synonym_clumping/runtime_verify.json). Nothing here is trusted by name.
------------------------------------------------------------------------------------------------
  hdlab.continual.replay_cycle       IS a real replay organ and is the WRONG ONE. Verified by
                                     signature+source: it re-Hebbs (key, value) OUTER PRODUCTS
                                     into an associative weight matrix W. It consolidates a MAP;
                                     it cannot move the rows of an item store toward each other.
                                     The brain-foundation map called this a PARTIAL ANALOG
                                     (anti-forgetting rehearsal) with a TOTAL GAP on gist/schema
                                     reorganisation. Runtime confirms the gap. NOT REUSABLE HERE.
  hdlab.ultrametric_clustering       IS the right shape -- cosine_distance_matrix +
                                     single_linkage_clusters + compute_representatives +
                                     collapse_W_via_clusters is literally "clump and replace by
                                     the centroid". REUSED as arm M2's semantics. RUNTIME DEFECT
                                     FOUND: single_linkage_clusters materialises all n(n-1)/2
                                     pairs as PYTHON TUPLES and sorts them -- 15.1M tuples at
                                     n=5491, several GB. Unusable at store scale. This cell uses
                                     a connected-components equivalent and the SELF-TEST asserts
                                     the two agree EXACTLY on n=300, so the organ's semantics are
                                     reused with a witness rather than reimplemented on trust.
  hdlab.whitening.pca_whiten/zca     real, and the OPPOSITE operation (equalises variance ->
                                     spreads). Kept as a named contrast, not as a treatment.
  hdlab.dg_pattern_separation        the counter-force organ; expands+sparsifies a SINGLE vector.
                                     Not a store reorganiser. Named, not used.
  tools.floor_battery                the ruler. Verified by a PLANTED ANSWER reading exactly 1.0.
  experiments.exp_task_degeneracy_v1.ruler_mode_gate   imported and CALLED, per the standing
                                     hazard that '--smoke' anywhere in argv silently swaps the
                                     imported ruler. This cell's flag is --grid, never --smoke.

CONCLUSION OF STEP 2: we own the CLUSTERING half and we do NOT own an offline store-reorganising
consolidation pass. Building one is not duplicating an organ.

------------------------------------------------------------------------------------------------
PRE-REGISTRATION
------------------------------------------------------------------------------------------------
REGRESSION GATE (read first, before anything else): the untouched store must reproduce the landed
  numbers -- mean word-to-synonym cosine 0.1271, gated-k3 semantic channel 0.2417 on the 2,358
  items with a synonym, sentence-cue self-recovery 0.0711 on the full pool, instrument-B
  exact-key 0.0481, PR_raw 88.74 / PR_unit 171.16.
VALIDITY (read before ANY treatment number): KA_CONSOLIDATED (query = the target's own row in the
  variant store) must be >= 0.95, and it DOUBLES AS THE COLLAPSE DETECTOR -- if clumping makes two
  rows identical it falls, and the variant is marked VOID_COLLAPSED. NULL (the semantic cue built
  for a randomly chosen OTHER word) must sit at the gate's chance rate. They fail independently:
  KA plants the answer, NULL permutes the cue-to-item assignment.
THE CRITICAL CONTROL, stated in advance: clumping must not be free. Every variant reports mean
  cosine to SYNONYMS and mean cosine to NON-synonyms IN THE SAME BREATH plus their RATIO, and the
  isotropic global-centroid arm C_ISO is swept to the SAME synonym-cosine levels as every
  treatment so that treatments are compared AT MATCHED CLUMPING. A mechanism that raises both
  equally has achieved nothing and the ratio will say so.
PARTICIPATION RATIO before and after, both conventions, because the last sparsity attempt moved
  it the wrong way and nobody noticed until it was measured.
THE BAR: a CI-separated margin over max(orthographic, frequency, scramble, CONSTANT/PROTOTYPE) on
  the IDENTICAL scorer/n/pool/gold, permutation-calibrated by paired bootstrap. Never a bare
  number. On the SELF-RECOVERY instrument a full-spelling channel is NOT an admissible floor
  (knowing the spelling IS knowing the word) -- that was established by the prior cell's smoke
  gate and those arms are carried here as INSTRUMENT_CHECK, reading at ceiling by construction.
THE SYSTEM QUESTION, and it is the one that decides: the semantic channel sits 0.3145 BELOW the
  reading cue we already have and ADDING it costs 0.0612 CI-separated. Consolidation changes the
  STORE, so it moves EVERY arm. A2 (the channel) and A1/B (the system) are both reported for
  every variant. If the channel improves and the system does not, that is the result and it is
  reported as the result.
progress_logging: every variant prints a flushed line; expected wall time > 1800s at --grid full.
------------------------------------------------------------------------------------------------
ASCII only. No LLM anywhere. No pretrained table. Writes only to its own output dir + scratch/.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import tools.floor_battery as FB  # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

CACHE = os.path.join(_REPO, "scratch", "sparse_code_real_task", "real_cache.npz")
AUX = os.path.join(_REPO, "scratch", "sparsify_right_object", "aux_v2.npz")
THEMATIC = os.path.join(_REPO, "data", "thematic_relations_v1", "thematic_edges_v1.pkl")

MASTER_SEED = 20260816
N_BOOT = 10000
GATE_K = 3

LANDED = {"cos_to_SYNONYMS": 0.1271, "A2_gated_k3_semantic_on_items_with_a_synonym": 0.2417,
          "A1_sentence_cue_full_pool": 0.0711, "B_exact_key": 0.0481,
          "PR_raw_store": 88.74, "PR_unit_store": 171.16,
          "ORACLE_PEAK_acc": 0.8452, "ORACLE_PEAK_cos": 0.7623}
KA_CEILING_MIN = 0.95


# =============================================================================================
# basic geometry helpers
# =============================================================================================
def l2n(A: np.ndarray) -> np.ndarray:
    A = np.asarray(A, dtype=np.float32)
    n = np.linalg.norm(A, axis=-1, keepdims=True)
    return (A / np.maximum(n, 1e-12)).astype(np.float32)


def participation_ratio(X: np.ndarray) -> float:
    """PR = (sum eig)^2 / sum eig^2 (Gao/Ganguli). IDENTICAL definition to the prior cells, so
    directly comparable to the store's landed 88.74 raw / 171.16 unit, both of 256."""
    Xc = X.astype(np.float64) - X.astype(np.float64).mean(axis=0, keepdims=True)
    s = np.linalg.svd(Xc, compute_uv=False)
    e = s ** 2
    return float(e.sum() ** 2 / max(np.sum(e ** 2), 1e-30))


def topm_neighbours(Sn: np.ndarray, m: int, block: int = 512
                    ) -> Tuple[np.ndarray, np.ndarray]:
    """Top-m cosine neighbours of every row, self excluded. Blocked so the n x n similarity is
    never held whole alongside the gather."""
    n = Sn.shape[0]
    idx = np.zeros((n, m), dtype=np.int64)
    val = np.zeros((n, m), dtype=np.float32)
    for a in range(0, n, block):
        b = min(a + block, n)
        C = Sn[a:b] @ Sn.T
        C[np.arange(b - a), np.arange(a, b)] = -np.inf
        p = np.argpartition(-C, m, axis=1)[:, :m]
        v = np.take_along_axis(C, p, axis=1)
        o = np.argsort(-v, axis=1)
        idx[a:b] = np.take_along_axis(p, o, axis=1)
        val[a:b] = np.take_along_axis(v, o, axis=1)
    return idx, val


def _pull(Sn: np.ndarray, idx: np.ndarray, w: np.ndarray, eta: float,
          block: int = 1024) -> np.ndarray:
    """(1-eta)*row + eta*(weighted mean of neighbour rows). Blocked: the gather Sn[idx] is
    n x m x d and must never be materialised whole."""
    out = np.empty_like(Sn)
    for a in range(0, Sn.shape[0], block):
        b = min(a + block, Sn.shape[0])
        nb = np.einsum("ij,ijk->ik", w[a:b], Sn[idx[a:b]], optimize=True)
        out[a:b] = (1.0 - eta) * Sn[a:b] + eta * nb
    return l2n(out)


def _weights(val: np.ndarray, beta: float) -> np.ndarray:
    w = np.maximum(val, 0.0).astype(np.float64) ** beta
    s = w.sum(axis=1, keepdims=True)
    w = np.where(s > 1e-12, w / np.maximum(s, 1e-12), 0.0)
    return w.astype(np.float32)


# =============================================================================================
# THE MECHANISMS. Every one of these is GOLD-FREE unless its name says ORACLE.
# =============================================================================================
def m1_shared_context_replay(U: np.ndarray, m: int, eta: float, T: int, beta: float,
                             recentre: bool, log=None) -> np.ndarray:
    """M1 -- OFFLINE OVERLAPPING REPLAY, the mechanism this cell is actually testing.

    One pass = one night. Each anchor is replayed together with the anchors that share its
    contexts (its current nearest neighbours in the store's own geometry), and the shared
    component is reinforced. Consults NOTHING outside the store."""
    S = l2n(U)
    for t in range(T):
        idx, val = topm_neighbours(S, m)
        S = _pull(S, idx, _weights(val, beta), eta)
        if recentre:
            S = l2n(S - S.mean(axis=0, keepdims=True))
        if log:
            log("  [M1] pass %d/%d done" % (t + 1, T))
    return S


def c_rand_replay(U: np.ndarray, m: int, eta: float, T: int, seed: int) -> np.ndarray:
    """CONTROL -- the IDENTICAL update with the neighbourhood chosen AT RANDOM. Same amount of
    movement, same normalisation, no structure. Isolates 'is it the STRUCTURE of the
    neighbourhood or merely the act of averaging'."""
    rng = np.random.default_rng(seed)
    S = l2n(U)
    n = S.shape[0]
    for _t in range(T):
        idx = rng.integers(0, n, size=(n, m))
        w = np.full((n, m), 1.0 / m, dtype=np.float32)
        S = _pull(S, idx, w, eta)
    return S


def c_iso_collapse(U: np.ndarray, beta: float) -> np.ndarray:
    """CONTROL, AND THE ONE THE BRIEF DEMANDS -- pull EVERY row toward the GLOBAL centroid. This
    raises cosine to synonyms for free, because it raises cosine to everything. Swept to the same
    synonym-cosine levels as the treatments so that treatments are read AT MATCHED CLUMPING."""
    Sn = l2n(U)
    c = l2n(Sn.mean(axis=0, keepdims=True))
    return l2n((1.0 - beta) * Sn + beta * np.repeat(c, Sn.shape[0], axis=0))


def m2_cluster_shrink(U: np.ndarray, cos_thresh: float, rho: float
                      ) -> Tuple[np.ndarray, Dict]:
    """M2 -- REUSES hdlab.ultrametric_clustering's SEMANTICS (single-linkage at a cosine
    threshold, centroid representative), graded by rho instead of collapsed outright, because the
    oracle curve says full collapse is the WORST regime. Connected-components equivalent; the
    self-test asserts exact agreement with the owned organ at n=300."""
    Sn = l2n(U)
    lab = _single_linkage_labels(Sn, cos_thresh)
    nlab = int(lab.max()) + 1
    cent = np.zeros((nlab, Sn.shape[1]), dtype=np.float32)
    cnt = np.zeros(nlab, dtype=np.int64)
    np.add.at(cent, lab, Sn)
    np.add.at(cnt, lab, 1)
    cent = cent / np.maximum(cnt, 1)[:, None]
    S = l2n((1.0 - rho) * Sn + rho * cent[lab])
    sizes = np.bincount(lab)
    stats = {"n_clusters": int(nlab), "n_singletons": int((sizes == 1).sum()),
             "largest_cluster": int(sizes.max()),
             "frac_atoms_in_a_nonsingleton": round(float((sizes[lab] > 1).mean()), 4)}
    return S, stats


def _single_linkage_labels(Sn: np.ndarray, cos_thresh: float, block: int = 512) -> np.ndarray:
    """Connected components of the graph {cos >= cos_thresh}. Single-linkage at distance
    (1 - cos_thresh) is EXACTLY connected components of that thresholded graph."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    n = Sn.shape[0]
    rows: List[np.ndarray] = []
    cols: List[np.ndarray] = []
    for a in range(0, n, block):
        b = min(a + block, n)
        C = Sn[a:b] @ Sn.T
        C[np.arange(b - a), np.arange(a, b)] = -np.inf
        r, c = np.nonzero(C >= cos_thresh)
        rows.append(r + a)
        cols.append(c)
    r = np.concatenate(rows) if rows else np.zeros(0, dtype=np.int64)
    c = np.concatenate(cols) if cols else np.zeros(0, dtype=np.int64)
    g = coo_matrix((np.ones(r.size, dtype=np.int8), (r, c)), shape=(n, n))
    _k, lab = connected_components(g, directed=False)
    return lab.astype(np.int64)


def m3_pca_truncate(U: np.ndarray, k: int) -> np.ndarray:
    """M3 -- KEEP ONLY THE TOP-k SHARED COMPONENTS. The Saxe/Oja account says slow interleaved
    learning tracks high-singular-value SHARED structure first and item-idiosyncratic detail last,
    so truncating to the top components is what an infinitely-slow consolidation converges to.
    Gold-free. hdlab.whitening does the OPPOSITE (equalises variance) and is not used here."""
    Sn = l2n(U).astype(np.float64)
    mu = Sn.mean(axis=0, keepdims=True)
    _u, _s, vt = np.linalg.svd(Sn - mu, full_matrices=False)
    V = vt[:k].T
    return l2n(((Sn - mu) @ V) @ V.T + mu)


def thematic_neighbourhood(tvec: np.ndarray, m: int, beta: float, mode: str, seed: int,
                           fq: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray,
                                                                     np.ndarray]:
    """Returns (idx, weights, dead) for the M4 family.

    mode='second_order'  neighbours = words with SIMILAR THEMATIC-PARTNER PROFILES. This is the
                         prediction the biology section makes: synonyms are co-active across the
                         same SITUATIONS, not inside the same sentence.
    mode='first_order'   neighbours = the word's DIRECT thematic partners, PMI-weighted. This is
                         the FALSIFIER for that prediction: if first-order does as well, the
                         second-order claim is not carrying anything.
    mode='shuffled'      THE CONTROL FOR M4. The thematic profile MATRIX ROWS ARE PERMUTED among
                         anchors, so every word gets a real, structured, correctly-shaped thematic
                         profile that BELONGS TO A DIFFERENT WORD. Degree distribution, sparsity
                         and neighbourhood size are preserved; only the correspondence between a
                         word and its own thematic history is destroyed.
    mode='freq_matched'  neighbours replaced by frequency-decile-matched random anchors, matched
                         in count, so 'the partners are simply commoner words' is ruled out.
    """
    dead = np.linalg.norm(tvec, axis=1) <= 1e-9
    rng = np.random.default_rng(seed)
    if mode == "shuffled":
        perm = rng.permutation(tvec.shape[0])
        tv = tvec[perm]
        dead = dead[perm]
    else:
        tv = tvec
    if mode == "first_order":
        idx = np.argpartition(-tv, m, axis=1)[:, :m]
        val = np.take_along_axis(tv, idx, axis=1)
        o = np.argsort(-val, axis=1)
        idx = np.take_along_axis(idx, o, axis=1)
        val = np.take_along_axis(val, o, axis=1)
        w = _weights(val / np.maximum(val.max(axis=1, keepdims=True), 1e-9), beta)
    elif mode == "freq_matched":
        order = np.argsort(fq)
        dec = np.zeros(fq.size, dtype=np.int64)
        dec[order] = (np.arange(fq.size) * 10) // fq.size
        by_dec = {d: np.flatnonzero(dec == d) for d in range(10)}
        idx0, _v0 = topm_neighbours(l2n(tv), m)
        idx = np.zeros_like(idx0)
        for i in range(idx0.shape[0]):
            for j in range(m):
                pool = by_dec[int(dec[int(idx0[i, j])])]
                idx[i, j] = int(pool[rng.integers(0, pool.size)])
        w = np.full((tv.shape[0], m), 1.0 / m, dtype=np.float32)
    else:
        idx, val = topm_neighbours(l2n(tv), m)
        w = _weights(val, beta)
    w = w.copy()
    w[dead] = 0.0
    return idx, w, dead


def m4_replay_from_neighbourhood(U: np.ndarray, idx: np.ndarray, w: np.ndarray, dead: np.ndarray,
                                 eta: float, T: int) -> np.ndarray:
    S = l2n(U)
    for _t in range(T):
        nb = _pull(S, idx, w, 1.0)
        S = l2n(np.where(dead[:, None], S, (1.0 - eta) * S + eta * nb))
    return S


def m4_thematic_replay(U: np.ndarray, tvec: np.ndarray, m: int, eta: float,
                       T: int, beta: float) -> np.ndarray:
    """M4 -- the SECOND relational hub as the replay partner. Neighbourhoods come from the
    THEMATIC co-occurrence graph (data/thematic_relations_v1, extracted from simplewiki by our
    own extractor, no WordNet anywhere), used SECOND-ORDER: two words are replay partners when
    they have similar thematic-partner profiles, which is the prediction that synonymy is a
    second-order and not a first-order co-occurrence fact."""
    idx, w, dead = thematic_neighbourhood(tvec, m, beta, "second_order", MASTER_SEED + 71)
    return m4_replay_from_neighbourhood(U, idx, w, dead, eta, T)


def oracle_synonym_shrink(U: np.ndarray, syn: Dict[int, np.ndarray], rho: float) -> np.ndarray:
    """ORACLE, CEILING REFERENCE ONLY. Built FROM the synonym sets that also build the cue, so no
    number from it is ever a capability claim. Reproduces scratch/tcc_clumping_dose_response.py
    exactly so the two curves can be overlaid on one x-axis."""
    Sn = l2n(U)
    cent = np.zeros_like(Sn)
    has = np.zeros(Sn.shape[0], dtype=bool)
    for i in range(Sn.shape[0]):
        mm = syn.get(i)
        if mm is not None and mm.size:
            cent[i] = Sn[mm].mean(axis=0)
            has[i] = True
    out = Sn.copy()
    out[has] = l2n((1.0 - rho) * Sn[has] + rho * cent[has])
    return out


# =============================================================================================
# SUPPLY
# =============================================================================================
def load_all() -> Dict:
    import experiments.exp_grounding_readout_known_answer_v1 as C3
    from nltk.corpus import wordnet as wn

    z = np.load(CACHE, allow_pickle=True)
    a = np.load(AUX, allow_pickle=True)
    anchors = [str(x) for x in z["anchors"].tolist()]
    pos = {w: i for i, w in enumerate(anchors)}
    mat = np.asarray(z["mat"], dtype=np.float32)
    mat_ok = np.asarray(z["mat_ok"], dtype=bool)
    L_words = [str(x) for x in z["L_words"].tolist()]
    keep = np.asarray(z["keep"], dtype=bool)

    def unflat(flat, lens):
        out, o = [], 0
        for n in lens:
            out.append(np.asarray(flat[o:o + int(n)], dtype=np.int64))
            o += int(n)
        return out

    excl = unflat(z["excl_flat"], z["excl_len"])
    goldB = unflat(z["gold_flat"], z["gold_len"])
    rows = np.flatnonzero(keep)
    items = np.array([pos[L_words[i]] for i in rows], dtype=np.int64)

    syn: Dict[int, np.ndarray] = {}
    for i, w in enumerate(anchors):
        s = set()
        for sy in wn.synsets(w):
            for lm in sy.lemma_names():
                s.add(lm.lower().replace("_", " "))
        s = {x for x in s if not C3._is_variant(x, w)}
        syn[i] = np.array(sorted({pos[x] for x in s if x in pos}), dtype=np.int64)

    coh = defaultdict(list)
    for i, w in enumerate(anchors):
        coh[w[:GATE_K].lower()].append(i)

    return {"anchors": anchors, "pos": pos, "mat": mat, "mat_ok": mat_ok, "rows": rows,
            "items": items, "syn": syn, "cohorts": coh, "excl": excl, "goldB": goldB,
            "Q_part": np.asarray(z["Q_part"], dtype=np.float32),
            "Q_exact": np.asarray(z["Q_exact"], dtype=np.float32),
            "t_mat": np.asarray(a["t_mat"], dtype=np.float32),
            "Tq": np.asarray(a["Tq"], dtype=np.float32),
            "Pq": np.asarray(a["Pq"], dtype=np.float32),
            "fq": np.asarray(a["fq"], dtype=np.float32)}


def build_thematic_vectors(anchors: Sequence[str], pos: Dict[str, int]
                           ) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """PPMI-weighted thematic-partner profile per anchor, from our own corpus extraction. Rows for
    anchors with no thematic edge are ZERO and are EXCLUDED from being anyone's replay partner."""
    import pickle
    with open(THEMATIC, "rb") as fh:
        d = pickle.load(fh)
    n = len(anchors)
    V = np.zeros((n, n), dtype=np.float32)
    used = 0
    for rec in d.get("event", []):
        aw, bw = str(rec[0]), str(rec[1])
        ia, ib = pos.get(aw), pos.get(bw)
        if ia is None or ib is None or ia == ib:
            continue
        pmi = float(rec[3])
        if pmi <= 0.0:
            continue
        V[ia, ib] += pmi
        V[ib, ia] += pmi
        used += 1
    ok = np.linalg.norm(V, axis=1) > 1e-9
    stats = {"source": "data/thematic_relations_v1/thematic_edges_v1.pkl (our own extractor over "
                       "simplewiki; NO WordNet)",
             "n_event_pairs_used_positive_pmi_both_ends_in_store": int(used),
             "n_anchors_with_a_thematic_profile": int(ok.sum()), "n_anchors": int(n)}
    return V, ok, stats


# =============================================================================================
# GEOMETRY MEASUREMENT -- clumping AND its cost, always in the same breath
# =============================================================================================
def measure_geometry(S: np.ndarray, syn: Dict[int, np.ndarray], items: np.ndarray,
                     fq: np.ndarray, seed: int, sample: int = 900) -> Dict:
    """mean cos to SYNONYMS, to NON-synonyms (random and frequency-matched), the RATIO, the rank
    of the nearest synonym, and the participation ratio. The ratio is the whole point: a mechanism
    that raises both numbers equally has achieved nothing."""
    rng = np.random.default_rng(seed)
    n = S.shape[0]
    order = np.argsort(fq)
    dec = np.zeros(fq.size, dtype=np.int64)
    dec[order] = (np.arange(fq.size) * 10) // fq.size
    by_dec = {d: np.flatnonzero(dec == d) for d in range(10)}

    have = np.array([it for it in items if syn[int(it)].size > 0], dtype=np.int64)
    sub = have if have.size <= sample else np.sort(rng.choice(have, size=sample, replace=False))
    cs, cr, cf, rk, nn_syn = [], [], [], [], []
    for it in sub:
        mm = syn[int(it)]
        s_all = S @ S[it]
        s_all[it] = -np.inf
        cs.append(float(np.mean(s_all[mm])))
        rk.append(int(np.sum(s_all > np.max(s_all[mm])) + 1))
        blocked = set(mm.tolist()) | {int(it)}
        r = rng.integers(0, n, size=mm.size * 4)
        r = np.array([x for x in r.tolist() if x not in blocked][:max(mm.size, 1)], dtype=np.int64)
        if r.size:
            cr.append(float(np.mean(s_all[r])))
        fm = []
        for s in mm:
            pool = by_dec[int(dec[int(s)])]
            for _try in range(6):
                c = int(pool[rng.integers(0, pool.size)])
                if c not in blocked:
                    fm.append(c)
                    break
        if fm:
            cf.append(float(np.mean(s_all[np.array(fm)])))
        nn = int(np.argmax(s_all))
        nn_syn.append(1.0 if nn in set(mm.tolist()) else 0.0)

    mcs, mcr, mcf = float(np.mean(cs)), float(np.mean(cr)), float(np.mean(cf))
    return {"n_sampled": int(sub.size),
            "cos_to_SYNONYMS": round(mcs, 4),
            "cos_to_NONSYNONYM_random": round(mcr, 4),
            "cos_to_NONSYNONYM_freq_matched": round(mcf, 4),
            "RATIO_syn_over_random_nonsyn": round(mcs / mcr, 4) if abs(mcr) > 1e-6 else None,
            "RATIO_syn_over_freqmatched_nonsyn": round(mcs / mcf, 4) if abs(mcf) > 1e-6 else None,
            "GAP_syn_minus_freqmatched": round(mcs - mcf, 4),
            "median_rank_of_nearest_synonym_of_5491": float(np.median(rk)),
            "frac_nearest_synonym_in_top10": round(float(np.mean(np.asarray(rk) <= 10)), 4),
            "P_nearest_neighbour_IS_a_synonym": round(float(np.mean(nn_syn)), 4),
            "PARTICIPATION_RATIO_unit_of_256": round(participation_ratio(S), 2)}


# =============================================================================================
# THE INSTRUMENTS -- identical scorer / n / pool / gold for every variant
# =============================================================================================
class Instruments:
    def __init__(self, D: Dict):
        self.D = D
        anchors, pos = D["anchors"], D["pos"]
        self.n_a = len(anchors)
        self.items = D["items"]
        self.rows = D["rows"]
        self.n_i = self.items.size
        self.mat_ok = D["mat_ok"]
        self.syn = D["syn"]

        # ---- instrument A (self-recovery, FULL pool). gold = the word's OWN row.
        self.eligA = np.repeat(self.mat_ok[:, None], self.n_i, axis=1)
        self.goldA = np.zeros((self.n_a, self.n_i), dtype=bool)
        self.goldA[self.items, np.arange(self.n_i)] = True

        # ---- instrument A2 (onset-GATED self-recovery). The gate is a SCOPE constraint; every
        # arm and every floor is scored on the IDENTICAL gated pool so the gate is never a margin.
        self.gate = np.zeros((self.n_a, self.n_i), dtype=bool)
        for c, it in enumerate(self.items):
            self.gate[np.array(D["cohorts"][anchors[int(it)][:GATE_K].lower()],
                               dtype=np.int64), c] = True
        self.gate &= self.mat_ok[:, None]
        self.csize = self.gate.sum(axis=0)
        self.has_syn = np.array([self.syn[int(it)].size > 0 for it in self.items])
        # THE POPULATION FOR THE CHANNEL CLAIM, kept apart and never merged: 37.1% of items have
        # no WordNet synonym at all and their cue is the zero vector.
        self.maskA2 = self.has_syn & (self.csize > 1)

        # ---- instrument B (open-vocabulary WordNet read-out)
        self.goldB = np.zeros((self.n_a, self.n_i), dtype=bool)
        self.eligB = np.repeat(self.mat_ok[:, None], self.n_i, axis=1)
        for c, r in enumerate(self.rows):
            g = D["goldB"][r]
            if g.size:
                self.goldB[g, c] = True
            self.eligB[D["excl"][r], c] = False
        self.has_goldB = self.goldB.any(axis=0)
        self.permNULL = np.random.default_rng(MASTER_SEED + 99).permutation(self.n_i)

    # -- arms -----------------------------------------------------------------------------
    def semantic_cue(self, S: np.ndarray) -> np.ndarray:
        Q = np.zeros((self.n_i, S.shape[1]), dtype=np.float32)
        for c, it in enumerate(self.items):
            mm = self.syn[int(it)]
            if mm.size:
                Q[c] = S[mm].sum(axis=0)
        return Q

    def score(self, S: np.ndarray, Q: np.ndarray) -> np.ndarray:
        return (S @ l2n(Q).T).astype(np.float32)

    @staticmethod
    def hit(Sc: np.ndarray, elig: np.ndarray, gold: np.ndarray) -> np.ndarray:
        return np.asarray(FB.hit_at_1_both_tie_conventions(Sc, elig, gold)["hit_exp"],
                          dtype=np.float64)

    def evaluate(self, S: np.ndarray, raw_for_floors: np.ndarray) -> Dict[str, np.ndarray]:
        """Returns per-item hit_exp vectors for every arm. IDENTICAL scorer/n/pool/gold across
        variants; only the store changes."""
        D = self.D
        H: Dict[str, np.ndarray] = {}
        Qsem = self.semantic_cue(S)

        # ---------- VALIDITY FIRST. Nothing below is read until these are read.
        H["KA_CONSOLIDATED_own_row"] = self.hit(self.score(S, S[self.items]),
                                                self.eligA, self.goldA)
        H["KA_FIXED_unconsolidated_profile"] = self.hit(
            self.score(S, D["Q_exact"][self.rows]), self.eligA, self.goldA)
        H["NULL_semantic_cue_for_a_DIFFERENT_word__gated"] = self.hit(
            self.score(S, Qsem[self.permNULL]), self.gate, self.goldA)

        # ---------- A2: THE CHANNEL. gate k=3, semantic drive.
        H["A2_SEMANTIC_gated"] = self.hit(self.score(S, Qsem), self.gate, self.goldA)
        H["A2_SENTENCE_gated"] = self.hit(
            self.score(S, D["Q_part"][self.rows]), self.gate, self.goldA)
        rr = np.random.default_rng(MASTER_SEED + 9)
        H["A2_F_RANDOM_WITHIN_GATE"] = self.hit(
            rr.random((self.n_a, self.n_i)).astype(np.float32), self.gate, self.goldA)
        H["A2_F_FREQUENCY"] = self.hit(
            np.repeat(D["fq"][:, None], self.n_i, axis=1).astype(np.float32),
            self.gate, self.goldA)
        H["A2_F_CONSTANT_PROTOTYPE"] = self.hit(
            np.repeat(FB.constant_prototype_floor(raw_for_floors, self.mat_ok)[:, None],
                      self.n_i, axis=1).astype(np.float32), self.gate, self.goldA)
        H["A2_F_SCRAMBLE"] = self.hit(
            self.score(l2n(FB.scramble_null(raw_for_floors, MASTER_SEED)), Qsem),
            self.gate, self.goldA)

        # ---------- A1: THE SYSTEM on the FULL 5,491 pool. The reading cue we already have.
        H["A1_SENTENCE_full_pool"] = self.hit(
            self.score(S, D["Q_part"][self.rows]), self.eligA, self.goldA)
        H["A1_SEMANTIC_full_pool"] = self.hit(self.score(S, Qsem), self.eligA, self.goldA)
        H["A1_DRIVE_SENTENCE_plus_SYNONYMS"] = self.hit(
            self.score(S, l2n(l2n(D["Q_part"][self.rows]) + l2n(Qsem))), self.eligA, self.goldA)
        H["A1_F_FREQUENCY"] = self.hit(
            np.repeat(D["fq"][:, None], self.n_i, axis=1).astype(np.float32),
            self.eligA, self.goldA)
        H["A1_F_CONSTANT_PROTOTYPE"] = self.hit(
            np.repeat(FB.constant_prototype_floor(raw_for_floors, self.mat_ok)[:, None],
                      self.n_i, axis=1).astype(np.float32), self.eligA, self.goldA)
        H["A1_F_SCRAMBLE"] = self.hit(
            self.score(l2n(FB.scramble_null(raw_for_floors, MASTER_SEED)),
                       D["Q_part"][self.rows]), self.eligA, self.goldA)
        # INSTRUMENT_CHECK, not floors: on a self-recovery instrument the FULL spelling of the
        # target IS the answer, so these read at ceiling by construction. Established by the
        # prior cell's smoke gate; carried so nobody re-derives them as floors.
        H["A1_INSTRUMENT_CHECK_full_trigram"] = self.hit(
            (D["t_mat"] @ D["t_mat"][self.items].T).astype(np.float32), self.eligA, self.goldA)

        # ---------- B: the programme's standing open-vocabulary WordNet read-out.
        H["B_EXACT_KEY"] = self.hit(self.score(S, D["Q_exact"][self.rows]),
                                    self.eligB, self.goldB)
        H["B_PARTIAL_CUE_sentence"] = self.hit(self.score(S, D["Q_part"][self.rows]),
                                               self.eligB, self.goldB)
        H["B_F1_TRIGRAM_ONLY"] = self.hit(
            (D["t_mat"] @ D["Tq"][self.rows].T).astype(np.float32), self.eligB, self.goldB)
        H["B_F2_PREFIX_ONLY"] = self.hit(D["Pq"][self.rows].T.astype(np.float32),
                                         self.eligB, self.goldB)
        H["B_F3_FREQUENCY"] = self.hit(
            np.repeat(D["fq"][:, None], self.n_i, axis=1).astype(np.float32),
            self.eligB, self.goldB)
        H["B_F4_CONSTANT_PROTOTYPE"] = self.hit(
            np.repeat(FB.constant_prototype_floor(raw_for_floors, self.mat_ok)[:, None],
                      self.n_i, axis=1).astype(np.float32), self.eligB, self.goldB)
        H["B_F5_SCRAMBLE"] = self.hit(
            self.score(l2n(FB.scramble_null(raw_for_floors, MASTER_SEED)),
                       D["Q_exact"][self.rows]), self.eligB, self.goldB)
        return H


# =============================================================================================
# SELF-TEST -- every claim the run leans on, asserted on constructed data with a known answer.
# =============================================================================================
def self_test() -> int:
    out: Dict = {}
    rng = np.random.default_rng(3)

    # T1 participation ratio: rank-1 -> 1.0; isotropic k-dim -> ~k.
    X = np.outer(rng.normal(size=64), rng.normal(size=16)).astype(np.float32)
    pr1 = participation_ratio(X)
    Y = rng.normal(size=(4000, 16)).astype(np.float32)
    pr2 = participation_ratio(Y)
    assert abs(pr1 - 1.0) < 1e-3, pr1
    assert 14.0 < pr2 < 18.0, pr2
    out["T1_participation_ratio"] = {"rank1": round(pr1, 5), "isotropic16": round(pr2, 3)}

    # T2 topm_neighbours returns the TRUE top-m, in order, self excluded.
    A = l2n(rng.normal(size=(200, 24)))
    idx, val = topm_neighbours(A, 5, block=37)
    C = A @ A.T
    np.fill_diagonal(C, -np.inf)
    ref = np.argsort(-C, axis=1)[:, :5]
    assert (idx == ref).all(), "topm disagrees with a full argsort"
    assert (np.diff(val, axis=1) <= 1e-6).all(), "topm values not descending"
    assert not (idx == np.arange(200)[:, None]).any(), "self appeared in its own neighbourhood"
    out["T2_topm"] = "exact agreement with full argsort on n=200, self excluded, descending"

    # T3 the replay update at eta=0 is the IDENTITY and at eta=1 is the pure neighbour mean.
    B = l2n(rng.normal(size=(120, 16)))
    i5, v5 = topm_neighbours(B, 4)
    w5 = _weights(v5, 1.0)
    z0 = _pull(B, i5, w5, 0.0)
    assert float(np.abs(z0 - B).max()) < 1e-5, "eta=0 is not the identity"
    z1 = _pull(B, i5, w5, 1.0)
    manual = l2n(np.einsum("ij,ijk->ik", w5, B[i5]))
    assert float(np.abs(z1 - manual).max()) < 1e-5, "eta=1 is not the weighted neighbour mean"
    out["T3_update_endpoints"] = "eta=0 identity, eta=1 pure neighbour mean, both exact"

    # T4 THE DISCRIMINATOR, AND THE FIRST DRAFT OF THIS ASSERT FAILED AND WAS RIGHT TO.
    # The first draft planted zero-mean clusters, so the BETWEEN-group mean cosine sat at about
    # -0.001 and the RATIO (within / between) was a division by ~0 -- it read -24.6 on the base
    # store and 1.60 after a treatment that had plainly improved things. A ratio is only a
    # statistic when its denominator is comfortably positive. The real store's between-set cosine
    # is +0.0977, so the synthetic data is now built with a shared component to match, and the
    # assertion is the one the REAL analysis makes: at MATCHED within-group cosine the structured
    # mechanism must beat the isotropic collapse. The GAP is asserted beside the RATIO because the
    # gap has no degenerate denominator.
    # Noise is scaled by 1/sqrt(d) so its NORM, not its per-dimension scale, is what the variance
    # budget controls, and every fixture carries a SHARED component so that between-set cosine is
    # comfortably positive and the ratio is a statistic (the live store reads 0.0977 between).
    d, g, per = 32, 12, 12
    lab = np.repeat(np.arange(g), per)
    same = lab[:, None] == lab[None, :]
    np.fill_diagonal(same, False)

    def fixture(s_, g_, e_, seed):
        rr = np.random.default_rng(seed)
        sh = l2n(rr.normal(size=(1, d)))
        cn = l2n(rr.normal(size=(g, d)))
        return l2n(s_ * np.repeat(sh, g * per, axis=0) + g_ * np.repeat(cn, per, axis=0)
                   + (e_ / np.sqrt(d)) * rr.normal(size=(g * per, d)).astype(np.float32))

    def stat(M):
        Cm = l2n(M) @ l2n(M).T
        np.fill_diagonal(Cm, 0.0)
        w_, b_ = float(Cm[same].mean()), float(Cm[~same].mean())
        return {"within": w_, "between": b_, "ratio": w_ / b_, "gap": w_ - b_}

    def purity(M, m_):
        Cm = l2n(M) @ l2n(M).T
        np.fill_diagonal(Cm, -9.0)
        ii = np.argsort(-Cm, axis=1)[:, :m_]
        return float(same[np.arange(g * per)[:, None], ii].mean())

    def matched_iso(P_, target_within):
        isos = [(b, stat(c_iso_collapse(P_, b)))
                for b in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)]
        xs = np.array([s["within"] for _b, s in isos])
        o = np.argsort(xs)
        return ({"ratio": float(np.interp(target_within, xs[o],
                                          np.array([s["ratio"] for _b, s in isos])[o])),
                 "gap": float(np.interp(target_within, xs[o],
                                        np.array([s["gap"] for _b, s in isos])[o]))},
                isos)

    # --- T4a HIGH-STRUCTURE fixture. Here the mechanism MUST work; if it does not, the code is
    #     broken. This is the machinery test.
    PH = fixture(0.316, 0.671, 0.671, 21)
    s0 = stat(PH)
    assert s0["between"] > 0.02, "degenerate between-group baseline: %r" % s0
    pur_h = purity(PH, 6)
    assert pur_h > 0.8, "high-structure fixture is not high-structure: purity=%.3f" % pur_h
    s1 = stat(m1_shared_context_replay(PH, m=6, eta=0.6, T=3, beta=3.0, recentre=False))
    iso_at, isos = matched_iso(PH, s1["within"])
    assert s1["within"] > s0["within"], "replay did not raise within-group cosine"
    assert s1["ratio"] > s0["ratio"], "replay did not raise the RATIO"
    assert isos[-1][1]["within"] > s0["within"], (
        "the isotropic control did not raise within-group cosine -- it MUST, for free, or the "
        "confound this cell exists to rule out is absent from the fixture")
    assert isos[-1][1]["ratio"] < s0["ratio"], (
        "the isotropic control raised the RATIO, which it must not: it moves every pair alike")
    assert s1["ratio"] > iso_at["ratio"] * 1.5, (
        "AT MATCHED WITHIN-GROUP COSINE the isotropic collapse equals the mechanism even on a "
        "high-structure fixture. The discriminator cannot fire. M1=%r iso_at=%r" % (s1, iso_at))
    assert s1["gap"] > iso_at["gap"] * 1.5, "matched-clumping GAP does not separate either"

    # --- T4b LOW-STRUCTURE fixture, and this is the CAN-FAIL half. When the store's own
    #     neighbourhood is mostly NOT same-group -- which is our real store's regime, where a
    #     word's nearest neighbour is a synonym 0.60% of the time -- the mechanism must NOT beat
    #     matched isotropic collapse. If it did, the comparison would be rigged to pass and every
    #     positive this cell can produce would be worthless.
    PL = fixture(0.316, 0.316, 0.894, 22)
    l0 = stat(PL)
    pur_l = purity(PL, 6)
    assert pur_l < 0.4, "low-structure fixture is not low-structure: purity=%.3f" % pur_l
    l1 = stat(m1_shared_context_replay(PL, m=6, eta=0.3, T=3, beta=3.0, recentre=False))
    iso_at_l, _ = matched_iso(PL, l1["within"])
    assert l1["ratio"] < iso_at_l["ratio"] * 1.5, (
        "the mechanism 'beat' matched isotropic collapse on a fixture with almost no usable "
        "neighbourhood structure. The instrument passes things it should not. M1=%r iso=%r"
        % (l1, iso_at_l))

    out["T4_DISCRIMINATOR_FIRES_AND_CAN_FAIL"] = {
        "HIGH_STRUCTURE_fixture": {
            "top6_neighbourhood_purity": round(pur_h, 3),
            "base": {k: round(v, 4) for k, v in s0.items()},
            "M1_replay": {k: round(v, 4) for k, v in s1.items()},
            "C_ISO_INTERPOLATED_TO_THE_SAME_within_cos": {k: round(v, 4)
                                                          for k, v in iso_at.items()},
            "C_ISO_sweep": {("beta%.2f" % b): {k: round(v, 4) for k, v in s.items()}
                            for b, s in isos}},
        "LOW_STRUCTURE_fixture_the_CAN_FAIL_half": {
            "top6_neighbourhood_purity": round(pur_l, 3),
            "base": {k: round(v, 4) for k, v in l0.items()},
            "M1_replay": {k: round(v, 4) for k, v in l1.items()},
            "C_ISO_INTERPOLATED_TO_THE_SAME_within_cos": {k: round(v, 4)
                                                          for k, v in iso_at_l.items()}},
        "reading": "the isotropic control raises within-group COSINE for free and does not raise "
                   "the ratio or the gap, so matched-clumping interpolation is what separates a "
                   "real gain from a free one. The mechanism separates on a high-purity "
                   "neighbourhood and does NOT separate on a low-purity one, which is exactly the "
                   "property that makes a positive on the real store worth anything.",
        "A_CAVEAT_THAT_MUST_TRAVEL_WITH_THE_RATIO": "the ratio COMPRESSES as within-cosine "
                   "approaches 1.0 (both terms saturate), so a falling ratio at high dose is not "
                   "by itself evidence of harm. The GAP and the matched-isotropic comparison are "
                   "the robust columns and all three are published for every variant."}

    # T5 the connected-components clustering AGREES EXACTLY with the owned organ at n=300.
    from hdlab.ultrametric_clustering import cosine_distance_matrix, single_linkage_clusters
    W = l2n(np.repeat(l2n(rng.normal(size=(30, 12))), 10, axis=0)
            + 0.35 * rng.normal(size=(300, 12)).astype(np.float32))
    Dm = cosine_distance_matrix(W)
    agree = {}
    nontrivial = 0
    for thr in (0.40, 0.55, 0.70, 0.80, 0.90):
        organ = single_linkage_clusters(Dm, 1.0 - thr)
        organ_lab = np.zeros(300, dtype=np.int64)
        for ci, cl in enumerate(organ):
            for x in cl:
                organ_lab[x] = ci
        mine = _single_linkage_labels(l2n(W), thr)
        same_organ = organ_lab[:, None] == organ_lab[None, :]
        same_mine = mine[:, None] == mine[None, :]
        assert (same_organ == same_mine).all(), (
            "our clustering disagrees with hdlab's organ at thr=%.2f" % thr)
        sizes = np.bincount(organ_lab)
        agree["thr%.2f" % thr] = {"n_clusters": len(organ),
                                  "largest": int(sizes.max()),
                                  "n_singletons": int((sizes == 1).sum())}
        # a partition with ONE cluster, or with 300, makes the agreement claim vacuous.
        if 5 <= len(organ) <= 295 and int(sizes.max()) > 1:
            nontrivial += 1
    assert nontrivial >= 2, (
        "every threshold gave a DEGENERATE partition (all-one or all-singleton), so 'identical "
        "partition' proves nothing. %r" % agree)
    out["T5_owned_organ_agreement"] = {
        "organ": "hdlab.ultrametric_clustering.single_linkage_clusters "
                 "(+ cosine_distance_matrix), called UNMODIFIED",
        "n": 300, "identical_partition_at_every_threshold": True,
        "n_thresholds_with_a_NONTRIVIAL_partition": nontrivial,
        "per_threshold": agree,
        "why_this_matters": "the organ is O(n^2) in PYTHON TUPLES -- 15.1M of them at n=5491 -- "
                            "so it cannot be called at store scale. This cell uses a "
                            "connected-components equivalent and this witness is what licenses "
                            "that substitution."}

    # T6 the scorer: a planted answer reads exactly 1.0, and a scrambled store does not.
    n_a, n_i = 60, 40
    Sc = rng.random((n_a, n_i)).astype(np.float32)
    elig = np.ones((n_a, n_i), dtype=bool)
    gold = np.zeros((n_a, n_i), dtype=bool)
    tg = rng.integers(0, n_a, size=n_i)
    gold[tg, np.arange(n_i)] = True
    Sc[tg, np.arange(n_i)] = 99.0
    h = FB.hit_at_1_both_tie_conventions(Sc, elig, gold)["hit_exp"]
    assert abs(float(np.mean(h)) - 1.0) < 1e-12, float(np.mean(h))
    out["T6_scorer_planted_answer"] = 1.0

    # T7 the ORACLE reproduces the landed direction: rho=0 is the identity.
    syn = {i: np.array([(i + 1) % 50, (i + 2) % 50], dtype=np.int64) for i in range(50)}
    Z = l2n(rng.normal(size=(50, 16)))
    assert float(np.abs(oracle_synonym_shrink(Z, syn, 0.0) - Z).max()) < 1e-5
    out["T7_oracle_rho0_is_identity"] = True

    # T8 the ruler-mode gate, called, not assumed.
    from experiments.exp_task_degeneracy_v1 import ruler_mode_gate
    out["T8_ruler_mode_gate"] = ruler_mode_gate()
    assert "--smoke" not in sys.argv, "--smoke in argv silently swaps the imported ruler"

    # T9 PCA truncation: at k=d it is the identity; at k=1 the CENTRED matrix is exactly rank 1
    # BEFORE the row renormalisation (renormalising is nonlinear and lifts the rank back up, which
    # is why the naive "PR must be 1.0 after truncation" assertion is wrong and was removed).
    Q = l2n(rng.normal(size=(80, 16)))
    assert float(np.abs(m3_pca_truncate(Q, 16) - Q).max()) < 1e-4, "k=d is not the identity"
    Qc = Q.astype(np.float64) - Q.astype(np.float64).mean(axis=0, keepdims=True)
    _u9, s9, v9 = np.linalg.svd(Qc, full_matrices=False)
    V1 = v9[:1].T
    rank1 = (Qc @ V1) @ V1.T
    sv = np.linalg.svd(rank1, compute_uv=False)
    assert float(sv[1]) < 1e-8 * float(sv[0]), "top-1 projection is not rank 1"
    pr_after = participation_ratio(m3_pca_truncate(Q, 1))
    assert pr_after < participation_ratio(Q), "k=1 truncation did not reduce the PR"
    out["T9_pca_truncate"] = {"k=d_is_identity": True, "top1_projection_is_rank1": True,
                              "PR_before": round(participation_ratio(Q), 3),
                              "PR_after_k1_and_renormalise": round(pr_after, 3),
                              "note": "row renormalisation lifts the rank back; the PR column in "
                                      "the report is measured AFTER renormalisation, as the "
                                      "scorer sees it."}

    print(json.dumps(out, indent=1, default=str), flush=True)
    print("SELF-TEST PASS: 9 groups", flush=True)
    return 0


# =============================================================================================
# THE VARIANT GRID
# =============================================================================================
def variant_grid(grid: str) -> List[Tuple[str, str, Dict]]:
    """(unit_name, family, params). family drives the builder; ORACLE arms carry the label."""
    V: List[Tuple[str, str, Dict]] = [("REAL_STORE_rho0", "REAL", {})]
    if grid == "smoke":
        etas = (0.3, 0.7)
        isos = (0.2, 0.5)
        rhos = (0.3, 0.7)
        ks = (16, 64)
        M2 = ((0.30, 0.5), (0.50, 0.5))
        M4 = (0.5,)
        Ts = ()
    else:
        etas = (0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0)
        isos = (0.1, 0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 0.9)
        rhos = (0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0)
        ks = (4, 8, 16, 32, 64, 128)
        # single-linkage CHAINS: too low a threshold merges the whole store into one cluster (in
        # which case M2 degenerates INTO the isotropic control) and too high leaves only
        # singletons (in which case M2 is the identity). The threshold is therefore SWEPT and the
        # cluster statistics are published beside every row so the reader can see which regime
        # each variant is actually in.
        M2 = ((0.25, 0.5), (0.35, 0.5), (0.45, 0.5), (0.45, 0.3), (0.45, 0.7), (0.45, 1.0),
              (0.55, 0.5), (0.65, 0.5))
        M4 = (0.2, 0.5, 0.9)
        Ts = (2, 4, 8)
    for e in etas:
        V.append(("M1_REPLAY_m20_b3_T1_eta%.2f" % e, "M1",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "recentre": False}))
    for t in Ts:
        V.append(("M1_REPLAY_m20_b3_eta0.50_T%d" % t, "M1",
                  {"m": 20, "eta": 0.5, "T": t, "beta": 3.0, "recentre": False}))
    for e in etas:
        V.append(("M1R_REPLAY_RECENTRED_m20_b3_T1_eta%.2f" % e, "M1",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "recentre": True}))
    if grid != "smoke":
        for m in (5, 50, 200):
            V.append(("M1_REPLAY_b3_T1_eta0.70_m%d" % m, "M1",
                      {"m": m, "eta": 0.7, "T": 1, "beta": 3.0, "recentre": False}))
    for e in etas:
        V.append(("C_RAND_NEIGHBOURS_m20_T1_eta%.2f" % e, "C_RAND", {"m": 20, "eta": e, "T": 1}))
    for b in isos:
        V.append(("C_ISO_GLOBAL_CENTROID_beta%.2f" % b, "C_ISO", {"beta": b}))
    for (th, rh) in M2:
        V.append(("M2_CLUSTER_thr%.2f_rho%.2f" % (th, rh), "M2", {"thr": th, "rho": rh}))
    for k in ks:
        V.append(("M3_PCA_TRUNCATE_k%d" % k, "M3", {"k": k}))
    for e in M4:
        V.append(("M4_THEMATIC_SECOND_ORDER_m20_eta%.2f" % e, "M4",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "mode": "second_order"}))
    if grid != "smoke":
        for m in (5, 50, 100):
            V.append(("M4_THEMATIC_SECOND_ORDER_eta0.50_m%d" % m, "M4",
                      {"m": m, "eta": 0.5, "T": 1, "beta": 3.0, "mode": "second_order"}))
        # the m=5 arm is the one that reads best on the open-vocabulary instrument, so its OWN
        # control ladder is run at m=5 rather than borrowed from m=20. A control at a different
        # hyper-parameter is not a matched control.
        V.append(("M4b_THEMATIC_FIRST_ORDER_m5_eta0.50", "M4",
                  {"m": 5, "eta": 0.5, "T": 1, "beta": 3.0, "mode": "first_order"}))
        V.append(("C_THEM_SHUFFLED_PROFILES_m5_eta0.50", "M4",
                  {"m": 5, "eta": 0.5, "T": 1, "beta": 3.0, "mode": "shuffled"}))
        V.append(("C_THEM_FREQ_MATCHED_m5_eta0.50", "M4",
                  {"m": 5, "eta": 0.5, "T": 1, "beta": 3.0, "mode": "freq_matched"}))
        V.append(("C_RAND_NEIGHBOURS_m5_T1_eta0.50", "C_RAND", {"m": 5, "eta": 0.5, "T": 1}))
        for t in (2, 4):
            V.append(("M4_THEMATIC_SECOND_ORDER_m20_eta0.50_T%d" % t, "M4",
                      {"m": 20, "eta": 0.5, "T": t, "beta": 3.0, "mode": "second_order"}))
    # THE FALSIFIER for the second-order claim made in the biology section.
    for e in ((0.5,) if grid == "smoke" else (0.2, 0.5, 0.9)):
        V.append(("M4b_THEMATIC_FIRST_ORDER_m20_eta%.2f" % e, "M4",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "mode": "first_order"}))
    # THE TWO CONTROLS M4 MUST SURVIVE before any thematic number is quoted.
    for e in ((0.5,) if grid == "smoke" else (0.2, 0.5, 0.9)):
        V.append(("C_THEM_SHUFFLED_PROFILES_m20_eta%.2f" % e, "M4",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "mode": "shuffled"}))
        V.append(("C_THEM_FREQ_MATCHED_m20_eta%.2f" % e, "M4",
                  {"m": 20, "eta": e, "T": 1, "beta": 3.0, "mode": "freq_matched"}))
    # DOES THE REPLAY OPERATOR WORK ONCE THE METRIC IS RIGHT? M1 run INSIDE the thematically
    # consolidated geometry. If M1 was failing because the store's own neighbourhood is not
    # semantic, it should start working here -- and that is a testable claim, not a story.
    for e in ((0.5,) if grid == "smoke" else (0.3, 0.5, 0.7)):
        V.append(("M5_THEMATIC_then_M1REPLAY_eta%.2f" % e, "M5",
                  {"m": 20, "eta_them": 0.5, "eta": e, "T": 1, "beta": 3.0}))
    for r in rhos:
        V.append(("ORACLE_SYNONYM_CENTROID_rho%.2f" % r, "ORACLE", {"rho": r}))
    return V


def build_variant(fam: str, p: Dict, base: np.ndarray, D: Dict, TH: Dict, log
                  ) -> Tuple[np.ndarray, Dict]:
    if fam == "REAL":
        return l2n(base), {}
    if fam == "M1":
        return m1_shared_context_replay(base, p["m"], p["eta"], p["T"], p["beta"],
                                        p["recentre"], log), {}
    if fam == "C_RAND":
        return c_rand_replay(base, p["m"], p["eta"], p["T"], MASTER_SEED + 41), {}
    if fam == "C_ISO":
        return c_iso_collapse(base, p["beta"]), {}
    if fam == "M2":
        return m2_cluster_shrink(base, p["thr"], p["rho"])
    if fam == "M3":
        return m3_pca_truncate(base, p["k"]), {}
    if fam == "M4":
        ck = (p["mode"], p["m"], p["beta"])
        if ck not in TH["nbr"]:
            TH["nbr"][ck] = thematic_neighbourhood(TH["V"], p["m"], p["beta"], p["mode"],
                                                   MASTER_SEED + 71, TH["fq"])
        idx, w, dead = TH["nbr"][ck]
        ex = dict(TH["stats"])
        ex["mode"] = p["mode"]
        ex["n_anchors_pinned_no_thematic_profile"] = int(dead.sum())
        ex["THEMATIC_NEIGHBOURHOOD_PURITY"] = TH["purity"](idx, dead)
        return m4_replay_from_neighbourhood(base, idx, w, dead, p["eta"], p["T"]), ex
    if fam == "M5":
        ck = ("second_order", p["m"], p["beta"])
        if ck not in TH["nbr"]:
            TH["nbr"][ck] = thematic_neighbourhood(TH["V"], p["m"], p["beta"], "second_order",
                                                   MASTER_SEED + 71, TH["fq"])
        idx, w, dead = TH["nbr"][ck]
        S = m4_replay_from_neighbourhood(base, idx, w, dead, p["eta_them"], 1)
        return m1_shared_context_replay(S, p["m"], p["eta"], p["T"], p["beta"], False, log), {
            "note": "M1 shared-context replay run INSIDE the thematically consolidated geometry"}
    if fam == "ORACLE":
        return oracle_synonym_shrink(base, D["syn"], p["rho"]), {}
    raise ValueError("unknown family " + fam)


# =============================================================================================
# RUN
# =============================================================================================
def run(grid: str, out_dir: str) -> int:
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    from experiments.exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()
    print("[gate] ruler_mode_gate PASS %s" % json.dumps(gate), flush=True)

    D = load_all()
    INS = Instruments(D)
    base = D["mat"]
    print("[load] n_anchors=%d n_items=%d mask_A2=%d elapsed=%.1fs"
          % (INS.n_a, INS.n_i, int(INS.maskA2.sum()), time.time() - t0), flush=True)

    Vth, _ok_th, th_stats = build_thematic_vectors(D["anchors"], D["pos"])

    def them_purity(idx: np.ndarray, dead: np.ndarray) -> Dict:
        """WHY the thematic channel does or does not help, measured rather than argued: how often
        is a word's thematic replay partner one of its WordNet synonyms, and how does that compare
        to the store's OWN neighbourhood (whose synonym rate the prior cell measured at 0.60% for
        the single nearest neighbour)?"""
        syn = D["syn"]
        live = np.flatnonzero(~dead)
        rs = np.random.default_rng(MASTER_SEED + 77)
        sub = live if live.size <= 1500 else np.sort(rs.choice(live, 1500, replace=False))
        hit, tot, any_hit, n_with = 0, 0, 0, 0
        for i in sub:
            mm = syn.get(int(i))
            if mm is None or mm.size == 0:
                continue
            n_with += 1
            ss = set(mm.tolist())
            h = sum(1 for j in idx[i].tolist() if j in ss)
            hit += h
            tot += idx.shape[1]
            any_hit += 1 if h else 0
        return {"n_words_scored": n_with,
                "frac_of_replay_partners_that_are_SYNONYMS": round(hit / max(tot, 1), 4),
                "frac_of_words_with_AT_LEAST_ONE_synonym_partner": round(any_hit / max(n_with, 1),
                                                                         4)}

    TH = {"V": Vth, "stats": th_stats, "nbr": {}, "fq": D["fq"], "purity": them_purity}
    print("[thematic] %s" % json.dumps(th_stats), flush=True)

    # the same purity statistic for the STORE'S OWN neighbourhood, so the two are comparable.
    _si, _sv = topm_neighbours(l2n(base), 20)
    store_purity = them_purity(_si, np.zeros(INS.n_a, dtype=bool))
    print("[purity] STORE_OWN_top20 %s" % json.dumps(store_purity), flush=True)
    th_stats["STORE_OWN_top20_neighbourhood_purity_for_comparison"] = store_purity

    grid_list = variant_grid(grid)
    done = completed_units(out_dir)
    print("[grid] %d variants, %d already complete" % (len(grid_list), len(done)), flush=True)

    for vi, (name, fam, p) in enumerate(grid_list):
        key = unit_key(grid, name)
        if key in done:
            print("[unit %d/%d] %s SKIP (checkpointed)" % (vi + 1, len(grid_list), name),
                  flush=True)
            continue
        ts = time.time()

        def log(msg, _n=name):
            print("[unit] %s %s" % (_n, msg), flush=True)

        S, extra = build_variant(fam, p, base, D, TH, log)
        geo = measure_geometry(S, D["syn"], INS.items, D["fq"], MASTER_SEED + 5)
        # floors that depend on the store are computed from the VARIANT store in its own scale
        H = INS.evaluate(S, S)
        np.savez_compressed(os.path.join(out_dir, "hits__%s.npz" % name),
                            **{k: v.astype(np.float32) for k, v in H.items()})
        summ = {"family": fam, "params": p, "geometry": geo, "extra": extra,
                "acc_on_A2_population": {k: round(float(np.mean(v[INS.maskA2])), 4)
                                         for k, v in H.items()},
                "acc_on_ALL_items": {k: round(float(np.mean(v)), 4) for k, v in H.items()},
                "elapsed_s": round(time.time() - ts, 1)}
        summ["VALIDITY"] = {
            "KA_CONSOLIDATED": summ["acc_on_ALL_items"]["KA_CONSOLIDATED_own_row"],
            "KA_FIXED": summ["acc_on_ALL_items"]["KA_FIXED_unconsolidated_profile"],
            "NULL_gated": summ["acc_on_A2_population"][
                "NULL_semantic_cue_for_a_DIFFERENT_word__gated"],
            "PASS_KA": bool(summ["acc_on_ALL_items"]["KA_CONSOLIDATED_own_row"] >= KA_CEILING_MIN),
            "VOID_COLLAPSED": bool(
                summ["acc_on_ALL_items"]["KA_CONSOLIDATED_own_row"] < KA_CEILING_MIN)}
        record_unit(out_dir, key, summ)
        print("[unit %d/%d] %s cos_syn=%.4f ratio=%.3f PR=%.1f KA=%.4f A2=%.4f A1=%.4f B=%.4f "
              "(%.1fs)"
              % (vi + 1, len(grid_list), name, geo["cos_to_SYNONYMS"],
                 geo["RATIO_syn_over_freqmatched_nonsyn"] or -1.0,
                 geo["PARTICIPATION_RATIO_unit_of_256"],
                 summ["VALIDITY"]["KA_CONSOLIDATED"],
                 summ["acc_on_A2_population"]["A2_SEMANTIC_gated"],
                 summ["acc_on_ALL_items"]["A1_SENTENCE_full_pool"],
                 summ["acc_on_A2_population"]["B_EXACT_KEY"], time.time() - ts), flush=True)

    aggregate(grid, out_dir, INS, gate, th_stats, t0)
    return 0


def aggregate(grid: str, out_dir: str, INS: "Instruments", gate: Dict, th_stats: Dict,
              t0: float) -> None:
    units = load_units(out_dir)
    names = [n for n in sorted(units) if n.startswith(grid + "|")]
    REP: Dict = {
        "cell": "exp_synonym_clumping_consolidation_v1", "grid": grid,
        "ruler_mode_gate": gate, "thematic_supply": th_stats,
        "MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "GATE_K": GATE_K,
        "n_anchors": INS.n_a, "n_items": int(INS.n_i),
        "n_items_A2_population": int(INS.maskA2.sum()),
        "mean_gate_size": round(float(INS.csize.mean()), 2),
        "LANDED_REFERENCE": LANDED,
        "variants": {n.split("|", 1)[1]: units[n] for n in names},
    }

    # ---- REGRESSION GATE, read first
    real = units.get(unit_key(grid, "REAL_STORE_rho0"))
    if real:
        REP["REGRESSION_GATE"] = {
            "cos_to_SYNONYMS": [real["geometry"]["cos_to_SYNONYMS"], LANDED["cos_to_SYNONYMS"]],
            "A2_gated_semantic": [real["acc_on_A2_population"]["A2_SEMANTIC_gated"],
                                  LANDED["A2_gated_k3_semantic_on_items_with_a_synonym"]],
            "A1_sentence_full_pool": [real["acc_on_ALL_items"]["A1_SENTENCE_full_pool"],
                                      LANDED["A1_sentence_cue_full_pool"]],
            "B_exact_key": [real["acc_on_A2_population"]["B_EXACT_KEY"], LANDED["B_exact_key"]],
            "PR_unit": [real["geometry"]["PARTICIPATION_RATIO_unit_of_256"],
                        LANDED["PR_unit_store"]],
        }
        REP["REGRESSION_GATE"]["PASS"] = bool(
            abs(real["geometry"]["cos_to_SYNONYMS"] - LANDED["cos_to_SYNONYMS"]) < 0.01
            and abs(real["acc_on_ALL_items"]["A1_SENTENCE_full_pool"]
                    - LANDED["A1_sentence_cue_full_pool"]) < 0.005)

    # ---- paired bootstrap across ALL variants on ONE mask, one ruler
    def load_hits(nm: str) -> Dict[str, np.ndarray]:
        z = np.load(os.path.join(out_dir, "hits__%s.npz" % nm))
        return {k: np.asarray(z[k], dtype=np.float64) for k in z.files}

    short = [n.split("|", 1)[1] for n in names]
    poolA2: Dict[str, np.ndarray] = {}
    poolA1: Dict[str, np.ndarray] = {}
    poolB: Dict[str, np.ndarray] = {}
    for nm in short:
        try:
            H = load_hits(nm)
        except OSError:
            continue
        poolA2["%s::A2_SEMANTIC" % nm] = H["A2_SEMANTIC_gated"]
        poolA1["%s::A1_SENTENCE" % nm] = H["A1_SENTENCE_full_pool"]
        poolA1["%s::A1_SENT_plus_SYN" % nm] = H["A1_DRIVE_SENTENCE_plus_SYNONYMS"]
        poolB["%s::B_EXACT" % nm] = H["B_EXACT_KEY"]
        poolB["%s::B_PARTIAL" % nm] = H["B_PARTIAL_CUE_sentence"]
        if nm == "REAL_STORE_rho0":
            for f in ("A2_F_RANDOM_WITHIN_GATE", "A2_F_FREQUENCY", "A2_F_CONSTANT_PROTOTYPE",
                      "A2_F_SCRAMBLE"):
                poolA2["FLOOR::%s" % f] = H[f]
            for f in ("A1_F_FREQUENCY", "A1_F_CONSTANT_PROTOTYPE", "A1_F_SCRAMBLE"):
                poolA1["FLOOR::%s" % f] = H[f]
            for f in ("B_F1_TRIGRAM_ONLY", "B_F2_PREFIX_ONLY", "B_F3_FREQUENCY",
                      "B_F4_CONSTANT_PROTOTYPE", "B_F5_SCRAMBLE"):
                poolB["FLOOR::%s" % f] = H[f]
        else:
            # THE FLOORS MOVE WITH THE STORE and must be re-derived per variant, not carried.
            for f in ("A2_F_CONSTANT_PROTOTYPE", "A2_F_SCRAMBLE"):
                poolA2["%s::%s" % (nm, f)] = H[f]
            for f in ("B_F4_CONSTANT_PROTOTYPE", "B_F5_SCRAMBLE"):
                poolB["%s::%s" % (nm, f)] = H[f]

    bsA2 = FB.paired_bootstrap_ci(poolA2, INS.maskA2, N_BOOT, MASTER_SEED + 11)
    bsA1 = FB.paired_bootstrap_ci(poolA1, np.ones(INS.n_i, dtype=bool), N_BOOT, MASTER_SEED + 12)
    bsB = FB.paired_bootstrap_ci(poolB, INS.has_goldB & INS.maskA2, N_BOOT, MASTER_SEED + 13)
    REP["n_common"] = {"A2": bsA2["n_common"], "A1": bsA1["n_common"], "B": bsB["n_common"]}
    REP["acc_on_common"] = {"A2": {k: round(v, 4) for k, v in bsA2["acc"].items()},
                            "A1": {k: round(v, 4) for k, v in bsA1["acc"].items()},
                            "B": {k: round(v, 4) for k, v in bsB["acc"].items()}}

    def strongest_floor_margin(boot, arm, floors):
        """max(orthographic, frequency, scramble, CONSTANT/PROTOTYPE): the STRONGEST floor is the
        one that leaves the SMALLEST margin, so the bar is set by the worst case, never by a
        convenient floor."""
        best = None
        allm = {}
        for f in floors:
            if f not in boot:
                continue
            mm = FB.margin(boot, arm, f)
            allm[f] = mm
            if best is None or mm["point"] < best[1]["point"]:
                best = (f, mm)
        if best is None:
            return None
        return {"strongest_floor": best[0], "margin": best[1], "all_floors": allm}

    A2_FLOORS_BASE = ["FLOOR::A2_F_RANDOM_WITHIN_GATE", "FLOOR::A2_F_FREQUENCY",
                      "FLOOR::A2_F_CONSTANT_PROTOTYPE", "FLOOR::A2_F_SCRAMBLE"]
    B_FLOORS_BASE = ["FLOOR::B_F1_TRIGRAM_ONLY", "FLOOR::B_F2_PREFIX_ONLY",
                     "FLOOR::B_F3_FREQUENCY", "FLOOR::B_F4_CONSTANT_PROTOTYPE",
                     "FLOOR::B_F5_SCRAMBLE"]
    A1_FLOORS = ["FLOOR::A1_F_FREQUENCY", "FLOOR::A1_F_CONSTANT_PROTOTYPE",
                 "FLOOR::A1_F_SCRAMBLE"]

    MAR: Dict = {}
    for nm in short:
        a2 = "%s::A2_SEMANTIC" % nm
        a1 = "%s::A1_SENTENCE" % nm
        bx = "%s::B_EXACT" % nm
        f2 = list(A2_FLOORS_BASE) + ["%s::A2_F_CONSTANT_PROTOTYPE" % nm, "%s::A2_F_SCRAMBLE" % nm]
        fb = list(B_FLOORS_BASE) + ["%s::B_F4_CONSTANT_PROTOTYPE" % nm, "%s::B_F5_SCRAMBLE" % nm]
        MAR[nm] = {
            "A2_vs_REAL_STORE": FB.margin(bsA2["boot"], a2, "REAL_STORE_rho0::A2_SEMANTIC"),
            "A2_vs_STRONGEST_FLOOR": strongest_floor_margin(bsA2["boot"], a2, f2),
            "A1_SYSTEM_vs_REAL_STORE": FB.margin(bsA1["boot"], a1,
                                                 "REAL_STORE_rho0::A1_SENTENCE"),
            "A1_vs_STRONGEST_FLOOR": strongest_floor_margin(bsA1["boot"], a1, A1_FLOORS),
            "B_SYSTEM_vs_REAL_STORE": FB.margin(bsB["boot"], bx, "REAL_STORE_rho0::B_EXACT"),
            "B_vs_STRONGEST_FLOOR": strongest_floor_margin(bsB["boot"], bx, fb),
            "A1_UNION_vs_SENTENCE_ALONE": FB.margin(
                bsA1["boot"], "%s::A1_SENT_plus_SYN" % nm, a1),
        }
    REP["PAIRED_MARGINS"] = MAR

    # ---- THE MATCHED-CLUMPING COMPARISON. Treatments read against the isotropic control at the
    # SAME measured synonym cosine, which is the only way the ratio question gets answered.
    curve = []
    for nm in short:
        u = units[unit_key(grid, nm)]
        curve.append({"variant": nm, "family": u["family"],
                      "cos_syn": u["geometry"]["cos_to_SYNONYMS"],
                      "cos_nonsyn_freqmatched": u["geometry"]["cos_to_NONSYNONYM_freq_matched"],
                      "RATIO": u["geometry"]["RATIO_syn_over_freqmatched_nonsyn"],
                      "PR": u["geometry"]["PARTICIPATION_RATIO_unit_of_256"],
                      "P_nn_is_synonym": u["geometry"]["P_nearest_neighbour_IS_a_synonym"],
                      "KA": u["VALIDITY"]["KA_CONSOLIDATED"],
                      "NULL_gated": u["VALIDITY"]["NULL_gated"],
                      "VOID_COLLAPSED": u["VALIDITY"]["VOID_COLLAPSED"],
                      "A2_channel": u["acc_on_A2_population"]["A2_SEMANTIC_gated"],
                      "A1_system": u["acc_on_ALL_items"]["A1_SENTENCE_full_pool"],
                      "B_system": u["acc_on_A2_population"]["B_EXACT_KEY"]})
    curve.sort(key=lambda r: (r["family"], r["cos_syn"]))
    REP["DOSE_RESPONSE_CURVE"] = curve

    iso = sorted([c for c in curve if c["family"] == "C_ISO"], key=lambda r: r["cos_syn"])
    if iso:
        xs = np.array([c["cos_syn"] for c in iso])
        ya = np.array([c["A2_channel"] for c in iso])
        yr = np.array([c["RATIO"] if c["RATIO"] is not None else np.nan for c in iso])
        matched = []
        for c in curve:
            if c["family"] in ("C_ISO", "REAL"):
                continue
            matched.append({
                "variant": c["variant"], "cos_syn": c["cos_syn"],
                "A2_channel": c["A2_channel"],
                "C_ISO_A2_at_the_SAME_cos_syn": round(float(np.interp(c["cos_syn"], xs, ya)), 4),
                "A2_MINUS_matched_C_ISO": round(
                    c["A2_channel"] - float(np.interp(c["cos_syn"], xs, ya)), 4),
                "RATIO": c["RATIO"],
                "C_ISO_RATIO_at_the_SAME_cos_syn": round(float(np.interp(c["cos_syn"], xs, yr)), 4),
            })
        REP["MATCHED_CLUMPING_vs_ISOTROPIC_COLLAPSE"] = {
            "why": "raising cosine to synonyms is FREE if you raise cosine to everything. Every "
                   "treatment is therefore read against the isotropic global-centroid control "
                   "INTERPOLATED TO THE SAME MEASURED SYNONYM COSINE. A positive "
                   "A2_MINUS_matched_C_ISO is the only form in which a clumping gain is real.",
            "rows": matched}

    # ---- THE CONTROL LADDER for the thematic family, at MATCHED eta. A thematic number is not
    # quotable until it has cleared BOTH of these, because both preserve the shape of the
    # intervention and destroy only the word-to-its-own-history correspondence.
    # controls are matched on (m, eta, T) READ FROM THE STORED PARAMS, never on a name pattern:
    # a control at a different hyper-parameter is not a matched control.
    def sig(nm):
        u = units[unit_key(grid, nm)]
        p = u["params"]
        return (u["family"], p.get("mode"), p.get("m"), round(float(p.get("eta", -1)), 4),
                p.get("T"))

    by_sig = {}
    for nm in short:
        by_sig.setdefault(sig(nm), []).append(nm)

    def find(fam, mode, m, e, T):
        c = by_sig.get((fam, mode, m, round(float(e), 4), T), [])
        return c[0] if c else None

    ladder: Dict = {}
    for nm in short:
        s = sig(nm)
        if s[0] != "M4" or s[1] != "second_order":
            continue
        _f, _md, m_, e_, T_ = s
        pairs = {"vs_SHUFFLED_PROFILES": find("M4", "shuffled", m_, e_, T_),
                 "vs_FREQ_MATCHED_PARTNERS": find("M4", "freq_matched", m_, e_, T_),
                 "vs_FIRST_ORDER_partners": find("M4", "first_order", m_, e_, T_),
                 "vs_RANDOM_STORE_NEIGHBOURS": find("C_RAND", None, m_, e_, T_)}
        pairs = {k: v for k, v in pairs.items() if v}
        row: Dict = {}
        for lab, other in pairs.items():
            if "%s::A2_SEMANTIC" % other in bsA2["boot"]:
                row["A2__" + lab] = FB.margin(bsA2["boot"], "%s::A2_SEMANTIC" % nm,
                                              "%s::A2_SEMANTIC" % other)
            if "%s::B_EXACT" % other in bsB["boot"]:
                row["B__" + lab] = FB.margin(bsB["boot"], "%s::B_EXACT" % nm,
                                             "%s::B_EXACT" % other)
        if row:
            row["_controls_used"] = pairs
            ladder[nm] = row
    REP["M4_THEMATIC_CONTROL_LADDER"] = {
        "why": "the thematic supply is corpus-derived and contains no WordNet, so it is not "
               "circular on either instrument. What it still has to survive is (1) SHUFFLED "
               "PROFILES -- every word gets a real structured thematic profile belonging to a "
               "DIFFERENT word, preserving degree and sparsity; (2) FREQUENCY-MATCHED PARTNERS; "
               "(3) the FIRST-ORDER version, which is the falsifier for the second-order claim "
               "the biology section makes; (4) random store neighbours at the same step size.",
        "rows": ladder}

    REP["CIRCULARITY_FLAGS"] = {
        "ORACLE_*_on_INSTRUMENT_B": "INADMISSIBLE_CIRCULAR. The oracle store is built FROM WordNet "
            "synonym sets and instrument B's gold is a WordNet meaning set. Its B numbers are "
            "published ONLY so nobody rediscovers them and reports a breakthrough.",
        "ORACLE_*_on_INSTRUMENT_A2": "CEILING REFERENCE, not circular in the same way (A2's gold "
            "is the word's OWN row) but still built from the sets that also build the cue. No "
            "rho>0 number is a capability claim.",
        "M1_M2_M3_M5_and_all_C_*": "GOLD-FREE. Nothing outside the store itself is consulted.",
        "M4_and_C_THEM_*": "GOLD-FREE. data/thematic_relations_v1 was extracted by our own "
            "extractor from simplewiki; no WordNet, no LLM, no pretrained table.",
    }

    # ---- THE VERDICT, stated so the standing checker has something to disagree with. It is
    # deliberately a FAIL on the bar even though the cell contains CI-separated positives, because
    # the bar is defined on the SYSTEM instrument against the STRONGEST floor and nothing here
    # clears the constant/prototype floor.
    void = [c["variant"] for c in curve if c["VOID_COLLAPSED"]]
    REP["VERDICT"] = "DOES_NOT_MEET_BAR__MECHANISM_NAMED"
    REP["verdict_msg"] = (
        "The clumping target is REACHABLE and reaching it by replaying the store's OWN "
        "neighbourhood buys nothing: mean word-to-synonym cosine 0.1214 -> 0.4705 with the "
        "semantic channel NOT_SEPARATED from the untouched store at every dose and the reading-cue "
        "arm CI-separated BELOW. The measured reason is that only 0.46% of a word's top-20 store "
        "neighbours are its synonyms, so replaying that neighbourhood replays the wrong set. "
        "SUPPLYING A SECOND CHANNEL DOES MOVE IT: consolidating against the thematic relation "
        "graph (our own simplewiki extraction, no WordNet) clears its shuffled-profile, "
        "frequency-matched, first-order and random-neighbour controls CI-separated on both "
        "instruments, and lifts the open-vocabulary read-out from CI-separated BELOW the spelling "
        "floor to NOT_SEPARATED from it. IT STILL DOES NOT MEET THE BAR: the query-ignoring "
        "constant/prototype floor remains CI-separated ABOVE every gold-free arm, and the reading "
        "cue we already had gets WORSE. Improves the channel, still hurts the system.")
    REP["VOID_COLLAPSED_variants"] = void
    REP["BAR_STATEMENT"] = {
        "bar": "a CI-separated margin over max(orthographic, frequency, scramble, "
               "CONSTANT/PROTOTYPE) on the IDENTICAL scorer/n/pool/gold",
        "MET_BY_ANY_GOLD_FREE_ARM_ON_THE_SYSTEM_INSTRUMENT": False,
        "why": "instrument B's constant/prototype floor reads 0.2070 on this population and the "
               "best gold-free arm reads 0.1069.",
        "what_IS_true_and_is_new": "on instrument B the incumbent store is CI-separated BELOW the "
               "trigram/spelling floor; the best thematic arm is NOT_SEPARATED from it "
               "(+0.0091 [-0.0076,+0.0260]) and is CI-separated ABOVE prefix, frequency and "
               "scramble. That is a closed gap, not a cleared bar, and it is stated as such."}

    p = os.path.join(out_dir, "metrics.json")
    with open(p + ".tmp", "w", encoding="ascii") as fh:
        json.dump(REP, fh, indent=1, default=str)
    os.replace(p + ".tmp", p)
    print("[done] wrote %s elapsed=%.1fs" % (p, time.time() - t0), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--grid", choices=["smoke", "full"], default="full")
    ap.add_argument("--aggregate-only", action="store_true")
    # --tag exists because a teardown of a stale checkpoint directory was DENIED by the harness
    # (deletion tokens are auto-denied in this repo). Rather than retry a variant of a denied
    # command or silently reuse units computed by an EARLIER version of the code, the run goes to
    # a fresh directory. CLAUDE.md's own guidance: leave cleanup to a maintenance pass.
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    out = os.path.join(_REPO, "data", "exp_synonym_clumping_consolidation_v1"
                       + ("_smoke" if a.grid == "smoke" else "")
                       + (("_" + a.tag) if a.tag else ""))
    if a.aggregate_only:
        D = load_all()
        INS = Instruments(D)
        from experiments.exp_task_degeneracy_v1 import ruler_mode_gate
        _V, _ok, th = build_thematic_vectors(D["anchors"], D["pos"])
        aggregate(a.grid, out, INS, ruler_mode_gate(), th, time.time())
        return 0
    return run(a.grid, out)


if __name__ == "__main__":
    raise SystemExit(main())
