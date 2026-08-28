"""exp_entity_store_sparse_fan_v1 -- WHY does the situation-model entity store fan on running
narrative, and what actually fixes it?

PROBLEM (slug the_entity_store_is_a_dense_bundle_that_fans). The brief's premise: the dense FHRR
bundle in hdlab.situation_model_accumulate BLURS as a character accumulates events (superposition
crosstalk destroys information), and the fix is a SPARSE DG-separated per-event store. THE DISK
CORRECTS THIS PREMISE (diagnosis reproduced below, all on LitBank, oracle=gold clusters):

  * Fan reproduced: decode(entity, sentence)->verb accuracy 0.9455 (1-3 events) -> 0.6574 (17+),
    fan SLOPE 0.288 [0.266,0.310] (28,569 queries).
  * BUT it is NOT superposition blur. It is an ADDRESSING COLLISION at an under-specified key:
      - UNIQUE (entity,sentence) queries decode at 1.0000 at EVERY fan level (even 17+).
      - 22.7% of (entity,sentence) addresses hold >1 DISTINCT verb (a busy character does several
        things per sentence). decode() returns ARGMAX, so co-address siblings are scored wrong.
      - The dense bundle does NOT lose the set: unbind(bundle, s) = v1+v2+..+vm+crosstalk, so a
        TOP-m readout recovers the co-slot verbs at ~1.0000 at every fan level (17+: 0.9997).
      - A FINER per-event temporal index makes the dense store decode at 1.0000 at every fan level.
  * The brief's SUPERPOSITION fan is real but only bites at HIGH unique-event load: DENSE_flat
    collapses 1.0->0.05 as N:20->800; multibank mitigates (->0.78); SPARSE_DG holds 1.0 to N=800.

BRAIN MECHANISM (the fix the disk points to): the hippocampus does NOT index episodes by a coarse
"sentence". Temporal context drifts CONTINUOUSLY (TCM; Howard & Kahana 2002) and each action binds
into a CONJUNCTIVE code with its finer context + content (DG conjunctive coding on LEC-content +
MEC-context convergence; Hargreaves 2005; O'Reilly & Rudy 2001). Retrieval reinstates the context
and reactivates the SET of events bound to it (context-cued recall; Bramao 2022 -- context
reinstatement resolves fan-like AB/AC interference; CA3 completion returns the attractor set,
Nakazawa 2002). So the faithful register keys each event by a FINER CONJUNCTIVE temporal context
and reads out the SET at a partial (entity, sentence) cue -- NOT a denser-vs-sparser single-item
store. DG SPARSE separation is the correct design for the SEPARATE high-load superposition regime
(Willshaw 1969; Treves & Rolls 1991: sparsity reduces the fan SLOPE ~a*ln(1/a), not to zero).

THREE PARTS (all bootstrap over DOCUMENTS; half-width + null p95 reported):
 PART 1 -- the MEASURED (collision) fan, SET-recall at partial cue (entity, sentence):
   DENSE_ARGMAX      : the real organ, decode top-1 (the baseline / the fan).
   DENSE_SETRETURN   : same bundle, top-m readout (m = collision count) -- the set IS in the bundle.
   FINER_CTX         : finer conjunctive temporal index (within-sentence order); set-recall via
                       (E, sentence, *) -- the brain-faithful representation fix (TCM).
   FINER_CTX_SPARSE  : FINER_CTX on a DG-sparse store (the brief's separator, on the finer key).
   POINTER_MULTIMAP  : exact (E,sentence)->set. Ceiling, NOT the proposed fix (no graceful degrade).
   -> fan SLOPE must FLATTEN CI-separated vs DENSE_ARGMAX.
 PART 2 -- SPECIFIC-action recall at cue (entity, sentence, within-sentence ORDER): does the finer
   index carry INFORMATION? FINER_TRUE (true order) vs RANDOM_ORDER_TWIN (shuffled order, info-free)
   -> the twin must LOSE CI-separated on colliding events (null p95 = twin upper).
 PART 3 -- the SUPERPOSITION regime (the brief's mechanism, construction proof on unique-address
   load): DENSE_flat vs DENSE_multibank vs SPARSE_DG, fan slope vs N; residual tracks item-SIMILARITY
   not item-COUNT (Leutgeb 2007; Yassa & Stark 2011).

Run: .venv/Scripts/python.exe experiments/exp_entity_store_sparse_fan_v1.py --diagnose
     ... --part1   ... --part2   ... --part3   ... --self-test
ASCII only. Reads data/litbank/who_did_what_events.json. Writes ONLY to data/entity_store_sparse_fan/.
NO hdlab/ write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_litbank_entity_tracking_end_to_end_v1 import _slots, D as FHRR_D  # noqa: E402
from hdlab.dg_pattern_separation import projection_matrix, dg_separate  # noqa: E402

CACHE = os.path.join(REPO_ROOT, "data", "litbank", "who_did_what_events.json")
OUTDIR = os.path.join(REPO_ROOT, "data", "entity_store_sparse_fan")

D0 = 512
DEXP = 4096
SPARSITY = 0.02
SEED = 20260827
BINS = ["1-3", "4-8", "9-16", "17+"]


def binof(n: int) -> str:
    if n <= 3:
        return "1-3"
    if n <= 8:
        return "4-8"
    if n <= 16:
        return "9-16"
    return "17+"


# --------------------------------------------------------------------------- data
def load_events(docs: Optional[int] = None) -> List[Dict]:
    """Per-doc event stream under ORACLE linking (gold clusters isolate the STORE). Each event gets a
    within-(entity,sentence) ORDER index (the finer temporal context). Record fields:
      events: [(entity:int, sent_slot:int, order:int, verb:str)]
      m_at:   {(entity,sent_slot): count}     verb_vocab, n_slots, ev_count:{E:n}."""
    recs = json.load(open(CACHE, encoding="utf-8"))
    if docs:
        recs = recs[:docs]
    out = []
    for r in recs:
        stream = r["stream"]
        verb_vocab = sorted({m["gov_verb"] for m in stream if m["gov_verb"] is not None})
        if not verb_vocab:
            continue
        slot_map, n_slots = _slots(stream)
        raw = [(int(m["gold"]), slot_map[m["sent"]], m["gov_verb"])
               for m in stream if m["gov_verb"] is not None]
        order_ctr: Dict[Tuple[int, int], int] = defaultdict(int)
        events = []
        for E, s, v in raw:
            o = order_ctr[(E, s)]
            order_ctr[(E, s)] += 1
            events.append((E, s, o, v))
        m_at = {k: c for k, c in order_ctr.items()}
        ev_count = Counter(E for E, _, _, _ in events)
        out.append({"doc": r["doc"], "events": events, "n_slots": n_slots, "m_at": m_at,
                    "verb_vocab": verb_vocab, "ev_count": dict(ev_count)})
    return out


def _seeded_real(tag: str, dim: int) -> np.ndarray:
    seed = int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "big") % (2 ** 32)
    return np.random.default_rng(seed).choice(np.array([-1.0, 1.0], dtype=np.float32), size=dim)


def _torch_gen(seed: int):
    import torch
    g = torch.Generator(); g.manual_seed(seed); return g


# --------------------------------------------------------------------------- DG sparse helpers
def _batch_dg(G, expand_dim, sparsity, W):
    Y = G @ W.T
    k = max(1, round(sparsity * expand_dim))
    if k < expand_dim:
        keep = np.argpartition(np.abs(Y), -k, axis=1)[:, -k:]
        mask = np.zeros_like(Y, dtype=bool)
        np.put_along_axis(mask, keep, True, axis=1)
        Y = np.where(mask, Y, 0.0).astype(np.float32)
    return (Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)).astype(np.float32)


# =========================================================================== PART 1: collision fan
def part1_doc(rec: Dict, arm: str, expand_dim=DEXP, sparsity=SPARSITY) -> List[Tuple[int, int]]:
    """SET-recall at partial cue (entity, sentence): for each event, is its verb in the set the store
    returns for (E, sentence)? Return [(ok, entity_event_count)]."""
    from hdlab.situation_model_accumulate import make_situation_register, cleanup_argmax  # noqa
    ev = rec["events"]; vv = list(rec["verb_vocab"]); evc = rec["ev_count"]; m_at = rec["m_at"]

    if arm == "POINTER_MULTIMAP":
        table: Dict[Tuple[int, int], set] = defaultdict(set)
        for E, s, o, v in ev:
            table[(E, s)].add(v)
        return [(int(v in table[(E, s)]), evc[E]) for E, s, o, v in ev]

    if arm in ("DENSE_ARGMAX", "DENSE_SETRETURN"):
        reg = make_situation_register(vv, FHRR_D, _torch_gen(hash7(rec["doc"])),
                                      max_event_slots=max(rec["n_slots"], 1), backend="multibank", n_banks=8)
        for E, s, o, v in ev:
            reg.add_event(str(E), v, s)
        out = []
        for E, s, o, v in ev:
            try:
                top1, scores = reg.decode(str(E), s)
            except KeyError:
                out.append((0, evc[E])); continue
            if arm == "DENSE_ARGMAX":
                out.append((int(top1 == v), evc[E]))
            else:  # top-m set-return (m = number of events at this (E,s))
                m = m_at[(E, s)]
                topm = {k for k, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:m]}
                out.append((int(v in topm), evc[E]))
        return out

    if arm in ("FINER_CTX", "FINER_CTX_SPARSE"):
        # finer conjunctive index: a distinct event-slot per (sentence, order). SET-recall for (E,s)
        # gathers the fine slots for that sentence (orders 0..m-1) and returns their decoded verbs.
        # map (s, o) -> a unique fine slot id
        fine_ids: Dict[Tuple[int, int], int] = {}
        for E, s, o, v in ev:
            fine_ids.setdefault((s, o), len(fine_ids))
        if arm == "FINER_CTX":
            reg = make_situation_register(vv, FHRR_D, _torch_gen(hash7(rec["doc"])),
                                          max_event_slots=max(len(fine_ids), 1), backend="multibank", n_banks=8)
            for E, s, o, v in ev:
                reg.add_event(str(E), v, fine_ids[(s, o)])
            out = []
            for E, s, o, v in ev:
                m = m_at[(E, s)]
                got = set()
                for oo in range(m):
                    try:
                        pv, _ = reg.decode(str(E), fine_ids[(s, oo)])
                        got.add(pv)
                    except KeyError:
                        pass
                out.append((int(v in got), evc[E]))
            return out
        else:  # FINER_CTX_SPARSE -- DG sparse store keyed on (E, fine-slot)
            return _sparse_setrecall(rec, fine_ids, expand_dim, sparsity)

    raise ValueError(arm)


def _sparse_setrecall(rec, fine_ids, expand_dim, sparsity) -> List[Tuple[int, int]]:
    """DG-sparse heteroassociative store keyed on conjunctive (entity x fine-slot); SET-recall at
    (E, sentence) gathers the fine slots for that sentence and reads out each -> set."""
    ev = rec["events"]; vv = list(rec["verb_vocab"]); evc = rec["ev_count"]; m_at = rec["m_at"]; doc = rec["doc"]
    vidx = {v: j for j, v in enumerate(vv)}
    Wp = projection_matrix(D0, expand_dim, "fanstore::sparse")
    ent_cache, slot_cache = {}, {}

    def addr(E, fs):
        if E not in ent_cache:
            ent_cache[E] = _seeded_real(f"ent::{doc}::{E}", D0)
        if fs not in slot_cache:
            slot_cache[fs] = _seeded_real(f"fslot::{doc}::{fs}", D0)
        return ent_cache[E] * slot_cache[fs]

    G = np.stack([addr(E, fine_ids[(s, o)]) for E, s, o, v in ev])
    A = _batch_dg(G, expand_dim, sparsity, Wp)                     # (n, dexp)
    y = np.array([vidx[v] for _, _, _, v in ev])
    Y = np.zeros((len(ev), len(vv)), dtype=np.float32); Y[np.arange(len(ev)), y] = 1.0
    W = A.T @ Y
    # query set-recall: for (E,s) reconstruct the fine addresses (orders 0..m-1), read out each
    out = []
    for i, (E, s, o, v) in enumerate(ev):
        m = m_at[(E, s)]
        got = set()
        for oo in range(m):
            a = _batch_dg(addr(E, fine_ids[(s, oo)])[None, :], expand_dim, sparsity, Wp)
            got.add(int(np.argmax(a @ W)))
        out.append((int(y[i] in got), evc[E]))
    return out


def hash7(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:4], "big")


# =========================================================================== PART 2: specific recall + twin
def part2_doc(rec: Dict, arm: str) -> List[Tuple[int, int, int]]:
    """SPECIFIC-action recall at cue (entity, sentence, within-sentence ORDER). Return
    [(ok, entity_event_count, m_at_this_address)]. RANDOM_ORDER_TWIN shuffles which order-label each
    event is stored under (info-free) -> querying by the TRUE order retrieves a sibling on collisions."""
    from hdlab.situation_model_accumulate import make_situation_register
    ev = rec["events"]; vv = list(rec["verb_vocab"]); evc = rec["ev_count"]; m_at = rec["m_at"]
    fine_ids: Dict[Tuple[int, int], int] = {}
    for E, s, o, v in ev:
        fine_ids.setdefault((s, o), len(fine_ids))
    # store-order labels
    if arm == "RANDOM_ORDER_TWIN":
        rng = np.random.default_rng(hash7(rec["doc"]) + 13)
        store_order: Dict[Tuple[int, int], List[int]] = {}
        by_addr: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        for idx, (E, s, o, v) in enumerate(ev):
            by_addr[(E, s)].append(o)
        for k, orders in by_addr.items():
            perm = list(orders); rng.shuffle(perm)
            store_order[k] = perm
    reg = make_situation_register(vv, FHRR_D, _torch_gen(hash7(rec["doc"])),
                                  max_event_slots=max(len(fine_ids), 1), backend="multibank", n_banks=8)
    for E, s, o, v in ev:
        so = o if arm == "FINER_TRUE" else store_order[(E, s)][o]
        reg.add_event(str(E), v, fine_ids[(s, so)])
    out = []
    for E, s, o, v in ev:
        try:
            pv, _ = reg.decode(str(E), fine_ids[(s, o)])
        except KeyError:
            pv = None
        out.append((int(pv == v), evc[E], m_at[(E, s)]))
    return out


# =========================================================================== PART 3: superposition regime
def part3_scaling(loads=(20, 50, 100, 200, 400, 800), expand_dim=DEXP, sparsity=SPARSITY, seed=SEED) -> Dict:
    """Construction proof: one entity, N UNIQUELY-addressed events (distinct verbs, vocab=N). Does the
    dense store fan and does SPARSE_DG flatten it? (The brief's superposition mechanism, on real codes.)"""
    from hdlab.situation_model_accumulate import make_situation_register
    out = {}
    Wp = projection_matrix(D0, expand_dim, "fanstore::part3")
    for N in loads:
        Vv = [f"v{i}" for i in range(N)]
        # dense flat + multibank (real organ)
        def dense(backend):
            reg = make_situation_register(Vv, FHRR_D, _torch_gen(7), max_event_slots=N, backend=backend,
                                          n_banks=8)
            for s in range(N):
                reg.add_event("0", Vv[s], s)
            return float(np.mean([int(reg.decode("0", s)[0] == Vv[s]) for s in range(N)]))
        # sparse DG
        G = np.stack([_seeded_real(f"e0", D0) * _seeded_real(f"s{s}", D0) for s in range(N)])
        A = _batch_dg(G, expand_dim, sparsity, Wp)
        Y = np.eye(N, dtype=np.float32)
        W = A.T @ Y
        sp = float(np.mean([int(np.argmax(A[s] @ W) == s) for s in range(N)]))
        out[f"N={N}"] = {"DENSE_flat": dense("flat"), "DENSE_multibank": dense("multibank"),
                         "SPARSE_DG": sp}
    return out


def _sparse_partial_cue_err(N, expand_dim, sparsity, keep, sim_frac_flip, seed):
    """Store N conjunctive addresses (half near-duplicate of a shared base = HIGH similarity, half
    orthogonal = LOW similarity), query each with a PARTIAL/degraded cue (flip (1-keep) of input
    dims), one-shot DG-sparse heteroassociative read. Return (err, is_similar). Under an EXACT cue a
    sparse store is pointer-exact (no errors); the partial cue is where residual interference appears
    and where CA3 completion would matter (Q4)."""
    Wp = projection_matrix(D0, expand_dim, "fanstore::resid")
    rng = np.random.default_rng(seed)
    base = rng.choice([-1.0, 1.0], size=D0).astype(np.float32)
    G = np.empty((N, D0), dtype=np.float32); is_similar = np.zeros(N, dtype=bool)
    for i in range(N):
        if i < N // 2:
            flip = rng.random(D0) < sim_frac_flip
            G[i] = np.where(flip, -base, base); is_similar[i] = True
        else:
            G[i] = rng.choice([-1.0, 1.0], size=D0)
    Q = G.copy()
    for i in range(N):
        fl = rng.random(D0) < (1 - keep)
        Q[i] = np.where(fl, -G[i], G[i])
    A = _batch_dg(G, expand_dim, sparsity, Wp)
    Aq = _batch_dg(Q, expand_dim, sparsity, Wp)
    W = A.T @ np.eye(N, dtype=np.float32)
    err = (np.argmax(Aq @ W, axis=1) != np.arange(N)).astype(np.float32)
    return err, is_similar


def part3_residual(N=800, expand_dim=DEXP, sparsity=SPARSITY, keep=0.7) -> Dict:
    """Residual-tracks-SIMILARITY-not-COUNT (the brain-faithful signature, Leutgeb 2007; Yassa &
    Stark 2011). Operationalized per the Q3 literature: a SIMILARITY arm (fix count N, split store
    into a high-similarity half and a low-similarity half -> error must be HIGHER for the similar
    half) and a COUNT arm (fix similarity distribution = all orthogonal, vary N -> error must be
    comparatively FLAT). Uses a PARTIAL cue because an exact cue makes any store pointer-exact."""
    # SIMILARITY arm: identical count, only similarity differs
    err, sim = _sparse_partial_cue_err(N, expand_dim, sparsity, keep, 0.08, SEED)
    # COUNT arm: all-orthogonal store (similarity held low+fixed), vary N
    count_arm = {}
    for n in (100, 200, 400, 800, 1600):
        Wp = projection_matrix(D0, expand_dim, "fanstore::count")
        rng = np.random.default_rng(SEED + n)
        G = rng.choice([-1.0, 1.0], size=(n, D0)).astype(np.float32)
        Q = G.copy()
        for i in range(n):
            fl = rng.random(D0) < (1 - keep); Q[i] = np.where(fl, -G[i], G[i])
        A = _batch_dg(G, expand_dim, sparsity, Wp); Aq = _batch_dg(Q, expand_dim, sparsity, Wp)
        W = A.T @ np.eye(n, dtype=np.float32)
        count_arm[f"N={n}"] = float((np.argmax(Aq @ W, axis=1) != np.arange(n)).astype(float).mean())
    return {"config": {"N": N, "expand_dim": expand_dim, "sparsity": sparsity, "keep": keep},
            "similarity_arm_fixed_count": {
                "err_high_similarity_half": float(err[sim].mean()),
                "err_low_similarity_half": float(err[~sim].mean()),
                "ratio": float(err[sim].mean() / (err[~sim].mean() + 1e-9))},
            "count_arm_fixed_low_similarity": count_arm,
            "note": ("similarity arm: same N, similar half errs MORE. count arm: similarity fixed low, "
                     "error stays comparatively flat as N grows 100->1600 (aggregate crosstalk grows "
                     "slowly, per Willshaw/Treves-Rolls a*ln(1/a)). Exact-cue would be 0 error (pointer-"
                     "exact); partial cue exposes the residual. kWTA WITHOUT iterative CA3 completion is "
                     "brittle to cue degradation -- completion is the missing robustness stage.")}


# --------------------------------------------------------------------------- bootstrap
def _boot_part1(per_arm: Dict[str, List[List[Tuple[int, int]]]], n_boot=2000, seed=SEED) -> Dict:
    arms = list(per_arm); ndoc = len(next(iter(per_arm.values())))
    rng = np.random.default_rng(seed)
    boot_idx = [rng.integers(0, ndoc, ndoc) for _ in range(n_boot)]

    def stats(per_doc, idx):
        agg = {b: [0, 0] for b in BINS}; tot = [0, 0]
        for i in idx:
            for ok, n in per_doc[i]:
                c = agg[binof(n)]; c[0] += ok; c[1] += 1; tot[0] += ok; tot[1] += 1
        acc = {b: (agg[b][0] / agg[b][1] if agg[b][1] else float("nan")) for b in BINS}
        return acc, (tot[0] / tot[1] if tot[1] else float("nan"))

    base_idx = np.arange(ndoc)
    res = {}
    slopes = {a: [] for a in arms}; overalls = {a: [] for a in arms}; acc17 = {a: [] for a in arms}
    for a in arms:
        acc0, ov0 = stats(per_arm[a], base_idx)
        res[a] = {"acc_by_bin": acc0, "overall": ov0, "fan_slope": acc0["1-3"] - acc0["17+"]}
    for idx in boot_idx:
        for a in arms:
            acc, ov = stats(per_arm[a], idx)
            slopes[a].append(acc["1-3"] - acc["17+"]); overalls[a].append(ov); acc17[a].append(acc["17+"])
    for a in arms:
        s = np.array(slopes[a])
        res[a]["slope_ci"] = [float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))]
        res[a]["slope_hw"] = float((np.percentile(s, 97.5) - np.percentile(s, 2.5)) / 2)
        res[a]["_slopes"] = s; res[a]["_overall"] = np.array(overalls[a]); res[a]["_acc17"] = np.array(acc17[a])
    # paired contrasts vs DENSE_ARGMAX
    contrasts = {}
    if "DENSE_ARGMAX" in res:
        for a in arms:
            if a == "DENSE_ARGMAX":
                continue
            d = res[a]["_slopes"] - res["DENSE_ARGMAX"]["_slopes"]
            lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
            contrasts[f"slope_{a}_minus_DENSE_ARGMAX"] = {
                "mean": float(d.mean()), "ci": [lo, hi], "hw": (hi - lo) / 2,
                "sep": "FLATTER" if hi < 0 else ("STEEPER" if lo > 0 else "NOT_SEP")}
    for a in arms:
        res[a] = {k: v for k, v in res[a].items() if not k.startswith("_")}
    return {"arms": res, "contrasts_slope_vs_DENSE_ARGMAX": contrasts}


