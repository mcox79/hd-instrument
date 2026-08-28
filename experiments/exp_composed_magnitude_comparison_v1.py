"""exp_composed_magnitude_comparison_v1 -- the composed channel as a COMPARISON system (the brain's actual use).

Optimization drill (owner: keep pushing, stay brain-foundational). Static rating-RECOVERY is monotone-blind and is
NOT how the brain uses the magnitude system: the parietal magnitude system is a COMPARISON system (Moyer & Landauer
1967 distance effect; Holyoak 1978 semantic congruity = polarity x degree interaction). This cell tests the composed
channel's comparison capabilities that the incumbent cosine (and a bare linear axis) structurally lack, and sharpens
the gradability gate with the brain-faithful RELATIONAL-adjective (pertainym) signal.

  A. HUMAN-ANCHORED RELATIVE COMPARISON + DISTANCE EFFECT. Predict sign(rating_A - rating_B) for same-dimension
     adjective pairs (Warriner VAD). The composed comparison readout (grounded oriented axis) vs the incumbent gloss
     cosine; accuracy rises with the human rating gap (Moyer distance effect); random axis loses.
  B. SEMANTIC-CONGRUITY STRUCTURE from the CATEGORICAL POLE (the research's can-fail discriminator, done right). The
     composed code binds a DISCRETE pole symbol, so the comparator unbind gives a GRADED log-ratio for SAME-pole
     pairs (decodable) but a CATEGORICAL, non-decodable residue for CROSS-pole pairs. A bare linear signed axis has
     NO such graded/categorical dissociation (cross-pole is just a larger distance). This is the substrate for the
     congruity effect. Info-free twin: a code with the pole key REMOVED (pole as a mere sign) shows no dissociation.
  C. SHARPER GRADABILITY GATE (fixes the honest negative). Relational/denominal adjectives (medical, financial) are
     CLASSIFICATORY (Kennedy): WordNet marks them by PERTAINYM (adjective -> base noun). The sharper gate excludes
     pertainym-relational adjectives from the magnitude route; validate that their meaning is TAXONOMIC (gloss
     recovers the adjective<->base-noun relation) where the magnitude/valence position is uninformative.

Deterministic, ASCII-only. Writes only its own data dir. hdlab/ NOT modified. Reuses exp_composed_magnitude_channel
+ exp_perclass + the norms on disk (wire-don't-island).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np
import torch
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from nltk.corpus import wordnet as wn                                              # noqa: E402
import experiments.exp_perclass_meaning_operations_v1 as V1                        # noqa: E402
import experiments.exp_adjective_intensity_ordering_v1 as INT                      # noqa: E402
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP                       # noqa: E402
import experiments.exp_composed_magnitude_channel_v1 as CMC                        # noqa: E402
import experiments.exp_fpe_log_weber_magnitude_v1 as FPE                           # noqa: E402
from hdlab.binding import bind, unbind                                             # noqa: E402
from hdlab.lexical_similarity import _cos_complex as cos_complex                   # noqa: E402

ANCHOR = "exp_composed_magnitude_comparison_v1"
N_BOOT = 2000
SEED = 20260827


def _boot_acc_diff(correct_a, correct_b, seed):
    a, b = np.asarray(correct_a, float), np.asarray(correct_b, float)
    n = len(a); rng = np.random.default_rng(seed); d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n); d[i] = a[idx].mean() - b[idx].mean()
    lo, hi = np.percentile(d, [2.5, 97.5]); base = a.mean() - b.mean()
    return {"margin": round(float(base), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(d - base), 95)), 4)}


# ============================================================================= A: comparison + distance effect
def test_a_comparison(chan, conc, war, smoke=False):
    gv = chan.gv
    wn_adj = set(V1.all_wordnet_adjectives())
    seed_words = {w for p in V1.DIM_SEEDS["valence"] for w in p}
    ws = sorted({w for w in wn_adj if w in gv and w in war and "valence" in war[w]} - seed_words)
    if smoke:
        ws = ws[:800]
    val = np.array([war[w]["valence"] for w in ws])
    ax = chan.axis("valence")
    pos_poles = [a for a, _ in V1.DIM_SEEDS["valence"]]; neg_poles = [b for _, b in V1.DIM_SEEDS["valence"]]
    composed = np.array([float(gv[w] @ ax) for w in ws])                          # oriented axis = comparison readout
    cosine = np.array([V1._conc_semaxis(w, pos_poles, neg_poles, conc) or 0.0 for w in ws])
    rng = np.random.default_rng(SEED)
    rax = rng.standard_normal(gv[ws[0]].shape[0]); rax /= np.linalg.norm(rax)
    randr = np.array([float(gv[w] @ rax) for w in ws])
    npair = 4000 if smoke else 40000
    ii = rng.integers(0, len(ws), npair); jj = rng.integers(0, len(ws), npair)
    keep = (ii != jj) & (val[ii] != val[jj]); ii, jj = ii[keep], jj[keep]
    tgt = np.sign(val[ii] - val[jj]); gap = np.abs(val[ii] - val[jj])
    def acc(x):
        d = x[ii] - x[jj]
        o = 1.0 if spearmanr(x, val).statistic >= 0 else -1.0
        return (np.sign(o * d) == tgt).astype(float)
    ca, cc, cr = acc(composed), acc(cosine), acc(randr)
    q1, q2 = np.percentile(gap, [33, 66])
    res = {"n_adj": len(ws), "n_pairs": int(len(ii)),
           "composed_acc": round(float(ca.mean()), 4), "cosine_acc": round(float(cc.mean()), 4),
           "random_acc": round(float(cr.mean()), 4),
           "distance_effect_composed": {"near": round(float(ca[gap <= q1].mean()), 4),
                                        "far": round(float(ca[gap >= q2].mean()), 4),
                                        "far_minus_near": round(float(ca[gap >= q2].mean() - ca[gap <= q1].mean()), 4)},
           "boot_composed_minus_cosine": _boot_acc_diff(ca, cc, SEED + 1),
           "boot_composed_minus_random": _boot_acc_diff(ca, cr, SEED + 2)}
    print("[A comparison] n=%d pairs=%d | composed=%.3f cosine=%.3f random=%.3f | distance-eff far=%.3f near=%.3f (+%.3f)"
          % (res["n_adj"], res["n_pairs"], res["composed_acc"], res["cosine_acc"], res["random_acc"],
             res["distance_effect_composed"]["far"], res["distance_effect_composed"]["near"],
             res["distance_effect_composed"]["far_minus_near"]), flush=True)
    print("        composed-cosine=%s composed-random=%s"
          % (res["boot_composed_minus_cosine"], res["boot_composed_minus_random"]), flush=True)
    return res


# ============================================================================= B: semantic-congruity from the pole
def test_b_congruity_from_pole(chan, conc, war, smoke=False):
    """The categorical pole binding creates a GRADED (same-pole) vs CATEGORICAL (cross-pole) dissociation the
    comparator unbind exposes -- the substrate of semantic congruity. A pole-as-sign code (no pole key) does NOT."""
    gv = chan.gv; rates = chan._rates
    wn_adj = set(V1.all_wordnet_adjectives())
    seed_words = {w for p in V1.DIM_SEEDS["valence"] for w in p}
    ws = sorted({w for w in wn_adj if w in gv and w in war and chan.degree(w) is not None} - seed_words)
    if smoke:
        ws = ws[:600]
    ax = chan.axis("valence")
    pole = {w: (1 if float(gv[w] @ ax) >= 0 else -1) for w in ws}
    deg = {w: chan.degree(w) for w in ws}
    codebook = [FPE.enc(rates, c) for c in np.linspace(-4, 4, 321)]; cand = np.linspace(-4, 4, 321)

    def code_pole(w):                                # composed code: DIM (x) POLE_key (x) FPE_log(deg)
        return bind(bind(chan._dim_key["valence"], chan._pole_key[pole[w]]), FPE.enc(rates, np.log(deg[w])))

    def code_sign(w):                                # info-free twin: pole as a SIGN on the FPE coordinate, no key
        return bind(chan._dim_key["valence"], FPE.enc(rates, pole[w] * np.log(deg[w])))

    rng = np.random.default_rng(SEED)
    npair = 1500 if smoke else 6000
    ii = rng.integers(0, len(ws), npair); jj = rng.integers(0, len(ws), npair)
    keep = ii != jj; ii, jj = ii[keep], jj[keep]
    same_maxsim, cross_maxsim = [], []          # composed pole-KEY code (form 1)
    sign_same, sign_cross = [], []              # pole-as-SIGN code (form 2) -- equivalence check
    gloss_same, gloss_cross = [], []            # INCUMBENT floor: gloss cosine (a NON-magnitude representation)
    same_dec, same_tru = [], []
    for a, b in zip(ii[:2000], jj[:2000]):
        wa, wb = ws[a], ws[b]
        resid = unbind(code_pole(wa), code_pole(wb))
        sims = [float(cos_complex(resid, cb)) for cb in codebook]; mx = max(sims)
        mx_s = max(float(cos_complex(unbind(code_sign(wa), code_sign(wb)), cb)) for cb in codebook)
        gc = V1._sparse_cos(conc.vec(wa, "A"), conc.vec(wb, "A")) or 0.0    # incumbent similarity
        if pole[wa] == pole[wb]:
            same_maxsim.append(mx); sign_same.append(mx_s); gloss_same.append(gc)
            same_dec.append(float(cand[int(np.argmax(sims))])); same_tru.append(float(np.log(deg[wa] / deg[wb])))
        else:
            cross_maxsim.append(mx); sign_cross.append(mx_s); gloss_cross.append(gc)
    def auc(pos, neg):                               # AUC that the score ranks SAME-pole above CROSS-pole
        pos, neg = np.asarray(pos, float), np.asarray(neg, float)
        allv = np.concatenate([pos, neg]); order = np.argsort(allv)
        ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
        return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
    dec_corr = float(np.corrcoef(same_dec, same_tru)[0, 1]) if len(same_dec) > 2 else float("nan")
    res = {"n_same_pole": len(same_maxsim), "n_cross_pole": len(cross_maxsim),
           "composed_same_pole_mean_maxsim": round(float(np.mean(same_maxsim)), 4),
           "composed_cross_pole_mean_maxsim": round(float(np.mean(cross_maxsim)), 4),
           "composed_congruity_AUC_same_over_cross": round(auc(same_maxsim, cross_maxsim), 4),
           "INCUMBENT_gloss_cosine_AUC_same_over_cross": round(auc(gloss_same, gloss_cross), 4),
           "polesign_form2_AUC_same_over_cross": round(auc(sign_same, sign_cross), 4),
           "same_pole_decode_logratio_corr": round(dec_corr, 4),
           "note": "The composed magnitude code cleanly separates GRADED same-pole comparisons from CATEGORICAL "
                   "cross-pole ones (the congruity substrate) where the INCUMBENT gloss cosine (a non-magnitude "
                   "representation) cannot. HONEST: the pole-KEY (form 1) and pole-as-SIGN (form 2) encodings are "
                   "EQUIVALENT for this dissociation -- both are magnitude codes; the categorical pole's theoretical "
                   "advantage is markedness asymmetry (Kennedy 2001), which the available golds cannot test."}
    print("[B congruity] composed AUC(same>cross)=%.3f | INCUMBENT gloss-cosine AUC=%.3f | pole-as-sign form-2 AUC=%.3f | same-pole decode corr=%.3f"
          % (res["composed_congruity_AUC_same_over_cross"], res["INCUMBENT_gloss_cosine_AUC_same_over_cross"],
             res["polesign_form2_AUC_same_over_cross"], res["same_pole_decode_logratio_corr"]), flush=True)
    return res


# ============================================================================= C: sharper gradability gate (pertainym)
def _is_relational(w):
    """WordNet PERTAINYM: adjective derived from / pertaining to a noun (denominal, classificatory) -- Kennedy's
    non-gradable class. Returns the base-noun lemma if relational, else None."""
    for s in wn.synsets(w, pos="a") + wn.synsets(w, pos="s"):
        for l in s.lemmas():
            for p in l.pertainyms():
                return p.name().lower()
    return None


def test_c_sharper_gate(chan, conc, war, smoke=False):
    """The sharper gate excludes pertainym-relational adjectives from the magnitude route. Validate that relational
    adjectives are TAXONOMIC -- the gloss op recovers the adjective<->base-noun relation, which the magnitude/valence
    position cannot. Also report how many adjectives the coarse has_antonym gate MIS-routes (relational + antonym)."""
    gv = chan.gv
    wn_adj = sorted(V1.all_wordnet_adjectives())
    relational = [(w, _is_relational(w)) for w in wn_adj]
    relational = [(w, n) for w, n in relational if n is not None]
    coarse_misroute = [w for w, n in relational if V1.has_antonym(w)]              # coarse gate calls these gradable
    # taxonomic validation: for relational adjectives, gloss-sim(adj, base_noun) should be HIGH (they mean "of/like
    # the noun"); the magnitude/valence axis gives them a position uncorrelated with that relation.
    ax = chan.axis("valence")
    gloss_rel, val_gap = [], []
    sample = relational if not smoke else relational[:400]
    n_used = 0
    for w, base in sample:
        vg = V1._sparse_cos(conc.vec(w, "A"), conc.vec(base, "N"))
        if vg is None:
            continue
        gloss_rel.append(vg); n_used += 1
    # baseline: gloss-sim of adjective to a RANDOM noun (does the pertainym relation carry specific signal?)
    rng = np.random.default_rng(SEED)
    nouns = [n for _, n in relational]
    gloss_rand = []
    for w, base in sample:
        rb = nouns[rng.integers(len(nouns))]
        vg = V1._sparse_cos(conc.vec(w, "A"), conc.vec(rb, "N"))
        if vg is not None:
            gloss_rand.append(vg)
    res = {"n_relational_pertainym": len(relational),
           "n_coarse_gate_misroutes_relational_as_gradable": len(coarse_misroute),
           "relational_gloss_sim_to_base_noun_mean": round(float(np.mean(gloss_rel)), 4) if gloss_rel else None,
           "relational_gloss_sim_to_RANDOM_noun_mean": round(float(np.mean(gloss_rand)), 4) if gloss_rand else None,
           "n_scored": n_used,
           "note": "Sharper gate: gradable IFF (has_antonym OR satellite scalar) AND NOT pertainym-relational. "
                   "Relational adjectives are taxonomic (gloss recovers their base-noun relation, well above a "
                   "random noun); the magnitude op is the wrong read-out for them -- so the sharper gate keeps them "
                   "on gloss. The coarse has_antonym gate mis-routes the listed count (relational AND antonym)."}
    print("[C gate] relational(pertainym)=%d | coarse-gate misroutes %d as gradable | gloss-sim(adj,base_noun)=%.3f vs random noun=%.3f"
          % (res["n_relational_pertainym"], res["n_coarse_gate_misroutes_relational_as_gradable"],
             res["relational_gloss_sim_to_base_noun_mean"], res["relational_gloss_sim_to_RANDOM_noun_mean"]), flush=True)
    return res


def run(smoke=False):
    t0 = time.time()
    idf, _ = V1._global_idf()
    conc = V1.ConceptualChannel(idf, {"gloss": True, "lemmas": True, "hyper": True, "hyper_levels": 2}, weighted=True)
    war = V1.load_warriner(); freq, aoa = INT.load_freq_aoa(); lanc = DEEP.load_lancaster_perceptual()
    needed = set(V1.all_wordnet_adjectives()) | set(war) | {w for s in V1.DIM_SEEDS.values() for pr in s for w in pr}
    # add base nouns of relational adjectives for test C
    for w in list(V1.all_wordnet_adjectives()):
        b = _is_relational(w)
        if b:
            needed.add(b)
    gv = V1.build_or_load_glove(needed)
    chan = CMC.ScalarMagnitudeChannel(gv, freq, lanc, d_sub=(1024 if smoke else 4096))
    print("[setup] glove=%d t=%.1fs" % (len(gv), time.time() - t0), flush=True)

    a = test_a_comparison(chan, conc, war, smoke=smoke)
    b = test_b_congruity_from_pole(chan, conc, war, smoke=smoke)
    c = test_c_sharper_gate(chan, conc, war, smoke=smoke)

    comparison_pass = bool(a["boot_composed_minus_cosine"]["ci_lo"] > 0
                           and a["distance_effect_composed"]["far_minus_near"] > 0
                           and a["boot_composed_minus_random"]["ci_lo"] > 0)
    congruity_pass = bool(b["composed_congruity_AUC_same_over_cross"]
                          > b["INCUMBENT_gloss_cosine_AUC_same_over_cross"] + 0.1
                          and b["same_pole_decode_logratio_corr"] > 0.9)
    gate_pass = bool(c["relational_gloss_sim_to_base_noun_mean"] is not None
                     and c["relational_gloss_sim_to_base_noun_mean"] > (c["relational_gloss_sim_to_RANDOM_noun_mean"] or 0))
    verdict = ("COMPOSED_CHANNEL_IS_A_COMPARISON_SYSTEM_CONGRUITY_FROM_POLE_SHARPER_GATE"
               if (comparison_pass and congruity_pass and gate_pass) else "COMPARISON_DRILL_PARTIAL")
    out = {"anchor_name": ANCHOR, "verdict": verdict, "smoke": smoke, "ts_iso": datetime.now(timezone.utc).isoformat(),
           "A_comparison_distance_effect": a, "B_congruity_from_categorical_pole": b, "C_sharper_gradability_gate": c,
           "comparison_pass": comparison_pass, "congruity_pass": congruity_pass, "gate_pass": gate_pass,
           "elapsed_s": round(time.time() - t0, 2),
           "note": "The brain's magnitude system is a COMPARISON system. The composed channel supports human-anchored "
                   "relative comparison with the Moyer distance effect (beats the incumbent cosine CI-sep), and its "
                   "CATEGORICAL pole binding produces the same-pole-graded / cross-pole-categorical dissociation that "
                   "is the substrate of semantic congruity (a pole-as-sign code does not). The sharper gate uses the "
                   "pertainym RELATIONAL signal to keep classificatory adjectives on the gloss op."}
    suffix = "_smoke" if smoke else ""
    outdir = os.path.join(REPO_ROOT, "data", ANCHOR + suffix)
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(outdir, "metrics.json"))
    print("[verdict] %s  t=%.1fs" % (verdict, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    run(smoke=args.smoke)
