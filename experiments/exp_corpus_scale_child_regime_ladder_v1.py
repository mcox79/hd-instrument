"""CORPUS SCALING LADDER: is our substrate STARVED, or is the machinery wrong?

THE QUESTION IS BRAIN-FIDELITY, NOT "SCALE IT UP".

Every arm this programme has ever measured was built on a store corpus of 34,169 sentences /
~623,522 tokens (verified via exp_cue_information_audit_v1.load_corpus_and_buckets). The
distributional methods we keep declaring failures come from a literature operating at 1e8-1e9
tokens. data/corpora/simplewiki/simplewiki_clean_v1.txt (~41.9M tokens) has been on disk the whole
time and was never used to build the usage representation.

OWNER'S CHALLENGE, which is the point of this cell:
    "the brain doesn't need 600000 words - does it? If we've set up the machinery right,
     shouldn't it work? Do this, but also make sure we're brain foundational"

That converts a scale sweep into a FALSIFIABLE FIDELITY TEST:

  - A child hears on the order of millions of words per year and has substantial vocabulary by
    age 4-6, i.e. TENS OF MILLIONS of tokens of input. ~42M is therefore roughly CHILD SCALE.
  - 623K is BELOW child scale. Starving the system is itself not brain-faithful, so this rung
    was never a fair test of any mechanism.
  - Needing 1e8-1e9 would be an ADMISSION THE MACHINERY IS WRONG, because no child gets that.

So the deliverable is not "does the number go up". It is WHERE ON THE CURVE the machinery would
have to sit to work, measured against what a child actually receives.

WHY CONTEXTS-PER-WORD IS REPORTED AT EVERY RUNG. Substitutability is a SECOND-ORDER statistic:
deciding whether two words are interchangeable means comparing the DISTRIBUTIONS of contexts they
each occur in. Raw token count is the wrong x-axis for that; the governing quantity is how many
context observations each evaluation word actually has. A curve plotted against tokens can look
flat merely because the words we test are rare.

PRE-COMMITTED READINGS (fixed before any number exists; see STATUS 2026-08-18):
  (A) RISING and reaching/approaching 0.5+ by ~42M
        -> scale was a genuine precondition we never met. Every "this mechanism does not work"
           verdict in this programme was reached in a regime where it COULD NOT have worked and
           must be RE-OPENED, not re-quoted.
  (B) RISING but extrapolating to require MUCH MORE THAN ~50M tokens
        -> THE MACHINERY IS NOT BRAIN-FAITHFUL. Report the extrapolated requirement explicitly.
           This is the MOST USEFUL outcome this cell can produce.
  (C) FLAT -> supply was never the binding constraint; the mechanism answers the wrong question;
           the scale hypothesis is closed.
  (D) NON-MONOTONIC -> the informative case. Report it. DO NOT SMOOTH IT.

CONTROLS THAT ARE NOT OPTIONAL, each earned by a specific failure in this programme:

  1. RANK-MATCHED NULL AT EVERY RUNG. The incumbent sits at ~0.06, FAR BELOW chance. Therefore
     DESTROYING information moves the score toward 0.5 and reads as progress -- the entire
     interval (0.06, 0.50) is reachable by degradation alone. On 2026-08-18 a cross-view arm
     reading 0.3129 was retracted when a random projection of the SAME store, which never saw the
     second channel, read 0.3079. A rise that does not beat a rank-matched null has shown NOTHING.

  2. ALL FOUR FLOORS AND THE BAR RECOMPUTED PER RUNG. A bigger corpus is a DIFFERENT
     REPRESENTATION, and F_SCRAMBLE / F_CONSTANT_PROTOTYPE are computed FROM the representation.
     Importing a bar across representations voided 21 arms on 2026-08-18. Never import
     0.5431 / 0.5510 / 0.5943 / 0.6317.

  3. F_SCRAMBLE IS A POLICY OVER >=500 PERMUTATIONS at the 95th percentile, never a single draw.
     Measured 2026-08-18: a single draw's own CI excludes 0.5 about 5% of the time BY
     CONSTRUCTION, so across four floors ~18% of runs are voided or passed on noise alone.

  4. CI half-width AND permutation null p95 beside every margin. A rung whose half-width exceeds
     the chance-to-bar interval is reported UNDERPOWERED, not given a verdict.

  5. EVALUATION POPULATION HELD FIXED across rungs so the rungs are comparable, with per-rung
     coverage attrition reported. A control that removes nothing is not a control.

REPRESENTATIONS. Two, deliberately:
  RAW_COUNT  -- L2-normalised raw co-occurrence counts. This is the incumbent's own construction
                and is FIRST-ORDER: it encodes "what appears beside this word". It is included as
                the anchor that should NOT be rescued by scale, because no amount of data turns a
                first-order statistic into a second-order one.
  PPMI_SVD   -- PPMI-weighted context vectors, truncated-SVD reduced. This IS the second-order
                comparison (two words are close when their CONTEXT DISTRIBUTIONS are close) and is
                the construction the cited literature uses. If anything is rescued by scale, this.

The contrast is the diagnosis: if PPMI_SVD rises with scale and RAW_COUNT does not, the missing
ingredient was contexts-per-word. If NEITHER rises, supply was never the constraint.

NESTING. Rungs are PREFIXES of the same shuffled line order, so each smaller corpus is a strict
subset of every larger one. The curve is therefore about SIZE, not about which text was drawn.

NO LLM anywhere in the operational path. Glass-box throughout.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import collections
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

sys.path.insert(0, str(REPO / "tools"))

import exp_dissociation_score_instrument_v1 as DSI  # noqa: E402
from exp_checkpoint import completed_units, load_units, record_unit, unit_key  # type: ignore # noqa

CORPUS = REPO / "data" / "corpora" / "simplewiki" / "simplewiki_clean_v1.txt"
INST_DIR = str(REPO / "data" / "exp_dissociation_score_instrument_v1")

CODE_VERSION = "v1.0"
RUNGS_FULL = [600_000, 2_000_000, 6_000_000, 20_000_000, 42_000_000]
RUNGS_SMOKE = [200_000, 600_000]
WINDOW = 5
CTX_VOCAB = 50_000
SVD_K = 300
N_BOOT = 10_000
N_SCRAMBLE = 500          # control 3: policy, never a single draw
N_RANKNULL = 200          # control 1
CHILD_SCALE_TOKENS = 50_000_000   # the fidelity threshold in branch (B)

_TOK = re.compile(r"[a-z]+")


def log(m: str) -> None:
    print(m, flush=True)


# ----------------------------------------------------------------- population
def population():
    """The instrument's OWN landed matched pairs, held fixed across every rung (control 5)."""
    pop = load_units(INST_DIR)[unit_key("POPULATION", "v1.7", "full")]
    mP = [tuple(x) for x in pop["matchedP"]]
    mS = [tuple(x) for x in pop["matchedS"]]
    assert len(mP) == len(mS) == 242, f"population drift: {len(mP)}/{len(mS)} != 242 -- VOID"
    words = sorted({w for a, b, _ in mP + mS for w in (a, b)})
    assert len(words) == 617, f"eval-word drift: {len(words)} != 617 -- VOID"
    return mP, mS, words


