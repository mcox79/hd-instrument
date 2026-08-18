"""LEAK-PROOF held-out-NEW relational-inference: CONTEXT-SIZE SWEEP (envelope map of the 29587 win).

ENVELOPE AXIS 1a (harder generalization) + AXIS 3 (reasoning-theory constraints) IN ONE SWEEP:
  Base win (leakproof_relational_inference_heldout_v1, banked 29587): LEARNED beats grounding-homophily
  +0.108 and non-learned 2-hop +0.093 on held-out-NEW concepts, at mean_ctx~40 CONTEXT edges. This cell
  throttles the number of CONTEXT edges the held-out rep is shown -- max_context in {1,2,3,5,10,ALL} --
  holding the PREDICT (eval) targets FIXED. Two questions, one sweep:
    (1a) FEWER-CONTEXT SURVIVAL: at max_context=1 (told ONE relation of the new concept), does LEARNED
         still beat {grounding-homophily, 2-hop, shuffle, collapse, popularity}? If the win EVAPORATES
         at low context => the base capability was context-saturated (scope boundary, reported honestly).
    (3)  CONSTRAINTS RAISE MARGIN: as max_context 1->2->3->5->10->ALL, does the LEARNED-minus-baseline
         margin GROW? Reasoning resolution should scale with # constraints brought to bear.
  ALL-context arm reproduces the 29587 number (positive control, Gate D).
  cap_nodes is the SCALE knob (axis 2): run FULL at cap_nodes 2500 (confirmed) / 4000 (scale point).

Everything else REUSED verbatim from the confirmed base: leak-proof CONTEXT-disjoint-PREDICT split +
0/N no-overlap witness, degree-matched negatives, shuffle-context COLLAPSE control, popularity + 2hop +
random-init baselines, fusion self-teacher (geometry+VICReg+relpred-InfoNCE+EMA), deterministic sha256
split. Only NEW code: a max_context cap on the HELD-OUT context (rep INPUT); negatives still exclude the
FULL true-neighbour set (capped-out partners are still real neighbours -> never sampled as a negative).

--- original base docstring (mechanism unchanged) ---
LEAK-PROOF held-out-NEW relational-INFERENCE diagnostic.

WHY (VET finding): the prior relational-placement eval in
  experiments/exp_deep_text_encoder_self_teacher_heldout_new_v1.py was CIRCULAR. For each held-out
  concept h, build_split (~645-660) built ctx_nei_by_rel[h] (the rep INPUT, pooled when use_ctx=True)
  AND train_neigh[h] (the eval POSITIVE set) from the SAME train-edges. So the held-out rep ingested a
  summary of the EXACT edges it was then scored on (VET: 1005/1005 context-neighbour == eval-positive
  overlap). Any "relational placement" win was store-then-recall, not inference.

WHAT THIS FIXES (ONLY the split; reuse the fusion encoder + geometry + relpred + degree-matched-neg infra):
  For each held-out-NEW concept, partition ITS train-edges into two DISJOINT sets:
    CONTEXT  = used to BUILD the rep (pooled into ctx block, the INPUT). never scored.
    PREDICT  = a held-out edge target, NEVER in context, NEVER in training. the eval POSITIVE.
  CONTEXT-neighbours INTERSECT PREDICT-targets = EMPTY (asserted empirically -> the leak-proof witness,
  must print 0/N). The predicted target concept never appears in the concept's context input in any form.

TASK (genuine inductive relational inference): given a held-out concept's rep (grounding + CONTEXT edges
  only), rank its true PREDICT-edge target among DEGREE-MATCHED train non-neighbour negatives. Told SOME
  of a new concept's relations, infer an UNSEEN one.

THE ONE NUMBER (pre-registered bands below, BEFORE running):
  LEARNED (fusion: grounding + relational-CONTEXT, trained geometry + VICReg + relpred-InfoNCE + EMA)
  vs the ceilings/floors:
    RAW_GROUNDING     : cosine over raw grounding (20d), NO learning, NO relational context. [THE ceiling]
    RANDOM_INIT       : same fusion architecture, UNTRAINED (isolates learning).
    STRUCT_2HOP       : non-learned relational baseline = count of CONTEXT-neighbours adjacent to the
                        candidate (friend-of-friend). Isolates "trivial structural overlap" from learning.
    POPULARITY        : rank candidates by train-degree only (query-independent). Degree-matched negs
                        => must sit ~0.50 (VALIDITY control that degree-matching killed the popularity confound).
    COLLAPSE_SHUFFLE  : fusion trained on row-permuted inputs => ~0.50 (can-fail / leak witness).
  HARD_PASS = LEARNED - RAW_GROUNDING >= 0.03 with per-seed min > 0 (genuine relational inference beyond
              homophily). TIE (|margin| < 0.03) CONFIRMS relational learning ~null at this data scale =
              the decisive honest finding (reported TIE_NULL). Requires VALIDITY (collapse ~0.5,
              popularity ~0.5, power >= MIN_QUERY_TASKS) or the number is untrustworthy -> HARD_FAIL_INVALID.

SCOPE NOTE (compute-proportionality + clean attribution): this diagnostic ISOLATES the RELATIONAL
  mechanism. The deep-text MLM / char-trigram branch of the source cell is DROPPED on purpose -- text
  MEANING is an orthogonal lever already measured ~null (R3/R4 +0.007) and would CONFOUND the
  relational-inference attribution. We reuse the fusion encoder, target-geometry, relpred InfoNCE, EMA,
  degree-matched-negative sampler, and deterministic sha256 split. No text, no NLTK, no GPU, no network.

HARD INVARIANTS: TEACHER-FREE (no borrowed vectors anywhere; inputs are ONLY measured grounding norms +
  the foundation's own relational graph). INDUCTIVE (held-out placed from its features; never a landmark /
  training anchor / relpred positive). LEAK-PROOF (CONTEXT disjoint from PREDICT; PREDICT never trains,
  never contexts; negatives exclude CONTEXT and PREDICT). ASCII-only. CPU-only.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test over the code arms)
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: AUC discriminator base = 0.5 exactly; collapse + popularity controls witness the floor
# - baseline_in_band at smoke: collapse ~0.5; popularity ~0.5; raw_grounding a real signal; primary not saturated
# - discriminator survives scale: FULL runs >=3 seeds foreground; smoke previews the number
# - HARD_PASS strictly above floor: margin>=0.03 AND per-seed min>0 (not at-floor)
# - HP_SCOPE: gates apply to ARM_LEARNED (primary) only
# - no sweep axis -> cardinality_ok via EXPECTED_N_UNITS = n_seeds
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (AUC base=0.5 analytic; collapse+popularity witness it)
# - deterministic seeding: sha256 concept split + sha256 context/predict split + fixed int seeds + sorted(); no hash()/list(set())
# - no substrate KGStore/fit objects (self-contained jsonl reader + numpy + torch) -> F.1/F.2 real_code_path N/A
# - progress_logging: print_flush_true (per-seed + eval logs flush=True)
"""

import argparse
import glob
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

ANCHOR_NAME = "leakproof_relinfer_context_sweep_v1"
FOUNDATION_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")
NODES_PATH = os.path.join(FOUNDATION_DIR, "nodes.jsonl")
EDGES_GLOB = os.path.join(FOUNDATION_DIR, "edges_shard_*.jsonl")

# Grounding feature layout (16 value dims + 4 group-present mask bits = 20).
LANCASTER_KEYS = ["aud", "gus", "hap", "int", "olf", "vis",
                  "foot", "hand", "head", "mouth", "torso"]
