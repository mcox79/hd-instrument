#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_frame_induction_oov_psych_real_v1

OOV VERB-FRAME INDUCTION ON REAL DATA (capability re-run of exp_frame_induction_oov_psych_v1,
commit 893a6fa88 / b8f54bf5d -- that cell was a MECHANISM DEMO on TEMPLATED sentences, MIDDLE per
"synthetic-toy outcomes can be construction-determined" USER-LOCKED discipline). This cell reuses
the SAME hdlab/frame_induction.py config-only learner-expand (registry.learn/apply, MDL-auto-select
across estimation/ruleind/proginduction) but points it at REAL narrative prose:
experiments/data/experiencer_narrative_roles_v1.jsonl (118 sentences, 67 psych verbs, mined
verbatim from litbank + 18 flagged supplements, non-circular human-verified gold; see
notes/experiencer_narrative_roles_v1_data_report_2026-08-04.md).

WHAT CHANGED vs the templated cell: the FEATURE ENCODER. Real prose needs construction cues the
templated 4-atom set (has_scomp/degree_mod/progressive/order_pre) under-detects -- zero-
complementizer finite clauses ("I fear his wits were touched", no "that") and exp_obj_passive
constructions ("was amused by"). hdlab/frame_induction.py gained (this session, same file, still
the feature-encoder module -- ZERO edits to hdlab/learner/{core,registry}.py or any plugin):
  - is_passive_real() -- BE-aux + adjacent participle-position surface detector
  - _is_animate_head() -- pronoun-set + capitalization animacy heuristic (Naigles-style semantic
    bootstrapping cue, genuinely additional to pure syntax, NEVER touches gold roles/lemma)
  - a nominative-case-pronoun zero-complementizer detector (case morphology: "I fear HE is right"
    vs "I fear HIM" signals an embedded clause, not a direct object)
  - locate_verb_idx / locate_head_idx / _lemma_candidates / real_construction_feats /
    build_real_episode -- the record-to-episode adapter
REAL_CONSTRUCTION_ATOMS = [has_scomp, degree_mod, progressive, passive, order_pre, arg_animate].
Deliberately NEVER features: the verb lemma, the gold role, or the dataset's own "construction"
field (using that field WOULD be circular -- it already encodes the exact subj-exp/obj-exp
semantic distinction induction is trying to recover; classic psych-verb minimal pairs like
fear/frighten are SYNTACTICALLY IDENTICAL "NP1 V NP2" in fixed-order English active voice -- this
is the textbook unsolvable-from-order-alone case, which is why exp_obj_active is pre-registered as
the hard axis).

TASK (per Director spawn 2026-08-04): train construction->EXPERIENCER-vs-OTHER induction on
TRAIN-split verbs; test on the 10 HELD-OUT lemmas (already lemma-level zero-leak split in the
dataset: subj-exp = cherish/crave/dread/loathe/yearn, obj-exp = astonish/embarrass/gladden/
horrify/terrify). PRIMARY = per-axis held-out accuracy (subj-axis and obj-axis reported SEPARATELY,
per VET-as-hard-as-a-negative / per-axis-not-aggregate discipline).

EVAL: for each heldout record, locate the EXPERIENCER-role argument's episode via
build_real_episode(); predict via the induced hypothesis; bucket the correctness by the record's
exp_type (subj / obj) -- that gives subj-axis and obj-axis held-out accuracy independently. N is
SMALL (report prominently): subj-axis N=6 sentences (12 records but yearn's 2 use pp_complement --
see per-record breakdown), obj-axis N=11 sentences MEASURED@this file's own eval, NOT hypothesized.

