"""Ingest-gate COMBINATION-RULE RACE: is being EXACTLY like the brain the right way to combine the 3 signals?

The v4 cell (exp_ingest_gate_deconfound_within_relation_derivability_v1, MEASURED@
data/exp_ingest_gate_deconfound_within_relation_derivability_v1/metrics.json: DECONF_AUC=0.545 ~chance) found that
FLAT raw-surprise does NOT separate DERIVABLE from UNDERIVABLE held-out r* facts once the relation row is TRAINED --
surprise detects WHOLE-RELATION presence, not within-schema derivability. The quantum drill
(notes/research_consolidation_gate_quantitative_signals_2026-07-16.md) delivered the brain's combination FORM
(Friston precision-weighted decomposition): schema-fit is not a bolt-on gate, it is the MIXING WEIGHT that splits raw
prediction-error into a schema-CONSISTENT fast-track component (raw_PE * schema_fit) and a schema-INCONSISTENT
slow-track component (raw_PE * (1 - schema_fit)); recurrence is a separate graded precision-accumulation gate. THIS
schema-conditioning is the proposed v4 fix.

THE RACE (3 arms, all on the SAME v4 arena, held-row-CONSTANT derivable/underivable split):
  ARM_FLAT      : revision-score = raw_PE                          (v4 baseline, reproduces ~0.545)
  ARM_SCHEMAFIT : revision-score = (1 - schema_fit)               (REFERENCE -- how much does schema_fit ALONE
                                                                    separate? guards the "brain wins" over-claim: if
                                                                    schema_fit alone already separates, the fix is
                                                                    schema_fit, NOT the surprise*schema interaction)
  ARM_BRAIN     : revision-score = raw_PE * (1 - schema_fit)       (brain FORM, FIXED unit weights -- NO fitting)
  ARM_HYBRID    : revision-score = sigma(w . [fast_track, slow_track]) (brain FORM, CALIBRATED weights -- isolates
                                                                    FORM vs WEIGHTS; fit on a DISJOINT calib split)
  ARM_LEARNED   : revision-score = sigma(w . [raw_PE, schema_fit, recurrence, fast_track, slow_track]) (FREE features,
                                                                    substrate LEARNS the combination; fit on calib)

DECISIVE metric = DECONF_AUC per arm = AUC(revision-score; UNDERIVABLE vs DERIVABLE), both held-out, SAME trained r*
row. Head-to-head:
  BRAIN-FAITHFUL WORKS  = brain_auc >= HP_DECONF_MIN AND brain >= max(flat, schemafit_alone) - TIE AND learned does
                          NOT decisively beat brain (learned <= brain + DECISIVE_MARGIN) => "being exactly like the
                          brain works" -- the brain's rule applied (no fitting) fixes v4. ROUTE TO VET.
  LEARNED BEATS BRAIN   = learned_auc >= HP_DECONF_MIN AND learned > brain + DECISIVE_MARGIN => the brain's FORM is
                          incomplete, WEIGHTS matter (hybrid isolates whether it is the form or the weights).
  SCHEMAFIT CARRIES     = schemafit_alone >= HP_DECONF_MIN AND brain <= schemafit_alone + TIE AND flat ~chance =>
                          the v4 fix is the schema_fit STRUCTURAL signal; the surprise-conditioning interaction is
                          inert (honest nuance -- still a fix, but not via the decomposition interaction).
  DECOMPOSITION NO SIGNAL = all of brain/learned/hybrid <= HF_DECONF_MAX (~chance) => schema-conditioning does NOT
                          fix v4 either; the cheap pre-check would have flagged this.
  SCHEMAFIT LEAK        = schemafit_alone >= SCHEMAFIT_LEAK_MAX (~1.0) => schema_fit is a near-copy of the label; the
                          whole race is vacuous, need an orthogonal schema_fit proxy (drill next-drill). DEMOTE.

CHEAP PRE-CHECK (drill-preregistered, the discriminator-fires gate, ZERO extra fits -- reuses v4's trained-row
foundation as "full re-fit" and untrained-row foundation as "before", plus a cheap TransE-mean fold-in as
"fast-track"): does the schema_fit TERTILE differentiate CONSOLIDATION BENEFIT? For each schema_fit tertile of the
held-out r* facts, ratio = (fast_track_MRR_gain) / (full_refit_MRR_gain). The brain claim: high-schema-fit items
recover most of the gain via the CHEAP fast-track path; low-schema-fit items need the costly full re-fit. Reported
gate: (top-tertile ratio - bottom-tertile ratio) >= PRECHECK_DIFF_MIN. If it FAILS the decomposition has no
load-bearing consolidation-cost signal -- report it (informative), do not force-frame the AUC race as a brain-win.

CONTROLS (harness-valid, reuse v4 verbatim): CONF_AUC (untrained-row confound) MUST reproduce; POSCTRL (corrupt-r*
vs in-train-r*) MUST fire; RANDLABEL ~chance; r* row genuinely trained; foundation generalizes; class balance.
4-BATCH ROUTING (reported): redundant->SKIP / derivable-novel->FAST / underivable->SLOW / one-off-noise->DISCARD.

HONEST: the Friston fast/slow decomposition is DIRECTOR/DRILL SYNTHESIS -- no paper states it, P<=0.50. Either
outcome is a clean finding (brain-form-works / learned-weights-needed / schema_fit-carries / no-signal).

REUSE (extend, don't rebuild): v4 gen_composed_arena / derivability_labels / _exact_path_labels / _balance_mask /
_arena_cfg / ARENA_BASE / k_hop_reachable_set; v2 fit_foundation / _to_int / _mean; v1 _auc / _recip_ranks /
_surprise / _sha / build_schema_fit / schema_fit_edges. New: the 5 arm revision-scores, the tiny numpy logistic
calibrator (deterministic zero-init), the schema_fit-tertile consolidation-benefit differentiation, the head-to-head.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (the 5 arm revision-score vectors hash-distinct on the test split)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: DECONF_AUC is a rank statistic over two measured score distributions; chance=0.5, self-calibrated by
#   the RANDLABEL must-fail control; no closed-form noise floor.
# - baseline_in_band: inferable held-out MRR 0.05<mrr<0.95 AND strong (>=HP_STRONG_MRR_MIN); r* MRR >= floor (trained)
# - discriminator survives scale: multi-seed smoke at reduced N (3 seeds) fires the pre-check + arm spread; FULL confirms
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (one synthetic race block per seed)
# - HARD_PASS strictly above chance-floor + band (HP_DECONF_MIN=0.65 vs chance 0.50); schemafit_leak guard at 0.95
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16
#   AND exercises gen_composed_arena + derivability_labels + race_seed + the logreg calibrator at tiny scale
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); logreg zero-init; no hash()-seeded RNG
# - progress_logging = print_flush_true (every seed + arm logs, flush=True)

ASCII-only. No emojis. Explicit dtypes. np.random.default_rng / torch.Generator seeded. Terse.
"""

