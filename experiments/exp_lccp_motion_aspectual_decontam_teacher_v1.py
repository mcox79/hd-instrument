"""FORK-(B) DECONTAMINATED-TEACHER: does re-designing the self-supervised LEARNING SIGNAL (so a verb's
argument-structure is judged from a signal that does NOT include that verb's OWN contaminated attachments)
make the substrate GENUINELY LEARN the motion/aspectual subcategorization rule -- i.e. the must-fail
control now FIRES and w[f_dirpp] learns the CORRECT (negative) sign robustly across seeds?

ROOT CAUSE BEING FIXED (VET-confirmed atom 29347, ac1817 split-result):
  ac1817's coherence teacher (L.build_semantic_teacher) builds each verb's patient-centroid from THAT
  VERB'S OWN post-verbal attachments. For an intransitive (come/sit/stand/walk) it bootstraps from its
  OWN spurious patients (home/eyes/tears/charles), rates those coherent, so subcatfreq stays HIGH
  (come~0.61) and the coherence target LABELS the directional-PP patient as coherent (=1). The logistic
  then sees f_dirpp=1 co-occur with target=1 -> it learns w[f_dirpp] POSITIVE (wrong sign). Circular /
  self-fulfilling. MEASURED@data/exp_lccp_motion_aspectual_subcat_break_v1/metrics.json:
    per_seed w_f_dirpp = +0.4467/+0.4439/+0.4534 (WRONG-signed, all 3 seeds);
    fp_a_reduction = 0.0333/0.0333/0.2333 (SEED-UNSTABLE; the 0.100 mean is 1/3 seeds);
    prediction3 must-fail: w_dirpp_clean_abs=0.4467 -> w_dirpp_degraded_abs=0.9333 (weight ROSE,
      drops=False) = the substrate did NOT learn (the win is construction-determined, not learned).
  CEILING reference (reachable target) MEASURED@ same file diagnostic_direct_gate_cue_ceiling:
    FP_a 0.100, overall precision 0.541, recall retention 0.9706 (the clean cues applied as a DIRECT gate).

THE FIX (decontaminate the TEACHER, grounded in the drilled acquisition lit -- Alishahi & Stevenson
2005/2008: recover from arg-structure overgeneralization using ONLY cross-situation frequency/co-occurrence,
NO negative evidence, NO self-contamination, because the frame is learned across MANY verbs, not one verb's
own noisy self-parse; Ford-Bresnan-Kaplan / Trueswell frame-frequency; Levin & Rappaport Hovav directional-PP
diagnostic). CITED@notes/research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md Angle-3/5.
  DECONTAMINATED sel(v,p): judge patient p against a LEAVE-VERB-v-OUT, DISPERSION-PURIFIED GLOBAL patient
    reference -- built from OTHER verbs' post-verbal content patients, restricted to LOW-DISPERSION fillers
    (a filler occurring with <= disp_thr distinct verbs = verb-specific = likely a true patient; high-
    dispersion fillers like home/there/back occur with MANY verbs = adjunct-typed = EXCLUDED from the
    reference AND scored low against it). v's own attachments NEVER define v's own judgment -> the self-
    fulfilling loop is broken. For come, "home" is high-dispersion + far from the real-patient reference ->
    coherence LOW -> target 0 -> f_dirpp=1 now co-occurs with target 0 -> w[f_dirpp] learns NEGATIVE.
  NON-CIRCULARITY (load-bearing, else the must-fail control is vacuous per drill Prediction-3): the teacher
    does NOT consult DIRGOAL / MA-membership. f_dirpp is a SEPARATE structural cue (directional token +
    verb-class). The logistic LEARNS that f_dirpp predicts the INDEPENDENT low-coherence target; degrading
    f_dirpp reliability (randomize MA membership) breaks that correlation -> |w[f_dirpp]| must COLLAPSE =
    genuine-learning signature.

ARMS (ONE VARIABLE = the LEARNING SIGNAL: contaminated self-centroid teacher vs decontaminated LOO-purified
teacher; EVERYTHING else identical -- same candidate gen, same 8 features {LCCP 6 + f_dirpp + f_subcatfreq},
same MA construction row, same PERCENTILE target rule, same lr/epochs/keep_thr/subcat_thr/seeds):
  ARM C0        = LIVE LCCP arm-C recompute (the real ~0.500 baseline; features OFF). Reference point.
  ARM D_contam  = C0 + {f_dirpp, f_subcatfreq, MA construction} with the CONTAMINATED teacher (the thing that
                  failed in ac1817; recomputed live under the fair shared percentile target rule to isolate
                  that CONTAMINATION -- not the threshold -- is the cause).
  ARM E_decontam= identical to D_contam but the teacher is DECONTAMINATED (LOO purified reference). THE fix.

TARGET RULE (shared by D_contam and E_decontam -> one variable preserved): the coherence accept/reject target
  for bare content patients is PERCENTILE-based within each arm's own sel distribution (target 1 if sel >=
  P_keep pct, 0 if sel <= P_drop pct, DEFER between), so a systematic scale shift between the two teachers is
  auto-calibrated and only the sel VALUES (from the teacher) differ. Structural overrides (funcword/prep/
  clause -> 0; pronoun-postverbal -> 1) identical to L.cand_target. calibration_check:
  adaptive_with_discriminator_gate (discriminator-fires verified at smoke).

MEASURED (decisive):
  PRIMARY (the LEARNING test): (1) w[f_dirpp] NEGATIVE for ALL seeds (E) vs POSITIVE (D_contam);
    (2) must-fail control FIRES for ALL seeds (degrade directional-PP cue -> |w[f_dirpp]| DROPS); (3) FP_a
    reduction SEED-STABLE (reduction > 0 for ALL seeds, not 1/3); (4) FP_a(E) approaches the direct-gate
    ceiling (~0.10) at recall retention >= 0.60.
  SECONDARY: overall patient precision/recall/F1 per arm; w_subcatfreq per arm; the direct-gate ceiling
    recomputed with the decontaminated cues; per-seed weights + signs; step-1 triage.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = D_contam (the ac1817 failed route) AND the direct-gate CEILING (FP_a 0.100 / P 0.541).
  (G2) ONE VARIABLE = contaminated vs decontaminated teacher; all else identical.
  (G3) CAN-FAIL-BOTH-WAYS: E can learn w[f_dirpp]<0 + must-fail fire + seed-stable FP_a cut (PASS) OR stay
       wrong-signed / seed-unstable / must-fail-fail (HARD-FAIL, a real localization: decontam insufficient).
  (G4) difficulty ON: same motion/aspectual residual, independent gold, category-c held OUT.
  (G5) discriminator fires at smoke: E's w[f_dirpp] < 0 AND D_contam's >= 0 (the arms diverge on the sign)
       AND E suppresses >0 of C0's motion/aspectual FPs AND kept sets differ.

VERDICT BANDS (pre-registered):
  HARD_PASS_GENUINE_LEARNING: w_f_dirpp(E) < 0 for ALL seeds AND must-fail fires for ALL seeds (degraded
    |w| < clean |w| - 1e-6) AND fp_a_reduction(E vs C0) > 0 for ALL seeds (seed-stable) AND mean FP_a(E)
    <= 0.20 (approaching the 0.10 ceiling) AND recall_retention(E/C0) >= 0.60.
  HARD_FAIL_DECONTAM_INSUFFICIENT: w_f_dirpp(E) >= 0 for ANY seed OR must-fail fails for ANY seed OR
    fp_a_reduction(E) seed-unstable (> 0 in fewer than ALL seeds) OR recall_retention(E/C0) < 0.40.
  MIDDLE_BAND: sign correct + must-fail fires but FP_a modest / not fully seed-stable / above ceiling band.

HONESTY GUARD (mandatory, printed + stored): even FULL success caps overall precision ~0.541 on arm-C0's
  scope, which is BELOW the stacked 0.557 patient-lens reader -> the value here is METHODOLOGICAL (a rule
  GENUINELY LEARNED, not hand-installed) + modest precision, NOT breaking 0.557. A stack re-measure is a
  SEPARATE step, NOT claimed here. No hand-applied number is reported as if learned.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- ~225 reader candidates, a
  few hundred GloVe cosines + a tiny 8-dim logistic x a few epochs x 3 seeds x 3 arms + a must-fail control;
  wall < ~180s. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage: no_storage
  (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic
  hashlib; no salted builtin hash / list(set); numpy default RNG seeded.

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (C0 vs D_contam vs E_decontam kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < arm-C0 precision < 0.95)
- discriminator fires at smoke (E w[f_dirpp] < 0 AND D_contam >= 0; E suppresses >0 MA FPs; kept sets differ)
- multi-seed (3 seeds); FP_a + weights aggregated per seed
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
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "lccp_motion_aspectual_decontam_teacher_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_lccp_motion_aspectual_subcat_break_v1 as MA  # noqa: E402

ARMS = ["C0_lccp_armC", "D_contam", "E_decontam"]
FEAT_NAMES_D = MA.FEAT_NAMES_D          # ["bias","f_adj","f_postv","f_prep","f_func","f_clause","f_dirpp","f_subcatfreq"]
N_FEAT = MA.N_FEAT
MA_SEED = MA.MA_SEED
DI = FEAT_NAMES_D.index("f_dirpp")
SI = FEAT_NAMES_D.index("f_subcatfreq")


# ------------------------------------------------------------------------------------------------
# Candidate builder (LCCP 6-feature candidates + _sent, mirrors MA.run_arm_D's front-end).
# ------------------------------------------------------------------------------------------------
def build_cands(order, reader_svo, sent_text):
    cands = []
    for sid in order:
        toks = L.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            feat, _ = L.candidate_features(toks, tup[0], tup[2])
            cands.append({"sid": sid, "v": L.lemma_verb(tup[0]), "a": tup[1], "p": tup[2],
                          "tup": tup, "feat": feat, "_sent": sent_text[sid]})
    return cands


def _is_bare_content(c):
    """post-verbal, not prep-governed, not funcword -> a bare content patient (the teacher's raw material)."""
    f = c["feat"]
    return f[2] >= 0.5 and f[3] < 0.5 and f[4] < 0.5


# ------------------------------------------------------------------------------------------------
# TEACHER (the ONE VARIABLE). kind = "contam" (per-verb self-centroid, ac1817) | "decontam" (LOO purified).
# ------------------------------------------------------------------------------------------------
def build_teacher(cands, glove, kind, cfg):
    if kind == "contam":
        sel_fn, verb_cent, glob_cent = L.build_semantic_teacher(cands, glove)
        return sel_fn, {"kind": "contam", "n_per_verb_centroids": len(verb_cent),
                        "note": "each verb judged vs its OWN post-verbal-patient centroid (self-fulfilling)"}

    # --- decontam: leave-verb-out, dispersion-purified GLOBAL patient reference ---
    dim = None
    for c in cands:
        pv = glove.get(c["p"])
        if pv is not None:
            dim = int(pv.shape[0])
            break
    if dim is None:
        # no glove coverage at all: degenerate; return a None-teacher (targets all DEFER)
        return (lambda v, p: None), {"kind": "decontam", "n_ref_patients": 0, "ref_path": "no_glove"}

    # filler dispersion = # distinct verbs a token appears with as a bare content patient
    filler_verbs = defaultdict(set)
    for c in cands:
        if _is_bare_content(c):
            filler_verbs[c["p"]].add(c["v"])
    dispersion = {p: len(vs) for p, vs in filler_verbs.items()}

    def build_sums(thr):
        verb_sum = defaultdict(lambda: [np.zeros(dim), 0])
        gsum = [np.zeros(dim), 0]
        used = 0
        for c in cands:
            pv = glove.get(c["p"])
            if pv is None or not _is_bare_content(c):
                continue
            if dispersion.get(c["p"], 10 ** 9) > thr:
                continue
            verb_sum[c["v"]][0] = verb_sum[c["v"]][0] + pv
            verb_sum[c["v"]][1] += 1
            gsum[0] = gsum[0] + pv
            gsum[1] += 1
            used += 1
        return verb_sum, gsum, used

    disp_thr = cfg["disp_thr"]
    verb_sum, gsum, used = build_sums(disp_thr)
    ref_path = "dispersion_purified"
    if used < cfg["min_ref"]:
        # too few verb-specific fillers to define a stable reference: relax purification (still LOO).
        verb_sum, gsum, used = build_sums(10 ** 9)
        ref_path = "all_content_loo_fallback"

    def sel(v, p):
        pv = glove.get(p)
        if pv is None:
            return None
        s = gsum[0] - verb_sum[v][0]        # LEAVE-VERB-v-OUT: v never defines its own judgment
        n = gsum[1] - verb_sum[v][1]
        if n <= 0:
            return None
        ref = s / n
        nn = np.linalg.norm(ref)
        ref = ref / (nn if nn > 1e-8 else 1.0)
        return float(np.dot(pv, ref))

    top_disp = sorted(dispersion.items(), key=lambda kv: -kv[1])[:15]
    return sel, {"kind": "decontam", "disp_thr": disp_thr, "n_ref_patients": used, "ref_path": ref_path,
                 "n_distinct_fillers": len(dispersion),
                 "top_dispersion_fillers": [[k, v] for k, v in top_disp]}


# ------------------------------------------------------------------------------------------------
# TARGET RULE (shared by both teachers). Percentile-based for bare content patients + structural overrides.
# ------------------------------------------------------------------------------------------------
def make_target_fn(cands, sel_fn, cfg):
    """Return (target_fn(c)->0/1/None, keep_abs, drop_abs). keep_abs/drop_abs are the arm's own sel
    distribution percentiles (auto-calibrates a scale shift between the two teachers -> one variable)."""
    if cfg.get("target_mode", "percentile") == "absolute":
        keep_abs, drop_abs = cfg["sel_keep"], cfg["sel_drop"]
    else:
        vals = []
        for c in cands:
            f = c["feat"]
            if f[4] >= 0.5 or f[3] >= 0.5 or f[5] >= 0.5:   # structural-override candidates excluded
                continue
            if c["p"] in L.PRONOUN:
                continue
            s = sel_fn(c["v"], c["p"])
            if s is not None:
                vals.append(s)
        if vals:
            keep_abs = float(np.percentile(vals, cfg["p_keep"]))
            drop_abs = float(np.percentile(vals, cfg["p_drop"]))
            if keep_abs <= drop_abs:                        # degenerate flat distribution guard
                keep_abs = drop_abs + 1e-6
        else:
            keep_abs, drop_abs = cfg["sel_keep"], cfg["sel_drop"]

    def target(c):
        f = c["feat"]
        p = c["p"]
        if f[4] >= 0.5:            # funcword / junk patient
            return 0.0
        if f[3] >= 0.5:            # preposition-governed = oblique
            return 0.0
        if f[5] >= 0.5:            # complementizer between v and p = clausal complement
            return 0.0
        if p in L.PRONOUN:         # pronoun in bare post-verbal position = valid object
            return 1.0 if f[2] >= 0.5 else 0.0
        s = sel_fn(c["v"], c["p"])
        if s is None:
            return None
        if s >= keep_abs:
            return 1.0
        if s <= drop_abs:
            return 0.0
        return None                # DEFER

    return target, keep_abs, drop_abs


def learn_weights(cands, target_fn, lr, epochs, seed):
    """8-dim error-driven logistic over feat8 -> the (shared) self-supervised target. cands must have feat8."""
    rng = np.random.default_rng(seed)
    w = np.zeros(N_FEAT)
    train = []
    for c in cands:
        t = target_fn(c)
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
# Localization diagnostics (make the sign result mechanistically decisive).
# ------------------------------------------------------------------------------------------------
def learn_ablated_dirpp(kind, order, reader_svo, sent_text, glove, cfg, seed):
    """w[f_dirpp] when f_subcatfreq is ABLATED (zeroed) -> isolates the directional cue's learned sign from
    collinearity with the subcat-frequency feature. If dirpp is genuinely learned as anti-patient, it must be
    negative here regardless of subcatfreq."""
    cands = build_cands(order, reader_svo, sent_text)
    sel_fn, _ = build_teacher(cands, glove, kind, cfg)
    target_fn, keep_abs, _ = make_target_fn(cands, sel_fn, cfg)
    subcat_freq, _ = MA.build_subcat_freq_table(cands, sel_fn, keep_abs)
    MA.extend_features(cands, subcat_freq, lambda v: v in MA_SEED)
    for c in cands:
        c["feat8"][SI] = 0.0
    w, _ = learn_weights(cands, target_fn, cfg["lr"], cfg["epochs"], seed)
    return round(float(w[DI]), 4)


def second_barrier_diag(kind, order, reader_svo, sent_text, glove, cfg):
    """Among candidates where f_dirpp fires (MA verb + directional context), how many does THIS teacher STILL
    label a coherent patient (target==1)? A decontamination that solved the rule would drive these to 0."""
    cands = build_cands(order, reader_svo, sent_text)
    sel_fn, tdiag = build_teacher(cands, glove, kind, cfg)
    target_fn, keep_abs, drop_abs = make_target_fn(cands, sel_fn, cfg)
    subcat_freq, _ = MA.build_subcat_freq_table(cands, sel_fn, keep_abs)
    MA.extend_features(cands, subcat_freq, lambda v: v in MA_SEED)
    n1 = n0 = nn = 0
    still_coherent = []
    for c in cands:
        if c["feat8"][DI] >= 0.5:
            t = target_fn(c)
            if t == 1.0:
                n1 += 1
                s = sel_fn(c["v"], c["p"])
                still_coherent.append([c["v"], c["p"], round(s, 3) if s is not None else None])
            elif t == 0.0:
                n0 += 1
            else:
                nn += 1
    return {"teacher_kind": kind, "keep_abs": round(keep_abs, 4),
            "n_dirpp_fires": n1 + n0 + nn, "n_still_labeled_patient_target1": n1,
            "n_labeled_not_patient_target0": n0, "n_defer": nn,
            "directional_patients_still_coherent": still_coherent[:12],
            "ref_path": tdiag.get("ref_path")}


def subcat_contam_vs_decontam(order, reader_svo, sent_text, glove, cfg):
    """Per MA verb: coherent-direct-patient rate under contam vs decontam teacher (was the SELF-contamination
    loop actually broken? decontam should give MA verbs LOWER subcatfreq than contam)."""
    out = {}
    tables = {}
    for kind in ("contam", "decontam"):
        cands = build_cands(order, reader_svo, sent_text)
        sel_fn, _ = build_teacher(cands, glove, kind, cfg)
        _, keep_abs, _ = make_target_fn(cands, sel_fn, cfg)
        subcat_freq, _ = MA.build_subcat_freq_table(cands, sel_fn, keep_abs)
        tables[kind] = subcat_freq
    ma_present = sorted(v for v in set(tables["contam"]) & set(tables["decontam"]) if v in MA_SEED)
    for v in ma_present:
        out[v] = {"contam": round(float(tables["contam"][v]), 4),
                  "decontam": round(float(tables["decontam"][v]), 4),
                  "dropped": bool(tables["decontam"][v] < tables["contam"][v] - 1e-6)}
    n_drop = sum(1 for v in out if out[v]["dropped"])
    return {"per_ma_verb": out, "n_ma_verbs": len(out), "n_subcatfreq_dropped_decontam": n_drop,
            "self_contamination_reduced_frac": round(n_drop / len(out), 4) if out else 0.0}


# ------------------------------------------------------------------------------------------------
# ARM runner (identical body for D_contam and E_decontam; only teacher kind differs). Mirrors
# MA.run_arm_D's construction + reading-order logic exactly.
# ------------------------------------------------------------------------------------------------
def run_arm(kind, order, reader_svo, sent_text, glove, cfg, seed, ma_membership=None, use_ma_construction=True):
    if ma_membership is None:
        ma_membership = lambda v: v in MA_SEED
    cands = build_cands(order, reader_svo, sent_text)

    sel_fn, tdiag = build_teacher(cands, glove, kind, cfg)
    target_fn, keep_abs, drop_abs = make_target_fn(cands, sel_fn, cfg)
    subcat_freq, subcat_diag = MA.build_subcat_freq_table(cands, sel_fn, keep_abs)
    MA.extend_features(cands, subcat_freq, ma_membership)
    w, n_train = learn_weights(cands, target_fn, cfg["lr"], cfg["epochs"], seed)

    # held-out verb split (SAME construction as LCCP/MA for parity)
    all_verbs = sorted(set(c["v"] for c in cands))
    rng = np.random.default_rng(seed + 1)
    perm = rng.permutation(len(all_verbs))
    n_heldout = max(1, int(round(cfg["heldout_frac"] * len(all_verbs))))
    heldout_verbs = set(all_verbs[i] for i in perm[:n_heldout])
    seen_verbs = set(all_verbs) - heldout_verbs

    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)

    verb_best = defaultdict(list)
    for (sid, v), cs in inst_groups.items():
        verb_best[v].append(max(score8(w, c["feat8"]) for c in cs))
    verb_trans = {v: float(np.mean(b)) for v, b in verb_best.items()}

    seen_ma = sorted(v for v in seen_verbs if ma_membership(v) and v in verb_trans)
    ma_constr_prior = float(np.mean([verb_trans[v] for v in seen_ma])) if seen_ma else None

    prof = {}
    for v in all_verbs:
        insts = [cs for (sid, vv), cs in inst_groups.items() if vv == v]
        if not insts:
            continue
        feats = [np.mean(np.stack([c["feat8"][1:7] for c in cs], 0), 0) for cs in insts]
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
            return ma_constr_prior
        if v in vconstr:
            return constr_trans.get(vconstr[v])
        j = nonma_heldout_construction(v)
        return constr_trans.get(j) if j is not None else None

    KAPPA = cfg.get("kappa", 1.5)
    per_inst_order = []
    for sid in order:
        for key in [k for k in inst_groups if k[0] == sid]:
            per_inst_order.append(key)
    t_run = defaultdict(lambda: [0.0, 0])
    kept = []
    graded = []
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
            kept.append((best["sid"], best["tup"]))
        graded.append({"sid": sid, "v": v, "p": best["p"], "best_sc": round(best_sc, 4), "kept": keep_patient})
        if v in seen_verbs:
            t_run[v][0] += best_sc
            t_run[v][1] += 1

    artifacts = {
        "teacher_kind": kind, "teacher_diag": tdiag,
        "w": [round(float(x), 4) for x in w], "feat_names": FEAT_NAMES_D, "n_train": n_train,
        "keep_abs": round(keep_abs, 4), "drop_abs": round(drop_abs, 4),
        "w_f_dirpp": round(float(w[DI]), 4), "w_f_subcatfreq": round(float(w[SI]), 4),
        "ma_construction_learned_prior": (round(ma_constr_prior, 4) if ma_constr_prior is not None else None),
        "n_seen_ma_verbs": len(seen_ma), "seen_ma_verbs": seen_ma,
        "subcat_freq_ma_sample": {v: subcat_diag["per_verb"][v] for v in sorted(subcat_diag["per_verb"])
                                  if v in MA_SEED and subcat_diag["per_verb"][v]["n_inst"] >= 1},
        "subcat_freq_global": subcat_diag["global_coherent_patient_rate"],
    }
    return kept, artifacts, graded, w, subcat_freq


