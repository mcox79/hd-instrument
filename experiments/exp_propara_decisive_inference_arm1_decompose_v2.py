# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; priors_only/reasoning/scramble grids differ)
# - final_metrics_atomicity: tmp_replace (single-shot decomposition; one split, no per-seed
#   checkpoint needed -- the scramble seeds are a fast inner loop over ONE fitted model)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison decomposition over a fixed real corpus (ProPara EMNLP18 TEST);
#   no capacity/noise-floor discriminator threshold to CRLB-check
# - HP_SCOPE: {content_delta: [content_delta_positive, content_delta_scramble_clean_across_seeds]}
# - cardinality_ok: EXPECTED_N_SCRAMBLE_SEEDS=len(SCRAMBLE_SEEDS)=2(smoke)/10(full)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (this is a DECOMPOSITION diagnostic, not a
#   PASS/FAIL capability claim; thresholds are for classifying the diagnostic outcome, stated in
#   prereg, not tuned)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (v1's reasoning + priors_only + official_eval) at tiny
#   scale (real_code_path); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_decisive_inference_arm1_decompose_v2.md for the full pre-reg.
"""exp_propara_decisive_inference_arm1_decompose_v2 -- DECOMPOSITION follow-up to
exp_propara_decisive_inference_arm1_oracle_v1 (which landed HARD_FAIL: the +0.306 official-metric
win over baselines was largely ORDER-INVARIANT under scramble, so most of it is structural-prior,
NOT content-based temporal composition).

This cell answers the decisive follow-up: how much of the reasoning arm's win is PRIORS-ONLY
(monotonicity CREATE-idx<DESTROY-idx + the oracle event-COUNT grant, with ZERO text/BoW
signal), and is there a GENUINE-CONTENT DELTA (full-reasoning minus priors-only) that (a) is
positive and (b) COLLAPSES under scramble across many seeds -- the only genuine comprehension
signal available here.

New arm vs v1:
  PRIORS_ONLY -- same oracle event MULTISET (identical grant to the reasoning arm) + the same
  monotonicity VALIDATE window, but the within-window RETRIEVE is CONTENT-BLIND: CREATE at the
  earliest feasible step, DESTROY at the latest feasible step, MOVEs spread deterministically
  across the remaining middle steps. NO sentence text is read. Therefore scramble-invariant by
  construction (there is no text signal to scramble). This isolates exactly the structural
  prior that survived scramble in v1.

Decomposition (all under the OFFICIAL ProPara metric AND the trap-check unmentioned-subset
proxy, both reused verbatim from v1 / propara_official_eval):
  priors_only_captures_frac = (priors_only - best_baseline) / (reasoning - best_baseline)
      -- how much of the win priors-only alone captures (official + focus).
  content_delta = reasoning - priors_only  (natural order)
      -- the increment the text/order signal adds ON TOP of the priors.
  content_delta_scramble[seed] = reasoning_scramble[seed] - priors_only
      -- priors_only is scramble-invariant, so this measures whether the content increment
         survives scramble. content_delta_retained_frac[seed] = content_delta_scramble[seed] /
         content_delta_natural. If this collapses (-> ~0 or negative) across seeds, the content
         increment is genuinely order-sensitive (real composition); if it stays ~1, the "content"
         increment is itself another order-invariant artifact.

Oracle-grant audit (point 3 of the follow-up): the oracle hands the reasoning ONLY the per-
participant event-COUNT multiset (CREATE/MOVE/DESTROY totals, order-free) + the participant
list -- events+entities, NOT the per-step state grid. self_test() asserts this on disk
(_audit_oracle_grant): the oracle dict values are pure integer counts with no step/position/
location field, so there is no per-step-state leak. The reasoning MUST infer localization.

10 scramble seeds (full) / 2 (smoke) -- n=3 in v1 was too thin for a collapse-consistency claim.
Reports the full distribution of content_delta_retained_frac.

Modes:
  --self-test  Tiny synthetic corpus (real v1 arms + priors_only + official eval) + oracle-grant
               audit + arms-must-differ + verdict-logic sanity.
  --smoke      DEV split, 2 scramble seeds (fast band sanity).
  --full       TEST split (EMNLP18 held-out, 54 paragraphs), 10 scramble seeds -- the decisive
               decomposition.
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
from typing import Dict, List, Tuple

import numpy as np
import torch

ANCHOR_NAME = "propara_decisive_inference_arm1_decompose_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import propara_official_eval as offeval  # noqa: E402
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
# REUSE v1 verbatim (import, do NOT re-transcribe): its data prep, arms, oracle multiset,
# official/proxy scorers, deterministic seeding, and the reasoning arm itself.
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    LABELS, REG_DIM, MAX_STEPS,
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers, reasoning_label_grids,
    _official_corpus_scores, _proxy_scores, _arms_must_differ,
    _det_seed,
)
from propara_trap_check import (  # noqa: E402
    build_step_rows, build_paragraph_set_rows, fit_step_bow,
)

SCRAMBLE_SEEDS_SMOKE = [7, 17]
SCRAMBLE_SEEDS_FULL = [7, 17, 29, 41, 53, 71, 83, 97, 101, 113]

# Decomposition-outcome classification thresholds (diagnostic, not a capability PASS/FAIL --
# stated in prereg, not tuned). A GENUINE content signal requires the content increment to be
# both materially positive AND to collapse under scramble across a MAJORITY of seeds.
CONTENT_DELTA_MIN_POSITIVE = 0.02        # content_delta (focus macro-F1) must exceed this to be "real"
CONTENT_DELTA_SCRAMBLE_COLLAPSE_FRAC = 0.50  # per-seed retained_frac <= this counts as "collapsed"
CONTENT_DELTA_COLLAPSE_SEED_MAJORITY = 0.70  # >= this fraction of seeds must collapse for "scramble-clean"


# ============================================================================ priors-only assignment (content-blind)
def _assign_events_priors_only(pending_counts: Dict[str, int], n_steps: int) -> Dict[int, str]:
    """CONTENT-BLIND analog of v1._assign_events_for_participant: same monotonicity VALIDATE
    window (CREATE pins lo, DESTROY pins hi), but the within-window RETRIEVE reads NO text --
    CREATE goes to the earliest feasible step, DESTROY to the latest feasible step, MOVEs are
    spread deterministically across the remaining middle steps. Uses ONLY the oracle counts +
    the monotonicity prior; therefore scramble-invariant by construction."""
    assigned: Dict[int, str] = {}
    used: set = set()
    lo, hi = 1, n_steps
    n_create = min(pending_counts.get("CREATE", 0), 1)
    n_destroy = min(pending_counts.get("DESTROY", 0), 1)
    n_move = pending_counts.get("MOVE", 0)

    if n_create:
        chosen = lo
        if chosen not in used and chosen <= hi:
            assigned[chosen] = "CREATE"
            used.add(chosen)
            lo = chosen + 1
    if n_destroy:
        chosen = hi
        if chosen not in used and chosen >= lo:
            assigned[chosen] = "DESTROY"
            used.add(chosen)
            hi = chosen - 1
    if n_move:
        window = [s for s in range(lo, hi + 1) if s not in used]
        if window:
            # spread MOVEs deterministically (evenly) across the remaining window
            k = min(n_move, len(window))
            for j in range(k):
                pos = int(round(j * (len(window) - 1) / max(k - 1, 1))) if k > 1 else len(window) // 2
                step = window[pos]
                if step not in used:
                    assigned[step] = "MOVE"
                    used.add(step)
    return assigned


def priors_only_label_grids(paragraphs: List[Dict],
                             oracle_multiset: Dict[Tuple[str, str], Dict[str, int]]
                             ) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, float]]:
    """Content-blind priors-only grids, wired through the SAME per-paragraph AccumulateRegister
    decode path as the reasoning arm (so the two are compared on an equal FHRR-decode footing,
    not one plain-dict vs one decoded)."""
    out: Dict[str, Dict[str, List[str]]] = {}
    decode_checks = {"n": 0, "match": 0}
    for para in paragraphs:
        para_id = para["para_id"]
        n = len(para["sentence_texts"])
        gen = torch.Generator()
        gen.manual_seed(_det_seed(f"situation_model_{para_id}"))
        reg = AccumulateRegister(role_vocab=LABELS, d=REG_DIM, generator=gen, max_event_slots=MAX_STEPS)
        grid = {}
        for participant in para["participants"]:
            counts = oracle_multiset.get((para_id, participant), {"CREATE": 0, "MOVE": 0, "DESTROY": 0})
            assigned = _assign_events_priors_only(counts, n)
            final_labels = [assigned.get(t, "NONE") for t in range(1, n + 1)]
            for t in range(1, n + 1):
                reg.add_event(participant, final_labels[t - 1], t - 1)
            decoded = []
            for t in range(1, n + 1):
                lab, _sc = reg.decode(participant, t - 1)
                decoded.append(lab)
                decode_checks["n"] += 1
                decode_checks["match"] += int(lab == final_labels[t - 1])
            grid[participant] = decoded
        out[para_id] = grid
    fidelity = decode_checks["match"] / max(decode_checks["n"], 1)
    return out, {"decode_fidelity": fidelity, "n_decoded": decode_checks["n"]}


# ============================================================================ oracle-grant audit
def _audit_oracle_grant(oracle_multiset: Dict[Tuple[str, str], Dict[str, int]]) -> Dict:
    """Point 3: confirm on disk that the oracle hands ONLY event COUNTS (+ the participant key),
    never a per-step state / location / position. Each value must be a dict whose keys are
    EXACTLY {CREATE, MOVE, DESTROY} and whose values are ints -- no step index, no location
    string, nothing that localizes an event to a step (that is what the reasoning must infer)."""
    ok = True
    offending = []
    for key, val in oracle_multiset.items():
        if set(val.keys()) != {"CREATE", "MOVE", "DESTROY"}:
            ok = False
            offending.append((key, list(val.keys())))
            continue
        if not all(isinstance(v, int) for v in val.values()):
            ok = False
            offending.append((key, "non_int_value"))
    return {"events_and_entities_only_no_state_leak": ok,
            "n_participant_pairs": len(oracle_multiset),
            "offending_examples": offending[:5],
            "grant_description": "per-(paragraph,participant) order-free counts of "
                                 "CREATE/MOVE/DESTROY; participant list = entities; NO per-step "
                                 "state grid, NO location, NO step index -> localization must be "
                                 "INFERRED by the reasoning arm"}


# ============================================================================ decomposition over a split
def run_decomposition(split: str, train_paragraphs: List[Dict], scramble_seeds: List[int]) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)

    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)
    oracle_audit = _audit_oracle_grant(oracle_multiset)

    # base arms (all scramble-invariant; computed once)
    grids: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
    grids["majority"] = majority_label_grids(paragraphs)
    grids["bow_singlestep"] = bow_label_grids(paragraphs, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(paragraphs, bag_clfs)
    grids["priors_only"], priors_diag = priors_only_label_grids(paragraphs, oracle_multiset)
    grids["reasoning"], reasoning_diag = reasoning_label_grids(paragraphs, vec, clf, oracle_multiset, scramble=False)

    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}

    best_baseline_official = max(official[a]["overall"]["f1"] for a in ("majority", "bow_singlestep", "bagstates"))
    best_baseline_focus = max(proxy[a]["unmentioned"].get("macro_f1", 0.0) for a in ("majority", "bow_singlestep", "bagstates"))

    priors_official = official["priors_only"]["overall"]["f1"]
    reasoning_official = official["reasoning"]["overall"]["f1"]
    priors_focus = proxy["priors_only"]["unmentioned"].get("macro_f1", 0.0)
    reasoning_focus = proxy["reasoning"]["unmentioned"].get("macro_f1", 0.0)

    def _capture_frac(priors, reasoning, baseline):
        denom = reasoning - baseline
        return (priors - baseline) / denom if abs(denom) > 1e-9 else None

    priors_captures_official = _capture_frac(priors_official, reasoning_official, best_baseline_official)
    priors_captures_focus = _capture_frac(priors_focus, reasoning_focus, best_baseline_focus)

    content_delta_official = reasoning_official - priors_official
    content_delta_focus = reasoning_focus - priors_focus

    # scramble sweep: reasoning_scramble focus per seed; content_delta collapse per seed
    per_seed_scramble = {}
    retained_fracs_focus = []
    scramble_focus_list = []
    for seed in scramble_seeds:
        g_scr, scr_diag = reasoning_label_grids(paragraphs, vec, clf, oracle_multiset,
                                                 scramble=True, scramble_seed=seed)
        prox_scr = _proxy_scores(steps_df, g_scr)
        off_scr = _official_corpus_scores(paragraphs, g_scr)
        scr_focus = prox_scr["unmentioned"].get("macro_f1", 0.0)
        scramble_focus_list.append(scr_focus)
        content_delta_scramble_focus = scr_focus - priors_focus
        retained = (content_delta_scramble_focus / content_delta_focus
                    if abs(content_delta_focus) > 1e-9 else None)
        if retained is not None:
            retained_fracs_focus.append(retained)
        per_seed_scramble[str(seed)] = {
            "scramble_focus_macro_f1": scr_focus,
            "scramble_official_overall_f1": off_scr["overall"]["f1"],
            "content_delta_scramble_focus": content_delta_scramble_focus,
            "content_delta_retained_frac_focus": retained,
            "decode_fidelity": scr_diag["decode_fidelity"],
            "collapsed": (retained is not None and retained <= CONTENT_DELTA_SCRAMBLE_COLLAPSE_FRAC),
        }

    n_collapsed = sum(1 for s in per_seed_scramble.values() if s["collapsed"])
    frac_seeds_collapsed = n_collapsed / max(len(per_seed_scramble), 1)
    retained_arr = np.array(retained_fracs_focus, dtype=float) if retained_fracs_focus else np.array([])

    diff = _arms_must_differ({"majority": grids["majority"], "bow_singlestep": grids["bow_singlestep"],
                              "bagstates": grids["bagstates"], "priors_only": grids["priors_only"],
                              "reasoning": grids["reasoning"]})

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "n_scramble_seeds": len(scramble_seeds), "scramble_seeds": scramble_seeds,
        "oracle_grant_audit": oracle_audit,
        "priors_decode_diag": priors_diag, "reasoning_decode_diag": reasoning_diag,
        "arms_differ": diff,
        "official": official, "proxy": proxy,
        "best_baseline_official_f1": best_baseline_official, "best_baseline_focus_macro_f1": best_baseline_focus,
        "priors_only_official_f1": priors_official, "reasoning_official_f1": reasoning_official,
        "priors_only_focus_macro_f1": priors_focus, "reasoning_focus_macro_f1": reasoning_focus,
        "priors_captures_frac_official": priors_captures_official,
        "priors_captures_frac_focus": priors_captures_focus,
        "content_delta_official_f1": content_delta_official,
        "content_delta_focus_macro_f1": content_delta_focus,
        "per_seed_scramble": per_seed_scramble,
        "content_delta_retained_frac_focus_list": retained_fracs_focus,
        "content_delta_retained_frac_focus_median": float(np.median(retained_arr)) if retained_arr.size else None,
        "content_delta_retained_frac_focus_mean": float(np.mean(retained_arr)) if retained_arr.size else None,
        "content_delta_retained_frac_focus_min": float(np.min(retained_arr)) if retained_arr.size else None,
        "content_delta_retained_frac_focus_max": float(np.max(retained_arr)) if retained_arr.size else None,
        "frac_seeds_collapsed": frac_seeds_collapsed, "n_seeds_collapsed": n_collapsed,
    }


# ============================================================================ verdict logic (diagnostic classification)
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    content_delta = result["content_delta_focus_macro_f1"]
    frac_collapsed = result["frac_seeds_collapsed"]
    median_retained = result["content_delta_retained_frac_focus_median"]
    arms_ok = result["arms_differ"]["all_differ"]
    audit_ok = result["oracle_grant_audit"]["events_and_entities_only_no_state_leak"]
    decode_ok = (result["priors_decode_diag"]["decode_fidelity"] >= 0.99
                 and result["reasoning_decode_diag"]["decode_fidelity"] >= 0.99)

    content_real = content_delta >= CONTENT_DELTA_MIN_POSITIVE
    content_scramble_clean = (frac_collapsed >= CONTENT_DELTA_COLLAPSE_SEED_MAJORITY)

    # sanity gates that would invalidate the whole decomposition regardless of the science
    infra_fail = (not arms_ok) or (not audit_ok) or (not decode_ok)

    genuine_signal = content_real and content_scramble_clean
    prior_confounded = (content_delta < CONTENT_DELTA_MIN_POSITIVE) or (not content_scramble_clean)

    msg = (f"split={result['split']} priors_captures_official={result['priors_captures_frac_official']} "
           f"priors_captures_focus={result['priors_captures_frac_focus']} "
           f"content_delta_focus={content_delta:.4f}(>= {CONTENT_DELTA_MIN_POSITIVE} to be real) "
           f"content_delta_official={result['content_delta_official_f1']:.4f} "
           f"frac_seeds_collapsed={frac_collapsed:.2f}(>= {CONTENT_DELTA_COLLAPSE_SEED_MAJORITY} for scramble-clean) "
           f"median_retained_frac={median_retained} "
           f"arms_ok={arms_ok} audit_ok={audit_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if genuine_signal:
        return "HARD_PASS", f"HARD_PASS_GENUINE_CONTENT_SIGNAL: {msg}"
    if prior_confounded:
        return "HARD_FAIL", f"HARD_FAIL_PRIOR_CONFOUNDED: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: {msg}"


# ============================================================================ output plumbing
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


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    off_result = offeval.self_test()  # official-fixture bit-exact regression (reused)

    synth_paras = [
        {"para_id": "s1", "sentence_texts": [
            "A seed is planted in soil.", "Water is added.", "The seed germinates.",
            "Roots grow into the soil.", "The plant grows tall."],
         "participants": ["seed", "water", "root"],
         "states": [
             ["-", "soil", "soil", "soil", "soil", "-"],
             ["-", "-", "pot", "soil", "soil", "soil"],
             ["-", "-", "-", "soil", "soil", "soil"],
         ]},
        {"para_id": "s2", "sentence_texts": [
            "Clouds form in the sky.", "Rain falls to earth.", "The rain soaks into ground."],
         "participants": ["cloud"],
         "states": [["-", "sky", "sky", "-"]]},
    ]
    train_paras = synth_paras
    steps_df = build_step_rows(synth_paras)
    train_steps_df = build_step_rows(train_paras)
    train_set_df = build_paragraph_set_rows(train_paras)
    vec, clf = fit_step_bow(train_steps_df)
    oracle_multiset = _oracle_event_multiset(steps_df)

    # oracle-grant audit MUST report events-only, no state leak
    audit = _audit_oracle_grant(oracle_multiset)
    assert audit["events_and_entities_only_no_state_leak"], f"ORACLE_GRANT_LEAK: {audit}"

    priors_grids, priors_diag = priors_only_label_grids(synth_paras, oracle_multiset)
    assert priors_diag["decode_fidelity"] == 1.0, f"PRIORS_DECODE_FAIL: {priors_diag}"
    # priors-only must respect monotonicity: seed CREATE before DESTROY, content-blind
    seed_lab = priors_grids["s1"]["seed"]
    assert seed_lab.count("CREATE") == 1 and seed_lab.count("DESTROY") == 1, seed_lab
    assert seed_lab.index("CREATE") < seed_lab.index("DESTROY"), f"PRIORS_MONOTONICITY_VIOLATION: {seed_lab}"
    # priors-only places CREATE at earliest feasible (step 1) and DESTROY at latest (step 5)
    assert seed_lab[0] == "CREATE", seed_lab
    assert seed_lab[-1] == "DESTROY", seed_lab

    reasoning_grids, reasoning_diag = reasoning_label_grids(synth_paras, vec, clf, oracle_multiset, scramble=False)
    # priors_only and reasoning must actually DIFFER somewhere (else "content" adds nothing even
    # in the tiny case, which would be a construction bug not a scientific finding)
    diff = _arms_must_differ({"priors_only": priors_grids, "reasoning": reasoning_grids})
    assert diff["all_differ"], f"PRIORS_EQUALS_REASONING_BUG: {diff}"

    result = run_decomposition("__synth__", synth_paras, [7, 17]) if False else None
    # run_decomposition loads a named split from disk; exercise its inner pieces directly on synth
    official = {arm: _official_corpus_scores(synth_paras, g)
                for arm, g in {"priors_only": priors_grids, "reasoning": reasoning_grids}.items()}
    assert 0.0 <= official["priors_only"]["overall"]["f1"] <= 1.0
    assert 0.0 <= official["reasoning"]["overall"]["f1"] <= 1.0

    # verdict-logic unit checks
    genuine = {"split": "x", "content_delta_focus_macro_f1": 0.10, "frac_seeds_collapsed": 1.0,
               "content_delta_retained_frac_focus_median": 0.1, "content_delta_official_f1": 0.05,
               "priors_captures_frac_official": 0.5, "priors_captures_frac_focus": 0.5,
               "arms_differ": {"all_differ": True}, "oracle_grant_audit": {"events_and_entities_only_no_state_leak": True},
               "priors_decode_diag": {"decode_fidelity": 1.0}, "reasoning_decode_diag": {"decode_fidelity": 1.0}}
    gv, _ = decomposition_verdict(genuine)
    assert gv == "HARD_PASS", gv

    confounded = dict(genuine); confounded["frac_seeds_collapsed"] = 0.2
    cv, _ = decomposition_verdict(confounded)
    assert cv == "HARD_FAIL", cv  # content increment does not collapse -> prior-confounded

    tiny = dict(genuine); tiny["content_delta_focus_macro_f1"] = 0.005
    tv, _ = decomposition_verdict(tiny)
    assert tv == "HARD_FAIL", tv  # content increment ~0 -> prior-confounded

    return {"official_eval_self_test": {"n_fixtures": len(off_result["official_fixtures"])},
            "oracle_grant_audit": audit, "priors_decode_diag": priors_diag,
            "reasoning_decode_diag": reasoning_diag,
            "priors_vs_reasoning_differ": diff["all_differ"],
            "synth_official": {k: official[k]["overall"] for k in official},
            "verdict_logic_unit_checks": {"genuine": gv, "confounded": cv, "tiny": tv}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str)[:8000])
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    split = "dev" if args.smoke else "test"
    scramble_seeds = SCRAMBLE_SEEDS_SMOKE if args.smoke else SCRAMBLE_SEEDS_FULL
    _write_start_marker(output_dir, run_mode, len(scramble_seeds))
    t0 = time.time()

    train_paragraphs = _load_split("train")
    print(f"[{run_mode}] split={split} decomposition, {len(scramble_seeds)} scramble seeds...", flush=True)
    result = run_decomposition(split, train_paragraphs, scramble_seeds)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "priors_captures_frac_official": result["priors_captures_frac_official"],
            "priors_captures_frac_focus": result["priors_captures_frac_focus"],
            "content_delta_focus_macro_f1": result["content_delta_focus_macro_f1"],
            "content_delta_official_f1": result["content_delta_official_f1"],
            "content_delta_retained_frac_focus_median": result["content_delta_retained_frac_focus_median"],
            "frac_seeds_collapsed": result["frac_seeds_collapsed"],
            "best_baseline_official_f1": result["best_baseline_official_f1"],
            "priors_only_official_f1": result["priors_only_official_f1"],
            "reasoning_official_f1": result["reasoning_official_f1"],
            "best_baseline_focus_macro_f1": result["best_baseline_focus_macro_f1"],
            "priors_only_focus_macro_f1": result["priors_only_focus_macro_f1"],
            "reasoning_focus_macro_f1": result["reasoning_focus_macro_f1"],
        },
        "cardinality_ok": len(result["per_seed_scramble"]) == len(scramble_seeds),
        "expected_n_units": len(scramble_seeds),
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison decomposition over a fixed real corpus (ProPara EMNLP18); no "
                    "capacity/noise-floor discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: decomposition-classification thresholds "
                             "stated in prereg (not tuned); diagnostic, not a capability PASS/FAIL",
        "thresholds": {"CONTENT_DELTA_MIN_POSITIVE": CONTENT_DELTA_MIN_POSITIVE,
                       "CONTENT_DELTA_SCRAMBLE_COLLAPSE_FRAC": CONTENT_DELTA_SCRAMBLE_COLLAPSE_FRAC,
                       "CONTENT_DELTA_COLLAPSE_SEED_MAJORITY": CONTENT_DELTA_COLLAPSE_SEED_MAJORITY},
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
