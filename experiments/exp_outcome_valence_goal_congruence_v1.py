"""exp_outcome_valence_goal_congruence_v1 -- brain-faithful OUTCOME-VALENCE (goal-congruence) mechanism
to replace the goal-INDEPENDENT word-lexicon (hdlab/goal_typing.py:84-87 V2_OUTCOME_UNMET/_MET).

WHY (drill spec, notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md, Sections 3+4):
the current lexicon scores "the boat sank" UNMET regardless of whose goal it serves. Three
independent literatures (Scherer/CPM goal-conduciveness, Roseman motive-consistency,
Trabasso causal-network goal-status) converge: the brain computes outcome valence as a
GOAL-CONGRUENCE comparison -- a goal's DESIRED-STATE vs the outcome's ACTUAL-STATE on the SAME
referent -- not as an intrinsic property of the outcome word. The can-fail discriminator: the
SAME outcome word ("sank"/"fell"/"lost"/"won") must flip polarity depending on whether the
antecedent goal wanted that state or its opposite. The lexicon, by construction, cannot do this.

MECHANISM (glass-box, deterministic, no RNG):
  1. Locate the goal's DESIRED-STATE: find a DESIDERATIVE_PASS verb (hdlab.goal_typing, reused
     unmodified), then the first purpose-infinitival "to VERB" after it (DET_STOP reused
     unmodified, same "to VP not to NP" check as action_frame_feats). Two syntactic patterns:
       - CONTROL ("X wanted to VP..."): the embedded VP's logical subject IS the goal-holder
         (control verbs). Referent = the goal-holder itself for SUBJECT_IS_REFERENT verb classes
         (achievement verbs: win/reach/escape/... -- the agent who acts IS the entity whose state
         changes), or the embedded verb's direct object for OBJECT_IS_REFERENT verb classes
         (change-of-state transitives: mend/save/fix/... -- the PATIENT is the entity whose state
         changes, syntactic object notwithstanding).
       - ECM ("X wanted NP to VP..."): an NP sits between the desiderative verb and "to" -- that
         NP (not the matrix subject) is the embedded VP's logical subject/referent, whichever verb
         class governs (this is what makes D-unmet a genuine can-fail case: "wanted his SISTER to
         win" has referent=sister, not owen).
     Result-state class comes from a small hand-authored RESULT_VERB_CLASS register (SUPPLY, not
     induce -- same pattern as goal_typing's DESIDERATIVE_PASS/ASPECTUAL_STOP partition).
  2. Locate the outcome's ACTUAL-STATE: scan the outcome sentence for the first token whose
     lemma (hdlab.thematic_role_labeler.lemma_verb, reused unmodified, tense-normalizes
     sank->sink/won->win/lost->lose/fell->fall) is a member of ANY RESULT_VERB_CLASS; referent =
     that clause's grammatical subject (the rightmost content token before the verb, minus one
     leading determiner/possessive -- handles both "the boat" and "Owen's rival" via a `token
     ends with "'s"` possessive-determiner check).
  3. Congruence: if the actual verb's class doesn't relate (same or opposed pair) to the desired
     class at all, or either referent extraction fails -> ABSTAIN (NA, precision guard; falls
     back to the current lexicon in the wrapper below -- unchanged behavior on non-flip items).
     Else: referents differ -> UNMET (the relevant event happened to/about the WRONG entity, so
     the goal-holder's goal is not satisfied regardless of verb polarity -- this is what D-unmet
     needs: "won" is same-class as "win" but the winner isn't the intended referent). Referents
     match + same/entailing class -> MET. Referents match + class in the OPPOSED pair -> UNMET.

REUSE (already own -- imported unmodified, never re-derived):
  hdlab.goal_typing: DESIDERATIVE_PASS, ASPECTUAL_STOP, OTHER_STOP_UNCHANGED, DET_STOP,
    DIRECTIONAL_PP, V2_OUTCOME_UNMET, V2_OUTCOME_MET (the lexicon being replaced/wrapped).
  hdlab.thematic_role_labeler.lemma_verb (tense normalization).
  hdlab.goal_owner_select: select_outcome_owner (production owner-selector, for the backward-
    compat regression check below), GeneralRecencyEntityResolver + _sentences (sentence split +
    structural subject resolver, reused for the 48-item subset filter).
  hdlab.coreference_resolver.normalize_tokens (lexicon set-membership tokenization, matches the
    existing V2_OUTCOME_UNMET/_MET usage in hdlab/goal_typing.py exactly).
Predictive-coding (hdlab/predictive_coding.py) is NOT imported: its literal numeric
cosine-mismatch residual is the WRONG METRIC for this discrete class-match decision (same ruling
frame_induction.py:27 already made for discrete role decisions -- drill Section 3 "Verdict on
predictive-coding-residual"). Its predict-then-observe SHAPE is exactly what steps 1-3 above
implement; that shape is reused as a DESIGN PATTERN, not a code dependency.

BUILT NEW (small, per drill): RESULT_VERB_CLASS register (REPAIR_PRESERVE/DAMAGE_LOSE/
ARRIVE_SUCCEED/FAIL_LOSE + their two OPPOSED_PAIRS), the desired/actual-state extractors, and the
~3-way congruence decision function.

TEST BANK (drill Section 4, verbatim): experiments/data/outcome_valence_congruence_v1.jsonl --
10 items: A/B/C core flip pairs (6, DAMAGE_LOSE-class), D entity-binding pair (2), H precision-
guard abstain (1), G positive control (1). The 8-item FLIP_SET (A/B/C/D, excludes H and G) is the
HARD-PASS discriminator set.

CONTROLS: LEXICON baseline (current V2_OUTCOME_UNMET/_MET set-membership on the outcome sentence
alone -- the mechanism being replaced, imported unmodified so the comparison is apples-to-apples).
MAJORITY-CLASS baseline (predict the more-frequent gold label on FLIP_SET). SCRAMBLE control
(pair item i's goal-clause with item (i+2)%10's outcome-clause -- offset=2, not offset=1, because
a +1 shift accidentally re-pairs A-unmet/A-met and B-unmet/B-met with their OWN sibling's
identical outcome text ["The boat sank."/"The tree fell." are shared verbatim within each family],
which would silently no-op the scramble for 2/10 items; +2 avoids every same-text coincidence,
verified by inspection of the bank). No hash()-seeded RNG anywhere -- the scramble pairing is a
fixed index arithmetic offset, deterministic across processes.

BACKWARD-COMPAT (mandatory, strict capability ADD): runs the new mechanism (ABSTAIN->lexicon
fallback) across all 62 rows of experiments/data/goal_owner_fair_v1.jsonl to prove it executes
cleanly (no crash, no accidental shared-state mutation from importing/using this module alongside
production hdlab/), and separately re-confirms hdlab.goal_owner_select.select_outcome_owner
(PRODUCTION, completely untouched by this cell) still lands 48/48 on the documented 48-item
primacy+recency-divergent subset. Structural note: select_outcome_owner's scoring
(directed_goal_outcome_score -> GoalOutcomeRegister.appraise) only inspects `has_goal` (whether
ANY GOAL event was written for the outcome-bound entity) -- it never inspects n_unmet/n_met, so a
polarity-only relabeling of OUTCOME_UNMET<->OUTCOME_MET is structurally incapable of changing
owner-selection; this cell verifies that invariant empirically rather than merely asserting it.

PRE-REGISTERED BANDS (notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md Section
"Falsifiable predictions", verbatim):
  HARD-PASS (ALL must hold): mechanism_acc_flip8 >= 0.875 (7/8) AND lexicon_acc_flip8 <= 0.625 AND
    (mechanism_acc_flip8 - lexicon_acc_flip8) >= 0.25 AND scramble collapses (does not retain
    original-pairing accuracy; literal band = within 0.15 of FLIP_SET base rate 0.5, see
    `scramble_collapse_strict`/`scramble_collapse_loose` in metrics for both readings) AND
    H-abstain fires NA (no false MET/UNMET) AND G-control correct AND owner_48_held.
  HARD-FAIL (ANY triggers): mechanism_acc_flip8 < 0.625 OR delta < 0.15 OR NOT scramble_collapse
    OR H false-fires (H does not abstain).
  N=10 is small -> MIDDLE_BAND unless HARD-PASS clears decisively; a 20-30 item follow-up bank is
  needed before production promotion regardless of tier (documented in verdict_msg).

Prior-work check (SUBSTRATE-KB, run before authoring, per exp_dev discipline): `tools/
substrate_query.sh "goal congruence outcome valence result verb class desired state actual state
referent match"` -- top hit cosine=0.3057 (generic entity='state' concept-node match across
verbnet/wordnet/framenet, not a specific mechanism atom). No atom at cosine>0.30 is about a
goal-congruence outcome-valence mechanism specifically. Novel, not a rediscovery (matches the
drill's own KB-check conclusion).

GUARDS: glass-box; fully deterministic (no RNG anywhere in the mechanism -- SEEDS kept as a single
[0] entry purely for exp_checkpoint API/organ-parity convention, results are seed-invariant by
construction); ASCII-only; atomic metrics write (tmp+os.replace); resumable per-unit
(tools/exp_checkpoint.py, two units: flip_set_eval + backward_compat_62); LOCAL-ONLY, in-process
foreground, NOT queue-dispatched, no push; production hdlab/ UNTOUCHED (goal_typing.py /
goal_owner_select.py imported and consumed unmodified only) -- this cell is the PARAMETERIZED
build; promotion to hdlab/goal_typing.py is a VET-time decision, not made here.

Cites: notes/drill_brain_outcome_valence_goal_congruence_2026-08-06.md (full spec, Sections 3+4);
hdlab/goal_typing.py (DESIDERATIVE_PASS/ASPECTUAL_STOP/DET_STOP/DIRECTIONAL_PP/V2_OUTCOME_UNMET/
V2_OUTCOME_MET, PROMOTED, consumed directly); hdlab/goal_owner_select.py (select_outcome_owner/
GeneralRecencyEntityResolver/_sentences, PROMOTED, consumed directly); hdlab/
thematic_role_labeler.py::lemma_verb; experiments/data/goal_owner_fair_v1.jsonl (backward-compat
bank); experiments/exp_c5_multigoal_content_coherence_tiebreak_v1.py (structural cell-template
this cell follows: checkpoint/resume, aggregate/verdict, self_test conventions).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

ANCHOR_NAME = "outcome_valence_goal_congruence_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "outcome_valence_congruence_v1.jsonl")
FAIR_BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_owner_fair_v1.jsonl")

# ---- PROMOTED PRODUCTION ORGANS (WIRE-DON'T-ISLAND: consume hdlab/, unmodified) ----------------
from hdlab.goal_typing import (  # noqa: E402
    DESIDERATIVE_PASS, DET_STOP, DIRECTIONAL_PP, V2_OUTCOME_UNMET, V2_OUTCOME_MET,
)
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
from hdlab.goal_owner_select import (  # noqa: E402
    select_outcome_owner, GeneralRecencyEntityResolver, _sentences,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0]  # mechanism has no RNG; kept as a single-entry list for checkpoint-API/organ-parity only

# ============================================================================ RESULT_VERB_CLASS
# Hand-authored, innate-core physical/social result-state verb typology (SUPPLY, not induce --
# same scope/pattern as hdlab.goal_typing's DESIDERATIVE_PASS/ASPECTUAL_STOP partition). Two
# OPPOSED PAIRS (not one global partition): a change-of-state pair (REPAIR_PRESERVE<->DAMAGE_LOSE)
# and an achievement pair (ARRIVE_SUCCEED<->FAIL_LOSE). "lose"/"fail" deliberately belong to BOTH
# DAMAGE_LOSE and FAIL_LOSE -- general failure verbs that can oppose either a preservation goal or
# an achievement goal depending on which pair the DESIRED verb anchors.
REPAIR_PRESERVE = {"mend", "fix", "repair", "save", "rescue", "protect", "build", "restore"}
DAMAGE_LOSE = {"sink", "break", "fall", "collapse", "lose", "fail", "destroy", "damage", "wreck",
               "crash", "drown", "flood"}
ARRIVE_SUCCEED = {"reach", "escape", "arrive", "win", "succeed"}
FAIL_LOSE = {"lose", "fail", "miss"}

CLASS_REGISTRY = {
    "REPAIR_PRESERVE": REPAIR_PRESERVE, "DAMAGE_LOSE": DAMAGE_LOSE,
    "ARRIVE_SUCCEED": ARRIVE_SUCCEED, "FAIL_LOSE": FAIL_LOSE,
}
OPPOSED_PAIRS = [("REPAIR_PRESERVE", "DAMAGE_LOSE"), ("ARRIVE_SUCCEED", "FAIL_LOSE")]
OPPOSED_OF: dict = {}
for _a, _b in OPPOSED_PAIRS:
    OPPOSED_OF.setdefault(_a, set()).add(_b)
    OPPOSED_OF.setdefault(_b, set()).add(_a)

# Which grammatical position holds the referent for CONTROL-pattern ("X wanted to VP") sentences,
# keyed by the embedded verb's class: achievement verbs (win/reach/...) -- the SUBJECT (agent) is
# who changes state; change-of-state transitives (mend/save/...) -- the OBJECT (patient) is who
# changes state, regardless of syntactic transitivity.
SUBJECT_IS_REFERENT_CLASSES = {"ARRIVE_SUCCEED", "FAIL_LOSE"}
OBJECT_IS_REFERENT_CLASSES = {"REPAIR_PRESERVE", "DAMAGE_LOSE"}


def _verb_classes(lemma: str) -> set:
    return {name for name, members in CLASS_REGISTRY.items() if lemma in members}


def _opposed_of(classes: set) -> set:
    out = set()
    for c in classes:
        out |= OPPOSED_OF.get(c, set())
    return out


# ============================================================================ tokenization + NP extraction
_DET = {"the", "a", "an", "his", "her", "its", "their", "this", "that", "my", "your", "our"}
_STOP_BOUNDARY = ({"before", "after", "so", "and", "but", "or", "when", "while", "until", "if",
                    "because", "from", "for", "by", "at", "in", "on", "with"} | DIRECTIONAL_PP)


def _tokens(sentence: str):
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


def _np_last_content(span):
    """Rightmost content token of an NP span, after stripping ONE leading determiner-equivalent
    (a closed DET set, or any token ending "'s" -- handles both "the old oak tree" (-> tree,
    fixes the single-head-noun compound-noun limitation of the sibling clause_theme heuristic in
    hdlab.goal_owner_select, which this function intentionally does NOT reuse for that reason) and
    possessive "Owen's rival" (-> rival, not owen))."""
    toks = list(span)
    if toks and (toks[0] in _DET or toks[0].endswith("'s")):
        toks = toks[1:]
    return toks[-1] if toks else None


def find_desired_state(sentence: str):
    """Locate a desiderative-governed purpose-infinitival "to VERB" and extract
    {referent, classes, verb_lemma, pattern}. Returns None if no DESIDERATIVE_PASS verb is found
    (v1 scope: this mechanism only fires on explicit desiderative constructions)."""
    toks = _tokens(sentence)
    dv_idx = next((i for i, t in enumerate(toks) if t in DESIDERATIVE_PASS), None)
    if dv_idx is None:
        return None
    for i in range(dv_idx + 1, len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        embedded_lemma = lemma_verb(toks[i + 1])
        classes = _verb_classes(embedded_lemma)
        between = toks[dv_idx + 1:i]
        if between:
            referent = _np_last_content(between)
            pattern = "ECM"
        else:
            pattern = "CONTROL"
            if classes & SUBJECT_IS_REFERENT_CLASSES:
                referent = _np_last_content(toks[:dv_idx])
            elif classes & OBJECT_IS_REFERENT_CLASSES:
                j = i + 2
                while j < len(toks) and toks[j] not in _STOP_BOUNDARY and toks[j] != "to":
                    j += 1
                referent = _np_last_content(toks[i + 2:j])
            else:
                referent = None
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": pattern}
    return None


def find_actual_state(sentence: str):
    """Scan for the first token whose lemma is a member of ANY RESULT_VERB_CLASS; referent = the
    rightmost content token of the subject span preceding it. Returns None if no known-class verb
    is found (precision guard -- caller ABSTAINs)."""
    toks = _tokens(sentence)
    for idx, t in enumerate(toks):
        lemma = lemma_verb(t)
        classes = _verb_classes(lemma)
        if classes:
            referent = _np_last_content(toks[:idx])
            return {"referent": referent, "classes": classes, "verb_lemma": lemma, "verb_idx": idx}
    return None


def congruence_decision(goal_sentences, outcome_sentence: str):
    """The 3-way congruence function. Returns (verdict, detail) where verdict in
    {"MET", "UNMET", "NA"}. NA = ABSTAIN (precision guard; caller falls back to the lexicon)."""
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    if desired is None:
        return "NA", {"reason": "no_desiderative_goal_found"}
    actual = find_actual_state(outcome_sentence)
    if actual is None or not actual["classes"]:
        return "NA", {"reason": "actual_verb_class_unknown", "desired": desired}
    same = desired["classes"] & actual["classes"]
    opposed = _opposed_of(desired["classes"]) & actual["classes"]
    if not same and not opposed:
        return "NA", {"reason": "verb_class_unrelated", "desired": desired, "actual": actual}
    if desired["referent"] is None or actual["referent"] is None:
        return "NA", {"reason": "referent_extraction_failed", "desired": desired, "actual": actual}
    if desired["referent"] != actual["referent"]:
        return "UNMET", {"reason": "referent_mismatch", "desired": desired, "actual": actual}
    if same:
        return "MET", {"reason": "same_class_same_referent", "desired": desired, "actual": actual}
    return "UNMET", {"reason": "opposed_class_same_referent", "desired": desired, "actual": actual}


def congruence_outcome_valence(passage_text: str):
    """Top-level entry: split `passage_text` into sentences (hdlab.goal_owner_select._sentences,
    reused), goal-sentences = all but the last, outcome-sentence = the last."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    return congruence_decision(sents[:-1], sents[-1])


