# PAIRWISE SR/PPR SCHEMA-FIT UPGRADE for CoDEx claim-validity (Safavi & Koutra EMNLP 2020).
#
# Question: does a PAIRWISE multi-path resolvent schema-fit signal (SR/personalized-PageRank
# M=(I-gamma*T)^-1) beat the NODE-ish RA (Resource-Allocation) schema-fit on the SAME
# frequency-blind CoDEx claim-validity split -- WIDENING the structural margin over the
# frequency-matched baseline (RA currently carries ~+0.07 over freq, per the VET-confirmed win in
# exp_codex_claimvalidity_frequency_vs_structural_v1.py)?
#
# WHY (research note research_schema_fit_derivability_signal_upgrade_2026-07-16.md):
#   RA(h,t) = sum_{z in N(h) cap N(t)} 1/deg(z) aggregates only 2-hop (single-length) common-neighbor
#   paths. The brain (CA3 aggregate convergence, structure-mapping systematicity) and network science
#   (Katz/PPR/SR resolvent) both point to a PAIR-SPECIFIC, MULTI-PATH, MULTI-LENGTH aggregator as the
#   richer derivability computation. The SR/PPR resolvent M=(I-gamma*T)^-1 is exactly that: M[t,h]
#   sums over ALL paths h->...->t weighted by gamma^len. This reuses the ALREADY-LANDED, self-test-passed
#   SRSolver machinery (M=(I-gamma*T)^-1, LU-factored) from
#   exp_grounding_multihop_sr_reachability_routing_v1.py -- reimplemented inline here (that module imports
#   a cascade of other cells at top level, so importing it is fragile; the resolvent math is identical and
#   a positive-control self-test reproduces its "SR recovers reachability" property).
#
# PRECONDITION (fairness certificate, reused VERBATIM from the v1 cell): the degree/frequency baseline
#   MUST be at/near CHANCE on the evaluated split by construction (escalate full -> relation-balanced ->
#   relation+degree-bin-matched -> relation+NN-degree-caliper-matched; take the FIRST control where the
#   freq baseline lands in [0.45,0.55]). If freq still discriminates, the split isn't frequency-blind and
#   NO gate result can be trusted -- report the split failure.
#
# DECISIVE: on the chosen frequency-blind split, is
#     margin_pairwise_vs_freq  =  AUROC(SR/PPR pairwise)  -  AUROC(freq baseline)
#   MEANINGFULLY LARGER than
#     margin_RA_vs_freq        =  AUROC(RA)               -  AUROC(freq baseline) ?
#   widening = margin_pairwise_vs_freq - margin_RA_vs_freq.
#
# KEEP IT HONEST (same scrutiny the VET applied to RA): the pairwise signal must stay POPULARITY-NEUTRAL.
#   We regress the pairwise score on (log head_deg, log tail_deg) and measure how much of its above-chance
#   discrimination survives residualization (degree_explained_fraction). A signal that only wins by
#   exploiting residual degree the matching missed is NOT a real schema-fit upgrade.
#
# PRE-REG bands (verdict gamma = 0.6, an interior pre-registered value; 0.5/0.7 are logged diagnostics only):
#   HARD_PASS = certificate fires AND widening >= 0.03 AND pairwise is popularity-neutral
#               (degree_explained_fraction < 0.5 AND residual pairwise AUROC > freq AUROC).
#   HARD_FAIL = certificate fires AND widening <= 0.0 (no improvement over RA).
#   MIDDLE    = certificate fires AND 0 < widening < 0.03, OR widening >= 0.03 but NOT popularity-neutral.
#   SPLIT_NOT_FREQUENCY_BLIND = no control drove the freq baseline into [0.45,0.55].
#
# ASCII-only. Local CPU. Deterministic (fixed seeds; no hash()-derived RNG; sorted selection). No queue/GPU/atoms.
# Single-shot local run-to-completion (NOT a queue dispatch), so runner start_marker/heartbeat gates do not
# apply; atomic tmp+os.replace metrics write, no bare except, arms-differ check are present.

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
OUT_DIR = os.path.join(REPO, "data", "exp_codex_claimvalidity_pairwise_schemafit")
RESULTS_PATH = os.path.join(OUT_DIR, "metrics.json")

SEED = int(os.environ.get("CV_SEED", "12345"))
NN_CALIPER = float(os.environ.get("CV_CALIPER", "0.20"))