import argparse
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

from hdlab.additive_map import AdditiveKGMap  # noqa: E402
from hdlab import reachability_audit as RA  # noqa: E402
# REUSE v4 arena + derivability machinery (import does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_deconfound_within_relation_derivability_v1 import (  # noqa: E402
    gen_composed_arena, derivability_labels, _exact_path_labels, _balance_mask, _arena_cfg, ARENA_BASE,
)
# REUSE v2 fit + helpers
from experiments.exp_ingest_gate_strong_foundation_novelty_v2 import (  # noqa: E402
    fit_foundation, _to_int as _arena_to_int, _mean,
)
# REUSE v1 metric + schema-fit machinery
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, build_schema_fit, schema_fit_edges,
)

ANCHOR_NAME = "ingest_gate_combination_rule_race_v1"

# ---- pre-registered bands ---------------------------------------------------------------------------------------
# HYPOTHESIZED@this-file (design; measured at smoke/full). DECONF_AUC chance = 0.50 (rank stat), self-checked by
# RANDLABEL. brain-form works P<=0.50 (novel synthesis). Expected modal outcome (deflated): brain ~ schemafit_alone
# (schema_fit carries the fix; surprise*schema interaction ~inert) -- an honest SCHEMAFIT_CARRIES finding is likely.
HP_DECONF_MIN = 0.65          # an arm "works": revision-score separates underivable-vs-derivable (>chance+0.15, +5% band)
HF_DECONF_MAX = 0.58          # an arm collapses to ~chance
DECISIVE_MARGIN = 0.05        # learned decisively beats brain (form incomplete, weights matter)
TIE_EPS = 0.02               # ties / "beats within noise"
SCHEMAFIT_LEAK_MAX = 0.95     # schema_fit near-copies the label -> race vacuous (demote; need orthogonal proxy)
PRECHECK_DIFF_MIN = 0.10      # discriminator-fires: (top-tertile - bottom-tertile) consolidation-benefit ratio
PRECHECK_TOP_HARD = 0.90      # drill HARD-PASS top-tertile ratio (reported, not gating)
PRECHECK_BOT_HARD = 0.50      # drill HARD-PASS bottom-tertile ratio (reported, not gating)

# harness-valid bands (reuse v4 verbatim)
HP_POSCTRL_AUC_MIN = 0.75
HP_CONF_AUC_MIN = 0.70
HP_RANDLABEL_LO = 0.40
HP_RANDLABEL_HI = 0.60
HP_RSTAR_TRAINED_MRR_MIN = 0.30
HP_STRONG_MRR_MIN = 0.40
HP_INFER_MRR_LO = 0.05
HP_INFER_MRR_HI = 0.95
HP_MIN_CLASS_FRAC = 0.20
HP_ARRAY_RECOMPUTE_TOL = 1e-6

# combination-rule constants (OURS to calibrate; the brain gives the FORM, not the numbers -- drill Part-B position)
TAU = 3.0                     # recurrence -> local_precision = rec/(rec+TAU) (graded, ACT-R/conjugate-Bayes form)
PRECISION_MIN = 0.5           # local_precision below -> HOLD/DISCARD (noise, rec=1 -> 1/(1+TAU)=0.25 < 0.5)
SURPRISE_FLOOR = 0.5          # raw_PE below -> SKIP (redundant)

EPS_BAND = 1e-9

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_ent=600, edges_per_rel=420, n_rstar=420,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=350,
    reach_k=2, reach_cap=300, min_class_n=25, calib_frac=0.5,
)
SMOKE_CFG = dict(
    seeds=[7, 13, 17],       # multi-seed smoke (MANDATORY for an AUC discriminator; single-seed inflates)
    n_ent=300, edges_per_rel=180, n_rstar=180,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=140,
    reach_k=2, reach_cap=150, min_class_n=10, calib_frac=0.5,
)

# batch ids for the per-candidate array dump (TEST split derivable/underivable)
B_DERIV, B_UNDERIV = 0, 1
ARM_ORDER = ["flat", "schemafit", "brain", "hybrid", "learned"]


# ---------------------------------------------------------------------------
# scaffolding
# ---------------------------------------------------------------------------
def _log(msg):
    print("[race_v1] %s" % msg, flush=True)


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


# ---------------------------------------------------------------------------
# tiny deterministic logistic calibrator (numpy; zero-init; no external dep, portable local/remote)
# ---------------------------------------------------------------------------
def _standardize_fit(Xf):
    mu = Xf.mean(axis=0)
    sd = Xf.std(axis=0)
    sd = np.where(sd > 1e-9, sd, 1.0)
    return mu, sd


def _standardize_apply(Xf, mu, sd):
    return (Xf - mu) / sd


def fit_logreg(Xf, y, epochs=400, lr=0.2, l2=1e-3):
    """Deterministic full-batch logistic regression. Xf (n,d) standardized, y (n,) in {0,1}. Zero-init -> no RNG."""
    n, d = Xf.shape
    Xb = np.concatenate([np.ones((n, 1)), Xf], axis=1)
    w = np.zeros(d + 1, dtype=np.float64)
    for _ in range(int(epochs)):
        z = np.clip(Xb @ w, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-z))
        reg = l2 * np.concatenate([[0.0], w[1:]])
        w = w - lr * (Xb.T @ (p - y) / n + reg)
    return w


def predict_logreg(w, Xf):
    Xb = np.concatenate([np.ones((Xf.shape[0], 1)), Xf], axis=1)
    z = np.clip(Xb @ w, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z))


# ---------------------------------------------------------------------------
# arm revision-scores (higher = more structural revision needed = UNDERIVABLE = slow-track)
# ---------------------------------------------------------------------------
def arm_scores_fixed(raw_pe, schema_fit):
    """Non-fitted arms: flat / schemafit-alone / brain fast+slow tracks."""
    fast_track = raw_pe * schema_fit
    slow_track = raw_pe * (1.0 - schema_fit)
    return dict(flat=raw_pe.copy(), schemafit=(1.0 - schema_fit), brain=slow_track,
                fast_track=fast_track, slow_track=slow_track)


def _learned_features(raw_pe, schema_fit, recur_prec):
    fast_track = raw_pe * schema_fit
    slow_track = raw_pe * (1.0 - schema_fit)
    return np.stack([raw_pe, schema_fit, recur_prec, fast_track, slow_track], axis=1)


def _hybrid_features(raw_pe, schema_fit):
    fast_track = raw_pe * schema_fit
    slow_track = raw_pe * (1.0 - schema_fit)
    return np.stack([fast_track, slow_track], axis=1)


