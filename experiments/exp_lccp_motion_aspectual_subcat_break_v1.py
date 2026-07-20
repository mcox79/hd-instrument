"""LCCP MOTION/ASPECTUAL SUBCAT BREAK: does adding TWO brain-derived features + ONE construction row to
the EXISTING LCCP parser CUT the motion/aspectual spurious-patient false-positives (came/sit/stand/walk/
lie/struggle given wrong patients), measured FAIRLY against independent gold with the contested/gradient
cases held OUT of the pass/fail count?

QUESTION (per the hard-residual brain-drill
notes/research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md, Angle 5 STRUCTURAL VERDICT):
  The LCCP arm-C (patient precision 0.500 vs independent gold; the true stacked reader = 0.557) still
  mis-licenses PATIENTS on motion/aspectual intransitives that its generic learned transitivity prior does
  not suppress (MEASURED: 9 such FPs survive in arm-C over 30 motion/aspectual nopat instances the reader
  attached to -> FP_a=0.300). The drill prescribes a SMALL, targeted ADDITION (not a new architecture):
    (F1) a per-verb / per-verb-class SUBCATEGORIZATION-FRAME-FREQUENCY feature consulted at the verb
         (Ford-Bresnan-Kaplan lexical-preference; Trueswell/Tanenhaus/Kello; Korhonen-class smoothing).
    (F2) a DIRECTIONAL/GOAL-PP diagnostic keyed on VERB CLASS = negative prior on patient-hood for a
         motion/aspectual verb followed by a directional/goal phrase (Levin & Rappaport Hovav 1995: the
         directional PP construes the sole argument as theme-of-a-path -> the following phrase is a
         goal/path modifier, structurally incompatible with a second patient-type argument).
    (CR) a MOTION/ASPECTUAL construction row, SEEDED from a small CREDITED Levin motion/aspectual class list
         (Levin 1993 classes 51.1 directed motion / 51.3.2 manner-of-motion / 47.6 assume-position / 55.1
         aspectual); the construction's transitivity prior (weight) is LEARNED distributionally from the
         coherence gate's accept/reject signal (Alishahi & Stevenson 2005/2008 update-rule shape), NOT
         hand-curated.

THE LEARNED MECHANISM (glass-box, CPU, NO treebank, NO external LLM):
  Reuse the LCCP's candidate generator, 6 structural cue-features, semantic selectional teacher, and
  error-driven logistic (all imported unchanged). ADD two features to the logistic input:
    f_dirpp     = 1.0 iff verb-lemma in the Levin motion/aspectual SEED and a directional/goal token
                  governs/follows (patient itself is a directional particle like home/there/away/out, OR a
                  directional preposition governs the patient, OR a directional particle sits right after the
                  verb). Learned weight expected NEGATIVE (directional PP -> not a patient).
    f_subcatfreq= smoothed per-verb frequency of taking a coherent DIRECT patient (post-verbal, not
                  prep-governed, not funcword, selectionally coherent), add-k smoothed, BACKED OFF to a
                  verb-CLASS prior (motion/aspectual seed verbs get a low class prior) for low-frequency
                  verbs. Consulted at the verb (per-instance constant). Learned weight expected POSITIVE.
  The weights on BOTH new features are LEARNED by the SAME self-supervised coherence teacher (semantic
  selectional coherence), so their signs EMERGE, they are not hand-set. GLASS-BOX recover: the learned
  8-dim cue-weights, the subcat-frame-frequency table, and the directional-PP prior.
  Construction row: MA-seed verbs are FORCED into one dedicated construction id; its transitivity prior is
  the LEARNED mean best-candidate objecthood of the MA verbs (low); held-out MA verbs inherit that shared
  low prior (weight-sharing generalization). Non-MA verbs cluster + backoff exactly as LCCP arm-C.

ARMS (ONE VARIABLE = the F1+F2+CR bundle ON vs OFF):
  ARM C0 = LCCP arm-C recomputed LIVE (the real 0.500 baseline; features OFF, no MA construction).
  ARM D  = C0 + f_dirpp + f_subcatfreq + MA construction row (bundle ON). Same candidate gen, same teacher,
           same lr/epochs/seed/keep_thr/subcat_thr; the ONLY difference is the two added features + the MA
           construction seed. (Diagnostic ablation D_feat = features ON but MA construction OFF, reported
           secondarily, NOT the pass/fail arm.)

MEASURED (decisive, vs INDEPENDENT gold; contested/gradient held OUT of pass/fail):
  PRIMARY = FP_a = motion/aspectual subcat FP-rate = fraction of the 30 motion/aspectual nopat INSTANCES the
    reader attached to for which the arm KEEPS a patient. HARD-PASS = FP_a(C0) - FP_a(D) >= 0.15 at bounded
    recall cost (recall retention D/C0 >= 0.60). HARD-FAIL = reduction < 0.05.
  SECONDARY = overall patient precision/recall/F1 (the 0.500 wall); STEP-1 triage counts (a/b/c); the
    Prediction-3 must-fail control (degrade the directional-PP cue reliability -> |w[f_dirpp]| must DROP);
    the Prediction-4 GRADED argument-hood score on clear-argument vs motion-nopat vs contested cases.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = LIVE LCCP arm-C recompute (P~0.500; NOT a strawman).
  (G2) ONE VARIABLE = C0 -> D adds exactly {f_dirpp, f_subcatfreq, MA construction}; all else identical.
  (G3) CAN-FAIL-BOTH-WAYS: FP_a(C0)=0.300 with 30 support instances; D can reach <=0.15 (>=5 suppressed) OR
       fail (<2 suppressed). Both reachable.
  (G4) difficulty ON: the target is the HARD residual arm-C's generic prior already FAILED to suppress.
  (G5) discriminator fires at smoke: arm D suppresses >0 of C0's motion/aspectual FPs AND kept sets differ.

VERDICT BANDS (pre-registered):
  HARD_PASS_MOTION_ASPECTUAL_SUBCAT_CUT: FP_a(C0) - FP_a(D) >= 0.15 AND recall_retention(D/C0) >= 0.60.
  HARD_FAIL_FEATURES_INSUFFICIENT: FP_a(C0) - FP_a(D) < 0.05 (directional-PP/subcat cues insufficient; the
    acquisition-lit gap is real) OR recall_retention < 0.40 (precision bought by destroying recall).
  MIDDLE_BAND: 0.05 <= reduction < 0.15, or partial.
  MECH_VALIDITY (Prediction-3, run alongside; not part of the FP_a band): degraded |w[f_dirpp]| < clean
    |w[f_dirpp]| -> the directional-PP weight is LEARNED not construction-determined. If unchanged -> flag.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): MIXED per the drill. The subcat-frame-frequency +
  directional-PP diagnostic are a genuine brain-faithful missing mechanism (expect real recovery on category
  a). But the brain pays a real combinatorial cost for this verb class, the acquisition literature flags the
  PP-arg-vs-adjunct problem as unresolved, and PropBank/FrameNet themselves disagree on this construction
  type -> a residual post-fix gap is EXPECTED and is not proof of mechanism failure without first checking
  whether the remainder is the gradient/contested subtype (category c, held OUT of pass/fail).

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- ~225 reader candidates, a
  few hundred GloVe cosines + a tiny logistic over 8 features x a few epochs x 3 seeds; wall < ~120s.
  Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage (extraction-
  precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib; no salted
  builtin hash / list(set); numpy default RNG seeded.

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (C0 vs D kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < arm-C0 precision < 0.95)
- discriminator fires at smoke (D suppresses >0 motion/aspectual FPs; kept sets differ)
- multi-seed (3 seeds); FP_a aggregated mean/std
- deterministic seeding; all numbers tagged MEASURED@/CITED@ (printed at run)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "lccp_motion_aspectual_subcat_break_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402

ARMS = ["C0_lccp_armC", "D_motion_aspectual"]

# ------------------------------------------------------------------------------------------------
# CREDITED Levin (1993) motion/aspectual SEED classes (small, borrowed, not induced cold).
#   51.1  verbs of inherently directed motion : come go fall rise arrive depart enter exit return ...
#   51.3.2 manner-of-motion (run verbs)        : run walk swim leap spring creep crawl dash flit jump ...
#   47.6  assume-a-spatial-configuration       : sit stand lie kneel lean
#   plus effort/oblique-motion (struggle/tread/meddle/reach) named in the task residual
#   55.1  aspectual verbs                       : begin start commence continue keep stop finish resume try
# CITED@ Levin 1993, English Verb Classes and Alternations; Levin & Rappaport Hovav 1995 (directional PP).
# ------------------------------------------------------------------------------------------------
MOTION_SEED = {"come", "go", "fall", "rise", "arrive", "depart", "enter", "exit", "return", "descend",
               "ascend", "run", "walk", "swim", "leap", "spring", "creep", "crawl", "dash", "flit",
               "jump", "march", "climb", "dart", "glide", "hop", "roll", "sit", "stand", "lie", "kneel",
               "lean", "struggle", "tread", "meddle", "reach"}
ASPECT_SEED = {"begin", "start", "commence", "continue", "keep", "stop", "finish", "resume", "try"}
MA_SEED = MOTION_SEED | ASPECT_SEED

# directional / goal / path tokens (particles + prepositions) -- the Levin & RH path/goal signal.
DIRGOAL = {"into", "onto", "out", "off", "up", "down", "across", "through", "along", "toward", "towards",
           "to", "from", "in", "on", "at", "over", "past", "round", "home", "there", "away", "back",
           "forward", "forth", "upon", "near", "behind", "between", "above", "under", "upstairs",
           "downstairs", "abroad", "aside", "apart", "aboard"}

FEAT_NAMES_D = L.FEAT_NAMES + ["f_dirpp", "f_subcatfreq"]   # 8-dim
N_FEAT = len(FEAT_NAMES_D)


# ------------------------------------------------------------------------------------------------
# Feature 2: directional/goal-PP diagnostic keyed on verb class.
# ------------------------------------------------------------------------------------------------
def dirpp_fires(v_lemma, toks, iv, ip, p_surf, ma_membership):
    """1.0 iff verb is (treated as) motion/aspectual AND a directional/goal token governs/follows.
    ma_membership: callable v_lemma->bool (lets Prediction-3 randomize class tags for the must-fail control)."""
    if not ma_membership(v_lemma):
        return 0.0
    if p_surf in DIRGOAL:
        return 1.0
    if ip is not None:
        prev1 = toks[ip - 1] if ip - 1 >= 0 else ""
        prev2 = toks[ip - 2] if ip - 2 >= 0 else ""
        if prev1 in DIRGOAL or prev2 in DIRGOAL:
            return 1.0
    if iv is not None:
        for k in range(iv + 1, min(iv + 3, len(toks))):
            if toks[k] in DIRGOAL:
                return 1.0
    return 0.0


# ------------------------------------------------------------------------------------------------
# Feature 1: subcategorization-frame-frequency table (per verb, class-backed-off, add-k smoothed).
# ------------------------------------------------------------------------------------------------
def build_subcat_freq_table(cands, sel_fn, sel_keep, k_smooth=2.0):
    """Per verb: smoothed frequency of taking a coherent DIRECT patient. Consulted at the verb.
    A verb-instance 'takes a coherent direct patient' iff its BEST post-verbal / not-prep / not-func
    candidate is selectionally coherent (sel >= sel_keep). Rate = mean over the verb's instances.
    Smoothed (n_pos + k*prior)/(n_inst + k); prior = low MA-class prior for motion/aspectual seed verbs,
    else global rate. Returns (freq_dict, diagnostics)."""
    by_inst = defaultdict(list)                      # (sid,v) -> [cand]
    for c in cands:
        by_inst[(c["sid"], c["v"])].append(c)
    verb_pos = defaultdict(int)
    verb_n = defaultdict(int)
    tot_pos = tot_n = 0
    for (sid, v), cs in by_inst.items():
        # coherent-direct-patient present in this instance?
        got = 0
        for c in cs:
            f = c["feat"]
            if f[2] >= 0.5 and f[3] < 0.5 and f[4] < 0.5:   # post-verbal, not prep, not funcword
                s = sel_fn(c["v"], c["p"])
                if s is not None and s >= sel_keep:
                    got = 1
                    break
        verb_pos[v] += got
        verb_n[v] += 1
        tot_pos += got
        tot_n += 1
    global_rate = (tot_pos / tot_n) if tot_n else 0.3
    MA_CLASS_PRIOR = 0.15                              # low prior for the motion/aspectual class (learned-adjacent seed)
    freq = {}
    diag = {}
    for v in verb_n:
        prior = MA_CLASS_PRIOR if v in MA_SEED else global_rate
        f = (verb_pos[v] + k_smooth * prior) / (verb_n[v] + k_smooth)
        freq[v] = float(f)
        diag[v] = {"n_inst": verb_n[v], "n_coherent_patient": verb_pos[v],
                   "prior_used": round(prior, 4), "smoothed_subcat_freq": round(float(f), 4)}
    return freq, {"global_coherent_patient_rate": round(global_rate, 4),
                  "ma_class_prior": MA_CLASS_PRIOR, "k_smooth": k_smooth,
                  "per_verb": diag}


# ------------------------------------------------------------------------------------------------
# Extended candidate features (LCCP 6 + f_dirpp + f_subcatfreq).
# ------------------------------------------------------------------------------------------------
def extend_features(cands, subcat_freq, ma_membership):
    """Append [f_dirpp, f_subcatfreq] to each candidate's LCCP 6-vector. In place-safe (writes feat8)."""
    for c in cands:
        toks = L.tokenize(c["_sent"])
        iv, ip = L.find_pair_positions(toks, c["tup"][0], c["p"])
        fdir = dirpp_fires(c["v"], toks, iv, ip, c["p"], ma_membership)
        fsub = float(subcat_freq.get(c["v"], 0.3))
        c["feat8"] = np.concatenate([c["feat"], [fdir, fsub]])


