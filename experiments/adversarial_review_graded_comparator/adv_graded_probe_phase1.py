"""ADVERSARIAL probe of exp_graded_divisive_comparator_v1 smoke n=600. READ-ONLY.

Re-derives the item set / anchors / queries with the cell's own imported code, then attacks:
  P0  independent re-derivation of the headline accuracies
  P1  tie rates + max delta attributable to alphabetical tie-breaking
  P2  nuisance channel: profile-sentence COUNT asymmetry (target vs distractor)
  P3  nuisance channel: anchor NORM / total-content-word-count
  P4  sentence LENGTH channel
  P5  zero rows / near-zero norms / zero-component fraction per anchor matrix
  P6  scrambled-floor decomposition (why below chance)
  P7  item-set symmetry (both orders present?) and B_FREQ == 0.5000 exactly
  P8  pool-statistic leakage: recompute A_GGZ using mu/sd from DISJOINT non-candidate words
  P9  delta on nuisance-balanced subsets
Writes nothing outside scratch/.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import numpy as np

REPO = "D:/AI/hd-instrument"
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT
import experiments.exp_graded_divisive_comparator_v1 as G
from hdlab.reading_grounding_loop import CTX_D, normalize_lemma
from hdlab.grounding_acquisition_loop import content_words

OUT = {}
print("CTX_D =", CTX_D)

MAXI = 600
assets = PARENT.build_corpus_assets()
counts = assets["counts"]
profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
items, item_diag = PARENT.build_items(assets["pairs_strict"], eval_pool, MAXI)
n = len(items)
print("[items] n=%d distinct_targets=%d" % (n, item_diag["distinct_target_words"]))

words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
wpos = {w: i for i, w in enumerate(words_used)}
nw = len(words_used)
print("[anchors] nw=%d" % nw)

# ---------------- anchors, exactly as the cell builds them -----------------------------------
sum_S = np.zeros((nw, CTX_D))
sum_G = np.zeros((nw, CTX_D))
n_prof_sent = 0
qs_S = np.zeros(CTX_D); qs_S2 = np.zeros(CTX_D)
qs_G = np.zeros(CTX_D); qs_G2 = np.zeros(CTX_D)
prof_sent_count = {}     # word -> n profile sentences used
prof_word_count = {}     # word -> total kept content words across profile sentences
for i, w in enumerate(words_used):
    drop = frozenset({w})
    ss = profile_pool.get(w, ())
    prof_sent_count[w] = len(ss)
    twc = 0
    for sent in ss:
        vs = G._signed(sent, drop)
        vg = G._graded(sent, drop)
        twc += len(G._kept_words(sent, drop))
        sum_S[i] += vs
        sum_G[i] += vg
        qs_S += vs; qs_S2 += vs * vs
        qs_G += vg; qs_G2 += vg * vg
        n_prof_sent += 1
    prof_word_count[w] = twc
print("[anchors] profile sentences =", n_prof_sent)

ANCH = {("S", "S"): np.stack([G._sign_anchor(sum_S[i]) for i in range(nw)]),
        ("S", "G"): sum_S,
        ("G", "S"): np.stack([G._sign_anchor(sum_G[i]) for i in range(nw)]),
        ("G", "G"): sum_G}

m = max(1, n_prof_sent)
QMU = {"S": qs_S / m, "G": qs_G / m}
QSD = {"S": np.sqrt(np.maximum(qs_S2 / m - QMU["S"] ** 2, 0.0)),
       "G": np.sqrt(np.maximum(qs_G2 / m - QMU["G"] ** 2, 0.0))}

# ---------------- queries ----------------------------------------------------------------------
donors = PARENT.assign_donors(items)
Q, QS = {}, {}
qlen = np.zeros(n, dtype=np.int64)          # kept content words in the real query
for enc, fn in (("S", G._signed), ("G", G._graded)):
    real = np.zeros((n, CTX_D)); scram = np.zeros((n, CTX_D))
    for i, it in enumerate(items):
        drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                          it["target"], it["distractor"]})
        real[i] = fn(it["sentence"], drop)
        if enc == "S":
            qlen[i] = len(G._kept_words(it["sentence"], drop))
        d = items[donors[i]]
        dd = drop | frozenset({normalize_lemma(d["target"]), normalize_lemma(d["distractor"]),
                               d["target"], d["distractor"]})
        scram[i] = fn(d["sentence"], dd)
    Q[enc] = real; QS[enc] = scram

# mask-set identity between arms (code-level check made numeric)
mask_ident = True
for i, it in enumerate(items[:200]):
    drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                      it["target"], it["distractor"]})
    if G._kept_words(it["sentence"], drop) != G._kept_words(it["sentence"], drop):
        mask_ident = False
OUT["mask_sets_identical_between_arms"] = mask_ident


def score(A, Qa, tie_mode="alpha", rng=None):
    """returns (correct bool array, margins, tie idx list)"""
    corr = np.zeros(n, dtype=bool)
    marg = np.zeros(n)
    ties = []
    for i, it in enumerate(items):
        pair = np.array([wpos[it["target"]], wpos[it["distractor"]]], dtype=np.int64)
        s = G._cos_rows(Qa[i], A[pair])
        st, sd = float(s[0]), float(s[1])
        marg[i] = st - sd
        if st == sd:
            ties.append(i)
            if tie_mode == "alpha":
                corr[i] = (it["target"] < it["distractor"])
            elif tie_mode == "coin":
                corr[i] = bool(rng.integers(2) == 0)
            elif tie_mode == "wrong":
                corr[i] = False
            else:
                corr[i] = True
        else:
            corr[i] = st > sd
    return corr, marg, ties


def arm(enc, agg, nm, scrambled=False, tie_mode="alpha", rng=None,
        amu=None, asd=None):
    A0 = ANCH[(enc, agg)]
    _amu = A0.mean(axis=0) if amu is None else amu
    _asd = A0.std(axis=0) if asd is None else asd
    A = G._normalise(A0, _amu, _asd, "Z" if nm == "ZA" else nm)
    qmode = "N" if nm == "ZA" else nm
    src = QS[enc] if scrambled else Q[enc]
    Qa = G._normalise(src, QMU[enc], QSD[enc], qmode)
    return score(A, Qa, tie_mode=tie_mode, rng=rng)


# ---------------- P0 re-derivation --------------------------------------------------------------
ref = json.load(open(os.path.join(REPO, "data",
                                  "exp_graded_divisive_comparator_v1_SMOKE_n600",
                                  "metrics.json")))
rederived = {}
for enc in ("S", "G"):
    for agg in ("S", "G"):
        for nm in ("N", "C", "Z", "ZA"):
            c, mg, ties = arm(enc, agg, nm)
            k = "A_%s%s%s" % (enc, agg, nm)
            rederived[k] = (round(float(c.mean()), 6), len(ties))
cS, mS, tS = arm("S", "S", "N", scrambled=True)
cG, mG, tG = arm("G", "G", "Z", scrambled=True)
rederived["F_SSN_SCRAM"] = (round(float(cS.mean()), 6), len(tS))
rederived["F_GGZ_SCRAM"] = (round(float(cG.mean()), 6), len(tG))
mismatch = {k: (v[0], ref["arm_accuracy"].get(k)) for k, v in rederived.items()
            if abs(v[0] - ref["arm_accuracy"].get(k, -9)) > 1e-9}
OUT["P0_rederived"] = {k: v[0] for k, v in rederived.items()}
OUT["P0_mismatch_vs_metrics_json"] = mismatch
OUT["P0_tie_counts"] = {k: v[1] for k, v in rederived.items()}
print("[P0] mismatches:", mismatch)

live_c, live_m, live_t = arm("S", "S", "N")
prim_c, prim_m, prim_t = arm("G", "G", "Z")
delta = float(prim_c.mean() - live_c.mean())
OUT["P0_delta_rederived"] = round(delta, 6)
print("[P0] LIVE=%.4f PRIMARY=%.4f delta=%.4f" % (live_c.mean(), prim_c.mean(), delta))

# ---------------- P1 ties ------------------------------------------------------------------------
tie_res = {}
for nm, tm in (("alpha", "alpha"), ("all_wrong", "wrong"), ("all_right", "right")):
    lc, _, lt = arm("S", "S", "N", tie_mode=tm)
    pc, _, pt = arm("G", "G", "Z", tie_mode=tm)
    tie_res[nm] = {"live": round(float(lc.mean()), 6), "primary": round(float(pc.mean()), 6),
                   "delta": round(float(pc.mean() - lc.mean()), 6),
                   "n_ties_live": len(lt), "n_ties_primary": len(pt)}
# expected coin value = midpoint of all_wrong / all_right
tie_res["alpha_tiebreak_correct_count_live"] = int(sum(
    1 for i in live_t if items[i]["target"] < items[i]["distractor"]))
tie_res["max_possible_delta_shift_from_ties"] = round(
    (len(live_t) + len(prim_t)) / float(n), 6)
OUT["P1_ties"] = tie_res
print("[P1]", json.dumps(tie_res))

# ---------------- P2 profile-count nuisance ------------------------------------------------------
pc_t = np.array([prof_sent_count[it["target"]] for it in items])
pc_d = np.array([prof_sent_count[it["distractor"]] for it in items])
pick_more = (pc_t > pc_d)
tie_pc = (pc_t == pc_d)
OUT["P2_profile_counts"] = {
    "target_mean": float(pc_t.mean()), "distractor_mean": float(pc_d.mean()),
    "target_min": int(pc_t.min()), "distractor_min": int(pc_d.min()),
    "frac_target_gt_distractor": float((pc_t > pc_d).mean()),
    "frac_equal": float(tie_pc.mean()),
    "acc_of_pick_more_profile_sentences": float(
        (pick_more[~tie_pc]).mean()) if (~tie_pc).sum() else None,
    "n_unequal": int((~tie_pc).sum()),
}
print("[P2]", json.dumps(OUT["P2_profile_counts"]))

# ---------------- P3 anchor norm / total word count ----------------------------------------------
normG = np.linalg.norm(ANCH[("G", "G")], axis=1)
normS = np.linalg.norm(ANCH[("S", "S")], axis=1)
wc = np.array([prof_word_count[w] for w in words_used], dtype=np.float64)
ti = np.array([wpos[it["target"]] for it in items])
di = np.array([wpos[it["distractor"]] for it in items])
pick_bigger_G = normG[ti] > normG[di]
pick_bigger_wc = wc[ti] > wc[di]
OUT["P3_norms"] = {
    "corr_normG_vs_total_profile_words": float(np.corrcoef(normG, wc)[0, 1]),
    "acc_pick_larger_graded_anchor_norm": float(pick_bigger_G.mean()),
    "acc_pick_larger_total_profile_wordcount": float(pick_bigger_wc.mean()),
    "acc_pick_larger_sign_anchor_norm": float((normS[ti] > normS[di]).mean()),
    "graded_norm_min": float(normG.min()), "graded_norm_max": float(normG.max()),
}
# does the graded-arm margin track the norm ratio?
lr = np.log(normG[ti] / normG[di])
OUT["P3_norms"]["corr_primary_margin_vs_log_norm_ratio"] = float(np.corrcoef(prim_m, lr)[0, 1])
OUT["P3_norms"]["corr_live_margin_vs_log_norm_ratio"] = float(np.corrcoef(live_m, lr)[0, 1])
print("[P3]", json.dumps(OUT["P3_norms"]))

# ---------------- P4 sentence length -------------------------------------------------------------
slen = np.array([len(content_words(it["sentence"])) for it in items])
OUT["P4_length"] = {
    "qlen_mean": float(qlen.mean()), "qlen_min": int(qlen.min()), "qlen_max": int(qlen.max()),
    "corr_qlen_vs_live_correct": float(np.corrcoef(qlen, live_c.astype(float))[0, 1]),
    "corr_qlen_vs_primary_correct": float(np.corrcoef(qlen, prim_c.astype(float))[0, 1]),
    "corr_qlen_vs_delta_correct": float(np.corrcoef(
        qlen, prim_c.astype(float) - live_c.astype(float))[0, 1]),
    "acc_live_short_half": float(live_c[qlen <= np.median(qlen)].mean()),
    "acc_live_long_half": float(live_c[qlen > np.median(qlen)].mean()),
    "acc_primary_short_half": float(prim_c[qlen <= np.median(qlen)].mean()),
    "acc_primary_long_half": float(prim_c[qlen > np.median(qlen)].mean()),
    "sentence_content_words_mean": float(slen.mean()),
}
print("[P4]", json.dumps(OUT["P4_length"]))

# ---------------- P5 anchor-matrix degeneracy -----------------------------------------------------
deg = {}
for key, M in ANCH.items():
    nn = np.linalg.norm(M, axis=1)
    deg["%s%s" % key] = {"zero_rows": int((nn < 1e-9).sum()),
                         "near_zero_rows_lt_1e-6": int((nn < 1e-6).sum()),
                         "min_norm": float(nn.min()), "median_norm": float(np.median(nn)),
                         "frac_zero_components": float((M == 0.0).mean())}
OUT["P5_anchor_degeneracy"] = deg
# duplicate anchor rows (exact) in the ternary code -> forced ties
A_SS = ANCH[("S", "S")]
dup_pairs = 0
for i, it in enumerate(items):
    if np.array_equal(A_SS[wpos[it["target"]]], A_SS[wpos[it["distractor"]]]):
        dup_pairs += 1
OUT["P5_identical_candidate_anchor_rows_SS"] = dup_pairs
print("[P5]", json.dumps(deg), "identical_SS_pairs=", dup_pairs)

# ---------------- P6 scrambled floor ---------------------------------------------------------------
OUT["P6_scram"] = {
    "acc_scram_live": float(cS.mean()), "acc_scram_primary": float(cG.mean()),
    "mean_signed_margin_scram_live": float(mS.mean()),
    "mean_signed_margin_scram_primary": float(mG.mean()),
    "frac_items_where_distractor_anchor_more_generic_G": None,
}
# genericity: cosine of each anchor to the anchor-pool mean (after the same Z transform)
A0 = ANCH[("G", "G")]
Az = G._normalise(A0, A0.mean(axis=0), A0.std(axis=0), "Z")
pool_mean = Az.mean(axis=0)
gen = (Az @ pool_mean) / (np.linalg.norm(Az, axis=1) * np.linalg.norm(pool_mean) + 1e-12)
OUT["P6_scram"]["frac_items_where_distractor_anchor_more_generic_G"] = float(
    (gen[di] > gen[ti]).mean())
OUT["P6_scram"]["acc_scram_primary_on_items_where_target_more_generic"] = float(
    cG[gen[ti] > gen[di]].mean())
OUT["P6_scram"]["acc_scram_primary_on_items_where_distractor_more_generic"] = float(
    cG[gen[di] > gen[ti]].mean())
OUT["P6_scram"]["corr_scram_primary_margin_vs_genericity_diff"] = float(
    np.corrcoef(mG, gen[ti] - gen[di])[0, 1])
# does the donor sentence share the item's WordNet group?
print("[P6]", json.dumps(OUT["P6_scram"]))

# ---------------- P7 item symmetry ------------------------------------------------------------------
pairs_seen = {}
for it in items:
    a, b = it["target"], it["distractor"]
    pairs_seen.setdefault(tuple(sorted((a, b))), set()).add((a, b))
both = sum(1 for v in pairs_seen.values() if len(v) == 2)
OUT["P7_item_symmetry"] = {
    "n_distinct_unordered_pairs": len(pairs_seen),
    "n_pairs_with_both_orders": both,
    "n_items_in_symmetric_pairs": sum(len(v) for v in pairs_seen.values() if len(v) == 2),
    "freq_arm_acc": float(np.mean([counts.get(it["target"], 0) > counts.get(it["distractor"], 0)
                                   for it in items])),
    "n_freq_exact_ties": int(sum(1 for it in items
                                 if counts.get(it["target"], 0) == counts.get(it["distractor"], 0))),
}
print("[P7]", json.dumps(OUT["P7_item_symmetry"]))

# ---------------- P8 pool-statistic leakage --------------------------------------------------------
# rebuild anchor mu/sd from a DISJOINT set of words that are NOT candidates in any item
all_bucket_words = sorted(assets["buckets"].keys())
extra = [w for w in all_bucket_words if w not in wpos][:600]
sumG_x = np.zeros((len(extra), CTX_D))
for i, w in enumerate(extra):
    drop = frozenset({w})
    for sent in profile_pool.get(w, ()):
        sumG_x[i] += G._graded(sent, drop)
amu_x, asd_x = sumG_x.mean(axis=0), sumG_x.std(axis=0)
c_x, m_x, t_x = arm("G", "G", "Z", amu=amu_x, asd=asd_x)
OUT["P8_disjoint_pool_stats"] = {
    "n_extra_words": len(extra),
    "primary_acc_with_disjoint_anchor_pool_stats": round(float(c_x.mean()), 6),
    "primary_acc_original": round(float(prim_c.mean()), 6),
    "delta_vs_live_with_disjoint_stats": round(float(c_x.mean() - live_c.mean()), 6),
    "cos_between_mu_vectors": float(
        np.dot(amu_x, ANCH[("G", "G")].mean(axis=0)) /
        (np.linalg.norm(amu_x) * np.linalg.norm(ANCH[("G", "G")].mean(axis=0)) + 1e-12)),
}
print("[P8]", json.dumps(OUT["P8_disjoint_pool_stats"]))

# ---------------- P9 nuisance-balanced subsets -------------------------------------------------------
def sub(mask, name):
    if mask.sum() < 20:
        return {"n": int(mask.sum()), "note": "too few"}
    return {"n": int(mask.sum()),
            "live": round(float(live_c[mask].mean()), 6),
            "primary": round(float(prim_c[mask].mean()), 6),
            "delta": round(float(prim_c[mask].mean() - live_c[mask].mean()), 6),
            "scram_primary": round(float(cG[mask].mean()), 6)}
OUT["P9_subsets"] = {
    "profile_count_equal": sub(tie_pc, "eq"),
    "profile_count_unequal": sub(~tie_pc, "neq"),
    "target_has_more_profile_sents": sub(pc_t > pc_d, "t>d"),
    "target_has_fewer_profile_sents": sub(pc_t < pc_d, "t<d"),
    "target_anchor_norm_larger": sub(normG[ti] > normG[di], "n>"),
    "target_anchor_norm_smaller": sub(normG[ti] < normG[di], "n<"),
    "short_queries": sub(qlen <= np.median(qlen), "short"),
    "long_queries": sub(qlen > np.median(qlen), "long"),
}
print("[P9]", json.dumps(OUT["P9_subsets"], indent=1))

with open(os.path.join(REPO, "scratch", "adv_graded_phase1_out.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=float)
print("DONE")
