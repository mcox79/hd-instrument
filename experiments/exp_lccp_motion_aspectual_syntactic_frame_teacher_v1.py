"""FORK-(SYNTACTIC-TEACHER): does replacing the SEMANTIC-coherence learning signal with a PURELY-SYNTACTIC
FRAME-FREQUENCY teacher (positional/POS distribution over syntactic frames, NO GloVe cosine) make the
substrate GENUINELY LEARN the motion/aspectual argument-structure rule -- i.e. w[f_dirpp] learns the CORRECT
(negative) sign ROBUSTLY across seeds AND the must-fail control FIRES (degrade the directional cue -> the
learned weight DROPS)?

THIS IS A LEARNING-MECHANISM DEMONSTRATION, NOT A PRECISION PLAY. Success = the substrate learns the correct
structural rule the HONEST way (from a syntactic-distributional signal, not hand-installed). Precision caps
~0.55 on this class, BELOW the stacked 0.557 patient-lens reader; the deliverable is "did it learn the rule",
NOT "did it break 0.557".

WHY THE PRIOR TWO ROUTES FAILED (VET-confirmed, MEASURED):
  Both prior teachers were SEMANTIC-coherence (cosine to a GloVe patient-centroid).
  - subcat_break (contaminated self-centroid): w[f_dirpp] = [0.4467,0.4439,0.4534] POSITIVE (wrong), pred3
    must-fail drops=False. MEASURED@data/exp_lccp_motion_aspectual_subcat_break_v1/metrics.json.
  - decontam (leave-one-out dispersion-purified semantic teacher): w[f_dirpp] = [2.3451,2.3348,2.2668]
    POSITIVE (wrong, LARGER), verdict HARD_FAIL_DECONTAM_INSUFFICIENT.
    MEASURED@data/exp_lccp_motion_aspectual_decontam_teacher_v1/metrics.json:LEARNING_w_f_dirpp_E_per_seed.
  VET's decisive localization: a SEMANTIC-coherence signal CANNOT encode a SYNTACTIC anti-patient rule --
    "home" is a semantically-fine thing to come TO (high cosine to the patient centroid), so a coherence
    teacher rates it a good patient and f_dirpp co-occurs with target=1 -> learns POSITIVE. Structural-beats-
    semantic AT THE LEARNING-SIGNAL LEVEL. The VET named the untested, more-brain-faithful lever: "a purely-
    syntactic frame-frequency teacher (positional/POS distribution, no GloVe cosine), framed as mechanism
    demonstration, not a 0.557 breaker."
  CITED@notes/research_argument_adjunct_subcat_hard_residual_brain_drill_2026-07-19.md Angle-1: frame-freq is
    retrieved AT the verb, gradient, causally malleable = LEARNED (Ford-Bresnan-Kaplan lexical preference;
    Trueswell/Tanenhaus/Kello 1993); Angle-2: directional/goal phrase after a motion verb = distinct
    (unaccusative/oblique-goal) arg-structure, NOT a patient reading (Levin & Rappaport Hovav 1995).

THE PURELY-SYNTACTIC FRAME-FREQUENCY TEACHER (the ONE VARIABLE; NO GloVe, NO semantic cosine):
  For every post-verbal slot in the corpus, classify its SYNTACTIC FRAME TYPE from POSITIONAL / POS / closed-
  class evidence ONLY (a directional-word list + preposition position + verb-slot position):
    DIR   = the post-verbal element is a directional/locative adverb (home/there/back/away/out/up/down/...) OR
            is governed by a directional/path preposition (to/from/into/onto/toward/down/up/across/...) OR a
            directional particle sits right after the verb. Detected SYNTACTICALLY, no meaning consulted.
    DO    = a bare post-verbal NP that is NOT directional, NOT prep-governed, NOT funcword, NOT clausal =
            the canonical direct-object slot.
    (OBL/CLAUSE/FUNC = prep-governed non-directional / complementizer / junk -- not object-frame evidence.)
  Then per verb v the SYNTACTIC frame-frequency of taking a canonical object:
    P_do(v) = (n_DO(v) + k*global) / (n_DO(v) + n_DIR(v) + k)   add-k smoothed, backed off to the global DO
    rate. A motion verb (come/go/walk/sit) has its post-verbal slots DOMINATED by DIR frames (home/to X/down)
    -> P_do LOW. A transitive verb (make/build/open) has DO-dominated slots -> P_do HIGH.
  THE CRITICAL ANTI-CONTAMINATION PROPERTY (why syntactic beats semantic): the semantic teacher saw "home" as
    a fine patient (concrete noun, high cosine). The SYNTACTIC teacher classifies "come home" as a DIR frame
    (home is in the directional closed class) and does NOT count it as DO evidence -> P_do(come) stays LOW.
    This is EXACTLY the positional/POS signal a semantic-coherence signal cannot represent.
  TARGET (self-supervised, per candidate; replaces L.cand_target's semantic branch): structural overrides
    IDENTICAL to before (funcword/prep/clause -> 0; pronoun bare-postverbal -> 1). For a bare content post-
    verbal patient (incl. bare directional adverbs like "home"): target = 1 if P_do(v) >= keep_abs, 0 if
    <= drop_abs, else DEFER. keep_abs/drop_abs = percentiles of the per-candidate P_do distribution (auto-
    calibrated split, both classes guaranteed present).
  NON-CIRCULARITY (load-bearing): the teacher does NOT consult MA-membership and does NOT hand-seed motion
    verbs a low prior (unlike the semantic subcat table's MA_CLASS_PRIOR=0.15). P_do is derived PURELY from
    the corpus frame distribution. f_dirpp is a SEPARATE per-candidate structural feature (MA-membership
    gate). The logistic DISCOVERS that f_dirpp fires on candidates belonging to low-P_do verbs (target 0) ->
    learns w[f_dirpp] < 0 FROM the frame-frequency distribution -- NOT hand-installed. The must-fail control
    degrades that link and the weight must collapse.

ARMS (ONE VARIABLE = the LEARNING SIGNAL: semantic-coherence teacher vs syntactic-frame-frequency teacher;
EVERYTHING else identical -- same candidate gen, same 8 features {LCCP 6 + f_dirpp + f_subcatfreq}, same MA
construction row, same lr/epochs/keep_thr/subcat_thr/seeds, same reading pass, same percentile target rule):
  ARM C0        = LIVE LCCP arm-C recompute (the real ~0.500 baseline; features OFF). Reference point.
  ARM S_semantic= C0 + {f_dirpp, f_subcatfreq(=semantic coherence subcat freq), MA construction} with the
                  SEMANTIC-coherence teacher (the ac1817/decontam FAILED route, recomputed LIVE). The REAL
                  baseline (reproduces w[f_dirpp] POSITIVE / wrong-signed).
  ARM T_syntactic = identical to S_semantic but the TEACHER is the PURELY-SYNTACTIC frame-frequency teacher
                  (P_do; NO GloVe; f_subcatfreq(=P_do)). THE fix.

MEASURED (decisive -- the LEARNING test):
  PRIMARY: (1) w[f_dirpp](T) NEGATIVE for ALL seeds (vs POSITIVE for S_semantic); (2) the must-fail control
    FIRES for ALL seeds (degrade directional cue -> |w[f_dirpp]| DROPS); ALSO reported: sign robust under
    f_subcatfreq ablation (collinearity control) + a second teacher-reliance control (permute P_do across
    verbs -> weight collapses).
  SECONDARY: FP_a per arm (fraction of the motion/aspectual nopat instances the reader attached to that the
    arm still keeps a patient for); overall precision/recall per arm; the direct-gate ceiling; per-seed
    weights + signs; triage.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = ARM S_semantic (reproduces the FAILED semantic route, w[f_dirpp] > 0) AND the direct-
       gate CEILING (P ~0.55). NOT a strawman.
  (G2) ONE VARIABLE = semantic-coherence teacher vs syntactic-frame-frequency teacher; all else identical.
  (G3) CAN-FAIL-BOTH-WAYS: T can learn w[f_dirpp] < 0 robustly + must-fail fire (PASS) OR stay wrong-signed /
       must-fail vacuous (HARD-FAIL: even a syntactic-distributional signal can't teach it here -> the rule
       needs given-scaffolding or is at learned-ceiling; a real, decisive localization).
  (G4) difficulty ON: same motion/aspectual residual, independent gold, category-c contested cases held OUT.
  (G5) discriminator fires at smoke: T's w[f_dirpp] < 0 AND S_semantic's >= 0 (arms DIVERGE on the sign) AND
       the syntactic P_do actually separates motion verbs low from transitive verbs high AND kept sets differ.

VERDICT BANDS (pre-registered):
  HARD_PASS_GENUINE_SYNTACTIC_LEARNING: w_f_dirpp(T) < 0 for ALL seeds AND w_f_dirpp(T) < 0 for ALL seeds
    with f_subcatfreq ABLATED (collinearity-robust) AND the must-fail (membership-randomization) FIRES for
    ALL seeds (degraded |w| < clean |w| - 1e-6) AND S_semantic w_f_dirpp >= 0 for ALL seeds (the failed
    route reproduced).
  HARD_FAIL_SYNTACTIC_INSUFFICIENT: w_f_dirpp(T) >= 0 for ANY seed (still wrong-signed) OR the must-fail
    fails for ANY seed (vacuous: weight does not drop = construction-determined, not learned) OR S_semantic
    does NOT reproduce w>=0 (the baseline is not the failed route -> comparison invalid).
  MIDDLE_BAND: sign correct clean but not collinearity-robust, or must-fail partial across seeds.

HONESTY GUARD (mandatory; printed + stored): even FULL success caps overall precision ~0.55 on arm-C0 scope,
  BELOW the stacked 0.557 patient-lens reader. The value here is METHODOLOGICAL (a structural rule GENUINELY
  LEARNED from a purely-syntactic frame-frequency signal, not hand-installed) + modest precision, NOT breaking
  0.557. The direct-gate ceiling is a HAND-APPLIED diagnostic reference, NOT a learned result. No hand-applied
  number is reported as if learned. A stack re-measure is a SEPARATE step, not claimed here.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- ~225 reader candidates, a
  small syntactic frame-count pass + a tiny 8-dim logistic x a few epochs x 3 seeds x 3 arms + per-seed must-
  fail controls; wall < ~180s. Foreground local-to-completion (NO queue; NO push; NO remote-persist; needs
  needs_orchestrator_store_sync). Storage: no_storage (extraction-precision measurement). Determinism:
  OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib; no salted builtin hash / list(set); numpy rng
  seeded.

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (C0 vs S_semantic vs T_syntactic kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < arm-C0 precision < 0.95)
- discriminator fires at smoke (T w[f_dirpp] < 0 AND S_semantic >= 0; P_do separates; kept sets differ)
- multi-seed (3 seeds); must-fail run PER SEED; weights + signs aggregated per seed
- deterministic seeding; all numbers tagged MEASURED@/CITED@ (printed at run)
- clean-toy mechanism self-test (P_do separation + learned sign + must-fail on a synthetic corpus)
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

ANCHOR_NAME = "lccp_motion_aspectual_syntactic_frame_teacher_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_lccp_motion_aspectual_subcat_break_v1 as MA  # noqa: E402

ARMS = ["C0_lccp_armC", "S_semantic", "T_syntactic"]
FEAT_NAMES_D = MA.FEAT_NAMES_D          # ["bias","f_adj","f_postv","f_prep","f_func","f_clause","f_dirpp","f_subcatfreq"]
N_FEAT = MA.N_FEAT
MA_SEED = MA.MA_SEED
DI = FEAT_NAMES_D.index("f_dirpp")       # 6
SI = FEAT_NAMES_D.index("f_subcatfreq")  # 7

# ------------------------------------------------------------------------------------------------
# PURELY-SYNTACTIC directional/locative closed classes (NO semantics; positional/POS only).
# CITED@ Levin & Rappaport Hovav 1995 directional-PP diagnostic. Split from MA.DIRGOAL into a bare-adverb
# set (particles that can occupy a bare post-verbal slot and masquerade as a direct object) and a
# directional-preposition set (govern a following NP as a path/goal).
# ------------------------------------------------------------------------------------------------
DIR_ADV = {"home", "there", "here", "back", "away", "forth", "forward", "out", "in", "on", "off", "up",
           "down", "over", "near", "round", "along", "past", "across", "through", "abroad", "aside",
           "apart", "aboard", "upstairs", "downstairs", "upward", "downward", "onward", "hither", "thither",
           "aloft", "ashore", "inside", "outside", "indoors", "outdoors"}
DIR_PREP = {"to", "from", "into", "onto", "toward", "towards", "up", "down", "across", "through", "along",
            "past", "over", "out", "off", "upon", "in", "on", "at", "unto", "round", "about", "under",
            "above", "beneath", "behind", "beyond"}


def is_directional_slot(p_surf, toks, iv, ip):
    """PURELY-SYNTACTIC directional detector (no meaning consulted). True iff the post-verbal element is a
    directional/locative adverb, OR is governed by a directional/path preposition, OR a directional particle
    sits right after the verb."""
    if p_surf in DIR_ADV:
        return True
    if ip is not None:
        prev1 = toks[ip - 1] if ip - 1 >= 0 else ""
        prev2 = toks[ip - 2] if ip - 2 >= 0 else ""
        if prev1 in DIR_PREP or prev2 in DIR_PREP:
            return True
    if iv is not None:
        for k in range(iv + 1, min(iv + 3, len(toks))):
            if toks[k] in DIR_ADV:
                return True
    return False


# ------------------------------------------------------------------------------------------------
# Candidate builder (LCCP 6-feature candidates + _sent + cached positions/frame-type).
# ------------------------------------------------------------------------------------------------
def build_cands(order, reader_svo, sent_text):
    cands = []
    for sid in order:
        toks = L.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            feat, _ = L.candidate_features(toks, tup[0], tup[2])
            iv, ip = L.find_pair_positions(toks, tup[0], tup[2])
            c = {"sid": sid, "v": L.lemma_verb(tup[0]), "a": tup[1], "p": tup[2],
                 "tup": tup, "feat": feat, "_sent": sent_text[sid], "_iv": iv, "_ip": ip, "_toks": toks}
            c["_dir"] = bool(is_directional_slot(tup[2], toks, iv, ip))
            cands.append(c)
    return cands


def _frame_type(c):
    """Syntactic frame type of a candidate's slot (positional/POS only). One of DO/DIR/OBL/CLAUSE/FUNC/PREV."""
    f = c["feat"]
    if f[2] < 0.5:                 # not post-verbal
        return "PREV"
    if f[4] >= 0.5:               # funcword / junk
        return "FUNC"
    if f[5] >= 0.5:               # complementizer between v and p -> clausal
        return "CLAUSE"
    if c["_dir"]:                 # directional adverb / directional-prep-governed / directional particle
        return "DIR"
    if f[3] >= 0.5:               # prep-governed non-directional -> oblique
        return "OBL"
    return "DO"                   # bare post-verbal content, not directional/prep/func/clause -> canonical DO


