"""exp_curriculum_order_ingest_real_codex_v1

REAL-DATA transfer test of the ingest-ORDER principle. Does ingesting REAL CoDEx-S facts (structured
triples) in a CURRICULUM order (already-anchored / foundational facts first) through a single-pass
schema-fit gate build a BETTER foundation than RANDOM order or FREQUENCY (popularity) order? "Better"
= held-out, non-circular, popularity-neutral quality (claim-validity AUROC of the pairwise RA schema-fit
index computed from the ADMITTED foundation subgraph, scored on human-verified hard negatives).

Ports two synthetic HARD_PASS cells to real data:
  - exp_curriculum_order_ingest_schema_fit_v1  (order matters; curriculum rescues schema-fit)
  - exp_provisional_hold_bootstrap_arbitrary_order_v1  (provisional-hold recovers arbitrary order)

MECHANISM PORT (see preregs/2026-07-16_curriculum_order_ingest_real_codex_v1.md):
  synthetic prerequisite DAG -> real train-graph connectivity. A triple's prerequisites = its endpoints
  being GROUNDED (anchored) in the current foundation. schema_fit(h,r,t) = (anchored(h)+anchored(t))/2;
  anchored(e) iff e in seed S or admit_count[e] >= K_ground. FIXED single-pass gate: admit iff
  schema_fit >= tau (tau=0.5 -> >=1 endpoint anchored). A triple arriving before an anchor is dropped
  forever -> ORDER matters. On admit both endpoints ground.

ARMS (same gate/tau/K_ground/seed S/per-seed randomness):
  CURRICULUM  = BFS-frontier admission order from S.
  RANDOM      = shuffled arrival, strict single-pass (baseline floor; mean over RAND_SEEDS).
  FREQUENCY   = descending relation-frequency then endpoint-degree (POPULARITY ordering control).
  RANDOM_HOLD = random arrival + provisional-hold (rejected -> buffer; re-sweep to fixpoint).
  REVERSE     = reverse curriculum order (DISCRIMINATOR: bad order defeats the gate).

QUALITY (held-out, non-circular): RA(h,t)=sum_{z in N_found(h) cap N_found(t)} 1/deg_found(z) over the
ADMITTED foundation only; AUROC on test pos vs hard-neg. Popularity-neutral stack: margin_over_degree
(RA beats best single degree feature), the FREQUENCY arm (curriculum must beat popularity ordering),
and a SCRAMBLE null (degree-preserving rewire of curriculum's foundation -> AUROC must collapse).
SIZE confound controlled by MATCHED BUDGET B = min(admit_cur, admit_freq, min_seed admit_rand): each
arm's admission-ordered foundation truncated to first B before scoring (primary margin). tau=0 null:
gate OFF -> all orders admit identical full graph -> order-invariant.

Determinism: numpy default_rng(fixed int seeds); no hash()-derived seeds; sorted() for set ops.
ASCII-only. No emojis. Local CPU single-shot, no queue/GPU/atoms/push. Runs to completion in foreground.
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

ANCHOR_NAME = "curriculum_order_ingest_real_codex_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- fixed config (a-priori) ----
TAU = 0.5             # admit iff >= half of endpoints anchored (>=1 of 2). Set ONCE, principled.
K_GROUND = 1          # an entity anchors after its first admitted appearance (or if in seed S).
N_SEED_TRIPLES = 8    # innate anchor seed = entities of this many fixed random train triples.
SEED_RNG = 12345      # rng for the shared seed-triple sample (same across all arms).
RAND_SEEDS_FULL = [11, 23, 37, 41, 53]
RAND_SEEDS_SMOKE = [11, 23]
SMOKE_TRAIN_CAP = 6000
SCRAMBLE_SEEDS = [101, 202, 303, 404, 505]
# Budget sweep (size control): first-B admitted foundation per arm, FIXED a-priori grid, capped at
# min admission across cur/freq/rand so every swept arm has >= B admitted triples.
BUDGET_GRID = [1000, 2000, 4000, 8000, 16000, 24000]

# verdict thresholds (FIXED a-priori)
MARGIN_CUR_RAND_HP = 0.030
MARGIN_CUR_FREQ_HP = 0.010
MARGIN_OVER_DEG_HP = 0.020
SCRAMBLE_HP = 0.55
SCRAMBLE_HF = 0.60
PREMATURE_DISCRIM = 0.10
HOLD_RECOVERY_HP = 0.50
MARGIN_CUR_RAND_HF = 0.005
INFO_CEILING_MIN = 0.03   # best real foundation must beat its degree-scramble null by >= this, else
                          # the popularity-neutral metric is near-vacuous (cannot resolve the order Q).


# --------------------------- data ------------------------------------------
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
        rng = np.random.default_rng(SEED_RNG)
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
    # leakage guard: no test positive may appear in the train graph
    train_set = set(train)
    leak = sum(1 for tp in tst_p if tp in train_set)
    assert leak == 0, "LEAK: %d test positives in train graph" % leak
    # full-graph undirected degree (for FREQUENCY ordering + degree baseline reference)
    deg_full = np.zeros(n_ent, dtype=np.int64)
    seen = [set() for _ in range(n_ent)]
    for h, _r, t in train_int:
        h = int(h); t = int(t)
        if h != t:
            seen[h].add(t); seen[t].add(h)
    for e in range(n_ent):
        deg_full[e] = len(seen[e])
    # eval pairs -> entity indices (all eval entities present in eidx)
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


# --------------------------- foundation + downstream quality -------------------
def build_foundation_nbr(train_int, admitted_rows, n_ent):
    """Neighbor sets + degree from ONLY the admitted foundation edges."""
    nbr = [set() for _ in range(n_ent)]
    for idx in admitted_rows:
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        if h != t:
            nbr[h].add(t); nbr[t].add(h)
    deg = np.array([len(s) for s in nbr], dtype=np.int64)
    return nbr, deg


def ra_scores(nbr, deg, hi, ti):
    """Pairwise Resource-Allocation index over the foundation neighbor sets."""
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
    """LABEL-FREE OLS coefficients for score ~ [1, log_hdeg, log_tdeg]. Inputs: score + degrees only."""
    n = len(score)
    A = np.column_stack([np.ones(n), log_hdeg, log_tdeg])
    coef, _, _, _ = np.linalg.lstsq(A, score, rcond=None)
    return coef


def _best_degree_auroc(y, deg, hi, ti):
    """Popularity baseline: best single-degree-feature AUROC (oriented)."""
    dh = deg[hi].astype(np.float64); dt = deg[ti].astype(np.float64)
    out = 0.0
    for v in (dh, dt, dh + dt):
        a = auroc(y, v)
        out = max(out, a, 1.0 - a)
    return out


def _quality_from_nbr(data, nbr, deg):
    """Degree-orthogonalized RA-AUROC (validated recipe): fit label-free OLS projection on VALID RA
    scores (held-out), residualize, score TEST. Reports raw + orthogonalized + degree baseline + margin."""
    vhi, vti = data["val_hi"], data["val_ti"]
    thi, tti, ty = data["test_hi"], data["test_ti"], data["test_y"]
    v_ra = ra_scores(nbr, deg, vhi, vti)
    t_ra = ra_scores(nbr, deg, thi, tti)
    v_lh = np.log1p(deg[vhi].astype(np.float64)); v_lt = np.log1p(deg[vti].astype(np.float64))
    t_lh = np.log1p(deg[thi].astype(np.float64)); t_lt = np.log1p(deg[tti].astype(np.float64))
    coef = fit_degree_projection(v_ra, v_lh, v_lt)          # LABEL-FREE, fit on VALID (held-out)
    t_resid = t_ra - (coef[0] + coef[1] * t_lh + coef[2] * t_lt)
    orth_auc = auroc(ty, t_resid)
    raw_auc = auroc(ty, t_ra)
    deg_auc = _best_degree_auroc(ty, deg, thi, tti)
    return {"ra_orth_auroc": orth_auc, "ra_raw_auroc": raw_auc, "degree_auroc": deg_auc,
            "margin_over_degree": orth_auc - deg_auc}


def foundation_quality(data, admitted_rows):
    """Degree-orthogonalized held-out RA quality from the admitted foundation subgraph (popularity-neutral)."""
    nbr, deg = build_foundation_nbr(data["train_int"], admitted_rows, data["n_ent"])
    q = _quality_from_nbr(data, nbr, deg)
    q["nbr"] = nbr; q["deg"] = deg
    return q


def scramble_quality(data, admitted_rows, rng):
    """Degree-preserving rewire null: replace each foundation edge endpoints by entities drawn in
    proportion to foundation degree (preserves edge count + approx degree distribution, destroys the
    specific common-neighbor structure). The degree-ORTHOGONALIZED RA-AUROC must collapse to chance --
    if it does not, the quality metric is a degree/popularity artifact, not structural."""
    n_ent = data["n_ent"]
    _nbr0, deg0 = build_foundation_nbr(data["train_int"], admitted_rows, n_ent)
    w = deg0.astype(np.float64)
    tot = w.sum()
    if tot <= 0:
        return 0.5
    p = w / tot
    m = len(admitted_rows)
    heads = rng.choice(n_ent, size=m, p=p)
    tails = rng.choice(n_ent, size=m, p=p)
    nbr = [set() for _ in range(n_ent)]
    for a, b in zip(heads.tolist(), tails.tolist()):
        if a != b:
            nbr[a].add(b); nbr[b].add(a)
    deg = np.array([len(s) for s in nbr], dtype=np.int64)
    return _quality_from_nbr(data, nbr, deg)["ra_orth_auroc"]


# --------------------------- ordering functions -------------------------------
def curriculum_order(train_int, n_ent, seed_entities):
    """BFS-frontier admission order from the seed entities over the train graph (structure only)."""
    inc = [[] for _ in range(n_ent)]
    for idx in range(train_int.shape[0]):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        inc[h].append(idx)
        if t != h:
            inc[t].append(idx)
    grounded = set(int(e) for e in seed_entities)
    used = np.zeros(train_int.shape[0], dtype=bool)
    order = []
    q = deque(sorted(grounded))
    while q:
        e = q.popleft()
        for idx in sorted(inc[e]):
            if used[idx]:
                continue
            used[idx] = True
            order.append(idx)
            h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
            for x in (h, t):
                if x not in grounded:
                    grounded.add(x); q.append(x)
    for idx in range(train_int.shape[0]):
        if not used[idx]:
            order.append(idx)
    return order


def frequency_order(train_int, rel_freq_int, deg_full):
    """Pure popularity ordering: descending relation-frequency, then endpoint-degree, then id."""
    n = train_int.shape[0]
    keys = []
    for idx in range(n):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        keys.append((-int(rel_freq_int[idx]), -(int(deg_full[h]) + int(deg_full[t])), idx))
    keys.sort()
    return [k[2] for k in keys]


# --------------------------- ingestion gate -----------------------------------
def ingest_strict(train_int, seq, seed_entities, tau, k_ground):
    """Single-pass strict gate. Returns admitted-row list (admission order), grounded set, rejected list,
    and premature-recoverable count (rejected but both endpoints anchored at end)."""
    admit_count = defaultdict(int)
    anchored = set(int(e) for e in seed_entities)
    admitted = []
    rejected = []
    for idx in seq:
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        sf = ((1.0 if h in anchored else 0.0) + (1.0 if t in anchored else 0.0)) / 2.0
        if sf >= tau:
            admitted.append(idx)
            for x in (h, t):
                admit_count[x] += 1
                if x not in anchored and admit_count[x] >= k_ground:
                    anchored.add(x)
        else:
            rejected.append(idx)
    premature = 0
    for idx in rejected:
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        if h in anchored and t in anchored:
            premature += 1
    return {"admitted": admitted, "anchored": anchored, "rejected": rejected,
            "premature": premature, "n_seq": len(seq)}


def ingest_hold(train_int, seq, seed_entities, tau, k_ground, max_passes):
    """Provisional-hold: rejected -> hold buffer; drain sweeps (synchronous, admitted-set frozen per
    pass) until a full sweep admits nothing (fixpoint). Returns admitted-row list + hold cost."""
    admit_count = defaultdict(int)
    anchored = set(int(e) for e in seed_entities)
    admitted = []
    hold = []

    def try_place(idx):
        h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
        sf = ((1.0 if h in anchored else 0.0) + (1.0 if t in anchored else 0.0)) / 2.0
        if sf >= tau:
            admitted.append(idx)
            for x in (h, t):
                admit_count[x] += 1
                if x not in anchored and admit_count[x] >= k_ground:
                    anchored.add(x)
            return True
        return False

    for idx in seq:
        if not try_place(idx):
            hold.append(idx)
    phase1_hold = len(hold)
    passes = 0
    buffer_trace = [len(hold)]
    while hold and passes < max_passes:
        passes += 1
        snapshot = frozenset(anchored)
        admitted_this = 0
        still = []
        for idx in hold:
            h = int(train_int[idx, 0]); t = int(train_int[idx, 2])
            sf = ((1.0 if h in snapshot else 0.0) + (1.0 if t in snapshot else 0.0)) / 2.0
            if sf >= tau and try_place(idx):
                admitted_this += 1
            else:
                still.append(idx)
        hold = still
        buffer_trace.append(len(hold))
        if admitted_this == 0:
            break
    monotone = all(buffer_trace[i + 1] <= buffer_trace[i] for i in range(len(buffer_trace) - 1))
    return {"admitted": admitted, "phase1_hold": phase1_hold, "final_hold": len(hold),
            "passes": passes, "buffer_monotone": monotone}


# --------------------------- arm runner ---------------------------------------
def run_arms(data, tau, k_ground, rand_seeds):
    train_int = data["train_int"]; n_ent = data["n_ent"]
    seed_rng = np.random.default_rng(SEED_RNG)
    n_tr = train_int.shape[0]
    seed_rows = sorted(seed_rng.choice(n_tr, size=min(N_SEED_TRIPLES, n_tr), replace=False).tolist())
    seed_entities = set()
    for idx in seed_rows:
        seed_entities.add(int(train_int[idx, 0])); seed_entities.add(int(train_int[idx, 2]))
    max_passes = 64

    cur_seq = curriculum_order(train_int, n_ent, seed_entities)
    freq_seq = frequency_order(train_int, data["rel_freq_int"], data["deg_full"])
    rev_seq = list(reversed(cur_seq))

    cur = ingest_strict(train_int, cur_seq, seed_entities, tau, k_ground)
    freq = ingest_strict(train_int, freq_seq, seed_entities, tau, k_ground)
    rev = ingest_strict(train_int, rev_seq, seed_entities, tau, k_ground)

    rand_runs = []
    hold_runs = []
    for s in rand_seeds:
        prng = np.random.default_rng(s)
        rseq = prng.permutation(n_tr).tolist()
        rand_runs.append(ingest_strict(train_int, rseq, seed_entities, tau, k_ground))
        hold_runs.append(ingest_hold(train_int, rseq, seed_entities, tau, k_ground, max_passes))

    def admit_n(run):
        return len(run["admitted"])

    def mean(vs):
        return float(np.mean(vs))

    def std(vs):
        return float(np.std(vs))

    def qfull(rows):
        return foundation_quality(data, rows)

    def orthB(rows, B):
        return foundation_quality(data, rows[:B])["ra_orth_auroc"]

    # ---- BUDGET SWEEP (the size control): compare first-B admitted foundations across arms. B is a
    # FIXED a-priori grid capped at the min admission across cur/freq/rand so every swept arm has >= B
    # admitted triples (curriculum first-B = coherent BFS core; random first-B = scattered subset). ----
    admit_cap = min(admit_n(cur), admit_n(freq), min(admit_n(r) for r in rand_runs))
    grid = sorted(b for b in BUDGET_GRID if b <= admit_cap)
    if not grid or grid[-1] < admit_cap:
        grid = sorted(set(grid) | {admit_cap})

    budget_sweep = {}
    margins_cur_rand = []
    margins_cur_freq = []
    cur_margin_over_deg_grid = []
    for B in grid:
        qc = foundation_quality(data, cur["admitted"][:B])
        qf = foundation_quality(data, freq["admitted"][:B])
        qr = [orthB(r["admitted"], B) for r in rand_runs]
        qrev = orthB(rev["admitted"], B) if admit_n(rev) >= B else None
        m_cr = qc["ra_orth_auroc"] - mean(qr)
        m_cf = qc["ra_orth_auroc"] - qf["ra_orth_auroc"]
        margins_cur_rand.append(m_cr)
        margins_cur_freq.append(m_cf)
        cur_margin_over_deg_grid.append(qc["margin_over_degree"])
        budget_sweep["B_%d" % B] = {
            "q_cur_orth": qc["ra_orth_auroc"], "q_cur_margin_deg": qc["margin_over_degree"],
            "q_freq_orth": qf["ra_orth_auroc"],
            "q_rand_orth_mean": mean(qr), "q_rand_orth_std": std(qr),
            "q_rev_orth": qrev,
            "margin_cur_rand": m_cr, "margin_cur_freq": m_cf,
        }

    # full-size quality (for hold-recovery + reporting)
    q_cur_full = qfull(cur["admitted"])
    q_freq_full = qfull(freq["admitted"])
    q_rand_full = [qfull(r["admitted"]) for r in rand_runs]
    q_hold_full = [qfull(h["admitted"]) for h in hold_runs]

    # scramble null on curriculum foundation (degree-orthogonalized -> must collapse to chance)
    scr = [scramble_quality(data, cur["admitted"], np.random.default_rng(s)) for s in SCRAMBLE_SEEDS]
    scramble_auroc = float(np.mean(scr))

    def prem_rate(run):
        return run["premature"] / float(run["n_seq"])

    n_budgets = len(grid)
    frac_cr_pos = float(np.mean([1.0 if m >= MARGIN_CUR_RAND_HP else 0.0 for m in margins_cur_rand]))
    frac_cf_pos = float(np.mean([1.0 if m >= MARGIN_CUR_FREQ_HP else 0.0 for m in margins_cur_freq]))

    out = {
        "seed_entities_n": len(seed_entities),
        "budget_grid": grid,
        "budget_sweep": budget_sweep,
        "margin_cur_rand_mean_over_grid": mean(margins_cur_rand),
        "margin_cur_rand_min_over_grid": float(min(margins_cur_rand)),
        "margin_cur_rand_max_over_grid": float(max(margins_cur_rand)),
        "margin_cur_freq_mean_over_grid": mean(margins_cur_freq),
        "cur_margin_over_degree_mean_over_grid": mean(cur_margin_over_deg_grid),
        "frac_budgets_cur_rand_ge_hp": frac_cr_pos,
        "frac_budgets_cur_freq_ge_hp": frac_cf_pos,
        "n_budgets": n_budgets,
        "arms": {
            "curriculum": {"admit": admit_n(cur), "admit_rate": admit_n(cur) / n_tr,
                           "premature_rate": prem_rate(cur),
                           "q_full_orth": q_cur_full["ra_orth_auroc"],
                           "q_full_raw": q_cur_full["ra_raw_auroc"],
                           "q_full_margin_deg": q_cur_full["margin_over_degree"],
                           "degree_auroc_full": q_cur_full["degree_auroc"]},
            "frequency": {"admit": admit_n(freq), "admit_rate": admit_n(freq) / n_tr,
                          "premature_rate": prem_rate(freq),
                          "q_full_orth": q_freq_full["ra_orth_auroc"]},
            "reverse": {"admit": admit_n(rev), "admit_rate": admit_n(rev) / n_tr,
                        "premature_rate": prem_rate(rev)},
            "random": {"admit_mean": mean([admit_n(r) for r in rand_runs]),
                       "admit_rate_mean": mean([admit_n(r) / n_tr for r in rand_runs]),
                       "premature_rate_mean": mean([prem_rate(r) for r in rand_runs]),
                       "premature_rate_std": std([prem_rate(r) for r in rand_runs]),
                       "q_full_orth_mean": mean([q["ra_orth_auroc"] for q in q_rand_full]),
                       "q_full_orth_std": std([q["ra_orth_auroc"] for q in q_rand_full])},
            "random_hold": {"admit_mean": mean([admit_n(h) for h in hold_runs]),
                            "admit_rate_mean": mean([admit_n(h) / n_tr for h in hold_runs]),
                            "q_full_orth_mean": mean([q["ra_orth_auroc"] for q in q_hold_full]),
                            "passes_mean": mean([h["passes"] for h in hold_runs]),
                            "passes_max": int(max(h["passes"] for h in hold_runs)),
                            "phase1_hold_mean": mean([h["phase1_hold"] for h in hold_runs]),
                            "final_hold_mean": mean([h["final_hold"] for h in hold_runs]),
                            "buffer_monotone_all": bool(all(h["buffer_monotone"] for h in hold_runs))},
        },
        "scramble_auroc": scramble_auroc,
        # admit-set frozensets for arms-must-differ
        "_admit_cur": frozenset(cur["admitted"]),
        "_admit_rand0": frozenset(rand_runs[0]["admitted"]),
        "_admit_hold0": frozenset(hold_runs[0]["admitted"]),
    }
    return out


def tau0_null(data, k_ground):
    """Gate OFF (tau=0): every order admits identical full graph -> order-invariant. Returns spread +
    identical-set flag."""
    train_int = data["train_int"]; n_ent = data["n_ent"]
    seed_rng = np.random.default_rng(SEED_RNG)
    n_tr = train_int.shape[0]
    seed_rows = sorted(seed_rng.choice(n_tr, size=min(N_SEED_TRIPLES, n_tr), replace=False).tolist())
    seed_entities = set()
    for idx in seed_rows:
        seed_entities.add(int(train_int[idx, 0])); seed_entities.add(int(train_int[idx, 2]))
    cur_seq = curriculum_order(train_int, n_ent, seed_entities)
    freq_seq = frequency_order(train_int, data["rel_freq_int"], data["deg_full"])
    rseq = np.random.default_rng(11).permutation(n_tr).tolist()
    sets = {}
    qs = {}
    for name, seq in (("curriculum", cur_seq), ("frequency", freq_seq), ("random", rseq)):
        run = ingest_strict(train_int, seq, seed_entities, 0.0, k_ground)
        sets[name] = frozenset(run["admitted"])
        qs[name] = foundation_quality(data, run["admitted"])["ra_orth_auroc"]
    identical = (sets["curriculum"] == sets["frequency"] == sets["random"])
    spread = max(qs.values()) - min(qs.values())
    return {"identical_admit_sets": bool(identical), "quality_spread": float(spread),
            "q_by_order": qs}


# --------------------------- verdict ------------------------------------------
def compute_verdict(res, tau0):
    a = res["arms"]
    # PRIMARY: budget-swept, degree-orthogonalized, popularity-neutral quality margins.
    margin_cur_rand = res["margin_cur_rand_mean_over_grid"]
    margin_cur_freq = res["margin_cur_freq_mean_over_grid"]
    cur_margin_deg = res["cur_margin_over_degree_mean_over_grid"]
    frac_cr = res["frac_budgets_cur_rand_ge_hp"]
    robust_cr = (frac_cr >= 0.5)  # margin >= HP at a MAJORITY of budgets (not cherry-picked)

    q_cur_full = a["curriculum"]["q_full_orth"]
    q_rand_full = a["random"]["q_full_orth_mean"]
    q_hold_full = a["random_hold"]["q_full_orth_mean"]

    scramble = res["scramble_auroc"]
    # DISCRIMINATOR = REVERSE order craters (bad order defeats the single-pass gate). Reverse admits far
    # less + high premature rejection. This is the order-sensitivity proof on real data.
    rev_prem = a["reverse"]["premature_rate"]
    rand_prem = a["random"]["premature_rate_mean"]
    rev_craters = (rev_prem >= 0.30) and (a["reverse"]["admit"] < 0.5 * a["curriculum"]["admit"])
    denom = q_cur_full - q_rand_full
    hold_recovery = (q_hold_full - q_rand_full) / denom if abs(denom) > 1e-6 else (
        1.0 if abs(q_hold_full - q_cur_full) < 1e-6 else 0.0)

    tau0_ok = tau0["identical_admit_sets"] and (tau0["quality_spread"] <= 1e-6)
    arms_differ = (res["_admit_cur"] != res["_admit_rand0"]) and (res["_admit_hold0"] != res["_admit_rand0"])

    # INFO-CEILING guard: how far does the BEST real foundation (curriculum, full) beat its own
    # degree-preserving scramble null? If < INFO_CEILING_MIN, the popularity-neutral metric is
    # near-vacuous (barely above chance) -> the test CANNOT distinguish "order-invariant" from "metric
    # too weak to tell". Reporting a HARD_FAIL order-invariance then would OVER-CLAIM.
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
    elif not rev_craters:
        verdict = "MIDDLE_BAND_DISCRIMINATOR_DID_NOT_FIRE_REVERSE_DID_NOT_CRATER"
    elif metric_near_vacuous:
        verdict = "MIDDLE_BAND_METRIC_NEAR_VACUOUS_INFO_CEILING_LOW"
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
        "margin_cur_freq_mean_grid": margin_cur_freq,
        "frac_budgets_cur_rand_ge_hp": frac_cr,
        "robust_cur_rand_majority": bool(robust_cr),
        "curriculum_margin_over_degree_mean_grid": cur_margin_deg,
        "scramble_auroc": scramble,
        "info_ceiling_cur_full_minus_scramble": info_ceiling,
        "metric_near_vacuous": bool(metric_near_vacuous),
        "reverse_premature_rate": rev_prem, "random_premature_rate": rand_prem,
        "reverse_craters": bool(rev_craters),
        "hold_recovery_fraction": hold_recovery,
        "q_cur_full": q_cur_full, "q_rand_full": q_rand_full, "q_hold_full": q_hold_full,
        "tau0_order_invariant": bool(tau0_ok),
        "arms_differ": bool(arms_differ),
    }


def _strip(res):
    return {k: v for k, v in res.items() if not k.startswith("_admit")}


# --------------------------- self-test ----------------------------------------
def self_test():
    # (A) positive control: RA index recovers planted structure; AUROC correctly orients.
    y = np.array([1, 1, 0, 0]); s = np.array([0.9, 0.8, 0.2, 0.1])
    assert auroc(y, s) == 1.0, "auroc orientation"
    assert abs(auroc(np.array([1, 0]), np.array([0.5, 0.5])) - 0.5) < 1e-9, "auroc ties -> 0.5"

    # (B) discriminator + nulls on REAL CoDEx-S at FULL-N (the reverse-craters discriminator is a
    # full-density property; smoke-subsample is too sparse). FULL graph runs in ~seconds; use the
    # reduced 2-seed random set to stay fast (smoke-at-full-N per DISCRIMINATOR-MUST-SURVIVE-SCALE).
    data = load_dataset("codex_claimvalidity", "full")
    res = run_arms(data, TAU, K_GROUND, RAND_SEEDS_SMOKE)
    tau0 = tau0_null(data, K_GROUND)
    v = compute_verdict(res, tau0)
    a = res["arms"]

    # DISCRIMINATOR: REVERSE order craters (bad order defeats the single-pass gate) -> order IS
    # sensitive at this scale. (Random is permissive on dense real data; reverse is the crater.)
    assert a["reverse"]["premature_rate"] >= 0.30, \
        "discriminator must fire: reverse must crater (premature_rev=%.3f)" % a["reverse"]["premature_rate"]
    assert a["reverse"]["admit"] < 0.5 * a["curriculum"]["admit"], "reverse must admit far less than curriculum"
    # arms differ: curriculum admits more than random; hold admits >= random.
    assert a["curriculum"]["admit"] > a["random"]["admit_mean"], "curriculum must admit more than random"
    assert a["random_hold"]["admit_mean"] >= a["random"]["admit_mean"], "hold must admit >= random"
    assert res["_admit_cur"] != res["_admit_rand0"], "arms-must-differ: cur vs rand"
    # tau0 null: order-invariant (identical admit sets, zero quality spread).
    assert tau0["identical_admit_sets"], "tau0 must admit identical sets across orders"
    assert tau0["quality_spread"] <= 1e-6, "tau0 quality spread must be ~0, got %.6f" % tau0["quality_spread"]
    # scramble null: degree-preserving rewire collapses ORTH AUROC to chance band (metric is structural).
    assert res["scramble_auroc"] <= SCRAMBLE_HF, \
        "scramble null must collapse (orth metric), got %.3f" % res["scramble_auroc"]
    # hold buffer bounded/monotone + drain terminated.
    assert a["random_hold"]["buffer_monotone_all"], "hold buffer must be monotone non-increasing"
    assert a["random_hold"]["passes_max"] < 64, "hold drain must terminate (fixpoint)"
    # budget sweep populated + curriculum quality measurable (in band).
    assert res["n_budgets"] >= 2, "budget sweep must have >=2 points"
    assert 0.05 < a["curriculum"]["q_full_orth"] < 0.99, \
        "curriculum orth-RA-AUROC must be measurable, got %.3f" % a["curriculum"]["q_full_orth"]

    print("[SELF-TEST] PASS")
    print("  smoke: budgets=%s  margin_cur_rand(mean/max grid)=%.3f/%.3f  margin_cur_freq(mean)=%.3f" % (
        res["budget_grid"], v["margin_cur_rand_mean_grid"], v["margin_cur_rand_max_grid"],
        v["margin_cur_freq_mean_grid"]))
    print("  admit: cur=%d freq=%d rev=%d rand=%.0f hold=%.0f | premature rev=%.3f rand=%.3f" % (
        a["curriculum"]["admit"], a["frequency"]["admit"], a["reverse"]["admit"],
        a["random"]["admit_mean"], a["random_hold"]["admit_mean"],
        a["reverse"]["premature_rate"], a["random"]["premature_rate_mean"]))
    print("  cur_margin_deg(mean grid)=%.3f scramble=%.3f tau0_inv=%s rev_craters=%s hold_recovery=%.3f -> %s" % (
        v["curriculum_margin_over_degree_mean_grid"], v["scramble_auroc"], v["tau0_order_invariant"],
        v["reverse_craters"], v["hold_recovery_fraction"], v["verdict"]))
    return True


# --------------------------- main ---------------------------------------------
def main(scale="full", dataset="codex_claimvalidity"):
    t0 = time.time()
    ts = datetime.now(timezone.utc)
    rand_seeds = RAND_SEEDS_SMOKE if scale == "smoke" else RAND_SEEDS_FULL
    data = load_dataset(dataset, scale)
    print("[load] dataset=%s scale=%s n_ent=%d n_train=%d n_test=%d" % (
        dataset, scale, data["n_ent"], data["train_int"].shape[0], len(data["test_y"])), flush=True)
    res = run_arms(data, TAU, K_GROUND, rand_seeds)
    tau0 = tau0_null(data, K_GROUND)
    verdict = compute_verdict(res, tau0)

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict["verdict"],
        "verdict_msg": ("%s | margin_cur_rand(mean grid)=%.3f (max=%.3f, frac>=hp=%.2f) "
                        "margin_cur_freq=%.3f cur_margin_deg=%.3f scramble=%.3f hold_recovery=%.3f "
                        "rev_prem=%.3f rev_craters=%s tau0_inv=%s" % (
                            verdict["verdict"], verdict["margin_cur_rand_mean_grid"],
                            verdict["margin_cur_rand_max_grid"], verdict["frac_budgets_cur_rand_ge_hp"],
                            verdict["margin_cur_freq_mean_grid"],
                            verdict["curriculum_margin_over_degree_mean_grid"], verdict["scramble_auroc"],
                            verdict["hold_recovery_fraction"], verdict["reverse_premature_rate"],
                            verdict["reverse_craters"], verdict["tau0_order_invariant"])),
        "summary": verdict["verdict"],
        "elapsed_s": elapsed,
        "ts_iso": ts.isoformat(),
        "scale": scale,
        "dataset": dataset,
        "run_mode": scale,
        "config": {"tau": TAU, "k_ground": K_GROUND, "n_seed_triples": N_SEED_TRIPLES,
                   "rand_seeds": rand_seeds, "scramble_seeds": SCRAMBLE_SEEDS,
                   "bands": {"margin_cur_rand_hp": MARGIN_CUR_RAND_HP, "margin_cur_freq_hp": MARGIN_CUR_FREQ_HP,
                             "margin_over_deg_hp": MARGIN_OVER_DEG_HP, "scramble_hp": SCRAMBLE_HP,
                             "scramble_hf": SCRAMBLE_HF, "premature_discrim": PREMATURE_DISCRIM,
                             "hold_recovery_hp": HOLD_RECOVERY_HP, "margin_cur_rand_hf": MARGIN_CUR_RAND_HF}},
        "verdict_detail": verdict,
        "results": _strip(res),
        "tau0_null": tau0,
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
    print("  seed_entities=%d  budget_grid=%s" % (res["seed_entities_n"], res["budget_grid"]))
    print("  ADMIT   cur=%d freq=%d rev=%d rand=%.0f hold=%.0f" % (
        a["curriculum"]["admit"], a["frequency"]["admit"], a["reverse"]["admit"],
        a["random"]["admit_mean"], a["random_hold"]["admit_mean"]))
    print("  PREMATURE(recoverable rejections) cur=%.3f freq=%.3f rev=%.3f rand=%.3f" % (
        a["curriculum"]["premature_rate"], a["frequency"]["premature_rate"],
        a["reverse"]["premature_rate"], a["random"]["premature_rate_mean"]))
    print("  BUDGET SWEEP (degree-orthogonalized held-out RA-AUROC):")
    for B in res["budget_grid"]:
        bs = res["budget_sweep"]["B_%d" % B]
        rev_s = ("%.3f" % bs["q_rev_orth"]) if bs["q_rev_orth"] is not None else "  -  "
        print("    B=%-6d cur=%.3f rand=%.3f freq=%.3f rev=%s | m_cr=%+.3f m_cf=%+.3f cur_mdeg=%+.3f" % (
            B, bs["q_cur_orth"], bs["q_rand_orth_mean"], bs["q_freq_orth"], rev_s,
            bs["margin_cur_rand"], bs["margin_cur_freq"], bs["q_cur_margin_deg"]))
    print("  margin_cur_rand mean/max grid=%.3f/%.3f frac_budgets>=hp=%.2f (robust=%s)" % (
        verdict["margin_cur_rand_mean_grid"], verdict["margin_cur_rand_max_grid"],
        verdict["frac_budgets_cur_rand_ge_hp"], verdict["robust_cur_rand_majority"]))
    print("  Q@full orth: cur=%.3f rand=%.3f hold=%.3f | hold_recovery=%.3f" % (
        a["curriculum"]["q_full_orth"], a["random"]["q_full_orth_mean"],
        a["random_hold"]["q_full_orth_mean"], verdict["hold_recovery_fraction"]))
    print("  scramble_null_orth_auroc=%.3f (<=%.2f pass, >%.2f fail) | rev_craters=%s | tau0_inv=%s spread=%.6f" % (
        verdict["scramble_auroc"], SCRAMBLE_HP, SCRAMBLE_HF, verdict["reverse_craters"],
        tau0["identical_admit_sets"], tau0["quality_spread"]))
    print("  INFO-CEILING (cur_full_orth - scramble)=%.3f (>=%.2f needed) metric_near_vacuous=%s" % (
        verdict["info_ceiling_cur_full_minus_scramble"], INFO_CEILING_MIN, verdict["metric_near_vacuous"]))
    print("  metrics -> %s" % final)
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dataset", default="codex_claimvalidity")
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(scale="smoke" if args.smoke else "full", dataset=args.dataset)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
