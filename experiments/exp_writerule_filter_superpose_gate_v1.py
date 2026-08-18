"""exp_writerule_filter_superpose_gate_v1 -- ORGAN A, THE LAST TWO UNGATED WRITE-RULE STEPS.

notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.9 (gate board): CODE exonerated twice (ac629b1e7),
ACCUMULATE gated as the interference source (b6cad69ca). FILTER and NORMALISE were the two rows still
"NOT GATED" on that board; NORMALISE is off by default (verified from runtime, sec 6.9 row 4) so this
cell does not re-gate it. This cell gates FILTER and, per the dispatch brief's naming, "SUPERPOSE" --
see STEP 1 below for the enumeration that corrects what "SUPERPOSE" actually names in live code.

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md). Ran:
`bash tools/substrate_query.sh "write rule FILTER SUPERPOSE gate isolate per anchor record disjoint
subspace interference dissociation"` -- TIMED OUT (exit 124) after 90s. This is the documented
director_kb livelock (notes/STATUS.md WHAT IS RUNNING: "hd_director_kb_continuous_ingest LIVELOCKED
... substrate_query.sh currently ERRORS on a locked cache file"), not a fresh failure. Fallback per
the sibling cell's own precedent (exp_organ_f_accumulate_interference_diagnosis_v1.py's own PRIOR-WORK
CHECK note): the directly-cited sibling cells were read in full instead --
exp_dissociation_score_instrument_v1.py (scorer + matched-pair population, reused verbatim below),
exp_organ_f_accumulate_interference_diagnosis_v1.py (the "mean pairwise anchor cosine" finding this
cell's Gate B brief cites), exp_writerule_step_ladder_v1.py (FILTER counterfactual precedent: R1
UNFILTERED_SINGLE_OCC, reused verbatim as F1 below), exp_writerule_learned_basis_denominator_gate_v1.py
(CODE gate, for contrast). None of the four builds a per-step FILTER sweep (POS-strict / syntactic-
neighbour / window-sweep / random-token control) or a per-anchor-isolated vs shared-store dissociation
comparison. Not a rediscovery.

=================================================================================================
STEP 1 -- ENUMERATED FROM LIVE CODE, NOT FROM THE BRIEF'S SKETCH. THE SKETCH IS WRONG ABOUT GATE B.

FILTER (Gate A) is exactly what the brief sketched: `content_words()`
(hdlab/grounding_acquisition_loop.py:106-114) -- regex `[a-z']+` on the lowered sentence, minus a
~70-word stopword set, minus tokens of length <=2. This is the ONLY token-survival gate anywhere on
the write path; there is no second filtering step.

"SUPERPOSE" (Gate B) DOES NOT EXIST AS A SEPARATE WRITE-TIME OPERATION IN LIVE CODE, and this is a
result in its own right, not a failure to find one. Two facts, both verified below by direct
recompute, not merely argued:

 (a) `ConceptSpace.observe` (hdlab/reading_grounding_loop.py:478-481) is `self._sums[lemma] +=
     ctx_vec` -- this reads and writes ONLY the ONE dict entry keyed by `lemma`. It never reads any
     OTHER anchor's entry. `anchor_matrix()` (same file, ~line 504) is `np.stack([self._sums[a] for a
     in anchors])` -- a plain stack of independently-computed rows, never an algebraic combination of
     different anchors' vectors into one shared memory trace (unlike a classical VSA cleanup memory,
     which DOES bundle many items into one vector and pays a crosstalk cost for it). "The store" is a
     matrix of rows, not a superposition.
 (b) Each row is *itself* fully reconstructible from that ONE anchor's own raw context-word counts and
     a FIXED, corpus-independent per-word symbol dictionary: `INFO.reconstruct_bipolar(counts, d) =
     sum_w counts[w] * symbol_vector(w)` (exp_cue_information_audit_v1.py:184-190, and
     exp_cue_information_audit_v1's own `verify_recoverability` already asserts this reconstruction is
     bit-exact against the live cache for the single-sentence case). `symbol_vector(w)` is a
     hashlib-seeded draw keyed ONLY on the word string (hdlab/reading_grounding_loop.py:297-310) --
     not on which anchor is being built, not on which OTHER anchors exist.

Consequence, stated as a prediction BEFORE running anything: because building anchor A's stored vector
never reads anchor B's data, data from ANY OTHER anchor, or "how many anchors are in the store", the
construction the brief names S1_PER_ANCHOR_ISOLATED ("score each anchor from its own record with NO
shared superposition at all") must be MATHEMATICALLY IDENTICAL to S0_INCUMBENT for any score function
that only ever looks at ONE NAMED PAIR of anchors at a time -- which is exactly what the licensed
dissociation AUC computes (dense_scores_from_dict_store: one dot product per named pair, the other
5,489 anchors never enter the computation). This is checked below both as a closed-form argument and
as a literal bit-exact recompute (GATE_B self-test), not assumed.

The mean-pairwise-anchor-cosine RISE the brief cites (0.0127 -> 0.272,
exp_organ_f_accumulate_interference_diagnosis_v1, commit b6cad69ca) is real and is NOT explained away
by the point above -- it is a fact about CONTENT (independently-built records increasingly resembling
each other as each one individually accumulates more high-frequency shared context, which is the
ACCUMULATE step, already gated), not about a shared-storage mechanism. Section 2 below designs Gate B
to test this directly rather than assume it, including a construction (S2_DISJOINT_SUBSPACES) that
turns out to be STRUCTURALLY UNMEASURABLE on a pairwise scorer, and says why, rather than forcing a
number out of it.

=================================================================================================
ORGAN REUSE, enumerated then reconciled -- nothing below is reimplemented:
  experiments.exp_dissociation_score_instrument_v1 (DISS)  the LICENSED matched-pair POPULATION
    (loaded from its own on-disk checkpoint, NEVER rebuilt -- "do not rebuild the matching"),
    dense_scores_from_dict_store, counts_to_dense_store, auc_of, auc_bootstrap, l2n, its own
    KNOWN_ANSWER_WORDNET_PATH_SIM / RANDOM_VECTOR_STORE / INCUMBENT_LIVE_STORE score arrays (loaded
    from its SCORES checkpoint unit, reused verbatim for K1/N0/S0 -- not recomputed).
  experiments.exp_cue_information_audit_v1 (INFO)  content_words-filtered raw_counts_for_window,
    load_corpus_and_buckets, build_vocab, to_sparse, l2n_sparse, reconstruct_bipolar, its Pstore
    checkpoint (full-accumulation raw counts per anchor, reused for Gate B S1/N2).
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)  build_single_occurrence_counts (F0),
    CTS re-export.
  experiments.exp_writerule_step_ladder_v1 (WR)  raw_counts_unfiltered_for_window,
    build_single_occurrence_counts_unfiltered (F1, REUSED VERBATIM -- this cell does not re-derive
    the unfiltered tokenizer), wordnet_relation_composition, syntagmatic_jaccard_composition.
  experiments.exp_cue_to_store_translation_v1 (CTS)  load_cache, load_aux, MASTER_SEED.
  hdlab.reading_grounding_loop  content_words, normalize_lemma, symbol_vector, StructuralEncoder
    (the persisted UD front-end: hdlab.pos_tagger.PosTagger, hdlab.arc_parser.ArcParser,
    hdlab.arc_labeler.ArcLabeler, already trained and on disk under data/frontend_assets/ -- reused
    for F2/F3, not retrained).
  tools.floor_battery (FB)  l2n (via DISS).
  experiments._seed_checkpoint / tools.exp_checkpoint  get_output_dir, write_metrics, checkpoint units.

=================================================================================================
GATE A (FILTER) ARM DEFINITIONS, one variable at a time, ALL on the SAME single occurrence per anchor
(buckets[a][0], matching F0/PIPE's own convention so every arm differs ONLY in token survival):
  F0_INCUMBENT               content_words() filter (PIPE.build_single_occurrence_counts, reused
                              verbatim). REGRESSION GATE: must reproduce DISS's own
                              RAW_COUNT_SINGLE_OCC AUC exactly (same construction, same population).
  F1_NO_FILTER                every token kept (WR.build_single_occurrence_counts_unfiltered, reused
                              verbatim). Predicted to make AUC WORSE (more co-occurrence-biased) than
                              F0 -- an arm that must lose if the filter does useful work.
  F2_CONTENT_ONLY_STRICT      keep only tokens the UD POS tagger calls NOUN/VERB/ADJ, drop everything
                              else (a STRICTER criterion than content_words' stopword/length rule).
  F3_SYNTACTIC_NEIGHBOURS_ONLY  keep only tokens in a DIRECT (1-hop) dependency relation with the
                              target occurrence -- the target's syntactic head plus its direct
                              dependents, content-word-restricted. Uses the persisted UD parser
                              already on disk; NOT a new parser.
  F4_WINDOW_SWEEP             symmetric token window +/-1, +/-2, +/-5, and whole-sentence (=F0 by
                              construction -- checked as an internal regression).
  N1_RANDOM_FILTER            THE CONTROL THAT CARRIES THE CLAIM: from the SAME unfiltered token pool
                              F1 uses, keep a RANDOM subset of the SAME SIZE F0 kept for that anchor's
                              occurrence (matched per-anchor, not globally). If a filter arm does not
                              beat this, its gain is attrition (fewer tokens), not selection (the
                              RIGHT tokens).

GATE B (SUPERPOSE, corrected per STEP 1) ARM DEFINITIONS, all on the FULL accumulation store (INFO's
Pstore checkpoint, matching DISS's own RAW_COUNT_FULL_ACCUM / INCUMBENT_LIVE_STORE source):
  S0_INCUMBENT                DISS's own INCUMBENT_LIVE_STORE arm (mat[w1] . mat[w2], the live H^T p_a
                              dense projected store), reused verbatim from its SCORES checkpoint.
                              REGRESSION GATE: must reproduce AUC 0.0710.
  S1_PER_ANCHOR_ISOLATED      each matched word's vector rebuilt via INFO.reconstruct_bipolar of ONLY
                              that word's own Pstore counts -- the function never reads any other
                              word's data. Self-tested (below) to be bit-exact against S0's own mat
                              rows for a real sample BEFORE the arm is scored, which is what makes
                              "matches S0" a proof rather than a coincidence.
  S2_DISJOINT_SUBSPACES       each anchor given a private, non-overlapping coordinate block. Reported
                              as a CAPACITY DIAGNOSTIC, not a pairwise AUC arm -- see STEP 1 and the
                              GATE_B_CAPACITY section for why a pairwise scorer cannot see this
                              construction at all (any two disjoint-block anchors have cosine exactly
                              0 by construction, independent of content).
  N2_SHUFFLED_ASSIGNMENT      S0's own store, anchor-to-vector KEY assignment permuted (a fixed
                              derangement-style permutation over the matched-pair word set) before
                              scoring. Must destroy the effect.
  K1 / N0                     DISS's own KNOWN_ANSWER_WORDNET_PATH_SIM / RANDOM_VECTOR_STORE score
                              arrays, reused verbatim (same population, same construction -- these do
                              not depend on FILTER or SUPERPOSE at all) and re-bootstrapped here so
                              this cell's own metrics.json carries its own licensing check rather than
                              pointing at another file.

SECONDARY MEASURE (beside the primary AUC, per the brief: "report hit@1 and winner composition beside
the AUC, never instead of it"). A RESTRICTED-FIELD retrieval check, cheap and self-contained, reusing
the SAME per-arm store dict already built for the AUC: for every SET-P (paradigmatic, substitutable)
matched pair (w1, w2), treat w1 as query and w2 as gold, rank against the OTHER distinct words in this
cell's own candidate pool (the matched-pair word union, typically a few hundred words -- NOT the full
5,491-anchor population; this is a SMALLER, adequately-powered population and is reported as such, per
the brief's own explicit "run a smaller adequately powered population and state n" fallback). Winner
composition (WordNet-relation rate, syntagmatic Jaccard) reuses WR.wordnet_relation_composition /
WR.syntagmatic_jaccard_composition verbatim, exactly as the write-rule ladder and the ACCUMULATE gate
both already use them.

=================================================================================================
BRAIN FRAMING, labelled per choice, per the dispatch brief.
PINNED: cortex is sparse and topographically organised -- not every neuron participates in every
representation. Our single shared dense store is the substitution FOR that; S2_DISJOINT_SUBSPACES is
the crude test of whether that substitution costs us, and the capacity arithmetic below reports that
cost directly rather than asserting it.
OUR INVENTION UNDER TEST, never claimed as brain-pinned: every specific filter rule (content_words'
~70-word stopword list, the POS-strict criterion, the 1-hop syntactic-neighbour restriction, every
window width), the N_HIGH_FREQ-style thresholds, and the disjoint-block sizing in S2.

ANOTHER AGENT (noncollapse-maxpool) IS LIVE IN experiments/ testing max-over-occurrences on the
licensed dissociation instrument. This cell uses a DISTINCT filename, writes only to
data/exp_writerule_filter_superpose_gate_v1[_reduced]/ and its own scratch/ subdir, imports
exp_dissociation_score_instrument_v1 READ-ONLY (never edits it), and does not touch hdlab/.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. data/foundation/
is never opened. Nothing here is wired into hdlab/.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every FILTER and SUPERPOSE arm's concatenated P+S score vector,
#   asserted >1 distinct digest (S2 is declared exempt -- its score is a tautological constant 0.5 by
#   construction, which the self-test proves directly rather than papering over with a fake digest)
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: GATE_A_SCORES and GATE_B_SCORES as separate tools.exp_checkpoint units
#   (parser-dependent F2/F3 are the interruption-prone phase), MAIN wraps the assembled report
# - discriminator survives scale: --grid reduced runs the IDENTICAL code path (same parser, same
#   matching machinery) on a smaller real word/pair subset, not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses DISS's own regression-gated population and
#   INFO's regression-gated Pstore checkpoint unmodified; every NEW construction -- F2/F3/F4/N1
#   filters, S1/S2/N2 store builds -- is self-tested against a hand-built fixture with a known answer)
# - progress_logging: print_flush_true (every phase prints a flushed line; F2/F3 involve parsing,
#   the slow phase, so progress is printed every 200 words there)
# - baseline_in_band / crlb_floor_computed: n/a -- this is a gate/diagnostic cell over an existing
#   store population, same family as DISS/the ACCUMULATE gate; declared, not omitted.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/hdlab/UD-frontend next -- this can take ~60-90s cold; "
      "flushed so a slow import is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DISS   # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO           # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE    # noqa: E402  READ ONLY
import experiments.exp_writerule_step_ladder_v1 as WR             # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import (                        # noqa: E402  READ ONLY
    content_words, normalize_lemma, symbol_vector, StructuralEncoder, CTX_D,
)
from experiments._seed_checkpoint import get_output_dir, write_metrics             # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "writerule_filter_superpose_gate_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/writerule_filter_superpose_gate_2026-08-18.md"
DISS_OUT_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
INFO_OUT_DIR = os.path.join(REPO, "data", "exp_cue_information_audit_v1")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = DISS.CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
_TOKEN_RE = re.compile(r"[a-z']+")     # byte-identical to content_words' own regex, matches WR's own
N_SMOKE_WORDS = 60                      # smoke: restrict the matched-pair word universe to this many
S2_BLOCK_SIZE = 8                       # OUR INVENTION UNDER TEST -- dims/anchor if capacity allowed


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# GATE A -- FILTER VARIANT BUILDERS. Each returns a Counter of SURFACE WORD -> count for ONE
# occurrence, matching PIPE.build_single_occurrence_counts / WR's own unfiltered counterpart's
# output convention exactly, so all five feed the SAME downstream DISS.counts_to_dense_store call.
# =================================================================================================
def raw_counts_pos_strict_for_window(encoder: StructuralEncoder, sentence: str, target_lemma: str
                                     ) -> Counter:
    """F2: keep a token iff the UD tagger calls it NOUN/VERB/ADJ (a STRICTER criterion than
    content_words' stopword+length rule, replacing it rather than adding to it) and its lemma !=
    target_lemma. Triggers StructuralEncoder._load() (shared tagger/parser/labeler weights, already
    on disk) but only USES the tagger; parse() is called anyway so both F2 and F3 share ONE parse per
    sentence rather than paying the parser cost twice."""
    p = encoder.parse(sentence)
    if p is None:
        return Counter()
    toks, lemmas, _heads, _labs, _ok = p
    pos_tags = encoder._tagger.tag(toks)
    out = Counter()
    for t, lm, pt in zip(toks, lemmas, pos_tags):
        if pt in ("NOUN", "VERB", "ADJ") and lm and lm != target_lemma:
            out[t.lower()] += 1
    return out


def raw_counts_syntactic_neighbours_for_window(encoder: StructuralEncoder, sentence: str,
                                               target_lemma: str) -> Tuple[Counter, bool]:
    """F3: keep only tokens in a DIRECT (1-hop) dependency relation with a target occurrence -- the
    target's own syntactic head, plus tokens that are the target's direct dependents. Content-word
    restricted (the same `ok` set StructuralEncoder.features() uses), but NOT StructuralEncoder's own
    `.features()` -- that also includes co-argument (~rel:rel) features, a 2-hop-through-the-predicate
    relation the brief's "direct dependency relation" does not ask for; this is the narrower 1-hop-only
    construction. Returns (counts, target_was_found) so a caller can report parse-miss rate honestly."""
    p = encoder.parse(sentence)
    if p is None:
        return Counter(), False
    toks, lemmas, heads, _labs, ok = p
    n = len(toks)

    def usable(j: int) -> bool:
        lm = lemmas[j - 1]
        return bool(lm) and lm != target_lemma and lm in ok

    out = Counter()
    found = False
    for i in range(1, n + 1):
        if lemmas[i - 1] != target_lemma:
            continue
        found = True
        h = heads.get(i, 0)
        if h and 1 <= h <= n and usable(h):
            out[toks[h - 1].lower()] += 1
        for j in range(1, n + 1):
            if heads.get(j, 0) == i and usable(j):
                out[toks[j - 1].lower()] += 1
    return out, found


def raw_counts_windowed_for_window(sentence: str, target_lemma: str,
                                   half_width: Optional[int]) -> Counter:
    """F4: symmetric token window around EVERY occurrence of target_lemma in the sentence's OWN
    (unfiltered) token sequence, THEN content_words' stopword+length filter applied within the
    window (so F4 differs from F0 ONLY in which POSITIONS are eligible, not in the survival rule
    itself). half_width=None means the whole sentence -- an internal regression check that this must
    reproduce F0 exactly is asserted in self_test()."""
    toks = _TOKEN_RE.findall(sentence.lower())
    lemmas = [normalize_lemma(t) for t in toks]
    n = len(toks)
    target_pos = [i for i, lm in enumerate(lemmas) if lm == target_lemma]
    if not target_pos:
        return Counter()
    if half_width is None:
        keep_idx = set(range(n))
    else:
        keep_idx = set()
        for tp in target_pos:
            for i in range(max(0, tp - half_width), min(n, tp + half_width + 1)):
                keep_idx.add(i)
    cw = set(content_words(sentence))
    out = Counter()
    for i in sorted(keep_idx):
        w = toks[i]
        if w in cw and lemmas[i] != target_lemma:
            out[w] += 1
    return out


def raw_counts_random_filter_for_window(sentence: str, target_lemma: str, keep_n: int,
                                        rng: np.random.Generator) -> Counter:
    """N1: from the SAME unfiltered token pool F1 uses (self-masked), keep a RANDOM subset of size
    keep_n (matched per-anchor to F0's OWN kept-token count for that occurrence). If keep_n exceeds
    the available pool, keep everything (no oversampling)."""
    toks_all = [w for w in _TOKEN_RE.findall(sentence.lower()) if normalize_lemma(w) != target_lemma]
    if not toks_all or keep_n <= 0:
        return Counter()
    k = min(keep_n, len(toks_all))
    idx = rng.choice(len(toks_all), size=k, replace=False)
    return Counter(toks_all[i] for i in idx)


def build_variant_counts(anchor_ids: Sequence[str], buckets: Dict[str, List[int]], sents: List[str],
                         fn, label: str) -> Tuple[Dict[str, Counter], Dict]:
    """Generic single-occurrence-per-anchor loop, mirroring PIPE.build_single_occurrence_counts /
    WR.build_single_occurrence_counts_unfiltered's own shape exactly (buckets[a][0] sentence choice)
    so every FILTER arm is built from the LITERAL SAME sentence per anchor."""
    t0 = time.time()
    out: Dict[str, Counter] = {}
    n_empty = 0
    for k, a in enumerate(anchor_ids):
        occ = buckets.get(a, [])
        if not occ:
            out[a] = Counter()
            n_empty += 1
            continue
        out[a] = fn(sents[occ[0]], a)
        if (k + 1) % 200 == 0 or k == len(anchor_ids) - 1:
            print("[%s] %d/%d elapsed=%.0fs" % (label, k + 1, len(anchor_ids), time.time() - t0),
                 flush=True)
    return out, {"n_anchors": len(anchor_ids), "n_empty_profile": n_empty,
                "elapsed_s": round(time.time() - t0, 1)}


# =================================================================================================
# GATE B -- SUPERPOSE VARIANT BUILDERS
# =================================================================================================
def build_S1_isolated_store(words_needed: Sequence[str], counts_full: Dict[str, Counter]
                            ) -> Dict[str, np.ndarray]:
    """Each word's dense vector rebuilt from ONLY that word's own Pstore counts via
    INFO.reconstruct_bipolar -- the function's own signature takes a single Counter and returns a
    single vector; it is called once per word here and NEVER passed any other word's data, any
    'store' object, or any population size. That is the literal, structural meaning of 'no shared
    superposition': the call site cannot see anchor B while building anchor A."""
    out: Dict[str, np.ndarray] = {}
    for w in words_needed:
        out[w] = INFO.reconstruct_bipolar(counts_full.get(w, Counter()), d=CTX_D)
    return out


def build_N2_shuffled_store(store: Dict[str, np.ndarray], words_needed: Sequence[str], seed: int
                            ) -> Dict[str, np.ndarray]:
    """S0's own vectors, but the WORD KEY each vector is filed under is permuted (a derangement-style
    shuffle: reject the identity permutation and retry if a fixed point survives, so every word's
    scored 'record' is provably SOMEONE ELSE's)."""
    words = list(words_needed)
    rng = np.random.default_rng(seed)
    for _ in range(200):
        perm = rng.permutation(len(words))
        if not np.any(perm == np.arange(len(words))):
            break
    mapping = {words[i]: words[int(perm[i])] for i in range(len(words))}
    return {w: store[mapping[w]] for w in words if mapping[w] in store}


def s2_capacity_report(n_pop: int, d_incumbent: int, block_size: int) -> Dict:
    """S2_DISJOINT_SUBSPACES capacity arithmetic. At the INCUMBENT's own dimensionality, dims-per-
    anchor if the budget were split evenly is d_incumbent // n_pop -- report whether that is even
    >=1. Separately report the dimensionality a genuinely non-degenerate disjoint allocation would
    need at `block_size` dims/anchor (OUR INVENTION UNDER TEST, not derived)."""
    dims_at_incumbent_budget = d_incumbent // max(n_pop, 1)
    d_needed_for_block_size = n_pop * block_size
    return {
        "n_pop": n_pop, "d_incumbent": d_incumbent, "s2_block_size_dims_per_anchor": block_size,
        "dims_per_anchor_at_incumbent_budget": dims_at_incumbent_budget,
        "DEGENERATE_AT_INCUMBENT_BUDGET": bool(dims_at_incumbent_budget < 1),
        "d_needed_for_nondegenerate_block_size": d_needed_for_block_size,
        "capacity_multiplier_vs_incumbent": round(d_needed_for_block_size / float(d_incumbent), 2),
    }


# =================================================================================================
# SECONDARY MEASURE -- restricted-field hit@1 + winner composition, reusing WR's composition fns.
# =================================================================================================
def restricted_hit1_and_composition(store: Dict[str, np.ndarray], pairsP: List[Tuple[str, str, str]],
                                    candidate_pool: List[str], where: Dict[str, set]) -> Dict:
    """For every SET-P (paradigmatic) matched pair (w1, w2): query=w1, gold=w2, competing field = all
    OTHER distinct words in candidate_pool that the store has a vector for. winner = argmax cosine.
    Cheap (n_pairs x |pool| dot products); NOT the historical ~5,491-anchor hit@1 population -- a
    smaller, adequately-powered restricted field, reported as such."""
    pool = [w for w in candidate_pool if w in store]
    if len(pool) < 3:
        return {"n_probed": 0, "hit_at_1": None, "note": "candidate pool too small"}
    M = np.stack([store[w] for w in pool], axis=0).astype(np.float64)
    norms = np.linalg.norm(M, axis=1)
    norms[norms < 1e-12] = 1.0
    Mn = M / norms[:, None]
    pool_idx = {w: i for i, w in enumerate(pool)}
    hits = []
    query_words, winner_words, in_gold = [], [], []
    for w1, w2, _pos in pairsP:
        if w1 not in pool_idx or w2 not in pool_idx or w1 not in store:
            continue
        qv = np.asarray(store[w1], dtype=np.float64)
        qn = np.linalg.norm(qv)
        if qn < 1e-12:
            continue
        qv = qv / qn
        scores = Mn @ qv
        self_i = pool_idx[w1]
        scores[self_i] = -np.inf
        winner_i = int(np.argmax(scores))
        winner = pool[winner_i]
        hit = bool(winner == w2)
        hits.append(hit)
        query_words.append(w1)
        winner_words.append(winner)
        in_gold.append(hit)
    n = len(hits)
    if n == 0:
        return {"n_probed": 0, "hit_at_1": None, "note": "no scorable SET-P pairs in this pool"}
    idx_probe = np.arange(n)
    comp = WR.wordnet_relation_composition(query_words, winner_words, np.array(in_gold), idx_probe)
    syn = WR.syntagmatic_jaccard_composition(query_words, winner_words, [None] * n, where, idx_probe)
    return {"n_probed": n, "n_pool": len(pool), "hit_at_1": round(float(np.mean(hits)), 4),
           "composition": comp, "syntagmatic": syn}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- F4 whole-sentence must reproduce F0's own content_words filter exactly -------------------
    s = "The quick brown zibbo jumped over the lazy dax and the dax barked at zibbo again."
    c_whole = raw_counts_windowed_for_window(s, "dax", None)
    c_f0 = INFO.raw_counts_for_window(s, "dax")
    assert c_whole == c_f0, "F4 whole-sentence must equal F0's own filter exactly: %r vs %r" % (
        c_whole, c_f0)
    ev["F4_whole_sentence_equals_F0"] = True

    # --- F4 narrow window must be a STRICT SUBSET of the whole-sentence count, and drop the far word
    c_w1 = raw_counts_windowed_for_window(s, "dax", 1)
    assert set(c_w1) <= set(c_f0), "windowed filter must never introduce a word F0 didn't keep"
    assert sum(c_w1.values()) < sum(c_f0.values()), "a narrow window must keep STRICTLY fewer tokens"
    ev["F4_window_is_strict_subset"] = {"narrow": dict(c_w1), "whole": dict(c_f0)}

    # --- F1 (unfiltered, WR's own) must be a SUPERSET of F0's vocabulary on the same sentence ------
    c_unf = WR.raw_counts_unfiltered_for_window(s, "dax")
    assert set(c_f0) <= set(c_unf), "F0's kept vocabulary must be a subset of F1's unfiltered one"
    assert "the" in c_unf and "the" not in c_f0, "F1 must keep the stopword F0 drops: %r" % c_unf
    ev["F1_superset_of_F0"] = True

    # --- N1: matched keep-count, and the drawn tokens are a subset of the unfiltered pool ----------
    rng = np.random.default_rng(3)
    keep_n = sum(c_f0.values())
    c_n1 = raw_counts_random_filter_for_window(s, "dax", keep_n, rng)
    assert sum(c_n1.values()) == min(keep_n, sum(c_unf.values())), "N1 must match the requested count"
    pool_words = set(_TOKEN_RE.findall(s.lower()))
    assert set(c_n1) <= pool_words, "N1 must draw only from tokens actually in the sentence"
    ev["N1_matched_count"] = {"requested": keep_n, "drawn_total": sum(c_n1.values())}

    # --- F2/F3 real code path: skip gracefully if the UD front-end assets are unavailable ----------
    encoder = StructuralEncoder(repo_root=REPO)
    try:
        p2 = raw_counts_pos_strict_for_window(encoder, s, "dax")
        p3, found3 = raw_counts_syntactic_neighbours_for_window(encoder, s, "dax")
        assert found3, "target 'dax' must be found by the parser in its own fixture sentence"
        assert set(p3) <= set(c_f0) | {"dax"}, "F3 fillers must be content words (never punctuation)"
        assert isinstance(p2, Counter) and isinstance(p3, Counter)
        ev["F2_F3_real_code_path"] = {"pos_strict": dict(p2), "syntactic": dict(p3)}
    except Exception as exc:  # UD front-end assets missing -- report, do not silently pass
        ev["F2_F3_LOAD_FAILED"] = repr(exc)
        raise

    # --- GATE B: S1 must be BIT-EXACT to a reference build via reconstruct_bipolar, on a toy fixture
    toy_counts = {"anchorA": Counter({"dog": 3, "run": 1}), "anchorB": Counter({"cat": 2, "run": 2})}
    s1 = build_S1_isolated_store(["anchorA", "anchorB"], toy_counts)
    ref_a = INFO.reconstruct_bipolar(toy_counts["anchorA"], d=CTX_D)
    assert np.array_equal(s1["anchorA"], ref_a), "S1 must be bit-exact to a direct reconstruct call"
    # cross-check: building anchorA WITH anchorB absent from the input dict changes nothing
    s1_alone = build_S1_isolated_store(["anchorA"], {"anchorA": toy_counts["anchorA"]})
    assert np.array_equal(s1["anchorA"], s1_alone["anchorA"]), (
        "S1 must be identical whether or not any other anchor is present -- this is the proof "
        "that the write rule has zero cross-anchor coupling")
    ev["S1_bit_exact_and_population_independent"] = True

    # --- N2: shuffled assignment must be a real derangement (no fixed points) and change every value
    toy_store = {"a": np.array([1.0, 0.0]), "b": np.array([0.0, 1.0]), "c": np.array([1.0, 1.0])}
    n2 = build_N2_shuffled_store(toy_store, ["a", "b", "c"], seed=1)
    for w in ("a", "b", "c"):
        assert not np.array_equal(n2[w], toy_store[w]), "N2 must never leave a word with its own record"
    ev["N2_true_derangement"] = True

    # --- S2 capacity arithmetic: known-answer sanity ------------------------------------------------
    cap = s2_capacity_report(n_pop=400, d_incumbent=256, block_size=8)
    assert cap["DEGENERATE_AT_INCUMBENT_BUDGET"] is True, "400 anchors in 256 dims must be degenerate"
    assert cap["d_needed_for_nondegenerate_block_size"] == 3200
    ev["S2_capacity_known_answer"] = cap

    # --- S2 pairwise AUC really is exactly 0.5 (tautology proof), on a tiny real construction -------
    words4 = ["dog", "cat", "run", "jump"]
    rng2 = np.random.default_rng(5)
    s2_store: Dict[str, np.ndarray] = {}
    for i, w in enumerate(words4):
        v = np.zeros(len(words4) * S2_BLOCK_SIZE)
        seed = int.from_bytes(hashlib.sha256(w.encode()).digest()[:8], "big") % (2 ** 32)
        v[i * S2_BLOCK_SIZE:(i + 1) * S2_BLOCK_SIZE] = np.random.default_rng(seed).choice(
            [-1.0, 1.0], size=S2_BLOCK_SIZE)
        s2_store[w] = v
    sp = DISS.dense_scores_from_dict_store(s2_store, [("dog", "cat", "n")])
    ss = DISS.dense_scores_from_dict_store(s2_store, [("run", "jump", "v")])
    assert sp[0] == 0.0 and ss[0] == 0.0, "disjoint-block anchors must have EXACTLY zero cosine: %r %r" % (
        sp, ss)
    ev["S2_pairwise_score_is_exactly_zero_tautology"] = True

    # --- restricted hit@1: a hand-built store where w1's true partner IS the nearest neighbour ------
    hand_store = {"king": np.array([1.0, 1.0, 0.0]), "queen": np.array([1.0, 0.9, 0.0]),
                 "bread": np.array([0.0, 0.0, 1.0]), "car": np.array([-1.0, 0.2, 0.3])}
    res = restricted_hit1_and_composition(hand_store, [("king", "queen", "n")],
                                          ["king", "queen", "bread", "car"], where={})
    assert res["hit_at_1"] == 1.0, "hand-built fixture must retrieve the true near-neighbour: %r" % res
    ev["restricted_hit1_known_answer"] = res

    # --- arms-must-differ digest sensitivity ---------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr)
    ev["arms_must_differ_digest_sensitivity"] = True

    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True}

    # =============================== REUSE DISS's LICENSED POPULATION, VERBATIM =====================
    diss_pop_key = unit_key("POPULATION", DISS.CODE_VERSION, "full")
    diss_pop = load_units(DISS_OUT_DIR).get(diss_pop_key)
    if diss_pop is None:
        raise SystemExit("DISS's own POPULATION checkpoint is missing at %s -- run "
                         "exp_dissociation_score_instrument_v1.py --grid full first; this cell must "
                         "NOT rebuild the matching." % DISS_OUT_DIR)
    matchedP_full = [tuple(x) for x in diss_pop["matchedP"]]
    matchedS_full = [tuple(x) for x in diss_pop["matchedS"]]
    diss_scores_key = unit_key("SCORES", DISS.CODE_VERSION, "full")
    diss_scores = load_units(DISS_OUT_DIR).get(diss_scores_key)
    if diss_scores is None:
        raise SystemExit("DISS's own SCORES checkpoint is missing -- required for K1/N0/S0 reuse.")

    if grid == "reduced":
        word_universe = sorted(set(w for w1, w2, _p in matchedP_full + matchedS_full for w in (w1, w2)))
        keep_words = set(word_universe[:N_SMOKE_WORDS])
        matchedP = [t for t in matchedP_full if t[0] in keep_words and t[1] in keep_words]
        matchedS = [t for t in matchedS_full if t[0] in keep_words and t[1] in keep_words]
        if len(matchedP) < 5 or len(matchedS) < 5:
            matchedP, matchedS = matchedP_full[:15], matchedS_full[:15]
    else:
        matchedP, matchedS = matchedP_full, matchedS_full

    rep["N_MATCHED_PAIRS_PER_CELL"] = len(matchedP)
    rep["REGRESSION_GATE_POPULATION"] = {
        "PASS": bool(grid == "reduced" or (len(matchedP) == 242 and len(matchedS) == 242)),
        "measured_n_P": len(matchedP), "measured_n_S": len(matchedS),
        "expected_full_n_per_cell": 242}
    if grid == "full" and not rep["REGRESSION_GATE_POPULATION"]["PASS"]:
        raise SystemExit("DISS's population size drifted from the licensed 242/242 -- REGRESSION "
                         "GATE FAILED: %r" % rep["REGRESSION_GATE_POPULATION"])

    words_needed = sorted(set(w for w1, w2, _p in matchedP + matchedS for w in (w1, w2)))
    print("[population] %d matched pairs/cell, %d distinct words needed" % (
        len(matchedP), len(words_needed)), flush=True)

    sents, buckets, _counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    where = {w: set(buckets.get(w, [])) for w in words_needed}

    # =============================== GATE A: FILTER (checkpointed unit) =============================
    gate_a_key = unit_key("GATE_A_SCORES", CODE_VERSION, grid)
    prior_a = load_units(out_dir_ckpt).get(gate_a_key)
    if prior_a is not None:
        print("[gate_a] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores_a = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_a["arms"].items()}
        gate_a_diag = prior_a["diag"]
        gate_a_hit1 = prior_a["hit1"]
    else:
        t0a = time.time()
        F0_counts, f0_diag = build_variant_counts(words_needed, buckets, sents, INFO.raw_counts_for_window, "F0")
        F1_counts, f1_diag = build_variant_counts(words_needed, buckets, sents, WR.raw_counts_unfiltered_for_window, "F1")

        encoder = StructuralEncoder(repo_root=REPO)
        F2_counts, f2_diag = build_variant_counts(
            words_needed, buckets, sents,
            lambda s_, a_: raw_counts_pos_strict_for_window(encoder, s_, a_), "F2")
        n_f3_found = [0]

        def _f3(s_, a_):
            c, found = raw_counts_syntactic_neighbours_for_window(encoder, s_, a_)
            if found:
                n_f3_found[0] += 1
            return c
        F3_counts, f3_diag = build_variant_counts(words_needed, buckets, sents, _f3, "F3")
        f3_diag["n_target_found_by_parser"] = n_f3_found[0]
        f3_diag["encoder_stats"] = encoder.stats()

        F4_1_counts, _ = build_variant_counts(
            words_needed, buckets, sents, lambda s_, a_: raw_counts_windowed_for_window(s_, a_, 1), "F4w1")
        F4_2_counts, _ = build_variant_counts(
            words_needed, buckets, sents, lambda s_, a_: raw_counts_windowed_for_window(s_, a_, 2), "F4w2")
        F4_5_counts, _ = build_variant_counts(
            words_needed, buckets, sents, lambda s_, a_: raw_counts_windowed_for_window(s_, a_, 5), "F4w5")
        F4_whole_counts, _ = build_variant_counts(
            words_needed, buckets, sents, lambda s_, a_: raw_counts_windowed_for_window(s_, a_, None), "F4whole")
        f4_whole_matches_f0 = all(F4_whole_counts[a] == F0_counts[a] for a in words_needed)

        rng_n1 = np.random.default_rng(MASTER_SEED + 5151)
        N1_counts = {}
        for a in words_needed:
            occ = buckets.get(a, [])
            if not occ:
                N1_counts[a] = Counter()
                continue
            keep_n = sum(F0_counts[a].values())
            N1_counts[a] = raw_counts_random_filter_for_window(sents[occ[0]], a, keep_n, rng_n1)

        gate_a_diag = {"F0": f0_diag, "F1": f1_diag, "F2": f2_diag, "F3": f3_diag,
                      "F4_whole_matches_F0_exactly": f4_whole_matches_f0,
                      "elapsed_s": round(time.time() - t0a, 1)}
        print("[gate_a] all variant counts built, elapsed=%.1fs" % (time.time() - t0a), flush=True)

        stores_a = {
            "F0_INCUMBENT": DISS.counts_to_dense_store(F0_counts, words_needed),
            "F1_NO_FILTER": DISS.counts_to_dense_store(F1_counts, words_needed),
            "F2_CONTENT_ONLY_STRICT": DISS.counts_to_dense_store(F2_counts, words_needed),
            "F3_SYNTACTIC_NEIGHBOURS_ONLY": DISS.counts_to_dense_store(F3_counts, words_needed),
            "F4_WINDOW_1": DISS.counts_to_dense_store(F4_1_counts, words_needed),
            "F4_WINDOW_2": DISS.counts_to_dense_store(F4_2_counts, words_needed),
            "F4_WINDOW_5": DISS.counts_to_dense_store(F4_5_counts, words_needed),
            "N1_RANDOM_FILTER": DISS.counts_to_dense_store(N1_counts, words_needed),
        }
        arm_scores_a = {}
        for name, store in stores_a.items():
            sp = DISS.dense_scores_from_dict_store(store, matchedP)
            ss = DISS.dense_scores_from_dict_store(store, matchedS)
            arm_scores_a[name] = {"P": sp, "S": ss}

        gate_a_hit1 = {}
        for name, store in stores_a.items():
            gate_a_hit1[name] = restricted_hit1_and_composition(store, matchedP, words_needed, where)

        record_unit(out_dir_ckpt, gate_a_key, {
            "arms": {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in arm_scores_a.items()},
            "diag": gate_a_diag, "hit1": gate_a_hit1})

    rep["GATE_A_DIAG"] = gate_a_diag
    rep["GATE_A_RESTRICTED_HIT1_AND_COMPOSITION"] = gate_a_hit1

    boot_seed_base = MASTER_SEED + 7171
    gate_a_auc = {}
    for i, (name, sc) in enumerate(arm_scores_a.items()):
        gate_a_auc[name] = DISS.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + i)
        print("[gate_a auc] %-28s AUC=%.4f CI=%r band=%s" % (
            name, gate_a_auc[name]["auc"], gate_a_auc[name]["ci95"], gate_a_auc[name]["band"]), flush=True)
    rep["GATE_A_AUC_PER_ARM"] = gate_a_auc

    digests_a = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores_a.items()}
    assert len(set(digests_a.values())) > 1, "GATE A: all arms produced identical score vectors"
    rep["GATE_A_ARM_DIGESTS"] = digests_a

    # =============================== GATE A REGRESSION vs DISS's own RAW_COUNT_SINGLE_OCC ============
    diss_single = {"P": np.array(diss_scores["RAW_COUNT_SINGLE_OCC"]["P"]),
                  "S": np.array(diss_scores["RAW_COUNT_SINGLE_OCC"]["S"])}
    if grid == "full":
        match_p = np.allclose(diss_single["P"], arm_scores_a["F0_INCUMBENT"]["P"], atol=1e-4, equal_nan=True)
        match_s = np.allclose(diss_single["S"], arm_scores_a["F0_INCUMBENT"]["S"], atol=1e-4, equal_nan=True)
        rep["GATE_A_REGRESSION_vs_DISS_RAW_COUNT_SINGLE_OCC"] = {
            "PASS": bool(match_p and match_s), "note": "F0_INCUMBENT must reproduce DISS's own "
            "RAW_COUNT_SINGLE_OCC arm bit-for-bit (identical construction, identical population)"}
        if not rep["GATE_A_REGRESSION_vs_DISS_RAW_COUNT_SINGLE_OCC"]["PASS"]:
            raise SystemExit("GATE A REGRESSION FAILED: F0 does not reproduce DISS's RAW_COUNT_SINGLE_OCC")

    # =============================== GATE B: SUPERPOSE (checkpointed unit) ===========================
    gate_b_key = unit_key("GATE_B_SCORES", CODE_VERSION, grid)
    prior_b = load_units(out_dir_ckpt).get(gate_b_key)
    if prior_b is not None:
        print("[gate_b] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores_b = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_b["arms"].items()}
        gate_b_diag = prior_b["diag"]
        gate_b_hit1 = prior_b["hit1"]
    else:
        t0b = time.time()
        C = DISS.CTS.load_cache()
        anchors_all = C["anchors"]
        mat = np.asarray(C["mat"], dtype=np.float32)
        pos_idx = C["pos"]

        units_info = load_units(INFO_OUT_DIR)
        counts_full: Dict[str, Counter] = {}
        missing = []
        for w in words_needed:
            rec = units_info.get(unit_key("Pstore", w))
            if rec is None:
                missing.append(w)
                continue
            counts_full[w] = Counter(rec["counts"])
        if missing:
            raise SystemExit("INFO's Pstore checkpoint missing entries this cell needs: %r" % missing[:20])

        store_s0 = {w: DISS.l2n(mat)[pos_idx[w]] for w in words_needed if w in pos_idx}
        store_s1_raw = build_S1_isolated_store(words_needed, counts_full)
        # S1 is scored directly from reconstruct_bipolar vectors (l2-normalised here, not via the
        # sparse-count path -- this is the DENSE H^T p reconstruction, matching S0's own dense arm).
        store_s1 = {}
        for w, v in store_s1_raw.items():
            nrm = float(np.linalg.norm(v))
            store_s1[w] = (v / nrm) if nrm > 1e-9 else v

        # --- proof: S1 matches S0 bit-close on the words this cell actually needs -------------------
        s1_vs_s0_maxerr = 0.0
        n_checked_s1 = 0
        for w in words_needed:
            if w in store_s0 and w in store_s1:
                s1_vs_s0_maxerr = max(s1_vs_s0_maxerr,
                                      float(np.max(np.abs(store_s0[w] - store_s1[w]))))
                n_checked_s1 += 1
        gate_b_s1_proof = {"n_checked": n_checked_s1, "max_abs_error_vs_S0": s1_vs_s0_maxerr,
                           "BIT_EXACT": bool(s1_vs_s0_maxerr < 1e-4)}

        store_n2 = build_N2_shuffled_store(store_s0, words_needed, seed=MASTER_SEED + 9292)

        cap = s2_capacity_report(n_pop=len(words_needed), d_incumbent=int(mat.shape[1]),
                                 block_size=S2_BLOCK_SIZE)
        # S2 proof-of-tautology on the REAL matched-pair words (not just the toy fixture in self_test):
        # build a real disjoint-block store at the capacity-honest dimensionality and confirm every
        # cross-anchor pairwise score is exactly zero.
        words_s2 = words_needed
        d_s2 = len(words_s2) * S2_BLOCK_SIZE
        store_s2 = {}
        for i, w in enumerate(words_s2):
            v = np.zeros(d_s2, dtype=np.float64)
            cnt = counts_full.get(w, Counter())
            block = np.zeros(S2_BLOCK_SIZE, dtype=np.float64)
            for cw_, c_ in cnt.items():
                seed = int.from_bytes(hashlib.sha256((w + "|" + cw_).encode("utf-8")).digest()[:8],
                                      "big") % (2 ** 32)
                block += float(c_) * np.random.default_rng(seed).choice([-1.0, 1.0], size=S2_BLOCK_SIZE)
            v[i * S2_BLOCK_SIZE:(i + 1) * S2_BLOCK_SIZE] = block
            nrm = float(np.linalg.norm(v))
            store_s2[w] = v / nrm if nrm > 1e-9 else v

        gate_b_diag = {"S1_bit_exact_proof": gate_b_s1_proof, "S2_capacity": cap,
                      "elapsed_s": round(time.time() - t0b, 1)}
        print("[gate_b] S1 proof max_abs_error=%.2e (BIT_EXACT=%r)" % (
            gate_b_s1_proof["max_abs_error_vs_S0"], gate_b_s1_proof["BIT_EXACT"]), flush=True)

        arm_scores_b = {
            "S0_INCUMBENT": {"P": DISS.dense_scores_from_dict_store(store_s0, matchedP),
                            "S": DISS.dense_scores_from_dict_store(store_s0, matchedS)},
            "S1_PER_ANCHOR_ISOLATED": {"P": DISS.dense_scores_from_dict_store(store_s1, matchedP),
                                       "S": DISS.dense_scores_from_dict_store(store_s1, matchedS)},
            "S2_DISJOINT_SUBSPACES": {"P": DISS.dense_scores_from_dict_store(store_s2, matchedP),
                                      "S": DISS.dense_scores_from_dict_store(store_s2, matchedS)},
            "N2_SHUFFLED_ASSIGNMENT": {"P": DISS.dense_scores_from_dict_store(store_n2, matchedP),
                                       "S": DISS.dense_scores_from_dict_store(store_n2, matchedS)},
        }
        gate_b_hit1 = {
            "S0_INCUMBENT": restricted_hit1_and_composition(store_s0, matchedP, words_needed, where),
            "S1_PER_ANCHOR_ISOLATED": {"note": "identical to S0 by the bit-exact proof above; not "
                                       "recomputed", "same_as": "S0_INCUMBENT"},
            "S2_DISJOINT_SUBSPACES": {"note": "UNMEASURABLE by construction -- every cross-anchor "
                                      "cosine is exactly 0 (disjoint support), so argmax over the "
                                      "field is undefined (all-tied); not fabricated"},
            "N2_SHUFFLED_ASSIGNMENT": restricted_hit1_and_composition(store_n2, matchedP, words_needed, where),
        }

        record_unit(out_dir_ckpt, gate_b_key, {
            "arms": {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in arm_scores_b.items()},
            "diag": gate_b_diag, "hit1": gate_b_hit1})

    rep["GATE_B_DIAG"] = gate_b_diag
    rep["GATE_B_RESTRICTED_HIT1_AND_COMPOSITION"] = gate_b_hit1

    gate_b_auc = {}
    for i, (name, sc) in enumerate(arm_scores_b.items()):
        gate_b_auc[name] = DISS.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + 5000 + i)
        print("[gate_b auc] %-28s AUC=%.4f CI=%r band=%s" % (
            name, gate_b_auc[name]["auc"], gate_b_auc[name]["ci95"], gate_b_auc[name]["band"]), flush=True)
    rep["GATE_B_AUC_PER_ARM"] = gate_b_auc

    # arms-must-differ for Gate B EXCLUDING S2 (S2's constant-zero score is the tautology proof
    # itself, not a construction bug -- declared exempt in the module docstring)
    digests_b = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores_b.items()
                if k != "S2_DISJOINT_SUBSPACES"}
    assert len(set(digests_b.values())) > 1, "GATE B (excl. S2): all arms identical -- construction bug"
    rep["GATE_B_ARM_DIGESTS"] = digests_b
    s2_all_zero = bool(np.allclose(arm_scores_b["S2_DISJOINT_SUBSPACES"]["P"], 0.0) and
                       np.allclose(arm_scores_b["S2_DISJOINT_SUBSPACES"]["S"], 0.0))
    rep["GATE_B_S2_TAUTOLOGY_CONFIRMED"] = s2_all_zero

    # =============================== GATE B REGRESSION vs DISS's own INCUMBENT_LIVE_STORE ============
    diss_incumbent = {"P": np.array(diss_scores["INCUMBENT_LIVE_STORE"]["P"]),
                      "S": np.array(diss_scores["INCUMBENT_LIVE_STORE"]["S"])}
    if grid == "full":
        match_p = np.allclose(diss_incumbent["P"], arm_scores_b["S0_INCUMBENT"]["P"], atol=1e-4, equal_nan=True)
        match_s = np.allclose(diss_incumbent["S"], arm_scores_b["S0_INCUMBENT"]["S"], atol=1e-4, equal_nan=True)
        rep["GATE_B_REGRESSION_vs_DISS_INCUMBENT_LIVE_STORE"] = {"PASS": bool(match_p and match_s)}
        if not rep["GATE_B_REGRESSION_vs_DISS_INCUMBENT_LIVE_STORE"]["PASS"]:
            raise SystemExit("GATE B REGRESSION FAILED: S0 does not reproduce DISS's INCUMBENT_LIVE_STORE")

    # =============================== K1 / N0, reused verbatim from DISS's own checkpoint =============
    k1_p = np.array(diss_scores["KNOWN_ANSWER_WORDNET_PATH_SIM"]["P"])
    k1_s = np.array(diss_scores["KNOWN_ANSWER_WORDNET_PATH_SIM"]["S"])
    n0_p = np.array(diss_scores["RANDOM_VECTOR_STORE"]["P"])
    n0_s = np.array(diss_scores["RANDOM_VECTOR_STORE"]["S"])
    if grid == "full":
        k1_res = DISS.auc_bootstrap(k1_p, k1_s, N_BOOT, boot_seed_base + 9999)
        n0_res = DISS.auc_bootstrap(n0_p, n0_s, N_BOOT, boot_seed_base + 10000)
    else:
        n_sm = len(matchedP)
        k1_res = DISS.auc_bootstrap(k1_p[:n_sm], k1_s[:n_sm], N_BOOT, boot_seed_base + 9999)
        n0_res = DISS.auc_bootstrap(n0_p[:n_sm], n0_s[:n_sm], N_BOOT, boot_seed_base + 10000)
    rep["K1_KNOWN_ANSWER_WORDNET_PATH_SIM"] = k1_res
    rep["N0_RANDOM_VECTOR_STORE"] = n0_res
    rep["K1_N0_SOURCE"] = "reused verbatim from DISS's own SCORES checkpoint, re-bootstrapped here"

    # =============================== FLOORS -- population-level, reused (not rebuilt) ================
    rep["FLOORS_SOURCE"] = ("this cell reuses DISS's own POPULATION verbatim (unchanged), so DISS's "
                            "already-licensed floor AUCs (F_ORTHOGRAPHIC/F_FREQUENCY/F_SCRAMBLE/"
                            "F_CONSTANT_PROTOTYPE, all NOT_SEPARATED from 0.5 at full scale) remain "
                            "valid for this population without re-derivation; they are properties of "
                            "the PAIR SET, not of the FILTER/SUPERPOSE arm being scored")
    diss_metrics_path = os.path.join(DISS_OUT_DIR, "metrics.json")
    if os.path.exists(diss_metrics_path):
        with open(diss_metrics_path, "r", encoding="utf-8") as fh:
            diss_metrics = json.load(fh)
        rep["FLOORS_FROM_DISS"] = diss_metrics.get("report", {}).get("AUC_PER_ARM", {})

    # =============================== STOP-IF EVALUATION ===============================================
    def _band(a): return gate_a_auc[a]["band"]
    def _hw(a): return gate_a_auc[a]["ci_halfwidth"]
    f0_auc, n1_auc = gate_a_auc["F0_INCUMBENT"]["auc"], gate_a_auc["N1_RANDOM_FILTER"]["auc"]
    f0_ci, n1_ci = gate_a_auc["F0_INCUMBENT"]["ci95"], gate_a_auc["N1_RANDOM_FILTER"]["ci95"]
    filter_arms = ["F1_NO_FILTER", "F2_CONTENT_ONLY_STRICT", "F3_SYNTACTIC_NEIGHBOURS_ONLY",
                  "F4_WINDOW_1", "F4_WINDOW_2", "F4_WINDOW_5"]
    stopif_i_fired = any(gate_a_auc[a]["ci95"][0] > f0_ci[1] and gate_a_auc[a]["ci95"][0] > n1_ci[1]
                         for a in filter_arms)
    stopif_ii_fired = not (gate_a_auc["F1_NO_FILTER"]["ci95"][1] < f0_ci[0])  # F1 must NOT be worse
    stopif_iii_fired = bool(gate_b_diag["S1_bit_exact_proof"]["BIT_EXACT"])
    s1_ci = gate_b_auc["S1_PER_ANCHOR_ISOLATED"]["ci95"]
    s0_ci = gate_b_auc["S0_INCUMBENT"]["ci95"]
    stopif_iv_fired = bool(s1_ci[0] > s0_ci[1] or s0_ci[0] > s1_ci[1])
    all_gate_a_ci = [gate_a_auc[a]["ci95"] for a in ["F0_INCUMBENT"] + filter_arms]
    all_gate_b_ci = [gate_b_auc[a]["ci95"] for a in ["S0_INCUMBENT", "N2_SHUFFLED_ASSIGNMENT"]]
    los_a = [c[0] for c in all_gate_a_ci]
    his_a = [c[1] for c in all_gate_a_ci]
    gate_a_all_tie = bool(max(los_a) <= min(his_a))
    stopif_v_fired = bool(gate_a_all_tie and stopif_iii_fired)

    rep["STOP_IF"] = {
        "i_filter_arm_above_F0_and_above_N1": {"FIRED": stopif_i_fired},
        "ii_F1_no_filter_fails_to_be_worse_than_F0": {"FIRED": stopif_ii_fired,
            "F1_auc": gate_a_auc["F1_NO_FILTER"]["auc"], "F0_auc": f0_auc},
        "iii_S1_matches_S0_SUPERPOSE_exonerated": {"FIRED": stopif_iii_fired,
            "max_abs_error": gate_b_diag["S1_bit_exact_proof"]["max_abs_error_vs_S0"]},
        "iv_S1_beats_S0_CI_separated": {"FIRED": stopif_iv_fired},
        "v_all_arms_tie_both_gates_exonerated": {"FIRED": stopif_v_fired,
            "gate_a_all_arms_mutually_ci_overlap": gate_a_all_tie},
        "vi_K1_fails_instrument_still_loose": {"FIRED": bool(k1_res["auc"] < 0.95)},
    }

    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    stopif = rep.get("STOP_IF", {})
    if stopif.get("vi_K1_fails_instrument_still_loose", {}).get("FIRED"):
        verdict = "INSTRUMENT_STILL_LOOSE_NO_PUBLISH"
    elif stopif.get("v_all_arms_tie_both_gates_exonerated", {}).get("FIRED"):
        verdict = "BOTH_GATES_EXONERATED_WRITE_RULE_FULLY_GATED_DEFECT_LOCALISED_TO_ACCUMULATE"
    else:
        i_fired = stopif.get("i_filter_arm_above_F0_and_above_N1", {}).get("FIRED")
        iii_fired = stopif.get("iii_S1_matches_S0_SUPERPOSE_exonerated", {}).get("FIRED")
        iv_fired = stopif.get("iv_S1_beats_S0_CI_separated", {}).get("FIRED")
        parts = []
        parts.append("FILTER_LOAD_BEARING" if i_fired else "FILTER_NOT_LOAD_BEARING")
        if iii_fired:
            parts.append("SUPERPOSE_EXONERATED")
        elif iv_fired:
            parts.append("SUPERPOSE_IS_A_REAL_COST")
        else:
            parts.append("SUPERPOSE_UNRESOLVED")
        verdict = "__".join(parts)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("ORGAN A write-rule gate: FILTER (F0-F4, N1) and SUPERPOSE (S0-S2, N2), on "
                       "the licensed dissociation AUC instrument, matched pairs and scorer reused "
                       "verbatim from exp_dissociation_score_instrument_v1. -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "S2_BLOCK_SIZE": S2_BLOCK_SIZE,
                  "N_SMOKE_WORDS": N_SMOKE_WORDS},
        "selftest_evidence_keys": sorted(ev.keys()),
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(3)