# SR/PPR resolvent discount. verdict = interior 0.6 (pre-registered, NOT tuned); 0.5/0.7 diagnostics.
GAMMAS = [0.5, 0.6, 0.7]
VERDICT_GAMMA = 0.6

# certificate band: frequency baseline is "at/near chance" iff AUROC in [0.45, 0.55]
FREQ_CHANCE_HI = 0.55
FREQ_CHANCE_LO = 0.45

# verdict thresholds
WIDEN_HARD_PASS = 0.03          # pairwise must widen RA's margin-over-freq by >= this
DEG_EXPLAINED_MAX = 0.50        # popularity-neutral iff < this fraction of above-chance signal is degree-explained


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


def residualize_on_degree(score, log_hdeg, log_tdeg):
    """OLS-residualize score against [1, log_hdeg, log_tdeg]; return residual (same orientation as score)."""
    n = len(score)
    A = np.column_stack([np.ones(n), log_hdeg, log_tdeg])
    coef, _, _, _ = np.linalg.lstsq(A, score, rcond=None)
    pred = A @ coef
    return score - pred


# --------------------------- SR / PPR resolvent (reimpl of landed SRSolver) ----
def build_row_normalized_T(adj, n_ent):
    """Undirected adjacency -> dense row-stochastic transition matrix T (float64). Dangling rows stay 0."""
    A = np.zeros((n_ent, n_ent), dtype=np.float64)
    for u in range(n_ent):
        nb = adj[u]
        if nb.shape[0]:
            A[u, nb] = 1.0
    deg = A.sum(axis=1, keepdims=True)
    deg[deg == 0.0] = 1.0
    return A / deg


def sr_resolvent(T, gamma):
    """M = (I - gamma*T)^-1. Same operator as the landed SRSolver (which LU-factors it); here a direct
    dense inverse (n~2034 -> ~2s). M[t,h] = sum over all paths h->...->t weighted by gamma^len, >= 0."""
    n = T.shape[0]
    return np.linalg.inv(np.eye(n, dtype=np.float64) - gamma * T)


