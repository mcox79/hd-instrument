# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified per config (META_RULE_AF; rc.run_config's LEARNED vs RANDOM_INIT eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = LEARNED_WM vs random-init-WM separation on the
#   SAME conditioned reps, judged live (chance=1/V_FILL=0.05, oracle ceiling 1.0).
# - baseline_in_band: RANDOM_INIT_WM control per conditioning MUST stay < RI_NEAR_CHANCE (verifies the
#   conditioning does not trivially leak the label); judged live, imported VERBATIM from rc.
# - discriminator survives scale: FULL is the scale of interest; self-test builds the REAL frozen encoder
#   + REAL conditioned role-separated WM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only (inherited from rc/base); no hash(),
#   no list(set()) (rc/base already comply; this harness adds no new randomness).
"""Binding read-conditioning ENCODER COMPARISON (v1) -- does forward-predictive (latent-PC) encoding make
role-filler binding MORE DIRECTLY READABLE than the MLM v2 encoder needed?

(notes/forward_predictive_second_encoder_build_plan_2026-07-30.md section 3.) THIN FORK of
exp_selective_overwrite_recall_nl_wm_readcond_v1 (`rc`) with exactly ONE change: the frozen encoder
checkpoint is PARAMETERIZED (ENCODER_ARM) instead of hardcoded to base.V2_CKPT. Everything scientific --
the role-separated content-gated WM (rc.ReadCondWM), the VET-confirmed NL Selective-Overwrite-Recall task
(calib), the conditioning arms (none / pca_whiten / combined), the RANDOM_INIT_WM can-fail control, the
WARMSTART_FROZEN honesty diagnostic, and the pre-registered bands (rc.WM_PROVEN_MIN / rc.WM_PARTIAL_MIN /
rc.RI_NEAR_CHANCE / rc.MECH_MARGIN / rc.Z_THRESH) -- is REUSED VERBATIM by importing rc. This is a harness,
not a rewrite.

ENCODER_ARM:
  "MLM_V2" -> base.V2_CKPT (data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt) = the reference row
             (also the self-test encoder; present without the LPC run).
  "LPC"    -> data/exp_encoder_latent_pc_arc_v1/ckpt_seed_<ENCODER_SEED>_ARM_LPC.pt (Fix 2d of the LPC cell)
             = the forward-predictive encoder under test. Can only RUN after the LPC FULL run lands that
             ckpt; BUILD + self-test now (self-test uses MLM_V2 so it needs no LPC ckpt).
The encoder is FIXED at ENCODER_SEED (7) while the WM seeds vary (7,13) -- identical protocol to rc, which
fixes the seed-7 V2 encoder and varies the WM seed. Apples-to-apples by construction (SAME bands, SAME WM).

REDUCED config matrix (section 3.2; the full none/zscore/pca/+aux/+warm matrix already ran for MLM in rc --
reuse those numbers as the MLM_V2 reference row, do NOT re-derive):
  none                -- conditioning=none (reproduce the raw-readability question on THIS encoder)
  pca_whiten          -- whiten-only, NO aux, NO warm-start (the LESS-scaffold test)
  pca_whiten_aux_warm -- combined scaffold = the REPLICATION arm (does read-conditioning generalize across
                         encoders at all? reported regardless of the HARD-WIN/FAIL outcome).

PRE-REGISTERED BANDS (section 3.3; addr/recall chance = 1/V_FILL = 0.05):
  HARD_WIN  = LPC + (none OR pca_whiten-only) reaches eval >= rc.WM_PROVEN_MIN (0.50) on BOTH seeds with
              that conditioning's RANDOM_INIT control < rc.RI_NEAR_CHANCE (0.10) -- binding readable with
              LESS scaffold than MLM needed (strictly higher bar than "combined also works").
  PARTIAL_WIN = LPC + none/whiten-only clears rc.WM_PARTIAL_MIN (0.15) both seeds AND significant over its
              control, but below the proven bar.
  HARD_FAIL = LPC + none AND LPC + pca_whiten-only BOTH stay within the MLM encoder's own none/whiten-only
              near-chance band (<= mlm_ref_band + 0.05) -- forward-prediction did not make binding more
              readable at the representation level.
  MIDDLE_BAND_INCONCLUSIVE = none of the above.
  CONTROL_FLOOR_BROKEN = a RANDOM_INIT control cleared RI_NEAR_CHANCE (a conditioning leaks a shortcut).
  Replication (separate, always reported): LPC + combined scaffold -- proven / partial / did_not_clear.

Run:  .venv/Scripts/python.exe experiments/exp_binding_readcond_encoder_compare_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_binding_readcond_encoder_compare_v1.py --full            (ENCODER_ARM=LPC)
      .venv/Scripts/python.exe experiments/exp_binding_readcond_encoder_compare_v1.py --full --encoder-arm MLM_V2

ASCII-only. No emojis. CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
"""

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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402

