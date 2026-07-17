"""exp_importance_retrieval_relevance_query_centrality_real_codex_v1

RE-TARGET of the HARD_FAIL importance/downstream-reach cell from ACQUISITION-ORDER to
RETRIEVAL-RELEVANCE. The prior cell
(exp_importance_downstream_reach_ingest_prioritization_real_codex_v1, HARD_FAIL) asked whether
downstream-reach should ORDER acquisition of new facts -- it lost to random + frequency order (the
BatchBALD/coreset redundancy anti-pattern). Separability still held on that cell
(importance_btwn_unique_variance=0.867, max_pop_corr=0.220, SEPARABLE) -- importance is a real,
popularity-decorrelated signal. The drill
(notes/research_importance_correct_function_retrieval_vs_active_learning_2026-07-16.md) identified the
UNTESTED correct function: RETRIEVAL / ATTENTION-TIME RELEVANCE (Mattar&Daw Gain x Need; priority maps;
classical-IR PageRank/HITS = retrieval-relevance-by-construction, NOT crawl-order). Near-zero new
compute: re-target the SAME already-fitted importance machinery (train-graph node value-of-information)
against a NEW, already-on-disk ground truth.

THE QUESTION (reported in THREE SEPARATE PARTS -- do not blob):
  Does a train-graph entity's IMPORTANCE (downstream-reach; degree-orthogonalized node value-of-info)
  predict how often it is NEEDED to answer HELD-OUT TEST QUERIES (retrieval-relevance / query-centrality
  = count of appearances as head or tail across the held-out test positives), POPULARITY-NEUTRAL
  (must beat a degree-matched control; must add BEYOND raw degree/frequency, not merely correlate with
  degree)?
    PART A  RETRIEVAL-PREDICTION: partial (rank) correlation of importance vs test_query_count,
            controlling for [log_degree, log_incidence]; + incremental rank-R^2.
    PART B  POPULARITY-NEUTRALITY (tertile-at-matched-degree): within each degree bin, do the
            top-importance-tertile entities appear in test at a higher RATE than bottom-importance-
            tertile (degree matched -> pure importance content)? + degree-matched-scramble null control
            (must collapse to ~0; validates the degree binning is not leaking).
    PART C  SEPARABILITY (re-report at node level): node importance vs degree/incidence correlation.

OPERATIONALIZATION (train-graph-only importance; held-out-test-only target; label-free):
  IMPORTANCE (per ENTITY, degree-decorrelated value-of-information):
    PRIMARY   imp_btwn_orth = degree-orthogonalized sampled VERTEX BETWEENNESS centrality on the
              undirected train graph. Vertex betweenness = "how many shortest reasoning-paths between
              OTHER entity pairs route THROUGH this entity" = value-of-information / downstream-reach,
              the per-node analog of the prior cell's degree-decorrelated edge-betweenness. Orthogonalize
              on log-degree (remove popularity) -> the neutral headline signal.
    DIAG      imp_reach_orth = degree-orthogonalized k-hop reachable-mass (arena-faithful, hub-aligned;
              correlates with degree -> reported as diagnostic, NOT the neutral headline).
  TARGET (per ENTITY, held-out): test_query_count (tqc) = number of appearances as head or tail across
    the n_test_pos held-out TEST POSITIVES (test.txt). A groupby-count on data already on disk; zero new
    labeling. test-appearance = (tqc > 0). Secondary robustness variant: test+valid positives combined.
  POPULARITY CONTROLS: log1p(train unique-neighbor degree), log1p(train incidence = # train triples the
    entity touches). Importance must predict tqc BEYOND these -- the schema-fit-win fairness discipline.

INFO-CEILING GATE (FIRST, MANDATORY): the retrieval-relevance TARGET must be NON-vacuous before any arm
  is interpreted -- (a) test-appearance rate strictly inside (CEIL_APPEAR_LO, CEIL_APPEAR_HI) (there is
  spread to predict), (b) tqc has non-zero variance, (c) raw degree RESOLVES the target above chance:
  spearman(log_degree, tqc) >= CEIL_DEG_PREDICTS_MIN (popularity DOES predict retrieval -- the expected,
  non-surprising part per KGQA popularity bias; if degree cannot predict tqc at all the target is noise).
  If any fails -> VACUOUS. Then the DECISIVE question is whether importance adds BEYOND degree.

PRE-REG BANDS (fixed a-priori; see preregs/2026-07-16_importance_retrieval_relevance_query_centrality.md):
  info-ceiling PASS is a precondition for ALL of the below. pc = partial rank-corr(importance, tqc |
  [log_deg, log_inc]); tert = degree-matched top-vs-bottom-importance-tertile test-appearance-rate gap.
  HARD_PASS : info-ceiling PASS AND pc >= PC_HP AND tert >= TERT_HP AND pc_boot_p05 > 0 AND
              tert_boot_p05 > 0 AND the degree-matched-scramble control is near-zero (pc_scramble <
              NEUTRAL_CTRL_MAX AND tert_scramble < NEUTRAL_CTRL_MAX) -> importance's CORRECT function
              found = a retrieval/attention-relevance signal, popularity-neutral, actionable as a
              query-time beam-allocation / ranking weight.
  HARD_FAIL : info-ceiling PASS AND NOT hard_pass AND (pc < PC_HF OR tert < TERT_HF) -> importance
              predicts retrieval no better than popularity (residualized corr null OR degree-matched
              arms show no separation) = importance predicts NEITHER acquisition-order NOR retrieval-
              relevance = genuinely low-value for our unbounded-store substrate. HONEST + IMPORTANT
              (follow-the-evidence): the SEPARABILITY finding still stands as a real measured quantity;
              what closes is "importance has predictive value for retrieval-priority beyond popularity".
              Do NOT manufacture a role.
  MIDDLE    : info-ceiling PASS AND real-but-modest (pc / tert between the FAIL and PASS floors) -> route
              to the heavier bounded-width retrieval-ranking-accuracy v2 (research note MIDDLE routing).
  BLOCK_BROKEN_DEGREE_CONTROL : the degree-matched-scramble null is NOT near-zero (degree binning leaks;
              the tertile comparison is confounded) -> cannot trust PART B; do not emit HARD_PASS.
  VACUOUS_METRIC : info-ceiling FAIL (target cannot be interpreted).

PRE-REG DEVIATION FLAG (per hand-off contract): the research note labels the HARD-PASS 0.15 bar
  "partial R^2" but the MIDDLE band it gives is "partial correlation 0.05-0.15" and the HARD-FAIL bar is
  "residualized correlation < 0.05" -- these are only mutually consistent if the decision scalar is the
  PARTIAL (residualized) CORRELATION on a 0.05 / 0.15 scale (a partial-R^2 of 0.15 would be corr ~0.39,
  inconsistent with the same-note MIDDLE upper edge of 0.15). This cell adopts the consistent reading:
  primary scalar = PARTIAL RANK-CORRELATION with bands PC_HF=0.05, PC_HP=0.15; incremental rank-R^2 is
  ALSO reported as a companion (not the gate). This is a faithful reconciliation, not a loosening.

Determinism: numpy default_rng(fixed int seeds); NO hash()-derived seeds; sorted() for set ops.
ASCII-only. No emojis. Local CPU single-shot run-to-completion (NOT a queue dispatch), so runner
start_marker/heartbeat/run_mode gates do not apply; atomic tmp+os.replace metrics write, no bare except,
SystemExit-first ordering, arms-differ check present. No queue/GPU/atoms/push.

CELL-TEMPLATE compliance (single-shot local, no queue):
- arms_differ_verified: primary imp vs scramble vs random importance vectors hashed distinct (META_RULE_AF).
- final_metrics_atomicity: tmp_replace (os.replace) (META_RULE_AH).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: signal is a rank partial-correlation over a parameter-free structural score; no noise-floor.
- baseline_in_band (META_RULE_AG analog): info-ceiling verifies degree-baseline resolves target in
  (chance, near-saturation) band and test-appearance rate is in-band -> the discriminator can fire.
- discriminator-fires: the degree-matched-scramble null control MUST return ~0 (BLOCK if it leaks) AND
  the tertile bins must be populated (>= MIN_BIN_ENTITIES) -> the popularity-neutral test actually fires.
- calibration_check: default_ok_for_this_regime -- thresholds are pre-registered from the research note,
  the target is a raw count on the real held-out split (no primitive-default inheritance).
- all reported numbers MEASURED@ this cell's metrics.json (no hypothesized numbers in verdict).
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "importance_retrieval_relevance_query_centrality_real_codex_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the prior cell's already-built, already-validated primitives (DRY; no re-derivation).
from experiments.exp_importance_downstream_reach_ingest_prioritization_real_codex_v1 import (  # noqa: E402
    read_triples, spearman, rankdata_avg, build_adj_list,
)

# ---- fixed config (a-priori) ----
KREACH_HOPS = 3
KREACH_CAP = 4000
N_BTWN_SOURCES_FULL = 192      # sampled Brandes sources (matches prior cell's full config)
N_BTWN_SOURCES_SMOKE = 48
BTWN_SEED = 2027
N_DEG_BINS = 4
MIN_BIN_ENTITIES = 6           # a degree bin must have >= this many entities to contribute a tertile gap
N_BOOT = 400
BOOT_LO_PCT = 5.0
BOOT_SEED = 909
SCRAMBLE_SEEDS = [7, 17, 29]   # degree-matched-scramble null control seeds
RANDOM_SEEDS = [11, 23, 37]    # full-shuffle null control seeds

# ---- pre-reg thresholds (FIXED a-priori; from the research note section (c)) ----
CEIL_APPEAR_LO = 0.05          # test-appearance rate must be strictly inside (LO, HI): spread exists
CEIL_APPEAR_HI = 0.98
CEIL_DEG_PREDICTS_MIN = 0.10   # spearman(log_deg, tqc) floor -> degree resolves the target (non-vacuous)

PC_HP = 0.15                   # partial rank-corr(importance, tqc | [log_deg, log_inc]) HARD_PASS floor
PC_HF = 0.05                   # below -> retrieval-relevance is popularity in disguise (HARD_FAIL side)
TERT_HP = 0.15                 # degree-matched tertile appearance-rate gap HARD_PASS floor (15 pp)
TERT_HF = 0.05                 # below -> degree-matched arms show no separation (HARD_FAIL side)
NEUTRAL_CTRL_MAX = 0.05        # degree-matched-scramble null must stay below this (else control leaks)


# =============================== data ==========================================
def load_entities_and_targets(dataset):
    """Mirror the prior cell's eidx construction EXACTLY (sorted union of all entities across
    train+valid+test pos+neg) so the train-graph importance/degree and the held-out target share one
    consistent entity index. Returns per-entity train degree/incidence + held-out test_query_count."""
    raw = os.path.join(REPO, "data", dataset, "raw")
    train = read_triples(raw, "train.txt")
    val_p = read_triples(raw, "valid.txt")
    val_n = read_triples(raw, "valid_negatives.txt")
    tst_p = read_triples(raw, "test.txt")
    tst_n = read_triples(raw, "test_negatives.txt")
    ents = set()
    for h, r, t in train + val_p + val_n + tst_p + tst_n:
        ents.add(h); ents.add(t)
    eidx = {e: i for i, e in enumerate(sorted(ents))}
    n_ent = len(eidx)
    train_int = np.array([[eidx[h], 0, eidx[t]] for h, r, t in train], dtype=np.int64)
    # leak guard: no held-out test positive may already be a train triple
    train_set = set(train)
    leak = sum(1 for tp in tst_p if tp in train_set)
    assert leak == 0, "LEAK: %d test positives present in train graph" % leak
    # train unique-neighbor degree + incidence (# train triples touching the entity, with multiplicity)
    seen = [set() for _ in range(n_ent)]
    inc = np.zeros(n_ent, dtype=np.int64)
    for h, r, t in train:
        a = eidx[h]; b = eidx[t]
        inc[a] += 1; inc[b] += 1
        if a != b:
            seen[a].add(b); seen[b].add(a)
    deg = np.array([len(s) for s in seen], dtype=np.int64)
    # held-out target: test_query_count (test positives only) + test+valid robustness variant
    tqc = np.zeros(n_ent, dtype=np.int64)
    for h, r, t in tst_p:
        tqc[eidx[h]] += 1; tqc[eidx[t]] += 1
    tqc_tv = tqc.copy()
    for h, r, t in val_p:
        tqc_tv[eidx[h]] += 1; tqc_tv[eidx[t]] += 1
    return {"n_ent": n_ent, "train_int": train_int, "deg": deg, "inc": inc,
            "tqc": tqc, "tqc_tv": tqc_tv, "n_test_pos": len(tst_p), "n_valid_pos": len(val_p)}


# =============================== importance signals ============================
def sampled_node_betweenness(adj, n_ent, n_sources, seed):
    """Brandes VERTEX betweenness with sampled BFS sources (undirected, unweighted). Returns bc[node].
    Per-node analog of the prior cell's sampled_edge_betweenness (same BFS/accumulation structure)."""
    rng = np.random.default_rng(seed)
    noniso = [v for v in range(n_ent) if adj[v]]
    if n_sources >= len(noniso):
        sources = sorted(noniso)
    else:
        sources = sorted(rng.choice(np.array(noniso), size=n_sources, replace=False).tolist())
    bc = np.zeros(n_ent, dtype=np.float64)
    for s in sources:
        S = []
        P = [[] for _ in range(n_ent)]
        sigma = np.zeros(n_ent, dtype=np.float64); sigma[s] = 1.0
        dist = np.full(n_ent, -1, dtype=np.int64); dist[s] = 0
        Q = deque([s])
        while Q:
            v = Q.popleft(); S.append(v)
            dv = dist[v]; sv = sigma[v]
            for w in adj[v]:
                if dist[w] < 0:
                    dist[w] = dv + 1; Q.append(w)
                if dist[w] == dv + 1:
                    sigma[w] += sv; P[w].append(v)
        delta = np.zeros(n_ent, dtype=np.float64)
        while S:
            w = S.pop()
            sw = sigma[w]; dw = delta[w]
            for v in P[w]:
                delta[v] += (sigma[v] / sw) * (1.0 + dw)
            if w != s:
                bc[w] += delta[w]
    scale = float(len(noniso)) / max(len(sources), 1)   # extrapolate sampled sum to full-source scale
    return bc * scale, len(sources)


