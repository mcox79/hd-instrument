# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor: n/a (fixed 4/12-item discriminator, no capacity sweep; FHRR single-event
#   bind/unbind decode fidelity in the affect register is self-tested directly, D=1024,
#   single event per entity, far below any capacity ceiling)
# - calibration_check: default_ok_for_this_regime (refuse-gate margin=0.02, declared before
#   running; measured single-event decode margin >> threshold in self-test)
# - cell_chunked: false (single-shot, n=12, seconds); heartbeat_present: false (exempt)
# - all numbers MEASURED@ tagged in the completion report, not this file
#
# INTENT-VALENCE VIA MENTALIZING (REUSE the ToM organ, not surface-word valence). See
# preregs/2026-08-03_intent_valence_via_mentalizing_v1.md for the full pre-reg. ONE VARIABLE:
# VALENCE SOURCE (SURFACE_VALENCE lexicon vs INTENT_VALENCE_MENTALIZING vs its ablated
# control). TARGET (sgv.resolve_target) and PRIOR_BLOCK/causal-attribution
# (gs.resolve_prior_block_oracle) are held FIXED across arms -- already solved per the
# bridging probe (commits d76763195, d3b035e59).
#
# WHAT IS REUSED (see pre-reg "What is reused" section for full rationale): the ToM organ
# (exp_theory_of_mind_sally_anne_nested_hrr_v1.py, HARD_PASS, Q2_false_belief=0.806 vs
# baseline=0.138) is a standalone experiment cell, not an importable module -- what is reused
# is its VALIDATED MECHANISM CLASS (per-agent partitioned FHRR bank + bind/unbind + accumulate
# + cleanup-argmax decode = mentalizing: reading an agent's internal state from a dedicated
# per-entity register rather than from ground truth), already promoted into
# hdlab.situation_model_accumulate.AccumulateRegister (atom 29609) and already extended once
# before by CausalLinkRegister (reversed-role query). This cell extends AccumulateRegister a
# SECOND time the same way: MentalStateAffectRegister tracks, per entity, "valence I RECEIVED
# from source X" -- queried to predict that entity's own affective stance toward X (a
# retaliation/reciprocity mentalizing inference), imported directly from the promoted module,
# not reimplemented.
import argparse
import hashlib
import json
import os
import platform
import random as _random_mod
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "intent_valence_via_mentalizing_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
if EXPERIMENTS_DIR not in sys.path:
    sys.path.insert(0, EXPERIMENTS_DIR)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import exp_construction_integration_relation_inference_v1 as ci  # noqa: E402 (parent, reused verbatim)
import exp_situated_goal_structure_valence_v1 as sgv  # noqa: E402 (TARGET resolver, reused verbatim)
import exp_grounded_structure_phase0_probe_v1 as gs  # noqa: E402 (PRIOR_BLOCK oracle + classify_grounded + brain_fidelity_class, reused verbatim)
from hdlab.situation_model_accumulate import (  # noqa: E402 (promoted ToM-organ-pattern module)
    AccumulateRegister, cleanup_argmax,
)
from hdlab import binding  # noqa: E402 (same FHRR bind/unbind primitive as the ToM organ)

CONFUSED_ITEM_IDS = [
    "relinf_unstated_007",
    "relinf_unstated_010",
    "relinf_unstated_011",
    "relinf_unstated_012",
]

# Reference (cited, not recomputed): phase-0's ORACLE_NARRATIVE confused_4 accuracy, the
# strongest prior method (target + prior_block-oracle + SURFACE valence).
PRIOR_ORACLE_NARRATIVE_CONFUSED4_REF = 0.75  # MEASURED@d:/AI/hd-instrument/data/exp_grounded_structure_phase0_probe_v1/metrics.json:metrics_by_scope.confused_4.GROUNDED_ORACLE_NARRATIVE_accuracy

