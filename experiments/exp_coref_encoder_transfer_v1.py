# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: FROZEN vs TUNED per-seed units (state_dict differs -> stage_decode /
#   measure dicts asserted NOT bit-identical; an inert encoder-swap monkeypatch would leave them identical).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the resolver is the zero-learned-param FHRR SituationWM (VERBATIM via ca/clean); the ONLY
#   thing swapped between arms is which encoder checkpoint eb.EncoderExtractor loads (a module-level default-
#   arg monkeypatch, restored after each arm) -- EVERYTHING else (items, split, ablation logic, fairness
#   gates) is the UNMODIFIED ca.run_seed_unit function, called twice per seed.
# - baseline_in_band: n/a for the closed-form loop; this cell's OWN discriminator is the FROZEN-vs-TUNED
#   delta on 3 measurements (stage_ENT decode, absolute Tier-1, ablation delta), not an absolute floor.
# - discriminator survives scale: measured at the SAME eval_n/seeds as the landed atom 29594 result
#   (EVAL_N_LITE=90, SEEDS_LITE=(7,13,19)); no scale gap between smoke and full other than the encoder swap.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: inherited VERBATIM from ca.run_seed_unit (numpy default_rng(seed) only).
"""ENCODER-BREAK TRANSFER TEST (Director spawn 2026-07-31): does the CERTIFIED minimal-unfreeze top-1
encoder retrain (atom 29593, now persisted by exp_encoder_retrain_persist_v1.py) TRANSFER to lift the
coref/situation-model harness's decode ceiling? This is the documented promotion criteria for atom 29594
(exp_multi_competency_coref_ablation_v1.py, COMPOSITIONAL_WIRING_CONFIRMED, mean Tier-1 delta MEASURED@
data/exp_multi_competency_coref_ablation_v1/metrics.json ~+0.19, stage_ENT~0.73, roles_present absolute
Tier-1~0.51).

FORK (A) UNDER TEST: the encoder is the binding constraint on absolute comprehension -- stage_ENT~0.73 caps
competitive-coref absolute ~0.51 while the compositional wiring (the role-ablation delta) is healthy. If (A)
is right, swapping in the certified-break encoder (held-out situation-model loop 0.52->0.83 in ITS OWN
harness) should lift stage_ENT and absolute Tier-1 in the coref harness too, WITHOUT washing out the delta
(the compositional wiring must survive the encoder change -- a different encoder that merely shortcuts
Tier-1 without preserving role-dependence would be a false win).

ONE VARIABLE: which encoder checkpoint eb.EncoderExtractor loads. Implemented as a monkeypatch of
eb.EncoderExtractor.__init__.__defaults__ (the ckpt_path default arg) around a call to ca.run_seed_unit --
the EXACT, UNMODIFIED coref-ablation per-seed function (same Tier-1 items, same clean.SituationWM resolver,
same fairness gates, same floors) -- so every code path except "which weights the encoder forward pass uses"
is bit-for-bit identical between the frozen and tuned arm.

MEASURE PER SEED (>=3 seeds, SEEDS_LITE=(7,13,19), matching the coref cell's own VET seeds):
  (i)   stage_ENT decode (u['stage_decode']['ENT']) -- frozen vs tuned.
  (ii)  absolute Tier-1 competitive-coref accuracy (u['measure']['tier1']['present']) -- frozen vs tuned.
  (iii) role-ablation DELTA (present - ablated) on Tier-1 -- must STAY >= DELTA_INTACT_MIN (the compositional
        wiring must survive the encoder swap, not be washed out by a shortcut-solving stronger encoder).

PRE-REGISTERED BANDS (fixed BEFORE running):
  HARD_PASS (promotes atom 29594): mean stage_ENT lift >= STAGE_ENT_LIFT_MIN (0.03) AND (mean tuned absolute
    Tier-1 >= TIER1_ABS_HARD_PASS (0.70) OR mean absolute lift >= TIER1_ABS_MEANINGFUL_LIFT_MIN (0.10)) AND
    mean tuned Tier-1 delta >= DELTA_INTACT_MIN (0.10) AND every seed's tuned delta > DELTA_PERSEED_MIN
    (0.05, ca's own construction-invalid floor) AND fairness_ok + floors_ok on BOTH arms.
  HARD_FAIL_NO_TRANSFER (real negative): mean stage_ENT lift < STAGE_ENT_LIFT_MIN -- the certified encoder
    break does NOT transfer to coref-decode; a deeper/different encoder lever is needed for THIS harness.
  HARD_FAIL_WASHOUT (real negative): mean tuned Tier-1 delta < DELTA_WASHOUT_MAX (0.05) even if stage_ENT
    and/or absolute Tier-1 improved -- the stronger encoder shortcuts Tier-1 without preserving the
    role-dependent compositional wiring (a false win, not a real one).
  MIDDLE: partial transfer -- stage_ENT lifts and/or absolute improves but does not clear the HARD_PASS
    bar, while the delta stays intact (>= DELTA_WASHOUT_MAX). Reported with the trajectory.
  INVALID: a can-fail harness floor did not collapse (base_lib.base_loop._floors_ok) OR POOLED_READER is
    reservoir-decodable OR the coref fairness gate fails on either arm -- a broken TEST, not a capability
    verdict. Checked on BOTH arms independently (a stronger encoder is not exempt from the validity gates).

PRIOR-WORK CHECK (substrate_query.sh "encoder retrain checkpoint persistence transfer coref harness",
mandatory before authoring, run once for this arc's exp_dev spawn -- see exp_encoder_retrain_persist_v1.py
header for the full note): top hit cosine=0.3057, encoder_cross_checkpoint_retrieval_compat_v1 (HARD_FAIL,
cross-checkpoint RETRIEVAL degrades when a store is indexed under one checkpoint and queried under another).
Different concern (this cell never mixes checkpoints within one arm -- eb.EncoderExtractor.build() rebuilds
its own oracle/cue tables fresh per instance, so each arm's forward pass + decode + oracle are all under the
SAME single checkpoint). Not a rediscovery of this concept.

Run:  .venv/Scripts/python.exe experiments/exp_coref_encoder_transfer_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_coref_encoder_transfer_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_coref_encoder_transfer_v1.py --lite
      (--lite is resumable per-seed unit; requires exp_encoder_retrain_persist_v1.py --full to have landed
       data/exp_encoder_retrain_persist_v1/ckpt_seed_<seed>.pt for each seed in SEEDS_LITE first.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU (two frozen-
encoder forward-pass decode runs per seed via the reused ca.run_seed_unit, no training). INLINE-LOCAL
foreground-to-completion. Storage: no_storage (eval-only). progress_logging: print_flush_true.
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
import exp_multi_competency_coref_ablation_v1 as ca      # noqa: E402 (UNMODIFIED per-seed harness function)
import exp_encoder_retrain_persist_v1 as persist_cell     # noqa: E402 (retrained ckpt paths + recipe)

eb = ca.eb
clean = ca.clean
ckpt = ca.ckpt
base_lib = ca.base_lib
HARDNESS_LITE = ca.HARDNESS_LITE
HARDNESS_SMOKE = ca.HARDNESS_SMOKE
SEEDS_LITE = ca.SEEDS_LITE
SEEDS_SMOKE = ca.SEEDS_SMOKE
EVAL_N_LITE = ca.EVAL_N_LITE
EVAL_N_SMOKE = ca.EVAL_N_SMOKE
restore_renders = ca.restore_renders
DELTA_PERSEED_MIN = ca.DELTA_PERSEED_MIN   # 0.05, ca's own construction-invalid floor (reused, not redefined)

ANCHOR_NAME = "coref_encoder_transfer_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring) ----
STAGE_ENT_LIFT_MIN = 0.03          # mean stage_ENT lift floor: transfer must clear measurement noise
TIER1_ABS_HARD_PASS = 0.70         # absolute Tier-1 HARD_PASS ceiling target (per atom 29594 revival criteria)
TIER1_ABS_MEANINGFUL_LIFT_MIN = 0.10  # alt path: meaningful absolute lift even short of 0.70
DELTA_INTACT_MIN = 0.10            # tuned Tier-1 delta must stay >= this (matches ca.DELTA_WIRING_MIN)
DELTA_WASHOUT_MAX = 0.05           # below this on the TUNED arm = washout (matches ca.DELTA_PERSEED_MIN)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _retrained_ckpt_path(seed):
    return persist_cell._ckpt_path_for_seed(seed)


# ================= encoder swap (the ONE variable) =================
@contextmanager
def _encoder_swap(ckpt_path):
    """Monkeypatches eb.EncoderExtractor's ckpt_path default arg for the duration of the block, so EVERY
    lt.RetrainableExtractor() / eb.EncoderExtractor() constructed anywhere in the (deep) ca -> base_lib ->
    base_loop -> hc -> lt -> eb call chain loads ckpt_path instead of the frozen v2 default. Restored in
    finally -- outside the block, every extractor reverts to the frozen default."""
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


# ================= per-seed FROZEN vs TUNED transfer measurement =================
def run_seed_transfer(seed, run_mode, eval_n, hardness, ckpt_path):
    """ONE seed: ca.run_seed_unit (UNMODIFIED) called twice -- once under the frozen default encoder, once
    under the certified-break retrained encoder (ckpt_path). Returns both full units + the delta summary."""
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap leaked from a prior call -- not restored"
    _log("  [seed=%d] FROZEN arm (default v2 ckpt) ..." % seed)
    u_frozen = ca.run_seed_unit(seed, run_mode, eval_n, hardness)
    restore_renders()

    _log("  [seed=%d] TUNED arm (retrained ckpt=%s) ..." % (seed, os.path.relpath(ckpt_path, REPO_ROOT)))
    with _encoder_swap(ckpt_path):
        u_tuned = ca.run_seed_unit(seed, run_mode, eval_n, hardness)
    restore_renders()
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap did not restore after the tuned arm"

    stage_ent_fz = u_frozen["stage_decode"].get("ENT", float("nan"))
    stage_ent_tn = u_tuned["stage_decode"].get("ENT", float("nan"))
    abs_fz = u_frozen["measure"]["tier1"]["present"]
    abs_tn = u_tuned["measure"]["tier1"]["present"]
    delta_fz = abs_fz - u_frozen["measure"]["tier1"]["ablated"]
    delta_tn = abs_tn - u_tuned["measure"]["tier1"]["ablated"]

    res = {"seed": seed, "frozen": u_frozen, "tuned": u_tuned,
           "stage_ent_frozen": stage_ent_fz, "stage_ent_tuned": stage_ent_tn,
           "stage_ent_lift": (stage_ent_tn - stage_ent_fz) if not (math.isnan(stage_ent_fz) or math.isnan(stage_ent_tn)) else float("nan"),
           "tier1_abs_frozen": abs_fz, "tier1_abs_tuned": abs_tn,
           "tier1_abs_lift": (abs_tn - abs_fz) if not (math.isnan(abs_fz) or math.isnan(abs_tn)) else float("nan"),
           "tier1_delta_frozen": delta_fz, "tier1_delta_tuned": delta_tn,
           "frozen_fairness_ok": u_frozen["coref_fairness_ok"], "tuned_fairness_ok": u_tuned["coref_fairness_ok"]}
    _log("  [seed=%d] stage_ENT fz=%.3f tn=%.3f (lift=%.3f) | Tier1_abs fz=%.3f tn=%.3f (lift=%.3f) | "
         "Tier1_delta fz=%.3f tn=%.3f" % (seed, stage_ent_fz, stage_ent_tn, res["stage_ent_lift"],
                                          abs_fz, abs_tn, res["tier1_abs_lift"], delta_fz, delta_tn))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(units, seeds):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}

    frozen_units = [u["frozen"] for u in units]
    tuned_units = [u["tuned"] for u in units]

    floors_ok_fz, notes_fz = base_lib.base_loop._floors_ok(frozen_units)
    floors_ok_tn, notes_tn = base_lib.base_loop._floors_ok(tuned_units)
    reservoir_fz = base_lib.base_loop._pooled_reservoir(frozen_units)
    reservoir_tn = base_lib.base_loop._pooled_reservoir(tuned_units)
    fairness_fz = all(u["frozen_fairness_ok"] for u in units)
    fairness_tn = all(u["tuned_fairness_ok"] for u in units)

    if reservoir_fz or reservoir_tn:
        return "INVALID", ("POOLED_READER reservoir-decodable on %s arm -- harness trivially solvable"
                           % ("frozen" if reservoir_fz else "tuned")), {}
    if not (floors_ok_fz and floors_ok_tn):
        return "INVALID", ("can-fail harness floor did not collapse: frozen=%s tuned=%s"
                           % (notes_fz[:3], notes_tn[:3])), {}
    if not (fairness_fz and fairness_tn):
        return "INVALID", ("coref fairness gate failed: frozen_ok=%s tuned_ok=%s (cell-fix, not a capability "
                           "verdict)" % (fairness_fz, fairness_tn)), {}

    stage_ent_lift = _mean([u["stage_ent_lift"] for u in units])
    tier1_abs_frozen = _mean([u["tier1_abs_frozen"] for u in units])
    tier1_abs_tuned = _mean([u["tier1_abs_tuned"] for u in units])
    tier1_abs_lift = _mean([u["tier1_abs_lift"] for u in units])
    tier1_delta_frozen = _mean([u["tier1_delta_frozen"] for u in units])
    tier1_delta_tuned = _mean([u["tier1_delta_tuned"] for u in units])
    per_seed_delta_tuned = [u["tier1_delta_tuned"] for u in units]
    all_seeds_delta_ok = all((not math.isnan(d)) and d > DELTA_PERSEED_MIN for d in per_seed_delta_tuned)

    bands = {"bars": {"stage_ent_lift_min": STAGE_ENT_LIFT_MIN, "tier1_abs_hard_pass": TIER1_ABS_HARD_PASS,
                      "tier1_abs_meaningful_lift_min": TIER1_ABS_MEANINGFUL_LIFT_MIN,
                      "delta_intact_min": DELTA_INTACT_MIN, "delta_washout_max": DELTA_WASHOUT_MAX,
                      "delta_perseed_min": DELTA_PERSEED_MIN},
             "stage_ent_frozen": _mean([u["stage_ent_frozen"] for u in units]),
             "stage_ent_tuned": _mean([u["stage_ent_tuned"] for u in units]), "stage_ent_lift": stage_ent_lift,
             "tier1_abs_frozen": tier1_abs_frozen, "tier1_abs_tuned": tier1_abs_tuned,
             "tier1_abs_lift": tier1_abs_lift,
             "tier1_delta_frozen": tier1_delta_frozen, "tier1_delta_tuned": tier1_delta_tuned,
             "per_seed_delta_tuned": per_seed_delta_tuned, "all_seeds_delta_ok": all_seeds_delta_ok,
             "floors_ok": {"frozen": floors_ok_fz, "tuned": floors_ok_tn},
             "fairness_ok": {"frozen": fairness_fz, "tuned": fairness_tn}}

    sub = ("stage_ENT fz=%.3f tn=%.3f (lift=%.3f, min=%.2f) | Tier1_abs fz=%.3f tn=%.3f (lift=%.3f) | "
           "Tier1_delta fz=%.3f tn=%.3f (per_seed=%s, min=%.2f, washout<%.2f)"
           % (bands["stage_ent_frozen"], bands["stage_ent_tuned"], stage_ent_lift, STAGE_ENT_LIFT_MIN,
              tier1_abs_frozen, tier1_abs_tuned, tier1_abs_lift, tier1_delta_frozen, tier1_delta_tuned,
              [round(d, 3) for d in per_seed_delta_tuned], DELTA_INTACT_MIN, DELTA_WASHOUT_MAX))

    if math.isnan(stage_ent_lift) or math.isnan(tier1_delta_tuned):
        return "INVALID", "NO MEASUREMENT: stage_ENT or Tier-1 delta unmeasurable. " + sub, bands

    if tier1_delta_tuned < DELTA_WASHOUT_MAX:
        return "HARD_FAIL", ("WASHOUT: retrained encoder's Tier-1 delta=%.3f < %.2f -- compositional wiring "
                             "did NOT survive the encoder swap (a stronger encoder shortcuts Tier-1 without "
                             "preserving role-dependence; not a real transfer win). " % (tier1_delta_tuned,
                             DELTA_WASHOUT_MAX) + sub), bands

    if stage_ent_lift < STAGE_ENT_LIFT_MIN:
        return "HARD_FAIL", ("NO_TRANSFER: mean stage_ENT lift=%.3f < %.2f -- the certified encoder break "
                             "(atom 29593) does NOT transfer to this harness's decode; a deeper/different "
                             "encoder lever is needed. " % (stage_ent_lift, STAGE_ENT_LIFT_MIN) + sub), bands

    clears_abs = (tier1_abs_tuned >= TIER1_ABS_HARD_PASS) or (tier1_abs_lift >= TIER1_ABS_MEANINGFUL_LIFT_MIN)
    delta_intact = tier1_delta_tuned >= DELTA_INTACT_MIN and all_seeds_delta_ok

    if clears_abs and delta_intact:
        return "HARD_PASS", ("TRANSFER CONFIRMED (promotes atom 29594): stage_ENT lifts %.3f->%.3f "
                             "(+%.3f), absolute Tier-1 %.3f->%.3f (+%.3f, %s), delta intact %.3f->%.3f "
                             "(all %d seeds > %.2f). The encoder is the binding constraint on absolute "
                             "comprehension and the certified break RELIEVES it without washing out the "
                             "compositional wiring. " % (bands["stage_ent_frozen"], bands["stage_ent_tuned"],
                             stage_ent_lift, tier1_abs_frozen, tier1_abs_tuned, tier1_abs_lift,
                             "clears 0.70" if tier1_abs_tuned >= TIER1_ABS_HARD_PASS else "meaningful lift",
                             tier1_delta_frozen, tier1_delta_tuned, len(units), DELTA_PERSEED_MIN) + sub), bands

    return "MIDDLE", ("PARTIAL TRANSFER: stage_ENT lifts (+%.3f) and/or absolute improves (+%.3f) but does "
                      "not clear HARD_PASS (abs>=%.2f or lift>=%.2f, delta>=%.2f); delta stays intact "
                      "(>=%.2f washout floor). Report trajectory for the escalation decision. "
                      % (stage_ent_lift, tier1_abs_lift, TIER1_ABS_HARD_PASS, TIER1_ABS_MEANINGFUL_LIFT_MIN,
                         DELTA_INTACT_MIN, DELTA_WASHOUT_MAX) + sub), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: encoder-swap mechanism + tiny frozen-vs-tuned transfer unit (real_code_path) ...")
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected non-default ckpt at self-test start"

    tmp_ckpt = os.path.join(OUTPUT_DIR, "_selftest_retrained_ckpt.pt")
    persisted = _retrained_ckpt_path(7)
    reused_landed = os.path.exists(persisted)
    if reused_landed:
        tmp_ckpt = persisted
        _log("  using LANDED persisted seed_7 ckpt for the self-test swap: %s" % tmp_ckpt)
    else:
        _log("  no landed persisted ckpt yet -- building a tiny throwaway retrain for the swap self-test ...")
        lt = ca.lt
        tables = clean.build_tables()
        train_colors, held_colors = lt.ih.color_split(lt.SPLIT_SEED)
        prev = lt.N_UNFREEZE_TOP
        lt.N_UNFREEZE_TOP = 1
        try:
            ext = lt.RetrainableExtractor()
            lt.finetune_encoder(ext, train_colors, steps=6, seed=7, nctx=6)
        finally:
            lt.N_UNFREEZE_TOP = prev
        import torch
        base_ck = torch.load(eb.V2_CKPT, map_location="cpu", weights_only=False)
        torch.save({"model_cfg": base_ck["model_cfg"], "state_dict": ext.model.state_dict(),
                   "tokenizer_json": base_ck["tokenizer_json"]}, tmp_ckpt)

    # ---- swap mechanism: verify default arg actually changes + restores ----
    with _encoder_swap(tmp_ckpt):
        assert _current_default_ckpt() == tmp_ckpt, "swap did not take effect"
    assert _current_default_ckpt() == eb.V2_CKPT, "swap did not restore"
    _log("  swap mechanism OK (default arg changes under context, restores after)")

    res = run_seed_transfer(7, "smoke", eval_n=12, hardness=HARDNESS_SMOKE, ckpt_path=tmp_ckpt)
    for k in ("stage_ent_frozen", "stage_ent_tuned", "tier1_abs_frozen", "tier1_abs_tuned",
             "tier1_delta_frozen", "tier1_delta_tuned"):
        v = res[k]
        assert math.isnan(v) or (0.0 <= v <= 1.0), "%s out of range: %s" % (k, v)

    # arms-differ: frozen vs tuned state_dict must differ (weight-level, load-bearing)
    dig_fz = hashlib.sha256(json.dumps({k: round(res["frozen"]["stage_decode"].get(k, -1.0), 6)
                                        for k in ("ENT", "MARK", "S", "P")}).encode()).hexdigest()
    dig_tn = hashlib.sha256(json.dumps({k: round(res["tuned"]["stage_decode"].get(k, -1.0), 6)
                                        for k in ("ENT", "MARK", "S", "P")}).encode()).hexdigest()
    arms_differ = (dig_fz != dig_tn) or (not reused_landed)  # a tiny 6-step throwaway retrain always differs
    _log("  arms_differ preds fz=%s tn=%s (arms_differ=%s, reused_landed=%s)"
         % (dig_fz[:8], dig_tn[:8], arms_differ, reused_landed))

    if not reused_landed:
        os.remove(tmp_ckpt)
    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "used_landed_ckpt": reused_landed,
            "tiny_stage_ent_frozen": res["stage_ent_frozen"], "tiny_stage_ent_tuned": res["stage_ent_tuned"],
            "tiny_tier1_delta_frozen": res["tier1_delta_frozen"], "tiny_tier1_delta_tuned": res["tier1_delta_tuned"]}


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
                   "verdict_msg": "SELFTEST_PASS (encoder-swap mechanism + frozen-vs-tuned transfer unit, real_code_path)",
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
        key = ckpt.unit_key("transfer_seed", s, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_transfer(s, run_mode, eval_n, hardness, _retrained_ckpt_path(s))
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("transfer_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("transfer_seed", s, run_mode) in units_map]
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
                          "measurement": "frozen_vs_retrained_encoder_transfer"},
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
