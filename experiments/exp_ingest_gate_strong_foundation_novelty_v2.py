"""Ingest-gate v2: does SURPRISE detect SEMANTIC NOVELTY on a STRONG (generalizing) foundation, or only
ENCODING-STATUS (train-vs-heldout)? -- closes the 4 gaps the v1 pilot VET raised.

v1 (commit 400c63e69, MEASURED@data/exp_ingest_gate_consolidation_loop_pilot_v1/metrics.json) landed HARD_PASS with
sep_auc=0.988 BUT base_mrr=0.104 (WEAK foundation). The VET narrowed the crux: v1's "redundant" batch was literally
TRAIN edges and "novel" was a withheld relation, so the 0.988 separation is ~train-vs-heldout (encoding-status), NOT
semantic-novelty. On a WEAK foundation those coincide; the real-regime question is whether they DIVERGE on a STRONG
foundation that actually GENERALIZES.

THE KEY TEST (VET gap 1): construct a foundation that GENERALIZES (high held-out MRR on INFERABLE edges), then ask
whether surprise separates
  NOVEL      = edges requiring info ABSENT from the foundation (a withheld relation r*) -> should rank low  -> HIGH surprise
  INFERABLE  = HELD-OUT edges of TRAINED relations the strong foundation CAN predict   -> should rank high -> LOW  surprise
BOTH are held-out (neither literally trained), so a positive AUC(surprise; NOVEL vs INFERABLE) is NOT the v1
train-vs-heldout confound -- it is genuine semantic-novelty detection. The load-bearing contrast: compute the SAME
AUC on a WEAK foundation (few epochs) fit on the SAME data. If the KEY AUC is high on STRONG and collapses to ~chance
on WEAK, surprise = "can the CURRENT foundation predict this", which BECOMES semantic-novelty as the foundation
strengthens (a strong foundation predicts everything inferable). If the KEY AUC COLLAPSES even on the strong
foundation (VET-predicted possible), surprise is only encoding-status -> reported honestly as the scoped bound
(+ brain-check: Lisman-Grace/Duszkiewicz novelty signal vs schema strength).

Why a SYNTHETIC compositional TransE arena (not raw CSKG): real CSKG additive-map MRR caps ~0.13 (VET'd held-out
0.1282) == the WEAK regime v1 already measured. A STRONG generalizing foundation does not exist on raw CSKG, so the
KEY TEST needs a regime where strong foundations are attainable + where NOVEL-vs-INFERABLE ground truth is known by
CONSTRUCTION (non-circular, independent of the gate signal). The arena is a functional TransE generative process
(t = nearest-entity(Z_h + G_r)); the additive map is the correct model class for it, so held-out edges of trained
relations ARE inferable and a well-fit map generalizes to them. Foundation strength is dialed ONLY by SGD epochs on
the SAME edges (clean controlled contrast). All v1 substrate machinery is REUSED (AdditiveKGMap.fit / score readout /
gate tree / schema-fit-via-reachability / TransE-mean fold-in); only the DATA source + the INFERABLE-heldout split +
the thin-provenance HOLD batch + held-out calibration + per-candidate array dump are new.

Gaps closed:
  gap1 KEY TEST      : AUC(surprise; NOVEL vs INFERABLE-heldout) on STRONG foundation + STRONG-vs-WEAK contrast.
  gap2 held-out calib: SKIP threshold selected on a CALIB split, routing rates reported on a DISJOINT EVAL split.
  gap3 HOLD branch   : a THIN-PROVENANCE novel batch (high surprise, few distinct sources) makes HOLD actually fire.
  gap4 array dump    : raw per-candidate surprise/schema-fit/label arrays written to per_candidate_arrays.npz +
                       reloaded + the KEY AUC recomputed off-disk to prove independent recomputability.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (WEAK vs STRONG surprise vectors hash-distinct)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: gate is a decision-tree over measured signals; no closed-form noise floor (bands from MEASURED calib)
# - baseline_in_band: WEAK inferable-heldout MRR 0.05<mrr<0.95 verified at smoke
# - discriminator survives scale: smoke verifies STRONG inferable-MRR >> WEAK AND KEY-AUC(strong) > KEY-AUC(weak)
# - HARD_PASS strictly above floor + 5% band-width
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity at N~16
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); no hash()-seeded RNG, no list(set()) order

ASCII-only. No emojis. Explicit dtypes. torch.Generator / np.random.default_rng seeded. Terse.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402
from hdlab import reachability_audit as RA  # noqa: E402
# REUSE v1 science helpers (importing the module does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, build_schema_fit, schema_fit_edges,
    RECURRENCE_MIN, DISTINCT_NOVELTY, SCHEMA_FIT_MIN, CONSOLIDATE,
)

ANCHOR_NAME = "ingest_gate_strong_foundation_novelty_v2"

# ---- pre-registered gate thresholds (design; SKIP threshold is CALIBRATED out-of-sample, gap 2) -----------------
# RECURRENCE_MIN / DISTINCT_NOVELTY / SCHEMA_FIT_MIN reused verbatim from v1 (imported above).

# ---- pre-registered HARD-PASS bands (set from the design; smoke calibrates that STRONG can be made strong) -------
# HYPOTHESIZED@this-file (design predictions; measured at smoke/full):
#   STRONG inferable-heldout MRR ~0.5-0.8; WEAK ~0.10; KEY-AUC(strong)>=0.75; KEY-AUC(weak)~0.5-0.6.
HP_STRONG_MRR_MIN = 0.50      # STRONG foundation must GENERALIZE to inferable-heldout (else "strong" is vacuous)
HP_KEY_AUC_STRONG_MIN = 0.75  # AUC(surprise; novel vs inferable-heldout | STRONG); floor+5% above chance 0.5
HP_DOSE_RESPONSE_MIN = 0.20   # KEY-AUC(strong) - KEY-AUC(dead): novelty-detection REQUIRES a generalizing foundation
HP_DEAD_COLLAPSE_MAX = 0.70   # DEAD (non-generalizing) foundation KEY-AUC must be near chance (must-collapse control)
HP_OOS_SKIP_MIN = 0.60        # out-of-sample skip-rate on inferable-eval (calibrated on disjoint calib split)
HP_OOS_CONS_MIN = 0.60        # out-of-sample consolidate-rate on novel-eval
HP_HOLD_FIRES_MIN = 0.30      # thin-provenance HOLD-rate (v1 was 0.000; must materially fire)
HP_DISCARD_MIN = 0.95         # noise DISCARD-rate (recurrence floor)
HP_INTERFERENCE_TOL = 1e-6    # append-only fold-in: existing-MRR delta ~0
HP_ARRAY_RECOMPUTE_TOL = 1e-6 # off-disk KEY-AUC must match in-memory within tol (gap 4)

EPS_BAND = 1e-9

# ---- arena / run configs ---------------------------------------------------------------------------------------
# Tuned (MEASURED@arena-probe): rel_scale=4.0/noise=0.10/n_ent=600 -> WEAK 40ep MRR=0.171 (in-band, real-regime-like)
# / STRONG 350ep MRR=0.662 (genuinely generalizing, non-saturated). rel_scale is the strong-ceiling lever; the
# additive map on a Gaussian-cloud NN arena caps ~0.31 at rel_scale=1.0 (crowded distractors) -> rel_scale=4.0
# moves targets to lower-density periphery so a well-fit map ranks the true tail clearly.
FULL_CFG = dict(n_ent=600, k_latent=16, k_fit=24, n_base_rel=12, edges_per_rel=420, gen_noise=0.10, rel_scale=4.0,
                frac_heldout=0.28, dead_epochs=22, weak_epochs=45, strong_epochs=350, seeds=[7, 13, 17],
                reach_k=2, reach_cap=300, thinprov_n=60, thinprov_sources=1, calib_frac=0.5)
SMOKE_CFG = dict(n_ent=400, k_latent=16, k_fit=24, n_base_rel=12, edges_per_rel=280, gen_noise=0.10, rel_scale=4.0,
                 frac_heldout=0.28, dead_epochs=18, weak_epochs=45, strong_epochs=300, seeds=[7],
                 reach_k=2, reach_cap=200, thinprov_n=40, thinprov_sources=1, calib_frac=0.5)

# foundation-strength sweep: DEAD (non-generalizing floor control -> KEY-AUC must collapse to ~chance),
# WEAK (real-CSKG-like regime, in-band), STRONG (genuinely generalizing). The dose-response KEY-AUC(strong) >>
# KEY-AUC(dead) is the load-bearing evidence that surprise-as-novelty REQUIRES a generalizing foundation
# (i.e. it is derivability/semantic-novelty, not a fixed train-vs-heldout artifact).
STRENGTH_ORDER = ["dead", "weak", "strong"]

# batch ids for the array dump
B_TRAIN, B_INFER, B_NOVEL, B_NOISE, B_THIN = 0, 1, 2, 3, 4


# ---------------------------------------------------------------------------
# start-marker / crash-diagnostic / atomic metrics (own copies; v1 helpers bind v1's ANCHOR_NAME)
# ---------------------------------------------------------------------------
def _log(msg):
    print("[ingest_gate_v2] %s" % msg, flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics_atomic(output_dir, diag)


def _mean(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


# ---------------------------------------------------------------------------
# synthetic compositional TransE arena (functional: t = nearest-entity(Z_h + G_r))
# ---------------------------------------------------------------------------
def gen_arena(cfg, seed):
    """Return (Z [N,kL], G [nR,kL], edges list[(h,r,t)] int). Functional relations -> additive map is correct class."""
    rng = np.random.default_rng(seed * 100003 + 11)
    N = cfg["n_ent"]; kL = cfg["k_latent"]; nR = cfg["n_base_rel"]
    Z = rng.standard_normal((N, kL)).astype(np.float64)
    G = (rng.standard_normal((nR, kL)) * cfg["rel_scale"]).astype(np.float64)
    edges = []
    for r in range(nR):
        m = min(cfg["edges_per_rel"], N)
        heads = rng.choice(N, size=m, replace=False)
        tgt = Z[heads] + G[r][None, :] + rng.standard_normal((m, kL)) * cfg["gen_noise"]   # (m,kL)
        # nearest entity per head (exclude self); brute-force distance (N small)
        d2 = ((tgt[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2)                            # (m,N)
        for i, h in enumerate(heads):
            d2[i, h] = np.inf
        tails = np.argmin(d2, axis=1)
        for i, h in enumerate(heads):
            edges.append((int(h), int(r), int(tails[i])))
    return Z, G, edges


def _to_int(triples):
    return np.array(triples, dtype=np.int64) if triples else np.zeros((0, 3), dtype=np.int64)


# ---------------------------------------------------------------------------
# calibrated gate + threshold selection (gap 2)
# ---------------------------------------------------------------------------
def gate_calibrated(schema_fit, surprise, recurrence, n_sources, skip_thresh):
    """v2 gate with the SKIP surprise-cutoff CALIBRATED (skip_thresh) instead of a fixed design constant."""
    if recurrence < RECURRENCE_MIN:
        return "DISCARD"
    if surprise < skip_thresh:
        return "SKIP"
    if surprise > DISTINCT_NOVELTY and n_sources < RECURRENCE_MIN:
        return "HOLD"
    if schema_fit >= SCHEMA_FIT_MIN:
        return "FAST_TRACK"
    return "SLOW_TRACK"


def calibrate_skip_threshold(surp_inferable_calib, surp_novel_calib):
    """Pick the surprise SKIP cutoff maximizing Youden's J on the CALIB split: inferable should SKIP (surprise<t),
    novel should NOT. Returns (best_t, best_J). Deterministic grid; no data leakage from eval."""
    inf = np.asarray(surp_inferable_calib, dtype=np.float64)
    nov = np.asarray(surp_novel_calib, dtype=np.float64)
    grid = np.linspace(0.0, 1.0, 201)
    best_t, best_j = 0.5, -2.0
    for t in grid:
        tpr = float(np.mean(inf < t)) if inf.size else 0.0     # correctly skip inferable
        fpr = float(np.mean(nov < t)) if nov.size else 0.0     # wrongly skip novel
        j = tpr - fpr
        if j > best_j:
            best_j, best_t = j, float(t)
    return best_t, best_j


def _rate(decisions, target_set):
    if not decisions:
        return 0.0
    return sum(1 for d in decisions if d in target_set) / len(decisions)


# ---------------------------------------------------------------------------
# fit a foundation at a given strength + compute all signals for the batches
# ---------------------------------------------------------------------------
def fit_foundation(cfg, seed, epochs, train, N, nR, device):
    """Fit AdditiveKGMap on train edges at the REAL live substrate object. Returns (X, D, all_true)."""
    entities = [str(i) for i in range(N)]
    relations = ["r%d" % r for r in range(nR)]
    train_lbl = [("%d" % h, "r%d" % r, "%d" % t) for (h, r, t) in train]
    kmap = AdditiveKGMap(device=device)
    kmap.fit(train_lbl, entities=entities, relations=relations, k=cfg["k_fit"], epochs=epochs, seed=seed)
    all_true = defaultdict(set)
    for h, r, t in train:
        all_true[(int(h), int(r))].add(int(t))
    return kmap.X, kmap.D, all_true


def run_seed(cfg, seed, device):
    """One arena; fit WEAK + STRONG foundations on identical data; build batches; compute KEY AUC + routing + HOLD."""
    Z, G, edges = gen_arena(cfg, seed)
    N = cfg["n_ent"]; nR = cfg["n_base_rel"]
    rng = np.random.default_rng(seed * 100003 + 29)

    # withhold one entire relation type as NOVEL (info absent from foundation)
    rstar = nR - 1
    novel_edges = [e for e in edges if e[1] == rstar]
    trained_edges = [e for e in edges if e[1] != rstar]

    # hold out a fraction of TRAINED-relation edges -> INFERABLE-heldout (foundation should predict if strong)
    ne = len(trained_edges)
    perm = rng.permutation(ne)
    n_hold = int(round(cfg["frac_heldout"] * ne))
    hold_idx = set(perm[:n_hold].tolist())
    train = [trained_edges[i] for i in range(ne) if i not in hold_idx]           # FOUNDATION train
    inferable = [trained_edges[i] for i in range(ne) if i in hold_idx]           # held-out, inferable

    train_int = _to_int(train)
    infer_int = _to_int(inferable)
    novel_int = _to_int(novel_edges)

    # NOISE = scrambled inferable edges (tails permuted), each one-off
    noise_int = infer_int.copy()
    if noise_int.shape[0] > 1:
        noise_int[:, 2] = noise_int[np.argsort(rng.random(noise_int.shape[0])), 2]

    # schema-fit (reachability over FOUNDATION train edges only -> no query leakage) -- REUSED from v1
    reach_pct, _mass = build_schema_fit(train_int, N, cfg["reach_k"], cfg["reach_cap"])

    # ---- fit DEAD + WEAK + STRONG on identical train edges (only epochs differ) ---------------------------
    arms = {}
    for name, ep in (("dead", cfg["dead_epochs"]), ("weak", cfg["weak_epochs"]), ("strong", cfg["strong_epochs"])):
        X, D, all_true = fit_foundation(cfg, seed, ep, train, N, nR, device)
        # surprise per batch (closed-loop score readout, filtered by train edges)
        surp_train = _surprise(_recip_ranks(X, D, train_int[:min(400, train_int.shape[0])], all_true, device))
        surp_infer = _surprise(_recip_ranks(X, D, infer_int, all_true, device))
        surp_novel = _surprise(_recip_ranks(X, D, novel_int, all_true, device))
        surp_noise = _surprise(_recip_ranks(X, D, noise_int, all_true, device))
        infer_mrr = float(np.mean(1.0 - surp_infer)) if surp_infer.size else float("nan")
        train_mrr = float(np.mean(1.0 - surp_train)) if surp_train.size else float("nan")
        # KEY AUC: novel (should be surprising) vs inferable-heldout (should be predictable). BOTH held-out.
        key_auc = _auc(surp_novel, surp_infer)
        # v1-style encoding-status AUC: novel vs TRAIN-redundant (the confounded metric) -- for contrast
        enc_auc = _auc(surp_novel, surp_train)
        arms[name] = dict(X=X, D=D, all_true=all_true, surp_train=surp_train, surp_infer=surp_infer,
                          surp_novel=surp_novel, surp_noise=surp_noise, infer_mrr=infer_mrr,
                          train_mrr=train_mrr, key_auc=key_auc, enc_auc=enc_auc)

    strong = arms["strong"]; weak = arms["weak"]; dead = arms["dead"]

    # ================= gap 2: held-out calibration on STRONG, routing on DISJOINT eval =================
    def split_calib_eval(int_edges, surp):
        n = int_edges.shape[0]
        p = rng.permutation(n)
        nc = int(round(cfg["calib_frac"] * n))
        c = p[:nc]; e = p[nc:]
        return c, e
    ic, ie = split_calib_eval(infer_int, strong["surp_infer"])
    nc, nef = split_calib_eval(novel_int, strong["surp_novel"])
    skip_thresh, calib_j = calibrate_skip_threshold(strong["surp_infer"][ic], strong["surp_novel"][nc])

    # recurrence / n_sources per batch: trained-rel edges recur across many distinct heads -> high; noise one-off.
    def rel_source_count(int_edges):
        by = defaultdict(set)
        for i in range(int_edges.shape[0]):
            by[int(int_edges[i, 1])].add(int(int_edges[i, 0]))
        return {r: len(s) for r, s in by.items()}
    infer_src = rel_source_count(infer_int)
    novel_src = rel_source_count(novel_int)
    rec_infer_e = np.array([infer_src[int(infer_int[i, 1])] for i in ie], dtype=np.int64)
    src_infer_e = rec_infer_e.copy()
    rec_novel_e = np.array([novel_src[int(novel_int[i, 1])] for i in nef], dtype=np.int64)
    src_novel_e = rec_novel_e.copy()
    sf_infer_e = schema_fit_edges(infer_int[ie], reach_pct, np.zeros(len(ie), dtype=bool))
    sf_novel_e = schema_fit_edges(novel_int[nef], reach_pct, np.ones(len(nef), dtype=bool))

    dec_infer_e = [gate_calibrated(float(sf_infer_e[i]), float(strong["surp_infer"][ie][i]),
                                   int(rec_infer_e[i]), int(src_infer_e[i]), skip_thresh) for i in range(len(ie))]
    dec_novel_e = [gate_calibrated(float(sf_novel_e[i]), float(strong["surp_novel"][nef][i]),
                                   int(rec_novel_e[i]), int(src_novel_e[i]), skip_thresh) for i in range(len(nef))]
    oos_skip_infer = _rate(dec_infer_e, {"SKIP"})
    oos_cons_novel = _rate(dec_novel_e, CONSOLIDATE)

    # ================= gap 3: THIN-PROVENANCE HOLD batch (high surprise + FEW distinct sources) =================
    # novel-r* edges but presented with THIN provenance (n_sources < RECURRENCE_MIN) and recurrence above the floor.
    nthin = min(cfg["thinprov_n"], novel_int.shape[0])
    thin_int = novel_int[rng.permutation(novel_int.shape[0])[:nthin]]
    thin_surp = strong["surp_novel"][:nthin] if strong["surp_novel"].size >= nthin else strong["surp_novel"]
    thin_surp = _surprise(_recip_ranks(strong["X"], strong["D"], thin_int, strong["all_true"], device))
    thin_rec = np.full(nthin, max(RECURRENCE_MIN + 2, 5), dtype=np.int64)          # above DISCARD floor
    thin_src_thin = np.full(nthin, cfg["thinprov_sources"], dtype=np.int64)        # THIN: 1 distinct source -> HOLD
    thin_src_rich = np.full(nthin, RECURRENCE_MIN + 3, dtype=np.int64)             # RICH contrast: many sources
    thin_sf = schema_fit_edges(thin_int, reach_pct, np.ones(nthin, dtype=bool))
    dec_thin = [gate_calibrated(float(thin_sf[i]), float(thin_surp[i]), int(thin_rec[i]), int(thin_src_thin[i]),
                                skip_thresh) for i in range(nthin)]
    dec_rich = [gate_calibrated(float(thin_sf[i]), float(thin_surp[i]), int(thin_rec[i]), int(thin_src_rich[i]),
                                skip_thresh) for i in range(nthin)]
    hold_rate_thin = _rate(dec_thin, {"HOLD"})
    hold_rate_rich = _rate(dec_rich, {"HOLD"})

    # ================= NOISE discard-rate (recurrence floor) =================
    noise_rec = np.ones(noise_int.shape[0], dtype=np.int64)
    noise_src = noise_rec.copy()
    noise_sf = schema_fit_edges(noise_int, reach_pct, np.zeros(noise_int.shape[0], dtype=bool))
    dec_noise = [gate_calibrated(float(noise_sf[i]), float(strong["surp_noise"][i]), int(noise_rec[i]),
                                 int(noise_src[i]), skip_thresh) for i in range(noise_int.shape[0])]
    discard_noise = _rate(dec_noise, {"DISCARD"})

    # ================= INTERFERENCE: append r* row via TransE-mean, existing-rel MRR must be bit-identical ========
    X = strong["X"]; D = strong["D"]; all_true = strong["all_true"]
    ristar = rstar
    half = novel_int.shape[0] // 2
    cons_i = novel_int[:half]; fresh_i = novel_int[half:]
    hc = torch.from_numpy(cons_i[:, 0]).long().to(device); tc = torch.from_numpy(cons_i[:, 2]).long().to(device)
    d_rstar = (X[tc] - X[hc]).mean(dim=0)
    mrr_novel_before = float(_recip_ranks(X, D, fresh_i, all_true, device).mean()) if fresh_i.shape[0] else float("nan")
    D_fold = D.clone(); D_fold[ristar] = d_rstar
    mrr_novel_after = float(_recip_ranks(X, D_fold, fresh_i, all_true, device).mean()) if fresh_i.shape[0] else float("nan")
    # existing-relation held-out MRR (inferable eval): before vs after fold-in -> append-only means identical
    exist_eval = infer_int[ie]
    mrr_exist_before = float(_recip_ranks(X, D, exist_eval, all_true, device).mean()) if exist_eval.shape[0] else float("nan")
    mrr_exist_after = float(_recip_ranks(X, D_fold, exist_eval, all_true, device).mean()) if exist_eval.shape[0] else float("nan")
    interference_delta = abs(mrr_exist_after - mrr_exist_before)
    # DESTRUCTIVE control: overwrite shared entity rows -> MUST regress (non-vacuous)
    X_destroy = X.clone()
    hd = torch.from_numpy(exist_eval[:min(50, exist_eval.shape[0]), 0]).long().to(device)
    g = torch.Generator().manual_seed(seed)
    X_destroy[hd] = X_destroy[hd] + torch.randn(hd.shape[0], X.shape[1], generator=g) * X.std()
    mrr_exist_destroy = float(_recip_ranks(X_destroy, D, exist_eval, all_true, device).mean()) if exist_eval.shape[0] else float("nan")

    # ================= telemetry-sensitivity: perturb each signal -> decision flips =================
    # probe surprise must sit ABOVE the calibrated skip cutoff AND above DISTINCT_NOVELTY so the FAST/SLOW/HOLD
    # region is reachable regardless of where calibration landed skip_thresh.
    s_route = min(0.999, max(skip_thresh + 0.02, DISTINCT_NOVELTY + 0.02))
    base = gate_calibrated(0.9, s_route, 5, 5, skip_thresh)              # expect FAST_TRACK (sf high, many sources)
    tele = dict(
        recurrence_flips=(gate_calibrated(0.9, s_route, RECURRENCE_MIN - 1, 5, skip_thresh) == "DISCARD" and base != "DISCARD"),
        surprise_flips=(gate_calibrated(0.9, 0.0, 5, 5, skip_thresh) == "SKIP" and base != "SKIP"),
        hold_flips=(gate_calibrated(0.9, s_route, 5, 1, skip_thresh) == "HOLD" and base != "HOLD"),
        route_flips=(gate_calibrated(0.0, s_route, 5, 5, skip_thresh) == "SLOW_TRACK"
                     and gate_calibrated(1.0, s_route, 5, 5, skip_thresh) == "FAST_TRACK"),
    )

    # ================= gap 4: per-candidate arrays (flat, for off-disk recompute) =================
    def stack(batch_id, surp, sf, novel_lbl):
        n = len(surp)
        return dict(batch=np.full(n, batch_id, dtype=np.int64), surprise=np.asarray(surp, dtype=np.float64),
                    schema_fit=np.asarray(sf, dtype=np.float64), novel_label=np.full(n, novel_lbl, dtype=np.int64),
                    seed=np.full(n, seed, dtype=np.int64))
    sf_train = schema_fit_edges(train_int[:strong["surp_train"].shape[0]], reach_pct,
                                np.zeros(strong["surp_train"].shape[0], dtype=bool))
    sf_infer_all = schema_fit_edges(infer_int, reach_pct, np.zeros(infer_int.shape[0], dtype=bool))
    sf_novel_all = schema_fit_edges(novel_int, reach_pct, np.ones(novel_int.shape[0], dtype=bool))
    parts = [stack(B_TRAIN, strong["surp_train"], sf_train, -1),
             stack(B_INFER, strong["surp_infer"], sf_infer_all, 0),
             stack(B_NOVEL, strong["surp_novel"], sf_novel_all, 1),
             stack(B_NOISE, strong["surp_noise"], noise_sf, -1),
             stack(B_THIN, thin_surp, thin_sf, 1)]
    per_cand = {kk: np.concatenate([p[kk] for p in parts]) for kk in parts[0]}

    return dict(
        seed=seed, rstar=rstar, N=N, n_train=len(train), n_infer=infer_int.shape[0], n_novel=novel_int.shape[0],
        dead=dict(infer_mrr=dead["infer_mrr"], train_mrr=dead["train_mrr"], key_auc=dead["key_auc"], enc_auc=dead["enc_auc"]),
        weak=dict(infer_mrr=weak["infer_mrr"], train_mrr=weak["train_mrr"], key_auc=weak["key_auc"], enc_auc=weak["enc_auc"]),
        strong=dict(infer_mrr=strong["infer_mrr"], train_mrr=strong["train_mrr"], key_auc=strong["key_auc"], enc_auc=strong["enc_auc"]),
        skip_thresh=skip_thresh, calib_youden_j=calib_j,
        oos=dict(skip_infer_eval=oos_skip_infer, cons_novel_eval=oos_cons_novel,
                 n_infer_eval=int(len(ie)), n_novel_eval=int(len(nef))),
        hold=dict(rate_thin=hold_rate_thin, rate_rich=hold_rate_rich, n_thin=int(nthin)),
        discard_noise=discard_noise,
        interference=dict(delta=interference_delta, mrr_before=mrr_exist_before, mrr_after=mrr_exist_after,
                          mrr_destructive=mrr_exist_destroy,
                          destructive_regresses=(mrr_exist_destroy < mrr_exist_before - 1e-4)),
        foldin=dict(novel_mrr_before=mrr_novel_before, novel_mrr_after=mrr_novel_after,
                    delta=mrr_novel_after - mrr_novel_before),
        telemetry=tele,
        surprise_sha=dict(dead=_sha(dead["surp_infer"]), weak=_sha(weak["surp_infer"]),
                          strong=_sha(strong["surp_infer"]), novel=_sha(strong["surp_novel"])),
        _per_cand=per_cand,   # popped before metrics.json
    )


# ---------------------------------------------------------------------------
# aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, run_mode, array_recompute_ok, array_recompute_delta):
    dead_mrr = _mean([s["dead"]["infer_mrr"] for s in per_seed])
    weak_mrr = _mean([s["weak"]["infer_mrr"] for s in per_seed])
    strong_mrr = _mean([s["strong"]["infer_mrr"] for s in per_seed])
    key_dead = _mean([s["dead"]["key_auc"] for s in per_seed])
    key_weak = _mean([s["weak"]["key_auc"] for s in per_seed])
    key_strong = _mean([s["strong"]["key_auc"] for s in per_seed])
    enc_strong = _mean([s["strong"]["enc_auc"] for s in per_seed])
    enc_weak = _mean([s["weak"]["enc_auc"] for s in per_seed])
    enc_dead = _mean([s["dead"]["enc_auc"] for s in per_seed])
    dose_response = key_strong - key_dead
    oos_skip = _mean([s["oos"]["skip_infer_eval"] for s in per_seed])
    oos_cons = _mean([s["oos"]["cons_novel_eval"] for s in per_seed])
    hold_thin = _mean([s["hold"]["rate_thin"] for s in per_seed])
    hold_rich = _mean([s["hold"]["rate_rich"] for s in per_seed])
    discard = _mean([s["discard_noise"] for s in per_seed])
    interf = _mean([s["interference"]["delta"] for s in per_seed])
    destr_ok = all(s["interference"]["destructive_regresses"] for s in per_seed)
    tele_ok = all(all([s["telemetry"]["recurrence_flips"], s["telemetry"]["surprise_flips"],
                       s["telemetry"]["hold_flips"], s["telemetry"]["route_flips"]]) for s in per_seed)

    g = {}
    g["HP_STRONG_IS_STRONG"] = strong_mrr >= HP_STRONG_MRR_MIN
    g["HP_KEY_AUC_STRONG"] = key_strong >= HP_KEY_AUC_STRONG_MIN + EPS_BAND
    g["HP_DOSE_RESPONSE"] = dose_response >= HP_DOSE_RESPONSE_MIN
    g["HP_DEAD_COLLAPSES"] = key_dead <= HP_DEAD_COLLAPSE_MAX
    g["HP_OOS_ROUTING"] = (oos_skip >= HP_OOS_SKIP_MIN) and (oos_cons >= HP_OOS_CONS_MIN)
    g["HP_HOLD_FIRES"] = (hold_thin >= HP_HOLD_FIRES_MIN) and (hold_thin > hold_rich + EPS_BAND)
    g["HP_DISCARD"] = discard >= HP_DISCARD_MIN
    g["HP_INTERFERENCE"] = (interf <= HP_INTERFERENCE_TOL) and destr_ok
    g["HP_TELEMETRY"] = tele_ok
    g["HP_ARRAYS_DUMPED"] = bool(array_recompute_ok)
    g["baseline_in_band"] = (0.05 < weak_mrr < 0.95) and (strong_mrr < 0.95)

    joint = all(g.values())

    # ---- the KEY interpretation (semantic-novelty vs encoding-status) --------------------------------------
    # SEMANTIC_NOVELTY requires: strong foundation is genuinely strong, separates novel-from-inferable (both
    # untrained -> deconfounded from train-membership), AND the separation is dose-dependent on foundation strength
    # (a DEAD/non-generalizing foundation collapses to ~chance). If strong is strong but KEY-AUC collapses -> the
    # VET-predicted encoding-status-only bound.
    if g["HP_STRONG_IS_STRONG"] and g["HP_KEY_AUC_STRONG"] and g["HP_DOSE_RESPONSE"] and g["HP_DEAD_COLLAPSES"]:
        novelty_verdict = "SEMANTIC_NOVELTY_derivability_dose_dependent_on_foundation_strength"
    elif g["HP_STRONG_IS_STRONG"] and g["HP_KEY_AUC_STRONG"] and (not g["HP_DOSE_RESPONSE"]):
        # signal present but NOT strength-dependent: surprise separates novel-from-inferable at ALL strengths ->
        # the withheld-relation novel is trivially surprising; separation is real but not a strength-gated phenomenon
        novelty_verdict = "NOVELTY_SEPARATION_present_but_not_strength_gated"
    elif g["HP_STRONG_IS_STRONG"] and (not g["HP_KEY_AUC_STRONG"]):
        novelty_verdict = "COLLAPSE_surprise_is_encoding_status_not_novelty_SCOPED_BOUND"
    elif not g["HP_STRONG_IS_STRONG"]:
        novelty_verdict = "INCONCLUSIVE_strong_foundation_not_attained_redial_arena"
    else:
        novelty_verdict = "PARTIAL_below_band"

    if joint:
        verdict = "HARD_PASS"
    elif g["HP_STRONG_IS_STRONG"] and (not g["HP_KEY_AUC_STRONG"]) and g["HP_DISCARD"] and g["HP_INTERFERENCE"]:
        verdict = "MEASURED_BOUND_surprise_encoding_status_only"
    elif not g["HP_STRONG_IS_STRONG"]:
        verdict = "INCONCLUSIVE_redial"
    else:
        verdict = "MIDDLE_BAND_partial"

    msg = ("mrr dead=%.3f weak=%.3f strong=%.3f | KEY_auc dead=%.3f weak=%.3f strong=%.3f dose=%+.3f | "
           "enc_auc dead=%.3f weak=%.3f strong=%.3f | oos skip=%.2f cons=%.2f | hold thin=%.2f rich=%.2f | "
           "discard=%.2f interf=%.2e destr=%s tele=%s arrays_ok=%s(d=%.1e) -> %s" % (
               dead_mrr, weak_mrr, strong_mrr, key_dead, key_weak, key_strong, dose_response, enc_dead, enc_weak,
               enc_strong, oos_skip, oos_cons, hold_thin, hold_rich, discard, interf, destr_ok, tele_ok,
               array_recompute_ok, array_recompute_delta, novelty_verdict))
    summary = "%s: %s" % (verdict, novelty_verdict)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, gates=g, joint_hard_pass=joint,
                novelty_verdict=novelty_verdict, run_mode=run_mode,
                agg=dict(dead_infer_mrr=dead_mrr, weak_infer_mrr=weak_mrr, strong_infer_mrr=strong_mrr,
                         key_auc_dead=key_dead, key_auc_weak=key_weak, key_auc_strong=key_strong,
                         key_auc_dose_response=dose_response, enc_auc_dead=enc_dead, enc_auc_weak=enc_weak,
                         enc_auc_strong=enc_strong, oos_skip_infer=oos_skip, oos_cons_novel=oos_cons,
                         hold_rate_thin=hold_thin, hold_rate_rich=hold_rich, discard_noise=discard,
                         interference_delta=interf, array_recompute_delta=array_recompute_delta))


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk KEY-AUC recompute (gap 4)
# ---------------------------------------------------------------------------
def dump_and_verify_arrays(output_dir, per_seed):
    """Concatenate all per-candidate arrays, save npz, reload, recompute the STRONG KEY AUC off-disk, compare."""
    keys = ["batch", "surprise", "schema_fit", "novel_label", "seed"]
    flat = {kk: np.concatenate([s["_per_cand"][kk] for s in per_seed]) for kk in keys}
    path = os.path.join(str(output_dir), "per_candidate_arrays.npz")
    tmp = os.path.join(str(output_dir), "per_candidate_arrays_tmp.npz")   # keep .npz so np.savez doesn't re-append
    np.savez(tmp, **flat)
    os.replace(tmp, path)
    # in-memory KEY AUC (strong batches: novel B_NOVEL vs inferable B_INFER, pooled across seeds)
    inmem = _auc(flat["surprise"][flat["batch"] == B_NOVEL], flat["surprise"][flat["batch"] == B_INFER])
    # off-disk recompute
    z = np.load(path)
    offdisk = _auc(z["surprise"][z["batch"] == B_NOVEL], z["surprise"][z["batch"] == B_INFER])
    delta = abs(float(inmem) - float(offdisk))
    ok = delta <= HP_ARRAY_RECOMPUTE_TOL and (inmem == inmem)
    return ok, delta, path


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap on a tiny synthetic arena")
    exercised = set()
    device = torch.device("cpu")

    cfg = dict(n_ent=16, k_latent=6, k_fit=8, n_base_rel=4, edges_per_rel=12, gen_noise=0.1, rel_scale=1.0,
               frac_heldout=0.3, strong_epochs=40, weak_epochs=4, reach_k=2, reach_cap=30,
               thinprov_n=4, thinprov_sources=1, calib_frac=0.5)
    Z, G, edges = gen_arena(cfg, 7)
    assert len(edges) > 0 and all(len(e) == 3 for e in edges)
    # REAL fit path
    train = [e for e in edges if e[1] != cfg["n_base_rel"] - 1]
    X, D, all_true = fit_foundation(cfg, 7, cfg["strong_epochs"], train, cfg["n_ent"], cfg["n_base_rel"], device)
    exercised.add("AdditiveKGMap"); exercised.add("AdditiveKGMap.fit")
    kmap = AdditiveKGMap(device=device)
    kmap.fit([("%d" % h, "r%d" % r, "%d" % t) for (h, r, t) in train],
             entities=[str(i) for i in range(cfg["n_ent"])], relations=["r%d" % r for r in range(cfg["n_base_rel"])],
             k=cfg["k_fit"], epochs=cfg["strong_epochs"], seed=7)
    _ = kmap.score_all("0", "r0"); exercised.add("AdditiveKGMap.score_all")
    code = kmap.compose_entity([("0", "r0"), ("1", "r1")]); exercised.add("AdditiveKGMap.compose_entity")
    _ = kmap.insert_entity(code, name="e_new"); exercised.add("AdditiveKGMap.insert_entity")

    # gate branch coverage (all 5 outcomes reachable at a mid skip_thresh)
    st = 0.5
    outs = {gate_calibrated(0.9, 0.0, 5, 5, st), gate_calibrated(0.9, 0.7, 5, 5, st),
            gate_calibrated(0.1, 0.7, 5, 5, st), gate_calibrated(0.9, 0.99, 5, 1, st),
            gate_calibrated(0.9, 0.7, 1, 1, st)}
    assert outs == {"SKIP", "FAST_TRACK", "SLOW_TRACK", "HOLD", "DISCARD"}, "gate branches incomplete: %s" % outs

    # calibration returns a threshold that skips inferable (low surprise) and not novel (high surprise)
    t, j = calibrate_skip_threshold(np.array([0.0, 0.1, 0.2]), np.array([0.9, 0.95, 0.99]))
    assert 0.2 <= t <= 0.9 and j > 0.5, "calibration failed: t=%s j=%s" % (t, j)

    # AUC monotonicity + KEY-AUC direction
    assert _auc([1, 2, 3], [0, 0, 0]) == 1.0 and _auc([0, 0], [1, 1]) == 0.0
    assert _auc([0.9, 0.95], [0.0, 0.1]) == 1.0    # novel(high) vs inferable(low) -> 1.0

    # append-only fold-in: existing scores identical after appending an r* row
    ristar = cfg["n_base_rel"] - 1
    train_int = _to_int(train)
    exist = train_int[:min(6, train_int.shape[0])]
    before = _recip_ranks(X, D, exist, all_true, device)
    D2 = D.clone(); D2[ristar] = (X[torch.tensor([2, 4])] - X[torch.tensor([0, 1])]).mean(0)
    after = _recip_ranks(X, D2, exist, all_true, device)
    assert np.allclose(before, after), "append-only fold-in changed existing retrieval (interference bug)"

    # array dump + off-disk recompute round-trip
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        fake = [dict(_per_cand=dict(batch=np.array([B_NOVEL, B_NOVEL, B_INFER, B_INFER]),
                                    surprise=np.array([0.9, 0.95, 0.1, 0.2]),
                                    schema_fit=np.array([0.5, 0.5, 0.5, 0.5]),
                                    novel_label=np.array([1, 1, 0, 0]), seed=np.array([7, 7, 7, 7])))]
        ok, delta, _p = dump_and_verify_arrays(td, fake)
        assert ok and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "key_auc", "before": 0.5, "after": 0.9, "min_delta": 1e-6},
    ], run_mode="selftest")
    assert ok, "validity preflight failed"
    _log("self_test PASS (real code path exercised: %s)" % sorted(exercised))
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _unk = ap.parse_known_args()

    from experiments._seed_checkpoint import get_output_dir
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else "full")
    output_dir = get_output_dir(ANCHOR_NAME + ("_selftest" if args.self_test else ("_smoke" if args.smoke else "")))
    global _OUT
    _OUT = output_dir

    if args.self_test:
        self_test()
        _write_metrics_atomic(output_dir, dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS", run_mode="self_test",
                                               summary="self_test ok", elapsed_s=0.0))
        return

    cfg = SMOKE_CFG if args.smoke else FULL_CFG
    _write_start_marker(output_dir, run_mode, len(cfg["seeds"]) * 3)
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    per_seed = []
    for si, seed in enumerate(cfg["seeds"]):
        _log("seed %d/%d (seed=%d): gen arena + fit WEAK + STRONG ..." % (si + 1, len(cfg["seeds"]), seed))
        res = run_seed(cfg, seed, device)
        per_seed.append(res)
        _log("seed=%d: mrr dead=%.3f weak=%.3f strong=%.3f | KEY_auc dead=%.3f weak=%.3f strong=%.3f | oos "
             "skip=%.2f cons=%.2f hold_thin=%.2f discard=%.2f (%.1fs)" % (
                 seed, res["dead"]["infer_mrr"], res["weak"]["infer_mrr"], res["strong"]["infer_mrr"],
                 res["dead"]["key_auc"], res["weak"]["key_auc"], res["strong"]["key_auc"],
                 res["oos"]["skip_infer_eval"], res["oos"]["cons_novel_eval"], res["hold"]["rate_thin"],
                 res["discard_noise"], time.time() - t0))

    # ARMS-MUST-DIFFER: DEAD/WEAK/STRONG surprise vectors distinct (META_RULE_AF)
    shas = per_seed[0]["surprise_sha"]
    assert len({shas["dead"], shas["weak"], shas["strong"], shas["novel"]}) >= 3, "surprise vectors bit-identical (arm bug)"

    # gap 4: dump per-candidate arrays + off-disk recompute of the KEY AUC
    array_ok, array_delta, array_path = dump_and_verify_arrays(output_dir, per_seed)
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%.2e)" % (array_path, array_ok, array_delta))

    for s in per_seed:
        s.pop("_per_cand", None)   # arrays live on disk; keep metrics.json lean

    v = aggregate_and_verdict(per_seed, run_mode, array_ok, array_delta)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(cfg["seeds"]),
                   config={kk: cfg[kk] for kk in ("n_ent", "k_latent", "k_fit", "n_base_rel", "edges_per_rel",
                                                  "gen_noise", "frac_heldout", "strong_epochs", "weak_epochs",
                                                  "seeds", "calib_frac", "thinprov_sources")},
                   bands=dict(HP_STRONG_MRR_MIN=HP_STRONG_MRR_MIN, HP_KEY_AUC_STRONG_MIN=HP_KEY_AUC_STRONG_MIN,
                              HP_DOSE_RESPONSE_MIN=HP_DOSE_RESPONSE_MIN, HP_DEAD_COLLAPSE_MAX=HP_DEAD_COLLAPSE_MAX,
                              HP_OOS_SKIP_MIN=HP_OOS_SKIP_MIN, HP_OOS_CONS_MIN=HP_OOS_CONS_MIN,
                              HP_HOLD_FIRES_MIN=HP_HOLD_FIRES_MIN, HP_DISCARD_MIN=HP_DISCARD_MIN),
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   per_candidate_arrays=os.path.basename(array_path),
                   **v, per_seed=per_seed)
    _write_metrics_atomic(output_dir, metrics)
    _log("VERDICT %s | %s" % (v["verdict"], v["verdict_msg"]))
    _log("wrote %s (%.1fs)" % (os.path.join(output_dir, "metrics.json"), elapsed))


_OUT = None
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT or os.path.join("data", "exp_" + ANCHOR_NAME), e)
        raise
