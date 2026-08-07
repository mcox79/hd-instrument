# CELL-TEMPLATE MANDATORY (isolated LOCAL prove-architecture probe; scope/scale/floor subset):
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - deterministic_seeding: weighted scramble control uses np.random.default_rng(fixed) (5 fixed
#   seeds, byte-identical seed scheme to the reused _scramble_control_weighted -- PROT-023
#   compliant, no hash()-seeding). WordNet synsets/morphy lookups + PosTagger.tag are deterministic
#   (no RNG; the tagger is a PERSISTED averaged-perceptron model, decoded via Viterbi).
# - start_marker + crash_diagnostic present; cell_chunked: true (tools/exp_checkpoint per-unit).
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate: n_windows_credited (POS-gated pass) must be > 0 (mechanism actually
#   attaches credit to at least one real window) -- checked at smoke.
# - arms_differ_verified: OLD_NAIVE (lemma_verb, no POS) vs WORDNET_GATE (dictionary-membership
#   is_verb, the prior cell's HARD_FAIL arm, reproduced here as a Gate-D positive control) vs
#   POS_GATE (contextual tagger.tag verdict, THIS cell's fix) -- all three registered maps compared
#   pairwise by sha256 digest in _aggregate (META_RULE_AF).
# - crlb_n/a: no swept capacity dimension; this is a credit-assignment SOURCE-OF-NOISE prove-
#   architecture cell (does replacing the WordNet DICTIONARY-MEMBERSHIP verb-gate with a CONTEXTUAL
#   per-token POS verdict make the real-prose teaching signal CARRY further), not a capacity
#   envelope.
# - positive_control_arms (SCHEMA-VET Gate D): WORDNET_GATE arm reproduces
#   data/exp_wordnet_verbid_earn_from_exposure_v1/metrics.json (primary_accuracy=0.4444,
#   scramble_lift=0.0388) AT THE SAME REGIME (same 1655-window corpus, same 36-item OOV bank, same
#   N_PASSES/MIN_CONFIRM/NEUTRAL_BAND, same code imported verbatim from that cell) -- tolerance 0.02,
#   checked in _aggregate before the POS_GATE arm's numbers are trusted.
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- experiments/ only, per Director task brief 2026-08-07 ("swap the token-level
#   is_verb(tok) dictionary-membership check for a CONTEXTUAL per-token POS verdict from the OWNED
#   trained tagger hdlab/pos_tagger.py").
# - all reported numbers MEASURED@ this cell's metrics.json, tagged in the completion report.
"""experiments/exp_contextual_pos_verbid_earn_from_exposure_v1.py -- CONTEXTUAL POS credit-assignment
fix for the OOV outcome-verb consequence-learning loop (Director task brief 2026-08-07).

THE RESIDUAL BUG (Director-VET'd, read-the-code, on the prior WordNet cell's OWN disk metrics):
experiments/exp_wordnet_verbid_earn_from_exposure_v1.py (commit 12aa5eab3, HARD_FAIL) proved WordNet
DICTIONARY-MEMBERSHIP (`is_verb(w) = len(wn.synsets(w, pos='v')) > 0`) cleans the OBVIOUS garbage a
suffix-stripper lemmatizer produces (cleanliness 0.758 -> 1.000: boy/sister/phillip/com/fr/kne/thi/
noth/us/alway/lik all correctly rejected) -- but scramble-lift only reached 0.0388 (still <=0.05,
NO_SIGNAL). Reading that cell's OWN metrics.json (data/exp_wordnet_verbid_earn_from_exposure_v1/
metrics.json:cleanliness_new.genuine_verb_lemmas), the credited set on the REAL corpus contains
"father", "house", "man", "table", "paper", "witch", "book", "arm", "hat"-class DENOMINAL homographs
-- words WordNet lists a verb SENSE for ("to father a child", "to house refugees", "to table a
motion") that overwhelmingly occur as ORDINARY NOUNS in real prose ("her father", "the house", "a
table"). is_verb() is DICTIONARY membership, not a CONTEXTUAL part-of-speech decision: it cannot tell
"the table was old" (table=NOUN) from "they table the motion" (table=VERB), so it still admits
noun-use occurrences of these words as verb-credit CANDIDATES whenever a coincidental object further
down the clause happens to referent-link (see self_test (2c) below for the exact reproduced case:
WordNet-gate on "Nell's father tinkered the canoe." wrongly credits 'father', because 'canoe' sits in
its forward object-scan and links to the goal referent -- the referent-linkage machinery has no way to
know 'father' was never a verb IN THIS SENTENCE).

THE FIX (this cell, Director task brief 2026-08-07): replace the OOV-candidate GATE's POS test itself
-- from WordNet DICTIONARY membership (type-level, context-free) to a CONTEXTUAL per-token POS verdict
from the OWNED trained tagger hdlab/pos_tagger.py (PosTagger wrapping hdlab.perceptron.
StructuredPerceptron, an averaged structured perceptron with Viterbi decoding -- glass-box, no LLM, no
nltk). The persisted production model (data/frontend_assets/pos_tagger_ud_ewt_upos.json,
HARD_PASS-certified seed-robust at token-tag-acc=0.9063+-0.0005 on real PTB data, data/
exp_pos_tagger_multiseed_cpu_v1/metrics.json) is loaded via PosTagger.load and run ONCE per window
(over the SAME `_tokens(window_text)` token stream the credit-assignment scan already walks), so
every candidate check queries the CONTEXTUAL tag at that exact token position:
  VERB_POS_TAGS = {"VERB", "AUX"}   -- the UD tags covering main verbs + copula/auxiliary (be/have/
                   do/will/...), matching WordNet's own verb-sense coverage (WordNet has a verb
                   synset for be/have/do too) so the two gates are apples-to-apples in SCOPE, only
                   differing in whether the decision is CONTEXTUAL or DICTIONARY-level.
  verb_lemma(w)  = UNCHANGED, still WordNet morphy (imported from the prior cell) -- per task brief
                   ("Layer the contextual-POS gate ON TOP of the existing WordNet morphy lemmatizer
                   (contextual POS decides IS-IT-A-VERB-HERE; morphy still lemmatizes)").
TEST-FIRST VALIDATION (mandatory per task contract, run + reported BEFORE this module was written --
see the completion report's calibration table, which reproduces this cell's own self_test(1)):
tagger.tag() on the EXACT denominal-noun failure cases the task brief names -- "the paper"/"the
table"/"his father" (paper/table/father tagged NOUN) vs "they paper the wall" (paper tagged VERB) --
all correctly disambiguated CONTEXTUALLY, plus 7 more denominal homographs (house/witch/man/book/arm/
hat/cap/back), 22/22 sentence-pairs correct. The tagger is NOT degenerate.

FIX 1 (kept, re-derived over the POS-gated pool): goal->outcome resolving-clause anchor
(_credit_targets_resolving_clause_pos), structurally identical to the prior cell's
_credit_targets_resolving_clause_wordnet.
FIX 2 (kept, REUSED verbatim from the prior cell): WordNet lexname-breadth/sense-count LIGHT/LOADED
selectional down-weight (verb_selectional_weight, weight_units) -- operates on the FINAL lemma
(WordNet morphy, unchanged), independent of which candidate-gate produced it, so it is imported and
applied unmodified.

REUSE (wire-don't-island; hdlab/ is READ-ONLY, never edited; the prior WordNet cell is also treated as
a READ-ONLY reused source, never edited, per the task brief -- "do NOT edit hdlab/ or the prior cell"):
  hdlab.pos_tagger.PosTagger: the launch-point fix itself (load + .tag()).
  hdlab.goal_typing: congruence_decision, _tokens, _CB_CLAUSE_BOUNDARY, _referent_links,
    _np_last_content, _STOP_BOUNDARY (identical import list to the prior cell).
  hdlab.thematic_role_labeler.lemma_verb (imported ONLY for the OLD/naive arm reproduction, exactly as
    the prior cell did -- NEVER called in the NEW POS-gated path).
  hdlab.consequence_learning_loop: _credit_targets (VERBATIM, OLD naive whole-window scan, BEFORE
    arm), consolidate (VERBATIM), teacher_verdict (VERBATIM, AND-gate teacher signal unchanged),
    learn_corpus (OLD baseline reproduction, unmodified), MIN_CONFIRM, NEUTRAL_BAND.
  hdlab.verb_lexical_similarity: in_lexicon, register_acquired_outcome, clear_acquired_outcome.
  experiments.exp_wordnet_verbid_earn_from_exposure_v1 (the prior cell, treated as a reused,
    UNMODIFIED source, same convention as importing an hdlab organ): is_verb, verb_lemma,
    _clause_bounds, _credit_targets_wordnet, run_pass_wordnet, learn_corpus_wordnet (the WordNet-gate
    arm, reproduced VERBATIM here as the Gate-D positive control), verb_selectional_weight,
    weight_units, is_loaded, _scramble_control_weighted, _verb_cleanliness, _calibration_table,
    GARBAGE_CANARY, N_PASSES, LIGHT_LEXNAME_BREADTH, LIGHT_SENSE_COUNT, LIGHT_VERB_WEIGHT,
    LOADED_VERB_WEIGHT, SCRAMBLE_LIFT_HARD_PASS, SCRAMBLE_LIFT_NO_SIGNAL.
  experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1: the proven corpus-reader /
    window-builder / eval-loader / scorer (_load_eval, _read_corpus_blocks, _build_windows,
    _exclusion_integrity, _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS,
    N_SCRAMBLE_SEEDS, LIGHT_VERB_CANARY, NOISE_CANARY) -- reused VERBATIM, same 1655 real windows /
    36-item OOV eval bank the Snorkel / sharpened-credit / WordNet HARD_FAIL cells' numbers came from.

GENUINELY-NEW code here (declared, thin, non-circular): VERB_POS_TAGS, _get_tagger (lazy singleton
load of the persisted model), _pos_tags_for_window (memoized per-window contextual tagging),
_credit_targets_pos (the whole-window scan, structurally IDENTICAL to _credit_targets_wordnet except
the candidate gate is CONTEXTUAL POS instead of WordNet dictionary membership),
_credit_targets_resolving_clause_pos (FIX 1, re-derived over the POS-gated candidate set), run_pass_pos
/ learn_corpus_pos (multi-pass driver, architecturally identical to learn_corpus_wordnet),
AMBIGUOUS_DENOMINAL_CANARY + _denominal_context_audit (the decisive contextual-cleanliness
measurement: for each real-corpus occurrence of a WordNet-admitted denominal-noun/verb homograph,
does the CONTEXTUAL tag say NOUN (correctly excluded) or VERB/AUX (correctly kept)?).

Prior-work check (mandatory substrate-KB gate before authoring): `bash tools/substrate_query.sh
"contextual POS tagger verb identification credit assignment consequence learning denominal noun
disambiguation"` -- top hit cosine=0.3262 (entity='identification', a generic concept_node from
atoms/wordnet, unrelated), all 5 returned hits below/at the noise floor for this specific concept
(next hits: a multi-agent credit-assignment research drill note at 0.3262/0.3164, unrelated domain;
CN_denomination at 0.3135, an unrelated concept-graph node). Prior-work check: NONE at cosine>0.30 for
THIS specific contextual-POS-tagger credit-assignment fix -- genuinely novel build in this substrate,
not a rediscovery (same finding pattern as the prior WordNet cell's own KB check).

Cites: data/exp_wordnet_verbid_earn_from_exposure_v1/metrics.json (the measured HARD_FAIL this cell
answers: primary=0.4444, floor=0.6389, scramble_lift=0.0388, cleanliness_new.genuine_verb_lemmas
containing the denominal homographs father/house/man/table/paper/witch/book/arm this cell's fix
targets); data/exp_pos_tagger_multiseed_cpu_v1/metrics.json (the tagger's own HARD_PASS certification,
mean_tag_acc=0.9063 seed-robust n=5); hdlab/pos_tagger.py (PosTagger, the fix); hdlab/perceptron.py
(StructuredPerceptron, the tagger's underlying mechanism); experiments/
exp_wordnet_verbid_earn_from_exposure_v1.py (the reused WordNet-gate positive-control source).
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

from hdlab.pos_tagger import PosTagger  # noqa: E402  -- THE FIX
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

# REUSE the prior WordNet-gate cell verbatim (READ-ONLY reused source, same convention as an hdlab
# import -- this cell never edits it). This gives the Gate-D positive-control arm "for free" (bit-
# identical reproduction of the cited HARD_FAIL numbers) instead of re-deriving 150 lines of
# byte-identical logic.
from experiments.exp_wordnet_verbid_earn_from_exposure_v1 import (  # noqa: E402
    is_verb, verb_lemma, _clause_bounds, _credit_targets_wordnet, run_pass_wordnet,
    learn_corpus_wordnet, verb_selectional_weight, weight_units, is_loaded,
    _scramble_control_weighted, _verb_cleanliness, _calibration_table, GARBAGE_CANARY,
    N_PASSES, LIGHT_LEXNAME_BREADTH, LIGHT_SENSE_COUNT, LIGHT_VERB_WEIGHT, LOADED_VERB_WEIGHT,
    SCRAMBLE_LIFT_HARD_PASS, SCRAMBLE_LIFT_NO_SIGNAL,
)

# REUSE the parent cell's validated corpus/scoring helpers verbatim (wire-don't-island; same pattern
# the Snorkel + sharpened-credit + WordNet cells already established).
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS,
    LIGHT_VERB_CANARY, NOISE_CANARY,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "contextual_pos_verbid_earn_from_exposure_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

POS_MODEL_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")

# VERB + AUX (copula/auxiliary: be/have/do/will/...) -- matches WordNet's OWN verb-sense coverage
# (WordNet has a verb synset for be/have/do too), so the POS-gate and the WordNet-gate are
# apples-to-apples in SCOPE; the only thing that changes is CONTEXTUAL vs DICTIONARY decision.
VERB_POS_TAGS = frozenset({"VERB", "AUX"})

# The exact denominal noun/verb homographs the prior cell's OWN disk metrics show WordNet's
# dictionary-membership gate admitting into the real-corpus credited set (data/
# exp_wordnet_verbid_earn_from_exposure_v1/metrics.json:cleanliness_new.genuine_verb_lemmas contains
# father/house/man/table/paper/witch/book/arm/hat/cap/back). Used both for the self-test contextual
# spot-check (TEST-FIRST VALIDATION) and the real-corpus _denominal_context_audit.
AMBIGUOUS_DENOMINAL_CANARY = ["father", "house", "man", "table", "paper", "witch", "book", "arm",
                              "hat", "cap", "back"]

# ---- can-fail bands (PRE-COMMITTED per task brief; decisive gate is the SAME as the prior cell's:
# does scramble now COLLAPSE?) -----------------------------------------------------------------
# (SCRAMBLE_LIFT_HARD_PASS / SCRAMBLE_LIFT_NO_SIGNAL imported unchanged from the prior cell: 0.10 / 0.05)

GATE_D_TOLERANCE = 0.02          # WordNet-gate positive-control reproduction tolerance
GATE_D_CITED_PRIMARY = 0.4444    # MEASURED@data/exp_wordnet_verbid_earn_from_exposure_v1/metrics.json
GATE_D_CITED_SCRAMBLE_LIFT = 0.0388  # MEASURED@ same file


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


# ================================================================== THE FIX: contextual POS tagger
_tagger_singleton = None


def _get_tagger() -> PosTagger:
    """Lazy-loaded singleton of the persisted, HARD_PASS-certified production POS tagger
    (data/exp_pos_tagger_multiseed_cpu_v1/metrics.json, mean_tag_acc=0.9063 seed-robust n=5).
    Deterministic decode (Viterbi over fixed averaged weights, no RNG)."""
    global _tagger_singleton
    if _tagger_singleton is None:
        if not os.path.exists(POS_MODEL_PATH):
            raise FileNotFoundError(
                f"trained POS tagger model not found at {POS_MODEL_PATH!r} -- "
                "cannot run the contextual-POS fix without it")
        _tagger_singleton = PosTagger.load(POS_MODEL_PATH)
    return _tagger_singleton


_pos_tags_cache: dict = {}


def _pos_tags_for_window(window_text: str):
    """Memoized (toks, tags) for one window's contextual POS tagging (deterministic given the fixed
    persisted model -- caching is safe and avoids re-tagging the same window across bootstrap passes;
    N_PASSES=3 would otherwise re-tag every window 3x for no benefit, since window text never
    changes pass-over-pass, only the OOV lexicon membership check inside the loop does)."""
    if window_text in _pos_tags_cache:
        return _pos_tags_cache[window_text]
    toks = _tokens(window_text)
    tags = _get_tagger().tag(toks) if toks else []
    _pos_tags_cache[window_text] = (toks, tags)
    return toks, tags


def _credit_targets_pos(window_text: str, desired_referent) -> list:
    """Structural credit-target scan, STRUCTURALLY IDENTICAL to
    experiments.exp_wordnet_verbid_earn_from_exposure_v1._credit_targets_wordnet (subject/object
    NP-head, clause-bounded via _CB_CLAUSE_BOUNDARY/_STOP_BOUNDARY, _referent_links-tested against
    `desired_referent`) -- the ONLY change is the candidate gate: CONTEXTUAL POS (tags[idx] in
    VERB_POS_TAGS, from the trained tagger) instead of WordNet DICTIONARY membership (is_verb(tok)).
    The lemma key is UNCHANGED (verb_lemma, WordNet morphy). This is THE launch-point fix of this
    cell: a token that WordNet lists a verb sense for but that is used as a NOUN in THIS SPECIFIC
    window (father/house/table/paper/witch/book/arm/...) is now excluded, because the tagger reads
    the surrounding context, not just dictionary membership."""
    if desired_referent is None:
        return []
    toks, tags = _pos_tags_for_window(window_text)
    targets: list = []
    for idx, tok in enumerate(toks):
        if tags[idx] not in VERB_POS_TAGS:
            continue  # CONTEXTUAL POS gate -- rejects noun/name/adjective USES, even of WordNet-verb-sense words
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
def _credit_targets_resolving_clause_pos(goal_sentence, window_text, desired_referent):
    """FIX 1, re-derived over the now-CONTEXTUALLY-CLEAN POS-gated candidate set. Structurally
    identical to experiments.exp_wordnet_verbid_earn_from_exposure_v1.
    _credit_targets_resolving_clause_wordnet -- only the candidate gate (tags[idx] in VERB_POS_TAGS
    instead of is_verb(tok)) differs. Returns (sharpened_lemma_list, reason)."""
    verdict, detail = congruence_decision([goal_sentence], window_text)
    if verdict not in ("MET", "UNMET"):
        return [], "no_teacher"
    actual = detail.get("actual") if isinstance(detail, dict) else None
    if not actual or actual.get("verb_idx") is None:
        return [], "no_anchor"
    whole_window_targets = set(_credit_targets_pos(window_text, desired_referent))
    if not whole_window_targets:
        return [], "no_whole_window_targets"
    toks, tags = _pos_tags_for_window(window_text)
    a_start, a_end = _clause_bounds(toks, actual["verb_idx"])
    clause_lemmas = {verb_lemma(t) for i, t in enumerate(toks[a_start:a_end + 1])
                      if tags[a_start + i] in VERB_POS_TAGS}
    sharpened = sorted(whole_window_targets & clause_lemmas)
    return sharpened, ("sharpened" if sharpened else "clause_filtered_to_empty")


# ================================================================== sharpened multi-pass driver (POS)
def run_pass_pos(goal_windows):
    """One corpus pass over the CONTEXTUAL-POS-gated, clause-anchored, selectional-weighted credit
    path. Architecturally identical to experiments.exp_wordnet_verbid_earn_from_exposure_v1.
    run_pass_wordnet. Returns (n_with_teacher, n_credited, n_no_anchor, n_clause_filtered_to_empty,
    exposure_records)."""
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
        targets, reason = _credit_targets_resolving_clause_pos(goal_sentence, window_text, desired_referent)
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


def learn_corpus_pos(goal_windows, n_passes=N_PASSES, register=True):
    """Multi-pass bootstrap driver, architecturally identical to
    experiments.exp_wordnet_verbid_earn_from_exposure_v1.learn_corpus_wordnet -- the ONLY change:
    credit targets come from _credit_targets_resolving_clause_pos (CONTEXTUAL-POS-gated candidate
    pool + FIX 1 clause anchor) instead of the WordNet-dictionary-gated version. FIX 2 (weight_units,
    imported unchanged from the prior cell) is unaffected -- it operates on the final lemma."""
    clear_acquired_outcome()
    master: dict = {}
    master_records: list = []
    seen_pairs = set()
    registered: dict = {}
    pass_reports = []
    for p in range(n_passes):
        n_with_teacher, n_credited, n_no_anchor, n_cfe, records = run_pass_pos(goal_windows)
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


# ================================================================== contextual-cleanliness measurement (THE proof)
def _denominal_context_audit(windows):
    """THE decisive contextual-cleanliness measurement: for every REAL-CORPUS occurrence of a
    WordNet-admitted denominal noun/verb homograph (AMBIGUOUS_DENOMINAL_CANARY -- words the prior
    cell's OWN disk metrics show its dictionary-membership gate credited), does the CONTEXTUAL tag
    say NOUN (correctly rejected -- WordNet's dictionary gate would have wrongly admitted it) or
    VERB/AUX (correctly kept -- a genuine verb use)? This is measured directly on the real corpus,
    independent of referent-linkage (referent-linkage is a further, separate filter on TOP of the
    candidate gate; this measures the gate's raw contextual precision on the ambiguous vocabulary)."""
    per_word: dict = {}
    n_total = 0
    n_pos_admits = 0
    n_pos_rejects = 0
    sample_rejects = []
    sample_admits = []
    for goal_sentence, window_text, desired_referent in windows:
        toks, tags = _pos_tags_for_window(window_text)
        for idx, tok in enumerate(toks):
            if tok not in AMBIGUOUS_DENOMINAL_CANARY:
                continue
            n_total += 1
            d = per_word.setdefault(tok, {"n": 0, "pos_admit": 0, "pos_reject": 0})
            d["n"] += 1
            admitted = tags[idx] in VERB_POS_TAGS
            if admitted:
                n_pos_admits += 1
                d["pos_admit"] += 1
                if len(sample_admits) < 10:
                    sample_admits.append({"tok": tok, "tag": tags[idx], "window": window_text[:120]})
            else:
                n_pos_rejects += 1
                d["pos_reject"] += 1
                if len(sample_rejects) < 10:
                    sample_rejects.append({"tok": tok, "tag": tags[idx], "window": window_text[:120]})
    return {
        "n_total_occurrences": n_total,
        "n_wordnet_would_admit": n_total,  # WordNet is_verb(w) True for every AMBIGUOUS_DENOMINAL_CANARY word by construction
        "n_pos_contextually_admits": n_pos_admits,
        "n_pos_contextually_rejects": n_pos_rejects,
        "pos_reject_rate": round(n_pos_rejects / n_total, 4) if n_total else None,
        "per_word": per_word,
        "sample_rejects": sample_rejects,
        "sample_admits": sample_admits,
    }


# ================================================================== calibration table (reported)
def _tagger_calibration_table():
    """Contextual spot-check on hand-authored noun-use / verb-use sentence pairs for EVERY
    AMBIGUOUS_DENOMINAL_CANARY word (TEST-FIRST VALIDATION, run + reported before this module's
    self_test is trusted; the exact task-brief-named cases -- 'the paper'/'the table'/'his father' vs
    'they paper the wall' -- are included). Reported honestly (hits AND misses)."""
    pairs = {
        "father": ("his father was kind", "father", "they father many children", "father"),
        "house": ("the house was big", "house", "they house the refugees", "house"),
        "man": ("the man walked away", "man", "they man the station", "man"),
        "table": ("the table was old", "table", "they table the motion", "table"),
        "paper": ("the paper was on the table", "paper", "they paper the wall", "paper"),
        "witch": ("the witch cackled", "witch", "they witch for water", "witch"),
        "book": ("she read the book", "book", "they will book the room", "book"),
        "arm": ("she hurt her arm", "arm", "he will arm the soldiers", "arm"),
        "hat": ("he wore a hat", "hat", "they will hat the scarecrow", "hat"),
        "cap": ("she wore a cap", "cap", "they will cap the well", "cap"),
        "back": ("he hurt his back", "back", "they will back the car", "back"),
    }
    out = {}
    n_correct = 0
    n_total = 0
    for word, (noun_sent, tgt, verb_sent, tgt2) in pairs.items():
        n_toks, n_tags = _pos_tags_for_window(noun_sent)
        v_toks, v_tags = _pos_tags_for_window(verb_sent)
        n_idx = n_toks.index(tgt)
        v_idx = v_toks.index(tgt2)
        noun_tag = n_tags[n_idx]
        verb_tag = v_tags[v_idx]
        noun_ok = noun_tag not in VERB_POS_TAGS
        verb_ok = verb_tag in VERB_POS_TAGS
        n_correct += int(noun_ok) + int(verb_ok)
        n_total += 2
        out[word] = {"noun_sentence": noun_sent, "noun_tag": noun_tag, "noun_correctly_rejected": noun_ok,
                     "verb_sentence": verb_sent, "verb_tag": verb_tag, "verb_correctly_admitted": verb_ok}
    out["summary"] = {"n_correct": n_correct, "n_total": n_total,
                      "frac_correct": round(n_correct / n_total, 4)}
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

    # ---- UNIT 2: OLD naive baseline reproduction (unmodified engine learn_corpus) -----------------
    if unit_key("old_naive", run_mode) not in completed_units(output_dir):
        print("[progress] OLD naive baseline reproduction (lemma_verb candidate gate, unmodified engine)", flush=True)
        old_rep = _engine_learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                                       credit_mode="referent_linked", register=False)
        clear_acquired_outcome()
        old_clean = _verb_cleanliness(old_rep["master_records"])
        record_unit(output_dir, unit_key("old_naive", run_mode), {
            "registered": old_rep["registered"], "master_records": old_rep["master_records"],
            "cleanliness": old_clean,
        })
        print(f"[progress] OLD_NAIVE: n_registered={len(old_rep['registered'])} "
              f"cleanliness={old_clean['cleanliness']} n_exposures={old_clean['n_exposures']}", flush=True)
    old_u = load_units(output_dir)[unit_key("old_naive", run_mode)]

    # ---- UNIT 3: WORDNET_GATE positive control (Gate D -- reproduces the prior cell verbatim) ------
    if unit_key("wordnet_gate", run_mode) not in completed_units(output_dir):
        print("[progress] WORDNET_GATE positive control (dictionary-membership is_verb, reproduced from prior cell)", flush=True)
        wn_rep = learn_corpus_wordnet(windows, n_passes=N_PASSES, register=True)
        wn_registered = wn_rep["registered"]
        wn_acc, wn_correct, wn_met_c, wn_unmet_c, wn_n_met, wn_n_unmet, _wn_details = _score_with_overlay(oov_rows, wn_registered)
        wn_clean = _verb_cleanliness(wn_rep["master_records"])
        wn_scr = _scramble_control_weighted(wn_rep["master_records"], oov_rows)
        record_unit(output_dir, unit_key("wordnet_gate", run_mode), {
            "registered": wn_registered, "master_records": wn_rep["master_records"],
            "primary_accuracy": round(wn_acc, 4), "cleanliness": wn_clean, "scramble": wn_scr,
        })
        print(f"[progress] WORDNET_GATE: primary_acc={wn_acc:.4f} n_registered={len(wn_registered)} "
              f"cleanliness={wn_clean['cleanliness']}", flush=True)
    wn_u = load_units(output_dir)[unit_key("wordnet_gate", run_mode)]

    # ---- UNIT 4: POS_GATE (THE FIX, + kept FIX 1 clause-anchor + FIX 2 weight) --------------------
    if unit_key("pos_gate", run_mode) not in completed_units(output_dir):
        print("[progress] POS_GATE learn (contextual tagger.tag candidates, clause-anchored, selectional-weighted)", flush=True)
        pos_rep = learn_corpus_pos(windows, n_passes=N_PASSES, register=True)
        registered = pos_rep["registered"]
        acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, registered)
        learnable = _learnable_subset(oov_rows, registered)
        pos_clean = _verb_cleanliness(pos_rep["master_records"])
        record_unit(output_dir, unit_key("pos_gate", run_mode), {
            "registered": registered, "master_records": pos_rep["master_records"],
            "master_grounded": pos_rep["master_grounded"], "pass_reports": pos_rep["pass_reports"],
            "primary_accuracy": round(acc, 4), "primary_correct": correct,
            "met_recall_correct": met_c, "met_total": n_met,
            "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
            "learnable": learnable, "cleanliness": pos_clean,
        })
        print(f"[progress] POS_GATE: primary_acc={acc:.4f} n_registered={len(registered)} "
              f"cleanliness={pos_clean['cleanliness']} n_learnable={learnable['n_learnable']}", flush=True)
    pos_u = load_units(output_dir)[unit_key("pos_gate", run_mode)]

    # ---- UNIT 5: baseline (empty overlay) ---------------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        clear_acquired_outcome()
        b_acc, b_correct = _score(oov_rows)[0:2]
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"fallthrough_baseline_accuracy": round(b_acc, 4), "fallthrough_correct": b_correct})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 6: weighted scramble control (5 seeds) on the POS_GATE exposures --------------------
    if unit_key("scramble_pos", run_mode) not in completed_units(output_dir):
        print("[progress] weighted scramble control on POS_GATE (5 seeds)", flush=True)
        scr = _scramble_control_weighted(pos_u["master_records"], oov_rows)
        record_unit(output_dir, unit_key("scramble_pos", run_mode), scr)
    scr_u = load_units(output_dir)[unit_key("scramble_pos", run_mode)]

    # ---- UNIT 7: denominal-noun contextual audit on the real corpus (THE decisive cleanliness proof)
    if unit_key("denominal_audit", run_mode) not in completed_units(output_dir):
        print("[progress] denominal-noun contextual audit (real corpus)", flush=True)
        audit = _denominal_context_audit(windows)
        record_unit(output_dir, unit_key("denominal_audit", run_mode), audit)
        print(f"[progress] denominal_audit: n_total={audit['n_total_occurrences']} "
              f"n_pos_rejects={audit['n_pos_contextually_rejects']} "
              f"reject_rate={audit['pos_reject_rate']}", flush=True)
    audit_u = load_units(output_dir)[unit_key("denominal_audit", run_mode)]

    return _aggregate(run_mode, oov_rows, majority_floor, corpus_u, old_u, wn_u, pos_u, base_u, scr_u, audit_u)


def _aggregate(run_mode, oov_rows, majority_floor, corpus_u, old_u, wn_u, pos_u, base_u, scr_u, audit_u):
    primary = pos_u["primary_accuracy"]
    scrambled = scr_u["scrambled_primary_accuracy"]
    lift = (round(primary - scrambled, 4) if scrambled is not None else None)
    learnable = pos_u["learnable"]
    integ = corpus_u["exclusion_integrity"]

    def _digest(reg):
        return hashlib.sha256(json.dumps(sorted(reg.items())).encode()).hexdigest()
    d_old, d_wn, d_pos = _digest(old_u["registered"]), _digest(wn_u["registered"]), _digest(pos_u["registered"])
    arms_differ = {"old_vs_wordnet": d_old != d_wn, "old_vs_pos": d_old != d_pos, "wordnet_vs_pos": d_wn != d_pos}
    arms_differ_verified = all(arms_differ.values())

    tagger_calibration = _tagger_calibration_table()
    wn_clean = wn_u["cleanliness"]
    pos_clean = pos_u["cleanliness"]
    cleanliness_delta_vs_wordnet = (round(pos_clean["cleanliness"] - wn_clean["cleanliness"], 4)
                                    if (wn_clean["cleanliness"] is not None and pos_clean["cleanliness"] is not None)
                                    else None)

    # Gate D positive control: WORDNET_GATE arm reproduction of the cited prior cell's disk numbers.
    wn_primary = wn_u["primary_accuracy"]
    wn_lift = (round(wn_primary - wn_u["scramble"]["scrambled_primary_accuracy"], 4)
              if wn_u["scramble"]["scrambled_primary_accuracy"] is not None else None)
    gate_d_primary_ok = abs(wn_primary - GATE_D_CITED_PRIMARY) <= GATE_D_TOLERANCE
    gate_d_lift_ok = (wn_lift is not None) and abs(wn_lift - GATE_D_CITED_SCRAMBLE_LIFT) <= GATE_D_TOLERANCE
    gate_d_reproduces = gate_d_primary_ok and gate_d_lift_ok

    # denominal canary: which AMBIGUOUS_DENOMINAL_CANARY words did each arm actually REGISTER?
    denom_in_wordnet = sorted(w for w in AMBIGUOUS_DENOMINAL_CANARY if w in wn_u["registered"])
    denom_in_pos = sorted(w for w in AMBIGUOUS_DENOMINAL_CANARY if w in pos_u["registered"])

    agg = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "config": {"N_PASSES": N_PASSES, "MIN_CONFIRM": MIN_CONFIRM, "NEUTRAL_BAND": NEUTRAL_BAND,
                   "n_scramble_seeds": N_SCRAMBLE_SEEDS, "n_oov_items": len(oov_rows),
                   "LIGHT_LEXNAME_BREADTH": LIGHT_LEXNAME_BREADTH, "LIGHT_SENSE_COUNT": LIGHT_SENSE_COUNT,
                   "LIGHT_VERB_WEIGHT": LIGHT_VERB_WEIGHT, "LOADED_VERB_WEIGHT": LOADED_VERB_WEIGHT,
                   "scramble_lift_hard_pass": SCRAMBLE_LIFT_HARD_PASS,
                   "scramble_lift_no_signal": SCRAMBLE_LIFT_NO_SIGNAL,
                   "pos_model_path": POS_MODEL_PATH, "verb_pos_tags": sorted(VERB_POS_TAGS)},
        "corpus_stats": corpus_u["corpus_stats"], "win_stats": corpus_u["win_stats"],
        "exclusion_integrity": integ,
        "majority_floor": majority_floor,
        "fallthrough_baseline_accuracy": base_u["fallthrough_baseline_accuracy"],
        "primary_accuracy": primary,
        "primary_minus_floor": round(primary - majority_floor, 4),
        "met_recall": f"{pos_u['met_recall_correct']}/{pos_u['met_total']}",
        "unmet_recall": f"{pos_u['unmet_recall_correct']}/{pos_u['unmet_total']}",
        "n_registered_old_naive": len(old_u["registered"]), "old_naive_registered": old_u["registered"],
        "n_registered_wordnet_gate": len(wn_u["registered"]), "wordnet_gate_registered": wn_u["registered"],
        "n_registered_pos_gate": len(pos_u["registered"]), "pos_gate_registered": pos_u["registered"],
        "learnable_subset": learnable,
        "bootstrap_curve": pos_u["pass_reports"],
        "scramble": scr_u, "scramble_lift": lift,
        "wordnet_gate_primary_accuracy": wn_primary, "wordnet_gate_scramble": wn_u["scramble"],
        "wordnet_gate_scramble_lift": wn_lift,
        "gate_d_positive_control": {
            "cited_primary": GATE_D_CITED_PRIMARY, "measured_primary": wn_primary,
            "cited_scramble_lift": GATE_D_CITED_SCRAMBLE_LIFT, "measured_scramble_lift": wn_lift,
            "tolerance": GATE_D_TOLERANCE, "primary_ok": gate_d_primary_ok, "lift_ok": gate_d_lift_ok,
            "reproduces": gate_d_reproduces,
        },
        "cleanliness_old_naive": old_u["cleanliness"], "cleanliness_wordnet_gate": wn_clean,
        "cleanliness_pos_gate": pos_clean, "cleanliness_delta_pos_vs_wordnet": cleanliness_delta_vs_wordnet,
        "garbage_canary": GARBAGE_CANARY,
        "denominal_canary": AMBIGUOUS_DENOMINAL_CANARY,
        "denominal_canary_present_in_wordnet_gate_registered": denom_in_wordnet,
        "denominal_canary_present_in_pos_gate_registered": denom_in_pos,
        "denominal_context_audit": audit_u,
        "tagger_calibration_table": tagger_calibration,
        "arms_differ": arms_differ, "arms_differ_verified": arms_differ_verified,
        "calibration_table": _calibration_table(),
    }

    scramble_collapses = (lift is not None and lift >= SCRAMBLE_LIFT_HARD_PASS)
    scramble_no_signal = (lift is not None and lift <= SCRAMBLE_LIFT_NO_SIGNAL)
    primary_above_floor = (primary >= majority_floor)
    cleanliness_improved = (cleanliness_delta_vs_wordnet is not None and cleanliness_delta_vs_wordnet > 0)
    denominal_audit_fires = audit_u["n_total_occurrences"] > 0

    hard_fail_reasons = []
    if scramble_no_signal:
        hard_fail_reasons.append("SCRAMBLE_STILL_DOES_NOT_COLLAPSE_signal_still_does_not_carry")
    if not arms_differ_verified:
        hard_fail_reasons.append("ARMS_IDENTICAL_META_RULE_AF")
    if not gate_d_reproduces:
        hard_fail_reasons.append("GATE_D_POSITIVE_CONTROL_DOES_NOT_REPRODUCE_PRIOR_CELL")

    hard_pass = scramble_collapses and primary_above_floor and arms_differ_verified and gate_d_reproduces

    if hard_pass and not hard_fail_reasons:
        verdict = "HARD_PASS"
    elif hard_fail_reasons:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    agg["gate_detail"] = {
        "SCRAMBLE_COLLAPSES_lift>=0.10": scramble_collapses,
        "PRIMARY_ABOVE_FLOOR": primary_above_floor,
        "ARMS_DIFFER": arms_differ_verified,
        "SCRAMBLE_NO_SIGNAL_lift<=0.05": scramble_no_signal,
        "CLEANLINESS_IMPROVED_VS_WORDNET": cleanliness_improved,
        "GATE_D_REPRODUCES": gate_d_reproduces,
        "DENOMINAL_AUDIT_FIRES": denominal_audit_fires,
        "hard_fail_reasons": hard_fail_reasons,
    }
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: primary={primary:.4f} (floor={majority_floor}, delta={agg['primary_minus_floor']}) | "
        f"scrambled={scrambled} lift={lift} (hard_pass>={SCRAMBLE_LIFT_HARD_PASS}, "
        f"no_signal<={SCRAMBLE_LIFT_NO_SIGNAL}) | prior_wordnet_gate_lift={GATE_D_CITED_SCRAMBLE_LIFT} | "
        f"gate_d_reproduces={gate_d_reproduces} (measured_wn_lift={wn_lift}) | "
        f"cleanliness wordnet_gate={wn_clean['cleanliness']} pos_gate={pos_clean['cleanliness']} "
        f"delta={cleanliness_delta_vs_wordnet} | "
        f"denominal_audit: n_occurrences={audit_u['n_total_occurrences']} "
        f"pos_reject_rate={audit_u['pos_reject_rate']} | "
        f"denom_in_wordnet_registered={denom_in_wordnet} denom_in_pos_registered={denom_in_pos} | "
        f"n_registered old_naive={len(old_u['registered'])} wordnet_gate={len(wn_u['registered'])} "
        f"pos_gate={len(pos_u['registered'])} | "
        f"arms_differ={arms_differ_verified} | hard_fail_reasons={hard_fail_reasons}")
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
    expected_n_units = 7  # corpus, old_naive, wordnet_gate, pos_gate, baseline, scramble_pos, denominal_audit
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
    """(1) TEST-FIRST VALIDATION: tagger loads + contextually disambiguates EVERY
    AMBIGUOUS_DENOMINAL_CANARY word (noun-use vs verb-use), including the exact task-brief-named
    cases ('the paper'/'the table'/'his father' vs 'they paper the wall'). If the tagger cannot load
    or is degenerate, this fails LOUDLY here (no fabricated fix). (2) _credit_targets_resolving_
    clause_pos on hand-authored micro-episodes -- same structural FIX-1 test as the prior WordNet
    cell, re-derived over the POS-gated pool. (3) THE decisive local proof (2c): a WordNet-admitted
    denominal-noun word ('father') sitting in the SAME clause as a real OOV outcome verb, whose
    OBJECT happens to referent-link -- WordNet-gate wrongly credits it (empirically reproduced here,
    non-circular: this IS the prior cell's own residual bug), POS-gate must NOT. (4) real code path:
    tiny real corpus slice + one real POS-gated pass (F.1, no synthetic-only branch). (5) determinism
    of the POS-gated multi-pass driver (the persisted tagger has no RNG)."""
    # (1) TEST-FIRST VALIDATION: tagger sanity + full denominal-canary contextual disambiguation.
    tagger = _get_tagger()
    assert set(tagger.tags) == {"ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM",
                                "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X"}, (
        f"unexpected tag set, tagger may not have loaded correctly: {tagger.tags}")
    calib = _tagger_calibration_table()
    assert calib["summary"]["n_correct"] == calib["summary"]["n_total"], (
        f"tagger failed to contextually disambiguate {calib['summary']['n_total'] - calib['summary']['n_correct']}"
        f"/{calib['summary']['n_total']} denominal noun/verb spot-checks: {calib}")
    # the exact task-brief-named cases, explicit standalone asserts (not just folded into the loop).
    p_toks, p_tags = _pos_tags_for_window("the paper was on the table")
    assert p_tags[p_toks.index("paper")] == "NOUN", "'the paper' -> paper must tag NOUN"
    assert p_tags[p_toks.index("table")] == "NOUN", "'the table' -> table must tag NOUN"
    f_toks, f_tags = _pos_tags_for_window("his father was kind")
    assert f_tags[f_toks.index("father")] == "NOUN", "'his father' -> father must tag NOUN"
    v_toks, v_tags = _pos_tags_for_window("they paper the wall")
    assert v_tags[v_toks.index("paper")] == "VERB", "'they paper the wall' -> paper must tag VERB"

    # (2) clause-anchored credit over the POS-gated pool: hand-authored windows where a referent-
    # linked OOV verb sits either IN or OUTSIDE the clause congruence_decision resolves the goal
    # against (byte-identical scenario to the prior cell's self_test, re-derived over the POS gate).
    g = "Owen wanted to mend the canoe before the flood came"
    tinker_lemma = verb_lemma("tinkered")
    dwindle_lemma = verb_lemma("dwindled")
    win_same_clause = "Owen tinkered mended the canoe by dawn."
    old_tgts_same = _credit_targets_pos(win_same_clause, "canoe")
    assert tinker_lemma in old_tgts_same, f"sanity: whole-window POS scan should find {tinker_lemma!r}: {old_tgts_same}"
    tgts_same, reason_same = _credit_targets_resolving_clause_pos(g, win_same_clause, "canoe")
    assert tinker_lemma in tgts_same, (
        f"OOV verb in the SAME (only) clause as the resolving verb must be credited: {tgts_same} ({reason_same})")

    win_diff_clause = ("The canoe dwindled in value over the years. "
                       "The men worked all night and mended the canoe by dawn.")
    old_tgts_diff = _credit_targets_pos(win_diff_clause, "canoe")
    new_tgts_diff, reason_diff = _credit_targets_resolving_clause_pos(g, win_diff_clause, "canoe")
    assert dwindle_lemma in old_tgts_diff, f"sanity: whole-window scan should find the bystander OOV verb: {old_tgts_diff}"
    assert dwindle_lemma not in new_tgts_diff, (
        f"clause-anchored scan must EXCLUDE an OOV verb outside the resolving clause: {new_tgts_diff} ({reason_diff})")

    # (3) THE decisive local proof: a WordNet-admitted denominal noun ('father') in the SAME clause
    # as a real OOV outcome verb, whose forward object-scan happens to referent-link to the goal
    # referent -- WordNet-gate (dictionary membership) wrongly credits it (reproduced here from the
    # imported, unmodified _credit_targets_wordnet -- empirically verified before hardening this
    # assert: WORDNET=['father','tinker'], POS=['tinker']). POS-gate must reject 'father' (tagged
    # NOUN in this sentence) while still crediting the genuine verb 'tinker'.
    win_denom = "Nell's father tinkered the canoe."
    wn_tgts_denom = _credit_targets_wordnet(win_denom, "canoe")  # imported, unmodified prior-cell fn
    pos_tgts_denom = _credit_targets_pos(win_denom, "canoe")
    assert "father" in wn_tgts_denom, (
        f"sanity: WordNet-gate (dictionary membership) should wrongly credit the denominal noun "
        f"'father' (WordNet has a verb sense for it): {wn_tgts_denom}")
    assert "father" not in pos_tgts_denom, (
        f"POS-gate must NOT credit 'father' (contextually NOUN in this sentence): {pos_tgts_denom}")
    assert tinker_lemma in pos_tgts_denom, f"POS-gate must still credit the real verb 'tinkered': {pos_tgts_denom}"

    # (4) real code path: tiny real corpus slice, real 3-arg call, one real POS-gated pass.
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV eval items, got {len(oov_rows)}"
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows, _win_stats = _build_windows(blocks[:40], all_rows)
    assert len(windows) > 0, "self-test corpus slice produced zero windows"
    n_wt, n_cred, n_na, n_cfe, recs = run_pass_pos(windows)
    assert n_cred <= n_wt

    # (5) determinism: two independent POS-gated runs over the SAME tiny window list produce
    # byte-identical registered maps (glass-box, persisted-model decode has no hidden RNG).
    r1 = learn_corpus_pos(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    r2 = learn_corpus_pos(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    assert r1["master_grounded"] == r2["master_grounded"], "GLASS-BOX FAILURE: non-deterministic POS-gated grounding"

    clear_acquired_outcome()
    return {
        "tagger_calibration_ok": True, "task_brief_cases_ok": True,
        "clause_anchor_exclusion_ok": True, "denominal_exclusion_ok": True,
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
