"""exp_srn_shrink_probe_replication_v1 -- DECISIVE replication of the ONE probe-confirmed positive from
exp_srn_capacity_growth_v1 (e81b06fbb; VET acaa64c9): does the SHRINK capacity SCHEDULE (train at FULL
capacity early, then mask the active effective dimension DOWN to d_low over epochs) genuinely encode MORE
linearly-decodable universal-POS than a FIXED-capacity learner -- across 3 SEEDS and beating a
GEOMETRY-MATCHED PCA control -- or was the seed-7 +6.4pt a single-seed fluke / a low-d clustering artifact?

WHY THIS CELL (the VET's exact revival criterion)
  The capacity-growth cell found the general "compression improves category abstraction" story is MOSTLY a
  dimensionality/clustering artifact: KMeans-AMI is dim-confounded (a fixed rep PCA-compressed to 8 dims gains
  AMI with ZERO retraining). BUT a NARROW real kernel survived on the DIM-AGNOSTIC logistic POS probe: at
  seed 7 the SHRINK schedule encoded +6.4pt more POS (probe_acc SHRINK 0.708 vs FIXED 0.644). Single seed.
  This cell replicates it decisively with the probe as the HEADLINE metric + a dimension-matched PCA control.
    MEASURED@d:/AI/hd-instrument (VET probe, session scratchpad probe_capacity.py): SHRINK_full=0.708,
    FIXED_full=0.644 at seed 7 (single seed; expected to regress under the single-seed-inflation rule).

THE DECISIVE TEST (metric = LOGISTIC POS-PROBE accuracy, k-fold, NOT KMeans-AMI which is dim-confounded)
  Arms differ in ONE variable only: the capacity SCHEDULE (same corpus / budget / order / seeds / learner).
    SHRINK : train full d, then staged-mask active d_eff DOWN to d_low (the hypothesis arm).
    FIXED  : d_eff = full d throughout (= parent LEARNER_POS default; REAL baseline).
  Representations probed by an IDENTICAL 5-fold stratified logistic probe (held-out folds; real Brown POS gold):
    SHRINK_full (d dims)   vs  FIXED_full (d dims)        -> REPLICATION gate (dimension-fair, 128 vs 128)
    SHRINK_pca_dlow (d_low) vs  FIXED_pca_dlow (d_low)    -> GEOMETRY gate  (dimension-MATCHED, d_low vs d_low)
  The PCA-geometry-matched control gives FIXED the SAME low-d geometry as SHRINK's final. If SHRINK's win is
  PURELY that its POS info lives in a low-d subspace, PCA extracts that subspace from FIXED and the two TIE at
  d_low. If SHRINK's d_low subspace still beats FIXED's PCA d_low subspace, the SCHEDULE (training under the
  tightening bottleneck) produced info PCA cannot recover from FIXED = a genuine schedule lever.

CAN-FAIL-BOTH-WAYS (design-gate compliant)
  HARD_PASS : SHRINK beats FIXED (replication, >=2/3 seeds by M_rep) AND SHRINK_pca_dlow beats FIXED_pca_dlow
              (geometry-matched, >=2/3 seeds by M_geo) -- genuine full-then-shrink abstraction lever, modest+real.
  HARD_FAIL_REPLICATION : SHRINK does NOT beat FIXED across seeds -- the seed-7 +6.4pt was single-seed noise.
  HARD_FAIL_GEOMETRY    : SHRINK_pca_dlow TIES/loses to FIXED_pca_dlow -- the win was low-d geometry (PCA
              recovers it equally from FIXED); the compression lever is fully refuted.
  DIFFICULTY-ON: held-out 5-fold probe; real universal-POS gold; d_low MATCHED between SHRINK-final and PCA
  control; SHRINK vs FIXED share identical corpus/budget/order/seed/learner (single variable = schedule).

DEFLATE: margins are deflated from the seed-7 +0.064 to acknowledge single-seed inflation
  (META_RULE_smoke_single_seed_inflates_AUC: single-seed measurements have inflated 3-seed values by
  0.05-0.25 this program). We do NOT require the exact +6.4pt; we require a strictly-above-noise replication.

GLASS-BOX: numpy / torch(cpu) / sklearn / nltk. NO spaCy-default / Stanza / transformers / runtime LLM.
  LOCAL-RUNNABLE, foreground-to-completion (~110s full: 2 arms x 3 seeds CPU; parent was 219.84s for 4 arms).
  Reuses the VET-confirmed corpus/vocab/gold/learner from exp_srn_capacity_growth_v1 VERBATIM (imported);
  the ONLY new code is the logistic probe + the PCA-geometry-matched control + the 3-seed verdict logic.
  ASCII-only. No emojis. Seeded generators; fixed int seeds.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; SHRINK vs FIXED reps hash-distinct)
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no capacity noise floor; discriminator is a held-out probe-accuracy gap (declared)
# - baseline_in_band at smoke (META_RULE_AG; majority < FIXED_full probe < 0.95)
# - discriminator previewed at smoke (SHRINK vs FIXED probe gap measurable) + FULL run to completion
# - HARD_PASS strictly above floor + margin (M_rep / M_geo deflated from seed-7 +0.064)
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; verdict counts len(per_seed)
# - per-seed failure isolation; no bare except; except Exception only
# - calibration_check: default_ok_for_this_regime (probe C=1.0/max_iter=2000 standard; label-free PCA)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - compute-architecture: sequential-CPU justified (wall < 10min; verbatim parent CPU learner; per-arm ~18s)
# - storage: no_storage / no_composition (representation-learning + probe cell)
"""

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import torch