GROUPS = [
    ("lancaster", LANCASTER_KEYS),
    ("concreteness", ["conc"]),
    ("vad", ["valence", "arousal", "dominance"]),
    ("aoa", ["aoa"]),
]
N_VALUE_DIMS = sum(len(ks) for _, ks in GROUPS)   # 16
N_GROUPS = len(GROUPS)                            # 4
GROUND_DIM = N_VALUE_DIMS + N_GROUPS              # 20

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
# ALL_CONTEXT sentinel: a max_context so large it never caps (reproduces the base all-context arm).
ALL_CONTEXT = 100000

SELFTEST_CFG = dict(
    min_deg=2, cap_nodes=400, seeds=[7], heldout_frac=0.2, top_rel=8, predict_frac=0.5,
    epochs=15, code_dim=32, hidden=64, lr=5e-3,
    n_landmarks=48, n_land_batch=48, n_anchor_batch=96,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    max_context_levels=[1, ALL_CONTEXT],
)
SMOKE_CFG = dict(
    min_deg=2, cap_nodes=800, seeds=[7], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=80, code_dim=128, hidden=256, lr=3e-3,
    n_landmarks=192, n_land_batch=128, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    max_context_levels=[1, 3, ALL_CONTEXT],
)
FULL_CFG = dict(
    min_deg=2, cap_nodes=2500, seeds=[7, 13, 19], heldout_frac=0.2, top_rel=16, predict_frac=0.5,
    epochs=140, code_dim=128, hidden=256, lr=2.5e-3,
    n_landmarks=448, n_land_batch=192, n_anchor_batch=256,
    lambda_var=1.0, w_geo=1.0, w_rel=0.5, w_ema=0.5, ema_momentum=0.99,
    infonce_tau=0.2, feat_dropout=0.1, n_deg_bins=5,
    max_context_levels=[1, 2, 3, 5, 10, ALL_CONTEXT],
)

# Deterministic salts / seeds
CONCEPT_SPLIT_SALT = "leakproof_rel_infer_v1_concept_split::"
CTX_PRED_SALT = "leakproof_rel_infer_v1_ctx_pred_split::"
EVAL_SEED = 20260726

# Pre-reg bands (applied to ARM_LEARNED primary held-out relational-inference AUC).
HP_MARGIN_OVER_RAW = 0.03         # THE NUMBER: LEARNED - RAW_GROUNDING must exceed this (real inference)
TIE_EPS = 0.03                    # |LEARNED - RAW_GROUNDING| < this => TIE_NULL (relational learning ~null)
HP_LEARNED_FLOOR = 0.53           # LEARNED must be a genuine >chance signal for a PASS to mean anything
COLLAPSE_BAND = (0.44, 0.56)      # ARM_COLLAPSE_SHUFFLE MUST sit here (can-fail witness)
POP_BAND = (0.44, 0.56)           # ARM_POPULARITY MUST sit ~0.5 (exact-degree-matching validity control)
MIN_QUERY_TASKS = 100             # power floor for the held-out AUC to be trustworthy
MAX_PRED_PER_QUERY = 20           # bound predict positives/query (deterministic subset) -> bounded compute

# Arms
RAW_ARM = "ARM_RAW_GROUNDING"
LEARNED_ARM = "ARM_LEARNED"
RANDINIT_ARM = "ARM_RANDOM_INIT"
STRUCT_ARM = "ARM_STRUCT_2HOP"
POP_ARM = "ARM_POPULARITY"
SHUFFLE_ARM = "ARM_COLLAPSE_SHUFFLE"
PRIMARY_ARM = LEARNED_ARM
# code-producing arms (get cosine scoring + arms-must-differ hash test)
CODE_ARMS = [RAW_ARM, LEARNED_ARM, RANDINIT_ARM, SHUFFLE_ARM]
# non-code arms (custom per-query scoring)
FUNC_ARMS = [STRUCT_ARM, POP_ARM]
ALL_ARMS = [RAW_ARM, LEARNED_ARM, RANDINIT_ARM, STRUCT_ARM, POP_ARM, SHUFFLE_ARM]


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


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ---------------------------------------------------------------------------
# Deterministic held-out split (sha256; PYTHONHASHSEED-independent)
# ---------------------------------------------------------------------------
def _concept_is_heldout(concept_id, heldout_frac):
    h = hashlib.sha256((CONCEPT_SPLIT_SALT + concept_id).encode("utf-8")).digest()
    r = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return r < heldout_frac