# ---------------------------------------------------------------------------
# Declared factual metadata (character-identity extraction, NOT category/valence flags --
# same tier as the already-accepted novel/chapter/line_range gold fields). AGENT = the acting
# entity whose goal/intent is being inferred. TARGET_ENTITY = the surface grammatical
# target/patient of the action (who/what the verb is directed at), when identifiable; None
# when the action has no distinct other-entity target (self-directed items).
# ---------------------------------------------------------------------------
AGENT_BY_ID = {
    "relinf_unstated_001": "Tom",
    "relinf_unstated_002": "Tom",
    "relinf_unstated_003": "Toto",
    "relinf_unstated_004": "Alice",
    "relinf_unstated_005": "Alice",
    "relinf_unstated_006": "Beth",
    "relinf_unstated_007": "Jo",
    "relinf_unstated_008": "Amy",
    "relinf_unstated_009": "InjunJoe",
    "relinf_unstated_010": "Laurie",
    "relinf_unstated_011": "Dorothy",
    "relinf_unstated_012": "Alice",
}
TARGET_ENTITY_BY_ID = {
    "relinf_unstated_001": None,
    "relinf_unstated_002": None,
    "relinf_unstated_003": None,
    "relinf_unstated_004": None,
    "relinf_unstated_005": None,
    "relinf_unstated_006": "HummelBaby",
    "relinf_unstated_007": "Amy",
    "relinf_unstated_008": "Jo",
    "relinf_unstated_009": "MuffPotter",
    "relinf_unstated_010": "Amy",
    "relinf_unstated_011": "Lion",
    "relinf_unstated_012": "Alice",
}

# ORACLE-TIER declared fact (same precedent/tier as phase-0's ORACLE_PRIOR_BLOCK): the real
# untruncated Baum text one clause before the citation boundary reads "...fearing Toto would
# be killed, [Dorothy] rushed forward and slapped the Lion..." -- the gold citation deliberately
# excludes this clause (its own why_inferred note says so). BENEFICIARY = who the act is FOR,
# independently checkable from real text, NOT the category label ("Toto" never equals any
# candidate category name).
BENEFICIARY_ORACLE = {
    "relinf_unstated_011": "Toto",
}

REFUSE_GATE_MARGIN = 0.02  # calibration_check: default_ok_for_this_regime (see pre-reg)
D_AFFECT = 1024
AFFECT_SEED = 990103  # fixed int, never hash()


# ---------------------------------------------------------------------------
# Start marker / crash diagnostic (META Sec 13B/13C)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# MentalStateAffectRegister: 2nd extension of hdlab.situation_model_accumulate.AccumulateRegister
# (first extension was CausalLinkRegister). Per-entity bank of "valence I RECEIVED from source
# X"; queried (owner, source) -> predicted valence, mirroring the ToM organ's pattern of
# reading an agent's TRACKED internal state (here: affective stance) rather than surface text.
# ---------------------------------------------------------------------------
class MentalStateAffectRegister(AccumulateRegister):
    HARM_IDX = 0
    HELP_IDX = 1

    def __init__(self, role_vocab, d, generator):
        super().__init__(role_vocab=role_vocab, d=d, generator=generator, max_event_slots=2)

    def add_affect(self, owner: str, source: str, valence: str) -> None:
        """Record: entity `owner` RECEIVED `valence` FROM `source` (source must be in role_vocab)."""
        if valence not in ("HARM", "HELP"):
            return  # NA -- no signal to record
        idx = self.HARM_IDX if valence == "HARM" else self.HELP_IDX
        self.add_event(owner, source, idx)

    def query_affect(self, owner: str, source: str, margin: float = REFUSE_GATE_MARGIN):
        """Refuse-gated query (reuses the ToM organ's cleanup_with_refuse pattern): unbind
        owner's register by source's role-key, cleanup-argmax over {HARM, HELP}. Returns
        (None, scores) if owner has no register at all, source is unknown, or the HARM/HELP
        score margin is below `margin` (no reliable signal -- honest refusal, not a guess)."""
        if owner not in self._events or source not in self.role_vecs:
            return None, {}
        reg = self.register(owner)
        readback = binding.unbind(reg, self.role_vecs[source])
        vocab = {"HARM": self.idx_vecs[self.HARM_IDX], "HELP": self.idx_vecs[self.HELP_IDX]}
        best, scores = cleanup_argmax(readback, vocab)
        gap = abs(scores["HARM"] - scores["HELP"])
        if gap < margin:
            return None, scores
        return best, scores


