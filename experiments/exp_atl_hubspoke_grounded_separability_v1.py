"""exp_atl_hubspoke_grounded_separability_v1 -- the RICHER ATL grounded hub-and-spoke, tested where the 12-dim
norms were ruled out. Binder 2016 ~65-dim brain-based attributes + Warriner VAD affect, ATL distinctive-feature
WHITENED (decorrelate the dominant shared axis -- the brain's privilege-distinctive-features operation), propagated
to coverage by brain-faithful SEMANTIC INHERITANCE through the WordNet hierarchy.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

THE BRIEF'S CORE CLAIM (this cell tests it with a NUMBER, not a re-run): "grounded dimensions are ORTHOGONAL to
distribution, so they SEPARATE the senses co-occurrence merges." So the load-bearing measurement is the SEPARABILITY
DECOMPOSITION: for each strict-doc-disjoint SemCor SUBORDINATE test item, how far apart are the GOLD (subordinate)
sense and its DOMINANT competitor IN THE GROUNDED SPACE -- and specifically, AMONG the items whose senses distribution
MERGES (high w2v-gloss cosine), does grounding pull them apart? Split by concreteness (grounding should separate
CONCRETE homonymy, per the parent's bank-river 0.813 vs bank-money -0.096 sanity check; the open question is ABSTRACT
regular polysemy, which dominates SemCor).

BRAIN-FOUNDATIONAL (researched, this session):
  * ATL hub-and-spoke canonical spokes = Sound/Praxis/Valence/Vision/Function/Speech (Lambon-Ralph 2017) -- PERCEPTUAL
    + AFFECT. Binder 2016 (Vision..Motor..Emotion..Cognition..Arousal, 65 dims) is the direct brain-attribute asset;
    Warriner VAD is the Valence spoke. (There is NO canonical "relational" spoke -- relational/thematic knowledge is
    a SEPARATE system, AG/event-schema; tested elsewhere.)
  * The ATL privileges DISTINCTIVE features == DECORRELATION: WHITEN the shared covariance so the dominant shared axis
    (concreteness/salience) does not swamp the discriminating dims (Patterson-Nestor-Rogers 2007; the landed
    hdlab.grounded_similarity distinctive-feature read-out). Coarse 12-dim was ruled out; 65-dim + whitening is the test.
  * Coverage to abstract/unseen senses = category-based SEMANTIC INHERITANCE down the WordNet hierarchy (a hyponym
    inherits its hypernym's grounded features), NOT a trained regressor (the brain does not regress vectors onto norms).

Readout = the WIRED biased-competition hdlab.diagnostic_context_wsd (asset-independent -- it accepts grounded/hub
vectors). Arms: gloss-w2v floor, RICH-w2v launch pad (0.318), grounded-only keys, CONCAT hub [w2v (+) lam*grounded],
grounded-channel additive fuse -- each vs the launch-pad floor, with the SHUFFLED-GROUNDING info-free twin LOSING.

Strict doc-disjoint SemCor subordinate, subject-weighted a_s, n=2676. Glass-box, NO external LLM, NO training,
NO transformer. Core-capped (USER 2026-09-04). ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv
# KB_REFERENT: data/grounding_testbed/Ratings_Warriner_et_al.csv
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import csv
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_grounded_separability_v1")
BINDER = os.path.join(_REPO, "data", "corpora", "binder", "binder2016_ratings.csv")
WARRINER = os.path.join(_REPO, "data", "grounding_testbed", "Ratings_Warriner_et_al.csv")

# Binder 2016: the 65 brain-attribute columns (Vision .. Arousal), col idx 5..69 inclusive.
BINDER_ATTR_LO, BINDER_ATTR_HI = 5, 70


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


# ---------------------------------------------------------------------------------------------------------------
# grounded feature tables: Binder 65-dim (+ optional Warriner VAD), z-scored on their own population.
# ---------------------------------------------------------------------------------------------------------------
def load_binder():
    words, rows = [], []
    with open(BINDER, encoding="utf-8-sig", newline="") as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            w = (r[1] or "").strip().lower()
            if not w or " " in w:
                continue
            try:
                vec = [float(x) for x in r[BINDER_ATTR_LO:BINDER_ATTR_HI]]
            except (ValueError, IndexError):
                continue
            if len(vec) != (BINDER_ATTR_HI - BINDER_ATTR_LO):
                continue
            words.append(w)
            rows.append(vec)
    M = np.asarray(rows, np.float64)
    mu, sd = M.mean(0), M.std(0) + 1e-9
    Z = (M - mu) / sd
    return {w: Z[i] for i, w in enumerate(words)}


def load_warriner():
    d = {}
    with open(WARRINER, encoding="utf-8", errors="ignore", newline="") as f:
        for row in csv.DictReader(f):
            try:
                d[row["Word"].strip().lower()] = [float(row["V.Mean.Sum"]), float(row["A.Mean.Sum"]),
                                                  float(row["D.Mean.Sum"])]
            except Exception:
                pass
    M = np.asarray(list(d.values()), np.float64)
    mu, sd = M.mean(0), M.std(0) + 1e-9
    return {w: (np.asarray(v) - mu) / sd for w, v in d.items()}


class Grounded:
    """Rich grounded feature space with the ATL distinctive-feature whitening. add_affect appends Warriner VAD
    (zero-filled when a Binder word lacks affect ratings). whiten() fits the decorrelation transform on the
    covered population (gold-blind: the transform sees only the feature table, never labels)."""

    def __init__(self, add_affect=True):
        binder = load_binder()
        warr = load_warriner() if add_affect else {}
        words = sorted(binder)
        rows = []
        for w in words:
            v = binder[w]
            if add_affect:
                a = warr.get(w)
                v = np.concatenate([v, a if a is not None else np.zeros(3)])
            rows.append(v)
        self.words = words
        self.raw = {w: rows[i] for i, w in enumerate(words)}
        self.dim = len(rows[0])
        X = np.asarray(rows)
        self.mu = X.mean(0)
        Xc = X - self.mu
        cov = (Xc.T @ Xc) / Xc.shape[0]
        evals, evecs = np.linalg.eigh(cov)
        self.W = evecs * (1.0 / np.sqrt(np.clip(evals, 1e-8, None)))[None, :]   # whitening projection
        self.top_pc_frac = float(evals[-1] / evals.sum())

    def vec(self, word, whiten):
        r = self.raw.get(word)
        if r is None:
            return None
        return _unit((r - self.mu) @ self.W) if whiten else _unit(r)


# ---------------------------------------------------------------------------------------------------------------
# semantic inheritance: a synset's grounded centroid = distance-weighted mean over own + hypernym-chain + hyponym
# lemma/gloss words that are grounded-covered (the brain's category-based grounding inference).
# ---------------------------------------------------------------------------------------------------------------
_STOP = G1._STOP


def _toks(defn):
    out = []
    for tok in defn.replace(";", " ").replace(",", " ").split():
        t = "".join(c for c in tok.lower() if c.isalpha())
        if len(t) >= 3 and t not in _STOP:
            out.append(t)
    return out


def sense_grounded_words(syn_name, up_depth=3, n_hypo=12, decay=0.5, own_lemma_w=1.0):
    """(word, weight) bag for a synset via WordNet inheritance -- own lemmas/gloss, hypernym chain (decayed UP),
    a few hyponyms (grounded concrete descendants DOWN).

    own_lemma_w controls the weight of the synset's OWN surface lemma_names. CRITICAL: competing senses of one
    word SHARE that surface form, so grounding it at full weight collapses their grounded signatures to identical
    (the smoke's concrete cos 0.92 artifact). own_lemma_w=0.0 = CATEGORY-ONLY grounding (gloss + hypernym +
    hyponym), the sense's meaning by its category/definition -- the non-degenerate, brain-faithful signature."""
    from nltk.corpus import wordnet as wn
    weighted = []

    def add(s, w, lemma_w=1.0):
        for ln in s.lemma_names():
            if lemma_w > 0:
                weighted.append((ln.lower().split("_")[0], w * lemma_w))
        for tok in _toks(s.definition()):
            weighted.append((tok, w * 0.5))
    try:
        s = wn.synset(syn_name)
    except Exception:
        return weighted
    add(s, 1.0, lemma_w=own_lemma_w)
    cur, ww = [s], decay
    for _ in range(up_depth):
        nxt = []
        for x in cur:
            for h in x.hypernyms():
                add(h, ww)
                nxt.append(h)
        cur, ww = nxt, ww * decay
        if not cur:
            break
    for h in s.hyponyms()[:n_hypo]:
        add(h, decay)
    return weighted