def _boot_part2(finer: List[List[Tuple]], twin: List[List[Tuple]], n_boot=2000, seed=SEED) -> Dict:
    """Contrast FINER_TRUE vs RANDOM_ORDER_TWIN on COLLIDING events (m>1) -- where order info matters."""
    ndoc = len(finer); rng = np.random.default_rng(seed)

    def acc_collide(per_doc, idx):
        c = [0, 0]
        for i in idx:
            for ok, n, m in per_doc[i]:
                if m > 1:
                    c[0] += ok; c[1] += 1
        return c[0] / c[1] if c[1] else float("nan")

    base = np.arange(ndoc)
    f0, t0 = acc_collide(finer, base), acc_collide(twin, base)
    diffs, tw = [], []
    for _ in range(n_boot):
        idx = rng.integers(0, ndoc, ndoc)
        fa, ta = acc_collide(finer, idx), acc_collide(twin, idx)
        diffs.append(fa - ta); tw.append(ta)
    diffs = np.array(diffs); tw = np.array(tw)
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    return {"finer_true_collide_acc": f0, "random_order_twin_collide_acc": t0,
            "diff_mean": float(diffs.mean()), "diff_ci": [lo, hi], "diff_hw": (hi - lo) / 2,
            "sep": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP"),
            "null_p95_twin_collide_upper": float(np.percentile(tw, 97.5))}


