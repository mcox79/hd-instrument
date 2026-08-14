"""Probe: does hdlab.bundling.bundle's PER-COMPONENT magnitude renormalisation (bundling.py
lines 36-39) erase per-feature weighting, and does it amplify near-cancelled components?

All hdlab code is IMPORTED, never re-implemented:
  - hdlab.lexical_similarity.CONCEPT_FEATURES / _feature_vocab / _feature_vectors / _cos_complex
  - hdlab.bundling.bundle  (the real op under test)
Only the four (weighting x normalisation) arms differ; the feature geometry is identical.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import math
import random
import sys

sys.path.insert(0, "D:/AI/hd-instrument")

import numpy as np
import torch

from hdlab import modulators
from hdlab.bundling import bundle
from hdlab.lexical_similarity import (
    CONCEPT_FEATURES,
    N_DIM,
    _cos_complex,
    _feature_vectors,
    _feature_vocab,
    _concept_vector_from,
)

OUT = {}
st = modulators.current()
OUT["env"] = {
    "python": sys.executable,
    "torch": torch.__version__,
    "N_DIM": N_DIM,
    "recency_at_run": st.recency,           # must be 0.0 -> bundle takes the plain-sum branch
    "n_concepts": len(CONCEPT_FEATURES),
    "n_features": len(_feature_vocab()),
}
assert st.recency == 0.0, "recency != 0: bundle would take the decay branch, not line 34"

FV = _feature_vectors()
VOCAB = sorted(CONCEPT_FEATURES)
NC = len(VOCAB)

# ---- log-IDF weights: w_f = log2(N_concepts / df_f), df over ALL of CONCEPT_FEATURES ----------
# Same formula the refuted experiment used for supply A (exp_distinctiveness_weighted_composition_v1
# _assert_pmi_reduction line 353: expect = math.log(prof.n_docs / feat_df[ft], 2)).
df = {}
for feats in CONCEPT_FEATURES.values():
    for f in feats:
        df[f] = df.get(f, 0) + 1
W = {f: math.log(NC / df[f], 2) for f in df}
wv_all = np.array(sorted(W.values()))
OUT["weights"] = {
    "formula": "w_f = log2(N_concepts / df_f), N_concepts=%d" % NC,
    "note": ("NO normalisation applied: both normalisers (per-component s/|s| and whole-vector "
             "s/||s||) are invariant to a global positive rescale of all weights, so any "
             "normalisation of W is a no-op for every number below. Verified numerically."),
    "min": float(wv_all.min()), "p05": float(np.percentile(wv_all, 5)),
    "p50": float(np.percentile(wv_all, 50)), "p95": float(np.percentile(wv_all, 95)),
    "max": float(wv_all.max()), "ratio_max_min": float(wv_all.max() / wv_all.min()),
}


def stack_of(word, weighted):
    feats = sorted(CONCEPT_FEATURES[word])
    s = torch.stack([FV[t] for t in feats])
    if weighted:
        w = torch.tensor([W[t] for t in feats], dtype=torch.float32)
        s = s * torch.complex(w, torch.zeros_like(w)).unsqueeze(-1)
    return s


def raw_sum(word, weighted):
    return stack_of(word, weighted).sum(dim=0)          # bundling.py line 34, verbatim


def vec_percomp(word, weighted):
    """hdlab's real op: bundle() on the (optionally weighted) stack."""
    return bundle(stack_of(word, weighted))


def vec_l2(word, weighted):
    """Same sum, WHOLE-VECTOR L2 instead of the per-component step (bundling.py lines 41-42
    branch, i.e. what bundle() already does for the REAL/HRR case)."""
    s = raw_sum(word, weighted)
    n = s.norm()
    return s / n if float(n) > 0 else s


def cos_general(a, b):
    """Re(<a,b>)/(||a||*||b||). For per-component-renormalised FHRR vectors ||a||=||b||=sqrt(d),
    so this is EXACTLY hdlab's _cos_complex (asserted below); it stays well-defined for the
    L2-normalised arm, where _cos_complex's fixed /d denominator would not be a cosine."""
    num = float(torch.real(torch.sum(torch.conj(a) * b)))
    return num / float(a.norm() * b.norm())


# ---- metric-equivalence guard: cos_general == _cos_complex on the per-component arm -----------
mx = 0.0
for w1 in VOCAB[:40]:
    for w2 in VOCAB[:40]:
        a, b = vec_percomp(w1, False), vec_percomp(w2, False)
        mx = max(mx, abs(cos_general(a, b) - _cos_complex(a, b)))