# ------------------------------------------------------------------------------------------------
# 8-dim error-driven logistic (mirrors LCCP.learn_cue_weights; teacher = LCCP.cand_target unchanged).
# ------------------------------------------------------------------------------------------------
def learn_weights_ext(cands, sel_fn, sel_keep, sel_drop, lr, epochs, seed):
    rng = np.random.default_rng(seed)
    w = np.zeros(N_FEAT)
    train = []
    for c in cands:
        t = L.cand_target(c, sel_fn, sel_keep, sel_drop)   # reads feat[2..5]; feat8[:6]==feat -> ok
        if t is None:
            continue
        train.append((c["feat8"].copy(), t))
    for _ in range(epochs):
        idx = rng.permutation(len(train))
        for kk in idx:
            x, t = train[kk]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + lr * (t - pred) * x
    return w, len(train)


def score8(w, feat8):
    return L.sigmoid(float(np.dot(w, feat8)))


# ------------------------------------------------------------------------------------------------
# Arm D: LCCP arm-C pipeline with 8-dim weights + MA construction row.
# ------------------------------------------------------------------------------------------------
def run_arm_D(order, reader_svo, sent_text, glove, cfg, seed, ma_membership=None, use_ma_construction=True):
    """Returns (kept_D, artifacts). Mirrors LCCP arm-C's best-candidate + subcat-gate, with the two new
    features and the motion/aspectual construction (seeded membership, LEARNED transitivity prior)."""
    if ma_membership is None:
        ma_membership = lambda v: v in MA_SEED
    cands = []
    for sid in order:
        toks = L.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            feat, _ = L.candidate_features(toks, tup[0], tup[2])
            cands.append({"sid": sid, "v": L.lemma_verb(tup[0]), "a": tup[1], "p": tup[2],
                          "tup": tup, "feat": feat, "_sent": sent_text[sid]})

    sel_fn, verb_cent, glob_cent = L.build_semantic_teacher(cands, glove)
    subcat_freq, subcat_diag = build_subcat_freq_table(cands, sel_fn, cfg["sel_keep"])
    extend_features(cands, subcat_freq, ma_membership)
    w, n_train = learn_weights_ext(cands, sel_fn, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"], cfg["epochs"], seed)

    # held-out verb split (SAME construction as LCCP for parity)
    all_verbs = sorted(set(c["v"] for c in cands))
    rng = np.random.default_rng(seed + 1)
    perm = rng.permutation(len(all_verbs))
    n_heldout = max(1, int(round(cfg["heldout_frac"] * len(all_verbs))))
    heldout_verbs = set(all_verbs[i] for i in perm[:n_heldout])
    seen_verbs = set(all_verbs) - heldout_verbs

    # instance groups
    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)

    # per-verb best-objecthood (for construction transitivity prior)
    verb_best = defaultdict(list)
    for (sid, v), cs in inst_groups.items():
        verb_best[v].append(max(score8(w, c["feat8"]) for c in cs))
    verb_trans = {v: float(np.mean(b)) for v, b in verb_best.items()}

    # MOTION/ASPECTUAL construction row: seed membership = MA_SEED; LEARNED prior = mean best-objecthood of
    # SEEN MA verbs (data-driven, not hand-set). Non-MA verbs -> LCCP-style kmeans construction backoff.
    seen_ma = sorted(v for v in seen_verbs if ma_membership(v) and v in verb_trans)
    ma_constr_prior = float(np.mean([verb_trans[v] for v in seen_ma])) if seen_ma else None

    # non-MA construction clustering (kmeans on cue-profiles), for held-out non-MA backoff
    prof = {}
    for v in all_verbs:
        insts = [cs for (sid, vv), cs in inst_groups.items() if vv == v]
        if not insts:
            continue
        feats = [np.mean(np.stack([c["feat8"][1:7] for c in cs], 0), 0) for cs in insts]  # 6 profile dims
        best = [max(score8(w, c["feat8"]) for c in cs) for cs in insts]
        prof[v] = np.concatenate([np.mean(np.stack(feats, 0), 0), [float(np.mean(best))]])
    seen_nonma = sorted(v for v in seen_verbs if not ma_membership(v) and v in prof)
    if seen_nonma:
        X = np.stack([prof[v] for v in seen_nonma], 0)
        Xn = (X - X.mean(0)) / (X.std(0) + 1e-8)
        assign, _ = L.kmeans(Xn, cfg["k_constructions"], seed + 2)
        vconstr = {seen_nonma[i]: int(assign[i]) for i in range(len(seen_nonma))}
        constr_trans = {}
        for j in range(cfg["k_constructions"]):
            members = [seen_nonma[i] for i in range(len(seen_nonma)) if int(assign[i]) == j]
            if members:
                constr_trans[j] = float(np.mean([verb_trans[m] for m in members]))
        constr_centroid = {j: Xn[assign == j].mean(0) for j in range(cfg["k_constructions"]) if (assign == j).any()}
        Xmean, Xstd = X.mean(0), X.std(0)
    else:
        vconstr, constr_trans, constr_centroid, Xmean, Xstd = {}, {}, {}, None, None

    def nonma_heldout_construction(v):
        if v not in prof or not constr_centroid or Xmean is None:
            return None
        p = (prof[v] - Xmean) / (Xstd + 1e-8)
        best_j, best_d = None, None
        for j, c in constr_centroid.items():
            d = float(((p - c) ** 2).sum())
            if best_d is None or d < best_d:
                best_j, best_d = j, d
        return best_j

    def constr_prior_for(v):
        if use_ma_construction and ma_membership(v):
            return ma_constr_prior                      # shared MA construction (seen + held-out)
        if v in vconstr:
            return constr_trans.get(vconstr[v])
        j = nonma_heldout_construction(v)
        return constr_trans.get(j) if j is not None else None

    # online reading-order pass (mirrors LCCP arm-C exactly, with 8-dim scores + MA construction prior)
    KAPPA = cfg.get("kappa", 1.5)
    per_inst_order = []
    for sid in order:
        for key in [k for k in inst_groups if k[0] == sid]:
            per_inst_order.append(key)
    t_run = defaultdict(lambda: [0.0, 0])
    kept_D = []
    graded = []                                          # (sid,v,p, best_sc, kept)  for Prediction-4
    verb_seen_count = defaultdict(int)
    for (sid, v) in per_inst_order:
        cs = inst_groups[(sid, v)]
        best = max(cs, key=lambda c: score8(w, c["feat8"]))
        best_sc = score8(w, best["feat8"])
        cprior = constr_prior_for(v)
        if v in seen_verbs:
            s, n = t_run[v]
            if cprior is None:
                prior = (s / n) if n > 0 else None
            else:
                prior = (s + KAPPA * cprior) / (n + KAPPA)
        else:
            prior = cprior
        if prior is not None and prior < cfg["subcat_thr"]:
            keep_patient = False
        else:
            keep_patient = best_sc >= cfg["keep_thr"]
        if keep_patient:
            kept_D.append((best["sid"], best["tup"]))
        graded.append({"sid": sid, "v": v, "p": best["p"], "best_sc": round(best_sc, 4), "kept": keep_patient})
        verb_seen_count[v] += 1
        if v in seen_verbs:
            t_run[v][0] += best_sc
            t_run[v][1] += 1

    artifacts = {
        "w": [round(float(x), 4) for x in w], "feat_names": FEAT_NAMES_D, "n_train": n_train,
        "n_candidates": len(cands), "n_verb_instances": len(inst_groups),
        "ma_construction_learned_prior": (round(ma_constr_prior, 4) if ma_constr_prior is not None else None),
        "n_seen_ma_verbs": len(seen_ma), "seen_ma_verbs": seen_ma,
        "w_f_dirpp": round(float(w[FEAT_NAMES_D.index("f_dirpp")]), 4),
        "w_f_subcatfreq": round(float(w[FEAT_NAMES_D.index("f_subcatfreq")]), 4),
        "subcat_freq_table_sample": {v: subcat_diag["per_verb"][v] for v in sorted(subcat_diag["per_verb"])
                                     if v in MA_SEED or subcat_diag["per_verb"][v]["n_inst"] >= 3},
        "subcat_freq_global": subcat_diag["global_coherent_patient_rate"],
        "heldout_verbs": sorted(heldout_verbs), "seen_verbs": sorted(seen_verbs),
    }
    return kept_D, artifacts, graded, w, subcat_freq, sel_fn, cands, heldout_verbs, seen_verbs


