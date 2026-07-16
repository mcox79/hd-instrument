"""Threshold-FREE / self-calibrating copy-dependence detector; re-test on BOTH
Weather (labeled copy graph) and Book (truth-value of copy-correction).

DESIGN-VALIDATION / REAL-DATA CHECK. NOT a substrate cell. Produces NO atoms.
No queue, no GPU/CPU dispatch, no origin push. Pure-Python (numpy + stdlib),
runs inline (plus the same one-time dataset downloads the predecessors use).

WHY (closing the open caveat): the committed Book result
`experiments/real_book_copy_correction_truth_2026-07-16.py` (commit ba22edcce)
is HARD-PASS-CONDITIONAL: copy-correction beats naive at excess-agreement
threshold 0.15, but 0.15 was HAND-SET -- inherited from the sibling Weather cell
`experiments/real_weather_copy_corroboration_validity_2026-07-16.py` (ac491e78e),
where it was calibrated against a LABELED copy graph. On Book the verdict FLIPS
sign at conservative thresholds (>=0.25) and Book has NO copy labels to tune on.
The caveat: the win is contingent on a magic number transferred from a different
corpus. This cell removes the magic number.

WHAT'S NEW: a SELF-CALIBRATING detector that sets its OWN operating point per
corpus with NO external label. Two principled variants (per the data-fusion /
weak-supervision literature: Dong/Berti-Equille joint reliability+dependence
inference; Efron empirical-null / Benjamini-Hochberg FDR control):

  PRIMARY  = per-pair one-sided BINOMIAL exact test + Benjamini-Hochberg FDR.
    For each source pair (i,j) with n co-reported objects, the number of
    agreements A ~ Binomial(n, p_exp) under INDEPENDENCE, where
    p_exp = ri*rj + (1-ri)(1-rj)*c is the same expected-independent-agreement
    the committed detector subtracts. The one-sided upper-tail p-value
    P(A >= observed) is a principled per-pair excess-agreement test whose scale
    (a p-value in [0,1]) is UNIVERSAL, not corpus-specific like a raw excess.
    The operating point is set by Benjamini-Hochberg FDR control at level q
    across ALL tested pairs -- a standard statistical convention, NOT a tuned
    excess threshold. Crucially the null is computed PER PAIR from that pair's
    own (ri, rj, overlap n, c): a large-overlap pair needs only a small excess
    to be significant; a thin-overlap pair needs a large one. The fixed 0.15
    ignored overlap; this uses it. So the operating point self-adapts to each
    corpus's own overlap + reliability structure with no hand tuning.

  ROBUSTNESS = Efron-style EMPIRICAL-NULL FDR. Trusting p_exp requires trusting
    the reliability estimates; the empirical null does not. It fits the central
    (independent) mass of the observed excess distribution robustly
    (median + 1.4826*MAD -> a Gaussian null), scores each pair's excess as an
    upper-tail deviate against THAT null, and BH-FDR-selects the outliers. This
    is "the data's own excess-agreement null distribution" (landscape note's
    phrasing) and is agnostic to p_exp mis-estimation. Reported alongside the
    primary as an independent cross-check; needs many pairs (Book/Weather scale).

The verdict is reported across an FDR-LEVEL SWEEP q in {0.01, 0.05, 0.10}. Where
the OLD cell's threshold sweep FLIPPED sign (0.15 -> 0.25+), a STABLE band across
q AND across the two methods is the evidence that removes the conditional caveat.

REUSE (per contract -- keep predecessors' parse + truth-eval): the committed
detector `detect_dependence_realvalued`, the reuse-integrity equivalence
self-test, prf/auc_score, GOLD/CROSSED/SILVER copy labels, the Weather object
matrix, and the ERA5 truth fetch are IMPORTED from the Weather cell. The Book
parse (parse_book/parse_truth/lastname_set/isbn13/jaccard/binom_sf_half) is
IMPORTED from the Book cell. The Book value-matrix build and the naive-vs-
corrected truth scoring are transcribed VERBATIM from the Book cell's evaluate_at
(the ONLY change is the detector operating-point selection, isolated in a
detector-factory so the identical downstream scoring runs on both the hand-tuned
0.15 clusters and the self-calibrated clusters). Reuse-integrity self-tests
prove (a) the imported detector reduces to the committed toy at c=1, (b) our
pairwise stats reproduce the committed detector's excess map, and (c) our
union-find clustering at a fixed threshold reproduces the committed detector's
clusters -- so ONLY the selection rule differs from committed code.

Pre-registered bands (removes the conditional caveat iff HARD-PASS):
  Let PRIMARY = binomial-FDR at q=0.05 (the self-set operating point, no 0.15).
  WEATHER component (detector recovery vs labeled gold copy graph):
    W-PASS = the FDR-selected detector recovers gold copies above shuffled
             chance (permutation p < 0.05) AND flags >= as many gold edges as the
             hand-tuned 0.15 detector while flagging NO MORE crossed (labeled
             hard-negative) edges than 0.15. (AUC of the excess ranking is
             operating-point-invariant and reported for context.)
  BOOK component (truth-value of copy-correction, error-propagating regime):
    B-PASS = at the self-set operating point, on subset B (books where corrected
             pick != naive pick): |B| >= 20 AND corrected win-rate >= 0.60 AND
             one-sided binomial p < 0.05 AND overall corrected mean-Jaccard NOT
             worse than naive (>= naive - 0.005) -- i.e. it REPRODUCES the Book
             cell's HARD-PASS bands WITHOUT the 0.15 tuning, and matches or beats
             the hand-tuned 0.15 corrected-vs-naive delta.
  HARD-PASS = W-PASS AND B-PASS AND the Book band is STABLE (does not flip to
              FAIL) across q in {0.01,0.05,0.10}. => the self-calibrated detector
              matches/beats the hand-tuned 0.15 result with NO external label =>
              the conditional caveat is REMOVED.
  HARD-FAIL = self-calibration can't match the hand-tuned operating point: Book
              corrected NOT > naive at the self-set point (win-rate <= 0.5 or |B|
              collapses < 20 or overall clearly worse) OR Weather recovery at
              chance (perm p >= 0.5). => no robust unsupervised win, the caveat
              STANDS (honest negative).
  MIDDLE    = otherwise (one component works, or directional but not decisive,
              or band unstable across q).

Self-tests run FIRST (reuse-integrity + SELF-CALIBRATION VALIDATION): on SYNTHETIC
data with a KNOWN planted copy structure, the self-set operating point (NO
threshold passed in) must recover the planted copies -- exact copy-graph recovery
on the toy generator AND on a second, differently-planted graph. If any fails the
real-data metrics are not trustworthy and the script aborts.
"""

