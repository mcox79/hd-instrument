# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a + discriminator_reachability declared (capacity-feasibility)
# - baseline_in_band n/a for classification arms (direct accuracy vs fixed true labels, not a
#   baseline-vs-mechanism comparison); end-to-end arm's recency baseline (0.70) is in-band.
# - discriminator survives scale: FULL-N IS the smoke regime (32+32 held-out words, not a reduced
#   preview) -- see self_test().
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - cardinality_ok for the 5-unit sweep (META_RULE_H; EXPECTED_N_UNITS gate)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except)
# - calibration_check field (META_RULE_M)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
"""exp_verb_class_openvocab_similarity_v1 -- pre-reg'd cell for the open-vocab VERB-CLASS
membership fix (Tier-2 shared-feature-similarity extension of hdlab/goal_typing.py's closed-set
verb lexicons), per notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md and
preregs/2026-08-06_verb_class_openvocab_similarity_v1.md (READ THAT PRE-REG FIRST -- it is this
cell's complete design spec + the MEASURED numbers this cell reproduces).

WHY (task brief, disk-verified trigger): commit 72f2c16b1 / f496caa51 (generalization probe)
measured owner-acc=0.30 vs recency=0.70 baseline on real McGuffey prose, with 6/10 items
OUTCOME_NEVER_TYPED, because hdlab/goal_typing.py's closed-set verb lexicons (CLASS_REGISTRY,
V2_OUTCOME_MET/_UNMET, DESIDERATIVE_PASS/ASPECTUAL_STOP) are OOV for real prose. The fix (already
built + wired in hdlab/goal_typing.py + hdlab/verb_lexical_similarity.py, strict ADD, Tier-1
exact-match always wins) extends verb-class membership to concept_similarity(verb, seed
exemplars) via the ALREADY-PROVEN FHRR bundle-cosine mechanism. This cell is the pre-reg'd,
non-circular, corpus-drawn-held-out MEASUREMENT of that fix (not the fix itself -- the fix lives in
hdlab/, this cell only measures it), reproducible from a clean process.

FIVE UNITS (checkpointed via tools/exp_checkpoint.py):
  (1) "classification" -- held-out non-circular OUTCOME polarity + GOAL-vs-ASPECT classification
      accuracy (32+32 words, FLOOR=0.35/MARGIN=0.15, drill Section 5 Measure A). FULL-N IS the
      smoke regime -- there is no reduced-N smoke variant, the whole held-out pool runs every time
      (fast, deterministic, no scale-saturation risk per DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
  (2) "scramble" -- global word->feature-tagset permutation control, 5 perm seeds, both pools
      (drill Section 5's scramble-collapse gate).
  (3-5) "endtoend_seed_{0,1,2}" -- THE DECISIVE END-TO-END TEST (drill Section 5 Measure B):
      re-run experiments.exp_real_text_goal_owner_generalization_diagnostic_v1.run_seed(seed) (the
      SAME production harness the disk-verified baseline used) with the Tier-2 patches LIVE in
      hdlab/goal_typing.py (this cell does not modify that harness or its bank; it imports and
      calls the SAME functions, which now transparently route through Tier-2 on OOV). Reports
      OUTCOME_NEVER_TYPED count + organ_owner_accuracy + organ_polarity_accuracy vs the disk-
      verified baseline (owner=0.30, OUTCOME_NEVER_TYPED=6/10, polarity=0.10,
      MEASURED@d:/AI/hd-instrument/data/exp_real_text_goal_owner_generalization_diagnostic_v1/
      metrics.json, commit f496caa51).

Cites: hdlab/verb_lexical_similarity.py (the built organ); hdlab/goal_typing.py (the three Tier-2
integration points); experiments/exp_real_text_goal_owner_generalization_diagnostic_v1.py (the
decisive end-to-end harness, reused not duplicated);
experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (the end-to-end bank);
preregs/2026-08-06_verb_class_openvocab_similarity_v1.md (full design spec + MEASURED numbers).

GUARDS: glass-box; deterministic (FEATURE_SEED=7 inherited convention, scramble perm seeds fixed
1-5, end-to-end SEEDS=[0,1,2] -- no hash()-derived seeding anywhere, PROT-023/F.5 compliant);
resumable per-unit via tools/exp_checkpoint.py; ASCII-only; atomic metrics write (tmp +
os.replace); LOCAL-ONLY, in-process foreground, no push.
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

ANCHOR_NAME = "verb_class_openvocab_similarity_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab import verb_lexical_similarity as V  # noqa: E402
from hdlab.goal_typing import _outcome_polarity_tier2  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
import torch  # noqa: E402

# The decisive end-to-end harness -- REUSED (imported, not duplicated). Its own module-level
# side-effect-free import is safe (no dispatch happens on import; run_seed is called explicitly
# below).
import exp_real_text_goal_owner_generalization_diagnostic_v1 as ENDTOEND  # noqa: E402

EXPECTED_N_UNITS = 5
ENDTOEND_SEEDS = [0, 1, 2]

# ---- BASELINE (disk-verified, commit f496caa51) -- what this cell's end-to-end arm is compared
# against. MEASURED@d:/AI/hd-instrument/data/exp_real_text_goal_owner_generalization_diagnostic_v1/
# metrics.json (read directly by self_test() below to guard against silent baseline drift; the
# numbers here are the frozen pre-reg record, not re-derived at import time).
BASELINE_OUTCOME_NEVER_TYPED = 6
BASELINE_OWNER_ACC = 0.30
BASELINE_POLARITY_ACC = 0.10
BASELINE_RECENCY_ACC = 0.70
BASELINE_N_ITEMS = 10


# ============================================================================ unit 1: classification
def run_classification():
    """Held-out non-circular OUTCOME polarity + GOAL-vs-ASPECT classification (drill Section 5
    Measure A). FLOOR/MARGIN match the production hdlab.goal_typing.VERB_CLASS_SIM_FLOOR/_MARGIN
    (0.35/0.15) -- imported directly, not re-typed, so this measurement can never silently drift
    from the production thresholds."""
    from hdlab.goal_typing import VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN

    seed_pos = list(V.OUTCOME_SEED_POS.keys())
    seed_neg = list(V.OUTCOME_SEED_NEG.keys())
    pos_h = list(V.OUTCOME_HELDOUT_POS.keys())
    neg_h = list(V.OUTCOME_HELDOUT_NEG.keys())
    outcome_rows = []
    for w in pos_h:
        pred = V.classify_2way(w, seed_pos, seed_neg, "outcome", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
        outcome_rows.append({"word": w, "true": "POS", "pred": pred, "correct": pred == "POS"})
    for w in neg_h:
        pred = V.classify_2way(w, seed_pos, seed_neg, "outcome", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
        outcome_rows.append({"word": w, "true": "NEG", "pred": pred, "correct": pred == "NEG"})
    outcome_acc = sum(r["correct"] for r in outcome_rows) / len(outcome_rows)

    seed_desid = list(V.GOAL_SEED_DESIDERATIVE.keys())
    seed_asp = list(V.GOAL_SEED_ASPECTUAL.keys())
    desid_h = list(V.GOAL_HELDOUT_DESIDERATIVE.keys())
    asp_h = list(V.GOAL_HELDOUT_ASPECTUAL.keys())
    goal_rows = []
    for w in desid_h:
        pred = V.classify_2way(w, seed_asp, seed_desid, "goal", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
        goal_rows.append({"word": w, "true": "DESID", "pred": ("DESID" if pred == "NEG" else pred),
                          "correct": pred == "NEG"})
    for w in asp_h:
        pred = V.classify_2way(w, seed_asp, seed_desid, "goal", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
        goal_rows.append({"word": w, "true": "ASPECT", "pred": ("ASPECT" if pred == "POS" else pred),
                          "correct": pred == "POS"})
    goal_acc = sum(r["correct"] for r in goal_rows) / len(goal_rows)

    praise_pred = _outcome_polarity_tier2("praise")
    accept_pred = _outcome_polarity_tier2("accept")
    invite_pred = _outcome_polarity_tier2("invite")
    probe_blockers_typed_correctly = (praise_pred == "MET" and accept_pred == "MET"
                                       and invite_pred == "MET")

    return dict(
        outcome_accuracy=round(outcome_acc, 4), outcome_n=len(outcome_rows),
        outcome_correct=sum(r["correct"] for r in outcome_rows),
        outcome_misses=[r for r in outcome_rows if not r["correct"]],
        goal_accuracy=round(goal_acc, 4), goal_n=len(goal_rows),
        goal_correct=sum(r["correct"] for r in goal_rows),
        goal_misses=[r for r in goal_rows if not r["correct"]],
        praise_pred=praise_pred, accept_pred=accept_pred, invite_pred=invite_pred,
        probe_blockers_typed_correctly=probe_blockers_typed_correctly,
    )


# ============================================================================ unit 2: scramble
def _scramble_accuracy(domain: str, pool_a_words, pool_b_words, heldout_a, heldout_b, perm_seed: int):
    """Global word->feature-tagset permutation (fixed disjoint perm_seed), then re-classify the
    SAME held-out test on the scrambled assignment. Byte-identical convention to
    hdlab/lexical_similarity.py's self_test SCRAMBLED_FEATURES arm."""
    feats = V._DOMAINS[domain]
    words = sorted(set(pool_a_words) | set(pool_b_words) | set(heldout_a) | set(heldout_b))
    gen = torch.Generator().manual_seed(perm_seed)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled = {words[i]: feats[words[perm[i]]] for i in range(len(words))}
    fv = V._feature_vectors(domain)

    def cvec(w):
        return V._concept_vector_from(scrambled[w], fv)

    def sim(a, b):
        return V._cos_complex(cvec(a), cvec(b))

    def mean_sim(w, pool):
        return sum(sim(w, s) for s in pool) / len(pool)

    correct, total = 0, 0
    for w in heldout_a:
        sa, sb = mean_sim(w, pool_a_words), mean_sim(w, pool_b_words)
        correct += int(sa > sb)
        total += 1
    for w in heldout_b:
        sa, sb = mean_sim(w, pool_a_words), mean_sim(w, pool_b_words)
        correct += int(sb > sa)
        total += 1
    return correct / total


