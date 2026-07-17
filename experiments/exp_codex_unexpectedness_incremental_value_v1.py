# UNEXPECTEDNESS (schema-conditioned prediction-error) INCREMENTAL VALUE on real CoDEx claim-validity.
#
# THE LAST UNTESTED INGEST SIGNAL ON REAL DATA. The 4-signal ingest gate's real-data scorecard so far:
# schema-fit WON (degree-orthogonal pairwise structural overlap beats a degree-matched freq baseline on
# novel claims); recurrence validated; importance LOW-VALUE (HARD_FAIL_IMPORTANCE_AXIS_DOES_NOT_TRANSFER).
# The FIRST signal -- UNEXPECTEDNESS = LOCAL schema-conditioned prediction-error (does the current partial
# foundation PREDICT this (s,r,o)? the residual = unexpectedness = -log P(fact | foundation), KL(post||prior),
# NOT a global frequency rank) -- was NEVER tested on real data. This cell tests it, PROPERLY FRAMED.
#
# FRAMING (load-bearing honesty): unexpectedness is NOT a standalone validity predictor -- a highly-unexpected
# fact can be novel-TRUE or false-NOISE (both unexpected). Its arena role is a COMPONENT of the branch/route
# (novelty-gating, paired with schema-fit). So the RIGHT question is NON-REDUNDANT INCREMENTAL VALUE:
#   Does adding schema-conditioned-PE to {schema-fit + recurrence} improve claim-validity discrimination
#   BEYOND what {schema-fit + recurrence} give alone, degree/popularity-neutral?
# It may be REDUNDANT (schema-fit already captures schema-consistency; PE ~ -predictability ~ -schema-fit) OR
# it may add relation-conditioned novelty value. FOLLOW THE EVIDENCE.
#
# OPERATIONALIZATION of UNEXPECTEDNESS on CoDEx = the arena's -log P(topic_t | topic_{t-1}) forward-model PE,
# transferred to a static KG as a RELATION-CONDITIONED community-transition prediction error:
#   1. communities: deterministic asynchronous label-propagation on the undirected TRAIN graph (the
#      foundation's schema), coarsened to top-C communities + an "other" bucket.
#   2. per-relation forward model: P(c_t | c_h, r) = Laplace-smoothed community-transition counts from TRAIN.
#   3. unexpectedness(h,r,t) = -log P(c_t | c_h, r)  = schema-conditioned prediction error of the foundation's
#      relation-typed forward model. LOCAL (uses the train graph structure), RELATION-CONDITIONED and
#      DIRECTED -- the axis that symmetric structural schema-fit/recurrence MISS. Higher = more surprising.
# This is faithful to the consolidation-note definition (local schema-conditioned PE, not a global anomaly rank)
# and is the potential source of NON-REDUNDANCY: a pair can be structurally well-connected (high schema-fit)
# yet the SPECIFIC relation r maps h's community to a DIFFERENT target community, making t unexpected.
#
# schema-fit  = degree-orthogonal pairwise Resource-Allocation index (the VET-confirmed real-data win). Symmetric.
# recurrence  = corroboration DIVERSITY: number of DISTINCT relation types among the common-neighbor paths
#               connecting (h,t) in train (independent lines of relational evidence; count not magnitude ->
#               distinct from RA's degree-weighted overlap). Degree-orthogonalized.
# ALL THREE signals are degree-orthogonalized held-out label-free (fit projection on VAL-matched, apply to TEST-
# matched) exactly as the VET'd schema-fit chassis (exp_codex_claimvalidity_degree_orthogonal_schemafit_v2).
#
# INCREMENTAL-VALUE TEST (per matched caliper, on held-out TEST claim-validity):
#   AUC_base = logistic{sf_orth, rec_orth}          fit VAL-matched -> eval TEST-matched
#   AUC_full = logistic{sf_orth, rec_orth, unexp_orth}
#   delta    = AUC_full - AUC_base                  (does the gate get BETTER)
#   partial  = AUROC(truth, residual of unexp_orth after OLS on [sf_orth,rec_orth], label-free) polarity-agnostic
#              (UNIQUE VARIANCE: unexp's conditional signal AFTER removing schema-fit + recurrence)
#   redundancy = R^2 of unexp_orth ~ [1, sf_orth, rec_orth]  (how much of unexp is already captured)
#   SHUFFLED-UNEXP NULL: permute unexp within rows (train + test), refit full -> delta_null distribution;
#              real delta must beat the null p95 (guards against extra-feature / overfitting inflation).
#   degree-neutrality: unexp_unique above-chance AUROC survives degree re-residualization (deg_explained<max).
#   info-ceiling gate FIRST: sf_orth alone must reproduce its VET'd frontier (>=0.53) AND full model above
#              chance, else the incremental test is uninformative regardless of unexp.
#
# PRE-REG (a-priori, bands FIXED before run):
#   HARD_PASS (unexpectedness adds NON-REDUNDANT value; 1st signal load-bearing on real data) =
#       cert fires all calipers AND info-ceiling passes all calipers AND for ALL calipers:
#         partial_unexp_auroc >= 0.53 AND partial bootstrap p05 > 0.50 (unique variance beyond sf,rec) AND
#         delta >= +0.015 AND real-delta bootstrap p05 > shuffled-null delta p95 (real gate improvement) AND
#         degree-neutral (unexp_unique held-out deg_explained < 0.10).
#   HARD_FAIL (unexpectedness REDUNDANT / low-value; real gate is 2-signal = schema-fit + recurrence) =
#       cert + info-ceiling OK BUT (partial_unexp_auroc <= 0.51 with p95 <= 0.52) OR (delta <= +0.005) OR
#       (real delta NOT distinguishable from the shuffled-unexp null) at the base caliper.
#   MIDDLE = otherwise (some unique variance but small/unrobust delta; or partial in (0.51,0.53)).
#   INFO_CEILING_FAIL / SPLIT_NOT_FREQUENCY_BLIND = test uninformative (report, do not over-claim).
#
# If HARD_FAIL: HONEST -- this plus the importance HARD_FAIL would mean the real-data ingest gate is really
# TWO signals (schema-fit + recurrence), a load-bearing conclusion re: the 4-signal design + the
# all-signals-load-bearing LOCK. FLAG FOR USER (do NOT prune unilaterally).
#
# ASCII-only. Local CPU. Deterministic (fixed integer seeds; np.random.default_rng only; sorted selection;
# NO hash()-derived RNG). No queue/GPU/atoms/push. Single-shot local run-to-completion (NOT a queue dispatch),
# so runner start_marker/heartbeat gates do not apply; atomic tmp+os.replace metrics write, no bare except,
# SystemExit-first ordering, arms-differ check are present.
#
# CELL-TEMPLATE compliance (single-shot local, no queue):
# - arms_differ_verified: sf_orth vs rec_orth vs unexp_orth hashed distinct at run + self-test (META_RULE_AF)
# - final_metrics_atomicity: tmp_replace (os.replace) (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: signals are rank-AUROC over parameter-free structural scores; no noise-floor threshold
# - baseline_in_band: freq certificate lands in [0.45,0.55] BY DESIGN (escalation gate); signals in measurable band
# - discriminator-fires: SHUFFLED-unexp null delta MUST be ~0 (if the null ALSO improves, the test is broken)
# - all reported numbers MEASURED@ this cell's metrics.json (no hypothesized numbers in verdict)

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO)
from hdlab import reachability_audit as ra  # noqa: E402

