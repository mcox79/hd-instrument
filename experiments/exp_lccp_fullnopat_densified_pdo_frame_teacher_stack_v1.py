"""DENSIFIED-P_do FULL-NOPAT FRAME-TEACHER STACK PAYOFF TEST (the reopening of atom 29350's HARD_FAIL).

atom 29350 (exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1) HARD_FAIL_RECALL_ARTIFACT: the syntactic
frame-frequency teacher (P_do) FIT ON THE 163-SENT GOLD SLICE raised the stacked patient-lens precision to
0.5803 (delta +0.0229 vs the 0.5574 reader) BUT only by DESTROYING recall (retention 0.6165 < 0.85) and the
must-fail did NOT fire (permute did not collapse the gain = vacuous). ROOT CAUSE localized by that cell: the
per-verb P_do was CORPUS-SPARSE on 163 sentences (build P_do 0.365, coin-flip regime) so it suppressed BOTH
the spurious build/stream AND the TRUE build/huts (a recall artifact), AND 8/27 residual FPs were high-P_do-
INVISIBLE verbs (say/leave/call = report/light verbs whose slots look like DOs -- frame-frequency STRUCTURALLY
cannot flag those).

THE REOPENING (atom of the density test exp_animacy_pverb_frame_density_scale_test_v1, MIXED_PDO_DENSIFIES):
P_do DENSIFIES on the 99k raw words already staged -- gold-verb median n_frame 1 -> 13; motion verbs correctly
LOW (come 0.335 / go 0.417 / sit 0.195 / walk 0.177 / run 0.292) vs argument-taking HIGH (reach 0.951 / keep
0.706 / lie 0.766 / stand 0.656). NOTE (honest, load-bearing): build densifies to n_frame 25 but P_do STAYS
LOW (0.3885, n_DO 9 / n_DIR 16) -- densification does NOT lift build; any recall recovery must come from the
verbs that densify HIGH (reach/keep/give/obtain/...), NOT build.

THE PAYOFF QUESTION (this cell): re-run the EXACT 29350 stack with the DENSIFIED FULL-CORPUS P_do table
injected into the treatment arm -- does the STACKED patient-lens precision actually MOVE materially above
0.5574 at BOUNDED RECALL COST (retention >= 0.85) with the frame signal DOING THE WORK (must-fail: permute the
densified P_do -> the gain collapses)? OR was sparse P_do only HALF the bottleneck -- the residual still
dominated by the structural high-P_do-INVISIBLE verbs (say/leave/call) that densification cannot touch (the
honest partial)?

ONE VARIABLE = the per-verb P_do TABLE injected into the syntactic frame teacher: SLICE (fit on the 163-sent
gold cands, = the 29350 treatment, reproduced live as the prior-failure reference) vs DENSE (fit on the full
~99k-word 5-reader corpus via the density-test parser, injected through the teacher's pdo_override path).
EVERYTHING else BYTE-IDENTICAL to 29350: the semantic-coherence LCCP base C0 (Q_base = the 0.5574 reader), the
same candidate gen / 8 features / MA construction row / f_dirpp MA scoping, the same ARG categorial cascade,
the same quotative arm, the same lr/epochs/thresholds/seeds. Only the P_do source differs across the two
treatment arms.

ARMS (stacked through the IDENTICAL ARG + QUOT filters; kept sets = the patient-lens reader):
  Q_base   = LCCP arm-C (semantic-coherence teacher) -> ARG -> QUOT  (the 0.5574 stacked reader; positive ctrl)
  Q_slice  = syntactic frame teacher, SLICE P_do (no override)  -> ARG -> QUOT  (reproduces 29350 Q_treat)
  Q_dense  = syntactic frame teacher, DENSE full-corpus P_do (pdo_override) -> ARG -> QUOT  (THE test)
  Q_dperm  = syntactic frame teacher, DENSE P_do PERMUTED across verbs (must-fail) -> ARG -> QUOT

MEASURED (decisive; vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json; category-c held OUT):
  PRIMARY = STACKED patient-lens precision Q_dense vs 0.5574 AND per-seed paired vs Q_base; recall retention
    Q_dense/Q_base (>= 0.85 = not a recall artifact); the DENSE-P_do-permute must-fail (Q_dense > Q_dperm +
    0.01 = the gain is driven by the REAL frame signal). SECONDARY = the SLICE arm reproduced live (must match
    29350: ~0.5803 precision / ~0.6165 retention / mustfail False) as the prior-failure reference; the cause-
    (a) SPARSE vs cause-(b) STRUCTURAL decomposition -- how many true patients LOST by SLICE does DENSE
    RECOVER (cause-a, fixed by densification) vs how many Q_dense residual FPs are high-P_do-INVISIBLE verbs
    (cause-b, remains); build/huts KEPT? build/stream SUPPRESSED?; per-class FP split; per-seed stability.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = the LIVE-recomputed STACKED reader Q_base (reproduces 0.5574 at seed7 within 0.02) AND
       the SLICE arm reproduces 29350's Q_treat (prior-failure reference); NOT strawmen.
  (G2) ONE VARIABLE = SLICE P_do vs DENSE full-corpus P_do injected into the teacher; ARG + QUOT + base identical.
  (G3) CAN-FAIL-BOTH-WAYS: Q_dense rises >= +0.02 at retention >= 0.85 with the gain collapsing under DENSE-
       P_do-permute (HARD-PASS: densification was the bottleneck, LEARNED) OR fails to move / buys precision
       with recall / survives permute / residual dominated by structural high-P_do-invisible verbs (HARD-FAIL:
       sparse P_do was only half the bottleneck -- the honest partial).
  (G4) difficulty ON: full independent gold, contested category-c held OUT of gold pos/nopat by construction;
       the target is the residual the 0.557 stack still mis-licenses.
  (G5) discriminator fires at smoke: DENSE P_do differs from SLICE (build n_frame >> slice), Q_dense kept set
       differs from Q_base, DENSE P_do separates motion-verbs-low from argument-verbs-high, w[f_dirpp](dense)<0.

VERDICT BANDS (pre-registered; IDENTICAL to 29350 -- NOT retuned; only the P_do source changed):
  delta_abs    = mean(precision_Q_dense) - 0.5574                 (material-move bar = >= +0.02)
  delta_paired = mean(precision_Q_dense - precision_Q_base)       (per-seed paired mechanism effect; must be > 0)
  rret         = mean(recall_Q_dense / recall_Q_base)             (recall retention; >= 0.85)
  mustfail     = mean(precision_Q_dense) > mean(precision_Q_dperm) + 0.01   (gain collapses under DENSE permute)
  HARD_PASS_DENSIFIED_FRAME_TEACHER_GENERALIZES: delta_abs >= 0.02 AND delta_paired > 0 AND rret >= 0.85 AND mustfail.
  HARD_FAIL_NO_MATERIAL_MOVE:        delta_abs < 0.02.
  HARD_FAIL_RECALL_ARTIFACT:         delta_abs >= 0.02 BUT rret < 0.85 (precision bought by destroying recall;
                                     = 29350's failure persists -- densification did not fix the recall side).
  HARD_FAIL_CONSTRUCTION_DETERMINED: delta_abs >= 0.02, rret ok, BUT not mustfail (gain survives DENSE permute).
  MIDDLE_BAND: material + recall ok + mustfail but paired <= 0 (seed-luck), or partial across seeds.

HONESTY GUARD (mandatory; printed + stored): report the stacked move vs 0.5574 EXACTLY AND per-seed paired
  Q_base; report recall retention (do NOT sell a recall-suppression artifact as a precision win -- the 29350
  trap); report the SLICE-arm reproduction as the prior-failure reference; report the cause-(a) recovered vs
  cause-(b) structural-residual decomposition; report build/huts kept + build/stream suppressed EXPLICITLY;
  build densified P_do STAYS LOW (0.39) so build/huts recovery is NOT expected from densification -- state that.
  The hand-seed scaffold (MA_SEED Levin list gating f_dirpp; MA construction row) is inherited UNCHANGED from
  29350 and honestly declared; its de-confound is a SEPARATE refinement, NOT claimed here. n_pred ~61 ->
  precision granularity ~0.016/FP; report absolute FP counts alongside precision. No number reported as learned
  when hand-applied. No out-of-corpus example invented. Do NOT redefine the pre-registered bars mid-run.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- ONE full-corpus reader parse
  (~5.7k sentences, done ONCE, ~60-180s) to fit the DENSE P_do table, then per seed: 1 LCCP arm-C recompute
  (GloVe + logistic) + 1 SLICE frame-teacher base + 1 DENSE frame-teacher base + 1 DENSE-permute base + 4
  post-hoc stack passes (ARG + quotative, cheap) over ~114 sentences; x 3 seeds; wall < ~8min. Foreground
  local-to-completion (NO queue; NO push; NO remote-persist; needs_orchestrator_store_sync=True). Storage:
  no_storage (extraction-precision measurement). CRLB n/a (precision/recall census; no additive-Gaussian
  estimator floor). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, deterministic hashlib + deterministic
  WordNet synset order (inherited from QUOT); no salted builtin hash / list(set); numpy default RNG seeded.

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (Q_base vs Q_dense kept-set hashes differ; SLICE vs DENSE reported)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < precision_Q_base < 0.95) + Q_base reproduces 0.5574 (full seed7)
- discriminator fires at smoke (DENSE P_do >> SLICE for build/come; Q_dense suppresses >0 Q_base FPs; arms
  differ; DENSE P_do separates; w[f_dirpp](dense) < 0)
- multi-seed (3 seeds full); must-fail (DENSE P_do permute) PER SEED; precision aggregated mean/std
- deterministic seeding; all numbers tagged MEASURED@/CITED@ (printed at run)
- clean-toy mechanism self-test (DENSE-vs-SLICE injection differs; stack-suppression; permute preserves marginal)
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

ANCHOR_NAME = "lccp_fullnopat_densified_pdo_frame_teacher_stack_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as L          # noqa: E402
import experiments.exp_lccp_motion_aspectual_subcat_break_v1 as MA                     # noqa: E402
import experiments.exp_lccp_motion_aspectual_syntactic_frame_teacher_v1 as FT          # noqa: E402
import experiments.exp_arg_adjunct_role_eligibility_categorial_break050_v1 as ARG      # noqa: E402
import experiments.exp_quotative_speaker_attribution_stack_break050_v1 as QUOT         # noqa: E402
import experiments.exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1 as S350         # noqa: E402
import experiments.exp_animacy_pverb_frame_density_scale_test_v1 as DENS               # noqa: E402
import experiments.exp_reader_clauseseg_topical_animate_subject_v2 as V2               # noqa: E402

DI = FT.DI  # index of f_dirpp in the 8-dim feature vector
PUBLISHED_STACK_PRECISION = S350.PUBLISHED_STACK_PRECISION  # 0.5574 CITED@ atom 29345 stacked reader
# CITED@ atom 29350 (SLICE) prior-failure reference values (this cell reproduces the SLICE arm live):
CITED_29350_SLICE = {"precision_Q_treat_mean": 0.5803, "recall_retention_mean": 0.6165,
                     "mustfail_pdo_permute_fires": False, "verdict": "HARD_FAIL_RECALL_ARTIFACT",
                     "MEASURED": "data/exp_lccp_fullnopat_syntactic_frame_teacher_stack_v1/metrics.json"}


# ------------------------------------------------------------------------------------------------
# DENSE full-corpus P_do table (fit ONCE on the ~99k-word 5-reader corpus via the density-test parser).
# ------------------------------------------------------------------------------------------------
def fit_dense_pdo(max_lessons=None):
    """Parse all 5 McGuffey readers with the reader's own parser (density-test path), build FT candidates,
    return (P_do_full dict, diag, n_sent, n_svo, n_lessons). This is the ONE densified table injected into
    the treatment arm's teacher (the single manipulated variable vs the 163-sent slice table)."""
    clf_reader = V2._fit_clf()
    order_f, sent_f, svo_f, n_lessons = DENS.parse_full_corpus(clf_reader, max_lessons=max_lessons)
    cands_f = FT.build_cands(order_f, svo_f, sent_f)
    P_do_full, diag = FT.build_syntactic_frame_table(cands_f)
    n_svo = sum(len(svo_f[s]) for s in order_f)
    return P_do_full, diag, len(order_f), n_svo, n_lessons


