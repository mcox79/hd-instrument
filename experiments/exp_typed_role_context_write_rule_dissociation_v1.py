"""exp_typed_role_context_write_rule_dissociation_v1 -- DOES THE GRAMMATICAL RELATION CARRY
SUBSTITUTABILITY THAT A BAG-OF-WORDS CONTEXT DISCARDS?

THIS IS THE CELL notes/admissible_supervision_sources_drill_2026-08-18.md sec 6 PRE-REGISTERED, per
`notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.29 (4). Read those two sources in full before
touching this file; this docstring summarises, it does not replace them.

=================================================================================================
WHY THIS CELL, AND WHY IT IS NOT A SIXTH TWEAK. Organ A (sec 6.23) gated all five write-rule steps,
PPMI(+SVD), second-order cosine and a from-scratch SGNS -- EVERY arm sits between 0.02 and 0.44 on
the dissociation AUC -- and concluded the missing ingredient is a LEARNING SIGNAL. The 6.28 drill
found what nobody had noticed across ~15 experiments: every one of those arms represented a word's
context as an UNORDERED BAG of the words in its sentence (verified in source,
`exp_cue_information_audit_v1.raw_counts_for_window`). Filter, code, accumulate, normalise,
superpose, max-pool, binarise, profile-write all varied WHICH words counted or HOW they were
weighted; NONE used the GRAMMATICAL RELATION. Even the closest prior arm,
`F3_SYNTACTIC_NEIGHBOURS_ONLY` (`exp_writerule_filter_superpose_gate_v1`, 0.4876 +/-0.0114), kept
only neighbour IDENTITY and discarded the label. One whole axis -- typed structure -- was never
varied. This cell is the first arm on that axis.

THE IDEA, one line: two substitutable words fill the SAME TYPED SLOTS -- subject of the same verbs,
object of the same verbs -- even when they never co-occur, and nothing about that consults a
dictionary.

=================================================================================================
PRIOR-WORK CHECK -- performed for me by the Director (main session), not by `substrate_query.sh`
(confirmed non-functional this session: returns zero bytes, exits 0 -- do not use it, do not treat
its silence as "no prior work"). Method used instead: a bounded name-level enumeration over
`experiments/` (cheap; the whole-`data/` os.walk this cell's own pre-reg drill used is the wrong tool
for a code-reuse check and was correctly abandoned). Result, relayed verbatim:

  `experiments/exp_dependency_context_codebook_location_artifact_v1.py` (2026-07-20) and its
  `..._weight_sweep_location_artifact_v2.py` ran the SAME hypothesis once before: "dependency-context
  vs window-context PPMI-SVD codebook ... SAME pipeline, differing ONLY in the co-occurrence feature:
  window (word, word) vs dependency-typed (word, relation+direction)". It credits Levy & Goldberg
  2014 (typed relations shift induced similarity from "relatedness" toward "similarity/co-type") and
  Komninos & Manandhar 2016 (window+dependency COMBINED beats either alone) -- both cited here too,
  first-hand read of that cell's own docstring, not copied blind.

  IT NEVER LANDED (no `data/` directory for it) -- the idea is UNPROVEN, not refuted, and this cell
  is the first to score it on the licensed dissociation instrument.

  ITS FEATURE-BUILDING CODE (`build_dependency_trigger_table` / `build_dep_cooc`) IS NOT REUSED HERE,
  and the reason is stated rather than silently diverged from: that cell had NO real dependency parser
  available (its own docstring: "no spaCy in .venv" at the time) and its corpus (text8) has ZERO
  sentence boundaries, so it built a RULE-BASED closed-class preposition/verb-slot approximation as an
  explicit fallback. Neither constraint applies here -- this project now owns a real, persisted,
  glass-box dependency parser (`hdlab.arc_parser` + `hdlab.arc_labeler` + `hdlab.pos_tagger`, already
  exercised by `experiments/selectional_preference_extractor_v1.py` on sentence-bounded text) -- so
  this cell uses the REAL parse, which is strictly the more faithful test of the SAME hypothesis those
  two authors named. Its `build_random_context_cooc` (permute a cooccurrence matrix's column
  assignment to destroy word-context association while preserving mass) is the same DESIGN PATTERN
  this cell's `random_typing_arc_events` control uses, arrived at independently but credited here on
  sight of the prior file.

  `exp_derived_filler_typing_single_edge_grounding_v1`'s ARTIFACT_POOL/LOCATION_POOL split was also
  flagged as a ready-made typed-item population; NOT used here -- this cell's population is DSI's own
  licensed 242-matched-pair population (nouns only), a different task and a different, already-vetted
  matching discipline (see NON-NEGOTIABLE PRECONDITIONS below); reusing a differently-matched
  population here would reintroduce exactly the floor-separation problems DSI's seven tightening
  rounds closed.

=================================================================================================
THE BAR IS max(FOUR FLOORS) = 0.5431 (F_CONSTANT_PROTOTYPE), NOT 0.5. Chance is 0.5; clearing 0.5 is
NOT clearing the bar. Every AUC below is reported against BOTH.

=================================================================================================
NON-NEGOTIABLE PRECONDITIONS (drill sec 6.1, restated as code-level commitments):
  1. LICENCE GATE FIRST. Reuses `exp_predictive_coding_write_gate_dissociation_v1.dsi_regression_gate`
     VERBATIM (not re-implemented) -- reproduces DSI's 8 cached checks at delta<=0.0005 and raises
     SystemExit on any miss, checked before anything else in this file runs.
  2. REUSE, DO NOT FORK. Front-end: `hdlab.pos_tagger.PosTagger` / `hdlab.arc_parser.ArcParser` /
     `hdlab.arc_labeler.ArcLabeler`, loaded via `experiments.selectional_preference_extractor_v1.
     _load_frontend()` (same persisted assets that cell already verified against the owner's own
     sentence). Global slot-filler distribution: `experiments.selectional_preference_extractor_v1.
     _process_chunk` / `_init_worker` called DIRECTLY on THIS cell's own corpus (never on
     `thematic_relation_extractor_v1`'s larger SimpleWiki budget -- that would be a second, uncontrolled
     variable). `CORE_ROLE` / `OBL_ROLE` / `STRUCT_TOKEN_RE` / `MIN_LEMMA_LEN` are reused from the same
     module so tokenisation is IDENTICAL between the slot pass and this cell's own targeted parse pass.
     Population / scorer / floors / K1 / N0: `exp_dissociation_score_instrument_v1`, reused via its
     regression-gated cache, never re-derived. `hdlab/predictive_coding.py`'s `residual_magnitude` is
     NOT reused for S1 (see S1 ALGEBRA below for why threshold/proportional gates do not fit a
     100%-write signed rule) -- the signed delta rule is new code, confined to THIS file, and is
     labelled OUR INVENTION UNDER TEST throughout, exactly as the drill requires. `hdlab/` is not
     edited (per this cell's own dispatch RULES: "Do NOT wire into hdlab/").
  3. NO HYPERPARAMETER SELECTED ON THE 242 PAIRS. The one threshold this cell introduces
     (COVERAGE_MIN, for N5) is fixed HERE, before any number in this file is computed, at 3
     (occurrences/slots) -- disclosed as a modest, corpus-scale-appropriate choice (this corpus is
     34,169 sentences vs the 41,529-slot asset's 737,488 -- roughly 22x smaller), not tuned to a
     result.
  4. ONE VARIABLE. Every arm re-extracts contexts from THIS CELL'S OWN 34,169-sentence corpus
     (`exp_cue_information_audit_v1.load_corpus_and_buckets`, the SAME corpus DSI's own
     RAW_COUNT_FULL_ACCUM arm was built from) via the SAME profile-occurrence convention
     (`buckets[w][:_n_profile(len(buckets[w]))]`, reused from
     `exp_grounding_readout_known_answer_v1._n_profile`). A0's OWN SCORE is not rebuilt -- it is
     DSI's cached RAW_COUNT_FULL_ACCUM arm (0.0510), the plain bag-of-words raw-count store over this
     identical corpus/occurrence convention, so the ONLY thing that differs between A0 and U1/U3/S1 is
     the context TYPE or the write RULE, never the corpus, the occurrence set, or the accumulation
     convention.
  5. NO LLM ANYWHERE. No pretrained table imported. Asserted in metrics.json.

=================================================================================================
S1 ALGEBRA, LABELLED OUR INVENTION (drill sec 3.4's own table: "the specific algebra ... is OUR
INVENTION UNDER TEST"). For occurrence of filler w in slot (v, ROLE), let `prior_share` = the GLOBAL,
whole-corpus fraction of that slot's observations already filled by w BEFORE this cell ever sees the
occurrence (a steady-state / batch quantity -- computed once from the FULL corpus's final slot-filler
distribution, not accumulated online in corpus order; disclosed as a scoped simplification, not a
claim about trial-by-trial cortical dynamics). delta = 1 - 2*prior_share, in (-1, 1]: a filler novel
to its slot (prior_share=0) writes at full strength (+1); a filler that is the ONLY thing that has
ever filled that slot (prior_share=1) is actively discounted (-1); a filler at exactly half the
slot's mass is neutral (0). Every occurrence is written (delta can be 0 or negative but the occurrence
is never skipped) -- S1's token count is IDENTICAL to A0's by construction, which is why the
rate-matched control that killed the 6.21 write-gate null CANNOT recur here; the correct control is
`N3_MAGNITUDE_PERMUTED`. `prior_share` is computed against the SLOT'S OWN GLOBAL FILLER POPULATION
(every corpus filler of that slot, not just the 617 matched-pair words) -- the direct operational
difference from 6.21's null, which compared a word only to ITS OWN running accumulator (a
self-prediction that can never discover two words never seen together belong in the same slot).

ARMS: A0_INCUMBENT (reused, not rebuilt) / U1_TYPED_CONTEXT / U3_ROLE_ONLY / S1_SLOT_COMPETITION /
N1_LABEL_PERMUTED / N2_RANDOM_TYPING / N3_MAGNITUDE_PERMUTED / N5_COVERAGE_MATCHED (applied to U1 and
S1) / N6_PARSE_NOISE (a sweep). K1 / N0 / four floors reused bit-for-bit from DSI's cache.
U2_TYPED_PPMI_SVD, S2_SLOT_COMPETITION_REPLAY and X1_SENSORIMOTOR_ERROR are DELIBERATELY OMITTED for
budget (drill sec 6.2 explicitly licenses this for X1; the same licence is taken here for U2/S2 since
the primary falsifier is U1 vs N1 and S1 vs N3, and this is disclosed here rather than silently
dropped -- report as "omitted for budget", never as "untested-because-refuted").
N4_UNTRAINED is DECLARED N/A: no arm in this cell has a trainable weight distinct from the corpus
itself (U1/U3 are deterministic counts, S1 is a deterministic corpus-derived delta) -- there is no
"untrained" variant to compare against, unlike a gradient-trained embedding arm.

STOP-IF, evaluated in this order (drill sec 6.4):
  1. LICENCE fails -> ABORT (SystemExit from dsi_regression_gate, before this file's own code runs).
  2. U1 NOT CI-separated above N1_LABEL_PERMUTED -> typing is not the variable; report null.
  3. U1 ~ U3_ROLE_ONLY -> U1 is a POS-profile in disguise, not a lexical-context effect.
  4. U1 above N1 but below max(floors) -> report the margin, do NOT call it a win; proceed to S1.
  5. S1 NOT CI-separated above N3_MAGNITUDE_PERMUTED -> error signal not the variable at this site
     either; second independent negative on prediction error.
  6. full-population vs N5-coverage-matched AUC disagree by more than a CI width -> coverage artifact.
  7. N6 shows steep sensitivity to arc corruption -> the binding constraint is parse quality
     (UAS reused from `data/exp_depparse_hashed_cpu_v1/metrics.json`, cited not recomputed), not the
     mechanism.
  8. Any arm CI-clears 0.5431 above all four floors AND both its mandatory controls -> Organ A REOPENS.

PRE-REGISTERED PRIORS (drill sec 6.0, restated so this file cannot be accused of hindsight framing):
  typed contexts (unsupervised) CI-clear 0.5431 above floors: 0.15
  typed contexts CI-separated above N1 but still below 0.5431: 0.35
  supervised slot-competition (S1) CI-clears 0.5431: 0.20
  a clean, well-controlled negative that closes context-type as a variable: 0.45

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: SLOT_DIST (global corpus pass) and OCC (per-word occurrence data) as separate
#   tools.exp_checkpoint units, so a kill loses at most one word's occurrence build, not the whole run
# - discriminator survives scale: FULL runs the real 242-pair-per-cell population; --grid reduced
#   truncates matchedP/matchedS to [:40]/[:40] (DSI/CAP/write-gate convention), a REAL smaller subset
# - calibration_check: default_ok_for_this_regime (reuses DSI's licensed instrument unmodified; only
#   the context TYPE / write RULE is new, which is the thing under test)
# - progress_logging: print_flush_true (every phase prints a flushed line, Sec 17)
# - baseline_in_band: n/a -- licensing-gate + dissociation-AUC instrument, not a 0.05-0.95-band
#   baseline cell; declared explicitly
# - crlb_floor_computed: n/a -- an AUC dissociation measurement is not a capacity sweep
# - tie conventions: DSI's AUC scorer (Mann-Whitney rank-sum) has ONE convention throughout the
#   project; declared explicitly rather than silently omitting an inapplicable requirement

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded per worker process
(multiprocessing is across PROCESSES for the corpus-wide slot pass only, not a numpy thread pool).
NOTHING under hdlab/ is modified. `data/foundation/**` is never opened. Writes only under
data/exp_typed_role_context_write_rule_dissociation_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/DSI/INFO/SPE/C3/CTS/arc-parser next -- flushed so a slow "
      "import is never mistaken for a hang)", flush=True)

import argparse
import collections
import hashlib
import multiprocessing as mp
import sys
import time
import traceback
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI                       # noqa: E402
import experiments.exp_predictive_coding_write_gate_dissociation_v1 as PCWG          # noqa: E402
import experiments.exp_cue_to_store_translation_v1 as CTS                            # noqa: E402
import experiments.exp_cue_information_audit_v1 as INFO                              # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3                       # noqa: E402
import experiments.selectional_preference_extractor_v1 as SPE                        # noqa: E402
from hdlab.reading_grounding_loop import normalize_lemma                             # noqa: E402
from experiments._seed_checkpoint import get_output_dir, write_metrics               # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "typed_role_context_write_rule_dissociation_v1"
# TWO SEPARATE VERSION TAGS, DELIBERATELY: UPSTREAM_VERSION keys the two EXPENSIVE checkpointed
# passes (SLOT_DIST = the corpus-wide slot-filler pass, ~5 min; OCC = per-word targeted parse) so a
# downstream-only change (new arm, new control) never orphans them. CODE_VERSION keys everything
# downstream (arm construction, MAIN, self-test) and MUST be bumped whenever SLOT_DIST/occurrence_
# features/build_occurrence_data change -- per the coordinator's mid-run correction (2026-08-18): a
# resumed checkpoint whose upstream logic changed without a version bump is a silent-stale-reuse
# hazard. v1.1 added T2_UNTYPED_SAME_COVERAGE (same arc-connected words as U1, neighbour identity
# kept, LABEL stripped -- decides TYPE vs mere WORD SELECTION, the ORIGINAL brief's own T1/T2
# framing) and T3_COMBINED (bag ⊕ typed, L2-renorm, Komninos & Manandhar 2016) -- both are pure
# downstream additions; UPSTREAM_VERSION stays "v1.0" so the already-computed SLOT_DIST/OCC
# checkpoints from the prior (abandoned mid-run) smoke attempt remain valid and are reused, not
# recomputed.
UPSTREAM_VERSION = "v1.0"
CODE_VERSION = "v1.1"
FINDINGS = "notes/typed_role_context_write_rule_dissociation_2026-08-18.md"

DSI_CODE_VERSION = "v1.7"
UAS_SOURCE = "data/exp_depparse_hashed_cpu_v1/metrics.json"   # cited, never recomputed here
UAS_CITED = 0.7868

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--workers", type=int, default=4)
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"
N_WORKERS = max(1, int(_ARGS.workers))

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
COVERAGE_MIN = 3           # PRE-REGISTERED before any result in this file is seen (see docstring 3)
CORRUPT_FRACS = (0.0, 0.25) if SMOKE else (0.0, 0.1, 0.25, 0.5)

FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]


def _digest(v) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _encode_slot(verb: str, role: str) -> str:
    return "%s|||%s" % (verb, role)


def _decode_slot(key: str) -> Tuple[str, str]:
    v, r = key.split("|||", 1)
    return v, r


# =================================================================================================
# STEP A -- GLOBAL slot-filler distribution over THIS CELL'S OWN 34,169-sentence corpus.
# Reuses SPE._init_worker / SPE._process_chunk VERBATIM (never forked), called on OUR sentences
# instead of THEM.CORPUS. norms = the CTS anchor set (5,491 words, WordNet-free, LLM-free) -- NOT
# GS._table() (which pulls in torch + a separate embedding table for an unrelated purpose); this is
# a deliberate, disclosed deviation from SPE.extract()'s own default norms argument, made possible
# because _process_chunk takes norms as a plain parameter.
# =================================================================================================
def build_global_slot_distribution(sents: List[str], norms: set, out_dir_ckpt: str, grid: str,
                                   n_workers: Optional[int] = None) -> Dict:
    key = unit_key("SLOT_DIST", UPSTREAM_VERSION, grid)
    prior = load_units(out_dir_ckpt).get(key)
    if prior is not None:
        print("[slotdist] RESUMED FROM CHECKPOINT (n_slots=%d)" % prior["n_slots"], flush=True)
        return prior
    t0 = time.time()
    n_workers = N_WORKERS if n_workers is None else n_workers
    chunk = max(1, (len(sents) + n_workers * 8 - 1) // (n_workers * 8))
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    slot_filler: Dict[Tuple[str, str], collections.Counter] = collections.defaultdict(
        collections.Counter)
    stats = collections.Counter()
    role_hist: collections.Counter = collections.Counter()
    track: set = set()
    if n_workers <= 1:
        SPE._init_worker(norms, track)
        for i, ch in enumerate(chunks):
            sf, _wc, st, rh = SPE._process_chunk(ch)
            for k, v in sf.items():
                slot_filler[k].update(v)
            stats.update(st)
            role_hist.update(rh)
            print("[slotdist] chunk %d/%d t=%.0fs slots=%d" % (
                i + 1, len(chunks), time.time() - t0, len(slot_filler)), flush=True)
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=n_workers, initializer=SPE._init_worker,
                      initargs=(norms, track)) as pool:
            for i, res in enumerate(pool.imap_unordered(SPE._process_chunk, chunks)):
                sf, _wc, st, rh = res
                for k, v in sf.items():
                    slot_filler[k].update(v)
                stats.update(st)
                role_hist.update(rh)
                print("[slotdist] chunk %d/%d t=%.0fs slots=%d" % (
                    i + 1, len(chunks), time.time() - t0, len(slot_filler)), flush=True)
    encoded = {_encode_slot(v, r): dict(c) for (v, r), c in slot_filler.items()}
    result = {"slot_filler": encoded, "stats": dict(stats), "role_histogram": dict(role_hist),
             "n_slots": len(slot_filler), "n_workers": n_workers,
             "elapsed_s": round(time.time() - t0, 1)}
    record_unit(out_dir_ckpt, key, result)
    print("[slotdist] DONE n_slots=%d n_slot_obs=%d elapsed=%.0fs" % (
        result["n_slots"], stats.get("n_slot_observations", 0), result["elapsed_s"]), flush=True)
    return result


def slot_lookup_tables(slot_dist: Dict) -> Tuple[Dict[Tuple[str, str], Dict[str, int]],
                                                  Dict[Tuple[str, str], int]]:
    filler_counts: Dict[Tuple[str, str], Dict[str, int]] = {}
    totals: Dict[Tuple[str, str], int] = {}
    for k, fillers in slot_dist["slot_filler"].items():
        vr = _decode_slot(k)
        filler_counts[vr] = fillers
        totals[vr] = sum(fillers.values())
    return filler_counts, totals


# =================================================================================================
# STEP B -- per-word occurrence data, restricted to each word's OWN PROFILE occurrences (the SAME
# convention DSI's RAW_COUNT_FULL_ACCUM / A0 already used). One targeted parse per NEEDED sentence
# (cached in-memory across words sharing a sentence), never a second global corpus pass.
# =================================================================================================
def parse_sentence(tg, pr, lb, sentence: str):
    toks = SPE.STRUCT_TOKEN_RE.findall(sentence)
    if not toks or len(toks) > 60:
        return None
    try:
        pos = tg.tag(toks)
        heads = pr.parse(toks, pos).heads
        labs = lb.label(toks, pos, heads)
    except Exception:
        return None
    lemmas = [normalize_lemma(t) for t in toks]
    return toks, pos, heads, labs, lemmas


def occurrence_features(parse, target_lemma: str
                        ) -> Tuple[List[Tuple[str, str, str]], Optional[Tuple[str, str]]]:
    """-> (arc_events: [(neighbour_lemma, relation, direction)], slot: (verb, ROLE) or None).

    arc_events: every 1-hop dependency arc touching a token whose lemma == target_lemma, in either
    direction ("up" = target is the dependent, neighbour is its head; "down" = target is the head,
    neighbour is a dependent), neighbour filtered to alpha + len>=MIN_LEMMA_LEN (same content-word
    spirit as A0's own raw_counts_for_window, so the comparison is context-TYPE-only).
    slot: the FIRST core-role/oblique argument-of-a-VERB relation found on a matching token, using
    SPE.CORE_ROLE / SPE.OBL_ROLE VERBATIM (the passive-alternation mapping is reused unmodified).
    """
    toks, pos, heads, labs, lemmas = parse
    n = len(toks)
    match_positions = [i for i in range(1, n + 1) if lemmas[i - 1] == target_lemma]
    if not match_positions:
        return [], None
    case_of: Dict[int, str] = {}
    for i in range(1, n + 1):
        if labs.get(i) == "case":
            h = heads.get(i, 0)
            if h and h not in case_of:
                case_of[h] = toks[i - 1].lower()
    events: List[Tuple[str, str, str]] = []
    slot: Optional[Tuple[str, str]] = None
    dependents_of: Dict[int, List[int]] = collections.defaultdict(list)
    for j in range(1, n + 1):
        h = heads.get(j, 0)
        if h:
            dependents_of[h].append(j)
    for i in match_positions:
        h = heads.get(i, 0)
        if h and 1 <= h <= n:
            rel = labs.get(i)
            nb = lemmas[h - 1]
            if rel and len(nb) >= SPE.MIN_LEMMA_LEN and nb.isalpha():
                events.append((nb, rel, "up"))
            if slot is None and rel and pos[h - 1] == "VERB":
                if rel in SPE.CORE_ROLE:
                    slot = (lemmas[h - 1], SPE.CORE_ROLE[rel])
                elif rel == SPE.OBL_ROLE:
                    prep = case_of.get(i)
                    if prep and prep.isalpha():
                        slot = (lemmas[h - 1], "obl:" + prep)
        for j in dependents_of.get(i, []):
            rel_j = labs.get(j)
            nb = lemmas[j - 1]
            if rel_j and len(nb) >= SPE.MIN_LEMMA_LEN and nb.isalpha():
                events.append((nb, rel_j, "down"))
    return events, slot


def build_occurrence_data(words_needed: Sequence[str], buckets: Dict[str, List[int]],
                          sents: List[str], tg, pr, lb, out_dir_ckpt: str, grid: str
                          ) -> Dict[str, List[Dict]]:
    """{word: [ {sent_idx, arc_events, slot, bag_counts}, ... ]}, one record per PROFILE occurrence,
    checkpointed PER WORD so a kill loses at most one word's build."""
    out: Dict[str, List[Dict]] = {}
    parse_cache: Dict[int, object] = {}
    done = load_units(out_dir_ckpt)
    t0 = time.time()
    n_built = n_reused = 0
    for k, w in enumerate(words_needed):
        key = unit_key("OCC", UPSTREAM_VERSION, grid, w)
        rec = done.get(key)
        if rec is not None:
            out[w] = rec["occurrences"]
            n_reused += 1
        else:
            occ = buckets.get(w, [])
            prof = occ[:C3._n_profile(len(occ))]
            recs: List[Dict] = []
            for si in prof:
                parse = parse_cache.get(si, "MISS")
                if parse == "MISS":
                    parse = parse_sentence(tg, pr, lb, sents[si])
                    parse_cache[si] = parse
                bag = dict(INFO.raw_counts_for_window(sents[si], w))
                if parse is None:
                    events, slot = [], None
                else:
                    events, slot = occurrence_features(parse, w)
                recs.append({"sent_idx": int(si), "arc_events": [list(e) for e in events],
                            "slot": list(slot) if slot is not None else None,
                            "bag_counts": bag})
            out[w] = recs
            record_unit(out_dir_ckpt, key, {"occurrences": recs})
            n_built += 1
        if (k + 1) % 100 == 0 or k == len(words_needed) - 1:
            print("[occdata] %d/%d words built=%d reused=%d parse_cache=%d elapsed=%.0fs" % (
                k + 1, len(words_needed), n_built, n_reused, len(parse_cache),
                time.time() - t0), flush=True)
    return out


def compute_deltas(occ_data: Dict[str, List[Dict]], filler_counts: Dict[Tuple[str, str], Dict[str, int]],
                   totals: Dict[Tuple[str, str], int]) -> Dict[str, List[float]]:
    """delta per occurrence, in the SAME order as occ_data[w] -- see S1 ALGEBRA in the module
    docstring. No slot info on an occurrence -> delta=1.0 (unmodulated full write)."""
    out: Dict[str, List[float]] = {}
    for w, recs in occ_data.items():
        deltas = []
        for rec in recs:
            slot = rec["slot"]
            if slot is None:
                deltas.append(1.0)
                continue
            vr = tuple(slot)
            total = totals.get(vr, 0)
            if total <= 0:
                deltas.append(1.0)
                continue
            prior = filler_counts.get(vr, {}).get(w, 0)
            share = prior / total
            deltas.append(1.0 - 2.0 * share)
        out[w] = deltas
    return out


# =================================================================================================
# STORE CONSTRUCTION -- U1/U3 from flat arc-event lists (so N1/N2/N6 can transform the SAME flat
# list before rebuilding); S1/N3 from flat (word, delta, bag) triples.
# =================================================================================================
def flatten_arc_events(occ_data: Dict[str, List[Dict]], target_words: Sequence[str]
                       ) -> List[List[str]]:
    out: List[List[str]] = []
    for w in target_words:
        for rec in occ_data.get(w, []):
            for nb, rel, direction in rec["arc_events"]:
                out.append([w, nb, rel, direction])
    return out


_ARC_KEY_MODES = ("typed", "role_only", "neighbour_only")


def store_from_arc_events(arc_events: List[List[str]], target_words: Sequence[str],
                          mode: str = "typed") -> Tuple[Dict[str, np.ndarray], Dict]:
    """mode="typed" -> U1 (neighbour, relation, direction). mode="role_only" -> U3 (relation,
    direction only, neighbour dropped -- ceiling on how much the role distribution alone carries).
    mode="neighbour_only" -> T2_UNTYPED_SAME_COVERAGE (neighbour identity only, relation/direction
    STRIPPED, SAME arc-connected words/coverage as U1 by construction since it consumes the
    identical `arc_events` list) -- decides whether the TYPE (label) carries information beyond mere
    WORD SELECTION, the original brief's own framing, distinct from U3 which asks the opposite
    question (does the label alone carry anything without the neighbour)."""
    if mode not in _ARC_KEY_MODES:
        raise ValueError("unknown mode %r, must be one of %r" % (mode, _ARC_KEY_MODES))
    acc: Dict[str, collections.Counter] = {w: collections.Counter() for w in target_words}
    for owner, nb, rel, direction in arc_events:
        if mode == "typed":
            key = "%s|%s|%s" % (nb, rel, direction)
        elif mode == "role_only":
            key = "%s|%s" % (rel, direction)
        else:
            key = nb
        acc[owner][key] += 1
    plain = {w: dict(c) for w, c in acc.items()}
    vocab = INFO.build_vocab([plain])
    if not vocab:
        return {w: np.zeros(1, dtype=np.float32) for w in target_words}, {
            "n_arc_events": len(arc_events), "vocab_size": 0, "mode": mode}
    M = INFO.to_sparse(plain, list(target_words), vocab)
    Mn = INFO.l2n_sparse(M)
    dense = np.asarray(Mn.todense(), dtype=np.float32)
    store = {w: dense[i] for i, w in enumerate(target_words)}
    return store, {"n_arc_events": len(arc_events), "vocab_size": len(vocab), "mode": mode}


def build_bag_store(occ_data: Dict[str, List[Dict]], target_words: Sequence[str]
                    ) -> Tuple[Dict[str, np.ndarray], Dict]:
    """The plain bag-of-words channel, built from THIS cell's own occ_data (delta=1.0 uniformly, i.e.
    store_from_s1 with no signed weighting) -- the SAME per-occurrence bag_counts A0 was built from,
    used here only as T3_COMBINED's second channel (never as a substitute for the reused, regression-
    gated A0_INCUMBENT score, which stays DSI's cached RAW_COUNT_FULL_ACCUM throughout)."""
    ones = {w: [1.0] * len(occ_data.get(w, [])) for w in target_words}
    return store_from_s1(occ_data, ones, target_words)


def combine_l2(store_a: Dict[str, np.ndarray], store_b: Dict[str, np.ndarray],
              target_words: Sequence[str]) -> Dict[str, np.ndarray]:
    """Komninos & Manandhar 2016 combination: concatenate two ALREADY L2-normalised channels, then
    L2-renormalise the concatenation. Reused DESIGN from `exp_dependency_context_codebook_location_
    artifact_v1.py`'s `combined_emb = _l2norm_rows(np.concatenate([window_emb, dep_emb], axis=1))`
    (same idea, independently implemented per-word here since that cell operates on dense matrices
    and this one on a {word: vector} dict store)."""
    out: Dict[str, np.ndarray] = {}
    for w in target_words:
        cat = np.concatenate([np.asarray(store_a[w], dtype=np.float64),
                              np.asarray(store_b[w], dtype=np.float64)])
        n = float(np.linalg.norm(cat))
        out[w] = (cat / n if n > 1e-12 else cat).astype(np.float32)
    return out


def permute_labels(arc_events: List[List[str]], seed: int) -> List[List[str]]:
    """N1_LABEL_PERMUTED: same owner/neighbour pairing, LABEL marginal preserved exactly (a true
    permutation, not an iid resample), correspondence between neighbour and role destroyed."""
    rng = np.random.default_rng(seed)
    labels = [(e[2], e[3]) for e in arc_events]
    idx = rng.permutation(len(labels))
    out = []
    for j, e in enumerate(arc_events):
        rel, direction = labels[idx[j]]
        out.append([e[0], e[1], rel, direction])
    return out


def random_typing(arc_events: List[List[str]], seed: int) -> List[List[str]]:
    """N2_RANDOM_TYPING: each arc gets an IID uniform draw from the K distinct labels seen (marginal
    NOT preserved -- destroys all syntactic content, including the true label frequency)."""
    rng = np.random.default_rng(seed)
    distinct = sorted(set((e[2], e[3]) for e in arc_events))
    if not distinct:
        return [list(e) for e in arc_events]
    choice = rng.integers(0, len(distinct), size=len(arc_events))
    out = []
    for j, e in enumerate(arc_events):
        rel, direction = distinct[int(choice[j])]
        out.append([e[0], e[1], rel, direction])
    return out


def corrupt_neighbors(arc_events: List[List[str]], p: float, seed: int) -> List[List[str]]:
    """N6_PARSE_NOISE: with probability p, replace an arc's NEIGHBOUR identity with a uniformly
    drawn neighbour from the same global pool -- a cheap, disclosed approximation of re-parsing under
    a corrupted parser (avoids a third full parse pass); labels/owners untouched."""
    if p <= 0.0 or not arc_events:
        return [list(e) for e in arc_events]
    rng = np.random.default_rng(seed)
    pool = [e[1] for e in arc_events]
    flips = rng.random(len(arc_events)) < p
    draws = rng.integers(0, len(pool), size=len(arc_events))
    out = []
    for j, e in enumerate(arc_events):
        if flips[j]:
            out.append([e[0], pool[int(draws[j])], e[2], e[3]])
        else:
            out.append(list(e))
    return out


def store_from_s1(occ_data: Dict[str, List[Dict]], deltas: Dict[str, List[float]],
                  target_words: Sequence[str]) -> Tuple[Dict[str, np.ndarray], Dict]:
    acc: Dict[str, Dict[str, float]] = {w: collections.defaultdict(float) for w in target_words}
    n_occ = 0
    for w in target_words:
        recs = occ_data.get(w, [])
        dl = deltas.get(w, [])
        for rec, d in zip(recs, dl):
            for surface, c in rec["bag_counts"].items():
                acc[w][surface] += d * c
            n_occ += 1
    plain = {w: dict(c) for w, c in acc.items()}
    vocab = INFO.build_vocab([plain])
    if not vocab:
        return {w: np.zeros(1, dtype=np.float32) for w in target_words}, {"n_occurrences": n_occ,
                                                                           "vocab_size": 0}
    M = INFO.to_sparse(plain, list(target_words), vocab)
    Mn = INFO.l2n_sparse(M)
    dense = np.asarray(Mn.todense(), dtype=np.float32)
    return {w: dense[i] for i, w in enumerate(target_words)}, {"n_occurrences": n_occ,
                                                                "vocab_size": len(vocab)}


def store_from_s1_permuted_magnitude(occ_data: Dict[str, List[Dict]], deltas: Dict[str, List[float]],
                                     target_words: Sequence[str], seed: int
                                    ) -> Tuple[Dict[str, np.ndarray], Dict]:
    """N3_MAGNITUDE_PERMUTED: flatten ALL (word, delta, bag) triples across target_words, permute the
    DELTA values only (same full magnitude distribution, same 100% write rate, same bag/word pairing)
    -- decorrelates which occurrence gets which magnitude."""
    flat_owner: List[str] = []
    flat_bag: List[Dict[str, int]] = []
    flat_delta: List[float] = []
    for w in target_words:
        recs = occ_data.get(w, [])
        dl = deltas.get(w, [])
        for rec, d in zip(recs, dl):
            flat_owner.append(w)
            flat_bag.append(rec["bag_counts"])
            flat_delta.append(d)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(flat_delta))
    shuffled = [flat_delta[i] for i in idx]
    acc: Dict[str, Dict[str, float]] = {w: collections.defaultdict(float) for w in target_words}
    for owner, bag, d in zip(flat_owner, flat_bag, shuffled):
        for surface, c in bag.items():
            acc[owner][surface] += d * c
    plain = {w: dict(c) for w, c in acc.items()}
    vocab = INFO.build_vocab([plain])
    if not vocab:
        return {w: np.zeros(1, dtype=np.float32) for w in target_words}, {"n_occurrences": len(flat_delta)}
    M = INFO.to_sparse(plain, list(target_words), vocab)
    Mn = INFO.l2n_sparse(M)
    dense = np.asarray(Mn.todense(), dtype=np.float32)
    return {w: dense[i] for i, w in enumerate(target_words)}, {"n_occurrences": len(flat_delta),
                                                                "vocab_size": len(vocab)}


