"""exp_coherence_aggregate_discriminates_goal_outcome_v1 -- does the PRODUCTION AGGREGATE mechanism
(hdlab/self_improving_loop.py::route_passage, whole-resolution aggregate margin-delta gated by
decide_keep_or_revert) discriminate a COHERENT goal-owner whole-resolution from a RECENCY-driven
whole-resolution on the goal-outcome instance -- the grain at which coref is production-validated --
vs the ATOMIC single-position grain that HARD_FAILED in exp_coherence_margin_discriminates_goal_
outcome_v1 (commit 15d8fd627, load-matched single-position delta EXACTLY 0.0 for coref/causal/
goal_outcome alike)?

THE CLAIM UNDER TEST: production coref discrimination (67% oracle-gain recovery, atom 29609,
exp_coref_autonomous_fix_router_v1) is an EMERGENT property of route_passage's WHOLE-PASSAGE
MANY-POSITION AGGREGATE (mean coherence-margin delta over flagged positions), not the atomic
per-position read. This cell calls route_passage DIRECTLY (the wired hdlab function, not an
inlined formula) on 3 arms:
  A) coref POSITIVE CONTROL -- reproduce atom 29609's aggregate discrimination on the same
     g5g6_reviewed McGuffey passages, same config (role_vocab, d, max_event_slots, per-passage
     seed formula). MUST fire or the harness itself is dead and nothing else is interpretable.
  B) goal_outcome TREATMENT -- synthetic multi-position items (goal-owner referenced at >=2
     positions across a dispersed goal-block, per exp_situation_model_goal_outcome_dimension_v1's
     naturalistic design), baseline=recency whole-resolution, candidate=coherent whole-resolution,
     ANTI-RECENCY BY CONSTRUCTION (true owner is never the most-recent entity at the outcome
     positions). 3 load-direction sub-arms (matched / foilheavy / ownerheavy) rule out the prior
     cell's load-artifact confound explicitly.
  C) SHUFFLED-STRUCTURE CONTROL -- role_seq reversed (deterministic index reversal, entities/loads/
     positions unchanged) on the go_matched items. A real structural-coherence signal must COLLAPSE;
     if it doesn't, the aggregate signal is a load/position artifact, not structural coherence.

ADJUDICATES: does aggregate-decodability-coherence (the mechanism that works for coref) EXTEND to
the goal-outcome RELATIONAL binding, or does goal-outcome pattern with the causal instance (which
needed a different quantity -- reach_value/M_backward, per notes/research_drill_biology_led_causal_
coherence_credit_assignment_2026-08-03.md -- not a decodability signal)?

Cites: preregs/2026-08-04_coherence_aggregate_discriminates_goal_outcome_v1.md;
hdlab/self_improving_loop.py (route_passage, decode_coherence_margins, decide_keep_or_revert --
reused verbatim); experiments/exp_coref_autonomous_fix_router_v1.py (atom 29609 positive-control
config); experiments/exp_situation_model_goal_outcome_dimension_v1.py (GO role vocab, sourced);
experiments/exp_coherence_margin_discriminates_goal_outcome_v1.py (the atomic-grain HARD_FAIL this
builds on); experiments/exp_wire_coref_accumulate_situation_model_v1.py (ROLE_VOCAB/D/MAX_EVENT_
SLOTS/SEED/event_slots_for, sourced).

Not dispatched remote: LOCAL/CPU only (local_cpu_queue), <30s wall time.
Self-test: python exp_coherence_aggregate_discriminates_goal_outcome_v1.py --self-test
Smoke:     python exp_coherence_aggregate_discriminates_goal_outcome_v1.py --smoke
Full:      python exp_coherence_aggregate_discriminates_goal_outcome_v1.py --full
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "coherence_aggregate_discriminates_goal_outcome_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL: THE production aggregate controller (not the atomic organ in isolation)
from hdlab.self_improving_loop import route_passage  # noqa: E402

# ---- REUSED BIT-IDENTICAL: coref primitives + atom 29609's own config constants ------------------
from hdlab.coreference_resolver import (  # noqa: E402
    build_mention_stream, enrich_dialogue, run_strict_cb_instrumented, run_principle_b_deixis,
    mention_link_wrong,
)
from exp_wire_coref_accumulate_situation_model_v1 import (  # noqa: E402
    event_slots_for, ROLE_VOCAB, D as COREF_D, MAX_EVENT_SLOTS, SEED as COREF_SEED,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
GO_D = 1024                 # matches GoalOutcomeRegister's D2 (exp_situation_model_goal_outcome_dimension_v1)
GO_ROLE_VOCAB = ["GOAL", "ACTION_AGAINST", "OUTCOME_UNMET", "OUTCOME_MET"]
GO_MAX_EVENT_SLOTS = 8       # matches that cell's MAX_EVENTS
GO_SEED_BASE = 30260804      # fixed integer seed base for this cell's own GO items (no hash())
ABSTAIN_BAND = 0.02          # route_passage default, kept explicit
FLAG_MIN_N_COMPATIBLE = 2    # atom 29609's earned-flag rule

SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)

GOLD_PATH_G5G6 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
    "gold_g5g6_dense_pronoun_verbatim_v1_reviewed.jsonl",
)


def load_passages(path: str):
    passages = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                passages.append(json.loads(line))
    return sorted(passages, key=lambda p: p["passage_id"])


# ============================================================================ ARM A: coref POSITIVE CONTROL
def coref_route_one_passage(passage: dict, p_idx: int, seed: int) -> dict:
    """Calls route_passage DIRECTLY (the wired aggregate controller) on ONE real McGuffey passage,
    exact atom 29609 config (role_vocab, d, max_event_slots, per-passage seed formula
    SEED + p_idx*100 -- identical to exp_coref_autonomous_fix_router_v1.process_passage)."""
    stream = enrich_dialogue(passage, build_mention_stream(passage))
    base_pred, base_decisions = run_strict_cb_instrumented(stream)
    cand_pred, _actions = run_principle_b_deixis(stream)
    event_slots, _n_slots, _c2s = event_slots_for(stream)
    role_seq = [rec["role"] for rec in stream]
    base_ids = [str(c) for c in base_pred]
    cand_ids = [str(c) for c in cand_pred]
    flagged = [pos for pos, rec in enumerate(stream)
               if rec["is_pronoun"] and base_decisions[pos]["n_compatible"] >= FLAG_MIN_N_COMPATIBLE]

    passage_seed = COREF_SEED + p_idx * 100 + seed
    result = route_passage(
        role_seq, event_slots, base_ids, {"principle_b_deixis": cand_ids}, flagged,
        ROLE_VOCAB, COREF_D, lambda: torch.Generator().manual_seed(passage_seed),
        MAX_EVENT_SLOTS, abstain_band=ABSTAIN_BAND,
    )
    pc = result["per_candidate"]["principle_b_deixis"]

    # oracle (gold-gated) decision restricted to this one candidate, on the SAME flagged/changed set
    net_gold = None
    if pc["applicable"]:
        changed = [p for p in flagged if cand_ids[p] != base_ids[p]]
        corr = brk = 0
        for pos in changed:
            wrong_pre = mention_link_wrong(pos, stream, base_pred)
            wrong_post = mention_link_wrong(pos, stream, cand_pred)
            if wrong_pre and not wrong_post:
                corr += 1
            elif wrong_post and not wrong_pre:
                brk += 1
        net_gold = corr - brk

    auto_adopt = result["adopt"] == "principle_b_deixis"
    oracle_adopt = (net_gold is not None and net_gold > 0)
    return dict(passage_id=passage["passage_id"], applicable=pc["applicable"],
                agg_coherence_delta=pc["agg_coherence_delta"], n_changed_flagged=pc["n_changed_flagged"],
                net_gold=net_gold, auto_adopt=auto_adopt, oracle_adopt=oracle_adopt,
                matches_oracle=(auto_adopt == oracle_adopt) if net_gold is not None else None)


def _coref_arm(seed: int) -> dict:
    passages = load_passages(GOLD_PATH_G5G6)
    rows = [coref_route_one_passage(p, i, seed) for i, p in enumerate(passages)]
    applicable = [r for r in rows if r["applicable"]]
    net_auto = sum((1 if r["auto_adopt"] else 0) - (0 if r["auto_adopt"] else 0)
                   for r in applicable)  # placeholder, real net computed below
    # net-corrected-broken style score: sum of net_gold where auto_adopt==True, i.e. the GAIN the
    # autonomous aggregate decision actually realizes (mirrors atom 29609's corrected_broken.net for
    # this one-candidate case).
    net_auto = sum(r["net_gold"] for r in applicable if r["auto_adopt"] and r["net_gold"] is not None)
    net_oracle = sum(r["net_gold"] for r in applicable if r["net_gold"] is not None and r["net_gold"] > 0)
    agree = [r for r in applicable if r["net_gold"] is not None]
    agreement_rate = (sum(r["matches_oracle"] for r in agree) / len(agree)) if agree else None
    recover_frac = (net_auto / net_oracle) if net_oracle else None
    fires = bool(net_auto is not None and net_auto > 0 and recover_frac is not None and recover_frac >= 0.5)
    return dict(n_passages=len(passages), n_applicable=len(applicable), net_auto=net_auto,
                net_oracle=net_oracle, recover_frac=recover_frac, agreement_rate=agreement_rate,
                fires=fires, rows=rows)


# ============================================================================ ARM B/C: goal_outcome items
def _go_matched_items():
    """LOAD-MATCHED: owner and foil each carry 2 non-flagged supporting events (symmetric). 2
    FLAGGED OUTCOME_UNMET positions -- the goal-owner referenced at >=2 dispersed positions;
    baseline(recency)=foil (more-recently-mentioned), candidate(coherent)=owner (TRUE), ANTI-
    RECENCY BY CONSTRUCTION."""
    specs = [("amy", "jo"), ("tom", "sid"), ("beth", "meg"), ("ruth", "ann")]
    items = []
    for idx, (owner, foil) in enumerate(specs):
        role_seq = ["GOAL", "ACTION_AGAINST", "GOAL", "ACTION_AGAINST", "OUTCOME_UNMET", "OUTCOME_UNMET"]
        event_slots = [0, 1, 0, 1, 2, 3]
        base_ids = [owner, owner, foil, foil, foil, foil]      # recency: outcome bound to foil
        true_ids = [owner, owner, foil, foil, owner, owner]    # coherent: outcome bound to TRUE owner
        items.append(dict(id=f"go_matched_{idx}_{owner}_vs_{foil}", role_seq=role_seq,
                           event_slots=event_slots, baseline_cluster_ids=base_ids,
                           true_cluster_ids=true_ids, flagged_positions=[4, 5],
                           max_event_slots=GO_MAX_EVENT_SLOTS))
    return items


def _go_asym_items(true_heavy: bool):
    """LOAD-ASYMMETRY probe: owner/foil non-flagged supporting-event counts deliberately unequal,
    then reversed. true_heavy=False (foilheavy): foil carries MORE events than owner (TRUE side
    stays lighter -- the direction that superficially 'looks like' a load-artifact win).
    true_heavy=True (ownerheavy): REVERSED -- owner (TRUE side) now carries MORE events. A genuine
    identity signal must NOT flip between these; a pure load artifact would."""
    specs = [("amy", "jo", 1, 4), ("tom", "sid", 1, 3), ("beth", "meg", 2, 5), ("ruth", "ann", 1, 4)]
    items = []
    for idx, (owner, foil, n_owner, n_foil) in enumerate(specs):
        if true_heavy:
            n_owner, n_foil = n_foil, n_owner
        # owner's supporting events: alternate GOAL/ACTION_AGAINST across n_owner slots
        owner_roles = [("GOAL" if i % 2 == 0 else "ACTION_AGAINST") for i in range(n_owner)]
        foil_roles = [("GOAL" if i % 2 == 0 else "ACTION_AGAINST") for i in range(n_foil)]
        role_seq = list(owner_roles) + list(foil_roles)
        event_slots = list(range(n_owner)) + list(range(n_foil))
        base_ids = [owner] * n_owner + [foil] * n_foil
        true_ids = list(base_ids)
        qslot = max(n_owner, n_foil)
        role_seq += ["OUTCOME_UNMET", "OUTCOME_UNMET"]
        event_slots += [qslot, qslot + 1]
        base_ids += [foil, foil]      # recency: bound to foil
        true_ids += [owner, owner]    # coherent: bound to TRUE owner
        tag = "ownerheavy" if true_heavy else "foilheavy"
        items.append(dict(id=f"go_asym_{tag}_{idx}_{owner}_vs_{foil}", role_seq=role_seq,
                           event_slots=event_slots, baseline_cluster_ids=base_ids,
                           true_cluster_ids=true_ids, flagged_positions=[len(role_seq) - 2, len(role_seq) - 1],
                           max_event_slots=qslot + 2))
    return items


def _shuffle_role_seq(items):
    """SHUFFLED-STRUCTURE CONTROL: role_seq REVERSED (deterministic index reversal, no hash()/RNG)
    -- entities/loads/event_slots/flagged_positions UNCHANGED, only which semantic role is bound to
    which entity-slot is scrambled. Destroys the 'owner stated GOAL, suffered ACTION_AGAINST, ended
    OUTCOME_UNMET' narrative coherence while preserving position/load structure exactly."""
    out = []
    for it in items:
        shuffled = dict(it)
        shuffled["id"] = it["id"] + "_SHUFFLED"
        shuffled["role_seq"] = list(reversed(it["role_seq"]))
        out.append(shuffled)
    return out


