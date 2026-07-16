"""Substrate-integrated multi-source memory-assimilation arena + ingest gate.

First substantial build of the foundation-endgame. EXTENDS the validated toy
(experiments/toy_multisource_arena_validity_2026-07-16.py, commit a0e918812) to
substrate scale + the 4-axis signal set. Modular-by-design: swappable signal
functions (SIGNAL_FUNCS registry) and swappable gate variants (GATE_FUNCS
registry) so improving one is a ONE-FUNCTION change without touching the arena.

Implements notes/research_multisource_memory_assimilation_arena_2026-07-16.md
"Part 5 -- Arena design translation", with the 4th axis (importance) from
notes/research_surprise_decomposition_unexpectedness_vs_importance_2026-07-16.md
and the PAIRWISE schema-fit from
notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md (Tier A,
Resource-Allocation index -- cheapest, near-zero build; SR/PPR resolvent left as
a pluggable slot). The gate route form follows
notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md.

FOUR genuinely-separate generative processes (the decorrelation precondition):
  1. temporal arrival stream (Markov topics)     -> unexpectedness (online PE)
  2. schema similarity graph (disjoint seed)      -> schema_fit (pairwise RA)
  3. source population + hidden dependence graph   -> recurrence (copy-corrected)
  4. consequence/dependency graph (independent)    -> importance (downstream-reach)
A hidden truth generator combines FOUR independent latents (one per process) via
a noisy sigmoid, so no single signal (or corroboration count) determines truth by
construction; ground truth is HELD SEPARATE from every signal.

Staging (report BOTH, in order):
  A) generator self-tests (reuse toy self-tests verbatim + graph/centrality ones)
  B) ARENA-VALIDITY precondition at scale FIRST -- pairwise |r|, conditional-MI,
     copying stress-test. The arena must PASS its own validity before any gate
     result is trusted.
  C) only if arena-valid: GATE BASELINE -- does the 4-axis route beat the best
     single-signal on held-out within-cell ground-truth recovery.

Pure-Python (numpy only). No substrate atoms persisted, no torch, no queue, no
origin push. Runs inline in seconds. Multi-seed (discriminator = accuracy race).

Run:
  python experiments/exp_multisource_arena_v1.py --self-test
  python experiments/exp_multisource_arena_v1.py --profile smoke
  python experiments/exp_multisource_arena_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (subset applicable to a numpy design/validity cell):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - no bare except; no hash()-derived seeds; sorted(set()) ordering only
# - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
# - start-marker + crash-diagnostic written; per-seed heartbeat
# - arms_differ: route vs weighted_sum vs best_single decisions hash-checked distinct
# - all reported numbers are MEASURED@ this run's metrics.json unless tagged else
# - baseline-in-band: best_single balanced-acc checked in (0.05, 0.95)

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "multisource_arena_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_v1")


# ============================================================================
# Config -- ALL knobs here, nothing hardcoded downstream.
# ============================================================================
class ArenaConfig:
    """Parametric arena generator config. profile in {smoke, full}."""

    def __init__(self, profile="full", seed=11):
        self.profile = profile
        self.seed = int(seed)
        # -- scale --
        if profile == "full":
            self.n_claims = 1600
            self.n_schema_entities = 320
            self.n_communities = 8
            self.conseq_edge_p = 0.020   # consequence-graph directed edge prob
        else:  # smoke
            self.n_claims = 480
            self.n_schema_entities = 120
            self.n_communities = 4
            self.conseq_edge_p = 0.030
        # schema-graph density is set by TARGET degrees (scale-robust): the
        # intra/inter edge probabilities are derived from these in
        # _build_schema_graph so RA-index has spread at any n_schema_entities.
        self.target_intra_degree = 8.0   # expected within-community degree
        self.target_inter_degree = 1.5   # expected cross-community degree
        # fraction of claims whose tail is sampled from the head's community
        # (schema-fitting candidates); the rest are cross-community (schema-
        # violating) -> gives the explicit schema-fit-vs-violating eval axis.
        self.claim_intra_frac = 0.55
        # -- sources (process 3) --
        self.n_sources = 6
        self.reliabilities = np.array([0.92, 0.88, 0.80, 0.72, 0.62, 0.55])
        # hidden dependence: sources 4,5 are noisy COPIES of source 0.
        self.copy_parent = np.array([-1, -1, -1, -1, 0, 0])
        self.copy_fidelity = 0.85
        self.assert_prob = 0.55
        self.specialization = 0.6    # <= 0.6 per spec
        # -- temporal arrival (process 1) --
        self.n_topics = 8 if profile == "full" else 6
        self.self_transition = 0.70  # topic persistence -> autocorrelation
        # -- conflict injection --
        self.conflict_frac = 0.15    # fraction of claims forced to mixed testimony
        # -- consequence graph (process 4) --
        self.conseq_reach_k = 2      # hops for downstream-reach
        # -- exogenous query-relevance layer for importance: default OFF --
        self.query_relevance_on = False
        self.query_relevance_weight = 0.0
        # -- hidden truth generator: one weight per INDEPENDENT latent --
        self.w_bias = 0.0
        self.w_schema = 1.3
        self.w_source = 1.5
        self.w_temporal = 0.9
        self.w_importance = 1.1
        # -- copy detector --
        self.dep_excess_thresh = 0.30
        self.dep_min_overlap = 15
        # -- copying stress-test --
        self.stress_pairs = 60
        self.stress_n = 4
        # -- gate / eval --
        self.test_frac = 0.5         # held-out fraction for gate baseline
        self.cell_bins = 2           # levels per signal for within-cell strata
        self.min_cell = 10           # min test claims per stratification cell


# ============================================================================
# small numeric helpers (numpy only)
# ============================================================================
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def zscore(x):
    x = np.asarray(x, dtype=float)
    s = x.std()
    if s < 1e-12:
        return x - x.mean()
    return (x - x.mean()) / s


def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if x.std() < 1e-12 or y.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


# ============================================================================
# Generative model -- FOUR independent processes
# ============================================================================
def _build_schema_graph(cfg, rng):
    """Process 2: undirected schema similarity graph from a DISJOINT seed corpus.
    Block/community structure so pairwise multi-path (RA) counts have spread.
    Returns adjacency as list-of-sets and degree array."""
    n = cfg.n_schema_entities
    comm = rng.integers(cfg.n_communities, size=n)
    adj = [set() for _ in range(n)]
    # derive edge probabilities from TARGET degrees (scale-robust spread).
    comm_size = max(2.0, n / cfg.n_communities)
    intra_p = min(0.9, cfg.target_intra_degree / (comm_size - 1))
    inter_p = min(0.5, cfg.target_inter_degree / max(n - comm_size, 1))
    # sample undirected edges by community membership
    iu, ju = np.triu_indices(n, k=1)
    same = comm[iu] == comm[ju]
    p = np.where(same, intra_p, inter_p)
    draw = rng.random(len(iu)) < p
    for a, b in zip(iu[draw], ju[draw]):
        adj[a].add(int(b))
        adj[b].add(int(a))
    deg = np.array([len(adj[i]) for i in range(n)], dtype=float)
    return adj, deg, comm


def _ra_pairwise(adj, deg, h, t):
    """Resource-Allocation index: sum over common neighbours z of 1/deg(z).
    Pair-specific, multi-path, hub-down-weighted (schema-fit-upgrade Tier A)."""
    nh, nt = adj[h], adj[t]
    if len(nh) > len(nt):
        nh, nt = nt, nh
    s = 0.0
    for z in nh:
        if z in nt and deg[z] > 0:
            s += 1.0 / deg[z]
    return s


def _build_consequence_graph(cfg, rng):
    """Process 4: INDEPENDENT directed consequence/dependency graph over the same
    entities, generated from separate randomness (no shared degree structure with
    the schema graph). downstream-reach(v) = fraction of nodes reachable from v
    within conseq_reach_k hops = 'how much depends on v' = value-of-information."""
    n = cfg.n_schema_entities
    # directed edges i->j (i != j), independent draws
    out_adj = [[] for _ in range(n)]
    src, dst = np.where(rng.random((n, n)) < cfg.conseq_edge_p)
    for i, j in zip(src, dst):
        if i != j:
            out_adj[i].append(int(j))
    # k-hop forward reach set size (BFS to depth k)
    reach = np.zeros(n, dtype=float)
    for v in range(n):
        seen = {v}
        frontier = [v]
        for _ in range(cfg.conseq_reach_k):
            nxt = []
            for u in frontier:
                for w in out_adj[u]:
                    if w not in seen:
                        seen.add(w)
                        nxt.append(w)
            frontier = nxt
            if not frontier:
                break
        reach[v] = (len(seen) - 1) / max(n - 1, 1)
    return out_adj, reach


def build_arena(cfg, rng):
    """Build the arena. Returns a dict of arrays. FOUR independent generative
    processes drive the four signals; a hidden truth generator combines four
    independent latents so each signal carries partial (independent) truth info
    and ground truth is not derivable from any single signal by construction."""
    K = cfg.n_claims
    S = cfg.n_sources
    n = cfg.n_schema_entities

    # --- Process 2: schema graph (static structural overlap) ---
    schema_adj, schema_deg, comm = _build_schema_graph(cfg, rng)

    # claims are candidate (h, t) entity pairs, drawn INDEPENDENTLY of arrival +
    # source structure. h != t. A claim_intra_frac fraction have the tail sampled
    # from the head's community (schema-fitting); the rest cross-community.
    by_comm = [np.where(comm == c)[0] for c in range(cfg.n_communities)]
    heads = rng.integers(n, size=K)
    tails = np.empty(K, dtype=int)
    want_intra = rng.random(K) < cfg.claim_intra_frac
    for k in range(K):
        h = int(heads[k])
        if want_intra[k] and len(by_comm[comm[h]]) > 1:
            pool = by_comm[comm[h]]
        else:
            pool = np.arange(n)
        t = int(rng.choice(pool))
        while t == h:
            t = int(rng.choice(pool))
        tails[k] = t
    schema_fit_raw = np.array([_ra_pairwise(schema_adj, schema_deg, int(heads[k]),
                                             int(tails[k])) for k in range(K)])
    L_schema = zscore(schema_fit_raw)

    # --- Process 4: consequence graph (importance / downstream-reach) ---
    conseq_adj, conseq_reach = _build_consequence_graph(cfg, rng)
    importance_raw = 0.5 * (conseq_reach[heads] + conseq_reach[tails])
    L_importance = zscore(importance_raw)

    # --- Process 1: temporal arrival stream (predictive surprise) ---
    T = np.full((cfg.n_topics, cfg.n_topics),
                (1.0 - cfg.self_transition) / (cfg.n_topics - 1))
    np.fill_diagonal(T, cfg.self_transition)
    topics = np.empty(K, dtype=int)
    topics[0] = rng.integers(cfg.n_topics)
    continued = np.zeros(K, dtype=bool)
    for tt in range(1, K):
        topics[tt] = rng.choice(cfg.n_topics, p=T[topics[tt - 1]])
        continued[tt] = (topics[tt] == topics[tt - 1])
    L_temporal = zscore(continued.astype(float))

    # --- Process 3: source population + hidden dependence (corroboration) ---
    src_pref = rng.normal(size=(S, n))  # per-source scope over entities
    # source affinity to a claim = mean of its scope on the two entities
    src_affinity = 0.5 * (src_pref[:, heads] + src_pref[:, tails]).T  # (K,S)
    L_source = zscore(rng.normal(size=K))  # independent genuine-support latent

    reports = np.zeros((K, S), dtype=bool)
    for s in range(S):
        if cfg.copy_parent[s] >= 0:
            continue
        logit = (np.log(cfg.assert_prob / (1 - cfg.assert_prob))
                 + cfg.specialization * zscore(src_affinity[:, s])
                 + 0.8 * L_source)
        reports[:, s] = rng.random(K) < sigmoid(logit)
    for s in range(S):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        follow = reports[:, par] & (rng.random(K) < cfg.copy_fidelity)
        extra = (~reports[:, par]) & (rng.random(K) < 0.10)
        reports[:, s] = follow | extra

    # --- hidden truth generator: FOUR independent latents ---
    truth_logit = (cfg.w_bias + cfg.w_schema * L_schema + cfg.w_source * L_source
                   + cfg.w_temporal * L_temporal + cfg.w_importance * L_importance)
    p_true = sigmoid(truth_logit)
    truth = rng.random(K) < p_true

    # --- source readings (value each reporting source asserts) ---
    value = np.full((K, S), -1, dtype=int)
    for s in range(S):
        if cfg.copy_parent[s] >= 0:
            continue
        mask = reports[:, s]
        correct = rng.random(K) < cfg.reliabilities[s]
        v = np.where(correct, truth.astype(int), 1 - truth.astype(int))
        value[mask, s] = v[mask]
    for s in range(S):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        mask = reports[:, s]
        echo = (rng.random(K) < cfg.copy_fidelity) & (value[:, par] >= 0)
        own_correct = rng.random(K) < cfg.reliabilities[s]
        own_v = np.where(own_correct, truth.astype(int), 1 - truth.astype(int))
        v = np.where(echo, value[:, par], own_v)
        value[mask, s] = v[mask]

    # --- conflict injection: force a fraction of claims to mixed testimony.
    # Restricted to INDEPENDENT NON-PARENT reporters: independent (so testimony
    # is genuine) and not a copy-parent (flipping a parent's value AFTER copies
    # echoed it would spuriously break the copy-dependence the detector relies
    # on). ---
    parents = set(int(p) for p in cfg.copy_parent if p >= 0)
    indep_srcs = np.array([s for s in range(S)
                           if cfg.copy_parent[s] < 0 and s not in parents])
    conflict_idx = rng.choice(K, size=int(cfg.conflict_frac * K), replace=False)
    for k in conflict_idx:
        rep = [s for s in indep_srcs if reports[k, s]]
        if len(rep) >= 2:
            value[k, rep[0]] = 1
            value[k, rep[1]] = 0
    # realized conflict rate = claims where reporters disagree
    disagree = np.zeros(K, dtype=bool)
    for k in range(K):
        vals = value[k][value[k] >= 0]
        if len(vals) >= 2 and vals.min() != vals.max():
            disagree[k] = True

    asserts_true = (value == 1)

    return dict(
        cfg=cfg, schema_adj=schema_adj, schema_deg=schema_deg, comm=comm,
        heads=heads, tails=tails, schema_fit_raw=schema_fit_raw, L_schema=L_schema,
        conseq_reach=conseq_reach, importance_raw=importance_raw,
        L_importance=L_importance, topics=topics, continued=continued,
        L_temporal=L_temporal, reports=reports, value=value,
        asserts_true=asserts_true, L_source=L_source, truth=truth, p_true=p_true,
        conflict_idx=conflict_idx, disagree=disagree,
    )


# ============================================================================
# Copy detector (truth-discovery style; uses NO ground-truth cluster labels)
# ============================================================================
def detect_dependence(value, reliabilities, cfg):
    S = value.shape[1]
    parent = list(range(S))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        parent[find(a)] = find(b)

    for i in range(S):
        for j in range(i + 1, S):
            both = (value[:, i] >= 0) & (value[:, j] >= 0)
            if both.sum() < cfg.dep_min_overlap:
                continue
            agree = (value[both, i] == value[both, j]).mean()
            ri, rj = reliabilities[i], reliabilities[j]
            exp_agree = ri * rj + (1 - ri) * (1 - rj)
            if (agree - exp_agree) > cfg.dep_excess_thresh:
                union(i, j)
    return np.array([find(s) for s in range(S)])


# ============================================================================
# FOUR pluggable signal functions. Each takes the arena dict + returns a
# per-claim raw score (higher = more of that property). Swap one = change one.
# ============================================================================
def signal_unexpectedness(arena):
    """Online / schema-conditioned prediction error. surprise_t =
    -log P(topic_t | topic_{t-1}) under counts seen SO FAR (causal). Local (the
    arena's forward model), NOT a global anomaly rank -- per the consolidation
    note's local/schema-conditioned requirement. Returned as a per-claim score
    where HIGHER = MORE surprising."""
    topics = arena["topics"]
    n_topics = arena["cfg"].n_topics
    K = len(topics)
    counts = np.zeros((n_topics, n_topics)) + 1.0
    surprise = np.zeros(K)
    surprise[0] = np.log(n_topics)
    for tt in range(1, K):
        prev, cur = topics[tt - 1], topics[tt]
        p = counts[prev, cur] / counts[prev].sum()
        surprise[tt] = -np.log(p)
        counts[prev, cur] += 1.0
    return surprise


def signal_schema_fit(arena):
    """PAIRWISE Resource-Allocation index on the pre-built schema graph
    (schema-fit-upgrade Tier A). Pair-specific + multi-path + hub-down-weighted;
    NOT a node-aggregate percentile. (SR/PPR resolvent = Tier B pluggable slot.)"""
    return arena["schema_fit_raw"].copy()


def signal_recurrence(arena, clusters=None):
    """COPY-CORRECTED corroboration: number of distinct DETECTED independent
    source clusters among asserting-true sources (dependence-corrected, not a
    naive count). Returns (corrected, naive)."""
    cfg = arena["cfg"]
    if clusters is None:
        clusters = detect_dependence(arena["value"], cfg.reliabilities, cfg)
    asserts_true = arena["asserts_true"]
    K = asserts_true.shape[0]
    naive = asserts_true.sum(axis=1).astype(float)
    corrected = np.zeros(K)
    for k in range(K):
        srcs = np.where(asserts_true[k])[0]
        if len(srcs):
            corrected[k] = len(set(int(clusters[s]) for s in srcs))
    return corrected, naive


def signal_importance(arena):
    """Intrinsic downstream-reach (graph centrality on the INDEPENDENT
    consequence graph) = value-of-information proxy: 'does this matter to other
    things'. Optional exogenous query-relevance layer (default OFF / intrinsic
    first) is a pluggable slot."""
    cfg = arena["cfg"]
    imp = arena["importance_raw"].copy()
    if cfg.query_relevance_on and cfg.query_relevance_weight > 0:
        # pluggable exogenous slot: overlap with a designer query vector.
        # default OFF; stub kept intentionally minimal.
        q = zscore(arena["conseq_reach"][arena["heads"]])
        imp = imp + cfg.query_relevance_weight * q
    return imp


SIGNAL_FUNCS = {
    "unexpectedness": signal_unexpectedness,
    "schema_fit": signal_schema_fit,
    "recurrence": signal_recurrence,
    "importance": signal_importance,
}


def compute_all_signals(arena, clusters):
    """Return dict of the 4 raw signals (all higher=more), plus naive corrob."""
    surprise = signal_unexpectedness(arena)
    schema = signal_schema_fit(arena)
    corrected, naive = signal_recurrence(arena, clusters)
    importance = signal_importance(arena)
    return {
        "unexpectedness": surprise,
        "schema_fit": schema,
        "recurrence": corrected,
        "importance": importance,
        "_naive_corrob": naive,
    }


# ============================================================================
# Validity harness (reuse toy's estimators; generalized to 4 signals)
# ============================================================================
def conditional_mi(sig, target, conditioners, sig_bins=3, cond_bins=2):
    """I(sig; target | conditioners). Bin conditioners into a joint grid, average
    binary-target MI within each cell. target binary. Positive => sig retains
    predictive power after conditioning on the other signals."""
    sig = np.asarray(sig, float)
    target = np.asarray(target, int)

    def binize(v, nb):
        v = np.asarray(v, float)
        qs = np.quantile(v, np.linspace(0, 1, nb + 1)[1:-1])
        return np.digitize(v, qs)

    bs = binize(sig, sig_bins)
    cbins = [binize(c, cond_bins) for c in conditioners]
    total = len(sig)
    # enumerate joint conditioner cells
    from itertools import product
    mi = 0.0
    for combo in product(*[range(cond_bins) for _ in conditioners]):
        cell = np.ones(total, dtype=bool)
        for cb, cv in zip(cbins, combo):
            cell &= (cb == cv)
        ncell = int(cell.sum())
        if ncell < 8:
            continue
        w = ncell / total
        s_cell, t_cell = bs[cell], target[cell]
        cell_mi = 0.0
        for sv in np.unique(s_cell):
            for tv in (0, 1):
                p_st = ((s_cell == sv) & (t_cell == tv)).mean()
                if p_st <= 0:
                    continue
                p_s = (s_cell == sv).mean()
                p_t = (t_cell == tv).mean()
                if p_s <= 0 or p_t <= 0:
                    continue
                cell_mi += p_st * np.log(p_st / (p_s * p_t))
        mi += w * cell_mi
    return float(mi)


def perm_pvalue_meandiff(a, b, rng, n_perm=5000):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    obs = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    na = len(a)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        if (pooled[:na].mean() - pooled[na:].mean()) >= obs:
            count += 1
    return obs, (count + 1) / (n_perm + 1)


def copying_stress_test(cfg, rng, clusters):
    """Matched claims: identical raw source count N, backed by N INDEPENDENT
    sources vs N COPIES-of-one. corrected must score independent > copied; naive
    must FAIL to separate (equal by construction)."""
    N = cfg.stress_n
    indep_sources = [s for s in range(cfg.n_sources) if cfg.copy_parent[s] < 0]
    naive_ind, naive_cop, corr_ind, corr_cop = [], [], [], []
    for _ in range(cfg.stress_pairs):
        chosen = rng.choice(indep_sources, size=min(N, len(indep_sources)),
                            replace=False)
        naive_ind.append(len(chosen))
        corr_ind.append(len(set(int(clusters[s]) for s in chosen)))
        naive_cop.append(N)
        corr_cop.append(1)
    corr_ind = np.array(corr_ind, float)
    corr_cop = np.array(corr_cop, float)
    _, p_corr = perm_pvalue_meandiff(corr_ind.copy(), corr_cop.copy(), rng)
    ratio = corr_ind.mean() / max(corr_cop.mean(), 1e-9)
    return dict(corr_ind_mean=float(corr_ind.mean()),
                corr_cop_mean=float(corr_cop.mean()),
                corr_ratio=float(ratio), corr_pvalue=float(p_corr),
                naive_separation=float(abs(np.mean(naive_ind) - np.mean(naive_cop))))


# ============================================================================
# GATE (separate module) -- route/weighted_sum variants + best-single baseline.
# Each takes standardized train signals + train truth, returns a fitted
# predictor callable(test_signals)->binary decision.
# ============================================================================
def _balanced_acc(pred, truth):
    truth = np.asarray(truth, int)
    pred = np.asarray(pred, int)
    accs = []
    for c in (0, 1):
        m = truth == c
        if m.sum() == 0:
            continue
        accs.append((pred[m] == c).mean())
    return float(np.mean(accs)) if accs else 0.5


def fit_weighted_sum(Xtr, ytr, l2=1.0, steps=400, lr=0.3):
    """Logistic regression (weighted_sum gate variant). numpy GD, deterministic."""
    n, d = Xtr.shape
    w = np.zeros(d)
    b = 0.0
    y = ytr.astype(float)
    for _ in range(steps):
        z = Xtr @ w + b
        p = sigmoid(z)
        gw = Xtr.T @ (p - y) / n + l2 * w / n
        gb = (p - y).mean()
        w -= lr * gw
        b -= lr * gb

    def predict(Xte):
        return (sigmoid(Xte @ w + b) >= 0.5).astype(int)
    return predict, dict(w=w.tolist(), b=float(b))


def fit_route(Xtr, ytr, cols, grid=(0.35, 0.5, 0.65)):
    """Brain-faithful ROUTE gate (cascade), thresholds grid-searched on TRAIN.
    cols maps signal name -> column index. Cascade per the consolidation note:
      1. reliability gate: low recurrence AND low importance -> DISCARD (0)
         one-shot salience bypass: very-high importance -> keep (1)
      2. route on schema-fit: high schema_fit + adequate corroboration -> 1 (fast)
         low schema_fit but expected + corroborated -> 1 (slow) else 0
    Signals are first ORIENTED truth-positive using train sign (so 'high' always
    means 'more evidence to assimilate' -- the arena's surprise is truth-NEGATIVE,
    which a naive cascade would route backwards). Thresholds are PERCENTILES fit
    on train signal distributions."""
    su, sf = cols["unexpectedness"], cols["schema_fit"]
    rc, im = cols["recurrence"], cols["importance"]
    # orient each column truth-positive on train (sign of correlation with ytr)
    sign = np.ones(Xtr.shape[1])
    yv = ytr.astype(float)
    for c in range(Xtr.shape[1]):
        if pearson(Xtr[:, c], yv) < 0:
            sign[c] = -1.0
    Xtr = Xtr * sign
    qs = {}
    for c in (su, sf, rc, im):
        qs[c] = {g: np.quantile(Xtr[:, c], g) for g in grid}

    def make_decider(rel_th, sal_th, sf_th, su_th):
        def decide(X):
            X = X * sign  # orient truth-positive (same train-fit signs)
            rel = X[:, rc]
            imp = X[:, im]
            sf_v = X[:, sf]
            su_v = X[:, su]
            dec = np.zeros(len(X), dtype=int)
            # salience one-shot bypass
            bypass = imp >= qs[im][sal_th]
            # reliability gate: pass if corroboration adequate OR bypass
            passed = (rel >= qs[rc][rel_th]) | bypass
            # route on schema-fit among passed
            fast = passed & (sf_v >= qs[sf][sf_th])
            slow = passed & (~fast) & (su_v >= qs[su][su_th])
            dec[fast | slow | bypass] = 1
            return dec
        return decide

    best = None
    best_acc = -1.0
    for rel_th in grid:
        for sal_th in grid:
            for sf_th in grid:
                for su_th in grid:
                    dec = make_decider(rel_th, sal_th, sf_th, su_th)
                    acc = _balanced_acc(dec(Xtr), ytr)
                    if acc > best_acc:
                        best_acc = acc
                        best = (rel_th, sal_th, sf_th, su_th)
    decider = make_decider(*best)
    return decider, dict(thresholds=dict(rel=best[0], sal=best[1],
                                         sf=best[2], su=best[3]),
                         train_bal_acc=float(best_acc))


def fit_best_single(Xtr, ytr, cols, grid_q=np.linspace(0.15, 0.85, 15)):
    """Best-single-signal baseline: per signal find best train threshold
    (and polarity), pick the signal with best TRAIN balanced-acc."""
    best = None
    best_acc = -1.0
    for name, c in cols.items():
        thr_cand = np.quantile(Xtr[:, c], grid_q)
        for thr in thr_cand:
            for pol in (1, -1):
                pred = ((Xtr[:, c] >= thr).astype(int) if pol == 1
                        else (Xtr[:, c] < thr).astype(int))
                acc = _balanced_acc(pred, ytr)
                if acc > best_acc:
                    best_acc = acc
                    best = (name, c, float(thr), pol)

    def predict(Xte):
        _, c, thr, pol = best
        return ((Xte[:, c] >= thr).astype(int) if pol == 1
                else (Xte[:, c] < thr).astype(int))
    return predict, dict(signal=best[0], thr=best[2], polarity=best[3],
                         train_bal_acc=float(best_acc))


def fit_single_signal(Xtr, ytr, c, grid_q=np.linspace(0.15, 0.85, 15)):
    """Best train threshold+polarity for ONE signal column -> predictor."""
    best = None
    best_acc = -1.0
    for thr in np.quantile(Xtr[:, c], grid_q):
        for pol in (1, -1):
            pred = ((Xtr[:, c] >= thr).astype(int) if pol == 1
                    else (Xtr[:, c] < thr).astype(int))
            acc = _balanced_acc(pred, ytr)
            if acc > best_acc:
                best_acc, best = acc, (float(thr), pol)

    def predict(Xte):
        thr, pol = best
        return ((Xte[:, c] >= thr).astype(int) if pol == 1
                else (Xte[:, c] < thr).astype(int))
    return predict


GATE_FUNCS = {"route": fit_route, "weighted_sum": fit_weighted_sum}


# ============================================================================
# within-cell ground-truth recovery (stratified; no marginal-correlation credit)
# ============================================================================
def within_cell_bal_acc(pred, truth, strat_signals, cfg, thresholds,
                        strat_names=("unexpectedness", "schema_fit", "recurrence")):
    """Stratify test claims into cells by binning the CORE note-signals
    (surprise x schema-fit x corroboration = 8 cells by default, per the arena
    note's grid) at TRAIN medians; within each populated cell compute BALANCED
    accuracy of pred vs truth; weight by cell size. Balanced-acc handles truth
    imbalance without subsampling. Stratifying on the 3 core signals (not all 4)
    leaves importance -- the added 4th axis -- room to add within-cell value,
    which is exactly the surprise-decomposition note's open question."""
    from itertools import product
    n = len(pred)
    bins = []
    for name in strat_names:
        bins.append((strat_signals[name] >= thresholds[name]).astype(int))
    bins = np.array(bins)
    tot_w = 0.0
    acc_sum = 0.0
    n_cells = 0
    for combo in product((0, 1), repeat=len(strat_names)):
        cell = np.ones(n, dtype=bool)
        for row, cv in enumerate(combo):
            cell &= (bins[row] == cv)
        ncell = int(cell.sum())
        if ncell < cfg.min_cell:
            continue
        tcell = truth[cell]
        if tcell.min() == tcell.max():
            continue  # single-class cell: balanced-acc undefined
        a = _balanced_acc(pred[cell], tcell)
        acc_sum += ncell * a
        tot_w += ncell
        n_cells += 1
    if tot_w == 0:
        return 0.5, 0
    return acc_sum / tot_w, n_cells


# ============================================================================
# Generator self-tests (staging A) -- reuse toy self-tests + graph/centrality
# ============================================================================
def run_self_tests(arena):
    cfg = arena["cfg"]
    fails, notes = [], []

    # ST1: higher-reliability INDEPENDENT sources emit more true asserts.
    indep = [s for s in range(cfg.n_sources) if cfg.copy_parent[s] < 0]
    acc, rel = [], []
    for s in indep:
        mask = arena["asserts_true"][:, s]
        if mask.sum() < 5:
            continue
        acc.append(arena["truth"][mask].mean())
        rel.append(cfg.reliabilities[s])
    r_rel_acc = pearson(np.array(rel), np.array(acc))
    notes.append("ST1 reliability-vs-assert-accuracy r=%.3f" % r_rel_acc)
    if r_rel_acc < 0.5:
        fails.append("ST1: higher-reliability sources do NOT emit more true claims")

    # ST2: copies share parent idiosyncratic errors.
    for s in range(cfg.n_sources):
        par = cfg.copy_parent[s]
        if par < 0:
            continue
        vp, vc = arena["value"][:, par], arena["value"][:, s]
        both = (vp >= 0) & (vc >= 0)
        par_err = both & (vp != arena["truth"].astype(int))
        if par_err.sum() < 5:
            fails.append("ST2: too few parent errors to test copy %d" % s)
            continue
        share = (vc[par_err] == vp[par_err]).mean()
        notes.append("ST2 copy%d-of-%d shares-parent-error=%.2f (n=%d)"
                     % (s, par, share, int(par_err.sum())))
        if share < 0.5:
            fails.append("ST2: copy %d does not share parent errors" % s)

    # ST3: copy detector recovers hidden dependence.
    clusters = detect_dependence(arena["value"], cfg.reliabilities, cfg)
    same_par = all(clusters[s] == clusters[cfg.copy_parent[s]]
                   for s in range(cfg.n_sources) if cfg.copy_parent[s] >= 0)
    indep_sep = all(clusters[i] != clusters[0] for i in (1, 2, 3))
    notes.append("ST3 clusters=%s copies-merged=%s indep-separate=%s"
                 % (clusters.tolist(), same_par, indep_sep))
    if not same_par:
        fails.append("ST3: copy detector failed to merge copies with parent")
    if not indep_sep:
        fails.append("ST3: copy detector wrongly merged independent sources")

    # ST4 (NEW): schema graph gives PAIRWISE RA a non-degenerate spread.
    sf = arena["schema_fit_raw"]
    frac_nonzero = float((sf > 0).mean())
    notes.append("ST4 schema RA-index: frac_nonzero=%.2f std=%.4f distinct=%d"
                 % (frac_nonzero, sf.std(), len(np.unique(sf))))
    if frac_nonzero < 0.30 or sf.std() < 1e-6:
        fails.append("ST4: schema RA-index degenerate (too sparse/no spread)")

    # ST5 (NEW): consequence graph is INDEPENDENT of schema graph -> importance
    # decorrelated from schema_fit at the RAW-signal level.
    r_si = pearson(arena["schema_fit_raw"], arena["importance_raw"])
    notes.append("ST5 schema-vs-importance RAW r=%.3f (must be |r|<0.3)" % r_si)
    if abs(r_si) > 0.3:
        fails.append("ST5: importance not independent of schema_fit (r=%.3f)" % r_si)

    # ST6 (NEW): conflict injection produced real mixed testimony.
    dis = float(arena["disagree"].mean())
    notes.append("ST6 realized disagreement rate=%.2f" % dis)
    if dis < 0.05:
        fails.append("ST6: conflict injection did not produce disagreement")

    # ST7: truth not derivable from a single signal (base-rate not degenerate).
    br = float(arena["truth"].mean())
    notes.append("ST7 truth base-rate=%.2f" % br)
    if br < 0.2 or br > 0.8:
        fails.append("ST7: truth base-rate degenerate (%.2f)" % br)

    return fails, notes, clusters


# ============================================================================
# staging B + C per seed
# ============================================================================
def run_one_seed(cfg, rng_stream):
    rng = np.random.default_rng(rng_stream)
    arena = build_arena(cfg, rng)
    fails, notes, clusters = run_self_tests(arena)
    sig = compute_all_signals(arena, clusters)
    truth = arena["truth"].astype(int)

    names = ["unexpectedness", "schema_fit", "recurrence", "importance"]
    # orient all signals so higher=more-of-property; for MI/gate we let the
    # fitter choose polarity. Surprise: higher=more surprising (lower truth-corr).
    raw = {n: sig[n] for n in names}

    # ---- (B) arena validity ----
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
    rvals = {f"{a}|{b}": abs(pearson(raw[a], raw[b])) for a, b in pairs}
    max_abs_r = max(rvals.values())

    # conditional MI: each signal | other three. surprise negated so "expected"
    # aligns with should-assimilate direction for the MI read.
    cmi = {}
    for n in names:
        others = [raw[o] for o in names if o != n]
        s = -raw[n] if n == "unexpectedness" else raw[n]
        cmi[n] = conditional_mi(s, truth, others)
    n_informative = int(sum(v > 1e-3 for v in cmi.values()))

    stress = copying_stress_test(cfg, rng, clusters)

    # ---- (C) gate baseline: held-out within-cell recovery ----
    K = cfg.n_claims
    idx = rng.permutation(K)
    n_test = int(cfg.test_frac * K)
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    # standardized feature matrix (z per signal on TRAIN stats)
    mu = np.array([raw[n][train_idx].mean() for n in names])
    sd = np.array([raw[n][train_idx].std() + 1e-9 for n in names])
    X = np.column_stack([raw[n] for n in names])
    Xz = (X - mu) / sd
    cols = {n: i for i, n in enumerate(names)}
    Xtr, ytr = Xz[train_idx], truth[train_idx]
    Xte, yte = Xz[test_idx], truth[test_idx]

    route_dec, route_info = fit_route(Xtr, ytr, cols)
    wsum_dec, wsum_info = fit_weighted_sum(Xtr, ytr)
    best_dec, best_info = fit_best_single(Xtr, ytr, cols)

    # stratification thresholds = TRAIN medians (in z-space) per signal
    strat_th = {n: 0.0 for n in names}  # z median ~ 0 on train after standardize
    strat_sig = {n: Xte[:, cols[n]] for n in names}

    route_pred = route_dec(Xte)
    wsum_pred = wsum_dec(Xte)
    best_pred = best_dec(Xte)

    # within-cell (stratified, primary per note) balanced-acc
    route_acc, ncell = within_cell_bal_acc(route_pred, yte, strat_sig, cfg, strat_th)
    wsum_acc, _ = within_cell_bal_acc(wsum_pred, yte, strat_sig, cfg, strat_th)
    # FAIR within-cell single-signal baseline: best over ALL 4 single signals
    # measured WITHIN-CELL (a signal that IS a stratification axis is pinned to
    # ~0.5 within-cell, so we must not fix best_single marginally -- importance,
    # the un-stratified 4th axis, is the honest within-cell single baseline).
    single_wc = {}
    for name in names:
        sp = fit_single_signal(Xtr, ytr, cols[name])(Xte)
        single_wc[name], _ = within_cell_bal_acc(sp, yte, strat_sig, cfg, strat_th)
    best_wc_name = max(single_wc, key=single_wc.get)
    best_acc = single_wc[best_wc_name]
    # marginal held-out balanced-acc (secondary; shows any multi-signal value)
    route_marg = _balanced_acc(route_pred, yte)
    wsum_marg = _balanced_acc(wsum_pred, yte)
    best_marg = _balanced_acc(best_pred, yte)

    # arms-must-differ: gate decisions distinct
    import hashlib
    def _h(a):
        return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()
    arms_differ = len({_h(route_pred), _h(wsum_pred), _h(best_pred)}) >= 2

    def rel_err_red(gate_acc, base_acc):
        e_g, e_b = 1 - gate_acc, 1 - base_acc
        return (e_b - e_g) / e_b if e_b > 1e-9 else 0.0

    return dict(
        self_test_fails=fails, self_test_notes=notes,
        truth_base_rate=float(truth.mean()),
        pairwise_abs_r=rvals, max_abs_r=float(max_abs_r),
        conditional_mi=cmi, n_informative=n_informative,
        copying=stress,
        best_single_signal=best_info["signal"],
        best_single_within_signal=best_wc_name,
        single_within_cell={k: float(v) for k, v in single_wc.items()},
        within_cell={"route": float(route_acc), "weighted_sum": float(wsum_acc),
                     "best_single": float(best_acc), "n_cells": int(ncell)},
        marginal={"route": float(route_marg), "weighted_sum": float(wsum_marg),
                  "best_single": float(best_marg)},
        rel_err_reduction={"route_vs_single": float(rel_err_red(route_acc, best_acc)),
                           "wsum_vs_single": float(rel_err_red(wsum_acc, best_acc)),
                           "route_marg_vs_single": float(rel_err_red(route_marg, best_marg)),
                           "wsum_marg_vs_single": float(rel_err_red(wsum_marg, best_marg))},
        route_thresholds=route_info["thresholds"], arms_differ=bool(arms_differ),
        n_test=int(n_test),
    )


# ============================================================================
# metrics IO + markers
# ============================================================================
def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_start_marker(expected_units, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    _atomic_write(os.path.join(OUTPUT_DIR, "_start_marker.json"), marker)


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED", "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), diag)