RAW = os.path.join(REPO, "data", "codex_claimvalidity", "raw")
OUT_DIR = os.path.join(REPO, "data", "exp_codex_unexpectedness_incremental_value_v1")
RESULTS_PATH = os.path.join(OUT_DIR, "metrics.json")

# ---- pre-registered config (FIXED A-PRIORI) ----
CALIPERS = [0.15, 0.20, 0.25]
BASE_CAP = 0.20
SEEDS = [12345, 67890]
N_BOOT = 400
N_NULL = 300

# community forward-model config
C_MAX = 16            # spectral communities (balanced); isolated (train-degree-0) entities -> bucket C_MAX
LP_ALPHA = 1.0        # Laplace smoothing for P(c_t | c_h, r)
KM_ITERS = 25         # deterministic k-means iterations on the spectral embedding
KM_SEED = 0

# certificate band: frequency baseline is "at/near chance" iff AUROC in [0.45, 0.55]
FREQ_CHANCE_HI = 0.55
FREQ_CHANCE_LO = 0.45

# verdict thresholds (FIXED A-PRIORI)
PARTIAL_HARD_PASS = 0.53      # unique-variance AUROC of unexp AFTER sf,rec
PARTIAL_HARD_FAIL = 0.51      # at/below this (with p95<=0.52) => redundant
DELTA_HARD_PASS = 0.015       # incremental AUROC of full over base
DELTA_HARD_FAIL = 0.005       # at/below this => adds ~nothing
DEG_EXPLAINED_MAX = 0.10      # unexp_unique popularity-neutral iff < this fraction is degree
INFO_CEILING_SF_MIN = 0.53    # sf_orth alone must reproduce >= this (VET'd RA-orth ~0.60-0.63)
INFO_CEILING_FULL_MIN = 0.55  # full model must be above chance
BOOT_LO_PCT = 5.0
NULL_HI_PCT = 95.0


# --------------------------- metrics ------------------------------------------
def auroc(y, s):
    """Rank-AUROC with tie handling. y in {0,1}, s continuous. higher s => label 1."""
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


def auroc_pa(y, s):
    """Polarity-agnostic AUROC = max(auroc, 1-auroc). For unsigned unique-variance reads."""
    a = auroc(y, s)
    return max(a, 1.0 - a)


def logistic_fit(Xtr, ytr, steps=800, lr=0.3, l2=1e-3):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0) + 1e-9
    Z = (Xtr - mu) / sd
    n, d = Z.shape
    w = np.zeros(d)
    b = 0.0
    pos_w = (len(ytr) / max(2 * ytr.sum(), 1))
    neg_w = (len(ytr) / max(2 * (len(ytr) - ytr.sum()), 1))
    sw = np.where(ytr == 1, pos_w, neg_w)
    for _ in range(steps):
        p = 1.0 / (1.0 + np.exp(-(Z @ w + b)))
        g = (p - ytr) * sw
        gw = Z.T @ g / n + l2 * w
        gb = g.mean()
        w -= lr * gw
        b -= lr * gb
    return w, b, mu, sd


def logistic_score(X, w, b, mu, sd):
    Z = (X - mu) / sd
    return 1.0 / (1.0 + np.exp(-(Z @ w + b)))


# --------------------------- degree-orthogonalization (LABEL-FREE) -------------
def fit_projection(target, cols):
    """OLS coefficients for target ~ [1, *cols]. LABEL-FREE: inputs are the score + regressors only."""
    n = len(target)
    A = np.column_stack([np.ones(n)] + list(cols))
    coef, _, _, _ = np.linalg.lstsq(A, target, rcond=None)
    return coef


def apply_projection(coef, target, cols):
    """Residual = target - (c0 + sum_k c_{k+1}*cols[k])."""
    pred = coef[0] + sum(coef[k + 1] * c for k, c in enumerate(cols))
    return target - pred


def r_squared(target, cols):
    """R^2 of OLS target ~ [1,*cols]."""
    coef = fit_projection(target, cols)
    resid = apply_projection(coef, target, cols)
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((target - target.mean()) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 0.0


# --------------------------- communities (deterministic spectral k-means) ------
def _kmeans_deterministic(X, k, iters, seed):
    """Deterministic k-means. Init = farthest-first (k-means++ maximal, no randomness): first centroid = the
    highest-norm point; each next = the point maximizing min-distance to chosen centroids. Fixed iterations,
    empty-cluster reseed to the globally-worst-assigned point. Returns integer labels 0..k-1."""
    n = X.shape[0]
    if n <= k:
        return np.arange(n) % k
    c0 = int(np.argmax((X * X).sum(axis=1)))
    centers = [c0]
    d2 = ((X - X[c0]) ** 2).sum(axis=1)
    while len(centers) < k:
        nxt = int(np.argmax(d2))
        if nxt in centers:
            # all remaining points coincide with a center; pad deterministically
            remaining = [i for i in range(n) if i not in centers]
            centers.append(remaining[0])
        else:
            centers.append(nxt)
        d2 = np.minimum(d2, ((X - X[centers[-1]]) ** 2).sum(axis=1))
    C = X[np.array(centers)].copy()
    labels = np.zeros(n, dtype=np.int64)
    for _ in range(iters):
        dists = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)  # (n,k)
        new_labels = np.argmin(dists, axis=1)
        if np.array_equal(new_labels, labels) and _ > 0:
            labels = new_labels
            break
        labels = new_labels
        for j in range(k):
            m = labels == j
            if m.any():
                C[j] = X[m].mean(axis=0)
            else:
                # empty cluster: reseed to the point currently worst-served
                worst = int(np.argmax(dists.min(axis=1)))
                C[j] = X[worst]
    return labels