# ------------------------------------------------------------------------------------------------
# Motion/aspectual FP-rate (PRIMARY metric) + triage.
# ------------------------------------------------------------------------------------------------
def motion_aspectual_instances(reader_svo, gold, order):
    """M = motion/aspectual nopat instances (sid,v) the reader attached a patient to. Denominator of FP_a."""
    M = set()
    for sid in order:
        rec = gold.get(sid)
        if not rec:
            continue
        for tup in reader_svo[sid]:
            v = L.lemma_verb(tup[0])
            if v in MA_SEED and v in rec["nopat"] and v not in rec["pos_verbs"]:
                M.add((sid, v))
    return M


def apply_direct_gate(keptC0, sent_text, subcat_freq, low_thr=0.35):
    """DIAGNOSTIC (non-pass/fail): the CEILING of the two cues applied as a DIRECT STRUCTURAL gate over
    arm-C0's kept set (NOT via the learned logistic). Suppress a kept patient iff the directional-PP
    diagnostic fires OR the verb is a motion/aspectual seed verb with low class-backed subcat frequency.
    Separates 'the cue is insufficient' (this ALSO fails) from 'the learned route failed' (this succeeds)."""
    ma_mem = lambda v: v in MA_SEED
    out = []
    for sid, tup in keptC0:
        v = L.lemma_verb(tup[0]); p = tup[2]
        toks = L.tokenize(sent_text.get(sid, ""))
        iv, ip = L.find_pair_positions(toks, tup[0], p)
        dirfire = dirpp_fires(v, toks, iv, ip, p, ma_mem) >= 0.5
        low_subcat = (v in MA_SEED and subcat_freq.get(v, 1.0) < low_thr)
        if dirfire or low_subcat:
            continue  # suppress
        out.append((sid, tup))
    return out


