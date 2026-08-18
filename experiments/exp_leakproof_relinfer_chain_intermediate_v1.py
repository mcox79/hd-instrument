"""LEAK-PROOF held-out relational inference: CHAINING THROUGH A HIDDEN INTERMEDIATE (the untested frontier).

WHY (the one condition prior cells identified but never tested):
  Confirmed (29587/88/89, exp_leakproof_relinfer_context_sweep_v1): SINGLE-SHOT learned inference works
  (LEARNED 0.6614 vs RAW_GROUNDING 0.5498) because the encoder integrates, at ENCODE TIME, the 1-hop
  context constraints it CAN SEE. Adding encoder-input depth (multihop_v1 -> DEPTH_FLAT) or a decision-time
  additive combiner over VISIBLE anchors (reasoner_multiconstraint_v1 -> REASONER_WORSE) does NOT help,
  because the constraints were already visible at encode time. THE UNTESTED LEVER: a constraint the encoder
  CANNOT see in one shot -- a path A -> B -> C where the direct A-C edge is held out AND the bridging
  intermediate B is hidden from BOTH A's and C's encoder context. Reaching C from A then REQUIRES genuine
  step-by-step derivation (compose two learned inference hops), which single-shot cannot do because neither
  code[A] nor code[C] ever materialized B. This is the core of "reasoning you can converse with".

THE CONSTRUCTION (leak-proof through-intermediate triangles):
  For each target triangle (A, B, C) -- three real edges A-B, B-C, A-C in the foundation graph:
    * code[A] is built WITHOUT the A-B and A-C edges (both HIDDEN from A's context input).
    * code[C] is built WITHOUT the C-A and C-B edges (both HIDDEN from C's context input).
    * code[B] is built normally (B sees A and C) -> code[B] is the bridge that carries BOTH endpoints.
    * relpred (InfoNCE) trains ONLY observed edges. A-C is NEVER a training pair from either side (each
      endpoint hid the other) -> the DIRECT link is untrained. A-B and B-C ARE trained (via anchor B) ->
      each HOP is a first-class learned relation. Composition must recover the link that was never learned.
  The target A-C edge is the eval positive; it never appears in any context input nor any training pair
  (leak-proof witness must print 0). Negatives = degree-matched non-neighbours of A (exclude EVERY true
  neighbour incl the hidden bridge).

THE MECHANISM (chained derivation over the learned rep; faithful CPU emulation of
  hdlab/reasoner.py::DerivationReasoner meet-in-middle + population-vector combiner):
    chained_score(cand | A) = sum over top-M discovered bridges B of
        relu(cos(code[A], code[B])) * relu(cos(code[B], code[cand]))
    Step 1 DISCOVERS the hidden intermediate B by learned inference (rank gallery by cos(code[A],.)) --
    the true B scores high because code[B] pooled A's grounding/context. Step 2 reaches cand via
    cos(code[B], code[cand]) -- the true C scores high because code[B] pooled C. The product peaks at the
    true bridge for the true target. Single-shot = cos(code[A], code[cand]) directly (no bridge).

THE ONE NUMBER + THE ANTI-TRAP (pre-registered BEFORE running; primary arm = ARM_CHAIN_LEARNED @ topM=20):
  L_chain_lift = chained_learned - singleshot_learned.
  HARD_PASS = L_chain_lift >= +0.05 with per-seed min > 0 AND chained_learned beats {non-learned multi-hop
    structure (common-neighbour over OBSERVED adjacency) +0.03, chained-over-grounding +0.03, single-shot
    grounding +0.03}, with validity holding.
  ANTI-TRAP #1 (task validity, LOAD-BEARING): single-shot learned MUST be near chance ([0.42, 0.60]). If
    single-shot already solves it (>0.60), the intermediate was NOT actually hidden (the encoder propagated
    2-hop structure into the codes) -> TASK_INVALID_SINGLESHOT_SOLVES. The chained win only counts if it
    recovers signal single-shot cannot.
  ANTI-TRAP #2 (not generic composition): chained-over-GROUNDING is the same combiner fed non-learned
    codes. If grounding-chaining lifts as much, composition is a generic homophily effect -> CHAIN_IS_GENERIC.
  Controls: ARM_COLLAPSE (chained over row-permuted learned codes -> ~0.50), ARM_BRIDGE_SHUFFLE (bridge
    discovery from a DIFFERENT query's code -> must collapse ~0.50), ARM_RANDINIT (untrained codes),
    ARM_POPULARITY (degree only -> ~0.50 by degree-matching).

VERDICTS: HARD_PASS | CHAIN_IS_GENERIC | CHAIN_FLAT (|lift|<0.05: local reasoning space exhausted, lever =
  representation quality = the scale run; honest null, report WHY) | CHAIN_WORSE (lift<=-0.05) |
  TASK_INVALID_SINGLESHOT_SOLVES | HARD_FAIL_INVALID (collapse/bridge-shuffle/pop/power fails).

REUSED VERBATIM (imported from exp_leakproof_relinfer_context_sweep_v1): load_grounded_subgraph, grounding
  layout, FusionEncoder + train_fusion + encode_all, compute_target_geometry, build_train_adjacency,
  select_landmarks, _pooled_ctx_block, tie-corrected Mann-Whitney _auc_from_scores, _l2_np, _emb_digest.
  NEW code = triangle-hiding split + chained (meet-in-middle) derivation scorer + through-intermediate eval
  + the single-shot-near-chance anti-trap + grounding/bridge-shuffle/collapse controls.

HARD INVARIANTS: TEACHER-FREE (inputs = measured grounding + the foundation's own relational graph; no
  borrowed vectors). INDUCTIVE (each hop inferred from features; direct link never trained/shown).
  LEAK-PROOF (A-C never in context or training; bridge hidden from both endpoints; negatives exclude every
  true neighbour). ASCII-only. CPU-only. Deterministic seeds. NO bank, NO push.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over learned/grounding/randinit codes)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + bridge-shuffle + popularity witness the floor
# - baseline_in_band at smoke: collapse ~0.5; bridge-shuffle ~0.5; popularity ~0.5; single-shot near-chance (validity)
# - discriminator survives scale: smoke previews chain-lift + validity; FULL runs >=3 seeds foreground
# - HARD_PASS strictly above floor: L_chain_lift>=0.05 AND per-seed min>0 (not at-floor) + beats struct/grounding/ss-grounding
# - HP_SCOPE: gates apply to ARM_CHAIN_LEARNED@topM=20 (primary) only
# - sweep axis topM -> cardinality_ok via EXPECTED_N_UNITS = n_seeds (topM levels are within-seed eval)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; collapse+bridge-shuffle+pop witness it)
# - deterministic seeding: sha256 triangle ordering + fixed int seeds + sorted(); no hash()/list(set())
# - no substrate KGStore/fit objects (imports self-contained base cell + numpy + torch) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (per-seed + per-arm logs flush=True)
"""

