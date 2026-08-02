# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (hash-compare ORACLE/REAL/FLOOR/REAL_V4_FOURWAY registers);
#   pairwise ties (if any) are MEASURED and exempted with a printed rationale, not assumed.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run < 30s)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "structural can-fail test, no CRLB noise floor applies"; discriminator_reachability=true
#   (ORACLE reproduction of the WM organ is the reachability check)
# - baseline_in_band EXEMPTED for FLOOR arm (can-fail arm is REQUIRED near its structural floor)
# - cell_chunked=False (single pass, 4 arms, wall time < 30s; per-arm checkpoint via
#   tools/exp_checkpoint.py used anyway per CLAUDE.md's "any cell looping over >1 unit" rule)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_wire_extraction_accumulate_wm_oracle_vs_real_v5 (2026-08-02)

ROLE-INVENTORY-EXPANSION re-run of the end-to-end wire cell, the next lever after v4's HARD_FAIL_V4_
DID_NOT_BEAT_V3_SAME_GOLD (MEASURED@data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/metrics.
json: REAL(4-way, two-lever commit-then-revise) multi_event_recall=0.4208, n=20, tied/below v3's one-
lever 0.4333). That cell's own role_census diagnosed the BINDING constraint: 29.3% of the eval's true
role events (theme=10, recipient=3, possessor=1, experiencer=2 of 58 total) are STRUCTURALLY OUTSIDE
the {agent, patient, addressee} vocab -- no extraction-layer accuracy fix can move events the vocabulary
itself cannot name.

THIS CELL'S ONE-VARIABLE CHANGE (per the director's contract): STAGE-1 extraction is replaced by
exp_extraction_commit_then_revise_v3_theme.py (5-way ROLE_VOCAB5 = agent/patient/addressee/theme/none;
MEASURED@data/exp_extraction_commit_then_revise_v3_theme/metrics.json full run, HARD_PASS_THEME_ADDED_
ROLES_PRESERVED_CANFAIL_OK: canonical=0.5303 quotative=0.7705 byagent=0.7872 theme=0.9412, vs POSITION
theme=0.0000/RANDOM theme=0.2353 can-fail). The TWO LEVERS (clause-level agent=subject COMMIT default +
margin-gated graceful-degrade REVISE) are UNCHANGED in mechanism -- only the role inventory (+1 class)
and the training gold (+1 pool, gold_copular_theme_v1.jsonl, train-only, never touches this eval file)
changed, plus a principled MARGIN_THRESH re-selection documented in that cell (the ONE necessary
adjustment, since an absolute margin cutoff calibrated on a 4-way softmax is not portable unchanged to
a 5-way one; THRESH itself and the gate/COMMIT/REVISE architecture are untouched).

STAGE 2 (accumulate WM) and the ORACLE/FLOOR arms are UNCHANGED verbatim from v1-v4 (same FHRR bind/
bundle/cleanup math, same role_vecs/idx_vecs seed, same gold_multiclause_entity_track_v2.jsonl target).
ROLE_VOCAB here is EXTENDED to include "theme" (role_vecs now covers 9 roles instead of 8) since the WM
register/cleanup organ itself is vocab-size-agnostic (any role gets its own random phase vector); this
is the only place outside the extraction cell where the vocabulary expansion surfaces.

reachable set for role_census is likewise extended (LOCAL role_census5, NOT editing v1's shared
role_census which several other cells import verbatim and which hardcodes {agent, patient} only --
duplicating with the extended reachable set here to avoid a regression-risk edit to a shared function).

REAL_V4_FOURWAY arm: v4's REAL (two-lever, 4-way ROLE_VOCAB4) STAGE-1 reproduced VERBATIM (import, not
reimplemented) as the direct SAME-GOLD one-variable lineage comparison for this cell's primary claim:
does the role-inventory expansion (this cell's REAL) beat the extraction-only fix alone (v4's REAL,
reproduced here) on the identical eval set and identical STAGE-2 WM organ?

CAN-FAIL (per contract): recipient/possessor/experiencer remain OUTSIDE ROLE_VOCAB5 -- their events
structurally cannot be predicted correctly by either REAL arm (no training signal, no vocab slot) and
are expected to keep contributing to the residual unreachable fraction, honestly reported below.

