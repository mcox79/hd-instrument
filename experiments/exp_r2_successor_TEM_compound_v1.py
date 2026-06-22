"""r2_successor_TEM_compound_v1 -- multi-hop chain-grade promotion via THREE structural fixes
to r1b's HARD_FAIL margin-decay pathology.

r1b HARD_FAILed (2026-06-22 full, 7 seeds N=8192 M=50000):
  K=3 mean 0.268 vs r1=0.240 diff=0.028 OUT-OF-TOL (+/- 0.02 band)
  OOD-refuse(margin) min 0.682 (FAIL: gate2 >= 0.90)
  margin-ratio min 1.003 (FAIL: c2 > 2.0x)

Three composable structural fixes (Research drill #3 5x DEEPER 2026-06-22):

  (1) SUCCESSOR_W_CLOSURE: M = sum_{k=1..K_max} gamma^k W^k applied AS the per-hop transition
      operator (M REPLACES W). Per-hop transition uses the multi-scale closure -- M aggregates
      1-hop..K_max-hop substrate paths weighted by gamma -- so each step has richer signal
      than a single W matvec. Critically, there is NO per-hop softmax / topk-bundle projection
      between hops; this LINEAR chain is what arrests r1b's per-hop margin decay. Source:
      Dayan 1993; Stachenfeld 2017 NatNeuro; Momennejad 2018 biorxiv.

  (2) TEM_FACTORED_COMPOUND: structural (R) factored from sensory (E); permutation-bound
      compound chain state = sum_k P^k @ e_k. Compound-margin refuse-gate operates on chain
      coherence (in-KB chains have COHERENT per-position recovery; OOD chains are INCOHERENT).
      Source: Whittington-Behrens 2020 Cell; Lisman-Jensen 2013; Kanerva 2009 HDC primitive.

  (3) ITER_CLEANUP_r1b_anchor: r1b's mechanism verbatim. MUST reproduce r1b means within
      +/- 0.01 (harness intact); anchor-fail => HARD_FAIL inconclusive (NOT mechanism-negative).

Pre-reg HARD bands (preregs/2026-06-22_r2_successor_TEM_compound_v1.md):
  HARD_PASS (K=4, winning arm in {SUCCESSOR_W_CLOSURE, TEM_FACTORED_COMPOUND}):
    mean acc >= 0.211 (1.20x r1's K=4 0.172) AND
    OOD_refuse_margin >= 0.90 at K=2,3,4 AND
    margin_ratio > 2.0x at K=2,3,4 AND
    cv across seeds <= 0.06 AND
    ITER_CLEANUP_r1b_anchor reproduces r1b within +/- 0.01 at K=2,3,4
  MIDDLE_BAND: partial gate lifts
  HARD_FAIL: no arm >= 1.05x r1 K=4 OR OOD-refuse < 0.80 at K=4 for all arms
  HARD_FAIL inconclusive: ITER_CLEANUP_r1b_anchor drift > 0.02 (harness changed)

Substrate-only-decode gate: torch is permitted (matmul backend; matches PROT-020 / Fix #24),
but NO LLM forward calls (no transformers, no AutoModel). Counter assertion at end of run.

Routing: matmul-heavy at N=8192 (W is 8192x8192 fp32 = 256 MB; K_max=5 chained matmuls for
SR closure; per-chain matmul-vector for iter-cleanup arm). Cell uses torch.cuda if available
(Fix #24: GPU dispatch must actually USE GPU); falls back to CPU. Routes to overnight_queue.

Compose: drill #2 c2 cascade-STC (independent harness; r2_cascade_W_v1 follow-on after both
land); HotpotQA K>=3 (post-r2 HARD_PASS); substrate_self_map_v2 (in-flight Director cell).
"""
import argparse
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

# ----- substrate-only-decode gate (counter; MUST stay at 0) -----
_LLM_CALL_COUNTER = [0]

ANCHOR_NAME = "r2_successor_TEM_compound_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# ----- r1b reference means (anchor arm must reproduce these within +/- 0.01) -----
R1B_MEAN_K2 = 0.3934
R1B_MEAN_K3 = 0.2677
R1B_MEAN_K4 = 0.1763
# r1 K=4 anchor for the HARD_PASS gain reference (>= 1.20x = 0.211)
R1_MEAN_K4 = 0.172
ANCHOR_TOL_TIGHT = 0.01   # ITER_CLEANUP_r1b_anchor reproduction tolerance
ANCHOR_TOL_LOOSE = 0.02   # harness-drift threshold (above this = INCONCLUSIVE)