# ------------------------------------------------------------------------------------------------
# SYNTACTIC FRAME-FREQUENCY TEACHER (the ONE VARIABLE). No GloVe. P_do(v) from corpus frame distribution.
# ------------------------------------------------------------------------------------------------
def build_syntactic_frame_table(cands, k_smooth=2.0, pdo_override=None):
    """Per verb: P_do(v) = smoothed frequency of a canonical-DO frame vs a directional frame in the verb's
    post-verbal slots. Purely syntactic (positional/POS closed-class typing). Returns (P_do, diagnostics).
    NON-CIRCULAR: does NOT consult MA-membership, does NOT hand-seed motion verbs a low prior; the low
    frame-frequency for motion verbs EMERGES from the directional frame count."""
    n_do = defaultdict(int)
    n_dir = defaultdict(int)
    n_other = defaultdict(int)
    tot_do = tot_dir = 0
    for c in cands:
        ft = _frame_type(c)
        if ft == "DO":
            n_do[c["v"]] += 1
            tot_do += 1
        elif ft == "DIR":
            n_dir[c["v"]] += 1
            tot_dir += 1
        else:
            n_other[c["v"]] += 1
    global_rate = (tot_do / (tot_do + tot_dir)) if (tot_do + tot_dir) > 0 else 0.5
    verbs = set(n_do) | set(n_dir) | set(n_other)
    P_do = {}
    diag = {}
    for v in verbs:
        nd, ndir = n_do[v], n_dir[v]
        pdo = (nd + k_smooth * global_rate) / (nd + ndir + k_smooth)
        P_do[v] = float(pdo)
        diag[v] = {"n_DO": nd, "n_DIR": ndir, "n_other": n_other[v], "P_do": round(float(pdo), 4)}
    if pdo_override is not None:
        # must-fail (teacher-reliance) control: replace P_do with a permuted mapping (breaks the frame-freq
        # <-> verb link) while preserving the marginal P_do distribution.
        P_do = dict(pdo_override)
    return P_do, {"global_do_rate": round(global_rate, 4), "k_smooth": k_smooth, "tot_DO": tot_do,
                  "tot_DIR": tot_dir, "n_verbs": len(verbs), "per_verb": diag}


