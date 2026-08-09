"""exp_mcscript2_script_chain_predict_gap_fill_v1 -- ANCHOR #3, the decisive test of the
ONLY lever past the MCScript2.0 content-matching ceiling: does GENUINE SCRIPT-INFERENCE
(hdlab.sequence_memory.SequenceMatrix.chain_predict, seeded from a DEV passage's OWN
last-observed per-sentence event, queried against a TRAIN-only per-scenario-type
script-transition model) add signal beyond passage-own content-matching on the items
where passage-own content-matching does not confidently resolve?

Pre-reg: preregs/2026-08-09_mcscript2_script_chain_predict_gap_fill_v1.md

BACKGROUND (MEASURED, prior cells, not re-derived here):
  data/exp_mcscript2_oracle_clustering_probe_v1/metrics.json:
    oracle_bow_commonsense_acc=0.6180 (cluster-prototype BoW content-matching, oracle
      clusters) vs baseline text_overlap=0.5859  MEASURED@data/exp_mcscript2_oracle_
      clustering_probe_v1/metrics.json:q_a_oracle_upper_bound
    oracle_fhrr_commonsense_acc=0.5507 (script role-structure content-matching, oracle
      clusters) -- UNDER BoW, not over  MEASURED@data/exp_mcscript2_oracle_clustering_
      probe_v1/metrics.json:q_b_representation_fairness
    scoring_locus_anchor1: passage's-OWN-content scoring (no cluster at all) closes
      >=80% of the as-run system's gap vs baseline at every pass 2-5  MEASURED@data/
      exp_mcscript2_oracle_clustering_probe_v1/metrics.json:scoring_locus_anchor1
  Reading: content-matching (clustered-or-not, BoW-or-structure) caps around ~0.55-0.62
  on this corpus. This cell tests whether GENUINE SCRIPT INFERENCE (predicting the next
  narrative beat from a learned TRAIN-only transition model, not just matching existing
  content) can push past that ceiling on the specific items where content-matching alone
  is uninformative.

DESIGN (see pre-reg for full rationale):
  PRIMARY (passage-own content-matching, TRAIN-independent): candidate answer scored by
    cos(context_vector(answer_text), context_vector(passage_own_full_text)). Computed for
    EVERY commonsense DEV question (no coverage gating -- always available).
  FALLBACK (genuine script inference): one shared hdlab.sequence_memory.SequenceMatrix
    (n_dim=256) PER TRAIN scenario TYPE, built by bind_sequence-ing every TRAIN instance
    of that type's own per-SENTENCE context_vector sequence into the same shared matrix
    (accumulating a "typical transition" structure across many tellings -- the SAME
    shared-matrix-across-many-items pattern as exp_substrate_native_qa_hotpotqa_v1/v2's
    build_sequence_matrix_from_items). At DEV time: k_start = the DEV passage's OWN
    last-sentence event vector (read-only query; never bound into any TRAIN matrix);
    chain_predict(k_start, depth=1) (pre-registered PRIMARY fallback depth; depths 2-3
    logged as non-gating bonus diagnostics). Candidate scored by
    cos(context_vector(answer_text), predicted_vector).
  STAGED DECISION (Bower/Black/Turner "Partial Copy", never "Full Copy"): if the primary's
    |score_0 - score_1| >= PRIMARY_MARGIN_THRESH (0.02), primary decides, fallback is NEVER
    consulted. Only when primary does not confidently resolve (margin < threshold) is the
    fallback consulted; if the fallback ALSO ties, fall through to the primary's own
    (weak) argmax -- never invent a "no answer" state.
  Per-passage event representation: context_vector(sentence_text) (the SAME whole-narrative
    BoW bipolar-bundle primitive that already measured, in the sibling cells' Amendment 1,
    to dominate the FHRR (verb,subj,obj) structural representation on THIS corpus), applied
    per-sentence instead of per-passage. hdlab.situation_model_accumulate.AccumulateRegister
    is deliberately NOT used (wrong-shaped primitive -- order-agnostic entity bundling, not
    an ordered-transition model); hdlab.sequence_memory.SequenceMatrix IS the substrate's
    dedicated ordered-transition organ and is the architecturally correct choice.
  Scenario-type routing for the fallback is ORACLE (inst["scenario"], ground truth) --
    isolates chain-inference from the keying/clustering problem (a separate, already-
    identified concern, "anchor #4" in the parent hand-off), matching this cell's REUSE of
    "the oracle cell's DEV parser + commonsense-subset + baselines" per the Director's task.

MANDATORY CONTROLS:
  Anti-circularity: DEV instances are NEVER bound into any TRAIN type's SequenceMatrix;
    only queried read-only via chain_predict from their own last-observed event.
  SCRAMBLE: a second SequenceMatrix per type built from the SAME per-instance sentence
    vectors, but with each TRAIN instance's OWN sentence order permuted (hashlib-seeded on
    instance id, PROT-023/F.5-compliant, no built-in hash()) before binding -- same content
    distribution feeding S, destroyed within-instance adjacency. If REAL's residual-item
    fallback-accuracy edge-over-chance does not exceed SCRAMBLE's, the "signal" is not from
    genuine order/script structure.
  MANDATORY PRE-CHECK (flat=broken-experiment guard): precheck_chain_predict_toy() builds a
    hand-crafted 4-step coherent script (repeated 40x with small per-repeat noise) vs the
    SAME symbols in per-repeat hashlib-permuted order, and asserts chain_predict's real-order
    prediction is materially closer to the true next symbol than the scrambled-order
    prediction. Must PASS before any HARD-FAIL from the real corpus is trusted (else the
    verdict is downgraded to HARD_FAIL_UNTRUSTED_PRECHECK_FAILED).

PRE-REGISTERED BANDS (verbatim from pre-reg / Director's task):
  HARD-PASS: staged_accuracy - primary_only_accuracy >= +0.02 on full commonsense DEV, AND
    fallback_accuracy_on_residual (post-hoc diagnostic set: items where primary_pred !=
    correct) > 0.55, AND REAL residual-fallback edge-over-chance > SCRAMBLE's.
  HARD-FAIL: margin <= 0, OR fallback_accuracy_on_residual in [0.45, 0.55] (chance-level),
    OR REAL edge <= SCRAMBLE edge. Relabeled HARD_FAIL_UNTRUSTED_PRECHECK_FAILED if the
    mandatory pre-check did not fire+discriminate.
  MIDDLE_BAND: everything else.
  Honest scope: a HARD-FAIL means "script-inference gap-filling adds negligible signal over
    passage-grounded scoring on THIS corpus specifically" (TEXT_OVERLAP is unusually strong
    on this lexically-grounded corpus) -- NOT a general refutation of chain-based script
    inference (independent positive precedent: exp_substrate_native_qa_hotpotqa_v1/v2).

# CELL-TEMPLATE MANDATORY (subset applied; local decisive probe, no push authorized):
# - except SystemExit: raise BEFORE except Exception (no bare except, no BaseException)
# - final_metrics_atomicity: tmp_replace (+ per-arm partial checkpoints, resumable real/scramble)
# - deterministic_seeding: hashlib-only; sorted(..., key=id) iteration order; no hash(),
#   no list(set())
# - start_marker + crash_diagnostic + progress_logging (print(..., flush=True))
# - real_code_path_exercised: SequenceMatrix.bind_sequence / chain_predict / context_vector /
#   split_sentences all constructed and called for real at self-test scale
# - arms_differ_verified (real vs scramble arm results hashed distinct)
# - cardinality_ok: len(per_arm) == 2
# - crlb_n_a: cosine-scoring + chain-prediction cell; no argmax/top-k capacity ceiling applies
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
import hashlib
import json
import os
import platform
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

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)
from hdlab.grounding_acquisition_loop import context_vector, _cos, D as BOW_D
from hdlab.mcscript_extraction import split_sentences
from hdlab.sequence_memory import SequenceMatrix

# Reuse the landed real-benchmark cell's data-loading + baseline functions VERBATIM
# (import, do not reimplement -- per Director contract, same convention as the sibling
# exp_mcscript2_oracle_clustering_probe_v1.py cell).
import experiments.exp_mcscript2_real_benchmark_validation_v1 as ORIG

ANCHOR_NAME = "mcscript2_script_chain_predict_gap_fill_v1"

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "self_test" if _ARGS.self_test else ("smoke" if _ARGS.smoke else "full")

# ---------------------------------------------------------------------------
# Config (exp_dev autonomy per pre-reg; fixed constants, not tuned post-hoc)
# ---------------------------------------------------------------------------
CHAIN_DEPTH = 1                    # pre-registered PRIMARY fallback depth
CHAIN_DEPTH_EXTRA = [2, 3]         # non-gating bonus diagnostics
PRIMARY_MARGIN_THRESH = 0.02       # |score0-score1| < this on the primary => "unresolved"
MARGIN_HP = 0.02                   # staged - primary_only must clear this for HARD_PASS
RESIDUAL_ACC_HP = 0.55             # fallback_accuracy_on_residual must exceed this for HARD_PASS
RESIDUAL_CHANCE_LO = 0.45
RESIDUAL_CHANCE_HI = 0.55
N_FORENSICS_SAMPLE = 15


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
# Per-sentence event vectors (the passage's own script/situation model)
# ---------------------------------------------------------------------------
def sentence_event_vectors(text: str) -> List[np.ndarray]:
    """Every sentence's context_vector (BoW bipolar), in narrative order. This IS the
    per-passage event sequence the SequenceMatrix binds/queries -- reuses split_sentences
    (hdlab.mcscript_extraction) + context_vector (hdlab.grounding_acquisition_loop)
    verbatim; no new representation-learning code."""
    return [context_vector(s) for s in split_sentences(text)]


def _deterministic_perm(identity_tag: str, n: int) -> List[int]:
    """Hashlib-seeded deterministic permutation of range(n) (PROT-023/F.5 compliant --
    no built-in hash(), no list(set()) ordering)."""
    seed = int.from_bytes(
        hashlib.sha256(f"chainpredict_scramble_perm::{identity_tag}".encode()).digest()[:8],
        "big") % (2 ** 32)
    rng = np.random.default_rng(seed)
    return rng.permutation(n).tolist()


def build_type_sequence_matrices(
    train_instances: List[Dict], train_sent_vecs: Dict[str, List[np.ndarray]], *, scramble: bool
) -> Tuple[Dict[str, SequenceMatrix], Dict[str, int]]:
    """One shared SequenceMatrix per scenario TYPE, built by bind_sequence-ing every TRAIN
    instance of that type's own per-sentence vector sequence (REAL: narrative order;
    SCRAMBLE: hashlib-permuted order, same vectors) into the same shared matrix. Instances
    with <2 sentences contribute zero pairs (bind_sequence no-ops on length<2) but are not
    otherwise special-cased. Anti-circularity: only TRAIN instances are ever bound here."""
    by_type: Dict[str, SequenceMatrix] = {}
    pairs_bound: Dict[str, int] = defaultdict(int)
    for inst in sorted(train_instances, key=lambda x: x["id"]):
        scen = inst["scenario"]
        vecs = train_sent_vecs[inst["id"]]
        if len(vecs) < 2:
            continue
        if scramble:
            perm = _deterministic_perm(inst["id"], len(vecs))
            vecs = [vecs[i] for i in perm]
        sm = by_type.setdefault(scen, SequenceMatrix(n_dim=BOW_D))
        keys = torch.from_numpy(np.stack(vecs, axis=0).astype(np.float32))
        n_before = len(sm)
        sm.bind_sequence(keys)
        pairs_bound[scen] += (len(sm) - n_before)
    return by_type, dict(pairs_bound)


def chain_predict_scores(sm: Optional[SequenceMatrix], k_start: Optional[np.ndarray],
                         depth: int) -> Optional[List[np.ndarray]]:
    """chain_predict wrapper; returns list of predicted vectors [depth1, depth2, ...] as
    numpy float64 arrays, or None if there is nothing to predict from (no type matrix, no
    pairs bound, or DEV passage has zero sentences)."""
    if sm is None or k_start is None or len(sm) == 0:
        return None
    k0 = torch.from_numpy(k_start.astype(np.float32))
    preds = sm.chain_predict(k0, depth=depth, codebook=None)
    return [p.detach().cpu().numpy().astype(np.float64) for p in preds]


# ---------------------------------------------------------------------------
# MANDATORY pre-check: does chain_predict actually fire + discriminate?
# ---------------------------------------------------------------------------
def precheck_chain_predict_toy() -> Dict:
    """Hand-built 4-step coherent script A->B->C->D (distinct multi-word content-phrases,
    so context_vector gives 4 clean distinct BoW codes) repeated 40x with small per-repeat
    noise (many independent TRAIN-like tellings reinforcing a genuine transition signal --
    the SAME accumulation mechanism build_type_sequence_matrices uses) vs the SAME symbols
    in per-repeat hashlib-permuted order (SCRAMBLE). Asserts chain_predict(A, depth=1) on
    the REAL matrix is materially closer to true B than the SCRAMBLE matrix's prediction,
    at production n_dim=BOW_D. This is the mandatory gate: a real corpus HARD-FAIL is only
    trusted if this fires."""
    words = {"A": "kitchen stove area", "B": "bowl egg mixture",
             "C": "oven bake pan heat", "D": "plate serve table"}
    symvecs = {k: context_vector(v) for k, v in words.items()}
    order = ["A", "B", "C", "D"]
    n_repeats = 40
    sm_real = SequenceMatrix(n_dim=BOW_D)
    sm_scr = SequenceMatrix(n_dim=BOW_D)
    rng = np.random.default_rng(1234567)
    for r in range(n_repeats):
        noisy = [symvecs[k] + 0.05 * rng.standard_normal(BOW_D) for k in order]
        keys_real = torch.from_numpy(np.stack(noisy, axis=0).astype(np.float32))
        sm_real.bind_sequence(keys_real)
        perm = _deterministic_perm(f"toy_repeat_{r}", len(noisy))
        keys_scr = torch.from_numpy(np.stack([noisy[i] for i in perm], axis=0).astype(np.float32))
        sm_scr.bind_sequence(keys_scr)
    k_start = torch.from_numpy(symvecs["A"].astype(np.float32))
    pred_real = sm_real.chain_predict(k_start, depth=1)[0].detach().cpu().numpy()
    pred_scr = sm_scr.chain_predict(k_start, depth=1)[0].detach().cpu().numpy()
    cos_real_to_b = _cos(pred_real, symvecs["B"])
    cos_scr_to_b = _cos(pred_scr, symvecs["B"])
    fires = bool(cos_real_to_b > 0.30 and cos_real_to_b > cos_scr_to_b + 0.10)
    return {
        "cos_real_chain_predict_to_true_next": round(float(cos_real_to_b), 4),
        "cos_scramble_chain_predict_to_true_next": round(float(cos_scr_to_b), 4),
        "n_pairs_bound_real": len(sm_real), "n_pairs_bound_scramble": len(sm_scr),
        "n_repeats": n_repeats,
        "fires_and_discriminates": fires,
    }


# ---------------------------------------------------------------------------
# PRIMARY (passage-own content-matching) + staged decision
# ---------------------------------------------------------------------------
def build_commonsense_questions(dev_instances: List[Dict]) -> List[Dict]:
    """Flatten every commonsense-type DEV question into a per-question record (fields
    needed for scoring; arm-independent)."""
    out: List[Dict] = []
    for inst in sorted(dev_instances, key=lambda x: x["id"]):
        for q in sorted(inst["questions"], key=lambda x: x["id"]):
            if q["type"] != "commonsense":
                continue
            out.append({
                "inst_id": inst["id"], "scenario": inst["scenario"], "narrative": inst["text"],
                "q_id": q["id"], "q_text": q["text"], "answers": q["answers"],
                "correct_id": next(a["id"] for a in q["answers"] if a["correct"]),
            })
    return out


def compute_primary(questions: List[Dict]) -> None:
    """In-place: attach primary_scores/primary_margin/primary_pred/primary_correct/
    unresolved to every question. TRAIN-independent (passage's own text only)."""
    for qd in questions:
        narrative_vec = context_vector(qd["narrative"])
        scores = [_cos(context_vector(a["text"]), narrative_vec) for a in qd["answers"]]
        margin = abs(scores[0] - scores[1])
        pred = qd["answers"][0]["id"] if scores[0] >= scores[1] else qd["answers"][1]["id"]
        qd["primary_scores"] = [round(float(s), 4) for s in scores]
        qd["primary_margin"] = round(float(margin), 4)
        qd["primary_pred"] = pred
        qd["primary_correct"] = bool(pred == qd["correct_id"])
        qd["unresolved"] = bool(margin < PRIMARY_MARGIN_THRESH)


def compute_dev_last_event(dev_instances: List[Dict]) -> Dict[str, Optional[np.ndarray]]:
    """DEV passage's own last-observed sentence event vector (k_start for chain_predict).
    Arm-independent (depends only on the DEV passage's own text)."""
    out: Dict[str, Optional[np.ndarray]] = {}
    for inst in dev_instances:
        vecs = sentence_event_vectors(inst["text"])
        out[inst["id"]] = vecs[-1] if vecs else None
    return out


def compute_arm(questions: List[Dict], dev_last_event: Dict[str, Optional[np.ndarray]],
                type_matrices: Dict[str, SequenceMatrix]) -> Dict:
    """Per-arm (real or scramble) fallback scoring + staged decision over every commonsense
    DEV question. Returns aggregate stats + the full per-question records list."""
    recs: List[Dict] = []
    n_type_covered = 0
    for qd in questions:
        rec = dict(qd)
        sm = type_matrices.get(qd["scenario"])
        k_start = dev_last_event.get(qd["inst_id"])
        max_depth = max([CHAIN_DEPTH] + CHAIN_DEPTH_EXTRA)
        preds = chain_predict_scores(sm, k_start, depth=max_depth)
        extra_scores: Dict[str, List[float]] = {}
        if preds is not None:
            n_type_covered += 1
            fb_vec = preds[CHAIN_DEPTH - 1]
            fb_scores = [_cos(context_vector(a["text"]), fb_vec) for a in qd["answers"]]
            fb_pred = qd["answers"][0]["id"] if fb_scores[0] >= fb_scores[1] else qd["answers"][1]["id"]
            for d in CHAIN_DEPTH_EXTRA:
                if d <= len(preds):
                    v = preds[d - 1]
                    s = [_cos(context_vector(a["text"]), v) for a in qd["answers"]]
                    extra_scores[f"depth{d}"] = [round(float(x), 4) for x in s]
        else:
            fb_scores = [0.0, 0.0]
            fb_pred = qd["primary_pred"]  # nothing to predict from -> defer to primary's own pick
        rec["fallback_scores"] = [round(float(x), 4) for x in fb_scores]
        rec["fallback_pred"] = fb_pred
        rec["fallback_correct"] = bool(fb_pred == qd["correct_id"])
        rec["fallback_extra_depths"] = extra_scores
        rec["type_covered"] = bool(preds is not None)

        if not qd["unresolved"]:
            staged_pred = qd["primary_pred"]                    # confident primary: fallback never consulted
        elif fb_scores[0] == fb_scores[1]:
            staged_pred = qd["primary_pred"]                    # fallback also ties: fall through, never invent
        else:
            staged_pred = fb_pred
        rec["staged_pred"] = staged_pred
        rec["staged_correct"] = bool(staged_pred == qd["correct_id"])
        rec["fallback_recovered"] = bool((not qd["primary_correct"]) and rec["staged_correct"])
        recs.append(rec)

    n = len(recs)
    staged_acc = (sum(r["staged_correct"] for r in recs) / n) if n else 0.0
    unresolved_recs = [r for r in recs if r["unresolved"]]
    staged_acc_on_unresolved = (
        sum(r["staged_correct"] for r in unresolved_recs) / len(unresolved_recs)
        if unresolved_recs else None)
    residual_recs = [r for r in recs if not r["primary_correct"]]
    fallback_acc_on_residual = (
        sum(r["fallback_correct"] for r in residual_recs) / len(residual_recs)
        if residual_recs else None)

    return {
        "n_questions": n,
        "staged_accuracy": round(staged_acc, 4),
        "n_unresolved": len(unresolved_recs),
        "staged_accuracy_on_unresolved": (
            round(staged_acc_on_unresolved, 4) if staged_acc_on_unresolved is not None else None),
        "n_residual": len(residual_recs),
        "fallback_accuracy_on_residual": (
            round(fallback_acc_on_residual, 4) if fallback_acc_on_residual is not None else None),
        "type_coverage_frac": round(n_type_covered / n, 4) if n else 0.0,
        "records": recs,
    }


def forensics_sample(records: List[Dict], n: int = N_FORENSICS_SAMPLE) -> Tuple[List[Dict], int]:
    """Deterministic sample of residual (primary-wrong) items, verbatim narrative/question/
    answer text + every score/prediction, so it's directly readable in the report."""
    residual = [r for r in records if not r["primary_correct"]]
    residual_sorted = sorted(residual, key=lambda r: (r["inst_id"], r["q_id"]))
    sample = []
    for r in residual_sorted[:n]:
        sample.append({
            "inst_id": r["inst_id"], "scenario": r["scenario"], "narrative": r["narrative"],
            "q_text": r["q_text"],
            "answers": [{"id": a["id"], "text": a["text"], "correct": a["correct"]} for a in r["answers"]],
            "correct_id": r["correct_id"],
            "primary_scores": r["primary_scores"], "primary_margin": r["primary_margin"],
            "primary_pred": r["primary_pred"], "unresolved": r["unresolved"],
            "fallback_scores": r["fallback_scores"], "fallback_pred": r["fallback_pred"],
            "type_covered": r["type_covered"],
            "staged_pred": r["staged_pred"], "staged_correct": r["staged_correct"],
            "fallback_recovered": r["fallback_recovered"],
        })
    return sample, len(residual)


# ---------------------------------------------------------------------------
# Self-test (real code path, per exp_dev SCHEMA-VET F.1)
# ---------------------------------------------------------------------------
def _toy_instance(iid: str, scenario: str, text: str, qtext: str, right: str, wrong: str) -> Dict:
    return {"id": iid, "scenario": scenario, "text": text,
            "questions": [{"id": "q0", "text": qtext, "type": "commonsense",
                           "answers": [{"id": "0", "text": right, "correct": True},
                                      {"id": "1", "text": wrong, "correct": False}]}]}


def self_test() -> Dict:
    precheck = precheck_chain_predict_toy()
    assert precheck["fires_and_discriminates"], f"MANDATORY precheck FAILED: {precheck}"

    scen_a_text = ("I gathered the kitchen ingredients . I cracked the eggs into a bowl . "
                  "I whisked the mixture well . I heated the oven pan . I served the warm omelette .")
    scen_b_text = ("I clipped the leash onto the dog . I walked the dog around the block . "
                  "The dog sniffed at the grass . I picked up after the dog . I brought the dog back home .")
    train = [_toy_instance(f"train_a_{i}", "making eggs", scen_a_text, "What did they make?",
                           "an omelette", "a sandwich") for i in range(6)]
    train += [_toy_instance(f"train_b_{i}", "walking dog", scen_b_text, "What did they use?",
                            "a leash", "a bicycle") for i in range(6)]
    dev = [_toy_instance("dev_a_0", "making eggs", scen_a_text, "What did they make?",
                         "an omelette", "a sandwich"),
           _toy_instance("dev_b_0", "walking dog", scen_b_text, "What did they use?",
                        "a leash", "a bicycle")]

    train_sent_vecs = {inst["id"]: sentence_event_vectors(inst["text"]) for inst in train}
    real_types, real_pairs = build_type_sequence_matrices(train, train_sent_vecs, scramble=False)
    scr_types, scr_pairs = build_type_sequence_matrices(train, train_sent_vecs, scramble=True)
    assert set(real_types.keys()) == {"making eggs", "walking dog"}, real_types.keys()
    assert all(v > 0 for v in real_pairs.values()), f"expected nonzero pairs bound: {real_pairs}"

    dev_last_event = compute_dev_last_event(dev)
    questions = build_commonsense_questions(dev)
    assert len(questions) == 2
    compute_primary(questions)
    arm_real = compute_arm(questions, dev_last_event, real_types)
    arm_scr = compute_arm(questions, dev_last_event, scr_types)
    assert 0.0 <= arm_real["staged_accuracy"] <= 1.0
    assert 0.0 <= arm_scr["staged_accuracy"] <= 1.0
    sample, n_res = forensics_sample(arm_real["records"], n=5)

    return {
        "precheck_chain_predict_toy": precheck,
        "toy_types_built": sorted(real_types.keys()),
        "toy_pairs_bound_real": real_pairs, "toy_pairs_bound_scramble": scr_pairs,
        "toy_arm_real_staged_accuracy": arm_real["staged_accuracy"],
        "toy_arm_scramble_staged_accuracy": arm_scr["staged_accuracy"],
        "toy_n_residual": n_res,
        "real_code_path_exercised": ["SequenceMatrix.bind_sequence", "SequenceMatrix.chain_predict",
                                     "context_vector", "split_sentences",
                                     "build_type_sequence_matrices", "compute_arm"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.perf_counter()
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE, expected_n_units=2)

    if RUN_MODE == "self_test":
        result = self_test()
        write_metrics(output_dir, {
            "verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS: real code path exercised; precheck fires.",
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
        smoke_scenarios = set(scen_sorted[:20])
        train_instances = ORIG.restrict_to_scenarios(train_all, smoke_scenarios)
        dev_instances = ORIG.restrict_to_scenarios(dev_all, smoke_scenarios)
    else:
        train_instances = train_all
        dev_instances = dev_all
    print(f"[main] using train={len(train_instances)} dev={len(dev_instances)} "
          f"n_scenarios_train={len({i['scenario'] for i in train_instances})}", flush=True)

    print("[main] MANDATORY PRE-CHECK: chain_predict fires+discriminates on toy "
          "coherent-vs-scrambled sequence...", flush=True)
    precheck = precheck_chain_predict_toy()
    print(f"[main] precheck result: {precheck}", flush=True)

    print("[main] precomputing per-sentence event vectors (TRAIN)...", flush=True)
    t1 = time.perf_counter()
    train_sent_vecs = {inst["id"]: sentence_event_vectors(inst["text"]) for inst in train_instances}
    n_multisent_train = sum(1 for v in train_sent_vecs.values() if len(v) >= 2)
    print(f"[main] train_sent_vecs done in {time.perf_counter()-t1:.1f}s "
          f"({n_multisent_train}/{len(train_instances)} TRAIN instances have >=2 sentences)", flush=True)

    print("[main] precomputing DEV last-event vectors + commonsense questions + PRIMARY scores...",
          flush=True)
    dev_last_event = compute_dev_last_event(dev_instances)
    questions = build_commonsense_questions(dev_instances)
    compute_primary(questions)
    n_q = len(questions)
    primary_only_acc = (sum(q["primary_correct"] for q in questions) / n_q) if n_q else 0.0
    n_unresolved_total = sum(1 for q in questions if q["unresolved"])
    n_residual_total = sum(1 for q in questions if not q["primary_correct"])
    print(f"[main] n_commonsense_dev_questions={n_q} primary_only_acc={primary_only_acc:.4f} "
          f"n_unresolved={n_unresolved_total} n_residual(primary_wrong)={n_residual_total}", flush=True)

    baselines_all = ORIG.baseline_accuracies(dev_instances, ORIG.compute_majority_answer_id(train_instances))
    baseline_cs = baselines_all["commonsense"]["text_overlap_acc"]
    print(f"[main] TEXT_OVERLAP baseline commonsense acc={baseline_cs:.4f} (context only)", flush=True)

    seeds = ["real", "scramble"]
    done, remaining = resumable_seeds(seeds, output_dir, run_config={"run_mode": RUN_MODE})
    print(f"[ckpt] {len(done)} of {len(seeds)} arms already complete; running {remaining}", flush=True)
    for arm in remaining:
        scramble = (arm == "scramble")
        print(f"[main] building per-type SequenceMatrix (arm={arm})...", flush=True)
        t_arm0 = time.perf_counter()
        type_matrices, pairs_bound = build_type_sequence_matrices(
            train_instances, train_sent_vecs, scramble=scramble)
        n_types = len(type_matrices)
        mean_pairs = (sum(pairs_bound.values()) / n_types) if n_types else 0.0
        print(f"[main] arm={arm} built {n_types} type matrices, mean_pairs_bound={mean_pairs:.1f} "
              f"in {time.perf_counter()-t_arm0:.1f}s; scoring DEV commonsense questions...", flush=True)
        arm_result = compute_arm(questions, dev_last_event, type_matrices)
        arm_result.pop("records")  # not persisted in the partial; recomputed cheaply below for forensics
        payload = {"seed": arm, "run_mode": RUN_MODE, "n_types": n_types,
                  "mean_pairs_bound_per_type": round(mean_pairs, 2), **arm_result}
        write_partial(output_dir, arm, payload)
        print(f"[main] arm={arm} done: staged_accuracy={arm_result['staged_accuracy']:.4f} "
              f"n_unresolved={arm_result['n_unresolved']} "
              f"fallback_accuracy_on_residual={arm_result['fallback_accuracy_on_residual']}", flush=True)

    per_arm = aggregate_partials(output_dir, seeds, run_config={"run_mode": RUN_MODE})
    real_p = per_arm["real"]
    scramble_p = per_arm["scramble"]

    # Recompute the REAL arm's full per-question records for forensics sampling (cheap,
    # deterministic -- doubles as a determinism self-check against the (possibly earlier-run)
    # partial's aggregate numbers).
    print("[main] recomputing REAL arm records for forensics sampling (determinism check)...", flush=True)
    real_types_check, _ = build_type_sequence_matrices(train_instances, train_sent_vecs, scramble=False)
    real_arm_full = compute_arm(questions, dev_last_event, real_types_check)
    if abs(real_arm_full["staged_accuracy"] - real_p["staged_accuracy"]) > 1e-9:
        raise AssertionError(
            f"DETERMINISM BREACH: recomputed real arm staged_accuracy "
            f"{real_arm_full['staged_accuracy']} != partial's {real_p['staged_accuracy']}")
    sample, n_residual_check = forensics_sample(real_arm_full["records"], n=N_FORENSICS_SAMPLE)

    # arms_differ_verified (META_RULE_AF)
    h_real = hashlib.sha256(json.dumps(
        [real_p["staged_accuracy"], real_p["fallback_accuracy_on_residual"],
         real_p["n_unresolved"], real_p["mean_pairs_bound_per_type"]]).encode()).hexdigest()
    h_scramble = hashlib.sha256(json.dumps(
        [scramble_p["staged_accuracy"], scramble_p["fallback_accuracy_on_residual"],
         scramble_p["n_unresolved"], scramble_p["mean_pairs_bound_per_type"]]).encode()).hexdigest()
    arms_differ = h_real != h_scramble

    # ---- Headline verdict ----
    margin = round(real_p["staged_accuracy"] - primary_only_acc, 4)
    residual_acc_real = real_p["fallback_accuracy_on_residual"] if real_p["fallback_accuracy_on_residual"] is not None else 0.0
    residual_acc_scramble = scramble_p["fallback_accuracy_on_residual"] if scramble_p["fallback_accuracy_on_residual"] is not None else 0.0
    real_edge = round(residual_acc_real - 0.50, 4)
    scramble_edge = round(residual_acc_scramble - 0.50, 4)
    real_beats_scramble = real_edge > scramble_edge

    qualifies_pass = (margin >= MARGIN_HP and residual_acc_real > RESIDUAL_ACC_HP and real_beats_scramble)
    qualifies_fail = (margin <= 0.0
                      or (RESIDUAL_CHANCE_LO <= residual_acc_real <= RESIDUAL_CHANCE_HI)
                      or (not real_beats_scramble))
    if qualifies_pass:
        verdict = "HARD_PASS"
    elif qualifies_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    precheck_trusted = bool(precheck["fires_and_discriminates"])
    if verdict == "HARD_FAIL" and not precheck_trusted:
        verdict = "HARD_FAIL_UNTRUSTED_PRECHECK_FAILED"

    verdict_msg = (
        f"{verdict}: staged_accuracy={real_p['staged_accuracy']:.4f} vs "
        f"primary_only_accuracy={primary_only_acc:.4f} (margin={margin:+.4f}, need >={MARGIN_HP:+.4f}); "
        f"fallback_accuracy_on_residual(real)={residual_acc_real:.4f} "
        f"(need >{RESIDUAL_ACC_HP}, chance-band=[{RESIDUAL_CHANCE_LO},{RESIDUAL_CHANCE_HI}]); "
        f"real_edge={real_edge:+.4f} vs scramble_edge={scramble_edge:+.4f} "
        f"(real_beats_scramble={real_beats_scramble}); precheck_trusted={precheck_trusted}; "
        f"n_residual={real_p['n_residual']} n_unresolved={real_p['n_unresolved']}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"run_mode={RUN_MODE} n_train={len(train_instances)} n_dev={len(dev_instances)} "
                  f"n_commonsense_q={n_q} verdict={verdict}",
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "run_mode": RUN_MODE,
        "config": {"CHAIN_DEPTH": CHAIN_DEPTH, "CHAIN_DEPTH_EXTRA": CHAIN_DEPTH_EXTRA,
                  "PRIMARY_MARGIN_THRESH": PRIMARY_MARGIN_THRESH, "MARGIN_HP": MARGIN_HP,
                  "RESIDUAL_ACC_HP": RESIDUAL_ACC_HP,
                  "RESIDUAL_CHANCE_BAND": [RESIDUAL_CHANCE_LO, RESIDUAL_CHANCE_HI],
                  "BOW_D": BOW_D},
        "precheck_chain_predict_toy": precheck,
        "baselines": baselines_all,
        "primary_only_accuracy": round(primary_only_acc, 4),
        "n_commonsense_dev_questions": n_q,
        "n_unresolved_total": n_unresolved_total,
        "n_residual_total": n_residual_total,
        "headline": {
            "staged_accuracy_real": real_p["staged_accuracy"],
            "primary_only_accuracy": round(primary_only_acc, 4),
            "margin": margin,
            "fallback_accuracy_on_residual_real": residual_acc_real,
            "fallback_accuracy_on_residual_scramble": residual_acc_scramble,
            "real_edge_over_chance": real_edge,
            "scramble_edge_over_chance": scramble_edge,
            "real_beats_scramble": real_beats_scramble,
            "precheck_trusted": precheck_trusted,
        },
        "arms_differ_verified": arms_differ,
        "cardinality_ok": len(per_arm) == 2,
        "n_train_instances": len(train_instances), "n_dev_instances": len(dev_instances),
        "n_train_scenarios": len({i["scenario"] for i in train_instances}),
        "n_dev_scenarios": len({i["scenario"] for i in dev_instances}),
        "real_arm": real_p, "scramble_arm": scramble_p,
        "residual_item_forensics_sample": sample,
        "residual_item_forensics_n_total": n_residual_check,
        "determinism_check_passed": True,
        "deterministic_seeding": True,
        "crlb_n_a": "cosine-scoring + chain-prediction cell; no argmax/top-k capacity ceiling applies",
        "final_metrics_atomicity": "tmp_replace",
    }
    write_metrics(output_dir, metrics)
    print(f"[main] VERDICT={verdict}", flush=True)
    print(f"[main] {verdict_msg}", flush=True)


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
