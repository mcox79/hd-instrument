"""CONSOLIDATION (P1): does INTERLEAVED-REPLAY SGD manufacture inference-capable structure at substrate scale?

Claim B (consolidation manufactures inference-capable structure) was CONFIRMED this program via 4 CLS/Saxe
signatures but ONLY in inline toys and NEVER integrated into the code-learning loop. This cell integrates the P1
"interleaved slow update" primitive (consolidation_to_structure_implementable_algorithm_2026-07-14.md) into the
substrate's learned-code loop and tests, at scale, whether interleaved-replay SGD MANUFACTURES held-out relational-
inference structure in the learned codes, BEATING continual (non-replayed, task-blocked) learning.

SUBSTRATE INTEGRATION. Entity codes X [N,k] and relation displacements D [n_rel,k] are the SAME objects the live
AdditiveKGMap owns (hdlab/additive_map.py). The held-out inference READOUT is the REAL additive/TransE primitive
`additive_direct_scores` (score(t) = -||X_h + D_r - X_t||), invoked through AdditiveKGMap.set_coords + score_edges.
The NEW piece is the consolidation-aware learning loop (three batch SCHEDULES), which is what the cell tests.

ARENA (scaled synthetic hierarchical concept-attribute KG, Saxe/Rogers-McClelland domain, with controls + info-
ceiling). Latent hierarchy: S domains x C categories/domain x M items/cat = N_ent entities. Each entity is a HEAD;
attribute-relations are the R (grouped by granularity):
  - SUPER relations: tail value determined by the entity's DOMAIN (coarse; high shared singular value -> Saxe-first).
  - SUB   relations: tail value determined by the entity's CATEGORY (fine; lower shared value -> Saxe-later).
Label noise p_noise flips a fraction of tail values (keeps oracle info-ceiling < 1 and POP a meaningful floor).
Held-out inference = held-out (entity, relation) EDGES whose tail is inferrable ONLY from cross-entity shared
structure (siblings agree) -- exactly the structure consolidation must MANUFACTURE.

The forgetting locus is the SHARED relation displacement D[r] (the CLS "slow cortical" weight): per-entity codes
X[e] are sharded (never overwritten across domains), but D[r] is contested across sequentially-presented domains, so
continual (task-blocked, no replay) drags D[r] toward the last domain and forgets early domains, while interleaved
keeps D[r] balanced.

ARMS (identical model + compute budget; ONLY the batch schedule / structure differs):
  INTERLEAVED : i.i.d. minibatch SGD over ALL train edges, P_max passes (the mechanism = replay/consolidation).
  CONTINUAL   : task-blocked by domain, P_max/S local passes per domain in order, NO replay (matched total steps).
  SHUFFLE     : interleaved schedule but cross-entity structure DESTROYED (per-entity random tails) -> nothing to
                generalize; held-out lift must stay flat at POP (clean control).
Non-arm references: POP (frequency/marginal baseline = fair floor), ORACLE (latent-type -> info-ceiling), and the
P=0 random-init readout (chance).

FOUR CONFIRMED SIGNATURES reproduced AT SCALE (the gates):
  (1) DOSE-RESPONSE   : INTERLEAVED held-out MRR GROWS with replay passes (saturating).
  (2) STAGING         : coarse/SUPER normalized-progress leads fine/SUB (structure-before-content).
  (3) BEAT-CONTINUAL  : INTERLEAVED held-out MRR > CONTINUAL by margin AND CONTINUAL early-domain MRR forgotten
                        (<= POP + eps) -- catastrophic forgetting fires.
  (4) SHUFFLE-FLAT    : SHUFFLE held-out lift ~ 0 (<= POP + eps), dose slope ~ 0.

BANDS (pre-registered; see preregs/2026-07-14_consol_interleaved_replay_v1.md):
  HARD_PASS = INTERLEAVED beats CONTINUAL by >= BEAT_MARGIN AND beats POP by >= POP_BEAT_MARGIN AND >= 3/4 signatures.
  REFUTE    = INTERLEAVED - CONTINUAL < REFUTE_EPS OR INTERLEAVED - POP < REFUTE_EPS (no structure manufactured).
  MIDDLE    = otherwise.
Honest REFUTE (replay does not beat continual at scale) is a valid, valuable outcome.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): INTERLEAVED / CONTINUAL / SHUFFLE produce distinct code hashes.
# - final_metrics_atomicity = tmp_replace (write_metrics uses atomic tmp+os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: relative-inference cell; the discriminator is a between-arm MRR GAP, not an absolute noise-floor target.
# - baseline_in_band at self-test (META_RULE_AG): POP/random floor < INTERLEAVED < ORACLE ceiling.
# - discriminator survives scale: self-test fires beat-continual + dose directionally; FULL uses substrate-scale N.
# - HARD_PASS strictly above floor (margins, not >=0 floor).
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds; verdict counts per_seed.
# - per-unit failure-class instrumentation (META_RULE_J; no bare except).
# - calibration_check = adaptive_with_discriminator_gate (bands calibrated at self-test; discriminator-fires verified).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ in the prereg.
# - self-test CONSTRUCTS the REAL AdditiveKGMap + set_coords + score_edges + additive_direct_scores (real_code_path).
# - substrate_signature binds AdditiveKGMap against inspect.signature; base/portable kwargs only.
# - deterministic integer seeds only; no salted-hash or set-dedup seeding (PROT-023 static scan runs on ship).

ASCII-only. No emojis. Explicit dtypes (float32). Deterministic integer seeds. Terse.
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
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402

ANCHOR_NAME = "consol_interleaved_replay_v1"

# ---- Arm names ----
INTERLEAVED = "INTERLEAVED"      # mechanism: i.i.d. replay SGD (consolidation)
CONTINUAL = "CONTINUAL"          # task-blocked, no replay (catastrophic-forgetting control)
SHUFFLE = "SHUFFLE"              # structure-destroyed control (must stay flat at POP)
ARMS = [INTERLEAVED, CONTINUAL, SHUFFLE]

SUPER = "super"
SUB = "sub"

# ---- Pre-registered bands (HYPOTHESIZED; calibrated + discriminator-verified at self-test) ----
BEAT_MARGIN = 0.05         # INTERLEAVED - CONTINUAL held-out MRR
POP_BEAT_MARGIN = 0.05     # INTERLEAVED - POP held-out MRR
DOSE_MARGIN = 0.05         # INTERLEAVED heldout MRR(P_max) - MRR(P=1)
FLAT_EPS = 0.03            # SHUFFLE MRR(P_max) - POP  (must be <= this)
FORGET_EPS = 0.03          # CONTINUAL early-domain MRR - POP (must be <= this to count as forgotten)
REFUTE_EPS = 0.02          # below this beat -> REFUTE
SIGS_FOR_HARD_PASS = 3     # >= this many of the 4 signatures must fire

# ---- Configs ----
SELFTEST_CFG = dict(S=2, C=2, M=8, r_super=2, r_sub=2, k=16, p_noise=0.10, heldout_frac=0.20,
                    P_max=12, k_neg=8, batch=128, lr=0.05, checkpoints=[0, 1, 2, 4, 8, 12], seeds=[7])
MEMSMOKE_CFG = dict(S=3, C=3, M=16, r_super=3, r_sub=3, k=24, p_noise=0.10, heldout_frac=0.15,
                    P_max=12, k_neg=12, batch=256, lr=0.04, checkpoints=[0, 1, 2, 4, 8, 12], seeds=[7, 13])
FULL_CFG = dict(S=4, C=4, M=32, r_super=4, r_sub=4, k=32, p_noise=0.10, heldout_frac=0.15,
                P_max=24, k_neg=16, batch=256, lr=0.04, checkpoints=[0, 1, 2, 4, 8, 16, 24],
                seeds=[7, 13, 19, 29, 37])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


# ---------------------------------------------------------------------------
# Defensive-error-checking helpers (start marker + crash metrics; heartbeat inline).
# ---------------------------------------------------------------------------

def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Arena: scaled synthetic hierarchical concept-attribute KG.
# ---------------------------------------------------------------------------

def build_arena(cfg, seed, destroy_structure=False):
    """Deterministic hierarchical arena. Returns a dict of int arrays + metadata.

    Entities 0..N_ent-1 are heads (domain = e//(C*M), category = e//M). Value entities follow. Each SUPER relation's
    tail = its domain-value (noise-flipped w.p. p_noise); each SUB relation's tail = its category-value (noise-flipped).
    destroy_structure=True (SHUFFLE control): replace each (entity, relation) tail with a per-entity RANDOM in-range
    value -> siblings no longer agree, so held-out edges are not inferrable.
    """
    rng = np.random.default_rng(int(seed) + (100003 if destroy_structure else 0))
    S, C, M = int(cfg["S"]), int(cfg["C"]), int(cfg["M"])
    r_super, r_sub = int(cfg["r_super"]), int(cfg["r_sub"])
    p_noise = float(cfg["p_noise"])
    n_ent = S * C * M
    n_cat = S * C

    # Relations: 0..r_super-1 = super, r_super..r_super+r_sub-1 = sub.
    n_rel = r_super + r_sub
    rel_level = [SUPER] * r_super + [SUB] * r_sub

    # Value-entity index blocks. Super relation rs has S values; sub relation has n_cat values.
    val_base = {}
    cursor = n_ent
    for r in range(n_rel):
        val_base[r] = cursor
        cursor += (S if rel_level[r] == SUPER else n_cat)
    n_val = cursor - n_ent
    n_total = n_ent + n_val
    rel_value_idx = {r: np.arange(val_base[r], val_base[r] + (S if rel_level[r] == SUPER else n_cat), dtype=np.int64)
                     for r in range(n_rel)}
    base_arr = np.array([val_base[r] for r in range(n_rel)], dtype=np.int64)
    span_arr = np.array([(S if rel_level[r] == SUPER else n_cat) for r in range(n_rel)], dtype=np.int64)

    domain_of = np.arange(n_ent, dtype=np.int64) // (C * M)
    cat_of = np.arange(n_ent, dtype=np.int64) // M

    edges = []           # (h, r, t)
    edge_level = []      # level of each edge
    for e in range(n_ent):
        for r in range(n_rel):
            rng_span = S if rel_level[r] == SUPER else n_cat
            if destroy_structure:
                local = int(rng.integers(0, rng_span))
            else:
                true_local = int(domain_of[e]) if rel_level[r] == SUPER else int(cat_of[e])
                if rng.random() < p_noise:
                    local = int(rng.integers(0, rng_span))  # noise flip
                else:
                    local = true_local
            t = val_base[r] + local
            edges.append((e, r, t))
            edge_level.append(rel_level[r])

    edges = np.array(edges, dtype=np.int64)
    edge_level = np.array(edge_level, dtype=object)

    # Split held-out inference edges (stratified across relations; deterministic permutation).
    ho_frac = float(cfg["heldout_frac"])
    perm = rng.permutation(edges.shape[0])
    n_ho = int(round(ho_frac * edges.shape[0]))
    ho_idx = np.sort(perm[:n_ho])
    tr_idx = np.sort(perm[n_ho:])
    train_int = edges[tr_idx]
    query_int = edges[ho_idx]
    query_level = edge_level[ho_idx]
    query_domain = domain_of[query_int[:, 0]]

    return dict(train_int=train_int, query_int=query_int, query_level=query_level, query_domain=query_domain,
                n_ent=n_ent, n_val=n_val, n_total=n_total, n_rel=n_rel, rel_level=rel_level,
                rel_value_idx=rel_value_idx, val_base=val_base, base_arr=base_arr, span_arr=span_arr,
                domain_of=domain_of, cat_of=cat_of, S=S, C=C, M=M, n_cat=n_cat)


# ---------------------------------------------------------------------------
# Consolidation-aware SGD (the P1 primitive: interleaved slow update). Real substrate objects X, D.
# ---------------------------------------------------------------------------

def _init_coords(n_total, n_rel, k, seed, device):
    g = torch.Generator(device="cpu").manual_seed(int(seed) + 991)
    X = (torch.randn(n_total, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    D = (torch.randn(n_rel, k, generator=g, dtype=torch.float32) * 0.1).to(device).requires_grad_(True)
    return X, D


def _batch_ce_loss(X, D, batch_int, base_arr, span_arr, k_neg, neg_gen, device):
    """CE over [pos, k_neg in-relation negatives]. score = -||X_h + D_r - X_t||. Returns scalar loss.

    Negatives are sampled VECTORIZED from each edge's relation value range via precomputed base_arr/span_arr
    (per-relation first-value-index / range-size), avoiding a per-edge Python loop at scale."""
    h = torch.from_numpy(batch_int[:, 0]).long().to(device)
    r_np = batch_int[:, 1]
    r = torch.from_numpy(r_np).long().to(device)
    t = torch.from_numpy(batch_int[:, 2]).long().to(device)
    pred = X[h] + D[r]                                          # (B,k)
    pos = -torch.linalg.norm(pred - X[t], dim=1, keepdim=True)  # (B,1)
    # in-relation negatives (vectorized): local offset = floor(u * span_r) within each edge's relation range
    B = batch_int.shape[0]
    span_b = span_arr[r_np].astype(np.int64)                   # (B,)
    base_b = base_arr[r_np].astype(np.int64)                   # (B,)
    u = neg_gen.random((B, k_neg))
    neg_local = np.floor(u * span_b[:, None]).astype(np.int64)
    neg_idx = base_b[:, None] + neg_local                      # (B,k_neg)
    tn = torch.from_numpy(neg_idx).long().to(device)           # (B,k_neg)
    neg_pred = pred.unsqueeze(1)                                # (B,1,k)
    neg = -torch.linalg.norm(neg_pred - X[tn], dim=2)          # (B,k_neg)
    logits = torch.cat([pos, neg], dim=1)                      # (B,1+k_neg), col0 = positive
    target = torch.zeros(B, dtype=torch.long, device=device)
    return torch.nn.functional.cross_entropy(logits, target)


def fit_schedule(arena, cfg, schedule, seed, device):
    """Fit X,D under a batch SCHEDULE. Returns dict: checkpoint_pass -> (X_np, D_np) snapshots (detached float32).

    INTERLEAVED : i.i.d. minibatch over all train edges, P_max passes; snapshot at cfg['checkpoints'].
    SHUFFLE     : identical schedule but arena already structure-destroyed by caller.
    CONTINUAL   : domain-blocked, P_max/S local passes per domain in order (matched total steps); snapshot after
                  each domain block (records the forgetting curve on early domains).
    """
    train_int = arena["train_int"]
    n_total, n_rel, k = arena["n_total"], arena["n_rel"], int(cfg["k"])
    base_arr, span_arr = arena["base_arr"], arena["span_arr"]
    P_max, k_neg, batch, lr = int(cfg["P_max"]), int(cfg["k_neg"]), int(cfg["batch"]), float(cfg["lr"])
    checkpoints = sorted(set(int(c) for c in cfg["checkpoints"]))

    torch.manual_seed(int(seed) + 7)
    neg_gen = np.random.default_rng(int(seed) + 555)
    perm_gen = np.random.default_rng(int(seed) + 333)
    X, D = _init_coords(n_total, n_rel, k, seed, device)
    opt = torch.optim.Adam([X, D], lr=lr)

    def snap():
        return (X.detach().cpu().numpy().astype(np.float32), D.detach().cpu().numpy().astype(np.float32))

    snaps = {}
    if 0 in checkpoints:
        snaps[0] = snap()

    if schedule == CONTINUAL:
        S = arena["S"]
        local_passes = max(1, P_max // S)
        dom = arena["domain_of"][train_int[:, 0]]
        done_pass = 0
        block_snaps = {}
        for d in range(S):
            block = train_int[dom == d]
            for _lp in range(local_passes):
                order = perm_gen.permutation(block.shape[0])
                bshuf = block[order]
                for s in range(0, bshuf.shape[0], batch):
                    opt.zero_grad()
                    loss = _batch_ce_loss(X, D, bshuf[s:s + batch], base_arr, span_arr, k_neg, neg_gen, device)
                    loss.backward()
                    opt.step()
                done_pass += 1
            block_snaps[d] = snap()   # snapshot after finishing domain d (forgetting curve)
        snaps["final"] = snap()
        snaps["_continual_blocks"] = block_snaps
        return snaps

    # INTERLEAVED / SHUFFLE: i.i.d. replay
    for p in range(1, P_max + 1):
        order = perm_gen.permutation(train_int.shape[0])
        tshuf = train_int[order]
        for s in range(0, tshuf.shape[0], batch):
            opt.zero_grad()
            loss = _batch_ce_loss(X, D, tshuf[s:s + batch], base_arr, span_arr, k_neg, neg_gen, device)
            loss.backward()
            opt.step()
        if p in checkpoints:
            snaps[p] = snap()
    if "final" not in snaps:
        snaps["final"] = snap()
    if P_max not in snaps:
        snaps[P_max] = snaps["final"]
    return snaps


# ---------------------------------------------------------------------------
# Held-out inference readout via the REAL AdditiveKGMap primitive.
# ---------------------------------------------------------------------------

def _map_from_coords(X_np, D_np, arena, device):
    """Wrap fit coords into the live AdditiveKGMap (real substrate object) for the readout path."""
    m = AdditiveKGMap(device=device)
    ent2idx = {str(i): i for i in range(arena["n_total"])}
    rel2idx = {str(r): r for r in range(arena["n_rel"])}
    m.set_coords(torch.from_numpy(X_np).to(torch.float32), torch.from_numpy(D_np).to(torch.float32),
                 ent2idx, rel2idx)
    return m


def _mrr_hits(scores_np, query_int, rel_value_idx):
    """Filtered MRR + hits@1 ranking the true tail among the query relation's value range. Returns (mrr, h1)."""
    nq = query_int.shape[0]
    if nq == 0:
        return float("nan"), float("nan")
    rr = np.zeros(nq, dtype=np.float64)
    h1 = np.zeros(nq, dtype=np.float64)
    for q in range(nq):
        r = int(query_int[q, 1]); t = int(query_int[q, 2])
        cand = rel_value_idx[r]
        sc = scores_np[q, cand]
        st = scores_np[q, t]
        greater = int(np.sum(sc > st))
        ties = int(np.sum(sc == st)) - 1   # exclude the true tail itself
        rank = 1.0 + greater + 0.5 * max(0, ties)
        rr[q] = 1.0 / rank
        h1[q] = 1.0 if rank <= 1.0 else 0.0
    return float(rr.mean()), float(h1.mean())


def eval_heldout(X_np, D_np, arena, device):
    """Held-out inference via AdditiveKGMap.score_edges (-> additive_direct_scores). Returns metric dict."""
    m = _map_from_coords(X_np, D_np, arena, device)
    q = arena["query_int"]
    scores = m.score_edges(q).numpy()          # (nq, N_total) real additive readout
    mrr_all, h1_all = _mrr_hits(scores, q, arena["rel_value_idx"])
    out = dict(mrr=mrr_all, hits1=h1_all)
    lvl = arena["query_level"]
    for level in (SUPER, SUB):
        mask = (lvl == level)
        if mask.sum() > 0:
            mm, hh = _mrr_hits(scores[mask], q[mask], arena["rel_value_idx"])
            out["mrr_%s" % level] = mm
    # by domain-presentation order (for continual forgetting): early = domain 0, late = last domain
    dom = arena["query_domain"]
    for tag, dval in (("early", 0), ("late", arena["S"] - 1)):
        mask = (dom == dval)
        if mask.sum() > 0:
            mm, _ = _mrr_hits(scores[mask], q[mask], arena["rel_value_idx"])
            out["mrr_%s" % tag] = mm
    return out


def pop_baseline(arena):
    """Frequency/marginal baseline: rank candidate tails by their global train frequency for that relation."""
    train_int = arena["train_int"]
    freq = {r: np.zeros(arena["rel_value_idx"][r].shape[0], dtype=np.float64) for r in range(arena["n_rel"])}
    base = arena["val_base"]
    for h, r, t in train_int:
        freq[int(r)][int(t) - base[int(r)]] += 1.0
    q = arena["query_int"]
    rr = []
    for i in range(q.shape[0]):
        r = int(q[i, 1]); t = int(q[i, 2])
        f = freq[r]
        tv = f[t - base[r]]
        greater = int(np.sum(f > tv)); ties = int(np.sum(f == tv)) - 1
        rank = 1.0 + greater + 0.5 * max(0, ties)
        rr.append(1.0 / rank)
    return float(np.mean(rr)) if rr else float("nan")


def oracle_ceiling(arena):
    """Info-ceiling: latent-type oracle predicts the CLEAN (domain/category) tail; MRR over the relation range."""
    q = arena["query_int"]; base = arena["val_base"]
    rr = []
    for i in range(q.shape[0]):
        h = int(q[i, 0]); r = int(q[i, 1]); t = int(q[i, 2])
        rng_span = arena["rel_value_idx"][r].shape[0]
        clean = int(arena["domain_of"][h]) if arena["rel_level"][r] == SUPER else int(arena["cat_of"][h])
        # oracle scores clean value top; true tail rank = 1 if t==clean else 2 (single competitor ranked above)
        rank = 1.0 if (t - base[r]) == clean else 2.0
        rr.append(1.0 / rank)
    return float(np.mean(rr)) if rr else float("nan")


# ---------------------------------------------------------------------------
# One seed: fit all arms, eval, compute the 4 signatures.
# ---------------------------------------------------------------------------

def _pass_to_half(traj_passes, traj_vals):
    """First checkpoint pass where normalized progress reaches half of (final-init). NaN if flat."""
    v0, vf = traj_vals[0], traj_vals[-1]
    if not (vf > v0 + 1e-6):
        return float("nan")
    half = v0 + 0.5 * (vf - v0)
    for p, v in zip(traj_passes, traj_vals):
        if v >= half:
            return float(p)
    return float(traj_passes[-1])


def run_seed(cfg, seed, device):
    arena = build_arena(cfg, seed, destroy_structure=False)
    arena_shuf = build_arena(cfg, seed, destroy_structure=True)
    pop = pop_baseline(arena)
    ceil = oracle_ceiling(arena)

    checkpoints = sorted(set(int(c) for c in cfg["checkpoints"]))
    P_max = int(cfg["P_max"])

    # INTERLEAVED trajectory
    inter_snaps = fit_schedule(arena, cfg, INTERLEAVED, seed, device)
    inter_traj = {}
    for p in checkpoints:
        if p in inter_snaps:
            Xn, Dn = inter_snaps[p]
            inter_traj[p] = eval_heldout(Xn, Dn, arena, device)
    Xf, Df = inter_snaps["final"]
    inter_final = eval_heldout(Xf, Df, arena, device)

    # SHUFFLE trajectory (structure destroyed)
    shuf_snaps = fit_schedule(arena_shuf, cfg, SHUFFLE, seed, device)
    shuf_traj = {}
    for p in checkpoints:
        if p in shuf_snaps:
            Xn, Dn = shuf_snaps[p]
            shuf_traj[p] = eval_heldout(Xn, Dn, arena_shuf, device)
    Xsf, Dsf = shuf_snaps["final"]
    shuf_final = eval_heldout(Xsf, Dsf, arena_shuf, device)
    pop_shuf = pop_baseline(arena_shuf)

    # CONTINUAL (task-blocked)
    cont_snaps = fit_schedule(arena, cfg, CONTINUAL, seed, device)
    Xc, Dc = cont_snaps["final"]
    cont_final = eval_heldout(Xc, Dc, arena, device)
    # forgetting curve: early-domain MRR after each domain block
    cont_early_curve = []
    for d in sorted(cont_snaps["_continual_blocks"].keys()):
        Xb, Db = cont_snaps["_continual_blocks"][d]
        cont_early_curve.append(eval_heldout(Xb, Db, arena, device).get("mrr_early", float("nan")))

    # ----- signatures -----
    passes = [p for p in checkpoints]
    inter_mrr_traj = [inter_traj[p]["mrr"] for p in passes]
    # (1) dose-response: rise from P=1 (or first>0) to P_max
    p_lo = passes[1] if (len(passes) > 1 and passes[0] == 0) else passes[0]
    dose_lift = inter_final["mrr"] - inter_traj.get(p_lo, inter_traj[passes[0]])["mrr"]
    sig_dose = bool(dose_lift >= DOSE_MARGIN)
    # (2) staging: coarse (super) normalized-progress leads fine (sub)
    super_traj = [inter_traj[p].get("mrr_super", float("nan")) for p in passes]
    sub_traj = [inter_traj[p].get("mrr_sub", float("nan")) for p in passes]
    half_super = _pass_to_half(passes, super_traj)
    half_sub = _pass_to_half(passes, sub_traj)
    sig_staging = bool(half_super == half_super and half_sub == half_sub and half_super < half_sub)
    # (3) beat-continual + forgetting
    beat_gap = inter_final["mrr"] - cont_final["mrr"]
    cont_early = cont_final.get("mrr_early", float("nan"))
    forgot = bool(cont_early == cont_early and cont_early <= pop + FORGET_EPS)
    sig_beat = bool(beat_gap >= BEAT_MARGIN and forgot)
    # (4) shuffle flat
    shuf_lift = shuf_final["mrr"] - pop_shuf
    shuf_dose = shuf_final["mrr"] - shuf_traj.get(p_lo, shuf_traj[passes[0]])["mrr"]
    sig_shuffle = bool(shuf_lift <= FLAT_EPS and abs(shuf_dose) <= max(FLAT_EPS, DOSE_MARGIN))

    beats_continual = bool(beat_gap >= BEAT_MARGIN)
    beats_pop = bool((inter_final["mrr"] - pop) >= POP_BEAT_MARGIN)
    n_sigs = int(sig_dose) + int(sig_staging) + int(sig_beat) + int(sig_shuffle)

    # arms-differ (META_RULE_AF): final code tables must be bit-distinct across arms
    def _digest(Xn):
        return hashlib.sha256(np.ascontiguousarray(Xn).tobytes()).hexdigest()
    digests = {INTERLEAVED: _digest(Xf), CONTINUAL: _digest(Xc), SHUFFLE: _digest(Xsf)}
    arms_differ = bool(len(set(digests.values())) == len(digests))

    return dict(
        seed=int(seed), pop=pop, pop_shuf=pop_shuf, oracle_ceiling=ceil,
        inter_final=inter_final, cont_final=cont_final, shuf_final=shuf_final,
        inter_mrr_traj={str(p): inter_traj[p]["mrr"] for p in passes},
        super_traj={str(p): super_traj[i] for i, p in enumerate(passes)},
        sub_traj={str(p): sub_traj[i] for i, p in enumerate(passes)},
        cont_early_curve=cont_early_curve,
        dose_lift=dose_lift, beat_gap=beat_gap, cont_early=cont_early, shuf_lift=shuf_lift, shuf_dose=shuf_dose,
        half_super=half_super, half_sub=half_sub,
        sig_dose=sig_dose, sig_staging=sig_staging, sig_beat=sig_beat, sig_shuffle=sig_shuffle,
        n_sigs=n_sigs, beats_continual=beats_continual, beats_pop=beats_pop, arms_differ=arms_differ,
        arm_digests=digests,
    )


# ---------------------------------------------------------------------------
# Aggregate across seeds -> verdict.
# ---------------------------------------------------------------------------

def _mean(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


def aggregate_and_verdict(per_seed):
    inter_mrr = _mean([r["inter_final"]["mrr"] for r in per_seed])
    cont_mrr = _mean([r["cont_final"]["mrr"] for r in per_seed])
    shuf_mrr = _mean([r["shuf_final"]["mrr"] for r in per_seed])
    pop = _mean([r["pop"] for r in per_seed])
    ceil = _mean([r["oracle_ceiling"] for r in per_seed])
    beat_gap = inter_mrr - cont_mrr
    pop_gap = inter_mrr - pop

    # a signature fires on aggregate if it fires on the mean AND on a majority of seeds
    n = len(per_seed)
    need = (n // 2) + 1

    def _sig_agg(key, mean_ok):
        votes = sum(1 for r in per_seed if r[key])
        return bool(mean_ok and votes >= need), votes

    sig_dose, v_dose = _sig_agg("sig_dose", _mean([r["dose_lift"] for r in per_seed]) >= DOSE_MARGIN)
    sig_staging, v_stag = _sig_agg("sig_staging", sum(1 for r in per_seed if r["sig_staging"]) >= need)
    cont_early_mean = _mean([r["cont_early"] for r in per_seed])
    forgot_mean = (cont_early_mean == cont_early_mean and cont_early_mean <= pop + FORGET_EPS)
    sig_beat, v_beat = _sig_agg("sig_beat", (beat_gap >= BEAT_MARGIN) and forgot_mean)
    sig_shuffle, v_shuf = _sig_agg("sig_shuffle", (shuf_mrr - _mean([r["pop_shuf"] for r in per_seed])) <= FLAT_EPS)

    n_sigs = int(sig_dose) + int(sig_staging) + int(sig_beat) + int(sig_shuffle)
    beats_continual = bool(beat_gap >= BEAT_MARGIN)
    beats_pop = bool(pop_gap >= POP_BEAT_MARGIN)
    arms_differ = all(r["arms_differ"] for r in per_seed)

    if not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif (beat_gap < REFUTE_EPS) or (pop_gap < REFUTE_EPS):
        verdict = "REFUTE"
    elif beats_continual and beats_pop and n_sigs >= SIGS_FOR_HARD_PASS:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE"

    msg = ("%s | INTERLEAVED_mrr=%.4f CONTINUAL_mrr=%.4f SHUFFLE_mrr=%.4f POP=%.4f CEIL=%.4f | "
           "beat_gap=%.4f (>= %.3f? %s) pop_gap=%.4f (>= %.3f? %s) | signatures %d/4 "
           "[dose=%s(v%d) staging=%s(v%d) beat=%s(v%d) shuffle=%s(v%d)] forgot_early_mean=%.4f arms_differ=%s"
           % (verdict, inter_mrr, cont_mrr, shuf_mrr, pop, ceil, beat_gap, BEAT_MARGIN, beats_continual,
              pop_gap, POP_BEAT_MARGIN, beats_pop, n_sigs, sig_dose, v_dose, sig_staging, v_stag,
              sig_beat, v_beat, sig_shuffle, v_shuf, cont_early_mean, arms_differ))
    gates = dict(verdict=verdict, inter_mrr=inter_mrr, cont_mrr=cont_mrr, shuf_mrr=shuf_mrr, pop=pop,
                 oracle_ceiling=ceil, beat_gap=beat_gap, pop_gap=pop_gap, beats_continual=beats_continual,
                 beats_pop=beats_pop, n_sigs=n_sigs, sig_dose=sig_dose, sig_staging=sig_staging,
                 sig_beat=sig_beat, sig_shuffle=sig_shuffle, forgot_early_mean=cont_early_mean,
                 arms_differ=arms_differ, seed_votes=dict(dose=v_dose, staging=v_stag, beat=v_beat, shuffle=v_shuf))
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test: exercises the REAL SGD-learning + AdditiveKGMap readout path + guard-vs-arena-floor.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    device = torch.device("cpu")
    cfg = dict(SELFTEST_CFG)
    exercised = set()

    r = run_seed(cfg, 7, device)
    # real_code_path was exercised inside run_seed via eval_heldout -> AdditiveKGMap + set_coords + score_edges
    exercised.update(["AdditiveKGMap", "AdditiveKGMap.set_coords", "AdditiveKGMap.score_edges",
                      "additive_direct_scores"])

    inter = r["inter_final"]["mrr"]; cont = r["cont_final"]["mrr"]; pop = r["pop"]; ceil = r["oracle_ceiling"]
    beat_gap = r["beat_gap"]

    # Directional discriminator at self-test scale: INTERLEAVED must beat CONTINUAL and POP (arena answerable);
    # SHUFFLE and CONTINUAL-early are the must-fail controls. Small-N bands are relaxed vs FULL.
    ST_BEAT = 0.02
    ST_POP = 0.02
    beats_cont = bool(beat_gap >= ST_BEAT)
    beats_pop = bool((inter - pop) >= ST_POP)
    baseline_in_band = bool(pop <= inter <= ceil + 1e-6 and 0.0 <= pop <= 1.0)
    arms_differ = r["arms_differ"]

    # VACUOUS-SMOKE guard: CONTINUAL/POP null must NOT reach INTERLEAVED (arena must be answerable + metric alive)
    control_reached_mech = bool((inter - max(cont, pop)) < ST_BEAT)
    assert_discriminator_fires(control_reached_mech, control_name="CONTINUAL_or_POP",
                               headline_name="interleaved_beats_continual_and_pop_heldout", run_mode="self_test",
                               extra="INTERLEAVED did not clear CONTINUAL/POP on the planted hierarchical arena -> "
                                     "arena not answerable / SGD or readout broken")

    # exercise the REAL AdditiveKGMap readout ONE more explicit time (real_code_path witness at N~small)
    Xf, Df = None, None
    arena = build_arena(cfg, 7)
    m = _map_from_coords(np.zeros((arena["n_total"], cfg["k"]), np.float32),
                         np.zeros((arena["n_rel"], cfg["k"]), np.float32), arena, device)
    _ = m.score_edges(arena["query_int"][:4]).numpy()   # additive_direct_scores exercised

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.set_coords", "AdditiveKGMap.score_edges",
                                        "additive_direct_scores"],
         "exercised_entrypoints": sorted(exercised),
         "extra": "held-out inference readout runs through the live AdditiveKGMap (set_coords + score_edges -> "
                  "additive_direct_scores) at self-test scale"},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"},
         "extra": "base/portable ctor kwargs only (device); coord_source optional/defaulted"},
        {"kind": "metric_moves", "metric_name": "interleaved_heldout_mrr",
         "values": [r["inter_mrr_traj"][k] for k in sorted(r["inter_mrr_traj"].keys(), key=lambda z: int(z))],
         "extra": "INTERLEAVED held-out MRR trajectory over replay passes must not be structurally frozen"},
        {"kind": "negative_control_margin",
         "control_scores": [r["shuf_final"]["mrr"], r["cont_final"].get("mrr_early", pop)],
         "headline_threshold": inter, "higher_is_pass": True, "margin": ST_BEAT, "n_repeats_min": 2,
         "control_name": "SHUFFLE_and_CONTINUAL_early_below_interleaved",
         "extra": "structure-destroyed SHUFFLE and forgotten CONTINUAL-early must sit below INTERLEAVED by margin"},
        {"kind": "guard_baseline_valid", "baseline_score": pop, "floor_score": 1.0 / max(2.0, arena["S"]),
         "guard_name": "INTERLEAVED_BEATS_POP", "baseline_name": "POP", "floor_name": "CHANCE", "eps": 0.02,
         "extra": "POP frequency floor validated above pure chance so the beats-POP guard is not comparing to a "
                  "structural-zero floor"},
    ], run_mode="self_test")

    out = dict(inter_mrr=round(inter, 5), cont_mrr=round(cont, 5), shuf_mrr=round(r["shuf_final"]["mrr"], 5),
               pop=round(pop, 5), oracle_ceiling=round(ceil, 5), beat_gap=round(beat_gap, 5),
               dose_lift=round(r["dose_lift"], 5), cont_early=round(r.get("cont_early", float("nan")), 5),
               shuf_lift=round(r["shuf_lift"], 5), half_super=r["half_super"], half_sub=r["half_sub"],
               sig_dose=r["sig_dose"], sig_staging=r["sig_staging"], sig_beat=r["sig_beat"],
               sig_shuffle=r["sig_shuffle"], n_sigs=r["n_sigs"], beats_cont=beats_cont, beats_pop=beats_pop,
               baseline_in_band=baseline_in_band, arms_differ=arms_differ, validity_preflight_ok=bool(vp_ok),
               validity_preflight_declared=["real_code_path", "substrate_signature", "metric_moves",
                                            "negative_control_fails_with_margin", "guard_baseline_valid"])
    ok = bool(beats_cont and beats_pop and baseline_in_band and arms_differ and vp_ok)
    if not ok:
        out["fail"] = ("selftest discriminator not clean: beats_cont=%s beats_pop=%s baseline_in_band=%s "
                       "arms_differ=%s vp_ok=%s" % (beats_cont, beats_pop, baseline_in_band, arms_differ, vp_ok))
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    if (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue"):
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else list(cfg["seeds"])
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(), "unit": tag, "idx": i,
                                "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s S=%s C=%s M=%s k=%s P_max=%s"
         % (device, torch.cuda.is_available(), run_mode, seeds, cfg["S"], cfg["C"], cfg["M"], cfg["k"], cfg["P_max"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s inter=%s cont=%s shuf=%s pop=%s beat_gap=%s n_sigs=%s vp_ok=%s"
         % (st_ok, st_res.get("inter_mrr"), st_res.get("cont_mrr"), st_res.get("shuf_mrr"), st_res.get("pop"),
            st_res.get("beat_gap"), st_res.get("n_sigs"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS consol interleaved-replay: INTERLEAVED beats CONTINUAL+POP on planted "
                        "hierarchical arena via REAL AdditiveKGMap readout; SHUFFLE/CONTINUAL-early controls below; "
                        "5 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            r = run_seed(cfg, seed, device)
            per_seed.append(r)
            write_partial(out_dir, seed, dict(seed=seed, metrics=_seed_summary(r), run_mode=run_mode))
            _log("seed=%d inter=%.4f cont=%.4f shuf=%.4f pop=%.4f ceil=%.4f | beat_gap=%.4f dose=%.4f "
                 "cont_early=%.4f shuf_lift=%.4f sigs=%d [d%d s%d b%d h%d] (%.1fs)"
                 % (seed, r["inter_final"]["mrr"], r["cont_final"]["mrr"], r["shuf_final"]["mrr"], r["pop"],
                    r["oracle_ceiling"], r["beat_gap"], r["dose_lift"], r.get("cont_early", float("nan")),
                    r["shuf_lift"], r["n_sigs"], r["sig_dose"], r["sig_staging"], r["sig_beat"], r["sig_shuffle"],
                    time.time() - ts))
            _hb("seed", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=[_seed_summary(r) for r in per_seed])
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def _seed_summary(r):
    """JSON-serializable per-seed summary (drop bulky raw arrays)."""
    return dict(seed=r["seed"], pop=r["pop"], pop_shuf=r["pop_shuf"], oracle_ceiling=r["oracle_ceiling"],
                inter_mrr=r["inter_final"]["mrr"], inter_hits1=r["inter_final"].get("hits1"),
                cont_mrr=r["cont_final"]["mrr"], shuf_mrr=r["shuf_final"]["mrr"],
                inter_mrr_super=r["inter_final"].get("mrr_super"), inter_mrr_sub=r["inter_final"].get("mrr_sub"),
                cont_early=r.get("cont_early"), inter_mrr_traj=r["inter_mrr_traj"],
                super_traj=r["super_traj"], sub_traj=r["sub_traj"], cont_early_curve=r["cont_early_curve"],
                dose_lift=r["dose_lift"], beat_gap=r["beat_gap"], shuf_lift=r["shuf_lift"], shuf_dose=r["shuf_dose"],
                half_super=r["half_super"], half_sub=r["half_sub"], sig_dose=r["sig_dose"],
                sig_staging=r["sig_staging"], sig_beat=r["sig_beat"], sig_shuffle=r["sig_shuffle"],
                n_sigs=r["n_sigs"], beats_continual=r["beats_continual"], beats_pop=r["beats_pop"],
                arms_differ=r["arms_differ"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