def sr_pairwise_scores(M, hidx, tidx):
    """Symmetrized pairwise resolvent score 0.5*(M[t,h]+M[h,t]) per candidate (h,t). h==t -> 0 (never used)."""
    out = np.zeros(len(hidx), dtype=np.float64)
    for i in range(len(hidx)):
        h, t = int(hidx[i]), int(tidx[i])
        if h == t:
            out[i] = 0.0
        else:
            out[i] = 0.5 * (M[t, h] + M[h, t])
    return out


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

    # ---- structural scaffolding from TRAIN only (the SAME adj_found foundation graph) ----
    adj = ra.build_undirected_adj(train_int, n_ent)
    deg = ra.degree_vector(adj)
    nbr = [set(int(x) for x in row) for row in adj]
    rel_freq = Counter(r for h, r, t in train)

    def schema_fit_ra(h_i, t_i):
        """Resource-Allocation pairwise index (the current VET-confirmed schema-fit signal)."""
        if h_i >= n_ent or t_i >= n_ent:
            return 0.0
        common = nbr[h_i] & nbr[t_i]
        val = 0.0
        for z in common:
            dz = deg[z]
            if dz > 0:
                val += 1.0 / dz
        return val

    # ---- SR/PPR resolvent M per gamma (global, computed once; reuses the landed resolvent operator) ----
    print("[sr] building row-normalized T (n_ent=%d) ..." % n_ent, flush=True)
    T = build_row_normalized_T(adj, n_ent)
    M_by_gamma = {}
    for g in GAMMAS:
        tg = time.time()
        M_by_gamma[g] = sr_resolvent(T, g)
        print("[sr] M=(I-%.2f*T)^-1 computed in %.1fs" % (g, time.time() - tg), flush=True)

    # ---- featurizer for a labeled row set ----
    def featurize(rows, labels):
        n = len(rows)
        raw_ra = np.zeros(n)
        hidx = np.zeros(n, dtype=np.int64); tidx = np.zeros(n, dtype=np.int64)
        hdeg = np.zeros(n); tdeg = np.zeros(n); rfreq = np.zeros(n)
        for i, (h, r, t) in enumerate(rows):
            hi, ti = eidx[h], eidx[t]
            hidx[i] = hi; tidx[i] = ti
            raw_ra[i] = schema_fit_ra(hi, ti)
            hdeg[i] = math.log1p(deg[hi])
            tdeg[i] = math.log1p(deg[ti])
            rfreq[i] = math.log1p(rel_freq.get(r, 0))
        feats = {"y": np.array(labels, dtype=np.float64),
                 "schema_fit_ra": raw_ra, "hidx": hidx, "tidx": tidx,
                 "head_deg": hdeg, "tail_deg": tdeg, "rel_freq": rfreq, "rows": rows}
        # SR pairwise per gamma
        for g in GAMMAS:
            feats["sr_g%.2f" % g] = sr_pairwise_scores(M_by_gamma[g], hidx, tidx)
        return feats

    # ---- fairness-control split constructors (deterministic; verbatim from v1) ----
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

    def build_relation_nn_degree_matched(pos, neg, caliper=NN_CALIPER):
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

    CONTROLS = [
        ("full", build_full),
        ("relation_balanced", build_relation_balanced),
        ("relation_degree_matched", build_relation_degree_matched),
        ("relation_nn_degree_matched", build_relation_nn_degree_matched),
    ]
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
        return {"freq_logistic_auroc": logit_auc, "freq_single_best_auroc": best_single,
                "freq_singles": singles, "certificate_auroc": max(logit_auc, best_single)}

    # ---- featurize valid + test ONCE, then subselect per control ----
    print("[featurize] valid + test ...", flush=True)
    F_val_full = featurize(*build_full(val_p, val_n))
    F_test_full = featurize(*build_full(tst_p, tst_n))

    def subselect(Ffull, pos, neg, builder):
        rows, labels = builder(pos, neg)
        used = defaultdict(int); buckets = defaultdict(list)
        for i, tr in enumerate(Ffull["rows"]):
            buckets[tr].append(i)
        out_idx = []
        for tr in rows:
            k = used[tr]; out_idx.append(buckets[tr][k]); used[tr] += 1
        out_idx = np.array(out_idx, dtype=np.int64)
        sub = {k: (v[out_idx] if isinstance(v, np.ndarray) else [v[i] for i in out_idx])
               for k, v in Ffull.items() if k != "rows"}
        sub["rows"] = [Ffull["rows"][i] for i in out_idx]
        sub["y"] = Ffull["y"][out_idx]
        return sub

    # ---- escalate controls until the freq certificate fires ----
    certs = {}
    chosen = None
    for cname, builder in CONTROLS:
        F_te = subselect(F_test_full, tst_p, tst_n, builder)
        F_tr = subselect(F_val_full, val_p, val_n, builder)
        fb = freq_baseline(F_tr, F_te)
        cert_fires = (FREQ_CHANCE_LO <= fb["certificate_auroc"] <= FREQ_CHANCE_HI)
        certs[cname] = {"n_test": len(F_te["y"]), "test_prevalence": float(F_te["y"].mean()),
                        "certificate_fires": cert_fires, **fb}
        print("[certificate] control=%s n_test=%d prev=%.3f freq_cert_auroc=%.3f fires=%s"
              % (cname, len(F_te["y"]), float(F_te["y"].mean()), fb["certificate_auroc"], cert_fires),
              flush=True)
        if cert_fires and chosen is None:
            chosen = (cname, F_tr, F_te, fb)

    results = {"certificates_by_control": certs}

    if chosen is None:
        summary = {
            "dataset": "CoDEx-S triple classification (Safavi & Koutra 2020)",
            "verdict": "SPLIT_NOT_FREQUENCY_BLIND",
            "verdict_msg": ("No fairness control drove the freq baseline to chance [%.2f,%.2f]; "
                            "the schema-fit race is untrustworthy on this split."
                            % (FREQ_CHANCE_LO, FREQ_CHANCE_HI)),
            "results": results, "elapsed_s": time.time() - t0,
        }
        write_metrics(summary); print(json.dumps(summary, indent=2), flush=True); return

    cname, F_tr, F_te, fb = chosen
    yte = F_te["y"]
    freq_auroc = fb["freq_logistic_auroc"]

    # ---- schema-fit arms (parameter-free; eval directly on the chosen test split) ----
    ra_auroc = auroc(yte, F_te["schema_fit_ra"])
    sr_auroc_by_gamma = {("g%.2f" % g): auroc(yte, F_te["sr_g%.2f" % g]) for g in GAMMAS}
    sr_verdict_auroc = sr_auroc_by_gamma["g%.2f" % VERDICT_GAMMA]

    margin_ra_vs_freq = ra_auroc - freq_auroc
    margin_sr_vs_freq = sr_verdict_auroc - freq_auroc
    widening = margin_sr_vs_freq - margin_ra_vs_freq

    # ---- popularity-neutrality: residualize each signal on (log hdeg, log tdeg), re-AUROC ----
    def neutrality(score_key):
        raw = F_te[score_key]
        raw_auc = auroc(yte, raw)
        resid = residualize_on_degree(raw, F_te["head_deg"], F_te["tail_deg"])
        resid_auc = auroc(yte, resid)
        above = raw_auc - 0.5
        frac = float((raw_auc - resid_auc) / above) if above > 1e-9 else 0.0
        frac = max(0.0, min(1.0, frac))
        return {"raw_auroc": raw_auc, "residual_auroc": resid_auc,
                "degree_explained_fraction": frac,
                "residual_beats_freq": bool(resid_auc > freq_auroc)}

    neut_ra = neutrality("schema_fit_ra")
    neut_sr = neutrality("sr_g%.2f" % VERDICT_GAMMA)
    pairwise_pop_neutral = (neut_sr["degree_explained_fraction"] < DEG_EXPLAINED_MAX
                            and neut_sr["residual_beats_freq"])

    # ---- ARMS-MUST-DIFFER (META_RULE_AF): RA vs SR schema-fit signals must not be bit-identical ----
    import hashlib
    dig_ra = hashlib.sha256(np.ascontiguousarray(F_te["schema_fit_ra"]).tobytes()).hexdigest()
    dig_sr = hashlib.sha256(np.ascontiguousarray(F_te["sr_g%.2f" % VERDICT_GAMMA]).tobytes()).hexdigest()
    assert dig_ra != dig_sr, "META_RULE_AF: RA and SR schema-fit signals bit-identical"

    # ---- verdict ----
    cert_fires = True  # chosen implies fired
    hard_pass = cert_fires and (widening >= WIDEN_HARD_PASS) and pairwise_pop_neutral
    hard_fail = cert_fires and (widening <= 0.0)
    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    summary = {
        "dataset": "CoDEx-S triple classification (Safavi & Koutra, EMNLP 2020) -- human-verified hard negatives",
        "chosen_control": cname,
        "n_test": len(yte), "test_prevalence": float(yte.mean()),
        "config": {"gammas": GAMMAS, "verdict_gamma": VERDICT_GAMMA, "seed": SEED,
                   "freq_chance_band": [FREQ_CHANCE_LO, FREQ_CHANCE_HI],
                   "widen_hard_pass": WIDEN_HARD_PASS, "deg_explained_max": DEG_EXPLAINED_MAX},
        "fairness_certificate": {
            "control_used": cname,
            "frequency_baseline_certificate_auroc": fb["certificate_auroc"],
            "freq_logistic_auroc": freq_auroc,
            "freq_single_best_auroc": fb["freq_single_best_auroc"],
            "certificate_fires_near_chance": True,
            "band": [FREQ_CHANCE_LO, FREQ_CHANCE_HI],
        },
        "schema_fit_arms": {
            "RA_pairwise_auroc": ra_auroc,
            "SR_PPR_pairwise_auroc_verdict_gamma": sr_verdict_auroc,
            "SR_PPR_pairwise_auroc_by_gamma": sr_auroc_by_gamma,
            "frequency_baseline_auroc": freq_auroc,
        },
        "decisive": {
            "margin_RA_vs_freq": margin_ra_vs_freq,
            "margin_SR_pairwise_vs_freq": margin_sr_vs_freq,
            "widening_SR_over_RA": widening,
            "widen_hard_pass_threshold": WIDEN_HARD_PASS,
        },
        "popularity_neutrality": {
            "RA": neut_ra,
            "SR_PPR_verdict_gamma": neut_sr,
            "pairwise_popularity_neutral": pairwise_pop_neutral,
        },
        "prereg_bands": {
            "HARD_PASS": "cert fires AND widening>=%.2f AND pairwise popularity-neutral (deg_frac<%.2f AND resid>freq)"
                         % (WIDEN_HARD_PASS, DEG_EXPLAINED_MAX),
            "HARD_FAIL": "cert fires AND widening<=0.0 (no improvement over RA)",
            "MIDDLE": "cert fires AND 0<widening<%.2f, OR widens but not popularity-neutral" % WIDEN_HARD_PASS,
            "SPLIT_NOT_FREQUENCY_BLIND": "no control drove freq baseline into [0.45,0.55]",
        },
        "verdict": verdict,
        "honesty_notes": [
            "margin reported as MARGIN-OVER-FREQ (RA baseline currently ~+0.07 per the VET-confirmed v1 win), not absolute.",
            "verdict gamma=0.6 is a pre-registered interior value; 0.5/0.7 are logged sensitivity diagnostics, NOT selected-for-pass.",
            "SR/PPR resolvent M=(I-gamma*T)^-1 reimplements the landed SRSolver operator; self-test reproduces its 'SR recovers reachability' property.",
            "popularity-neutrality: pairwise signal residualized on (log head_deg, log tail_deg); a win that dies under residualization is degree, not schema-fit.",
            "same frequency-blind split + freq-at-chance certificate as exp_codex_claimvalidity_frequency_vs_structural_v1.py; all arms scored on identical test rows; parameter-free schema-fit arms eval directly (no fit, no leak).",
        ],
        "results": results,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2), flush=True)


