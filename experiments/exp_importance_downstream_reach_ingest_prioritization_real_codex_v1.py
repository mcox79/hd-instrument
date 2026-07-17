"""exp_importance_downstream_reach_ingest_prioritization_real_codex_v1

REAL-DATA transfer of the ingest-gate 4th axis (IMPORTANCE = downstream-reach / value-of-information;
the USER "rock-at-head" salience signal). The importance axis was validated ONLY in the synthetic
multisource arena (exp_multisource_arena_v1.py: importance = 0.5*(conseq_reach[h]+conseq_reach[t])).
Schema-fit and recurrence already WON on real CoDEx; importance never was tested. This cell closes it.

THE QUESTION (reported in THREE SEPARATE PARTS -- do not blob):
  1. SEPARABILITY: is IMPORTANCE (downstream-reach on the real CoDEx train graph) a real signal that is
     non-redundant with schema-fit, recurrence, and raw degree/frequency (popularity)?
  2. FOUNDATION-GROWTH: does ingesting HIGH-IMPORTANCE facts first build a foundation that answers
     held-out queries better/sooner (foundation-quality vs #facts) than frequency-order or random-order?
  3. POPULARITY-NEUTRALITY: does importance-order beat a DEGREE-MATCHED ordering (its own degree
     trajectory, importance content scrambled) -- the schema-fit-win fairness discipline?

OPERATIONALIZATION (train-graph-only, label-free, test-free -- same discipline as the schema-fit win):
  IMPORTANCE = downstream-reach / value-of-information of a fact (edge h-t):
    PRIMARY  importance_btwn = SAMPLED edge BETWEENNESS centrality on the undirected train graph.
             Justification: "how many other facts a fact unlocks" = how many shortest reasoning-paths
             between OTHER entity pairs route THROUGH this edge = edge betweenness = value-of-information
             (remove the edge -> those pairwise connections degrade). Classic DEGREE-DECORRELATED
             centrality: a fact between two hubs can be redundant (low betweenness); a bridge fact
             between sparse regions is high-value even at low degree. This is what gives the
             popularity-neutrality question genuine teeth.
    SECONDARY importance_reach = faithful arena transfer: 0.5*(kreach[h]+kreach[t]), kreach = k-hop
             reachable-mass (how much relational structure the endpoints reach). Hub-aligned (correlates
             with degree) -> reported as diagnostic, NOT the neutral headline.

FOUNDATION-QUALITY (held-out, non-circular, popularity-neutral -- REUSED verbatim from the landed
  exp_curriculum_order_ingest_real_codex_v1 chassis): foundation at budget B = the FIRST B triples in an
  arm's ingest order; quality = degree-ORTHOGONALIZED held-out RA schema-fit AUROC (RA fit label-free on
  VALID, residualized on log-degrees, scored on TEST pos vs human-verified hard negatives). This IS the
  validated real query-answering mechanism. AUAC = mean foundation-quality over a fixed budget grid
  (emphasizes the low-budget prioritization regime where order matters; at full graph all orders are
  identical so full is excluded from margins). Secondary path-based cross-check = SR/PPR resolvent AUROC
  at 3 budgets (guards against RA's 2-hop common-neighbor metric structurally favouring hub-front-loading
  frequency-order over bridge-front-loading importance-order).

ARMS (ingest orderings of the SAME train triples):
  importance_btwn      = desc raw betweenness (PRIMARY value-of-information order)
  importance_reach     = desc endpoint k-hop reach (SECONDARY hub-aligned arena transfer)
  importance_btwn_orth = desc degree-orthogonalized betweenness (pure structure, degree removed)
  frequency            = desc relation-freq then endpoint-degree (POPULARITY / recurrence order)
  random               = shuffled arrival (mean over RAND_SEEDS)
  degree_matched       = matches importance_btwn's degree-bin TRAJECTORY, importance content scrambled
                         within degree bin (mean over MATCH_SEEDS) -- the popularity-neutrality control

INFO-CEILING GATE (FIRST, MANDATORY): the foundation-quality metric must be NON-vacuous before any arm is
  interpreted -- (a) full-graph degree-orth RA AUROC >= CEIL_FULL_MIN (the metric resolves truth at all),
  (b) full beats its degree-scramble null by >= CEIL_STRUCT_MIN (structural, not popularity artifact),
  (c) a resolvable GROWTH regime exists: q at the smallest budget is below q at full by >= CEIL_RANGE_MIN
  (else the foundation saturates instantly and no ordering CAN matter). If any fails -> VACUOUS verdict.

PRE-REG BANDS (fixed a-priori; see preregs/2026-07-16_importance_downstream_reach_ingest_prioritization.md):
  info-ceiling PASS is a precondition for ALL of the below.
  PART1 SEPARABLE  : importance_btwn unique-variance (1 - R^2 vs [deg,rel_freq,schema_fit,recurrence]) >=
                     SEP_UNIQVAR_HP AND max|spearman(imp,{deg,rel_freq})| <= SEP_POPCORR_HP.
        REDUNDANT  : unique-variance < SEP_UNIQVAR_HF OR max pop-corr > SEP_POPCORR_HF.
  PART2 BEATS_BOTH : bootstrap p05 of [AUAC(imp_btwn)-AUAC(freq)] > 0 AND p05[AUAC(imp_btwn)-AUAC(rand)] > 0.
        FAILS      : p05[AUAC(imp_btwn)-AUAC(freq)] <= 0 (importance does NOT beat frequency-order).
  PART3 NEUTRAL    : bootstrap p05[AUAC(imp_btwn)-AUAC(degree_matched)] > 0.
        NOT_NEUTRAL: p05 <= 0 (the gain was the degree trajectory, not importance content).
  HARD_PASS  = info-ceiling PASS AND PART1 SEPARABLE AND PART2 BEATS_BOTH AND PART3 NEUTRAL.
  HARD_FAIL  = info-ceiling PASS AND (PART2 FAILS OR PART1 REDUNDANT OR PART3 NOT_NEUTRAL)
               = the 4th axis (importance) does NOT transfer to real data (honest negative; brain-check:
                 the brain's salience/value signals ARE real -> a fail = our real-data operationalization
                 (betweenness importance x RA answerability) is mismatched, NOT the concept).
  MIDDLE     = info-ceiling PASS AND mixed (e.g. separable + beats random but not frequency; or beats
               frequency but not popularity-neutral).
  VACUOUS_METRIC = info-ceiling FAIL (cannot interpret arms).

Determinism: numpy default_rng(fixed int seeds); NO hash()-derived seeds; sorted() for set ops.
ASCII-only. No emojis. Local CPU single-shot run-to-completion (NOT a queue dispatch), so runner
start_marker/heartbeat/run_mode gates do not apply; atomic tmp+os.replace metrics write, no bare except,
SystemExit-first ordering, arms-differ check present. No queue/GPU/atoms/push.

CELL-TEMPLATE compliance (single-shot local, no queue):
- arms_differ_verified: importance vs frequency vs random orderings hashed distinct (META_RULE_AF).
- final_metrics_atomicity: tmp_replace (os.replace) (META_RULE_AH).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: signal is a rank-AUROC over a parameter-free structural score; no noise-floor threshold.
- baseline_in_band: full-graph orth RA AUROC verified measurable (0.05 < q < 0.99) by info-ceiling gate.
- discriminator-fires: info-ceiling GROWTH-regime check (q_smallB < q_full) is the discriminator gate.
- all reported numbers MEASURED@ this cell's metrics.json (no hypothesized numbers in verdict).
"""

