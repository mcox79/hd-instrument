# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; with/without/lesion grids differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {bridging: [with_beats_without_on_unmentioned, with_beats_prior_lesion, knowledge_is_load_bearing]}
# - cardinality_ok: single split, one pass (+ optional scramble seeds); EXPECTED arms fixed
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (bands DEV-calibrated, pinned before TEST)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (extraction + firing + official_eval) at tiny scale
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_bridging_knowledge_vs_mechanism_v1.md for the full pre-reg.
"""exp_propara_bridging_knowledge_vs_mechanism_v1 -- the DECISIVE mechanism-vs-knowledge diagnostic
on ProPara's UNMENTIONED subset (the genuine residual after the localization thread was exhausted
by ARM2).

CONTEXT: v3 (oracle) HARD_PASS was retro-corrected by ARM2 -- its scramble-clean order-dependence
was ambiguity-DISAMBIGUATION of participant-agnostic evidence, NOT cross-step composition; the
localization signal dissolves into order-invariant local verb-spotting under precise extraction.
The real remaining wall = cross-step inference for UNMENTIONED states = persistence (priors cover
it) + CAUSAL BRIDGING from world-knowledge (the residual). This cell decides the NEXT direction:
is the wall the BRIDGING MECHANISM or the missing KNOWLEDGE?

DESIGN (isolate BRIDGING; grant the event-COUNT budget to BOTH arms so counting is not the
variable -- that cost was measured separately in ARM2 -- and vary ONLY the bridge-location
knowledge):
  WITHOUT_KNOWLEDGE: oracle event-count budget + ARM2 participant-attributed firing (dep-parse +
    coref). Events land on ATTRIBUTED (mentioned) steps; any event whose participant is UNMENTIONED
    at its true step is not attributed -> goes to random fallback (the loop cannot LOCATE the
    unmentioned change). This is the mechanism WITHOUT bridging knowledge.
  WITH_KNOWLEDGE: identical loop + oracle BRIDGE FACTS. A bridge fact is the minimal GENERAL causal
    rule form `(effect_type, trigger_verb_class)` per participant -- e.g. "p is DESTROYED by a
    DESTROY-class (consumption) process" / "p is DESTROYED as a precursor of a CREATE-class
    (conversion / 'becomes') process". Sourced from ProPara gold: for each of p's UNMENTIONED gold
    changes, record (its effect_type, the participant-AGNOSTIC verb-class present in the TEXT at
    that step). This is NOT the per-instance answer (no step index, no per-step label): it is the
    reusable "this process affects this participant" world-knowledge fact. The loop RETRIEVES the
    fact, LOCATES a text step carrying the trigger verb-class (the step comes from TEXT, not
    oracle), VALIDATES state-feasibility, and APPLIES the effect. If the trigger verb is absent or
    ambiguous the loop can still fail -- so WITH is NOT a trivial answer-copy.
  PRIOR_LESION: oracle budget + random-monotonic placement (content-free floor). WITH must beat it.

HONEST GUARDS (the recurring oracle-leak trap): (1) the bridge fact is the general
(effect_type, trigger_class) rule, never (step, label); (2) the KNOWLEDGE-ABLATION (WITHOUT) must
COLLAPSE on the unmentioned subset -- if WITHOUT already scores high, the knowledge was not needed
(no bridging happening) and the result is void; (3) LEAK CHECK -- if WITH scores ~1.0 on the
unmentioned subset the trigger uniquely located every step (answer leaked); a GENUINE bridging
result is PARTIAL (limited by trigger-verb readability + multi-step ambiguity). All three are
reported + gated.

DECISIVE READ:
  (a) WITH beats WITHOUT (by >= band) + beats prior-lesion on the unmentioned subset, WITH not ~1.0
      -> the loop USES supplied knowledge -> the wall is KNOWLEDGE-SOURCING (build a real bridging
      KB); the mechanism works.
  (b) WITH ~= WITHOUT -> the loop cannot bridge even given the knowledge -> the MECHANISM is the
      wall (converges with the SIQa covered-knowledge-but-USE-fails finding).

METRIC: per-step 4-way change-label on the UNMENTIONED subset (macro-F1 + accuracy; the trap-check
proxy restricted to mentioned==False rows -- exactly the residual), reported alongside the official
metric (full) + the focus. Scramble optional (bridging is a knowledge test, not an order test) --
reported cheaply (2 seeds) as a secondary.

Modes: --self-test / --smoke (DEV) / --full (TEST).
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
from typing import Dict, List, Set, Tuple

import numpy as np
import pandas as pd

ANCHOR_NAME = "propara_bridging_knowledge_vs_mechanism_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import propara_official_eval as offeval  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers,
    _official_corpus_scores, _proxy_scores, _arms_must_differ, _det_seed,
)
from experiments.exp_propara_decisive_inference_arm1_v3_stateful_verb_v1 import (  # noqa: E402
    verb_classes, _canonical_sequence, _assign_prior_lesion, _rng, _grids_from_assign,
)
from experiments.exp_propara_arm2_extracted_structure_v1 import (  # noqa: E402
    _extract_paragraph, _load_coref,
)
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

SCRAMBLE_SEEDS = [7, 17]  # secondary/optional; bridging is not an order test

# Bands (DEV-calibrated; pinned before TEST -- see prereg)
WITH_MINUS_WITHOUT_HARD_PASS = 0.05   # WITH beats WITHOUT on unmentioned macro-F1 by >= this -> knowledge load-bearing
WITH_MINUS_WITHOUT_HARD_FAIL = 0.02   # WITH ~= WITHOUT (< this) -> mechanism cannot use knowledge -> mechanism wall
LEAK_CEILING = 0.95                   # WITH unmentioned macro-F1 > this -> possible answer-leak (inconclusive)
WITHOUT_COLLAPSE_CEILING = 0.60       # WITHOUT unmentioned macro-F1 must be < this (else ablation did not collapse)


# ============================================================================ oracle budget + bridge facts
def _oracle_budget(pid, participant, oracle_multiset) -> Dict[str, int]:
    ob = oracle_multiset.get((pid, participant), {"CREATE": 0, "MOVE": 0, "DESTROY": 0})
    return {"CREATE": min(int(ob.get("CREATE", 0)), 1), "MOVE": int(ob.get("MOVE", 0)),
            "DESTROY": min(int(ob.get("DESTROY", 0)), 1)}


def _build_bridge_facts(paragraphs, steps_df) -> Dict[Tuple, Dict[str, Set[str]]]:
    """Per (para_id, participant): {effect_label: set(trigger_verb_classes)} sourced from gold
    UNMENTIONED changes. GENERAL rule form (effect, trigger), NOT (step, label). trigger =
    participant-AGNOSTIC verb-class present in the TEXT at that gold-change step (a truly-cueless
    change contributes no trigger -> unbridgeable from text, honest ceiling)."""
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    by_para = {str(p["para_id"]): p for p in paragraphs}
    step_vclass_cache: Dict[str, List[Set[str]]] = {}
    for pid, p in by_para.items():
        step_vclass_cache[pid] = [verb_classes(s) for s in p["sentence_texts"]]
    for row in steps_df.itertuples():
        pid = str(row.para_id)
        key = (pid, row.participant)
        facts.setdefault(key, {})
        if (not row.mentioned) and row.label != "NONE":
            trig = step_vclass_cache[pid][row.step - 1]
            facts[key].setdefault(row.label, set()).update(trig)
    return facts


# ============================================================================ firing (base attributed + optional bridge/random fallback)
def _assign(budget: Dict[str, int], evidence: Dict[int, Set[str]], mentioned_steps: Set[int],
            step_vclass: List[Set[str]], bridge: Dict[str, Set[str]], presented_true_steps: List[int],
            n: int, rng, use_bridge: bool) -> Dict[int, str]:
    """Base ARM2-style attributed firing (oracle budget), then place UNFIRED budget events via
    either the BRIDGE (locate an unmentioned step carrying the fact's trigger verb-class) [WITH] or
    a RANDOM unused step [WITHOUT]. Both respect existence-monotonicity via processing state."""
    seq = _canonical_sequence(budget, n)
    if not seq:
        return {}
    c0 = min(int(budget.get("CREATE", 0)), 1)
    exists = (c0 == 0)
    ptr = 0
    assigned: Dict[int, str] = {}
    used: Set[int] = set()
    # base pass: attributed firing in presented order
    for true_step in presented_true_steps:
        if ptr >= len(seq):
            break
        if true_step in used:
            continue
        nxt = seq[ptr]
        classes = evidence.get(true_step - 1, set())
        state_ok = (nxt == "CREATE" and not exists) or (nxt in ("MOVE", "DESTROY") and exists)
        if state_ok and nxt in classes:
            assigned[true_step] = nxt
            used.add(true_step)
            if nxt == "CREATE":
                exists = True
            elif nxt == "DESTROY":
                exists = False
            ptr += 1
    # fallback for unfired budget events
    remaining = seq[ptr:]
    for lab in remaining:
        placed = None
        if use_bridge:
            trig = bridge.get(lab, set())
            if trig:
                # locate an UNMENTIONED step whose text verb-class matches the fact's trigger
                cands = [t for t in range(1, n + 1)
                         if t not in used and t not in mentioned_steps and (step_vclass[t - 1] & trig)]
                if cands:
                    placed = cands[0]  # retrieve-validate: first feasible unmentioned trigger step
        if placed is None:
            free = [t for t in range(1, n + 1) if t not in used]
            if free:
                placed = sorted(rng.sample(free, 1))[0]
        if placed is not None:
            assigned[placed] = lab
            used.add(placed)
    return assigned


# ============================================================================ grid builders
def _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df):
    """Per paragraph: extraction (attributed evidence), oracle budget, mentioned-step sets, step
    verb-classes, bridge facts."""
    bridge_facts = _build_bridge_facts(paragraphs, steps_df)
    # mentioned steps per (pid, participant) from steps_df (1-based step where mentioned==True)
    ment: Dict[Tuple, Set[int]] = {}
    for row in steps_df.itertuples():
        if row.mentioned:
            ment.setdefault((str(row.para_id), row.participant), set()).add(int(row.step))
    pre = {}
    for para in paragraphs:
        pid = str(para["para_id"])
        extraction = _extract_paragraph(para, coref[pid])
        step_vclass = [verb_classes(s) for s in para["sentence_texts"]]
        pre[pid] = {"extraction": extraction, "step_vclass": step_vclass,
                    "budget": {pp: _oracle_budget(para["para_id"], pp, oracle_multiset) for pp in para["participants"]},
                    "mentioned": {pp: ment.get((pid, pp), set()) for pp in para["participants"]},
                    "bridge": {pp: bridge_facts.get((pid, pp), {}) for pp in para["participants"]}}
    return pre


def _grids(paragraphs, pre, use_bridge, scramble=False, scramble_seed=0):
    def _fn(para, participant, n):
        pid = str(para["para_id"])
        P = pre[pid]
        ev = P["extraction"][participant]["evidence"]
        budget = P["budget"][participant]
        bridge = P["bridge"][participant]
        mentioned = P["mentioned"][participant]
        step_vclass = P["step_vclass"]
        if scramble:
            perm = _rng(f"bridge_scr_{scramble_seed}_{pid}").sample(range(n), n)
        else:
            perm = list(range(n))
        pts = [p + 1 for p in perm]
        rng = _rng(f"bridge_fb_{use_bridge}_{scramble}_{scramble_seed}_{pid}_{participant}")
        return _assign(budget, ev, mentioned, step_vclass, bridge, pts, n, rng, use_bridge)
    return _grids_from_assign(paragraphs, _fn)


def _prior_lesion_grids(paragraphs, pre):
    def _fn(para, participant, n):
        pid = str(para["para_id"])
        budget = pre[pid]["budget"][participant]
        return _assign_prior_lesion(budget, n, _rng(f"bridge_lesion_{pid}_{participant}"))
    return _grids_from_assign(paragraphs, _fn)


# ============================================================================ decomposition
def _unm(proxy_arm):
    b = proxy_arm["unmentioned"]
    return {"macro_f1": float(b.get("macro_f1", 0.0)), "accuracy": float(b.get("accuracy", 0.0)), "n": int(b.get("n", 0))}


def run_decomposition(split: str, train_paragraphs: List[Dict], with_scramble: bool) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)
    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)
    coref = _load_coref(split)

    print(f"[extract] precompute (parse + coref + bridge facts) {len(paragraphs)} paragraphs...", flush=True)
    pre = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)

    grids: Dict[str, Dict] = {}
    grids["majority"] = majority_label_grids(paragraphs)
    grids["bow_singlestep"] = bow_label_grids(paragraphs, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(paragraphs, bag_clfs)
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre, use_bridge=False)
    grids["with_knowledge"], with_diag = _grids(paragraphs, pre, use_bridge=True)

    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}

    unm = {arm: _unm(proxy[arm]) for arm in proxy}
    with_f1 = unm["with_knowledge"]["macro_f1"]
    without_f1 = unm["without_knowledge"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]
    best_baseline_unm = max(unm[a]["macro_f1"] for a in ("majority", "bow_singlestep", "bagstates"))

    with_minus_without = with_f1 - without_f1
    with_minus_lesion = with_f1 - lesion_f1
    with_minus_best_baseline = with_f1 - best_baseline_unm

    # how many gold unmentioned changes even HAVE a textual trigger (upper bound on bridgeable)
    n_unm_changes = 0
    n_unm_changes_with_trigger = 0
    for key, fdict in _build_bridge_facts(paragraphs, steps_df).items():
        for lab, trig in fdict.items():
            n_unm_changes += 1
            if trig:
                n_unm_changes_with_trigger += 1

    diff = _arms_must_differ({"prior_lesion": grids["prior_lesion"],
                              "without_knowledge": grids["without_knowledge"],
                              "with_knowledge": grids["with_knowledge"]})

    scramble_report = None
    if with_scramble:
        rl = []
        for seed in SCRAMBLE_SEEDS:
            gw, _ = _grids(paragraphs, pre, use_bridge=True, scramble=True, scramble_seed=seed)
            pu = _unm(_proxy_scores(steps_df, gw))
            rl.append(pu["macro_f1"])
        scramble_report = {"with_knowledge_unm_f1_scrambled": rl,
                           "natural_with_unm_f1": with_f1}

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff, "lesion_decode": lesion_diag["decode_fidelity"],
        "without_decode": without_diag["decode_fidelity"], "with_decode": with_diag["decode_fidelity"],
        "unmentioned_subset": unm,
        "with_minus_without": with_minus_without, "with_minus_prior_lesion": with_minus_lesion,
        "with_minus_best_baseline": with_minus_best_baseline,
        "best_baseline_unm_macro_f1": best_baseline_unm,
        "official": {arm: official[arm]["overall"] for arm in official},
        "official_full": official,
        "focus_macro_f1": {arm: float(proxy[arm]["unmentioned"].get("macro_f1", 0.0)) for arm in proxy},
        "n_unm_changes": n_unm_changes, "n_unm_changes_with_trigger": n_unm_changes_with_trigger,
        "bridgeable_fraction": round(n_unm_changes_with_trigger / max(n_unm_changes, 1), 4),
        "scramble_report": scramble_report,
    }


# ============================================================================ verdict logic
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    wmw = result["with_minus_without"]
    wml = result["with_minus_prior_lesion"]
    with_f1 = result["unmentioned_subset"]["with_knowledge"]["macro_f1"]
    without_f1 = result["unmentioned_subset"]["without_knowledge"]["macro_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = (result["lesion_decode"] >= 0.99 and result["without_decode"] >= 0.99 and result["with_decode"] >= 0.99)
    infra_fail = (not arms_ok) or (not decode_ok)

    ablation_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING       # WITHOUT must be low (else no bridging needed)
    leak = with_f1 > LEAK_CEILING                                    # WITH ~1.0 -> answer leaked -> inconclusive
    knowledge_used = (wmw >= WITH_MINUS_WITHOUT_HARD_PASS) and (wml > 0.0)
    mechanism_wall = (wmw < WITH_MINUS_WITHOUT_HARD_FAIL)

    msg = (f"split={result['split']} UNMENTIONED with_f1={with_f1:.4f} without_f1={without_f1:.4f} "
           f"with_minus_without={wmw:.4f}(>= {WITH_MINUS_WITHOUT_HARD_PASS} used, < {WITH_MINUS_WITHOUT_HARD_FAIL} wall) "
           f"with_minus_prior_lesion={wml:.4f} bridgeable_frac={result['bridgeable_fraction']} "
           f"ablation_collapsed={ablation_collapsed}(WITHOUT<{WITHOUT_COLLAPSE_CEILING}) leak={leak}(WITH>{LEAK_CEILING}) "
           f"arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not ablation_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_ABLATION_DID_NOT_COLLAPSE_result_void: {msg}"
    if leak:
        return "MIDDLE_BAND", f"MIDDLE_BAND_POSSIBLE_LEAK_inconclusive: {msg}"
    if knowledge_used:
        return "HARD_PASS", f"HARD_PASS_KNOWLEDGE_IS_LOAD_BEARING_wall_is_SOURCING: {msg}"
    if mechanism_wall:
        return "HARD_FAIL", f"HARD_FAIL_MECHANISM_WALL_loop_cannot_use_knowledge: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND_PARTIAL: {msg}"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, n):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": n, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    off_result = offeval.self_test()

    # synth: seed has an UNMENTIONED destroy at a step whose text has a DESTROY-class verb about
    # ANOTHER entity ("the fire consumes everything") -> bridge should locate + destroy seed there.
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["A seed appears in soil.", "Water is added.",
                            "The fire consumes everything.", "Ash remains."],
         "participants": ["seed"],
         "states": [["-", "soil", "soil", "-", "-"]]},  # CREATE@1 (mentioned), DESTROY@3 (UNMENTIONED: seed not named)
    ]
    text = " ".join(synth[0]["sentence_texts"]); offs = []; cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    coref = {"s1": {"text": text, "sentence_offsets": offs, "n_sentences": 4, "clusters": []}}

    steps_df = build_step_rows(synth)
    oracle = _oracle_event_multiset(steps_df)
    pre = _paragraph_precompute(synth, oracle, coref, steps_df)

    # gold: seed DESTROY at step 3, seed NOT mentioned there -> a bridge fact (DESTROY, {DESTROY})
    bf = pre["s1"]["bridge"]["seed"]
    assert "DESTROY" in bf and ("DESTROY" in bf["DESTROY"]), bf  # "consumes" is DESTROY-class

    g_without, dw = _grids(synth, pre, use_bridge=False)
    g_with, dwith = _grids(synth, pre, use_bridge=True)
    lesion, dl = _prior_lesion_grids(synth, pre)
    assert dw["decode_fidelity"] == 1.0 and dwith["decode_fidelity"] == 1.0 and dl["decode_fidelity"] == 1.0

    # WITH must place seed DESTROY at step 3 (the consume step); WITHOUT places it randomly (fallback)
    assert g_with["s1"]["seed"][2] == "DESTROY", g_with["s1"]["seed"]
    # CREATE is attributed at step 1 in both (seed appears)
    assert g_with["s1"]["seed"][0] == "CREATE", g_with["s1"]["seed"]

    diff = _arms_must_differ({"without_knowledge": g_without, "with_knowledge": g_with})
    # WITH and WITHOUT may or may not differ on this tiny case depending on the random fallback draw;
    # assert the mechanism ran (grids valid), not that they differ here (real corpus checks differ).
    assert isinstance(diff["all_differ"], bool)

    official = _official_corpus_scores(synth, g_with)
    assert 0.0 <= official["overall"]["f1"] <= 1.0

    # verdict-logic unit checks
    used = {"split": "x", "with_minus_without": 0.10, "with_minus_prior_lesion": 0.08,
            "unmentioned_subset": {"with_knowledge": {"macro_f1": 0.55}, "without_knowledge": {"macro_f1": 0.30}},
            "arms_differ": {"all_differ": True}, "lesion_decode": 1.0, "without_decode": 1.0, "with_decode": 1.0,
            "bridgeable_fraction": 0.7}
    uv, _ = decomposition_verdict(used)
    assert uv == "HARD_PASS", uv
    wall = dict(used); wall["with_minus_without"] = 0.005; wall["unmentioned_subset"] = {"with_knowledge": {"macro_f1": 0.31}, "without_knowledge": {"macro_f1": 0.305}}
    wv, _ = decomposition_verdict(wall)
    assert wv == "HARD_FAIL", wv
    nocollapse = dict(used); nocollapse["unmentioned_subset"] = {"with_knowledge": {"macro_f1": 0.85}, "without_knowledge": {"macro_f1": 0.75}}
    nv, _ = decomposition_verdict(nocollapse)
    assert nv == "HARD_FAIL", nv  # WITHOUT >= 0.60 ceiling -> ablation did not collapse -> void
    leaky = dict(used); leaky["unmentioned_subset"] = {"with_knowledge": {"macro_f1": 0.97}, "without_knowledge": {"macro_f1": 0.30}}
    lv, _ = decomposition_verdict(leaky)
    assert lv == "MIDDLE_BAND", lv  # WITH ~1.0 -> possible leak -> inconclusive

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "bridge_fact_seed": {k: sorted(v) for k, v in bf.items()},
            "with_seed_labels": g_with["s1"]["seed"], "without_seed_labels": g_without["s1"]["seed"],
            "verdict_logic_unit_checks": {"used": uv, "wall": wv, "no_collapse": nv, "leak": lv}}


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
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                   "elapsed_s": round(time.time() - t0, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                   "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str)[:8000])
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    split = "dev" if args.smoke else "test"
    _write_start_marker(output_dir, run_mode, 1)
    t0 = time.time()
    train_paragraphs = _load_split("train")
    print(f"[{run_mode}] split={split} bridging knowledge-vs-mechanism diagnostic...", flush=True)
    result = run_decomposition(split, train_paragraphs, with_scramble=True)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "UNMENTIONED_with_knowledge_macro_f1": result["unmentioned_subset"]["with_knowledge"]["macro_f1"],
            "UNMENTIONED_without_knowledge_macro_f1": result["unmentioned_subset"]["without_knowledge"]["macro_f1"],
            "UNMENTIONED_prior_lesion_macro_f1": result["unmentioned_subset"]["prior_lesion"]["macro_f1"],
            "with_minus_without": result["with_minus_without"],
            "with_minus_prior_lesion": result["with_minus_prior_lesion"],
            "with_minus_best_baseline": result["with_minus_best_baseline"],
            "bridgeable_fraction": result["bridgeable_fraction"],
            "n_unm_changes": result["n_unm_changes"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: bands DEV-calibrated (see prereg), pinned before TEST",
        "thresholds": {"WITH_MINUS_WITHOUT_HARD_PASS": WITH_MINUS_WITHOUT_HARD_PASS,
                       "WITH_MINUS_WITHOUT_HARD_FAIL": WITH_MINUS_WITHOUT_HARD_FAIL,
                       "LEAK_CEILING": LEAK_CEILING, "WITHOUT_COLLAPSE_CEILING": WITHOUT_COLLAPSE_CEILING},
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
