"""exp_forgetting_kernel_signreadout_v1 -- does the terminal sign() destroy the forgetting exponent?

Pre-registration: preregs/2026-08-14_forgetting_kernel_signreadout_v1.md (READ IT FIRST; the
analytic prediction, the arms, the AIC rule and the PASS/FAIL bands are all declared there before
this file was run).

STEP 2 of notes/SUBSTRATE_STRATEGY.md. Tests the hypothesis raised in
notes/drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md sec 4.4: that the substrate's
forgetting exponent is not absent but destroyed by the np.sign() at
hdlab/reading_grounding_loop.py:490/504.

PRIMARY MEASURAND: the fitted log-log slope of SNR(t) vs t (Benna-Fusi's own SNR definition),
plus a pre-declared AIC comparison of a power-law fit against an exponential fit on the same
response variable (log SNR), same n, same parameter count.

TIME AXIS: encounters OF THE TRACKED LEMMA, which is exactly Benna-Fusi's "memories stored at this
synapse" -- _sums[lemma] is a bank of d dedicated accumulators and every observe(lemma, v) writes to
all of them. Anchor-DICTIONARY growth is a second, NON-Benna-Fusi channel and is measured separately
in section CHANNEL_B, never fitted against a Benna-Fusi prediction.

hdlab/ is NOT modified by this cell. The live functions (context_vector_masked, ConceptSpace) are
called verbatim; nothing is re-implemented except the argmax in CHANNEL_B, which is noted there.
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import random
import re
import sys
import time

import numpy as np  # must come AFTER the thread pins above

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key

CORPUS = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

STREAMS = ("synth", "real", "scram_order", "scram_content")
READOUTS = ("graded", "binarised")

CFG = {
    "smoke": {"n_lemmas": 8, "t_max": 64, "max_scan": 40000, "n_probes": 128, "n_grid": 14,
              "n_boot": 400, "chanb_max_anchors": 200},
    "full": {"n_lemmas": 60, "t_max": 1024, "max_scan": 400000, "n_probes": 128, "n_grid": 24,
             "n_boot": 2000, "chanb_max_anchors": 4000},
}

FIT_T_MIN = 4          # PRE-DECLARED fit window floor (asymptotics invalid at t=1,2)
UNIT_NS = "v2meanfit"  # unit-key namespace. Bumped when the ESTIMATOR changed, so the original
                       # pre-declared (biased) units stay on disk in units.jsonl for audit
                       # instead of being deleted or silently overwritten.


def uk(readout: str, stream: str) -> str:
    return unit_key(readout, stream, UNIT_NS)

DAIC_DECISIVE = 10.0   # PRE-DECLARED decision threshold


# ------------------------------------------------------------------ fitting / model comparison

def _ols(x: np.ndarray, y: np.ndarray):
    """OLS y = a + b*x. Returns (a, b, rss, n)."""
    n = int(x.size)
    xm = float(x.mean())
    ym = float(y.mean())
    sxx = float(((x - xm) ** 2).sum())
    if sxx <= 0.0:
        return ym, 0.0, float(((y - ym) ** 2).sum()), n
    b = float(((x - xm) * (y - ym)).sum() / sxx)
    a = ym - b * xm
    resid = y - (a + b * x)
    return a, b, float((resid ** 2).sum()), n


def _aic(rss: float, n: int, k: int = 3) -> float:
    """Gaussian AIC. k=3: intercept, slope, variance. Identical k for both models, so the
    comparison is like-for-like on the same response variable."""
    rss = max(rss, 1e-300)
    return n * math.log(rss / n) + 2 * k


def _r2(rss: float, y: np.ndarray) -> float:
    tss = float(((y - y.mean()) ** 2).sum())
    return float(1.0 - rss / tss) if tss > 0 else float("nan")


def compare_fits(t: np.ndarray, snr: np.ndarray) -> dict:
    """POWER: log snr = a + b*log t. EXPONENTIAL: log snr = c + e*t. Same response (log snr),
    same n, same k -> AIC directly comparable. dAIC = AIC_exp - AIC_pow; > +10 power wins."""
    ok = np.isfinite(snr) & (snr > 0) & np.isfinite(t) & (t > 0)
    n_dropped = int((~ok).sum())
    t = t[ok].astype(np.float64)
    y = np.log(snr[ok].astype(np.float64))
    if y.size < 4:
        return {"n": int(y.size), "n_dropped": n_dropped, "insufficient": True}
    a, b, rss_p, n = _ols(np.log(t), y)
    c, e, rss_e, _ = _ols(t, y)
    aic_p, aic_e = _aic(rss_p, n), _aic(rss_e, n)
    daic = aic_e - aic_p
    return {
        "n": n, "n_dropped": n_dropped, "insufficient": False,
        "power_slope": b, "power_intercept": a, "power_r2": _r2(rss_p, y), "power_aic": aic_p,
        "exp_rate": e, "exp_intercept": c, "exp_r2": _r2(rss_e, y), "exp_aic": aic_e,
        "dAIC_exp_minus_pow": daic,
        "winner": ("power" if daic > DAIC_DECISIVE
                   else ("exponential" if daic < -DAIC_DECISIVE else "ambiguous")),
    }


def _p_walk_zero(t: int) -> float:
    """P(W_t = 0) for a t-step +-1 walk (t even), via lgamma so t=1024 does not overflow.
    For odd t the walk cannot be 0 and the relevant expectation equals the same asymptote, so
    sqrt(2/(pi t)) is used there."""
    if t % 2:
        return math.sqrt(2.0 / (math.pi * t))
    lg = math.lgamma(t + 1) - 2 * math.lgamma(t / 2 + 1) - t * math.log(2.0)
    return math.exp(lg)


def exact_reference_slopes(t_window: np.ndarray, d: int) -> dict:
    """The slope the fitter returns on the EXACT, NOISE-FREE closed-form curves, evaluated on
    THIS t-grid and THIS fit window.

    Why this exists (2026-08-14, disclosed in the prereg): the closed forms are only ASYMPTOTICALLY
    t^-1/2. The graded curve is sqrt(d/(t+1)), whose local log-log slope is -0.5*t/(t+1) -- at the
    window floor t=4 that is -0.40, not -0.50. So an OLS slope over a window starting at t=4 is
    LEGITIMATELY flatter than -1/2 by ~0.018, purely as a window artifact and with no estimator
    defect involved. Comparing a measured slope to -0.5 therefore mis-scores it. Comparing it to
    the exact curve pushed through the SAME fitter on the SAME grid removes the artifact exactly."""
    g = np.sqrt(d / (t_window + 1.0))
    b = np.array([d * _p_walk_zero(int(t)) / math.sqrt(d) for t in t_window])
    return {"graded": compare_fits(t_window, g)["power_slope"],
            "binarised": compare_fits(t_window, b)["power_slope"],
            "asymptote": -0.5}


def mean_curve(curves: np.ndarray) -> np.ndarray:
    """Per-t MEAN SNR across tracked lemmas (nan-aware)."""
    with np.errstate(invalid="ignore"):
        return np.nanmean(curves, axis=0)


def fit_mean_curve(t_grid: np.ndarray, curves: np.ndarray) -> dict:
    """THE CORRECTED PRIMARY ESTIMATOR (added 2026-08-14, disclosed in the prereg).

    Fits log(mean-over-lemmas SNR) against log t, with n = the number of t POINTS.

    Two independent defects in the originally pre-declared pooled-per-lemma estimator, BOTH
    caught by the known-answer synth arm and neither by any arm of interest:

    1. SURVIVORSHIP BIAS. Pooling per-lemma log SNR must drop non-positive SNRs. Per-lemma SNR has
       s.d. ~1 by construction, so at large t (where the true SNR falls below ~1) a large minority
       of lemmas go negative and are DROPPED -- leaving only the upward fluctuations. That inflates
       log SNR at exactly the large-t end that sets the slope, and FLATTENS it. Measured on the
       synth arm, whose true slope is -0.5 by derivation: 96/1140 points dropped and the pooled
       estimator returned -0.4271 with a CI EXCLUDING -0.5. Averaging BEFORE the log drops nothing.
    2. PSEUDO-REPLICATION. The pooled fit counted 19 t-points x 60 lemmas as n=1140 independent
       observations. The independent units are the LEMMAS, and the curve SHAPE is what is being
       fitted, so the honest n for AIC is the number of t points. The pooled dAIC values were
       inflated accordingly and must not be quoted.

    The pooled fit is still computed and reported as `fit_pooled_perlemma_PREDECLARED_BIASED` so
    the originally pre-declared number stays auditable."""
    m = mean_curve(curves)
    return compare_fits(t_grid, m)


def cluster_bootstrap_slope(t_grid: np.ndarray, curves: np.ndarray, n_boot: int, seed: int) -> dict:
    """Percentile CI on the power-law slope of the MEAN curve, resampling TRACKED LEMMAS."""
    rng = np.random.default_rng(seed)
    n_lem = curves.shape[0]
    point = fit_mean_curve(t_grid, curves)
    if point.get("insufficient"):
        return {"point": None, "ci_lo": None, "ci_hi": None, "n_boot": 0}
    slopes = []
    for _ in range(n_boot):
        idx = rng.integers(0, n_lem, size=n_lem)
        f = fit_mean_curve(t_grid, curves[idx])
        if not f.get("insufficient"):
            slopes.append(f["power_slope"])
    if len(slopes) < 20:
        return {"point": point["power_slope"], "ci_lo": None, "ci_hi": None, "n_boot": len(slopes)}
    s = np.array(sorted(slopes))
    return {"point": point["power_slope"], "ci_lo": float(np.percentile(s, 2.5)),
            "ci_hi": float(np.percentile(s, 97.5)), "n_boot": len(slopes)}


# ------------------------------------------------------------------ SNR core

def snr_curve(v0: np.ndarray, interference: list, t_grid: list, probes: np.ndarray,
              binarise: bool) -> np.ndarray:
    """Benna-Fusi SNR(t): signal = dot(v0, R(sum_t)); noise = sd over probes of dot(u, R(sum_t)).
    R = sign(.) when binarise else identity. ||R|| cancels, so the two readouts are comparable."""
    out = np.full(len(t_grid), np.nan, dtype=np.float64)
    acc = v0.astype(np.float64).copy()
    nxt = 0
    tmax = max(t_grid)
    for t in range(0, tmax + 1):
        if t > 0:
            acc += interference[t - 1]
        while nxt < len(t_grid) and t_grid[nxt] == t:
            r = np.sign(acc) if binarise else acc
            sig = float(v0 @ r)
            noise = float(np.std(probes @ r))
            out[nxt] = (sig / noise) if noise > 0 else np.nan
            nxt += 1
        if nxt >= len(t_grid):
            break
    return out


def log_grid(t_max: int, n: int) -> list:
    g = np.unique(np.round(np.geomspace(1, t_max, n)).astype(int))
    return sorted(set(int(x) for x in g if 1 <= x <= t_max))


# ------------------------------------------------------------------ corpus

def build_corpus_pools(sentence_lemmas, context_vector_masked, cfg, log):
    """Scan simplewiki, pick the most frequent lemmas with >= t_max+1 occurrences, and vectorise
    ONLY those sentences. Returns {lemma: [ctx vectors]} plus scan stats."""
    need = cfg["t_max"] + 1
    log("scanning corpus (max %d sentences) ..." % cfg["max_scan"])
    t0 = time.time()
    counts = {}
    hits = {}
    sents = []
    with open(CORPUS, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if i >= cfg["max_scan"]:
                break
            s = line.strip()
            if len(s) < 20:
                sents.append("")
                continue
            sents.append(s)
            for lem in sentence_lemmas(s):
                counts[lem] = counts.get(lem, 0) + 1
                if lem not in hits:
                    hits[lem] = []
                if len(hits[lem]) < need:
                    hits[lem].append(i)
    log("scan done in %.1fs, %d sentences, %d distinct lemmas" % (time.time() - t0, len(sents),
                                                                  len(counts)))
    eligible = sorted([l for l, c in counts.items() if c >= need],
                      key=lambda l: (-counts[l], l))
    if len(eligible) < cfg["n_lemmas"] + 20:
        raise SystemExit("PRECONDITION FAIL: only %d lemmas reach %d occurrences in %d sentences; "
                         "raise max_scan or lower t_max" % (len(eligible), need, cfg["max_scan"]))
    tracked = sorted(eligible[:cfg["n_lemmas"]])
    # probe/distractor pool: lemmas well AWAY from the tracked set, so probes are genuinely
    # unrelated memories rather than near-synonyms of the tracked lemmas.
    pool_lemmas = sorted(eligible[cfg["n_lemmas"] + 10:cfg["n_lemmas"] + 60])
    log("vectorising %d tracked + %d pool lemmas ..." % (len(tracked), len(pool_lemmas)))
    t1 = time.time()
    vecs = {}
    for lem in sorted(set(tracked) | set(pool_lemmas)):
        seq = []
        for i in hits[lem]:
            v = context_vector_masked(sents[i], lem)
            if np.any(v != 0):
                seq.append(v.astype(np.float64))
        vecs[lem] = seq
    log("vectorised in %.1fs" % (time.time() - t1))
    tracked = [l for l in tracked if len(vecs[l]) >= need]
    return {"vecs": vecs, "tracked": tracked, "pool": pool_lemmas,
            "counts": {l: counts[l] for l in tracked},
            "n_scanned": len(sents), "n_distinct_lemmas": len(counts)}


# ------------------------------------------------------------------ one unit

def run_unit(readout: str, stream: str, cfg: dict, corpus, d: int, seed: int, log) -> dict:
    binarise = (readout == "binarised")
    t_grid = log_grid(cfg["t_max"], cfg["n_grid"])
    rng = np.random.default_rng(seed)
    n_lem = cfg["n_lemmas"]
    need = cfg["t_max"] + 1

    if stream == "synth":
        probes = rng.choice([-1.0, 1.0], size=(cfg["n_probes"], d))
        curves = []
        for _ in range(n_lem):
            v0 = rng.choice([-1.0, 1.0], size=d)
            interf = [rng.choice([-1.0, 1.0], size=d) for _ in range(cfg["t_max"])]
            curves.append(snr_curve(v0, interf, t_grid, probes, binarise))
    else:
        tracked = corpus["tracked"][:n_lem]
        pool = corpus["pool"]
        probe_src = []
        for lem in pool:
            probe_src.extend(corpus["vecs"][lem][:40])
        if len(probe_src) < cfg["n_probes"]:
            raise SystemExit("PRECONDITION FAIL: probe pool too small (%d)" % len(probe_src))
        pidx = rng.choice(len(probe_src), size=cfg["n_probes"], replace=False)
        probes = np.stack([probe_src[int(i)] for i in sorted(pidx)], axis=0)
        curves = []
        for lem in tracked:
            seq = corpus["vecs"][lem]
            if len(seq) < need:
                continue
            v0 = seq[0]
            if stream == "real":
                interf = seq[1:need]
            elif stream == "scram_order":
                order = list(range(1, need))
                random.Random(seed + hash(lem) % 100000).shuffle(order)
                interf = [seq[i] for i in order]
            elif stream == "scram_content":
                sidx = rng.choice(len(probe_src), size=cfg["t_max"], replace=True)
                interf = [probe_src[int(i)] for i in sidx]
            else:
                raise SystemExit("unknown stream %s" % stream)
            curves.append(snr_curve(v0, interf, t_grid, probes, binarise))

    curves = np.stack(curves, axis=0)
    tg = np.array(t_grid, dtype=np.float64)
    win = tg >= FIT_T_MIN
    # PRIMARY (corrected): mean-over-lemmas first, then log-log fit; n = number of t points.
    fit_win = fit_mean_curve(tg[win], curves[:, win])
    fit_all = fit_mean_curve(tg, curves)
    # The originally pre-declared estimator, retained verbatim so the number stays auditable.
    fit_pooled = compare_fits(np.tile(tg[win], curves.shape[0]), curves[:, win].reshape(-1))
    boot = cluster_bootstrap_slope(tg[win], curves[:, win], cfg["n_boot"], seed + 7)
    with np.errstate(invalid="ignore"):
        med = np.nanmedian(curves, axis=0)
        mn = np.nanmean(curves, axis=0)
    log("  %-9s %-14s slope=%.4f [%s, %s] dAIC=%+.1f winner=%s" % (
        readout, stream, fit_win.get("power_slope", float("nan")),
        ("%.4f" % boot["ci_lo"]) if boot.get("ci_lo") is not None else "na",
        ("%.4f" % boot["ci_hi"]) if boot.get("ci_hi") is not None else "na",
        fit_win.get("dAIC_exp_minus_pow", float("nan")), fit_win.get("winner")))
    return {
        "readout": readout, "stream": stream, "n_lemmas_used": int(curves.shape[0]),
        "d": d, "t_grid": t_grid, "fit_window_t_min": FIT_T_MIN,
        "estimator": "mean-over-lemmas then log-log OLS; n = number of t points",
        "exact_reference_slopes_this_grid": exact_reference_slopes(tg[win], d),
        "fit": fit_win, "fit_full_window_sensitivity": fit_all,
        "fit_pooled_perlemma_PREDECLARED_BIASED": fit_pooled,
        "slope_ci": boot,
        "mean_snr_by_t": [None if not np.isfinite(x) else float(x) for x in mn],
        "median_snr_by_t": [None if not np.isfinite(x) else float(x) for x in med],
    }


# ------------------------------------------------------------------ CHANNEL B (non-BF axis)

def run_channel_b(readout: str, cfg: dict, corpus, ConceptSpace, log) -> dict:
    """Retrieval accuracy vs ANCHOR-DICTIONARY SIZE. Explicitly NOT a Benna-Fusi axis (they have
    no dictionary and no argmax); reported so the axis question is answered with a measurement.
    The argmax below is the only re-implementation in this cell, and it is exactly what
    ConceptSpace.anchor_matrix's docstring says canonicalize_fast does with its rows."""
    tracked = corpus["tracked"]
    pool = corpus["pool"]
    space = ConceptSpace()
    held = {}
    order = sorted(set(tracked) | set(pool))
    for lem in order:
        seq = corpus["vecs"][lem]
        if len(seq) < 12:
            continue
        held[lem] = seq[-5:]
        for v in seq[:-5][:64]:
            space.observe(lem, v)
    probe_lemmas = [l for l in tracked if l in held]
    sizes = sorted(set(int(x) for x in
                       np.unique(np.round(np.geomspace(2, max(4, len(order)), 8)).astype(int))))
    rows = []
    anchors_all, mat_all = space.anchor_matrix()
    a_index = {a: i for i, a in enumerate(anchors_all)}
    for m in sizes:
        sub = order[:m]
        idxs = [a_index[a] for a in sub if a in a_index]
        if len(idxs) < 2:
            continue
        sub_names = [anchors_all[i] for i in idxs]
        sub_mat = mat_all[idxs]
        nrm = np.linalg.norm(sub_mat, axis=1)
        nrm[nrm == 0] = 1.0
        ok = tot = 0
        for lem in probe_lemmas:
            if lem not in sub_names:
                continue
            for q in held[lem]:
                qn = np.linalg.norm(q)
                if qn == 0:
                    continue
                cos = (sub_mat @ q) / (nrm * qn)
                if sub_names[int(np.argmax(cos))] == lem:
                    ok += 1
                tot += 1
        if tot:
            rows.append({"n_anchors": len(idxs), "acc": ok / tot, "n": tot})
    log("  CHANNEL_B %s: %s" % (readout, [(r["n_anchors"], round(r["acc"], 3)) for r in rows]))
    return {"readout": readout, "note": "NON-Benna-Fusi axis (dictionary competition), reported "
                                        "separately, never fitted against a BF prediction",
            "accuracy_vs_anchor_count": rows}