# ============================================================================
# main
# ============================================================================
def aggregate_and_verdict(profile, seeds, per_seed, elapsed):
    """Aggregate multi-seed results into arena-validity + gate-baseline verdict."""
    names = ["unexpectedness", "schema_fit", "recurrence", "importance"]
    # arena validity (aggregate)
    max_r_seeds = [s["max_abs_r"] for s in per_seed]
    n_info_seeds = [s["n_informative"] for s in per_seed]
    ratio_seeds = [s["copying"]["corr_ratio"] for s in per_seed]
    pval_seeds = [s["copying"]["corr_pvalue"] for s in per_seed]
    # mean pairwise |r| per pair
    pair_keys = list(per_seed[0]["pairwise_abs_r"].keys())
    mean_pair_r = {k: float(np.mean([s["pairwise_abs_r"][k] for s in per_seed]))
                   for k in pair_keys}
    mean_cmi = {n: float(np.mean([s["conditional_mi"][n] for s in per_seed]))
                for n in names}

    max_abs_r = float(np.max(max_r_seeds))
    mean_ratio = float(np.mean(ratio_seeds))
    worst_p = float(np.max(pval_seeds))
    min_info = int(np.min(n_info_seeds))

    # arena-validity bands (pre-registered):
    #  HARD-PASS: all pairwise |r| < 0.3 AND copying >=1.5x p<0.05 AND >=3/4 cMI
    #  HARD-FAIL: any |r| > 0.6 OR copying at chance (ratio<1.05 or p>=0.05)
    #  re-collapse concern band 0.3-0.6 -> MIDDLE
    arena_hard_pass = (max_abs_r < 0.30 and mean_ratio >= 1.5 and worst_p < 0.05
                       and min_info >= 3)
    arena_hard_fail = (max_abs_r > 0.60 or mean_ratio < 1.05 or worst_p >= 0.05)
    arena_middle = not (arena_hard_pass or arena_hard_fail)
    if arena_hard_pass:
        arena_verdict = "ARENA_VALID"
    elif arena_hard_fail:
        arena_verdict = "ARENA_INVALID"
    else:
        arena_verdict = "ARENA_MIDDLE"

    # gate baseline (aggregate) -- only trusted if arena valid or middle
    def _m(metric, key):
        return float(np.mean([s[metric][key] for s in per_seed]))
    route_acc, wsum_acc, best_acc = (_m("within_cell", "route"),
                                     _m("within_cell", "weighted_sum"),
                                     _m("within_cell", "best_single"))
    route_marg, wsum_marg, best_marg = (_m("marginal", "route"),
                                        _m("marginal", "weighted_sum"),
                                        _m("marginal", "best_single"))
    route_rr = _m("rel_err_reduction", "route_vs_single")
    wsum_rr = _m("rel_err_reduction", "wsum_vs_single")
    route_marg_rr = _m("rel_err_reduction", "route_marg_vs_single")
    wsum_marg_rr = _m("rel_err_reduction", "wsum_marg_vs_single")
    baseline_in_band = 0.05 < best_acc < 0.95 and 0.05 < best_marg < 0.95
    arms_differ_all = all(s["arms_differ"] for s in per_seed)

    # gate bands. PRIMARY (contract) = 4-axis ROUTE beats best-single by >=15%
    # rel error reduction on within-cell recovery. We ALSO report the logistic
    # (weighted_sum) and the MARGINAL held-out metric to localize whether any
    # multi-signal value exists vs the route form specifically underperforming.
    if not (arena_hard_pass or arena_middle):
        gate_verdict = "GATE_NOT_TRUSTED_ARENA_INVALID"
    elif route_rr >= 0.15 and baseline_in_band and arms_differ_all:
        gate_verdict = "GATE_ROUTE_WINS"
    elif wsum_rr >= 0.15 and baseline_in_band:
        gate_verdict = "GATE_LOGISTIC_WINS_ROUTE_UNCALIBRATED"
    elif max(wsum_marg_rr, route_marg_rr) >= 0.15 and baseline_in_band:
        gate_verdict = "GATE_MARGINAL_MULTISIGNAL_ONLY"
    elif max(route_rr, wsum_rr, route_marg_rr, wsum_marg_rr) <= 0.0:
        gate_verdict = "GATE_NO_MULTISIGNAL_VALUE"
    else:
        gate_verdict = "GATE_MIDDLE"

    # combined top-level verdict
    if arena_verdict == "ARENA_INVALID":
        verdict = "HARD_FAIL_ARENA_INVALID"
    elif arena_verdict == "ARENA_VALID" and gate_verdict == "GATE_ROUTE_WINS":
        verdict = "HARD_PASS"
    elif arena_verdict == "ARENA_VALID" and gate_verdict == "GATE_NO_MULTISIGNAL_VALUE":
        verdict = "HARD_FAIL_GATE_NO_VALUE"
    else:
        verdict = "MIDDLE"

    msg = ("profile=%s seeds=%d | ARENA %s (max|r|=%.3f copy=%.2fx p<=%.4f cMI=%d/4)"
           " | GATE %s (within-cell: route=%.3f wsum=%.3f best-single[%s]=%.3f"
           " rr_route=%.1f%% rr_wsum=%.1f%%; marginal: route=%.3f wsum=%.3f"
           " single=%.3f rr_wsum_marg=%.1f%%)" %
           (profile, len(seeds), arena_verdict, max_abs_r, mean_ratio, worst_p,
            min_info, gate_verdict, route_acc, wsum_acc,
            per_seed[0]["best_single_signal"], best_acc, 100 * route_rr,
            100 * wsum_rr, route_marg, wsum_marg, best_marg, 100 * wsum_marg_rr))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "arena_validity": {
            "verdict": arena_verdict, "max_abs_r": max_abs_r,
            "mean_pairwise_abs_r": mean_pair_r, "copying_ratio_mean": mean_ratio,
            "copying_worst_pvalue": worst_p, "mean_conditional_mi": mean_cmi,
            "min_informative_signals_of_4": min_info,
        },
        "gate_baseline": {
            "verdict": gate_verdict,
            "within_cell_bal_acc": {
                "route": route_acc, "weighted_sum": wsum_acc, "best_single": best_acc},
            "marginal_bal_acc": {
                "route": route_marg, "weighted_sum": wsum_marg, "best_single": best_marg},
            "best_single_signal": per_seed[0]["best_single_signal"],
            "rel_err_reduction_within_cell": {
                "route_vs_single": route_rr, "wsum_vs_single": wsum_rr},
            "rel_err_reduction_marginal": {
                "route_vs_single": route_marg_rr, "wsum_vs_single": wsum_marg_rr},
            "baseline_in_band": bool(baseline_in_band),
            "arms_differ_verified": bool(arms_differ_all),
        },
        "per_seed": per_seed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="staging A only: generator self-tests, tiny scale")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()

    t0 = time.perf_counter()

    if args.self_test:
        # tiny-scale generator self-test (staging A). Exercises the REAL arena
        # build + all 4 real signal functions + copy detector at small N.
        cfg = ArenaConfig(profile="smoke", seed=11)
        cfg.n_claims = 420
        cfg.n_schema_entities = 100
        _write_start_marker(1, "self_test")
        rng = np.random.default_rng(cfg.seed)
        arena = build_arena(cfg, rng)
        fails, notes, clusters = run_self_tests(arena)
        # exercise every signal function (real code path)
        _ = compute_all_signals(arena, clusters)
        print("=== STAGING A: GENERATOR SELF-TESTS (self-test mode) ===")
        for nline in notes:
            print("  " + nline)
        if fails:
            print("SELF-TEST FAILED:")
            for f in fails:
                print("  FAIL: " + f)
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "; ".join(fails), "elapsed_s":
                           time.perf_counter() - t0, "anchor_name": ANCHOR_NAME})
            return 2
        print("SELFTEST_PASS: all generator self-tests pass")
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71] if profile == "full" else [11, 23, 37])
    _write_start_marker(len(seeds), profile)

    per_seed = []
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=== profile=%s seeds=%s ===" % (profile, seeds))
    for si, sd in enumerate(seeds):
        cfg = ArenaConfig(profile=profile, seed=sd)
        res = run_one_seed(cfg, sd)
        if res["self_test_fails"]:
            print("SEED %d SELF-TEST FAIL: %s" % (sd, res["self_test_fails"]))
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "seed %d: %s" % (sd, res["self_test_fails"]),
                           "elapsed_s": time.perf_counter() - t0,
                           "anchor_name": ANCHOR_NAME})
            return 2
        per_seed.append(res)
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit_idx": si, "total_units": len(seeds),
                                "elapsed_s": time.perf_counter() - t0}) + "\n")
        print("  seed %d: max|r|=%.3f cMI=%d/4 copy=%.2fx | route=%.3f "
              "wsum=%.3f best_single[%s]=%.3f rr_route=%.1f%%" %
              (sd, res["max_abs_r"], res["n_informative"],
               res["copying"]["corr_ratio"], res["within_cell"]["route"],
               res["within_cell"]["weighted_sum"], res["best_single_signal"],
               res["within_cell"]["best_single"],
               100 * res["rel_err_reduction"]["route_vs_single"]))

    out = aggregate_and_verdict(profile, seeds, per_seed, time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("STAGING B -- ARENA VALIDITY: %s" % out["arena_validity"]["verdict"])
    av = out["arena_validity"]
    print("  max pairwise |r| = %.3f (band < 0.30; re-collapse if > 0.60)"
          % av["max_abs_r"])
    print("  mean pairwise |r|:")
    for k, v in av["mean_pairwise_abs_r"].items():
        print("    %-30s %.3f" % (k, v))
    print("  copying stress: %.2fx (indep>copied) worst-p=%.4f"
          % (av["copying_ratio_mean"], av["copying_worst_pvalue"]))
    print("  conditional-MI | other 3 (nats): " +
          ", ".join("%s=%.4f" % (k, v) for k, v in av["mean_conditional_mi"].items()))
    print("  informative signals (min across seeds): %d/4"
          % av["min_informative_signals_of_4"])
    print("\nSTAGING C -- GATE BASELINE: %s" % out["gate_baseline"]["verdict"])
    gb = out["gate_baseline"]
    wc, mg = gb["within_cell_bal_acc"], gb["marginal_bal_acc"]
    print("  within-cell bal-acc: route=%.3f weighted_sum=%.3f best_single[%s]=%.3f"
          % (wc["route"], wc["weighted_sum"], gb["best_single_signal"], wc["best_single"]))
    print("    rel err reduction: route=%.1f%% wsum=%.1f%% (HARD-PASS route >= 15%%)"
          % (100 * gb["rel_err_reduction_within_cell"]["route_vs_single"],
             100 * gb["rel_err_reduction_within_cell"]["wsum_vs_single"]))
    print("  marginal   bal-acc: route=%.3f weighted_sum=%.3f best_single=%.3f"
          % (mg["route"], mg["weighted_sum"], mg["best_single"]))
    print("    rel err reduction: route=%.1f%% wsum=%.1f%%"
          % (100 * gb["rel_err_reduction_marginal"]["route_vs_single"],
             100 * gb["rel_err_reduction_marginal"]["wsum_vs_single"]))
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"])
    print("  " + out["verdict_msg"])
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit
        _write_crash_metrics(e)
        raise
    sys.exit(rc)
