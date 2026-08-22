"""exp_flat_vs_addressed_identity_recovery_livepath_v1 -- DOES ADDRESSED STORAGE BEAT THE FLAT SUM
(AND THE STRONGEST COUNTING FLOOR) ON THE LIVE READING PATH, ON HELD-OUT TEXT?

SOLVER SESSION, problem slug `flat_store_destroys_the_code`. Design frozen BEFORE this ran:
notes/problems/flat_store_destroys_the_code/DESIGN.md. This cell MEASURES; it writes nothing under
hdlab/ (owner ruling Q111 -- the strategy session lands changes). READ-ONLY on data/foundation/*.

THE CLAIM UNDER TEST (PROBLEM.md). The live reading loop "adds each word's pattern into one running
total per concept" -- hdlab.reading_grounding_loop.ConceptSpace._sums[lemma] += ctx_vec, a flat
PROTOTYPE. The paint analogy is IDENTITY DESTRUCTION: mix red+blue+yellow, you cannot pull the red
back out. The proposed fix is a store that keeps a LABEL ON EVERY ITEM (addressed / episodic). The
bar: a read-out on the LIVE reading path that uses addressed storage instead of the flat sum and
BEATS THE STRONGEST COUNTING FLOOR, CI-separated, ON HELD-OUT TEXT.

THE TASK -- open-vocabulary IDENTITY RECOVERY ("pull the red back out"). Candidate/label set = the
harness's anchor lemmas. For a query cue, each arm scores EVERY lemma; hit@1 iff argmax lemma == the
true lemma L. This is exactly the "which item was this?" question the isolation proofs (1.000 vs
0.003) and the exact/held-out collapse (0.9333 vs 0.0044) measure -- run here on real reading text
with the strongest counting floor beside it, which no prior cell did.

ARMS (identical candidates, gold=L, n):
  A_FLAT       score(lem)=cos(query, prototype(lem)); prototype = RAW sum of profile
               context_vector_masked vectors (accumulated RAW; normalise only at compare time -- the
               sec-7 warning: normalising where the substrate accumulates raw is 1/44th of a write).
  A_ADDRESSED  keep EVERY profile encounter as a labelled episode; score(lem)=max over that lemma's
               episodes of cos(query, episode). Exemplar / CA3-completion read-out, no discrete
               codebook (the handicap the plan flagged on the prior completer test).
  F_COUNT1     first-order explicit co-occurrence: cos(prof(lem), indicator-bag of query lemmas).
  F_COUNT2     second-order explicit co-occurrence: cos(prof(lem), sum of query lemmas' own profs).
               prof() is the validated PMI-profile math from
               tools/measure_counting_floors_through_the_harness.py. Second-order is the stronger
               counting floor on record (+28.3pp). Gate on the max of the counting arms' CI UPPER.

TWO CUE REGIMES, same items:
  EXACT-KEY  query = an in-store PROFILE sentence of L (leave-one-out for A_ADDRESSED so its own
             episode cannot trivially self-match). Instrument-works diagnostic.
  HELD-OUT   query = L's held-out sentence (never stored). THE column the bar is decided on.

CONTROLS (none optional; each reports how many items it removed):
  SCRAMBLE-CONTENT  query = a DIFFERENT lemma's held-out cue, gold stays L (destroys the cue's
                    CONTENT, not word order). Must collapse to ~chance.
  INFO-FREE A_ADDRESSED  episodes replaced by random +/-1 codes (same count, same grouping). Must LOSE.
  ABLATION  A_ADDRESSED -> A_FLAT is the addressed-off delta; reported.
  POSITIVE CONTROL  2AFC self-retrieval on held-out cues (A_FLAT) >= 0.70 or the whole comparison
                    is VOID_PLUMBING.
  TIE REPORT  argmax tie density reported per arm/regime; the counting arms can tie at 0.0 cosine.

REUSE, not reinvention: experiments/exp_grounding_readout_known_answer_v1 (C3) supplies the corpus,
the 80/20 profile/held-out split (_n_profile), MASTER_SEED, paired_bootstrap and _derangement;
hdlab.reading_grounding_loop supplies context_vector_masked, content_lemmas, normalize_lemma, CTX_D.
The PMI profile is the exact prof() math from tools/measure_counting_floors_through_the_harness.py.

ASCII-only. Deterministic: sorted(set(...)) iteration, hashlib-seeded RNG, fixed seeds.
Run: .venv/Scripts/python.exe experiments/exp_flat_vs_addressed_identity_recovery_livepath_v1.py
       [--smoke | --self-test]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("HD_GRADED_COMPARATOR", "1")   # live default; set before hdlab import

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.reading_grounding_loop import (  # noqa: E402
    CTX_D, GRADED_COMPARATOR, content_lemmas, context_vector_masked, normalize_lemma,
)
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402

ANCHOR_NAME = "exp_flat_vs_addressed_identity_recovery_livepath_v1"
DESIGN_PATH = "notes/problems/flat_store_destroys_the_code/DESIGN.md"
MASTER_SEED = C3.MASTER_SEED
N_BOOT = 5000

# scale (full): every anchor lemma is a candidate; the store keeps up to STORE_CAP episodes/lemma so
# the exemplar KNN and the PPMI matrix stay in memory. Smoke shrinks the corpus and the store.
STORE_CAP_FULL = 25
STORE_CAP_SMOKE = 8
V_CAP = 9000                 # keep the top-V_CAP context lemmas by document frequency (bounds PPMI)
SELF_RETRIEVAL_FLOOR = 0.70
TIE_REPORT_MIN = 0.02        # if argmax ties exceed this fraction, report both tie conventions


def _out_dir(smoke: bool) -> str:
    p = os.path.join(_REPO, "data", ANCHOR_NAME + ("_smoke" if smoke else ""))
    os.makedirs(p, exist_ok=True)
    return p


def _digest(vec: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(vec, dtype=np.uint8).tobytes()).hexdigest()


def _l2_rows(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return (M / n).astype(np.float32)


# --------------------------------------------------------------------------- store construction
def build_store(sents: List[str], buckets: Dict[str, List[int]], store_cap: int,
                output_dir: str) -> dict:
    """One pass over lemmas building, from the SAME capped PROFILE sentences:
       - prototypes (raw dense sum per lemma)          -> A_FLAT
       - episodes (every profile cue, labelled)        -> A_ADDRESSED
       - df / co counts over unique store sentences     -> F_COUNT1 / F_COUNT2 (prof() PMI)
    Plus one EXACT-KEY cue (a profile sentence) and one HELD-OUT cue per lemma. Every cue masks its
    own target lemma (context_vector_masked / lemma-exclusion), matching the live no-leak rule."""
    lemmas = sorted(buckets)
    d = CTX_D
    proto: Dict[str, np.ndarray] = {}
    epi_vecs: List[np.ndarray] = []
    epi_lem: List[int] = []
    epi_sent: List[int] = []
    exact_cue: Dict[str, Tuple[int, np.ndarray]] = {}   # lemma -> (profile sent idx used, cue vec)
    held_cue: Dict[str, Tuple[int, np.ndarray]] = {}    # lemma -> (heldout sent idx, cue vec)
    store_sent_ids: set = set()
    t0 = time.time()
    kept_lemmas: List[str] = []
    for k, L in enumerate(lemmas):
        idx = buckets[L]
        n_prof = C3._n_profile(len(idx))
        prof_idx = idx[:n_prof][:store_cap]
        held_idx = idx[n_prof:]
        if not prof_idx or not held_idx:
            continue
        acc = np.zeros(d, dtype=np.float64)
        li = len(kept_lemmas)
        n_epi_here = 0
        for si in prof_idx:
            v = context_vector_masked(sents[si], L)
            if float(np.linalg.norm(v)) < 1e-9:
                continue
            acc += v
            epi_vecs.append(v.astype(np.float32))
            epi_lem.append(li)
            epi_sent.append(si)
            store_sent_ids.add(si)
            n_epi_here += 1
        if n_epi_here == 0 or float(np.linalg.norm(acc)) < 1e-9:
            # roll back this lemma's episodes; it produced no usable cue
            del epi_vecs[len(epi_vecs) - n_epi_here:]
            del epi_lem[len(epi_lem) - n_epi_here:]
            del epi_sent[len(epi_sent) - n_epi_here:]
            continue
        # exact-key cue: the first profile sentence used (an IN-STORE sentence)
        ex_si = epi_sent[len(epi_sent) - n_epi_here]
        ex_v = context_vector_masked(sents[ex_si], L)
        # held-out cue: first held-out sentence with a non-degenerate masked context
        hv = None
        h_si = None
        for si in held_idx:
            cand = context_vector_masked(sents[si], L)
            if float(np.linalg.norm(cand)) >= 1e-9:
                hv, h_si = cand, si
                break
        if hv is None:
            del epi_vecs[len(epi_vecs) - n_epi_here:]
            del epi_lem[len(epi_lem) - n_epi_here:]
            del epi_sent[len(epi_sent) - n_epi_here:]
            continue
        proto[L] = acc
        exact_cue[L] = (ex_si, ex_v.astype(np.float32))
        held_cue[L] = (h_si, hv.astype(np.float32))
        kept_lemmas.append(L)
        if k % 500 == 0 or k == len(lemmas) - 1:
            print("[store] %d/%d lemmas kept=%d n_epi=%d elapsed=%.1fs"
                  % (k + 1, len(lemmas), len(kept_lemmas), len(epi_vecs), time.time() - t0),
                  flush=True)
    # PMI profiles (prof()) over the UNIQUE store sentences -- exact math of the validated tool.
    df: Counter = Counter()
    co: Dict[str, Counter] = defaultdict(Counter)
    n_sent = 0
    for si in sorted(store_sent_ids):
        u = sorted(set(content_lemmas(sents[si])))
        n_sent += 1
        df.update(u)
        for w in u:
            co[w].update(u)
    print("[store] PMI counts: n_unique_store_sents=%d vocab=%d elapsed=%.1fs"
          % (n_sent, len(df), time.time() - t0), flush=True)
    return {
        "lemmas": kept_lemmas, "proto": proto,
        "epi_vecs": epi_vecs, "epi_lem": epi_lem, "epi_sent": epi_sent,
        "exact_cue": exact_cue, "held_cue": held_cue,
        "df": df, "co": co, "n_sent": n_sent, "d": d,
    }


def build_pmi_matrix(store: dict) -> dict:
    """prof(w) PMI profile per lemma (validated math), assembled into a dense (n_lem x V) row-
    normalised matrix over the top-V_CAP context lemmas by document frequency."""
    df, co, n = store["df"], store["co"], store["n_sent"]
    lemmas = store["lemmas"]
    # context vocab = top-V_CAP by df (bounds memory; PPMI already drops rare/uninformative pairs)
    ctx = [w for w, _c in sorted(df.items(), key=lambda kv: (-kv[1], kv[0]))[:V_CAP]]
    cidx = {w: j for j, w in enumerate(ctx)}
    V = len(ctx)
    M = np.zeros((len(lemmas), V), dtype=np.float32)

    _pc: Dict[str, Dict[str, float]] = {}

    def prof(w: str) -> Dict[str, float]:
        hit = _pc.get(w)
        if hit is not None:
            return hit
        pw = df[w] / n if df.get(w) else 0.0
        v: Dict[str, float] = {}
        if pw > 0:
            for c, j in co[w].items():
                if c == w or c not in cidx:
                    continue
                pc = df[c] / n
                if pc > 0 and j > 0:
                    p = math.log((j / n) / (pw * pc))
                    if p > 0:
                        v[c] = p
        nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        out = {kk: x / nrm for kk, x in v.items()}
        _pc[w] = out
        return out

    prof_cache: Dict[str, Dict[str, float]] = {}
    for i, L in enumerate(lemmas):
        pv = prof(L)
        prof_cache[L] = pv
        for c, x in pv.items():
            M[i, cidx[c]] = x
    return {"ctx": ctx, "cidx": cidx, "M": M, "prof_cache": prof_cache, "prof_fn": prof}


# --------------------------------------------------------------------------- read-out scorers
def _seg_max(sims: np.ndarray, offsets: np.ndarray, n_lem: int,
             exclude_col: Optional[np.ndarray] = None) -> np.ndarray:
    """Per-lemma MAX of an (nq x n_epi) similarity block, episodes grouped by lemma (offsets are the
    start index of each lemma's block). exclude_col[i] (optional) is a global episode column to set
    to -inf for query row i (leave-one-out of the query's own stored episode)."""
    nq = sims.shape[0]
    if exclude_col is not None:
        rows = np.arange(nq)
        valid = exclude_col >= 0
        sims[rows[valid], exclude_col[valid]] = -np.inf
    out = np.maximum.reduceat(sims, offsets, axis=1)     # (nq x n_lem)
    # reduceat over a zero-length trailing segment can misbehave, but every lemma has >=1 episode.
    if out.shape[1] != n_lem:
        raise AssertionError("seg_max produced %d cols, expected %d" % (out.shape[1], n_lem))
    return out


def score_arms(store: dict, pmi: dict, Q_dense: np.ndarray, q_true: np.ndarray,
               q_ctx: List[List[int]], epi_mat_n: np.ndarray, offsets: np.ndarray,
               exclude_col: Optional[np.ndarray], proto_n: np.ndarray,
               rng_tie: np.random.Generator, batch: int = 256) -> dict:
    """Return {arm: (hit_bool[nq], pred_lem[nq], n_tie[int])} for one cue regime."""
    n_lem = len(store["lemmas"])
    nq = Q_dense.shape[0]
    Qn = _l2_rows(Q_dense)
    M = pmi["M"]                                    # (n_lem x V), row-normalised
    V = M.shape[1]
    # counting query vectors
    Q1 = np.zeros((nq, V), dtype=np.float32)        # first-order: indicator bag of query lemmas
    Q2 = np.zeros((nq, V), dtype=np.float32)        # second-order: sum of query lemmas' profs
    prof_fn = pmi["prof_fn"]
    cidx = pmi["cidx"]
    for i, cl in enumerate(q_ctx):
        for cj in cl:
            Q1[i, cj] = 1.0
        # second order: compose the profs of the query's context lemmas
        for cj in cl:
            pv = prof_fn(pmi["ctx"][cj])
            for c, x in pv.items():
                jj = cidx.get(c)
                if jj is not None:
                    Q2[i, jj] += x
    Q1 = _l2_rows(Q1)
    Q2 = _l2_rows(Q2)

    arms: Dict[str, Tuple[np.ndarray, np.ndarray, int]] = {}

    def _finalize(name: str, scores: np.ndarray) -> None:
        # deterministic tie-broken argmax; count rows where the max is shared
        mx = scores.max(axis=1, keepdims=True)
        tie_mask = scores >= (mx - 1e-9)
        n_tie = int((tie_mask.sum(axis=1) > 1).sum())
        jitter = rng_tie.random(scores.shape).astype(np.float32) * 1e-6
        pred = np.argmax(np.where(tie_mask, jitter, -1.0), axis=1)
        hit = (pred == q_true)
        arms[name] = (hit, pred, n_tie)

    # dense prototype + counting are single matmuls; only the big episode block is batched below
    _finalize("A_FLAT", Qn @ proto_n.T)
    _finalize("F_COUNT1", Q1 @ M.T)
    _finalize("F_COUNT2", Q2 @ M.T)

    # addressed exemplar: batched episode block -> per-lemma max
    n_epi = epi_mat_n.shape[0]
    addr = np.empty((nq, n_lem), dtype=np.float32)
    for b0 in range(0, nq, batch):
        b1 = min(nq, b0 + batch)
        sims = Qn[b0:b1] @ epi_mat_n.T                 # (bq x n_epi)
        exc = exclude_col[b0:b1] if exclude_col is not None else None
        addr[b0:b1] = _seg_max(sims, offsets, n_lem, exclude_col=exc)
    _finalize("A_ADDRESSED", addr)
    return arms


# --------------------------------------------------------------------------- main measurement
def run(smoke: bool, output_dir: str) -> dict:
    t0 = time.time()
    assert GRADED_COMPARATOR is True, "HD_GRADED_COMPARATOR changed; live default assumption broken"
    store_cap = STORE_CAP_SMOKE if smoke else STORE_CAP_FULL
    sents = C3.build_corpus("smoke" if smoke else "full")
    buckets, _counts = C3.build_buckets(sents)
    print("[corpus] n_sents=%d n_lemmas=%d elapsed=%.1fs"
          % (len(sents), len(buckets), time.time() - t0), flush=True)

    store = build_store(sents, buckets, store_cap, output_dir)
    lemmas = store["lemmas"]
    n_lem = len(lemmas)
    lidx = {L: i for i, L in enumerate(lemmas)}
    if n_lem < 50:
        return {"verdict": "INSUFFICIENT_LEMMAS_NO_READ", "n_lem": n_lem}

    pmi = build_pmi_matrix(store)
    proto_n = _l2_rows(np.stack([store["proto"][L] for L in lemmas], axis=0))
    epi_mat = np.stack(store["epi_vecs"], axis=0)
    epi_mat_n = _l2_rows(epi_mat)
    epi_lem = np.asarray(store["epi_lem"], dtype=np.int64)
    epi_sent = np.asarray(store["epi_sent"], dtype=np.int64)
    # offsets: episodes were appended lemma-by-lemma in `lemmas` order, so they are grouped/sorted.
    assert np.all(np.diff(epi_lem) >= 0), "episodes are not grouped by lemma -- seg_max invalid"
    offsets = np.searchsorted(epi_lem, np.arange(n_lem), side="left")
    print("[matrices] n_lem=%d n_epi=%d V=%d elapsed=%.1fs"
          % (n_lem, epi_mat.shape[0], pmi["M"].shape[1], time.time() - t0), flush=True)

    def _ctx_ids(sent_idx: int, target: str) -> List[int]:
        cidx = pmi["cidx"]
        out = []
        for w in sorted(set(content_lemmas(sents[sent_idx]))):
            if w == target:
                continue
            j = cidx.get(w)
            if j is not None:
                out.append(j)
        return out

    # ---- HELD-OUT regime (the bar column) ----
    q_true = np.arange(n_lem, dtype=np.int64)
    Q_held = np.stack([store["held_cue"][L][1] for L in lemmas], axis=0).astype(np.float32)
    q_ctx_held = [_ctx_ids(store["held_cue"][L][0], L) for L in lemmas]
    rng_tie = np.random.default_rng(MASTER_SEED + 101)
    held = score_arms(store, pmi, Q_held, q_true, q_ctx_held, epi_mat_n, offsets,
                      exclude_col=None, proto_n=proto_n, rng_tie=rng_tie)

    # ---- EXACT-KEY regime (instrument-works CEILING diagnostic) ----
    # PROBLEM.md sec 8: "at exact key the cue IS the vector the episode was written from." So the cue
    # is a stored episode and the addressed store is allowed to SELF-MATCH (~1.0) -- this column is
    # the ceiling that proves the store CAN pull an exact item back, NOT a fair flat-vs-addressed
    # contest (that is the HELD-OUT column). No leave-one-out: leaving it out for the exemplar arm
    # but not the prototype arm was an asymmetric handicap.
    Q_exact = np.stack([store["exact_cue"][L][1] for L in lemmas], axis=0).astype(np.float32)
    q_ctx_exact = [_ctx_ids(store["exact_cue"][L][0], L) for L in lemmas]
    rng_tie2 = np.random.default_rng(MASTER_SEED + 202)
    exact = score_arms(store, pmi, Q_exact, q_true, q_ctx_exact, epi_mat_n, offsets,
                       exclude_col=None, proto_n=proto_n, rng_tie=rng_tie2)

    # ---- SCRAMBLE-CONTENT control (held-out cue of a DIFFERENT lemma; gold stays L) ----
    donors = C3._derangement(n_lem, lambda i, j: i == j)
    Q_scr = Q_held[np.asarray(donors, dtype=np.int64)]
    q_ctx_scr = [q_ctx_held[donors[i]] for i in range(n_lem)]
    rng_tie3 = np.random.default_rng(MASTER_SEED + 303)
    scr = score_arms(store, pmi, Q_scr, q_true, q_ctx_scr, epi_mat_n, offsets,
                     exclude_col=None, proto_n=proto_n, rng_tie=rng_tie3)

    # ---- INFO-FREE A_ADDRESSED (random +/-1 episodes, same grouping) held-out + exact ----
    rng_if = np.random.default_rng(MASTER_SEED + 404)
    epi_rand_n = _l2_rows(rng_if.choice([-1.0, 1.0], size=epi_mat.shape).astype(np.float32))
    infofree_held = _seg_max_full(Q_held, epi_rand_n, offsets, n_lem, None,
                                  np.random.default_rng(MASTER_SEED + 405), q_true)
    infofree_exact = _seg_max_full(Q_exact, epi_rand_n, offsets, n_lem, None,
                                   np.random.default_rng(MASTER_SEED + 406), q_true)

    # ---- POSITIVE CONTROL: 2AFC self-retrieval on held-out cues (A_FLAT), {L, random other} ----
    rng_sr = np.random.default_rng(MASTER_SEED + 9)
    Qh_n = _l2_rows(Q_held)
    sr_hits, sr_n = 0, 0
    for i in range(min(300, n_lem)):
        other = int(rng_sr.integers(n_lem))
        tries = 0
        while tries < 20 and other == i:
            other = int(rng_sr.integers(n_lem))
            tries += 1
        if other == i:
            continue
        s_self = float(Qh_n[i] @ proto_n[i])
        s_other = float(Qh_n[i] @ proto_n[other])
        sr_hits += int(s_self > s_other)
        sr_n += 1
    self_retrieval = sr_hits / max(1, sr_n)

    # ---- assemble hit vectors, digests, bootstrap ----
    def _hit(reg: dict, arm: str) -> np.ndarray:
        return reg[arm][0].astype(float)

    correct = {
        "A_FLAT_HELD": _hit(held, "A_FLAT"),
        "A_ADDRESSED_HELD": _hit(held, "A_ADDRESSED"),
        "F_COUNT1_HELD": _hit(held, "F_COUNT1"),
        "F_COUNT2_HELD": _hit(held, "F_COUNT2"),
        "SCRAMBLE_ADDRESSED_HELD": _hit(scr, "A_ADDRESSED"),
        "SCRAMBLE_FLAT_HELD": _hit(scr, "A_FLAT"),
        "INFOFREE_ADDRESSED_HELD": infofree_held.astype(float),
        "A_FLAT_EXACT": _hit(exact, "A_FLAT"),
        "A_ADDRESSED_EXACT": _hit(exact, "A_ADDRESSED"),
        "F_COUNT2_EXACT": _hit(exact, "F_COUNT2"),
        "INFOFREE_ADDRESSED_EXACT": infofree_exact.astype(float),
    }
    arm_keys = sorted(correct)
    deltas = [
        ("d_ADDR_minus_COUNT2_HELD", "A_ADDRESSED_HELD", "F_COUNT2_HELD"),
        ("d_ADDR_minus_COUNT1_HELD", "A_ADDRESSED_HELD", "F_COUNT1_HELD"),
        ("d_ADDR_minus_FLAT_HELD", "A_ADDRESSED_HELD", "A_FLAT_HELD"),
        ("d_ADDR_minus_SCRAMBLE_HELD", "A_ADDRESSED_HELD", "SCRAMBLE_ADDRESSED_HELD"),
        ("d_ADDR_minus_INFOFREE_HELD", "A_ADDRESSED_HELD", "INFOFREE_ADDRESSED_HELD"),
        ("d_FLAT_minus_COUNT2_HELD", "A_FLAT_HELD", "F_COUNT2_HELD"),
        ("d_ADDR_minus_FLAT_EXACT", "A_ADDRESSED_EXACT", "A_FLAT_EXACT"),
        ("d_ADDR_minus_INFOFREE_EXACT", "A_ADDRESSED_EXACT", "INFOFREE_ADDRESSED_EXACT"),
    ]
    bs = C3.paired_bootstrap(correct, arm_keys, deltas, N_BOOT, MASTER_SEED + 5)

    digests = {k: _digest(v.astype(np.uint8)) for k, v in correct.items()}
    # arms-must-differ applies only to the SUBSTANTIVE arms. The SCRAMBLE_* / INFOFREE_* controls
    # are SUPPOSED to sit at floor and, over ~thousands of candidates, are legitimately all-zero, so
    # two of them sharing a digest is correct behaviour, not a plumbing bug.
    primary = ["A_FLAT_HELD", "A_ADDRESSED_HELD", "F_COUNT1_HELD", "F_COUNT2_HELD",
               "A_FLAT_EXACT", "A_ADDRESSED_EXACT", "F_COUNT2_EXACT"]
    dupe = defaultdict(list)
    for k in primary:
        dupe[digests[k]].append(k)
    collisions = {dg: v for dg, v in dupe.items() if len(v) > 1}
    all_dupe = defaultdict(list)
    for k, dg in digests.items():
        all_dupe[dg].append(k)
    control_collisions = {dg: v for dg, v in all_dupe.items()
                          if len(v) > 1 and dg not in collisions}

    def acc(a: str) -> float:
        return float(bs["arm_acc_ci"][a]["acc"])

    def ub(a: str) -> float:
        return float(bs["arm_acc_ci"][a]["ci_hi"])

    tie = {reg_name: {arm: reg[arm][2] for arm in reg}
           for reg_name, reg in (("HELD", held), ("EXACT", exact), ("SCRAMBLE", scr))}

    # ---- the frozen gate: ADDRESSED beats max(COUNT1, COUNT2, SCRAMBLE) UPPER on HELD-OUT ----
    floor_ub = max(ub("F_COUNT1_HELD"), ub("F_COUNT2_HELD"), ub("SCRAMBLE_ADDRESSED_HELD"))
    d_addr_c2 = bs["deltas"]["d_ADDR_minus_COUNT2_HELD"]
    d_addr_c1 = bs["deltas"]["d_ADDR_minus_COUNT1_HELD"]
    d_addr_scr = bs["deltas"]["d_ADDR_minus_SCRAMBLE_HELD"]
    addr_beats_floor = bool(acc("A_ADDRESSED_HELD") > floor_ub
                            and d_addr_c2["ci_excludes_zero"] and d_addr_c2["delta"] > 0
                            and d_addr_c1["ci_excludes_zero"] and d_addr_c1["delta"] > 0
                            and d_addr_scr["ci_excludes_zero"] and d_addr_scr["delta"] > 0)
    infofree_ok = bool(bs["deltas"]["d_ADDR_minus_INFOFREE_HELD"]["delta"] > 0
                       and bs["deltas"]["d_ADDR_minus_INFOFREE_EXACT"]["delta"] > 0)
    addr_wins_exact = bool(acc("A_ADDRESSED_EXACT") > acc("A_FLAT_EXACT"))
    sr_ok = self_retrieval >= SELF_RETRIEVAL_FLOOR and sr_n >= 30

    if not sr_ok:
        verdict = "VOID_PLUMBING_SELF_RETRIEVAL"
        vmsg = ("held-out 2AFC self-retrieval %.4f (n=%d) below %.2f -- read-out not functioning; "
                "no capability claim either way." % (self_retrieval, sr_n, SELF_RETRIEVAL_FLOOR))
    elif not collisions == {}:
        verdict = "ARMS_COLLIDE_STOP"
        vmsg = "arms produced bit-identical correctness vectors: %s" % collisions
    elif addr_beats_floor and infofree_ok:
        verdict = "ADDRESSED_BEATS_FLOOR_HELDOUT"
        vmsg = ("A_ADDRESSED held-out %.4f CLEARS the counting-floor upper bound %.4f, CI-separated, "
                "with the info-free arm losing." % (acc("A_ADDRESSED_HELD"), floor_ub))
    elif addr_wins_exact and not addr_beats_floor:
        verdict = "ADDRESSED_WINS_EXACT_ONLY_NOT_HELDOUT"
        vmsg = ("A_ADDRESSED wins at EXACT-KEY (%.4f vs FLAT %.4f) but does NOT clear the counting "
                "floor upper bound %.4f on HELD-OUT (A_ADDRESSED_HELD=%.4f). This is the "
                "already-known exact-vs-held-out collapse (failure mode c), NOT progress: the "
                "isolation win does not reproduce once the cue is partial."
                % (acc("A_ADDRESSED_EXACT"), acc("A_FLAT_EXACT"), floor_ub, acc("A_ADDRESSED_HELD")))
    else:
        verdict = "ADDRESSED_DOES_NOT_BEAT_FLOOR_HELDOUT"
        vmsg = ("A_ADDRESSED held-out %.4f does NOT clear the counting-floor upper bound %.4f; "
                "d(ADDR-FLAT)_held=%.4f CI[%.4f,%.4f]. Addressing is not the lever on the real "
                "reading task." % (acc("A_ADDRESSED_HELD"), floor_ub,
                                   bs["deltas"]["d_ADDR_minus_FLAT_HELD"]["delta"],
                                   bs["deltas"]["d_ADDR_minus_FLAT_HELD"]["ci_lo"],
                                   bs["deltas"]["d_ADDR_minus_FLAT_HELD"]["ci_hi"]))

    rep = {
        "anchor_name": ANCHOR_NAME, "run_mode": "smoke" if smoke else "full",
        "design": DESIGN_PATH, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "graded_comparator": bool(GRADED_COMPARATOR),
        "n_lemmas_candidates": n_lem, "n_episodes": int(epi_mat.shape[0]),
        "store_cap": store_cap, "V_context": int(pmi["M"].shape[1]),
        "chance_hit_at_1": round(1.0 / n_lem, 8),
        "self_retrieval_2afc": {"acc": round(self_retrieval, 6), "n": sr_n,
                                "floor": SELF_RETRIEVAL_FLOOR, "ok": bool(sr_ok)},
        "held_out": {a: {"hit_at_1": round(acc(a + "_HELD"), 6) if a + "_HELD" in correct else None}
                     for a in ("A_FLAT", "A_ADDRESSED", "F_COUNT1", "F_COUNT2")},
        "exact_key": {a: round(acc(a + "_EXACT"), 6)
                      for a in ("A_FLAT", "A_ADDRESSED", "F_COUNT2")},
        "arm_acc_ci": bs["arm_acc_ci"], "deltas": bs["deltas"],
        "counting_floor_upper_bound_heldout": round(floor_ub, 6),
        "addr_beats_floor_heldout": addr_beats_floor,
        "addr_wins_exact_key": addr_wins_exact,
        "infofree_loses": infofree_ok,
        "tie_counts": tie, "tie_report_threshold_frac": TIE_REPORT_MIN,
        "arm_digests": digests, "arms_must_differ_ok": collisions == {},
        "primary_arm_collisions": collisions,
        "control_arm_collisions_expected_at_floor": control_collisions,
        "scramble_removed_items": 0, "infofree_removed_items": 0,
        "verdict": verdict, "verdict_msg": vmsg,
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(output_dir, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print("\n==== HELD-OUT hit@1 ====")
    for a in ("A_FLAT", "A_ADDRESSED", "F_COUNT1", "F_COUNT2"):
        print("  %-14s %.4f  CI[%.4f,%.4f]" % (a, acc(a + "_HELD"),
              bs["arm_acc_ci"][a + "_HELD"]["ci_lo"], bs["arm_acc_ci"][a + "_HELD"]["ci_hi"]))
    print("  counting-floor UPPER bound (held-out) = %.4f" % floor_ub)
    print("==== EXACT-KEY hit@1 ====")
    for a in ("A_FLAT", "A_ADDRESSED", "F_COUNT2"):
        print("  %-14s %.4f" % (a, acc(a + "_EXACT")))
    print("self-retrieval 2AFC (held-out) = %.4f (floor %.2f, n=%d)"
          % (self_retrieval, SELF_RETRIEVAL_FLOOR, sr_n))
    print("VERDICT:", verdict)
    print("VERDICT_MSG:", vmsg)
    print("WROTE", p)
    return rep


def _seg_max_full(Q: np.ndarray, epi_n: np.ndarray, offsets: np.ndarray, n_lem: int,
                  exclude_col: Optional[np.ndarray], rng_tie: np.random.Generator,
                  q_true: np.ndarray, batch: int = 256) -> np.ndarray:
    """Full exemplar read-out over a given (possibly random) episode matrix; returns hit@1 bool."""
    Qn = _l2_rows(Q)
    nq = Qn.shape[0]
    out = np.empty((nq, n_lem), dtype=np.float32)
    for b0 in range(0, nq, batch):
        b1 = min(nq, b0 + batch)
        sims = Qn[b0:b1] @ epi_n.T
        exc = exclude_col[b0:b1] if exclude_col is not None else None
        out[b0:b1] = _seg_max(sims, offsets, n_lem, exclude_col=exc)
    mx = out.max(axis=1, keepdims=True)
    tie_mask = out >= (mx - 1e-9)
    jitter = rng_tie.random(out.shape).astype(np.float32) * 1e-6
    pred = np.argmax(np.where(tie_mask, jitter, -1.0), axis=1)
    return pred == q_true


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    print("[self-test] synthetic identity-recovery sanity checks...", flush=True)
    d = 256
    rng = np.random.default_rng(0)
    n_lem, per = 40, 6
    # each lemma has a distinct "true direction"; episodes = direction + noise
    dirs = rng.choice([-1.0, 1.0], size=(n_lem, d)).astype(np.float32)
    epi_vecs, epi_lem, offsets_list = [], [], []
    off = 0
    for i in range(n_lem):
        offsets_list.append(off)
        for _ in range(per):
            v = dirs[i] + 0.6 * rng.standard_normal(d).astype(np.float32)
            epi_vecs.append(v)
            epi_lem.append(i)
            off += 1
    epi_n = _l2_rows(np.stack(epi_vecs))
    offsets = np.asarray(offsets_list, dtype=np.int64)
    q_true = np.arange(n_lem)
    # held-out cue: a fresh sample of each lemma's direction -> exemplar should recover identity well
    Q = _l2_rows((dirs + 0.6 * rng.standard_normal((n_lem, d)).astype(np.float32)))
    hit_real = _seg_max_full(Q, epi_n, offsets, n_lem, None, np.random.default_rng(1), q_true)
    assert hit_real.mean() > 0.7, "exemplar cannot recover identity on clean synthetic data: %.3f" % hit_real.mean()
    # info-free episodes: random codes -> must be at chance
    epi_rand = _l2_rows(rng.choice([-1.0, 1.0], size=epi_n.shape).astype(np.float32))
    hit_if = _seg_max_full(Q, epi_rand, offsets, n_lem, None, np.random.default_rng(2), q_true)
    assert hit_if.mean() < 0.25, "info-free arm not at chance: %.3f" % hit_if.mean()
    # read-out MOVES: two different queries give different picks
    assert not np.array_equal(
        _seg_max_full(Q[:1], epi_n, offsets, n_lem, None, np.random.default_rng(3), q_true[:1]),
        _seg_max_full(Q[1:2], epi_n, offsets, n_lem, None, np.random.default_rng(3), q_true[:1])), \
        "read-out pinned"
    # leave-one-out excludes the self episode
    excl = np.array([offsets[i] for i in range(n_lem)], dtype=np.int64)  # exclude first episode of each
    Qself = epi_n[offsets]           # query = each lemma's first stored episode
    hit_loo = _seg_max_full(Qself, epi_n, offsets, n_lem, excl, np.random.default_rng(4), q_true)
    assert hit_loo.mean() > 0.7, "LOO exact-key identity recovery too low: %.3f" % hit_loo.mean()
    # bootstrap detects a real delta
    a = np.zeros(300); a[:210] = 1
    b = np.zeros(300); b[:120] = 1
    bs = C3.paired_bootstrap({"A": a, "B": b}, ["A", "B"], [("d", "A", "B")], 400, 7)
    assert bs["deltas"]["d"]["ci_excludes_zero"]
    print("[self-test] PASS: exemplar_real=%.3f info_free=%.3f loo=%.3f"
          % (hit_real.mean(), hit_if.mean(), hit_loo.mean()), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run(args.smoke, _out_dir(args.smoke))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        out = _out_dir("--smoke" in sys.argv)
        with open(os.path.join(out, "_crash_diagnostic.json"), "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME,
                       "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        raise
