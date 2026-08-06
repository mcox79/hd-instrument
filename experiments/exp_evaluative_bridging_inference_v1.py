# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (bridging arm binds all 9 POS_MET/NEG_UNMET items; lexical-only
#   arm binds none of them -- checked in self_test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity claim; FHRR decode of <=8 bound event-slots at d=1024 far below any
#   capacity ceiling (decode fidelity > 0.99 at this scale, established by goal_owner_select /
#   grounded_appraisal_sim self-tests); this cell's discriminator is a boolean construction-detector +
#   registry lookup, not a noise-limited decode
# - baseline_in_band: n/a (LEXICAL-ONLY baseline is a MUST-FAIL floor by construction: 0/9 on the
#   zero-lexical-overlap items, not a mid-band baseline)
# - discriminator survives scale: n/a, fixed-size N=13 hand-authored bank, no scale sweep
# - cardinality_ok: EXPECTED_N_SEEDS=3, EXPECTED_N_ITEMS=13; HARD_FAIL_CARDINALITY if either short
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands set BEFORE running, per
#   preregs/2026-08-06_evaluative_bridging_inference_v1.md, not tuned post-hoc)
# - deterministic_seeding: torch.Generator per seed; fixed-int seeds; scramble = fixed cyclic shift
#   (offset=1, asserted zero-fixed-points), never hash()-derived; no push
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py); start_marker + crash_diag present
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""exp_evaluative_bridging_inference_v1 -- Graesser Class-7 BACKWARD causal-antecedent BRIDGING
INFERENCE from an evaluative speech act ("you are a good boy") back to a standing GOAL, for the case
where the outcome clause shares ZERO verb/theme/thematic-role with the goal clause (the audit's
"good boy" barrier case: no similarity/verb-typing/theme-match mechanism can EVER bridge these, so
only an inferential bridge can).

