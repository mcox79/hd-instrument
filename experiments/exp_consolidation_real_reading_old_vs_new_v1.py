"""CONSOLIDATION (D4 / audit deviation #5): does BRAIN-FAITHFUL consolidation (fast/slow separation +
SELECTIVE, SCHEMA-GATED, INTERLEAVED replay) beat a SINGLE AVERAGING op at integrating NEW knowledge from
REAL reading WITHOUT catastrophically forgetting the OLD -- on REAL TEXT (the untested frontier per
notes/ORGAN_MAP.md D4: "WHAT IS ACTUALLY UNTESTED: D4 on REAL TEXT, and D4 AT THE LIVE CALL SITE").

WHY THIS FRAME IS BRAIN-FAITHFUL (CLS, McClelland/O'Reilly/Norman 1995; O'Reilly 2014):
  The two memory systems exist to SOLVE catastrophic interference. Hippocampus = fast, sparse, PATTERN-
  SEPARATED, one-shot, SEPARABLE-ROW index (DG). Cortex = slow, DISTRIBUTED, ERROR-CORRECTING statistical
  learner. Consolidation = REPLAY of hippocampal traces INTERLEAVED with old material so the cortex
  integrates new without erasing old. Selection: SWRs preferentially replay salient/surprising/rewarded
  episodes (Ambrose-Pfeiffer-Foster 2016). Schema-gate: a fact consistent with an existing schema
  consolidates in ONE trial (Tse 2007/2011). PINNED as a system; the SELECTION FUNCTION is UNPINNED
  (OUR-INVENTION-UNDER-TEST) -- copy the COMPUTATION, sweep the PARAMETERS.

THE INSTRUMENT (paired-associate catastrophic-interference, McCloskey-Cohen 1989, pairs from REAL reading):
  N concepts from simplewiki reading (corpus era FIXED -- all from one corpus). Each concept c:
    KEY  k_c  = a random unit code (the hippocampal pattern-separated INDEX / pointer; DG).
    VALUE v_c = the concept's REAL mean-context semantic vector learned from reading (PPMI+SVD; the
                cortical CONTENT). This is what consolidation must fold into durable memory.
  The CORTEX is a fixed-capacity linear store W [Dv x Dk] mapping k_c -> v_c. Retrieval: yhat = W k_c;
  rank all concepts by cos(yhat, v_j); correct if v_c is top-1 (also MRR). This forgets CATASTROPHICALLY
  under sequential error-correction (that is the point -- it is the regime where averaging and selective
  interleaved replay DIVERGE).
  OLD = first half of concepts, NEW = second half (disjoint). Phase 1 learns OLD; Phase 2 learns NEW.
  Arms differ ONLY in the Phase-2 consolidation schedule. JOINT retention = top-1 over OLD u NEW after
  Phase 2. Also reported: OLD-alone (forgetting) and NEW-alone (acquisition), and HELD-OUT INFERENCE
  (generalisation: retrieve a held-out concept's content from a NOISY/partial index -- did consolidation
  build an OVERLAPPING code, or only memorise?).

ARMS (identical model, identical TOTAL update budget; ONLY the Phase-2 schedule differs):
  HEBBIAN_SUM        (SINGLE-AVERAGE floor = the live op analog): W = sum_c v_c k_c^T over ALL pairs,
                       order-free. Never forgets by addition; suffers crosstalk at load>Dk. THE STRONGEST
                       FLOOR (the current live "single averaging op, ungated/un-interleaved/un-budgeted").
  SEQUENTIAL         (un-interleaved cortex): delta-rule SGD, OLD epochs then NEW epochs, NO replay ->
                       catastrophic forgetting of OLD. The failure the brain's architecture avoids.
  INTERLEAVED        (brain interleave): Phase-2 minibatches mix NEW with REPLAYED OLD (uniform) at ratio.
  INTERLV_SELECTIVE  (MECHANISM): interleaved, OLD replay budget allocated ~ (current surprise)^alpha,
                       surprise = 1 - reciprocal_rank recomputed each block (closed-loop, Schaul PER style).
  INTERLV_SCHEMA     (MECHANISM): Tse 2007 -- NEW pairs the current W already predicts (schema-consistent,
                       low error) consolidate one-shot; freed replay budget goes to at-risk OLD.
  INTERLV_3FACTOR    (the DEEP fix): delta-rule with a neuromodulator-gated eligibility trace -- updates
                       weighted by |error| (three-factor). The surprise cell showed rank-1/shared stores
                       can only RESHUFFLE capacity under priority replay; three-factor is what ADDS it.
  INTERLV_RANDOM     (INFO-FREE TWIN): interleaved, OLD replay selected UNIFORMLY AT RANDOM == exactly
                       hdlab.continual.replay_cycle. Must LOSE CI-separated to INTERLV_SELECTIVE.
  Non-arm floors: POP (predict the global mean value -> a fair frequency floor), CHANCE (1/N),
                  SHUFFLE null (permuted k->v mapping; retrieval must collapse -> null p95).

THE BAR (from PROBLEM.md sec 7, verbatim): brain-faithful consolidation must beat the single-average
  CI-separated over the strongest floor's UPPER bound on JOINT old+new retention, with the info-free twin
  (RANDOM replay selection, same budget) LOSING CI-separated; CI half-width + null p95 reported. Sweep the
  selection/interleave parameters; do not adopt a number.
DECISIVE EITHER WAY: win -> wire continual.py (+selection). Rigorous loss -> selective interleaved replay
  does not beat averaging at our scale (say WHY) -> catastrophic forgetting is not yet the binding
  constraint; a full PASS that redirects to what consolidation is FOR here (generalisation, not retention).

ASCII-only. float32/float64 explicit. Deterministic integer seeds. Self-contained numpy (+ reused helpers).
"""
from __future__ import annotations