ANCHOR_NAME = "binding_readcond_encoder_compare_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- encoder selection (the ONE parameterized axis vs rc) ----
ENCODER_SEED = 7                                   # which trained-encoder seed to freeze (WM seeds vary)
LPC_CKPT_DIR = os.path.join(REPO_ROOT, "data", "exp_encoder_latent_pc_arc_v1")
RC_METRICS = os.path.join(REPO_ROOT, "data", "exp_selective_overwrite_recall_nl_wm_readcond_v1",
                          "metrics.json")

# ---- reduced config matrix (section 3.2): (name, conditioning, aux, warmstart) ----
CONFIGS_CMP = [
    ("none",                 "none",       False, False),   # raw-readability on THIS encoder
    ("pca_whiten",           "pca_whiten", False, False),   # whiten-only (the less-scaffold test)
    ("pca_whiten_aux_warm",  "pca_whiten", True,  True),    # REPLICATION arm (combined scaffold)
]
CONDITIONINGS_USED = ["none", "pca_whiten"]        # RANDOM_INIT controls computed once per conditioning
# HARD_FAIL clause margin: LPC none/whiten within this of the MLM encoder's own near-chance band -> no gain
MLM_BAND_EPS = 0.05
# CITED fallback if the readcond metrics.json is absent (MLM none eval ~ chance).
# MEASURED@commit b3e5c0b7f (rc docstring): none eval acc = [0.061, 0.039] (near CHANCE=0.05).
MLM_REF_FALLBACK_BAND = 0.061


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units, encoder_arm):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node(),
              "encoder_arm": encoder_arm}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- encoder path resolver (the ONE parameterized change) ----------------
def resolve_encoder_ckpt(encoder_arm, encoder_seed=ENCODER_SEED):
    if encoder_arm == "MLM_V2":
        return base.V2_CKPT
    if encoder_arm == "LPC":
        return os.path.join(LPC_CKPT_DIR, "ckpt_seed_%d_%s.pt" % (encoder_seed, "ARM_LPC"))
    raise ValueError("unknown ENCODER_ARM %r (expected MLM_V2 | LPC)" % encoder_arm)


def build_encoder(encoder_arm, encoder_seed=ENCODER_SEED):
    path = resolve_encoder_ckpt(encoder_arm, encoder_seed)
    if not os.path.exists(path):
        raise FileNotFoundError(
            "encoder ckpt for ENCODER_ARM=%s not found: %s%s"
            % (encoder_arm, path,
               " (run the LPC FULL cell first: experiments/exp_encoder_latent_pc_arc_v1.py --full)"
               if encoder_arm == "LPC" else ""))
    enc = base.FrozenV2Encoder(path)               # loader is encoder-agnostic (state_dict+model_cfg+tok)
    n_cached = enc.build_cache()
    return enc, n_cached, os.path.relpath(path, REPO_ROOT)


# ---------------- MLM reference band (read the readcond MLM row; do NOT re-derive) ----------------
def load_mlm_reference():
    ref = {"source": "cited_fallback_b3e5c0b7f", "none": None, "pca_whiten": None,
           "near_chance_band": MLM_REF_FALLBACK_BAND}
    if not os.path.exists(RC_METRICS):
        return ref
    try:
        with open(RC_METRICS, "r", encoding="utf-8") as f:
            m = json.load(f)
    except (OSError, ValueError):
        return ref
    crs = m.get("config_results") or []
    got = {"none": None, "pca_whiten": None}
    for cr in crs:
        if cr.get("name") in got:
            got[cr["name"]] = cr.get("learned_accs")
    accs = [a for k in got for a in (got[k] or [])]
    if accs:
        return {"source": "readcond_metrics", "none": got["none"], "pca_whiten": got["pca_whiten"],
                "near_chance_band": float(max(accs))}
    return ref


