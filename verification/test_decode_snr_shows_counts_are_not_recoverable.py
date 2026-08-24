"""Scaffold-free witness for `the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`.

Reproduces, from the landed artifact and a live spot-check, the headline that the co-occurrence
counts PPMI needs CANNOT be recovered from the substrate's stored `_sums` bundle at realistic
accumulation -- and that this is an information limit of the 256-dim random projection, not a weak
decoder. Prints the CI half-widths and the info-free null p95/max beside every margin (bar item 6),
then asserts the qualitative claims. Exit 0 == all witnesses pass.

Run: .venv/Scripts/python.exe verification/test_decode_snr_shows_counts_are_not_recoverable.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

METRICS = os.path.join(REPO, "data", "exp_decode_snr_real_store_field_v1", "metrics.json")
POP = os.path.join(REPO, "data", "exp_decode_snr_real_store_field_v1", "scored_population.json")
D = 256
BOOT_SEED = 20260824
N_BOOT = 5000


def _boot_median_ci(vals, seed=BOOT_SEED, n=N_BOOT):
    v = np.array([x for x in vals if np.isfinite(x)], dtype=float)
    if len(v) < 3:
        return (float("nan"), float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    meds = np.array([np.median(rng.choice(v, size=len(v), replace=True)) for _ in range(n)])
    return float(np.median(v)), float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5))


def test_live_encoder_identity_bit_exact():
    """The field this cell decodes IS the live field: reconstruct_bipolar(counts) == the live
    context_vector_masked, byte-for-byte, on real sentences."""
    from hdlab.reading_grounding_loop import (
        content_words, context_vector_masked, normalize_lemma, symbol_vector,
    )
    from collections import Counter
    import numpy as np
    z = np.load(os.path.join(REPO, "scratch", "cue_information_audit_v1", "buckets_full.npz"),
                allow_pickle=True)
    sents = [str(s) for s in z["sents"]]
    max_err = 0.0
    n = 0
    for a in ("amazon", "river", "planet"):
        cnt = 0
        for s in sents:
            if a in s and cnt < 5:
                p = Counter(w for w in content_words(s) if normalize_lemma(w) != a)
                if sum(p.values()) == 0:
                    continue
                lhs = np.zeros(D)
                for w, c in p.items():
                    lhs += float(c) * symbol_vector(w, D)
                rhs = context_vector_masked(s, a, graded=True)
                max_err = max(max_err, float(np.max(np.abs(lhs - rhs))))
                n += 1
                cnt += 1
    assert n >= 5, "identity spot-check found too few sentences (n=%d)" % n
    assert max_err == 0.0, "encoder identity DRIFTED: max_abs_err=%g" % max_err
    return {"max_abs_error": max_err, "n_checked": n}


def _load():
    d = json.load(open(METRICS))
    rows = json.load(open(POP))["rows"]
    return d, rows


def test_decoder_works_at_tiny_accumulation_positive_control():
    """POSITIVE CONTROL: at tiny accumulation the decoder recovers count-1 words far above the
    info-free null, or the whole degradation claim is void."""
    d, rows = _load()
    small = [r["sep_count1_sd"] for r in rows if r["k_sents"] <= 2]
    med, lo, hi = _boot_median_ci(small)
    twin = np.array([r["shuffled_sep_count1_sd"] for r in rows if np.isfinite(r["shuffled_sep_count1_sd"])])
    null_p95 = float(np.percentile(twin, 95)); null_max = float(np.max(twin))
    print("[positive control] small-k count-1 separation median=%.2f CI[%.2f,%.2f] hw=%.2f "
          "vs info-free null p95=%.3f max=%.3f" % (med, lo, hi, (hi - lo) / 2, null_p95, null_max))
    assert lo > 3.0, "positive control too weak (CI_lo=%.2f)" % lo
    assert lo > null_max, "positive control does not clear the info-free null MAX"
    return {"median": med, "ci": [lo, hi]}


def test_rare_counts_are_at_noise_at_realistic_accumulation():
    """THE HEADLINE: at realistic accumulation (>=256 distinct context words) a count-1 word barely
    separates from an absent word, and rare-count decode correlation collapses to near zero -- the
    entries PPMI leans on hardest are exactly the ones that drown."""
    d, rows = _load()
    large = [r for r in rows if r["n_distinct"] >= 256]
    sep = [r["sep_count1_sd"] for r in large]
    rare_r = [r["pearson_rare"] for r in large]
    sep_med, sep_lo, sep_hi = _boot_median_ci(sep)
    r_med, r_lo, r_hi = _boot_median_ci(rare_r)
    twin = np.array([r["shuffled_sep_count1_sd"] for r in rows if np.isfinite(r["shuffled_sep_count1_sd"])])
    null_p95 = float(np.percentile(twin, 95)); null_max = float(np.max(twin))
    print("[realistic >=256 distinct] count-1 sep median=%.3f CI[%.3f,%.3f] hw=%.3f "
          "(null p95=%.3f max=%.3f)" % (sep_med, sep_lo, sep_hi, (sep_hi - sep_lo) / 2, null_p95, null_max))
    print("[realistic >=256 distinct] rare-count decode r median=%.3f CI[%.3f,%.3f] hw=%.3f"
          % (r_med, r_lo, r_hi, (r_hi - r_lo) / 2))
    # the collapse is the finding: realistic separation is a small fraction of the positive control
    small = [r["sep_count1_sd"] for r in rows if r["k_sents"] <= 2]
    pos_med = float(np.median([x for x in small if np.isfinite(x)]))
    assert sep_med < 0.15 * pos_med, "no collapse: realistic=%.3f vs positive=%.3f" % (sep_med, pos_med)
    assert r_hi < 0.30, "rare-count recovery is NOT at noise at realistic sizes (CI_hi=%.3f)" % r_hi
    return {"sep_med": sep_med, "rare_r_med": r_med}


def test_failure_is_the_random_projection_noise_model_not_a_bug():
    """The measured absent-word noise std equals the analytic crosstalk std ||P_a||/sqrt(d) to within
    a couple percent -- so the failure is a deterministic property of the random projection, not an
    implementation defect."""
    d, rows = _load()
    npred = np.array([r["noise_pred_sd"] for r in rows], float)
    nmeas = np.array([r["noise_meas_sd"] for r in rows], float)
    ok = np.isfinite(npred) & np.isfinite(nmeas) & (npred > 0)
    ratio = float(np.median(nmeas[ok] / npred[ok]))
    r = float(np.corrcoef(npred[ok], nmeas[ok])[0, 1])
    print("[noise model] median measured/predicted=%.4f  pearson(pred,measured)=%.4f" % (ratio, r))
    assert 0.9 < ratio < 1.1, "noise model off (ratio=%.3f)" % ratio
    assert r > 0.95, "noise model does not explain the spread (r=%.3f)" % r
    return {"ratio": ratio, "r": r}


def test_even_the_optimal_linear_decoder_hits_the_same_cliff_at_support_equals_d():
    """The strongest linear decoder -- oracle-support least-squares (TOLD which words co-occur) --
    recovers counts EXACTLY when support<=d and falls to noise when support>d. No decoder beats the
    projection width; the naive matched filter and the optimum share the information limit."""
    d, rows = _load()
    by = d["STRONGER_DECODER_LSQ"]["by_support_over_d"]
    over = d["STRONGER_DECODER_LSQ"]["median_pearson_rare_overdetermined_support_le_d"]
    under = d["STRONGER_DECODER_LSQ"]["median_pearson_rare_underdetermined_support_gt_d"]
    print("[oracle-support lstsq] support<=d rare-r=%.3f ; support>d rare-r=%.3f" % (over, under))
    for k, v in by.items():
        print("   support/d %-9s n=%-4d rare-r=%.3f decoy_falsepos_std=%.3g"
              % (k, v["n"], v["median_pearson_rare_lsq"], v["median_decoy_falsepos_std"]))
    assert over > 0.99, "overdetermined recovery should be near-exact (got %.3f)" % over
    assert under < 0.40, "underdetermined recovery should be near-noise (got %.3f)" % under
    return {"over": over, "under": under}


def test_info_free_twin_collapses_everywhere():
    """The shuffled-code info-free twin (same estimator, scrambled word<->code map) sits at ~0 at
    every accumulation size -- the small-accumulation signal is real information, not an artifact."""
    d, rows = _load()
    twin = np.array([r["shuffled_sep_count1_sd"] for r in rows if np.isfinite(r["shuffled_sep_count1_sd"])])
    print("[info-free twin] median=%.3f p95=%.3f max=%.3f" % (np.median(twin), np.percentile(twin, 95), twin.max()))
    assert abs(float(np.median(twin))) < 0.15, "info-free twin is not ~0 (median=%.3f)" % np.median(twin)
    return {"median": float(np.median(twin))}


def test_frequent_anchors_are_the_least_recoverable():
    """The inverse relationship that makes this fatal for the intended use: the anchors with the MOST
    distinct context words (the frequent words you most need a distributional vector for) are exactly
    the ones over the recovery limit."""
    d, rows = _load()
    dist = d["REALISTIC_ACCUMULATION_DISTRIBUTION"]
    print("[accumulation] distinct-context-words median=%.0f p90=%.0f max=%.0f ; fraction over d=%.3f"
          % (dist["n_distinct_at_max_k_median"], dist["n_distinct_at_max_k_p90"],
             dist["n_distinct_at_max_k_max"], dist["fraction_anchors_over_d"]))
    # correlation of corpus frequency with distinct-context-words, over anchors
    from collections import defaultdict
    mx = {}
    for r in rows:
        a = r["anchor"]
        if a not in mx or r["k_sents"] > mx[a]["k_sents"]:
            mx[a] = r
    cc = np.array([mx[a]["corpus_count"] for a in mx], float)
    nd = np.array([mx[a]["n_distinct"] for a in mx], float)
    rho = float(np.corrcoef(np.argsort(np.argsort(cc)), np.argsort(np.argsort(nd)))[0, 1])
    print("[inverse relationship] Spearman(corpus_frequency, distinct_context_words)=%.3f" % rho)
    assert dist["fraction_anchors_over_d"] > 0.0
    assert rho > 0.5, "frequency should track accumulation size (rho=%.3f)" % rho
    return {"rho": rho}


def main():
    tests = [
        test_live_encoder_identity_bit_exact,
        test_decoder_works_at_tiny_accumulation_positive_control,
        test_rare_counts_are_at_noise_at_realistic_accumulation,
        test_failure_is_the_random_projection_noise_model_not_a_bug,
        test_even_the_optimal_linear_decoder_hits_the_same_cliff_at_support_equals_d,
        test_info_free_twin_collapses_everywhere,
        test_frequent_anchors_are_the_least_recoverable,
    ]
    n_pass = 0
    for t in tests:
        try:
            t()
            print("PASS  %s" % t.__name__)
            n_pass += 1
        except Exception as e:
            print("FAIL  %s -> %s" % (t.__name__, e))
    print("\n%d/%d WITNESSES PASSED" % (n_pass, len(tests)))
    return 0 if n_pass == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