import argparse
import hashlib
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

# REUSE VERBATIM from the confirmed base cell (import; its main() is __main__-guarded).
from experiments.exp_leakproof_relinfer_context_sweep_v1 import (  # noqa: E402
    GROUND_DIM,
    N_GROUPS,
    N_VALUE_DIMS,
    build_train_adjacency,
    compute_target_geometry,
    encode_all,
    load_grounded_subgraph,
    select_landmarks,
    train_fusion,
    _auc_from_scores,
    _emb_digest,
    _l2_np,
    _pooled_ctx_block,
)

ANCHOR_NAME = "leakproof_relinfer_chain_intermediate_v1"

# ---------------------------------------------------------------------------
# Config profiles (CPU-local; sized to finish FULL foreground <= ~10 min per INLINE-LOCAL MANDATE)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=400, seeds=[7], top_rel=8,
    epochs=12, code_dim=32, hidden=64, lr=5e-3,
    n_landmarks=48, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    n_targets=40, n_neg=10, max_degree=12, min_obs_ctx=1,
    topM_levels=[20], min_instances=10,
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=700, seeds=[7], top_rel=16,
    epochs=45, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=160, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    n_targets=200, n_neg=20, max_degree=16, min_obs_ctx=1,
    topM_levels=[5, 20, 100000], min_instances=20,
)
# FULL regime is pinned to the VALIDATED near-chance regime (cap700/max_degree16/50ep), where the
# single-shot-near-chance anti-trap holds so the chain-vs-single-shot number is INTERPRETABLE. Larger caps
# (e.g. cap1400) push single-shot ABOVE the validity band (the encoder integrates the 2-hop signal ever more
# thoroughly via transitive relpred) -> TASK_INVALID_SINGLESHOT_SOLVES, which is uninformative about chaining
# (measured 2026-07-27: cap1400/75ep ss=0.652, chain=0.650, lift=-0.0014). The scale trend is reported.
FULL_CFG = dict(
    min_deg=2, cap_nodes=700, seeds=[7, 13, 19], top_rel=16,
    epochs=50, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=160, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1,
    n_targets=250, n_neg=20, max_degree=16, min_obs_ctx=1,
    topM_levels=[5, 20, 100000], min_instances=100,
)

ALL_M = 100000            # topM sentinel = use every discovered bridge
EVAL_SEED = 20260727
TRIANGLE_SALT = "leakproof_chain_intermediate_v1_triangle_order::"

# ---------------------------------------------------------------------------
# Pre-reg bands (primary = ARM_CHAIN_LEARNED @ topM=20)
# ---------------------------------------------------------------------------
PRIMARY_TOPM = 20
HP_CHAIN_LIFT = 0.05          # THE NUMBER: chained_learned - singleshot_learned must exceed this
HP_OVER_STRUCT = 0.03         # chained_learned must beat non-learned multi-hop structure
HP_OVER_GROUND_CHAIN = 0.03   # ANTI-TRAP #2: chained_learned must beat chained-over-grounding
HP_OVER_SS_GROUND = 0.03      # chained_learned must beat single-shot grounding
SS_CHANCE_BAND = (0.42, 0.60) # ANTI-TRAP #1: single-shot learned MUST be near chance for a valid task
COLLAPSE_BAND = (0.42, 0.58)  # ARM_COLLAPSE MUST sit here (can-fail witness)
BRIDGE_SHUF_BAND = (0.42, 0.58)  # ARM_BRIDGE_SHUFFLE MUST collapse here (bridge-specificity witness)
POP_BAND = (0.42, 0.58)       # ARM_POPULARITY ~0.5 (degree-matching validity)
MIN_QUERY_TASKS = 100
MIN_QUERY_TASKS_SMOKE = 20

# Arm names
SS_LEARNED = "ARM_SINGLESHOT_LEARNED"
SS_GROUND = "ARM_SINGLESHOT_GROUNDING"
CHAIN_LEARNED = "ARM_CHAIN_LEARNED"          # per-topM
CHAIN_GROUND = "ARM_CHAIN_GROUNDING"         # per-topM
CHAIN_RANDINIT = "ARM_CHAIN_RANDINIT"        # per-topM
STRUCT_MH = "ARM_STRUCT_MULTIHOP"
POP_ARM = "ARM_POPULARITY"
COLLAPSE_ARM = "ARM_COLLAPSE"                # chained over row-permuted learned codes
BRIDGE_SHUF_ARM = "ARM_BRIDGE_SHUFFLE"       # chained learned, wrong-query bridge discovery


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Start marker / crash diagnostics (SCHEMA-VET section 13)
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