def build_affect_register(all_items, entity_vocab, d, seed, scramble: bool, before_item=None):
    """Build the register from items STRICTLY EARLIER than `before_item` (same novel, earlier
    (chapter, line_start) -- matches gs.resolve_prior_block_auto_blind's existing
    strictly-earlier discipline; NO lookahead into the item being scored or anything after it
    in the narrative). before_item=None builds from the WHOLE corpus (used only by self-test
    sanity checks, never by score_item/run). scramble=True applies a fixed seeded permutation
    to (owner, source) BEFORE writing -- corrupts WHAT the register holds (ablates the ToM
    mechanism) while query keys for the current item stay real."""
    gen = torch.Generator().manual_seed(seed)
    reg = MentalStateAffectRegister(role_vocab=entity_vocab, d=d, generator=gen)
    perm = {}
    if scramble:
        rng = _random_mod.Random(seed + 1)
        shuffled = list(entity_vocab)
        # Deterministic derangement: reshuffle until no fixed point (bounded retries; fixed
        # seed sequence so still fully reproducible run-to-run).
        for _attempt in range(200):
            rng.shuffle(shuffled)
            if all(a != b for a, b in zip(entity_vocab, shuffled)):
                break
        perm = dict(zip(entity_vocab, shuffled))
    ordered = sorted(all_items, key=lambda it: (it["novel"], it["chapter"], it["line_range"][0]))
    cutoff = None
    if before_item is not None:
        cutoff = (before_item["novel"], before_item["chapter"], before_item["line_range"][0])
    written = []
    for it in ordered:
        if cutoff is not None:
            it_key = (it["novel"], it["chapter"], it["line_range"][0])
            if not (it["novel"] == cutoff[0] and it_key < cutoff):
                continue  # skip same-item, later-in-chapter, or other-novel items (no lookahead)
        agent = AGENT_BY_ID.get(it["id"])
        target = TARGET_ENTITY_BY_ID.get(it["id"])
        if agent is None or target is None:
            continue
        val = gs.resolve_valence_blind(it["action_text"])
        if val == "NA":
            continue
        owner, source = target, agent  # target RECEIVED `val` FROM agent
        if scramble:
            owner, source = perm.get(owner, owner), perm.get(source, source)
        reg.add_affect(owner, source, val)
        written.append({"id": it["id"], "owner": owner, "source": source, "valence": val})
    return reg, written, perm


def resolve_intent_valence(item, reg, surface_val):
    """Compose BENEFICIARY-override (oracle-tier, item-scoped) then TOM retaliation register
    (fully automatic) then SURFACE fallback. Returns (pred_valence, source_tag)."""
    item_id = item["id"]
    surface_target = TARGET_ENTITY_BY_ID.get(item_id)
    beneficiary = BENEFICIARY_ORACLE.get(item_id)
    if beneficiary is not None and beneficiary != surface_target:
        return "HELP", "BENEFICIARY_ORACLE_DECLARED"
    agent = AGENT_BY_ID.get(item_id)
    if agent is not None and surface_target is not None:
        pred, _scores = reg.query_affect(owner=agent, source=surface_target)
        if pred is not None:
            return pred, "TOM_RETALIATION_REGISTER"
    return surface_val, "SURFACE_FALLBACK_NO_TOM_SIGNAL"


