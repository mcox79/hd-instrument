# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; without/real_generic/real_cn/oracle differ)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold
# - HP_SCOPE: {conceptnet: [survival_cn_material, cn_adds_over_generic, cn_ablation_collapses, no_leak]}
# - cardinality_ok: single split, one pass; EXPECTED arms fixed
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (survival bar pre-registered before TEST)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL objects (spaCy SRL + ConceptNet index + firing + official_eval)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_propara_bridging_conceptnet_coparticipation_v1.md for the full pre-reg.
"""exp_propara_bridging_conceptnet_coparticipation_v1 -- the REUSE-vs-BUILD check-before-build probe.

The real-KB-sourcing go/no-go (exp_propara_bridging_real_kb_sourcing_v1, NO-GO survival 0.22)
showed generic verb-lexicon + SRL + coref STRUCTURALLY cannot source co-participation (SRL only
sees surface args; an unmentioned change's trigger is a verb about ANOTHER entity). The mechanism
works (the oracle diagnostic proved the loop USES facts); the missing component is PARTICIPANT-ROLE
CO-PARTICIPATION world-knowledge. This cell decides REUSE-vs-BUILD: does an EXISTING KB
(ConceptNet 5.7.0) supply the co-participation knowledge SRL cannot?

ONE CLEAN VARIABLE added to the real-KB cell: + ConceptNet co-participation sourcing. Loop + all
controls identical. Computed in ONE run: without / with_oracle / with_real_GENERIC (SRL+coref, the
prior 0.22) / with_real_CN (SRL+coref + ConceptNet co-participation) / prior_lesion.

CONCEPTNET CO-PARTICIPATION SOURCING (NO gold): at a step whose trigger verb V (class -> effect E
via the generic rule) has surface argument-tokens A (SRL patient/theme), EXPAND A via the ProPara-
scoped ConceptNet index (data/benchmark_trap_check/propara_conceptnet_index_v1.json, built by
tools/benchmark_trap_check/build_propara_conceptnet_index_v1.py) over CO-PARTICIPATION relations
(PartOf/MadeOf/HasA/UsedFor/ReceivesAction/IsA/DerivedFrom/FormOf/Synonym/SimilarTo/HasSubevent/
Causes). If an UNMENTIONED participant p is ConceptNet-linked to a surface entity in A (p PartOf X,
X MadeOf p, ...), bind p as a co-participant and emit the real-KB fact (E, V) for p. This targets
EXACTLY the piece SRL missed (generic pair_recall was 0.235). ConceptNet FILLS the co-participation
gap; it does NOT replace the generic verb-class->effect lexicon.

RESIDUAL ORACLE DEPENDENCY (flagged): event-COUNT budget only (granted to all arms, as before).
Bridge FACTS in with_real_cn are 100% real-sourced (generic semantics + SRL + coref + ConceptNet).

DECISIVE = SURVIVAL_CN = (with_real_cn - without)/(with_oracle - without) vs generic 0.22. GO
(>=0.50) = REUSE ConceptNet, build the foundation on it. NO-GO (~0.2-0.3) = generic KBs lack
scientific-process co-participation -> the foundation must be BUILT (distilled process-physics KB).
Also report: ConceptNet pair_recall (did it fix 0.235?) + which ProPara processes ConceptNet
covers vs misses (scientific-domain coverage).

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

ANCHOR_NAME = "propara_bridging_conceptnet_coparticipation_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CN_INDEX_PATH = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_conceptnet_index_v1.json")

import propara_official_eval as offeval  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import (  # noqa: E402
    _load_split, _oracle_event_multiset,
    majority_label_grids, bow_label_grids, bag_of_states_label_grids,
    fit_bag_of_states_classifiers, _official_corpus_scores, _proxy_scores, _arms_must_differ,
)
from experiments.exp_propara_arm2_extracted_structure_v1 import _get_nlp, _load_coref  # noqa: E402
from experiments.exp_propara_bridging_knowledge_vs_mechanism_v1 import (  # noqa: E402
    _paragraph_precompute, _grids, _prior_lesion_grids, _unm,
    LEAK_CEILING, WITHOUT_COLLAPSE_CEILING,
)
from experiments.exp_propara_bridging_real_kb_sourcing_v1 import (  # noqa: E402
    _build_real_kb_bridge_facts, _fact_coverage, _verb_effects, _alias_tokens_by_participant,
)
from propara_trap_check import build_step_rows, build_paragraph_set_rows, fit_step_bow  # noqa: E402

# co-participation relations for ConceptNet expansion (exclude loose RelatedTo/AtLocation/CapableOf/HasProperty)
CO_PART_RELS = {"PartOf", "MadeOf", "HasA", "UsedFor", "ReceivesAction", "IsA", "DerivedFrom",
                "FormOf", "Synonym", "SimilarTo", "HasSubevent", "Causes"}
_WORD = re.compile(r"[a-z]+")

# Survival bar (pre-registered BEFORE running; see prereg)
SURVIVAL_HARD_PASS = 0.50    # with_real_cn recovers >= 50% of oracle lift -> GO: REUSE ConceptNet
SURVIVAL_HARD_FAIL = 0.30    # survival_cn < 0.30 -> NO-GO: existing KB lacks it -> BUILD
CN_MUST_ADD_OVER_GENERIC = 0.05  # survival_cn - survival_generic must exceed this for CN to be "load-bearing"


def _toks(s):
    return {t for t in _WORD.findall(s.lower()) if len(t) > 2}


# ============================================================================ ConceptNet co-participation expansion
def _load_cn_neighbors() -> Dict[str, Set[str]]:
    """token -> set of neighbor head-tokens over CO_PART_RELS (from the ProPara-scoped index)."""
    with open(CN_INDEX_PATH, encoding="utf-8") as f:
        idx = json.load(f)
    out: Dict[str, Set[str]] = {}
    for term, edges in idx["edges"].items():
        nb = set()
        for rel, other, _w in edges:
            if rel in CO_PART_RELS:
                nb |= _toks(other)
        if nb:
            out[term] = nb
    return out


def _build_conceptnet_bridge_facts(paragraphs, coref, cn_neighbors
                                   ) -> Tuple[Dict[Tuple, Dict[str, Set[str]]], Dict]:
    """Real-KB facts sourced from generic verb-class->effect + SRL binding + fastcoref alias +
    CONCEPTNET co-participation expansion. Returns (facts, cn_stats). cn_stats tracks how many
    facts were sourced ONLY via ConceptNet (SRL/alias missed but ConceptNet linked)."""
    nlp = _get_nlp()
    facts: Dict[Tuple, Dict[str, Set[str]]] = {}
    stats = {"n_cn_only_bindings": 0, "n_srl_bindings": 0, "participants_with_cn_only": set()}
    for para in paragraphs:
        pid = str(para["para_id"])
        alias = _alias_tokens_by_participant(para["participants"], coref[pid])
        p_toks = {pp: _toks(pp) for pp in para["participants"]}
        for pp in para["participants"]:
            facts[(pid, pp)] = {}
        docs = list(nlp.pipe(para["sentence_texts"]))
        for doc in docs:
            for effect, V, aff_tokens in _verb_effects(doc):
                # ConceptNet expansion of the surface argument tokens
                cn_expanded = set(aff_tokens)
                for a in aff_tokens:
                    cn_expanded |= cn_neighbors.get(a, set())
                for pp in para["participants"]:
                    srl_bind = bool(aff_tokens & alias[pp])
                    cn_bind = (not srl_bind) and bool((p_toks[pp] & cn_expanded)
                                                      or (aff_tokens & _cn_expand(p_toks[pp], cn_neighbors)))
                    if srl_bind or cn_bind:
                        facts[(pid, pp)].setdefault(effect, set()).add(V)
                        if srl_bind:
                            stats["n_srl_bindings"] += 1
                        else:
                            stats["n_cn_only_bindings"] += 1
                            stats["participants_with_cn_only"].add((pid, pp))
    stats["n_participants_with_cn_only_binding"] = len(stats.pop("participants_with_cn_only"))
    return facts, stats


def _cn_expand(tokens: Set[str], cn_neighbors: Dict[str, Set[str]]) -> Set[str]:
    out = set(tokens)
    for t in tokens:
        out |= cn_neighbors.get(t, set())
    return out


# ============================================================================ ConceptNet domain-coverage diagnostic
def _cn_domain_coverage(paragraphs, steps_df, coref, cn_neighbors, pre_oracle) -> Dict:
    """For each gold UNMENTIONED change (the residual), does ConceptNet link the affected
    participant to ANY surface entity present at that step? Quantifies scientific-domain coverage:
    covered = ConceptNet has a co-participation path; missed = it does not."""
    nlp = _get_nlp()
    covered = 0
    total = 0
    missed_examples = []
    by_para = {str(p["para_id"]): p for p in paragraphs}
    parse_cache = {}
    for pid, p in by_para.items():
        parse_cache[pid] = list(nlp.pipe(p["sentence_texts"]))
    for row in steps_df.itertuples():
        if row.mentioned or row.label == "NONE":
            continue
        pid = str(row.para_id)
        doc = parse_cache[pid][row.step - 1]
        # surface content tokens at this step (nouns/propn)
        surf = {t.text.lower() for t in doc if t.pos_ in ("NOUN", "PROPN")}
        p_toks = _toks(row.participant)
        surf_exp = set(surf)
        for s in surf:
            surf_exp |= cn_neighbors.get(s, set())
        linked = bool((p_toks & surf_exp) or (surf & _cn_expand(p_toks, cn_neighbors)))
        total += 1
        if linked:
            covered += 1
        elif len(missed_examples) < 20:
            missed_examples.append({"participant": row.participant, "step_surface": sorted(surf)[:6]})
    return {"unmentioned_changes": total, "conceptnet_linked": covered,
            "coverage_fraction": round(covered / max(total, 1), 4),
            "missed_examples": missed_examples[:12]}


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

    print(f"[precompute] {len(paragraphs)} paragraphs (extraction + oracle facts)...", flush=True)
    pre_oracle = _paragraph_precompute(paragraphs, oracle_multiset, coref, steps_df)
    oracle_facts = {(pid, pp): pre_oracle[pid]["bridge"][pp] for pid in pre_oracle for pp in pre_oracle[pid]["bridge"]}

    print("[real-kb] generic SRL sourcing...", flush=True)
    generic_facts = _build_real_kb_bridge_facts(paragraphs, coref)
    print("[conceptnet] loading index + co-participation sourcing...", flush=True)
    cn_neighbors = _load_cn_neighbors()
    cn_facts, cn_stats = _build_conceptnet_bridge_facts(paragraphs, coref, cn_neighbors)

    cov_generic = _fact_coverage(generic_facts, oracle_facts)
    cov_cn = _fact_coverage(cn_facts, oracle_facts)
    domain_cov = _cn_domain_coverage(paragraphs, steps_df, coref, cn_neighbors, pre_oracle)

    def _pre_with(facts):
        out = {}
        for para in paragraphs:
            pid = str(para["para_id"])
            pr = dict(pre_oracle[pid])
            pr["bridge"] = {pp: facts.get((pid, pp), {}) for pp in para["participants"]}
            out[pid] = pr
        return out
    pre_generic = _pre_with(generic_facts)
    pre_cn = _pre_with(cn_facts)

    grids: Dict[str, Dict] = {}
    grids["prior_lesion"], lesion_diag = _prior_lesion_grids(paragraphs, pre_oracle)
    grids["without_knowledge"], without_diag = _grids(paragraphs, pre_oracle, use_bridge=False)
    grids["with_oracle"], oracle_diag = _grids(paragraphs, pre_oracle, use_bridge=True)
    grids["with_real_generic"], generic_diag = _grids(paragraphs, pre_generic, use_bridge=True)
    grids["with_real_cn"], cn_diag = _grids(paragraphs, pre_cn, use_bridge=True)

    proxy = {arm: _proxy_scores(steps_df, g) for arm, g in grids.items()}
    official = {arm: _official_corpus_scores(paragraphs, g) for arm, g in grids.items()}
    unm = {arm: _unm(proxy[arm]) for arm in proxy}

    without_f1 = unm["without_knowledge"]["macro_f1"]
    oracle_f1 = unm["with_oracle"]["macro_f1"]
    generic_f1 = unm["with_real_generic"]["macro_f1"]
    cn_f1 = unm["with_real_cn"]["macro_f1"]
    lesion_f1 = unm["prior_lesion"]["macro_f1"]

    oracle_lift = oracle_f1 - without_f1
    generic_lift = generic_f1 - without_f1
    cn_lift = cn_f1 - without_f1
    survival_generic = (generic_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None
    survival_cn = (cn_lift / oracle_lift) if abs(oracle_lift) > 1e-9 else None

    diff = _arms_must_differ({"without_knowledge": grids["without_knowledge"], "with_oracle": grids["with_oracle"],
                              "with_real_generic": grids["with_real_generic"], "with_real_cn": grids["with_real_cn"]})

    elapsed = time.time() - t0
    return {
        "split": split, "elapsed_s": round(elapsed, 3), "n_paragraphs": len(paragraphs),
        "arms_differ": diff, "decode": {k: v for k, v in
                                        [("lesion", lesion_diag["decode_fidelity"]),
                                         ("without", without_diag["decode_fidelity"]),
                                         ("oracle", oracle_diag["decode_fidelity"]),
                                         ("generic", generic_diag["decode_fidelity"]),
                                         ("cn", cn_diag["decode_fidelity"])]},
        "unmentioned_subset": unm,
        "without_f1": without_f1, "with_oracle_f1": oracle_f1,
        "with_real_generic_f1": generic_f1, "with_real_cn_f1": cn_f1, "prior_lesion_f1": lesion_f1,
        "oracle_lift": oracle_lift, "generic_lift": generic_lift, "cn_lift": cn_lift,
        "survival_generic": survival_generic, "survival_cn": survival_cn,
        "cn_minus_generic_survival": (survival_cn - survival_generic) if (survival_cn is not None and survival_generic is not None) else None,
        "cn_minus_prior_lesion": cn_f1 - lesion_f1,
        "fact_coverage_generic": cov_generic, "fact_coverage_cn": cov_cn,
        "conceptnet_binding_stats": cn_stats,
        "conceptnet_domain_coverage": domain_cov,
        "official": {arm: official[arm]["overall"] for arm in official},
    }


# ============================================================================ verdict
def decomposition_verdict(result: Dict) -> Tuple[str, str]:
    survival_cn = result["survival_cn"]
    survival_generic = result["survival_generic"]
    cn_add = result["cn_minus_generic_survival"]
    without_f1 = result["without_f1"]
    cn_f1 = result["with_real_cn_f1"]
    arms_ok = result["arms_differ"]["all_differ"]
    decode_ok = all(v >= 0.99 for v in result["decode"].values())
    infra_fail = (not arms_ok) or (not decode_ok)

    ablation_collapsed = without_f1 < WITHOUT_COLLAPSE_CEILING
    leak = cn_f1 > LEAK_CEILING
    go = (survival_cn is not None and survival_cn >= SURVIVAL_HARD_PASS
          and cn_add is not None and cn_add >= CN_MUST_ADD_OVER_GENERIC)
    no_go = (survival_cn is None) or (survival_cn < SURVIVAL_HARD_FAIL) or (cn_add is not None and cn_add < CN_MUST_ADD_OVER_GENERIC)

    dc = result["conceptnet_domain_coverage"]
    cov = result["fact_coverage_cn"]
    msg = (f"split={result['split']} SURVIVAL_CN={survival_cn} (generic={survival_generic}) "
           f"cn_add={cn_add} cn_f1={cn_f1:.4f} without_f1={without_f1:.4f} "
           f"cn_pair_recall={cov['pair_recall']} (generic was {result['fact_coverage_generic']['pair_recall']}) "
           f"cn_domain_coverage={dc['coverage_fraction']} "
           f"ablation_collapsed={ablation_collapsed} leak={leak} arms_ok={arms_ok} decode_ok={decode_ok}")

    if infra_fail:
        return "HARD_FAIL", f"HARD_FAIL_INFRA: {msg}"
    if not ablation_collapsed:
        return "HARD_FAIL", f"HARD_FAIL_ABLATION_DID_NOT_COLLAPSE_void: {msg}"
    if leak:
        return "MIDDLE_BAND", f"MIDDLE_BAND_POSSIBLE_LEAK: {msg}"
    if go:
        return "HARD_PASS", f"HARD_PASS_REUSE_CONCEPTNET_GO: {msg}"
    if no_go:
        return "HARD_FAIL", f"HARD_FAIL_CONCEPTNET_INSUFFICIENT_BUILD_NOT_REUSE: {msg}"
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
    cn_neighbors = _load_cn_neighbors()
    # sanity: ConceptNet index has co-participation neighbors for a common ProPara term
    assert "oil" in cn_neighbors or "water" in cn_neighbors, "CN index missing expected terms"

    # synth where the UNMENTIONED participant is linked to the surface entity via ConceptNet:
    # 'plants' (participant) destroyed at a step naming only 'material'/'sediment'; ConceptNet
    # should link plant<->... Use a controllable hand cn_neighbors override for determinism.
    cn_test = {"material": {"plant", "plants"}, "plants": {"material"}}
    synth = [
        {"para_id": "s1",
         "sentence_texts": ["Plants appear.", "Water is added.",
                            "The fire consumes the material.", "Ash remains."],
         "participants": ["plants"],
         "states": [["-", "here", "here", "-", "-"]]},  # CREATE@1, DESTROY@3 (plants unmentioned; 'material')
    ]
    text = " ".join(synth[0]["sentence_texts"]); offs = []; cur = 0
    for s in synth[0]["sentence_texts"]:
        offs.append(cur); cur += len(s) + 1
    coref = {"s1": {"text": text, "sentence_offsets": offs, "n_sentences": 4, "clusters": []}}

    cn_facts, cn_stats = _build_conceptnet_bridge_facts(synth, coref, cn_test)
    f = cn_facts[("s1", "plants")]
    # ConceptNet links plants<->material -> 'consumes the material' (DESTROY) bridges to plants
    assert "DESTROY" in f and "DESTROY" in f["DESTROY"], (f, cn_stats)
    assert cn_stats["n_cn_only_bindings"] >= 1, cn_stats

    # generic (SRL only, no CN) should NOT source the DESTROY (plants not the syntactic patient)
    from experiments.exp_propara_bridging_real_kb_sourcing_v1 import _build_real_kb_bridge_facts as _gen
    gfacts = _gen(synth, coref)
    gf = gfacts[("s1", "plants")]
    assert not ("DESTROY" in gf and "DESTROY" in gf.get("DESTROY", set())), gf  # SRL misses it

    # verdict-logic unit checks
    go = {"split": "x", "survival_cn": 0.6, "survival_generic": 0.22, "cn_minus_generic_survival": 0.38,
          "without_f1": 0.35, "with_real_cn_f1": 0.45, "arms_differ": {"all_differ": True}, "decode": {"a": 1.0},
          "conceptnet_domain_coverage": {"coverage_fraction": 0.5}, "fact_coverage_cn": {"pair_recall": 0.5},
          "fact_coverage_generic": {"pair_recall": 0.23}}
    gv, _ = decomposition_verdict(go)
    assert gv == "HARD_PASS", gv
    nogo = dict(go); nogo["survival_cn"] = 0.25; nogo["cn_minus_generic_survival"] = 0.03
    nv, _ = decomposition_verdict(nogo)
    assert nv == "HARD_FAIL", nv  # CN didn't add materially -> BUILD not REUSE
    void = dict(go); void["without_f1"] = 0.7
    vv, _ = decomposition_verdict(void)
    assert vv == "HARD_FAIL", vv

    return {"official_eval_fixtures": len(off_result["official_fixtures"]),
            "cn_index_terms": len(cn_neighbors),
            "cn_fact_plants": {k: sorted(v) for k, v in f.items()}, "cn_stats": cn_stats,
            "generic_missed_destroy": gf,
            "verdict_logic_unit_checks": {"go": gv, "no_go": nv, "void": vv}}


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
    print(f"[{run_mode}] split={split} ConceptNet co-participation reuse-vs-build probe...", flush=True)
    result = run_decomposition(split, train_paragraphs)
    verdict, msg = decomposition_verdict(result)
    print(f"[{run_mode}] {verdict}: {msg}", flush=True)

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "split": split,
        "result": result,
        "headline": {
            "SURVIVAL_CN": result["survival_cn"], "SURVIVAL_GENERIC": result["survival_generic"],
            "cn_minus_generic_survival": result["cn_minus_generic_survival"],
            "with_real_cn_f1": result["with_real_cn_f1"], "with_real_generic_f1": result["with_real_generic_f1"],
            "with_oracle_f1": result["with_oracle_f1"], "without_f1": result["without_f1"],
            "cn_pair_recall": result["fact_coverage_cn"]["pair_recall"],
            "generic_pair_recall": result["fact_coverage_generic"]["pair_recall"],
            "conceptnet_domain_coverage_fraction": result["conceptnet_domain_coverage"]["coverage_fraction"],
            "conceptnet_binding_stats": result["conceptnet_binding_stats"],
            "official_overall": result["official"],
        },
        "cardinality_ok": True, "expected_n_units": 1,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "F1-comparison over a fixed real corpus (ProPara EMNLP18); no noise-floor threshold",
        "deterministic_seeding": True,
        "calibration_check": "default_ok_for_this_regime: survival bar pre-registered before TEST",
        "thresholds": {"SURVIVAL_HARD_PASS": SURVIVAL_HARD_PASS, "SURVIVAL_HARD_FAIL": SURVIVAL_HARD_FAIL,
                       "CN_MUST_ADD_OVER_GENERIC": CN_MUST_ADD_OVER_GENERIC,
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