def permute_pdo(P_do, seed):
    """Must-fail: permute P_do VALUES across verbs (seeded numpy rng, NOT builtin hash), breaking the
    frame-freq <-> verb link while preserving the marginal P_do distribution."""
    verbs = sorted(P_do.keys())
    vals = np.array([P_do[v] for v in verbs])
    rng = np.random.default_rng(seed + 909)
    perm = rng.permutation(len(verbs))
    return {verbs[i]: float(vals[perm[i]]) for i in range(len(verbs))}


def dense_coverage(P_do_full, order, reader_svo):
    """How many gold-slice verbs the DENSE full-corpus table covers (missing verbs DEFER in the target = a
    genuine consequence of densification-via-a-different-parser; reported, not hidden)."""
    slice_verbs = sorted(set(L.lemma_verb(t[0]) for sid in order for t in reader_svo[sid]))
    covered = [v for v in slice_verbs if v in P_do_full]
    missing = [v for v in slice_verbs if v not in P_do_full]
    return {"n_slice_verbs": len(slice_verbs), "n_covered_by_dense": len(covered),
            "coverage_frac": round(len(covered) / len(slice_verbs), 4) if slice_verbs else 0.0,
            "missing_verbs": missing}


# ------------------------------------------------------------------------------------------------
# cause-(a) SPARSE-fixed vs cause-(b) STRUCTURAL-remains decomposition (the task's central question).
# ------------------------------------------------------------------------------------------------
def _keyset(kept):
    return set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in kept)