def make_syntactic_target_fn(cands, P_do, cfg):
    """Return (target_fn(c)->0/1/None, keep_abs, drop_abs). Structural overrides identical to L.cand_target;
    for bare content post-verbal patients the VERB's syntactic frame-frequency P_do decides. keep_abs/drop_abs
    = percentiles of the per-candidate P_do distribution (guarantees both classes present)."""
    vals = []
    for c in cands:
        f = c["feat"]
        if f[2] < 0.5 or f[4] >= 0.5 or f[3] >= 0.5 or f[5] >= 0.5:
            continue
        if c["p"] in L.PRONOUN:
            continue
        pd = P_do.get(c["v"])
        if pd is not None:
            vals.append(pd)
    if vals:
        keep_abs = float(np.percentile(vals, cfg["p_keep"]))
        drop_abs = float(np.percentile(vals, cfg["p_drop"]))
        if keep_abs <= drop_abs:
            keep_abs = drop_abs + 1e-6
    else:
        keep_abs, drop_abs = 0.5, 0.35

    def target(c):
        f = c["feat"]
        p = c["p"]
        if f[4] >= 0.5:            # funcword / junk
            return 0.0
        if f[3] >= 0.5:            # prep-governed = oblique
            return 0.0
        if f[5] >= 0.5:            # clausal complement
            return 0.0
        if p in L.PRONOUN:         # bare post-verbal pronoun = valid object
            return 1.0 if f[2] >= 0.5 else 0.0
        if f[2] < 0.5:             # pre-verbal
            return None
        pd = P_do.get(c["v"])      # bare content post-verbal (incl bare directional adverb): frame-freq decides
        if pd is None:
            return None
        if pd >= keep_abs:
            return 1.0
        if pd <= drop_abs:
            return 0.0
        return None                # DEFER

    return target, keep_abs, drop_abs