def ols_resid(y, cols):
    """Residual of y after OLS on [1] + cols (each an array). Degree-orthogonalization primitive."""
    n = len(y)
    X = np.column_stack([np.ones(n)] + [np.asarray(c, dtype=np.float64) for c in cols])
    coef, _, _, _ = np.linalg.lstsq(X, np.asarray(y, dtype=np.float64), rcond=None)
    return np.asarray(y, dtype=np.float64) - X @ coef


# =============================== analysis primitives ==========================
def spearman_corr_matrix(cols):
    """Symmetric Spearman rank-correlation matrix over a list of arrays."""
    k = len(cols)
    rk = [rankdata_avg(c) for c in cols]
    rk = [r - r.mean() for r in rk]
    R = np.eye(k, dtype=np.float64)
    for i in range(k):
        for j in range(i + 1, k):
            d = math.sqrt(float((rk[i] * rk[i]).sum()) * float((rk[j] * rk[j]).sum()))
            c = float((rk[i] * rk[j]).sum() / d) if d > 0 else 0.0
            R[i, j] = R[j, i] = c
    return R


def partial_spearman(predictor, target, controls):
    """Partial (rank) correlation of predictor vs target, controlling for a list of control arrays.
    Uses the precision-matrix formula on the Spearman correlation matrix; pinv for numerical safety."""
    cols = [predictor, target] + list(controls)
    R = spearman_corr_matrix(cols)
    P = np.linalg.pinv(R)
    denom = math.sqrt(P[0, 0] * P[1, 1])
    return float(-P[0, 1] / denom) if denom > 0 else 0.0


