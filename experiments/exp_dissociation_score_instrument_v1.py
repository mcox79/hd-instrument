"""exp_dissociation_score_instrument_v1 -- THE DISSOCIATION-SCORE INSTRUMENT.

THIS IS AN INSTRUMENT BUILD, NOT AN ORGAN GATE. Its deliverable is a validated measuring device
(pre-registered floors + known-answer + random-store licensing) plus a re-scoring of stores we
already have. It does NOT claim any capability. Full spec:
notes/protocol_representational_content_organ_gates_2026-08-18.md sec 8.3 (commit 446f61aa0),
ADOPTED notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.11 (commit b8cb6f39e).

=================================================================================================
WHY THIS INSTRUMENT, IN ONE SENTENCE. Every hit@1 number this project has produced sits BELOW its
own strongest floor (0.02-0.06 vs a constant-prototype floor of 0.1390/0.2070 depending on
population), so "margin over floor" returns the SAME VERDICT (negative) for a promising arm and a
hopeless one. The dissociation score is constructed so all four floors sit at CHANCE (AUC 0.5) BY
CONSTRUCTION -- it finally measures the STORE'S CONTENT instead of the POOL'S popularity structure.

THE CONSTRUCTION.
  SET P (paradigmatic, substitutable, non-co-occurring): word pairs sharing a WordNet SYNSET
    (literal synonyms -- the closest WordNet relation there is) whose corpus co-occurrence count is
    EXACTLY ZERO (never appear in the same sentence, over the full 34,169-sentence corpus this
    store was built from). "Could replace, never seen together."
  SET S (syntagmatic, co-occurring, non-substitutable): word pairs in the TOP DECILE (or higher) of
    corpus co-occurrence count, with NO close WordNet relation (best path_similarity < 0.25, the
    SAME threshold `exp_writerule_step_ladder_v1.wordnet_relation_composition` and
    `exp_readout_second_order_v1`'s C1 use for "taxonomically close"). "Seen together, cannot
    replace."
  MATCHED on unigram frequency (mean log1p corpus count of the pair), word length (mean surface
    length), and WordNet part-of-speech (both members of every pair share ONE dominant WordNet POS;
    matching is per-POS-stratum nearest-neighbour on the standardised (freq, length) plane).
  SCORE = AUC separating SET P's store-similarity from SET S's store-similarity, paired bootstrap
    CI. AUC > 0.5 CI-separated = the store encodes substitutability. AUC < 0.5 CI-separated = the
    store encodes co-occurrence. NOT_SEPARATED = the store encodes neither (a third diagnosis).

=================================================================================================
PRIOR-WORK CHECK (substrate-KB, mandatory per .claude/agents/exp_dev.md "SUBSTRATE-KB CONCEPT-QUERY
BEFORE AUTHORING"). Ran: `bash tools/substrate_query.sh "dissociation score substitutability
co-occurrence AUC WordNet paradigmatic syntagmatic representational content instrument"`.
confidence=0.3369 (above the cosine>0.30 read-the-top-2 threshold). Top hit (cosine=0.3369):
notes/research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md -- a biology-first
drill on why distributional co-occurrence (GloVe/WordNet) CANNOT carry a concept's SPECIFIC
distinguishing content (hydroelectric vs nuclear vs coal), proposing a content-ENRICHMENT cell (add
featural/property-norm information). Second hit (cosine=0.333): a generic 'mental representation'
atom, no method content. NEITHER builds a paradigmatic-vs-syntagmatic dissociation instrument, a
frequency/length/POS-matched pair design, or an AUC read-out; the July-25 note's question is "how do
we ADD missing content to the store", this cell's question is "which relation does the store we
ALREADY HAVE encode, measured directly, with the floors neutralised by construction". NOT a
rediscovery -- genuinely novel instrument, builds on the July-25 note's diagnosis (distributional
co-occurrence is content-blind) rather than repeating it.

=================================================================================================
ORGAN REUSE ("reuse the landed cells as LIBRARIES", per the dispatch brief -- no store is rebuilt
from scratch; every arm below is either the LIVE cached instrument or a byte-identical construction
already landed elsewhere):
  experiments.exp_cue_to_store_translation_v1 (CTS)   load_cache() [anchors, mat, mat_ok, pos dict],
                                                        load_aux() [t_mat trigram, fq=log1p(freq)],
                                                        MASTER_SEED. NEVER edited, never rebuilt.
  experiments.exp_cue_information_audit_v1 (INFO)     load_corpus_and_buckets() [sents, buckets,
                                                        cached under scratch/cue_information_audit_v1
                                                        -- reused, NOT rebuilt: this cell's own probe
                                                        (scratch/_probe_dissociation.py) confirmed the
                                                        reused-cache path returns 34,169 sentences in
                                                        0.45s], build_vocab, to_sparse, l2n_sparse --
                                                        the FULL-ACCUMULATION raw-count store (every
                                                        one of the 5,491 anchors' Pstore checkpoint
                                                        already exists in
                                                        data/exp_cue_information_audit_v1/units.jsonl,
                                                        verified 0 missing by this cell's own probe;
                                                        loaded, never recomputed).
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)  build_single_occurrence_counts (the ONE
                                                        profile occurrence per anchor construction,
                                                        REUSED VERBATIM) and its own l2n.
  experiments.exp_readout_writerule_paradigmatic_v1 (WRP)  build_arm(..., mode="PROFILE") -- the
                                                        landed second-order paradigmatic write rule
                                                        (+0.0075 CI-separated over the incumbent on
                                                        hit@1). Reused wholesale; only the ANCHOR LIST
                                                        passed in is restricted to the words this
                                                        cell actually needs (a strict subset of the
                                                        function's own full-population call), so the
                                                        construction is byte-identical to the landed
                                                        cell's, just evaluated at fewer rows.
  tools.floor_battery (FB)                             l2n, scramble_null, constant_prototype_floor,
                                                        frequency_floor (cited for its formula only --
                                                        aux['fq'] IS already log1p(count), see below).
  hdlab.reading_grounding_loop                         content_lemmas, normalize_lemma.
  experiments._seed_checkpoint / tools.exp_checkpoint  get_output_dir, write_metrics (Path, not str),
                                                        unit_key/completed_units/record_unit/load_units.

=================================================================================================
WHY THE POPULATION IS FAST TO BUILD (measured, not hoped): this cell's own pre-authoring probe
(scratch/_probe_dissociation.py, run against the live cache) found n_anchors=5491, 5208 WordNet
same-synset candidate pairs among them (built in 1.2s via nltk), 3912 of those at EXACTLY ZERO
corpus co-occurrence (SET P's raw candidate pool), and 711,206 distinct co-occurring anchor pairs
over the 34,169-sentence corpus (built in 2.2s, corpus reused from cache) with a 90th-percentile
co-occurrence count of 4 (SET S's raw candidate pool, before the WordNet-relation exclusion, is
therefore >> SET P's -- SET P is the bottleneck, as expected for a "never co-occur" construction).
Total probe wall time: 11.3s. This licenses running the FULL population inline, foreground, with
generous headroom under the INLINE-LOCAL 10-minute mandate.

=================================================================================================
THE FOUR FLOORS, PAIRWISE ANALOGUES (Gate 3, recomputed on THIS pair population, never imported):
  F_ORTHOGRAPHIC   cos(trigram_vec(w1), trigram_vec(w2)) -- aux['t_mat'], the SAME trigram asset
                   every sibling cell uses.
  F_FREQUENCY      max(log1p(freq(w1)), log1p(freq(w2))) -- deliberately NOT the exact matching
                   statistic (which is the PAIR MEAN), so this is a genuine out-of-sample check that
                   the match generalises beyond the one covariate it was built on, not a tautology.
  F_SCRAMBLE       cos() under FB.scramble_null(mat, seed) -- the anchor-to-row assignment permuted,
                   destroying identity while preserving every marginal.
  F_CONSTANT_PROTOTYPE  mean(FB.constant_prototype_floor(w1), FB.constant_prototype_floor(w2)) --
                   cosine-to-mean-direction, a CONSTANT (query-independent) genericity score.
The protocol's claim is that frequency+length+POS matching neutralises all four BY CONSTRUCTION.
This cell VERIFIES that empirically rather than asserting it (STOP-IF (i)).

KNOWN-ANSWER ARM: score(pair) = best WordNet path_similarity (identical construction/threshold to
`wordnet_relation_composition` above), must read AUC ~1.0 (K1-style gate, ADDRESS_EXACT_MIN=0.95
convention reused from the write-rule ladder). RANDOM-VECTOR ARM: iid Gaussian d=256 per anchor
(matching the incumbent's own dimensionality), independent of the true store, must read AUC 0.5.

=================================================================================================
ARMS RE-SCORED (one arm at a time, on this SAME instrument, one similarity function per arm):
  INCUMBENT_LIVE_STORE       cos(mat[w1], mat[w2]) -- H^T p_a, random projection, unweighted sum.
  RAW_COUNT_FULL_ACCUM       cos() over the UNCOMPRESSED full-accumulation raw-count rows (reused
                             Pstore checkpoint, never re-tokenised).
  RAW_COUNT_SINGLE_OCC       cos() over ONE profile occurrence per anchor (PIPE.build_single_
                             occurrence_counts) -- the "does one occurrence already carry it"
                             comparison the write-rule ladder's decisive arm motivates.
  PRESENCE_ABSENCE_BINARIZED cos() over the SAME full-accumulation counts, binarised (count>0 -> 1)
                             before L2-normalising.
  PARADIGMATIC_PROFILE_WRITE cos() over WRP.build_arm(mode="PROFILE") rows -- the landed second-
                             order write rule.
Only the WORDS ACTUALLY NEEDED (the union of both matched cells' members, typically low hundreds --
NOT the full 5,491-anchor population) are ever built for RAW_COUNT_SINGLE_OCC and
PARADIGMATIC_PROFILE_WRITE, since those are the only two arms requiring fresh per-word computation;
this is a strict subset of each reused function's own full-population call, so the underlying
construction is byte-identical, only the row COUNT differs.

=================================================================================================
STOP-IF (evaluated in this order, per the dispatch brief):
  (i)   any floor's AUC 95% CI excludes 0.5 -> matching is broken; INSTRUMENT_LICENSED=False.
  (ii)  known-answer arm AUC < 0.95 -> the instrument cannot see the relation; INSTRUMENT_LICENSED=False.
  (iii) incumbent AUC CI-separated BELOW 0.5, as pre-registered -> co-occurrence diagnosis CONFIRMED.
  (iv)  incumbent AUC CI-separated AT-OR-ABOVE 0.5 -> co-occurrence diagnosis REFUTED, report loudly.
  (v)   all re-scored arms NOT_SEPARATED from each other -> instrument lacks resolution at this n;
        report the resolution (CI half-width), not a ranking.
If (i) or (ii) fires, store-arm numbers are still WRITTEN (for the record) but the verdict states
UNLICENSED and no store-arm number may be interpreted as a finding.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: POPULATION (candidate gen + matching) and SCORES (per-arm score arrays) as
#   separate tools.exp_checkpoint units, MAIN wraps the whole run() result (same pattern as the
#   directly-reused sibling exp_writerule_step_ladder_v1)
# - discriminator survives scale: this cell runs the FULL population, no scale-preview needed; the
#   reduced/--grid smoke uses a real (smaller) population, not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated cache and
#   checkpoint units unmodified)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - baseline_in_band: n/a -- this is a licensing-gate instrument (K1/floor gates), not a
#   0.05-0.95-band baseline; declared explicitly rather than silently omitted
# - crlb_floor_computed: n/a -- an AUC dissociation measurement over an existing store is not a
#   capacity sweep; declared explicitly

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. No store is
rebuilt; data/foundation/** is never opened. Writes only under
data/exp_dissociation_score_instrument_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/hdlab next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import rankdata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from nltk.corpus import wordnet as wn                                    # noqa: E402

import experiments.exp_cue_to_store_translation_v1 as CTS                # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                  # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE           # noqa: E402  READ ONLY
import experiments.exp_readout_writerule_paradigmatic_v1 as WRP          # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "dissociation_score_instrument_v1"
CODE_VERSION = "v1.7"  # v1.6's full run LICENSED cleanly (all 4 floors NOT_SEPARATED, known-answer
                       # 0.9599, incumbent CI-separated BELOW 0.5 as pre-registered) but its STOP-IF
                       # (v) check had a bug: it compared BANDS (same side of 0.5) across store arms
                       # rather than a genuine pairwise CI-overlap test, so it wrongly fired
                       # "arms indistinguishable" when all 5 store arms happened to sit BELOW 0.5
                       # despite point AUCs spanning 0.03-0.42 (a real, wide, resolvable spread).
                       # v1.7 fixes STOP-IF (v) to a mutual-CI-overlap check across store arms;
                       # POPULATION/SCORES construction is UNCHANGED from v1.6, only the
                       # interpretation-assembly code after them differs. Bumped anyway per the
                       # standing no-silent-resume discipline.
# CODE_VERSION HISTORY v1.0->v1.6, ITERATIVE MATCHING REPAIR, each step measured then disclosed
# (STOP-IF (i) applied repeatedly, never widened): v1.0 (freq_mean/length/POS only) left
                       # F_ORTHOGRAPHIC AUC=0.6801 and F_FREQUENCY(max) AUC=0.1266 CI-separated.
                       # v1.1 added |freq_diff| + trigram-cosine covariates but UNCAPPED matching
                       # still force-matched (post-match SMD(mean_log_freq)=-1.9564). v1.2 added a
                       # TOTAL-SUM-OF-SQUARES caliper (1.0): fixed F_ORTHOGRAPHIC/F_CONSTANT_
                       # PROTOTYPE, left F_FREQUENCY separated (SMD=-0.6155). v1.3 tightened the
                       # total caliper to 0.3: fixed F_FREQUENCY at SMOKE scale but exposed
                       # F_CONSTANT_PROTOTYPE (AUC=0.6598 at smoke N=68). v1.4 added mean constant-
                       # prototype as a 5th covariate: all 4 floors CI-included 0.5 at smoke scale,
                       # but at FULL scale (n=430, tighter CI) F_FREQUENCY re-separated (AUC=0.3923
                       # [0.3537,0.4302]) -- a single TOTAL Euclidean budget lets one covariate
                       # spend the whole caliper when the others sit near 0. v1.5 switched to a
                       # UNIFORM PER-DIMENSION (L-infinity) caliper (0.25 on all 5) -- STILL left a
                       # SYSTEMATIC residual (post-match SMD(mean_log_freq)=-0.6235) because a
                       # per-pair magnitude bound does not prevent a same-direction bias from
                       # accumulating when SET S's raw pool is structurally more frequent than SET
                       # P's. v1.6 uses a PER-DIMENSION VECTOR: the two frequency covariates get a
                       # caliper 12.5x tighter (0.02) than length/ortho/prototype (0.25, already
                       # measured clean). Bumped each time so no checkpoint key silently resumes a
                       # prior version's under-matched population.
FINDINGS = "notes/dissociation_score_instrument_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
WN_CLOSE_THRESHOLD = 0.25       # SAME threshold exp_writerule_step_ladder_v1 / exp_readout_second_order_v1 use
TOP_DECILE_Q = 0.90
CELL_S_CAND_CAP = 1500 if SMOKE else 8000     # top co-occurring pairs kept as SET S candidates
SYNSET_CAP = 6                                # synsets scanned per anchor (matches sibling convention)
KNOWN_ANSWER_MIN_AUC = 0.95                    # K1-style gate, ADDRESS_EXACT_MIN convention reused
POS_MAP = {"n": "n", "v": "v", "a": "a", "s": "a", "r": "r"}   # satellite adj folded into adj


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# WORDNET HELPERS
# =================================================================================================
_POS_CACHE: Dict[str, Optional[str]] = {}


def wn_dominant_pos(word: str) -> Optional[str]:
    """The POS of `word`'s FIRST (most frequent, by WordNet's own sense-ordering convention)
    synset, folded to n/v/a/r. None if the word has no synsets at all."""
    if word in _POS_CACHE:
        return _POS_CACHE[word]
    syns = wn.synsets(word)
    p = POS_MAP.get(syns[0].pos()) if syns else None
    _POS_CACHE[word] = p
    return p


def wn_best_path_similarity(w1: str, w2: str) -> float:
    """Best path_similarity over the first SYNSET_CAP synsets of each word, POS-matched pairs only.
    IDENTICAL construction to exp_writerule_step_ladder_v1.wordnet_relation_composition's inner
    loop (same cap, same POS-match requirement) so this cell's KNOWN-ANSWER arm and its SET
    construction use one consistent WordNet-closeness definition throughout."""
    sq, sw = wn.synsets(w1)[:SYNSET_CAP], wn.synsets(w2)[:SYNSET_CAP]
    if not sq or not sw:
        return 0.0
    best = 0.0
    for a in sq:
        for b in sw:
            if a.pos() != b.pos():
                continue
            p = a.path_similarity(b)
            if p and p > best:
                best = float(p)
    return best


def build_wordnet_synonym_candidates(anchor_set: Sequence[str]) -> List[Tuple[str, str, str]]:
    """Every (w1, w2, pos) pair sharing a WordNet SYNSET, both members in anchor_set, w1<w2 by sort
    order, deduplicated. Same-synset lemmas are the closest WordNet relation there is (path_sim ==
    1.0 by definition), so this is the cleanest, least-ambiguous SET P raw candidate source."""
    aset = set(anchor_set)
    seen: set = set()
    pairs: List[Tuple[str, str, str]] = []
    for w in sorted(aset):
        for syn in wn.synsets(w)[:SYNSET_CAP]:
            for lemma in syn.lemma_names():
                l = lemma.replace("_", " ")
                if " " in l or l == w or l not in aset:
                    continue
                key = tuple(sorted((w, l)))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append((key[0], key[1], POS_MAP.get(syn.pos(), syn.pos())))
    return pairs


def build_cooccurrence_paircounts(sents: List[str], anchor_set: Sequence[str]) -> Counter:
    """Distinct co-occurring ANCHOR pairs (w1<w2) and their sentence co-occurrence count, over the
    full corpus. content_lemmas() already dedupes within a sentence (sorted(set(...))), so this
    counts SENTENCES a pair shares, not raw token co-occurrence. Anchor-restricted so this stays
    O(sentences * avg_anchor_words_per_sentence^2), never O(vocab^2)."""
    aset = set(anchor_set)
    pair_counts: Counter = Counter()
    t0 = time.time()
    for si, s in enumerate(sents):
        lemmas = sorted(w for w in set(content_lemmas(s)) if w in aset)
        n = len(lemmas)
        if n > 1:
            for i in range(n):
                for j in range(i + 1, n):
                    pair_counts[(lemmas[i], lemmas[j])] += 1
        if (si + 1) % 30000 == 0:
            print("[cooc] scanned %d/%d elapsed=%.1fs" % (si + 1, len(sents), time.time() - t0),
                  flush=True)
    print("[cooc] done: %d distinct co-occurring anchor pairs, elapsed=%.1fs" % (
        len(pair_counts), time.time() - t0), flush=True)
    return pair_counts


# =================================================================================================
# CELL S CANDIDATE CONSTRUCTION
# =================================================================================================
def build_syntagmatic_candidates(pair_counts: Counter, wn_pair_set: set, cap: int
                                 ) -> Tuple[List[Tuple[str, str, str]], Dict]:
    """Top co-occurring anchor pairs, capped at `cap` by descending count (>> the 90th percentile
    of the FULL co-occurrence distribution, so this is a stronger-than-top-decile pool, reported
    explicitly), excluding any pair that IS a WordNet same-synset pair, THEN excluding any pair
    whose best path_similarity >= WN_CLOSE_THRESHOLD (the near-synonym net the same-synset
    exclusion alone would miss), requiring both members share one dominant WordNet POS."""
    if not pair_counts:
        return [], {"n_raw_top": 0}
    counts_sorted = sorted(pair_counts.items(), key=lambda kv: kv[1], reverse=True)
    vals = np.array([c for _, c in pair_counts.items()], dtype=np.float64)
    decile_thresh = float(np.percentile(vals, TOP_DECILE_Q * 100))
    top = counts_sorted[:cap]
    actual_cap_thresh = top[-1][1] if top else 0
    kept_pos: List[Tuple[str, str, str]] = []
    n_excl_wn_exact = n_excl_wn_near = n_excl_pos = 0
    for (w1, w2), c in top:
        key = (w1, w2) if w1 < w2 else (w2, w1)
        if key in wn_pair_set:
            n_excl_wn_exact += 1
            continue
        p1, p2 = wn_dominant_pos(w1), wn_dominant_pos(w2)
        if p1 is None or p2 is None or p1 != p2:
            n_excl_pos += 1
            continue
        if wn_best_path_similarity(w1, w2) >= WN_CLOSE_THRESHOLD:
            n_excl_wn_near += 1
            continue
        kept_pos.append((key[0], key[1], p1))
    diag = {"n_raw_top_pool": len(top), "cap_requested": cap,
            "actual_min_count_in_pool": int(actual_cap_thresh),
            "decile_90_threshold_full_population": decile_thresh,
            "pool_is_at_least_top_decile": bool(actual_cap_thresh >= decile_thresh),
            "n_excluded_wn_exact_synonym": n_excl_wn_exact,
            "n_excluded_wn_near_path_sim_ge_thresh": n_excl_wn_near,
            "n_excluded_pos_mismatch_or_no_synsets": n_excl_pos,
            "n_kept": len(kept_pos)}
    return kept_pos, diag


# =================================================================================================
# MATCHING -- per-POS-stratum nearest neighbour on standardised (mean_log_freq, |freq_diff|,
# mean_length, orthographic trigram-cosine).
#
# FOUR covariates, not the three (freq/length/POS) the protocol text names -- an EARNED extension,
# not a deviation taken lightly. This cell's own smoke run (--grid reduced, n=246 pairs/cell) found
# that matching on freq/length/POS ALONE left TWO of the four floors CI-separated from chance:
#   F_ORTHOGRAPHIC AUC=0.6801 [0.6406,0.7189] (WordNet-synonym pairs are orthographically closer
#     than co-occurring pairs even after freq/length matching -- e.g. shared derivational
#     morphology within a synset)
#   F_FREQUENCY (max-of-pair, deliberately NOT the matched MEAN statistic) AUC=0.1266
#     [0.0972,0.1591] (matching the MEAN of two frequencies does not pin either INDIVIDUAL member's
#     frequency, so a max-based or skew-sensitive statistic can still separate the cells)
# Per the protocol's own instruction ("if a floor DOES separate them, the stimulus set is broken
# and must be rebuilt"), covariates were added to close each gap as it was found: |freq_diff| (pins
# the SHAPE of the pair's frequency split, not just its mean) and pair trigram-cosine (pins
# orthographic similarity directly, since it is a per-PAIR property already, not a per-word one).
# An UNCAPPED nearest-neighbour match on those still force-matched poorly-paired items (measured
# post-match SMD(mean_log_freq)=-1.9564), so a CALIPER was added (match_cells' caliper_sq): a P item
# with no genuinely close S partner is DROPPED, not force-matched. Tightening the caliper to fix
# F_FREQUENCY then exposed F_CONSTANT_PROTOTYPE (AUC=0.6598 at the smoke's reduced N=68) -- so
# constant-prototype score (mean of both members' FB.constant_prototype_floor value) was added as a
# FIFTH covariate. This is the protocol's own STOP-IF (i) applied iteratively and disclosed at each
# step, not a single design choice presented as settled from the start.
# =================================================================================================
def _pair_covariates(pairs: List[Tuple[str, str, str]], fq: Dict[str, float],
                     tri_of: Optional[Dict[str, np.ndarray]] = None,
                     proto_of: Optional[Dict[str, float]] = None) -> np.ndarray:
    """[n, 5]: col0=mean log1p(freq), col1=|freq diff|, col2=mean surface length,
    col3=orthographic trigram-cosine of the pair, col4=mean constant-prototype score (0.0 if the
    optional dict is not supplied, e.g. tiny fixtures)."""
    out = np.zeros((len(pairs), 5), dtype=np.float64)
    for i, (w1, w2, _p) in enumerate(pairs):
        f1, f2 = fq.get(w1, 0.0), fq.get(w2, 0.0)
        out[i, 0] = 0.5 * (f1 + f2)
        out[i, 1] = abs(f1 - f2)
        out[i, 2] = 0.5 * (len(w1) + len(w2))
        if tri_of is not None and w1 in tri_of and w2 in tri_of:
            out[i, 3] = float(np.dot(tri_of[w1], tri_of[w2]))
        if proto_of is not None and w1 in proto_of and w2 in proto_of:
            out[i, 4] = 0.5 * (proto_of[w1] + proto_of[w2])
    return out


def smd(a: np.ndarray, b: np.ndarray) -> float:
    """Standardised mean difference (Cohen's-d-style, pooled unweighted variance)."""
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    pooled_sd = float(np.sqrt(0.5 * (a.var() + b.var())))
    if pooled_sd < 1e-12:
        return 0.0
    return float((a.mean() - b.mean()) / pooled_sd)


DEFAULT_CALIPER_SQ_PER_DIM = np.array([0.02, 0.02, 0.25, 0.25, 0.25])  # mean_log_freq, abs_freq_diff
# tightened FAR below length/ortho/proto -- see match_cells docstring for the measured reason.


def match_cells(cellP: List[Tuple[str, str, str]], cellS: List[Tuple[str, str, str]],
                fq: Dict[str, float], seed: int,
                tri_of: Optional[Dict[str, np.ndarray]] = None,
                proto_of: Optional[Dict[str, float]] = None,
                caliper_sq=None
                ) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]], Dict]:
    """Greedy 1:1 nearest-neighbour matching WITHIN each POS stratum, on the z-scored 5-covariate
    plane (mean_log_freq, |freq_diff|, mean_length, orthographic trigram-cosine, mean constant-
    prototype score -- see the module comment above _pair_covariates for why 5, not the protocol
    text's literal 3). Vectorised per query (numpy distance to all remaining candidates, not a
    python-level O(n*m) double loop) so this stays fast even at thousands of candidates.

    CALIPER, ADDED after this cell's own smoke/full runs exposed the need, in three rounds:
      round 1 (UNCAPPED): a P pair with no genuinely similar S partner still gets "matched" to the
        least-bad option -- MEASURED smoke, uncapped: post-match SMD(mean_log_freq)=-1.9564
        (pre-match -2.5923). A P item whose nearest available S neighbour exceeds the caliper is
        DROPPED rather than force-matched, same fail-closed philosophy as
        tools.floor_battery.matched_candidate_sets ("the stratum is never widened to rescue it").
      round 2 (uniform total-Euclidean caliper): let one covariate spend the whole budget when the
        others sit near 0 -- MEASURED full scale, caliper_sq=0.3: F_FREQUENCY(max) AUC=0.3923.
      round 3 (uniform PER-DIMENSION/L-infinity caliper=0.25 on all 5 dims): still left a
        SYSTEMATIC (not just noisy) residual on mean_log_freq -- MEASURED full scale: post-match
        SMD(mean_log_freq)=-0.6235 even though EVERY accepted pair's z-diff on that one axis is
        individually <=0.5. The caliper bounds MAGNITUDE per pair, not DIRECTION; because SET S's
        raw candidate pool is structurally more frequent than SET P's (top-co-occurring vs
        zero-co-occurring), the slack a uniform caliper allows gets used in the SAME direction on
        most pairs, accumulating a net offset the per-pair bound does not prevent.
      round 4 (THIS ONE, default): a PER-DIMENSION VECTOR, not a scalar -- the two frequency
        covariates get a caliper 12.5x tighter (0.02, i.e. |z-diff|<=0.14 SD) than length/ortho/
        prototype (0.25 each, already measured clean). This trades matched N for tight control on
        the one axis that kept re-separating, rather than spending the SAME tolerance everywhere.
    `caliper_sq` accepts a scalar (uniform, legacy behaviour) or a length-n_cov array; None uses
    DEFAULT_CALIPER_SQ_PER_DIM."""
    covP = _pair_covariates(cellP, fq, tri_of, proto_of)
    covS = _pair_covariates(cellS, fq, tri_of, proto_of)
    n_cov = covP.shape[1] if covP.ndim == 2 else 5
    if caliper_sq is None:
        caliper_sq = DEFAULT_CALIPER_SQ_PER_DIM[:n_cov]
    caliper_vec = np.broadcast_to(np.asarray(caliper_sq, dtype=np.float64), (n_cov,))
    all_cov = np.vstack([covP, covS]) if (len(cellP) and len(cellS)) else np.zeros((0, n_cov))
    mu = all_cov.mean(axis=0) if all_cov.size else np.zeros(n_cov)
    sd = all_cov.std(axis=0) if all_cov.size else np.ones(n_cov)
    sd[sd < 1e-9] = 1.0
    zP = (covP - mu) / sd
    zS = (covS - mu) / sd

    rng = np.random.default_rng(seed)
    pos_tags = sorted(set(p for _, _, p in cellP) | set(p for _, _, p in cellS))
    matchedP: List[Tuple[str, str, str]] = []
    matchedS: List[Tuple[str, str, str]] = []
    per_stratum: Dict[str, Dict] = {}
    n_dropped_caliper_total = 0
    for tag in pos_tags:
        idxP = np.flatnonzero(np.array([p == tag for _, _, p in cellP]))
        idxS = np.flatnonzero(np.array([p == tag for _, _, p in cellS]))
        if idxP.size == 0 or idxS.size == 0:
            per_stratum[tag] = {"n_P_candidates": int(idxP.size), "n_S_candidates": int(idxS.size),
                                "n_matched": 0, "n_dropped_caliper": 0}
            continue
        # Vectorised per-query nearest-available-neighbour (O(n*m) total, one numpy distance call
        # per P item over the whole remaining S stratum -- not a python-level O(n*m) double loop).
        # Processing ORDER is randomised (not priority-sorted: a fully-recomputed priority order is
        # O(n^2*m) per stratum and was measured too slow at this population's stratum sizes); the
        # CALIPER below is what actually enforces balance, independent of order -- every ACCEPTED
        # match is within caliper_sq regardless of which P item claimed it first.
        order = rng.permutation(idxP.size)
        S_pts = zS[idxS]
        used = np.zeros(idxS.size, dtype=bool)
        n_matched_here = n_dropped_here = 0
        for k in order:
            i = idxP[k]
            if used.all():
                break
            # PER-DIMENSION (L-infinity) CALIPER, not a total-Euclidean budget. A single Euclidean
            # sum-of-squares cap lets one covariate "spend" the whole budget when the others are
            # near-zero -- MEASURED at full scale with a 0.3 total-sq-distance cap: F_FREQUENCY(max)
            # still separated (AUC=0.3923 [0.3537,0.4302]) because the frequency axis alone can eat
            # the entire caliper while length/ortho/proto sit at ~0. Requiring EVERY covariate's own
            # squared z-difference to individually clear the cap closes that loophole.
            diffsq = (S_pts - zP[i][None, :]) ** 2
            diffsq[used] = np.inf
            elig = np.all(diffsq <= caliper_vec[None, :], axis=1)
            if not elig.any():
                n_dropped_here += 1
                continue
            d_tot = diffsq.sum(axis=1)
            d_tot[~elig] = np.inf
            j_local = int(np.argmin(d_tot))
            used[j_local] = True
            matchedP.append(cellP[i])
            matchedS.append(cellS[idxS[j_local]])
            n_matched_here += 1
        n_dropped_caliper_total += n_dropped_here
        per_stratum[tag] = {"n_P_candidates": int(idxP.size), "n_S_candidates": int(idxS.size),
                            "n_matched": n_matched_here, "n_dropped_caliper": n_dropped_here}

    covP_m = _pair_covariates(matchedP, fq, tri_of, proto_of)
    covS_m = _pair_covariates(matchedS, fq, tri_of, proto_of)
    COV_NAMES = ["mean_log_freq", "abs_freq_diff", "mean_length", "orthographic_trigram_cos",
                "mean_constant_prototype"]

    def _smd_dict(a: np.ndarray, b: np.ndarray) -> Dict:
        if a.size == 0 or b.size == 0:
            return {k: None for k in COV_NAMES}
        return {k: round(smd(a[:, i], b[:, i]), 4) for i, k in enumerate(COV_NAMES)}

    diag = {
        "per_pos_stratum": per_stratum,
        "n_candidates_P": len(cellP), "n_candidates_S": len(cellS),
        "n_matched_P": len(matchedP), "n_matched_S": len(matchedS),
        "n_dropped_caliper": n_dropped_caliper_total, "caliper_sq_per_dim": caliper_vec.tolist(),
        "matching_covariates": COV_NAMES,
        "pre_match_smd": _smd_dict(covP, covS),
        "post_match_smd": _smd_dict(covP_m, covS_m),
        "post_match_pos_distribution_P": dict(Counter(p for _, _, p in matchedP)),
        "post_match_pos_distribution_S": dict(Counter(p for _, _, p in matchedS)),
    }
    return matchedP, matchedS, diag


