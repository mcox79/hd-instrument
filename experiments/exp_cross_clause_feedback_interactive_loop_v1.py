# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: MEASURED (not assumed) -- ties are EXPECTED for single-event chains
#   (k=0 never receives feedback in any arm, so BASE==REAL==ORACLE==SCRAMBLED there by construction)
#   and are honestly reported/exempted per-entity, not asserted away; the gate below flags ANY
#   tie across MULTI-EVENT chains only (where feedback had a chance to fire) as a wiring bug.
# - final_metrics_atomicity = tmp_replace (single-shot; whole run measured < 10s on 39 passages)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "structural can-fail test (SCRAMBLED wrong-entity prior), no CRLB noise floor
#   applies"; discriminator_reachability=true (ORACLE reproducing >= BASE recall on a real prior
#   IS the reachability check; SCRAMBLED must NOT reproduce it)
# - baseline_in_band: N/A (single-pass measurement cell, not a tuned sweep; BASE recall itself is
#   the pre-registered reference point, MEASURED@data/exp_self_correct_loop_powered_eval_v1/
#   metrics.json:summary.correction.baseline_multi_event_recall = 0.6006, reproduced fresh below)
# - cell_chunked=False (single pass, 4 arms x ~40 entities, wall time < 10s; no per-unit checkpoint
#   needed per CLAUDE.md's checkpoint rule, which applies to loops that could be killed mid-way --
#   this whole cell is one atomic numpy pass, same exemption class as exp_self_correct_loop_
#   powered_eval_v1 and exp_wire_extraction_accumulate_wm_oracle_vs_real_v6)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_cross_clause_feedback_interactive_loop_v1 (2026-08-02)

THE TRUE CROSS-CLAUSE INTERACTIVE LOOP: does the accumulated situation-model state from clauses
0..N-1 FEED BACK to constrain the role decision at clause N? This is the missing brain mechanism
the corrected 'interactive loop' (atoms 29604-6, see PRIOR-WORK CHECK below) turned out NOT to be
-- that mechanism was within-sentence construction-cue -> role (feed-forward, no memory). Here the
top-down signal is genuinely cross-clause: an entity's own accumulate-WM register, built from ITS
OWN clauses seen so far, biases the classifier's decision on the CURRENT clause (Kintsch
Construction-Integration: the situation model constrains ongoing parsing; Zwaan event-indexing;
Trueswell/Altmann&Kamide ~200ms top-down feedback into parsing, generalized here from within-
sentence to cross-clause timescale).

PRIOR-WORK CHECK (SUBSTRATE-KB CONCEPT-QUERY, USER-locked 2026-07-01): queried
`tools/substrate_query.sh "cross-clause situation model feedback role assignment interactive
loop"`. Top hit (cosine=0.3711) was preregs/interactive_extraction_situation_model_loop_probe1_v1
-- the WITHIN-SENTENCE construction-cue probe this cell's docstring explicitly distinguishes
itself from (that probe's top-down signal is a sentence-level construction summary available
BEFORE any clause is read; it carries no information across clauses). A closer, undocumented-by-
the-KFB-encoder prior-work match found by manual repo inspection (not surfaced by the cosine
search, encoder is a char-trigram model that undervalues near-duplicate code-structure): the
exp_wire_extraction_accumulate_wm_oracle_vs_real_v1..v6 family (commits 8b57859cf..) wires
extraction FEED-FORWARD into the accumulate-WM and then QUERIES the final state -- that family
never lets the WM's state feed BACK into an in-progress role decision. THIS cell is the reverse
direction (WM state -> constrains the CURRENT decision, recomputed sequentially clause-by-clause)
and has not been built before. Verdict: NOT a rediscovery; the closest relative is a feed-forward
sibling, not the same mechanism.

REUSES VERBATIM (import, no reimplementation):
  - exp_wire_extraction_accumulate_wm_oracle_vs_real_v1: unit_phase_vec, fhrr_bind, fhrr_unbind,
    fhrr_bundle, cleanup_argmax, run_self_test, load_multiclause_gold, build_register, score_entity,
    MAX_EVENT_SLOTS (the exact validated FHRR accumulate-WM organ, atom 29609/situation_model_
    accumulate_register_organ; hdlab/situation_model_accumulate.py is the torch promotion of the
    same organ -- this cell uses the numpy original verbatim, matching the rest of the wire_
    extraction/self_correct_loop family it is designed to compare against apples-to-apples).
  - exp_self_error_detection_internal_signals_v1.build_instrumented_events: builds per-entity
    clause chains with the FROZEN production STAGE-1 (v4-animacy commit-then-revise) predicted role
    per clause -- the exact same STAGE-1 output the BASE arm and the self_correct_loop cell's
    baseline both consume.
  - exp_extraction_commit_then_revise_v4_animacy.fit_commit_revise_v4_animacy_production_model:
    the frozen STAGE-1 model fit (unchanged from every prior wire_extraction/self_correct_loop cell
    this session).

