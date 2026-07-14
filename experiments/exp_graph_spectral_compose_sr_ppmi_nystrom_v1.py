"""GRAPH_SPECTRAL_COMPOSE_SR_PPMI_NYSTROM: envelope-push on the VET'd graph-spectral inductive-compose near-miss
(data/exp_graph_spectral_entity_codes_cskg_v1/metrics.json, GRAPH_STRUCTURE_LIFTS_PARTIAL_MIDDLE:
LAP_COMPOSE=0.0099 vs RAND_COMPOSE=0.0040, lift 0.0059, needed >=0.010; scramble-verified real, margin 0.0092).
The parent only ever composed the TRANSDUCTIVELY WORST codebook (LAP: oracle 0.0107) inductively with a FLAT
neighbor-mean. The two best transductive codebooks were NEVER composed inductively (PPMI oracle 0.1189 = 11x LAP;
SR oracle 0.0508 = 5x LAP), and the flat unweighted mean is the aggregation NEITHER brain theory (Dayan 1993 SR
Bellman recursion: new state = own edges + TRANSITION-WEIGHTED neighbor SR rows) NOR graph theory (Nystrom /
APPNP out-of-sample extension: EDGE-SIMILARITY-WEIGHTED average, down-weight promiscuous hub neighbors) recommends.
This cell varies the ONE axis that was never varied -- CODEBOOK (PPMI/SR vs LAP) x AGGREGATION (flat unweighted
mean vs edge-similarity/degree-weighted mean) -- reusing the shipped harness verbatim on the SAME leak-free
held-out-ENTITY CSKG-core arena (k_core=12, N~25.7k, frac=0.15, support_frac=0.5, seeds 7/13/17).

AGGREGATION -- what "better" means, and what was REJECTED (honest apparatus note):
  The literature-correct closed form for spectral out-of-sample composition is the Nystrom extension
  phi_k(x) ~= (1/lambda_k) sum_i w(x,x_i) phi_k(x_i) (Bengio 2004; Levin et al. arXiv:1802.06307): an
  eigenvalue-normalized, edge-similarity-weighted average. The literal 1/lambda_k eigenvalue-INVERSION term was
  IMPLEMENTED AND EMPIRICALLY REJECTED at author time: on the degree-homogeneous planted-SBM positive-control
  arena it AMPLIFIES the partial-neighborhood reconstruction error in the low-eigenvalue (noise) dims and drives
  the mechanism arm BELOW the chance floor (LAP_COMPOSE_NYS=0.042 < RAND_NULL=0.10) -- a broken discriminator, not
  a lift. The ROBUST core that both routes share (Nystrom edge-similarity weighting, APPNP PageRank propagation,
  SR transition weighting) is the EDGE/DEGREE weighting: down-weight promiscuous high-degree hub neighbors that
  connect to everything and carry little entity-specific signal. This cell's "NYS" aggregation therefore realizes
  the frame-safe, robust component -- a SYMMETRIC-NORMALIZED (1/sqrt(deg_train(h))) degree-weighted neighbor mean,
  computed in the SAME scaled spectral-embedding frame as the FLAT arm (so FLAT vs NYS is a PURE aggregation
  contrast, identical codebook + frame, only the neighbor weight differs). On a degree-HOMOGENEOUS graph NYS==FLAT
  by construction; the contrast only appears under the CSKG graph's MEASURED degree heterogeneity (Gini=0.5368) --
  which is exactly the setting where a hub-downweighted aggregation is hypothesized to matter.

LEAK-FREE (the crux; the parent's confound-controlled compose kept clean, do NOT regress it):
  * COMPOSE codes are built on the TRAIN-ONLY adjacency A_train (train_int; fold_in=None). Held-out entities have
    ZERO train edges (build_heldout_entity_split_ac excludes any edge touching a held-out entity from train).
  * A held-out entity t's code is the (flat or degree-weighted) aggregate of its SUPPORT-neighbor heads' TRAIN
    codes. Support edges are used ONLY to build t's code, NEVER scored. QUERY edges are ONLY scored, NEVER used to
    build any code. support_int and query_int are disjoint edge-sets. A per-run leak_audit asserts:
    (1) |query_edges INTERSECT support_edges| == 0, (2) every held-out (scored) tail has train-degree 0, (3) the
    compose store W is ingested from train_int ONLY (n_ingested == n_train). Any breach -> INCONCLUSIVE.

WHY the degree-weighting gap is expected at FULL but not at self-test scale (discriminator-survives-scale option B,
analytical): the flat vs degree-weighted gap only appears under DEGREE HETEROGENEITY (Gini(deg)=0.5368 MEASURED on
this exact CSKG graph). The planted-SBM self-test arena is degree-HOMOGENEOUS by construction, so flat and NYS are
near-equivalent there; the self-test therefore proves BOTH aggregations RUN + their scramble controls COLLAPSE
(mechanism fires), and the flat-vs-degree magnitude question is answered only on the real heterogeneous CSKG graph.

TWO AGGREGATIONS (both PAIRED on the SAME held-out QUERY edges; filtered MRR-vs-all-N; matched dim d=1024;
scaled spectral embedding E = row_norm(U * sqrt(s)) for ALL code arms -- the parent frame):
  FLAT (uniform index_add neighbor-mean; the parent's aggregation, reused verbatim):
    RAND_COMPOSE          : flat mean over random train codes -> the FLAT random bar.
    LAP_COMPOSE_FLAT      : == parent LAP_COMPOSE; reproduce ~0.0099 (anchor / positive control).
    PPMI_COMPOSE_FLAT     : flat mean, PPMI train codebook (untested; strongest transductive performer). HEADLINE.
    SR_COMPOSE_FLAT       : flat mean, SR train codebook (direct brain analog). HEADLINE.
  NYS (symmetric-degree-weighted neighbor mean; SAME scaled codebook + frame as FLAT; only the neighbor weight
       w(t,h) = 1/sqrt(deg_train(h)) differs -> pure aggregation contrast):
    RAND_COMPOSE_NYS      : degree-weighted mean over random codes -> the NYS random bar.
    LAP_COMPOSE_NYS       : degree-weighted, LAP codebook (isolates AGGREGATION holding codebook=LAP). HEADLINE.
    SR_COMPOSE_NYS        : degree-weighted, SR codebook (best codebook x best aggregation; interaction). HEADLINE.
  SCRAMBLE must-fail (aggregate over RANDOM entities, not the true support-neighbors -> needs the TRUE neighborhood):
    PPMI_COMPOSE_FLAT_SCRAMBLE, SR_COMPOSE_FLAT_SCRAMBLE, LAP_COMPOSE_NYS_SCRAMBLE, SR_COMPOSE_NYS_SCRAMBLE.
  ORACLE (transductive ceiling + positive controls; reused verbatim from the parent):
    RAND_ORACLE (reproduce native ~0.023), LAP_ORACLE, PPMI_ORACLE, SR_ORACLE.
  RAND_NULL (chance floor). BASELINE_POP (freq baseline / BROKEN guard).

LOCALIZATION / VERDICT (pre-registered BELOW, picked BEFORE the run; strictly-above-floor per META_RULE_L):
  A creditable compose arm X in {PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT, LAP_COMPOSE_NYS, SR_COMPOSE_NYS} is CREDITED iff:
    (i)  compose_lift(X) = MRR(X) - MRR(matched random bar) >= LIFT_MARGIN(0.010)
         [flat arms vs RAND_COMPOSE; nys arms vs RAND_COMPOSE_NYS -- each aggregation gets its OWN matched random bar]
    (ii) scramble_margin(X) = MRR(X) - MRR(X_SCRAMBLE) >= COMPOSE_SCRAMBLE_MARGIN(0.005)
    (iii) MRR(X) > MRR(LAP_COMPOSE_FLAT) (strictly beats the failed flat-LAP baseline ~0.0099; contract clause c).
  SCAFFOLD_BIND_TRANSFERS : pos-controls hold AND oracle fires AND >=1 creditable arm passes (i)+(ii)+(iii).
  SCAFFOLD_BIND_DOESNT    : pos-controls hold AND oracle fires AND NO creditable arm clears LIFT_MARGIN AND none
                            improves its scramble margin beyond the parent's 0.0092 (clean stronger negative:
                            closes the topology-only compose lens across BOTH new codebooks AND the hub-downweighted
                            aggregation -> redirect to relation-typed additive/reciprocal-edge program).
  MIDDLE_BAND : some creditable arm lands lift in (0.005, 0.010] -> real-but-minor, close as such.
  INCONCLUSIVE : pos-controls/oracle fail, leak_audit breach, too few held-out queries, or POP beats RAND_NULL.
  ISOLATION readout (logged regardless): winner_axis = CODEBOOK (a *_FLAT beats LAP_COMPOSE_FLAT) vs AGGREGATION
    (LAP_COMPOSE_NYS beats LAP_COMPOSE_FLAT) vs INTERACTION (SR_COMPOSE_NYS is the top arm).

## Compute architecture
class (b) sequential-CPU, justified -- identical cost profile to the parent (closed-form randomized-SVD of a
~25.7k-node/~474k-edge SPARSE operator; no SGD/epochs/learned aggregator; one-shot Hebbian KGStore.ingest_triples).
Per seed: parent's 4 oracle spectral factorizations + 3 train factorizations (LAP/PPMI/SR) + ~13 native d=1024
Hebbian stores (FLAT and NYS reuse the SAME scaled codebooks). All CPU, device=cpu -> remote_cpu_queue. No GPU. No
mutation of any persisted store; codes in-memory per seed. Parent ran 610s/3seeds; this adds ~1x the compose stores.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test + per-seed (META_RULE_AF): 17 arms produce >=8 distinct score signatures.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: bands = MEASURED in-run matched-aggregation RANDOM bars (flat->RAND_COMPOSE, nys->
#   RAND_COMPOSE_NYS) + CITED additive-compose 0.1282 stretch ceiling. Filtered-MRR chance floor ~1/N (2e-5);
#   native 0.023 @ d1024 is ~600x chance -> arena answerable; discriminator can fire in EITHER direction (relief
#   ceiling 0.781 >> any compose arm) so no saturation. discriminator_reachability OK.
# - baseline_in_band: RAND_ORACLE reproduces native ~0.023 (>> RAND_NULL) = ORACLE-FIRES gate (calibration_check).
# - discriminator survives scale: FULL at the EXACT CSKG-core/held-out regime that MEASURED 0.023->0.781+0.137; the
#   degree-weighting gap is expected only under the graph's Gini=0.537 heterogeneity (option B analytical); the
#   self-test fires LAP-recovers-planted + embedding-separates + BOTH flat AND degree-weighted compose-scramble
#   collapse (the eigenvalue-inversion Nystrom term was rejected because it collapses the positive control).
# - HARD bands strictly separated: TRANSFERS needs matched-random + 0.010 (MIDDLE dead-band (0.005,0.010]).
# - HP_SCOPE: the credit gates apply to {PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT, LAP_COMPOSE_NYS, SR_COMPOSE_NYS} only.
#   RAND_COMPOSE / RAND_COMPOSE_NYS = matched random bars; *_SCRAMBLE = must-fail; RAND_NULL = chance; POP = BROKEN.
# - cardinality: EXPECTED_N_UNITS = n_seeds(3); each seed asserted to produce all arms + >=8 sigs + finite W + leak-ok.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- ALL dims/ranks/fracs/tols/gammas pre-registered, NOT tuned on
#   real data; the CSKG-core + held-out split config is COPIED VERBATIM from the parent VET'd arena.
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the docstring.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-arm flush prints + heartbeat; timeout>=1800).

MEASURED@data/exp_graph_spectral_entity_codes_cskg_v1/metrics.json: LAP_COMPOSE=0.009852 RAND_COMPOSE=0.003957
  SCRAMBLE=0.000681 RAND_ORACLE=0.023083 LAP_ORACLE=0.010685 PPMI_ORACLE=0.118939 SR_ORACLE=0.050790 RAND_NULL=0.000449.
CITED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json: ANCHOR_COMPOSE(additive realized)=0.12821 (stretch).
THEORETICAL@Levin,Roosta-Khorasani,Mahoney,Priebe arXiv:1802.06307 (graph-Nystrom OOS edge-similarity weighting);
  Klicpera et al. ICLR 2019 arXiv:1810.05997 (APPNP bare PageRank propagation); Dayan 1993 SR Bellman recursion.

ASCII-only. No bare except; except SystemExit before except Exception.
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from hdlab.kg_traversal import KGStore  # noqa: E402
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402
import experiments.exp_graph_spectral_entity_codes_cskg_v1 as G  # noqa: E402  (parent harness; reused verbatim)

ANCHOR_NAME = "graph_spectral_compose_sr_ppmi_nystrom_v1"

# ---- Arm names ----
RAND_ORACLE = "RAND_ORACLE"
LAP_ORACLE = "LAP_ORACLE"
PPMI_ORACLE = "PPMI_ORACLE"
SR_ORACLE = "SR_ORACLE"
RAND_COMPOSE = "RAND_COMPOSE"                      # flat random bar
RAND_COMPOSE_NYS = "RAND_COMPOSE_NYS"              # degree-weighted random bar
LAP_COMPOSE_FLAT = "LAP_COMPOSE_FLAT"             # anchor: reproduce parent LAP_COMPOSE ~0.0099
PPMI_COMPOSE_FLAT = "PPMI_COMPOSE_FLAT"           # creditable
SR_COMPOSE_FLAT = "SR_COMPOSE_FLAT"               # creditable
LAP_COMPOSE_NYS = "LAP_COMPOSE_NYS"               # creditable (degree-weighted)
SR_COMPOSE_NYS = "SR_COMPOSE_NYS"                 # creditable (degree-weighted)
PPMI_COMPOSE_FLAT_SCRAMBLE = "PPMI_COMPOSE_FLAT_SCRAMBLE"
SR_COMPOSE_FLAT_SCRAMBLE = "SR_COMPOSE_FLAT_SCRAMBLE"
LAP_COMPOSE_NYS_SCRAMBLE = "LAP_COMPOSE_NYS_SCRAMBLE"
SR_COMPOSE_NYS_SCRAMBLE = "SR_COMPOSE_NYS_SCRAMBLE"
RAND_NULL = "RAND_NULL"
POP = "BASELINE_POP"

ORACLE_ARMS = [RAND_ORACLE, LAP_ORACLE, PPMI_ORACLE, SR_ORACLE]
CREDIT_ARMS = [PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT, LAP_COMPOSE_NYS, SR_COMPOSE_NYS]
RANDOM_BAR = {PPMI_COMPOSE_FLAT: RAND_COMPOSE, SR_COMPOSE_FLAT: RAND_COMPOSE,
              LAP_COMPOSE_NYS: RAND_COMPOSE_NYS, SR_COMPOSE_NYS: RAND_COMPOSE_NYS}
SCRAMBLE_OF = {PPMI_COMPOSE_FLAT: PPMI_COMPOSE_FLAT_SCRAMBLE, SR_COMPOSE_FLAT: SR_COMPOSE_FLAT_SCRAMBLE,
               LAP_COMPOSE_NYS: LAP_COMPOSE_NYS_SCRAMBLE, SR_COMPOSE_NYS: SR_COMPOSE_NYS_SCRAMBLE}
ALL_ARMS = [RAND_ORACLE, LAP_ORACLE, PPMI_ORACLE, SR_ORACLE,
            RAND_COMPOSE, RAND_COMPOSE_NYS, LAP_COMPOSE_FLAT, PPMI_COMPOSE_FLAT, SR_COMPOSE_FLAT,
            LAP_COMPOSE_NYS, SR_COMPOSE_NYS,
            PPMI_COMPOSE_FLAT_SCRAMBLE, SR_COMPOSE_FLAT_SCRAMBLE, LAP_COMPOSE_NYS_SCRAMBLE, SR_COMPOSE_NYS_SCRAMBLE,
            RAND_NULL, POP]

EVAL_KS = G.EVAL_KS
CEIL_METRIC = G.CEIL_METRIC

# ---- CITED reference ceilings ----
CITED_NATIVE_1024 = G.CITED_NATIVE_1024
CITED_ADD_COMPOSE = G.CITED_ADD_COMPOSE

# ---- Params (pre-registered; inherited verbatim from parent; NOT tuned on real data) ----
D_CODE = G.D_CODE
SVD_N_ITER = G.SVD_N_ITER
SR_GAMMA = G.SR_GAMMA
SR_KSTEPS = G.SR_KSTEPS

# ---- Pre-registered bands (inherited verbatim from parent) ----
REPRODUCE_TOL = G.REPRODUCE_TOL
RAND_NULL_FLOOR = G.RAND_NULL_FLOOR
ORACLE_FIRE_RATIO = G.ORACLE_FIRE_RATIO
ORACLE_FIRE_ABS = G.ORACLE_FIRE_ABS
LIFT_MARGIN = G.LIFT_MARGIN                # 0.010
COMPOSE_SCRAMBLE_MARGIN = G.COMPOSE_SCRAMBLE_MARGIN  # 0.005
PARENT_LAP_COMPOSE = 0.009852             # MEASURED@parent metrics: the flat-LAP baseline this cell must beat
PARENT_SCR_MARGIN = 0.009171              # MEASURED@parent metrics: scramble margin to improve on for the negative
MIDDLE_LO = 0.005

# ---- Self-test planted thresholds (calibrated on synthetic SBM, NOT real data; inherited from parent) ----
ST_LAP_ORACLE_MIN = G.ST_LAP_ORACLE_MIN
ST_ORACLE_BEATS_NULL = G.ST_ORACLE_BEATS_NULL
ST_BLOCK_PURITY_MIN = G.ST_BLOCK_PURITY_MIN
ST_COMPOSE_SCRAMBLE_MARGIN = G.ST_COMPOSE_SCRAMBLE_MARGIN

SELFTEST_CFG = dict(G.SELFTEST_CFG)
FULL_CFG = dict(d_code=D_CODE, svd_n_iter=SVD_N_ITER, heldout_entity_frac=0.15, support_frac=0.5,
                cskg_max_lines=0, k_core=12, cskg_max_nodes=0, n_heldout_eval=3000, min_heldout=20,
                seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


# ---------------------------------------------------------------------------
# Degree-weighted (Nystrom/APPNP edge-similarity) out-of-sample compose. SAME scaled codebook + frame as the FLAT
# arm (parent's G.compose_neighbor_codes); ONLY the neighbor weight w(t,h)=1/sqrt(deg_train(h)) differs -> a PURE
# aggregation contrast. The literal 1/lambda Nystrom eigenvalue-inversion term was rejected (collapses the positive
# control below chance on the degree-homogeneous synthetic arena -- see docstring apparatus note).
# ---------------------------------------------------------------------------

def compose_neighbor_codes_wdeg(train_codes, support_int, N, d, seed, A_train, scramble=False):
    """held-out t code = row_norm( sum_h w(t,h) train_codes[h] / sum_h w(t,h) ), w(t,h)=1/sqrt(max(deg_train(h),1))
    symmetric-normalized hub-downweighting. scramble=True aggregates over RANDOM entities (same count)."""
    deg_train = np.asarray(A_train.sum(axis=1)).ravel().astype(np.float64)
    heads = support_int[:, 0].astype(np.int64)
    tails = support_int[:, 2].astype(np.int64)
    if scramble:
        rng = np.random.default_rng(seed * 8887 + 5)
        heads = rng.integers(0, N, size=heads.shape[0]).astype(np.int64)
    w_edge = (1.0 / np.sqrt(np.maximum(deg_train[heads], 1.0))).astype(np.float32)
    Ep = train_codes.clone()
    acc = torch.zeros(N, d, dtype=torch.float32)
    acc.index_add_(0, torch.from_numpy(tails).long(),
                   train_codes[torch.from_numpy(heads).long()] * torch.from_numpy(w_edge).unsqueeze(1))
    wsum = torch.zeros(N, dtype=torch.float32)
    wsum.index_add_(0, torch.from_numpy(tails).long(), torch.from_numpy(w_edge))
    mask = wsum > 0
    comp = acc[mask] / wsum[mask].unsqueeze(1)
    nrm = comp.norm(dim=1, keepdim=True); nrm[nrm < 1e-9] = 1.0
    Ep[mask] = comp * (float(np.sqrt(d)) / nrm)
    return Ep


def compose_score_wdeg(N, n_rel, d, seed, train_codes, train_int, support_int, query_int, A_train, scramble=False):
    """Train-only W over train_codes (scaled spectral embedding, SAME as FLAT); patch held-out rows with the
    degree-weighted neighbor mean; native recall + score."""
    store, fin = G.build_store_with_codes(N, n_rel, d, seed, train_codes, train_int, fold_in=None)
    Ep = compose_neighbor_codes_wdeg(train_codes, support_int, N, d, seed, A_train, scramble=scramble)
    store.E = Ep.contiguous()
    recall = base.native_query_recall(store, query_int)
    return base.score_from_codes(recall, store.E), fin


# ---------------------------------------------------------------------------
# Leak audit (the crux; assert train-only codes + disjoint support/query + held-out tails have zero train degree).
# ---------------------------------------------------------------------------

def leak_audit(prep, n_ingested_compose):
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    N = prep["N"]

    def _eset(a):
        if a.shape[0] == 0:
            return set()
        return set((int(x[0]), int(x[1]), int(x[2])) for x in a)

    qs = _eset(query_int); ss = _eset(support_int)
    overlap = len(qs & ss)
    tdeg = np.zeros(N, dtype=np.int64)
    if train_int.shape[0]:
        np.add.at(tdeg, train_int[:, 0].astype(np.int64), 1)
        np.add.at(tdeg, train_int[:, 2].astype(np.int64), 1)
    scored_tails = np.unique(query_int[:, 2].astype(np.int64)) if query_int.shape[0] else np.array([], dtype=np.int64)
    scored_tail_train_deg = int(tdeg[scored_tails].sum()) if scored_tails.shape[0] else 0
    ingest_ok = bool(n_ingested_compose == int(train_int.shape[0]))
    ok = bool(overlap == 0 and scored_tail_train_deg == 0 and ingest_ok)
    return dict(query_support_overlap=overlap, n_query=int(query_int.shape[0]), n_support=int(support_int.shape[0]),
                scored_tail_train_degree=scored_tail_train_deg, n_train=int(train_int.shape[0]),
                compose_store_n_ingested=int(n_ingested_compose), ingest_equals_train=ingest_ok, leak_free=ok)


# ---------------------------------------------------------------------------
# Score all arms PAIRED on the SAME held-out QUERY edges.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, seed):
    N = prep["N"]; n_rel = prep["n_rel"]; d = cfg["d_code"]; n_iter = cfg["svd_n_iter"]
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    hold_all = prep["hold_all"]; all_true = prep["all_true"]

    A_oracle = G.build_adjacency(np.concatenate([train_int, hold_all], axis=0), N)
    A_train = G.build_adjacency(train_int, N)

    # RAND_ORACLE via the base native path (bit-identical bipolar E) -> reproduce CITED native ~0.023.
    store_rand_o = base.build_store(N, n_rel, d, seed, train_int, fold_in=hold_all)
    recall_r = base.native_query_recall(store_rand_o, query_int)
    rand_codes = base.build_store(N, n_rel, d, seed, train_int).E.contiguous()   # random codebook (train-W frame)

    # oracle spectral codebooks (fold-in graph).
    lap_o, _ = G.lap_codes(A_oracle, d, n_iter, seed)
    ppmi_o, _ = G.ppmi_codes(A_oracle, d, n_iter, seed)
    sr_o, _ = G.sr_codes(A_oracle, d, n_iter, seed)
    # compose train codebooks (scaled-E frame; SHARED by FLAT and NYS arms).
    lap_tr, _ = G.lap_codes(A_train, d, n_iter, seed)
    ppmi_tr, _ = G.ppmi_codes(A_train, d, n_iter, seed)
    sr_tr, _ = G.sr_codes(A_train, d, n_iter, seed)

    finite = bool(torch.isfinite(store_rand_o.W).all().item())
    arm_scores = {RAND_ORACLE: base.score_from_codes(recall_r, store_rand_o.E)}

    def _acc(name, sc, fin):
        arm_scores[name] = sc
        return fin

    for name, codes in [(LAP_ORACLE, lap_o), (PPMI_ORACLE, ppmi_o), (SR_ORACLE, sr_o)]:
        sc, fin = G.oracle_score(N, n_rel, d, seed, codes, train_int, hold_all, query_int)
        finite = finite and _acc(name, sc, fin)

    # FLAT compose arms (uniform mean; parent aggregation reused verbatim; RAND_COMPOSE = flat random bar).
    for name, tc, scr in [
        (RAND_COMPOSE, rand_codes, False),
        (LAP_COMPOSE_FLAT, lap_tr, False),
        (PPMI_COMPOSE_FLAT, ppmi_tr, False),
        (SR_COMPOSE_FLAT, sr_tr, False),
        (PPMI_COMPOSE_FLAT_SCRAMBLE, ppmi_tr, True),
        (SR_COMPOSE_FLAT_SCRAMBLE, sr_tr, True),
    ]:
        sc, fin = G.compose_score(N, n_rel, d, seed, tc, train_int, support_int, query_int, scramble=scr)
        finite = finite and _acc(name, sc, fin)

    # NYS compose arms (degree-weighted mean; SAME scaled codebooks; RAND_COMPOSE_NYS = degree-weighted random bar).
    for name, tc, scr in [
        (RAND_COMPOSE_NYS, rand_codes, False),
        (LAP_COMPOSE_NYS, lap_tr, False),
        (SR_COMPOSE_NYS, sr_tr, False),
        (LAP_COMPOSE_NYS_SCRAMBLE, lap_tr, True),
        (SR_COMPOSE_NYS_SCRAMBLE, sr_tr, True),
    ]:
        sc, fin = compose_score_wdeg(N, n_rel, d, seed, tc, train_int, support_int, query_int, A_train, scramble=scr)
        finite = finite and _acc(name, sc, fin)

    arm_scores[RAND_NULL] = base.random_scores(N, query_int, d, seed)

    arm_metric, arm_sig = {}, {}
    for name, sc in arm_scores.items():
        arm_metric[name] = G.filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = G._sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
    pop_m, pop_rank_vec = G.pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = G._sig(pop_rank_vec.astype(np.float64))

    # leak audit: probe a compose store built the SAME way the compose arms build it (train_int only).
    probe_store, _ = G.build_store_with_codes(N, n_rel, d, seed, lap_tr, train_int, fold_in=None)
    lk = leak_audit(prep, int(probe_store._n_triples_ingested))

    diag = dict(finite=bool(finite), d_code=int(d), N=int(N), leak=lk)
    return dict(arm_metric=arm_metric, arm_sig=arm_sig, arm_scores=arm_scores, diag=diag)


def run_corpus(pool_lbl, cfg, seed, corpus_name):
    prep = G.prepare_corpus(pool_lbl, cfg, seed)
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_heldout_entities=len(prep["hold_ids"]),
                  n_support=int(prep["support_int"].shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(prep["query_int"].shape[0]), n_cold=int(prep["n_cold"]), d_code=int(cfg["d_code"]))
    if prep["query_int"].shape[0] < 1:
        result["empty"] = True
        return result, None
    fs = score_all_arms(prep, cfg, seed)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs={a: fs["arm_sig"][a] for a in ALL_ARMS},
        diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# Lift verdict.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def lift_verdict(per_seed):
    def agg(arm):
        return _nm([_m(ps, arm) for ps in per_seed])

    mrr = {a: agg(a) for a in ALL_ARMS}
    rand_o = mrr[RAND_ORACLE]; rand_null = mrr[RAND_NULL]; pop = mrr[POP]
    lap_flat = mrr[LAP_COMPOSE_FLAT]

    def _sub(a, b):
        return (a - b) if (a == a and b == b) else float("nan")

    rand_reproduces = bool(rand_o == rand_o and abs(rand_o - CITED_NATIVE_1024) <= REPRODUCE_TOL)
    null_floor = bool(rand_null == rand_null and rand_null <= RAND_NULL_FLOOR)
    oracle_ratio = G._ratio(rand_o, rand_null)
    oracle_fires = bool(_sub(rand_o, rand_null) == _sub(rand_o, rand_null) and _sub(rand_o, rand_null) >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    finite = all(ps.get("diag", {}).get("finite", False) for ps in per_seed)
    leak_free = all(ps.get("diag", {}).get("leak", {}).get("leak_free", False) for ps in per_seed)
    broken = bool(pop == pop and rand_null == rand_null and (pop - rand_null) > max(RAND_NULL_FLOOR, 0.005))
    pos_controls_ok = bool(rand_reproduces and null_floor and oracle_fires and finite and leak_free and not broken)

    credit = {}
    for arm in CREDIT_ARMS:
        val = mrr[arm]; bar = mrr[RANDOM_BAR[arm]]; scr = mrr[SCRAMBLE_OF[arm]]
        lift = _sub(val, bar)
        scr_margin = _sub(val, scr)
        beats_flat = bool(val == val and lap_flat == lap_flat and val > lap_flat)
        clears_lift = bool(lift == lift and lift >= LIFT_MARGIN)
        clears_scr = bool(scr_margin == scr_margin and scr_margin >= COMPOSE_SCRAMBLE_MARGIN)
        in_middle = bool(lift == lift and MIDDLE_LO < lift < LIFT_MARGIN)
        credited = bool(clears_lift and clears_scr and beats_flat)
        credit[arm] = dict(mrr=val, random_bar=RANDOM_BAR[arm], bar_mrr=bar, lift=lift, scramble=SCRAMBLE_OF[arm],
                           scramble_mrr=scr, scramble_margin=scr_margin, beats_flat_lap=beats_flat,
                           clears_lift=clears_lift, clears_scramble=clears_scr, in_middle=in_middle, credited=credited)

    any_credited = any(credit[a]["credited"] for a in CREDIT_ARMS)
    any_middle = any(credit[a]["in_middle"] for a in CREDIT_ARMS)
    best_scr_margin = max([credit[a]["scramble_margin"] for a in CREDIT_ARMS
                           if credit[a]["scramble_margin"] == credit[a]["scramble_margin"]] + [float("-inf")])
    improves_parent_scr = bool(best_scr_margin > PARENT_SCR_MARGIN)

    def _better(a):
        return bool(mrr[a] == mrr[a] and lap_flat == lap_flat and mrr[a] > lap_flat)
    codebook_axis = bool(_better(PPMI_COMPOSE_FLAT) or _better(SR_COMPOSE_FLAT))
    aggregation_axis = _better(LAP_COMPOSE_NYS)
    top_arm = max(CREDIT_ARMS, key=lambda a: (mrr[a] if mrr[a] == mrr[a] else -1))
    interaction = bool(top_arm == SR_COMPOSE_NYS)
    winner_axis = ("INTERACTION_SR_NYS" if (interaction and any_credited) else
                   "AGGREGATION" if (aggregation_axis and not codebook_axis) else
                   "CODEBOOK" if (codebook_axis and not aggregation_axis) else
                   "BOTH" if (codebook_axis and aggregation_axis) else "NONE")

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_POSCONTROL_ORACLE_OR_LEAK_FAILED"
    elif any_credited:
        verdict = "SCAFFOLD_BIND_TRANSFERS"
    elif any_middle:
        verdict = "SCAFFOLD_BIND_MIDDLE_BAND"
    elif not improves_parent_scr:
        verdict = "SCAFFOLD_BIND_DOESNT"
    else:
        verdict = "SCAFFOLD_BIND_MIDDLE_BAND"

    def _r(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    lk0 = per_seed[0].get("diag", {}).get("leak", {}) if per_seed else {}
    verdict_msg = (
        "%s || FLAT compose MRR: RAND=%s LAP=%s(anchor,parent0.0099) PPMI=%s SR=%s | NYS(degwt) MRR: RAND=%s LAP=%s SR=%s "
        "|| credited=%s [%s] winner_axis=%s top=%s(%s) "
        "|| ORACLE MRR: RAND=%s(repro0.023=%s) LAP=%s PPMI=%s SR=%s "
        "|| RAND_NULL=%s POP=%s leak_free=%s(qs_overlap=%s scored_tail_traindeg=%s) oracle_fires=%s pos_controls=%s seeds=%d"
        % (verdict, _fmt(mrr[RAND_COMPOSE]), _fmt(lap_flat), _fmt(mrr[PPMI_COMPOSE_FLAT]), _fmt(mrr[SR_COMPOSE_FLAT]),
           _fmt(mrr[RAND_COMPOSE_NYS]), _fmt(mrr[LAP_COMPOSE_NYS]), _fmt(mrr[SR_COMPOSE_NYS]),
           any_credited, ",".join(a for a in CREDIT_ARMS if credit[a]["credited"]) or "none", winner_axis,
           top_arm, _fmt(mrr[top_arm]),
           _fmt(rand_o), rand_reproduces, _fmt(mrr[LAP_ORACLE]), _fmt(mrr[PPMI_ORACLE]), _fmt(mrr[SR_ORACLE]),
           _fmt(rand_null), _fmt(pop), leak_free, lk0.get("query_support_overlap"), lk0.get("scored_tail_train_degree"),
           oracle_fires, pos_controls_ok, len(per_seed)))

    metric_keys = ["hits@%d" % kk for kk in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    gates = dict(
        verdict=verdict,
        compose_mrr_flat=dict(RAND=_r(mrr[RAND_COMPOSE]), LAP=_r(lap_flat), PPMI=_r(mrr[PPMI_COMPOSE_FLAT]),
                              SR=_r(mrr[SR_COMPOSE_FLAT])),
        compose_mrr_degwt=dict(RAND=_r(mrr[RAND_COMPOSE_NYS]), LAP=_r(mrr[LAP_COMPOSE_NYS]), SR=_r(mrr[SR_COMPOSE_NYS])),
        scramble_mrr=dict(PPMI_FLAT=_r(mrr[PPMI_COMPOSE_FLAT_SCRAMBLE]), SR_FLAT=_r(mrr[SR_COMPOSE_FLAT_SCRAMBLE]),
                          LAP_NYS=_r(mrr[LAP_COMPOSE_NYS_SCRAMBLE]), SR_NYS=_r(mrr[SR_COMPOSE_NYS_SCRAMBLE])),
        credit={a: {kk: (_r(vv) if isinstance(vv, float) else vv) for kk, vv in credit[a].items()} for a in CREDIT_ARMS},
        any_credited=any_credited, winner_axis=winner_axis, top_arm=top_arm,
        codebook_axis_helps=codebook_axis, aggregation_axis_helps=aggregation_axis, interaction=interaction,
        parent_flat_lap=PARENT_LAP_COMPOSE, parent_scramble_margin=PARENT_SCR_MARGIN,
        best_scramble_margin=_r(best_scr_margin), improves_parent_scramble=improves_parent_scr,
        oracle_mrr=dict(RAND=_r(rand_o), LAP=_r(mrr[LAP_ORACLE]), PPMI=_r(mrr[PPMI_ORACLE]), SR=_r(mrr[SR_ORACLE])),
        random_null_mrr=_r(rand_null), controls=dict(POP=_r(pop)),
        rand_reproduces=rand_reproduces, null_floor=null_floor, oracle_fires=oracle_fires,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        finite=finite, leak_free=leak_free, broken=broken, pos_controls_ok=pos_controls_ok,
        leak_audit_per_seed=[ps.get("diag", {}).get("leak", {}) for ps in per_seed],
        heldout_metric_spectrum={a: {mk: _r(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        bands=dict(CITED_NATIVE_1024=CITED_NATIVE_1024, CITED_ADD_COMPOSE=CITED_ADD_COMPOSE, D_CODE=D_CODE,
                   LIFT_MARGIN=LIFT_MARGIN, COMPOSE_SCRAMBLE_MARGIN=COMPOSE_SCRAMBLE_MARGIN, MIDDLE_LO=MIDDLE_LO,
                   REPRODUCE_TOL=REPRODUCE_TOL, RAND_NULL_FLOOR=RAND_NULL_FLOOR, SR_GAMMA=SR_GAMMA, SR_KSTEPS=SR_KSTEPS),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test (planted SBM; fires FLAT + degree-weighted compose discriminators).
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _selftest_real_store_smoke(cfg):
    """Gate F.1: CONSTRUCT the REAL KGStore + inject a scaled spectral codebook + RUN ingest_triples + the FLAT and
    degree-weighted OOS compose. Populates the exercised set."""
    exercised = set()
    d = cfg["d_code"]
    tri = np.array([[0, 0, 1], [1, 0, 2], [2, 1, 0], [3, 1, 0]], dtype=np.int64)
    A = G.build_adjacency(tri, 4)
    exercised.add("build_adjacency")
    codes, _s = G.lap_codes(A, d, cfg["svd_n_iter"], 7)
    exercised.add("lap_codes")
    store, fin = G.build_store_with_codes(4, 2, d, 7, codes, tri, fold_in=tri[:1])
    exercised.add("KGStore")
    exercised.add("build_store_with_codes")
    if store._n_triples_ingested > 0:
        exercised.add("ingest_triples")
    sc_f, fin_f = G.compose_score(4, 2, d, 7, codes, tri, tri[:2], tri, scramble=False)
    exercised.add("compose_score")
    sc_w, fin_w = compose_score_wdeg(4, 2, d, 7, codes, tri, tri[:2], tri, A, scramble=False)
    exercised.add("compose_score_wdeg")
    rec = base.native_query_recall(store, tri)
    if rec.shape == (4, d):
        exercised.add("native_query_recall")
    return exercised, bool(fin and fin_f and fin_w and rec.shape == (4, d))


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    out = {}
    exercised, real_ok = _selftest_real_store_smoke(cfg)

    pool, block_of = G.build_planted_sbm_arena(7, cfg["st_blocks"], cfg["st_members"], cfg["st_rels"],
                                               cfg["st_edges_per_member"])
    prep = G.prepare_corpus(pool, cfg, 7)
    if prep["query_int"].shape[0] < cfg["min_heldout"]:
        out["fail"] = "planted SBM arena produced too few held-out queries (%d)" % prep["query_int"].shape[0]
        return False, out

    res, fs = run_corpus(pool, cfg, 7, "PLANTED_SBM")
    am = fs["arm_metric"]
    sm = {a: am[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(fs["arm_sig"][a] for a in ALL_ARMS))

    lap_o = sm[LAP_ORACLE]; rand_null = sm[RAND_NULL]
    lap_recovers = bool(lap_o == lap_o and lap_o >= ST_LAP_ORACLE_MIN)
    lap_beats_null = bool(lap_o == lap_o and rand_null == rand_null and (lap_o - rand_null) >= ST_ORACLE_BEATS_NULL)

    def _fires(arm):
        v = sm[arm]; scr = sm[SCRAMBLE_OF[arm]]
        return bool(v == v and scr == scr and (v - scr) >= ST_COMPOSE_SCRAMBLE_MARGIN)
    flat_fires = _fires(SR_COMPOSE_FLAT)
    nys_fires = _fires(LAP_COMPOSE_NYS)
    nys_sr_fires = _fires(SR_COMPOSE_NYS)
    compose_scr_fails = bool(flat_fires and nys_fires and nys_sr_fires)
    arms_differ = bool(n_sigs >= 8)
    finite = bool(fs["diag"]["finite"])
    leak = fs["diag"]["leak"]
    leak_ok = bool(leak.get("leak_free", False))

    A_full = G.build_adjacency(np.concatenate([prep["train_int"], prep["hold_all"]], axis=0), prep["N"])
    lap_codes_full, _ = G.lap_codes(A_full, cfg["d_code"], cfg["svd_n_iter"], 7)
    purity = G._block_purity(lap_codes_full, block_of, k=8)
    embedding_separates = bool(purity >= ST_BLOCK_PURITY_MIN)

    # VACUOUS-SMOKE guard: the degree-weighted compose must fire above its scramble (the new aggregation mechanism).
    nys_frozen = bool((sm[LAP_COMPOSE_NYS] - sm[LAP_COMPOSE_NYS_SCRAMBLE]) < ST_COMPOSE_SCRAMBLE_MARGIN)
    assert_discriminator_fires(nys_frozen, control_name=LAP_COMPOSE_NYS_SCRAMBLE,
                               headline_name="degree_weighted_compose_over_true_neighbors_beats_scramble",
                               run_mode="self_test",
                               extra="LAP_COMPOSE_NYS did NOT separate from its scrambled-neighbor control on the "
                                     "planted SBM -> the degree-weighted aggregation mechanism is frozen / broken")

    st_verdict, _stmsg, _stg = lift_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(lap_recovers and lap_beats_null and embedding_separates),
         "control_name": "RAND_NULL", "headline_name": "spectral_codes_recover_planted_and_embedding_separates",
         "extra": "planted SBM: the LAP spectral codebook recovers planted held-out tails above chance (fold-in) AND "
                  "the embedding separates the planted blocks (purity>=%.2f) -> the spectral code path fires" % ST_BLOCK_PURITY_MIN},
        {"kind": "metric_moves", "metric_name": "compose_arms_mrr",
         "values": [rand_null, sm[SR_COMPOSE_FLAT_SCRAMBLE], sm[RAND_COMPOSE], sm[SR_COMPOSE_FLAT],
                    sm[RAND_COMPOSE_NYS], sm[LAP_COMPOSE_NYS], sm[SR_COMPOSE_NYS]],
         "extra": "flat + degree-weighted compose arms MOVE on synthetic (not frozen): RAND=%.3f SR_FLAT_SCR=%.3f "
                  "SR_FLAT=%.3f RAND_NYS=%.3f LAP_NYS=%.3f SR_NYS=%.3f"
                  % (sm[RAND_COMPOSE], sm[SR_COMPOSE_FLAT_SCRAMBLE], sm[SR_COMPOSE_FLAT], sm[RAND_COMPOSE_NYS],
                     sm[LAP_COMPOSE_NYS], sm[SR_COMPOSE_NYS])},
        {"kind": "negative_control_margin",
         "control_scores": [sm[SR_COMPOSE_FLAT_SCRAMBLE], sm[LAP_COMPOSE_NYS_SCRAMBLE], sm[SR_COMPOSE_NYS_SCRAMBLE],
                            rand_null, sm[POP]],
         "headline_threshold": min(sm[SR_COMPOSE_FLAT], sm[LAP_COMPOSE_NYS], sm[SR_COMPOSE_NYS]),
         "higher_is_pass": True, "margin": ST_COMPOSE_SCRAMBLE_MARGIN, "n_repeats_min": 3,
         "control_name": "scrambled_neighbor_compose_below_true_neighbor_compose", "extra":
         "every scrambled-neighbor compose (flat + degree-weighted) + RAND_NULL + POP sit below the true-neighbor "
         "compose arms by the MRR margin -> the compose lift needs the TRUE support-neighborhood, not code volume"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["lap_recovers", "lap_beats_null", "embedding_separates", "flat_fires",
                                    "nys_fires", "nys_sr_fires", "leak_ok", "arms_differ", "real_code_path",
                                    "lift_verdict"],
         "exercised_gates": ["lap_recovers", "lap_beats_null", "embedding_separates", "flat_fires",
                             "nys_fires", "nys_sr_fires", "leak_ok", "arms_differ", "real_code_path", "lift_verdict"],
         "extra": "lift_verdict=%s at self-test scale" % st_verdict},
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["KGStore", "build_store_with_codes", "ingest_triples", "native_query_recall",
                                        "compose_score", "compose_score_wdeg"],
         "exercised_entrypoints": exercised,
         "extra": "self-test constructs the REAL KGStore, injects a scaled spectral codebook, runs ingest_triples + "
                  "the flat AND degree-weighted OOS compose"},
        {"kind": "substrate_signature", "callable_obj": KGStore, "callable_name": "KGStore",
         "kwargs": {"n_ent": 1, "n_rel": 1, "n_dim": 16, "generator": None},
         "extra": "base/portable KGStore kwargs only (n_ent,n_rel,n_dim,generator); no optional init_entities"},
        {"kind": "guard_baseline_valid", "baseline_score": sm[RAND_ORACLE], "floor_score": rand_null,
         "guard_name": "BROKEN_POP_BEATS_RANDNULL", "baseline_name": "RAND_ORACLE", "floor_name": "RAND_NULL",
         "eps": 0.02,
         "extra": "the BROKEN guard compares POP against the RAND_NULL floor (not a structural-zero POP); RAND_ORACLE "
                  "sits above the floor so the arena baseline is valid"},
    ], run_mode="self_test")

    out.update(
        real_code_path_ok=bool(real_ok), exercised_entrypoints=sorted(exercised),
        planted={a: (round(sm[a], 5) if sm[a] == sm[a] else None) for a in ALL_ARMS},
        block_purity=round(purity, 4), n_distinct_sigs=n_sigs, lap_recovers=lap_recovers,
        lap_beats_null=lap_beats_null, embedding_separates=embedding_separates,
        flat_compose_fires=flat_fires, degwt_compose_fires=nys_fires, degwt_sr_compose_fires=nys_sr_fires,
        compose_scr_fails=compose_scr_fails, arms_differ=arms_differ, finite=finite, leak_free=leak_ok,
        leak_audit=leak, selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"],
    )
    ok = bool(real_ok and lap_recovers and lap_beats_null and embedding_separates and compose_scr_fails
              and leak_ok and arms_differ and finite and vp_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s d_code=%s svd_iter=%s sr_gamma=%s"
         % (run_mode, seeds, cfg["d_code"], cfg["svd_n_iter"], SR_GAMMA))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s | flat_fires=%s degwt_fires=%s degwt_sr_fires=%s leak_free=%s "
         "embedding_separates=%s real_code=%s vp_ok=%s n_sigs=%s"
         % (st_ok, st_res.get("flat_compose_fires"), st_res.get("degwt_compose_fires"),
            st_res.get("degwt_sr_compose_fires"), st_res.get("leak_free"),
            st_res.get("embedding_separates"), st_res.get("real_code_path_ok"), st_res.get("validity_preflight_ok"),
            st_res.get("n_distinct_sigs")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s"
                        % {kk: st_res.get(kk) for kk in ("lap_recovers", "flat_compose_fires", "degwt_compose_fires",
                           "degwt_sr_compose_fires", "leak_free", "real_code_path_ok", "arms_differ",
                           "validity_preflight_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS GRAPH_SPECTRAL_COMPOSE_SR_PPMI_NYSTROM: planted SBM -- LAP spectral codebook "
                        "recovers planted held-out tails + embedding separates blocks; BOTH flat AND degree-weighted "
                        "compose over TRUE support-neighbors beat their scrambled controls; leak_audit clean "
                        "(train-only codes, disjoint support/query, held-out tails train-degree 0); REAL KGStore + "
                        "both OOS compose paths exercised; 7 validity-preflight checks declared (F.1-F.4 ENFORCE)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not G._ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = G.build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, _fs = run_corpus(pool, cfg, seed, "CSKG_CORE_HELDOUT_ENTITY")
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", 20):
                raise RuntimeError("held-out query edges too few (%d)" % res.get("n_query_scored", 0))
            sigset = set(res["arm_sigs"][a] for a in ALL_ARMS)
            if len(sigset) < 8:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d sigs" % (seed, len(sigset)))
            if not res["diag"]["finite"]:
                raise RuntimeError("non-finite W seed=%d" % seed)
            if not res["diag"]["leak"]["leak_free"]:
                raise RuntimeError("LEAK_AUDIT_BREACH seed=%d %s" % (seed, res["diag"]["leak"]))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            ah = res["arm_hits"]
            _log("seed=%d nq=%d | FLAT LAP=%s PPMI=%s SR=%s RAND=%s | DEGWT LAP=%s SR=%s RAND=%s | "
                 "SCR PPMI_F=%s SR_F=%s LAP_N=%s SR_N=%s | ORACLE R=%s L=%s P=%s S=%s NULL=%s leak=%s (%.1fs)"
                 % (seed, res["n_query_scored"],
                    _fmt(ah[LAP_COMPOSE_FLAT][CEIL_METRIC]), _fmt(ah[PPMI_COMPOSE_FLAT][CEIL_METRIC]),
                    _fmt(ah[SR_COMPOSE_FLAT][CEIL_METRIC]), _fmt(ah[RAND_COMPOSE][CEIL_METRIC]),
                    _fmt(ah[LAP_COMPOSE_NYS][CEIL_METRIC]), _fmt(ah[SR_COMPOSE_NYS][CEIL_METRIC]),
                    _fmt(ah[RAND_COMPOSE_NYS][CEIL_METRIC]),
                    _fmt(ah[PPMI_COMPOSE_FLAT_SCRAMBLE][CEIL_METRIC]), _fmt(ah[SR_COMPOSE_FLAT_SCRAMBLE][CEIL_METRIC]),
                    _fmt(ah[LAP_COMPOSE_NYS_SCRAMBLE][CEIL_METRIC]), _fmt(ah[SR_COMPOSE_NYS_SCRAMBLE][CEIL_METRIC]),
                    _fmt(ah[RAND_ORACLE][CEIL_METRIC]), _fmt(ah[LAP_ORACLE][CEIL_METRIC]),
                    _fmt(ah[PPMI_ORACLE][CEIL_METRIC]), _fmt(ah[SR_ORACLE][CEIL_METRIC]),
                    _fmt(ah[RAND_NULL][CEIL_METRIC]), res["diag"]["leak"]["leak_free"], time.time() - ts))
            _hb("cskg", si + 1)
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
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = lift_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