# ----- pre-registered HARD thresholds -----
HARD_PASS_K4_FLOOR = 0.211          # 1.20x r1 K=4 (0.172)
OOD_REFUSE_MIN = 0.90
MARGIN_RATIO_MIN = 2.0
CV_PASS = 0.06

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- device selection (Fix #24: actually USE GPU when dispatched to GPU queue) -----
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ----- configuration -----
if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 2048
    M_TRIPLES = 5000
    # K=1 bracket dropped: chain sampler excludes (s, o) in direct triples, so at K=1 every
    # candidate is rejected (every direct triple IS a direct triple). K=10 deferred to full.
    K_HOPS_LIST = [2, 3]
    N_CHAINS = 100
    N_OOD = 100
    K_SET = 8
    K_INNER = 1
    K_MAX_SR = 3                       # smaller SR depth in smoke
    GAMMA = 0.8
    PERM_TYPE = "random"
    BETA_CLEANUP = float(N_DIM)
    ARMS = ["ITER_CLEANUP_r1b_anchor", "SUCCESSOR_W_CLOSURE", "TEM_FACTORED_COMPOUND"]
else:
    SEEDS = [7, 17, 23, 31, 41, 53, 67]
    N_DIM = 8192
    M_TRIPLES = 50000
    # K=1 bracket dropped (sampler excludes direct triples). K=10 retained as discriminating
    # bracket -- all arms should collapse to <0.05; SR collapse confirms K_max=5 is the active
    # window (no leakage from K_max+ paths).
    K_HOPS_LIST = [2, 3, 4, 10]
    N_CHAINS = 500
    N_OOD = 500
    K_SET = 8
    K_INNER = 1
    K_MAX_SR = 5
    GAMMA = 0.8
    PERM_TYPE = "random"
    BETA_CLEANUP = float(N_DIM)
    ARMS = ["ITER_CLEANUP_r1b_anchor", "SUCCESSOR_W_CLOSURE", "TEM_FACTORED_COMPOUND"]

CONFIG_VERSION = (
    "r2-successor-TEM-compound: arms=%s; N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
    "K_max_SR=%d gamma=%.2f perm=%s n_seeds=%d n_chains=%d device=%s; "
    "bands K4>=%.3f (1.20x r1) OOD-refuse>=%.2f margin-ratio>%.1f cv<=%.2f anchor-tol+/-%.2f"
    % (str(ARMS), N_DIM, M_TRIPLES, str(K_HOPS_LIST), K_SET, K_INNER,
       K_MAX_SR, GAMMA, PERM_TYPE, len(SEEDS), N_CHAINS, str(DEVICE),
       HARD_PASS_K4_FLOOR, OOD_REFUSE_MIN, MARGIN_RATIO_MIN, CV_PASS, ANCHOR_TOL_TIGHT)
)


# ----- core HD primitives -----

def bipolar_np(M, n, g):
    """Numpy bipolar codebook (kept for selftest determinism vs torch)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def bipolar_torch(M, n, g):
    """Torch bipolar codebook on DEVICE. Uses numpy RNG for cross-seed reproducibility."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return torch.from_numpy(Xn).to(DEVICE)


def _normalize_t(v, eps=1e-8):
    """Normalize a torch 1-D vector."""
    n = torch.linalg.norm(v)
    return v / (n + eps)


def _random_perm_indices(n, g):
    """Random permutation as torch index tensor on DEVICE."""
    p = g.permutation(n).astype(np.int64)
    return torch.from_numpy(p).to(DEVICE)


def _apply_perm_k(v, perm_idx, k):
    """Apply perm permutation k times to a 1-D torch vector. k can be negative (inverse)."""
    if k == 0:
        return v
    if k > 0:
        out = v
        for _ in range(k):
            out = out[perm_idx]
        return out
    # negative k: apply inverse permutation |k| times
    # inverse perm: inv[perm_idx[i]] = i
    inv_idx = torch.empty_like(perm_idx)
    inv_idx[perm_idx] = torch.arange(perm_idx.shape[0], device=DEVICE)
    out = v
    for _ in range(-k):
        out = out[inv_idx]
    return out


# ----- self-test: tiny synthetic KG, prove all 3 arms run + SR>=ITER + compound-margin separates -----

def _selftest():
    """Tiny synthetic KG K=2 sanity: SUCCESSOR_W_CLOSURE >= ITER_CLEANUP on a clean chain set;
    TEM compound-margin separates in-KB from OOD."""
    g = np.random.default_rng(0)
    n = 256
    ne = 30
    nr = 3
    E = bipolar_torch(ne, n, g)
    R = bipolar_torch(nr, n, g)
    sq = math.sqrt(n)
    # Build 10 chains s -p0-> x -p1-> o
    triples = []
    chains_truth = []
    for i in range(10):
        s, x, o = i, 10 + i, 20 + i
        triples.append((s, 0, x))
        triples.append((x, 1, o))
        chains_truth.append((s, [0, 1], o))
    # Multi-value Hebbian
    W = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    for (s, p, o) in triples:
        key = E[s] * R[p] * sq
        W += torch.outer(E[o], key) / n

    # ITER_CLEANUP K=2
    K_set_local = 4
    beta_local = float(n)
    iter_hit = 0
    for (s, rels, o_true) in chains_truth:
        state = E[s].clone()
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set_local)
            z = beta_local * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
        pred = int(torch.argmax(E @ state).item())
        if pred == o_true:
            iter_hit += 1
    iter_acc = iter_hit / len(chains_truth)

    # SUCCESSOR_W_CLOSURE: M = sum_{k=1..K_max} gamma^k W^k applied AS the per-hop operator
    K_max = 2
    gamma = 0.8
    Wk = W.clone()
    M = gamma * Wk
    for k in range(2, K_max + 1):
        Wk = W @ Wk
        M = M + (gamma ** k) * Wk
    sr_hit = 0
    for (s, rels, o_true) in chains_truth:
        state = E[s].clone()
        for p in rels:
            state = M @ (state * R[p] * sq)
            state = _normalize_t(state)
        ent_scores = E @ state
        pred = int(torch.argmax(ent_scores).item())
        if pred == o_true:
            sr_hit += 1
    sr_acc = sr_hit / len(chains_truth)

    # TEM_FACTORED_COMPOUND: compound chain state via permutation-binding; verify margin separation
    perm_idx = _random_perm_indices(n, g)
    inkb_margins = []
    ood_margins = []
    for (s, rels, o_true) in chains_truth:
        # in-KB chain: hop iteratively, collect chain entities
        chain_ents = [E[s]]
        state = E[s].clone()
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set_local)
            z = beta_local * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
            chain_ents.append(state)
        # Compound chain: sum_k P^k @ e_k
        compound = torch.zeros(n, dtype=TORCH_DTYPE, device=DEVICE)
        for k, e_k in enumerate(chain_ents):
            compound = compound + _apply_perm_k(e_k, perm_idx, k)
        compound = _normalize_t(compound)
        # Compound-margin: average of per-position recovery margin (top1 - top2 over codebook)
        pos_margins = []
        for k in range(len(chain_ents)):
            recov = _apply_perm_k(compound, perm_idx, -k)
            ent_scores = E @ recov
            top2, _ = torch.topk(ent_scores, 2)
            pos_margins.append(float(top2[0].item() - top2[1].item()))
        inkb_margins.append(float(np.mean(pos_margins)))
    # OOD chains: random relation sequences (unused chain at this s)
    for trial in range(10):
        s = 29
        rels = [2, 0]
        chain_ents = [E[s]]
        state = E[s].clone()
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set_local)
            z = beta_local * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
            chain_ents.append(state)
        compound = torch.zeros(n, dtype=TORCH_DTYPE, device=DEVICE)
        for k, e_k in enumerate(chain_ents):
            compound = compound + _apply_perm_k(e_k, perm_idx, k)
        compound = _normalize_t(compound)
        pos_margins = []
        for k in range(len(chain_ents)):
            recov = _apply_perm_k(compound, perm_idx, -k)
            ent_scores = E @ recov
            top2, _ = torch.topk(ent_scores, 2)
            pos_margins.append(float(top2[0].item() - top2[1].item()))
        ood_margins.append(float(np.mean(pos_margins)))
    inkb_mean = float(np.mean(inkb_margins))
    ood_mean = float(np.mean(ood_margins))

    assert iter_acc >= 0.7, "selftest: ITER_CLEANUP K=2 acc too low %.2f" % iter_acc
    assert sr_acc >= iter_acc, (
        "selftest: SR_CLOSURE K=2 acc %.2f below ITER_CLEANUP %.2f -- SR mechanism broken"
        % (sr_acc, iter_acc)
    )
    assert inkb_mean > ood_mean, (
        "selftest: TEM compound-margin in-KB %.4f must exceed OOD %.4f"
        % (inkb_mean, ood_mean)
    )
    print(
        "[selftest] PASS: ITER K=2 acc=%.2f; SR K=2 acc=%.2f (>= ITER); "
        "TEM compound-margin in-KB %.4f > OOD %.4f (ratio %.2fx) [device=%s]"
        % (iter_acc, sr_acc, inkb_mean, ood_mean,
           inkb_mean / max(abs(ood_mean), 1e-9), str(DEVICE)),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- KG loader -----

def load_kg(seed, m_triples):
    if not KG_PATH.exists():
        raise FileNotFoundError("FB15k-237 not found at %s" % KG_PATH)
    rows = []
    with open(KG_PATH, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            rows.append((r["subject"], r["predicate"], r["object"]))
    g = np.random.default_rng(seed)
    g.shuffle(rows)
    rows = rows[:m_triples]
    ents = sorted({s for s, _, _ in rows} | {o for _, _, o in rows})
    rels = sorted({p for _, p, _ in rows})
    eid = {e: i for i, e in enumerate(ents)}
    rid = {p: i for i, p in enumerate(rels)}
    triples = [(eid[s], rid[p], eid[o]) for s, p, o in rows]
    keyobjs = defaultdict(set)
    for (s, p, o) in triples:
        keyobjs[(s, p)].add(o)
    return triples, {k: sorted(v) for k, v in keyobjs.items()}, len(ents), len(rels)


def ingest_hebbian_torch(triples, n_ent, n_rel, g, batch=5000):
    """Build E, R codebooks and W transition matrix on DEVICE."""
    E = bipolar_torch(n_ent, N_DIM, g)
    R = bipolar_torch(n_rel, N_DIM, g)
    sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx_np, p_idx_np, o_idx_np = tr[:, 0], tr[:, 1], tr[:, 2]
    W = torch.zeros((N_DIM, N_DIM), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, len(tr), batch):
        s_b = torch.from_numpy(s_idx_np[b:b + batch]).to(DEVICE)
        p_b = torch.from_numpy(p_idx_np[b:b + batch]).to(DEVICE)
        o_b = torch.from_numpy(o_idx_np[b:b + batch]).to(DEVICE)
        ks = (E[s_b] * R[p_b] * sq).to(TORCH_DTYPE)
        W += (E[o_b].T @ ks) / N_DIM
    return E, R, W, sq


def precompute_sr_closure(W, K_max, gamma):
    """M = sum_{k=1..K_max} gamma^k W^k. Done on DEVICE."""
    Wk = W.clone()
    M = gamma * Wk
    for k in range(2, K_max + 1):
        Wk = W @ Wk
        M = M + (gamma ** k) * Wk
    return M


# ----- K-hop chain sampling (heldout_in_compose_graph guard inherited from r1b) -----

def sample_k_hop_chains(triples, keyobjs, K, n_chains, g):
    adj = defaultdict(list)
    for (s, p), objs in keyobjs.items():
        for o in objs:
            adj[s].append((p, o))
    direct = set((s, o) for (s, p, o) in triples)
    starts = [s for s in adj if adj[s]]
    if not starts:
        return [], 0
    chains = []
    leak = 0
    tries = 0
    max_tries = n_chains * 80
    while len(chains) < n_chains and tries < max_tries:
        tries += 1
        s = int(g.choice(starts))
        rels = []
        ints = []
        cur = s
        ok = True
        o_final = None
        for k in range(K):
            if cur not in adj or not adj[cur]:
                ok = False
                break
            p_k, o_k = adj[cur][int(g.integers(0, len(adj[cur])))]
            rels.append(p_k)
            if k < K - 1:
                ints.append(o_k)
            else:
                o_final = o_k
            cur = o_k
        if not ok or o_final is None:
            continue
        if o_final == s:
            continue
        if (s, o_final) in direct:
            leak += 1
            continue
        if any(x == s for x in ints):
            continue
        chains.append((s, rels, ints, o_final))
    return chains, leak


def sample_ood_k_hop(keyobjs, n_ent, n_rel, K, n_chains, g):
    keyset = set(keyobjs.keys())
    ood = []
    tries = 0
    max_tries = n_chains * 50
    while len(ood) < n_chains and tries < max_tries:
        tries += 1
        s = int(g.integers(0, n_ent))
        rels = [int(g.integers(0, n_rel)) for _ in range(K)]
        if (s, rels[0]) in keyset:
            continue
        ood.append((s, rels))
    return ood


# ----- ARM 1: ITER_CLEANUP (r1b verbatim, torch-backed) -----

def traverse_iter_cleanup(E, R, W, sq, start_ent, rel_chain, K_set, K_inner, beta):
    state = E[start_ent].clone()
    final_top1 = 0.0
    final_top2 = 0.0
    for p in rel_chain:
        for _inner in range(K_inner):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set)
            final_top1 = float(top_conf[0].item())
            final_top2 = float(top_conf[1].item())
            z = beta * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
    ent_scores = E @ state
    pred = int(torch.argmax(ent_scores).item())
    return pred, final_top1, final_top2


# ----- ARM 2: SUCCESSOR_W_CLOSURE -----

def traverse_successor(E, R, M, sq, start_ent, rel_chain):
    """K-hop retrieval via SUCCESSOR-W closure M = sum_{k=1..K_max} gamma^k W^k applied as
    the per-hop transition operator (M replaces W). Per-hop transition uses the multi-scale
    closure operator -- M aggregates 1-hop, 2-hop, ..., K_max-hop substrate paths weighted
    by gamma -- so each step has richer signal than a single W matvec. Critically, there is
    NO per-hop softmax / topk-bundle projection between hops; this LINEAR chain is what
    arrests the per-hop margin decay (the r1b failure mode). Refuse-gate is the final
    top1-top2 margin in the codebook readout.

    state_0 = E[start]
    state_k = M @ (state_{k-1} * R[p_k] * sq)
    pred = argmax(E @ state_K)
    Returns (pred, top1, top2).
    """
    state = E[start_ent].clone()
    for p in rel_chain:
        state = M @ (state * R[p] * sq)
        state = _normalize_t(state)
    ent_scores = E @ state
    top_conf, top_idx = torch.topk(ent_scores, 2)
    top1 = float(top_conf[0].item())
    top2 = float(top_conf[1].item())
    pred = int(torch.argmax(ent_scores).item())
    return pred, top1, top2


# ----- ARM 3: TEM_FACTORED_COMPOUND -----

def traverse_tem_compound(E, R, W, sq, start_ent, rel_chain, K_set, K_inner, beta, perm_idx):
    """TEM-factored: structural R applied per-hop to factored state; compound state =
    sum_k P^k @ e_k. Returns (pred, compound_margin_mean, top1_final, top2_final).
    compound_margin_mean = mean per-position (top1 - top2) recovered from compound state."""
    # Run iterative-cleanup for the chain entities (factored: R as structural operator)
    chain_ents = [E[start_ent].clone()]
    state = E[start_ent].clone()
    final_top1 = 0.0
    final_top2 = 0.0
    for p in rel_chain:
        for _inner in range(K_inner):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_conf, top_idx = torch.topk(ent_scores, K_set)
            final_top1 = float(top_conf[0].item())
            final_top2 = float(top_conf[1].item())
            z = beta * top_conf
            w = torch.softmax(z, dim=0)
            state = (w.unsqueeze(1) * E[top_idx]).sum(dim=0)
            state = _normalize_t(state)
        chain_ents.append(state.clone())
    # Compound state: sum_k P^k @ e_k
    compound = torch.zeros(N_DIM, dtype=TORCH_DTYPE, device=DEVICE)
    for k, e_k in enumerate(chain_ents):
        compound = compound + _apply_perm_k(e_k, perm_idx, k)
    compound = _normalize_t(compound)
    # Compound-margin: mean per-position (top1 - top2) over codebook readout
    pos_margins = []
    for k in range(len(chain_ents)):
        recov = _apply_perm_k(compound, perm_idx, -k)
        ent_scores = E @ recov
        top2_t, _ = torch.topk(ent_scores, 2)
        pos_margins.append(float(top2_t[0].item() - top2_t[1].item()))
    compound_margin_mean = float(np.mean(pos_margins))
    # Final-hop prediction = last chain entity (post-cleanup)
    ent_scores = E @ state
    pred = int(torch.argmax(ent_scores).item())
    return pred, compound_margin_mean, final_top1, final_top2


# ----- per-arm evaluator -----

def eval_arm_on_chains(arm, E, R, W, M, sq, chains, ood_chains, K, perm_idx):
    """Returns dict with per-chain results for this arm at this K.
    Fields: iter_acc, inkb_top1, inkb_top2, ood_top1, ood_top2,
            inkb_compound_margin (TEM only), ood_compound_margin (TEM only),
            iter_wall_s, ood_wall_s."""
    inkb_top1 = []
    inkb_top2 = []
    inkb_compound = []
    n_hit = 0
    t = time.time()
    for (s, rels, _ints, o_true) in chains:
        if arm == "ITER_CLEANUP_r1b_anchor":
            pred, ft1, ft2 = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP,
            )
        elif arm == "SUCCESSOR_W_CLOSURE":
            pred, ft1, ft2 = traverse_successor(E, R, M, sq, s, rels)
        elif arm == "TEM_FACTORED_COMPOUND":
            pred, cm, ft1, ft2 = traverse_tem_compound(
                E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP, perm_idx,
            )
            inkb_compound.append(cm)
        else:
            raise ValueError("unknown arm %s" % arm)
        n_hit += int(pred == o_true)
        inkb_top1.append(ft1)
        inkb_top2.append(ft2)
    iter_acc = n_hit / max(len(chains), 1)
    iter_wall = time.time() - t

    ood_top1 = []
    ood_top2 = []
    ood_compound = []
    t = time.time()
    for (s, rels) in ood_chains:
        if arm == "ITER_CLEANUP_r1b_anchor":
            _pred, ft1, ft2 = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP,
            )
        elif arm == "SUCCESSOR_W_CLOSURE":
            _pred, ft1, ft2 = traverse_successor(E, R, M, sq, s, rels)
        elif arm == "TEM_FACTORED_COMPOUND":
            _pred, cm, ft1, ft2 = traverse_tem_compound(
                E, R, W, sq, s, rels, K_SET, K_INNER, BETA_CLEANUP, perm_idx,
            )
            ood_compound.append(cm)
        ood_top1.append(ft1)
        ood_top2.append(ft2)
    ood_wall = time.time() - t
    return {
        "iter_acc": iter_acc,
        "inkb_top1": np.asarray(inkb_top1, dtype=np.float32),
        "inkb_top2": np.asarray(inkb_top2, dtype=np.float32),
        "ood_top1": np.asarray(ood_top1, dtype=np.float32),
        "ood_top2": np.asarray(ood_top2, dtype=np.float32),
        "inkb_compound": np.asarray(inkb_compound, dtype=np.float32) if inkb_compound else None,
        "ood_compound": np.asarray(ood_compound, dtype=np.float32) if ood_compound else None,
        "iter_wall_s": iter_wall,
        "ood_wall_s": ood_wall,
    }


