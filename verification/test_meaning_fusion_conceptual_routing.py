"""Witness for the CONCEPTUAL IDENTITY channel wired into hdlab/meaning_fusion.py (2026-08-30).

Owner-directed landing: the reader's general meaning read-out (meaning_fusion) had ONLY the
associative/relatedness system (reading+grounded z-fusion, validated on WordSim-353). This wires in
the ATL conceptual identity hub (hdlab.conceptual_meaning) as an OPT-IN, DEMAND-ROUTED channel so the
reader gains the second, dissociable meaning system it lacked -- WITHOUT pooling the two (which would
destroy both). This witness recomputes from source (SimLex-999 + WordSim-353), scaffold-free:

  (1) REGRESSION -- the default (conceptual OFF) object is byte-identical: the data-free self_test
      (which includes routing logic + the byte-identical invariant) passes.
  (2) WIRING FIDELITY -- mf.meaning(w1,w2,demand='similarity') routes to and EQUALS the conceptual
      channel's own similarity(), exactly, on real pairs (the wiring dispatches faithfully).
  (3) THE DOUBLE DISSOCIATION IS PRESERVED BY ROUTING (the owner's explicit ask), lower-bounded:
        * on SimLex (gold=SIMILARITY): the similarity-demand route (conceptual) BEATS the
          relatedness-demand route (associative), paired-bootstrap CI-separated -- the identity WIN;
        * on WordSim (gold=RELATEDNESS): the similarity-demand route (conceptual) does NOT beat the
          relatedness-demand route (associative) CI-separated -- the similarity channel is NOT a
          better relatedness read-out, so pooling it into the relatedness pool would only drag that
          read-out toward the similarity signal for no relatedness gain. This is why routing (keep the
          channels separate, SELECT by demand) is correct, not pooling.
  (4) TWIN -- an info-free shuffled-similarity twin LOSES on SimLex (the ranking carries real signal).

The associative comparator here is the GROUNDED spoke ALONE (a cheap static asset). The reading spoke
needs a slow live read; it is the co-occurrence channel that makes the associative side WIN relatedness
outright (the full crossover -- separately proven by the distributional_meaning_channel + conceptual
organ witnesses). With grounded-only the two TIE on WordSim relatedness (conceptual does not win), which
is the honest LOWER bound and already establishes the no-pooling point. The full crossover strengthens
it and is not re-derived here.
ASCII-only, deterministic, CPU-only.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np
from scipy.stats import spearmanr

from hdlab.meaning_fusion import MeaningFusion, self_test
from hdlab.conceptual_meaning import ConceptualChannel, POSMAP
from hdlab.grounded_similarity import grounded_vector
from hdlab.meaning_operation_router import route as mor_route

N_BOOT = 2000
SEED = 20260830
BENCH = {
    "SimLex_sim": ("data/encoder_eval_benchmarks/simlex999.txt", "tsv", 0, 1, 3),
    "WordSim_rel": ("data/encoder_eval_benchmarks/wordsim353_combined.csv", "csv", 0, 1, 2),
}


def _load_bench(path, kind, i1, i2, isc):
    """(w1, w2, pos, score). pos from col 2 for tsv when it is a POSMAP key, else 'N'."""
    rows = []
    with open(os.path.join(_REPO, path), encoding="utf-8") as f:
        f.readline()
        sep = "," if kind == "csv" else "\t"
        for line in f:
            p = line.rstrip("\n").split(sep)
            if len(p) <= max(i1, i2, isc):
                continue
            try:
                w1, w2, sc = p[i1].strip().lower(), p[i2].strip().lower(), float(p[isc])
            except ValueError:
                continue
            pos = p[2].strip() if (kind == "tsv" and len(p) > 2 and p[2].strip() in POSMAP) else "N"
            rows.append((w1, w2, pos, sc))
    return rows


def _boot_rho(x, g, seed):
    x, g = np.asarray(x, float), np.asarray(g, float)
    n = len(g)
    rng = np.random.default_rng(seed)
    b = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        b[i] = spearmanr(x[idx], g[idx]).statistic
    lo, hi = np.percentile(b, [2.5, 97.5])
    return {"rho": round(float(spearmanr(x, g).statistic), 4), "ci_lo": round(float(lo), 4),
            "ci_hi": round(float(hi), 4), "n": n}


def _boot_rho_diff(xa, xb, g, seed):
    """paired bootstrap of rho(xa,g) - rho(xb,g) on the SAME items."""
    a, b, g = np.asarray(xa, float), np.asarray(xb, float), np.asarray(g, float)
    n = len(g)
    rng = np.random.default_rng(seed)
    d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d[i] = spearmanr(a[idx], g[idx]).statistic - spearmanr(b[idx], g[idx]).statistic
    lo, hi = np.percentile(d, [2.5, 97.5])
    base = spearmanr(a, g).statistic - spearmanr(b, g).statistic
    return {"margin": round(float(base), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4)}


def _grounded_only_fusion():
    """A MeaningFusion whose reading spoke is EMPTY -> relatedness route == the grounded spoke (z over
    the batch). Conceptual channel + router wired ON. (Cheap: no live read.)"""
    ref = {"mu_r": 0.0, "sd_r": 1.0, "mu_g": 0.0, "sd_g": 1.0}
    return MeaningFusion(words=[], row_idx={}, phi=np.zeros((0, 0)), grounded_fn=grounded_vector,
                         ref_stats=ref, weights=(0.5, 0.5),
                         conceptual=ConceptualChannel(), router_fn=mor_route)


def _channels_on(mf, rows):
    """Per pair: (similarity-route score, relatedness-route score, gold). Keep pairs BOTH cover."""
    items = [(w1, pos, w2, pos) for (w1, w2, pos, _s) in rows]
    sim = mf.meaning_batch(items, demand="similarity")     # routed -> conceptual (or magnitude)
    rel = mf.meaning_batch(items, demand="relatedness")    # routed -> grounded (empty reading -> fallback)
    xs_s, xs_r, ys, idx = [], [], [], []
    for k, (_w1, _w2, _pos, s) in enumerate(rows):
        if sim[k] is not None and rel[k] is not None:
            xs_s.append(sim[k]); xs_r.append(rel[k]); ys.append(s); idx.append(k)
    return xs_s, xs_r, ys, idx


def test_meaning_fusion_conceptual_routing():
    # (1) REGRESSION: default byte-identical + routing logic.
    ev = self_test()
    assert ev["batch_matches_zfusion_formula"] and ev["oov_policy_ok"] and ev["determinism_ok"]
    assert ev["routing_logic_ok"], "routing logic self-test must pass"
    print("[1] self_test PASS (default byte-identical + routing logic)")

    mf = _grounded_only_fusion()
    conc = ConceptualChannel()
    simlex = _load_bench(*BENCH["SimLex_sim"])
    wordsim = _load_bench(*BENCH["WordSim_rel"])

    # (2) WIRING FIDELITY: mf.meaning(demand='similarity') routes to & equals the conceptual channel.
    checked = 0
    for (w1, w2, pos, _s) in simlex:
        routed = mf.meaning(w1, w2, pos_a=pos, pos_b=pos, demand="similarity")
        # noun/verb/non-gradable-adj pairs route to conceptual; a gradable-adj pair takes the
        # magnitude ruler (unavailable here -> conceptual fallback). Either way it equals conc.similarity.
        direct = conc.similarity(w1, pos, w2, pos)
        if routed is None or direct is None:
            continue
        assert abs(routed - direct) < 1e-12, "wiring must route similarity-demand to the conceptual channel"
        checked += 1
    assert checked >= 300, "too few SimLex pairs checked for wiring fidelity (%d)" % checked
    print("[2] wiring fidelity PASS: meaning(similarity) == conceptual.similarity on %d SimLex pairs" % checked)

    # (3) THE DOUBLE DISSOCIATION, preserved by routing.
    xs_s, xs_r, ys, _ = _channels_on(mf, simlex)
    r_sim_conc = _boot_rho(xs_s, ys, SEED + 1)      # similarity route on SimLex
    r_sim_rel = _boot_rho(xs_r, ys, SEED + 2)       # relatedness route on SimLex
    d_simlex = _boot_rho_diff(xs_s, xs_r, ys, SEED + 3)   # conceptual - associative on SimLex
    print("[3a] SimLex (gold=SIMILARITY) n=%d  similarity-route(conceptual)=%.4f CI[%.4f,%.4f]  "
          "relatedness-route(assoc)=%.4f  conc-assoc=%.4f CI[%.4f,%.4f]"
          % (r_sim_conc["n"], r_sim_conc["rho"], r_sim_conc["ci_lo"], r_sim_conc["ci_hi"],
             r_sim_rel["rho"], d_simlex["margin"], d_simlex["ci_lo"], d_simlex["ci_hi"]))

    xs_s2, xs_r2, ys2, _ = _channels_on(mf, wordsim)
    r_rel_conc = _boot_rho(xs_s2, ys2, SEED + 4)    # similarity route on WordSim
    r_rel_rel = _boot_rho(xs_r2, ys2, SEED + 5)     # relatedness route on WordSim
    d_wordsim = _boot_rho_diff(xs_s2, xs_r2, ys2, SEED + 6)  # conceptual - associative on WordSim
    print("[3b] WordSim (gold=RELATEDNESS) n=%d  relatedness-route(assoc)=%.4f CI[%.4f,%.4f]  "
          "similarity-route(conceptual)=%.4f  conc-assoc=%.4f CI[%.4f,%.4f]"
          % (r_rel_rel["n"], r_rel_rel["rho"], r_rel_rel["ci_lo"], r_rel_rel["ci_hi"],
             r_rel_conc["rho"], d_wordsim["margin"], d_wordsim["ci_lo"], d_wordsim["ci_hi"]))

    assert d_simlex["ci_lo"] > 0, "conceptual must beat associative on SimLex SIMILARITY, CI-separated"
    assert d_wordsim["ci_lo"] <= 0, ("conceptual must NOT CI-separately beat associative on WordSim "
                                     "relatedness -- else it would be a better relatedness read-out and "
                                     "the no-pooling argument would not hold")
    print("[3] DISSOCIATION preserved by routing (lower bound): conceptual WINS similarity CI-sep "
          "(+%.4f), and does NOT win relatedness CI-sep (conc-assoc CI upper %.4f) -> keep channels "
          "separate, route by demand; pooling would only pollute relatedness." % (d_simlex["margin"], d_wordsim["ci_hi"]))

    # (4) TWIN: shuffle the similarity-route scores -> rho collapses (info-free).
    rng = np.random.default_rng(SEED + 7)
    perm = rng.permutation(len(xs_s))
    twin = [xs_s[i] for i in perm]
    r_twin = _boot_rho(twin, ys, SEED + 8)
    assert r_twin["ci_hi"] < r_sim_conc["ci_lo"], "shuffled-similarity twin must LOSE CI-separated"
    print("[4] TWIN PASS: shuffled similarity twin rho=%.4f CI[%.4f,%.4f] < conceptual %.4f (loses CI-sep)"
          % (r_twin["rho"], r_twin["ci_lo"], r_twin["ci_hi"], r_sim_conc["rho"]))

    print("ALL WITNESS CHECKS PASSED")


if __name__ == "__main__":
    test_meaning_fusion_conceptual_routing()