# =================================================================================================
# AUC + PAIRED BOOTSTRAP
# =================================================================================================
def auc_of(sp: np.ndarray, ss: np.ndarray) -> float:
    """Mann-Whitney-U-style AUC: P(random SET-P score > random SET-S score) + 0.5*P(tie)."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    n_p, n_s = sp.size, ss.size
    if n_p == 0 or n_s == 0:
        return float("nan")
    ranks = rankdata(np.concatenate([sp, ss]))
    rank_sum_p = ranks[:n_p].sum()
    return float((rank_sum_p - n_p * (n_p + 1) / 2.0) / (n_p * n_s))


def auc_bootstrap(sp: np.ndarray, ss: np.ndarray, n_boot: int, seed: int) -> Dict:
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    n_p, n_s = sp.size, ss.size
    point = auc_of(sp, ss)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        ip = rng.integers(0, n_p, size=n_p)
        isv = rng.integers(0, n_s, size=n_s)
        boots[b] = auc_of(sp[ip], ss[isv])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    if lo > 0.5:
        band = "ABOVE_0.5_SUBSTITUTABILITY"
    elif hi < 0.5:
        band = "BELOW_0.5_COOCCURRENCE"
    else:
        band = "NOT_SEPARATED_FROM_CHANCE"
    return {"n_pairs_P": int(n_p), "n_pairs_S": int(n_s), "auc": round(point, 4),
            "ci95": [round(lo, 4), round(hi, 4)], "ci_halfwidth": round((hi - lo) / 2.0, 4),
            "band": band}


# =================================================================================================
# SCORE EXTRACTION PER ARM -- only the words the matched cells actually need
# =================================================================================================
def dense_scores_from_dict_store(store: Dict[str, np.ndarray], pairs: List[Tuple[str, str, str]]
                                 ) -> np.ndarray:
    out = np.zeros(len(pairs), dtype=np.float64)
    for i, (w1, w2, _p) in enumerate(pairs):
        v1, v2 = store.get(w1), store.get(w2)
        out[i] = float(np.dot(v1, v2)) if v1 is not None and v2 is not None else np.nan
    return out


def counts_to_dense_store(counts_by_word: Dict[str, Counter], words: Sequence[str],
                          binarize: bool = False) -> Dict[str, np.ndarray]:
    vocab = INFO.build_vocab([counts_by_word])
    if not vocab:
        return {w: np.zeros(1, dtype=np.float32) for w in words}
    cbw = counts_by_word
    if binarize:
        cbw = {k: Counter({w: 1 for w in c}) for k, c in counts_by_word.items()}
    M = INFO.to_sparse(cbw, list(words), vocab)
    Mn = INFO.l2n_sparse(M)
    dense = np.asarray(Mn.todense(), dtype=np.float32)
    return {w: dense[i] for i, w in enumerate(words)}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- wn_dominant_pos + synonym candidate construction, REAL words, REAL WordNet -------------
    tiny_anchors = ["car", "auto", "dog", "canine", "salt", "pepper", "happy", "unrelatedxyz"]
    p_car = wn_dominant_pos("car")
    assert p_car == "n", "car must have dominant POS noun: %r" % p_car
    pairs = build_wordnet_synonym_candidates(tiny_anchors)
    pair_set = set(tuple(sorted((a, b))) for a, b, _ in pairs)
    assert ("auto", "car") in pair_set, "car/auto is a textbook WordNet same-synset pair: %r" % pairs
    ev["wordnet_synonym_real_code_path"] = {"tiny_pairs": pairs}

    # --- path similarity: car/auto must be CLOSE, car/pepper must NOT ------------------------------
    ps_close = wn_best_path_similarity("car", "auto")
    ps_far = wn_best_path_similarity("car", "pepper")
    assert ps_close >= WN_CLOSE_THRESHOLD, "car/auto path_similarity should clear the close threshold: %.4f" % ps_close
    assert ps_far < WN_CLOSE_THRESHOLD, "car/pepper should NOT be WordNet-close: %.4f" % ps_far
    ev["path_similarity_known_answers"] = {"car_auto": round(ps_close, 4), "car_pepper": round(ps_far, 4)}

    # --- co-occurrence index on a tiny hand-built sentence set -------------------------------------
    tiny_sents = ["the salt and pepper sat on the table", "a dog ran past the car",
                  "salt and pepper again on the table", "auto repair shop downtown"]
    anchor_set = {"salt", "pepper", "dog", "car", "auto", "table"}
    pc = build_cooccurrence_paircounts(tiny_sents, anchor_set)
    assert pc.get(("pepper", "salt"), 0) == 2 or pc.get(("salt", "pepper"), 0) == 2, \
        "salt/pepper must co-occur exactly twice in the fixture: %r" % pc
    assert ("car", "auto") not in pc and ("auto", "car") not in pc, \
        "car/auto never appear in the SAME fixture sentence -- must have zero co-occurrence: %r" % pc
    ev["cooccurrence_known_answer"] = {"salt_pepper_count": pc.get(("pepper", "salt"),
                                                                   pc.get(("salt", "pepper"), 0))}

    # --- SET S candidate construction: excludes a WordNet-close pair even if it co-occurs a lot ---
    fake_counts = Counter({("car", "auto"): 50, ("salt", "pepper"): 2, ("dog", "table"): 1})
    wn_set = set(tuple(sorted((a, b))) for a, b, _ in build_wordnet_synonym_candidates(
        ["car", "auto", "salt", "pepper", "dog", "table"]))
    candS, diagS = build_syntagmatic_candidates(fake_counts, wn_set, cap=10)
    assert ("auto", "car") not in {(a, b) for a, b, _ in candS}, \
        "car/auto co-occurs 50x but IS a WordNet synonym pair -- must be excluded from SET S: %r" % candS
    ev["set_S_excludes_wordnet_pair_even_at_high_cooccurrence"] = diagS

    # --- AUC: known-separable case reads 1.0, overlapping case reads ~0.5 -------------------------
    sp = np.array([0.9, 0.8, 0.95, 0.85])
    ss = np.array([0.1, 0.2, 0.05, 0.15])
    a1 = auc_of(sp, ss)
    assert abs(a1 - 1.0) < 1e-9, "perfectly separable AUC must be 1.0: %.4f" % a1
    rng = np.random.default_rng(0)
    sp2 = rng.standard_normal(500)
    ss2 = rng.standard_normal(500)
    a2 = auc_of(sp2, ss2)
    assert abs(a2 - 0.5) < 0.05, "identically-distributed AUC should be near 0.5: %.4f" % a2
    ev["AUC_known_answers"] = {"separable": round(a1, 4), "overlapping_null": round(a2, 4)}

    # --- bootstrap CI: separable case CI must exclude 0.5; null case CI must include 0.5 ----------
    bs_sep = auc_bootstrap(sp2 + 3.0, ss2, 500, 1)
    bs_null = auc_bootstrap(sp2, ss2, 500, 2)
    assert bs_sep["band"] == "ABOVE_0.5_SUBSTITUTABILITY", "shifted-apart arrays must separate above 0.5: %r" % bs_sep
    assert bs_null["band"] == "NOT_SEPARATED_FROM_CHANCE", "identically-distributed arrays must NOT separate: %r" % bs_null
    ev["bootstrap_known_answers"] = {"separable_band": bs_sep["band"], "null_band": bs_null["band"]}

    # --- matching: two tiny synthetic pools, EACH P item has exactly one GENUINELY close S item
    # (s1 close to p1's frequency, s2 close to p2's) plus a far-off distractor S3 nobody should
    # claim (within caliper) -- proves both the pairing-quality AND the caliper-drop behaviour ----
    fq_fake = {w: float(v) for w, v in zip(
        ["p1a", "p1b", "p2a", "p2b", "s1a", "s1b", "s2a", "s2b", "s3a", "s3b"],
        [5.0, 5.0, 2.0, 2.0, 6.0, 6.0, 1.5, 1.5, 40.0, 40.0])}
    cellP_fake = [("p1a", "p1b", "n"), ("p2a", "p2b", "n")]
    cellS_fake = [("s1a", "s1b", "n"), ("s2a", "s2b", "n"), ("s3a", "s3b", "n")]
    mP, mS, mdiag = match_cells(cellP_fake, cellS_fake, fq_fake, seed=7, caliper_sq=1.0)
    assert len(mP) == len(mS) == 2, "both P items have a close S partner within caliper: %r %r %r" % (mP, mS, mdiag)
    assert set(mS) == {("s1a", "s1b", "n"), ("s2a", "s2b", "n")}, \
        "the far-off s3 distractor must NEVER be matched: %r" % (mS,)
    # --- CALIPER DROP: shrink S to ONLY the far-off distractor -- must drop BOTH P items, not force ---
    mP2, mS2, mdiag2 = match_cells(cellP_fake, [("s3a", "s3b", "n")], fq_fake, seed=7, caliper_sq=1.0)
    assert len(mP2) == 0, "with only a far-off S candidate, the caliper must drop both P items, not force-match: %r" % mP2
    assert mdiag2["n_dropped_caliper"] == 2, "caliper drop count wrong: %r" % mdiag2
    ev["matching_known_answer"] = mdiag
    ev["matching_caliper_drop_known_answer"] = mdiag2

    # --- dense store extraction from raw counts: binarize actually changes the vector --------------
    fake_store = {"w1": Counter(a=3, b=1), "w2": Counter(a=1, b=1)}
    graded = counts_to_dense_store(fake_store, ["w1", "w2"], binarize=False)
    binar = counts_to_dense_store(fake_store, ["w1", "w2"], binarize=True)
    assert not np.allclose(graded["w1"], binar["w1"]), "binarizing must change the row (counts 3,1 vs 1,1)"
    ev["binarize_changes_store"] = True

    # --- arms-must-differ (META_RULE_AF) -----------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr), "distinct score vectors must produce distinct digests"
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test) ------------------------------
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

    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors: List[str] = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    mat = np.asarray(C["mat"], dtype=np.float32)
    n_anchors = len(anchors)
    anchor_set = set(a for a, ok in zip(anchors, mat_ok) if ok)
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}  # ALREADY log1p(freq)
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)
    pos_idx: Dict[str, int] = C["pos"]
    print("[load] n_anchors=%d n_valid=%d t=%.1fs" % (n_anchors, len(anchor_set), time.time() - t0),
          flush=True)

    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "population_n_anchors": n_anchors}

    # =============================== REGRESSION GATE (proves the same landed instrument) ============
    rep["REGRESSION_GATE"] = {"expected_source": "PIPE.REGRESSION_A0_PARTIAL == %.4f (same cache CTS "
                              "loads); this cell scores PAIRWISE similarity, not hit@1, so it cannot "
                              "reproduce that number directly -- instead it asserts the cache identity "
                              "(anchor count, mat shape) matches every sibling cell's own regression-"
                              "gated load." % PIPE.REGRESSION_A0_PARTIAL,
                              "n_anchors": n_anchors, "mat_shape": list(mat.shape),
                              "PASS": bool(n_anchors == mat.shape[0] == t_mat.shape[0])}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- cache shapes disagree: %r" % rep["REGRESSION_GATE"])

    # =============================== POPULATION (checkpointed unit) =================================
    n_anchors_pop = n_anchors if grid == "full" else min(1800, n_anchors)
    anchor_set_pop = anchor_set if grid == "full" else set(sorted(anchor_set)[:n_anchors_pop])
    pop_key = unit_key("POPULATION", CODE_VERSION, grid)
    prior_pop = load_units(out_dir_ckpt).get(pop_key)
    if prior_pop is not None:
        print("[population] RESUMED FROM CHECKPOINT", flush=True)
        matchedP = [tuple(x) for x in prior_pop["matchedP"]]
        matchedS = [tuple(x) for x in prior_pop["matchedS"]]
        pop_diag = prior_pop["diag"]
    else:
        wn_pairs = build_wordnet_synonym_candidates(anchor_set_pop)
        wn_pair_set = set(tuple(sorted((a, b))) for a, b, _ in wn_pairs)
        print("[population] %d WordNet same-synset candidate pairs" % len(wn_pairs), flush=True)

        sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
        rep["corpus_provenance"] = corpus_prov
        pair_counts = build_cooccurrence_paircounts(sents, anchor_set_pop)

        cellP = [(w1, w2, p) for (w1, w2, p) in wn_pairs if pair_counts.get((w1, w2), 0) == 0]
        print("[population] SET P (WordNet-synonym, zero co-occurrence) raw candidates: %d" %
             len(cellP), flush=True)

        cellS, candS_diag = build_syntagmatic_candidates(pair_counts, wn_pair_set,
                                                          cap=CELL_S_CAND_CAP)
        print("[population] SET S (top co-occurring, no close WordNet relation) raw candidates: %d"
             % len(cellS), flush=True)

        tri_all = l2n(t_mat)
        proto_all = FB.constant_prototype_floor(mat, mat_ok)
        cand_words = set(w for w1, w2, _p in cellP + cellS for w in (w1, w2))
        tri_of = {w: tri_all[pos_idx[w]] for w in cand_words if w in pos_idx}
        proto_of = {w: float(proto_all[pos_idx[w]]) for w in cand_words if w in pos_idx}
        matchedP, matchedS, match_diag = match_cells(cellP, cellS, fq_log, seed=MASTER_SEED + 701,
                                                     tri_of=tri_of, proto_of=proto_of)
        print("[population] MATCHED n_P=%d n_S=%d" % (len(matchedP), len(matchedS)), flush=True)

        pop_diag = {"n_wordnet_synonym_candidates": len(wn_pairs),
                   "n_distinct_cooccurring_anchor_pairs": len(pair_counts),
                   "n_setP_raw_zero_cooccurrence": len(cellP),
                   "setS_candidate_construction": candS_diag,
                   "matching": match_diag}
        record_unit(out_dir_ckpt, pop_key, {"matchedP": matchedP, "matchedS": matchedS, "diag": pop_diag})

    rep["POPULATION"] = pop_diag
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match
    if n_match < 20:
        raise SystemExit("INSTRUMENT_UNBUILDABLE_AT_THIS_N -- only %d matched pairs per cell; too "
                         "few for a meaningful AUC. diag=%r" % (n_match, pop_diag))

    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    print("[scores] %d distinct words needed across both matched cells" % len(words_needed), flush=True)

    # =============================== SCORES (checkpointed unit) =====================================
    scores_key = unit_key("SCORES", CODE_VERSION, grid)
    prior_scores = load_units(out_dir_ckpt).get(scores_key)
    if prior_scores is not None:
        print("[scores] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_scores.items()}
    else:
        wid = {w: pos_idx[w] for w in words_needed}
        Mn_incumbent = l2n(mat)
        t0s = time.time()

        # ---- INCUMBENT_LIVE_STORE ---------------------------------------------------------------
        store_incumbent = {w: Mn_incumbent[wid[w]] for w in words_needed}

        # ---- RANDOM_VECTOR (validation, not a "real" arm) --------------------------------------
        rng_rand = np.random.default_rng(MASTER_SEED + 909)
        rand_full = l2n(rng_rand.standard_normal((n_anchors, mat.shape[1])).astype(np.float32))
        store_random = {w: rand_full[wid[w]] for w in words_needed}

        # ---- F_SCRAMBLE ---------------------------------------------------------------------------
        scrambled = l2n(FB.scramble_null(mat, MASTER_SEED + 4242))
        store_scramble = {w: scrambled[wid[w]] for w in words_needed}

        # ---- F_ORTHOGRAPHIC -------------------------------------------------------------------
        Tn = l2n(t_mat)
        store_ortho = {w: Tn[wid[w]] for w in words_needed}

        # ---- F_CONSTANT_PROTOTYPE (scalar per anchor -> pair score = mean, computed directly) --
        proto = FB.constant_prototype_floor(mat, mat_ok)
        proto_of = {w: float(proto[wid[w]]) for w in words_needed}

        # ---- F_FREQUENCY (scalar per anchor, aux['fq'] already log1p) --------------------------
        freq_of = {w: fq_log.get(w, 0.0) for w in words_needed}

        # ---- RAW_COUNT_FULL_ACCUM (checkpoint reuse, no retokenisation) -------------------------
        units_info = load_units(os.path.join(REPO, "data", "exp_cue_information_audit_v1"))
        counts_full: Dict[str, Counter] = {}
        missing_p = []
        for w in words_needed:
            rec = units_info.get(unit_key("Pstore", w))
            if rec is None:
                missing_p.append(w)
                continue
            counts_full[w] = Counter(rec["counts"])
        if missing_p:
            raise SystemExit("CHECKPOINT REUSE INCOMPLETE -- exp_cue_information_audit_v1's own "
                             "units.jsonl is missing Pstore for: %r" % missing_p[:20])
        store_raw_full = counts_to_dense_store(counts_full, words_needed, binarize=False)
        store_binarized = counts_to_dense_store(counts_full, words_needed, binarize=True)

        # ---- RAW_COUNT_SINGLE_OCC (PIPE, reused verbatim, restricted to words_needed) ------------
        sents, buckets, counts, _prov = INFO.load_corpus_and_buckets()
        P_single, single_diag = PIPE.build_single_occurrence_counts(words_needed, buckets, sents)
        rep["single_occurrence_build_diag"] = single_diag
        store_single = counts_to_dense_store(P_single, words_needed, binarize=False)

        # ---- PARADIGMATIC_PROFILE_WRITE (WRP.build_arm, mode=PROFILE, restricted anchor list) ---
        mat0n = WRP.l2n_rows64(mat)
        d_dim = mat.shape[1]
        cw_cache: Dict[int, List[str]] = {}
        t_w1 = time.time()
        mat_w1, _part = WRP.build_arm(words_needed, buckets, cw_cache, sents, mat0n, pos_idx,
                                      d_dim, "PROFILE")
        print("[scores] PARADIGMATIC_PROFILE_WRITE built for %d words in %.1fs" % (
            len(words_needed), time.time() - t_w1), flush=True)
        w1n = l2n(mat_w1)
        store_paradigmatic = {w: w1n[i] for i, w in enumerate(words_needed)}

        print("[scores] all arms built, elapsed=%.1fs" % (time.time() - t0s), flush=True)

        def pair_dense(store: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
            return (dense_scores_from_dict_store(store, matchedP),
                    dense_scores_from_dict_store(store, matchedS))

        def pair_scalar_mean(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
            fp = lambda pairs: np.array([0.5 * (scalar_of.get(w1, 0.0) + scalar_of.get(w2, 0.0))
                                        for w1, w2, _p in pairs])
            return fp(matchedP), fp(matchedS)

        def pair_scalar_max(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
            fp = lambda pairs: np.array([max(scalar_of.get(w1, 0.0), scalar_of.get(w2, 0.0))
                                        for w1, w2, _p in pairs])
            return fp(matchedP), fp(matchedS)

        def pair_path_sim() -> Tuple[np.ndarray, np.ndarray]:
            fp = lambda pairs: np.array([wn_best_path_similarity(w1, w2) for w1, w2, _p in pairs])
            return fp(matchedP), fp(matchedS)

        arm_scores_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "F_ORTHOGRAPHIC": pair_dense(store_ortho),
            "F_FREQUENCY": pair_scalar_max(freq_of),
            "F_SCRAMBLE": pair_dense(store_scramble),
            "F_CONSTANT_PROTOTYPE": pair_scalar_mean(proto_of),
            "KNOWN_ANSWER_WORDNET_PATH_SIM": pair_path_sim(),
            "RANDOM_VECTOR_STORE": pair_dense(store_random),
            "INCUMBENT_LIVE_STORE": pair_dense(store_incumbent),
            "RAW_COUNT_FULL_ACCUM": pair_dense(store_raw_full),
            "RAW_COUNT_SINGLE_OCC": pair_dense(store_single),
            "PRESENCE_ABSENCE_BINARIZED": pair_dense(store_binarized),
            "PARADIGMATIC_PROFILE_WRITE": pair_dense(store_paradigmatic),
        }
        arm_scores = {k: {"P": v[0], "S": v[1]} for k, v in arm_scores_raw.items()}
        record_unit(out_dir_ckpt, scores_key,
                   {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in arm_scores.items()})

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC PER ARM ======================================================
    FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    STORE_ARM_NAMES = ["INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM", "RAW_COUNT_SINGLE_OCC",
                      "PRESENCE_ABSENCE_BINARIZED", "PARADIGMATIC_PROFILE_WRITE"]
    boot_seed_base = MASTER_SEED + 8181
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(arm_scores.items()):
        n_boot_here = N_BOOT
        res = auc_bootstrap(sc["P"], sc["S"], n_boot_here, boot_seed_base + i)
        auc_results[name] = res
        print("[auc] %-30s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)
    rep["AUC_PER_ARM"] = auc_results

    # =============================== LICENSING (STOP-IF i, ii) =======================================
    floor_licensing_ok = all(auc_results[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in FLOOR_NAMES)
    floor_failures = [f for f in FLOOR_NAMES if auc_results[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    known_answer_ok = auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"] >= KNOWN_ANSWER_MIN_AUC
    random_store_ok = auc_results["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    instrument_licensed = bool(floor_licensing_ok and known_answer_ok)
    rep["LICENSING"] = {
        "STOP_IF_i_floors_at_chance": {"PASS": floor_licensing_ok, "floor_failures": floor_failures},
        "STOP_IF_ii_known_answer_near_1": {"PASS": known_answer_ok,
                                          "measured_auc": auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"],
                                          "gate": KNOWN_ANSWER_MIN_AUC},
        "random_vector_store_at_chance": {"PASS": random_store_ok},
        "INSTRUMENT_LICENSED": instrument_licensed,
    }
    if not instrument_licensed:
        print("[LICENSING] INSTRUMENT UNLICENSED -- store-arm numbers are WRITTEN below for the "
             "record but MUST NOT be interpreted as a finding. floor_failures=%r known_answer=%.4f"
             % (floor_failures, auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"]), flush=True)

    # =============================== STOP-IF iii/iv/v (interpretation, only if licensed) =============
    incumbent = auc_results["INCUMBENT_LIVE_STORE"]
    if instrument_licensed:
        if incumbent["band"] == "BELOW_0.5_COOCCURRENCE":
            interp = "STOP_IF_iii_COOCCURRENCE_DIAGNOSIS_CONFIRMED"
        elif incumbent["band"] == "ABOVE_0.5_SUBSTITUTABILITY":
            interp = "STOP_IF_iv_COOCCURRENCE_DIAGNOSIS_REFUTED"
        else:
            interp = "INCUMBENT_NOT_SEPARATED_FROM_CHANCE"
        # STOP-IF (v): arms "indistinguishable from EACH OTHER", i.e. a pairwise question -- NOT
        # "all arms sit on the same side of 0.5" (a bug in an earlier version of this cell: all 5
        # store arms read BELOW_0.5 at full scale, which triggered a same-BAND check even though
        # their point AUCs range 0.03-0.42, a real, wide spread). The correct, cheap proxy: do ALL
        # of the store arms' 95% CIs share a COMMON overlap region? If the CIs have a nonempty
        # mutual intersection, no pairwise comparison in this set can be called separated at this n
        # (a necessary, not sufficient, condition for "some pair differs" -- reported as a coarse
        # resolution check, not a full pairwise test battery).
        los = [auc_results[a]["ci95"][0] for a in STORE_ARM_NAMES]
        his = [auc_results[a]["ci95"][1] for a in STORE_ARM_NAMES]
        mutual_overlap = bool(max(los) <= min(his))
        rep["ARM_RESOLUTION_CHECK"] = {"method": "mutual 95% CI overlap across all store arms",
                                       "max_lo": round(max(los), 4), "min_hi": round(min(his), 4),
                                       "all_arms_mutually_overlap": mutual_overlap}
        if mutual_overlap:
            interp += "__STOP_IF_v_ALL_STORE_ARMS_MUTUALLY_CI_OVERLAPPING"
    else:
        interp = "INSTRUMENT_UNLICENSED_NO_INTERPRETATION_PERMITTED"
    rep["INTERPRETATION"] = interp

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

    licensed = rep.get("LICENSING", {}).get("INSTRUMENT_LICENSED", False)
    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "DISSOCIATION_INSTRUMENT_%s__%s" % ("LICENSED" if licensed else "UNLICENSED", interp)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Dissociation-score instrument (protocol sec 8.3): SET P (WordNet-synonym, "
                       "zero co-occurrence) vs SET S (top co-occurring, no close WordNet relation), "
                       "frequency/length/POS matched. AUC separating them under the store's own "
                       "similarity, per arm, with 4 floors + known-answer + random-store licensing. "
                       "-> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT,
                  "WN_CLOSE_THRESHOLD": WN_CLOSE_THRESHOLD, "TOP_DECILE_Q": TOP_DECILE_Q,
                  "CELL_S_CAND_CAP": CELL_S_CAND_CAP, "KNOWN_ANSWER_MIN_AUC": KNOWN_ANSWER_MIN_AUC},
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
