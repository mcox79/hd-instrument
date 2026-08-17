"""exp_readout_second_order_v1 -- IS OUR NEIGHBOURHOOD SYNTAGMATIC WHERE THE TASK IS PARADIGMATIC?

FINDINGS LOG: notes/readout_ceiling_findings_2026-08-17.md
SIBLING (the diagnosis this builds on): experiments/exp_readout_ceiling_diagnosis_v1.py

WHY THIS CELL EXISTS -- it is answering a question the diagnosis RAISED, not a hunch.
The reduced-grid smoke of the sibling measured four candidate causes of the read-out ceiling and
killed all four:
  hubness      Nk-Gini REAL 0.7130 vs SCRAMBLE NULL 0.6973 -- no excess concentration to correct
  degeneracy   364 distinct top-1 answers for 400 queries -- the read-out is not stuck
  genericity   corr(times an anchor wins, constant-prototype score) = 0.045
  frequency    corr(times an anchor wins, log corpus count)         = 0.042
and it showed the store DOES contain the answer: the exact-key rank curve is CI-separated ABOVE the
per-item random-ranking null at all 11 values of k (3.02x at k=1, median rank of the best gold 52
of 5,491 against a random expectation of 224), while only overtaking a QUERY-IGNORING constant
ranking at about k=50.

So the read-out returns a SPECIFIC, QUERY-CONDITIONAL, PLAUSIBLE word that is not a synonym, and
the query signal is real but sits BELOW the top of the ranking. That is the signature of a
SYNTAGMATIC neighbourhood (words that OCCUR WITH the query) being asked a PARADIGMATIC question
(words that SUBSTITUTE FOR the query). Our store is `self._sums[lemma] += ctx_vec` -- a FIRST-ORDER
co-occurrence sum -- so first-order cosine returns co-occurrence partners by construction.

THE ARMS, and the last two have never been run in this repo.

C1  WINNER FORENSICS         what ARE the top-1 picks? WordNet relation of winner-to-query,
                             classified: in the generous gold / taxonomically related but outside
                             it / no WordNet relation at all. Plus the same census for the best
                             gold, as the matched comparison.
C2  SYNTAGMATIC TEST         THE DISCRIMINATOR. Do the winners CO-OCCUR with the query word in the
                             corpus more than the gold synonyms do? Pre-registered prediction:
                             YES, and by a wide margin. The corpus is re-read for COUNTS ONLY; the
                             STORE IS NEVER REBUILT, so the identical-instrument invariant holds.
C3  SECOND-ORDER READ-OUT    "two words are similar if they have similar NEIGHBOURS" -- score by
                             the similarity of two anchors' similarity PROFILES rather than by
                             their direct cosine. Profile truncation k is a PARAMETER and is SWEPT.
C4  SUCCESSOR REPRESENTATION M = (I - gamma*A)^-1 on our own anchor graph, gamma SWEPT.
                             ORGAN_MAP D7 lists the successor representation as MISSING and gives
                             this equation; the 2026-08-16 theory drill says of it: "it is cheap,
                             it is glass-box (a matrix inverse of a graph we own), it uses no
                             external asset, and IT HAS NEVER BEEN RUN." It is run here.

BRAIN FIDELITY, and the honest split.
  PINNED-BY-EVIDENCE as a representational signature: the successor representation. Place-field
    skewing in directed environments; hippocampal pattern similarity mirroring the COMMUNITY
    STRUCTURE of a graph; successor-like representations in human hippocampus AND V1 (Ekman et al.
    eLife 2023). Stachenfeld, Botvinick & Gershman 2017 Nat Neurosci.
  CONTESTED: its LEARNING RULE. TD learning is not known to be implemented in hippocampal networks;
    George et al. 2023 approximate M with STDP + theta phase precession instead. And M is
    POLICY-DEPENDENT -- a map of what you DO, not of what IS. Reported, not adjudicated.
  OURS, INVENTION UNDER TEST: using M's rows as a RETRIEVAL SCORE for a synonym task. Nothing in
    the biology says that. The second-order profile comparator is likewise OURS (Ruge 1992 and the
    distributional-semantics tradition), run as the standard engineering method for exactly this
    syntagmatic/paradigmatic problem and labelled as such.
  THE ADJACENT PIN THAT CUTS AGAINST US, stated so it is not lost: every implemented cortical model
    in the CLS lineage extracts latent structure with an ERROR-DRIVEN objective, not a Hebbian sum,
    and the ATL hub's operation is pattern completion via a compact abstract label feeding BACK
    onto shallower features (Jackson, Rogers & Lambon Ralph 2021) -- a LOOP, not a metric. Neither
    C3 nor C4 supplies that. They test whether a SECOND-ORDER read of a first-order store recovers
    the paradigmatic relation; they do not make the store's objective correct.
  VSA algebraic binding is UNPINNED in the brain (three live accounts, published objections to
    each). Nothing here depends on it and nothing here tests it.
  SHELVE/REVIVAL, BRAIN-FRAMED: if C3/C4 do not move hit@1, the criterion is NOT "it did not
    score". It is that a second-order read cannot manufacture a distinction the WRITE never
    encoded, and the revival condition is a store whose value is built by a RESIDUAL update rather
    than a uniform sum.

SAME BAR AS THE SIBLING. Same landed OPEN pool, same WordNet gold, same scorer
(floor_battery.hit_at_1_both_tie_conventions, tie-corrected primary), same four floors ALL
recomputed here, same paired bootstrap, all three tie conventions. 0.1382 / 0.2070 / -0.1959 are
NEVER imported. Regression-gated against the landed 0.0223 and 0.0481. KA and NULL arms verified
before any treatment number.

ORGAN REUSE: experiments/exp_readout_ceiling_diagnosis_v1 (population, rank curve, random-ranking
null, tripwire), tools/floor_battery, experiments/exp_cue_to_store_translation_v1, tools/exp_checkpoint.
NONE is edited. NO EXTERNAL LANGUAGE MODEL ANYWHERE. ASCII-only. CPU. data/foundation/** untouched.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_readout_ceiling_diagnosis_v1 as DIAG          # population + rank curve, NEVER EDITED
import exp_cue_to_store_translation_v1 as CTS            # cache loaders + ruler gate, NEVER EDITED
from tools import floor_battery as FB                    # floors + scorer + bootstrap, NEVER EDITED
from tools.exp_checkpoint import completed_units, record_unit, unit_key

ANCHOR_NAME = "exp_readout_second_order_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_ceiling_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--arm", choices=("C1", "C2", "C3", "C4", "all"), default="all")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "reduced" if _ARGS.grid == "reduced" else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if RUN_MODE == "reduced" else 10000
KA_MIN = 0.95
FLOOR_NAMES = DIAG.FLOOR_NAMES
K_GRID = DIAG.K_GRID

# PARAMETER SWEEPS. Brain PARAMETERS are constraint-derived and are SWEPT, never adopted.
PROFILE_K = (10, 25, 50, 100, 250, 0)        # 0 = untruncated profile
SR_GAMMA = (0.3, 0.5, 0.7, 0.9)
SR_GRAPH_K = 25                              # out-degree of the anchor graph M is built on
COOC_MAX_ITEMS = 1500                        # C2 co-occurrence census cap (cost control, PRE-SET)


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _out_dir() -> str:
    return os.path.join(REPO_ROOT, "data",
                        ANCHOR_NAME + ("" if RUN_MODE == "full" else "_REDUCED"))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


# =================================================================================================
# THE TWO NEW READ-OUTS
# =================================================================================================
def second_order_scores(P: np.ndarray, Sq: np.ndarray, k: int,
                        self_idx: Optional[np.ndarray] = None) -> np.ndarray:
    """"Two words are similar if they have similar NEIGHBOURS."

    P  [n_anchors, n_anchors]  each anchor's similarity PROFILE over the store (first-order)
    Sq [n_anchors, n_items]    each query's similarity profile over the store (= the raw scores)
    k  keep only each profile's top-k entries, zero the rest (0 = no truncation)

    Returns cos(profile(a), profile(query_i)) for every (a, i).

    TRUNCATION IS THE WHOLE POINT AND IT IS A SWEPT PARAMETER, NOT A CHOICE. An untruncated profile
    is dominated by the long tail of near-zero similarities that every anchor shares, which is the
    same common component the constant floor exploits; truncation is what makes a second-order
    measure express PARADIGMATIC rather than SYNTAGMATIC similarity in the distributional tradition.
    k=0 is run so the untruncated case is measured, not assumed bad.

    THE SELF TERM IS REMOVED, AND THE SELF-TEST IS WHY. With the diagonal left in, a word that is
    DIRECTLY adjacent to the query outscores the query's true profile-twin: the two big self
    entries (prof_A[A] = 1 and prof_M[M] = 1) pair up with the direct similarities and hand the
    neighbour a large spurious overlap. On the T1 fixture that alone was the difference between the
    arm working and reading 0.0000. A word's similarity to ITSELF carries no information about its
    NEIGHBOURHOOD, which is the quantity a second-order measure is defined on, so removing it is
    the correct operation and not a tuning knob.
    """
    P = P.copy()
    np.fill_diagonal(P, 0.0)
    Sq = Sq.copy()
    if self_idx is not None:
        m = np.asarray(self_idx) >= 0
        Sq[np.asarray(self_idx)[m], np.flatnonzero(m)] = 0.0

    def trunc(M: np.ndarray) -> np.ndarray:
        if k <= 0:
            return M
        kk = int(min(k, M.shape[0] - 1))
        out = np.zeros_like(M)
        idx = np.argpartition(-M, kk - 1, axis=0)[:kk, :]
        cols = np.repeat(np.arange(M.shape[1])[None, :], kk, axis=0)
        out[idx.ravel(), cols.ravel()] = M[idx.ravel(), cols.ravel()]
        return out
    A = l2n(trunc(P).T)                 # [n_anchors, n_anchors] rows = truncated anchor profiles
    B = l2n(trunc(Sq).T)                # [n_items, n_anchors]   rows = truncated query profiles
    return (A @ B.T).astype(np.float32)


def successor_representation(P: np.ndarray, k: int, gamma: float) -> np.ndarray:
    """M = (I - gamma*A)^-1 on OUR OWN anchor graph. ORGAN_MAP D7's equation, never before run here.

    A is the row-stochastic k-nearest-neighbour graph of the store (self excluded). M[s, s'] is the
    discounted expected future occupancy of s' from s, i.e. exactly Stachenfeld, Botvinick &
    Gershman 2017's predictive map, computed in closed form rather than learned by TD -- which is
    also the honest choice, because TD learning is NOT known to be implemented in hippocampal
    networks and the closed form commits us to no learning rule we cannot defend.

    `gamma` IS A PARAMETER, swept. `k` is the graph's out-degree and is also ours.
    """
    n = P.shape[0]
    kk = int(min(k, n - 1))
    Pc = P.copy()
    np.fill_diagonal(Pc, -np.inf)
    idx = np.argpartition(-Pc, kk - 1, axis=1)[:, :kk]
    A = np.zeros((n, n), dtype=np.float64)
    rows = np.repeat(np.arange(n)[:, None], kk, axis=1)
    w = np.maximum(Pc[rows.ravel(), idx.ravel()], 0.0)
    A[rows.ravel(), idx.ravel()] = w
    rs = A.sum(axis=1, keepdims=True)
    A = A / np.maximum(rs, 1e-12)
    M = np.linalg.inv(np.eye(n, dtype=np.float64) - float(gamma) * A)
    return M.astype(np.float32)


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    DIAG.install_grounded_similarity_tripwire()
    ev["floor_battery_selftest_ok"] = sorted(FB.self_test().keys())

    rng = np.random.default_rng(5)
    d = 64
    n_pairs, n_med, n_fill = 20, 5, 60

    # --- T1. SECOND-ORDER RECOVERS A RELATION FIRST-ORDER CANNOT SEE. A can-fail known answer.
    #
    #     THE FIXTURE, and my FIRST attempt at it was WRONG and the assertion caught it (both arms
    #     read 0.0000): I built partners that shared a context direction, which made every word
    #     sharing that direction closer to the query than its own partner, so the second-order read
    #     had nothing to recover either. That fixture would have tested NOTHING while appearing to.
    #
    #     The construction below is the correct one and it is EXACTLY the syntagmatic/paradigmatic
    #     situation being claimed about the real store:
    #       A_p and B_p are ORTHOGONAL to each other (cos = 0) -- they never "occur together",
    #       so no first-order measure can link them;
    #       both are close to the SAME m MEDIATOR words (the contexts they each appear in).
    #     First-order argmax must therefore return a MEDIATOR, never the partner. A second-order
    #     read compares PROFILES, and A_p and B_p have nearly the same profile. If the second-order
    #     arm cannot win here it is not measuring what it claims to.
    n = 2 * n_pairs + n_pairs * n_med + n_fill
    X = np.zeros((n, d), dtype=np.float32)
    partner: Dict[int, int] = {}
    row = 0
    med_rows = []
    for p in range(n_pairs):
        u = rng.standard_normal(d).astype(np.float32)
        u /= np.linalg.norm(u) + 1e-9
        w = rng.standard_normal(d).astype(np.float32)
        w -= (w @ u) * u                                  # w PERPENDICULAR to u -> cos(A,B) = 0
        w /= np.linalg.norm(w) + 1e-9
        a_i, b_i = row, row + 1
        X[a_i], X[b_i] = u, w
        partner[a_i], partner[b_i] = b_i, a_i
        row += 2
        for _ in range(n_med):                            # the shared contexts
            # the mediators must be mutually DISSIMILAR, or they form their own tight cluster and
            # win on any measure. A large private component is what keeps them distinct contexts
            # rather than five copies of one context.
            r = rng.standard_normal(d).astype(np.float32)
            r -= (r @ u) * u
            r -= (r @ w) * w
            r /= np.linalg.norm(r) + 1e-9
            m = 0.45 * u + 0.45 * w + 0.78 * r
            X[row] = m / (np.linalg.norm(m) + 1e-9)
            med_rows.append(row)
            row += 1
    X[row:] = l2n(rng.standard_normal((n - row, d)).astype(np.float32))
    Xn = l2n(X)
    P = (Xn @ Xn.T).astype(np.float32)
    qi = np.array(sorted(partner), dtype=np.int64)
    gold_idx = np.array([partner[int(q)] for q in qi], dtype=np.int64)
    Sq = P[:, qi].copy()
    E = np.ones((n, qi.size), dtype=bool)
    E[qi, np.arange(qi.size)] = False                # a word may not answer with itself
    G = np.zeros((n, qi.size), dtype=bool)
    G[gold_idx, np.arange(qi.size)] = True
    h1 = FB.hit_at_1_both_tie_conventions(Sq, E, G)["hit_exp"].mean()
    h2 = FB.hit_at_1_both_tie_conventions(second_order_scores(P, Sq, 10, qi), E, G)["hit_exp"].mean()
    # the fixture must be one FIRST-ORDER GENUINELY CANNOT DO, or "second-order wins" is vacuous
    assert h1 < 0.10, ("the fixture is not first-order-hard (first=%.4f) -- a second-order win on "
                       "it would prove nothing" % h1)
    assert h2 > h1 + 0.50, ("the second-order read does NOT recover a shared-neighbour relation "
                            "that first-order misses: first=%.4f second=%.4f" % (h1, h2))
    ev["T1_second_order_recovers_what_first_order_misses"] = {
        "first_order_hit1": round(float(h1), 4), "second_order_hit1": round(float(h2), 4),
        "fixture": "partners ORTHOGONAL to each other, both close to the same %d mediators; "
                   "%d pairs, %d fillers, d=%d" % (n_med, n_pairs, n_fill, d)}

    # --- T2. AND IT CAN FAIL. On a fixture where the gold is a RANDOM unrelated word, the
    #     second-order read must NOT manufacture a hit. An arm that only ever wins is not an arm.
    Grnd = np.zeros((n, qi.size), dtype=bool)
    r = rng.permutation(n)[:qi.size]
    Grnd[r, np.arange(qi.size)] = True
    h2r = FB.hit_at_1_both_tie_conventions(second_order_scores(P, Sq, 10, qi), E, Grnd)["hit_exp"].mean()
    assert h2r < 0.10, "the second-order read fires on a random gold: %.4f" % h2r
    ev["T2_second_order_can_fail"] = {"random_gold_hit1": round(float(h2r), 4)}

    # --- T3. TRUNCATION ACTUALLY CHANGES THE ANSWER (the swept parameter is a real parameter).
    hs = {k: float(FB.hit_at_1_both_tie_conventions(second_order_scores(P, Sq, k, qi), E, G)
                   ["hit_exp"].mean()) for k in (5, 25, 0)}
    assert len(set(round(v, 6) for v in hs.values())) > 1, \
        "profile truncation k does nothing -- it is not a parameter, it is decoration"
    ev["T3_truncation_is_a_real_parameter"] = {str(k): round(v, 4) for k, v in hs.items()}

    # --- T4. THE SUCCESSOR REPRESENTATION IS THE MATRIX IT CLAIMS TO BE.
    #     (I - gamma A) M = I to numerical tolerance, M is non-negative for a non-negative A, and
    #     gamma -> 0 collapses M to the identity (no propagation), which is the sanity boundary.
    Msr = successor_representation(P, 8, 0.5)
    kk = 8
    Pc = P.copy(); np.fill_diagonal(Pc, -np.inf)
    idx = np.argpartition(-Pc, kk - 1, axis=1)[:, :kk]
    A = np.zeros((n, n), dtype=np.float64)
    rr = np.repeat(np.arange(n)[:, None], kk, axis=1)
    A[rr.ravel(), idx.ravel()] = np.maximum(Pc[rr.ravel(), idx.ravel()], 0.0)
    A = A / np.maximum(A.sum(axis=1, keepdims=True), 1e-12)
    resid = np.abs((np.eye(n) - 0.5 * A) @ Msr.astype(np.float64) - np.eye(n)).max()
    assert resid < 1e-6, "(I - gamma A) M != I, residual %.3e -- the SR is not an SR" % resid
    assert np.all(A.sum(axis=1) > 0.999), "the SR graph is not row-stochastic"
    M0 = successor_representation(P, 8, 1e-9)
    assert np.abs(M0 - np.eye(n, dtype=np.float32)).max() < 1e-5, \
        "gamma -> 0 does not collapse the SR to the identity"
    ev["T4_successor_representation_is_correct"] = {
        "max_abs_residual_of_(I-gammaA)M_minus_I": float(resid),
        "gamma_to_zero_collapses_to_identity": True,
        "row_stochastic": True}

    # --- T5. the SR read can BOTH fire and fail, on the same two fixtures as T1/T2.
    Msr = successor_representation(P, 8, 0.7)
    S_sr = Msr[:, qi].copy()
    hsr = FB.hit_at_1_both_tie_conventions(S_sr, E, G)["hit_exp"].mean()
    hsr_r = FB.hit_at_1_both_tie_conventions(S_sr, E, Grnd)["hit_exp"].mean()
    assert hsr_r < 0.15, "the SR read fires on a random gold: %.4f" % hsr_r
    ev["T5_SR_read_fires_and_fails"] = {"planted_gold": round(float(hsr), 4),
                                        "random_gold": round(float(hsr_r), 4)}

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1200], flush=True)
    return ev


# =================================================================================================
def run(grid: str, which: str, output_dir: str) -> Dict:
    t0 = time.time()
    gate = CTS.ruler_mode_gate()
    tripwire = DIAG.install_grounded_similarity_tripwire()
    P0 = DIAG.build_population()
    C, mat, mat_ok = P0["C"], P0["mat"], P0["mat_ok"]
    n_anchors, qidx = P0["n_anchors"], P0["qidx"]
    GOLD, E, keep_ALL = P0["GOLD"], P0["E"], P0["keep"]
    anchors = P0["anchors"]
    aux = P0["aux"]

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T, E_T = GOLD[:, T].copy(), E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    MATn = l2n(mat)
    print("[load] n_anchors=%d n_items=%d t=%.0fs" % (n_anchors, n_items, time.time() - t0),
          flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "arm": which, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(tripwire),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "population": {"n_anchors": n_anchors, "n_items_scored": n_items,
                       "pool": "the LANDED OPEN pool, identical to the sibling diagnosis cell",
                       "gold": "WordNet 3.0 generous set, exp_grounding_readout_known_answer_v1",
                       "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions"},
    }

    # ---- REGRESSION + VALIDITY, before anything ------------------------------------------------
    S = (MATn @ l2n(Q_exact).T).astype(np.float32)
    S_pf = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h = FB.hit_at_1_both_tie_conventions(S_pf, E, GOLD)
    a0 = float(h["hit_exp"][h["scored"] & keep_ALL].mean())
    del S_pf, h
    S_ef = (MATn @ l2n(C["Q_exact"]).T).astype(np.float32)
    h = FB.hit_at_1_both_tie_conventions(S_ef, E, GOLD)
    a1 = float(h["hit_exp"][h["scored"] & keep_ALL].mean())
    del S_ef, h
    rep["REGRESSION_GATE"] = {
        "partial_cue_FULL_POP": round(a0, 4), "expected": DIAG.REGRESSION_A0_PARTIAL,
        "exact_key_FULL_POP": round(a1, 4), "expected_exact": DIAG.REGRESSION_A1_EXACT,
        "PASS": bool(abs(a0 - DIAG.REGRESSION_A0_PARTIAL) <= DIAG.REGRESSION_TOL
                     and abs(a1 - DIAG.REGRESSION_A1_EXACT) <= DIAG.REGRESSION_TOL)}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED: %r" % rep["REGRESSION_GATE"])
    ok_q = qidx_T >= 0
    ka = float(np.mean(np.argmax(S, axis=0)[ok_q] == qidx_T[ok_q]))
    rng = np.random.default_rng(MASTER_SEED + 77)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    hn = FB.hit_at_1_both_tie_conventions(S[:, perm], E_T, GOLD_T)
    rep["VALIDITY"] = {
        "KA_SELF_ADDRESS": {"value": round(ka, 4), "gate": KA_MIN, "PASS": bool(ka >= KA_MIN)},
        "NULL_PERMUTED": {"hit_at_1": round(float(hn["hit_exp"][hn["scored"]].mean()), 6),
                          "addressing": round(float(np.mean(
                              np.argmax(S[:, perm], axis=0)[ok_q] == qidx_T[ok_q])), 8),
                          "chance_addressing": round(1.0 / n_anchors, 8)},
        "they_fail_independently": "a scorer/comparator bug drops KA and leaves NULL at chance; a "
                                   "pairing or leak bug leaves KA at ceiling and lifts NULL."}
    if ka < KA_MIN:
        raise SystemExit("KA ARM FAILED (%.4f) -- no treatment number read" % ka)
    print("[regression] partial=%.4f exact=%.4f | KA=%.4f NULL=%.6f"
          % (a0, a1, ka, rep["VALIDITY"]["NULL_PERMUTED"]["hit_at_1"]), flush=True)

    # ---- FLOORS, ALL recomputed here ------------------------------------------------------------
    floors_S: Dict[str, np.ndarray] = {}
    try:
        floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(aux["Tq"][T]).T).astype(np.float32)
    except Exception as exc:
        rep.setdefault("FLOOR_NOTES", {})["F_ORTHOGRAPHIC"] = "UNAVAILABLE: %r" % (exc,)
    try:
        floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
            FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    except Exception as exc:
        rep.setdefault("FLOOR_NOTES", {})["F_FREQUENCY"] = "UNAVAILABLE: %r" % (exc,)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 91))
                              @ l2n(Q_exact).T).astype(np.float32)
    const_vec = FB.constant_prototype_floor(mat, mat_ok)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_vec, n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors,
                                  [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959"]

    hits_exp, hits_opt, hits_cons, tie_of = {}, {}, {}, {}
    scored_all = np.ones(n_items, dtype=bool)

    def add_arm(name: str, Sx: np.ndarray) -> None:
        nonlocal scored_all
        hh = FB.hit_at_1_both_tie_conventions(Sx, E_T, GOLD_T)
        hits_exp[name] = hh["hit_exp"]; hits_opt[name] = hh["hit_opt"]
        hits_cons[name] = hh["hit_cons"]; tie_of[name] = float(hh["tie_mass"].mean())
        scored_all = scored_all & hh["scored"]

    for k, Sf in floors_S.items():
        add_arm(k, Sf)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)
    add_arm("R0_COSINE_ARGMAX_INCUMBENT", S)

    # ---- C1. WINNER FORENSICS -------------------------------------------------------------------
    if which in ("C1", "all"):
        Sm = np.where(E_T, S, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        try:
            from nltk.corpus import wordnet as wn
            rel = Counter()
            examples: List[str] = []
            n_probe = int(min(n_items, 2000))
            for i in range(n_probe):
                qw, ww = C["L_words"][int(T[i])], anchors[int(top1[i])]
                if GOLD_T[int(top1[i]), i]:
                    rel["IN_THE_GENEROUS_GOLD"] += 1
                    continue
                sq, sw = wn.synsets(qw), wn.synsets(ww)
                if not sq or not sw:
                    rel["WINNER_NOT_IN_WORDNET"] += 1
                    continue
                best = 0.0
                for a in sq[:4]:
                    for b in sw[:4]:
                        if a.pos() != b.pos():
                            continue
                        p = a.path_similarity(b)
                        if p and p > best:
                            best = float(p)
                if best >= 0.25:
                    rel["TAXONOMICALLY_CLOSE_but_outside_the_gold"] += 1
                elif best > 0.0:
                    rel["TAXONOMICALLY_DISTANT"] += 1
                else:
                    rel["NO_WORDNET_PATH_AT_ALL"] += 1
                if len(examples) < 40:
                    examples.append("%s -> %s (path_sim=%.3f)" % (qw, ww, best))
            rep["C1_WINNER_FORENSICS"] = {
                "n_probed": n_probe,
                "what_the_top1_pick_IS": {k: int(v) for k, v in rel.most_common()},
                "as_fraction": {k: round(v / n_probe, 4) for k, v in rel.most_common()},
                "examples": examples,
                "reading": "the generous gold already contains synonyms, hypernyms 2 up, sisters "
                           "and hyponyms. A winner OUTSIDE it that also has no close WordNet path "
                           "is not a taxonomic near-miss at all -- it is a different KIND of "
                           "relation, which is what C2 tests directly."}
            print("[C1] " + json.dumps(rep["C1_WINNER_FORENSICS"]["as_fraction"]), flush=True)
        except Exception as exc:
            rep["C1_WINNER_FORENSICS"] = {"UNAVAILABLE": "%r" % (exc,)}
        record_unit(output_dir, unit_key("C1", "forensics"), rep.get("C1_WINNER_FORENSICS", {}))
        del Sm

    # ---- C2. THE SYNTAGMATIC TEST ---------------------------------------------------------------
    if which in ("C2", "all"):
        try:
            from experiments.exp_grounding_readout_known_answer_v1 import content_lemmas
            from experiments.exp_definitional_grounding_v5 import load_corpus_v5
            t1 = time.time()
            sents = [s for _seg, s in load_corpus_v5(None, lineaware=True)]
            print("[C2] corpus re-read for COUNTS ONLY: %d sentences t=%.0fs (THE STORE IS NOT "
                  "REBUILT)" % (len(sents), time.time() - t1), flush=True)
            sent_sets = [set(content_lemmas(s)) for s in sents]
            where: Dict[str, set] = {}
            for si, ls in enumerate(sent_sets):
                for w in ls:
                    where.setdefault(w, set()).add(si)
            Sm = np.where(E_T, S, -np.inf)
            top1 = np.argmax(Sm, axis=0)
            gbest = np.where(GOLD_T & E_T, Sm, -np.inf)
            gtop = np.argmax(gbest, axis=0)
            del Sm, gbest
            rr = np.random.default_rng(MASTER_SEED + 5)
            elig_idx = np.flatnonzero(mat_ok)

            def jac(a: str, b: str) -> Optional[float]:
                A, B = where.get(a), where.get(b)
                if not A or not B:
                    return None
                return len(A & B) / float(len(A | B))

            n_probe = int(min(n_items, COOC_MAX_ITEMS))
            jw, jg, jr = [], [], []
            for i in range(n_probe):
                qw = C["L_words"][int(T[i])]
                for lst, other in ((jw, anchors[int(top1[i])]), (jg, anchors[int(gtop[i])]),
                                   (jr, anchors[int(elig_idx[rr.integers(elig_idx.size)])])):
                    v = jac(qw, other)
                    if v is not None:
                        lst.append(v)
            def stat(x):
                x = np.asarray(x, dtype=np.float64)
                return {"n": int(x.size), "mean": round(float(x.mean()), 5),
                        "median": round(float(np.median(x)), 5),
                        "frac_ever_co_occurring": round(float((x > 0).mean()), 4)}
            rep["C2_SYNTAGMATIC_TEST"] = {
                "PRE_REGISTERED_PREDICTION":
                    "the top-1 WINNER co-occurs with the query word in the same sentence far more "
                    "than the best GOLD synonym does. If it fires, our store's neighbourhood is "
                    "SYNTAGMATIC (occurs-with) where the task is PARADIGMATIC (substitutes-for), "
                    "and that is a property of the WRITE RULE (a first-order co-occurrence sum), "
                    "not of the comparator.",
                "measure": "sentence-level Jaccard over the corpus the store was built from; "
                           "counts only, THE STORE IS NEVER REBUILT",
                "n_sentences": len(sents),
                "TOP1_WINNER": stat(jw), "BEST_GOLD_SYNONYM": stat(jg),
                "RANDOM_ELIGIBLE_ANCHOR": stat(jr),
                "winner_over_gold_ratio_of_means":
                    round(float(np.mean(jw)) / max(float(np.mean(jg)), 1e-12), 2) if jw and jg
                    else None,
                "VERDICT": ("SYNTAGMATIC_CONFIRMED" if jw and jg
                            and float(np.mean(jw)) > 1.5 * float(np.mean(jg))
                            else "SYNTAGMATIC_NOT_CONFIRMED")}
            print("[C2] winner_cooc=%s gold_cooc=%s random=%s -> %s"
                  % (rep["C2_SYNTAGMATIC_TEST"]["TOP1_WINNER"]["mean"],
                     rep["C2_SYNTAGMATIC_TEST"]["BEST_GOLD_SYNONYM"]["mean"],
                     rep["C2_SYNTAGMATIC_TEST"]["RANDOM_ELIGIBLE_ANCHOR"]["mean"],
                     rep["C2_SYNTAGMATIC_TEST"]["VERDICT"]), flush=True)
            del sents, sent_sets, where
        except Exception as exc:
            rep["C2_SYNTAGMATIC_TEST"] = {"UNAVAILABLE": "%r" % (exc,),
                                          "traceback": traceback.format_exc()[-1500:]}
            print("[C2] UNAVAILABLE: %r" % (exc,), flush=True)
        record_unit(output_dir, unit_key("C2", "cooc"), rep.get("C2_SYNTAGMATIC_TEST", {}))

    # ---- C3 / C4. THE TWO NEW READ-OUTS ---------------------------------------------------------
    ka_of: Dict[str, float] = {}
    if which in ("C3", "C4", "all"):
        print("[C3] building the first-order anchor-anchor profile matrix (%d x %d) ..."
              % (n_anchors, n_anchors), flush=True)
        P = (MATn @ MATn.T).astype(np.float32)
        if which in ("C3", "all"):
            for k in PROFILE_K:
                nm = "C3_SECOND_ORDER_profileK%d" % k
                Sx = second_order_scores(P, S, k, qidx_T)
                add_arm(nm, Sx)
                ka_of[nm] = float(np.mean(np.argmax(Sx, axis=0)[ok_q] == qidx_T[ok_q]))
                record_unit(output_dir, unit_key("C3", nm), {"ka": round(ka_of[nm], 4)})
                print("[C3] %-32s KA=%.4f t=%.0fs" % (nm, ka_of[nm], time.time() - t0), flush=True)
                del Sx
        if which in ("C4", "all"):
            for g in SR_GAMMA:
                nm = "C4_SUCCESSOR_REPRESENTATION_gamma%g" % g
                M = successor_representation(P, SR_GRAPH_K, g)
                Sx = M[:, qidx_T].copy()
                Sx[:, ~ok_q] = 0.0
                add_arm(nm, Sx)
                ka_of[nm] = float(np.mean(np.argmax(Sx, axis=0)[ok_q] == qidx_T[ok_q]))
                record_unit(output_dir, unit_key("C4", nm), {"ka": round(ka_of[nm], 4)})
                print("[C4] %-32s KA=%.4f t=%.0fs" % (nm, ka_of[nm], time.time() - t0), flush=True)
                del M, Sx
        del P
        rep["KA_PER_NEW_READOUT"] = {
            "what": "the KNOWN-ANSWER arm re-run for every new read-out. NOTE, and it is a real "
                    "caveat not a formality: a SECOND-ORDER read-out is NOT expected to address "
                    "the item's own row at 1.0000, because a word's profile is similar to its "
                    "NEIGHBOURS' profiles by construction. A low KA here is a property of the "
                    "measure, not necessarily a broken instrument -- so it is REPORTED beside each "
                    "arm and is NOT used to void an arm the way it is for the first-order family.",
            "values": {k: round(v, 4) for k, v in ka_of.items()}}

    # ---- SCORING --------------------------------------------------------------------------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_opt = FB.paired_bootstrap_ci(hits_opt, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_cons = FB.paired_bootstrap_ci(hits_cons, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    nc = pb["n_common"]
    margins = {}
    if binding:
        for k in sorted(acc):
            if k == binding or k.startswith("ORACLE"):
                continue
            mg = FB.margin(boot, k, binding)
            mg["ci_halfwidth"] = round((mg["ci95"][1] - mg["ci95"][0]) / 2.0, 5)
            mg["analytic_null_halfwidth_at_this_n"] = round(DIAG._halfwidth(acc[binding], nc), 5)
            mg["arm_value"] = round(acc[k], 5)
            mg["margin_over_own_ci_halfwidth"] = round(
                abs(mg["point"]) / max(mg["ci_halfwidth"], 1e-9), 2)
            margins[k] = mg
    rep["HIT_AT_1"] = {
        "n_common_scored": nc, "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED",
        "tie_corrected": {k: round(v, 5) for k, v in acc.items()},
        "optimistic_tie": {k: round(v, 5) for k, v in pb_opt["acc"].items()},
        "conservative_tie": {k: round(v, 5) for k, v in pb_cons["acc"].items()},
        "mean_tie_mass": {k: round(v, 5) for k, v in tie_of.items()},
        "BINDING_FLOOR": binding,
        "BINDING_FLOOR_VALUE": round(acc[binding], 5) if binding else None,
        "ALL_FOUR_FLOORS": {f: round(acc[f], 5) for f in present},
        "ORACLE_CONSTANT_not_a_floor":
            round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 5),
        "MARGIN_vs_binding_floor_TIE_CORRECTED": margins,
        "ARMS_CI_SEPARATED_ABOVE_THE_BINDING_FLOOR":
            sorted(k for k, v in margins.items() if v["band"] == "ABOVE"),
        "ARMS_CI_SEPARATED_ABOVE_THE_INCUMBENT":
            sorted(k for k in acc if k not in ("R0_COSINE_ARGMAX_INCUMBENT",)
                   and not k.startswith(("F_", "ORACLE"))
                   and FB.margin(boot, k, "R0_COSINE_ARGMAX_INCUMBENT")["band"] == "ABOVE"),
        "MARGIN_vs_the_INCUMBENT": {
            k: FB.margin(boot, k, "R0_COSINE_ARGMAX_INCUMBENT") for k in sorted(acc)
            if k != "R0_COSINE_ARGMAX_INCUMBENT" and not k.startswith("ORACLE")},
    }
    rep["POWER"] = {"n_common_scored": nc,
                    "binom_ci_halfwidth_at_binding_floor":
                        round(DIAG._halfwidth(acc[binding], nc), 6) if binding else None,
                    "reading": "A WIDTH IS NOT AN EFFECT. Every margin carries "
                               "margin_over_own_ci_halfwidth beside it."}
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = {
        "loaded": sorted(m for m in sys.modules if m.startswith(("hdlab", "tools.", "exp_"))),
        "edited_by_this_cell": []}
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def decide(rep: Dict) -> Tuple[str, str]:
    parts, msg = [], []
    c2 = rep.get("C2_SYNTAGMATIC_TEST", {})
    if "VERDICT" in c2:
        parts.append(c2["VERDICT"])
        msg.append("C2 co-occurrence: winner %s vs best-gold %s vs random %s (ratio %s)"
                   % (c2["TOP1_WINNER"]["mean"], c2["BEST_GOLD_SYNONYM"]["mean"],
                      c2["RANDOM_ELIGIBLE_ANCHOR"]["mean"], c2.get("winner_over_gold_ratio_of_means")))
    h = rep.get("HIT_AT_1")
    if h:
        ab, ai = (h["ARMS_CI_SEPARATED_ABOVE_THE_BINDING_FLOOR"],
                  h["ARMS_CI_SEPARATED_ABOVE_THE_INCUMBENT"])
        parts.append("NEW_READOUT_CLEARS_FLOOR_%s" % ("YES" if ab else "NO"))
        parts.append("BEATS_INCUMBENT_%s" % ("YES" if ai else "NO"))
        msg.append("binding floor %s=%s; incumbent=%s; %d arms above the floor, %d above the "
                   "incumbent%s" % (h["BINDING_FLOOR"], h["BINDING_FLOOR_VALUE"],
                                    h["tie_corrected"].get("R0_COSINE_ARGMAX_INCUMBENT"),
                                    len(ab), len(ai), (": " + ", ".join(ai[:5])) if ai else ""))
    return "__".join(parts) if parts else "NO_ARM_RUN", " || ".join(msg)


def main() -> None:
    args = _ap.parse_args()
    if args.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return
    output_dir = _out_dir()
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"),
                 {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                  "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "arm": args.arm})
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(args.grid, args.arm, output_dir)
        v, m = decide(rep)
        rep["verdict"], rep["verdict_msg"], rep["wire_status"] = v, m, "VET_PENDING"
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        print(json.dumps({"verdict": v, "verdict_msg": m}, indent=2), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(output_dir, "_crash_diagnostic.json"),
                     {"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise


if __name__ == "__main__":
    main()