def write_metrics(summary):
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = RESULTS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp, RESULTS_PATH)


# --------------------------- self-test (positive controls; fast) ---------------
def self_test():
    """Positive controls: (1) SR resolvent recovers reachability (landed-component property);
    (2) RA index behaves; (3) arms differ. No CoDEx data touched."""
    # planted graph: 0-1-2-3 chain + isolated 4,5. reachable pairs should get higher SR than unreachable.
    n = 6
    A = np.zeros((n, n))
    for a, b in [(0, 1), (1, 2), (2, 3)]:
        A[a, b] = 1; A[b, a] = 1
    deg = A.sum(axis=1, keepdims=True); deg[deg == 0] = 1
    T = A / deg
    M = sr_resolvent(T, 0.6)
    # 0->3 (reachable through chain) must score > 0->5 (isolated -> 0)
    s_03 = 0.5 * (M[3, 0] + M[0, 3])
    s_05 = 0.5 * (M[5, 0] + M[0, 5])
    assert s_03 > s_05 + 1e-9, "SR self-test: reachable pair not > unreachable (%.4f vs %.4f)" % (s_03, s_05)
    assert s_05 < 1e-9, "SR self-test: isolated-node pair should be ~0 (%.6f)" % s_05
    # closer pair scores higher than farther pair (multi-length decay)
    s_01 = 0.5 * (M[1, 0] + M[0, 1]); s_03b = 0.5 * (M[3, 0] + M[0, 3])
    assert s_01 > s_03b, "SR self-test: adjacent pair not > distance-3 pair (%.4f vs %.4f)" % (s_01, s_03b)

    # RA index on the chain 0-1-2-3: nodes 1 and 3 share exactly common neighbor 2 (deg 2) -> RA(1,3)=1/2.
    nbr = [set(np.nonzero(A[i])[0].tolist()) for i in range(n)]
    common = nbr[1] & nbr[3]
    ra_13 = sum(1.0 / int(A[z].sum()) for z in common if A[z].sum() > 0)
    assert abs(ra_13 - 0.5) < 1e-9, "RA self-test: expected RA(1,3)=1/deg(2)=0.5, got %.4f" % ra_13

    # arms differ on a small vector
    import hashlib
    v_ra = np.array([ra_13, 0.0, 0.5]); v_sr = np.array([s_03, s_05, s_01])
    assert hashlib.sha256(v_ra.tobytes()).hexdigest() != hashlib.sha256(v_sr.tobytes()).hexdigest()

    # residualize sanity: perfectly degree-explained signal -> residual ~0 -> AUROC ~0.5
    hd = np.array([1.0, 2.0, 3.0, 4.0]); td = np.array([1.0, 1.0, 1.0, 1.0])
    score = 2.0 * hd + 1.0  # pure linear in degree
    resid = residualize_on_degree(score, hd, td)
    assert np.abs(resid).max() < 1e-6, "residualize self-test: pure-degree signal should residualize to ~0"
    print("SELFTEST_PASS: SR-recovers-reachability + RA + arms-differ + residualize all OK", flush=True)


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