OUT["metric_guard_max_abs_diff_cosgeneral_vs_cos_complex_percomp"] = mx
assert mx < 1e-5, mx

# ---- guard: vec_percomp(word, False) is byte-identical to the module's own concept path -------
bad = 0
for w in VOCAB:
    if not torch.equal(vec_percomp(w, False), _concept_vector_from(CONCEPT_FEATURES[w], FV)):
        bad += 1
OUT["guard_percomp_unweighted_matches_module_concept_vector_mismatches"] = bad
assert bad == 0

# =============================================================================================
# (a) distribution of |s_j| BEFORE the per-component renormalisation
# =============================================================================================
def mag_stats(weighted):
    fracs, ratios, kk = [], [], []
    for w in VOCAB:
        k = len(CONCEPT_FEATURES[w])
        if k < 2:
            continue                     # k=1 -> |s_j| == w_f everywhere, no cancellation possible
        m = raw_sum(w, weighted).abs().numpy()
        med = float(np.median(m))
        fracs.append(float((m < 0.10 * med).mean()))
        ratios.append(float(np.percentile(m, 1) / med))
        kk.append(k)
    return {
        "n_concepts_k_ge_2": len(fracs),
        "mean_frac_below_10pct_of_median": float(np.mean(fracs)),
        "max_frac_below_10pct_of_median": float(np.max(fracs)),
        "mean_p01_over_median": float(np.mean(ratios)),
        "mean_k": float(np.mean(kk)),
    }


OUT["a_magnitude_before_renorm"] = {
    "UNWEIGHTED": mag_stats(False),
    "LOGIDF_WEIGHTED": mag_stats(True),
}
# also: raw |s_j| percentiles pooled over all concepts with k>=2, and the amplification factor
# median(|s|)/|s_j| applied by the per-component step at the 1st percentile.
for tag, wt in (("UNWEIGHTED", False), ("LOGIDF_WEIGHTED", True)):
    pool = np.concatenate([raw_sum(w, wt).abs().numpy() / float(np.median(raw_sum(w, wt).abs().numpy()))
                           for w in VOCAB if len(CONCEPT_FEATURES[w]) >= 2])
    OUT["a_magnitude_before_renorm"][tag]["pooled_normalised_|s_j|/median"] = {
        "p001": float(np.percentile(pool, 0.1)), "p01": float(np.percentile(pool, 1)),
        "p05": float(np.percentile(pool, 5)), "p50": float(np.percentile(pool, 50)),
        "frac_below_0.10": float((pool < 0.10).mean()),
        "frac_below_0.25": float((pool < 0.25).mean()),
    }

# =============================================================================================
# (b) cosine between weighted and unweighted versions of the SAME concept
# =============================================================================================
same_pc, same_l2 = [], []
for w in VOCAB:
    if len(CONCEPT_FEATURES[w]) < 2:
        continue
    same_pc.append(_cos_complex(vec_percomp(w, False), vec_percomp(w, True)))   # hdlab's metric
    same_l2.append(cos_general(vec_l2(w, False), vec_l2(w, True)))
OUT["b_self_cos_weighted_vs_unweighted"] = {
    "PER_COMPONENT_RENORM_cos_complex": {
        "mean": float(np.mean(same_pc)), "median": float(np.median(same_pc)),
        "min": float(np.min(same_pc)), "p05": float(np.percentile(same_pc, 5)),
        "n": len(same_pc)},
    "WHOLE_VECTOR_L2": {
        "mean": float(np.mean(same_l2)), "median": float(np.median(same_l2)),
        "min": float(np.min(same_l2)), "p05": float(np.percentile(same_l2, 5)),
        "n": len(same_l2)},
}

# =============================================================================================
# (c) KEY CONTROL: near-pair vs random-pair separation under 2x2 arms
# =============================================================================================
# Pair sets are defined SYMBOLICALLY on the raw feature sets and are IDENTICAL across all four
# arms (they are arm-independent by construction, so no arm can be favoured by the pair choice).
pairs_all = [(VOCAB[i], VOCAB[j]) for i in range(NC) for j in range(i + 1, NC)]


def jac(a, b):
    A, B = CONCEPT_FEATURES[a], CONCEPT_FEATURES[b]
    return len(A & B) / len(A | B)