def spectral_communities(adj, n_ent, c_max, km_iters, km_seed):
    """Balanced C-way partition of the undirected TRAIN graph via symmetric-normalized-Laplacian spectral
    embedding + deterministic k-means. Train-degree-0 (isolated) entities -> dedicated bucket id c_max.
    Deterministic. Returns (comm 0..c_max, C=c_max+1)."""
    A = np.zeros((n_ent, n_ent), dtype=np.float64)
    for u in range(n_ent):
        nb = adj[u]
        if nb.shape[0]:
            A[u, nb] = 1.0
    deg = A.sum(axis=1)
    iso = deg == 0.0
    comm = np.full(n_ent, c_max, dtype=np.int64)   # default: isolated bucket
    keep = np.where(~iso)[0]
    if len(keep) > c_max:
        As = A[np.ix_(keep, keep)]
        ds = As.sum(axis=1)
        ds[ds == 0.0] = 1.0
        dinv = 1.0 / np.sqrt(ds)
        Lsym = np.eye(len(keep)) - (dinv[:, None] * As * dinv[None, :])
        _, evecs = np.linalg.eigh(Lsym)          # ascending eigenvalues
        emb = evecs[:, :c_max]
        # row-normalize (Ng-Jordan-Weiss)
        norms = np.sqrt((emb ** 2).sum(axis=1, keepdims=True))
        norms[norms == 0.0] = 1.0
        emb = emb / norms
        lab = _kmeans_deterministic(emb, c_max, km_iters, km_seed)
        comm[keep] = lab
    return comm, (c_max + 1)


# --------------------------- data ------------------------------------------
def read_triples(fname):
    return [tuple(l.split("\t")) for l in
            open(os.path.join(RAW, fname), encoding="utf-8").read().split("\n") if l]