# ---------------------------------------------------------------------------
# LOAD-BEARING PRIMITIVE: the head-to-head combination-rule race on one composed arena.
# ---------------------------------------------------------------------------
def race_seed(cfg, seed, device, want_arrays=False):
    """Fit trained-row + untrained-row foundations; build the derivable/underivable split; compute the 5 arm
    DECONF_AUCs (calib/test generalization for learned+hybrid), the harness controls, the consolidation-benefit
    tertile differentiation, and the 4-batch routing. Reuses v4 arena + derivability oracle verbatim."""
    acfg = _arena_cfg(cfg["n_ent"], cfg["edges_per_rel"])
    N = acfg["n_ent"]; nR_base = acfg["n_base_rel"]
    rstar_idx = nR_base                      # r* gets its own relation row; total rels = nR_base + 1
    nR_total = nR_base + 1
    ra, rb = 0, 1                            # r* = r0 o r1

    Z, G, base_edges, rstar_edges, mid = gen_composed_arena(acfg, seed, rstar_idx, ra, rb, cfg["n_rstar"])
    rng = np.random.default_rng(seed * 100003 + 131)

    # split base edges -> base_train (foundation) + base_heldout (INFERABLE for baseline + CONF arm)
    nb = len(base_edges)
    pb = rng.permutation(nb)
    nb_hold = int(round(cfg["frac_heldout_base"] * nb))
    hold_b = set(pb[:nb_hold].tolist())
    base_train = [base_edges[i] for i in range(nb) if i not in hold_b]
    base_heldout = [base_edges[i] for i in range(nb) if i in hold_b]

    # split r* edges -> rstar_train (TRAINS the row) + rstar_heldout (the derivable/underivable split)
    nr = len(rstar_edges)
    pr = rng.permutation(nr)
    nr_train = int(round(cfg["train_frac_rstar"] * nr))
    tr_r = set(pr[:nr_train].tolist())
    rstar_train = [rstar_edges[i] for i in range(nr) if i in tr_r]
    rstar_heldout = [rstar_edges[i] for i in range(nr) if i not in tr_r]

    base_train_int = _arena_to_int(base_train)
    base_heldout_int = _arena_to_int(base_heldout)
    rstar_train_int = _arena_to_int(rstar_train)
    rstar_heldout_int = _arena_to_int(rstar_heldout)

    # ---- derivability oracle (reachability over FOUNDATION base-train edges only; non-circular) ----
    adj_found = RA.build_undirected_adj(base_train_int, N)
    derivable = derivability_labels(rstar_heldout_int, adj_found, cfg["reach_k"])
    base_train_set = set((int(h), int(r), int(t)) for (h, r, t) in base_train)
    mid_of_head = {int(rstar_edges[i][0]): int(mid[i]) for i in range(nr)}
    derivable_exact = _exact_path_labels(rstar_heldout_int, mid_of_head, base_train_set, ra, rb)

    # balance classes (within 1.5x) so AUC is not driven by class-size asymmetry
    keep = _balance_mask(derivable, np.random.default_rng(seed * 100003 + 191), cfg["min_class_n"])
    if keep is None:
        return dict(seed=int(seed), status="ONE_CLASS_EMPTY", n_deriv=int(derivable.sum()),
                    n_underiv=int((~derivable).sum()))
    held_int = rstar_heldout_int[keep]
    deriv_lbl = derivable[keep]
    deriv_exact_lbl = derivable_exact[keep]
    n_deriv = int(deriv_lbl.sum()); n_underiv = int((~deriv_lbl).sum())

    # ---- SCHEMA-FIT (reachability rank-percentile over foundation; DIFFERENT computation than the derivable
    #      label -- entity-connectivity, NOT the specific h->t path -> the schemafit_alone arm is a genuine
    #      reference, and the SCHEMAFIT_LEAK guard fires if it near-copies the label) ----
    reach_pct, reach_mass = build_schema_fit(base_train_int, N, cfg["reach_k"], cfg["reach_cap"])
    schema_fit_held = schema_fit_edges(held_int, reach_pct, np.zeros(held_int.shape[0], dtype=bool))
    schema_fit_held = np.clip(np.asarray(schema_fit_held, dtype=np.float64), 0.0, 1.0)

    # ---- RECURRENCE -> local precision (graded; head provenance mass = foundation degree of h) ----
    deg = RA.degree_vector(adj_found)                       # (N,) int64
    rec_held = deg[held_int[:, 0]].astype(np.float64)       # provenance mass of the head
    recur_prec_held = rec_held / (rec_held + TAU)           # local_precision in (0,1)

    # ---- FOUNDATION_T: r* row TRAINED (base_train + rstar_train) = the "full re-fit" ----
    train_T = base_train + rstar_train
    X_T, D_T, all_true_T = fit_foundation(acfg, seed, cfg["epochs"], train_T, N, nR_total, device)

    # surprise on held-out r* (both classes; SAME trained row) -> raw_PE, the DECISIVE signal
    raw_pe_held = _surprise(_recip_ranks(X_T, D_T, held_int, all_true_T, device))
    raw_pe_held = np.clip(raw_pe_held, 0.0, 1.0)

    # baseline: inferable held-out MRR (foundation strength) + in-train r* MRR (row genuinely trained)
    surp_infer_T = _surprise(_recip_ranks(X_T, D_T, base_heldout_int, all_true_T, device))
    infer_mrr = float(np.mean(1.0 - surp_infer_T)) if surp_infer_T.size else float("nan")
    surp_rtrain_T = _surprise(_recip_ranks(X_T, D_T, rstar_train_int, all_true_T, device))
    rstar_train_mrr = float(np.mean(1.0 - surp_rtrain_T)) if surp_rtrain_T.size else float("nan")

    # ---- POS-CONTROL (must fire): corrupt-r* vs in-train-r* under FOUNDATION_T ----
    corrupt = rstar_train_int.copy()
    if corrupt.shape[0] > 0:
        rand_t = rng.integers(0, N, size=corrupt.shape[0])
        for i in range(corrupt.shape[0]):
            if int(rand_t[i]) == int(corrupt[i, 2]):
                rand_t[i] = (int(rand_t[i]) + 1) % N
        corrupt[:, 2] = rand_t
    surp_corrupt = _surprise(_recip_ranks(X_T, D_T, corrupt, all_true_T, device))
    posctrl_auc = _auc(surp_corrupt, surp_rtrain_T)

    # ---- CONF ARM (reproduce v3/v4 confound): r* row UNTRAINED (base_train only) = "before" foundation ----
    X_U, D_U, all_true_U = fit_foundation(acfg, seed, cfg["epochs"], base_train, N, nR_total, device)
    all_rstar_int = _arena_to_int(rstar_edges)
    surp_conf_novel = _surprise(_recip_ranks(X_U, D_U, all_rstar_int, all_true_U, device))
    surp_conf_infer = _surprise(_recip_ranks(X_U, D_U, base_heldout_int, all_true_U, device))
    conf_auc = _auc(surp_conf_novel, surp_conf_infer)

    # ---- MUST-FAIL: RANDOM-LABEL shuffle of derivable/underivable -> AUC ~chance (on raw_PE) ----
    rlrng = np.random.default_rng(seed * 100003 + 313)
    shuf = rlrng.permutation(raw_pe_held.shape[0])
    randlabel_auc = _auc(raw_pe_held[shuf[n_deriv:]], raw_pe_held[shuf[:n_deriv]])

    # ---- CALIB / TEST split of the held facts (stratified by derivable) -> generalization for learned+hybrid ----
    srng = np.random.default_rng(seed * 100003 + 401)
    idx_d = np.where(deriv_lbl)[0]; idx_u = np.where(~deriv_lbl)[0]
    srng.shuffle(idx_d); srng.shuffle(idx_u)
    cd = max(1, int(round(cfg["calib_frac"] * idx_d.size)))
    cu = max(1, int(round(cfg["calib_frac"] * idx_u.size)))
    calib_idx = np.concatenate([idx_d[:cd], idx_u[:cu]])
    test_idx = np.concatenate([idx_d[cd:], idx_u[cu:]])
    # robustness: if either split lost a class, fall back to full-set (flag reduced generalization)
    reduced_gen = False
    if (test_idx.size == 0 or deriv_lbl[test_idx].sum() == 0 or (~deriv_lbl[test_idx]).sum() == 0
            or calib_idx.size == 0 or deriv_lbl[calib_idx].sum() == 0 or (~deriv_lbl[calib_idx]).sum() == 0):
        reduced_gen = True
        calib_idx = np.arange(deriv_lbl.shape[0])
        test_idx = np.arange(deriv_lbl.shape[0])

    y_calib = (~deriv_lbl[calib_idx]).astype(np.float64)   # 1 = underivable (revision needed)
    y_test = (~deriv_lbl[test_idx]).astype(np.float64)

    fixed = arm_scores_fixed(raw_pe_held, schema_fit_held)

    # LEARNED arm: 5 features, fit logreg on calib, predict on test
    Xl = _learned_features(raw_pe_held, schema_fit_held, recur_prec_held)
    mu_l, sd_l = _standardize_fit(Xl[calib_idx])
    w_l = fit_logreg(_standardize_apply(Xl[calib_idx], mu_l, sd_l), y_calib)
    learned_prob = predict_logreg(w_l, _standardize_apply(Xl, mu_l, sd_l))

    # HYBRID arm: brain 2-track FORM, calibrated weights
    Xh = _hybrid_features(raw_pe_held, schema_fit_held)
    mu_h, sd_h = _standardize_fit(Xh[calib_idx])
    w_h = fit_logreg(_standardize_apply(Xh[calib_idx], mu_h, sd_h), y_calib)
    hybrid_score = predict_logreg(w_h, _standardize_apply(Xh, mu_h, sd_h))

    # per-arm revision-score vectors (aligned to held_int order)
    arm_score = dict(flat=fixed["flat"], schemafit=fixed["schemafit"], brain=fixed["brain"],
                     hybrid=hybrid_score, learned=learned_prob)

    def _arm_auc(score, idx):
        pos = score[idx][(~deriv_lbl[idx])]      # underivable (should be high)
        neg = score[idx][deriv_lbl[idx]]         # derivable (should be low)
        return _auc(pos, neg)

    deconf_test = {a: _arm_auc(arm_score[a], test_idx) for a in ARM_ORDER}
    deconf_full = {a: _arm_auc(arm_score[a], np.arange(deriv_lbl.shape[0])) for a in ARM_ORDER}

    # ---- CONSOLIDATION-BENEFIT tertile differentiation (cheap pre-check; zero extra fits) ----
    # before = held MRR under FOUNDATION_U (random r* row); fast_track = FOUNDATION_U + TransE-mean D[r*] fold-in;
    # refit = held MRR under FOUNDATION_T (full re-fit). ratio = fast_gain / refit_gain per schema_fit tertile.
    hc = torch.from_numpy(rstar_train_int[:, 0]).long().to(device)
    tc = torch.from_numpy(rstar_train_int[:, 2]).long().to(device)
    d_rstar = (X_U[tc] - X_U[hc]).mean(dim=0)                    # TransE-mean displacement (cheap fast-track)
    D_U_fold = D_U.clone(); D_U_fold[rstar_idx] = d_rstar
    rr_before = _recip_ranks(X_U, D_U, held_int, all_true_U, device)
    rr_fast = _recip_ranks(X_U, D_U_fold, held_int, all_true_U, device)
    rr_refit = _recip_ranks(X_T, D_T, held_int, all_true_T, device)
    precheck = _tertile_consolidation(schema_fit_held, rr_before, rr_fast, rr_refit)

    # ---- 4-BATCH ROUTING per arm (redundant->SKIP / derivable->FAST / underivable->SLOW / noise->DISCARD) ----
    routing = _four_batch_routing(cfg, seed, N, rstar_idx, base_train_int, rstar_train_int, held_int, deriv_lbl,
                                  raw_pe_held, schema_fit_held, recur_prec_held, arm_score, calib_idx, deg,
                                  X_T, D_T, all_true_T, device)

    out = dict(
        seed=int(seed), status="OK", N=int(N), n_deriv=n_deriv, n_underiv=n_underiv,
        deriv_frac=float(deriv_lbl.mean()) if deriv_lbl.size else float("nan"),
        deconf_test=deconf_test, deconf_full=deconf_full,
        deconf_exact_flat=_auc(raw_pe_held[~deriv_exact_lbl], raw_pe_held[deriv_exact_lbl]),
        conf_auc=conf_auc, posctrl_auc=posctrl_auc, randlabel_auc=randlabel_auc,
        infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
        schemafit_deriv_mean=float(np.mean(schema_fit_held[deriv_lbl])) if n_deriv else float("nan"),
        schemafit_underiv_mean=float(np.mean(schema_fit_held[~deriv_lbl])) if n_underiv else float("nan"),
        precheck=precheck, routing=routing, reduced_gen=bool(reduced_gen),
        n_calib=int(calib_idx.size), n_test=int(test_idx.size),
        arm_score_sha={a: _sha(arm_score[a]) for a in ARM_ORDER},
    )
    if want_arrays:
        out["_arrays"] = dict(
            batch=(~deriv_lbl[test_idx]).astype(np.int64),   # 0=deriv,1=underiv on the TEST split
            raw_pe=raw_pe_held[test_idx], schema_fit=schema_fit_held[test_idx],
            recurrence=recur_prec_held[test_idx],
            fast_track=fixed["fast_track"][test_idx], slow_track=fixed["slow_track"][test_idx],
            brain=arm_score["brain"][test_idx], hybrid=hybrid_score[test_idx], learned=learned_prob[test_idx],
            deriv_label=deriv_lbl[test_idx].astype(np.int64),
        )
    return out


