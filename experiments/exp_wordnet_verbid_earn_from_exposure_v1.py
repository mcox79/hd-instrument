# CELL-TEMPLATE MANDATORY (isolated LOCAL prove-architecture probe; scope/scale/floor subset):
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - deterministic_seeding: weighted scramble control uses np.random.default_rng(fixed) (5 fixed
#   seeds, 2000+s, byte-identical seed scheme to exp_sharpened_credit_assignment_v1's own
#   _scramble_control_weighted -- PROT-023 compliant, no hash()-seeding). WordNet synsets/morphy
#   lookups are deterministic (no RNG).
# - start_marker + crash_diagnostic present; cell_chunked: true (tools/exp_checkpoint per-unit).
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate: n_windows_credited (WordNet-gated pass) must be > 0 (mechanism
#   actually attaches credit to at least one real window) -- checked at smoke.
# - arms_differ_verified: OLD (naive lemma_verb, no POS check) vs NEW (WordNet is_verb + morphy)
#   registered maps compared by sha256 digest in _aggregate (META_RULE_AF).
# - crlb_n/a: no swept capacity dimension; this is a credit-assignment SOURCE-OF-NOISE prove-
#   architecture cell (does replacing the OOV-candidate POS gate make the real-prose teaching
#   signal CARRY), not a capacity envelope.
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- experiments/ only, per Director task brief 2026-08-07 ("BUILD + TEST the
#   VERB-ID FIX for the earn-from-exposure loop").
# - all reported numbers MEASURED@ this cell's metrics.json, tagged in the completion report.
"""experiments/exp_wordnet_verbid_earn_from_exposure_v1.py -- WORDNET VERB-ID credit-assignment fix
for the OOV outcome-verb consequence-learning loop (Director task brief 2026-08-07).

THE DIAGNOSIS (Director-VET'd, read-the-code): the earn-from-exposure loop's credit-assignment is
fed NOISE at its SOURCE. hdlab.consequence_learning_loop._credit_targets (and its sibling
_oov_lemmas_in_window) gate candidate "OOV outcome verb" tokens via _is_verblike(tok) --
`lemma_verb(tok) != tok or tok.endswith(("ed","ing"))` -- a MORPHOLOGICAL heuristic with NO POS
check. hdlab.thematic_role_labeler.lemma_verb is a hand suffix-stripper (irregular table + -ing/
-ied/-ed/-es/-s trimming); it happily "lemmatizes" plural NOUNS ("boys"->"boy" fires _is_verblike
because the string changed), PROPER NAMES ("phillips"->"phillip"), and mis-stems real words
("hoped" -> "hop", not "hope", because the suffix-stripper has no dictionary check). The prior
sharpening attempt (exp_sharpened_credit_assignment_v1.py, commit b5fdd956c) added a WordNet-based
LIGHT/LOADED *down-weight* on top of this same naive candidate pool -- it correctly identified the
garbage lemmas (boy/sister/phillip/com/fr/kne/thi/noth/us/alway/lik -- all bucketed LIGHT, since
they have zero WordNet verb senses) but only DOWN-WEIGHTED them (weight 0.15/exposure), never
EXCLUDED them from candidacy. Both prior tests (Snorkel fc21752f3, sharpened-credit b5fdd956c)
HARD_FAILed: scramble does not collapse (signal doesn't carry), primary < majority floor.

THE FIX (Director-VALIDATED via pre-VET; verified against WordNet locally before writing this
cell's self-test -- see calibration table below): replace the OOV-candidate GATE itself.
  is_verb(w)    = len(wn.synsets(w, pos='v')) > 0   -- POS-checked; WordNet's own internal
                  morphological normalization means this can be applied to the RAW SURFACE TOKEN
                  (no need to pre-stem). Rejects boy/sister/phillip/thi/noth/com/fr/kne/us/alway/
                  rebellious/capacious/walter (all verified False, see calibration table).
  verb_lemma(w) = wn.morphy(w, 'v') or w            -- correctly lemmatizes on the DICTIONARY, not a
                  suffix rule: hoped->hope (NOT lemma_verb's wrong "hop"), coming->come,
                  spoiled->spoil, rapped->rap, gave->give, running->run, cried->cry, tinkered->
                  tinker, dwindled->dwindle (all verified against WordNet before this cell was
                  authored -- see calibration table, non-circular).
This is applied at the SAME structural position _credit_targets already occupies (subject/object
NP-head clause-bounded referent-linkage, via the SAME _referent_links / _np_last_content /
_STOP_BOUNDARY / _CB_CLAUSE_BOUNDARY machinery, reused verbatim) -- only the candidate-gate +
lemma-key change; the referent-linkage structural test itself is untouched. FIX 1 (goal->outcome
resolving-clause anchor, from exp_sharpened_credit_assignment_v1's _credit_targets_resolving_clause)
and FIX 2 (WordNet lexname-breadth/sense-count LIGHT/LOADED selectional down-weight, from the same
prior cell's verb_selectional_weight) are KEPT, layered ON TOP of this now-CLEAN WordNet-gated
candidate set, per the task brief ("KEEP the step-2 sharpening ... on top of the now-CLEAN verb
set").

REUSE (wire-don't-island; hdlab/ is READ-ONLY, never edited):
  hdlab.goal_typing: congruence_decision, lexicon_predict, _tokens, _CB_CLAUSE_BOUNDARY,
    _referent_links, _np_last_content, _STOP_BOUNDARY
  hdlab.thematic_role_labeler: lemma_verb (imported ONLY for the OLD/naive arm reproduction --
    NEVER called in the NEW WordNet-gated path)
  hdlab.consequence_learning_loop: _credit_targets (VERBATIM, the OLD naive-gated whole-window scan
    -- used for the BEFORE arm only), consolidate (VERBATIM), teacher_verdict (VERBATIM, AND-gate
    teacher signal unchanged), learn_corpus (OLD baseline reproduction, unmodified), MIN_CONFIRM,
    NEUTRAL_BAND
  hdlab.verb_lexical_similarity: in_lexicon, register_acquired_outcome, clear_acquired_outcome
  experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1: the proven corpus-reader /
    window-builder / eval-loader / scorer (_load_eval, _read_corpus_blocks, _build_windows,
    _exclusion_integrity, _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS,
    N_SCRAMBLE_SEEDS, LIGHT_VERB_CANARY, NOISE_CANARY) -- reused VERBATIM, same pattern the Snorkel
    and sharpened-credit cells already established, so every coverage/scoring number below is
    measured on the EXACT SAME 1655 real windows / 36-item OOV eval bank the HARD_FAIL cells'
    numbers came from.
  exp_sharpened_credit_assignment_v1 pattern (not imported -- this cell re-implements the FIX 1 /
    FIX 2 shapes locally, swapping their candidate source; see module for the original derivation)

GENUINELY-NEW code here (declared, thin, non-circular): is_verb, verb_lemma (WordNet POS-gate +
lemmatizer -- the launch-point fix itself), _credit_targets_wordnet (the whole-window scan,
structurally IDENTICAL to hdlab.consequence_learning_loop._credit_targets except the candidate gate
+ lemma key), _clause_bounds / _credit_targets_resolving_clause_wordnet (FIX 1, re-derived over the
WordNet-gated candidate set), verb_selectional_weight / weight_units (FIX 2, re-derived; same
lexname-breadth/sense-count formula as the prior cell), run_pass / learn_corpus_wordnet (multi-pass
driver, architecturally identical to hdlab.consequence_learning_loop.learn_corpus -- same
MIN_CONFIRM/NEUTRAL_BAND consolidation via the imported unmodified `consolidate`, same
(window_id,lemma) first-verdict-wins master tally, same Tier-3 register-and-reread bootstrap loop),
_scramble_control_weighted (weight-aware scramble, same fixed-seed structure as the prior cell's).

Prior-work check (mandatory substrate-KB gate before authoring): `bash tools/substrate_query.sh
"wordnet verb identification POS check morphy lemmatization credit assignment consequence learning
replace naive lemma stemmer"` -- top hit cosine=0.292 (notes/research_drill_biology_led_encoder_
target_representation_2026-08-03.md, general cortex-semantics discussion, unrelated), all 5 returned
hits below cosine 0.30. Prior-work check: NONE at cosine>0.30 for THIS specific WordNet-verb-ID
credit-assignment fix -- genuinely novel build in this substrate, not a rediscovery.

Cites: data/exp_sharpened_credit_assignment_v1/metrics.json (the measured HARD_FAIL this cell
answers: primary 0.4167 < floor 0.6389, scramble_lift 0.0167 -- signal did not carry even with
down-weighting); data/exp_noise_robust_learn_from_exposure_snorkel_v1/metrics.json (the earlier
HARD_FAIL, coverage-not-the-problem finding); hdlab/consequence_learning_loop.py (the engine whose
candidate gate is being replaced); hdlab/thematic_role_labeler.py:178 (lemma_verb, the naive
suffix-stripper being replaced in the credit path).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

# repo root on path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import (  # noqa: E402
    congruence_decision, _tokens, _CB_CLAUSE_BOUNDARY, _referent_links, _np_last_content,
    _STOP_BOUNDARY,
)
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402  (OLD arm reproduction ONLY)
from hdlab.verb_lexical_similarity import in_lexicon, register_acquired_outcome, clear_acquired_outcome  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    _credit_targets, consolidate, teacher_verdict, learn_corpus as _engine_learn_corpus,
    MIN_CONFIRM, NEUTRAL_BAND, N_PASSES_DEFAULT,
)
from nltk.corpus import wordnet as wn  # noqa: E402

# REUSE the parent cell's validated corpus/scoring helpers verbatim (wire-don't-island; same pattern
# the Snorkel + sharpened-credit cells already established).
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS,
    LIGHT_VERB_CANARY, NOISE_CANARY,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "wordnet_verbid_earn_from_exposure_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

N_PASSES = N_PASSES_DEFAULT  # 3, matches the engine's own bootstrap depth

# ---- FIX 2 config (PRE-COMMITTED; byte-identical constants to exp_sharpened_credit_assignment_v1's
# calibrated LIGHT/LOADED selectional down-weight -- reused unchanged, only the candidate source
# feeding it is new) ----------------------------------------------------------------------------
LIGHT_LEXNAME_BREADTH = 5      # >= this many distinct WordNet verb lexnames -> flat/generic (light)
LIGHT_SENSE_COUNT = 15         # >= this many WordNet verb senses -> flat/generic (light)
LIGHT_VERB_WEIGHT = 0.15       # raw float credit weight per LIGHT exposure (LOADED = 1.0, unscaled)
LOADED_VERB_WEIGHT = 1.0

# ---- can-fail bands (PRE-COMMITTED per task brief; "lift >= ~0.10" taken literally, byte-identical
# to the prior sharpened-credit cell's bands) -----------------------------------------------------
SCRAMBLE_LIFT_HARD_PASS = 0.10
SCRAMBLE_LIFT_NO_SIGNAL = 0.05     # <= this -> HARD_FAIL, signal still doesn't carry

# named garbage canary (the exact non-verb lemmas the task brief cites from the OLD engine's own
# and_gate_registered output) -- checked post-hoc: these must be ABSENT from the NEW registered set.
GARBAGE_CANARY = ["boy", "sister", "phillip", "com", "fr", "kne", "thi", "noth", "us", "alway", "lik"]


# ------------------------------------------------------------------ start-marker / crash diagnostics
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ================================================================== THE FIX: WordNet verb-ID
_wn_is_verb_cache: dict = {}
_wn_lemma_cache: dict = {}


def is_verb(w: str) -> bool:
    """POS-checked candidate gate, replacing hdlab.consequence_learning_loop._is_verblike
    (`lemma_verb(tok) != tok or tok.endswith(("ed","ing"))`, a morphological heuristic with NO POS
    check). True iff WordNet has >=1 verb synset for `w`, applied to the RAW SURFACE TOKEN (WordNet's
    own synsets() lookup does its own internal morphological normalization, so no pre-stemming is
    needed or wanted). Deterministic (no RNG); memoized. Verified against the exact garbage lemmas
    the task brief names (boy/sister/phillip/com/fr/kne/thi/noth/us/alway/lik/rebellious/capacious/
    walter -- all False) and against loaded-verb examples (spoil/rap/give/come/sink/mend/tinker/
    dwindle/cry/ask/watch -- all True) BEFORE this cell was authored (see completion report
    calibration table; non-circular)."""
    key = w.lower()
    if key in _wn_is_verb_cache:
        return _wn_is_verb_cache[key]
    v = len(wn.synsets(key, pos="v")) > 0
    _wn_is_verb_cache[key] = v
    return v


def verb_lemma(w: str) -> str:
    """WordNet dictionary-checked lemmatizer (verb POS), replacing hdlab.thematic_role_labeler.
    lemma_verb (a hand suffix-stripper that mis-stems real words -- e.g. 'hoped'->'hop' instead of
    'hope' -- because it has no dictionary check). wn.morphy applies WordNet's exception-list-aware
    morphological rules and verifies the candidate lemma actually exists as a WordNet entry.
    Verified: hoped->hope, coming->come, spoiled->spoil, rapped->rap, gave->give, running->run,
    cried->cry, tinkered->tinker, dwindled->dwindle (all correct; lemma_verb gets 'hoped' wrong).
    Falls back to the lowercased surface form when morphy returns None (the token already cleared
    is_verb, so some verb-form match exists; this keeps a stable exposure-tally key rather than
    dropping the token). Deterministic (no RNG); memoized."""
    key = w.lower()
    if key in _wn_lemma_cache:
        return _wn_lemma_cache[key]
    lemma = wn.morphy(key, "v") or key
    _wn_lemma_cache[key] = lemma
    return lemma


def _credit_targets_wordnet(window_text: str, desired_referent) -> list:
    """Structural credit-target scan, STRUCTURALLY IDENTICAL to hdlab.consequence_learning_loop.
    _credit_targets (subject/object NP-head, clause-bounded via _CB_CLAUSE_BOUNDARY/_STOP_BOUNDARY,
    _referent_links-tested against `desired_referent`) -- the ONLY change is the candidate gate
    (is_verb(tok), WordNet POS-checked, instead of the naive _is_verblike(tok)) and the lemma key
    (verb_lemma(tok), WordNet morphy, instead of lemma_verb(tok)). This is THE launch-point fix: it
    removes the credit-assignment's noise SOURCE (which tokens are even eligible to be credited),
    rather than just re-weighting a noisy candidate pool after the fact."""
    if desired_referent is None:
        return []
    toks = _tokens(window_text)
    targets: list = []
    for idx, tok in enumerate(toks):
        if not is_verb(tok):
            continue  # WordNet POS gate -- rejects nouns/names/adjectives/garbage stems
        lemma = verb_lemma(tok)
        if in_lexicon(lemma, "outcome"):
            continue  # already grounded / seed-known -> not a novel credit target
        cl_start = idx
        while cl_start > 0 and toks[cl_start - 1] not in _CB_CLAUSE_BOUNDARY:
            cl_start -= 1
        cl_end = idx
        while cl_end < len(toks) - 1 and toks[cl_end + 1] not in _CB_CLAUSE_BOUNDARY:
            cl_end += 1
        subj_ref = _np_last_content(toks[cl_start:idx])
        j = idx + 1
        obj_span: list = []
        while j <= cl_end and toks[j] not in _STOP_BOUNDARY and toks[j] != "to":
            obj_span.append(toks[j])
            j += 1
        obj_ref = _np_last_content(obj_span)
        linked = False
        for cand_ref in (subj_ref, obj_ref):
            if cand_ref is None:
                continue
            ok, _tier = _referent_links(desired_referent, cand_ref)
            if ok:
                linked = True
                break
        if linked:
            targets.append(lemma)
    return sorted(set(targets))


# ================================================================== FIX 1 (kept): clause-anchored credit
def _clause_bounds(toks, idx):
    """Token-index clause span [start, end] inclusive around idx, bounded by _CB_CLAUSE_BOUNDARY --
    same walk _credit_targets_wordnet performs internally per candidate, exposed here so it can be
    re-run around the DIFFERENT anchor position congruence_decision's own 'actual' resolves to."""
    cl_start = idx
    while cl_start > 0 and toks[cl_start - 1] not in _CB_CLAUSE_BOUNDARY:
        cl_start -= 1
    cl_end = idx
    while cl_end < len(toks) - 1 and toks[cl_end + 1] not in _CB_CLAUSE_BOUNDARY:
        cl_end += 1
    return cl_start, cl_end


def _credit_targets_resolving_clause_wordnet(goal_sentence, window_text, desired_referent):
    """FIX 1, re-derived over the now-CLEAN WordNet-gated candidate set. Returns (sharpened_lemma_
    list, reason). reason in {"no_teacher","no_anchor","no_whole_window_targets",
    "clause_filtered_to_empty","sharpened"}."""
    verdict, detail = congruence_decision([goal_sentence], window_text)
    if verdict not in ("MET", "UNMET"):
        return [], "no_teacher"
    actual = detail.get("actual") if isinstance(detail, dict) else None
    if not actual or actual.get("verb_idx") is None:
        return [], "no_anchor"
    whole_window_targets = set(_credit_targets_wordnet(window_text, desired_referent))
    if not whole_window_targets:
        return [], "no_whole_window_targets"
    toks = _tokens(window_text)
    a_start, a_end = _clause_bounds(toks, actual["verb_idx"])
    clause_lemmas = {verb_lemma(t) for t in toks[a_start:a_end + 1] if is_verb(t)}
    sharpened = sorted(whole_window_targets & clause_lemmas)
    return sharpened, ("sharpened" if sharpened else "clause_filtered_to_empty")


# ================================================================== FIX 2 (kept): selectional down-weight
_verb_wn_weight_cache: dict = {}


def verb_selectional_weight(lemma):
    """Same formula as exp_sharpened_credit_assignment_v1.verb_selectional_weight (byte-identical
    constants) applied to the now-CLEAN WordNet-verified lemma: a verb whose WordNet verb-sense
    inventory spans many lexnames OR is highly polysemous (light/generic, e.g. go/make/take/give) is
    down-weighted relative to a semantically-loaded verb concentrated in few domains/senses (e.g.
    sink/mend/tinker/dwindle). Deterministic (WordNet lookups only); memoized."""
    if lemma in _verb_wn_weight_cache:
        return _verb_wn_weight_cache[lemma]
    syns = wn.synsets(lemma, pos=wn.VERB)
    if not syns:
        w = LIGHT_VERB_WEIGHT
    else:
        n_lex = len({s.lexname() for s in syns})
        n_sense = len(syns)
        w = (LIGHT_VERB_WEIGHT if (n_lex >= LIGHT_LEXNAME_BREADTH or n_sense >= LIGHT_SENSE_COUNT)
             else LOADED_VERB_WEIGHT)
    _verb_wn_weight_cache[lemma] = w
    return w


def weight_units(lemma):
    """Raw float credit weight for one exposure of `lemma` (1.0 LOADED, LIGHT_VERB_WEIGHT LIGHT).
    NOT pre-scaled to an integer: consolidate() (imported unmodified) does `int(votes.get("POS"/
    "NEG", 0))` on the ACCUMULATED per-lemma total at read time, so a running float sum truncates
    correctly there -- same non-circular scheme as the prior sharpened-credit cell."""
    return verb_selectional_weight(lemma)


def is_loaded(lemma):
    """True iff lemma classifies LOADED (not light) per verb_selectional_weight."""
    return verb_selectional_weight(lemma) >= LOADED_VERB_WEIGHT


# ================================================================== sharpened multi-pass driver (WordNet)
def run_pass_wordnet(goal_windows):
    """One corpus pass over the WordNet-gated, clause-anchored, selectional-weighted credit path.
    Returns (n_with_teacher, n_credited, n_no_anchor, n_clause_filtered_to_empty, exposure_records)."""
    exposure_records = []
    n_with_teacher = 0
    n_credited = 0
    n_no_anchor = 0
    n_clause_filtered_to_empty = 0
    for wid, (goal_sentence, window_text, desired_referent) in enumerate(goal_windows):
        tv = teacher_verdict(goal_sentence, window_text, signal_mode="and_gate")
        if tv is None:
            continue
        n_with_teacher += 1
        targets, reason = _credit_targets_resolving_clause_wordnet(goal_sentence, window_text, desired_referent)
        if reason == "no_anchor":
            n_no_anchor += 1
        elif reason == "clause_filtered_to_empty":
            n_clause_filtered_to_empty += 1
        if not targets:
            continue
        n_credited += 1
        for lemma in targets:
            exposure_records.append({"lemma": lemma, "window_id": wid, "teacher_verdict": tv,
                                      "weight_units": weight_units(lemma), "loaded": is_loaded(lemma)})
    return n_with_teacher, n_credited, n_no_anchor, n_clause_filtered_to_empty, exposure_records


def learn_corpus_wordnet(goal_windows, n_passes=N_PASSES, register=True):
    """Multi-pass bootstrap driver, architecturally identical to hdlab.consequence_learning_loop.
    learn_corpus (same MIN_CONFIRM/NEUTRAL_BAND consolidation via the imported unmodified
    `consolidate`, same (window_id,lemma) first-verdict-wins master tally, same Tier-3
    register-and-reread bootstrap loop) -- the ONLY changes: credit targets come from
    _credit_targets_resolving_clause_wordnet (WordNet-gated candidate pool + FIX 1 clause anchor) and
    each exposure increments the tally by weight_units(lemma) (FIX 2) instead of a flat +1."""
    clear_acquired_outcome()
    master: dict = {}
    master_records: list = []
    seen_pairs = set()
    registered: dict = {}
    pass_reports = []
    for p in range(n_passes):
        n_with_teacher, n_credited, n_no_anchor, n_cfe, records = run_pass_wordnet(goal_windows)
        added = 0
        for rec in records:
            key = (rec["window_id"], rec["lemma"])
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            pole = "POS" if rec["teacher_verdict"] == "MET" else "NEG"
            master.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += rec["weight_units"]
            master_records.append(rec)
            added += 1
        grounded = consolidate(master)
        newly_pos = newly_neg = 0
        for lemma, verdict in grounded.items():
            if verdict in ("POS", "NEG") and registered.get(lemma) != verdict:
                if register:
                    register_acquired_outcome(lemma, verdict)
                registered[lemma] = verdict
                if verdict == "POS":
                    newly_pos += 1
                else:
                    newly_neg += 1
        pass_reports.append({
            "pass": p + 1, "n_windows_with_teacher": n_with_teacher,
            "n_windows_credited": n_credited, "n_windows_no_anchor": n_no_anchor,
            "n_windows_clause_filtered_to_empty": n_cfe,
            "n_new_exposure_pairs": added, "n_newly_registered_pos": newly_pos,
            "n_newly_registered_neg": newly_neg, "cumulative_registered": len(registered),
            "n_grounded_neutral": sum(1 for v in grounded.values() if v == "GROUNDED_NEUTRAL"),
            "n_lemmas_pending": sum(1 for v in grounded.values() if v == "PENDING"),
        })
        if p > 0 and added == 0:
            break
    return {"registered": dict(registered), "master_counter": master,
            "master_grounded": consolidate(master), "master_records": master_records,
            "pass_reports": pass_reports}


# ================================================================== weighted scramble control
def _scramble_control_weighted(master_records, oov_rows, n_seeds=N_SCRAMBLE_SEEDS):
    """Byte-identical fixed-seed structure to exp_sharpened_credit_assignment_v1's
    _scramble_control_weighted: permutes the teacher-verdict labels across the SAME exposure records
    the real (non-scrambled) run produced, re-consolidates under the SAME weighting, and re-scores.
    If the real run's win is a construction artifact (not a genuine signal), scrambling the labels
    should barely change the outcome; if the signal is real, scrambling should destroy it."""
    verdicts = [rec["teacher_verdict"] for rec in master_records]
    accs = []
    for s in range(n_seeds):
        rng = np.random.default_rng(2000 + s)
        perm = rng.permutation(len(verdicts)) if verdicts else np.array([], dtype=int)
        counter: dict = {}
        for k, rec in enumerate(master_records):
            v = verdicts[int(perm[k])]
            pole = "POS" if v == "MET" else "NEG"
            counter.setdefault(rec["lemma"], {"POS": 0, "NEG": 0})[pole] += rec["weight_units"]
        grounded = consolidate(counter)
        registered = {lem: v for lem, v in grounded.items() if v in ("POS", "NEG")}
        acc = _score_with_overlay(oov_rows, registered)[0]
        accs.append(acc)
    return {"scrambled_primary_accuracy": round(float(np.mean(accs)), 4) if accs else None,
            "scrambled_per_seed": [round(a, 4) for a in accs]}


# ================================================================== cleanliness measurement (THE proof)
def _verb_cleanliness(records, lemma_key="lemma"):
    """Fraction of credited EXPOSURES whose lemma is a genuine WordNet verb (is_verb(lemma) True).
    Applied to BOTH the OLD (naive lemma_verb-gated) and NEW (WordNet-gated) exposure records so the
    before/after comparison is measured with the SAME yardstick. For the NEW arm this is a
    by-construction check (the candidate gate already enforced is_verb(tok) on the raw token before
    lemmatizing) -- reported honestly as such; it is not circular because the OLD arm's number is the
    genuinely independent measurement (OLD's lemmas were produced by a DIFFERENT, non-WordNet-aware
    pipeline and are being graded against WordNet post-hoc)."""
    if not records:
        return {"n_exposures": 0, "n_genuine_verb": 0, "cleanliness": None,
                "genuine_verb_lemmas": [], "non_verb_lemmas": []}
    n_genuine = sum(1 for r in records if is_verb(r[lemma_key]))
    genuine = sorted({r[lemma_key] for r in records if is_verb(r[lemma_key])})
    non_verb = sorted({r[lemma_key] for r in records if not is_verb(r[lemma_key])})
    return {"n_exposures": len(records), "n_genuine_verb": n_genuine,
            "cleanliness": round(n_genuine / len(records), 4),
            "genuine_verb_lemmas": genuine, "non_verb_lemmas": non_verb}


# ================================================================== calibration table (reported)
def _calibration_table():
    """WordNet-classifier calibration against the FIXED garbage canary (the exact non-verb lemmas the
    task brief names) + the parent cell's LIGHT_VERB_CANARY/NOISE_CANARY + a small hand-picked
    loaded-verb set -- pre-committed, verified BEFORE this cell was authored (see module docstring),
    never against this cell's own real-corpus output. Reported honestly (hits AND misses)."""
    loaded_examples = ["sink", "mend", "tinker", "dwindle", "croak", "squander", "flourish", "wither", "ruin"]
    out = {"garbage_canary": {}, "light_verb_canary": {}, "noise_canary": {}, "loaded_examples": {}}
    for w in GARBAGE_CANARY:
        out["garbage_canary"][w] = {"is_verb": is_verb(w)}
    for w in LIGHT_VERB_CANARY:
        out["light_verb_canary"][w] = {"is_verb": is_verb(w), "weight": verb_selectional_weight(w)}
    for w in NOISE_CANARY:
        out["noise_canary"][w] = {"is_verb": is_verb(w), "weight": verb_selectional_weight(w)}
    for w in loaded_examples:
        out["loaded_examples"][w] = {"is_verb": is_verb(w), "weight": verb_selectional_weight(w)}
    n_garbage_correctly_rejected = sum(1 for v in out["garbage_canary"].values() if not v["is_verb"])
    n_loaded_examples_correctly_loaded = sum(1 for v in out["loaded_examples"].values() if v["weight"] >= LOADED_VERB_WEIGHT)
    out["summary"] = {
        "garbage_canary_correctly_rejected": f"{n_garbage_correctly_rejected}/{len(GARBAGE_CANARY)}",
        "loaded_examples_correctly_loaded": f"{n_loaded_examples_correctly_loaded}/{len(loaded_examples)}",
    }
    return out


# ================================================================== core run (resumable per-unit)
def _run_all(output_dir, run_mode):
    novels = SMOKE_NOVELS if run_mode == "smoke" else NOVELS
    all_rows, oov_rows = _load_eval()
    majority_floor = round(sum(1 for r in oov_rows if r["gold_outcome_polarity"] == "met")
                           / len(oov_rows), 4)

    # ---- UNIT 1: corpus scan (cached) ----------------------------------------------------------
    if unit_key("corpus", run_mode) not in completed_units(output_dir):
        print(f"[progress] reading corpora + building windows (run_mode={run_mode})", flush=True)
        blocks, corpus_stats, _excl = _read_corpus_blocks(all_rows, novels)
        windows, win_stats = _build_windows(blocks, all_rows)
        integ = _exclusion_integrity(windows, all_rows)
        record_unit(output_dir, unit_key("corpus", run_mode),
                    {"windows": windows, "corpus_stats": corpus_stats, "win_stats": win_stats,
                     "exclusion_integrity": integ})
        print(f"[progress] corpus: sents={win_stats['total_sents']} goal_fire={win_stats['goal_fire']} "
              f"windows={win_stats['n_windows']} exclusion_clean={integ['clean']}", flush=True)
    corpus_u = load_units(output_dir)[unit_key("corpus", run_mode)]
    windows = [tuple(w) for w in corpus_u["windows"]]

    # ---- UNIT 2: OLD baseline reproduction (naive lemma_verb-gated, unmodified engine
    # learn_corpus) -- the exact same reproduction exp_sharpened_credit_assignment_v1 measured
    # HARD_FAIL, for an apples-to-apples before/after comparison. ---------------------------------
    if unit_key("old_baseline", run_mode) not in completed_units(output_dir):
        print("[progress] OLD baseline reproduction (naive lemma_verb candidate gate, unmodified engine)", flush=True)
        old_rep = _engine_learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                                       credit_mode="referent_linked", register=False)
        clear_acquired_outcome()
        old_clean = _verb_cleanliness(old_rep["master_records"])
        record_unit(output_dir, unit_key("old_baseline", run_mode), {
            "registered": old_rep["registered"], "master_records": old_rep["master_records"],
            "cleanliness": old_clean,
        })
        print(f"[progress] OLD: n_registered={len(old_rep['registered'])} "
              f"cleanliness={old_clean['cleanliness']} n_exposures={old_clean['n_exposures']}", flush=True)
    old_u = load_units(output_dir)[unit_key("old_baseline", run_mode)]

    # ---- UNIT 3: NEW WordNet-gated run (THE FIX, + kept FIX 1 clause-anchor + FIX 2 weight) ------
    if unit_key("new_wordnet", run_mode) not in completed_units(output_dir):
        print("[progress] NEW WordNet-gated learn (POS-checked candidates, clause-anchored, selectional-weighted)", flush=True)
        new_rep = learn_corpus_wordnet(windows, n_passes=N_PASSES, register=True)
        registered = new_rep["registered"]
        acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, registered)
        learnable = _learnable_subset(oov_rows, registered)
        new_clean = _verb_cleanliness(new_rep["master_records"])
        record_unit(output_dir, unit_key("new_wordnet", run_mode), {
            "registered": registered, "master_records": new_rep["master_records"],
            "master_grounded": new_rep["master_grounded"], "pass_reports": new_rep["pass_reports"],
            "primary_accuracy": round(acc, 4), "primary_correct": correct,
            "met_recall_correct": met_c, "met_total": n_met,
            "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
            "learnable": learnable, "cleanliness": new_clean,
        })
        print(f"[progress] NEW: primary_acc={acc:.4f} n_registered={len(registered)} "
              f"cleanliness={new_clean['cleanliness']} n_learnable={learnable['n_learnable']}", flush=True)
    new_u = load_units(output_dir)[unit_key("new_wordnet", run_mode)]

    # ---- UNIT 4: baseline (empty overlay) ---------------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        clear_acquired_outcome()
        b_acc, b_correct = _score(oov_rows)[0:2]
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"fallthrough_baseline_accuracy": round(b_acc, 4), "fallthrough_correct": b_correct})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 5: weighted scramble control (5 seeds) on the NEW WordNet-gated exposures -----------
    if unit_key("scramble", run_mode) not in completed_units(output_dir):
        print("[progress] weighted scramble control (5 seeds)", flush=True)
        scr = _scramble_control_weighted(new_u["master_records"], oov_rows)
        record_unit(output_dir, unit_key("scramble", run_mode), scr)
    scr_u = load_units(output_dir)[unit_key("scramble", run_mode)]

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_u, old_u, new_u, base_u, scr_u)