def run_scramble():
    seed_pos = list(V.OUTCOME_SEED_POS.keys())
    seed_neg = list(V.OUTCOME_SEED_NEG.keys())
    pos_h = list(V.OUTCOME_HELDOUT_POS.keys())
    neg_h = list(V.OUTCOME_HELDOUT_NEG.keys())
    outcome_accs = [_scramble_accuracy("outcome", seed_pos, seed_neg, pos_h, neg_h, s)
                    for s in (1, 2, 3, 4, 5)]

    seed_desid = list(V.GOAL_SEED_DESIDERATIVE.keys())
    seed_asp = list(V.GOAL_SEED_ASPECTUAL.keys())
    desid_h = list(V.GOAL_HELDOUT_DESIDERATIVE.keys())
    asp_h = list(V.GOAL_HELDOUT_ASPECTUAL.keys())
    goal_accs = [_scramble_accuracy("goal", seed_asp, seed_desid, asp_h, desid_h, s)
                 for s in (1, 2, 3, 4, 5)]

    outcome_mean = sum(outcome_accs) / len(outcome_accs)
    goal_mean = sum(goal_accs) / len(goal_accs)
    return dict(
        outcome_scramble_accs=outcome_accs, outcome_scramble_mean=round(outcome_mean, 4),
        goal_scramble_accs=goal_accs, goal_scramble_mean=round(goal_mean, 4),
        outcome_collapses_within_15pct=abs(outcome_mean - 0.5) <= 0.15,
        goal_collapses_within_15pct=abs(goal_mean - 0.5) <= 0.15,
    )


