"""METACOGNITION / ABSTAIN CONFORMAL-TRANSFER: does a CONFORMAL-calibrated abstain threshold on
the reader's learned cue-score TRANSFER from a CALIBRATION split to a DISJOINT TEST split?

HARDENS chain-grade atom 29367 (exp_metacog_abstain_readout_signal_thresholding_v1): S1
reader_best_score cut confident-wrong 0.732 -> 0.493 @cov0.50 (rel_red 0.327), p=0.0, 3 seeds,
NO gold leakage -- BUT the abstain operating point (coverage/threshold) was chosen IN-SAMPLE on
the same held-out eval it measured. Open caveat: transfer to fresh text UNTESTED. This cell
resolves it with SPLIT-CONFORMAL: calibrate the threshold on one split, apply to a disjoint one.

METHOD (build-on, credited): split-conformal prediction (Vovk/Gammerman/Shafer 2005;
Angelopoulos & Bates 2021) via hdlab/conformal.py, plus the 3 cheap closed-form pieces the
self-monitoring scour flagged missing (Mondrian per-partition quantiles, Gibbs & Candes 2021
adaptive-alpha, Chow 1970 set-size reject rule). Abstain = Chow reject option on a conformal set.

SAME held-out reader eval as 29367: we REUSE build_pop_lccp() from the original cell (no code
drift) to build the exact POP-LCCP population (per verb-instance reader learned cue-score S1 +
gold-correct), for reader seeds [7,13,19]. n=142 verb-instances/seed. base_wrong=0.732.
MEASURED@data/exp_metacog_abstain_readout_signal_thresholding_v1/metrics.json.

TRANSFER PROCEDURE (one variable = the SELECTION RULE at matched coverage):
  nonconformity s_i = -reader_best_score_i (lower s = higher confidence = keep).
  For each (reader_seed, split_seed): random 50/50 split instances -> CAL, TEST (disjoint).
    q = calibrate_quantile(s_CAL, alpha=1-target_cov)   # conformal (1-alpha) quantile on CAL only
    keep_TEST = {i in TEST : s_i <= q}                  # applied to the DISJOINT split
    realized_cov = mean(keep_TEST);  confident_wrong = wrong_rate among kept on TEST
    rel_reduction = (base_wrong_TEST - confident_wrong) / base_wrong_TEST
    RANDOM-abstain control at MATCHED realized coverage on TEST (bootstrap band, one-sided p).
    transfer_gap = confident_wrong_TEST - confident_wrong_CAL (overfit probe).
  Aggregate MEDIAN over N_SPLITS x reader_seeds.

PRE-REGISTERED BANDS (BEFORE running; NOT tuned to pass). Primary target_cov=0.50 (== 29367
operating point). Verdict on the DISJOINT TEST split, median over 200 splits x 3 reader seeds:
  In-sample reference (29367): rel_red=0.327, confident_wrong=0.493, base_wrong=0.732 (THEORETICAL
    anchors for tolerance; from the on-disk 29367 metrics).
  HARD_PASS (ALL of):
    T1 coverage valid : median realized TEST keep-fraction in [0.45, 0.60]
    T2 reduction transfers: median rel_reduction_TEST >= 0.20 (retains ~60%+ of in-sample 0.327,
                            clears the 29367-era MIDDLE floor 0.15 with margin)
    T3 beats random   : fraction of splits with confident_wrong_TEST beating random-abstain p2.5
                        (one-sided p<0.05) >= 0.60 AND pooled median TEST point beats random p2.5
    T4 honest calib   : median transfer_gap (test_cw - cal_cw) <= 0.12 (threshold not overfit)
  HARD_FAIL (ANY of):
    median rel_reduction_TEST < 0.15 (no transfer; threshold overfit CAL) OR
    median realized coverage outside [0.40, 0.65] (miscalibrated) OR
    fraction of splits beating random < 0.40
  MIDDLE_BAND: transfer present but attenuated (between the two -- real but weak transfer).

DISCRIMINATOR-FIRES / CAN-FAIL gates (must hold or population vacuous):
  base_wrong_TEST median in (0.15, 0.85); reader_best_score non-degenerate variance;
  MUST-FAIL control = RANDOM-abstain threshold does NOT transfer (rel_red ~0, does not beat itself).
  The test genuinely CAN fail: if the cov=0.50 point was cherry-picked in-sample, a CAL-calibrated
  threshold will NOT reproduce the reduction on disjoint TEST.

SECONDARY (reported, NON-gating): (a) target_cov grid {0.50,0.60,0.70} robustness; (b) Mondrian
per-partition (seen-verb vs held-out-verb) coverage on TEST -- does group-conditional calibration
improve coverage validity; (c) adaptive-alpha online coverage tracking over the TEST stream.

COMPUTE ARCHITECTURE: class (b) sequential-CPU. Building 3 reader-seed populations ~30-45s
(GloVe cosines + tiny logistic, reused from 29367); splits are pure numpy. Foreground
local-to-completion (< ~90s). NO queue, NO push, NO remote-persist, NO git add.
needs_orchestrator_store_sync=True (metrics only). LOCAL-ONLY.

CELL-TEMPLATE MANDATES: except SystemExit: raise before except Exception (no BaseException);
  atomic tmp+os.replace metrics; start-marker; crash-diagnostic; arms-differ (conformal vs random);
  baseline_in_band; FIXED integer seeds only (no hash()-derived seeding); ASCII-only; print flush.
"""
import os
import sys
import json
import time
import hashlib
import traceback
from datetime import datetime, timezone
from collections import defaultdict