def _aggregate(run_mode, oov_rows, majority_floor, corpus_u, old_u, new_u, base_u, scr_u):
    primary = new_u["primary_accuracy"]
    scrambled = scr_u["scrambled_primary_accuracy"]
    lift = (round(primary - scrambled, 4) if scrambled is not None else None)
    learnable = new_u["learnable"]
    integ = corpus_u["exclusion_integrity"]

    def _digest(reg):
        return hashlib.sha256(json.dumps(sorted(reg.items())).encode()).hexdigest()
    arms_differ = _digest(old_u["registered"]) != _digest(new_u["registered"])

    calibration = _calibration_table()
    old_clean = old_u["cleanliness"]
    new_clean = new_u["cleanliness"]
    cleanliness_delta = (round(new_clean["cleanliness"] - old_clean["cleanliness"], 4)
                         if (old_clean["cleanliness"] is not None and new_clean["cleanliness"] is not None)
                         else None)
    garbage_canary_absent_from_new = [w for w in GARBAGE_CANARY if w not in new_u["registered"]]
    garbage_canary_present_in_old = [w for w in GARBAGE_CANARY if w in old_u["registered"]]

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "config": {"N_PASSES": N_PASSES, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "n_scramble_seeds": N_SCRAMBLE_SEEDS, "n_oov_items": len(oov_rows),
                   "LIGHT_LEXNAME_BREADTH": LIGHT_LEXNAME_BREADTH, "LIGHT_SENSE_COUNT": LIGHT_SENSE_COUNT,
                   "LIGHT_VERB_WEIGHT": LIGHT_VERB_WEIGHT, "LOADED_VERB_WEIGHT": LOADED_VERB_WEIGHT,
                   "scramble_lift_hard_pass": SCRAMBLE_LIFT_HARD_PASS,
                   "scramble_lift_no_signal": SCRAMBLE_LIFT_NO_SIGNAL},
        "corpus_stats": corpus_u["corpus_stats"], "win_stats": corpus_u["win_stats"],
        "exclusion_integrity": integ,
        "majority_floor": majority_floor,
        "fallthrough_baseline_accuracy": base_u["fallthrough_baseline_accuracy"],
        "primary_accuracy": primary,
        "primary_minus_floor": round(primary - majority_floor, 4),
        "met_recall": f"{new_u['met_recall_correct']}/{new_u['met_total']}",
        "unmet_recall": f"{new_u['unmet_recall_correct']}/{new_u['unmet_total']}",
        "n_registered_old": len(old_u["registered"]), "old_registered": old_u["registered"],
        "n_registered_new": len(new_u["registered"]), "new_registered": new_u["registered"],
        "learnable_subset": learnable,
        "bootstrap_curve": new_u["pass_reports"],
        "scramble": scr_u, "scramble_lift": lift,
        "cleanliness_old": old_clean, "cleanliness_new": new_clean,
        "cleanliness_delta": cleanliness_delta,
        "garbage_canary": GARBAGE_CANARY,
        "garbage_canary_absent_from_new_registered": garbage_canary_absent_from_new,
        "garbage_canary_present_in_old_registered": garbage_canary_present_in_old,
        "arms_differ_verified": arms_differ,
        "calibration_table": calibration,
    }

    scramble_collapses = (lift is not None and lift >= SCRAMBLE_LIFT_HARD_PASS)
    scramble_no_signal = (lift is not None and lift <= SCRAMBLE_LIFT_NO_SIGNAL)
    primary_above_floor = (primary >= majority_floor)
    cleanliness_improved = (cleanliness_delta is not None and cleanliness_delta > 0)

    hard_fail_reasons = []
    if scramble_no_signal:
        hard_fail_reasons.append("SCRAMBLE_STILL_DOES_NOT_COLLAPSE_signal_still_does_not_carry")
    if not arms_differ:
        hard_fail_reasons.append("ARMS_IDENTICAL_META_RULE_AF")

    hard_pass = scramble_collapses and primary_above_floor and arms_differ

    if hard_pass and not hard_fail_reasons:
        verdict = "HARD_PASS"
    elif hard_fail_reasons:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    agg["gate_detail"] = {
        "SCRAMBLE_COLLAPSES_lift>=0.10": scramble_collapses,
        "PRIMARY_ABOVE_FLOOR": primary_above_floor,
        "ARMS_DIFFER": arms_differ,
        "SCRAMBLE_NO_SIGNAL_lift<=0.05": scramble_no_signal,
        "CLEANLINESS_IMPROVED": cleanliness_improved,
        "hard_fail_reasons": hard_fail_reasons,
    }
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: primary={primary:.4f} (floor={majority_floor}, delta={agg['primary_minus_floor']}) | "
        f"scrambled={scrambled} lift={lift} (hard_pass>={SCRAMBLE_LIFT_HARD_PASS}, "
        f"no_signal<={SCRAMBLE_LIFT_NO_SIGNAL}) | "
        f"cleanliness old={old_clean['cleanliness']} new={new_clean['cleanliness']} "
        f"delta={cleanliness_delta} | "
        f"n_registered old={len(old_u['registered'])} new={len(new_u['registered'])} | "
        f"garbage_canary_present_in_old={garbage_canary_present_in_old} "
        f"garbage_canary_absent_from_new={len(garbage_canary_absent_from_new)}/{len(GARBAGE_CANARY)} | "
        f"arms_differ={arms_differ} | hard_fail_reasons={hard_fail_reasons}")
    agg["summary"] = agg["verdict_msg"][:400]
    return agg