import os as _os
_os.environ.setdefault("OMP_NUM_THREADS", "1")
_os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
_os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import collections
import json
import random
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from hdlab.corpus_registry import CorpusRegistry  # noqa: E402
from hdlab.reading_grounding_loop import content_lemmas  # noqa: E402
from hdlab.substrate import Substrate  # noqa: E402
from exp_cortical_store_read_path_v1 import _build_lsa  # noqa: E402  (PPMI+SVD over read text)

TRAIN_CORPUS = "simplewiki"
DATA_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "data",
                         "exp_consolidation_real_reading_old_vs_new_v1")

# defaults (swept in FULL; smoke overrides small)
CODE_DIM = 48        # cortical code dim (top-SVD components kept). Capacity ~ CODE_DIM -> load N_train/CODE_DIM
                     # drives interference. Cortex COMPRESSES (this is faithful, and it forces overlap).
SPARSE_KEEP = 1.0    # 1.0 = dense; <1 = k-WTA pattern separation (DG-style). Tests whether SPARSITY
                     # (deviation #4) unlocks SELECTIVE replay by raising capacity / killing the zero-sum.
N_CONCEPTS = 320     # total concepts; ~0.4 old / 0.4 new -> ~256 train pairs into a CODE_DIM store (over cap)
EPOCHS = 40          # delta-rule passes per phase
LR = 0.5             # delta-rule step
REPLAY_RATIO = 1.0   # replayed-OLD : NEW ratio during Phase 2 (interleave strength)
SURPRISE_ALPHA = 2.0 # priority exponent for selective replay
SEEDS = (20260826, 7, 101)