def _ols_r2(y, X):
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = float(((y - yhat) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0


def incremental_rank_r2(predictor, target, controls):
    """Incremental rank-R^2 that `predictor` adds to explaining `target` beyond `controls`
    (all rank-transformed). Companion to the partial correlation (not the decision gate)."""
    ry = rankdata_avg(target)
    rc = [rankdata_avg(c) for c in controls]
    rp = rankdata_avg(predictor)
    n = len(target)
    X_red = np.column_stack([np.ones(n)] + rc)
    X_full = np.column_stack([np.ones(n)] + rc + [rp])
    return max(0.0, _ols_r2(ry, X_full) - _ols_r2(ry, X_red))


def entity_degree_bins(deg, n_bins=N_DEG_BINS):
    """Per-entity degree bin from quantiles of log1p(degree) over the connected entities.
    Isolated (deg==0) entities fall in the lowest bin."""
    ld = np.log1p(deg.astype(np.float64))
    pos = ld[deg > 0]
    if len(pos):
        qthr = np.quantile(pos, np.linspace(0, 1, n_bins + 1)[1:-1])
    else:
        qthr = np.zeros(n_bins - 1)
    return np.searchsorted(qthr, ld).astype(np.int64)


def tertile_matched_gap(imp, tqc, dbin):
    """Within each degree bin, appearance-rate(top importance tertile) - appearance-rate(bottom
    importance tertile); size-weighted mean across bins. Isolates importance CONTENT at matched degree."""
    appear = (np.asarray(tqc) > 0).astype(np.float64)
    num = 0.0; den = 0.0; per_bin = {}
    for b in sorted(set(int(x) for x in dbin.tolist())):
        idx = np.where(dbin == b)[0]
        if len(idx) < MIN_BIN_ENTITIES:
            continue
        order = idx[np.argsort(imp[idx], kind="mergesort")]
        tert = len(order) // 3
        if tert < 1:
            continue
        bottom = order[:tert]; top = order[-tert:]
        top_rate = float(appear[top].mean()); bot_rate = float(appear[bottom].mean())
        gap = top_rate - bot_rate
        w = len(top) + len(bottom)
        num += gap * w; den += w
        per_bin[int(b)] = {"gap": gap, "n_top": int(len(top)), "n_bottom": int(len(bottom)),
                           "top_rate": top_rate, "bottom_rate": bot_rate}
    return (num / den if den > 0 else 0.0), per_bin, int(len(per_bin))


def scramble_within_bins(imp, dbin, seed):
    """Permute importance values WITHIN each degree bin (preserves the degree-conditional importance
    distribution, destroys the entity-level importance<->target pairing). The strict popularity-neutral
    null: partial corr / tertile gap must collapse to ~0."""
    rng = np.random.default_rng(seed)
    out = imp.copy()
    buckets = defaultdict(list)
    for i in range(len(dbin)):
        buckets[int(dbin[i])].append(i)
    for b in sorted(buckets):
        idxs = buckets[b]
        vals = imp[idxs].copy()
        perm = rng.permutation(len(idxs))
        for k in range(len(idxs)):
            out[idxs[k]] = vals[perm[k]]
    return out


def _digest(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


# =============================== main run =====================================
def run(d, scale):
    t0 = time.time()
    n_ent = d["n_ent"]; train_int = d["train_int"]
    deg = d["deg"]; inc = d["inc"]; tqc = d["tqc"]
    n_btwn = N_BTWN_SOURCES_SMOKE if scale == "smoke" else N_BTWN_SOURCES_FULL

    log_deg = np.log1p(deg.astype(np.float64))
    log_inc = np.log1p(inc.astype(np.float64))
    controls = [log_deg, log_inc]

    # ---- importance signals (train-graph-only, label-free) ----
    adj, _edge_id = build_adj_list(train_int, n_ent)
    print("[imp] sampled vertex betweenness: n_sources=%d n_ent=%d ..." % (n_btwn, n_ent), flush=True)
    tb = time.time()
    bc, used_sources = sampled_node_betweenness(adj, n_ent, n_btwn, BTWN_SEED)
    print("[imp] node betweenness done in %.1fs (sources=%d)" % (time.time() - tb, used_sources), flush=True)
    imp_btwn_orth = ols_resid(bc, [log_deg])   # PRIMARY: degree-decorrelated value-of-information

    # DIAGNOSTIC hub-aligned reach (arena-faithful k-hop reachable mass), degree-orthogonalized
    from hdlab import reachability_audit as ra
    adj_arr = ra.build_undirected_adj(train_int, n_ent)
    kreach = ra.k_hop_reachable_mass(adj_arr, KREACH_HOPS, cap=KREACH_CAP)
    imp_reach_orth = ols_resid(np.asarray(kreach, dtype=np.float64), [log_deg])

    dbin = entity_degree_bins(deg)

    # ---- info-ceiling gate (FIRST) ----
    appear_rate = float((tqc > 0).mean())
    deg_predicts = spearman(log_deg, tqc.astype(np.float64))
    tqc_std = float(tqc.astype(np.float64).std())
    info_ceiling_pass = (CEIL_APPEAR_LO < appear_rate < CEIL_APPEAR_HI
                         and deg_predicts >= CEIL_DEG_PREDICTS_MIN and tqc_std > 0.0)

    # ---- PART A: retrieval-prediction (partial corr + incremental rank-R^2) ----
    pc_btwn = partial_spearman(imp_btwn_orth, tqc.astype(np.float64), controls)
    incr2_btwn = incremental_rank_r2(imp_btwn_orth, tqc.astype(np.float64), controls)
    pc_reach = partial_spearman(imp_reach_orth, tqc.astype(np.float64), controls)
    incr2_reach = incremental_rank_r2(imp_reach_orth, tqc.astype(np.float64), controls)

    # ---- PART B: degree-matched tertile gap + scramble/random nulls ----
    tert_btwn, tert_per_bin, n_bins_fired = tertile_matched_gap(imp_btwn_orth, tqc, dbin)
    tert_reach, _tr_bin, _ = tertile_matched_gap(imp_reach_orth, tqc, dbin)

    scr_imps = [scramble_within_bins(imp_btwn_orth, dbin, s) for s in SCRAMBLE_SEEDS]
    pc_scramble = float(np.mean([abs(partial_spearman(si, tqc.astype(np.float64), controls)) for si in scr_imps]))
    tert_scramble = float(np.mean([abs(tertile_matched_gap(si, tqc, dbin)[0]) for si in scr_imps]))

    rnd_imps = [np.random.default_rng(s).permutation(imp_btwn_orth) for s in RANDOM_SEEDS]
    pc_random = float(np.mean([abs(partial_spearman(ri, tqc.astype(np.float64), controls)) for ri in rnd_imps]))
    tert_random = float(np.mean([abs(tertile_matched_gap(ri, tqc, dbin)[0]) for ri in rnd_imps]))

    # ---- bootstrap over entities (p05 of pc_btwn and tert_btwn) ----
    rng = np.random.default_rng(BOOT_SEED)
    boot_pc = []; boot_tert = []
    tqc_f = tqc.astype(np.float64)
    for _b in range(N_BOOT):
        idx = rng.integers(0, n_ent, size=n_ent)
        bpc = partial_spearman(imp_btwn_orth[idx], tqc_f[idx], [log_deg[idx], log_inc[idx]])
        bt, _pb, _nb = tertile_matched_gap(imp_btwn_orth[idx], tqc[idx], dbin[idx])
        boot_pc.append(bpc); boot_tert.append(bt)
    pc_p05 = float(np.percentile(boot_pc, BOOT_LO_PCT))
    tert_p05 = float(np.percentile(boot_tert, BOOT_LO_PCT))

    # ---- PART C: separability (node level, re-report) ----
    corr_imp_deg = spearman(imp_btwn_orth, log_deg)   # ~0 by construction (orthogonalized)
    corr_bc_deg = spearman(bc, log_deg)               # raw betweenness vs degree (pre-orthogonalization)
    corr_bc_inc = spearman(bc, log_inc)
    max_pop_corr_raw = max(abs(corr_bc_deg), abs(corr_bc_inc))

    # ---- test+valid robustness variant (secondary) ----
    tqc_tv = d["tqc_tv"]
    pc_btwn_tv = partial_spearman(imp_btwn_orth, tqc_tv.astype(np.float64), controls)
    tert_btwn_tv, _tvb, _tvn = tertile_matched_gap(imp_btwn_orth, tqc_tv, dbin)

    # ---- arms-differ (META_RULE_AF) ----
    digests = {"imp_btwn_orth": _digest(imp_btwn_orth), "scramble0": _digest(scr_imps[0]),
               "random0": _digest(rnd_imps[0]), "imp_reach_orth": _digest(imp_reach_orth)}
    arms_differ = len(set(digests.values())) == len(digests)

    # ---- verdict ----
    control_near_zero = (pc_scramble < NEUTRAL_CTRL_MAX and tert_scramble < NEUTRAL_CTRL_MAX)
    hard_pass = (info_ceiling_pass and pc_btwn >= PC_HP and tert_btwn >= TERT_HP
                 and pc_p05 > 0.0 and tert_p05 > 0.0 and control_near_zero)
    if not info_ceiling_pass:
        verdict = "VACUOUS_METRIC_INFO_CEILING_FAIL"
    elif not arms_differ:
        verdict = "BLOCK_ARMS_IDENTICAL"
    elif not control_near_zero:
        verdict = "BLOCK_BROKEN_DEGREE_CONTROL"
    elif hard_pass:
        verdict = "HARD_PASS_IMPORTANCE_PREDICTS_RETRIEVAL_RELEVANCE"
    elif pc_btwn < PC_HF or tert_btwn < TERT_HF:
        verdict = "HARD_FAIL_IMPORTANCE_LOW_VALUE_NO_RETRIEVAL_RELEVANCE_BEYOND_POPULARITY"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    out = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "run_mode": scale,
        "scale": scale,
        "dataset": "codex_claimvalidity",
        "elapsed_s": elapsed,
        "n_ent": n_ent, "n_train": int(train_int.shape[0]),
        "n_test_pos": d["n_test_pos"], "n_valid_pos": d["n_valid_pos"],
        "info_ceiling": {
            "test_appearance_rate": appear_rate,
            "deg_predicts_tqc_spearman": deg_predicts,
            "tqc_std": tqc_std,
            "thresholds": {"CEIL_APPEAR_LO": CEIL_APPEAR_LO, "CEIL_APPEAR_HI": CEIL_APPEAR_HI,
                           "CEIL_DEG_PREDICTS_MIN": CEIL_DEG_PREDICTS_MIN},
            "info_ceiling_pass": bool(info_ceiling_pass),
        },
        "partA_retrieval_prediction": {
            "primary_metric": "partial_rank_corr(imp_btwn_orth, tqc | [log_deg, log_inc])",
            "pc_btwn": pc_btwn, "incr_rank_r2_btwn": incr2_btwn,
            "pc_btwn_boot_p05": pc_p05,
            "pc_reach_diag": pc_reach, "incr_rank_r2_reach_diag": incr2_reach,
            "pc_btwn_test_plus_valid": pc_btwn_tv,
            "bands": {"PC_HF": PC_HF, "PC_HP": PC_HP},
        },
        "partB_popularity_neutrality": {
            "tert_btwn": tert_btwn, "tert_btwn_boot_p05": tert_p05,
            "n_degree_bins_fired": n_bins_fired, "n_degree_bins": N_DEG_BINS,
            "tert_per_bin": tert_per_bin,
            "tert_reach_diag": tert_reach,
            "tert_btwn_test_plus_valid": tert_btwn_tv,
            "control_pc_scramble": pc_scramble, "control_tert_scramble": tert_scramble,
            "control_pc_random": pc_random, "control_tert_random": tert_random,
            "control_near_zero": bool(control_near_zero),
            "bands": {"TERT_HF": TERT_HF, "TERT_HP": TERT_HP, "NEUTRAL_CTRL_MAX": NEUTRAL_CTRL_MAX},
        },
        "partC_separability_node_level": {
            "corr_imp_orth_deg": corr_imp_deg,
            "corr_raw_btwn_deg": corr_bc_deg, "corr_raw_btwn_inc": corr_bc_inc,
            "max_pop_corr_raw_btwn": max_pop_corr_raw,
            "note": "prior cell edge-level: importance_btwn_unique_variance=0.867 SEPARABLE (real signal)",
        },
        "config": {
            "n_btwn_sources": used_sources, "kreach_hops": KREACH_HOPS, "n_deg_bins": N_DEG_BINS,
            "n_boot": N_BOOT, "scramble_seeds": SCRAMBLE_SEEDS, "random_seeds": RANDOM_SEEDS,
            "bands": {"PC_HP": PC_HP, "PC_HF": PC_HF, "TERT_HP": TERT_HP, "TERT_HF": TERT_HF,
                      "NEUTRAL_CTRL_MAX": NEUTRAL_CTRL_MAX, "CEIL_DEG_PREDICTS_MIN": CEIL_DEG_PREDICTS_MIN},
        },
        "arm_digests": digests,
        "arms_differ": bool(arms_differ),
        "verdict_msg": (
            "%s | A[retrieval] pc_btwn=%.4f (p05=%+.4f incrR2=%.4f) pc_reach_diag=%.4f | "
            "B[neutral] tert_btwn=%.4f (p05=%+.4f, %d/%d bins) scramble(pc=%.4f tert=%.4f) "
            "random(pc=%.4f tert=%.4f) ctrl_near0=%s | C[sep] raw_btwn~deg=%.3f orth~deg=%.3f | "
            "info_ceiling(appear=%.3f deg_predicts=%.3f pass=%s)" % (
                verdict, pc_btwn, pc_p05, incr2_btwn, pc_reach, tert_btwn, tert_p05,
                n_bins_fired, N_DEG_BINS, pc_scramble, tert_scramble, pc_random, tert_random,
                control_near_zero, corr_bc_deg, corr_imp_deg, appear_rate, deg_predicts,
                info_ceiling_pass)),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out["summary"] = verdict
    return out


def write_metrics(out):
    out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    clean = {k: v for k, v in out.items() if not k.startswith("_")}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)
    os.replace(tmp, final)
    return final


# =============================== self-test ====================================
def self_test():
    # (A) node betweenness fires on a planted bridge, degree-DECORRELATED.
    #     Two triangles {0,1,2} and {3,4,5} joined by a single bridge edge (2,3). The two bridge
    #     endpoints (2,3) must have HIGHER vertex betweenness than their triangle peers, despite EQUAL
    #     degree (3) -> betweenness is not degree.
    tri = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (2, 3)]
    n = 6
    train = np.array([[a, 0, b] for a, b in tri], dtype=np.int64)
    adj, _eid = build_adj_list(train, n)
    bc, _u = sampled_node_betweenness(adj, n, n, 1)
    assert bc[2] > bc[0] + 1e-9 and bc[2] > bc[1] + 1e-9, \
        "node betweenness: bridge endpoint 2 must dominate its triangle peers (bc2=%.3f bc0=%.3f)" % (bc[2], bc[0])
    assert bc[3] > bc[4] + 1e-9 and bc[3] > bc[5] + 1e-9, \
        "node betweenness: bridge endpoint 3 must dominate its triangle peers (bc3=%.3f bc4=%.3f)" % (bc[3], bc[4])

    # (B) partial correlation recovers signal-beyond-a-control and returns ~0 for a pure function of it.
    rng = np.random.default_rng(0)
    m = 800
    ctrl = rng.normal(size=m)
    extra = rng.normal(size=m)
    pred = ctrl + 0.9 * extra                        # has variance beyond ctrl
    tgt = 0.8 * extra + 0.2 * rng.normal(size=m)     # driven by extra, NOT by ctrl
    pc = partial_spearman(pred, tgt, [ctrl])
    assert pc > 0.20, "partial corr must recover signal beyond control, got %.3f" % pc
    pred_pure = 3.0 * ctrl                            # pure function of the control -> no unique info
    pc0 = partial_spearman(pred_pure, tgt, [ctrl])
    assert abs(pc0) < 0.10, "partial corr of a pure-control predictor must be ~0, got %.3f" % pc0

    # (C) incremental rank-R^2: a control-only predictor adds ~0; an independent predictor adds > 0.
    inc0 = incremental_rank_r2(pred_pure, tgt, [ctrl])
    inc1 = incremental_rank_r2(pred, tgt, [ctrl])
    assert inc0 < 0.02, "incr R^2 of a pure-control predictor must be ~0, got %.3f" % inc0
    assert inc1 > inc0, "incr R^2 of an informative predictor must exceed the pure-control one"

    # (D) tertile-matched gap fires with planted within-bin signal and the scramble null collapses to ~0.
    n_e = 600
    deg_e = rng.integers(1, 50, size=n_e)
    dbin = entity_degree_bins(deg_e)
    imp_e = rng.normal(size=n_e)
    # plant: entities with high importance appear in test (tqc>0) more often, WITHIN every degree bin
    p_appear = 1.0 / (1.0 + np.exp(-1.5 * imp_e))
    tqc_e = (rng.random(n_e) < p_appear).astype(np.int64)
    gap, per_bin, nb = tertile_matched_gap(imp_e, tqc_e, dbin)
    assert nb >= 1 and gap > 0.10, "tertile gap must fire on planted within-bin signal (gap=%.3f bins=%d)" % (gap, nb)
    scr = scramble_within_bins(imp_e, dbin, 7)
    gap_scr, _pb, _nb = tertile_matched_gap(scr, tqc_e, dbin)
    assert abs(gap_scr) < gap, "degree-matched scramble null must collapse below the true gap"

    # (E) partial correlation is invariant-ish to a monotone transform of the control (rank-based).
    pc_log = partial_spearman(pred, tgt, [np.exp(ctrl)])
    assert abs(pc_log - pc) < 0.05, "rank partial-corr must be stable under a monotone control transform"

    # (F) REAL code path + REAL info-ceiling on CoDEx at FULL entity index (fast). Exercises the ACTUAL
    #     loader + the ACTUAL node-betweenness path the FULL run uses (tiny source sample for speed) and
    #     asserts the retrieval-relevance TARGET is NON-vacuous (the mandatory info-ceiling precondition).
    d = load_entities_and_targets("codex_claimvalidity")
    assert d["n_ent"] == 2034, "expected CoDEx n_ent=2034, got %d" % d["n_ent"]
    tqc = d["tqc"]
    appear = float((tqc > 0).mean())
    dp = spearman(np.log1p(d["deg"].astype(np.float64)), tqc.astype(np.float64))
    assert CEIL_APPEAR_LO < appear < CEIL_APPEAR_HI, \
        "info-ceiling: test-appearance rate %.3f must be inside band (spread exists)" % appear
    assert dp >= CEIL_DEG_PREDICTS_MIN, \
        "info-ceiling: degree must resolve tqc above chance (spearman=%.3f >= %.2f)" % (dp, CEIL_DEG_PREDICTS_MIN)
    adj_r, _e = build_adj_list(d["train_int"], d["n_ent"])
    bc_r, used = sampled_node_betweenness(adj_r, d["n_ent"], 8, BTWN_SEED)   # tiny sample: real path only
    assert used == 8 and bc_r.sum() > 0.0, "real node-betweenness path must run and produce nonzero mass"
    print("[SELF-TEST] PASS  bridge_ok | partial_corr_ok | incr_r2_ok | tertile+scramble_ok | "
          "REAL info-ceiling(appear=%.3f deg_predicts=%.3f) real_btwn_ok(sources=%d)" % (appear, dp, used))
    return True


# =============================== entry ========================================
def main(scale="full"):
    d = load_entities_and_targets("codex_claimvalidity")
    print("[load] scale=%s n_ent=%d n_train=%d n_test_pos=%d n_valid_pos=%d" % (
        scale, d["n_ent"], d["train_int"].shape[0], d["n_test_pos"], d["n_valid_pos"]), flush=True)
    out = run(d, scale)
    final = write_metrics(out)
    print("[VERDICT] %s" % out["verdict"])
    ic = out["info_ceiling"]
    print("  INFO-CEILING: appear_rate=%.3f deg_predicts_tqc=%.3f tqc_std=%.2f -> pass=%s" % (
        ic["test_appearance_rate"], ic["deg_predicts_tqc_spearman"], ic["tqc_std"], ic["info_ceiling_pass"]))
    a = out["partA_retrieval_prediction"]
    print("  PART A RETRIEVAL: pc_btwn=%.4f (p05=%+.4f incrR2=%.4f) | pc_reach_diag=%.4f | pc(test+valid)=%.4f" % (
        a["pc_btwn"], a["pc_btwn_boot_p05"], a["incr_rank_r2_btwn"], a["pc_reach_diag"], a["pc_btwn_test_plus_valid"]))
    b = out["partB_popularity_neutrality"]
    print("  PART B NEUTRALITY: tert_btwn=%.4f (p05=%+.4f, %d/%d bins) | scramble(pc=%.4f tert=%.4f) "
          "random(pc=%.4f tert=%.4f) ctrl_near0=%s" % (
              b["tert_btwn"], b["tert_btwn_boot_p05"], b["n_degree_bins_fired"], b["n_degree_bins"],
              b["control_pc_scramble"], b["control_tert_scramble"], b["control_pc_random"],
              b["control_tert_random"], b["control_near_zero"]))
    c = out["partC_separability_node_level"]
    print("  PART C SEPARABILITY: raw_btwn~deg=%.3f raw_btwn~inc=%.3f orth~deg=%.3f (max_pop_corr_raw=%.3f)" % (
        c["corr_raw_btwn_deg"], c["corr_raw_btwn_inc"], c["corr_imp_orth_deg"], c["max_pop_corr_raw_btwn"]))
    print("  elapsed=%.1fs metrics -> %s" % (out["elapsed_s"], final))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(scale="smoke" if args.smoke else "full")
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