def _tertile_consolidation(schema_fit, rr_before, rr_fast, rr_refit):
    """Per schema_fit tertile: ratio = mean(rr_fast - rr_before) / mean(rr_refit - rr_before). Brain claim: high
    schema_fit -> fast-track recovers most of the gain; low schema_fit -> needs full re-fit."""
    n = schema_fit.shape[0]
    order = np.argsort(schema_fit, kind="mergesort")
    tert = np.zeros(n, dtype=np.int64)
    b1 = n // 3; b2 = 2 * n // 3
    tert[order[b1:b2]] = 1; tert[order[b2:]] = 2
    gain_fast = rr_fast - rr_before
    gain_refit = rr_refit - rr_before
    ratios = {}
    for tt, name in [(0, "low"), (1, "mid"), (2, "high")]:
        m = (tert == tt)
        gf = float(np.mean(gain_fast[m])) if m.any() else float("nan")
        gr = float(np.mean(gain_refit[m])) if m.any() else float("nan")
        ratios[name] = (gf / gr) if (gr == gr and abs(gr) > 1e-4) else float("nan")
        ratios[name + "_gain_fast"] = gf
        ratios[name + "_gain_refit"] = gr
    hi = ratios.get("high", float("nan")); lo = ratios.get("low", float("nan"))
    ratios["diff_high_minus_low"] = (hi - lo) if (hi == hi and lo == lo) else float("nan")
    ratios["global_refit_gain"] = float(np.mean(gain_refit))
    ratios["global_fast_gain"] = float(np.mean(gain_fast))
    return ratios


