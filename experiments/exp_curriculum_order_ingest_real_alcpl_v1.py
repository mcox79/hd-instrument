"""exp_curriculum_order_ingest_real_alcpl_v1

FAIR real-data transfer test of the ingest-ORDER principle on a corpus that ACTUALLY has prerequisite
structure. The CoDEx sibling landed MIDDLE_BAND_METRIC_NEAR_VACUOUS; the brain-check attributed it to
CORPUS-MISMATCH (CoDEx = flat dense web, order VACUOUS per Knowledge-Space-Theory). AL-CPL is a genuine
author-validated strict partial-order concept-PREREQUISITE DAG (100% prerequisite-typed edges). If the
synthetic HARD_PASS transfers, curriculum order should now BEAT random/frequency.

PORTS `exp_curriculum_order_ingest_real_codex_v1.py` to AL-CPL directed prerequisite edges. Two documented
mechanistically-justified deviations (see preregs/2026-07-16_curriculum_order_ingest_real_alcpl_v1.md):
  (1) metric RA (common-neighbor) -> directed KATZ transitive-proximity (RA near-vacuous on a sparse DAG;
      Katz captures the transitive-closure signal that IS a prerequisite DAG's structure);
  (2) discriminator "reverse admits < 0.5*curriculum" -> "reverse quality craters to chance" (shallow
      depth-6 DAG does not strand >50% by count, but reverse builds a CHANCE-quality foundation).
All numeric margin/scramble/info-ceiling bands are UNCHANGED from CoDEx.

DATA (AL-CPL, github.com/harrylclc/AL-CPL-dataset, CC BY-NC-SA, local research use, not redistributed):
  <domain>.preqs  line "u,v" = "v is a prerequisite of u" -> directed edge v->u (prereq->dependent). POS.
  <domain>.pairs  all labeled candidate pairs = positives + negatives (negatives include the reversed
                  pair of every positive -> built-in popularity-neutral hard-negative set).

MECHANISM: FOUNDATION = admitted prereq edges + grounded concepts. seed S = ROOTS (in-degree-0) of the
TRAIN DAG (shared across arms). DIRECTIONAL schema_fit(p->d)=anchored(p): the PREREQUISITE p must be
grounded first. FIXED single-pass gate: admit iff anchored(p); on admit the dependent d grounds. An edge
whose prereq is not yet grounded is dropped forever -> ORDER matters.

ARMS: CURRICULUM (topo order) / RANDOM (mean over seeds) / FREQUENCY (popularity) / RANDOM_HOLD
(provisional-hold re-sweep) / REVERSE (discriminator).

QUALITY (held-out, non-circular, popularity-neutral): degree-orthogonalized directed KATZ AUROC over the
ADMITTED foundation, scoring held-out TEST positives vs negatives. Katz(x,y)=sum_k beta^k (A^k)[x,y]. Two
neg sets: ALL negs (primary) + REVERSED hard-negs (popularity-neutral corroboration). Budget sweep = size
control. Nulls: SCRAMBLE (degree-preserving directed rewire -> collapse) + tau0 (gate off -> identical).
INFO-CEILING gate checked FIRST: Q_cur_full - scramble >= 0.03 else metric near-vacuous (anti over-claim).

Determinism: numpy default_rng(fixed int seeds); no hash()-derived seeds; sorted() for set ops.
ASCII-only. No emojis. Local CPU single-shot, no queue/GPU/atoms/push. Runs to completion in foreground.
"""

import argparse
import json
import os
import sys
import time
import traceback
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "curriculum_order_ingest_real_alcpl_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- fixed config (a-priori) ----
TAU = 0.5             # admit iff prereq anchored (schema_fit >= 0.5). Set ONCE, principled.
K_GROUND = 1          # a concept anchors after its first admitted appearance as a dependent (or if seed).
TEST_FRAC = 0.30      # held-out fraction of positive edges (never admitted; scored).
SPLIT_RNG = 2024      # rng for the deterministic pos-edge train/test split (same across all arms).
RAND_SEEDS_FULL = [11, 23, 37, 41, 53]
RAND_SEEDS_SMOKE = [11, 23]
SCRAMBLE_SEEDS = [101, 202, 303, 404, 505]
KATZ_BETA = 0.5
KATZ_L = 6            # >= graph longest-path depth (measured 6 on Data Mining positive DAG).
BUDGET_GRID = [40, 80, 120]   # + min-admit cap appended at runtime.

# verdict thresholds (FIXED a-priori; UNCHANGED from CoDEx sibling)
MARGIN_CUR_RAND_HP = 0.030
MARGIN_CUR_FREQ_HP = 0.010
MARGIN_OVER_DEG_HP = 0.020
SCRAMBLE_HP = 0.55
SCRAMBLE_HF = 0.60
HOLD_RECOVERY_HP = 0.50
MARGIN_CUR_RAND_HF = 0.005
INFO_CEILING_MIN = 0.03
REV_QUALITY_CHANCE = 0.55     # reverse foundation quality must crater to <= this (discriminator).
REV_PREMATURE_MIN = 0.30      # reverse premature-rejection rate must be >= this (discriminator).


# --------------------------- data ------------------------------------------
def read_pairs(path):
    return [tuple(l.split(",")) for l in open(path, encoding="utf-8").read().split("\n") if l]