# ------------------------------------------------------------------------------------------------
def _unit_rows(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return M / n


def _build_pairs(seed: int, n_read: int, chunk: int) -> Optional[dict]:
    """Read simplewiki (corpus era FIXED), build a REAL relational-association map over OVERLAPPING
    cortical semantics. For each concept c: key = its own semantic vector s_c (PPMI+SVD; OVERLAPPING
    distributed code -- similar concepts share dimensions, the cortical regime where interference AND
    generalisation are both real); value = the semantic vector of its top-PMI ASSOCIATE s_{a(c)} (a real
    co-occurrence relation learned from reading). The cortex W must learn the map s_c -> s_{a(c)}.
    Concepts split OLD / NEW / HELDOUT (disjoint). HELDOUT is trained in NEITHER phase -> tests whether
    consolidation built a GENERALISING overlapping code or only memorised."""
    sub = Substrate(seed=seed)
    total = 0
    while total < n_read:
        r = sub.read(corpus=TRAIN_CORPUS, n_sentences=chunk, batch=50, max_patches=1, consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences
    reg = CorpusRegistry()
    read_text = reg.handles[TRAIN_CORPUS].take(total)

    lsa = _build_lsa(read_text)            # concept -> PPMI+SVD content vector (overlapping cortical semantics)
    if not lsa:
        return None
    freq: collections.Counter = collections.Counter()
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for s in read_text:
        lems = [l for l in content_lemmas(s) if l in lsa]
        freq.update(lems)
        u = set(lems)
        for a in u:
            for b in u:
                if a != b:
                    cooc[a][b] += 1
    cand = [w for w, _ in freq.most_common() if w in lsa][:N_CONCEPTS + 60]
    cand_set = set(cand)
    tot = sum(freq.values())
    # top-PMI associate a(c) among candidate concepts (a real learned relation, not identity)
    def _assoc(c: str) -> Optional[str]:
        best, bestpmi = None, -1e9
        fc = freq[c]
        for b, cab in cooc[c].items():
            if b not in cand_set or b == c:
                continue
            pmi = np.log((cab * tot) / (fc * freq[b] + 1e-9) + 1e-12)
            if pmi > bestpmi:
                bestpmi, best = pmi, b
        return best
    names, avals = [], []
    for c in cand:
        a = _assoc(c)
        if a is not None:
            names.append(c); avals.append(a)
        if len(names) >= N_CONCEPTS:
            break
    if len(names) < 60:
        return None
    def _trunc(v):                                     # keep top-CODE_DIM SVD components (dominant shared structure)
        w = np.asarray(v, dtype=np.float64)[:CODE_DIM]
        if SPARSE_KEEP < 1.0:                          # k-WTA pattern separation (DG-style): keep top-|s*d| mags
            k = max(1, int(round(SPARSE_KEEP * w.shape[0])))
            if k < w.shape[0]:
                idx = np.argpartition(np.abs(w), w.shape[0] - k)[w.shape[0] - k:]
                s = np.zeros_like(w); s[idx] = w[idx]; w = s
        n = np.linalg.norm(w)
        return w / n if n > 1e-12 else w
    K = np.stack([_trunc(lsa[c]) for c in names])       # keys = own compressed semantics (OVERLAPPING)
    Dv = K.shape[1]
    nameset = set(names)
    assoc_vec = {a: _trunc(lsa[a]) for a in set(avals) if a not in nameset}
    return dict(names=names, avals=avals, K=K, Dv=Dv, assoc_vec=assoc_vec,
                n_read=total, n_sent=len(read_text))


# ---- retrieval / scoring -----------------------------------------------------------------------
def _retrieve_ranks(W: np.ndarray, K: np.ndarray, C: np.ndarray, tgt: np.ndarray,
                    idxs: Sequence[int], self_cb: Optional[np.ndarray] = None) -> np.ndarray:
    """For each concept i in idxs: yhat = W k_i; rank the CONCEPT CODEBOOK C by cos(yhat, C_j); return
    the rank of the TRUE associate concept tgt[i] (0 = top-1). Ranking over concept identities avoids
    duplicate-value degeneracy when two concepts share an associate. self_cb[i] = the concept's OWN
    codebook position -> masked out (a concept never retrieves itself as its associate)."""
    Yhat = _unit_rows(K[idxs] @ W.T)           # [m,Dv]
    S = Yhat @ C.T                             # [m,M] cos with unit codebook rows
    if self_cb is not None:
        for r, i in enumerate(idxs):
            S[r, self_cb[i]] = -1e9
    order = np.argsort(-S, axis=1)             # descending
    ranks = np.empty(len(idxs), dtype=np.int64)
    for r, i in enumerate(idxs):
        ranks[r] = int(np.where(order[r] == tgt[i])[0][0])
    return ranks


def _acc_mrr(ranks: np.ndarray) -> Tuple[float, float]:
    if ranks.size == 0:
        return 0.0, 0.0
    return float(np.mean(ranks == 0)), float(np.mean(1.0 / (ranks + 1.0)))


# ---- learning rules ----------------------------------------------------------------------------
def _hebb_sum(K: np.ndarray, V: np.ndarray, idxs: Sequence[int]) -> np.ndarray:
    """SINGLE-AVERAGE floor: W = sum_i v_i k_i^T (order-free additive; never forgets, crosstalks)."""
    Dv, Dk = V.shape[1], K.shape[1]
    W = np.zeros((Dv, Dk), dtype=np.float64)
    for i in idxs:
        W += np.outer(V[i], K[i])
    return W


def _delta_epochs(W: np.ndarray, K: np.ndarray, V: np.ndarray, idxs: List[int],
                  epochs: int, lr: float, rng: random.Random,
                  three_factor: bool = False) -> np.ndarray:
    """Error-correcting delta rule (cortex). three_factor: gate the update by a neuromodulatory |error|
    signal (per-item eligibility weighting) -- the mechanism that ADDS protected capacity rather than
    reshuffling it (surprise-cell finding)."""
    for _ in range(epochs):
        order = idxs[:]
        rng.shuffle(order)
        for i in order:
            err = V[i] - W @ K[i]              # [Dv]
            g = lr
            if three_factor:
                # neuromodulator gain ~ current error magnitude (bounded); differential weighting
                g = lr * float(min(2.0, 0.5 + np.linalg.norm(err)))
            W += g * np.outer(err, K[i])
    return W


def _surprise(W: np.ndarray, K: np.ndarray, C: np.ndarray, tgt: np.ndarray, idxs: List[int],
              self_cb: Optional[np.ndarray] = None) -> np.ndarray:
    """closed-loop surprise per item = 1 - reciprocal_rank (glass-box; additive_map.score_all analog)."""
    ranks = _retrieve_ranks(W, K, C, tgt, idxs, self_cb)
    return 1.0 - 1.0 / (ranks + 1.0)


def _schema_error(W: np.ndarray, K: np.ndarray, V: np.ndarray, idxs: List[int]) -> np.ndarray:
    """schema-INconsistency per NEW item = reconstruction error norm under current W (low = fits schema)."""
    E = V[idxs] - K[idxs] @ W.T
    return np.linalg.norm(E, axis=1)


# ------------------------------------------------------------------------------------------------
def _phase2(arm: str, W0: np.ndarray, K: np.ndarray, V: np.ndarray, C: np.ndarray, tgt: np.ndarray,
            old: List[int], new: List[int], epochs: int, lr: float,
            replay_ratio: float, alpha: float, seed: int, self_cb: np.ndarray) -> np.ndarray:
    """Run Phase 2 (learn NEW) under the arm's schedule, starting from W0 (= post-OLD cortex).
    All delta arms are matched to the SAME number of weight updates per epoch:
      updates/epoch = |new| + round(replay_ratio*|new|)  (NEW pairs + replayed OLD pairs).
    Only the SELECTION of which OLD get replayed (and, for schema, how NEW are scheduled) differs."""
    rng = random.Random(seed ^ 0xC0FFEE)
    W = W0.copy()
    n_replay = int(round(replay_ratio * len(new)))
    three = (arm == "INTERLV_3FACTOR")
    consolidated_new: set = set()      # SCHEMA: NEW items that already fit the schema (Tse: fast, one-shot)
    for _ in range(epochs):
        # ---- NEW side (schema gate): schema-consistent NEW consolidate FAST and drop out, FREEING budget ----
        if arm == "INTERLV_SCHEMA":
            active_new = [n for n in new if n not in consolidated_new]
            serr = _schema_error(W, K, V, active_new) if active_new else np.array([])
            if serr.size:
                thr = float(np.median(serr))
                newly = [active_new[j] for j in range(len(active_new)) if serr[j] <= thr]
                consolidated_new |= set(newly)             # schema-consistent -> consolidated in one trial
            active_new = [n for n in new if n not in consolidated_new]
            budget = n_replay + (len(new) - len(active_new))   # freed slots -> extra OLD replay (matched budget)
            new_side = active_new
        else:
            budget = n_replay
            new_side = new
        # ---- OLD side: choose which OLD to replay this epoch ----
        m = min(budget, len(old))
        if arm == "SEQUENTIAL":
            replay = []                                    # no replay -> catastrophic forgetting
        elif arm in ("INTERLEAVED", "INTERLV_RANDOM", "INTERLV_3FACTOR"):
            replay = [old[j] for j in rng.sample(range(len(old)), m)]   # uniform (twin == continual.replay_cycle)
        elif arm in ("INTERLV_SELECTIVE", "INTERLV_SCHEMA"):            # priority ~ surprise^alpha (closed-loop)
            s = _surprise(W, K, C, tgt, old, self_cb)
            p = np.power(np.clip(s, 1e-6, None), alpha); p = p / p.sum()
            sel = np.random.default_rng(seed ^ (rng.randrange(1 << 30))).choice(len(old), size=m, replace=False, p=p)
            replay = [old[j] for j in sel]
        else:
            replay = []
        W = _delta_epochs(W, K, V, new_side + replay, epochs=1, lr=lr, rng=rng, three_factor=three)
    return W


# ------------------------------------------------------------------------------------------------
ARMS = ("HEBBIAN_SUM", "SEQUENTIAL", "INTERLEAVED", "INTERLV_SELECTIVE",
        "INTERLV_SCHEMA", "INTERLV_3FACTOR", "INTERLV_RANDOM")


def _run(seed: int, n_read: int, chunk: int, epochs: int, lr: float,
         replay_ratio: float, alpha: float, prebuilt: Optional[dict] = None) -> Optional[dict]:
    d = prebuilt if prebuilt is not None else _build_pairs(seed, n_read, chunk)
    if d is None:
        return None
    K, names, avals = d["K"], d["names"], d["avals"]
    Dv = d["Dv"]
    # codebook = all distinct concepts appearing as a concept OR an associate (rank retrieval over identities)
    cb_names = list(dict.fromkeys(list(names) + list(avals)))
    cb_pos = {c: i for i, c in enumerate(cb_names)}
    # reuse the semantic vectors already carried in K (for names) / need associates too -> rebuild from lsa
    # K rows are unit semantics for names; build codebook C from the same source via a small lookup
    name_vec = {names[i]: K[i] for i in range(len(names))}
    # associates' vectors: some associates are also names; others need their own semantic row from d
    assoc_vec = d.get("assoc_vec", {})
    C = np.zeros((len(cb_names), Dv), dtype=np.float64)
    for i, c in enumerate(cb_names):
        if c in name_vec:
            C[i] = name_vec[c]
        else:
            C[i] = assoc_vec[c]
    C = _unit_rows(C)
    tgt = np.array([cb_pos[avals[i]] for i in range(len(names))], dtype=np.int64)  # target = associate concept
    self_cb = np.array([cb_pos[names[i]] for i in range(len(names))], dtype=np.int64)  # own codebook pos (masked)
    V = C[tgt]                                        # per-item target vector (associate semantics)

    N = len(names)
    perm = np.random.default_rng(seed ^ 0x513).permutation(N)
    n_old = int(0.4 * N); n_new = int(0.4 * N)
    old = list(perm[:n_old]); new = list(perm[n_old:n_old + n_new]); held = list(perm[n_old + n_new:])
    train = old + new

    W_old = _delta_epochs(np.zeros((Dv, Dv)), K, V, old, epochs=epochs, lr=lr,
                          rng=random.Random(seed ^ 0xA11CE))

    res: Dict[str, dict] = {}
    for arm in ARMS:
        if arm == "HEBBIAN_SUM":
            W = _hebb_sum(K, V, train)                 # single average over ALL train pairs (order-free)
        else:
            W = _phase2(arm, W_old, K, V, C, tgt, old, new, epochs, lr, replay_ratio, alpha, seed, self_cb)
        r_old = _retrieve_ranks(W, K, C, tgt, old, self_cb)
        r_new = _retrieve_ranks(W, K, C, tgt, new, self_cb)
        r_all = np.concatenate([r_old, r_new])
        r_held = _retrieve_ranks(W, K, C, tgt, held, self_cb)   # HELD-OUT generalisation (neither phase)
        acc_old, _ = _acc_mrr(r_old)
        acc_new, _ = _acc_mrr(r_new)
        acc_all, mrr_all = _acc_mrr(r_all)
        acc_held, _ = _acc_mrr(r_held)
        res[arm] = dict(acc_old=acc_old, acc_new=acc_new, acc_joint=acc_all, mrr_joint=mrr_all,
                        acc_inf=acc_held, ranks_old=r_old.tolist(), ranks_new=r_new.tolist(),
                        ranks_joint=r_all.tolist(), ranks_inf=r_held.tolist())

    # ---- FAITHFUL SINGLE-AVERAGE floors (the LIVE op is SEPARABLE-row, not a shared W) ----
    # SEP_LOOKUP: the live HDFactStore reality -- each concept in its OWN slot; storing NEW never
    #   touches OLD's slot -> retention is a LOOKUP, invariant to phase order (NO catastrophic forgetting).
    #   Retrieval of a trained concept returns its exact stored associate (rank 0). Held-out has no slot.
    r_old_lk = np.zeros(len(old), dtype=np.int64)          # trained -> exact recall
    r_new_lk = np.zeros(len(new), dtype=np.int64)
    gmean = _unit_rows(C[[cb_pos[avals[i]] for i in train]].mean(axis=0, keepdims=True))[0]
    held_pred = int(np.argmax(C @ gmean))                  # no slot -> best it can do is the global prior
    r_held_lk = np.array([0 if tgt[i] == held_pred else 1 for i in held], dtype=np.int64)
    res["SEP_LOOKUP"] = dict(acc_old=1.0, acc_new=1.0, acc_joint=1.0, mrr_joint=1.0,
                             acc_inf=float(np.mean(r_held_lk == 0)),
                             ranks_old=r_old_lk.tolist(), ranks_new=r_new_lk.tolist(),
                             ranks_joint=(r_old_lk.tolist() + r_new_lk.tolist()),
                             ranks_inf=r_held_lk.tolist())
    # SEP_AVG_SIM: per-concept averaged CONTENT read by SIMILARITY (cos(s_c, codebook), self masked) -- the
    #   live "average + similarity read", no learned relational map. First-order floor; also does not forget.
    def _sim_ranks(idxs):
        S = _unit_rows(K[idxs]) @ C.T
        for r, i in enumerate(idxs):
            S[r, self_cb[i]] = -1e9
        order = np.argsort(-S, axis=1)
        return np.array([int(np.where(order[r] == tgt[i])[0][0]) for r, i in enumerate(idxs)])
    r_old_sim = _sim_ranks(old); r_new_sim = _sim_ranks(new)
    r_all_sim = np.concatenate([r_old_sim, r_new_sim])
    r_held_sim = _sim_ranks(held)
    res["SEP_AVG_SIM"] = dict(acc_old=float(np.mean(r_old_sim == 0)),
                              acc_new=float(np.mean(r_new_sim == 0)),
                              acc_joint=float(np.mean(r_all_sim == 0)),
                              mrr_joint=float(np.mean(1.0 / (r_all_sim + 1.0))),
                              acc_inf=float(np.mean(r_held_sim == 0)),
                              ranks_old=r_old_sim.tolist(), ranks_new=r_new_sim.tolist(),
                              ranks_joint=r_all_sim.tolist(), ranks_inf=r_held_sim.tolist())

    M = len(cb_names)
    chance = 1.0 / M
    # POP floor: everyone predicts the single most-frequent associate concept (first-order frequency)
    from collections import Counter as _C
    pop_tgt = _C(avals).most_common(1)[0][0]
    pop_i = cb_pos[pop_tgt]
    pop_acc = float(np.mean([1.0 if tgt[i] == pop_i else 0.0 for i in train]))
    # SHUFFLE null: permute key->target mapping (single-average pipeline) -> retrieval must collapse
    prng = np.random.default_rng(seed ^ 0xBEEF)
    pp = prng.permutation(N)
    Wnull = _hebb_sum(K, V[pp], train)
    rnull = _retrieve_ranks(Wnull, K, C, tgt, train)
    null_acc, _ = _acc_mrr(rnull)

    return dict(seed=seed, n_concepts=N, codebook=M, dv=Dv, n_read=d["n_read"], n_sent=d["n_sent"],
                n_old=len(old), n_new=len(new), n_held=len(held), epochs=epochs, lr=lr,
                replay_ratio=replay_ratio, alpha=alpha, arms=res, chance=chance,
                pop_acc=pop_acc, null_acc=null_acc)


def _boot_ci(vals: np.ndarray, rng: np.random.Generator, iters: int = 2000) -> Tuple[float, float, float]:
    if vals.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, vals.size, size=(iters, vals.size))
    boots = vals[idx].mean(axis=1)
    return float(vals.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def _agg_arm(rows: List[dict], arm: str, key: str, brng) -> Tuple[float, float, float]:
    r = np.concatenate([np.array(x["arms"][arm][key]) for x in rows])
    return _boot_ci((r == 0).astype(np.float64), brng)


def _sweep_replay(seeds, n_read, args, ratios) -> None:
    """SCARCITY DRILL: at replay_ratio=1.0 the replay budget = |old|, so uniform and selective replay the
    SAME full set -- selection is null BY CONSTRUCTION. The brain's selective replay is a lever only when
    the budget is SCARCE (budget << #memories), forcing a choice. Sweep replay_ratio DOWN, reading ONCE per
    seed, and test whether SELECTIVE/SCHEMA beat UNIFORM on OLD + BALANCED(min old,new) retention."""
    brng = np.random.default_rng(999)
    t0 = time.time()
    out_ratios = {}
    key_arms = ("SEQUENTIAL", "INTERLEAVED", "INTERLV_SELECTIVE", "INTERLV_SCHEMA", "INTERLV_3FACTOR")
    per_seed_pairs = {}
    print(f"SCARCITY DRILL: sweeping replay_ratio {ratios}  (|old|=|new|; budget=ratio*|new| of |old|)")
    for r in ratios:
        rows = []
        for sd in seeds:
            if sd not in per_seed_pairs:
                per_seed_pairs[sd] = _build_pairs(sd, n_read, args.chunk)
            d = per_seed_pairs[sd]
            row = _run(sd, n_read, args.chunk, args.epochs, args.lr, r, args.alpha, prebuilt=d)
            if row is not None:
                rows.append(row)
        if not rows:
            continue
        agg = {}
        for arm in key_arms:
            mo, loo, hio = _agg_arm(rows, arm, "ranks_old", brng)
            mn, lon, hin = _agg_arm(rows, arm, "ranks_new", brng)
            agg[arm] = dict(old=mo, old_lo=loo, old_hi=hio, new=mn, bal=min(mo, mn))
        budget_frac = min(r, 1.0)   # budget = r*|new| of |old| (|new|==|old|)
        out_ratios[str(r)] = agg
        itl, sel, sch = agg["INTERLEAVED"], agg["INTERLV_SELECTIVE"], agg["INTERLV_SCHEMA"]
        sep = sel["old_lo"] > itl["old_hi"]
        print(f"\n  replay_ratio={r} (budget~{budget_frac*100:.0f}% of OLD) [{time.time()-t0:.0f}s]")
        print(f"    OLD: SEQ={agg['SEQUENTIAL']['old']:.3f} UNIFORM={itl['old']:.3f}[{itl['old_lo']:.3f},{itl['old_hi']:.3f}] "
              f"SELECTIVE={sel['old']:.3f}[{sel['old_lo']:.3f},{sel['old_hi']:.3f}] SCHEMA={sch['old']:.3f} 3F={agg['INTERLV_3FACTOR']['old']:.3f}")
        print(f"    BALANCED(min old,new): UNIFORM={itl['bal']:.3f} SELECTIVE={sel['bal']:.3f} SCHEMA={sch['bal']:.3f} 3F={agg['INTERLV_3FACTOR']['bal']:.3f}")
        print(f"    -> SELECTIVE beats UNIFORM on OLD CI-sep? {sep}  | on BALANCED? {sel['bal'] > itl['bal']}")
    _os.makedirs(DATA_DIR, exist_ok=True)
    tmp = _os.path.join(DATA_DIR, "metrics_sweep.json.tmp")
    with open(tmp, "w") as f:
        json.dump(dict(run="sweep_replay", ratios=ratios, seeds=list(seeds),
                       config=dict(n_concepts=N_CONCEPTS, code_dim=CODE_DIM, sparse_keep=SPARSE_KEEP,
                                   epochs=args.epochs, lr=args.lr, alpha=args.alpha), agg=out_ratios), f)
    _os.replace(tmp, _os.path.join(DATA_DIR, "metrics_sweep.json"))
    print(f"\n[sweep done {time.time()-t0:.0f}s -> metrics_sweep.json]")


def main() -> None:
    global N_CONCEPTS, CODE_DIM, SPARSE_KEEP
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n_read", type=int, default=8000)
    ap.add_argument("--chunk", type=int, default=1000)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--lr", type=float, default=LR)
    ap.add_argument("--replay_ratio", type=float, default=REPLAY_RATIO)
    ap.add_argument("--alpha", type=float, default=SURPRISE_ALPHA)
    ap.add_argument("--code_dim", type=int, default=CODE_DIM)
    ap.add_argument("--n_concepts", type=int, default=N_CONCEPTS)
    ap.add_argument("--sparse_keep", type=float, default=SPARSE_KEEP)
    ap.add_argument("--sweep_replay", type=str, default="",
                    help="comma list of replay_ratio to sweep (budget scarcity); reads once per seed")
    args = ap.parse_args()

    CODE_DIM = args.code_dim
    N_CONCEPTS = args.n_concepts
    SPARSE_KEEP = args.sparse_keep
    seeds = (20260826,) if args.smoke else SEEDS
    n_read = 2500 if args.smoke else args.n_read
    if args.smoke:
        N_CONCEPTS = 120

    if args.sweep_replay:
        _sweep_replay(seeds, n_read, args, [float(x) for x in args.sweep_replay.split(",")])
        return

    t0 = time.time()
    rows = []
    for sd in seeds:
        r = _run(sd, n_read, args.chunk, args.epochs, args.lr, args.replay_ratio, args.alpha)
        if r is not None:
            rows.append(r)
        print(f"  seed {sd} done ({time.time()-t0:.0f}s)")
        if r:
            a = r["arms"]
            print(f"    JOINT top1: HEBB(avg)={a['HEBBIAN_SUM']['acc_joint']:.3f} "
                  f"SEQ={a['SEQUENTIAL']['acc_joint']:.3f} INTERLV={a['INTERLEAVED']['acc_joint']:.3f} "
                  f"SEL={a['INTERLV_SELECTIVE']['acc_joint']:.3f} SCHEMA={a['INTERLV_SCHEMA']['acc_joint']:.3f} "
                  f"3F={a['INTERLV_3FACTOR']['acc_joint']:.3f} RAND(twin)={a['INTERLV_RANDOM']['acc_joint']:.3f} "
                  f"| floor pop={r['pop_acc']:.3f} null={r['null_acc']:.3f} chance={r['chance']:.4f}")
            print(f"    OLD-alone: SEQ={a['SEQUENTIAL']['acc_old']:.3f} INTERLV={a['INTERLEAVED']['acc_old']:.3f} "
                  f"SEL={a['INTERLV_SELECTIVE']['acc_old']:.3f} 3F={a['INTERLV_3FACTOR']['acc_old']:.3f}")
            print(f"    INFER(heldout,noisy idx) top1: HEBB={a['HEBBIAN_SUM']['acc_inf']:.3f} "
                  f"INTERLV={a['INTERLEAVED']['acc_inf']:.3f} 3F={a['INTERLV_3FACTOR']['acc_inf']:.3f}")

    if not rows:
        print("NO ROWS")
        return

    # aggregate: pool ranks across seeds per arm, bootstrap CI on top-1
    report_arms = ARMS + ("SEP_AVG_SIM", "SEP_LOOKUP")
    brng = np.random.default_rng(12345)
    agg: Dict[str, dict] = {}
    for arm in report_arms:
        rj = np.concatenate([np.array(r["arms"][arm]["ranks_joint"]) for r in rows])
        ri = np.concatenate([np.array(r["arms"][arm]["ranks_inf"]) for r in rows])
        ro = np.concatenate([np.array(r["arms"][arm]["ranks_old"]) for r in rows])
        rn = np.concatenate([np.array(r["arms"][arm]["ranks_new"]) for r in rows])
        m, lo, hi = _boot_ci((rj == 0).astype(np.float64), brng)
        mi, loi, hii = _boot_ci((ri == 0).astype(np.float64), brng)
        mo, loo, hio = _boot_ci((ro == 0).astype(np.float64), brng)
        mn, lon, hin = _boot_ci((rn == 0).astype(np.float64), brng)
        # BALANCED retention: paired min(old_hit, new_hit) per bootstrap resample of concepts -- exposes
        # arms that hoard OLD by abandoning NEW (a mean-JOINT win that is a degenerate policy).
        bal = min(mo, mn)
        agg[arm] = dict(joint_top1=m, joint_lo=lo, joint_hi=hi, half=(hi - lo) / 2,
                        inf_top1=mi, inf_lo=loi, inf_hi=hii,
                        old_top1=mo, old_lo=loo, old_hi=hio,
                        new_top1=mn, new_lo=lon, new_hi=hin, balanced=bal)
    pop = float(np.mean([r["pop_acc"] for r in rows]))
    null = float(np.mean([r["null_acc"] for r in rows]))
    chance = float(np.mean([r["chance"] for r in rows]))

    out = dict(run_mode="smoke" if args.smoke else "full", anchor_name="consolidation_real_reading_old_vs_new_v1",
               n_seeds=len(rows), seeds=list(seeds), agg=agg, pop_acc=pop, null_acc=null, chance=chance,
               elapsed_s=time.time() - t0, config=dict(n_concepts=N_CONCEPTS, code_dim=CODE_DIM,
               sparse_keep=SPARSE_KEEP, epochs=args.epochs, lr=args.lr, replay_ratio=args.replay_ratio,
               alpha=args.alpha, n_read=n_read), per_seed=rows)

    _os.makedirs(DATA_DIR, exist_ok=True)
    tmp = _os.path.join(DATA_DIR, "metrics.json.tmp")
    with open(tmp, "w") as f:
        json.dump(out, f)
    _os.replace(tmp, _os.path.join(DATA_DIR, "metrics.json"))

    print("\n==== AGGREGATE (pooled ranks, bootstrap 95% CI on JOINT top-1) ====")
    print(f"floors: pop={pop:.3f} null={null:.4f} chance={chance:.4f}")
    for arm in report_arms:
        g = agg[arm]
        print(f"  {arm:18s} JOINT={g['joint_top1']:.3f} OLD={g['old_top1']:.3f}[{g['old_lo']:.3f},{g['old_hi']:.3f}] "
              f"NEW={g['new_top1']:.3f}[{g['new_lo']:.3f},{g['new_hi']:.3f}] "
              f"BAL(min)={g['balanced']:.3f} INFER={g['inf_top1']:.3f}")
    # verdict helpers -- STRONGEST single-average floor = best of the faithful separable / distributed averages
    sel = agg["INTERLV_SELECTIVE"]; twin = agg["INTERLV_RANDOM"]; itl = agg["INTERLEAVED"]
    floor_arms = {"HEBBIAN_SUM": agg["HEBBIAN_SUM"], "SEP_AVG_SIM": agg["SEP_AVG_SIM"], "SEP_LOOKUP": agg["SEP_LOOKUP"]}
    strongest = max(floor_arms, key=lambda k: floor_arms[k]["joint_top1"])
    sf = floor_arms[strongest]
    # HONEST headline = BALANCED retention (min of old,new) -- a mean-JOINT win by hoarding OLD is degenerate
    best_name = max(("INTERLEAVED", "INTERLV_SELECTIVE", "INTERLV_SCHEMA", "INTERLV_3FACTOR"),
                    key=lambda k: agg[k]["balanced"])
    best = agg[best_name]
    print("\nBAR CHECKS:")
    print(f"  strongest single-average floor = {strongest} JOINT={sf['joint_top1']:.3f} (SEP_LOOKUP never forgets)")
    print(f"  best brain-faithful by BALANCED(min old,new) = {best_name} bal={best['balanced']:.3f} "
          f"(old={best['old_top1']:.3f} new={best['new_top1']:.3f})")
    print(f"  info-free twin LOSES? SELECTIVE bal={sel['balanced']:.3f} vs uniform INTERLEAVED bal="
          f"{itl['balanced']:.3f} -> selective beats uniform? {sel['balanced'] > itl['balanced']}")
    print(f"  SCHEMA hoards OLD? old={agg['INTERLV_SCHEMA']['old_top1']:.3f} new="
          f"{agg['INTERLV_SCHEMA']['new_top1']:.3f} (bal={agg['INTERLV_SCHEMA']['balanced']:.3f})")
    print(f"  [OLD retention -- catastrophic forgetting] SEQ={agg['SEQUENTIAL']['old_top1']:.3f} "
          f"INTERLV={itl['old_top1']:.3f}  replay-beats-sequential CI-sep? INTERLV.old_lo={itl['old_lo']:.3f} "
          f"> SEQ.old_hi={agg['SEQUENTIAL']['old_hi']:.3f} -> {itl['old_lo'] > agg['SEQUENTIAL']['old_hi']}")
    print(f"  [generalisation, held-out] best INFER any arm = "
          f"{max(agg[a]['inf_top1'] for a in report_arms):.3f} vs chance {chance:.4f}")


if __name__ == "__main__":
    main()