def _is_tp(k, gold):
    return L.match_pos(k[1], k[2], gold.get(k[0], {"pos": []})["pos"]) is not None


def decompose_causes(keptQ_base, keptQ_slice, keptQ_dense, gold, P_do_full, drop_abs):
    """cause-(a): true patients LOST by SLICE that DENSE RECOVERS (verbs that densify HIGH -> recall fixed).
    cause-(b): Q_dense residual FPs whose verb has HIGH DENSE P_do (> drop_abs) -- frame-freq says 'takes an
    object' but it is still a spurious patient (report/light verbs say/leave/call): densification CANNOT
    touch these. Also: build/huts kept? build/stream suppressed?"""
    base_k, slice_k, dense_k = _keyset(keptQ_base), _keyset(keptQ_slice), _keyset(keptQ_dense)
    base_tp = set(k for k in base_k if _is_tp(k, gold))
    slice_tp = set(k for k in slice_k if _is_tp(k, gold))
    dense_tp = set(k for k in dense_k if _is_tp(k, gold))
    dense_fp = set(k for k in dense_k if not _is_tp(k, gold))

    tp_lost_by_slice = base_tp - slice_tp                 # recall damage of the sparse arm
    tp_recovered_by_dense = (dense_tp & tp_lost_by_slice)  # cause-(a): densification fixed these
    tp_still_lost_by_dense = base_tp - dense_tp            # recall still lost even with dense P_do

    struct_resid = []   # cause-(b): high-P_do FP the frame teacher structurally cannot flag
    frameaddr_resid = []
    for k in sorted(dense_fp):
        pdo = P_do_full.get(k[1])
        pdo_r = round(float(pdo), 3) if pdo is not None else None
        if pdo is not None and pdo > drop_abs:
            struct_resid.append([k[0], k[1], k[2], pdo_r])
        else:
            frameaddr_resid.append([k[0], k[1], k[2], pdo_r])

    def _has(keyset, verb, patient):
        return any(kk[1] == verb and kk[2] == patient for kk in keyset)

    build_probe = {
        "build_huts_kept_by_base": _has(base_k, "build", "huts"),
        "build_huts_kept_by_slice": _has(slice_k, "build", "huts"),
        "build_huts_kept_by_dense": _has(dense_k, "build", "huts"),
        "build_stream_kept_by_base": _has(base_k, "build", "stream"),
        "build_stream_kept_by_slice": _has(slice_k, "build", "stream"),
        "build_stream_kept_by_dense": _has(dense_k, "build", "stream"),
        "build_dense_P_do": round(float(P_do_full.get("build")), 4) if "build" in P_do_full else None,
    }
    return {
        "n_tp_lost_by_slice": len(tp_lost_by_slice),
        "tp_lost_by_slice": sorted([list(k) for k in tp_lost_by_slice]),
        "n_tp_recovered_by_dense_causeA": len(tp_recovered_by_dense),
        "tp_recovered_by_dense_causeA": sorted([list(k) for k in tp_recovered_by_dense]),
        "n_tp_still_lost_by_dense": len(tp_still_lost_by_dense),
        "tp_still_lost_by_dense": sorted([list(k) for k in tp_still_lost_by_dense]),
        "n_structural_highPdo_residual_causeB": len(struct_resid),
        "structural_highPdo_residual_causeB": struct_resid,
        "n_frameaddressable_residual_dense": len(frameaddr_resid),
        "frameaddressable_residual_dense": frameaddr_resid,
        "build_probe": build_probe,
    }