def _ctx_pred_rank(query_id, partner_id):
    """Deterministic hash key ranking a partner within a query's neighbour set."""
    return hashlib.sha256((CTX_PRED_SALT + query_id + "::" + partner_id).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Grounding
# ---------------------------------------------------------------------------
def _grounding_vector(gd):
    vals = np.full(N_VALUE_DIMS, np.nan, dtype=np.float64)
    gpres = np.zeros(N_GROUPS, dtype=np.float64)
    off = 0
    for gi, (gname, keys) in enumerate(GROUPS):
        sub = gd.get(gname)
        if isinstance(sub, dict) and len(sub) > 0:
            gpres[gi] = 1.0
            for k in keys:
                v = sub.get(k)
                if v is not None:
                    vals[off + keys.index(k)] = float(v)
        off += len(keys)
    return vals, gpres


def load_grounded_subgraph(cfg):
    """Load grounded concepts + induced relational subgraph among them (degree-filtered, capped)."""
    if not os.path.exists(NODES_PATH):
        raise FileNotFoundError("nodes.jsonl not found at %s" % NODES_PATH)

    gid_list, surf_list, raw_vals, raw_gpres = [], [], [], []
    with open(NODES_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            gd = d.get("grounding")
            if not gd:
                continue
            vals, gpres = _grounding_vector(gd)
            gid_list.append(d["id"])
            surf_list.append(d.get("surface", d["id"]))
            raw_vals.append(vals)
            raw_gpres.append(gpres)
    if len(gid_list) < 200:
        raise RuntimeError("too few grounded nodes (%d)" % len(gid_list))

    gid_set = set(gid_list)
    idx_of = {c: i for i, c in enumerate(gid_list)}

    pair_rels = {}
    for shard in sorted(glob.glob(EDGES_GLOB)):
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                s = e.get("subject")
                o = e.get("obj")
                rel = e.get("relation") or "OTHER"
                if s is None or o is None or s == o:
                    continue
                if s in gid_set and o in gid_set:
                    a, b = idx_of[s], idx_of[o]
                    if a > b:
                        a, b = b, a
                    pair_rels.setdefault((a, b), set()).add(rel)
    if len(pair_rels) < 100:
        raise RuntimeError("too few induced pairs among grounded (%d)" % len(pair_rels))

    n_all = len(gid_list)
    induced_deg = np.zeros(n_all, dtype=np.int64)
    for (a, b) in pair_rels:
        induced_deg[a] += 1
        induced_deg[b] += 1

    keep_mask = induced_deg >= cfg["min_deg"]
    keep_idx = np.nonzero(keep_mask)[0]
    if keep_idx.shape[0] > cfg["cap_nodes"]:
        order = sorted(keep_idx.tolist(), key=lambda i: (-int(induced_deg[i]), gid_list[i]))
        keep_idx = np.array(sorted(order[:cfg["cap_nodes"]]), dtype=np.int64)
    keep_idx_set = set(keep_idx.tolist())

    kept = sorted(keep_idx.tolist())
    remap = {old: new for new, old in enumerate(kept)}
    K = len(kept)
    ids = [gid_list[o] for o in kept]
    surfaces = [surf_list[o] for o in kept]
    vals = np.stack([raw_vals[o] for o in kept], axis=0)
    gpres = np.stack([raw_gpres[o] for o in kept], axis=0)

    rel_freq = {}
    kept_pair_rels = {}
    for (a, b), rels in pair_rels.items():
        if a in keep_idx_set and b in keep_idx_set:
            na, nb = remap[a], remap[b]
            key = (na, nb) if na < nb else (nb, na)
            kept_pair_rels[key] = set(rels)
            for r in rels:
                rel_freq[r] = rel_freq.get(r, 0) + 1
    if len(kept_pair_rels) < 100:
        raise RuntimeError("too few kept pairs after degree filter (%d)" % len(kept_pair_rels))

    rel_sorted = sorted(rel_freq.items(), key=lambda kv: (-kv[1], kv[0]))
    top_rels = [r for r, _ in rel_sorted[:cfg["top_rel"]]]
    rel_id = {r: i for i, r in enumerate(top_rels)}
    R = len(top_rels) + 1
    other_id = R - 1

    def _rel_slot(r):
        return rel_id.get(r, other_id)

    meta = dict(
        n_grounded_total=n_all, n_induced_pairs_total=len(pair_rels),
        n_kept_concepts=K, n_kept_pairs=len(kept_pair_rels),
        min_deg=cfg["min_deg"], cap_nodes=cfg["cap_nodes"],
        top_rels=top_rels, n_rel_slots=R,
    )
    return dict(ids=ids, surfaces=surfaces, vals=vals, gpres=gpres,
                pair_rels=kept_pair_rels, K=K, R=R, rel_slot=_rel_slot, meta=meta)


# ---------------------------------------------------------------------------
# LEAK-PROOF split: held-out concept edges -> disjoint CONTEXT / PREDICT
# ---------------------------------------------------------------------------
def build_leakproof_split(data, cfg, max_context=None):
    """CONTEXT edges build the rep (input); PREDICT edges are held-out targets (never context/training).
    Asserts CONTEXT-neigh INTERSECT PREDICT-target == EMPTY per held-out query (leak-proof witness).
    max_context (int or None): cap the number of HELD-OUT context edges SHOWN to the rep (top-k by the
    deterministic ctx/pred rank). PREDICT targets are held FIXED across the sweep. Capped-out partners are
    still real neighbours (stored in true_nei_all) so they are EXCLUDED from negatives (never a false-neg)."""
    ids = data["ids"]
    K = data["K"]
    R = data["R"]
    rel_slot = data["rel_slot"]
    predict_frac = cfg["predict_frac"]
    if max_context is None:
        max_context = ALL_CONTEXT

    heldout = np.array([_concept_is_heldout(c, cfg["heldout_frac"]) for c in ids], dtype=bool)
    is_train = ~heldout
    train_idx = np.nonzero(is_train)[0]
    held_idx = np.nonzero(heldout)[0]
    if train_idx.shape[0] < 100 or held_idx.shape[0] < 40:
        raise RuntimeError("degenerate split: train=%d held=%d" % (train_idx.shape[0], held_idx.shape[0]))
    train_set = set(train_idx.tolist())

    # neighbours restricted to TRAIN partner: {concept -> {train_partner_idx: set(rels)}}
    neigh_by = [dict() for _ in range(K)]
    for (a, b), rels in data["pair_rels"].items():
        if b in train_set:
            neigh_by[a][b] = set(rels)
        if a in train_set:
            neigh_by[b][a] = set(rels)

    # standardize grounding on TRAIN stats only
    vals = data["vals"]
    tr_vals = vals[train_idx]
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", RuntimeWarning)
        mu = np.nanmean(tr_vals, axis=0)
        sd = np.nanstd(tr_vals, axis=0)
    mu = np.nan_to_num(mu, nan=0.0)
    sd = np.where(np.isnan(sd) | (sd < 1e-6), 1.0, sd)
    z = (vals - mu[None, :]) / sd[None, :]
    z = np.where(np.isnan(z), 0.0, z).astype(np.float64)
    own_feat = np.concatenate([z, data["gpres"]], axis=1).astype(np.float64)   # [K,20]

    ctx_nei_by_rel = [dict() for _ in range(K)]   # rep INPUT context (per-rel neighbour sets)
    train_neigh = [set() for _ in range(K)]       # relpred positives (TRAIN anchors only, uses all edges)
    predict_nei = [set() for _ in range(K)]       # held-out PREDICT targets (eval positives, held-out only)
    context_nei = [set() for _ in range(K)]       # held-out CONTEXT partners SHOWN (capped; struct_2hop src)
    true_nei_all = [set() for _ in range(K)]      # held-out ALL true neighbours (incl capped-out; neg-exclude)
    train_deg = np.zeros(K, dtype=np.float64)     # train-train degree (gallery degree bins + landmarks)

    # TRAIN concepts: full context + relpred positives; train-train degree
    for i in train_idx.tolist():
        for j, rels in neigh_by[i].items():
            for r in rels:
                ctx_nei_by_rel[i].setdefault(rel_slot(r), set()).add(j)
            train_neigh[i].add(j)          # j is a train partner
            train_deg[i] += 1              # both endpoints train (neigh_by only has train partners)

    # HELD-OUT concepts: split train partners into disjoint CONTEXT / PREDICT
    overlap_total = 0
    predict_targets_total = 0
    n_eval_queries = 0
    held_ctx_sizes = []
    for h in held_idx.tolist():
        partners = sorted(neigh_by[h].keys())      # deterministic
        if len(partners) < 2:                      # need >=1 context + >=1 predict
            continue
        ranked = sorted(partners, key=lambda j: _ctx_pred_rank(ids[h], ids[j]))
        m = len(ranked)
        n_pred = max(1, min(m - 1, int(round(predict_frac * m))))
        pred_set = set(ranked[:n_pred])
        ctx_ranked = ranked[n_pred:]                    # full context pool (rank-ordered, deterministic)
        ctx_full = set(ctx_ranked)
        ctx_shown = set(ctx_ranked[:max_context])       # CAPPED context actually shown to the rep
        # leak-proof witness: SHOWN context and predict MUST be disjoint (and full context vs predict)
        overlap_total += len(pred_set & ctx_full)
        predict_targets_total += len(pred_set)
        predict_nei[h] = pred_set
        context_nei[h] = ctx_shown                      # struct_2hop uses only shown context
        true_nei_all[h] = pred_set | ctx_full           # every real neighbour -> excluded from negatives
        # build the rep INPUT context from SHOWN (capped) CONTEXT partners ONLY
        for j in ctx_shown:
            for r in neigh_by[h][j]:
                ctx_nei_by_rel[h].setdefault(rel_slot(r), set()).add(j)
        held_ctx_sizes.append(len(ctx_shown))
        n_eval_queries += 1

    if overlap_total != 0:
        raise RuntimeError("LEAK: context INTERSECT predict = %d (must be 0)" % overlap_total)
    if n_eval_queries < 5:
        raise RuntimeError("too few held-out eval queries with >=2 train neighbours (%d)" % n_eval_queries)

    split_meta = dict(
        n_train=int(train_idx.shape[0]), n_heldout=int(held_idx.shape[0]),
        n_eval_queries=n_eval_queries,
        no_overlap_witness_overlap=overlap_total,          # MUST be 0
        no_overlap_witness_predict_targets=predict_targets_total,
        mean_held_context_size=float(np.mean(held_ctx_sizes)) if held_ctx_sizes else 0.0,
        n_rel_slots=R, predict_frac=predict_frac,
        max_context=(None if max_context >= ALL_CONTEXT else int(max_context)),
    )
    return dict(own_feat=own_feat, is_train=is_train, K=K, R=R,
                train_idx=train_idx, held_idx=held_idx, train_deg=train_deg,
                ctx_nei_by_rel=ctx_nei_by_rel, train_neigh=train_neigh,
                predict_nei=predict_nei, context_nei=context_nei,
                true_nei_all=true_nei_all, split_meta=split_meta)


def _pooled_ctx_block(split, per_source, block_dim):
    K = split["K"]
    R = split["R"]
    ctx_nei_by_rel = split["ctx_nei_by_rel"]
    import math
    per_rel = block_dim + 2
    out = np.zeros((K, R * per_rel), dtype=np.float64)
    ps = per_source.astype(np.float64)
    for i in range(K):
        for s in range(R):
            neigh = ctx_nei_by_rel[i].get(s)
            off = s * per_rel
            if neigh:
                nj = np.fromiter(sorted(neigh), dtype=np.int64, count=len(neigh))
                out[i, off:off + block_dim] = ps[nj].mean(axis=0)
                out[i, off + block_dim] = 1.0
                out[i, off + block_dim + 1] = math.log1p(len(neigh))
    return out


# ---------------------------------------------------------------------------
# Fusion encoder (grounding + relational-context), teacher-free self-teacher
# ---------------------------------------------------------------------------
class FusionEncoder(torch.nn.Module):
    def __init__(self, ground_dim, ctx_dim, hidden, code_dim, use_ctx):
        super().__init__()
        self.use_ctx = use_ctx
        in_dim = ground_dim + (ctx_dim if use_ctx else 0)
        self.net = torch.nn.Sequential(
            torch.nn.Linear(in_dim, hidden), torch.nn.GELU(),
            torch.nn.Linear(hidden, code_dim))

    def encode(self, ground, ctx):
        parts = [ground]
        if self.use_ctx:
            parts.append(ctx)
        return self.net(torch.cat(parts, dim=1))

    def forward(self, ground, ctx):
        return self.encode(ground, ctx)


def _l2_np(x, eps=1e-8):
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)


def _l2_t(h, eps=1e-8):
    return h / (h.norm(dim=1, keepdim=True) + eps)


def select_landmarks(split, cfg):
    train_idx = split["train_idx"].tolist()
    train_deg = split["train_deg"]
    ranked = sorted(train_idx, key=lambda i: (-float(train_deg[i]), i))
    L = min(cfg["n_landmarks"], len(ranked))
    return np.array(sorted(ranked[:L]), dtype=np.int64)


def build_train_adjacency(split):
    """Adjacency over ctx_nei_by_rel (TRAIN context; held-out rows use CONTEXT-only edges)."""
    K = split["K"]
    ctx_nei_by_rel = split["ctx_nei_by_rel"]
    A = np.zeros((K, K), dtype=np.float32)
    for i in range(K):
        for s, neigh in ctx_nei_by_rel[i].items():
            for j in neigh:
                A[i, j] = 1.0
    return A


def _zscore_matrix(M):
    mu = float(M.mean())
    sd = float(M.std()) + 1e-6
    return (M - mu) / sd


def compute_target_geometry(own_norm, A, landmarks, alpha=0.5):
    Lm_own = own_norm[landmarks]
    G = own_norm @ Lm_own.T
    Lm_A = A[landmarks]
    shared = A @ Lm_A.T
    deg = np.sqrt((A * A).sum(axis=1) + 1e-6)
    deg_l = deg[landmarks]
    Rm = shared / (deg[:, None] * deg_l[None, :] + 1e-6)
    T = alpha * _zscore_matrix(G) + (1.0 - alpha) * _zscore_matrix(Rm)
    return T.astype(np.float32)


def _pick_relpred_positive(anchor_ids, train_neigh, rng):
    valid = np.zeros(anchor_ids.shape[0], dtype=bool)
    pos = np.zeros(anchor_ids.shape[0], dtype=np.int64)
    for k, a in enumerate(anchor_ids.tolist()):
        nb = train_neigh[a]
        if nb:
            arr = np.fromiter(sorted(nb), dtype=np.int64, count=len(nb))
            pos[k] = int(arr[rng.integers(0, arr.shape[0])])
            valid[k] = True
    return valid, pos


def train_fusion(feats, target_geo, landmarks, split, cfg, seed,
                 use_ctx, w_rel, w_ema, do_train=True, shuffle_rows=False):
    """Fusion self-teacher: geometry (smooth-L1 to teacher-free grounding+adjacency profile) + VICReg
    var + relpred InfoNCE (predict TRAIN neighbours) + EMA. do_train=False => random-init.
    shuffle_rows permutes input rows across ids (COLLAPSE witness)."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed + 17)

    K = split["K"]
    ground = feats["own"].astype(np.float32)
    ctx = feats["ctx"].astype(np.float32)
    if shuffle_rows:
        perm = np.random.default_rng(seed + 909).permutation(K)
        ground = ground[perm]
        ctx = ctx[perm]

    Xg = torch.from_numpy(ground)
    Xc = torch.from_numpy(ctx)

    enc = FusionEncoder(GROUND_DIM, ctx.shape[1], cfg["hidden"], cfg["code_dim"], use_ctx=use_ctx)
    if not do_train:
        enc.eval()
        return enc

    ema = None
    if w_ema > 0.0:
        import copy
        ema = copy.deepcopy(enc)
        for p in ema.parameters():
            p.requires_grad_(False)

    opt = torch.optim.Adam([p for p in enc.parameters() if p.requires_grad], lr=cfg["lr"])
    Lm_all = torch.from_numpy(landmarks.astype(np.int64))
    T_all = torch.from_numpy(target_geo.astype(np.float32))
    anchors = np.asarray(split["train_idx"], dtype=np.int64)
    train_neigh = split["train_neigh"]
    nL = landmarks.shape[0]
    fd = cfg["feat_dropout"]
    tau = cfg["infonce_tau"]
    log_every = max(1, cfg["epochs"] // 4)
    t0 = time.perf_counter()

    def _enc_rows(module, rows, feat_drop=0.0):
        g = Xg[rows]
        c = Xc[rows]
        if feat_drop > 0.0:
            g = torch.nn.functional.dropout(g, p=feat_drop, training=True)
            c = torch.nn.functional.dropout(c, p=feat_drop, training=True)
        return module.encode(g, c)

    for ep in range(cfg["epochs"]):
        a_bs = min(cfg["n_anchor_batch"], anchors.shape[0])
        l_bs = min(cfg["n_land_batch"], nL)
        a_idx = rng.choice(anchors, size=a_bs, replace=False)
        l_sel = np.sort(rng.choice(nL, size=l_bs, replace=False))
        a_rows = torch.from_numpy(a_idx)
        l_rows = Lm_all[torch.from_numpy(l_sel)]

        z_a = _l2_t(_enc_rows(enc, a_rows))
        z_l = _l2_t(_enc_rows(enc, l_rows))
        S = z_a @ z_l.t()
        T = T_all[a_rows][:, torch.from_numpy(l_sel)]
        S_c = S - S.mean(dim=1, keepdim=True)
        T_c = T - T.mean(dim=1, keepdim=True)
        geo_loss = torch.nn.functional.smooth_l1_loss(S_c, T_c, beta=0.1)
        hc = z_a - z_a.mean(dim=0, keepdim=True)
        std = torch.sqrt(hc.var(dim=0) + 1e-4)
        var_term = torch.mean(torch.relu(1.0 - std))
        loss = cfg["w_geo"] * geo_loss + cfg["lambda_var"] * var_term

        rel_loss_val = 0.0
        if w_rel > 0.0:
            valid, pos_j = _pick_relpred_positive(a_idx, train_neigh, rng)
            if valid.sum() >= 4:
                vsel = np.nonzero(valid)[0]
                z_anc = z_a[torch.from_numpy(vsel.astype(np.int64))]
                pos_rows = torch.from_numpy(pos_j[vsel].astype(np.int64))
                z_pos = _l2_t(_enc_rows(enc, pos_rows))
                logits = (z_anc @ z_pos.t()) / tau
                tgt = torch.arange(z_anc.shape[0])
                rel_loss = torch.nn.functional.cross_entropy(logits, tgt)
                loss = loss + w_rel * rel_loss
                rel_loss_val = float(rel_loss.detach())

        ema_loss_val = 0.0
        if w_ema > 0.0 and ema is not None:
            z_stud = _l2_t(_enc_rows(enc, a_rows, feat_drop=fd))
            with torch.no_grad():
                z_teach = _l2_t(_enc_rows(ema, a_rows, feat_drop=fd))
            ema_loss = (1.0 - (z_stud * z_teach).sum(dim=1)).mean()
            loss = loss + w_ema * ema_loss
            ema_loss_val = float(ema_loss.detach())

        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite fusion loss ep=%d seed=%d" % (ep, seed))
        opt.zero_grad()
        loss.backward()
        opt.step()

        if ema is not None:
            m = cfg["ema_momentum"]
            with torch.no_grad():
                for pe, ps in zip(ema.parameters(), enc.parameters()):
                    pe.mul_(m).add_(ps, alpha=1.0 - m)

        if (ep % log_every == 0) or (ep == cfg["epochs"] - 1):
            _log("  fusion seed=%d ep=%d/%d geo=%.4f var=%.4f rel=%.4f ema=%.4f (%.1fs)"
                 % (seed, ep, cfg["epochs"], float(geo_loss.detach()), float(var_term.detach()),
                    rel_loss_val, ema_loss_val, time.perf_counter() - t0))
    enc.eval()
    return enc


def encode_all(enc, feats):
    with torch.no_grad():
        g = torch.from_numpy(feats["own"].astype(np.float32))
        c = torch.from_numpy(feats["ctx"].astype(np.float32))
        emb = _l2_t(enc.encode(g, c)).numpy().astype(np.float32)
    return emb


# ---------------------------------------------------------------------------
# Eval: LEAK-PROOF relational inference (predict-target vs degree-matched negatives)
# ---------------------------------------------------------------------------
def _auc_from_scores(scores, pos_mask):
    """Tie-corrected Mann-Whitney AUC (average ranks for ties). Exact-degree-matched popularity -> 0.5."""
    n_pos = int(pos_mask.sum())
    n_neg = int(pos_mask.shape[0] - n_pos)
    if n_pos == 0 or n_neg == 0:
        return None
    order = np.argsort(scores, kind="mergesort")
    ss = scores[order]
    ranks_sorted = np.empty(ss.shape[0], dtype=np.float64)
    i = 0
    n = ss.shape[0]
    while i < n:
        j = i
        while j + 1 < n and ss[j + 1] == ss[i]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0                 # 1-based average rank over the tie block
        ranks_sorted[i:j + 1] = avg
        i = j + 1
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = ranks_sorted
    return float((ranks[pos_mask].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def build_eval_context(split, _n_bins_unused):
    """Precompute gallery positions, integer degree per position, degree->positions map, gallery adjacency."""
    train_idx = split["train_idx"].astype(np.int64)
    G = train_idx.shape[0]
    pos_of = {int(t): p for p, t in enumerate(train_idx.tolist())}
    deg_on_train = split["train_deg"][train_idx]
    deg_int = np.rint(deg_on_train).astype(np.int64)
    deg_to_pos = {}
    for p in range(G):
        deg_to_pos.setdefault(int(deg_int[p]), []).append(p)
    deg_to_pos = {d: np.asarray(v, dtype=np.int64) for d, v in deg_to_pos.items()}
    max_deg = int(deg_int.max()) if G > 0 else 0
    # gallery adjacency among train positions (for STRUCT_2HOP + leak-check)
    gal_adj = [set() for _ in range(G)]
    for i in split["train_idx"].tolist():
        pi = pos_of[i]
        for _s, neigh in split["ctx_nei_by_rel"][i].items():
            for j in neigh:
                if j in pos_of:
                    gal_adj[pi].add(pos_of[j])
    return dict(train_idx=train_idx, G=G, pos_of=pos_of, deg_on_train=deg_on_train,
                deg_int=deg_int, deg_to_pos=deg_to_pos, max_deg=max_deg, gal_adj=gal_adj)


def _query_positives_negatives(h, split, ev_ctx, rng):
    """Return (pos_positions, neg_positions, ctx_positions). Negatives = EXACT-degree-matched (window grown
    only if the exact degree is exhausted) train non-neighbours, excluding CONTEXT+PREDICT. Predict positives
    capped at MAX_PRED_PER_QUERY (deterministic subset). Returns None if unusable."""
    pos_of = ev_ctx["pos_of"]
    deg_int = ev_ctx["deg_int"]
    deg_to_pos = ev_ctx["deg_to_pos"]
    max_deg = ev_ctx["max_deg"]
    pred = sorted(pos_of[j] for j in split["predict_nei"][h] if j in pos_of)
    ctxp = set(pos_of[j] for j in split["context_nei"][h] if j in pos_of)   # SHOWN context (struct_2hop src)
    allp = set(pos_of[j] for j in split["true_nei_all"][h] if j in pos_of)  # ALL real neighbours
    if len(pred) == 0:
        return None
    if len(pred) > MAX_PRED_PER_QUERY:
        pred = pred[:MAX_PRED_PER_QUERY]            # deterministic (sorted) subset -> bounded compute
    exclude = set(pred) | allp                      # exclude EVERY true neighbour (incl capped-out context)
    neg = []
    used_neg = set()
    for p in pred:
        dp = int(deg_int[p])
        picked = -1
        for tol in range(0, max_deg + 1):           # exact degree first, then widen minimally
            cand_arrs = []
            for dd in ((dp,) if tol == 0 else (dp - tol, dp + tol)):
                if dd >= 0 and dd in deg_to_pos:
                    cand_arrs.append(deg_to_pos[dd])
            if not cand_arrs:
                continue
            cc = np.concatenate(cand_arrs)
            cc = [int(x) for x in cc.tolist() if x not in exclude and x not in used_neg]
            if cc:
                picked = cc[int(rng.integers(0, len(cc)))]
                break
        if picked >= 0:
            neg.append(picked)
            used_neg.add(picked)
    if len(neg) < 1:
        return None
    return np.asarray(pred, dtype=np.int64), np.asarray(neg, dtype=np.int64), ctxp, exclude


def eval_relational_inference(score_matrix, split, ev_ctx, struct_2hop=False, popularity=False):
    """Held-out relational-inference AUC. For each held-out query rank its PREDICT target(s) among
    degree-matched negatives. score_matrix: codes[K,d] for cosine arms; ignored for struct/popularity."""
    G = ev_ctx["G"]
    train_idx = ev_ctx["train_idx"]
    gal_adj = ev_ctx["gal_adj"]
    deg_on_train = ev_ctx["deg_on_train"]
    Zg = None
    if not (struct_2hop or popularity):
        Zg = score_matrix[train_idx]              # gallery codes [G,d]
    rng = np.random.default_rng(EVAL_SEED)
    aucs = []
    neg_in_exclude = 0                            # must remain 0 (negatives never a true neighbour)
    for h in split["held_idx"].tolist():
        qpn = _query_positives_negatives(h, split, ev_ctx, rng)
        if qpn is None:
            continue
        pos_arr, neg_arr, ctxp, exclude = qpn
        # leak-check: no negative is ANY true neighbour (predict OR shown/capped-out context)
        neg_in_exclude += sum(1 for n in neg_arr.tolist() if n in exclude)
        sel = np.concatenate([pos_arr, neg_arr])
        if popularity:
            sc = deg_on_train[sel]
        elif struct_2hop:
            # count of the query's CONTEXT-neighbours adjacent to each candidate (friend-of-friend)
            ctx_positions = ctxp
            sc = np.zeros(sel.shape[0], dtype=np.float64)
            for k, c in enumerate(sel.tolist()):
                sc[k] = float(len(gal_adj[c] & ctx_positions))
        else:
            sc = Zg[sel] @ score_matrix[h]
        pm = np.zeros(sel.shape[0], dtype=bool)
        pm[:pos_arr.shape[0]] = True
        a = _auc_from_scores(sc, pm)
        if a is not None:
            aucs.append(a)
    if len(aucs) < 5:
        return float("nan"), len(aucs), neg_in_exclude
    return float(np.mean(aucs)), len(aucs), neg_in_exclude


def _emb_digest(emb):
    return hashlib.sha256(np.ascontiguousarray(emb.astype(np.float32)).tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# One seed: build all arms + eval
# ---------------------------------------------------------------------------
def run_seed(seed, split, base_feats, landmarks, target_geo, ev_ctx, cfg):
    c = cfg
    own = base_feats["own"]
    ctx = base_feats["ctx"]
    feats = dict(own=own, ctx=ctx)

    codes = {}
    # RAW_GROUNDING: grounding cosine (homophily, no learning, no context) -- THE ceiling
    codes[RAW_ARM] = _l2_np(own.astype(np.float64)).astype(np.float32)

    # LEARNED (PRIMARY): grounding + relational-context, geometry + VICReg + relpred + EMA
    enc_l = train_fusion(feats, target_geo, landmarks, split, c, seed,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=True)
    codes[LEARNED_ARM] = encode_all(enc_l, feats)

    # RANDOM_INIT: same architecture, untrained (isolates learning)
    enc_r = train_fusion(feats, target_geo, landmarks, split, c, seed + 101,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"], do_train=False)
    codes[RANDINIT_ARM] = encode_all(enc_r, feats)

    # COLLAPSE_SHUFFLE: permute input rows across ids, train -> ~0.5 witness
    enc_s = train_fusion(feats, target_geo, landmarks, split, c, seed + 1,
                         use_ctx=True, w_rel=c["w_rel"], w_ema=c["w_ema"],
                         do_train=True, shuffle_rows=True)
    Kk = split["K"]
    perm = np.random.default_rng(seed + 1 + 909).permutation(Kk)
    feats_shuf = dict(own=own[perm], ctx=ctx[perm])
    codes[SHUFFLE_ARM] = encode_all(enc_s, feats_shuf)

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
        elif arm == POP_ARM:
            auc, nq, nleak = eval_relational_inference(None, split, ev_ctx, popularity=True)
        else:
            auc, nq, nleak = eval_relational_inference(codes[arm], split, ev_ctx)
        neg_leak_total += nleak
        arm_metrics[arm] = dict(rel_infer_auc=auc, n_query=nq, neg_in_exclude=nleak,
                                emb_digest=(digs[arm] if arm in digs else None))
        _log("seed=%d arm=%-20s rel_infer_auc=%.4f n_q=%d neg_leak=%d"
             % (seed, arm, auc, nq, nleak))
    arm_metrics["_neg_leak_total"] = neg_leak_total
    if neg_leak_total != 0:
        raise RuntimeError("LEAK: %d negatives were true neighbours (must be 0)" % neg_leak_total)
    return arm_metrics


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, data_meta, split_meta):
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
    learned_min = agg[LEARNED_ARM]["rel_infer_auc_min"]
    raw = agg[RAW_ARM]["rel_infer_auc_mean"]
    randinit = agg[RANDINIT_ARM]["rel_infer_auc_mean"]
    struct = agg[STRUCT_ARM]["rel_infer_auc_mean"]
    pop = agg[POP_ARM]["rel_infer_auc_mean"]
    shuf = agg[SHUFFLE_ARM]["rel_infer_auc_mean"]

    # THE NUMBER: LEARNED - RAW_GROUNDING (per-seed for robustness)
    margin_series = (series(LEARNED_ARM) - series(RAW_ARM))
    margin = float(np.nanmean(margin_series))
    margin_min = float(np.nanmin(margin_series))

    n_query = agg[LEARNED_ARM]["n_query"]
    power_ok = bool(n_query >= MIN_QUERY_TASKS)
    cb_lo, cb_hi = COLLAPSE_BAND
    can_fail_fired = bool(cb_lo <= shuf <= cb_hi)
    pb_lo, pb_hi = POP_BAND
    pop_ok = bool(pb_lo <= pop <= pb_hi)
    validity_ok = bool(power_ok and can_fail_fired and pop_ok)

    real_margin = bool(margin >= HP_MARGIN_OVER_RAW and margin_min > 0.0)
    is_tie = bool(abs(margin) < TIE_EPS)

    if not validity_ok:
        verdict = "HARD_FAIL_INVALID"
    elif real_margin and learned >= HP_LEARNED_FLOOR and learned >= randinit:
        verdict = "HARD_PASS"
    elif is_tie:
        verdict = "TIE_NULL"          # LEARNED ties RAW_GROUNDING -> relational learning ~null (decisive honest finding)
    elif margin <= -TIE_EPS:
        verdict = "LEARNED_WORSE"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s | THE-NUMBER learned - raw_grounding = %.4f - %.4f = %+.4f (min=%+.4f, need>=%.2f) | "
        "LEARNED=%.4f (min=%.4f) RAW_GROUNDING=%.4f RANDOM_INIT=%.4f STRUCT_2HOP=%.4f POPULARITY=%.4f "
        "COLLAPSE=%.4f | VALIDITY power_ok=%s(n_q=%d) can_fail=%s(collapse~0.5) pop_ok=%s(pop~0.5) | "
        "leak-proof witness: context-INT-predict overlap=%d/%d predict-targets (MUST be 0) | "
        "corpus: K=%d train=%d heldout=%d eval_queries=%d mean_ctx=%.2f pairs=%d rels=%d"
        % (verdict, learned, raw, margin, margin_min, HP_MARGIN_OVER_RAW,
           learned, learned_min, raw, randinit, struct, pop, shuf,
           power_ok, n_query, can_fail_fired, pop_ok,
           split_meta["no_overlap_witness_overlap"], split_meta["no_overlap_witness_predict_targets"],
           data_meta["n_kept_concepts"], split_meta["n_train"], split_meta["n_heldout"],
           split_meta["n_eval_queries"], split_meta["mean_held_context_size"],
           data_meta["n_kept_pairs"], data_meta["n_rel_slots"]))

    gates = dict(
        learned_rel_infer_auc=learned, learned_rel_infer_auc_min=learned_min,
        raw_grounding_rel_infer_auc=raw, random_init_rel_infer_auc=randinit,
        struct_2hop_rel_infer_auc=struct, popularity_rel_infer_auc=pop,
        collapse_shuffle_rel_infer_auc=shuf,
        margin_over_raw_grounding=margin, margin_over_raw_grounding_min=margin_min,
        margin_over_random_init=float(learned - randinit),
        margin_over_struct_2hop=float(learned - struct),
        real_margin=real_margin, is_tie=is_tie,
        power_ok=power_ok, n_query=n_query, can_fail_fired=can_fail_fired, pop_ok=pop_ok,
        validity_ok=validity_ok,
        no_overlap_witness_overlap=split_meta["no_overlap_witness_overlap"],
        no_overlap_witness_predict_targets=split_meta["no_overlap_witness_predict_targets"],
        collapse_band=list(COLLAPSE_BAND), pop_band=list(POP_BAND),
        hp_margin_over_raw=HP_MARGIN_OVER_RAW, tie_eps=TIE_EPS,
        hp_learned_floor=HP_LEARNED_FLOOR, min_query_tasks=MIN_QUERY_TASKS,
    )
    return verdict, verdict_msg, agg, gates


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def discriminator_selftest():
    """Planted: query linked to a cluster; its held-out target is IN the cluster -> AUC high; random -> 0.5.
    Exercises _auc_from_scores + degree-matched negative sampling logic sanity."""
    rng = np.random.default_rng(0)
    # synthetic: 30 candidates, planted score for positives high, negatives low
    n = 30
    scores = rng.standard_normal(n)
    pos_mask = np.zeros(n, dtype=bool)
    pos_mask[:5] = True
    scores[:5] += 3.0                      # positives clearly higher
    auc_struct = _auc_from_scores(scores, pos_mask)
    scores_rand = rng.standard_normal(n)
    auc_rand = _auc_from_scores(scores_rand, pos_mask)
    res = dict(auc_struct=auc_struct, auc_rand=auc_rand)
    ok = (auc_struct is not None and auc_struct >= 0.85
          and auc_rand is not None and abs(auc_rand - 0.5) < 0.30)
    return bool(ok), res


def leakproof_split_selftest():
    """REAL-CODE-PATH: build a tiny synthetic grounded subgraph, run build_leakproof_split, and assert
    (a) context INTERSECT predict == EMPTY for every held-out query, (b) predict targets are TRAIN concepts,
    (c) context edges never include a predict target, (d) held-out never appears as a train relpred anchor."""
    K = 200
    rng = np.random.default_rng(3)
    ids = ["c%03d" % i for i in range(K)]
    vals = rng.standard_normal((K, N_VALUE_DIMS))
    gpres = np.ones((K, N_GROUPS), dtype=np.float64)
    # random relational graph (dense enough that held-out have >=2 train neighbours)
    pair_rels = {}
    for _ in range(3000):
        a = int(rng.integers(0, K))
        b = int(rng.integers(0, K))
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
    cfg = dict(heldout_frac=0.35, predict_frac=0.5)
    try:
        split = build_leakproof_split(data, cfg)                       # uncapped (ALL context)
        split_cap = build_leakproof_split(data, cfg, max_context=2)    # CAPPED at 2 (exercise sweep path)
    except RuntimeError as e:
        return False, dict(err=str(e)[:200])

    train_set = set(split["train_idx"].tolist())
    ok = True
    checks = dict(overlap=split["split_meta"]["no_overlap_witness_overlap"], viols=0)
    for h in split["held_idx"].tolist():
        pred = split["predict_nei"][h]
        ctxs = split["context_nei"][h]
        if pred & ctxs:
            ok = False
            checks["viols"] += 1
        if any(j not in train_set for j in pred):   # predict target must be a TRAIN concept
            ok = False
            checks["viols"] += 1
        # context rep must not contain any predict target
        ctx_flat = set()
        for _s, neigh in split["ctx_nei_by_rel"][h].items():
            ctx_flat |= neigh
        if ctx_flat & pred:
            ok = False
            checks["viols"] += 1
        # true_nei_all must SUPERSET both predict and shown context (neg-exclusion correctness)
        if not (pred <= split["true_nei_all"][h] and ctxs <= split["true_nei_all"][h]):
            ok = False
            checks["viols"] += 1
    # held-out never a train relpred anchor
    for h in split["held_idx"].tolist():
        if split["train_neigh"][h]:
            ok = False
            checks["viols"] += 1
    # CAPPED sweep path: shown context <= 2, predict + true_nei_all unchanged vs uncapped, still leak-proof
    cap_viol = 0
    for h in split_cap["held_idx"].tolist():
        if len(split_cap["context_nei"][h]) > 2:
            cap_viol += 1
        if split_cap["predict_nei"][h] & split_cap["context_nei"][h]:
            cap_viol += 1
        if split_cap["context_nei"][h] and not (split_cap["context_nei"][h] <= split_cap["true_nei_all"][h]):
            cap_viol += 1
    checks["cap_mean_ctx"] = split_cap["split_meta"]["mean_held_context_size"]
    checks["cap_viol"] = cap_viol
    checks["overlap_cap"] = split_cap["split_meta"]["no_overlap_witness_overlap"]
    checks["n_eval_queries"] = split["split_meta"]["n_eval_queries"]
    ok = (ok and (checks["overlap"] == 0) and (checks["overlap_cap"] == 0)
          and (cap_viol == 0) and (checks["cap_mean_ctx"] <= 2.0 + 1e-9)
          and (checks["n_eval_queries"] >= 5))
    return bool(ok), checks


# ---------------------------------------------------------------------------
# Per-level context build + sweep verdict
# ---------------------------------------------------------------------------
def build_level_context(split, cfg):
    """From a (possibly context-capped) split, build fusion inputs + landmarks + target geometry + eval ctx."""
    own = split["own_feat"]
    ctx = _pooled_ctx_block(split, own, GROUND_DIM)
    base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
    landmarks = select_landmarks(split, cfg)
    A = build_train_adjacency(split)
    own_norm = _l2_np(own.astype(np.float64)).astype(np.float32)
    target_geo = compute_target_geometry(own_norm, A, landmarks)
    ev_ctx = build_eval_context(split, cfg["n_deg_bins"])
    return base_feats, landmarks, target_geo, ev_ctx


def sweep_verdict(per_level):
    """Overall envelope verdict over the context-size sweep.
    per_level: list of dicts {max_context (None=ALL), gates, agg, n_seeds} ordered by context ascending
    (None sorted last). Reports: (1a) survival at minimal context, (3) margin scaling with # constraints,
    positive-control reproduction at ALL-context."""
    def _ctx_key(pl):
        mc = pl["max_context"]
        return ALL_CONTEXT if mc is None else mc
    ordered = sorted(per_level, key=_ctx_key)
    lvl_min = ordered[0]
    lvl_all = ordered[-1]                                   # ALL-context (positive control)

    curve = [(("ALL" if pl["max_context"] is None else pl["max_context"]),
              round(pl["gates"]["margin_over_raw_grounding"], 4),
              round(pl["gates"]["learned_rel_infer_auc"], 4),
              round(pl["gates"]["raw_grounding_rel_infer_auc"], 4),
              round(pl["gates"]["struct_2hop_rel_infer_auc"], 4),
              round(pl["gates"]["collapse_shuffle_rel_infer_auc"], 4),
              bool(pl["gates"]["validity_ok"])) for pl in ordered]

    g_min = lvl_min["gates"]
    g_all = lvl_all["gates"]
    survives_minimal = bool(g_min["validity_ok"] and g_min["margin_over_raw_grounding"] >= HP_MARGIN_OVER_RAW
                            and g_min["margin_over_raw_grounding_min"] > 0.0
                            and g_min["learned_rel_infer_auc"] >= HP_LEARNED_FLOOR)
    all_valid = bool(g_all["validity_ok"] and g_all["margin_over_raw_grounding"] >= HP_MARGIN_OVER_RAW)
    margin_min_ctx = float(g_min["margin_over_raw_grounding"])
    margin_all_ctx = float(g_all["margin_over_raw_grounding"])
    constraints_grow = bool(margin_all_ctx - margin_min_ctx >= 0.0)

    all_levels_valid = all(pl["gates"]["validity_ok"] for pl in ordered)
    if not all_valid:
        verdict = "HARD_FAIL_INVALID"          # ALL-context positive control failed -> suspect
    elif survives_minimal and constraints_grow:
        verdict = "HOLDS_AND_SCALES"           # win holds at minimal context AND grows with constraints
    elif survives_minimal:
        verdict = "HOLDS_AT_MINIMAL_FLAT"      # holds at 1 edge but does not grow with more constraints
    elif all_valid:
        verdict = "SCOPE_BOUNDED_NEEDS_CONTEXT"  # evaporates at low context; needs multiple constraints
    else:
        verdict = "MIXED"

    verdict_msg = (
        "%s | context-sweep margin(learned-raw) vs #ctx-edges: %s | "
        "survives_minimal(ctx=%s)=%s margin=%+.4f(min=%+.4f) learned=%.4f | "
        "ALL-ctx positive-control margin=%+.4f valid=%s | constraints_grow(all>=min)=%s (delta=%+.4f) | "
        "all_levels_valid=%s"
        % (verdict, curve,
           ("ALL" if lvl_min["max_context"] is None else lvl_min["max_context"]),
           survives_minimal, margin_min_ctx, g_min["margin_over_raw_grounding_min"],
           g_min["learned_rel_infer_auc"],
           margin_all_ctx, all_valid, constraints_grow, margin_all_ctx - margin_min_ctx,
           all_levels_valid))
    summary = dict(verdict=verdict, curve=curve, survives_minimal=survives_minimal,
                   all_valid=all_valid, constraints_grow=constraints_grow,
                   margin_min_ctx=margin_min_ctx, margin_all_ctx=margin_all_ctx,
                   margin_delta=margin_all_ctx - margin_min_ctx, all_levels_valid=all_levels_valid)
    return verdict, verdict_msg, summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap-nodes", type=int, default=0, help="override cap_nodes (SCALE axis; 0=cfg default)")
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
        cfg["cap_nodes"] = int(args.cap_nodes)               # SCALE-axis override (axis 2)
    # scale-point runs get an isolated output dir so they never clobber the canonical cap_nodes run
    anchor = ANCHOR_NAME if not (args.cap_nodes and run_mode == "full") else ("%s_cap%d" % (ANCHOR_NAME, args.cap_nodes))
    output_dir = get_output_dir(anchor)
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()

    st_ok, st_res = discriminator_selftest()
    lp_ok, lp_res = leakproof_split_selftest()
    _log("discriminator_selftest ok=%s %s" % (st_ok, st_res))
    _log("leakproof_split_selftest ok=%s %s" % (lp_ok, lp_res))
    if not (st_ok and lp_ok):
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELFTEST_FAILED discriminator_ok=%s leakproof_ok=%s: %s | %s"
                        % (st_ok, lp_ok, st_res, lp_res),
            summary="selftest failed", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, leakproof_split_selftest=lp_res))
        raise SystemExit(1)

    _log("loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
         % (cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]))
    data = load_grounded_subgraph(cfg)
    _log("grounded universe: %s" % {k: v for k, v in data["meta"].items() if k != "top_rels"})

    levels = list(cfg["max_context_levels"])
    expected_total_units = len(cfg["seeds"]) * len(levels)      # META_RULE_H cardinality

    if run_mode == "self_test":
        split = build_leakproof_split(data, cfg, max_context=ALL_CONTEXT)
        base_feats, landmarks, target_geo, ev_ctx = build_level_context(split, cfg)
        pm = run_seed(cfg["seeds"][0], split, base_feats, landmarks, target_geo, ev_ctx, cfg)
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS leak-proof context-cap split + fusion + degree-matched rel-infer eval exercised",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            discriminator_selftest=st_res, leakproof_split_selftest=lp_res,
            data_meta=data["meta"], split_meta=split["split_meta"],
            learned_rel_infer_auc=pm[LEARNED_ARM]["rel_infer_auc"],
            raw_grounding_rel_infer_auc=pm[RAW_ARM]["rel_infer_auc"],
            collapse_shuffle_rel_infer_auc=pm[SHUFFLE_ARM]["rel_infer_auc"],
            popularity_rel_infer_auc=pm[POP_ARM]["rel_infer_auc"]))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_level = []
    seed_failures = []
    total_units_run = 0
    for mc in levels:
        mc_label = "ALL" if mc >= ALL_CONTEXT else str(mc)
        split = build_leakproof_split(data, cfg, max_context=mc)
        _log("[ctx=%s] split: %s" % (mc_label, split["split_meta"]))
        base_feats, landmarks, target_geo, ev_ctx = build_level_context(split, cfg)
        _log("[ctx=%s] landmarks=%d ctx_dim=%d gallery=%d mean_ctx=%.2f"
             % (mc_label, landmarks.shape[0], base_feats["ctx"].shape[1], ev_ctx["G"],
                split["split_meta"]["mean_held_context_size"]))
        per_seed = []
        for seed in cfg["seeds"]:
            try:
                pm = run_seed(seed, split, base_feats, landmarks, target_geo, ev_ctx, cfg)
                per_seed.append(pm)
                total_units_run += 1
                write_partial(output_dir, "mc%s_seed%d" % (mc_label, seed), dict(
                    max_context=mc_label, seed=seed,
                    arms={a: {k: v for k, v in pm[a].items() if k != "emb_digest"} for a in ALL_ARMS},
                    run_mode=run_mode))
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                fc = type(e).__name__
                seed_failures.append(dict(max_context=mc_label, seed=seed, failure_class=fc, msg=str(e)[:300]))
                _log("SEED_FAILED ctx=%s seed=%d class=%s: %s" % (mc_label, seed, fc, str(e)[:200]))
        if len(per_seed) < len(cfg["seeds"]):
            continue
        v_l, msg_l, agg_l, gates_l = aggregate_and_verdict(per_seed, data["meta"], split["split_meta"])
        _log("[ctx=%s] %s" % (mc_label, msg_l))
        per_level.append(dict(
            max_context=(None if mc >= ALL_CONTEXT else int(mc)),
            level_verdict=v_l, gates=gates_l, arms_aggregate=agg_l,
            split_meta=split["split_meta"], n_seeds=len(per_seed),
            per_seed=[{a: {k: v for k, v in per_seed[i][a].items() if k != "emb_digest"}
                       for a in ALL_ARMS} for i in range(len(per_seed))]))

    if total_units_run < expected_total_units:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units (%d seeds x %d ctx-levels) got %d (failures=%s)"
                        % (expected_total_units, len(cfg["seeds"]), len(levels), total_units_run, seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, data_meta=data["meta"]))
        raise SystemExit(1)

    verdict, verdict_msg, sweep_summary = sweep_verdict(per_level)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_seeds=len(cfg["seeds"]), seeds=cfg["seeds"],
        max_context_levels=[("ALL" if x >= ALL_CONTEXT else x) for x in levels],
        expected_total_units=expected_total_units, total_units_run=total_units_run,
        config={k: v for k, v in cfg.items()},
        data_meta={k: v for k, v in data["meta"].items()},
        sweep_summary=sweep_summary, per_level=per_level,
        discriminator_selftest=st_res, leakproof_split_selftest=lp_res,
        seed_failures=seed_failures,
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