# Verbatim reuse of the VET-confirmed corpus / vocab / gold / learner (the ONLY change vs parent is the
# probe + PCA control + 3-seed verdict; the learner mechanics are IDENTICAL by import, not re-implementation).
import exp_srn_capacity_growth_v1 as C

ANCHOR_NAME = "srn_shrink_probe_replication_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------- IO / diagnostics
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


# --------------------------------------------------------------------------- probe helpers (the new science)
def _rownorm(X):
    """Row-normalize (unit L2 rows); zero rows -> unit denom. Matches VET probe + parent eval preprocessing."""
    nrm = np.linalg.norm(X, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return X / nrm


def pca_reduce(X, npc, seed=0):
    """Label-FREE (unsupervised) PCA compression of row-normalized X to npc components, then row-normalize the
    reduced features (VET recipe). No label leakage: PCA never sees POS gold. Returns [n, npc]."""
    from sklearn.decomposition import PCA
    Xn = _rownorm(X)
    Z = PCA(n_components=npc, random_state=seed).fit_transform(Xn)
    return _rownorm(Z)


def logistic_probe(X, y, n_folds, seed=0):
    """5-fold (default) stratified logistic POS probe on held-out folds. X assumed already the exact feature
    matrix to probe (row-normalized upstream). Returns (mean_acc, std_acc, per_fold_list)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    accs = []
    for tr_i, te_i in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[tr_i], y[tr_i])
        accs.append(float(clf.score(X[te_i], y[te_i])))
    return float(np.mean(accs)), float(np.std(accs)), [round(a, 4) for a in accs]


# --------------------------------------------------------------------------- config
def cfg_for(mode):
    if mode == "smoke":
        # smaller scale; 3 seeds run so the multi-seed variance is previewed even at smoke.
        return dict(n_sents=800, vocab_size=200, min_count=3, d=64, d_min=8, n_stages=4, k=4, epochs=8,
                    batch=512, lr=0.01, seeds=[7, 13, 19], min_members=6, probe_folds=3, probe_seed=0)
    if mode == "full":
        # SAME budget/config as parent exp_srn_capacity_growth_v1 / exp_srn_predict_category_v1.
        return dict(n_sents=8000, vocab_size=900, min_count=5, d=128, d_min=8, n_stages=5, k=5, epochs=16,
                    batch=512, lr=0.01, seeds=[7, 13, 19], min_members=8, probe_folds=5, probe_seed=0)
    raise ValueError("mode must be smoke|full")


# --------------------------------------------------------------------------- run
def run(mode):
    t0 = time.perf_counter()
    cfg = cfg_for(mode)
    n_seeds = len(cfg["seeds"])
    EXPECTED_N_UNITS = n_seeds
    output_dir = os.path.join(REPO, "data", "exp_%s%s" % (ANCHOR_NAME, "_smoke" if mode == "smoke" else ""))
    _write_start_marker(output_dir, mode, expected_n_units=EXPECTED_N_UNITS)

    # ---- corpus / vocab / gold (verbatim parent path) ----
    sentences = C.load_brown_slice(cfg["n_sents"])
    word2id, id2word, gold, cats_used, purity = C.build_vocab_and_gold(
        sentences, cfg["vocab_size"], cfg["min_count"])
    V = len(id2word)
    seqs = C.tokenize_ids(sentences, word2id)
    present = np.array([g for g in gold if g >= 0])
    cat_counts = Counter(present.tolist())
    keep_cats = sorted([c for c, n in cat_counts.items() if n >= cfg["min_members"]])
    remap = {c: i for i, c in enumerate(keep_cats)}
    gold2 = np.array([remap.get(g, -1) if g >= 0 else -1 for g in gold], dtype=np.int64)
    n_cats = len(keep_cats)
    cats_used2 = [cats_used[c] for c in keep_cats]

    idx = np.where(gold2 >= 0)[0]
    y = gold2[idx]
    n_gold = int(len(y))
    maj_baseline = float(Counter(y.tolist()).most_common(1)[0][1]) / max(1, n_gold)

    # ---- capacity schedules (verbatim parent builder); d_low = SHRINK's FINAL active d_eff ----
    sched_shrink = C.capacity_schedule(cfg["epochs"], cfg["d"], cfg["d_min"], cfg["n_stages"], "shrink")
    sched_fixed = C.capacity_schedule(cfg["epochs"], cfg["d"], cfg["d_min"], cfg["n_stages"], "fixed")
    d_low = int(sched_shrink[-1])
    assert d_low == cfg["d_min"], "d_low (%d) must equal SHRINK final d_eff == d_min (%d)" % (d_low, cfg["d_min"])
    assert d_low < cfg["d"], "d_low (%d) must be strictly below full d (%d) for the geometry control" % (d_low, cfg["d"])

    random_vec = C.arm_random(V, cfg["d"], seed=0)  # sanity: random code carries ~no POS info

    per_seed = []
    digests_logged = None
    for si, seed in enumerate(cfg["seeds"]):
        # ---- train the two arms (SHRINK, FIXED); ONE variable = schedule ----
        shE, shW, sh_ce, sh_ce1 = C.arm_learner_capacity(seqs, V, cfg["d"], cfg["k"], cfg["epochs"],
                                                         cfg["batch"], cfg["lr"], seed, sched_shrink)
        fxE, fxW, fx_ce, fx_ce1 = C.arm_learner_capacity(seqs, V, cfg["d"], cfg["k"], cfg["epochs"],
                                                         cfg["batch"], cfg["lr"], seed, sched_fixed)
        if si == 0:
            digests_logged = arms_must_differ({"SHRINK": shE, "FIXED": fxE, "RANDOM_CODE": random_vec})

        # ---- build the probed feature matrices (all on the SAME gold-word rows) ----
        Xsh = shE[idx]
        Xfx = fxE[idx]
        Xr = random_vec[idx]
        pf = cfg["probe_folds"]
        ps = cfg["probe_seed"]

        # REPLICATION gate inputs: full-d probe, dimension-fair (d vs d), ONLY schedule differs
        acc_sh_full, std_sh_full, folds_sh_full = logistic_probe(_rownorm(Xsh), y, pf, ps)
        acc_fx_full, std_fx_full, folds_fx_full = logistic_probe(_rownorm(Xfx), y, pf, ps)
        # GEOMETRY gate inputs: dimension-MATCHED PCA to d_low (d_low vs d_low), ONLY schedule differs
        acc_sh_pca, std_sh_pca, _ = logistic_probe(pca_reduce(Xsh, d_low, ps), y, pf, ps)
        acc_fx_pca, std_fx_pca, _ = logistic_probe(pca_reduce(Xfx, d_low, ps), y, pf, ps)
        # descriptors: SHRINK's own leading-d_low ACTIVE subspace; RANDOM-code sanity
        acc_sh_active, _, _ = logistic_probe(_rownorm(shE[idx][:, :d_low]), y, pf, ps)
        acc_rand, _, _ = logistic_probe(_rownorm(Xr), y, pf, ps)

        delta_rep = acc_sh_full - acc_fx_full          # PRIMARY: SHRINK vs FIXED, full-d (the +6.4pt claim)
        delta_geo = acc_sh_pca - acc_fx_pca            # DECISIVE: schedule vs PCA-geometry at matched d_low
        pca_recovers = acc_fx_pca - acc_sh_full        # descriptor: does low-d geometry lift FIXED to SHRINK?

        per_seed.append({
            "seed": seed,
            "acc_shrink_full": round(acc_sh_full, 4), "acc_fixed_full": round(acc_fx_full, 4),
            "std_shrink_full": round(std_sh_full, 4), "std_fixed_full": round(std_fx_full, 4),
            "folds_shrink_full": folds_sh_full, "folds_fixed_full": folds_fx_full,
            "acc_shrink_pca%d" % d_low: round(acc_sh_pca, 4), "acc_fixed_pca%d" % d_low: round(acc_fx_pca, 4),
            "acc_shrink_active%d" % d_low: round(acc_sh_active, 4),
            "acc_randomcode_full": round(acc_rand, 4),
            "sh_ce": round(sh_ce, 4), "fx_ce": round(fx_ce, 4),
            "delta_rep": round(delta_rep, 4),          # SHRINK_full - FIXED_full
            "delta_geo": round(delta_geo, 4),          # SHRINK_pca_dlow - FIXED_pca_dlow
            "pca_recovers": round(pca_recovers, 4),    # FIXED_pca_dlow - SHRINK_full (>=~0 => geometry lifts FIXED)
        })

    # ---- CARDINALITY (META_RULE_H) ----
    cardinality_ok = (len(per_seed) == EXPECTED_N_UNITS)

    # ---- aggregate ----
    def mean(key):
        return float(np.mean([p[key] for p in per_seed]))
    acc_sh_full_m = mean("acc_shrink_full")
    acc_fx_full_m = mean("acc_fixed_full")
    acc_sh_pca_m = mean("acc_shrink_pca%d" % d_low)
    acc_fx_pca_m = mean("acc_fixed_pca%d" % d_low)
    acc_rand_m = mean("acc_randomcode_full")
    delta_rep_m = mean("delta_rep")
    delta_geo_m = mean("delta_geo")

    # ---- pre-registered margins (deflated from seed-7 +0.064; single-seed-inflation aware) ----
    M_REP = 0.03   # SHRINK_full - FIXED_full strictly-above-noise replication margin
    M_GEO = 0.03   # SHRINK_pca_dlow - FIXED_pca_dlow schedule-beats-PCA margin
    maj = (n_seeds // 2) + 1  # >= 2/3

    rep_seeds = sum(1 for p in per_seed if p["delta_rep"] >= M_REP)
    geo_seeds = sum(1 for p in per_seed if p["delta_geo"] >= M_GEO)
    rep_pass = (rep_seeds >= maj)
    geo_pass = (geo_seeds >= maj)
    # clear-failure conditions (task-worded HARD_FAILs)
    rep_absent = (rep_seeds < maj) and (delta_rep_m < M_REP)   # didn't replicate vs FIXED
    geo_absent = (geo_seeds < maj) and (delta_geo_m < M_GEO)   # ties/loses PCA control => low-d geometry

    # ---- sanity gates (difficulty-on / metric-fires / baseline-in-band) ----
    metric_fires = (acc_rand_m <= maj_baseline + 0.05)                 # random code ~ majority baseline
    baseline_above_chance = (acc_fx_full_m >= maj_baseline + 0.10)     # FIXED learner well above majority
    baseline_in_band = (maj_baseline < acc_fx_full_m < 0.95)
    sanity_ok = cardinality_ok and metric_fires and baseline_above_chance and baseline_in_band

    # ---- verdict ----
    if not sanity_ok:
        verdict = "INVALID_REGIME"
        msg = ("regime/sanity invalid: cardinality_ok=%s (n_units=%d exp=%d); metric_fires=%s "
               "(acc_random=%.3f vs maj=%.3f+0.05); baseline_above_chance=%s (acc_fixed_full=%.3f vs "
               "maj=%.3f+0.10); baseline_in_band=%s"
               % (cardinality_ok, len(per_seed), EXPECTED_N_UNITS, metric_fires, acc_rand_m, maj_baseline,
                  baseline_above_chance, acc_fx_full_m, maj_baseline, baseline_in_band))
    elif rep_pass and geo_pass:
        verdict = "HARD_PASS"
        msg = ("GENUINE full-then-shrink abstraction lever: SHRINK beats FIXED on the logistic POS probe "
               "(delta_rep>=+%.2f on %d/%d seeds; acc_shrink_full=%.3f > acc_fixed_full=%.3f) AND SHRINK beats "
               "the dimension-MATCHED PCA-geometry control (delta_geo>=+%.2f on %d/%d seeds; "
               "acc_shrink_pca%d=%.3f > acc_fixed_pca%d=%.3f) -- the win is the SCHEDULE, not low-d geometry. "
               "(seed-7 origin +0.064; 3-seed mean delta_rep=+%.3f, delta_geo=+%.3f.)"
               % (M_REP, rep_seeds, n_seeds, acc_sh_full_m, acc_fx_full_m, M_GEO, geo_seeds, n_seeds,
                  d_low, acc_sh_pca_m, d_low, acc_fx_pca_m, delta_rep_m, delta_geo_m))
    elif rep_absent:
        verdict = "HARD_FAIL_REPLICATION"
        msg = ("SINGLE-SEED NOISE: SHRINK does NOT replicate its POS-probe advantage over FIXED across seeds "
               "(delta_rep>=+%.2f on only %d/%d seeds; 3-seed mean acc_shrink_full=%.3f vs acc_fixed_full=%.3f, "
               "delta_rep=+%.3f < +%.2f) -- the seed-7 +6.4pt was a single-seed fluke; efficiency-lever thread "
               "CLOSED negative." % (M_REP, rep_seeds, n_seeds, acc_sh_full_m, acc_fx_full_m, delta_rep_m, M_REP))
    elif geo_absent:
        verdict = "HARD_FAIL_GEOMETRY"
        msg = ("LOW-D GEOMETRY AFTER ALL, compression lever fully refuted: SHRINK replicates vs FIXED on full-d "
               "(delta_rep=+%.3f) BUT at the dimension-MATCHED PCA control it TIES/loses (delta_geo=+%.3f on "
               "%d/%d seeds; acc_shrink_pca%d=%.3f ~ acc_fixed_pca%d=%.3f) -- PCA extracts the SAME low-d POS "
               "geometry from FIXED, so the SHRINK win was the low-d geometry, NOT the schedule; efficiency-lever "
               "thread CLOSED negative." % (delta_rep_m, delta_geo_m, geo_seeds, n_seeds, d_low, acc_sh_pca_m,
                                            d_low, acc_fx_pca_m))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("marginal/split: delta_rep=+%.3f (%d/%d seeds>=+%.2f), delta_geo=+%.3f (%d/%d seeds>=+%.2f); "
               "acc_shrink_full=%.3f fixed_full=%.3f shrink_pca%d=%.3f fixed_pca%d=%.3f -- effect present but "
               "not decisively above the replication AND geometry margins on >=2/3 seeds."
               % (delta_rep_m, rep_seeds, n_seeds, M_REP, delta_geo_m, geo_seeds, n_seeds, M_GEO,
                  acc_sh_full_m, acc_fx_full_m, d_low, acc_sh_pca_m, d_low, acc_fx_pca_m))

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": verdict, "verdict_msg": msg, "summary": "%s: %s" % (verdict, msg[:120]),
        "elapsed_s": round(elapsed, 2), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "mode": mode,
        "config": cfg,
        "d_low": d_low,
        "capacity_schedules": {"shrink": sched_shrink, "fixed": sched_fixed},
        "corpus": {"n_sentences": len(sentences), "n_sequences": len(seqs),
                   "n_tokens": int(sum(len(s) for s in seqs)), "vocab_size": V,
                   "n_gold_words": n_gold, "n_categories": n_cats, "categories": cats_used2,
                   "majority_baseline_acc": round(maj_baseline, 4),
                   "metric": "logistic_5fold_stratified_POS_probe_accuracy"},
        "arms": ["SHRINK", "FIXED", "RANDOM_CODE"],
        "probed_reps": ["SHRINK_full", "FIXED_full", "SHRINK_pca_dlow", "FIXED_pca_dlow",
                        "SHRINK_active_dlow", "RANDOM_CODE_full"],
        "per_seed": per_seed,
        "aggregate": {
            "acc_shrink_full_mean": round(acc_sh_full_m, 4), "acc_fixed_full_mean": round(acc_fx_full_m, 4),
            "acc_shrink_pca%d_mean" % d_low: round(acc_sh_pca_m, 4),
            "acc_fixed_pca%d_mean" % d_low: round(acc_fx_pca_m, 4),
            "acc_randomcode_full_mean": round(acc_rand_m, 4),
            "delta_rep_mean": round(delta_rep_m, 4), "delta_geo_mean": round(delta_geo_m, 4),
            "rep_seeds": rep_seeds, "geo_seeds": geo_seeds, "n_seeds": n_seeds, "maj_needed": maj,
            "M_rep": M_REP, "M_geo": M_GEO,
            "seed7_origin_delta_rep": 0.064},
        "gates": {"cardinality_ok": cardinality_ok, "metric_fires": metric_fires,
                  "baseline_above_chance": baseline_above_chance, "baseline_in_band": baseline_in_band,
                  "rep_pass": rep_pass, "geo_pass": geo_pass, "rep_absent": rep_absent, "geo_absent": geo_absent,
                  "arms_differ_verified": True, "sanity_ok": sanity_ok},
        "arm_digests": digests_logged,
        "crlb_n_a": "no capacity noise floor; discriminator is a held-out logistic probe-accuracy gap",
        "compute_architecture": "sequential_CPU_justified_wall_under_10min_verbatim_parent_learner",
        "storage_strategy": "no_storage_no_composition_representation_probe_cell",
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "default_ok_for_this_regime",
    }
    _write_metrics(output_dir, metrics)
    print("[%s] verdict=%s" % (ANCHOR_NAME, verdict))
    print(msg)
    print("per_seed:", json.dumps(per_seed, indent=2))
    print("aggregate:", json.dumps(metrics["aggregate"], indent=2))
    print("gates:", json.dumps(metrics["gates"]))
    print("metrics ->", os.path.join(output_dir, "metrics.json"))
    return metrics


# --------------------------------------------------------------------------- arms-must-differ (verbatim parent)
def arms_must_differ(arm_outputs):
    digests = {}
    for name, out in arm_outputs.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(out).tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], "META_RULE_AF: arms %s and %s bit-identical" % (a, b)
    return digests


# --------------------------------------------------------------------------- self-test (real code path)
def self_test():
    """Exercise the REAL learner + the NEW probe/PCA-control code path on a tiny synthetic corpus; assert
    the probe fires (structured learner > random code), the PCA-geometry control is dimension-matched and
    computes, arms differ, and the gate arithmetic is sound + deterministic."""
    print("[self-test] building tiny synthetic corpus...")
    dets = ["the", "a", "this", "that"]
    nouns = ["dog", "cat", "man", "car", "tree", "house", "bird", "road"]
    verbs = ["runs", "sees", "eats", "moves", "finds", "holds", "makes", "takes"]
    tagmap = {}
    for w in dets:
        tagmap[w] = "DET"
    for w in nouns:
        tagmap[w] = "NOUN"
    for w in verbs:
        tagmap[w] = "VERB"
    rng = np.random.default_rng(0)
    sentences = []
    for _ in range(700):
        d_ = rng.choice(dets); n = rng.choice(nouns); v = rng.choice(verbs)
        sentences.append([(d_, tagmap[d_]), (n, tagmap[n]), (v, tagmap[v])])
    word2id, id2word, gold, cats_used, purity = C.build_vocab_and_gold(sentences, vocab_size=50, min_count=1)
    V = len(id2word)
    seqs = C.tokenize_ids(sentences, word2id)
    present = sorted(set(int(g) for g in gold if g >= 0))
    remap = {c: i for i, c in enumerate(present)}
    gold2 = np.array([remap[int(g)] if g >= 0 else -1 for g in gold], dtype=np.int64)
    idx = np.where(gold2 >= 0)[0]
    y = gold2[idx]

    epochs, d, d_min, n_stages, k = 8, 32, 8, 4, 2
    ss = C.capacity_schedule(epochs, d, d_min, n_stages, "shrink")
    sf = C.capacity_schedule(epochs, d, d_min, n_stages, "fixed")
    d_low = int(ss[-1])
    assert d_low == d_min and d_low < d, "d_low must be d_min and < d: d_low=%d d_min=%d d=%d" % (d_low, d_min, d)
    assert sf == [d] * epochs, "fixed must be constant full-d"

    # (1) REAL learner code path (imported parent arm), both arms; arms differ.
    shE, _, sh_ce, _ = C.arm_learner_capacity(seqs, V, d, k, epochs, 128, 0.02, 7, ss)
    fxE, _, fx_ce, _ = C.arm_learner_capacity(seqs, V, d, k, epochs, 128, 0.02, 7, sf)
    R = C.arm_random(V, d, 0)
    digs = arms_must_differ({"SHRINK": shE, "FIXED": fxE, "RANDOM_CODE": R})
    assert len(set(digs.values())) == 3, "3 arms must be bit-distinct"

    # (2) NEW probe/PCA path executes + is dimension-matched; probe fires (structured > random).
    Xsh, Xfx, Xr = shE[idx], fxE[idx], R[idx]
    zsh = pca_reduce(Xsh, d_low)
    zfx = pca_reduce(Xfx, d_low)
    assert zsh.shape == (len(y), d_low) and zfx.shape == (len(y), d_low), "PCA control not dimension-matched"
    a_sh_full, _, _ = logistic_probe(_rownorm(Xsh), y, 3, 0)
    a_fx_full, _, _ = logistic_probe(_rownorm(Xfx), y, 3, 0)
    a_sh_pca, _, _ = logistic_probe(zsh, y, 3, 0)
    a_fx_pca, _, _ = logistic_probe(zfx, y, 3, 0)
    a_rand, _, _ = logistic_probe(_rownorm(Xr), y, 3, 0)
    maj = float(Counter(y.tolist()).most_common(1)[0][1]) / len(y)
    print("[self-test] probe full: shrink=%.3f fixed=%.3f random=%.3f | pca%d: shrink=%.3f fixed=%.3f | maj=%.3f"
          % (a_sh_full, a_fx_full, a_rand, d_low, a_sh_pca, a_fx_pca, maj))
    assert a_sh_full > a_rand and a_fx_full > a_rand, "structured learners must beat random code on rigid grammar"
    assert a_rand <= maj + 0.15, "random-code probe %.3f should be near majority baseline %.3f" % (a_rand, maj)

    # (3) gate arithmetic sanity: margins, maj-vote, both fail-branches reachable (construct toy deltas).
    def _classify(dr, dg, n=3, M=0.03):
        rs = sum(1 for x in dr if x >= M); gs = sum(1 for x in dg if x >= M)
        mj = (n // 2) + 1
        drm = float(np.mean(dr)); dgm = float(np.mean(dg))
        rep_pass, geo_pass = rs >= mj, gs >= mj
        rep_absent = (rs < mj) and (drm < M); geo_absent = (gs < mj) and (dgm < M)
        if rep_pass and geo_pass:
            return "HARD_PASS"
        if rep_absent:
            return "HARD_FAIL_REPLICATION"
        if geo_absent:
            return "HARD_FAIL_GEOMETRY"
        return "MIDDLE_BAND"
    assert _classify([0.05, 0.06, 0.04], [0.05, 0.06, 0.04]) == "HARD_PASS", "PASS branch"
    assert _classify([0.00, 0.01, -0.01], [0.05, 0.06, 0.04]) == "HARD_FAIL_REPLICATION", "REPL-fail branch"
    assert _classify([0.05, 0.06, 0.04], [0.00, 0.01, -0.01]) == "HARD_FAIL_GEOMETRY", "GEO-fail branch"
    # geo mean above margin (0.04) but only 1/3 seeds clear it -> not geo_absent, not geo_pass -> split
    assert _classify([0.05, 0.06, 0.04], [0.10, 0.00, 0.02]) == "MIDDLE_BAND", "MIDDLE split-on-geo"

    # (4) determinism: same seed/schedule re-run bit-identical (F.5).
    shE2, _, _, _ = C.arm_learner_capacity(seqs, V, d, k, epochs, 128, 0.02, 7, ss)
    assert np.array_equal(shE, shE2), "learner nondeterministic across runs (F.5 violation)"
    print("[self-test] PASS: real learner path; probe fires; PCA control dimension-matched; all 3 verdict "
          "branches reachable; deterministic.")
    return True


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    output_dir_guess = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(output_dir_guess, e)
        raise