def _arms_must_differ_check(items):
    import hashlib
    for it in items:
        db = hashlib.sha256(json.dumps(it["baseline_cluster_ids"]).encode()).hexdigest()
        dt = hashlib.sha256(json.dumps(it["true_cluster_ids"]).encode()).hexdigest()
        assert db != dt, f"META_RULE_AF VIOLATION: item {it['id']} baseline==true cluster_ids"


def _go_route_one(it: dict, seed: int) -> dict:
    item_seed = GO_SEED_BASE + seed * 1000 + (hash_stable(it["id"]) % 1000)
    result = route_passage(
        it["role_seq"], it["event_slots"], it["baseline_cluster_ids"],
        {"coherent": it["true_cluster_ids"]}, it["flagged_positions"], GO_ROLE_VOCAB, GO_D,
        lambda: torch.Generator().manual_seed(item_seed), it["max_event_slots"],
        abstain_band=ABSTAIN_BAND,
    )
    pc = result["per_candidate"]["coherent"]
    return dict(id=it["id"], adopt_coherent=(result["adopt"] == "coherent"),
                applicable=pc["applicable"], agg_coherence_delta=pc["agg_coherence_delta"])


def hash_stable(s: str) -> int:
    """Deterministic (non-salted, cross-process-stable) string->int, per §F.5 PROT-023: never seed
    RNG from built-in hash(). sha256-based, fixed across runs/processes."""
    import hashlib
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def _go_arm_rate(items, seed: int):
    rows = [_go_route_one(it, seed) for it in items]
    rate = round(sum(r["adopt_coherent"] for r in rows) / len(rows), 4) if rows else None
    return rate, rows