# --------------------------------------------------------------------------- diagnosis (premise check)
def diagnose(docs=None) -> Dict:
    """Reproduce the fan on the real organ + prove it is collision (unique-address decodes at ceiling;
    top-m recovers the set) not superposition."""
    from hdlab.situation_model_accumulate import make_situation_register
    recs = load_events(docs)
    agg_all = defaultdict(lambda: [0, 0]); agg_uniq = defaultdict(lambda: [0, 0]); agg_topm = defaultdict(lambda: [0, 0])
    coll_pairs = tot_pairs = 0
    for r in recs:
        ev = r["events"]; vv = list(r["verb_vocab"]); evc = r["ev_count"]; m_at = r["m_at"]
        reg = make_situation_register(vv, FHRR_D, _torch_gen(hash7(r["doc"])),
                                      max_event_slots=max(r["n_slots"], 1), backend="multibank", n_banks=8)
        for E, s, o, v in ev:
            reg.add_event(str(E), v, s)
        distinct_verbs = defaultdict(set)
        for E, s, o, v in ev:
            distinct_verbs[(E, s)].add(v)
        for k, vs in distinct_verbs.items():
            tot_pairs += 1
            if len(vs) > 1:
                coll_pairs += 1
        for E, s, o, v in ev:
            b = binof(evc[E]); m = m_at[(E, s)]
            try:
                top1, scores = reg.decode(str(E), s)
            except KeyError:
                agg_all[b][1] += 1; continue
            ok = int(top1 == v)
            agg_all[b][0] += ok; agg_all[b][1] += 1
            if m == 1:
                agg_uniq[b][0] += ok; agg_uniq[b][1] += 1
            topm = {kk for kk, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:m]}
            agg_topm[b][0] += int(v in topm); agg_topm[b][1] += 1
    def fmt(agg):
        return {b: {"acc": (agg[b][0] / agg[b][1] if agg[b][1] else None), "n": agg[b][1]} for b in BINS}
    return {"collision_rate_pairs_with_multi_verb": coll_pairs / tot_pairs, "n_addresses": tot_pairs,
            "all_queries_argmax": fmt(agg_all), "unique_address_only": fmt(agg_uniq),
            "topm_setreturn": fmt(agg_topm)}


