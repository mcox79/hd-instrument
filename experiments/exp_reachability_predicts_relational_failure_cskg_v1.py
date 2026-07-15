"""REACHABILITY-AUDIT PREDICTIVE-DIAGNOSTIC TEST (grounding deliverable, drill_grounding_scoping_is_it_subsumed_by
_foundation_hub_or_separate_2026-07-15): does per-entity RELATIONAL-REACHABILITY PREDICT relational-inference FAILURE
on the existing reduced-CSKG, BEYOND a raw-degree/frequency confound? Validates the diagnostic claim behind the
reachability-audit tool (hdlab/reachability_audit.py): a poorly-reachable entity (a closed relational island, an
ungrounded name-tag) is where the additive relational readout underperforms.

The audit tool has TWO modes: (a) MEASURED-REACHABILITY certification (needs grounded modules; STUB-READY, inert on
the metadata-empty substrate, reported here as measured_reachability_active=False -- ready for Costanzo/BioGRID);
(b) RELATIONAL-REACHABILITY diagnostic (runs NOW). This cell tests mode (b)'s diagnostic power.

TEST: transductive held-out-EDGE arena (identical machinery to the VET-run bucket_diversity_degree_controlled cell:
same induced 6-bucket CSKG-relations subgraph, same build_holdout_split, same additive KGE fit + additive_direct
readout + filtered per-query RR). Per QUERY-HEAD entity: y = mean filtered RR (its relational-inference accuracy),
z = undirected TRAIN degree (the confound), R = k-hop reachable mass (the reachability anchor), all computed ONLY
from TRAIN-remaining edges (no query leakage). PRIMARY = partial Spearman(R, y | z) with a within-degree-stratum
permutation null (the decisive beyond-degree control). SECONDARY (reported, non-gating): distance-to-hub (expected
NEGATIVE), mean-neighbor-degree (expected POSITIVE), raw uncontrolled Spearman (shows how much degree explains),
bottom/top-RR-decile mean reachability (the 6-instance relational-failure-track-record tie-in: are the failures the
low-reachability entities?).

SIGN CONVENTION: reachability defined so HIGHER = better-connected/more-grounded. HARD_PASS expects a POSITIVE partial
rho (more reachable -> higher accuracy), equivalently reachability predicts FAILURE (low reachability -> low accuracy,
the task's 'negative correlation' framing on the failure axis). distance_to_hub (higher = more peripheral) is the
mirror metric expected NEGATIVE.

## Prior-work check (substrate-KB concept-query, mandatory pre-authoring)
`bash tools/substrate_query.sh "reachability audit measured-attribute grounding relational-inference entity
connectivity degree hub"` -> top hit cosine=0.3008 (notes/research_drill_teacher_free_semantic_bootstrapping_from
_sparse_kb_2026-07-04.md::chunk015, a KB-density/semantic-bootstrapping note; RELATED theme of relational-structure
richness but a DIFFERENT question -- that note predicts semantic-neighbor structure emerges at higher KB density;
this cell asks whether per-entity graph reachability predicts relational readout failure at CURRENT density). All
other hits < 0.30 (token-similarity noise: relativity/reactivity/retentivity). VERDICT: genuinely NOVEL -- no prior
reachability-audit CELL; the degree-control methodology has precedent in the bucket_diversity cell (whose machinery
this reuses verbatim) but the covariate (reachability, not bucket-diversity) and the diagnostic claim are new.

## Arms
  MAIN             : fitted additive scorer (X_h + D_r) on the TRAIN graph -- produces the per-entity accuracy y.
  RANDOM_CODES     : random X,D (no fit) -- null floor (arena-fires gate).
  RELATION_SCRAMBLE: MAIN's X, D rows permuted at score time -- must-fail control (relational signal genuine).
  BASELINE_POP     : frequency incumbent (pop_hits) -- reported for context, not gated.

## Controls / must-fails
  ARENA_FIRES        : MAIN_mrr >= 3x RANDOM_mrr AND (MAIN - RANDOM) >= 0.01 (arena answerable; else INCONCLUSIVE).
  SCRAMBLE_CONTROLLED: (SCRAMBLE - RANDOM) <= 0.25*(MAIN - RANDOM) (relation-scramble collapses).
  WITHIN-DEGREE-STRATUM PERMUTATION NULL (the decisive control for THIS cell's question): shuffle each entity's
    reachability value only AMONG entities of SIMILAR degree (quantile strata); recompute partial rho N_PERM times;
    p = fraction of |null partial-rho| >= |real|. A real partial-rho beating this null is signal BEYOND degree.
  Two seeds (7,13) drive BOTH the split AND the fit; verdict requires sign-consistency AND significance across BOTH.

## PRE-REGISTERED BANDS (picked BEFORE the run; all HYPOTHESIZED@this-prereg unless tagged)
  primary = partial_spearman(k_hop_reachable_mass, mean_RR | undirected_train_degree), per seed, permutation p.
  HARD_PASS_REACHABILITY_PREDICTS_RELATIONAL_FAILURE: arena_fires AND scramble_controlled AND both seeds have
    >= MIN_ENTITIES query-head entities AND BOTH seeds: partial_rho > 0 (correct sign) AND partial_rho >= 0.10 AND
    perm_p <= 0.05. => the audit's diagnostic claim HOLDS beyond degree.
  MIDDLE_REACHABILITY_WEAK_OR_LARGELY_DEGREE: arena+scramble+entities OK AND both seeds correct sign AND both
    perm_p <= 0.15 AND both |partial_rho| >= 0.04, but not meeting HARD (small effect or marginal p) => reachability
    correlates but the beyond-degree component is weak.
  REFUTE_REACHABILITY_DOES_NOT_PREDICT_BEYOND_DEGREE: arena+scramble+entities OK AND NOT correct-sign-significant
    (any seed wrong sign, OR both |partial_rho| < 0.04, OR any perm_p > 0.15, OR seed sign-disagreement) => the
    diagnostic claim is UNSUPPORTED; reachability failure-prediction is a degree artifact. HONEST NEGATIVE, valuable.
  INCONCLUSIVE_ARENA_DID_NOT_FIRE / INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED / INCONCLUSIVE_INSUFFICIENT_ENTITIES:
    fail-closed labels when the arena or entity population is not sound enough to trust any correlation call.

## Compute architecture
class (a) batched: ONE transductive additive-KGE fit (vectorized torch minibatch SGD, CPU) per seed -- the SAME
config as bucket_diversity FULL (k=16, epochs=150, n_neg=64, batch=8192, neg_chunk=16), which ran within budget
(MEASURED@data/exp_bucket_diversity_degree_controlled_inference_cskg_v1 -- reproduced machinery). The KGE fit is the
mechanism whose per-entity failures we diagnose, so it is NOT over-build: there is no cheaper way to obtain per-entity
relational-inference accuracy than running the actual readout (compute-proportionality: heavy method justified because
the CLAIM is the substrate's own per-entity accuracy). Reachability traversal (k-hop BFS, multi-source BFS, partial
Spearman, stratified permutation) is CHEAP (seconds), dwarfed by the fit. Storage SHARDED (each entity its own X row).
Readout query-chunked batched matmul (SCORE_CHUNK). device=cpu (task-specified; CPU-appropriate scale). Seeds
sequential in one process.

# CELL-TEMPLATE MANDATORY (per experiments/_validity_preflight + exp_dev.md SS12-SS17):
# - arms_differ_verified at self-test + per-seed (MAIN/RANDOM/SCRAMBLE score-signature hashes >= 3 distinct).
# - final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb_n/a: no closed-form noise floor for a partial-rank-correlation test; feasibility established empirically
#   (arena_fires gate: MAIN clears RANDOM by fixed ratio+abs) + MIN_ENTITIES population floor known before the run.
# - baseline_in_band: arena_fires IS the baseline-in-band check (RANDOM near floor; MAIN clears it).
# - discriminator survives scale: option (C) discriminator-preview -- SMOKE runs the FULL induced graph (full N,
#   full edge set), single seed, reduced epochs, to preview arena_fires + entity-population + a non-degenerate
#   partial-rho pipeline BEFORE the 2-seed FULL commits full compute.
# - HP_SCOPE: arena_fires + scramble_controlled apply to ALL seeds unconditionally; HARD/MIDDLE/REFUTE bands apply to
#   the cross-seed aggregate of the partial-rho (not per-arm).
# - cardinality: EXPECTED_N_UNITS = n_seeds (2 FULL / 1 SMOKE); per-seed failure halts with failure_class.
# - calibration_check: default_ok_for_this_regime -- split knobs + fit hyperparams inherited unchanged from the VET
#   bucket_diversity cell; RHO/P bands are effect-size thresholds picked from correlation convention, NOT tuned on
#   the outcome (the run has not been executed).
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ above.
# - real_code_path: self-test constructs the REAL reachability tool + REAL fit/score/RR/partial-rho pipeline at N~150.
# - deterministic_seeding: fixed int seeds; sorted iteration; np.random.default_rng only (PROT-023 source-scanned).
# - progress_logging: print_flush_true (line-buffered stdout + flush prints per seed).

ASCII-only. No bare except; except SystemExit before except Exception.
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.reachability_audit import (  # noqa: E402
    build_undirected_adj, degree_vector, k_hop_reachable_mass, distance_to_hub, mean_neighbor_degree,
    top_degree_hubs, measured_reachability, spearman, partial_spearman, quantile_strata,
    perm_p_partial_stratified,
)
from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, pop_hits,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402
from experiments.exp_bucket_diversity_degree_controlled_inference_cskg_v1 import (  # noqa: E402
    BUCKET_MAP, DATA_REL, load_induced_triples, build_holdout_split, filtered_rr_per_query,
    build_planted_bucket_arena, SYNTH_BUCKET_MAP,
)

ANCHOR_NAME = "reachability_predicts_relational_failure_cskg_v1"

# ---- reachability knobs ----
KHOP_K = 2                 # primary reachability = distinct entities within 2 undirected hops
KHOP_CAP = 60000           # bound seen-set growth for extreme hubs (recorded mass is a floor if hit)
HUB_FRAC = 0.01            # top 1% degree = the relational core (distance-to-hub target set)
DEG_STRATA_BINS = 10       # quantile strata for the within-degree permutation null

# ---- population / band knobs (pre-registered; effect-size thresholds, NOT tuned on outcome) ----
MIN_ENTITIES = 200
RHO_HARD = 0.10
RHO_MID = 0.04
P_SIG = 0.05
P_MID = 0.15
EXPECTED_SIGN = 1          # higher reachability -> higher accuracy
N_PERM = 500

# ---- arena / scramble gates (inherited from the VET bucket_diversity cell) ----
ARENA_FIRE_RATIO = 3.0
ARENA_FIRE_ABS = 0.01
SCRAMBLE_CEIL_FRAC = 0.25

SCORE_CHUNK = 256


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Per-entity reachability + accuracy assembly + the partial-correlation diagnostic.
# ---------------------------------------------------------------------------

def build_entity_arrays(query_int, rr_main, adj, deg):
    """Per QUERY-HEAD entity: mean RR (accuracy), degree, k-hop mass, distance-to-hub, mean-neighbor-degree.

    Returns dict of parallel np arrays keyed by entity int-id order (only entities with >=1 query)."""
    rr_by_head = defaultdict(list)
    for i in range(query_int.shape[0]):
        rr_by_head[int(query_int[i, 0])].append(float(rr_main[i]))
    heads = sorted(rr_by_head.keys())
    y = np.array([float(np.mean(rr_by_head[h])) for h in heads], dtype=np.float64)
    nq = np.array([len(rr_by_head[h]) for h in heads], dtype=np.int64)
    z_deg = deg[heads].astype(np.float64)
    khop = k_hop_reachable_mass(adj, KHOP_K, cap=KHOP_CAP)[heads].astype(np.float64)
    hub_ids = top_degree_hubs(deg, HUB_FRAC)
    d2h = distance_to_hub(adj, hub_ids)[heads].astype(np.float64)
    mnd = mean_neighbor_degree(adj, deg)[heads].astype(np.float64)
    return dict(heads=np.array(heads, dtype=np.int64), y=y, nq=nq, deg=z_deg, khop=khop, d2h=d2h, mnd=mnd,
                n_hubs=int(hub_ids.shape[0]))


def diagnostic_for_seed(ea, seed):
    """Partial-rho diagnostics for one seed. PRIMARY = partial_spearman(khop, y | deg) + stratified perm p."""
    y, deg, khop, d2h, mnd = ea["y"], ea["deg"], ea["khop"], ea["d2h"], ea["mnd"]
    strata = quantile_strata(deg, DEG_STRATA_BINS)
    rho_primary, p_primary, null_mean, null_std = perm_p_partial_stratified(khop, y, deg, strata, N_PERM, seed * 6151 + 5)
    # secondary (reported, non-gating)
    rho_d2h = partial_spearman(d2h, y, deg)          # expected NEGATIVE (far from hub -> low accuracy)
    rho_mnd = partial_spearman(mnd, y, deg)          # expected POSITIVE
    rho_raw = spearman(khop, y)                       # uncontrolled (degree still in it)
    rho_deg = spearman(deg, y)                        # degree-vs-accuracy alone (the confound's own signal)
    # 6-instance failure tie-in: mean reachability of the worst vs best accuracy entities
    n = y.shape[0]
    order = np.argsort(y)
    dec = max(1, n // 10)
    bot_khop = float(np.mean(khop[order[:dec]])) if n else float("nan")
    top_khop = float(np.mean(khop[order[-dec:]])) if n else float("nan")
    return dict(
        seed=seed, n_entities=int(n),
        partial_rho_khop=round(rho_primary, 6), perm_p_khop=round(p_primary, 6),
        perm_null_mean=round(null_mean, 6), perm_null_std=round(null_std, 6),
        partial_rho_dist2hub=round(rho_d2h, 6), partial_rho_meanNbrDeg=round(rho_mnd, 6),
        raw_spearman_khop=round(rho_raw, 6), spearman_degree_only=round(rho_deg, 6),
        bottom_decile_mean_khop=round(bot_khop, 4), top_decile_mean_khop=round(top_khop, 4),
        n_hubs=ea["n_hubs"], mean_nq=round(float(np.mean(ea["nq"])), 3), median_deg=float(np.median(deg)),
    )


# ---------------------------------------------------------------------------
# One seed: split -> fit -> 3 arms -> per-entity RR -> reachability -> diagnostic.
# ---------------------------------------------------------------------------

def run_one_seed(triples, bucket_map, cfg, device, seed, ckpt_dir=None):
    train_lbl, query_lbl, _src_train_degree, _src_train_buckets = build_holdout_split(triples, bucket_map, seed)
    all_lbl = train_lbl + query_lbl
    ent2i, rel2i = build_ids(all_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, query_int)
    gd = Graph(train_lbl, ent2i, rel2i)

    result = dict(N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]), n_query=int(query_int.shape[0]),
                  seed=seed)
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    ckpt = FitCheckpoint(ckpt_dir, "kge_seed%d" % seed, cfg.get("ckpt_every")) if (ckpt_dir and cfg.get("ckpt_every")) else None
    X, D = fit_kge_anchor1(train_int, N, n_rel, cfg["k"], device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"], neg_chunk=cfg.get("neg_chunk"), ckpt=ckpt)
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, cfg["k"], generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, cfg["k"], generator=gR) * 0.1).to(device)
    rng2 = np.random.default_rng(seed * 4441 + 17)
    perm = rng2.permutation(n_rel)
    if n_rel > 1 and bool((perm == np.arange(n_rel)).all()):
        perm = np.roll(perm, 1)
    Dscr = D[torch.from_numpy(perm).long().to(device)]

    sc_main = additive_direct_scores(X, D, query_int, device, chunk=SCORE_CHUNK)
    sc_random = additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)
    sc_scramble = additive_direct_scores(X, Dscr, query_int, device, chunk=SCORE_CHUNK)

    rr_main = filtered_rr_per_query(sc_main, query_int, all_true)
    rr_random = filtered_rr_per_query(sc_random, query_int, all_true)
    rr_scramble = filtered_rr_per_query(sc_scramble, query_int, all_true)
    pop_m, _ = pop_hits(gd.rel_tail_freq, query_int, all_true, N, ks=(1, 10))

    arm_sigs = dict(MAIN=_sig(sc_main.numpy()[:min(64, sc_main.shape[0])].ravel()),
                    RANDOM=_sig(sc_random.numpy()[:min(64, sc_random.shape[0])].ravel()),
                    SCRAMBLE=_sig(sc_scramble.numpy()[:min(64, sc_scramble.shape[0])].ravel()))

    # reachability from TRAIN edges ONLY (no query leakage)
    adj = build_undirected_adj(train_int, N)
    deg = degree_vector(adj)
    ea = build_entity_arrays(query_int, rr_main, adj, deg)
    diag = diagnostic_for_seed(ea, seed)

    # mode (a) measured-reachability: inert on metadata-empty substrate (no grounded content yet)
    grounded_mask = np.zeros(N, dtype=bool)
    mr = measured_reachability(adj, grounded_mask, KHOP_K)
    diag["measured_reachability_active"] = bool(mr.any())
    diag["n_grounded_entities"] = int(grounded_mask.sum())

    del sc_main, sc_random, sc_scramble, X, D, Xr, Dr, Dscr
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    result.update(
        main_mrr=round(float(np.mean(rr_main)), 6), random_mrr=round(float(np.mean(rr_random)), 6),
        scramble_mrr=round(float(np.mean(rr_scramble)), 6), pop_mrr=round(pop_m.get("mrr", float("nan")), 6),
        arm_sigs=arm_sigs, diagnostic=diag, n_entities=diag["n_entities"],
    )
    return result


# ---------------------------------------------------------------------------
# Cross-seed verdict.
# ---------------------------------------------------------------------------

def verdict_from_gates(per_seed):
    main_mrr = float(np.mean([r["main_mrr"] for r in per_seed]))
    random_mrr = float(np.mean([r["random_mrr"] for r in per_seed]))
    scramble_mrr = float(np.mean([r["scramble_mrr"] for r in per_seed]))
    pop_mrr = float(np.mean([r["pop_mrr"] for r in per_seed]))

    arena_margin = main_mrr - random_mrr
    arena_ratio = (main_mrr / random_mrr) if random_mrr > 0 else float("inf")
    arena_fires = bool(arena_margin >= ARENA_FIRE_ABS and arena_ratio >= ARENA_FIRE_RATIO)

    scr_margin = scramble_mrr - random_mrr
    scramble_ceiling = SCRAMBLE_CEIL_FRAC * arena_margin if arena_margin == arena_margin else float("nan")
    scramble_controlled = bool(scr_margin == scr_margin and scramble_ceiling == scramble_ceiling
                               and scr_margin <= scramble_ceiling)

    all_sigs = set()
    for r in per_seed:
        all_sigs |= set(r.get("arm_sigs", {}).values())
    arms_differ = bool(len(all_sigs) >= 3)

    diags = [r["diagnostic"] for r in per_seed]
    n_ents = [d["n_entities"] for d in diags]
    rhos = [d["partial_rho_khop"] for d in diags]
    ps = [d["perm_p_khop"] for d in diags]
    signs = [1 if rr > 0 else (-1 if rr < 0 else 0) for rr in rhos]

    enough_entities = bool(min(n_ents) >= MIN_ENTITIES)
    correct_sign_both = bool(all(s == EXPECTED_SIGN for s in signs))
    hard = bool(correct_sign_both and all(abs(rr) >= RHO_HARD for rr in rhos) and all(p <= P_SIG for p in ps))
    middle = bool(correct_sign_both and all(abs(rr) >= RHO_MID for rr in rhos) and all(p <= P_MID for p in ps))

    if not arena_fires:
        verdict = "INCONCLUSIVE_ARENA_DID_NOT_FIRE"
    elif not scramble_controlled:
        verdict = "INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED"
    elif not enough_entities:
        verdict = "INCONCLUSIVE_INSUFFICIENT_ENTITIES"
    elif hard:
        verdict = "HARD_PASS_REACHABILITY_PREDICTS_RELATIONAL_FAILURE"
    elif middle:
        verdict = "MIDDLE_REACHABILITY_WEAK_OR_LARGELY_DEGREE"
    else:
        verdict = "REFUTE_REACHABILITY_DOES_NOT_PREDICT_BEYOND_DEGREE"

    verdict_msg = (
        "%s || MAIN=%s RANDOM=%s SCRAMBLE=%s POP=%s (arena_margin=%s ratio=%s fires=%s) | scramble_controlled=%s | "
        "per_seed partial_rho(khop,RR|deg)=%s perm_p=%s sign_ok=%s | per_seed raw_spearman=%s degree_only=%s | "
        "dist2hub_rho=%s meanNbrDeg_rho=%s | bottom/top-decile khop=%s | n_entities=%s | arms_differ=%s(sigs=%d) seeds=%d"
        % (verdict, _fmt(main_mrr), _fmt(random_mrr), _fmt(scramble_mrr), _fmt(pop_mrr),
           _fmt(arena_margin), (_fmt(arena_ratio) if arena_ratio != float("inf") else "inf"), arena_fires,
           scramble_controlled,
           [round(x, 4) for x in rhos], [round(x, 4) for x in ps], correct_sign_both,
           [d["raw_spearman_khop"] for d in diags], [d["spearman_degree_only"] for d in diags],
           [d["partial_rho_dist2hub"] for d in diags], [d["partial_rho_meanNbrDeg"] for d in diags],
           [(d["bottom_decile_mean_khop"], d["top_decile_mean_khop"]) for d in diags],
           n_ents, arms_differ, len(all_sigs), len(per_seed)))

    gates = dict(
        verdict=verdict, main_mrr=round(main_mrr, 6), random_mrr=round(random_mrr, 6),
        scramble_mrr=round(scramble_mrr, 6), pop_mrr=round(pop_mrr, 6),
        arena_margin=round(arena_margin, 6),
        arena_ratio=(round(arena_ratio, 3) if arena_ratio != float("inf") else None), arena_fires=arena_fires,
        scramble_margin=round(scr_margin, 6),
        scramble_ceiling=round(scramble_ceiling, 6) if scramble_ceiling == scramble_ceiling else None,
        scramble_controlled=scramble_controlled, arms_differ=arms_differ, n_distinct_sigs=len(all_sigs),
        enough_entities=enough_entities, correct_sign_both=correct_sign_both, hard=hard, middle=middle,
        per_seed_partial_rho_khop=rhos, per_seed_perm_p_khop=ps, per_seed_n_entities=n_ents,
        per_seed_diagnostic=diags,
        bands=dict(RHO_HARD=RHO_HARD, RHO_MID=RHO_MID, P_SIG=P_SIG, P_MID=P_MID, EXPECTED_SIGN=EXPECTED_SIGN,
                   MIN_ENTITIES=MIN_ENTITIES, N_PERM=N_PERM, KHOP_K=KHOP_K, HUB_FRAC=HUB_FRAC,
                   DEG_STRATA_BINS=DEG_STRATA_BINS, ARENA_FIRE_RATIO=ARENA_FIRE_RATIO, ARENA_FIRE_ABS=ARENA_FIRE_ABS,
                   SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test (real code path, tiny planted synthetic arena + mode-(a) traversal proof).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(k=8, epochs=60, n_neg=16, batch=512)
SELFTEST_MIN_QUERY = 8


def self_test():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _self_test_body(device)
    finally:
        torch.set_num_threads(_prev)


def _self_test_body(device):
    exercised = set()
    triples = build_planted_bucket_arena(7, n_ent=150, n_rel=6, k_lat=6, deg_lo=5, deg_hi=10)
    exercised.add("build_planted_bucket_arena")

    res = run_one_seed(triples, SYNTH_BUCKET_MAP, SELFTEST_CFG, device, 7, ckpt_dir=None)
    exercised.update(["build_holdout_split", "fit_kge_anchor1", "additive_direct_scores", "filtered_rr_per_query",
                      "build_undirected_adj", "degree_vector", "k_hop_reachable_mass", "distance_to_hub",
                      "top_degree_hubs", "mean_neighbor_degree", "partial_spearman", "quantile_strata",
                      "perm_p_partial_stratified", "measured_reachability"])
    out = dict(n_query=res.get("n_query"), n_entities=res.get("n_entities"))
    if res.get("empty") or res.get("n_query", 0) < SELFTEST_MIN_QUERY:
        out["fail"] = "planted arena produced too few query edges (%s)" % res.get("n_query")
        return False, out

    v, msg, gates = verdict_from_gates([res])
    exercised.add("verdict_from_gates")
    out["selftest_verdict"] = v
    out["gates"] = gates

    arena_fires = bool(gates["arena_fires"])
    scramble_controlled = bool(gates["scramble_controlled"])
    arms_differ = bool(gates["arms_differ"])
    diag = res["diagnostic"]
    p_ok = bool(0.0 <= diag["perm_p_khop"] <= 1.0)
    rho_ok = bool(-1.0 <= diag["partial_rho_khop"] <= 1.0)

    # mode (a) traversal correctness: inject a synthetic grounded set and assert reachable-grounded-mass fires.
    N = res["N"]
    train_lbl, query_lbl, _d, _b = build_holdout_split(triples, SYNTH_BUCKET_MAP, 7)
    ent2i, rel2i = build_ids(train_lbl + query_lbl, [], [])
    adj_st = build_undirected_adj(_to_int_edges(train_lbl, ent2i, rel2i), len(ent2i))
    deg_st = degree_vector(adj_st)
    hub = int(np.argmax(deg_st))
    gmask = np.zeros(len(ent2i), dtype=bool)
    gmask[hub] = True                                   # one grounded node (the top hub)
    mr = measured_reachability(adj_st, gmask, 2)
    mode_a_fires = bool(mr.sum() > 0 and mr[hub] >= 1)  # hub reaches itself; its neighbors reach it within 1-2 hops
    mode_a_inert_when_empty = bool(measured_reachability(adj_st, np.zeros(len(ent2i), dtype=bool), 2).sum() == 0)

    assert_discriminator_fires(bool(not arena_fires), control_name="RANDOM_CODES", headline_name="arena_fires",
                               run_mode="self_test",
                               extra="RANDOM reached MAIN on the planted arena -> arena not answerable")
    assert_discriminator_fires(bool(not scramble_controlled), control_name="RELATION_SCRAMBLE",
                               headline_name="scramble_controlled", run_mode="self_test",
                               extra="relation-scrambled D did not collapse toward RANDOM")

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path", "full_substrate_entrypoints":
            ["build_holdout_split", "fit_kge_anchor1", "additive_direct_scores", "filtered_rr_per_query",
             "build_undirected_adj", "k_hop_reachable_mass", "distance_to_hub", "measured_reachability",
             "partial_spearman", "perm_p_partial_stratified", "verdict_from_gates"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1,
         "kwargs": dict(train_edges=None, N=1, n_rel=1, k=8, device=device, seed=7, epochs=1,
                        reciprocal=True, lr=A1_LR, n_neg=4, batch_size=32, neg_chunk=None, ckpt=None),
         "callable_name": "fit_kge_anchor1"},
        {"kind": "metric_moves", "metric_name": "mrr",
         "values": [gates["random_mrr"], gates["scramble_mrr"], gates["main_mrr"]],
         "extra": "MRR RANDOM=%.4f SCRAMBLE=%.4f MAIN=%.4f" % (gates["random_mrr"], gates["scramble_mrr"],
                                                               gates["main_mrr"])},
        {"kind": "negative_control_margin", "control_scores": [gates["random_mrr"], gates["scramble_mrr"]],
         "headline_threshold": gates["main_mrr"], "higher_is_pass": True, "margin": 0.01, "n_repeats_min": 2,
         "control_name": "RANDOM_SCRAMBLE_below_MAIN",
         "extra": "RANDOM + relation-scrambled must sit below MAIN"},
        {"kind": "guard_baseline_valid", "baseline_score": gates["pop_mrr"], "floor_score": gates["random_mrr"],
         "guard_name": "n/a_no_control_beats_baseline_guard_in_this_cell", "baseline_name": "POP",
         "floor_name": "RANDOM", "eps": 0.02},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arena_fires", "scramble_controlled", "arms_differ", "partial_rho_in_bounds",
                                    "perm_p_in_bounds", "mode_a_traversal_correct"],
         "exercised_gates": ["arena_fires", "scramble_controlled", "arms_differ", "partial_rho_in_bounds",
                             "perm_p_in_bounds", "mode_a_traversal_correct"],
         "extra": "verdict_from_gates verdict=%s at self-test scale" % v},
    ], run_mode="self_test")

    out.update(arena_fires=arena_fires, scramble_controlled=scramble_controlled, arms_differ=arms_differ,
               partial_rho_in_bounds=rho_ok, perm_p_in_bounds=p_ok, mode_a_fires=mode_a_fires,
               mode_a_inert_when_empty=mode_a_inert_when_empty, validity_preflight_ok=bool(vp_ok),
               exercised_entrypoints=sorted(exercised))
    ok = bool(arena_fires and scramble_controlled and arms_differ and p_ok and rho_ok
              and mode_a_fires and mode_a_inert_when_empty)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

SMOKE_CFG = dict(k=12, epochs=40, n_neg=32, batch=4096, neg_chunk=None, seeds=[7])
FULL_CFG = dict(k=16, epochs=150, n_neg=64, batch=8192, neg_chunk=16, ckpt_every=20, seeds=[7, 13])


def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue in ("remote_cpu_queue", "local_cpu_queue"))
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]) if run_mode != "self_test" else None
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s" % (device, torch.cuda.is_available(), run_mode, seeds))

    st_ok, st_res = self_test()
    _log("self_test ok=%s arena_fires=%s scramble_controlled=%s arms_differ=%s mode_a_fires=%s vp_ok=%s" %
         (st_ok, st_res.get("arena_fires"), st_res.get("scramble_controlled"), st_res.get("arms_differ"),
          st_res.get("mode_a_fires"), st_res.get("validity_preflight_ok")))
    _hb("self_test", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELF_TEST_FAILED (arena/scramble/arms/partial-rho/perm-p/mode-a traversal): %s"
                        % st_res.get("fail", st_res),
            summary="self-test failed", elapsed_s=time.perf_counter() - t_start, self_test=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS reachability_predicts_relational_failure: real fit/score/RR + reachability tool "
                        "(k-hop mass, distance-to-hub, partial-Spearman, stratified permutation) + mode-(a) measured-"
                        "reachability traversal all exercised; arena fires; scramble collapses; p/rho in bounds",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, self_test=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    data_path = os.path.join(_REPO, DATA_REL)
    if not os.path.isfile(data_path):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="active partition file absent: %s" % data_path, summary="data missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    triples = load_induced_triples(BUCKET_MAP, data_path)
    _log("loaded induced triples=%d" % len(triples))

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            res = run_one_seed(triples, BUCKET_MAP, cfg, device, seed, ckpt_dir=out_dir)
            if res.get("empty") or res.get("n_query", 0) < 1:
                raise RuntimeError("no query edges produced for seed=%d" % seed)
            sigset = set(res.get("arm_sigs", {}).values())
            if len(sigset) < 3:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            d = res["diagnostic"]
            _log("seed=%d N=%d n_train=%d n_query=%d n_ent=%d MAIN=%s RANDOM=%s SCRAMBLE=%s | "
                 "partial_rho(khop|deg)=%s perm_p=%s raw=%s deg_only=%s (%.1fs)" %
                 (seed, res["N"], res["n_train"], res["n_query"], res["n_entities"], _fmt(res["main_mrr"]),
                  _fmt(res["random_mrr"]), _fmt(res["scramble_mrr"]), _fmt(d["partial_rho_khop"]),
                  _fmt(d["perm_p_khop"]), _fmt(d["raw_spearman_khop"]), _fmt(d["spearman_degree_only"]),
                  time.time() - ts))
            _hb("seed", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start, seed_failures=seed_failures,
            self_test=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = verdict_from_gates(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, self_test=st_res, seed_failures=seed_failures,
                   n_induced_triples=len(triples))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="alias for --run-mode smoke (queue_add.py gate convention)")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if run_mode is None:
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "smoke", "full"):
            run_mode = env_mode
        else:
            raise ValueError("no --run-mode / --self-test / HDLAB_RUN_MODE specified; explicit run_mode required "
                             "(no silent self_test default per RUN_MODE VERIFICATION discipline)")
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