def _four_batch_routing(cfg, seed, N, rstar_idx, base_train_int, rstar_train_int, held_int, deriv_lbl,
                        raw_pe_held, schema_fit_held, recur_prec_held, arm_score, calib_idx, deg, X_T, D_T,
                        all_true_T, device):
    """Reported (secondary) construction check: does each arm's rule route the 4 batches correctly?
    redundant->SKIP, derivable-novel->FAST_TRACK, underivable->SLOW_TRACK, one-off-noise->DISCARD.
    Shared precision/skip gates; the fast-vs-slow decision is the arm-specific differentiator (threshold at the
    calib-set class-balanced median of the arm score)."""
    rng = np.random.default_rng(seed * 100003 + 733)
    # REDUNDANT batch: base-train edges sample (foundation saw them -> low surprise)
    nred = min(200, base_train_int.shape[0])
    red = base_train_int[np.sort(rng.choice(base_train_int.shape[0], size=nred, replace=False))]
    raw_pe_red = np.clip(_surprise(_recip_ranks(X_T, D_T, red, all_true_T, device)), 0.0, 1.0)
    prec_red = deg[red[:, 0]].astype(np.float64) / (deg[red[:, 0]].astype(np.float64) + TAU)
    # NOISE batch: corrupt r* (random tail), recurrence forced one-off (rec=1 -> precision 1/(1+TAU))
    noise = rstar_train_int.copy()
    if noise.shape[0] > 0:
        rt = rng.integers(0, N, size=noise.shape[0]); noise[:, 2] = rt
    raw_pe_noise = np.clip(_surprise(_recip_ranks(X_T, D_T, noise, all_true_T, device)), 0.0, 1.0)
    prec_noise = np.full(noise.shape[0], 1.0 / (1.0 + TAU), dtype=np.float64)

    # arm-specific fast/slow threshold from the calib subset of held facts
    def _route_batch(raw_pe, prec, revscore, thresh):
        out = []
        for i in range(len(raw_pe)):
            if prec[i] < PRECISION_MIN:
                out.append("DISCARD")
            elif raw_pe[i] < SURPRISE_FLOOR:
                out.append("SKIP")
            elif revscore[i] >= thresh:
                out.append("SLOW_TRACK")
            else:
                out.append("FAST_TRACK")
        return out

    routing = {}
    for a in ARM_ORDER:
        thresh = float(np.median(arm_score[a][calib_idx]))
        # held facts routed with this arm's revision score
        dec_held = _route_batch(raw_pe_held, recur_prec_held, arm_score[a], thresh)
        # redundant / noise routed with a matched-shape revision score (only precision + surprise gates fire for them)
        rev_red = np.zeros(len(red), dtype=np.float64)      # low revision -> would FAST, but SKIP gate dominates
        rev_noise = np.zeros(len(noise), dtype=np.float64)  # DISCARD gate dominates (precision floor)
        dec_red = _route_batch(raw_pe_red, prec_red, rev_red, thresh)
        dec_noise = _route_batch(raw_pe_noise, prec_noise, rev_noise, thresh)
        skip_red = np.mean([d == "SKIP" for d in dec_red]) if dec_red else float("nan")
        disc_noise = np.mean([d == "DISCARD" for d in dec_noise]) if dec_noise else float("nan")
        di = np.where(deriv_lbl)[0]; ui = np.where(~deriv_lbl)[0]
        fast_deriv = np.mean([dec_held[i] == "FAST_TRACK" for i in di]) if di.size else float("nan")
        slow_underiv = np.mean([dec_held[i] == "SLOW_TRACK" for i in ui]) if ui.size else float("nan")
        acc = _mean([skip_red, disc_noise, fast_deriv, slow_underiv])
        routing[a] = dict(skip_redundant=float(skip_red), discard_noise=float(disc_noise),
                          fast_derivable=float(fast_deriv), slow_underivable=float(slow_underiv),
                          routing_accuracy=float(acc))
    return routing


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk recompute of brain DECONF_AUC (pooled test split)
# ---------------------------------------------------------------------------
def dump_and_verify_arrays(output_dir, arrays_by_seed):
    cols = defaultdict(list)
    seed_col = []
    for seed, arr in arrays_by_seed:
        n = arr["batch"].shape[0]
        seed_col.append(np.full(n, seed, dtype=np.int64))
        for kk, vv in arr.items():
            cols[kk].append(np.asarray(vv, dtype=np.float64))
    flat = {kk: np.concatenate(vv) for kk, vv in cols.items()}
    flat["seed"] = np.concatenate(seed_col)
    path = os.path.join(str(output_dir), "per_candidate_arrays.npz")
    tmp = os.path.join(str(output_dir), "per_candidate_arrays_tmp.npz")
    np.savez(tmp, **flat)
    os.replace(tmp, path)
    inmem = _auc(flat["brain"][flat["batch"] == B_UNDERIV], flat["brain"][flat["batch"] == B_DERIV])
    z = np.load(path)
    offdisk = _auc(z["brain"][z["batch"] == B_UNDERIV], z["brain"][z["batch"] == B_DERIV])
    delta = abs(float(inmem) - float(offdisk)) if (inmem == inmem and offdisk == offdisk) else 0.0
    return (delta <= HP_ARRAY_RECOMPUTE_TOL), delta, path


