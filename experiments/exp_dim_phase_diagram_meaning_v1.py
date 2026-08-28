"""DIMENSIONAL PHASE DIAGRAM -- the ATL conceptual meaning channel (hdlab.conceptual_meaning).

This organ is NOT a fixed-D superposition code: it is a SPARSE, EXACT IDF-weighted definitional-feature
cosine over ~tens of thousands of WordNet tokens. There is no bundle, no cross-talk, no sqrt(D/M) capacity
cliff -- so it CANNOT be "under-dimensioned" in the register's sense (it already operates at full feature
width). The honest dimensionality question for a sparse-exact code is different: what is the INTRINSIC
DIMENSIONALITY of its similarity signal -- i.e. to how few dimensions can the meaning vector be compressed
(random projection, Johnson-Lindenstrauss) before its human-similarity correlation degrades?

Why this matters (forward-looking, not a capacity fix for THIS organ): if meaning is ever to be BOUND into
the FHRR register (the convergent-cue composition), it must be projected to the register's dimension D. This
sweep tells strategy the MINIMUM D that preserves the meaning signal -- a phase curve for meaning that is
directly comparable to the register's.

METHOD: on SimLex-999 (noun + verb pairs, human gold), compute Spearman rho between the channel's similarity
and the gold. FULL = the exact sparse cosine (reproduces the landed rho ~0.52). Then random-project each
word's sparse feature vector to K dims (Rademacher sign projection over the union feature vocabulary) and
recompute rho vs gold, for K in a sweep. Floor/twin recomputed: chance rho = 0 (shuffled-gold twin).

VERDICT: UNDER-DIMENSIONED-if-bound if projected rho is still CI-rising at K=1024; SATURATED (intrinsic dim
< 1024) if projected rho reaches the full-exact rho at some K* < 1024.

Run:  .venv/Scripts/python.exe experiments/exp_dim_phase_diagram_meaning_v1.py [--self-test]
ASCII only. Reads data/lemmatised_grounding_task_v1/*.json (SimLex). Writes ONLY to its own dir. NO hdlab write.
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

OUTDIR = os.path.join(REPO_ROOT, "data", "exp_dim_phase_diagram_meaning_v1")
SEED = 20260828
K_GRID = [32, 64, 128, 256, 512, 1024, 2048]
SIMLEX = {
    "N": os.path.join(REPO_ROOT, "data", "lemmatised_grounding_task_v1", "scored_population_SIMLEX_NOUN.json"),
    "V": os.path.join(REPO_ROOT, "data", "lemmatised_grounding_task_v1", "scored_population_SIMLEX_VERB.json"),
}


def _spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    denom = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    return float((rx * ry).sum() / denom) if denom > 1e-12 else 0.0


def _boot_rho(sims, gold, seed, n_boot=2000):
    sims = np.asarray(sims, float); gold = np.asarray(gold, float)
    n = len(sims); r = np.random.default_rng(seed)
    pt = _spearman(sims, gold)
    b = []
    for _ in range(n_boot):
        idx = r.integers(0, n, n)
        b.append(_spearman(sims[idx], gold[idx]))
    return round(pt, 4), round(float(np.percentile(b, 2.5)), 4), round(float(np.percentile(b, 97.5)), 4)


def load_pairs():
    pairs = []
    for pos, path in SIMLEX.items():
        if not os.path.exists(path):
            continue
        d = json.load(open(path, encoding="utf-8"))
        for p in d["pairs"]:
            pairs.append((p["a"], p["b"], float(p["gold"]), pos))
    return pairs


def run(k_grid=None):
    k_grid = k_grid or K_GRID
    chan = ConceptualChannel()
    pairs = load_pairs()
    # exact sparse cosine + gather the union feature vocabulary from the vectors actually used
    used = []   # (i_a_key, i_b_key, gold)
    vecs = {}   # (word,pos) -> dict feature->weight
    feat_index = {}
    gold_all = []
    exact_sims = []
    for a, b, gold, pos in pairs:
        va = chan.vec(a, pos); vb = chan.vec(b, pos)
        if va is None or vb is None:
            continue
        # exact cosine (the landed channel)
        common = set(va) & set(vb)
        if common:
            num = sum(va[w] * vb[w] for w in common)
            da = np.sqrt(sum(x * x for x in va.values())); db = np.sqrt(sum(x * x for x in vb.values()))
            cos = num / (da * db) if da > 1e-12 and db > 1e-12 else 0.0
        else:
            cos = 0.0
        ka, kb = (a, pos), (b, pos)
        vecs[ka] = va; vecs[kb] = vb
        for f in va:
            feat_index.setdefault(f, len(feat_index))
        for f in vb:
            feat_index.setdefault(f, len(feat_index))
        used.append((ka, kb, gold)); gold_all.append(gold); exact_sims.append(cos)
    n_feat = len(feat_index); n_pairs = len(used)
    exact = _boot_rho(exact_sims, gold_all, SEED)

    # one Rademacher sign projection at MAX K; smaller K = column prefix (valid JL) -- project each unique word once
    kmax = max(k_grid)
    rng = np.random.default_rng(SEED)
    R = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(n_feat, kmax)) / np.sqrt(kmax)
    proj = {}   # (word,pos) -> projected dense vector at kmax
    for key, v in vecs.items():
        acc = np.zeros(kmax, dtype=np.float32)
        for f, w in v.items():
            acc += np.float32(w) * R[feat_index[f]]
        proj[key] = acc

    curves = {}
    for K in k_grid:
        sims = []
        for ka, kb, _g in used:
            a = proj[ka][:K]; b = proj[kb][:K]
            na = float(np.linalg.norm(a)); nb = float(np.linalg.norm(b))
            sims.append(float(np.dot(a, b) / (na * nb)) if na > 1e-9 and nb > 1e-9 else 0.0)
        curves[K] = _boot_rho(sims, gold_all, SEED + K)
    # info-free twin: shuffled gold at full exact
    r = np.random.default_rng(SEED + 7)
    twin = _boot_rho(exact_sims, list(np.array(gold_all)[r.permutation(n_pairs)]), SEED + 8)

    # verdict: smallest K whose CI includes the exact point estimate (intrinsic dim), and rising@1024?
    ksat = None
    for K in k_grid:
        if curves[K][2] >= exact[0]:      # projected upper-CI reaches exact point
            ksat = K; break
    op = 1024 if 1024 in k_grid else k_grid[-1]
    top = k_grid[-1]
    rising = curves[top][1] > curves[op][2]
    return {"anchor": "dim_phase_diagram_meaning_v1", "n_pairs": n_pairs, "n_feat": n_feat,
            "exact_rho": exact, "twin_shuffled_gold_rho": twin, "k_grid": k_grid,
            "projected_rho": curves, "k_saturation": ksat, "rising_at_1024": bool(rising),
            "verdict": ("SPARSE_EXACT_no_fixed_D__intrinsic_dim~%s" % (ksat if ksat else ">%d" % top))}


def summarize(res):
    print(f"\n=== MEANING CHANNEL dimensionality probe (SimLex noun+verb, n_pairs={res['n_pairs']}, "
          f"n_feat={res['n_feat']}) ===")
    e = res["exact_rho"]
    print(f"  EXACT sparse cosine (the landed channel): rho {e[0]:.3f} CI[{e[1]:.3f},{e[2]:.3f}]  "
          f"(full feature width -- NOT a fixed-D store)")
    print(f"  shuffled-gold twin: rho {res['twin_shuffled_gold_rho'][0]:.3f}  (info-free floor ~0)")
    print("  random-projected rho vs embedding dim K:")
    print("      K     rho   [lo,   hi]")
    for K in res["k_grid"]:
        c = res["projected_rho"][K]
        print(f"  {K:>5d}   {c[0]:.3f}  [{c[1]:.3f},{c[2]:.3f}]")
    print(f"  intrinsic dim (first K whose CI reaches exact rho): K* = {res['k_saturation']}")
    print(f"  VERDICT: {res['verdict']}  (rising@1024={res['rising_at_1024']}) -- the ORGAN is sparse-exact, "
          f"so D is not a lever FOR IT; K* is the min-D to BIND meaning into the register")


def self_test():
    chan = ConceptualChannel()
    # two clearly-related nouns should score above two unrelated; and a word vs itself ~ 1.0
    hi = chan.similarity("dog", "N", "cat", "N")
    lo = chan.similarity("dog", "N", "truth", "N")
    assert hi is not None and lo is not None and hi > lo, f"related>unrelated expected; dog-cat={hi} dog-truth={lo}"
    r = _spearman([1, 2, 3, 4], [1, 2, 3, 4]); assert abs(r - 1.0) < 1e-9, r
    r2 = _spearman([1, 2, 3, 4], [4, 3, 2, 1]); assert abs(r2 + 1.0) < 1e-9, r2
    print(f"SELF-TEST PASS: dog-cat {hi:.3f} > dog-truth {lo:.3f}; spearman monotone ok")


def main():
    if "--self-test" in sys.argv:
        self_test(); return
    t0 = time.time()
    res = run()
    res["elapsed_s"] = round(time.time() - t0, 1)
    summarize(res)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="utf-8", newline="") as fh:
        json.dump(res, fh, indent=2)
    print(f"\nwrote {OUTDIR} (elapsed {res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
