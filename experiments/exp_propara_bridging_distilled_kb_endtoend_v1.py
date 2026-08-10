# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; without/with_distilled/with_oracle/lesion differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {distilled_kb: [survival_material, ablation_collapses, no_leak, facts_general_hand_vet]}
# - cardinality_ok: single split, one pass; EXPECTED arms fixed
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (survival bar pre-registered before TEST)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (distilled KB + firing + official_eval)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_bridging_distilled_kb_endtoend_v1.md for the full pre-reg.
"""exp_propara_bridging_distilled_kb_endtoend_v1 -- THE CULMINATION: the decisive end-to-end
glass-box comprehension test on real prose with a BUILT knowledge foundation.

Arc: v1 oracle (order-invariant priors) -> v2 decomposition (priors) -> v3 stateful-verb
(order-dependent MOVES, HARD_PASS) -> ARM2 extracted (local verb-spotting; retro-corrects v3) ->
bridging diagnostic (loop USES oracle facts +0.106; wall = SOURCING) -> real-KB (generic SRL
survival 0.22, NO-GO) -> ConceptNet (survival 0.22 +0.002, promiscuous, misses scientific
processes -> BUILD not REUSE). Everything is validated EXCEPT the one missing component: a
process-specific co-participation KB. This cell BUILDS it (offline-distilled, glass-box runtime,
per the 07-14 foundation pivot) and runs the decisive end-to-end test.

PIPELINE (extract structure + distilled process-KB typed facts + retrieve-validate loop):
  STEP 1 (offline, tools/benchmark_trap_check/build_propara_process_physics_kb_v1.py): a DISTILLED
    process-physics co-participation KB -- GENERAL type-level science (combustion consumes fuel+
    oxygen -> produces CO2+ash), authored from public middle-school science + TRAIN process topics,
    NEVER from TEST gold grids, NO per-paragraph (participant,step,effect) tuples. 18 process types.
  STEP 2 (in-cell, no gold): for each paragraph, MATCH process type(s) by signature-keyword overlap
    with the text; MAP each participant to a role (consumes/produces/moves) by lexical overlap with
    the matched process's role lists; SOURCE (effect, trigger_verb_class) facts
    (consumes->DESTROY, produces->CREATE, moves->MOVE).
  STEP 3: re-run the SAME retrieve-validate loop WITH_distilled vs WITHOUT vs WITH_oracle vs
    prior_lesion in one run, unmentioned subset, official metric.

DECISIVE = distilled SURVIVAL FRACTION = distilled_lift / oracle_lift (oracle +0.106).

LEAK-SAFETY (paramount -- the KB is LLM/agent-distilled):
  - HELD-OUT: process types from TRAIN topics; test on held-out TEST paragraphs.
  - NO-LEAK: WITH_distilled must stay < 0.95 AND must NOT approach the oracle 0.463 (if it does, the
    KB leaked per-instance answers, not general knowledge -> FLAG + reject). Bounded by the ~0.73
    cueless cap.
  - ABLATION: WITHOUT must still collapse (< 0.60). prior-lesion as before.
  - The KB carries a HAND-VET of 10 facts (each independently-verifiable general science), surfaced
    in metrics for audit.

Residual oracle dependency (flagged): event-COUNT budget only (all arms). Distilled bridge FACTS
are 100% from the general KB + no-gold text mapping.

Modes: --self-test / --smoke (DEV) / --full (TEST).
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
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

import numpy as np

ANCHOR_NAME = "propara_bridging_distilled_kb_endtoend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
KB_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_process_physics_kb_v1.json")

import propara_official_eval as offeval  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers, _official_corpus_scores, _proxy_scores, _arms_must_differ,
)
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING,
)
from experiments.exp_propara_bridging_real_kb_sourcing_v1 import _fact_coverage  # noqa: E402
from experiments.exp_propara_arm2_extracted_structure_v1 import _load_coref  # noqa: E402
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

_WORD = re.compile(r"[a-z]+")

# Survival bar (pre-registered BEFORE running; see prereg)
SURVIVAL_HARD_PASS = 0.50    # distilled recovers >= 50% of the oracle lift -> validated end-to-end pipeline
SURVIVAL_HARD_FAIL = 0.25    # < 0.25 -> even a built KB does not carry it -> report the residual
LEAK_ORACLE_MARGIN = 0.02    # with_distilled >= oracle - this -> suspiciously answer-like -> FLAG leak


def _toks(s):
    return {t for t in _WORD.findall(s.lower()) if len(t) > 2}


def _singularize(t):
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("es") and len(t) > 4:
        return t[:-2]
    if t.endswith("s") and len(t) > 3:
        return t[:-1]
    return t


def _norm_toks(s):
    """Tokens plus singular/plural variants, so 'plants' matches role keyword 'plant'."""
    base = _toks(s)
    out = set(base)
    for t in base:
        out.add(_singularize(t))
        out.add(t + "s")
    return out


# ============================================================================ distilled KB sourcing (no gold)
def _load_kb():
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


_ROLE_EFFECT = [("consumes", "DESTROY", {"DESTROY", "CREATE"}),
                ("produces", "CREATE", {"CREATE"}),
                ("moves", "MOVE", {"MOVE"})]


def _build_distilled_bridge_facts(paragraphs, kb) -> Tuple[Dict[Tuple, Dict[str, Set[str]]], Dict]:
    """MATCH process type(s) per paragraph by signature overlap; MAP each participant to a role by
    lexical overlap; SOURCE (effect, trigger_verb_class) facts. NO gold."""
    procs = kb["processes"]
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    proc_log = {}
    n_role_hits = 0
    for para in paragraphs:
        pid = str(para["para_id"])
        text_toks = _toks(" ".join(para["sentence_texts"]))
        scored = [(name, len(set(d["signature"]) & text_toks)) for name, d in procs.items()]
        scored = sorted([s for s in scored if s[1] > 0], key=lambda kv: -kv[1])
        matched = [name for name, sc in scored[:2]]  # top-2 process types (DEV: top-1 was worse, 0.033 vs 0.081)
        proc_log[pid] = matched
        for participant in para["participants"]:
            p_toks = _norm_toks(participant)
            fdict: Dict[str, Set[str]] = {}
            for pname in matched:
                d = procs[pname]
                for role, effect, trigs in _ROLE_EFFECT:
                    role_toks = set(d.get(role, [])) | {_singularize(x) for x in d.get(role, [])}
                    if p_toks & role_toks:
                        fdict.setdefault(effect, set()).update(trigs)
                        n_role_hits += 1
            facts[(pid, participant)] = fdict
    stats = {"n_paragraphs_matched": sum(1 for v in proc_log.values() if v),
             "n_role_hits": n_role_hits,
             "process_match_sample": {k: proc_log[k] for k in list(proc_log)[:8]}}
    return facts, stats


# ============================================================================ decomposition
def run_decomposition(split: str, train_paragraphs: List[Dict]) -> Dict:
    t0 = time.time()
    paragraphs = _load_split(split)
    steps_df = build_step_rows(paragraphs)
    train_steps_df = build_step_rows(train_paragraphs)
    train_set_df = build_paragraph_set_rows(train_paragraphs)
    vec, clf = fit_step_bow(train_steps_df)
    bag_clfs = fit_bag_of_states_classifiers(train_set_df)
    oracle_multiset = _oracle_event_multiset(steps_df)
    coref = _load_coref(split)
    kb = _load_kb()

    print(f"[precompute] {len(paragraphs)} paragraphs (extraction + oracle facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}

    print("[distilled] process-physics KB sourcing (match process + map roles, no gold)...", flush=True)
    distilled_facts, distilled_stats = _build_distilled_bridge_facts(paragraphs, kb)
    cov = _fact_coverage(distilled_facts, oracle_facts)

    pre_distilled = {}
    for para in paragraphs:
        pid = str(para["para_id"])
        pr = dict(pre_oracle[pid])
        pr["bridge"] = {pp: distilled_facts.get((pid, pp), {}) for pp in para["participants"]}
        pre_distilled[pid] = pr

    grids: Dict[str, Dict] = {}
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre_oracle)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre_oracle, use_bridge=False)
    grids["with_oracle"], oracle_diag = _grids(paragraphs, pre_oracle, use_bridge=True)
    grids["with_distilled"], distilled_diag = _grids(paragraphs, pre_distilled, use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    distilled_f1 = unm["with_distilled"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    distilled_lift = distilled_f1 - without_f1
    survival = (distilled_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None

    diff = _arms_must_differ({"prior_lesion": grids["prior_lesion"], "without_knowledge": grids["without_knowledge"],
                              "with_oracle": grids["with_oracle"], "with_distilled": grids["with_distilled"]})

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff,
        "decode": {"lesion": lesion_diag["decode_fidelity"], "without": without_diag["decode_fidelity"],
                   "oracle": oracle_diag["decode_fidelity"], "distilled": distilled_diag["decode_fidelity"]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1, "with_distilled_f1": distilled_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "distilled_lift": distilled_lift, "survival_fraction": survival,
        "distilled_minus_prior_lesion": distilled_f1 - lesion_f1,
        "fact_coverage_distilled_vs_oracle": cov,
        "distilled_sourcing_stats": distilled_stats,
        "kb_hand_vet": kb["_meta"]["hand_vet_general_science"],
        "kb_n_processes": kb["_meta"]["n_processes"],
        "official": {arm: official[arm]["overall"] for arm in official},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    survival = result["survival_fraction"]
    distilled_lift = result["distilled_lift"]
    without_f1 = result["without_f1"]
    distilled_f1 = result["with_distilled_f1"]
    oracle_f1 = result["with_oracle_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    ablation_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = (distilled_f1 > LEAK_CEILING) or (distilled_f1 >= oracle_f1 - LEAK_ORACLE_MARGIN)
    survives = (survival is not None and survival >= SURVIVAL_HARD_PASS)
    no_go = (survival is None) or (survival < SURVIVAL_HARD_FAIL) or (distilled_lift < 0.02)

    cov = result["fact_coverage_distilled_vs_oracle"]
    msg = (f"split={result['split']} DISTILLED_SURVIVAL={survival} (distilled_lift={distilled_lift:.4f} / "
           f"oracle_lift={result['oracle_lift']:.4f}) with_distilled_f1={distilled_f1:.4f} "
           f"oracle_f1={oracle_f1:.4f} without_f1={without_f1:.4f} "
           f"distilled_pair_recall={cov['pair_recall']} pair_precision={cov['pair_precision']} "
           f"ablation_collapsed={ablation_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not ablation_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_ABLATION_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "HARD_FAIL", f"HARD_FAIL_KB_LEAKED_ANSWERS_reject: {msg}"
    if survives:
        return "HARD_PASS", f"HARD_PASS_END_TO_END_PIPELINE_VALIDATED_built_KB: {msg}"
    if no_go:
        return "HARD_FAIL", f"HARD_FAIL_DISTILLED_KB_SURVIVAL_LOW_residual: {msg}"
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
    kb = _load_kb()
    assert kb["_meta"]["n_processes"] >= 12, kb["_meta"]
    assert len(kb["_meta"]["hand_vet_general_science"]) >= 10

    # synth: a fossilization paragraph; 'plants' UNMENTIONED at a burial step -> distilled KB maps
    # plants -> consumes role of fossilization -> DESTROY fact.
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["Plants die and fall.", "Sediment buries the remains.",
                            "Millions of years pass.", "The material becomes oil."],
         "participants": ["plants"],
         "states": [["-", "here", "here", "here", "-"]]},  # DESTROY somewhere unmentioned
    ]
    facts, stats = _build_distilled_bridge_facts(synth, kb)
    f = facts[("s1", "plants")]
    # 'plants' is in fossilization/hydrocarbon consumes -> DESTROY sourced
    assert "DESTROY" in f, (f, stats)
    assert stats["n_role_hits"] >= 1, stats

    text = " ".join(synth[0]["sentence_texts"]); offs = []; cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    coref = {"s1": {"text": text, "sentence_offsets": offs, "n_sentences": 4, "clusters": []}}
    steps_df = build_step_rows(synth)
    oracle = _oracle_event_multiset(steps_df)
    pre = _paragraph_precompute(synth, oracle, coref, steps_df)
    pre_d = {"s1": {**pre["s1"], "bridge": {"plants": f}}}
    gd, dd = _grids(synth, pre_d, use_bridge=True)
    assert dd["decode_fidelity"] == 1.0
    assert "DESTROY" in gd["s1"]["plants"], gd["s1"]["plants"]

    # verdict-logic unit checks
    hp = {"split": "x", "survival_fraction": 0.6, "distilled_lift": 0.07, "oracle_lift": 0.11,
          "without_f1": 0.35, "with_distilled_f1": 0.42, "with_oracle_f1": 0.46, "arms_differ": {"all_differ": True},
          "decode": {"a": 1.0}, "fact_coverage_distilled_vs_oracle": {"pair_recall": 0.5, "pair_precision": 0.3}}
    hv, _ = decomposition_verdict(hp)
    assert hv == "HARD_PASS", hv
    leak = dict(hp); leak["with_distilled_f1"] = 0.46
    lv, _ = decomposition_verdict(leak)
    assert lv == "HARD_FAIL", lv  # distilled ~= oracle -> leak
    nogo = dict(hp); nogo["survival_fraction"] = 0.1; nogo["distilled_lift"] = 0.01
    nv, _ = decomposition_verdict(nogo)
    assert nv == "HARD_FAIL", nv
    void = dict(hp); void["without_f1"] = 0.7
    vv, _ = decomposition_verdict(void)
    assert vv == "HARD_FAIL", vv

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "kb_n_processes": kb["_meta"]["n_processes"],
            "distilled_fact_plants": {k: sorted(v) for k, v in f.items()}, "sourcing_stats": stats,
            "with_distilled_plants_labels": gd["s1"]["plants"],
            "verdict_logic_unit_checks": {"hard_pass": hv, "leak": lv, "no_go": nv, "void": vv}}


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
    print(f"[{run_mode}] split={split} DISTILLED process-KB end-to-end culmination test...", flush=True)
    result = run_decomposition(split, train_paragraphs)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "DISTILLED_SURVIVAL_FRACTION": result["survival_fraction"],
            "with_distilled_f1": result["with_distilled_f1"], "with_oracle_f1": result["with_oracle_f1"],
            "without_f1": result["without_f1"], "prior_lesion_f1": result["prior_lesion_f1"],
            "distilled_lift": result["distilled_lift"], "oracle_lift": result["oracle_lift"],
            "distilled_minus_prior_lesion": result["distilled_minus_prior_lesion"],
            "distilled_pair_recall": result["fact_coverage_distilled_vs_oracle"]["pair_recall"],
            "distilled_pair_precision": result["fact_coverage_distilled_vs_oracle"]["pair_precision"],
            "distilled_sourcing_stats": result["distilled_sourcing_stats"],
            "kb_hand_vet_general_science": result["kb_hand_vet"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: survival bar pre-registered before TEST",
        "thresholds": {"SURVIVAL_HARD_PASS": SURVIVAL_HARD_PASS, "SURVIVAL_HARD_FAIL": SURVIVAL_HARD_FAIL,
                       "LEAK_CEILING": LEAK_CEILING, "LEAK_ORACLE_MARGIN": LEAK_ORACLE_MARGIN,
                       "WITHOUT_COLLAPSE_CEILING": WITHOUT_COLLAPSE_CEILING},
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