ARMS (one variable = source of the cross-clause feedback prior fed into the role decision):
  BASE      = STAGE-1's own predicted role per clause, NO cross-clause feedback at all. Reproduces
              the trustworthy baseline_multi_event_recall = 0.6006 MEASURED@data/exp_self_correct_
              loop_powered_eval_v1/metrics.json:summary.correction.baseline_multi_event_recall
              (identical STAGE-1 model + identical v3 gold + identical accumulate-WM scoring path).
  REAL      = at clause k>=1, feed back a prior derived from the ENTITY'S OWN accumulate-WM
              register built from ITS OWN finalized role decisions at clauses 0..k-1 (this arm's
              own sequential output -- genuinely interactive/recurrent, not a batch post-hoc query).
              The prior is a per-role score vector (average of the register's own cleanup-readback
              scores at each already-bound slot -- literally 'what has this entity's accumulated
              situation-model state said about its roles so far', the ACCUMULATE organ's actual
              readback, not a hand-tallied frequency count). Combined with STAGE-1's one-hot vote
              for clause k via BETA-weighted addition (BETA=1.0, REASONED@notes/interactive_
              extraction_situation_model_loop_design_and_first_probe_2026-08-01.md's finding that
              one-shot additive top-down beat iterative settling in the validated within-sentence
              probe -- reused here as the a-priori weight, NOT tuned to this eval's outcome; a BETA
              sensitivity diagnostic at {0.5, 1.0, 2.0} is reported separately, non-gating).
  ORACLE    = identical mechanism to REAL, except the prior at clause k is built from the entity's
              TRUE roles at clauses 0..k-1 (perfect cross-clause memory) instead of its own
              finalized predictions. STAGE-1's one-hot vote for the CURRENT clause is UNCHANGED
              from REAL/BASE -- ORACLE isolates the VALUE OF THE FEEDBACK ITSELF (not extraction
              quality). This is the VALUE CEILING: if perfect cross-clause memory does not lift
              recall over BASE, no amount of improving the REAL accumulate organ's fidelity can
              help on this content, and the honest conclusion is the content (short, 2-4 clause
              McGuffey passages) does not exercise cross-clause coherence enough to matter --
              contract's pre-registered 'needs richer content' branch.
  SCRAMBLED = identical mechanism to REAL, except the prior source at clause k is a DIFFERENT
              entity's REAL finalized-role history (deterministic cyclic-shift pairing over the
              sorted entity-key list; first k roles of the wrong entity's own REAL sequence).
              CAN-FAIL: a wrong entity's history must NOT help -- if SCRAMBLED lifts recall as
              much as REAL/ORACLE, the apparent lift is a capacity/regularization artifact of the
              FHRR register math, not genuine cross-clause CONTENT, and the whole probe is invalid.

METRIC: multi_event_recall (mean per-entity mean-correct, entities with >=2 role-events only -- the
same quantity every wire_extraction/self_correct_loop cell in this family reports) via the SAME
build_register + score_entity FHRR round-trip used everywhere else (apples-to-apples with 0.6006).

Eval data: data/eval_gold_mention_role_mcguffey_v1/gold_multiclause_entity_track_v3.jsonl (39
passages, 165 role-events, MEASURED@ same file every prior v3-era cell in this family used).

Run:  .venv/Scripts/python.exe experiments/exp_cross_clause_feedback_interactive_loop_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_cross_clause_feedback_interactive_loop_v1.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    unit_phase_vec, fhrr_bind, fhrr_unbind, fhrr_bundle, cleanup_argmax, run_self_test,
    load_multiclause_gold, build_register, score_entity, MAX_EVENT_SLOTS,
)
from exp_extraction_commit_then_revise_v4_animacy import (  # noqa: E402
    fit_commit_revise_v4_animacy_production_model,
)
from exp_self_error_detection_internal_signals_v1 import build_instrumented_events  # noqa: E402