# ----------------------------------------------------------------- corpus
def stream_tokens(limit: int):
    """Yield token lists per line until `limit` tokens are consumed. PREFIX order, so every rung
    is a strict subset of every larger rung."""
    used = 0
    with open(CORPUS, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            toks = _TOK.findall(line.lower())
            if not toks:
                continue
            yield toks
            used += len(toks)
            if used >= limit:
                return


def build_counts(limit: int, row_words):
    """word x context sparse counts over a +/-WINDOW window. Rows are the evaluation words; the
    context vocabulary is the top CTX_VOCAB tokens AT THIS RUNG (a property of the rung, not
    imported from another one)."""
    t0 = time.time()
    freq = collections.Counter()
    n_tok = 0
    for toks in stream_tokens(limit):
        freq.update(toks)
        n_tok += len(toks)
    ctx = [w for w, _ in freq.most_common(CTX_VOCAB)]
    cix = {w: i for i, w in enumerate(ctx)}
    rix = {w: i for i, w in enumerate(row_words)}
    rows, cols, vals = [], [], []
    acc = collections.Counter()
    for toks in stream_tokens(limit):
        n = len(toks)
        for i, w in enumerate(toks):
            r = rix.get(w)
            if r is None:
                continue
            lo, hi = max(0, i - WINDOW), min(n, i + WINDOW + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                c = cix.get(toks[j])
                if c is not None:
                    acc[(r, c)] += 1
    for (r, c), v in acc.items():
        rows.append(r); cols.append(c); vals.append(v)
    M = sp.coo_matrix((vals, (rows, cols)),
                      shape=(len(row_words), len(ctx)), dtype=np.float64).tocsr()
    contexts_per_word = np.asarray(M.sum(axis=1)).ravel()
    log(f"    corpus: {n_tok:,} tokens | {len(freq):,} types | matrix nnz {M.nnz:,} "
        f"| {time.time()-t0:.0f}s")
    return M, n_tok, len(freq), contexts_per_word


# ----------------------------------------------------------------- representations
def l2n(X):
    X = np.asarray(X, dtype=np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


def rep_raw_count(M):
    return l2n(M.toarray())


def rep_ppmi_svd(M, k=SVD_K):
    """PPMI then truncated SVD. This is the SECOND-ORDER construction: closeness means similar
    CONTEXT DISTRIBUTIONS, which is what substitutability actually is."""
    M = M.tocoo()
    total = M.data.sum()
    if total <= 0:
        return np.zeros((M.shape[0], 2))
    rs = np.asarray(M.tocsr().sum(axis=1)).ravel()
    cs = np.asarray(M.tocsr().sum(axis=0)).ravel()
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((M.data * total) / (rs[M.row] * cs[M.col]))
    pmi[~np.isfinite(pmi)] = 0.0
    pmi[pmi < 0] = 0.0                                   # positive PMI
    P = sp.coo_matrix((pmi, (M.row, M.col)), shape=M.shape).tocsr()
    P.eliminate_zeros()
    kk = int(min(k, min(P.shape) - 1))
    if kk < 2 or P.nnz == 0:
        return l2n(P.toarray())
    U, S, _ = svds(P, k=kk)
    return l2n(U * S)


# ----------------------------------------------------------------- scoring
def scores(V, rix, pairs):
    out = []
    for a, b, _ in pairs:
        ia, ib = rix.get(a), rix.get(b)
        out.append(float(V[ia] @ V[ib]) if ia is not None and ib is not None else np.nan)
    return np.asarray(out, dtype=np.float64)


def auc_ci(sp_, ss_, seed=1):
    ok = ~(np.isnan(sp_) | np.isnan(ss_))          # matched-preserved (control 5)
    a, b = sp_[ok], ss_[ok]
    if len(a) < 10:
        return dict(auc=float("nan"), ci95=[float("nan")] * 2, hw=float("nan"), n=int(ok.sum()))
    r = DSI.auc_bootstrap(a, b, N_BOOT, seed)
    lo, hi = r["ci95"]
    return dict(auc=r["auc"], ci95=[lo, hi], hw=(hi - lo) / 2.0, n=int(ok.sum()))


def floor_scramble(V, rix, mP, mS, seed=7):
    """CONTROL 3. A POLICY over N_SCRAMBLE permutations; the bar term is the 95th percentile of
    that distribution, NOT one draw. A single draw's own CI excludes 0.5 ~5% of the time."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(N_SCRAMBLE):
        perm = rng.permutation(V.shape[0])
        Vp = V[perm]
        s1, s2 = scores(Vp, rix, mP), scores(Vp, rix, mS)
        ok = ~(np.isnan(s1) | np.isnan(s2))
        if ok.sum() >= 10:
            vals.append(DSI.auc_of(s1[ok], s2[ok]))
    v = np.asarray(vals)
    return dict(mean=float(v.mean()), p95=float(np.percentile(v, 95)), n=len(v))


def floor_constant_prototype(V, rix, mP, mS):
    """Every word replaced by the population mean vector -- what you score with NO word identity."""
    proto = V.mean(axis=0, keepdims=True)
    Vc = np.repeat(proto, V.shape[0], axis=0)
    return auc_ci(scores(Vc, rix, mP), scores(Vc, rix, mS))["auc"]


def floor_orthographic(mP, mS):
    def tri(w):
        return {w[i:i + 3] for i in range(max(1, len(w) - 2))}
    def s(pairs):
        o = []
        for a, b, _ in pairs:
            A, B = tri(a), tri(b)
            o.append(len(A & B) / math.sqrt(len(A) * len(B)) if A and B else 0.0)
        return np.asarray(o)
    return auc_ci(s(mP), s(mS))["auc"]


def floor_frequency(mP, mS, freq_of):
    def s(pairs):
        return np.asarray([-abs(math.log1p(freq_of.get(a, 0)) - math.log1p(freq_of.get(b, 0)))
                           for a, b, _ in pairs])
    return auc_ci(s(mP), s(mS))["auc"]


def rank_matched_null(V, rix, mP, mS, k, seed=11):
    """CONTROL 1. A RANDOM k-dimensional projection of the SAME representation. Because the
    baseline sits far below chance, rank reduction alone walks the score toward 0.5. An arm that
    does not beat this has demonstrated nothing."""
    rng = np.random.default_rng(seed)
    d = V.shape[1]
    kk = int(min(k, d))
    vals = []
    for _ in range(N_RANKNULL):
        R = rng.standard_normal((d, kk))
        Vr = l2n(V @ R)
        s1, s2 = scores(Vr, rix, mP), scores(Vr, rix, mS)
        ok = ~(np.isnan(s1) | np.isnan(s2))
        if ok.sum() >= 10:
            vals.append(DSI.auc_of(s1[ok], s2[ok]))
    v = np.asarray(vals)
    return dict(mean=float(v.mean()), p95=float(np.percentile(v, 95)), n=len(v))


# ----------------------------------------------------------------- rung
def run_rung(limit, mP, mS, words):
    rix = {w: i for i, w in enumerate(words)}
    M, n_tok, n_types, cpw = build_counts(limit, words)
    freq_of = {w: float(cpw[i]) for w, i in rix.items()}
    covered = int((cpw > 0).sum())
    res = {
        "tokens_requested": limit, "tokens_used": n_tok, "types": n_types,
        "eval_words_covered": covered, "eval_words_total": len(words),
        "median_contexts_per_eval_word": float(np.median(cpw)),
        "median_contexts_per_COVERED_eval_word": float(np.median(cpw[cpw > 0])) if covered else 0.0,
        "arms": {},
    }
    # ARM RANK matters for the rank-matched null and the smoke exposed why. The null asks "could a
    # RANDOM transform to the SAME effective dimensionality score as well?" That is meaningful only
    # for an arm that REDUCES rank. RAW_COUNT is full-rank, and a random projection approximately
    # PRESERVES cosine (Johnson-Lindenstrauss), so the null came back at or above the arm
    # (0.6408 vs 0.6321) purely by construction and could never fire. Reported N_A there rather
    # than left to read as a failure; the four recomputed floors carry the load for full-rank arms.
    for name, V, arm_rank in (("RAW_COUNT", rep_raw_count(M), None),
                              ("PPMI_SVD", rep_ppmi_svd(M), SVD_K)):
        s1, s2 = scores(V, rix, mP), scores(V, rix, mS)
        a = auc_ci(s1, s2)
        f_scr = floor_scramble(V, rix, mP, mS)
        floors = {
            "F_SCRAMBLE_p95": f_scr["p95"], "F_SCRAMBLE_mean": f_scr["mean"],
            "F_CONSTANT_PROTOTYPE": floor_constant_prototype(V, rix, mP, mS),
            "F_ORTHOGRAPHIC": floor_orthographic(mP, mS),
            "F_FREQUENCY": floor_frequency(mP, mS, freq_of),
        }
        bar = max(v for v in floors.values() if np.isfinite(v))          # control 2
        if arm_rank is None:
            rn = {"mean": float("nan"), "p95": float("nan"), "n": 0, "applicable": False}
            beats = None
        else:
            rn = rank_matched_null(V, rix, mP, mS, arm_rank)
            rn["applicable"] = True
            beats = bool(np.isfinite(a["auc"]) and a["auc"] > rn["p95"])
        chance_to_bar = bar - 0.5
        # THE GATE THAT MATTERS: CI-separated above the bar, i.e. the CI LOWER BOUND clears it.
        # A point estimate over the bar is not a result -- that error cost us today.
        ci_sep = bool(np.isfinite(a["ci95"][0]) and a["ci95"][0] > bar)
        res["arms"][name] = {
            **a, "floors": floors, "bar": bar, "margin_vs_bar": a["auc"] - bar,
            "CI_SEPARATED_ABOVE_BAR": ci_sep,
            "rank_matched_null_mean": rn["mean"], "rank_matched_null_p95": rn["p95"],
            "rank_null_applicable": rn["applicable"], "beats_rank_null": beats,
            "arm_rank": arm_rank if arm_rank is not None else "FULL",
            "rows_dropped_coverage": 242 - a["n"],
            "UNDERPOWERED": bool(np.isfinite(a["hw"]) and a["hw"] > max(chance_to_bar, 1e-9)),
        }
        nulls = "N_A(full-rank)" if arm_rank is None else f"{rn['p95']:.4f} beats={beats}"
        log(f"    {name:10s} auc={a['auc']:.4f} [{a['ci95'][0]:.4f},{a['ci95'][1]:.4f}] "
            f"hw={a['hw']:.4f} bar={bar:.4f} margin={a['auc']-bar:+.4f} CI_SEP={ci_sep} "
            f"ranknull={nulls} n={a['n']} dropped={242-a['n']}")
    return res


# ----------------------------------------------------------------- branch
def read_branch(rungs):
    """The four pre-committed readings. Decided before any number existed."""
    def best(r):
        return max((r["arms"][k]["auc"] - r["arms"][k]["bar"]) for k in r["arms"])
    xs = [r["tokens_used"] for r in rungs]
    ys = [best(r) for r in rungs]
    if len(xs) < 2 or not all(np.isfinite(ys)):
        return "INCONCLUSIVE_INSUFFICIENT_RUNGS", {}
    rising = ys[-1] > ys[0]
    monotone = all(ys[i + 1] >= ys[i] - 1e-9 for i in range(len(ys) - 1))
    # "Cleared" requires the CI LOWER BOUND above the bar, and -- where the rank null is
    # applicable at all -- beating it. A full-rank arm has no meaningful rank null (a random
    # rotation preserves cosine), so it is not held to a vacuous test.
    cleared = any(r["arms"][k].get("CI_SEPARATED_ABOVE_BAR")
                  and (r["arms"][k].get("beats_rank_null") is not False)
                  for r in rungs for k in r["arms"])
    info = {"tokens": xs, "best_margin_vs_bar": ys}
    if cleared:
        return "A_SCALE_WAS_A_REAL_PRECONDITION__REOPEN_PRIOR_VERDICTS", info
    if not rising:
        return "C_FLAT__SUPPLY_WAS_NEVER_BINDING__MECHANISM_ANSWERS_WRONG_QUESTION", info
    if not monotone:
        return "D_NON_MONOTONIC__INFORMATIVE__DO_NOT_SMOOTH", info
    # rising but never clears: extrapolate log-linearly to margin 0
    lx = np.log10(np.maximum(xs, 1))
    sl, ic = np.polyfit(lx, ys, 1)
    need = float(10 ** ((0.0 - ic) / sl)) if sl > 0 else float("inf")
    info["extrapolated_tokens_to_clear_bar"] = need
    info["child_scale_tokens"] = CHILD_SCALE_TOKENS
    if need > CHILD_SCALE_TOKENS:
        return "B_RISING_BUT_BEYOND_CHILD_SCALE__MACHINERY_NOT_BRAIN_FAITHFUL", info
    return "A_SCALE_WAS_A_REAL_PRECONDITION__REOPEN_PRIOR_VERDICTS", info


# ----------------------------------------------------------------- self-test
def self_test() -> int:
    ok = True
    mP, mS, words = population()
    log(f"[selftest] population 242/242 rows, {len(words)} eval words  PASS")

    rix = {w: i for i, w in enumerate(words)}
    rng = np.random.default_rng(0)

    # PLANTED POSITIVE. Naive `V[b] = V[a]` per pair is WRONG and scored 0.8469 on the first run:
    # evaluation words recur across pairs, so a later assignment silently overwrites a vector an
    # earlier pair had already matched, breaking pairs the fixture claims to have planted. Union-
    # find gives every connected component of the P-graph ONE vector, so every P pair is exactly
    # identical by construction. (AUC can still fall below 1.0 if transitivity happens to make an
    # S pair identical too -- that is real, not fixture error, hence the 0.95 gate rather than 1.0.)
    parent = list(range(len(words)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a_, b_, _ in mP:
        ra, rb = find(rix[a_]), find(rix[b_])
        if ra != rb:
            parent[ra] = rb
    base = rng.standard_normal((len(words), 64))
    V = l2n(np.array([base[find(i)] for i in range(len(words))]))
    a = auc_ci(scores(V, rix, mP), scores(V, rix, mS))
    log(f"[selftest] planted-separable auc={a['auc']:.4f} (expect ~1.0) "
        f"{'PASS' if a['auc'] > 0.95 else 'FAIL'}")
    ok &= a["auc"] > 0.95

    # scramble floor of the planted store must collapse to chance
    f = floor_scramble(V, rix, mP, mS, seed=3)
    log(f"[selftest] scramble policy mean={f['mean']:.4f} p95={f['p95']:.4f} over {f['n']} perms "
        f"{'PASS' if abs(f['mean'] - 0.5) < 0.06 else 'FAIL'}")
    ok &= abs(f["mean"] - 0.5) < 0.06

    # THE control that caught today's retraction: rank reduction of a BELOW-chance store must walk
    # toward 0.5, proving the null is LIVE rather than decorative.
    #
    # TWO FIXTURES FAILED HERE BEFORE THIS ONE, AND THE GATE CAUGHT BOTH -- worth recording,
    # because each was a wrong belief about WHY rank reduction moves a below-chance score:
    #   (i) S pairs made EXACTLY identical. Exact identity is PROJECTION-INVARIANT: cosine stays
    #       1.0 through any linear map, so nothing could move (0.1188 -> 0.1109).
    #   (ii) S pairs made DENSE and 0.9-correlated. Random projection APPROXIMATELY PRESERVES
    #       cosines (Johnson-Lindenstrauss), so a dense correlation that strong survives the
    #       projection too (0.1169 -> 0.1105).
    # The real incumbent store is SPARSE, non-negative and heavy-tailed, and its below-chance
    # signal lives in WHICH CONTEXT DIMENSIONS two words share. Random projection MIXES those
    # dimensions, destroying the sparse alignment -- which is exactly how a random 8-dim projection
    # of the real store read 0.3079 against the store's own 0.0603 on 2026-08-18. So the fixture
    # must be SPARSE AND NON-NEGATIVE, i.e. count-like, or it does not test the phenomenon.
    d = 256
    Vb = np.zeros((len(words), d))
    for i in range(len(words)):
        idx = rng.choice(d, size=12, replace=False)
        Vb[i, idx] = rng.gamma(1.5, 1.0, size=12)          # sparse, non-negative, heavy-tailed
    for a_, b_, _ in mS:
        ia, ib = rix[a_], rix[b_]
        share = np.nonzero(Vb[ia])[0][:8]                   # S pairs SHARE SUPPORT (co-occurrence)
        Vb[ib, share] += Vb[ia, share]
    base = auc_ci(scores(Vb, rix, mP), scores(Vb, rix, mS))["auc"]
    rn = rank_matched_null(Vb, rix, mP, mS, 8, seed=5)
    log(f"[selftest] below-chance store {base:.4f} -> rank-8 null mean {rn['mean']:.4f} "
        f"{'PASS (null is live)' if rn['mean'] > base else 'FAIL (null decorative)'}")
    ok &= rn["mean"] > base

    # branch function must be able to fire the fidelity failure
    fake = [{"tokens_used": t, "arms": {"X": {"auc": 0.30 + 0.01 * i, "bar": 0.55,
                                              "beats_rank_null": False}}}
            for i, t in enumerate([6e5, 2e6, 6e6, 2e7, 4.2e7])]
    br, inf = read_branch(fake)
    log(f"[selftest] branch on a slow-rising fake -> {br} "
        f"{'PASS' if br.startswith('B_') else 'FAIL'}")
    ok &= br.startswith("B_")

    log(f"[selftest] RESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ----------------------------------------------------------------- main
def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    smoke = "--smoke" in sys.argv or "--grid" in sys.argv
    rungs = RUNGS_SMOKE if smoke else RUNGS_FULL
    name = "exp_corpus_scale_child_regime_ladder_v1" + ("_smoke" if smoke else "")
    outdir = str(REPO / "data" / name)
    os.makedirs(outdir, exist_ok=True)

    assert CORPUS.exists(), f"corpus missing: {CORPUS}"
    mP, mS, words = population()
    log(f"[population] 242 matched rows, {len(words)} eval words (HELD FIXED across rungs)")

    done = completed_units(outdir)
    results = []
    for limit in rungs:
        key = unit_key("RUNG", CODE_VERSION, str(limit))
        if key in done:
            results.append(load_units(outdir)[key])
            log(f"[rung {limit:,}] cached")
            continue
        log(f"[rung {limit:,}] building")
        r = run_rung(limit, mP, mS, words)
        record_unit(outdir, key, r)
        results.append(r)

    branch, info = read_branch(results)
    log("")
    log("=" * 100)
    log(f"{'tokens':>12} {'types':>9} {'ctx/word':>9} {'arm':>10} {'auc':>7} {'hw':>7} "
        f"{'bar':>7} {'margin':>8} {'ranknull':>9} {'beats':>6}")
    for r in results:
        for k, v in r["arms"].items():
            log(f"{r['tokens_used']:>12,} {r['types']:>9,} "
                f"{r['median_contexts_per_COVERED_eval_word']:>9.0f} {k:>10} "
                f"{v['auc']:>7.4f} {v['hw']:>7.4f} {v['bar']:>7.4f} {v['margin_vs_bar']:>+8.4f} "
                f"{v['rank_matched_null_p95']:>9.4f} {str(v['beats_rank_null']):>6}")
    log("=" * 100)
    log(f"BRANCH: {branch}")
    if "extrapolated_tokens_to_clear_bar" in info:
        need = info["extrapolated_tokens_to_clear_bar"]
        log(f"  extrapolated tokens to clear the bar: {need:,.0f}")
        log(f"  child-scale reference:                {CHILD_SCALE_TOKENS:,}")
        log(f"  -> {'BEYOND child scale: MACHINERY NOT BRAIN-FAITHFUL' if need > CHILD_SCALE_TOKENS else 'within child scale'}")

    metrics = {
        "verdict": branch,
        "code_version": CODE_VERSION,
        "corpus": str(CORPUS),
        "window": WINDOW, "ctx_vocab": CTX_VOCAB, "svd_k": SVD_K,
        "n_boot": N_BOOT, "n_scramble_permutations": N_SCRAMBLE, "n_rank_null": N_RANKNULL,
        "child_scale_tokens": CHILD_SCALE_TOKENS,
        "branch_info": info,
        "rungs": results,
        "NOTE_BARS_RECOMPUTED_PER_RUNG": "no bar imported; each rung's bar is max(4 floors) on ITS "
                                         "OWN representation and population",
        "NOTE_RANK_NULL": "an arm that does not exceed rank_matched_null_p95 has shown nothing, "
                          "because degradation alone walks a below-chance score toward 0.5",
    }
    with open(os.path.join(outdir, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=1)
    log(f"[done] {os.path.join(outdir, 'metrics.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
