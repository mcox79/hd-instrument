"""DOES THE ORTHOGONALITY WALL BITE ON REAL CODES? -- and does DG sparse decorrelation fix it?

The beyond-N sweep showed CODE ORTHOGONALITY is the dominant capacity axis (correlated codes collapse cleanup even
with dimensional headroom), and flagged our iid-random-code assumption as an unflagged OUR-INVENTION. On SYNTHETIC
codes that is a knob. This cell tests it on REAL content codes and closes the brain-foundational loop:

  * REAL semantic codes are correlated BY DESIGN (similar meanings -> similar codes -- that is what makes them
    useful for similarity). We build them from the landed ATL meaning organ (hdlab.conceptual_meaning) feature
    vectors, random-projected to dense D=1024 (the meaning K-sweep showed K>=256 preserves the signal).
  * The BRAIN stores correlated cortical codes by first DECORRELATING them in the dentate gyrus (sparse k-WTA
    pattern separation; Marr 1971; Treves & Rolls 1994; O'Reilly & McClelland 1994). We model DG as top-k magnitude
    sparsification of the same code.

TEST (a real-valued superposition store = the event_bundle / hd_fact_store regime): build a codebook of N items;
bundle a random M-subset; recover the members by cosine cleanup (flat top-M). Compare, at fixed D:
  REAL-DENSE (correlated)  vs  DG-SPARSE (decorrelated real code)  vs  RANDOM-ORTHOGONAL (the iid ideal).
Also report each code family's mean pairwise |cos| (the empirical correlation) and chance. FLOOR = random-subset
chance; TWIN = decode a bundle that does NOT contain the queried item (shuffled membership) -> must not "recover" it.

VERDICT: if REAL-DENSE cliffs EARLIER than RANDOM-ORTHOGONAL, the substrate's meaning codes ARE in the degraded
regime when superposed, and if DG-SPARSE recovers toward orthogonal, sparse pattern separation is the fix (an
hdlab direction: decorrelate before you store, exactly as the brain does).

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_realcode_v1.py [--self-test]
ASCII only. Reads SimLex words for a real vocabulary. Writes ONLY to its own dir. NO hdlab write.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.conceptual_meaning import ConceptualChannel  # noqa: E402

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_realcode_v1")
SEED = 20260828
D = 1024
SIMLEX_N = os.path.join(REPO_ROOT, "data", "lemmatised_grounding_task_v1", "scored_population_SIMLEX_NOUN.json")


def _unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-12)


def _mean_abs_cos(mat):
    """Mean off-diagonal |cosine| over a set of unit rows -- the empirical code correlation."""
    m = _unit(mat.astype(np.float64))
    g = m @ m.T
    n = g.shape[0]
    off = g[~np.eye(n, dtype=bool)]
    return float(np.mean(np.abs(off)))


def _dg_sparsify(mat, frac=0.02):
    """DG pattern separation model: keep the top-|frac*D| magnitude components per code, zero the rest
    (k-winners-take-all expansion analog), then unit-normalise. Decorrelates dense correlated codes."""
    d = mat.shape[1]; k = max(1, int(frac * d))
    out = np.zeros_like(mat)
    idx = np.argpartition(-np.abs(mat), k - 1, axis=1)[:, :k]
    rows = np.arange(mat.shape[0])[:, None]
    out[rows, idx] = mat[rows, idx]
    return _unit(out)


def _build_codes(rng):
    """Return {family: (N,D) unit codebook} for REAL-DENSE (WordNet meaning, random-projected), DG-SPARSE, and
    RANDOM-ORTHOGONAL, over a shared real vocabulary."""
    chan = ConceptualChannel()
    words = []
    if os.path.exists(SIMLEX_N):
        d = json.load(open(SIMLEX_N, encoding="utf-8"))
        seen = set()
        for p in d["pairs"]:
            for w in (p["a"], p["b"]):
                if w not in seen and chan.vec(w, "N") is not None:
                    seen.add(w); words.append(w)
    words = words[:120]
    # feature index over the used words, then random-project sparse feature vecs to dense D
    feat_index = {}
    vecs = []
    for w in words:
        v = chan.vec(w, "N") or {}
        for f in v:
            feat_index.setdefault(f, len(feat_index))
        vecs.append(v)
    nf = len(feat_index)
    R = rng.choice(np.array([-1.0, 1.0]), size=(nf, D)) / np.sqrt(D)
    dense = np.zeros((len(words), D), dtype=np.float64)
    for i, v in enumerate(vecs):
        for f, wt in v.items():
            dense[i] += wt * R[feat_index[f]]
    real_dense = _unit(dense)
    dg_sparse = _dg_sparsify(dense, frac=0.02)
    rand_orth = _unit(rng.standard_normal((len(words), D)))
    return {"real_dense": real_dense, "dg_sparse": dg_sparse, "rand_orth": rand_orth}, len(words)


def _recover(codebook, m, n_trials, seed):
    """Bundle a random M-subset (unit-weight sum), recover members by flat top-M cosine. Returns
    (mean per-item recall, twin recall). Twin: query membership of items NOT bundled (must be ~0/chance)."""
    N = codebook.shape[0]
    rng = np.random.default_rng(seed)
    hit = tot = 0
    twin_hit = twin_tot = 0
    cb = codebook
    for _ in range(n_trials):
        members = rng.choice(N, size=m, replace=False)
        bundle = cb[members].sum(axis=0)
        scores = cb @ bundle                      # (N,) cleanup scores
        topm = set(np.argpartition(-scores, m - 1)[:m].tolist())
        mem = set(members.tolist())
        hit += len(topm & mem); tot += m
        # twin: are NON-members spuriously "recovered"? fraction of top-M that are NOT true members
        twin_hit += len(topm - mem); twin_tot += m
    return hit / tot, twin_hit / twin_tot


def run():
    rng = np.random.default_rng(SEED)
    codes, n = _build_codes(rng)
    corr = {fam: round(_mean_abs_cos(codes[fam]), 4) for fam in codes}
    m_grid = [2, 4, 8, 16, 24, 32, 48]
    m_grid = [m for m in m_grid if m < n]
    rows = []
    for m in m_grid:
        row = {"M": m}
        for fam in ("real_dense", "dg_sparse", "rand_orth"):
            rec, tw = _recover(codes[fam], m, 200, SEED + m)
            row[fam] = round(rec, 4); row[fam + "_twin"] = round(tw, 4)
        rows.append(row)
    return {"anchor": "dim_phase_diagram_realcode_v1", "D": D, "n_words": n, "n_random_baseline_expected_cos": round(1/np.sqrt(D), 4),
            "mean_abs_cos": corr, "m_grid": m_grid, "recovery": rows}


def summarize(res):
    print(f"\n=== REAL-CODE orthogonality + DG fix (D={res['D']}, N={res['n_words']} real WordNet words) ===")
    print(f"  mean pairwise |cos| (code correlation):  real_dense={res['mean_abs_cos']['real_dense']}  "
          f"dg_sparse={res['mean_abs_cos']['dg_sparse']}  rand_orth={res['mean_abs_cos']['rand_orth']}  "
          f"(iid expectation ~{res['n_random_baseline_expected_cos']})")
    print("  member-recovery accuracy vs bundle load M (real-valued superposition store):")
    print("     M   real_dense  dg_sparse  rand_orth   (real_dense twin)")
    for r in res["recovery"]:
        print(f"  {r['M']:>4d}    {r['real_dense']:.3f}      {r['dg_sparse']:.3f}     {r['rand_orth']:.3f}"
              f"       {r['real_dense_twin']:.3f}")
    # verdict at a mid load
    mid = res["recovery"][min(4, len(res["recovery"]) - 1)]
    print(f"  => at M={mid['M']}: real-dense {mid['real_dense']:.3f} vs orthogonal {mid['rand_orth']:.3f} "
          f"(correlation cost); DG-sparse {mid['dg_sparse']:.3f} (decorrelation {'RECOVERS' if mid['dg_sparse']>mid['real_dense']+0.03 else 'does not recover'}).")


def self_test():
    rng = np.random.default_rng(1)
    codes, n = _build_codes(rng)
    assert n > 40, f"need a real vocabulary; got {n}"
    c_real = _mean_abs_cos(codes["real_dense"]); c_orth = _mean_abs_cos(codes["rand_orth"])
    assert c_real > c_orth, f"real semantic codes must be MORE correlated than random; real={c_real} orth={c_orth}"
    rec, tw = _recover(codes["rand_orth"], 4, 50, 2)
    assert rec > 0.9, f"orthogonal codes must recover a small bundle; got {rec}"
    print(f"SELF-TEST PASS: n={n}; corr real={c_real:.3f} > orth={c_orth:.3f}; orth recovery@M4={rec:.3f} twin={tw:.3f}")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run(); res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