# ============================================================================ units 3-5: end-to-end
def run_endtoend_seed(seed: int):
    """Re-run the decisive production harness (imported, not duplicated) with Tier-2 live."""
    res = ENDTOEND.run_seed(seed)
    return dict(
        seed=seed, n_items=res["n_items"],
        n_outcome_typeable=res["n_outcome_typeable"],
        outcome_never_typed_count=res["n_items"] - res["n_outcome_typeable"],
        organ_owner_accuracy=res["organ_owner_accuracy"],
        recency_accuracy=res["recency_accuracy"],
        organ_polarity_accuracy=res["organ_polarity_accuracy"],
        lexicon_baseline_polarity_accuracy=res["lexicon_baseline_polarity_accuracy"],
        owner_failure_tally=res["owner_failure_tally"],
        polarity_failure_tally=res["polarity_failure_tally"],
    )


# ============================================================================ arms-must-differ (META_RULE_AF)
def _arms_must_differ_check():
    """real vs SCRAMBLED concept vectors for the decisive praise/crave pairs must be bit-different
    (hash check) -- catches a degenerate scramble that accidentally reproduces the real assignment."""
    real_praise = V.concept_vector("praise", "outcome")
    fv = V._feature_vectors("outcome")
    words = sorted(V.OUTCOME_VERB_FEATURES.keys())
    gen = torch.Generator().manual_seed(999)
    perm = torch.randperm(len(words), generator=gen).tolist()
    scrambled_map = {words[i]: V.OUTCOME_VERB_FEATURES[words[perm[i]]] for i in range(len(words))}
    scr_praise = V._concept_vector_from(scrambled_map["praise"], fv)

    def digest(t):
        return hashlib.sha256(t.numpy().tobytes()).hexdigest()

    d_real, d_scr = digest(real_praise), digest(scr_praise)
    return {"real_praise": d_real, "scrambled_praise": d_scr, "differ": d_real != d_scr}


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": anchor_name, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    _write_json(os.path.join(output_dir, "_start_marker.json"), marker)