def make_semantic_target_fn(cands, glove, cfg):
    """The FAILED semantic route (arm S baseline): sel(v,p) = GloVe cosine to the verb/global patient centroid;
    target = L.cand_target. Returns (target_fn, sel_fn, subcat_freq_dict)."""
    sel_fn, _vc, _gc = L.build_semantic_teacher(cands, glove)
    subcat_freq, _diag = MA.build_subcat_freq_table(cands, sel_fn, cfg["sel_keep"])

    def target(c):
        return L.cand_target(c, sel_fn, cfg["sel_keep"], cfg["sel_drop"])

    return target, sel_fn, subcat_freq


def learn_weights(cands, target_fn, lr, epochs, seed):
    """8-dim error-driven logistic over feat8 -> the (teacher-supplied) self-supervised target."""
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
# ARM runner (identical body for S_semantic and T_syntactic; only the TEACHER differs). Mirrors
# MA.run_arm_D / decontam run_arm construction + reading-order logic exactly.
# ------------------------------------------------------------------------------------------------
def run_arm(teacher_kind, order, reader_svo, sent_text, glove, cfg, seed,
            ma_membership=None, use_ma_construction=True, pdo_override=None):
    if ma_membership is None:
        ma_membership = lambda v: v in MA_SEED
    cands = build_cands(order, reader_svo, sent_text)

    if teacher_kind == "syntactic":
        P_do, tdiag = build_syntactic_frame_table(cands, pdo_override=pdo_override)
        target_fn, keep_abs, drop_abs = make_syntactic_target_fn(cands, P_do, cfg)
        subcat_freq = P_do                              # f_subcatfreq = the syntactic frame-frequency
        teacher_diag = {"kind": "syntactic", "global_do_rate": tdiag["global_do_rate"],
                        "tot_DO": tdiag["tot_DO"], "tot_DIR": tdiag["tot_DIR"], "n_verbs": tdiag["n_verbs"]}
    elif teacher_kind == "semantic":
        target_fn, sel_fn, subcat_freq = make_semantic_target_fn(cands, glove, cfg)
        keep_abs, drop_abs = cfg["sel_keep"], cfg["sel_drop"]
        teacher_diag = {"kind": "semantic", "note": "GloVe cosine to patient centroid (the FAILED route)"}
    else:
        raise ValueError(f"unknown teacher_kind {teacher_kind!r}")

    MA.extend_features(cands, subcat_freq, ma_membership)   # writes feat8 = concat(feat6, [f_dirpp, f_subcatfreq])
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

    # syntactic P_do sample for the MA verbs (glass-box: is the frame-freq low for motion verbs?)
    pdo_ma_sample = {}
    if teacher_kind == "syntactic":
        pdo_ma_sample = {v: tdiag["per_verb"][v] for v in sorted(tdiag["per_verb"])
                         if v in MA_SEED and (tdiag["per_verb"][v]["n_DO"] + tdiag["per_verb"][v]["n_DIR"]) >= 1}

    artifacts = {
        "teacher_kind": teacher_kind, "teacher_diag": teacher_diag,
        "w": [round(float(x), 4) for x in w], "feat_names": FEAT_NAMES_D, "n_train": n_train,
        "keep_abs": round(float(keep_abs), 4), "drop_abs": round(float(drop_abs), 4),
        "w_f_dirpp": round(float(w[DI]), 4), "w_f_subcatfreq": round(float(w[SI]), 4),
        "ma_construction_learned_prior": (round(ma_constr_prior, 4) if ma_constr_prior is not None else None),
        "n_seen_ma_verbs": len(seen_ma), "seen_ma_verbs": seen_ma,
        "P_do_ma_sample": pdo_ma_sample,
    }
    return kept, artifacts, graded, w, subcat_freq


# ------------------------------------------------------------------------------------------------
# Diagnostics.
# ------------------------------------------------------------------------------------------------
def learn_ablated_dirpp(teacher_kind, order, reader_svo, sent_text, glove, cfg, seed):
    """w[f_dirpp] when f_subcatfreq is ABLATED (zeroed) -> isolates the directional cue's learned sign from
    collinearity with the frame-frequency feature."""
    cands = build_cands(order, reader_svo, sent_text)
    if teacher_kind == "syntactic":
        P_do, _ = build_syntactic_frame_table(cands)
        target_fn, _, _ = make_syntactic_target_fn(cands, P_do, cfg)
        subcat_freq = P_do
    else:
        target_fn, _sel, subcat_freq = make_semantic_target_fn(cands, glove, cfg)
    MA.extend_features(cands, subcat_freq, lambda v: v in MA_SEED)
    for c in cands:
        c["feat8"][SI] = 0.0
    w, _ = learn_weights(cands, target_fn, cfg["lr"], cfg["epochs"], seed)
    return round(float(w[DI]), 4)


