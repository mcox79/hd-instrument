# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; without/with_oracle/with_real/lesion differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {real_kb: [survival_fraction_material, real_ablation_collapses, real_no_leak]}
# - cardinality_ok: single split, one pass; EXPECTED arms fixed
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (bands DEV-calibrated, pinned before TEST)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (spaCy SRL + real-KB sourcing + firing + official_eval)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_bridging_real_kb_sourcing_v1.md for the full pre-reg.
"""exp_propara_bridging_real_kb_sourcing_v1 -- the GO/NO-GO on the bridging-KB foundation.

The oracle-knowledge diagnostic (exp_propara_bridging_knowledge_vs_mechanism_v1, HARD_PASS)
proved the retrieve-validate loop USES typed causal bridging facts (WITH 0.463 / WITHOUT 0.356 on
the unmentioned subset, +0.106 load-bearing, no leak) -> the unmentioned-state wall is KNOWLEDGE-
SOURCING, not the mechanism. This cell answers: how much of that +0.106 SURVIVES when the bridge
facts are sourced from a REAL non-oracle KB instead of gold?

ONE CLEAN VARIABLE vs the diagnostic: oracle bridge facts -> REAL-KB-sourced bridge facts. The
loop + all controls (WITHOUT ablation, prior-lesion, no-leak ceiling, unmentioned subset, official
metric, oracle event-COUNT budget granted to all arms) are IDENTICAL (imported verbatim from the
diagnostic cell).

REAL-KB SOURCING of the typed (effect_type, trigger_verb_class) facts -- NO gold (effect/label/step):
  1. VERB-CLASS -> EFFECT semantics (generic, VerbNet/FrameNet-style, hand-curated rule; the same
     verb-class lexicon reused from v3): a DESTROY-class verb (consume/burn/dissolve/absorb) ->
     its PATIENT is DESTROYED; a CREATE-class verb (form/become/produce) -> its OBJECT/product is
     CREATED and (for "become"-type conversion) its SUBJECT/precursor is DESTROYED; a MOVE-class
     verb (move/flow/enter/fall) -> its THEME MOVES.
  2. PARTICIPANT BINDING via spaCy dep-parse SRL-lite (the patient/theme argument = the affected
     participant) + fastcoref alias resolution (the argument noun, incl. pronouns like it/they,
     resolved to a participant via its coref cluster). NOT oracle participant->effect.
  The real-KB fact for participant p = { (effect, verb_class) : some verb of that class in the
  paragraph has an affected argument (by role) that binds to p (exact-name or coref-alias) }.
  ConceptNet participant-role affordances = NOT used in v1 (flagged; a gap-filler if survival is
  low and binding is the bottleneck).

RESIDUAL ORACLE DEPENDENCY (flagged): the event-COUNT budget is still oracle-granted to ALL arms
(same as the diagnostic; that extraction cost was measured in ARM2). The bridge FACTS in the
with_real arm are 100% real-sourced (no gold effect/label/step). No other oracle dependency.

DECISIVE MEASUREMENT = SURVIVAL FRACTION = (with_real - without) / (with_oracle - without) on the
unmentioned subset. All computed in ONE run (self-contained), so with_oracle reproduces the
diagnostic and survival is measured on the identical split.

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
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

import numpy as np

ANCHOR_NAME = "propara_bridging_real_kb_sourcing_v1"
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
    _official_corpus_scores, _proxy_scores, _arms_must_differ,
)
from experiments.exp_propara_decisive_inference_arm1_v3_stateful_verb_v1 import (  # noqa: E402
    VERB_CLASS_SETS, _rng,
)
from experiments.exp_propara_arm2_extracted_structure_v1 import _get_nlp, _load_coref  # noqa: E402
# REUSE the diagnostic's loop + controls VERBATIM (one clean variable = the bridge facts):
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING, WITH_MINUS_WITHOUT_HARD_PASS,
)
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

SCRAMBLE_SEEDS = [7, 17]

# Survival bar (pre-registered BEFORE running; see prereg)
SURVIVAL_HARD_PASS = 0.50   # real-KB recovers >= 50% of the oracle +0.106 lift -> GO on the KB foundation
SURVIVAL_HARD_FAIL = 0.25   # real-KB recovers < 25% -> real sourcing does not carry the bridge -> NO-GO (localize gap)
CONVERSION_LEMMAS = {"become", "becomes", "became", "turn", "turns", "turned", "form", "forms",
                     "formed", "convert", "converts", "converted", "transform", "transforms"}


# ============================================================================ REAL-KB sourcing (generic verb-class->effect + SRL-lite binding + coref)
def _alias_tokens_by_participant(participant_list: List[str], para_coref: Dict) -> Dict[str, Set[str]]:
    """Per participant: the set of alias TOKENS = its name tokens UNION the tokens of every surface
    string in fastcoref clusters that contain a name-token span (so pronouns/aliases like it/they/
    'the material' become recognizable participant references). NO gold."""
    def _toks(s):
        return {t for t in s.lower().replace(".", " ").replace(",", " ").replace(";", " ").split() if len(t) > 1}
    name_toks = {p: _toks(p) for p in participant_list}
    alias = {p: set(name_toks[p]) for p in participant_list}
    text = para_coref["text"]
    for cl in para_coref["clusters"]:
        surfaces = [text[s[0]:s[1]] for s in cl]
        cl_tokens = set()
        for surf in surfaces:
            cl_tokens |= _toks(surf)
        for p in participant_list:
            if name_toks[p] & cl_tokens:
                alias[p] |= cl_tokens
    return alias


def _arg_tokens(nodes) -> Set[str]:
    out = set()
    for nd in nodes:
        for t in nd.subtree:
            if t.pos_ in ("NOUN", "PROPN", "PRON"):
                out.add(t.text.lower())
    return out


def _verb_effects(doc) -> List[Tuple[str, str, Set[str]]]:
    """Generic verb-class -> (effect, verb_class, affected_arg_tokens) via role. NO gold."""
    out = []
    for tok in doc:
        if tok.pos_ != "VERB":
            continue
        lemma = tok.lemma_.lower()
        V = next((c for c, vs in VERB_CLASS_SETS.items() if lemma in vs), None)
        if V is None:
            continue
        subj = [c for c in tok.children if c.dep_ in ("nsubj", "nsubjpass")]
        obj = [c for c in tok.children if c.dep_ in ("dobj", "attr", "oprd")]
        pobj = [gc for c in tok.children if c.dep_ == "prep" for gc in c.children if gc.dep_ == "pobj"]
        subj_t, obj_t, pobj_t = _arg_tokens(subj), _arg_tokens(obj), _arg_tokens(pobj)
        if V == "DESTROY":
            aff = obj_t if obj_t else subj_t  # patient = object, else intransitive/passive subject
            if aff:
                out.append(("DESTROY", V, aff))
        elif V == "CREATE":
            if obj_t:
                out.append(("CREATE", V, obj_t))            # product created
            if subj_t and lemma in CONVERSION_LEMMAS and obj_t:
                out.append(("DESTROY", V, subj_t))          # precursor destroyed in conversion X->Y
            elif subj_t and not obj_t:
                out.append(("CREATE", V, subj_t))           # intransitive 'X forms' -> X created
        elif V == "MOVE":
            aff = subj_t | obj_t
            if aff:
                out.append(("MOVE", V, aff))
    return out


def _build_real_kb_bridge_facts(paragraphs, coref) -> Dict[Tuple, Dict[str, Set[str]]]:
    """Real-KB (effect_type, trigger_verb_class) facts per (para, participant), sourced from
    generic verb-class->effect semantics + SRL-lite dep-parse binding + coref alias resolution.
    NO gold (effect/label/step)."""
    nlp = _get_nlp()
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    for para in paragraphs:
        pid = str(para["para_id"])
        alias = _alias_tokens_by_participant(para["participants"], coref[pid])
        for participant in para["participants"]:
            facts[(pid, participant)] = {}
        docs = list(nlp.pipe(para["sentence_texts"]))
        for doc in docs:
            for effect, V, aff_tokens in _verb_effects(doc):
                for participant in para["participants"]:
                    if aff_tokens & alias[participant]:
                        facts[(pid, participant)].setdefault(effect, set()).add(V)
    return facts


# ============================================================================ fact-coverage diagnostic (real vs oracle)
def _fact_coverage(real_facts, oracle_facts) -> Dict:
    """How well the real-KB (effect, trigger) pairs reconstruct the oracle facts (which participants
    got ANY real fact; pair-level precision/recall)."""
    tp = fp = fn = 0
    n_oracle_parts_with_fact = 0
    n_oracle_parts_covered = 0
    for key, ofd in oracle_facts.items():
        opairs = {(e, v) for e, vs in ofd.items() for v in vs}
        if not opairs:
            continue
        n_oracle_parts_with_fact += 1
        rfd = real_facts.get(key, {})
        rpairs = {(e, v) for e, vs in rfd.items() for v in vs}
        if rpairs:
            n_oracle_parts_covered += 1
        tp += len(opairs & rpairs)
        fn += len(opairs - rpairs)
    for key, rfd in real_facts.items():
        rpairs = {(e, v) for e, vs in rfd.items() for v in vs}
        ofd = oracle_facts.get(key, {})
        opairs = {(e, v) for e, vs in ofd.items() for v in vs}
        fp += len(rpairs - opairs)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    return {"pair_precision": round(prec, 4), "pair_recall": round(rec, 4),
            "pair_f1": round(2 * prec * rec / (prec + rec), 4) if (prec + rec) else 0.0,
            "participant_binding_coverage": round(n_oracle_parts_covered / max(n_oracle_parts_with_fact, 1), 4),
            "n_oracle_participants_with_fact": n_oracle_parts_with_fact,
            "n_oracle_participants_covered_by_real": n_oracle_parts_covered}


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

    print(f"[precompute] {len(paragraphs)} paragraphs (extraction + oracle bridge facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)  # bridge = oracle
    print("[real-kb] sourcing bridge facts from generic verb-class->effect + SRL + coref...", flush=True)
    real_facts = _build_real_kb_bridge_facts(paragraphs, coref)
    # oracle facts (for coverage diagnostic) = pre_oracle bridge
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}
    coverage = _fact_coverage(real_facts, oracle_facts)

    # pre_real: same as pre_oracle but bridge slot = real-KB facts
    pre_real = {}
    for para in paragraphs:
        pid = str(para["para_id"])
        pr = dict(pre_oracle[pid])
        pr["bridge"] = {pp: real_facts.get((pid, pp), {}) for pp in para["participants"]}
        pre_real[pid] = pr

    grids: Dict[str, Dict] = {}
    grids["majority"] = majority_label_grids(paragraphs)
    grids["bow_singlestep"] = bow_label_grids(paragraphs, vec, clf)
    grids["bagstates"] = bag_of_states_label_grids(paragraphs, bag_clfs)
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre_oracle)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre_oracle, use_bridge=False)
    grids["with_oracle"], oracle_diag = _grids(paragraphs, pre_oracle, use_bridge=True)
    grids["with_real_kb"], real_diag = _grids(paragraphs, pre_real, use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    real_f1 = unm["with_real_kb"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    real_lift = real_f1 - without_f1
    survival = (real_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None

    diff = _arms_must_differ({"without_knowledge": grids["without_knowledge"],
                              "with_oracle": grids["with_oracle"], "with_real_kb": grids["with_real_kb"],
                              "prior_lesion": grids["prior_lesion"]})

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff, "decode": {"lesion": lesion_diag["decode_fidelity"],
                                        "without": without_diag["decode_fidelity"],
                                        "with_oracle": oracle_diag["decode_fidelity"],
                                        "with_real_kb": real_diag["decode_fidelity"]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1, "with_real_kb_f1": real_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "real_lift": real_lift, "survival_fraction": survival,
        "real_minus_without": real_lift, "real_minus_prior_lesion": real_f1 - lesion_f1,
        "fact_coverage_real_vs_oracle": coverage,
        "official": {arm: official[arm]["overall"] for arm in official},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    survival = result["survival_fraction"]
    real_lift = result["real_lift"]
    without_f1 = result["without_f1"]
    real_f1 = result["with_real_kb_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    ablation_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = real_f1 > LEAK_CEILING
    real_load_bearing = real_lift >= WITH_MINUS_WITHOUT_HARD_PASS
    survives = (survival is not None and survival >= SURVIVAL_HARD_PASS)
    no_go = (survival is None) or (survival < SURVIVAL_HARD_FAIL) or (real_lift < 0.02)

    cov = result["fact_coverage_real_vs_oracle"]
    msg = (f"split={result['split']} SURVIVAL={survival} (real_lift={real_lift:.4f} / oracle_lift={result['oracle_lift']:.4f}) "
           f"with_real_f1={real_f1:.4f} without_f1={without_f1:.4f} "
           f"real_pair_recall={cov['pair_recall']} binding_cov={cov['participant_binding_coverage']} "
           f"ablation_collapsed={ablation_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not ablation_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_ABLATION_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "MIDDLE_BAND", f"MIDDLE_BAND_POSSIBLE_LEAK: {msg}"
    if survives and real_load_bearing:
        return "HARD_PASS", f"HARD_PASS_REAL_KB_SOURCES_THE_BRIDGE_GO: {msg}"
    if no_go:
        return "HARD_FAIL", f"HARD_FAIL_REAL_KB_DOES_NOT_SOURCE_NO_GO: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND_PARTIAL_SURVIVAL: {msg}"


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

    # "the fire consumes everything" -> real-KB should source (DESTROY, DESTROY) for a participant
    # coref-linked to "everything"/pronoun; here test direct patient binding.
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["A seed appears in soil.", "Water is added.",
                            "The fire consumes the seed.", "Ash remains."],
         "participants": ["seed"],
         "states": [["-", "soil", "soil", "-", "-"]]},  # CREATE@1, DESTROY@3 (seed IS patient of consume)
    ]
    text = " ".join(synth[0]["sentence_texts"]); offs = []; cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    coref = {"s1": {"text": text, "sentence_offsets": offs, "n_sentences": 4, "clusters": []}}

    real_facts = _build_real_kb_bridge_facts(synth, coref)
    fseed = real_facts[("s1", "seed")]
    # seed appears (CREATE) + consume(seed) (DESTROY) -> real-KB sources both from generic semantics
    assert "DESTROY" in fseed and "DESTROY" in fseed["DESTROY"], fseed  # consume -> patient destroyed
    assert "CREATE" in fseed, fseed  # appear/intransitive create OR seed as subject; appears is CREATE-class

    steps_df = build_step_rows(synth)
    oracle = _oracle_event_multiset(steps_df)
    pre = _paragraph_precompute(synth, oracle, coref, steps_df)
    pre_real = {"s1": {**pre["s1"], "bridge": {"seed": real_facts[("s1", "seed")]}}}
    gr, drg = _grids(synth, pre_real, use_bridge=True)
    assert drg["decode_fidelity"] == 1.0
    # WITH real-KB places seed DESTROY at the consume step (3)
    assert gr["s1"]["seed"][2] == "DESTROY", gr["s1"]["seed"]

    cov = _fact_coverage(real_facts, {("s1", "seed"): pre["s1"]["bridge"]["seed"]})
    assert 0.0 <= cov["pair_recall"] <= 1.0

    # verdict-logic unit checks
    go = {"split": "x", "survival_fraction": 0.7, "real_lift": 0.08, "without_f1": 0.35, "with_real_kb_f1": 0.42,
          "oracle_lift": 0.11, "arms_differ": {"all_differ": True},
          "decode": {"a": 1.0}, "fact_coverage_real_vs_oracle": {"pair_recall": 0.6, "participant_binding_coverage": 0.7}}
    gv, _ = decomposition_verdict(go)
    assert gv == "HARD_PASS", gv
    nogo = dict(go); nogo["survival_fraction"] = 0.1; nogo["real_lift"] = 0.01
    nv, _ = decomposition_verdict(nogo)
    assert nv == "HARD_FAIL", nv
    mid = dict(go); mid["survival_fraction"] = 0.35
    mv, _ = decomposition_verdict(mid)
    assert mv == "MIDDLE_BAND", mv
    void = dict(go); void["without_f1"] = 0.7
    vv, _ = decomposition_verdict(void)
    assert vv == "HARD_FAIL", vv  # ablation did not collapse

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "real_kb_fact_seed": {k: sorted(v) for k, v in fseed.items()},
            "with_real_seed_labels": gr["s1"]["seed"], "fact_coverage_synth": cov,
            "verdict_logic_unit_checks": {"go": gv, "no_go": nv, "middle": mv, "void": vv}}


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
    print(f"[{run_mode}] split={split} real-KB bridge sourcing go/no-go...", flush=True)
    result = run_decomposition(split, train_paragraphs)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "SURVIVAL_FRACTION": result["survival_fraction"],
            "with_real_kb_f1": result["with_real_kb_f1"], "with_oracle_f1": result["with_oracle_f1"],
            "without_f1": result["without_f1"], "prior_lesion_f1": result["prior_lesion_f1"],
            "real_lift": result["real_lift"], "oracle_lift": result["oracle_lift"],
            "real_minus_prior_lesion": result["real_minus_prior_lesion"],
            "fact_coverage_real_vs_oracle": result["fact_coverage_real_vs_oracle"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: survival bar pre-registered before TEST",
        "thresholds": {"SURVIVAL_HARD_PASS": SURVIVAL_HARD_PASS, "SURVIVAL_HARD_FAIL": SURVIVAL_HARD_FAIL,
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