def load_dataset(domain):
    """AL-CPL domain -> directed prereq edges (prereq->dependent), node index, train/test split, negs."""
    ddir = os.path.join(REPO, "data", "alcpl")
    preqs = read_pairs(os.path.join(ddir, "%s.preqs" % domain))   # line (u,v): v prereq of u -> edge v->u
    pairs = read_pairs(os.path.join(ddir, "%s.pairs" % domain))   # all labeled candidate pairs
    pos_edges = [(v, u) for (u, v) in preqs]                      # directed edge prereq -> dependent
    pos_set = set(pos_edges)
    # node index over ALL concepts appearing in candidate pairs (superset of DAG nodes)
    concepts = set()
    for (a, b) in pairs:
        concepts.add(a); concepts.add(b)
    for (a, b) in preqs:
        concepts.add(a); concepts.add(b)
    nodes = sorted(concepts)
    idx = {n: i for i, n in enumerate(nodes)}
    n_ent = len(nodes)
    # negative candidate directed edges: line (u,v) whose (v,u) is NOT a positive edge -> candidate v->u
    neg_edges = [(v, u) for (u, v) in pairs if (v, u) not in pos_set]
    # reversed hard-negative for each positive edge (p,d): candidate (d,p) if present in .pairs negatives
    neg_set = set(neg_edges)
    # deterministic 30% hold-out of positive edges
    rng = np.random.default_rng(SPLIT_RNG)
    perm = rng.permutation(len(pos_edges))
    n_test = int(TEST_FRAC * len(pos_edges))
    test_i = sorted(perm[:n_test].tolist())
    train_i = sorted(perm[n_test:].tolist())
    train_edges = [pos_edges[i] for i in train_i]
    test_edges = [pos_edges[i] for i in test_i]
    train_set = set(train_edges)
    # leak guard: no held-out test edge may appear in the train (foundation-source) graph
    leak = sum(1 for e in test_edges if e in train_set)
    assert leak == 0, "LEAK: %d test edges in train graph" % leak
    # reversed hard-neg per test positive (identical endpoint degrees; only direction differs)
    test_rev = [(d, p) for (p, d) in test_edges]                 # candidate d->p (false direction)
    rev_present = [1 if (d, p) in neg_set else 0 for (p, d) in test_edges]
    return {
        "nodes": nodes, "idx": idx, "n_ent": n_ent,
        "train_edges": train_edges, "test_edges": test_edges,
        "neg_edges": neg_edges, "test_rev": test_rev, "rev_present": rev_present,
        "n_pos": len(pos_edges), "n_neg": len(neg_edges),
    }


# --------------------------- metrics ------------------------------------------
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


def katz_from_edges(edge_idx, n_ent, beta=KATZ_BETA, L=KATZ_L):
    """Directed Katz proximity matrix from foundation edges (as (src_idx, dst_idx) pairs)."""
    A = np.zeros((n_ent, n_ent), dtype=np.float64)
    for (a, b) in edge_idx:
        if a != b:
            A[a, b] = 1.0
    K = np.zeros((n_ent, n_ent), dtype=np.float64)
    Ak = np.eye(n_ent, dtype=np.float64)
    for _k in range(1, L + 1):
        Ak = Ak @ A
        K += (beta ** _k) * Ak
    return K, A


def _edge_idx(edges, idx):
    return [(idx[p], idx[d]) for (p, d) in edges]


def _degrees_from_edges(edge_idx, n_ent):
    outd = np.zeros(n_ent, dtype=np.float64)
    ind = np.zeros(n_ent, dtype=np.float64)
    for (a, b) in edge_idx:
        if a != b:
            outd[a] += 1.0; ind[b] += 1.0
    return outd, ind


def _score_cands(K, cands_idx):
    return np.array([K[a, b] for (a, b) in cands_idx], dtype=np.float64)


def _best_degree_auroc(y, outd, ind, cands_idx):
    """Popularity baseline: best single directed-degree feature AUROC (oriented)."""
    op = np.array([outd[a] for (a, b) in cands_idx], dtype=np.float64)
    ip = np.array([ind[b] for (a, b) in cands_idx], dtype=np.float64)
    out = 0.0
    for v in (op, ip, op + ip):
        a = auroc(y, v)
        out = max(out, a, 1.0 - a)
    return out


def quality_from_foundation(data, admitted_edges):
    """Degree-orthogonalized directed-Katz AUROC over the admitted foundation (popularity-neutral).

    Returns orth/raw AUROC vs ALL negatives (primary) + vs REVERSED hard-negs (pop-neutral) + degree
    baseline + margin_over_degree. Degree-orthogonalization is LABEL-FREE: fit OLS Katz ~ [1, log
    outdeg(src), log indeg(dst)] over ALL candidate pairs (no labels), residualize, AUROC on residual.
    """
    idx = data["idx"]; n_ent = data["n_ent"]
    fnd = _edge_idx(admitted_edges, idx)
    K, _A = katz_from_edges(fnd, n_ent)
    outd, ind = _degrees_from_edges(fnd, n_ent)

    pos_c = _edge_idx(data["test_edges"], idx)
    neg_c = _edge_idx(data["neg_edges"], idx)
    rev_c = _edge_idx(data["test_rev"], idx)

    def feats(cands):
        s = _score_cands(K, cands)
        lo = np.log1p(np.array([outd[a] for (a, b) in cands], dtype=np.float64))
        li = np.log1p(np.array([ind[b] for (a, b) in cands], dtype=np.float64))
        return s, lo, li

    sp, lop, lip = feats(pos_c)
    sn, lon, lin = feats(neg_c)
    sr, lor, lir = feats(rev_c)
    # LABEL-FREE OLS degree projection fit on ALL candidate pairs (pos + all-neg); labels never used here
    s_all = np.concatenate([sp, sn]); lo_all = np.concatenate([lop, lon]); li_all = np.concatenate([lip, lin])
    Amat = np.column_stack([np.ones(len(s_all)), lo_all, li_all])
    coef, _, _, _ = np.linalg.lstsq(Amat, s_all, rcond=None)

    def resid(s, lo, li):
        return s - (coef[0] + coef[1] * lo + coef[2] * li)

    y_all = np.concatenate([np.ones(len(sp)), np.zeros(len(sn))])
    orth_all = auroc(y_all, np.concatenate([resid(sp, lop, lip), resid(sn, lon, lin)]))
    raw_all = auroc(y_all, np.concatenate([sp, sn]))
    deg_all = _best_degree_auroc(y_all, outd, ind, pos_c + neg_c)
    # reversed hard-neg (popularity-neutral): only test positives whose reversed pair is a real negative
    mask = np.array(data["rev_present"], dtype=bool)
    if mask.sum() > 0:
        y_rev = np.concatenate([np.ones(int(mask.sum())), np.zeros(int(mask.sum()))])
        pr = resid(sp, lop, lip)[mask]; rr = resid(sr, lor, lir)[mask]
        orth_rev = auroc(y_rev, np.concatenate([pr, rr]))
        raw_rev = auroc(y_rev, np.concatenate([sp[mask], sr[mask]]))
    else:
        orth_rev = 0.5; raw_rev = 0.5
    return {"orth_all": orth_all, "raw_all": raw_all, "degree_all": deg_all,
            "margin_over_degree": orth_all - deg_all, "orth_rev": orth_rev, "raw_rev": raw_rev}