def must_fail_control(order, reader_svo, sent_text, glove, cfg, seed, M):
    """Genuine-learning controls, run on the SYNTACTIC arm. Deterministic (seeded numpy rng, NOT builtin hash).
    (A) MEMBERSHIP-RANDOMIZATION (the pre-registered gate control; comparable to the prior cells): randomize
        MA class-membership per verb -> f_dirpp fires on RANDOM verbs -> the LEARNED |w[f_dirpp]| must DROP
        (the directional feature no longer fires on the low-frame-freq verbs that carry the target-0 signal).
    (B) TEACHER-RELIANCE (permute P_do across verbs): break the frame-frequency <-> verb link while preserving
        the marginal P_do distribution -> the teacher target no longer tracks real frames -> |w[f_dirpp]|
        must DROP. Tests reliance on the REAL syntactic frame structure (not the f_dirpp feature)."""
    _, art_clean, _, w_clean, _ = run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed)

    # (A) membership randomization
    rng = np.random.default_rng(seed + 101)
    all_verbs = sorted(set(L.lemma_verb(t[0]) for sid in order for t in reader_svo[sid]))
    n_ma = sum(1 for v in all_verbs if v in MA_SEED)
    perm = rng.permutation(len(all_verbs))
    rand_ma = set(all_verbs[perm[i]] for i in range(min(n_ma, len(all_verbs))))
    ma_rand = lambda v: v in rand_ma
    keptA_deg, artA_deg, _, wA_deg, _ = run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed,
                                                ma_membership=ma_rand, use_ma_construction=True)

    # (B) teacher-reliance: permute P_do values across verbs (seeded)
    cands = build_cands(order, reader_svo, sent_text)
    P_do_true, _ = build_syntactic_frame_table(cands)
    verbs_sorted = sorted(P_do_true.keys())
    vals = np.array([P_do_true[v] for v in verbs_sorted])
    rng2 = np.random.default_rng(seed + 202)
    permB = rng2.permutation(len(verbs_sorted))
    P_do_perm = {verbs_sorted[i]: float(vals[permB[i]]) for i in range(len(verbs_sorted))}
    _, artB_deg, _, wB_deg, _ = run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed,
                                        pdo_override=P_do_perm)

    keptClean, _, _, _, _ = run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed)
    lccp_cfg = {k: v for k, v in cfg.items() if k != "seeds"}
    lccp_cfg["seed"] = seed
    keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
    fpaC0, _ = MA.fp_a(keptC0, M)
    fpaClean, _ = MA.fp_a(keptClean, M)
    fpaA, _ = MA.fp_a(keptA_deg, M)
    wc = abs(float(w_clean[DI])); wA = abs(float(wA_deg[DI])); wB = abs(float(wB_deg[DI]))
    return {"w_dirpp_clean": round(float(w_clean[DI]), 4),
            "w_dirpp_membership_randomized": round(float(wA_deg[DI]), 4),
            "w_dirpp_pdo_permuted": round(float(wB_deg[DI]), 4),
            "w_dirpp_clean_abs": round(wc, 4), "w_dirpp_membership_randomized_abs": round(wA, 4),
            "w_dirpp_pdo_permuted_abs": round(wB, 4),
            "weight_drops_membership": bool(wA < wc - 1e-6),
            "weight_drops_pdo_permute": bool(wB < wc - 1e-6),
            "clean_sign_negative": bool(float(w_clean[DI]) < 0.0),
            "fp_a_reduction_clean": round(fpaC0 - fpaClean, 4),
            "fp_a_reduction_membership_randomized": round(fpaC0 - fpaA, 4)}


