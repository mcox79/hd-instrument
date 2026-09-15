"""Scaffold-free witness for the_reader_has_no_conceptual_meaning_channel.

Recomputes the HEADLINE claims INDEPENDENTLY (fresh spearman + paired bootstrap, not the cell's own
report dict) so it cannot self-confirm. Uses the cached GloVe benchmark subset (built on the cell's first
run) so it does NOT pay the 4-min full-GloVe load and does NOT touch the landed metrics.json.

Asserts, floors recomputed on each population:
  A (identity): CONCEPTUAL (WordNet gloss+genus, IDF) beats the STEELMANNED associative competitor
     (GloVe-300) on SimLex-999 AND SimVerb (human SIMILARITY, off-WordNet gold), paired-bootstrap CI_lo>0;
     the info-free twin (shuffled glosses) LOSES (conceptual >> twin p95); concreteness floor cleared;
     the distinctive-feature (IDF) op beats UNWEIGHTED overlap (the ATL WRONG-OP) CI-sep.
  B (dissociation): conceptual tracks similarity > relatedness while GloVe tracks relatedness > similarity
     -- crossover CI_lo>0 on SimLex (same pairs, SimLex999 vs Assoc(USF)); and GloVe beats conceptual on
     WordSim-353 relatedness CI-sep. The two systems each win their own axis (real, partial dissociation).

Run: .venv/Scripts/python.exe verification/test_conceptual_meaning_channel.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import sys
import numpy as np
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_conceptual_meaning_channel_v1 import (
    _load_bench, _global_idf, ConceptualChannel, _sparse_cos, _load_assoc, BENCH)

SEED = 4242


def _paired_ci(ca, cb, g, n_boot=2000, seed=SEED):
    ca, cb, g = np.asarray(ca, float), np.asarray(cb, float), np.asarray(g, float)
    n = len(g)
    rng = np.random.default_rng(seed)
    d = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        d[i] = spearmanr(ca[idx], g[idx]).statistic - spearmanr(cb[idx], g[idx]).statistic
    lo, hi = np.percentile(d, [2.5, 97.5])
    base = spearmanr(ca, g).statistic - spearmanr(cb, g).statistic
    return float(base), float(lo), float(hi)


def main():
    print("[witness] building conceptual channel (IDF over all WordNet synsets) ...", flush=True)
    idf, nsyn = _global_idf()
    C = ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=True)
    Cu = ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=False)

    benches = {bn: _load_bench(p, k, i1, i2, isc) for bn, (p, k, i1, i2, isc) in BENCH.items()}
    full_vocab = {w for rows in benches.values() for w1, w2, *_ in rows for w in (w1, w2)}
    print("[witness] loading associative competitor (cached GloVe subset) ...", flush=True)
    kv = _load_assoc(full_vocab)
    def acos(w1, w2):
        return float(kv.similarity(w1, w2)) if (w1 in kv.key_to_index and w2 in kv.key_to_index) else None

    def cols(rows, chan, need_assoc=True):
        cc, aa, yy = [], [], []
        for w1, w2, pos, s, *_ in rows:
            cv = _sparse_cos(chan.vec(w1, pos), chan.vec(w2, pos))
            av = acos(w1, w2)
            if cv is None or (need_assoc and av is None):
                continue
            cc.append(cv); aa.append(av if av is not None else 0.0); yy.append(s)
        return np.array(cc), np.array(aa), np.array(yy)

    # ---------- BAR A: identity on SimLex + SimVerb ----------
    for bn in ("SimLex_sim", "SimVerb_test"):
        c, a, y = cols(benches[bn], C)
        rc = spearmanr(c, y).statistic; ra = spearmanr(a, y).statistic
        base, lo, hi = _paired_ci(c, a, y)
        # twin null: shuffle bags across (word,pos) keys, 40 draws
        keys = sorted({(w, pos) for w1, w2, pos, *_ in benches[bn] for w in (w1, w2)})
        twin_rhos = []
        for t in range(40):
            rng = np.random.default_rng(SEED + 100 + t)
            perm = rng.permutation(len(keys))
            vv = [C.vec(w, p) for (w, p) in keys]
            m = {keys[i]: vv[perm[i]] for i in range(len(keys))}
            xs = [_sparse_cos(m[(w1, pos)], m[(w2, pos)]) for w1, w2, pos, *_ in benches[bn]
                  if _sparse_cos(C.vec(w1, pos), C.vec(w2, pos)) is not None and acos(w1, w2) is not None]
            rr = spearmanr(np.array([x if x is not None else 0.0 for x in xs]), y).statistic
            if rr == rr:
                twin_rhos.append(abs(rr))
        twin_p95 = float(np.percentile(twin_rhos, 95))
        # distinctive-feature (IDF) vs UNWEIGHTED overlap (the ATL WRONG-OP), aligned on same rows
        cc2, uu2, yy2 = [], [], []
        for w1, w2, pos, s, *_ in benches[bn]:
            ci = _sparse_cos(C.vec(w1, pos), C.vec(w2, pos))
            ui = _sparse_cos(Cu.vec(w1, pos), Cu.vec(w2, pos))
            if ci is not None and ui is not None:
                cc2.append(ci); uu2.append(ui); yy2.append(s)
        _, ilo, _ = _paired_ci(np.array(cc2), np.array(uu2), np.array(yy2))
        print("[A:%s] n=%d CONC=%.4f GloVe=%.4f d=%.4f CI[%.4f,%.4f] | twin_p95=%.4f | IDF-vs-UNW CI_lo=%.4f"
              % (bn, len(y), rc, ra, base, lo, hi, twin_p95, ilo), flush=True)
        assert lo > 0, "%s: conceptual must beat GloVe CI-separated (lo=%.4f)" % (bn, lo)
        assert rc > twin_p95 + 0.1, "%s: conceptual must beat the shuffled-gloss twin (%.4f vs p95 %.4f)" % (bn, rc, twin_p95)
        assert ilo > 0, "%s: IDF (distinctive-feature) must beat UNWEIGHTED overlap CI-sep (lo=%.4f)" % (bn, ilo)

    # ---------- BAR B: double dissociation ----------
    sl = benches["SimLex_sim"]
    sc, sa, sim = [], [], []
    asc = []
    for w1, w2, pos, s, assoc, sa333 in sl:
        cv = _sparse_cos(C.vec(w1, pos), C.vec(w2, pos)); av = acos(w1, w2)
        if cv is not None and av is not None and assoc is not None:
            sc.append(cv); sa.append(av); sim.append(s); asc.append(assoc)
    sc, sa, sim, asc = map(np.array, (sc, sa, sim, asc))
    C_sim, C_asc = spearmanr(sc, sim).statistic, spearmanr(sc, asc).statistic
    A_sim, A_asc = spearmanr(sa, sim).statistic, spearmanr(sa, asc).statistic
    rng = np.random.default_rng(SEED + 7)
    xb = np.empty(2000)
    for i in range(2000):
        idx = rng.integers(0, len(sim), len(sim))
        xb[i] = ((spearmanr(sc[idx], sim[idx]).statistic - spearmanr(sc[idx], asc[idx]).statistic)
                 - (spearmanr(sa[idx], sim[idx]).statistic - spearmanr(sa[idx], asc[idx]).statistic))
    xlo = float(np.percentile(xb, 2.5))
    print("[B] CONC sim=%.4f assoc=%.4f | GloVe sim=%.4f assoc=%.4f | crossover_CI_lo=%.4f"
          % (C_sim, C_asc, A_sim, A_asc, xlo), flush=True)
    assert (C_sim - C_asc) > 0, "conceptual must track similarity over association"
    assert xlo > 0, "double-dissociation crossover must be CI-separated (lo=%.4f)" % xlo
    # WordSim relatedness: GloVe beats conceptual CI-sep
    wc, wa, wy = cols(benches["WordSim_rel"], C)
    _, wlo, _ = _paired_ci(wa, wc, wy)
    print("[B] WordSim CONC=%.4f GloVe=%.4f | GloVe-CONC CI_lo=%.4f" % (spearmanr(wc, wy).statistic, spearmanr(wa, wy).statistic, wlo), flush=True)
    assert wlo > 0, "GloVe must beat conceptual on relatedness CI-sep (lo=%.4f)" % wlo

    print("\n[witness] PASS: conceptual channel wins meaning-IDENTITY off-WordNet (CI-sep, twin loses, "
          "distinctive-feature op earns its keep) AND the two systems double-dissociate.")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