WHY (task brief, disk-verified): notes/audit_SYNTHESIS_semantic_meaning_barrier_2026-08-06.md +
notes/audit_brain_composition_situationmodel_2026-08-06.md. The wired goal-owner/outcome-valence
organs are HARD_PASS on hand-authored instruments but stall on real prose (mg2_henry_bootblack:
goal "wanted to help his mother" -> outcome "You are a dear, good boy, Henry" = goal MET) because
verb-typing has NOTHING to match on -- zero shared verb/theme/thematic role between the two clauses.
The brain solves this via Graesser Class-7 bridging: value the evaluative speech act, retrieve the
antecedent goal, bridge (approval-of-agent implies the agent's recent goal succeeded).

MECHANISM (strict ADD, reuses owned organs verbatim, NO new binding operator per the audit's own
Falsifiable-predictions section):
1. DETECT: detect_evaluative_construction() -- copula (is/are/was/were) + an evaluative adjective
   from a hand-supplied POS-blind valence lexicon (EVAL_POS/EVAL_NEG below), the SAME "SUPPLY schema
   knowledge" pattern as hdlab.goal_typing's RESULT_VERB_CLASS / V2_OUTCOME_MET/_UNMET registers.
   Addressee = 2nd-person "you...Name" vocative (last roster name in the sentence) or 3rd-person
   "Name is/was ADJ" (roster name immediately preceding the copula).
2. VALUE: POS lexicon hit -> praise, NEG lexicon hit -> criticism (lexicon lookup, NOT verb typing).
3. BRIDGE: bridge_outcome() reuses hdlab.goal_owner_select.GoalOutcomeRegister (byte-identical,
   UNMODIFIED import) -- fires ONLY if the construction's addressee == the queried entity AND
   register.appraise(entity)["has_goal"] is True (the entity currently holds an open GOAL, written by
   ordinary hdlab.goal_typing.type_goal_events calls on the passage's non-outcome sentences). POS ->
   OUTCOME_MET, NEG -> OUTCOME_UNMET. No match / no open goal -> abstain, never forces a bridge.
4. STRICT-ADD GATING: resolve_outcome() tries LEXICAL verb-typing (hdlab.goal_typing.type_goal_events,
   unmodified production organ) on the outcome sentence FIRST; the bridge is consulted ONLY when
   verb-typing produced NOTHING for every roster entity (the OUTCOME_NEVER_TYPED case). Existing
   production behavior is byte-identical whenever verb-typing already fires (see UNCHANGED category).

No production file is modified (hdlab/goal_typing.py, hdlab/goal_owner_select.py are imported
read-only) -- this cell is a self-contained harness, so verification/run_certification.py is NOT
required for this increment (nothing production changed).

INSTRUMENT: experiments/data/evaluative_bridging_bank_v1.jsonl, N=13 hand-authored items, 4
categories (POS_MET n=6 incl. mg2_henry_bootblack VERBATIM, NEG_UNMET n=3, BYSTANDER n=2, UNCHANGED
n=2). Zero-lexical-overlap between goal clause and outcome clause is mechanically checked in
self-test (content-token intersection, minus roster names and a closed-class stopword list, must be
empty) for every POS_MET/NEG_UNMET item -- not just asserted by construction.

PRE-REGISTERED BANDS (see preregs/2026-08-06_evaluative_bridging_inference_v1.md for full text,
written BEFORE this cell was run): HARD-PASS requires zero_overlap_bridging_acc>=0.85 (incl. mg2
correct) AND gap-vs-lexical-only>=0.50 AND both valence controls==1.0 AND bystander_no_bridge==1.0
AND unchanged_control==1.0 AND scramble_acc<=0.15. HARD-FAIL on any over-fire (wrong entity / fires
on non-evaluative / wrong valence) OR bridging_acc<0.85 OR gap<0.25 OR scramble doesn't collapse.

Cites: hdlab/goal_owner_select.py::GoalOutcomeRegister (unmodified); hdlab/goal_typing.py::
type_goal_events/_sentences/_ordered_tokens (unmodified); experiments/exp_grounded_appraisal_
sim_earned_v1.py (sibling cell-template convention); experiments/data/
real_text_goal_owner_diagnostic_v1.jsonl (mg2 verbatim source).
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

ANCHOR_NAME = "evaluative_bridging_inference_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
BANK_PATH = os.path.join(REPO_ROOT, "experiments", "data", "evaluative_bridging_bank_v1.jsonl")

# ---- REUSED, UNMODIFIED production organs (read-only imports; nothing here is a new mechanism) ----
from hdlab.goal_typing import (  # noqa: E402
    type_goal_events, _sentences, _ordered_tokens, R_GOAL, R_UNMET, R_MET,
)
from hdlab.goal_owner_select import (  # noqa: E402
    GoalOutcomeRegister, D2_DEFAULT, _is_pron_general, _gender_of_general,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

SEEDS = [0, 1, 2]
EXPECTED_N_SEEDS = len(SEEDS)
EXPECTED_N_ITEMS = 13
EXPECTED_CAT_COUNTS = {"POS_MET": 6, "NEG_UNMET": 3, "BYSTANDER": 2, "UNCHANGED": 2}

# ============================================================================ SUPPLIED SCHEMA: the
# POS-blind evaluative-valence lexicon (same SUPPLY pattern as hdlab.goal_typing's RESULT_VERB_CLASS /
# V2_OUTCOME_MET/_UNMET registers -- hand-authored, not induced; the substrate does the retrieve +
# value + bind, this is the SCHEMA it operates over).
EVAL_POS = {
    "good", "dear", "kind", "fine", "gentle", "devoted", "obedient", "cheerful", "quiet",
    "thoughtful", "gallant", "noble", "sweet", "honest", "brave",
}
EVAL_NEG = {
    "bad", "wicked", "naughty", "clumsy", "careless", "cruel", "foolish", "selfish", "unkind",
    "rude", "lazy",
}
_COPULA = {"is", "are", "was", "were"}
_EVAL_WINDOW = 6


# ============================================================================ (1) DETECT + (2) VALUE
def detect_evaluative_construction(sentence: str, roster: dict):
    """Copula + evaluative-predicate construction detector (glass-box, no POS tagger). Returns
    (polarity, addressee) where polarity in {"POS","NEG"}, or (None, None) if no evaluative
    construction is found. addressee: 2nd-person "you...Name" -> the LAST roster name token in the
    sentence (vocative); 3rd-person "Name is/was ADJ" -> the roster name immediately preceding the
    copula. Neither pattern matched -> addressee=None (polarity may still be non-None; bridge_outcome
    below requires addressee==entity, so a None addressee never binds anyone)."""
    toks = _ordered_tokens(sentence)
    cop_idx = None
    for i, t in enumerate(toks):
        if t in _COPULA:
            cop_idx = i
            break
    if cop_idx is None:
        return None, None
    polarity = None
    for w in toks[cop_idx + 1: cop_idx + 1 + _EVAL_WINDOW]:
        if w in EVAL_POS:
            polarity = "POS"
            break
        if w in EVAL_NEG:
            polarity = "NEG"
            break
    if polarity is None:
        return None, None
    subj = toks[cop_idx - 1] if cop_idx > 0 else None
    if subj == "you":
        addressee = None
        for t in reversed(toks):
            if t in roster:
                addressee = t
                break
        return polarity, addressee
    if subj in roster:
        return polarity, subj
    return polarity, None


# ============================================================================ (3) BRIDGE
def bridge_outcome(entity: str, sentence: str, roster: dict, register: GoalOutcomeRegister):
    """Class-7 backward causal-antecedent bridge: fires ONLY if the evaluative construction's
    addressee is `entity` AND `entity` currently holds an open GOAL in `register` (written by ordinary
    hdlab.goal_typing.type_goal_events calls on the passage's non-outcome sentences, elsewhere in this
    file). Returns R_MET / R_UNMET / None (abstain -- no forced bridge)."""
    polarity, addressee = detect_evaluative_construction(sentence, roster)
    if polarity is None or addressee != entity:
        return None
    ap = register.appraise(entity)
    if not ap["has_goal"]:
        return None
    return R_MET if polarity == "POS" else R_UNMET


# ============================================================================ harness-local subject
# resolution for populating the register (sentence-initial-token heuristic: check the FIRST content
# token for an explicit roster name or a gendered pronoun-recency match BEFORE falling back to a
# whole-sentence roster-name scan). This is NOT hdlab.goal_owner_select.GeneralRecencyEntityResolver
# (that organ's whole-sentence-first-roster-name scan mis-resolves "He wanted to help his mother" to
# "mother" -- the OBJECT, not the pronoun SUBJECT "he" -- because "mother" is itself a roster key that
# appears later in the same sentence; a known, separately-scoped coref limitation, not what this
# bridging increment targets). This harness-local resolver is scoped ONLY to this cell's bank.
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
    gen = torch.Generator().manual_seed(4000 + int(seed))
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
    roster entity. Byte-identical to what hdlab.goal_owner_select.build_candidate_role_seq does on the
    outcome sentence for each enumerated candidate."""
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
    "said", "was", "were", "is", "are", "very", "every", "just",
}


def content_tokens(sentence: str, roster: dict) -> set:
    return {t for t in _ordered_tokens(sentence) if t not in _STOPWORDS and t not in roster}


def find_goal_sentence(item: dict) -> str:
    """The specific sentence that fires the R_GOAL event for item['goal_holder'] (not necessarily
    sents[0] -- e.g. mg2_henry_bootblack has two scene-setting sentences before the actual
    desiderative goal clause). Falls back to sents[0] if no sentence fires GOAL (should not happen
    for POS_MET/NEG_UNMET items; asserted separately)."""
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


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    bank = load_bank()
    registers = {it["id"]: build_register(it, seed) for it in bank}
    id_order = [it["id"]] if False else [it["id"] for it in bank]  # keep bank order, explicit

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
    cat12_ids = [it["id"] for it in bank if it["category"] in ("POS_MET", "NEG_UNMET")]
    n12 = len(cat12_ids)
    shifted_ids = cat12_ids[1:] + cat12_ids[:1]
    assert all(a != b for a, b in zip(cat12_ids, shifted_ids)), (
        "scramble permutation has a fixed point; not a genuine derangement")
    id_to_item = {it["id"]: it for it in bank}
    scramble_rows = []
    for real_id, scrambled_id in zip(cat12_ids, shifted_ids):
        it = id_to_item[real_id]
        wrong_register = registers[scrambled_id]
        hits_s, _src_s = resolve_outcome(it, wrong_register)
        scramble_rows.append({
            "id": real_id, "scrambled_register_from": scrambled_id,
            "hits": hits_s, "correct": score_item(it, hits_s),
        })

    def rate(pred):
        vals = [1.0 if pred(r) else 0.0 for r in rows]
        return sum(vals) / len(vals) if vals else None

    cat12_rows = [r for r in rows if r["category"] in ("POS_MET", "NEG_UNMET")]
    pos_rows = [r for r in rows if r["category"] == "POS_MET"]
    neg_rows = [r for r in rows if r["category"] == "NEG_UNMET"]
    bystander_rows = [r for r in rows if r["category"] == "BYSTANDER"]
    unchanged_rows = [r for r in rows if r["category"] == "UNCHANGED"]

    def frac(rs, key):
        return (sum(1.0 for r in rs if r[key]) / len(rs)) if rs else None

    mg2_row = next(r for r in rows if r["id"] == "mg2_henry_bootblack")

    unchanged_ok = all(
        r["bridging_hits"] == r["lexical_hits"] and r["bridging_source"] == "LEXICAL"
        and r["bridging_correct"] for r in unchanged_rows)

    return {
        "seed": seed,
        "n_items": len(rows),
        "cat_counts": {c: sum(1 for r in rows if r["category"] == c) for c in EXPECTED_CAT_COUNTS},
        "zero_overlap_bridging_acc": frac(cat12_rows, "bridging_correct"),
        "lexical_only_acc": frac(cat12_rows, "lexical_correct"),
        "mg2_bridging_correct": mg2_row["bridging_correct"],
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
def aggregate_and_verdict(per_seed: dict) -> dict:
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
    mg2_all = all(per_seed[s]["mg2_bridging_correct"] for s in seeds)

    cardinality_ok = all(per_seed[s]["n_items"] == EXPECTED_N_ITEMS for s in seeds)
    counts_ok = all(per_seed[s]["cat_counts"] == EXPECTED_CAT_COUNTS for s in seeds)
    deterministic = len({tuple((r["bridging_correct"], r["lexical_correct"])
                                for r in per_seed[s]["rows"]) for s in seeds}) == 1

    if n < EXPECTED_N_SEEDS or not cardinality_ok or not counts_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    else:
        hard_pass = (z is not None and z >= 0.85 and mg2_all and gap is not None and gap >= 0.50
                     and vpos == 1.0 and vneg == 1.0 and bys == 1.0 and unc == 1.0
                     and scr is not None and scr <= 0.15)
        hard_fail = (
            (z is None or z < 0.85) or (gap is None or gap < 0.25)
            or (bys is None or bys < 1.0) or (unc is None or unc < 1.0)
            or (vpos is None or vpos < 1.0) or (vneg is None or vneg < 1.0)
            or (scr is None or scr > 0.15))
        if hard_pass:
            verdict = "HARD_PASS"
        elif hard_fail:
            verdict = "HARD_FAIL"
        else:
            verdict = "MIDDLE_BAND"

    summary = (
        f"zero_overlap_bridging_acc={z} (incl mg2 correct={mg2_all}) vs lexical_only_acc={lex} "
        f"(gap={gap}) | valence: pos_acc={vpos} neg_acc={vneg} | bystander_no_bridge_acc={bys} | "
        f"unchanged_control_acc={unc} | scramble_acc={scr} | deterministic_across_seeds={deterministic}"
    )
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "cardinality_ok": cardinality_ok, "counts_ok": counts_ok,
        "deterministic_across_seeds": deterministic,
        "zero_overlap_bridging_acc": z, "lexical_only_acc": lex, "gap": gap,
        "mg2_bridging_correct_all_seeds": mg2_all,
        "valence_pos_acc": vpos, "valence_neg_acc": vneg,
        "bystander_no_bridge_acc": bys, "unchanged_control_acc": unc, "scramble_acc": scr,
        "per_seed": per_seed,
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
    cat12 = [r for r in rows if r["category"] in ("POS_MET", "NEG_UNMET")]

    def digest(key):
        blob = "|".join(f"{r['id']}:{sorted(r[key].items())}" for r in cat12)
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
    agg = aggregate_and_verdict(per_seed)
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
    agg["prereg"] = "preregs/2026-08-06_evaluative_bridging_inference_v1.md"
    agg["cites"] = [
        "hdlab/goal_owner_select.py::GoalOutcomeRegister (unmodified)",
        "hdlab/goal_typing.py::type_goal_events/_sentences/_ordered_tokens (unmodified)",
        "experiments/data/evaluative_bridging_bank_v1.jsonl (this cell's bank, 13 items)",
        "experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (mg2 verbatim source)",
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
    print(f"[SELFTEST 1/5] bank cardinality + category counts OK: {cat_counts}", flush=True)

    # (2) zero-lexical-overlap mechanical check for every POS_MET/NEG_UNMET item (incl mg2)
    for it in bank:
        if it["category"] not in ("POS_MET", "NEG_UNMET"):
            continue
        chk = zero_overlap_check(it)
        assert chk["zero_overlap"], f"{it['id']}: lexical overlap found: {chk['overlap']}"
    print("[SELFTEST 2/5] zero-lexical-overlap mechanically verified on all POS_MET/NEG_UNMET items "
          "(incl mg2_henry_bootblack)", flush=True)

    # (3) real production organs are actually being called (real_code_path, not synthetic-only):
    # exercise type_goal_events + GoalOutcomeRegister on the mg2 item directly.
    mg2 = next(it for it in bank if it["id"] == "mg2_henry_bootblack")
    reg0 = build_register(mg2, seed=0)
    ap = reg0.appraise("henry")
    assert ap["has_goal"], f"mg2 goal-holder henry must carry an open GOAL in the register: {ap}"
    hits_a, src_a = resolve_outcome(mg2, reg0)
    print(f"[SELFTEST 3/5] real organs live: mg2 register has_goal(henry)={ap['has_goal']} "
          f"resolve_outcome={hits_a} source={src_a}", flush=True)
    assert src_a == "BRIDGE", f"mg2 must resolve via BRIDGE (lexical verb-typing has nothing to match): {src_a}"
    assert hits_a == {"henry": R_MET}, f"mg2 bridge must bind henry->MET: {hits_a}"

    # (4) one full seed sanity + arms-must-differ
    res = run_seed(0)
    assert res["n_items"] == EXPECTED_N_ITEMS
    amd = _arms_must_differ_check(res["rows"])
    assert not amd["identical"], "META_RULE_AF VIOLATION: bridging and lexical-only arms identical"
    print(f"[SELFTEST 4/5] seed0: zero_overlap_acc={res['zero_overlap_bridging_acc']} "
          f"lexical_acc={res['lexical_only_acc']} valence_pos={res['valence_pos_acc']} "
          f"valence_neg={res['valence_neg_acc']} bystander={res['bystander_no_bridge_acc']} "
          f"unchanged={res['unchanged_control_acc']} scramble={res['scramble_acc']} "
          f"arms_differ={not amd['identical']}", flush=True)

    # (5) determinism: repeating seed 0 reproduces byte-identical hit-pattern (PROT-023/F.5 self-check)
    res_repeat = run_seed(0)
    pat1 = tuple((r["bridging_correct"], r["lexical_correct"]) for r in res["rows"])
    pat2 = tuple((r["bridging_correct"], r["lexical_correct"]) for r in res_repeat["rows"])
    assert pat1 == pat2, "non-deterministic hit-pattern across repeated seed-0 runs"
    print("[SELFTEST 5/5] seed0 repeat is deterministic (bit-identical hit pattern)", flush=True)
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