import argparse
import collections
import importlib.util
import math
import os
import statistics
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEATHER_PATH = os.path.join(
    REPO, "experiments", "real_weather_copy_corroboration_validity_2026-07-16.py")
BOOK_PATH = os.path.join(
    REPO, "experiments", "real_book_copy_correction_truth_2026-07-16.py")

# Self-calibration knobs (NOT operating-point thresholds -- these are universal
# statistical conventions, swept for stability, never a corpus-specific excess).
FDR_Q_PRIMARY = 0.05
FDR_Q_SWEEP = [0.01, 0.05, 0.10]
EXACT_BINOM_N = 200          # exact binomial for n <= this, else normal approx
HAND_TUNED_THRESH = 0.15     # the INHERITED value, used ONLY as the baseline to
                             # match/beat -- never as our operating point.


# ---------------------------------------------------------------------------
# module loader
# ---------------------------------------------------------------------------
def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# Self-calibrating detector core (the ONLY new machinery vs committed code).
# ---------------------------------------------------------------------------
def _phi_sf(z):
    """Upper-tail standard-normal survival 1 - Phi(z), stdlib erfc."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def binom_upper_pvalue(k, n, p):
    """One-sided P(X >= k) for X ~ Binomial(n, p). Exact for n <= EXACT_BINOM_N,
    else normal approximation with continuity correction. p clamped off {0,1}."""
    if n <= 0 or k <= 0:
        return 1.0
    if k > n:
        return 0.0
    p = min(max(p, 1e-9), 1.0 - 1e-9)
    if n <= EXACT_BINOM_N:
        tot = 0.0
        for i in range(k, n + 1):
            tot += math.comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
        return min(max(tot, 0.0), 1.0)
    mu = n * p
    var = n * p * (1.0 - p)
    if var <= 0:
        return 1.0 if k <= mu else 0.0
    z = (k - 0.5 - mu) / math.sqrt(var)
    return _phi_sf(z)


def bh_fdr(pvals, q):
    """Benjamini-Hochberg step-up. Returns the set of indices rejected at FDR q.
    m (denominator) = number of tested hypotheses = len(pvals)."""
    m = len(pvals)
    if m == 0:
        return set()
    order = sorted(range(m), key=lambda i: pvals[i])
    kmax = 0
    for rank, idx in enumerate(order, start=1):
        if pvals[idx] <= (rank / m) * q:
            kmax = rank
    return set(order[:kmax])


def pairwise_stats(value, rel, c, min_overlap, missing):
    """Per-pair excess-agreement components over co-reported objects. Returns a
    list of dicts (i,j,n,agree,exp,excess,k). excess == committed detector's
    excess_map entry (asserted equal in the reuse-integrity self-test)."""
    S = value.shape[1]
    out = []
    for i in range(S):
        vi = value[:, i]
        for j in range(i + 1, S):
            vj = value[:, j]
            both = (vi != missing) & (vj != missing)
            n = int(both.sum())
            if n < min_overlap:
                continue
            agree = float((vi[both] == vj[both]).mean())
            ri, rj = rel[i], rel[j]
            exp = ri * rj + (1.0 - ri) * (1.0 - rj) * c
            out.append(dict(i=i, j=j, n=n, agree=agree, exp=exp,
                            excess=agree - exp, k=int(round(agree * n))))
    return out


def fdr_edges_binom(stats, q):
    """Self-calibrated flagged edge set via per-pair binomial test + BH-FDR.
    Non-positive-excess pairs get p=1.0 (upper tail >= 0.5, never rejected at
    q <= 0.10) -- a conservative shortcut that skips the expensive exact sum."""
    pvals = []
    for s in stats:
        if s["excess"] <= 0.0:
            pvals.append(1.0)
        else:
            pvals.append(binom_upper_pvalue(s["k"], s["n"], s["exp"]))
    rej = bh_fdr(pvals, q)
    edges = set((stats[i]["i"], stats[i]["j"]) for i in rej)
    return edges, pvals


def fdr_edges_empirical(stats, q):
    """Efron empirical-null FDR: fit central mass of the excess distribution
    (median + 1.4826*MAD), score each pair as an upper-tail deviate, BH-select.
    Returns (edges, m0, s0) or None if too few pairs to fit a null."""
    if len(stats) < 30:
        return None
    ex = np.array([s["excess"] for s in stats], dtype=float)
    m0 = float(np.median(ex))
    mad = float(np.median(np.abs(ex - m0)))
    s0 = 1.4826 * mad if mad > 0 else (float(ex.std()) or 1.0)
    pvals = [_phi_sf((e - m0) / s0) for e in ex]
    rej = bh_fdr(pvals, q)
    edges = set((stats[i]["i"], stats[i]["j"]) for i in rej)
    return edges, m0, s0


def estimate_reliability(value, missing, min_reporters=3):
    """Estimate per-source reliability as P(agree with consensus) -- the SAME
    procedure the committed Weather and Book cells use (consensus = mode among
    >= min_reporters reporters). The real pipeline never has 'declared'
    reliabilities, so any faithful self-test must estimate them this way too.
    Note: a copy of a good source correctly gets a HIGH estimated reliability
    (it agrees with consensus a lot); its copy status is detected from EXCESS
    agreement with its parent beyond that reliability, not from a low estimate."""
    K, S = value.shape
    cons = np.full(K, missing)
    for k in range(K):
        row = value[k][value[k] != missing]
        if len(row) >= min_reporters:
            vals, cnts = np.unique(row, return_counts=True)
            cons[k] = int(vals[np.argmax(cnts)])
    rel = np.zeros(S)
    for si in range(S):
        m = (value[:, si] != missing) & (cons != missing)
        rel[si] = float((value[m, si] == cons[m]).mean()) if m.sum() else 0.0
    return rel


def clusters_from_edges(S, edges):
    """Union-find over a flagged edge set -> cluster id per source (same union-
    find used by the committed detector; only the edge SOURCE differs)."""
    parent = list(range(S))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for (i, j) in edges:
        parent[find(i)] = find(j)
    return np.array([find(s) for s in range(S)])


# ---------------------------------------------------------------------------
# Reuse-integrity + self-calibration validation self-tests (NO network).
# ---------------------------------------------------------------------------
def _co_membership(clusters):
    S = len(clusters)
    return np.array([[clusters[a] == clusters[b] for b in range(S)]
                     for a in range(S)])


def reuse_integrity_self_test(w, toy):
    """(a) committed detector reduces to committed toy at c=1 (reuse w's test).
    (b) our pairwise_stats excess reproduces the committed excess_map.
    (c) our union-find at a fixed threshold reproduces committed clusters.
    All on the toy's own binary generator. Returns (ok, notes)."""
    notes = []
    ok = True

    # (a) delegate to the committed equivalence self-test.
    eq = w.equivalence_self_test(toy)
    notes.append("(a) imported detector == committed toy at c=1: %s"
                 % ("PASS" if eq else "FAIL"))
    ok = ok and eq

    cfg = toy.Cfg()
    rng = np.random.default_rng(cfg.seed)
    G = toy.build_generator(cfg, rng)
    value = G["value"]                 # (K,S) binary, missing = -1
    rel = cfg.reliabilities
    thr = cfg.dep_excess_thresh
    ovl = cfg.dep_min_overlap

    # committed detector reference (excess_map + clusters) at MISSING = -1.
    old = w.MISSING
    w.MISSING = -1
    try:
        ref_clusters, ref_edges, ref_excess = w.detect_dependence_realvalued(
            value, rel, 1.0, thr, ovl)
    finally:
        w.MISSING = old

    # (b) excess equivalence.
    stats = pairwise_stats(value, rel, 1.0, ovl, -1)
    max_dex = 0.0
    for s in stats:
        ref = ref_excess.get((s["i"], s["j"]))
        if ref is None:
            ok = False
            notes.append("(b) FAIL: pair %s missing in committed excess_map"
                         % ((s["i"], s["j"]),))
            break
        max_dex = max(max_dex, abs(ref - s["excess"]))
    notes.append("(b) our excess vs committed excess_map: max|delta|=%.2e -> %s"
                 % (max_dex, "PASS" if max_dex < 1e-9 else "FAIL"))
    ok = ok and (max_dex < 1e-9)

    # (c) union-find equivalence at the same fixed threshold.
    our_edges = set((s["i"], s["j"]) for s in stats if s["excess"] > thr)
    our_clusters = clusters_from_edges(value.shape[1], our_edges)
    same = bool((_co_membership(our_clusters) == _co_membership(ref_clusters)).all())
    notes.append("(c) our union-find(thr=%.2f) == committed clusters: %s"
                 % (thr, "PASS" if same else "FAIL"))
    ok = ok and same
    return ok, notes


def _recover_planted(toy, n_sources, reliabilities, copy_parent, n_claims, seed,
                     ovl):
    """Run the SELF-CALIBRATED (binomial-FDR, NO threshold passed) detector on a
    synthetic corpus with a KNOWN planted copy graph; return (recovered_ok,
    detail). Reliabilities are ESTIMATED from consensus (real-pipeline faithful),
    NOT taken from the generator's declared values. Binary values -> c = 1.0."""
    cfg = toy.Cfg()
    cfg.n_sources = n_sources
    cfg.reliabilities = np.array(reliabilities)
    cfg.copy_parent = np.array(copy_parent)
    cfg.n_claims = n_claims
    cfg.seed = seed
    rng = np.random.default_rng(seed)
    G = toy.build_generator(cfg, rng)
    value = G["value"]
    rel = estimate_reliability(value, -1)                    # as the real pipeline
    stats = pairwise_stats(value, rel, 1.0, ovl, -1)
    edges, _ = fdr_edges_binom(stats, FDR_Q_PRIMARY)          # self-set, no thr
    clusters = clusters_from_edges(value.shape[1], edges)
    S = value.shape[1]

    def root(s):
        while cfg.copy_parent[s] >= 0:
            s = cfg.copy_parent[s]
        return s
    planted = np.array([[root(a) == root(b) for b in range(S)] for a in range(S)])
    got = _co_membership(clusters)
    ok = bool((planted == got).all())
    n_planted = sum(1 for a in range(S) for bb in range(a + 1, S)
                    if root(a) == root(bb))
    return ok, dict(clusters=clusters.tolist(), n_edges=len(edges),
                    n_planted=n_planted)


def self_calibration_validation(toy):
    """The key new self-test (per contract): on synthetic data with known copy
    structure, the SELF-SET operating point (no hand threshold) recovers the
    planted copies. Cases use MINORITY-copy structures (the realistic regime;
    when copiers form a consensus-capturing majority the excess signal collapses
    for the committed detector too -- an honest limitation, not specific to
    self-calibration)."""
    notes = []
    ok = True
    cases = [
        # (label, n_sources, reliabilities, copy_parent, n_claims, seed, overlap)
        ("6src two-cluster {0<-4},{1<-5}", 6,
         [0.92, 0.88, 0.80, 0.72, 0.62, 0.55], [-1, -1, -1, -1, 0, 1],
         200, 20260717, 15),
        ("12src minority cluster {0,9,10,11}", 12,
         [0.93, 0.90, 0.88, 0.85, 0.82, 0.80, 0.77, 0.74, 0.70, 0.62, 0.58, 0.55],
         [-1] * 9 + [0, 0, 0], 600, 20260716, 30),
    ]
    for label, ns, rels, cp, nc, seed, ovl in cases:
        rec_ok, detail = _recover_planted(toy, ns, rels, cp, nc, seed, ovl)
        notes.append("  %-36s recovered=%s (planted_edges=%d flagged=%d)"
                     % (label, rec_ok, detail["n_planted"], detail["n_edges"]))
        ok = ok and rec_ok
    return ok, notes


# ---------------------------------------------------------------------------
# Binomial one-sided p (P(X >= k) under Binom(n, 0.5)) -- reused from Book cell
# for the corrected-vs-naive subset-B test (kept identical).
# ---------------------------------------------------------------------------
def binom_sf_half(k, n):
    if n == 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i)
    return total / (2.0 ** n)