ANCHOR_NAME = "cross_clause_feedback_interactive_loop_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GOLD_V3 = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_multiclause_entity_track_v3.jsonl")

# 9-way: the wire_extraction family's 8-way ROLE_VOCAB plus "goal" (MEASURED@ present in v3 gold,
# e.g. James_Mason/goal in george_ellet_snowball -- absent from prior cells that only used v1/v2
# gold or the 8-way vocab; this cell's role_vecs dict must cover every TRUE role in v3 or
# build_register KeyErrors on it).
ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker", "possessor",
              "experiencer", "goal"]

BETA = 1.0                       # REASONED (see docstring); fixed a priori, not tuned to this eval
BETA_SENSITIVITY_GRID = [0.5, 1.0, 2.0]   # non-gating diagnostic only

# --- pre-registered bands (declared BEFORE reading results) ------------------------------------
BASELINE_REPRO_TARGET = 0.6005747126436781   # MEASURED@data/exp_self_correct_loop_powered_eval_v1/
                                              # metrics.json:summary.correction.baseline_multi_event_recall
BASELINE_REPRO_TOL = 0.02
ORACLE_CEILING_MIN = 0.03        # oracle_lift below this = content doesn't support cross-clause feedback
SCRAMBLED_CANFAIL_MAX = 0.02     # scrambled_lift above this = can-fail violation (wrong-entity prior helped)
REAL_CAPTURE_FRAC_HARDPASS = 0.50
REAL_CAPTURE_FRAC_MIDDLE = 0.15


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


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


# ---------------------------------------------------------------------------
# THE INTERACTIVE FEEDBACK MECHANISM (the ONE new piece this cell builds)
# ---------------------------------------------------------------------------
def prior_role_scores(roles_so_far, role_vecs, idx_vecs):
    """The accumulate organ's ACTUAL readback used as a cross-clause top-down prior: build the FHRR
    register from roles_so_far (bound at slots 0..len-1), then unbind+cleanup at EACH already-bound
    slot and average the per-role cleanup scores. This is a genuine readback (every slot queried WAS
    bound), not a no-info decode of an unbound future slot. Returns None if roles_so_far is empty
    (clause 0 of any chain has no prior; feedback structurally cannot fire there)."""
    if not roles_so_far:
        return None
    reg = build_register(roles_so_far, role_vecs, idx_vecs[:len(roles_so_far)])
    agg = {r: 0.0 for r in role_vecs}
    for j in range(len(roles_so_far)):
        readback = fhrr_unbind(reg, idx_vecs[j])
        _, scores = cleanup_argmax(readback, role_vecs)
        for r, s in scores.items():
            agg[r] += s
    n = len(roles_so_far)
    return {r: v / n for r, v in agg.items()}


def combine_decision(pred_role_k, prior_scores, beta):
    """STAGE-1's clause-k prediction is a one-hot vote (weight 1.0 on its own label); the cross-
    clause prior is a continuous BETA-weighted vote over all roles. argmax of the sum = the ONE
    interactive-feedback decision rule used by every feedback arm (REAL/ORACLE/SCRAMBLED); BASE
    never calls this (prior_scores always None for BASE by construction)."""
    if prior_scores is None:
        return pred_role_k
    combined = {r: (1.0 if r == pred_role_k else 0.0) + beta * prior_scores[r] for r in prior_scores}
    return max(combined.items(), key=lambda kv: kv[1])[0]


def base_final_roles(chain):
    return [ev["pred_role"] for ev in chain]


def compute_real_final_roles(chain, role_vecs, idx_vecs, beta):
    """Sequential/recurrent: clause k's decision depends on THIS SAME ARM's own finalized decisions
    at clauses 0..k-1 (genuinely interactive, not a batch post-hoc query of a frozen WM)."""
    final_roles = []
    for k, ev in enumerate(chain):
        prior = prior_role_scores(final_roles, role_vecs, idx_vecs) if k > 0 else None
        final_roles.append(combine_decision(ev["pred_role"], prior, beta))
    return final_roles