import numpy as np
import torch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.conformal import (calibrate_quantile, calibrate_quantile_mondrian,
                             adaptive_alpha_update, empirical_coverage)

ANCHOR_NAME = "metacog_abstain_conformal_transfer_v1"

# ---- pre-registered constants (NOT tuned to pass) ----
FULL_SLICE = ["L04", "L05", "L07", "L08", "L09", "L10", "L12"]  # == 29367 LCCP slice
SMOKE_SLICE = ["L04", "L05"]
READER_SEEDS = [7, 13, 19]
TARGET_COV_PRIMARY = 0.50            # == 29367 operating point; alpha = 1 - cov
TARGET_COV_GRID = [0.50, 0.60, 0.70]
SPLIT_FRAC_CAL = 0.50               # 50/50 cal/test
N_SPLITS_FULL = 200
N_SPLITS_SMOKE = 40
BOOT_DRAWS = 1000                   # random-abstain matched-coverage baseline per split
ALPHA_SIG = 0.05                    # one-sided beats-random significance
BASE_SPLIT_SEED = 20260720         # fixed integer; NEVER hash()-derived

# In-sample reference (29367) -- THEORETICAL anchors for tolerance bands (from on-disk metrics)
INSAMPLE_RELRED = 0.327
INSAMPLE_CW = 0.493
INSAMPLE_BASEWRONG = 0.732

# pre-registered band thresholds
HP_COV_LO, HP_COV_HI = 0.45, 0.60
HP_RELRED = 0.20
HP_BEATS_FRAC = 0.60
HP_GAP_MAX = 0.12
HF_RELRED = 0.15
HF_COV_LO, HF_COV_HI = 0.40, 0.65
HF_BEATS_FRAC = 0.40
BASE_WRONG_LO, BASE_WRONG_HI = 0.15, 0.85


# ----------------------------------------------------------------------------------------------
# population build -- REUSE the 29367 population (no code drift) + capture verb/heldout for Mondrian
# ----------------------------------------------------------------------------------------------
def build_pop_lccp_ext(slice_lessons, seed):
    """Return (best_score[], correct[bool], group[str]) per verb-instance for one reader seed.
    best_score/correct are bit-identical to 29367's build_pop_lccp; group = seen|heldout verb."""
    from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L
    order, sent_text, reader_svo = L.load_slice_and_reader(slice_lessons)
    gold, _gm = L.load_gold(slice_lessons)
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)
    cfg = dict(L.cfg_full()); cfg["slice_lessons"] = slice_lessons; cfg["seed"] = seed
    decisions, artifacts, subcat_decisions, heldout_verbs, seen_verbs, inst_groups, w = L.run_arms(
        order, reader_svo, sent_text, glove, cfg, seed)
    heldout = set(heldout_verbs) if heldout_verbs is not None else set()
    best_score, correct, group = [], [], []
    for (sid, v), cs in inst_groups.items():
        best = max(cs, key=lambda c: L.score_cand(w, c["feat"]))
        top1 = max(L.score_cand(w, c["feat"]) for c in cs)
        best_score.append(float(top1))
        rec = gold.get(sid, {"pos": []})
        g = L.match_pos(best["v"], best["tup"][2], rec.get("pos", []))
        correct.append(g is not None)
        group.append("heldout" if v in heldout else "seen")
    return (np.asarray(best_score, dtype=np.float64), np.asarray(correct, dtype=bool),
            np.asarray(group, dtype=object))