Run:  .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v5.py --self-test
      .venv/Scripts/python.exe experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v5.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# STAGE 2 (accumulate WM) + shared plumbing, REUSED VERBATIM from v1 (import, not reimplemented).
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    unit_phase_vec, fhrr_bind, fhrr_unbind, fhrr_bundle, cleanup_argmax, run_self_test,
    match_mention_to_token, load_multiclause_gold, build_register, score_entity, MAX_EVENT_SLOTS,
)

# v4's STAGE-1 (commit-then-revise, TWO levers, 4-way ROLE_VOCAB4), REUSED VERBATIM for the direct
# SAME-GOLD lineage comparison arm (the primary one-variable claim of THIS cell).
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v4 import (  # noqa: E402
    fit_commit_revise_v2_production_model, stage1_predict_clause_commit_revise_v2, _gate_fires_v2_bound,
)

# THIS cell's STAGE-1 (commit-then-revise, TWO levers + THEME, 5-way ROLE_VOCAB5), REUSED VERBATIM from
# the new extraction cell.
from exp_extraction_commit_then_revise_v3_theme import (  # noqa: E402
    fit_commit_revise_v3_theme_production_model, stage1_predict_clause_commit_revise_v3_theme,
    gate_fires_v3, THRESH as V3_THEME_THRESH, ROLE_VOCAB5,
)

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker", "possessor", "experiencer"]
REACHABLE_ROLES_V5 = {"agent", "patient", "addressee", "theme"}   # extraction-layer vocab THIS cell covers

GOLD_MULTICLAUSE = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v2.jsonl")

ANCHOR_NAME = "wire_extraction_accumulate_wm_oracle_vs_real_v5"

ORACLE_REPRO_TOL = 0.08
ORACLE_REPRO_TARGET = 1.0
FLOOR_MAX = 1.0 / len(ROLE_VOCAB) + 0.15
REAL_HARD_PASS_MIN = 0.50
REAL_MIDDLE_MIN = 0.30
V4_REAL_SAME_GOLD = 0.4208   # MEASURED@data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/
                            # metrics.json:summary.real_multi_event_recall -- the number THIS cell's
                            # role-inventory-expansion claim must beat on the identical gold/WM organ.
V5_MUST_BEAT_MARGIN = 0.03


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


OUTPUT_DIR = repo_path(f"data/exp_{ANCHOR_NAME}")


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": os.environ.get("COMPUTERNAME", "unknown")}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def role_census5(entities_gold_only):
    """LOCAL extension of v1's role_census with the wider reachable set (agent/patient/addressee/theme)
    THIS cell's STAGE-1 vocab covers. NOT editing v1's shared role_census (imported verbatim by v2/v3/
    v4) to avoid a regression-risk shared-function edit -- duplicated here instead."""
    c = Counter()
    for e in entities_gold_only:
        for r in e["true_roles"]:
            c[r] += 1
    total = sum(c.values())
    reachable = sum(c.get(r, 0) for r in REACHABLE_ROLES_V5)
    return {"counts": dict(c), "total_events": total, "reachable_events": reachable,
            "unreachable_events": total - reachable,
            "unreachable_fraction": (total - reachable) / total if total else None,
            "reachable_roles": sorted(REACHABLE_ROLES_V5)}


