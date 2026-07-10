"""RUNG-2b LOOP-CLOSER: does GROUNDING the consolidation geometry with fused MEASURED attributes fix the ORIGINAL
inductive-RELATIONAL-inference failure DEGREE-INVARIANTLY -- turning the additive code's LOW-degree tail-collapse
(LOW d=-0.040 MEASURED@data/exp_grounding_additive_geometric_degree_control_v1/metrics.json:gates.strata.LOW.
delta_transe_discrete) into a POSITIVE tail lift?

THE ARC. "Make relational real" started from a wall: inductive RELATIONAL inference (predict a held-out EDGE's target,
degree-invariantly). The additive/geometric code did it DEGREE-DEPENDENTLY -- it rode popularity (HIGH d=+0.264) and
COLLAPSED on the rare tail (LOW d=-0.040) -> HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT. Separately, GROUNDING now works
for ATTRIBUTE prediction: fusing measured senses (concreteness + sensory-modality + AoA) diffused over the ConceptNet
graph improves held-out attribute prediction DEGREE-UNIFORMLY (grounding_multiattribute_fusion_v1: ground_gap 0.079,
strata LOW/MID/HIGH all positive, LOSO-robust MEASURED_MECHANISM). THE FINISH LINE: does grounding the GEOMETRY (anchor
consolidation to the fused measured attributes) TRANSFER to RELATIONAL inference degree-invariantly? If yes, grounding is
the lever the code-swaps were not, and the arc closes. If no, grounding predicts attributes but does NOT transfer to
relational inference -- a real, bounded negative (attribute-grounding != relational-inference).

WHY NOT GUARANTEED (carried honestly): the Pillar-2 router negative taught us low-rank/geometric generalization helps
SMOOTH tasks (attribute prediction) but FAILS high-capacity DISCRETE addressing (routing at scale). Relational inference
(predict 1 correct target among many candidates) sits BETWEEN. This cell MEASURES where it lands -- it does NOT assume
grounding transfers. HARD_FAIL is a valid, valuable bounded finding.

THE TEST (reuses the retest's EXACT relational apparatus -- clean apples-to-apples rematch vs the code's failure):
COMPLETABLE reach@1 (filtered Hits@1 on held-out completable directed triples), degree strata LOW/MID/HIGH by true-tail
visible degree, degree-only POPULARITY baseline, RANDOM (codes-necessary) + ORACLE (oracle-leak / setup-works) controls.
All from experiments.exp_grounding_additive_geometric_degree_control_retest_v1, imported VERBATIM (rt.*).

THE GROUNDED GEOMETRY (reuses the VALIDATED diffusion-with-restart engine, eng.*, from the consolidation loop cell):
per entity a STRUCTURAL channel (structural_features of the visible typed graph; degree-biased) + an exterior channel;
build the cross-channel AGREEMENT kNN graph (survives only where BOTH channels concur -> filters degree hubs); diffuse
the anchor with normalized-Laplacian RESTART (anti-collapse, degree-balancing); FREEZE the settled entity codes; fit
additive relation offsets R_r on visible edges; score held-out tails by -||E_h + R_r - E_t||_1. This is the engine's
CONS mechanic -- the ONLY thing this cell changes is the exterior channel identity, which is exactly the ablation.

ARMS (all learn from the VISIBLE typed graph only unless noted; PAIRED: same held-out split + completable subset +
candidate negatives + degree strata per seed):
  GROUNDED    (MECHANISM): exterior channel = the fused independence-selected MEASURED attributes (concreteness +
              sensory-modality + AoA, projected). agreement(struct, attr); anchor = cat(struct, attr); settle; read off.
  UNGROUNDED  (ablation / graph-alone reference): exterior channel = a SECOND STRUCTURAL VIEW (struct2). agreement(
              struct, struct2); anchor = cat(struct, struct2). Dimension-matched to GROUNDED; the ONLY difference is the
              exterior half is graph-structure, not measured attributes -> consolidation-alone, no grounding. GROUNDED
              minus UNGROUNDED == the grounding lift == the decisive ablation (grounding must be LOAD-BEARING).
  SCRAMBLED   (must-fail values control): exterior channel = the SAME measured attributes with values PERMUTED across
              concepts. Dimension-matched to GROUNDED; if SCRAMBLED reproduces the lift, the lift is dimensionality /
              structure, NOT the attribute VALUES -> HARD_FAIL_SCRAMBLE_LAUNDERS.
  ONESHOT_CODE (the failed additive code, direct contrast): TransE trained one-shot from scratch (entity+relation).
              Reproduces the code's degree-dependent result on this graph (the LOW=-0.040 reference).
  POPULARITY_DEGREE (confound baseline): score(candidate) = visible-graph degree(candidate). No geometry.
  RANDOM_CODES (null / codes-necessary): untrained TransE codes -> chance floor.
  TRANSE_TRANSDUCTIVE (oracle / must-fire, oracle-leak check): TransE trained WITH held-out visible; must recover >>
              random or the setup is broken (INCONCLUSIVE).

PRIMARY METRIC (pre-registered, identical to the retest): COMPLETABLE reach@1, aggregate + per degree stratum, per arm.
THE KEY NUMBER (the finish line): LOW-stratum grounding lift = reach@1[GROUNDED, LOW] - reach@1[UNGROUNDED, LOW]. Does it
go POSITIVE where the additive code's LOW gap went NEGATIVE (-0.040)?

DISCRIMINATOR (pre-registered; BOTH bands numeric BEFORE the run; the LOW-stratum-positive decision is NOT loosened and
the ablation control is NOT dropped -- Director contract):
  HARD_PASS_GROUNDING_CLOSES_THE_LOOP (ALL must hold; the arc closes):
      NOT collapsed (grounded eff_rank > COLLAPSE_RANK_FLOOR AND rep_var > COLLAPSE_VAR_FLOOR)
    AND aggregate lift ok: (GROUNDED - UNGROUNDED) reach@1 >= GROUND_MARGIN
    AND tail SURVIVES + LOW POSITIVE: (GROUNDED - UNGROUNDED) >= STRAT_MARGIN in BOTH LOW and MID strata (>=MIN_STRAT_Q
        each) -> the LOW-degree tail grounding lift is POSITIVE (the finish-line number, vs the code's -0.040)
    AND grounding is LOAD-BEARING vs values (scramble control): (SCRAMBLED - UNGROUNDED) <= SCRAMBLE_MAX AND
        (GROUNDED - SCRAMBLED) >= SCRAMBLE_BEAT
    AND popularity does NOT recover it: (GROUNDED - POP) >= POP_GAP AND pop/grounded <= POP_RECOVER_FRAC_MAX
  HARD_FAIL_GROUNDING_DOESNT_TRANSFER (grounding predicts attributes but not relations -- a valid bounded negative):
      NOT collapsed AND (
        ties ungrounded: (GROUNDED - UNGROUNDED) <= TIE_EPS        [no transfer]
     OR tail collapse: (GROUNDED - UNGROUNDED) <= TIE_EPS in LOW or MID [still degree-dependent]
     OR popularity recovers: (GROUNDED - POP) <= TIE_EPS OR pop/grounded >= POP_RECOVER_FRAC_HI
     OR scramble launders: (SCRAMBLED - UNGROUNDED) >= GROUND_MARGIN OR (GROUNDED - SCRAMBLED) <= 0 )
  HARD_FAIL_CONSOLIDATION_COLLAPSED: grounded geometry collapsed (eff_rank / rep_var floors).
  MIDDLE_BAND_PARTIAL: otherwise (lift present but sub-material / tail ambiguous / scramble ambiguous).
Gating precondition INCONCLUSIVE arms: enough completable, negatives_valid (random <= RANDOM_CEIL), oracle_fires.

SELF-TEST (planted worlds; the grounding-transfer discriminators must FIRE):
  (a) GROUNDED-SIGNAL-TRANSFERS: a clustered grid-translation world (degree-invariant relations) whose visible STRUCTURE
      is degree-contaminated (noise hub edges blur structural_features) while the measured ATTRIBUTE is a CLEAN cluster
      centroid. GROUNDED (struct, attr) de-biases the agreement graph -> recovers held-out translations (>= 5x chance),
      BEATS UNGROUNDED (struct, struct2 -- both blurred) by >= a margin, and the LOW-degree stratum lift is POSITIVE.
  (b) ABLATED-NO-TRANSFER: UNGROUNDED does NOT recover the extra signal (grounded - ungrounded >= margin -- same test).
  (c) SCRAMBLED-NO-TRANSFER: permuting the attribute across concepts kills the lift (scrambled - ungrounded <= small).
  (d) COLLAPSE caught: a near-constant code trips the representation-variance floor; the healthy grounded code passes.
  Saturation-vacuous guard: the must-fail controls (ungrounded-no-recover, scrambled-no-transfer) FAIL at self-test scale
  by construction, so a green self-test cannot rubber-stamp a degenerate FULL.

## Compute architecture
class: (c) mixed / CPU-fast. Grounded/ungrounded/scrambled geometries = dense [n,n] cosine + topk agreement + a few
normalized-Laplacian diffusion matmuls ([n,n]@[n,2*dim]) at n<=3300, 2*dim=128 -> seconds each on CPU; relation-offset
fit + one-shot/oracle TransE are vectorized margin-rank over edge mini-batches (no python-loop matmul). Storage strategy:
SHARDED (each entity its own settled code + offset vector; no bundling). GPU gives marginal benefit at this scale; the
FULL routes to remote_cpu_queue (CPU-fast, keeps the laptop free per the SMOKE-ONLY-LOCAL lock). Self-test is the local
discriminator gate; smoke is the local run-through; FULL (3 seeds, n=5000 target) is canonical on remote_cpu_queue.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): >= 5 distinct held-out score signatures among the 7 arms.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace; write_partial per seed).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: filtered Hits@1 chance floor = 1/(N_RANK_NEG+1) ~ 0.01 (THEORETICAL). HARD_PASS needs GROUNDED-UNGROUNDED >=
#   0.03 aggregate AND LOW+MID >= 0.02 (>> tie-eps 0.0); self-test planted arm demonstrates >= 0.25 reachable.
#   discriminator_reachability: OK.
# - baseline_in_band: RANDOM_CODES is the anti-triviality null (<= RANDOM_CEIL 0.15); ORACLE the must-fire (>= rand+0.15);
#   UNGROUNDED is the ablation reference (measured, not gated as a null); POP the confound baseline (measured).
# - discriminator survives scale: consolidation/agreement/rel-fit params (CONS_KNN/PASSES/ALPHA/REL_EPOCHS/DIM) SHARED
#   across self-test/smoke/full; the transfer discriminator (per-stratum grounding lift + scramble control) fires in the
#   planted self-test; the real-graph transfer outcome is the OPEN measurement.
# - HARD_PASS strictly above floor: GROUNDED-UNGROUNDED >= 0.03 aggregate AND both tail strata >= 0.02.
# - HP_SCOPE: the transfer gate applies to GROUNDED vs UNGROUNDED + POP, with SCRAMBLED as a must-fail control. RANDOM=
#   null; ORACLE=must-fire; ONESHOT_CODE=the failed additive code (reported, degree-dependent, the -0.040 contrast).
# - positive_control (Gate D): TRANSE_TRANSDUCTIVE reproduces the transductive-KGE result (>> random); ONESHOT_CODE
#   reproduces the retest's degree-dependent additive result on the same 30% split (rematch sanity).
# - sweep axis: ARM (method) x seed x degree-stratum; EXPECTED_N_UNITS = n_seeds; each seed asserts >= 5 distinct arms.
# - per-unit failure-class instrumentation (no bare except; per-arm try/except records failure_class).
# - calibration_check: default_ok_for_this_regime. HELDOUT_FRAC=0.30 + completable-subset inherited from the retest;
#   degree tertiles are DATA-driven quantiles; consolidation/KGE hyperparams pre-registered (reused from the engine cell).
# - PAIRED: all arms share the identical held-out split + completable subset + candidate negatives + degree strata.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm/per-stratum flush prints).
"""