# ----------------------------------------------------------------------------------------------
# transfer core
# ----------------------------------------------------------------------------------------------
def _wrong_rate_kept(wrong, keep_mask):
    k = int(keep_mask.sum())
    if k == 0:
        return None, 0
    return float(wrong[keep_mask].mean()), k


def _random_abstain_p(wrong_test, k_keep, n_draws, rng):
    """Random-abstain at MATCHED coverage: keep random size-k subset. Return (p2.5, p50, draws)."""
    n = len(wrong_test)
    if k_keep <= 0 or k_keep > n:
        return None, None, None
    rates = np.empty(n_draws, dtype=np.float64)
    for d in range(n_draws):
        idx = rng.choice(n, size=k_keep, replace=False)
        rates[d] = wrong_test[idx].mean()
    rates.sort()
    return float(np.percentile(rates, 2.5)), float(np.percentile(rates, 50.0)), rates


def run_one_split(score, correct, group, target_cov, split_seed, boot_draws):
    """One CAL/TEST split at one target coverage. Returns dict of transfer metrics or None if degenerate."""
    n = len(score)
    rng = np.random.default_rng(split_seed)
    perm = rng.permutation(n)
    n_cal = max(2, int(round(SPLIT_FRAC_CAL * n)))
    cal_idx, test_idx = perm[:n_cal], perm[n_cal:]
    if len(test_idx) < 2:
        return None
    s = -score  # nonconformity: lower = more conformal = keep
    wrong = (~correct).astype(np.float64)
    alpha = 1.0 - target_cov
    q = calibrate_quantile(torch.as_tensor(s[cal_idx]), alpha=alpha)

    keep_test = s[test_idx] <= q
    keep_cal = s[cal_idx] <= q
    base_wrong_test = float(wrong[test_idx].mean())
    cw_test, k_test = _wrong_rate_kept(wrong[test_idx], keep_test)
    cw_cal, _ = _wrong_rate_kept(wrong[cal_idx], keep_cal)
    if cw_test is None or k_test == 0 or base_wrong_test <= 0:
        return None
    realized_cov = float(keep_test.mean())
    rel_red = (base_wrong_test - cw_test) / base_wrong_test
    transfer_gap = cw_test - (cw_cal if cw_cal is not None else cw_test)

    # random-abstain control at MATCHED coverage on TEST (one variable = selection rule)
    rp = np.random.default_rng(split_seed + 1)
    p25, p50, draws = _random_abstain_p(wrong[test_idx], k_test, boot_draws, rp)
    beats = bool(cw_test < p25) if p25 is not None else False
    perm_p = float(np.mean(draws <= cw_test + 1e-12)) if draws is not None else 1.0

    return {"target_cov": target_cov, "q": q, "realized_cov": realized_cov,
            "base_wrong_test": base_wrong_test, "cw_test": cw_test, "cw_cal": cw_cal,
            "rel_red": rel_red, "transfer_gap": transfer_gap, "k_test": k_test,
            "n_test": len(test_idx), "rand_p2.5": p25, "rand_p50": p50,
            "beats_random": beats, "perm_p": perm_p}


def mondrian_vs_pooled(score, correct, group, target_cov, split_seed):
    """Assess Mondrian (per-partition) vs pooled per-group coverage on the disjoint TEST split.
    Non-gating. Returns per-group realized coverage under pooled q and Mondrian q_g."""
    n = len(score)
    rng = np.random.default_rng(split_seed + 7)
    perm = rng.permutation(n)
    n_cal = max(2, int(round(SPLIT_FRAC_CAL * n)))
    cal_idx, test_idx = perm[:n_cal], perm[n_cal:]
    s = -score
    alpha = 1.0 - target_cov
    groups_cal = list(group[cal_idx])
    uniq = sorted(set(groups_cal))
    if len(uniq) < 2:
        return {"applicable": False, "reason": "single_group_in_cal", "groups": uniq}
    q_pool = calibrate_quantile(torch.as_tensor(s[cal_idx]), alpha=alpha)
    qs = calibrate_quantile_mondrian(torch.as_tensor(s[cal_idx]), groups_cal, alpha=alpha, min_group=3)
    out = {"applicable": True, "per_group": {}}
    for g in uniq:
        gmask = np.asarray([gg == g for gg in group[test_idx]], dtype=bool)
        if gmask.sum() == 0:
            continue
        st = s[test_idx][gmask]
        cov_pool = float((st <= q_pool).mean())
        cov_mond = float((st <= qs.get(g, q_pool)).mean())
        out["per_group"][g] = {"n_test": int(gmask.sum()), "target": target_cov,
                               "cov_pooled": cov_pool, "cov_mondrian": cov_mond}
    return out