def dsi_score(store: Dict[str, np.ndarray], matchedP, matchedS) -> Dict[str, np.ndarray]:
    return {"P": DSI.dense_scores_from_dict_store(store, matchedP),
           "S": DSI.dense_scores_from_dict_store(store, matchedS)}


def band_vs_bar(auc: float, ci: List[float], bar: float) -> str:
    if ci[0] > bar:
        return "ABOVE_BAR"
    if ci[1] < bar:
        return "BELOW_BAR"
    return "NOT_SEPARATED_FROM_BAR"


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- real front-end loads and recovers the owner's own known-answer parse (same fixture
    # selectional_preference_extractor_v1's own self-test uses, verified independently here) --------
    tg, lb, pr = SPE._load_frontend()
    parse = parse_sentence(tg, pr, lb, "The tove ran across the road .")
    assert parse is not None, "owner-sentence fixture must parse"
    events_tove, slot_tove = occurrence_features(parse, "tove")
    assert slot_tove == ("run", "SUBJ"), "tove must fill run/SUBJ: %r" % (slot_tove,)
    events_road, slot_road = occurrence_features(parse, "road")
    assert slot_road is not None and slot_road[0] == "run" and slot_road[1].startswith("obl:"), \
        "road must fill a run/obl:* slot: %r" % (slot_road,)
    ev["owner_sentence_slot_recovery"] = {"tove": slot_tove, "road": slot_road}

    # --- global slot distribution, real code path, tiny corpus with a repeated slot ---------------
    # FRESH, uniquely-named scratch path EVERY invocation (pid + monotonic ns) -- structurally
    # impossible to resume a stale checkpoint from a prior self-test run. Per the coordinator's
    # 2026-08-18 correction: a FIXED scratch path let a resumed self-test load a checkpoint written
    # by an earlier version of this file without the difference being visible; a fresh path removes
    # the hazard entirely rather than relying on a version bump discipline for a throwaway fixture.
    tiny_sents = ["the dog ran across the road .", "a rabbit ran across the road .",
                 "the deer ran across the road .", "the dog is an animal ."]
    norms_tiny = {"dog", "rabbit", "deer", "road", "animal", "run"}
    scratch_dir = os.path.join(REPO, "data", "%s_selftest_scratch_%d_%d" % (
        ANCHOR_NAME, os.getpid(), time.time_ns()))
    dist = build_global_slot_distribution(tiny_sents, norms_tiny, scratch_dir, "selftest",
                                          n_workers=1)
    fc, tot = slot_lookup_tables(dist)
    assert ("run", "SUBJ") in fc, "run/SUBJ must appear in the tiny corpus slot dist: %r" % sorted(fc)
    assert set(fc[("run", "SUBJ")]) == {"dog", "rabbit", "deer"}, \
        "run/SUBJ fillers wrong: %r" % fc[("run", "SUBJ")]
    ev["slot_dist_known_answer"] = {"run/SUBJ": fc[("run", "SUBJ")], "total": tot[("run", "SUBJ")]}

    # --- delta known-answer: a filler that is the ONLY thing ever seen in a slot must be discounted
    # to exactly -1.0; a filler at exactly half the slot mass must be exactly 0.0 --------------------
    fc2 = {("v", "SUBJ"): {"only": 4}}
    tot2 = {("v", "SUBJ"): 4}
    occ = {"only": [{"slot": ["v", "SUBJ"], "arc_events": [], "bag_counts": {}, "sent_idx": 0}]}
    dl = compute_deltas(occ, fc2, tot2)
    assert abs(dl["only"][0] - (-1.0)) < 1e-9, "an always-only filler must be discounted to -1.0: %r" % dl
    fc3 = {("v", "OBJ"): {"half": 2, "other": 2}}
    tot3 = {("v", "OBJ"): 4}
    occ3 = {"half": [{"slot": ["v", "OBJ"], "arc_events": [], "bag_counts": {}, "sent_idx": 0}]}
    dl3 = compute_deltas(occ3, fc3, tot3)
    assert abs(dl3["half"][0] - 0.0) < 1e-9, "a half-share filler must be neutral (delta=0): %r" % dl3
    occ4 = {"novel": [{"slot": None, "arc_events": [], "bag_counts": {}, "sent_idx": 0}]}
    dl4 = compute_deltas(occ4, {}, {})
    assert abs(dl4["novel"][0] - 1.0) < 1e-9, "no slot info must default to full-strength write: %r" % dl4
    ev["delta_known_answers"] = {"only": dl["only"][0], "half": dl3["half"][0], "no_slot": dl4["novel"][0]}

    # --- store construction: U1 must distinguish "a" and "b" (different neighbour identity, SAME
    # role); U3 must COLLAPSE them (role_only drops the neighbour, leaving only one role column) --
    # -- this is the concrete claim behind STOP-IF 3 (U1~U3 => POS-profile in disguise) ---------------
    fake_events = [["a", "verb1", "SUBJ", "up"], ["a", "verb1", "SUBJ", "up"],
                  ["b", "verb2", "SUBJ", "up"], ["b", "verb2", "SUBJ", "up"]]
    store_u1, diag_u1 = store_from_arc_events(fake_events, ["a", "b"], mode="typed")
    store_u3, diag_u3 = store_from_arc_events(fake_events, ["a", "b"], mode="role_only")
    assert not np.allclose(store_u1["a"], store_u1["b"]), \
        "U1 must distinguish two words with different neighbour identity: %r vs %r" % (
            store_u1["a"], store_u1["b"])
    assert np.allclose(store_u3["a"], store_u3["b"]), \
        "U3 (role-only) must COLLAPSE two words sharing one role to the identical row: %r vs %r" % (
            store_u3["a"], store_u3["b"])
    ev["u1_u3_differ"] = {"u1_vocab": diag_u1["vocab_size"], "u3_vocab": diag_u3["vocab_size"],
                          "u1_a_vs_b_differ": bool(not np.allclose(store_u1["a"], store_u1["b"])),
                          "u3_a_vs_b_collapse": bool(np.allclose(store_u3["a"], store_u3["b"]))}

    # --- T2_UNTYPED_SAME_COVERAGE: neighbour identity kept (so "a" vs "b" still distinguished, same
    # as U1) but the LABEL dropped -- must have a SMALLER-OR-EQUAL vocab than U1 (fewer distinct
    # (neighbour) keys than (neighbour,relation,direction) keys) while still separating a/b ----------
    store_t2, diag_t2 = store_from_arc_events(fake_events, ["a", "b"], mode="neighbour_only")
    assert not np.allclose(store_t2["a"], store_t2["b"]), \
        "T2 must still distinguish a/b on neighbour identity alone: %r vs %r" % (
            store_t2["a"], store_t2["b"])
    assert diag_t2["vocab_size"] <= diag_u1["vocab_size"], \
        "T2 (neighbour-only) vocab must be <= U1's (typed) vocab: %r vs %r" % (
            diag_t2["vocab_size"], diag_u1["vocab_size"])
    ev["t2_untyped_same_coverage"] = {"t2_vocab": diag_t2["vocab_size"],
                                      "t2_a_vs_b_differ": bool(not np.allclose(store_t2["a"], store_t2["b"]))}

    # --- T3_COMBINED (Komninos & Manandhar 2016 pattern): concatenate two ALREADY-normalised unit
    # rows and re-normalise -- resulting row must itself be unit-norm, and must NOT equal either
    # input channel alone (genuinely a third representation, not an alias of one channel) -----------
    fake_occ = {"a": [{"slot": None, "arc_events": [], "bag_counts": {"bagword": 3}, "sent_idx": 0}],
               "b": [{"slot": None, "arc_events": [], "bag_counts": {"bagword": 1, "other": 2}, "sent_idx": 1}]}
    store_bag_fixture, _diag_bag = build_bag_store(fake_occ, ["a", "b"])
    store_t3_fixture = combine_l2(store_bag_fixture, store_u1, ["a", "b"])
    for w in ("a", "b"):
        norm_w = float(np.linalg.norm(store_t3_fixture[w]))
        assert abs(norm_w - 1.0) < 1e-6, "T3 combined row must be unit-norm: word=%r norm=%.6f" % (w, norm_w)
        assert store_t3_fixture[w].shape[0] == store_bag_fixture[w].shape[0] + store_u1[w].shape[0], \
            "T3 combined row must have the concatenated shape"
    ev["t3_combined_known_answer"] = {"a_norm": float(np.linalg.norm(store_t3_fixture["a"])),
                                      "shape": int(store_t3_fixture["a"].shape[0])}

    permuted = permute_labels(fake_events, seed=0)
    orig_labels = sorted((e[2], e[3]) for e in fake_events)
    perm_labels = sorted((e[2], e[3]) for e in permuted)
    assert orig_labels == perm_labels, "label MULTISET must be preserved exactly under permutation"
    orig_pairs = set((e[0], e[1], e[2], e[3]) for e in fake_events)
    perm_pairs = set((e[0], e[1], e[2], e[3]) for e in permuted)
    ev["label_permute_marginal_preserved"] = {"orig_labels": orig_labels, "perm_labels": perm_labels,
                                              "pairing_changed": orig_pairs != perm_pairs}

    corrupted = corrupt_neighbors(fake_events, p=1.0, seed=0)
    assert all(e[0] == f[0] and e[2] == f[2] and e[3] == f[3]
              for e, f in zip(corrupted, fake_events)), \
        "corruption must only ever touch the neighbour field"
    ev["corrupt_neighbors_field_scoped"] = True

    # --- S1 store: a positive-delta occurrence and a negative-delta occurrence must move the store
    # in OPPOSITE directions on the same bag, proving the sign is load-bearing, not just magnitude ---
    occ_s1 = {"w": [{"slot": None, "arc_events": [], "bag_counts": {"ctx": 5}, "sent_idx": 0}]}
    dl_pos = {"w": [1.0]}
    dl_neg = {"w": [-1.0]}
    s_pos, _ = store_from_s1(occ_s1, dl_pos, ["w"])
    s_neg, _ = store_from_s1(occ_s1, dl_neg, ["w"])
    assert float(np.dot(s_pos["w"], s_neg["w"])) < 0.0, \
        "opposite-sign deltas on the identical occurrence must anti-correlate: %r %r" % (
            s_pos["w"], s_neg["w"])
    ev["s1_sign_is_load_bearing"] = {"dot": float(np.dot(s_pos["w"], s_neg["w"]))}

    # --- N3 magnitude-permute known answer: the MULTISET of deltas actually applied must be
    # unchanged (only the owner assignment differs) -------------------------------------------------
    occ_n3 = {"w1": [{"slot": None, "arc_events": [], "bag_counts": {"x": 1}, "sent_idx": 0}],
             "w2": [{"slot": None, "arc_events": [], "bag_counts": {"x": 1}, "sent_idx": 0}]}
    dl_n3 = {"w1": [1.0], "w2": [-1.0]}
    _s_n3, diag_n3 = store_from_s1_permuted_magnitude(occ_n3, dl_n3, ["w1", "w2"], seed=1)
    assert diag_n3["n_occurrences"] == 2, "N3 must preserve total occurrence count: %r" % diag_n3
    ev["n3_occurrence_count_preserved"] = diag_n3["n_occurrences"]

    # --- band_vs_bar known answers ------------------------------------------------------------------
    assert band_vs_bar(0.60, [0.55, 0.65], 0.5431) == "ABOVE_BAR"
    assert band_vs_bar(0.40, [0.35, 0.45], 0.5431) == "BELOW_BAR"
    assert band_vs_bar(0.55, [0.50, 0.60], 0.5431) == "NOT_SEPARATED_FROM_BAR"
    ev["band_vs_bar_known_answers"] = True

    # --- arms-must-differ digest sensitivity --------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr), "distinct score vectors must produce distinct digests"
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip ----------------------------------------------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    # --- DSI regression gate is reachable and reusable (does NOT re-run the full gate here -- that
    # happens once for real in run(); this just proves the import/function exist and are callable) --
    assert callable(PCWG.dsi_regression_gate), "PCWG.dsi_regression_gate must be importable/callable"
    assert callable(PCWG.auc_margin_paired), "PCWG.auc_margin_paired must be importable/callable"
    ev["reused_functions_importable"] = True

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "NO_PRETRAINED_TABLE_IMPORTED": True, "BAR_MAX_FLOOR_AUC": None}

    # =============================== STOP-IF 1: LICENCE, checked first, reused verbatim ==============
    gate = PCWG.dsi_regression_gate()
    rep["DSI_REGRESSION_GATE"] = gate["gate_report"]
    matchedP, matchedS = gate["matchedP"], gate["matchedS"]
    if grid == "reduced":
        matchedP, matchedS = matchedP[:40], matchedS[:40]
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match
    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    rep["N_WORDS_NEEDED"] = len(words_needed)

    bar = gate["gate_report"]["recomputed_AUC_PER_ARM"]["F_CONSTANT_PROTOTYPE"]["auc"]
    rep["BAR_MAX_FLOOR_AUC"] = bar
    print("[gate] BAR (max floor, F_CONSTANT_PROTOTYPE) = %.4f -- this is the bar, NOT 0.5" % bar,
         flush=True)

    # =============================== reused floors / K1 / N0 / A0 (never rebuilt) ====================
    floor_res: Dict[str, Dict] = {}
    for name in FLOOR_NAMES + ["KNOWN_ANSWER_WORDNET_PATH_SIM", "RANDOM_VECTOR_STORE",
                               "RAW_COUNT_FULL_ACCUM"]:
        sc = gate["arm_scores"][name]
        floor_res[name] = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, MASTER_SEED + 1000 + hash(name) % 1000)
    rep["REUSED_ARMS"] = floor_res
    a0_scores = {"P": gate["arm_scores"]["RAW_COUNT_FULL_ACCUM"]["P"],
                "S": gate["arm_scores"]["RAW_COUNT_FULL_ACCUM"]["S"]}
    if grid == "reduced":
        a0_scores = {"P": a0_scores["P"][:40], "S": a0_scores["S"][:40]}
    a0_auc = DSI.auc_bootstrap(a0_scores["P"], a0_scores["S"], N_BOOT, MASTER_SEED + 2)
    rep["A0_INCUMBENT"] = a0_auc
    print("[a0] A0_INCUMBENT (reused RAW_COUNT_FULL_ACCUM) AUC=%.4f CI=%r" % (
        a0_auc["auc"], a0_auc["ci95"]), flush=True)

    # =============================== corpus (reused, never rebuilt) ==================================
    sents, buckets, _counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    rep["n_corpus_sentences"] = len(sents)
    print("[corpus] n_sentences=%d" % len(sents), flush=True)

    C = CTS.load_cache()
    anchors_all = [a for a, ok in zip(C["anchors"], np.asarray(C["mat_ok"], bool)) if ok]
    norms = set(anchors_all) | set(words_needed)
    print("[norms] |norms|=%d (CTS anchor set union words_needed; NOT GS._table())" % len(norms),
         flush=True)

    # =============================== STEP A: global slot distribution (checkpointed) =================
    slot_dist = build_global_slot_distribution(sents, norms, out_dir_ckpt, grid)
    rep["GLOBAL_SLOT_DISTRIBUTION_STATS"] = {k: v for k, v in slot_dist.items() if k != "slot_filler"}
    filler_counts, totals = slot_lookup_tables(slot_dist)

    # =============================== STEP B: per-word occurrence data (checkpointed per word) ========
    tg, lb, pr = SPE._load_frontend()
    occ_data = build_occurrence_data(words_needed, buckets, sents, tg, pr, lb, out_dir_ckpt, grid)
    n_occ_total = sum(len(v) for v in occ_data.values())
    n_with_slot = sum(1 for recs in occ_data.values() for r in recs if r["slot"] is not None)
    n_parsed_fail = sum(1 for recs in occ_data.values() for r in recs
                        if not r["arc_events"] and r["slot"] is None and not r["bag_counts"])
    rep["OCCURRENCE_DATA_STATS"] = {"n_words": len(occ_data), "n_occurrences_total": n_occ_total,
                                    "n_occurrences_with_slot": n_with_slot,
                                    "frac_with_slot": round(n_with_slot / max(1, n_occ_total), 4)}
    print("[occdata] n_occurrences=%d n_with_slot=%d frac=%.4f" % (
        n_occ_total, n_with_slot, rep["OCCURRENCE_DATA_STATS"]["frac_with_slot"]), flush=True)

    deltas = compute_deltas(occ_data, filler_counts, totals)

    # =============================== coverage diagnostics (for N5) ===================================
    n_arc_by_word = {w: sum(len(r["arc_events"]) for r in occ_data.get(w, [])) for w in words_needed}
    n_slot_by_word = {w: sum(1 for r in occ_data.get(w, []) if r["slot"] is not None)
                      for w in words_needed}
    rep["COVERAGE_MIN"] = COVERAGE_MIN

    def coverage_matched_pairs(pairs, cov_of):
        return [p for p in pairs if cov_of.get(p[0], 0) >= COVERAGE_MIN
               and cov_of.get(p[1], 0) >= COVERAGE_MIN]

    matchedP_cov_u1 = coverage_matched_pairs(matchedP, n_arc_by_word)
    matchedS_cov_u1 = coverage_matched_pairs(matchedS, n_arc_by_word)
    matchedP_cov_s1 = coverage_matched_pairs(matchedP, n_slot_by_word)
    matchedS_cov_s1 = coverage_matched_pairs(matchedS, n_slot_by_word)
    rep["N5_COVERAGE_MATCHED_N"] = {
        "u1_before": {"P": len(matchedP), "S": len(matchedS)},
        "u1_after": {"P": len(matchedP_cov_u1), "S": len(matchedS_cov_u1)},
        "s1_before": {"P": len(matchedP), "S": len(matchedS)},
        "s1_after": {"P": len(matchedP_cov_s1), "S": len(matchedS_cov_s1)},
    }
    print("[coverage] N5 n before/after: U1 P=%d->%d S=%d->%d | S1 P=%d->%d S=%d->%d" % (
        len(matchedP), len(matchedP_cov_u1), len(matchedS), len(matchedS_cov_u1),
        len(matchedP), len(matchedP_cov_s1), len(matchedS), len(matchedS_cov_s1)), flush=True)

    # =============================== ARM CONSTRUCTION =================================================
    arc_events = flatten_arc_events(occ_data, words_needed)
    rep["N_ARC_EVENTS_TOTAL"] = len(arc_events)

    arm_scores: Dict[str, Dict[str, np.ndarray]] = {}
    arm_diags: Dict[str, Dict] = {}

    def score_it(name: str, store: Dict[str, np.ndarray], diag: Dict, mP=None, mS=None) -> None:
        mP = matchedP if mP is None else mP
        mS = matchedS if mS is None else mS
        sc = dsi_score(store, mP, mS)
        arm_scores[name] = sc
        arm_diags[name] = diag

    store_u1, diag_u1 = store_from_arc_events(arc_events, words_needed, mode="typed")
    score_it("U1_TYPED_CONTEXT", store_u1, diag_u1)

    store_u3, diag_u3 = store_from_arc_events(arc_events, words_needed, mode="role_only")
    score_it("U3_ROLE_ONLY", store_u3, diag_u3)

    store_t2, diag_t2 = store_from_arc_events(arc_events, words_needed, mode="neighbour_only")
    score_it("T2_UNTYPED_SAME_COVERAGE", store_t2, diag_t2)

    store_bag, diag_bag = build_bag_store(occ_data, words_needed)
    store_t3 = combine_l2(store_bag, store_u1, words_needed)
    score_it("T3_COMBINED", store_t3, {"channel_a": "bag_this_cells_own_occ_data",
                                       "channel_b": "U1_TYPED_CONTEXT", "channel_a_diag": diag_bag})

    n1_events = permute_labels(arc_events, seed=MASTER_SEED + 501)
    store_n1, diag_n1 = store_from_arc_events(n1_events, words_needed, mode="typed")
    score_it("N1_LABEL_PERMUTED", store_n1, diag_n1)

    n2_events = random_typing(arc_events, seed=MASTER_SEED + 502)
    store_n2, diag_n2 = store_from_arc_events(n2_events, words_needed, mode="typed")
    score_it("N2_RANDOM_TYPING", store_n2, diag_n2)

    store_s1, diag_s1 = store_from_s1(occ_data, deltas, words_needed)
    score_it("S1_SLOT_COMPETITION", store_s1, diag_s1)

    store_n3, diag_n3 = store_from_s1_permuted_magnitude(occ_data, deltas, words_needed,
                                                          seed=MASTER_SEED + 503)
    score_it("N3_MAGNITUDE_PERMUTED", store_n3, diag_n3)

    n5_scores: Dict[str, Dict] = {}
    if len(matchedP_cov_u1) >= 10 and len(matchedS_cov_u1) >= 10:
        n5_scores["U1_COVERAGE_MATCHED"] = dsi_score(store_u1, matchedP_cov_u1, matchedS_cov_u1)
    if len(matchedP_cov_s1) >= 10 and len(matchedS_cov_s1) >= 10:
        n5_scores["S1_COVERAGE_MATCHED"] = dsi_score(store_s1, matchedP_cov_s1, matchedS_cov_s1)

    n6_results: Dict[str, Dict] = {}
    for pi, p in enumerate(CORRUPT_FRACS):
        ev_c = corrupt_neighbors(arc_events, p, seed=MASTER_SEED + 600 + pi)
        store_c, _diag_c = store_from_arc_events(ev_c, words_needed, mode="typed")
        sc_c = dsi_score(store_c, matchedP, matchedS)
        n6_results["p%.2f" % p] = DSI.auc_bootstrap(sc_c["P"], sc_c["S"], N_BOOT, MASTER_SEED + 700 + pi)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores.items()}
    digests["A0_INCUMBENT"] = _digest(np.concatenate([a0_scores["P"], a0_scores["S"]]))
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC per arm ======================================================
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(arm_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, MASTER_SEED + 8181 + i)
        res["band_vs_bar"] = band_vs_bar(res["auc"], res["ci95"], bar)
        auc_results[name] = res
        print("[auc] %-24s AUC=%.4f CI=%r band=%s band_vs_bar=%s" % (
            name, res["auc"], res["ci95"], res["band"], res["band_vs_bar"]), flush=True)
    for name, sc in n5_scores.items():
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, MASTER_SEED + 8300)
        res["band_vs_bar"] = band_vs_bar(res["auc"], res["ci95"], bar)
        auc_results[name] = res
        print("[auc] %-24s AUC=%.4f CI=%r (coverage-matched)" % (name, res["auc"], res["ci95"]), flush=True)
    rep["AUC_PER_ARM"] = auc_results
    rep["N6_PARSE_NOISE_SWEEP"] = n6_results
    rep["ARM_DIAGS"] = arm_diags
    rep["UAS_CITED_NOT_RECOMPUTED"] = {"source": UAS_SOURCE, "value": UAS_CITED}

    # =============================== paired margins (the decisive comparisons) =======================
    margins: Dict[str, Dict] = {}
    margins["U1_vs_N1"] = PCWG.auc_margin_paired(
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"],
        arm_scores["N1_LABEL_PERMUTED"]["P"], arm_scores["N1_LABEL_PERMUTED"]["S"], N_BOOT, MASTER_SEED + 40)
    margins["U1_vs_N2"] = PCWG.auc_margin_paired(
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"],
        arm_scores["N2_RANDOM_TYPING"]["P"], arm_scores["N2_RANDOM_TYPING"]["S"], N_BOOT, MASTER_SEED + 41)
    margins["U1_vs_U3"] = PCWG.auc_margin_paired(
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"],
        arm_scores["U3_ROLE_ONLY"]["P"], arm_scores["U3_ROLE_ONLY"]["S"], N_BOOT, MASTER_SEED + 42)
    margins["U1_vs_A0"] = PCWG.auc_margin_paired(
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"],
        a0_scores["P"], a0_scores["S"], N_BOOT, MASTER_SEED + 43)
    margins["U1_vs_T2"] = PCWG.auc_margin_paired(
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"],
        arm_scores["T2_UNTYPED_SAME_COVERAGE"]["P"], arm_scores["T2_UNTYPED_SAME_COVERAGE"]["S"],
        N_BOOT, MASTER_SEED + 46)
    margins["T2_vs_A0"] = PCWG.auc_margin_paired(
        arm_scores["T2_UNTYPED_SAME_COVERAGE"]["P"], arm_scores["T2_UNTYPED_SAME_COVERAGE"]["S"],
        a0_scores["P"], a0_scores["S"], N_BOOT, MASTER_SEED + 47)
    margins["T3_vs_U1"] = PCWG.auc_margin_paired(
        arm_scores["T3_COMBINED"]["P"], arm_scores["T3_COMBINED"]["S"],
        arm_scores["U1_TYPED_CONTEXT"]["P"], arm_scores["U1_TYPED_CONTEXT"]["S"], N_BOOT, MASTER_SEED + 48)
    margins["T3_vs_A0"] = PCWG.auc_margin_paired(
        arm_scores["T3_COMBINED"]["P"], arm_scores["T3_COMBINED"]["S"],
        a0_scores["P"], a0_scores["S"], N_BOOT, MASTER_SEED + 49)
    margins["S1_vs_N3"] = PCWG.auc_margin_paired(
        arm_scores["S1_SLOT_COMPETITION"]["P"], arm_scores["S1_SLOT_COMPETITION"]["S"],
        arm_scores["N3_MAGNITUDE_PERMUTED"]["P"], arm_scores["N3_MAGNITUDE_PERMUTED"]["S"], N_BOOT,
        MASTER_SEED + 44)
    margins["S1_vs_A0"] = PCWG.auc_margin_paired(
        arm_scores["S1_SLOT_COMPETITION"]["P"], arm_scores["S1_SLOT_COMPETITION"]["S"],
        a0_scores["P"], a0_scores["S"], N_BOOT, MASTER_SEED + 45)
    rep["PAIRED_MARGINS"] = margins

    # =============================== STOP-IF interpretation (drill sec 6.4) ==========================
    u1 = auc_results["U1_TYPED_CONTEXT"]
    u3 = auc_results["U3_ROLE_ONLY"]
    s1 = auc_results["S1_SLOT_COMPETITION"]
    findings: List[str] = []

    u1_above_n1 = margins["U1_vs_N1"]["band"] == "A_ABOVE_B"
    if not u1_above_n1:
        findings.append("STOPIF2_U1_NOT_ABOVE_N1__TYPING_NOT_THE_VARIABLE")
    u1_vs_u3_sep = margins["U1_vs_U3"]["band"] != "NOT_SEPARATED"
    if not u1_vs_u3_sep:
        findings.append("STOPIF3_U1_TIES_U3__POS_PROFILE_IN_DISGUISE")
    u1_above_bar = u1["band_vs_bar"] == "ABOVE_BAR"
    if u1_above_n1 and not u1_above_bar:
        findings.append("STOPIF4_U1_ABOVE_N1_BUT_BELOW_BAR__MARGIN_NOT_A_WIN")
    s1_above_n3 = margins["S1_vs_N3"]["band"] == "A_ABOVE_B"
    if not s1_above_n3:
        findings.append("STOPIF5_S1_NOT_ABOVE_N3__SECOND_INDEPENDENT_NEGATIVE_ON_PREDICTION_ERROR")

    # --- ORIGINAL BRIEF's own STOP-IF (ii): T1(=U1) beats A0 but NOT T2_UNTYPED -> the gain is the
    # WORD SELECTION (which neighbours got counted), not the TYPE (the relation label). This is a
    # DIFFERENT question from STOPIF3 (U1 vs U3, role-alone ceiling) -- T2 keeps neighbour identity
    # and the SAME coverage as U1, dropping only the label, so it isolates the label's own marginal
    # contribution over and above merely restricting to arc-connected neighbours. ------------------
    u1_beats_a0 = margins["U1_vs_A0"]["band"] == "A_ABOVE_B"
    t2_beats_a0 = margins["T2_vs_A0"]["band"] == "A_ABOVE_B"
    u1_beats_t2 = margins["U1_vs_T2"]["band"] == "A_ABOVE_B"
    if u1_beats_a0 and t2_beats_a0 and not u1_beats_t2:
        findings.append("ORIGBRIEF_ii_U1_BEATS_A0_BUT_NOT_T2__GAIN_IS_WORD_SELECTION_NOT_TYPE")
    elif u1_beats_a0 and u1_beats_t2:
        findings.append("U1_BEATS_BOTH_A0_AND_T2__TYPE_CARRIES_MARGINAL_INFORMATION_OVER_SELECTION")

    # --- T3_COMBINED (Komninos & Manandhar 2016): the published-best configuration, added on the
    # coordinator's mid-run instruction. Report whether combining ever beats its own better half. --
    t3_beats_u1 = margins["T3_vs_U1"]["band"] == "A_ABOVE_B"
    t3_beats_a0 = margins["T3_vs_A0"]["band"] == "A_ABOVE_B"
    if t3_beats_u1 and t3_beats_a0:
        findings.append("T3_COMBINED_BEATS_BOTH_ITS_OWN_CHANNELS__KOMNINOS_MANANDHAR_CONFIRMED_HERE")
    elif t3_beats_a0 and not t3_beats_u1:
        findings.append("T3_COMBINED_BEATS_A0_BUT_NOT_U1__COMBINATION_DID_NOT_HELP_OVER_TYPED_ALONE")

    cov_disagree = []
    for base, cov_name in (("U1_TYPED_CONTEXT", "U1_COVERAGE_MATCHED"),
                           ("S1_SLOT_COMPETITION", "S1_COVERAGE_MATCHED")):
        if cov_name in auc_results:
            full_auc = auc_results[base]["auc"]
            cov_auc = auc_results[cov_name]["auc"]
            ci_w = auc_results[base]["ci_halfwidth"]
            if abs(full_auc - cov_auc) > ci_w:
                cov_disagree.append(cov_name)
    if cov_disagree:
        findings.append("STOPIF6_COVERAGE_MATCHED_DISAGREES__%s" % ",".join(cov_disagree))

    n6_aucs = [n6_results[k]["auc"] for k in sorted(n6_results)]
    n6_spread = (max(n6_aucs) - min(n6_aucs)) if n6_aucs else 0.0
    if n6_spread > 0.10:
        findings.append("STOPIF7_N6_STEEP_SENSITIVITY_TO_PARSE_CORRUPTION__spread=%.4f" % n6_spread)

    def clears_all(name: str, ctrl_names: List[str]) -> bool:
        res = auc_results[name]
        if res["band_vs_bar"] != "ABOVE_BAR":
            return False
        for c in ctrl_names:
            if margins.get("%s_vs_%s" % (name.split("_")[0], c), {}).get("band") != "A_ABOVE_B":
                pass
        return True

    reopens = []
    if u1["band_vs_bar"] == "ABOVE_BAR" and u1_above_n1 and margins["U1_vs_N2"]["band"] == "A_ABOVE_B":
        reopens.append("U1_TYPED_CONTEXT")
    if s1["band_vs_bar"] == "ABOVE_BAR" and s1_above_n3:
        reopens.append("S1_SLOT_COMPETITION")
    if reopens:
        findings.append("STOPIF8_ORGAN_A_REOPENS__%s" % ",".join(reopens))

    if not findings:
        findings.append("CLEAN_NEGATIVE_CONTEXT_TYPE_AXIS_CLOSED")

    rep["STOP_IF_FINDINGS"] = findings
    rep["SUMMARY_AUC"] = {
        "bar": bar, "A0_INCUMBENT": a0_auc["auc"], "U1_TYPED_CONTEXT": u1["auc"],
        "U3_ROLE_ONLY": u3["auc"], "T2_UNTYPED_SAME_COVERAGE": auc_results["T2_UNTYPED_SAME_COVERAGE"]["auc"],
        "T3_COMBINED": auc_results["T3_COMBINED"]["auc"], "S1_SLOT_COMPETITION": s1["auc"],
        "N1_LABEL_PERMUTED": auc_results["N1_LABEL_PERMUTED"]["auc"],
        "N2_RANDOM_TYPING": auc_results["N2_RANDOM_TYPING"]["auc"],
        "N3_MAGNITUDE_PERMUTED": auc_results["N3_MAGNITUDE_PERMUTED"]["auc"],
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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_WORKERS={N_WORKERS} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    findings = rep.get("STOP_IF_FINDINGS", ["UNKNOWN"])
    verdict = "TYPED_ROLE_CONTEXT__" + "__".join(findings)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Does the grammatical relation carry substitutability a bag-of-words context "
                       "discards? U1 (typed context) vs N1 (label-permuted)/N2 (random-typing)/U3 "
                       "(role-only) vs A0 (reused bag-of-words); S1 (slot-competition write rule) vs "
                       "N3 (magnitude-permuted) vs A0. Bar = max(4 floors) = %.4f, not 0.5. -> %s" % (
                           rep.get("BAR_MAX_FLOOR_AUC", float("nan")), "; ".join(findings))),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "COVERAGE_MIN": COVERAGE_MIN,
                  "CORRUPT_FRACS": list(CORRUPT_FRACS), "DSI_CODE_VERSION": DSI_CODE_VERSION,
                  "N_WORKERS": N_WORKERS},
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
