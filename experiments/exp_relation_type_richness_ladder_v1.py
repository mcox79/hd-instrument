"""RELATION-TYPE-RICHNESS LADDER: does raising relation-COMPOSITION richness raise the inductive-inference floor?

QUESTION (next arc after #4-VET). The ingested-graph inductive wall (#4: no method beats codes ~0.70; held-out edges
unpredictable from structure) was traced to KNOWLEDGE thinness, and a naive density fix (k-core subsetting) was refuted
as a BRANCHINESS confound (denser subset = higher out-degree = harder routing, which cancels the raw density benefit).
The research drill (notes/research_inductive_inference_enablement_richness_vs_mechanism_2026-07-09.md) argues the missing
richness axis is RELATION-TYPE / COMPOSITION-PATTERN diversity, NOT raw density or entity count. This cell is the
confound-fixed first test: raise the number of distinct relation TYPES across rungs on the SAME node set, at MATCHED
out-degree (configuration-model-style degree-preserving resampling), and ask whether the best-method inductive held-out
score rises -- WHILE the known-degree oracle ceiling stays FLAT (proving the degree control held, unlike the k-core test).

CONSTRUCTION (reuses the #4 graph-inductive-ceiling harness VERBATIM: split, negatives, AUC, classic LP, GCN, codes).
  Ladder: nested relation-type sets ranked by edge-count. rung k in {2,5,10,16} distinct types (top-k by mass).
  Degree control: pick D* = the per-node degree sequence of the LOWEST rung (top-2 types) on the common node set;
    for EVERY rung, degree-preserving greedy resampling selects edges from that rung's allowed-type pool to approximate
    D* per node (configuration-model-style). Nested supersets => every rung can hit D* (feasibility guaranteed). Higher
    rungs fill the SAME degree quota using a MORE DIVERSE type mix => richness varies, branchiness (out-degree) held.
  Per rung, run the identical #4 harness (CN/AA/RA/JC/PA/GCN/CODE_COSINE, held-out far-negative AUC).

PRIMARY METRIC. best_inductive[rung] = max over {CN,AA,RA,JC,GCN,CODE_COSINE} of held-out far-AUC (PA EXCLUDED: PA =
  deg(u)*deg(v) is the degree/configuration-model oracle, not an inductive signal). ORACLE[rung] = PA far-AUC = the
  known-degree transition ceiling = the branchiness/difficulty control (the same degree-artifact diagnostic that exposed
  the k-core density confound).

DISCRIMINATOR (pre-registered; bands from the research note, not loosened).
  P1 (richness axis): slope = best_inductive[k=16] - best_inductive[k=2].
  P3 (degree-control validity, MANDATORY GATE): oracle_range_rel = (max-min ORACLE)/mean ORACLE across rungs;
     degree_range_rel = (max-min mean_degree)/mean mean_degree across rungs.
  HARD_PASS_RICHNESS_IS_LEVER = slope >= +0.05 AND oracle_range_rel <= 0.10 AND degree_range_rel <= 0.10
     (richness, independent of branchiness, raises the inductive floor; degree control held).
  HARD_FAIL_DEGREE_CONTROL_FAILED = oracle_range_rel > 0.15 OR degree_range_rel > 0.10  (CHECKED FIRST; confounded --
     the degree match did not hold, so any P1 read repeats the k-core interpretive mistake; result uninterpretable).
  HARD_FAIL_RICHNESS_NOT_LEVER = |slope| < 0.05 or non-monotonic decline AND degree_range_rel <= 0.05 (tight match)
     -> relation-type richness ALONE (within one graph, no cross-domain transfer) is NOT the lever; redirect to
     ULTRA-style cross-domain composition-pattern transfer.
  MIDDLE_BAND = otherwise (e.g. 0 < slope < 0.05, or oracle drifts 0.10-0.15).
Reported (never gated): per-rung per-method AUC, realized type-entropy + n_types_used, mean_degree, oracle, code AUC,
  monotonicity, relation-type pool size + per-type edge counts (Anchor 0 audit embedded).

SELF-TEST (mechanism; planted; MANDATORY assert_discriminator_fires; blocks dispatch if any fails):
  POS  (composition richness genuinely enables inference at matched degree): a base random graph + added TRANSITIVE-
       CLOSURE relation types (each added type contributes held-out edges that ARE predictable via a common base-neighbor
       hub). At matched degree, higher rungs hold a higher FRACTION of closure edges => best_inductive MUST rise
       (>= +0.05, k=2 -> k=max) while oracle stays flat.
  NULL (richness is fake -- more type LABELS, no composition structure): the SAME base random graph with extra types
       that are RANDOM RELABELS of random edges (no closure) => best_inductive MUST NOT rise (|slope| < 0.05) at matched
       degree. Proves the ladder does not reward type-COUNT per se, only composition STRUCTURE.
  DEGREE (oracle-detects-degree control): fixed richness, VARYING degree across probe-rungs => ORACLE (PA) AUC MUST MOVE
       (range > 0.10). Proves the oracle-flat check on real data genuinely certifies matched degree (a flat oracle is
       informative only if the oracle CAN move when degree changes).
  assert_discriminator_fires = POS_slope >= 0.05 AND |NULL_slope| < 0.05 AND DEGREE_oracle_range > 0.10.

## Compute architecture
class: (b) sequential-CPU with justification -- inherits the #4 harness compute class VERBATIM (classic predictors =
parameter-free neighbor-set intersections; GCN = one tiny dense 2-layer conv over n<=4500 normalized adjacency;
CODE_COSINE = the phase-0 binding encoder, ~13-30s/rung/seed CPU). 4 rungs x 3 seeds sequential; no
Python-loop-over-independent-points matmul; total wall < 3h/FULL. Storage strategy: no_storage / no_composition (graph-
analysis ceiling probe; no HD bundling or chained retrieval). Device-aware torch; CPU adequate -> remote_cpu_queue.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: reuses run_regime's per-method sha256 score signatures; >=4 distinct structural sigs asserted
#   per rung (inherited from the #4 harness ARMS-MUST-DIFFER path).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: AUC chance floor = 0.50. slope band +0.05 is a DELTA on far-AUC (reachable: planted POS demonstrates it);
#   oracle-flat 10% and degree-flat 10% are relative-range bounds. crlb_reachability: OK (planted POS clears +0.05).
# - baseline_in_band: the NULL planted arm is the 'must-not-rise on structureless richness' control (|slope|<0.05);
#   the POS planted arm is the 'must-rise when composition present' control (slope>=0.05); DEGREE arm is the
#   'oracle-must-move when degree changes' control. On real data the ladder trajectory IS the measurement.
# - discriminator survives scale: the planted POS/NULL/DEGREE selftests are analytical/by-construction and fire at any
#   scale (SELFTEST + SMOKE both run them at reduced n; classic-predictor AUC is deterministic given graph+split).
#   SMOKE previews the real ladder at n=1800; FULL (3 seeds, n=5000) canonical.
# - HARD_PASS slope +0.05 strictly above the |slope|<0.05 HARD_FAIL flat band; degree/oracle-flat add strictness.
# - HP_SCOPE: slope gate over best_inductive={CN,AA,RA,JC,GCN,CODE}. ORACLE=PA (degree control, flatness-gated, NOT an
#   inductive arm). CODE_COSINE also reported as reference. Planted POS/NULL/DEGREE = selftest controls.
# - positive_control (Gate D): CODE_COSINE reproduces the phase-0/#4 code-cosine regime per rung (reported); the #4
#   harness self-test (SBM signal vs ER null, gap>=0.20) is inherited and re-run implicitly via run_regime primitives.
# - sweep axis: relation-type-count in {2,5,10,16} x density-controlled; EXPECTED_N_UNITS = n_seeds; each seed asserted
#   to produce ALL rungs (rung-cardinality gate).
# - per-unit failure-class instrumentation (no bare except; per-rung/per-seed failure-class recorded).
# - calibration_check: default_ok_for_this_regime -- HELDOUT_FRAC + far-negative construction inherited VERBATIM from
#   phase-0 M5 / #4; rung boundaries {2,5,10,16} chosen by fixed rank-by-mass rule (Anchor 0), not tuned for verdict.
# - effective_vs_nominal (Gate A): swept param = n_distinct_relation_types; the primitive that experiences it is the
#   composition/common-neighbor structure of the visible graph. Degree held constant => the sweep is ALIGNED (richness
#   is the only varied axis; the oracle-flat check certifies alignment empirically per run).
# - discriminating_fraction (Gate B): the planted POS selftest demonstrates >=1 rung-pair in the discriminating band;
#   real-data bracket is the measurement (bands are deltas, not absolute-accuracy points).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-rung/per-method flush prints).
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import (  # noqa: E402
    load_typed_cn_subgraph, make_unitary_roles,
)
# Reuse the #4 harness VERBATIM (split, negatives, AUC, classic LP, GCN, CODE_COSINE, per-rung runner).
from experiments.exp_graph_inductive_ceiling_v1 import (  # noqa: E402
    run_regime, build_adj_sets, subgraph_reindex,
    CN, AA, RA, JC, PA, GCN, CODE, STRUCTURAL_METHODS, REL_METHODS, ALL_METHODS,
    MIN_HELDOUT_EDGES,
)

try:
    from experiments._cell_heartbeat import emit_heartbeat  # noqa: E402
except Exception:  # noqa -- optional instrumentation; explicit Exception, no bare except
    def emit_heartbeat(*a, **k):
        return None

ANCHOR_NAME = "relation_type_richness_ladder_v1"

# best_inductive = max over these (PA excluded = it is the degree/config-model oracle, not an inductive signal).
INDUCTIVE_METHODS = [CN, AA, RA, JC, GCN, CODE]

# ---- Pre-registered bands (picked BEFORE the run; from the research note) ----
RICHNESS_SLOPE_HP = 0.05        # HARD_PASS: best_inductive[max] - best_inductive[min] >= this
RICHNESS_SLOPE_FLAT = 0.05      # HARD_FAIL flat band: |slope| < this
ORACLE_FLAT_REL = 0.10          # P3: oracle range/mean <= this => degree control held
ORACLE_FAIL_REL = 0.15          # P3: oracle range/mean > this => degree control FAILED (confounded)
DEGREE_FLAT_REL = 0.10          # mean-degree range/mean <= this required for a clean richness read
DEGREE_TIGHT_REL = 0.05         # tight-match threshold for a clean HARD_FAIL_RICHNESS_NOT_LEVER

# ---- Ladder rungs (nested relation-type counts, ranked by edge mass; see Anchor 0 audit) ----
RUNG_KS = [2, 5, 10, 16]

# ---- Config profiles. SMOKE/SELFTEST exercise the SAME code path as FULL; only n + epochs + seeds differ. ----
_ENC_SMALL = dict(epochs=40, batch=256, code_dim=256, feat_dim=2048, temp=0.15, lr=0.01,
                  lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0)
_ENC_FULL = dict(epochs=80, batch=256, code_dim=512, feat_dim=4096, temp=0.15, lr=0.01,
                 lambda_cov=1.0, lambda_var=1.0, lambda_bind=1.0)
SELFTEST_CFG = dict(seeds=[7], n_nodes=1200, enc=_ENC_SMALL, gcn_epochs=60)
SMOKE_CFG = dict(seeds=[7], n_nodes=1800, enc=_ENC_SMALL, gcn_epochs=120)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, enc=_ENC_FULL, gcn_epochs=200)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


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
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Degree-preserving (configuration-model-style) edge resampling.
# Given a candidate edge pool (allowed relation types) and a per-node degree quota D*, greedily select a subset whose
# per-node degree approximates D*. Shuffle => higher rungs (richer type pool) fill the SAME quota with a MORE DIVERSE
# type mix, holding out-degree matched while richness varies.
# ---------------------------------------------------------------------------

def degree_matched_subsample(pool_edges, pool_rels, target_deg, seed):
    """pool_edges: [P,2] int array; pool_rels: [P] int; target_deg: [n] int quota. Returns (kept_edges, kept_rels)."""
    rng = np.random.default_rng(seed * 1000003 + 17)
    order = rng.permutation(len(pool_edges))
    resid = target_deg.astype(np.int64).copy()
    kept = []
    kept_rels = []
    for idx in order:
        u = int(pool_edges[idx, 0]); v = int(pool_edges[idx, 1])
        if u == v:
            continue
        if resid[u] > 0 and resid[v] > 0:
            kept.append((u, v))
            kept_rels.append(int(pool_rels[idx]))
            resid[u] -= 1
            resid[v] -= 1
    if not kept:
        return np.zeros((0, 2), dtype=np.int64), np.zeros((0,), dtype=np.int64)
    return np.asarray(kept, dtype=np.int64), np.asarray(kept_rels, dtype=np.int64)


def type_entropy(rels, n_types):
    if len(rels) == 0:
        return 0.0, 0
    cnt = np.bincount(np.asarray(rels, dtype=np.int64), minlength=n_types).astype(np.float64)
    p = cnt / cnt.sum()
    p = p[p > 0]
    h = float(-(p * np.log(p)).sum())
    return h, int((cnt > 0).sum())


# ---------------------------------------------------------------------------
# Rank relation types by edge mass; build nested rung type-sets.
# ---------------------------------------------------------------------------

def rank_types_by_mass(rels, n_types):
    cnt = np.bincount(np.asarray(rels, dtype=np.int64), minlength=n_types)
    ranked = list(np.argsort(-cnt))                     # type ids, descending edge count
    return [int(t) for t in ranked], cnt


def build_ladder(edges_c, rels_c, n_common, ranked_types, rung_ks, seed):
    """For each rung k: pool = common-node edges of the top-k types; degree-match to D* (top-rung-min degree seq)."""
    # D* = degree sequence of the LOWEST rung (top-2 types) on the common node set.
    k_min = rung_ks[0]
    low_types = set(ranked_types[:k_min])
    low_mask = np.array([r in low_types for r in rels_c], dtype=bool)
    adj_low, _ = build_adj_sets(edges_c[low_mask], n_common)
    D_star = np.array([len(adj_low[u]) for u in range(n_common)], dtype=np.int64)

    rungs = []
    for k in rung_ks:
        kset = set(ranked_types[:k])
        pmask = np.array([r in kset for r in rels_c], dtype=bool)
        pool_e = edges_c[pmask]
        pool_r = rels_c[pmask]
        ke, kr = degree_matched_subsample(pool_e, pool_r, D_star, seed + k)
        adj_k, _ = build_adj_sets(ke, n_common)
        deg_k = np.array([len(adj_k[u]) for u in range(n_common)], dtype=np.int64)
        h, ntu = type_entropy(kr, int(rels_c.max()) + 1 if len(rels_c) else 1)
        rungs.append(dict(k=k, edges=ke, rels=kr, n_edges=int(ke.shape[0]),
                          mean_degree=float(2.0 * ke.shape[0] / max(n_common, 1)),
                          realized_mean_deg_nz=float(deg_k[deg_k > 0].mean()) if (deg_k > 0).any() else 0.0,
                          type_entropy=h, n_types_used=ntu))
    return rungs, D_star


# ---------------------------------------------------------------------------
# Run one rung through the #4 harness (VERBATIM run_regime) + extract inductive + oracle.
# ---------------------------------------------------------------------------

def run_rung(rung, node_words_c, roles_t, enc_cfg, gcn_epochs, seed, device, do_code=True):
    label = "RUNG_K%02d" % rung["k"]
    res = run_regime(label, rung["edges"], rung["rels"], node_words_c, roles_t, enc_cfg, gcn_epochs,
                     seed, device, out_dir=None, do_code=do_code)
    if res.get("too_few"):
        return dict(k=rung["k"], too_few=True, n_heldout=res.get("n_heldout", 0))
    meth = res["methods"]

    def _auc(m):
        return meth.get(m, {}).get("auc_far", float("nan"))

    inductive_vals = [_auc(m) for m in INDUCTIVE_METHODS if _auc(m) == _auc(m)]
    best_inductive = max(inductive_vals) if inductive_vals else float("nan")
    best_arg = None
    if inductive_vals:
        for m in INDUCTIVE_METHODS:
            if _auc(m) == best_inductive:
                best_arg = m
                break
    oracle = _auc(PA)                                    # PA = deg(u)*deg(v) = known-degree config-model oracle
    # arms-differ (inherited): count distinct structural score signatures
    sig_vals = set(v for kk, v in res.get("sigs", {}).items()
                   if kk in STRUCTURAL_METHODS and v not in ("gcn_failed", "code_failed"))
    return dict(
        k=rung["k"], too_few=False,
        best_inductive=float(best_inductive), best_inductive_method=best_arg,
        oracle_pa=float(oracle),
        per_method={m: dict(auc_far=_auc(m)) for m in ALL_METHODS if m in meth},
        code_auc=_auc(CODE), n_heldout=int(res["n_heldout"]),
        mean_degree=float(res["mean_degree"]), mean_clustering=float(res.get("mean_clustering", float("nan"))),
        type_entropy=rung["type_entropy"], n_types_used=rung["n_types_used"], n_edges=rung["n_edges"],
        n_distinct_sigs=len(sig_vals), failures=res.get("failures", []),
    )


# ---------------------------------------------------------------------------
# Per-seed: build ladder from the loaded (common-node) graph, run all rungs.
# ---------------------------------------------------------------------------

def run_seed_ladder(seed, edges_c, rels_c, node_words_c, ranked_types, roles_t, enc_cfg, gcn_epochs, device,
                    out_dir=None):
    n_common = len(node_words_c)
    t0 = time.perf_counter()
    rungs, D_star = build_ladder(edges_c, rels_c, n_common, ranked_types, RUNG_KS, seed)
    rung_results = []
    for i, rung in enumerate(rungs):
        rr = run_rung(rung, node_words_c, roles_t, enc_cfg, gcn_epochs, seed, device, do_code=True)
        rung_results.append(rr)
        _log("  seed=%d k=%d E=%d mean_deg=%.2f H=%.2f n_types=%d n_ho=%s :: best_ind=%s(%s) oracle_PA=%s code=%s" % (
            seed, rung["k"], rung["n_edges"], rung["mean_degree"], rung["type_entropy"], rung["n_types_used"],
            rr.get("n_heldout"), _fmt(rr.get("best_inductive", float("nan"))), rr.get("best_inductive_method"),
            _fmt(rr.get("oracle_pa", float("nan"))), _fmt(rr.get("code_auc", float("nan")))))
        if out_dir:
            emit_heartbeat(out_dir, unit_idx=i, total_units=len(rungs), elapsed_s=time.perf_counter() - t0)
    return dict(seed=seed, rungs=rung_results, D_star_mean=float(D_star[D_star > 0].mean()) if (D_star > 0).any() else 0.0)


# ---------------------------------------------------------------------------
# Aggregate across seeds + verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed):
    ks = RUNG_KS
    # per-rung (index-aligned) means across seeds
    def rung_val(i, key):
        return _nm([m["rungs"][i].get(key, float("nan")) for m in per_seed
                    if i < len(m["rungs"]) and not m["rungs"][i].get("too_few", False)])

    best_ind = [rung_val(i, "best_inductive") for i in range(len(ks))]
    oracle = [rung_val(i, "oracle_pa") for i in range(len(ks))]
    mean_deg = [rung_val(i, "mean_degree") for i in range(len(ks))]
    code_auc = [rung_val(i, "code_auc") for i in range(len(ks))]
    entropy = [rung_val(i, "type_entropy") for i in range(len(ks))]
    n_types = [rung_val(i, "n_types_used") for i in range(len(ks))]
    n_ho = [int(rung_val(i, "n_heldout")) if rung_val(i, "n_heldout") == rung_val(i, "n_heldout") else 0
            for i in range(len(ks))]

    valid = [v for v in best_ind if v == v]
    enough = bool(min(n_ho) >= MIN_HELDOUT_EDGES) if n_ho else False

    def _range_rel(vals):
        a = np.array([v for v in vals if v == v], dtype=np.float64)
        if a.shape[0] < 2 or a.mean() == 0:
            return float("nan")
        return float((a.max() - a.min()) / abs(a.mean()))

    slope = (best_ind[-1] - best_ind[0]) if (best_ind[-1] == best_ind[-1] and best_ind[0] == best_ind[0]) else float("nan")
    # monotonic non-decreasing (allow tiny dips <=0.01)
    monotonic = all((best_ind[i + 1] >= best_ind[i] - 0.01)
                    for i in range(len(best_ind) - 1)
                    if best_ind[i] == best_ind[i] and best_ind[i + 1] == best_ind[i + 1])
    oracle_range_rel = _range_rel(oracle)
    degree_range_rel = _range_rel(mean_deg)

    oracle_flat = bool(oracle_range_rel == oracle_range_rel and oracle_range_rel <= ORACLE_FLAT_REL)
    degree_flat = bool(degree_range_rel == degree_range_rel and degree_range_rel <= DEGREE_FLAT_REL)
    degree_tight = bool(degree_range_rel == degree_range_rel and degree_range_rel <= DEGREE_TIGHT_REL)
    degree_control_failed = bool((oracle_range_rel == oracle_range_rel and oracle_range_rel > ORACLE_FAIL_REL)
                                 or (degree_range_rel == degree_range_rel and degree_range_rel > DEGREE_FLAT_REL))

    richness_rises = bool(slope == slope and slope >= RICHNESS_SLOPE_HP)
    richness_flat = bool(slope == slope and abs(slope) < RICHNESS_SLOPE_FLAT)

    if not enough or len(valid) < len(ks):
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT_OR_RUNG"
    elif degree_control_failed:
        verdict = "HARD_FAIL_DEGREE_CONTROL_FAILED_CONFOUNDED"
    elif richness_rises and oracle_flat and degree_flat:
        verdict = "HARD_PASS_RICHNESS_IS_LEVER"
    elif richness_flat and degree_tight:
        verdict = "HARD_FAIL_RICHNESS_NOT_LEVER"
    else:
        verdict = "MIDDLE_BAND_RICHNESS_LADDER"

    verdict_msg = (
        "%s || rungs k=%s best_inductive=%s (slope k2->k16=%s mono=%s) | ORACLE_PA=%s (range_rel=%s flat<=%.2f:%s) | "
        "mean_deg=%s (range_rel=%s flat<=%.2f:%s) | code=%s | type_entropy=%s n_types_used=%s n_ho=%s || "
        "RICHNESS_RISES(slope>=%.2f)=%s DEGREE_CONTROL_HELD=%s(oracle_flat=%s,deg_flat=%s) || seeds=%d" % (
            verdict, ks,
            "[" + ",".join(_fmt(v) for v in best_ind) + "]", _fmt(slope), monotonic,
            "[" + ",".join(_fmt(v) for v in oracle) + "]", _fmt(oracle_range_rel), ORACLE_FLAT_REL, oracle_flat,
            "[" + ",".join(_fmt(v) for v in mean_deg) + "]", _fmt(degree_range_rel), DEGREE_FLAT_REL, degree_flat,
            "[" + ",".join(_fmt(v) for v in code_auc) + "]",
            "[" + ",".join(_fmt(v) for v in entropy) + "]",
            "[" + ",".join("%d" % int(v) if v == v else 0 for v in n_types) + "]", n_ho,
            RICHNESS_SLOPE_HP, richness_rises, (not degree_control_failed), oracle_flat, degree_flat,
            len(per_seed)))

    gates = dict(
        verdict=verdict, rung_ks=ks,
        best_inductive_per_rung=best_ind, oracle_pa_per_rung=oracle, mean_degree_per_rung=mean_deg,
        code_auc_per_rung=code_auc, type_entropy_per_rung=entropy, n_types_used_per_rung=n_types,
        n_heldout_per_rung=n_ho,
        richness_slope=slope, richness_monotonic=monotonic,
        oracle_range_rel=oracle_range_rel, degree_range_rel=degree_range_rel,
        oracle_flat=oracle_flat, degree_flat=degree_flat, degree_tight=degree_tight,
        degree_control_failed=degree_control_failed,
        richness_rises=richness_rises, richness_flat=richness_flat, enough_heldout=enough,
        bands=dict(RICHNESS_SLOPE_HP=RICHNESS_SLOPE_HP, RICHNESS_SLOPE_FLAT=RICHNESS_SLOPE_FLAT,
                   ORACLE_FLAT_REL=ORACLE_FLAT_REL, ORACLE_FAIL_REL=ORACLE_FAIL_REL,
                   DEGREE_FLAT_REL=DEGREE_FLAT_REL, DEGREE_TIGHT_REL=DEGREE_TIGHT_REL, RUNG_KS=RUNG_KS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted self-tests (richness discriminator; MANDATORY).
# ---------------------------------------------------------------------------

def _planted_pos(m, k_types, n_base_per, clique_size, rng):
    """TWO random base types (0,1; unpredictable, highest mass => they form the k=2 floor rung) + one DENSE typed CLIQUE
    per added relation type (2..k-1; redundant common neighbors).

    The k=2 floor is pure random (AUC ~0.5); higher rungs add clique-types => a rising fraction of held-out edges are
    clique-internal (predictable via multiple common neighbors) => best_inductive rises. D* derives from the homogeneous
    random base => flat degree/oracle across rungs. Clique redundancy (clique_size >> D*) survives degree-preserving
    subsampling. n_base_per must exceed C(clique_size,2) so the two base types rank top-2 by mass. Returns (edges, rels)."""
    edges = []
    rels = []
    for bt in (0, 1):                                # two random base types (the k=2 floor)
        for _ in range(n_base_per):
            u = int(rng.integers(0, m)); v = int(rng.integers(0, m))
            if u != v:
                edges.append((u, v)); rels.append(bt)
    for t in range(2, k_types):                      # one dense clique per added type
        grp = rng.choice(m, size=min(clique_size, m), replace=False)
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                edges.append((int(grp[i]), int(grp[j]))); rels.append(t)
    return np.asarray(edges, dtype=np.int64), np.asarray(rels, dtype=np.int64)


def _planted_null(m, k_types, n_base, n_extra_per_type, rng):
    """Base ER + extra RANDOM edges labelled with fake types (no closure structure). More types = more random edges,
    no composition => best_inductive must NOT rise at matched degree."""
    edges = []
    rels = []
    for _ in range(n_base):
        u = int(rng.integers(0, m)); v = int(rng.integers(0, m))
        if u != v:
            edges.append((u, v)); rels.append(0)
    for t in range(1, k_types):
        for _ in range(n_extra_per_type):
            u = int(rng.integers(0, m)); v = int(rng.integers(0, m))
            if u != v:
                edges.append((u, v)); rels.append(t)
    return np.asarray(edges, dtype=np.int64), np.asarray(rels, dtype=np.int64)


def _ladder_on_planted(edges, rels, m, rung_ks, gcn_epochs, device, seed, tag):
    """Run the SAME degree-matched ladder on a planted graph (no codes). Returns best_inductive + oracle per rung."""
    node_words = ["n%d" % i for i in range(m)]
    ranked, _cnt = rank_types_by_mass(rels, int(rels.max()) + 1 if len(rels) else 1)
    rungs, _D = build_ladder(edges, rels, m, ranked, rung_ks, seed)
    best = []
    orac = []
    deg = []
    for rung in rungs:
        rr = run_rung(rung, node_words, None, None, gcn_epochs, seed, device, do_code=False)
        if rr.get("too_few"):
            best.append(float("nan")); orac.append(float("nan")); deg.append(rung["mean_degree"])
            continue
        best.append(rr["best_inductive"]); orac.append(rr["oracle_pa"]); deg.append(rr["mean_degree"])
    _log("  planted[%s] best_inductive=%s oracle_PA=%s mean_deg=%s" % (
        tag, "[" + ",".join(_fmt(v) for v in best) + "]",
        "[" + ",".join(_fmt(v) for v in orac) + "]",
        "[" + ",".join(_fmt(v) for v in deg) + "]"))
    return best, orac, deg


def _ba_graph(m, m_attach, rng):
    """Barabasi-Albert preferential-attachment growth => heterogeneous (power-law) degrees. PA-oracle is informative
    and tracks density on such a graph (unlike degree-homogeneous ER, where deg(u)*deg(v) carries little signal)."""
    edges = []
    targets = list(range(min(m_attach + 1, m)))
    repeated = list(targets)
    for new in range(len(targets), m):
        chosen = set()
        while len(chosen) < min(m_attach, len(set(repeated))):
            chosen.add(repeated[int(rng.integers(0, len(repeated)))])
        for t in chosen:
            edges.append((new, t))
            repeated.append(new); repeated.append(t)
    return np.asarray(edges, dtype=np.int64)


def _degree_probe(m, gcn_epochs, device, seed):
    """Fixed richness (single type), VARY degree via preferential-attachment m_attach; ORACLE (PA) must MOVE => the
    oracle genuinely detects branchiness/degree changes (so a flat oracle on real data certifies matched degree)."""
    rng = np.random.default_rng(seed + 999)
    node_words = ["n%d" % i for i in range(m)]
    oracle = []
    for m_attach in [1, 4, 10]:
        e = _ba_graph(m, m_attach, rng)
        rr = run_rung(dict(k=1, edges=e, rels=np.zeros(len(e), dtype=np.int64),
                           n_edges=len(e), mean_degree=2.0 * len(e) / m, type_entropy=0.0, n_types_used=1),
                      node_words, None, None, gcn_epochs, seed, device, do_code=False)
        oracle.append(rr.get("oracle_pa", float("nan")) if not rr.get("too_few") else float("nan"))
    return oracle


def mechanism_selftest(device, small=True):
    m = 260 if small else 400
    n_base_per = 540                      # per base-type random edges (> C(clique_size,2)=435 so base ranks top-2)
    clique_size = 30                      # dense typed clique per added relation type (clique_size >> D* ~ 8)
    n_extra = m // 2
    rng = np.random.default_rng(0)
    # planted ladder k=2 (pure random base, floor ~0.5) -> k=8 (6 cliques, high coverage). Richness = clique coverage
    # fraction at matched degree. Real-data ladder uses RUNG_KS=[2,5,10,16] (mass-based).
    rung_ks = [2, 4, 8]
    gcn_ep = 60

    pos_e, pos_r = _planted_pos(m, 8, n_base_per, clique_size, rng)
    pos_best, pos_orac, pos_deg = _ladder_on_planted(pos_e, pos_r, m, rung_ks, gcn_ep, device, 7, "POS")

    null_e, null_r = _planted_null(m, 8, 2 * n_base_per, n_extra, rng)
    null_best, null_orac, null_deg = _ladder_on_planted(null_e, null_r, m, rung_ks, gcn_ep, device, 7, "NULL")

    deg_oracle = _degree_probe(m, gcn_ep, device, 5)

    def _slope(v):
        vv = [x for x in v if x == x]
        return (vv[-1] - vv[0]) if len(vv) >= 2 else float("nan")

    def _range(v):
        vv = [x for x in v if x == x]
        return (max(vv) - min(vv)) if len(vv) >= 2 else float("nan")

    pos_slope = _slope(pos_best)
    null_slope = _slope(null_best)
    pos_oracle_range_rel = (_range(pos_orac) / (np.mean([x for x in pos_orac if x == x]) + 1e-9))
    deg_oracle_range = _range(deg_oracle)

    pos_rises = bool(pos_slope == pos_slope and pos_slope >= RICHNESS_SLOPE_HP)
    null_flat = bool(null_slope == null_slope and abs(null_slope) < RICHNESS_SLOPE_FLAT)
    pos_oracle_flat = bool(pos_oracle_range_rel == pos_oracle_range_rel and pos_oracle_range_rel <= ORACLE_FLAT_REL)
    degree_probe_moves = bool(deg_oracle_range == deg_oracle_range and deg_oracle_range > 0.10)

    res = dict(
        pos_best=pos_best, pos_oracle=pos_orac, pos_slope=pos_slope, pos_oracle_range_rel=pos_oracle_range_rel,
        null_best=null_best, null_slope=null_slope,
        degree_probe_oracle=deg_oracle, degree_probe_range=deg_oracle_range,
        pos_rises=pos_rises, null_flat=null_flat, pos_oracle_flat=pos_oracle_flat,
        degree_probe_moves=degree_probe_moves,
    )
    ok = bool(pos_rises and null_flat and degree_probe_moves)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if (args.device == "cuda" and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s rungs=%s" % (device, torch.cuda.is_available(), run_mode, RUNG_KS))

    st_ok, st_res = mechanism_selftest(device, small=(run_mode != "full"))
    _log("mechanism_selftest ok=%s pos_slope=%s null_slope=%s deg_probe_range=%s" % (
        st_ok, _fmt(st_res["pos_slope"]), _fmt(st_res["null_slope"]), _fmt(st_res["degree_probe_range"])))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg=("MECHANISM_SELFTEST_FAILED (richness discriminator does not fire): pos_rises=%s null_flat=%s "
                         "degree_probe_moves=%s :: %s" % (st_res["pos_rises"], st_res["null_flat"],
                                                          st_res["degree_probe_moves"], st_res)),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg=("SELFTEST_PASS relation-type-richness-ladder: planted POS rises with type-count (slope=%s>=%.2f) "
                         "at matched degree (oracle_flat=%s), planted NULL flat (slope=%s), degree-probe moves oracle "
                         "(range=%s>0.10) -> ladder detects composition-richness, not type-count per se, and the oracle "
                         "control fires on degree changes" % (
                             _fmt(st_res["pos_slope"]), RICHNESS_SLOPE_HP, st_res["pos_oracle_flat"],
                             _fmt(st_res["null_slope"]), _fmt(st_res["degree_probe_range"]))),
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    # ---- Load the typed ConceptNet subgraph, restrict to common node set (rung-1 coverage), reindex ----
    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels, dtype=np.int64)
    ranked_types, type_counts = rank_types_by_mass(rels, T)
    rel_pool_audit = dict(n_relation_types=int(T),
                          per_type_edge_count={types[i]: int(type_counts[i]) for i in range(T)},
                          ranked_types_by_mass=[types[t] for t in ranked_types])
    _log("subgraph: n_nodes=%d n_edges=%d rel_types=%d ranked=%s"
         % (len(node_ids), edges.shape[0], T, [types[t] for t in ranked_types[:6]]))

    # common node set = nodes with >=1 edge among the lowest rung's (top-2) relation types
    low_types = set(ranked_types[:RUNG_KS[0]])
    low_mask = np.array([r in low_types for r in rels], dtype=bool)
    adj_low, _ = build_adj_sets(edges[low_mask], len(node_ids))
    common_mask = np.array([len(adj_low[u]) >= 1 for u in range(len(node_ids))], dtype=bool)
    edges_c, rels_c, node_words_c, _old = subgraph_reindex(edges, rels, node_words, common_mask)
    rels_c = np.asarray(rels_c, dtype=np.int64)
    n_common = len(node_words_c)
    _log("common node set (rung-1 coverage): n_common=%d edges_c=%d (of %d nodes)"
         % (n_common, edges_c.shape[0], len(node_ids)))

    role_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 777)
    roles_t = torch.from_numpy(make_unitary_roles(T, cfg["enc"]["code_dim"], role_rng)).to(device)

    out_dir_path = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            sd = run_seed_ladder(seed, edges_c, rels_c, node_words_c, ranked_types, roles_t,
                                 cfg["enc"], cfg["gcn_epochs"], device, out_dir=out_dir_path)
            # rung-cardinality (META_RULE_H): every rung must be present + valid
            valid_rungs = [r for r in sd["rungs"] if not r.get("too_few", False)]
            if len(valid_rungs) < len(RUNG_KS):
                raise RuntimeError("RUNG_CARDINALITY_BREACH seed=%d only %d/%d valid rungs"
                                   % (seed, len(valid_rungs), len(RUNG_KS)))
            # arms-differ (META_RULE_AF) per rung
            for r in valid_rungs:
                if r.get("n_distinct_sigs", 0) < 4:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d k=%d only %d distinct sigs"
                                       % (seed, r["k"], r.get("n_distinct_sigs", 0)))
            per_seed.append(sd)
            write_partial(out_dir_path, seed, dict(seed=seed, metrics=sd))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta, relation_pool_audit=rel_pool_audit))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], n_common_nodes=n_common,
                   config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"], rung_ks=RUNG_KS,
                               gcn_epochs=cfg["gcn_epochs"], enc=cfg["enc"]),
                   subgraph_meta=meta, relation_pool_audit=rel_pool_audit, gates=gates,
                   mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