def adaptive_alpha_track(score, correct, target_cov, split_seed, gamma=0.05):
    """Online adaptive-alpha (Gibbs-Candes) over the TEST stream: track realized coverage vs target.
    Non-gating. Returns final alpha + realized long-run coverage vs the target, and the static
    (fixed-alpha) coverage for contrast."""
    n = len(score)
    rng = np.random.default_rng(split_seed + 11)
    perm = rng.permutation(n)
    n_cal = max(2, int(round(SPLIT_FRAC_CAL * n)))
    cal_idx, test_idx = perm[:n_cal], perm[n_cal:]
    s = -score
    target_alpha = 1.0 - target_cov
    s_cal = torch.as_tensor(s[cal_idx])
    # static baseline
    q_static = calibrate_quantile(s_cal, alpha=target_alpha)
    cov_static = float((s[test_idx] <= q_static).mean())
    # online: recalibrate q from the (fixed) cal set at the evolving alpha; covered iff s<=q
    a = target_alpha
    covered_hist = []
    for i in test_idx:
        q_t = calibrate_quantile(s_cal, alpha=min(max(a, 1e-3), 0.999))
        covered = 1.0 if s[i] <= q_t else 0.0
        covered_hist.append(covered)
        a = adaptive_alpha_update(a, miscovered=1.0 - covered, target_alpha=target_alpha, gamma=gamma)
    cov_online = float(np.mean(covered_hist)) if covered_hist else 0.0
    return {"target_cov": target_cov, "cov_static": cov_static, "cov_online": cov_online,
            "final_alpha": float(a)}


def _digest(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.float64).tobytes()).hexdigest()