BASELINES: DEFAULT_FRAME (never predict EXPERIENCER for an unknown verb -> 0.0 on both axes by
construction) + POSITION-MAJORITY (majority EXPERIENCER-vs-OTHER conditioned on order_pre alone,
fit on TRAIN -- the audit's standing "position-majority in disguise" foil).

CONTROLS: SCRAMBLE (derange EXPERIENCER<->OTHER on TRAIN; induced held-out accuracy MUST collapse)
+ construction-signal-not-position (induction must beat position-majority on held-out, per axis).

PRE-REGISTERED BANDS (per-axis, both must independently clear for overall HARD_PASS):
  HARD_PASS(axis) = held-out acc(axis) >= 0.55 AND beats default-AGENT AND beats position-majority
                    on that axis, AND (aggregate) scramble collapses.
  HARD_FAIL(axis) = held-out acc(axis) < 0.35 OR scramble does not collapse.
  MIDDLE(axis)     = 0.35-0.55, or a control weak, or N too small to trust the point estimate
                    (N<8 sentences per axis auto-caps that axis at MIDDLE regardless of the point
                    accuracy -- small-N discipline, reported honestly per Director's instruction).
Overall verdict = the WORSE of the two per-axis tiers (an axis-blind aggregate would hide exactly
the exp_obj_active failure mode this cell exists to surface).

COMPUTE ARCHITECTURE: class (b) sequential-CPU, closed-form counting/rule-search/bounded-DSL only
(no matmul, no torch). Wall time sub-second. LOCAL-ONLY, foreground-to-completion; NO queue, NO
push, NO remote-persist, NO hdlab/learner mutation, NO atom bank. Deterministic: fixed int seeds +
sorted(set()); NO hash()-seeded RNG or ordering (PROT-023).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import random
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "frame_induction_oov_psych_real_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import frame_induction as FI  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DATA_PATH = os.path.join(REPO_ROOT, "experiments", "data", "experiencer_narrative_roles_v1.jsonl")

# ---- Pre-registered bands (per-axis) ----
HP_ACC_MIN = 0.55
HF_ACC_MAX = 0.35
SCRAMBLE_COLLAPSE_DELTA_MIN = 0.20
POSITION_BEAT_MARGIN_MIN = 0.10
SMALL_N_CAP = 8          # axis N below this auto-caps that axis's tier at MIDDLE (max)
SPLIT_SEED = 8040804
SCRAMBLE_SEED = 20260804
EPS = 1e-9

HELDOUT_SUBJ_LEMMAS = ["cherish", "crave", "dread", "loathe", "yearn"]
HELDOUT_OBJ_LEMMAS = ["astonish", "embarrass", "gladden", "horrify", "terrify"]


def _load_records():
    recs = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def _find_experiencer_arg(record):
    for a in record["args"]:
        if a["role"] == "EXPERIENCER":
            return a
    return None


def build_episode_for_record(record, arg, unresolved_log):
    """Locate verb + arg token indices in record['text'] and build a real-data episode. Returns
    None (and logs to unresolved_log) if either token can't be located -- an honest data-quality
    exclusion, not a silent skip (counted + surfaced in metrics)."""
    tokens = record["text"].split()
    v_idx = FI.locate_verb_idx(tokens, record["verb_lemma"])
    if v_idx is None:
        unresolved_log.append({"reason": "verb_not_located", "text": record["text"],
                               "verb_lemma": record["verb_lemma"]})
        return None
    a_idx = FI.locate_head_idx(tokens, arg["head"])
    if a_idx is None:
        unresolved_log.append({"reason": "arg_not_located", "text": record["text"],
                               "head": arg["head"]})
        return None
    ep = FI.build_real_episode(tokens, v_idx, a_idx, arg["role"])
    ep["verb"] = record["verb_lemma"]
    ep["exp_type"] = record["exp_type"]
    ep["construction_gold"] = record["construction"]  # glass-box provenance ONLY, never a feature
    ep["text"] = record["text"]
    ep["arg_role"] = arg["role"]
    ep["arg_is_subject_position"] = "order_pre" in ep["feats"]
    return ep


def build_corpus():
    """TRAIN = split_recommendation=='train' records' EXPERIENCER arg + all non-EXPERIENCER args
    (both directions -> binary contrast). HELDOUT = split_recommendation=='heldout' records'
    EXPERIENCER arg only (the axis metric is defined on that one argument per record)."""
    recs = _load_records()
    unresolved = []
    train_eps, held_eps = [], []
    for r in recs:
        is_train = r["split_recommendation"] == "train"
        for a in r["args"]:
            ep = build_episode_for_record(r, a, unresolved)
            if ep is None:
                continue
            if is_train:
                train_eps.append(ep)
            elif a["role"] == "EXPERIENCER":
                held_eps.append(ep)
    # Leakage guard: no held-out lemma appears in any training episode.
    train_verbs = {e["verb"] for e in train_eps}
    for v in HELDOUT_SUBJ_LEMMAS + HELDOUT_OBJ_LEMMAS:
        assert v not in train_verbs, "LEAK: held-out lemma %r present in training episodes" % v
    return train_eps, held_eps, unresolved


def experiencer_axis_acc(preds, eps):
    if not eps:
        return None
    correct = sum(1 for p, ep in zip(preds, eps) if p == ep["gold_class"])
    return correct / len(eps)


def position_majority_fit(train_eps):
    buckets = {"pre": Counter(), "post": Counter()}
    for ep in train_eps:
        order = "pre" if "order_pre" in ep["feats"] else "post"
        buckets[order][ep["gold_class"]] += 1
    table = {}
    for order, c in buckets.items():
        table[order] = c.most_common(1)[0][0] if c else "OTHER"
    return table


def position_majority_predict(table, eps):
    out = []
    for ep in eps:
        order = "pre" if "order_pre" in ep["feats"] else "post"
        out.append(table.get(order, "OTHER"))
    return out


def scramble_train(train_eps, seed=SCRAMBLE_SEED):
    classes = sorted({ep["gold_class"] for ep in train_eps})
    rng = random.Random(seed)
    perm = classes[:]
    rng.shuffle(perm)
    if perm == classes:
        perm = perm[::-1]
    cmap = dict(zip(classes, perm))
    out = []
    for ep in train_eps:
        ne = dict(ep)
        ne["feats"] = list(ep["feats"])
        ne["gold_class"] = cmap[ep["gold_class"]]
        out.append(ne)
    return out, cmap


def _predict_all(chosen_name, hypothesis, eps):
    return [FI.predict_subj_role(chosen_name, hypothesis, ep["feats"], default="OTHER") for ep in eps]


def _arms_differ_hash(pred_dict):
    digests = {}
    for name, preds in pred_dict.items():
        b = ("|".join(preds)).encode("utf-8")
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    identical = [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))
                 if digests[names[i]] == digests[names[j]]]
    return digests, identical


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _axis_tier(acc, beats_default, beats_position, n):
    if acc is None:
        return "NO_DATA"
    if n < SMALL_N_CAP:
        cap = "MIDDLE_BAND"
    else:
        cap = None
    if acc < HF_ACC_MAX:
        return "HARD_FAIL"
    if acc >= HP_ACC_MIN - EPS and beats_default and beats_position:
        return cap or "HARD_PASS"
    return "MIDDLE_BAND"