# ------------------------------------------------------------------ self-test

def self_test(log) -> bool:
    d = 256
    rng = np.random.default_rng(20260814)
    t_grid = log_grid(512, 18)
    probes = rng.choice([-1.0, 1.0], size=(128, d))
    res = {}
    for name, binar in (("graded", False), ("binarised", True)):
        curves = []
        for _ in range(64):
            v0 = rng.choice([-1.0, 1.0], size=d)
            interf = [rng.choice([-1.0, 1.0], size=d) for _ in range(512)]
            curves.append(snr_curve(v0, interf, t_grid, probes, binar))
        c = np.stack(curves, axis=0)
        tg = np.array(t_grid, dtype=np.float64)
        w = tg >= FIT_T_MIN
        f = fit_mean_curve(tg[w], c[:, w])   # the CORRECTED primary estimator
        res[name] = f
        log("  selftest %-9s slope=%.4f dAIC=%+.1f" % (name, f["power_slope"],
                                                       f["dAIC_exp_minus_pow"]))

    ok = True
    sg = res["graded"]["power_slope"]
    sb = res["binarised"]["power_slope"]
    tgw = np.array([t for t in t_grid if t >= FIT_T_MIN], dtype=np.float64)
    ref = exact_reference_slopes(tgw, d)
    log("  selftest EXACT-curve reference slopes on this grid: graded %.4f binarised %.4f "
        "(asymptote -0.5)" % (ref["graded"], ref["binarised"]))
    if abs(sg - ref["graded"]) > 0.04:
        log("  SELFTEST FAIL 1: graded synth slope %.4f differs from exact-curve %.4f by %.4f"
            % (sg, ref["graded"], abs(sg - ref["graded"]))); ok = False
    if abs(sb - ref["binarised"]) > 0.04:
        log("  SELFTEST FAIL 2: binarised synth slope %.4f differs from exact-curve %.4f by %.4f"
            % (sb, ref["binarised"], abs(sb - ref["binarised"]))); ok = False

    # 3. PREFACTOR gate -- the thing the sign() actually costs. AMENDED 2026-08-14 (disclosed in
    # the prereg): the original n=24 MEDIAN estimator had a sampling sd of ~0.2 on a quantity of
    # ~0.6, i.e. it could not resolve a +-0.10 band at all. Re-specified as an n=400 MEAN at t=64
    # against the EXACT finite-t closed forms, which is both properly powered and TIGHTER
    # (+-0.08). The closed forms are derived, not fitted:
    #   graded    SNR = sqrt(d/(t+1))
    #   binarised SNR = d*P(W_t=0)/sqrt(d),  P(W_t=0) = C(t,t/2)/2^t  (-> sqrt(2/(pi t)))
    t_lv, n_lv = 64, 400
    lvl = {}
    for name, binar in (("graded", False), ("binarised", True)):
        vals = [snr_curve(rng.choice([-1.0, 1.0], size=d),
                          [rng.choice([-1.0, 1.0], size=d) for _ in range(t_lv)],
                          [t_lv], probes, binar)[0] for _ in range(n_lv)]
        lvl[name] = float(np.mean(vals))
    p0 = math.comb(t_lv, t_lv // 2) / 2.0 ** t_lv
    der = {"graded": math.sqrt(d / (t_lv + 1.0)), "binarised": d * p0 / math.sqrt(d)}
    for name in ("graded", "binarised"):
        rel = abs(lvl[name] - der[name]) / der[name]
        log("  selftest level %-9s measured %.4f vs derived %.4f (rel %.3f)"
            % (name, lvl[name], der[name], rel))
        if rel > 0.08:
            log("  SELFTEST FAIL 3%s: %s level off closed form by %.1f%%"
                % ("a" if name == "graded" else "b", name, 100 * rel)); ok = False
    ratio = lvl["binarised"] / lvl["graded"]
    der_ratio = der["binarised"] / der["graded"]
    log("  selftest level ratio %.4f vs derived %.4f (asymptote sqrt(2/pi)=%.4f)"
        % (ratio, der_ratio, math.sqrt(2.0 / math.pi)))
    if abs(ratio - der_ratio) > 0.08:
        log("  SELFTEST FAIL 3c: level ratio %.4f not within 0.08 of derived %.4f"
            % (ratio, der_ratio)); ok = False

    # 4. DISCRIMINATOR MUST FIRE: a planted exponential must be called exponential.
    tt = np.array(t_grid, dtype=np.float64)
    tt = tt[tt >= FIT_T_MIN]
    planted = np.exp(-tt / 90.0) * (1.0 + 0.01 * rng.standard_normal(tt.size))
    fp = compare_fits(np.tile(tt, 8), np.tile(planted, 8))
    log("  selftest planted-exponential dAIC=%+.1f winner=%s" % (fp["dAIC_exp_minus_pow"],
                                                                 fp["winner"]))
    if fp["winner"] != "exponential":
        log("  SELFTEST FAIL 4: planted exponential not detected -> discriminator is VACUOUS")
        ok = False

    # 5. live context vectors are real, not all-zero / all-identical (content_words digit trap)
    from hdlab.reading_grounding_loop import context_vector_masked
    s1 = "The cathedral in the old city was built by the king in 1290 for the people."
    s2 = "Water boils at 100 degrees and freezes at 0 degrees under normal pressure."
    v1 = context_vector_masked(s1, "city")
    v2 = context_vector_masked(s2, "water")
    if not np.any(v1 != 0) or not np.any(v2 != 0):
        log("  SELFTEST FAIL 5a: a live context vector is ALL ZERO"); ok = False
    if np.array_equal(v1, v2):
        log("  SELFTEST FAIL 5b: two different sentences gave identical vectors"); ok = False
    log("  selftest live ctx vectors ok (nonzero frac %.3f / %.3f, cos %.4f)"
        % (float(np.mean(v1 != 0)), float(np.mean(v2 != 0)),
           float(v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2)))))
    log("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return ok


# ------------------------------------------------------------------ assembly

def assemble(out_dir: str, cfg: dict, meta: dict, log) -> bool:
    units = load_units(out_dir)
    expected = sorted(set(uk(r, s) for r in READOUTS for s in STREAMS))
    missing = sorted(set(expected) - set(units))
    if missing:
        log("assembly deferred, %d unit(s) missing: %s" % (len(missing), missing))
        return False
    verdict = classify(units)
    payload = {
        "cell": "exp_forgetting_kernel_signreadout_v1",
        "prereg": "preregs/2026-08-14_forgetting_kernel_signreadout_v1.md",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "meta": meta,
        "REQUIRED_FIELDS": ["verdict", "units", "analytic_prediction", "axis_reconciliation"],
        "analytic_prediction": {
            "graded_slope": -0.5, "binarised_slope": -0.5,
            "binarised_over_graded_level_ratio": math.sqrt(2.0 / math.pi),
            "derivation": "unbounded integrator SNR=sqrt(d/(t+1)); sign() readout gives "
                          "sqrt(d)*sqrt(2/(pi t)) -- same exponent, prefactor sqrt(2/pi)",
        },
        "axis_reconciliation": {
            "primary_axis": "encounters of the tracked lemma == Benna-Fusi 'memories stored at "
                            "this synapse' (_sums[lemma] is a bank of d dedicated accumulators)",
            "reconcilable": True,
            "second_channel": "anchor-dictionary growth; NOT a Benna-Fusi channel (no dictionary, "
                              "no argmax in their model); see channel_b",
        },
        "verdict": verdict,
        "units": units,
        "channel_b": {k: v for k, v in load_units(out_dir).items() if k.startswith("channel_b")},
    }
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))
    log("WROTE %s" % os.path.join(out_dir, "metrics.json"))
    log("VERDICT: %s -- %s" % (verdict["band"], verdict["reason"]))
    return True