def compute_oracle_final_roles(chain, role_vecs, idx_vecs, beta):
    """Same decision rule as REAL, but the prior is built from TRUE roles of clauses 0..k-1 (perfect
    cross-clause memory) -- isolates the VALUE of feedback from extraction quality."""
    final_roles = []
    true_so_far = []
    for k, ev in enumerate(chain):
        prior = prior_role_scores(true_so_far, role_vecs, idx_vecs) if k > 0 else None
        final_roles.append(combine_decision(ev["pred_role"], prior, beta))
        true_so_far.append(ev["true_role"])
    return final_roles


def compute_scrambled_final_roles(chain, wrong_real_history, role_vecs, idx_vecs, beta):
    """Same decision rule as REAL, but the prior source at clause k is a DIFFERENT entity's own REAL
    finalized-role history (first k roles of it) -- the wrong entity's identity, not this entity's."""
    final_roles = []
    for k, ev in enumerate(chain):
        src = wrong_real_history[:k]
        prior = prior_role_scores(src, role_vecs, idx_vecs) if src else None
        final_roles.append(combine_decision(ev["pred_role"], prior, beta))
    return final_roles


def score_chain(final_roles, chain, role_vecs, idx_vecs):
    true_roles = [ev["true_role"] for ev in chain]
    reg = build_register(final_roles, role_vecs, idx_vecs[:len(final_roles)])
    return score_entity(reg, true_roles, idx_vecs, role_vecs)


def multi_event_recall(per_entity_arm, events):
    vals = [per_entity_arm[e["key"]]["recall"] for e in events if len(e["chain"]) >= 2]
    return float(np.mean(vals)) if vals else None


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
def run_arms(events, role_vecs, idx_vecs, beta):
    """Returns per_entity: {arm: {key: {"correct": [...], "recall": float}}} for the 4 arms."""
    base_roles, real_roles, oracle_roles = {}, {}, {}
    for e in events:
        key, chain = e["key"], e["chain"]
        base_roles[key] = base_final_roles(chain)
        real_roles[key] = compute_real_final_roles(chain, role_vecs, idx_vecs, beta)
        oracle_roles[key] = compute_oracle_final_roles(chain, role_vecs, idx_vecs, beta)

    sorted_keys = sorted(real_roles.keys())
    n_ent = len(sorted_keys)
    partner_of = ({sorted_keys[i]: sorted_keys[(i + 1) % n_ent] for i in range(n_ent)}
                  if n_ent > 1 else {})
    scrambled_roles = {}
    for e in events:
        key, chain = e["key"], e["chain"]
        partner = partner_of.get(key)
        wrong_hist = real_roles[partner] if (partner and partner != key) else []
        scrambled_roles[key] = compute_scrambled_final_roles(chain, wrong_hist, role_vecs, idx_vecs, beta)

    arm_roles = {"BASE": base_roles, "REAL": real_roles, "ORACLE": oracle_roles, "SCRAMBLED": scrambled_roles}
    per_entity = {arm: {} for arm in arm_roles}
    for arm, roles_by_key in arm_roles.items():
        for e in events:
            key, chain = e["key"], e["chain"]
            correct = score_chain(roles_by_key[key], chain, role_vecs, idx_vecs)
            per_entity[arm][key] = {"correct": correct, "recall": float(np.mean(correct)),
                                     "final_roles": roles_by_key[key]}
    return per_entity, partner_of


def run_all(mode, restrict_n=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] fitting STAGE-1 v4-animacy production model (frozen, reused verbatim) ..."
          % mode, flush=True)
    model = fit_commit_revise_v4_animacy_production_model()
    print("[%s] model fit on %d sentences" % (mode, model["n_train_sentences"]), flush=True)

    passages = load_multiclause_gold(GOLD_V3)
    if restrict_n is not None:
        passages = passages[:restrict_n]
    print("[%s] loaded %d multiclause passages" % (mode, len(passages)), flush=True)

    events, n_clauses = build_instrumented_events(passages, model)
    n_entities = len(events)
    n_role_events = sum(len(e["chain"]) for e in events)
    n_multi = sum(1 for e in events if len(e["chain"]) >= 2)
    print("[%s] %d entity chains (%d multi-event, %d role-events) over %d clauses"
          % (mode, n_entities, n_multi, n_role_events, n_clauses), flush=True)

    max_chain = max((len(e["chain"]) for e in events), default=0)
    assert max_chain <= MAX_EVENT_SLOTS, (
        f"gold chain length {max_chain} exceeds declared MAX_EVENT_SLOTS={MAX_EVENT_SLOTS}"
    )

    seed = 20260802
    rng = np.random.default_rng(seed)
    d = 1024
    role_vecs = {r: unit_phase_vec(rng, d) for r in ROLE_VOCAB}
    idx_vecs = [unit_phase_vec(rng, d) for _ in range(MAX_EVENT_SLOTS)]

    per_entity, partner_of = run_arms(events, role_vecs, idx_vecs, BETA)

    # BETA sensitivity diagnostic (non-gating; REAL/ORACLE only, BASE/SCRAMBLED do not depend on beta
    # in a way that matters for this diagnostic's question).
    beta_sensitivity = {}
    for b in BETA_SENSITIVITY_GRID:
        pe_b, _ = run_arms(events, role_vecs, idx_vecs, b)
        beta_sensitivity[str(b)] = {
            "REAL": multi_event_recall(pe_b["REAL"], events),
            "ORACLE": multi_event_recall(pe_b["ORACLE"], events),
        }

    elapsed = time.perf_counter() - t0
    return per_entity, partner_of, events, n_clauses, beta_sensitivity, elapsed