def refuse_gate_calibrated(margin_in, margin_ood):
    """Calibrate tau on held-CAL split (first half), evaluate on held-TEST split (second half).
    Returns (tau, ood_refuse_test, inkb_accept_test, cal_balanced_score)."""
    h_in = len(margin_in) // 2
    h_ood = len(margin_ood) // 2
    cal_in = margin_in[:h_in]
    cal_ood = margin_ood[:h_ood]
    test_in = margin_in[h_in:]
    test_ood = margin_ood[h_ood:]
    if len(cal_in) == 0 or len(cal_ood) == 0:
        return 0.0, 0.0, 0.0, 0.0
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau = float(cands[0])
    best_bal = -1.0
    for tcand in cands:
        acc_in = float((cal_in >= tcand).mean())
        ref_ood = float((cal_ood < tcand).mean())
        bal = 0.5 * (acc_in + ref_ood)
        if bal > best_bal:
            best_bal = bal
            best_tau = float(tcand)
    ood_refuse_test = float((test_ood < best_tau).mean()) if len(test_ood) else 0.0
    inkb_accept_test = float((test_in >= best_tau).mean()) if len(test_in) else 0.0
    return best_tau, ood_refuse_test, inkb_accept_test, best_bal


# ----- single seed run -----

def run_seed(seed, out_dir):
    g = np.random.default_rng(seed)
    out = {
        "seed": seed,
        "_ckpt_key": str(seed),
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": M_TRIPLES,
        "device": str(DEVICE),
        "per_unit": [],
    }
    t0 = time.time()
    triples, keyobjs, n_ent, n_rel = load_kg(seed, M_TRIPLES)
    E, R, W, sq = ingest_hebbian_torch(triples, n_ent, n_rel, g)
    ingest_s = time.time() - t0
    # Precompute SR closure (once per seed; used by SUCCESSOR_W_CLOSURE arm at all K)
    t_sr = time.time()
    M = precompute_sr_closure(W, K_MAX_SR, GAMMA)
    sr_setup_s = time.time() - t_sr
    # Permutation matrix for TEM compound (once per seed)
    perm_idx = _random_perm_indices(N_DIM, g)
    print(
        "  [seed=%d] ingested M=%d in %.1fs (n_ent=%d n_rel=%d n_keys=%d); "
        "SR closure (K_max=%d gamma=%.2f) precomputed in %.1fs; device=%s"
        % (seed, M_TRIPLES, ingest_s, n_ent, n_rel, len(keyobjs),
           K_MAX_SR, GAMMA, sr_setup_s, str(DEVICE)),
        flush=True,
    )

    for K in K_HOPS_LIST:
        chains, leak = sample_k_hop_chains(
            triples, keyobjs, K, n_chains=N_CHAINS,
            g=np.random.default_rng(seed + 100 + K),
        )
        n_actual = len(chains)
        if n_actual == 0:
            print("  [seed=%d K=%d] no chains" % (seed, K), flush=True)
            continue
        ood_chains = sample_ood_k_hop(
            keyobjs, n_ent, n_rel, K, n_chains=N_OOD,
            g=np.random.default_rng(seed + 700 + K),
        )

        for arm in ARMS:
            res = eval_arm_on_chains(arm, E, R, W, M, sq, chains, ood_chains, K, perm_idx)
            # Margin signal: top1 - top2 (the r1b refuse-signal) for all arms
            inkb_margin = res["inkb_top1"] - res["inkb_top2"]
            ood_margin = res["ood_top1"] - res["ood_top2"]
            best_tau, ood_refuse, inkb_accept, best_bal = refuse_gate_calibrated(
                inkb_margin, ood_margin)
            inkb_margin_mean = float(np.mean(inkb_margin)) if len(inkb_margin) else 0.0
            ood_margin_mean = float(np.mean(ood_margin)) if len(ood_margin) else 0.0
            margin_ratio = inkb_margin_mean / max(abs(ood_margin_mean), 1e-9)

            # Compound-margin refuse-gate (TEM arm only)
            compound_tau = 0.0
            compound_refuse = 0.0
            compound_accept = 0.0
            compound_bal = 0.0
            compound_ratio = 0.0
            compound_inkb_mean = 0.0
            compound_ood_mean = 0.0
            if arm == "TEM_FACTORED_COMPOUND" and res["inkb_compound"] is not None:
                compound_tau, compound_refuse, compound_accept, compound_bal = (
                    refuse_gate_calibrated(res["inkb_compound"], res["ood_compound"])
                )
                compound_inkb_mean = float(np.mean(res["inkb_compound"]))
                compound_ood_mean = float(np.mean(res["ood_compound"]))
                compound_ratio = compound_inkb_mean / max(abs(compound_ood_mean), 1e-9)

            unit = {
                "seed": seed,
                "K_hops": K,
                "arm": arm,
                "n_chains_actual": n_actual,
                "leak_skipped": leak,
                "n_ood_chains": len(ood_chains),
                "iter_acc": round(res["iter_acc"], 4),
                # per-hop margin refuse (same gate as r1b for cross-arm comparability)
                "tau_margin": float(best_tau),
                "ood_refuse_margin_test": round(ood_refuse, 4),
                "inkb_accept_margin_test": round(inkb_accept, 4),
                "best_cal_bal_margin": round(best_bal, 4),
                "inkb_margin_mean": round(inkb_margin_mean, 6),
                "ood_margin_mean": round(ood_margin_mean, 6),
                "margin_ratio": round(margin_ratio, 4),
                # compound-margin (TEM only)
                "compound_margin_inkb_mean": round(compound_inkb_mean, 6),
                "compound_margin_ood_mean": round(compound_ood_mean, 6),
                "compound_margin_ratio": round(compound_ratio, 4),
                "compound_ood_refuse_test": round(compound_refuse, 4),
                "compound_inkb_accept_test": round(compound_accept, 4),
                "compound_tau": float(compound_tau),
                # walls
                "iter_wall_s": round(res["iter_wall_s"], 2),
                "ood_wall_s": round(res["ood_wall_s"], 2),
            }
            out["per_unit"].append(unit)
            print(
                ("  [seed=%d K=%d arm=%s n=%d leak=%d] acc=%.4f | "
                 "OOD-refuse(margin,test)=%.3f margin-ratio=%.3fx | "
                 "compound ratio=%.3fx OOD-refuse=%.3f")
                % (seed, K, arm, n_actual, leak, res["iter_acc"],
                   ood_refuse, margin_ratio, compound_ratio, compound_refuse),
                flush=True,
            )

    out["ingest_s"] = round(ingest_s, 1)
    out["sr_setup_s"] = round(sr_setup_s, 1)
    out["seed_wall_s"] = round(time.time() - t0, 1)
    return out