def scramble_quality(data, admitted_edges, rng):
    """Degree-preserving directed rewire null: preserve out/in-degree sequence, destroy specific edges.
    The degree-ORTHOGONALIZED Katz AUROC must collapse -- else the metric is a degree/popularity artifact."""
    idx = data["idx"]; n_ent = data["n_ent"]
    fnd = _edge_idx(admitted_edges, idx)
    outd, ind = _degrees_from_edges(fnd, n_ent)
    src = []; dst = []
    for n in range(n_ent):
        src += [n] * int(outd[n]); dst += [n] * int(ind[n])
    if not src or not dst:
        return 0.5
    src = np.array(src); dst = np.array(dst)
    rng.shuffle(src); rng.shuffle(dst)
    re = [(int(src[i]), int(dst[i])) for i in range(len(src)) if src[i] != dst[i]]
    # score orth-all AUROC on the rewired foundation
    K, _A = katz_from_edges(re, n_ent)
    o2, i2 = _degrees_from_edges(re, n_ent)
    pos_c = _edge_idx(data["test_edges"], idx)
    neg_c = _edge_idx(data["neg_edges"], idx)

    def feats(cands):
        s = _score_cands(K, cands)
        lo = np.log1p(np.array([o2[a] for (a, b) in cands], dtype=np.float64))
        li = np.log1p(np.array([i2[b] for (a, b) in cands], dtype=np.float64))
        return s, lo, li

    sp, lop, lip = feats(pos_c); sn, lon, lin = feats(neg_c)
    s_all = np.concatenate([sp, sn]); lo_all = np.concatenate([lop, lon]); li_all = np.concatenate([lip, lin])
    Amat = np.column_stack([np.ones(len(s_all)), lo_all, li_all])
    coef, _, _, _ = np.linalg.lstsq(Amat, s_all, rcond=None)
    r = np.concatenate([sp - (coef[0] + coef[1] * lop + coef[2] * lip),
                        sn - (coef[0] + coef[1] * lon + coef[2] * lin)])
    return auroc(np.concatenate([np.ones(len(sp)), np.zeros(len(sn))]), r)


# --------------------------- ordering functions -------------------------------
def train_roots(train_edges, idx, n_ent):
    """Roots = concepts (strings) with in-degree 0 in the TRAIN prereq DAG (genuinely foundational).
    Returns the seed set as CONCEPT STRINGS to match ingest_strict (which operates on string edges)."""
    indeg = defaultdict(int); nodes = set()
    for (p, d) in train_edges:
        indeg[d] += 1; nodes.add(p); nodes.add(d)
    return set(n for n in nodes if indeg[n] == 0), nodes


def curriculum_order(train_edges, idx):
    """Topological-order admission: edges sorted by (topo-rank of prereq, topo-rank of dependent)."""
    adj = defaultdict(list); ind = defaultdict(int); nodes = set()
    for (p, d) in train_edges:
        adj[idx[p]].append(idx[d]); ind[idx[d]] += 1
        nodes.add(idx[p]); nodes.add(idx[d])
    for n in nodes:
        ind.setdefault(n, 0)
    ind_work = dict(ind)
    q = deque(sorted(n for n in nodes if ind_work[n] == 0))
    topo = []
    while q:
        x = q.popleft(); topo.append(x)
        for y in sorted(adj[x]):
            ind_work[y] -= 1
            if ind_work[y] == 0:
                q.append(y)
    rank = {n: i for i, n in enumerate(topo)}
    big = len(topo) + 1
    return sorted(train_edges, key=lambda e: (rank.get(idx[e[0]], big), rank.get(idx[e[1]], big),
                                              idx[e[0]], idx[e[1]]))


def frequency_order(train_edges, idx, n_ent):
    """Popularity ordering: descending (prereq out-degree + dependent in-degree), then id."""
    outd, ind = _degrees_from_edges(_edge_idx(train_edges, idx), n_ent)
    return sorted(train_edges, key=lambda e: (-(outd[idx[e[0]]] + ind[idx[e[1]]]), idx[e[0]], idx[e[1]]))