def main():
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)

    train = read_triples("train.txt")
    val_p = read_triples("valid.txt");  val_n = read_triples("valid_negatives.txt")
    tst_p = read_triples("test.txt");   tst_n = read_triples("test_negatives.txt")

    ents, rels = set(), set()
    for h, r, t in train + val_p + val_n + tst_p + tst_n:
        ents.add(h); ents.add(t); rels.add(r)
    eidx = {e: i for i, e in enumerate(sorted(ents))}
    ridx = {p: i for i, p in enumerate(sorted(rels))}
    n_ent, n_rel = len(eidx), len(ridx)

    train_int = np.array([[eidx[h], ridx[r], eidx[t]] for h, r, t in train], dtype=np.int64)

    # leakage guard: no eval POSITIVE may appear in the training graph
    train_set = set(train)
    leak = sum(1 for tp in (val_p + tst_p) if tp in train_set)
    assert leak == 0, "LEAK: %d eval positives found in train graph" % leak

    # ---- structural scaffolding from TRAIN only ----
    adj = ra.build_undirected_adj(train_int, n_ent)
    deg = ra.degree_vector(adj)
    nbr = [set(int(x) for x in row) for row in adj]
    rel_freq = Counter(r for h, r, t in train)

    # relation-typed undirected edge map: (a,b) sorted -> set(rel idx). For recurrence diversity.
    pair_rels = defaultdict(set)
    for h, r, t in train:
        hi, ti, riu = eidx[h], eidx[t], ridx[r]
        if hi != ti:
            a, b = (hi, ti) if hi < ti else (ti, hi)
            pair_rels[(a, b)].add(riu)

    # ---- communities + per-relation forward model P(c_t | c_h, r) from TRAIN ----
    print("[comm] spectral communities (n_ent=%d, c_max=%d) ..." % (n_ent, C_MAX), flush=True)
    comm, C = spectral_communities(adj, n_ent, C_MAX, KM_ITERS, KM_SEED)
    comm_sizes = Counter(int(c) for c in comm)
    print("[comm] C=%d communities; sizes(top)=%s" %
          (C, sorted(comm_sizes.values(), reverse=True)[:10]), flush=True)

    # per-relation community transition counts (from TRAIN triples = the foundation)
    trans = np.zeros((n_rel, C, C), dtype=np.float64)
    for h, r, t in train:
        trans[ridx[r], comm[eidx[h]], comm[eidx[t]]] += 1.0
    # row-conditional smoothed P(c_t | c_h, r)
    row_tot = trans.sum(axis=2, keepdims=True)          # (n_rel, C, 1)
    P_ct = (trans + LP_ALPHA) / (row_tot + LP_ALPHA * C)  # (n_rel, C, C)

    def schema_fit_ra(h_i, t_i):
        """Resource-Allocation pairwise index (the VET-confirmed schema-fit signal). Symmetric structural."""
        if h_i == t_i:
            return 0.0
        common = nbr[h_i] & nbr[t_i]
        val = 0.0
        for z in common:
            dz = deg[z]
            if dz > 0:
                val += 1.0 / dz
        return val

    def recurrence_diversity(h_i, t_i):
        """DISTINCT relation-type corroboration: number of distinct relation types on the common-neighbor
        paths connecting (h,t) in train. Count (diversity), not magnitude -> distinct from RA."""
        if h_i == t_i:
            return 0.0
        common = nbr[h_i] & nbr[t_i]
        rset = set()
        for z in common:
            a, b = (h_i, z) if h_i < z else (z, h_i)
            rset |= pair_rels.get((a, b), set())
            a, b = (z, t_i) if z < t_i else (t_i, z)
            rset |= pair_rels.get((a, b), set())
        # also direct h-t relations (rare among eval negatives; positives excluded from train by leak guard)
        a, b = (h_i, t_i) if h_i < t_i else (t_i, h_i)
        rset |= pair_rels.get((a, b), set())
        return float(len(rset))

    def unexpectedness_pe(h_i, r_i, t_i):
        """Schema-conditioned prediction error = -log P(c_t | c_h, r) under the foundation's relation-typed
        community-transition forward model. Higher = more surprising / less predicted by the foundation."""
        p = P_ct[r_i, comm[h_i], comm[t_i]]
        return float(-math.log(p))

    # ---- featurizer ----
    def featurize(rows, labels):
        n = len(rows)
        sf = np.zeros(n); rec = np.zeros(n); unex = np.zeros(n)
        hdeg = np.zeros(n); tdeg = np.zeros(n); rfreq = np.zeros(n)
        for i, (h, r, t) in enumerate(rows):
            hi, ti, riu = eidx[h], eidx[t], ridx[r]
            sf[i] = schema_fit_ra(hi, ti)
            rec[i] = recurrence_diversity(hi, ti)
            unex[i] = unexpectedness_pe(hi, riu, ti)
            hdeg[i] = math.log1p(deg[hi])
            tdeg[i] = math.log1p(deg[ti])
            rfreq[i] = math.log1p(rel_freq.get(r, 0))
        return {"y": np.array(labels, dtype=np.float64),
                "schema_fit": sf, "recurrence": rec, "unexpectedness": unex,
                "head_deg": hdeg, "tail_deg": tdeg, "rel_freq": rfreq, "rows": rows}

    # ---- fairness-control split constructors (deterministic; from the VET'd chassis) ----
    ld = np.log1p(deg[deg > 0])
    qthr = np.quantile(ld, [0.25, 0.5, 0.75]) if len(ld) else np.array([0., 0., 0.])
    def dbin(e_i):
        return int(np.searchsorted(qthr, math.log1p(deg[e_i])))

    def build_full(pos, neg):
        return list(pos) + list(neg), [1] * len(pos) + [0] * len(neg)

    def build_relation_balanced(pos, neg):
        by_r_p = defaultdict(list); by_r_n = defaultdict(list)
        for tr in pos: by_r_p[tr[1]].append(tr)
        for tr in neg: by_r_n[tr[1]].append(tr)
        rows, labels = [], []
        for r in sorted(set(by_r_p) | set(by_r_n)):
            k = min(len(by_r_p[r]), len(by_r_n[r]))
            for tr in sorted(by_r_p[r])[:k]: rows.append(tr); labels.append(1)
            for tr in sorted(by_r_n[r])[:k]: rows.append(tr); labels.append(0)
        return rows, labels

    def build_relation_degree_matched(pos, neg):
        cell_p = defaultdict(list); cell_n = defaultdict(list)
        for tr in pos:
            cell_p[(tr[1], dbin(eidx[tr[0]]), dbin(eidx[tr[2]]))].append(tr)
        for tr in neg:
            cell_n[(tr[1], dbin(eidx[tr[0]]), dbin(eidx[tr[2]]))].append(tr)
        rows, labels = [], []
        for key in sorted(set(cell_p) | set(cell_n)):
            k = min(len(cell_p[key]), len(cell_n[key]))
            for tr in sorted(cell_p[key])[:k]: rows.append(tr); labels.append(1)
            for tr in sorted(cell_n[key])[:k]: rows.append(tr); labels.append(0)
        return rows, labels

    def make_nn_matcher(caliper):
        def build_relation_nn_degree_matched(pos, neg):
            by_r_p = defaultdict(list); by_r_n = defaultdict(list)
            for tr in pos: by_r_p[tr[1]].append(tr)
            for tr in neg: by_r_n[tr[1]].append(tr)
            def feat(tr): return (math.log1p(deg[eidx[tr[0]]]), math.log1p(deg[eidx[tr[2]]]))
            rows, labels = [], []
            for r in sorted(set(by_r_p) | set(by_r_n)):
                P = sorted(by_r_p[r]); Nn = sorted(by_r_n[r])
                if not P or not Nn:
                    continue
                Pf = [feat(tr) for tr in P]; Nf = [feat(tr) for tr in Nn]
                used = [False] * len(Nn)
                for pi, tr in enumerate(P):
                    best, bestd = -1, caliper
                    for ni in range(len(Nn)):
                        if used[ni]:
                            continue
                        d = math.hypot(Pf[pi][0] - Nf[ni][0], Pf[pi][1] - Nf[ni][1])
                        if d <= bestd:
                            bestd, best = d, ni
                    if best >= 0:
                        used[best] = True
                        rows.append(tr); labels.append(1)
                        rows.append(Nn[best]); labels.append(0)
            return rows, labels
        return build_relation_nn_degree_matched

    FREQ_FEATS = ["head_deg", "tail_deg", "rel_freq"]

    def freq_baseline(feat_tr, feat_te):
        Xtr = np.column_stack([feat_tr[f] for f in FREQ_FEATS])
        Xte = np.column_stack([feat_te[f] for f in FREQ_FEATS])
        w, b, mu, sd = logistic_fit(Xtr, feat_tr["y"])
        pred = logistic_score(Xte, w, b, mu, sd)
        logit_auc = auroc(feat_te["y"], pred)
        singles = {f: max(auroc(feat_te["y"], feat_te[f]), 1 - auroc(feat_te["y"], feat_te[f]))
                   for f in FREQ_FEATS}
        best_single = max(singles.values())
        return {"freq_pred": pred, "freq_logistic_auroc": logit_auc,
                "freq_single_best_auroc": best_single,
                "certificate_auroc": max(logit_auc, best_single)}

    # ---- featurize valid + test ONCE ----
    print("[featurize] valid + test ...", flush=True)
    F_val_full = featurize(*build_full(val_p, val_n))
    F_test_full = featurize(*build_full(tst_p, tst_n))

    def subselect(Ffull, builder, pos, neg):
        rows, labels = builder(pos, neg)
        buckets = defaultdict(list)
        for i, tr in enumerate(Ffull["rows"]):
            buckets[tr].append(i)
        used = defaultdict(int); out_idx = []
        for tr in rows:
            k = used[tr]; out_idx.append(buckets[tr][k]); used[tr] += 1
        out_idx = np.array(out_idx, dtype=np.int64)
        sub = {k: (v[out_idx] if isinstance(v, np.ndarray) else [v[i] for i in out_idx])
               for k, v in Ffull.items() if k != "rows"}
        sub["rows"] = [Ffull["rows"][i] for i in out_idx]
        sub["y"] = Ffull["y"][out_idx]
        return sub

    def escalate(caliper):
        controls = [
            ("full", build_full),
            ("relation_balanced", build_relation_balanced),
            ("relation_degree_matched", build_relation_degree_matched),
            ("relation_nn_degree_matched", make_nn_matcher(caliper)),
        ]
        certs = {}; chosen = None
        for cname, builder in controls:
            F_te = subselect(F_test_full, builder, tst_p, tst_n)
            F_tr = subselect(F_val_full, builder, val_p, val_n)
            fb = freq_baseline(F_tr, F_te)
            fires = (FREQ_CHANCE_LO <= fb["certificate_auroc"] <= FREQ_CHANCE_HI)
            certs[cname] = {"n_test": len(F_te["y"]), "certificate_fires": fires,
                            "certificate_auroc": fb["certificate_auroc"],
                            "freq_logistic_auroc": fb["freq_logistic_auroc"]}
            if fires and chosen is None:
                chosen = (cname, F_tr, F_te, fb)
        return chosen, certs

    # ---- degree-orthogonalize a signal held-out label-free (fit VAL, apply VAL+TEST) ----
    def orth_pair(F_tr, F_te, key):
        coef = fit_projection(F_tr[key], [F_tr["head_deg"], F_tr["tail_deg"]])
        o_tr = apply_projection(coef, F_tr[key], [F_tr["head_deg"], F_tr["tail_deg"]])
        o_te = apply_projection(coef, F_te[key], [F_te["head_deg"], F_te["tail_deg"]])
        return o_tr, o_te

    def degree_explained_heldout(resid_te, F_te):
        """Re-residualize held-out unique signal on TEST degrees; fraction of above-chance AUROC removed."""
        raw = auroc_pa(F_te["y"], resid_te)
        coef2 = fit_projection(resid_te, [F_te["head_deg"], F_te["tail_deg"]])
        r2 = apply_projection(coef2, resid_te, [F_te["head_deg"], F_te["tail_deg"]])
        r2_auc = auroc_pa(F_te["y"], r2)
        above = raw - 0.5
        frac = float((raw - r2_auc) / above) if above > 1e-9 else 0.0
        return max(0.0, min(1.0, frac))

    import hashlib
    def _dig(a):
        return hashlib.sha256(np.ascontiguousarray(np.asarray(a, np.float64)).tobytes()).hexdigest()

    # ============================ RUN THE CALIPER GRID ============================
    per_caliper = {}
    all_cert_fire = True
    all_info_ceiling = True
    split_broken = []
    arms_differ_all = True

    for cap in CALIPERS:
        chosen, certs = escalate(cap)
        if chosen is None:
            all_cert_fire = False
            split_broken.append("cal%.2f" % cap)
            per_caliper["cal%.2f" % cap] = {"certificate_fires": False, "certs_by_control": certs}
            continue
        cname, F_tr, F_te, fb = chosen
        ytr, yte = F_tr["y"], F_te["y"]
        freq_pred = fb["freq_pred"]

        # degree-orthogonalized signals (held-out, label-free)
        sf_tr, sf_te = orth_pair(F_tr, F_te, "schema_fit")
        rec_tr, rec_te = orth_pair(F_tr, F_te, "recurrence")
        un_tr, un_te = orth_pair(F_tr, F_te, "unexpectedness")

        # arms-must-differ (META_RULE_AF)
        if len({_dig(sf_te), _dig(rec_te), _dig(un_te)}) < 3:
            arms_differ_all = False

        # info-ceiling gate FIRST: sf reproduces frontier; full above chance
        sf_auc = auroc(yte, sf_te)
        sf_auc_pa = max(sf_auc, 1 - sf_auc)
        info_ok = sf_auc_pa >= INFO_CEILING_SF_MIN

        # base vs full logistic (fit on TRAIN-orth, eval TEST-orth)
        Xb_tr = np.column_stack([sf_tr, rec_tr]); Xb_te = np.column_stack([sf_te, rec_te])
        Xf_tr = np.column_stack([sf_tr, rec_tr, un_tr]); Xf_te = np.column_stack([sf_te, rec_te, un_te])
        wb, bb, mub, sdb = logistic_fit(Xb_tr, ytr)
        wf, bf, muf, sdf = logistic_fit(Xf_tr, ytr)
        pb = logistic_score(Xb_te, wb, bb, mub, sdb)
        pf = logistic_score(Xf_te, wf, bf, muf, sdf)
        auc_base = auroc(yte, pb)
        auc_full = auroc(yte, pf)
        delta = auc_full - auc_base
        info_ok = info_ok and (auc_full >= INFO_CEILING_FULL_MIN)
        if not info_ok:
            all_info_ceiling = False

        # partial / unique variance: residualize unexp on [sf,rec] label-free (fit TRAIN, apply TEST)
        pcoef = fit_projection(un_tr, [sf_tr, rec_tr])
        un_unique_te = apply_projection(pcoef, un_te, [sf_te, rec_te])
        partial_auc = auroc_pa(yte, un_unique_te)
        redundancy_r2 = r_squared(un_tr, [sf_tr, rec_tr])   # how much of unexp already in sf,rec (train)
        unexp_alone_auc = auroc_pa(yte, un_te)
        corr_un_sf = abs(float(np.corrcoef(un_tr, sf_tr)[0, 1]))
        corr_un_rec = abs(float(np.corrcoef(un_tr, rec_tr)[0, 1]))
        deg_expl = degree_explained_heldout(un_unique_te, F_te)

        # ---- bootstrap: real delta p05 + partial p05 (models fixed; resample TEST rows) ----
        n = len(yte)
        boot_delta, boot_partial = [], []
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            for _b in range(N_BOOT):
                idx = rng.integers(0, n, size=n)
                yb = yte[idx]
                if yb.sum() == 0 or yb.sum() == n:
                    continue
                boot_delta.append(auroc(yb, pf[idx]) - auroc(yb, pb[idx]))
                boot_partial.append(auroc_pa(yb, un_unique_te[idx]))
        boot_delta = np.array(boot_delta); boot_partial = np.array(boot_partial)
        delta_p05 = float(np.percentile(boot_delta, BOOT_LO_PCT))
        partial_p05 = float(np.percentile(boot_partial, BOOT_LO_PCT))
        partial_p95 = float(np.percentile(boot_partial, NULL_HI_PCT))

        # ---- SHUFFLED-UNEXP NULL: permute unexp within train+test, refit full, delta_null distribution ----
        null_deltas = []
        rngn = np.random.default_rng(4242)
        for _k in range(N_NULL):
            un_tr_s = un_tr[rngn.permutation(len(un_tr))]
            un_te_s = un_te[rngn.permutation(len(un_te))]
            Xf_tr_s = np.column_stack([sf_tr, rec_tr, un_tr_s])
            Xf_te_s = np.column_stack([sf_te, rec_te, un_te_s])
            ws, bs, mus, sds = logistic_fit(Xf_tr_s, ytr)
            ps = logistic_score(Xf_te_s, ws, bs, mus, sds)
            null_deltas.append(auroc(yte, ps) - auc_base)
        null_deltas = np.array(null_deltas)
        null_delta_p95 = float(np.percentile(null_deltas, NULL_HI_PCT))
        null_delta_mean = float(null_deltas.mean())
        beats_null = delta_p05 > null_delta_p95

        per_caliper["cal%.2f" % cap] = {
            "certificate_fires": True, "chosen_control": cname, "n_test": n,
            "freq_logistic_auroc": fb["freq_logistic_auroc"], "certificate_auroc": fb["certificate_auroc"],
            "info_ceiling_ok": bool(info_ok),
            "sf_orth_auroc_pa": sf_auc_pa,
            "auc_base_sf_rec": auc_base, "auc_full_sf_rec_unexp": auc_full,
            "delta_auc": delta, "delta_auc_boot_p05": delta_p05,
            "partial_unexp_auroc": partial_auc, "partial_boot_p05": partial_p05,
            "partial_boot_p95": partial_p95,
            "unexp_alone_auroc_pa": unexp_alone_auc,
            "redundancy_r2_unexp_on_sf_rec": redundancy_r2,
            "corr_unexp_schemafit": corr_un_sf, "corr_unexp_recurrence": corr_un_rec,
            "unexp_unique_degree_explained_heldout": deg_expl,
            "shuffled_null_delta_p95": null_delta_p95, "shuffled_null_delta_mean": null_delta_mean,
            "real_delta_beats_null": bool(beats_null),
        }
        print("  cal%.2f [%s] n=%d | sf_orth=%.3f base=%.3f full=%.3f delta=%.4f (p05=%.4f) | "
              "partial=%.3f (p05=%.3f) unexp_alone=%.3f R2=%.3f corr_sf=%.3f | null_d_p95=%.4f beats_null=%s"
              % (cap, cname, n, sf_auc_pa, auc_base, auc_full, delta, delta_p05,
                 partial_auc, partial_p05, unexp_alone_auc, redundancy_r2, corr_un_sf,
                 null_delta_p95, beats_null), flush=True)

    # ---- short-circuits ----
    if not all_cert_fire:
        _finish({"verdict": "SPLIT_NOT_FREQUENCY_BLIND",
                 "verdict_msg": "config(s) %s had no control driving freq baseline into [%.2f,%.2f]"
                 % (split_broken, FREQ_CHANCE_LO, FREQ_CHANCE_HI),
                 "per_caliper": per_caliper, "elapsed_s": time.time() - t0})
        return
    if not all_info_ceiling:
        _finish({"verdict": "INFO_CEILING_FAIL",
                 "verdict_msg": "schema-fit frontier not reproduced (>= %.2f) OR full model below chance "
                 "(>= %.2f) at some caliper; incremental test uninformative"
                 % (INFO_CEILING_SF_MIN, INFO_CEILING_FULL_MIN),
                 "per_caliper": per_caliper, "elapsed_s": time.time() - t0})
        return

    # ============================ VERDICT (base caliper primary; robustness across all) ============================
    def blk(cap):
        return per_caliper["cal%.2f" % cap]
    base = blk(BASE_CAP)

    # HARD_PASS requires the gate to hold across ALL calipers
    hp_partial = all(blk(c)["partial_unexp_auroc"] >= PARTIAL_HARD_PASS and blk(c)["partial_boot_p05"] > 0.50
                     for c in CALIPERS)
    hp_delta = all(blk(c)["delta_auc"] >= DELTA_HARD_PASS and blk(c)["real_delta_beats_null"]
                   for c in CALIPERS)
    hp_neutral = all(blk(c)["unexp_unique_degree_explained_heldout"] < DEG_EXPLAINED_MAX for c in CALIPERS)

    # HARD_FAIL evaluated at base caliper (redundant / adds nothing)
    hf_partial = base["partial_unexp_auroc"] <= PARTIAL_HARD_FAIL and base["partial_boot_p95"] <= 0.52
    hf_delta = base["delta_auc"] <= DELTA_HARD_FAIL
    hf_null = not base["real_delta_beats_null"]

    if hp_partial and hp_delta and hp_neutral and arms_differ_all:
        verdict = "HARD_PASS_UNEXPECTEDNESS_ADDS_NONREDUNDANT_VALUE"
    elif hf_partial or hf_delta or hf_null:
        verdict = "HARD_FAIL_UNEXPECTEDNESS_REDUNDANT_REAL_GATE_IS_2SIGNAL"
    else:
        verdict = "MIDDLE"

    verdict_msg = (
        "UNEXPECTEDNESS incremental value vs {schema-fit + recurrence} on CoDEx-S claim-validity "
        "(base cal%.2f [%s] n=%d): base=%.3f full=%.3f delta=%.4f (p05=%.4f); "
        "partial(unique-variance) AUROC=%.3f (p05=%.3f p95=%.3f); unexp_alone=%.3f; "
        "redundancy R2(unexp~sf,rec)=%.3f corr(unexp,sf)=%.3f; deg_explained=%.3f; "
        "shuffled-null delta p95=%.4f beats_null=%s; robust-across-calipers HP(partial=%s delta=%s neutral=%s)"
        % (BASE_CAP, base["chosen_control"], base["n_test"], base["auc_base_sf_rec"],
           base["auc_full_sf_rec_unexp"], base["delta_auc"], base["delta_auc_boot_p05"],
           base["partial_unexp_auroc"], base["partial_boot_p05"], base["partial_boot_p95"],
           base["unexp_alone_auroc_pa"], base["redundancy_r2_unexp_on_sf_rec"],
           base["corr_unexp_schemafit"], base["unexp_unique_degree_explained_heldout"],
           base["shuffled_null_delta_p95"], base["real_delta_beats_null"],
           hp_partial, hp_delta, hp_neutral))

    _finish({
        "dataset": "CoDEx-S triple classification (Safavi & Koutra, EMNLP 2020) -- human-verified hard negatives",
        "verdict": verdict, "summary": verdict, "verdict_msg": verdict_msg,
        "signal_definitions": {
            "schema_fit": "degree-orthogonal pairwise Resource-Allocation index (VET'd real-data win); symmetric structural overlap",
            "recurrence": "degree-orthogonal count of DISTINCT relation types among common-neighbor paths (corroboration diversity)",
            "unexpectedness": "degree-orthogonal -log P(c_t | c_h, r): schema-conditioned prediction error of the "
                              "foundation's relation-typed community-transition forward model (LOCAL, relation-conditioned, directed)",
        },
        "community_model": {"C": C, "c_max": C_MAX, "method": "spectral_kmeans", "lp_alpha": LP_ALPHA,
                            "km_iters": KM_ITERS, "top_sizes": sorted(comm_sizes.values(), reverse=True)[:10]},
        "config": {"calipers": CALIPERS, "base_caliper": BASE_CAP, "seeds": SEEDS,
                   "n_boot": N_BOOT, "n_null": N_NULL,
                   "partial_hard_pass": PARTIAL_HARD_PASS, "partial_hard_fail": PARTIAL_HARD_FAIL,
                   "delta_hard_pass": DELTA_HARD_PASS, "delta_hard_fail": DELTA_HARD_FAIL,
                   "deg_explained_max": DEG_EXPLAINED_MAX,
                   "info_ceiling_sf_min": INFO_CEILING_SF_MIN, "info_ceiling_full_min": INFO_CEILING_FULL_MIN},
        "verdict_gates": {
            "hp_partial_unique_variance_all_calipers": bool(hp_partial),
            "hp_delta_and_beats_null_all_calipers": bool(hp_delta),
            "hp_degree_neutral_all_calipers": bool(hp_neutral),
            "hf_partial_redundant_base": bool(hf_partial),
            "hf_delta_adds_nothing_base": bool(hf_delta),
            "hf_delta_not_beat_null_base": bool(hf_null),
            "arms_differ_verified": bool(arms_differ_all),
            "cert_fires_all": bool(all_cert_fire), "info_ceiling_all": bool(all_info_ceiling),
        },
        "prereg_bands": {
            "HARD_PASS": "cert+info-ceiling all AND all calipers: partial>=%.2f (p05>0.50) AND delta>=%.3f "
                         "AND real-delta p05>shuffled-null p95 AND deg_explained<%.2f -> unexpectedness "
                         "adds non-redundant value; 1st signal load-bearing on real data"
                         % (PARTIAL_HARD_PASS, DELTA_HARD_PASS, DEG_EXPLAINED_MAX),
            "HARD_FAIL": "cert+info-ceiling OK BUT base caliper: partial<=%.2f (p95<=0.52) OR delta<=%.3f OR "
                         "real-delta not beating shuffled-null -> unexpectedness REDUNDANT; real gate is "
                         "2-signal (schema-fit + recurrence) -> FLAG FOR USER (4-signal design + all-signals LOCK)"
                         % (PARTIAL_HARD_FAIL, DELTA_HARD_FAIL),
            "MIDDLE": "otherwise (unique variance present but delta small/unrobust; partial in (0.51,0.53))",
            "INFO_CEILING_FAIL": "schema-fit frontier not reproduced OR full model below chance",
            "SPLIT_NOT_FREQUENCY_BLIND": "no control drove the freq baseline into [0.45,0.55]",
        },
        "honesty_notes": [
            "unexpectedness is NOT a standalone validity predictor by design (novel-true and false-noise are "
            "both unexpected); this cell tests its NON-REDUNDANT INCREMENTAL value as a component of the gate.",
            "all 3 signals degree-orthogonalized held-out label-free (fit VAL-matched, apply TEST-matched); "
            "same frequency-blind escalation + freq-at-chance certificate as the VET'd schema-fit chassis.",
            "SHUFFLED-unexp null is the discriminator-fires guard: adding ANY 3rd feature can nudge AUROC by "
            "overfitting; the real delta must beat the permutation-null delta p95, else the 'improvement' is "
            "a feature-count artifact.",
            "partial (unique-variance) AUROC = AUROC of unexp AFTER OLS-removing schema-fit + recurrence "
            "(label-free); this is the load-bearing redundancy discriminator. redundancy_r2 reports how much "
            "of unexp is already linearly captured by schema-fit + recurrence.",
            "if HARD_FAIL: this + the importance HARD_FAIL => real-data ingest gate is really 2 signals "
            "(schema-fit + recurrence); a load-bearing conclusion re: the 4-signal design + all-signals LOCK. "
            "FLAG FOR USER; do NOT prune unilaterally.",
        ],
        "per_caliper": per_caliper,
        "elapsed_s": time.time() - t0,
    })
    print("\nTOP-LEVEL VERDICT: %s\n  %s" % (verdict, verdict_msg), flush=True)