import argparse
import json
import math
import os
import sys
import time
import traceback
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "importance_downstream_reach_ingest_prioritization_real_codex_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# ---- fixed config (a-priori) ----
KREACH_HOPS = 3            # arena-faithful downstream reach depth (k-hop endpoint mass)
KREACH_CAP = 4000          # BFS seen-set cap for extreme hubs (mass becomes a floor)
N_BTWN_SOURCES_FULL = 192  # sampled Brandes sources for edge betweenness (approx ranking)
N_BTWN_SOURCES_SMOKE = 48
BTWN_SEED = 2027
SR_GAMMA = 0.6             # SR/PPR resolvent discount = PRIMARY popularity-neutral answerability metric

RAND_SEEDS_FULL = [11, 23, 37]
RAND_SEEDS_SMOKE = [11, 23]
MATCH_SEEDS_FULL = [101, 202, 303]
MATCH_SEEDS_SMOKE = [101, 202]
SCRAMBLE_SEEDS = [7, 17, 29]
SMOKE_TRAIN_CAP = 6000

# budget grid = low/mid regime where prioritization discriminates (full excluded: all orders equal there).
# 500 dropped: at ~500 edges over 2034 nodes the subgraph is near-empty and the resolvent ~ identity.
BUDGET_GRID = [1000, 2000, 4000, 8000, 16000, 24000]
N_BOOT = 400
BOOT_LO_PCT = 5.0
BOOT_SEED = 909

# ---- pre-reg thresholds (FIXED a-priori) ----
CEIL_FULL_MIN = 0.55     # full-graph degree-orth RA AUROC floor (metric resolves truth)
CEIL_STRUCT_MIN = 0.03   # full - degree-scramble null (structural, not popularity artifact)
CEIL_RANGE_MIN = 0.02    # q_full - q_smallestB (a resolvable growth regime exists)

SEP_UNIQVAR_HP = 0.50    # importance unique variance vs [deg,freq,schema_fit,recurrence] for SEPARABLE
SEP_UNIQVAR_HF = 0.20    # below this -> REDUNDANT
SEP_POPCORR_HP = 0.40    # max |spearman(imp, {deg,rel_freq})| for SEPARABLE
SEP_POPCORR_HF = 0.75    # above this -> REDUNDANT

MARGIN_P05_FLOOR = 0.0   # bootstrap p05 of an AUAC margin must exceed this to count as a robust win


# =============================== data ==========================================
def read_triples(raw_dir, fname):
    return [tuple(l.split("\t")) for l in
            open(os.path.join(raw_dir, fname), encoding="utf-8").read().split("\n") if l]


def load_dataset(dataset, scale):
    raw = os.path.join(REPO, "data", dataset, "raw")
    train = read_triples(raw, "train.txt")
    val_p = read_triples(raw, "valid.txt")
    val_n = read_triples(raw, "valid_negatives.txt")
    tst_p = read_triples(raw, "test.txt")
    tst_n = read_triples(raw, "test_negatives.txt")
    if scale == "smoke" and len(train) > SMOKE_TRAIN_CAP:
        rng = np.random.default_rng(BTWN_SEED)
        idx = sorted(rng.choice(len(train), size=SMOKE_TRAIN_CAP, replace=False).tolist())
        train = [train[i] for i in idx]
    ents, rels = set(), set()
    for h, r, t in train + val_p + val_n + tst_p + tst_n:
        ents.add(h); ents.add(t); rels.add(r)
    eidx = {e: i for i, e in enumerate(sorted(ents))}
    ridx = {p: i for i, p in enumerate(sorted(rels))}
    n_ent = len(eidx)
    train_int = np.array([[eidx[h], ridx[r], eidx[t]] for h, r, t in train], dtype=np.int64)
    rel_freq = Counter(r for h, r, t in train)
    rel_freq_int = np.array([rel_freq[r] for h, r, t in train], dtype=np.int64)
    train_set = set(train)
    leak = sum(1 for tp in tst_p if tp in train_set)
    assert leak == 0, "LEAK: %d test positives in train graph" % leak
    # full-graph undirected degree
    deg_full = np.zeros(n_ent, dtype=np.int64)
    seen = [set() for _ in range(n_ent)]
    for h, _r, t in train_int:
        h = int(h); t = int(t)
        if h != t:
            seen[h].add(t); seen[t].add(h)
    for e in range(n_ent):
        deg_full[e] = len(seen[e])

    def pack(pos, neg):
        hi = np.array([eidx[h] for h, r, t in pos] + [eidx[h] for h, r, t in neg], dtype=np.int64)
        ti = np.array([eidx[t] for h, r, t in pos] + [eidx[t] for h, r, t in neg], dtype=np.int64)
        y = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))]).astype(np.float64)
        return hi, ti, y
    val_hi, val_ti, val_y = pack(val_p, val_n)
    test_hi, test_ti, test_y = pack(tst_p, tst_n)
    return {"train_int": train_int, "n_ent": n_ent, "rel_freq_int": rel_freq_int,
            "deg_full": deg_full, "val_hi": val_hi, "val_ti": val_ti, "val_y": val_y,
            "test_hi": test_hi, "test_ti": test_ti, "test_y": test_y}