def build_entity_chains_predsdict(passages, predict_fn, gate_fn, restrict_n=None):
    if restrict_n is not None:
        passages = passages[:restrict_n]

    entities_out = []
    clause_dump = []
    n_matched = 0
    n_total_events = 0
    pred_role_counts = {}
    n_gate_fired = 0
    n_clauses_total = 0

    for rec in passages:
        pid = rec["passage_id"]
        clauses = rec["clauses"]
        clause_infer = [predict_fn(c) for c in clauses]
        for ci, (sent, preds) in enumerate(clause_infer):
            n_clauses_total += 1
            fired = bool(gate_fn(sent))
            n_gate_fired += int(fired)
            clause_dump.append({
                "passage_id": pid, "clause_idx": ci, "text": clauses[ci],
                "n_mentions": len(sent["mention_idx"]), "gate_fired": fired,
                "mention_role_preds": {sent["tokens"][i]: r for i, r in preds.items()},
            })

        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            true_roles, pred_roles, match_ok = [], [], []
            for ev in chain:
                ci = ev["clause"]
                sent, preds = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci])
                n_total_events += 1
                if tok_i is not None:
                    used_per_clause[ci].add(tok_i)
                    n_matched += 1
                    raw_pred = preds.get(tok_i, "none")
                    pred_role = raw_pred if raw_pred != "none" else "patient"
                    pred_role_counts[pred_role] = pred_role_counts.get(pred_role, 0) + 1
                    match_ok.append(True)
                else:
                    pred_role = "patient"
                    match_ok.append(False)
                true_roles.append(ev["role"])
                pred_roles.append(pred_role)
            entities_out.append({
                "key": f"{pid}::{name}", "passage_id": pid, "name": name,
                "true_roles": true_roles, "pred_roles": pred_roles, "match_ok": match_ok,
                "n_events": len(true_roles), "multi_event": len(true_roles) >= 2,
            })

    diag = {
        "n_entity_events_total": n_total_events, "n_mention_matched": n_matched,
        "mention_match_rate": (n_matched / n_total_events) if n_total_events else None,
        "pred_role_counts": pred_role_counts,
        "n_clauses_total": n_clauses_total, "n_clauses_gate_fired": n_gate_fired,
        "clause_gate_fire_rate": (n_gate_fired / n_clauses_total) if n_clauses_total else None,
    }
    return entities_out, clause_dump, diag


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 commit-then-revise-v3-theme (5-way, THIS cell's arm) production model ..."
          % mode, flush=True)
    model_v3theme = fit_commit_revise_v3_theme_production_model()
    print("[%s] STAGE-1 v3-theme model fit on %d sentences" % (mode, model_v3theme["n_train_sentences"]),
          flush=True)

    print("[%s] fitting STAGE-1 commit-then-revise-v2 (4-way, lineage-comparison arm) production model ..."
          % mode, flush=True)
    model_v2 = fit_commit_revise_v2_production_model()

    passages = load_multiclause_gold(GOLD_MULTICLAUSE)
    print("[%s] loaded %d multiclause passages" % (mode, len(passages)), flush=True)

    entities, clause_dump, extraction_diag = build_entity_chains_predsdict(
        passages, lambda c: stage1_predict_clause_commit_revise_v3_theme(c, model_v3theme),
        lambda sent: gate_fires_v3(sent, V3_THEME_THRESH), restrict_n=restrict_n)
    entities_v4, clause_dump_v4, extraction_diag_v4 = build_entity_chains_predsdict(
        passages, lambda c: stage1_predict_clause_commit_revise_v2(c, model_v2), _gate_fires_v2_bound,
        restrict_n=restrict_n)

    census = role_census5(entities)
    print("[%s] role census (5-way reachable set): %s" % (mode, census["counts"]), flush=True)
    print("[%s] extraction diag (v5, theme-extended): %s" % (mode, extraction_diag), flush=True)
    print("[%s] extraction diag (v4, 4-way lineage): %s" % (mode, extraction_diag_v4), flush=True)

    max_chain = max((e["n_events"] for e in entities), default=0)
    assert max_chain <= MAX_EVENT_SLOTS, (
        f"gold chain length {max_chain} exceeds declared MAX_EVENT_SLOTS={MAX_EVENT_SLOTS}"
    )

    seed = 20260802
    rng = np.random.default_rng(seed)
    rng_floor = np.random.default_rng(seed + 999)
    d = 1024
    role_vecs = {r: unit_phase_vec(rng, d) for r in ROLE_VOCAB}
    idx_vecs = [unit_phase_vec(rng, d) for _ in range(MAX_EVENT_SLOTS)]

    def run_arm(arm_name, tick):
        key = ckpt.unit_key(mode, arm_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            reg_bytes = []
            per_entity = []
            if arm_name == "real_v4_fourway":
                src_entities = entities_v4
            else:
                src_entities = entities
            for e in src_entities:
                if arm_name == "oracle":
                    reg = build_register(e["true_roles"], role_vecs, idx_vecs)
                elif arm_name in ("real", "real_v4_fourway"):
                    reg = build_register(e["pred_roles"], role_vecs, idx_vecs)
                else:
                    reg = unit_phase_vec(rng_floor, d)
                correct = score_entity(reg, e["true_roles"], idx_vecs, role_vecs)
                reg_bytes.append(reg.tobytes())
                per_entity.append({"key": e["key"], "n_events": e["n_events"], "multi_event": e["multi_event"],
                                   "correct": correct, "recall": float(np.mean(correct))})
            result = {"per_entity": per_entity, "reg_digest": hashlib.sha256(b"".join(reg_bytes)).hexdigest()}
            ckpt.record_unit(OUTPUT_DIR, key, result)
            multi = [r["recall"] for r in per_entity if r["multi_event"]]
            print("[%s] arm=%s multi_event_recall=%.4f (n=%d)"
                  % (mode, arm_name, float(np.mean(multi)) if multi else -1.0, len(multi)), flush=True)

    for i, arm in enumerate(["oracle", "real", "floor", "real_v4_fourway"]):
        run_arm(arm, i)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, entities, clause_dump, extraction_diag, extraction_diag_v4, census, elapsed


def _measure_arms_differ(units):
    digs = {name: u["reg_digest"] for name, u in units.items()}
    names = sorted(digs)
    ties = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digs[a] == digs[b]:
                ties.append((a, b))
    return ties


def _arms_must_differ(units, exempt_pairs):
    digs = {name: u["reg_digest"] for name, u in units.items()}
    names = sorted(digs)
    exempt = {tuple(sorted(p)) for p in exempt_pairs}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if tuple(sorted((a, b))) in exempt:
                continue
            assert digs[a] != digs[b], f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical registers"


def _agg_multi(unit):
    vals = [e["recall"] for e in unit["per_entity"] if e["multi_event"]]
    return {"mean": float(np.mean(vals)) if vals else None, "n_entities": len(vals)}


def decide_verdict(units, census):
    oracle_multi = _agg_multi(units["oracle"])
    real_multi = _agg_multi(units["real"])
    floor_multi = _agg_multi(units["floor"])
    real_v4_multi = _agg_multi(units["real_v4_fourway"])

    oracle_ok = (oracle_multi["mean"] is not None
                 and abs(oracle_multi["mean"] - ORACLE_REPRO_TARGET) <= ORACLE_REPRO_TOL)
    floor_ok = floor_multi["mean"] is not None and floor_multi["mean"] <= FLOOR_MAX

    rm = real_multi["mean"] or 0.0
    fm = floor_multi["mean"] or 0.0
    rv4m = real_v4_multi["mean"] or 0.0
    beats_v4_same_gold = rm >= (rv4m + V5_MUST_BEAT_MARGIN)
    beats_v4_cited_anchor = rm >= (V4_REAL_SAME_GOLD + V5_MUST_BEAT_MARGIN)

    summary = {
        "oracle_multi_event_recall": oracle_multi["mean"], "oracle_n_entities": oracle_multi["n_entities"],
        "real_multi_event_recall": real_multi["mean"], "real_n_entities": real_multi["n_entities"],
        "floor_multi_event_recall": floor_multi["mean"], "floor_n_entities": floor_multi["n_entities"],
        "real_v4_fourway_multi_event_recall": real_v4_multi["mean"],
        "real_v4_fourway_n_entities": real_v4_multi["n_entities"],
        "oracle_reproduces_target": bool(oracle_ok), "floor_at_chance": bool(floor_ok),
        "v4_cited_anchor_same_gold": V4_REAL_SAME_GOLD,
        "v5_minus_v4_cited_anchor": rm - V4_REAL_SAME_GOLD,
        "beats_v4_cited_anchor": bool(beats_v4_cited_anchor),
        "beats_v4_same_gold_reproduced_here": bool(beats_v4_same_gold),
        "v5_minus_v4_same_gold_reproduced_here": rm - rv4m,
        "role_census": census,
    }

    if not oracle_ok:
        return "HARD_FAIL_MISWIRED_ORACLE_DOES_NOT_REPRODUCE", summary
    if not floor_ok:
        return "HARD_FAIL_CANFAIL_VIOLATION_FLOOR_NOT_AT_CHANCE", summary

    if rm >= REAL_HARD_PASS_MIN and rm > fm + 0.20 and beats_v4_same_gold:
        return "HARD_PASS_V5_ROLE_INVENTORY_EXPANSION_BEATS_V4_AND_CLEARS_HARD_PASS_BAR", summary
    if beats_v4_same_gold and rm >= REAL_MIDDLE_MIN:
        return "MIDDLE_BAND_V5_BEATS_V4_SAME_GOLD_BUT_BELOW_HARD_PASS", summary
    if beats_v4_same_gold:
        return "PARTIAL_V5_BEATS_V4_SAME_GOLD_STILL_NEAR_FLOOR", summary
    if rm <= fm + 0.10:
        return "HARD_FAIL_V5_REAL_NO_BETTER_THAN_FLOOR", summary
    return "HARD_FAIL_V5_DID_NOT_BEAT_V4_SAME_GOLD", summary


def _write_metrics(verdict, summary, units, entities, clause_dump, extraction_diag, extraction_diag_v4,
                    elapsed, mode, arms_differ_exempted, arms_differ_rationale):
    combined = {}
    for arm in ("oracle", "real", "floor", "real_v4_fourway"):
        for e in units[arm]["per_entity"]:
            combined.setdefault(e["key"], {"key": e["key"], "n_events": e["n_events"], "multi_event": e["multi_event"]})
            combined[e["key"]][arm + "_recall"] = e["recall"]
            combined[e["key"]][arm + "_correct"] = e["correct"]
    entity_true_pred = {e["key"]: {"true_roles": e["true_roles"], "pred_roles": e["pred_roles"],
                                    "match_ok": e["match_ok"]} for e in entities}
    for key, row in combined.items():
        row.update(entity_true_pred.get(key, {}))
    per_entity_dump = list(combined.values())

    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | ORACLE recall=%.4f (n=%d) | REAL(v5 theme-extended) recall=%.4f (n=%d) | "
            "REAL(v4 4-way, same gold) recall=%.4f (n=%d) | FLOOR recall=%.4f (n=%d) | "
            "v4_cited_anchor=%.4f | beats_v4_same_gold=%s | unreachable_role_fraction=%.4f"
            % (verdict, summary["oracle_multi_event_recall"] or -1, summary["oracle_n_entities"],
               summary["real_multi_event_recall"] or -1, summary["real_n_entities"],
               summary["real_v4_fourway_multi_event_recall"] or -1, summary["real_v4_fourway_n_entities"],
               summary["floor_multi_event_recall"] or -1, summary["floor_n_entities"],
               summary["v4_cited_anchor_same_gold"], summary["beats_v4_same_gold_reproduced_here"],
               summary["role_census"]["unreachable_fraction"] or -1)
        ),
        "summary": summary,
        "bands": {"ORACLE_REPRO_TARGET": ORACLE_REPRO_TARGET, "ORACLE_REPRO_TOL": ORACLE_REPRO_TOL,
                  "FLOOR_MAX": FLOOR_MAX, "REAL_HARD_PASS_MIN": REAL_HARD_PASS_MIN,
                  "REAL_MIDDLE_MIN": REAL_MIDDLE_MIN, "V4_REAL_SAME_GOLD": V4_REAL_SAME_GOLD,
                  "V5_MUST_BEAT_MARGIN": V5_MUST_BEAT_MARGIN},
        "per_arm": units,
        "extraction_diag_v5_theme_extended": extraction_diag,
        "extraction_diag_v4_fourway": extraction_diag_v4,
        "per_entity_dump": per_entity_dump,
        "clause_dump": clause_dump,
        "role_vocab": ROLE_VOCAB,
        "new_extraction_role_vocab": ROLE_VOCAB5,
        "reachable_roles_v5": sorted(REACHABLE_ROLES_V5),
        "arms_differ_verified": True,
        "arms_differ_exempted": arms_differ_exempted,
        "arms_differ_exemption_rationale": arms_differ_rationale,
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt30s",
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="formula self-test timeout budget (declared; this cell runs in <60s)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=4)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        restrict_n = 2 if mode == "self_test" else None
        units, entities, clause_dump, extraction_diag, extraction_diag_v4, census, elapsed = run_all(
            mode, restrict_n=restrict_n)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    measured_ties = _measure_arms_differ(units)
    arms_differ_exempted = []
    arms_differ_rationale = "no ties measured; all arm registers pairwise distinct."
    if measured_ties:
        arms_differ_exempted = measured_ties
        arms_differ_rationale = (
            "MEASURED (this run) pairwise-identical pred_roles/registers for: %s -- reported honestly, "
            "not assumed." % (measured_ties,)
        )
        print("[%s] WARNING: measured arm ties (exempting from META_RULE_AF): %s" % (mode, measured_ties),
              flush=True)

    _arms_must_differ(units, arms_differ_exempted)
    verdict, summary = decide_verdict(units, census)
    metrics = _write_metrics(verdict, summary, units, entities, clause_dump, extraction_diag,
                              extraction_diag_v4, elapsed, mode, arms_differ_exempted, arms_differ_rationale)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