# ------------------------------------------------------------------------------------------------
# Must-fail control (genuine-learning test), run on the DECONTAMINATED arm.
# ------------------------------------------------------------------------------------------------
def must_fail_control(order, reader_svo, sent_text, glove, cfg, seed, M):
    """Degrade the directional-PP cue reliability by randomizing MA class membership per verb -> the LEARNED
    |w[f_dirpp]| must DROP (the cue no longer predicts the independent low-coherence target). Deterministic
    (seeded numpy rng, NOT builtin hash). Also reports whether the FP_a win survives membership randomization
    (a surviving win = construction-determined, not learned)."""
    _, art_clean, _, w_clean, _ = run_arm("decontam", order, reader_svo, sent_text, glove, cfg, seed)
    rng = np.random.default_rng(seed + 101)
    all_verbs = sorted(set(L.lemma_verb(t[0]) for sid in order for t in reader_svo[sid]))
    n_ma = sum(1 for v in all_verbs if v in MA_SEED)
    perm = rng.permutation(len(all_verbs))
    rand_ma = set(all_verbs[perm[i]] for i in range(min(n_ma, len(all_verbs))))
    ma_rand = lambda v: v in rand_ma
    keptD_deg, art_deg, _, w_deg, _ = run_arm("decontam", order, reader_svo, sent_text, glove, cfg, seed,
                                              ma_membership=ma_rand, use_ma_construction=True)
    keptE_clean, _, _, _, _ = run_arm("decontam", order, reader_svo, sent_text, glove, cfg, seed)
    lccp_cfg = {k: v for k, v in cfg.items() if k != "seeds"}
    lccp_cfg["seed"] = seed
    keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
    fpaC0, _ = MA.fp_a(keptC0, M)
    fpaClean, _ = MA.fp_a(keptE_clean, M)
    fpaDeg, _ = MA.fp_a(keptD_deg, M)
    wc, wd = abs(float(w_clean[DI])), abs(float(w_deg[DI]))
    red_clean = fpaC0 - fpaClean
    red_deg = fpaC0 - fpaDeg
    return {"w_dirpp_clean": round(float(w_clean[DI]), 4), "w_dirpp_degraded": round(float(w_deg[DI]), 4),
            "w_dirpp_clean_abs": round(wc, 4), "w_dirpp_degraded_abs": round(wd, 4),
            "weight_drops_when_degraded": bool(wd < wc - 1e-6),
            "clean_sign_negative": bool(float(w_clean[DI]) < 0.0),
            "fp_a_reduction_clean_membership": round(red_clean, 4),
            "fp_a_reduction_random_membership": round(red_deg, 4),
            "fp_a_win_collapses_under_random_membership": bool(red_deg < red_clean - 0.05)}