# --------------------------- ingestion gate -----------------------------------
def ingest_strict(train_edges, seq, seed_entities, tau, k_ground):
    """Directional single-pass strict gate. schema_fit(p->d)=anchored(p); admit iff >=tau; on admit d
    grounds. Returns admitted edges (admission order), anchored set, premature-recoverable count."""
    anchored = set(seed_entities)
    dep_count = defaultdict(int)
    admitted = []; rejected = []
    for (p, d) in seq:
        sf = 1.0 if p in anchored else 0.0
        if sf >= tau:
            admitted.append((p, d))
            dep_count[d] += 1
            if d not in anchored and dep_count[d] >= k_ground:
                anchored.add(d)
        else:
            rejected.append((p, d))
    premature = sum(1 for (p, d) in rejected if p in anchored)   # prereq later anchored -> recoverable
    return {"admitted": admitted, "anchored": anchored, "rejected": rejected,
            "premature": premature, "n_seq": len(seq)}


def ingest_hold(train_edges, seq, seed_entities, tau, k_ground, max_passes):
    """Provisional-hold: rejected -> hold buffer; drain sweeps (anchored frozen per pass) to fixpoint."""
    anchored = set(seed_entities)
    dep_count = defaultdict(int)
    admitted = []; hold = []

    def try_place(p, d):
        sf = 1.0 if p in anchored else 0.0
        if sf >= tau:
            admitted.append((p, d)); dep_count[d] += 1
            if d not in anchored and dep_count[d] >= k_ground:
                anchored.add(d)
            return True
        return False

    for (p, d) in seq:
        if not try_place(p, d):
            hold.append((p, d))
    phase1_hold = len(hold)
    passes = 0
    buffer_trace = [len(hold)]
    while hold and passes < max_passes:
        passes += 1
        snapshot = frozenset(anchored)
        admitted_this = 0; still = []
        for (p, d) in hold:
            sf = 1.0 if p in snapshot else 0.0
            if sf >= tau and try_place(p, d):
                admitted_this += 1
            else:
                still.append((p, d))
        hold = still
        buffer_trace.append(len(hold))
        if admitted_this == 0:
            break
    monotone = all(buffer_trace[i + 1] <= buffer_trace[i] for i in range(len(buffer_trace) - 1))
    return {"admitted": admitted, "phase1_hold": phase1_hold, "final_hold": len(hold),
            "passes": passes, "buffer_monotone": monotone}


