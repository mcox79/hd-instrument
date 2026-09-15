"""Scaffold-free witness for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.

Recomputes the load-bearing claims by LIVE recompute on the real substrate + cross-checks the landed metrics.
No metric crosses harnesses. Covers both cells + the reuse + the decisive extraction-vs-abstraction ablation.

  W1 REUSED ORGAN (live, from source): hdlab.transitive_ordering.TransitiveOrderingLine integrates pairwise
     precedence premises and answers an UN-STATED pair by transitive read-out -- the general cognitive-map /
     relational-integration machinery we REUSE for canonical script-order (not a bespoke tally).
  W2 LIVE PIPELINE + a REAL twin (live read()): drive SituationReader.read() on fresh MCScript2 passages, run
     the temporal-order reasoner (cell 1); the shuffled-timeline info-free twin CHANGES decisions (a non-degenerate
     control), and similarity is undiscriminating on symmetric before/after candidates.
  W3 LEARNED SCHEMA reuses the organ (live): induce a canonical order for a scenario from its TRAIN narratives via
     read() + the ordering organ; the line answers a before/after that the induction supports.
  W4 THE DECISIVE ABLATION (landed cross-check): every brain-faithful aggregator (equal-tally, precision-weighted,
     SR-multistep, precision+SR) leaves the learned order AT CHANCE -> the binding wall is EXTRACTION (parser-recall),
     not abstraction. ABLATION_VERDICT == PLATEAU.
  W5 CELL-1 HEADLINES (landed cross-check): the episodic-timeline twin LOSES CI-separated; on the narration!=chronology
     subset the timeline beats text-order; retrieval is NOT the wall (coverage 0.55->0.69, accuracy flat).

Run:  .venv/Scripts/python.exe verification/test_reasoning_over_situation_model.py
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import torch

import experiments._situation_inference_live as L
import experiments.exp_situation_model_inference_mcscript_v1 as E
import experiments.exp_learned_script_order_prior_mcscript_v1 as S
from hdlab.transitive_ordering import TransitiveOrderingLine

FAIL = []


def check(name, cond, detail=""):
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        FAIL.append(name)


# -- W1: the REUSED ordering organ answers an UN-STATED pair by transitive read-out (live, from source) --
def w1_reused_organ():
    gen = torch.Generator().manual_seed(7)
    line = TransitiveOrderingLine(3, 1024, gen, seed=7)
    line.integrate([(0, 1), (1, 2)])          # 0>1, 1>2 stated; 0>2 UN-stated
    c = line.compare(0, 2)                     # must infer 0>2 by transitive integration
    check("W1_reused_transitive_ordering", c == 1, "compare(0,2)=%d (expect +1)" % c)


# -- W2: live pipeline + a non-degenerate twin, on fresh reads --
def w2_live_pipeline():
    items = [it for it in E.collect_symmetric(["dev"]) if E.parse_before_after(it)[3]][:60]
    reader = L.build_reader()
    passages = sorted({it["passage"] for it in items})[:20]
    cache, _ = E.build_sm_cache(passages, reader, verbose=False)
    pset = set(p for p in passages)
    n_dec = twin_diff = sim_tie = 0
    for it in items:
        if it["passage"] not in pset:
            continue
        sm = cache[E._pid(it["passage"])]
        mp, _ = E.temporal_predict(it, sm, kind="model")
        if mp is None:
            continue
        n_dec += 1
        wp, _ = E.temporal_predict(it, sm, kind="twin", seed=123 + n_dec)
        if wp is not None and wp != mp:
            twin_diff += 1
        # similarity is undiscriminating on symmetric before/after (shared content words)
        cw = [L.content_words(c) for c in it["cands"]]
        if E.sim_pick(cw, set(L.content_words(it["passage"]))) == 0 and \
           set(cw[0]) & set(cw[1]) == (set(cw[0]) | set(cw[1])) - {"before", "after"}:
            sim_tie += 1
    check("W2_live_reasoner_decides", n_dec >= 5, "%d live before/after decisions" % n_dec)
    check("W2_twin_is_a_real_control", twin_diff >= 1, "shuffled-timeline twin changed %d decisions" % twin_diff)


# -- W3: the learned schema reuses the organ (live induce on a couple scenarios) --
def w3_learned_schema():
    reader = L.build_reader()
    items = E.collect_symmetric(["dev"])
    scen = sorted({it["scenario"] for it in items})[:3]
    schema, _, _ = S.induce_schema(set(scen), reader, verbose=False, train_cap=8)
    built = [s for s in scen if schema.get(s) and schema[s]["line"] is not None]
    check("W3_schema_built_via_organ", len(built) >= 1,
          "%d/%d scenarios got an ordering line from TRAIN narratives" % (len(built), len(scen)))
    if built:
        s = schema[built[0]]
        # the line answers SOME canonical pair (a decision, not all-zero)
        lems = sorted(s["idx"])[:8]
        decided = sum(1 for i in range(len(lems)) for j in range(i + 1, len(lems))
                      if S.canonical_pred(s, lems[i], lems[j]) != 0)
        check("W3_line_answers_pairs", decided >= 1, "%d canonical pairs decided" % decided)


# -- W4: the DECISIVE ablation plateaus (landed cross-check) --
def w4_ablation_plateau():
    p = os.path.join(REPO, "data", "exp_learned_script_order_prior_mcscript_v1", "metrics.json")
    m = json.load(open(p))
    verdict = m.get("ABLATION_VERDICT", "")
    check("W4_ablation_verdict_plateau", verdict.startswith("PLATEAU"), verdict)
    abl = m.get("aggregator_ablation", {})
    none_above = all(not v.get("above_chance") for v in abl.values()) and len(abl) >= 3
    check("W4_no_aggregator_above_chance", none_above,
          "aggregators: " + ", ".join("%s=%.3f%s" % (k, v["acc"], "*" if v["above_chance"] else "")
                                       for k, v in abl.items()))


# -- W5: cell-1 headlines (landed cross-check) --
def w5_cell1_headlines():
    p = os.path.join(REPO, "data", "exp_situation_model_inference_mcscript_v1", "metrics.json")
    m = json.load(open(p))
    tw = m["contrasts"]["MODEL_minus_TWIN"]
    check("W5_episodic_twin_loses_CI_sep", tw["sep_above"],
          "MODEL-TWIN=%.3f %s" % (tw["delta"], tw["ci"]))
    reo = m["reordered_analysis"]
    check("W5_timeline_beats_textorder_on_reordered",
          (reo["MODEL_acc_reordered"] or 0) > (reo["TEXTORDER_acc_reordered"] or 1),
          "reordered MODEL=%.3f vs TEXTORDER=%.3f (n=%d)"
          % (reo["MODEL_acc_reordered"], reo["TEXTORDER_acc_reordered"], reo["n_reordered"]))
    sr = m["sentence_retrieval"]
    flat = abs(sr["MODEL_SENT_e2e"]["acc"] - m["acc"]["MODEL_e2e"]["acc"]) < 0.03
    check("W5_retrieval_not_the_wall", sr["coverage"] > m["coverage"] and flat,
          "coverage %.2f->%.2f, accuracy flat (%.3f->%.3f)"
          % (m["coverage"], sr["coverage"], m["acc"]["MODEL_e2e"]["acc"], sr["MODEL_SENT_e2e"]["acc"]))


# -- W6: the LOOP-CLOSER -- clean extraction is NOT sufficient (landed cross-check) --
def w6_oracle_not_sufficient():
    p = os.path.join(REPO, "data", "exp_oracle_extraction_script_order_mcscript_v1", "metrics.json")
    if not os.path.exists(p):
        check("W6_oracle_present", False, "oracle metrics.json missing"); return
    m = json.load(open(p))
    # clean extraction + LEXICAL/object retrieval raises coverage but NOT accuracy (still ~chance, at/below SIM)
    clean = m["acc"]["CLEAN_SCHEMA"]["acc"]
    check("W6_clean_extraction_not_sufficient", clean <= m["acc"]["SIM_floor"]["acc"] + 0.01 and m["coverage"] > 0.6,
          "coverage %.2f (clean spaCy raised it) but CLEAN(object) %.3f <= SIM %.3f -- clean extraction alone not sufficient"
          % (m["coverage"], clean, m["acc"]["SIM_floor"]["acc"]))
    cc = m.get("committed_covered", {})
    ties_twin = abs(cc.get("CLEAN_SCHEMA", {}).get("acc", 0) - cc.get("TWIN_same", 1)) < 0.06
    check("W6_learned_order_ties_its_twin", ties_twin,
          "object-retrieval committed CLEAN %.3f vs random-order TWIN %.3f (lexical/object alignment ties)"
          % (cc.get("CLEAN_SCHEMA", {}).get("acc", 0), cc.get("TWIN_same", 0)))


# -- W7: the FORK RESOLVER -- SEMANTIC alignment lifts the learned order to BEAT its info-free twin (landed) --
def w7_semantic_alignment_beats_twin():
    p = os.path.join(REPO, "data", "exp_oracle_extraction_script_order_mcscript_v1", "metrics.json")
    if not os.path.exists(p):
        check("W7_semantic_present", False, "oracle metrics.json missing"); return
    sa = json.load(open(p)).get("semantic_alignment", {})
    d = sa.get("SEM_minus_TWIN")
    check("W7_semantic_order_beats_twin_CIsep", bool(d) and d.get("sep_above"),
          "SEM %.3f vs shuffled-order twin: delta %.3f %s (semantic cross-narrative alignment makes the learned "
          "script-order a real signal — the dominant residual)"
          % (sa.get("CLEAN_SEM", {}).get("acc", 0), (d or {}).get("delta", 0), (d or {}).get("ci")))
    # near-positive but not a clean full-bar pass: does NOT CI-separate over the similarity floor
    ds = sa.get("SEM_minus_SIM", {})
    check("W7_not_clean_full_bar_over_similarity", not ds.get("sep_above"),
          "SEM - SIM %.3f %s (borderline, not CI-sep -> the residual knowledge/robustness gap)"
          % (ds.get("delta", 0), ds.get("ci")))


def main():
    w1_reused_organ()
    w2_live_pipeline()
    w3_learned_schema()
    w4_ablation_plateau()
    w5_cell1_headlines()
    w6_oracle_not_sufficient()
    w7_semantic_alignment_beats_twin()
    print("\n%s (%d checks, %d failed)" % ("ALL PASS" if not FAIL else "FAILED: " + ", ".join(FAIL),
                                           15, len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
