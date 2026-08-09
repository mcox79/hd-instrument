"""exp_mcscript2_oracle_clustering_probe_v1 -- DECISIVE "was there enough chance /
was it fair" oracle-upper-bound diagnostic for the MCScript2.0 HARD_FAIL
(exp_mcscript2_real_benchmark_validation_v1, commit 5c1199f87: system commonsense
accuracy 0.5538 < text-overlap baseline 0.5859, root cause mechanistically
diagnosed as greedy CA3/DG keying over-merging TRAIN instances into 33 catch-all
items covering 195 true scenarios, mean item purity (majority_frac) = 0.1999).

Pre-reg: preregs/2026-08-09_mcscript2_oracle_clustering_probe_v1.md

WHAT (Q-A, the decisive number): hand the mechanism PERFECT clusters (group TRAIN
instances by their TRUE scenario label -- purity=1.0 by construction, 195 items)
and route DEV instances to their TRUE-scenario item (also oracle -- isolates the
MC-SCORING step alone, zero clustering/routing noise anywhere). Does BoW
context_vector grounding + cosine MC-scoring then beat the TEXT_OVERLAP baseline
(0.5859) on the commonsense DEV subset? ORACLE_BEATS_BASELINE => clustering is the
fixable blocker (DG-separation rescue worth it). ORACLE_LOSES => the whole
"cluster-and-score-against-prototype" approach is insufficient for this MC task
even with perfect clusters (rescue needs a different architecture).

WHAT (Q-B, representation fairness): under the SAME oracle clustering, do the
REAL FHRR script role-structure registers (hdlab.script_grain_acquisition_loop.
build_instance_register, TRIGGER/CONSEQUENT/AGENT/PATIENT bind-bundle -- the
situation_model_accumulate-family role-binding organ) add anything over the BoW
context_vector signal (Amendment 1's signal, what the landed HARD_FAIL actually
scored with) once clustering noise is removed? Candidate MC answers are short
spans (not multi-sentence narratives), so a NEW lenient single-clause extractor
(extract_answer_role_tuple, reusing extract_root_verb/extract_args from
hdlab.mcscript_extraction VERBATIM) is used answer-side; this granularity
mismatch is disclosed in the pre-reg BEFORE running, not discovered after.

WHAT (item forensics): deterministically REPRODUCE the landed real-arm system
(same TRAIN sort order, same precheck_a-calibrated novelty_thresh, same 5-pass
consolidation -- fully seedless/deterministic, must reproduce 0.5538 exactly as a
sanity gate) and log every DEV commonsense question's prediction so the cases
where SYSTEM lost but TEXT_OVERLAP won can be sampled and read verbatim.

CONTRACT (fixed by Director): reuse hdlab/mcscript_extraction.py +
exp_mcscript2_real_benchmark_validation_v1.py's Stage-2 MC scoring + baselines
VERBATIM -- only the clustering-construction step and MC-scoring representation
are swapped. This file imports those functions rather than reimplementing them.

# CELL-TEMPLATE MANDATORY (subset applied; this is a one-shot local diagnostic,
# not a queued/dispatched pipeline cell -- "Local." per Director, no push
# authorized):
# - except SystemExit: raise BEFORE except Exception (no bare except, no BaseException)
# - final_metrics_atomicity: tmp_replace (write_metrics os.replace, reused)
# - deterministic_seeding: hashlib-only (reused primitives), sorted(..., key=id)
#   iteration order throughout; no built-in hash(), no list(set())
# - start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
# - real_code_path_exercised: parse_mcscript_xml / CandidateGenerator /
#   extract_instance_tuple / extract_answer_role_tuple / build_instance_register /
#   ScriptLibrary.match_or_spawn (item-forensics reproduction only) all
#   constructed and called for real at self-test scale
# - all numbers in this file's comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@
#
# ASCII-only; no unicode; no emojis.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import platform
import re
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

from hdlab.grounding_acquisition_loop import context_vector, _cos, _bundle
from hdlab.script_grain_acquisition_loop import (
    build_instance_register, ScriptLibrary, ScriptTrace, _real2d,
    script_consolidation_pass,
)
from hdlab import bundling
from hdlab.cleanup_family import iterative_attractor  # noqa: F401 (real_code_path decl below)
from hdlab.mcscript_extraction import (
    parse_mcscript_xml, extract_instance_tuple, extract_root_verb, extract_args,
    self_test as extraction_self_test,
)
from hdlab.candidate_generator import CandidateGenerator

# Reuse the landed cell's own Stage-2 MC-scoring + baseline functions VERBATIM
# (import, do not reimplement -- per Director contract).
import experiments.exp_mcscript2_real_benchmark_validation_v1 as ORIG

ANCHOR_NAME = "mcscript2_oracle_clustering_probe_v1"

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "self_test" if _ARGS.self_test else ("smoke" if _ARGS.smoke else "full")

ORACLE_MARGIN = 0.02  # pre-registered non-trivial-beat margin (META_RULE_L style)
N_FORENSICS_SAMPLE = 20
MAX_PER_ITEM_FORENSICS = 2


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


# ---------------------------------------------------------------------------
# Answer-side lenient role extraction (NEW, this cell only; reuses
# extract_root_verb / extract_args from hdlab.mcscript_extraction VERBATIM)
# ---------------------------------------------------------------------------
_NOVERB = "NOVERB_PLACEHOLDER"
_NOAGENT = "NOAGENT_PLACEHOLDER"
_NOPATIENT = "NOPATIENT_PLACEHOLDER"


def _ordered_content_tokens(text: str) -> List[str]:
    """Order-preserving content-token list (rightmost = crude head-noun proxy for
    bare-NP answers with no verb structure). Reuses ORIG._STOPWORDS verbatim."""
    return [w for w in re.findall(r"[a-z']+", (text or "").lower())
            if w not in ORIG._STOPWORDS and len(w) > 2]


def extract_answer_role_tuple(text: str, gen: CandidateGenerator) -> Tuple[Tuple[str, str, str, str], Dict]:
    """Lenient single-clause extraction for short MC candidate answers (NOT
    multi-sentence narratives -- extract_instance_tuple's >=2-sentence gate would
    always return None on these). Treats the whole answer text as ONE sentence;
    falls back to constant role-placeholders + a rightmost-content-word head-noun
    proxy when no verbal/argument structure is found (the common case for bare-NP
    answers like "a beer" / "at the bar" -- disclosed in the pre-reg BEFORE this
    was run, not discovered after)."""
    text = (text or "").strip()
    toks = _ordered_content_tokens(text)
    head = toks[-1] if toks else None
    if not text:
        return (_NOVERB, _NOVERB, _NOAGENT, _NOPATIENT), {"mode": "empty_answer"}
    cr = gen.generate(text)
    rv = extract_root_verb(cr)
    if rv is not None:
        v_idx, lemma = rv
        subj_tok, obj_tok = extract_args(cr, v_idx, lemma)
        trigger = consequent = lemma
        agent = subj_tok if subj_tok else _NOAGENT
        patient = obj_tok if obj_tok else (head if head else _NOPATIENT)
        diag = {"mode": "verb_found", "lemma": lemma, "subj": subj_tok, "obj": obj_tok}
    else:
        trigger = consequent = _NOVERB
        agent = _NOAGENT
        patient = head if head else _NOPATIENT
        diag = {"mode": "no_verb_head_noun_fallback", "head": head}
    return (trigger, consequent, agent, patient), diag


def _fhrr_bundle(regs: List[torch.Tensor]) -> torch.Tensor:
    if len(regs) == 1:
        return regs[0]
    return bundling.bundle(torch.stack(regs, dim=0))


def _real2d_unit(v: torch.Tensor) -> np.ndarray:
    a = _real2d(v)
    n = float(np.linalg.norm(a))
    return a / n if n > 1e-9 else a


# ---------------------------------------------------------------------------
# Gold (oracle) library construction
# ---------------------------------------------------------------------------
def build_gold_prototypes(train_instances: List[Dict], gen: CandidateGenerator) -> Dict:
    """Group TRAIN instances by TRUE scenario (purity=1.0 by construction).
    Builds BOTH a BoW prototype (Amendment-1 signal, what the landed HARD_FAIL
    scored with) and an FHRR structural prototype (build_instance_register bundle
    over successfully-extracted traces) per scenario."""
    by_scenario: Dict[str, List[Dict]] = {}
    for inst in sorted(train_instances, key=lambda x: x["id"]):
        by_scenario.setdefault(inst["scenario"], []).append(inst)

    proto_bow: Dict[str, np.ndarray] = {}
    proto_fhrr: Dict[str, np.ndarray] = {}
    n_extract_ok, n_extract_fail = 0, 0
    scenarios_with_zero_structural = []
    for scen in sorted(by_scenario):
        insts = by_scenario[scen]
        bow_vecs = [context_vector(i["text"]) for i in insts]
        proto_bow[scen] = _bundle(bow_vecs) if len(bow_vecs) > 1 else bow_vecs[0]

        regs = []
        for i in insts:
            tup, diag = extract_instance_tuple(i["text"], gen)
            if tup is None:
                n_extract_fail += 1
                continue
            n_extract_ok += 1
            trigger, consequent, agent, patient = tup
            regs.append(build_instance_register(agent, patient, trigger, consequent))
        if regs:
            proto_fhrr[scen] = _real2d_unit(_fhrr_bundle(regs))
        else:
            scenarios_with_zero_structural.append(scen)

    return {
        "proto_bow": proto_bow, "proto_fhrr": proto_fhrr,
        "n_scenarios": len(by_scenario),
        "n_train_extract_ok": n_extract_ok, "n_train_extract_fail": n_extract_fail,
        "scenarios_with_zero_structural_extraction": scenarios_with_zero_structural,
    }


def _tiebreak_pick(answers: List[Dict], scores: List[float]) -> str:
    if scores[0] == scores[1]:
        return answers[0]["id"]
    return answers[0]["id"] if scores[0] > scores[1] else answers[1]["id"]


def eval_oracle_dev(dev_instances: List[Dict], proto_bow: Dict, proto_fhrr: Dict,
                    gen: CandidateGenerator) -> Dict:
    """Oracle-routed (DEV instance's own TRUE scenario label selects the
    TRAIN-only-built item, zero clustering/routing noise) MC evaluation under
    BOTH representations. Anti-circularity: DEV text is NEVER added to any
    prototype; only the ground-truth scenario LABEL routes the query."""
    correct_bow = defaultdict(int)
    correct_fhrr = defaultdict(int)
    total = defaultdict(int)
    n_fhrr_fallback = 0

    for inst in sorted(dev_instances, key=lambda x: x["id"]):
        scen = inst["scenario"]
        if scen not in proto_bow:
            raise AssertionError(
                f"DEV scenario {scen!r} has no TRAIN gold item -- anti-circularity/"
                f"data-assumption violated (expected: all DEV scenarios occur in TRAIN)")
        pb = proto_bow[scen]
        pf = proto_fhrr.get(scen)
        for q in sorted(inst["questions"], key=lambda x: x["id"]):
            qtype = q["type"]
            correct_id = next(a["id"] for a in q["answers"] if a["correct"])
            scores_bow = [_cos(context_vector(a["text"]), pb) for a in q["answers"]]
            pred_bow = _tiebreak_pick(q["answers"], scores_bow)
            if pf is not None:
                scores_fhrr = []
                for a in q["answers"]:
                    tup, _diag = extract_answer_role_tuple(a["text"], gen)
                    trigger, consequent, agent, patient = tup
                    reg = build_instance_register(agent, patient, trigger, consequent)
                    scores_fhrr.append(float(np.dot(_real2d_unit(reg), pf)))
                pred_fhrr = _tiebreak_pick(q["answers"], scores_fhrr)
            else:
                n_fhrr_fallback += 1
                pred_fhrr = q["answers"][0]["id"]
            total[qtype] += 1
            total["ALL"] += 1
            if pred_bow == correct_id:
                correct_bow[qtype] += 1
                correct_bow["ALL"] += 1
            if pred_fhrr == correct_id:
                correct_fhrr[qtype] += 1
                correct_fhrr["ALL"] += 1

    def _acc(c, t, qtype):
        return (c.get(qtype, 0) / t.get(qtype, 1)) if t.get(qtype, 0) else 0.0

    by_type = {}
    for qtype in ("commonsense", "text", "positive-merged", "ALL"):
        by_type[qtype] = {
            "oracle_bow_acc": _acc(correct_bow, total, qtype),
            "oracle_fhrr_acc": _acc(correct_fhrr, total, qtype),
            "n_questions": total.get(qtype, 0),
        }
    return {"by_type": by_type, "n_fhrr_fallback_to_neutral": n_fhrr_fallback,
            "coverage": 1.0}  # oracle routing -> every question is "covered" by construction


# ---------------------------------------------------------------------------
# Item forensics: deterministically reproduce the landed real-arm system
# ---------------------------------------------------------------------------
def _eval_covered_commonsense_three_ways(dev_instances: List[Dict], library: ScriptLibrary,
                                         novelty_thresh: float) -> Tuple[Dict, List[Dict]]:
    """SCORING-LOCUS measurement (anchor #1). On the COVERED commonsense subset
    (use_script True, identical gating to the landed cell -- does NOT change which
    questions are diverted), scores each question THREE ways and returns per-scoring
    covered accuracy:
      - covered_system_acc:        proto = item_context_prototype(matched CLUSTER)  [as-run]
      - covered_passage_own_acc:   proto = context_vector(THIS passage's OWN text)  [anchor #1]
      - covered_text_baseline_acc: text_overlap_decide(answers, narrative)          [baseline]
    passage-own proto is the exact vector precompute_dev_caches already builds
    (bow_register(inst.text) -> real part == context_vector(inst.text)); zero extra
    compute beyond re-scoring. Also returns the per-question records (final-pass
    library state, all qtypes) for item forensics."""
    item_ids, codebook, statuses = ORIG.build_query_codebook(library)
    cov_sys = cov_own = cov_txt = n_cov = 0
    records: List[Dict] = []
    for inst in sorted(dev_instances, key=lambda x: x["id"]):
        key = ORIG.bow_register(inst["text"])
        item_id, score, status = ORIG.query_best_match_cached(
            item_ids, codebook, statuses, key, temp=ORIG.ATTRACTOR_TEMP, max_steps=ORIG.ATTRACTOR_MAX_STEPS)
        use_script = (item_id is not None and status is not None
                     and status.startswith("GROUNDED") and score >= novelty_thresh)
        cluster_proto = ORIG.item_context_prototype(library.items[item_id]) if use_script else None
        passage_own_proto = ORIG._bow_np(key)  # this passage's OWN bag-of-words (anchor #1)
        for q in sorted(inst["questions"], key=lambda x: x["id"]):
            correct_id = next(a["id"] for a in q["answers"] if a["correct"])
            text_pred = ORIG.text_overlap_decide(q["answers"], inst["text"])
            sys_pred = ORIG.script_decide(q["answers"], cluster_proto) if use_script else text_pred
            own_pred = ORIG.script_decide(q["answers"], passage_own_proto) if use_script else text_pred
            records.append({"inst_id": inst["id"], "scenario": inst["scenario"], "narrative": inst["text"],
                            "q_id": q["id"], "q_text": q["text"], "qtype": q["type"],
                            "answers": q["answers"], "correct_id": correct_id,
                            "system_pred": sys_pred, "text_pred": text_pred,
                            "passage_own_pred": own_pred, "use_script": bool(use_script),
                            "matched_item_id": item_id, "match_score": round(float(score), 4)})
            if q["type"] == "commonsense" and use_script:
                n_cov += 1
                cov_sys += (sys_pred == correct_id)
                cov_own += (own_pred == correct_id)
                cov_txt += (text_pred == correct_id)
    covered = {
        "n_covered": n_cov,
        "covered_system_acc": round(cov_sys / n_cov, 4) if n_cov else 0.0,
        "covered_passage_own_acc": round(cov_own / n_cov, 4) if n_cov else 0.0,
        "covered_text_baseline_acc": round(cov_txt / n_cov, 4) if n_cov else 0.0,
    }
    return covered, records


def reproduce_real_system_with_logging(train_instances: List[Dict], dev_instances: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Bit-for-bit reproduction of the landed real-arm pipeline (fully
    deterministic/seedless): same TRAIN sort order, same precheck_a-calibrated
    novelty_thresh, same 5-pass script_consolidation_pass sequence. Evaluates the
    scoring-locus three-way covered accuracy AFTER EACH pass (anchor #1), and
    returns the final-pass per-DEV-question records for item forensics."""
    precheck_a = ORIG.precheck_a_keying_discriminates(train_instances)
    novelty_thresh = precheck_a["novelty_thresh_calibrated"]

    library = ScriptLibrary()
    for inst in sorted(train_instances, key=lambda x: x["id"]):
        reg = ORIG.bow_register(inst["text"])
        ctx = ORIG._bow_np(reg)
        library.match_or_spawn(reg, inst["id"], "NA", ctx, 0, true_type=inst["scenario"],
                               temp=ORIG.ATTRACTOR_TEMP, max_steps=ORIG.ATTRACTOR_MAX_STEPS,
                               novelty_thresh=novelty_thresh)

    scoring_locus_curve: List[Dict] = []
    records: List[Dict] = []
    total_cs = correct_sys_overall = correct_txt_overall = 0
    for pass_idx in range(1, ORIG.N_PASSES + 1):
        script_consolidation_pass(library, pass_idx, min_confirm=ORIG.MIN_CONFIRM,
                                  schema_thresh=ORIG.SCHEMA_THRESH, neutral_band=ORIG.NEUTRAL_BAND,
                                  patience_max=ORIG.PATIENCE_MAX, mdl_gate_fn=None,
                                  replay_budget_frac=ORIG.REPLAY_BUDGET_FRAC)
        covered, records = _eval_covered_commonsense_three_ways(dev_instances, library, novelty_thresh)
        covered["pass"] = pass_idx
        scoring_locus_curve.append(covered)
        print(f"[repro pass {pass_idx}/{ORIG.N_PASSES}] n_covered={covered['n_covered']} "
              f"covered_system={covered['covered_system_acc']:.4f} "
              f"covered_passage_own={covered['covered_passage_own_acc']:.4f} "
              f"covered_text_baseline={covered['covered_text_baseline_acc']:.4f}", flush=True)

    # overall commonsense system/text acc on final-pass records (sanity vs landed 0.5538)
    for r in records:
        if r["qtype"] == "commonsense":
            total_cs += 1
            correct_sys_overall += (r["system_pred"] == r["correct_id"])
            correct_txt_overall += (r["text_pred"] == r["correct_id"])

    sanity = {"reproduced_commonsense_system_acc": round(correct_sys_overall / total_cs, 4) if total_cs else 0.0,
             "reproduced_commonsense_text_acc": round(correct_txt_overall / total_cs, 4) if total_cs else 0.0,
             "novelty_thresh": novelty_thresh,
             "final_grounded": sum(1 for i in library.items.values() if i.status.startswith("GROUNDED")),
             "scoring_locus_curve": scoring_locus_curve}
    return records, sanity


def sample_forensics(records: List[Dict], n: int = N_FORENSICS_SAMPLE,
                     max_per_item: int = MAX_PER_ITEM_FORENSICS) -> List[Dict]:
    wrong = [r for r in records if r["qtype"] == "commonsense"
             and r["system_pred"] != r["correct_id"] and r["text_pred"] == r["correct_id"]]
    wrong.sort(key=lambda r: (str(r["matched_item_id"]), r["inst_id"], r["q_id"]))
    per_item_count: Dict = defaultdict(int)
    sample = []
    for r in wrong:
        if per_item_count[r["matched_item_id"]] >= max_per_item:
            continue
        sample.append(r)
        per_item_count[r["matched_item_id"]] += 1
        if len(sample) >= n:
            break
    return sample, len(wrong)


# ---------------------------------------------------------------------------
# Self-test (real code path, per exp_dev SCHEMA-VET F.1)
# ---------------------------------------------------------------------------
def self_test() -> Dict:
    extraction_result = extraction_self_test(str(ORIG.POS_CKPT), str(ORIG.ARC_CKPT))
    gen = CandidateGenerator.load(str(ORIG.POS_CKPT), str(ORIG.ARC_CKPT))

    # extract_answer_role_tuple: verb-bearing answer vs bare-NP answer.
    tup_v, diag_v = extract_answer_role_tuple("She fixed the lantern quickly.", gen)
    assert diag_v["mode"] == "verb_found", f"expected verb_found on a clausal answer: {diag_v}"
    tup_nv, diag_nv = extract_answer_role_tuple("a beer", gen)
    assert diag_nv["mode"] == "no_verb_head_noun_fallback", f"expected fallback on bare NP: {diag_nv}"
    assert tup_nv[3] == "beer", f"head-noun fallback must pick the content word: {tup_nv}"
    tup_empty, diag_empty = extract_answer_role_tuple("", gen)
    assert diag_empty["mode"] == "empty_answer"

    # tiny hand-built end-to-end pipeline.
    xml_train = _selftest_xml(n_scenarios=2, n_per_scenario=5, seed_tag="train")
    xml_dev = _selftest_xml(n_scenarios=2, n_per_scenario=2, seed_tag="dev")
    import tempfile
    fd1, p1 = tempfile.mkstemp(suffix=".xml")
    fd2, p2 = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd1, "w", encoding="utf-8") as f:
            f.write(xml_train)
        with os.fdopen(fd2, "w", encoding="utf-8") as f:
            f.write(xml_dev)
        train_inst = parse_mcscript_xml(p1)
        dev_inst = parse_mcscript_xml(p2)
    finally:
        os.remove(p1)
        os.remove(p2)

    gold = build_gold_prototypes(train_inst, gen)
    assert gold["n_scenarios"] == 2
    oracle_eval = eval_oracle_dev(dev_inst, gold["proto_bow"], gold["proto_fhrr"], gen)
    assert oracle_eval["by_type"]["ALL"]["n_questions"] == sum(len(i["questions"]) for i in dev_inst)
    assert oracle_eval["by_type"]["commonsense"]["oracle_bow_acc"] == 1.0, (
        "self-test corpus is trivially separable (2 disjoint scenarios); oracle BoW must saturate "
        f"at 1.0 on this toy case: {oracle_eval['by_type']['commonsense']}")

    records, sanity = reproduce_real_system_with_logging(train_inst, dev_inst)
    assert len(records) == sum(len(i["questions"]) for i in dev_inst)
    sample, n_wrong_total = sample_forensics(records, n=5)

    return {
        "extraction_self_test": extraction_result,
        "answer_role_tuple_verb_found": True, "answer_role_tuple_fallback_ok": True,
        "gold_prototypes_ok": True, "oracle_eval_saturates_on_toy_corpus": True,
        "real_system_reproduction_ok": True, "n_wrong_total_toy": n_wrong_total,
        "real_code_path_exercised": ["CandidateGenerator", "parse_mcscript_xml",
                                     "extract_instance_tuple", "extract_answer_role_tuple",
                                     "build_instance_register", "ScriptLibrary.match_or_spawn",
                                     "script_consolidation_pass"],
    }


def _selftest_xml(n_scenarios: int, n_per_scenario: int, seed_tag: str) -> str:
    scenarios = {
        "making eggs": (
            "I cracked the eggs into a bowl . I whisked them well . "
            "I poured the mixture into a hot pan . I cooked the eggs until done . I served the eggs on a plate .",
            [("What did they make?", "an omelette", "a sandwich", "commonsense")],
        ),
        "walking dog": (
            "I clipped the leash onto the dog . I walked the dog around the block . "
            "The dog sniffed at the grass . I picked up after the dog . I brought the dog back home .",
            [("What did they use?", "a leash", "a bicycle", "commonsense")],
        ),
    }
    names = list(scenarios.keys())[:n_scenarios]
    parts = ["<data>"]
    iid = 0
    for scen in names:
        base_text, qs = scenarios[scen]
        for k in range(n_per_scenario):
            q_parts = []
            for qi, (qtext, right, wrong, qtype) in enumerate(qs):
                q_parts.append(
                    f'<question id="{qi}" text="{qtext}" type="{qtype}">'
                    f'<answer correct="True" id="0" text="{right}" />'
                    f'<answer correct="False" id="1" text="{wrong}" /></question>')
            parts.append(
                f'<instance id="{seed_tag}_{iid}" scenario="{scen}">'
                f"<text>{base_text}</text><questions>{''.join(q_parts)}</questions></instance>")
            iid += 1
    parts.append("</data>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE, expected_n_units=1)

    if RUN_MODE == "self_test":
        result = self_test()
        write_metrics(output_dir, {
            "verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS: real code path exercised.",
            "summary": "self_test", "elapsed_s": round(time.perf_counter() - t0, 3),
            "run_mode": "self_test", "self_test_result": result,
        })
        print(json.dumps(result, indent=2, default=str), flush=True)
        return

    print(f"[main] run_mode={RUN_MODE} loading MCScript2.0 splits from {ORIG.DATA_DIR}", flush=True)
    train_all = ORIG.load_split("train")
    dev_all = ORIG.load_split("dev")
    print(f"[main] loaded train={len(train_all)} dev={len(dev_all)}", flush=True)

    if RUN_MODE == "smoke":
        scen_sorted = sorted({inst["scenario"] for inst in train_all})
        smoke_scenarios = set(scen_sorted[:15])
        train_instances = ORIG.restrict_to_scenarios(train_all, smoke_scenarios)
        dev_instances = ORIG.restrict_to_scenarios(dev_all, smoke_scenarios)
    else:
        train_instances = train_all
        dev_instances = dev_all
    print(f"[main] using train={len(train_instances)} dev={len(dev_instances)} "
          f"(n_scenarios={len({i['scenario'] for i in train_instances})})", flush=True)

    print("[main] loading CandidateGenerator (real front end)...", flush=True)
    gen = CandidateGenerator.load(str(ORIG.POS_CKPT), str(ORIG.ARC_CKPT))

    print("[main] Q-A/Q-B: building GOLD (oracle) prototypes over TRAIN...", flush=True)
    t_gold0 = time.perf_counter()
    gold = build_gold_prototypes(train_instances, gen)
    print(f"[main] gold prototypes built in {time.perf_counter()-t_gold0:.1f}s "
          f"(n_scenarios={gold['n_scenarios']} extract_ok={gold['n_train_extract_ok']} "
          f"extract_fail={gold['n_train_extract_fail']} "
          f"zero_structural_scenarios={len(gold['scenarios_with_zero_structural_extraction'])})",
          flush=True)

    print("[main] Q-A/Q-B: oracle-routed DEV MC scoring (BoW vs FHRR)...", flush=True)
    t_eval0 = time.perf_counter()
    oracle_eval = eval_oracle_dev(dev_instances, gold["proto_bow"], gold["proto_fhrr"], gen)
    print(f"[main] oracle eval done in {time.perf_counter()-t_eval0:.1f}s: "
          f"{json.dumps(oracle_eval['by_type']['commonsense'])}", flush=True)

    baselines = ORIG.baseline_accuracies(dev_instances, ORIG.compute_majority_answer_id(train_instances))
    baseline_cs = baselines["commonsense"]["text_overlap_acc"]

    oracle_bow_cs = oracle_eval["by_type"]["commonsense"]["oracle_bow_acc"]
    oracle_fhrr_cs = oracle_eval["by_type"]["commonsense"]["oracle_fhrr_acc"]
    qa_beats_baseline = oracle_bow_cs > baseline_cs + ORACLE_MARGIN
    qa_loses = oracle_bow_cs <= baseline_cs
    qa_verdict = ("ORACLE_BEATS_BASELINE" if qa_beats_baseline else
                  ("ORACLE_LOSES" if qa_loses else "MIDDLE_BAND_MARGINAL"))
    qb_fhrr_adds_value = oracle_fhrr_cs > oracle_bow_cs + ORACLE_MARGIN
    qb_verdict = "FHRR_ADDS_VALUE" if qb_fhrr_adds_value else "FHRR_NO_BETTER"

    print(f"[main] Q-A verdict={qa_verdict} oracle_bow_cs={oracle_bow_cs:.4f} "
          f"baseline_cs={baseline_cs:.4f}", flush=True)
    print(f"[main] Q-B verdict={qb_verdict} oracle_fhrr_cs={oracle_fhrr_cs:.4f} "
          f"oracle_bow_cs={oracle_bow_cs:.4f}", flush=True)

    print("[main] item forensics: reproducing landed real-arm system with logging...", flush=True)
    t_repro0 = time.perf_counter()
    records, sanity = reproduce_real_system_with_logging(train_instances, dev_instances)
    print(f"[main] real-system reproduction done in {time.perf_counter()-t_repro0:.1f}s: {sanity}",
          flush=True)
    sample, n_wrong_total = sample_forensics(records)
    print(f"[main] item forensics: {n_wrong_total} commonsense cases where SYSTEM lost but "
          f"TEXT_OVERLAP won; sampled {len(sample)} for manual read", flush=True)

    # ---- SCORING-LOCUS verdict (anchor #1): does passage-own close the gap? ----
    slc = sanity["scoring_locus_curve"]
    gap_closed = []  # per pass 2..5
    for cov in slc:
        if cov["pass"] < 2:
            continue
        gap = cov["covered_text_baseline_acc"] - cov["covered_system_acc"]
        frac = ((cov["covered_passage_own_acc"] - cov["covered_system_acc"]) / gap) if abs(gap) > 1e-9 else None
        gap_closed.append({"pass": cov["pass"], "gap": round(gap, 4),
                           "closed_frac": (round(frac, 4) if frac is not None else None),
                           "covered_system_acc": cov["covered_system_acc"],
                           "covered_passage_own_acc": cov["covered_passage_own_acc"],
                           "covered_text_baseline_acc": cov["covered_text_baseline_acc"]})
    fracs = [g["closed_frac"] for g in gap_closed if g["closed_frac"] is not None]
    if fracs and all(f >= 0.80 for f in fracs):
        scoring_locus_verdict = "SCORING_LOCUS_HARD_PASS"
    elif any((f is not None and f < 0.50) for f in [g["closed_frac"] for g in gap_closed]):
        scoring_locus_verdict = "SCORING_LOCUS_HARD_FAIL"
    else:
        scoring_locus_verdict = "SCORING_LOCUS_MIDDLE_BAND"
    print(f"[main] SCORING-LOCUS verdict={scoring_locus_verdict} gap_closed={gap_closed}", flush=True)

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",  # this cell answers a diagnostic question, not a HARD_PASS/FAIL gate
        "verdict_msg": (f"Q-A={qa_verdict} (oracle_bow_commonsense={oracle_bow_cs:.4f} vs "
                        f"baseline={baseline_cs:.4f}); Q-B={qb_verdict} "
                        f"(oracle_fhrr_commonsense={oracle_fhrr_cs:.4f} vs oracle_bow={oracle_bow_cs:.4f}); "
                        f"SCORING_LOCUS={scoring_locus_verdict}"),
        "summary": f"run_mode={RUN_MODE} n_train={len(train_instances)} n_dev={len(dev_instances)} "
                  f"qa={qa_verdict} qb={qb_verdict} scoring_locus={scoring_locus_verdict}",
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "run_mode": RUN_MODE,
        "q_a_oracle_upper_bound": {
            "verdict": qa_verdict, "margin_required": ORACLE_MARGIN,
            "oracle_bow_commonsense_acc": round(oracle_bow_cs, 4),
            "baseline_text_overlap_commonsense_acc": round(baseline_cs, 4),
            "as_run_system_commonsense_acc_CITED": 0.5538,
            "majority_floor_commonsense_acc_CITED": round(baselines["commonsense"]["majority_acc"], 4),
        },
        "q_b_representation_fairness": {
            "verdict": qb_verdict, "margin_required": ORACLE_MARGIN,
            "oracle_fhrr_commonsense_acc": round(oracle_fhrr_cs, 4),
            "oracle_bow_commonsense_acc": round(oracle_bow_cs, 4),
            "n_fhrr_fallback_to_neutral": oracle_eval["n_fhrr_fallback_to_neutral"],
            "n_scenarios_zero_structural_extraction": len(gold["scenarios_with_zero_structural_extraction"]),
            "n_train_extract_ok": gold["n_train_extract_ok"], "n_train_extract_fail": gold["n_train_extract_fail"],
        },
        "scoring_locus_anchor1": {
            "verdict": scoring_locus_verdict,
            "hard_pass_rule": "covered_passage_own closes >=80% of (covered_text_baseline - covered_system) at EVERY pass 2-5",
            "hard_fail_rule": "closes <50% at ANY pass 2-5",
            "per_pass_gap_closed": gap_closed,
            "full_scoring_locus_curve": slc,
        },
        "oracle_eval_full_by_type": oracle_eval["by_type"],
        "baselines": baselines,
        "gold_n_scenarios": gold["n_scenarios"],
        "item_forensics": {
            "n_commonsense_questions_total": sum(1 for r in records if r["qtype"] == "commonsense"),
            "n_wrong_system_right_baseline_total": n_wrong_total,
            "sanity_reproduced_commonsense_system_acc": sanity["reproduced_commonsense_system_acc"],
            "sanity_reproduced_commonsense_text_acc": sanity["reproduced_commonsense_text_acc"],
            "sanity_matches_landed_run": abs(sanity["reproduced_commonsense_system_acc"] - 0.5538) < 1e-3,
            "novelty_thresh": sanity["novelty_thresh"], "final_grounded": sanity["final_grounded"],
            "sample": sample,
        },
        "n_train_instances": len(train_instances), "n_dev_instances": len(dev_instances),
        "deterministic_seeding": True,
        "final_metrics_atomicity": "tmp_replace",
    }
    write_metrics(output_dir, metrics)
    print(f"[main] DONE elapsed_s={metrics['elapsed_s']}", flush=True)
    print(f"[main] {metrics['verdict_msg']}", flush=True)


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out_dir_for_crash, e)
        raise