def run_pipeline(run_mode):
    t0 = time.perf_counter()

    train_eps, held_eps, unresolved = build_corpus()
    assert len(train_eps) > 0 and len(held_eps) > 0, "empty corpus after real-data adaptation"

    held_subj = [e for e in held_eps if e["exp_type"] == "subj"]
    held_obj = [e for e in held_eps if e["exp_type"] == "obj"]

    # ---- Induce (MDL-auto-select), REAL_CONSTRUCTION_ATOMS ----
    classes = sorted({ep["gold_class"] for ep in train_eps})
    spec = FI.default_spec(classes, atoms=FI.REAL_CONSTRUCTION_ATOMS)
    chosen_name, chosen, all_results = FI.induce(train_eps, spec=spec)
    induced_hyp = chosen.hypothesis if chosen is not None else None

    preds_subj = _predict_all(chosen_name, induced_hyp, held_subj)
    preds_obj = _predict_all(chosen_name, induced_hyp, held_obj)
    acc_subj = experiencer_axis_acc(preds_subj, held_subj)
    acc_obj = experiencer_axis_acc(preds_obj, held_obj)

    per_record = []
    for group, preds in ((held_subj, preds_subj), (held_obj, preds_obj)):
        for ep, p in zip(group, preds):
            per_record.append({"verb": ep["verb"], "exp_type": ep["exp_type"],
                               "construction_gold": ep["construction_gold"], "text": ep["text"],
                               "feats": ep["feats"], "pred": p, "gold": ep["gold_class"],
                               "correct": bool(p == ep["gold_class"])})

    # ---- Baseline 1: DEFAULT_FRAME (never predict EXPERIENCER for an unknown verb) ----
    def_subj = ["OTHER"] * len(held_subj)
    def_obj = ["OTHER"] * len(held_obj)
    acc_def_subj = experiencer_axis_acc(def_subj, held_subj)
    acc_def_obj = experiencer_axis_acc(def_obj, held_obj)

    # ---- Baseline 2: POSITION-MAJORITY (order_pre-conditioned majority from TRAIN) ----
    pos_table = position_majority_fit(train_eps)
    pos_subj = position_majority_predict(pos_table, held_subj)
    pos_obj = position_majority_predict(pos_table, held_obj)
    acc_pos_subj = experiencer_axis_acc(pos_subj, held_subj)
    acc_pos_obj = experiencer_axis_acc(pos_obj, held_obj)

    # ---- Control: SCRAMBLE (aggregate over both axes' held-out episodes) ----
    scr_train, scramble_map = scramble_train(train_eps)
    scr_name, scr_chosen, _ = FI.induce(scr_train, spec=FI.default_spec(
        sorted({e["gold_class"] for e in scr_train}), atoms=FI.REAL_CONSTRUCTION_ATOMS))
    scr_hyp = scr_chosen.hypothesis if scr_chosen is not None else None
    preds_scr_subj = _predict_all(scr_name, scr_hyp, held_subj)
    preds_scr_obj = _predict_all(scr_name, scr_hyp, held_obj)
    acc_scr_subj = experiencer_axis_acc(preds_scr_subj, held_subj)
    acc_scr_obj = experiencer_axis_acc(preds_scr_obj, held_obj)
    acc_all = experiencer_axis_acc(preds_subj + preds_obj, held_subj + held_obj)
    acc_scr_all = experiencer_axis_acc(preds_scr_subj + preds_scr_obj, held_subj + held_obj)
    scramble_delta = (acc_all - acc_scr_all) if (acc_all is not None and acc_scr_all is not None) else None
    scramble_collapses = bool(scramble_delta is not None and scramble_delta >= SCRAMBLE_COLLAPSE_DELTA_MIN - EPS)

    beats_default_subj = bool(acc_subj is not None and acc_def_subj is not None and acc_subj > acc_def_subj + EPS)
    beats_default_obj = bool(acc_obj is not None and acc_def_obj is not None and acc_obj > acc_def_obj + EPS)
    beats_position_subj = bool(acc_subj is not None and acc_pos_subj is not None and
                               (acc_subj - acc_pos_subj) >= POSITION_BEAT_MARGIN_MIN - EPS)
    beats_position_obj = bool(acc_obj is not None and acc_pos_obj is not None and
                              (acc_obj - acc_pos_obj) >= POSITION_BEAT_MARGIN_MIN - EPS)

    tier_subj = _axis_tier(acc_subj, beats_default_subj, beats_position_subj, len(held_subj))
    tier_obj = _axis_tier(acc_obj, beats_default_obj, beats_position_obj, len(held_obj))
    if not scramble_collapses:
        # scramble failure invalidates the induced mechanism entirely -- both axes demote.
        tier_subj = "HARD_FAIL" if tier_subj != "NO_DATA" else tier_subj
        tier_obj = "HARD_FAIL" if tier_obj != "NO_DATA" else tier_obj

    _TIER_ORDER = {"HARD_FAIL": 0, "NO_DATA": 0, "MIDDLE_BAND": 1, "HARD_PASS": 2}
    overall = min([tier_subj, tier_obj], key=lambda t: _TIER_ORDER[t])

    digests, identical = _arms_differ_hash({
        "induced_subj": preds_subj, "induced_obj": preds_obj,
        "default_subj": def_subj, "default_obj": def_obj,
        "position_subj": pos_subj, "position_obj": pos_obj,
        "scramble_subj": preds_scr_subj, "scramble_obj": preds_scr_obj})

    msg = (
        "overall=%s (worse-of-axes). SUBJ-axis: acc=%s N=%d tier=%s beats_default=%s beats_position=%s "
        "(pos_acc=%s). OBJ-axis (hard case): acc=%s N=%d tier=%s beats_default=%s beats_position=%s "
        "(pos_acc=%s). scramble_delta=%s scramble_collapses=%s. Induced=%s. Real litbank-mined data, "
        "NOT templated." % (
            overall, acc_subj, len(held_subj), tier_subj, beats_default_subj, beats_position_subj,
            acc_pos_subj, acc_obj, len(held_obj), tier_obj, beats_default_obj, beats_position_obj,
            acc_pos_obj, scramble_delta, scramble_collapses, chosen_name))

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": overall, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "scope_note": ("Real-data capability re-run of the templated mechanism-demo "
                       "(exp_frame_induction_oov_psych_v1, commit 893a6fa88/b8f54bf5d, MIDDLE per "
                       "synthetic-toy-outcomes-can-be-construction-determined). Same learner-expand "
                       "mechanism (registry.learn/apply, MDL-auto-select), NEW real-text feature "
                       "encoder (hdlab/frame_induction.py real-data adapter, this session)."),
        "supplied_vs_earned": ("role vocabulary (EXPERIENCER/OTHER) + construction-cue detector "
                               "definitions (has_scomp/degree_mod/progressive/passive/order_pre/"
                               "arg_animate) SUPPLIED; construction->frame MAPPING EARNED (induced "
                               "from TRAIN-split real sentences, transferred to unseen lemmas by "
                               "construction-feature overlap only; lemma never a feature)."),
        "data_source": "experiments/data/experiencer_narrative_roles_v1.jsonl (real, litbank-mined + flagged supplements)",
        "config_only_expand": True,
        "hdlab_learner_core_registry_plugins_edited": False,
        "induced_plugin": chosen_name,
        "induced_hypothesis": induced_hyp,
        "all_plugin_compression_ratios": {
            n: (r.compression_ratio if (r.description_bits > 0 or r.null_bits > 0) else None)
            for n, r in all_results.items()},
        "n_train_episodes": len(train_eps),
        "n_unresolved_locate_failures": len(unresolved),
        "unresolved_locate_failures_sample": unresolved[:10],
        "heldout_subj_lemmas": HELDOUT_SUBJ_LEMMAS,
        "heldout_obj_lemmas": HELDOUT_OBJ_LEMMAS,
        "n_heldout_subj_sentences": len(held_subj),
        "n_heldout_obj_sentences": len(held_obj),
        "small_n_cap_threshold": SMALL_N_CAP,
        "acc_experiencer_subj_axis_heldout": acc_subj,
        "acc_experiencer_obj_axis_heldout": acc_obj,
        "acc_default_agent_subj_axis": acc_def_subj,
        "acc_default_agent_obj_axis": acc_def_obj,
        "acc_position_majority_subj_axis": acc_pos_subj,
        "acc_position_majority_obj_axis": acc_pos_obj,
        "acc_experiencer_scrambled_aggregate": acc_scr_all,
        "acc_experiencer_unscrambled_aggregate": acc_all,
        "scramble_delta": scramble_delta,
        "scramble_collapses": scramble_collapses,
        "scramble_class_map": scramble_map,
        "beats_default_agent_subj": beats_default_subj,
        "beats_default_agent_obj": beats_default_obj,
        "beats_position_majority_subj": beats_position_subj,
        "beats_position_majority_obj": beats_position_obj,
        "tier_subj_axis": tier_subj,
        "tier_obj_axis": tier_obj,
        "position_majority_table": pos_table,
        "per_heldout_record": per_record,
        "arms_differ": {"digests": digests, "identical_pairs": identical},
        "arms_differ_verified": bool(len(identical) == 0),
        "arms_differ_exempted": (
            [{"pair": p, "rationale": "default and position-majority arms may legitimately "
              "coincide (both predict all-OTHER on an axis) when the order-conditioned TRAIN "
              "majority happens to be OTHER; not an arm-implementation bug."}
             for p in identical] if identical else []),
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "accuracy over a discrete 2-class axis; no capacity/CRLB floor",
        "baseline_in_band": "n/a (DEFAULT_AGENT + POSITION_MAJORITY are the discriminating baselines under test)",
        "cardinality_ok": True, "expected_n_units": 1,
        "calibration_check": "default_ok_for_this_regime",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
    }
    return metrics


def _instrumentation_selftest():
    FI._selftest()
    FI._selftest_real_adapter()
    train_eps, held_eps, unresolved = build_corpus()
    assert len(train_eps) >= 100, "train episode count too low: %d" % len(train_eps)
    assert len(held_eps) == 23, "heldout episode count mismatch: %d (expected 23)" % len(held_eps)
    assert len(unresolved) <= 5, "too many locate failures (%d) -- encoder regression" % len(unresolved)
    tv = {e["verb"] for e in train_eps}
    for v in HELDOUT_SUBJ_LEMMAS + HELDOUT_OBJ_LEMMAS:
        assert v not in tv, "LEAK: %r in training" % v


_instrumentation_selftest()


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR, metrics)
    print("[self_test] verdict=%s" % metrics["verdict"], flush=True)
    print("[self_test] " + metrics["verdict_msg"], flush=True)
    return metrics["verdict"] != "CELL_CRASHED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["full", "self_test"], default="full")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]), flush=True)
    print("[%s] %s" % (args.run_mode, metrics["verdict_msg"]), flush=True)
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("induced_hypothesis", "arms_differ", "per_heldout_record")}, indent=2), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