# ------------------------------------------------------------------------------------------------
# Config + run.
# ------------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(slice_lessons=["L04", "L05"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4,
               p_keep=60.0, p_drop=40.0, seeds=[7])


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], sel_keep=0.28,
               sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25,
               k_constructions=4, p_keep=60.0, p_drop=40.0, seeds=[7, 13, 19])


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
        keptS, artS, gradedS, wS, subS = run_arm("semantic", order, reader_svo, sent_text, glove, cfg, seed)
        keptT, artT, gradedT, wT, subT = run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed)
        abl_dirpp_T = learn_ablated_dirpp("syntactic", order, reader_svo, sent_text, glove, cfg, seed)
        abl_dirpp_S = learn_ablated_dirpp("semantic", order, reader_svo, sent_text, glove, cfg, seed)
        mf = must_fail_control(order, reader_svo, sent_text, glove, cfg, seed, M)

        mC = L.score_arm(keptC0, gold)
        mS = L.score_arm(keptS, gold)
        mT = L.score_arm(keptT, gold)
        fpaC, keepsC = MA.fp_a(keptC0, M)
        fpaS, keepsS = MA.fp_a(keptS, M)
        fpaT, keepsT = MA.fp_a(keptT, M)
        per_seed.append({
            "seed": seed,
            "C0": {"precision": mC["precision"], "recall": mC["recall"], "f1": mC["f1"], "n_pred": mC["n_pred"]},
            "S_semantic": {"precision": mS["precision"], "recall": mS["recall"], "f1": mS["f1"], "n_pred": mS["n_pred"]},
            "T_syntactic": {"precision": mT["precision"], "recall": mT["recall"], "f1": mT["f1"], "n_pred": mT["n_pred"]},
            "fp_a_C0": round(fpaC, 4), "fp_a_S": round(fpaS, 4), "fp_a_T": round(fpaT, 4),
            "ma_keeps_C0": keepsC, "ma_keeps_S": keepsS, "ma_keeps_T": keepsT,
            "fp_a_reduction_T": round(fpaC - fpaT, 4), "fp_a_reduction_S": round(fpaC - fpaS, 4),
            "recall_retention_T_over_C0": round((mT["recall"] / mC["recall"]) if mC["recall"] > 0 else 0.0, 4),
            "w_f_dirpp_S": artS["w_f_dirpp"], "w_f_dirpp_T": artT["w_f_dirpp"],
            "w_f_subcatfreq_S": artS["w_f_subcatfreq"], "w_f_subcatfreq_T": artT["w_f_subcatfreq"],
            "w_f_dirpp_T_subcatfreq_ablated": abl_dirpp_T, "w_f_dirpp_S_subcatfreq_ablated": abl_dirpp_S,
            "mustfail": mf,
        })
        if seed == cfg["seeds"][0]:
            ref = {"keptC0": keptC0, "keptS": keptS, "keptT": keptT, "artS": artS, "artT": artT,
                   "gradedT": gradedT, "subT": subT}
            ref["triC0"], ref["exC0"] = MA.triage_fps(keptC0, gold, reader_svo, order)
            ref["triT"], ref["exT"] = MA.triage_fps(keptT, gold, reader_svo, order)

    def agg(key, sub=None):
        vals = [(p[key][sub] if sub else p[key]) for p in per_seed]
        return round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)

    fpaC_m, fpaC_s = agg("fp_a_C0")
    fpaS_m, fpaS_s = agg("fp_a_S")
    fpaT_m, fpaT_s = agg("fp_a_T")
    redT_m, redT_s = agg("fp_a_reduction_T")
    rretT_m, rretT_s = agg("recall_retention_T_over_C0")
    pC_m, _ = agg("C0", "precision")
    pS_m, _ = agg("S_semantic", "precision")
    pT_m, _ = agg("T_syntactic", "precision")
    rC_m, _ = agg("C0", "recall")
    rT_m, _ = agg("T_syntactic", "recall")

    wdirT = [p["w_f_dirpp_T"] for p in per_seed]
    wdirS = [p["w_f_dirpp_S"] for p in per_seed]
    wdirT_abl = [p["w_f_dirpp_T_subcatfreq_ablated"] for p in per_seed]
    wdirS_abl = [p["w_f_dirpp_S_subcatfreq_ablated"] for p in per_seed]
    t_sign_all_negative = all(x < 0 for x in wdirT)
    t_sign_all_negative_ablated = all(x < 0 for x in wdirT_abl)
    s_sign_all_nonneg = all(x >= 0 for x in wdirS)
    mustfail_membership_all = all(p["mustfail"]["weight_drops_membership"] for p in per_seed)
    mustfail_pdo_all = all(p["mustfail"]["weight_drops_pdo_permute"] for p in per_seed)
    clean_sign_neg_all = all(p["mustfail"]["clean_sign_negative"] for p in per_seed)

    # direct-gate CEILING (hand-applied structural gate over arm-C0; DIAGNOSTIC reference only, NOT learned)
    keptDirect = MA.apply_direct_gate(ref["keptC0"], sent_text, ref["subT"])
    mDirect = L.score_arm(keptDirect, gold)
    fpa_direct, keeps_direct = MA.fp_a(keptDirect, M)
    mC0ref = L.score_arm(ref["keptC0"], gold)
    ceiling = {
        "note": "HAND-APPLIED structural gate (dirpp OR low syntactic-P_do) over arm-C0; DIAGNOSTIC ceiling "
                "only (NOT learned). The LEARNED arm T should approach this WITHOUT hand-installing the rule.",
        "fp_a_direct_gate": round(fpa_direct, 4), "ma_keeps_direct": keeps_direct,
        "overall_precision_direct": mDirect["precision"], "overall_recall_direct": mDirect["recall"],
        "recall_retention_direct_over_C0": round((mDirect["recall"] / mC0ref["recall"]) if mC0ref["recall"] > 0 else 0.0, 4),
    }
    pred4 = MA.graded_score_report(ref["gradedT"], gold, M)

    # VERDICT (the LEARNING test)
    if (not t_sign_all_negative) or (not mustfail_membership_all) or (not s_sign_all_nonneg):
        verdict = "HARD_FAIL_SYNTACTIC_INSUFFICIENT"
    elif t_sign_all_negative and t_sign_all_negative_ablated and mustfail_membership_all and s_sign_all_nonneg:
        verdict = "HARD_PASS_GENUINE_SYNTACTIC_LEARNING"
    else:
        verdict = "MIDDLE_BAND"

    hashes = {"C0_lccp_armC": kept_hash(ref["keptC0"]), "S_semantic": kept_hash(ref["keptS"]),
              "T_syntactic": kept_hash(ref["keptT"])}
    arms_differ = (hashes["C0_lccp_armC"] != hashes["S_semantic"]
                   and hashes["S_semantic"] != hashes["T_syntactic"]
                   and hashes["C0_lccp_armC"] != hashes["T_syntactic"])
    baseline_in_band = bool(0.05 < pC_m < 0.95)
    # discriminator fires: the two teachers DIVERGE on the dirpp sign at seed0 AND P_do separates MA verbs low
    pdo_ma = ref["artT"]["P_do_ma_sample"]
    pdo_ma_vals = [d["P_do"] for d in pdo_ma.values()] if pdo_ma else []
    global_do = ref["artT"]["teacher_diag"]["global_do_rate"]
    pdo_separates = bool(pdo_ma_vals and (float(np.mean(pdo_ma_vals)) < global_do))
    discriminator_fires = bool((wdirT[0] < 0) and (wdirS[0] >= 0) and pdo_separates)

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict,
        "primary_metric": "GENUINE-SYNTACTIC-LEARNING test: w[f_dirpp](T) sign robustness (clean + subcatfreq-"
                          "ablated) + must-fail membership-randomization fires + S_semantic reproduces the "
                          "failed positive-sign route (independent gold, category-c held OUT)",
        "needs_orchestrator_store_sync": True,
        "denominator_M_motion_aspectual_nopat_instances": len(M),
        "fp_a_C0_mean": fpaC_m, "fp_a_C0_std": fpaC_s,
        "fp_a_S_semantic_mean": fpaS_m, "fp_a_S_semantic_std": fpaS_s,
        "fp_a_T_syntactic_mean": fpaT_m, "fp_a_T_syntactic_std": fpaT_s,
        "fp_a_reduction_T_mean": redT_m, "fp_a_reduction_T_std": redT_s,
        "recall_retention_T_mean": rretT_m, "recall_retention_T_std": rretT_s,
        "overall_precision_C0_mean": pC_m, "overall_precision_S_mean": pS_m, "overall_precision_T_mean": pT_m,
        "overall_recall_C0_mean": rC_m, "overall_recall_T_mean": rT_m,
        "LEARNING_w_f_dirpp_T_per_seed": wdirT, "LEARNING_w_f_dirpp_S_per_seed": wdirS,
        "LEARNING_w_f_dirpp_T_subcatfreq_ablated_per_seed": wdirT_abl,
        "LEARNING_w_f_dirpp_S_subcatfreq_ablated_per_seed": wdirS_abl,
        "LEARNING_t_dirpp_all_negative": bool(t_sign_all_negative),
        "LEARNING_t_dirpp_all_negative_ablated": bool(t_sign_all_negative_ablated),
        "LEARNING_s_dirpp_all_nonneg": bool(s_sign_all_nonneg),
        "LEARNING_mustfail_membership_all_seeds": bool(mustfail_membership_all),
        "LEARNING_mustfail_pdo_permute_all_seeds": bool(mustfail_pdo_all),
        "LEARNING_clean_sign_negative_all_seeds": bool(clean_sign_neg_all),
        "mustfail_per_seed": [p["mustfail"] for p in per_seed],
        "direct_gate_ceiling": ceiling,
        "prediction4_graded_argument_hood": pred4,
        "syntactic_P_do_ma_sample_seed0": pdo_ma,
        "syntactic_global_do_rate_seed0": global_do,
        "pdo_separates_ma_low": pdo_separates,
        "per_seed": per_seed,
        "step1_triage_C0": {"counts": ref["triC0"], "examples": ref["exC0"]},
        "step1_triage_T": {"counts": ref["triT"], "examples": ref["exT"]},
        "arm_T_artifacts_seed0": ref["artT"], "arm_S_artifacts_seed0": ref["artS"],
        "kept_hashes": hashes, "arms_differ_verified": arms_differ,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "adaptive_with_discriminator_gate",
        "n_sentences": len(order), "n_reader_svo": sum(len(reader_svo[sid]) for sid in order),
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "seeds": cfg["seeds"], "config": {k: v for k, v in cfg.items()},
        "prior_failed_routes_reference": {
            "subcat_break_w_f_dirpp_per_seed": [0.4467, 0.4439, 0.4534],
            "subcat_break_MEASURED": "data/exp_lccp_motion_aspectual_subcat_break_v1/metrics.json",
            "decontam_w_f_dirpp_per_seed": [2.3451, 2.3348, 2.2668],
            "decontam_verdict": "HARD_FAIL_DECONTAM_INSUFFICIENT",
            "decontam_MEASURED": "data/exp_lccp_motion_aspectual_decontam_teacher_v1/metrics.json",
            "note": "both prior routes used a SEMANTIC-coherence teacher -> w[f_dirpp] POSITIVE (wrong sign)."},
        "HONESTY_GUARD": ("Even full success caps overall precision ~0.55 on arm-C0 scope, BELOW the stacked "
                          "0.557 patient-lens reader. Value here is METHODOLOGICAL (a structural rule GENUINELY "
                          "LEARNED from a purely-syntactic frame-frequency signal, not hand-installed) + modest "
                          "precision, NOT breaking 0.557. The direct-gate ceiling is a HAND-APPLIED diagnostic "
                          "reference, NOT a learned result. A stack re-measure is a SEPARATE step, not claimed."),
        "REQUIRED_FIELDS": ["verdict", "fp_a_C0_mean", "fp_a_S_semantic_mean", "fp_a_T_syntactic_mean",
                            "fp_a_reduction_T_mean", "recall_retention_T_mean", "LEARNING_w_f_dirpp_T_per_seed",
                            "LEARNING_w_f_dirpp_S_per_seed", "LEARNING_w_f_dirpp_T_subcatfreq_ablated_per_seed",
                            "LEARNING_t_dirpp_all_negative", "LEARNING_t_dirpp_all_negative_ablated",
                            "LEARNING_s_dirpp_all_nonneg", "LEARNING_mustfail_membership_all_seeds",
                            "mustfail_per_seed", "direct_gate_ceiling", "syntactic_P_do_ma_sample_seed0",
                            "pdo_separates_ma_low", "per_seed"],
    }
    msg = (f"{verdict} | M={len(M)} | FP_a C0={fpaC_m:.3f} S={fpaS_m:.3f} T={fpaT_m:.3f}+-{fpaT_s:.3f} "
           f"redT={redT_m:+.3f} RretT={rretT_m:.3f} "
           f"| w_dirpp T/seed={wdirT} S/seed={wdirS} Tneg_all={t_sign_all_negative} "
           f"Tneg_ablated_all={t_sign_all_negative_ablated} Snonneg_all={s_sign_all_nonneg} "
           f"| mustfail_membership_drops_all={mustfail_membership_all} pdo_permute_drops_all={mustfail_pdo_all} "
           f"cleanNeg_all={clean_sign_neg_all} "
           f"| P_do MA sep low={pdo_separates} (globalDO={global_do:.3f}) "
           f"| ceiling FP_a={ceiling['fp_a_direct_gate']:.3f} P={ceiling['overall_precision_direct']:.3f} "
           f"| overallP C0={pC_m:.3f} S={pS_m:.3f} T={pT_m:.3f} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires} arms_differ={arms_differ}")
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
    assert out["arms_differ_verified"], "META_RULE_AF: arms C0/S/T not all distinct"
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, out)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  T teacher diag: {out['arm_T_artifacts_seed0']['teacher_diag']}", flush=True)
    print(f"  T learned 8-weights: {dict(zip(FEAT_NAMES_D, out['arm_T_artifacts_seed0']['w']))}", flush=True)
    print(f"  S learned 8-weights: {dict(zip(FEAT_NAMES_D, out['arm_S_artifacts_seed0']['w']))}", flush=True)
    print(f"  T syntactic P_do (MA verbs, seed0): {out['syntactic_P_do_ma_sample_seed0']} "
          f"| global DO rate={out['syntactic_global_do_rate_seed0']}", flush=True)
    for p in out["per_seed"]:
        print(f"  [seed {p['seed']}] FP_a C0={p['fp_a_C0']:.3f} S={p['fp_a_S']:.3f} T={p['fp_a_T']:.3f} "
              f"redT={p['fp_a_reduction_T']:+.3f} | w_dirpp S={p['w_f_dirpp_S']:+.3f} T={p['w_f_dirpp_T']:+.3f} "
              f"(T_ablated={p['w_f_dirpp_T_subcatfreq_ablated']:+.3f}) "
              f"| overallP C0={p['C0']['precision']:.3f} T={p['T_syntactic']['precision']:.3f} "
              f"RretT={p['recall_retention_T_over_C0']:.3f}", flush=True)
        mf = p["mustfail"]
        print(f"    [mustfail seed {p['seed']}] w_clean={mf['w_dirpp_clean']:+.3f} "
              f"w_membRand={mf['w_dirpp_membership_randomized']:+.3f}(drops={mf['weight_drops_membership']}) "
              f"w_pdoPerm={mf['w_dirpp_pdo_permuted']:+.3f}(drops={mf['weight_drops_pdo_permute']}) "
              f"cleanNeg={mf['clean_sign_negative']}", flush=True)
    print(f"  [ceiling]  {out['direct_gate_ceiling']}", flush=True)
    print(f"  [triage C0] {out['step1_triage_C0']['counts']}", flush=True)
    print(f"  [triage T ] {out['step1_triage_T']['counts']}", flush=True)
    print(f"  [pred4] {out['prediction4_graded_argument_hood']}", flush=True)
    print(f"  [HONESTY] {out['HONESTY_GUARD']}", flush=True)
    return out


