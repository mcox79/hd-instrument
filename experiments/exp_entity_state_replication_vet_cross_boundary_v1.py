"""CELL: entity_state_replication_vet_cross_boundary_v1 (2026-07-29) -- RE-DISPATCH.

A prior attempt at this same replication question died with the Claude process exiting
overnight; nothing shipped, nothing committed. This is a fresh start.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test over per-unit eval-coherent
#   feature arrays: MEAN_POOL / CLAUSE_SPLIT_CONCAT / RANDOM_INIT_ENCODER) -- YES
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace, single-shot run)
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- YES
# - crlb_floor_computed + discriminator_reachability -- crlb_n/a (accuracy-margin discriminator
#   over a binary probe, not a capacity/noise regime; see prereg)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- MEAN_POOL coherent_acc
#   MEASURED 0.63-0.75 across the 2026-07-28 cell's calibration + seed_7 own-encoder runs on this
#   SAME construction, comfortably inside band
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm) -- runs the
#   construction at FULL scale (train=1800/eval=300-per-label) for every unit, no smaller regime
# - HARD_PASS ("REPLICATES") strictly above floor + 5% band-width (META_RULE_L) -- threshold 0.15
#   sits inside the measured 0.13-0.28 range this construction/family has produced to date
# - HP_SCOPE per-arm declaration -- see prereg (only RELOBJ_v3_seed_13 gates the verdict)
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS=3, fixed list) -- YES
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- YES
# - calibration_check field (META_RULE_M) -- adaptive_with_discriminator_gate: RE-RUNS the
#   CROSS_BOUNDARY calibration gate itself at dispatch time (imported verbatim, not
#   reimplemented); ABORTS (CALIBRATION_GATE_FAIL) before touching any frozen encoder if no known
#   reader clears it at this exact regime
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - cell_chunked: false -- EXEMPTION per exp_dev.md SS13A: lightweight (<10min), CPU-only,
#   EVAL-ONLY cell; per-unit write_partial/resumable_seeds (same precedent as the immediately-prior
#   exp_entity_slot_gate_cross_boundary_v1.py) gives runner-death resilience without physically
#   separate seed-files for a sub-10-minute run

WHY / QUESTION: does the frozen RELOBJ_v3 encoder's cross-boundary entity-tracking MEAN_POOL
margin (seed_7 measured +0.2083/+0.21 on `gen_cross_boundary`,
MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json and
MEASURED@d:/AI/hd-instrument/data/exp_entity_slot_gate_cross_boundary_v1_smoke/metrics.json)
REPLICATE at seed_13, or collapse the way the OLDER `gen_entity_state` construction did
(seed_7 +0.283 -> seed_13 +0.130)? Also: is any signal objective-independent (v2 MLM baseline,
seed_7)? See preregs/2026-07-29_entity_state_replication_vet_cross_boundary_v1.md for the full
band definitions + HP_SCOPE + prior-work check.

NO retrain. NO new mechanism -- `hdlab/entity_slot_gate.py` is NOT touched by this cell. Pure
EVAL-ONLY read of existing FROZEN encoders through the EXISTING calibration-validated
`gen_cross_boundary` construction, reusing the SAME readout/probe/calibration machinery as
`experiments/exp_entity_slot_gate_cross_boundary_v1.py` and
`experiments/diag_order_critical_comprehension_calib_v1.py`.

Run modes:
  --self-test : tiny REAL-code-path pass (train_target=40, eval_target_per_label=20) on ONE unit
                (RELOBJ_v3_seed_7) -- constructs the ACTUAL substrate objects (gen_cross_boundary,
                load_frozen_encoder/TinyTransformer, compute_hidden_cache, fit_binary_probe) at
                tiny scale (Gate F.1). Calibration gate COMPUTED but not hard-blocking at this
                scale.
  --smoke     : FULL-scale construction (train=1800, eval_per_label=300 -- IDENTICAL to --full)
                but ONE unit (RELOBJ_v3_seed_7, the within-run reproduction check) --
                DISCRIMINATOR-MUST-SURVIVE-SCALE Option A. Calibration gate IS enforced.
  --full      : ALL 3 units (RELOBJ_v3_seed_13 [gating], RELOBJ_v3_seed_7 [informational],
                BASELINE_v2_seed_7 [informational]).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.diag_order_critical_comprehension_calib_v1 import (  # noqa: E402
    gen_cross_boundary, score_readout_arm, MARGIN_THRESH, COHERENT_FLOOR,
)
from experiments.exp_entity_slot_gate_cross_boundary_v1 import run_calibration_gate  # noqa: E402
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402  (_scramble_words)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from experiments.diag_comprehension_readout_sweep_v1 import compute_hidden_cache, readout_mean_pool  # noqa: E402
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, resumable_seeds,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "entity_state_replication_vet_cross_boundary_v1"

CKPT_RELOBJ_V3_SEED13 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_13.pt")
CKPT_RELOBJ_V3_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")
CKPT_BASELINE_V2_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")

# unit_key -> (ckpt_path, gates_verdict)
UNITS_FULL = [
    ("RELOBJ_v3_seed_13", CKPT_RELOBJ_V3_SEED13, True),
    ("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False),
    ("BASELINE_v2_seed_7", CKPT_BASELINE_V2_SEED7, False),
]
UNITS_SMOKE = [("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False)]
UNITS_SELFTEST = [("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False)]

SEED = 20260728   # MATCHES diag_order_critical_comprehension_calib_v1.SEED (identical split/scramble)

SELFTEST_CFG = dict(run_mode="selftest", train_target=40, eval_target_per_label=20,
                     units=UNITS_SELFTEST, enforce_calibration=False)
SMOKE_CFG = dict(run_mode="smoke", train_target=1800, eval_target_per_label=300,
                  units=UNITS_SMOKE, enforce_calibration=True)
FULL_CFG = dict(run_mode="full", train_target=1800, eval_target_per_label=300,
                 units=UNITS_FULL, enforce_calibration=True)

REPLICATES_THRESH = 0.15
FAILS_FLOOR = 0.05
FAILS_RATIO = 0.5          # seed_13 <= 0.5 * seed_7 => proportional collapse (mirrors 0.130/0.283=0.46)
RANDOM_GATE_EPS = 0.02      # random-init-encoder control must trail trained margin by >= this


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Clause / whole-sentence encoding helpers (mirrors exp_entity_slot_gate_cross_boundary_v1)
# ---------------------------------------------------------------------------
def _full_sent_meanpool(model, tok, spec, sents):
    device = torch.device("cpu")
    cfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H, M, _ = compute_hidden_cache(model, tok, spec, sents, cfg, device)
    return readout_mean_pool(H, M)


def _clause_meanpools(model, tok, spec, clause1_texts, clause2_texts):
    device = torch.device("cpu")
    cfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H1, M1, _ = compute_hidden_cache(model, tok, spec, clause1_texts, cfg, device)
    H2, M2, _ = compute_hidden_cache(model, tok, spec, clause2_texts, cfg, device)
    return readout_mean_pool(H1, M1), readout_mean_pool(H2, M2)


def _unit_norm(x):
    n = np.linalg.norm(x, axis=1, keepdims=True)
    return x / np.clip(n, 1e-8, None)


def _clause_split_concat(g1, g2):
    return np.concatenate([_unit_norm(g1), _unit_norm(g2)], axis=1).astype(np.float32)


def _scramble_clause_texts(items, seed):
    srng = np.random.default_rng(seed)
    c1s = [LOOP2._scramble_words(it["clause1"], srng) for it in items]
    c2s = [LOOP2._scramble_words(it["clause2"], srng) for it in items]
    return c1s, c2s


def _arms_must_differ_np(arms):
    import hashlib
    digests = {}
    for name, arr in arms.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    return digests


# ---------------------------------------------------------------------------
# One unit: MEAN_POOL (gating readout) + CLAUSE_SPLIT_CONCAT (informational) +
# RANDOM_INIT_ENCODER MEAN_POOL (mandatory structure-alone control)
# ---------------------------------------------------------------------------
def run_one_unit(unit_key, ckpt_path, construction, eval_scr_sents_wholesent):
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError("frozen checkpoint not found: %s" % ckpt_path)
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)

    train_items = construction["train"]
    eval_items = construction["eval"]
    y_train_np = np.array([it["label"] for it in train_items], dtype=np.int64)
    y_eval_np = np.array([it["label"] for it in eval_items], dtype=np.int64)

    train_sents = [it["sent"] for it in train_items]
    eval_sents = [it["sent"] for it in eval_items]

    # ---- MEAN_POOL (gating readout) ----
    G_tr = _full_sent_meanpool(model, tok, spec, train_sents)
    G_ec = _full_sent_meanpool(model, tok, spec, eval_sents)
    G_es = _full_sent_meanpool(model, tok, spec, eval_scr_sents_wholesent)
    meanpool_res = score_readout_arm("MEAN_POOL", G_tr, y_train_np, G_ec, G_es, y_eval_np, SEED)

    # ---- CLAUSE_SPLIT_CONCAT (informational) ----
    h1_tr, h2_tr = _clause_meanpools(model, tok, spec, [it["clause1"] for it in train_items],
                                      [it["clause2"] for it in train_items])
    h1_ec, h2_ec = _clause_meanpools(model, tok, spec, [it["clause1"] for it in eval_items],
                                      [it["clause2"] for it in eval_items])
    c1_scr, c2_scr = _scramble_clause_texts(eval_items, SEED + 5555)
    h1_es, h2_es = _clause_meanpools(model, tok, spec, c1_scr, c2_scr)
    F_tr = _clause_split_concat(h1_tr, h2_tr)
    F_ec = _clause_split_concat(h1_ec, h2_ec)
    F_es = _clause_split_concat(h1_es, h2_es)
    clause_split_res = score_readout_arm("CLAUSE_SPLIT_CONCAT", F_tr, y_train_np, F_ec, F_es, y_eval_np, SEED)

    # ---- RANDOM_INIT_ENCODER MEAN_POOL (mandatory structure-alone control) ----
    mc = ckpt_meta["model_cfg"]
    torch.manual_seed(SEED + 999)
    rand_model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                  mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    rand_model.eval()
    for p in rand_model.parameters():
        p.requires_grad_(False)
    R_tr = _full_sent_meanpool(rand_model, tok, spec, train_sents)
    R_ec = _full_sent_meanpool(rand_model, tok, spec, eval_sents)
    R_es = _full_sent_meanpool(rand_model, tok, spec, eval_scr_sents_wholesent)
    random_init_res = score_readout_arm("RANDOM_INIT_ENCODER", R_tr, y_train_np, R_ec, R_es, y_eval_np, SEED)

    arms_differ = _arms_must_differ_np({
        "MEAN_POOL": G_ec, "CLAUSE_SPLIT_CONCAT": F_ec, "RANDOM_INIT_ENCODER": R_ec,
    })

    trained_margin = meanpool_res["margin"]
    random_margin = random_init_res["margin"]
    structure_alone = bool(random_margin >= trained_margin - RANDOM_GATE_EPS)

    return dict(
        unit_key=unit_key, ckpt_path=ckpt_path, ckpt_meta=ckpt_meta,
        mean_pool=meanpool_res, clause_split_concat=clause_split_res,
        random_init_encoder=random_init_res,
        structure_alone=structure_alone, arms_differ_digests=arms_differ,
        failure_class=None,
    )


# ---------------------------------------------------------------------------
# Self-test assertions (Gate F.1)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_unit, calib):
    assert len(per_unit) == 1, "selftest expected exactly 1 unit"
    v = list(per_unit.values())[0]
    assert not v.get("failure_class"), "selftest unit crashed: %s: %s" % (v.get("failure_class"), v.get("error_msg"))
    for arm in ("mean_pool", "clause_split_concat", "random_init_encoder"):
        m = v[arm]["margin"]
        assert -1.0 <= m <= 1.0, "margin out of range for %s: %s" % (arm, m)
    assert len(v["arms_differ_digests"]) == 3, "arms-must-differ digests missing"
    assert isinstance(calib["calibration_pass"], bool), "calibration_pass not a bool"


# ---------------------------------------------------------------------------
# Verdict (only RELOBJ_v3_seed_13 gates; see HP_SCOPE in prereg)
# ---------------------------------------------------------------------------
def build_verdict(per_unit, units, calib_pass, enforce_calibration):
    expected_n = len(units)
    got_n = len(per_unit)
    if enforce_calibration and not calib_pass:
        return ("CALIBRATION_GATE_FAIL",
                "No known reader cleared MARGIN_THRESH=%.2f/COHERENT_FLOOR=%.2f on CROSS_BOUNDARY "
                "at this regime -- own-encoder scoring uninterpretable, SKIPPED." % (MARGIN_THRESH, COHERENT_FLOOR),
                False, expected_n, 0)
    if got_n != expected_n:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "expected %d units, got %d" % (expected_n, got_n), False, expected_n, got_n)

    any_failure = any(v.get("failure_class") for v in per_unit.values())
    if any_failure:
        return ("HARD_FAIL_UNIT_CRASH",
                "one or more units crashed: %s" % {k: v.get("failure_class") for k, v in per_unit.items()
                                                     if v.get("failure_class")},
                True, expected_n, got_n)

    gating_key = "RELOBJ_v3_seed_13"
    if gating_key not in per_unit:
        # smoke/self-test: gating unit not run this mode; report structurally, no verdict claim
        return ("NO_GATING_UNIT_THIS_RUN_MODE",
                "gating unit %s not included in this run_mode's unit list" % gating_key,
                True, expected_n, got_n)

    g = per_unit[gating_key]
    seed13_margin = g["mean_pool"]["margin"]
    seed13_spec = g["mean_pool"]["comprehension_specific"]
    seed7 = per_unit.get("RELOBJ_v3_seed_7")
    seed7_margin = seed7["mean_pool"]["margin"] if seed7 else None

    if g["structure_alone"]:
        return ("HARD_FAIL_STRUCTURE_ALONE",
                "RELOBJ_v3_seed_13 random-init-encoder control (margin=%.4f) matched/exceeded the "
                "trained MEAN_POOL margin (%.4f) minus eps=%.2f -- structure alone, not learned "
                "semantics." % (g["random_init_encoder"]["margin"], seed13_margin, RANDOM_GATE_EPS),
                True, expected_n, got_n)

    collapsed = (seed7_margin is not None and seed7_margin > 0
                 and seed13_margin <= FAILS_RATIO * seed7_margin)
    if seed13_margin < FAILS_FLOOR or collapsed:
        msg = ("FAILS_TO_REPLICATE: RELOBJ_v3_seed_13 MEAN_POOL margin=%.4f (comprehension_specific=%s)"
               % (seed13_margin, seed13_spec))
        if seed7_margin is not None:
            msg += (" vs RELOBJ_v3_seed_7=%.4f (ratio=%.2f, FAILS_RATIO=%.2f) -- mirrors the prior "
                     "ENTITY_STATE collapse (+0.130/+0.283=0.46)." % (
                         seed7_margin, (seed13_margin / seed7_margin) if seed7_margin else float("nan"),
                         FAILS_RATIO))
        return ("FAILS_TO_REPLICATE", msg, True, expected_n, got_n)

    if seed13_margin >= REPLICATES_THRESH and seed13_spec:
        msg = ("REPLICATES: RELOBJ_v3_seed_13 MEAN_POOL margin=%.4f >= REPLICATES_THRESH=%.2f, "
               "comprehension_specific=True, random-init-encoder control margin=%.4f trails by >=%.2f "
               "(not structure-alone)." % (seed13_margin, REPLICATES_THRESH,
                                           g["random_init_encoder"]["margin"], RANDOM_GATE_EPS))
        if seed7_margin is not None:
            msg += " RELOBJ_v3_seed_7 (within-run reproduction) margin=%.4f." % seed7_margin
        return ("REPLICATES", msg, True, expected_n, got_n)

    msg = ("MIDDLE_BAND: RELOBJ_v3_seed_13 MEAN_POOL margin=%.4f (comprehension_specific=%s) -- "
           "neither a clean REPLICATES (>=%.2f) nor a clean FAILS_TO_REPLICATE (<%.2f or collapse)."
           % (seed13_margin, seed13_spec, REPLICATES_THRESH, FAILS_FLOOR))
    if seed7_margin is not None:
        msg += " seed_7=%.4f." % seed7_margin
    return ("MIDDLE_BAND", msg, True, expected_n, got_n)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        cfg = SELFTEST_CFG
    elif args.smoke:
        cfg = SMOKE_CFG
    else:
        cfg = FULL_CFG

    out_dir = get_output_dir(ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    units = cfg["units"]

    _write_start_marker(out_dir, cfg["run_mode"], len(units))
    _log("run_mode=%s n_units=%d units=%s train_target=%d eval_per_label=%d"
         % (cfg["run_mode"], len(units), [u[0] for u in units], cfg["train_target"], cfg["eval_target_per_label"]))

    t_wall0 = time.perf_counter()
    with CellHeartbeat(out_dir, total_units=len(units) + 1, interval_s=30) as hb:
        rng = np.random.default_rng(SEED)
        construction = gen_cross_boundary(rng, train_target=cfg["train_target"],
                                          eval_target_per_label=cfg["eval_target_per_label"])
        assert construction["train_group_set"].isdisjoint(construction["eval_group_set"]), \
            "LEAK: CROSS_BOUNDARY train/eval group overlap"
        _log("construction built: train=%d eval=%d groups(train/eval)=%d/%d"
             % (len(construction["train"]), len(construction["eval"]),
                len(construction["train_group_set"]), len(construction["eval_group_set"])))
        hb.tick(0, extra={"stage": "construction"}, force=True)

        calib, eval_scr_sents_wholesent = run_calibration_gate(construction, hb=hb)
        _log("calibration_pass=%s" % calib["calibration_pass"])
        hb.tick(1, extra={"stage": "calibration_done"}, force=True)

        per_unit = {}
        if (not cfg["enforce_calibration"]) or calib["calibration_pass"]:
            unit_keys = [u[0] for u in units]
            ckpt_by_key = {u[0]: u[1] for u in units}
            _, remaining = resumable_seeds(unit_keys, out_dir, run_config=dict(run_mode=cfg["run_mode"]))
            remaining_keys = [k for k in unit_keys if k in set(remaining)]
            for i, key in enumerate(remaining_keys):
                t0 = time.perf_counter()
                try:
                    res = run_one_unit(key, ckpt_by_key[key], construction, eval_scr_sents_wholesent)
                    res["elapsed_s"] = time.perf_counter() - t0
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                    res = dict(unit_key=key, failure_class=type(e).__name__, error_msg=str(e)[:500],
                              elapsed_s=time.perf_counter() - t0)
                    _log("UNIT FAILED %s: %s: %s" % (key, type(e).__name__, e))
                write_partial(out_dir, key, res)
                _log("unit=%s done in %.1fs mean_pool_margin=%s"
                    % (key, res["elapsed_s"], (res.get("mean_pool") or {}).get("margin")))
                hb.tick(2 + i, extra={"unit": key}, force=True)
            per_unit = aggregate_partials(out_dir, unit_keys)
        else:
            _log("CALIBRATION_GATE_FAIL -- skipping own-encoder scoring entirely")

    verdict, vmsg, cardinality_ok, expected_n, got_n = build_verdict(
        per_unit, units, calib["calibration_pass"], cfg["enforce_calibration"])
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg, anchor_name=ANCHOR_NAME,
        run_mode=cfg["run_mode"], ts_iso=datetime.now(timezone.utc).isoformat(),
        device="cpu", cuda=False, n_units=len(per_unit),
        per_unit=per_unit, cardinality_ok=cardinality_ok,
        expected_n_units=expected_n, got_n_units=got_n,
        calibration=calib, calibration_enforced=cfg["enforce_calibration"],
        bands=dict(replicates_thresh=REPLICATES_THRESH, fails_floor=FAILS_FLOOR,
                  fails_ratio=FAILS_RATIO, random_gate_eps=RANDOM_GATE_EPS,
                  margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR),
        hp_scope=dict(applies_to=["RELOBJ_v3_seed_13"],
                     informational_only=["RELOBJ_v3_seed_7", "BASELINE_v2_seed_7",
                                         "clause_split_concat (all units)"]),
        cfg=dict(run_mode=cfg["run_mode"], train_target=cfg["train_target"],
                eval_target_per_label=cfg["eval_target_per_label"], units=[u[0] for u in units],
                enforce_calibration=cfg["enforce_calibration"]),
        elapsed_s_total=time.perf_counter() - t_wall0,
        construction_meta=dict(n_train=len(construction["train"]), n_eval=len(construction["eval"]),
                               n_train_groups=len(construction["train_group_set"]),
                               n_eval_groups=len(construction["eval_group_set"])),
    )
    write_metrics(out_dir, metrics, results=list(per_unit.values()))

    if args.self_test:
        _selftest_assertions(per_unit, calib)
        _log("SELF-TEST PASS")


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