def lexicon_predict(outcome_sentence: str):
    """The mechanism being replaced: V2_OUTCOME_UNMET/_MET set-membership on the outcome sentence
    alone (imported unmodified from hdlab.goal_typing -- same sets, same tokenization convention
    as production's type_sentence_events_c3)."""
    t = normalize_tokens(outcome_sentence)
    has_unmet = bool(t & V2_OUTCOME_UNMET)
    has_met = bool(t & V2_OUTCOME_MET)
    if has_unmet and has_met:
        return "AMBIGUOUS"
    if has_unmet:
        return "UNMET"
    if has_met:
        return "MET"
    return "NONE"


def congruence_with_lexicon_fallback(passage_text: str):
    """ABSTAIN -> lexicon fallback (backward-compat contract): if the mechanism can't confidently
    decide, fall back to today's production lexicon behavior on the outcome sentence."""
    verdict, detail = congruence_outcome_valence(passage_text)
    if verdict != "NA":
        return verdict, detail
    sents = _sentences(passage_text)
    lex = lexicon_predict(sents[-1]) if sents else "NONE"
    return lex, {"reason": "abstain_fallback_to_lexicon", "lexicon_raw": lex}


# ============================================================================ 10-item bank
def _jsonable(obj):
    """Recursively convert sets (result-verb-class detail) to sorted lists so per-item detail is
    JSON-serializable for the units.jsonl shard (record_unit uses a plain json.dumps)."""
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def load_bank():
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


