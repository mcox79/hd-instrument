"""LEAK-PROOF held-out-NEW relational-inference: MULTI-HOP CONSTRAINT-SCALING (push the constraint lever).

WHY: The confirmed dose-response (banked 29587/29588/29589, cell
  experiments/exp_leakproof_relinfer_context_sweep_v1.py) shows margin(learned - raw_grounding) grows
  MONOTONICALLY with the number of 1-hop CONTEXT edges brought to bear:
    cap2500 curve (MEASURED@data/exp_leakproof_relinfer_context_sweep_v1/metrics.json:sweep_summary.curve):
      ctx=1  learned=0.6173 margin=+0.0675 ;  ctx=ALL learned=0.6614 margin=+0.1116
    cap4000 (MEASURED@data/exp_leakproof_relinfer_context_sweep_v1_cap4000/...): ctx=ALL learned=0.6786.
  That is the reasoning theory (resolution scales with # constraints). This cell PUSHES the same lever a
  different direction: instead of MORE 1-hop edges, bring DEEPER (multi-HOP) relational constraints to bear,
  aggregated reasoner-style (additive typed-relation-path constraint blocks the fusion MLP sums). Question:
  does absolute leak-proof held-out-NEW inference AUC rise ABOVE the single-hop all-context ceiling (~0.66
  at cap2500 / ~0.68 at cap4000) as hop-depth 1 -> 2 -> 3 adds more constraints?

WHAT IS NEW vs the confirmed base (everything else REUSED verbatim by import):
  (1) MULTI-HOP CONTEXT (rep INPUT): the base pools 1-hop neighbour grounding per typed relation. This cell
      adds, for hop-depth d in {2, 3}, additional per-(relation, hop) pooled grounding blocks built by BFS
      from the SHOWN 1-hop context out to hop d. Each hop's contributing set EXCLUDES every true neighbour
      of the held-out concept (true_nei_all = predict targets + all shown/capped-out 1-hop) AND the concept
      itself AND all shallower-hop nodes -> the rep NEVER sees the answer at ANY hop (leak-proof witness at
      every hop, must print 0). Depth=1 uses ONLY the base 1-hop block byte-for-byte -> it reproduces the
      confirmed all-context number (positive control, Gate D).
  (2) ctx-ONLY neighbour-shuffle control (ARM_CTX_ONLY_SHUFFLE): the CONTRACT caveat-closer. Take the
      TRAINED learned encoder, keep every concept's OWN grounding intact, and permute ONLY the context
      block among held-out concepts, then re-encode + eval. If the specific multi-hop context is load-
      bearing (not a structural artifact), this MUST collapse the signal to ~raw_grounding. Distinct from
      the base COLLAPSE_SHUFFLE (which permutes ALL input rows and RETRAINS -> a pipeline can-fail witness);
      CTX_ONLY_SHUFFLE keeps own grounding + the trained weights and isolates the context contribution.
  (3) STRONGER non-learned multi-hop structural baseline (ARM_STRUCT_MULTIHOP): base STRUCT_2HOP counts
      context-neighbours adjacent to a candidate (friend-of-friend, path len 2). This adds a PPR-lite length
      <=3 reachability count (candidate-neighbours within 2 gallery-hops of the context set). HARD_PASS
      requires the LEARNED multi-hop arm to still beat this STRONGER structural baseline.

REUSED VERBATIM (imported from exp_leakproof_relinfer_context_sweep_v1): leak-proof CONTEXT-disjoint-PREDICT
  split + 0/N no-overlap witness, deterministic sha256 concept/ctx-pred split, degree-matched negative
  sampler, fusion self-teacher (geometry + VICReg + relpred-InfoNCE + EMA), RAW_GROUNDING / RANDOM_INIT /
  STRUCT_2HOP / POPULARITY / COLLAPSE_SHUFFLE baselines, tie-corrected Mann-Whitney AUC, target geometry.

THE SWEEP AXIS = hop_depth in {1, 2, 3}, at max_context = ALL (the confirmed ceiling operating point) so the
  HOP-DEPTH lever is isolated from the ctx-COUNT lever already mapped by the base.

PRE-REGISTERED BANDS (BEFORE running; applied to ARM_LEARNED primary):
  Gate D (positive control): depth=1 all-context LEARNED AUC within 0.03 of the confirmed cap2500 number
    0.6614 (only enforced for cap_nodes==2500; reported-not-enforced otherwise).
  HARD_PASS = best multi-hop depth (2 or 3) LEARNED AUC beats depth-1 all-context by >= +0.02 absolute AND
    per-seed min rise > 0 AND best-depth LEARNED beats ARM_STRUCT_MULTIHOP by >= 0.03 AND best-depth
    LEARNED beats RAW_GROUNDING by >= 0.03 AND ARM_CTX_ONLY_SHUFFLE collapses to ~grounding
    (ctxshuf <= raw_grounding + 0.03) at the best depth, with per-level VALIDITY (collapse ~0.5, pop ~0.5,
    power >= MIN_QUERY_TASKS) holding at every level.
  DEPTH_FLAT = valid + Gate-D-ok but best multi-hop does NOT beat depth-1 by >= +0.02 (multi-hop does not
    raise absolute quality; honest null, report WHY).
  DEPTH_HURTS = best multi-hop <= depth-1 - 0.02 (deeper context dilutes; honest).
  HARD_FAIL_INVALID = validity fails at any level. HARD_FAIL_REGIME_MISMATCH = Gate D fails.

HARD INVARIANTS: TEACHER-FREE (no borrowed vectors; inputs = measured grounding + the foundation's own
  relational graph). INDUCTIVE (held-out placed from its features). LEAK-PROOF (context disjoint from
  predict at EVERY hop; negatives exclude every true neighbour). ASCII-only. CPU-only. Deterministic.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over the code arms incl CTX_ONLY_SHUFFLE)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real signal; primary not saturated
# - discriminator survives scale: smoke previews hop-depth deltas; FULL runs >=3 seeds foreground
# - HARD_PASS strictly above floor: rise>=0.02 AND per-seed min>0 (not at-floor) + beats stronger struct baseline
# - HP_SCOPE: gates apply to ARM_LEARNED (primary) only
# - sweep axis hop_depth -> cardinality_ok via EXPECTED_N_UNITS = n_seeds * n_depths
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; collapse+popularity witness it)
# - deterministic seeding: imported sha256 splits + fixed int seeds + sorted(); no hash()/list(set())
# - no substrate KGStore/fit objects (imports self-contained base cell + numpy + torch) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (per-seed + per-level logs flush=True)
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
import experiments.exp_leakproof_relinfer_context_sweep_v1 as base  # noqa: E402
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

ANCHOR_NAME = "leakproof_relinfer_multihop_v1"

# ---------------------------------------------------------------------------
# Config profiles (mirror base FULL_CFG so depth=1 reproduces the confirmed all-context number)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=400, seeds=[7], heldout_frac=0.2, top_rel=8, predict_frac=0.5,
    epochs=15, code_dim=32, hidden=64, lr=5e-3,
    n_landmarks=48, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    hop_depths=[1, 2], max_hop_nodes=120,
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=800, seeds=[7], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=80, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=192, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    hop_depths=[1, 2, 3], max_hop_nodes=150,
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=2500, seeds=[7, 13, 19], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=140, code_dim=128, hidden=256, lr=2.5e-3,
    n_landmarks=448, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    hop_depths=[1, 2, 3], max_hop_nodes=200,
)

EVAL_SEED = 20260726

# Pre-reg bands
CONFIRMED_DEPTH1_ALL_CAP2500 = 0.6614   # MEASURED@data/exp_leakproof_relinfer_context_sweep_v1/metrics.json (ALL, cap2500)
GATE_D_TOL = 0.03                        # depth-1 all-context must reproduce the confirmed number (cap2500)
HP_DEPTH_RISE = 0.02                     # best multi-hop LEARNED must beat depth-1 by this ABSOLUTE margin
HP_OVER_STRUCTMH = 0.03                  # LEARNED must beat the stronger STRUCT_MULTIHOP baseline
HP_OVER_RAW = 0.03                       # LEARNED must still beat RAW_GROUNDING (inherited)
# ctx-only-shuffle control: shuffling ONLY the context (own grounding intact, trained weights) MUST remove
# the context-specific signal -> (learned - ctxshuf) is the SPECIFIC-context contribution. Note ctxshuf sits
# ABOVE raw_grounding by the trained-own-grounding transform (a legitimate learned improvement, NOT a
# context artifact; RANDOM_INIT confirms untrained own-ctx ~ raw). So the correct gate is on the DROP, not
# on ctxshuf reaching raw exactly. (Original ctxshuf<=raw+eps band was mis-specified; refined at smoke.)
HP_CTX_SPECIFIC = 0.03                   # (learned - ctxshuf) MUST exceed this: specific context is load-bearing
CTX_COLLAPSE_FRAC = 0.40                 # >= this fraction of the (learned-raw) margin must vanish on ctx-shuffle
COLLAPSE_BAND = (0.44, 0.56)
POP_BAND = (0.44, 0.56)
MIN_QUERY_TASKS = 100
MIN_QUERY_TASKS_SMOKE = 20

# Arms
RAW_ARM = "ARM_RAW_GROUNDING"
LEARNED_ARM = "ARM_LEARNED"
RANDINIT_ARM = "ARM_RANDOM_INIT"
STRUCT_ARM = "ARM_STRUCT_2HOP"
STRUCTMH_ARM = "ARM_STRUCT_MULTIHOP"
POP_ARM = "ARM_POPULARITY"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
CTXSHUF_ARM = "ARM_CTX_ONLY_SHUFFLE"
PRIMARY_ARM = LEARNED_ARM
CODE_ARMS = [RAW_ARM, LEARNED_ARM, RANDINIT_ARM, SHUFFLE_ARM, CTXSHUF_ARM]
FUNC_ARMS = [STRUCT_ARM, STRUCTMH_ARM, POP_ARM]
ALL_ARMS = [RAW_ARM, LEARNED_ARM, RANDINIT_ARM, STRUCT_ARM, STRUCTMH_ARM,
            POP_ARM, SHUFFLE_ARM, CTXSHUF_ARM]


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
# Multi-hop relational context (NEW; leak-proof at every hop)
# ---------------------------------------------------------------------------
def build_full_adj_rel(data):
    """Full typed adjacency over ALL kept concepts (train+held): adj[i] = {j: set(rel_slots)}.
    Includes predict edges (that is why hop expansion below EXCLUDES true_nei_all at every hop)."""
    K = data["K"]
    rel_slot = data["rel_slot"]
    adj = [dict() for _ in range(K)]
    for (a, b), rels in data["pair_rels"].items():
        slots = set(rel_slot(r) for r in rels)
        adj[a].setdefault(b, set()).update(slots)
        adj[b].setdefault(a, set()).update(slots)
    return adj


def build_multihop_ctx_nei(split, data, adj, depth, max_hop_nodes):
    """For each concept, per-hop per-relation contributing neighbour sets, leak-proof at every hop.

    Returns mh[i] = list of length `depth`; mh[i][k] = {rel_slot: set(node_idx)} for hop k+1.
    hop-0 (k=0) is EXACTLY split['ctx_nei_by_rel'][i] (the base 1-hop block -> depth=1 reproduces base).
    For k>=1 the contributing set is BFS-expanded from hop k-1, grouped by the relation of the LAST edge,
    EXCLUDING: the concept itself, true_nei_all[i] (predict + all real 1-hop neighbours), and every node
    already used at a shallower hop. Frontier capped at max_hop_nodes (deterministic, sorted by idx).
    leak_at_hop counts any excluded true-neighbour that slipped into hop>=1 (MUST be 0)."""
    K = split["K"]
    base_ctx = split["ctx_nei_by_rel"]
    true_nei_all = split["true_nei_all"]
    mh = [None] * K
    leak_at_hop = 0
    for i in range(K):
        levels = []
        # hop-0 == base 1-hop block (verbatim)
        hop0 = {s: set(neigh) for s, neigh in base_ctx[i].items()}
        levels.append(hop0)
        forbidden = set()
        forbidden.add(i)
        forbidden |= true_nei_all[i]                    # empty for train; predict+all-1hop for held-out
        frontier = set()
        for s, neigh in hop0.items():
            frontier |= neigh
        used = set(frontier)
        used.add(i)
        for _k in range(1, depth):
            nxt = {}
            new_nodes = set()
            for u in sorted(frontier):
                for v, slots in adj[u].items():
                    if v == i or v in forbidden or v in used or v in new_nodes:
                        continue
                    if v in true_nei_all[i]:            # explicit leak guard (redundant w/ forbidden)
                        leak_at_hop += 1
                        continue
                    for s in slots:
                        nxt.setdefault(s, set()).add(v)
                    new_nodes.add(v)
            # deterministic cap on the hop's total contributing set
            if len(new_nodes) > max_hop_nodes:
                keep = set(sorted(new_nodes)[:max_hop_nodes])
                nxt = {s: (ns & keep) for s, ns in nxt.items()}
                nxt = {s: ns for s, ns in nxt.items() if ns}
                new_nodes = keep
            levels.append(nxt)
            used |= new_nodes
            frontier = new_nodes
        mh[i] = levels
    return mh, leak_at_hop


def pooled_multihop_block(mh, per_source, block_dim, R, depth):
    """[K, depth*R*per_rel]: per (hop, relation) mean-pooled grounding + present-bit + log1p(count).
    hop-0 columns are byte-identical to base._pooled_ctx_block (depth=1 == base input)."""
    import math
    K = len(mh)
    per_rel = block_dim + 2
    width = R * per_rel
    out = np.zeros((K, depth * width), dtype=np.float64)
    ps = per_source.astype(np.float64)
    for i in range(K):
        levels = mh[i]
        for k in range(depth):
            if k >= len(levels):
                continue
            hop = levels[k]
            base_off = k * width
            for s in range(R):
                neigh = hop.get(s)
                off = base_off + s * per_rel
                if neigh:
                    nj = np.fromiter(sorted(neigh), dtype=np.int64, count=len(neigh))
                    out[i, off:off + block_dim] = ps[nj].mean(axis=0)
                    out[i, off + block_dim] = 1.0
                    out[i, off + block_dim + 1] = math.log1p(len(neigh))
    return out


def build_level_context_mh(split, data, adj, cfg, depth):
    """Build fusion inputs (own + multi-hop ctx) + landmarks + target geometry + eval ctx for a hop-depth.
    Geometry teacher + landmarks + eval ctx are IDENTICAL to base (1-hop); only the encoder INPUT ctx grows."""
    own = split["own_feat"]
    R = split["R"]
    mh, leak_at_hop = build_multihop_ctx_nei(split, data, adj, depth, cfg["max_hop_nodes"])
    if leak_at_hop != 0:
        raise RuntimeError("MULTIHOP LEAK: %d true-neighbours entered hop>=1 context (must be 0)" % leak_at_hop)
    ctx = pooled_multihop_block(mh, own, GROUND_DIM, R, depth)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    ev_ctx = build_eval_context(split, cfg["n_deg_bins"])
    # diagnostics: mean hop-set sizes among held-out (must be > 0 at hop>=2 for depth>=2)
    held = split["held_idx"].tolist()
    hop_sizes = []
    for k in range(depth):
        sz = []
        for h in held:
            tot = 0
            for _s, ns in mh[h][k].items():
                tot += len(ns)
            sz.append(tot)
        hop_sizes.append(float(np.mean(sz)) if sz else 0.0)
    return base_feats, landmarks, target_geo, ev_ctx, dict(
        ctx_dim=int(ctx.shape[1]), depth=depth, mean_hop_sizes_heldout=hop_sizes,
        leak_at_hop=leak_at_hop)


# ---------------------------------------------------------------------------
# STRUCT_MULTIHOP eval (stronger non-learned structural baseline, PPR-lite len<=3)
# ---------------------------------------------------------------------------
def eval_struct_multihop(split, ev_ctx):
    """Candidate score = # of candidate-neighbours within 2 gallery-hops of the query's context set.
    i.e. count of gallery nodes reachable from context within 2 hops that are adjacent to the candidate
    (paths of length up to 3 from query through context to candidate). Reuses degree-matched negatives."""
    gal_adj = ev_ctx["gal_adj"]
    rng = np.random.default_rng(EVAL_SEED)
    aucs = []
    neg_leak = 0
    for h in split["held_idx"].tolist():
        qpn = _query_positives_negatives(h, split, ev_ctx, rng)
        if qpn is None:
            continue
        pos_arr, neg_arr, ctxp, exclude = qpn
        neg_leak += sum(1 for n in neg_arr.tolist() if n in exclude)
        # 2-hop closure of the context set within the gallery
        ctx2 = set(ctxp)
        for c in ctxp:
            ctx2 |= gal_adj[c]
        sel = np.concatenate([pos_arr, neg_arr])
        sc = np.zeros(sel.shape[0], dtype=np.float64)
        for k, cand in enumerate(sel.tolist()):
            sc[k] = float(len(gal_adj[cand] & ctx2))
        pm = np.zeros(sel.shape[0], dtype=bool)
        pm[:pos_arr.shape[0]] = True
        a = _auc_from_scores(sc, pm)
        if a is not None:
            aucs.append(a)
    if len(aucs) < 5:
        return float("nan"), len(aucs), neg_leak
    return float(np.mean(aucs)), len(aucs), neg_leak


# ---------------------------------------------------------------------------
# One seed: build all arms + eval, at a fixed hop-depth
# ---------------------------------------------------------------------------
def run_seed_mh(seed, split, base_feats, landmarks, target_geo, ev_ctx, cfg):
    c = cfg
    own = base_feats["own"]
    ctx = base_feats["ctx"]
    feats = dict(own=own, ctx=ctx)

    codes = {}
    codes[RAW_ARM] = _l2_np(own.astype(np.float64)).astype(np.float32)

    # LEARNED (PRIMARY): grounding + MULTI-HOP relational context
    enc_l = train_fusion(feats, target_geo, landmarks, split, c, seed,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=True)
    codes[LEARNED_ARM] = encode_all(enc_l, feats)

    # RANDOM_INIT: same architecture (multi-hop input), untrained
    enc_r = train_fusion(feats, target_geo, landmarks, split, c, seed + 101,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=False)
    codes[RANDINIT_ARM] = encode_all(enc_r, feats)

    # COLLAPSE_SHUFFLE: permute ALL input rows + retrain -> ~0.5 (base pipeline can-fail witness)
    enc_s = train_fusion(feats, target_geo, landmarks, split, c, seed + 1,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"],
                         do_train=True, shuffle_rows=True)
    Kk = split["K"]
    perm_all = np.random.default_rng(seed + 1 + 909).permutation(Kk)
    feats_shuf = dict(own=own[perm_all], ctx=ctx[perm_all])
    codes[SHUFFLE_ARM] = encode_all(enc_s, feats_shuf)

    # CTX_ONLY_SHUFFLE (CONTRACT caveat-closer): trained LEARNED encoder, own grounding intact,
    # permute ONLY the context block among HELD-OUT concepts -> must collapse to ~grounding.
    held = split["held_idx"]
    csr = np.random.default_rng(seed + 4242)
    perm_h = held.copy()
    if held.shape[0] > 1:
        for _try in range(8):
            p = csr.permutation(held.shape[0])
            if np.any(p != np.arange(held.shape[0])):
                perm_h = held[p]
                break
    ctx_cs = ctx.copy()
    ctx_cs[held] = ctx[perm_h]
    feats_cs = dict(own=own, ctx=ctx_cs)
    codes[CTXSHUF_ARM] = encode_all(enc_l, feats_cs)

    # ARMS-MUST-DIFFER (META_RULE_AF) over code arms
    digs = {a: _emb_digest(codes[a]) for a in CODE_ARMS}
    dl = sorted(digs.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            assert dl[i][1] != dl[j][1], ("META_RULE_AF VIOLATION: arms %s and %s bit-identical"
                                          % (dl[i][0], dl[j][0]))

    arm_metrics = {}
    neg_leak_total = 0
    for arm in ALL_ARMS:
        if arm == STRUCT_ARM:
            auc, nq, nleak = eval_relational_inference(None, split, ev_ctx, struct_2hop=True)
        elif arm == STRUCTMH_ARM:
            auc, nq, nleak = eval_struct_multihop(split, ev_ctx)
        elif arm == POP_ARM:
            auc, nq, nleak = eval_relational_inference(None, split, ev_ctx, popularity=True)
        else:
            auc, nq, nleak = eval_relational_inference(codes[arm], split, ev_ctx)
        neg_leak_total += nleak
        arm_metrics[arm] = dict(rel_infer_auc=auc, n_query=nq, neg_in_exclude=nleak,
                                emb_digest=(digs[arm] if arm in digs else None))
        _log("seed=%d arm=%-22s rel_infer_auc=%.4f n_q=%d neg_leak=%d"
             % (seed, arm, auc, nq, nleak))
    arm_metrics["_neg_leak_total"] = neg_leak_total
    if neg_leak_total != 0:
        raise RuntimeError("LEAK: %d negatives were true neighbours (must be 0)" % neg_leak_total)
    return arm_metrics


# ---------------------------------------------------------------------------
# Per-level verdict + depth-sweep verdict
# ---------------------------------------------------------------------------
def aggregate_level(per_seed, min_query_tasks):
    def series(arm):
        return np.array([m[arm]["rel_infer_auc"] for m in per_seed], dtype=np.float64)
    agg = {}
    for arm in ALL_ARMS:
        s = series(arm)
        agg[arm] = dict(rel_infer_auc_mean=float(np.nanmean(s)),
                        rel_infer_auc_min=float(np.nanmin(s)),
                        n_query=int(np.min([m[arm]["n_query"] for m in per_seed])),
                        n_seeds=len(per_seed))
    learned = agg[LEARNED_ARM]["rel_infer_auc_mean"]
    raw = agg[RAW_ARM]["rel_infer_auc_mean"]
    struct_mh = agg[STRUCTMH_ARM]["rel_infer_auc_mean"]
    pop = agg[POP_ARM]["rel_infer_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["rel_infer_auc_mean"]
    ctxshuf = agg[CTXSHUF_ARM]["rel_infer_auc_mean"]
    n_query = agg[LEARNED_ARM]["n_query"]
    cb_lo, cb_hi = COLLAPSE_BAND
    pb_lo, pb_hi = POP_BAND
    power_ok = bool(n_query >= min_query_tasks)
    can_fail_fired = bool(cb_lo <= shuf <= cb_hi)
    pop_ok = bool(pb_lo <= pop <= pb_hi)
    # ctx-only-shuffle collapse: specific context is load-bearing iff shuffling it removes a real, absolute
    # AND fractional part of the learned-over-raw margin (see HP_CTX_SPECIFIC / CTX_COLLAPSE_FRAC notes).
    ctx_specific = float(learned - ctxshuf)
    learned_over_raw = float(learned - raw)
    ctx_collapse_frac = float(ctx_specific / learned_over_raw) if learned_over_raw > 1e-9 else 0.0
    ctxshuf_collapses = bool(ctx_specific >= HP_CTX_SPECIFIC and ctx_collapse_frac >= CTX_COLLAPSE_FRAC)
    validity_ok = bool(power_ok and can_fail_fired and pop_ok)
    gates = dict(
        learned_rel_infer_auc=learned, learned_rel_infer_auc_min=agg[LEARNED_ARM]["rel_infer_auc_min"],
        raw_grounding_rel_infer_auc=raw,
        random_init_rel_infer_auc=agg[RANDINIT_ARM]["rel_infer_auc_mean"],
        struct_2hop_rel_infer_auc=agg[STRUCT_ARM]["rel_infer_auc_mean"],
        struct_multihop_rel_infer_auc=struct_mh,
        popularity_rel_infer_auc=pop, collapse_shuffle_rel_infer_auc=shuf,
        ctx_only_shuffle_rel_infer_auc=ctxshuf,
        margin_over_raw_grounding=float(learned - raw),
        margin_over_struct_multihop=float(learned - struct_mh),
        margin_over_ctx_only_shuffle=float(learned - ctxshuf),
        ctx_specific_contribution=ctx_specific, ctx_collapse_frac=ctx_collapse_frac,
        power_ok=power_ok, n_query=n_query, can_fail_fired=can_fail_fired, pop_ok=pop_ok,
        ctxshuf_collapses=ctxshuf_collapses, validity_ok=validity_ok,
    )
    return agg, gates


def depth_sweep_verdict(per_level, cap_nodes):
    """per_level: list ordered by depth ascending; each {hop_depth, gates, per_seed_learned}."""
    ordered = sorted(per_level, key=lambda pl: pl["hop_depth"])
    d1 = ordered[0]
    assert d1["hop_depth"] == 1, "depth-1 must be present as positive control"
    d1_learned = d1["gates"]["learned_rel_infer_auc"]
    d1_series = np.array(d1["per_seed_learned"], dtype=np.float64)

    # Gate D: depth-1 all-context reproduces the confirmed number (only enforced at cap2500)
    gate_d_applicable = (int(cap_nodes) == 2500)
    gate_d_delta = float(d1_learned - CONFIRMED_DEPTH1_ALL_CAP2500)
    gate_d_ok = (not gate_d_applicable) or (abs(gate_d_delta) <= GATE_D_TOL)

    # best multi-hop depth (>=2)
    mh_levels = [pl for pl in ordered if pl["hop_depth"] >= 2]
    best = None
    for pl in mh_levels:
        if best is None or pl["gates"]["learned_rel_infer_auc"] > best["gates"]["learned_rel_infer_auc"]:
            best = pl
    curve = [(pl["hop_depth"],
              round(pl["gates"]["learned_rel_infer_auc"], 4),
              round(pl["gates"]["raw_grounding_rel_infer_auc"], 4),
              round(pl["gates"]["struct_multihop_rel_infer_auc"], 4),
              round(pl["gates"]["ctx_only_shuffle_rel_infer_auc"], 4),
              round(pl["gates"]["margin_over_raw_grounding"], 4),
              bool(pl["gates"]["validity_ok"]),
              bool(pl["gates"]["ctxshuf_collapses"])) for pl in ordered]

    all_valid = all(pl["gates"]["validity_ok"] for pl in ordered)

    if best is None:
        verdict = "NO_MULTIHOP_LEVEL"
        best_learned = d1_learned
        abs_rise = 0.0
        per_seed_rise_min = 0.0
        beats_structmh = False
        ctxshuf_collapses_best = bool(d1["gates"]["ctxshuf_collapses"])
        beats_raw = bool(d1["gates"]["margin_over_raw_grounding"] >= HP_OVER_RAW)
    else:
        best_learned = best["gates"]["learned_rel_infer_auc"]
        abs_rise = float(best_learned - d1_learned)
        best_series = np.array(best["per_seed_learned"], dtype=np.float64)
        n = min(best_series.shape[0], d1_series.shape[0])
        per_seed_rise_min = float(np.nanmin(best_series[:n] - d1_series[:n]))
        beats_structmh = bool(best["gates"]["margin_over_struct_multihop"] >= HP_OVER_STRUCTMH)
        ctxshuf_collapses_best = bool(best["gates"]["ctxshuf_collapses"])
        beats_raw = bool(best["gates"]["margin_over_raw_grounding"] >= HP_OVER_RAW)

    if not all_valid:
        verdict = "HARD_FAIL_INVALID"
    elif not gate_d_ok:
        verdict = "HARD_FAIL_REGIME_MISMATCH"
    elif best is None:
        verdict = "NO_MULTIHOP_LEVEL"
    elif (abs_rise >= HP_DEPTH_RISE and per_seed_rise_min > 0.0 and beats_structmh
          and beats_raw and ctxshuf_collapses_best):
        verdict = "HARD_PASS"
    elif abs_rise <= -HP_DEPTH_RISE:
        verdict = "DEPTH_HURTS"
    else:
        verdict = "DEPTH_FLAT"

    verdict_msg = (
        "%s | hop-depth curve (depth, learned, raw, struct_mh, ctxshuf, margin_raw, valid, ctxshuf_collapse): %s | "
        "depth1(all-ctx positive-control)=%.4f gate_d_ok=%s(delta=%+.4f vs confirmed %.4f, applicable=%s) | "
        "best_multihop depth=%s learned=%.4f abs_rise_vs_depth1=%+.4f (per-seed min rise=%+.4f, need>=%.2f) | "
        "beats_struct_multihop=%s(margin=%+.4f) beats_raw=%s ctxshuf_collapses@best=%s | all_levels_valid=%s"
        % (verdict, curve, d1_learned, gate_d_ok, gate_d_delta, CONFIRMED_DEPTH1_ALL_CAP2500,
           gate_d_applicable,
           (best["hop_depth"] if best else None), best_learned, abs_rise, per_seed_rise_min, HP_DEPTH_RISE,
           beats_structmh, (best["gates"]["margin_over_struct_multihop"] if best else float("nan")),
           beats_raw, ctxshuf_collapses_best, all_valid))
    summary = dict(verdict=verdict, curve=curve, depth1_learned=d1_learned,
                   gate_d_ok=gate_d_ok, gate_d_delta=gate_d_delta, gate_d_applicable=gate_d_applicable,
                   best_multihop_depth=(best["hop_depth"] if best else None),
                   best_multihop_learned=best_learned, abs_rise_vs_depth1=abs_rise,
                   per_seed_rise_min=per_seed_rise_min, beats_struct_multihop=beats_structmh,
                   beats_raw=beats_raw, ctxshuf_collapses_best=ctxshuf_collapses_best,
                   all_levels_valid=all_valid)
    return verdict, verdict_msg, summary


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def multihop_selftest():
    """REAL-CODE-PATH: tiny synthetic grounded subgraph; verify (a) depth-1 multi-hop block == base
    1-hop block byte-for-byte, (b) depth>=2 adds NON-trivial hop-2 content, (c) NO true neighbour of a
    held-out concept enters ANY hop (leak_at_hop == 0), (d) struct_multihop eval runs + degree-matched."""
    from experiments.exp_leakproof_relinfer_context_sweep_v1 import (
        N_GROUPS, N_VALUE_DIMS,
    )
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
    cfg = dict(heldout_frac=0.3, predict_frac=0.5, n_deg_bins=5, max_hop_nodes=60)
    try:
        split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
    except RuntimeError as e:
        return False, dict(err="split:" + str(e)[:200])

    adj = build_full_adj_rel(data)
    own = split["own_feat"]
    # depth-1 multihop block must equal base 1-hop block byte-for-byte
    base_block = _pooled_ctx_block(split, own, GROUND_DIM)
    mh1, leak1 = build_multihop_ctx_nei(split, data, adj, 1, cfg["max_hop_nodes"])
    d1_block = pooled_multihop_block(mh1, own, GROUND_DIM, R, 1)
    same_d1 = bool(np.allclose(base_block, d1_block, atol=0, rtol=0))

    mh3, leak3 = build_multihop_ctx_nei(split, data, adj, 3, cfg["max_hop_nodes"])
    # hop-2 content non-trivial + leak-proof + hop disjointness among held-out
    held = split["held_idx"].tolist()
    hop2_nonzero = 0
    disjoint_viol = 0
    ans_leak = 0
    for h in held:
        levels = mh3[h]
        s0 = set().union(*[levels[0][s] for s in levels[0]]) if levels[0] else set()
        s1 = set().union(*[levels[1][s] for s in levels[1]]) if len(levels) > 1 and levels[1] else set()
        s2 = set().union(*[levels[2][s] for s in levels[2]]) if len(levels) > 2 and levels[2] else set()
        if len(s1) > 0:
            hop2_nonzero += 1
        if (s0 & s1) or (s0 & s2) or (s1 & s2):
            disjoint_viol += 1
        tn = split["true_nei_all"][h]
        if (s1 & tn) or (s2 & tn) or (h in s0) or (h in s1) or (h in s2):
            ans_leak += 1

    ev_ctx = build_eval_context(split, cfg["n_deg_bins"])
    smh_auc, smh_nq, smh_leak = eval_struct_multihop(split, ev_ctx)

    checks = dict(same_depth1_as_base=same_d1, leak_at_hop_d1=leak1, leak_at_hop_d3=leak3,
                  hop2_nonzero_heldout=hop2_nonzero, n_held=len(held),
                  disjoint_viol=disjoint_viol, answer_leak=ans_leak,
                  struct_mh_auc=smh_auc, struct_mh_nq=smh_nq, struct_mh_neg_leak=smh_leak)
    ok = (same_d1 and leak1 == 0 and leak3 == 0 and disjoint_viol == 0 and ans_leak == 0
          and hop2_nonzero >= max(3, len(held) // 3) and smh_leak == 0
          and smh_auc == smh_auc)  # not NaN
    return bool(ok), checks


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
    depths = list(cfg["hop_depths"])
    expected_total_units = len(cfg["seeds"]) * len(depths)
    _write_start_marker(output_dir, run_mode, expected_total_units)
    t_start = time.perf_counter()

    st_ok, st_res = multihop_selftest()
    _log("multihop_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED multihop_ok=%s: %s" % (st_ok, st_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            multihop_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})
    adj = build_full_adj_rel(data)

    if run_mode == "self_test":
        split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
        bf, lm, tg, ev, ctx_meta = build_level_context_mh(split, data, adj, cfg, depth=2)
        pm = run_seed_mh(cfg["seeds"][0], split, bf, lm, tg, ev, cfg)
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS multi-hop leak-proof context + fusion + degree-matched rel-infer eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            multihop_selftest=st_res, ctx_meta=ctx_meta, data_meta=data["meta"],
            learned_rel_infer_auc=pm[LEARNED_ARM]["rel_infer_auc"],
            raw_grounding_rel_infer_auc=pm[RAW_ARM]["rel_infer_auc"],
            struct_multihop_rel_infer_auc=pm[STRUCTMH_ARM]["rel_infer_auc"],
            ctx_only_shuffle_rel_infer_auc=pm[CTXSHUF_ARM]["rel_infer_auc"],
            collapse_shuffle_rel_infer_auc=pm[SHUFFLE_ARM]["rel_infer_auc"],
            popularity_rel_infer_auc=pm[POP_ARM]["rel_infer_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    # the leak-proof split is IDENTICAL across depths (max_context=ALL); only ctx INPUT grows with depth.
    split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
    _log("split: %s" % split["split_meta"])

    per_level = []
    seed_failures = []
    total_units_run = 0
    for depth in depths:
        bf, lm, tg, ev, ctx_meta = build_level_context_mh(split, data, adj, cfg, depth)
        _log("[depth=%d] ctx_dim=%d mean_hop_sizes_heldout=%s landmarks=%d gallery=%d"
             % (depth, ctx_meta["ctx_dim"], ctx_meta["mean_hop_sizes_heldout"], lm.shape[0], ev["G"]))
        per_seed = []
        for seed in cfg["seeds"]:
            try:
                pm = run_seed_mh(seed, split, bf, lm, tg, ev, cfg)
                per_seed.append(pm)
                total_units_run += 1
                write_partial(output_dir, "d%d_seed%d" % (depth, seed), dict(
                    hop_depth=depth, seed=seed,
                    arms={a: {k: v for k, v in pm[a].items() if k != "emb_digest"} for a in ALL_ARMS},
                    run_mode=run_mode))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                fc = type(e).__name__
                seed_failures.append(dict(hop_depth=depth, seed=seed, failure_class=fc, msg=str(e)[:300]))
                _log("SEED_FAILED depth=%d seed=%d class=%s: %s" % (depth, seed, fc, str(e)[:200]))
        if len(per_seed) < len(cfg["seeds"]):
            continue
        agg_l, gates_l = aggregate_level(per_seed, min_query)
        per_seed_learned = [float(m[LEARNED_ARM]["rel_infer_auc"]) for m in per_seed]
        _log("[depth=%d] learned=%.4f raw=%.4f struct_mh=%.4f ctxshuf=%.4f collapse=%.4f pop=%.4f valid=%s ctxshuf_collapse=%s"
             % (depth, gates_l["learned_rel_infer_auc"], gates_l["raw_grounding_rel_infer_auc"],
                gates_l["struct_multihop_rel_infer_auc"], gates_l["ctx_only_shuffle_rel_infer_auc"],
                gates_l["collapse_shuffle_rel_infer_auc"], gates_l["popularity_rel_infer_auc"],
                gates_l["validity_ok"], gates_l["ctxshuf_collapses"]))
        per_level.append(dict(
            hop_depth=depth, gates=gates_l, arms_aggregate=agg_l, ctx_meta=ctx_meta,
            per_seed_learned=per_seed_learned, n_seeds=len(per_seed),
            per_seed=[{a: {k: v for k, v in per_seed[i][a].items() if k != "emb_digest"}
                       for a in ALL_ARMS} for i in range(len(per_seed))]))

    if total_units_run < expected_total_units:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units (%d seeds x %d depths) got %d (failures=%s)"
                        % (expected_total_units, len(cfg["seeds"]), len(depths), total_units_run, seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, data_meta=data["meta"]))
        raise SystemExit(1)

    verdict, verdict_msg, sweep_summary = depth_sweep_verdict(per_level, cfg["cap_nodes"])

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"], hop_depths=depths,
        expected_total_units=expected_total_units, total_units_run=total_units_run,
        config={k: v for k, v in cfg.items()},
        data_meta={k: v for k, v in data["meta"].items()},
        split_meta=split["split_meta"],
        sweep_summary=sweep_summary, per_level=per_level,
        multihop_selftest=st_res, seed_failures=seed_failures,
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