# ============================================================================ per-seed unit
def run_seed(seed: int) -> dict:
    coref = _coref_arm(seed)

    go_matched = _go_matched_items()
    go_foilheavy = _go_asym_items(true_heavy=False)
    go_ownerheavy = _go_asym_items(true_heavy=True)
    go_shuffled = _shuffle_role_seq(go_matched)
    _arms_must_differ_check(go_matched + go_foilheavy + go_ownerheavy)
    for a, b in zip(go_matched, go_shuffled):
        assert a["role_seq"] != b["role_seq"], f"shuffle no-op on {a['id']}"

    rate_matched, rows_matched = _go_arm_rate(go_matched, seed)
    rate_foilheavy, rows_foilheavy = _go_arm_rate(go_foilheavy, seed)
    rate_ownerheavy, rows_ownerheavy = _go_arm_rate(go_ownerheavy, seed)
    rate_shuffled, rows_shuffled = _go_arm_rate(go_shuffled, seed)

    return dict(
        seed=seed,
        coref_n_passages=coref["n_passages"], coref_n_applicable=coref["n_applicable"],
        coref_net_auto=coref["net_auto"], coref_net_oracle=coref["net_oracle"],
        coref_recover_frac=coref["recover_frac"], coref_agreement_rate=coref["agreement_rate"],
        coref_fires=coref["fires"], coref_rows=coref["rows"],
        go_matched_adopt_rate=rate_matched, go_foilheavy_adopt_rate=rate_foilheavy,
        go_ownerheavy_adopt_rate=rate_ownerheavy, go_shuffled_adopt_rate=rate_shuffled,
        go_matched_rows=rows_matched, go_foilheavy_rows=rows_foilheavy,
        go_ownerheavy_rows=rows_ownerheavy, go_shuffled_rows=rows_shuffled,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(sum(vals) / len(vals), 4) if vals else None

    coref_fires_all_seeds = all(per_seed[s]["coref_fires"] for s in seeds)
    coref_net_auto_mean = mean("coref_net_auto")
    coref_recover_frac_mean = mean("coref_recover_frac")

    go_matched = mean("go_matched_adopt_rate")
    go_foilheavy = mean("go_foilheavy_adopt_rate")
    go_ownerheavy = mean("go_ownerheavy_adopt_rate")
    go_shuffled = mean("go_shuffled_adopt_rate")

    load_range = None
    load_artifact_ruled_out = None
    if None not in (go_matched, go_foilheavy, go_ownerheavy):
        vals = [go_matched, go_foilheavy, go_ownerheavy]
        load_range = round(max(vals) - min(vals), 4)
        load_artifact_ruled_out = bool(min(vals) >= 0.5 and load_range <= 0.35)

    shuffled_collapses = (go_shuffled is not None and go_shuffled <= 0.25)
    shuffled_survives = (go_shuffled is not None and go_shuffled >= 0.75)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif not coref_fires_all_seeds:
        verdict = "HARNESS_DEAD_POSITIVE_CONTROL_FAILED"
    elif go_matched is not None and go_matched <= 0.25:
        verdict = "HARD_FAIL_GOAL_OUTCOME_DOES_NOT_EXTEND"
    elif go_matched is not None and go_matched >= 0.75 and (
            load_artifact_ruled_out is False or shuffled_survives):
        verdict = "HARD_FAIL_LOAD_ARTIFACT"
    elif (go_matched is not None and go_matched >= 0.75 and load_artifact_ruled_out
          and shuffled_collapses):
        verdict = "HARD_PASS_AGGREGATE_DECODABILITY_EXTENDS_TO_GOAL_OUTCOME"
    else:
        verdict = "MIDDLE_BAND_MIXED_OR_INCONCLUSIVE"

    load_artifact_ruled_out_str = "y" if load_artifact_ruled_out else ("n" if load_artifact_ruled_out is False else "unknown")
    extends_str = "y" if verdict == "HARD_PASS_AGGREGATE_DECODABILITY_EXTENDS_TO_GOAL_OUTCOME" else (
        "n" if verdict in ("HARD_FAIL_GOAL_OUTCOME_DOES_NOT_EXTEND", "HARD_FAIL_LOAD_ARTIFACT") else "inconclusive")

    summary = (
        f"ARM_A(coref pos-control) fires_all_seeds={coref_fires_all_seeds} "
        f"net_auto_mean={coref_net_auto_mean} recover_frac_mean={coref_recover_frac_mean} | "
        f"ARM_B(goal_outcome) matched={go_matched} foilheavy={go_foilheavy} ownerheavy={go_ownerheavy} "
        f"load_range={load_range} load_artifact_ruled_out={load_artifact_ruled_out_str} | "
        f"ARM_C(shuffled) adopt_rate={go_shuffled} collapses={shuffled_collapses} | "
        f"aggregate_decodability_extends_to_goal_outcome={extends_str}"
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        means=dict(
            coref_net_auto=coref_net_auto_mean, coref_recover_frac=coref_recover_frac_mean,
            coref_agreement_rate=mean("coref_agreement_rate"),
            go_matched_adopt_rate=go_matched, go_foilheavy_adopt_rate=go_foilheavy,
            go_ownerheavy_adopt_rate=go_ownerheavy, go_shuffled_adopt_rate=go_shuffled,
        ),
        bands=dict(coref_fires_all_seeds=coref_fires_all_seeds, load_artifact_ruled_out=load_artifact_ruled_out,
                   load_range=load_range, shuffled_collapses=shuffled_collapses,
                   shuffled_survives=shuffled_survives),
        aggregate_decodability_extends_to_goal_outcome=extends_str,
        load_artifact_ruled_out_flag=load_artifact_ruled_out_str,
        per_seed_coref_rows_seed0=per_seed[seeds[0]]["coref_rows"],
        per_seed_go_rows_seed0=dict(
            matched=per_seed[seeds[0]]["go_matched_rows"], foilheavy=per_seed[seeds[0]]["go_foilheavy_rows"],
            ownerheavy=per_seed[seeds[0]]["go_ownerheavy_rows"], shuffled=per_seed[seeds[0]]["go_shuffled_rows"],
        ),
        arms_differ_verified=True,
        brain_fidelity_caveat=(
            "route_passage's aggregate is a SINGLE-PASS integration over the whole passage/item -- a "
            "brain-COMPATIBLE approximation of Kintsch construction-integration / CA3 recurrent "
            "attractor settling, not the full recurrent fixed-point. A HARD_PASS here shows the "
            "discrimination is ALREADY carried by the one-shot aggregate (no settling needed to see "
            "it in THIS mechanism); a HARD_FAIL_GOAL_OUTCOME_DOES_NOT_EXTEND leaves open whether a "
            "settling mechanism (not yet built) would recover it -- this cell only rules out the "
            "one-shot decodability-aggregate, not every possible mechanism."
        ),
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    _write_json(os.path.join(output_dir, "metrics.json"), diag)


def run(run_mode: str) -> dict:
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    _write_json(os.path.join(out_dir, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                 "expected_n_units": EXPECTED_N_SEEDS})

    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"coref_fires={res['coref_fires']} net_auto={res['coref_net_auto']} "
              f"go_matched={res['go_matched_adopt_rate']} go_foilheavy={res['go_foilheavy_adopt_rate']} "
              f"go_ownerheavy={res['go_ownerheavy_adopt_rate']} go_shuffled={res['go_shuffled_adopt_rate']}",
              flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(coref_d=COREF_D, coref_role_vocab=ROLE_VOCAB, coref_max_event_slots=MAX_EVENT_SLOTS,
                          go_d=GO_D, go_role_vocab=GO_ROLE_VOCAB, go_max_event_slots=GO_MAX_EVENT_SLOTS,
                          abstain_band=ABSTAIN_BAND, flag_min_n_compatible=FLAG_MIN_N_COMPATIBLE,
                          seeds=seeds, n_coref_passages=18, n_go_matched=4, n_go_foilheavy=4,
                          n_go_ownerheavy=4, n_go_shuffled=4)
    agg["prereg"] = "preregs/2026-08-04_coherence_aggregate_discriminates_goal_outcome_v1.md"
    agg["cites"] = [
        "hdlab/self_improving_loop.py (route_passage, reused verbatim)",
        "experiments/exp_coref_autonomous_fix_router_v1.py (atom 29609 config)",
        "experiments/exp_situation_model_goal_outcome_dimension_v1.py (GO role vocab, sourced)",
        "experiments/exp_coherence_margin_discriminates_goal_outcome_v1.py (atomic-grain HARD_FAIL this builds on)",
    ]
    agg["per_seed"] = per_seed
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) real code path: route_passage exercised directly (not a synthetic-only branch).
    res = route_passage(["agent"], [0], ["A"], {"cand": ["B"]}, [0], ["agent", "mentioned"], 64,
                         lambda: torch.Generator().manual_seed(0), 1, abstain_band=ABSTAIN_BAND)
    assert "adopt" in res and "per_candidate" in res, f"route_passage real-call bad: {res}"

    # (1) item construction sanity + arms-must-differ + shuffle actually differs
    go_matched = _go_matched_items()
    assert len(go_matched) == 4, go_matched
    go_foilheavy = _go_asym_items(true_heavy=False)
    go_ownerheavy = _go_asym_items(true_heavy=True)
    assert len(go_foilheavy) == 4 and len(go_ownerheavy) == 4
    _arms_must_differ_check(go_matched + go_foilheavy + go_ownerheavy)
    go_shuffled = _shuffle_role_seq(go_matched)
    for a, b in zip(go_matched, go_shuffled):
        assert a["role_seq"] != b["role_seq"], f"shuffle no-op on {a['id']}"
        assert a["baseline_cluster_ids"] == b["baseline_cluster_ids"], "shuffle must NOT touch entities"
        assert a["event_slots"] == b["event_slots"], "shuffle must NOT touch event_slots"

    # (2) load-matched items are actually load-matched (self-check the construction)
    for it in go_matched:
        supp = [c for p, c in enumerate(it["baseline_cluster_ids"]) if p not in it["flagged_positions"]]
        owner = it["true_cluster_ids"][it["flagged_positions"][0]]
        foil = it["baseline_cluster_ids"][it["flagged_positions"][0]]
        assert supp.count(owner) == supp.count(foil), f"{it['id']}: load not matched"

    # (3) load-asymmetry items are genuinely asymmetric and reversed correctly
    for a, b in zip(go_foilheavy, go_ownerheavy):
        owner = a["true_cluster_ids"][a["flagged_positions"][0]]
        foil = a["baseline_cluster_ids"][a["flagged_positions"][0]]
        supp_a = [c for p, c in enumerate(a["baseline_cluster_ids"]) if p not in a["flagged_positions"]]
        supp_b = [c for p, c in enumerate(b["baseline_cluster_ids"]) if p not in b["flagged_positions"]]
        assert supp_a.count(foil) > supp_a.count(owner), f"{a['id']}: foilheavy not foil-heavy"
        assert supp_b.count(owner) > supp_b.count(foil), f"{b['id']}: ownerheavy not owner-heavy"

    # (4) deterministic seeding sanity: hash_stable is stable across calls (not built-in hash())
    assert hash_stable("go_matched_0_amy_vs_jo") == hash_stable("go_matched_0_amy_vs_jo")

    # (5) coref arm real gold path + one real route_passage call end-to-end
    passages = load_passages(GOLD_PATH_G5G6)
    assert len(passages) == 18, f"expected 18 g5g6 passages, got {len(passages)}"
    row0 = coref_route_one_passage(passages[0], 0, 0)
    assert "auto_adopt" in row0 and "oracle_adopt" in row0

    # (6) one full seed sanity (all 4 sub-arms + coref arm run to completion)
    res = run_seed(0)
    assert res["coref_fires"] is not None
    for k in ("go_matched_adopt_rate", "go_foilheavy_adopt_rate", "go_ownerheavy_adopt_rate",
              "go_shuffled_adopt_rate"):
        assert res[k] is not None, f"{k} missing"

    print(f"[SELFTEST PASS] route_passage exercised directly; go items load-matched/asymmetric by "
          f"construction; shuffle verified structural-only; seed0 coref_fires={res['coref_fires']} "
          f"net_auto={res['coref_net_auto']} go_matched={res['go_matched_adopt_rate']} "
          f"go_foilheavy={res['go_foilheavy_adopt_rate']} go_ownerheavy={res['go_ownerheavy_adopt_rate']} "
          f"go_shuffled={res['go_shuffled_adopt_rate']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        if args.smoke:
            run("smoke")
            raise SystemExit(0)
        run("full")
        raise SystemExit(0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise


if __name__ == "__main__":
    main()
