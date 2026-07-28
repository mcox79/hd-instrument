"""CELL: relational_readout_promote_v1 -- promotes diag_readout_limit_probe_v1 (seed_7-only,
single-shot, NOT a dispatched cell) into a leak-proof, multi-seed, arbitrary-ckpt dispatched cell.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test) -- YES, per unit
# - final_metrics_atomicity declared (META_RULE_AH; per_iter_paths -- write_partial per unit + tmp_replace final)
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- YES
# - crlb_floor_computed + discriminator_reachability declared -- crlb_n/a (AUC discriminator, not a
#   capacity/noise regime; declared explicitly, see prereg)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.95) -- YES (BASELINE_COSINE ~0.56-0.64)
# - discriminator survives scale (smoke at full-N OR analytical OR preview arm) -- smoke uses reduced
#   N (for queue_add's 180s mechanical gate); the DISCRIMINATOR-MUST-SURVIVE-SCALE preview check is
#   done by exp_dev manually invoking --full on a SINGLE unit before FULL dispatch (Option C), citing
#   diag_readout_limit_probe_v1's already-MEASURED full-N result as corroborating evidence.
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- HARD_PASS margin >= 0.03, band
#   [0.0, 0.067] measured ceiling -> 5% width = 0.0033 << 0.03
# - HP_SCOPE per-arm declaration -- PRIMARY units only (mlm_v2_seed7 x 3 diag-seeds); SECONDARY
#   (relobj cross-seed) units are informational, not gated
# - cardinality_ok for sweep-axis cells (META_RULE_H; EXPECTED_N_UNITS gate) -- YES
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- YES
# - calibration_check field (META_RULE_M) -- default_ok_for_this_regime (same cfg as the
#   already-measured diag_readout_limit_probe_v1 FULL_CFG; controls validated at that regime)
# - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)

WHY (promotion, not a fresh idea): diag_readout_limit_probe_v1.py measured, on ckpt_seed_7 of the
MLM-only v2 baseline, a learned low-rank bilinear readout beating cosine-NN on held-out-NEW
relational AUC by +0.0666 (95% paired-bootstrap CI [0.0277, 0.1081], excludes zero; corroborated on
its own TRAIN-fit pairs too) -- MEASURED@d:/AI/hd-instrument/data/diag_readout_limit_probe_v1/
results.json:margin_over_baseline. That was ONE seed, ONE ckpt, ONE ad-hoc script (no pre-reg, no
dispatch, no leak-proof-cell hardening beyond its own inline asserts). This cell:
  (1) REPLICATES the finding's robustness on the SAME encoder by sweeping the diagnostic's OWN
      arbitrary choices (DIAG_SEED: controls anchor sampling, negative sampling, probe init,
      bootstrap resampling) across 3 independent seeds on ckpt_seed_7 -- the closest available
      "multi-seed" check, because **NO SECOND MLM-v2 TRAINING SEED CHECKPOINT EXISTS ON DISK**
      (confirmed: `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` is the ONLY seed;
      GAP flagged honestly, not papered over -- see prereg "known gap" section).
  (2) BUILDS A FAIR-TEST HARNESS that accepts an arbitrary ckpt path, so it re-measures ANY encoder
      (grounding / relObj, as they land) under the SAME learned-readout comparison: does the trained
      objective add DECODABLE relational structure BEYOND what a learned readout already extracts
      from the MLM-only baseline? This cell's SECONDARY arm-group exercises that harness NOW against
      the two v3_relobj checkpoints that DO exist with two real training seeds (seed_7, seed_13) --
      giving a genuine (if off-objective) cross-training-seed portability check of the mechanism
      while the harness itself stays ckpt-agnostic for future grounding/relobj/future-objective ckpts.

Leak-proofness, probe-fit code (fit_diag_probe / fit_bilinear_probe / build_train_pairs /
eval_relational_all_arms), and the arms-must-differ hash check are now in the SHARED module
`experiments/_learned_relational_readout.py` (not re-implemented here) so future consumers
(eval_battery_relational_cloze_v7.py already has an inline near-duplicate -- WIRE-consolidation
candidate flagged for Skunkworks, not touched in this pass) share ONE implementation.

Run modes:
  --self-test : tiny REAL-code-path pass (min_deg=1, cap_eval_concepts=150, max_lines=5000) on
                ckpt_seed_7 -- constructs the ACTUAL substrate objects (load_concept_universe,
                count_pass, build_split, collect_pass, load_adjacency, TinyTransformer via
                load_frozen_encoder, build_train_pairs, fit_diag_probe, fit_bilinear_probe,
                eval_relational_all_arms) at tiny scale, not a synthetic-only branch (Gate F.1).
  --smoke     : small-real-scale (cap_eval_concepts=500, max_lines=300000) single unit
                (ckpt_seed_7, DIAG_SEED=20260727) -- fast queue_add.py mechanical gate (<180s).
  --full      : PRIMARY (ckpt_seed_7 x DIAG_SEED in {20260727, 11, 42}) + SECONDARY (relobj_v3
                seed_7, seed_13 x DIAG_SEED=20260727) = 5 units, chunked/resumable via
                experiments._seed_checkpoint (one unit = one "seed" key in that framework).
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

from experiments.exp_scale_meaning_learn_arc_heldout_v2 import (  # noqa: E402
    load_concept_universe, count_pass, build_split, collect_pass,
    build_grounding_reps, encode_concept_text_reps, load_adjacency, _auc_from_scores,
)
from experiments.diag_readout_limit_probe_v1 import load_frozen_encoder  # noqa: E402
from experiments._learned_relational_readout import (  # noqa: E402
    build_train_pairs, fit_diag_probe, fit_bilinear_probe, eval_relational_all_arms,
    arms_must_differ_hashes,
)
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial, aggregate_partials, write_metrics, resumable_seeds,
)
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "relational_readout_promote_v1"

# ---------------------------------------------------------------------------
# Ckpt registry (paths resolved relative to _REPO -- portable local/remote as
# long as both sides mirror the data/ layout under the same relative path;
# the GPU box that trained these IS the remote_cpu_queue/overnight_queue
# target "marsh@home", so the ckpts live at the SAME relative path there).
# ---------------------------------------------------------------------------
CKPT_MLM_V2_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2", "ckpt_seed_7.pt")
CKPT_RELOBJ_V3_SEED7 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_7.pt")
CKPT_RELOBJ_V3_SEED13 = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v3_relobj", "ckpt_seed_13.pt")

PRIMARY_DIAG_SEEDS = [20260727, 11, 42]   # 20260727 = the original diagnostic's seed (reproduction check)
SECONDARY_DIAG_SEED = 20260727

# ---------------------------------------------------------------------------
# Per-mode data-scale configs. FULL_CFG is BYTE-IDENTICAL to
# diag_readout_limit_probe_v1.DIAG_CFG (Gate D: reproduce prior result at
# the SAME test regime, not a different one).
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    run_mode="selftest",
    min_deg=2, cap_eval_concepts=1200, heldout_count=80, min_mentions_eval=1,
    max_lines=100000, dedup_cap=110000, bpe_sample_lines=100, cap_mentions=4,
    max_len=24, n_freq_buckets=3, max_shards=6, encode_batch=128,
    n_anchors=300, max_pos=4, probe_steps=30, bilinear_rank=8,
)
SMOKE_CFG = dict(
    run_mode="smoke",
    min_deg=2, cap_eval_concepts=500, heldout_count=60, min_mentions_eval=4,
    max_lines=300000, dedup_cap=350000, bpe_sample_lines=100, cap_mentions=8,
    max_len=24, n_freq_buckets=6, max_shards=16, encode_batch=256,
    n_anchors=400, max_pos=8, probe_steps=300, bilinear_rank=32,
)
FULL_CFG = dict(
    run_mode="full",
    min_deg=2, cap_eval_concepts=3000, heldout_count=400, min_mentions_eval=8,
    max_lines=3000000, dedup_cap=2000000, bpe_sample_lines=100, cap_mentions=8,
    max_len=24, n_freq_buckets=6, max_shards=16, encode_batch=256,
    n_anchors=2000, max_pos=8, probe_steps=500, bilinear_rank=32,
)

HARD_PASS_MARGIN = 0.03      # << measured 0.0666 (diag); band [0, ~0.067], 5%-width floor = 0.0033
VALIDITY_BAND = (0.40, 0.60)  # SHUFFLE_CONTROL / POPULARITY_CONTROL must land inside this


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
# Units: PRIMARY (mlm_v2_seed7 x 3 diag-seeds) + SECONDARY (relobj cross-seed x 1 diag-seed each)
# ---------------------------------------------------------------------------
def build_units(run_mode):
    if run_mode in ("selftest", "smoke"):
        return [dict(unit_key="mlm_v2_seed7__ds%d" % SECONDARY_DIAG_SEED, ckpt_path=CKPT_MLM_V2_SEED7,
                     ckpt_label="mlm_v2_seed7", diag_seed=SECONDARY_DIAG_SEED, arm_group="PRIMARY")]
    units = []
    for ds in PRIMARY_DIAG_SEEDS:
        units.append(dict(unit_key="mlm_v2_seed7__ds%d" % ds, ckpt_path=CKPT_MLM_V2_SEED7,
                          ckpt_label="mlm_v2_seed7", diag_seed=ds, arm_group="PRIMARY"))
    units.append(dict(unit_key="relobj_v3_seed7__ds%d" % SECONDARY_DIAG_SEED, ckpt_path=CKPT_RELOBJ_V3_SEED7,
                      ckpt_label="relobj_v3_seed7", diag_seed=SECONDARY_DIAG_SEED, arm_group="SECONDARY"))
    units.append(dict(unit_key="relobj_v3_seed13__ds%d" % SECONDARY_DIAG_SEED, ckpt_path=CKPT_RELOBJ_V3_SEED13,
                      ckpt_label="relobj_v3_seed13", diag_seed=SECONDARY_DIAG_SEED, arm_group="SECONDARY"))
    # DEBUG-ONLY preview filter (exp_dev pre-dispatch discriminator-survives-scale check,
    # DISCRIMINATOR-MUST-SURVIVE-SCALE Option C). Never set on the real remote FULL dispatch --
    # absence of the env var (the normal case) returns all 5 units unfiltered.
    only = os.environ.get("HDLAB_UNITS_OVERRIDE")
    if only:
        keep = set(only.split(","))
        units = [u for u in units if u["unit_key"] in keep]
        if not units:
            raise ValueError("HDLAB_UNITS_OVERRIDE=%r matched no unit_key" % only)
    return units


# ---------------------------------------------------------------------------
# Shared (ckpt-independent) bundle: universe / counts / split / postings / adjacency / grounding.
# These depend on `cfg` + the corpus/nodes files, NOT on the encoder checkpoint -- computed ONCE
# per FULL run and reused across every ckpt (the encoder only affects encode_concept_text_reps).
# ---------------------------------------------------------------------------
def build_shared_bundle(cfg, hb=None):
    t_stage = {}
    t0 = time.perf_counter()
    universe = load_concept_universe(cfg)
    t_stage["universe_s"] = time.perf_counter() - t0
    _log("universe K=%d (%.1fs)" % (universe["K"], t_stage["universe_s"]))
    if hb: hb.tick(0, extra={"stage": "universe"}, force=True)

    t0 = time.perf_counter()
    counts, corpus_stats = count_pass(cfg, universe["surf_to_idx"])
    t_stage["count_pass_s"] = time.perf_counter() - t0
    _log("count_pass done (%.1fs) kept=%d dup_rate=%.4f"
         % (t_stage["count_pass_s"], corpus_stats["n_kept"], corpus_stats["dup_rate"]))
    if hb: hb.tick(0, extra={"stage": "count_pass"}, force=True)

    t0 = time.perf_counter()
    split = build_split(universe, counts, cfg)
    t_stage["split_s"] = time.perf_counter() - t0
    _log("split: heldout=%d train_eval=%d" % (split["split_meta"]["n_heldout"], split["split_meta"]["n_train_eval"]))

    t0 = time.perf_counter()
    postings, _bpe_lines, collect_meta = collect_pass(cfg, universe, split)
    t_stage["collect_pass_s"] = time.perf_counter() - t0
    _log("collect_pass done (%.1fs) train_lines=%d held_lines=%d"
         % (t_stage["collect_pass_s"], collect_meta["n_train_lines"], collect_meta["n_held_lines"]))
    if hb: hb.tick(0, extra={"stage": "collect_pass"}, force=True)

    t0 = time.perf_counter()
    adj, deg, n_shards = load_adjacency(universe, cfg)
    t_stage["adjacency_s"] = time.perf_counter() - t0
    _log("adjacency loaded (%.1fs) n_shards=%d" % (t_stage["adjacency_s"], n_shards))

    ground = build_grounding_reps(universe, split)
    if hb: hb.tick(0, extra={"stage": "adjacency_grounding"}, force=True)

    return dict(universe=universe, counts=counts, corpus_stats=corpus_stats, split=split,
               postings=postings, collect_meta=collect_meta, adj=adj, deg=deg,
               n_shards=n_shards, ground=ground, t_stage=t_stage)


def encode_for_ckpt(ckpt_path, cfg, bundle, hb=None):
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError("frozen checkpoint not found: %s" % ckpt_path)
    t0 = time.perf_counter()
    model, tok, spec, ckpt_meta = load_frozen_encoder(ckpt_path)
    load_s = time.perf_counter() - t0
    _log("loaded ckpt %s meta=%s (%.1fs)" % (os.path.basename(ckpt_path), ckpt_meta, load_s))

    t0 = time.perf_counter()
    text_reps, mrep_cnt = encode_concept_text_reps(model, tok, bundle["postings"], cfg, torch.device("cpu"), spec)
    encode_s = time.perf_counter() - t0
    have_text = np.linalg.norm(text_reps, axis=1) > 1e-8
    _log("encode done (%.1fs) concepts_with_text=%d/%d"
         % (encode_s, int(have_text.sum()), bundle["universe"]["K"]))
    if hb: hb.tick(0, extra={"stage": "encode", "ckpt": os.path.basename(ckpt_path)}, force=True)
    return dict(ckpt_meta=ckpt_meta, text_reps=text_reps, have_text=have_text,
               load_s=load_s, encode_s=encode_s, mrep_cnt=mrep_cnt)


# ---------------------------------------------------------------------------
# One unit: fit both probes (TRAIN-TRAIN only) + leak-proof held-out-NEW eval + paired bootstrap CI.
# ---------------------------------------------------------------------------
def run_one_unit(unit, cfg, bundle, enc):
    split = bundle["split"]
    diag_seed = unit["diag_seed"]
    text_reps = enc["text_reps"]
    have_text = enc["have_text"]

    pi, pj, lab, fit_meta = build_train_pairs(split, bundle["adj"], bundle["deg"], have_text, diag_seed,
                                              n_anchors=cfg["n_anchors"], max_pos=cfg["max_pos"])
    if lab.shape[0] < 20:
        raise RuntimeError("too few TRAIN-TRAIN fit pairs (%d) for unit %s" % (lab.shape[0], unit["unit_key"]))

    w_diag, diag_loss = fit_diag_probe(text_reps, pi, pj, lab, steps=cfg["probe_steps"], seed=diag_seed)
    P_bilinear, bilin_loss = fit_bilinear_probe(text_reps, pi, pj, lab, r=cfg["bilinear_rank"],
                                                steps=cfg["probe_steps"], seed=diag_seed)
    diag_moved = float(np.abs(w_diag - 1.0).mean())
    assert diag_moved > 1e-4, "PROBE_DIAG weights did not move from init -- training no-op"

    xi_tr, xj_tr = text_reps[pi], text_reps[pj]
    cos_fit = (xi_tr * xj_tr).sum(axis=1)
    diag_fit_score = (xi_tr * xj_tr * w_diag[None, :]).sum(axis=1)
    proj_i = (P_bilinear @ xi_tr.T).T
    proj_j = (P_bilinear @ xj_tr.T).T
    proj_i = proj_i / (np.linalg.norm(proj_i, axis=1, keepdims=True) + 1e-8)
    proj_j = proj_j / (np.linalg.norm(proj_j, axis=1, keepdims=True) + 1e-8)
    bilin_fit_score = (proj_i * proj_j).sum(axis=1)
    train_auc = dict(cosine=_auc_from_scores(cos_fit, lab.astype(bool)),
                     diag=_auc_from_scores(diag_fit_score, lab.astype(bool)),
                     bilinear=_auc_from_scores(bilin_fit_score, lab.astype(bool)))

    eval_res, per_query = eval_relational_all_arms(text_reps, bundle["ground"], split, bundle["adj"],
                                                   bundle["deg"], have_text, w_diag, P_bilinear, diag_seed,
                                                   _auc_from_scores)

    # META_RULE_AF arms-must-differ hash check (per unit; over the per-query score vectors)
    arm_vecs = {a: np.array([q.get(a, np.nan) for q in per_query]) for a in
               ("BASELINE_COSINE", "PROBE_DIAG", "PROBE_BILINEAR", "SHUFFLE_CONTROL", "POPULARITY_CONTROL")}
    arms_digests = arms_must_differ_hashes(arm_vecs)

    baseline = eval_res["BASELINE_COSINE"]
    diag_auc = eval_res["PROBE_DIAG"]
    bilin_auc = eval_res["PROBE_BILINEAR"]
    n_q = eval_res["_n_query"]
    validity_ok = (eval_res["SHUFFLE_CONTROL"] is not None and VALIDITY_BAND[0] <= eval_res["SHUFFLE_CONTROL"] <= VALIDITY_BAND[1]
                  and eval_res["POPULARITY_CONTROL"] is not None and VALIDITY_BAND[0] <= eval_res["POPULARITY_CONTROL"] <= VALIDITY_BAND[1])

    best_probe = best_probe_auc = margin = None
    if diag_auc is not None and bilin_auc is not None:
        best_probe, best_probe_auc = (("PROBE_DIAG", diag_auc) if diag_auc >= bilin_auc else ("PROBE_BILINEAR", bilin_auc))
        margin = best_probe_auc - baseline if baseline is not None else None

    boot_ci = None
    train_corroborates = None
    if best_probe is not None and n_q >= 10:
        b_vals = np.array([q["BASELINE_COSINE"] for q in per_query])
        p_vals = np.array([q[best_probe] for q in per_query])
        rng_b = np.random.default_rng(diag_seed + 7777)
        n = b_vals.shape[0]
        boot_margins = np.empty(2000, dtype=np.float64)
        for bi in range(2000):
            idx = rng_b.integers(0, n, size=n)
            boot_margins[bi] = p_vals[idx].mean() - b_vals[idx].mean()
        lo, hi = float(np.percentile(boot_margins, 2.5)), float(np.percentile(boot_margins, 97.5))
        boot_ci = dict(probe=best_probe, point_margin=float(p_vals.mean() - b_vals.mean()),
                      ci95_lo=lo, ci95_hi=hi, ci_excludes_zero=bool(lo > 0.0))
        train_key = "diag" if best_probe == "PROBE_DIAG" else "bilinear"
        train_margin = (train_auc[train_key] - train_auc["cosine"]) if (
            train_auc[train_key] is not None and train_auc["cosine"] is not None) else None
        train_corroborates = bool(train_margin is not None and train_margin > 0.0)

    unit_pass = bool(validity_ok and margin is not None and margin >= HARD_PASS_MARGIN
                    and boot_ci is not None and boot_ci["ci_excludes_zero"] and train_corroborates)

    return dict(
        unit_key=unit["unit_key"], ckpt_label=unit["ckpt_label"], ckpt_path=unit["ckpt_path"],
        diag_seed=diag_seed, arm_group=unit["arm_group"], ckpt_meta=enc["ckpt_meta"],
        fit_pairs_meta=fit_meta,
        probe_fit=dict(diag_final_bce=diag_loss, diag_weight_moved=diag_moved,
                       bilinear_final_bce=bilin_loss, bilinear_rank=cfg["bilinear_rank"],
                       train_fit_pair_auc=train_auc),
        held_out_relational_auc=eval_res, validity_ok=validity_ok, n_query=n_q,
        baseline_cosine_auc=baseline, probe_diag_auc=diag_auc, probe_bilinear_auc=bilin_auc,
        best_probe=best_probe, best_probe_auc=best_probe_auc, margin_over_baseline=margin,
        bootstrap_ci=boot_ci, train_corroborates=train_corroborates,
        arms_differ_digests=arms_digests, unit_pass=unit_pass, failure_class=None,
    )


# ---------------------------------------------------------------------------
# Verdict: PRIMARY units (mlm_v2_seed7 x diag-seeds) gate HARD_PASS/MIDDLE_BAND/HARD_FAIL.
# SECONDARY units (relobj cross-seed) are informational (HP_SCOPE excludes them).
# ---------------------------------------------------------------------------
def build_verdict(per_unit, units):
    expected_n = len(units)
    got_n = len(per_unit)
    if got_n != expected_n:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
               "expected %d units, got %d (units=%s)" % (expected_n, got_n, sorted(per_unit.keys())),
               False, expected_n, got_n)

    primary = [v for v in per_unit.values() if v["arm_group"] == "PRIMARY"]
    secondary = [v for v in per_unit.values() if v["arm_group"] == "SECONDARY"]

    any_primary_invalid = any(not v["validity_ok"] for v in primary)
    n_primary_pass = sum(1 for v in primary if v["unit_pass"])
    n_primary = len(primary)

    sec_summary = {v["unit_key"]: dict(ckpt_label=v["ckpt_label"], margin=v["margin_over_baseline"],
                                       validity_ok=v["validity_ok"],
                                       ci_excludes_zero=(v["bootstrap_ci"] or {}).get("ci_excludes_zero"))
                  for v in secondary}

    if any_primary_invalid:
        verdict = "HARD_FAIL_VALIDITY_CONTROL_BREACH"
        msg = ("At least one PRIMARY unit (mlm_v2_seed7) had SHUFFLE_CONTROL/POPULARITY_CONTROL "
              "outside [%.2f,%.2f] -- harness invalid at that unit, cannot trust the readout-lift "
              "reading for this diag-seed. Per-unit validity: %s"
              % (VALIDITY_BAND[0], VALIDITY_BAND[1], {v["unit_key"]: v["validity_ok"] for v in primary}))
    elif n_primary_pass >= 2:
        verdict = "HARD_PASS" if n_primary_pass == n_primary else "HARD_PASS_MAJORITY"
        msg = ("REPLICATED: %d/%d PRIMARY diag-seeds (mlm_v2_seed7) show learned-readout margin "
              ">= %.3f over cosine-NN baseline with bootstrap-CI excluding zero + train-corroboration. "
              "Per-seed margins: %s. SECONDARY (relobj cross-training-seed, informational): %s"
              % (n_primary_pass, n_primary, HARD_PASS_MARGIN,
                 {v["unit_key"]: v["margin_over_baseline"] for v in primary}, sec_summary))
    elif n_primary_pass == 1:
        verdict = "MIDDLE_BAND"
        msg = ("NOT REPLICATED at majority: only 1/%d PRIMARY diag-seeds clear the HARD_PASS bar "
              "(seed-luck cannot be ruled out per the standing seed-luck-over-read discipline). "
              "Per-seed margins: %s. SECONDARY: %s"
              % (n_primary, {v["unit_key"]: v["margin_over_baseline"] for v in primary}, sec_summary))
    else:
        verdict = "HARD_FAIL"
        msg = ("readout-lift finding did NOT replicate: 0/%d PRIMARY diag-seeds cleared margin>=%.3f "
              "with CI excluding zero. Per-seed margins: %s. SECONDARY: %s"
              % (n_primary, HARD_PASS_MARGIN, {v["unit_key"]: v["margin_over_baseline"] for v in primary}, sec_summary))

    return verdict, msg, True, expected_n, got_n


# ---------------------------------------------------------------------------
# Self-test assertions (Gate F.1: exercises the REAL substrate objects at tiny scale)
# ---------------------------------------------------------------------------
def _selftest_assertions(per_unit, verdict):
    assert len(per_unit) == 1, "selftest expected exactly 1 unit"
    v = list(per_unit.values())[0]
    assert not v.get("failure_class"), "selftest unit crashed: %s: %s" % (v.get("failure_class"), v.get("error_msg"))
    assert v["fit_pairs_meta"]["leak_check"] == "PASS_disjoint_from_held", "leak-proof check did not pass"
    assert v["fit_pairs_meta"]["n_pairs"] > 0, "no TRAIN-TRAIN fit pairs built"
    for k in ("BASELINE_COSINE", "PROBE_DIAG", "PROBE_BILINEAR"):
        au = v["held_out_relational_auc"].get(k)
        if au is not None:
            assert 0.0 <= au <= 1.0, "AUC out of range for %s: %s" % (k, au)
    assert len(v["arms_differ_digests"]) >= 3, "arms-must-differ digests missing"
    assert v["ckpt_meta"]["seed"] == 7, "self-test ckpt seed mismatch"
    assert isinstance(v["validity_ok"], bool), "validity_ok not a bool"


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
    units = build_units(cfg["run_mode"])
    unit_keys = [u["unit_key"] for u in units]

    _write_start_marker(out_dir, cfg["run_mode"], len(units))
    _log("run_mode=%s n_units=%d units=%s" % (cfg["run_mode"], len(units), unit_keys))

    t_wall0 = time.perf_counter()
    with CellHeartbeat(out_dir, total_units=len(units), interval_s=30) as hb:
        bundle = build_shared_bundle(cfg, hb=hb)

        _, remaining = resumable_seeds(unit_keys, out_dir, run_config=dict(run_mode=cfg["run_mode"]))
        remaining_set = set(remaining)
        units_by_ckpt = {}
        for u in units:
            if u["unit_key"] in remaining_set:
                units_by_ckpt.setdefault(u["ckpt_path"], []).append(u)

        for ckpt_path, ckpt_units in units_by_ckpt.items():
            enc = encode_for_ckpt(ckpt_path, cfg, bundle, hb=hb)
            for i, u in enumerate(ckpt_units):
                t0 = time.perf_counter()
                try:
                    res = run_one_unit(u, cfg, bundle, enc)
                    res["elapsed_s"] = time.perf_counter() - t0
                except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J); not silent
                    res = dict(unit_key=u["unit_key"], ckpt_label=u["ckpt_label"], ckpt_path=u["ckpt_path"],
                              diag_seed=u["diag_seed"], arm_group=u["arm_group"],
                              failure_class=type(e).__name__, error_msg=str(e)[:500],
                              unit_pass=False, validity_ok=False,
                              elapsed_s=time.perf_counter() - t0)
                    _log("UNIT FAILED %s: %s: %s" % (u["unit_key"], type(e).__name__, e))
                write_partial(out_dir, u["unit_key"], res)
                _log("unit=%s done in %.1fs pass=%s margin=%s" %
                    (u["unit_key"], res["elapsed_s"], res.get("unit_pass"), res.get("margin_over_baseline")))
                hb.tick(len(remaining_set), extra={"unit": u["unit_key"]}, force=True)

    per_unit = aggregate_partials(out_dir, unit_keys)
    verdict, vmsg, cardinality_ok, expected_n, got_n = build_verdict(per_unit, units)
    any_failure_class = any(v.get("failure_class") for v in per_unit.values())
    if any_failure_class and not verdict.startswith("HARD_FAIL"):
        verdict = "HARD_FAIL_UNIT_CRASH"
        vmsg = "One or more units crashed (failure_class set): %s | prior verdict logic: %s" % (
            {k: v.get("failure_class") for k, v in per_unit.items() if v.get("failure_class")}, vmsg)
    _log("VERDICT: %s" % verdict)
    _log(vmsg)

    metrics = dict(
        verdict=verdict, verdict_msg=vmsg, summary=vmsg, anchor_name=ANCHOR_NAME,
        run_mode=cfg["run_mode"], ts_iso=datetime.now(timezone.utc).isoformat(),
        device="cpu", cuda=False, n_units=len(per_unit),
        per_unit=per_unit, cardinality_ok=cardinality_ok,
        expected_n_units=expected_n, got_n_units=got_n,
        bands=dict(hard_pass_margin=HARD_PASS_MARGIN, validity_band=list(VALIDITY_BAND)),
        hp_scope=dict(applies_to=["PRIMARY"], informational_only=["SECONDARY"]),
        diag_cfg=cfg, elapsed_s_total=time.perf_counter() - t_wall0,
        wire_target=("experiments/eval_battery_relational_cloze_v7.py (relational readout arm) + "
                    "the main reasoning loop's relational nearest-neighbor readout (target to be "
                    "confirmed at WIRE time by whoever owns capability_registry.jsonl integration)"),
        known_gap=("No second MLM-v2 training-seed checkpoint exists on disk; PRIMARY replication "
                  "uses DIAG_SEED variation (fit/eval RNG) on the SAME ckpt_seed_7, not a second "
                  "independently-trained encoder. SECONDARY relobj_v3 seed_7/seed_13 gives a genuine "
                  "cross-training-seed check of the MECHANISM (learned readout beats cosine) but on a "
                  "different objective, not the MLM baseline itself."),
    )
    write_metrics(out_dir, metrics, results=list(per_unit.values()))

    if args.self_test:
        _selftest_assertions(per_unit, verdict)
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