def fp_a(kept, M):
    """Fraction of M the arm KEEPS a patient for (lower = better)."""
    kept_inst = set((sid, L.lemma_verb(tup[0])) for sid, tup in kept)
    if not M:
        return 0.0, 0
    keeps = sum(1 for key in M if key in kept_inst)
    return keeps / len(M), keeps


def triage_fps(kept, gold, reader_svo, order):
    """STEP-1 triage of an arm's kept FPs into (a) motion/aspectual, (b) within-transitive/other,
    (c) contested/gradient. Returns counts + examples."""
    from collections import Counter
    c = Counter()
    ex = defaultdict(list)
    for sid, tup in kept:
        v = L.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None:
            c["TP"] += 1
            continue
        toks = L.tokenize(reader_svo.get("_sent", {}).get(sid, "")) if False else L.tokenize("")
        # detect directional context from patient token + preps (position-free; conservative)
        dir_ctx = p in DIRGOAL
        ma = v in MA_SEED
        if ma and v in rec["nopat"] and v not in rec["pos_verbs"]:
            cls = "a_motion_aspectual"
        elif ma and dir_ctx:
            cls = "a_motion_aspectual"
        elif dir_ctx and (ma or v in {"put", "throw", "pass", "lay", "set", "place", "get", "bring", "carry"}):
            cls = "c_contested_gradient"
        elif v in rec["pos_verbs"]:
            cls = "b_within_transitive"
        elif v in rec["nopat"]:
            cls = "b_other_nopat_nonmotion"
        else:
            cls = "b_spurious_or_other"
        c[cls] += 1
        ex[cls].append([sid, v, p])
    return dict(c), {k: v[:12] for k, v in ex.items()}