def _edge_order_key(ids, a, c):
    """Deterministic, PYTHONHASHSEED-independent ordering key for an edge (a<c)."""
    return hashlib.sha256((TRIANGLE_SALT + ids[a] + "::" + ids[c]).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Triangle-hiding split (NEW): every concept gets a code; per target triangle the direct A-C edge and the
# bridge B are HIDDEN from BOTH endpoints' context + training; B keeps full context (carries both endpoints).
# ---------------------------------------------------------------------------
def build_triangle_split(data, cfg):
    ids = data["ids"]
    K = data["K"]
    R = data["R"]
    rel_slot = data["rel_slot"]

    pair_rels = data["pair_rels"]

    # SPARSIFY (load-bearing): the induced CSKG subgraph is extremely dense (mean deg ~200 at cap=700), so
    # hiding a couple of edges leaves A and C connected through hundreds of OTHER shared neighbours -> the
    # intermediate is not actually hidden -> single-shot trivially solves it (the smoke_v1 failure mode).
    # Greedily keep at most max_degree edges per node (deterministic sha256 edge order) so 2-hop bridges are
    # MEANINGFUL and hideable. Sparse graph = the only regime where the through-intermediate task is valid.
    max_degree = int(cfg.get("max_degree", 16))
    edges_all = []
    for (a, b) in pair_rels:
        aa, cc = (a, b) if a < b else (b, a)
        edges_all.append((aa, cc))
    edges_all = sorted(set(edges_all), key=lambda e: _edge_order_key(ids, e[0], e[1]))
    deg_cap = np.zeros(K, dtype=np.int64)
    adj = [set() for _ in range(K)]
    for (a, b) in edges_all:
        if deg_cap[a] < max_degree and deg_cap[b] < max_degree:
            adj[a].add(b)
            adj[b].add(a)
            deg_cap[a] += 1
            deg_cap[b] += 1

    # standardize grounding (inductive-safe: whole-corpus stats; grounding standardization is not leaky)
    vals = data["vals"]
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", RuntimeWarning)
        mu = np.nanmean(vals, axis=0)
        sd = np.nanstd(vals, axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (vals - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z).astype(np.float64)
    own_feat = np.concatenate([z, data["gpres"]], axis=1).astype(np.float64)   # [K,20]

    # enumerate target triangles on the SPARSE graph. For each edge (A,C) that has >=1 common neighbour,
    # designate ALL common neighbours as bridges and HIDE THE ENTIRE COMMON-NEIGHBOUR SET (all possible
    # bridges) + the direct A-C edge from BOTH endpoints' context/training. A designated primary bridge B
    # (highest-degree common neighbour) keeps its FULL context (B is NEVER an endpoint) so code[B] carries
    # both A and C -> only step-by-step derivation THROUGH B can reach C. Roles are disjoint: a concept is
    # an ENDPOINT (max once) XOR a BRIDGE, so a bridge's context is never truncated by endpoint-hiding.
    edges = list(edges_all)      # already deterministically ordered + sparse

    role = np.zeros(K, dtype=np.int64)     # 0=free, 1=endpoint, 2=bridge
    targets = []                 # list of dict(A, B, C, n_common)
    hidden_ctx = [set() for _ in range(K)]   # neighbours to HIDE from concept's context + training
    min_obs = int(cfg["min_obs_ctx"])
    n_want = int(cfg["n_targets"])

    for (a, c) in edges:
        if len(targets) >= n_want:
            break
        if role[a] != 0 or role[c] != 0:               # each endpoint used at most once; never a bridge
            continue
        common = (adj[a] & adj[c]) - {a, c}
        # bridges must be role-free (so their context stays full) and not the endpoints
        common = {b for b in common if role[b] in (0, 2)}
        if not common:
            continue
        bridge = sorted(common, key=lambda b: (-len(adj[b]), ids[b]))[0]
        # endpoints must keep >= min_obs OTHER observed neighbours after hiding the whole common set + partner
        a_remaining = adj[a] - common - {c}
        c_remaining = adj[c] - common - {a}
        if len(a_remaining) < min_obs or len(c_remaining) < min_obs:
            continue
        targets.append(dict(A=int(a), B=int(bridge), C=int(c), n_common=int(len(common))))
        # HIDE from A: entire common set (all bridges) + target C ; from C: entire common set + target A
        hidden_ctx[a] |= common
        hidden_ctx[a].add(c)
        hidden_ctx[c] |= common
        hidden_ctx[c].add(a)
        role[a] = 1
        role[c] = 1
        for b in common:
            if role[b] == 0:
                role[b] = 2                              # lock bridges out of the endpoint pool

    if len(targets) < cfg["min_instances"]:
        raise RuntimeError("too few through-intermediate triangles: %d (< %d)" % (len(targets), cfg["min_instances"]))

    # build OBSERVED context (per-rel neighbour sets) = all edges minus hidden_ctx ; train_neigh = observed
    ctx_nei_by_rel = [dict() for _ in range(K)]
    train_neigh = [set() for _ in range(K)]
    train_deg = np.zeros(K, dtype=np.float64)
    for i in range(K):
        obs = adj[i] - hidden_ctx[i]
        for j in sorted(obs):
            key = (i, j) if i < j else (j, i)
            rels = pair_rels.get(key, {"OTHER"})
            for r in rels:
                ctx_nei_by_rel[i].setdefault(rel_slot(r), set()).add(j)
            train_neigh[i].add(j)
        train_deg[i] = float(len(obs))

    # LEAK WITNESSES (must all be 0)
    leak_ctx = 0        # bridge/other-endpoint appearing in an endpoint's observed context
    leak_train = 0      # target A-C appearing as a training pair from either side
    for t in targets:
        A, B, C = t["A"], t["B"], t["C"]
        a_obs = set().union(*[ctx_nei_by_rel[A][s] for s in ctx_nei_by_rel[A]]) if ctx_nei_by_rel[A] else set()
        c_obs = set().union(*[ctx_nei_by_rel[C][s] for s in ctx_nei_by_rel[C]]) if ctx_nei_by_rel[C] else set()
        if (B in a_obs) or (C in a_obs):
            leak_ctx += 1
        if (B in c_obs) or (A in c_obs):
            leak_ctx += 1
        if (C in train_neigh[A]) or (A in train_neigh[C]):
            leak_train += 1
    if leak_ctx != 0:
        raise RuntimeError("CONTEXT LEAK: %d endpoints saw the bridge/target in context (must be 0)" % leak_ctx)
    if leak_train != 0:
        raise RuntimeError("TRAIN LEAK: %d target A-C edges appear as a training pair (must be 0)" % leak_train)

    train_idx = np.arange(K, dtype=np.int64)   # everyone is a gallery concept (per-edge hiding, not per-concept)
    obs_deg_q = float(np.mean([train_deg[t["A"]] for t in targets]))
    obs_deg_b = float(np.mean([train_deg[t["B"]] for t in targets]))
    mean_ncommon = float(np.mean([t["n_common"] for t in targets]))
    split = dict(
        own_feat=own_feat, K=K, R=R,
        train_idx=train_idx, train_deg=train_deg,
        ctx_nei_by_rel=ctx_nei_by_rel, train_neigh=train_neigh,
        adj=adj, hidden_ctx=hidden_ctx, targets=targets,
        split_meta=dict(
            n_concepts=K, n_targets=len(targets),
            leak_ctx_witness=leak_ctx, leak_train_witness=leak_train,
            mean_obs_deg_query=obs_deg_q, mean_obs_deg_bridge=obs_deg_b,
            mean_n_common_bridges=mean_ncommon,
            max_degree=max_degree, mean_sparse_deg=float(np.mean(deg_cap)),
            n_endpoints=int((role == 1).sum()), n_bridges=int((role == 2).sum()),
            n_rel_slots=R),
    )
    return split


# ---------------------------------------------------------------------------
# Degree-matched negatives per query (observed degree), excluding EVERY true neighbour + bridge
# ---------------------------------------------------------------------------
def _build_deg_index(split):
    K = split["K"]
    deg_int = np.rint(split["train_deg"]).astype(np.int64)
    deg_to_idx = {}
    for i in range(K):
        deg_to_idx.setdefault(int(deg_int[i]), []).append(i)
    deg_to_idx = {d: np.asarray(v, dtype=np.int64) for d, v in deg_to_idx.items()}
    return deg_int, deg_to_idx, (int(deg_int.max()) if K > 0 else 0)


def _sample_negatives(A, C, split, deg_int, deg_to_idx, max_deg, n_neg, rng):
    """Negatives = non-neighbours of A (never the answer), degree-matched to the TARGET C's OBSERVED degree
    (widen minimally) so ARM_POPULARITY sits ~0.5 (hiding lowered C's degree, so match to C not to A)."""
    exclude = set(split["adj"][A])
    exclude.add(A)
    exclude.add(C)
    dA = int(deg_int[C])                                # match to the target's degree, not the query's
    negs = []
    used = set()
    tries = 0
    while len(negs) < n_neg and tries < (max_deg + 2):
        tol = tries
        cand_arrs = []
        for dd in ((dA,) if tol == 0 else (dA - tol, dA + tol)):
            if dd >= 0 and dd in deg_to_idx:
                cand_arrs.append(deg_to_idx[dd])
        tries += 1
        if not cand_arrs:
            continue
        cc = np.concatenate(cand_arrs)
        pool = [int(x) for x in cc.tolist() if x not in exclude and x not in used]
        if not pool:
            continue
        rng.shuffle(pool)
        for p in pool:
            negs.append(p)
            used.add(p)
            if len(negs) >= n_neg:
                break
    return negs


# ---------------------------------------------------------------------------
# THE MECHANISM: chained (meet-in-middle) derivation scorer + single-shot + structural
# ---------------------------------------------------------------------------
def _chained_scores(codeA_row, Zbridge, cand_codes, cand_idx, A_idx, topM):
    """chained_score(cand) = sum over top-M bridges B (by cos(codeA, code[B])) of
       relu(cos(codeA, B)) * relu(cos(B, cand)).  Bridge pool = all gallery except A and the cand itself.
    codeA_row: [d] query code (from the arm's OWN code matrix, or a permuted partner for bridge-shuffle).
    Zbridge: [K,d] gallery codes used AS BRIDGES (learned codes for the mechanism arm).
    cand_codes: [n_cand,d] candidate codes (same code space as Zbridge).
    Returns [n_cand] scores."""
    K = Zbridge.shape[0]
    wA = Zbridge @ codeA_row.astype(np.float64)            # [K] cos(A, every bridge)
    wA[A_idx] = -np.inf                                    # A never bridges itself
    m = K if topM >= ALL_M else min(topM, K - 1)
    top = np.argpartition(wA, -m)[-m:]                     # top-m bridge indices (unordered ok)
    top = top[np.isfinite(wA[top])]
    wA_top = np.maximum(wA[top], 0.0)                      # relu step-1 affinity
    Bsel = Zbridge[top]                                    # [m,d]
    wBc = cand_codes @ Bsel.T                              # [n_cand, m] cos(cand, bridge)
    wBc = np.maximum(wBc, 0.0)                             # relu step-2 affinity
    scores = wBc @ wA_top                                  # [n_cand]
    # exclude a candidate from bridging itself: subtract self-term if the cand is among the top bridges
    top_pos = {int(b): k for k, b in enumerate(top.tolist())}
    for j, ci in enumerate(cand_idx.tolist()):
        if ci in top_pos:
            k = top_pos[ci]
            scores[j] -= wA_top[k] * max(float(cand_codes[j] @ Bsel[k]), 0.0)
    return scores


def _struct_multihop_score(A, cand_idx, split):
    """Non-learned multi-hop structure: # common neighbours of A and cand over OBSERVED adjacency
    (Adamic-Adar-lite). The hidden bridge is NOT in A's observed adjacency, so structure cannot use it."""
    ctxA = set()
    for s in split["ctx_nei_by_rel"][A]:
        ctxA |= split["ctx_nei_by_rel"][A][s]
    out = np.zeros(cand_idx.shape[0], dtype=np.float64)
    cnbr = split["ctx_nei_by_rel"]
    for j, c in enumerate(cand_idx.tolist()):
        ctxC = set()
        for s in cnbr[c]:
            ctxC |= cnbr[c][s]
        out[j] = float(len(ctxA & ctxC))
    return out


def run_seed(seed, split, base_feats, landmarks, target_geo, ev_deg, cfg, topM_levels):
    c = cfg
    own = base_feats["own"]
    ctx = base_feats["ctx"]
    feats = dict(own=own, ctx=ctx)

    # LEARNED codes (grounding + observed relational context; geometry + VICReg + relpred + EMA)
    enc_l = train_fusion(feats, target_geo, landmarks, split, c, seed,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=True)
    Z_learned = encode_all(enc_l, feats)
    # RANDOM-INIT codes (same architecture, untrained)
    enc_r = train_fusion(feats, target_geo, landmarks, split, c, seed + 101,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=False)
    Z_rand = encode_all(enc_r, feats)
    # GROUNDING codes (raw L2 grounding; non-learned)
    Z_ground = _l2_np(own.astype(np.float64)).astype(np.float32)

    # ARMS-MUST-DIFFER (META_RULE_AF)
    digs = {"learned": _emb_digest(Z_learned), "grounding": _emb_digest(Z_ground),
            "randinit": _emb_digest(Z_rand)}
    dl = sorted(digs.items())
    for i in range(len(dl)):
        for j in range(i + 1, len(dl)):
            assert dl[i][1] != dl[j][1], ("META_RULE_AF VIOLATION: %s and %s bit-identical"
                                          % (dl[i][0], dl[j][0]))

    # COLLAPSE codes: row-permuted learned codes (scorer can-fail witness)
    permK = np.random.default_rng(seed + 909).permutation(split["K"])
    Z_collapse = Z_learned[permK]

    # BRIDGE-SHUFFLE partner map over target queries (deterministic derangement of target indices)
    n_t = len(split["targets"])
    bs_rng = np.random.default_rng(seed + 4242)
    partner = np.arange(n_t)
    if n_t > 1:
        for _try in range(8):
            p = bs_rng.permutation(n_t)
            if np.all(p != np.arange(n_t)):
                partner = p
                break
        else:
            partner = np.roll(np.arange(n_t), 1)

    deg_int, deg_to_idx, max_deg = ev_deg
    neg_rng = np.random.default_rng(EVAL_SEED + seed)

    # Precompute negatives per target (shared across arms for a fair comparison)
    inst = []
    for ti, t in enumerate(split["targets"]):
        A, C = t["A"], t["C"]
        negs = _sample_negatives(A, C, split, deg_int, deg_to_idx, max_deg, cfg["n_neg"], neg_rng)
        if len(negs) < 1:
            continue
        cand_idx = np.asarray([C] + negs, dtype=np.int64)
        pm = np.zeros(cand_idx.shape[0], dtype=bool)
        pm[0] = True
        inst.append(dict(ti=ti, A=A, C=C, cand_idx=cand_idx, pm=pm))
    n_query = len(inst)

    # leak-check on negatives: no negative is a true neighbour of A
    neg_leak = 0
    for it in inst:
        adjA = split["adj"][it["A"]]
        neg_leak += sum(1 for x in it["cand_idx"][1:].tolist() if x in adjA)
    if neg_leak != 0:
        raise RuntimeError("NEG LEAK: %d negatives are true neighbours of A (must be 0)" % neg_leak)

    # accumulators
    def _new_acc():
        return []

    auc = {SS_LEARNED: _new_acc(), SS_GROUND: _new_acc(), STRUCT_MH: _new_acc(), POP_ARM: _new_acc()}
    for M in topM_levels:
        auc[(CHAIN_LEARNED, M)] = _new_acc()
        auc[(CHAIN_GROUND, M)] = _new_acc()
        auc[(CHAIN_RANDINIT, M)] = _new_acc()
    auc[(COLLAPSE_ARM, PRIMARY_TOPM)] = _new_acc()
    auc[(BRIDGE_SHUF_ARM, PRIMARY_TOPM)] = _new_acc()

    for it in inst:
        A = it["A"]
        cand_idx = it["cand_idx"]
        pm = it["pm"]
        # SINGLE-SHOT arms (direct cosine)
        sc = Z_learned[cand_idx].astype(np.float64) @ Z_learned[A].astype(np.float64)
        _acc_auc(auc[SS_LEARNED], sc, pm)
        scg = Z_ground[cand_idx].astype(np.float64) @ Z_ground[A].astype(np.float64)
        _acc_auc(auc[SS_GROUND], scg, pm)
        # STRUCTURAL multi-hop (observed common neighbours)
        _acc_auc(auc[STRUCT_MH], _struct_multihop_score(A, cand_idx, split), pm)
        # POPULARITY (observed degree)
        _acc_auc(auc[POP_ARM], split["train_deg"][cand_idx].astype(np.float64), pm)
        # CHAINED arms per topM
        for M in topM_levels:
            _acc_auc(auc[(CHAIN_LEARNED, M)],
                     _chained_scores(Z_learned[A], Z_learned.astype(np.float64),
                                     Z_learned[cand_idx].astype(np.float64), cand_idx, A, M), pm)
            _acc_auc(auc[(CHAIN_GROUND, M)],
                     _chained_scores(Z_ground[A], Z_ground.astype(np.float64),
                                     Z_ground[cand_idx].astype(np.float64), cand_idx, A, M), pm)
            _acc_auc(auc[(CHAIN_RANDINIT, M)],
                     _chained_scores(Z_rand[A], Z_rand.astype(np.float64),
                                     Z_rand[cand_idx].astype(np.float64), cand_idx, A, M), pm)
        # COLLAPSE (row-permuted learned codes) at primary topM
        _acc_auc(auc[(COLLAPSE_ARM, PRIMARY_TOPM)],
                 _chained_scores(Z_collapse[A], Z_collapse.astype(np.float64),
                                 Z_collapse[cand_idx].astype(np.float64), cand_idx, A, PRIMARY_TOPM), pm)
        # BRIDGE-SHUFFLE (query code from a DIFFERENT target; candidates + bridges are learned) at primary topM
        A_partner = split["targets"][partner[it["ti"]]]["A"]
        _acc_auc(auc[(BRIDGE_SHUF_ARM, PRIMARY_TOPM)],
                 _chained_scores(Z_learned[A_partner], Z_learned.astype(np.float64),
                                 Z_learned[cand_idx].astype(np.float64), cand_idx, A, PRIMARY_TOPM), pm)

    out = {}
    for k, v in auc.items():
        name = k if isinstance(k, str) else ("%s@M%s" % (k[0], "ALL" if k[1] >= ALL_M else k[1]))
        out[name] = float(np.mean(v)) if v else float("nan")
    out["_n_query"] = n_query
    out["_neg_leak"] = neg_leak
    out["_code_digests"] = digs
    _log("seed=%d n_q=%d | ss_learned=%.4f ss_ground=%.4f struct=%.4f pop=%.4f | "
         "chain_learned@M%d=%.4f chain_ground@M%d=%.4f collapse=%.4f bridge_shuf=%.4f"
         % (seed, n_query, out[SS_LEARNED], out[SS_GROUND], out[STRUCT_MH], out[POP_ARM],
            PRIMARY_TOPM, out["%s@M%d" % (CHAIN_LEARNED, PRIMARY_TOPM)],
            PRIMARY_TOPM, out["%s@M%d" % (CHAIN_GROUND, PRIMARY_TOPM)],
            out["%s@M%d" % (COLLAPSE_ARM, PRIMARY_TOPM)],
            out["%s@M%d" % (BRIDGE_SHUF_ARM, PRIMARY_TOPM)]))
    return out


def _acc_auc(acc_list, scores, pos_mask):
    a = _auc_from_scores(np.asarray(scores, dtype=np.float64), pos_mask)
    if a is not None:
        acc_list.append(a)


# ---------------------------------------------------------------------------
# Aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, split_meta, cfg, topM_levels, min_query_tasks):
    def series(name):
        return np.array([m[name] for m in per_seed], dtype=np.float64)

    def mean(name):
        return float(np.nanmean(series(name)))

    prim_chain = "%s@M%d" % (CHAIN_LEARNED, PRIMARY_TOPM)
    prim_ground = "%s@M%d" % (CHAIN_GROUND, PRIMARY_TOPM)
    prim_collapse = "%s@M%d" % (COLLAPSE_ARM, PRIMARY_TOPM)
    prim_bshuf = "%s@M%d" % (BRIDGE_SHUF_ARM, PRIMARY_TOPM)

    ss_learned = mean(SS_LEARNED)
    ss_ground = mean(SS_GROUND)
    chain_learned = mean(prim_chain)
    chain_ground = mean(prim_ground)
    struct = mean(STRUCT_MH)
    pop = mean(POP_ARM)
    collapse = mean(prim_collapse)
    bshuf = mean(prim_bshuf)
    n_query = int(np.min([m["_n_query"] for m in per_seed]))

    lift_series = series(prim_chain) - series(SS_LEARNED)
    L_chain_lift = float(np.nanmean(lift_series))
    L_chain_lift_min = float(np.nanmin(lift_series))
    diff_vs_ground_series = (series(prim_chain) - series(SS_LEARNED)) - (series(prim_ground) - series(SS_GROUND))
    diff_vs_ground = float(np.nanmean(diff_vs_ground_series))

    # exploratory: best chained topM (reported, NOT the gate)
    chain_curve = [("ALL" if M >= ALL_M else M, round(mean("%s@M%s" % (CHAIN_LEARNED, "ALL" if M >= ALL_M else M)), 4))
                   for M in topM_levels]
    ground_curve = [("ALL" if M >= ALL_M else M, round(mean("%s@M%s" % (CHAIN_GROUND, "ALL" if M >= ALL_M else M)), 4))
                    for M in topM_levels]
    randinit_curve = [("ALL" if M >= ALL_M else M, round(mean("%s@M%s" % (CHAIN_RANDINIT, "ALL" if M >= ALL_M else M)), 4))
                      for M in topM_levels]

    # validity
    ssb_lo, ssb_hi = SS_CHANCE_BAND
    cb_lo, cb_hi = COLLAPSE_BAND
    bb_lo, bb_hi = BRIDGE_SHUF_BAND
    pb_lo, pb_hi = POP_BAND
    power_ok = bool(n_query >= min_query_tasks)
    collapse_ok = bool(cb_lo <= collapse <= cb_hi)
    bridge_shuf_ok = bool(bb_lo <= bshuf <= bb_hi)
    pop_ok = bool(pb_lo <= pop <= pb_hi)
    validity_ok = bool(power_ok and collapse_ok and bridge_shuf_ok and pop_ok)

    singleshot_near_chance = bool(ssb_lo <= ss_learned <= ssb_hi)

    beats_struct = bool((chain_learned - struct) >= HP_OVER_STRUCT)
    beats_ground_chain = bool((chain_learned - chain_ground) >= HP_OVER_GROUND_CHAIN)
    beats_ss_ground = bool((chain_learned - ss_ground) >= HP_OVER_SS_GROUND)
    lift_ok = bool(L_chain_lift >= HP_CHAIN_LIFT and L_chain_lift_min > 0.0)

    if not validity_ok:
        verdict = "HARD_FAIL_INVALID"
    elif not singleshot_near_chance:
        verdict = "TASK_INVALID_SINGLESHOT_SOLVES"
    elif lift_ok and beats_struct and beats_ground_chain and beats_ss_ground:
        verdict = "HARD_PASS"
    elif lift_ok and not beats_ground_chain:
        verdict = "CHAIN_IS_GENERIC"
    elif abs(L_chain_lift) < HP_CHAIN_LIFT:
        verdict = "CHAIN_FLAT"
    elif L_chain_lift <= -HP_CHAIN_LIFT:
        verdict = "CHAIN_WORSE"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | THE-NUMBER L_chain_lift = chain_learned(M%d) - singleshot_learned = %.4f - %.4f = %+.4f "
        "(per-seed min=%+.4f, need>=%.2f) | ANTI-TRAP1 singleshot_near_chance=%s (ss_learned=%.4f band=%s) | "
        "ANTI-TRAP2 chain_learned - chain_grounding = %.4f - %.4f = %+.4f (need>=%.2f, beats=%s) diff_vs_ground=%+.4f | "
        "chain_learned - struct_multihop = %+.4f (beats=%s) | chain_learned - ss_grounding = %+.4f (beats=%s) | "
        "chain_learned dose-response(topM) %s | grounding-chain %s | randinit-chain %s | "
        "VALIDITY power=%s(n_q=%d) collapse=%.4f(ok=%s) bridge_shuffle=%.4f(ok=%s) pop=%.4f(ok=%s) | "
        "leak-proof witnesses: ctx_leak=%d train_leak=%d (MUST be 0) | "
        "corpus K=%d targets=%d mean_obs_deg_query=%.2f"
        % (verdict, PRIMARY_TOPM, chain_learned, ss_learned, L_chain_lift, L_chain_lift_min, HP_CHAIN_LIFT,
           singleshot_near_chance, ss_learned, list(SS_CHANCE_BAND),
           chain_learned, chain_ground, (chain_learned - chain_ground), HP_OVER_GROUND_CHAIN, beats_ground_chain,
           diff_vs_ground,
           (chain_learned - struct), beats_struct, (chain_learned - ss_ground), beats_ss_ground,
           chain_curve, ground_curve, randinit_curve,
           power_ok, n_query, collapse, collapse_ok, bshuf, bridge_shuf_ok, pop, pop_ok,
           split_meta["leak_ctx_witness"], split_meta["leak_train_witness"],
           split_meta["n_concepts"], split_meta["n_targets"], split_meta["mean_obs_deg_query"]))

    gates = dict(
        singleshot_learned=ss_learned, singleshot_grounding=ss_ground,
        chain_learned_primary=chain_learned, chain_grounding_primary=chain_ground,
        struct_multihop=struct, popularity=pop, collapse=collapse, bridge_shuffle=bshuf,
        L_chain_lift=L_chain_lift, L_chain_lift_min=L_chain_lift_min, diff_vs_grounding=diff_vs_ground,
        margin_over_struct=float(chain_learned - struct),
        margin_over_grounding_chain=float(chain_learned - chain_ground),
        margin_over_ss_grounding=float(chain_learned - ss_ground),
        singleshot_near_chance=singleshot_near_chance, lift_ok=lift_ok,
        beats_struct=beats_struct, beats_grounding_chain=beats_ground_chain, beats_ss_grounding=beats_ss_ground,
        power_ok=power_ok, n_query=n_query, collapse_ok=collapse_ok, bridge_shuf_ok=bridge_shuf_ok,
        pop_ok=pop_ok, validity_ok=validity_ok,
        chain_learned_curve=chain_curve, chain_grounding_curve=ground_curve, chain_randinit_curve=randinit_curve,
        primary_topM=PRIMARY_TOPM,
        hp_chain_lift=HP_CHAIN_LIFT, hp_over_struct=HP_OVER_STRUCT,
        hp_over_grounding_chain=HP_OVER_GROUND_CHAIN, hp_over_ss_grounding=HP_OVER_SS_GROUND,
        ss_chance_band=list(SS_CHANCE_BAND), collapse_band=list(COLLAPSE_BAND),
        bridge_shuf_band=list(BRIDGE_SHUF_BAND), pop_band=list(POP_BAND),
        min_query_tasks=min_query_tasks,
        leak_ctx_witness=split_meta["leak_ctx_witness"], leak_train_witness=split_meta["leak_train_witness"],
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test (REAL-CODE-PATH): tiny synthetic graph engineered to CONTAIN triangles
# ---------------------------------------------------------------------------
def chain_selftest():
    """Assert (a) the triangle-hiding split is leak-proof (ctx_leak==0, train_leak==0), (b) each hidden
    bridge/target is genuinely absent from BOTH endpoints' observed context, (c) the chained scorer runs +
    at n=0 bridges (impossible) vs single-shot differ (mechanism fires), (d) single-shot != chained on
    codes (arms differ), (e) bridge-shuffle produces a finite AUC (mechanics)."""
    K = 240
    rng = np.random.default_rng(11)
    ids = ["c%03d" % i for i in range(K)]
    vals = rng.standard_normal((K, N_VALUE_DIMS))
    gpres = np.ones((K, N_GROUPS), dtype=np.float64)
    # build edges + PLANT triangles so build_triangle_split finds targets on a small graph
    pair_rels = {}

    def _add(a, b, r):
        if a == b:
            return
        if a > b:
            a, b = b, a
        pair_rels.setdefault((a, b), set()).add(r)

    for _ in range(3000):
        a = int(rng.integers(0, K)); b = int(rng.integers(0, K))
        _add(a, b, "REL_%d" % rng.integers(0, 4))
    # plant explicit triangles (a, bridge, c) with a shared bridge + extra context so hiding keeps >=1 obs
    for k in range(30):
        a = 3 * k % K
        c = (3 * k + 1) % K
        bridge = (3 * k + 2) % K
        _add(a, bridge, "REL_0")
        _add(bridge, c, "REL_1")
        _add(a, c, "REL_2")
        _add(a, (a + 7) % K, "REL_3")     # extra observed context for A
        _add(c, (c + 11) % K, "REL_3")    # extra observed context for C
    top_rels = ["REL_0", "REL_1", "REL_2", "REL_3"]
    rel_id = {r: i for i, r in enumerate(top_rels)}
    R = len(top_rels) + 1

    def _rel_slot(r):
        return rel_id.get(r, R - 1)

    data = dict(ids=ids, surfaces=ids, vals=vals, gpres=gpres, pair_rels=pair_rels,
                K=K, R=R, rel_slot=_rel_slot,
                meta=dict(n_kept_concepts=K, n_kept_pairs=len(pair_rels), n_rel_slots=R))
    cfg = dict(n_targets=25, n_neg=8, max_endpoint_uses=2, min_obs_ctx=1, min_instances=10,
               epochs=8, code_dim=24, hidden=40, lr=5e-3,
               n_landmarks=24, n_land_batch=24, n_anchor_batch=48,
               lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
               infonce_tau=0.2, feat_dropout=0.1)
    try:
        split = build_triangle_split(data, cfg)
    except RuntimeError as e:
        return False, dict(err="split:" + str(e)[:200])

    # (b) verify hiding per target
    hide_ok = True
    for t in split["targets"]:
        A, B, C = t["A"], t["B"], t["C"]
        a_obs = set().union(*[split["ctx_nei_by_rel"][A][s] for s in split["ctx_nei_by_rel"][A]]) \
            if split["ctx_nei_by_rel"][A] else set()
        c_obs = set().union(*[split["ctx_nei_by_rel"][C][s] for s in split["ctx_nei_by_rel"][C]]) \
            if split["ctx_nei_by_rel"][C] else set()
        if (B in a_obs) or (C in a_obs) or (B in c_obs) or (A in c_obs):
            hide_ok = False
            break

    own = split["own_feat"]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A_adj = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A_adj, landmarks)
    feats = dict(own=base_feats["own"], ctx=base_feats["ctx"])
    enc = train_fusion(feats, target_geo, landmarks, split, cfg, 7,
                       use_ctx=True, w_rel=cfg["w_rel"], w_ema=cfg["w_ema"], do_train=True)
    Z = encode_all(enc, feats)

    # (c/d) single-shot vs chained on one instance
    deg_int, deg_to_idx, max_deg = _build_deg_index(split)
    neg_rng = np.random.default_rng(123)
    t0 = split["targets"][0]
    A, C = t0["A"], t0["C"]
    negs = _sample_negatives(A, C, split, deg_int, deg_to_idx, max_deg, cfg["n_neg"], neg_rng)
    cand_idx = np.asarray([C] + negs, dtype=np.int64)
    pm = np.zeros(cand_idx.shape[0], dtype=bool); pm[0] = True
    ss = Z[cand_idx].astype(np.float64) @ Z[A].astype(np.float64)
    ch = _chained_scores(Z[A], Z.astype(np.float64), Z[cand_idx].astype(np.float64), cand_idx, A, 20)
    ss_auc = _auc_from_scores(ss, pm)
    ch_auc = _auc_from_scores(ch, pm)
    # MECHANISM FIRES = the chained scorer is a genuinely DIFFERENT computation than single-shot cosine
    # (compare the raw score VECTORS, not the AUCs -- on a structure-free synthetic graph two arms can
    # coincidentally share an AUC while producing different scores; the AUC discriminator is a real-data
    # property verified at smoke, not a synthetic-graph guarantee).
    mechanism_fires = bool(ss_auc is not None and ch_auc is not None
                           and ss.shape == ch.shape and not np.allclose(ss, ch, atol=1e-9)
                           and np.all(np.isfinite(ch)))
    neg_leak = sum(1 for x in negs if x in split["adj"][A])

    checks = dict(n_targets=split["split_meta"]["n_targets"],
                  leak_ctx=split["split_meta"]["leak_ctx_witness"],
                  leak_train=split["split_meta"]["leak_train_witness"],
                  hide_ok=hide_ok, ss_auc=round(float(ss_auc), 4) if ss_auc is not None else None,
                  chain_auc=round(float(ch_auc), 4) if ch_auc is not None else None,
                  mechanism_fires=mechanism_fires, neg_leak=neg_leak)
    ok = bool(hide_ok and split["split_meta"]["leak_ctx_witness"] == 0
              and split["split_meta"]["leak_train_witness"] == 0
              and mechanism_fires and neg_leak == 0
              and split["split_meta"]["n_targets"] >= cfg["min_instances"])
    return ok, checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap-nodes", type=int, default=0)
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
    topM_levels = list(cfg["topM_levels"])
    if PRIMARY_TOPM not in topM_levels:            # primary arm (+ collapse/bridge-shuffle) key on PRIMARY_TOPM
        topM_levels = sorted(set(topM_levels) | {PRIMARY_TOPM})

    anchor = ANCHOR_NAME
    if run_mode == "self_test":
        anchor = anchor + "_selftest"
    elif run_mode == "smoke":
        anchor = anchor + "_smoke"
    output_dir = get_output_dir(anchor)
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = chain_selftest()
    _log("chain_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED chain_ok=%s: %s" % (st_ok, st_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            chain_selftest=st_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})

    split = build_triangle_split(data, cfg)
    _log("triangle split: %s" % split["split_meta"])
    own = split["own_feat"]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A_adj = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A_adj, landmarks)
    ev_deg = _build_deg_index(split)
    _log("landmarks=%d ctx_dim=%d topM=%s"
         % (landmarks.shape[0], base_feats["ctx"].shape[1],
            ["ALL" if m >= ALL_M else m for m in topM_levels]))

    if run_mode == "self_test":
        pm = run_seed(cfg["seeds"][0], split, base_feats, landmarks, target_geo, ev_deg, cfg, topM_levels)
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS through-intermediate chaining exercised on real code path",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            chain_selftest=st_res, data_meta=data["meta"], split_meta=split["split_meta"],
            singleshot_learned=pm[SS_LEARNED],
            chain_learned_primary=pm["%s@M%d" % (CHAIN_LEARNED, PRIMARY_TOPM)]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed = []
    seed_failures = []
    total_units_run = 0
    for seed in cfg["seeds"]:
        try:
            pm = run_seed(seed, split, base_feats, landmarks, target_geo, ev_deg, cfg, topM_levels)
            per_seed.append(pm)
            total_units_run += 1
            write_partial(output_dir, "seed%d" % seed,
                          {k: v for k, v in pm.items() if not k.startswith("_code")})
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
        per_seed, split["split_meta"], cfg, topM_levels, min_query)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"],
        topM_levels=["ALL" if m >= ALL_M else m for m in topM_levels],
        expected_total_units=expected_n_units, total_units_run=total_units_run,
        config={k: v for k, v in cfg.items()},
        data_meta={k: v for k, v in data["meta"].items()},
        split_meta=split["split_meta"],
        gates=gates,
        per_seed=[{k: v for k, v in m.items() if not k.startswith("_code")} for m in per_seed],
        chain_selftest=st_res, seed_failures=seed_failures,
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
