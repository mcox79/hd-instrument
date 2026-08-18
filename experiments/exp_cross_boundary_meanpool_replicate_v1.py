"""CELL: cross_boundary_meanpool_replicate_v1 -- LIGHTWEIGHT VET (seed-replication of an
INCIDENTAL positive found while authoring exp_entity_slot_gate_cross_boundary_v1). NOT a new
mechanism -- reuses the EXISTING calibration-validated CROSS_BOUNDARY instrument
(experiments.diag_order_critical_comprehension_calib_v1.gen_cross_boundary + score_readout_arm +
fit_binary_probe, UNCHANGED) on FROZEN encoders, EVAL-ONLY (no training/retraining of any
encoder; the only fit is the standard linear probe already used by every arm in this instrument
family). Adds ONE new readout ARM (CLAUSE_SPLIT_CONCAT = concat of the two clause-level
MEAN_POOL vectors, reusing compute_hidden_cache/readout_mean_pool verbatim -- no new learned
architecture, unlike EntitySlotGate) and TWO more units (RELOBJ_v3 seed_13, BASELINE_v2 seed_7)
against the ONE unit already measured (RELOBJ_v3 seed_7).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test MEAN_POOL vs CLAUSE_SPLIT_CONCAT
#   feature vectors per unit) -- YES
# - final_metrics_atomicity declared (META_RULE_AH; per_iter_paths via _seed_checkpoint
#   write_partial per unit + tmp_replace on the final aggregate)
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- YES
# - crlb_floor_computed: crlb_n/a -- accuracy-margin discriminator over a binary linear probe
#   (coherent-vs-scrambled), not a capacity/noise regime; no CRLB formula applies
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- MEAN_POOL coherent_acc on
#   RELOBJ_v3 seed_7 MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/
#   results.json:own_encoder_results.RELOBJ_v3.CROSS_BOUNDARY.per_readout.MEAN_POOL.coherent_acc
#   (well inside 0.05-0.95; exact value re-verified at smoke)
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm) -- smoke runs the
#   construction at FULL scale (train=1800/eval_per_label=300, IDENTICAL to FULL_CFG,
#   DISCRIMINATOR-MUST-SURVIVE-SCALE Option A), ONE unit (RELOBJ_v3 seed_7 reproduction) to prove
#   the +0.21 MEASURED margin reproduces before spending the other 3 units' wall time.
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- REPLICATE_MARGIN_THRESH=0.15
#   is the SAME MARGIN_THRESH the base instrument already uses as its known-reader calibration
#   bar (not a new invented number); measured seed_7 margin ~0.21-0.28 range clears it comfortably
# - HP_SCOPE per-arm declaration -- see prereg; RANDOM_INIT_ENCODER unit is a CONTROL (must NOT
#   clear REPLICATE_MARGIN_THRESH) not a HARD_PASS candidate
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate) -- YES (4 units:
#   RELOBJ_v3_seed_7 repro, RELOBJ_v3_seed_13 replication, BASELINE_v2_seed_7 objective-
#   independence check, RANDOM_INIT_ENCODER structure-alone control)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- YES
# - calibration_check field (META_RULE_M) -- adaptive_with_discriminator_gate: this cell RE-RUNS
#   the calibration gate itself (own function, mirrors exp_entity_slot_gate_cross_boundary_v1's
#   run_calibration_gate; NOT imported cross-cell to avoid pulling that cell's heavy
#   hdlab.entity_slot_gate transitive dependency onto a script that does not need it) and ABORTS
#   (CALIBRATION_GATE_FAIL) before touching any frozen encoder if no known reader clears it
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
#   (META_RULE_AC) -- see WHY section below
# - compute architecture: (b) sequential-CPU with justification -- 4 small frozen-encoder eval
#   passes (batched internally at encode_batch=256 via compute_hidden_cache); no GPU speedup
#   available on remote_cpu_queue (CPU-only runner, by task constraint: do not contend the GPU
#   breadth run). This CELL reuses the calibration instrument's existing forward-pass machinery
#   unchanged, not a new heavy sweep.
# - storage strategy: no_storage / no_composition (pure eval scoring; no substrate memory writes)

WHY: exp_entity_slot_gate_cross_boundary_v1.py's docstring records ONE single-seed measurement --
RELOBJ_v3 seed_7 MEAN_POOL margin=+0.2083 on CROSS_BOUNDARY
(MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json:
own_encoder_results.RELOBJ_v3.CROSS_BOUNDARY.per_readout.MEAN_POOL.margin). Director's spawn
context additionally cites a MEAN_POOL margin of +0.21 and a CLAUSE_SPLIT_CONCAT margin of +0.24,
both tagged HYPOTHESIZED@director-spawn-context (CLAUSE_SPLIT_CONCAT does not exist as code
anywhere in this repo -- grep-verified across experiments/*.py and notes/*.md before authoring;
this cell IMPLEMENTS it for the first time as a mechanical concat of two already-existing
MEAN_POOL calls, not a new learned mechanism). This session's standing discipline
(seed-luck over-read caught 2026-07-28: entity-state MEAN_POOL margin collapsed +0.283 seed_7 ->
+0.130 seed_13) means the CROSS_BOUNDARY seed_7 number MUST NOT be trusted until it replicates on
seed_13. This cell is EXACTLY that replication check, run on the SAME instrument, EVAL-ONLY.

CONSTRUCTION: experiments.diag_order_critical_comprehension_calib_v1.gen_cross_boundary,
UNCHANGED (calibration-validated v4: BGE_SMALL MEAN_POOL coherent=0.7483 scrambled=0.4883
margin=+0.2600 z-sig -- MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/
results.json:calibration_results.BGE_SMALL.CROSS_BOUNDARY.per_readout.MEAN_POOL). Calibration gate
is RE-RUN at dispatch time (not trusted from cache) per the standing discipline that a dispatched
cell must be self-contained/reproducible on remote.

Run modes:
  --self-test : tiny REAL-code-path pass (train_target=40, eval_target_per_label=20) on
                RELOBJ_v3 seed_7 only -- constructs the ACTUAL substrate objects
                (gen_cross_boundary, load_frozen_encoder/TinyTransformer, compute_hidden_cache,
                fit_binary_probe) at tiny scale, not a synthetic-only branch (Gate F.1).
                Calibration gate is COMPUTED but NOT hard-blocking at this scale.
  --smoke     : FULL-scale construction (train=1800, eval_per_label=300 -- IDENTICAL to FULL_CFG,
                DISCRIMINATOR-MUST-SURVIVE-SCALE Option A) but ONE unit (RELOBJ_v3 seed_7
                reproduction). Calibration gate IS enforced (this is the real construction).
  --full      : ALL 4 units (RELOBJ_v3 seed_7, RELOBJ_v3 seed_13, BASELINE_v2 seed_7,
                RANDOM_INIT_ENCODER control).
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
    gen_cross_boundary, CALIBRATION_MODELS, _raw_hf_encode, score_readout_arm, fit_binary_probe,
    MARGIN_THRESH, COHERENT_FLOOR,
)
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402  (_scramble_words)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from experiments.diag_comprehension_readout_sweep_v1 import compute_hidden_cache, readout_mean_pool  # noqa: E402
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, resumable_seeds,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "cross_boundary_meanpool_replicate_v1"

CKPT_RELOBJ_V3_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")
CKPT_RELOBJ_V3_SEED13 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_13.pt")
CKPT_BASELINE_V2_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")

SEED = 20260728          # construction RNG seed -- MATCHES diag_order_critical_comprehension_calib_v1.SEED
                          # (identical split/items every run mode; only train_target/eval_target scale down)

# unit key -> (ckpt_path, random_init_encoder). RANDOM_INIT_ENCODER reuses RELOBJ_v3 seed_7's
# tokenizer/spec/architecture (mc) but discards the trained weights (fresh nn.Module init) --
# same pattern as exp_entity_slot_gate_cross_boundary_v1.py's informational control.
UNIT_SPECS_FULL = [
    ("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False),
    ("RELOBJ_v3_seed_13", CKPT_RELOBJ_V3_SEED13, False),
    ("BASELINE_v2_seed_7", CKPT_BASELINE_V2_SEED7, False),
    ("RANDOM_INIT_ENCODER", CKPT_RELOBJ_V3_SEED7, True),
]
UNIT_SPECS_SMOKE = [("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False)]
UNIT_SPECS_SELFTEST = [("RELOBJ_v3_seed_7", CKPT_RELOBJ_V3_SEED7, False)]

SELFTEST_CFG = dict(run_mode="selftest", train_target=40, eval_target_per_label=20,
                     units=UNIT_SPECS_SELFTEST, enforce_calibration=False)
SMOKE_CFG = dict(run_mode="smoke", train_target=1800, eval_target_per_label=300,
                  units=UNIT_SPECS_SMOKE, enforce_calibration=True)
FULL_CFG = dict(run_mode="full", train_target=1800, eval_target_per_label=300,
                 units=UNIT_SPECS_FULL, enforce_calibration=True)

REPLICATE_MARGIN_THRESH = MARGIN_THRESH   # 0.15 -- SAME bar the base instrument's known readers must clear
COLLAPSE_RATIO = 0.5                      # seed_13 margin < 0.5 * seed_7 margin => collapse-pattern flag


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics / logging (per exp_dev.md SS13)
# ---------------------------------------------------------------------------
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


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)   # SS17: flush=True on every progress line


# ---------------------------------------------------------------------------
# Calibration gate (re-run at dispatch time; mirrors exp_entity_slot_gate_cross_boundary_v1's
# run_calibration_gate but NOT imported cross-cell -- avoids pulling that cell's heavy
# hdlab.entity_slot_gate transitive dependency onto this eval-only script).
# ---------------------------------------------------------------------------
def run_calibration_gate(construction, hb=None):
    train_sents = [it["sent"] for it in construction["train"]]
    eval_sents = [it["sent"] for it in construction["eval"]]
    y_train = np.array([it["label"] for it in construction["train"]], dtype=np.int64)
    y_eval = np.array([it["label"] for it in construction["eval"]], dtype=np.int64)
    srng = np.random.default_rng(SEED + 1234)
    eval_scr_sents = [LOOP2._scramble_words(it["sent"], srng) for it in construction["eval"]]

    per_model = {}
    any_pass = False
    for model_name, short in CALIBRATION_MODELS:
        G_tr = _raw_hf_encode(model_name, train_sents)
        G_ec = _raw_hf_encode(model_name, eval_sents)
        G_es = _raw_hf_encode(model_name, eval_scr_sents)
        per_readout = {}
        for rn in ("MEAN_POOL", "CLS_TOKEN", "LAST_TOKEN"):
            res = score_readout_arm(rn, G_tr[rn], y_train, G_ec[rn], G_es[rn], y_eval, SEED)
            per_readout[rn] = res
            if res["comprehension_specific"]:
                any_pass = True
        per_model[short] = per_readout
        _log("calibration %s: %s" % (short, {k: round(v["margin"], 4) for k, v in per_readout.items()}))
        if hb:
            hb.tick(0, extra={"stage": "calibration", "model": short}, force=True)
    return dict(per_model=per_model, calibration_pass=any_pass), eval_scr_sents


# ---------------------------------------------------------------------------
# Readout helpers (reuse verbatim: compute_hidden_cache / readout_mean_pool)
# ---------------------------------------------------------------------------
def _whole_sent_meanpool(model, tok, spec, sents):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H, M, _ = compute_hidden_cache(model, tok, spec, sents, ecfg, device)
    return readout_mean_pool(H, M)


def _clause_meanpools(model, tok, spec, clause1_texts, clause2_texts):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H1, M1, _ = compute_hidden_cache(model, tok, spec, clause1_texts, ecfg, device)
    H2, M2, _ = compute_hidden_cache(model, tok, spec, clause2_texts, ecfg, device)
    return readout_mean_pool(H1, M1), readout_mean_pool(H2, M2)


def _scramble_clause_texts(items, seed):
    srng = np.random.default_rng(seed)
    c1s = [LOOP2._scramble_words(it["clause1"], srng) for it in items]
    c2s = [LOOP2._scramble_words(it["clause2"], srng) for it in items]
    return c1s, c2s


# ---------------------------------------------------------------------------
# arms-must-differ (META_RULE_AF)
# ---------------------------------------------------------------------------
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
# One unit: MEAN_POOL (matched-plain-readout) + CLAUSE_SPLIT_CONCAT (new arm, mechanical concat
# of two existing MEAN_POOL calls, no new learned mechanism).
# ---------------------------------------------------------------------------
def run_one_unit(unit_key, ckpt_path, random_init, construction, eval_scr_sents_wholesent):
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError("frozen checkpoint not found: %s" % ckpt_path)
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)

    if random_init:
        mc = ckpt_meta["model_cfg"]
        torch.manual_seed(SEED + 999)
        model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                 mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
        model.eval()
        for p in model.parameters():
            p.requires_grad_(False)
        # ckpt_meta.seed/w_star are the DONOR ckpt's (RELOBJ_v3 seed_7) -- keep for provenance but
        # flag random_init so downstream readers don't mistake this for a trained-encoder result.
        ckpt_meta = dict(ckpt_meta, random_init=True, donor_ckpt=ckpt_path)
    else:
        ckpt_meta = dict(ckpt_meta, random_init=False)

    train_items = construction["train"]
    eval_items = construction["eval"]
    y_train_np = np.array([it["label"] for it in train_items], dtype=np.int64)
    y_eval_np = np.array([it["label"] for it in eval_items], dtype=np.int64)

    train_sents = [it["sent"] for it in train_items]
    eval_sents = [it["sent"] for it in eval_items]

    # ---- MEAN_POOL: whole-sentence forward pass (matches the base instrument's matched readout) ----
    G_tr = _whole_sent_meanpool(model, tok, spec, train_sents)
    G_ec = _whole_sent_meanpool(model, tok, spec, eval_sents)
    G_es = _whole_sent_meanpool(model, tok, spec, eval_scr_sents_wholesent)
    meanpool_res = score_readout_arm("MEAN_POOL", G_tr, y_train_np, G_ec, G_es, y_eval_np, SEED)

    # ---- CLAUSE_SPLIT_CONCAT: concat(meanpool(clause1), meanpool(clause2)) -- new readout arm,
    # mechanical concat of two existing calls, NOT a new learned mechanism. ----
    c1_tr, c2_tr = _clause_meanpools(model, tok, spec, [it["clause1"] for it in train_items],
                                      [it["clause2"] for it in train_items])
    c1_ec, c2_ec = _clause_meanpools(model, tok, spec, [it["clause1"] for it in eval_items],
                                      [it["clause2"] for it in eval_items])
    c1_scr, c2_scr = _scramble_clause_texts(eval_items, SEED + 5555)
    c1_es, c2_es = _clause_meanpools(model, tok, spec, c1_scr, c2_scr)

    F_tr = np.concatenate([c1_tr, c2_tr], axis=1)
    F_ec = np.concatenate([c1_ec, c2_ec], axis=1)
    F_es = np.concatenate([c1_es, c2_es], axis=1)
    concat_res = score_readout_arm("CLAUSE_SPLIT_CONCAT", F_tr, y_train_np, F_ec, F_es, y_eval_np, SEED)

    arms_differ = _arms_must_differ_np({"MEAN_POOL": G_ec, "CLAUSE_SPLIT_CONCAT": F_ec})

    return dict(
        unit_key=unit_key, ckpt_path=ckpt_path, ckpt_meta=ckpt_meta, random_init=random_init,
        mean_pool=meanpool_res, clause_split_concat=concat_res,
        arms_differ_digests=arms_differ, failure_class=None,
    )


# ---------------------------------------------------------------------------
# Self-test assertions (Gate F.1)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_unit, calib):
    assert len(per_unit) == 1, "selftest expected exactly 1 unit"
    v = list(per_unit.values())[0]
    assert not v.get("failure_class"), "selftest unit crashed: %s: %s" % (v.get("failure_class"), v.get("error_msg"))
    for arm in ("mean_pool", "clause_split_concat"):
        m = v[arm]["margin"]
        assert -1.0 <= m <= 1.0, "margin out of range for %s: %s" % (arm, m)
    assert len(v["arms_differ_digests"]) == 2, "arms-must-differ digests missing"
    assert v["ckpt_meta"]["seed"] == 7, "self-test ckpt seed mismatch"
    assert isinstance(calib["calibration_pass"], bool), "calibration_pass not a bool"


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def build_verdict(per_unit, unit_keys, calib_pass, enforce_calibration):
    expected_n = len(unit_keys)
    got_n = len(per_unit)
    if enforce_calibration and not calib_pass:
        return ("CALIBRATION_GATE_FAIL",
                "No known reader (MiniLM/BGE_SMALL) cleared MARGIN_THRESH=%.2f / COHERENT_FLOOR=%.2f "
                "on CROSS_BOUNDARY at this regime -- construction is broken at this scale; own-encoder "
                "scoring is uninterpretable and was SKIPPED per the calibration-first rule."
                % (MARGIN_THRESH, COHERENT_FLOOR), False, expected_n, 0)
    if got_n != expected_n:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "expected %d units, got %d" % (expected_n, got_n), False, expected_n, got_n)

    any_failure = any(v.get("failure_class") for v in per_unit.values())
    if any_failure:
        return ("HARD_FAIL_UNIT_CRASH",
                "one or more units crashed: %s" % {k: v.get("failure_class") for k, v in per_unit.items()
                                                     if v.get("failure_class")},
                True, expected_n, got_n)

    if "RELOBJ_v3_seed_13" not in per_unit:
        # smoke / self-test: only the seed_7 reproduction ran; report reproduction status only.
        rep = per_unit.get("RELOBJ_v3_seed_7")
        m = rep["mean_pool"]["margin"] if rep else None
        return ("REPRODUCTION_ONLY",
                "seed_13 not in this run (smoke/self-test scope); RELOBJ_v3_seed_7 MEAN_POOL "
                "margin=%s (prior MEASURED=+0.2083). Full replication check requires --full."
                % (("%+.4f" % m) if m is not None else "N/A"),
                True, expected_n, got_n)

    seed7 = per_unit.get("RELOBJ_v3_seed_7")
    seed13 = per_unit["RELOBJ_v3_seed_13"]
    rand_ctrl = per_unit.get("RANDOM_INIT_ENCODER")
    baseline_v2 = per_unit.get("BASELINE_v2_seed_7")

    m13 = seed13["mean_pool"]["margin"]
    cs13 = seed13["mean_pool"]["comprehension_specific"]
    m7 = seed7["mean_pool"]["margin"] if seed7 else None
    m_rand = rand_ctrl["mean_pool"]["margin"] if rand_ctrl else None

    collapse_flag = (m7 is not None and m7 > 0 and m13 < COLLAPSE_RATIO * m7)
    structure_alone_flag = (m_rand is not None and m_rand >= REPLICATE_MARGIN_THRESH)

    replicates = bool(m13 >= REPLICATE_MARGIN_THRESH and cs13 and not structure_alone_flag)

    gains = dict(
        RELOBJ_v3_seed_7_MEAN_POOL_margin=m7,
        RELOBJ_v3_seed_13_MEAN_POOL_margin=m13,
        RELOBJ_v3_seed_13_CLAUSE_SPLIT_CONCAT_margin=seed13["clause_split_concat"]["margin"],
        RANDOM_INIT_ENCODER_MEAN_POOL_margin=m_rand,
        BASELINE_v2_seed_7_MEAN_POOL_margin=(baseline_v2["mean_pool"]["margin"] if baseline_v2 else None),
    )

    if structure_alone_flag:
        verdict = "STRUCTURE_ALONE_CONFOUND"
        msg = ("RANDOM_INIT_ENCODER (untrained TinyTransformer, same architecture as RELOBJ_v3) "
               "MEAN_POOL margin=%+.4f already clears REPLICATE_MARGIN_THRESH=%.2f -- the seed_13 "
               "signal (margin=%+.4f) cannot be attributed to LEARNED structure; matches this "
               "session's prior finding (random-init beat trained on ENTITY_STATE). Per-unit "
               "margins: %s" % (m_rand, REPLICATE_MARGIN_THRESH, m13, gains))
    elif replicates:
        verdict = "REPLICATES"
        msg = ("RELOBJ_v3 seed_13 MEAN_POOL margin=%+.4f clears REPLICATE_MARGIN_THRESH=%.2f "
               "(comprehension_specific=%s), scrambled control intact, RANDOM_INIT_ENCODER does "
               "NOT match (margin=%s). seed_7 reproduction margin=%s. Per-unit margins: %s"
               % (m13, REPLICATE_MARGIN_THRESH, cs13, ("%+.4f" % m_rand) if m_rand is not None else "N/A",
                  ("%+.4f" % m7) if m7 is not None else "N/A", gains))
    elif collapse_flag:
        verdict = "FAILS_TO_REPLICATE"
        msg = ("RELOBJ_v3 seed_13 MEAN_POOL margin=%+.4f is < %.0f%% of seed_7's %+.4f -- the SAME "
               "collapse pattern as ENTITY_STATE (+0.283 seed_7 -> +0.130 seed_13). seed_7 was "
               "SEED-LUCK, not a genuine cross-boundary tracking signal. Per-unit margins: %s"
               % (m13, COLLAPSE_RATIO * 100, m7, gains))
    else:
        verdict = "FAILS_TO_REPLICATE"
        msg = ("RELOBJ_v3 seed_13 MEAN_POOL margin=%+.4f does not clear REPLICATE_MARGIN_THRESH=%.2f "
               "(comprehension_specific=%s). Per-unit margins: %s"
               % (m13, REPLICATE_MARGIN_THRESH, cs13, gains))

    return verdict, msg, True, expected_n, got_n


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
    unit_specs = cfg["units"]
    unit_keys = [u[0] for u in unit_specs]
    unit_lookup = {u[0]: (u[1], u[2]) for u in unit_specs}

    _write_start_marker(out_dir, cfg["run_mode"], len(unit_keys))
    _log("run_mode=%s n_units=%d units=%s train_target=%d eval_per_label=%d"
         % (cfg["run_mode"], len(unit_keys), unit_keys, cfg["train_target"], cfg["eval_target_per_label"]))

    t_wall0 = time.perf_counter()
    with CellHeartbeat(out_dir, total_units=len(unit_keys) + 1, interval_s=30) as hb:
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
            _, remaining = resumable_seeds(unit_keys, out_dir, run_config=dict(run_mode=cfg["run_mode"]))
            remaining_units = [k for k in unit_keys if k in set(remaining)]
            for i, key in enumerate(remaining_units):
                ckpt_path, random_init = unit_lookup[key]
                t0 = time.perf_counter()
                try:
                    res = run_one_unit(key, ckpt_path, random_init, construction, eval_scr_sents_wholesent)
                    res["elapsed_s"] = time.perf_counter() - t0
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                    res = dict(unit_key=key, failure_class=type(e).__name__, error_msg=str(e)[:500],
                              elapsed_s=time.perf_counter() - t0)
                    _log("UNIT FAILED unit=%s: %s: %s" % (key, type(e).__name__, e))
                write_partial(out_dir, key, res)
                mp_margin = res.get("mean_pool", {}).get("margin") if not res.get("failure_class") else None
                _log("unit=%s done in %.1fs mean_pool_margin=%s" %
                    (key, res["elapsed_s"], ("%+.4f" % mp_margin) if mp_margin is not None else "FAILED"))
                hb.tick(2 + i, extra={"unit": key}, force=True)
            per_unit = aggregate_partials(out_dir, unit_keys)
        else:
            _log("CALIBRATION_GATE_FAIL -- skipping own-encoder scoring entirely (uninterpretable "
                 "against a broken instrument at this regime)")

    verdict, vmsg, cardinality_ok, expected_n, got_n = build_verdict(
        per_unit, unit_keys, calib["calibration_pass"], cfg["enforce_calibration"])
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg, anchor_name=ANCHOR_NAME,
        run_mode=cfg["run_mode"], ts_iso=datetime.now(timezone.utc).isoformat(),
        device="cpu", cuda=False, n_units=len(per_unit),
        per_unit=per_unit, cardinality_ok=cardinality_ok,
        expected_n_units=expected_n, got_n_units=got_n,
        calibration=calib, calibration_enforced=cfg["enforce_calibration"],
        bands=dict(replicate_margin_thresh=REPLICATE_MARGIN_THRESH, collapse_ratio=COLLAPSE_RATIO,
                  margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR),
        hp_scope=dict(replication_units=["RELOBJ_v3_seed_13"],
                     reproduction_units=["RELOBJ_v3_seed_7"],
                     objective_independence_units=["BASELINE_v2_seed_7"],
                     structure_alone_control=["RANDOM_INIT_ENCODER"]),
        cfg=dict(cfg, units=unit_keys), elapsed_s_total=time.perf_counter() - t_wall0,
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