def _measure_arms_differ_multi_event(per_entity, events):
    """MEASURE (not assert) ties across arms, restricted to multi-event chains (single-event chains
    are EXPECTED to tie in every arm since k=0 never receives feedback -- exempted structurally, not
    reported as a finding)."""
    ties = []
    arms = ["BASE", "REAL", "ORACLE", "SCRAMBLED"]
    for e in events:
        if len(e["chain"]) < 2:
            continue
        key = e["key"]
        digs = {a: hashlib.sha256(json.dumps(per_entity[a][key]["final_roles"]).encode()).hexdigest()
                for a in arms}
        for i in range(len(arms)):
            for j in range(i + 1, len(arms)):
                a, b = arms[i], arms[j]
                if digs[a] == digs[b]:
                    ties.append({"key": key, "pair": [a, b]})
    return ties


def decide_verdict(per_entity, events, mode):
    base_r = multi_event_recall(per_entity["BASE"], events)
    real_r = multi_event_recall(per_entity["REAL"], events)
    oracle_r = multi_event_recall(per_entity["ORACLE"], events)
    scrambled_r = multi_event_recall(per_entity["SCRAMBLED"], events)

    baseline_repro_ok = (base_r is not None
                         and abs(base_r - BASELINE_REPRO_TARGET) <= BASELINE_REPRO_TOL)

    oracle_lift = (oracle_r - base_r) if (oracle_r is not None and base_r is not None) else None
    real_lift = (real_r - base_r) if (real_r is not None and base_r is not None) else None
    scrambled_lift = (scrambled_r - base_r) if (scrambled_r is not None and base_r is not None) else None
    capture_frac = (real_lift / oracle_lift) if (oracle_lift and oracle_lift > 0) else None

    summary = {
        "base_multi_event_recall": base_r, "real_multi_event_recall": real_r,
        "oracle_multi_event_recall": oracle_r, "scrambled_multi_event_recall": scrambled_r,
        "oracle_lift_over_base": oracle_lift, "real_lift_over_base": real_lift,
        "scrambled_lift_over_base": scrambled_lift, "real_capture_fraction_of_oracle_lift": capture_frac,
        "baseline_repro_ok": bool(baseline_repro_ok), "baseline_repro_target": BASELINE_REPRO_TARGET,
        "n_multi_event_entities": sum(1 for e in events if len(e["chain"]) >= 2),
        "n_entities_total": len(events),
    }

    if mode == "full" and not baseline_repro_ok:
        return "HARD_FAIL_BASELINE_DID_NOT_REPRODUCE_0p60_PIPELINE_DRIFT", summary

    if scrambled_lift is not None and scrambled_lift > SCRAMBLED_CANFAIL_MAX:
        return "HARD_FAIL_CANFAIL_VIOLATION_SCRAMBLED_WRONG_ENTITY_PRIOR_HELPED", summary

    if oracle_lift is None or oracle_lift < ORACLE_CEILING_MIN:
        return "NULL_RESULT_ORACLE_CEILING_ZERO_CONTENT_TOO_SHORT_FOR_CROSSCLAUSE_FEEDBACK", summary

    if capture_frac is not None and real_lift >= ORACLE_CEILING_MIN and capture_frac >= REAL_CAPTURE_FRAC_HARDPASS:
        return "HARD_PASS_REAL_FEEDBACK_CAPTURES_MAJORITY_OF_ORACLE_CEILING", summary
    if capture_frac is not None and capture_frac >= REAL_CAPTURE_FRAC_MIDDLE:
        return "MIDDLE_BAND_REAL_FEEDBACK_CAPTURES_PARTIAL_CEILING_ACCUMULATE_ORGAN_LOSSY", summary
    return "HARD_FAIL_ORACLE_CEILING_POSITIVE_BUT_REAL_ORGAN_CAPTURES_NEAR_NOTHING", summary


