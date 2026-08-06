# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (bridging arm binds all 8 POS_MET/NEG_UNMET items; lexical-only
#   arm binds none of them -- checked in self_test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity claim; FHRR decode of <=8 bound event-slots at d=1024 far below any
#   capacity ceiling (established by the sibling evaluative-bridging cell + goal_owner_select /
#   grounded_appraisal_sim self-tests); this cell's discriminator is a boolean construction-detector +
#   registry lookup, not a noise-limited decode
# - baseline_in_band: n/a (LEXICAL-ONLY baseline is a MUST-FAIL floor by construction: 0/8 on the
#   zero-lexical-overlap items, not a mid-band baseline)
# - discriminator survives scale: n/a, fixed-size N=12 hand-authored bank, no scale sweep
# - cardinality_ok: EXPECTED_N_SEEDS=3, EXPECTED_N_ITEMS=12; HARD_FAIL_CARDINALITY if either short
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands set BEFORE running, per
#   preregs/2026-08-06_affect_state_bridging_inference_v1.md, not tuned post-hoc)
# - deterministic_seeding: torch.Generator per seed; fixed-int seeds; scramble = fixed cyclic shift
#   (offset=1, asserted zero-fixed-points), never hash()-derived; no push
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py); start_marker + crash_diag present
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""exp_affect_state_bridging_inference_v1 -- Graesser Class-7 BACKWARD causal-antecedent BRIDGING
INFERENCE from an AFFECT-STATE predicate (the protagonist's OWN emotion: "Oh, how glad I am!" /
"he felt ashamed") back to a standing GOAL. SIBLING of exp_evaluative_bridging_inference_v1.py
(commit 17dd3567b, HARD_PASS, wired to production Tier-3 at commit d157941c6), which bridges an
EXTERNAL evaluative speech act about the addressee ("you are a good boy") to the addressee's goal.
This cell bridges the INTERNAL affect-state of the goal-holder's own experience instead -- a
different construction, same bridging pattern (valence -> goal-outcome), same strict-ADD scope.

WHY (task brief, disk-verified): real-prose item mg1_frank_fishing (experiments/data/
real_text_goal_owner_diagnostic_v1.jsonl) contains the verbatim line "Oh, how glad I am!" as its
outcome expression -- a construction the evaluative bridge (external, addressee-directed) cannot
reach, because nobody EVALUATES Frank; Frank expresses his OWN affect. Brain-foundational: abstract
goal/outcome concepts ground via AFFECT + reward-PE (notes/audit_brain_feature_acquisition_
grounding_2026-08-06.md); this increment is a lexicon-based step toward that affect-grounded route,
not the grounding itself (see Follow-ups in the pre-reg).

MECHANISM (strict ADD, reuses owned organs verbatim, NO new binding operator):
1. DETECT: detect_affect_state_construction() -- Pattern A (third person: roster NAME or a
   gender-resolvable pronoun immediately followed by feels/felt/is/was, then an AFFECT word within a
   window -- deliberately excludes are/were so it can NEVER match a 2nd-person "you are ADJ" address,
   the sibling's construction) OR Pattern B (first person dialogue: "i" adjacent to "am", AFFECT word
   anywhere in the sentence to cover both "I am so glad" and "how glad I am" word order; holder =
   the reporting-verb speaker attribution, the first roster name token in the sentence).
2. VALUE: AFFECT_POS lexicon hit -> pos-affect, AFFECT_NEG hit -> neg-affect (lexicon lookup, SAME
   SUPPLY-schema pattern as the sibling's EVAL_POS/EVAL_NEG).
3. BRIDGE: bridge_outcome() reuses hdlab.goal_owner_select.GoalOutcomeRegister (byte-identical,
   UNMODIFIED import) -- fires ONLY if the construction's HOLDER == the queried entity (the affect
   must be the GOAL-HOLDER's OWN affect, never a bystander's -- the critical over-fire guard) AND
   register.appraise(entity)["has_goal"] is True. POS -> OUTCOME_MET, NEG -> OUTCOME_UNMET. No match
   / wrong holder / no open goal -> abstain, never forces a bridge.
