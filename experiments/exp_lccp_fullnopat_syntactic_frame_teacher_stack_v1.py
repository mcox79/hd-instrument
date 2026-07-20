"""FULL-NOPAT SYNTACTIC-FRAME-TEACHER PAYOFF TEST (the chain-grade blocker probe): does the VALIDATED per-verb
syntactic frame-frequency teacher (P_do, atom 29349 -- 'does this verb take a bare-NP direct object', VET-
verified EMERGENT from POS/position, NO GloVe) GENERALIZE beyond the 9 motion verbs to move the STACKED
READER precision (LCCP + arg/adjunct + quotative = 0.5574 patient-lens, MEASURED@data/exp_quotative_speaker_
attribution_stack_break050_v1/metrics.json:arm_metrics.Q_quotative.precision) across the FULL intransitive/
oblique/cognition 'spurious-patient' residual -- WITHOUT hand-installing, WITHOUT a recall artifact, and with
the LEARNED frame signal doing the work (must-fail: degrade the frame signal -> the stacked gain collapses)?

WHY THIS IS THE RIGHT NEXT TEST (not another single-class cleanup):
  atom 29349 proved a PURELY-SYNTACTIC frame-frequency teacher (P_do from corpus DO/DIR frame counts, no
  GloVe) makes the substrate GENUINELY LEARN the anti-patient rule (w[f_dirpp] NEGATIVE robustly + must-fail
  fires) where the SEMANTIC-coherence teacher failed (w[f_dirpp] POSITIVE). But that was framed as a LEARNING-
  MECHANISM demo on the motion-only class (precision capped ~0.55 BELOW the stacked 0.557; motion is only
  9/34 FPs). P_do is ALREADY general: f_subcatfreq = P_do(v) is computed for EVERY verb from the corpus frame
  distribution (FT.build_syntactic_frame_table), and the syntactic target rule (FT.make_syntactic_target_fn)
  decides ALL bare-content post-verbal patients. So 'does this verb take a bare-NP object' is a GENERAL cue
  (Ford-Bresnan-Kaplan applies to every verb) that should suppress spurious patients on cognition (sentential-
  complement) + oblique verbs too, not just motion. The payoff question: does feeding the LCCP the frame-
  teacher-learned base, then re-stacking the SAME arg/adjunct + quotative filters, move the STACKED precision
  MATERIALLY above 0.557 -- i.e. is the reader's residual actually frame-frequency-addressable, or was motion
  special / do cognition-oblique need a different signal? Either answer is a decisive localization of where
  the reader's residual lives (the chain-grade parser-extraction blocker).

THE STACK (post-hoc filters over the LCCP arm-C kept set; reproduced, not conflated):
  keptBase -> ARG.build_cascade (Signal-0 categorial arg/adjunct + Signal-1 verb-diversity = kept_B1 = arm S)
           -> QUOT.build_quotative_arm (report-verb + person + quotative-frame speaker/addressee suppression)
           = kept_Q  (the 0.5574 stacked patient-lens reader).
  BASELINE arm  Q_base  = C0 (LCCP arm-C, the ORIGINAL semantic-coherence teacher) -> ARG -> QUOT.
  TREATMENT arm Q_treat = T  (LCCP base with the SYNTACTIC frame-frequency teacher, atom 29349's T_syntactic:
                          f_subcatfreq = P_do(all verbs) + MA-scoped f_dirpp + syntactic target) -> ARG -> QUOT.
  ONE VARIABLE = the LCCP BASE reader's teacher (semantic-coherence C0 vs syntactic-frame-frequency T). The
  arg/adjunct cascade and the quotative arm are BYTE-IDENTICAL across the two arms (imported unchanged). The
  directional-PP feature f_dirpp stays scoped to the motion subset (MA_SEED) exactly as atom 29349; the
  GENERAL lever is f_subcatfreq = P_do over ALL verbs + the syntactic target.

STEP 1 (free, gates interpretation): triage the FULL stacked residual (Q_base FALSE POSITIVES) by verb-class
  x P_do into FRAME-FREQUENCY-ADDRESSABLE (verb in gold-nopat AND low P_do: intransitive-motion / cognition-
  sentential-complement / oblique) vs OUT-OF-SCOPE (within-transitive attachment / coref -- verb DOES license
  objects, wrong-object error, different mechanism) vs spurious-unannotated. Report counts + verbs + P_do.

MEASURED (decisive; vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json; category-c held OUT by gold):
  PRIMARY = STACKED patient-lens precision Q_treat vs the 0.5574 reference AND paired vs the per-seed recomputed
    Q_base; recall retention Q_treat/Q_base (>= 0.85 = not a recall artifact); the LEARNED w[f_dirpp](T) sign
    (reproduces 29349 NEGATIVE); the STACKED-GAIN must-fail (permute P_do across verbs -> the stacked gain
    must COLLAPSE). SECONDARY = per-class FP suppression delta (which residual classes the frame teacher cleans
    up: motion vs cognition-oblique vs within-transitive), n_pred/TP/FP split, per-seed stability.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = the LIVE-recomputed STACKED reader Q_base (positive control: at seed 7 it must reproduce
       the published 0.5574 within 0.02); NOT a strawman, NOT a sub-arm.
  (G2) ONE VARIABLE = C0 (semantic teacher) vs T (syntactic frame teacher) at the LCCP base; ARG + QUOT identical.
  (G3) CAN-FAIL-BOTH-WAYS: Q_treat can rise >= 0.577 at recall retention >= 0.85 with the gain collapsing under
       P_do-permute (HARD-PASS: residual is frame-freq-addressable, LEARNED) OR fail to move / buy precision with
       recall / survive P_do-permute (HARD-FAIL: motion was special, cognition-oblique need a different signal,
       or the gain is construction-determined -- a real localization).
  (G4) difficulty ON: full independent gold, contested/gradient (category c) held OUT of the gold pos/nopat by
       construction (the annotator excluded them); the target is the residual the 0.557 stack still mis-licenses.
  (G5) discriminator fires at smoke: Q_treat suppresses >0 of Q_base's residual FPs, arms differ (kept hashes),
       P_do separates the low-frame nopat verbs from the high-frame transitive verbs, w[f_dirpp](T) < 0.

VERDICT BANDS (pre-registered):
  delta_abs   = mean(precision_Q_treat) - 0.5574                (material-move bar = >= +0.02)
  delta_paired= mean(precision_Q_treat - precision_Q_base)      (per-seed paired mechanism effect; must be > 0)
  rret        = mean(recall_Q_treat / recall_Q_base)            (recall retention; >= 0.85)
  mustfail    = mean(precision_Q_treat) > mean(precision_Q_pdoPermuted) + 0.01  (stacked gain collapses under
                                                                                 P_do permute = LEARNED)
  HARD_PASS_FRAME_TEACHER_GENERALIZES: delta_abs >= 0.02 AND delta_paired > 0 AND rret >= 0.85 AND mustfail.
  HARD_FAIL_NO_MATERIAL_MOVE:        delta_abs < 0.02 (motion was special / cognition-oblique need a different
                                     signal -- the reader residual is NOT frame-freq-addressable at the stack).
  HARD_FAIL_RECALL_ARTIFACT:         delta_abs >= 0.02 BUT rret < 0.85 (precision bought by destroying recall).
  HARD_FAIL_CONSTRUCTION_DETERMINED: delta_abs >= 0.02, rret ok, BUT not mustfail (the gain survives P_do
                                     permute -> not driven by the real frame signal).
  MIDDLE_BAND: material move + recall ok + mustfail but paired<=0 (seed-luck), or partial across seeds.

HONESTY GUARD (mandatory; printed + stored): report the stacked move vs 0.5574 EXACTLY (not vs a sub-arm) AND
  the per-seed paired baseline; report recall retention (do NOT sell a recall-suppression artifact as a
  precision win); report the per-class suppression delta and the must-fail; the hand-seed scaffold (MA_SEED
  Levin list gating f_dirpp; MA construction row) is HONESTLY DECLARED and inherited unchanged from atom 29349
  -- the de-confound of that scaffold is a SEPARATE refinement, NOT claimed here. n_pred is small (~61) so
  precision granularity is coarse (~0.016/FP); report absolute FP counts alongside precision. No number is
  reported as if learned when it is hand-applied. No example outside the corpus is invented.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- per seed: 1 LCCP arm-C recompute
  (GloVe teacher + logistic) + 1 syntactic-frame-teacher base recompute + 1 P_do-permuted base + 3 post-hoc
  stack passes (ARG cascade + quotative, cheap) over ~225 candidates / ~114 sentences; x 3 seeds; wall < ~5min.
  Foreground local-to-completion (NO queue; NO push; NO remote-persist; needs_orchestrator_store_sync=True).
  Storage: no_storage (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds,
  deterministic hashlib + deterministic WordNet synset order (inherited from QUOT); no salted builtin hash /
  list(set); numpy default RNG seeded.

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (Q_base vs Q_treat kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < precision_Q_base < 0.95) + baseline positive-control reproduces 0.5574 (full seed7)
- discriminator fires at smoke (Q_treat suppresses >0 Q_base residual FPs; arms differ; P_do separates; w[f_dirpp](T)<0)
- multi-seed (3 seeds full); must-fail (P_do permute) PER SEED; precision aggregated mean/std
- deterministic seeding; all numbers tagged MEASURED@/CITED@ (printed at run)
- clean-toy mechanism self-test (P_do separation + stack-suppression on a synthetic corpus)
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
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "lccp_fullnopat_syntactic_frame_teacher_stack_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as L      # noqa: E402
import experiments.exp_lccp_motion_aspectual_subcat_break_v1 as MA                 # noqa: E402
import experiments.exp_lccp_motion_aspectual_syntactic_frame_teacher_v1 as FT      # noqa: E402
import experiments.exp_arg_adjunct_role_eligibility_categorial_break050_v1 as ARG  # noqa: E402
import experiments.exp_quotative_speaker_attribution_stack_break050_v1 as QUOT     # noqa: E402

DI = FT.DI            # index of f_dirpp in the 8-dim feature vector
ARMS = ["Q_base_semantic", "Q_treat_syntactic"]
PUBLISHED_STACK_PRECISION = 0.5574  # CITED@ data/exp_quotative_speaker_attribution_stack_break050_v1/metrics.json
PUBLISHED_STACK_RECALL = 0.34       # CITED@ same


# ------------------------------------------------------------------------------------------------
# The stack (post-hoc filters over a base kept set) -- IDENTICAL for both arms (imported unchanged).
# ------------------------------------------------------------------------------------------------
def stack_over(kept_base, order, sent_text, reader_svo, gold_agent, div_thr):
    """kept_base -> ARG categorial cascade (kept_B1 = arm S) -> QUOT quotative (kept_Q). Returns kept_Q."""
    kA, kB1, kB2, arg_per, verb_div, cmeta = ARG.build_cascade(order, sent_text, reader_svo, kept_base, div_thr)
    kept_Q, _per = QUOT.build_quotative_arm(kB1, sent_text, gold_agent)
    return kept_Q


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def build_pdo_permutation(order, reader_svo, sent_text, seed):
    """Must-fail: permute P_do VALUES across verbs (seeded), breaking the frame-freq<->verb link while
    preserving the marginal P_do distribution. Deterministic (numpy rng, NOT builtin hash)."""
    cands = FT.build_cands(order, reader_svo, sent_text)
    P_do_true, _ = FT.build_syntactic_frame_table(cands)
    verbs_sorted = sorted(P_do_true.keys())
    vals = np.array([P_do_true[v] for v in verbs_sorted])
    rng = np.random.default_rng(seed + 202)
    perm = rng.permutation(len(verbs_sorted))
    return {verbs_sorted[i]: float(vals[perm[i]]) for i in range(len(verbs_sorted))}


def pdo_table_and_split(order, reader_svo, sent_text, cfg):
    """P_do(v) over the full corpus + the syntactic target drop/keep abs thresholds (for triage classing)."""
    cands = FT.build_cands(order, reader_svo, sent_text)
    P_do, tdiag = FT.build_syntactic_frame_table(cands)
    _tf, keep_abs, drop_abs = FT.make_syntactic_target_fn(cands, P_do, cfg)
    return P_do, keep_abs, drop_abs, tdiag


# ------------------------------------------------------------------------------------------------
# STEP-1 triage: classify a kept set's residual FPs by verb-class x P_do.
# ------------------------------------------------------------------------------------------------
def triage_residual(kept, gold, P_do, drop_abs):
    """Split a kept set's FALSE POSITIVES into frame-frequency-addressable (nopat verb + low P_do) vs
    out-of-scope (within-transitive) vs spurious. Returns (counts, detail, addressable_verbs)."""
    counts = Counter()
    detail = defaultdict(list)
    addressable_verbs = set()
    for sid, tup in kept:
        v = L.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None:
            counts["TP"] += 1
            continue
        pdo = P_do.get(v)
        pdo_r = round(float(pdo), 3) if pdo is not None else None
        if v in rec["nopat"]:
            verb_class = "motion_aspectual" if v in MA.MA_SEED else "cognition_oblique_other"
            low_frame = (pdo is not None and pdo <= drop_abs)
            if low_frame:
                key = f"ADDRESSABLE_nopat_{verb_class}"
                addressable_verbs.add(v)
            else:
                key = f"nopat_highPdo_{verb_class}"     # nopat but NOT flagged low-frame (harder to address)
            counts[key] += 1
            detail[key].append([sid, v, p, pdo_r])
        elif v in rec["pos_verbs"]:
            counts["OUTOFSCOPE_within_transitive"] += 1
            detail["OUTOFSCOPE_within_transitive"].append([sid, v, p, pdo_r])
        else:
            counts["spurious_verb_unannotated"] += 1
            detail["spurious_verb_unannotated"].append([sid, v, p, pdo_r])
    return dict(counts), {k: vv[:15] for k, vv in detail.items()}, sorted(addressable_verbs)


def per_class_fp_split(kept, gold):
    """Coarse FP split reusing the scorer semantics: subcat (nopat verb) / within (pos verb, wrong obj) /
    spurious (unannotated verb)."""
    c = Counter()
    for sid, tup in kept:
        v = L.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if L.match_pos(v, p, rec["pos"]) is not None:
            continue
        if v in rec["nopat"]:
            c["subcat_fp"] += 1
        elif v in rec["pos_verbs"]:
            c["within_fp"] += 1
        else:
            c["spurious_fp"] += 1
    return dict(c)


# ------------------------------------------------------------------------------------------------
# Config.
# ------------------------------------------------------------------------------------------------
def _base_cfg():
    return dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42,
               heldout_frac=0.25, k_constructions=4, p_keep=60.0, p_drop=40.0, div_thr=3)


def cfg_smoke():
    c = _base_cfg()
    c.update(slice_lessons=["L04", "L10"], seeds=[7])   # L04 (say/inversion) + L10 (came/home motion, tell)
    return c


def cfg_full():
    c = _base_cfg()
    c.update(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], seeds=[7, 13, 19])
    return c


# ------------------------------------------------------------------------------------------------
# Run.
# ------------------------------------------------------------------------------------------------
def run_config(cfg, mode):
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    gold_agent = QUOT.load_gold_raw(cfg["slice_lessons"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = L.load_glove_for(toks)

    P_do, keep_abs, drop_abs, tdiag = pdo_table_and_split(order, reader_svo, sent_text, cfg)
    div_thr = cfg["div_thr"]

    per_seed = []
    ref = {}
    for seed in cfg["seeds"]:
        lccp_cfg = {k: v for k, v in cfg.items() if k != "seeds"}
        lccp_cfg["seed"] = seed

        # BASELINE base = LCCP arm-C (semantic teacher); TREATMENT base = syntactic frame-teacher T.
        keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
        keptT, artT, _gradT, wT, _subT = FT.run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed)

        # must-fail: P_do permuted syntactic base.
        P_do_perm = build_pdo_permutation(order, reader_svo, sent_text, seed)
        keptT_perm, artT_perm, _g2, wT_perm, _s2 = FT.run_arm(
            "syntactic", order, reader_svo, sent_text, glove, cfg, seed, pdo_override=P_do_perm)

        # STACK all three bases through the IDENTICAL ARG + QUOT filters.
        keptQ_base = stack_over(keptC0, order, sent_text, reader_svo, gold_agent, div_thr)
        keptQ_treat = stack_over(keptT, order, sent_text, reader_svo, gold_agent, div_thr)
        keptQ_perm = stack_over(keptT_perm, order, sent_text, reader_svo, gold_agent, div_thr)

        mQb = L.score_arm(keptQ_base, gold)
        mQt = L.score_arm(keptQ_treat, gold)
        mQp = L.score_arm(keptQ_perm, gold)

        # residual FPs suppressed by the treatment that the baseline kept (the discriminator action)
        base_keep = set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in keptQ_base)
        treat_keep = set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in keptQ_treat)
        base_fp = set(k for k in base_keep
                      if L.match_pos(k[1], k[2], gold.get(k[0], {"pos": []})["pos"]) is None)
        treat_fp = set(k for k in treat_keep
                       if L.match_pos(k[1], k[2], gold.get(k[0], {"pos": []})["pos"]) is None)
        fps_suppressed_by_treat = sorted(base_fp - treat_fp)
        true_pat_lost_by_treat = sorted(
            k for k in (base_keep - treat_keep)
            if L.match_pos(k[1], k[2], gold.get(k[0], {"pos": []})["pos"]) is not None)

        rret = (mQt["recall"] / mQb["recall"]) if mQb["recall"] > 0 else 0.0
        per_seed.append({
            "seed": seed,
            "Q_base": {k: mQb[k] for k in ("precision", "recall", "f1", "n_pred", "tp",
                                           "subcat_fp", "within_frame_fp", "spurious_verb_fp", "total_fp")},
            "Q_treat": {k: mQt[k] for k in ("precision", "recall", "f1", "n_pred", "tp",
                                            "subcat_fp", "within_frame_fp", "spurious_verb_fp", "total_fp")},
            "Q_pdoperm": {k: mQp[k] for k in ("precision", "recall", "f1", "n_pred", "total_fp")},
            "precision_delta_paired": round(mQt["precision"] - mQb["precision"], 4),
            "precision_delta_vs_0557": round(mQt["precision"] - PUBLISHED_STACK_PRECISION, 4),
            "recall_retention_treat_over_base": round(rret, 4),
            "n_fps_suppressed_by_treat": len(fps_suppressed_by_treat),
            "n_true_patients_lost_by_treat": len(true_pat_lost_by_treat),
            "w_f_dirpp_T": round(float(wT[DI]), 4),
            "w_f_dirpp_T_pdoperm": round(float(wT_perm[DI]), 4),
            "stacked_gain_clean": round(mQt["precision"] - PUBLISHED_STACK_PRECISION, 4),
            "stacked_gain_pdoperm": round(mQp["precision"] - PUBLISHED_STACK_PRECISION, 4),
        })
        if seed == cfg["seeds"][0]:
            triQb_c, triQb_d, addr_v = triage_residual(keptQ_base, gold, P_do, drop_abs)
            triQt_c, _triQt_d, _av = triage_residual(keptQ_treat, gold, P_do, drop_abs)
            ref = {
                "keptQ_base": keptQ_base, "keptQ_treat": keptQ_treat,
                "triage_Q_base": {"counts": triQb_c, "detail": triQb_d, "addressable_verbs": addr_v},
                "triage_Q_treat_counts": triQt_c,
                "fp_split_Q_base": per_class_fp_split(keptQ_base, gold),
                "fp_split_Q_treat": per_class_fp_split(keptQ_treat, gold),
                "fps_suppressed_by_treat_seed0": [list(k) + [round(float(P_do.get(k[1], -1)), 3)]
                                                  for k in fps_suppressed_by_treat],
                "true_patients_lost_by_treat_seed0": [list(k) for k in true_pat_lost_by_treat],
                "artT": artT,
                "P_do_ma_sample": artT.get("P_do_ma_sample", {}),
            }

    # aggregate
    def agg(getter):
        vals = [getter(p) for p in per_seed]
        return round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)

    pQt_m, pQt_s = agg(lambda p: p["Q_treat"]["precision"])
    pQb_m, pQb_s = agg(lambda p: p["Q_base"]["precision"])
    pQp_m, pQp_s = agg(lambda p: p["Q_pdoperm"]["precision"])
    rQt_m, _ = agg(lambda p: p["Q_treat"]["recall"])
    rQb_m, _ = agg(lambda p: p["Q_base"]["recall"])
    dpair_m, dpair_s = agg(lambda p: p["precision_delta_paired"])
    rret_m, rret_s = agg(lambda p: p["recall_retention_treat_over_base"])

    delta_abs = round(pQt_m - PUBLISHED_STACK_PRECISION, 4)
    mustfail_fires = bool(pQt_m > pQp_m + 0.01)
    material_move = bool(delta_abs >= 0.02)
    paired_positive = bool(dpair_m > 0.0)
    recall_ok = bool(rret_m >= 0.85)
    w_dirpp_T_neg_all = all(p["w_f_dirpp_T"] < 0 for p in per_seed)

    # positive control: baseline Q at seed0 reproduces the published 0.5574 (only strict at FULL config).
    base_seed0_prec = per_seed[0]["Q_base"]["precision"]
    baseline_reproduces_0557 = bool(abs(base_seed0_prec - PUBLISHED_STACK_PRECISION) < 0.02)

    if material_move and recall_ok and mustfail_fires and paired_positive:
        verdict = "HARD_PASS_FRAME_TEACHER_GENERALIZES"
    elif not material_move:
        verdict = "HARD_FAIL_NO_MATERIAL_MOVE"
    elif not recall_ok:
        verdict = "HARD_FAIL_RECALL_ARTIFACT"
    elif not mustfail_fires:
        verdict = "HARD_FAIL_CONSTRUCTION_DETERMINED"
    else:
        verdict = "MIDDLE_BAND"

    hashes = {"Q_base_semantic": kept_hash(ref["keptQ_base"]), "Q_treat_syntactic": kept_hash(ref["keptQ_treat"])}
    arms_differ = hashes["Q_base_semantic"] != hashes["Q_treat_syntactic"]
    baseline_in_band = bool(0.05 < pQb_m < 0.95)
    pdo_ma_vals = [d["P_do"] for d in ref["P_do_ma_sample"].values()] if ref["P_do_ma_sample"] else []
    global_do = ref["artT"]["teacher_diag"].get("global_do_rate")
    pdo_separates = bool(pdo_ma_vals and global_do is not None and float(np.mean(pdo_ma_vals)) < global_do)
    discriminator_fires = bool(per_seed[0]["n_fps_suppressed_by_treat"] > 0 and arms_differ
                               and pdo_separates and per_seed[0]["w_f_dirpp_T"] < 0)

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict,
        "needs_orchestrator_store_sync": True,
        "primary_metric": "STACKED patient-lens precision Q_treat (LCCP-frame-teacher -> ARG -> quotative) vs "
                          "0.5574 reference AND per-seed paired Q_base; recall retention; P_do-permute must-fail",
        "published_stack_precision_reference": PUBLISHED_STACK_PRECISION,
        "precision_Q_base_mean": pQb_m, "precision_Q_base_std": pQb_s,
        "precision_Q_treat_mean": pQt_m, "precision_Q_treat_std": pQt_s,
        "precision_Q_pdoperm_mean": pQp_m, "precision_Q_pdoperm_std": pQp_s,
        "recall_Q_base_mean": rQb_m, "recall_Q_treat_mean": rQt_m,
        "precision_delta_abs_vs_0557": delta_abs,
        "precision_delta_paired_mean": dpair_m, "precision_delta_paired_std": dpair_s,
        "recall_retention_mean": rret_m, "recall_retention_std": rret_s,
        "mustfail_pdo_permute_fires": mustfail_fires,
        "material_move": material_move, "paired_positive": paired_positive, "recall_ok": recall_ok,
        "w_f_dirpp_T_per_seed": [p["w_f_dirpp_T"] for p in per_seed],
        "w_f_dirpp_T_pdoperm_per_seed": [p["w_f_dirpp_T_pdoperm"] for p in per_seed],
        "w_f_dirpp_T_all_negative": w_dirpp_T_neg_all,
        "baseline_reproduces_0557_seed0": baseline_reproduces_0557,
        "baseline_precision_seed0": base_seed0_prec,
        "step1_triage_Q_base_residual": ref["triage_Q_base"],
        "step1_triage_Q_treat_residual_counts": ref["triage_Q_treat_counts"],
        "fp_split_Q_base_seed0": ref["fp_split_Q_base"],
        "fp_split_Q_treat_seed0": ref["fp_split_Q_treat"],
        "fps_suppressed_by_treat_seed0": ref["fps_suppressed_by_treat_seed0"],
        "true_patients_lost_by_treat_seed0": ref["true_patients_lost_by_treat_seed0"],
        "P_do_ma_sample_seed0": ref["P_do_ma_sample"],
        "syntactic_global_do_rate": global_do, "pdo_separates_ma_low": pdo_separates,
        "per_seed": per_seed,
        "kept_hashes": hashes, "arms_differ_verified": arms_differ,
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "adaptive_with_discriminator_gate",
        "n_sentences": len(order), "n_reader_svo": sum(len(reader_svo[sid]) for sid in order),
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "seeds": cfg["seeds"], "config": {k: v for k, v in cfg.items()},
        "HONESTY_GUARD": ("Precision reported vs 0.5574 EXACTLY (published stack) AND per-seed paired Q_base. "
                          "Recall retention reported (a recall-suppression artifact is NOT a precision win). "
                          "Per-class suppression delta + P_do-permute must-fail reported. The hand-seed scaffold "
                          "(MA_SEED Levin list gating f_dirpp + MA construction row) is inherited UNCHANGED from "
                          "atom 29349 and honestly declared; its de-confound is a SEPARATE refinement not claimed "
                          "here. n_pred ~61 -> precision granularity ~0.016/FP; absolute FP counts reported "
                          "alongside. No hand-applied number reported as learned; no out-of-corpus example."),
        "CITED": {"frame_teacher_mechanism": "atom 29349 / exp_lccp_motion_aspectual_syntactic_frame_teacher_v1 "
                                             "(P_do EMERGENT, w[f_dirpp] NEGATIVE, must-fail fires, VET-verified)",
                  "stacked_reader_0557": "data/exp_quotative_speaker_attribution_stack_break050_v1/metrics.json "
                                        ":arm_metrics.Q_quotative (precision 0.5574, recall 0.34, atom 29345 CG)",
                  "levin_seed": "Levin 1993 verb classes 51.1/51.3.2/47.6/55.1 (MA_SEED, gates f_dirpp only)"},
        "REQUIRED_FIELDS": ["verdict", "precision_Q_base_mean", "precision_Q_treat_mean",
                            "precision_Q_pdoperm_mean", "precision_delta_abs_vs_0557",
                            "precision_delta_paired_mean", "recall_retention_mean", "mustfail_pdo_permute_fires",
                            "w_f_dirpp_T_per_seed", "step1_triage_Q_base_residual", "fps_suppressed_by_treat_seed0",
                            "fp_split_Q_base_seed0", "fp_split_Q_treat_seed0", "per_seed"],
    }
    msg = (f"{verdict} | P Q_base={pQb_m:.4f} Q_treat={pQt_m:.4f}+-{pQt_s:.4f} Q_pdoperm={pQp_m:.4f} "
           f"| dAbs_vs0557={delta_abs:+.4f} dPaired={dpair_m:+.4f} Rret={rret_m:.3f} "
           f"| mustfail_fires={mustfail_fires} material={material_move} paired+={paired_positive} recallOK={recall_ok} "
           f"| w_dirpp_T={[p['w_f_dirpp_T'] for p in per_seed]} negAll={w_dirpp_T_neg_all} "
           f"| suppressed_FPs_seed0={per_seed[0]['n_fps_suppressed_by_treat']} "
           f"truePatLost_seed0={per_seed[0]['n_true_patients_lost_by_treat']} "
           f"| triageQ_base={ref['triage_Q_base']['counts']} "
           f"| base_repro_0557={baseline_reproduces_0557}({base_seed0_prec:.4f}) "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires} arms_differ={arms_differ} "
           f"pdo_sep={pdo_separates}")
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
    assert out["arms_differ_verified"], "META_RULE_AF: Q_base and Q_treat kept-sets bit-identical (arm no-op)"
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, out)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  [STEP1 triage Q_base residual] {out['step1_triage_Q_base_residual']['counts']}", flush=True)
    print(f"    addressable_verbs: {out['step1_triage_Q_base_residual']['addressable_verbs']}", flush=True)
    print(f"  [fp_split] Q_base={out['fp_split_Q_base_seed0']} Q_treat={out['fp_split_Q_treat_seed0']}", flush=True)
    print(f"  [FPs suppressed by treat, seed0] {out['fps_suppressed_by_treat_seed0']}", flush=True)
    print(f"  [true patients lost by treat, seed0] {out['true_patients_lost_by_treat_seed0']}", flush=True)
    print(f"  [P_do MA sample seed0] {out['P_do_ma_sample_seed0']} | globalDO={out['syntactic_global_do_rate']}",
          flush=True)
    for p in out["per_seed"]:
        print(f"  [seed {p['seed']}] P Q_base={p['Q_base']['precision']:.4f}({p['Q_base']['tp']}/{p['Q_base']['n_pred']}) "
              f"Q_treat={p['Q_treat']['precision']:.4f}({p['Q_treat']['tp']}/{p['Q_treat']['n_pred']}) "
              f"Q_pdoperm={p['Q_pdoperm']['precision']:.4f} | dPaired={p['precision_delta_paired']:+.4f} "
              f"Rret={p['recall_retention_treat_over_base']:.3f} | w_dirpp_T={p['w_f_dirpp_T']:+.3f} "
              f"(perm={p['w_f_dirpp_T_pdoperm']:+.3f}) suppFP={p['n_fps_suppressed_by_treat']} "
              f"lostTP={p['n_true_patients_lost_by_treat']}", flush=True)
    print(f"  [HONESTY] {out['HONESTY_GUARD']}", flush=True)
    return out


def self_test():
    # 1. stack_over composes ARG + QUOT and reduces (or equals) a base kept set (never grows it).
    #    Build a tiny synthetic base + minimal structures the imported filters need.
    order, sent_text, reader_svo = L.load_slice_and_reader(["L04"])
    gold, _gm = L.load_gold(["L04"])
    gold_agent = QUOT.load_gold_raw(["L04"])
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, L.lemma_verb(v)])
    glove = L.load_glove_for(toks)
    cfg = _base_cfg()
    keptC0 = L.run_arms(order, reader_svo, sent_text, glove, {**cfg, "seed": 7}, 7)[0]["C_lccp"]
    keptQ = stack_over(keptC0, order, sent_text, reader_svo, gold_agent, cfg["div_thr"])
    assert len(keptQ) <= len(keptC0), "stack must not grow the kept set"

    # 2. triage classes are disjoint + cover all FPs; addressable subset are nopat verbs.
    P_do, keep_abs, drop_abs, _td = pdo_table_and_split(order, reader_svo, sent_text, cfg)
    counts, detail, addr_v = triage_residual(keptQ, gold, P_do, drop_abs)
    m = L.score_arm(keptQ, gold)
    total_fp_from_triage = sum(v for k, v in counts.items() if k != "TP")
    assert total_fp_from_triage == m["total_fp"], (
        f"triage FP total {total_fp_from_triage} != scorer total_fp {m['total_fp']}")
    assert counts.get("TP", 0) == m["tp"], f"triage TP {counts.get('TP')} != scorer tp {m['tp']}"

    # 3. clean-toy P_do separation (reuse FT's validated mechanism): a directional-dominated verb gets LOW
    #    P_do, a DO-dominated verb HIGH; confirms the general lever is imported intact.
    def mk(v, p):
        tk = [v, p]
        c = {"sid": f"s{v}{p}", "v": v, "a": "x", "p": p, "tup": (v, "x", p),
             "feat": np.array([1.0, 0.5, 1.0, 0.0, 0.0, 0.0], dtype=float),
             "_sent": f"{v} {p}", "_iv": 0, "_ip": 1, "_toks": tk}
        c["_dir"] = bool(FT.is_directional_slot(p, tk, 0, 1))
        return c
    toy = []
    for p in ["home", "there", "back", "away", "home", "there"]:
        toy.append(mk("come", p))
    toy.append(mk("come", "box"))
    for p in ["house", "wall", "boat", "cart", "house", "wall"]:
        toy.append(mk("build", p))
    P_do_toy, _ = FT.build_syntactic_frame_table(toy, k_smooth=1.0)
    assert P_do_toy["come"] < 0.5 < P_do_toy["build"], (
        f"P_do separation weak: come={P_do_toy['come']:.3f} build={P_do_toy['build']:.3f}")

    # 4. P_do permutation preserves the multiset of values (marginal) but changes the mapping.
    perm = build_pdo_permutation(order, reader_svo, sent_text, 7)
    assert sorted(round(v, 6) for v in perm.values()) == sorted(round(P_do[v], 6) for v in perm), \
        "P_do permutation must preserve the value multiset"

    # 5. end-to-end smoke: arms differ, baseline in band, discriminator context present.
    out, _ = run_config(cfg_smoke(), "smoke")
    assert out["arms_differ_verified"], "arms Q_base and Q_treat must differ"
    assert out["baseline_in_band"], f"baseline precision out of band: {out['precision_Q_base_mean']}"
    print(f"[{ANCHOR_NAME}] self-test OK | toy P_do come={P_do_toy['come']:.3f} build={P_do_toy['build']:.3f} "
          f"| smoke: P Q_base={out['precision_Q_base_mean']:.4f} Q_treat={out['precision_Q_treat_mean']:.4f} "
          f"dAbs={out['precision_delta_abs_vs_0557']:+.4f} Rret={out['recall_retention_mean']:.3f} "
          f"suppFP_seed0={out['per_seed'][0]['n_fps_suppressed_by_treat']} "
          f"w_dirpp_T={out['w_f_dirpp_T_per_seed']} discrim={out['discriminator_fires']} "
          f"verdict={out['verdict']}", flush=True)


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