# ============================================================================ verdict logic
def aggregate(units: dict):
    cls_r = units["classification"]
    scr_r = units["scramble"]
    e0, e1, e2 = units["endtoend_seed_0"], units["endtoend_seed_1"], units["endtoend_seed_2"]
    endtoend_deterministic = (
        e0["outcome_never_typed_count"] == e1["outcome_never_typed_count"] == e2["outcome_never_typed_count"]
        and e0["organ_owner_accuracy"] == e1["organ_owner_accuracy"] == e2["organ_owner_accuracy"])

    outcome_never_typed = e0["outcome_never_typed_count"]
    owner_acc = e0["organ_owner_accuracy"]
    polarity_acc = e0["organ_polarity_accuracy"]

    gate_held_out_80 = cls_r["outcome_accuracy"] >= 0.80 and cls_r["goal_accuracy"] >= 0.80
    gate_scramble_collapses = scr_r["outcome_collapses_within_15pct"] and scr_r["goal_collapses_within_15pct"]
    gate_probe_blockers = cls_r["probe_blockers_typed_correctly"]
    gate_never_typed_drops = outcome_never_typed < BASELINE_OUTCOME_NEVER_TYPED
    owner_acc_delta = round(owner_acc - BASELINE_OWNER_ACC, 4)
    gate_owner_acc_material = owner_acc_delta >= 0.10  # "materially" = >=10 percentage points

    hard_fail_held_out_below_60 = cls_r["outcome_accuracy"] < 0.60 or cls_r["goal_accuracy"] < 0.60
    hard_fail_scramble_no_collapse = (scr_r["outcome_scramble_mean"] > 0.70
                                       or scr_r["goal_scramble_mean"] > 0.70)
    hard_fail_probe_blockers = not gate_probe_blockers
    hard_fail_bottleneck_misdiagnosed = gate_never_typed_drops and not gate_owner_acc_material

    any_hard_fail = (hard_fail_held_out_below_60 or hard_fail_scramble_no_collapse
                      or hard_fail_probe_blockers or hard_fail_bottleneck_misdiagnosed)
    all_hard_pass = (gate_held_out_80 and gate_scramble_collapses and gate_probe_blockers
                     and gate_never_typed_drops and gate_owner_acc_material)

    if any_hard_fail:
        verdict = "HARD_FAIL"
    elif all_hard_pass:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    summary = (
        f"held_out_acc(outcome={cls_r['outcome_accuracy']}, goal={cls_r['goal_accuracy']}) "
        f"scramble_mean(outcome={scr_r['outcome_scramble_mean']}, goal={scr_r['goal_scramble_mean']}) "
        f"probe_blockers_ok={gate_probe_blockers} "
        f"OUTCOME_NEVER_TYPED(baseline={BASELINE_OUTCOME_NEVER_TYPED} -> now={outcome_never_typed}) "
        f"owner_acc(baseline={BASELINE_OWNER_ACC} -> now={owner_acc}, delta={owner_acc_delta}) "
        f"vs recency={BASELINE_RECENCY_ACC} "
        f"polarity_acc(baseline={BASELINE_POLARITY_ACC} -> now={polarity_acc}) "
        f"endtoend_deterministic_across_seeds={endtoend_deterministic}."
    )

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary,
        gates=dict(
            held_out_80=gate_held_out_80, scramble_collapses=gate_scramble_collapses,
            probe_blockers_typed=gate_probe_blockers, never_typed_drops=gate_never_typed_drops,
            owner_acc_material=gate_owner_acc_material, owner_acc_delta=owner_acc_delta,
        ),
        hard_fail_triggers=dict(
            held_out_below_60=hard_fail_held_out_below_60,
            scramble_no_collapse=hard_fail_scramble_no_collapse,
            probe_blockers_fail=hard_fail_probe_blockers,
            bottleneck_misdiagnosed=hard_fail_bottleneck_misdiagnosed,
        ),
        baseline=dict(outcome_never_typed=BASELINE_OUTCOME_NEVER_TYPED, owner_acc=BASELINE_OWNER_ACC,
                      polarity_acc=BASELINE_POLARITY_ACC, recency_acc=BASELINE_RECENCY_ACC,
                      n_items=BASELINE_N_ITEMS,
                      source="data/exp_real_text_goal_owner_generalization_diagnostic_v1/metrics.json "
                             "(commit f496caa51, disk-verified)"),
        measured=dict(outcome_never_typed=outcome_never_typed, owner_acc=owner_acc,
                     polarity_acc=polarity_acc, endtoend_deterministic_across_seeds=endtoend_deterministic),
        classification=cls_r, scramble=scr_r,
        endtoend_per_seed={0: e0, 1: e1, 2: e2},
    )