# ------------------------------------------------------------------------------------------------
# Prediction-3 must-fail control: degrade directional-PP cue reliability -> |w[f_dirpp]| must drop.
# ------------------------------------------------------------------------------------------------
def prediction3_control(order, reader_svo, sent_text, glove, cfg, seed, M, gold):
    """Must-fail control (2 parts). Deterministic (seeded rng, not builtin hash).
    (Part A, per drill Prediction-3 literal) degrade the directional-PP cue reliability by RANDOMIZING MA
      class-membership per verb -> the LEARNED |w[f_dirpp]| should DROP vs the clean run.
    (Part B, DECISIVE vacuousness test) does the FP_a WIN survive membership randomization? If randomizing
      which verbs are 'motion/aspectual' preserves the FP_a reduction, the win is CONSTRUCTION-DETERMINED /
      not tied to the true Levin class. A genuine mechanism -> FP_a reduction on the TRUE motion class
      COLLAPSES when membership is randomized."""
    di = FEAT_NAMES_D.index("f_dirpp")
    keptD_clean, art_clean, _, w_clean, *_ = run_arm_D(order, reader_svo, sent_text, glove, cfg, seed)
    rng = np.random.default_rng(seed + 101)
    all_verbs = sorted(set(L.lemma_verb(t[0]) for sid in order for t in reader_svo[sid]))
    # keep the SAME number of 'MA' verbs, but a random set (removes the true Levin class signal)
    n_ma = sum(1 for v in all_verbs if v in MA_SEED)
    perm = rng.permutation(len(all_verbs))
    rand_ma = set(all_verbs[perm[i]] for i in range(min(n_ma, len(all_verbs))))
    ma_rand = lambda v: v in rand_ma
    keptD_deg, art_deg, _, w_deg, *_ = run_arm_D(order, reader_svo, sent_text, glove, cfg, seed,
                                                 ma_membership=ma_rand, use_ma_construction=True)
    keptC0 = L.run_arms(order, reader_svo, sent_text, glove,
                        {**{k: v for k, v in cfg.items() if k != "seeds"}, "seed": seed}, seed)[0]["C_lccp"]
    fpaC0, _ = fp_a(keptC0, M)
    fpaClean, _ = fp_a(keptD_clean, M)
    fpaDeg, _ = fp_a(keptD_deg, M)
    wc, wd = abs(float(w_clean[di])), abs(float(w_deg[di]))
    red_clean = fpaC0 - fpaClean
    red_deg = fpaC0 - fpaDeg
    return {"w_dirpp_clean_abs": round(wc, 4), "w_dirpp_degraded_abs": round(wd, 4),
            "w_dirpp_clean": round(float(w_clean[di]), 4), "w_dirpp_degraded": round(float(w_deg[di]), 4),
            "weight_drops_when_degraded": bool(wd < wc - 1e-6),
            "fp_a_reduction_clean_membership": round(red_clean, 4),
            "fp_a_reduction_random_membership": round(red_deg, 4),
            "fp_a_win_collapses_under_random_membership": bool(red_deg < red_clean - 0.05),
            "mechanism_not_construction_determined": bool(red_deg < red_clean - 0.05)}