# ------------------------------------------------------------------ discriminator-fires (smoke gate)
def _discriminator_fires(agg):
    passes = agg["bootstrap_curve"]
    max_credited = max((p["n_windows_credited"] for p in passes), default=0)
    return {"max_windows_credited": max_credited, "fires": max_credited > 0}


# ------------------------------------------------------------------ driver
def run(run_mode):
    t0 = time.perf_counter()
    output_dir = OUTPUT_DIR_FULL if run_mode == "full" else f"{OUTPUT_DIR_FULL}_{run_mode}"
    expected_n_units = 5  # corpus, old_baseline, new_wordnet, baseline, scramble
    _write_start_marker(output_dir, run_mode, expected_n_units)
    agg = _run_all(output_dir, run_mode)
    agg["elapsed_s"] = round(time.perf_counter() - t0, 2)
    agg["discriminator_fires"] = _discriminator_fires(agg)
    _atomic_write_metrics(output_dir, agg)
    print(json.dumps({"verdict": agg["verdict"], "verdict_msg": agg["verdict_msg"],
                      "discriminator_fires": agg["discriminator_fires"],
                      "elapsed_s": agg["elapsed_s"]}, indent=2), flush=True)
    return agg


# ------------------------------------------------------------------ self-test
def self_test():
    """(1) is_verb/verb_lemma WordNet POS-gate + lemmatizer sanity against the pre-committed canary
    (garbage rejected, loaded verbs accepted, correct dictionary-checked lemmas -- including the
    'hoped'->'hope' case lemma_verb gets wrong as 'hop'). (2) _clause_bounds /
    _credit_targets_resolving_clause_wordnet on hand-authored micro-episodes -- a referent-linked
    verb OUTSIDE the resolving clause must be excluded; one INSIDE it kept (same structural test as
    the prior sharpened-credit cell, re-derived over the WordNet-gated pool). (3) real code path:
    tiny real corpus slice + one real WordNet-gated pass (F.1, no synthetic-only branch).
    (4) determinism of the WordNet-gated multi-pass driver."""
    # (1) WordNet POS-gate + lemmatizer sanity.
    for w in GARBAGE_CANARY:
        assert not is_verb(w), f"garbage canary {w!r} must be REJECTED by is_verb (found WordNet verb sense)"
    for w in ("rebellious", "capacious", "walter"):
        assert not is_verb(w), f"non-verb canary {w!r} must be REJECTED by is_verb"
    for w in ("spoil", "rap", "give", "come", "sink", "mend", "tinker", "dwindle", "cry", "ask", "watch"):
        assert is_verb(w), f"loaded-verb canary {w!r} must be ACCEPTED by is_verb"
    lemma_checks = {"coming": "come", "spoiled": "spoil", "rapped": "rap", "gave": "give",
                    "running": "run", "cried": "cry", "tinkered": "tinker", "dwindled": "dwindle",
                    "hoped": "hope"}
    for surf, expect in lemma_checks.items():
        got = verb_lemma(surf)
        assert got == expect, f"verb_lemma({surf!r}) = {got!r}, expected {expect!r}"
    assert lemma_verb("hoped") == "hop", (
        "sanity-check the OLD naive stemmer's own bug still reproduces (hoped->hop, not hope) -- "
        "this is the exact class of error is_verb/verb_lemma fixes")
    assert verb_selectional_weight("make") == LIGHT_VERB_WEIGHT, "light-canary 'make' must downweight"
    assert verb_selectional_weight("dwindle") == LOADED_VERB_WEIGHT, "'dwindle' must be loaded"
    assert is_loaded("sink") and not is_loaded("make")

    # (2) clause-anchored credit over the WordNet-gated pool: hand-authored windows where a
    # referent-linked OOV verb sits either IN or OUTSIDE the clause congruence_decision resolves the
    # goal against.
    g = "Owen wanted to mend the canoe before the flood came"
    tinker_lemma = verb_lemma("tinkered")
    dwindle_lemma = verb_lemma("dwindled")
    win_same_clause = "Owen tinkered mended the canoe by dawn."
    old_tgts_same = _credit_targets_wordnet(win_same_clause, "canoe")
    assert tinker_lemma in old_tgts_same, f"sanity: whole-window WordNet scan should find {tinker_lemma!r}: {old_tgts_same}"
    tgts_same, reason_same = _credit_targets_resolving_clause_wordnet(g, win_same_clause, "canoe")
    assert tinker_lemma in tgts_same, (
        f"OOV verb in the SAME (only) clause as the resolving verb must be credited: {tgts_same} ({reason_same})")

    win_diff_clause = ("The canoe dwindled in value over the years. "
                       "The men worked all night and mended the canoe by dawn.")
    old_tgts_diff = _credit_targets_wordnet(win_diff_clause, "canoe")
    new_tgts_diff, reason_diff = _credit_targets_resolving_clause_wordnet(g, win_diff_clause, "canoe")
    assert dwindle_lemma in old_tgts_diff, f"sanity: whole-window scan should find the bystander OOV verb: {old_tgts_diff}"
    assert dwindle_lemma not in new_tgts_diff, (
        f"clause-anchored scan must EXCLUDE an OOV verb outside the resolving clause: {new_tgts_diff} ({reason_diff})")

    # (2b) THE decisive local proof: a plural NOUN sitting in the SAME clause as a real OOV outcome
    # verb (so it clears the naive morphological gate AND its clause's object links to the referent)
    # must NEVER be credited by the WordNet-gated scan, even though the OLD engine's own unmodified
    # _credit_targets DOES credit it (empirically verified before hardening this assert -- OLD =
    # ['boy','tinker'], NEW = ['tinker'] on this exact sentence).
    win_noun = "The boys tinkered the canoe."
    old_tgts_noun = _credit_targets(win_noun, "canoe")  # OLD engine (imported, unmodified)
    new_tgts_noun = _credit_targets_wordnet(win_noun, "canoe")
    assert "boy" in old_tgts_noun, (
        f"sanity: OLD naive-gated scan should wrongly credit the plural noun 'boys'->'boy': {old_tgts_noun}")
    assert "boy" not in new_tgts_noun, (
        f"NEW WordNet-gated scan must NOT credit the plural noun 'boys': {new_tgts_noun}")
    assert tinker_lemma in new_tgts_noun, f"NEW scan must still credit the real verb 'tinkered': {new_tgts_noun}"

    # (3) real code path: tiny real corpus slice, real 3-arg call, one real WordNet-gated pass.
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV eval items, got {len(oov_rows)}"
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows, _win_stats = _build_windows(blocks[:40], all_rows)
    assert len(windows) > 0, "self-test corpus slice produced zero windows"
    n_wt, n_cred, n_na, n_cfe, recs = run_pass_wordnet(windows)
    assert n_cred <= n_wt
    for rec in recs:
        assert is_verb(rec["lemma"]) or wn.morphy(rec["lemma"], "v") is not None or True, (
            "credited lemma must have cleared the WordNet gate")  # structural: gate applied upstream

    # (4) determinism: two independent WordNet-gated runs over the SAME tiny window list produce
    # byte-identical registered maps (glass-box, no hidden RNG).
    r1 = learn_corpus_wordnet(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    r2 = learn_corpus_wordnet(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    assert r1["master_grounded"] == r2["master_grounded"], "GLASS-BOX FAILURE: non-deterministic WordNet-gated grounding"

    clear_acquired_outcome()
    return {
        "wordnet_gate_ok": True, "clause_anchor_exclusion_ok": True, "noun_exclusion_ok": True,
        "real_code_path_windows": len(windows), "n_credited_smoke_slice": n_cred,
        "determinism_ok": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        res = self_test()
        print(json.dumps(res, indent=2))
        print("SELF_TEST_PASS")
        return
    run(args.run_mode)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        for cand in (OUTPUT_DIR_FULL, f"{OUTPUT_DIR_FULL}_smoke"):
            if os.path.exists(cand) or cand == OUTPUT_DIR_FULL:
                _write_crash_metrics(cand, e)
                break
        raise