# --------------------------- arm runner ---------------------------------------
def run_arms(data, tau, k_ground, rand_seeds):
    idx = data["idx"]; n_ent = data["n_ent"]; train_edges = data["train_edges"]
    seed_entities, _tnodes = train_roots(train_edges, idx, n_ent)
    n_tr = len(train_edges)
    max_passes = 64

    cur_seq = curriculum_order(train_edges, idx)
    freq_seq = frequency_order(train_edges, idx, n_ent)
    rev_seq = list(reversed(cur_seq))

    cur = ingest_strict(train_edges, cur_seq, seed_entities, tau, k_ground)
    freq = ingest_strict(train_edges, freq_seq, seed_entities, tau, k_ground)
    rev = ingest_strict(train_edges, rev_seq, seed_entities, tau, k_ground)

    rand_runs = []; hold_runs = []
    for s in rand_seeds:
        prng = np.random.default_rng(s)
        rseq = [train_edges[i] for i in prng.permutation(n_tr).tolist()]
        rand_runs.append(ingest_strict(train_edges, rseq, seed_entities, tau, k_ground))
        hold_runs.append(ingest_hold(train_edges, rseq, seed_entities, tau, k_ground, max_passes))

    def admit_n(run):
        return len(run["admitted"])

    def mean(vs):
        return float(np.mean(vs))

    def std(vs):
        return float(np.std(vs))

    def orthB(edges, B):
        return quality_from_foundation(data, edges[:B])["orth_all"]

    # ---- BUDGET SWEEP (size control): first-B admitted foundations per arm ----
    admit_cap = min(admit_n(cur), admit_n(freq), min(admit_n(r) for r in rand_runs))
    grid = sorted(b for b in BUDGET_GRID if b <= admit_cap)
    if not grid or grid[-1] < admit_cap:
        grid = sorted(set(grid) | {admit_cap})

    budget_sweep = {}
    margins_cur_rand = []; margins_cur_freq = []; cur_margin_over_deg_grid = []
    for B in grid:
        qc = quality_from_foundation(data, cur["admitted"][:B])
        qf = quality_from_foundation(data, freq["admitted"][:B])
        qr = [orthB(r["admitted"], B) for r in rand_runs]
        qrev = orthB(rev["admitted"], B) if admit_n(rev) >= B else None
        m_cr = qc["orth_all"] - mean(qr)
        m_cf = qc["orth_all"] - qf["orth_all"]
        margins_cur_rand.append(m_cr); margins_cur_freq.append(m_cf)
        cur_margin_over_deg_grid.append(qc["margin_over_degree"])
        budget_sweep["B_%d" % B] = {
            "q_cur_orth": qc["orth_all"], "q_cur_margin_deg": qc["margin_over_degree"],
            "q_cur_orth_rev": qc["orth_rev"],
            "q_freq_orth": qf["orth_all"], "q_rand_orth_mean": mean(qr), "q_rand_orth_std": std(qr),
            "q_rev_orth": qrev, "margin_cur_rand": m_cr, "margin_cur_freq": m_cf,
        }

    q_cur_full = quality_from_foundation(data, cur["admitted"])
    q_freq_full = quality_from_foundation(data, freq["admitted"])
    q_rev_full = quality_from_foundation(data, rev["admitted"])
    q_rand_full = [quality_from_foundation(data, r["admitted"]) for r in rand_runs]
    q_hold_full = [quality_from_foundation(data, h["admitted"]) for h in hold_runs]

    scr = [scramble_quality(data, cur["admitted"], np.random.default_rng(s)) for s in SCRAMBLE_SEEDS]
    scramble_auroc = float(np.mean(scr))

    def prem_rate(run):
        return run["premature"] / float(run["n_seq"]) if run["n_seq"] else 0.0

    frac_cr_pos = float(np.mean([1.0 if m >= MARGIN_CUR_RAND_HP else 0.0 for m in margins_cur_rand]))
    frac_cf_pos = float(np.mean([1.0 if m >= MARGIN_CUR_FREQ_HP else 0.0 for m in margins_cur_freq]))

    out = {
        "seed_entities_n": len(seed_entities),
        "budget_grid": grid, "budget_sweep": budget_sweep,
        "margin_cur_rand_mean_over_grid": mean(margins_cur_rand),
        "margin_cur_rand_min_over_grid": float(min(margins_cur_rand)),
        "margin_cur_rand_max_over_grid": float(max(margins_cur_rand)),
        "margin_cur_freq_mean_over_grid": mean(margins_cur_freq),
        "cur_margin_over_degree_mean_over_grid": mean(cur_margin_over_deg_grid),
        "frac_budgets_cur_rand_ge_hp": frac_cr_pos,
        "frac_budgets_cur_freq_ge_hp": frac_cf_pos,
        "n_budgets": len(grid),
        "arms": {
            "curriculum": {"admit": admit_n(cur), "admit_rate": admit_n(cur) / n_tr,
                           "premature_rate": prem_rate(cur),
                           "q_full_orth": q_cur_full["orth_all"], "q_full_raw": q_cur_full["raw_all"],
                           "q_full_orth_rev": q_cur_full["orth_rev"],
                           "q_full_margin_deg": q_cur_full["margin_over_degree"],
                           "degree_auroc_full": q_cur_full["degree_all"]},
            "frequency": {"admit": admit_n(freq), "admit_rate": admit_n(freq) / n_tr,
                          "premature_rate": prem_rate(freq), "q_full_orth": q_freq_full["orth_all"],
                          "q_full_orth_rev": q_freq_full["orth_rev"]},
            "reverse": {"admit": admit_n(rev), "admit_rate": admit_n(rev) / n_tr,
                        "premature_rate": prem_rate(rev), "q_full_orth": q_rev_full["orth_all"],
                        "q_full_orth_rev": q_rev_full["orth_rev"]},
            "random": {"admit_mean": mean([admit_n(r) for r in rand_runs]),
                       "admit_rate_mean": mean([admit_n(r) / n_tr for r in rand_runs]),
                       "premature_rate_mean": mean([prem_rate(r) for r in rand_runs]),
                       "premature_rate_std": std([prem_rate(r) for r in rand_runs]),
                       "q_full_orth_mean": mean([q["orth_all"] for q in q_rand_full]),
                       "q_full_orth_std": std([q["orth_all"] for q in q_rand_full]),
                       "q_full_orth_rev_mean": mean([q["orth_rev"] for q in q_rand_full])},
            "random_hold": {"admit_mean": mean([admit_n(h) for h in hold_runs]),
                            "admit_rate_mean": mean([admit_n(h) / n_tr for h in hold_runs]),
                            "q_full_orth_mean": mean([q["orth_all"] for q in q_hold_full]),
                            "passes_mean": mean([h["passes"] for h in hold_runs]),
                            "passes_max": int(max(h["passes"] for h in hold_runs)),
                            "phase1_hold_mean": mean([h["phase1_hold"] for h in hold_runs]),
                            "final_hold_mean": mean([h["final_hold"] for h in hold_runs]),
                            "buffer_monotone_all": bool(all(h["buffer_monotone"] for h in hold_runs))},
        },
        "scramble_auroc": scramble_auroc,
        "_admit_cur": frozenset(cur["admitted"]),
        "_admit_rand0": frozenset(rand_runs[0]["admitted"]),
        "_admit_hold0": frozenset(hold_runs[0]["admitted"]),
    }
    return out


def tau0_null(data, k_ground):
    """Gate OFF (tau=0): every order admits identical full train graph -> order-invariant."""
    idx = data["idx"]; n_ent = data["n_ent"]; train_edges = data["train_edges"]
    seed_entities, _ = train_roots(train_edges, idx, n_ent)
    cur_seq = curriculum_order(train_edges, idx)
    freq_seq = frequency_order(train_edges, idx, n_ent)
    rprng = np.random.default_rng(11)
    rseq = [train_edges[i] for i in rprng.permutation(len(train_edges)).tolist()]
    sets = {}; qs = {}
    for name, seq in (("curriculum", cur_seq), ("frequency", freq_seq), ("random", rseq)):
        run = ingest_strict(train_edges, seq, seed_entities, 0.0, k_ground)
        sets[name] = frozenset(run["admitted"])
        qs[name] = quality_from_foundation(data, run["admitted"])["orth_all"]
    identical = (sets["curriculum"] == sets["frequency"] == sets["random"])
    spread = max(qs.values()) - min(qs.values())
    return {"identical_admit_sets": bool(identical), "quality_spread": float(spread), "q_by_order": qs}