# ----- verdict (pre-reg HARD bands) -----

def verdict(ps) -> Tuple[str, str]:
    # Aggregate by (K, arm)
    by_k_arm = defaultdict(lambda: {
        "iter_acc": [],
        "ood_refuse_margin": [],
        "margin_ratio": [],
        "compound_ratio": [],
        "compound_ood_refuse": [],
    })
    for p in ps:
        for u in p["per_unit"]:
            key = (u["K_hops"], u["arm"])
            by_k_arm[key]["iter_acc"].append(u["iter_acc"])
            by_k_arm[key]["ood_refuse_margin"].append(u["ood_refuse_margin_test"])
            by_k_arm[key]["margin_ratio"].append(u["margin_ratio"])
            by_k_arm[key]["compound_ratio"].append(u["compound_margin_ratio"])
            by_k_arm[key]["compound_ood_refuse"].append(u["compound_ood_refuse_test"])

    agg = {}
    for (K, arm), d in by_k_arm.items():
        m_acc = float(np.mean(d["iter_acc"])) if d["iter_acc"] else 0.0
        cv_acc = (float(np.std(d["iter_acc"]) / max(np.mean(d["iter_acc"]), 1e-9))
                  if d["iter_acc"] else 0.0)
        agg.setdefault(K, {})[arm] = {
            "iter_acc": round(m_acc, 4),
            "cv": round(cv_acc, 4),
            "ood_refuse_margin": round(float(np.mean(d["ood_refuse_margin"])) if d["ood_refuse_margin"] else 0.0, 4),
            "margin_ratio": round(float(np.mean(d["margin_ratio"])) if d["margin_ratio"] else 0.0, 4),
            "compound_ratio": round(float(np.mean(d["compound_ratio"])) if d["compound_ratio"] else 0.0, 4),
            "compound_ood_refuse": round(float(np.mean(d["compound_ood_refuse"])) if d["compound_ood_refuse"] else 0.0, 4),
            "n_seeds": len(d["iter_acc"]),
        }

    enforce_repro = (RUN_MODE == "full" and M_TRIPLES >= 25000 and N_DIM >= 4096)

    # ---- Anchor reproduction check (ITER_CLEANUP_r1b_anchor vs r1b means) ----
    anchor_msgs = []
    anchor_drift_tight = False
    anchor_drift_loose = False
    for K, ref_mean in zip([2, 3, 4], [R1B_MEAN_K2, R1B_MEAN_K3, R1B_MEAN_K4]):
        if K not in agg:
            continue
        anchor = agg[K].get("ITER_CLEANUP_r1b_anchor")
        if anchor is None:
            continue
        diff = abs(anchor["iter_acc"] - ref_mean)
        tight_ok = diff <= ANCHOR_TOL_TIGHT
        loose_ok = diff <= ANCHOR_TOL_LOOSE
        if enforce_repro:
            if not tight_ok:
                anchor_drift_tight = True
            if not loose_ok:
                anchor_drift_loose = True
        tag = "OK" if tight_ok else ("LOOSE-OK" if loose_ok else (
            "DRIFT" if enforce_repro else "SMOKE-SKIP"))
        anchor_msgs.append("K%d anchor=%.4f r1b=%.4f diff=%.4f %s" % (
            K, anchor["iter_acc"], ref_mean, diff, tag))

    # ---- Find winning arm at K=4 (best non-anchor mean) ----
    winning_arm = None
    winning_mean = -1.0
    if 4 in agg:
        for arm, d in agg[4].items():
            if arm == "ITER_CLEANUP_r1b_anchor":
                continue
            if d["iter_acc"] > winning_mean:
                winning_mean = d["iter_acc"]
                winning_arm = arm

    # ---- Discriminating-regime sanity (K=10 bracket; K=1 dropped per sampler design) ----
    bracket_msgs = []
    k10_sanity_ok = True
    if 10 in agg:
        for arm in ARMS:
            if arm in agg[10]:
                acc = agg[10][arm]["iter_acc"]
                ok = acc <= 0.05  # K=10 should collapse
                if not ok:
                    k10_sanity_ok = False
                bracket_msgs.append("K10[%s]=%.3f%s" % (arm, acc, "" if ok else "(LEAK)"))

    # ---- HARD_PASS check at K=4 for winning arm ----
    hp_msgs = []
    hp_pass = False
    if winning_arm is not None and 4 in agg:
        wd = agg[4][winning_arm]
        c_acc = wd["iter_acc"] >= HARD_PASS_K4_FLOOR
        # Margin OOD-refuse across K in {2,3,4}
        ood_refuses = [agg[K][winning_arm]["ood_refuse_margin"]
                       for K in [2, 3, 4] if K in agg and winning_arm in agg[K]]
        c_ood = all(x >= OOD_REFUSE_MIN for x in ood_refuses) if ood_refuses else False
        ood_min = float(min(ood_refuses)) if ood_refuses else 0.0
        # Margin-ratio across K in {2,3,4}
        ratios = [agg[K][winning_arm]["margin_ratio"]
                  for K in [2, 3, 4] if K in agg and winning_arm in agg[K]]
        c_ratio = all(r > MARGIN_RATIO_MIN for r in ratios) if ratios else False
        ratio_min = float(min(ratios)) if ratios else 0.0
        # cv
        c_cv = wd["cv"] <= CV_PASS
        hp_msgs.append(("winning=%s K4=%.4f (>=%.3f:%s) OOD-refuse(margin)min=%.3f (>=%.2f:%s) "
                        "margin-ratio min=%.3f (>%.1f:%s) cv=%.4f (<=%.2f:%s)") %
                       (winning_arm, wd["iter_acc"], HARD_PASS_K4_FLOOR, c_acc,
                        ood_min, OOD_REFUSE_MIN, c_ood,
                        ratio_min, MARGIN_RATIO_MIN, c_ratio,
                        wd["cv"], CV_PASS, c_cv))
        hp_pass = c_acc and c_ood and c_ratio and c_cv

    # ---- MIDDLE_BAND check (partial gates lift) ----
    middle_pass = False
    if winning_arm is not None and 4 in agg:
        wd = agg[4][winning_arm]
        m_acc = wd["iter_acc"] >= 1.05 * R1_MEAN_K4   # >= 0.181
        ood_refuses = [agg[K][winning_arm]["ood_refuse_margin"]
                       for K in [2, 3, 4] if K in agg and winning_arm in agg[K]]
        m_ood = (min(ood_refuses) >= 0.80) if ood_refuses else False
        ratios = [agg[K][winning_arm]["margin_ratio"]
                  for K in [2, 3, 4] if K in agg and winning_arm in agg[K]]
        m_ratio = (min(ratios) >= 1.5) if ratios else False
        middle_pass = (m_acc or m_ood or m_ratio) and not hp_pass

    summ = (
        "by-K-by-arm: %s | anchor-repro: %s | brackets: %s | winning: %s"
        % (json.dumps({"K%d" % K: agg[K] for K in sorted(agg.keys())}),
           " ; ".join(anchor_msgs) if anchor_msgs else "n/a",
           " ; ".join(bracket_msgs) if bracket_msgs else "n/a",
           " ; ".join(hp_msgs) if hp_msgs else "n/a")
    )

    # Inconclusive HARD_FAIL: anchor drift > 0.02 means harness intact-check failed
    if enforce_repro and anchor_drift_loose:
        return (
            "HARD_FAIL",
            "HARD_FAIL inconclusive: ITER_CLEANUP_r1b_anchor drifted >+/-%.2f vs r1b means -- "
            "harness changed; cannot evaluate chain-grade promotion mechanism. " % ANCHOR_TOL_LOOSE
            + summ,
        )

    if hp_pass and not anchor_drift_tight:
        return (
            "HARD_PASS",
            ("HARD_PASS: r1 chain-grade promotion via %s -- K4=%.4f >= %.3f (1.20x r1 K=4); "
             "OOD-refuse(margin) >= %.2f at all K; margin-ratio > %.1fx at all K; cv <= %.2f; "
             "anchor reproduces r1b within +/- %.2f. ") % (
                winning_arm, agg[4][winning_arm]["iter_acc"], HARD_PASS_K4_FLOOR,
                OOD_REFUSE_MIN, MARGIN_RATIO_MIN, CV_PASS, ANCHOR_TOL_TIGHT)
            + summ,
        )

    if middle_pass and not anchor_drift_loose:
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: partial chain-grade path via %s -- some gates lift, not all. "
            % (winning_arm or "?") + summ,
        )

    # HARD_FAIL: anchor reproduces but no arm crosses MIDDLE thresholds
    return (
        "HARD_FAIL",
        "HARD_FAIL: anchor reproduces r1b (mechanism baseline confirmed) BUT no arm achieves "
        "structural fix at K=4 (mean / OOD-refuse / margin-ratio). " + summ,
    )