# ---------------- verdict (section 3.3; imports bands VERBATIM from rc) ----------------
def decide_compare_verdict(encoder_arm, config_results, ri_controls, mlm_ref, cond_diag):
    by = {c["name"]: c for c in config_results}
    ri_all = [a for r in ri_controls.values() for a in r["accs"]]
    control_floor_ok = all(a < rc.RI_NEAR_CHANCE for a in ri_all)
    ri_max = float(max(ri_all)) if ri_all else 1.0

    replication = by.get("pca_whiten_aux_warm")
    if replication is None:
        replication_status = "not_run"
    elif replication["proven"]:
        replication_status = "proven"
    elif replication["partial"]:
        replication_status = "partial"
    else:
        replication_status = "did_not_clear"

    none_c, whit_c = by.get("none"), by.get("pca_whiten")

    def _proven(c, kind):
        return (c is not None and all(a >= rc.WM_PROVEN_MIN for a in c["learned_accs"])
                and kind in ri_controls and ri_controls[kind]["max"] < rc.RI_NEAR_CHANCE)

    def _partial(c):
        return (c is not None and all(a >= rc.WM_PARTIAL_MIN for a in c["learned_accs"])
                and all(c["significant_per_seed"]))

    band = float(mlm_ref["near_chance_band"]) + MLM_BAND_EPS

    def _in_mlm_band(c):
        return c is not None and all(a <= band for a in c["learned_accs"])

    hard_win = _proven(none_c, "none") or _proven(whit_c, "pca_whiten")
    partial_win = (not hard_win) and (_partial(none_c) or _partial(whit_c))
    hard_fail = _in_mlm_band(none_c) and _in_mlm_band(whit_c)

    best = max(config_results, key=lambda c: max(c["learned_accs"])) if config_results else None

    if encoder_arm == "MLM_V2":
        verdict = "MLM_V2_REFERENCE_ROW"
        msg = ("MLM_V2 reference row re-run on the compare harness (this is NOT the HARD-WIN test -- the "
               "HARD-WIN band applies to ENCODER_ARM=LPC). none=%s pca_whiten=%s combined=%s replication=%s "
               "control_floor_ok=%s (max ri=%.3f)."
               % (none_c["learned_accs"] if none_c else None,
                  whit_c["learned_accs"] if whit_c else None,
                  by.get("pca_whiten_aux_warm", {}).get("learned_accs") if by.get("pca_whiten_aux_warm") else None,
                  replication_status, control_floor_ok, ri_max))
    elif not control_floor_ok:
        verdict = "CONTROL_FLOOR_BROKEN"
        msg = ("a RANDOM_INIT_WM control cleared %.2f (max=%.3f) on some conditioning: the can-fail floor "
               "is not clean; margins untrustworthy. (encoder=%s)" % (rc.RI_NEAR_CHANCE, ri_max, encoder_arm))
    elif hard_win:
        verdict = "HARD_WIN_LPC_BINDING_READABLE_WITH_LESS_SCAFFOLD"
        msg = ("HARD-WIN: LPC encoder makes binding readable with LESS scaffold than MLM needed -- "
               "none/whiten-only reached eval>=%.2f both seeds with control<%.2f. none=%s pca_whiten=%s "
               "(MLM ref band=%.3f from %s). Replication(combined)=%s. Best=%s eval=%s."
               % (rc.WM_PROVEN_MIN, rc.RI_NEAR_CHANCE, none_c["learned_accs"] if none_c else None,
                  whit_c["learned_accs"] if whit_c else None, mlm_ref["near_chance_band"],
                  mlm_ref["source"], replication_status, best["name"], best["learned_accs"]))
    elif partial_win:
        verdict = "PARTIAL_WIN_LPC_REDUCED_SCAFFOLD"
        msg = ("PARTIAL-WIN: LPC none/whiten-only clears eval>=%.2f both seeds AND significant over control "
               "but below the proven bar %.2f. none=%s pca_whiten=%s. Replication(combined)=%s. Best=%s eval=%s."
               % (rc.WM_PARTIAL_MIN, rc.WM_PROVEN_MIN, none_c["learned_accs"] if none_c else None,
                  whit_c["learned_accs"] if whit_c else None, replication_status, best["name"],
                  best["learned_accs"]))
    elif hard_fail:
        verdict = "HARD_FAIL_LPC_NO_MORE_READABLE_THAN_MLM"
        msg = ("HARD-FAIL: LPC none AND whiten-only BOTH stay in the MLM encoder's near-chance band "
               "(<= %.3f+%.2f). Forward-prediction did not make binding more directly readable at the rep "
               "level. none=%s pca_whiten=%s (MLM ref band=%.3f from %s). Replication(combined)=%s -- if "
               "'did_not_clear', the read-conditioning MECHANISM itself may be checkpoint-specific."
               % (mlm_ref["near_chance_band"], MLM_BAND_EPS, none_c["learned_accs"] if none_c else None,
                  whit_c["learned_accs"] if whit_c else None, mlm_ref["near_chance_band"],
                  mlm_ref["source"], replication_status))
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"
        msg = ("MIDDLE_BAND: LPC none/whiten-only neither cleared the proven/partial bar nor stayed inside "
               "the MLM near-chance band. none=%s pca_whiten=%s (MLM ref band=%.3f). Replication(combined)=%s. "
               "Report honestly; do not round up."
               % (none_c["learned_accs"] if none_c else None, whit_c["learned_accs"] if whit_c else None,
                  mlm_ref["near_chance_band"], replication_status))

    bands = {"encoder_arm": encoder_arm, "chance": rc.CHANCE, "wm_proven_min": rc.WM_PROVEN_MIN,
             "wm_partial_min": rc.WM_PARTIAL_MIN, "ri_near_chance": rc.RI_NEAR_CHANCE,
             "mech_margin": rc.MECH_MARGIN, "z_thresh": rc.Z_THRESH, "mlm_band_eps": MLM_BAND_EPS,
             "control_floor_ok": bool(control_floor_ok), "ri_control_max": ri_max,
             "hard_win": bool(hard_win), "partial_win": bool(partial_win), "hard_fail": bool(hard_fail),
             "replication_status": replication_status, "mlm_reference": mlm_ref,
             "best_config": best["name"] if best else None,
             "best_learned_accs": best["learned_accs"] if best else None,
             "raw_query_slot_cos": cond_diag["none"]["query_slot_cos_mean"],
             "pca_query_slot_cos": cond_diag["pca_whiten"]["query_slot_cos_mean"]}
    return verdict, msg, bands


