"""r1b_multihop_refuse_calibration_v1 -- r1 chain-grade promotion path per brain-drill #3.

r1 (commit 3a0fb256, MIDDLE_BAND) demonstrated iterative-Hopfield cleanup composes K=3,4
with chain-grade magnitudes but missed TWO strict pre-reg gates:
  (g1) K=3 cv = 0.145 > 0.07 (seed-noise; 3 seeds x 200 chains too sparse)
  (g2) OOD-refuse mean 0.53-0.72 < 0.90 (absolute-conf threshold wrong reference
       distribution for multi-hop bundle-compressed intermediates)

r1b lifts both gates while reproducing r1's per-K means within +/- 0.02:
  (g1 fix) 7 seeds (vs r1's 3) + 500 chains per K (vs r1's 200): combined sqrt(7/3)*sqrt(5/2)
           ~ 2.4x cv reduction (target cv <= 0.06 at K=3)
  (g2 fix) MARGIN-based refuse-signal (top1 - top2) instead of absolute top1; calibrated
           per-K on held-split (separate train/val/test); target OOD-refuse mean >= 0.90 at
           K=2,3,4

Discriminating controls (to keep mechanism honest):
  (c1) Mean reproduction at K=2,3,4 within +/- 0.02 of r1's [0.395, 0.240, 0.172]
       (verifies r1b didn't break the cleanup mechanism)
  (c2) Margin must SEPARATE in-KB from OOD substantially (target margin-ratio > 2x)
       (if margin doesn't separate, the refuse-signal redesign itself failed)

Mechanism inherited verbatim from r1 (commit 3a0fb256):
  - Multi-value Hebbian ingest (U1)
  - Iterative cleanup: Modern-Hopfield one-iteration bundle-of-topK projection per hop
    (Ramsauer 2021; beta = N_DIM softmax scale)
  - FB15k-237 50k corpus; K_inner=1; K_set=8; N_DIM=8192; M_TRIPLES=50000
  - CERT 591 contrastive projection harness compatible (no projection here; this cell tests
    the multi-hop pipeline at the *substrate-native* layer just like r1)

Smoke detection: cell detects smoke via --smoke arg OR HDLAB_EXP_NAME endswith "_smoke"
(runner overrides HDLAB_RUN_MODE=full unconditionally; the entry-name suffix is the only
signal the runner respects). Adopted from sibling cells (c1_cls_replay, csp_hebbian) and
patched template TODO #6.

Wall-budget pre-check (template TODO #8): full grid 7 seeds x K in {2,3,4} x 500 chains x
3 arms x N=8192. r1 ran 3 seeds x 3 K x 200 chains x 3 arms in ~25min = ~1500s. Linear in
seeds * chains => 1500 * (7/3) * (500/200) ~ 8750s. Add 1.5x safety => budget 13125s.
Round up to 14400 (4h) per PROT-019 _n8192 floor (also satisfies PROT-021 checkpoint
requirement via _seed_checkpoint).

Partial-recovery (template TODO #9): cell writes per-seed partials atomically AND emits
metrics.json incrementally after each seed (so a timeout still leaves a valid metrics.json
with the seeds completed so far + a verdict computed off the partials).

Pre-reg HARD bands (from notes/research_brain_multihop_working_memory_5x_drill_2026-06-22.md
+ task pre-reg in this cycle):
  HARD_PASS (r1 chain-grade promotion):
    r1b means at K=2,3,4 within +/- 0.02 of r1 [0.395, 0.240, 0.172] AND
    K=3 cv <= 0.06 AND
    OOD-refuse mean >= 0.90 at K=2,3,4 (margin-based, held-test split)
  MIDDLE_BAND (partial path): one of two strict gates lifts, not both
  HARD_FAIL: means reproduce BUT both gates still miss => rigor-fundamentally-limited;
    route to brain-drill #4 (alternative mechanism)
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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)

# ----- substrate-only-decode gate (baked-in counter; Skunkworks structural blocker #3) -----
_LLM_CALL_COUNTER = [0]   # MUST stay at 0; we never import transformers/torch/AutoModel.

ANCHOR_NAME = "r1b_multihop_refuse_calibration_v1"
KG_PATH = REPO / "data" / "datasets" / "fb15k_237_train_50k.jsonl"

# ----- r1 reference means (cited from notes/r1_multihop_iterative_cleanup_complete_2026-06-22.md,
# re-derived from per_seed -- not phantoms) -----
R1_MEAN_K2 = 0.395
R1_MEAN_K3 = 0.240
R1_MEAN_K4 = 0.172
MEAN_REPRO_TOL = 0.02     # +/- 0.02 mean-reproduction band (task pre-reg)

# ----- pre-registered HARD thresholds for r1b chain-grade promotion -----
CV_K3_PASS = 0.06         # target K=3 cv after seed-noise reduction (target <= 0.07 with margin)
OOD_REFUSE_MIN = 0.90     # target OOD-refuse mean across K=2,3,4 (margin-based, held-test split)
MARGIN_RATIO_MIN = 2.0    # discriminating control: in-KB margin / OOD margin must be > 2x

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

# Smoke detection: --smoke flag OR HDLAB_EXP_NAME ending in _smoke (runner sets HDLAB_RUN_MODE=full
# unconditionally; the entry-name suffix is the only signal the runner respects).
_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# ----- configuration: smoke vs full -----
if RUN_MODE == "smoke":
    # Smoke: 1 seed, small M, K in {2,3} only, 100 chains; goal = verify mean reproduces r1
    # at K=2 and margin-calibration converges. Fits in <5min single-CPU.
    SEEDS = [1]
    N_DIM = 2048
    M_TRIPLES = 5000
    K_HOPS_LIST = [2, 3]
    N_CHAINS = 100
    N_OOD = 100
    K_SET = 8
    K_INNER = 1
    BETA_CLEANUP = float(N_DIM)
else:
    # Full Phase-1: 7 seeds x K in {2,3,4} x 500 chains x N=8192 x M=50000
    # Drop K=5 per r1 cost finding; defer to Phase 2.
    # Budget: 7 seeds * (K2+K3+K4) wall * 3 arms ~ 8750s estimated (linear in seeds*chains).
    # Conservative timeout 14400s = 4h. Per-seed checkpoint resume on timeout.
    SEEDS = [7, 17, 23, 31, 41, 53, 67]   # 7 seeds (vs r1's 3); evenly spaced primes
    N_DIM = 8192
    M_TRIPLES = 50000
    K_HOPS_LIST = [2, 3, 4]
    N_CHAINS = 500                         # vs r1's 200 (2.5x for cv reduction)
    N_OOD = 500                            # match in-KB chain count for held-split balance
    K_SET = 8
    K_INNER = 1
    BETA_CLEANUP = float(N_DIM)

ARMS = ["ITERATIVE_CLEANUP"]    # r1b only runs the ITER arm (refuse-cal focus); r1 already
                                # validated NAIVE/RANDOM controls. Reproducing r1's means
                                # cross-checks ITER arm; controls re-runs are redundant.

# tau_margin calibration method: balanced-(accept, refuse) maximization on held-CAL split,
# evaluated on held-TEST split (avoids circularity)
TAU_MARGIN_METHOD = "held_split_balanced_accrefuse"

CONFIG_VERSION = (
    "r1b-multihop-refuse-cal: r1 iterative-cleanup mechanism (Modern-Hopfield beta=%.0f); "
    "MARGIN-based refuse (top1-top2) calibrated per-K via %s; "
    "N%d M%d K_hops=%s K_set=%d K_inner=%d n_seeds=%d n_chains=%d; "
    "bands mean-repro+/-%.2f K3cv<=%.2f OOD-refuse-mean>=%.2f margin-ratio>%.1fx"
    % (BETA_CLEANUP, TAU_MARGIN_METHOD, N_DIM, M_TRIPLES, str(K_HOPS_LIST), K_SET, K_INNER,
       len(SEEDS), N_CHAINS, MEAN_REPRO_TOL, CV_K3_PASS, OOD_REFUSE_MIN, MARGIN_RATIO_MIN)
)


# ----- core HD primitives (verbatim from r1 / U1) -----

def bipolar(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _normalize(v, eps=1e-8):
    n = float(np.linalg.norm(v))
    return v / (n + eps)


# ----- self-test: confirm iterative-cleanup + margin-refuse on a tiny synthetic KG -----

def _selftest():
    """Tiny synthetic KG: prove ITERATIVE_CLEANUP K=2 + margin-refuse signal SEPARATES in-KB
    from OOD."""
    g = np.random.default_rng(0)
    n = 256
    ne = 30
    nr = 3
    E = bipolar(ne, n, g)
    R = bipolar(nr, n, g)
    sq = math.sqrt(n)
    # Build chains: s -p0-> x -p1-> o for 10 distinct chains
    triples = []
    chains_truth = []
    for i in range(10):
        s, x, o = i, 10 + i, 20 + i
        triples.append((s, 0, x))
        triples.append((x, 1, o))
        chains_truth.append((s, [0, 1], o))
    # multi-value Hebbian
    W = np.zeros((n, n), dtype=np.float32)
    for (s, p, o) in triples:
        key = E[s] * R[p] * sq
        W += np.outer(E[o], key) / n
    K_set = 4
    beta_local = float(n)
    iter_hit = 0
    inkb_margins = []
    ood_margins = []
    for (s, rels, o_true) in chains_truth:
        state = E[s].copy()
        last_top1 = 0.0
        last_top2 = 0.0
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_idx = np.argpartition(ent_scores, -K_set)[-K_set:]
            top_conf = ent_scores[top_idx]
            order = np.argsort(-top_conf)
            top_idx = top_idx[order]
            top_conf = top_conf[order]
            last_top1 = float(top_conf[0])
            last_top2 = float(top_conf[1])
            z = beta_local * top_conf
            w = np.exp(z - z.max()); w = w / w.sum()
            state = (w[:, None] * E[top_idx]).sum(axis=0)
            state = _normalize(state)
        pred = int(np.argmax(E @ state))
        if pred == o_true:
            iter_hit += 1
        inkb_margins.append(last_top1 - last_top2)
    iter_acc = iter_hit / len(chains_truth)
    # OOD margins: random (s, p_chain) where p[0] is unused
    for trial in range(10):
        s = 29
        rels = [2, 0]  # p=2 unused; p=0 then
        state = E[s].copy()
        last_top1 = 0.0
        last_top2 = 0.0
        for p in rels:
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_idx = np.argpartition(ent_scores, -K_set)[-K_set:]
            top_conf = ent_scores[top_idx]
            order = np.argsort(-top_conf)
            top_idx = top_idx[order]; top_conf = top_conf[order]
            last_top1 = float(top_conf[0])
            last_top2 = float(top_conf[1])
            z = beta_local * top_conf
            w = np.exp(z - z.max()); w = w / w.sum()
            state = (w[:, None] * E[top_idx]).sum(axis=0)
            state = _normalize(state)
        ood_margins.append(last_top1 - last_top2)
    inkb_mean = float(np.mean(inkb_margins))
    ood_mean = float(np.mean(ood_margins))
    assert iter_acc >= 0.7, "selftest: ITERATIVE_CLEANUP K=2 acc too low %.2f" % iter_acc
    assert inkb_mean > ood_mean, (
        "selftest: in-KB margin %.4f must exceed OOD margin %.4f -- margin-signal degenerate"
        % (inkb_mean, ood_mean))
    print(
        "[selftest] PASS: iter K=2 acc=%.2f; in-KB margin %.4f > OOD margin %.4f (ratio %.2fx)"
        % (iter_acc, inkb_mean, ood_mean,
           inkb_mean / max(abs(ood_mean), 1e-9)),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- KG loader (verbatim from r1 / U1) -----

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


# ----- K-hop chain sampling (heldout_in_compose_graph == 0 leak guard; r1 / U1) -----

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


# ----- ITERATIVE_CLEANUP traversal with margin-instrumented per-hop top1/top2 -----

def traverse_iter_cleanup(E, R, W, sq, start_ent, rel_chain, K_set, K_inner):
    """ITERATIVE_CLEANUP K-hop. Returns (pred_o, final_top1, final_top2, per_hop_top1, per_hop_top2).
    No tau-termination during traversal (we collect final-hop top1/top2 + run the margin-gate
    POST-traversal on the FINAL-hop margin -- the per_unit metric).
    """
    state = E[start_ent].copy()
    per_hop_top1 = []
    per_hop_top2 = []
    final_top1 = 0.0
    final_top2 = 0.0
    for p in rel_chain:
        for _inner in range(K_inner):
            transit = W @ (state * R[p] * sq)
            ent_scores = E @ transit
            top_idx = np.argpartition(ent_scores, -K_set)[-K_set:]
            top_conf = ent_scores[top_idx]
            order = np.argsort(-top_conf)
            top_idx = top_idx[order]
            top_conf = top_conf[order]
            final_top1 = float(top_conf[0])
            final_top2 = float(top_conf[1])
            z = BETA_CLEANUP * top_conf
            w = np.exp(z - z.max())
            w = w / w.sum()
            state = (w[:, None] * E[top_idx]).sum(axis=0)
            state = _normalize(state)
        per_hop_top1.append(final_top1)
        per_hop_top2.append(final_top2)
    ent_scores = E @ state
    pred = int(np.argmax(ent_scores))
    return pred, final_top1, final_top2, per_hop_top1, per_hop_top2


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
        "per_unit": [],
    }
    t0 = time.time()
    triples, keyobjs, n_ent, n_rel = load_kg(seed, M_TRIPLES)
    E, R, W, sq = ingest_hebbian(triples, n_ent, n_rel, g)
    ingest_s = time.time() - t0
    print(
        "  [seed=%d] ingested M=%d in %.1fs (n_ent=%d n_rel=%d n_keys=%d)"
        % (seed, M_TRIPLES, ingest_s, n_ent, n_rel, len(keyobjs)),
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

        # IN-KG arm: traverse + collect FINAL-hop top1/top2 + pred-correct
        t = time.time()
        n_hit = 0
        inkb_top1 = []
        inkb_top2 = []
        inkb_correct = []
        for (s, rels, _ints, o_true) in chains:
            pred, ft1, ft2, _h1, _h2 = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_set=K_SET, K_inner=K_INNER,
            )
            hit = int(pred == o_true)
            n_hit += hit
            inkb_top1.append(ft1)
            inkb_top2.append(ft2)
            inkb_correct.append(hit)
        iter_acc = n_hit / n_actual
        iter_wall = time.time() - t

        # OOD arm: traverse + collect FINAL-hop top1/top2 (no pred-correct -- it's OOD)
        t = time.time()
        ood_top1 = []
        ood_top2 = []
        for (s, rels) in ood_chains:
            _pred, ft1, ft2, _h1, _h2 = traverse_iter_cleanup(
                E, R, W, sq, s, rels, K_set=K_SET, K_inner=K_INNER,
            )
            ood_top1.append(ft1)
            ood_top2.append(ft2)
        ood_wall = time.time() - t

        inkb_top1 = np.array(inkb_top1, dtype=np.float32)
        inkb_top2 = np.array(inkb_top2, dtype=np.float32)
        ood_top1 = np.array(ood_top1, dtype=np.float32)
        ood_top2 = np.array(ood_top2, dtype=np.float32)

        # Margin signal: top1 - top2 (top-2 gap). Calibrate tau_margin on a held CAL split
        # (first half), evaluate on a held TEST split (second half).
        inkb_margin = inkb_top1 - inkb_top2
        ood_margin = ood_top1 - ood_top2

        h_in = len(inkb_margin) // 2
        h_ood = len(ood_margin) // 2
        cal_in = inkb_margin[:h_in]
        cal_ood = ood_margin[:h_ood]
        test_in = inkb_margin[h_in:]
        test_ood = ood_margin[h_ood:]

        if len(cal_in) == 0 or len(cal_ood) == 0:
            best_tau_margin = 0.0
            best_bal = 0.0
        else:
            cands = np.unique(np.concatenate([cal_in, cal_ood]))
            best_tau_margin = float(cands[0])
            best_bal = -1.0
            for tcand in cands:
                acc_in = float((cal_in >= tcand).mean())
                ref_ood = float((cal_ood < tcand).mean())
                bal = 0.5 * (acc_in + ref_ood)
                if bal > best_bal:
                    best_bal = bal
                    best_tau_margin = float(tcand)

        # Evaluate on held TEST split (no circularity)
        ood_refuse_rate_test = (
            float((test_ood < best_tau_margin).mean()) if len(test_ood) else 0.0
        )
        inkb_accept_rate_test = (
            float((test_in >= best_tau_margin).mean()) if len(test_in) else 0.0
        )

        # Discriminating control (c2): margin-ratio = in-KB margin mean / OOD margin mean.
        # If margin doesn't separate (ratio <= 1), the refuse-signal redesign itself failed.
        inkb_margin_mean = float(np.mean(inkb_margin)) if len(inkb_margin) else 0.0
        ood_margin_mean = float(np.mean(ood_margin)) if len(ood_margin) else 0.0
        margin_ratio = inkb_margin_mean / max(abs(ood_margin_mean), 1e-9)

        # Also compute ABSOLUTE-conf based OOD-refuse for direct comparison to r1
        # (r1 used absolute top1 with held-split balanced max). This is the reference
        # the r1b margin-fix is replacing -- keeping it visible for landed-VET.
        h_in2, h_ood2 = h_in, h_ood
        cal_in_abs = inkb_top1[:h_in2]
        cal_ood_abs = ood_top1[:h_ood2]
        test_in_abs = inkb_top1[h_in2:]
        test_ood_abs = ood_top1[h_ood2:]
        if len(cal_in_abs) and len(cal_ood_abs):
            cands_abs = np.unique(np.concatenate([cal_in_abs, cal_ood_abs]))
            best_tau_abs = float(cands_abs[0])
            best_bal_abs = -1.0
            for tcand in cands_abs:
                acc_in = float((cal_in_abs >= tcand).mean())
                ref_ood = float((cal_ood_abs < tcand).mean())
                bal = 0.5 * (acc_in + ref_ood)
                if bal > best_bal_abs:
                    best_bal_abs = bal
                    best_tau_abs = float(tcand)
            ood_refuse_abs_test = float((test_ood_abs < best_tau_abs).mean())
            inkb_accept_abs_test = float((test_in_abs >= best_tau_abs).mean())
        else:
            best_tau_abs = 0.0
            ood_refuse_abs_test = 0.0
            inkb_accept_abs_test = 0.0

        unit = {
            "seed": seed,
            "K_hops": K,
            "n_chains_actual": n_actual,
            "leak_skipped": leak,
            "n_ood_chains": len(ood_chains),
            "iterative_cleanup_acc": round(iter_acc, 4),
            # margin-based refuse (the load-bearing chain-grade gate)
            "tau_margin_per_K": float(best_tau_margin),
            "refuse_ood_rate_margin_test": round(ood_refuse_rate_test, 4),
            "inkb_accept_rate_margin_test": round(inkb_accept_rate_test, 4),
            "best_cal_bal_margin": round(float(best_bal), 4),
            # discriminating control (c2)
            "inkb_margin_mean": round(inkb_margin_mean, 6),
            "ood_margin_mean": round(ood_margin_mean, 6),
            "margin_ratio": round(margin_ratio, 4),
            # absolute-conf refuse for r1 comparison (the gate r1 used)
            "tau_abs_per_K": float(best_tau_abs),
            "refuse_ood_rate_abs_test": round(ood_refuse_abs_test, 4),
            "inkb_accept_rate_abs_test": round(inkb_accept_abs_test, 4),
            # walls
            "iter_wall_s": round(iter_wall, 2),
            "ood_wall_s": round(ood_wall, 2),
        }
        out["per_unit"].append(unit)
        print(
            ("  [seed=%d K=%d n=%d leak=%d] ITER=%.4f | "
             "margin-tau=%.4f OOD-refuse(margin,test)=%.3f in-KB-accept(margin,test)=%.3f | "
             "in-KB margin %.4f vs OOD margin %.4f (ratio %.2fx) | "
             "abs-tau=%.4f OOD-refuse(abs,test)=%.3f")
            % (seed, K, n_actual, leak, iter_acc,
               best_tau_margin, ood_refuse_rate_test, inkb_accept_rate_test,
               inkb_margin_mean, ood_margin_mean, margin_ratio,
               best_tau_abs, ood_refuse_abs_test),
            flush=True,
        )

    out["ingest_s"] = round(ingest_s, 1)
    out["seed_wall_s"] = round(time.time() - t0, 1)
    return out


# ----- verdict (pre-reg HARD bands; chain-grade promotion path) -----

def verdict(ps) -> Tuple[str, str]:
    by_k = defaultdict(lambda: {"iter": [], "ood_refuse_margin": [], "inkb_accept_margin": [],
                                "margin_ratio": [], "ood_refuse_abs": []})
    for p in ps:
        for u in p["per_unit"]:
            K = u["K_hops"]
            by_k[K]["iter"].append(u["iterative_cleanup_acc"])
            by_k[K]["ood_refuse_margin"].append(u["refuse_ood_rate_margin_test"])
            by_k[K]["inkb_accept_margin"].append(u["inkb_accept_rate_margin_test"])
            by_k[K]["margin_ratio"].append(u["margin_ratio"])
            by_k[K]["ood_refuse_abs"].append(u["refuse_ood_rate_abs_test"])

    agg = {}
    for K, d in by_k.items():
        m_iter = float(np.mean(d["iter"])) if d["iter"] else 0.0
        cv_iter = (float(np.std(d["iter"]) / max(np.mean(d["iter"]), 1e-9))
                   if d["iter"] else 0.0)
        m_ood_margin = float(np.mean(d["ood_refuse_margin"])) if d["ood_refuse_margin"] else 0.0
        m_inkb_margin = (float(np.mean(d["inkb_accept_margin"]))
                         if d["inkb_accept_margin"] else 0.0)
        m_ratio = float(np.mean(d["margin_ratio"])) if d["margin_ratio"] else 0.0
        m_ood_abs = float(np.mean(d["ood_refuse_abs"])) if d["ood_refuse_abs"] else 0.0
        agg[K] = {
            "iter": round(m_iter, 4),
            "cv_iter": round(cv_iter, 4),
            "ood_refuse_margin": round(m_ood_margin, 4),
            "inkb_accept_margin": round(m_inkb_margin, 4),
            "margin_ratio": round(m_ratio, 4),
            "ood_refuse_abs": round(m_ood_abs, 4),
            "n_seeds": len(d["iter"]),
        }

    # Mean-reproduction check (c1): r1 means [0.395, 0.240, 0.172] at K=2,3,4 within +/- 0.02.
    # ONLY enforced at FULL config (M=50000, N=8192) -- r1's anchor was measured there; smoke
    # at smaller M/N is easier so the mean-reproduction check does not apply. This mirrors r1's
    # K=2 anchor-check-skipped pattern (cell exp_r1_multihop_iterative_cleanup_v1.py lines 597-608).
    repro_msgs = []
    repro_pass = True
    enforce_repro = (RUN_MODE == "full" and M_TRIPLES >= 25000 and N_DIM >= 4096)
    for K, r1_mean in zip([2, 3, 4], [R1_MEAN_K2, R1_MEAN_K3, R1_MEAN_K4]):
        if K in agg:
            diff = abs(agg[K]["iter"] - r1_mean)
            ok = diff <= MEAN_REPRO_TOL
            if not ok and enforce_repro:
                repro_pass = False
            tag = "OK" if ok else ("OUT-OF-TOL" if enforce_repro else "SKIPPED-SMOKE")
            repro_msgs.append("K%d=%.3f vs r1=%.3f diff=%.3f %s" % (
                K, agg[K]["iter"], r1_mean, diff, tag))

    # Gate 1: K=3 cv <= CV_K3_PASS
    k3_cv = agg.get(3, {}).get("cv_iter", 1.0)
    gate1_pass = k3_cv <= CV_K3_PASS

    # Gate 2: OOD-refuse mean (margin-based) >= OOD_REFUSE_MIN at K=2,3,4
    ood_margin_means = [agg[K]["ood_refuse_margin"] for K in [2, 3, 4] if K in agg]
    gate2_pass = all(x >= OOD_REFUSE_MIN for x in ood_margin_means) if ood_margin_means else False
    ood_margin_min = float(min(ood_margin_means)) if ood_margin_means else 0.0

    # Discriminating control c2: margin-ratio > MARGIN_RATIO_MIN at every K
    margin_ratios = [agg[K]["margin_ratio"] for K in [2, 3, 4] if K in agg]
    margin_ratio_min = float(min(margin_ratios)) if margin_ratios else 0.0
    c2_pass = all(r > MARGIN_RATIO_MIN for r in margin_ratios) if margin_ratios else False

    summ = (
        "by-K: %s | mean-repro: %s | gate1(K3 cv<=%.2f): %s (cv=%.4f) | "
        "gate2(OOD-refuse(margin) mean>=%.2f at K=2,3,4): %s (min=%.3f) | "
        "c2(margin-ratio>%.1fx): %s (min=%.3f)"
    ) % (
        json.dumps({K: agg[K] for K in sorted(agg.keys())}),
        " ; ".join(repro_msgs),
        CV_K3_PASS, "PASS" if gate1_pass else "FAIL", k3_cv,
        OOD_REFUSE_MIN, "PASS" if gate2_pass else "FAIL", ood_margin_min,
        MARGIN_RATIO_MIN, "PASS" if c2_pass else "FAIL", margin_ratio_min,
    )

    # Mean-reproduction is a HARNESS-INTACT precondition: if r1b means don't reproduce r1
    # means within +/- 0.02, the cell is broken / config changed -- HARD_FAIL inconclusive
    if not repro_pass:
        return (
            "HARD_FAIL",
            "HARD_FAIL: r1b means do not reproduce r1 within +/- %.2f at all K -- harness "
            "drift or config change; cannot evaluate chain-grade promotion. " % MEAN_REPRO_TOL
            + summ,
        )

    # If margin-signal doesn't separate (c2 fail), the refuse-signal redesign itself failed
    if not c2_pass:
        return (
            "HARD_FAIL",
            "HARD_FAIL: margin-signal failed discriminating control c2 -- in-KB margin not "
            "separated from OOD margin (ratio min %.3f <= %.1f); refuse-signal redesign needs "
            "further work (not chain-grade). " % (margin_ratio_min, MARGIN_RATIO_MIN) + summ,
        )

    # Chain-grade promotion: both gates lift
    if gate1_pass and gate2_pass:
        return (
            "HARD_PASS",
            "HARD_PASS: r1 chain-grade promotion path GO -- means reproduce r1 within "
            "+/- %.2f at K=2,3,4 AND K3 cv %.4f <= %.2f AND OOD-refuse(margin) mean >= %.2f "
            "at all K (min %.3f). " % (
                MEAN_REPRO_TOL, k3_cv, CV_K3_PASS, OOD_REFUSE_MIN, ood_margin_min,
            )
            + summ,
        )

    # MIDDLE_BAND: one gate lifts, not both -- partial chain-grade path
    if gate1_pass != gate2_pass:
        which = "gate1 (cv) only" if gate1_pass else "gate2 (OOD-refuse margin) only"
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: partial chain-grade path -- %s; means reproduce r1. " % which + summ,
        )

    # HARD_FAIL: means reproduce but BOTH gates still miss -- rigor-fundamentally-limited
    return (
        "HARD_FAIL",
        "HARD_FAIL: means reproduce r1 BUT both pre-reg gates miss (gate1 cv=%.4f, "
        "gate2 OOD-refuse(margin) min=%.3f); mechanism is real but rigor-bound -- route to "
        "brain-drill #4 (alternative mechanism). " % (k3_cv, ood_margin_min)
        + summ,
    )


# ----- metrics.json builder (called incrementally after each seed for partial-recovery) -----

def build_metrics_payload(ps, elapsed_s):
    v, vmsg = verdict(ps)
    # per-K cv across seeds (the load-bearing gate1)
    by_k_seedwise = defaultdict(lambda: {"iter": []})
    for p in ps:
        for u in p["per_unit"]:
            by_k_seedwise[u["K_hops"]]["iter"].append(u["iterative_cleanup_acc"])
    cv_by_k = {
        K: (float(np.std(d["iter"]) / max(np.mean(d["iter"]), 1e-9))
            if d["iter"] else 0.0)
        for K, d in by_k_seedwise.items()
    }
    max_cv = float(max(cv_by_k.values())) if cv_by_k else 0.0

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
        "cv_by_K": {str(K): round(c, 4) for K, c in cv_by_k.items()},
        "max_cv_across_K": round(max_cv, 4),
        "K_hops_list": K_HOPS_LIST,
        "K_set": K_SET,
        "K_inner": K_INNER,
        "N_DIM": N_DIM,
        "M_TRIPLES": M_TRIPLES,
        "n_chains": N_CHAINS,
        "tau_margin_method": TAU_MARGIN_METHOD,
        "zero_llm_calls_at_inference": True,
        "llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "substrate_native": True,
        "substrate_role": "native_inference",
        "r1_reference_means": {"K2": R1_MEAN_K2, "K3": R1_MEAN_K3, "K4": R1_MEAN_K4},
        "DESIGN_NOTE": (
            "r1b r1-chain-grade-promotion path. Inherits r1 mechanism (iterative-cleanup) "
            "verbatim; lifts the two strict-missed pre-reg gates via (a) 7 seeds + 500 chains "
            "for cv reduction; (b) MARGIN-based refuse-signal (top1-top2) calibrated per-K "
            "on held CAL+TEST split. Pre-reg: HARD_PASS iff mean-reproduction within +/- 0.02 "
            "at K=2,3,4 AND K3 cv <= 0.06 AND OOD-refuse(margin) mean >= 0.90 at K=2,3,4. "
            "Discriminating control c2: margin-ratio > 2x (margin must SEPARATE in-KB from "
            "OOD or refuse-signal redesign itself failed)."
        ),
    }


# ----- main -----

if __name__ == "__main__":
    print(
        "[config] anchor=%s mode=%s seeds=%s N=%d M=%d K_hops=%s K_set=%d K_inner=%d "
        "n_chains=%d | %s" % (
            ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, M_TRIPLES, K_HOPS_LIST, K_SET, K_INNER,
            N_CHAINS, CONFIG_VERSION,
        ),
        flush=True,
    )
    print(
        "[smoke-detect] _ARGS.smoke=%s _ARGS.self_test=%s HDLAB_EXP_NAME=%r ends_with_smoke=%s "
        "-> RUN_MODE=%s" % (
            _ARGS.smoke, _ARGS.self_test, _HDLAB_NAME, _IS_SMOKE_BY_NAME, RUN_MODE,
        ),
        flush=True,
    )
    t0 = time.time()
    # Output dir: get_output_dir prefers HDLAB_EXP_NAME (set by runner) and falls back to
    # anchor_name. For local --smoke direct invocation (no HDLAB_EXP_NAME), suffix with
    # _smoke to keep smoke and full partials separated.
    _fallback_name = (ANCHOR_NAME + "_smoke") if (RUN_MODE == "smoke" and not _HDLAB_NAME) else ANCHOR_NAME
    out_dir = get_output_dir(_fallback_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-seed checkpoint: resume from any completed seeds for this run config
    run_config = {"N": N_DIM, "M": M_TRIPLES, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds done; running %s" % (
        len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

    for seed in remaining_seeds:
        rec = run_seed(seed, out_dir)
        write_partial(out_dir, seed, rec)
        # Partial-recovery (template TODO #9): emit metrics.json incrementally after each seed
        # so a timeout still leaves a usable partial metrics.json with verdict computed off
        # what's complete.
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

    # Final aggregate (all seeds; clears incremental flag)
    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    ps_list = [v for k, v in sorted(per_seed.items(), key=lambda kv: int(kv[0]))]

    # SUBSTRATE-ONLY-DECODE GATE assertion
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