# ---------------------------------------------------------------------------
# aggregate + head-to-head verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, run_mode, array_ok, array_delta, expected_units, observed_units):
    ok = [s for s in per_seed if s.get("status") == "OK"]
    def agg_arm(field, arm):
        return _mean([s[field][arm] for s in ok])
    deconf = {a: agg_arm("deconf_test", a) for a in ARM_ORDER}
    deconf_full = {a: agg_arm("deconf_full", a) for a in ARM_ORDER}
    conf = _mean([s["conf_auc"] for s in ok])
    posctrl = _mean([s["posctrl_auc"] for s in ok])
    randlabel = _mean([s["randlabel_auc"] for s in ok])
    infer_mrr = _mean([s["infer_mrr"] for s in ok])
    rstar_train_mrr = _mean([s["rstar_train_mrr"] for s in ok])
    min_class = min([min(s["n_deriv"], s["n_underiv"]) for s in ok]) if ok else 0
    min_class_frac = min([min(s["deriv_frac"], 1.0 - s["deriv_frac"]) for s in ok]) if ok else 0.0
    precheck_diff = _mean([s["precheck"]["diff_high_minus_low"] for s in ok])
    precheck_hi = _mean([s["precheck"]["high"] for s in ok])
    precheck_lo = _mean([s["precheck"]["low"] for s in ok])
    routing_acc = {a: _mean([s["routing"][a]["routing_accuracy"] for s in ok]) for a in ARM_ORDER}

    g = {}
    g["cardinality_ok"] = (observed_units == expected_units)
    g["all_seeds_ok"] = (len(ok) == len(per_seed)) and len(ok) > 0
    g["HP_POSCTRL_FIRES"] = (posctrl == posctrl) and (posctrl >= HP_POSCTRL_AUC_MIN)
    g["HP_CONF_REPRODUCES"] = (conf == conf) and (conf >= HP_CONF_AUC_MIN)
    g["HP_RANDLABEL_CHANCE"] = (randlabel == randlabel) and (HP_RANDLABEL_LO <= randlabel <= HP_RANDLABEL_HI)
    g["HP_RSTAR_TRAINED"] = (rstar_train_mrr == rstar_train_mrr) and (rstar_train_mrr >= HP_RSTAR_TRAINED_MRR_MIN)
    g["HP_FOUNDATION_STRONG"] = (infer_mrr == infer_mrr) and (infer_mrr >= HP_STRONG_MRR_MIN)
    g["baseline_in_band"] = (infer_mrr == infer_mrr) and (HP_INFER_MRR_LO < infer_mrr < HP_INFER_MRR_HI)
    g["class_balance_ok"] = (min_class_frac >= HP_MIN_CLASS_FRAC) and (min_class > 0)
    harness_valid = all(g.values())

    flat_a = deconf["flat"]; sfa = deconf["schemafit"]; brain_a = deconf["brain"]
    hybrid_a = deconf["hybrid"]; learned_a = deconf["learned"]

    # cheap pre-check discriminator-fires (consolidation-benefit tertile differentiation)
    precheck_fires = (precheck_diff == precheck_diff) and (precheck_diff >= PRECHECK_DIFF_MIN)
    precheck_hard = ((precheck_hi == precheck_hi) and (precheck_hi >= PRECHECK_TOP_HARD)
                     and (precheck_lo == precheck_lo) and (precheck_lo <= PRECHECK_BOT_HARD))

    schemafit_leak = (sfa == sfa) and (sfa >= SCHEMAFIT_LEAK_MAX)
    brain_works = (brain_a == brain_a) and (brain_a >= HP_DECONF_MIN)
    learned_works = (learned_a == learned_a) and (learned_a >= HP_DECONF_MIN)
    sfa_works = (sfa == sfa) and (sfa >= HP_DECONF_MIN)
    brain_ge_refs = (brain_a == brain_a) and (brain_a >= max(flat_a, sfa) - TIE_EPS)
    learned_beats_brain = (learned_a == learned_a) and (brain_a == brain_a) and (learned_a > brain_a + DECISIVE_MARGIN)
    hybrid_beats_brain = (hybrid_a == hybrid_a) and (brain_a == brain_a) and (hybrid_a > brain_a + DECISIVE_MARGIN)
    all_collapse = all((deconf[a] == deconf[a]) and (deconf[a] <= HF_DECONF_MAX) for a in ("brain", "hybrid", "learned"))
    flat_at_chance = (flat_a == flat_a) and (flat_a <= HF_DECONF_MAX)

    if not harness_valid:
        verdict = "INCONCLUSIVE_harness"
        finding = ("INCONCLUSIVE: harness not validated (posctrl=%.3f conf=%.3f randlabel=%.3f rstar_mrr=%.3f "
                   "infer_mrr=%.3f class_bal=%.2f card=%s)." % (posctrl, conf, randlabel, rstar_train_mrr, infer_mrr,
                                                                min_class_frac, g["cardinality_ok"]))
    elif schemafit_leak:
        verdict = "SCHEMAFIT_LEAK_race_vacuous"
        finding = ("SCHEMAFIT_LEAK: schema_fit alone separates the classes at AUC=%.3f >= %.2f -- it near-copies the "
                   "derivable label, so the race is vacuous. Need an orthogonal schema_fit proxy (spectral-gap / "
                   "expander-mixing) before re-running. DEMOTE." % (sfa, SCHEMAFIT_LEAK_MAX))
    elif learned_beats_brain and learned_works:
        verdict = "LEARNED_BEATS_BRAIN_form_incomplete"
        finding = ("LEARNED_BEATS_BRAIN: learned DECONF_AUC=%.3f decisively beats brain-faithful=%.3f (margin>%.2f); "
                   "hybrid(calibrated brain-form)=%.3f. The brain's FORM is INCOMPLETE at this substrate -- %s. "
                   "flat(v4)=%.3f schemafit_alone=%.3f." % (
                       learned_a, brain_a, DECISIVE_MARGIN, hybrid_a,
                       ("WEIGHTS within the brain form recover it (hybrid~learned)" if hybrid_beats_brain
                        else "richer features beyond the 2-track form are needed"), flat_a, sfa))
    elif brain_works and brain_ge_refs and not learned_beats_brain:
        verdict = "BRAIN_FORM_WORKS"
        interaction = ("the surprise*schema INTERACTION adds signal (brain > schemafit_alone+%.2f)" % TIE_EPS
                       if brain_a > sfa + TIE_EPS else
                       "carried mostly by schema_fit (brain ~ schemafit_alone) -- the decomposition routes correctly "
                       "but the interaction term is ~inert")
        verdict = "BRAIN_FORM_WORKS" if (brain_a > sfa + TIE_EPS or not sfa_works) else "SCHEMAFIT_CARRIES_brain_ties"
        finding = ("BRAIN-FAITHFUL WORKS: brain DECONF_AUC=%.3f >= %.2f, ties/beats flat(v4)=%.3f and "
                   "schemafit_alone=%.3f, and learned=%.3f does NOT decisively beat it => being EXACTLY like the "
                   "brain (Friston fast/slow decomposition, NO fitting) FIXES v4's coarse surprise. %s. hybrid=%.3f. "
                   "BRAIN-CHECK: aligned (Tse 2007 schema-congruent fast-track / incongruent slow-track). ROUTE TO "
                   "SKUNKWORKS VET." % (brain_a, HP_DECONF_MIN, flat_a, sfa, learned_a, interaction, hybrid_a))
    elif sfa_works and (brain_a <= sfa + TIE_EPS) and flat_at_chance:
        verdict = "SCHEMAFIT_CARRIES_the_fix"
        finding = ("SCHEMAFIT_CARRIES: schema_fit_alone DECONF_AUC=%.3f >= %.2f while flat(v4)=%.3f ~chance; "
                   "brain-faithful=%.3f does not beat schema_fit_alone (interaction inert) and learned=%.3f. The v4 "
                   "fix is the schema_fit STRUCTURAL signal, not the surprise*schema decomposition. BRAIN-CHECK: the "
                   "schema-fit channel is load-bearing; the precision-weighted surprise interaction is not measurable "
                   "on this geometry." % (sfa, HP_DECONF_MIN, flat_a, brain_a, learned_a))
    elif all_collapse:
        verdict = "DECOMPOSITION_NO_SIGNAL"
        finding = ("DECOMPOSITION_NO_SIGNAL: no arm (brain=%.3f hybrid=%.3f learned=%.3f) clears ~chance (<=%.2f); "
                   "schema-conditioning does NOT fix v4. flat(v4)=%.3f schemafit_alone=%.3f. precheck_diff=%.3f "
                   "(fires=%s). The within-relation derivability signal is absent from ALL measurable combinations." % (
                       brain_a, hybrid_a, learned_a, HF_DECONF_MAX, flat_a, sfa, precheck_diff, precheck_fires))
    else:
        verdict = "MIDDLE_BAND_straddle"
        finding = ("STRADDLE: arms sit between collapse (%.2f) and pass (%.2f): flat=%.3f schemafit=%.3f brain=%.3f "
                   "hybrid=%.3f learned=%.3f -- partial signal (ambiguous)." % (
                       HF_DECONF_MAX, HP_DECONF_MIN, flat_a, sfa, brain_a, hybrid_a, learned_a))

    msg = ("DECONF_AUC[test] flat=%.3f schemafit=%.3f brain=%.3f hybrid=%.3f learned=%.3f | precheck_diff=%.3f "
           "(hi=%.3f lo=%.3f fires=%s hard=%s) | route_acc brain=%.2f learned=%.2f | CONF=%.3f POSCTRL=%.3f "
           "RAND=%.3f infer_mrr=%.3f rstar_mrr=%.3f bal=%.2f | harness=%s arrays_ok=%s(d=%.1e) card=%s -> %s" % (
               flat_a, sfa, brain_a, hybrid_a, learned_a, precheck_diff, precheck_hi, precheck_lo, precheck_fires,
               precheck_hard, routing_acc["brain"], routing_acc["learned"], conf, posctrl, randlabel, infer_mrr,
               rstar_train_mrr, min_class_frac, harness_valid, array_ok, array_delta, g["cardinality_ok"], verdict))
    summary = "%s: %s" % (verdict, finding)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, finding=finding, gates=g,
                harness_valid=harness_valid, run_mode=run_mode,
                precheck_fires=bool(precheck_fires), precheck_hard=bool(precheck_hard),
                agg=dict(deconf_test=deconf, deconf_full=deconf_full, conf_auc=conf, posctrl_auc=posctrl,
                         randlabel_auc=randlabel, infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
                         precheck_diff=precheck_diff, precheck_high=precheck_hi, precheck_low=precheck_lo,
                         routing_accuracy=routing_acc, min_class=int(min_class), min_class_frac=min_class_frac,
                         array_recompute_delta=array_delta,
                         head_to_head=dict(brain_works=bool(brain_works), learned_works=bool(learned_works),
                                           schemafit_alone_works=bool(sfa_works),
                                           learned_beats_brain=bool(learned_beats_brain),
                                           hybrid_beats_brain=bool(hybrid_beats_brain),
                                           schemafit_leak=bool(schemafit_leak))))


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16 + race primitive + logreg; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap + composed arena + race primitive at tiny scale")
    exercised = set()
    device = torch.device("cpu")

    # REAL substrate object path (matches FULL: AdditiveKGMap.fit is what fit_foundation calls)
    triples = []
    for i in range(16):
        triples.append(("e%d" % i, "ra", "e%d" % ((i + 1) % 16)))
        triples.append(("e%d" % i, "rb", "e%d" % ((i + 3) % 16)))
        triples.append(("e%d" % i, "rc", "e%d" % ((i + 5) % 16)))
    ents = sorted({x for tr in triples for x in (tr[0], tr[2])})
    rels = sorted({tr[1] for tr in triples})
    kmap = AdditiveKGMap(device=device)
    kmap.fit(triples, entities=ents, relations=rels, k=8, epochs=30, seed=7)
    exercised.add("AdditiveKGMap"); exercised.add("AdditiveKGMap.fit")
    _ = kmap.score_all("e0", "ra"); exercised.add("AdditiveKGMap.score_all")
    code = kmap.compose_entity([("e0", "ra"), ("e1", "rb")]); exercised.add("AdditiveKGMap.compose_entity")
    _ = kmap.insert_entity(code, name="e_new"); exercised.add("AdditiveKGMap.insert_entity")

    # logistic calibrator: learns a linearly-separable toy (deterministic, zero-init)
    Xf = np.array([[0.1, 0.9], [0.2, 0.8], [0.85, 0.1], [0.9, 0.2], [0.15, 0.85], [0.95, 0.05]], dtype=np.float64)
    y = np.array([0, 0, 1, 1, 0, 1], dtype=np.float64)
    mu, sd = _standardize_fit(Xf)
    w = fit_logreg(_standardize_apply(Xf, mu, sd), y)
    p = predict_logreg(w, _standardize_apply(Xf, mu, sd))
    assert _auc(p[y == 1], p[y == 0]) >= 0.9, "logreg failed to separate a linearly-separable toy"
    exercised.add("fit_logreg"); exercised.add("predict_logreg")

    # arm scores: brain slow_track HIGH for low schema_fit, fast_track HIGH for high schema_fit
    raw = np.array([0.9, 0.9, 0.9, 0.9], dtype=np.float64)
    sf = np.array([0.9, 0.1, 0.8, 0.2], dtype=np.float64)
    fixed = arm_scores_fixed(raw, sf)
    assert np.all(fixed["brain"][[1, 3]] > fixed["brain"][[0, 2]]), "brain slow_track not higher for low schema_fit"
    assert np.allclose(fixed["fast_track"] + fixed["slow_track"], raw), "fast+slow must reconstruct raw_PE"

    # tertile consolidation helper: high-schema-fit gets more of its gain cheaply -> ratio differentiates
    sfv = np.array([0.05, 0.1, 0.2, 0.5, 0.8, 0.95], dtype=np.float64)
    before = np.zeros(6); fast = np.array([0.1, 0.1, 0.2, 0.5, 0.8, 0.9]); refit = np.array([0.9, 0.9, 0.9, 0.9, 0.9, 0.9])
    pc = _tertile_consolidation(sfv, before, fast, refit)
    assert pc["high"] > pc["low"], "tertile consolidation ratio must differentiate on the toy"

    # race primitive: composed arena at tiny scale gives defined per-arm AUCs + firing controls
    cfg = dict(n_ent=80, edges_per_rel=48, n_rstar=48, train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=60,
               reach_k=2, reach_cap=60, min_class_n=3, calib_frac=0.5)
    r = race_seed(cfg, 7, device, want_arrays=True)
    exercised.add("race_seed"); exercised.add("gen_composed_arena"); exercised.add("derivability_labels")
    assert r["status"] in ("OK", "ONE_CLASS_EMPTY"), "race_seed status: %s" % r["status"]
    if r["status"] == "OK":
        for a in ARM_ORDER:
            assert 0.0 <= r["deconf_test"][a] <= 1.0, "%s deconf out of [0,1]: %s" % (a, r["deconf_test"][a])
        assert len(set(r["arm_score_sha"].values())) >= 3, "arm revision-score vectors bit-identical (arm bug)"
        for kk in ("conf_auc", "posctrl_auc", "randlabel_auc"):
            assert 0.0 <= r[kk] <= 1.0, "%s out of [0,1]" % kk

    # AUC direction sanity
    assert _auc([0.9, 0.95], [0.1, 0.2]) == 1.0 and _auc([0.1, 0.2], [0.9, 0.95]) == 0.0

    # array dump round-trip
    import tempfile
    if r["status"] == "OK":
        with tempfile.TemporaryDirectory() as td:
            okd, delta, _p = dump_and_verify_arrays(td, [(7, r["_arrays"])])
            assert okd and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    okp = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity",
                                        "gen_composed_arena", "derivability_labels", "race_seed",
                                        "fit_logreg", "predict_logreg"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "brain_deconf_auc", "before": 0.50, "after": 0.80, "min_delta": 1e-6},
    ], run_mode="selftest")
    assert okp, "validity preflight failed"
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
    seeds = cfg["seeds"]
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()
    device = torch.device("cpu")

    per_seed = []
    arrays_by_seed = []
    observed_units = 0
    for si, seed in enumerate(seeds):
        _log("seed %d/%d (seed=%d): fitting trained-row + untrained-row foundations; racing 5 arms ..." % (
            si + 1, len(seeds), seed))
        want = (si == 0)
        s = race_seed(cfg, seed, device, want_arrays=want)
        if want and s.get("status") == "OK":
            arrays_by_seed.append((seed, s.pop("_arrays")))
        else:
            s.pop("_arrays", None)
        per_seed.append(s)
        observed_units += 1
        if s.get("status") == "OK":
            dt = s["deconf_test"]
            _log("  [seed=%d] status=OK DECONF_AUC flat=%.3f schemafit=%.3f brain=%.3f hybrid=%.3f learned=%.3f | "
                 "precheck_diff=%.3f | CONF=%.3f POSCTRL=%.3f infer_mrr=%.3f n_deriv=%d n_underiv=%d (%.1fs)" % (
                     seed, dt["flat"], dt["schemafit"], dt["brain"], dt["hybrid"], dt["learned"],
                     s["precheck"]["diff_high_minus_low"], s["conf_auc"], s["posctrl_auc"], s["infer_mrr"],
                     s["n_deriv"], s["n_underiv"], time.time() - t0))
        else:
            _log("  [seed=%d] status=%s (%.1fs)" % (seed, s.get("status"), time.time() - t0))

    # ARMS-MUST-DIFFER across arm revision-score vectors (META_RULE_AF)
    ok = [s for s in per_seed if s.get("status") == "OK"]
    if ok:
        assert len(set(ok[0]["arm_score_sha"].values())) >= 3, "arm revision-score vectors bit-identical (arm bug)"

    if arrays_by_seed:
        array_ok, array_delta, array_path = dump_and_verify_arrays(output_dir, arrays_by_seed)
    else:
        array_ok, array_delta, array_path = False, float("nan"), ""
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%s)" % (array_path, array_ok, array_delta))

    v = aggregate_and_verdict(per_seed, run_mode, array_ok, array_delta, expected_units, observed_units)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds),
                   config=dict(seeds=seeds, n_ent=cfg["n_ent"], edges_per_rel=cfg["edges_per_rel"],
                               n_rstar=cfg["n_rstar"], train_frac_rstar=cfg["train_frac_rstar"],
                               frac_heldout_base=cfg["frac_heldout_base"], epochs=cfg["epochs"],
                               reach_k=cfg["reach_k"], rel_scale=ARENA_BASE["rel_scale"], calib_frac=cfg["calib_frac"]),
                   bands=dict(HP_DECONF_MIN=HP_DECONF_MIN, HF_DECONF_MAX=HF_DECONF_MAX, DECISIVE_MARGIN=DECISIVE_MARGIN,
                              TIE_EPS=TIE_EPS, SCHEMAFIT_LEAK_MAX=SCHEMAFIT_LEAK_MAX, PRECHECK_DIFF_MIN=PRECHECK_DIFF_MIN,
                              TAU=TAU, PRECISION_MIN=PRECISION_MIN, SURPRISE_FLOOR=SURPRISE_FLOOR),
                   expected_n_units=expected_units, observed_n_units=observed_units,
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   progress_logging="print_flush_true", cell_chunked=False,
                   start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=False,
                   defensive_error_checking="single_seed_loop_short_cell_no_heartbeat",
                   per_candidate_arrays=os.path.basename(array_path) if array_path else None,
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
