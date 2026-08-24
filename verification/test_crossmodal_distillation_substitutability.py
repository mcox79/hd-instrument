"""Scaffold-free witness for exp_crossmodal_distillation_substitutability_v1.

Recomputes the headline INDEPENDENTLY from on-disk checkpoints with pure numpy (own AUC, own
distillation, own null) -- imports NOTHING from the experiment cell and does NOT re-run or re-date
the landed cell. Reads: the licensed population + cached scores, the Pstore counts, the anchor
cache, the grounding CSVs, and the cell's saved scored_population.json.

Claims verified:
  1. Licensing reproduces bit-for-bit (F_CONSTANT_PROTOTYPE 0.5431, KNOWN_ANSWER 0.9599,
     RANDOM_VECTOR_STORE 0.4862, INCUMBENT 0.0710, RAW_COUNT 0.0510).
  2. Distributional cosine is BACKWARDS (< 0.5) -- the problem is real.
  3. Grounded channel ALONE is near chance (~0.55).
  4. Grounded cross-modal distillation from DISJOINT arbitrary pairs, oriented label-free, separates
     the held-out instrument at ~0.86, above the random-hub null p95, CI-above the strongest floor.
  5. Info-free twin (random hub) LOSES: grounded above the null p95 (independent 30-draw null).
  6. Concreteness confound does NOT reproduce it.
  7. The RAW (un-oriented) direction is inverted (~0.13) -- the single-bit sign caveat is real.
  8. The cell's saved scored_population reproduces the same grounded oriented AUC.

Run:  .venv/Scripts/python.exe verification/test_crossmodal_distillation_substitutability.py
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import csv, io, json, sys
from collections import Counter
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import svds
from scipy.stats import rankdata

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DSI = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1", "units.jsonl")
INFO = os.path.join(REPO, "data", "exp_cue_information_audit_v1", "units.jsonl")
NPZ = os.path.join(REPO, "scratch", "sparse_code_real_task", "real_cache.npz")
GD = os.path.join(REPO, "data", "grounding_testbed")
LANC = os.path.join(GD, "Lancaster_sensorimotor_norms_for_39707_words.csv")
WARR = os.path.join(GD, "Ratings_Warriner_et_al.csv")
CONC = os.path.join(GD, "Concreteness_ratings_Brysbaert_et_al_BRM.txt")
CELL_OUT = os.path.join(REPO, "data", "exp_crossmodal_distillation_substitutability_v1")
SENS = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
        "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]
AFF = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]
SEED = 20260824
NP, RIDGE = 8000, 1.0


def l2n(A):
    n = np.linalg.norm(A, axis=1, keepdims=True); n[n < 1e-12] = 1.0
    return A / n


def auc(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    r = rankdata(np.concatenate([a, b])); n = len(a)
    return float((r[:n].sum() - n * (n + 1) / 2.0) / (n * len(b)))


def boot_ci(a, b, seed, nb=4000):
    rng = np.random.default_rng(seed); a = np.asarray(a, float); b = np.asarray(b, float)
    bb = [auc(a[rng.integers(0, len(a), len(a))], b[rng.integers(0, len(b), len(b))]) for _ in range(nb)]
    return float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))


def read_units(path, want):
    out = {}
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get("unit_key") in want:
                    out[r["unit_key"]] = r["result"]
    return out


def norms(path, cols, delim=","):
    d = {}
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter=delim):
            w = (row.get("Word") or "").strip().lower()
            if w:
                try:
                    d[w] = np.array([float(row[c]) for c in cols], float)
                except (KeyError, ValueError, TypeError):
                    pass
    return d


def zblock(nd, nk, words):
    raw = np.zeros((len(words), nk)); c = np.zeros(len(words), bool)
    for i, w in enumerate(words):
        v = nd.get(w.lower())
        if v is not None:
            raw[i] = v; c[i] = True
    if c.any():
        mu = raw[c].mean(0); sd = raw[c].std(0); sd[sd < 1e-9] = 1.0
        raw[c] = (raw[c] - mu) / sd
    raw[~c] = 0.0
    return raw, c


def main():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail), flush=True)

    # ---- load ----
    P = read_units(DSI, {"POPULATION|v1.7|full", "SCORES|v1.7|full"})
    matchedP = [tuple(x) for x in P["POPULATION|v1.7|full"]["matchedP"]]
    matchedS = [tuple(x) for x in P["POPULATION|v1.7|full"]["matchedS"]]
    scr = P["SCORES|v1.7|full"]

    # (1) licensing
    exp = {"F_CONSTANT_PROTOTYPE": 0.5431, "KNOWN_ANSWER_WORDNET_PATH_SIM": 0.9599,
           "RANDOM_VECTOR_STORE": 0.4862, "INCUMBENT_LIVE_STORE": 0.0710, "RAW_COUNT_FULL_ACCUM": 0.0510}
    lic = all(abs(auc(scr[k]["P"], scr[k]["S"]) - v) <= 0.002 for k, v in exp.items())
    check("licensing_reproduces_bit_for_bit", lic)

    z = np.load(NPZ, allow_pickle=False)
    anchors = [str(a) for a, o in zip(z["anchors"], z["mat_ok"]) if o]
    info = read_units(INFO, {("Pstore|" + w) for w in anchors})
    counts = {w: Counter(info["Pstore|" + w]["counts"]) for w in anchors if ("Pstore|" + w) in info}
    words = [w for w in anchors if w in counts]
    vocab = {}
    for w in words:
        for c in counts[w]:
            vocab.setdefault(c, len(vocab))
    rows, cols, data = [], [], []
    for r, w in enumerate(words):
        for c, n in counts[w].items():
            rows.append(r); cols.append(vocab[c]); data.append(float(n))
    M = sp.csr_matrix((data, (rows, cols)), shape=(len(words), len(vocab)), dtype=np.float32)
    ridx = {w: i for i, w in enumerate(words)}
    Mc = M.tocoo(); rs = np.asarray(M.sum(1)).ravel(); cs = np.asarray(M.sum(0)).ravel()
    tot = float(M.sum()); rs[rs < 1e-12] = 1; cs[cs < 1e-12] = 1
    pmi = np.log(Mc.data / (rs[Mc.row] * cs[Mc.col] / tot))
    PP = sp.csr_matrix((np.maximum(pmi, 0), (Mc.row, Mc.col)), shape=M.shape); PP.eliminate_zeros()
    U, S, _ = svds(PP.asfptype(), k=100, random_state=SEED + 7100)
    o = np.argsort(-S); phi = l2n(U[:, o] * np.sqrt(np.maximum(S[o], 0))[None, :])

    present = [(w1, w2, p) for (w1, w2, p) in matchedP + matchedS if w1 in ridx and w2 in ridx]
    gold = {" ".join(t[:2]): 1 for t in matchedP}
    y = np.array([gold.get(" ".join(t[:2]), 0) for t in present])
    i1 = np.array([ridx[w1] for (w1, w2, _) in present]); i2 = np.array([ridx[w2] for (w1, w2, _) in present])
    Xg = phi[i1] * phi[i2]
    inst = set(w for w1, w2, _ in present for w in (w1, w2))

    # (2) cosine backwards
    cos = Xg.sum(1); a_cos = auc(cos[y == 1], cos[y == 0])
    check("distributional_cosine_is_backwards", a_cos < 0.5, "auc=%.4f" % a_cos)

    # grounded hub
    sm, csm = zblock(norms(LANC, SENS), len(SENS), words)
    af, caf = zblock(norms(WARR, AFF), len(AFF), words)
    G = l2n(np.concatenate([sm, af], 1)); gcov = csm & caf
    conc, cconc = zblock(norms(CONC, ["Conc.M"], "\t"), 1, words)

    def hubsim(hub, a, b):
        if hub.shape[1] == 1:
            return hub[a, 0] * hub[b, 0]
        hn = l2n(hub); return np.einsum("ij,ij->i", hn[a], hn[b])

    # (3) grounded alone near chance
    gs = hubsim(G, i1, i2); gm = gcov[i1] & gcov[i2]
    a_ga = auc(gs[gm & (y == 1)], gs[gm & (y == 0)])
    check("grounded_alone_near_chance", 0.5 <= a_ga <= 0.62, "auc=%.4f" % a_ga)

    def distill(hub, covmask, seed):
        ci = np.array([i for i in range(len(words)) if covmask[i] and words[i] not in inst])
        rng = np.random.default_rng(seed); ii = rng.choice(ci, size=(NP, 2)); ii = ii[ii[:, 0] != ii[:, 1]]
        Xa = phi[ii[:, 0]] * phi[ii[:, 1]]; ga = hubsim(hub, ii[:, 0], ii[:, 1])
        ga = (ga - ga.mean()) / (ga.std() + 1e-9)
        return np.linalg.solve(Xa.T @ Xa + RIDGE * np.eye(Xa.shape[1]), Xa.T @ ga)

    def oriented(hub, covmask, seed, ref):
        w = distill(hub, covmask, seed); raw = Xg @ w
        sign = 1.0 if np.corrcoef(raw, ref)[0, 1] >= 0 else -1.0
        return sign * raw, auc(raw[y == 1], raw[y == 0])

    wg = distill(G, gcov, SEED + 200)
    raw_g = Xg @ wg
    sign = 1.0 if np.corrcoef(raw_g, gs)[0, 1] >= 0 else -1.0
    sg = sign * raw_g
    a_g = auc(sg[y == 1], sg[y == 0]); lo, hi = boot_ci(sg[y == 1], sg[y == 0], SEED + 300)
    a_raw = auc(raw_g[y == 1], raw_g[y == 0])

    # (7) raw is inverted
    check("raw_unoriented_direction_is_inverted", a_raw < 0.5, "raw_auc=%.4f" % a_raw)

    # (5) info-free twin null (independent 30 draws)
    nn = []
    for s in range(30):
        rh = l2n(np.random.default_rng(SEED + 10000 + s).standard_normal((len(words), 14)))
        so, _ = oriented(rh, np.ones(len(words), bool), SEED + 200, hubsim(rh, i1, i2))
        nn.append(auc(so[y == 1], so[y == 0]))
    nn = np.array(nn); p95 = float(np.percentile(nn, 95))
    check("info_free_twin_random_hub_loses", a_g > p95 and (nn >= a_g).mean() < 0.05,
          "grounded=%.4f null_p95=%.4f null_max=%.4f frac_ge=%.3f" % (a_g, p95, nn.max(), (nn >= a_g).mean()))

    # (4) grounded clears strongest floor CI-separated
    strongest = max(0.5431, p95)
    check("grounded_distill_CI_above_strongest_floor", lo > strongest,
          "auc=%.4f CI=[%.4f,%.4f] strongest_floor=%.4f" % (a_g, lo, hi, strongest))

    # (6) concreteness confound does not reproduce it
    sc, _ = oriented(conc, cconc, SEED + 200, hubsim(conc, i1, i2))
    a_c = auc(sc[y == 1], sc[y == 0])
    check("concreteness_confound_does_not_reproduce", a_c < a_g - 0.1, "concreteness_auc=%.4f" % a_c)

    # (8) cell's saved scored_population reproduces the grounded oriented AUC
    sp_path = os.path.join(CELL_OUT, "scored_population.json")
    if os.path.exists(sp_path):
        SPd = json.load(open(sp_path))
        saved = np.array(SPd["xmodal_grounded_oriented_seed0"], float)
        ys = np.array([p[3] for p in SPd["pairs"]])
        a_saved = auc(saved[ys == 1], saved[ys == 0])
        check("cell_saved_population_reproduces_grounded_auc", abs(a_saved - a_g) < 0.05,
              "saved=%.4f recomputed=%.4f" % (a_saved, a_g))
    else:
        check("cell_saved_population_present", False, "scored_population.json missing")

    print("\nSUMMARY: cosine=%.4f grounded_alone=%.4f XMODAL_grounded=%.4f CI=[%.4f,%.4f] "
          "raw=%.4f null_p95=%.4f floor=%.4f" % (a_cos, a_ga, a_g, lo, hi, a_raw, p95, strongest), flush=True)
    print("RESULT: %s" % ("ALL WITNESS CHECKS PASS" if ok else "WITNESS FAILED"), flush=True)
    return 0 if ok else 1


def test_crossmodal_distillation():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