# ---------------- one full comparison run for a chosen encoder ----------------
def run_compare(encoder_arm, encoder_seed, train_n, eval_n, out_dir):
    enc, n_cached, enc_relpath = build_encoder(encoder_arm, encoder_seed)
    _log("encoder=%s ckpt=%s cached %d sentence TOKEN reps (d=%d, L=%d)"
         % (encoder_arm, enc_relpath, n_cached, enc.d, rc.SENT_CAP))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    _log("--- conditioning diagnostic (mechanism the fix targets) ---")
    cond_diag = rc.conditioning_diagnostic(enc, cond, seed=7)
    for kind in CONDITIONINGS_USED:
        d = cond_diag[kind]
        _log("  %-11s query-slot cos=%.3f (distinct=%d/6)"
             % (kind, d["query_slot_cos_mean"], d["untrained_addr_distinct"]))

    datasets = {}
    for seed in rc.SEEDS_FULL:
        tr = calib.gen_dataset(train_n, np.random.default_rng(seed))
        ev = calib.gen_dataset(eval_n, np.random.default_rng(seed + 777))
        datasets[seed] = (rc.build_index_batch(tr, enc, seed), rc.build_index_batch(ev, enc, seed + 777))

    _log("--- random-init controls (can-fail floor per conditioning) ---")
    ri_controls, ri_logits_by = {}, {}
    ctrl_seed = rc.SEEDS_FULL[0]
    ctrl_tr, ctrl_ev = datasets[ctrl_seed]
    for kind in CONDITIONINGS_USED:
        r, lg = rc.run_ri_control(enc, cond, kind, ctrl_tr, ctrl_ev, ctrl_seed, rc.N_RANDOM_INIT)
        ri_controls[kind] = r
        ri_logits_by[kind] = lg

    # per-config LEARNED units with checkpoint/resume (unit = (encoder, config_name); seed granularity is
    # INSIDE rc.run_config, reused verbatim -- forking to split seeds would break the verbatim-reuse contract)
    _log("--- learned configs (checkpointed per config) ---")
    done = ckpt.completed_units(out_dir)
    prior = ckpt.load_units(out_dir) if done else {}
    config_results = []
    for cfg in CONFIGS_CMP:
        name, kind = cfg[0], cfg[1]
        key = ckpt.unit_key(encoder_arm, name)
        if key in done:
            config_results.append(prior[key])         # load_units already unwraps to the result dict
            _log("  config %s: RESUMED from units.jsonl (skip)" % name)
            continue
        _log("=== config: %s (cond=%s aux=%s warm=%s) ===" % cfg)
        res = rc.run_config(cfg, enc, cond, datasets, ri_controls, ri_logits_by)
        config_results.append(res)
        ckpt.record_unit(out_dir, key, res)
    return enc, n_cached, enc_relpath, cond_diag, ri_controls, config_results


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: real frozen encoder (MLM_V2) + conditioner + role split + tiny learned config + arms-differ")
    # encoder path resolver works for BOTH arms (LPC path may not exist yet -- only resolve, don't load)
    assert resolve_encoder_ckpt("MLM_V2").endswith("ckpt_seed_7.pt")
    assert resolve_encoder_ckpt("LPC").endswith("ckpt_seed_7_ARM_LPC.pt")
    # bands imported VERBATIM from rc (no local redefinition)
    for attr in ("WM_PROVEN_MIN", "WM_PARTIAL_MIN", "RI_NEAR_CHANCE", "MECH_MARGIN", "Z_THRESH", "CHANCE"):
        assert hasattr(rc, attr), "rc band %s missing (import drift)" % attr

    enc, n_cached, enc_relpath = build_encoder("MLM_V2")
    assert n_cached >= 3000, "closed sentence set smaller than expected (%d)" % n_cached
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)

    # role split is non-degenerate on conditioned reps
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    wm = rc.ReadCondWM(7, enc.d, rc.D_MEM, rc.K_SLOTS, rc.HIDDEN, rc.V_FILL, rc.ADDR_TEMP, Uc, enc.U_pad_t)
    with torch.no_grad():
        slot_u, fill_u = wm._role_reps()
    assert not torch.allclose(slot_u, fill_u), "slot/fill role reps identical (degenerate split)"

    cond_diag = rc.conditioning_diagnostic(enc, cond, seed=7)
    assert cond_diag["pca_whiten"]["query_slot_cos_mean"] < cond_diag["none"]["query_slot_cos_mean"], \
        "pca_whiten did not reduce the shared component"

    # tiny end-to-end config (pca_whiten+aux) + arms-differ (LEARNED vs RANDOM_INIT), via rc verbatim
    datasets = {7: (rc.build_index_batch(calib.gen_dataset(200, np.random.default_rng(7)), enc, 7),
                    rc.build_index_batch(calib.gen_dataset(200, np.random.default_rng(7 + 777)), enc, 7 + 777))}
    ri, ri_logits = rc.run_ri_control(enc, cond, "pca_whiten", datasets[7][0], datasets[7][1], 7, 2)
    ri_by = {"pca_whiten": ri}
    ri_logits_by = {"pca_whiten": ri_logits}
    saved_steps, saved_seeds = rc.STEPS_WM, rc.SEEDS_FULL
    rc.STEPS_WM, rc.SEEDS_FULL = 60, (7,)
    try:
        res = rc.run_config(("tiny_pca_aux", "pca_whiten", True, False), enc, cond, datasets, ri_by, ri_logits_by)
    finally:
        rc.STEPS_WM, rc.SEEDS_FULL = saved_steps, saved_seeds
    assert res["per_seed"][0]["arms_differ_verified"], "arms bit-identical (LEARNED vs RANDOM_INIT)"
    assert 0.0 <= res["learned_accs"][0] <= 1.0 and 0.0 <= res["ri_mean"] <= 1.0, "acc out of range"

    # MLM reference reader + verdict logic exercise (synthetic config results, both branches)
    mlm_ref = load_mlm_reference()
    assert "near_chance_band" in mlm_ref
    fake_win = [{"name": "none", "learned_accs": [0.9, 0.85], "significant_per_seed": [True, True],
                 "proven": True, "partial": False},
                {"name": "pca_whiten", "learned_accs": [0.88, 0.9], "significant_per_seed": [True, True],
                 "proven": True, "partial": False}]
    v_win, _, _ = decide_compare_verdict("LPC", fake_win,
                                         {"none": {"accs": [0.05, 0.04], "max": 0.05},
                                          "pca_whiten": {"accs": [0.06, 0.05], "max": 0.06}},
                                         {"near_chance_band": 0.06, "source": "t"}, cond_diag)
    assert v_win == "HARD_WIN_LPC_BINDING_READABLE_WITH_LESS_SCAFFOLD", v_win
    fake_fail = [{"name": "none", "learned_accs": [0.06, 0.05], "significant_per_seed": [False, False],
                  "proven": False, "partial": False},
                 {"name": "pca_whiten", "learned_accs": [0.07, 0.06], "significant_per_seed": [False, False],
                  "proven": False, "partial": False}]
    v_fail, _, _ = decide_compare_verdict("LPC", fake_fail,
                                          {"none": {"accs": [0.05, 0.04], "max": 0.05},
                                           "pca_whiten": {"accs": [0.06, 0.05], "max": 0.06}},
                                          {"near_chance_band": 0.06, "source": "t"}, cond_diag)
    assert v_fail == "HARD_FAIL_LPC_NO_MORE_READABLE_THAN_MLM", v_fail

    _log("SELF-TEST PASS (encoder resolver + role split + arms-differ + bands import + verdict branches)")
    return {"n_cached": n_cached, "encoder_ckpt": enc_relpath,
            "tiny": {"learned": res["learned_accs"][0], "ri_mean": res["ri_mean"],
                     "arms_differ": res["per_seed"][0]["arms_differ_verified"]},
            "mlm_reference": mlm_ref, "verdict_branches_ok": True}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--encoder-arm", default="LPC", choices=["LPC", "MLM_V2"])
    ap.add_argument("--encoder-seed", type=int, default=ENCODER_SEED)
    ap.add_argument("--train-n", type=int, default=rc.FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=rc.FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=rc.STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(CONFIGS_CMP)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units, args.encoder_arm)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (encoder resolver + real MLM_V2 encoder + role split + arms-differ "
                           "+ rc bands import + verdict branches)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "encoder_arm": "MLM_V2(selftest)",
            "chance": rc.CHANCE, "selftest": st,
            "start_marker_written": True, "crash_diagnostic_present": True,
            "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    rc.STEPS_WM = args.steps_wm
    _log("FULL: encoder_arm=%s encoder_seed=%d train_n=%d eval_n=%d steps_wm=%d wm_seeds=%s chance=%.4f "
         "configs=%d" % (args.encoder_arm, args.encoder_seed, args.train_n, args.eval_n, rc.STEPS_WM,
                         rc.SEEDS_FULL, rc.CHANCE, len(CONFIGS_CMP)))

    enc, n_cached, enc_relpath, cond_diag, ri_controls, config_results = run_compare(
        args.encoder_arm, args.encoder_seed, args.train_n, args.eval_n, OUTPUT_DIR)

    mlm_ref = load_mlm_reference()
    verdict, msg, bands = decide_compare_verdict(args.encoder_arm, config_results, ri_controls,
                                                 mlm_ref, cond_diag)
    elapsed = time.perf_counter() - t0

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | encoder=%s | chance=%.4f | %s" % (verdict, args.encoder_arm, rc.CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "encoder_arm": args.encoder_arm, "encoder_seed": args.encoder_seed, "encoder_ckpt": enc_relpath,
        "chance": rc.CHANCE, "oracle_ceiling_ref": rc.ORACLE_CEILING, "bands": bands,
        "conditioning_diagnostic": cond_diag, "random_init_controls": ri_controls,
        "config_results": config_results, "mlm_reference": mlm_ref,
        "cardinality_ok": bool(len(config_results) == len(CONFIGS_CMP)),
        "expected_n_units": len(CONFIGS_CMP), "n_units_done": len(config_results),
        "params": {"K_SLOTS": rc.K_SLOTS, "D_MEM": rc.D_MEM, "D_ENC": enc.d, "HIDDEN": rc.HIDDEN,
                   "ADDR_TEMP": rc.ADDR_TEMP, "SENT_CAP": rc.SENT_CAP, "STEPS_WM": rc.STEPS_WM,
                   "STEPS_READOUT": rc.STEPS_READOUT, "LR": rc.LR, "AUX_W": rc.AUX_W, "PCA_EPS": rc.PCA_EPS,
                   "N_RANDOM_INIT": rc.N_RANDOM_INIT, "train_n": args.train_n, "eval_n": args.eval_n,
                   "wm_seeds": list(rc.SEEDS_FULL), "n_cached_sentences": n_cached,
                   "configs": [c[0] for c in CONFIGS_CMP], "encoder_ckpt": enc_relpath},
        "progress_logging": "print_flush_true",
        "checkpoint": {"unit_granularity": "(encoder_arm, config_name)", "helper": "tools/exp_checkpoint.py"},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


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