def self_test():
    # 1. syntactic frame typing: 'home' (bare directional adverb) is a DIR slot; 'door' is a DO slot.
    toks = L.tokenize("charley came home from school")
    iv, ip = L.find_pair_positions(toks, "came", "home")
    assert is_directional_slot("home", toks, iv, ip), "home must be a directional slot"
    toks2 = L.tokenize("he opened the door")
    iv2, ip2 = L.find_pair_positions(toks2, "opened", "door")
    assert not is_directional_slot("door", toks2, iv2, ip2), "door must NOT be directional"
    toks3 = L.tokenize("he walked to school")
    iv3, ip3 = L.find_pair_positions(toks3, "walked", "school")
    assert is_directional_slot("school", toks3, iv3, ip3), "to school = directional-prep-governed"

    # 2. clean-toy MECHANISM test: a motion verb (mostly directional slots) gets LOW P_do; a transitive verb
    #    (mostly DO slots) gets HIGH P_do; the learned w[f_dirpp] is NEGATIVE and the must-fail fires.
    def mk(v, p, feat):
        toks = [v, p]
        c = {"sid": f"s{np.random.randint(0, 10 ** 9)}", "v": v, "a": "x", "p": p, "tup": (v, "x", p),
             "feat": np.array(feat, dtype=float), "_sent": f"{v} {p}", "_iv": 0, "_ip": 1, "_toks": toks}
        c["_dir"] = bool(is_directional_slot(p, toks, 0, 1))
        return c
    postv_do = [1.0, 0.5, 1.0, 0.0, 0.0, 0.0]     # bare post-verbal, not prep/func/clause
    cands = []
    # motion verb 'come': post-verbal slots dominated by directional adverbs (home/there/back/away)
    for p in ["home", "there", "back", "away", "home", "there"]:
        cands.append(mk("come", p, postv_do))
    cands.append(mk("come", "box", postv_do))     # one stray DO
    # transitive verb 'build': post-verbal slots dominated by canonical DOs (house/wall/...)
    for p in ["house", "wall", "boat", "cart", "house", "wall"]:
        cands.append(mk("build", p, postv_do))
    P_do, tdiag = build_syntactic_frame_table(cands, k_smooth=1.0)
    assert P_do["come"] < P_do["build"], f"P_do come {P_do['come']:.3f} !< build {P_do['build']:.3f}"
    assert P_do["come"] < 0.5 < P_do["build"], f"P_do separation weak: come={P_do['come']:.3f} build={P_do['build']:.3f}"
    tcfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.3, epochs=200, p_keep=60.0, p_drop=40.0)
    target_fn, keep_abs, drop_abs = make_syntactic_target_fn(cands, P_do, tcfg)
    MA.extend_features(cands, P_do, lambda v: v in MA_SEED)
    w, ntr = learn_weights(cands, target_fn, tcfg["lr"], tcfg["epochs"], 7)
    assert w[DI] < 0.0, f"clean-toy: w[f_dirpp] must be NEGATIVE, got {w[DI]:+.4f}"
    assert w[SI] > 0.0, f"clean-toy: w[f_subcatfreq] must be POSITIVE, got {w[SI]:+.4f}"
    # must-fail: randomize MA membership so f_dirpp fires on 'build' (a DO verb) instead of 'come'
    rand_mem = lambda v: v == "build"
    cands2 = []
    for p in ["home", "there", "back", "away", "home", "there"]:
        cands2.append(mk("come", p, postv_do))
    cands2.append(mk("come", "box", postv_do))
    for p in ["house", "wall", "boat", "cart", "house", "wall"]:
        cands2.append(mk("build", p, postv_do))
    P_do2, _ = build_syntactic_frame_table(cands2, k_smooth=1.0)
    tf2, _, _ = make_syntactic_target_fn(cands2, P_do2, tcfg)
    MA.extend_features(cands2, P_do2, rand_mem)
    w2, _ = learn_weights(cands2, tf2, tcfg["lr"], tcfg["epochs"], 7)
    assert abs(w2[DI]) < abs(w[DI]) + 1e-9, (
        f"clean-toy must-fail: |w[f_dirpp]| should not exceed clean when f_dirpp fires on a DO verb "
        f"(clean={w[DI]:+.4f} degraded={w2[DI]:+.4f})")

    # 3. lemma parity + dirpp feature reuse
    assert L.lemma_verb("came") == "come"
    assert MA.dirpp_fires("come", toks, iv, ip, "home", lambda v: v in MA_SEED) == 1.0

    # 4. end-to-end smoke: arms differ + the two teachers DIVERGE on the dirpp sign (the discriminator)
    cfg = cfg_smoke()
    out, _ = run_config(cfg, "smoke")
    assert out["arms_differ_verified"], "arms C0/S/T must all differ"
    wT = out["arm_T_artifacts_seed0"]["w"][DI]
    wS = out["arm_S_artifacts_seed0"]["w"][DI]
    print(f"[{ANCHOR_NAME}] self-test OK | toy: P_do come={P_do['come']:.3f} build={P_do['build']:.3f} "
          f"w_dirpp clean={w[DI]:+.3f} degraded={w2[DI]:+.3f} w_subcatfreq={w[SI]:+.3f} "
          f"| smoke: w_dirpp T={wT:+.3f} S={wS:+.3f} FP_a C0={out['fp_a_C0_mean']:.3f} "
          f"T={out['fp_a_T_syntactic_mean']:.3f} pdo_sep={out['pdo_separates_ma_low']} "
          f"mustfail_memb_all={out['LEARNING_mustfail_membership_all_seeds']} verdict={out['verdict']}",
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