# ------------------------------------------------------------------------------------------------
# Config + run.
# ------------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4,
               target_mode="percentile", p_keep=60.0, p_drop=40.0, disp_thr=2, min_ref=8, seeds=[7])


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], sel_keep=0.28,
               sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25,
               k_constructions=4, target_mode="percentile", p_keep=60.0, p_drop=40.0, disp_thr=2,
               min_ref=8, seeds=[7, 13, 19])


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

    M = MA.motion_aspectual_instances(reader_svo, gold, order)

    per_seed = []
    ref = {}
    for seed in cfg["seeds"]:
        lccp_cfg = {k: v for k, v in cfg.items() if k != "seeds"}
        lccp_cfg["seed"] = seed
        keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
        keptD, artD, gradedD, wD, subD = run_arm("contam", order, reader_svo, sent_text, glove, cfg, seed)
        keptE, artE, gradedE, wE, subE = run_arm("decontam", order, reader_svo, sent_text, glove, cfg, seed)
        abl_dirpp_E = learn_ablated_dirpp("decontam", order, reader_svo, sent_text, glove, cfg, seed)
        abl_dirpp_D = learn_ablated_dirpp("contam", order, reader_svo, sent_text, glove, cfg, seed)

        mC = L.score_arm(keptC0, gold)
        mD = L.score_arm(keptD, gold)
        mE = L.score_arm(keptE, gold)
        fpaC, keepsC = MA.fp_a(keptC0, M)
        fpaD, keepsD = MA.fp_a(keptD, M)
        fpaE, keepsE = MA.fp_a(keptE, M)
        per_seed.append({
            "seed": seed,
            "C0": {"precision": mC["precision"], "recall": mC["recall"], "f1": mC["f1"], "n_pred": mC["n_pred"]},
            "D_contam": {"precision": mD["precision"], "recall": mD["recall"], "f1": mD["f1"], "n_pred": mD["n_pred"]},
            "E_decontam": {"precision": mE["precision"], "recall": mE["recall"], "f1": mE["f1"], "n_pred": mE["n_pred"]},
            "fp_a_C0": round(fpaC, 4), "fp_a_D": round(fpaD, 4), "fp_a_E": round(fpaE, 4),
            "ma_keeps_C0": keepsC, "ma_keeps_D": keepsD, "ma_keeps_E": keepsE,
            "fp_a_reduction_E": round(fpaC - fpaE, 4), "fp_a_reduction_D": round(fpaC - fpaD, 4),
            "recall_retention_E_over_C0": round((mE["recall"] / mC["recall"]) if mC["recall"] > 0 else 0.0, 4),
            "w_f_dirpp_D": artD["w_f_dirpp"], "w_f_dirpp_E": artE["w_f_dirpp"],
            "w_f_subcatfreq_D": artD["w_f_subcatfreq"], "w_f_subcatfreq_E": artE["w_f_subcatfreq"],
            "keep_abs_D": artD["keep_abs"], "keep_abs_E": artE["keep_abs"],
            "ma_prior_D": artD["ma_construction_learned_prior"], "ma_prior_E": artE["ma_construction_learned_prior"],
            "w_f_dirpp_E_subcatfreq_ablated": abl_dirpp_E, "w_f_dirpp_D_subcatfreq_ablated": abl_dirpp_D,
        })
        if seed == cfg["seeds"][0]:
            ref = {"keptC0": keptC0, "keptD": keptD, "keptE": keptE, "artD": artD, "artE": artE,
                   "gradedE": gradedE, "subE": subE}
            ref["triC0"], ref["exC0"] = MA.triage_fps(keptC0, gold, reader_svo, order)
            ref["triE"], ref["exE"] = MA.triage_fps(keptE, gold, reader_svo, order)

    def agg(key, sub=None):
        vals = [(p[key][sub] if sub else p[key]) for p in per_seed]
        return round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)

    fpaC_m, fpaC_s = agg("fp_a_C0")
    fpaD_m, fpaD_s = agg("fp_a_D")
    fpaE_m, fpaE_s = agg("fp_a_E")
    redE_m, redE_s = agg("fp_a_reduction_E")
    rretE_m, rretE_s = agg("recall_retention_E_over_C0")
    pC_m, _ = agg("C0", "precision")
    pD_m, _ = agg("D_contam", "precision")
    pE_m, _ = agg("E_decontam", "precision")
    rC_m, _ = agg("C0", "recall")
    rE_m, _ = agg("E_decontam", "recall")

    # per-seed learning diagnostics
    wdirE = [p["w_f_dirpp_E"] for p in per_seed]
    wdirD = [p["w_f_dirpp_D"] for p in per_seed]
    wdirE_abl = [p["w_f_dirpp_E_subcatfreq_ablated"] for p in per_seed]
    wdirD_abl = [p["w_f_dirpp_D_subcatfreq_ablated"] for p in per_seed]
    redE_per = [p["fp_a_reduction_E"] for p in per_seed]
    e_sign_all_negative = all(x < 0 for x in wdirE)
    e_sign_all_negative_ablated = all(x < 0 for x in wdirE_abl)
    d_sign_all_nonneg = all(x >= 0 for x in wdirD)
    fp_a_seed_stable_E = all(x > 1e-9 for x in redE_per)

    # localization diagnostics (seed-independent): was self-contamination broken? does a SECOND barrier remain?
    barrier_contam = second_barrier_diag("contam", order, reader_svo, sent_text, glove, cfg)
    barrier_decontam = second_barrier_diag("decontam", order, reader_svo, sent_text, glove, cfg)
    self_contam = subcat_contam_vs_decontam(order, reader_svo, sent_text, glove, cfg)

    mustfail = must_fail_control(order, reader_svo, sent_text, glove, cfg, cfg["seeds"][0], M)
    pred4 = MA.graded_score_report(ref["gradedE"], gold, M)

    # direct-gate CEILING recomputed with the DECONTAMINATED subcat cues (reachable-target reference)
    keptDirect = MA.apply_direct_gate(ref["keptC0"], sent_text, ref["subE"])
    mDirect = L.score_arm(keptDirect, gold)
    fpa_direct, keeps_direct = MA.fp_a(keptDirect, M)
    mC0ref = L.score_arm(ref["keptC0"], gold)
    ceiling = {
        "note": "hand-applied structural gate (dirpp OR low decontam-subcat) over arm-C0; DIAGNOSTIC ceiling "
                "only (NOT learned). The LEARNED arm E should approach this without hand-installing the rule.",
        "fp_a_direct_gate": round(fpa_direct, 4), "ma_keeps_direct": keeps_direct,
        "overall_precision_direct": mDirect["precision"], "overall_recall_direct": mDirect["recall"],
        "recall_retention_direct_over_C0": round((mDirect["recall"] / mC0ref["recall"]) if mC0ref["recall"] > 0 else 0.0, 4),
    }

    # VERDICT (the LEARNING test)
    must_fires = bool(mustfail["weight_drops_when_degraded"])
    if (not e_sign_all_negative) or (not must_fires) or (not fp_a_seed_stable_E) or (rretE_m < 0.40):
        verdict = "HARD_FAIL_DECONTAM_INSUFFICIENT"
    elif e_sign_all_negative and must_fires and fp_a_seed_stable_E and fpaE_m <= 0.20 and rretE_m >= 0.60:
        verdict = "HARD_PASS_GENUINE_LEARNING"
    else:
        verdict = "MIDDLE_BAND"

    hashes = {"C0_lccp_armC": kept_hash(ref["keptC0"]), "D_contam": kept_hash(ref["keptD"]),
              "E_decontam": kept_hash(ref["keptE"])}
    arms_differ = (hashes["C0_lccp_armC"] != hashes["D_contam"]
                   and hashes["D_contam"] != hashes["E_decontam"]
                   and hashes["C0_lccp_armC"] != hashes["E_decontam"])
    baseline_in_band = bool(0.05 < pC_m < 0.95)
    # discriminator fires: the two teachers DIVERGE on the dirpp sign AND E suppresses > 0 MA FPs
    discriminator_fires = bool((wdirE[0] < 0) and (wdirD[0] >= 0)
                               and (per_seed[0]["ma_keeps_E"] < per_seed[0]["ma_keeps_C0"]))

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict,
        "primary_metric": "GENUINE-LEARNING test: w[f_dirpp] sign robustness + must-fail control fires + "
                          "FP_a seed-stability + approach to direct-gate ceiling (independent gold, cat-c held OUT)",
        "denominator_M_motion_aspectual_nopat_instances": len(M),
        "fp_a_C0_mean": fpaC_m, "fp_a_C0_std": fpaC_s,
        "fp_a_D_contam_mean": fpaD_m, "fp_a_D_contam_std": fpaD_s,
        "fp_a_E_decontam_mean": fpaE_m, "fp_a_E_decontam_std": fpaE_s,
        "fp_a_reduction_E_mean": redE_m, "fp_a_reduction_E_std": redE_s,
        "recall_retention_E_mean": rretE_m, "recall_retention_E_std": rretE_s,
        "overall_precision_C0_mean": pC_m, "overall_precision_D_mean": pD_m, "overall_precision_E_mean": pE_m,
        "overall_recall_C0_mean": rC_m, "overall_recall_E_mean": rE_m,
        "LEARNING_w_f_dirpp_E_per_seed": wdirE, "LEARNING_w_f_dirpp_D_per_seed": wdirD,
        "LEARNING_w_f_dirpp_E_subcatfreq_ablated_per_seed": wdirE_abl,
        "LEARNING_w_f_dirpp_D_subcatfreq_ablated_per_seed": wdirD_abl,
        "LEARNING_e_dirpp_all_negative": bool(e_sign_all_negative),
        "LEARNING_e_dirpp_all_negative_ablated": bool(e_sign_all_negative_ablated),
        "LEARNING_d_dirpp_all_nonneg": bool(d_sign_all_nonneg),
        "LEARNING_fp_a_reduction_E_per_seed": redE_per,
        "LEARNING_fp_a_seed_stable_E": bool(fp_a_seed_stable_E),
        "localization_self_contamination_broken": self_contam,
        "localization_second_barrier_contam": barrier_contam,
        "localization_second_barrier_decontam": barrier_decontam,
        "mustfail_control": mustfail,
        "prediction4_graded_argument_hood": pred4,
        "direct_gate_ceiling_decontam_cues": ceiling,
        "per_seed": per_seed,
        "step1_triage_C0": {"counts": ref["triC0"], "examples": ref["exC0"]},
        "step1_triage_E": {"counts": ref["triE"], "examples": ref["exE"]},
        "arm_E_artifacts_seed0": ref["artE"], "arm_D_artifacts_seed0": ref["artD"],
        "kept_hashes": hashes, "arms_differ_verified": arms_differ,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "adaptive_with_discriminator_gate",
        "n_sentences": len(order), "n_reader_svo": sum(len(reader_svo[sid]) for sid in order),
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "seeds": cfg["seeds"], "config": {k: v for k, v in cfg.items()},
        "ac1817_reference": {
            "note": "the CONTAMINATED route that failed (MEASURED@data/exp_lccp_motion_aspectual_subcat_break_v1/metrics.json)",
            "w_f_dirpp_per_seed": [0.4467, 0.4439, 0.4534], "fp_a_reduction_per_seed": [0.0333, 0.0333, 0.2333],
            "mustfail_drops": False, "mustfail_w_clean_abs": 0.4467, "mustfail_w_deg_abs": 0.9333,
            "direct_gate_ceiling_fp_a": 0.100, "direct_gate_ceiling_P": 0.541},
        "HONESTY_GUARD": ("Even full success caps overall precision ~0.541 on arm-C0 scope, BELOW the stacked "
                          "0.557 patient-lens reader. Value here is METHODOLOGICAL (a rule GENUINELY LEARNED via "
                          "a decontaminated signal, not hand-installed) + modest precision, NOT breaking 0.557. "
                          "The direct-gate ceiling is a HAND-APPLIED diagnostic, reported as a reference NOT a "
                          "learned result. A stack re-measure is a SEPARATE step, not claimed here."),
        "REQUIRED_FIELDS": ["verdict", "fp_a_C0_mean", "fp_a_D_contam_mean", "fp_a_E_decontam_mean",
                            "fp_a_reduction_E_mean", "recall_retention_E_mean", "LEARNING_w_f_dirpp_E_per_seed",
                            "LEARNING_w_f_dirpp_E_subcatfreq_ablated_per_seed", "LEARNING_e_dirpp_all_negative",
                            "LEARNING_e_dirpp_all_negative_ablated", "LEARNING_fp_a_seed_stable_E",
                            "localization_self_contamination_broken", "localization_second_barrier_decontam",
                            "mustfail_control", "direct_gate_ceiling_decontam_cues", "per_seed"],
    }
    msg = (f"{verdict} | M={len(M)} | FP_a C0={fpaC_m:.3f} D_contam={fpaD_m:.3f} E_decontam={fpaE_m:.3f}+-{fpaE_s:.3f} "
           f"| redE={redE_m:+.3f}+-{redE_s:.3f} RretE={rretE_m:.3f} "
           f"| w_dirpp E/seed={wdirE} D/seed={wdirD} Eneg_all={e_sign_all_negative} "
           f"| redE/seed={redE_per} seedStable={fp_a_seed_stable_E} "
           f"| mustfail: w_clean={mustfail['w_dirpp_clean']:+.3f} w_deg={mustfail['w_dirpp_degraded']:+.3f} "
           f"|w|drops={mustfail['weight_drops_when_degraded']} cleanNeg={mustfail['clean_sign_negative']} "
           f"| ceiling FP_a={ceiling['fp_a_direct_gate']:.3f} P={ceiling['overall_precision_direct']:.3f} "
           f"| overallP C0={pC_m:.3f} E={pE_m:.3f} | base_in_band={baseline_in_band} discrim={discriminator_fires} "
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
    assert out["arms_differ_verified"], "META_RULE_AF: arms C0/D/E not all distinct"
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, out)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  E teacher diag: {out['arm_E_artifacts_seed0']['teacher_diag']}", flush=True)
    print(f"  E learned 8-weights: {dict(zip(FEAT_NAMES_D, out['arm_E_artifacts_seed0']['w']))}", flush=True)
    print(f"  D learned 8-weights: {dict(zip(FEAT_NAMES_D, out['arm_D_artifacts_seed0']['w']))}", flush=True)
    for p in out["per_seed"]:
        print(f"  [seed {p['seed']}] FP_a C0={p['fp_a_C0']:.3f} D={p['fp_a_D']:.3f} E={p['fp_a_E']:.3f} "
              f"redE={p['fp_a_reduction_E']:+.3f} | w_dirpp D={p['w_f_dirpp_D']:+.3f} E={p['w_f_dirpp_E']:+.3f} "
              f"| overallP C0={p['C0']['precision']:.3f} E={p['E_decontam']['precision']:.3f} "
              f"RretE={p['recall_retention_E_over_C0']:.3f}", flush=True)
    print(f"  [ablated w_dirpp (no subcatfreq)] E/seed={out['LEARNING_w_f_dirpp_E_subcatfreq_ablated_per_seed']} "
          f"D/seed={out['LEARNING_w_f_dirpp_D_subcatfreq_ablated_per_seed']}", flush=True)
    sc = out["localization_self_contamination_broken"]
    print(f"  [self-contam broken] {sc['n_subcatfreq_dropped_decontam']}/{sc['n_ma_verbs']} MA verbs' subcatfreq "
          f"dropped under decontam (frac={sc['self_contamination_reduced_frac']})", flush=True)
    bc = out["localization_second_barrier_contam"]; bd = out["localization_second_barrier_decontam"]
    print(f"  [2nd barrier contam ] dirpp-fires still-labeled-patient={bc['n_still_labeled_patient_target1']}"
          f"/{bc['n_dirpp_fires']} e.g.{bc['directional_patients_still_coherent'][:5]}", flush=True)
    print(f"  [2nd barrier decontam] dirpp-fires still-labeled-patient={bd['n_still_labeled_patient_target1']}"
          f"/{bd['n_dirpp_fires']} e.g.{bd['directional_patients_still_coherent'][:5]}", flush=True)
    print(f"  [mustfail] {out['mustfail_control']}", flush=True)
    print(f"  [ceiling]  {out['direct_gate_ceiling_decontam_cues']}", flush=True)
    print(f"  [triage C0] {out['step1_triage_C0']['counts']}", flush=True)
    print(f"  [triage E ] {out['step1_triage_E']['counts']}", flush=True)
    print(f"  [pred4] {out['prediction4_graded_argument_hood']}", flush=True)
    print(f"  [HONESTY] {out['HONESTY_GUARD']}", flush=True)
    return out


