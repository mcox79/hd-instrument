"""CELL: entity_slot_gate_cross_boundary_v1 -- comprehension-frontier "design A" first can-fail
experiment (see notes/comprehension_situation_model_frontier_scoping.md "First can-fail
experiment"). ONE variable = mechanism/readout only; encoder/data/seeds/construction FIXED.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test over per-unit arm score vectors) -- YES
# - final_metrics_atomicity declared (META_RULE_AH; per_iter_paths -- write_partial per unit + tmp_replace final)
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- YES
# - crlb_floor_computed + discriminator_reachability -- crlb_n/a (accuracy-margin discriminator over
#   a binary probe, not a capacity/noise regime; see prereg)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- MEAN_POOL coherent_acc
#   MEASURED 0.6300-0.7517 across calibration models on this construction, well inside band
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm) -- smoke runs the
#   construction at FULL scale (train=1800/eval=300-per-label, IDENTICAL to FULL_CFG); only the
#   ckpt-seed count (1 vs 2) and gate-training epoch count differ smoke-vs-full (Option A)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- HARD_PASS_GAIN=0.05 vs measured
#   RELOBJ_v3/CROSS_BOUNDARY/MEAN_POOL margin ceiling ~0.21-0.28 range -> band width comfortably
#   clears the 5%-of-width floor test
# - HP_SCOPE per-arm declaration -- see prereg
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate) -- YES (2 units: seed_7, seed_13)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- YES
# - calibration_check field (META_RULE_M) -- adaptive_with_discriminator_gate: this cell RE-RUNS the
#   calibration gate itself (not a cached prior result) at whatever regime it is dispatched at, and
#   ABORTS (CALIBRATION_GATE_FAIL) before touching the frozen encoder if no known reader clears it
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)

WHY: notes/comprehension_situation_model_frontier_scoping.md "Candidate designs", design A
(RECOMMENDED FIRST): "Entity-slot scaffold + learned write-gate on the frozen encoder's OWN hidden
states. At each clause boundary a TRAINED small head reads the hidden state for a mention vs the
slot's content -> update-vs-keep + new value (learned decision). Write op reuses
hdlab/sequence_memory.SequenceMatrix." Implemented in `hdlab/entity_slot_gate.py`
(EntitySlotGate / fit_entity_slot_gate) -- see that module's docstring for the exact mechanism
(content-addressed slots, gated Hebbian write via SequenceMatrix.bind_pair, differentiable
prediction-error read). THE LINE: slot count / addressing scheme / write primitive / boundary
position are supplied STRUCTURE (allowed); WHICH slot to write and HOW MUCH are LEARNED decisions
(addr_net / gate_net trained by backprop), never a hand-coded referent/state resolver.

CONSTRUCTION: `experiments.diag_order_critical_comprehension_calib_v1.gen_cross_boundary`
(extended IN PLACE this session -- see that module for the CROSS_BOUNDARY construction docstring
+ the calibration-iteration history: v1-v3 wordings FAILED calibration, v4 -- split clause-1 into
two sentences + train=1800/eval_per_label=300 -- PASSES:
MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json:
calibration_results.BGE_SMALL.CROSS_BOUNDARY.per_readout.MEAN_POOL = {coherent_acc: 0.7517,
scrambled_acc: 0.5217, margin: +0.2300, comprehension_specific: true}). This cell RE-RUNS that
SAME calibration gate at dispatch time (not trusting the cached diag results.json) because a
dispatched cell must be self-contained/reproducible on remote.

REAL BASELINE (per the frontier note): RELOBJ_v3 MEAN_POOL on ENTITY_STATE was +0.283 seed7 /
+0.130 seed13 (the non-replicated positive motivating this whole track) --
MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1{,_seed13}/results.json.
On the NEW CROSS_BOUNDARY construction specifically, RELOBJ_v3 MEAN_POOL (seed_7) already measures
margin=+0.2083 (comprehension_specific=True) -- MEASURED@d:/AI/hd-instrument/data/
diag_order_critical_comprehension_calib_v1/results.json:own_encoder_results.RELOBJ_v3.
CROSS_BOUNDARY.per_readout.MEAN_POOL.margin. This cell's "matched plain readout" arm reproduces
that number per-unit (same construction, same ckpt, same split) as the comparison point the
SLOT_GATE mechanism must beat by >=0.05 (HARD_PASS gain) in BOTH seeds.

MANDATORY ablation (frontier note, non-negotiable): SLOT_GATE_RANDOM_GATE runs the IDENTICAL
EntitySlotGate structure with addr_net/gate_net left at random init (fit_entity_slot_gate(...,
random_init=True) -- zero optimizer steps). If this control's gain-over-MEAN_POOL matches or
exceeds the TRAINED gate's gain, HARD_FAIL (structure alone, not learning) -- this session's C-design
work already found random-init beating trained on entity-state once; this gate makes sure a repeat
cannot be missed. A SECOND, informational-only control (RANDOM_INIT_ENCODER) additionally swaps in
a random-init (never-fitted) TinyTransformer with the SAME architecture as RELOBJ_v3 (through a
TRAINED gate) -- isolates whether the ENCODER's learned semantics matter vs the untrained
transformer's structural biases; not part of the HARD_PASS/HARD_FAIL gate (see prereg HP_SCOPE).

Run modes:
  --self-test : tiny REAL-code-path pass (train_target=40, eval_target_per_label=20, n_slots=2,
                epochs=3) on RELOBJ_v3 seed_7 -- constructs the ACTUAL substrate objects
                (gen_cross_boundary, load_frozen_encoder/TinyTransformer, compute_hidden_cache,
                EntitySlotGate/fit_entity_slot_gate/SequenceMatrix.bind_pair, fit_binary_probe) at
                tiny scale, not a synthetic-only branch (Gate F.1). Calibration gate is COMPUTED but
                NOT hard-blocking at this scale (see calibration_check).
  --smoke     : FULL-scale construction (train=1800, eval_per_label=300 -- IDENTICAL to FULL_CFG,
                DISCRIMINATOR-MUST-SURVIVE-SCALE Option A) but ONE unit (seed_7) and reduced
                gate-training epochs (8 vs 15) for speed. Calibration gate IS enforced (this is the
                real construction).
  --full      : BOTH units (RELOBJ_v3 seed_7, seed_13), full epochs (15), n_slots=4.
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
from hdlab.entity_slot_gate import fit_entity_slot_gate  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, resumable_seeds,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "entity_slot_gate_cross_boundary_v1"

CKPT_RELOBJ_V3_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")
CKPT_RELOBJ_V3_SEED13 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_13.pt")
CKPTS_BY_SEED = {7: CKPT_RELOBJ_V3_SEED7, 13: CKPT_RELOBJ_V3_SEED13}

SEED = 20260728          # construction RNG seed -- MATCHES diag_order_critical_comprehension_calib_v1.SEED
                          # (same split/items every run mode; only train_target/eval_target scale down)

SELFTEST_CFG = dict(run_mode="selftest", train_target=40, eval_target_per_label=20,
                     n_slots=2, epochs=3, gate_hidden=8, seeds=[7], enforce_calibration=False)
# n_slots=16 (not 4): a smoke-stage capacity diagnostic (this session, exp_dev) found the mechanism
# margin at 8 epochs was 0.0050 @n_slots=4 (Hebbian bundle severely over capacity: ~900 coherent
# train pairs into a d=512 associative matrix; classical bundle capacity ~0.15*512=77 pairs) vs
# 0.0717 @n_slots=16 vs 0.0667 @n_slots=64 -- 16 is the measured best/near-plateau point.
# MEASURED@this session's ad-hoc capacity sweep (not re-run as a formal cell; see prereg
# "Smoke-stage discriminator-fires investigation" section for the full record + the definitive
# combo-feature test that supersedes this as the reason NOT to dispatch FULL).
SMOKE_CFG = dict(run_mode="smoke", train_target=1800, eval_target_per_label=300,
                  n_slots=16, epochs=8, gate_hidden=32, seeds=[7], enforce_calibration=True)
FULL_CFG = dict(run_mode="full", train_target=1800, eval_target_per_label=300,
                 n_slots=16, epochs=15, gate_hidden=32, seeds=[7, 13], enforce_calibration=True)

HARD_PASS_GAIN = 0.05        # SLOT_GATE_TRAINED margin - MEAN_POOL margin, per seed
MIDDLE_BAND_GAIN = 0.02
RANDOM_GATE_EPS = 0.02       # random-gate control must trail trained gain by at least this to clear


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
# Calibration gate (re-run at dispatch time, not trusted from a cached prior result)
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
# Clause + full-sentence encoding for one ckpt
# ---------------------------------------------------------------------------
def _clause_reps(model, tok, spec, clause1_texts, clause2_texts, cfg):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H1, M1, _ = compute_hidden_cache(model, tok, spec, clause1_texts, ecfg, device)
    H2, M2, _ = compute_hidden_cache(model, tok, spec, clause2_texts, ecfg, device)
    g1 = readout_mean_pool(H1, M1)
    g2 = readout_mean_pool(H2, M2)
    return torch.from_numpy(g1).float(), torch.from_numpy(g2).float()


def _full_sent_meanpool(model, tok, spec, sents):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H, M, _ = compute_hidden_cache(model, tok, spec, sents, ecfg, device)
    return readout_mean_pool(H, M)


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
# One unit (one RELOBJ_v3 seed): matched-plain-readout + slot-gate (trained/random) + informational
# random-init-encoder control.
# ---------------------------------------------------------------------------
def run_one_unit(seed, cfg, construction, eval_scr_sents_wholesent):
    ckpt_path = CKPTS_BY_SEED[seed]
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError("frozen checkpoint not found: %s" % ckpt_path)
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)
    d_model = ckpt_meta["model_cfg"]["d_model"]

    train_items = construction["train"]
    eval_items = construction["eval"]
    y_train_np = np.array([it["label"] for it in train_items], dtype=np.int64)
    y_eval_np = np.array([it["label"] for it in eval_items], dtype=np.int64)
    y_train_t = torch.from_numpy(y_train_np).long()

    train_sents = [it["sent"] for it in train_items]
    eval_sents = [it["sent"] for it in eval_items]

    # ---- matched plain readout: MEAN_POOL over the full (whole-sentence) forward pass ----
    G_tr = _full_sent_meanpool(model, tok, spec, train_sents)
    G_ec = _full_sent_meanpool(model, tok, spec, eval_sents)
    G_es = _full_sent_meanpool(model, tok, spec, eval_scr_sents_wholesent)
    meanpool_res = score_readout_arm("MEAN_POOL", G_tr, y_train_np, G_ec, G_es, y_eval_np, SEED)

    # ---- clause-separated encodings for the slot-gate mechanism ----
    h1_tr, h2_tr = _clause_reps(model, tok, spec, [it["clause1"] for it in train_items],
                                 [it["clause2"] for it in train_items], cfg)
    h1_ec, h2_ec = _clause_reps(model, tok, spec, [it["clause1"] for it in eval_items],
                                 [it["clause2"] for it in eval_items], cfg)
    c1_scr, c2_scr = _scramble_clause_texts(eval_items, SEED + 5555)
    h1_es, h2_es = _clause_reps(model, tok, spec, c1_scr, c2_scr, cfg)

    def _slot_gate_arm(name, random_init, seed_offset=0):
        mod = fit_entity_slot_gate(d_model, h1_tr, h2_tr, y_train_t, n_slots=cfg["n_slots"],
                                    epochs=cfg["epochs"], seed=SEED + seed_offset, random_init=random_init)
        f_tr = mod.surprise_features(h1_tr, h2_tr).detach().numpy()
        f_ec = mod.surprise_features(h1_ec, h2_ec).detach().numpy()
        f_es = mod.surprise_features(h1_es, h2_es).detach().numpy()
        return score_readout_arm(name, f_tr, y_train_np, f_ec, f_es, y_eval_np, SEED), f_ec

    trained_res, trained_feats_ec = _slot_gate_arm("SLOT_GATE_TRAINED", False)
    random_gate_res, random_gate_feats_ec = _slot_gate_arm("SLOT_GATE_RANDOM_GATE", True, seed_offset=1)

    # ---- informational-only control: random-init (never-fitted) encoder + TRAINED gate ----
    mc = ckpt_meta["model_cfg"]
    torch.manual_seed(SEED + 999)
    rand_model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                  mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    rand_model.eval()
    for p in rand_model.parameters():
        p.requires_grad_(False)
    rh1_tr, rh2_tr = _clause_reps(rand_model, tok, spec, [it["clause1"] for it in train_items],
                                   [it["clause2"] for it in train_items], cfg)
    rh1_ec, rh2_ec = _clause_reps(rand_model, tok, spec, [it["clause1"] for it in eval_items],
                                   [it["clause2"] for it in eval_items], cfg)
    rh1_es, rh2_es = _clause_reps(rand_model, tok, spec, c1_scr, c2_scr, cfg)
    rmod = fit_entity_slot_gate(d_model, rh1_tr, rh2_tr, y_train_t, n_slots=cfg["n_slots"],
                                 epochs=cfg["epochs"], seed=SEED + 2, random_init=False)
    rf_tr = rmod.surprise_features(rh1_tr, rh2_tr).detach().numpy()
    rf_ec = rmod.surprise_features(rh1_ec, rh2_ec).detach().numpy()
    rf_es = rmod.surprise_features(rh1_es, rh2_es).detach().numpy()
    random_encoder_res = score_readout_arm("RANDOM_INIT_ENCODER_SLOT_GATE", rf_tr, y_train_np,
                                            rf_ec, rf_es, y_eval_np, SEED)

    arms_differ = _arms_must_differ_np({
        "MEAN_POOL": G_ec, "SLOT_GATE_TRAINED_feats": trained_feats_ec,
        "SLOT_GATE_RANDOM_GATE_feats": random_gate_feats_ec, "RANDOM_INIT_ENCODER_feats": rf_ec,
    })

    trained_margin = trained_res["margin"]
    meanpool_margin = meanpool_res["margin"]
    random_gate_margin = random_gate_res["margin"]
    gain = trained_margin - meanpool_margin
    random_gate_gain = random_gate_margin - meanpool_margin
    structure_alone = bool(random_gate_gain >= gain - RANDOM_GATE_EPS)
    unit_pass = bool(gain >= HARD_PASS_GAIN and not structure_alone)

    return dict(
        seed=seed, ckpt_path=ckpt_path, ckpt_meta=ckpt_meta, d_model=d_model,
        meanpool=meanpool_res, slot_gate_trained=trained_res, slot_gate_random_gate=random_gate_res,
        random_init_encoder_slot_gate=random_encoder_res,
        gain_over_meanpool=gain, random_gate_gain_over_meanpool=random_gate_gain,
        structure_alone=structure_alone, arms_differ_digests=arms_differ, unit_pass=unit_pass,
        failure_class=None,
    )


# ---------------------------------------------------------------------------
# Self-test assertions (Gate F.1)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_unit, calib):
    assert len(per_unit) == 1, "selftest expected exactly 1 unit"
    v = list(per_unit.values())[0]
    assert not v.get("failure_class"), "selftest unit crashed: %s: %s" % (v.get("failure_class"), v.get("error_msg"))
    for arm in ("meanpool", "slot_gate_trained", "slot_gate_random_gate", "random_init_encoder_slot_gate"):
        m = v[arm]["margin"]
        assert -1.0 <= m <= 1.0, "margin out of range for %s: %s" % (arm, m)
    assert len(v["arms_differ_digests"]) >= 3, "arms-must-differ digests missing"
    assert v["ckpt_meta"]["seed"] == 7, "self-test ckpt seed mismatch"
    assert isinstance(v["unit_pass"], bool), "unit_pass not a bool"
    assert isinstance(calib["calibration_pass"], bool), "calibration_pass not a bool"


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def build_verdict(per_unit, seeds, calib_pass, enforce_calibration):
    expected_n = len(seeds)
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

    any_structure_alone = any(v["structure_alone"] for v in per_unit.values())
    gains = {k: v["gain_over_meanpool"] for k, v in per_unit.items()}
    n_pass = sum(1 for v in per_unit.values() if v["gain_over_meanpool"] >= HARD_PASS_GAIN)
    n_middle = sum(1 for v in per_unit.values()
                   if MIDDLE_BAND_GAIN <= v["gain_over_meanpool"] < HARD_PASS_GAIN)
    n_units = len(per_unit)

    if any_structure_alone:
        verdict = "HARD_FAIL_STRUCTURE_ALONE"
        msg = ("MANDATORY random-init-gate control matched/exceeded the trained gate's gain over "
               "MEAN_POOL on >=1 unit (structure alone, not learning). Per-unit "
               "gain/random_gate_gain: %s" % {k: (v["gain_over_meanpool"], v["random_gate_gain_over_meanpool"])
                                               for k, v in per_unit.items()})
    elif n_pass == n_units:
        verdict = "HARD_PASS"
        msg = ("SLOT_GATE_TRAINED beats matched MEAN_POOL readout by >=%.2f margin on ALL %d units, "
               "random-init-gate control does NOT match the gain on any unit. Per-unit gains: %s"
               % (HARD_PASS_GAIN, n_units, gains))
    elif n_pass >= 1:
        verdict = "MIDDLE_BAND"
        msg = ("Only %d/%d units clear HARD_PASS_GAIN=%.2f (single-seed pass does not replicate per "
               "the standing seed-luck discipline). Per-unit gains: %s" % (n_pass, n_units, HARD_PASS_GAIN, gains))
    elif n_middle >= 1:
        verdict = "MIDDLE_BAND"
        msg = "Gain(s) in [%.2f, %.2f) band, not a clean HARD_PASS or HARD_FAIL. Per-unit gains: %s" % (
            MIDDLE_BAND_GAIN, HARD_PASS_GAIN, gains)
    else:
        verdict = "HARD_FAIL"
        msg = "0/%d units clear MIDDLE_BAND_GAIN=%.2f. Per-unit gains: %s" % (n_units, MIDDLE_BAND_GAIN, gains)

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
    seeds = cfg["seeds"]

    _write_start_marker(out_dir, cfg["run_mode"], len(seeds))
    _log("run_mode=%s n_units=%d seeds=%s train_target=%d eval_per_label=%d n_slots=%d epochs=%d"
         % (cfg["run_mode"], len(seeds), seeds, cfg["train_target"], cfg["eval_target_per_label"],
            cfg["n_slots"], cfg["epochs"]))

    t_wall0 = time.perf_counter()
    with CellHeartbeat(out_dir, total_units=len(seeds) + 1, interval_s=30) as hb:
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
            unit_keys = ["seed_%d" % s for s in seeds]
            _, remaining = resumable_seeds(unit_keys, out_dir, run_config=dict(run_mode=cfg["run_mode"]))
            remaining_seeds = [s for s in seeds if ("seed_%d" % s) in set(remaining)]
            for i, s in enumerate(remaining_seeds):
                t0 = time.perf_counter()
                key = "seed_%d" % s
                try:
                    res = run_one_unit(s, cfg, construction, eval_scr_sents_wholesent)
                    res["elapsed_s"] = time.perf_counter() - t0
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                    res = dict(seed=s, failure_class=type(e).__name__, error_msg=str(e)[:500],
                              unit_pass=False, elapsed_s=time.perf_counter() - t0)
                    _log("UNIT FAILED seed=%d: %s: %s" % (s, type(e).__name__, e))
                write_partial(out_dir, key, res)
                _log("unit=%s done in %.1fs pass=%s gain=%s" %
                    (key, res["elapsed_s"], res.get("unit_pass"), res.get("gain_over_meanpool")))
                hb.tick(2 + i, extra={"unit": key}, force=True)
            per_unit = aggregate_partials(out_dir, unit_keys)
        else:
            _log("CALIBRATION_GATE_FAIL -- skipping own-encoder scoring entirely (uninterpretable "
                 "against a broken instrument at this regime)")

    verdict, vmsg, cardinality_ok, expected_n, got_n = build_verdict(
        per_unit, seeds, calib["calibration_pass"], cfg["enforce_calibration"])
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg, anchor_name=ANCHOR_NAME,
        run_mode=cfg["run_mode"], ts_iso=datetime.now(timezone.utc).isoformat(),
        device="cpu", cuda=False, n_units=len(per_unit),
        per_unit=per_unit, cardinality_ok=cardinality_ok,
        expected_n_units=expected_n, got_n_units=got_n,
        calibration=calib, calibration_enforced=cfg["enforce_calibration"],
        bands=dict(hard_pass_gain=HARD_PASS_GAIN, middle_band_gain=MIDDLE_BAND_GAIN,
                  random_gate_eps=RANDOM_GATE_EPS, margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR),
        hp_scope=dict(applies_to=["seed_7", "seed_13"],
                     informational_only=["random_init_encoder_slot_gate arm (all units)"]),
        cfg=cfg, elapsed_s_total=time.perf_counter() - t_wall0,
        construction_meta=dict(n_train=len(construction["train"]), n_eval=len(construction["eval"]),
                               n_train_groups=len(construction["train_group_set"]),
                               n_eval_groups=len(construction["eval_group_set"])),
        wire_target="hdlab/entity_slot_gate.py (EntitySlotGate) IF HARD_PASS -- target integration "
                    "site TBD by Skunkworks/Director at WIRE time per WIRE-DON'T-ISLAND.",
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