# --------------------------------------------------------------------------- self-test
def self_test() -> Dict:
    rng = np.random.default_rng(0)
    G = rng.standard_normal((5, D0)).astype(np.float32)
    Wp = projection_matrix(D0, 2048, "st")
    A = _batch_dg(G, 2048, 0.05, Wp)
    for i in range(5):
        ref = dg_separate(G[i], expand_dim=2048, sparsity=0.05, proj_seed_tag="st", W=Wp)
        assert np.allclose(A[i], ref, atol=1e-5), "batched DG != organ dg_separate"
    # synthetic doc: one entity, 3 verbs at ONE sentence (a collision) + unique events elsewhere
    events = [(0, 0, 0, "a"), (0, 0, 1, "b"), (0, 0, 2, "c"),
              (0, 1, 0, "d"), (0, 2, 0, "e")]
    m_at = {(0, 0): 3, (0, 1): 1, (0, 2): 1}
    rec = {"doc": "syn", "events": events, "n_slots": 3, "m_at": m_at,
           "verb_vocab": ["a", "b", "c", "d", "e"], "ev_count": {0: 5}}
    argmax = np.mean([ok for ok, _ in part1_doc(rec, "DENSE_ARGMAX")])
    setret = np.mean([ok for ok, _ in part1_doc(rec, "DENSE_SETRETURN")])
    finer = np.mean([ok for ok, _ in part1_doc(rec, "FINER_CTX")])
    ptr = np.mean([ok for ok, _ in part1_doc(rec, "POINTER_MULTIMAP")])
    # argmax must MISS co-slot siblings (3 events at one address -> only 1 can be top1)
    assert argmax < 0.7, f"argmax should miss collisions: {argmax}"
    assert setret == 1.0, f"top-m set-return must recover the collision set: {setret}"
    assert finer == 1.0, f"finer conjunctive index must recover the set: {finer}"
    assert ptr == 1.0, f"pointer multimap must be exact: {ptr}"
    # part2: true order recovers specific action; shuffled-order twin loses on the collision
    ft = np.mean([ok for ok, _, m in part2_doc(rec, "FINER_TRUE") if m > 1])
    tw = np.mean([ok for ok, _, m in part2_doc(rec, "RANDOM_ORDER_TWIN") if m > 1])
    assert ft == 1.0, f"finer-true specific recall must be exact: {ft}"
    assert tw < ft, f"info-free order twin must lose on collisions: twin={tw} true={ft}"
    # part3: sparse holds at high load where dense flat fans
    sc = part3_scaling(loads=(50, 400))
    assert sc["N=400"]["SPARSE_DG"] > sc["N=400"]["DENSE_flat"], "sparse must beat dense_flat at N=400"
    return {"batched_dg_ok": True, "part1_syn": {"DENSE_ARGMAX": round(float(argmax), 3),
            "DENSE_SETRETURN": setret, "FINER_CTX": finer, "POINTER": ptr},
            "part2_syn": {"FINER_TRUE": ft, "RANDOM_ORDER_TWIN": round(float(tw), 3)},
            "part3_syn": sc}


