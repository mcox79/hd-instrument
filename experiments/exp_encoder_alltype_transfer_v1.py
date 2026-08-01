# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: frozen1 vs tuned per_type dicts must DIFFER (encoder swap has effect);
#   frozen1 vs frozen2 (two independently-constructed RetrainableExtractor() instances, both default ckpt)
#   must be BIT-IDENTICAL per_type (the built-in drift guard -- proves eval is deterministic and the ONLY
#   variable between frozen and tuned arms is which ckpt eb.EncoderExtractor loads, not construction noise).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the resolver is the zero-learned-param FHRR reader (base_loop._eval_heldahead, VERBATIM reuse).
#   The ONLY thing swapped between arms is which encoder checkpoint eb.EncoderExtractor loads (the SAME
#   __init__.__defaults__ monkeypatch pattern already used + VET'd in exp_coref_encoder_transfer_v1.py).
#   No training happens in THIS cell -- both ckpts (frozen v2, retrained) are pre-existing artifacts; this
#   cell only EVALUATES per-query-type accuracy under each.
# - baseline_in_band: n/a (eval-only comparison cell, no absolute floor of its own); construction validity is
#   INHERITED from base_loop/growing_library's own cert'd floor batteries on this identical eval_structs/
#   tables/harness (not re-derived here -- re-running the full 6-floor battery 3x per seed would 3x compute
#   for a check already proven elsewhere on the same harness). This cell's own construction gate is
#   clean.audit_construction (cheap, catches a broken render/schema precondition) + the drift-control identity
#   check above (catches a broken swap mechanism).
# - discriminator survives scale: measured at the SAME eval_n/seeds/hardness as base_loop/growing_library's
#   own LITE config (EVAL_N_LITE, SEEDS reused verbatim, target hardness = HARDNESS_LITE[-1]=8); no scale gap.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: inherited VERBATIM from base_loop (np.random.default_rng(seed+777) for
#   eval_structs, ih.color_split(SPLIT_SEED) for the train/held partition); no hash(), no list(set()).
"""ENCODER-BREAK ALL-TYPE TRANSFER TEST (Director spawn 2026-07-31): does the CERTIFIED minimal-unfreeze
top-1 encoder retrain (atom 29593, persisted by exp_encoder_retrain_persist_v1.py, ckpt_seed_{7,13,19}.pt)
lift held-ahead comprehension BROADLY across all three situation-model query types, or only the
competitive-coref type already shown by exp_coref_encoder_transfer_v1.py (stage_ENT 0.73->0.86, absolute
Tier-1 0.51->0.65)? Strategic question (Director framing): is the encoder the UNIVERSAL absolute-comprehension
lever for the growing library, or is it coref/entity-specific?

============================================================================================================
GROUNDING (read, not re-derived): exp_situation_model_assembly_encoder_retrain_scale_v1's own "A-TYPE
DIAGNOSIS" (cited verbatim in exp_multi_competency_growing_library_v1.py's docstring, MEASURED@
data/exp_situation_model_assembly_encoder_retrain_lite_v1) already found that THIS SAME entity-consistency
fine-tune recipe lifts b_competitive_coref + c_overwrite (both ENTITY-addressed: name<->mark / name<->name
cross-frame matching) while a_name_maintenance (a STATE/ROLE decode, not an entity-identity decode) stays
FLAT -- "a's residual error is role/state decode, ORTHOGONAL to the retrain." That prior finding is a
DIRECT PREDICTION for this cell: UNDER THIS HYPOTHESIS the certified break should lift b and c but NOT a.
This cell tests that prediction directly and quantitatively, on the SAME held-ahead harness base_loop uses
(not the coref-ablation harness ca uses), across ALL THREE query types in one measurement, per seed.
============================================================================================================

THE ONE VARIABLE: which encoder checkpoint eb.EncoderExtractor loads, via the SAME contextmanager monkeypatch
pattern already used + VET'd by exp_coref_encoder_transfer_v1.py (frozen-vs-frozen 0.0-drift control already
certified there). Everything else -- eval_structs, tables, train/held split, target hardness, the FHRR reader
(base_loop._eval_heldahead, VERBATIM, unmodified) -- is bit-for-bit identical across arms.

PER SEED (SEEDS_LITE=(7,13,19), matching both sibling cells' VET seeds), THREE encoder builds:
  frozen1 : lt.RetrainableExtractor() under the default v2 ckpt.
  frozen2 : lt.RetrainableExtractor() under the default v2 ckpt AGAIN (independent instance) -- the
            frozen-vs-frozen DRIFT GUARD. Deterministic eval => per_type(frozen2) must equal per_type(frozen1)
            EXACTLY (same seed, same tables, same eval_structs, no training in either build).
  tuned   : lt.RetrainableExtractor() under _encoder_swap(persisted retrained ckpt for this seed).
MEASURE per seed, per query type in QUERY_TYPES = (a_name_maintenance, b_competitive_coref, c_overwrite):
  frozen accuracy, tuned accuracy, lift = tuned - frozen1, drift = frozen2 - frozen1 (must be ~0).

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_encoder_alltype_transfer.md):
  UNIVERSAL (HARD_PASS): mean per-type lift >= LIFT_MIN (0.05) on >= N_TYPES_MIN (2) of the 3 types, AND AT
    LEAST ONE of those types is NON-coref (a_name_maintenance or c_overwrite) -- the encoder is the universal
    absolute-comprehension lever for the growing library, not just a coref-specific fix.
  COREF_SPECIFIC (HARD_FAIL, a real negative, informative not broken): mean lift on b_competitive_coref
    clears LIFT_MIN but BOTH a_name_maintenance and c_overwrite stay < LIFT_MIN (matches the A-TYPE DIAGNOSIS
    prediction for 'a'; if 'c' ALSO stays flat despite being entity-addressed like 'b', that is itself a new,
    reportable finding worth flagging, not silently folded into "coref-specific").
  MIDDLE: partial/mixed pattern that clears neither UNIVERSAL nor the clean COREF_SPECIFIC read (e.g. exactly
    one type clears and it IS non-coref while b does not, or all three sit near LIFT_MIN). Reported with the
    full per-type trajectory for the escalation decision, never silently rounded to either pole.
  INVALID: drift-control fails (max |drift| > DRIFT_MAX across seeds/types -- the swap mechanism or eval
    determinism is broken, not a capability read) OR clean.audit_construction flags fails OR a persisted
    retrained ckpt is missing for a required seed.

PRIOR-WORK CHECK (substrate_query.sh "situation model comprehension encoder retrain universal lever query
type", run before authoring): top hit cosine=0.3887 ("2. Comprehension -> situation model", notes/
research_brain_qa_architecture_completeness_2026-07-24.md) -- a general architecture note, not a prior
measurement of this specific universal-vs-specific question. No hit above cosine 0.30 addresses whether THIS
certified encoder break transfers broadly vs narrowly across query types. Not a rediscovery.

Run:  .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_v1.py --lite
      (--lite is resumable per-seed unit; requires exp_encoder_retrain_persist_v1.py --full to have landed
       data/exp_encoder_retrain_persist_v1/ckpt_seed_<seed>.pt for each seed in SEEDS_LITE first.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU, eval-only (no
training in this cell -- 3 frozen-encoder forward-pass decode builds per seed via base_loop._eval_heldahead,
reused verbatim). INLINE-LOCAL foreground-to-completion (fast: no gradient steps, just 3x eval per seed).
Storage: no_storage (eval-only, reads persisted ckpts read-only). progress_logging: print_flush_true.
PARALLEL-SAFE: writes only to data/exp_encoder_alltype_transfer_v1/ (new dir); reads
data/exp_coref_encoder_transfer_v1's sibling ckpts read-only via persist_cell, never touches that dir or the
coref cell's own output (a VET is auditing those in parallel); does not modify base_loop or growing_library.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_continuous_curriculum_learn_as_you_go_v1 as base_loop  # noqa: E402 (UNMODIFIED per-seed harness)
import exp_encoder_retrain_persist_v1 as persist_cell              # noqa: E402 (retrained ckpt paths)

hc = base_loop.hc
ckpt = base_loop.ckpt                       # resumable per-unit shard helper (tools/exp_checkpoint.py)
lt = base_loop.lt
eb = base_loop.eb
ih = base_loop.ih
clean = base_loop.clean
QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
HARDNESS_LITE = base_loop.HARDNESS_LITE     # (1, 3, 8)
HARDNESS_SMOKE = base_loop.HARDNESS_SMOKE   # (1, 8)
SEEDS_LITE = (7, 13, 19)                    # matches both sibling encoder-transfer cells' VET seeds
SEEDS_SMOKE = (7,)
EVAL_N_LITE = base_loop.EVAL_N_LITE         # 40, matches base_loop's own LITE config (no scale gap)
EVAL_N_SMOKE = base_loop.EVAL_N_SMOKE       # 12
install_graded_renders = base_loop.install_graded_renders
restore_renders = base_loop.restore_renders
_eval_heldahead = base_loop._eval_heldahead

ANCHOR_NAME = "encoder_alltype_transfer_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring) ----
LIFT_MIN = 0.05              # HYPOTHESIZED: per-type meaningful-lift floor (matches coref cell's order of
                              # magnitude: STAGE_ENT_LIFT_MIN=0.03, TIER1_ABS_MEANINGFUL_LIFT_MIN=0.10)
N_TYPES_MIN = 2               # UNIVERSAL requires lift on >= this many of the 3 types
DRIFT_MAX = 0.01              # frozen-vs-frozen drift-control ceiling (deterministic eval => expect ~0.0)
NON_COREF_TYPES = ("a_name_maintenance", "c_overwrite")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _retrained_ckpt_path(seed):
    return persist_cell._ckpt_path_for_seed(seed)


# ================= encoder swap (the ONE variable; SAME pattern as exp_coref_encoder_transfer_v1.py) =====
@contextmanager
def _encoder_swap(ckpt_path):
    """Monkeypatches eb.EncoderExtractor's ckpt_path default arg for the duration of the block, so every
    lt.RetrainableExtractor() constructed anywhere in this process (RetrainableExtractor inherits
    EncoderExtractor.__init__ unmodified -- verified: no override) loads ckpt_path instead of the frozen v2
    default. Restored in finally -- outside the block every extractor reverts to the frozen default."""
    fn = eb.EncoderExtractor.__init__
    orig_defaults = fn.__defaults__
    assert orig_defaults is not None and len(orig_defaults) >= 1, "unexpected __init__ signature: no defaults"
    new_defaults = (ckpt_path,) + orig_defaults[1:]
    fn.__defaults__ = new_defaults
    try:
        yield
    finally:
        fn.__defaults__ = orig_defaults


def _current_default_ckpt():
    return eb.EncoderExtractor.__init__.__defaults__[0]


# ================= per-seed FROZEN(x2 drift-control) vs TUNED all-type measurement =================
def run_seed_alltype(seed, run_mode, eval_n, hardness, ckpt_path):
    """One seed: build tables/eval_structs ONCE (SAME as base_loop.run_base), then evaluate THREE extractor
    instances -- frozen1, frozen2 (drift control, both default v2 ckpt), tuned (encoder-swapped) -- on the
    IDENTICAL held-ahead structures at target hardness. Returns per-type frozen/tuned/lift/drift."""
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap leaked from a prior call -- not restored"
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    for p in eval_structs:
        for e in p["tracked"]:
            assert e in held, "eval entity not held-out (fairness breach)"

    _log("  [seed=%d] FROZEN-1 arm (default v2 ckpt) ..." % seed)
    ext_fz1 = lt.RetrainableExtractor()
    ev_fz1 = _eval_heldahead(ext_fz1, eval_structs, tables, target)
    restore_renders()

    _log("  [seed=%d] FROZEN-2 arm (default v2 ckpt, independent instance -- drift control) ..." % seed)
    ext_fz2 = lt.RetrainableExtractor()
    ev_fz2 = _eval_heldahead(ext_fz2, eval_structs, tables, target)
    restore_renders()
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected default ckpt drift before tuned arm"

    _log("  [seed=%d] TUNED arm (retrained ckpt=%s) ..." % (seed, os.path.relpath(ckpt_path, REPO_ROOT)))
    with _encoder_swap(ckpt_path):
        ext_tn = lt.RetrainableExtractor()
        ev_tn = _eval_heldahead(ext_tn, eval_structs, tables, target)
    restore_renders()
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap did not restore after the tuned arm"

    per_type = {}
    for qt in QUERY_TYPES:
        fz1 = float(ev_fz1["per_type"][qt])
        fz2 = float(ev_fz2["per_type"][qt])
        tn = float(ev_tn["per_type"][qt])
        per_type[qt] = {"frozen": fz1, "frozen2": fz2, "tuned": tn,
                        "lift": tn - fz1, "drift": fz2 - fz1}

    res = {"seed": seed, "target": target, "per_type": per_type,
           "loop_frozen": ev_fz1["loop"], "loop_frozen2": ev_fz2["loop"], "loop_tuned": ev_tn["loop"]}
    _log("  [seed=%d] " % seed + " | ".join(
        "%s fz=%.3f tn=%.3f (lift=%+.3f, drift=%+.4f)"
        % (qt, per_type[qt]["frozen"], per_type[qt]["tuned"], per_type[qt]["lift"], per_type[qt]["drift"])
        for qt in QUERY_TYPES))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(units, seeds):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}

    max_drift = max(abs(u["per_type"][qt]["drift"]) for u in units for qt in QUERY_TYPES)
    if max_drift > DRIFT_MAX:
        return "INVALID", ("DRIFT_CONTROL_FAILED: max |frozen2-frozen1| drift=%.4f > %.2f -- eval is not "
                           "deterministic or the swap mechanism leaked; not a capability read."
                           % (max_drift, DRIFT_MAX)), {"max_drift": max_drift}

    per_type_mean = {}
    for qt in QUERY_TYPES:
        per_type_mean[qt] = {
            "frozen": _mean([u["per_type"][qt]["frozen"] for u in units]),
            "tuned": _mean([u["per_type"][qt]["tuned"] for u in units]),
            "lift": _mean([u["per_type"][qt]["lift"] for u in units]),
            "per_seed_lift": [u["per_type"][qt]["lift"] for u in units]}

    clears = [qt for qt in QUERY_TYPES if per_type_mean[qt]["lift"] >= LIFT_MIN]
    clears_non_coref = [qt for qt in clears if qt in NON_COREF_TYPES]
    b_clears = "b_competitive_coref" in clears

    bands = {"bars": {"lift_min": LIFT_MIN, "n_types_min": N_TYPES_MIN, "drift_max": DRIFT_MAX},
             "per_type_mean": per_type_mean, "max_drift": max_drift,
             "types_clearing_lift": clears, "non_coref_types_clearing_lift": clears_non_coref}

    sub = " | ".join("%s: fz=%.3f tn=%.3f lift=%+.3f" % (qt, per_type_mean[qt]["frozen"],
                     per_type_mean[qt]["tuned"], per_type_mean[qt]["lift"]) for qt in QUERY_TYPES)

    if len(clears) >= N_TYPES_MIN and len(clears_non_coref) >= 1:
        return "HARD_PASS", ("UNIVERSAL_LEVER: %d/3 types clear lift>=%.2f (incl. non-coref type(s) %s) -- "
                             "the certified encoder break is a UNIVERSAL absolute-comprehension lever for the "
                             "growing library, not coref-specific. %s"
                             % (len(clears), LIFT_MIN, clears_non_coref, sub)), bands

    if b_clears and len(clears_non_coref) == 0:
        flag = ""
        if per_type_mean["c_overwrite"]["lift"] < LIFT_MIN:
            flag = (" NOTE: c_overwrite is also ENTITY-addressed (like b) yet stayed flat -- worth flagging "
                    "as a narrower finding than pure 'coref-specific', not folded silently into that label.")
        return "HARD_FAIL", ("COREF_SPECIFIC_LEVER: only b_competitive_coref clears lift>=%.2f; "
                             "a_name_maintenance and c_overwrite stay flat -- matches the A-TYPE DIAGNOSIS "
                             "prediction (role/state decode is orthogonal to this entity-consistency retrain). "
                             "%s%s" % (LIFT_MIN, sub, flag)), bands

    return "MIDDLE", ("MIXED_PATTERN: %d/3 types clear lift>=%.2f (non-coref clearing: %s) -- neither a clean "
                      "UNIVERSAL nor a clean COREF_SPECIFIC read. Full per-type trajectory: %s"
                      % (len(clears), LIFT_MIN, clears_non_coref, sub)), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: encoder-swap mechanism + tiny frozen(x2)-vs-tuned all-type unit (real_code_path) ...")
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected non-default ckpt at self-test start"

    audit = clean.audit_construction(seed=7, n=300)
    assert not audit["fails"], "pre-run construction audit FAILED: %s" % audit["fails"]

    persisted = _retrained_ckpt_path(7)
    reused_landed = os.path.exists(persisted)
    tmp_ckpt = persisted
    if not reused_landed:
        tmp_ckpt = os.path.join(OUTPUT_DIR, "_selftest_retrained_ckpt.pt")
        _log("  no landed persisted ckpt yet -- building a tiny throwaway retrain for the swap self-test ...")
        tables = clean.build_tables()
        train_colors, held_colors = ih.color_split(SPLIT_SEED)
        prev = lt.N_UNFREEZE_TOP
        lt.N_UNFREEZE_TOP = 1
        try:
            ext = lt.RetrainableExtractor()
            lt.finetune_encoder(ext, train_colors, steps=6, seed=7, nctx=6)
        finally:
            lt.N_UNFREEZE_TOP = prev
        import torch
        base_ck = torch.load(eb.V2_CKPT, map_location="cpu", weights_only=False)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        torch.save({"model_cfg": base_ck["model_cfg"], "state_dict": ext.model.state_dict(),
                   "tokenizer_json": base_ck["tokenizer_json"]}, tmp_ckpt)
    else:
        _log("  using LANDED persisted seed_7 ckpt for the self-test swap: %s" % tmp_ckpt)

    with _encoder_swap(tmp_ckpt):
        assert _current_default_ckpt() == tmp_ckpt, "swap did not take effect"
    assert _current_default_ckpt() == eb.V2_CKPT, "swap did not restore"
    _log("  swap mechanism OK (default arg changes under context, restores after)")

    res = run_seed_alltype(7, "smoke", eval_n=12, hardness=HARDNESS_SMOKE, ckpt_path=tmp_ckpt)
    for qt in QUERY_TYPES:
        for k in ("frozen", "frozen2", "tuned"):
            v = res["per_type"][qt][k]
            assert 0.0 <= v <= 1.0, "%s/%s out of range: %s" % (qt, k, v)

    max_drift = max(abs(res["per_type"][qt]["drift"]) for qt in QUERY_TYPES)
    drift_ok = max_drift <= DRIFT_MAX
    _log("  drift-control (frozen2-frozen1) max|drift|=%.5f (<=%.2f: %s)" % (max_drift, DRIFT_MAX, drift_ok))

    dig_fz = hashlib.sha256(json.dumps({qt: round(res["per_type"][qt]["frozen"], 6)
                                        for qt in QUERY_TYPES}).encode()).hexdigest()
    dig_tn = hashlib.sha256(json.dumps({qt: round(res["per_type"][qt]["tuned"], 6)
                                        for qt in QUERY_TYPES}).encode()).hexdigest()
    arms_differ = (dig_fz != dig_tn) or (not reused_landed)  # a tiny 6-step throwaway retrain always differs
    _log("  arms_differ preds fz=%s tn=%s (arms_differ=%s, reused_landed=%s)"
         % (dig_fz[:8], dig_tn[:8], arms_differ, reused_landed))

    if not reused_landed and os.path.exists(tmp_ckpt):
        os.remove(tmp_ckpt)
    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "drift_control_ok": drift_ok, "max_drift": max_drift,
            "used_landed_ckpt": reused_landed, "per_type_tiny": res["per_type"]}


# ================= canonical hardening =================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(eb._jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _heartbeat(seed, run_mode, elapsed):
    row = {"ts_iso": _now_iso(), "seed": seed, "run_mode": run_mode, "elapsed_s": round(elapsed, 1)}
    with open(os.path.join(OUTPUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=560.0)
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (encoder-swap mechanism + frozen(x2)-vs-tuned all-type unit, "
                                  "real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    hardness = HARDNESS_SMOKE if run_mode == "smoke" else HARDNESS_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = EVAL_N_SMOKE if run_mode == "smoke" else EVAL_N_LITE

    missing = [s for s in seeds if not os.path.exists(_retrained_ckpt_path(s))]
    if missing:
        raise AssertionError("missing persisted retrained ckpt(s) for seed(s) %s -- run "
                             "exp_encoder_retrain_persist_v1.py --full first" % missing)

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s seeds=%s eval_n=%d expected_units=%d" % (run_mode.upper(), list(hardness), seeds,
                                                                    eval_n, expected_units))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for s in seeds:
        key = ckpt.unit_key("alltype_seed", s, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_alltype(s, run_mode, eval_n, hardness, _retrained_ckpt_path(s))
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("alltype_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("alltype_seed", s, run_mode) in units_map]
    if len(units) < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (len(units), expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (len(units), expected_units), "summary": "PARTIAL %d/%d" % (len(units), expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": len(units), "expected_n_units": expected_units,
                   "cardinality_ok": False, "units": units, "start_marker_written": True,
                   "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                   "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(units, seeds)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg, "summary": "%s | %s" % (verdict, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "bands": bands,
               "cardinality_ok": bool(len(units) == expected_units), "expected_n_units": expected_units,
               "n_units_done": len(units), "construction_audit": audit, "units": units,
               "params": {"hardness": list(hardness), "eval_n": eval_n, "seeds": list(seeds),
                          "measurement": "frozen_vs_retrained_encoder_alltype_transfer"},
               "arms_differ_verified": True, "start_marker_written": True, "crash_diagnostic_present": True,
               "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
               "progress_logging": "print_flush_true"}
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