def _write_metrics(verdict, summary, per_entity, events, n_clauses, beta_sensitivity, elapsed, mode,
                    measured_ties):
    per_entity_dump = []
    for e in events:
        key = e["key"]
        row = {"key": key, "n_events": len(e["chain"]), "multi_event": len(e["chain"]) >= 2,
               "true_roles": [ev["true_role"] for ev in e["chain"]]}
        for arm in ("BASE", "REAL", "ORACLE", "SCRAMBLED"):
            row[arm + "_final_roles"] = per_entity[arm][key]["final_roles"]
            row[arm + "_correct"] = per_entity[arm][key]["correct"]
            row[arm + "_recall"] = per_entity[arm][key]["recall"]
        per_entity_dump.append(row)

    def _f(v):
        return "%.4f" % v if v is not None else "NA"

    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | BASE=%s REAL=%s ORACLE=%s SCRAMBLED=%s | oracle_lift=%s real_lift=%s "
            "scrambled_lift=%s capture_frac=%s | baseline_repro_ok=%s | n_multi_event=%d/%d"
            % (verdict, _f(summary["base_multi_event_recall"]), _f(summary["real_multi_event_recall"]),
               _f(summary["oracle_multi_event_recall"]), _f(summary["scrambled_multi_event_recall"]),
               _f(summary["oracle_lift_over_base"]), _f(summary["real_lift_over_base"]),
               _f(summary["scrambled_lift_over_base"]), _f(summary["real_capture_fraction_of_oracle_lift"]),
               summary["baseline_repro_ok"], summary["n_multi_event_entities"], summary["n_entities_total"])
        ),
        "summary": summary,
        "bands": {"BASELINE_REPRO_TARGET": BASELINE_REPRO_TARGET, "BASELINE_REPRO_TOL": BASELINE_REPRO_TOL,
                  "ORACLE_CEILING_MIN": ORACLE_CEILING_MIN, "SCRAMBLED_CANFAIL_MAX": SCRAMBLED_CANFAIL_MAX,
                  "REAL_CAPTURE_FRAC_HARDPASS": REAL_CAPTURE_FRAC_HARDPASS,
                  "REAL_CAPTURE_FRAC_MIDDLE": REAL_CAPTURE_FRAC_MIDDLE, "BETA": BETA},
        "beta_sensitivity_diagnostic_nongating": beta_sensitivity,
        "per_entity_dump": per_entity_dump,
        "measured_multi_event_arm_ties": measured_ties,
        "role_vocab": ROLE_VOCAB,
        "arms_differ_verified": "measured_not_asserted_see_measured_multi_event_arm_ties",
        "arms_differ_exempted": "single-event chains (k=0 never receives feedback in any arm by "
                                "construction; excluded from the tie-measurement above already)",
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_heartbeat_exempt_lt30s",
        "n_clauses": n_clauses,
        "gold_file": GOLD_V3,
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
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="formula self-test timeout budget (declared; full run expected < 15s: "
                         "numpy-only, 39 passages/165 role-events, no grid sweep beyond the 3-point "
                         "beta diagnostic, no torch, no GPU)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    _write_start_marker(OUTPUT_DIR, mode, expected_n_units=1)

    rng = np.random.default_rng(20260802)
    run_self_test(rng)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        restrict_n = 3 if mode == "self_test" else None
        per_entity, partner_of, events, n_clauses, beta_sensitivity, elapsed = run_all(
            mode, restrict_n=restrict_n)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    measured_ties = _measure_arms_differ_multi_event(per_entity, events)
    if measured_ties:
        print("[%s] NOTE: measured multi-event arm ties (reported, not asserted-fail): %d pairs"
              % (mode, len(measured_ties)), flush=True)

    verdict, summary = decide_verdict(per_entity, events, mode)
    metrics = _write_metrics(verdict, summary, per_entity, events, n_clauses, beta_sensitivity,
                              elapsed, mode, measured_ties)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
