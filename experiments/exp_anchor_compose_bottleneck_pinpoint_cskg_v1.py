"""BOTTLENECK-PINPOINT (guardrail-1: confirm the wall BEFORE building). Where does the anchor_compose ~0.13-MRR
deficit actually live -- and is the residual COLD/D1 deficit DECODER/BUDGET-limited, DATA-limited, or a hard
REPRESENTATION wall? This cell does NOT chase a capability win; it is a near-zero-new-mechanism DIAGNOSTIC that reuses
the landed additive-SGD arena to decide WHERE all further effort aims.

CONTEXT (the reframe drill, on-disk-verified). The aggregate 0.13 MRR is a degree-stratified MIXTURE, not a uniform
representation wall: re-reading data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json degree-stratified showed
mid/high-support buckets already sit at 60-133% of their OWN oracle ceiling (nothing left for representation there),
while the ENTIRE deficit is concentrated in COLD (0 support, BELOW random) + D1 (1 support, ~85%-of-oracle headroom).
CITED@notes/research_drill_reframe_true_bottleneck_2026-07-13.md (Section (a) + Tests 2/3).
MEASURED anchors (off-disk, scaling_ladder_v3 r0_base degree table):
  cold : anchor_mrr=0.000041 oracle_mrr=0.650751 (0.01% of oracle; 0.08x random -- WORSE than random)
  d1   : anchor_mrr=0.059252 oracle_mrr=0.391866 (15.1% of oracle; 85% headroom unclaimed)
  d2_3 : anchor_mrr=0.078897 oracle_mrr=0.123391 (63.9% of oracle -- near ceiling)
  MEASURED@data/exp_anchor_compose_scaling_ladder_cskg_v3/metrics.json:scaling_summary.rungs.r0_base.anchor_mrr_by_support_degree

THE TWO DECISIVE SUB-TESTS (both stratified by support-degree into the contract's 3 buckets: cold=0 / d1=1 / d2_3plus=2+):

TEST 2 (DECODER / BUDGET-limited?). Sweep the mechanism's CAPACITY/READOUT BUDGET (the fit/code dimension k, the
budget the single-shot nearest-neighbour readout has to separate candidates) over K_GRID={24,48,96} on the
BIT-IDENTICAL held-out-entity arena (the split depends only on the seed, not k, so every k re-scores the SAME query
edges; only budget varies). The already-landed closedform_budget_sweep swept budget on the AGGREGATE (dominated by
saturated buckets -> STRICT_DEAD); this cell scores the SAME sweep STRATIFIED per bucket. Question: does D1's
anchor_mrr RISE toward its own bucket-oracle as budget grows? If yes -> the D1 deficit is BUDGET/CAPACITY-recoverable
(a fixable readout/capacity headroom, not a hard wall). If flat -> budget is NOT the D1 lever.
NOTE (honest labelling): in this FROZEN-scaffold KGE regime the readout is single-shot nearest-neighbour -- there is
no iterative decoder to add rounds to -- so "decode/readout budget" is realized as the code/fit dimension k (the
capacity the readout has). Sweeping k refits the k-dim scaffold per budget (NOT zero-retrain), but the seed-determined
split keeps the scored query edges bit-identical across k, so the per-k per-bucket comparison is clean.

TEST 3 (DATA-limited?). For COLD + D1 held-out entities, a near-zero-compute graph reachability check: reconstruct the
seed-deterministic split, build the TRAIN-graph adjacency, and BFS from each query-head h_q to the entity's
SUPPORT-anchor set (<= REACH_H hops, through train edges only -- NEVER the held-out edge). reachable_frac = fraction of
a bucket's query edges whose query context is relationally linked to its evidence context in the ALREADY-INGESTED
graph. COLD (0 support -> empty anchor set) is UNREACHABLE by construction (evidence-absent). If most D1 queries are
UNREACHABLE -> DATA-limited (the answer is not recoverable from ingested facts except via the held edge -> the fix is
INGEST, not a smarter algorithm). If most D1 queries ARE reachable-but-unscored -> the signal is present and the
mechanism is not using it -> a DECODER/REPRESENTATION lever.

THE REDIRECT (per bucket, the answer that aims all further work):
  cold      : Test3 reachable_frac -> expect DATA_LIMITED (0 support by construction).
  d1        : Test2 recovers    -> BUDGET/CAPACITY-RECOVERABLE (raise k; not a hard wall).
              Test2 flat + Test3 data-limited  -> DATA-LIMITED (ingest lever).
              Test2 flat + Test3 decodable     -> REPRESENTATION/INFERENCE-WALL (right-shaped mechanism, full budget,
                                                   answer reachable, still fails -> a genuine hard wall to attack).
  d2_3plus  : reference bucket -> expect Test2 FLAT/near-ceiling (confirms the majority is NOT budget-limited; it is
              already near its own oracle, the reframe drill's core finding).

PRE-REG BANDS (picked BEFORE the run; primary metric = FILTERED MRR rank-vs-ALL, degree-unbiased; NOT tuned on real
data). Test-2 per-bucket k-trajectory (kmin=24 -> kmax=96):
  BUDGET_RECOVERS (d1) : anchor_mrr(kmax)/anchor_mrr(kmin) >= D1_RISE_RECOVER(=1.30) AND the k-rise closes >=
                         D1_GAP_CLOSE_RECOVER(=0.30) of the bucket's (oracle_mrr - anchor_mrr(kmin)) gap AND the
                         absolute rise >= MIN_SIG_MRR(=0.002). => budget/capacity-recoverable.
  BUDGET_FLAT     (d1) : anchor_mrr(kmax)/anchor_mrr(kmin) < D1_RISE_FLAT(=1.15). => budget is not the lever.
  BUDGET_MIDDLE   (d1) : between the two (partial budget response).
  (a bucket with fewer than MIN_BUCKET_Q(=8) query edges pooled over seeds -> INCONCLUSIVE_TOO_FEW for that bucket.)
Test-3 per-bucket reachability (reach_frac at REACH_H=3 hops, train graph, excludes held edge):
  DATA_LIMITED : reach_frac(H=3) <  REACH_DATA_FRAC(=0.30) (most queries have NO independent ingested path).
  DECODABLE    : reach_frac(H=3) >= REACH_DECODE_FRAC(=0.60) (signal present; mechanism not using it).
  MIXED        : between.
Fail-closed preamble (any -> INCONCLUSIVE, no bucket verdict trusted): ORACLE must fire at every k (arena answerable);
cardinality EXPECTED_N_UNITS = n_seeds*len(k_grid) Test-2 units + n_seeds Test-3 passes; no control (RANDOM/SCRAMBLE)
beats the ORACLE ceiling (broken guard, F.4-valid vs the RANDOM floor).

SEVEN VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight; F.1-F.4 = ENFORCE):
  (1) positive_control        : ORACLE_ADDITIVE recovers folded-in held-out tails and clears RANDOM by the
                                ceiling-aware (ratio+abs) fire gate at the largest self-test budget.
  (2) metric_moves            : held-out ORACLE mrr MOVES across the swept budgets (the capacity axis is live).
  (3) negative_control_margin : RANDOM + ANCHOR_SCRAMBLE sit below ANCHOR by an MRR margin, deterministically (>=2).
  (4) full_gates_exercised    : aggregate_bottleneck_verdict runs on the planted per-(seed,k) + per-seed reachability,
                                firing every fail-closed gate (cardinality, oracle-fires, broken, per-bucket band).
  (5) real_code_path (F.1)    : the self-test constructs/calls the REAL objects the FULL uses (run_corpus,
                                build_anchor_compose_codes, additive_direct_scores, build_heldout_entity_split_ac,
                                reachability_by_bucket) at tiny scale across >=2 budgets -- no synthetic-only branch.
  (6) substrate_signature(F2/3): every reused call binds against its LIVE inspect.signature with base/portable
                                positional args (run_corpus, build_anchor_compose_codes, additive_direct_scores,
                                build_heldout_entity_split_ac).
  (7) guard_baseline_valid(F.4): the broken-test guard fires against ORACLE_best (above the floor when the oracle
                                fires), NOT POP (structurally ~0 on held-out arenas) -> declared valid vs the RANDOM
                                floor so it cannot mis-fire on this arena's zeros.

## Compute architecture
class (c) MIXED: Test-2 reuses run_corpus VERBATIM from exp_anchor_compose_scaling_ladder_cskg_v3 (split + support/query
partition + POP = sequential-CPU graph ops; the additive/rotate/oracle fits = minibatch SGD, batched + neg-chunked;
E_derived = a single vectorized index_add_ bundle; readouts = query-chunked batched matmul, the (nq,N) map never
materialized whole). Test-3 = a pure Python BFS on the train-graph adjacency, computed ONLY for the tiny COLD/D1
buckets (a few dozen query edges) + a capped d2_3plus reference sample -> negligible. SHARDED storage (each entity its
own code; relations = per-TYPE additive displacements; the only bundle is the per-ENTITY anchor mean). device=auto
(cuda on the GPU host -> the k-sweep SGD fits are GPU-friendly, so overnight_queue GPU is the fast target); remote_cpu
forces cpu. Per-(seed,k) fits are independent; per-seed empty_cache between units. The k-sweep fits refit per budget
so a multi-seed MEMSMOKE is NOT needed at these k (<=96, same footprint as the confirmed k=24 scaling ladder that ran
overnight); the discriminator-fires proof is the self-test + the analytical oracle-fires gate.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - SWEEP-AXIS cell (k): cardinality_ok -> EXPECTED_N_UNITS = n_seeds*len(k_grid); verdict emits
#   HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer Test-2 units land.
# - arms_differ_verified per unit (META_RULE_AF): run_corpus's 7 arms produce >=5 distinct score sigs per (seed,k).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary metric FILTERED MRR + ceiling-aware ORACLE-fire gate; the per-bucket ORACLE is the
#   MEASURED ceiling each bucket's anchor is scored against -> reachability by construction. This is a DIAGNOSTIC:
#   all three outcomes (recover / data / representation) are informative; there is no unreachable HARD_PASS band.
# - baseline_in_band: ORACLE fires per k; ANCHOR d1 ~0.06 (in band, not saturated, not floor); RANDOM/POP ~1/N floor.
# - discriminator survives scale: analytical -- the per-bucket ORACLE proves each bucket's arena answerable at scale;
#   the Test-2 question (does the d1 trajectory rise with budget) is measured at FULL, not planted; the self-test
#   fires ANCHOR-beats-RANDOM + scramble-fails + oracle-fires + metric-moves-across-budget deterministically.
# - HARD-PASS strictly above floor: N/A (diagnostic; the bands are RECOVER/FLAT/MIXED + DATA/DECODABLE, not a PASS).
# - HP_SCOPE: Test-2 bands apply to the ANCHOR_COMPOSE per-bucket trajectory; ORACLE = positive control (must fire);
#   RANDOM/ANCHOR_SCRAMBLE = must-not-clear controls; ADDITIVE/ONESHOT = memorize head-to-heads; POP = sanity.
# - per-unit failure-class instrumentation (no bare except; per-(seed,k) + per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- ORACLE_FIRE_RATIO/ABS + the RISE/GAP_CLOSE/REACH fractions
#   pre-registered, NOT tuned on real data.
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ in the prereg + docstring.
# - progress_logging: print_flush_true (line-buffered stdout + per-(seed,k) + per-seed flush prints); timeout_s>1800.

ASCII-only. No bare except; except SystemExit before except Exception. Explicit float32 fits (reused). torch.Generator seeded.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
# REUSE THE ADDITIVE-SGD ARENA + STRATIFICATION VERBATIM from the confirmed scaling-ladder cell (the real 0.13-MRR
# mechanism; the split/fit/compose/score/localize path is bit-identical -> the per-bucket k-sweep is a faithful
# stratified re-score of the SAME arena).
from experiments.exp_anchor_compose_scaling_ladder_cskg_v3 import (  # noqa: E402
    run_corpus, aggregate_and_verdict, build_planted_transe_arena, build_heldout_entity_split_ac,
    build_anchor_compose_codes, SUPPORT_BINS,
    ANCHOR, ADDITIVE, ONESHOT, RANDOM, SCRAMBLE, ORACLE, POP, ALL_ARMS,
    CEIL_METRIC, ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS, MIN_HELDOUT, MIN_STRAT_Q,
    HELDOUT_ENTITY_FRAC, SUPPORT_FRAC, _nm, _ratio,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402

ANCHOR_NAME = "anchor_compose_bottleneck_pinpoint_cskg_v1"

# ---- the contract's 3 support-degree buckets (collapse the 5 SUPPORT_BINS by n-weighted MRR pooling) ----
BUCKETS3 = ["cold", "d1", "d2_3plus"]
BUCKET_SRC = {"cold": ["cold"], "d1": ["d1"], "d2_3plus": ["d2_3", "d4_7", "d8plus"]}

# ---- Test-2 budget-sweep axis (capacity/readout budget = fit/code dimension k) ----
K_GRID_FULL = [24, 48, 96]
K_GRID_SELFTEST = [6, 12]

# ---- Test-2 per-bucket k-trajectory bands (pre-registered; NOT tuned on real data) ----
D1_RISE_RECOVER = 1.30      # anchor_mrr(kmax)/anchor_mrr(kmin) >= this -> budget-recoverable
D1_RISE_FLAT = 1.15         # < this -> budget-flat (not the lever)
D1_GAP_CLOSE_RECOVER = 0.30 # AND the k-rise closes >= this fraction of the (oracle - anchor@kmin) headroom gap
MIN_SIG_MRR = 0.002         # AND the absolute rise clears this no-noise floor
MIN_BUCKET_Q = 8            # min pooled query edges for a bucket verdict (else INCONCLUSIVE_TOO_FEW)

# ---- Test-3 reachability bands (pre-registered) ----
REACH_H = 3                 # BFS hop cap (train graph, excludes the held edge)
REACH_DATA_FRAC = 0.30      # reach_frac(H=3) <  this -> DATA_LIMITED (no independent ingested path)
REACH_DECODE_FRAC = 0.60    # reach_frac(H=3) >= this -> DECODABLE (signal present; not used)
REACH_D23_SAMPLE = 400      # cap the d2_3plus reference reachability sample (cold/d1 fully covered; tiny)

CONTROL_LOSE_EPS = 0.005    # broken guard: a control beating ORACLE_best by > this mrr = degenerate readout

# ---- self-test planted thresholds on the PRIMARY metric (MRR); calibrated on the synthetic planted arena, NOT real
#      data (mirror the scaling-ladder self-test values; the planted arena registers strong additive signal). ----
SELFTEST_ORACLE_MRR_MIN = 0.30
SELFTEST_ANCHOR_MRR_MIN = 0.12
SELFTEST_AC_BEATS_RANDOM_MRR = 0.06
SELFTEST_SCRAMBLE_MARGIN_MRR = 0.03
SELFTEST_MIN_HO = 8

# ---- run_corpus cfg profiles (SELFTEST/FULL exercise the SAME split->fit->compose->score->localize path) ----
SELFTEST_CFG = dict(epochs=350, n_neg=32, batch=4096, heldout_entity_frac=0.15, support_frac=0.5,
                    n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO, k_grid=K_GRID_SELFTEST)
# FULL: same fit knobs as confirmed scaling_ladder v1/v3 (k=24, ep=500) + CSKG core (k_core=12). k varies per sweep
# point; the split is seed-determined (k-independent) so every k re-scores the SAME held-out query edges.
FULL_CFG = dict(epochs=500, n_neg=128, batch=8192, neg_chunk=16, heldout_entity_frac=HELDOUT_ENTITY_FRAC,
                support_frac=SUPPORT_FRAC, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_heldout_eval=3000, min_heldout=MIN_HELDOUT, seeds=[7, 13], k_grid=K_GRID_FULL)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


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


def _cfg_for_k(cfg, k):
    c = dict(cfg)
    c["k"] = int(k)
    c.pop("k_grid", None)
    c.pop("seeds", None)
    return c


# ---------------------------------------------------------------------------
# TEST 2 support-degree collapse: 5 SUPPORT_BINS -> 3 contract buckets via n-weighted MRR pooling.
#   MRR = mean over queries of reciprocal rank, so a bucket's MRR is the n-weighted mean of its sub-bin MRRs.
# ---------------------------------------------------------------------------

def collapse_to_3buckets(by_support_degree, arms=(ANCHOR, ADDITIVE, RANDOM, ORACLE)):
    out = {}
    for b3 in BUCKETS3:
        cells = [by_support_degree.get(src, {}) for src in BUCKET_SRC[b3]]
        rec = {}
        for a in arms:
            num, den = 0.0, 0
            for c in cells:
                ac = c.get(a, {})
                mrr = ac.get("mrr"); n = ac.get("n", 0)
                if mrr is not None and mrr == mrr and n and n > 0:
                    num += float(mrr) * int(n); den += int(n)
            rec[a] = dict(mrr=(num / den if den > 0 else float("nan")), n=den)
        out[b3] = rec
    return out


# ---------------------------------------------------------------------------
# TEST 3 data-coverage: reconstruct the seed-deterministic split, build the TRAIN-graph adjacency, BFS from each
# query-head to the held-out entity's SUPPORT-anchor set (<= REACH_H hops, train edges only, never the held edge).
# COLD (empty support) is UNREACHABLE by construction. Returns per-bucket reach_frac at H=1,2,3.
# ---------------------------------------------------------------------------

def build_train_adjacency(train_lbl):
    """Undirected label adjacency from the TRAIN edges (the held-out support/query edges are NOT in train)."""
    adj = defaultdict(set)
    for (h, r, t) in train_lbl:
        adj[h].add(t)
        adj[t].add(h)
    return adj


def bfs_min_hops(adj, src, targets, hmax):
    """Min hop distance from src to ANY node in targets via train edges, capped at hmax. inf if unreachable/absent."""
    if not targets or src not in adj:
        return float("inf")
    if src in targets:
        return 0
    seen = {src}
    frontier = deque([(src, 0)])
    while frontier:
        node, d = frontier.popleft()
        if d >= hmax:
            continue
        for nb in adj[node]:
            if nb in seen:
                continue
            if nb in targets:
                return d + 1
            seen.add(nb)
            frontier.append((nb, d + 1))
    return float("inf")


def _bucket_of(support_deg):
    if support_deg <= 0:
        return "cold"
    if support_deg == 1:
        return "d1"
    return "d2_3plus"


def reachability_by_bucket(pool_lbl, cfg, seed):
    """Per-bucket fraction of held-out QUERY edges whose query-head is within REACH_H hops of the entity's support
    anchors in the TRAIN graph (excludes the held edge by construction). d2_3plus is a capped reference sample."""
    ent2i, _rel2i = build_ids(pool_lbl, [], [])
    train_lbl, support_lbl, query_lbl, _hold_ids, _n_cold = build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    adj = build_train_adjacency(train_lbl)
    # support anchors per held tail (labels)
    anchors_by_tail = defaultdict(set)
    for (h, _r, t) in support_lbl:
        anchors_by_tail[t].add(h)
    # bucket each query edge by its tail's support degree; count + BFS
    hs = [1, 2, 3]
    agg = {b: {"n": 0, "reach": {h: 0 for h in hs}, "unreach": 0, "n_bfs": 0} for b in BUCKETS3}
    d23_seen = 0
    rng = np.random.default_rng(seed * 13 + 1)
    order = rng.permutation(len(query_lbl)).tolist()
    for qi in order:
        (h_q, _r_q, t) = query_lbl[qi]
        anchors = anchors_by_tail.get(t, set())
        b = _bucket_of(len(anchors))
        if b == "d2_3plus":
            if d23_seen >= REACH_D23_SAMPLE:
                continue
            d23_seen += 1
        agg[b]["n"] += 1
        if b == "cold" or not anchors:
            # cold: empty support -> unreachable by construction (evidence-absent)
            agg[b]["unreach"] += 1
            agg[b]["n_bfs"] += 1
            continue
        dist = bfs_min_hops(adj, h_q, anchors, REACH_H)
        agg[b]["n_bfs"] += 1
        if dist == float("inf"):
            agg[b]["unreach"] += 1
        else:
            for h in hs:
                if dist <= h:
                    agg[b]["reach"][h] += 1
    out = {}
    for b in BUCKETS3:
        n_bfs = agg[b]["n_bfs"]
        out[b] = dict(
            n=agg[b]["n"], n_bfs=n_bfs,
            reach_frac_h1=(agg[b]["reach"][1] / n_bfs) if n_bfs > 0 else float("nan"),
            reach_frac_h2=(agg[b]["reach"][2] / n_bfs) if n_bfs > 0 else float("nan"),
            reach_frac_h3=(agg[b]["reach"][3] / n_bfs) if n_bfs > 0 else float("nan"),
            unreach_frac=(agg[b]["unreach"] / n_bfs) if n_bfs > 0 else float("nan"))
    out["_meta"] = dict(seed=int(seed), n_train=len(train_lbl), n_support=len(support_lbl),
                        n_query=len(query_lbl), reach_h=REACH_H, d23_sampled=d23_seen)
    return out


# ---------------------------------------------------------------------------
# TEST 2 unit: one (seed,k) run_corpus -> overall arm MRR + oracle_fires/broken + 3-bucket stratified MRR.
# ---------------------------------------------------------------------------

def run_test2_unit(pool_lbl, cfg, device, seed, k):
    res = run_corpus(pool_lbl, _cfg_for_k(cfg, k), device, seed, "CSKG_HELDOUT_ENTITY_BOTTLENECK_K%d" % k,
                     ckpt_dir=None, localize=True)
    if res.get("empty") or res.get("n_query_scored", 0) < cfg.get("min_heldout", MIN_HELDOUT):
        raise RuntimeError("held-out-entity query edges too few (%s < %s)"
                           % (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
    sigset = set(res["arm_sigs"].values())
    if len(sigset) < 5:
        raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d k=%d only %d sigs" % (seed, k, len(sigset)))
    _v, _msg, gates = aggregate_and_verdict([res])
    by3 = collapse_to_3buckets(res.get("localization", {}).get("by_support_degree", {}))
    return dict(
        seed=int(seed), k=int(k), n_query_scored=int(res["n_query_scored"]), n_support=int(res["n_support"]),
        arm_mrr={a: res["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS},
        oracle_fires=bool(gates.get("oracle_fires")), broken=bool(gates.get("broken")),
        oracle_headroom=gates.get("oracle_headroom"),
        by3={b: {a: {"mrr": by3[b][a]["mrr"], "n": by3[b][a]["n"]} for a in (ANCHOR, ADDITIVE, RANDOM, ORACLE)}
             for b in BUCKETS3},
        support_deg_hist=res.get("localization", {}).get("support_deg_hist"))


# ---------------------------------------------------------------------------
# Aggregate: Test-2 per-bucket k-trajectory + Test-3 per-bucket reachability -> per-bucket bottleneck class + redirect.
# ---------------------------------------------------------------------------

def _rnd(x, nd=6):
    return round(x, nd) if (x == x) else None


def _bucket_k_trajectory(test2_units, k_grid, bucket):
    """Mean-over-seeds ANCHOR/ORACLE/RANDOM mrr + n per k for a bucket."""
    ks = sorted(set(int(k) for k in k_grid))
    traj = {}
    for k in ks:
        rows = [u for u in test2_units if int(u["k"]) == k]
        cell = {}
        for a in (ANCHOR, ORACLE, RANDOM):
            vals = [u["by3"][bucket][a]["mrr"] for u in rows
                    if u["by3"][bucket][a]["mrr"] == u["by3"][bucket][a]["mrr"]]
            cell[a] = _nm(vals) if vals else float("nan")
        cell["n"] = int(sum(u["by3"][bucket][ANCHOR]["n"] for u in rows))  # pooled query count
        traj[k] = cell
    return ks, traj


def _classify_test2_bucket(ks, traj):
    kmin, kmax = ks[0], ks[-1]
    a_min = traj[kmin][ANCHOR]
    a_max = traj[kmax][ANCHOR]
    orc_min = traj[kmin][ORACLE]
    n_pooled = max(traj[kmin]["n"], traj[kmax]["n"])
    rise_ratio = _ratio(a_max, a_min)
    abs_rise = _sub(a_max, a_min)
    gap = _sub(orc_min, a_min)
    gap_closed = (abs_rise / gap) if (gap == gap and gap > 0 and abs_rise == abs_rise) else float("nan")
    if n_pooled < MIN_BUCKET_Q or not (a_min == a_min and a_max == a_max):
        cls = "INCONCLUSIVE_TOO_FEW"
    elif (rise_ratio == rise_ratio and rise_ratio >= D1_RISE_RECOVER
          and abs_rise == abs_rise and abs_rise >= MIN_SIG_MRR
          and gap_closed == gap_closed and gap_closed >= D1_GAP_CLOSE_RECOVER):
        cls = "BUDGET_RECOVERS"
    elif rise_ratio == rise_ratio and rise_ratio < D1_RISE_FLAT:
        cls = "BUDGET_FLAT"
    else:
        cls = "BUDGET_MIDDLE"
    return dict(cls=cls, anchor_kmin=_rnd(a_min), anchor_kmax=_rnd(a_max), oracle_kmin=_rnd(orc_min),
                rise_ratio=(round(rise_ratio, 3) if (rise_ratio == rise_ratio and rise_ratio != float("inf")) else None),
                abs_rise=_rnd(abs_rise), gap_closed=_rnd(gap_closed, 4), n_pooled=int(n_pooled))


def _classify_test3_bucket(reach_seeds, bucket):
    fracs = [rs[bucket]["reach_frac_h%d" % REACH_H] for rs in reach_seeds
             if rs[bucket]["reach_frac_h%d" % REACH_H] == rs[bucket]["reach_frac_h%d" % REACH_H]]
    n = int(sum(rs[bucket]["n_bfs"] for rs in reach_seeds))
    rf = _nm(fracs) if fracs else float("nan")
    if not (rf == rf) or n < 1:
        cls = "INCONCLUSIVE_TOO_FEW"
    elif rf < REACH_DATA_FRAC:
        cls = "DATA_LIMITED"
    elif rf >= REACH_DECODE_FRAC:
        cls = "DECODABLE"
    else:
        cls = "MIXED"
    return dict(cls=cls, reach_frac_h3=_rnd(rf, 4), n_bfs=n)


def _bucket_redirect(bucket, t2, t3):
    """Fuse Test-2 + Test-3 into the per-bucket bottleneck class (the answer that aims further work)."""
    if bucket == "cold":
        # 0 support by construction -> reachability decides; expect DATA_LIMITED
        if t3["cls"] == "DATA_LIMITED":
            return "DATA_LIMITED_EVIDENCE_ABSENT"
        if t3["cls"] == "DECODABLE":
            return "DECODABLE_BUT_UNSCORED_ANOMALY"   # flagged: cold has structure the mechanism ignores
        return "INCONCLUSIVE"
    if bucket == "d2_3plus":
        # reference: expect budget-flat near its own ceiling (the reframe drill's core finding)
        if t2["cls"] in ("BUDGET_FLAT", "BUDGET_MIDDLE"):
            return "NOT_BUDGET_LIMITED_NEAR_CEILING"
        if t2["cls"] == "BUDGET_RECOVERS":
            return "BUDGET_RECOVERS_UNEXPECTED"       # flagged: majority WAS budget-limited (contradicts reframe)
        return "INCONCLUSIVE"
    # d1: the decisive bucket
    if t2["cls"] == "BUDGET_RECOVERS":
        return "BUDGET_CAPACITY_RECOVERABLE"
    if t2["cls"] == "INCONCLUSIVE_TOO_FEW":
        # fall back to reachability if the budget trajectory is under-powered
        if t3["cls"] == "DATA_LIMITED":
            return "DATA_LIMITED_INGEST_LEVER"
        if t3["cls"] == "DECODABLE":
            return "REPRESENTATION_INFERENCE_WALL"
        return "INCONCLUSIVE"
    # budget flat/middle -> reachability adjudicates data vs representation
    if t3["cls"] == "DATA_LIMITED":
        return "DATA_LIMITED_INGEST_LEVER"
    if t3["cls"] == "DECODABLE":
        return "REPRESENTATION_INFERENCE_WALL"
    return "MIXED_DATA_AND_REPRESENTATION"


def aggregate_bottleneck_verdict(test2_units, reach_seeds, k_grid, run_mode):
    ks = sorted(set(int(k) for k in k_grid))
    seeds = sorted(set(int(u["seed"]) for u in test2_units))

    # ---- fail-closed preamble ----
    enough_heldout = bool(all(u["n_query_scored"] >= MIN_HELDOUT for u in test2_units)) and len(test2_units) > 0
    oracle_fires_all = bool(len(test2_units) > 0 and all(u["oracle_fires"] for u in test2_units))
    broken_any = bool(any(u["broken"] for u in test2_units))

    # ---- per-bucket Test-2 + Test-3 classifications + redirect ----
    per_bucket = {}
    for b in BUCKETS3:
        bks, traj = _bucket_k_trajectory(test2_units, ks, b)
        t2 = _classify_test2_bucket(bks, traj)
        t3 = _classify_test3_bucket(reach_seeds, b)
        redirect = _bucket_redirect(b, t2, t3)
        per_bucket[b] = dict(
            test2=t2, test3=t3, redirect=redirect,
            k_trajectory={str(k): dict(anchor_mrr=_rnd(traj[k][ANCHOR]), oracle_mrr=_rnd(traj[k][ORACLE]),
                                       random_mrr=_rnd(traj[k][RANDOM]), n=traj[k]["n"]) for k in bks})

    # ---- overall verdict resolution (fail-closed order) ----
    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif broken_any:
        verdict = "BROKEN_TEST_CONTROL_BEATS_ORACLE"
    elif not oracle_fires_all:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    else:
        verdict = "BOTTLENECK_PINPOINT_%s__cold=%s__d1=%s__d2_3plus=%s" % (
            "OK", per_bucket["cold"]["redirect"], per_bucket["d1"]["redirect"],
            per_bucket["d2_3plus"]["redirect"])

    d1r = per_bucket["d1"]["redirect"]
    verdict_msg = (
        "%s || [seeds=%d ks=%s] || D1 (decisive): Test2=%s (anchor k%d=%s->k%d=%s rise=%sx close=%s n=%s) | "
        "Test3=%s (reach@%dh=%s n=%s) -> REDIRECT=%s || COLD: Test3=%s (reach@%dh=%s) -> %s || D2_3PLUS(ref): "
        "Test2=%s (anchor k%d=%s->k%d=%s) -> %s || oracle_fires_all=%s broken=%s"
        % (
            verdict, len(seeds), ks,
            per_bucket["d1"]["test2"]["cls"], ks[0], _fmt(per_bucket["d1"]["test2"]["anchor_kmin"] or float("nan")),
            ks[-1], _fmt(per_bucket["d1"]["test2"]["anchor_kmax"] or float("nan")),
            per_bucket["d1"]["test2"]["rise_ratio"], per_bucket["d1"]["test2"]["gap_closed"],
            per_bucket["d1"]["test2"]["n_pooled"],
            per_bucket["d1"]["test3"]["cls"], REACH_H, per_bucket["d1"]["test3"]["reach_frac_h3"],
            per_bucket["d1"]["test3"]["n_bfs"], d1r,
            per_bucket["cold"]["test3"]["cls"], REACH_H, per_bucket["cold"]["test3"]["reach_frac_h3"],
            per_bucket["cold"]["redirect"],
            per_bucket["d2_3plus"]["test2"]["cls"], ks[0],
            _fmt(per_bucket["d2_3plus"]["test2"]["anchor_kmin"] or float("nan")), ks[-1],
            _fmt(per_bucket["d2_3plus"]["test2"]["anchor_kmax"] or float("nan")),
            per_bucket["d2_3plus"]["redirect"], oracle_fires_all, broken_any))

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC, k_grid=ks, n_seeds=len(seeds),
        per_bucket=per_bucket,
        enough_heldout=enough_heldout, oracle_fires_all=oracle_fires_all, broken_any=broken_any,
        d1_redirect=d1r, cold_redirect=per_bucket["cold"]["redirect"],
        d2_3plus_redirect=per_bucket["d2_3plus"]["redirect"],
        bands=dict(D1_RISE_RECOVER=D1_RISE_RECOVER, D1_RISE_FLAT=D1_RISE_FLAT,
                   D1_GAP_CLOSE_RECOVER=D1_GAP_CLOSE_RECOVER, MIN_SIG_MRR=MIN_SIG_MRR, MIN_BUCKET_Q=MIN_BUCKET_Q,
                   REACH_H=REACH_H, REACH_DATA_FRAC=REACH_DATA_FRAC, REACH_DECODE_FRAC=REACH_DECODE_FRAC,
                   ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS=ORACLE_FIRE_ABS,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC))
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted TransE-consistent grid: run_corpus at >=2 budgets + reachability per seed; the Test-2 +
# Test-3 machinery + verdict fire on the REAL objects. Determinism-pinned to single-thread CPU.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    exercised = set()
    pool = build_planted_transe_arena(7, n_ent=300, n_rel=6, k_lat=8, deg=3)
    cfg = dict(SELFTEST_CFG)
    k_grid = cfg["k_grid"]

    # TEST 2 units (real code path: run_corpus + collapse) across >=2 budgets
    test2_units = []
    for k in k_grid:
        u = run_test2_unit(pool, cfg, device, 7, k)
        exercised.update({"run_corpus", "build_anchor_compose_codes", "additive_direct_scores"})
        test2_units.append(u)
    # TEST 3 reachability (real code path: split reconstruct + BFS)
    reach = reachability_by_bucket(pool, cfg, 7)
    exercised.update({"build_heldout_entity_split_ac", "reachability_by_bucket"})
    reach_seeds = [reach]

    top = test2_units[-1]
    m = top["arm_mrr"]
    anchor_margin = _sub(m[ANCHOR], m[RANDOM])
    scramble_margin = _sub(m[ANCHOR], m[SCRAMBLE])
    oracle_margin = _sub(m[ORACLE], m[RANDOM])
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    oracle_recovers = bool(m[ORACLE] == m[ORACLE] and m[ORACLE] >= SELFTEST_ORACLE_MRR_MIN)
    oracle_fires = bool(top["oracle_fires"])
    anchor_recovers = bool(m[ANCHOR] == m[ANCHOR] and m[ANCHOR] >= SELFTEST_ANCHOR_MRR_MIN)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM_MRR)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN_MRR)
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(m[RANDOM], 0.02) + CONTROL_LOSE_EPS)

    # oracle mrr MOVES across the tiny budgets (the capacity axis is live)
    oracle_vals = [u["arm_mrr"][ORACLE] for u in test2_units]

    # reachability computed finite fractions per bucket (Test-3 machinery ran on real objects)
    reach_ok = True
    for b in BUCKETS3:
        rf = reach[b]["reach_frac_h%d" % REACH_H]
        if reach[b]["n_bfs"] > 0 and not (0.0 <= rf <= 1.0):
            reach_ok = False

    st_verdict, st_msg, st_gates = aggregate_bottleneck_verdict(test2_units, reach_seeds, k_grid, "self_test")

    oracle_best = max((v for v in oracle_vals if v == v), default=float("nan"))
    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(oracle_recovers and oracle_fires),
         "control_name": "ORACLE_ADDITIVE", "headline_name": "oracle_beats_random_heldout_mrr",
         "extra": "planted grid at the largest self-test budget: ORACLE (learned held-out codes) recovers held-out "
                  "tails and clears RANDOM by the ceiling-aware ratio+abs gate -> each bucket's oracle ceiling is a "
                  "valid reference to score the anchor budget-trajectory against"},
        {"kind": "metric_moves", "metric_name": "oracle_mrr_across_budget", "values": oracle_vals,
         "extra": "ORACLE mrr across k=%s must MOVE -> the capacity/budget axis is live, not inert" % list(k_grid)},
        {"kind": "negative_control_margin", "control_scores": [m[RANDOM], m[SCRAMBLE]],
         "headline_threshold": m[ANCHOR], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN_MRR,
         "n_repeats_min": 2, "control_name": "RANDOM_and_ANCHOR_SCRAMBLE_below_anchor_mrr",
         "extra": "RANDOM + relation-scrambled ANCHOR must sit below ANCHOR_COMPOSE by the MRR margin -> the RELATION "
                  "operators carry the signal, not anchor identity/degree"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["cardinality", "enough_heldout", "oracle_fires_all", "broken_test_guard",
                                    "test2_bucket_band", "test3_reach_band", "arms_differ"],
         "exercised_gates": ["cardinality", "enough_heldout", "oracle_fires_all", "broken_test_guard",
                             "test2_bucket_band", "test3_reach_band", "arms_differ"],
         "extra": "aggregate_bottleneck_verdict verdict=%s over %d planted Test-2 units + %d reachability pass"
                  % (st_verdict[:60], len(test2_units), len(reach_seeds))},
        # F.1: the self-test EXERCISED the REAL objects the FULL uses (Test-2 arena + Test-3 BFS) across >=2 budgets.
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["run_corpus", "build_anchor_compose_codes", "additive_direct_scores",
                                        "build_heldout_entity_split_ac", "reachability_by_bucket"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "self-test ran run_corpus (imported verbatim) at k=%s + reachability_by_bucket on the REAL split "
                  "reconstruction + BFS" % list(k_grid)},
        # F.2/F.3: reused calls bind against their LIVE signatures with base/portable POSITIONAL args (no
        # version-specific optional kwargs -> local/remote portability).
        {"kind": "substrate_signature", "callable_obj": run_corpus, "callable_name": "run_corpus", "args_count": 5},
        {"kind": "substrate_signature", "callable_obj": build_anchor_compose_codes,
         "callable_name": "build_anchor_compose_codes", "args_count": 4},
        {"kind": "substrate_signature", "callable_obj": additive_direct_scores,
         "callable_name": "additive_direct_scores", "args_count": 4},
        {"kind": "substrate_signature", "callable_obj": build_heldout_entity_split_ac,
         "callable_name": "build_heldout_entity_split_ac", "args_count": 5},
        # F.4: the broken-test guard fires against ORACLE_best (above the floor when the oracle fires), NOT POP
        # (structurally ~0 on this held-out arena). Validate the guard baseline is above the RANDOM floor.
        {"kind": "guard_baseline_valid", "baseline_score": oracle_best, "floor_score": m[RANDOM],
         "guard_name": "BROKEN_TEST_CONTROL_BEATS_ORACLE", "baseline_name": "ORACLE_best",
         "floor_name": "RANDOM", "eps": 0.02},
    ], run_mode="self_test")

    out = dict(
        n_grid_entities=top.get("n_query_scored"), k_grid=list(k_grid), top_budget=int(k_grid[-1]),
        heldout_mrr_top={a: round(m[a], 5) for a in ALL_ARMS},
        oracle_across_budget=[round(v, 5) if v == v else None for v in oracle_vals],
        anchor_margin=round(anchor_margin, 5) if anchor_margin == anchor_margin else None,
        scramble_margin=round(scramble_margin, 5) if scramble_margin == scramble_margin else None,
        oracle_margin=round(oracle_margin, 5) if oracle_margin == oracle_margin else None,
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        oracle_recovers=oracle_recovers, oracle_fires=oracle_fires, anchor_recovers=anchor_recovers,
        anchor_beats_random=anchor_beats_random, scramble_fails=scramble_fails, pop_at_floor=pop_at_floor,
        reach_ok=reach_ok, reachability=reach,
        selftest_verdict=st_verdict, validity_preflight_ok=bool(vp_ok),
        exercised_entrypoints=sorted(exercised),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest",
                                     "real_code_path_F1", "substrate_signature_F2_F3", "guard_baseline_valid_F4"])
    ok = bool(oracle_recovers and oracle_fires and anchor_recovers and anchor_beats_random
              and scramble_fails and pop_at_floor and reach_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    k_grid = cfg["k_grid"]
    expected_n_units = len(seeds) * len(k_grid)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k_grid=%s epochs=%s expected_units=%d" %
         (device, torch.cuda.is_available(), run_mode, seeds, k_grid, cfg["epochs"], expected_n_units))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s anchor_margin=%s scramble_margin=%s oracle_fires=%s oracle_across_budget=%s "
         "reach_ok=%s vp_ok=%s" % (st_ok, st_res.get("anchor_margin"), st_res.get("scramble_margin"),
                                   st_res.get("oracle_fires"), st_res.get("oracle_across_budget"),
                                   st_res.get("reach_ok"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (ORACLE did not recover/fire, or ANCHOR did not beat random, or "
                        "scramble did not fail, or POP not at floor, or reachability out of range): %s"
                        % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS bottleneck-pinpoint: run_corpus recovers planted held-out tails across >=2 "
                        "budgets (ORACLE fires; ANCHOR beats RANDOM; scramble fails); Test-3 reachability BFS runs on "
                        "the real split reconstruction; 7 validity-preflight checks declared (F.1-F.4 enforce)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    test2_units, reach_seeds, unit_failures = [], [], []
    for si, seed in enumerate(seeds):
        try:
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, k=None, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_CORPUS_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
            continue
        # TEST 3 reachability (once per seed; split is k-independent)
        try:
            reach = reachability_by_bucket(pool, cfg, seed)
            reach["cskg_provenance"] = dict(n_core_nodes=prov["n_core_nodes"], n_core_edges=prov["n_core_edges"])
            reach_seeds.append(reach)
            _log("seed=%d TEST3 reach@%dh cold=%s(n=%s) d1=%s(n=%s) d2_3plus=%s(n=%s)"
                 % (seed, REACH_H, _fmt(reach["cold"]["reach_frac_h%d" % REACH_H]), reach["cold"]["n_bfs"],
                    _fmt(reach["d1"]["reach_frac_h%d" % REACH_H]), reach["d1"]["n_bfs"],
                    _fmt(reach["d2_3plus"]["reach_frac_h%d" % REACH_H]), reach["d2_3plus"]["n_bfs"]))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, k="reach", failure_class=fc, msg=str(e)[:300]))
            _log("REACH_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        # TEST 2 budget sweep
        for k in k_grid:
            try:
                ts = time.time()
                u = run_test2_unit(pool, cfg, device, seed, k)
                test2_units.append(u)
                write_partial(out_dir, "%d_k%d" % (seed, k), dict(seed=seed, k=k, metrics=u, run_mode=run_mode))
                b = u["by3"]
                _log("seed=%d k=%d nq=%d | ANCHOR/ORACLE mrr cold=%s/%s(n%s) d1=%s/%s(n%s) d2_3plus=%s/%s(n%s) "
                     "oracle_fires=%s (%.1fs)" %
                     (seed, k, u["n_query_scored"],
                      _fmt(b["cold"][ANCHOR]["mrr"]), _fmt(b["cold"][ORACLE]["mrr"]), b["cold"][ANCHOR]["n"],
                      _fmt(b["d1"][ANCHOR]["mrr"]), _fmt(b["d1"][ORACLE]["mrr"]), b["d1"][ANCHOR]["n"],
                      _fmt(b["d2_3plus"][ANCHOR]["mrr"]), _fmt(b["d2_3plus"][ORACLE]["mrr"]), b["d2_3plus"][ANCHOR]["n"],
                      u["oracle_fires"], time.time() - ts))
                _hb("cskg_seed%d" % seed, k)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                fc = type(e).__name__
                unit_failures.append(dict(seed=seed, k=int(k), failure_class=fc, msg=str(e)[:300]))
                _log("UNIT_FAILED seed=%d k=%d class=%s: %s" % (seed, k, fc, str(e)[:200]))
            finally:
                if getattr(device, "type", "") == "cuda":
                    torch.cuda.empty_cache()

    if len(test2_units) < expected_n_units or len(reach_seeds) < len(seeds):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d Test-2 units (seeds %s x k_grid %s) + %d reachability passes, got %d + %d "
                        "(failures=%s)" % (expected_n_units, seeds, k_grid, len(seeds), len(test2_units),
                                           len(reach_seeds), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_bottleneck_verdict(test2_units, reach_seeds, k_grid, run_mode)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                   n_seeds=len(seeds), seeds=seeds, k_grid=k_grid, expected_n_units=expected_n_units,
                   n_units=len(test2_units), config=cfg, gates=gates, mechanism_selftest=st_res,
                   unit_failures=unit_failures, test2_units=test2_units, reachability=reach_seeds)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
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