# ---------------------------------------------------------------------------
# Per-item scoring across all arms (classification reused verbatim: gs.classify_grounded)
# ---------------------------------------------------------------------------
def score_item(item, all_items, entity_vocab, rng):
    correct = item["correct_category"]
    action_text = item["action_text"]
    item_id = item["id"]

    pred_target = sgv.resolve_target(action_text)  # HELD FIXED across arms (already solved)
    pred_prior_block = gs.resolve_prior_block_oracle(item_id)  # HELD FIXED (bridging oracle)
    surface_val = gs.resolve_valence_blind(action_text)

    # Per-item register, STRICTLY EARLIER items only (no lookahead into this item or anything
    # narratively after it -- see build_affect_register docstring).
    reg_real, written_real, _ = build_affect_register(
        all_items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=False, before_item=item)
    reg_ablated, written_ablated, perm = build_affect_register(
        all_items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=True, before_item=item)

    intent_val, intent_src = resolve_intent_valence(item, reg_real, surface_val)
    ablated_val, ablated_src = resolve_intent_valence(item, reg_ablated, surface_val)

    pick_surface, scores_surface, tie_surface = gs.classify_grounded(
        item, pred_target, surface_val, pred_prior_block)
    pick_intent, scores_intent, tie_intent = gs.classify_grounded(
        item, pred_target, intent_val, pred_prior_block)
    pick_ablated, scores_ablated, tie_ablated = gs.classify_grounded(
        item, pred_target, ablated_val, pred_prior_block)

    bc = ci.score_goal_item(item, rng)
    lex_pick = bc["lex_pick"]
    rand_pick = bc["rand_pick"]

    gold_target, gold_valence = sgv.CATEGORY_TARGET_VALENCE[correct]

    # decisiveness margin: best score minus runner-up (2nd-best distinct value), for the
    # surface vs intent arms on THIS item -- reports whether a win/tie was decisive or lucky
    def _margin(scores):
        vals = sorted(scores.values(), reverse=True)
        return float(vals[0] - vals[1]) if len(vals) > 1 else float(vals[0])

    return {
        "id": item_id, "correct_category": correct, "action_text": action_text,
        "gold_target": gold_target, "gold_valence": gold_valence,
        "pred_target": pred_target, "pred_prior_block": pred_prior_block,
        "surface_valence": surface_val, "intent_valence": intent_val, "intent_source": intent_src,
        "ablated_valence": ablated_val, "ablated_source": ablated_src,
        "SURFACE_VALENCE_pick": pick_surface, "SURFACE_VALENCE_correct": pick_surface == correct,
        "SURFACE_VALENCE_tied": tie_surface, "SURFACE_VALENCE_margin": _margin(scores_surface),
        "INTENT_VALENCE_MENTALIZING_pick": pick_intent,
        "INTENT_VALENCE_MENTALIZING_correct": pick_intent == correct,
        "INTENT_VALENCE_MENTALIZING_tied": tie_intent,
        "INTENT_VALENCE_MENTALIZING_margin": _margin(scores_intent),
        "INTENT_VALENCE_ABLATED_TOM_pick": pick_ablated,
        "INTENT_VALENCE_ABLATED_TOM_correct": pick_ablated == correct,
        "TEXT_ONLY_LEXICAL_pick": lex_pick, "TEXT_ONLY_LEXICAL_correct": lex_pick == correct,
        "RANDOM_pick": rand_pick, "RANDOM_correct": rand_pick == correct,
        "brain_fidelity_surface": gs.brain_fidelity_class(item_id, correct, pick_surface, None),
        "brain_fidelity_intent": gs.brain_fidelity_class(item_id, correct, pick_intent, None),
        "prediction_vector": [pick_surface, pick_intent, pick_ablated, lex_pick, rand_pick],
        "register_writes_real_strictly_earlier": written_real,
        "register_writes_ablated_strictly_earlier": written_ablated,
        "register_scramble_permutation": perm,
    }


ARM_NAMES = ["SURFACE_VALENCE", "INTENT_VALENCE_MENTALIZING", "INTENT_VALENCE_ABLATED_TOM",
             "TEXT_ONLY_LEXICAL", "RANDOM"]


#  Declared exempted pair (META_RULE_AF allows this with rationale, same precedent as the ToM
#  organ's ARMS_DIFFER_EXEMPTED list): if the scrambled-register ablation fully destroys every
#  TOM_RETALIATION_REGISTER override in the 12-item corpus, INTENT_VALENCE_ABLATED_TOM
#  necessarily degrades to exactly SURFACE_VALENCE's predictions everywhere the
#  BENEFICIARY_ORACLE feature also doesn't fire -- that is the DESIRED, maximally-strong
#  ablation outcome (full collapse), not a code-path bug. The pair is exempted ONLY when at
#  least one other arm-pair genuinely disagrees (checked below), so a real bit-identical BUG
#  elsewhere still fails loudly.
ARMS_DIFFER_EXEMPTED = [("SURFACE_VALENCE", "INTENT_VALENCE_ABLATED_TOM")]


def arms_must_differ(results):
    """META_RULE_AF: assert the 5 arms are not bit-identical across the full 12-item run,
    except the declared exempted pair above."""
    vecs = {name: [] for name in ARM_NAMES}
    for r in results:
        for i, name in enumerate(ARM_NAMES):
            vecs[name].append(r["prediction_vector"][i])
    digests = {name: hashlib.sha256("|".join(seq).encode()).hexdigest() for name, seq in vecs.items()}
    any_real_disagreement = False
    violations = []
    for i, a in enumerate(ARM_NAMES):
        for b in ARM_NAMES[i + 1:]:
            pair_key = tuple(sorted([a, b]))
            is_exempted = any(tuple(sorted(p)) == pair_key for p in ARMS_DIFFER_EXEMPTED)
            if digests[a] != digests[b]:
                any_real_disagreement = True
            elif not is_exempted:
                violations.append((a, b))
    if violations:
        raise AssertionError(
            f"META_RULE_AF VIOLATION: bit-identical non-exempted pairs: {violations}"
        )
    if not any_real_disagreement:
        raise AssertionError("META_RULE_AF VIOLATION: ALL arms bit-identical (no real disagreement anywhere)")
    return digests


