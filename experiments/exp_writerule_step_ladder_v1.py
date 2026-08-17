"""exp_writerule_step_ladder_v1 -- ORGAN A: WHICH STEP OF THE WRITE RULE DESTROYS SUBSTITUTABILITY?

THE QUESTION (notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md, ORGAN A). The store records CO-OCCURRENCE
("appears near"); the task scores SUBSTITUTABILITY ("could replace"). Landed evidence
(notes/readout_ceiling_findings_2026-08-17.md ARM5): 79.3% of winners have no close WordNet relation
to the query and co-occur 4.24x more than the correct answer; the median gold co-occurrence is
EXACTLY ZERO. "The write rule" has so far been treated as ONE opaque box. This cell enumerates its
steps from LIVE CODE and asks, per step, which one converts substitutability into adjacency.

=================================================================================================
STEP ENUMERATION -- METHOD: runtime evidence, not grep (per CLAUDE.md "prefer runtime evidence").
Read hdlab/grounding_acquisition_loop.py (content_words, context_vector -- module docstring names
these "GENUINELY-NEW code here"), hdlab/reading_grounding_loop.py (ConceptSpace.observe /
anchor_matrix / bundle, symbol_vector, GRADED_COMPARATOR), and REUSED the runtime-verified step
enumeration already landed in experiments/exp_pipeline_stage_oracle_ladder_v1.py (commit e28d1b8d6,
itself built by reading the same three files plus the machine-asserted H^T p == mat[a] identity in
experiments/exp_cue_information_audit_v1.py). That enumeration is not re-derived from scratch here;
it is READ, VERIFIED against the live source below, and then EXTENDED, because it collapsed the
write side to two physical events (S1 code, S2 accumulate) and never asked the composition question.

VERIFIED DIRECTLY IN THIS CELL'S OWN BUILD (not merely cited):
  hdlab/grounding_acquisition_loop.py:113-117  content_words(text) = regex [a-z']+ tokens, lowered,
    minus a ~70-word stopword set, minus len<=2 tokens. Called INSIDE context_vector.
  hdlab/reading_grounding_loop.py:297-309  symbol_vector(w) = hashlib.sha256(w)-seeded bipolar draw
    at d=256, ONE FIXED random basis H shared by the entire vocabulary. A word's occurrence-level
    code IS its row of H; summing a sentence's content words' rows projects the raw count vector
    directly at d=256 -- there is no separate uncompressed intermediate in the live path (the
    "uncompressed" P_a this cell also builds is a POST-HOC reconstruction, H^T p == mat[a] bit-exact,
    used as a counterfactual, not a real earlier artifact).
  hdlab/reading_grounding_loop.py:478-481  ConceptSpace.observe: `self._sums[lemma] += ctx_vec`,
    unweighted summation across every PROFILE occurrence of that anchor. No decay, no cap.
  hdlab/reading_grounding_loop.py:103-107,502-511  GRADED_COMPARATOR (env HD_GRADED_COMPARATOR,
    default "1" i.e. ON): `anchor_matrix()` returns `np.sign(mat)` ONLY when this flag is OFF; with
    the LIVE DEFAULT it returns the raw graded sums untouched. **CORRECTION TO THE DIRECTOR'S SKETCH,
    STATED PLAINLY: item (d) "what normalisation happens and when" -- under the CURRENT DEFAULT PATH
    (the one every headline number in this arc, including the 79.3%/4.24x ARM5 finding, was measured
    on) NOTHING normalises the store. Sign-quantisation is a REAL, LIVE, TOGGLEABLE code path (it was
    the default until 2026-08-14) but is OFF today. It is laddered here anyway because it is
    enumerable from live code and reachable by one env var -- exactly the brief's bar for a step.**

SO THE WRITE RULE HAS FOUR STEPS ON THIS CELL'S OWN READING, WHERE THE DIRECTOR'S FIVE-ITEM SKETCH
(a-e: filter, code, accumulate, normalise, superpose) HAD FIVE. THIS IS ITSELF A RESULT, reported
per the brief's instruction to expect and report a correction:
  FILTER      content_words: keep alphabetic tokens > 2 chars, drop ~70 stopwords. Sketch item (a).
  CODE        symbol_vector per surviving word, summed -> one d=256 vector. Sketch items (b) AND the
              "superposition with every other word" item (e) are THE SAME EVENT: cross-talk between
              different words' codes happens INSIDE this one shared-basis projection (already
              established, exp_pipeline_stage_oracle_ladder_v1 STAGE_ENUMERATION, mean|cos| among
              5000 sampled symbol-vector pairs = 0.0499, close to the 1/sqrt(256) JL bound) -- there
              is no separate later "superposed into a store shared with every other word" step to
              ladder; it is baked into CODE and is not independently manipulable.
  ACCUMULATE  ConceptSpace.observe, summed across profile occurrences. Sketch item (c).
  NORMALISE   sign() quantisation, CONDITIONAL, OFF by default (GRADED_COMPARATOR=True). Sketch
              item (d), corrected as above.
Director's sketch item (e) does not survive as an independent step (folded into CODE, above) --
the same shape of correction exp_pipeline_stage_oracle_ladder_v1 already made to the READ side.

=================================================================================================
THE LADDER, ORACLE-DOWNSTREAM PER STEP (method sec 1.3): at every rung the CUE is the item's own
oracle self-address (query = that representation's own stored row for its anchor -- addressing must
read ~1.0 by construction; this is the SAME "EXACT KEY" oracle regime the whole 2026-08-17 arc uses,
so numbers here are the write-side residue after the READ side is held perfect, exactly matching
exp_pipeline_stage_oracle_ladder_v1 PART B's own framing). Four rungs, chained by DIRECT REUSE of
prior organs wherever one already exists, plus TWO new rungs for the two steps nobody has isolated
(FILTER, NORMALISE):

  R1 UNFILTERED_SINGLE_OCC     (NEW) one profile sentence per anchor, EVERY token kept (no stopword/
                                length filter), raw counts, unprojected. Isolates FILTER's INPUT.
  R2 FILTERED_SINGLE_OCC       (REUSED VERBATIM: exp_pipeline_stage_oracle_ladder_v1
                                .build_single_occurrence_counts == its own DIAG_B1 construction)
                                same one sentence per anchor, content-word filtered, unprojected.
                                R1 -> R2 isolates FILTER, at matched (single-occurrence) depth --
                                a full-accumulation FILTER rung would need an unfiltered full-corpus
                                pass with no existing cache (INFO's own >1800s-class cost) and is
                                deliberately NOT built; disclosed as a scope limit, not a leak.
  R3 FILTERED_FULL_ACCUM       (REUSED VERBATIM: exp_cue_information_audit_v1's own landed checkpoint
                                via exp_pipeline_stage_oracle_ladder_v1.load_full_accum_from_checkpoint
                                == its own DIAG_B2). R2 -> R3 isolates ACCUMULATE (same construction,
                                more profile sentences).
  R4 PROJECTED_GRADED_FULL_ACCUM  the REAL incumbent store (mat, GRADED_COMPARATOR default) at the
                                exact-key cue -- numerically the same construction as
                                exp_pipeline_stage_oracle_ladder_v1's LAM_1.00 / this arc's headline
                                0.0481. R3 -> R4 isolates CODE/PROJECT.
  R5 PROJECTED_SIGN_FULL_ACCUM (NEW) the SAME store, sign()-quantised (both store and query, matching
                                what GRADED_COMPARATOR=False would have produced). R4 -> R5 isolates
                                NORMALISE.

MONOTONICITY. R2->R3 (ACCUMULATE) is EXCLUDED from the strict "signal cannot rise" assertion for the
IDENTICAL reason exp_pipeline_stage_oracle_ladder_v1 excluded its own B1->B2: more accumulated
evidence is not a downstream information-loss step, it is strictly more real material, and that
cell's own measurement already found it DROPS the score (-0.0263) despite being "more data" -- a
genuine finding, not a leak, and this cell's own recomputation (paired to its own composition
measurement) either reproduces or updates that number, never silently imports it. R1->R2 (FILTER),
R3->R4 (CODE/PROJECT) and R4->R5 (NORMALISE) ARE each a deterministic transform of a FIXED underlying
signal (word-count evidence) with something specific removed (noise tokens / dimensionality /
magnitude), so `check_monotone_nonincreasing` (REUSED, exp_pipeline_stage_oracle_ladder_v1) is run
over [R1,R2,R4,R5] (R3 held alongside as the ACCUMULATE-linked rung, reported but not chained into
this specific assertion, matching the same precedent) and ANY rise beyond MONOTONE_TOL_SIGMA is
reported as a LEAK, per the brief, before any other reading is offered.

THE COMPOSITION MEASUREMENT (the brief's stated scientific core, never computed at intermediate rungs
before). At every rung: the WordNet-relation rate of the top-1 winner (REUSED classification and
0.25 path-similarity threshold from exp_readout_second_order_v1's C1, generalised to take an
arbitrary per-item winner array so it can run at 5 rungs, not just the incumbent) and the sentence-
level Jaccard co-occurrence of query vs winner vs best-gold (REUSED construction from the same
cell's C2), on a SHARED, seeded, paired index subset so a composition DELTA between rungs is a valid
paired comparison, not two separately-drawn samples.

=================================================================================================
ORGAN REUSE, enumerated then reconciled -- no pipeline stage is reimplemented:
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)   build_population, load_full_accum_from_
                                                            checkpoint, build_single_occurrence_counts,
                                                            dprime_stats/summary, rank_summary,
                                                            check_monotone_nonincreasing, l2n, its own
                                                            self_test() (called wholesale)
  experiments.exp_cue_information_audit_v1 (INFO)          load_corpus_and_buckets, raw_counts_for_
                                                            window, build_vocab, to_sparse, l2n_sparse,
                                                            _ShimSpace, C3 (= exp_grounding_readout_
                                                            known_answer_v1), its own self_test()
  tools.floor_battery (FB)                                 hit_at_1_both_tie_conventions, the four
                                                            floors, paired_bootstrap_ci, margin,
                                                            oracle_constant_scores, as_constant_matrix
  hdlab.reading_grounding_loop                             content_lemmas, normalize_lemma (for the
                                                            new unfiltered tokenizer's self-exclusion)
  exp_readout_second_order_v1's C1/C2 CONSTRUCTION is reused (identical classification bins,
  identical 0.25 threshold, identical Jaccard measure) but not IMPORTED as a function (that cell
  embeds C1/C2 inline in its own `run()`, not as top-level callables) -- reimplemented here as small,
  independently self-tested utilities with the SAME construction, which is the measurement
  instrument itself (analogous to floor_battery being a reused instrument, not a reused pipeline
  stage) and is required here regardless because no existing cell computes it at more than one rung.

PRIOR-WORK CHECK (enumerate, don't just search, per CLAUDE.md). Read notes/PLAN_ORGAN_STEP_LADDERS_
2026-08-17.md sec "ORGAN A", notes/readout_ceiling_findings_2026-08-17.md (ARM1-5, the 79.3%/4.24x
source), notes/readout_writerule_selection_axis_2026-08-17.md (payload+selection axes, both tested
and both null), and data/exp_pipeline_stage_oracle_ladder_v1/metrics.json (the FILTER+ACCUMULATE+
PROJECT numbers this cell reuses/extends). None of those compute composition (WordNet-relation rate,
co-occurrence ratio) at more than the single incumbent rung; none isolates FILTER or NORMALISE at
all. This cell is not a rediscovery of any of them; it composes and extends all four.

Prior-work check (substrate-KB): `bash tools/substrate_query.sh` is documented STALE this session
(hd_director_kb_continuous_ingest livelock, notes/STATUS.md); per the standing rule the enumeration
above (reading every organ-A-relevant note + the two directly-reused cells) is the substitute, per
the same exemption the sibling 2026-08-17 cells recorded for themselves.

BRAIN FRAMING. PINNED: complementary learning systems -- neocortex extracts CROSS-EPISODE
REGULARITIES, hippocampus keeps the episode (McClelland/O'Reilly); cortical semantic representation
is organised by similarity of experience, not temporal adjacency. Adjacency-in-a-sentence is an
EPISODIC fact; substitutability is the REGULARITY -- this cell asks WHICH WRITE-RULE STEP is where
that confusion is introduced. OUR INVENTION UNDER TEST: every operator laddered here (content_words'
particular stopword list, the sha256-seeded random basis, unweighted summation, sign quantisation).
No anatomical structure is claimed for any of them; nothing here claims a brain structure computes
second-order co-occurrence, per the standing fidelity-gate ban on inventing anatomy to fill a box.

FLOORS. All four (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE) recomputed on THIS
cell's own population via tools.floor_battery, both tie conventions, CI half-width and analytic null
half-width beside every margin. 0.1390/0.0873/0.1382/0.2070/-0.1959 are NEVER imported.

CONTROLS. K1 KNOWN-ANSWER: addressing must read ~1.0 at every one of the 5 main rungs (each is an
oracle self-address by construction) or nothing is published. N1 NULL: the exact-key query
assignment deranged (never-self permutation) on the incumbent (R4) rung must sit at this pool's own
chance addressing.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every rung's hit-vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: ONE unit "MAIN" via tools.exp_checkpoint, resume-safe (same pattern as the
#   directly-reused sibling exp_pipeline_stage_oracle_ladder_v1)
# - discriminator survives scale: this cell RUNS the FULL grid, no scale-preview needed
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated cache
#   unmodified; the two NEW rungs use the SAME cache/corpus, no new calibration introduced)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - baseline_in_band: n/a -- every rung is oracle-self-address by construction (~1.0), the gate here
#   is K1/N1 (addressing), not a 0.05-0.95 baseline band
# - crlb_floor_computed: n/a -- this is a composition/margin measurement over an existing store, not
#   a capacity-sweep; declared explicitly rather than silently omitted

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. The store is
NEVER rebuilt. data/foundation/** is never opened. Writes only under
data/exp_writerule_step_ladder_v1[_reduced]/ and this cell's own scratch/ subdirectory (none needed).
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

import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE          # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas, normalize_lemma  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "writerule_step_ladder_v1"
CODE_VERSION = "v1.1"  # v1.0's first full run had a monotonicity-chain construction bug (skipped R3,
                       # falsely flagged a LEAK); v1.1 fixes it with per-leg checks. See
                       # MONOTONICITY_NOTE_BUG_DISCLOSURE in the metrics. Version bumped so the
                       # checkpoint key does not silently resume the buggy v1.0 MAIN unit.
FINDINGS = "notes/writerule_step_ladder_v1_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = PIPE.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
ADDRESS_EXACT_MIN = 0.95
MONOTONE_TOL_SIGMA = PIPE.MONOTONE_TOL_SIGMA
N_PROBE_COMPOSITION = 60 if SMOKE else 700   # shared, PAIRED across every rung -- see build_population
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")

_TOKEN_RE = re.compile(r"[a-z']+")


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# THE TWO NEW STEPS -- FILTER counterfactual (unfiltered tokenizer) and NORMALISE (sign quantise)
# =================================================================================================
def raw_counts_unfiltered_for_window(sentence: str, target_lemma: str) -> Counter:
    """UNFILTERED counterpart of INFO.raw_counts_for_window: the IDENTICAL regex tokenisation
    ([a-z']+, lowered) and the IDENTICAL target-lemma self-exclusion (normalize_lemma(w) !=
    target_lemma, matching context_vector_masked's own masking), but WITHOUT content_words' ~70-word
    stopword filter and len>2 length filter. Isolates the FILTER step: every other construction
    choice (regex, self-masking, count-not-set semantics) is held fixed."""
    toks = _TOKEN_RE.findall(sentence.lower())
    return Counter(w for w in toks if normalize_lemma(w) != target_lemma)


def build_single_occurrence_counts_unfiltered(anchor_ids: Sequence[str],
                                              buckets: Dict[str, List[int]],
                                              sents: List[str]) -> Tuple[Dict[str, Counter], Dict]:
    """Mirrors PIPE.build_single_occurrence_counts EXACTLY (same anchor loop, same
    buckets[a][0] sentence choice per anchor) except for the tokenizer -- so R1 and R2 (=DIAG_B1)
    are built from the LITERAL SAME sentence per anchor, differing only in FILTER."""
    t0 = time.time()
    P1: Dict[str, Counter] = {}
    n_empty = 0
    for k, a in enumerate(anchor_ids):
        occ = buckets.get(a, [])
        if not occ:
            P1[a] = Counter()
            n_empty += 1
            continue
        P1[a] = raw_counts_unfiltered_for_window(sents[occ[0]], a)
        if (k + 1) % 2000 == 0 or k == len(anchor_ids) - 1:
            print("[single_occ_unfiltered] %d/%d elapsed=%.0fs" % (
                k + 1, len(anchor_ids), time.time() - t0), flush=True)
    return P1, {"n_anchors": len(anchor_ids), "n_empty_profile": n_empty,
               "elapsed_s": round(time.time() - t0, 1)}


# =================================================================================================
# THE COMPOSITION INSTRUMENT -- reused construction from exp_readout_second_order_v1's C1/C2,
# generalised to run at an arbitrary rung's winner array on a SHARED paired index subset.
# =================================================================================================
def wordnet_relation_composition(query_words: Sequence[str], winner_words: Sequence[str],
                                 in_gold: np.ndarray, idx_probe: np.ndarray) -> Dict:
    """C1-style winner forensics (exp_readout_second_order_v1), reused construction: WordNet
    synsets, path_similarity capped at the first 4 synsets/POS-matched pairs, threshold 0.25 for
    'taxonomically close'. Returns per-item booleans so a caller can paired-bootstrap the DELTA
    between two rungs on the IDENTICAL idx_probe."""
    from nltk.corpus import wordnet as wn
    rel = Counter()
    examples: List[str] = []
    no_relation = np.zeros(len(idx_probe), dtype=bool)
    for j, i in enumerate(idx_probe):
        qw, ww = query_words[int(i)], winner_words[int(i)]
        if bool(in_gold[int(i)]):
            rel["IN_THE_GENEROUS_GOLD"] += 1
            continue
        sq, sw = wn.synsets(qw), wn.synsets(ww)
        if not sq or not sw:
            rel["WINNER_NOT_IN_WORDNET"] += 1
            continue
        best = 0.0
        for a in sq[:4]:
            for b in sw[:4]:
                if a.pos() != b.pos():
                    continue
                p = a.path_similarity(b)
                if p and p > best:
                    best = float(p)
        if best >= 0.25:
            rel["TAXONOMICALLY_CLOSE_but_outside_the_gold"] += 1
        elif best > 0.0:
            rel["TAXONOMICALLY_DISTANT"] += 1
            no_relation[j] = True
        else:
            rel["NO_WORDNET_PATH_AT_ALL"] += 1
            no_relation[j] = True
        if len(examples) < 20:
            examples.append("%s -> %s (path_sim=%.3f)" % (qw, ww, best))
    n = len(idx_probe)
    return {"n_probed": n, "counts": {k: int(v) for k, v in rel.most_common()},
            "fractions": {k: round(v / n, 4) for k, v in rel.most_common()} if n else {},
            "fraction_no_close_relation": round(float(no_relation.mean()), 4) if n else None,
            "no_relation_bool": no_relation.tolist(), "examples": examples}


def syntagmatic_jaccard_composition(query_words: Sequence[str], winner_words: Sequence[str],
                                    gold_words: Sequence[Optional[str]], where: Dict[str, set],
                                    idx_probe: np.ndarray) -> Dict:
    """C2-style syntagmatic test (exp_readout_second_order_v1): sentence-level Jaccard co-occurrence
    of query-vs-winner and query-vs-best-gold, over the SAME corpus the store was built from."""
    def jac(a: str, b: Optional[str]) -> Optional[float]:
        if b is None:
            return None
        A, B = where.get(a), where.get(b)
        if not A or not B:
            return None
        return len(A & B) / float(len(A | B))

    jw, jg = [], []
    for i in idx_probe:
        i = int(i)
        qw = query_words[i]
        v = jac(qw, winner_words[i])
        if v is not None:
            jw.append(v)
        v2 = jac(qw, gold_words[i])
        if v2 is not None:
            jg.append(v2)

    def stat(x: List[float]) -> Dict:
        if not x:
            return {"n": 0, "mean": None, "median": None, "frac_ever_co_occurring": None}
        xa = np.asarray(x, dtype=np.float64)
        return {"n": int(xa.size), "mean": round(float(xa.mean()), 5),
                "median": round(float(np.median(xa)), 5),
                "frac_ever_co_occurring": round(float((xa > 0).mean()), 4)}

    sw, sg = stat(jw), stat(jg)
    ratio = (sw["mean"] / max(sg["mean"], 1e-12)) if sw["mean"] is not None and sg["mean"] else None
    return {"TOP1_WINNER": sw, "BEST_GOLD_SYNONYM": sg,
            "winner_over_gold_ratio_of_means": round(ratio, 3) if ratio is not None else None,
            "jw_array": jw, "jg_array": jg}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    print("[selftest] reusing PIPE's own self_test() wholesale (FB, dprime, rank_summary, "
          "monotonicity checker, INFO's own self_test chained inside it)", flush=True)
    ev["PIPE_selftest_keys"] = sorted(PIPE.self_test().keys())

    # --- FILTER isolation, real construction, tiny scale (Gate F.1: exercise the REAL objects) ---
    sent = "The cat sat on the mat and the dog ran to the abbey with a highclere pigment."
    filt = INFO.raw_counts_for_window(sent, "cat")
    unf = raw_counts_unfiltered_for_window(sent, "cat")
    assert "the" not in filt and "on" not in filt, "FILTERED counts leaked a stopword: %r" % filt
    assert "the" in unf and "on" in unf, "UNFILTERED counts lost a stopword: %r" % unf
    assert set(filt) <= set(unf), "FILTERED vocabulary is not a subset of UNFILTERED on the same " \
                                  "sentence -- the two tokenizers disagree on more than the filter"
    assert unf["the"] >= 2, "UNFILTERED must keep repeats (a COUNT vector, not a set): %r" % unf
    assert "cat" not in filt and "cat" not in unf, "target-lemma self-exclusion did not fire"
    ev["FILTER_isolation_real_code_path"] = {"filtered_vocab": sorted(filt), "unfiltered_vocab": sorted(unf)}

    # --- NORMALISE isolation: sign() applied consistently to store+query changes argmax on a
    # constructed case where it must (magnitude-only difference collapses under sign) --------------
    store = np.array([[3.0, 1.0], [1.0, 3.0]], dtype=np.float64)
    q = np.array([[2.0, 0.5]], dtype=np.float64)     # closer to row0 in COSINE on raw magnitudes
    s_graded = l2n(store) @ l2n(q).T
    s_sign = l2n(np.sign(store)) @ l2n(np.sign(q)).T
    assert not np.allclose(s_graded, s_sign), "sign() must change the score in this fixture"
    ev["NORMALISE_isolation_changes_score"] = True

    # --- wordnet_relation_composition: known IN_GOLD, known NO_PATH, known TAXONOMICALLY_CLOSE ---
    qw_ = ["dog", "dog", "dog"]
    ww_ = ["canine", "carburetor", "dog"]     # close synonym-ish / unrelated / trivially in-gold
    ig_ = np.array([False, False, True])
    idxp = np.array([0, 1, 2])
    comp = wordnet_relation_composition(qw_, ww_, ig_, idxp)
    assert comp["n_probed"] == 3
    assert comp["counts"].get("IN_THE_GENEROUS_GOLD", 0) == 1, comp
    assert sum(comp["counts"].values()) == 3, comp
    ev["wordnet_relation_composition_known_answers"] = comp["counts"]

    # --- syntagmatic_jaccard_composition: known co-occurrence via a tiny hand-built index ---------
    where_ = {"a": {0, 1}, "b": {0, 1}, "c": {5}, "d": set()}
    comp2 = syntagmatic_jaccard_composition(["a", "a"], ["b", "c"], ["b", None], where_,
                                            np.array([0, 1]))
    assert comp2["TOP1_WINNER"]["n"] == 2 and abs(comp2["TOP1_WINNER"]["mean"] - 0.5) < 1e-9, comp2
    ev["syntagmatic_jaccard_known_answer"] = comp2["TOP1_WINNER"]

    # --- arms-must-differ on a tiny synthetic construction (META_RULE_AF) --------------------------
    a1 = np.array([1.0, 2.0, 3.0])
    a2 = np.array([1.0, 2.0, 3.0001])
    assert _digest(a1) != _digest(a2), "distinct arrays must produce distinct digests"
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test, called not reimplemented) ---
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    P_ = PIPE.build_population()
    C, mat, mat_ok = P_["C"], P_["mat"], P_["mat_ok"]
    n_anchors, qidx = P_["n_anchors"], P_["qidx"]
    GOLD, E, keep_ALL = P_["GOLD"], P_["E"], P_["keep"]
    aux = P_["aux"]

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:300]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    MATn = l2n(mat)
    query_words = [C["L_words"][int(t)] for t in T]
    anchors = list(C["anchors"])
    print(f"[load] n_anchors={n_anchors} n_items={n_items} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": PIPE.CTS.ruler_mode_gate(),
        "population": {"n_anchors": n_anchors, "n_items_scored": n_items,
                       "pool": "the LANDED OPEN pool (mat_ok minus per-item exclusions), same as "
                               "exp_pipeline_stage_oracle_ladder_v1"},
    }

    # =============================== REGRESSION GATE (proves the same instrument) ===================
    S_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E, GOLD)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGRESSION_GATE"] = {"measured": round(a0_full, 4), "expected": PIPE.REGRESSION_A0_PARTIAL,
                              "tol": PIPE.REGRESSION_TOL,
                              "PASS": bool(abs(a0_full - PIPE.REGRESSION_A0_PARTIAL) <= PIPE.REGRESSION_TOL)}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % rep["REGRESSION_GATE"])
    print("[regression] PASS %.4f (expected %.4f)" % (a0_full, PIPE.REGRESSION_A0_PARTIAL), flush=True)
    del S_full, h_full

    # =============================== FLOORS, recomputed on THIS population ==========================
    floors_S: Dict[str, np.ndarray] = {}
    Tq = aux["Tq"][T]
    floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(Tq).T).astype(np.float32)
    floors_S["F_FREQUENCY"] = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 291)) @ l2n(Q_exact).T).astype(np.float32)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    S_cache: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add_arm(name: str, S: np.ndarray, addressing_target: Optional[np.ndarray] = None) -> None:
        nonlocal scored_all
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        hits_exp[name] = h["hit_exp"]; hits_opt[name] = h["hit_opt"]; hits_cons[name] = h["hit_cons"]
        scored_all = scored_all & h["scored"]
        noise_of[name] = PIPE.dprime_summary(PIPE.dprime_stats(S, E_T, GOLD_T))
        rs, _, _ = PIPE.rank_summary(S, E_T, GOLD_T)
        rank_of[name] = rs
        if addressing_target is not None:
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = addressing_target >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == addressing_target[ok])), 6)
        S_cache[name] = S
        print(f"[{name}] hit@1={h['hit_exp'][h['scored']].mean():.4f} n_scored={int(h['scored'].sum())}",
             flush=True)

    for k, S in floors_S.items():
        add_arm(k, S)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)

    # =============================== WRITE-SIDE CORPUS (reused, cached) =============================
    print("[corpus] loading (cached; instant if scratch/cue_information_audit_v1/buckets_full.npz "
         "exists)", flush=True)
    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, item_diag = INFO.C3.build_items(shim, buckets, counts, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), \
        "rebuilt item metadata does not align with cached L_words -- STOP"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    anchor_ids = anchors

    # ---- R2/R3 FILTERED (single-occ, full-accum) -- REUSED VERBATIM, byte-identical constructions
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    P_full, _Q_ctx_full, reuse_diag = PIPE.load_full_accum_from_checkpoint(info_out_dir, anchor_ids, item_ids_T)
    rep["checkpoint_reuse_R3_full_accum"] = reuse_diag
    P_single, single_diag = PIPE.build_single_occurrence_counts(anchor_ids, buckets, sents)
    rep["single_occurrence_build_R2"] = single_diag

    # ---- R1 UNFILTERED (single-occ) -- NEW, matched sentence-per-anchor to R2 ----------------------
    P_single_unf, single_unf_diag = build_single_occurrence_counts_unfiltered(anchor_ids, buckets, sents)
    rep["single_occurrence_build_R1_unfiltered"] = single_unf_diag

    vocab_f = INFO.build_vocab([P_full, P_single])
    vocab_u = INFO.build_vocab([P_single_unf])
    rep["vocab_sizes"] = {"filtered_content_words": len(vocab_f), "unfiltered_all_tokens": len(vocab_u)}
    Pm_full = INFO.l2n_sparse(INFO.to_sparse(P_full, anchor_ids, vocab_f))
    Pm_single = INFO.l2n_sparse(INFO.to_sparse(P_single, anchor_ids, vocab_f))
    Pm_single_unf = INFO.l2n_sparse(INFO.to_sparse(P_single_unf, anchor_ids, vocab_u))

    S_R1 = np.asarray((Pm_single_unf @ Pm_single_unf[qidx_T].T).todense(), dtype=np.float32)
    S_R2 = np.asarray((Pm_single @ Pm_single[qidx_T].T).todense(), dtype=np.float32)
    S_R3 = np.asarray((Pm_full @ Pm_full[qidx_T].T).todense(), dtype=np.float32)
    S_R4 = (MATn @ l2n(Q_exact).T).astype(np.float32)                      # incumbent, GRADED
    mat_sign = np.sign(mat)
    Q_exact_sign = np.sign(Q_exact)
    S_R5 = (l2n(mat_sign) @ l2n(Q_exact_sign).T).astype(np.float32)        # NORMALISE applied

    add_arm("R1_UNFILTERED_SINGLE_OCC", S_R1, addressing_target=qidx_T)
    add_arm("R2_FILTERED_SINGLE_OCC", S_R2, addressing_target=qidx_T)
    add_arm("R3_FILTERED_FULL_ACCUM", S_R3, addressing_target=qidx_T)
    add_arm("R4_PROJECTED_GRADED_FULL_ACCUM", S_R4, addressing_target=qidx_T)
    add_arm("R5_PROJECTED_SIGN_FULL_ACCUM", S_R5, addressing_target=qidx_T)

    # ---- N1 NULL: derangement of R4's query assignment ---------------------------------------------
    rng_n = np.random.default_rng(MASTER_SEED + 4242)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng_n.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    S_null = (MATn @ l2n(Q_exact[perm]).T).astype(np.float32)
    add_arm("N1_RANDOM_NULL", S_null, addressing_target=qidx_T)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== SANITY (K1/N1) -- gates BEFORE anything else is published ------
    main_rungs = ["R1_UNFILTERED_SINGLE_OCC", "R2_FILTERED_SINGLE_OCC", "R3_FILTERED_FULL_ACCUM",
                 "R4_PROJECTED_GRADED_FULL_ACCUM", "R5_PROJECTED_SIGN_FULL_ACCUM"]
    k1 = {name: addressing_of.get(name) for name in main_rungs}
    k1_pass = all((v is not None and v >= ADDRESS_EXACT_MIN) for v in k1.values())
    n1_addr = addressing_of.get("N1_RANDOM_NULL")
    n1_addr = 1.0 if n1_addr is None else n1_addr
    n1_pass = bool(n1_addr < max(0.02, 20.0 / n_anchors))
    rep["K1_KNOWN_ANSWER"] = {"addressing_per_rung": k1, "gate": ADDRESS_EXACT_MIN, "PASS": bool(k1_pass)}
    rep["N1_NULL"] = {"addressing_RANDOM_NULL": n1_addr, "chance_addressing": round(1.0 / n_anchors, 8),
                      "PASS": n1_pass}
    if not (k1_pass and n1_pass):
        raise SystemExit("INSTRUMENT_STILL_LOOSE -- K1/N1 gate failed, publishing nothing: K1=%r N1=%r"
                         % (rep["K1_KNOWN_ANSWER"], rep["N1_NULL"]))
    print("[gates] K1 PASS (%r) N1 PASS (%.6f < chance-ish threshold)" % (k1, n1_addr), flush=True)

    # =============================== BOOTSTRAP ========================================================
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    ci_halfwidth = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
                    for k, v in boot.items()}
    analytic_null_hw = round(float(1.645 / np.sqrt(max(nc - 1, 1))), 5)
    rep["POWER"] = {"n_common_scored": nc, "analytic_null_halfwidth": analytic_null_hw}
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1390", "0.0873", "0.1382", "0.2070", "-0.1959"]
    rep["BINDING_FLOOR"] = binding
    rep["BINDING_FLOOR_VALUE"] = round(acc[binding], 4) if binding else None

    # =============================== RANKED DROP TABLE ================================================
    step_pairs = [
        ("R1_UNFILTERED_SINGLE_OCC", "R2_FILTERED_SINGLE_OCC", "FILTER"),
        ("R2_FILTERED_SINGLE_OCC", "R3_FILTERED_FULL_ACCUM", "ACCUMULATE_not_a_downstream_pair"),
        ("R3_FILTERED_FULL_ACCUM", "R4_PROJECTED_GRADED_FULL_ACCUM", "CODE_PROJECT"),
        ("R4_PROJECTED_GRADED_FULL_ACCUM", "R5_PROJECTED_SIGN_FULL_ACCUM", "NORMALISE"),
    ]
    drops = []
    for a, b, tag in step_pairs:
        m = FB.margin(boot, a, b)
        drops.append({"from": a, "to": b, "step": tag, "drop_point": m["point"], "drop_ci95": m["ci95"],
                      "drop_ci_halfwidth": round((m["ci95"][1] - m["ci95"][0]) / 2.0, 4), "band": m["band"]})
    drops_ranked = sorted(drops, key=lambda d: abs(d["drop_point"]), reverse=True)
    rep["RANKED_DROP_TABLE"] = drops_ranked

    # =============================== MONOTONICITY -- PER-LEG, NEVER SKIPPING A RUNG =================
    # BUG CAUGHT BY THIS CELL'S OWN FIRST FULL RUN, DISCLOSED NOT QUIETLY FIXED: v1.0's first cut
    # built ONE chain [R1,R2,R4,R5] that DROPPED R3 out of the array entirely (meaning to exempt only
    # the R2->R3 ACCUMULATE *transition* per the exp_pipeline_stage_oracle_ladder_v1 precedent). That
    # made R2 and R4 artificially ADJACENT, so check_monotone_nonincreasing scored a rise of
    # acc[R4]-acc[R2] as if it were one step, when it is actually TWO real steps (ACCUMULATE then
    # CODE_PROJECT) added together. The reported "LEAK" (rung_index=2, rise=0.0140) was this
    # arithmetic artifact, not a leak in the ladder. Fixed: three separate PER-LEG checks, each on
    # genuinely adjacent rungs, so no leg's check can smuggle in a skipped rung's effect.
    def _leg(a: str, b: str) -> Dict:
        return PIPE.check_monotone_nonincreasing([acc[a], acc[b]],
                                                  [ci_halfwidth[a] / 2.0, ci_halfwidth[b] / 2.0],
                                                  MONOTONE_TOL_SIGMA)
    mono_filter = _leg("R1_UNFILTERED_SINGLE_OCC", "R2_FILTERED_SINGLE_OCC")
    mono_project = _leg("R3_FILTERED_FULL_ACCUM", "R4_PROJECTED_GRADED_FULL_ACCUM")
    mono_normalise = _leg("R4_PROJECTED_GRADED_FULL_ACCUM", "R5_PROJECTED_SIGN_FULL_ACCUM")
    legs = {"FILTER_R1_to_R2": mono_filter, "CODE_PROJECT_R3_to_R4": mono_project,
           "NORMALISE_R4_to_R5": mono_normalise}
    rep["MONOTONICITY_PER_LEG"] = legs
    rep["MONOTONICITY"] = {"MONOTONE": all(v["MONOTONE"] for v in legs.values()),
                           "n_leaks": sum(v["n_leaks"] for v in legs.values()),
                           "legs_with_leak": [k for k, v in legs.items() if not v["MONOTONE"]],
                           "tol_sigma": MONOTONE_TOL_SIGMA}
    rep["MONOTONICITY_NOTE"] = (
        "R2->R3 (ACCUMULATE) is EXCLUDED from every leg check, for the identical reason "
        "exp_pipeline_stage_oracle_ladder_v1 excluded its own B1->B2: more accumulated evidence is "
        "not a downstream information-loss step. Its own drop/rise is reported in the RANKED_DROP_"
        "TABLE and is not hidden. FILTER, CODE_PROJECT and NORMALISE are each checked on their OWN "
        "genuinely-adjacent pair, never skipping a rung -- the construction bug this replaces (v1.0's "
        "first full run) skipped R3 out of the array and scored a spurious two-step rise as one leak; "
        "see MONOTONICITY_NOTE_BUG_DISCLOSURE.")
    rep["MONOTONICITY_NOTE_BUG_DISCLOSURE"] = (
        "v1.0's FIRST full run (elapsed 41.3s, same day) reported WRITERULE_LADDER_LEAK_DETECTED from "
        "a chain [R1,R2,R4,R5] that omitted R3, so the printed 'rise' (rung_index=2, rise=0.0140, "
        "combined_ci_halfwidth=0.0057) was acc[R4]-acc[R2], not a genuinely-adjacent comparison. The "
        "PER-LEG fix below shows that rise decomposes into a REAL drop (R2->R3, ACCUMULATE, -0.0263 "
        "BELOW, exempted per precedent) followed by a REAL, CI-separated rise (R3->R4, CODE_PROJECT, "
        "+0.0123 ABOVE) that independently reproduces exp_pipeline_stage_oracle_ladder_v1's own "
        "DIAG_B2->LAM_1.00 margin BIT-FOR-BIT (+0.0123 [+0.006,+0.0188] in both cells) -- cross-cell "
        "replication, not a construction artifact. Whether that rise is itself a leak or a genuine "
        "denoising effect of the lossy random projection is addressed by CODE_PROJECT's own leg check "
        "below, not swept into an unrelated pair.")

    # =============================== WINNER COMPOSITION -- the scientific core ======================
    print("[composition] building sentence co-occurrence index (content_lemmas over %d sentences, "
         "REUSED corpus, store never rebuilt)" % len(sents), flush=True)
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in content_lemmas(s):
            where.setdefault(w, set()).add(si)

    rng_probe = np.random.default_rng(MASTER_SEED + 909)
    common_idx = np.flatnonzero(scored_all)
    idx_probe = rng_probe.choice(common_idx, size=min(N_PROBE_COMPOSITION, common_idx.size), replace=False)
    idx_probe = np.sort(idx_probe)
    rep["COMPOSITION_N_PROBE"] = int(idx_probe.size)

    composition_per_rung: Dict[str, Dict] = {}
    no_relation_bool_of: Dict[str, np.ndarray] = {}
    for name in main_rungs:
        S = S_cache[name]
        out_dir_ckpt = os.path.join(REPO, "data", ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
        ck_key = unit_key("COMPOSITION", CODE_VERSION, grid, name)
        prior = load_units(out_dir_ckpt).get(ck_key)
        if prior is not None:
            print("[composition] %s RESUMED FROM CHECKPOINT" % name, flush=True)
            composition_per_rung[name] = prior
            no_relation_bool_of[name] = np.array(prior["wordnet"]["no_relation_bool"], dtype=bool)
            continue
        Sm = np.where(E_T, S, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        winner_words = [anchors[int(w)] for w in top1]
        in_gold = np.array([bool(GOLD_T[int(top1[i]), i]) for i in range(n_items)])
        gbest = np.where(GOLD_T & E_T, Sm, -np.inf)
        gtop = np.argmax(gbest, axis=0)
        has_gold = (GOLD_T & E_T).any(axis=0)
        gold_words: List[Optional[str]] = [anchors[int(gtop[i])] if has_gold[i] else None
                                           for i in range(n_items)]
        wn_comp = wordnet_relation_composition(query_words, winner_words, in_gold, idx_probe)
        jac_comp = syntagmatic_jaccard_composition(query_words, winner_words, gold_words, where, idx_probe)
        rec = {"wordnet": wn_comp, "syntagmatic": jac_comp}
        composition_per_rung[name] = rec
        no_relation_bool_of[name] = np.array(wn_comp["no_relation_bool"], dtype=bool)
        record_unit(out_dir_ckpt, ck_key, rec)
        print("[composition] %s no_relation=%.3f winner_cooc=%s gold_cooc=%s ratio=%s" % (
            name, wn_comp["fraction_no_close_relation"] or -1, jac_comp["TOP1_WINNER"]["mean"],
            jac_comp["BEST_GOLD_SYNONYM"]["mean"], jac_comp["winner_over_gold_ratio_of_means"]),
            flush=True)
    rep["WINNER_COMPOSITION_PER_RUNG"] = composition_per_rung

    # ---- paired composition deltas across the SAME step pairs, bootstrap over idx_probe ------------
    comp_drops = []
    rng_cb = np.random.default_rng(MASTER_SEED + 5151)
    n_probe = idx_probe.size
    for a, b, tag in step_pairs:
        if a not in no_relation_bool_of or b not in no_relation_bool_of:
            continue
        xa, xb = no_relation_bool_of[a].astype(np.float64), no_relation_bool_of[b].astype(np.float64)
        boot_idx = rng_cb.integers(0, n_probe, size=(2000, n_probe))
        diff = xb[boot_idx].mean(axis=1) - xa[boot_idx].mean(axis=1)
        lo, hi = float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))
        band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
        comp_drops.append({"from": a, "to": b, "step": tag,
                           "no_relation_rate_from": round(float(xa.mean()), 4),
                           "no_relation_rate_to": round(float(xb.mean()), 4),
                           "delta_point": round(float(np.mean(diff)), 4),
                           "delta_ci95": [round(lo, 4), round(hi, 4)], "band": band})
    rep["COMPOSITION_DELTA_TABLE"] = comp_drops

    # =============================== STOP-IF EVALUATION ================================================
    top_drop = drops_ranked[0] if drops_ranked else None
    span = sum(abs(d["drop_point"]) for d in drops_ranked) or 1.0
    dominant = bool(top_drop is not None and abs(top_drop["drop_point"]) / span > 0.5)
    distributed = bool(top_drop is not None and abs(top_drop["drop_point"]) / span <= 0.5
                       and span > 3 * analytic_null_hw)
    composition_flip = [d for d in comp_drops if d["band"] != "NOT_SEPARATED"
                        and abs(d["delta_point"]) >= 0.03]
    stop_if: List[str] = []
    if dominant:
        stop_if.append("(i) ONE_STEP_DOMINATES -- the 'distributed deficit' reading is WRONG")
    if distributed and not dominant:
        stop_if.append("(ii) LOSS_SPREAD_EVENLY -- the distributed reading is CONFIRMED")
    if composition_flip:
        stop_if.append("(iii) ACCURACY_FLAT_COMPOSITION_SHIFTS -- a build target independent of "
                       "accuracy: %r" % composition_flip)
    if not rep["MONOTONICITY"]["MONOTONE"]:
        stop_if.append("(iv->leak) MONOTONICITY LEAK in leg(s) %r -- report the leak, not the ladder"
                       % rep["MONOTONICITY"]["legs_with_leak"])
    rep["STOP_IF_FIRED"] = stop_if if stop_if else ["NONE of (i)-(iv) fired on this run's numbers"]

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

    mono = rep.get("MONOTONICITY", {})
    drops = rep.get("RANKED_DROP_TABLE", [])
    top = drops[0] if drops else None
    verdict = "WRITERULE_LADDER_%s__TOP_STEP_%s__STOPIF_%s" % (
        "MONOTONE" if mono.get("MONOTONE") else "LEAK_DETECTED",
        (top["step"] if top else "NONE"),
        "FIRED" if any("NONE" not in s for s in rep.get("STOP_IF_FIRED", [])) else "NONE")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ORGAN A write-rule step ladder: FILTER / ACCUMULATE(not a downstream pair) / "
            "CODE_PROJECT / NORMALISE, oracle-cue self-address throughout, with WordNet-relation-"
            "rate and co-occurrence-ratio composition measured at every rung on a shared paired "
            "probe. -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "N_PROBE_COMPOSITION": N_PROBE_COMPOSITION,
                   "MONOTONE_TOL_SIGMA": MONOTONE_TOL_SIGMA, "ADDRESS_EXACT_MIN": ADDRESS_EXACT_MIN},
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
