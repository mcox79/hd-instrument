# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; 6-arm hash-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (cosine-gap discrimination measurement; band threshold is THIS RUN's own
#   re-measured BoW gap, not a capacity/noise-floor CRLB)
# - HP_SCOPE: {GROUNDED_DROP_TENSE: [reaches_bow, scramble_collapses], GROUNDED_CHUNKEDFOCUS: [same]}
#   BOW / FLAT_GROUNDED are RE-MEASURED reference (positive-control) arms, not gated.
# - cardinality_ok: EXPECTED_N_UNITS = len(sample) instances
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: adaptive_with_discriminator_gate (HYPERNYM_DEPTH/DECAY inherited unchanged from
#   E3; CAPACITY/FANOUT = hdlab.situation_focus.ChunkedFocus module defaults, fixed before running)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL ChunkedFocus / EventBundleCodec / build_grounded_codec (real_code_path)
# - progress_logging: print_flush_true
# See preregs/2026-08-10_focus_encode_shapefix_realprose_v1.md for the full pre-reg.
"""exp_focus_encode_shapefix_realprose_v1 -- E3b aggregation-shape-fix gate.

E3 (exp_focus_encode_grounded_event_discrimination_realprose_v1, HARD_FAIL) diagnosed that grounding
alone does not fix real-prose event discrimination: the flat multi-event bundle-SUM lets low-entropy
TENSE (SIMPLE_PAST = 60% of 994 events) dominate the accumulated bundle, so matched and wrong-pair
cosines land in a uniformly-high band with almost no separation (grounded gap 0.0542, scramble 0.0551 --
scramble does NOT collapse, meaning the structure carries no discriminative work).

This cell tests whether FIXING THE AGGREGATION SHAPE recovers discriminative power, REUSING (not
re-grounding) the exact same grounded fillers / extraction / sample from E3 by importing E3's own
functions directly. Two orthogonal shape-fixes, both re-measured against E3's own re-measured BOW and
FLAT_GROUNDED (== E3's GROUNDED_STRUCTURED) reference arms:

  BOW                          : unchanged from E3 (encode_instance_bow over codec_ungrounded).
  FLAT_GROUNDED                : unchanged from E3 (E3's GROUNDED_STRUCTURED, re-measured bit-identically).
  GROUNDED_DROP_TENSE          : flat bundle-SUM aggregation UNCHANGED, but TENSE excluded from each
                                  event's role-filler dict (PRED/AGENT/PATIENT only).
  GROUNDED_DROP_TENSE_SCRAMBLE : same 3-role pipeline, role<->filler binding destroyed via a derangement
                                  over the 3 active role keys.
  GROUNDED_CHUNKEDFOCUS        : per-event encoding UNCHANGED (all 4 roles), but the AGGREGATION OPERATOR
                                  is hdlab.situation_focus.ChunkedFocus (Cowan capacity=4, fanout=2
                                  bounded focus) instead of an unbounded flat sum.
  GROUNDED_CHUNKEDFOCUS_SCRAMBLE: same chunked pipeline, each pushed event vector uses E3's own 4-role
                                  scramble derangement before chunking.

Discriminator: identical to E3 -- matched-pair (same-scenario) mean cosine minus wrong-pair
(different-scenario) mean cosine, over all pairwise instance comparisons in the sample.

Success signal (per Director task contract): NOT primarily "beat BoW" (this is a BoW-favorable task --
topic content-words alone discriminate scenarios) but whether role-SCRAMBLE COLLAPSES under either
shape-fix -- proof the role structure, not vocabulary co-occurrence, is doing the discriminative work.

Modes:
  --self-test  Real-code-path check: tiny synthetic corpus through the full 6-arm pipeline; reproduces
               E3's own encode_instance_structured bit-for-bit; ChunkedFocus stays bounded; arms differ.
               No queue dispatch.
  --smoke      Small real MCScript2.0 sample (E3's SMOKE regime: <=15 instances, >=5 scenarios).
  --full       Full real MCScript2.0 sample (E3's FULL regime: <=60 instances, >=12 scenarios) + Gate D
               positive-control reproduction check against E3's own landed metrics.json.
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

from hdlab.event_bundle import EventBundleCodec, DEFAULT_ROLES  # noqa: E402
from hdlab.situation_focus import ChunkedFocus  # noqa: E402
from hdlab.role_slot_summarizer import _bipolar_quantize  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from tools import exp_checkpoint as _ckpt  # noqa: E402

# REUSE, do NOT re-ground: import E3's own extraction/grounding/measurement code directly so the
# 60-instance/15-scenario sample and the grounded symbol codebook are bit-identical to E3's, not a
# re-transcription.
from experiments.exp_focus_encode_grounded_event_discrimination_realprose_v1 import (  # noqa: E402
    build_instance_role_events, build_grounded_codec, select_sample,
    matched_wrong_gap, cosine, encode_instance_bow, encode_instance_structured,
    CORPUS_PATH, N_DIM, SEED, HYPERNYM_DEPTH, DECAY,
    N_SCENARIOS_FULL, MAX_PER_SCENARIO_FULL, N_SCENARIOS_SMOKE, MAX_PER_SCENARIO_SMOKE,
    NONE_FILLER,
)

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

ANCHOR_NAME = "focus_encode_shapefix_realprose_v1"
REPO_ROOT = Path(_REPO)
OUTPUT_DIR = REPO_ROOT / "data" / f"exp_{ANCHOR_NAME}"
E3_METRICS_PATH = (REPO_ROOT / "data" /
                   "exp_focus_encode_grounded_event_discrimination_realprose_v1" / "metrics.json")

DROP_TENSE_ROLES: Tuple[str, ...] = ("PRED", "AGENT", "PATIENT")
DROP_TENSE_PERM = [1, 2, 0]          # derangement over the 3 surviving role keys (0=PRED,1=AGENT,2=PATIENT)
FULL_SCRAMBLE_PERM = [1, 2, 3, 0]    # E3's own derangement over (PRED,AGENT,PATIENT,TENSE); reused as-is

CAPACITY = 4                         # Cowan ~4-chunk focus; hdlab.situation_focus.ChunkedFocus default
FANOUT = 2                           # hdlab.situation_focus.ChunkedFocus default

SCRAMBLE_COLLAPSE_FRAC = 0.5         # HARD_PASS gate: scramble_gap < 0.5 * arm_gap
POSITIVE_CONTROL_TOLERANCE = 0.005   # Gate D: FULL-only reproduction tolerance vs E3's own landed gaps

ARM_NAMES = ("BOW", "FLAT_GROUNDED", "GROUNDED_DROP_TENSE", "GROUNDED_DROP_TENSE_SCRAMBLE",
            "GROUNDED_CHUNKEDFOCUS", "GROUNDED_CHUNKEDFOCUS_SCRAMBLE")


# =====================================================================================
# Aggregation operators (the ONLY new mechanism this cell adds; extraction/grounding reused verbatim).
# =====================================================================================
def encode_flat_subset(role_events: List[Dict[str, str]], codec: EventBundleCodec,
                       roles_subset: Sequence[str], scrambled: bool = False,
                       perm: Optional[Sequence[int]] = None) -> Optional[torch.Tensor]:
    """Flat bundle-SUM aggregation over a ROLE SUBSET of each event (shape-fix A: drop-TENSE uses
    roles_subset=('PRED','AGENT','PATIENT'); passing the full DEFAULT_ROLES reproduces E3's
    FLAT_GROUNDED / encode_instance_structured exactly)."""
    if not role_events:
        return None
    acc = torch.zeros(codec.n_dim, dtype=torch.float32)
    for rf in role_events:
        rf_sub = {k: rf[k] for k in roles_subset}
        if scrambled:
            acc = acc + codec.encode_scrambled_event(rf_sub, perm)
        else:
            acc = acc + codec.encode_event(rf_sub)
    return _bipolar_quantize(acc)


def encode_chunkedfocus(role_events: List[Dict[str, str]], codec: EventBundleCodec,
                        capacity: int, fanout: int, seed: int, scrambled: bool = False,
                        perm: Optional[Sequence[int]] = None) -> Optional[torch.Tensor]:
    """Shape-fix B: capacity-limited chunked aggregation (Cowan-bounded focus) instead of an unbounded
    flat sum. Per-event encoding unchanged (all 4 roles); only the aggregation operator differs."""
    if not role_events:
        return None
    cf = ChunkedFocus(codec, capacity=capacity, fanout=fanout, seed=seed)
    for gidx, rf in enumerate(role_events):
        ev_vec = codec.encode_scrambled_event(rf, perm) if scrambled else codec.encode_event(rf)
        cf.push(ev_vec, gidx)
    return cf.focus_vec()


# =====================================================================================
# Arms-must-differ (META_RULE_AF), generalized to N arms.
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
# Main pipeline: pass 1 (extraction, checkpointed, IDENTICAL to E3) -> grounding table (IDENTICAL to
# E3) -> pass 2 (6-arm encode, NEW aggregation shapes).
# =====================================================================================
def run_pipeline(sample: List[dict], output_dir: Path, n_dim: int = N_DIM,
                 seed: int = SEED) -> dict:
    output_dir = Path(output_dir)
    scenario_by_id = {inst["id"]: inst["scenario"] for inst in sample}

    # ---- pass 1: extraction (checkpointed per instance; SAME extractor E3 uses) ----
    done = _ckpt.completed_units(str(output_dir))
    for inst in sample:
        key = _ckpt.unit_key("extract", inst["id"])
        if key in done:
            continue
        role_events, content_words = build_instance_role_events(inst["text"])
        _ckpt.record_unit(str(output_dir), key,
                          {"instance_id": inst["id"], "scenario": inst["scenario"],
                           "role_events": role_events, "content_words": content_words})
        print(f"[pass1] instance={inst['id']} scenario={inst['scenario']!r} "
              f"n_events={len(role_events)} n_content_words={len(content_words)}", flush=True)
    units = _ckpt.load_units(str(output_dir))
    extracted = {}
    for inst in sample:
        key = _ckpt.unit_key("extract", inst["id"])
        if key in units:
            extracted[inst["id"]] = units[key]

    n_extraction_miss = sum(1 for v in extracted.values() if not v["role_events"])
    print(f"[pass1] done: {len(extracted)}/{len(sample)} instances "
          f"({n_extraction_miss} with zero events)", flush=True)

    # ---- grounding table (IDENTICAL call to E3's build_grounded_codec: same vocab -> same codebook) ----
    pred_words, arg_words = [], []
    for v in extracted.values():
        for rf in v["role_events"]:
            pred_words.append(rf["PRED"])
            if rf["AGENT"] != NONE_FILLER:
                arg_words.append(rf["AGENT"])
            if rf["PATIENT"] != NONE_FILLER:
                arg_words.append(rf["PATIENT"])
    codec_grounded, coverage = build_grounded_codec(n_dim, seed, pred_words, arg_words)
    codec_ungrounded = EventBundleCodec(n_dim=n_dim, seed=seed)
    print(f"[grounding] coverage={coverage}", flush=True)

    # ---- pass 2: encode 6 arms per instance ----
    bow_vecs: Dict[str, Optional[torch.Tensor]] = {}
    flat_gnd_vecs: Dict[str, Optional[torch.Tensor]] = {}
    drop_tense_vecs: Dict[str, Optional[torch.Tensor]] = {}
    drop_tense_scr_vecs: Dict[str, Optional[torch.Tensor]] = {}
    chunked_vecs: Dict[str, Optional[torch.Tensor]] = {}
    chunked_scr_vecs: Dict[str, Optional[torch.Tensor]] = {}

    for iid, v in extracted.items():
        role_events = v["role_events"]
        bow_vecs[iid] = encode_instance_bow(v["content_words"], codec_ungrounded)
        flat_gnd_vecs[iid] = encode_instance_structured(role_events, codec_grounded, scrambled=False)
        drop_tense_vecs[iid] = encode_flat_subset(role_events, codec_grounded, DROP_TENSE_ROLES,
                                                  scrambled=False)
        drop_tense_scr_vecs[iid] = encode_flat_subset(role_events, codec_grounded, DROP_TENSE_ROLES,
                                                       scrambled=True, perm=DROP_TENSE_PERM)
        chunked_vecs[iid] = encode_chunkedfocus(role_events, codec_grounded, CAPACITY, FANOUT, seed,
                                                scrambled=False)
        chunked_scr_vecs[iid] = encode_chunkedfocus(role_events, codec_grounded, CAPACITY, FANOUT, seed,
                                                    scrambled=True, perm=FULL_SCRAMBLE_PERM)

    per_arm_vecs = {
        "BOW": bow_vecs, "FLAT_GROUNDED": flat_gnd_vecs,
        "GROUNDED_DROP_TENSE": drop_tense_vecs, "GROUNDED_DROP_TENSE_SCRAMBLE": drop_tense_scr_vecs,
        "GROUNDED_CHUNKEDFOCUS": chunked_vecs, "GROUNDED_CHUNKEDFOCUS_SCRAMBLE": chunked_scr_vecs,
    }

    # NaN/Inf defensive check (should never fire; bipolar quantize is always finite).
    for name, vecs in per_arm_vecs.items():
        for iid, vv in vecs.items():
            if vv is not None and not torch.isfinite(vv).all():
                raise RuntimeError(f"NON_FINITE_VECTOR arm={name} instance={iid}")

    gaps = {name: matched_wrong_gap(vecs, scenario_by_id) for name, vecs in per_arm_vecs.items()}
    diff = _arms_must_differ(per_arm_vecs)

    # concrete example passages: first matched-pair (same scenario) with events + cosines per arm.
    examples = []
    scn_groups: Dict[str, List[str]] = {}
    for iid, scn in scenario_by_id.items():
        if iid in extracted:
            scn_groups.setdefault(scn, []).append(iid)
    for scn in sorted(scn_groups):
        ids = sorted(scn_groups[scn])
        if len(ids) >= 2 and flat_gnd_vecs.get(ids[0]) is not None and flat_gnd_vecs.get(ids[1]) is not None:
            a, b = ids[0], ids[1]
            examples.append({
                "scenario": scn, "instance_a": a, "instance_b": b,
                "text_a_snippet": next(inst["text"] for inst in sample if inst["id"] == a)[:200],
                "text_b_snippet": next(inst["text"] for inst in sample if inst["id"] == b)[:200],
                "role_events_a": extracted[a]["role_events"][:3],
                "role_events_b": extracted[b]["role_events"][:3],
                "cos_bow": cosine(bow_vecs[a], bow_vecs[b]),
                "cos_flat_grounded": cosine(flat_gnd_vecs[a], flat_gnd_vecs[b]),
                "cos_drop_tense": cosine(drop_tense_vecs[a], drop_tense_vecs[b]),
                "cos_chunkedfocus": cosine(chunked_vecs[a], chunked_vecs[b]),
            })
        if len(examples) >= 3:
            break

    return {
        "n_sample": len(sample), "n_extracted": len(extracted),
        "n_extraction_miss": n_extraction_miss,
        "cardinality_ok": len(extracted) == len(sample),
        "coverage": coverage,
        "gaps": gaps,
        "arms_differ_check": diff, "arms_differ_verified": diff["all_differ"],
        "examples": examples,
    }


# =====================================================================================
# Verdict logic.
# =====================================================================================
def evaluate_shapefix_arm(gap_arm: float, gap_scramble_arm: float, bow_ref: float) -> dict:
    reaches_bow = gap_arm >= bow_ref
    collapses = (gap_arm > 0) and (gap_scramble_arm < SCRAMBLE_COLLAPSE_FRAC * gap_arm)
    if reaches_bow and collapses:
        tier = "HARD_PASS"
    elif reaches_bow or collapses:
        tier = "MIDDLE_BAND"
    else:
        tier = "HARD_FAIL"
    return {"tier": tier, "reaches_bow_parity": reaches_bow, "scramble_collapses": collapses,
           "gap_arm": gap_arm, "gap_scramble_arm": gap_scramble_arm, "bow_ref": bow_ref}


_TIER_ORDER = {"HARD_PASS": 2, "MIDDLE_BAND": 1, "HARD_FAIL": 0}


def apply_bands(result: dict, positive_control: Optional[dict] = None) -> Tuple[str, str, dict]:
    gaps = result["gaps"]
    if not result["cardinality_ok"]:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: extracted {result['n_extracted']}/{result['n_sample']}",
               {})
    if not result["arms_differ_verified"]:
        return "HARD_FAIL", f"ARMS_IDENTICAL: {result['arms_differ_check']['pairs']}", {}
    all_gap_vals = [g["gap"] for g in gaps.values()]
    if any(math.isnan(x) for x in all_gap_vals):
        return "HARD_FAIL", "NAN_GAP: insufficient matched or wrong pairs in sample", {}
    if positive_control is not None and not positive_control["ok"]:
        return "HARD_FAIL", f"POSITIVE_CONTROL_REPRODUCTION_MISMATCH: {positive_control}", {}

    bow_ref = gaps["BOW"]["gap"]
    per_arm_eval = {
        "GROUNDED_DROP_TENSE": evaluate_shapefix_arm(
            gaps["GROUNDED_DROP_TENSE"]["gap"], gaps["GROUNDED_DROP_TENSE_SCRAMBLE"]["gap"], bow_ref),
        "GROUNDED_CHUNKEDFOCUS": evaluate_shapefix_arm(
            gaps["GROUNDED_CHUNKEDFOCUS"]["gap"], gaps["GROUNDED_CHUNKEDFOCUS_SCRAMBLE"]["gap"], bow_ref),
    }
    best_name = max(per_arm_eval, key=lambda k: (_TIER_ORDER[per_arm_eval[k]["tier"]],
                                                  per_arm_eval[k]["gap_arm"]))
    best = per_arm_eval[best_name]
    overall = best["tier"]
    msg = (f"{overall}: best_arm={best_name} gap={best['gap_arm']:.4f} bow_ref={bow_ref:.4f} "
          f"reaches_bow={best['reaches_bow_parity']} scramble={best['gap_scramble_arm']:.4f} "
          f"collapses={best['scramble_collapses']} | all_arms={per_arm_eval}")
    return overall, msg, {"per_arm_eval": per_arm_eval, "best_arm": best_name}


# =====================================================================================
# Self-test.
# =====================================================================================
def self_test() -> dict:
    checks = {}
    exercised = set()

    synth = [
        {"id": "s0", "scenario": "cooking", "text": "I cracked the egg . I poured the mixture ."},
        {"id": "s1", "scenario": "cooking", "text": "She broke the egg . She stirred the batter ."},
        {"id": "s2", "scenario": "sports", "text": "He kicked the ball . He scored a goal ."},
        {"id": "s3", "scenario": "sports", "text": "They passed the ball . They won the match ."},
    ]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res = run_pipeline(synth, Path(td), n_dim=512, seed=SEED)
    exercised.update({"EventBundleCodec", "ChunkedFocus", "build_grounded_codec", "select_sample"})
    checks["synthetic_arms_differ"] = res["arms_differ_check"]
    assert res["arms_differ_verified"], f"arms did not differ on synthetic corpus: {res['arms_differ_check']}"
    checks["synthetic_cardinality_ok"] = res["cardinality_ok"]
    assert res["cardinality_ok"]

    # (1) reproduction: this cell's flat-4-role aggregation must be BIT-IDENTICAL to E3's own
    # encode_instance_structured on the SAME role_events (proves genuine reuse, not re-transcription).
    role_events_probe = [
        {"PRED": "crack", "AGENT": "i", "PATIENT": "egg", "TENSE": "SIMPLE_PAST"},
        {"PRED": "pour", "AGENT": "i", "PATIENT": "mixture", "TENSE": "SIMPLE_PAST"},
    ]
    codec_probe, _cov = build_grounded_codec(512, SEED, ["crack", "pour"], ["egg", "mixture"])
    v_mine = encode_flat_subset(role_events_probe, codec_probe, DEFAULT_ROLES, scrambled=False)
    v_e3 = encode_instance_structured(role_events_probe, codec_probe, scrambled=False)
    assert torch.equal(v_mine, v_e3), "flat-4-role aggregation NOT bit-identical to E3's encode_instance_structured"
    checks["flat_aggregation_reproduces_e3"] = True

    # (2) GROUNDED_DROP_TENSE must differ from FLAT_GROUNDED when TENSE actually varies.
    v_full = encode_flat_subset(role_events_probe, codec_probe, DEFAULT_ROLES, scrambled=False)
    v_drop = encode_flat_subset(role_events_probe, codec_probe, DROP_TENSE_ROLES, scrambled=False)
    assert not torch.equal(v_full, v_drop), "drop-TENSE vector identical to full-role vector"
    checks["drop_tense_differs_from_flat"] = True

    # (3) ChunkedFocus real construction: active buffer stays bounded past capacity (real code path).
    cf = ChunkedFocus(codec_probe, capacity=3, fanout=2, seed=SEED)
    for g in range(6):
        rf = {"PRED": "crack", "AGENT": "i", "PATIENT": f"item{g}", "TENSE": "SIMPLE_PAST"}
        cf.push(codec_probe.encode_event(rf), g)
        assert len(cf.active) <= cf.capacity, f"active grew past capacity at push {g}"
    fv = cf.focus_vec()
    assert torch.isfinite(fv).all() and fv.numel() == 512
    checks["chunkedfocus_bounded_and_finite"] = True

    # (4) substrate-signature + real-code-path preflight (declared, machine-checked).
    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["EventBundleCodec", "ChunkedFocus", "build_grounded_codec",
                                        "select_sample"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": ChunkedFocus, "callable_name": "ChunkedFocus",
         "kwargs": {"codec": None, "capacity": 4, "fanout": 2, "seed": 0}},
        {"kind": "substrate_signature", "callable_obj": EventBundleCodec, "callable_name": "EventBundleCodec",
         "kwargs": {"n_dim": 8192, "seed": 7}},
    ], run_mode="selftest")
    checks["validity_preflight_ok"] = bool(ok)

    # (5) E3 metrics.json is readable + the two reference numbers this cell relies on are present.
    e3_ref = load_e3_reference()
    assert e3_ref is not None, "E3 reference metrics.json not found; positive control cannot run"
    assert e3_ref["bow_gap"] > 0.10, f"E3 bow_gap suspiciously small: {e3_ref}"
    checks["e3_reference_readable"] = e3_ref

    return checks


def load_e3_reference() -> Optional[dict]:
    if not E3_METRICS_PATH.exists():
        return None
    with open(E3_METRICS_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    return {"bow_gap": d["gap_bow"]["gap"], "flat_grounded_gap": d["gap_grounded_structured"]["gap"]}


def check_positive_control(result: dict) -> dict:
    e3_ref = load_e3_reference()
    if e3_ref is None:
        return {"ok": False, "reason": "E3_METRICS_MISSING", "path": str(E3_METRICS_PATH)}
    bow_delta = abs(result["gaps"]["BOW"]["gap"] - e3_ref["bow_gap"])
    flat_delta = abs(result["gaps"]["FLAT_GROUNDED"]["gap"] - e3_ref["flat_grounded_gap"])
    ok = bow_delta <= POSITIVE_CONTROL_TOLERANCE and flat_delta <= POSITIVE_CONTROL_TOLERANCE
    return {"ok": ok, "e3_bow_gap": e3_ref["bow_gap"], "measured_bow_gap": result["gaps"]["BOW"]["gap"],
           "bow_delta": bow_delta, "e3_flat_grounded_gap": e3_ref["flat_grounded_gap"],
           "measured_flat_grounded_gap": result["gaps"]["FLAT_GROUNDED"]["gap"],
           "flat_delta": flat_delta, "tolerance": POSITIVE_CONTROL_TOLERANCE}


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
    n_scn = N_SCENARIOS_SMOKE if args.smoke else N_SCENARIOS_FULL
    max_per = MAX_PER_SCENARIO_SMOKE if args.smoke else MAX_PER_SCENARIO_FULL

    t0 = time.time()
    sample = select_sample(CORPUS_PATH, n_scn, max_per)
    n_scenarios_actual = len({inst["scenario"] for inst in sample})
    print(f"[{run_mode}] sample: {len(sample)} instances across {n_scenarios_actual} scenarios",
          flush=True)

    result = run_pipeline(sample, output_dir, n_dim=N_DIM, seed=SEED)

    positive_control = None
    if run_mode == "full":
        positive_control = check_positive_control(result)
        print(f"[full] positive_control={positive_control}", flush=True)

    verdict, msg, verdict_detail = apply_bands(result, positive_control)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": f"{verdict}: {msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_dim": N_DIM, "seed": SEED, "hypernym_depth": HYPERNYM_DEPTH, "decay": DECAY,
        "capacity": CAPACITY, "fanout": FANOUT,
        "n_scenarios_actual": n_scenarios_actual,
        "expected_n_units": len(sample), "cardinality_ok": result["cardinality_ok"],
        "n_extracted": result["n_extracted"], "n_extraction_miss": result["n_extraction_miss"],
        "coverage": result["coverage"],
        "gaps": result["gaps"],
        "positive_control": positive_control,
        "verdict_detail": verdict_detail,
        "arms_differ_verified": result["arms_differ_verified"],
        "arms_differ_check": result["arms_differ_check"],
        "examples": result["examples"],
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "cosine-gap discrimination measurement on real narrative text; band threshold is "
                    "this run's own re-measured BoW gap (self-referential per task contract), not a "
                    "synthetic capacity envelope",
        "deterministic_seeding": True,
        "calibration_check": "adaptive_with_discriminator_gate: HYPERNYM_DEPTH=3/DECAY=0.7 inherited "
                            "unchanged from E3; CAPACITY=4/FANOUT=2 are ChunkedFocus module defaults, "
                            "fixed before running",
        "progress_logging": "print_flush_true",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("examples",)},
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