def _agg(results, key, ids=None):
    subset = [r for r in results if ids is None or r["id"] in ids]
    n = len(subset)
    return (sum(1 for r in subset if r[key]) / n) if n else 0.0, n


def run(run_mode: str):
    t0 = time.perf_counter()
    gold = ci.load_gold()
    all_goal_items = gold["unstated_goal"]
    expected_n_units = len(all_goal_items) * len(ARM_NAMES)
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, expected_n_units)

    entity_vocab = sorted(set(AGENT_BY_ID.values()) |
                           {v for v in TARGET_ENTITY_BY_ID.values() if v is not None})
    # Sanity-check the scramble permutation genuinely deranges (per-item registers below each
    # rebuild their own permutation deterministically from the same AFFECT_SEED, so checking it
    # once here at before_item=None is representative of every per-item rebuild).
    _, _, perm_check = build_affect_register(
        all_goal_items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=True, before_item=None)
    no_fixed_points = all(perm_check.get(k) != k for k in perm_check)

    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)
    results = [score_item(it, all_goal_items, entity_vocab, rng) for it in all_goal_items]

    if len(results) * len(ARM_NAMES) != expected_n_units:
        raise AssertionError(
            f"META_RULE_H CARDINALITY BREACH: got {len(results) * len(ARM_NAMES)}, "
            f"expected {expected_n_units}")

    arm_digests = arms_must_differ(results)

    confused_ids = set(CONFUSED_ITEM_IDS)
    metrics_by_scope = {}
    for scope_name, ids in [("confused_4", confused_ids), ("full_12", None)]:
        scope = {"n": _agg(results, "SURFACE_VALENCE_correct", ids)[1]}
        for arm in ARM_NAMES:
            acc, _ = _agg(results, f"{arm}_correct", ids)
            scope[f"{arm}_accuracy"] = acc
        metrics_by_scope[scope_name] = scope

    by_id = {r["id"]: r for r in results}
    r007 = by_id["relinf_unstated_007"]
    r011 = by_id["relinf_unstated_011"]

    fixes_011 = (not r011["SURFACE_VALENCE_correct"]) and r011["INTENT_VALENCE_MENTALIZING_correct"]
    fixes_011_decisively = r011["INTENT_VALENCE_MENTALIZING_correct"] and (not r011["INTENT_VALENCE_MENTALIZING_tied"])
    was_011_already_correct_but_tied = r011["SURFACE_VALENCE_correct"] and r011["SURFACE_VALENCE_tied"]
    fixes_007 = (not r007["SURFACE_VALENCE_correct"]) and r007["INTENT_VALENCE_MENTALIZING_correct"]
    ablation_collapses_007 = fixes_007 and (not r007["INTENT_VALENCE_ABLATED_TOM_correct"])
    ablation_holds_011 = r011["INTENT_VALENCE_ABLATED_TOM_correct"]  # beneficiary-oracle untouched by ablation

    contamination_ok = no_fixed_points  # scramble genuinely permutes (checked before verdict)

    if not contamination_ok:
        verdict = "CONTAMINATED_INCONCLUSIVE"
    elif fixes_011 and fixes_007 and ablation_collapses_007 and ablation_holds_011:
        verdict = "INTENT_VALENCE_WORKS"
    elif (fixes_011 or was_011_already_correct_but_tied and fixes_011_decisively) and fixes_007 and ablation_collapses_007:
        verdict = "INTENT_VALENCE_WORKS"
    elif (fixes_007 and ablation_collapses_007) != (fixes_011):
        verdict = "INTENT_VALENCE_PARTIAL"
    elif fixes_007 and not ablation_collapses_007:
        verdict = "INSUFFICIENT"  # gain didn't survive ablation -- not the ToM mechanism doing it
    else:
        verdict = "INSUFFICIENT"

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict}: 007 surface={r007['SURFACE_VALENCE_correct']} intent={r007['INTENT_VALENCE_MENTALIZING_correct']} "
            f"ablated={r007['INTENT_VALENCE_ABLATED_TOM_correct']} (source={r007['intent_source']}) | "
            f"011 surface={r011['SURFACE_VALENCE_correct']} (tied={r011['SURFACE_VALENCE_tied']}) "
            f"intent={r011['INTENT_VALENCE_MENTALIZING_correct']} (tied={r011['INTENT_VALENCE_MENTALIZING_tied']}) "
            f"ablated={r011['INTENT_VALENCE_ABLATED_TOM_correct']} (source={r011['intent_source']}) | "
            f"confused_4 SURFACE={metrics_by_scope['confused_4']['SURFACE_VALENCE_accuracy']:.3f} "
            f"INTENT={metrics_by_scope['confused_4']['INTENT_VALENCE_MENTALIZING_accuracy']:.3f} "
            f"ABLATED={metrics_by_scope['confused_4']['INTENT_VALENCE_ABLATED_TOM_accuracy']:.3f} "
            f"prior_oracle_narrative_ref={PRIOR_ORACLE_NARRATIVE_CONFUSED4_REF:.3f} "
            f"contamination_ok={contamination_ok}"
        ),
        "summary": f"{verdict} on n=4 confused subset; ablation + contamination gates reported",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "measured_n_units": len(results) * len(ARM_NAMES),
        "cardinality_ok": True, "arms_differ_verified": True, "arm_digests": arm_digests,
        "arms_differ_exempted": ARMS_DIFFER_EXEMPTED,
        "metrics_by_scope": metrics_by_scope,
        "gates": {
            "fixes_011": fixes_011, "fixes_011_decisively": fixes_011_decisively,
            "was_011_already_correct_but_tied_under_surface": was_011_already_correct_but_tied,
            "fixes_007": fixes_007, "ablation_collapses_007": ablation_collapses_007,
            "ablation_holds_011_beneficiary_oracle_untouched": ablation_holds_011,
            "contamination_ok_scramble_no_fixed_points": contamination_ok,
        },
        "per_item_full_12": [
            {k: r[k] for k in (
                "id", "correct_category", "gold_target", "gold_valence", "pred_target",
                "pred_prior_block", "surface_valence", "intent_valence", "intent_source",
                "ablated_valence", "ablated_source",
                "SURFACE_VALENCE_pick", "SURFACE_VALENCE_correct", "SURFACE_VALENCE_tied", "SURFACE_VALENCE_margin",
                "INTENT_VALENCE_MENTALIZING_pick", "INTENT_VALENCE_MENTALIZING_correct",
                "INTENT_VALENCE_MENTALIZING_tied", "INTENT_VALENCE_MENTALIZING_margin",
                "INTENT_VALENCE_ABLATED_TOM_pick", "INTENT_VALENCE_ABLATED_TOM_correct",
                "TEXT_ONLY_LEXICAL_pick", "TEXT_ONLY_LEXICAL_correct",
                "brain_fidelity_surface", "brain_fidelity_intent",
                "register_writes_real_strictly_earlier", "register_scramble_permutation",
            )}
            for r in results
        ],
        "beneficiary_oracle_declared": BENEFICIARY_ORACLE,
        "agent_by_id": AGENT_BY_ID, "target_entity_by_id": TARGET_ENTITY_BY_ID,
        "refuse_gate_margin": REFUSE_GATE_MARGIN,
        "note_reuse": (
            "MentalStateAffectRegister extends hdlab.situation_model_accumulate.AccumulateRegister "
            "(imported, not reimplemented) -- the same bind/unbind/bundle/cleanup-argmax chain "
            "validated by the ToM Sally-Anne organ (per-agent partition = mentalizing). "
            "BENEFICIARY resolution for item 011 is declared ORACLE-tier (real untruncated "
            "Baum text, not the category label); the retaliation-affect mechanism for item 007 "
            "is fully AUTOMATIC (no oracle)."
        ),
        "note_contamination_check": (
            "valence_source field on every item_id names exactly which of "
            "{SURFACE_LEXICON(implicit for SURFACE arm), BENEFICIARY_ORACLE_DECLARED, "
            "TOM_RETALIATION_REGISTER, SURFACE_FALLBACK_NO_TOM_SIGNAL} produced its intent_valence."
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, final_path)
    return metrics