# --------------------------- verdict ------------------------------------------
def compute_verdict(res, tau0):
    a = res["arms"]
    margin_cur_rand = res["margin_cur_rand_mean_over_grid"]
    margin_cur_freq = res["margin_cur_freq_mean_over_grid"]
    cur_margin_deg = res["cur_margin_over_degree_mean_over_grid"]
    frac_cr = res["frac_budgets_cur_rand_ge_hp"]
    robust_cr = (frac_cr >= 0.5)

    q_cur_full = a["curriculum"]["q_full_orth"]
    q_rand_full = a["random"]["q_full_orth_mean"]
    q_hold_full = a["random_hold"]["q_full_orth_mean"]
    scramble = res["scramble_auroc"]

    # DISCRIMINATOR (deviation from CoDEx, documented): REVERSE builds a CHANCE-quality foundation
    # (order-sensitivity signature on a shallow DAG) with elevated premature rejection.
    rev_prem = a["reverse"]["premature_rate"]
    rand_prem = a["random"]["premature_rate_mean"]
    q_rev_full = a["reverse"]["q_full_orth"]
    rev_craters = (q_rev_full <= REV_QUALITY_CHANCE) and (rev_prem >= REV_PREMATURE_MIN)

    denom = q_cur_full - q_rand_full
    hold_recovery = (q_hold_full - q_rand_full) / denom if abs(denom) > 1e-6 else (
        1.0 if abs(q_hold_full - q_cur_full) < 1e-6 else 0.0)

    tau0_ok = tau0["identical_admit_sets"] and (tau0["quality_spread"] <= 1e-6)
    arms_differ = (res["_admit_cur"] != res["_admit_rand0"]) and (res["_admit_hold0"] != res["_admit_rand0"])

    # INFO-CEILING guard (checked FIRST): best real foundation vs its own degree-scramble.
    info_ceiling = q_cur_full - scramble
    metric_near_vacuous = (info_ceiling < INFO_CEILING_MIN)

    hard_pass = (margin_cur_rand >= MARGIN_CUR_RAND_HP and robust_cr
                 and margin_cur_freq >= MARGIN_CUR_FREQ_HP and cur_margin_deg >= MARGIN_OVER_DEG_HP
                 and scramble <= SCRAMBLE_HP and tau0_ok and rev_craters and not metric_near_vacuous)
    hard_fail = ((margin_cur_rand <= MARGIN_CUR_RAND_HF and not metric_near_vacuous)
                 or scramble > SCRAMBLE_HF or not tau0_ok)

    if not tau0_ok:
        verdict = "HARD_FAIL_TAU0_NOT_ORDER_INVARIANT_HARNESS_BUG"
    elif not arms_differ:
        verdict = "BLOCK_ARMS_IDENTICAL"
    elif scramble > SCRAMBLE_HF:
        verdict = "HARD_FAIL_SCRAMBLE_NULL_NOT_STRUCTURAL_METRIC_ARTIFACT"
    elif metric_near_vacuous:
        verdict = "MIDDLE_BAND_METRIC_NEAR_VACUOUS_INFO_CEILING_LOW"
    elif not rev_craters:
        verdict = "MIDDLE_BAND_DISCRIMINATOR_DID_NOT_FIRE_REVERSE_DID_NOT_CRATER"
    elif hard_pass:
        verdict = "HARD_PASS_CURRICULUM_ORDER_BUILDS_BETTER_REAL_FOUNDATION"
    elif hard_fail:
        verdict = "HARD_FAIL_ORDER_INVARIANT_QUALITY_NO_PRIZE"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "margin_cur_rand_mean_grid": margin_cur_rand,
        "margin_cur_rand_max_grid": res["margin_cur_rand_max_over_grid"],
        "margin_cur_rand_min_grid": res["margin_cur_rand_min_over_grid"],
        "margin_cur_freq_mean_grid": margin_cur_freq,
        "frac_budgets_cur_rand_ge_hp": frac_cr,
        "robust_cur_rand_majority": bool(robust_cr),
        "curriculum_margin_over_degree_mean_grid": cur_margin_deg,
        "scramble_auroc": scramble,
        "info_ceiling_cur_full_minus_scramble": info_ceiling,
        "metric_near_vacuous": bool(metric_near_vacuous),
        "reverse_premature_rate": rev_prem, "random_premature_rate": rand_prem,
        "reverse_q_full_orth": q_rev_full, "reverse_craters": bool(rev_craters),
        "hold_recovery_fraction": hold_recovery,
        "q_cur_full": q_cur_full, "q_rand_full": q_rand_full, "q_hold_full": q_hold_full,
        "q_cur_full_orth_rev": a["curriculum"]["q_full_orth_rev"],
        "q_rand_full_orth_rev": a["random"]["q_full_orth_rev_mean"],
        "tau0_order_invariant": bool(tau0_ok), "arms_differ": bool(arms_differ),
    }


def _strip(res):
    return {k: v for k, v in res.items() if not k.startswith("_admit")}


