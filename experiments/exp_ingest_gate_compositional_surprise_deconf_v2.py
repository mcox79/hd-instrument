"""POWER-FIX + AUGMENT of ingest_gate_compositional_surprise_deconf_v1 (landed INCONCLUSIVE_harness, run_mode=full,
data/exp_ingest_gate_compositional_surprise_deconf_v1/metrics.json). ROOT CAUSE (verified on disk): v1's
_balance_mask (imported VERBATIM from the v4 file, unchanged here) caps the MAJORITY class to 1.5x the RAW MINORITY
class size but has NO FLOOR on the minority class itself -- and the minority class (empirically always
"underivable") is a naturally SMALL, HIGH-VARIANCE tail fraction of the ~210 held-out r* facts per seed (raw
minority counts observed: seed7=33, seed13=3(!), seed17=11). Averaging 3 per-seed AUCs computed on such tiny samples
made HP_RANDLABEL_CHANCE fail (randlabel_auc=0.366, not ~0.5) even though the arena/split itself was CORRECT
(GATE_D passed both sub-checks). THE FIX (power only, NOT a redesign): (1) scale up n_ent/edges_per_rel/n_rstar so
the raw per-seed heldout pool is ~2-2.5x larger, (2) add 4 more seeds (7 total), (3) POOL every seed's per-candidate
score+label arrays into ONE combined set and compute DECONF_AUC (and randlabel_auc, GATE_D, class-balance) on the
POOLED set with a bootstrap 95% CI -- this directly fixes the per-seed-tiny-N problem regardless of how skewed any
INDIVIDUAL seed's minority class happens to be, since seeds compensate for each other in the pool. The DEFINITION of
derivable/underivable, the 5 original arms, GATE_D, reach_k, rel_scale, TAU, and epochs are UNCHANGED from v1.

AUGMENT (Director synthesis 2026-07-16, notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md): the
existing `schemafit` arm is a NODE-AGGREGATE percentile (0.5*(reach_pct[h]+reach_pct[t])) that discards the specific
h-to-t pair relationship. Add ONE new arm, `schemafit_pairwise` (Tier A from that drill, near-zero build): the
Resource-Allocation link-prediction index RA(h,t) = sum_{z in N(h) & N(t)} 1/deg(z), computed on the SAME adj_found
graph the current schemafit already builds (RA.build_undirected_adj(base_train_int, N)), rank-percentiled the same
way (_rank_pct), surprise = 1 - rank_pct(RA). This lets the ONE powered run also answer: does a genuinely PAIR-
SPECIFIC schema-fit score beat the node-aggregate one? (Tier B / SRColumnSolver explicitly deferred per Director's
scope instruction -- Tier A only here.)

Also independently corroborates a parallel finding in that same note (Q3): the race cell's reported schemafit
0.719/0.836 headline is itself partly a small-sample artifact of equal-weighted per-seed averaging (seed13's n=8
AUC=1.000 drags the mean up over seed7's n=83 AUC=0.642-0.745). This cell's pooled/CI methodology applies the SAME
fix to schemafit (and schemafit_pairwise) as to comp_op -- ALL arms are scored under the identical pooled/n-weighted
scheme, so comp_op-vs-schemafit is apples-to-apples on the HONEST (de-inflated) baseline, not the old per-seed-mean.

DECISIVE QUESTION (unchanged from v1, now answered with power): does comp_op sit STATISTICALLY ABOVE add_flat
(non-overlapping 95% CI) AND CONVERGE with schemafit (CI overlap or |diff|<=CONVERGE_EPS) -> EXTRACTOR_ARTIFACT
confirmed; OR does it sit decisively above add_flat but NOT reach schemafit -> PARTIAL_RECOVERY (the "stay strictly
between" case); OR does it stay at/below chance even pooled -> SURPRISE_GENUINELY_INERT (race conclusion holds).
SEPARATELY (non-gating, auxiliary): does schemafit_pairwise decisively beat node-aggregate schemafit (CI non-overlap)?

REUSE (extend, don't rebuild; NO science redesign, ONLY power + one additive arm):
  - v4 (exp_ingest_gate_deconfound_within_relation_derivability_v1): gen_composed_arena, derivability_labels,
    _exact_path_labels, _balance_mask, _arena_cfg, ARENA_BASE -- UNCHANGED, imported verbatim.
  - v2 (exp_ingest_gate_strong_foundation_novelty_v2): fit_foundation, _to_int, _mean -- UNCHANGED.
  - v1-pilot (exp_ingest_gate_consolidation_loop_pilot_v1): _auc, _recip_ranks, _surprise, _sha, build_schema_fit,
    schema_fit_edges, _rank_pct -- UNCHANGED.
  - v1-compositional (exp_ingest_gate_compositional_surprise_deconf_v1): comp_op_surprise, comp_path_surprise --
    UNCHANGED (pure, parameter-free readouts off the fitted foundation).
  - NEW in this file: _ra_pairwise_batch (Tier-A RA pairwise index), comp_surprise_seed_v2 (v1's comp_surprise_seed
    body + the one new arm, duplicated not edited so the landed v1 file stays an immutable provenance record),
    pooled_auc_ci (bootstrap-CI pooled AUC), the pooled aggregation + CI-based verdict logic.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (6 arm score vectors hash-distinct on the held split)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: DECONF_AUC is a rank statistic over two measured score distributions; chance=0.5, self-checked by a
#   POOLED RANDLABEL must-fail control (large-N now, low-variance); no closed-form noise floor.
# - baseline_in_band: inferable held-out MRR 0.05<mrr<0.95 AND strong (>=HP_STRONG_MRR_MIN); r* MRR >= floor (trained)
# - discriminator survives scale: multi-seed smoke at reduced (but still multi-hundred-candidate) N demonstrates the
#   pooled minority-class floor gate fires (POOLED_MIN_CLASS_FLOOR); FULL scales it further.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (one arena race block per seed)
# - HARD_PASS strictly above chance-floor + band (HP_DECONF_MIN=0.65 vs chance 0.50) -- UNCHANGED from v1
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (see completion report, not inline here)
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16 AND
#   exercises gen_composed_arena + derivability_labels + comp_surprise_seed_v2 + _ra_pairwise_batch + pooled_auc_ci
#   + both compositional readouts at tiny scale
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); NO hash()-seeded RNG, no list(set()) order;
#   bootstrap RNG uses a FIXED integer seed (not derived from wall-clock or hash())
# - progress_logging = print_flush_true (every seed + arm logs, flush=True)
# - POWER-FIX new gate: HP_POOLED_MIN_CLASS (pooled minority-class raw count >= POOLED_MIN_CLASS_FLOOR) -- this is
#   the gate that DIRECTLY operationalizes "did the power fix work"; it is the harness-validity blocker being fixed.

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

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402
from hdlab import reachability_audit as RA  # noqa: E402
# REUSE v4 arena + derivability machinery (import does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_deconfound_within_relation_derivability_v1 import (  # noqa: E402
    gen_composed_arena, derivability_labels, _exact_path_labels, _balance_mask, _arena_cfg, ARENA_BASE,
)
# REUSE v2 fit + helpers
from experiments.exp_ingest_gate_strong_foundation_novelty_v2 import (  # noqa: E402
    fit_foundation, _to_int as _arena_to_int, _mean,
)
# REUSE v1-pilot metric + schema-fit machinery
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, build_schema_fit, schema_fit_edges, _rank_pct,
)
# REUSE v1-compositional readouts (pure, parameter-free; unchanged)
from experiments.exp_ingest_gate_compositional_surprise_deconf_v1 import (  # noqa: E402
    comp_op_surprise, comp_path_surprise,
)

ANCHOR_NAME = "ingest_gate_compositional_surprise_deconf_v2"

# ---- pre-registered bands (UNCHANGED science thresholds from v1; only the ESTIMATION METHOD changed to pooled+CI) --
HP_DECONF_MIN = 0.65          # a comp arm "carries the signal": separates underivable-vs-derivable (>chance+0.15)
HF_DECONF_MAX = 0.58          # an arm collapses to ~chance
DECISIVE_MARGIN = 0.10        # comp decisively beats additive-flat (POINT-ESTIMATE secondary check, kept for continuity)
CONVERGE_EPS = 0.07           # comp "converges with" schema-fit (point-estimate secondary check)

# harness-valid bands (reuse v1 verbatim)
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
# Gate-D positive control (reproduce the race's qualitative SCHEMAFIT_CARRIES at this scale) -- now POOLED
FLAT_REPRO_MAX = 0.60
SCHEMAFIT_GAP_MIN = 0.08

# NEW power-fix gate: the pooled minority-class raw count (across ALL seeds) must clear this floor. This is the
# gate that directly certifies the power-fix worked (root cause of v1's INCONCLUSIVE_harness).
POOLED_MIN_CLASS_FLOOR = 60

TAU = 3.0
COMP_PATH_TOPM = 5
N_BOOT = 2000                 # bootstrap resamples for the pooled 95% CI
BOOT_SEED = 20260716           # FIXED int seed (no hash()/wall-clock derivation; META_RULE F.5)

EPS_BAND = 1e-9
B_DERIV, B_UNDERIV = 0, 1
ARM_ORDER = ["add_flat", "schemafit", "schemafit_pairwise", "comp_op", "comp_path", "recur"]
COMP_ARMS = ["comp_op", "comp_path"]

# POWERED FULL config: n_ent/edges_per_rel/n_rstar scaled ~2.5x vs v1 (same ratios: edges_per_rel/n_ent=0.7,
# n_rstar/n_ent=0.6) + 7 seeds (original 3 + 4 new). reach_cap scaled proportionally (300/600=0.5 -> 750/1500=0.5).
# epochs UNCHANGED per contract. min_class_n is a DEAD parameter in the imported _balance_mask (verified on read:
# the function never uses its 3rd arg) -- kept scaled for API-cleanliness only, has zero effect on results.
FULL_CFG = dict(
    seeds=[7, 13, 17, 19, 23, 29, 31],
    n_ent=1500, edges_per_rel=1050, n_rstar=900,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=350,
    reach_k=2, reach_cap=750, min_class_n=60,
)
SMOKE_CFG = dict(
    seeds=[7, 13, 17],
    n_ent=750, edges_per_rel=525, n_rstar=450,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=175,
    reach_k=2, reach_cap=375, min_class_n=30,
)


# ---------------------------------------------------------------------------
# scaffolding
# ---------------------------------------------------------------------------
def _log(msg):
    print("[comp_surp_v2] %s" % msg, flush=True)


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


def _pearson(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size < 2:
        return float("nan")
    sa = a.std(); sb = b.std()
    if sa < 1e-12 or sb < 1e-12:
        return float("nan")
    return float(np.mean((a - a.mean()) * (b - b.mean())) / (sa * sb))


# ---------------------------------------------------------------------------
# NEW: Tier-A pairwise schema-fit (Resource-Allocation index); reuses adj_found verbatim.
# ---------------------------------------------------------------------------
def _ra_pairwise_batch(adj, degv, heads, tails):
    """RA(h,t) = sum_{z in N(h) & N(t)} 1/deg(z). adj: List[np.ndarray] from RA.build_undirected_adj. Returns (n,)."""
    n = heads.shape[0]
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        h = int(heads[i]); t = int(tails[i])
        nh = adj[h]; nt = adj[t]
        if nh.size == 0 or nt.size == 0:
            continue
        common = np.intersect1d(nh, nt, assume_unique=True)
        if common.size == 0:
            continue
        dz = degv[common].astype(np.float64)
        mask = dz > 0
        if not np.any(mask):
            continue
        out[i] = float(np.sum(1.0 / dz[mask]))
    return out


# ---------------------------------------------------------------------------
# LOAD-BEARING PRIMITIVE v2: v1's comp_surprise_seed body + the ONE new schemafit_pairwise arm.
# Duplicated (not imported+patched) so the landed v1 file remains an untouched provenance record.
# ---------------------------------------------------------------------------
def comp_surprise_seed_v2(cfg, seed, device, want_arrays=False):
    """SPLIT DERIVATION COPIED VERBATIM from v1 (== race_seed) so the derivable/underivable held set is IDENTICAL
    across v1/v2 at matched cfg. Computes 6 arm scores + their DECONF_AUC (full balanced held set) + harness
    controls + D[r*]-vs-D[r0]+D[r1] diagnostics + the new RA-pairwise diagnostics."""
    acfg = _arena_cfg(cfg["n_ent"], cfg["edges_per_rel"])
    N = acfg["n_ent"]; nR_base = acfg["n_base_rel"]
    rstar_idx = nR_base
    nR_total = nR_base + 1
    ra, rb = 0, 1

    Z, G, base_edges, rstar_edges, mid = gen_composed_arena(acfg, seed, rstar_idx, ra, rb, cfg["n_rstar"])
    rng = np.random.default_rng(seed * 100003 + 131)   # VERBATIM race_seed seed

    nb = len(base_edges)
    pb = rng.permutation(nb)
    nb_hold = int(round(cfg["frac_heldout_base"] * nb))
    hold_b = set(pb[:nb_hold].tolist())
    base_train = [base_edges[i] for i in range(nb) if i not in hold_b]
    base_heldout = [base_edges[i] for i in range(nb) if i in hold_b]

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

    adj_found = RA.build_undirected_adj(base_train_int, N)
    derivable = derivability_labels(rstar_heldout_int, adj_found, cfg["reach_k"])
    base_train_set = set((int(h), int(r), int(t)) for (h, r, t) in base_train)
    mid_of_head = {int(rstar_edges[i][0]): int(mid[i]) for i in range(nr)}
    derivable_exact = _exact_path_labels(rstar_heldout_int, mid_of_head, base_train_set, ra, rb)

    keep = _balance_mask(derivable, np.random.default_rng(seed * 100003 + 191), cfg["min_class_n"])  # VERBATIM
    if keep is None:
        return dict(seed=int(seed), status="ONE_CLASS_EMPTY", n_deriv=int(derivable.sum()),
                    n_underiv=int((~derivable).sum()))
    held_int = rstar_heldout_int[keep]
    deriv_lbl = derivable[keep]
    deriv_exact_lbl = derivable_exact[keep]
    n_deriv = int(deriv_lbl.sum()); n_underiv = int((~deriv_lbl).sum())

    # SCHEMA-FIT (node-aggregate reachability rank-percentile) -- the v1 reference arm
    reach_pct, reach_mass = build_schema_fit(base_train_int, N, cfg["reach_k"], cfg["reach_cap"])
    schema_fit_held = schema_fit_edges(held_int, reach_pct, np.zeros(held_int.shape[0], dtype=bool))
    schema_fit_held = np.clip(np.asarray(schema_fit_held, dtype=np.float64), 0.0, 1.0)

    # NEW: SCHEMA-FIT PAIRWISE (Resource-Allocation index; Tier A, Director 2026-07-16). Same adj_found, no leakage.
    deg = RA.degree_vector(adj_found)
    ra_raw = _ra_pairwise_batch(adj_found, deg, held_int[:, 0], held_int[:, 2])
    schema_fit_pair_held = 1.0 - _rank_pct(ra_raw)   # surprise convention: higher = more underivable

    # RECURRENCE -> graded local precision (deg(h)/(deg(h)+TAU)); the degree/frequency confound probe
    rec_held = deg[held_int[:, 0]].astype(np.float64)
    recur_held = rec_held / (rec_held + TAU)

    # FOUNDATION_T: r* row TRAINED (base_train + rstar_train) = the arena the race scored on
    train_T = base_train + rstar_train
    X_T, D_T, all_true_T = fit_foundation(acfg, seed, cfg["epochs"], train_T, N, nR_total, device)

    all_true_rstar = defaultdict(set)
    for h, r, t in train_T:
        if int(r) == rstar_idx:
            all_true_rstar[int(h)].add(int(t))

    # ---- ARM scores (all non-fitted; higher = more UNDERIVABLE = revision needed) ----
    add_flat = np.clip(_surprise(_recip_ranks(X_T, D_T, held_int, all_true_T, device)), 0.0, 1.0)
    sf_score = 1.0 - schema_fit_held
    sf_pair_score = np.clip(schema_fit_pair_held, 0.0, 1.0)
    comp_op = comp_op_surprise(X_T, D_T, held_int, ra, rb, all_true_rstar, device)
    comp_path = comp_path_surprise(X_T, D_T, held_int, ra, rb, all_true_T, device, COMP_PATH_TOPM)
    arm_score = dict(add_flat=add_flat, schemafit=sf_score, schemafit_pairwise=sf_pair_score,
                      comp_op=comp_op, comp_path=comp_path, recur=recur_held)

    def _arm_auc(score):
        pos = score[~deriv_lbl]      # underivable (should be HIGH)
        neg = score[deriv_lbl]       # derivable (should be LOW)
        return _auc(pos, neg)

    deconf = {a: _arm_auc(arm_score[a]) for a in ARM_ORDER}
    deconf_exact = {a: _auc(arm_score[a][~deriv_exact_lbl], arm_score[a][deriv_exact_lbl]) for a in ARM_ORDER}

    surp_infer_T = _surprise(_recip_ranks(X_T, D_T, base_heldout_int, all_true_T, device))
    infer_mrr = float(np.mean(1.0 - surp_infer_T)) if surp_infer_T.size else float("nan")
    surp_rtrain_T = _surprise(_recip_ranks(X_T, D_T, rstar_train_int, all_true_T, device))
    rstar_train_mrr = float(np.mean(1.0 - surp_rtrain_T)) if surp_rtrain_T.size else float("nan")

    corrupt = rstar_train_int.copy()
    if corrupt.shape[0] > 0:
        rand_t = rng.integers(0, N, size=corrupt.shape[0])
        for i in range(corrupt.shape[0]):
            if int(rand_t[i]) == int(corrupt[i, 2]):
                rand_t[i] = (int(rand_t[i]) + 1) % N
        corrupt[:, 2] = rand_t
    surp_corrupt = _surprise(_recip_ranks(X_T, D_T, corrupt, all_true_T, device))
    posctrl_auc = _auc(surp_corrupt, surp_rtrain_T)

    X_U, D_U, all_true_U = fit_foundation(acfg, seed, cfg["epochs"], base_train, N, nR_total, device)
    all_rstar_int = _arena_to_int(rstar_edges)
    surp_conf_novel = _surprise(_recip_ranks(X_U, D_U, all_rstar_int, all_true_U, device))
    surp_conf_infer = _surprise(_recip_ranks(X_U, D_U, base_heldout_int, all_true_U, device))
    conf_auc = _auc(surp_conf_novel, surp_conf_infer)

    d_star = D_T[rstar_idx]; d_comp = D_T[ra] + D_T[rb]
    cos_star_comp = float(torch.nn.functional.cosine_similarity(d_star.unsqueeze(0), d_comp.unsqueeze(0)).item())
    corr_comp_flat = _pearson(comp_op, add_flat)
    corr_comp_sf = _pearson(comp_op, sf_score)
    corr_sfpair_sf = _pearson(sf_pair_score, sf_score)

    out = dict(
        seed=int(seed), status="OK", N=int(N), n_deriv=n_deriv, n_underiv=n_underiv,
        deriv_frac=float(deriv_lbl.mean()) if deriv_lbl.size else float("nan"),
        deconf=deconf, deconf_exact=deconf_exact,
        conf_auc=conf_auc, posctrl_auc=posctrl_auc,
        infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
        cos_dstar_dcomp=cos_star_comp, corr_comp_flat=corr_comp_flat, corr_comp_schemafit=corr_comp_sf,
        corr_sfpair_schemafit=corr_sfpair_sf,
        recurrence_form="graded_deg_over_deg_plus_tau_TAU_%.1f" % TAU,
        arm_score_sha={a: _sha(arm_score[a]) for a in ARM_ORDER},
    )
    if want_arrays:
        out["_arrays"] = dict(
            batch=(~deriv_lbl).astype(np.int64),   # 0=deriv,1=underiv on the full balanced held set
            add_flat=add_flat, schemafit=sf_score, schemafit_pairwise=sf_pair_score,
            comp_op=comp_op, comp_path=comp_path, recur=recur_held,
            deriv_label=deriv_lbl.astype(np.int64),
        )
    return out


# ---------------------------------------------------------------------------
# POOLING + bootstrap-CI (the power fix's core statistic)
# ---------------------------------------------------------------------------
def pooled_auc_ci(scores, is_underiv, n_boot=N_BOOT, seed=BOOT_SEED):
    """Pooled AUC(underivable vs derivable) + a 95% bootstrap CI (resample within each class, fixed int seed)."""
    scores = np.asarray(scores, dtype=np.float64)
    is_underiv = np.asarray(is_underiv, dtype=bool)
    pos = scores[is_underiv]; neg = scores[~is_underiv]
    point = _auc(pos, neg)
    n_pos, n_neg = pos.size, neg.size
    if n_pos == 0 or n_neg == 0 or point != point:
        return dict(point=point, lo=float("nan"), hi=float("nan"), n_pos=int(n_pos), n_neg=int(n_neg))
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        pi = rng.integers(0, n_pos, size=n_pos)
        ni = rng.integers(0, n_neg, size=n_neg)
        boots[b] = _auc(pos[pi], neg[ni])
    lo, hi = (float(x) for x in np.percentile(boots, [2.5, 97.5]))
    return dict(point=float(point), lo=lo, hi=hi, n_pos=int(n_pos), n_neg=int(n_neg))


def ci_decisively_above(a, b):
    """a decisively ABOVE b: a's CI lower bound clears b's CI upper bound (non-overlapping, a>b side)."""
    if any(x != x for x in (a["lo"], b["hi"])):
        return False
    return a["lo"] > b["hi"]


def ci_overlap_or_close(a, b, eps):
    """a 'converges with' b: point estimates within eps, OR the two 95% CIs overlap."""
    if a["point"] == a["point"] and b["point"] == b["point"] and abs(a["point"] - b["point"]) <= eps:
        return True
    if any(x != x for x in (a["lo"], a["hi"], b["lo"], b["hi"])):
        return False
    return not (a["hi"] < b["lo"] or b["hi"] < a["lo"])


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk recompute of comp_op pooled DECONF_AUC
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
    inmem = _auc(flat["comp_op"][flat["batch"] == B_UNDERIV], flat["comp_op"][flat["batch"] == B_DERIV])
    z = np.load(path)
    offdisk = _auc(z["comp_op"][z["batch"] == B_UNDERIV], z["comp_op"][z["batch"] == B_DERIV])
    delta = abs(float(inmem) - float(offdisk)) if (inmem == inmem and offdisk == offdisk) else 0.0
    return (delta <= HP_ARRAY_RECOMPUTE_TOL), delta, path, flat


# ---------------------------------------------------------------------------
# aggregate + POOLED head-to-head verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict_pooled(per_seed, pooled_flat, run_mode, array_ok, array_delta, expected_units,
                                  observed_units):
    ok = [s for s in per_seed if s.get("status") == "OK"]

    conf = _mean([s["conf_auc"] for s in ok])
    posctrl = _mean([s["posctrl_auc"] for s in ok])
    infer_mrr = _mean([s["infer_mrr"] for s in ok])
    rstar_train_mrr = _mean([s["rstar_train_mrr"] for s in ok])
    cos_dstar_dcomp = _mean([s["cos_dstar_dcomp"] for s in ok])
    corr_comp_flat = _mean([s["corr_comp_flat"] for s in ok])
    corr_comp_sf = _mean([s["corr_comp_schemafit"] for s in ok])
    corr_sfpair_sf = _mean([s["corr_sfpair_schemafit"] for s in ok])

    batch = pooled_flat["batch"].astype(bool)     # True = UNDERIVABLE
    pooled_n_underiv = int(batch.sum()); pooled_n_deriv = int((~batch).sum())
    pooled_total = pooled_n_underiv + pooled_n_deriv
    pooled_min_class = min(pooled_n_underiv, pooled_n_deriv)
    pooled_min_class_frac = (pooled_min_class / pooled_total) if pooled_total else 0.0

    pooled = {a: pooled_auc_ci(pooled_flat[a], batch) for a in ARM_ORDER}

    # RECUR DIAGNOSIS (Director-requested, non-gating): recur = deg(h)/(deg(h)+TAU) scored in the surprise convention
    # (higher = MORE underivable). But degree is structurally HIGHER for DERIVABLE facts (a high-degree head reaches
    # more tails within reach_k -> more likely derivable), so the arm's fixed orientation yields a BELOW-chance AUC.
    # This is a SIGN/ORIENTATION artifact riding on a DEGREE CONFOUND (they are the same thing here: recur == raw
    # degree, which POSITIVELY correlates with derivability in this arena). recur_flipped = the honest magnitude of
    # how well degree PREDICTS DERIVABILITY (deriv-vs-underiv orientation). NOT a redesign; just the sign-corrected #.
    recur_flip_point = _auc(pooled_flat["recur"][~batch], pooled_flat["recur"][batch])   # deriv vs underiv = 1 - recur
    corr_recur_deriv = _pearson(pooled_flat["recur"], (~batch).astype(np.float64))       # +ve => degree ~ derivable
    recur_flipped = dict(point=float(recur_flip_point),
                         lo=(1.0 - pooled["recur"]["hi"]) if pooled["recur"]["hi"] == pooled["recur"]["hi"] else float("nan"),
                         hi=(1.0 - pooled["recur"]["lo"]) if pooled["recur"]["lo"] == pooled["recur"]["lo"] else float("nan"),
                         corr_recur_derivable=float(corr_recur_deriv),
                         root_cause="sign_orientation_riding_on_degree_confound_recur_eq_degree_correlates_POSITIVELY_with_derivability")

    # POOLED RANDLABEL: shuffle the pooled comp_op scores against a random relabeling (fixed seed), CI via the
    # same bootstrap machinery on the shuffled assignment (checks the null distribution is centered ~0.5).
    rlrng = np.random.default_rng(BOOT_SEED + 7)
    shuf_batch = batch.copy()
    rlrng.shuffle(shuf_batch)
    randlabel = pooled_auc_ci(pooled_flat["comp_op"], shuf_batch)

    g = {}
    g["cardinality_ok"] = (observed_units == expected_units)
    g["all_seeds_ok"] = (len(ok) == len(per_seed)) and len(ok) > 0
    g["HP_POSCTRL_FIRES"] = (posctrl == posctrl) and (posctrl >= HP_POSCTRL_AUC_MIN)
    g["HP_CONF_REPRODUCES"] = (conf == conf) and (conf >= HP_CONF_AUC_MIN)
    g["HP_RANDLABEL_CHANCE"] = (randlabel["point"] == randlabel["point"]) and (
        HP_RANDLABEL_LO <= randlabel["point"] <= HP_RANDLABEL_HI)
    g["HP_RSTAR_TRAINED"] = (rstar_train_mrr == rstar_train_mrr) and (rstar_train_mrr >= HP_RSTAR_TRAINED_MRR_MIN)
    g["HP_FOUNDATION_STRONG"] = (infer_mrr == infer_mrr) and (infer_mrr >= HP_STRONG_MRR_MIN)
    g["baseline_in_band"] = (infer_mrr == infer_mrr) and (HP_INFER_MRR_LO < infer_mrr < HP_INFER_MRR_HI)
    g["class_balance_ok"] = (pooled_min_class_frac >= HP_MIN_CLASS_FRAC) and (pooled_min_class > 0)
    g["HP_POOLED_MIN_CLASS"] = pooled_min_class >= POOLED_MIN_CLASS_FLOOR   # NEW power-fix gate
    flat_a = pooled["add_flat"]["point"]; sfa = pooled["schemafit"]["point"]
    g["GATE_D_FLAT_INERT"] = (flat_a == flat_a) and (flat_a <= FLAT_REPRO_MAX)
    g["GATE_D_SCHEMAFIT_CARRIES"] = (sfa == sfa) and (flat_a == flat_a) and (sfa >= flat_a + SCHEMAFIT_GAP_MIN)
    harness_valid = all(g.values())

    comp_op_p = pooled["comp_op"]; comp_path_p = pooled["comp_path"]; recur_p = pooled["recur"]
    sfpair_p = pooled["schemafit_pairwise"]; sf_p = pooled["schemafit"]; flat_p = pooled["add_flat"]
    best_comp_name = "comp_op" if (comp_op_p["point"] >= (comp_path_p["point"] if comp_path_p["point"] == comp_path_p["point"] else -1)) else "comp_path"
    best_comp = pooled[best_comp_name]

    comp_op_works = (comp_op_p["point"] == comp_op_p["point"]) and (comp_op_p["point"] >= HP_DECONF_MIN)
    comp_path_works = (comp_path_p["point"] == comp_path_p["point"]) and (comp_path_p["point"] >= HP_DECONF_MIN)
    both_comp_chance = (comp_op_p["point"] <= HF_DECONF_MAX) and (comp_path_p["point"] <= HF_DECONF_MAX)

    # CI-based decisiveness (PRIMARY, this is the whole point of the power fix) + point-margin (secondary/legacy)
    comp_beats_flat_ci = ci_decisively_above(best_comp, flat_p)
    comp_beats_flat_point = (best_comp["point"] >= flat_p["point"] + DECISIVE_MARGIN) if (
        best_comp["point"] == best_comp["point"] and flat_p["point"] == flat_p["point"]) else False
    converges_sf_ci = ci_overlap_or_close(best_comp, sf_p, CONVERGE_EPS)

    # auxiliary (non-gating): pairwise vs node-aggregate schema-fit
    sfpair_beats_sf_ci = ci_decisively_above(sfpair_p, sf_p)
    sf_beats_sfpair_ci = ci_decisively_above(sf_p, sfpair_p)
    if sfpair_beats_sf_ci:
        sfpair_verdict = "PAIRWISE_BEATS_NODE_AGGREGATE"
    elif sf_beats_sfpair_ci:
        sfpair_verdict = "NODE_AGGREGATE_BEATS_PAIRWISE"
    else:
        sfpair_verdict = "NO_DECISIVE_DIFFERENCE"

    if not harness_valid:
        verdict = "INCONCLUSIVE_harness"
        finding = ("INCONCLUSIVE: harness/positive-control not validated (posctrl=%.3f conf=%.3f "
                   "randlabel=%.3f[CI %.3f-%.3f] rstar_mrr=%.3f infer_mrr=%.3f class_bal=%.2f pooled_min_class=%d "
                   "(floor=%d) card=%s GATE_D_flat_inert=%s[%.3f] GATE_D_sf_carries=%s[flat=%.3f sf=%.3f]). If "
                   "GATE_D failed, the split diverged from the race and the compositional arm is on the wrong "
                   "arena." % (
                       posctrl, conf, randlabel["point"], randlabel["lo"], randlabel["hi"], rstar_train_mrr,
                       infer_mrr, pooled_min_class_frac, pooled_min_class, POOLED_MIN_CLASS_FLOOR,
                       g["cardinality_ok"], g["GATE_D_FLAT_INERT"], flat_a, g["GATE_D_SCHEMAFIT_CARRIES"], flat_a, sfa))
    elif comp_beats_flat_ci and converges_sf_ci:
        verdict = "EXTRACTOR_ARTIFACT_comp_carries_CONFIRMED"
        finding = ("EXTRACTOR_ARTIFACT (POWERED+CONFIRMED): %s pooled DECONF_AUC=%.3f [CI %.3f-%.3f] is "
                   "STATISTICALLY ABOVE add_flat=%.3f [CI %.3f-%.3f] (non-overlapping 95%% CIs) AND CONVERGES with "
                   "schemafit=%.3f [CI %.3f-%.3f]. The 'surprise inert' v1-race finding was an ARTIFACT of the "
                   "additive-DIRECT extractor; a compositional surprise recovers the full signal. schemafit_pairwise="
                   "%.3f [CI %.3f-%.3f] (%s). ROUTE TO SKUNKWORKS VET." % (
                       best_comp_name, best_comp["point"], best_comp["lo"], best_comp["hi"], flat_p["point"],
                       flat_p["lo"], flat_p["hi"], sf_p["point"], sf_p["lo"], sf_p["hi"], sfpair_p["point"],
                       sfpair_p["lo"], sfpair_p["hi"], sfpair_verdict))
    elif comp_beats_flat_ci and not converges_sf_ci:
        verdict = "PARTIAL_RECOVERY_comp_above_flat_below_schemafit"
        finding = ("PARTIAL_RECOVERY (POWERED): %s pooled DECONF_AUC=%.3f [CI %.3f-%.3f] is STATISTICALLY ABOVE "
                   "add_flat=%.3f [CI %.3f-%.3f] but does NOT converge with schemafit=%.3f [CI %.3f-%.3f] (CIs "
                   "non-overlapping, gap %.3f > CONVERGE_EPS=%.2f). A compositional surprise recovers PART of the "
                   "signal the additive-direct extractor missed; schema-fit-direct remains the strongest single "
                   "arm. schemafit_pairwise=%.3f [CI %.3f-%.3f] (%s)." % (
                       best_comp_name, best_comp["point"], best_comp["lo"], best_comp["hi"], flat_p["point"],
                       flat_p["lo"], flat_p["hi"], sf_p["point"], sf_p["lo"], sf_p["hi"],
                       abs(best_comp["point"] - sf_p["point"]), CONVERGE_EPS, sfpair_p["point"], sfpair_p["lo"],
                       sfpair_p["hi"], sfpair_verdict))
    elif both_comp_chance:
        verdict = "SURPRISE_GENUINELY_INERT"
        finding = ("SURPRISE_GENUINELY_INERT (POWERED): even a COMPOSITIONAL, POOLED surprise stays ~chance "
                   "(comp_op=%.3f [CI %.3f-%.3f] comp_path=%.3f [CI %.3f-%.3f], both <= %.2f) while "
                   "add_flat=%.3f schemafit=%.3f. Surprise is genuinely inert for within-relation derivability here; "
                   "schema-fit-DIRECT stands (race conclusion holds, now confirmed at power). schemafit_pairwise="
                   "%.3f [CI %.3f-%.3f] (%s)." % (
                       comp_op_p["point"], comp_op_p["lo"], comp_op_p["hi"], comp_path_p["point"], comp_path_p["lo"],
                       comp_path_p["hi"], HF_DECONF_MAX, flat_p["point"], sf_p["point"], sfpair_p["point"],
                       sfpair_p["lo"], sfpair_p["hi"], sfpair_verdict))
    else:
        verdict = "MIDDLE_BAND_partial"
        finding = ("MIDDLE_BAND (POWERED): pooled compositional surprise straddles chance..pass without a decisive "
                   "CI call vs add_flat (comp_op=%.3f [CI %.3f-%.3f] comp_path=%.3f [CI %.3f-%.3f]) vs "
                   "add_flat=%.3f schemafit=%.3f -- ambiguous even pooled. comp_beats_flat_ci=%s "
                   "comp_beats_flat_point=%s. schemafit_pairwise=%.3f (%s)." % (
                       comp_op_p["point"], comp_op_p["lo"], comp_op_p["hi"], comp_path_p["point"], comp_path_p["lo"],
                       comp_path_p["hi"], flat_p["point"], sf_p["point"], comp_beats_flat_ci, comp_beats_flat_point,
                       sfpair_p["point"], sfpair_verdict))

    msg = ("POOLED_DECONF add_flat=%.3f[%.3f,%.3f] schemafit=%.3f[%.3f,%.3f] schemafit_pairwise=%.3f[%.3f,%.3f] "
           "comp_op=%.3f[%.3f,%.3f] comp_path=%.3f[%.3f,%.3f] recur=%.3f[%.3f,%.3f] | comp_beats_flat_ci=%s "
           "comp_beats_flat_point=%s converges_sf_ci=%s sfpair_verdict=%s | CONF=%.3f POSCTRL=%.3f "
           "RANDLABEL=%.3f[%.3f,%.3f] infer_mrr=%.3f rstar_mrr=%.3f pooled_min_class=%d/%d(floor=%d) | "
           "GATE_D[flat_inert=%s sf_carries=%s] harness=%s arrays_ok=%s(d=%.1e) card=%s -> %s" % (
               flat_p["point"], flat_p["lo"], flat_p["hi"], sf_p["point"], sf_p["lo"], sf_p["hi"], sfpair_p["point"],
               sfpair_p["lo"], sfpair_p["hi"], comp_op_p["point"], comp_op_p["lo"], comp_op_p["hi"],
               comp_path_p["point"], comp_path_p["lo"], comp_path_p["hi"], recur_p["point"], recur_p["lo"],
               recur_p["hi"], comp_beats_flat_ci, comp_beats_flat_point, converges_sf_ci, sfpair_verdict, conf,
               posctrl, randlabel["point"], randlabel["lo"], randlabel["hi"], infer_mrr, rstar_train_mrr,
               pooled_min_class, pooled_total, POOLED_MIN_CLASS_FLOOR, g["GATE_D_FLAT_INERT"],
               g["GATE_D_SCHEMAFIT_CARRIES"], harness_valid, array_ok, array_delta, g["cardinality_ok"], verdict))
    summary = "%s: %s" % (verdict, finding)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, finding=finding, gates=g,
                harness_valid=harness_valid, run_mode=run_mode,
                agg=dict(pooled_deconf={a: pooled[a] for a in ARM_ORDER}, recur_flipped=recur_flipped,
                         conf_auc=conf, posctrl_auc=posctrl,
                         randlabel=randlabel, infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
                         cos_dstar_dcomp=cos_dstar_dcomp, corr_comp_flat=corr_comp_flat,
                         corr_comp_schemafit=corr_comp_sf, corr_sfpair_schemafit=corr_sfpair_sf,
                         pooled_n_deriv=pooled_n_deriv, pooled_n_underiv=pooled_n_underiv,
                         pooled_min_class=pooled_min_class, pooled_min_class_frac=pooled_min_class_frac,
                         array_recompute_delta=array_delta,
                         head_to_head=dict(comp_op_works=bool(comp_op_works), comp_path_works=bool(comp_path_works),
                                           comp_beats_flat_ci=bool(comp_beats_flat_ci),
                                           comp_beats_flat_point=bool(comp_beats_flat_point),
                                           both_comp_chance=bool(both_comp_chance),
                                           converges_schemafit_ci=bool(converges_sf_ci),
                                           best_comp=best_comp["point"], best_comp_name=best_comp_name,
                                           sfpair_verdict=sfpair_verdict)))


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16 + compositional readouts + pooling; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap + composed arena + pooled compositional readouts at tiny scale")
    exercised = set()
    device = torch.device("cpu")

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

    X = kmap.X; D = kmap.D
    held = np.array([[0, 0, 3], [1, 1, 5], [2, 0, 7]], dtype=np.int64)
    all_true_rstar = defaultdict(set)
    co = comp_op_surprise(X, D, held, 0, 1, all_true_rstar, device)
    exercised.add("comp_op_surprise")
    assert co.shape[0] == 3 and np.all((co >= 0.0) & (co <= 1.0)), "comp_op surprise out of [0,1]"
    all_true_T = defaultdict(set)
    tri_int = np.array([[ents.index(h), rels.index(r), ents.index(t)] for h, r, t in triples], dtype=np.int64)
    for h, r, t in tri_int:
        all_true_T[(int(h), int(r))].add(int(t))
    cp = comp_path_surprise(X, D, held, 0, 1, all_true_T, device, 3)
    exercised.add("comp_path_surprise")
    assert cp.shape[0] == 3 and np.all((cp >= 0.0) & (cp <= 1.0)), "comp_path surprise out of [0,1]"

    # NEW: RA pairwise batch sanity
    adj_tiny = RA.build_undirected_adj(tri_int, 16)
    degv_tiny = RA.degree_vector(adj_tiny)
    ra_raw = _ra_pairwise_batch(adj_tiny, degv_tiny, held[:, 0], held[:, 2])
    exercised.add("_ra_pairwise_batch")
    assert ra_raw.shape[0] == 3 and np.all(ra_raw >= 0.0), "RA pairwise scores must be >= 0"
    rp = _rank_pct(ra_raw)
    assert rp.shape[0] == 3 and np.all((rp >= 0.0) & (rp <= 1.0)), "rank_pct out of [0,1]"

    assert _auc([0.9, 0.95], [0.1, 0.2]) == 1.0 and _auc([0.1, 0.2], [0.9, 0.95]) == 0.0

    # pooled_auc_ci sanity: perfect separation -> point=1.0, CI tight near 1.0
    pac = pooled_auc_ci(np.array([0.9, 0.95, 0.92, 0.1, 0.2, 0.15]), np.array([True, True, True, False, False, False]))
    exercised.add("pooled_auc_ci")
    assert abs(pac["point"] - 1.0) < 1e-9 and pac["lo"] > 0.5, "pooled_auc_ci perfect-separation sanity failed: %s" % pac
    # ci_decisively_above / ci_overlap_or_close sanity
    a_hi = dict(point=0.9, lo=0.85, hi=0.95); b_lo = dict(point=0.5, lo=0.4, hi=0.6)
    assert ci_decisively_above(a_hi, b_lo) is True
    assert ci_overlap_or_close(a_hi, dict(point=0.88, lo=0.8, hi=0.96), CONVERGE_EPS) is True
    exercised.add("ci_decisively_above"); exercised.add("ci_overlap_or_close")

    # full seed primitive at tiny scale: composed arena gives defined per-arm AUCs + firing controls + distinct arms
    cfg = dict(n_ent=80, edges_per_rel=48, n_rstar=48, train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=60,
               reach_k=2, reach_cap=60, min_class_n=3)
    r = comp_surprise_seed_v2(cfg, 7, device, want_arrays=True)
    exercised.add("comp_surprise_seed_v2"); exercised.add("gen_composed_arena"); exercised.add("derivability_labels")
    assert r["status"] in ("OK", "ONE_CLASS_EMPTY"), "comp_surprise_seed_v2 status: %s" % r["status"]
    if r["status"] == "OK":
        for a in ARM_ORDER:
            assert 0.0 <= r["deconf"][a] <= 1.0, "%s deconf out of [0,1]: %s" % (a, r["deconf"][a])
        assert len(set(r["arm_score_sha"].values())) >= 5, "arm score vectors not distinct (arm bug)"
        for kk in ("conf_auc", "posctrl_auc"):
            assert 0.0 <= r[kk] <= 1.0, "%s out of [0,1]" % kk
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            okd, delta, _p, _flat = dump_and_verify_arrays(td, [(7, r["_arrays"])])
            assert okd and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    okp = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity",
                                        "gen_composed_arena", "derivability_labels", "comp_surprise_seed_v2",
                                        "comp_op_surprise", "comp_path_surprise", "_ra_pairwise_batch",
                                        "pooled_auc_ci", "ci_decisively_above", "ci_overlap_or_close"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "comp_op_pooled_deconf_auc", "before": 0.50, "after": 0.80,
         "min_delta": 1e-6},
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
        _log("seed %d/%d (seed=%d): fitting trained-row + untrained-row foundations; scoring 6 arms ..." % (
            si + 1, len(seeds), seed))
        s = comp_surprise_seed_v2(cfg, seed, device, want_arrays=True)   # ALWAYS want_arrays: pooling needs every seed
        if s.get("status") == "OK":
            arrays_by_seed.append((seed, s.pop("_arrays")))
        else:
            s.pop("_arrays", None)
        per_seed.append(s)
        observed_units += 1
        if s.get("status") == "OK":
            dc = s["deconf"]
            _log("  [seed=%d] status=OK DECONF add_flat=%.3f schemafit=%.3f sf_pair=%.3f comp_op=%.3f "
                 "comp_path=%.3f recur=%.3f | n_deriv=%d n_underiv=%d CONF=%.3f POSCTRL=%.3f infer_mrr=%.3f "
                 "(%.1fs elapsed)" % (
                     seed, dc["add_flat"], dc["schemafit"], dc["schemafit_pairwise"], dc["comp_op"], dc["comp_path"],
                     dc["recur"], s["n_deriv"], s["n_underiv"], s["conf_auc"], s["posctrl_auc"], s["infer_mrr"],
                     time.time() - t0))
        else:
            _log("  [seed=%d] status=%s (%.1fs elapsed)" % (seed, s.get("status"), time.time() - t0))

    ok = [s for s in per_seed if s.get("status") == "OK"]
    if ok:
        assert len(set(ok[0]["arm_score_sha"].values())) >= 5, "arm score vectors not distinct (arm bug)"

    if arrays_by_seed:
        array_ok, array_delta, array_path, pooled_flat = dump_and_verify_arrays(output_dir, arrays_by_seed)
    else:
        array_ok, array_delta, array_path, pooled_flat = False, float("nan"), "", None
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%s pooled_N=%s)" % (
        array_path, array_ok, array_delta, pooled_flat["batch"].shape[0] if pooled_flat is not None else "NONE"))

    if pooled_flat is None:
        v = dict(verdict="CELL_CRASHED", verdict_msg="no seeds produced arrays; cannot pool", gates={},
                  harness_valid=False, run_mode=run_mode,
                  agg=dict(pooled_deconf={}, conf_auc=float("nan"), posctrl_auc=float("nan"),
                           randlabel=dict(point=float("nan"), lo=float("nan"), hi=float("nan")),
                           infer_mrr=float("nan"), rstar_train_mrr=float("nan")))
    else:
        v = aggregate_and_verdict_pooled(per_seed, pooled_flat, run_mode, array_ok, array_delta, expected_units,
                                         observed_units)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds),
                   config=dict(seeds=seeds, n_ent=cfg["n_ent"], edges_per_rel=cfg["edges_per_rel"],
                               n_rstar=cfg["n_rstar"], train_frac_rstar=cfg["train_frac_rstar"],
                               frac_heldout_base=cfg["frac_heldout_base"], epochs=cfg["epochs"],
                               reach_k=cfg["reach_k"], rel_scale=ARENA_BASE["rel_scale"],
                               comp_path_topM=COMP_PATH_TOPM, TAU=TAU, n_boot=N_BOOT,
                               pooled_min_class_floor=POOLED_MIN_CLASS_FLOOR),
                   bands=dict(HP_DECONF_MIN=HP_DECONF_MIN, HF_DECONF_MAX=HF_DECONF_MAX, DECISIVE_MARGIN=DECISIVE_MARGIN,
                              CONVERGE_EPS=CONVERGE_EPS, FLAT_REPRO_MAX=FLAT_REPRO_MAX,
                              SCHEMAFIT_GAP_MIN=SCHEMAFIT_GAP_MIN, POOLED_MIN_CLASS_FLOOR=POOLED_MIN_CLASS_FLOOR),
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