def build_sense_grounded(cand, gr, whiten, own_lemma_w=0.0):
    """synset -> unit grounded centroid (or None if no grounded word inherited). own_lemma_w=0.0 (default) =
    CATEGORY-ONLY grounding (gloss+hypernym+hyponym; the non-degenerate signature that does not collapse competing
    senses onto their shared surface form)."""
    out = {}
    for syn in cand:
        vs = []
        for word, wt in sense_grounded_words(syn, own_lemma_w=own_lemma_w):
            v = gr.vec(word, whiten)
            if v is not None:
                vs.append(v * wt)
        out[syn] = _unit(np.sum(vs, 0)) if vs else None
    return out


# ---------------------------------------------------------------------------------------------------------------
def _paired_ci(a, b, seed):
    return G1._paired(np.asarray(a, float), np.asarray(b, float), seed)


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs])
    sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0])
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    if smoke:
        dev_idx, test_idx = dev_idx[:250], test_idx[:250]

    cand = set()
    for i in dev_idx + test_idx:
        cand.update(recs[i]["tn"])
    cand = sorted(cand)

    gr = Grounded(add_affect=True)
    print("[grounded] Binder+Warriner dim=%d covered_words=%d top_pc_frac=%.3f (%.0fs)"
          % (gr.dim, len(gr.words), gr.top_pc_frac, time.time() - t0), flush=True)

    # sense grounded centroids: CATEGORY-ONLY (own_lemma_w=0.0, the non-degenerate signature) + a SURFACE variant
    # (own_lemma_w=1.0) kept only to document the shared-surface-lemma collapse control.
    sg_white = build_sense_grounded(cand, gr, whiten=True, own_lemma_w=0.0)
    sg_raw = build_sense_grounded(cand, gr, whiten=False, own_lemma_w=0.0)
    sg_white_surface = build_sense_grounded(cand, gr, whiten=True, own_lemma_w=1.0)
    cov = np.mean([sg_white[s] is not None for s in cand])
    gloss_words = {s: G1._seed_words(s, w2i) for s in cand}
    gloss_sig = {s: G1._sigvec(mat, w2i, gloss_words[s]) for s in cand}   # unit w2v gloss centroid (L0)
    print("[grounded] sense-inheritance coverage=%.3f of %d candidate synsets (%.0fs)"
          % (cov, len(cand), time.time() - t0), flush=True)

    # ---------------------------------------------------------------------------------------------------------
    # (1) SEPARABILITY DECOMPOSITION -- the brief's core claim, as a number.
    #     For each test item: gold (subordinate) vs DOMINANT competitor (max SemCor prior among candidates).
    # ---------------------------------------------------------------------------------------------------------
    def cos(a, b):
        return float(a @ b) if (a is not None and b is not None) else None

    sep = {"grounded_white": [], "grounded_raw": [], "w2v_gloss": [], "concrete": [], "grounded_surface": []}
    n_both_grounded = 0
    for i in test_idx:
        r = recs[i]
        tn = r["tn"]
        gold = r["gold"]
        if gold not in tn or len(tn) < 2:
            continue
        prior = np.asarray(r["prior"], float)[:len(tn)]
        dom = tn[int(np.argmax(prior))]
        if dom == gold:
            # gold is itself the max-prior sense on this population; use the next-highest as the competitor
            order = np.argsort(-prior)
            dom = tn[int(order[1])]
        cg, cd = cos(sg_white.get(gold), sg_white.get(dom)), None
        gg, gd = sg_white.get(gold), sg_white.get(dom)
        if gg is not None and gd is not None:
            n_both_grounded += 1
            sep["grounded_white"].append(float(gg @ gd))
            rg, rd = sg_raw.get(gold), sg_raw.get(dom)
            sep["grounded_raw"].append(float(rg @ rd))
            wg, wd = gloss_sig.get(gold), gloss_sig.get(dom)
            sep["w2v_gloss"].append(float(wg @ wd) if (wg is not None and np.any(wg) and wd is not None and np.any(wd)) else np.nan)
            # concreteness proxy: gold sense's head lemma directly Binder-covered (concrete homonymy vs abstract)
            head = gold.split(".")[0]
            sep["concrete"].append(bool(gr.raw.get(head) is not None))
            # surface-collapse control: same cos but with own-surface-lemma grounding (own_lemma_w=1.0)
            sg2, sd2 = sg_white_surface.get(gold), sg_white_surface.get(dom)
            sep["grounded_surface"].append(float(sg2 @ sd2) if (sg2 is not None and sd2 is not None) else np.nan)

    gw = np.asarray(sep["grounded_white"]); w2 = np.asarray(sep["w2v_gloss"]); conc = np.asarray(sep["concrete"])
    valid = ~np.isnan(w2)
    # the crux: AMONG items distribution MERGES (high w2v cos), does grounding SEPARATE them (low grounded cos)?
    merged = valid & (w2 >= 0.5)
    decomp = {
        "n_test_items": len(test_idx),
        "n_both_grounded": int(n_both_grounded),
        "grounded_coverage_of_pairs": round(float(n_both_grounded / max(1, len(test_idx))), 3),
        "grounded_white_cos_gold_vs_dominant_mean": round(float(gw.mean()), 4) if len(gw) else None,
        "grounded_white_cos_median": round(float(np.median(gw)), 4) if len(gw) else None,
        "frac_grounded_separable_cos_lt_0.5": round(float((gw < 0.5).mean()), 4) if len(gw) else None,
        "w2v_gloss_cos_gold_vs_dominant_mean": round(float(np.nanmean(w2)), 4) if valid.any() else None,
        "n_distribution_merged_cos_ge_0.5": int(merged.sum()),
        "among_merged__grounded_white_cos_mean": round(float(gw[merged].mean()), 4) if merged.any() else None,
        "among_merged__frac_grounding_rescues_cos_lt_0.5": round(float((gw[merged] < 0.5).mean()), 4) if merged.any() else None,
        "concrete__grounded_cos_mean": round(float(gw[conc].mean()), 4) if conc.any() else None,
        "abstract__grounded_cos_mean": round(float(gw[~conc].mean()), 4) if (~conc).any() else None,
        "frac_concrete": round(float(conc.mean()), 4) if len(conc) else None,
        "surface_collapse_control__grounded_cos_mean": (
            round(float(np.nanmean(np.asarray(sep["grounded_surface"]))), 4)
            if np.isfinite(np.asarray(sep["grounded_surface"], float)).any() else None),
    }
    print("[decomp] grounded cov=%.3f | grounded-white cos(gold,dom) mean=%s median=%s | frac separable(<.5)=%s"
          % (decomp["grounded_coverage_of_pairs"], decomp["grounded_white_cos_gold_vs_dominant_mean"],
             decomp["grounded_white_cos_median"], decomp["frac_grounded_separable_cos_lt_0.5"]), flush=True)
    print("[decomp] among distribution-MERGED (w2v>=.5, n=%d): grounded cos mean=%s | grounding RESCUES frac=%s"
          % (decomp["n_distribution_merged_cos_ge_0.5"], decomp["among_merged__grounded_white_cos_mean"],
             decomp["among_merged__frac_grounding_rescues_cos_lt_0.5"]), flush=True)
    print("[decomp] concrete grounded cos=%s | abstract grounded cos=%s | frac concrete=%s"
          % (decomp["concrete__grounded_cos_mean"], decomp["abstract__grounded_cos_mean"], decomp["frac_concrete"]),
          flush=True)

    # ---------------------------------------------------------------------------------------------------------
    # (2) a_s ARMS through the wired biased-competition readout (asset-independent).
    # ---------------------------------------------------------------------------------------------------------
    def w2v_ctx(r):
        return [(_unit(mat[w2i[x]])) for x in r["ctx"] if x in w2i]

    def a_s_w2v(idxs, sig):
        ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]
            rows = w2v_ctx(r)
            if not rows:
                continue
            G = np.stack([sig.get(s) if sig.get(s) is not None else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
            if not np.any(G):
                continue
            C = np.stack(rows)
            ok.append(int(tn[int(np.argmax(diagnostic_context_scores(C, G)))] == r["gold"]))
        return np.asarray(ok, float)

    def a_s_grounded(idxs, sgrnd, whiten, shuffle=False):
        rng = np.random.default_rng(12345) if shuffle else None
        ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]
            rows = [gr.vec(x, whiten) for x in r["ctx"]]
            rows = [v for v in rows if v is not None]
            if not rows:
                continue
            keys = [sgrnd.get(s) for s in tn]
            if all(k is None for k in keys):
                continue
            d = rows[0].shape[0]
            G = np.stack([k if k is not None else np.zeros(d) for k in keys])
            C = np.stack(rows)
            if shuffle:
                G = G[rng.permutation(len(G))]     # info-free twin: grounded keys permuted onto WRONG senses
            ok.append(int(tn[int(np.argmax(diagnostic_context_scores(C, G)))] == r["gold"]))
        return np.asarray(ok, float)

    def a_s_hub(idxs, wsig, sgrnd, lam, shuffle=False):
        """CONCAT hub: key = [unit(w2v gloss) ; lam*unit(grounded_white)] ; context = same on both spokes."""
        rng = np.random.default_rng(777) if shuffle else None
        ok = []
        for i in idxs:
            r = recs[i]; tn = r["tn"]
            crows = []
            for x in r["ctx"]:
                if x not in w2i:
                    continue
                dv = _unit(mat[w2i[x]])
                gv = gr.vec(x, True)
                crows.append(np.concatenate([dv, lam * (gv if gv is not None else np.zeros(gr.dim))]))
            if not crows:
                continue
            keys = []
            for s in tn:
                dv = wsig.get(s)
                dv = dv if (dv is not None and np.any(dv)) else np.zeros(G1.EMB_DIM, np.float32)
                gv = sgrnd.get(s)
                keys.append(np.concatenate([dv, lam * (gv if gv is not None else np.zeros(gr.dim))]))
            G = np.stack([_unit(k) for k in keys]); C = np.stack([_unit(c) for c in crows])
            if shuffle:
                G = G[rng.permutation(len(G))]
            ok.append(int(tn[int(np.argmax(diagnostic_context_scores(C, G)))] == r["gold"]))
        return np.asarray(ok, float)

    # rich w2v launch-pad atom (L3) reused from the brain-faithful reader builder
    import experiments.exp_brain_faithful_reader_v1 as BF
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in cand}

    arms = {}
    floor_gloss = a_s_w2v(test_idx, gloss_sig)
    floor_rich = a_s_w2v(test_idx, rich_sig)                    # the launch pad (~0.318)
    arms["L0_gloss_w2v"] = round(float(floor_gloss.mean()), 4)
    arms["L3_rich_w2v_LAUNCHPAD"] = round(float(floor_rich.mean()), 4)
    print("[arm] L0_gloss_w2v=%.4f  L3_rich_w2v(launchpad)=%.4f (%.0fs)"
          % (arms["L0_gloss_w2v"], arms["L3_rich_w2v_LAUNCHPAD"], time.time() - t0), flush=True)

    gk_white = a_s_grounded(test_idx, sg_white, True)
    gk_raw = a_s_grounded(test_idx, sg_raw, False)
    arms["grounded_keys_whitened"] = round(float(gk_white.mean()), 4)
    arms["grounded_keys_raw"] = round(float(gk_raw.mean()), 4)
    print("[arm] grounded_keys_whitened=%.4f  grounded_keys_raw=%.4f (%.0fs)"
          % (arms["grounded_keys_whitened"], arms["grounded_keys_raw"], time.time() - t0), flush=True)

    # CONCAT hub: sweep lam on DEV, report best on TEST
    best_lam, best_dev = 0.0, -1.0
    for lam in [0.25, 0.5, 1.0, 2.0]:
        dv = a_s_hub(dev_idx, rich_sig, sg_white, lam).mean()
        if dv > best_dev:
            best_dev, best_lam = float(dv), lam
    hub_test = a_s_hub(test_idx, rich_sig, sg_white, best_lam)
    arms["hub_concat_best_lam"] = best_lam
    arms["hub_concat"] = round(float(hub_test.mean()), 4)
    hub_twin = a_s_hub(test_idx, rich_sig, sg_white, best_lam, shuffle=True)
    arms["hub_concat_shuffled_twin"] = round(float(hub_twin.mean()), 4)
    print("[arm] hub_concat(lam=%.2f)=%.4f  shuffled_twin=%.4f (%.0fs)"
          % (best_lam, arms["hub_concat"], arms["hub_concat_shuffled_twin"], time.time() - t0), flush=True)

    # paired contrasts vs the launch-pad floor (align lengths defensively)
    def pair(x):
        n = min(len(x), len(floor_rich))
        return _paired_ci(x[:n], floor_rich[:n], 901)
    res = {
        "n_dev": len(dev_idx), "n_test": len(test_idx),
        "separability_decomposition": decomp,
        "arms": arms,
        "hub_vs_launchpad": pair(hub_test),
        "grounded_keys_white_vs_launchpad": pair(gk_white),
        "hub_vs_shuffled_twin": _paired_ci(hub_test[:min(len(hub_test), len(hub_twin))],
                                           hub_twin[:min(len(hub_test), len(hub_twin))], 902),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = ("ATL RICHER GROUNDED HUB | launchpad=%.4f hub_concat=%.4f (vs launchpad sep=%s ci=%s) | "
                       "grounded cov=%.3f cos(gold,dom)=%.3f rescues-merged=%s | %s"
                       % (arms["L3_rich_w2v_LAUNCHPAD"], arms["hub_concat"], res["hub_vs_launchpad"]["sep"],
                          res["hub_vs_launchpad"]["ci"], decomp["grounded_coverage_of_pairs"],
                          decomp["grounded_white_cos_gold_vs_dominant_mean"] or -1,
                          decomp["among_merged__frac_grounding_rescues_cos_lt_0.5"],
                          "GROUNDING CROSSES" if res["hub_vs_launchpad"]["sep"] and arms["hub_concat"] > arms["L3_rich_w2v_LAUNCHPAD"]
                          else "LOCATED NEGATIVE (grounding does not cross the launch pad)"))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_grounded_separability_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    gr = Grounded(add_affect=True)
    assert gr.dim == (BINDER_ATTR_HI - BINDER_ATTR_LO) + 3, "dim = 65 Binder + 3 VAD"
    assert len(gr.words) >= 400, "Binder coverage collapsed: %d" % len(gr.words)
    v = gr.vec("dog", True)
    assert v is not None and abs(np.linalg.norm(v) - 1.0) < 1e-6, "whitened vec is unit"
    # inheritance returns a grounded centroid for a concrete synset
    sg = build_sense_grounded(["dog.n.01"], gr, True)
    assert sg["dog.n.01"] is not None, "inheritance grounds dog.n.01"
    print("SELFTEST PASS (Binder %dd +VAD, whiten unit, inheritance grounds dog.n.01)" % gr.dim, flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