FLIP_SET_IDS = {"A-unmet", "A-met", "B-unmet", "B-met", "C-unmet", "C-met", "D-met", "D-unmet"}
SCRAMBLE_OFFSET = 2  # see module docstring "CONTROLS" for why +1 is unsound for this bank


def run_bank_item(item: dict):
    sents = _sentences(item["text"])
    goal_sentences, outcome_sentence = sents[:-1], sents[-1]
    mech_verdict, mech_detail = congruence_decision(goal_sentences, outcome_sentence)
    lex_verdict = lexicon_predict(outcome_sentence)
    return dict(id=item["id"], category=item["category"], gold=item["gold"],
                mechanism=mech_verdict, mechanism_detail=_jsonable(mech_detail),
                mechanism_matches=(mech_verdict == item["gold"]),
                lexicon=lex_verdict, lexicon_matches=(lex_verdict == item["gold"]))


def run_scramble(rows):
    n = len(rows)
    out = []
    for i, item in enumerate(rows):
        goal_item = item
        outcome_item = rows[(i + SCRAMBLE_OFFSET) % n]
        goal_sentences = _sentences(goal_item["text"])[:-1]
        outcome_sentence = _sentences(outcome_item["text"])[-1]
        verdict, detail = congruence_decision(goal_sentences, outcome_sentence)
        out.append(dict(id=goal_item["id"], scrambled_with=outcome_item["id"],
                        gold=goal_item["gold"], scrambled_verdict=verdict,
                        scrambled_matches=(verdict == goal_item["gold"])))
    return out