def classify(units: dict) -> dict:
    """Apply the PRE-DECLARED bands from the prereg. No band is a tuning target."""
    out = {"per_stream": {}}
    for stream in STREAMS:
        g = units.get(uk("graded", stream))
        b = units.get(uk("binarised", stream))
        if not g or not b:
            continue
        gs, bs = g["fit"]["power_slope"], b["fit"]["power_slope"]
        gw, bw = g["fit"]["winner"], b["fit"]["winner"]
        gci, bci = g["slope_ci"], b["slope_ci"]
        overlap = (gci.get("ci_lo") is not None and bci.get("ci_lo") is not None
                   and gci["ci_lo"] <= bci["ci_hi"] and bci["ci_lo"] <= gci["ci_hi"])
        if gw == "power" and bw != "power":
            band = "CONFIRMS"
            reason = "graded fits power law (dAIC %+.1f), binarised does not (%s, dAIC %+.1f)" % (
                g["fit"]["dAIC_exp_minus_pow"], bw, b["fit"]["dAIC_exp_minus_pow"])
        elif gw == "power" and bw == "power" and overlap and abs(gs - bs) < 0.10:
            band = "REFUTES"
            reason = ("both arms fit power law, slope CIs overlap, |dslope|=%.4f < 0.10 -- "
                      "the sign() is NOT the cause" % abs(gs - bs))
        elif gw == "exponential" and bw == "exponential":
            band = "REFUTES"
            reason = "both arms fit exponential -- the sign() is NOT the cause"
        else:
            band = "INCONCLUSIVE"
            reason = "graded=%s (slope %.4f), binarised=%s (slope %.4f), |dslope|=%.4f" % (
                gw, gs, bw, bs, abs(gs - bs))
        out["per_stream"][stream] = {
            "band": band, "reason": reason,
            "graded_slope": gs, "graded_ci": [gci.get("ci_lo"), gci.get("ci_hi")],
            "graded_dAIC": g["fit"]["dAIC_exp_minus_pow"], "graded_winner": gw,
            "binarised_slope": bs, "binarised_ci": [bci.get("ci_lo"), bci.get("ci_hi")],
            "binarised_dAIC": b["fit"]["dAIC_exp_minus_pow"], "binarised_winner": bw,
            "slope_delta": gs - bs,
        }
    # PRE-DECLARED control band: does shuffled ingest order change the shape?
    ctrl = {}
    for r in READOUTS:
        rr = units.get(uk(r, "real"))
        so = units.get(uk(r, "scram_order"))
        if rr and so:
            dd = abs(rr["fit"]["power_slope"] - so["fit"]["power_slope"])
            ctrl[r] = {"slope_real": rr["fit"]["power_slope"],
                       "slope_scram_order": so["fit"]["power_slope"],
                       "abs_delta": dd,
                       "shape_unchanged_by_order": bool(dd < 0.05),
                       "meaning": ("curve is NOT measuring consolidation -- the accumulator is "
                                   "order-invariant" if dd < 0.05 else
                                   "order matters: some temporal structure is present")}
    out["scramble_control"] = ctrl
    prim = out["per_stream"].get("real", {})
    out["band"] = prim.get("band", "INCONCLUSIVE")
    out["reason"] = "PRIMARY (stream=real): " + prim.get("reason", "real stream missing")
    return out