# --------------------------- self-test ----------------------------------------
def self_test():
    # (A) AUROC orientation + ties.
    assert auroc(np.array([1, 1, 0, 0]), np.array([0.9, 0.8, 0.2, 0.1])) == 1.0, "auroc orientation"
    assert abs(auroc(np.array([1, 0]), np.array([0.5, 0.5])) - 0.5) < 1e-9, "auroc ties -> 0.5"
    # (B) Katz recovers a planted 2-hop transitive edge: a->b, b->c in foundation -> Katz[a,c] > 0.
    K, _A = katz_from_edges([(0, 1), (1, 2)], 3)
    assert K[0, 2] > 0.0 and K[2, 0] == 0.0, "Katz must recover directed 2-hop transitive proximity"

    # (C) discriminator + nulls on REAL AL-CPL Data Mining at FULL graph (small; ~1s), reduced 2-seed rand.
    data = load_dataset("data_mining")
    res = run_arms(data, TAU, K_GROUND, RAND_SEEDS_SMOKE)
    tau0 = tau0_null(data, K_GROUND)
    v = compute_verdict(res, tau0)
    a = res["arms"]

    # DISCRIMINATOR (deviation, documented): REVERSE builds chance-quality foundation + high premature.
    assert a["reverse"]["q_full_orth"] <= REV_QUALITY_CHANCE, \
        "discriminator: reverse foundation must crater to chance, got orth=%.3f" % a["reverse"]["q_full_orth"]
    assert a["reverse"]["premature_rate"] >= REV_PREMATURE_MIN, \
        "discriminator: reverse premature must be >= %.2f, got %.3f" % (REV_PREMATURE_MIN, a["reverse"]["premature_rate"])
    # arms differ: curriculum admits more than random; hold admits >= random.
    assert a["curriculum"]["admit"] > a["random"]["admit_mean"], "curriculum must admit more than random"
    assert a["random_hold"]["admit_mean"] >= a["random"]["admit_mean"], "hold must admit >= random"
    assert res["_admit_cur"] != res["_admit_rand0"], "arms-must-differ: cur vs rand"
    # leak guard already asserted in load_dataset; re-assert admitted foundation excludes test edges.
    test_set = set(data["test_edges"])
    assert not (set(a_e for a_e in res["_admit_cur"]) & test_set), "LEAK: test edge in curriculum foundation"
    # tau0 null: order-invariant.
    assert tau0["identical_admit_sets"], "tau0 must admit identical sets across orders"
    assert tau0["quality_spread"] <= 1e-6, "tau0 quality spread must be ~0, got %.6f" % tau0["quality_spread"]
    # scramble null: degree-preserving rewire collapses orth AUROC (metric is structural).
    assert res["scramble_auroc"] <= SCRAMBLE_HF, \
        "scramble null must collapse (orth metric), got %.3f" % res["scramble_auroc"]
    # INFO-CEILING non-vacuous at smoke (the whole point vs CoDEx).
    assert v["info_ceiling_cur_full_minus_scramble"] >= INFO_CEILING_MIN, \
        "info-ceiling must be non-vacuous, got %.3f" % v["info_ceiling_cur_full_minus_scramble"]
    # hold buffer bounded/monotone + drain terminated.
    assert a["random_hold"]["buffer_monotone_all"], "hold buffer must be monotone non-increasing"
    assert a["random_hold"]["passes_max"] < 64, "hold drain must terminate (fixpoint)"
    # curriculum quality in a measurable band.
    assert 0.05 < a["curriculum"]["q_full_orth"] < 0.99, \
        "curriculum orth-Katz-AUROC must be measurable, got %.3f" % a["curriculum"]["q_full_orth"]
    assert res["n_budgets"] >= 2, "budget sweep must have >=2 points"

    print("[SELF-TEST] PASS")
    print("  budgets=%s  margin_cur_rand(mean/max grid)=%.3f/%.3f  margin_cur_freq(mean)=%.3f" % (
        res["budget_grid"], v["margin_cur_rand_mean_grid"], v["margin_cur_rand_max_grid"],
        v["margin_cur_freq_mean_grid"]))
    print("  admit: cur=%d freq=%d rev=%d rand=%.0f hold=%.0f | premature rev=%.3f rand=%.3f" % (
        a["curriculum"]["admit"], a["frequency"]["admit"], a["reverse"]["admit"],
        a["random"]["admit_mean"], a["random_hold"]["admit_mean"],
        a["reverse"]["premature_rate"], a["random"]["premature_rate_mean"]))
    print("  Q@full cur=%.3f freq=%.3f rev=%.3f rand=%.3f | scramble=%.3f info_ceiling=%.3f near_vacuous=%s" % (
        a["curriculum"]["q_full_orth"], a["frequency"]["q_full_orth"], a["reverse"]["q_full_orth"],
        a["random"]["q_full_orth_mean"], v["scramble_auroc"], v["info_ceiling_cur_full_minus_scramble"],
        v["metric_near_vacuous"]))
    print("  tau0_inv=%s rev_craters=%s -> %s" % (v["tau0_order_invariant"], v["reverse_craters"], v["verdict"]))
    return True