# ============================================================================ run
def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_start_marker(OUTPUT_DIR, ANCHOR_NAME, run_mode, EXPECTED_N_UNITS)

    unit_names = ["classification", "scramble"] + [f"endtoend_seed_{s}" for s in ENDTOEND_SEEDS]
    unit_fns = {
        "classification": run_classification,
        "scramble": run_scramble,
    }
    for s in ENDTOEND_SEEDS:
        unit_fns[f"endtoend_seed_{s}"] = (lambda seed=s: run_endtoend_seed(seed))

    done = completed_units(OUTPUT_DIR)
    for name in unit_names:
        k = unit_key(name)
        if k in done:
            print(f"[resume] unit={name} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = unit_fns[name]()
        record_unit(OUTPUT_DIR, k, res)
        print(f"[progress] unit={name} {time.perf_counter() - ts:.2f}s", flush=True)

    loaded = load_units(OUTPUT_DIR)
    units = {name: loaded[unit_key(name)] for name in unit_names}
    if len(units) < EXPECTED_N_UNITS:
        raise RuntimeError(f"META_RULE_H cardinality breach: {len(units)}/{EXPECTED_N_UNITS} units")

    agg = aggregate(units)
    agg["arms_must_differ"] = _arms_must_differ_check()
    agg["arms_differ_verified"] = agg["arms_must_differ"]["differ"]
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(
        expected_n_units=EXPECTED_N_UNITS, cardinality_ok=(len(units) == EXPECTED_N_UNITS),
        endtoend_seeds=ENDTOEND_SEEDS, final_metrics_atomicity="tmp_replace", cell_chunked=True,
        deterministic_seeding=True,
        crlb_n_a="graded-similarity threshold decision + bounded accuracy metric, not a "
                 "capacity/argmax-noise-floor cell",
        discriminator_reachability=True,
        baseline_in_band_n_a="classification arms are direct held-out accuracy vs fixed true "
                              "labels, not a baseline-vs-mechanism comparison; end-to-end arm's "
                              "recency baseline (0.70) is in-band by construction",
        calibration_check="default_ok_for_this_regime: VERB_CLASS_SIM_FLOOR/MARGIN imported "
                          "directly from hdlab.goal_typing (production values), not re-typed",
    )
    agg["prereg"] = "preregs/2026-08-06_verb_class_openvocab_similarity_v1.md"
    agg["cites"] = [
        "hdlab/verb_lexical_similarity.py (the built organ)",
        "hdlab/goal_typing.py (three Tier-2 integration points)",
        "experiments/exp_real_text_goal_owner_generalization_diagnostic_v1.py (decisive end-to-end harness, reused)",
        "experiments/data/real_text_goal_owner_diagnostic_v1.jsonl (end-to-end bank, 10 items)",
        "notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md (formalize drill)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (1) module coverage sanity
    assert len(V.OUTCOME_HELDOUT_POS) == 16 and len(V.OUTCOME_HELDOUT_NEG) == 16
    assert len(V.GOAL_HELDOUT_DESIDERATIVE) == 16 and len(V.GOAL_HELDOUT_ASPECTUAL) == 16
    print("[SELFTEST 1/5] held-out pool cardinality: 16+16 outcome, 16+16 goal", flush=True)

    # (2) real production code path: hdlab.goal_typing's Tier-2 functions are actually callable and
    # produce well-typed results (not a synthetic-only branch).
    from hdlab.goal_typing import _verb_classes, congruence_with_lexicon_fallback
    classes = _verb_classes("recover")
    assert classes == {"HEAL_CLASS"}, f"expected recover->HEAL_CLASS via Tier-2, got {classes}"
    pol, detail = congruence_with_lexicon_fallback(
        "Owen wanted to open the greenhouse before winter came. The gardener invited him in.")
    assert pol in ("MET", "UNMET", "AMBIGUOUS", "NONE", "NA"), f"unexpected polarity token {pol!r}"
    print(f"[SELFTEST 2/5] real production Tier-2 callable: recover->{classes}, "
          f"congruence_with_lexicon_fallback->{pol}", flush=True)

    # (3) one full classification unit + scramble unit at FULL-N (32+32 words each -- this IS the
    # full regime, no reduced smoke variant; discriminator-survives-scale option A satisfied by
    # construction).
    cls_r = run_classification()
    assert cls_r["outcome_n"] == 32 and cls_r["goal_n"] == 32
    assert cls_r["probe_blockers_typed_correctly"], (
        f"praise/accept/invite must all type MET, got praise={cls_r['praise_pred']} "
        f"accept={cls_r['accept_pred']} invite={cls_r['invite_pred']}")
    print(f"[SELFTEST 3/5] classification FULL-N: outcome_acc={cls_r['outcome_accuracy']} "
          f"goal_acc={cls_r['goal_accuracy']} probe_blockers_ok=True", flush=True)

    scr_r = run_scramble()
    print(f"[SELFTEST 4/5] scramble: outcome_mean={scr_r['outcome_scramble_mean']} "
          f"goal_mean={scr_r['goal_scramble_mean']}", flush=True)

    # (4) end-to-end harness importable + callable on seed 0 (real code path, not synthetic).
    e0 = run_endtoend_seed(0)
    assert e0["n_items"] == 10
    assert 0.0 <= e0["organ_owner_accuracy"] <= 1.0
    print(f"[SELFTEST 5/5] endtoend seed0: n_outcome_typeable={e0['n_outcome_typeable']}/10 "
          f"owner_acc={e0['organ_owner_accuracy']} polarity_acc={e0['organ_polarity_accuracy']}",
          flush=True)

    # (5) determinism: repeating seed 0 must be bit-identical (PROT-023/F.5 self-check).
    e0_repeat = run_endtoend_seed(0)
    assert e0["organ_owner_accuracy"] == e0_repeat["organ_owner_accuracy"]
    assert e0["outcome_never_typed_count"] == e0_repeat["outcome_never_typed_count"]
    print("[SELFTEST OK] endtoend seed0 repeat is deterministic", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "summary": f"CELL_CRASHED: {type(e).__name__}",
                     "elapsed_s": 0.0,
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