# ===========================================================================
# WEATHER re-test: detector recovery vs labeled gold copy graph.
# ===========================================================================
def weather_object_matrix(w, data_dir):
    """Transcribed from the Weather cell main: build (object x temp-source) int
    matrix of per-slot median temps, plus rel + empirical collision c."""
    sources = sorted(w.EXPECTED_ID)
    temp_sources = sorted(w.TEMPCOL)
    per_src_temp = {}
    for name in sources:
        _hid, recs = w.read_source(data_dir, name)
        if name in w.TEMPCOL:
            slotbuf = {}
            for (t, c, v) in recs:
                if v is None:
                    continue
                slot = int(t.timestamp() / 60.0 // w.SLOT_MIN)
                slotbuf.setdefault((c, slot), []).append(v)
            per_src_temp[name] = {k: int(round(statistics.median(vs)))
                                  for k, vs in slotbuf.items()}
    objs = sorted(set().union(*[set(per_src_temp[n]) for n in temp_sources]))
    oi = {o: k for k, o in enumerate(objs)}
    K, S = len(objs), len(temp_sources)
    val = np.full((K, S), w.MISSING, dtype=int)
    for si, n in enumerate(temp_sources):
        for o, v in per_src_temp[n].items():
            val[oi[o], si] = v
    cons = np.full(K, w.MISSING)
    for k in range(K):
        row = val[k][val[k] != w.MISSING]
        if len(row) >= 3:
            cons[k] = int(round(np.median(row)))
    rel = np.zeros(S)
    for si in range(S):
        m = (val[:, si] != w.MISSING) & (cons != w.MISSING)
        rel[si] = float((val[m, si] == cons[m]).mean()) if m.sum() else 0.0
    devs = []
    for si in range(S):
        m = (val[:, si] != w.MISSING) & (cons != w.MISSING)
        d = val[m, si] - cons[m]
        devs += list(d[d != 0])
    devs = np.asarray(devs)
    _, cnts = np.unique(devs, return_counts=True)
    pmf = cnts / cnts.sum()
    c_collision = float((pmf ** 2).sum())
    return val, rel, c_collision, temp_sources


def weather_retest(w, data_dir):
    w.ensure_dataset(data_dir)
    val, rel, c_collision, temp_sources = weather_object_matrix(w, data_dir)
    idx = {n: i for i, n in enumerate(temp_sources)}
    ovl = w.DEP_MIN_OVERLAP

    stats = pairwise_stats(val, rel, c_collision, ovl, w.MISSING)
    excess = {(s["i"], s["j"]): s["excess"] for s in stats}
    universe = set(excess)

    def epair(a, b):
        i, j = idx[a], idx[b]
        return (min(i, j), max(i, j))

    def obs(es):
        out = set()
        for a, b in es:
            if a in idx and b in idx:
                out.add(epair(a, b))
        return out & universe

    gold_obs = obs(w.GOLD_EDGES)
    silver_obs = obs(w.SILVER_EDGES)
    crossed_obs = obs(w.CROSSED_EDGES)

    # operating-point-INVARIANT ranking metric (context).
    ulist = sorted(universe)
    scores = np.array([excess[p] for p in ulist])
    labels = np.array([1 if p in gold_obs else 0 for p in ulist])
    auc_gold = w.auc_score(scores, labels)
    gc = [p for p in ulist if p in gold_obs or p in crossed_obs]
    auc_gc = w.auc_score([excess[p] for p in gc],
                         [1 if p in gold_obs else 0 for p in gc])

    def eval_detected(detected):
        p_g, r_g, f_g, tp_g = w.prf(detected, gold_obs, universe)
        gold_flagged = tp_g
        crossed_flagged = sum(1 for p in crossed_obs if p in detected)
        # shuffled-label permutation chance on F1 (same as Weather cell).
        rng = np.random.default_rng(20260716)
        npos = len(gold_obs)
        chance = []
        for _ in range(20000):
            pick = set(map(tuple, np.array(ulist, dtype=object)[
                rng.choice(len(ulist), size=npos, replace=False)]))
            _, _, f, _ = w.prf(detected, pick, universe)
            chance.append(f)
        chance = np.asarray(chance)
        p_emp = float((chance >= f_g).mean())
        return dict(f1=f_g, prec=p_g, rec=r_g, gold_flagged=gold_flagged,
                    crossed_flagged=crossed_flagged, p_emp=p_emp,
                    n_detected=len(detected), ch95=float(np.percentile(chance, 95)))

    # baseline: the hand-tuned 0.15 detector.
    base_detected = set(p for p in universe if excess[p] > HAND_TUNED_THRESH)
    base = eval_detected(base_detected)

    # self-calibrated: binomial-FDR sweep + empirical-null cross-check.
    fdr_runs = {}
    for q in FDR_Q_SWEEP:
        edges, _ = fdr_edges_binom(stats, q)
        fdr_runs[q] = eval_detected(edges & universe)
    emp = fdr_edges_empirical(stats, FDR_Q_PRIMARY)
    emp_eval = None
    emp_info = None
    if emp is not None:
        e_edges, m0, s0 = emp
        emp_eval = eval_detected(e_edges & universe)
        emp_info = (m0, s0)

    return dict(universe=len(universe), gold=len(gold_obs), crossed=len(crossed_obs),
                auc_gold=auc_gold, auc_gc=auc_gc, base=base, fdr=fdr_runs,
                emp=emp_eval, emp_info=emp_info)


# ===========================================================================
# BOOK re-test: truth-value of copy-correction at the self-set operating point.
# ===========================================================================
def book_value_matrix(b, w, data_dir):
    """Transcribed from the Book cell main: (book x source) value-id matrix +
    consensus/reliability/collision; returns everything the eval needs."""
    book_txt, gold_txt, silver_txt = b.ensure_dataset(data_dir)
    claims, sources, books = b.parse_book(book_txt)
    silver = b.parse_truth(silver_txt)
    gold = b.parse_truth(gold_txt, gold=True)

    set_id = {}

    def gid(fs):
        if fs not in set_id:
            set_id[fs] = len(set_id)
        return set_id[fs]

    src_list = sorted(sources)
    src_idx = {s: i for i, s in enumerate(src_list)}
    book_list = sorted(books)
    book_idx = {bk: k for k, bk in enumerate(book_list)}
    K, S = len(book_list), len(src_list)
    MISSING = w.MISSING
    val = np.full((K, S), MISSING, dtype=int)
    for (isbn, src), fs in claims.items():
        if not fs:
            continue
        val[book_idx[isbn], src_idx[src]] = gid(fs)

    reports_per_src = (val != MISSING).sum(axis=0)
    cons = np.full(K, MISSING)
    for k in range(K):
        row = val[k][val[k] != MISSING]
        if len(row) >= b.MIN_REPORTERS:
            vals, cnts = np.unique(row, return_counts=True)
            cons[k] = int(vals[np.argmax(cnts)])
    rel = np.zeros(S)
    for si in range(S):
        m = (val[:, si] != MISSING) & (cons != MISSING)
        rel[si] = float((val[m, si] == cons[m]).mean()) if m.sum() else 0.0
    coll_terms = []
    for k in range(K):
        if cons[k] == MISSING:
            continue
        row = val[k][val[k] != MISSING]
        wrong = row[row != cons[k]]
        if len(wrong) >= 2:
            _, cnts = np.unique(wrong, return_counts=True)
            p = cnts / cnts.sum()
            coll_terms.append(float((p ** 2).sum()))
    c_collision = float(np.mean(coll_terms)) if coll_terms else 0.0
    inv = {i: fs for fs, i in set_id.items()}
    return dict(val=val, rel=rel, c_collision=c_collision, book_list=book_list,
                reports_per_src=reports_per_src, inv=inv, silver=silver, gold=gold,
                S=S, K=K, n_valueids=len(set_id))


def book_eval(b, w, D, clusters, truth_map):
    """Transcribed VERBATIM from the Book cell's evaluate_at scoring (naive =
    raw source count, corrected = distinct detected-cluster count); the ONLY
    change vs the Book cell is that `clusters` is supplied externally instead of
    being computed by the hand-tuned detector inline."""
    val, book_list, inv = D["val"], D["book_list"], D["inv"]
    K = D["K"]
    MISSING = w.MISSING
    MIN_REPORTERS = b.MIN_REPORTERS

    jn_all, jc_all, en_all, ec_all = [], [], [], []
    n_disagree = B_cw = B_nw = B_tie = B_size = 0
    B_exact_c = B_exact_n = evaluated = 0
    for k in range(K):
        tset = truth_map.get(book_list[k])
        if not tset:
            continue
        row_srcs = np.where(val[k] != MISSING)[0]
        if len(row_srcs) < MIN_REPORTERS:
            continue
        evaluated += 1
        by_val = collections.defaultdict(list)
        for si in row_srcs:
            by_val[int(val[k, si])].append(si)
        if len(by_val) >= 2:
            n_disagree += 1
        naive_score = {v: len(ss) for v, ss in by_val.items()}
        corr_score = {v: len(set(clusters[s] for s in ss))
                      for v, ss in by_val.items()}

        def pick(score):
            return max(score, key=lambda v: (score[v], naive_score[v], -v))
        npick, cpick = pick(naive_score), pick(corr_score)
        pn, pc = inv[npick], inv[cpick]
        jn, jc = b.jaccard(pn, tset), b.jaccard(pc, tset)
        jn_all.append(jn); jc_all.append(jc)
        en_all.append(float(pn == tset)); ec_all.append(float(pc == tset))
        if npick != cpick:
            B_size += 1
            B_exact_c += int(pc == tset); B_exact_n += int(pn == tset)
            if jc > jn:
                B_cw += 1
            elif jn > jc:
                B_nw += 1
            else:
                B_tie += 1
    denom = B_cw + B_nw
    return dict(
        evaluated=evaluated, n_disagree=n_disagree, B_size=B_size, B_cw=B_cw,
        B_nw=B_nw, B_tie=B_tie, B_exact_c=B_exact_c, B_exact_n=B_exact_n,
        mjn=float(np.mean(jn_all)) if jn_all else 0.0,
        mjc=float(np.mean(jc_all)) if jc_all else 0.0,
        men=float(np.mean(en_all)) if en_all else 0.0,
        mec=float(np.mean(ec_all)) if ec_all else 0.0,
        denom=denom, win_rate=(B_cw / denom if denom else float("nan")),
        p_bin=(binom_sf_half(B_cw, denom) if denom else float("nan")))


def book_band(r):
    """Transcribed VERBATIM from the Book cell's band()."""
    overall_not_worse = r["mjc"] >= r["mjn"] - 0.005
    overall_clearly_worse = r["mjc"] < r["mjn"] - 0.01
    hp = (r["B_size"] >= 20 and r["denom"] > 0 and r["win_rate"] >= 0.60
          and r["p_bin"] < 0.05 and overall_not_worse)
    hf = (r["denom"] > 0 and r["B_cw"] <= r["B_nw"]) or overall_clearly_worse
    return "HARD-PASS" if hp else ("HARD-FAIL" if hf else "MIDDLE")


def book_clusters(D, w, det_srcs, detector):
    """Build global cluster ids exactly as the Book cell does: big sources get
    detector cluster ids, all other sources stay singleton. `detector(sub,
    sub_rel)` returns a length-len(det_srcs) local cluster array."""
    S = D["S"]
    sub_rel = D["rel"][det_srcs]
    sub = D["val"][:, det_srcs]
    sub_clusters = detector(sub, sub_rel)
    clusters = np.arange(S) + 10_000_000
    for local_i, si in enumerate(det_srcs):
        clusters[si] = int(sub_clusters[local_i])
    return clusters


def book_retest(b, w, data_dir, truth_choice):
    D = book_value_matrix(b, w, data_dir)
    truth_map = D["silver"] if truth_choice == "silver" else (
        D["gold"] if truth_choice == "gold" else {**D["silver"], **D["gold"]})
    det_srcs = [si for si in range(D["S"])
                if D["reports_per_src"][si] >= b.MIN_REPORTS_DET]
    c = D["c_collision"]
    ovl = b.DEP_MIN_OVERLAP

    # baseline detector: hand-tuned 0.15 (committed path).
    def base_detector(sub, sub_rel):
        cl, _, _ = w.detect_dependence_realvalued(
            sub, sub_rel, c, HAND_TUNED_THRESH, ovl)
        return cl

    base_clusters = book_clusters(D, w, det_srcs, base_detector)
    base_r = book_eval(b, w, D, base_clusters, truth_map)

    # self-calibrated detectors: binomial-FDR sweep + empirical-null.
    def make_binom_detector(q):
        def det(sub, sub_rel):
            stats = pairwise_stats(sub, sub_rel, c, ovl, w.MISSING)
            edges, _ = fdr_edges_binom(stats, q)
            return clusters_from_edges(sub.shape[1], edges)
        return det

    fdr_r = {}
    fdr_nedges = {}
    for q in FDR_Q_SWEEP:
        stats = pairwise_stats(D["val"][:, det_srcs], D["rel"][det_srcs], c, ovl,
                               w.MISSING)
        edges, _ = fdr_edges_binom(stats, q)
        fdr_nedges[q] = len(edges)
        cl = book_clusters(D, w, det_srcs, make_binom_detector(q))
        fdr_r[q] = book_eval(b, w, D, cl, truth_map)

    # empirical-null at primary q.
    def emp_detector(sub, sub_rel):
        stats = pairwise_stats(sub, sub_rel, c, ovl, w.MISSING)
        res = fdr_edges_empirical(stats, FDR_Q_PRIMARY)
        edges = res[0] if res is not None else set()
        return clusters_from_edges(sub.shape[1], edges)
    emp_clusters = book_clusters(D, w, det_srcs, emp_detector)
    emp_r = book_eval(b, w, D, emp_clusters, truth_map)

    # baseline edge count for context.
    base_stats = pairwise_stats(D["val"][:, det_srcs], D["rel"][det_srcs], c, ovl,
                                w.MISSING)
    base_nedges = sum(1 for s in base_stats if s["excess"] > HAND_TUNED_THRESH)

    return dict(D=D, det_srcs=len(det_srcs), truth_choice=truth_choice,
                base=base_r, base_nedges=base_nedges, fdr=fdr_r,
                fdr_nedges=fdr_nedges, emp=emp_r)


# ===========================================================================
# Main
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weather-dir",
                    default=os.path.join(REPO, "data", "weather_dong_vldb2010"))
    ap.add_argument("--book-dir",
                    default=os.path.join(REPO, "data", "book_dong"))
    ap.add_argument("--truth", choices=["silver", "gold", "gold+silver"],
                    default="silver")
    ap.add_argument("--skip-weather", action="store_true")
    ap.add_argument("--skip-book", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="run self-tests only (no network) and exit")
    args = ap.parse_args()

    w = _load_module(WEATHER_PATH, "weather_cell")
    b = _load_module(BOOK_PATH, "book_cell")
    toy = w._load_toy()

    print("=" * 80)
    print("SELF-CALIBRATING (THRESHOLD-FREE) COPY DETECTOR -- re-test Weather + Book")
    print("=" * 80)

    # -------- SELF-TESTS FIRST (no network) --------
    print("\n--- REUSE-INTEGRITY SELF-TESTS ---")
    ri_ok, ri_notes = reuse_integrity_self_test(w, toy)
    for n in ri_notes:
        print("  " + n)
    print("\n--- SELF-CALIBRATION VALIDATION (planted copies, self-set op-point) ---")
    sc_ok, sc_notes = self_calibration_validation(toy)
    for n in sc_notes:
        print(n)
    print("  self-calibration recovery: %s" % ("PASS" if sc_ok else "FAIL"))

    if not (ri_ok and sc_ok):
        print("\nSELF-TEST FAILED -- real-data metrics not trustworthy, aborting.")
        print("VERDICT: SELFTEST_INVALID")
        return 2
    print("\n  all self-tests PASS")

    if args.self_test:
        print("\n--self-test only: OK")
        return 0

    # -------- WEATHER RE-TEST --------
    W = None
    if not args.skip_weather:
        print("\n" + "=" * 80)
        print("WEATHER RE-TEST -- detector recovery vs labeled gold copy graph")
        print("=" * 80)
        W = weather_retest(w, args.weather_dir)
        base = W["base"]
        print("  universe=%d pairs  gold=%d crossed=%d  AUC(gold|rest)=%.3f "
              "AUC(gold|crossed)=%.3f (op-point-invariant)"
              % (W["universe"], W["gold"], W["crossed"], W["auc_gold"], W["auc_gc"]))
        print("  HAND-TUNED thr=%.2f  : detected=%d gold_flagged=%d/%d crossed_flagged=%d "
              "F1=%.3f perm_p=%.4f"
              % (HAND_TUNED_THRESH, base["n_detected"], base["gold_flagged"],
                 W["gold"], base["crossed_flagged"], base["f1"], base["p_emp"]))
        print("  SELF-CALIBRATED binomial-FDR:")
        for q in FDR_Q_SWEEP:
            r = W["fdr"][q]
            print("    q=%.2f : detected=%d gold_flagged=%d/%d crossed_flagged=%d "
                  "F1=%.3f perm_p=%.4f" % (q, r["n_detected"], r["gold_flagged"],
                  W["gold"], r["crossed_flagged"], r["f1"], r["p_emp"]))
        if W["emp"] is not None:
            r = W["emp"]
            m0, s0 = W["emp_info"]
            print("  EMPIRICAL-NULL FDR q=%.2f (null m0=%.3f s0=%.3f): detected=%d "
                  "gold_flagged=%d/%d crossed_flagged=%d F1=%.3f perm_p=%.4f"
                  % (FDR_Q_PRIMARY, m0, s0, r["n_detected"], r["gold_flagged"],
                     W["gold"], r["crossed_flagged"], r["f1"], r["p_emp"]))

    # -------- BOOK RE-TEST --------
    B = None
    if not args.skip_book:
        print("\n" + "=" * 80)
        print("BOOK RE-TEST -- truth-value of copy-correction at self-set op-point")
        print("=" * 80)
        B = book_retest(b, w, args.book_dir, args.truth)
        base = B["base"]
        print("  truth=%s  big-sources(det)=%d" % (B["truth_choice"], B["det_srcs"]))
        print("  %-26s %-7s %-8s %-8s %-5s %-11s %-8s %-9s %s"
              % ("operating point", "edges", "mJ_naive", "mJ_corr", "|B|",
                 "cw/nw/tie", "winrate", "binom_p", "band"))

        def prow(label, edges, r):
            print("  %-26s %-7s %-8.4f %-8.4f %-5d %d/%d/%-5d %-8.3f %-9.4g %s"
                  % (label, edges, r["mjn"], r["mjc"], r["B_size"], r["B_cw"],
                     r["B_nw"], r["B_tie"], r["win_rate"], r["p_bin"], book_band(r)))
        prow("HAND-TUNED thr=0.15", B["base_nedges"], base)
        for q in FDR_Q_SWEEP:
            prow("self-calib binom q=%.2f" % q, B["fdr_nedges"][q], B["fdr"][q])
        prow("self-calib empirical-null", "-", B["emp"])
        print("  (mJ = mean last-name Jaccard vs %s truth; corrected beats naive iff "
              "mJ_corr >= mJ_naive AND subset-B win-rate/binom_p pass)" % B["truth_choice"])

    # -------- COMBINED VERDICT --------
    print("\n" + "=" * 80)
    print("VERDICT BLOCK -- does self-calibration REMOVE the conditional caveat?")
    print("=" * 80)

    verdict = "MIDDLE"
    w_pass = w_detail = None
    b_pass = b_stable = None
    if W is not None and B is not None:
        base_w = W["base"]
        fdr_w = W["fdr"][FDR_Q_PRIMARY]
        # W-PASS: FDR recovers gold above chance AND matches/beats hand-tuned set.
        w_pass = (fdr_w["p_emp"] < 0.05
                  and fdr_w["gold_flagged"] >= base_w["gold_flagged"]
                  and fdr_w["crossed_flagged"] <= base_w["crossed_flagged"])
        w_fail = (fdr_w["p_emp"] >= 0.5)
        base_b = B["base"]
        prim_b = B["fdr"][FDR_Q_PRIMARY]
        prim_band = book_band(prim_b)
        # B-PASS: self-set point reproduces HARD-PASS AND matches/beats 0.15 delta.
        b_delta = prim_b["mjc"] - prim_b["mjn"]
        base_delta = base_b["mjc"] - base_b["mjn"]
        b_pass = (prim_band == "HARD-PASS" and b_delta >= base_delta - 0.005)
        b_fail = (book_band(prim_b) == "HARD-FAIL"
                  or (prim_b["denom"] > 0 and prim_b["win_rate"] <= 0.5)
                  or prim_b["B_size"] < 20)
        # stability across q: Book band never flips to FAIL.
        b_bands = [book_band(B["fdr"][q]) for q in FDR_Q_SWEEP]
        b_stable = ("HARD-FAIL" not in b_bands)

        print("  WEATHER (primary q=%.2f): gold_flagged=%d (hand-tuned %d) "
              "crossed_flagged=%d (hand-tuned %d) perm_p=%.4f -> W-%s"
              % (FDR_Q_PRIMARY, fdr_w["gold_flagged"], base_w["gold_flagged"],
                 fdr_w["crossed_flagged"], base_w["crossed_flagged"], fdr_w["p_emp"],
                 "PASS" if w_pass else ("FAIL" if w_fail else "MIXED")))
        print("  BOOK (primary q=%.2f): band=%s win-rate=%.3f (p=%.4g |B|=%d) "
              "mJ delta=%+.4f (hand-tuned 0.15 delta=%+.4f) -> B-%s"
              % (FDR_Q_PRIMARY, prim_band, prim_b["win_rate"], prim_b["p_bin"],
                 prim_b["B_size"], b_delta, base_delta,
                 "PASS" if b_pass else ("FAIL" if b_fail else "MIXED")))
        print("  BOOK band stability across q%s: %s -> %s"
              % (FDR_Q_SWEEP, b_bands, "STABLE" if b_stable else "UNSTABLE"))

        if w_pass and b_pass and b_stable:
            verdict = "HARD-PASS"
        elif (w_fail or b_fail):
            verdict = "HARD-FAIL"
        else:
            verdict = "MIDDLE"
    else:
        print("  (one corpus skipped; combined verdict requires both)")

    print("\n  METHOD: self-calibrating operating point = per-pair binomial "
          "excess-agreement test + Benjamini-Hochberg FDR (q=%.2f primary), no "
          "hand-set excess threshold; empirical-null FDR cross-check." % FDR_Q_PRIMARY)
    print("  PRE-REG VERDICT: %s" % verdict)
    if verdict == "HARD-PASS":
        print("  CALL: the self-calibrated detector matches/beats the hand-tuned 0.15 "
              "result with NO external label and a STABLE band across FDR levels ==> "
              "the CONDITIONAL CAVEAT IS REMOVED.")
    elif verdict == "HARD-FAIL":
        print("  CALL: self-calibration cannot match the hand-tuned operating point / "
              "no robust unsupervised win ==> the conditional caveat STANDS (honest "
              "negative).")
    else:
        print("  CALL: MIDDLE -- self-calibration partially matches the hand-tuned "
              "point; caveat softened but not decisively removed.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