import argparse
import hashlib
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

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import load_typed_cn_subgraph  # noqa: E402
# Reuse the retest harness VERBATIM (apples-to-apples rematch): split, completable, degree, KGE, ranking, strata.
import experiments.exp_grounding_additive_geometric_degree_control_retest_v1 as rt  # noqa: E402
# Reuse the VALIDATED diffusion-with-restart consolidation engine (agreement, consolidate, fit_relation_offsets, floors).
import experiments.exp_grounding_consolidation_loop_degree_invariant_v1 as eng  # noqa: E402
# Reuse the fusion cell's data acquisition + candidate columns + independence selection (the grounding source).
import experiments.exp_grounding_multiattribute_fusion_v1 as fus  # noqa: E402

ANCHOR_NAME = "grounding_rung2_loop_closer_v1"

# ---- Arm names ----
GROUNDED = "GROUNDED"                    # MECHANISM: consolidation anchored to fused measured attributes
UNGROUNDED = "UNGROUNDED"                # ablation / graph-alone reference: 2nd structural view (dim-matched)
SCRAMBLED = "SCRAMBLED"                  # must-fail: attribute values permuted across concepts (dim-matched)
ONESHOT = "ONESHOT_CODE"                 # the failed additive code (one-shot TransE), the -0.040 contrast
POP = "POPULARITY_DEGREE"                # degree-only popularity baseline (no geometry)
RANDOM = "RANDOM_CODES"                  # null: untrained TransE codes (codes-necessary)
ORACLE = "TRANSE_TRANSDUCTIVE"           # oracle / must-fire (oracle-leak check)
ALL_ARMS = [GROUNDED, UNGROUNDED, SCRAMBLED, ONESHOT, POP, RANDOM, ORACLE]

STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (picked BEFORE the run; the LOW-stratum-positive decision + ablation are load-bearing) ----
GROUND_MARGIN = 0.03          # HARD_PASS aggregate: (GROUNDED - UNGROUNDED) reach@1 >= this (material grounding lift)
STRAT_MARGIN = 0.02           # HARD_PASS tail survival: (GROUNDED - UNGROUNDED) >= this in BOTH LOW and MID (LOW POSITIVE)
TIE_EPS = 0.0                 # HARD_FAIL: (GROUNDED - UNGROUNDED) <= this aggregate OR in a tail stratum (no transfer)
SCRAMBLE_MAX = 0.02           # HARD_PASS: (SCRAMBLED - UNGROUNDED) <= this (scramble does NOT reproduce the lift)
SCRAMBLE_BEAT = 0.02          # HARD_PASS: (GROUNDED - SCRAMBLED) >= this (grounding beats scrambled -> it is the VALUES)
POP_GAP = 0.03                # HARD_PASS: (GROUNDED - POP) reach@1 >= this
POP_RECOVER_FRAC_MAX = 0.60   # HARD_PASS: popularity recovers <= this fraction of GROUNDED reach
POP_RECOVER_FRAC_HI = 0.80    # HARD_FAIL: popularity recovers >= this fraction of GROUNDED reach
RANDOM_CEIL = 0.15            # anti-triviality: RANDOM reach@1 <= this
ORACLE_FIRE_MARGIN = 0.15     # discriminator-fires: ORACLE must beat RANDOM by this
MIN_STRAT_Q = 40              # min queries in a tail stratum to assess its margin
MIN_HELDOUT_COMPLETABLE = 60

# ---- Held-out construction + hyperparams (inherited from the retest / engine cell; NOT tuned on real data) ----
HELDOUT_FRAC = eng.HELDOUT_FRAC          # 0.30
N_RANK_NEG = eng.N_RANK_NEG              # 99 filtered negatives per positive
MAX_RANK_QUERIES = eng.MAX_RANK_QUERIES  # 1500
DIM = 64                                 # per-channel feature dim; anchor dim = 2*DIM = 128
STRUCT_HOP2 = 1.0                        # 2nd structural view hop weight (distinct from struct hop 0.5)

# ---- Attribute-channel independence selection thresholds (reused from the fusion cell's gate) ----
# fus.REDUNDANT_R (0.70 marginal-|r| pruning) + fus.MIN_TARGET_R (0.20) select the non-redundant "senses".

# Config profiles. Consolidation/agreement/rel-fit params SHARED across self-test/smoke/full (survives-scale).
SELFTEST_CFG = dict(seeds=[7], n_nodes=400, kge_dim=DIM, kge_epochs=350, kge_batch=512, kge_lr=0.01)
SMOKE_CFG = dict(seeds=[7, 13], n_nodes=1800, kge_dim=DIM, kge_epochs=350, kge_batch=512, kge_lr=0.01)
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=5000, kge_dim=DIM, kge_epochs=500, kge_batch=1024, kge_lr=0.01)

# Candidate attribute columns + separators (reused from the fusion cell).
_SEPS = {"conc": "\t", "warriner": ",", "lancaster": ",", "aoa": ","}


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
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
# Covered typed-subgraph builder: concreteness-covered + connected nodes, TYPED edges preserved, attributes joined.
# (Restricts the relational task to the grounding testbed's covered node set -> the selected attributes have near-full
# coverage there, so grounding is tested where the measured attribute EXISTS; no mean-mask degeneracy.)
# ---------------------------------------------------------------------------

def build_covered_typed_subgraph(n_nodes, base_seed):
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(n_nodes, base_seed)
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels, dtype=np.int64)
    conc_map = fus._load_col_map("conc", "Conc.M", "\t")

    def _lookup(cm, w):
        k = fus._norm_word(w)
        if k in cm:
            return cm[k]
        k2 = k.replace(" ", "")
        return cm[k2] if k2 in cm else np.nan

    y_conc = np.array([_lookup(conc_map, w) for w in node_words], dtype=np.float64)
    cov = np.isfinite(y_conc)
    me = cov[edges[:, 0]] & cov[edges[:, 1]] & (edges[:, 0] != edges[:, 1])
    e2 = edges[me]
    r2 = rels[me]
    used = np.unique(e2)
    remap = {int(o): i for i, o in enumerate(used)}
    words = [node_words[int(o)] for o in used]
    m = len(used)
    edges_sub = np.empty_like(e2)
    for k in range(e2.shape[0]):
        edges_sub[k, 0] = remap[int(e2[k, 0])]
        edges_sub[k, 1] = remap[int(e2[k, 1])]

    # Join all candidate attribute columns over the covered node set.
    col_maps = {name: fus._load_col_map(ds, col, _SEPS[ds]) for name, ds, col in fus.CANDIDATES}
    K = len(fus.CANDIDATES)
    Y = np.full((m, K), np.nan, dtype=np.float64)
    for ci, (name, ds, col) in enumerate(fus.CANDIDATES):
        cm = col_maps[name]
        for i, w in enumerate(words):
            Y[i, ci] = _lookup(cm, w)
    present = np.isfinite(Y)
    attr_names = [c[0] for c in fus.CANDIDATES]
    cover_frac = {attr_names[ci]: float(present[:, ci].mean()) for ci in range(K)}
    n_rels = int(r2.max()) + 1 if r2.shape[0] > 0 else 1
    meta2 = dict(n_subgraph=len(node_ids), n_covered_connected=m, n_typed_edges=int(edges_sub.shape[0]),
                 n_rels=n_rels, attr_coverage=cover_frac, coverage_frac_concreteness=float(cov.mean()))
    return edges_sub, r2.astype(np.int64), words, Y, present, attr_names, meta2