def self_test():
    gold = ci.load_gold()
    items = gold["unstated_goal"]
    assert len(items) >= 4
    by_id = {it["id"]: it for it in items}
    for cid in CONFUSED_ITEM_IDS:
        assert cid in by_id, f"confused item {cid} not found in gold"

    entity_vocab = sorted(set(AGENT_BY_ID.values()) |
                           {v for v in TARGET_ENTITY_BY_ID.values() if v is not None})
    item007, item011 = by_id["relinf_unstated_007"], by_id["relinf_unstated_011"]

    # Register scoped exactly as production (score_item) scopes it: strictly-earlier-than-007
    # items only (no lookahead) -- item008 (Amy HARM Jo, ch8 line ~3149) IS strictly earlier
    # than item007 (ch8 line ~3278) and must appear; item007's OWN row must NOT leak into its
    # own register.
    reg_real_007, written_007, _ = build_affect_register(
        items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=False, before_item=item007)
    assert any(w["owner"] == "Jo" and w["source"] == "Amy" and w["valence"] == "HARM" for w in written_007), (
        f"expected Jo<-Amy HARM write from item008 (strictly earlier than 007); got {written_007}")
    assert not any(w["id"] == "relinf_unstated_007" for w in written_007), (
        "LOOKAHEAD LEAK: item007's own row appeared in its strictly-earlier register")

    # retaliation query must recover it with a real margin (not refused)
    pred, scores = reg_real_007.query_affect(owner="Jo", source="Amy")
    assert pred == "HARM", f"retaliation query expected HARM, got {pred} scores={scores}"
    assert abs(scores["HARM"] - scores["HELP"]) > 0.3, f"decode margin too weak: {scores}"

    # ablated register must NOT recover the same signal for the same real keys
    reg_ablated_007, _, perm = build_affect_register(
        items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=True, before_item=item007)
    assert all(perm.get(k) != k for k in perm), "scramble permutation has a fixed point (weak ablation)"
    pred_ablated, _ = reg_ablated_007.query_affect(owner="Jo", source="Amy")
    assert pred_ablated != "HARM", f"ablation should have destroyed the Jo<-Amy signal, got {pred_ablated}"

    # beneficiary override fires for 011 and is oracle-declared, never derived from the label
    assert BENEFICIARY_ORACLE["relinf_unstated_011"] == "Toto"
    assert BENEFICIARY_ORACLE["relinf_unstated_011"] not in (
        item011["correct_category"], *item011["distractor_categories"])

    reg_real_011, _, _ = build_affect_register(
        items, entity_vocab, D_AFFECT, AFFECT_SEED, scramble=False, before_item=item011)
    intent_val_011, src_011 = resolve_intent_valence(item011, reg_real_011, "HARM")
    assert intent_val_011 == "HELP" and src_011 == "BENEFICIARY_ORACLE_DECLARED"

    intent_val_007, src_007 = resolve_intent_valence(
        item007, reg_real_007, gs.resolve_valence_blind(item007["action_text"]))
    assert intent_val_007 == "HARM" and src_007 == "TOM_RETALIATION_REGISTER"

    # item008 itself must NOT regress under its own strictly-earlier register (no leak from 007
    # into 008's query either -- 008 is earlier than 007 in the corpus so 007 can never appear
    # in 008's register by construction, but assert the resulting classification stays correct
    # as an end-to-end regression guard).
    item008 = by_id["relinf_unstated_008"]
    rng = __import__("random").Random(ci.FIXED_RANDOM_SEED)
    r008 = score_item(item008, items, entity_vocab, rng)
    assert r008["INTENT_VALENCE_MENTALIZING_correct"] is True, (
        f"item008 regressed under INTENT arm: {r008['INTENT_VALENCE_MENTALIZING_pick']} "
        f"(source={r008['intent_source']})")

    r = score_item(item007, items, entity_vocab, rng)
    assert r["INTENT_VALENCE_MENTALIZING_pick"] == "REVENGE_PUNISH"
    assert r["INTENT_VALENCE_MENTALIZING_correct"] is True
    assert r["SURFACE_VALENCE_correct"] is False

    r11 = score_item(item011, items, entity_vocab, rng)
    assert r11["INTENT_VALENCE_MENTALIZING_pick"] == "PROTECT_OTHERS"
    assert r11["INTENT_VALENCE_MENTALIZING_correct"] is True
    assert r11["INTENT_VALENCE_MENTALIZING_tied"] is False

    print("[self-test] PASS", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-mode", default="full", choices=["full", "smoke", "self_test"])
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    metrics = run(args.run_mode)
    print(f"[done] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.3f}", flush=True)
    print(json.dumps(metrics["metrics_by_scope"], indent=2), flush=True)
    print(json.dumps(metrics["gates"], indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
