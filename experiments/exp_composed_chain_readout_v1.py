#!/usr/bin/env python
"""COMPOSED CHAIN read-out: whiten / pseudoinverse-write / coarse-to-fine, each stage separable.

PREREG: preregs/2026-08-14_composed_chain_readout_v1.md (committed 2e9bbdce5, BEFORE this run).
STAGE 0 pre-check: exp_codebook_geometry_precheck_v1 (committed aea33edf2, run first).

PRIMARY MEASURAND is the target's RANK, not "does it beat argmax". Baseline, read from
data/exp_sharpening_readout_sister_separation_v1_SMOKE_n600/metrics.json:
    median_rank_of_target_among_all_anchors = 84.0   n_anchors = 647
    frac_target_outside_top50 = 0.60  => top-50 fraction = 0.40
    frac_target_rank1 = 0.098333
This cell reproduces that draw EXACTLY (same helpers, same salt "") so those are legitimate
comparators.

WHAT IS AND IS NOT LIVE (read from hdlab/reading_grounding_loop.py, not assumed):
    ConceptSpace.observe  = `self._sums[lemma] += ctx_vec`   -> write rule is PURE HEBBIAN
    canonicalize_fast     = `(mat @ nb) / (norms * nn)`, argmax -> read is PLAIN COSINE
    => whitening, pseudoinverse write, and coarse-to-fine are ALL ABSENT from the live path.
    (ReadoutConfig FIX 2 `anchor_background` is a per-anchor mean/sd z-score = a DIAGONAL
     approximation to whitening, and is OFF by default. It is not full covariance whitening.)

PRE-DECLARED (prereg sec 4), restated here so a reader of the code sees it:
 (a) A pseudoinverse memory is exact only up to `d` linearly-independent keys. d=256 and we have
     647 (2.5x over) or 5491 (21.4x over) anchors, so the pinv guarantee is VOID BY CONSTRUCTION
     at our operating point. A null at full anchor count is a SCALE result. The anchor-count SWEEP
     down to n<=256 is the test that separates "does not transfer to our codes" from "does not fit
     in our dimensionality" -- it is mandatory, not optional.
 (d) Coarse-to-fine CANNOT raise accuracy: its own cell reports recall 0.992 against a full-fine
     CEILING of 0.992. It is a COST mechanism (cost ratio 0.200). Restricting candidates either
     drops competitors (rank same-or-better) or drops the target (a miss). Expected hit@1
     contribution <= 0. A3 is a COST arm; reporting its null as a mechanism failure is an ERROR.

NOTE ON STAGE INDEPENDENCE (a real finding, not a caveat): A2_PINV is
`Q (K^T K + lam I)^-1 K^T`, i.e. whitening the query by the anchor SECOND-MOMENT matrix.
A1_WHITEN is ZCA by the anchor CENTERED COVARIANCE applied to both sides. The two "stages" are
near-relatives of one operation, so their contributions are NOT expected to be additive, and the
composed arm is not the sum of its parts. Declared before the numbers exist.

No beta / no softmax anywhere in this cell, so the `hdlab/multi_hop.py` beta=n_dim hard-argmax
trap is out of scope and there is no weight entropy to report.

ASCII-only. Threads pinned before numpy import.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse                                                                # noqa: E402
import json                                                                    # noqa: E402
import platform                                                                # noqa: E402
import sys                                                                     # noqa: E402
import time                                                                    # noqa: E402
import traceback                                                               # noqa: E402
from datetime import datetime, timezone                                        # noqa: E402
from typing import Dict, List, Sequence, Tuple                                 # noqa: E402

import numpy as np                                                             # noqa: E402

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_sharpening_readout_sister_separation_v1 as SH                       # noqa: E402
import exp_context_conditioned_near_neighbour_v1 as NN                         # noqa: E402

ANCHOR_NAME = "exp_composed_chain_readout_v1"
PREREG_PATH = "preregs/2026-08-14_composed_chain_readout_v1.md"

MASTER_SEED = 20260814
BOOTSTRAP_SEED = 20260814
N_BOOTSTRAP = 5000
N_DRAWS_FULL, N_DRAWS_SMOKE = 4, 2          # prereg: >=4 (the baseline's n_draws=2 sd is unusable)
MAX_ITEMS_FULL, MAX_ITEMS_SMOKE = 600, 150

LAMBDAS_REL = (1e-4, 1e-3, 1e-2, 1e-1)      # relative to trace(K^T K)/d
LAMBDA_PRIMARY = 1e-3                        # DECLARED primary; the rest are sensitivity only
WHITEN_EPS_REL = 1e-3
D_COARSE = 128                               # from the coarse-to-fine cell
SHORTLIST_FRAC = 0.10                        # its k0.1 operating point

ANCHOR_SWEEP = (64, 128, 192, 256, 384, 512, 647)
SWEEP_REPLICATES = 8

# baseline constants, quoted from the source metrics.json (see module docstring)
BASE_MEDIAN_RANK = 84.0
BASE_N_ANCHORS = 647
BASE_TOP50_FRAC = 0.40
BASE_HIT1 = 0.098333
BASE_2AFC = 0.7083


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _out_dir(run_mode: str) -> str:
    suffix = "" if run_mode == "full" else "_" + run_mode.upper()
    d = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _atomic_write(path: str, obj: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(json.dumps(obj, indent=2).encode("utf-8"))
    os.replace(tmp, path)


def _hb(out_dir: str, phase: str, t0: float, extra: dict = None) -> None:
    rec = {"phase": phase, "elapsed_s": round(time.time() - t0, 1), "ts_iso": _now()}
    if extra:
        rec.update(extra)
    with open(os.path.join(out_dir, "_heartbeat.jsonl"), "ab") as fh:
        fh.write((json.dumps(rec) + "\n").encode("utf-8"))


# ---------------------------------------------------------------------------------------------
# The four stages. Each is a pure function of (Q, K) -> score matrix (n_items x n_anchors).
# ---------------------------------------------------------------------------------------------
def _unit(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return M / n


def score_baseline(Q: np.ndarray, K: np.ndarray) -> np.ndarray:
    """A0 -- exactly `canonicalize_fast`: cosine of the query against each anchor."""
    return _unit(Q) @ _unit(K).T


def fit_whiten(K: np.ndarray, eps_rel: float = WHITEN_EPS_REL):
    """ZCA fitted on the ANCHOR cloud: centre, decorrelate, equalise. Returns (mu, W)."""
    X = np.asarray(K, dtype=np.float64)
    mu = X.mean(axis=0, keepdims=True)
    Xc = X - mu
    C = (Xc.T @ Xc) / max(1, Xc.shape[0] - 1)
    eps = eps_rel * float(np.trace(C)) / C.shape[0]
    w, V = np.linalg.eigh(C)
    W = V @ np.diag(1.0 / np.sqrt(np.maximum(w, 0.0) + eps)) @ V.T
    return mu, W


def score_whiten(Q: np.ndarray, K: np.ndarray) -> np.ndarray:
    """A1 -- whiten BOTH sides with the anchor-cloud ZCA, then cosine."""
    mu, W = fit_whiten(K)
    return score_baseline((Q - mu) @ W, (K - mu) @ W)


def score_pinv(Q: np.ndarray, K: np.ndarray, lam_rel: float = LAMBDA_PRIMARY) -> np.ndarray:
    """A2 -- pseudoinverse (projection) WRITE rule, heteroassociative form.

    Hebb reads each anchor independently: S = Q K^T. The pinv rule instead stores the decorrelating
    map, so recall of a stored key returns its own slot rather than every correlated slot:
        S = Q K^+ ,  K^+ = K^T (K K^T + lam I)^-1
    Computed via the push-through identity K^T (K K^T + lam I)^-1 = (K^T K + lam I)^-1 K^T, so the
    inverse is d x d (256) and never n_anchors x n_anchors (5491) -- same matrix, ~10^4x cheaper.
    """
    Kd = np.asarray(K, dtype=np.float64)
    G = Kd.T @ Kd                                          # (d, d)
    lam = lam_rel * float(np.trace(G)) / G.shape[0]
    M = np.linalg.inv(G + lam * np.eye(G.shape[0]))
    S = (np.asarray(Q, dtype=np.float64) @ M) @ Kd.T
    # scale-free comparison: the pinv map is not norm preserving, so compare on the same footing
    # as cosine by normalising each row (monotone per item; ranks and argmax are unaffected).
    return S / np.maximum(np.linalg.norm(S, axis=1, keepdims=True), 1e-12)


def shortlist_c2f(Q: np.ndarray, K: np.ndarray, base_scores: np.ndarray,
                  seed: int, d_coarse: int = D_COARSE,
                  frac: float = SHORTLIST_FRAC) -> Tuple[np.ndarray, np.ndarray]:
    """A3 -- coarse random projection -> top-k shortlist -> fine rescore inside the shortlist.

    Returns (masked_scores, shortlist_mask). Anchors outside the shortlist are set to -inf, so a
    target that falls out of the shortlist is ranked LAST (an honest miss, not a silent drop)."""
    n_anchors = K.shape[0]
    k = max(1, int(np.ceil(frac * n_anchors)))
    rng = np.random.default_rng(seed)
    R = rng.standard_normal((K.shape[1], d_coarse)) / np.sqrt(d_coarse)
    coarse = score_baseline(np.asarray(Q, dtype=np.float64) @ R,
                            np.asarray(K, dtype=np.float64) @ R)
    idx = np.argpartition(-coarse, kth=k - 1, axis=1)[:, :k]
    mask = np.zeros_like(coarse, dtype=bool)
    np.put_along_axis(mask, idx, True, axis=1)
    out = np.where(mask, base_scores, -np.inf)
    return out, mask


# ---------------------------------------------------------------------------------------------
# Measurands
# ---------------------------------------------------------------------------------------------
def rank_stats(S: np.ndarray, ti: np.ndarray) -> dict:
    """Rank of the TARGET among ALL anchors (1 = best).

    CORRECTNESS NOTE (a bug the smoke gate caught in this file, not in the substrate): for a
    shortlist arm the non-shortlisted anchors carry -inf. A target that FELL OUT of the shortlist
    then has tscore = -inf, and `(S > -inf).sum()+1` counts only the k shortlisted anchors, so the
    miss was scoring as rank k+1 -- an EXCELLENT rank. That produced frac_top50 = 1.0000 for an arm
    whose shortlist only retained 31% of targets. A dropped target must rank LAST among all
    anchors, which is what the explicit non-finite branch below enforces."""
    n, m = S.shape
    tscore = S[np.arange(n), ti]
    rank = (S > tscore[:, None]).sum(axis=1) + 1
    dropped = ~np.isfinite(tscore)
    rank = np.where(dropped, m, rank)
    return {
        "median_rank": float(np.median(rank)),
        "mean_rank": round(float(rank.mean()), 2),
        "frac_top50": round(float((rank <= 50).mean()), 6),
        "frac_outside_top50": round(float((rank > 50).mean()), 6),
        "frac_rank1": round(float((rank == 1).mean()), 6),
        "frac_target_dropped_from_shortlist": round(float(dropped.mean()), 6),
        "n_items": int(n),
    }, rank


def hit1(S: np.ndarray, ti: np.ndarray) -> np.ndarray:
    return np.asarray(S.argmax(axis=1) == ti, dtype=bool)


def afc2(S: np.ndarray, ti: np.ndarray, di: np.ndarray) -> np.ndarray:
    n = S.shape[0]
    return np.asarray(S[np.arange(n), ti] > S[np.arange(n), di], dtype=bool)


def paired_bootstrap(arms: Dict[str, np.ndarray], deltas: Sequence[Tuple[str, str, str]],
                     n_boot: int, seed: int) -> dict:
    keys = sorted(arms)
    n = len(arms[keys[0]])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = {k: np.asarray(arms[k], dtype=np.float64)[idx].mean(axis=1) for k in keys}
    out = {"n_boot": n_boot, "n_items": n, "seed": seed,
           "arm_acc": {k: round(float(np.mean(arms[k])), 6) for k in keys}, "deltas": {}}
    for name, a, b in deltas:
        d = means[a] - means[b]
        out["deltas"][name] = {
            "delta": round(float(np.mean(arms[a]) - np.mean(arms[b])), 6),
            "ci_lo": round(float(np.percentile(d, 2.5)), 6),
            "ci_hi": round(float(np.percentile(d, 97.5)), 6),
            "excludes_zero": bool(np.percentile(d, 2.5) > 0 or np.percentile(d, 97.5) < 0)}
    return out


# ---------------------------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------------------------
def _selftest() -> None:
    rng = np.random.default_rng(3)
    d, m, n = 32, 20, 40

    # 1. baseline scorer IS cosine, and reproduces canonicalize_fast's argmax on a real ConceptSpace
    from hdlab.reading_grounding_loop import ConceptSpace, canonicalize_fast
    sp = ConceptSpace(d=d)
    for i in range(m):
        for _ in range(3):
            sp.observe("w%02d" % i, rng.standard_normal(d))
    anchors, K = sp.anchor_matrix()
    q = rng.standard_normal(d)
    S = score_baseline(q[None, :], K)
    mine = anchors[int(S.argmax())]
    theirs, _c = canonicalize_fast("__query_not_an_anchor__", q, sp, thresh=-1.0)
    assert mine == theirs, "A0 must reproduce canonicalize_fast: %s vs %s" % (mine, theirs)

    # 2. pinv EXACTLY recovers stored keys when m <= d (its precondition) and the push-through
    #    identity matches the literal n_anchors-sized inverse
    Ks = rng.standard_normal((m, d))
    Ss = score_pinv(Ks, Ks, lam_rel=1e-10)
    assert (Ss.argmax(axis=1) == np.arange(m)).all(), "pinv must recall stored keys at m<=d"
    G2 = Ks @ Ks.T
    lam = 1e-10 * float(np.trace(Ks.T @ Ks)) / d
    lit = Ks @ Ks.T @ np.linalg.inv(G2 + lam * np.eye(m))
    lit = lit / np.maximum(np.linalg.norm(lit, axis=1, keepdims=True), 1e-12)
    assert np.abs(lit - Ss).max() < 1e-6, "push-through identity broken: %g" % np.abs(lit - Ss).max()

    # 3. pinv's guarantee BREAKS above capacity -- the pre-declared failure mode is real, not an
    #    excuse invented after the fact. MEASURED CORRECTION to a naive form of this test: at
    #    m > d the recall operator K(K^T K)^-1 K^T is a rank-d PROJECTION, so it CANNOT equal the
    #    identity (the exactness guarantee is void), yet it stays diagonally dominant and therefore
    #    still argmaxes CLEAN stored keys correctly. The capacity ceiling does not destroy clean
    #    recall -- it destroys NOISE TOLERANCE, which is the regime a held-out-sentence query is
    #    actually in. Both halves are asserted.
    Kin = rng.standard_normal((d // 2, d))                        # within capacity
    Kover = rng.standard_normal((4 * d, d))                       # 4x over capacity
    P = Kover @ np.linalg.inv(Kover.T @ Kover) @ Kover.T
    assert np.linalg.matrix_rank(P) <= d + 1, "over-capacity operator should be rank<=d"
    off = float(np.abs(P - np.diag(np.diag(P))).max())
    assert off > 1e-3, "over-capacity cross-talk should be non-zero, got %g" % off
    # The measurable claim the anchor-count sweep actually tests is not pinv's ABSOLUTE accuracy
    # (which falls with m simply because there are more competitors) but pinv's ADVANTAGE OVER
    # PLAIN COSINE. That advantage is what the capacity ceiling erodes. NOTE: lam must be the
    # PRIMARY value, not ~0 -- at m < d the matrix K^T K is itself rank-deficient, so a near-zero
    # lambda makes the d x d inverse numerically meaningless and the test measures noise, not
    # mechanism. (This bit an earlier draft of this very self-test.)
    def _adv(m_keys: int, noise: float = 0.8) -> float:
        g = np.random.default_rng(11)
        Kx = g.standard_normal((m_keys, d))
        Qx = Kx + noise * g.standard_normal((m_keys, d))
        tgt = np.arange(m_keys)
        a_p = float((score_pinv(Qx, Kx, lam_rel=LAMBDA_PRIMARY).argmax(axis=1) == tgt).mean())
        a_c = float((score_baseline(Qx, Kx).argmax(axis=1) == tgt).mean())
        return a_p - a_c
    adv_in, adv_over = _adv(d // 2), _adv(4 * d)
    assert adv_in > adv_over, ("pinv advantage must shrink past capacity: within=%.3f over=%.3f"
                               % (adv_in, adv_over))

    # 4. whitening decorrelates the anchor cloud
    A = rng.standard_normal((200, d)) @ rng.standard_normal((d, d))
    mu, W = fit_whiten(A)
    Cw = np.cov(((A - mu) @ W).T)
    off = np.abs(Cw - np.diag(np.diag(Cw))).max()
    assert off < 0.2, "whitening left off-diagonal %.3f" % off

    # 5. coarse-to-fine can only preserve-or-worsen the target rank vs its own fine scores, and
    #    NEVER improves hit@1 above the full-fine ceiling (pre-declared failure mode (d))
    Kq = rng.standard_normal((n, d))
    Qq = Kq + 0.3 * rng.standard_normal((n, d))
    base = score_baseline(Qq, Kq)
    ti = np.arange(n)
    c2f, mask = shortlist_c2f(Qq, Kq, base, seed=1)
    h_base, h_c2f = hit1(base, ti).mean(), hit1(c2f, ti).mean()
    assert h_c2f <= h_base + 1e-12, "c2f exceeded the full-fine ceiling: %.4f > %.4f" % (h_c2f, h_base)
    r_base, _ = rank_stats(base, ti)
    r_c2f, _ = rank_stats(c2f, ti)
    assert r_c2f["median_rank"] >= 1.0 and r_base["median_rank"] >= 1.0

    # 6. rank_stats agrees with a literal per-row computation, and masked anchors rank last
    Sm = np.array([[0.9, 0.5, 0.1], [0.1, 0.2, 0.3]])
    rs, rk = rank_stats(Sm, np.array([0, 0]))
    assert list(rk) == [1, 3], list(rk)
    # a target DROPPED from a shortlist must rank LAST among ALL anchors, not (k+1)-th. This is
    # the regression test for the bug the smoke gate caught: with 3 anchors of which only one is
    # shortlisted, a dropped target scored rank 2 and counted as "top-50".
    Sinf = np.array([[-np.inf, 0.5, -np.inf]])
    rs2, rk2 = rank_stats(Sinf, np.array([0]))
    assert int(rk2[0]) == 3, "dropped target must rank last, got %s" % rk2
    assert rs2["frac_target_dropped_from_shortlist"] == 1.0, rs2
    big = np.full((1, 200), -np.inf)
    big[0, :20] = np.linspace(1, 0, 20)
    rs3, _ = rank_stats(big, np.array([150]))
    assert rs3["frac_top50"] == 0.0, "dropped target must NOT count as top-50: %s" % rs3

    # 7. bootstrap sanity: identical arms give a zero delta whose CI contains zero
    a = rng.random(200) < 0.6
    bs = paired_bootstrap({"X": a, "Y": a.copy()}, [("d", "X", "Y")], 500, 7)
    assert bs["deltas"]["d"]["delta"] == 0.0 and not bs["deltas"]["d"]["excludes_zero"]

    print("SELF-TEST OK (7 checks incl. A0==canonicalize_fast, pinv capacity break, c2f ceiling)",
          flush=True)


# ---------------------------------------------------------------------------------------------
def run(run_mode: str, out_dir: str) -> dict:
    t0 = time.time()
    n_draws = N_DRAWS_FULL if run_mode == "full" else N_DRAWS_SMOKE
    n_boot = N_BOOTSTRAP if run_mode == "full" else 1000
    max_items = MAX_ITEMS_FULL if run_mode == "full" else MAX_ITEMS_SMOKE

    assets = NN.build_corpus_assets()
    _hb(out_dir, "corpus", t0)

    # ---- PRIMARY DRAW: salt "" == the sharpening cell's own split, so 84/647 and 0.40 compare ---
    items, item_diag, space, anchors, K, prof = SH._build_draw(assets, "", max_items)
    K = np.asarray(K, dtype=np.float64)
    n = len(items)
    pos = {a: i for i, a in enumerate(anchors)}
    ti = np.asarray([pos[it["target"]] for it in items])
    di = np.asarray([pos[it["distractor"]] for it in items])
    Q, n_zero = SH._queries(items, "real")
    Qs, _ = SH._queries(items, "scram")
    Q = np.asarray(Q, dtype=np.float64)
    Qs = np.asarray(Qs, dtype=np.float64)
    print("[draw] n_items=%d n_anchors=%d d=%d zero_queries=%d" % (n, len(anchors), K.shape[1],
                                                                   n_zero), flush=True)
    _hb(out_dir, "draw", t0, {"n_items": n, "n_anchors": len(anchors)})

    # ---- arms -----------------------------------------------------------------------------------
    scores: Dict[str, np.ndarray] = {}
    scores["A0_BASELINE"] = score_baseline(Q, K)
    scores["A1_WHITEN"] = score_whiten(Q, K)
    scores["A2_PINV"] = score_pinv(Q, K, LAMBDA_PRIMARY)
    scores["A3_C2F"], mask_a3 = shortlist_c2f(Q, K, scores["A0_BASELINE"], MASTER_SEED + 1)

    mu, W = fit_whiten(K)
    Kw, Qw = (K - mu) @ W, (Q - mu) @ W
    full_fine = score_pinv(Qw, Kw, LAMBDA_PRIMARY)
    scores["A4_FULL"], mask_a4 = shortlist_c2f(Qw, Kw, full_fine, MASTER_SEED + 2)

    # floors
    scores["F_SCRAMBLE"] = score_baseline(Qs, K)
    rng_f = np.random.default_rng(MASTER_SEED + 3)
    counts = assets["counts"]
    freq_vec = np.asarray([float(counts.get(a, 0)) for a in anchors])
    scores["F_FREQUENCY"] = np.tile(freq_vec[None, :], (n, 1)) + 1e-9 * rng_f.standard_normal((n, len(anchors)))

    # lambda sensitivity (DECLARED as sensitivity, not selection)
    lam_sens = {}
    for lr in LAMBDAS_REL:
        Sl = score_pinv(Q, K, lr)
        rs, _ = rank_stats(Sl, ti)
        lam_sens["lam_rel_%g" % lr] = {"rank": rs, "hit1": round(float(hit1(Sl, ti).mean()), 6),
                                       "afc2": round(float(afc2(Sl, ti, di).mean()), 6)}
        del Sl
    print("[lambda] " + " | ".join("%s med_rank=%.0f hit1=%.4f" % (k, v["rank"]["median_rank"],
                                                                   v["hit1"])
                                   for k, v in sorted(lam_sens.items())), flush=True)

    # 2AFC SOURCE, declared: a shortlist is an OPEN-VOCABULARY device. In a two-alternative forced
    # choice the two candidates are named, so no shortlist is consulted and both are scored
    # directly. Scoring 2AFC on the MASKED matrix would compare -inf with -inf and score every
    # such item wrong, manufacturing a below-chance number that describes the mask, not the
    # mechanism (the smoke gate showed exactly that: A4 2AFC 0.1067). The c2f arms therefore take
    # 2AFC from their own UNMASKED fine scores; every other arm is unchanged.
    afc_src = dict(scores)
    afc_src["A3_C2F"] = scores["A0_BASELINE"]
    afc_src["A4_FULL"] = full_fine

    per_arm, hits, afcs = {}, {}, {}
    for name in sorted(scores):
        rs, _rk = rank_stats(scores[name], ti)
        hits[name] = hit1(scores[name], ti)
        afcs[name] = afc2(afc_src[name], ti, di)
        per_arm[name] = {"rank": rs, "hit1": round(float(hits[name].mean()), 6),
                         "afc2": round(float(afcs[name].mean()), 6)}
        print("[arm] %-12s median_rank=%6.1f/%d frac_top50=%.4f hit@1=%.5f 2AFC=%.4f"
              % (name, rs["median_rank"], len(anchors), rs["frac_top50"],
                 per_arm[name]["hit1"], per_arm[name]["afc2"]), flush=True)
        _hb(out_dir, "arm", t0, {"arm": name})

    per_arm["A3_C2F"]["shortlist_hit"] = round(float(mask_a3[np.arange(n), ti].mean()), 6)
    per_arm["A4_FULL"]["shortlist_hit"] = round(float(mask_a4[np.arange(n), ti].mean()), 6)

    dl = [("d_%s_minus_A0" % a, a, "A0_BASELINE")
          for a in ("A1_WHITEN", "A2_PINV", "A3_C2F", "A4_FULL")]
    dl += [("d_A0_minus_SCRAMBLE", "A0_BASELINE", "F_SCRAMBLE"),
           ("d_A0_minus_FREQUENCY", "A0_BASELINE", "F_FREQUENCY")]
    bs_hit = paired_bootstrap(hits, dl, n_boot, BOOTSTRAP_SEED)
    bs_afc = paired_bootstrap(afcs, dl, n_boot, BOOTSTRAP_SEED + 1)
    _hb(out_dir, "bootstrap", t0)

    # ---- BETWEEN-DRAW SD (prereg: n_draws>=4; the baseline's n_draws=2 sd is unusable) ----------
    draw_rows = []
    for k in range(1, n_draws):
        salt = "draw%d" % k
        try:
            it2, _d2, _sp2, an2, K2, _p2 = SH._build_draw(assets, salt, max_items)
        except AssertionError as exc:
            print("[draw] SKIP %s: %s" % (salt, exc), flush=True)
            continue
        K2 = np.asarray(K2, dtype=np.float64)
        p2 = {a: i for i, a in enumerate(an2)}
        t2 = np.asarray([p2[x["target"]] for x in it2])
        d2i = np.asarray([p2[x["distractor"]] for x in it2])
        Q2 = np.asarray(SH._queries(it2, "real")[0], dtype=np.float64)
        row = {"salt": salt, "n_items": len(it2), "n_anchors": len(an2)}
        for nm, fn in (("A0_BASELINE", score_baseline), ("A1_WHITEN", score_whiten),
                       ("A2_PINV", score_pinv)):
            S2 = fn(Q2, K2)
            r2, _ = rank_stats(S2, t2)
            row[nm] = {"median_rank": r2["median_rank"], "frac_top50": r2["frac_top50"],
                       "hit1": round(float(hit1(S2, t2).mean()), 6),
                       "afc2": round(float(afc2(S2, t2, d2i).mean()), 6)}
            del S2
        draw_rows.append(row)
        print("[draw %s] n=%d anchors=%d A0 hit1=%.5f med_rank=%.0f"
              % (salt, len(it2), len(an2), row["A0_BASELINE"]["hit1"],
                 row["A0_BASELINE"]["median_rank"]), flush=True)
        _hb(out_dir, "extra_draw", t0, {"salt": salt})

    def _bd(metric: str, arm: str) -> float:
        vals = [per_arm[arm]["rank"][metric] if metric in ("median_rank", "frac_top50")
                else per_arm[arm][metric]]
        vals += [r[arm][metric] for r in draw_rows if arm in r]
        return round(float(np.std(vals, ddof=1)), 6) if len(vals) > 1 else float("nan")

    between_draw = {"n_draws": 1 + len(draw_rows),
                    "sd": {m: {a: _bd(m, a) for a in ("A0_BASELINE", "A1_WHITEN", "A2_PINV")}
                           for m in ("median_rank", "frac_top50", "hit1", "afc2")},
                    "rows": draw_rows}
    print("[floors] between-draw sd (n_draws=%d): hit1 A0=%.5f median_rank A0=%.2f"
          % (between_draw["n_draws"], between_draw["sd"]["hit1"]["A0_BASELINE"],
             between_draw["sd"]["median_rank"]["A0_BASELINE"]), flush=True)

    # ---- ANCHOR-COUNT SWEEP: the mandatory test of pre-declared failure mode (a) -----------------
    # The pinv precondition is n_anchors <= d (=256). If A2 beats A0 BELOW that line and not above,
    # the mechanism is real and our dimensionality is the binding constraint -- a scale result.
    # If A2 fails even below it, the transfer genuinely does not hold on OUR codes.
    sweep = {}
    for m in ANCHOR_SWEEP:
        if m > len(anchors):
            continue
        acc = {a: [] for a in ("A0_BASELINE", "A1_WHITEN", "A2_PINV")}
        rk = {a: [] for a in acc}
        n_pool = 0
        for r in range(SWEEP_REPLICATES):
            rg = np.random.default_rng(MASTER_SEED + 100 * m + r)
            sub = np.sort(rg.choice(len(anchors), size=m, replace=False))
            in_sub = np.zeros(len(anchors), dtype=bool)
            in_sub[sub] = True
            keep = np.flatnonzero(in_sub[ti])
            if len(keep) < 5:
                continue
            remap = {int(g): j for j, g in enumerate(sub)}
            t_loc = np.asarray([remap[int(ti[i])] for i in keep])
            Ksub, Qsub = K[sub], Q[keep]
            n_pool += len(keep)
            for a, fn in (("A0_BASELINE", score_baseline), ("A1_WHITEN", score_whiten),
                          ("A2_PINV", score_pinv)):
                Ss = fn(Qsub, Ksub)
                acc[a].append(hit1(Ss, t_loc))
                rk[a].append((Ss > Ss[np.arange(len(keep)), t_loc][:, None]).sum(axis=1) + 1)
                del Ss
        if n_pool == 0:
            continue
        sweep["m%d" % m] = {
            "n_anchors": m, "n_pooled_items": n_pool,
            "within_pinv_capacity": bool(m <= K.shape[1]),
            **{a: {"hit1": round(float(np.concatenate(acc[a]).mean()), 6),
                   "median_rank": float(np.median(np.concatenate(rk[a]))),
                   "frac_top50": round(float((np.concatenate(rk[a]) <= 50).mean()), 6)}
               for a in acc}}
        s = sweep["m%d" % m]
        print("[sweep] m=%-4d (cap_ok=%s n=%4d) A0 hit1=%.4f | A1 %.4f | A2 %.4f | "
              "A2-A0=%+.4f" % (m, s["within_pinv_capacity"], n_pool, s["A0_BASELINE"]["hit1"],
                               s["A1_WHITEN"]["hit1"], s["A2_PINV"]["hit1"],
                               s["A2_PINV"]["hit1"] - s["A0_BASELINE"]["hit1"]), flush=True)
        _hb(out_dir, "sweep", t0, {"m": m})

    # ---- verdict --------------------------------------------------------------------------------
    sd_rank = between_draw["sd"]["median_rank"]["A0_BASELINE"]
    sd_hit = between_draw["sd"]["hit1"]["A0_BASELINE"]
    best_arm, best_gain = None, -1e9
    for a in ("A1_WHITEN", "A2_PINV", "A3_C2F", "A4_FULL"):
        g = per_arm[a]["hit1"] - per_arm["A0_BASELINE"]["hit1"]
        if g > best_gain:
            best_arm, best_gain = a, g
    base_rank = per_arm["A0_BASELINE"]["rank"]["median_rank"]
    best_rank_arm = min(("A1_WHITEN", "A2_PINV", "A3_C2F", "A4_FULL"),
                        key=lambda a: per_arm[a]["rank"]["median_rank"])
    br = per_arm[best_rank_arm]["rank"]
    rank_cut = 1.0 - br["median_rank"] / max(base_rank, 1e-9)
    top50_gain = br["frac_top50"] - per_arm["A0_BASELINE"]["rank"]["frac_top50"]
    ci = bs_hit["deltas"]["d_%s_minus_A0" % best_arm]
    hard_pass = (rank_cut >= 0.33 and top50_gain >= 0.10 and ci["excludes_zero"]
                 and best_gain > (sd_hit if sd_hit == sd_hit else 0.0))
    sub_cap = [v for v in sweep.values() if v["within_pinv_capacity"]]
    pinv_helps_in_cap = any(v["A2_PINV"]["hit1"] - v["A0_BASELINE"]["hit1"] > 0.01
                            for v in sub_cap)
    moved = abs(br["median_rank"] - base_rank) > (sd_rank if sd_rank == sd_rank else 0.0)
    if hard_pass:
        verdict = "HARD_PASS"
    elif pinv_helps_in_cap:
        verdict = "MIDDLE_BAND_MECHANISM_REAL_BELOW_CAPACITY_ONLY"
    elif not moved:
        verdict = "HARD_FAIL_NO_EFFECT"
    else:
        verdict = "MIDDLE_BAND"
    msg = ("n_items=%d n_anchors=%d d=%d | A0 median_rank=%.0f/%d (baseline 84/647) top50=%.4f "
           "(baseline 0.40) hit@1=%.5f (baseline 0.09833) 2AFC=%.4f (baseline 0.7083) | BEST-rank "
           "arm %s median_rank=%.0f cut=%+.1f%% top50=%+.4f | BEST-hit@1 arm %s d=%+.5f "
           "CI=[%.5f,%.5f] | floors: scramble hit@1=%.5f 2AFC=%.4f, frequency hit@1=%.5f "
           "2AFC=%.4f, between-draw sd(n=%d) hit@1=%.5f median_rank=%.2f | pinv within-capacity "
           "(m<=256) helps: %s | c2f shortlist_hit=%.4f (pre-declared COST arm, ceiling=A0)"
           % (n, len(anchors), K.shape[1], base_rank, len(anchors),
              per_arm["A0_BASELINE"]["rank"]["frac_top50"], per_arm["A0_BASELINE"]["hit1"],
              per_arm["A0_BASELINE"]["afc2"], best_rank_arm, br["median_rank"], -100.0 * rank_cut,
              top50_gain, best_arm, best_gain, ci["ci_lo"], ci["ci_hi"],
              per_arm["F_SCRAMBLE"]["hit1"], per_arm["F_SCRAMBLE"]["afc2"],
              per_arm["F_FREQUENCY"]["hit1"], per_arm["F_FREQUENCY"]["afc2"],
              between_draw["n_draws"], sd_hit, sd_rank, pinv_helps_in_cap,
              per_arm["A3_C2F"]["shortlist_hit"]))
    print("[verdict] %s | %s" % (verdict, msg), flush=True)

    return {
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH, "run_mode": run_mode,
        "ts_iso": _now(), "verdict": verdict, "verdict_msg": msg,
        "baseline_quoted": {
            "source": "data/exp_sharpening_readout_sister_separation_v1_SMOKE_n600/metrics.json",
            "median_rank": BASE_MEDIAN_RANK, "n_anchors": BASE_N_ANCHORS,
            "frac_top50": BASE_TOP50_FRAC, "hit1": BASE_HIT1, "afc2_S0": BASE_2AFC,
            "SCOPE_NOTE": ("SMOKE run at 647 anchors / n=600. NOT the 5491-anchor space, whose "
                           "hit@1 is 0.0480 (exp_grounding_readout_known_answer_v1). The two "
                           "hit@1 numbers describe different anchor-set sizes and must not be "
                           "compared to each other.")},
        "stages_already_live": {
            "whitening": False, "pseudoinverse_write": False, "coarse_to_fine": False,
            "evidence": ("hdlab/reading_grounding_loop.py: ConceptSpace.observe is "
                         "`self._sums[lemma] += ctx_vec` (Hebbian); canonicalize_fast is "
                         "`(mat @ nb)/(norms*nn)` + argmax (plain cosine). ReadoutConfig FIX 2 "
                         "anchor_background is a per-anchor mean/sd z-score = DIAGONAL whitening "
                         "only, and is OFF by default.")},
        "n_items": n, "n_anchors": len(anchors), "d": int(K.shape[1]),
        "overcompleteness_vs_pinv_capacity": round(len(anchors) / float(K.shape[1]), 3),
        "item_diag": item_diag, "n_zero_queries": int(n_zero),
        "per_arm": per_arm,
        "bootstrap_hit1": bs_hit, "bootstrap_2afc": bs_afc,
        "lambda_sensitivity": lam_sens, "lambda_primary_rel": LAMBDA_PRIMARY,
        "between_draw": between_draw,
        "anchor_count_sweep": sweep,
        "config": {"d_coarse": D_COARSE, "shortlist_frac": SHORTLIST_FRAC,
                   "whiten_eps_rel": WHITEN_EPS_REL, "n_bootstrap": n_boot,
                   "sweep_replicates": SWEEP_REPLICATES, "master_seed": MASTER_SEED},
        "elapsed_s": round(time.time() - t0, 1), "python": platform.python_version(),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=["full", "smoke"])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        _selftest()
        return
    out = _out_dir(args.run_mode)
    print("[start] %s run_mode=%s out=%s" % (ANCHOR_NAME, args.run_mode, out), flush=True)
    try:
        metrics = run(args.run_mode, out)
    except Exception as exc:                                                  # noqa: BLE001
        _atomic_write(os.path.join(out, "metrics.json"),
                      {"anchor_name": ANCHOR_NAME, "run_mode": args.run_mode, "ts_iso": _now(),
                       "verdict": "CRASH", "verdict_msg": repr(exc),
                       "traceback": traceback.format_exc()})
        raise
    _atomic_write(os.path.join(out, "metrics.json"), metrics)
    print("[done] -> %s" % os.path.join(out, "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