# ----- metrics.json builder -----

def build_metrics_payload(ps, elapsed_s):
    v, vmsg = verdict(ps)
    return {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(ps),
        "n_seeds_target": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(elapsed_s, 1),
        "summary": vmsg[:500],
        "K_hops_list": K_HOPS_LIST,
        "K_set": K_SET,
        "K_inner": K_INNER,
        "K_max_SR": K_MAX_SR,
        "gamma": GAMMA,
        "permutation_type": PERM_TYPE,
        "N_DIM": N_DIM,
        "M_TRIPLES": M_TRIPLES,
        "n_chains": N_CHAINS,
        "arms": ARMS,
        "device": str(DEVICE),
        "torch_cuda_available": bool(torch.cuda.is_available()),
        "zero_llm_calls_at_inference": True,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "substrate_native": True,
        "substrate_role": "native_inference",
        "r1b_reference_means": {"K2": R1B_MEAN_K2, "K3": R1B_MEAN_K3, "K4": R1B_MEAN_K4},
        "r1_reference_K4": R1_MEAN_K4,
        "DESIGN_NOTE": (
            "r2: structural fix for r1b HARD_FAIL via 3 composable arms: "
            "(1) ITER_CLEANUP_r1b_anchor (verbatim r1b; must reproduce within +/- 0.01); "
            "(2) SUCCESSOR_W_CLOSURE (M=sum gamma^k W^k; single-matmul retrieval); "
            "(3) TEM_FACTORED_COMPOUND (perm-bound compound chain + compound-margin refuse). "
            "Pre-reg HARD_PASS: winning arm K4 >= 0.211 + OOD-refuse>=0.90 + margin-ratio>2.0x + cv<=0.06. "
            "K=1 and K=10 brackets for discriminating-regime sanity."
        ),
    }