# ------------------------------------------------------------------------------------------------
# Config.
# ------------------------------------------------------------------------------------------------
def _base_cfg():
    return dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60, keep_thr=0.45, subcat_thr=0.42,
               heldout_frac=0.25, k_constructions=4, p_keep=60.0, p_drop=40.0, div_thr=3)


def cfg_smoke():
    # Smoke parses the FULL corpus (dense_max_lessons=None) so the DENSE table is the REAL one and the
    # discriminator fires at full-scale params (build/reach only appear in the later readers); only the eval
    # scope (2 lessons, 1 seed) is reduced. Per DISCRIMINATOR-MUST-SURVIVE-SCALE.
    c = _base_cfg()
    c.update(slice_lessons=["L04", "L10"], seeds=[7], dense_max_lessons=None)
    return c


def cfg_full():
    c = _base_cfg()
    c.update(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], seeds=[7, 13, 19],
             dense_max_lessons=None)
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
    div_thr = cfg["div_thr"]

    # DENSE P_do table (fit ONCE on the full corpus).
    P_do_full, dense_diag, n_sent_full, n_svo_full, n_lessons_full = fit_dense_pdo(cfg["dense_max_lessons"])
    cov = dense_coverage(P_do_full, order, reader_svo)

    # SLICE P_do + slice target thresholds (for triage classing; = the 29350 teacher).
    P_do_slice, keep_abs_s, drop_abs_s, _td = S350.pdo_table_and_split(order, reader_svo, sent_text, cfg)
    # DENSE target thresholds (percentiles of the gold-slice cands' DENSE P_do; for cause-(b) classing).
    cands_slice = FT.build_cands(order, reader_svo, sent_text)
    _tf_d, keep_abs_d, drop_abs_d = FT.make_syntactic_target_fn(cands_slice, P_do_full, cfg)

    per_seed = []
    ref = {}
    for seed in cfg["seeds"]:
        lccp_cfg = {k: v for k, v in cfg.items() if k not in ("seeds", "dense_max_lessons")}
        lccp_cfg["seed"] = seed

        keptC0 = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)[0]["C_lccp"]
        # SLICE treatment base = 29350 Q_treat (no override) -- prior-failure reference.
        keptT_slice, artT_s, _g0, wT_s, _s0 = FT.run_arm("syntactic", order, reader_svo, sent_text, glove, cfg, seed)
        # DENSE treatment base = full-corpus P_do injected via pdo_override.
        keptT_dense, artT_d, _g1, wT_d, _s1 = FT.run_arm(
            "syntactic", order, reader_svo, sent_text, glove, cfg, seed, pdo_override=P_do_full)
        # must-fail: DENSE P_do permuted across verbs.
        P_do_perm = permute_pdo(P_do_full, seed)
        keptT_dperm, artT_p, _g2, wT_p, _s2 = FT.run_arm(
            "syntactic", order, reader_svo, sent_text, glove, cfg, seed, pdo_override=P_do_perm)

        keptQ_base = S350.stack_over(keptC0, order, sent_text, reader_svo, gold_agent, div_thr)
        keptQ_slice = S350.stack_over(keptT_slice, order, sent_text, reader_svo, gold_agent, div_thr)
        keptQ_dense = S350.stack_over(keptT_dense, order, sent_text, reader_svo, gold_agent, div_thr)
        keptQ_dperm = S350.stack_over(keptT_dperm, order, sent_text, reader_svo, gold_agent, div_thr)

        mQb = L.score_arm(keptQ_base, gold)
        mQs = L.score_arm(keptQ_slice, gold)
        mQd = L.score_arm(keptQ_dense, gold)
        mQp = L.score_arm(keptQ_dperm, gold)

        base_fp = set(k for k in _keyset(keptQ_base) if not _is_tp(k, gold))
        dense_fp = set(k for k in _keyset(keptQ_dense) if not _is_tp(k, gold))
        fps_suppressed_by_dense = sorted(base_fp - dense_fp)

        rret = (mQd["recall"] / mQb["recall"]) if mQb["recall"] > 0 else 0.0
        rret_slice = (mQs["recall"] / mQb["recall"]) if mQb["recall"] > 0 else 0.0
        per_seed.append({
            "seed": seed,
            "Q_base": {k: mQb[k] for k in ("precision", "recall", "f1", "n_pred", "tp",
                                           "subcat_fp", "within_frame_fp", "spurious_verb_fp", "total_fp")},
            "Q_slice": {k: mQs[k] for k in ("precision", "recall", "f1", "n_pred", "tp", "total_fp")},
            "Q_dense": {k: mQd[k] for k in ("precision", "recall", "f1", "n_pred", "tp",
                                            "subcat_fp", "within_frame_fp", "spurious_verb_fp", "total_fp")},
            "Q_dperm": {k: mQp[k] for k in ("precision", "recall", "n_pred", "total_fp")},
            "precision_delta_paired": round(mQd["precision"] - mQb["precision"], 4),
            "precision_delta_vs_0557": round(mQd["precision"] - PUBLISHED_STACK_PRECISION, 4),
            "recall_retention_dense_over_base": round(rret, 4),
            "recall_retention_slice_over_base": round(rret_slice, 4),
            "slice_precision_delta_vs_0557": round(mQs["precision"] - PUBLISHED_STACK_PRECISION, 4),
            "n_fps_suppressed_by_dense": len(fps_suppressed_by_dense),
            "w_f_dirpp_dense": round(float(wT_d[DI]), 4),
            "w_f_dirpp_slice": round(float(wT_s[DI]), 4),
            "w_f_dirpp_dperm": round(float(wT_p[DI]), 4),
        })
        if seed == cfg["seeds"][0]:
            triQb_c, triQb_d, addr_v = S350.triage_residual(keptQ_base, gold, P_do_full, drop_abs_d)
            triQd_c, _d, _a = S350.triage_residual(keptQ_dense, gold, P_do_full, drop_abs_d)
            causes = decompose_causes(keptQ_base, keptQ_slice, keptQ_dense, gold, P_do_full, drop_abs_d)
            ref = {
                "keptQ_base": keptQ_base, "keptQ_slice": keptQ_slice, "keptQ_dense": keptQ_dense,
                "triage_Q_base_dense_classing": {"counts": triQb_c, "detail": triQb_d, "addressable_verbs": addr_v},
                "triage_Q_dense_counts": triQd_c,
                "fp_split_Q_base": S350.per_class_fp_split(keptQ_base, gold),
                "fp_split_Q_slice": S350.per_class_fp_split(keptQ_slice, gold),
                "fp_split_Q_dense": S350.per_class_fp_split(keptQ_dense, gold),
                "fps_suppressed_by_dense_seed0": [list(k) + [round(float(P_do_full.get(k[1], -1)), 3),
                                                             round(float(P_do_slice.get(k[1], -1)), 3)]
                                                  for k in fps_suppressed_by_dense],
                "causes_decomposition": causes,
            }

    def agg(getter):
        vals = [getter(p) for p in per_seed]
        return round(float(np.mean(vals)), 4), round(float(np.std(vals)), 4)

    pQd_m, pQd_s = agg(lambda p: p["Q_dense"]["precision"])
    pQb_m, pQb_s = agg(lambda p: p["Q_base"]["precision"])
    pQs_m, pQs_s = agg(lambda p: p["Q_slice"]["precision"])
    pQp_m, pQp_s = agg(lambda p: p["Q_dperm"]["precision"])
    rQd_m, _ = agg(lambda p: p["Q_dense"]["recall"])
    rQb_m, _ = agg(lambda p: p["Q_base"]["recall"])
    rQs_m, _ = agg(lambda p: p["Q_slice"]["recall"])
    dpair_m, dpair_s = agg(lambda p: p["precision_delta_paired"])
    rret_m, rret_s = agg(lambda p: p["recall_retention_dense_over_base"])
    rret_slice_m, _ = agg(lambda p: p["recall_retention_slice_over_base"])

    delta_abs = round(pQd_m - PUBLISHED_STACK_PRECISION, 4)
    slice_delta_abs = round(pQs_m - PUBLISHED_STACK_PRECISION, 4)
    mustfail_fires = bool(pQd_m > pQp_m + 0.01)
    material_move = bool(delta_abs >= 0.02)
    paired_positive = bool(dpair_m > 0.0)
    recall_ok = bool(rret_m >= 0.85)
    w_dirpp_dense_neg_all = all(p["w_f_dirpp_dense"] < 0 for p in per_seed)

    base_seed0_prec = per_seed[0]["Q_base"]["precision"]
    baseline_reproduces_0557 = bool(abs(base_seed0_prec - PUBLISHED_STACK_PRECISION) < 0.02)
    slice_reproduces_29350 = bool(abs(pQs_m - CITED_29350_SLICE["precision_Q_treat_mean"]) < 0.03)

    if material_move and recall_ok and mustfail_fires and paired_positive:
        verdict = "HARD_PASS_DENSIFIED_FRAME_TEACHER_GENERALIZES"
    elif not material_move:
        verdict = "HARD_FAIL_NO_MATERIAL_MOVE"
    elif not recall_ok:
        verdict = "HARD_FAIL_RECALL_ARTIFACT"
    elif not mustfail_fires:
        verdict = "HARD_FAIL_CONSTRUCTION_DETERMINED"
    else:
        verdict = "MIDDLE_BAND"

    hashes = {"Q_base": S350.kept_hash(ref["keptQ_base"]), "Q_slice": S350.kept_hash(ref["keptQ_slice"]),
              "Q_dense": S350.kept_hash(ref["keptQ_dense"])}
    arms_differ = hashes["Q_base"] != hashes["Q_dense"]
    slice_vs_dense_differ = hashes["Q_slice"] != hashes["Q_dense"]
    baseline_in_band = bool(0.05 < pQb_m < 0.95)

    # DENSE P_do separation: motion verbs LOW vs global DO rate; build densified stays LOW (honest).
    ma_dense = {v: round(float(P_do_full[v]), 4) for v in sorted(FT.MA_SEED) if v in P_do_full}
    global_do = dense_diag.get("global_do_rate")
    ma_low_vals = [P_do_full[v] for v in FT.MA_SEED
                   if v in P_do_full and v in ("come", "go", "sit", "walk", "run")]
    pdo_separates = bool(ma_low_vals and global_do is not None and float(np.mean(ma_low_vals)) < global_do)
    build_slice = P_do_slice.get("build")
    build_dense = P_do_full.get("build")
    build_densified = bool(build_slice is not None and build_dense is not None
                           and dense_diag["per_verb"].get("build", {}).get("n_DO", 0)
                           + dense_diag["per_verb"].get("build", {}).get("n_DIR", 0) >= 10)
    discriminator_fires = bool(per_seed[0]["n_fps_suppressed_by_dense"] > 0 and arms_differ
                               and pdo_separates and per_seed[0]["w_f_dirpp_dense"] < 0 and build_densified)

    out = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict,
        "needs_orchestrator_store_sync": True,
        "primary_metric": "STACKED patient-lens precision Q_dense (DENSE full-corpus P_do frame teacher -> ARG "
                          "-> quotative) vs 0.5574 AND per-seed paired Q_base; recall retention; DENSE-P_do-"
                          "permute must-fail. ONE VARIABLE vs Q_slice = the P_do table (slice vs full corpus).",
        "one_variable": "per-verb P_do table injected into the syntactic frame teacher: 163-sent gold slice "
                        "(Q_slice = 29350) vs full ~99k-word 5-reader corpus (Q_dense). ARG+QUOT+base identical.",
        "published_stack_precision_reference": PUBLISHED_STACK_PRECISION,
        "cited_29350_slice_prior_failure": CITED_29350_SLICE,
        "precision_Q_base_mean": pQb_m, "precision_Q_base_std": pQb_s,
        "precision_Q_slice_mean": pQs_m, "precision_Q_slice_std": pQs_s,
        "precision_Q_dense_mean": pQd_m, "precision_Q_dense_std": pQd_s,
        "precision_Q_dperm_mean": pQp_m, "precision_Q_dperm_std": pQp_s,
        "recall_Q_base_mean": rQb_m, "recall_Q_slice_mean": rQs_m, "recall_Q_dense_mean": rQd_m,
        "precision_delta_abs_vs_0557": delta_abs,
        "slice_precision_delta_abs_vs_0557": slice_delta_abs,
        "precision_delta_paired_mean": dpair_m, "precision_delta_paired_std": dpair_s,
        "recall_retention_mean": rret_m, "recall_retention_std": rret_s,
        "recall_retention_slice_mean": rret_slice_m,
        "mustfail_dense_pdo_permute_fires": mustfail_fires,
        "material_move": material_move, "paired_positive": paired_positive, "recall_ok": recall_ok,
        "w_f_dirpp_dense_per_seed": [p["w_f_dirpp_dense"] for p in per_seed],
        "w_f_dirpp_slice_per_seed": [p["w_f_dirpp_slice"] for p in per_seed],
        "w_f_dirpp_dperm_per_seed": [p["w_f_dirpp_dperm"] for p in per_seed],
        "w_f_dirpp_dense_all_negative": w_dirpp_dense_neg_all,
        "baseline_reproduces_0557_seed0": baseline_reproduces_0557, "baseline_precision_seed0": base_seed0_prec,
        "slice_reproduces_29350_prior_failure": slice_reproduces_29350,
        "dense_corpus": {"n_sent": n_sent_full, "n_svo": n_svo_full, "n_lessons": n_lessons_full,
                         "n_verbs": dense_diag.get("n_verbs"), "global_do_rate": global_do},
        "dense_coverage_of_slice_verbs": cov,
        "dense_P_do_ma_sample": ma_dense,
        "build_P_do_slice": (round(float(build_slice), 4) if build_slice is not None else None),
        "build_P_do_dense": (round(float(build_dense), 4) if build_dense is not None else None),
        "build_dense_frame_counts": dense_diag["per_verb"].get("build"),
        "build_densified": build_densified,
        "dense_target_keep_abs": round(float(keep_abs_d), 4), "dense_target_drop_abs": round(float(drop_abs_d), 4),
        "slice_target_keep_abs": round(float(keep_abs_s), 4), "slice_target_drop_abs": round(float(drop_abs_s), 4),
        "step1_triage_Q_base_residual_dense_classing": ref["triage_Q_base_dense_classing"],
        "step1_triage_Q_dense_residual_counts": ref["triage_Q_dense_counts"],
        "fp_split_Q_base_seed0": ref["fp_split_Q_base"],
        "fp_split_Q_slice_seed0": ref["fp_split_Q_slice"],
        "fp_split_Q_dense_seed0": ref["fp_split_Q_dense"],
        "fps_suppressed_by_dense_seed0": ref["fps_suppressed_by_dense_seed0"],
        "cause_decomposition_seed0": ref["causes_decomposition"],
        "pdo_separates_ma_low": pdo_separates,
        "per_seed": per_seed,
        "kept_hashes": hashes, "arms_differ_verified": arms_differ,
        "slice_vs_dense_kept_differ": slice_vs_dense_differ,
        "arms_differ_exempted": [["Q_slice", "Q_dense"]],  # may coincide if densification changes no kept item
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "adaptive_with_discriminator_gate",
        "crlb_n_a": "precision/recall census over a fixed candidate set; no additive-Gaussian estimator floor",
        "n_sentences": len(order), "n_reader_svo": sum(len(reader_svo[sid]) for sid in order),
        "n_gold_pos": sum(len(r["pos"]) for r in gold.values()),
        "n_gold_nopat": sum(len(r["nopat"]) for r in gold.values()),
        "seeds": cfg["seeds"], "config": {k: v for k, v in cfg.items()},
        "HONESTY_GUARD": ("Precision reported vs 0.5574 EXACTLY (published stack) AND per-seed paired Q_base. "
                          "Recall retention reported (a recall-suppression artifact is NOT a precision win -- "
                          "the 29350 trap). SLICE arm reproduced live as the prior-failure reference. cause-(a) "
                          "sparse-fixed (true patients recovered by densification) vs cause-(b) structural high-"
                          "P_do-invisible residual (say/leave/call, densification cannot touch) both reported. "
                          "build densified P_do STAYS LOW (~0.39, n_DO<n_DIR) so build/huts recovery is NOT "
                          "expected from densification -- reported explicitly. The MA_SEED Levin scaffold gating "
                          "f_dirpp + MA construction row are inherited UNCHANGED from 29350; their de-confound is "
                          "a SEPARATE refinement not claimed here. n_pred ~61 -> precision granularity ~0.016/FP; "
                          "absolute FP counts reported. No hand-applied number reported as learned. Pre-registered "
                          "bars NOT retuned (identical to 29350; only the P_do source changed)."),
        "CITED": {"frame_teacher_mechanism": "atom 29349 / exp_lccp_motion_aspectual_syntactic_frame_teacher_v1",
                  "stacked_reader_0557": "atom 29345 / data/exp_quotative_speaker_attribution_stack_break050_v1",
                  "prior_failure_29350": CITED_29350_SLICE["MEASURED"],
                  "density_reopening": "data/exp_animacy_pverb_frame_density_scale_test_v1/metrics.json "
                                       "(MIXED_PDO_DENSIFIES; build 10->25 obs P_do 0.365->0.389)"},
        "REQUIRED_FIELDS": ["verdict", "precision_Q_base_mean", "precision_Q_slice_mean", "precision_Q_dense_mean",
                            "precision_Q_dperm_mean", "precision_delta_abs_vs_0557", "precision_delta_paired_mean",
                            "recall_retention_mean", "recall_retention_slice_mean", "mustfail_dense_pdo_permute_fires",
                            "w_f_dirpp_dense_per_seed", "slice_reproduces_29350_prior_failure",
                            "cause_decomposition_seed0", "fp_split_Q_base_seed0", "fp_split_Q_dense_seed0",
                            "dense_P_do_ma_sample", "build_P_do_dense", "per_seed"],
    }
    msg = (f"{verdict} | P Q_base={pQb_m:.4f} Q_slice={pQs_m:.4f} Q_dense={pQd_m:.4f}+-{pQd_s:.4f} "
           f"Q_dperm={pQp_m:.4f} | dAbs_vs0557={delta_abs:+.4f} (slice {slice_delta_abs:+.4f}) "
           f"dPaired={dpair_m:+.4f} | Rret dense={rret_m:.3f} slice={rret_slice_m:.3f} "
           f"| mustfail={mustfail_fires} material={material_move} paired+={paired_positive} recallOK={recall_ok} "
           f"| w_dirpp_dense={[p['w_f_dirpp_dense'] for p in per_seed]} negAll={w_dirpp_dense_neg_all} "
           f"| suppFP_seed0={per_seed[0]['n_fps_suppressed_by_dense']} "
           f"| causeA_recovered={ref['causes_decomposition']['n_tp_recovered_by_dense_causeA']} "
           f"causeB_struct={ref['causes_decomposition']['n_structural_highPdo_residual_causeB']} "
           f"still_lost={ref['causes_decomposition']['n_tp_still_lost_by_dense']} "
           f"| build P_do {out['build_P_do_slice']}->{out['build_P_do_dense']} "
           f"huts_dense={ref['causes_decomposition']['build_probe']['build_huts_kept_by_dense']} "
           f"| base_repro0557={baseline_reproduces_0557}({base_seed0_prec:.4f}) "
           f"slice_repro29350={slice_reproduces_29350} "
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
    assert out["arms_differ_verified"], "META_RULE_AF: Q_base and Q_dense kept-sets bit-identical (arm no-op)"
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    write_metrics(output_dir, out)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  [dense corpus] {out['dense_corpus']}", flush=True)
    print(f"  [dense coverage of slice verbs] {out['dense_coverage_of_slice_verbs']}", flush=True)
    print(f"  [dense P_do MA sample] {out['dense_P_do_ma_sample']}", flush=True)
    print(f"  [build] slice P_do={out['build_P_do_slice']} dense P_do={out['build_P_do_dense']} "
          f"counts={out['build_dense_frame_counts']} densified={out['build_densified']}", flush=True)
    print(f"  [dense target] keep_abs={out['dense_target_keep_abs']} drop_abs={out['dense_target_drop_abs']}", flush=True)
    print(f"  [fp_split] Q_base={out['fp_split_Q_base_seed0']} Q_slice={out['fp_split_Q_slice_seed0']} "
          f"Q_dense={out['fp_split_Q_dense_seed0']}", flush=True)
    print(f"  [FPs suppressed by dense, seed0 (verb, patient, dense_Pdo, slice_Pdo)] "
          f"{out['fps_suppressed_by_dense_seed0']}", flush=True)
    c = out["cause_decomposition_seed0"]
    print(f"  [cause-(a) SPARSE-fixed] tp_lost_by_slice={c['n_tp_lost_by_slice']} "
          f"recovered_by_dense={c['n_tp_recovered_by_dense_causeA']} {c['tp_recovered_by_dense_causeA']}", flush=True)
    print(f"  [cause-(a) residual] tp_still_lost_by_dense={c['n_tp_still_lost_by_dense']} "
          f"{c['tp_still_lost_by_dense']}", flush=True)
    print(f"  [cause-(b) STRUCTURAL high-P_do-invisible] n={c['n_structural_highPdo_residual_causeB']} "
          f"{c['structural_highPdo_residual_causeB']}", flush=True)
    print(f"  [build probe] {c['build_probe']}", flush=True)
    for p in out["per_seed"]:
        print(f"  [seed {p['seed']}] P Q_base={p['Q_base']['precision']:.4f}({p['Q_base']['tp']}/{p['Q_base']['n_pred']}) "
              f"Q_slice={p['Q_slice']['precision']:.4f} Q_dense={p['Q_dense']['precision']:.4f}"
              f"({p['Q_dense']['tp']}/{p['Q_dense']['n_pred']}) Q_dperm={p['Q_dperm']['precision']:.4f} "
              f"| dPaired={p['precision_delta_paired']:+.4f} Rret dense={p['recall_retention_dense_over_base']:.3f} "
              f"slice={p['recall_retention_slice_over_base']:.3f} "
              f"| w_dirpp dense={p['w_f_dirpp_dense']:+.3f} (perm={p['w_f_dirpp_dperm']:+.3f}) "
              f"suppFP={p['n_fps_suppressed_by_dense']}", flush=True)
    print(f"  [HONESTY] {out['HONESTY_GUARD']}", flush=True)
    return out


def self_test():
    # 1. permute preserves the P_do marginal multiset but changes the mapping.
    toy_pdo = {"come": 0.20, "build": 0.39, "reach": 0.95, "keep": 0.71, "sit": 0.19}
    perm = permute_pdo(toy_pdo, 7)
    assert sorted(round(v, 6) for v in perm.values()) == sorted(round(v, 6) for v in toy_pdo.values()), \
        "permute must preserve the value multiset"
    assert set(perm.keys()) == set(toy_pdo.keys()), "permute must preserve the verb key set"

    # 2. cause decomposition classes are consistent (recovered subset of lost; struct+frameaddr = all dense FP).
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
    keptQ_base = S350.stack_over(keptC0, order, sent_text, reader_svo, gold_agent, cfg["div_thr"])
    # tiny dense-ish table from the slice itself (self-test only exercises the plumbing, not the science).
    cands = FT.build_cands(order, reader_svo, sent_text)
    P_do_toy, _d = FT.build_syntactic_frame_table(cands)
    _tf, _ka, drop_abs = FT.make_syntactic_target_fn(cands, P_do_toy, cfg)
    causes = decompose_causes(keptQ_base, keptQ_base, keptQ_base, gold, P_do_toy, drop_abs)
    # base==slice==dense here -> nothing lost, nothing recovered, struct+frameaddr covers all dense FP.
    dense_fp_total = causes["n_structural_highPdo_residual_causeB"] + causes["n_frameaddressable_residual_dense"]
    m = L.score_arm(keptQ_base, gold)
    assert dense_fp_total == m["total_fp"], f"cause FP split {dense_fp_total} != scorer total_fp {m['total_fp']}"
    assert causes["n_tp_lost_by_slice"] == 0 and causes["n_tp_recovered_by_dense_causeA"] == 0, \
        "identical arms must lose/recover nothing"

    # 3. injecting a DIFFERENT (non-uniform) P_do table via pdo_override changes the treatment kept set (the
    #    one variable actually moves the mechanism). Use a 2-lesson slice (enough candidates) and compare the
    #    slice-P_do run vs a PERMUTED-slice override (non-uniform; a UNIFORM table is degenerate under the
    #    percentile target and cannot test this). Proven live: slice kept-set != permuted kept-set.
    order2, sent2, svo2 = L.load_slice_and_reader(["L04", "L10"])
    toks2 = set()
    for sid in order2:
        for v, a, p in svo2[sid]:
            toks2.update([p, L.lemma_verb(v)])
    glove2 = L.load_glove_for(toks2)
    cands2 = FT.build_cands(order2, svo2, sent2)
    P_do2, _d2 = FT.build_syntactic_frame_table(cands2)
    keptT_slice, _a0, _g0, _w0, _s0 = FT.run_arm("syntactic", order2, svo2, sent2, glove2, cfg, 7)
    keptT_perm, _a1, _g1, _w1, _s1 = FT.run_arm("syntactic", order2, svo2, sent2, glove2, cfg, 7,
                                                pdo_override=permute_pdo(P_do2, 7))
    assert S350.kept_hash(keptT_slice) != S350.kept_hash(keptT_perm), \
        "pdo_override must change the treatment kept set (one-variable injection is live)"

    # 4. DENSE fit path runs on a small cap + covers common verbs (real-code-path exercise for F.1).
    P_do_full, ddiag, n_sent, n_svo, n_les = fit_dense_pdo(max_lessons=40)
    assert n_sent > 100 and n_svo > 50, f"dense parse too small: {n_sent} sent / {n_svo} svo"
    assert "come" in P_do_full or "go" in P_do_full, f"dense table missing common motion verbs: {list(P_do_full)[:20]}"

    # 5. end-to-end smoke plumbing (capped dense parse for speed; the REAL smoke gate uses the full corpus):
    #    arms differ, baseline in band, cause-decomposition present.
    st_cfg = {**cfg_smoke(), "dense_max_lessons": 40}
    out, _ = run_config(st_cfg, "smoke")
    assert out["arms_differ_verified"], "arms Q_base and Q_dense must differ"
    assert out["baseline_in_band"], f"baseline precision out of band: {out['precision_Q_base_mean']}"
    print(f"[{ANCHOR_NAME}] self-test OK | permute-marginal OK | cause-split OK | override-live OK "
          f"| dense40 {n_sent}sent/{n_svo}svo | plumbing: P Q_base={out['precision_Q_base_mean']:.4f} "
          f"Q_slice={out['precision_Q_slice_mean']:.4f} Q_dense={out['precision_Q_dense_mean']:.4f} "
          f"dAbs={out['precision_delta_abs_vs_0557']:+.4f} Rret={out['recall_retention_mean']:.3f} "
          f"build_dense_Pdo={out['build_P_do_dense']} discrim={out['discriminator_fires']} "
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