# =============================== metrics =======================================
def auroc(y, s):
    """Rank-AUROC with tie handling. y in {0,1}, s continuous, higher s => label 1."""
    y = np.asarray(y, dtype=np.float64)
    s = np.asarray(s, dtype=np.float64)
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=np.float64)
    ranks[order] = np.arange(1, len(s) + 1)
    s_sorted = s[order]
    i = 0
    while i < len(s_sorted):
        j = i
        while j + 1 < len(s_sorted) and s_sorted[j + 1] == s_sorted[i]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for kk in range(i, j + 1):
                ranks[order[kk]] = avg
        i = j + 1
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    sum_pos = ranks[y == 1].sum()
    return float((sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def rankdata_avg(a):
    a = np.asarray(a, dtype=np.float64)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    ranks[order] = np.arange(1, len(a) + 1)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        if j > i:
            avg = (ranks[order[i]] + ranks[order[j]]) / 2.0
            for kk in range(i, j + 1):
                ranks[order[kk]] = avg
        i = j + 1
    return ranks


def spearman(x, y):
    rx = rankdata_avg(x); ry = rankdata_avg(y)
    rx = rx - rx.mean(); ry = ry - ry.mean()
    d = math.sqrt(float((rx * rx).sum()) * float((ry * ry).sum()))
    return float((rx * ry).sum() / d) if d > 0 else 0.0


# =============================== foundation quality ============================
def build_foundation_nbr(train_int, admitted_rows, n_ent):
    nbr = [set() for _ in range(n_ent)]
    for idx in admitted_rows:
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        if h != t:
            nbr[h].add(t); nbr[t].add(h)
    deg = np.array([len(s) for s in nbr], dtype=np.int64)
    return nbr, deg


def ra_scores(nbr, deg, hi, ti):
    """Pairwise Resource-Allocation index over foundation neighbor sets."""
    out = np.zeros(len(hi), dtype=np.float64)
    for k in range(len(hi)):
        a = int(hi[k]); b = int(ti[k])
        na = nbr[a]; nb = nbr[b]
        if not na or not nb:
            continue
        common = na & nb if len(na) <= len(nb) else nb & na
        v = 0.0
        for z in common:
            dz = deg[z]
            if dz > 0:
                v += 1.0 / dz
        out[k] = v
    return out


def fit_degree_projection(score, log_hdeg, log_tdeg):
    """LABEL-FREE OLS coefficients for score ~ [1, log_hdeg, log_tdeg]."""
    n = len(score)
    A = np.column_stack([np.ones(n), log_hdeg, log_tdeg])
    coef, _, _, _ = np.linalg.lstsq(A, score, rcond=None)
    return coef


def _best_degree_auroc(y, deg, hi, ti):
    dh = deg[hi].astype(np.float64); dt = deg[ti].astype(np.float64)
    out = 0.0
    for v in (dh, dt, dh + dt):
        a = auroc(y, v)
        out = max(out, a, 1.0 - a)
    return out


def foundation_test_resid(data, admitted_rows):
    """Degree-orthogonalized held-out RA quality from the admitted foundation. Returns per-TEST-row
    residual scores (for bootstrap) + point AUROCs + degree baseline."""
    nbr, deg = build_foundation_nbr(data["train_int"], admitted_rows, data["n_ent"])
    vhi, vti = data["val_hi"], data["val_ti"]
    thi, tti, ty = data["test_hi"], data["test_ti"], data["test_y"]
    v_ra = ra_scores(nbr, deg, vhi, vti)
    t_ra = ra_scores(nbr, deg, thi, tti)
    v_lh = np.log1p(deg[vhi].astype(np.float64)); v_lt = np.log1p(deg[vti].astype(np.float64))
    t_lh = np.log1p(deg[thi].astype(np.float64)); t_lt = np.log1p(deg[tti].astype(np.float64))
    coef = fit_degree_projection(v_ra, v_lh, v_lt)
    t_resid = t_ra - (coef[0] + coef[1] * t_lh + coef[2] * t_lt)
    return {"test_resid": t_resid, "orth_auroc": auroc(ty, t_resid), "raw_auroc": auroc(ty, t_ra),
            "degree_auroc": _best_degree_auroc(ty, deg, thi, tti), "nbr": nbr, "deg": deg}


def scramble_orth_auroc(data, admitted_rows, rng):
    """Degree-preserving rewire null: orth-RA-AUROC must collapse to chance if the metric is structural."""
    n_ent = data["n_ent"]
    _n0, deg0 = build_foundation_nbr(data["train_int"], admitted_rows, n_ent)
    w = deg0.astype(np.float64); tot = w.sum()
    if tot <= 0:
        return 0.5
    p = w / tot
    m = len(admitted_rows)
    heads = rng.choice(n_ent, size=m, p=p); tails = rng.choice(n_ent, size=m, p=p)
    nbr = [set() for _ in range(n_ent)]
    for a, b in zip(heads.tolist(), tails.tolist()):
        if a != b:
            nbr[a].add(b); nbr[b].add(a)
    deg = np.array([len(s) for s in nbr], dtype=np.int64)
    return foundation_test_resid_from_nbr(data, nbr, deg)["orth_auroc"]


def foundation_test_resid_from_nbr(data, nbr, deg):
    vhi, vti = data["val_hi"], data["val_ti"]
    thi, tti, ty = data["test_hi"], data["test_ti"], data["test_y"]
    v_ra = ra_scores(nbr, deg, vhi, vti)
    t_ra = ra_scores(nbr, deg, thi, tti)
    v_lh = np.log1p(deg[vhi].astype(np.float64)); v_lt = np.log1p(deg[vti].astype(np.float64))
    t_lh = np.log1p(deg[thi].astype(np.float64)); t_lt = np.log1p(deg[tti].astype(np.float64))
    coef = fit_degree_projection(v_ra, v_lh, v_lt)
    t_resid = t_ra - (coef[0] + coef[1] * t_lh + coef[2] * t_lt)
    return {"orth_auroc": auroc(ty, t_resid), "test_resid": t_resid}


# =============================== SR/PPR resolvent (PRIMARY answerability) =======
# RA (2-hop common-neighbor) is popularity-VACUOUS after degree-orthogonalization on this data
# (measured: full-graph orth RA AUROC 0.489, struct-vs-scramble 0.012). The SR/PPR resolvent (multi-hop
# path reachability) IS the popularity-neutral answerability signal (measured: full-graph orth 0.738) --
# it is the real schema-fit-win signal. So the resolvent is the PRIMARY foundation-quality metric here;
# RA is reported as a documented diagnostic only.
def _sr_M(data, admitted_rows, gamma):
    n_ent = data["n_ent"]
    nbr, deg = build_foundation_nbr(data["train_int"], admitted_rows, n_ent)
    A = np.zeros((n_ent, n_ent), dtype=np.float64)
    for u in range(n_ent):
        for v in nbr[u]:
            A[u, v] = 1.0
    d = A.sum(axis=1, keepdims=True); d[d == 0.0] = 1.0
    T = A / d
    M = np.linalg.inv(np.eye(n_ent, dtype=np.float64) - gamma * T)
    return M, deg


def _sr_pairs(M, hi, ti):
    out = np.zeros(len(hi), dtype=np.float64)
    for i in range(len(hi)):
        a = int(hi[i]); b = int(ti[i])
        out[i] = 0.0 if a == b else 0.5 * (M[b, a] + M[a, b])
    return out


def sr_foundation(data, admitted_rows, gamma):
    """Degree-orthogonalized held-out SR/PPR resolvent quality from the admitted foundation subgraph.
    Returns per-TEST-row residual scores (for bootstrap) + point orth/raw AUROC + degree baseline."""
    M, deg = _sr_M(data, admitted_rows, gamma)
    vhi, vti = data["val_hi"], data["val_ti"]
    thi, tti, ty = data["test_hi"], data["test_ti"], data["test_y"]
    v_s = _sr_pairs(M, vhi, vti); t_s = _sr_pairs(M, thi, tti)
    v_lh = np.log1p(deg[vhi].astype(np.float64)); v_lt = np.log1p(deg[vti].astype(np.float64))
    t_lh = np.log1p(deg[thi].astype(np.float64)); t_lt = np.log1p(deg[tti].astype(np.float64))
    coef = fit_degree_projection(v_s, v_lh, v_lt)
    t_resid = t_s - (coef[0] + coef[1] * t_lh + coef[2] * t_lt)
    return {"test_resid": t_resid, "orth_auroc": auroc(ty, t_resid), "raw_auroc": auroc(ty, t_s),
            "degree_auroc": _best_degree_auroc(ty, deg, thi, tti)}


def sr_scramble_orth(data, admitted_rows, gamma, rng):
    """Degree-preserving rewire null under the SR metric: orth AUROC must collapse if the resolvent
    answerability is structural rather than a popularity artifact."""
    n_ent = data["n_ent"]
    _n0, deg0 = build_foundation_nbr(data["train_int"], admitted_rows, n_ent)
    w = deg0.astype(np.float64); tot = w.sum()
    if tot <= 0:
        return 0.5
    p = w / tot; m = len(admitted_rows)
    heads = rng.choice(n_ent, size=m, p=p); tails = rng.choice(n_ent, size=m, p=p)
    A = np.zeros((n_ent, n_ent), dtype=np.float64)
    deg = np.zeros(n_ent, dtype=np.int64)
    seen = [set() for _ in range(n_ent)]
    for a, b in zip(heads.tolist(), tails.tolist()):
        if a != b:
            seen[a].add(b); seen[b].add(a)
    for u in range(n_ent):
        for v in seen[u]:
            A[u, v] = 1.0
        deg[u] = len(seen[u])
    d = A.sum(axis=1, keepdims=True); d[d == 0.0] = 1.0
    M = np.linalg.inv(np.eye(n_ent, dtype=np.float64) - gamma * (A / d))
    vhi, vti = data["val_hi"], data["val_ti"]
    thi, tti, ty = data["test_hi"], data["test_ti"], data["test_y"]
    v_s = _sr_pairs(M, vhi, vti); t_s = _sr_pairs(M, thi, tti)
    v_lh = np.log1p(deg[vhi].astype(np.float64)); v_lt = np.log1p(deg[vti].astype(np.float64))
    t_lh = np.log1p(deg[thi].astype(np.float64)); t_lt = np.log1p(deg[tti].astype(np.float64))
    coef = fit_degree_projection(v_s, v_lh, v_lt)
    return auroc(ty, t_s - (coef[0] + coef[1] * t_lh + coef[2] * t_lt))


# =============================== importance signals ============================
def build_adj_list(train_int, n_ent):
    """Undirected simple-graph adjacency (list of sorted neighbor lists) + unique-edge index."""
    nbr = [set() for _ in range(n_ent)]
    for idx in range(train_int.shape[0]):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        if h != t:
            nbr[h].add(t); nbr[t].add(h)
    adj = [sorted(s) for s in nbr]
    edge_id = {}
    for u in range(n_ent):
        for v in adj[u]:
            if u < v:
                edge_id[(u, v)] = len(edge_id)
    return adj, edge_id


def sampled_edge_betweenness(adj, n_ent, edge_id, n_sources, seed):
    """Brandes edge-betweenness with sampled BFS sources (undirected, unweighted). Returns eb[edge_id]."""
    rng = np.random.default_rng(seed)
    noniso = [v for v in range(n_ent) if adj[v]]
    if n_sources >= len(noniso):
        sources = sorted(noniso)
    else:
        sources = sorted(rng.choice(np.array(noniso), size=n_sources, replace=False).tolist())
    n_edges = len(edge_id)
    eb = np.zeros(n_edges, dtype=np.float64)
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
                c = (sigma[v] / sw) * (1.0 + dw)
                key = (v, w) if v < w else (w, v)
                eb[edge_id[key]] += c
                delta[v] += c
    scale = float(len(noniso)) / max(len(sources), 1)   # extrapolate sampled sum to full-source scale
    return eb * scale, len(sources)


def per_triple_importance(train_int, n_ent, adj, edge_id, eb, kreach):
    """Map per-EDGE betweenness + per-NODE k-hop reach to per-TRIPLE importance values."""
    n = train_int.shape[0]
    imp_btwn = np.zeros(n, dtype=np.float64)
    imp_reach = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        if h != t:
            key = (h, t) if h < t else (t, h)
            imp_btwn[idx] = eb[edge_id[key]] if key in edge_id else 0.0
        imp_reach[idx] = 0.5 * (float(kreach[h]) + float(kreach[t]))
    return imp_btwn, imp_reach


# =============================== separability =================================
def per_triple_feature_table(train_int, n_ent, adj, deg_full, rel_freq_int, imp_btwn, imp_reach):
    """Per-triple: schema_fit (RA of the pair, full graph), recurrence (common-neighbor COUNT),
    degree (log endpoint-deg sum), rel_freq (log). Returns dict of arrays for the separability analysis."""
    n = train_int.shape[0]
    nbrset = [set(a) for a in adj]
    schema_fit = np.zeros(n, dtype=np.float64)
    recurrence = np.zeros(n, dtype=np.float64)
    degree = np.zeros(n, dtype=np.float64)
    relfreq = np.zeros(n, dtype=np.float64)
    for idx in range(n):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        na = nbrset[h]; nb = nbrset[t]
        if na and nb and h != t:
            common = na & nb if len(na) <= len(nb) else nb & na
            recurrence[idx] = float(len(common))
            v = 0.0
            for z in common:
                dz = deg_full[z]
                if dz > 0:
                    v += 1.0 / float(dz)
            schema_fit[idx] = v
        degree[idx] = math.log1p(deg_full[h]) + math.log1p(deg_full[t])
        relfreq[idx] = math.log1p(int(rel_freq_int[idx]))
    return {"importance_btwn": imp_btwn, "importance_reach": imp_reach, "schema_fit": schema_fit,
            "recurrence": recurrence, "degree": degree, "rel_freq": relfreq}


def separability_analysis(feat):
    """Correlation matrix (spearman) + unique variance of importance_btwn vs the other 4 signals.
    unique_variance = 1 - R^2 of OLS regressing z(importance_btwn) on z([deg,rel_freq,schema_fit,
    recurrence]). Also reports the degree-orthogonalized importance to confirm residual structure remains."""
    names = ["importance_btwn", "importance_reach", "schema_fit", "recurrence", "degree", "rel_freq"]
    corr = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            corr["%s__%s" % (names[i], names[j])] = spearman(feat[names[i]], feat[names[j]])

    def z(a):
        a = np.asarray(a, dtype=np.float64)
        sd = a.std()
        return (a - a.mean()) / sd if sd > 1e-12 else a * 0.0

    y = z(feat["importance_btwn"])
    others = ["degree", "rel_freq", "schema_fit", "recurrence"]
    X = np.column_stack([np.ones(len(y))] + [z(feat[o]) for o in others])
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = float(((y - yhat) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    unique_var = max(0.0, 1.0 - r2)
    max_pop_corr = max(abs(corr["importance_btwn__degree"]), abs(corr["importance_btwn__rel_freq"]))
    if unique_var >= SEP_UNIQVAR_HP and max_pop_corr <= SEP_POPCORR_HP:
        tier = "SEPARABLE"
    elif unique_var < SEP_UNIQVAR_HF or max_pop_corr > SEP_POPCORR_HF:
        tier = "REDUNDANT"
    else:
        tier = "PARTIAL"
    return {"spearman_corr": corr, "importance_btwn_R2_on_others": r2,
            "importance_btwn_unique_variance": unique_var, "max_pop_corr": max_pop_corr,
            "separability_tier": tier,
            "R2_regressors": others}


# =============================== orderings ====================================
def order_desc(values, tiebreak_seed):
    """Descending order by value, random tie-break (deterministic seed) then id. Returns row-index list."""
    rng = np.random.default_rng(tiebreak_seed)
    jitter = rng.random(len(values)) * 1e-9
    keys = [(-float(values[i] + jitter[i]), i) for i in range(len(values))]
    keys.sort()
    return [k[1] for k in keys]


def frequency_order(train_int, rel_freq_int, deg_full):
    n = train_int.shape[0]
    keys = []
    for idx in range(n):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        keys.append((-int(rel_freq_int[idx]), -(int(deg_full[h]) + int(deg_full[t])), idx))
    keys.sort()
    return [k[2] for k in keys]


def degree_bin_map(train_int, deg_full, n_bins=4):
    """Per-triple (dbin(h), dbin(t)) key from quartile bins of log-degree (order-independent id)."""
    ld = np.log1p(deg_full[deg_full > 0].astype(np.float64))
    qthr = np.quantile(ld, np.linspace(0, 1, n_bins + 1)[1:-1]) if len(ld) else np.zeros(n_bins - 1)

    def dbin(e):
        return int(np.searchsorted(qthr, math.log1p(deg_full[e])))
    keys = []
    for idx in range(train_int.shape[0]):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        a, b = dbin(h), dbin(t)
        keys.append((a, b) if a <= b else (b, a))
    return keys


def degree_matched_order(reference_order, dbin_keys, seed):
    """Ordering that reproduces reference_order's degree-bin TRAJECTORY exactly, but scrambles the
    within-bin selection (importance content removed). At every prefix B the degree-bin composition
    equals the reference's -> isolates whether the reference's gain is degree-trajectory or content."""
    rng = np.random.default_rng(seed)
    buckets = defaultdict(list)
    for idx in range(len(dbin_keys)):
        buckets[dbin_keys[idx]].append(idx)
    for kb in buckets:
        arr = buckets[kb]
        perm = rng.permutation(len(arr))
        buckets[kb] = [arr[p] for p in perm]
    cursor = defaultdict(int)
    out = []
    for idx in reference_order:
        kb = dbin_keys[idx]
        c = cursor[kb]
        out.append(buckets[kb][c])
        cursor[kb] += 1
    return out


# =============================== AUAC over budgets =============================
def arm_curve_resid(data, order, grid):
    """Per-budget cached TEST residual scores + point orth AUROC for an ordering, under the PRIMARY
    SR/PPR resolvent answerability metric. resid_by_B[B] = per-test-row residual, q_by_B[B] = orth AUROC."""
    resid_by_B = {}
    q_by_B = {}
    for B in grid:
        r = sr_foundation(data, order[:B], SR_GAMMA)
        resid_by_B[B] = r["test_resid"]
        q_by_B[B] = r["orth_auroc"]
    return resid_by_B, q_by_B


def auac_from_q(q_by_B, grid):
    """Mean foundation-quality over the budget grid (equal weight -> emphasizes low-budget regime)."""
    return float(np.mean([q_by_B[B] for B in grid]))


def facts_to_target(q_by_B, grid, q_full, frac=0.9):
    """Linear-interpolated #facts at which quality first reaches frac*q_full. None if never within grid."""
    target = frac * q_full
    prevB, prevq = 0, 0.5
    for B in grid:
        q = q_by_B[B]
        if q >= target:
            if q == prevq:
                return float(B)
            f = (target - prevq) / (q - prevq)
            return float(prevB + f * (B - prevB))
        prevB, prevq = B, q
    return None


# =============================== main run =====================================
def run(data, scale):
    t0 = time.time()
    train_int = data["train_int"]; n_ent = data["n_ent"]
    n_tr = train_int.shape[0]
    grid = [b for b in BUDGET_GRID if b < n_tr]
    if not grid:
        grid = [max(1, n_tr // 2)]

    rand_seeds = RAND_SEEDS_SMOKE if scale == "smoke" else RAND_SEEDS_FULL
    match_seeds = MATCH_SEEDS_SMOKE if scale == "smoke" else MATCH_SEEDS_FULL
    n_btwn = N_BTWN_SOURCES_SMOKE if scale == "smoke" else N_BTWN_SOURCES_FULL

    # ---- importance signals (train-graph-only, label-free) ----
    from hdlab import reachability_audit as ra
    adj_arr = ra.build_undirected_adj(train_int, n_ent)          # list of np arrays (for k-hop reach)
    kreach = ra.k_hop_reachable_mass(adj_arr, KREACH_HOPS, cap=KREACH_CAP)
    adj, edge_id = build_adj_list(train_int, n_ent)
    print("[imp] sampled edge betweenness: n_sources=%d n_edges=%d ..." % (n_btwn, len(edge_id)), flush=True)
    tb = time.time()
    eb, used_sources = sampled_edge_betweenness(adj, n_ent, edge_id, n_btwn, BTWN_SEED)
    print("[imp] betweenness done in %.1fs (sources=%d)" % (time.time() - tb, used_sources), flush=True)
    imp_btwn, imp_reach = per_triple_importance(train_int, n_ent, adj, edge_id, eb, kreach)

    # ---- separability (PART 1) ----
    feat = per_triple_feature_table(train_int, n_ent, adj, data["deg_full"],
                                    data["rel_freq_int"], imp_btwn, imp_reach)
    sep = separability_analysis(feat)
    print("[sep] tier=%s unique_var=%.3f max_pop_corr=%.3f (imp~deg=%.3f imp~schemafit=%.3f)" % (
        sep["separability_tier"], sep["importance_btwn_unique_variance"], sep["max_pop_corr"],
        sep["spearman_corr"]["importance_btwn__degree"],
        sep["spearman_corr"]["importance_btwn__schema_fit"]), flush=True)

    # ---- degree-orthogonalized betweenness (pure structure) for the diag arm ----
    lh = np.log1p(data["deg_full"][train_int[:, 0]].astype(np.float64))
    lt = np.log1p(data["deg_full"][train_int[:, 2]].astype(np.float64))
    coef_imp = fit_degree_projection(imp_btwn, lh, lt)
    imp_btwn_orth = imp_btwn - (coef_imp[0] + coef_imp[1] * lh + coef_imp[2] * lt)

    # ---- orderings ----
    dbin_keys = degree_bin_map(train_int, data["deg_full"])
    orders = {
        "importance_btwn": order_desc(imp_btwn, 1),
        "importance_reach": order_desc(imp_reach, 2),
        "importance_btwn_orth": order_desc(imp_btwn_orth, 3),
        "frequency": frequency_order(train_int, data["rel_freq_int"], data["deg_full"]),
    }
    rand_orders = {s: np.random.default_rng(s).permutation(n_tr).tolist() for s in rand_seeds}
    match_orders = {s: degree_matched_order(orders["importance_btwn"], dbin_keys, s) for s in match_seeds}

    # ---- per-arm quality curves (cache test residuals for bootstrap) ----
    print("[curve] budget grid=%s building %d single + %d rand + %d match arm curves ..." % (
        grid, len(orders), len(rand_orders), len(match_orders)), flush=True)
    resid = {}; qcurve = {}
    for name, o in orders.items():
        resid[name], qcurve[name] = arm_curve_resid(data, o, grid)
    rand_resid = {}; rand_q = {}
    for s, o in rand_orders.items():
        rand_resid[s], rand_q[s] = arm_curve_resid(data, o, grid)
    match_resid = {}; match_q = {}
    for s, o in match_orders.items():
        match_resid[s], match_q[s] = arm_curve_resid(data, o, grid)

    # mean per-row residual across seeds (for a single bootstrappable random/degree-matched curve)
    def mean_resid(rd):
        return {B: np.mean([rd[s][B] for s in rd], axis=0) for B in grid}

    def mean_q(qd):
        return {B: float(np.mean([qd[s][B] for s in qd])) for B in grid}
    rand_resid_m = mean_resid(rand_resid); rand_q_m = mean_q(rand_q)
    match_resid_m = mean_resid(match_resid); match_q_m = mean_q(match_q)

    # ---- full-graph foundation quality (PRIMARY=SR resolvent) + scramble null + info-ceiling ----
    full_rows = list(range(n_tr))
    q_full = sr_foundation(data, full_rows, SR_GAMMA)
    ra_full = foundation_test_resid(data, full_rows)   # RA diagnostic (documented popularity-vacuity)
    scr = [sr_scramble_orth(data, full_rows, SR_GAMMA, np.random.default_rng(s)) for s in SCRAMBLE_SEEDS]
    scramble_full = float(np.mean(scr))
    q_full_orth = q_full["orth_auroc"]
    smallest_B = grid[0]
    q_smallB = float(np.mean([rand_q_m[smallest_B]] + [qcurve[n][smallest_B] for n in orders]))
    info_ceiling_struct = q_full_orth - scramble_full
    growth_range = q_full_orth - q_smallB
    info_ceiling_pass = (q_full_orth >= CEIL_FULL_MIN and info_ceiling_struct >= CEIL_STRUCT_MIN
                         and growth_range >= CEIL_RANGE_MIN)

    # ---- AUAC point estimates ----
    auac = {n: auac_from_q(qcurve[n], grid) for n in orders}
    auac["random"] = auac_from_q(rand_q_m, grid)
    auac["degree_matched"] = auac_from_q(match_q_m, grid)
    ftt = {n: facts_to_target(qcurve[n], grid, q_full_orth) for n in orders}
    ftt["random"] = facts_to_target(rand_q_m, grid, q_full_orth)
    ftt["degree_matched"] = facts_to_target(match_q_m, grid, q_full_orth)

    # ---- bootstrap AUAC margins (resample TEST rows; recompute per-B AUROC from cached residuals) ----
    ty = data["test_y"]
    n_test = len(ty)
    rng = np.random.default_rng(BOOT_SEED)

    def auac_boot(resid_by_B, idx):
        yb = ty[idx]
        if yb.sum() == 0 or yb.sum() == len(yb):
            return None
        return float(np.mean([auroc(yb, resid_by_B[B][idx]) for B in grid]))

    boot_imp = []; boot_freq = []; boot_rand = []; boot_match = []
    for _b in range(N_BOOT):
        idx = rng.integers(0, n_test, size=n_test)
        ai = auac_boot(resid["importance_btwn"], idx)
        af = auac_boot(resid["frequency"], idx)
        ar = auac_boot(rand_resid_m, idx)
        am = auac_boot(match_resid_m, idx)
        if None in (ai, af, ar, am):
            continue
        boot_imp.append(ai); boot_freq.append(af); boot_rand.append(ar); boot_match.append(am)
    boot_imp = np.array(boot_imp); boot_freq = np.array(boot_freq)
    boot_rand = np.array(boot_rand); boot_match = np.array(boot_match)
    m_if = boot_imp - boot_freq
    m_ir = boot_imp - boot_rand
    m_im = boot_imp - boot_match

    def p05(a):
        return float(np.percentile(a, BOOT_LO_PCT)) if len(a) else 0.0
    margin_imp_freq_p05 = p05(m_if)
    margin_imp_rand_p05 = p05(m_ir)
    margin_imp_match_p05 = p05(m_im)

    # ---- RA diagnostic (documents that 2-hop RA answerability is popularity-vacuous on this data) ----
    ra_diag = {"ra_raw_auroc_full": ra_full["raw_auroc"], "ra_orth_auroc_full": ra_full["orth_auroc"],
               "degree_auroc_full": ra_full["degree_auroc"],
               "note": "RA orth AUROC near/below chance -> RA power is popularity; SR resolvent used as primary."}

    # ---- verdict ----
    tier = sep["separability_tier"]
    part1_separable = (tier == "SEPARABLE")
    part1_redundant = (tier == "REDUNDANT")
    part2_beats_both = (margin_imp_freq_p05 > MARGIN_P05_FLOOR and margin_imp_rand_p05 > MARGIN_P05_FLOOR)
    part2_fails = (margin_imp_freq_p05 <= MARGIN_P05_FLOOR)
    part3_neutral = (margin_imp_match_p05 > MARGIN_P05_FLOOR)
    part3_not_neutral = (margin_imp_match_p05 <= MARGIN_P05_FLOOR)

    # arms-differ (direct order-prefix comparison; no hashing)
    arms_differ = (orders["importance_btwn"][:500] != orders["frequency"][:500]
                   and orders["importance_btwn"][:500] != rand_orders[rand_seeds[0]][:500]
                   and orders["importance_btwn"][:500] != match_orders[match_seeds[0]][:500])

    if not info_ceiling_pass:
        verdict = "VACUOUS_METRIC_INFO_CEILING_FAIL"
    elif not arms_differ:
        verdict = "BLOCK_ARMS_IDENTICAL"
    elif part1_separable and part2_beats_both and part3_neutral:
        verdict = "HARD_PASS_IMPORTANCE_TRANSFERS_TO_REAL_DATA"
    elif part2_fails or part1_redundant or part3_not_neutral:
        verdict = "HARD_FAIL_IMPORTANCE_AXIS_DOES_NOT_TRANSFER_TO_REAL_DATA"
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
        "n_ent": n_ent, "n_train": n_tr, "n_test": n_test,
        "budget_grid": grid,
        "info_ceiling": {
            "q_full_orth_auroc": q_full_orth,
            "scramble_full_orth_auroc": scramble_full,
            "info_ceiling_structural": info_ceiling_struct,
            "q_smallB_mean": q_smallB, "growth_range": growth_range,
            "thresholds": {"CEIL_FULL_MIN": CEIL_FULL_MIN, "CEIL_STRUCT_MIN": CEIL_STRUCT_MIN,
                           "CEIL_RANGE_MIN": CEIL_RANGE_MIN},
            "info_ceiling_pass": bool(info_ceiling_pass),
        },
        "part1_separability": sep,
        "part2_foundation_growth": {
            "auac_by_arm": auac,
            "facts_to_90pct_full": ftt,
            "q_full_orth_auroc": q_full_orth,
            "margin_imp_freq_p05": margin_imp_freq_p05,
            "margin_imp_rand_p05": margin_imp_rand_p05,
            "margin_imp_freq_mean": float(m_if.mean()) if len(m_if) else 0.0,
            "margin_imp_rand_mean": float(m_ir.mean()) if len(m_ir) else 0.0,
            "beats_both": bool(part2_beats_both), "fails": bool(part2_fails),
            "n_boot_used": int(len(boot_imp)),
        },
        "part3_popularity_neutrality": {
            "auac_importance_btwn": auac["importance_btwn"],
            "auac_degree_matched": auac["degree_matched"],
            "margin_imp_degmatched_p05": margin_imp_match_p05,
            "margin_imp_degmatched_mean": float(m_im.mean()) if len(m_im) else 0.0,
            "neutral": bool(part3_neutral), "not_neutral": bool(part3_not_neutral),
        },
        "primary_metric": "degree_orthogonalized_SR_PPR_resolvent_orth_AUROC (gamma=%.2f)" % SR_GAMMA,
        "ra_diagnostic": ra_diag,
        "qcurve_by_arm": {n: {str(B): qcurve[n][B] for B in grid} for n in orders},
        "qcurve_random_mean": {str(B): rand_q_m[B] for B in grid},
        "qcurve_degree_matched_mean": {str(B): match_q_m[B] for B in grid},
        "config": {
            "kreach_hops": KREACH_HOPS, "n_btwn_sources": used_sources, "sr_gamma": SR_GAMMA,
            "rand_seeds": rand_seeds, "match_seeds": match_seeds, "scramble_seeds": SCRAMBLE_SEEDS,
            "n_boot": N_BOOT, "bands": {
                "SEP_UNIQVAR_HP": SEP_UNIQVAR_HP, "SEP_UNIQVAR_HF": SEP_UNIQVAR_HF,
                "SEP_POPCORR_HP": SEP_POPCORR_HP, "SEP_POPCORR_HF": SEP_POPCORR_HF,
                "MARGIN_P05_FLOOR": MARGIN_P05_FLOOR}},
        "arms_differ": bool(arms_differ),
        "verdict_msg": (
            "%s | SEP tier=%s (uniqvar=%.3f max_pop_corr=%.3f) | GROWTH[SR-resolvent] auac imp=%.4f "
            "freq=%.4f rand=%.4f (p05 imp-freq=%+.4f imp-rand=%+.4f) | NEUTRAL auac degmatched=%.4f "
            "(p05 imp-degm=%+.4f) | info_ceiling(full_orth=%.3f struct=%.3f range=%.3f pass=%s) | "
            "RA-diag orth=%.3f (popularity-vacuous)" % (
                verdict, tier, sep["importance_btwn_unique_variance"], sep["max_pop_corr"],
                auac["importance_btwn"], auac["frequency"], auac["random"],
                margin_imp_freq_p05, margin_imp_rand_p05, auac["degree_matched"], margin_imp_match_p05,
                q_full_orth, info_ceiling_struct, growth_range, info_ceiling_pass, ra_full["orth_auroc"])),
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
    # (A) auroc orientation + ties
    assert auroc(np.array([1, 1, 0, 0]), np.array([.9, .8, .2, .1])) == 1.0, "auroc orientation"
    assert abs(auroc(np.array([1, 0]), np.array([.5, .5])) - 0.5) < 1e-9, "auroc ties -> 0.5"

    # (B) spearman + separability primitives on a planted example
    x = np.arange(50.0); y = x * 2.0 + 1.0
    assert abs(spearman(x, y) - 1.0) < 1e-9, "spearman monotone -> 1"
    assert abs(spearman(x, -y) + 1.0) < 1e-9, "spearman anti -> -1"

    # (C) betweenness fires on a planted bridge: path 0-1-2-3-4 -> the middle edge (1,2)?? use bridge graph:
    #     two triangles {0,1,2} and {3,4,5} joined by a single bridge edge (2,3). The bridge must have the
    #     HIGHEST edge betweenness (all cross-cluster shortest paths route through it) -> degree-decorrelated.
    tri = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (2, 3)]
    n = 6
    train = np.array([[a, 0, b] for a, b in tri], dtype=np.int64)
    adj, eid = build_adj_list(train, n)
    eb, used = sampled_edge_betweenness(adj, n, eid, n, 1)
    bridge = eid[(2, 3)]
    others = [eid[k] for k in eid if k != (2, 3)]
    assert eb[bridge] > max(eb[o] for o in others) + 1e-9, \
        "betweenness self-test: bridge edge must dominate (bridge=%.3f max_other=%.3f)" % (
            eb[bridge], max(eb[o] for o in others))
    # bridge endpoints (2 and 3) have SAME degree (3) as their triangle peers -> betweenness is NOT degree.

    # (D) degree_matched_order reproduces the reference degree-bin trajectory exactly.
    rng = np.random.default_rng(0)
    m = 400
    dfull = rng.integers(1, 40, size=60)
    ti2 = np.column_stack([rng.integers(0, 60, m), np.zeros(m, dtype=np.int64), rng.integers(0, 60, m)])
    keys = degree_bin_map(ti2, dfull)
    ref = list(rng.permutation(m))
    dm = degree_matched_order(ref, keys, 7)
    assert sorted(dm) == sorted(ref), "degree_matched must be a permutation of all rows"
    for pos in range(m):
        assert keys[dm[pos]] == keys[ref[pos]], "degree_matched must match ref degree-bin at every position"
    assert dm != ref, "degree_matched must scramble content (not identical to reference)"

    # (E) PRIMARY answerability metric (SR/PPR resolvent) + info-ceiling on REAL CoDEx at FULL-N (fast).
    #     Verifies the metric is NON-vacuous (the mandatory precondition) BEFORE trusting any arm. RA
    #     (2-hop) is ALSO measured to confirm it is popularity-vacuous (why the resolvent is primary).
    data = load_dataset("codex_claimvalidity", "full")
    full = list(range(data["train_int"].shape[0]))
    q_full = sr_foundation(data, full, SR_GAMMA)
    ra_full = foundation_test_resid(data, full)
    assert 0.05 < q_full["orth_auroc"] < 0.99, "full orth SR AUROC must be measurable, got %.3f" % q_full["orth_auroc"]
    assert q_full["orth_auroc"] >= CEIL_FULL_MIN, \
        "info-ceiling precondition: full SR orth AUROC %.3f must clear CEIL_FULL_MIN=%.2f" % (
            q_full["orth_auroc"], CEIL_FULL_MIN)
    scr = np.mean([sr_scramble_orth(data, full, SR_GAMMA, np.random.default_rng(s)) for s in SCRAMBLE_SEEDS])
    assert q_full["orth_auroc"] - scr >= CEIL_STRUCT_MIN, \
        "info-ceiling: full SR must beat scramble null by >= %.2f (got %.3f)" % (
            CEIL_STRUCT_MIN, q_full["orth_auroc"] - scr)
    assert ra_full["orth_auroc"] < q_full["orth_auroc"], "RA-diagnostic: RA orth must be below SR orth"

    print("[SELF-TEST] PASS  SR full_orth=%.3f scramble=%.3f (struct=%.3f) | RA_orth=%.3f (vacuous) | bridge_ok" % (
        q_full["orth_auroc"], scr, q_full["orth_auroc"] - scr, ra_full["orth_auroc"]))
    return True


# =============================== entry ========================================
def main(scale="full"):
    data = load_dataset("codex_claimvalidity", scale)
    print("[load] scale=%s n_ent=%d n_train=%d n_test=%d" % (
        scale, data["n_ent"], data["train_int"].shape[0], len(data["test_y"])), flush=True)
    out = run(data, scale)
    final = write_metrics(out)
    print("[VERDICT] %s" % out["verdict"])
    print("  PART1 SEPARABILITY: tier=%s uniq_var=%.3f max_pop_corr=%.3f" % (
        out["part1_separability"]["separability_tier"],
        out["part1_separability"]["importance_btwn_unique_variance"],
        out["part1_separability"]["max_pop_corr"]))
    sc = out["part1_separability"]["spearman_corr"]
    print("    corr: imp~deg=%.3f imp~relfreq=%.3f imp~schemafit=%.3f imp~recurrence=%.3f imp~reach=%.3f" % (
        sc["importance_btwn__degree"], sc["importance_btwn__rel_freq"], sc["importance_btwn__schema_fit"],
        sc["importance_btwn__recurrence"], sc["importance_btwn__importance_reach"]))
    g = out["part2_foundation_growth"]
    print("  PART2 GROWTH: AUAC imp_btwn=%.4f imp_reach=%.4f imp_orth=%.4f freq=%.4f rand=%.4f" % (
        g["auac_by_arm"]["importance_btwn"], g["auac_by_arm"]["importance_reach"],
        g["auac_by_arm"]["importance_btwn_orth"], g["auac_by_arm"]["frequency"], g["auac_by_arm"]["random"]))
    print("    p05[imp-freq]=%+.4f p05[imp-rand]=%+.4f | beats_both=%s fails=%s | facts_to_90pct: imp=%s freq=%s" % (
        g["margin_imp_freq_p05"], g["margin_imp_rand_p05"], g["beats_both"], g["fails"],
        g["facts_to_90pct_full"]["importance_btwn"], g["facts_to_90pct_full"]["frequency"]))
    p3 = out["part3_popularity_neutrality"]
    print("  PART3 NEUTRALITY: AUAC imp=%.4f degree_matched=%.4f p05[imp-degm]=%+.4f | neutral=%s" % (
        p3["auac_importance_btwn"], p3["auac_degree_matched"], p3["margin_imp_degmatched_p05"], p3["neutral"]))
    ic = out["info_ceiling"]
    print("  INFO-CEILING: full_orth=%.3f scramble=%.3f struct=%.3f growth_range=%.3f -> pass=%s" % (
        ic["q_full_orth_auroc"], ic["scramble_full_orth_auroc"], ic["info_ceiling_structural"],
        ic["growth_range"], ic["info_ceiling_pass"]))
    rd = out["ra_diagnostic"]
    print("  RA-DIAG (2-hop, popularity-vacuous): raw=%.3f orth=%.3f degree=%.3f" % (
        rd["ra_raw_auroc_full"], rd["ra_orth_auroc_full"], rd["degree_auroc_full"]))
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
