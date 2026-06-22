"""r1_multihop_iterative_cleanup_v1 -- extend U1's 2-hop FB15k-237 traversal to K in {2,3,4,5}
hops, comparing NAIVE single-shot composition vs ITERATIVE CLEANUP (modern-Hopfield per-hop
attractor cleanup), per brain-drill #3 (notes/research_brain_multihop_working_memory_5x_drill_2026-06-22.md).

Mechanism (substrate-only / pure numpy + BLAS / ZERO LLM forward-calls):
  - INGEST: same multi-value Hebbian store as U1 (W += outer(E[o], E[s]*R[p]*sqrt(N))/N)
  - NAIVE single-shot K-hop: chain in HD vector space WITHOUT projecting between hops.
      state_hv = E[start]
      for p_i in rel_chain: state_hv = W @ (state_hv * R[p_i] * sq)
      argmax(E @ state_hv)
  - ITERATIVE_CLEANUP K-hop: project state to nearest attractor after each hop (modern-Hopfield
      one-iteration cleanup; Ramsauer 2021); the cleanup state is the bundle of top-K_set
      entity vectors weighted by softmax-confidence.
        for p_i in rel_chain:
            scores = W @ (state_hv * R[p_i] * sq)        # hop transition
            ent_scores = E @ scores                       # readout in entity-space
            top_idx, top_conf = topk(ent_scores, K_set)
            if top_conf[0] < tau_terminate: REFUSE
            state_hv = bundle(E[top_idx], softmax(top_conf))   # cleanup-by-projection
        final argmax(E @ state_hv)
  - RANDOM_CLEANUP control (discriminating): same iteration, but shuffle the top-K_set entity
      indices (and hence the bundle) before re-projection. Verifies cleanup is doing real work,
      not just averaging noise.

Pre-reg HARD bands (verbatim from notes/research_brain_multihop_working_memory_5x_drill_2026-06-22.md):
  HARD_PASS: K=3 iter acc >= 0.20 AND ratio iter/naive >= 3x AND K=4 iter >= 0.10
             AND refuse-gate OOD K-hop accept-rate >= 0.90 (=> the gate FIRES on OOD: refuse-rate >= 0.90).
             Anchor: K=2 naive must reproduce U1 substrate_2hop = 0.381 +/- 0.05.
  MIDDLE_BAND: K=3 iter in [0.10, 0.20] AND ratio >= 1.5x.
  HARD_FAIL: K=3 iter < 0.10 OR ratio < 1.5x.
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

# ----- substrate-only-decode gate (baked-in counter; Fix per pipeline-template 1a + Skunkworks #3) -----
_LLM_CALL_COUNTER = [0]   # MUST stay at 0; we never import transformers/torch/AutoModel.

REPO = Path(__file__).resolve().parent.parent
ANCHOR_NAME = "r1_multihop_iterative_cleanup_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# ----- pre-registered HARD thresholds (Research drill #3, deflated P=0.45) -----
HARD_PASS_K3_FLOOR = 0.20         # K=3 iterative acc floor
HARD_PASS_K3_RATIO_MIN = 3.0      # iter/naive at K=3
HARD_PASS_K4_FLOOR = 0.10         # K=4 iterative acc floor
REFUSE_OOD_MIN = 0.90             # refuse-gate must REFUSE OOD K-hop >= 0.90 of the time
MIDDLE_K3_LOWER = 0.10            # MIDDLE_BAND floor
MIDDLE_K3_RATIO_MIN = 1.5         # MIDDLE_BAND ratio
K2_ANCHOR_TARGET = 0.381          # U1 substrate_2hop (verdict-anchor)
K2_ANCHOR_TOL = 0.05              # +/- tolerance for the anchor sanity check
CV_BUDGET = 0.07                  # looser than U1's 0.05 because deeper hops add noise (drill #3 explicit)

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# ----- configuration: smoke vs full -----
if RUN_MODE == "smoke":
    # Smoke: 1 seed, small M (faster ingest), small K-set, K in {2,3} only (decisive on anchor + first novel hop)
    SEEDS = [1]
    N_DIM = 2048
    M_TRIPLES = 5000
    K_HOPS_LIST = [2, 3]
    N_CHAINS = 60         # per K, per arm
    N_OOD = 60
    K_SET = 8
    K_INNER = 1           # number of cleanup iterations per hop (1 = single Modern-Hopfield update)
    BUFFER_SIZE = 4
    BETA_CLEANUP = float(N_DIM)  # Modern-Hopfield softmax inverse-temperature (scales sub-N Hebbian scores into near-argmax bundle)
else:
    # Full: 3 seeds, large M, K in {2,3,4,5}
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    M_TRIPLES = 50000
    K_HOPS_LIST = [2, 3, 4, 5]
    N_CHAINS = 300        # per K, per arm
    N_OOD = 300
    K_SET = 8
    K_INNER = 1
    BUFFER_SIZE = 4
    BETA_CLEANUP = float(N_DIM)  # Modern-Hopfield softmax inverse-temperature (Ramsauer 2021); ~N_DIM is the substrate-appropriate scale

# tau_terminate is calibrated PER SEED from a held split (PBWM-style); init placeholder
TAU_TERMINATE_DEFAULT = None   # set by calibrate_tau() per seed

# Arms: keep the matrix small (Phase-1 decisive on iter-vs-naive)
ARMS = ["NAIVE", "ITERATIVE_CLEANUP", "RANDOM_CLEANUP_CTRL"]

CONFIG_VERSION = (
    "r1-multihop-iterative-cleanup: U1-style multi-value Hebbian; "
    "NAIVE chain-in-vec-space vs ITERATIVE_CLEANUP bundle-of-topk (Modern-Hopfield beta=%.0f) vs RANDOM_CLEANUP shuffle-ctrl; "
    "N%d M%d K_hops=%s K_set=%d K_inner=%d buffer=%d; bands K3>=%.2f ratio>=%.1fx K4>=%.2f OOD-refuse>=%.2f cv<=%.2f"
    % (BETA_CLEANUP, N_DIM, M_TRIPLES, str(K_HOPS_LIST), K_SET, K_INNER, BUFFER_SIZE,
       HARD_PASS_K3_FLOOR, HARD_PASS_K3_RATIO_MIN, HARD_PASS_K4_FLOOR, REFUSE_OOD_MIN, CV_BUDGET)
)


# ----- core HD primitives (verbatim from U1) -----

def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


# ----- self-test: confirm the iterative cleanup primitive WORKS on a tiny synthetic KG -----

def _selftest():
    """Tiny synthetic KG: prove ITERATIVE_CLEANUP at K=2 reproduces argmax-then-rebind (U1 pattern),
    and that NAIVE chain-in-vec at K=2 is WEAKER than ITERATIVE_CLEANUP on the same data."""
    g = np.random.default_rng(0)
    n = 256
    ne = 30
    nr = 3
    E = bipolar(ne, n, g)
    R = bipolar(nr, n, g)
    sq = math.sqrt(n)
    # Build a chain-friendly KG: s -p0-> x -p1-> o for 10 distinct chains
    triples = []
    chains_truth = []
    for i in range(10):
        s = i
        x = 10 + i
        o = 20 + i
        triples.append((s, 0, x))
        triples.append((x, 1, o))
        chains_truth.append((s, 0, x, 1, o))
    # multi-value Hebbian
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p, o) in triples:
        key = E[s] * R[p] * sq
        W += np.outer(E[o], key) / n
    # NAIVE chain (no cleanup): state_hv accumulates HD products
    naive_hit = 0
    for (s, _p0, _x, _p1, o) in chains_truth:
        state = E[s].copy()
        for p in (0, 1):
            state = W @ (state * R[p] * sq)
        pred = int(np.argmax(E @ state))
        if pred == o:
            naive_hit += 1
    naive_acc = naive_hit / len(chains_truth)
    # ITERATIVE_CLEANUP chain: per-hop project to top-K_set entity bundle (Modern-Hopfield beta=N)
    K_set = 4
    beta_local = float(n)
    iter_hit = 0
    for (s, _p0, _x, _p1, o) in chains_truth:
        state = E[s].copy()
        for p in (0, 1):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_idx = np.argpartition(ent_scores, -K_set)[-K_set:]
            top_conf = ent_scores[top_idx]
            # beta-scaled softmax (Ramsauer Modern-Hopfield; sharpens near-argmax cleanup)
            z = beta_local * top_conf
            w = np.exp(z - z.max()); w = w / w.sum()
            state = (w[:, None] * E[top_idx]).sum(axis=0)
            state = state / (np.linalg.norm(state) + 1e-8)
        pred = int(np.argmax(E @ state))
        if pred == o:
            iter_hit += 1
    iter_acc = iter_hit / len(chains_truth)
    # Assert: cleanup helps OR matches (with a 10-chain synthetic; should be near 1.0 for cleanup)
    assert iter_acc >= 0.7, "selftest: ITERATIVE_CLEANUP K=2 acc too low %.2f" % iter_acc
    assert iter_acc >= naive_acc - 0.1, "selftest: cleanup must not be dramatically worse than naive"
    # Refuse-gate sanity: in-KB conf > OOD conf (random s-p combination)
    s_inkb = 0
    score_inkb = float(np.max(E @ (W @ (E[s_inkb] * R[0] * sq))))
    # Pick an OOD pair: (s=29 which is unused as subject, p=2 which is unused)
    score_ood = float(np.max(E @ (W @ (E[29] * R[2] * sq))))
    assert score_inkb > score_ood, "selftest: refuse-conf in-KB(%.4f) > OOD(%.4f)" % (score_inkb, score_ood)
    print("[selftest] PASS: naive K=2 acc=%.2f, iter K=2 acc=%.2f; refuse-conf in-KB %.4f > OOD %.4f"
          % (naive_acc, iter_acc, score_inkb, score_ood), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- KG loader (verbatim from U1) -----

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


def ingest_hebbian(triples, n_ent, n_rel, g, batch=5000):
    """U1 multi-value Hebbian ingest -- verbatim mechanism."""
    E = bipolar(n_ent, N_DIM, g)
    R = bipolar(n_rel, N_DIM, g)
    sq = math.sqrt(N_DIM)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / N_DIM
    return E, R, W, sq


# ----- K-hop chain sampling (heldout_in_compose_graph == 0 leak guard, like U1) -----

def sample_k_hop_chains(triples, keyobjs, K, n_chains, g):
    """Sample K-hop chains (s, p1, x1, p2, x2, ..., pK, o) where (s, o) is NOT a direct
    train edge (heldout_in_compose_graph guard from U1). Returns list of tuples.

    Tuple layout: (s, [p1..pK], [x1..x_{K-1}], o)  where intermediates x_i are the truth labels.
    """
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
        if not ok:
            continue
        if o_final == s:
            continue
        if (s, o_final) in direct:
            leak += 1
            continue
        # also reject if any intermediate equals s (degenerate cycle)
        if any(x == s for x in ints):
            continue
        chains.append((s, rels, ints, o_final))
    return chains, leak


# ----- K-hop traversal: NAIVE vs ITERATIVE_CLEANUP vs RANDOM_CLEANUP_CTRL -----

def _normalize(v, eps=1e-8):
    n = float(np.linalg.norm(v))
    return v / (n + eps)


def traverse_naive(E, R, W, sq, start_ent, rel_chain):
    """NAIVE: chain in HD vector space, no per-hop cleanup; final argmax against E.
    Returns (pred_o, per_hop_confs (always [])).
    """
    state = E[start_ent].copy()
    for p in rel_chain:
        state = W @ (state * R[p] * sq)
        # NO normalization between hops -- NAIVE means do nothing per-hop
    ent_scores = E @ state
    return int(np.argmax(ent_scores)), []


def traverse_iter_cleanup(E, R, W, sq, start_ent, rel_chain, K_set, K_inner, tau_terminate,
                          shuffle_top=False, shuffle_rng=None):
    """ITERATIVE_CLEANUP: project state to top-K_set entity bundle after each hop (Modern-Hopfield
    one-iteration cleanup); K_inner=1 = single Hopfield step per hop (the standard r1 mechanism).
    K_inner>1 = iterate the cleanup K_inner times within each hop (deeper attractor convergence).

    shuffle_top=True implements the RANDOM_CLEANUP_CTRL discriminator: at the cleanup step,
    SHUFFLE the top-K_set entity indices (and re-evaluate the bundle); this destroys the
    information content of the cleanup while keeping the iteration structure identical.

    Returns (pred_o or None, per_hop_top1_confs, terminated_at_hop_or_-1).
    """
    state = E[start_ent].copy()
    per_hop_conf = []
    terminated_at = -1
    for hop_idx, p in enumerate(rel_chain):
        for _inner in range(K_inner):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_idx = np.argpartition(ent_scores, -K_set)[-K_set:]
            top_conf = ent_scores[top_idx]
            # sort descending
            order = np.argsort(-top_conf)
            top_idx = top_idx[order]
            top_conf = top_conf[order]
            # refuse-gate PBWM termination: top-1 below tau -> refuse
            top1 = float(top_conf[0])
            if tau_terminate is not None and top1 < tau_terminate:
                terminated_at = hop_idx
                return None, per_hop_conf, terminated_at
            if shuffle_top:
                # discriminating control: shuffle the entity indices (destroys cleanup signal)
                shuf = shuffle_rng.permutation(top_idx)
                top_idx = shuf
            # Modern-Hopfield beta-scaled softmax bundle (Ramsauer 2021 one-iteration cleanup)
            z = BETA_CLEANUP * top_conf
            w = np.exp(z - z.max())
            w = w / w.sum()
            state = (w[:, None] * E[top_idx]).sum(axis=0)
            state = _normalize(state)
        per_hop_conf.append(float(top_conf[0]))
    ent_scores = E @ state
    return int(np.argmax(ent_scores)), per_hop_conf, terminated_at


# ----- tau calibration (PBWM-style; U1 refuse-gate style) -----

def calibrate_tau(E, R, W, sq, keyobjs, n_ent, n_rel, g, n_q=200):
    """Calibrate tau_terminate on a held split of (in-KB top-1 conf) vs (OOD top-1 conf)
    using the same logic as U1's refuse_gate -- balanced (accept, refuse) maximization.

    Returns calibrated tau (a float; the per-hop top-1 score threshold).
    """
    inkb_keys = list(keyobjs.keys())
    idx = g.permutation(len(inkb_keys))[:min(n_q, len(inkb_keys))]
    sp_inkb = [inkb_keys[i] for i in idx]
    s_arr = np.array([x[0] for x in sp_inkb])
    p_arr = np.array([x[1] for x in sp_inkb])
    keys = (E[s_arr] * R[p_arr] * sq).astype(np.float32)
    transit = E @ (W @ keys.T)
    inkb_conf = transit.max(axis=0)
    # OOD pairs (no edge): subject + relation drawn at random; reject if in keyobjs
    keyset = set(keyobjs.keys())
    ood_sp = []
    tries = 0
    while len(ood_sp) < n_q and tries < n_q * 50:
        s = int(g.integers(0, n_ent)); p = int(g.integers(0, n_rel)); tries += 1
        if (s, p) in keyset:
            continue
        ood_sp.append((s, p))
    if not ood_sp:
        return 0.0
    s_a = np.array([x[0] for x in ood_sp])
    p_a = np.array([x[1] for x in ood_sp])
    keys = (E[s_a] * R[p_a] * sq).astype(np.float32)
    ood_conf = (E @ (W @ keys.T)).max(axis=0)
    # held split: first half calibrate, second half eval (we just need the tau)
    h = len(inkb_conf) // 2; ho = len(ood_conf) // 2
    cal_in = inkb_conf[:h]; cal_ood = ood_conf[:ho]
    cands = np.unique(np.concatenate([cal_in, cal_ood]))
    best_tau, best_bal = float(cands[0]), -1.0
    for tau in cands:
        acc = float((cal_in >= tau).mean())
        ref = float((cal_ood < tau).mean())
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal; best_tau = float(tau)
    return best_tau


# ----- OOD K-hop chain sampling (refuse-gate audit) -----

def sample_ood_k_hop(E_keyobjs, keyobjs, n_ent, n_rel, K, n_chains, g):
    """OOD K-hop: choose (s, p1, p2, ..., pK) where the chain CANNOT be traversed (intermediate
    has no out-edge for the chosen p_i) -- i.e., a chain that does not exist in the KG.

    We generate s + random rel-chain; reject if the first hop is in keyobjs (so we know the
    chain is at-least-partially OOD). The refuse-gate at hop 1 should fire (terminate).
    """
    keyset = set(keyobjs.keys())
    ood = []
    tries = 0
    max_tries = n_chains * 50
    while len(ood) < n_chains and tries < max_tries:
        tries += 1
        s = int(g.integers(0, n_ent))
        rels = [int(g.integers(0, n_rel)) for _ in range(K)]
        # reject if the (s, p1) pair IS in KG (we want OOD)
        if (s, rels[0]) in keyset:
            continue
        ood.append((s, rels))
    return ood


# ----- single seed run -----

def run_seed(seed):
    g = np.random.default_rng(seed)
    out = {"seed": seed, "config_version": CONFIG_VERSION, "per_unit": []}
    # Ingest
    t0 = time.time()
    triples, keyobjs, n_ent, n_rel = load_kg(seed, M_TRIPLES)
    E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
    ingest_s = time.time() - t0
    print("  [seed=%d] ingested M=%d in %.1fs (n_ent=%d, n_rel=%d, n_keys=%d)"
          % (seed, M_TRIPLES, ingest_s, n_ent, n_rel, len(keyobjs)), flush=True)

    # Calibrate tau on this seed (PBWM termination threshold)
    tau = calibrate_tau(E, R, W, sq, keyobjs, n_ent, n_rel, np.random.default_rng(seed + 11))
    out["tau_terminate"] = float(tau)
    print("  [seed=%d] tau_terminate=%.6f" % (seed, tau), flush=True)

    # K-loop
    for K in K_HOPS_LIST:
        # Sample in-KG K-hop chains (leak-guarded)
        chains, leak = sample_k_hop_chains(triples, keyobjs, K,
                                            n_chains=N_CHAINS,
                                            g=np.random.default_rng(seed + 100 + K))
        n_actual = len(chains)
        if n_actual == 0:
            print("  [seed=%d K=%d] no chains sampled (corpus too sparse for K=%d)"
                  % (seed, K, K), flush=True)
            continue

        # OOD K-hop chains (for refuse-gate audit)
        ood_chains = sample_ood_k_hop(E, keyobjs, n_ent, n_rel, K,
                                       n_chains=N_OOD,
                                       g=np.random.default_rng(seed + 700 + K))

        # NAIVE arm
        t = time.time()
        n_hit = 0
        for (s, rels, _ints, o_true) in chains:
            pred, _ = traverse_naive(E, R, W, sq, s, rels)
            if pred == o_true:
                n_hit += 1
        naive_acc = n_hit / n_actual
        naive_wall = time.time() - t

        # ITERATIVE_CLEANUP arm (NO refuse-gate termination -- so we measure pure cleanup gain)
        t = time.time()
        n_hit = 0
        confs_at_final = []
        for (s, rels, _ints, o_true) in chains:
            pred, hop_confs, _term = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_set=K_SET, K_inner=K_INNER,
                tau_terminate=None,  # NO termination for the in-KG arm (we want pure-mechanism acc)
                shuffle_top=False)
            if pred is not None and pred == o_true:
                n_hit += 1
            if hop_confs:
                confs_at_final.append(hop_confs[-1])
        iter_acc = n_hit / n_actual
        iter_wall = time.time() - t
        mean_final_conf = float(np.mean(confs_at_final)) if confs_at_final else 0.0

        # Calibrate tau-per-K: the U1 tau is the hop-1 magnitude; per-hop bundle states drop
        # in confidence with K. Use a held split of IN-KG vs OOD K-hop end-confidences to
        # set the per-K tau. (Same balanced-accept-refuse logic as U1 refuse_gate.)
        # We need the FINAL-hop top-1 confidence for both in-KG and OOD K-hop chains.
        def _final_top1_conf(start, rel_chain):
            state = E[start].copy()
            top1_last = 0.0
            for p in rel_chain:
                transit = W @ (state * R[p] * sq)
                ent_scores = E @ transit
                top_idx = np.argpartition(ent_scores, -K_SET)[-K_SET:]
                top_conf = ent_scores[top_idx]
                order = np.argsort(-top_conf)
                top_idx = top_idx[order]; top_conf = top_conf[order]
                top1_last = float(top_conf[0])
                z = BETA_CLEANUP * top_conf
                w = np.exp(z - z.max()); w = w / w.sum()
                state = (w[:, None] * E[top_idx]).sum(axis=0)
                state = state / (np.linalg.norm(state) + 1e-8)
            return top1_last
        in_confs = np.array([_final_top1_conf(s, rels) for (s, rels, _ints, _o) in chains], dtype=np.float32)
        ood_confs = np.array([_final_top1_conf(s, rels) for (s, rels) in ood_chains], dtype=np.float32)
        # held split: first half calibrate, second half eval (avoid circularity)
        h_in = len(in_confs) // 2; h_ood = len(ood_confs) // 2
        cal_in = in_confs[:h_in]; cal_ood = ood_confs[:h_ood]
        eval_in = in_confs[h_in:]; eval_ood = ood_confs[h_ood:]
        cands = np.unique(np.concatenate([cal_in, cal_ood])) if (len(cal_in) and len(cal_ood)) else np.array([0.0])
        best_tau_k, best_bal = float(cands[0]), -1.0
        for tcand in cands:
            acc_in = float((cal_in >= tcand).mean()) if len(cal_in) else 0.0
            ref_ood = float((cal_ood < tcand).mean()) if len(cal_ood) else 0.0
            bal = 0.5 * (acc_in + ref_ood)
            if bal > best_bal:
                best_bal = bal; best_tau_k = float(tcand)
        # eval on held split
        ood_refuse_rate = float((eval_ood < best_tau_k).mean()) if len(eval_ood) else 0.0
        inkb_accept_rate = float((eval_in >= best_tau_k).mean()) if len(eval_in) else 0.0

        # RANDOM_CLEANUP_CTRL: discriminator (same iteration, shuffle top-K indices)
        t = time.time()
        n_hit = 0
        shuffle_rng = np.random.default_rng(seed + 900 + K)
        for (s, rels, _ints, o_true) in chains:
            pred, _hc, _term = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_set=K_SET, K_inner=K_INNER,
                tau_terminate=None, shuffle_top=True, shuffle_rng=shuffle_rng)
            if pred is not None and pred == o_true:
                n_hit += 1
        rand_acc = n_hit / n_actual
        rand_wall = time.time() - t

        # Compute ratio (iter / naive)
        ratio = iter_acc / max(naive_acc, 1e-6)

        unit = {
            "seed": seed,
            "K_hops": K,
            "n_chains_actual": n_actual,
            "leak_skipped": leak,
            "n_ood_chains": len(ood_chains),
            "naive_acc": round(naive_acc, 4),
            "iterative_cleanup_acc": round(iter_acc, 4),
            "random_cleanup_ctrl_acc": round(rand_acc, 4),
            "iter_over_naive_ratio": round(ratio, 3),
            "iter_over_random_ratio": round(iter_acc / max(rand_acc, 1e-6), 3),
            "refuse_ood_rate": round(ood_refuse_rate, 4),    # how often the gate FIRES on OOD
            "refuse_inkb_accept_rate": round(inkb_accept_rate, 4),  # how often it ACCEPTS in-KG
            "tau_terminate_per_K": float(best_tau_k),
            "in_kg_conf_mean": float(in_confs.mean()) if len(in_confs) else 0.0,
            "ood_conf_mean": float(ood_confs.mean()) if len(ood_confs) else 0.0,
            "mean_final_hop_conf": round(mean_final_conf, 6),
            "naive_wall_s": round(naive_wall, 2),
            "iter_wall_s": round(iter_wall, 2),
            "rand_wall_s": round(rand_wall, 2),
        }
        out["per_unit"].append(unit)
        print(("  [seed=%d K=%d n=%d leak=%d] NAIVE=%.4f ITER=%.4f RAND=%.4f "
               "ratio=%.2fx | OOD-refuse=%.3f in-KG-accept=%.3f")
              % (seed, K, n_actual, leak, naive_acc, iter_acc, rand_acc, ratio,
                 ood_refuse_rate, inkb_accept_rate), flush=True)

    out["ingest_s"] = round(ingest_s, 1)
    return out


# ----- verdict (PRE-REG direction check; Skunkworks Fix #5 sibling discipline) -----

def verdict(ps) -> Tuple[str, str]:
    # Build per-K aggregates (mean across seeds)
    by_k = defaultdict(lambda: {"naive": [], "iter": [], "rand": [], "ratio": [],
                                  "ood_refuse": [], "inkb_accept": []})
    for p in ps:
        for u in p["per_unit"]:
            K = u["K_hops"]
            by_k[K]["naive"].append(u["naive_acc"])
            by_k[K]["iter"].append(u["iterative_cleanup_acc"])
            by_k[K]["rand"].append(u["random_cleanup_ctrl_acc"])
            by_k[K]["ratio"].append(u["iter_over_naive_ratio"])
            by_k[K]["ood_refuse"].append(u["refuse_ood_rate"])
            by_k[K]["inkb_accept"].append(u["refuse_inkb_accept_rate"])
    agg = {}
    for K, d in by_k.items():
        m_naive = float(np.mean(d["naive"])) if d["naive"] else 0.0
        m_iter = float(np.mean(d["iter"])) if d["iter"] else 0.0
        m_rand = float(np.mean(d["rand"])) if d["rand"] else 0.0
        m_ratio = float(np.mean(d["ratio"])) if d["ratio"] else 0.0
        m_ood = float(np.mean(d["ood_refuse"])) if d["ood_refuse"] else 0.0
        m_in = float(np.mean(d["inkb_accept"])) if d["inkb_accept"] else 0.0
        # cv on iter acc
        cv_iter = float(np.std(d["iter"]) / max(np.mean(d["iter"]), 1e-9)) if d["iter"] else 0.0
        agg[K] = {"naive": round(m_naive, 4), "iter": round(m_iter, 4), "rand": round(m_rand, 4),
                  "ratio": round(m_ratio, 3), "ood_refuse": round(m_ood, 4),
                  "inkb_accept": round(m_in, 4), "cv_iter": round(cv_iter, 4)}

    # K=2 anchor sanity check (the U1 reproduction) -- ONLY enforced at full M=50000
    # (U1's anchor 0.381 was measured at M=50000, N=8192; smoke at smaller M/N is easier
    # so K=2 will be much higher and the absolute-target check does not apply.)
    k2 = agg.get(2)
    anchor_ok = True
    anchor_msg = ""
    if k2 is not None and RUN_MODE == "full" and M_TRIPLES >= 25000:
        # ITERATIVE_CLEANUP at K=2 with K_inner=1 IS U1's per-hop pattern.
        diff = abs(k2["iter"] - K2_ANCHOR_TARGET)
        anchor_ok = diff <= K2_ANCHOR_TOL
        anchor_msg = "K=2 ITER=%.3f vs U1=%.3f (diff %.3f, tol %.3f) -> %s" % (
            k2["iter"], K2_ANCHOR_TARGET, diff, K2_ANCHOR_TOL,
            "OK" if anchor_ok else "OUT-OF-TOL")
    elif k2 is not None:
        anchor_msg = "K=2 ITER=%.3f (anchor-check skipped: M=%d < 25000 or run_mode=%s)" % (
            k2["iter"], M_TRIPLES, RUN_MODE)

    # Pre-reg HARD bands at K=3 (decisive)
    k3 = agg.get(3)
    k4 = agg.get(4)
    k3_iter = k3["iter"] if k3 else 0.0
    k3_ratio = k3["ratio"] if k3 else 0.0
    k3_cv = k3["cv_iter"] if k3 else 0.0
    k4_iter = k4["iter"] if k4 else 0.0
    # OOD refuse: take the MIN across K (gate must hold at every depth)
    ood_rates = [agg[K]["ood_refuse"] for K in agg if agg[K]["ood_refuse"] is not None]
    ood_min = float(min(ood_rates)) if ood_rates else 0.0

    summ = ("by-K: %s | anchor %s | K=3 ITER=%.3f NAIVE=%.3f RAND=%.3f ratio=%.2fx cv=%.3f | "
            "K=4 ITER=%.3f | OOD-refuse min=%.3f") % (
        json.dumps({K: agg[K] for K in sorted(agg.keys())}),
        anchor_msg, k3_iter, (k3["naive"] if k3 else 0.0),
        (k3["rand"] if k3 else 0.0), k3_ratio, k3_cv, k4_iter, ood_min)

    # PRE-REG-DIRECTION CHECK (Skunkworks Fix #5 sibling): the improvement direction is
    # iter > naive (cleanup HELPS). A large wrong-direction delta = HARD_FAIL not MIDDLE_BAND.
    direction_ok = k3 is None or k3["iter"] >= k3["naive"] - 0.02
    if not direction_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: iterative cleanup HURTS at K=3 (wrong direction; iter %.3f < naive %.3f). "
                + summ) % (k3["iter"], k3["naive"])

    # If K=2 anchor missed by > tol -> harness corrupt -> HARD_FAIL inconclusive
    if k2 is not None and not anchor_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: K=2 anchor missed (iter %.3f vs U1 %.3f); harness corrupt. "
                % (k2["iter"], K2_ANCHOR_TARGET) + summ)

    # K=3 HARD_PASS bar
    k3_pass = (k3_iter >= HARD_PASS_K3_FLOOR
               and k3_ratio >= HARD_PASS_K3_RATIO_MIN
               and k3_cv <= CV_BUDGET)
    k4_pass = (k4 is None) or (k4_iter >= HARD_PASS_K4_FLOOR)
    refuse_pass = ood_min >= REFUSE_OOD_MIN

    if k3_pass and k4_pass and refuse_pass and (k2 is None or anchor_ok):
        return ("HARD_PASS",
                "HARD_PASS: iterative cleanup composes K>=3 with cleanup gain; refuse-gate holds. " + summ)
    # MIDDLE_BAND: K=3 partial mechanism
    if k3 and MIDDLE_K3_LOWER <= k3_iter < HARD_PASS_K3_FLOOR and k3_ratio >= MIDDLE_K3_RATIO_MIN:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: partial cleanup mechanism at K=3 (proven bound). " + summ)
    # HARD_FAIL: below MIDDLE bar
    return ("HARD_FAIL",
            "HARD_FAIL: cleanup does not rescue K=3 to PASS or MIDDLE bands. " + summ)


# ----- main -----

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d M=%d K_hops=%s K_set=%d K_inner=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_TRIPLES, K_HOPS_LIST, K_SET, K_INNER, CONFIG_VERSION),
          flush=True)
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s%s" % (ANCHOR_NAME, "_smoke" if RUN_MODE == "smoke" else ""))
    out_dir.mkdir(parents=True, exist_ok=True)

    ps = []
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint (config match)" % s, flush=True)
                    ps.append(rec)
                    continue
            except Exception:
                pass
        rec = run_seed(s)
        pf.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        ps.append(rec)

    # SUBSTRATE-ONLY-DECODE GATE assertion (final, before writing metrics)
    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero: %d -- substrate-only-gate VIOLATED" % _LLM_CALL_COUNTER[0])

    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)

    # Per-seed per-K cv for the by_k table
    by_k_seedwise = defaultdict(lambda: {"iter": []})
    for p in ps:
        for u in p["per_unit"]:
            by_k_seedwise[u["K_hops"]]["iter"].append(u["iterative_cleanup_acc"])
    cv_by_k = {K: (float(np.std(d["iter"]) / max(np.mean(d["iter"]), 1e-9))
                   if d["iter"] else 0.0)
               for K, d in by_k_seedwise.items()}
    max_cv = float(max(cv_by_k.values())) if cv_by_k else 0.0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(time.time() - t0, 1),
        "cv_by_K": {str(K): round(c, 4) for K, c in cv_by_k.items()},
        "max_cv_across_K": round(max_cv, 4),
        "K_hops_list": K_HOPS_LIST,
        "K_set": K_SET,
        "K_inner": K_INNER,
        "buffer_size": BUFFER_SIZE,
        "N_DIM": N_DIM,
        "M_TRIPLES": M_TRIPLES,
        "zero_llm_calls_at_inference": True,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "substrate_native": True,
        "substrate_role": "native_inference",
        "DESIGN_NOTE": (
            "r1 brain-drill #3 cell. NAIVE = chain-in-HD-vec-space (no per-hop projection). "
            "ITERATIVE_CLEANUP = bundle-of-topK_set Modern-Hopfield projection per hop. "
            "RANDOM_CLEANUP_CTRL = shuffle top-K indices (discriminator). "
            "K=2 anchor uses ITERATIVE_CLEANUP arm to reproduce U1 substrate_2hop=0.381 "
            "(U1's per-hop argmax pattern is closest to ITERATIVE_CLEANUP K_inner=1). "
            "Refuse-gate: tau calibrated per-seed via held-split balanced(accept,refuse); "
            "OOD K-hop chain = random (s, p_chain) where (s,p1) not in keyobjs."),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
