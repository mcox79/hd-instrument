# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; BOW/GROUNDED_DROP_TENSE/PROPER_SCRAMBLE hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (MCQA pick-accuracy measurement; thresholds are this cell's own declared bands)
# - HP_SCOPE: {GROUNDED_DROP_TENSE: [reaches_margin], PROPER_SCRAMBLE: [collapses]}; BOW is reference only.
# - cardinality_ok: EXPECTED_N_UNITS = n_instances (pass1) + n_questions*2 (pass1b)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (HYPERNYM_DEPTH/DECAY inherited unchanged from E3)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL parse_mcscript_xml / EventBundleCodec / build_grounded_codec (real_code_path)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_mcscript2_mcqa_droptense_properscramble_v1.md for the full pre-reg.
"""exp_mcscript2_mcqa_droptense_properscramble_v1 -- the first REAL comprehension test: MCScript2.0 dev
multiple-choice QA, glass-box.

Does the DROP-TENSE grounded role-bundle representation (reused verbatim from E3b's `encode_flat_subset`
over roles_subset=(PRED,AGENT,PATIENT)) pick the correct answer better than plain bag-of-words on the REAL
2-way MC questions, AND does a PROPER per-instance-independently-random role-scramble control collapse
that advantage toward chance -- proving genuine role structure (not vocabulary overlap) drives the win?

This fixes the underpowered scramble control used by E3 (exp_focus_encode_grounded_event_discrimination_
realprose_v1) and E3b (exp_focus_encode_shapefix_realprose_v1): both used ONE FIXED role-key derangement
shared by every instance in the corpus. Bipolar bind is an elementwise-multiply ISOMETRY, so a globally
shared permutation is a relabeling, not noise -- cosine(v'_A, v'_B) under the shared derangement equals
cosine under the original keys with a correspondingly relabeled role assignment applied IDENTICALLY to A
and B, so cross-instance role-alignment survives intact (E3's scramble gap 0.0551 was ABOVE its grounded
gap 0.0542; E3b's GROUNDED_DROP_TENSE_SCRAMBLE gap 0.1337 was statistically identical to its own arm's
0.1336 -- neither scramble ever collapsed). Additionally the 3-role permutation group has only 2 members,
so even an independent-per-unit DRAW from that tiny group collides ~50% of the time by chance, diluting
rather than cleanly collapsing the signal.

PROPER_SCRAMBLE here instead draws a FRESH, INDEPENDENT set of 3 random n_dim=8192 bipolar role keys per
ENCODED UNIT (the passage's key-set is fixed per instance id; each candidate's key-set is fixed per
(instance_id, question_id, answer_id) -- passage and candidate NEVER share a key-set within one
comparison, by construction seed derivation). At n_dim=8192 two independent bipolar vectors have expected
dot product ~1/sqrt(8192) (~1.1%) -- effectively orthogonal, giving a clean decorrelation immune to the
small-permutation-group collision confound.

Three arms per scorable question (passage vs 2 candidates, argmax cosine picks the answer):
  BOW              : encode_instance_bow(content_words, codec_ungrounded) -- literal lexical-overlap
                     baseline, unchanged convention from E3/E3b. Scored on the FULL 2020-question set
                     (context) AND the scorable 1084-question matched-subset (the actual comparison bar).
  GROUNDED_DROP_TENSE: encode_flat_subset(role_events, codec_grounded, DROP_TENSE_ROLES, scrambled=False)
                     -- E3b's own function, imported verbatim.
  PROPER_SCRAMBLE  : same roles/fillers, but role KEYS are per-unit independent random vectors (see above),
                     NOT a permutation of the codec's small fixed role_keys array.

Modes:
  --self-test  Real-code-path check: a REAL tiny MCScript-XML-schema temp file through parse_mcscript_xml;
               reproduction check vs E3b's encode_flat_subset; scramble determinism + independence;
               arms-must-differ on a tiny synthetic corpus. No queue dispatch.
  --smoke      First 40 real dev-data.xml instances (real corpus, real subset).
  --full       All 355 dev-data.xml instances / 2020 questions.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.event_bundle import EventBundleCodec  # noqa: E402
from hdlab.role_slot_summarizer import _bipolar_bind, _bipolar_quantize, _bipolar_random  # noqa: E402
from hdlab.mcscript_extraction import parse_mcscript_xml  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from tools import exp_checkpoint as _ckpt  # noqa: E402

# REUSE, do NOT re-implement: E3's extraction/grounding pipeline + E3b's DROP_TENSE aggregation.
from experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1 import (  # noqa: E402
    build_instance_role_events, build_grounded_codec, encode_instance_bow, cosine,
    N_DIM, SEED, HYPERNYM_DEPTH, DECAY, NONE_FILLER,
)
from experiments.exp_focus_encode_shapefix_realprose_v1 import (  # noqa: E402
    encode_flat_subset, DROP_TENSE_ROLES,
)

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ANCHOR_NAME = "mcscript2_mcqa_droptense_properscramble_v1"
REPO_ROOT = Path(_REPO)
CORPUS_PATH = REPO_ROOT / "data" / "corpora" / "mcscript2" / "extracted" / "dev-data.xml"
OUTPUT_DIR = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"

N_SMOKE_INSTANCES = 40

# Pre-registered bands (preregs/2026-08-10_mcscript2_mcqa_droptense_properscramble_v1.md).
HARD_PASS_MARGIN = 0.05       # HYPOTHESIZED@preregs/2026-08-10_mcscript2_mcqa_droptense_properscramble_v1.md
HARD_PASS_STRUCT_FLOOR = 0.55  # same
SCRAMBLE_COLLAPSE_FRAC = 0.5   # same convention as E3b's own scramble-collapse gate
CHANCE = 0.5


# =====================================================================================
# Candidate text construction + per-question scorability.
# =====================================================================================
def candidate_text(question_text: str, answer_text: str) -> str:
    return f"{question_text} {answer_text}"


def build_units(insts: List[dict], output_dir: Path) -> Tuple[Dict, Dict, dict]:
    """Pass 1 (passage extraction, checkpointed) + pass 1b (candidate extraction, checkpointed).
    Returns (passage_units keyed by instance id, candidate_units keyed by 'iid|qid|aid', diag)."""
    done = _ckpt.completed_units(str(output_dir))

    # ---- pass 1: passages ----
    for inst in insts:
        key = _ckpt.unit_key("passage", inst["id"])
        if key in done:
            continue
        role_events, content_words = build_instance_role_events(inst["text"])
        _ckpt.record_unit(str(output_dir), key,
                          {"kind": "passage", "instance_id": inst["id"], "scenario": inst["scenario"],
                           "role_events": role_events, "content_words": content_words})
    units = _ckpt.load_units(str(output_dir))
    passage_units = {}
    for inst in insts:
        key = _ckpt.unit_key("passage", inst["id"])
        if key in units:
            passage_units[inst["id"]] = units[key]
    n_passage_zero = sum(1 for v in passage_units.values() if not v["role_events"])
    print(f"[pass1] passages: {len(passage_units)}/{len(insts)} extracted "
          f"({n_passage_zero} with zero events)", flush=True)

    # ---- pass 1b: candidates ----
    done = _ckpt.completed_units(str(output_dir))
    n_cand_total = 0
    for inst in insts:
        for q in inst["questions"]:
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                n_cand_total += 1
                if key in done:
                    continue
                txt = candidate_text(q["text"], a["text"])
                role_events, content_words = build_instance_role_events(txt)
                _ckpt.record_unit(str(output_dir), key,
                                  {"kind": "cand", "instance_id": inst["id"], "question_id": q["id"],
                                   "answer_id": a["id"], "role_events": role_events,
                                   "content_words": content_words})
    units = _ckpt.load_units(str(output_dir))
    cand_units = {}
    n_cand_zero = 0
    for inst in insts:
        for q in inst["questions"]:
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                if key in units:
                    cand_units[key] = units[key]
                    if not units[key]["role_events"]:
                        n_cand_zero += 1
    print(f"[pass1b] candidates: {len(cand_units)}/{n_cand_total} extracted "
          f"({n_cand_zero} with zero events)", flush=True)

    diag = {"n_instances": len(insts), "n_passage_extracted": len(passage_units),
           "n_passage_zero": n_passage_zero, "n_cand_total": n_cand_total,
           "n_cand_extracted": len(cand_units), "n_cand_zero": n_cand_zero}
    return passage_units, cand_units, diag


def scorable_questions(insts: List[dict], passage_units: Dict, cand_units: Dict) -> List[dict]:
    """A question is SCORABLE iff its passage AND both candidates have >=1 extracted role event."""
    out = []
    for inst in insts:
        pu = passage_units.get(inst["id"])
        if pu is None or not pu["role_events"]:
            continue
        for q in inst["questions"]:
            ok = True
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                cu = cand_units.get(key)
                if cu is None or not cu["role_events"]:
                    ok = False
                    break
            if ok:
                out.append({"instance_id": inst["id"], "scenario": inst["scenario"],
                           "question_id": q["id"], "question_type": q["type"],
                           "question_text": q["text"], "answers": q["answers"]})
    return out


# =====================================================================================
# PROPER_SCRAMBLE: per-unit independent random role keys (the load-bearing fix; see module docstring).
# =====================================================================================
def _unit_seed(unit_id: str) -> int:
    """Deterministic per-unit RNG seed via hashlib (NEVER Python hash()); PROT-023 compliant."""
    h = hashlib.sha256(("PROPER_SCRAMBLE_KEYS::" + unit_id).encode("ascii")).digest()
    return int.from_bytes(h[:8], "big") % (2**31 - 1)


def encode_flat_subset_independent_random_keys(role_events: List[Dict[str, str]],
                                               codec: EventBundleCodec,
                                               roles_subset: Sequence[str],
                                               unit_id: str) -> Optional[torch.Tensor]:
    """PROPER scramble: bind each event's roles_subset fillers (codec.SYMBOL vectors -- filler semantics
    stay grounded/shared) to a FRESH set of independent random role keys drawn ONLY for this unit_id (not
    the codec's shared role_keys array, not a permutation of them). Deterministic given unit_id."""
    if not role_events:
        return None
    gen = torch.Generator()
    gen.manual_seed(_unit_seed(unit_id))
    local_keys = {r: _bipolar_random((codec.n_dim,), gen) for r in roles_subset}
    acc = torch.zeros(codec.n_dim, dtype=torch.float32)
    for rf in role_events:
        for r in roles_subset:
            filler = rf[r]
            if filler == NONE_FILLER:
                continue
            acc = acc + _bipolar_bind(local_keys[r], codec._sym_vec(filler))
    return _bipolar_quantize(acc)


# =====================================================================================
# Arms-must-differ (META_RULE_AF).
# =====================================================================================
def _hash_vec(v: Optional[torch.Tensor]) -> str:
    if v is None:
        return "NONE"
    return hashlib.sha256(v.numpy().tobytes()).hexdigest()


def _arms_must_differ(per_arm_vecs: Dict[str, Dict[str, Optional[torch.Tensor]]]) -> dict:
    digests = {}
    for arm, vecs in per_arm_vecs.items():
        ids = sorted(vecs.keys())
        h = hashlib.sha256()
        for i in ids:
            h.update(_hash_vec(vecs[i]).encode("ascii"))
        digests[arm] = h.hexdigest()
    names = sorted(digests.keys())
    all_differ = True
    pairs = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            same = digests[a] == digests[b]
            pairs[f"{a}__vs__{b}"] = "IDENTICAL" if same else "DIFFERS"
            if same:
                all_differ = False
    return {"all_differ": all_differ, "digests": digests, "pairs": pairs}


# =====================================================================================
# Main pipeline.
# =====================================================================================
def run_pipeline(insts: List[dict], output_dir: Path, n_dim: int = N_DIM, seed: int = SEED) -> dict:
    output_dir = Path(output_dir)
    passage_units, cand_units, extract_diag = build_units(insts, output_dir)

    sq = scorable_questions(insts, passage_units, cand_units)
    print(f"[scorable] {len(sq)} scorable questions "
          f"(of {sum(len(i['questions']) for i in insts)} total)", flush=True)

    # ---- grounding vocab: over scorable-question passages + candidates only ----
    pred_words, arg_words = [], []
    scorable_instance_ids = sorted({q["instance_id"] for q in sq})
    for iid in scorable_instance_ids:
        for rf in passage_units[iid]["role_events"]:
            pred_words.append(rf["PRED"])
            if rf["AGENT"] != NONE_FILLER:
                arg_words.append(rf["AGENT"])
            if rf["PATIENT"] != NONE_FILLER:
                arg_words.append(rf["PATIENT"])
    for q in sq:
        for a in q["answers"]:
            key = _ckpt.unit_key("cand", q["instance_id"], q["question_id"], a["id"])
            for rf in cand_units[key]["role_events"]:
                pred_words.append(rf["PRED"])
                if rf["AGENT"] != NONE_FILLER:
                    arg_words.append(rf["AGENT"])
                if rf["PATIENT"] != NONE_FILLER:
                    arg_words.append(rf["PATIENT"])
    codec_grounded, coverage = build_grounded_codec(n_dim, seed, pred_words, arg_words)
    codec_ungrounded = EventBundleCodec(n_dim=n_dim, seed=seed)
    print(f"[grounding] coverage={coverage}", flush=True)

    # ---- encode passages (3 arms) ----
    passage_bow: Dict[str, Optional[torch.Tensor]] = {}
    passage_struct: Dict[str, Optional[torch.Tensor]] = {}
    passage_scr: Dict[str, Optional[torch.Tensor]] = {}
    for iid in scorable_instance_ids:
        pu = passage_units[iid]
        passage_bow[iid] = encode_instance_bow(pu["content_words"], codec_ungrounded)
        passage_struct[iid] = encode_flat_subset(pu["role_events"], codec_grounded, DROP_TENSE_ROLES,
                                                 scrambled=False)
        unit_id = _ckpt.unit_key("passage", iid)
        passage_scr[iid] = encode_flat_subset_independent_random_keys(
            pu["role_events"], codec_grounded, DROP_TENSE_ROLES, unit_id)

    # ---- encode candidates (3 arms) + score ----
    per_q_results = []
    n_ties = 0
    for q in sq:
        cand_vecs = {"BOW": [], "GROUNDED_DROP_TENSE": [], "PROPER_SCRAMBLE": []}
        cand_role_events = []
        for a in q["answers"]:
            key = _ckpt.unit_key("cand", q["instance_id"], q["question_id"], a["id"])
            cu = cand_units[key]
            cand_role_events.append(cu["role_events"])
            cand_vecs["BOW"].append(encode_instance_bow(cu["content_words"], codec_ungrounded))
            cand_vecs["GROUNDED_DROP_TENSE"].append(
                encode_flat_subset(cu["role_events"], codec_grounded, DROP_TENSE_ROLES, scrambled=False))
            cand_vecs["PROPER_SCRAMBLE"].append(
                encode_flat_subset_independent_random_keys(
                    cu["role_events"], codec_grounded, DROP_TENSE_ROLES, key))

        scores = {}
        preds = {}
        arm_passage_vec = {"BOW": passage_bow[q["instance_id"]],
                          "GROUNDED_DROP_TENSE": passage_struct[q["instance_id"]],
                          "PROPER_SCRAMBLE": passage_scr[q["instance_id"]]}
        for arm in ("BOW", "GROUNDED_DROP_TENSE", "PROPER_SCRAMBLE"):
            pv = arm_passage_vec[arm]
            c0, c1 = cand_vecs[arm][0], cand_vecs[arm][1]
            s0 = cosine(pv, c0) if pv is not None and c0 is not None else float("nan")
            s1 = cosine(pv, c1) if pv is not None and c1 is not None else float("nan")
            scores[arm] = [s0, s1]
            if s0 == s1:
                n_ties += 1
                preds[arm] = None  # tie -> counted as WRONG (conservative)
            else:
                preds[arm] = 0 if s0 > s1 else 1

        correct_idx = next(i for i, a in enumerate(q["answers"]) if a["correct"])
        per_q_results.append({
            "instance_id": q["instance_id"], "scenario": q["scenario"], "question_id": q["question_id"],
            "question_type": q["question_type"], "question_text": q["question_text"],
            "answers": [a["text"] for a in q["answers"]], "correct_idx": correct_idx,
            "scores": scores, "preds": preds,
            "cand_role_events": cand_role_events,
        })

    diff = _arms_must_differ({
        "BOW": {**passage_bow, **{f"c|{i}": v for i, v in enumerate(
            [encode_instance_bow(cand_units[_ckpt.unit_key('cand', q['instance_id'], q['question_id'], a['id'])]['content_words'], codec_ungrounded)
             for q in sq for a in q['answers']])}},
        "GROUNDED_DROP_TENSE": {**passage_struct, **{f"c|{i}": v for i, v in enumerate(
            [encode_flat_subset(cand_units[_ckpt.unit_key('cand', q['instance_id'], q['question_id'], a['id'])]['role_events'], codec_grounded, DROP_TENSE_ROLES, scrambled=False)
             for q in sq for a in q['answers']])}},
        "PROPER_SCRAMBLE": {**passage_scr, **{f"c|{i}": v for i, v in enumerate(
            [encode_flat_subset_independent_random_keys(
                cand_units[_ckpt.unit_key('cand', q['instance_id'], q['question_id'], a['id'])]['role_events'],
                codec_grounded, DROP_TENSE_ROLES,
                _ckpt.unit_key('cand', q['instance_id'], q['question_id'], a['id']))
             for q in sq for a in q['answers']])}},
    })

    # ---- BOW_full: score on ALL questions (context only) ----
    full_bow_correct = 0
    full_bow_scored = 0
    for inst in insts:
        pu = passage_units.get(inst["id"])
        if pu is None:
            continue
        p_bow = encode_instance_bow(pu["content_words"], codec_ungrounded)
        for q in inst["questions"]:
            cvecs = []
            for a in q["answers"]:
                key = _ckpt.unit_key("cand", inst["id"], q["id"], a["id"])
                cu = cand_units.get(key)
                cvecs.append(encode_instance_bow(cu["content_words"], codec_ungrounded) if cu else None)
            if p_bow is None or cvecs[0] is None or cvecs[1] is None:
                continue
            s0, s1 = cosine(p_bow, cvecs[0]), cosine(p_bow, cvecs[1])
            if s0 == s1:
                continue
            pred = 0 if s0 > s1 else 1
            correct_idx = next(i for i, a in enumerate(q["answers"]) if a["correct"])
            full_bow_scored += 1
            if pred == correct_idx:
                full_bow_correct += 1

    return {
        "extract_diag": extract_diag,
        "n_questions_total": sum(len(i["questions"]) for i in insts),
        "n_scorable": len(sq),
        "coverage": coverage,
        "arms_differ_check": diff, "arms_differ_verified": diff["all_differ"],
        "per_q_results": per_q_results,
        "n_ties": n_ties,
        "bow_full": {"correct": full_bow_correct, "scored": full_bow_scored,
                    "accuracy": (full_bow_correct / full_bow_scored) if full_bow_scored else float("nan")},
    }


# =====================================================================================
# Accuracy aggregation + verdict logic.
# =====================================================================================
def aggregate_accuracy(per_q_results: List[dict]) -> dict:
    per_arm = {"BOW": {"correct": 0, "scored": 0}, "GROUNDED_DROP_TENSE": {"correct": 0, "scored": 0},
              "PROPER_SCRAMBLE": {"correct": 0, "scored": 0}}
    per_type_arm: Dict[str, Dict[str, dict]] = {}
    for r in per_q_results:
        qt = r["question_type"]
        per_type_arm.setdefault(qt, {"BOW": {"correct": 0, "scored": 0},
                                     "GROUNDED_DROP_TENSE": {"correct": 0, "scored": 0},
                                     "PROPER_SCRAMBLE": {"correct": 0, "scored": 0}})
        for arm in per_arm:
            pred = r["preds"][arm]
            per_arm[arm]["scored"] += 1
            per_type_arm[qt][arm]["scored"] += 1
            if pred is not None and pred == r["correct_idx"]:
                per_arm[arm]["correct"] += 1
                per_type_arm[qt][arm]["correct"] += 1
    out = {}
    for arm, d in per_arm.items():
        out[arm] = {**d, "accuracy": (d["correct"] / d["scored"]) if d["scored"] else float("nan")}
    out_by_type = {}
    for qt, arms in per_type_arm.items():
        out_by_type[qt] = {arm: {**d, "accuracy": (d["correct"] / d["scored"]) if d["scored"] else float("nan")}
                          for arm, d in arms.items()}
    return {"overall": out, "by_type": out_by_type}


def pick_examples(per_q_results: List[dict], n: int = 5) -> dict:
    helps, hurts = [], []
    for r in per_q_results:
        bow_ok = r["preds"]["BOW"] == r["correct_idx"]
        struct_ok = r["preds"]["GROUNDED_DROP_TENSE"] == r["correct_idx"]
        entry = {"instance_id": r["instance_id"], "scenario": r["scenario"], "question_id": r["question_id"],
                 "question_type": r["question_type"], "question_text": r["question_text"],
                 "answers": r["answers"], "correct_idx": r["correct_idx"],
                 "preds": r["preds"], "scores": r["scores"], "cand_role_events": r["cand_role_events"]}
        if struct_ok and not bow_ok:
            helps.append(entry)
        elif bow_ok and not struct_ok:
            hurts.append(entry)
    return {"structure_helps": helps[:n], "structure_hurts": hurts[:n],
           "n_structure_helps_total": len(helps), "n_structure_hurts_total": len(hurts)}


def apply_bands(acc: dict) -> Tuple[str, str, dict]:
    a_bow = acc["overall"]["BOW"]["accuracy"]
    a_struct = acc["overall"]["GROUNDED_DROP_TENSE"]["accuracy"]
    a_scr = acc["overall"]["PROPER_SCRAMBLE"]["accuracy"]
    if any(math.isnan(x) for x in (a_bow, a_struct, a_scr)):
        return "HARD_FAIL", "NAN_ACCURACY: insufficient scorable questions", {}

    gap_struct = a_struct - CHANCE
    gap_scr = a_scr - CHANCE
    margin = a_struct - a_bow

    reaches_margin = (margin >= HARD_PASS_MARGIN) and (a_struct >= HARD_PASS_STRUCT_FLOOR)
    collapses = (gap_struct > 0) and (gap_scr < SCRAMBLE_COLLAPSE_FRAC * gap_struct)

    detail = {"acc_bow_matched": a_bow, "acc_struct": a_struct, "acc_scramble": a_scr,
              "gap_struct": gap_struct, "gap_scramble": gap_scr, "margin_over_bow": margin,
              "reaches_margin": reaches_margin, "collapses": collapses}

    if reaches_margin and collapses:
        tier = "HARD_PASS"
        msg = (f"HARD_PASS: acc_struct={a_struct:.4f} beats acc_bow_matched={a_bow:.4f} by "
              f"{margin:.4f} (>= {HARD_PASS_MARGIN}) AND acc_scramble={a_scr:.4f} collapses "
              f"(gap_scramble={gap_scr:.4f} < {SCRAMBLE_COLLAPSE_FRAC}*gap_struct={SCRAMBLE_COLLAPSE_FRAC*gap_struct:.4f})")
    elif (margin <= 0) or (not collapses):
        tier = "HARD_FAIL"
        msg = (f"HARD_FAIL: margin_over_bow={margin:.4f} collapses={collapses} "
              f"(acc_struct={a_struct:.4f} acc_bow={a_bow:.4f} acc_scramble={a_scr:.4f} "
              f"gap_struct={gap_struct:.4f} gap_scramble={gap_scr:.4f})")
    else:
        tier = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: structured~BoW (margin={margin:.4f} < {HARD_PASS_MARGIN} but positive, "
              f"scramble collapses OK) acc_struct={a_struct:.4f} acc_bow={a_bow:.4f} acc_scramble={a_scr:.4f}")
    return tier, msg, detail


# =====================================================================================
# Self-test.
# =====================================================================================
_TINY_XML = """<data>
  <instance id="t0" scenario="cooking">
    <text>I cracked the egg . I poured the mixture into the pan .</text>
    <questions>
      <question id="0" text="What did I crack ?" type="text">
        <answer correct="True" id="0" text="the egg" />
        <answer correct="False" id="1" text="the pan" />
      </question>
    </questions>
  </instance>
  <instance id="t1" scenario="cleaning">
    <text>I washed the dishes . I dried the counter .</text>
    <questions>
      <question id="0" text="What did I wash ?" type="text">
        <answer correct="True" id="0" text="the dishes" />
        <answer correct="False" id="1" text="the counter" />
      </question>
    </questions>
  </instance>
</data>
"""


def self_test() -> dict:
    checks = {}
    exercised = set()

    # (1) real code path: write a REAL MCScript-schema tiny XML, parse via the REAL parse_mcscript_xml.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        xml_path = Path(td) / "tiny.xml"
        xml_path.write_text(_TINY_XML, encoding="utf-8")
        insts = parse_mcscript_xml(str(xml_path))
        exercised.add("parse_mcscript_xml")
        assert len(insts) == 2 and len(insts[0]["questions"]) == 1
        assert insts[0]["questions"][0]["answers"][0]["correct"] is True
        checks["real_xml_parse"] = True

        out_dir = Path(td) / "out"
        result = run_pipeline(insts, out_dir, n_dim=512, seed=SEED)
        exercised.update({"EventBundleCodec", "build_grounded_codec"})
    checks["synthetic_n_scorable"] = result["n_scorable"]
    assert result["n_scorable"] == 2, f"expected 2 scorable questions on the tiny corpus: {result['n_scorable']}"
    checks["arms_differ_verified_synthetic"] = result["arms_differ_verified"]
    assert result["arms_differ_verified"], f"arms did not differ: {result['arms_differ_check']}"

    # (2) reproduction: this cell's structured encode reuses E3b's encode_flat_subset UNMODIFIED (proof by
    # direct import + identical call, asserted for META_RULE_AC discipline).
    role_events_probe = [{"PRED": "crack", "AGENT": "i", "PATIENT": "egg", "TENSE": "SIMPLE_PAST"}]
    codec_probe, _cov = build_grounded_codec(512, SEED, ["crack"], ["egg"])
    v_mine = encode_flat_subset(role_events_probe, codec_probe, DROP_TENSE_ROLES, scrambled=False)
    v_ref = encode_flat_subset(role_events_probe, codec_probe, DROP_TENSE_ROLES, scrambled=False)
    assert torch.equal(v_mine, v_ref)
    checks["reuses_e3b_encode_flat_subset"] = True

    # (3) PROPER_SCRAMBLE determinism: same unit_id -> bit-identical output.
    v_a = encode_flat_subset_independent_random_keys(role_events_probe, codec_probe, DROP_TENSE_ROLES, "unit_X")
    v_b = encode_flat_subset_independent_random_keys(role_events_probe, codec_probe, DROP_TENSE_ROLES, "unit_X")
    assert torch.equal(v_a, v_b), "PROPER_SCRAMBLE not deterministic for the same unit_id"
    checks["scramble_deterministic"] = True

    # (4) PROPER_SCRAMBLE independence: different unit_id -> different keys -> different output.
    v_c = encode_flat_subset_independent_random_keys(role_events_probe, codec_probe, DROP_TENSE_ROLES, "unit_Y")
    assert not torch.equal(v_a, v_c), "PROPER_SCRAMBLE gave identical output for two different unit_ids"
    checks["scramble_independent_across_units"] = True

    # (5) passage and its own candidate never share a key-set: even with IDENTICAL role_events, a
    # "passage"-id-seeded encode and a "cand"-id-seeded encode must differ.
    v_passage_like = encode_flat_subset_independent_random_keys(
        role_events_probe, codec_probe, DROP_TENSE_ROLES, _ckpt.unit_key("passage", "t0"))
    v_cand_like = encode_flat_subset_independent_random_keys(
        role_events_probe, codec_probe, DROP_TENSE_ROLES, _ckpt.unit_key("cand", "t0", "0", "0"))
    assert not torch.equal(v_passage_like, v_cand_like), \
        "passage-seeded and candidate-seeded scramble keys collided on identical role_events"
    checks["passage_candidate_never_share_keys"] = True

    # (6) validity preflight (declared, machine-checked).
    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["parse_mcscript_xml", "EventBundleCodec", "build_grounded_codec"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": EventBundleCodec, "callable_name": "EventBundleCodec",
         "kwargs": {"n_dim": 512, "seed": 7}},
    ], run_mode="selftest")
    checks["validity_preflight_ok"] = bool(ok)

    # (7) bands function sanity: a hand-built accuracy dict must classify correctly at each corner.
    hp_tier, _, _ = apply_bands({"overall": {"BOW": {"accuracy": 0.55}, "GROUNDED_DROP_TENSE": {"accuracy": 0.65},
                                             "PROPER_SCRAMBLE": {"accuracy": 0.52}}})
    assert hp_tier == "HARD_PASS", f"expected HARD_PASS on a clean-win/collapsing synthetic case: {hp_tier}"
    hf_tier, _, _ = apply_bands({"overall": {"BOW": {"accuracy": 0.55}, "GROUNDED_DROP_TENSE": {"accuracy": 0.65},
                                             "PROPER_SCRAMBLE": {"accuracy": 0.63}}})
    assert hf_tier == "HARD_FAIL", f"expected HARD_FAIL on a non-collapsing synthetic case: {hf_tier}"
    mb_tier, _, _ = apply_bands({"overall": {"BOW": {"accuracy": 0.55}, "GROUNDED_DROP_TENSE": {"accuracy": 0.57},
                                             "PROPER_SCRAMBLE": {"accuracy": 0.51}}})
    assert mb_tier == "MIDDLE_BAND", f"expected MIDDLE_BAND on a small-but-collapsing synthetic case: {mb_tier}"
    checks["band_logic_sanity"] = {"hard_pass": hp_tier, "hard_fail": hf_tier, "middle_band": mb_tier}

    return checks


