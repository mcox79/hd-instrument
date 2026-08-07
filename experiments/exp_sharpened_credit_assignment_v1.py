# CELL-TEMPLATE MANDATORY (isolated LOCAL prove-architecture probe; scope/scale/floor subset):
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - deterministic_seeding: weighted scramble control uses np.random.default_rng(fixed) (5 fixed
#   seeds, 2000+s, byte-identical seed scheme to the parent cell's _scramble_control -- PROT-023
#   compliant, no hash()-seeding). WordNet lexname/sense lookups are deterministic (no RNG).
# - start_marker + crash_diagnostic present; cell_chunked: true (tools/exp_checkpoint per-unit).
# - progress_logging: print(..., flush=True)
# - discriminator-fires gate: n_windows_sharpened_credited must be > 0 (mechanism actually attaches
#   credit to at least one real window) -- checked at smoke.
# - arms_differ_verified: OLD (unweighted, whole-window) vs NEW (sharpened, clause-anchored +
#   selectional-weighted) registered maps compared by sha256 digest in _aggregate (META_RULE_AF).
# - crlb_n/a: no swept capacity dimension; this is a credit-assignment-precision prove-architecture
#   cell (does sharpening make the real-prose teaching signal CARRY), not a capacity envelope.
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- experiments/ only, per Director task brief 2026-08-07 ("BUILD + TEST B Step-2:
#   sharpen credit-assignment").
# - all reported numbers MEASURED@ this cell's metrics.json, tagged in the completion report.
"""experiments/exp_sharpened_credit_assignment_v1.py -- SHARPENED credit-assignment for the OOV
outcome-verb consequence-learning loop (Director task brief 2026-08-07, "BUILD+TEST B Step-2").

THE WALL THIS ANSWERS (Director-VET'd, data/exp_noise_robust_learn_from_exposure_snorkel_v1/
metrics.json, commit fc21752f3): on REAL prose the earn-from-exposure teaching signal does NOT
CARRY -- real primary_accuracy 0.4722 vs scrambled 0.5000 (gap -0.0278; scramble does NOT collapse,
i.e. no real signal), primary 0.4722 < majority floor 0.6389. Coverage was NOT the problem (the
AND-gate teacher fires on 439/1655 real windows). The diagnosed problem is CREDIT-ASSIGNMENT
PRECISION: hdlab.consequence_learning_loop._credit_targets attributes a window's whole-window
MET/UNMET consequence to EVERY OOV outcome-verb whose LOCAL-CLAUSE referent links to the goal
referent anywhere across the (goal + up to 3 following sentences) window -- on real prose that
credits co-occurring LIGHT verbs (and, empirically, some morphological-heuristic non-verb noun-stem
artifacts -- see NOUN_ARTIFACT_CHECK below) alongside the one semantically-loaded verb, diluting the
signal to noise. and_gate_registered from the Snorkel run's own metrics.json contains entries like
"boy"/"sister"/"friend"/"us"/"ad"/"thi"/"noth"/"hop"/"lik"/"alway" -- these are NOT outcome verbs.

TWO SHARPENING FIXES (both structural, reuse-heavy, no new taxonomy):

FIX 1 -- GOAL->OUTCOME RESOLVING-VERB CREDIT (_credit_targets_resolving_clause): instead of
crediting every referent-linked OOV verb ANYWHERE in the window, first ask congruence_decision --
the SAME did-it-happen/congruence machinery that already computes the AND-gate teacher verdict --
WHICH verb it resolved the goal against (its own Pass-1 referent-linked + class-related pick, or the
first-match fallback, returned as detail['actual']). That resolving verb's own CLAUSE (via the SAME
_CB_CLAUSE_BOUNDARY coordinator/subordinator walk hdlab.consequence_learning_loop._credit_targets
already performs internally, exposed here as _clause_bounds and re-run around the DIFFERENT anchor
position congruence_decision resolves to) becomes the load-bearing outcome clause. Credit is
restricted to _credit_targets' own OOV lemma set INTERSECTED with that one clause's tokens -- a
referent-linked OOV verb sitting in an earlier/later sentence of a multi-sentence window, outside the
clause that actually decided MET/UNMET, is no longer credited. _credit_targets itself is called
VERBATIM, unmodified; the intersection is the only new step.

FIX 2 -- RICHER SELECTIONAL-CLASS DOWN-WEIGHT (verb_selectional_weight): a verb whose WordNet
verb-sense inventory spans many distinct lexicographer domains (lexnames) OR is highly polysemous has
a FLAT/GENERIC selectional profile -- a light verb (go/make/take/give/get/have/come/find/see/carry/
put/do/try/want/look/feel measured below). A verb concentrated in few domains with few senses has a
SPECIFIC profile -- a semantically-loaded verb (sink/mend/tinker/dwindle/croak/wither/flourish/
squander measured below). This is the SAME granularity-of-WordNet-class principle proven in
experiments/exp_richer_selectional_context_key_v1.py (commit 0527afeab, finer_wordnet_class: a
flat/broad hypernym-closure class carries less disambiguating information than a narrow one),
applied here to VERBS via lexname-domain breadth + sense count instead of that cell's noun-hypernym
classifier (that cell classifies PATIENT NOUNS; this cell needs a VERB-side generality signal, so a
new, declared, analogous WordNet-based function is built here -- not a literal import, the *method*
is reused, the specific classifier is new). A token with ZERO WordNet verb senses at all (the
morphological _is_verblike/lemma_verb heuristic false-firing on a bare plural-noun stem -- exactly
the "boy"/"sister"/"friend"/"us" artifacts above) is bucketed WITH light verbs: it has no verb
selectional profile to be specific about, the most extreme case of "flat/generic." Down-weighting
(not a hard zero-cut) is implemented via a RAW FLOAT credit weight per exposure (LOADED = 1.0,
byte-identical to the original unweighted +=1-per-exposure scheme; LIGHT = LIGHT_VERB_WEIGHT < 1.0)
accumulated directly into the UNCHANGED, imported hdlab.consequence_learning_loop.consolidate()'s
per-lemma POS/NEG tally, relying on consolidate()'s own `int()` cast at READ time to truncate the
ACCUMULATED total correctly (e.g. 20 LIGHT exposures at 0.15 = 3.0 -> int(3.0) = 3, needing ~1/
LIGHT_VERB_WEIGHT as many exposures as a LOADED verb to clear the same MIN_CONFIRM bar) -- no hdlab/
edit. An earlier draft pre-scaled everything to integer "weight units" via a WEIGHT_SCALE=20 factor;
that was WRONG (it made a SINGLE loaded-verb exposure worth 20 units, instantly clearing MIN_CONFIRM
=3 on one exposure and silently defeating the cross-situational anti-noise gate for EVERY verb, not
just light ones) -- caught by the first smoke run (registered count 14->62, an obvious red flag) and
fixed before the full dispatch; see the completion report and weight_units()'s own docstring below.

THRESHOLDS PRE-COMMITTED (calibrated against the FIXED LIGHT_VERB_CANARY / NOISE_CANARY / a small
hand-picked loaded-verb set from the parent cell's own pre-reg -- see calibration table in the
completion report -- NEVER against this cell's own real-corpus output; non-circularity). The teacher
signal itself (congruence_decision AND-gate, teacher_verdict) is REUSED UNCHANGED -- only WHICH verb
gets credited and HOW MUCH weight it gets are sharpened; the wall diagnosis explicitly named
credit-assignment precision, not coverage or the teacher signal, as the fixable lever.

REUSE (wire-don't-island; hdlab/ is READ-ONLY, never edited):
  hdlab.goal_typing: congruence_decision, lexicon_predict, _tokens, _CB_CLAUSE_BOUNDARY
  hdlab.thematic_role_labeler: lemma_verb
  hdlab.consequence_learning_loop: _credit_targets (VERBATIM, unmodified), consolidate (VERBATIM),
    teacher_verdict (VERBATIM, AND-gate teacher signal unchanged), learn_corpus (OLD baseline
    reproduction, unmodified), MIN_CONFIRM, NEUTRAL_BAND
  hdlab.verb_lexical_similarity: register_acquired_outcome, clear_acquired_outcome
  experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1: the proven corpus-reader /
    window-builder / eval-loader / scorer (_load_eval, _read_corpus_blocks, _build_windows,
    _exclusion_integrity, _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS,
    N_SCRAMBLE_SEEDS, LIGHT_VERB_CANARY, NOISE_CANARY) -- reused VERBATIM, same pattern the Snorkel
    cell (exp_noise_robust_learn_from_exposure_snorkel_v1.py) and the signal_a_primary cell already
    established, so every coverage/scoring number below is measured on the EXACT SAME 1655 real
    windows / 36-item OOV eval bank the HARD_FAIL cell's numbers came from.

GENUINELY-NEW code here (declared, thin, non-circular): _clause_bounds, _credit_targets_resolving_
clause (FIX 1), verb_selectional_weight / weight_units (FIX 2), run_pass_sharpened /
learn_corpus_sharpened (multi-pass driver, architecturally identical to hdlab.consequence_learning_
loop.learn_corpus -- same MIN_CONFIRM/NEUTRAL_BAND consolidation via the imported unmodified
`consolidate`, same (window_id,lemma) first-verdict-wins master tally, same Tier-3 register-and-reread
bootstrap loop -- the ONLY changes are the credit-target source and the per-exposure weight),
_scramble_control_weighted (thin adaptation of the parent cell's _scramble_control: identical fixed
seeds/permutation structure, only the tally increment is weight-aware instead of a fixed +1).

Prior-work check (mandatory substrate-KB gate before authoring): `bash tools/substrate_query.sh
"sharpen credit assignment goal outcome resolving verb clause anchor light verb selectional
specificity down-weight consequence learning"` -- top hit cosine=0.2939 (the base consequence-
learning-loop design note, its own direct ancestor/expected prior context), all 5 returned hits below
cosine 0.30. Prior-work check: NONE at cosine>0.30 for THIS specific sharpening combination --
genuinely novel build in this substrate, not a rediscovery (the base loop it sharpens is, correctly,
the nearest prior work and is cited throughout above).

Cites: data/exp_noise_robust_learn_from_exposure_snorkel_v1/metrics.json (the measured wall this
cell answers); hdlab/consequence_learning_loop.py (the engine being sharpened);
experiments/exp_richer_selectional_context_key_v1.py commit 0527afeab (the finer-WordNet-class
method FIX 2 extends to verbs); experiments/exp_consequence_learning_loop_oov_outcome_verb_valence_v1.py
(the corpus/scoring infra reused verbatim).
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

from hdlab.goal_typing import congruence_decision, _tokens, _CB_CLAUSE_BOUNDARY  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab import verb_lexical_similarity as _vls  # noqa: E402
from hdlab.verb_lexical_similarity import register_acquired_outcome, clear_acquired_outcome  # noqa: E402
from hdlab.consequence_learning_loop import (  # noqa: E402
    _credit_targets, consolidate, teacher_verdict, learn_corpus as _engine_learn_corpus,
    MIN_CONFIRM, NEUTRAL_BAND, N_PASSES_DEFAULT,
)
from nltk.corpus import wordnet as wn  # noqa: E402

# REUSE the parent cell's validated corpus/scoring helpers verbatim (wire-don't-island; same pattern
# the Snorkel cell already established).
from experiments.exp_consequence_learning_loop_oov_outcome_verb_valence_v1 import (  # noqa: E402
    _load_eval, _read_corpus_blocks, _build_windows, _exclusion_integrity,
    _score, _score_with_overlay, _learnable_subset, NOVELS, SMOKE_NOVELS, N_SCRAMBLE_SEEDS,
    LIGHT_VERB_CANARY, NOISE_CANARY,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

ANCHOR_NAME = "sharpened_credit_assignment_v1"
OUTPUT_DIR_FULL = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

N_PASSES = N_PASSES_DEFAULT  # 3, matches the engine's own bootstrap depth

# ---- FIX 2 config (PRE-COMMITTED before this cell was ever run against the real corpus; calibrated
# against LIGHT_VERB_CANARY / NOISE_CANARY / a small hand-picked loaded-verb set only) -------------
LIGHT_LEXNAME_BREADTH = 5      # >= this many distinct WordNet verb lexnames -> flat/generic (light)
LIGHT_SENSE_COUNT = 15         # >= this many WordNet verb senses -> flat/generic (light)
LIGHT_VERB_WEIGHT = 0.15       # raw float credit weight per LIGHT exposure (LOADED = 1.0, unscaled)
LOADED_VERB_WEIGHT = 1.0

# ---- can-fail bands (PRE-COMMITTED per task brief; "lift >= ~0.10" taken literally) ---------------
SCRAMBLE_LIFT_HARD_PASS = 0.10
SCRAMBLE_LIFT_NO_SIGNAL = 0.05     # <= this -> HARD_FAIL, signal still doesn't carry


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


# ================================================================== FIX 1: clause-anchored credit
def _clause_bounds(toks, idx):
    """Token-index clause span [start, end] inclusive around idx, bounded by _CB_CLAUSE_BOUNDARY --
    IDENTICAL walk to the one hdlab.consequence_learning_loop._credit_targets performs internally per
    candidate, exposed here so it can be re-run around the DIFFERENT anchor position congruence_
    decision's own 'actual' resolves to."""
    cl_start = idx
    while cl_start > 0 and toks[cl_start - 1] not in _CB_CLAUSE_BOUNDARY:
        cl_start -= 1
    cl_end = idx
    while cl_end < len(toks) - 1 and toks[cl_end + 1] not in _CB_CLAUSE_BOUNDARY:
        cl_end += 1
    return cl_start, cl_end


def _credit_targets_resolving_clause(goal_sentence, window_text, desired_referent):
    """FIX 1. Returns (sharpened_lemma_list, reason). reason in {"no_teacher","no_anchor",
    "no_whole_window_targets","clause_filtered_to_empty","sharpened"} -- reported for honest
    diagnostics (how much attrition each stage causes)."""
    verdict, detail = congruence_decision([goal_sentence], window_text)
    if verdict not in ("MET", "UNMET"):
        return [], "no_teacher"
    actual = detail.get("actual") if isinstance(detail, dict) else None
    if not actual or actual.get("verb_idx") is None:
        return [], "no_anchor"
    whole_window_targets = set(_credit_targets(window_text, desired_referent))
    if not whole_window_targets:
        return [], "no_whole_window_targets"
    toks = _tokens(window_text)
    a_start, a_end = _clause_bounds(toks, actual["verb_idx"])
    clause_lemmas = {lemma_verb(t) for t in toks[a_start:a_end + 1]}
    sharpened = sorted(whole_window_targets & clause_lemmas)
    return sharpened, ("sharpened" if sharpened else "clause_filtered_to_empty")


# ================================================================== FIX 2: selectional down-weight
_verb_wn_cache: dict = {}


def verb_selectional_weight(lemma):
    """See module docstring FIX 2. Deterministic (WordNet lookups only, no RNG); memoized."""
    if lemma in _verb_wn_cache:
        return _verb_wn_cache[lemma]
    syns = wn.synsets(lemma, pos=wn.VERB)
    if not syns:
        w = LIGHT_VERB_WEIGHT
    else:
        n_lex = len({s.lexname() for s in syns})
        n_sense = len(syns)
        w = (LIGHT_VERB_WEIGHT if (n_lex >= LIGHT_LEXNAME_BREADTH or n_sense >= LIGHT_SENSE_COUNT)
             else LOADED_VERB_WEIGHT)
    _verb_wn_cache[lemma] = w
    return w


def weight_units(lemma):
    """Raw float credit weight for one exposure of `lemma` (1.0 for LOADED, LIGHT_VERB_WEIGHT for
    LIGHT). NOT pre-scaled to an integer: consolidate() (imported unmodified) does `int(votes.get(
    "POS"/"NEG", 0))` on the ACCUMULATED per-lemma total at read time, so a running float sum
    truncates correctly there (e.g. 20 LIGHT exposures at 0.15 = 3.0 -> int(3.0) = 3, clears
    MIN_CONFIRM exactly like 3 raw LOADED exposures at weight 1.0 would) -- LOADED verbs reproduce
    the ORIGINAL unweighted +=1-per-exposure semantics byte-for-byte (weight 1.0), so MIN_CONFIRM's
    'at least 3 INDEPENDENT exposures' anti-noise gate is preserved for loaded verbs and only LIGHT
    verbs need proportionally more (~1/LIGHT_VERB_WEIGHT) exposures to consolidate. PRE-SCALING this
    to integer units (an earlier draft's WEIGHT_SCALE=20 design) was WRONG and is not used: it made
    a SINGLE loaded-verb exposure worth 20 units, instantly clearing MIN_CONFIRM=3 on one exposure
    and inflating registered-word count 14->62 on the smoke slice -- caught by first smoke run,
    fixed before the full dispatch (see completion report)."""
    return verb_selectional_weight(lemma)


def is_loaded(lemma):
    """True iff lemma classifies LOADED (not light, not zero-WordNet-verb-sense)."""
    return verb_selectional_weight(lemma) >= LOADED_VERB_WEIGHT


# ================================================================== sharpened multi-pass driver
def run_pass_sharpened(goal_windows):
    """One corpus pass. Returns (n_with_teacher, n_credited, n_no_anchor, n_clause_filtered_to_empty,
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
        targets, reason = _credit_targets_resolving_clause(goal_sentence, window_text, desired_referent)
        if reason == "no_anchor":
            n_no_anchor += 1
        elif reason == "clause_filtered_to_empty":
            n_clause_filtered_to_empty += 1
        if not targets:
            continue
        n_credited += 1
        for lemma in targets:
            exposure_records.append({"lemma": lemma, "window_id": wid, "teacher_verdict": tv,
                                      "weight_units": weight_units(lemma),
                                      "loaded": is_loaded(lemma)})
    return n_with_teacher, n_credited, n_no_anchor, n_clause_filtered_to_empty, exposure_records


def learn_corpus_sharpened(goal_windows, n_passes=N_PASSES, register=True):
    """Multi-pass bootstrap driver, architecturally identical to hdlab.consequence_learning_loop.
    learn_corpus (same MIN_CONFIRM/NEUTRAL_BAND consolidation via the imported unmodified
    `consolidate`, same (window_id,lemma) first-verdict-wins master tally, same Tier-3 register-and-
    reread bootstrap loop) -- the ONLY changes: credit targets come from _credit_targets_resolving_
    clause (FIX 1) and each exposure increments the tally by weight_units(lemma) (FIX 2) instead of a
    flat +1."""
    clear_acquired_outcome()
    master: dict = {}
    master_records: list = []
    seen_pairs = set()
    registered: dict = {}
    pass_reports = []
    for p in range(n_passes):
        n_with_teacher, n_credited, n_no_anchor, n_cfe, records = run_pass_sharpened(goal_windows)
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
    """Thin adaptation of the parent cell's _scramble_control: identical fixed seeds (2000+s) and
    permutation structure; the ONLY change is the tally increment uses rec['weight_units'] instead of
    a flat +1, so the scramble control operates under the SAME weighting the real run does."""
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


# ================================================================== attribution-precision measurement
def _attribution_precision(master_records):
    """Fraction of credited EXPOSURES (not unique lemmas -- reflects how often dilution actually
    happens) whose lemma classifies LOADED per verb_selectional_weight. Reported alongside a manual
    hand-check in the completion report (this function is the automated half)."""
    if not master_records:
        return {"n_exposures": 0, "n_loaded": 0, "precision": None, "loaded_lemmas": [], "light_lemmas": []}
    n_loaded = sum(1 for r in master_records if r.get("loaded", is_loaded(r["lemma"])))
    loaded_lemmas = sorted({r["lemma"] for r in master_records if r.get("loaded", is_loaded(r["lemma"]))})
    light_lemmas = sorted({r["lemma"] for r in master_records if not r.get("loaded", is_loaded(r["lemma"]))})
    return {"n_exposures": len(master_records), "n_loaded": n_loaded,
            "precision": round(n_loaded / len(master_records), 4),
            "loaded_lemmas": loaded_lemmas, "light_lemmas": light_lemmas}


def _attribution_precision_old(old_master_records):
    """Same measurement applied to the OLD (unweighted, whole-window) engine's exposure records --
    old records have no 'weight_units'/'loaded' key, so classify lemma directly."""
    if not old_master_records:
        return {"n_exposures": 0, "n_loaded": 0, "precision": None, "loaded_lemmas": [], "light_lemmas": []}
    n_loaded = sum(1 for r in old_master_records if is_loaded(r["lemma"]))
    loaded_lemmas = sorted({r["lemma"] for r in old_master_records if is_loaded(r["lemma"])})
    light_lemmas = sorted({r["lemma"] for r in old_master_records if not is_loaded(r["lemma"])})
    return {"n_exposures": len(old_master_records), "n_loaded": n_loaded,
            "precision": round(n_loaded / len(old_master_records), 4),
            "loaded_lemmas": loaded_lemmas, "light_lemmas": light_lemmas}


# ================================================================== calibration self-check (reported)
def _calibration_table():
    """WordNet-classifier calibration against the FIXED canary lists (pre-committed, never against
    this cell's own real-corpus output). Reported honestly (hits AND misses)."""
    loaded_examples = ["sink", "mend", "tinker", "dwindle", "croak", "squander", "flourish", "wither", "ruin"]
    out = {"light_verb_canary": {}, "noise_canary": {}, "loaded_examples": {}}
    for w in LIGHT_VERB_CANARY:
        out["light_verb_canary"][w] = {"weight": verb_selectional_weight(w), "loaded": is_loaded(w)}
    for w in NOISE_CANARY:
        out["noise_canary"][w] = {"weight": verb_selectional_weight(w), "loaded": is_loaded(w)}
    for w in loaded_examples:
        out["loaded_examples"][w] = {"weight": verb_selectional_weight(w), "loaded": is_loaded(w)}
    n_light_canary_correctly_downweighted = sum(1 for v in out["light_verb_canary"].values() if not v["loaded"])
    n_loaded_examples_correctly_loaded = sum(1 for v in out["loaded_examples"].values() if v["loaded"])
    out["summary"] = {
        "light_canary_correctly_downweighted": f"{n_light_canary_correctly_downweighted}/{len(LIGHT_VERB_CANARY)}",
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

    # ---- UNIT 2: OLD baseline reproduction (unweighted, whole-window _credit_targets, unmodified
    # engine learn_corpus) -- the exact same AND-gate/referent-linked reproduction the parent + Snorkel
    # cells already measured HARD_FAIL, for an apples-to-apples before/after comparison. -------------
    if unit_key("old_baseline", run_mode) not in completed_units(output_dir):
        print("[progress] OLD baseline reproduction (unmodified engine, whole-window credit)", flush=True)
        old_rep = _engine_learn_corpus(windows, n_passes=N_PASSES, signal_mode="and_gate",
                                       credit_mode="referent_linked", register=False)
        clear_acquired_outcome()
        old_precision = _attribution_precision_old(old_rep["master_records"])
        record_unit(output_dir, unit_key("old_baseline", run_mode), {
            "registered": old_rep["registered"], "master_records": old_rep["master_records"],
            "attribution_precision": old_precision,
        })
        print(f"[progress] OLD: n_registered={len(old_rep['registered'])} "
              f"attribution_precision={old_precision['precision']}", flush=True)
    old_u = load_units(output_dir)[unit_key("old_baseline", run_mode)]

    # ---- UNIT 3: NEW sharpened run (FIX 1 clause-anchor + FIX 2 selectional weight) --------------
    if unit_key("new_sharpened", run_mode) not in completed_units(output_dir):
        print("[progress] NEW sharpened learn (clause-anchored + selectional-weighted)", flush=True)
        new_rep = learn_corpus_sharpened(windows, n_passes=N_PASSES, register=True)
        registered = new_rep["registered"]
        acc, correct, met_c, unmet_c, n_met, n_unmet, details = _score_with_overlay(oov_rows, registered)
        learnable = _learnable_subset(oov_rows, registered)
        new_precision = _attribution_precision(new_rep["master_records"])
        record_unit(output_dir, unit_key("new_sharpened", run_mode), {
            "registered": registered, "master_records": new_rep["master_records"],
            "master_grounded": new_rep["master_grounded"], "pass_reports": new_rep["pass_reports"],
            "primary_accuracy": round(acc, 4), "primary_correct": correct,
            "met_recall_correct": met_c, "met_total": n_met,
            "unmet_recall_correct": unmet_c, "unmet_total": n_unmet,
            "learnable": learnable, "attribution_precision": new_precision,
        })
        print(f"[progress] NEW: primary_acc={acc:.4f} n_registered={len(registered)} "
              f"attribution_precision={new_precision['precision']} "
              f"n_learnable={learnable['n_learnable']}", flush=True)
    new_u = load_units(output_dir)[unit_key("new_sharpened", run_mode)]

    # ---- UNIT 4: baseline (empty overlay) ---------------------------------------------------------
    if unit_key("baseline", run_mode) not in completed_units(output_dir):
        clear_acquired_outcome()
        b_acc, b_correct = _score(oov_rows)[0:2]
        record_unit(output_dir, unit_key("baseline", run_mode),
                    {"fallthrough_baseline_accuracy": round(b_acc, 4), "fallthrough_correct": b_correct})
    base_u = load_units(output_dir)[unit_key("baseline", run_mode)]

    # ---- UNIT 5: weighted scramble control (5 seeds) on the NEW sharpened exposures --------------
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
        "attribution_precision_old": old_u["attribution_precision"],
        "attribution_precision_new": new_u["attribution_precision"],
        "arms_differ_verified": arms_differ,
        "calibration_table": calibration,
    }

    scramble_collapses = (lift is not None and lift >= SCRAMBLE_LIFT_HARD_PASS)
    scramble_no_signal = (lift is not None and lift <= SCRAMBLE_LIFT_NO_SIGNAL)
    primary_above_floor = (primary >= majority_floor)

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
        "hard_fail_reasons": hard_fail_reasons,
    }
    agg["verdict"] = verdict
    agg["verdict_msg"] = (
        f"{verdict}: primary={primary:.4f} (floor={majority_floor}, delta={agg['primary_minus_floor']}) | "
        f"scrambled={scrambled} lift={lift} (hard_pass>={SCRAMBLE_LIFT_HARD_PASS}, "
        f"no_signal<={SCRAMBLE_LIFT_NO_SIGNAL}) | "
        f"attribution_precision old={old_u['attribution_precision']['precision']} "
        f"new={new_u['attribution_precision']['precision']} | "
        f"n_registered old={len(old_u['registered'])} new={len(new_u['registered'])} | "
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
    expected_n_units = 5  # corpus, old_baseline, new_sharpened, baseline, scramble
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
    """(1) verb_selectional_weight math on hand-known light/loaded examples (no real corpus).
    (2) _clause_bounds / _credit_targets_resolving_clause on hand-authored micro-episodes -- a
    referent-linked OOV verb OUTSIDE the resolving clause must be excluded; one INSIDE it kept.
    (3) real code path: tiny real corpus slice + one real sharpened pass (F.1, no synthetic-only
    branch). (4) determinism of the sharpened multi-pass driver."""
    # (1) selectional weight sanity.
    assert verb_selectional_weight("make") == LIGHT_VERB_WEIGHT, "light-canary 'make' must downweight"
    assert verb_selectional_weight("go") == LIGHT_VERB_WEIGHT, "light-canary 'go' must downweight"
    assert verb_selectional_weight("dwindle") == LOADED_VERB_WEIGHT, "'dwindle' must be loaded"
    assert verb_selectional_weight("sink") == LOADED_VERB_WEIGHT, "'sink' must be loaded"
    assert verb_selectional_weight("zzznonexistentverbxyz") == LIGHT_VERB_WEIGHT, (
        "a token with zero WordNet verb senses must bucket with light (no selectional profile)")
    assert weight_units("dwindle") == LOADED_VERB_WEIGHT
    assert weight_units("make") == LIGHT_VERB_WEIGHT
    assert is_loaded("sink") and not is_loaded("make")

    # (2) clause-anchored credit: hand-authored windows where a referent-linked OOV verb sits either
    # IN or OUTSIDE the clause congruence_decision itself resolves the goal against.
    g = "Owen wanted to mend the canoe before the flood came"
    tinker_lemma = lemma_verb("tinkered")
    dwindle_lemma = lemma_verb("dwindled")
    # 'tinkered' (OOV) sits in the SAME (only) clause as 'mended' (the resolving verb; no
    # _CB_CLAUSE_BOUNDARY token anywhere in this window -- verified: old whole-window scan and the
    # clause-anchored scan must agree here (no false-negative from clause-anchoring).
    win_same_clause = "Owen tinkered mended the canoe by dawn."
    old_tgts_same = _credit_targets(win_same_clause, "canoe")
    assert tinker_lemma in old_tgts_same, f"sanity: whole-window scan should find {tinker_lemma!r}: {old_tgts_same}"
    tgts_same, reason_same = _credit_targets_resolving_clause(g, win_same_clause, "canoe")
    assert tinker_lemma in tgts_same, (
        f"OOV verb in the SAME (only) clause as the resolving verb must be credited: {tgts_same} ({reason_same})")

    # 'dwindled' (OOV) is referent-linked to 'canoe' via a DIFFERENT, EARLIER sentence than the
    # resolving 'mended' clause (separated by an 'and' _CB_CLAUSE_BOUNDARY token) -- whole-window
    # _credit_targets credits it; the clause-anchored sharpened scan must NOT (this is the exact
    # dilution class the fix targets).
    win_diff_clause = ("The canoe dwindled in value over the years. "
                       "The men worked all night and mended the canoe by dawn.")
    old_tgts_diff = _credit_targets(win_diff_clause, "canoe")
    new_tgts_diff, reason_diff = _credit_targets_resolving_clause(g, win_diff_clause, "canoe")
    assert dwindle_lemma in old_tgts_diff, f"sanity: whole-window scan should find the bystander OOV verb: {old_tgts_diff}"
    assert dwindle_lemma not in new_tgts_diff, (
        f"clause-anchored scan must EXCLUDE an OOV verb outside the resolving clause: {new_tgts_diff} ({reason_diff})")

    # (3) real code path: tiny real corpus slice, real 3-arg call, one real sharpened pass.
    all_rows, oov_rows = _load_eval()
    assert len(oov_rows) == 36, f"expected 36 OOV eval items, got {len(oov_rows)}"
    blocks, _stats, _excl = _read_corpus_blocks(all_rows, SMOKE_NOVELS)
    windows, _win_stats = _build_windows(blocks[:40], all_rows)
    assert len(windows) > 0, "self-test corpus slice produced zero windows"
    n_wt, n_cred, n_na, n_cfe, recs = run_pass_sharpened(windows)
    assert n_cred <= n_wt

    # (4) determinism: two independent sharpened runs over the SAME tiny window list produce
    # byte-identical registered maps (glass-box, no hidden RNG).
    r1 = learn_corpus_sharpened(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    r2 = learn_corpus_sharpened(windows, n_passes=2, register=True)
    clear_acquired_outcome()
    assert r1["master_grounded"] == r2["master_grounded"], "GLASS-BOX FAILURE: non-deterministic sharpened grounding"

    clear_acquired_outcome()
    return {
        "selectional_weight_ok": True, "clause_anchor_exclusion_ok": True,
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