def attribute_features(Y, sel_idx, dim, seed, device, scramble=False, scramble_seed=0):
    """Per-entity exterior feature [n, dim] from the selected measured attributes: z-scored (missing -> observed mean),
    random-projected to dim, L2-normalized rows. scramble=True permutes each column across concepts (values control)."""
    n = Y.shape[0]
    cols = []
    for ci in sel_idx:
        v = Y[:, ci].astype(np.float64).copy()
        obs = np.isfinite(v)
        mu = float(v[obs].mean()) if obs.sum() > 0 else 0.0
        sd = float(v[obs].std()) + 1e-9 if obs.sum() > 1 else 1.0
        v[~obs] = mu
        v = (v - mu) / sd
        if scramble:
            v = v[np.random.default_rng(scramble_seed * 131 + ci).permutation(n)]
        cols.append(v.astype(np.float32))
    Z = np.stack(cols, axis=1) if cols else np.zeros((n, 1), dtype=np.float32)  # [n, Ksel]
    g = torch.Generator(device="cpu").manual_seed(seed + 97)
    P = torch.randn(Z.shape[1], dim, generator=g).numpy().astype(np.float32)
    F = torch.from_numpy(Z @ P).to(device)
    return torch.nn.functional.normalize(F, dim=1)


# ---------------------------------------------------------------------------
# One grounded/ungrounded/scrambled geometry: agreement(struct, exterior) -> diffuse-restart(anchor=cat) -> fit offsets.
# ---------------------------------------------------------------------------

def build_geometry(struct, exterior, vis_tri, n, n_rels, cfg, seed, device, tag):
    """anchor = cat(struct, exterior) [n, 2*DIM]; agreement graph from the two channels; settle; freeze; fit offsets."""
    E0 = torch.cat([struct, exterior], dim=1)
    a_src, a_dst = eng.agreement_edges(struct, exterior, eng.CONS_KNN, device)
    E = eng.consolidate(a_src, a_dst, E0, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, tag)
    R = eng.fit_relation_offsets(E, vis_tri, n_rels, E.shape[1], eng.REL_EPOCHS, eng.REL_BATCH,
                                 cfg["kge_lr"], seed, device)
    return E, R, eng._effective_rank(E), eng._rep_variance(E), int(a_src.shape[0])


# ---------------------------------------------------------------------------
# Per-seed run on the covered typed subgraph.
# ---------------------------------------------------------------------------