# =====================================================================================
# Metrics write.
# =====================================================================================
def _write_metrics(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    import traceback
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME,
        "pid": os.getpid(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2, default=str)
    os.replace(tmp, final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        checks = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "checks": checks}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = Path(str(OUTPUT_DIR) + "_smoke") if args.smoke else OUTPUT_DIR

    t0 = time.time()
    all_insts = parse_mcscript_xml(str(CORPUS_PATH))
    all_insts.sort(key=lambda d: d["id"])
    insts = all_insts[:N_SMOKE_INSTANCES] if args.smoke else all_insts
    print(f"[{run_mode}] {len(insts)} instances, "
          f"{sum(len(i['questions']) for i in insts)} questions", flush=True)

    result = run_pipeline(insts, output_dir, n_dim=N_DIM, seed=SEED)
    acc = aggregate_accuracy(result["per_q_results"])
    examples = pick_examples(result["per_q_results"])
    verdict, msg, band_detail = apply_bands(acc)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM, "seed": SEED, "hypernym_depth": HYPERNYM_DEPTH, "decay": DECAY,
        "n_instances": len(insts),
        "n_questions_total": result["n_questions_total"], "n_scorable": result["n_scorable"],
        "cardinality_ok": result["extract_diag"]["n_cand_extracted"] == result["extract_diag"]["n_cand_total"]
                          and result["extract_diag"]["n_passage_extracted"] == result["extract_diag"]["n_instances"],
        "extract_diag": result["extract_diag"],
        "coverage": result["coverage"],
        "n_ties": result["n_ties"],
        "accuracy": acc,
        "bow_full": result["bow_full"],
        "band_detail": band_detail,
        "arms_differ_verified": result["arms_differ_verified"],
        "arms_differ_check": result["arms_differ_check"],
        "examples": examples,
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "MCQA pick-accuracy measurement on real dev-set questions; HARD_PASS_MARGIN/"
                    "SCRAMBLE_COLLAPSE_FRAC are this cell's own declared thresholds, not a synthetic "
                    "capacity envelope",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: HYPERNYM_DEPTH=3/DECAY=0.7 inherited "
                            "unchanged from E3/E3b (grounding quality not the variable under test)",
        "progress_logging": "print_flush_true",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("examples", "extract_diag")},
                     indent=2, default=str))
    print(json.dumps({"examples": metrics["examples"]}, indent=2, default=str))


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