# ----------------------------------------------------------------------------------------------
# analyze
# ----------------------------------------------------------------------------------------------
def analyze(slice_lessons, n_splits, boot_draws, reader_seeds):
    t0 = time.perf_counter()
    pops = {}
    for sd in reader_seeds:
        bs, cor, grp = build_pop_lccp_ext(slice_lessons, sd)
        pops[sd] = {"score": bs, "correct": cor, "group": grp}
        print(f"[pop] seed={sd} n={len(bs)} base_wrong={float((~cor).mean()):.3f} "
              f"score_var={float(bs.var()):.4g} groups={dict(zip(*np.unique(grp, return_counts=True)))} "
              f"elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    # ---- PRIMARY: transfer at target_cov=0.50, median over splits x seeds ----
    prim = {"target_cov": TARGET_COV_PRIMARY, "per_split": []}
    for sd in reader_seeds:
        p = pops[sd]
        for j in range(n_splits):
            split_seed = BASE_SPLIT_SEED + j * 7919 + sd * 104729
            r = run_one_split(p["score"], p["correct"], p["group"], TARGET_COV_PRIMARY,
                              split_seed, boot_draws)
            if r is not None:
                r["reader_seed"] = sd
                prim["per_split"].append(r)
    ps = prim["per_split"]
    n_ok = len(ps)

    def med(key):
        return float(np.median([r[key] for r in ps])) if ps else None

    prim_summary = {
        "n_splits_ok": n_ok,
        "median_realized_cov": med("realized_cov"),
        "median_base_wrong_test": med("base_wrong_test"),
        "median_cw_test": med("cw_test"),
        "median_rel_red": med("rel_red"),
        "median_transfer_gap": med("transfer_gap"),
        "frac_beats_random": float(np.mean([r["beats_random"] for r in ps])) if ps else None,
        "iqr_rel_red": [float(np.percentile([r["rel_red"] for r in ps], 25)),
                        float(np.percentile([r["rel_red"] for r in ps], 75))] if ps else None,
        "pooled_median_cw": med("cw_test"),
        "pooled_median_rand_p2.5": med("rand_p2.5"),
    }
    prim_summary["pooled_beats_random"] = bool(
        prim_summary["pooled_median_cw"] is not None and prim_summary["pooled_median_rand_p2.5"] is not None
        and prim_summary["pooled_median_cw"] < prim_summary["pooled_median_rand_p2.5"])

    # ---- MUST-FAIL control: RANDOM threshold (shuffle score) must NOT transfer ----
    ctrl_relred = []
    for sd in reader_seeds:
        p = pops[sd]
        rngc = np.random.default_rng(BASE_SPLIT_SEED + sd)
        for j in range(min(n_splits, 60)):
            shuffled = p["score"].copy()
            rngc.shuffle(shuffled)  # destroy score<->correct alignment
            split_seed = BASE_SPLIT_SEED + j * 7919 + sd * 104729
            r = run_one_split(shuffled, p["correct"], p["group"], TARGET_COV_PRIMARY, split_seed, 200)
            if r is not None:
                ctrl_relred.append(r["rel_red"])
    ctrl_median_relred = float(np.median(ctrl_relred)) if ctrl_relred else None

    # ---- SECONDARY: target-cov grid robustness ----
    grid = {}
    for tc in TARGET_COV_GRID:
        rr, cov, beats = [], [], []
        for sd in reader_seeds:
            p = pops[sd]
            for j in range(min(n_splits, 80)):
                split_seed = BASE_SPLIT_SEED + j * 7919 + sd * 104729
                r = run_one_split(p["score"], p["correct"], p["group"], tc, split_seed, 400)
                if r is not None:
                    rr.append(r["rel_red"]); cov.append(r["realized_cov"]); beats.append(r["beats_random"])
        grid[str(tc)] = {"median_rel_red": float(np.median(rr)) if rr else None,
                         "median_realized_cov": float(np.median(cov)) if cov else None,
                         "frac_beats_random": float(np.mean(beats)) if beats else None}

    # ---- SECONDARY: Mondrian per-partition coverage (aggregate over splits) ----
    mond_agg = defaultdict(lambda: {"cov_pooled": [], "cov_mondrian": [], "n": 0})
    mond_applicable = 0
    for sd in reader_seeds:
        p = pops[sd]
        for j in range(min(n_splits, 60)):
            split_seed = BASE_SPLIT_SEED + j * 7919 + sd * 104729
            m = mondrian_vs_pooled(p["score"], p["correct"], p["group"], TARGET_COV_PRIMARY, split_seed)
            if m.get("applicable"):
                mond_applicable += 1
                for g, d in m["per_group"].items():
                    mond_agg[g]["cov_pooled"].append(d["cov_pooled"])
                    mond_agg[g]["cov_mondrian"].append(d["cov_mondrian"])
                    mond_agg[g]["n"] += 1
    mond = {"applicable_splits": mond_applicable, "target": TARGET_COV_PRIMARY, "per_group": {}}
    for g, d in mond_agg.items():
        mond["per_group"][g] = {"n_splits": d["n"],
                                "mean_cov_pooled": float(np.mean(d["cov_pooled"])) if d["cov_pooled"] else None,
                                "mean_cov_mondrian": float(np.mean(d["cov_mondrian"])) if d["cov_mondrian"] else None}

    # ---- SECONDARY: adaptive-alpha online tracking ----
    adap = []
    for sd in reader_seeds:
        p = pops[sd]
        for j in range(min(n_splits, 40)):
            split_seed = BASE_SPLIT_SEED + j * 7919 + sd * 104729
            adap.append(adaptive_alpha_track(p["score"], p["correct"], TARGET_COV_PRIMARY, split_seed))
    adap_summary = {"target_cov": TARGET_COV_PRIMARY,
                    "mean_cov_static": float(np.mean([a["cov_static"] for a in adap])) if adap else None,
                    "mean_cov_online": float(np.mean([a["cov_online"] for a in adap])) if adap else None,
                    "mean_abs_err_static": float(np.mean([abs(a["cov_static"] - TARGET_COV_PRIMARY) for a in adap])) if adap else None,
                    "mean_abs_err_online": float(np.mean([abs(a["cov_online"] - TARGET_COV_PRIMARY) for a in adap])) if adap else None}

    # ---- gates ----
    base_wrong_med = prim_summary["median_base_wrong_test"]
    base_in_band = bool(base_wrong_med is not None and BASE_WRONG_LO < base_wrong_med < BASE_WRONG_HI)
    signal_nondegen = all(pops[sd]["score"].var() > 1e-9 for sd in reader_seeds)
    # arms-differ: conformal selection vs random selection (control) must differ in rel_red
    arms_differ = bool(ctrl_median_relred is not None and prim_summary["median_rel_red"] is not None
                       and abs(prim_summary["median_rel_red"] - ctrl_median_relred) > 0.02)

    # ---- verdict (transfer bands) ----
    mrr = prim_summary["median_rel_red"]
    mcov = prim_summary["median_realized_cov"]
    bfrac = prim_summary["frac_beats_random"]
    gap = prim_summary["median_transfer_gap"]

    hard_fail = (mrr is None or mrr < HF_RELRED or mcov is None or not (HF_COV_LO <= mcov <= HF_COV_HI)
                 or bfrac is None or bfrac < HF_BEATS_FRAC)
    hard_pass = (mrr is not None and mrr >= HP_RELRED and mcov is not None and HP_COV_LO <= mcov <= HP_COV_HI
                 and bfrac is not None and bfrac >= HP_BEATS_FRAC
                 and gap is not None and gap <= HP_GAP_MAX and prim_summary["pooled_beats_random"])

    if not (base_in_band and signal_nondegen):
        verdict = "INVALID_DISCRIMINATOR_DID_NOT_FIRE"
    elif hard_pass:
        verdict = "HARD_PASS_CONFORMAL_THRESHOLD_TRANSFERS_TO_DISJOINT_TEST"
    elif hard_fail:
        verdict = "HARD_FAIL_THRESHOLD_DOES_NOT_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_TRANSFER"

    gate_notes = []
    if not base_in_band:
        gate_notes.append(f"BASE_WRONG_OUT_OF_BAND:{base_wrong_med}")
    if not signal_nondegen:
        gate_notes.append("SIGNAL_DEGENERATE")
    if ctrl_median_relred is not None and ctrl_median_relred >= HF_RELRED:
        gate_notes.append(f"MUST_FAIL_CONTROL_TRANSFERRED:{ctrl_median_relred:.3f}")

    return {
        "verdict": verdict,
        "primary": prim_summary,
        "must_fail_control_median_rel_red": ctrl_median_relred,
        "target_cov_grid": grid,
        "mondrian": mond,
        "adaptive_alpha": adap_summary,
        "insample_reference": {"rel_red": INSAMPLE_RELRED, "confident_wrong": INSAMPLE_CW,
                               "base_wrong": INSAMPLE_BASEWRONG,
                               "source": "MEASURED@data/exp_metacog_abstain_readout_signal_thresholding_v1/metrics.json"},
        "gates": {"base_wrong_in_band": base_in_band, "signal_nondegenerate": signal_nondegen,
                  "arms_differ": arms_differ, "gate_notes": gate_notes},
        "n_pop_per_seed": {str(sd): int(len(pops[sd]["score"])) for sd in reader_seeds},
        "score_digests": {str(sd): _digest(pops[sd]["score"]) for sd in reader_seeds},
        "elapsed_build_s": time.perf_counter() - t0,
    }


# ----------------------------------------------------------------------------------------------
# infra
# ----------------------------------------------------------------------------------------------
def _write_start_marker(output_dir):
    import platform
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _atomic_write(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    _atomic_write(output_dir, diag)


def run_mode(mode):
    t0 = time.perf_counter()
    suffix = "_smoke" if mode == "smoke" else ""
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}{suffix}")
    _write_start_marker(output_dir)
    if mode == "smoke":
        res = analyze(FULL_SLICE, N_SPLITS_SMOKE, 300, [READER_SEEDS[0]])
    else:
        res = analyze(FULL_SLICE, N_SPLITS_FULL, BOOT_DRAWS, READER_SEEDS)
    elapsed = time.perf_counter() - t0

    p = res["primary"]
    msg = (f"{res['verdict']} | median rel_red={p['median_rel_red']:.3f} (in-sample {INSAMPLE_RELRED}) "
           f"cov={p['median_realized_cov']:.3f} cw_test={p['median_cw_test']:.3f} "
           f"beats_rand_frac={p['frac_beats_random']:.3f} pooled_beats={p['pooled_beats_random']} "
           f"gap={p['median_transfer_gap']:.3f} base_wrong={p['median_base_wrong_test']:.3f} "
           f"| must_fail_ctrl_relred={res['must_fail_control_median_rel_red']} "
           f"| gates={res['gates']['gate_notes'] if res['gates']['gate_notes'] else 'ok'}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode,
        "verdict": res["verdict"], "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "needs_orchestrator_store_sync": True, "local_only": True,
        "arms_differ_verified": res["gates"]["arms_differ"],
        "baseline_in_band": res["gates"]["base_wrong_in_band"],
        "discriminator_fires": res["gates"]["base_wrong_in_band"] and res["gates"]["signal_nondegenerate"],
        "final_metrics_atomicity": "tmp_replace",
        "prereg": {"target_cov_primary": TARGET_COV_PRIMARY, "target_cov_grid": TARGET_COV_GRID,
                   "n_splits": N_SPLITS_FULL if mode == "full" else N_SPLITS_SMOKE,
                   "reader_seeds": READER_SEEDS, "split_frac_cal": SPLIT_FRAC_CAL,
                   "HP": {"cov": [HP_COV_LO, HP_COV_HI], "rel_red": HP_RELRED,
                          "beats_frac": HP_BEATS_FRAC, "gap_max": HP_GAP_MAX},
                   "HF": {"rel_red_lt": HF_RELRED, "cov_outside": [HF_COV_LO, HF_COV_HI],
                          "beats_frac_lt": HF_BEATS_FRAC},
                   "insample_relred": INSAMPLE_RELRED,
                   "method": "split-conformal (Vovk/Angelopoulos) + Chow reject; hdlab/conformal.py"},
        "result": res,
        "REQUIRED_FIELDS": ["verdict", "verdict_msg", "summary", "elapsed_s", "result"],
    }
    _atomic_write(output_dir, payload)
    print(msg, flush=True)
    print(f"[conformal-transfer] wrote {os.path.join(output_dir, 'metrics.json')} in {elapsed:.1f}s", flush=True)
    return payload


def self_test():
    """Exercise the REAL code paths at tiny scale; assert wiring + closed-form correctness."""
    # real population build (tiny slice)
    bs, cor, grp = build_pop_lccp_ext(["L04"], seed=7)
    assert len(bs) == len(cor) == len(grp) > 0, "pop empty"
    assert bs.var() > 0, "score degenerate"
    # real single-split transfer runs end to end
    r = run_one_split(bs, cor, grp, 0.5, split_seed=123, boot_draws=200)
    assert r is None or ("rel_red" in r and "realized_cov" in r and "beats_random" in r), "split schema"
    # closed-form witness: a PERFECT confidence signal transfers (rel_red high, coverage ~target)
    perfect_score = np.concatenate([np.ones(60), np.zeros(60)])       # high score = correct
    correct = np.concatenate([np.ones(60), np.zeros(60)]).astype(bool)
    group = np.array(["seen"] * 120, dtype=object)
    rr = [run_one_split(perfect_score, correct, group, 0.5, 1000 + i, 300) for i in range(30)]
    rr = [x for x in rr if x is not None]
    med_rr = float(np.median([x["rel_red"] for x in rr]))
    med_cov = float(np.median([x["realized_cov"] for x in rr]))
    assert med_rr > 0.8, f"perfect signal must transfer high reduction, got {med_rr}"
    assert 0.40 <= med_cov <= 0.62, f"perfect signal coverage off target: {med_cov}"
    # closed-form witness: a RANDOM signal must NOT transfer (rel_red ~0)
    rng = np.random.default_rng(5)
    rand_score = rng.random(120)
    rr2 = [run_one_split(rand_score, correct, group, 0.5, 2000 + i, 300) for i in range(30)]
    rr2 = [x for x in rr2 if x is not None]
    med_rr2 = float(np.median([x["rel_red"] for x in rr2]))
    assert abs(med_rr2) < 0.20, f"random signal must not transfer, got {med_rr2}"
    # Mondrian + adaptive-alpha wiring on real pop (must not crash)
    _ = mondrian_vs_pooled(bs, cor, grp, 0.5, split_seed=7)
    _ = adaptive_alpha_track(bs, cor, 0.5, split_seed=7)
    print(f"[self-test] pop n={len(bs)} groups={dict(zip(*np.unique(grp, return_counts=True)))} "
          f"perfect_transfer relred={med_rr:.3f} cov={med_cov:.3f} | random_transfer relred={med_rr2:.3f}",
          flush=True)
    print("[self-test] PASS", flush=True)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    _out = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