def self_test():
    # 1. decontam teacher: a high-dispersion filler (occurs with many verbs) scores LOWER than a verb-specific
    #    content patient, against the LOO purified reference. Synthetic mini-corpus.
    rng = np.random.default_rng(0)
    dim = 8
    obj = rng.normal(size=dim); obj /= np.linalg.norm(obj)          # "object-type" direction
    loc = rng.normal(size=dim); loc /= np.linalg.norm(loc)          # "location-type" direction (adjunct)
    glove = {}
    cands = []
    postv = np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0])                # bare content patient feature row

    def add(v, p, vec):
        glove[p] = vec / np.linalg.norm(vec)
        cands.append({"sid": f"s{len(cands)}", "v": v, "a": "x", "p": p, "tup": (v, "x", p),
                      "feat": postv.copy(), "_sent": f"{v} {p}"})
    # 4 transitive verbs each with their own verb-specific object (low dispersion); "home" adjunct with all 4
    for i, v in enumerate(["build", "make", "bake", "carve"]):
        add(v, f"obj{i}", obj + 0.15 * rng.normal(size=dim))        # object-like, verb-specific
        add(v, "home", loc + 0.05 * rng.normal(size=dim))           # location-like, appears with ALL verbs
    sel_dec, diag = build_teacher(cands, glove, "decontam", dict(disp_thr=2, min_ref=4))
    s_obj = sel_dec("build", "obj0")
    s_home = sel_dec("build", "home")
    assert diag["ref_path"] == "dispersion_purified", f"expected purified ref, got {diag['ref_path']}"
    assert s_obj is not None and s_home is not None
    assert s_obj > s_home, f"decontam: verb-specific object ({s_obj:.3f}) must score > adjunct home ({s_home:.3f})"
    # 2. contam teacher: build's OWN home is in build's self-centroid -> home scores HIGH for build (the bug)
    sel_con, _ = build_teacher(cands, glove, "contam", {})
    s_home_con = sel_con("build", "home")
    assert s_home_con is not None and s_home_con > s_home, \
        f"contam should rate build/home ({s_home_con:.3f}) HIGHER than decontam ({s_home:.3f}) (self-fulfilling)"
    # 3. lemma parity + dirpp reuse
    assert L.lemma_verb("came") == "come"
    toks = L.tokenize("charley came home from school")
    iv, ip = L.find_pair_positions(toks, "came", "home")
    assert MA.dirpp_fires("come", toks, iv, ip, "home", lambda v: v in MA_SEED) == 1.0
    # 4. end-to-end smoke: arms differ + E dirpp sign is the discriminator
    cfg = cfg_smoke()
    out, _ = run_config(cfg, "smoke")
    assert out["arms_differ_verified"], "arms C0/D/E must all differ"
    wE = out["arm_E_artifacts_seed0"]["w"][DI]
    wD = out["arm_D_artifacts_seed0"]["w"][DI]
    print(f"[{ANCHOR_NAME}] self-test OK | decontam obj={s_obj:.3f} home={s_home:.3f} (obj>home) "
          f"contam home={s_home_con:.3f} | smoke: w_dirpp E={wE:+.3f} D={wD:+.3f} "
          f"FP_a C0={out['fp_a_C0_mean']:.3f} E={out['fp_a_E_decontam_mean']:.3f} "
          f"mustfail_drops={out['mustfail_control']['weight_drops_when_degraded']} verdict={out['verdict']}",
          flush=True)


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