def _finish(summary):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = RESULTS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp, RESULTS_PATH)
    print(json.dumps({k: v for k, v in summary.items() if k != "per_caliper"}, indent=2)[:1800], flush=True)


# --------------------------- self-test (positive controls; fast, no CoDEx) ---------------
def self_test():
    """HARDENED positive controls (no CoDEx data touched):
    (1) auroc monotone + polarity-agnostic sane;
    (2) spectral communities separate two disjoint cliques into distinct clusters;
    (3) forward-model PE: an UNEXPECTED (rare) community transition scores higher -log P than an expected one;
    (4) unique-variance (partial) recovers a PLANTED signal that is orthogonal to the conditioners, and returns
        ~0.5 for a signal that is a pure FUNCTION of the conditioners (the redundancy case the cell must detect);
    (5) shuffled-null control: permuting a real informative signal collapses its incremental AUROC to ~0;
    (6) arms differ."""
    rng = np.random.default_rng(7)

    # (1) auroc
    y = np.array([0, 0, 1, 1, 1]); s = np.array([0.1, 0.2, 0.3, 0.9, 0.8])
    assert auroc(y, s) == 1.0, "auroc perfect-sep should be 1.0"
    assert abs(auroc_pa(y, -s) - 1.0) < 1e-9, "auroc_pa polarity-agnostic broken"

    # (2) spectral communities: two disjoint cliques {0,1,2,3} + {4,5,6} must go to distinct clusters;
    #     an isolated node (7) must land in the dedicated isolated bucket (id c_max).
    n = 8
    edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (4, 5), (5, 6), (4, 6)]
    adj = [np.array(sorted([b for (a, b) in edges if a == u] + [a for (a, b) in edges if b == u]),
                    dtype=np.int64) for u in range(n)]
    comm, C = spectral_communities(adj, n, 2, KM_ITERS, KM_SEED)
    assert len(set(int(comm[i]) for i in (0, 1, 2, 3))) == 1, "spectral failed to group clique1 (%s)" % comm.tolist()
    assert len(set(int(comm[i]) for i in (4, 5, 6))) == 1, "spectral failed to group clique2 (%s)" % comm.tolist()
    assert comm[0] != comm[4], "spectral wrongly merged the two disjoint cliques"
    assert comm[7] == 2, "isolated node not routed to the isolated bucket (id c_max=2): got %d" % comm[7]
    assert C == 3 and comm.max() < C, "spectral produced bad ids"

    # (3) forward-model PE: build a 2-community, 1-relation transition that ALWAYS goes 0->0; a 0->1 test
    #     transition must have HIGHER -log P than a 0->0 transition.
    Cc = 2
    tr = np.zeros((1, Cc, Cc)); tr[0, 0, 0] = 50.0; tr[0, 1, 1] = 50.0
    P = (tr + 1.0) / (tr.sum(axis=2, keepdims=True) + 1.0 * Cc)
    pe_expected = -math.log(P[0, 0, 0])   # 0->0 seen 50x -> low surprise
    pe_surprise = -math.log(P[0, 0, 1])   # 0->1 never seen -> high surprise
    assert pe_surprise > pe_expected + 1.0, "PE self-test: unexpected transition not more surprising (%.3f vs %.3f)" % (pe_surprise, pe_expected)

    # (4) unique-variance discriminator (the load-bearing redundancy test).
    m = 600
    yy = (rng.random(m) < 0.5).astype(float)
    sf = yy + rng.normal(scale=0.7, size=m)                     # schema-fit: informative conditioner
    rec = rng.normal(size=m)                                    # recurrence: noise conditioner
    # (a) unexp_indep = independent informative signal (orthogonal to sf,rec) -> partial should be ABOVE chance
    unexp_indep = yy + rng.normal(scale=0.9, size=m)
    coef = fit_projection(unexp_indep, [sf, rec]); uq = apply_projection(coef, unexp_indep, [sf, rec])
    assert auroc_pa(yy, uq) > 0.55, "partial self-test: independent informative signal shows no unique variance (%.3f)" % auroc_pa(yy, uq)
    # (b) unexp_redundant correlates with y ONLY through sf (= 2*sf + noise INDEPENDENT of y): the real
    #     redundancy case. Its residual after removing sf is y-independent noise -> partial should be ~chance.
    unexp_redundant = 2.0 * sf + rng.normal(scale=0.5, size=m)
    coefr = fit_projection(unexp_redundant, [sf, rec]); uqr = apply_projection(coefr, unexp_redundant, [sf, rec])
    assert auroc_pa(yy, uqr) < 0.56, "partial self-test: y-info-only-via-sf shows spurious unique variance (%.3f)" % auroc_pa(yy, uqr)
    assert r_squared(unexp_redundant, [sf, rec]) > 0.60, "R2 self-test: sf-dominated signal R2 should be high"

    # (5) shuffled-null: permuting the informative unexp collapses incremental AUROC.
    Xb = np.column_stack([sf, rec]); Xf = np.column_stack([sf, rec, unexp_indep])
    wb, bb, mub, sdb = logistic_fit(Xb, yy); wf, bf, muf, sdf = logistic_fit(Xf, yy)
    auc_b = auroc(yy, logistic_score(Xb, wb, bb, mub, sdb))
    auc_f = auroc(yy, logistic_score(Xf, wf, bf, muf, sdf))
    Xf_s = np.column_stack([sf, rec, unexp_indep[rng.permutation(m)]])
    ws, bs, mus, sds = logistic_fit(Xf_s, yy)
    auc_fs = auroc(yy, logistic_score(Xf_s, ws, bs, mus, sds))
    assert (auc_f - auc_b) > (auc_fs - auc_b) + 0.01, "shuffled-null self-test: real delta must beat shuffled delta (%.4f vs %.4f)" % (auc_f - auc_b, auc_fs - auc_b)

    # (6) arms differ
    import hashlib
    def d(a): return hashlib.sha256(np.ascontiguousarray(np.asarray(a, np.float64)).tobytes()).hexdigest()
    assert len({d(sf), d(rec), d(unexp_indep)}) == 3, "arms-differ self-test failed"

    print("SELFTEST_PASS: auroc + LP(merge-clique/separate-components) + forward-PE(unexpected>expected) + "
          "unique-variance(indep=%.3f>redundant=%.3f) + shuffled-null(real_delta %.4f > null %.4f) + arms-differ OK"
          % (auroc_pa(yy, uq), auroc_pa(yy, uqr), auc_f - auc_b, auc_fs - auc_b), flush=True)


if __name__ == "__main__":
    try:
        if "--self-test" in sys.argv:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