# --------------------------------------------------------------------------- CLI
def _dump(name, obj):
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=float)
    print(f"[wrote] {os.path.join(OUTDIR, name)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnose", action="store_true")
    ap.add_argument("--part1", action="store_true")
    ap.add_argument("--part2", action="store_true")
    ap.add_argument("--part3", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--expand-dim", type=int, default=DEXP)
    ap.add_argument("--sparsity", type=float, default=SPARSITY)
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, default=float)); return
    if args.diagnose:
        d = diagnose(args.docs); print(json.dumps(d, indent=2, default=float)); _dump("diagnose.json", d); return
    if args.part1:
        recs = load_events(args.docs)
        arms = ["DENSE_ARGMAX", "DENSE_SETRETURN", "FINER_CTX", "FINER_CTX_SPARSE", "POINTER_MULTIMAP"]
        per_arm = {a: [part1_doc(r, a, args.expand_dim, args.sparsity) for r in recs] for a in arms}
        rep = _boot_part1(per_arm)
        print(json.dumps(rep, indent=2, default=float)); _dump("part1.json", rep); return
    if args.part2:
        recs = load_events(args.docs)
        finer = [part2_doc(r, "FINER_TRUE") for r in recs]
        twin = [part2_doc(r, "RANDOM_ORDER_TWIN") for r in recs]
        rep = _boot_part2(finer, twin)
        print(json.dumps(rep, indent=2, default=float)); _dump("part2.json", rep); return
    if args.part3:
        sc = part3_scaling(expand_dim=args.expand_dim, sparsity=args.sparsity)
        rz = part3_residual(expand_dim=args.expand_dim, sparsity=args.sparsity)
        rep = {"scaling": sc, "residual_similarity_not_count": rz}
        print(json.dumps(rep, indent=2, default=float)); _dump("part3.json", rep); return
    ap.print_help()


if __name__ == "__main__":
    main()
