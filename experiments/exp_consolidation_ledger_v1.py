"""exp_consolidation_ledger_v1 (2026-08-02)

OBSERVABLE FLAG -> LEARN -> CONSOLIDATE LOOP, glass-box CONSOLIDATION LEDGER.

USER directive (via director task contract): "make sure the reader is flagging things it doesn't
understand and then trying to learn on its own; look into what it ISN'T able to consolidate (and
what it DOES) to make sure it's working correctly." The dangerous failure mode this cell is built
to CATCH is FALSE CONSOLIDATION -- the loop believing it kept a good fix when the fix is actually
wrong. The ledger records, per flagged item: what was flagged (+ its own error-estimate signal),
what the loop TRIED, and the OUTCOME (consolidated vs not), then INSPECTS both piles against gold.

WIRE-DON'T-ISLAND: every mechanism primitive is imported verbatim from the already-wired stack,
nothing reimplemented:
  - hdlab.coreference_resolver: build_mention_stream, enrich_dialogue, run_strict_cb_instrumented
    (baseline + margin/n_compatible flag signals), run_principle_b_deixis (the one library "fix"
    candidate -- Binding Principle B + speaker/addressee deixis over the pronoun branch only; the
    name/nominal branch is byte-identical across resolvers so a "fix" only ever changes a pronoun
    pick), mention_link_wrong (gold correctness label), bcubed.
  - hdlab.situation_model_accumulate.AccumulateRegister (via decode_coherence_margins) for the
    event-coherence flag signal.
  - hdlab.self_improving_loop.route_passage / decode_coherence_margins / decide_keep_or_revert:
    the ACTUAL coherence-gated keep/revert controller. Adoption granularity is per (passage,
    candidate) as that module mandates (see its "ADOPTION GRANULARITY" docstring) -- this cell
    does NOT stitch per-position picks from different resolutions into one hybrid array; every
    correctness check below reads mention_link_wrong against a FULL resolver output array
    (base_pred or cand_pred), never a Frankenstein mix.
  - exp_wire_coref_accumulate_situation_model_v1: ROLE_VOCAB / D / MAX_EVENT_SLOTS / SEED /
    event_slots_for (shared constants + the compact-clause-to-slot helper), imported not
    redefined, to stay consistent with the rest of the wired stack.

CONTENT: data/eval_gold_mention_role_mcguffey_v1/gold_combined_pronoun_powered_v1.jsonl (36
passages, the DENSE powered-pronoun eval -- real cross-entity ambiguity, gold available for the
correctness check). Roles are gold-supplied in this dataset (verified: all 0 missing across 36
passages / 7 distinct role labels, all inside ROLE_VOCAB) -- this cell isolates the coreference +
consolidation-loop layer, same scope declaration as exp_wire_coref_accumulate_situation_model_v1.

FLAG TYPES (each carries its OWN signal value as its error-estimate, per the task's "each flag
carries the signal value = its own error estimate"; scope = PRONOUN decisions only, because the
one wired library fix (run_principle_b_deixis) only ever changes a pronoun pick -- the name/
nominal branch is identical across every resolver in hdlab.coreference_resolver, so a flag on a
name/nominal position would have zero fix-lever available by construction and would only measure
flag-inventory noise, not loop behavior):
  - high_n_compatible:  n_compatible >= 2 (real candidate-pool competition; signal = n_compatible)
  - low_margin_tie:     strict-Cb's own selection-criterion margin == 0.0 (a genuine criterion
                        tie, the ambiguous case the flag signal is built to catch; signal = margin)
  - low_coherence:      the baseline AccumulateRegister role-decode margin at this mention's own
                        event slot falls below the dataset's own 25th percentile among pronoun
                        positions (data-driven, not a hand-picked constant; signal = base margin)
  - role_confidence / construction_confidence: NOT DETECTABLE at this layer and explicitly
                        reported as such -- role is GOLD-SUPPLIED input to this eval (the role-
                        extraction organ is a separate, already-measured ~0.60 layer, per
                        exp_wire_coref_accumulate_situation_model_v1's scope note), so there is no
                        predicted-role confidence signal to flag on here. Honest omission, not a
                        silent gap (task explicitly allows "(if detectable)").

LEARN ATTEMPT (per flagged item): does the ONE library candidate (principle_b_deixis) change the
pick at this position at all?
  - NO  -> "no_fix_available": the library has no lever here (name/nominal branch identical, or
           Principle-B/deixis guards both abstained on this pronoun). Diagnostic only, no route.
  - YES -> route the WHOLE passage through hdlab.self_improving_loop.route_passage with this
           passage's full flagged-position list (never a single-item stitch) and read whether THIS
           item's own position was inside the passage's adopted-or-reverted decision.

OUTCOME per item -- CONSOLIDATED (loop kept a route_passage-adopted resolution at this position) vs
NOT-CONSOLIDATED (no fix available, OR route_passage reverted the passage to baseline). NOT-
CONSOLIDATED items are further categorized by re-checking BOTH the individual item's own coherence
delta AND gold correctness of what the un-adopted candidate would have produced, giving an honest
GENUINELY-HARD vs INSTRUMENTATION-GAP split (see _categorize_not_consolidated docstring).

INSPECTION (the point of this cell; VET hard both ways, do not force "working"):
  1. CONSOLIDATED-CORRECTNESS / FALSE-CONSOLIDATION RATE (the dangerous number, reported first).
  2. NOT-CONSOLIDATED-HARDNESS: genuinely-hard vs instrumentation-gap breakdown.
  3. Does consolidation track the loop's own coherence signal (not noise)?
  4. Flag inventory + calibration: do higher-error-estimate flags (tie margin, low percentile
     coherence) actually correspond to a higher not-consolidated / false-consolidation rate?

VERDICT (pre-declared bands, honest both ways):
  LOOP_WORKING iff false_consolidation_rate <= FALSE_CONSOLIDATION_BAND (0.20) AND
    genuinely_hard_frac_of_not_consolidated >= GENUINE_HARD_BAND (0.50) AND coherence tracks
    (delta-positive items are not less accurate than delta-non-positive items among candidate-
    changed flagged items -- i.e. the signal the loop bases keep/revert on is not backwards).
  Else BROKEN_OR_UNDER_INSTRUMENTED, with the specific failing gate(s) named in verdict_msg.

Not dispatched to any queue (director task contract, single local diagnostic run, no pre-reg/
queue_add -- same convention as exp_coref_autonomous_fix_router_v1.py).
Self-test: python exp_consolidation_ledger_v1.py --self-test
Full:      python exp_consolidation_ledger_v1.py --timeout 120
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

import torch  # noqa: E402

from hdlab.coreference_resolver import (  # noqa: E402
    build_mention_stream,
    enrich_dialogue,
    run_strict_cb_instrumented,
    run_principle_b_deixis,
    mention_link_wrong,
)
from hdlab.self_improving_loop import (  # noqa: E402
    decode_coherence_margins,
    route_passage,
    ABSTAIN_BAND_DEFAULT,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    ROLE_VOCAB, D, MAX_EVENT_SLOTS, SEED, event_slots_for,
)
import exp_checkpoint as ckpt  # noqa: E402 (per-unit checkpoint/resume, MANDATORY per CLAUDE.md)

ANCHOR_NAME = "consolidation_ledger_v1"
_GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_PATH = os.path.join(_GOLD_DIR, "gold_combined_pronoun_powered_v1.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

CANDIDATE_NAME = "principle_b_deixis"
LOW_COHERENCE_PERCENTILE = 25.0
FALSE_CONSOLIDATION_BAND = 0.20   # HARD_PASS ceiling on false-consolidation rate
GENUINE_HARD_BAND = 0.50          # not-consolidated pile must be >= this fraction genuinely-hard


def load_passages(path: str) -> List[dict]:
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


def _seed_for(p_idx: int) -> int:
    return SEED + p_idx * 100


def _gen(seed: int) -> torch.Generator:
    return torch.Generator().manual_seed(seed)


# ---------------------------------------------------------------------------
# Pass-1 per-passage raw computation (checkpointed unit): resolver outputs, flag signals, and the
# per-position coherence-margin arrays under BOTH the full baseline and full candidate resolution.
# Nothing here depends on the dataset-wide low-coherence threshold (that is a pass-2, post-hoc cut).
# ---------------------------------------------------------------------------
def process_passage_raw(passage: dict, p_idx: int) -> dict:
    stream = enrich_dialogue(passage, build_mention_stream(passage))
    base_pred, base_decisions = run_strict_cb_instrumented(stream)
    cand_pred, _cand_actions = run_principle_b_deixis(stream)
    role_seq = [rec["role"] for rec in stream]
    event_slots, _n_slots, _c2s = event_slots_for(stream)

    base_cids = [str(c) for c in base_pred]
    cand_cids = [str(c) for c in cand_pred]
    seed = _seed_for(p_idx)
    base_dm = decode_coherence_margins(role_seq, event_slots, base_cids, ROLE_VOCAB, D,
                                       _gen(seed), MAX_EVENT_SLOTS)
    cand_dm = decode_coherence_margins(role_seq, event_slots, cand_cids, ROLE_VOCAB, D,
                                       _gen(seed), MAX_EVENT_SLOTS)

    return {
        "passage_id": passage["passage_id"],
        "stream": stream,
        "base_pred": base_pred,
        "cand_pred": cand_pred,
        "base_decisions": base_decisions,
        "base_cids": base_cids,
        "cand_cids": cand_cids,
        "role_seq": role_seq,
        "event_slots": event_slots,
        "base_dm": base_dm,
        "cand_dm": cand_dm,
        "seed": seed,
    }


# ---------------------------------------------------------------------------
# Pass-2: build the flag set (needs the dataset-wide low-coherence percentile), run route_passage
# per passage (the real controller, whole-passage adoption granularity), then the per-item ledger.
# ---------------------------------------------------------------------------
def _low_coherence_threshold(raw_units: List[dict]) -> float:
    vals = []
    for u in raw_units:
        for pos, rec in enumerate(u["stream"]):
            if rec["is_pronoun"]:
                vals.append(u["base_dm"][pos])
    if not vals:
        return float("-inf")
    vals_sorted = sorted(vals)
    idx = max(0, min(len(vals_sorted) - 1,
                     int(round((LOW_COHERENCE_PERCENTILE / 100.0) * (len(vals_sorted) - 1)))))
    return vals_sorted[idx]


def _flags_for_position(pos: int, rec: dict, decision: dict, base_margin: float,
                        low_coh_thresh: float) -> List[str]:
    flags = []
    if decision["n_compatible"] >= 2:
        flags.append("high_n_compatible")
    if decision["margin"] == 0.0:
        flags.append("low_margin_tie")
    if base_margin <= low_coh_thresh:
        flags.append("low_coherence")
    return flags


def _categorize_not_consolidated(candidate_changed: bool, baseline_wrong: bool,
                                 item_delta: Optional[float], candidate_wrong: Optional[bool],
                                 abstain_band: float) -> str:
    """NOT-CONSOLIDATED hardness category, re-checked against gold + the item's own coherence delta.

    candidate_changed=False (no library lever reached this position at all):
    - no_fix_available_baseline_wrong: baseline is wrong -- GENUINELY HARD (no lever the loop owns
      can reach this case).
    - no_fix_needed_baseline_correct: baseline already right and candidate agrees (trivially, since
      it never changed) -- a FLAG-CALIBRATION miss (fired on a case with no error), not a hardness
      case; reported separately in the flag-calibration section.

    candidate_changed=True (a fix WAS available but the loop did not adopt it) -- cross baseline
    correctness against candidate correctness (4 cells), since "no fix needed" applies here too
    whenever baseline was ALREADY correct, regardless of what the un-adopted candidate would have
    done:
    - no_fix_needed_baseline_correct_candidate_agrees: baseline correct, candidate ALSO correct --
      nothing was broken by staying reverted; not a hardness case, FLAG-CALIBRATION miss (the flag
      fired on a position with no error to fix, same bucket as the candidate_changed=False case).
    - correctly_reverted_avoided_break: baseline correct, candidate would have been WRONG -- staying
      reverted correctly avoided introducing an error. GENUINELY HARD/correct-call bucket (the
      un-adopted candidate was itself unreliable here, not an instrumentation gap).
    - genuinely_hard_correctly_reverted: baseline wrong, candidate would ALSO have been wrong, and
      the item's own coherence delta did not clear the abstain band -- the loop correctly avoided a
      bad fix (neither option was right). GENUINELY HARD.
    - correctly_reverted_noisy_positive_delta: baseline wrong, candidate would ALSO have been wrong,
      but the item's own delta was positive (a noisy false-positive signal the passage-level
      aggregate correctly overrode). GENUINELY HARD (correct outcome; per-item signal alone would
      have misled, aggregate saved it).
    - instrumentation_gap_missed_good_fix: baseline wrong, candidate WOULD have been correct, but
      the item's own coherence delta did not clear the abstain band -- the signal failed to detect a
      real improvement. INSTRUMENTATION GAP.
    - instrumentation_gap_diluted_by_passage_aggregate: baseline wrong, candidate WOULD have been
      correct, and the item's own delta DID clear the band, but the passage-level aggregate
      (route_passage averages over every changed+flagged position in the passage) vetoed adoption
      anyway -- a real per-item win diluted by co-occurring bad items in the same passage.
      INSTRUMENTATION GAP (adoption-granularity cost).
    """
    if not candidate_changed:
        return ("no_fix_available_baseline_wrong" if baseline_wrong
                else "no_fix_needed_baseline_correct")
    if not baseline_wrong:
        return ("no_fix_needed_baseline_correct_candidate_agrees" if not candidate_wrong
                else "correctly_reverted_avoided_break")
    item_delta_clears = item_delta is not None and item_delta > abstain_band
    if candidate_wrong:
        return ("correctly_reverted_noisy_positive_delta" if item_delta_clears
                else "genuinely_hard_correctly_reverted")
    return ("instrumentation_gap_diluted_by_passage_aggregate" if item_delta_clears
            else "instrumentation_gap_missed_good_fix")


GENUINELY_HARD_CATEGORIES = frozenset({
    "no_fix_available_baseline_wrong",
    "genuinely_hard_correctly_reverted",
    "correctly_reverted_noisy_positive_delta",
    "correctly_reverted_avoided_break",
})
INSTRUMENTATION_GAP_CATEGORIES = frozenset({
    "instrumentation_gap_diluted_by_passage_aggregate",
    "instrumentation_gap_missed_good_fix",
})
FLAG_CALIBRATION_MISS_CATEGORIES = frozenset({
    "no_fix_needed_baseline_correct",
    "no_fix_needed_baseline_correct_candidate_agrees",
})


def build_ledger(raw_units: List[dict], abstain_band: float = ABSTAIN_BAND_DEFAULT) -> dict:
    """The full ledger + route_passage pass. Returns {items: [...], low_coh_thresh: float,
    per_passage_route: {passage_id: route_passage_result}}."""
    low_coh_thresh = _low_coherence_threshold(raw_units)
    items: List[dict] = []
    per_passage_route: Dict[str, dict] = {}

    for u in raw_units:
        stream = u["stream"]
        base_decisions = u["base_decisions"]
        base_pred, cand_pred = u["base_pred"], u["cand_pred"]
        base_cids, cand_cids = u["base_cids"], u["cand_cids"]
        base_dm, cand_dm = u["base_dm"], u["cand_dm"]

        flagged_positions = []
        pos_flags: Dict[int, List[str]] = {}
        for pos, rec in enumerate(stream):
            if not rec["is_pronoun"]:
                continue
            fl = _flags_for_position(pos, rec, base_decisions[pos], base_dm[pos], low_coh_thresh)
            if fl:
                pos_flags[pos] = fl
                flagged_positions.append(pos)

        seed = u["seed"]
        route = route_passage(
            role_seq=u["role_seq"], event_slots=u["event_slots"],
            baseline_cluster_ids=base_cids,
            candidate_cluster_ids={CANDIDATE_NAME: cand_cids},
            flagged_positions=flagged_positions,
            role_vocab=ROLE_VOCAB, d=D,
            generator_factory=lambda seed=seed: _gen(seed),
            max_event_slots=MAX_EVENT_SLOTS, abstain_band=abstain_band,
        )
        per_passage_route[u["passage_id"]] = route
        adopted = route["adopt"] == CANDIDATE_NAME

        for pos in flagged_positions:
            candidate_changed = cand_cids[pos] != base_cids[pos]
            item_delta = (cand_dm[pos] - base_dm[pos]) if candidate_changed else None
            baseline_wrong = mention_link_wrong(pos, stream, base_pred)
            candidate_wrong = mention_link_wrong(pos, stream, cand_pred) if candidate_changed else None

            if candidate_changed and adopted:
                outcome = "CONSOLIDATED"
                final_wrong = candidate_wrong
                category = "false_consolidation" if final_wrong else "consolidated_correct"
            else:
                outcome = "NOT_CONSOLIDATED"
                final_wrong = baseline_wrong
                category = _categorize_not_consolidated(
                    candidate_changed, baseline_wrong, item_delta, candidate_wrong, abstain_band)

            items.append({
                "passage_id": u["passage_id"], "pos": pos,
                "mention_text": stream[pos]["mention_text"],
                "flags": pos_flags[pos],
                "error_estimates": {
                    "margin": base_decisions[pos]["margin"],
                    "n_compatible": base_decisions[pos]["n_compatible"],
                    "base_coherence_margin": base_dm[pos],
                },
                "candidate_changed": candidate_changed,
                "item_coherence_delta": item_delta,
                "passage_adopted_candidate": adopted,
                "passage_agg_coherence_delta": route["per_candidate"][CANDIDATE_NAME]["agg_coherence_delta"],
                "outcome": outcome,
                "category": category,
                "final_wrong": final_wrong,
            })

    return {"items": items, "low_coherence_threshold": low_coh_thresh,
           "per_passage_route": per_passage_route}


# ---------------------------------------------------------------------------
# Inspection / summary.
# ---------------------------------------------------------------------------
def summarize_ledger(ledger: dict) -> dict:
    items = ledger["items"]
    n_flagged = len(items)
    consolidated = [it for it in items if it["outcome"] == "CONSOLIDATED"]
    not_consolidated = [it for it in items if it["outcome"] == "NOT_CONSOLIDATED"]

    n_false_consolidation = sum(1 for it in consolidated if it["final_wrong"])
    false_consolidation_rate = (n_false_consolidation / len(consolidated)) if consolidated else None
    consolidated_correctness = {
        "n_consolidated": len(consolidated),
        "n_correct": len(consolidated) - n_false_consolidation,
        "n_false_consolidation": n_false_consolidation,
        "false_consolidation_rate": false_consolidation_rate,
    }

    hardness_counts = Counter(it["category"] for it in not_consolidated)
    n_genuinely_hard = sum(hardness_counts[c] for c in GENUINELY_HARD_CATEGORIES)
    n_instrumentation_gap = sum(hardness_counts[c] for c in INSTRUMENTATION_GAP_CATEGORIES)
    n_calibration_miss = sum(hardness_counts[c] for c in FLAG_CALIBRATION_MISS_CATEGORIES)
    n_hardness_scored = n_genuinely_hard + n_instrumentation_gap  # excludes calibration-miss bucket
    genuinely_hard_frac = (n_genuinely_hard / n_hardness_scored) if n_hardness_scored else None
    not_consolidated_hardness = {
        "counts_by_category": dict(hardness_counts),
        "n_genuinely_hard": n_genuinely_hard,
        "n_instrumentation_gap": n_instrumentation_gap,
        "n_flag_calibration_miss": n_calibration_miss,
        "genuinely_hard_frac_of_scored": genuinely_hard_frac,
    }

    # (3) does consolidation track the coherence signal? Among candidate-changed flagged items,
    # split by item_coherence_delta > abstain_band vs <=, report accuracy (final_wrong rate) each
    # side. A working loop's delta-positive side should have LOWER final_wrong rate.
    changed = [it for it in items if it["candidate_changed"]]
    pos_side = [it for it in changed if it["item_coherence_delta"] is not None
               and it["item_coherence_delta"] > ABSTAIN_BAND_DEFAULT]
    nonpos_side = [it for it in changed if it["item_coherence_delta"] is not None
                  and it["item_coherence_delta"] <= ABSTAIN_BAND_DEFAULT]

    def _wrong_rate(rows):
        if not rows:
            return None
        return sum(1 for it in rows if it["final_wrong"]) / len(rows)

    coherence_tracking = {
        "n_candidate_changed": len(changed),
        "n_item_delta_positive": len(pos_side),
        "n_item_delta_nonpositive": len(nonpos_side),
        "final_wrong_rate_delta_positive": _wrong_rate(pos_side),
        "final_wrong_rate_delta_nonpositive": _wrong_rate(nonpos_side),
        "tracks_signal": (
            _wrong_rate(pos_side) is not None and _wrong_rate(nonpos_side) is not None
            and _wrong_rate(pos_side) <= _wrong_rate(nonpos_side)
        ) if (pos_side and nonpos_side) else None,
    }

    # (4) flag inventory + calibration.
    flag_counts = Counter()
    for it in items:
        for f in it["flags"]:
            flag_counts[f] += 1
    calibration = {}
    for flag_name in ("high_n_compatible", "low_margin_tie", "low_coherence"):
        rows = [it for it in items if flag_name in it["flags"]]
        rows_other = [it for it in items if flag_name not in it["flags"]]
        calibration[flag_name] = {
            "n_items": len(rows),
            "not_consolidated_rate": (
                sum(1 for it in rows if it["outcome"] == "NOT_CONSOLIDATED") / len(rows)
                if rows else None),
            "not_consolidated_rate_without_flag": (
                sum(1 for it in rows_other if it["outcome"] == "NOT_CONSOLIDATED") / len(rows_other)
                if rows_other else None),
            "false_consolidation_rate": (
                sum(1 for it in rows if it["category"] == "false_consolidation")
                / max(1, sum(1 for it in rows if it["outcome"] == "CONSOLIDATED")))
                if any(it["outcome"] == "CONSOLIDATED" for it in rows) else None,
        }
    flag_inventory = {
        "n_flagged_items_total": n_flagged,
        "counts_by_flag_type": dict(flag_counts),
        "n_multi_flag_items": sum(1 for it in items if len(it["flags"]) >= 2),
        "role_construction_confidence_flag": "NOT_DETECTABLE_role_is_gold_supplied_in_this_eval",
        "calibration_by_flag_type": calibration,
    }

    return {
        "n_passages": None,  # filled by caller
        "n_flagged_items_total": n_flagged,
        "outcome_counts": {"CONSOLIDATED": len(consolidated), "NOT_CONSOLIDATED": len(not_consolidated)},
        "consolidated_correctness": consolidated_correctness,
        "not_consolidated_hardness": not_consolidated_hardness,
        "coherence_tracking": coherence_tracking,
        "flag_inventory": flag_inventory,
        "low_coherence_threshold": ledger["low_coherence_threshold"],
    }


def verdict_from_summary(summ: dict) -> tuple:
    fcr = summ["consolidated_correctness"]["false_consolidation_rate"]
    ghf = summ["not_consolidated_hardness"]["genuinely_hard_frac_of_scored"]
    tracks = summ["coherence_tracking"]["tracks_signal"]

    reasons = []
    fcr_ok = fcr is None or fcr <= FALSE_CONSOLIDATION_BAND
    if not fcr_ok:
        reasons.append(f"false_consolidation_rate={fcr:.3f} > band {FALSE_CONSOLIDATION_BAND}")
    ghf_ok = ghf is None or ghf >= GENUINE_HARD_BAND
    if not ghf_ok:
        reasons.append(f"genuinely_hard_frac={ghf:.3f} < band {GENUINE_HARD_BAND}")
    tracks_ok = tracks is None or tracks is True
    if tracks is False:
        reasons.append("coherence signal does NOT track correctness (delta-positive items are LESS "
                       "accurate than delta-nonpositive items)")

    if fcr_ok and ghf_ok and tracks_ok:
        verdict = "LOOP_WORKING"
    else:
        verdict = "BROKEN_OR_UNDER_INSTRUMENTED"
    return verdict, reasons


# ---------------------------------------------------------------------------
# Self-test: (1) real-code-path fixture with one clearly-consolidatable item (must be CONSOLIDATED
# + correct) and one genuinely-unresolvable item (must be NOT_CONSOLIDATED, categorized
# no_fix_available_baseline_wrong) -- false-consolidation MUST be 0 on this fixture. (2) real gold
# path loads + processes cleanly.
# ---------------------------------------------------------------------------
def self_test() -> None:
    # --- fixture A: clearly-consolidatable (ported from exp_coref_autonomous_fix_router_v1's
    # gold-verified good-fix dialogue fixture -- strict_cb mispicks addressee Stephen for the
    # in-quote "He"; principle_b_deixis correctly forces the absent third party Robertson). p_idx=2
    # per that cell's documented note: at this tiny fixture scale the FHRR coherence margin is seed-
    # sensitive; p_idx=2 is a fixed, non-cherry-picked-against-real-data choice that demonstrates the
    # mechanism cleanly (does not affect the FULL run, which always uses each real passage's own
    # natural p_idx).
    good = {
        "passage_id": "dlg1",
        "clauses": [
            "Farmer Robertson broke the cane.",
            '"Who did it," asked Stephen.',
            '"He broke my cane," replied Philip.',
        ],
        "entities": {
            "Robertson": [{"clause": 0, "mention": "Farmer Robertson", "role": "agent"},
                          {"clause": 2, "mention": "He", "role": "agent"}],
            "Stephen": [{"clause": 1, "mention": "Stephen", "role": "agent"}],
            "Philip": [{"clause": 2, "mention": "Philip", "role": "agent"}],
        },
    }
    # --- fixture B: genuinely unresolvable -- 3 same-gender entities taking turns, no quote/deixis
    # marker, no same-clause co-argument for Principle B to exclude -- the ONE library candidate
    # (principle_b_deixis) degrades to strict_cb's plain most-recent-subject-clause pick here, which
    # picks the WRONG (most-recent) entity; the loop has no lever to reach this case at all.
    hard = {
        "passage_id": "hard1",
        "clauses": [
            "Tom looked at the ball.",
            "Dick threw the ball to Tom.",
            "He caught it.",
        ],
        "entities": {
            "Tom": [{"clause": 0, "mention": "Tom", "role": "agent"},
                    {"clause": 2, "mention": "He", "role": "agent"}],
            "Dick": [{"clause": 1, "mention": "Dick", "role": "agent"}],
        },
    }
    raw = [process_passage_raw(good, 2), process_passage_raw(hard, 0)]
    ledger = build_ledger(raw)
    items = ledger["items"]
    by_passage = {}
    for it in items:
        by_passage.setdefault(it["passage_id"], []).append(it)

    good_items = by_passage.get("dlg1", [])
    assert len(good_items) >= 1, f"fixture A produced no flagged items: {items}"
    g = good_items[0]
    assert g["candidate_changed"], f"fixture A candidate must change the pick: {g}"
    assert g["outcome"] == "CONSOLIDATED", f"fixture A must be CONSOLIDATED: {g}"
    assert g["category"] == "consolidated_correct", f"fixture A must be gold-correct: {g}"
    assert g["final_wrong"] is False

    hard_items = by_passage.get("hard1", [])
    assert len(hard_items) >= 1, f"fixture B produced no flagged items: {items}"
    h = hard_items[0]
    assert not h["candidate_changed"], (
        f"fixture B's one library candidate must NOT reach this case (no quote/no same-clause "
        f"co-argument for Principle B): {h}")
    assert h["outcome"] == "NOT_CONSOLIDATED", f"fixture B must be NOT_CONSOLIDATED: {h}"
    assert h["category"] == "no_fix_available_baseline_wrong", (
        f"fixture B must be classified genuinely-hard/no-fix-available (baseline is wrong and the "
        f"library has no lever): {h}")

    summ = summarize_ledger(ledger)
    assert summ["consolidated_correctness"]["n_false_consolidation"] == 0, (
        f"false-consolidation must be 0 on this fixture: {summ['consolidated_correctness']}")

    # (2) real gold path sanity.
    assert os.path.exists(GOLD_PATH), f"gold missing: {GOLD_PATH}"
    passages = load_passages(GOLD_PATH)
    assert len(passages) == 36, f"expected 36 combined passages, got {len(passages)}"
    _ = process_passage_raw(passages[0], 0)

    print("[SELF-TEST] PASS: fixture A (real gold-verified fix) is CONSOLIDATED + correct; fixture "
          "B (genuinely unresolvable, no library lever reaches it) is NOT_CONSOLIDATED and "
          "correctly categorized no_fix_available_baseline_wrong; false-consolidation=0 on this "
          "fixture; real gold path loads and processes cleanly via the real substrate objects "
          "(build_mention_stream, enrich_dialogue, run_strict_cb_instrumented, "
          "run_principle_b_deixis, route_passage, decode_coherence_margins).")


# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def main(timeout_s: float) -> None:
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    passages = load_passages(GOLD_PATH)
    done = ckpt.completed_units(OUTPUT_DIR)
    n_run = 0
    for p_idx, p in enumerate(passages):
        key = ckpt.unit_key(p["passage_id"])
        if key in done:
            continue
        if time.perf_counter() - t0 > timeout_s:
            raise TimeoutError(
                f"exceeded --timeout {timeout_s}s after {n_run} new units; resume by re-running "
                f"(checkpointed).")
        raw = process_passage_raw(p, p_idx)
        ckpt.record_unit(OUTPUT_DIR, key, raw)
        n_run += 1

    units = ckpt.load_units(OUTPUT_DIR)
    assert len(units) == len(passages), f"expected {len(passages)} units, have {len(units)}"
    raw_units = [units[ckpt.unit_key(p["passage_id"])] for p in passages]

    ledger = build_ledger(raw_units)
    summ = summarize_ledger(ledger)
    summ["n_passages"] = len(passages)
    verdict, reasons = verdict_from_summary(summ)

    cc = summ["consolidated_correctness"]
    nch = summ["not_consolidated_hardness"]
    ct = summ["coherence_tracking"]
    verdict_msg = (
        f"[{verdict}] n_passages={summ['n_passages']} n_flagged_items={summ['n_flagged_items_total']} "
        f"outcomes={summ['outcome_counts']}. FALSE-CONSOLIDATION rate="
        f"{cc['false_consolidation_rate']} ({cc['n_false_consolidation']}/{cc['n_consolidated']} "
        f"consolidated items wrong vs gold) [band <= {FALSE_CONSOLIDATION_BAND}]. NOT-CONSOLIDATED "
        f"hardness: genuinely_hard={nch['n_genuinely_hard']} instrumentation_gap="
        f"{nch['n_instrumentation_gap']} flag_calibration_miss={nch['n_flag_calibration_miss']} "
        f"genuinely_hard_frac={nch['genuinely_hard_frac_of_scored']} [band >= {GENUINE_HARD_BAND}]. "
        f"coherence_tracks_signal={ct['tracks_signal']} "
        f"(wrong_rate delta+={ct['final_wrong_rate_delta_positive']} vs "
        f"delta<=0={ct['final_wrong_rate_delta_nonpositive']}). "
        + (f"FAILING_GATES: {'; '.join(reasons)}. " if reasons else "")
        + "N is modest (McGuffey scope only, 36 passages); see reproducibility_note."
    )

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "seed": SEED,
        "d": D,
        "max_event_slots": MAX_EVENT_SLOTS,
        "candidate_name": CANDIDATE_NAME,
        "abstain_band": ABSTAIN_BAND_DEFAULT,
        "false_consolidation_band": FALSE_CONSOLIDATION_BAND,
        "genuine_hard_band": GENUINE_HARD_BAND,
        "low_coherence_percentile": LOW_COHERENCE_PERCENTILE,
        "ledger_summary": summ,
        "ledger_items": ledger["items"],
        "failing_gates": reasons,
        "timeout_s": timeout_s,
        "final_metrics_atomicity": "tmp_replace",
        "checkpointed": True,
        "n_units_total": len(passages),
        "n_units_ran_this_invocation": n_run,
        "reproducibility_note": (
            "hdlab.coreference_resolver (build_mention_stream, enrich_dialogue, "
            "run_strict_cb_instrumented, run_principle_b_deixis, mention_link_wrong) and "
            "hdlab.self_improving_loop (route_passage, decode_coherence_margins, "
            "decide_keep_or_revert via route_passage) imported verbatim, never mutated. "
            "ROLE_VOCAB/D/MAX_EVENT_SLOTS/SEED/event_slots_for imported from "
            "exp_wire_coref_accumulate_situation_model_v1 for consistency with the rest of the "
            "wired stack. Not dispatched: single local diagnostic run, no pre-reg/queue_add, per "
            "director task contract."
        ),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    print(f"[{ANCHOR_NAME}] {verdict}")
    print(verdict_msg)
    print(f"metrics written to {final}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--timeout", type=float, default=120.0,
        help=("formula: 36 passages, each doing 1 baseline (instrumented) resolution + 1 candidate "
             "resolution + 2 full-passage AccumulateRegister decode-margin passes + 1 route_passage "
             "call (itself 2 more decode-margin passes); all CPU-only, <=100ms/passage on comparable "
             "cells; 120s gives generous headroom."),
    )
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(args.timeout)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