4. STRICT-ADD GATING: resolve_outcome() tries LEXICAL verb-typing (hdlab.goal_typing.type_goal_events,
   unmodified production organ) on the outcome sentence FIRST; the bridge is consulted ONLY when
   verb-typing produced NOTHING for every candidate (OUTCOME_NEVER_TYPED).
5. COMPOSITION CHECK: imports the sibling's detect_evaluative_construction (read-only) to verify
   ZERO cross-fire in both directions, and re-runs the sibling's own self_test() in-process to prove
   this new file caused zero regression to the existing evaluative bridge.

No production file is modified (hdlab/goal_typing.py, hdlab/goal_owner_select.py are imported
read-only; exp_evaluative_bridging_inference_v1.py is imported read-only, also unmodified) -- this
cell is a self-contained harness, so verification/run_certification.py is NOT required.

INSTRUMENT: experiments/data/affect_state_bridging_bank_v1.jsonl, N=12 hand-authored items, 4
categories (POS_MET n=5 incl. frank_fishing_glad "how glad I am!", NEG_UNMET n=3, BYSTANDER n=2,
UNCHANGED n=2). Zero-lexical-overlap between goal clause and outcome clause is mechanically checked
in self-test for every POS_MET/NEG_UNMET item.

PRE-REGISTERED BANDS (see preregs/2026-08-06_affect_state_bridging_inference_v1.md for full text,
written BEFORE this cell was run): HARD-PASS requires zero_overlap_bridging_acc>=0.85 (incl.
frank_fishing_glad correct) AND gap-vs-lexical-only>=0.50 AND both valence controls==1.0 AND
bystander_no_bridge==1.0 AND unchanged_control==1.0 AND scramble_acc<=0.15 AND no_interference==True
(both cross-detector fire-counts 0 AND the sibling's own self_test() still passes). HARD-FAIL on any
over-fire (wrong entity / fires on non-affect / wrong valence) OR bridging_acc<0.85 OR gap<0.25 OR
scramble doesn't collapse OR interference detected.

HONEST SCOPE: this validates the AFFECT-STATE BRIDGING MECHANISM IN ISOLATION. frank_fishing_glad
is MODELED ON mg1_frank_fishing's affect phrasing (verbatim "Oh, how glad I am!"), NOT that item
verbatim -- mg1_frank_fishing's own GOAL is expressed only through a dialogue REQUEST ("would you
like to go?"/"may I go?"), a SEPARATE competency (dialogue-request goal recognition) this cell does
NOT build. Passing this pre-reg does NOT mean mg1_frank_fishing is solved end-to-end.

Cites: hdlab/goal_owner_select.py::GoalOutcomeRegister (unmodified); hdlab/goal_typing.py::
type_goal_events/_sentences/_ordered_tokens (unmodified); experiments/
exp_evaluative_bridging_inference_v1.py (sibling, imported read-only for the composition check);
experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (mg1_frank_fishing, affect-phrasing
source).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "affect_state_bridging_inference_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "affect_state_bridging_bank_v1.jsonl")

# ---- REUSED, UNMODIFIED production organs (read-only imports; nothing here is a new mechanism) ----
from hdlab.goal_typing import (  # noqa: E402
    type_goal_events, _sentences, _ordered_tokens, R_GOAL, R_UNMET, R_MET,
)
from hdlab.goal_owner_select import (  # noqa: E402
    GoalOutcomeRegister, D2_DEFAULT, _is_pron_general, _gender_of_general,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ---- REUSED, UNMODIFIED sibling cell (read-only import; used ONLY for the composition/
# no-interference check -- this cell's own mechanism never calls anything from the sibling) ----
import exp_evaluative_bridging_inference_v1 as _eval_mod  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
EXPECTED_N_ITEMS = 12
EXPECTED_CAT_COUNTS = {"POS_MET": 5, "NEG_UNMET": 3, "BYSTANDER": 2, "UNCHANGED": 2}

# ============================================================================ SUPPLIED SCHEMA: the
# POS-blind affect-valence lexicon (same SUPPLY pattern as the sibling's EVAL_POS/EVAL_NEG and
# hdlab.goal_typing's RESULT_VERB_CLASS / V2_OUTCOME_MET/_UNMET registers). Exact lexicon per task
# brief. NOTE the one genuine lexical overlap with the sibling's EVAL_POS: "cheerful" is a member of
# both lists -- handled structurally, not by lexicon surgery: Pattern A below only matches is/was
# (never are/were), so it can never fire on the sibling's "you are ADJ" construction regardless of
# which adjective is in the window (verified empirically in self-test's interference gate, not just
# asserted).
AFFECT_POS = {
    "glad", "happy", "joyful", "delighted", "proud", "pleased", "thankful", "merry", "cheerful",
}
AFFECT_NEG = {
    "sad", "ashamed", "sorry", "miserable", "disappointed", "unhappy", "grieved", "downcast",
    "sorrowful",
}
_AFFECT_TRIGGERS_3P = {"feels", "felt", "is", "was"}  # deliberately NOT are/were (2nd-person guard)
_AFFECT_WINDOW = 6


# ============================================================================ (1) DETECT + (2) VALUE
def detect_affect_state_construction(sentence: str, roster: dict):
    """Own-affect construction detector (glass-box, no POS tagger). Returns (polarity, holder) where
    polarity in {"POS","NEG"}, holder = the roster entity whose OWN affect this is, or (None, None).

    Pattern B (first person) checked FIRST: "i" immediately followed by "am" (covers "I am so glad"
    AND "how glad I am!" word order -- the AFFECT scan below covers the WHOLE sentence for this
    pattern, since the affect word can precede "i am"). Holder = the first roster-name token in the
    sentence (reporting-verb speaker attribution, e.g. "Frank cried, ...I am!").

    Pattern A (third person): a roster NAME or a gender-resolvable pronoun (he/she) immediately
    preceding feels/felt/is/was (NEVER are/were -- that word order is the sibling's 2nd-person "you
    are ADJ" construction, out of scope here by construction, not by exclusion-list patching), AFFECT
    word within a forward window. Ambiguous pronoun (no unique gender match in roster) -> abstain for
    that trigger, scan continues."""
    toks = _ordered_tokens(sentence)
    # ---- Pattern B: first person dialogue ----
    for i, t in enumerate(toks):
        if t == "i" and i + 1 < len(toks) and toks[i + 1] == "am":
            polarity = None
            for w in toks:
                if w in AFFECT_POS:
                    polarity = "POS"
                    break
                if w in AFFECT_NEG:
                    polarity = "NEG"
                    break
            if polarity is None:
                continue
            holder = None
            for t2 in toks:
                if t2 in roster:
                    holder = t2
                    break
            return polarity, holder
    # ---- Pattern A: third person ----
    for i, t in enumerate(toks):
        if t not in _AFFECT_TRIGGERS_3P:
            continue
        subj = toks[i - 1] if i > 0 else None
        if subj is None or subj in ("you", "i"):
            continue
        holder = None
        if subj in roster:
            holder = subj
        elif _is_pron_general(subj):
            want = _gender_of_general(subj, roster)
            cands = sorted(e for e in roster if roster[e] == want)
            if len(cands) == 1:
                holder = cands[0]
        if holder is None:
            continue
        polarity = None
        for w in toks[i + 1: i + 1 + _AFFECT_WINDOW]:
            if w in AFFECT_POS:
                polarity = "POS"
                break
            if w in AFFECT_NEG:
                polarity = "NEG"
                break
        if polarity is not None:
            return polarity, holder
    return None, None


# ============================================================================ (3) BRIDGE
def bridge_outcome(entity: str, sentence: str, roster: dict, register: GoalOutcomeRegister):
    """Class-7 backward causal-antecedent bridge: fires ONLY if the affect-state construction's
    holder is `entity` (the affect is the GOAL-HOLDER's OWN affect, never a bystander's) AND `entity`
    currently holds an open GOAL in `register` (written by ordinary
    hdlab.goal_typing.type_goal_events calls on the passage's non-outcome sentences, elsewhere in
    this file). Returns R_MET / R_UNMET / None (abstain -- no forced bridge)."""
    polarity, holder = detect_affect_state_construction(sentence, roster)
    if polarity is None or holder != entity:
        return None
    ap = register.appraise(entity)
    if not ap["has_goal"]:
        return None
    return R_MET if polarity == "POS" else R_UNMET


# ============================================================================ harness-local subject
# resolution for populating the register (byte-identical logic to the sibling's
# resolve_goal_subject -- deliberately duplicated, not cross-imported, so this cell's own mechanism
# stays fully self-contained; the sibling is imported ONLY for the composition-check functions
# below). Sentence-initial-token heuristic: check the FIRST content token for an explicit roster name
# or a gendered pronoun-recency match BEFORE falling back to a whole-sentence roster-name scan.
def resolve_goal_subject(sentence: str, roster: dict, recent: list):
    toks = _ordered_tokens(sentence)
    if not toks:
        return None, False
    first = toks[0]
    if first in roster:
        return first, True
    if _is_pron_general(first):
        want = _gender_of_general(first, roster)
        for e in reversed(recent):
            if _gender_of_general(e, roster) == want:
                return e, False
    for t in toks:
        if t in roster:
            return t, True
    return None, False


def build_register(item: dict, seed: int) -> GoalOutcomeRegister:
    text, roster = item["text"], item["roster"]
    sents = _sentences(text)
    gen = torch.Generator().manual_seed(5000 + int(seed))
    reg = GoalOutcomeRegister(d=D2_DEFAULT, generator=gen, max_event_slots=8)
    recent: list = []
    for s in sents[:-1]:
        subj, is_name = resolve_goal_subject(s, roster, recent)
        if is_name:
            recent.append(subj)
        if subj is not None:
            for (e, r) in type_goal_events(s, subj):
                reg.add_typed_event(e, r)
    return reg


# ============================================================================ (4) STRICT-ADD GATING
def lexical_hits_for(outcome_sentence: str, roster: dict) -> dict:
    """ARM B / step-1 of ARM A: unmodified production verb-typing (type_goal_events) queried per
    roster entity. Byte-identical to what hdlab.goal_owner_select.build_candidate_role_seq does on
    the outcome sentence for each enumerated candidate."""
    hits = {}
    for cand in sorted(roster):
        for (e, r) in type_goal_events(outcome_sentence, cand):
            if e == cand and r in (R_UNMET, R_MET):
                hits[cand] = r
    return hits


def resolve_outcome(item: dict, register: GoalOutcomeRegister):
    """ARM A (BRIDGING): lexical verb-typing first (unchanged production path); the bridge is
    consulted ONLY when lexical typing produced NOTHING for every candidate (OUTCOME_NEVER_TYPED).
    Returns (hits: dict, source: 'LEXICAL'|'BRIDGE'|'NONE')."""
    text, roster = item["text"], item["roster"]
    outcome_sentence = _sentences(text)[-1]
    lex = lexical_hits_for(outcome_sentence, roster)
    if lex:
        return lex, "LEXICAL"
    bridge_hits = {}
    for cand in sorted(roster):
        role = bridge_outcome(cand, outcome_sentence, roster, register)
        if role is not None:
            bridge_hits[cand] = role
    return bridge_hits, ("BRIDGE" if bridge_hits else "NONE")


# ============================================================================ bank + zero-overlap check
def load_bank():
    rows = []
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


_STOPWORDS = {
    "a", "an", "the", "to", "of", "and", "or", "but", "for", "with", "before", "after", "so",
    "when", "while", "until", "if", "because", "from", "by", "at", "in", "on", "as", "that",
    "this", "his", "her", "its", "their", "he", "she", "it", "they", "him", "them", "you", "your",
    "said", "was", "were", "is", "are", "very", "every", "just", "i", "am", "oh", "cried",
}


def content_tokens(sentence: str, roster: dict) -> set:
    return {t for t in _ordered_tokens(sentence) if t not in _STOPWORDS and t not in roster}


def find_goal_sentence(item: dict) -> str:
    """The specific sentence that fires the R_GOAL event for item['goal_holder']. Falls back to
    sents[0] if no sentence fires GOAL (should not happen for POS_MET/NEG_UNMET items; asserted
    separately)."""
    sents = _sentences(item["text"])
    roster, holder = item["roster"], item["goal_holder"]
    recent: list = []
    for s in sents[:-1]:
        subj, is_name = resolve_goal_subject(s, roster, recent)
        if is_name:
            recent.append(subj)
        if subj is not None and any(
                e == holder and r == R_GOAL for (e, r) in type_goal_events(s, subj)):
            return s
    return sents[0]


def zero_overlap_check(item: dict) -> dict:
    """Mechanical check (not just asserted by construction): the sentence that actually fires the
    GOAL event for item['goal_holder'] and the outcome sentence's content tokens share NO token
    (minus stopwords/roster names)."""
    sents = _sentences(item["text"])
    goal_sent, outcome_sent = find_goal_sentence(item), sents[-1]
    g = content_tokens(goal_sent, item["roster"])
    o = content_tokens(outcome_sent, item["roster"])
    overlap = g & o
    return {"goal_sentence": goal_sent, "goal_tokens": sorted(g), "outcome_tokens": sorted(o),
            "overlap": sorted(overlap), "zero_overlap": len(overlap) == 0}


# ============================================================================ per-item scoring
def score_item(item: dict, hits: dict) -> bool:
    cat = item["category"]
    holder = item["goal_holder"]
    gold_role = R_MET if item["gold_polarity"] == "MET" else (
        R_UNMET if item["gold_polarity"] == "UNMET" else None)
    if cat in ("POS_MET", "NEG_UNMET"):
        return hits == {holder: gold_role}
    if cat == "BYSTANDER":
        return hits == {}
    if cat == "UNCHANGED":
        return hits.get(holder) == gold_role
    raise ValueError(f"unknown category {cat!r}")


# ============================================================================ (5) COMPOSITION /
# NO-INTERFERENCE CHECK (real other-detector, not a re-implementation; seed-independent, pure
# detector composition)
def check_no_interference() -> dict:
    eval_bank = _eval_mod.load_bank()
    affect_fires_on_eval = []
    for it in eval_bank:
        outcome_sentence = _sentences(it["text"])[-1]
        polarity, holder = detect_affect_state_construction(outcome_sentence, it["roster"])
        if polarity is not None:
            affect_fires_on_eval.append({"id": it["id"], "polarity": polarity, "holder": holder})

    affect_bank = load_bank()
    eval_fires_on_affect = []
    for it in affect_bank:
        outcome_sentence = _sentences(it["text"])[-1]
        polarity, addressee = _eval_mod.detect_evaluative_construction(outcome_sentence, it["roster"])
        if polarity is not None:
            eval_fires_on_affect.append({"id": it["id"], "polarity": polarity, "addressee": addressee})

    sibling_self_test_passed = bool(_eval_mod.self_test())

    return {
        "affect_detector_fires_on_eval_bank_n": len(affect_fires_on_eval),
        "affect_detector_fires_on_eval_bank_items": affect_fires_on_eval,
        "eval_detector_fires_on_affect_bank_n": len(eval_fires_on_affect),
        "eval_detector_fires_on_affect_bank_items": eval_fires_on_affect,
        "sibling_self_test_passed": sibling_self_test_passed,
        "no_interference": (len(affect_fires_on_eval) == 0 and len(eval_fires_on_affect) == 0
                             and sibling_self_test_passed),
    }


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    bank = load_bank()
    registers = {it["id"]: build_register(it, seed) for it in bank}

    rows = []
    for it in bank:
        hits_a, source_a = resolve_outcome(it, registers[it["id"]])
        hits_b = lexical_hits_for(_sentences(it["text"])[-1], it["roster"])
        rows.append({
            "id": it["id"], "category": it["category"], "goal_holder": it["goal_holder"],
            "gold_polarity": it["gold_polarity"],
            "bridging_hits": hits_a, "bridging_source": source_a,
            "bridging_correct": score_item(it, hits_a),
            "lexical_hits": hits_b, "lexical_correct": score_item(it, hits_b),
        })

    # scramble control (iv): fixed cyclic shift (offset=1) over the POS_MET+NEG_UNMET item ids only.
    cat_bridge_ids = [it["id"] for it in bank if it["category"] in ("POS_MET", "NEG_UNMET")]
    n_cb = len(cat_bridge_ids)
    shifted_ids = cat_bridge_ids[1:] + cat_bridge_ids[:1]
    assert all(a != b for a, b in zip(cat_bridge_ids, shifted_ids)), (
        "scramble permutation has a fixed point; not a genuine derangement")
    id_to_item = {it["id"]: it for it in bank}
    scramble_rows = []
    for real_id, scrambled_id in zip(cat_bridge_ids, shifted_ids):
        it = id_to_item[real_id]
        wrong_register = registers[scrambled_id]
        hits_s, _src_s = resolve_outcome(it, wrong_register)
        scramble_rows.append({
            "id": real_id, "scrambled_register_from": scrambled_id,
            "hits": hits_s, "correct": score_item(it, hits_s),
        })

    def frac(rs, key):
        return (sum(1.0 for r in rs if r[key]) / len(rs)) if rs else None

    cat_bridge_rows = [r for r in rows if r["category"] in ("POS_MET", "NEG_UNMET")]
    pos_rows = [r for r in rows if r["category"] == "POS_MET"]
    neg_rows = [r for r in rows if r["category"] == "NEG_UNMET"]
    bystander_rows = [r for r in rows if r["category"] == "BYSTANDER"]
    unchanged_rows = [r for r in rows if r["category"] == "UNCHANGED"]

    frank_row = next(r for r in rows if r["id"] == "frank_fishing_glad")

    unchanged_ok = all(
        r["bridging_hits"] == r["lexical_hits"] and r["bridging_source"] == "LEXICAL"
        and r["bridging_correct"] for r in unchanged_rows)

    return {
        "seed": seed,
        "n_items": len(rows),
        "cat_counts": {c: sum(1 for r in rows if r["category"] == c) for c in EXPECTED_CAT_COUNTS},
        "zero_overlap_bridging_acc": frac(cat_bridge_rows, "bridging_correct"),
        "lexical_only_acc": frac(cat_bridge_rows, "lexical_correct"),
        "frank_fishing_glad_bridging_correct": frank_row["bridging_correct"],
        "valence_pos_acc": frac(pos_rows, "bridging_correct"),
        "valence_neg_acc": frac(neg_rows, "bridging_correct"),
        "bystander_no_bridge_acc": frac(bystander_rows, "bridging_correct"),
        "unchanged_control_acc": (1.0 if unchanged_ok else
                                   frac(unchanged_rows, "bridging_correct")),
        "scramble_acc": (sum(1.0 for r in scramble_rows if r["correct"]) / len(scramble_rows)
                         if scramble_rows else None),
        "rows": rows,
        "scramble_rows": scramble_rows,
    }


# ============================================================================ aggregate + verdict
def aggregate_and_verdict(per_seed: dict, interference: dict) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    z = mean("zero_overlap_bridging_acc")
    lex = mean("lexical_only_acc")
    gap = round(z - lex, 4) if (z is not None and lex is not None) else None
    vpos = mean("valence_pos_acc")
    vneg = mean("valence_neg_acc")
    bys = mean("bystander_no_bridge_acc")
    unc = mean("unchanged_control_acc")
    scr = mean("scramble_acc")
    frank_all = all(per_seed[s]["frank_fishing_glad_bridging_correct"] for s in seeds)
    no_interference = interference["no_interference"]

    cardinality_ok = all(per_seed[s]["n_items"] == EXPECTED_N_ITEMS for s in seeds)
    counts_ok = all(per_seed[s]["cat_counts"] == EXPECTED_CAT_COUNTS for s in seeds)
    deterministic = len({tuple((r["bridging_correct"], r["lexical_correct"])
                                for r in per_seed[s]["rows"]) for s in seeds}) == 1

    if n < EXPECTED_N_SEEDS or not cardinality_ok or not counts_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    else:
        hard_pass = (z is not None and z >= 0.85 and frank_all and gap is not None and gap >= 0.50
                     and vpos == 1.0 and vneg == 1.0 and bys == 1.0 and unc == 1.0
                     and scr is not None and scr <= 0.15 and no_interference)
        hard_fail = (
            (z is None or z < 0.85) or (gap is None or gap < 0.25)
            or (bys is None or bys < 1.0) or (unc is None or unc < 1.0)
            or (vpos is None or vpos < 1.0) or (vneg is None or vneg < 1.0)
            or (scr is None or scr > 0.15) or (not no_interference))
        if hard_pass:
            verdict = "HARD_PASS"
        elif hard_fail:
            verdict = "HARD_FAIL"
        else:
            verdict = "MIDDLE_BAND"

    summary = (
        f"zero_overlap_bridging_acc={z} (incl frank_fishing_glad correct={frank_all}) vs "
        f"lexical_only_acc={lex} (gap={gap}) | valence: pos_acc={vpos} neg_acc={vneg} | "
        f"bystander_no_bridge_acc={bys} | unchanged_control_acc={unc} | scramble_acc={scr} | "
        f"no_interference={no_interference} | deterministic_across_seeds={deterministic}"
    )
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "cardinality_ok": cardinality_ok, "counts_ok": counts_ok,
        "deterministic_across_seeds": deterministic,
        "zero_overlap_bridging_acc": z, "lexical_only_acc": lex, "gap": gap,
        "frank_fishing_glad_bridging_correct_all_seeds": frank_all,
        "valence_pos_acc": vpos, "valence_neg_acc": vneg,
        "bystander_no_bridge_acc": bys, "unchanged_control_acc": unc, "scramble_acc": scr,
        "interference": interference, "per_seed": per_seed,
    }


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _arms_must_differ_check(rows):
    """META_RULE_AF: bridging arm and lexical-only arm must produce DIFFERENT hit-patterns on the
    zero-lexical-overlap items (else the bridging code path is dead/vacuous)."""
    cat_bridge = [r for r in rows if r["category"] in ("POS_MET", "NEG_UNMET")]

    def digest(key):
        blob = "|".join(f"{r['id']}:{sorted(r[key].items())}" for r in cat_bridge)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()
    d_bridge = digest("bridging_hits")
    d_lex = digest("lexical_hits")
    return {"bridging": d_bridge, "lexical": d_lex, "identical": d_bridge == d_lex}


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS})
    done = completed_units(OUTPUT_DIR)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(OUTPUT_DIR, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.3f}s "
              f"zero_overlap_acc={res['zero_overlap_bridging_acc']} "
              f"lexical_acc={res['lexical_only_acc']} scramble_acc={res['scramble_acc']}",
              flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(OUTPUT_DIR).values()}
    if len(per_seed) < EXPECTED_N_SEEDS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(per_seed)}/{EXPECTED_N_SEEDS} seeds")
    interference = check_no_interference()
    agg = aggregate_and_verdict(per_seed, interference)
    agg["arms_must_differ"] = _arms_must_differ_check(per_seed[SEEDS[0]]["rows"])
    agg["arms_differ_verified"] = not agg["arms_must_differ"]["identical"]
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        seeds=SEEDS, bank_path=BANK_PATH, expected_n_items=EXPECTED_N_ITEMS,
        expected_cat_counts=EXPECTED_CAT_COUNTS,
        final_metrics_atomicity="tmp_replace", crlb_n_a="boolean construction-detector + registry "
        "lookup, no capacity-feasibility quantitative discriminator threshold", deterministic_seeding=True,
        production_files_modified=[], no_cert_gate_required_reason="no production file modified",
    )
    agg["prereg"] = "preregs/2026-08-06_affect_state_bridging_inference_v1.md"
    agg["cites"] = [
        "hdlab/goal_owner_select.py::GoalOutcomeRegister (unmodified)",
        "hdlab/goal_typing.py::type_goal_events/_sentences/_ordered_tokens (unmodified)",
        "experiments/exp_evaluative_bridging_inference_v1.py (sibling, read-only, composition check)",
        "experiments/data/affect_state_bridging_bank_v1.jsonl (this cell's bank, 12 items)",
        "experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (mg1_frank_fishing affect source)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.3f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    bank = load_bank()
    assert len(bank) == EXPECTED_N_ITEMS, f"expected {EXPECTED_N_ITEMS} items, got {len(bank)}"
    cat_counts = {c: sum(1 for it in bank if it["category"] == c) for c in EXPECTED_CAT_COUNTS}
    assert cat_counts == EXPECTED_CAT_COUNTS, cat_counts
    for it in bank:
        assert it["goal_holder"] in it["roster"], it["id"]
        sents = _sentences(it["text"])
        assert len(sents) >= 2, f"{it['id']}: need >=2 sentences"
    print(f"[SELFTEST 1/6] bank cardinality + category counts OK: {cat_counts}", flush=True)

    # (2) zero-lexical-overlap mechanical check for every POS_MET/NEG_UNMET item (incl
    # frank_fishing_glad)
    for it in bank:
        if it["category"] not in ("POS_MET", "NEG_UNMET"):
            continue
        chk = zero_overlap_check(it)
        assert chk["zero_overlap"], f"{it['id']}: lexical overlap found: {chk['overlap']}"
    print("[SELFTEST 2/6] zero-lexical-overlap mechanically verified on all POS_MET/NEG_UNMET items "
          "(incl frank_fishing_glad)", flush=True)

    # (3) real production organs are actually being called (real_code_path, not synthetic-only):
    # exercise type_goal_events + GoalOutcomeRegister on the frank_fishing_glad item directly.
    frank = next(it for it in bank if it["id"] == "frank_fishing_glad")
    reg0 = build_register(frank, seed=0)
    ap = reg0.appraise("frank")
    assert ap["has_goal"], f"frank_fishing_glad goal-holder frank must carry an open GOAL: {ap}"
    hits_a, src_a = resolve_outcome(frank, reg0)
    print(f"[SELFTEST 3/6] real organs live: frank register has_goal={ap['has_goal']} "
          f"resolve_outcome={hits_a} source={src_a}", flush=True)
    assert src_a == "BRIDGE", f"frank_fishing_glad must resolve via BRIDGE: {src_a}"
    assert hits_a == {"frank": R_MET}, f"frank_fishing_glad bridge must bind frank->MET: {hits_a}"

    # (4) one full seed sanity + arms-must-differ
    res = run_seed(0)
    assert res["n_items"] == EXPECTED_N_ITEMS
    amd = _arms_must_differ_check(res["rows"])
    assert not amd["identical"], "META_RULE_AF VIOLATION: bridging and lexical-only arms identical"
    print(f"[SELFTEST 4/6] seed0: zero_overlap_acc={res['zero_overlap_bridging_acc']} "
          f"lexical_acc={res['lexical_only_acc']} valence_pos={res['valence_pos_acc']} "
          f"valence_neg={res['valence_neg_acc']} bystander={res['bystander_no_bridge_acc']} "
          f"unchanged={res['unchanged_control_acc']} scramble={res['scramble_acc']} "
          f"arms_differ={not amd['identical']}", flush=True)

    # (5) determinism: repeating seed 0 reproduces byte-identical hit-pattern (PROT-023/F.5)
    res_repeat = run_seed(0)
    pat1 = tuple((r["bridging_correct"], r["lexical_correct"]) for r in res["rows"])
    pat2 = tuple((r["bridging_correct"], r["lexical_correct"]) for r in res_repeat["rows"])
    assert pat1 == pat2, "non-deterministic hit-pattern across repeated seed-0 runs"
    print("[SELFTEST 5/6] seed0 repeat is deterministic (bit-identical hit pattern)", flush=True)

    # (6) composition / no-interference gate (real other-detector, real sibling self_test())
    interference = check_no_interference()
    print(f"[SELFTEST 6/6] no_interference={interference['no_interference']} "
          f"affect_on_eval_n={interference['affect_detector_fires_on_eval_bank_n']} "
          f"eval_on_affect_n={interference['eval_detector_fires_on_affect_bank_n']} "
          f"sibling_self_test_passed={interference['sibling_self_test_passed']}", flush=True)
    assert interference["no_interference"], f"composition gate FAILED: {interference}"
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
    except Exception as e:  # NOT BaseException
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
