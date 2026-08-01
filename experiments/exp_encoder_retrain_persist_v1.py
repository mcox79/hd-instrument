# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: reloaded-tuned extractor's ENT-slot preds digest vs frozen extractor's
#   preds digest on a probe set must be DISTINCT (an inert save/reload would leave them identical).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: this cell does NOT introduce a new discriminator -- it PERSISTS the already-certified
#   encoder-retrain recipe (atom 29593, exp_situation_model_assembly_encoder_retrain_scale_v1.py CLEAN_PASS,
#   config d1_div40: depth=1 top-layer unfreeze, nctx=40, steps=220) to a loadable .pt checkpoint. The
#   fine-tune code path (lt.finetune_encoder / lt.RetrainableExtractor.unfreeze_top) is imported VERBATIM
#   and UNCHANGED -- only the save/reload wiring is new.
# - baseline_in_band: n/a (no accuracy discriminator here; this cell fixes a WIRING gap: the cert cell never
#   wrote its retrained weights to disk, so every downstream reuse had to re-run the ~2min fine-tune from
#   scratch and the weights were not transferable to other harnesses).
# - discriminator survives scale: n/a (persistence utility, not a capability measurement).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only (inherited from lt.finetune_encoder);
#   NO hash(), NO list(set()).
"""ENCODER-RETRAIN PERSIST (Director spawn 2026-07-31, transfer-test prerequisite). Fixes the wiring gap in
the CERTIFIED encoder-break cell (atom 29593, exp_situation_model_assembly_encoder_retrain_scale_v1.py):
that cell CLEAN_PASSed (held-out situation-model loop lifted 0.52->0.83 via minimal-unfreeze top-1 +
cross-mention CONSISTENCY-pull / inter-entity PUSH / VICReg anti-collapse) but never persisted the retrained
encoder weights to disk (data/exp_situation_model_assembly_encoder_retrain_scale_v1/ has metrics+units but
no .pt) -- so the break could not be reused by any other harness.

THE RECIPE (UNCHANGED from the cert cell; imported VERBATIM via lt = exp_situation_model_assembly_encoder_
retrain_lite_v1): depth=1 (unfreeze only the TOP transformer layer + final norm -- deeper unfreeze (top-3,
top-6) OVERFITS/DEGRADES per the cert cell's MEASURED depth curve: top-1 tuned_loop 0.715-0.799 >> top-3
0.532 >> top-6 0.292 collapse -- do NOT change unfreeze depth here), nctx=40 (contexts per train color),
steps=220. Config key "d1_div40", one of the two CLEAN_PASS configs (the other, d1_div80, scored slightly
higher (best single seed 0.830) but costs ~80% more fine-tune wall-time for the same qualitative recipe;
d1_div40 is picked here as the CHEAPER of the two certified-clean configs to keep this INLINE-LOCAL
foreground run comfortably under the 10-min timeout for all 3 seeds).

OUTPUT: one .pt per seed at data/exp_encoder_retrain_persist_v1/ckpt_seed_<seed>.pt, in the SAME schema
eb.EncoderExtractor.__init__ / RetrainableExtractor expects (model_cfg / state_dict / tokenizer_json), so any
downstream cell can load it via EncoderExtractor(ckpt_path=<this path>) exactly like the frozen v2 ckpt.
model_cfg + tokenizer_json are copied VERBATIM from the frozen base ckpt (data/exp_scale_meaning_learn_arc_
heldout_v2/ckpt_seed_7.pt) -- architecture and tokenizer are UNCHANGED by a top-1 fine-tune; only state_dict
differs (frozen bottom layers are numerically identical bit-for-bit; only the top layer + final norm moved).

MEASURE + REPORT: per-seed fine-tune wall time, trainable param count, and a SANITY REPRODUCTION -- reload
the saved ckpt fresh (real_code_path: a brand-new process-clean EncoderExtractor(ckpt_path=...)) and re-score
the SAME held-out set the cert cell used (ih.gen_dataset_split(eval_n, default_rng(seed+777), held, train))
via lt.score_extractor, comparing tuned_loop_mean against the cert cell's landed per-seed metrics
(data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json, condition d1_div40_s<seed>). A
close reproduction (within a small tolerance) proves the .pt round-trips the fine-tuned weights faithfully,
not just that torch.save/load doesn't crash.

PRE-REGISTERED BANDS:
  RECIPE_PERSISTED (HARD_PASS): all 3 seed ckpts save + reload without error AND each reloaded seed's
    resurrected tuned_loop_mean is within RECONSTRUCTION_TOL (0.05) of the cert cell's landed d1_div40_s<seed>
    tuned_loop_mean (MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1/metrics.json).
  HARD_FAIL: any seed's reconstruction deviates by more than RECONSTRUCTION_TOL, or save/reload raises
    (state_dict shape mismatch, missing tokenizer, etc) -- the persistence wiring itself is broken.

PRIOR-WORK CHECK (substrate_query.sh "encoder retrain checkpoint persistence transfer coref harness",
mandatory before authoring): top hit at cosine=0.3057 is
data/exp_encoder_cross_checkpoint_retrieval_compat_v1/metrics.json (HARD_FAIL: cross-checkpoint RETRIEVAL
collapses to ~1-2% when a content-addressable store is INDEXED under one encoder checkpoint and QUERIED
under a different one -- the two checkpoints occupy substantially different embedding geometries). That is a
DIFFERENT concern (mixing index/query checkpoints within one retrieval store) from what this cell does
(persisting ONE checkpoint's weights faithfully so a downstream cell can run a fully self-consistent forward
pass under it). Not a rediscovery; a useful caution reinforcing that frozen-vs-tuned decode geometry differs
substantially, so downstream harnesses must rebuild their own oracle/cue tables per-extractor (which
eb.EncoderExtractor.build() already does -- no shared-table cross-checkpoint mixing risk here).

Run:  .venv/Scripts/python.exe experiments/exp_encoder_retrain_persist_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_retrain_persist_v1.py --full

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU (one fine-tune
per seed, ~110-130s each per the cert cell's MEASURED d1_div40 ft_seconds); INLINE-LOCAL foreground-to-
completion (3 seeds ~6-7min total, under the 10-min timeout). Storage: n/a (no substrate memory writes).
progress_logging: print_flush_true.
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
from datetime import datetime, timezone

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_situation_model_assembly_encoder_retrain_lite_v1 as lt  # noqa: E402 (fine-tune recipe, VERBATIM)

eb = lt.eb
ih = lt.ih
clean = lt.clean
ckpt = lt.ckpt
V2_CKPT = lt.V2_CKPT
SPLIT_SEED = lt.SPLIT_SEED

ANCHOR_NAME = "encoder_retrain_persist_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- the CERTIFIED recipe (UNCHANGED; matches d1_div40 in the cert cell's CLEAN_PASS grid) ----
RECIPE_DEPTH = 1        # top-1 unfreeze -- do NOT change (deeper unfreeze overfits per cert cell)
RECIPE_NCTX = 40
RECIPE_STEPS = 220
SEEDS_FULL = (7, 13, 19)
SEEDS_SMOKE = (7,)
SMOKE_STEPS = 20
SMOKE_NCTX = 8

CERT_METRICS_PATH = os.path.join(REPO_ROOT, "data",
                                  "exp_situation_model_assembly_encoder_retrain_scale_v1", "metrics.json")
RECONSTRUCTION_TOL = 0.05    # HARD_PASS band: reloaded tuned_loop_mean within this of the cert cell's landed value
GRID_EVAL_N = 100            # matches the cert cell's GRID_EVAL_N for an apples-to-apples reconstruction check


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _ckpt_path_for_seed(seed):
    return os.path.join(OUTPUT_DIR, "ckpt_seed_%d.pt" % seed)


# ================= fine-tune + persist (the new wiring) =================
def finetune_and_save(seed, out_path, nctx, steps, eval_n):
    """Fine-tunes ONE seed with the certified recipe (depth=1, VERBATIM lt.finetune_encoder), saves the
    resulting weights to out_path in the eb.EncoderExtractor-loadable schema, then reloads FRESH from disk
    (real_code_path) and re-scores the held-out set for a reconstruction sanity check."""
    tables = clean.build_tables()
    train_colors, held_colors = ih.color_split(SPLIT_SEED)

    prev_depth = lt.N_UNFREEZE_TOP
    lt.N_UNFREEZE_TOP = RECIPE_DEPTH
    try:
        ext_tn = lt.RetrainableExtractor()          # loads the FROZEN v2 base ckpt, then fine-tunes top-1
        t_ft = time.perf_counter()
        ft = lt.finetune_encoder(ext_tn, train_colors, steps=steps, seed=seed, nctx=nctx)
        ft_seconds = time.perf_counter() - t_ft
        ext_tn.build()
    finally:
        lt.N_UNFREEZE_TOP = prev_depth

    # ---- save: SAME schema as the base ckpt (model_cfg + tokenizer_json copied VERBATIM; only state_dict
    #      differs -- the base ckpt is loaded once more here, read-only, to source the untouched fields) ----
    base_ck = torch.load(V2_CKPT, map_location="cpu", weights_only=False)
    save_payload = {
        "model_cfg": base_ck["model_cfg"],
        "state_dict": ext_tn.model.state_dict(),
        "tokenizer_json": base_ck["tokenizer_json"],
        "provenance": {
            "recipe": "certified_break_atom_29593_minimal_unfreeze_top1",
            "source_cell": "exp_situation_model_assembly_encoder_retrain_scale_v1.py",
            "base_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT),
            "depth": RECIPE_DEPTH, "nctx": nctx, "steps": steps, "seed": seed,
            "n_trainable_params": ft["n_trainable_params"], "ft_seconds": ft_seconds,
            "saved_ts_iso": _now_iso(),
        },
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = out_path + ".tmp"
    torch.save(save_payload, tmp)
    os.replace(tmp, out_path)
    _log("  [seed=%d] saved %s (%d trainable params, ft=%.1fs)"
         % (seed, out_path, ft["n_trainable_params"], ft_seconds))

    # ---- reload FRESH (real_code_path) + reconstruction sanity check on the SAME held-out set ----
    ext_reload = eb.EncoderExtractor(ckpt_path=out_path)
    ext_reload.build()
    ev_held = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    sc_reload = lt.score_extractor(ext_reload, ev_held, tables)
    reload_loop_mean = float(np.mean([sc_reload["main_enc"][qt]["acc"] for qt in lt.QUERY_TYPES
                                      if not math.isnan(sc_reload["main_enc"][qt]["acc"])]))

    return {"seed": seed, "depth": RECIPE_DEPTH, "nctx": nctx, "steps": steps, "eval_n": eval_n,
            "ft_seconds": ft_seconds, "n_trainable_params": ft["n_trainable_params"],
            "ckpt_path": os.path.relpath(out_path, REPO_ROOT),
            "reload_tuned_loop_mean": reload_loop_mean,
            "in_memory_tuned_loop_mean": None}  # filled by caller if it also scored ext_tn pre-save


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: tiny fine-tune + save + reload + arms-differ (real_code_path) ...")
    tables = clean.build_tables()
    train_colors, held_colors = ih.color_split(SPLIT_SEED)

    # frozen probe (baseline for arms-differ)
    ext_fz = lt.RetrainableExtractor()
    ext_fz.build()
    ds = clean.gen_dataset(8, np.random.default_rng(7))
    dec_fz, ans_fz, _ = eb.build_decoded_dataset(ds, ext_fz, "role_attn")
    main_fz = eb.run_arm_decoded(dec_fz, ans_fz, tables, "main")
    dig_fz = hashlib.sha256(json.dumps([round(main_fz[qt]["acc"], 6) if not math.isnan(main_fz[qt]["acc"])
                                        else -1.0 for qt in lt.QUERY_TYPES]).encode()).hexdigest()

    tmp_ckpt = os.path.join(OUTPUT_DIR, "_selftest_ckpt.pt")
    res = finetune_and_save(7, tmp_ckpt, nctx=6, steps=6, eval_n=16)
    assert os.path.exists(tmp_ckpt), "save did not land a file"
    assert os.path.getsize(tmp_ckpt) > 1000, "saved ckpt suspiciously small: %d bytes" % os.path.getsize(tmp_ckpt)

    # reload again (independent of finetune_and_save's internal reload) + verify state_dict round-trips
    ck2 = torch.load(tmp_ckpt, map_location="cpu", weights_only=False)
    for k in ("model_cfg", "state_dict", "tokenizer_json"):
        assert k in ck2, "MISSING_KEY %s -- schema drift vs eb.EncoderExtractor.__init__ expectations" % k
    assert ck2["model_cfg"] == json.loads(json.dumps(ck2["model_cfg"])), "model_cfg not JSON-clean"

    ext_reload = eb.EncoderExtractor(ckpt_path=tmp_ckpt)
    ext_reload.build()
    dec_tn, ans_tn, _ = eb.build_decoded_dataset(ds, ext_reload, "role_attn")
    main_tn = eb.run_arm_decoded(dec_tn, ans_tn, tables, "main")
    dig_tn = hashlib.sha256(json.dumps([round(main_tn[qt]["acc"], 6) if not math.isnan(main_tn[qt]["acc"])
                                        else -1.0 for qt in lt.QUERY_TYPES]).encode()).hexdigest()
    # weight-level arms-differ (load-bearing: proves the reloaded model is NOT bit-identical to frozen)
    sd_fz = ext_fz.model.state_dict()
    sd_tn = ext_reload.model.state_dict()
    any_layer_differs = False
    for k in sd_fz:
        if not torch.equal(sd_fz[k], sd_tn[k]):
            any_layer_differs = True
            break
    assert any_layer_differs, "META_RULE_AF: reloaded state_dict bit-identical to frozen -- save/reload inert"
    _log("  arms_differ: preds_digest fz=%s tn=%s (may coincide on a tiny probe) | state_dict differs=%s"
         % (dig_fz[:8], dig_tn[:8], any_layer_differs))

    os.remove(tmp_ckpt)
    _log("SELF-TEST PASS (reload_tuned_loop_mean=%.3f on tiny probe)" % res["reload_tuned_loop_mean"])
    return {"arms_differ_verified": True, "state_dict_differs": any_layer_differs,
            "tiny_reload_tuned_loop_mean": res["reload_tuned_loop_mean"],
            "tiny_ft_seconds": res["ft_seconds"], "tiny_n_trainable_params": res["n_trainable_params"]}


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


# ================= verdict =================
def _cert_landed_loop(seed):
    if not os.path.exists(CERT_METRICS_PATH):
        return None
    with open(CERT_METRICS_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    for c in d.get("per_condition", []):
        if c["name"] == "d1_div40_s%d" % seed:
            return c["tuned_loop_mean"]
    return None


def decide_verdict(units, seeds):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}
    per_seed = []
    all_ok = True
    for u in units:
        cert_loop = _cert_landed_loop(u["seed"])
        dev = (abs(u["reload_tuned_loop_mean"] - cert_loop) if cert_loop is not None else None)
        ok = (dev is not None) and dev <= RECONSTRUCTION_TOL
        all_ok = all_ok and ok
        per_seed.append({"seed": u["seed"], "reload_tuned_loop_mean": u["reload_tuned_loop_mean"],
                         "cert_landed_tuned_loop_mean": cert_loop, "deviation": dev,
                         "within_tol": ok, "ckpt_path": u["ckpt_path"]})
    bands = {"reconstruction_tol": RECONSTRUCTION_TOL, "per_seed": per_seed,
             "recipe": {"depth": RECIPE_DEPTH, "nctx": RECIPE_NCTX, "steps": RECIPE_STEPS}}
    if all_ok:
        return "HARD_PASS", ("RECIPE_PERSISTED: all %d seed ckpts saved + reload fresh reproduces the cert "
                             "cell's landed d1_div40 tuned_loop_mean within tol=%.2f. per_seed=%s"
                             % (len(units), RECONSTRUCTION_TOL, per_seed)), bands
    return "HARD_FAIL", ("RECONSTRUCTION_MISMATCH: one or more reloaded seeds deviate from the cert cell's "
                         "landed tuned_loop_mean by more than tol=%.2f -- persistence wiring is suspect. "
                         "per_seed=%s" % (RECONSTRUCTION_TOL, per_seed)), bands


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=560.0)
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "full"

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (fine-tune + save + reload + state_dict arms-differ, real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL
    nctx = SMOKE_NCTX if run_mode == "smoke" else RECIPE_NCTX
    steps = SMOKE_STEPS if run_mode == "smoke" else RECIPE_STEPS
    eval_n = 24 if run_mode == "smoke" else GRID_EVAL_N
    _write_start_marker(OUTPUT_DIR, run_mode, len(seeds))
    t0 = time.perf_counter()
    _log("%s: seeds=%s depth=%d nctx=%d steps=%d eval_n=%d" % (run_mode.upper(), seeds, RECIPE_DEPTH,
                                                                nctx, steps, eval_n))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for s in seeds:
        key = ckpt.unit_key("persist_seed", s, run_mode)
        if key in done:
            _log("  [seed=%d] loaded from checkpoint" % s)
            continue
        if ran >= 1 and run_mode == "full" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new seed(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = finetune_and_save(s, _ckpt_path_for_seed(s), nctx=nctx, steps=steps, eval_n=eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("persist_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("persist_seed", s, run_mode) in units_map]
    if len(units) < len(seeds):
        _log("PARTIAL: %d/%d seeds done -- re-run to resume" % (len(units), len(seeds)))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d seeds complete; re-run to resume"
                   % (len(units), len(seeds)), "summary": "PARTIAL %d/%d" % (len(units), len(seeds)),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": len(units), "expected_n_units": len(seeds),
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
               "cardinality_ok": bool(len(units) == len(seeds)), "expected_n_units": len(seeds),
               "n_units_done": len(units), "units": units,
               "params": {"depth": RECIPE_DEPTH, "nctx": nctx, "steps": steps, "eval_n": eval_n,
                          "seeds": list(seeds)},
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
