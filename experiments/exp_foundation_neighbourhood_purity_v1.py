"""FOUNDATION NEIGHBOURHOOD PURITY -- is PURITY the lever, and does any foundation clear the floor?

THE DEFINING MEASUREMENT THIS CELL IS BUILT ON (b84417941, reproduced here as a regression gate):
  ONLY 0.46% OF A WORD'S TOP-20 NEIGHBOURS IN OUR STORE ARE ITS SYNONYMS.
Our store is a co-occurrence bag and co-occurrence neighbours are not meaning neighbours. Any
mechanism that reinforces, re-weights, completes from or replays the store's own neighbourhoods is
operating on a set that is 99.5% wrong. Hebbian replay of the store's own geometry REACHES the
clumping target (synonym cosine 0.1214 -> 0.4705) and buys NOTHING; consolidating against a SECOND
channel (our thematic relation graph) raises replay-partner purity 4.4x and more than doubles the
open-vocabulary read-out 0.0462 -> 0.1069. Still short: the query-ignoring constant/prototype floor
sits at 0.2070, CI-separated ABOVE.

WHAT THIS CELL ADDS, AND IT IS TWO SEPARATE THINGS.
 (1) PURITY AS THE PRIMARY QUANTITY, not as a diagnostic. Every foundation is scored on ONE
     instrument and reported as a point on a RETRIEVAL-vs-PURITY curve. If retrieval tracks purity
     across families that raise purity by DIFFERENT means, purity is the control variable and can
     be optimised directly, scoring any future supply source with one cheap statistic. If it does
     not, purity was a correlate and the report says so plainly.
 (2) STATIC OFFLINE-BUILT FOUNDATIONS ARE NOW ADMISSIBLE AS AN INGREDIENT (owner ruling, BOARD Q3,
     2026-08-16, verbatim): "We can build a foundation in whatever way is most efficient. the brain
     began with hundreds of millions of years of evolution instilling a foundation. we can build
     that foundation however we want, as long as it is a strong foundation, and the operation is
     not llm". THE INVARIANT IS UNCHANGED AND ABSOLUTE: NO LLM IN THE OPERATIONAL FLOW. Every
     table used here is a STATIC FILE READ OFF DISK at build time. Nothing calls a model at
     inference. A FOUNDATION DECISION IS NOT A RESULT: if a static asset wins, that is a statement
     about the INGREDIENT, and it is labelled that way throughout.

------------------------------------------------------------------------------------------------
STEP 1 -- THE BIOLOGY. WHICH STRUCTURE, AND WHICH PART IS OURS.
------------------------------------------------------------------------------------------------
BRAIN STRUCTURE: the VENTRAL / LATERAL TEMPORAL SEMANTIC MAP -- the cortical store whose
  neighbourhood relation IS meaning. [PINNED] Huth 2012 Neuron / 2016 Nature: related categories
  occupy neighbouring cortical territory, a smooth continuous semantic map. THAT IS THE 0.46% GAP
  STATED AS ANATOMY: cortical semantic neighbourhoods are organised by MEANING; ours are organised
  by TEXTUAL ADJACENCY. This is a claim about the STORE, not about a mechanism operating on it,
  which is why this cell changes the store and holds every mechanism fixed.
[PINNED] WORD FORM AND WORD MEANING ARE SEPARATE SYSTEMS (VWFA vs anterior temporal hub). A
  spelling-derived code is a FORM code. The orthographic floor is therefore a FORM channel and a
  foundation that beats it has done something a form channel cannot.
[PINNED] TWO RELATIONAL HUBS: taxonomic (anterior temporal) and thematic (temporo-parietal),
  dissociated by lesion [Schwartz 2011; Mirman 2017]. Our thematic arm is the second hub and is
  carried here UNCHANGED as the incumbent best, so the static assets are compared against the best
  thing we own rather than against the weakest.
[PINNED] EVOLUTION INSTALLED A PRIOR. A human infant does not derive its semantic organisation
  from its own reading. This is the owner's argument and it is the stronger brain argument: an
  offline-built static foundation is the analogue of an inherited prior, and refusing it held the
  substrate to a standard the brain itself does not meet.
[OURS -- INVENTION UNDER TEST, stated as invention, never as pinned]
  - that a 300-dim static distributional table is an acceptable stand-in for an inherited prior.
    The brain's prior is not a lookup table of word vectors. This is the cheapest admissible
    version and it is labelled as such.
  - the CONCATENATION FUSION [sqrt(1-w)*ours | sqrt(w)*static] as the model of two cortical
    channels contributing to one similarity. The brain does not concatenate blocks; it has
    convergent projections. What the algebra buys is exactness: cosine in the fused space is
    EXACTLY (1-w)*cos_ours + w*cos_static on covered pairs, so w is a clean single knob and the
    w=0 endpoint MUST reproduce the incumbent -- a regression gate at every step of the ladder.
  - the replay operator (move each row toward a sharpened weighted mean of its m supply
    neighbours), reused UNCHANGED from the thematic cell so that SUPPLY is the only variable.
[OURS, NOT BRAIN-MOTIVATED AT ALL] the exhaustive cosine argmax read-out; the scramble / shuffle /
  frequency-matched / oracle arms, which are MEASUREMENT INSTRUMENTS and never proposed
  representations.
SHELVE / REVIVAL CRITERION, BRAIN-FRAMED: if a foundation raises purity and retrieval does NOT
  follow, the diverging element is that a SIMILARITY NEIGHBOURHOOD is not an ADDRESS -- the
  cortical map is read out by an addressed hippocampal circuit, and we read it out by exhaustive
  cosine argmax. Revive the purity lever the moment an addressed read-out exists. If retrieval
  DOES follow purity, the shelved replay operator (which failed on a 0.46%-pure neighbourhood) is
  revived UNCHANGED, because the operator is not what failed.

------------------------------------------------------------------------------------------------
STEP 2 -- ENUMERATED FROM DISK, RECONCILED TO THE REGISTRY, VERIFIED BY RUNTIME
(scratch/foundation_purity/runtime_verify_part{1,2}.json; six module names have been caught lying
in two days, so nothing here is trusted by name or docstring)
------------------------------------------------------------------------------------------------
  data/gensim_cache/glove-wiki-gigaword-300      LOADED. 400,000 words, 300 dim, anchor coverage
                                                 98.60%, cos(king,queen)=0.6336 vs
                                                 cos(king,banana)=0.0666.
  data/gensim_cache/word2vec-google-news-300     LOADED (top 600k). coverage 96.19%.
  data/gensim_cache/fasttext-wiki-news-subwords  LOADED (top 600k). coverage 98.96%. NOTE the
                                                 measured caveat: cos(king,banana)=0.3231, i.e.
                                                 this table's similarities are inflated by
                                                 SUBWORD overlap, which is a FORM channel leaking
                                                 into a meaning table. Reported, not hidden.
  data/cskg_foundation_v1                        16 edge shards, records
                                                 {subject, relation, obj, source, trust, ...}.
                                                 SOURCE-FILTERED: every edge whose source names
                                                 WordNet is DROPPED, because instrument B's gold
                                                 is a WordNet meaning set and an unfiltered CSKG
                                                 foundation would be partly circular.
  experiments.exp_synonym_clumping_consolidation_v1   REUSED WHOLE: load_all, Instruments,
                                                 measure_geometry, topm_neighbours,
                                                 m1_shared_context_replay, c_iso_collapse,
                                                 thematic_neighbourhood, m4_replay_from_
                                                 neighbourhood, oracle_synonym_shrink. Reusing the
                                                 instrument is what makes 0.0462 / 0.1069 / 0.2070
                                                 directly comparable instead of carried.
  tools.floor_battery                            the ruler. Verified in-session by a PLANTED
                                                 ANSWER reading exactly 1.0.
  experiments.exp_task_degeneracy_v1.ruler_mode_gate  imported and CALLED. This cell's flag is
                                                 --grid, never --smoke.
  hdlab.grounded_similarity                      NEVER IMPORTED. Not used as a scorer anywhere.
  RUNTIME FACT THAT MAKES THE CROSS-SPACE COMPARISON POSSIBLE AT ALL: Q_exact IS THE WORD'S OWN
  STORE ROW (cos 1.000000, min 1.000000, on all 500 checked). So instrument B's exact-key arm is
  "rank all anchors by similarity to this word's own representation, gold = its WordNet meaning
  set, itself and its morphological variants excluded" -- which is defined NATIVELY in ANY vector
  space. Without that fact a foundation in a different space could not be scored on instrument B
  at all without a learned projection.

------------------------------------------------------------------------------------------------
PRE-REGISTRATION
------------------------------------------------------------------------------------------------
REGRESSION GATE, read before anything else. The incumbent store must reproduce: store top-20
  synonym purity 0.0046 (SAME estimator, SAME seed as the landed run), A2 gated-k3 semantic
  channel 0.2417, A1 sentence-cue self-recovery 0.0711, instrument-B exact-key 0.0462, B floors
  0.0978 / 0.0833 / 0.0233 / 0.2070 / 0.0161, PR_unit 171.16.
THE TWO EXACT-KEY DEFINITIONS ARE KEPT APART AND NEVER MIXED.
  B_EXACT_KEY_FIXEDCUE  cue = the word's ORIGINAL profile, pool = the variant store. This is the
                        landed definition and the one 0.1069 was measured under. Defined ONLY for
                        variants that live in our 256-dim space.
  B_EXACT_KEY_NATIVE    cue = the word's OWN ROW IN THE VARIANT STORE. Defined for EVERY
                        foundation, and the ONLY cross-foundation column. On the INCUMBENT store
                        the two are IDENTICAL BY CONSTRUCTION and the self-test asserts it to
                        machine precision. On a consolidated store they differ, both are printed,
                        and no number is carried between them.
VALIDITY, read before ANY treatment number. KA_NATIVE (query = the target's own row in the variant
  store) >= 0.95 and DOUBLES AS THE COLLAPSE DETECTOR. NULL (the semantic cue built for a randomly
  chosen OTHER word, identical gate) at the gate's chance rate. They fail independently: KA plants
  the answer, NULL permutes the cue-to-item assignment.
THE MANDATORY CONTROLS.
  - mean cosine to FREQUENCY-MATCHED NON-SYNONYMS reported beside mean cosine to synonyms for
    every foundation, plus the RATIO. A foundation that raises both equally has achieved nothing.
  - PARTICIPATION RATIO for every foundation. The last mechanism collapsed it 171 -> 31 while
    appearing to succeed.
  - the SHUFFLED-PROFILE control at matched hyper-parameters for every supply arm, and the
    SHUFFLED-TABLE control (the anchor -> static-row assignment permuted) at every fusion weight.
    The shuffled table has the IDENTICAL geometry, degree distribution and norm structure; only
    the correspondence between a word and its own row is destroyed.
  - the RANDOM-NEIGHBOUR and FREQUENCY-MATCHED-NEIGHBOUR controls for the supply family.
  - the ISOTROPIC global-centroid arm, which reaches cosine 0.99 with the channel going DOWN, as
    the standing proof that free clumping is worth less than nothing.
THE BAR: a CI-separated margin over max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE, CONSTANT/PROTOTYPE) on
  the IDENTICAL scorer / n / pool / gold, paired bootstrap, 10,000 draws, never a bare number. The
  store-dependent floors (constant/prototype, scramble) are recomputed FROM EACH FOUNDATION, and
  the incumbent's 0.2070 is additionally carried as a fixed reference; the BINDING floor is the
  max of the two. Tie conventions reported BOTH ways for every headline arm.
REGIMES REPORTED SEPARATELY: exact-key (available for every foundation) and partial-cue (the real
  one; available only where the corpus-side sentence cue can be expressed, which is our 256-dim
  space and the fused space with a zero static block). PREDICTION WRITTEN IN ADVANCE: the sentence
  cue has NO static component, so the fused reading-cue arm is expected to be FLAT in w; if it
  moves it moved through the coverage artifact, not through meaning.
PROGRESS LOGGING: every variant prints a flushed line. Expected wall time > 1800s at --grid full.
------------------------------------------------------------------------------------------------
ASCII only. No LLM in any path. Writes only to its own output dir. data/foundation/** never opened.
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
from typing import Dict, List, Optional, Sequence, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

import numpy as np  # noqa: E402

import tools.floor_battery as FB  # noqa: E402
import experiments.exp_synonym_clumping_consolidation_v1 as SC  # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

l2n = SC.l2n
topm = SC.topm_neighbours

MASTER_SEED = 20260816
N_BOOT = 10000
PURITY_SEED = MASTER_SEED + 77          # the landed purity seed, so 0.0046 must reproduce
PURITY_SAMPLE = 1500

GENSIM = os.path.join(_REPO, "data", "gensim_cache")
CSKG = os.path.join(_REPO, "data", "cskg_foundation_v1")

TABLES = {
    "GLOVE": ("glove-wiki-gigaword-300", "glove-wiki-gigaword-300.gz", False, None),
    "W2V": ("word2vec-google-news-300", "word2vec-google-news-300.gz", True, 600000),
    "FASTTEXT": ("fasttext-wiki-news-subwords-300", "fasttext-wiki-news-subwords-300.gz",
                 False, 600000),
}

LANDED = {"STORE_top20_synonym_purity": 0.0046, "A2_SEMANTIC_gated": 0.2417,
          "A1_SENTENCE_full_pool": 0.0711, "B_EXACT_KEY": 0.0462,
          "B_F1_TRIGRAM_ONLY": 0.0978, "B_F2_PREFIX_ONLY": 0.0833, "B_F3_FREQUENCY": 0.0233,
          "B_F4_CONSTANT_PROTOTYPE": 0.2070, "B_F5_SCRAMBLE": 0.0161,
          "PR_unit_store": 171.16, "THEMATIC_m5_B": 0.1069, "THEMATIC_m5_A2": 0.2795}
KA_CEILING_MIN = 0.95


# =============================================================================================
# PURITY -- the primary quantity of this cell
# =============================================================================================
def purity_of_store(S: np.ndarray, syn: Dict[int, np.ndarray], ks: Sequence[int] = (1, 20, 50),
                    sample: int = PURITY_SAMPLE, seed: int = PURITY_SEED) -> Dict[str, Dict]:
    """What fraction of a word's top-k neighbours IN THIS FOUNDATION are its synonyms.

    Identical estimator and identical seed to the landed store measurement, so the incumbent must
    reproduce 0.0046 exactly. Words whose row is all-zero (a foundation that does not cover them)
    are excluded from the SAMPLED SET but remain eligible as anybody's neighbour -- a zero row can
    never be a top-k neighbour of anything, which is the honest treatment of a coverage gap. The
    neighbour list is computed ONCE at max(ks) and the smaller k are its prefixes.
    """
    Sn = l2n(S)
    kmax = int(max(ks))
    idx, _v = topm(Sn, kmax)
    rs = np.random.default_rng(seed)
    live = np.flatnonzero(np.linalg.norm(Sn, axis=1) > 1e-6)
    sub = live if live.size <= sample else np.sort(rs.choice(live, sample, replace=False))
    out: Dict[str, Dict] = {}
    for k in ks:
        hit = tot = anyh = nw = 0
        for i in sub:
            mm = syn.get(int(i))
            if mm is None or mm.size == 0:
                continue
            nw += 1
            ss = set(mm.tolist())
            h = sum(1 for j in idx[i, :k].tolist() if j in ss)
            hit += h
            tot += k
            anyh += 1 if h else 0
        out["top%d" % k] = {"k": int(k), "n_words_scored": nw,
                            "PURITY": round(hit / max(tot, 1), 5),
                            "frac_words_with_a_synonym_in_topk": round(anyh / max(nw, 1), 4)}
    return out


def purity_of_supply(idx: np.ndarray, dead: np.ndarray, syn: Dict[int, np.ndarray],
                     sample: int = PURITY_SAMPLE, seed: int = PURITY_SEED) -> Dict:
    """The SAME statistic for a REPLAY-PARTNER set rather than for the store's own neighbourhood.
    This is the number the thematic cell moved 0.0046 -> 0.0203."""
    rs = np.random.default_rng(seed)
    live = np.flatnonzero(~dead)
    sub = live if live.size <= sample else np.sort(rs.choice(live, sample, replace=False))
    hit = tot = anyh = nw = 0
    for i in sub:
        mm = syn.get(int(i))
        if mm is None or mm.size == 0:
            continue
        nw += 1
        ss = set(mm.tolist())
        h = sum(1 for j in idx[i].tolist() if j in ss)
        hit += h
        tot += idx.shape[1]
        anyh += 1 if h else 0
    return {"n_words_scored": nw, "SUPPLY_PURITY": round(hit / max(tot, 1), 5),
            "frac_words_with_a_synonym_partner": round(anyh / max(nw, 1), 4)}


# =============================================================================================
# THE INSTRUMENT -- identical scorer / n / pool / gold, extended NATIVELY to any vector space
# =============================================================================================
class NativeInstruments(SC.Instruments):
    """SC.Instruments with a cross-space evaluation. Every arm below is defined by the SAME gate,
    the SAME gold and the SAME scorer as the landed cell; the ONLY change is that the exact-key
    cue is taken from the variant store itself, which is provably identical on the incumbent."""

    _oracle_const: Optional[np.ndarray] = None

    def hit3(self, Sc: np.ndarray, elig: np.ndarray, gold: np.ndarray) -> Dict[str, np.ndarray]:
        return FB.hit_at_1_both_tie_conventions(Sc, elig, gold)

    def gold_sets(self) -> List[np.ndarray]:
        return [np.flatnonzero(self.goldB[:, c]) for c in range(self.n_i)]

    def evaluate_foundation(self, S: np.ndarray, qmap, qmap2=None
                            ) -> Tuple[Dict[str, np.ndarray], Dict, Dict]:
        """qmap: callable mapping our 256-dim corpus-side cue matrix into this foundation's space,
        or None when the corpus cue cannot be expressed there (a pure static table).
        qmap2: the TWO-STAGE cue -- same corpus cue, but allowed to REACH the new channel through
        the store (see build_variant). Optional; None for every foundation where it is undefined."""
        D = self.D
        H: Dict[str, np.ndarray] = {}
        TIE: Dict[str, Dict] = {}
        DIAG: Dict[str, float] = {}
        Qsem = self.semantic_cue(S)

        def put(name, Sc, elig, gold, tie=False):
            r = self.hit3(Sc, elig, gold)
            H[name] = np.asarray(r["hit_exp"], dtype=np.float64)
            if tie:
                TIE[name] = {"opt": r["hit_opt"], "cons": r["hit_cons"], "tie": r["tie_mass"]}

        # ---------- VALIDITY FIRST. Nothing below is read until these are read.
        put("KA_NATIVE_own_row", self.score(S, S[self.items]), self.eligA, self.goldA)
        put("NULL_semantic_cue_for_a_DIFFERENT_word__gated", self.score(S, Qsem[self.permNULL]),
            self.gate, self.goldA)

        # ---------- A2: THE CHANNEL (gate k=3, semantic drive), native in any space.
        put("A2_SEMANTIC_gated", self.score(S, Qsem), self.gate, self.goldA, tie=True)
        rr = np.random.default_rng(MASTER_SEED + 9)
        put("A2_F_RANDOM_WITHIN_GATE", rr.random((self.n_a, self.n_i)).astype(np.float32),
            self.gate, self.goldA)
        put("A2_F_FREQUENCY", FB.as_constant_matrix(D["fq"], self.n_i), self.gate, self.goldA)
        put("A2_F_CONSTANT_PROTOTYPE",
            FB.as_constant_matrix(FB.constant_prototype_floor(S, self.mat_ok), self.n_i),
            self.gate, self.goldA, tie=True)
        put("A2_F_SCRAMBLE", self.score(l2n(FB.scramble_null(S, MASTER_SEED)), Qsem),
            self.gate, self.goldA)

        # ---------- B: the standing open-vocabulary WordNet read-out, EXACT-KEY regime, native.
        Sc_b = self.score(S, S[self.items])
        put("B_EXACT_KEY_NATIVE", Sc_b, self.eligB, self.goldB, tie=True)
        put("B_F1_TRIGRAM_ONLY", (D["t_mat"] @ D["Tq"][self.rows].T).astype(np.float32),
            self.eligB, self.goldB, tie=True)
        put("B_F2_PREFIX_ONLY", D["Pq"][self.rows].T.astype(np.float32),
            self.eligB, self.goldB, tie=True)
        put("B_F3_FREQUENCY", FB.as_constant_matrix(D["fq"], self.n_i), self.eligB, self.goldB)
        put("B_F4_CONSTANT_PROTOTYPE",
            FB.as_constant_matrix(FB.constant_prototype_floor(S, self.mat_ok), self.n_i),
            self.eligB, self.goldB, tie=True)
        SS = l2n(FB.scramble_null(S, MASTER_SEED))
        put("B_F5_SCRAMBLE_NATIVE", self.score(SS, S[self.items]), self.eligB, self.goldB)
        # NOT A FLOOR AND LABELLED SO: the CEILING of the query-ignoring family, FITTED ON THE GOLD
        # LABELS (gold-degree ranking). If a foundation does not beat this, its win is inside what
        # a constant answer can achieve when it is allowed to see the answer key.
        if self._oracle_const is None:
            self._oracle_const = FB.oracle_constant_scores(self.n_a, self.gold_sets())
        put("B_ORACLE_CONSTANT_GOLD_DEGREE_not_a_floor",
            FB.as_constant_matrix(self._oracle_const, self.n_i), self.eligB, self.goldB, tie=True)

        # ---------- arms that need the CORPUS-SIDE cue. Only where it can be expressed.
        if qmap is not None:
            Qp = qmap(D["Q_part"][self.rows])
            Qe = qmap(D["Q_exact"][self.rows])
            put("A1_SENTENCE_full_pool", self.score(S, Qp), self.eligA, self.goldA)
            put("A1_F_CONSTANT_PROTOTYPE",
                FB.as_constant_matrix(FB.constant_prototype_floor(S, self.mat_ok), self.n_i),
                self.eligA, self.goldA)
            put("A1_F_FREQUENCY", FB.as_constant_matrix(D["fq"], self.n_i),
                self.eligA, self.goldA)
            put("A2_SENTENCE_gated", self.score(S, Qp), self.gate, self.goldA)
            put("B_EXACT_KEY_FIXEDCUE", self.score(S, Qe), self.eligB, self.goldB, tie=True)
            put("B_PARTIAL_CUE_sentence", self.score(S, Qp), self.eligB, self.goldB, tie=True)
            # WHY the corpus cue does or does not follow the store: does the target's row still sit
            # near the cue that is supposed to find it? Measured, not argued.
            qq = l2n(Qp)
            DIAG["cue_to_target_cos_SENTENCE"] = round(
                float(np.mean(np.sum(S[self.items] * qq, axis=1))), 4)
        if qmap2 is not None:
            Q2 = qmap2(D["Q_part"][self.rows])
            put("A1_SENTENCE_TWOSTAGE_full_pool", self.score(S, Q2), self.eligA, self.goldA)
            put("B_PARTIAL_CUE_TWOSTAGE", self.score(S, Q2), self.eligB, self.goldB, tie=True)
            DIAG["cue_to_target_cos_SENTENCE_TWOSTAGE"] = round(
                float(np.mean(np.sum(S[self.items] * l2n(Q2), axis=1))), 4)
        return H, {k: {kk: round(float(np.mean(vv[self.maskA2])), 4) for kk, vv in v.items()}
                   for k, v in TIE.items()}, DIAG


# =============================================================================================
# THE FOUNDATIONS
# =============================================================================================
def load_table(name: str, anchors: Sequence[str], cache_dir: str) -> Tuple[np.ndarray, np.ndarray,
                                                                          Dict]:
    """Load a STATIC table off disk and project it onto our anchor list. Cached inside the cell's
    OWN output dir (never scratch/, which is cleared) so a resumed run does not pay 100-160s
    again. NO NETWORK: the .gz path is opened directly. NO LLM."""
    sub, fn, binary, limit = TABLES[name]
    cpath = os.path.join(cache_dir, "table_%s.npz" % name)
    if os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=True)
        return (np.asarray(z["X"], dtype=np.float32), np.asarray(z["hit"], dtype=bool),
                json.loads(str(z["stats"])))
    from gensim.models import KeyedVectors
    p = os.path.join(GENSIM, sub, fn)
    t = time.time()
    kv = KeyedVectors.load_word2vec_format(p, binary=binary, limit=limit)
    dim = int(kv.vector_size)
    X = np.zeros((len(anchors), dim), dtype=np.float32)
    hit = np.zeros(len(anchors), dtype=bool)
    for i, w in enumerate(anchors):
        for cand in (w, w.capitalize(), w.upper()):
            if cand in kv.key_to_index:
                X[i] = kv[cand]
                hit[i] = True
                break
    stats = {"asset": p, "vocab": int(len(kv.key_to_index)), "dim": dim, "limit": limit,
             "anchor_coverage": round(float(hit.mean()), 4), "n_covered": int(hit.sum()),
             "load_s": round(time.time() - t, 1),
             "SANITY_cos_king_queen": round(float(kv.similarity("king", "queen")), 4),
             "SANITY_cos_king_banana": round(float(kv.similarity("king", "banana")), 4),
             "IS_A_STATIC_FILE_READ_AT_BUILD_TIME_NOT_A_MODEL_CALLED_AT_INFERENCE": True}
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cpath, X=X, hit=hit, stats=json.dumps(stats))
    del kv
    return X, hit, stats


def build_cskg_profiles(anchors: Sequence[str], pos: Dict[str, int]) -> Tuple[np.ndarray, Dict]:
    """CSKG as a SUPPLY channel: a word's profile is its CSKG neighbours. WordNet-sourced edges are
    DROPPED because instrument B's gold is a WordNet meaning set."""
    n = len(anchors)
    V = np.zeros((n, n), dtype=np.float32)
    src_counts: Dict[str, int] = {}
    used = dropped_wn = 0
    for f in sorted(os.listdir(CSKG)):
        if not f.startswith("edges_shard"):
            continue
        with open(os.path.join(CSKG, f), "r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                s = str(r.get("source", "?"))
                src_counts[s] = src_counts.get(s, 0) + 1
                a = pos.get(str(r.get("subject", "")).lower())
                b = pos.get(str(r.get("obj", "")).lower())
                if a is None or b is None or a == b:
                    continue
                if "wn" in s.lower() or "wordnet" in s.lower():
                    dropped_wn += 1
                    continue
                V[a, b] += 1.0
                V[b, a] += 1.0
                used += 1
    ok = np.linalg.norm(V, axis=1) > 1e-9
    return V, {"source": "data/cskg_foundation_v1 (16 shards)", "edges_used": int(used),
               "edges_DROPPED_because_WORDNET_SOURCED": int(dropped_wn),
               "source_histogram": dict(sorted(src_counts.items(), key=lambda kv: -kv[1])[:12]),
               "n_anchors_with_a_cskg_profile": int(ok.sum())}


def fuse_multi(U: np.ndarray, Xs: Sequence[Tuple[np.ndarray, np.ndarray]], w: float
               ) -> np.ndarray:
    """The same fusion with SEVERAL static blocks sharing the weight w equally. Used only to put
    higher-purity GOLD-FREE points on the curve; it is not proposed as a representation."""
    blocks = [l2n(U) * np.float32(np.sqrt(max(0.0, 1.0 - w)))]
    for X, hit in Xs:
        B = l2n(X) * np.float32(np.sqrt(w / len(Xs)))
        B[~hit] = 0.0
        blocks.append(B)
    return l2n(np.concatenate(blocks, axis=1))


def two_stage_cue(Q: np.ndarray, U: np.ndarray, X: np.ndarray, hit: np.ndarray, w: float,
                  k: int = 5, beta: float = 3.0) -> np.ndarray:
    """THE CORPUS CUE, ALLOWED TO REACH THE STATIC CHANNEL THROUGH THE STORE.

    The reading cue is a context profile in OUR space, so in a fused store it can only address the
    ours-block: a foundation can improve the meaning geometry and the only cue we actually own
    cannot see it. This arm is the cheapest honest attempt to connect them: rank anchors by the
    cue in OUR space, then fill the static block with the sharpened weighted mean of the top-k
    anchors' STATIC rows. No gold is consulted at any point.

    [PINNED, loosely] a cortical form-to-lexical-to-semantic cascade: a sensory fragment activates
    lexical candidates and those candidates' semantic representations become available.
    [OURS -- INVENTION UNDER TEST] top-k over cosine with a sharpened weight is not a cascade, and
    it carries its own control: the identical construction over the SHUFFLED table.
    """
    Qo = l2n(Q)
    sims = Qo @ l2n(U).T
    idx = np.argpartition(-sims, k, axis=1)[:, :k]
    val = np.take_along_axis(sims, idx, axis=1)
    wt = np.maximum(val, 0.0) ** beta
    wt = wt / np.maximum(wt.sum(axis=1, keepdims=True), 1e-12)
    Xn = l2n(X).copy()
    Xn[~hit] = 0.0
    qs = np.einsum("ij,ijk->ik", wt.astype(np.float32), Xn[idx], optimize=True)
    return np.concatenate([Qo * np.float32(np.sqrt(max(0.0, 1.0 - w))),
                           l2n(qs) * np.float32(np.sqrt(w))], axis=1)


def fuse(U: np.ndarray, X: np.ndarray, hit: np.ndarray, w: float) -> np.ndarray:
    """[sqrt(1-w) * l2n(ours) | sqrt(w) * l2n(static)], rows renormalised.

    On a pair BOTH of which the table covers, cosine is EXACTLY (1-w)*cos_ours + w*cos_static (the
    self-test asserts it). An anchor the table does NOT cover keeps a zero static block, so after
    renormalisation it is a pure-ours unit vector: it is systematically less similar to covered
    anchors and therefore mildly penalised. That is a COVERAGE artifact, it is disclosed, and the
    covered-only subpopulation is reported beside the full one."""
    A = l2n(U) * np.float32(np.sqrt(max(0.0, 1.0 - w)))
    B = l2n(X) * np.float32(np.sqrt(w))
    B[~hit] = 0.0
    return l2n(np.concatenate([A, B], axis=1))


def build_variant(fam: str, p: Dict, base: np.ndarray, D: Dict, ASSET: Dict, log
                  ) -> Tuple[np.ndarray, Optional[object], Optional[object], Dict]:
    """Returns (store, qmap_or_None, qmap2_or_None, extra). qmap embeds our 256-dim corpus cue
    into the store's space; None means the corpus-side cue cannot be expressed there and those
    arms are NOT_APPLICABLE rather than zero. qmap2 is the TWO-STAGE cue, defined only where the
    plain cue cannot reach the new channel."""
    ident = (lambda Q: Q)
    n_us = base.shape[1]

    if fam == "REAL":
        return l2n(base), ident, None, {}
    if fam == "M1":
        return SC.m1_shared_context_replay(base, p["m"], p["eta"], p["T"], p["beta"], False,
                                           log), ident, None, {}
    if fam == "C_ISO":
        return SC.c_iso_collapse(base, p["beta"]), ident, None, {}
    if fam == "C_RAND":
        return SC.c_rand_replay(base, p["m"], p["eta"], p["T"], MASTER_SEED + 41), ident, None, {}
    if fam == "ORACLE":
        return SC.oracle_synonym_shrink(base, D["syn"], p["rho"]), ident, None, {
            "LABEL": "INADMISSIBLE_CIRCULAR -- built FROM the WordNet synonym sets that also build "
                     "the A2 cue and overlap instrument B's gold. A CEILING REFERENCE, never a "
                     "capability claim."}
    if fam == "SUPPLY":
        src = p["src"]
        V = ASSET["profiles"][src]
        idx, w, dead = SC.thematic_neighbourhood(V, p["m"], p["beta"], p["mode"],
                                                 MASTER_SEED + 71, D["fq"])
        ex = {"supply_source": src, "mode": p["mode"], "n_dead": int(dead.sum()),
              "supply_stats": ASSET["profile_stats"].get(src, {}),
              "SUPPLY_PURITY": purity_of_supply(idx, dead, D["syn"])}
        return (SC.m4_replay_from_neighbourhood(base, idx, w, dead, p["eta"], p["T"]),
                ident, None, ex)
    if fam == "FUSE_MULTI":
        Xs = [(ASSET["tables"][t][0], ASSET["tables"][t][1]) for t in p["tables"]]
        w = p["w"]
        S = fuse_multi(base, Xs, w)
        d_static = sum(x.shape[1] for x, _h in Xs)

        def qmapm(Q, _d=d_static):
            return np.concatenate([Q, np.zeros((Q.shape[0], _d), dtype=np.float32)], axis=1)

        return S, (qmapm if w < 1.0 else None), None, {
            "tables": list(p["tables"]), "w": w,
            "NOTE": "several static blocks sharing w equally. A GOLD-FREE high-purity point on the "
                    "curve, NOT a proposed representation."}
    if fam == "FUSE":
        X, hit, st = ASSET["tables"][p["table"]]
        if p.get("shuffled"):
            # THE DECISIVE CONTROL for the replacement family: the anchor -> static-row assignment
            # is permuted, so the table keeps its ENTIRE geometry, norm structure and coverage
            # count, and only the correspondence between a word and its own row is destroyed.
            # This is exactly FB.scramble_null, applied to the table and to its coverage mask with
            # THE SAME permutation so a row and its own coverage flag never come apart.
            perm = np.random.default_rng(MASTER_SEED + 5).permutation(X.shape[0])
            X, hit = X[perm], hit[perm]
        w = p["w"]
        S = fuse(base, X, hit, w)
        d_static = X.shape[1]

        def qmap(Q, _n=n_us, _d=d_static):
            return np.concatenate([Q, np.zeros((Q.shape[0], _d), dtype=np.float32)], axis=1)

        ex = {"table": p["table"], "w": w, "shuffled": bool(p.get("shuffled")),
              "table_stats": st, "coverage": round(float(hit.mean()), 4),
              "NOTE_on_the_corpus_cue": "the sentence cue has NO static component, so its query is "
                                        "embedded with a ZERO static block. PRE-REGISTERED "
                                        "PREDICTION: this arm is flat in w."}
        if w >= 1.0:
            # w=1 IS the pure static foundation: the ours-block is zeroed out entirely, so the
            # store is l2n(table) with a zero row wherever the table does not cover the anchor.
            ex["LABEL"] = ("FOUNDATION DECISION, NOT A RESULT -- at w=1 this is the INGREDIENT'S "
                           "score, not our mechanism's.")

        def qmap2(Q, _U=base, _X=X, _h=hit, _w=w):
            return two_stage_cue(Q, _U, _X, _h, _w)

        return S, (qmap if w < 1.0 else None), (qmap2 if 0.0 < w else None), ex
    raise ValueError("unknown family " + fam)


def variant_grid(grid: str) -> List[Tuple[str, str, Dict]]:
    V: List[Tuple[str, str, Dict]] = [("F00_INCUMBENT_OURS_COOCCURRENCE", "REAL", {})]
    small = grid == "smoke"
    B3 = 3.0
    # -- the store's OWN replay: raises synonym COSINE, does NOT raise purity. The off-curve
    #    points that decide whether purity or cosine is the variable.
    for e in ((0.70,) if small else (0.50, 0.70, 1.00)):
        V.append(("F01_OURS_M1REPLAY_eta%.2f" % e, "M1",
                  {"m": 20, "eta": e, "T": 1, "beta": B3}))
    for b in ((0.50,) if small else (0.30, 0.50)):
        V.append(("F02_OURS_C_ISO_beta%.2f" % b, "C_ISO", {"beta": b}))
    # -- the incumbent BEST: our own thematic hub, reproduced with its own control
    for m in ((5,) if small else (5, 20)):
        V.append(("F03_OURS_THEMATIC_m%d_eta0.50" % m, "SUPPLY",
                  {"src": "THEMATIC", "m": m, "eta": 0.50, "T": 1, "beta": B3,
                   "mode": "second_order"}))
    V.append(("F04_C_THEMATIC_SHUFFLED_m5_eta0.50", "SUPPLY",
              {"src": "THEMATIC", "m": 5, "eta": 0.50, "T": 1, "beta": B3, "mode": "shuffled"}))
    # -- SUPPLY from a static table: the SAME operator, the SAME space, only the supply changes
    for tb in (("GLOVE",) if small else ("GLOVE", "W2V", "FASTTEXT")):
        for m, e in (((5, 0.50),) if small else ((5, 0.50), (20, 0.50), (5, 0.90), (20, 0.90))):
            V.append(("F10_SUPPLY_%s_m%d_eta%.2f" % (tb, m, e), "SUPPLY",
                      {"src": tb, "m": m, "eta": e, "T": 1, "beta": B3, "mode": "second_order"}))
    for md in ("shuffled", "freq_matched"):
        V.append(("F11_C_SUPPLY_GLOVE_%s_m5_eta0.50" % md.upper(), "SUPPLY",
                  {"src": "GLOVE", "m": 5, "eta": 0.50, "T": 1, "beta": B3, "mode": md}))
    V.append(("F12_C_RAND_STORE_NEIGHBOURS_m5_eta0.50", "C_RAND", {"m": 5, "eta": 0.50, "T": 1}))
    if not small:
        V.append(("F13_SUPPLY_CSKG_m5_eta0.50", "SUPPLY",
                  {"src": "CSKG", "m": 5, "eta": 0.50, "T": 1, "beta": B3,
                   "mode": "second_order"}))
        V.append(("F14_C_SUPPLY_CSKG_SHUFFLED_m5_eta0.50", "SUPPLY",
                  {"src": "CSKG", "m": 5, "eta": 0.50, "T": 1, "beta": B3, "mode": "shuffled"}))
    # -- THE FUSION LADDER: one knob, one space, w=0 must reproduce the incumbent EXACTLY
    ws = (0.0, 0.50, 1.0) if small else (0.0, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0)
    for w in ws:
        V.append(("F20_FUSE_GLOVE_w%.2f" % w, "FUSE", {"table": "GLOVE", "w": w}))
    if not small:
        for w in (0.30, 0.50, 1.0):
            V.append(("F21_FUSE_W2V_w%.2f" % w, "FUSE", {"table": "W2V", "w": w}))
            V.append(("F22_FUSE_FASTTEXT_w%.2f" % w, "FUSE", {"table": "FASTTEXT", "w": w}))
    for w in ((0.50,) if small else (0.30, 0.50, 1.0)):
        V.append(("F23_C_FUSE_GLOVE_SHUFFLED_w%.2f" % w, "FUSE",
                  {"table": "GLOVE", "w": w, "shuffled": True}))
    if not small:
        for w in (0.50, 1.0):
            V.append(("F24_FUSE_ALL3_STATIC_w%.2f" % w, "FUSE_MULTI",
                      {"tables": ("GLOVE", "W2V", "FASTTEXT"), "w": w}))
    # -- the CIRCULAR ceiling, labelled
    for r in ((0.30,) if small else (0.30, 0.70)):
        V.append(("F30_ORACLE_WORDNET_CIRCULAR_rho%.2f" % r, "ORACLE", {"rho": r}))
    return V


# =============================================================================================
# SELF-TEST -- every claim the run leans on, asserted on data with a known answer
# =============================================================================================
def self_test() -> int:
    out: Dict = {}
    rng = np.random.default_rng(5)

    # T1 -- FUSION ALGEBRA. cosine in the fused space is EXACTLY the convex mixture, and w=0 is
    # the identity on the ours-kernel. This is what licenses w as a single clean knob.
    U = rng.normal(size=(60, 16)).astype(np.float32)
    X = rng.normal(size=(60, 12)).astype(np.float32)
    hit = np.ones(60, dtype=bool)
    Ku, Kx = l2n(U) @ l2n(U).T, l2n(X) @ l2n(X).T
    for w in (0.0, 0.25, 0.5, 1.0):
        F = fuse(U, X, hit, w)
        K = F @ F.T
        exp = (1.0 - w) * Ku + w * Kx
        assert np.abs(K - exp).max() < 2e-5, (w, float(np.abs(K - exp).max()))
    F0 = fuse(U, X, hit, 0.0)
    assert np.abs(F0 @ F0.T - Ku).max() < 2e-5
    # and an UNCOVERED anchor must fall back to pure-ours, not to noise
    h2 = hit.copy()
    h2[0] = False
    F = fuse(U, X, h2, 0.5)
    assert abs(float(np.dot(F[0], F[0])) - 1.0) < 1e-4
    assert np.abs(F[0, 16:]).max() == 0.0
    out["T1_fusion_algebra"] = "OK"

    # T2 -- THE PURITY ESTIMATOR, both ends. On a store where each word's synonyms ARE its top
    # neighbours it must read ~1.0; on a random store it must read ~0. An estimator that cannot
    # fail in one direction cannot support the curve this cell is built on.
    n, k = 300, 5
    syn = {i: np.array(sorted(set(range((i // 6) * 6, (i // 6) * 6 + 6)) - {i}), dtype=np.int64)
           for i in range(n)}
    cen = rng.normal(size=(n // 6, 40)).astype(np.float32)
    Sgood = l2n(np.repeat(cen, 6, axis=0) + 0.02 * rng.normal(size=(n, 40)).astype(np.float32))
    Srand = l2n(rng.normal(size=(n, 40)).astype(np.float32))
    pg = purity_of_store(Sgood, syn, ks=(k,), sample=n, seed=1)["top%d" % k]["PURITY"]
    pr = purity_of_store(Srand, syn, ks=(k,), sample=n, seed=1)["top%d" % k]["PURITY"]
    assert pg > 0.95, pg
    assert pr < 0.05, pr
    # a ZERO row can never be a top-k neighbour and is excluded from the sampled set
    Sz = Sgood.copy()
    Sz[0] = 0.0
    idx, _ = topm(l2n(Sz), k)
    assert 0 not in set(idx.ravel().tolist()), "a zero row was selected as a neighbour"
    out["T2_purity_estimator"] = {"planted_high": pg, "random": pr}

    # T3 -- THE COLLAPSE DETECTOR ACTUALLY FIRES. If a foundation makes rows identical the
    # known-answer arm MUST fall below the gate. Asserted, not assumed.
    elig = np.ones((40, 40), dtype=bool)
    gold = np.eye(40, dtype=bool)
    Scol = np.repeat(l2n(rng.normal(size=(1, 24)).astype(np.float32)), 40, axis=0)
    ka_col = float(np.mean(FB.hit_at_1_both_tie_conventions((Scol @ Scol.T).astype(np.float32),
                                                            elig, gold)["hit_exp"]))
    Sok = l2n(rng.normal(size=(40, 24)).astype(np.float32))
    ka_ok = float(np.mean(FB.hit_at_1_both_tie_conventions((Sok @ Sok.T).astype(np.float32),
                                                           elig, gold)["hit_exp"]))
    assert ka_col < KA_CEILING_MIN, ka_col          # a collapsed store MUST be caught
    assert ka_ok == 1.0, ka_ok                      # a healthy store MUST pass
    out["T3_collapse_detector"] = {"collapsed_KA": round(ka_col, 4), "healthy_KA": ka_ok}

    # T4 -- THE SUPPLY NEIGHBOURHOOD IS EXACT and its SHUFFLED control really destroys the
    # correspondence while preserving the shape.
    Vp = np.abs(rng.normal(size=(80, 80)).astype(np.float32))
    idx, w, dead = SC.thematic_neighbourhood(Vp, 4, 3.0, "second_order", 1, None)
    Kn = l2n(Vp) @ l2n(Vp).T
    np.fill_diagonal(Kn, -np.inf)
    ref = np.argsort(-Kn, axis=1)[:, :4]
    assert (idx == ref).all(), "top-m supply neighbours are not the exact argsort"
    syn2 = {i: np.array([j for j in ref[i]], dtype=np.int64) for i in range(80)}
    p_true = purity_of_supply(idx, dead, syn2, sample=80, seed=1)["SUPPLY_PURITY"]
    ish, wsh, dsh = SC.thematic_neighbourhood(Vp, 4, 3.0, "shuffled", 1, None)
    p_sh = purity_of_supply(ish, dsh, syn2, sample=80, seed=1)["SUPPLY_PURITY"]
    assert p_true == 1.0, p_true
    assert p_sh < 0.2, p_sh
    assert ish.shape == idx.shape
    out["T4_supply_neighbourhood"] = {"true": p_true, "shuffled": p_sh}

    # T5 -- THE RULER, on a planted answer, in this session.
    Sf = l2n(rng.normal(size=(200, 32)).astype(np.float32))
    r = FB.hit_at_1_both_tie_conventions((Sf @ Sf[:50].T).astype(np.float32),
                                         np.ones((200, 50), dtype=bool),
                                         np.eye(200, 50, dtype=bool))
    assert float(np.mean(r["hit_exp"])) == 1.0
    out["T5_ruler_planted_answer"] = 1.0

    # T6 -- the paired bootstrap says NOT_SEPARATED for identical arms and ABOVE for a planted
    # +0.10. A margin machine that cannot return NOT_SEPARATED is not a margin machine.
    a = (rng.random(1200) < 0.30).astype(np.float64)
    b = a.copy()
    c = np.clip(a + (rng.random(1200) < 0.10), 0, 1).astype(np.float64)
    bo = FB.paired_bootstrap_ci({"a": a, "b": b, "c": c}, np.ones(1200, dtype=bool), 2000, 3)
    assert FB.margin(bo["boot"], "a", "b")["band"] == "NOT_SEPARATED"
    assert FB.margin(bo["boot"], "c", "a")["band"] == "ABOVE"
    out["T6_bootstrap"] = "OK"

    # T7 -- ARMS MUST DIFFER: a shuffled static table is not the static table.
    Xs = FB.scramble_null(X, MASTER_SEED + 5)
    assert not np.allclose(Xs, X)
    out["T7_arms_differ"] = "OK"

    # T8 -- the ruler-mode gate is CALLED, and '--smoke' is never in argv (it silently swaps the
    # imported ruler; this cell's flag is --grid).
    from experiments.exp_task_degeneracy_v1 import ruler_mode_gate
    g = ruler_mode_gate()
    assert g.get("PASS") is True, g
    assert "--smoke" not in sys.argv, sys.argv
    out["T8_ruler_mode_gate"] = g

    print(json.dumps(out, indent=1, default=str), flush=True)
    print("SELFTEST_ALL_GROUPS_PASS", flush=True)
    return 0


# =============================================================================================
# RUN
# =============================================================================================
def run(grid: str, out_dir: str) -> int:
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    from experiments.exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()
    assert gate.get("PASS") is True, gate
    print("[gate] ruler_mode_gate %s" % json.dumps(gate), flush=True)

    D = SC.load_all()
    INS = NativeInstruments(D)
    base = D["mat"]
    n_a, n_i = INS.n_a, INS.n_i
    print("[load] n_anchors=%d n_items=%d maskA2=%d (%.1fs)"
          % (n_a, n_i, int(INS.maskA2.sum()), time.time() - t0), flush=True)

    # ---- THE BRIDGE THAT LICENSES EVERY CROSS-FOUNDATION NUMBER, asserted at runtime on the
    # incumbent store: the NATIVE exact-key arm and the LANDED fixed-cue arm are the same array.
    S0 = l2n(base)
    h_native = FB.hit_at_1_both_tie_conventions(INS.score(S0, S0[INS.items]),
                                                INS.eligB, INS.goldB)["hit_exp"]
    h_fixed = FB.hit_at_1_both_tie_conventions(INS.score(S0, D["Q_exact"][INS.rows]),
                                               INS.eligB, INS.goldB)["hit_exp"]
    dmax = float(np.abs(np.asarray(h_native) - np.asarray(h_fixed)).max())
    assert dmax == 0.0, "native and fixed-cue exact-key arms differ on the incumbent: %g" % dmax
    print("[bridge] B_EXACT_KEY_NATIVE == B_EXACT_KEY_FIXEDCUE on the incumbent, max|diff|=%g"
          % dmax, flush=True)

    # ---- assets, all STATIC FILES read at BUILD TIME
    ASSET: Dict = {"tables": {}, "profiles": {}, "profile_stats": {}}
    need = {"GLOVE"} if grid == "smoke" else {"GLOVE", "W2V", "FASTTEXT"}
    for tb in sorted(need):
        X, hit, st = load_table(tb, D["anchors"], out_dir)
        ASSET["tables"][tb] = (X, hit, st)
        ASSET["profiles"][tb] = X
        ASSET["profile_stats"][tb] = st
        print("[asset] %s %s" % (tb, json.dumps(st)), flush=True)
    Vth, _okth, th_stats = SC.build_thematic_vectors(D["anchors"], D["pos"])
    ASSET["profiles"]["THEMATIC"] = Vth
    ASSET["profile_stats"]["THEMATIC"] = th_stats
    print("[asset] THEMATIC %s" % json.dumps(th_stats), flush=True)
    if grid != "smoke":
        Vck, ck_stats = build_cskg_profiles(D["anchors"], D["pos"])
        ASSET["profiles"]["CSKG"] = Vck
        ASSET["profile_stats"]["CSKG"] = ck_stats
        print("[asset] CSKG %s" % json.dumps(ck_stats), flush=True)

    # ---- REGRESSION GATE on the defining statistic, same estimator, same seed
    p0 = purity_of_store(S0, D["syn"])
    print("[regression] INCUMBENT store purity = %s (landed top20 %.4f)"
          % (json.dumps(p0), LANDED["STORE_top20_synonym_purity"]), flush=True)

    grid_list = variant_grid(grid)
    done = completed_units(out_dir)
    print("[grid] %d foundations, %d already complete" % (len(grid_list), len(done)), flush=True)

    for vi, (name, fam, p) in enumerate(grid_list):
        key = unit_key(grid, name)
        if key in done:
            print("[unit %d/%d] %s SKIP (checkpointed)" % (vi + 1, len(grid_list), name),
                  flush=True)
            continue
        ts = time.time()

        def log(msg, _n=name):
            print("[unit] %s %s" % (_n, msg), flush=True)

        S, qmap, qmap2, extra = build_variant(fam, p, base, D, ASSET, log)
        geo = SC.measure_geometry(S, D["syn"], INS.items, D["fq"], MASTER_SEED + 5)
        pur = purity_of_store(S, D["syn"])
        H, TIE, DIAG = INS.evaluate_foundation(S, qmap, qmap2)
        np.savez_compressed(os.path.join(out_dir, "hits__%s.npz" % name),
                            **{k: v.astype(np.float32) for k, v in H.items()})
        summ = {"family": fam, "params": p, "PURITY": pur, "geometry": geo, "extra": extra,
                "tie_conventions_on_A2_population": TIE, "cue_diagnostics": DIAG,
                "dim": int(S.shape[1]), "corpus_cue_expressible": qmap is not None,
                "acc_on_A2_population_n%d" % int(INS.maskA2.sum()):
                    {k: round(float(np.mean(v[INS.maskA2])), 4) for k, v in H.items()},
                "acc_on_ALL_items_n%d" % n_i:
                    {k: round(float(np.mean(v)), 4) for k, v in H.items()},
                "elapsed_s": round(time.time() - ts, 1)}
        ka = summ["acc_on_ALL_items_n%d" % n_i]["KA_NATIVE_own_row"]
        summ["VALIDITY"] = {
            "KA_NATIVE": ka,
            "NULL_gated": summ["acc_on_A2_population_n%d" % int(INS.maskA2.sum())][
                "NULL_semantic_cue_for_a_DIFFERENT_word__gated"],
            "PASS_KA": bool(ka >= KA_CEILING_MIN),
            "VOID_COLLAPSED": bool(ka < KA_CEILING_MIN)}
        record_unit(out_dir, key, summ)
        A2p = summ["acc_on_A2_population_n%d" % int(INS.maskA2.sum())]
        print("[unit %d/%d] %s PURITY20=%.5f cos_syn=%.4f ratio=%s PR=%.1f KA=%.4f A2=%.4f "
              "B_native=%.4f B_F4=%.4f (%.1fs)"
              % (vi + 1, len(grid_list), name, pur["top20"]["PURITY"], geo["cos_to_SYNONYMS"],
                 geo["RATIO_syn_over_freqmatched_nonsyn"], geo["PARTICIPATION_RATIO_unit_of_256"],
                 ka, A2p["A2_SEMANTIC_gated"], A2p["B_EXACT_KEY_NATIVE"],
                 A2p["B_F4_CONSTANT_PROTOTYPE"], time.time() - ts), flush=True)

    aggregate(grid, out_dir, INS, gate, t0)
    return 0


CURVE_ARMS = ("A2_SEMANTIC_gated", "B_EXACT_KEY_NATIVE", "B_EXACT_KEY_FIXEDCUE",
              "B_PARTIAL_CUE_sentence", "A1_SENTENCE_full_pool",
              "B_PARTIAL_CUE_TWOSTAGE", "A1_SENTENCE_TWOSTAGE_full_pool",
              "B_F4_CONSTANT_PROTOTYPE", "A2_F_CONSTANT_PROTOTYPE", "B_F5_SCRAMBLE_NATIVE",
              "A2_F_SCRAMBLE")
FIXED_FLOORS = ("B_F1_TRIGRAM_ONLY", "B_F2_PREFIX_ONLY", "B_F3_FREQUENCY",
                "A2_F_FREQUENCY", "A2_F_RANDOM_WITHIN_GATE")
# NOT FLOORS. The ceiling of the query-ignoring family, FITTED ON GOLD. Reported beside every
# claim so that "beats a constant" is never read as "beats the best possible constant".
FIXED_ORACLES = ("B_ORACLE_CONSTANT_GOLD_DEGREE_not_a_floor",)


def aggregate(grid: str, out_dir: str, INS: "NativeInstruments", gate: Dict, t0: float) -> None:
    from experiments._seed_checkpoint import write_metrics

    rows = {k.split("|")[-1]: v for k, v in load_units(out_dir).items()}
    order = [n for n, _f, _p in variant_grid(grid) if n in rows]
    mask = INS.maskA2
    npop = int(mask.sum())

    # ---- one bootstrap draw over the common population, every quoted arm inside it
    hits: Dict[str, np.ndarray] = {}
    for nm in order:
        z = np.load(os.path.join(out_dir, "hits__%s.npz" % nm))
        for arm in CURVE_ARMS:
            if arm in z.files:
                hits["%s::%s" % (nm, arm)] = np.asarray(z[arm], dtype=np.float64)
        if nm == order[0]:
            for arm in FIXED_FLOORS + FIXED_ORACLES:
                hits["FIXED::%s" % arm] = np.asarray(z[arm], dtype=np.float64)
    boot = FB.paired_bootstrap_ci(hits, mask, N_BOOT, MASTER_SEED + 3)
    acc, B = boot["acc"], boot["boot"]

    def mg(a, b):
        return FB.margin(B, a, b) if a in B and b in B else None

    inc = order[0]
    # ---- THE DELIVERABLE: retrieval against purity, one row per foundation
    curve = []
    for nm in order:
        r = rows[nm]
        A = r["acc_on_A2_population_n%d" % npop]
        curve.append({
            "foundation": nm, "family": r["family"], "dim": r["dim"],
            "PURITY_top20": r["PURITY"]["top20"]["PURITY"],
            "PURITY_top1": r["PURITY"]["top1"]["PURITY"],
            "frac_words_with_a_synonym_in_top20":
                r["PURITY"]["top20"]["frac_words_with_a_synonym_in_topk"],
            "SUPPLY_PURITY": r["extra"].get("SUPPLY_PURITY", {}).get("SUPPLY_PURITY"),
            "cos_to_SYNONYMS": r["geometry"]["cos_to_SYNONYMS"],
            "cos_to_NONSYN_freq_matched": r["geometry"]["cos_to_NONSYNONYM_freq_matched"],
            "RATIO": r["geometry"]["RATIO_syn_over_freqmatched_nonsyn"],
            "PARTICIPATION_RATIO": r["geometry"]["PARTICIPATION_RATIO_unit_of_256"],
            "KA": r["VALIDITY"]["KA_NATIVE"], "NULL": r["VALIDITY"]["NULL_gated"],
            "VOID_COLLAPSED": r["VALIDITY"]["VOID_COLLAPSED"],
            "A2_SEMANTIC": A.get("A2_SEMANTIC_gated"),
            "B_EXACT_KEY_NATIVE": A.get("B_EXACT_KEY_NATIVE"),
            "B_EXACT_KEY_FIXEDCUE": A.get("B_EXACT_KEY_FIXEDCUE"),
            "B_PARTIAL_CUE": A.get("B_PARTIAL_CUE_sentence"),
            "B_PARTIAL_CUE_TWOSTAGE": A.get("B_PARTIAL_CUE_TWOSTAGE"),
            "A1_SENTENCE": r["acc_on_ALL_items_n%d" % INS.n_i].get("A1_SENTENCE_full_pool"),
            "A1_SENTENCE_TWOSTAGE": r["acc_on_ALL_items_n%d" % INS.n_i].get(
                "A1_SENTENCE_TWOSTAGE_full_pool"),
            "cue_diagnostics": r.get("cue_diagnostics", {}),
            "OWN_B_F4_CONSTANT": A.get("B_F4_CONSTANT_PROTOTYPE"),
            "OWN_B_F5_SCRAMBLE": A.get("B_F5_SCRAMBLE_NATIVE"),
            "circular": "CIRCULAR" in json.dumps(r["extra"]).upper()})

    # ---- the bar, arm by arm, never a MEETS_BAR
    fixed = {a: acc["FIXED::%s" % a] for a in FIXED_FLOORS}
    bars = {}
    for nm in order:
        kB = "%s::B_EXACT_KEY_NATIVE" % nm
        kA = "%s::A2_SEMANTIC_gated" % nm
        e = {"vs_INCUMBENT_B": mg(kB, "%s::B_EXACT_KEY_NATIVE" % inc),
             "vs_INCUMBENT_A2": mg(kA, "%s::A2_SEMANTIC_gated" % inc),
             "B_vs_OWN_CONSTANT_PROTOTYPE": mg(kB, "%s::B_F4_CONSTANT_PROTOTYPE" % nm),
             "B_vs_INCUMBENT_CONSTANT_PROTOTYPE_0.2070": mg(
                 kB, "%s::B_F4_CONSTANT_PROTOTYPE" % inc),
             "B_vs_TRIGRAM": mg(kB, "FIXED::B_F1_TRIGRAM_ONLY"),
             "B_vs_PREFIX": mg(kB, "FIXED::B_F2_PREFIX_ONLY"),
             "B_vs_FREQUENCY": mg(kB, "FIXED::B_F3_FREQUENCY"),
             "B_vs_OWN_SCRAMBLE": mg(kB, "%s::B_F5_SCRAMBLE_NATIVE" % nm),
             "A2_vs_OWN_CONSTANT_PROTOTYPE": mg(kA, "%s::A2_F_CONSTANT_PROTOTYPE" % nm),
             "A2_vs_FREQUENCY": mg(kA, "FIXED::A2_F_FREQUENCY"),
             "A2_vs_RANDOM_WITHIN_GATE": mg(kA, "FIXED::A2_F_RANDOM_WITHIN_GATE"),
             "A2_vs_OWN_SCRAMBLE": mg(kA, "%s::A2_F_SCRAMBLE" % nm),
             "B_vs_ORACLE_CONSTANT_GOLD_DEGREE_NOT_A_FLOOR": mg(
                 kB, "FIXED::B_ORACLE_CONSTANT_GOLD_DEGREE_not_a_floor"),
             "PARTIAL_CUE_vs_INCUMBENT": mg("%s::B_PARTIAL_CUE_sentence" % nm,
                                            "%s::B_PARTIAL_CUE_sentence" % inc),
             "A1_vs_INCUMBENT": mg("%s::A1_SENTENCE_full_pool" % nm,
                                   "%s::A1_SENTENCE_full_pool" % inc),
             "A1_TWOSTAGE_vs_INCUMBENT_A1": mg("%s::A1_SENTENCE_TWOSTAGE_full_pool" % nm,
                                               "%s::A1_SENTENCE_full_pool" % inc),
             "PARTIAL_CUE_TWOSTAGE_vs_INCUMBENT": mg("%s::B_PARTIAL_CUE_TWOSTAGE" % nm,
                                                     "%s::B_PARTIAL_CUE_sentence" % inc)}
        floors_B = {"TRIGRAM": fixed["B_F1_TRIGRAM_ONLY"], "PREFIX": fixed["B_F2_PREFIX_ONLY"],
                    "FREQUENCY": fixed["B_F3_FREQUENCY"],
                    "OWN_CONSTANT": acc.get("%s::B_F4_CONSTANT_PROTOTYPE" % nm),
                    "INCUMBENT_CONSTANT": acc.get("%s::B_F4_CONSTANT_PROTOTYPE" % inc),
                    "OWN_SCRAMBLE": acc.get("%s::B_F5_SCRAMBLE_NATIVE" % nm)}
        bind = max(floors_B.items(), key=lambda kv: (kv[1] if kv[1] is not None else -1))
        e["B_BINDING_FLOOR"] = {"which": bind[0], "value": round(float(bind[1]), 4)}
        e["B_vs_BINDING_FLOOR"] = (
            e["B_vs_OWN_CONSTANT_PROTOTYPE"] if bind[0] == "OWN_CONSTANT" else
            e["B_vs_INCUMBENT_CONSTANT_PROTOTYPE_0.2070"] if bind[0] == "INCUMBENT_CONSTANT" else
            e["B_vs_TRIGRAM"] if bind[0] == "TRIGRAM" else
            e["B_vs_PREFIX"] if bind[0] == "PREFIX" else
            e["B_vs_OWN_SCRAMBLE"] if bind[0] == "OWN_SCRAMBLE" else e["B_vs_FREQUENCY"])
        bars[nm] = e

    # ---- the matched CONTROL ladder, every rung at matched hyper-parameters
    pairs = [("F10_SUPPLY_GLOVE_m5_eta0.50", "F11_C_SUPPLY_GLOVE_SHUFFLED_m5_eta0.50"),
             ("F10_SUPPLY_GLOVE_m5_eta0.50", "F11_C_SUPPLY_GLOVE_FREQ_MATCHED_m5_eta0.50"),
             ("F10_SUPPLY_GLOVE_m5_eta0.50", "F12_C_RAND_STORE_NEIGHBOURS_m5_eta0.50"),
             ("F03_OURS_THEMATIC_m5_eta0.50", "F04_C_THEMATIC_SHUFFLED_m5_eta0.50"),
             ("F13_SUPPLY_CSKG_m5_eta0.50", "F14_C_SUPPLY_CSKG_SHUFFLED_m5_eta0.50"),
             ("F20_FUSE_GLOVE_w0.30", "F23_C_FUSE_GLOVE_SHUFFLED_w0.30"),
             ("F20_FUSE_GLOVE_w0.50", "F23_C_FUSE_GLOVE_SHUFFLED_w0.50"),
             ("F20_FUSE_GLOVE_w1.00", "F23_C_FUSE_GLOVE_SHUFFLED_w1.00")]
    ladder = {}
    for a, b in pairs:
        if a in rows and b in rows:
            ladder["%s__vs__%s" % (a, b)] = {
                "B": mg("%s::B_EXACT_KEY_NATIVE" % a, "%s::B_EXACT_KEY_NATIVE" % b),
                "A2": mg("%s::A2_SEMANTIC_gated" % a, "%s::A2_SEMANTIC_gated" % b),
                "TWOSTAGE_partial_cue": mg("%s::B_PARTIAL_CUE_TWOSTAGE" % a,
                                           "%s::B_PARTIAL_CUE_TWOSTAGE" % b),
                "TWOSTAGE_A1": mg("%s::A1_SENTENCE_TWOSTAGE_full_pool" % a,
                                  "%s::A1_SENTENCE_TWOSTAGE_full_pool" % b),
                "purity_a": rows[a]["PURITY"]["top20"]["PURITY"],
                "purity_b": rows[b]["PURITY"]["top20"]["PURITY"]}

    # ---- DOES RETRIEVAL TRACK PURITY. Spearman over the GOLD-FREE, non-collapsed foundations.
    def spearman(x, y):
        x, y = np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64)
        rx = np.argsort(np.argsort(x)).astype(np.float64)
        ry = np.argsort(np.argsort(y)).astype(np.float64)
        rx -= rx.mean()
        ry -= ry.mean()
        d = float(np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))
        return round(float((rx * ry).sum() / d), 4) if d > 0 else None

    adm = [c for c in curve if not c["circular"] and not c["VOID_COLLAPSED"]]
    corr = {}
    for ycol in ("B_EXACT_KEY_NATIVE", "A2_SEMANTIC", "A1_SENTENCE", "B_PARTIAL_CUE",
                 "B_PARTIAL_CUE_TWOSTAGE", "A1_SENTENCE_TWOSTAGE"):
        sel = [c for c in adm if c[ycol] is not None]
        if len(sel) >= 5:
            corr[ycol] = {
                "n_foundations": len(sel),
                "rho_vs_PURITY_top20": spearman([c["PURITY_top20"] for c in sel],
                                                [c[ycol] for c in sel]),
                "rho_vs_cos_to_SYNONYMS": spearman([c["cos_to_SYNONYMS"] for c in sel],
                                                   [c[ycol] for c in sel]),
                "rho_vs_RATIO": spearman([c["RATIO"] or 0.0 for c in sel], [c[ycol] for c in sel]),
                "rho_vs_PARTICIPATION_RATIO": spearman([c["PARTICIPATION_RATIO"] for c in sel],
                                                       [c[ycol] for c in sel])}

    clears = [nm for nm in order
              if bars[nm]["B_vs_BINDING_FLOOR"] and
              bars[nm]["B_vs_BINDING_FLOOR"]["band"] == "ABOVE" and not curve[
                  order.index(nm)]["circular"] and not curve[order.index(nm)]["VOID_COLLAPSED"]]

    # ---- IN-GRID IDENTITY CHECK. The fusion ladder's w=0 endpoint is the incumbent store with a
    # zero static block, so EVERY arm must agree to machine precision. If it does not, the ladder
    # is not a single knob and nothing on it can be read.
    ident_check = None
    if "F20_FUSE_GLOVE_w0.00" in rows:
        z0 = np.load(os.path.join(out_dir, "hits__%s.npz" % inc))
        z1 = np.load(os.path.join(out_dir, "hits__F20_FUSE_GLOVE_w0.00.npz"))
        shared = sorted(set(z0.files) & set(z1.files))
        dm = {a: float(np.abs(np.asarray(z0[a], dtype=np.float64)
                              - np.asarray(z1[a], dtype=np.float64)).max()) for a in shared}
        ident_check = {"n_arms": len(shared), "max_abs_diff_over_all_arms": max(dm.values()),
                       "per_arm": {a: v for a, v in dm.items() if v > 0.0},
                       "PASS": bool(max(dm.values()) < 1e-9)}

    reg = {"STORE_top20_synonym_purity": [curve[0]["PURITY_top20"],
                                          LANDED["STORE_top20_synonym_purity"]],
           "A2_SEMANTIC_gated": [curve[0]["A2_SEMANTIC"], LANDED["A2_SEMANTIC_gated"]],
           "A1_SENTENCE_full_pool": [curve[0]["A1_SENTENCE"], LANDED["A1_SENTENCE_full_pool"]],
           "B_EXACT_KEY": [curve[0]["B_EXACT_KEY_NATIVE"], LANDED["B_EXACT_KEY"]],
           "B_F1_TRIGRAM_ONLY": [round(fixed["B_F1_TRIGRAM_ONLY"], 4),
                                 LANDED["B_F1_TRIGRAM_ONLY"]],
           "B_F2_PREFIX_ONLY": [round(fixed["B_F2_PREFIX_ONLY"], 4), LANDED["B_F2_PREFIX_ONLY"]],
           "B_F3_FREQUENCY": [round(fixed["B_F3_FREQUENCY"], 4), LANDED["B_F3_FREQUENCY"]],
           "B_F4_CONSTANT_PROTOTYPE": [curve[0]["OWN_B_F4_CONSTANT"],
                                       LANDED["B_F4_CONSTANT_PROTOTYPE"]],
           "PR_unit_store": [curve[0]["PARTICIPATION_RATIO"], LANDED["PR_unit_store"]]}

    M = {"grid": grid, "n_foundations": len(order), "population_n": npop,
         "ruler_mode_gate": gate,
         "REGRESSION_GATE_measured_vs_landed": reg,
         "IN_GRID_IDENTITY_CHECK_fusion_w0_equals_incumbent": ident_check,
         "THE_CURVE_retrieval_against_purity": curve,
         "DOES_RETRIEVAL_TRACK_PURITY": corr,
         "BAR_arm_by_arm": bars,
         "MATCHED_CONTROL_LADDER": ladder,
         "FIXED_FLOORS_on_the_identical_population": {k: round(v, 4) for k, v in fixed.items()},
         "FIXED_ORACLE_NOT_A_FLOOR_fitted_on_gold": {
             a: round(acc["FIXED::%s" % a], 4) for a in FIXED_ORACLES},
         "FOUNDATIONS_CLEARING_THE_BINDING_FLOOR": clears,
         "tie_conventions": {nm: rows[nm]["tie_conventions_on_A2_population"] for nm in order},
         "elapsed_s": round(time.time() - t0, 1)}
    verdict = ("A_FOUNDATION_CLEARS_THE_BINDING_FLOOR" if clears
               else "NO_FOUNDATION_CLEARS_THE_BINDING_FLOOR")
    msg = ("purity(store top-20 synonyms) %.5f -> %.5f across %d foundations; best gold-free "
           "B_EXACT_KEY_NATIVE %.4f vs binding floor; clears=%s"
           % (curve[0]["PURITY_top20"],
              max(c["PURITY_top20"] for c in adm) if adm else -1.0, len(order),
              max((c["B_EXACT_KEY_NATIVE"] or 0.0) for c in adm) if adm else -1.0,
              ",".join(clears) if clears else "NONE"))
    from pathlib import Path
    write_metrics(Path(out_dir), {"verdict": verdict, "verdict_msg": msg,
                            "elapsed_s": round(time.time() - t0, 1), "summary": M})
    print("[done] %s | %s" % (verdict, msg), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--grid", default="full", choices=("smoke", "full"))
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    # smoke output is ALWAYS isolated from the full path, and --tag lets a clean-slate
    # precondition be met by writing to a FRESH directory rather than by deleting one.
    name = ("exp_foundation_neighbourhood_purity_v1"
            + ("_smoke" if a.grid == "smoke" else "")
            + (("_" + a.tag) if a.tag else ""))
    out = os.path.join(_REPO, "data", name)
    return run(a.grid, out)


if __name__ == "__main__":
    raise SystemExit(main())