def run_seed(seed, edges, rels, node_words, Y, sel_idx, cfg, device):
    n = len(node_words)
    n_rels = int(np.asarray(rels).max()) + 1
    dim = cfg["kge_dim"]

    vis, hold, tri_all = rt.split_heldout(edges, rels, HELDOUT_FRAC, seed)
    comp = rt.completable_mask(hold, vis, n, n_rels)
    hold_comp = hold[comp]
    n_comp = int(hold_comp.shape[0])
    n_hold = int(hold.shape[0])
    deg_vis = rt.visible_degree(vis, n)
    deg_vis_t = torch.from_numpy(deg_vis.astype(np.float32)).to(device)
    _log("  seed=%d vis_tri=%d hold_tri=%d completable=%d" % (seed, vis.shape[0], n_hold, n_comp))

    rng = np.random.default_rng(seed * 991 + 3)
    if n_comp > MAX_RANK_QUERIES:
        queries = hold_comp[rng.choice(n_comp, size=MAX_RANK_QUERIES, replace=False)]
    else:
        queries = hold_comp
    cand = rt.build_ranking_candidates(queries, tri_all, n, N_RANK_NEG, seed) if queries.shape[0] > 0 \
        else np.zeros((0, N_RANK_NEG + 1), dtype=np.int64)
    strata, (sq1, sq2) = rt.stratify_by_target_degree(queries, deg_vis)

    arms = {}
    arms_strat = {}
    sigs = {}
    failures = []

    def _score_and_store(arm, score_fn):
        try:
            if queries.shape[0] == 0:
                raise RuntimeError("no completable queries")
            sc = score_fn()
            rank = rt._ranks_from_scores(sc)
            h1, h3, h10, mrr = rt._hits_from_ranks(rank)
            arms[arm] = dict(hits1=h1, hits3=h3, hits10=h10, mrr=mrr)
            arms_strat[arm] = rt._per_stratum_hits1(rank.cpu().numpy(), strata)
            sigs[arm] = hashlib.sha256(np.round(sc[:64].detach().cpu().numpy().astype(np.float64), 5)
                                       .tobytes()).hexdigest()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failures.append(dict(arm=arm, failure_class=type(e).__name__, msg=str(e)[:200]))
            arms[arm] = dict(hits1=float("nan"), hits3=float("nan"), hits10=float("nan"), mrr=float("nan"))
            arms_strat[arm] = {s: dict(hits1=float("nan"), n=0) for s in STRATA}
            sigs[arm] = "%s_failed" % arm

    # ---- Channels ----
    struct = eng.structural_features(vis, n, dim, seed, device)                       # graph-structural (degree-biased)
    struct2 = eng.structural_features(vis, n, dim, seed + 1234, device, hop=STRUCT_HOP2)  # 2nd structural view
    attr = attribute_features(Y, sel_idx, dim, seed, device)                          # fused measured attributes
    attr_scr = attribute_features(Y, sel_idx, dim, seed, device, scramble=True, scramble_seed=seed)

    # ---- GROUNDED (mechanism) ----
    Eg, Rg, g_rank, g_var, g_agr = build_geometry(struct, attr, vis, n, n_rels, cfg, seed, device, "[grounded]")
    _score_and_store(GROUNDED, lambda: rt.rank_transe(Eg, Rg, queries, cand, device))

    # ---- UNGROUNDED (graph-alone ablation; dim-matched) ----
    Eu, Ru, u_rank, u_var, u_agr = build_geometry(struct, struct2, vis, n, n_rels, cfg, seed + 5, device, "[ungrounded]")
    _score_and_store(UNGROUNDED, lambda: rt.rank_transe(Eu, Ru, queries, cand, device))

    # ---- SCRAMBLED (must-fail values control; dim-matched) ----
    Es, Rs, s_rank, s_var, s_agr = build_geometry(struct, attr_scr, vis, n, n_rels, cfg, seed + 9, device, "[scrambled]")
    _score_and_store(SCRAMBLED, lambda: rt.rank_transe(Es, Rs, queries, cand, device))

    # ---- ONESHOT_CODE (the failed additive code; one-shot TransE from scratch) ----
    Et, Rt = rt.train_kge(n, n_rels, vis, dim, cfg["kge_epochs"], cfg["kge_batch"], cfg["kge_lr"],
                          seed, device, "transe")
    _score_and_store(ONESHOT, lambda: rt.rank_transe(Et, Rt, queries, cand, device))

    # ---- POPULARITY (degree-only) ----
    _score_and_store(POP, lambda: rt.rank_popularity(deg_vis_t, queries, cand, device))

    # ---- RANDOM (null / codes-necessary) ----
    Er = rt._renorm_rows(rt._init_emb(n, dim, seed + 101, device, 6.0 / (dim ** 0.5)), cap=1.0)
    Rr = rt._init_emb(n_rels, dim, seed + 102, device, 6.0 / (dim ** 0.5))
    _score_and_store(RANDOM, lambda: rt.rank_transe(Er, Rr, queries, cand, device))

    # ---- ORACLE (must-fire; oracle-leak check): TransE trained WITH held-out visible ----
    Eo, Ro = rt.train_kge(n, n_rels, tri_all, dim, cfg["kge_epochs"], cfg["kge_batch"], cfg["kge_lr"],
                          seed, device, "transe")
    _score_and_store(ORACLE, lambda: rt.rank_transe(Eo, Ro, queries, cand, device))

    for arm in ALL_ARMS:
        a = arms[arm]
        st = arms_strat[arm]
        _log("  seed=%d %-18s hits1=%s (LOW=%s[n=%d] MID=%s[n=%d] HIGH=%s[n=%d]) mrr=%s" % (
            seed, arm, _fmt(a["hits1"]),
            _fmt(st["LOW"]["hits1"]), st["LOW"]["n"], _fmt(st["MID"]["hits1"]), st["MID"]["n"],
            _fmt(st["HIGH"]["hits1"]), st["HIGH"]["n"], _fmt(a["mrr"])))
    # THE finish-line numbers, logged per seed.
    for sn in STRATA:
        gh = arms_strat[GROUNDED][sn]["hits1"]
        uh = arms_strat[UNGROUNDED][sn]["hits1"]
        oh = arms_strat[ONESHOT][sn]["hits1"]
        _log("    seed=%d stratum %-4s GROUNDED=%s UNGROUNDED=%s lift(G-U)=%s  ONESHOT=%s lift(G-code)=%s [n=%d]"
             % (seed, sn, _fmt(gh), _fmt(uh), _fmt(gh - uh), _fmt(oh), _fmt(gh - oh),
                arms_strat[GROUNDED][sn]["n"]))
    _log("  seed=%d degree tertiles: q1=%.1f q2=%.1f | grounded eff_rank=%.1f rep_var=%.3f agr[g/u/s]=%d/%d/%d"
         % (seed, sq1, sq2, g_rank, g_var, g_agr, u_agr, s_agr))

    return dict(seed=seed, arms=arms, arms_strat=arms_strat, arm_sigs=sigs,
                grounded_eff_rank=g_rank, grounded_rep_var=g_var,
                ungrounded_eff_rank=u_rank, scrambled_eff_rank=s_rank,
                n_agr_grounded=g_agr, n_agr_ungrounded=u_agr, n_agr_scrambled=s_agr,
                deg_tertiles=[sq1, sq2], n_completable=n_comp, n_heldout=n_hold, n_queries=int(queries.shape[0]),
                n_visible_tri=int(vis.shape[0]), failures=failures, kge_dim=dim, n_rels=n_rels)


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def aggregate_and_verdict(per_seed, sel_info, meta):
    def A(arm, key):
        return rt._nm([m["arms"][arm][key] for m in per_seed if arm in m["arms"]])

    g1 = A(GROUNDED, "hits1"); u1 = A(UNGROUNDED, "hits1"); s1 = A(SCRAMBLED, "hits1")
    o1 = A(ONESHOT, "hits1"); pop1 = A(POP, "hits1"); rand1 = A(RANDOM, "hits1"); orac1 = A(ORACLE, "hits1")
    n_comp = int(rt._nm([m["n_completable"] for m in per_seed]))
    n_hold = int(rt._nm([m["n_heldout"] for m in per_seed]))
    g_rank = rt._nm([m["grounded_eff_rank"] for m in per_seed])
    g_var = rt._nm([m["grounded_rep_var"] for m in per_seed])

    lift = (g1 - u1) if (g1 == g1 and u1 == u1) else float("nan")
    scr_lift = (s1 - u1) if (s1 == s1 and u1 == u1) else float("nan")
    g_minus_scr = (g1 - s1) if (g1 == g1 and s1 == s1) else float("nan")
    g_minus_pop = (g1 - pop1) if (g1 == g1 and pop1 == pop1) else float("nan")
    pop_recover_frac = (pop1 / g1) if (g1 == g1 and g1 > 1e-9 and pop1 == pop1) else float("nan")

    strat = {}
    for sn in STRATA:
        g_h, g_n = rt._strat_agg(per_seed, GROUNDED, sn)
        u_h, _un = rt._strat_agg(per_seed, UNGROUNDED, sn)
        s_h, _sn = rt._strat_agg(per_seed, SCRAMBLED, sn)
        o_h, _on = rt._strat_agg(per_seed, ONESHOT, sn)
        p_h, _pn = rt._strat_agg(per_seed, POP, sn)
        lift_gu = (g_h - u_h) if (g_h == g_h and u_h == u_h) else float("nan")
        lift_gc = (g_h - o_h) if (g_h == g_h and o_h == o_h) else float("nan")
        strat[sn] = dict(grounded_hits1=g_h, ungrounded_hits1=u_h, scrambled_hits1=s_h, oneshot_hits1=o_h,
                         pop_hits1=p_h, lift_grounded_ungrounded=lift_gu, lift_grounded_code=lift_gc, n=g_n)
    low_lift = strat["LOW"]["lift_grounded_ungrounded"]
    mid_lift = strat["MID"]["lift_grounded_ungrounded"]
    high_lift = strat["HIGH"]["lift_grounded_ungrounded"]
    low_lift_vs_code = strat["LOW"]["lift_grounded_code"]

    # ---- precondition gates ----
    enough = bool(n_comp >= MIN_HELDOUT_COMPLETABLE)
    negatives_valid = bool(rand1 == rand1 and rand1 <= RANDOM_CEIL)
    oracle_fires = bool(orac1 == orac1 and rand1 == rand1 and orac1 >= rand1 + ORACLE_FIRE_MARGIN)
    collapsed = bool((g_rank == g_rank and g_rank <= eng.COLLAPSE_RANK_FLOOR)
                     or (g_var == g_var and g_var <= eng.COLLAPSE_VAR_FLOOR))

    # ---- transfer decision (the pre-registered core: LOW-stratum-positive + ablation + scramble; NOT loosened) ----
    aggregate_lift_ok = bool(lift == lift and lift >= GROUND_MARGIN)

    def _tail_ok(sn):
        s = strat[sn]
        return bool(s["n"] >= MIN_STRAT_Q and s["lift_grounded_ungrounded"] == s["lift_grounded_ungrounded"]
                    and s["lift_grounded_ungrounded"] >= STRAT_MARGIN)

    def _tail_collapse(sn):
        s = strat[sn]
        return bool(s["n"] >= MIN_STRAT_Q and s["lift_grounded_ungrounded"] == s["lift_grounded_ungrounded"]
                    and s["lift_grounded_ungrounded"] <= TIE_EPS)

    tail_survives = bool(_tail_ok("LOW") and _tail_ok("MID"))
    low_positive = bool(low_lift == low_lift and low_lift > TIE_EPS)
    tail_collapses = bool(_tail_collapse("LOW") or _tail_collapse("MID"))
    scramble_ok = bool(scr_lift == scr_lift and scr_lift <= SCRAMBLE_MAX
                       and g_minus_scr == g_minus_scr and g_minus_scr >= SCRAMBLE_BEAT)
    scramble_launders = bool((scr_lift == scr_lift and scr_lift >= GROUND_MARGIN)
                             or (g_minus_scr == g_minus_scr and g_minus_scr <= 0.0))
    pop_not_recovering = bool(g_minus_pop == g_minus_pop and g_minus_pop >= POP_GAP
                              and pop_recover_frac == pop_recover_frac and pop_recover_frac <= POP_RECOVER_FRAC_MAX)
    pop_recovers = bool((g_minus_pop == g_minus_pop and g_minus_pop <= TIE_EPS)
                        or (pop_recover_frac == pop_recover_frac and pop_recover_frac >= POP_RECOVER_FRAC_HI))
    ties_ungrounded = bool(lift == lift and lift <= TIE_EPS)

    grounding_closes_loop = bool(not collapsed and aggregate_lift_ok and tail_survives and low_positive
                                 and scramble_ok and pop_not_recovering)
    grounding_doesnt_transfer = bool(not collapsed and (ties_ungrounded or tail_collapses or pop_recovers
                                                        or scramble_launders))

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_COMPLETABLE"
    elif not negatives_valid:
        verdict = "INCONCLUSIVE_NEGATIVES_TRIVIAL"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_DID_NOT_FIRE"
    elif collapsed:
        verdict = "HARD_FAIL_CONSOLIDATION_COLLAPSED"
    elif grounding_closes_loop:
        verdict = "HARD_PASS_GROUNDING_CLOSES_THE_LOOP"
    elif grounding_doesnt_transfer:
        verdict = "HARD_FAIL_GROUNDING_DOESNT_TRANSFER"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_TRANSFER_AMBIGUOUS"

    verdict_msg = (
        "%s || COMPLETABLE reach@1: GROUNDED=%.3f UNGROUNDED=%.3f SCRAMBLED=%.3f ONESHOT=%.3f POP=%.3f RANDOM=%.3f "
        "ORACLE=%.3f || lift(G-U)=%s scr_lift(S-U)=%s G-SCR=%s G-POP=%s pop_recover_frac=%s || "
        "STRATA lift(G-U) [n]: LOW=%s[%d] MID=%s[%d] HIGH=%s[%d] (LOW_POSITIVE=%s vs code_LOW=-0.040; LOW lift vs code "
        "G-ONESHOT=%s) || "
        "STRATA G/U/ONESHOT: LOW=%.3f/%.3f/%.3f MID=%.3f/%.3f/%.3f HIGH=%.3f/%.3f/%.3f || "
        "grounded eff_rank=%.1f rep_var=%.3f collapsed=%s || "
        "agg_lift(>=%.2f)=%s tail_survives(LOW&MID>=%.2f)=%s low_positive=%s scramble_ok(S-U<=%.2f & G-S>=%.2f)=%s "
        "pop_not_recovering=%s || HARD_PASS(loop_closes)=%s HARD_FAIL(no_transfer)=%s || "
        "GATES: enough(%d>=%d)=%s neg_valid(rand<=%.2f)=%s oracle_fires=%s || selected=%s(n=%d) || "
        "n_hold=%d nodes=%d E=%d seeds=%d run=%s" % (
            verdict, g1, u1, s1, o1, pop1, rand1, orac1,
            _fmt(lift), _fmt(scr_lift), _fmt(g_minus_scr), _fmt(g_minus_pop), _fmt(pop_recover_frac),
            _fmt(low_lift), strat["LOW"]["n"], _fmt(mid_lift), strat["MID"]["n"], _fmt(high_lift), strat["HIGH"]["n"],
            low_positive, _fmt(low_lift_vs_code),
            strat["LOW"]["grounded_hits1"], strat["LOW"]["ungrounded_hits1"], strat["LOW"]["oneshot_hits1"],
            strat["MID"]["grounded_hits1"], strat["MID"]["ungrounded_hits1"], strat["MID"]["oneshot_hits1"],
            strat["HIGH"]["grounded_hits1"], strat["HIGH"]["ungrounded_hits1"], strat["HIGH"]["oneshot_hits1"],
            g_rank, g_var, collapsed,
            GROUND_MARGIN, aggregate_lift_ok, STRAT_MARGIN, tail_survives, low_positive,
            SCRAMBLE_MAX, SCRAMBLE_BEAT, scramble_ok, pop_not_recovering,
            grounding_closes_loop, grounding_doesnt_transfer,
            n_comp, MIN_HELDOUT_COMPLETABLE, enough, RANDOM_CEIL, negatives_valid, oracle_fires,
            ",".join(sel_info.get("selected", [])), sel_info.get("n_selected", -1),
            n_hold, meta.get("n_covered_connected", -1), meta.get("n_typed_edges", -1), len(per_seed),
            "full" if len(per_seed) >= 3 else "smoke"))

    gates = dict(
        verdict=verdict,
        arms={a: {k: A(a, k) for k in ("hits1", "hits3", "hits10", "mrr")} for a in ALL_ARMS},
        strata=strat,
        cg=dict(grounded_hits1=g1, ungrounded_hits1=u1, scrambled_hits1=s1, oneshot_hits1=o1,
                pop_hits1=pop1, random_hits1=rand1, oracle_hits1=orac1,
                lift_grounded_ungrounded=lift, scramble_lift=scr_lift, grounded_minus_scrambled=g_minus_scr,
                grounded_minus_pop=g_minus_pop, pop_recover_frac=pop_recover_frac,
                low_lift=low_lift, mid_lift=mid_lift, high_lift=high_lift, low_lift_vs_code=low_lift_vs_code,
                low_positive=low_positive, aggregate_lift_ok=aggregate_lift_ok, tail_survives=tail_survives,
                tail_collapses=tail_collapses, scramble_ok=scramble_ok, scramble_launders=scramble_launders,
                pop_not_recovering=pop_not_recovering, pop_recovers=pop_recovers, ties_ungrounded=ties_ungrounded,
                grounded_eff_rank=g_rank, grounded_rep_var=g_var, collapsed=collapsed,
                grounding_closes_loop=grounding_closes_loop, grounding_doesnt_transfer=grounding_doesnt_transfer),
        discriminator_fires=dict(enough_completable=enough, negatives_valid=negatives_valid,
                                 oracle_fires=oracle_fires),
        independence=sel_info,
        n_completable=n_comp, n_heldout=n_hold,
        bands=dict(GROUND_MARGIN=GROUND_MARGIN, STRAT_MARGIN=STRAT_MARGIN, TIE_EPS=TIE_EPS,
                   SCRAMBLE_MAX=SCRAMBLE_MAX, SCRAMBLE_BEAT=SCRAMBLE_BEAT, POP_GAP=POP_GAP,
                   POP_RECOVER_FRAC_MAX=POP_RECOVER_FRAC_MAX, POP_RECOVER_FRAC_HI=POP_RECOVER_FRAC_HI,
                   RANDOM_CEIL=RANDOM_CEIL, ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, MIN_STRAT_Q=MIN_STRAT_Q,
                   HELDOUT_FRAC=HELDOUT_FRAC, MIN_HELDOUT_COMPLETABLE=MIN_HELDOUT_COMPLETABLE, N_RANK_NEG=N_RANK_NEG,
                   CONS_KNN=eng.CONS_KNN, CONS_PASSES=eng.CONS_PASSES, CONS_ALPHA=eng.CONS_ALPHA,
                   REL_EPOCHS=eng.REL_EPOCHS, COLLAPSE_RANK_FLOOR=eng.COLLAPSE_RANK_FLOOR,
                   COLLAPSE_VAR_FLOOR=eng.COLLAPSE_VAR_FLOOR, DIM=DIM),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test: planted worlds; the grounding-transfer discriminators must FIRE.
# ---------------------------------------------------------------------------

ST_CHANCE = 1.0 / (N_RANK_NEG + 1)       # ~0.01 filtered Hits@1 chance floor (THEORETICAL)
ST_CAPTURE_MIN = 5.0 * ST_CHANCE         # grounded must recover >= 5x chance on the clean planted world
ST_TRANSFER_MARGIN = 0.05                # grounded must beat ungrounded by this (aggregate) on the planted world
ST_SCRAMBLE_MAX = 0.05                   # scrambled must NOT reproduce the lift (scrambled - ungrounded <= this)


def _planted_grounding_world(side, per_cell, n_rels, seed, noise_edge_mult=1.0):
    """Clustered grid-translation world (degree-invariant relations) whose visible STRUCTURE is degree-contaminated by
    random cross-cluster hub edges (blur structural_features), while the measured ATTRIBUTE is a CLEAN cluster centroid.
    Returns (n, n_rels, tri_task, noise_edges, ent_cluster, cc). tri_task = the clean relational-inference target edges;
    noise_edges contaminate ONLY the structural feature computation (not the held-out queries)."""
    n, nr, tri_task, ent_cluster, cc = eng._clustered_world(side, per_cell, n_rels, seed)
    g = np.random.default_rng(seed + 71)
    n_noise = int(noise_edge_mult * tri_task.shape[0])
    # hub-biased cross-cluster noise: heads drawn uniformly, tails biased to a few high-degree hubs (popularity contam.)
    hubs = g.choice(n, size=max(2, n // 20), replace=False)
    h = g.integers(0, n, size=n_noise)
    t = g.choice(hubs, size=n_noise)
    r = g.integers(0, nr, size=n_noise)
    keep = h != t
    noise_edges = np.stack([h[keep], r[keep], t[keep]], axis=1).astype(np.int64)
    return n, nr, tri_task, noise_edges, ent_cluster, cc


def _selftest_geom_one(struct, exterior, vis_tri, tri_all, n, n_rels, queries, cand, strata, dim, seed, device):
    """Run one grounded/ungrounded/scrambled geometry on the planted task; return reach@1 + LOW-stratum reach + sig."""
    E0 = torch.cat([struct, exterior], dim=1)
    a_src, a_dst = eng.agreement_edges(struct, exterior, eng.CONS_KNN, device)
    E = eng.consolidate(a_src, a_dst, E0, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "[st]")
    R = eng.fit_relation_offsets(E, vis_tri, n_rels, E.shape[1], min(eng.REL_EPOCHS, 300), 512, 0.01, seed, device)
    sc = rt.rank_transe(E, R, queries, cand, device)
    rank = rt._ranks_from_scores(sc).cpu().numpy()
    low = strata == 0
    return dict(reach=float((rank < 1.0).mean()),
                reach_low=float((rank[low] < 1.0).mean()) if int(low.sum()) >= 8 else float("nan"),
                rep_var=eng._rep_variance(E),
                sig=hashlib.sha256(np.round(sc[:32].cpu().numpy().astype(np.float64), 5).tobytes()).hexdigest())


def _mechanism_selftest(device, dim=DIM):
    # Planted world: clean grid-translation task + degree-contaminated structure + clean attribute centroid.
    n, nr, tri_task, noise_edges, ent_cluster, cc = _planted_grounding_world(9, 3, 6, 0, noise_edge_mult=1.5)
    rng = np.random.default_rng(17)
    M = tri_task.shape[0]
    perm = rng.permutation(M)
    n_hold = int(HELDOUT_FRAC * M)
    hold = tri_task[perm[:n_hold]]
    vis = tri_task[perm[n_hold:]]
    comp = rt.completable_mask(hold, vis, n, nr)
    queries = hold[comp]
    if queries.shape[0] > 400:
        queries = queries[rng.choice(queries.shape[0], size=400, replace=False)]
    cand = rt.build_ranking_candidates(queries, tri_task, n, min(N_RANK_NEG, n - 2), 7)
    deg_vis = rt.visible_degree(vis, n)
    deg_vis_t = torch.from_numpy(deg_vis.astype(np.float32)).to(device)
    strata, _q = rt.stratify_by_target_degree(queries, deg_vis)

    # STRUCTURE is computed from visible task edges PLUS the contaminating noise edges (degree-blurred).
    vis_struct = np.concatenate([vis, noise_edges], axis=0)
    struct = eng.structural_features(vis_struct, n, dim, 7, device)
    struct2 = eng.structural_features(vis_struct, n, dim, 7 + 1234, device, hop=STRUCT_HOP2)
    # ATTRIBUTE = clean cluster centroid (exterior, degree-blind) via the engine's additive-preserving feature.
    attr = eng._cluster_feat(ent_cluster, cc, dim, 31, 0.3, device)
    attr = torch.nn.functional.normalize(attr, dim=1)
    attr_scr = attr[torch.from_numpy(rng.permutation(n)).to(device)]

    g = _selftest_geom_one(struct, attr, vis, tri_task, n, nr, queries, cand, strata, dim, 7, device)
    u = _selftest_geom_one(struct, struct2, vis, tri_task, n, nr, queries, cand, strata, dim, 11, device)
    s = _selftest_geom_one(struct, attr_scr, vis, tri_task, n, nr, queries, cand, strata, dim, 13, device)
    pop_h1 = rt._hits_from_ranks(rt._ranks_from_scores(rt.rank_popularity(deg_vis_t, queries, cand, device)))[0]

    # (d) collapse discriminator.
    base_row = eng._noise_feat(1, 2 * dim, 9, device)
    collapsed = base_row.repeat(n, 1) + 1e-4 * eng._noise_feat(n, 2 * dim, 3, device)
    collapsed_var = eng._rep_variance(collapsed)

    a_grounded_recovers = bool(g["reach"] == g["reach"] and g["reach"] >= ST_CAPTURE_MIN)
    a_transfers = bool(g["reach"] == g["reach"] and u["reach"] == u["reach"]
                       and (g["reach"] - u["reach"]) >= ST_TRANSFER_MARGIN)
    a_low_positive = bool(g["reach_low"] == g["reach_low"] and u["reach_low"] == u["reach_low"]
                          and (g["reach_low"] - u["reach_low"]) > 0.0)
    c_scramble_no_transfer = bool(s["reach"] == s["reach"] and u["reach"] == u["reach"]
                                  and (s["reach"] - u["reach"]) <= ST_SCRAMBLE_MAX)
    a_beats_pop = bool(g["reach"] == g["reach"] and pop_h1 == pop_h1 and (g["reach"] - pop_h1) >= 0.05)
    d_collapse_caught = bool(collapsed_var <= eng.COLLAPSE_VAR_FLOOR
                             and g["rep_var"] == g["rep_var"] and g["rep_var"] > eng.COLLAPSE_VAR_FLOOR)
    arms_differ = bool(len({g["sig"], u["sig"], s["sig"]}) >= 3)

    res = dict(grounded_reach=round(g["reach"], 4), ungrounded_reach=round(u["reach"], 4),
               scrambled_reach=round(s["reach"], 4), pop_reach=round(pop_h1, 4),
               grounded_reach_low=round(g["reach_low"], 4) if g["reach_low"] == g["reach_low"] else None,
               ungrounded_reach_low=round(u["reach_low"], 4) if u["reach_low"] == u["reach_low"] else None,
               transfer_margin=round(g["reach"] - u["reach"], 4),
               scramble_lift=round(s["reach"] - u["reach"], 4),
               collapsed_var=round(collapsed_var, 5), grounded_var=round(g["rep_var"], 4),
               ST_CAPTURE_MIN=round(ST_CAPTURE_MIN, 4), ST_TRANSFER_MARGIN=ST_TRANSFER_MARGIN,
               a_grounded_recovers=a_grounded_recovers, a_transfers=a_transfers, a_low_positive=a_low_positive,
               c_scramble_no_transfer=c_scramble_no_transfer, a_beats_pop=a_beats_pop,
               d_collapse_caught=d_collapse_caught, arms_differ=arms_differ,
               task_edges=int(tri_task.shape[0]), noise_edges=int(noise_edges.shape[0]), n_queries=int(queries.shape[0]))
    ok = bool(a_grounded_recovers and a_transfers and a_low_positive and c_scramble_no_transfer and a_beats_pop
              and d_collapse_caught and arms_differ)
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
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t0 = time.perf_counter()
    _log("device=%s run_mode=%s" % (device, run_mode))

    st_ok, st_res = _mechanism_selftest(device, dim=cfg["kge_dim"])
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (grounded-transfers / ablated-no-transfer / scrambled-no-transfer / "
                        "collapse discriminators did not fire): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS loop-closer: (a) grounded geometry TRANSFERS to relational inference (beats "
                        "ungrounded + LOW-stratum positive) on the planted degree-contaminated world; (b) ungrounded "
                        "does not recover; (c) scrambled does not transfer; (d) collapse caught; arms differ",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    for key in fus.DATASETS:
        if not fus._ensure_dataset(key):
            write_metrics(get_output_dir(ANCHOR_NAME), dict(
                verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                verdict_msg="testbed dataset %r absent + self-acquire failed on runner: %s (see data/grounding_testbed/"
                            "PROVENANCE_multiattribute.md; stage the file or check runner network)"
                            % (key, fus.DATASETS[key]["path"]),
                summary="testbed data missing", elapsed_s=time.perf_counter() - t0))
            raise SystemExit(1)

    _log("building covered typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    edges, rels, node_words, Y, present, attr_names, meta = build_covered_typed_subgraph(cfg["n_nodes"],
                                                                                         SUBGRAPH_BASE_SEED)
    _log("covered+connected n=%d typed_edges=%d n_rels=%d coverage(conc)=%.1f%%"
         % (meta["n_covered_connected"], meta["n_typed_edges"], meta["n_rels"],
            100 * meta["coverage_frac_concreteness"]))
    _log("attr coverage: %s" % {k: round(v, 3) for k, v in meta["attr_coverage"].items()})

    # Independence selection of the fused measured attributes (reuses the fusion cell's gate; the grounding source).
    sel, sel_info = fus.independence_select(Y, present, attr_names, Y[:, 0])
    _log("SELECTED (fused measured attributes): %s (n=%d)" % (sel, sel_info["n_selected"]))
    sel_idx = [attr_names.index(s) for s in sel]
    if len(sel_idx) < 1:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="HARD_FAIL_NO_ATTRIBUTES_SELECTED", run_mode=run_mode,
            verdict_msg="independence selection returned no attributes to ground with (n_selected=%d)"
                        % sel_info["n_selected"],
            summary="no attributes selected", elapsed_s=time.perf_counter() - t0, independence=sel_info,
            subgraph_meta=meta))
        raise SystemExit(1)

    out_dir = get_output_dir(ANCHOR_NAME)
    per_seed = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, edges, rels, node_words, Y, sel_idx, cfg, device)
            sig_vals = set(v for v in pm["arm_sigs"].values() if not v.endswith("_failed"))
            if len(sig_vals) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct arm sigs"
                                   % (seed, len(sig_vals)))
            per_seed.append(pm)
            write_partial(out_dir, seed, dict(seed=seed, metrics=pm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
            seed_failures=seed_failures, subgraph_meta=meta, independence=sel_info))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, sel_info, meta)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"], dim=DIM,
                                                   kge_epochs=cfg["kge_epochs"]),
                   subgraph_meta=meta, gates=gates, independence=sel_info, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t0))


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