# --------------------------- main ---------------------------------------------
def main(domain="data_mining", rand_seeds=None):
    t0 = time.time()
    ts = datetime.now(timezone.utc)
    rand_seeds = rand_seeds if rand_seeds is not None else RAND_SEEDS_FULL
    data = load_dataset(domain)
    print("[load] domain=%s n_ent=%d n_train=%d n_test=%d n_neg=%d" % (
        domain, data["n_ent"], len(data["train_edges"]), len(data["test_edges"]), data["n_neg"]), flush=True)
    res = run_arms(data, TAU, K_GROUND, rand_seeds)
    tau0 = tau0_null(data, K_GROUND)
    verdict = compute_verdict(res, tau0)

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict["verdict"],
        "verdict_msg": ("%s | domain=%s margin_cur_rand(mean grid)=%.3f (max=%.3f, min=%.3f, frac>=hp=%.2f) "
                        "margin_cur_freq=%.3f cur_margin_deg=%.3f scramble=%.3f info_ceiling=%.3f "
                        "rev_q=%.3f rev_prem=%.3f rev_craters=%s tau0_inv=%s" % (
                            verdict["verdict"], domain, verdict["margin_cur_rand_mean_grid"],
                            verdict["margin_cur_rand_max_grid"], verdict["margin_cur_rand_min_grid"],
                            verdict["frac_budgets_cur_rand_ge_hp"], verdict["margin_cur_freq_mean_grid"],
                            verdict["curriculum_margin_over_degree_mean_grid"], verdict["scramble_auroc"],
                            verdict["info_ceiling_cur_full_minus_scramble"], verdict["reverse_q_full_orth"],
                            verdict["reverse_premature_rate"], verdict["reverse_craters"],
                            verdict["tau0_order_invariant"])),
        "summary": verdict["verdict"],
        "elapsed_s": elapsed, "ts_iso": ts.isoformat(), "domain": domain, "run_mode": "full",
        "config": {"tau": TAU, "k_ground": K_GROUND, "test_frac": TEST_FRAC, "split_rng": SPLIT_RNG,
                   "rand_seeds": rand_seeds, "scramble_seeds": SCRAMBLE_SEEDS, "katz_beta": KATZ_BETA,
                   "katz_L": KATZ_L, "budget_grid_base": BUDGET_GRID,
                   "bands": {"margin_cur_rand_hp": MARGIN_CUR_RAND_HP, "margin_cur_freq_hp": MARGIN_CUR_FREQ_HP,
                             "margin_over_deg_hp": MARGIN_OVER_DEG_HP, "scramble_hp": SCRAMBLE_HP,
                             "scramble_hf": SCRAMBLE_HF, "hold_recovery_hp": HOLD_RECOVERY_HP,
                             "margin_cur_rand_hf": MARGIN_CUR_RAND_HF, "info_ceiling_min": INFO_CEILING_MIN,
                             "rev_quality_chance": REV_QUALITY_CHANCE, "rev_premature_min": REV_PREMATURE_MIN}},
        "verdict_detail": verdict, "results": _strip(res), "tau0_null": tau0,
    }
    out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)

    a = res["arms"]
    print("[VERDICT] %s" % verdict["verdict"])
    print("  seed_roots=%d  budget_grid=%s" % (res["seed_entities_n"], res["budget_grid"]))
    print("  ADMIT   cur=%d freq=%d rev=%d rand=%.0f hold=%.0f" % (
        a["curriculum"]["admit"], a["frequency"]["admit"], a["reverse"]["admit"],
        a["random"]["admit_mean"], a["random_hold"]["admit_mean"]))
    print("  PREMATURE cur=%.3f freq=%.3f rev=%.3f rand=%.3f" % (
        a["curriculum"]["premature_rate"], a["frequency"]["premature_rate"],
        a["reverse"]["premature_rate"], a["random"]["premature_rate_mean"]))
    print("  BUDGET SWEEP (degree-orth held-out Katz AUROC):")
    for B in res["budget_grid"]:
        bs = res["budget_sweep"]["B_%d" % B]
        rev_s = ("%.3f" % bs["q_rev_orth"]) if bs["q_rev_orth"] is not None else "  -  "
        print("    B=%-5d cur=%.3f rand=%.3f freq=%.3f rev=%s | m_cr=%+.3f m_cf=%+.3f cur_mdeg=%+.3f" % (
            B, bs["q_cur_orth"], bs["q_rand_orth_mean"], bs["q_freq_orth"], rev_s,
            bs["margin_cur_rand"], bs["margin_cur_freq"], bs["q_cur_margin_deg"]))
    print("  margin_cur_rand mean/max/min grid=%.3f/%.3f/%.3f frac_budgets>=hp=%.2f (robust=%s)" % (
        verdict["margin_cur_rand_mean_grid"], verdict["margin_cur_rand_max_grid"],
        verdict["margin_cur_rand_min_grid"], verdict["frac_budgets_cur_rand_ge_hp"],
        verdict["robust_cur_rand_majority"]))
    print("  margin_cur_freq mean grid=%.3f (hp>=%.3f)" % (verdict["margin_cur_freq_mean_grid"], MARGIN_CUR_FREQ_HP))
    print("  Q@full orth(all): cur=%.3f freq=%.3f rand=%.3f hold=%.3f | hold_recovery=%.3f" % (
        a["curriculum"]["q_full_orth"], a["frequency"]["q_full_orth"], a["random"]["q_full_orth_mean"],
        a["random_hold"]["q_full_orth_mean"], verdict["hold_recovery_fraction"]))
    print("  Q@full orth(rev,pop-neutral): cur=%.3f freq=%.3f rand=%.3f rev=%.3f" % (
        a["curriculum"]["q_full_orth_rev"], a["frequency"]["q_full_orth_rev"],
        a["random"]["q_full_orth_rev_mean"], a["reverse"]["q_full_orth_rev"]))
    print("  scramble_orth=%.3f (<=%.2f pass) | INFO-CEILING=%.3f (>=%.2f) near_vacuous=%s" % (
        verdict["scramble_auroc"], SCRAMBLE_HP, verdict["info_ceiling_cur_full_minus_scramble"],
        INFO_CEILING_MIN, verdict["metric_near_vacuous"]))
    print("  reverse Q_full_orth=%.3f (craters<=%.2f) rev_craters=%s | tau0_inv=%s spread=%.6f" % (
        verdict["reverse_q_full_orth"], REV_QUALITY_CHANCE, verdict["reverse_craters"],
        tau0["identical_admit_sets"], tau0["quality_spread"]))
    print("  metrics -> %s" % final)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--domain", default="data_mining",
                    choices=["data_mining", "geometry", "physics", "precalculus"])
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(domain=args.domain)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