NEAR = [p for p in pairs_all if jac(*p) >= 0.5]
DISJOINT = [p for p in pairs_all if not (CONCEPT_FEATURES[p[0]] & CONCEPT_FEATURES[p[1]])]
rng = random.Random(20260813)
RANDOM = rng.sample(pairs_all, 2000)
RANDOM_DISJOINT = rng.sample(DISJOINT, 2000)
OUT["c_pair_sets"] = {
    "n_pairs_total": len(pairs_all), "n_near_jaccard_ge_0.5": len(NEAR),
    "n_random_uniform": len(RANDOM), "n_disjoint_total": len(DISJOINT),
    "n_random_disjoint": len(RANDOM_DISJOINT),
    "near_examples": [list(p) for p in NEAR[:8]],
}

CACHE = {}
def vec(word, weighted, norm):
    key = (word, weighted, norm)
    if key not in CACHE:
        CACHE[key] = (vec_percomp(word, weighted) if norm == "PERCOMP"
                      else vec_l2(word, weighted))
    return CACHE[key]


def arm(weighted, norm):
    def sims(ps):
        return np.array([cos_general(vec(a, weighted, norm), vec(b, weighted, norm))
                         for a, b in ps])
    n_, r_, rd_ = sims(NEAR), sims(RANDOM), sims(RANDOM_DISJOINT)

    def dprime(x, y):
        sd = math.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2.0)
        return float((x.mean() - y.mean()) / sd) if sd > 0 else float("nan")
    return {
        "near_mean": float(n_.mean()), "near_sd": float(n_.std(ddof=1)),
        "random_mean": float(r_.mean()), "random_sd": float(r_.std(ddof=1)),
        "separation_near_minus_random": float(n_.mean() - r_.mean()),
        "dprime_near_vs_random": dprime(n_, r_),
        "random_disjoint_mean": float(rd_.mean()),
        "separation_near_minus_disjoint": float(n_.mean() - rd_.mean()),
        "dprime_near_vs_disjoint": dprime(n_, rd_),
    }


OUT["c_arms"] = {
    "UNWEIGHTED|PERCOMP_RENORM(hdlab bundle)": arm(False, "PERCOMP"),
    "LOGIDF|PERCOMP_RENORM(hdlab bundle)": arm(True, "PERCOMP"),
    "UNWEIGHTED|WHOLE_VECTOR_L2": arm(False, "L2"),
    "LOGIDF|WHOLE_VECTOR_L2": arm(True, "L2"),
}
for k in ("dprime_near_vs_random", "dprime_near_vs_disjoint", "separation_near_minus_random"):
    OUT.setdefault("c_weighting_gain_logidf_minus_unweighted", {})[k] = {
        "PERCOMP_RENORM": round(OUT["c_arms"]["LOGIDF|PERCOMP_RENORM(hdlab bundle)"][k]
                                - OUT["c_arms"]["UNWEIGHTED|PERCOMP_RENORM(hdlab bundle)"][k], 4),
        "WHOLE_VECTOR_L2": round(OUT["c_arms"]["LOGIDF|WHOLE_VECTOR_L2"][k]
                                 - OUT["c_arms"]["UNWEIGHTED|WHOLE_VECTOR_L2"][k], 4),
    }

# ---- scale-invariance check named in OUT["weights"]["note"] -----------------------------------
W_SCALED = {f: 3.7 * v for f, v in W.items()}
_Wsave = dict(W)
W.update(W_SCALED)
CACHE.clear()
scaled_arm_pc = arm(True, "PERCOMP")["dprime_near_vs_random"]
scaled_arm_l2 = arm(True, "L2")["dprime_near_vs_random"]
W.clear(); W.update(_Wsave); CACHE.clear()
OUT["weights"]["scale_invariance_check_dprime_with_weights_x3.7"] = {
    "PERCOMP": scaled_arm_pc, "L2": scaled_arm_l2,
    "unscaled_PERCOMP": OUT["c_arms"]["LOGIDF|PERCOMP_RENORM(hdlab bundle)"]["dprime_near_vs_random"],
    "unscaled_L2": OUT["c_arms"]["LOGIDF|WHOLE_VECTOR_L2"]["dprime_near_vs_random"],
}

print(json.dumps(OUT, indent=2))
with open("D:/AI/hd-instrument/scratch/percomp_renorm_probe_out.json", "w") as fh:
    json.dump(OUT, fh, indent=2)
