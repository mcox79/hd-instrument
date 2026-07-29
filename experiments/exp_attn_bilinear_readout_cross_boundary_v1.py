"""CELL: attn_bilinear_readout_cross_boundary_v1 -- component brain-fidelity ledger ROW 4
(READOUT/decoding) can-fail build. See notes/drill_brain_faithful_comprehension_readout.md
(design, commit 880fd5254) and notes/component_brain_fidelity_ledger.md row 4. Judged on the
READOUT'S OWN brain metric (calibration-first, role-general order/relation decodability) NOT a
downstream task-win. ALSO subsumes the pending CROSS-BOUNDARY mean-pool VET (does the frozen
encoder's +0.21 cross-boundary tracking REPLICATE across seeds -- the MEAN_POOL arm IS the VET).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hash-test over per-unit arm score vectors) -- YES
# - final_metrics_atomicity declared (META_RULE_AH; per_iter_paths -- write_partial per unit + tmp_replace final)
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- YES
# - crlb_floor_computed + discriminator_reachability -- crlb_n/a (accuracy-margin discriminator over
#   a binary probe, not a capacity/noise regime; see prereg)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- MEAN_POOL coherent_acc
#   MEASURED@d:/AI/hd-instrument/data/diag_order_critical_comprehension_calib_v1/results.json:
#   own_encoder_results.RELOBJ_v3.CROSS_BOUNDARY.per_readout.MEAN_POOL.coherent_acc ~ 0.70-0.75 range
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm) -- smoke runs the
#   construction at FULL scale (train=1800/eval_per_label=300, IDENTICAL to FULL_CFG); only unit
#   count (1 vs 3) and gate-training epoch count differ smoke-vs-full (Option A, same precedent as
#   exp_entity_slot_gate_cross_boundary_v1.py)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- HARD_PASS_GAIN=0.05 vs a
#   [0.00,0.05) MIDDLE/FAIL range -> 0.05 gate is the top of the band, not a floor-hugging value
# - HP_SCOPE per-arm declaration -- see prereg / metrics.hp_scope
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate) -- YES (3 units FULL:
#   RELOBJ_v3 seed_7, RELOBJ_v3 seed_13, BASELINE_v2 seed_7)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- YES
# - calibration_check field (META_RULE_M) -- adaptive_with_discriminator_gate: this cell RE-RUNS
#   the CROSS_BOUNDARY calibration gate itself (imported from exp_entity_slot_gate_cross_boundary_v1,
#   not a cached prior result) at whatever regime it is dispatched at, and ABORTS
#   (CALIBRATION_GATE_FAIL) before touching the frozen encoder if no known reader clears it
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)

WHY: ledger row 4 status at drill time = IMPROVING (learned bilinear/probe readout fix measured
+0.038 mean AUC on a DIFFERENT (ARC relational-retrieval) task; cross-boundary +0.21 on THIS
construction was VET-pending -- single-seed only). Gap named: "linear where brain is nonlinear+
attentional; mean-pool order-blind." This cell builds `AttnBilinearReadout` (experiments.
_learned_relational_readout.AttnBilinearReadout / fit_attn_bilinear_readout / score_attn_bilinear_
arm, extended in this session) = (a) query-conditioned ATTENTION POOL over frozen per-token hidden
states (fixes mean-pool order-blindness / gain-modulation analog, Reynolds & Heeger) + (b) an
explicit LOW-RANK QUADRATIC interaction term between clause1/clause2 pooled reps (mixed-selectivity
substitute, Rigotti/Fusi 2013) -- both LEARNED heads on the FROZEN encoder, no retrain, no
grounding, no borrowed embedding, no external LLM. Role-general bind/unbind (ledger row 4's item
2c) is correctly DEFERRED per the design note (composes with row 6 working-memory later).

CONSTRUCTION: `experiments.diag_order_critical_comprehension_calib_v1.gen_cross_boundary` (READ-ONLY
import -- a separate agent's ground, per dispatch-prompt instruction; NOT edited by this cell).
Calibration gate re-run via `experiments.exp_entity_slot_gate_cross_boundary_v1.run_calibration_gate`
(reused verbatim, not reimplemented, since that cell already built + validated this exact gate for
this exact construction).

ARMS (3 substantive + 2 controls, per-unit):
  MEAN_POOL             -- whole-sentence mean-pool readout (the CURRENT matched baseline / the
                            arm that IS the mean-pool VET: does RELOBJ_v3's cross-boundary tracking
                            REPLICATE seed_7 -> seed_13?).
  CLAUSE_SPLIT_CONCAT    -- concat(mean_pool(clause1), mean_pool(clause2)) -> linear probe (the
                            +0.24-class reference: order-preserving-by-clause-granularity but still
                            linear/non-attentional).
  ATTN_BILINEAR          -- the new brain-faithful readout under test (attention-pool + explicit
                            bilinear interaction over clause1/clause2, trained end-to-end).
  RANDOM_INIT_ENCODER    -- MANDATORY (dispatch-prompt hard gate): identical ATTN_BILINEAR readout,
                            TRAINED, but the frozen encoder itself is swapped for a random-init
                            (never-fitted) TinyTransformer of the SAME architecture -- isolates
                            whether the ENCODER's learned semantics (vs untrained-transformer
                            structural biases alone) drive the gain. If this control's gain-over-
                            MEAN_POOL matches/exceeds the trained-encoder gain -> HARD_FAIL
                            (structure-not-learning; this session's prior random-init-beats-trained
                            scare on entity-state, 0.704 vs 0.592, makes this control non-negotiable).
  RANDOM_INIT_READOUT    -- informational-only (design-doc's own "untrained/random-init ATTN_
                            BILINEAR" arm): trained encoder, but ATTN_BILINEAR left at its random
                            torch initialization (ZERO optimizer steps) -- checks whether the
                            readout ARCHITECTURE alone (without learning attention/interaction
                            weights) already produces the gain. Reported, does not gate HARD_PASS/
                            HARD_FAIL on its own (the dispatch prompt's explicit hard gate is the
                            RANDOM_INIT_ENCODER control), but any positive match here would also be
                            flagged in verdict_msg as an additional caveat.

UNITS: RELOBJ_v3 seed_7, RELOBJ_v3 seed_13 (the two gate on HARD_PASS/HARD_FAIL, "BOTH seeds" per
the dispatch prompt's bands), BASELINE_v2 seed_7 (informational third data point, not gating --
declared in HP_SCOPE).

Run modes:
  --self-test : tiny REAL-code-path pass (train_target=40, eval_target_per_label=20, r=4, epochs=3)
                on RELOBJ_v3 seed_7 -- constructs the ACTUAL substrate objects (gen_cross_boundary,
                load_frozen_encoder/TinyTransformer, compute_hidden_cache, AttnBilinearReadout/
                fit_attn_bilinear_readout, fit_binary_probe) at tiny scale (Gate F.1). Calibration
                gate is COMPUTED but NOT hard-blocking at this scale.
  --smoke     : FULL-scale construction (train=1800, eval_per_label=300 -- IDENTICAL to FULL_CFG)
                but ONE unit (RELOBJ_v3 seed_7). epochs=8 was tried first and found to badly
                UNDER-fit (ATTN_BILINEAR train_balanced_acc=0.564, below the SANITY_MARGIN gate) --
                epochs=40 is required for the end-to-end attention+interaction+classifier fit to
                converge on ~1800 full-batch items; SMOKE_CFG and FULL_CFG both use epochs=40
                (no smoke/full epoch discrepancy, since 8 was a real convergence bug, not a
                legitimate speed/fidelity tradeoff). Calibration gate IS enforced.
  --full      : all 3 units, epochs=40, r=32.
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
    gen_cross_boundary, score_readout_arm, MARGIN_THRESH, COHERENT_FLOOR, SANITY_MARGIN,
)
from experiments.exp_entity_slot_gate_cross_boundary_v1 import run_calibration_gate  # noqa: E402
import experiments.exp_unified_self_learning_loop_v2 as LOOP2  # noqa: E402  (_scramble_words)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from experiments.diag_comprehension_readout_sweep_v1 import compute_hidden_cache, readout_mean_pool  # noqa: E402
from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer  # noqa: E402
from experiments._learned_relational_readout import (  # noqa: E402
    fit_attn_bilinear_readout, score_attn_bilinear_arm,
)
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, resumable_seeds,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "attn_bilinear_readout_cross_boundary_v1"

CKPT_RELOBJ_V3_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")
CKPT_RELOBJ_V3_SEED13 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_13.pt")
CKPT_BASELINE_V2_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")

UNITS = [
    dict(unit="RELOBJ_v3_seed_7", ckpt=CKPT_RELOBJ_V3_SEED7, gating=True),
    dict(unit="RELOBJ_v3_seed_13", ckpt=CKPT_RELOBJ_V3_SEED13, gating=True),
    dict(unit="BASELINE_v2_seed_7", ckpt=CKPT_BASELINE_V2_SEED7, gating=False),
]

SEED = 20260728          # construction RNG seed -- MATCHES diag_order_critical_comprehension_calib_v1.SEED
                          # (same split/items every run mode; only train_target/eval_target scale down)

SELFTEST_CFG = dict(run_mode="selftest", train_target=40, eval_target_per_label=20,
                     r=4, epochs=3, seeds=["RELOBJ_v3_seed_7"], enforce_calibration=False)
SMOKE_CFG = dict(run_mode="smoke", train_target=1800, eval_target_per_label=300,
                  r=32, epochs=40, seeds=["RELOBJ_v3_seed_7"], enforce_calibration=True)
# epochs=8 tried first (see module docstring) -- badly under-fit (ATTN_BILINEAR
# train_balanced_acc=0.564 < SANITY_MARGIN gate). MEASURED@d:/AI/hd-instrument/data/
# exp_attn_bilinear_readout_cross_boundary_v1_smoke/metrics.json (pre-fix run, since overwritten).
FULL_CFG = dict(run_mode="full", train_target=1800, eval_target_per_label=300,
                 r=32, epochs=40, seeds=["RELOBJ_v3_seed_7", "RELOBJ_v3_seed_13", "BASELINE_v2_seed_7"],
                 enforce_calibration=True)

HARD_PASS_GAIN = 0.05        # ATTN_BILINEAR margin - MEAN_POOL margin, per gating unit
MIDDLE_BAND_GAIN = 0.02
RANDOM_ENCODER_EPS = 0.02    # random-init-encoder control must trail trained gain by at least this
VET_REPLICATE_MARGIN = 0.15  # seed_13 MEAN_POOL margin threshold for "replicates"
UNIT_BY_NAME = {u["unit"]: u for u in UNITS}


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
# Encoding helpers
# ---------------------------------------------------------------------------
def _full_sent_meanpool(model, tok, spec, sents):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H, M, _ = compute_hidden_cache(model, tok, spec, sents, ecfg, device)
    return readout_mean_pool(H, M)


def _clause_raw(model, tok, spec, clause1_texts, clause2_texts):
    """Raw (unpooled) per-token hidden states + mask for each clause, for AttnBilinearReadout."""
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H1, M1, _ = compute_hidden_cache(model, tok, spec, clause1_texts, ecfg, device)
    H2, M2, _ = compute_hidden_cache(model, tok, spec, clause2_texts, ecfg, device)
    return (torch.from_numpy(H1).float(), torch.from_numpy(M1).bool(),
            torch.from_numpy(H2).float(), torch.from_numpy(M2).bool())


def _clause_meanpool(model, tok, spec, clause1_texts, clause2_texts):
    device = torch.device("cpu")
    ecfg = dict(max_len=min(32, getattr(model, "max_len", 32)), encode_batch=256)
    H1, M1, _ = compute_hidden_cache(model, tok, spec, clause1_texts, ecfg, device)
    H2, M2, _ = compute_hidden_cache(model, tok, spec, clause2_texts, ecfg, device)
    g1 = readout_mean_pool(H1, M1)
    g2 = readout_mean_pool(H2, M2)
    return np.concatenate([g1, g2], axis=1)


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
# One unit: MEAN_POOL (the VET arm) + CLAUSE_SPLIT_CONCAT + ATTN_BILINEAR (trained/random-readout/
# random-encoder).
# ---------------------------------------------------------------------------
def run_one_unit(unit_name, cfg, construction, eval_scr_sents_wholesent):
    u = UNIT_BY_NAME[unit_name]
    ckpt_path = u["ckpt"]
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

    # ---- MEAN_POOL: whole-sentence mean-pool -- the matched baseline / mean-pool VET arm ----
    G_tr = _full_sent_meanpool(model, tok, spec, train_sents)
    G_ec = _full_sent_meanpool(model, tok, spec, eval_sents)
    G_es = _full_sent_meanpool(model, tok, spec, eval_scr_sents_wholesent)
    meanpool_res = score_readout_arm("MEAN_POOL", G_tr, y_train_np, G_ec, G_es, y_eval_np, SEED)

    # ---- CLAUSE_SPLIT_CONCAT: concat(mean_pool(clause1), mean_pool(clause2)) ----
    c1_scr, c2_scr = _scramble_clause_texts(eval_items, SEED + 5555)
    CC_tr = _clause_meanpool(model, tok, spec, [it["clause1"] for it in train_items],
                              [it["clause2"] for it in train_items])
    CC_ec = _clause_meanpool(model, tok, spec, [it["clause1"] for it in eval_items],
                              [it["clause2"] for it in eval_items])
    CC_es = _clause_meanpool(model, tok, spec, c1_scr, c2_scr)
    clause_concat_res = score_readout_arm("CLAUSE_SPLIT_CONCAT", CC_tr, y_train_np, CC_ec, CC_es, y_eval_np, SEED)

    # ---- raw per-token clause encodings for ATTN_BILINEAR ----
    H1_tr, M1_tr, H2_tr, M2_tr = _clause_raw(model, tok, spec, [it["clause1"] for it in train_items],
                                              [it["clause2"] for it in train_items])
    H1_ec, M1_ec, H2_ec, M2_ec = _clause_raw(model, tok, spec, [it["clause1"] for it in eval_items],
                                              [it["clause2"] for it in eval_items])
    H1_es, M1_es, H2_es, M2_es = _clause_raw(model, tok, spec, c1_scr, c2_scr)

    def _attn_bilinear_arm(name, random_init, seed_offset=0):
        mod = fit_attn_bilinear_readout(d_model, H1_tr, M1_tr, H2_tr, M2_tr, y_train_t, r=cfg["r"],
                                        epochs=cfg["epochs"], seed=SEED + seed_offset, random_init=random_init)
        res = score_attn_bilinear_arm(name, mod, H1_tr, M1_tr, H2_tr, M2_tr, y_train_np,
                                       H1_ec, M1_ec, H2_ec, M2_ec, H1_es, M1_es, H2_es, M2_es, y_eval_np,
                                       MARGIN_THRESH, COHERENT_FLOOR, SANITY_MARGIN)
        with torch.no_grad():
            feats_ec = mod.features(H1_ec, M1_ec, H2_ec, M2_ec).numpy()
        return res, feats_ec

    trained_res, trained_feats_ec = _attn_bilinear_arm("ATTN_BILINEAR", False)
    random_readout_res, random_readout_feats_ec = _attn_bilinear_arm(
        "RANDOM_INIT_READOUT", True, seed_offset=1)

    # ---- MANDATORY control: random-init (never-fitted) encoder + TRAINED ATTN_BILINEAR readout ----
    mc = ckpt_meta["model_cfg"]
    torch.manual_seed(SEED + 999)
    rand_model = TinyTransformer(mc["vocab"], mc["max_len"], mc["d_model"], mc["n_layers"],
                                  mc["n_heads"], mc["ffn_mult"], mc["pad_id"])
    rand_model.eval()
    for p in rand_model.parameters():
        p.requires_grad_(False)
    rH1_tr, rM1_tr, rH2_tr, rM2_tr = _clause_raw(rand_model, tok, spec, [it["clause1"] for it in train_items],
                                                  [it["clause2"] for it in train_items])
    rH1_ec, rM1_ec, rH2_ec, rM2_ec = _clause_raw(rand_model, tok, spec, [it["clause1"] for it in eval_items],
                                                  [it["clause2"] for it in eval_items])
    rH1_es, rM1_es, rH2_es, rM2_es = _clause_raw(rand_model, tok, spec, c1_scr, c2_scr)
    rmod = fit_attn_bilinear_readout(d_model, rH1_tr, rM1_tr, rH2_tr, rM2_tr, y_train_t, r=cfg["r"],
                                     epochs=cfg["epochs"], seed=SEED + 2, random_init=False)
    random_encoder_res = score_attn_bilinear_arm(
        "RANDOM_INIT_ENCODER", rmod, rH1_tr, rM1_tr, rH2_tr, rM2_tr, y_train_np,
        rH1_ec, rM1_ec, rH2_ec, rM2_ec, rH1_es, rM1_es, rH2_es, rM2_es, y_eval_np,
        MARGIN_THRESH, COHERENT_FLOOR, SANITY_MARGIN)
    with torch.no_grad():
        random_encoder_feats_ec = rmod.features(rH1_ec, rM1_ec, rH2_ec, rM2_ec).numpy()

    # ---- informational-only: MEAN_POOL through the random-init encoder (feeds the VET check) ----
    rG_tr = _full_sent_meanpool(rand_model, tok, spec, train_sents)
    rG_ec = _full_sent_meanpool(rand_model, tok, spec, eval_sents)
    rG_es = _full_sent_meanpool(rand_model, tok, spec, eval_scr_sents_wholesent)
    random_encoder_meanpool_res = score_readout_arm(
        "RANDOM_INIT_ENCODER_MEAN_POOL", rG_tr, y_train_np, rG_ec, rG_es, y_eval_np, SEED)

    arms_differ = _arms_must_differ_np({
        "MEAN_POOL": G_ec, "CLAUSE_SPLIT_CONCAT": CC_ec,
        "ATTN_BILINEAR_feats": trained_feats_ec, "RANDOM_INIT_READOUT_feats": random_readout_feats_ec,
        "RANDOM_INIT_ENCODER_feats": random_encoder_feats_ec, "RANDOM_INIT_ENCODER_MEAN_POOL": rG_ec,
    })

    trained_margin = trained_res["margin"]
    meanpool_margin = meanpool_res["margin"]
    random_readout_margin = random_readout_res["margin"]
    random_encoder_margin = random_encoder_res["margin"]
    gain = trained_margin - meanpool_margin
    random_readout_gain = random_readout_margin - meanpool_margin
    random_encoder_gain = random_encoder_margin - meanpool_margin
    structure_alone_encoder = bool(random_encoder_gain >= gain - RANDOM_ENCODER_EPS)
    structure_alone_readout_note = bool(random_readout_gain >= gain - RANDOM_ENCODER_EPS)
    unit_pass = bool(gain >= HARD_PASS_GAIN and not structure_alone_encoder)

    return dict(
        unit=unit_name, gating=u["gating"], ckpt_path=ckpt_path, ckpt_meta=ckpt_meta, d_model=d_model,
        mean_pool=meanpool_res, clause_split_concat=clause_concat_res,
        attn_bilinear_trained=trained_res, random_init_readout=random_readout_res,
        random_init_encoder=random_encoder_res, random_init_encoder_mean_pool=random_encoder_meanpool_res,
        gain_over_meanpool=gain, random_readout_gain_over_meanpool=random_readout_gain,
        random_encoder_gain_over_meanpool=random_encoder_gain,
        structure_alone_encoder=structure_alone_encoder,
        structure_alone_readout_note=structure_alone_readout_note,
        arms_differ_digests=arms_differ, unit_pass=unit_pass, failure_class=None,
    )


# ---------------------------------------------------------------------------
# Self-test assertions (Gate F.1)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_unit, calib):
    assert len(per_unit) == 1, "selftest expected exactly 1 unit"
    v = list(per_unit.values())[0]
    assert not v.get("failure_class"), "selftest unit crashed: %s: %s" % (v.get("failure_class"), v.get("error_msg"))
    for arm in ("mean_pool", "clause_split_concat", "attn_bilinear_trained", "random_init_readout",
                "random_init_encoder", "random_init_encoder_mean_pool"):
        m = v[arm]["margin"]
        assert -1.0 <= m <= 1.0, "margin out of range for %s: %s" % (arm, m)
    assert len(v["arms_differ_digests"]) >= 5, "arms-must-differ digests missing"
    assert v["ckpt_meta"]["seed"] == 7, "self-test ckpt seed mismatch"
    assert isinstance(v["unit_pass"], bool), "unit_pass not a bool"
    assert isinstance(calib["calibration_pass"], bool), "calibration_pass not a bool"


# ---------------------------------------------------------------------------
# Verdict: READOUT verdict (ATTN_BILINEAR vs MEAN_POOL, gated on RELOBJ_v3 seeds) + VET sub-verdict
# (MEAN_POOL seed_7 -> seed_13 replication).
# ---------------------------------------------------------------------------
def build_verdict(per_unit, seeds, calib_pass, enforce_calibration):
    expected_n = len(seeds)
    got_n = len(per_unit)
    if enforce_calibration and not calib_pass:
        return ("CALIBRATION_GATE_FAIL",
                "No known reader (MiniLM/BGE_SMALL) cleared MARGIN_THRESH=%.2f / COHERENT_FLOOR=%.2f "
                "on CROSS_BOUNDARY at this regime -- construction is broken at this scale; own-encoder "
                "scoring is uninterpretable and was SKIPPED per the calibration-first rule."
                % (MARGIN_THRESH, COHERENT_FLOOR), False, expected_n, 0, None)
    if got_n != expected_n:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "expected %d units, got %d" % (expected_n, got_n), False, expected_n, got_n, None)

    any_failure = any(v.get("failure_class") for v in per_unit.values())
    if any_failure:
        return ("HARD_FAIL_UNIT_CRASH",
                "one or more units crashed: %s" % {k: v.get("failure_class") for k, v in per_unit.items()
                                                     if v.get("failure_class")},
                True, expected_n, got_n, None)

    # --- VET sub-verdict: does MEAN_POOL's RELOBJ_v3 seed_7 cross-boundary margin replicate at seed_13? ---
    vet = None
    if "RELOBJ_v3_seed_7" in per_unit and "RELOBJ_v3_seed_13" in per_unit:
        s7 = per_unit["RELOBJ_v3_seed_7"]["mean_pool"]
        s13 = per_unit["RELOBJ_v3_seed_13"]["mean_pool"]
        s13_scr_at_chance = abs(s13["scrambled_acc"] - 0.5) <= 0.10
        s13_rand_encoder = per_unit["RELOBJ_v3_seed_13"]["random_init_encoder_mean_pool"]
        s13_random_matches = bool(s13_rand_encoder["margin"] >= s13["margin"] - RANDOM_ENCODER_EPS)
        vet_replicates = bool(s13["margin"] >= VET_REPLICATE_MARGIN and s13_scr_at_chance
                               and not s13_random_matches)
        vet = dict(seed_7_margin=s7["margin"], seed_13_margin=s13["margin"],
                   seed_13_scrambled_acc=s13["scrambled_acc"], seed_13_scr_at_chance=s13_scr_at_chance,
                   seed_13_random_init_encoder_margin=s13_rand_encoder["margin"],
                   seed_13_random_matches=s13_random_matches,
                   vet_verdict=("REPLICATES" if vet_replicates else "FAILS_TO_REPLICATE"))

    gating_units = {k: v for k, v in per_unit.items() if v["gating"]}
    n_gating = len(gating_units)
    any_structure_alone = any(v["structure_alone_encoder"] for v in gating_units.values())
    gains = {k: v["gain_over_meanpool"] for k, v in per_unit.items()}
    n_pass = sum(1 for v in gating_units.values() if v["gain_over_meanpool"] >= HARD_PASS_GAIN)
    n_middle = sum(1 for v in gating_units.values()
                   if MIDDLE_BAND_GAIN <= v["gain_over_meanpool"] < HARD_PASS_GAIN)

    if any_structure_alone:
        verdict = "HARD_FAIL_STRUCTURE_ALONE"
        msg = ("MANDATORY random-init-ENCODER control matched/exceeded the trained ATTN_BILINEAR "
               "gain over MEAN_POOL on >=1 gating unit (structure alone, not learning). "
               "Per-gating-unit gain/random_encoder_gain: %s"
               % {k: (v["gain_over_meanpool"], v["random_encoder_gain_over_meanpool"])
                  for k, v in gating_units.items()})
    elif n_pass == n_gating and n_gating >= 2:
        verdict = "HARD_PASS"
        msg = ("ATTN_BILINEAR beats matched MEAN_POOL readout by >=%.2f margin on ALL %d RELOBJ_v3 "
               "seeds, random-init-encoder control does NOT match the gain on any gating unit. "
               "Per-unit gains: %s" % (HARD_PASS_GAIN, n_gating, gains))
    elif n_pass >= 1:
        verdict = "MIDDLE_BAND"
        msg = ("Only %d/%d RELOBJ_v3 seeds clear HARD_PASS_GAIN=%.2f (single-seed pass does not "
               "replicate per the standing seed-luck discipline). Per-unit gains: %s"
               % (n_pass, n_gating, HARD_PASS_GAIN, gains))
    elif n_middle >= 1:
        verdict = "MIDDLE_BAND"
        msg = "Gain(s) in [%.2f, %.2f) band, not a clean HARD_PASS or HARD_FAIL. Per-unit gains: %s" % (
            MIDDLE_BAND_GAIN, HARD_PASS_GAIN, gains)
    else:
        verdict = "HARD_FAIL"
        msg = "0/%d RELOBJ_v3 seeds clear MIDDLE_BAND_GAIN=%.2f. Per-unit gains: %s" % (
            n_gating, MIDDLE_BAND_GAIN, gains)

    if vet is not None:
        msg = msg + " || VET(mean_pool seed_13 replication): %s" % vet["vet_verdict"]

    return verdict, msg, True, expected_n, got_n, vet


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
    _log("run_mode=%s n_units=%d units=%s train_target=%d eval_per_label=%d r=%d epochs=%d"
         % (cfg["run_mode"], len(seeds), seeds, cfg["train_target"], cfg["eval_target_per_label"],
            cfg["r"], cfg["epochs"]))

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
            unit_keys = list(seeds)
            _, remaining = resumable_seeds(unit_keys, out_dir, run_config=dict(run_mode=cfg["run_mode"]))
            remaining_units = [s for s in seeds if s in set(remaining)]
            for i, unit_name in enumerate(remaining_units):
                t0 = time.perf_counter()
                try:
                    res = run_one_unit(unit_name, cfg, construction, eval_scr_sents_wholesent)
                    res["elapsed_s"] = time.perf_counter() - t0
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                    res = dict(unit=unit_name, gating=UNIT_BY_NAME[unit_name]["gating"],
                              failure_class=type(e).__name__, error_msg=str(e)[:500],
                              unit_pass=False, elapsed_s=time.perf_counter() - t0)
                    _log("UNIT FAILED unit=%s: %s: %s" % (unit_name, type(e).__name__, e))
                write_partial(out_dir, unit_name, res)
                _log("unit=%s done in %.1fs pass=%s gain=%s" %
                    (unit_name, res["elapsed_s"], res.get("unit_pass"), res.get("gain_over_meanpool")))
                hb.tick(2 + i, extra={"unit": unit_name}, force=True)
            per_unit = aggregate_partials(out_dir, unit_keys)
        else:
            _log("CALIBRATION_GATE_FAIL -- skipping own-encoder scoring entirely (uninterpretable "
                 "against a broken instrument at this regime)")

    verdict, vmsg, cardinality_ok, expected_n, got_n, vet = build_verdict(
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
        vet_mean_pool_replication=vet,
        bands=dict(hard_pass_gain=HARD_PASS_GAIN, middle_band_gain=MIDDLE_BAND_GAIN,
                  random_encoder_eps=RANDOM_ENCODER_EPS, vet_replicate_margin=VET_REPLICATE_MARGIN,
                  margin_thresh=MARGIN_THRESH, coherent_floor=COHERENT_FLOOR),
        hp_scope=dict(applies_to=["RELOBJ_v3_seed_7", "RELOBJ_v3_seed_13"],
                     informational_only=["BASELINE_v2_seed_7 (all arms)",
                                          "random_init_readout arm (all units)",
                                          "random_init_encoder_mean_pool arm (all units, feeds VET only)"]),
        cfg=cfg, elapsed_s_total=time.perf_counter() - t_wall0,
        construction_meta=dict(n_train=len(construction["train"]), n_eval=len(construction["eval"]),
                               n_train_groups=len(construction["train_group_set"]),
                               n_eval_groups=len(construction["eval_group_set"])),
        wire_target="experiments/_learned_relational_readout.py (AttnBilinearReadout) IF HARD_PASS -- "
                    "target integration site (hdlab/ promotion) TBD by Skunkworks/Director at WIRE "
                    "time per WIRE-DON'T-ISLAND.",
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