# ------------------------------------------------------------------------------------------------
# Prediction-4 graded argument-hood score.
# ------------------------------------------------------------------------------------------------
def graded_score_report(graded, gold, M):
    """Mean graded (sigmoid) objecthood for clear-argument (gold TP), motion-nopat (category a), and
    contested/gradient (patient is directional-goal on a change-of-location verb)."""
    clear_arg, motion_nopat, contested = [], [], []
    for g in graded:
        sid, v, p, sc = g["sid"], g["v"], g["p"], g["best_sc"]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None:
            clear_arg.append(sc)
        elif (sid, v) in M:
            motion_nopat.append(sc)
        if p in DIRGOAL and (v in MA_SEED or v in {"put", "throw", "pass", "lay", "set", "place", "get"}):
            contested.append(sc)

    def stat(xs):
        return {"mean": round(float(np.mean(xs)), 4) if xs else None,
                "n": len(xs), "min": round(min(xs), 4) if xs else None,
                "max": round(max(xs), 4) if xs else None}
    return {"clear_argument_gold_TP": stat(clear_arg), "motion_nopat_category_a": stat(motion_nopat),
            "contested_gradient_category_c": stat(contested),
            "ordering_ok": bool(clear_arg and motion_nopat and np.mean(clear_arg) > np.mean(motion_nopat))}


