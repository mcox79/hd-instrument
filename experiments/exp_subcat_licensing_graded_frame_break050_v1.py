"""SUBCAT-LICENSING LEVER (graded semantic frame-licensing): does STRENGTHENING the LCCP's LEARNED
verb-argument-frame licensing REDUCE the residual ~23 SUBCAT mis-attachments (patients wrongly handed to
intransitive/cognition/oblique verbs -- come/stand/walk/wish/think/lie) vs INDEPENDENT gold, WITHOUT hurting
the transitive cases? (2nd mapped break-0.50 lever, after the NP-head-finder's candidate-gen fix, atom 29342.)

CONTEXT (milestone VET adce417f / atom 29340): the assembled reading-axis scorer's 48 gold-wrong split into
~23 SUBCAT-LICENSING (a patient handed to a verb that licenses NO such argument in gold) + ~25 attachment/
coref. The LCCP parser (atom 29338) ALREADY learned verb-transitivity (transitive-prior 0.79 vs intransitive
0.34) and got the EASY subcat. THIS cell attacks the HARDER residual it still mis-licenses.

ROOT CAUSE (read from exp_learned_argstruct_parser_lccp_independent_gold_v1.py arm-C): the current subcat
transitivity prior is a running mean of the verb's best STRUCTURAL objecthood score sigmoid(w.feat). It is
PURELY STRUCTURAL -- the semantic selectional teacher (sel_fn) that TRAINED the cue-weights is DISCARDED at
frame-estimation time. An intransitive verb like come/stand/walk frequently has a post-verbal noun (came HOME,
stood THERE, walked ROAD): structurally object-like (f_postv=1, f_prep=0, f_func=0) -> high best_sc -> its
running transitivity prior stays above subcat_thr -> patient NEVER suppressed => the residual SUBCAT FP.

THE IMPROVED LICENSING (LEARNED, glass-box; ONE VARIABLE = the licensing gate; MONOTONE STRENGTHENING):
  ARM A_current    = the LCCP's CURRENT arm-C licensing (structural running-mean transitivity prior, HARD
                     threshold: suppress-all if prior<subcat_thr; else keep if best_sc>=keep_thr). Verified
                     NUMERICALLY IDENTICAL to LCCP arm-C by the ARM-A-parity self-test -- the real 0.50
                     baseline, not a strawman.
  ARM B_sem_tighten = A's decision AND an ADDITIONAL learned SEMANTIC frame-licensing bar: keep iff A keeps
                     AND best_sc >= keep_thr + gamma * max(0, sem_tau - sem_frame(v)), where sem_frame(v) is
                     a LEARNED per-verb SELECTIONAL-COHERENCE estimate (mean, over v's instances, of the
                     semantic teacher's coherence of v's best candidate patient vs v's learned object-centroid;
                     unsupervised GloVe signal, NO gold, NO LLM). A verb whose learned frame semantically
                     disprefers a patient (low sem_frame) faces a HIGHER objecthood bar. The gate is MONOTONE:
                     B can only suppress a SUBSET of what A keeps -> B never loosens A -> the trade-off is
                     clean (subcat_fp can only fall; transitive recall can only fall). NOT a hand blocklist:
                     the per-verb signal is learned; only the gate SHAPE + 2 scalars (gamma, sem_tau) are set.
  All candidates, cue-weights w, construction clustering and the structural prior are SHARED/IDENTICAL across
  A and B (single-variable guarantee). A TAU-SWEEP (hard semantic threshold) traces the full Pareto envelope
  of achievable (subcat-removed, transitive-recall-kept) -- the decisive test of whether ANY operating point
  reaches the HARD_PASS band, independent of the one chosen (gamma, sem_tau).

MEASURED (decisive, per arm, vs INDEPENDENT data/gold_mcguffey_lccp_argstruct_v1.json):
  - SUBCAT residual fixed: subcat_fp (wrong patients on nopat verbs) A vs B, absolute + fraction; per-verb
    subcat_fp for the target residual verbs come/stand/walk/wish/think/lie.
  - subcat TRUE-NEGATIVE suppression over reader-attached nopat instances (A vs B).
  - overall PRECISION raise; overall pos RECALL and TRANSITIVE-verb pos recall retention (the trade-off).
  - within-frame + spurious FP; the semantic class-separation (transitive vs intransitive sem_frame); the
    TAU-SWEEP Pareto envelope (best subcat reduction achievable at >=0.90 transitive-recall retention).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = LCCP arm-C (ARM-A-parity self-test asserts numerical identity).
  (G2) baseline_in_band: 0.05 < arm-A primary precision < 0.95 (un-saturated wall).
  (G3) DIFFICULTY-ON + CAN-FAIL-BOTH-WAYS: subcat_fp_A > 0 (a real residual) AND arms differ; the metric can
       reward (residual falls at kept recall) OR punish (residual immovable OR transitive recall craters).
  (G4) discriminator fires: B suppresses >0 patients that A kept AND kept-set hashes differ A vs B.
  (G5) ONE VARIABLE A->B = the licensing gate (shared cands/w/construction/struct-prior verified).

VERDICT BANDS (pre-registered; subcat_fp = wrong patients on gold-nopat verbs, vs independent gold):
  HARD_PASS_SUBCAT_LICENSING_REDUCES: subcat_fp reduction (A->B) >= 0.30 of subcat_fp_A AND transitive-pos
    recall retention (B/A) >= 0.90 AND overall precision_B > precision_A. (a real 2nd break-0.50 step.)
  MIDDLE_BAND_PARTIAL: 0.10 <= reduction_frac < 0.30 AND transitive-recall retention >= 0.85.
  HARD_FAIL_LOW_CEILING: reduction_frac < 0.10 (residual frame-immovable / LCCP at its verb-frame ceiling on
    this small corpus) OR transitive recall retention < 0.75 (the trade-off bites). A LOW-CEILING result is an
    HONEST, valuable finding: it localizes the subcat lever's limit (fix needs a syntactic argument/adjunct
    signal or more data), NOT a defeat.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): graded verb-frame licensing -- a verb whose learned
argument-frame disprefers an argument requires stronger evidence to license it -- is brain-faithful (Competition
Model cue-validity, MacWhinney; usage-based subcategorization, Fitz & Chang). The open question is whether the
23-residual is FRAME-LEARNABLE from the selectional-coherence signal on this small corpus. If intransitive
adjuncts (came HOME, stood THERE) are semantically separable from true objects here, the lever works. If they
are NOT -- because a locative/cognition complement is a semantically coherent word, so distinguishing an
ADJUNCT from an ARGUMENT needs SYNTACTIC role, not lexical semantics -- that is the SAME LIMIT the brain hits
with equally sparse cues -> ACCEPT it as a low-ceiling bound; the substrate-native fix (syntactic role / more
corpus / document-scope consistency) is the flagged next step, NOT built here.

COMPUTE: class (b) sequential-CPU. Reuses the LCCP pipeline + 2 gate passes + a tau-sweep; wall < ~90s.
Foreground local-to-completion (NO queue, NO push, NO remote-persist). Storage: no_storage. Determinism:
OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib; no salted builtin hash / list(set).

CELL-TEMPLATE (LOCAL foreground): arms_differ_verified; final_metrics atomic (os.replace); except SystemExit
before except Exception; baseline_in_band at smoke; discriminator fires at smoke; scaffold-free witness;
deterministic seeding; ARM-A-parity self-test (my A == LCCP arm-C numerically).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "subcat_licensing_graded_frame_break050_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse the LCCP pipeline wholesale so the ONLY thing that varies A->B is the licensing gate.
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402

ARMS = ["A_current", "B_sem_tighten"]
TARGET_RESIDUAL_VERBS = ["come", "stand", "walk", "wish", "think", "lie"]


def cfg_smoke():
    b = LCCP.cfg_smoke()
    b.update(gamma=3.0, sem_tau=0.30, kappa=1.5)
    return b


def cfg_full():
    b = LCCP.cfg_full()
    b.update(gamma=3.0, sem_tau=0.30, kappa=1.5)
    return b


# ----------------------------------------------------------------------------------------------
# Shared precompute: reproduces LCCP.run_arms' shared block EXACTLY (verified by ARM-A-parity self-test) so A
# and B differ ONLY in the licensing gate. Adds the NEW learned per-verb semantic frame estimate.
# ----------------------------------------------------------------------------------------------
def build_shared(order, reader_svo, sent_text, glove, cfg, seed):
    cands = []
    for sid in order:
        toks = LCCP.tokenize(sent_text[sid])
        for tup in reader_svo[sid]:
            v_surf, a, p = tup
            feat, _pos = LCCP.candidate_features(toks, v_surf, p)
            cands.append({"sid": sid, "v": LCCP.lemma_verb(v_surf), "a": a, "p": p, "tup": tup, "feat": feat})

    sel_fn, verb_cent, glob_cent = LCCP.build_semantic_teacher(cands, glove)
    w, n_train = LCCP.learn_cue_weights(cands, sel_fn, cfg["sel_keep"], cfg["sel_drop"], cfg["lr"],
                                        cfg["epochs"], seed)

    all_verbs = sorted(set(c["v"] for c in cands))
    rng = np.random.default_rng(seed + 1)
    perm = rng.permutation(len(all_verbs))
    n_heldout = max(1, int(round(cfg["heldout_frac"] * len(all_verbs))))
    heldout_verbs = set(all_verbs[i] for i in perm[:n_heldout])
    seen_verbs = set(all_verbs) - heldout_verbs

    prof = LCCP.verb_cue_profiles(cands, w, sel_fn)
    seen_list = sorted(v for v in seen_verbs if v in prof)
    if seen_list:
        X = np.stack([prof[v] for v in seen_list], 0)
        Xn = (X - X.mean(0)) / (X.std(0) + 1e-8)
        assign, _cent = LCCP.kmeans(Xn, cfg["k_constructions"], seed + 2)
        vconstr = {seen_list[i]: int(assign[i]) for i in range(len(seen_list))}
        constr_centroid = {j: Xn[assign == j].mean(0)
                           for j in range(cfg["k_constructions"]) if (assign == j).any()}
    else:
        vconstr, constr_centroid, X, assign = {}, {}, None, None

    constr_trans = {}
    if seen_list:
        for j in range(cfg["k_constructions"]):
            members = [seen_list[i] for i in range(len(seen_list)) if int(assign[i]) == j]
            if members:
                constr_trans[j] = float(np.mean([prof[m][-1] for m in members]))

    def assign_heldout_construction(v):
        if v not in prof or not constr_centroid or X is None:
            return None
        p = (prof[v] - X.mean(0)) / (X.std(0) + 1e-8)
        best_j, best_d = None, None
        for j, c in constr_centroid.items():
            d = float(((p - c) ** 2).sum())
            if best_d is None or d < best_d:
                best_j, best_d = j, d
        return best_j

    def constr_prior_for(v):
        if v in vconstr:
            return constr_trans.get(vconstr[v])
        j = assign_heldout_construction(v)
        return constr_trans.get(j) if j is not None else None

    inst_groups = defaultdict(list)
    for c in cands:
        inst_groups[(c["sid"], c["v"])].append(c)

    per_inst_order = []
    for sid in order:
        for key in [k for k in inst_groups if k[0] == sid]:
            per_inst_order.append(key)

    # NEW learned per-verb semantic frame estimate: mean selectional coherence of the verb's best candidate
    # patient vs the verb's learned object-centroid (sel_fn). Unsupervised (no gold), whole-corpus scope --
    # same scope as verb_cent / the construction clustering arm-C already uses.
    sem_raw = defaultdict(list)
    for (sid, v), cs in inst_groups.items():
        best = max(cs, key=lambda c: LCCP.score_cand(w, c["feat"]))
        s = sel_fn(v, best["p"])
        if s is not None:
            sem_raw[v].append(s)
    sem_frame = {v: float(np.mean(xs)) for v, xs in sem_raw.items() if xs}

    return {"cands": cands, "w": w, "n_train": n_train, "sel_fn": sel_fn,
            "seen_verbs": seen_verbs, "heldout_verbs": heldout_verbs,
            "constr_prior_for": constr_prior_for, "inst_groups": inst_groups,
            "per_inst_order": per_inst_order, "sem_frame": sem_frame}


# ----------------------------------------------------------------------------------------------
# Licensing gates. B is a MONOTONE STRENGTHENING of A (keeps a subset of A's keeps). The struct running-prior
# update is IDENTICAL across arms (updates with best_sc regardless of decision) -> single variable = the gate.
# ----------------------------------------------------------------------------------------------
def _a_keep(best_sc, prior, cfg):
    if prior is not None and prior < cfg["subcat_thr"]:
        return False
    return best_sc >= cfg["keep_thr"]


def _gate_decide(name, best_sc, prior, sem_raw, cfg):
    a = _a_keep(best_sc, prior, cfg)
    if name == "A_current":
        return a
    if not a:
        return False  # monotone: B can only tighten
    if name == "B_sem_tighten":
        if sem_raw is None:
            return True  # no semantic evidence -> keep A's decision (never loosen)
        eff = cfg["keep_thr"] + cfg["gamma"] * max(0.0, cfg["sem_tau"] - sem_raw)
        return best_sc >= eff
    raise ValueError(name)


def run_gate(name, shared, cfg):
    inst_groups = shared["inst_groups"]; per_inst_order = shared["per_inst_order"]; w = shared["w"]
    seen_verbs = shared["seen_verbs"]; heldout_verbs = shared["heldout_verbs"]
    constr_prior_for = shared["constr_prior_for"]; sem_frame = shared["sem_frame"]
    KAPPA = cfg.get("kappa", 1.5)
    t_run = defaultdict(lambda: [0.0, 0]); verb_seen_count = defaultdict(int)
    kept, subcat_decisions = [], []
    for (sid, v) in per_inst_order:
        cs = inst_groups[(sid, v)]
        best = max(cs, key=lambda c: LCCP.score_cand(w, c["feat"]))
        best_sc = LCCP.score_cand(w, best["feat"])
        cprior = constr_prior_for(v)
        if v in seen_verbs:
            s, n = t_run[v]
            prior = (s / n) if (cprior is None and n > 0) else (
                None if cprior is None else (s + KAPPA * cprior) / (n + KAPPA))
        else:
            prior = cprior
        sem = sem_frame.get(v)
        keep_patient = _gate_decide(name, best_sc, prior, sem, cfg)
        if keep_patient:
            kept.append((best["sid"], best["tup"]))
        subcat_decisions.append({"sid": sid, "v": v, "kept": keep_patient, "occ": verb_seen_count[v],
                                 "heldout": v in heldout_verbs, "prior": prior, "sem": sem, "best_sc": best_sc})
        verb_seen_count[v] += 1
        if v in seen_verbs:
            t_run[v][0] += best_sc; t_run[v][1] += 1
    return kept, subcat_decisions


# ----------------------------------------------------------------------------------------------
# Diagnostics.
# ----------------------------------------------------------------------------------------------
def per_verb_subcat_fp(kept, gold, verbs):
    out = {v: {"subcat_fp": 0, "kept": 0, "tp": 0} for v in verbs}
    for sid, tup in kept:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        if v not in out:
            continue
        out[v]["kept"] += 1
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None:
            out[v]["tp"] += 1
        elif v in rec["nopat"] and v not in rec["pos_verbs"]:
            out[v]["subcat_fp"] += 1
    return out


def pure_transitive_verbs(gold):
    pos_v, nopat_v = set(), set()
    for rec in gold.values():
        pos_v |= rec["pos_verbs"]; nopat_v |= rec["nopat"]
    return pos_v - nopat_v


def semantic_separation(shared, gold, cfg):
    """Does the learned per-verb sem_frame separate gold-transitive from gold-intransitive verbs? Reports
    class means + best single-threshold balanced accuracy (the decisive 'is the signal exploitable' probe)."""
    sem = shared["sem_frame"]
    pos_v, nopat_v = set(), set()
    for rec in gold.values():
        pos_v |= rec["pos_verbs"]; nopat_v |= rec["nopat"]
    pure_pos = [v for v in (pos_v - nopat_v) if v in sem]
    pure_nopat = [v for v in (nopat_v - pos_v) if v in sem]
    pp = np.array([sem[v] for v in pure_pos]) if pure_pos else np.array([0.0])
    nn = np.array([sem[v] for v in pure_nopat]) if pure_nopat else np.array([0.0])
    labeled = [(sem[v], 1) for v in pure_pos] + [(sem[v], 0) for v in pure_nopat]
    best_thr, best_bal = None, 0.0
    if pure_pos and pure_nopat:
        for thr in np.linspace(min(s for s, _ in labeled), max(s for s, _ in labeled), 60):
            tp = sum(1 for s, y in labeled if y == 1 and s >= thr)
            tn = sum(1 for s, y in labeled if y == 0 and s < thr)
            bal = 0.5 * (tp / len(pure_pos) + tn / len(pure_nopat))
            if bal > best_bal:
                best_bal, best_thr = bal, float(thr)
    return {"sem_transitive_mean": round(float(pp.mean()), 4), "sem_intransitive_mean": round(float(nn.mean()), 4),
            "best_separating_threshold": round(best_thr, 4) if best_thr is not None else None,
            "best_balanced_accuracy": round(best_bal, 4),
            "separates": bool(best_bal >= 0.70), "n_pure_transitive": len(pure_pos),
            "n_pure_intransitive": len(pure_nopat),
            "target_verb_sem": {v: (round(sem[v], 4) if v in sem else None) for v in TARGET_RESIDUAL_VERBS}}


def tau_sweep(kept_A, shared, gold, trans_verbs):
    """Hard semantic-threshold Pareto envelope: for each tau, suppress every A-kept patient whose verb has
    sem_frame < tau; measure subcat_fp reduction vs transitive-recall retention. If NO tau reaches >=0.30
    reduction at >=0.90 transitive-recall retention, HARD_PASS is unreachable = definitive low-ceiling."""
    sem = shared["sem_frame"]
    base = LCCP.score_arm(kept_A, gold)
    subcat_fp_A = base["subcat_fp"]
    trans_A = LCCP.score_arm(kept_A, gold, only_verbs=trans_verbs)["recall"]
    rows = []
    for tau in np.linspace(0.0, 0.85, 35):
        kept_t = [(sid, t) for sid, t in kept_A if sem.get(LCCP.lemma_verb(t[0]), 1e9) >= tau]
        m = LCCP.score_arm(kept_t, gold)
        tr = LCCP.score_arm(kept_t, gold, only_verbs=trans_verbs)["recall"]
        red = subcat_fp_A - m["subcat_fp"]
        rows.append({"tau": round(float(tau), 3), "subcat_fp": m["subcat_fp"],
                     "red_frac": round(red / subcat_fp_A, 3) if subcat_fp_A else 0.0,
                     "trans_recall_ret": round(tr / trans_A, 3) if trans_A else 1.0,
                     "precision": m["precision"]})
    feasible = [r for r in rows if r["trans_recall_ret"] >= 0.90]
    best = max(feasible, key=lambda r: r["red_frac"]) if feasible else None
    return {"subcat_fp_A": subcat_fp_A, "trans_recall_A": round(trans_A, 4), "rows": rows,
            "best_feasible_at_ret090": best,
            "hard_pass_reachable_any_tau": bool(best is not None and best["red_frac"] >= 0.30),
            "middle_reachable_any_tau": bool(best is not None and best["red_frac"] >= 0.10)}


def scaffold_free_witness(decisions, gold):
    a_inst = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["A_current"])
    b_inst = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["B_sem_tighten"])
    supp = None
    for (sid, v, p) in sorted(a_inst):
        rec = gold.get(sid)
        if rec and v in rec["nopat"] and v not in rec["pos_verbs"] and (sid, v, p) not in b_inst:
            supp = [sid, v, p]; break
    keep = None
    for (sid, v, p) in sorted(b_inst):
        rec = gold.get(sid)
        if rec and LCCP.match_pos(v, p, rec["pos"]) is not None:
            keep = [sid, v, p]; break
    return {"subcat_overextraction_suppressed_by_B_kept_by_A": supp,
            "true_transitive_patient_kept_by_B": keep,
            "witness": "PASS" if (supp is not None and keep is not None) else "PARTIAL"}


# ----------------------------------------------------------------------------------------------
# Run + verdict.
# ----------------------------------------------------------------------------------------------
def run_config(cfg):
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = LCCP.load_gold(cfg["slice_lessons"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, LCCP.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = LCCP.load_glove_for(toks)

    shared = build_shared(order, reader_svo, sent_text, glove, cfg, cfg["seed"])
    decisions, subcat_decs = {}, {}
    for arm in ARMS:
        kept, sd = run_gate(arm, shared, cfg)
        decisions[arm] = kept; subcat_decs[arm] = sd

    trans_verbs = pure_transitive_verbs(gold)
    arm_metrics = {}
    for arm in ARMS:
        arm_metrics[arm] = {
            "all": LCCP.score_arm(decisions[arm], gold),
            "seen": LCCP.score_arm(decisions[arm], gold, only_verbs=shared["seen_verbs"]),
            "heldout": LCCP.score_arm(decisions[arm], gold, only_verbs=shared["heldout_verbs"]),
            "transitive": LCCP.score_arm(decisions[arm], gold, only_verbs=trans_verbs)}
    subcat_tn = LCCP.subcat_true_negatives(decisions, gold, reader_svo, order)
    lc = {arm: LCCP.learning_curve(subcat_decs[arm], gold) for arm in ARMS}
    pv = {arm: per_verb_subcat_fp(decisions[arm], gold, TARGET_RESIDUAL_VERBS) for arm in ARMS}
    sem_sep = semantic_separation(shared, gold, cfg)
    sweep = tau_sweep(decisions["A_current"], shared, gold, trans_verbs)

    n_reader = sum(len(reader_svo[sid]) for sid in order)
    meta = {"slice_lessons": cfg["slice_lessons"], "n_sentences": len(order), "n_reader_svo": n_reader,
            "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
            "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
            "glove_coverage": round(len(glove) / max(1, len(toks)), 3),
            "n_seen_verbs": len(shared["seen_verbs"]), "n_heldout_verbs": len(shared["heldout_verbs"]),
            "learned_weights": {LCCP.FEAT_NAMES[i]: round(float(shared["w"][i]), 4) for i in range(6)},
            "reader_svo_dump": {sid: [list(t) for t in reader_svo[sid]] for sid in order if reader_svo[sid]}}
    return arm_metrics, subcat_tn, lc, pv, sem_sep, sweep, meta, decisions, gold, trans_verbs


def build_verdict(arm_metrics, subcat_tn, sweep):
    A = arm_metrics["A_current"]["all"]; B = arm_metrics["B_sem_tighten"]["all"]
    subcat_fp_A, subcat_fp_B = A["subcat_fp"], B["subcat_fp"]
    red_abs = subcat_fp_A - subcat_fp_B
    red_frac = (red_abs / subcat_fp_A) if subcat_fp_A > 0 else 0.0
    tA = arm_metrics["A_current"]["transitive"]["recall"]; tB = arm_metrics["B_sem_tighten"]["transitive"]["recall"]
    trans_ret = (tB / tA) if tA > 0 else 1.0
    prec_raise = B["precision"] - A["precision"]
    if subcat_fp_A == 0:
        verdict = "DEGENERATE_NO_SUBCAT_RESIDUAL"
    elif red_frac < 0.10 or trans_ret < 0.75:
        verdict = "HARD_FAIL_LOW_CEILING"
    elif red_frac >= 0.30 and trans_ret >= 0.90 and prec_raise > 0:
        verdict = "HARD_PASS_SUBCAT_LICENSING_REDUCES"
    elif red_frac >= 0.10 and trans_ret >= 0.85:
        verdict = "MIDDLE_BAND_PARTIAL"
    else:
        verdict = "HARD_FAIL_LOW_CEILING"
    return {"verdict": verdict, "subcat_fp_A": subcat_fp_A, "subcat_fp_B": subcat_fp_B,
            "subcat_reduction_abs": red_abs, "subcat_reduction_frac": round(red_frac, 4),
            "transitive_recall_A": round(tA, 4), "transitive_recall_B": round(tB, 4),
            "transitive_recall_retention": round(trans_ret, 4),
            "precision_A": A["precision"], "precision_B": B["precision"], "precision_raise": round(prec_raise, 4),
            "subcat_tn_A": subcat_tn["A_current"]["n_suppressed_TN"],
            "subcat_tn_B": subcat_tn["B_sem_tighten"]["n_suppressed_TN"],
            "hard_pass_reachable_any_tau": sweep["hard_pass_reachable_any_tau"],
            "best_feasible_subcat_reduction_at_ret090": (sweep["best_feasible_at_ret090"]["red_frac"]
                                                         if sweep["best_feasible_at_ret090"] else 0.0)}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    out_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    arm_metrics, subcat_tn, lc, pv, sem_sep, sweep, meta, decisions, gold, trans_verbs = run_config(cfg)
    vd = build_verdict(arm_metrics, subcat_tn, sweep)
    witness = scaffold_free_witness(decisions, gold)

    hashes = {arm: LCCP.kept_hash(decisions[arm]) for arm in ARMS}
    assert hashes["A_current"] != hashes["B_sem_tighten"], "META_RULE_AF: A==B (improved licensing no-op)"
    A = arm_metrics["A_current"]["all"]; B = arm_metrics["B_sem_tighten"]["all"]
    baseline_in_band = bool(0.05 < A["precision"] < 0.95)
    n_suppressed = len(decisions["A_current"]) - len(set(decisions["B_sem_tighten"]) & set(decisions["A_current"]))
    discriminator_fires = bool(vd["subcat_tn_B"] >= vd["subcat_tn_A"] and hashes["A_current"] != hashes["B_sem_tighten"])
    subcat_residual_present = bool(vd["subcat_fp_A"] > 0)
    elapsed = time.perf_counter() - t0

    v = vd["verdict"]
    bf = sweep["best_feasible_at_ret090"]
    msg = (f"{v} | slice={'+'.join(cfg['slice_lessons'])} sents={meta['n_sentences']} reader={meta['n_reader_svo']} "
           f"gold_pos={meta['n_gold_pos']} gold_nopat={meta['n_gold_nopat']} "
           f"| A P={A['precision']:.3f} R={A['recall']:.3f} subFP={A['subcat_fp']} wfFP={A['within_frame_fp']} "
           f"| B P={B['precision']:.3f} R={B['recall']:.3f} subFP={B['subcat_fp']} wfFP={B['within_frame_fp']} "
           f"| subcatRED abs={vd['subcat_reduction_abs']} frac={vd['subcat_reduction_frac']:.3f} "
           f"| transRecall A={vd['transitive_recall_A']:.3f} B={vd['transitive_recall_B']:.3f} ret={vd['transitive_recall_retention']:.3f} "
           f"| precRaise={vd['precision_raise']:+.3f} "
           f"| semSEP bal_acc={sem_sep['best_balanced_accuracy']:.3f} T={sem_sep['sem_transitive_mean']:.3f} I={sem_sep['sem_intransitive_mean']:.3f} "
           f"| SWEEP hardpass_reachable={sweep['hard_pass_reachable_any_tau']} best_feasible_red={(bf['red_frac'] if bf else 0.0):.3f} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires} residual={subcat_residual_present}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "verdict_detail": vd, "subcat_true_negatives": subcat_tn,
        "learning_curve": lc, "per_verb_subcat_fp": pv, "semantic_separation": sem_sep, "tau_sweep": sweep,
        "kept_hashes": hashes, "arms_differ_verified": bool(len(set(hashes.values())) >= 2),
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "n_patients_B_suppressed_from_A": n_suppressed, "subcat_residual_present": subcat_residual_present,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "independent_gold_source": ("data/gold_mcguffey_lccp_argstruct_v1.json -- single-annotator gold, "
                                    "pos + nopat verb-instances, independent of reader output."),
        "one_variable_note": ("A and B share candidates, cue-weights w, construction clustering and the "
                              "structural running-prior; the ONLY difference is the licensing gate (A=hard "
                              "struct threshold [=LCCP arm-C], B=A AND graded semantic-frame bar). B is a "
                              "MONOTONE strengthening of A. ARM-A-parity self-test asserts A == LCCP arm-C."),
        "data_meta": meta,
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "verdict_detail", "subcat_true_negatives",
                            "per_verb_subcat_fp", "semantic_separation", "tau_sweep", "scaffold_free_witness",
                            "data_meta"],
        "notes": ("SUBCAT-LICENSING lever: monotone graded semantic verb-frame licensing on top of LCCP arm-C. "
                  "HARD_PASS = subcat_fp reduction >=0.30 of A AND transitive recall retention >=0.90 AND "
                  "precision raise >0. MIDDLE = 0.10-0.30 reduction at >=0.85 recall retention. "
                  "HARD_FAIL_LOW_CEILING = <0.10 reduction OR transitive recall retention <0.75. tau_sweep "
                  "traces the full Pareto envelope: hard_pass_reachable_any_tau=False => the ceiling is "
                  "structural (selectional coherence orthogonal to subcategorization on this corpus; fix needs "
                  "a syntactic argument/adjunct signal). LOW-CEILING is an HONEST localizing finding, NOT a "
                  "hand blocklist. CLAIM-VET-pending; single-annotator gold caveated."),
    }
    write_metrics(out_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    print(f"  learned weights: {meta['learned_weights']}", flush=True)
    for arm in ARMS:
        m = arm_metrics[arm]["all"]; tr = arm_metrics[arm]["transitive"]
        print(f"  [{arm:>14}] P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} n_pred={m['n_pred']} "
              f"tp={m['tp']} fp(sub/wf/sp)={m['subcat_fp']}/{m['within_frame_fp']}/{m['spurious_verb_fp']} "
              f"| transR={tr['recall']:.3f} transTP={tr['tp']}/{tr['n_gold']} "
              f"| subcatTN={subcat_tn[arm]['n_suppressed_TN']}/{subcat_tn[arm]['n_nopat_reader_attached']}", flush=True)
    print("  [per-verb subcat_fp on target residual verbs]", flush=True)
    for v_ in TARGET_RESIDUAL_VERBS:
        sv = sem_sep["target_verb_sem"].get(v_)
        print(f"    {v_:>7}: A={pv['A_current'][v_]['subcat_fp']} B={pv['B_sem_tighten'][v_]['subcat_fp']} "
              f"(A_kept={pv['A_current'][v_]['kept']} B_kept={pv['B_sem_tighten'][v_]['kept']}) sem={sv}", flush=True)
    print(f"  [semantic separation] best_balanced_acc={sem_sep['best_balanced_accuracy']:.3f} "
          f"thr={sem_sep['best_separating_threshold']} transitive_mean={sem_sep['sem_transitive_mean']:.3f} "
          f"intransitive_mean={sem_sep['sem_intransitive_mean']:.3f} separates={sem_sep['separates']} "
          f"(n_T={sem_sep['n_pure_transitive']} n_I={sem_sep['n_pure_intransitive']})", flush=True)
    print(f"  [tau-sweep envelope] hard_pass_reachable_any_tau={sweep['hard_pass_reachable_any_tau']} "
          f"middle_reachable_any_tau={sweep['middle_reachable_any_tau']} "
          f"best_feasible_at_ret090={sweep['best_feasible_at_ret090']}", flush=True)
    print(f"  [verdict] subcatRED abs={vd['subcat_reduction_abs']} frac={vd['subcat_reduction_frac']:.3f} | "
          f"transRecall ret={vd['transitive_recall_retention']:.3f} | precRaise={vd['precision_raise']:+.3f}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def self_test():
    cfg = cfg_smoke()
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    gold, _ = LCCP.load_gold(cfg["slice_lessons"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, LCCP.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = LCCP.load_glove_for(toks)
    shared = build_shared(order, reader_svo, sent_text, glove, cfg, cfg["seed"])
    kept_A, _ = run_gate("A_current", shared, cfg)
    lccp_dec, _, _, _, _, _, _ = LCCP.run_arms(order, reader_svo, sent_text, glove, cfg, cfg["seed"])
    h_mine = LCCP.kept_hash(kept_A); h_lccp = LCCP.kept_hash(lccp_dec["C_lccp"])
    assert h_mine == h_lccp, f"ARM-A-PARITY FAIL: my A={h_mine} != LCCP arm-C={h_lccp}"
    kept_B, _ = run_gate("B_sem_tighten", shared, cfg)
    # monotone: B keeps a subset of A
    assert set(map(tuple, kept_B)).issubset(set(map(tuple, kept_A))), "B not a subset of A (non-monotone)"
    arm_metrics, subcat_tn, lc, pv, sem_sep, sweep, meta, decisions, gold2, tv = run_config(cfg)
    vd = build_verdict(arm_metrics, subcat_tn, sweep)
    A = arm_metrics["A_current"]["all"]; B = arm_metrics["B_sem_tighten"]["all"]
    print(f"[{ANCHOR_NAME}] self-test: ARM-A-PARITY vs LCCP arm-C = OK ({h_mine}); B subset of A = OK", flush=True)
    print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={vd['verdict']} A_P={A['precision']:.3f} B_P={B['precision']:.3f} "
          f"subFP A={A['subcat_fp']} B={B['subcat_fp']} red_frac={vd['subcat_reduction_frac']:.3f} "
          f"transRet={vd['transitive_recall_retention']:.3f} semSEP_balacc={sem_sep['best_balanced_accuracy']:.3f} "
          f"hardpass_reachable={sweep['hard_pass_reachable_any_tau']} reader={meta['n_reader_svo']} "
          f"gold_pos={meta['n_gold_pos']} gold_nopat={meta['n_gold_nopat']}", flush=True)


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
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