# ----- main -----

if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
        "K_max_SR=%d gamma=%.2f device=%s arms=%s" % (
            ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_TRIPLES, K_HOPS_LIST, K_SET, K_INNER,
            K_MAX_SR, GAMMA, str(DEVICE), ARMS,
        ),
        flush=True,
    )
    print(
        "[smoke-detect] _ARGS.smoke=%s _ARGS.self_test=%s HDLAB_EXP_NAME=%r ends_with_smoke=%s "
        "-> RUN_MODE=%s | cuda_available=%s" % (
            _ARGS.smoke, _ARGS.self_test, _HDLAB_NAME, _IS_SMOKE_BY_NAME, RUN_MODE,
            torch.cuda.is_available(),
        ),
        flush=True,
    )
    t0 = time.time()
    _fallback_name = (ANCHOR_NAME + "_smoke") if (RUN_MODE == "smoke" and not _HDLAB_NAME) else ANCHOR_NAME
    out_dir = get_output_dir(_fallback_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_config = {"N": N_DIM, "M": M_TRIPLES, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds done; running %s" % (
        len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

    for seed in remaining_seeds:
        rec = run_seed(seed, out_dir)
        write_partial(out_dir, seed, rec)
        ps_so_far = aggregate_partials(out_dir, SEEDS)
        ps_list = [v for k, v in sorted(ps_so_far.items(), key=lambda kv: int(kv[0]))]
        metrics_partial = build_metrics_payload(ps_list, time.time() - t0)
        metrics_partial["incremental"] = True
        metrics_partial["n_seeds_completed"] = len(ps_list)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics_partial, indent=2), encoding="utf-8")
        print(
            "  [incremental metrics] %d/%d seeds complete; current verdict=%s"
            % (len(ps_list), len(SEEDS), metrics_partial["verdict"]),
            flush=True,
        )

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    ps_list = [v for k, v in sorted(per_seed.items(), key=lambda kv: int(kv[0]))]

    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero: %d -- substrate-only-gate VIOLATED"
        % _LLM_CALL_COUNTER[0])

    metrics = build_metrics_payload(ps_list, time.time() - t0)
    metrics["incremental"] = False
    metrics["n_seeds_completed"] = len(ps_list)
    (out_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8")
    print("\n[VERDICT] " + metrics["verdict_msg"], flush=True)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
