"""LEAK-PROOF held-out-NEW relational inference: DECISION-TIME MULTI-CONSTRAINT REASONER over the learned rep.

NORTH-STAR STEP: reasoning OVER the learned representation. The confirmed win
  (experiments/exp_leakproof_relinfer_context_sweep_v1.py, banked 29587/88/89) shows SINGLE-SHOT leak-proof
  held-out-NEW inference: rank a held-out concept h's UNSEEN neighbour t by cosine(code[h], code[t]).
  LEARNED=0.6614 vs RAW_GROUNDING=0.5498 (margin +0.1116) at cap2500 all-context. Dose-response: the margin
  grows monotonically with the number of ENCODER-INPUT context edges (early fusion). A sibling cell pushed
  encoder-input DEPTH (multihop_v1) and got DEPTH_FLAT (0.6614->0.6582; early-fusion depth lever exhausted).

WHAT IS NEW (the untested lever): DECISION-TIME combination. Instead of pooling the context INTO code[h]
  (early fusion, done by the trained MLP), bring MULTIPLE per-anchor learned-inference constraints to bear
  at DECISION time and combine them with the substrate reasoner's ADDITIVE population-vector combiner
  (faithful emulation of hdlab/reasoner.py::DerivationReasoner._combiner_score -- sum the constraint reps,
  L2-normalize, cosine to each candidate; the reasoner's additive multi-constraint satisfaction core).
    Multi-constraint query for a held-out concept h: its SHOWN context anchors {a1..ak} are the GIVENS
    (each a known relation of h; leak-proof, disjoint from the predict target). To reach the held-out
    target t we combine the whole-concept constraint code[h] with per-anchor 2-hop constraints
    (h --given-- a_i --learned-inference-- t): each a_i imposes "t should be a learned-neighbour of a_i".
    reasoner score(t) = cosine( Z[t], L2( Z[h] + sum_i<=n Z[a_i] ) ). n=0 is EXACTLY single-shot (Gate D).
    The held-out TARGET edge h--t is NEVER in context or training (leak-proof witness, must print 0/N).

THE ONE NUMBER + THE TRAP (pre-registered BEFORE running):
  Bar (a) single-shot: does REASONER (n=ALL constraints) beat SINGLE-SHOT (n=0) for the LEARNED codes?
    L_lift = learned(ALL) - learned(n=0). HARD_PASS needs L_lift >= +0.02 with per-seed min > 0.
  THE ANTI-CAUTION GATE (load-bearing): the prior brain drill flagged that "more constraints -> better
    resolution" is GENERIC answer-set-shrinkage MATH, not a learned capability. To NOT be a third instance
    of that trap, the SAME additive combiner is fed NON-LEARNED (raw-grounding) constraints as a control:
    G_lift = grounding(ALL) - grounding(n=0). The learned rep is the genuine lever ONLY if the added-
    constraint lift is BIGGER for learned than for grounding: diff_lift = L_lift - G_lift >= +0.02.
    If L_lift >= 0.02 but diff_lift < 0.02 => COMBINATION_IS_GENERIC (the trap realized; honest, decisive).
  Bar (b) non-learned multi-hop structure: reasoner(learned, ALL) must beat ARM_STRUCT_MULTIHOP (PPR-lite
    len<=3) by >= 0.03. Bar (c) grounding-homophily: must beat single-shot grounding (n=0) by >= 0.03.
  Controls: ARM_RANDOM_INIT (untrained codes -> combiner ~ grounding); ARM_ANCHOR_SHUFFLE (bundle sourced
    from a DIFFERENT held-out concept's constraint set -> MUST collapse ~0.5, leak/artifact witness);
    ARM_POPULARITY ~0.5 (degree-matched validity). Validity: pop~0.5, anchor-shuffle collapses, power.

VERDICTS: HARD_PASS (L_lift>=.02 & diff_lift>=.02 & beats struct_mh & beats grounding & anchor-shuffle
  collapses & valid); COMBINATION_IS_GENERIC (L_lift>=.02 but diff_lift<.02 -> the CAUTION); REASONER_TIES
  (|L_lift|<.02 -> late-fusion combination does not beat trained early-fusion encoder; honest null);
  REASONER_WORSE (L_lift<=-.02); HARD_FAIL_REGIME_MISMATCH (Gate D n=0 learned != confirmed 0.6614 at
  cap2500); HARD_FAIL_INVALID (validity fails).

REUSED VERBATIM (imported): leak-proof CONTEXT-disjoint-PREDICT split + 0/N witness, deterministic sha256
  splits, degree-matched negative sampler, fusion self-teacher (geometry+VICReg+relpred-InfoNCE+EMA),
  tie-corrected Mann-Whitney AUC, target geometry (from context_sweep_v1); eval_struct_multihop (PPR-lite,
  from multihop_v1). NEW code = the additive multi-constraint reasoner scorer + its dose-response + the
  learned-vs-grounding lift-differential anti-trap gate.

HARD INVARIANTS: TEACHER-FREE (inputs = measured grounding + the foundation's own relational graph; no
  borrowed vectors). INDUCTIVE (held-out placed from its features). LEAK-PROOF (target h--t disjoint from
  context+training; negatives exclude every true neighbour). ASCII-only. CPU-only. Deterministic.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over the code matrices)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; anchor-shuffle + popularity witness the floor
# - baseline_in_band at smoke: anchor-shuffle ~0.5; popularity ~0.5; single-shot grounding a real signal; primary not saturated
# - discriminator survives scale: n=0 reproduces confirmed 0.6614 (Gate D); smoke previews the lift deltas
# - HARD_PASS strictly above floor: L_lift>=.02 AND per-seed min>0 AND diff_lift>=.02 (anti-generic-combination)
# - HP_SCOPE: gates apply to ARM_REASONER_LEARNED (primary) only
# - sweep axis n_constraints computed within one trained encoder per seed -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; anchor-shuffle+popularity witness it)
# - deterministic seeding: imported sha256 splits + fixed int seeds + sorted(); no hash()/list(set())
# - no substrate KGStore/fit objects (imports self-contained base cell + numpy + torch) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (per-seed + per-n logs flush=True)
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)

# REUSE VERBATIM from the confirmed dose-response cell (import; its main() is __main__-guarded).
from experiments.exp_leakproof_relinfer_context_sweep_v1 import (  # noqa: E402
    ALL_CONTEXT,
    GROUND_DIM,
    build_eval_context,
    build_leakproof_split,
    build_train_adjacency,
    compute_target_geometry,
    encode_all,
    eval_relational_inference,
    load_grounded_subgraph,
    select_landmarks,
    train_fusion,
    _auc_from_scores,
    _emb_digest,
    _l2_np,
    _pooled_ctx_block,
    _query_positives_negatives,
)
# stronger non-learned multi-hop structural baseline (PPR-lite len<=3) -- reuse from the sibling cell.
from experiments.exp_leakproof_relinfer_multihop_v1 import eval_struct_multihop  # noqa: E402

ANCHOR_NAME = "leakproof_relinfer_reasoner_multiconstraint_v1"

# ALL-constraints sentinel (use every available anchor).
ALL_CONSTR = 100000

# ---------------------------------------------------------------------------
# Config profiles (mirror base FULL_CFG so n=0 reproduces the confirmed single-shot number)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=400, seeds=[7], heldout_frac=0.2, top_rel=8, predict_frac=0.5,
    epochs=15, code_dim=32, hidden=64, lr=5e-3,
    n_landmarks=48, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    n_constraint_levels=[0, 1, ALL_CONSTR],
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=800, seeds=[7], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=80, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=192, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    n_constraint_levels=[0, 1, 2, 3, 5, ALL_CONSTR],
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=2500, seeds=[7, 13, 19], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=140, code_dim=128, hidden=256, lr=2.5e-3,
    n_landmarks=448, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    n_constraint_levels=[0, 1, 2, 3, 5, ALL_CONSTR],
)

EVAL_SEED = 20260726

# Pre-reg bands (applied to ARM_REASONER_LEARNED primary; PRIMARY constraint level = ALL).
CONFIRMED_SINGLESHOT_CAP2500 = 0.6614   # MEASURED@data/exp_leakproof_relinfer_context_sweep_v1/metrics.json (ALL, cap2500)
GATE_D_TOL = 0.03                        # n=0 learned must reproduce the confirmed single-shot number (cap2500)
HP_L_LIFT = 0.02                         # reasoner(ALL) must beat single-shot(n=0) by this ABSOLUTE margin
HP_DIFF_LIFT = 0.02                      # ANTI-CAUTION: learned lift must exceed grounding lift by this (not generic)
HP_OVER_STRUCTMH = 0.03                  # reasoner(learned,ALL) must beat the PPR-lite multi-hop baseline
HP_OVER_GROUNDING = 0.03                 # reasoner(learned,ALL) must beat single-shot grounding (n=0)
ANCHOR_SHUF_BAND = (0.44, 0.56)          # ARM_ANCHOR_SHUFFLE MUST collapse here (can-fail / leak witness)
POP_BAND = (0.44, 0.56)                  # ARM_POPULARITY MUST sit ~0.5 (degree-matching validity)
MIN_QUERY_TASKS = 100
MIN_QUERY_TASKS_SMOKE = 20

# Arms (code matrices)
LEARNED = "LEARNED"
GROUNDING = "GROUNDING"
RANDINIT = "RANDINIT"
CODE_KEYS = [LEARNED, GROUNDING, RANDINIT]

# Reported arm names (per-constraint-level for the code arms; single for func arms)
REASONER_LEARNED_ARM = "ARM_REASONER_LEARNED"
REASONER_GROUNDING_ARM = "ARM_REASONER_GROUNDING"
REASONER_RANDINIT_ARM = "ARM_REASONER_RANDINIT"
ANCHOR_SHUFFLE_ARM = "ARM_ANCHOR_SHUFFLE"
STRUCTMH_ARM = "ARM_STRUCT_MULTIHOP"
POP_ARM = "ARM_POPULARITY"


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(
        pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode,
        expected_n_units=expected_n_units, host=platform.node(),
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED",
        verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
        summary=("CELL_CRASHED: %s" % type(exc).__name__),
        elapsed_s=0.0, traceback=traceback.format_exc()[:5000],
        ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME,
    )
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# THE NEW MECHANISM: additive multi-constraint reasoner scorer.
# Faithful emulation of hdlab/reasoner.py::DerivationReasoner._combiner_score (population-vector combiner:
# sum the constraint reps, L2-normalize the bundle, cosine to each candidate). Multi-constraint satisfaction
# = bringing the whole-concept constraint code[h] PLUS up to n per-anchor 2-hop constraints code[a_i] to bear.
# n_constraints=0 => bundle == code[h] == the confirmed single-shot arm (Gate D positive control).
# ---------------------------------------------------------------------------
def eval_reasoner(Z, split, ev_ctx, n_constraints, bundle_perm=None):
    """Held-out relational-inference AUC under the additive multi-constraint combiner.

    Z: code matrix [K, d], rows L2-normalized (learned / grounding / random-init).
    n_constraints: number of anchor constraints to ADD to the whole-concept constraint (0 == single-shot;
      >= ALL_CONSTR uses every available anchor).
    bundle_perm: optional dict held_idx -> held_idx. When given, the constraint bundle for query h is built
      from a DIFFERENT concept's (h', anchors(h')) set while h's own candidates/negatives are scored
      (ANCHOR_SHUFFLE must-fail; the specific constraints are load-bearing iff this collapses to ~0.5).

    Returns (mean_auc, n_query, neg_in_exclude, mean_anchors_used). Iteration order + rng consumption match
    base.eval_relational_inference EXACTLY so at n=0 (no perm) the AUC is bit-equal to the base single-shot.
    """
    train_idx = ev_ctx["train_idx"]
    pos_of = ev_ctx["pos_of"]
    context_nei = split["context_nei"]
    rng = np.random.default_rng(EVAL_SEED)
    aucs = []
    neg_leak = 0
    anchors_used = []
    eps = 1e-8
    for h in split["held_idx"].tolist():
        qpn = _query_positives_negatives(h, split, ev_ctx, rng)
        if qpn is None:
            continue
        pos_arr, neg_arr, _ctxp, exclude = qpn
        neg_leak += sum(1 for n in neg_arr.tolist() if n in exclude)
        sel = np.concatenate([pos_arr, neg_arr])
        cand_concept = train_idx[sel]                      # candidate concept indices [n_cand]
        # source concept for the constraint bundle (h itself, or a permuted partner for anchor-shuffle)
        src = h if bundle_perm is None else int(bundle_perm.get(h, h))
        # anchors of src = its SHOWN context partners as concept indices, deterministic (sorted by gallery pos)
        src_ctx_pos = sorted(pos_of[j] for j in context_nei[src] if j in pos_of)
        anchor_concepts = [int(train_idx[p]) for p in src_ctx_pos]
        if n_constraints < ALL_CONSTR:
            anchor_concepts = anchor_concepts[:n_constraints]
        anchors_used.append(len(anchor_concepts))
        # additive population-vector combiner: sum(constraint reps), L2-normalize the bundle
        bundle = Z[src].astype(np.float64).copy()
        for a in anchor_concepts:
            bundle = bundle + Z[a].astype(np.float64)
        bn = float(np.linalg.norm(bundle))
        if bn <= 0.0:
            continue
        bundle = bundle / (bn + eps)
        sc = Z[cand_concept].astype(np.float64) @ bundle   # cosine to each candidate
        pm = np.zeros(sel.shape[0], dtype=bool)
        pm[:pos_arr.shape[0]] = True
        a = _auc_from_scores(sc, pm)
        if a is not None:
            aucs.append(a)
    mean_anchor = float(np.mean(anchors_used)) if anchors_used else 0.0
    if len(aucs) < 5:
        return float("nan"), len(aucs), neg_leak, mean_anchor
    return float(np.mean(aucs)), len(aucs), neg_leak, mean_anchor


def _build_anchor_perm(split, seed):
    """Deterministic derangement-ish permutation of held-out concepts (for ANCHOR_SHUFFLE)."""
    held = split["held_idx"]
    rng = np.random.default_rng(seed + 4242)
    if held.shape[0] <= 1:
        return {int(h): int(h) for h in held.tolist()}
    perm = held.copy()
    for _try in range(8):
        p = rng.permutation(held.shape[0])
        if np.all(p != np.arange(held.shape[0])):
            perm = held[p]
            break
    else:
        # guarantee no fixed point by a single roll if the loop never fully deranged
        p = np.roll(np.arange(held.shape[0]), 1)
        perm = held[p]
    return {int(h): int(perm[i]) for i, h in enumerate(held.tolist())}


# ---------------------------------------------------------------------------
# One seed: train ONE encoder, build code matrices, run the reasoner dose-response + controls
# ---------------------------------------------------------------------------
def build_context(split, cfg):
    own = split["own_feat"]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    ev_ctx = build_eval_context(split, cfg["n_deg_bins"])
    return base_feats, landmarks, target_geo, ev_ctx


def run_seed(seed, split, base_feats, landmarks, target_geo, ev_ctx, cfg, levels):
    c = cfg
    own = base_feats["own"]
    ctx = base_feats["ctx"]
    feats = dict(own=own, ctx=ctx)

    Z = {}
    Z[GROUNDING] = _l2_np(own.astype(np.float64)).astype(np.float32)   # raw grounding (non-learned constraint source)
    enc_l = train_fusion(feats, target_geo, landmarks, split, c, seed,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=True)
    Z[LEARNED] = encode_all(enc_l, feats)
    enc_r = train_fusion(feats, target_geo, landmarks, split, c, seed + 101,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=False)
    Z[RANDINIT] = encode_all(enc_r, feats)

    # ARMS-MUST-DIFFER (META_RULE_AF) over the code matrices
    digs = {k: _emb_digest(Z[k]) for k in CODE_KEYS}
    dl = sorted(digs.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            assert dl[i][1] != dl[j][1], ("META_RULE_AF VIOLATION: code matrices %s and %s bit-identical"
                                          % (dl[i][0], dl[j][0]))

    perm = _build_anchor_perm(split, seed)
    neg_leak_total = 0

    # dose-response over n_constraints for LEARNED / GROUNDING / RANDINIT
    per_n = {}
    n_query = None
    mean_anchor_all = None
    for n in levels:
        n_label = "ALL" if n >= ALL_CONSTR else n
        row = {}
        for key, arm in ((LEARNED, REASONER_LEARNED_ARM), (GROUNDING, REASONER_GROUNDING_ARM),
                         (RANDINIT, REASONER_RANDINIT_ARM)):
            auc, nq, nleak, man = eval_reasoner(Z[key], split, ev_ctx, n)
            neg_leak_total += nleak
            row[arm] = auc
            if arm == REASONER_LEARNED_ARM:
                n_query = nq
                if n >= ALL_CONSTR:
                    mean_anchor_all = man
        # ANCHOR_SHUFFLE at this level (learned codes, wrong constraint bundle -> must collapse)
        auc_sh, _nqs, nleak_sh, _man = eval_reasoner(Z[LEARNED], split, ev_ctx, n, bundle_perm=perm)
        neg_leak_total += nleak_sh
        row[ANCHOR_SHUFFLE_ARM] = auc_sh
        per_n[n_label] = row
        _log("seed=%d n_constraints=%-4s learned=%.4f grounding=%.4f randinit=%.4f anchor_shuffle=%.4f"
             % (seed, str(n_label), row[REASONER_LEARNED_ARM], row[REASONER_GROUNDING_ARM],
                row[REASONER_RANDINIT_ARM], row[ANCHOR_SHUFFLE_ARM]))

    # non-learned multi-hop structural baseline (PPR-lite len<=3) + popularity (n-independent).
    # NOTE: both helpers return 3-tuples (auc, n_query, neg_in_exclude).
    smh_auc, _nq, smh_leak = eval_struct_multihop(split, ev_ctx)
    pop_auc, _nq2, pop_leak = eval_relational_inference(None, split, ev_ctx, popularity=True)
    neg_leak_total += smh_leak + pop_leak
    _log("seed=%d %s=%.4f %s=%.4f n_q=%d mean_anchors@ALL=%.2f"
         % (seed, STRUCTMH_ARM, smh_auc, POP_ARM, pop_auc, n_query, mean_anchor_all or 0.0))

    if neg_leak_total != 0:
        raise RuntimeError("LEAK: %d negatives were true neighbours (must be 0)" % neg_leak_total)

    return dict(per_n=per_n, struct_multihop=smh_auc, popularity=pop_auc,
                n_query=n_query, mean_anchor_all=mean_anchor_all,
                code_digests=digs)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, data_meta, split_meta, cap_nodes, min_query_tasks, levels):
    n_labels = ["ALL" if n >= ALL_CONSTR else n for n in levels]

    def arm_series(n_label, arm):
        return np.array([m["per_n"][n_label][arm] for m in per_seed], dtype=np.float64)

    def arm_mean(n_label, arm):
        return float(np.nanmean(arm_series(n_label, arm)))

    # dose-response curves
    curve_learned = [(nl, round(arm_mean(nl, REASONER_LEARNED_ARM), 4)) for nl in n_labels]
    curve_grounding = [(nl, round(arm_mean(nl, REASONER_GROUNDING_ARM), 4)) for nl in n_labels]
    curve_randinit = [(nl, round(arm_mean(nl, REASONER_RANDINIT_ARM), 4)) for nl in n_labels]
    curve_anchorshuf = [(nl, round(arm_mean(nl, ANCHOR_SHUFFLE_ARM), 4)) for nl in n_labels]

    learned_n0 = arm_mean(0, REASONER_LEARNED_ARM)
    grounding_n0 = arm_mean(0, REASONER_GROUNDING_ARM)
    learned_all = arm_mean("ALL", REASONER_LEARNED_ARM)
    grounding_all = arm_mean("ALL", REASONER_GROUNDING_ARM)
    randinit_all = arm_mean("ALL", REASONER_RANDINIT_ARM)
    anchorshuf_all = arm_mean("ALL", ANCHOR_SHUFFLE_ARM)
    struct_mh = float(np.nanmean([m["struct_multihop"] for m in per_seed]))
    pop = float(np.nanmean([m["popularity"] for m in per_seed]))
    n_query = int(np.min([m["n_query"] for m in per_seed]))
    mean_anchor_all = float(np.nanmean([m["mean_anchor_all"] for m in per_seed]))

    # THE NUMBER: does bringing ALL learned constraints to bear beat single-shot (n=0)?
    l_lift_series = arm_series("ALL", REASONER_LEARNED_ARM) - arm_series(0, REASONER_LEARNED_ARM)
    g_lift_series = arm_series("ALL", REASONER_GROUNDING_ARM) - arm_series(0, REASONER_GROUNDING_ARM)
    L_lift = float(np.nanmean(l_lift_series))
    L_lift_min = float(np.nanmin(l_lift_series))
    G_lift = float(np.nanmean(g_lift_series))
    diff_lift_series = l_lift_series - g_lift_series
    diff_lift = float(np.nanmean(diff_lift_series))
    diff_lift_min = float(np.nanmin(diff_lift_series))

    # Gate D: n=0 learned reproduces the confirmed single-shot number (enforced only at cap2500)
    gate_d_applicable = (int(cap_nodes) == 2500)
    gate_d_delta = float(learned_n0 - CONFIRMED_SINGLESHOT_CAP2500)
    gate_d_ok = (not gate_d_applicable) or (abs(gate_d_delta) <= GATE_D_TOL)

    # validity
    asb_lo, asb_hi = ANCHOR_SHUF_BAND
    pb_lo, pb_hi = POP_BAND
    power_ok = bool(n_query >= min_query_tasks)
    anchor_shuffle_collapses = bool(asb_lo <= anchorshuf_all <= asb_hi)
    pop_ok = bool(pb_lo <= pop <= pb_hi)
    validity_ok = bool(power_ok and anchor_shuffle_collapses and pop_ok)

    beats_structmh = bool((learned_all - struct_mh) >= HP_OVER_STRUCTMH)
    beats_grounding = bool((learned_all - grounding_n0) >= HP_OVER_GROUNDING)
    l_lift_ok = bool(L_lift >= HP_L_LIFT and L_lift_min > 0.0)
    diff_lift_ok = bool(diff_lift >= HP_DIFF_LIFT)

    if not validity_ok:
        verdict = "HARD_FAIL_INVALID"
    elif not gate_d_ok:
        verdict = "HARD_FAIL_REGIME_MISMATCH"
    elif l_lift_ok and diff_lift_ok and beats_structmh and beats_grounding:
        verdict = "HARD_PASS"
    elif l_lift_ok and not diff_lift_ok:
        verdict = "COMBINATION_IS_GENERIC"     # THE CAUTION realized: learned lift ~ grounding lift
    elif abs(L_lift) < HP_L_LIFT:
        verdict = "REASONER_TIES_SINGLESHOT"   # late-fusion combination does not beat trained early-fusion
    elif L_lift <= -HP_L_LIFT:
        verdict = "REASONER_WORSE"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | THE-NUMBER L_lift = learned(ALL) - learned(n0) = %.4f - %.4f = %+.4f (min=%+.4f, need>=%.2f) | "
        "ANTI-CAUTION diff_lift = L_lift - G_lift = %+.4f - %+.4f = %+.4f (min=%+.4f, need>=%.2f) | "
        "learned dose-response %s | grounding dose-response %s | anchor_shuffle %s | randinit(ALL)=%.4f | "
        "learned(ALL)=%.4f struct_multihop=%.4f (beats=%s) grounding(n0)=%.4f (beats=%s) | "
        "Gate-D n0_learned=%.4f ok=%s(delta=%+.4f vs %.4f, applicable=%s) | "
        "VALIDITY power=%s(n_q=%d) anchor_shuffle_collapses=%s(=%.4f) pop_ok=%s(=%.4f) | mean_anchors@ALL=%.2f | "
        "leak-proof witness: context-INT-predict overlap=%d/%d (MUST be 0) | "
        "corpus K=%d train=%d heldout=%d eval_queries=%d pairs=%d rels=%d"
        % (verdict, learned_all, learned_n0, L_lift, L_lift_min, HP_L_LIFT,
           L_lift, G_lift, diff_lift, diff_lift_min, HP_DIFF_LIFT,
           curve_learned, curve_grounding, curve_anchorshuf, randinit_all,
           learned_all, struct_mh, beats_structmh, grounding_n0, beats_grounding,
           learned_n0, gate_d_ok, gate_d_delta, CONFIRMED_SINGLESHOT_CAP2500, gate_d_applicable,
           power_ok, n_query, anchor_shuffle_collapses, anchorshuf_all, pop_ok, pop, mean_anchor_all,
           split_meta["no_overlap_witness_overlap"], split_meta["no_overlap_witness_predict_targets"],
           data_meta["n_kept_concepts"], split_meta["n_train"], split_meta["n_heldout"],
           split_meta["n_eval_queries"], data_meta["n_kept_pairs"], data_meta["n_rel_slots"]))

    gates = dict(
        reasoner_learned_n0=learned_n0, reasoner_learned_all=learned_all,
        reasoner_grounding_n0=grounding_n0, reasoner_grounding_all=grounding_all,
        reasoner_randinit_all=randinit_all, anchor_shuffle_all=anchorshuf_all,
        struct_multihop=struct_mh, popularity=pop,
        L_lift=L_lift, L_lift_min=L_lift_min, G_lift=G_lift,
        diff_lift=diff_lift, diff_lift_min=diff_lift_min,
        l_lift_ok=l_lift_ok, diff_lift_ok=diff_lift_ok,
        beats_struct_multihop=beats_structmh, beats_grounding=beats_grounding,
        margin_over_struct_multihop=float(learned_all - struct_mh),
        margin_over_grounding_n0=float(learned_all - grounding_n0),
        gate_d_ok=gate_d_ok, gate_d_delta=gate_d_delta, gate_d_applicable=gate_d_applicable,
        power_ok=power_ok, n_query=n_query,
        anchor_shuffle_collapses=anchor_shuffle_collapses, pop_ok=pop_ok, validity_ok=validity_ok,
        mean_anchors_at_all=mean_anchor_all,
        curve_learned=curve_learned, curve_grounding=curve_grounding,
        curve_randinit=curve_randinit, curve_anchorshuf=curve_anchorshuf,
        no_overlap_witness_overlap=split_meta["no_overlap_witness_overlap"],
        no_overlap_witness_predict_targets=split_meta["no_overlap_witness_predict_targets"],
        anchor_shuffle_band=list(ANCHOR_SHUF_BAND), pop_band=list(POP_BAND),
        hp_l_lift=HP_L_LIFT, hp_diff_lift=HP_DIFF_LIFT,
        hp_over_struct_multihop=HP_OVER_STRUCTMH, hp_over_grounding=HP_OVER_GROUNDING,
        min_query_tasks=min_query_tasks,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test (REAL-CODE-PATH): tiny synthetic grounded subgraph
# ---------------------------------------------------------------------------
def reasoner_selftest():
    """Assert (a) eval_reasoner at n=0 (no perm) == base.eval_relational_inference single-shot AUC (the
    reasoner reduces to single-shot at zero constraints), (b) leak witness 0, (c) anchor-shuffle produces a
    finite AUC that is materially LOWER than the true-bundle AUC (constraints are load-bearing), (d) adding
    constraints changes the AUC (mechanism fires)."""
    from experiments.exp_leakproof_relinfer_context_sweep_v1 import N_GROUPS, N_VALUE_DIMS
    K = 220
    rng = np.random.default_rng(5)
    ids = ["c%03d" % i for i in range(K)]
    vals = rng.standard_normal((K, N_VALUE_DIMS))
    gpres = np.ones((K, N_GROUPS), dtype=np.float64)
    pair_rels = {}
    for _ in range(4000):
        a = int(rng.integers(0, K)); b = int(rng.integers(0, K))
        if a == b:
            continue
        if a > b:
            a, b = b, a
        pair_rels.setdefault((a, b), set()).add("REL_%d" % rng.integers(0, 4))
    top_rels = ["REL_0", "REL_1", "REL_2", "REL_3"]
    rel_id = {r: i for i, r in enumerate(top_rels)}
    R = len(top_rels) + 1

    def _rel_slot(r):
        return rel_id.get(r, R - 1)

    data = dict(ids=ids, surfaces=ids, vals=vals, gpres=gpres, pair_rels=pair_rels,
                K=K, R=R, rel_slot=_rel_slot,
                meta=dict(n_kept_concepts=K, n_kept_pairs=len(pair_rels), n_rel_slots=R))
    cfg = dict(heldout_frac=0.3, predict_frac=0.5, n_deg_bins=5,
               epochs=12, code_dim=32, hidden=48, lr=5e-3,
               n_landmarks=32, n_land_batch=32, n_anchor_batch=64,
               lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
               infonce_tau=0.2, feat_dropout=0.1)
    try:
        split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
    except RuntimeError as e:
        return False, dict(err="split:" + str(e)[:200])

    base_feats, landmarks, target_geo, ev_ctx = build_context(split, cfg)
    feats = dict(own=base_feats["own"], ctx=base_feats["ctx"])
    enc = train_fusion(feats, target_geo, landmarks, split, cfg, 7,
                       use_ctx=True, w_rel=cfg["w_rel"], w_ema=cfg["w_ema"], do_train=True)
    Zl = encode_all(enc, feats)

    # (a) n=0 reasoner == base single-shot
    base_auc, base_nq, base_leak = eval_relational_inference(Zl, split, ev_ctx)
    r0_auc, r0_nq, r0_leak, _man0 = eval_reasoner(Zl, split, ev_ctx, 0)
    same_singleshot = bool(np.isfinite(base_auc) and np.isfinite(r0_auc)
                           and abs(base_auc - r0_auc) < 1e-6 and base_nq == r0_nq)
    # (d) adding all constraints changes the AUC (mechanism fires)
    rall_auc, _nq, rall_leak, man_all = eval_reasoner(Zl, split, ev_ctx, ALL_CONSTR)
    mechanism_fires = bool(np.isfinite(rall_auc) and abs(rall_auc - r0_auc) > 1e-4 and man_all > 0.0)
    # (c) anchor-shuffle RUNS via a genuine derangement + finite AUC (MECHANICS only; on this random
    #     synthetic graph there is no learnable relational structure, so true-vs-shuffled bundles are
    #     equally uninformative -- the COLLAPSE property is a real-data discriminator verified at smoke,
    #     NOT a synthetic-graph guarantee).
    perm = _build_anchor_perm(split, 7)
    held_list = split["held_idx"].tolist()
    deranged = bool(len(held_list) <= 1 or all(perm[h] != h for h in held_list))
    sh_auc, _nqs, sh_leak, _m = eval_reasoner(Zl, split, ev_ctx, ALL_CONSTR, bundle_perm=perm)
    anchor_shuffle_ran = bool(np.isfinite(sh_auc) and deranged)
    no_leak = bool(base_leak == 0 and r0_leak == 0 and rall_leak == 0 and sh_leak == 0)

    checks = dict(base_singleshot_auc=round(base_auc, 6), reasoner_n0_auc=round(r0_auc, 6),
                  same_singleshot=same_singleshot, reasoner_all_auc=round(rall_auc, 4),
                  mechanism_fires=mechanism_fires, mean_anchors_all=round(man_all, 3),
                  anchor_shuffle_auc=round(sh_auc, 4), anchor_shuffle_ran=anchor_shuffle_ran,
                  deranged=deranged, no_leak=no_leak, n_query=r0_nq,
                  overlap=split["split_meta"]["no_overlap_witness_overlap"])
    ok = bool(same_singleshot and mechanism_fires and anchor_shuffle_ran and no_leak
              and split["split_meta"]["no_overlap_witness_overlap"] == 0)
    return ok, checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap-nodes", type=int, default=0, help="override cap_nodes (0=cfg default)")
    args, _unknown = ap.parse_known_args()

    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode

    torch.set_num_threads(max(1, os.cpu_count() or 1))
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode])
    if args.cap_nodes and args.cap_nodes > 0:
        cfg["cap_nodes"] = int(args.cap_nodes)
    min_query = MIN_QUERY_TASKS_SMOKE if run_mode in ("smoke", "self_test") else MIN_QUERY_TASKS

    anchor = ANCHOR_NAME if not (args.cap_nodes and run_mode == "full") else ("%s_cap%d" % (ANCHOR_NAME, args.cap_nodes))
    if run_mode == "self_test":
        anchor = anchor + "_selftest"
    elif run_mode == "smoke":
        anchor = anchor + "_smoke"
    output_dir = get_output_dir(anchor)
    expected_n_units = len(cfg["seeds"])                # one trained encoder per seed (n-levels are within-unit eval)
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = reasoner_selftest()
    _log("reasoner_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED reasoner_ok=%s: %s" % (st_ok, st_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            reasoner_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})

    split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
    _log("split: %s" % split["split_meta"])
    base_feats, landmarks, target_geo, ev_ctx = build_context(split, cfg)
    levels = list(cfg["n_constraint_levels"])
    _log("landmarks=%d ctx_dim=%d gallery=%d n_constraint_levels=%s"
         % (landmarks.shape[0], base_feats["ctx"].shape[1], ev_ctx["G"],
            ["ALL" if n >= ALL_CONSTR else n for n in levels]))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], split, base_feats, landmarks, target_geo, ev_ctx, cfg, levels)
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS additive multi-constraint reasoner over leak-proof held-out inference exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            reasoner_selftest=st_res, data_meta=data["meta"], split_meta=split["split_meta"],
            per_n={str(k): v for k, v in pm["per_n"].items()},
            struct_multihop=pm["struct_multihop"], popularity=pm["popularity"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed = []
    seed_failures = []
    total_units_run = 0
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, split, base_feats, landmarks, target_geo, ev_ctx, cfg, levels)
            per_seed.append(pm)
            total_units_run += 1
            write_partial(output_dir, "seed%d" % seed, dict(
                seed=seed, per_n={str(k): v for k, v in pm["per_n"].items()},
                struct_multihop=pm["struct_multihop"], popularity=pm["popularity"],
                n_query=pm["n_query"], mean_anchor_all=pm["mean_anchor_all"], run_mode=run_mode))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if total_units_run < expected_n_units:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units (%d seeds) got %d (failures=%s)"
                        % (expected_n_units, len(cfg["seeds"]), total_units_run, seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, data_meta=data["meta"]))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(
        per_seed, data["meta"], split["split_meta"], cfg["cap_nodes"], min_query, levels)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"],
        n_constraint_levels=["ALL" if n >= ALL_CONSTR else n for n in levels],
        expected_total_units=expected_n_units, total_units_run=total_units_run,
        config={k: v for k, v in cfg.items()},
        data_meta={k: v for k, v in data["meta"].items()},
        split_meta=split["split_meta"],
        gates=gates,
        per_seed=[{"seed": cfg["seeds"][i],
                   "per_n": {str(k): v for k, v in per_seed[i]["per_n"].items()},
                   "struct_multihop": per_seed[i]["struct_multihop"],
                   "popularity": per_seed[i]["popularity"],
                   "n_query": per_seed[i]["n_query"],
                   "mean_anchor_all": per_seed[i]["mean_anchor_all"]} for i in range(len(per_seed))],
        reasoner_selftest=st_res, seed_failures=seed_failures,
    )
    write_metrics(output_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