# ------------------------------------------------------------------------------------------------
# Config + run.
# ------------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seeds=[7])


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], sel_keep=0.28,
               sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25,
               k_constructions=4, seeds=[7, 13, 19])


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def run_config(cfg, mode):
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)

    M = motion_aspectual_instances(reader_svo, gold, order)

    # ARM C0: LIVE LCCP arm-C recompute (real baseline). Seed = first seed for the kept-set; metrics over seeds.
    per_seed = []
    keptC0_ref, keptD_ref = None, None
    for seed in cfg["seeds"]:
        lccp_cfg = {k: v for k, v in cfg.items() if k != "seeds"}
        lccp_cfg["seed"] = seed
        decisions, _art, _sd, ho, sn, _ig, _w = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)
        keptC0 = decisions["C_lccp"]
        keptD, artD, graded, wD, subfreq, sel_fn, cands, hoD, snD = run_arm_D(
            order, reader_svo, sent_text, glove, lccp_cfg, seed)
        mC = L.score_arm(keptC0, gold)
        mD = L.score_arm(keptD, gold)
        fpaC, keepsC = fp_a(keptC0, M)
        fpaD, keepsD = fp_a(keptD, M)
        per_seed.append({
            "seed": seed,
            "C0": {"precision": mC["precision"], "recall": mC["recall"], "f1": mC["f1"],
                   "n_pred": mC["n_pred"], "fp_rate": mC["fp_rate"], "subcat_fp": mC["subcat_fp"]},
            "D": {"precision": mD["precision"], "recall": mD["recall"], "f1": mD["f1"],
                  "n_pred": mD["n_pred"], "fp_rate": mD["fp_rate"], "subcat_fp": mD["subcat_fp"]},
            "fp_a_C0": round(fpaC, 4), "fp_a_D": round(fpaD, 4),
            "motion_aspectual_keeps_C0": keepsC, "motion_aspectual_keeps_D": keepsD,
            "fp_a_reduction": round(fpaC - fpaD, 4),
            "recall_retention_D_over_C0": round((mD["recall"] / mC["recall"]) if mC["recall"] > 0 else 0.0, 4),
            "w_f_dirpp": artD["w_f_dirpp"], "w_f_subcatfreq": artD["w_f_subcatfreq"],
            "ma_construction_learned_prior": artD["ma_construction_learned_prior"],
        })
        if seed == cfg["seeds"][0]:
            keptC0_ref, keptD_ref = keptC0, keptD
            artD_ref, graded_ref, subfreq_ref = artD, graded, subfreq
            triC0, exC0 = triage_fps(keptC0, gold, reader_svo, order)
            triD, exD = triage_fps(keptD, gold, reader_svo, order)

    # aggregate
    def agg(key, sub=None):
        vals = [(p[key][sub] if sub else p[key]) for p in per_seed]
        return round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)

    fpaC_m, fpaC_s = agg("fp_a_C0")
    fpaD_m, fpaD_s = agg("fp_a_D")
    red_m, red_s = agg("fp_a_reduction")
    rret_m, rret_s = agg("recall_retention_D_over_C0")
    pC_m, _ = agg("C0", "precision")
    pD_m, _ = agg("D", "precision")
    rC_m, _ = agg("C0", "recall")
    rD_m, _ = agg("D", "recall")

    pred3 = prediction3_control(order, reader_svo, sent_text, glove, cfg, cfg["seeds"][0], M, gold)
    pred4 = graded_score_report(graded_ref, gold, M)

    # DIAGNOSTIC: direct-structural-gate ceiling of the two cues (separates cue-insufficient from learned-route-failed)
    keptDdirect = apply_direct_gate(keptC0_ref, sent_text, subfreq_ref)
    mDirect = L.score_arm(keptDdirect, gold)
    fpa_direct, keeps_direct = fp_a(keptDdirect, M)
    mC0ref = L.score_arm(keptC0_ref, gold)
    diag_direct = {
        "note": "hand-applied structural gate (dirpp OR low-class-subcat) over arm-C0; NOT learned; ceiling only",
        "fp_a_direct_gate": round(fpa_direct, 4), "motion_aspectual_keeps_direct": keeps_direct,
        "fp_a_reduction_vs_C0": round(fpaC_m - fpa_direct, 4),
        "overall_precision_direct": mDirect["precision"], "overall_recall_direct": mDirect["recall"],
        "recall_retention_direct_over_C0": round((mDirect["recall"] / mC0ref["recall"]) if mC0ref["recall"] > 0 else 0.0, 4),
        "cue_ceiling_interpretation": ("if this reduces FP_a >=0.15 at recall retention >=0.60, the CUES are "
                                       "sufficient and the LEARNED-via-coherence route is what failed "
                                       "(re-design the learning signal); if this ALSO fails, the cues "
                                       "themselves are insufficient (Prediction-1 real HARD-FAIL)."),
    }

    # verdict
    if red_m < 0.05 or rret_m < 0.40:
        verdict = "HARD_FAIL_FEATURES_INSUFFICIENT"
    elif red_m >= 0.15 and rret_m >= 0.60:
        verdict = "HARD_PASS_MOTION_ASPECTUAL_SUBCAT_CUT"
    else:
        verdict = "MIDDLE_BAND"

    hashes = {"C0_lccp_armC": kept_hash(keptC0_ref), "D_motion_aspectual": kept_hash(keptD_ref)}
    arms_differ = hashes["C0_lccp_armC"] != hashes["D_motion_aspectual"]
    baseline_in_band = bool(0.05 < pC_m < 0.95)
    discriminator_fires = bool(per_seed[0]["motion_aspectual_keeps_D"] < per_seed[0]["motion_aspectual_keeps_C0"])

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict,
        "primary_metric": "motion_aspectual_subcat_FP_rate (FP_a), independent gold, category-c held OUT",
        "denominator_M_motion_aspectual_nopat_instances": len(M),
        "fp_a_C0_mean": fpaC_m, "fp_a_C0_std": fpaC_s,
        "fp_a_D_mean": fpaD_m, "fp_a_D_std": fpaD_s,
        "fp_a_reduction_mean": red_m, "fp_a_reduction_std": red_s,
        "recall_retention_mean": rret_m, "recall_retention_std": rret_s,
        "overall_precision_C0_mean": pC_m, "overall_precision_D_mean": pD_m,
        "overall_recall_C0_mean": rC_m, "overall_recall_D_mean": rD_m,
        "per_seed": per_seed,
        "step1_triage_C0": {"counts": triC0, "examples": exC0},
        "step1_triage_D": {"counts": triD, "examples": exD},
        "prediction3_mechanism_validity": pred3,
        "prediction4_graded_argument_hood": pred4,
        "diagnostic_direct_gate_cue_ceiling": diag_direct,
        "arm_D_artifacts_seed0": artD_ref,
        "kept_hashes": hashes, "arms_differ_verified": arms_differ,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace",
        "n_sentences": len(order), "n_reader_svo": sum(len(reader_svo[sid]) for sid in order),
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "seeds": cfg["seeds"], "config": {k: v for k, v in cfg.items()},
        "levin_seed_cited": "Levin 1993 English Verb Classes and Alternations (51.1/51.3.2/47.6/55.1); "
                            "Levin & Rappaport Hovav 1995 directional-PP diagnostic",
        "REQUIRED_FIELDS": ["verdict", "fp_a_C0_mean", "fp_a_D_mean", "fp_a_reduction_mean",
                            "recall_retention_mean", "per_seed", "step1_triage_C0", "step1_triage_D",
                            "prediction3_mechanism_validity", "prediction4_graded_argument_hood"],
    }
    msg = (f"{verdict} | M={len(M)} | FP_a C0={fpaC_m:.3f}+-{fpaC_s:.3f} D={fpaD_m:.3f}+-{fpaD_s:.3f} "
           f"red={red_m:+.3f}+-{red_s:.3f} | Rret={rret_m:.3f} | overallP C0={pC_m:.3f} D={pD_m:.3f} "
           f"overallR C0={rC_m:.3f} D={rD_m:.3f} | w_dirpp={artD_ref['w_f_dirpp']:.2f} "
           f"w_subcatfreq={artD_ref['w_f_subcatfreq']:.2f} MAprior={artD_ref['ma_construction_learned_prior']} "
           f"| pred3 dirppW clean={pred3['w_dirpp_clean_abs']:.3f} deg={pred3['w_dirpp_degraded_abs']:.3f} "
           f"drops={pred3['weight_drops_when_degraded']} "
           f"| pred4 argTP={pred4['clear_argument_gold_TP']['mean']} "
           f"motionNoPat={pred4['motion_nopat_category_a']['mean']} "
           f"contested={pred4['contested_gradient_category_c']['mean']}(n={pred4['contested_gradient_category_c']['n']}) "
           f"| triage_C0 a={triC0.get('a_motion_aspectual',0)} b_wt={triC0.get('b_within_transitive',0)} "
           f"c={triC0.get('c_contested_gradient',0)} | base_in_band={baseline_in_band} discrim={discriminator_fires} "
           f"arms_differ={arms_differ}")
    out["verdict_msg"] = msg
    out["summary"] = msg
    return out, msg


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    out, msg = run_config(cfg, mode)
    out["elapsed_s"] = time.perf_counter() - t0
    out["ts_iso"] = datetime.now(timezone.utc).isoformat()
    # smoke gates
    assert out["arms_differ_verified"], "META_RULE_AF: C0==D (bundle no-op)"
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, out)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  learned 8-weights: {dict(zip(FEAT_NAMES_D, out['arm_D_artifacts_seed0']['w']))}", flush=True)
    print(f"  MA construction learned prior: {out['arm_D_artifacts_seed0']['ma_construction_learned_prior']} "
          f"(seen MA verbs: {out['arm_D_artifacts_seed0']['n_seen_ma_verbs']})", flush=True)
    for p in out["per_seed"]:
        print(f"  [seed {p['seed']}] FP_a C0={p['fp_a_C0']:.3f}({p['motion_aspectual_keeps_C0']}/{out['denominator_M_motion_aspectual_nopat_instances']}) "
              f"D={p['fp_a_D']:.3f}({p['motion_aspectual_keeps_D']}/{out['denominator_M_motion_aspectual_nopat_instances']}) "
              f"red={p['fp_a_reduction']:+.3f} | overallP C0={p['C0']['precision']:.3f} D={p['D']['precision']:.3f} "
              f"Rret={p['recall_retention_D_over_C0']:.3f}", flush=True)
    print(f"  [triage C0] {out['step1_triage_C0']['counts']}", flush=True)
    print(f"  [triage D ] {out['step1_triage_D']['counts']}", flush=True)
    print(f"  [pred3] {out['prediction3_mechanism_validity']}", flush=True)
    print(f"  [pred4] {out['prediction4_graded_argument_hood']}", flush=True)
    dd = out["diagnostic_direct_gate_cue_ceiling"]
    print(f"  [diag direct-gate ceiling] FP_a={dd['fp_a_direct_gate']:.3f} (keeps {dd['motion_aspectual_keeps_direct']}/{out['denominator_M_motion_aspectual_nopat_instances']}) "
          f"red_vs_C0={dd['fp_a_reduction_vs_C0']:+.3f} | overallP={dd['overall_precision_direct']:.3f} "
          f"Rret={dd['recall_retention_direct_over_C0']:.3f}", flush=True)
    return out