# ------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", choices=READOUTS, default=None)
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assemble-only", action="store_true")
    ap.add_argument("--timeout", type=int, default=2400)
    args = ap.parse_args()

    # THE FLAG IS SET HERE, BEFORE hdlab IS IMPORTED. Never as an inline shell prefix.
    if args.readout is not None:
        os.environ["HD_GRADED_COMPARATOR"] = "1" if args.readout == "graded" else "0"

    def log(msg):
        print("[fk] %s" % msg, flush=True)

    if args.self_test:
        return 0 if self_test(log) else 1

    if args.readout is None and not args.assemble_only:
        log("--readout is required (or --assemble-only / --self-test)")
        return 2

    cfg = CFG[args.mode]
    out_dir = os.path.join(REPO, "data", "exp_forgetting_kernel_signreadout_v1"
                           + ("_smoke" if args.mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)

    from hdlab.reading_grounding_loop import (ConceptSpace, GRADED_COMPARATOR,
                                              content_lemmas, context_vector_masked)
    from hdlab.grounding_acquisition_loop import D as LIVE_D

    meta = {"mode": args.mode, "cfg": cfg, "live_d": int(LIVE_D), "corpus": CORPUS,
            "timeout_s": args.timeout,
            "progress_logging": "print(..., flush=True) per unit and per corpus phase"}

    if args.assemble_only:
        return 0 if assemble(out_dir, cfg, meta, log) else 3

    want = "1" if args.readout == "graded" else "0"
    assert os.environ["HD_GRADED_COMPARATOR"] == want
    assert GRADED_COMPARATOR == (args.readout == "graded"), \
        "flag did not take: hdlab was imported before the env var was set"
    log("readout=%s GRADED_COMPARATOR=%s d=%d mode=%s" % (args.readout, GRADED_COMPARATOR,
                                                          LIVE_D, args.mode))

    done = completed_units(out_dir)
    todo = [s for s in STREAMS if uk(args.readout, s) not in done]
    need_corpus = any(s != "synth" for s in todo) or (
        unit_key("channel_b", args.readout) not in done)
    corpus = None
    if need_corpus:
        corpus = build_corpus_pools(content_lemmas, context_vector_masked, cfg, log)
        log("tracked lemmas (%d): %s" % (len(corpus["tracked"]), corpus["tracked"][:12]))

    for stream in STREAMS:
        k = uk(args.readout, stream)
        if k in done:
            log("skip completed unit %s" % k)
            continue
        t0 = time.time()
        res = run_unit(args.readout, stream, cfg, corpus, int(LIVE_D), 20260814, log)
        res["elapsed_s"] = round(time.time() - t0, 2)
        record_unit(out_dir, k, res)

    kb = unit_key("channel_b", args.readout)
    if kb not in done and corpus is not None:
        record_unit(out_dir, kb, run_channel_b(args.readout, cfg, corpus, ConceptSpace, log))

    assemble(out_dir, cfg, meta, log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