# ============================================================================ backward-compat (62-item bank)
def load_fair_bank():
    rows = []
    with open(FAIR_BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def resolve_recency_positional(item: dict):
    resolver = GeneralRecencyEntityResolver(item["roster"])
    last = None
    for s in _sentences(item["text"]):
        last = resolver.subject_entity(s)
    return last


def load_48_item_subset(rows):
    """Reproduces the documented 48-item subset (hdlab/goal_owner_select.py docstring: primacy ep
    12/12 + ai 8/8, recency-trap DIVERGENT ep 18/18 + ai 10/10) via the same filter convention as
    experiments/exp_c5_multigoal_content_coherence_tiebreak_v1.py's load_full_instrument."""
    units = []
    for r in rows:
        if r.get("verb_type") not in ("explicit_psych", "action_implied"):
            continue
        if r.get("trap_type") == "primacy":
            units.append(r)
        elif r.get("trap_type", "recency") == "recency" and r.get("has_distractor"):
            if resolve_recency_positional(r) != r["gold_outcome_owner"]:
                units.append(r)
    return units


def backward_compat_check():
    rows = load_fair_bank()
    subset48 = load_48_item_subset(rows)
    owner_correct, owner_misses = 0, []
    for it in subset48:
        pick = select_outcome_owner(it["text"], it["roster"], seed=0)
        if pick == it["gold_outcome_owner"]:
            owner_correct += 1
        else:
            owner_misses.append(it["id"])
    mech_dist: Counter = Counter()
    mech_errors = []
    for it in rows:
        try:
            verdict, _detail = congruence_with_lexicon_fallback(it["text"])
            mech_dist[verdict] += 1
        except Exception as e:  # noqa: BLE001 -- recorded, not swallowed silently (no continue-past)
            mech_errors.append({"id": it["id"], "error": f"{type(e).__name__}: {e}"})
    return dict(n_total_rows=len(rows), n_48_subset=len(subset48), owner_correct=owner_correct,
                owner_misses=owner_misses, owner_48_held=(owner_correct == len(subset48) == 48),
                mechanism_verdict_distribution=dict(mech_dist), mechanism_errors=mech_errors,
                mechanism_ran_clean=(len(mech_errors) == 0))


# ============================================================================ per-unit + aggregate
def run_flip_set_eval():
    rows = load_bank()
    per_item = [run_bank_item(it) for it in rows]
    scramble = run_scramble(rows)
    return dict(per_item=per_item, scramble=scramble)


def _acc(rows, key, ids=None):
    if ids is not None:
        rows = [r for r in rows if r["id"] in ids]
    vals = [r[key] for r in rows]
    return round(sum(bool(v) for v in vals) / len(vals), 4) if vals else None


def aggregate(flip_unit: dict, bc_unit: dict):
    per_item = flip_unit["per_item"]
    scramble = flip_unit["scramble"]

    mech_acc_flip8 = _acc(per_item, "mechanism_matches", FLIP_SET_IDS)
    lex_acc_flip8 = _acc(per_item, "lexicon_matches", FLIP_SET_IDS)
    delta = round(mech_acc_flip8 - lex_acc_flip8, 4) if (mech_acc_flip8 is not None
                                                          and lex_acc_flip8 is not None) else None

    gold_flip8 = [r["gold"] for r in per_item if r["id"] in FLIP_SET_IDS]
    base_rate = round(max(Counter(gold_flip8).values()) / len(gold_flip8), 4) if gold_flip8 else None

    scramble_acc = _acc(scramble, "scrambled_matches")
    scramble_collapse_strict = (scramble_acc is not None and base_rate is not None
                                and abs(scramble_acc - base_rate) <= 0.15)
    # loose reading: the failure mode this control guards against is scramble STAYING artificially
    # high (mechanism secretly still keyed off the outcome word alone); a mechanism that instead
    # ABSTAINs under mismatched goal/outcome pairing and lands AT OR BELOW base rate is not that
    # failure mode -- report both, gate on the strict (literal pre-reg) reading.
    scramble_collapse_loose = (scramble_acc is not None and base_rate is not None
                               and scramble_acc <= base_rate + 0.15)
    scramble_collapses = scramble_collapse_strict

    h_row = next((r for r in per_item if r["id"] == "H-abstain"), None)
    h_abstains = bool(h_row and h_row["mechanism"] == "NA")
    g_row = next((r for r in per_item if r["id"] == "G-control"), None)
    g_correct = bool(g_row and g_row["mechanism_matches"])

    owner_48_held = bc_unit["owner_48_held"]

    hard_pass = bool(
        mech_acc_flip8 is not None and mech_acc_flip8 >= 7 / 8 - 1e-9
        and lex_acc_flip8 is not None and lex_acc_flip8 <= 0.625 + 1e-9
        and delta is not None and delta >= 0.25 - 1e-9
        and scramble_collapses and h_abstains and g_correct and owner_48_held
    )
    hard_fail = bool(
        (mech_acc_flip8 is not None and mech_acc_flip8 < 0.625 - 1e-9)
        or (delta is not None and delta < 0.15 - 1e-9)
        or not scramble_collapses or not h_abstains
    )
    verdict = "HARD_FAIL" if hard_fail else ("HARD_PASS" if hard_pass else "MIDDLE_BAND")

    msg = (
        f"FLIP_SET(N=8): mechanism_acc={mech_acc_flip8} lexicon_acc={lex_acc_flip8} "
        f"delta={delta}. base_rate={base_rate} scramble_acc={scramble_acc} "
        f"collapse_strict(within 0.15 of base_rate)={scramble_collapse_strict} "
        f"collapse_loose(<=base_rate+0.15)={scramble_collapse_loose}. "
        f"H_abstains={h_abstains} G_correct={g_correct} owner_48_held={owner_48_held} "
        f"(owner_correct={bc_unit['owner_correct']}/{bc_unit['n_48_subset']}). "
        f"mechanism_ran_clean_on_62={bc_unit['mechanism_ran_clean']} "
        f"mech_verdict_dist_on_62={bc_unit['mechanism_verdict_distribution']}. "
        f"N=10 is small; MIDDLE_BAND unless HARD-PASS clears decisively -- a 20-30 item follow-up "
        f"bank is needed before production promotion regardless of tier. VERDICT={verdict}.")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {msg}", summary=msg,
        flip_set=dict(n=8, mechanism_accuracy=mech_acc_flip8, lexicon_accuracy=lex_acc_flip8,
                     delta=delta, base_rate=base_rate, per_item=per_item),
        scramble=dict(offset=SCRAMBLE_OFFSET, accuracy=scramble_acc,
                     collapse_strict=scramble_collapse_strict, collapse_loose=scramble_collapse_loose,
                     per_item=scramble),
        precision_guard=dict(h_abstains=h_abstains, h_detail=h_row, g_correct=g_correct, g_detail=g_row),
        backward_compat=bc_unit,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, path)


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": 2})

    done = completed_units(OUTPUT_DIR)
    if "flip_set_eval" not in done:
        ts = time.perf_counter()
        res = run_flip_set_eval()
        record_unit(OUTPUT_DIR, "flip_set_eval", res)
        print(f"[progress] flip_set_eval {time.perf_counter()-ts:.3f}s "
              f"mech_acc={_acc(res['per_item'], 'mechanism_matches', FLIP_SET_IDS)} "
              f"lex_acc={_acc(res['per_item'], 'lexicon_matches', FLIP_SET_IDS)}", flush=True)
    else:
        print("[resume] flip_set_eval done, skip", flush=True)

    if "backward_compat_62" not in done:
        ts = time.perf_counter()
        res = backward_compat_check()
        record_unit(OUTPUT_DIR, "backward_compat_62", res)
        print(f"[progress] backward_compat_62 {time.perf_counter()-ts:.3f}s "
              f"owner_48_held={res['owner_48_held']} clean={res['mechanism_ran_clean']}", flush=True)
    else:
        print("[resume] backward_compat_62 done, skip", flush=True)

    units = load_units(OUTPUT_DIR)
    if "flip_set_eval" not in units or "backward_compat_62" not in units:
        raise RuntimeError(f"META_RULE_H cardinality breach: units present={sorted(units.keys())}, "
                           f"expected ['flip_set_eval','backward_compat_62']")

    agg = aggregate(units["flip_set_eval"], units["backward_compat_62"])
    agg["arms_differ_verified"] = False
    agg["arms_differ_exempted"] = [("mechanism", "lexicon")]
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        seeds=SEEDS, bank_path=BANK_PATH, fair_bank_path=FAIR_BANK_PATH,
        cardinality_ok=(set(units.keys()) == {"flip_set_eval", "backward_compat_62"}),
        result_verb_classes={k: sorted(v) for k, v in CLASS_REGISTRY.items()},
        opposed_pairs=OPPOSED_PAIRS,
        mechanism="goal-congruence: (theme_referent, result_verb_class) desired-vs-actual on the "
                 "shared referent; ABSTAIN falls back to hdlab.goal_typing's V2_OUTCOME_UNMET/_MET lexicon")
    agg["final_metrics_atomicity"] = "tmp_replace"
    agg["crlb_n/a"] = "boolean congruence-decision accuracy, not an SNR/capacity regime"
    agg["deterministic_seeding"] = True
    agg["prereg"] = ("inline (docstring, mirrors notes/drill_brain_outcome_valence_goal_congruence_"
                     "2026-08-06.md Section 4 bands verbatim; no separate preregs/ file)")
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.3f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    rows = load_bank()
    assert len(rows) == 10, f"expected 10 bank items, got {len(rows)}"
    ids = {r["id"] for r in rows}
    assert ids == (FLIP_SET_IDS | {"H-abstain", "G-control"}), f"unexpected id set: {ids}"
    print(f"[SELFTEST 1/6] bank: 10 items, flip_set={len(FLIP_SET_IDS)}", flush=True)

    # (2) DECISIVE: same outcome word ("sank"), opposite gold, mechanism gets BOTH right, lexicon
    # gets only the UNMET one right (by construction, since it's word-only).
    a_unmet = next(run_bank_item(r) for r in rows if r["id"] == "A-unmet")
    a_met = next(run_bank_item(r) for r in rows if r["id"] == "A-met")
    assert a_unmet["mechanism"] == "UNMET" and a_unmet["lexicon"] == "UNMET"
    assert a_met["mechanism"] == "MET", f"A-met mechanism must be MET, got {a_met['mechanism']}"
    assert a_met["lexicon"] == "UNMET", "lexicon must (wrongly) predict UNMET for A-met by construction"
    print(f"[SELFTEST 2/6] A-unmet/A-met flip: mechanism={a_unmet['mechanism']}/{a_met['mechanism']} "
          f"(correct both), lexicon={a_unmet['lexicon']}/{a_met['lexicon']} (wrong on A-met)", flush=True)

    # (3) DECISIVE: entity-binding (D-unmet) -- same verb class both sides (win), but wrong
    # referent (rival, not sister) -- mechanism must say UNMET, not MET.
    d_unmet = next(run_bank_item(r) for r in rows if r["id"] == "D-unmet")
    assert d_unmet["mechanism"] == "UNMET", f"D-unmet mechanism must be UNMET, got {d_unmet['mechanism']}"
    assert d_unmet["mechanism_detail"]["reason"] == "referent_mismatch"
    assert d_unmet["lexicon"] == "MET", "lexicon must (wrongly) predict MET for D-unmet by construction"
    print(f"[SELFTEST 3/6] D-unmet entity-binding: mechanism=UNMET (referent_mismatch, sister!=rival), "
          f"lexicon=MET (wrong)", flush=True)

    # (4) PRECISION GUARD: H must abstain (NA), not hallucinate a verdict.
    h = next(run_bank_item(r) for r in rows if r["id"] == "H-abstain")
    assert h["mechanism"] == "NA", f"H-abstain must be NA, got {h['mechanism']}"
    print(f"[SELFTEST 4/6] H-abstain: mechanism=NA (precision guard fires)", flush=True)

    # (5) FULL flip-set + scramble + backward-compat wired end-to-end.
    flip_unit = run_flip_set_eval()
    bc_unit = backward_compat_check()
    agg = aggregate(flip_unit, bc_unit)
    assert agg["flip_set"]["mechanism_accuracy"] >= 7 / 8 - 1e-9, (
        f"self-test expects mechanism to clear the 7/8 HARD-PASS floor, "
        f"got {agg['flip_set']['mechanism_accuracy']}")
    assert agg["flip_set"]["lexicon_accuracy"] <= 0.625 + 1e-9, (
        f"self-test expects lexicon <= 0.625, got {agg['flip_set']['lexicon_accuracy']}")
    assert agg["backward_compat"]["owner_48_held"], "backward-compat 48/48 must hold"
    assert agg["backward_compat"]["mechanism_ran_clean"], "mechanism must run clean over the 62-item bank"
    print(f"[SELFTEST 5/6] flip_set mech_acc={agg['flip_set']['mechanism_accuracy']} "
          f"lex_acc={agg['flip_set']['lexicon_accuracy']} owner_48_held="
          f"{agg['backward_compat']['owner_48_held']}", flush=True)

    # (6) determinism: re-running yields bit-identical per_item verdicts (no RNG anywhere).
    flip_unit2 = run_flip_set_eval()
    assert flip_unit["per_item"] == flip_unit2["per_item"], "mechanism must be deterministic"
    print(f"[SELFTEST 6/6] determinism: repeated run bit-identical", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