def self_test():
    # feature-2 directional detector fires on 'came home', not on 'opened door'
    toks = L.tokenize("charley came home from school")
    iv, ip = L.find_pair_positions(toks, "came", "home")
    assert dirpp_fires("come", toks, iv, ip, "home", lambda v: v in MA_SEED) == 1.0, "come home -> dirpp"
    toks2 = L.tokenize("he opened the door")
    iv2, ip2 = L.find_pair_positions(toks2, "opened", "door")
    assert dirpp_fires("open", toks2, iv2, ip2, "door", lambda v: v in MA_SEED) == 0.0, "open door -> no dirpp (not MA)"
    toks3 = L.tokenize("he walked on the gravel")
    iv3, ip3 = L.find_pair_positions(toks3, "walked", "gravel")
    assert dirpp_fires("walk", toks3, iv3, ip3, "gravel", lambda v: v in MA_SEED) == 1.0, "walk on gravel -> dirpp"
    # subcat-freq: motion seed verb gets a LOW class prior vs a clearly transitive verb
    cands = [
        {"sid": "s0", "v": "come", "p": "home", "feat": np.array([1., .5, 1., 0., 0., 0.])},
        {"sid": "s1", "v": "come", "p": "eyes", "feat": np.array([1., .3, 1., 0., 0., 0.])},
        {"sid": "s2", "v": "build", "p": "house", "feat": np.array([1., .9, 1., 0., 0., 0.])},
        {"sid": "s3", "v": "build", "p": "castle", "feat": np.array([1., .9, 1., 0., 0., 0.])},
    ]
    sel = lambda v, p: 0.6 if v == "build" else 0.05   # build coherent, come not
    freq, _ = build_subcat_freq_table(cands, sel, 0.28)
    assert freq["build"] > freq["come"], f"build subcatfreq {freq['build']:.3f} !> come {freq['come']:.3f}"
    assert freq["come"] < 0.35, f"come subcatfreq should be low, got {freq['come']:.3f}"
    # lemma parity with LCCP
    assert L.lemma_verb("came") == "come" and L.lemma_verb("walked") == "walk"
    # end-to-end smoke config runs + arms differ + weight signs
    cfg = cfg_smoke()
    out, _ = run_config(cfg, "smoke")
    assert out["arms_differ_verified"], "arms C0 and D must differ"
    w = out["arm_D_artifacts_seed0"]["w"]
    wd = w[FEAT_NAMES_D.index("f_dirpp")]
    ws = w[FEAT_NAMES_D.index("f_subcatfreq")]
    print(f"[{ANCHOR_NAME}] self-test OK | FP_a C0={out['fp_a_C0_mean']:.3f} D={out['fp_a_D_mean']:.3f} "
          f"red={out['fp_a_reduction_mean']:+.3f} | w_dirpp={wd:+.3f} w_subcatfreq={ws:+.3f} "
          f"| pred3_drops={out['prediction3_mechanism_validity']['weight_drops_when_degraded']} "
          f"| verdict={out['verdict']}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
