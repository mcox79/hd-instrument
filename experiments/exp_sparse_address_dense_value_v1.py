"""exp_sparse_address_dense_value_v1 -- ITEM 3: SPARSIFY THE ADDRESS, KEEP THE VALUE DENSE.

THE QUESTION
------------
Our store is ONE FLAT OBJECT asked to be both key and value, scored by cosine in one space. Does a
SPARSE ADDRESS pointing at a DENSE GRADED VALUE, returned by LINK and NEVER RECONSTRUCTED, address
better under a partial cue than the flat store?

WHY THE CONFIDENCE IN THIS DESIGN IS HIGHER THAN IN EITHER ROUTE ALONE -- TWO LITERATURES CONVERGE
--------------------------------------------------------------------------------------------------
ROUTE ONE, hippocampal indexing (Teyler & DiScenna 1986; Teyler & Rudy 2007; Goode et al. 2020):
the hippocampus computes a sparse POINTER SET into distributed neocortical activity and THE CONTENT
NEVER ENTERS IT; retrieval is reinstatement of the LINKED cortical pattern, not reconstruction from
the index. PINNED as an architecture on engram-tagging and optogenetic reactivation.
ROUTE TWO, the four sparsity objectives, which the literature routinely conflates and so did we:
CAPACITY/INTERFERENCE (Marr; Willshaw; Treves & Rolls, p ~ C/(a ln(1/a))) wants the KEY sparse;
EFFICIENT CODING OF STATISTICS (Barlow; Olshausen & Field) wants the VALUE dense and graded. We
applied the capacity objective's optimum and then measured the efficient-coding objective's
quantity -- which is exactly why the pinned MTL band was the WORST meaning zone in its own sweep
(0.0396 at f=0.002 against 0.0744 dense). SEPARATION IS THE DELIBERATE DESTRUCTION OF SIMILARITY;
a code optimised to make two similar things orthogonal is optimised to make a similarity judgement
impossible. Applying it to a MEANING metric should hurt, and it did, monotonically.
Two independent literatures prescribe the same unbuilt design. This is that design.

THE REGIME IS SET PER ORGAN, NOT GLOBALLY. The owner: "we have a phase diagram for substrate -- we
can set all variables, including dimensionality, wherever we want for each process. The brain does
some in sparse space, some in dense, and we have the ability to change them on the fly."
WHAT THIS CELL SETS, ORGAN BY ORGAN, AND WHY:

  ORGAN                     REGIME SET HERE                       BASIS
  VALUE / meaning store     DENSE, d=256, graded, NEVER           efficient-coding objective; and
                            sparsified, returned by LINK          our own sweep says the best
                                                                  sparse value point is +0.0030
                                                                  [-0.0030,+0.0088] over dense =
                                                                  NOT separated. Nothing to win.
  ADDRESS-WRITE / key       EXPANDED then SPARSE. expansion       capacity/interference objective;
  (dentate-like)            SWEPT 1x/8x/32x, active fraction      EC II -> DG is an EXPANSION into
                            a_w SWEPT 0.002/0.01/0.05/0.20        a ~100x sparser code. Ratios are
                                                                  PARAMETERS, swept, not adopted.
  ADDRESS-READ / cue        DENSER THAN THE KEY. a_r swept        Treves & Rolls 1992's two-input
  (perforant-like)          INDEPENDENTLY: symmetric / 0.20 /     argument: STORE with few strong
                            1.00 (fully dense cue)                signals (mossy fibre), RETRIEVE
                                                                  with a numerically LARGE input
                                                                  through individually WEAK
                                                                  synapses (direct perforant path).
  REGIME SWITCH             a_w != a_r IS the switch.             O'Reilly & McClelland 1994 is
  (Hasselmo SPEAR)          a_w == a_r is the incumbent's         titled "avoiding a trade-off";
                            ONE operating point for both          the field's resolution is a
                            write and read.                       REGIME SWITCH, not a parameter
                                                                  setting. We have no switch at all.

COPY THE COMPUTATION, SWEEP THE PARAMETER. COMPUTATIONS COPIED: expansion BEFORE sparsification;
separation at encoding and completion at retrieval as an ordered pair; a dense cue addressing a
sparse store; key and value as DIFFERENT objects with DIFFERENT regimes; retrieval by LINK.
PARAMETERS SWEPT, NEVER ADOPTED: the ~5x expansion ratio, the ~100x sparsening, the 0.2% MTL active
fraction. OURS, INVENTION UNDER TEST: the expansion operator (a Gaussian random projection), the
k-winner sparsifier, and the index ALLOCATION rule -- nothing in the literature says which cells get
recruited to an index, so that choice is ours.
CONTESTED AND REPORTED AS CONTESTED: there are FOUR live accounts of what the hippocampus computes
-- index (sparse address + linked value), conjunctive autoassociative store (a compressed CONTENT
vector), relational map (an EDGE), predictive map (a discounted-future occupancy). OUR FLAT STORE IS
THE CONJUNCTIVE ACCOUNT DONE WITHOUT THE SPARSITY THAT ACCOUNT'S OWN CAPACITY EQUATION REQUIRES.
Goode 2020 proposes they reconcile at different levels; that reconciliation is a proposal, not a
measurement, and this cell does not adjudicate it.
(Standing caveat: VSA ALGEBRAIC BINDING ITSELF IS UNPINNED IN THE BRAIN. The representation being
addressed is invention-under-test, not biology.)

THE MEASUREMENT
---------------
PRIMARY, PART 1: ADDRESSING ACCURACY -- does the cue's top-scoring anchor IN KEY SPACE equal the
anchor the cue was written from? This is the isolated blocker: the sparse key addresses the store
1.0000 from the store's own rows and 0.0325 from the partial cue. THOSE TWO NUMBERS ARE FROM A
DIFFERENT CELL ON A DIFFERENT POPULATION (n=1997) AND ARE NOT IMPORTED AS A COMPARISON. This cell
recomputes the incumbent on ITS OWN population and reports both side by side, labelled.
SECONDARY, PART 2: read-out hit@1 against the full four-floor battery on the pool ladder.

VALIDITY, DEMONSTRATED BEFORE ANY TREATMENT NUMBER
  K1_ORACLE_ADDRESS   hand the correct address; the LINK stage must return ~1.0 or the instrument
                      is dead and no quality number is published.
  N1_RANDOM_ADDRESS   a size-matched random key per anchor, carrying NO structure of its value;
                      must sit at chance at every expansion level.
  EXACT-KEY arm       the known-answer regime; must stay at 1.0000 at every level.
  The two are broken in turn in --self-test and the other is shown to survive.

BETWEEN-PROJECTION-DRAW VARIANCE IS REPORTED BESIDE THE ITEM BOOTSTRAP CI. Item bootstraps are
blind to shared-randomness variance and every cell built on a random projection must report it;
three independent projection draws are run at the reference expansion.

FLOORS: CI-separated over max(ORTHOGRAPHIC, FREQUENCY, SCRAMBLE, CONSTANT) COMPUTED ON THIS CELL'S
OWN POPULATION WITH ITS OWN n, under all three tie conventions. 0.1382 and 0.2070 are NEVER
imported. The per-pool oracle check is RUN and REPORTED for every pool.
NEVER uses grounded_similarity() as a scorer. ASCII-only. No LLM anywhere in the flow.
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
from datetime import datetime, timezone
from typing import Dict, List, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402
from tools.floor_battery import (                                                    # noqa: E402
    as_constant_matrix, balanced_candidate_sets, constant_prototype_floor, frequency_floor,
    hit_at_1_both_tie_conventions, l2n, oracle_constant_scores, pool_admits_a_winning_constant,
    scramble_null,
)

ANCHOR_NAME = "exp_sparse_address_dense_value_v1"
CODE_VERSION = "v1.0.1"   # bumped when the dense-key path and the a_write=1.00 rung were added;
                          # the bump gives a CLEAN SLATE by key rather than by deleting anything
OUT_DIR_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_DIR_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")

MASTER_SEED = 20260817
K_LIST = (15, 49)
KA_CEILING_MIN = 0.95

# PARAMETERS -- ALL SWEPT, NONE ADOPTED. 0.002 is the pinned MTL band, entered as a HYPOTHESIS.
D_KEYS = (256, 2048, 8192)
# a_write = 1.00 is THE INCUMBENT ADDRESS (a fully dense key). Without that rung the cell cannot
# say whether sparsifying the address helps -- it could only compare sparse against sparser.
A_WRITE = (0.002, 0.01, 0.05, 0.20, 1.00)
A_READ = ("sym", 0.20, 1.00)
PROJ_SEEDS = (0, 1, 2)
D_REF = 2048                      # the level at which the between-draw SD is measured


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=float).encode("utf-8"))
    os.replace(tmp, path)


def col(v: np.ndarray) -> np.ndarray:
    return np.asarray(v, dtype=np.float32).reshape(-1, 1)


# =================================================================================================
# the two organ operators
# =================================================================================================
def expand(X: np.ndarray, D: int, seed: int) -> np.ndarray:
    """THE EXPANSION. Gaussian random projection d -> D. OURS, invention under test: the brain's
    EC II -> DG expansion is a divergent anatomical projection, not a Gaussian matrix; what is
    copied is the COMPUTATION (expand before sparsifying), not the operator."""
    if D == X.shape[1]:
        return np.asarray(X, dtype=np.float32)
    rng = np.random.default_rng(seed)
    R = rng.standard_normal((X.shape[1], D), dtype=np.float32) / np.float32(np.sqrt(X.shape[1]))
    return (np.asarray(X, dtype=np.float32) @ R).astype(np.float32)


def sparsify(X: np.ndarray, frac: float, binary: bool = False) -> sp.csr_matrix:
    """k-WINNERS-TAKE-ALL by magnitude, returned SPARSE. frac=1.0 leaves the row fully dense.

    `binary=True` keeps only WHICH units are active (the dentate analogue: a set of active granule
    cells carries no graded value); `binary=False` keeps the signed value inside the active set.
    Both are reported; neither is assumed.
    """
    X = np.asarray(X, dtype=np.float32)
    n, D = X.shape
    k = D if frac >= 1.0 else max(1, int(round(float(frac) * D)))
    if k >= D and not binary:
        return sp.csr_matrix(X)
    idx = np.argpartition(-np.abs(X), kth=min(k, D - 1) - 1 if k < D else D - 1, axis=1)[:, :k]
    rows = np.repeat(np.arange(n, dtype=np.int64), k)
    cols = idx.ravel()
    vals = X[rows, cols]
    if binary:
        vals = np.sign(vals).astype(np.float32)
    M = sp.csr_matrix((vals.astype(np.float32), (rows, cols)), shape=(n, D))
    M.sum_duplicates()
    return M


def rownorm_csr(M: sp.csr_matrix) -> sp.csr_matrix:
    """L2-normalise CSR rows, zero-safe, so a sparse dot IS a cosine."""
    M = M.tocsr(copy=True)
    nrm = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel())
    inv = 1.0 / np.maximum(nrm, 1e-12)
    M = sp.diags(inv.astype(np.float32)) @ M
    return M.tocsr()


def code_matrix(X: np.ndarray, D: int, frac: float, binary: bool, seed: int):
    """Expand then sparsify, row-normalised. Returns DENSE ndarray when frac >= 1.0 and the code is
    signed (a fully dense key is the INCUMBENT rung, and materialising it as CSR at D=8192 costs
    ~700 MB for no benefit), otherwise a CSR matrix. `pair` handles both."""
    Xe = expand(X, D, seed)
    if frac >= 1.0 and not binary:
        return l2n(Xe)
    return rownorm_csr(sparsify(Xe, frac, binary))


def pair(A, B) -> np.ndarray:
    """[n_A, n_B] cosine scores for any combination of dense ndarray and CSR row-normalised codes."""
    a_sp, b_sp = sp.issparse(A), sp.issparse(B)
    if a_sp and b_sp:
        return (A @ B.T).toarray().astype(np.float32)
    if a_sp and not b_sp:
        return (A @ np.asarray(B, dtype=np.float32).T).astype(np.float32)
    if (not a_sp) and b_sp:
        return (B @ np.asarray(A, dtype=np.float32).T).T.astype(np.float32)
    return (np.asarray(A, dtype=np.float32) @ np.asarray(B, dtype=np.float32).T).astype(np.float32)


def _nnz_per_row(M) -> float:
    if sp.issparse(M):
        return float(M.nnz) / max(M.shape[0], 1)
    return float(M.shape[1])


# =================================================================================================
# PART 1 -- ADDRESSING
# =================================================================================================
def addressing_unit(mat: np.ndarray, Q: np.ndarray, qidx: np.ndarray, keep: np.ndarray,
                    D: int, a_w: float, a_r, binary: bool, seed: int,
                    n_boot: int, boot_seed: int) -> Dict:
    """Does the cue's top-scoring anchor IN KEY SPACE equal the anchor it was written from?"""
    KEY = code_matrix(mat, D, a_w, binary, seed)
    ar = a_w if a_r == "sym" else float(a_r)
    CUE = code_matrix(Q, D, ar, binary, seed)
    S = pair(KEY, CUE)                                            # [n_anchors, n_items]
    top = np.argmax(S, axis=0)
    ok = np.asarray(keep, dtype=bool)
    hit = (top[ok] == qidx[ok]).astype(np.float64)
    del S
    # a size-matched RANDOM key per anchor: same D, same active fraction, carrying no structure of
    # the value it addresses. Must sit at chance.
    rngn = np.random.default_rng(seed + 7717)
    RKraw = rngn.standard_normal((mat.shape[0], D), dtype=np.float32)
    RK = l2n(RKraw) if (a_w >= 1.0 and not binary) else rownorm_csr(
        sparsify(RKraw, a_w, binary))
    Sn = pair(RK, CUE)
    hit_n = (np.argmax(Sn, axis=0)[ok] == qidx[ok]).astype(np.float64)
    rb = np.random.default_rng(boot_seed)
    n = hit.size
    IB = rb.integers(0, n, size=(int(n_boot), n))
    b = hit[IB].mean(axis=1)
    bn = hit_n[IB].mean(axis=1)
    d = b - bn
    nnz_key = _nnz_per_row(KEY)
    nnz_cue = _nnz_per_row(CUE)
    return {"D": int(D), "a_write": float(a_w), "a_read": (a_r if a_r == "sym" else float(a_r)),
            "binary_code": bool(binary), "proj_seed": int(seed), "n_items": int(n),
            "active_units_per_key": round(nnz_key, 1), "active_units_per_cue": round(nnz_cue, 1),
            "ADDRESSING_ACCURACY": round(float(hit.mean()), 4),
            "ci95": [round(float(np.percentile(b, 2.5)), 4),
                     round(float(np.percentile(b, 97.5)), 4)],
            "N1_RANDOM_ADDRESS_control": round(float(hit_n.mean()), 4),
            "MARGIN_vs_random_address": {
                "point": round(float(d.mean()), 4),
                "ci95": [round(float(np.percentile(d, 2.5)), 4),
                         round(float(np.percentile(d, 97.5)), 4)],
                "band": ("ABOVE" if float(np.percentile(d, 2.5)) > 0 else
                         ("BELOW" if float(np.percentile(d, 97.5)) < 0 else "NOT_SEPARATED"))},
            "chance_1_over_n_anchors": round(1.0 / mat.shape[0], 8)}


# =================================================================================================
# PART 2 -- the read-out, with the full floor battery
# =================================================================================================
def score_readout(name: str, E: np.ndarray, GOLD: np.ndarray, keepm: np.ndarray,
                  arms: Dict[str, np.ndarray], chance: float, floors: Sequence[str],
                  n_boot: int, seed: int) -> Dict:
    per: Dict[str, Dict] = {}
    scored_all = None
    for k, S in arms.items():
        h = hit_at_1_both_tie_conventions(S, E, GOLD)
        sc = h["scored"] & keepm
        per[k] = {"hit_exp": h["hit_exp"], "hit_opt": h["hit_opt"], "hit_cons": h["hit_cons"],
                  "tie": h["tie_mass"], "scored": sc}
        scored_all = sc.copy() if scored_all is None else (scored_all & sc)
    idx = np.flatnonzero(scored_all)
    nc = int(idx.size)
    if nc < 50:
        return {"n_common_scored": nc, "UNREADABLE": "fewer than 50 commonly scored items"}
    rng = np.random.default_rng(seed)
    IDX = rng.integers(0, nc, size=(int(n_boot), nc))
    boot = {c: {k: per[k][c][idx][IDX].mean(axis=1) for k in arms}
            for c in ("hit_exp", "hit_opt", "hit_cons")}
    del IDX
    acc = {c: {k: round(float(per[k][c][idx].mean()), 4) for k in arms}
           for c in ("hit_exp", "hit_opt", "hit_cons")}
    ci = {k: [round(float(np.percentile(boot["hit_exp"][k], 2.5)), 4),
              round(float(np.percentile(boot["hit_exp"][k], 97.5)), 4)] for k in arms}

    def mrg(conv: str, a: str, b: str) -> Dict:
        d = boot[conv][a] - boot[conv][b]
        lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
        return {"point": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}

    A = acc["hit_exp"]
    present = [f for f in floors if f in A]
    binding = max(present, key=lambda f: A[f]) if present else None
    ka = A.get("K1_ORACLE_ADDRESS", float("nan"))
    nul = A.get("N1_RANDOM_ADDRESS", float("nan"))
    out = {"n_common_scored": nc, "chance_for_THIS_condition": round(float(chance), 6),
           "n_boot": int(n_boot),
           "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED (expected hit under a random tie-break)",
           "VALIDITY": {"KNOWN_ANSWER_K1_ORACLE_ADDRESS": ka, "gate": KA_CEILING_MIN,
                        "KA_PASSES": bool(ka >= KA_CEILING_MIN),
                        "NULL_N1_RANDOM_ADDRESS": nul, "chance": round(float(chance), 6),
                        "NULL_near_chance": bool(abs(nul - chance) < max(0.02, 0.5 * chance)),
                        "CONDITION_READABLE": bool(ka >= KA_CEILING_MIN)},
           "hit_at_1_TIE_CORRECTED_primary": A,
           "hit_at_1_OPTIMISTIC_tie": acc["hit_opt"],
           "hit_at_1_CONSERVATIVE_tie": acc["hit_cons"],
           "ci95_tie_corrected": ci, "BINDING_FLOOR": binding,
           "BINDING_FLOOR_VALUE_tie_corrected": (A[binding] if binding else None),
           "FLOOR_VALUES_on_THIS_population": {f: A[f] for f in present}}
    if binding:
        for conv, lab in (("hit_exp", "TIE_CORRECTED"), ("hit_cons", "CONSERVATIVE"),
                          ("hit_opt", "OPTIMISTIC")):
            out["MARGIN_vs_binding_floor_" + lab] = {k: mrg(conv, k, binding)
                                                     for k in arms if k != binding}
    a0 = "A0_FLAT_incumbent"
    if a0 in arms:
        out["LADDER_vs_A0_FLAT_tie_corrected"] = {k: mrg("hit_exp", k, a0)
                                                  for k in arms if k != a0}
    if "T1_SPARSE_KEY_DENSE_VALUE" in arms and "C1_SPARSE_BOTH" in arms:
        out["KEY_VS_VALUE_DECIDER_T1_minus_C1"] = mrg("hit_exp", "T1_SPARSE_KEY_DENSE_VALUE",
                                                      "C1_SPARSE_BOTH")
    if "T2_REGIME_SWITCH_asym" in arms and "T1_SPARSE_KEY_DENSE_VALUE" in arms:
        out["REGIME_SWITCH_DECIDER_T2_minus_T1"] = mrg("hit_exp", "T2_REGIME_SWITCH_asym",
                                                       "T1_SPARSE_KEY_DENSE_VALUE")
    print("[%s] n=%d KA=%.4f NULL=%.4f chance=%.4f binding=%s :: " % (
        name, nc, ka, nul, chance, binding)
        + " ".join("%s=%.4f" % (k[:24], v) for k, v in A.items()), flush=True)
    return out


# =================================================================================================
# self-test -- ASSERT VALUES
# =================================================================================================
def self_test() -> Dict:
    res: Dict = {}
    rng = np.random.default_rng(9)

    # S1 -- sparsify keeps EXACTLY the requested number of units and they are the largest by
    # magnitude. A sparsifier that silently keeps more is the whole cell's confound.
    X = rng.standard_normal((50, 400)).astype(np.float32)
    for f in (0.002, 0.01, 0.05, 0.20, 1.0):
        M = sparsify(X, f)
        k = 400 if f >= 1.0 else max(1, int(round(f * 400)))
        nz = np.diff(M.indptr)
        assert np.all(nz == k), "sparsify kept %r units, expected %d at frac %g" % (
            sorted(set(nz.tolist())), k, f)
        if f < 1.0:
            r0 = M.getrow(0).toarray().ravel()
            kept = np.flatnonzero(r0)
            thr = np.sort(np.abs(X[0]))[::-1][k - 1]
            assert np.all(np.abs(X[0][kept]) >= thr - 1e-6), "sparsify did not keep the top-k"
    res["S1_sparsifier_exact_k_and_top_by_magnitude"] = True

    # S2 -- a BINARY code really discards the graded value, and a SIGNED one really keeps it.
    Mb = sparsify(X, 0.05, binary=True)
    assert set(np.unique(Mb.data).tolist()) <= {-1.0, 1.0}, "binary code is not binary"
    Ms = sparsify(X, 0.05, binary=False)
    assert len(np.unique(Ms.data)) > 10, "signed code collapsed to a few values"
    res["S2_binary_vs_signed_codes_differ"] = True

    # S3 -- expansion at D == d is the IDENTITY, so the D=256 rung is genuinely the incumbent and
    # any lift at 2048 cannot be an artefact of the projection being applied at all.
    assert np.array_equal(expand(X, 400, 3), X), "expand at D==d is not the identity"
    res["S3_expand_identity_at_D_equals_d"] = True

    # S4 -- rownorm_csr makes a sparse dot an exact cosine, checked against a dense cosine.
    A = sparsify(X[:10], 0.25)
    An = rownorm_csr(A)
    Ad = A.toarray()
    G = (An @ An.T).toarray()
    Gd = l2n(Ad) @ l2n(Ad).T
    assert np.allclose(G, Gd, atol=1e-5), "sparse dot is not the dense cosine"
    res["S4_sparse_dot_is_a_cosine"] = True

    # S4b -- the DENSE fast path at frac=1.0 gives the SAME scores as the sparse path. If it did
    # not, the incumbent rung would be a different arm wearing the same label.
    Xa, Xb = X[:20], X[20:40]
    dens = pair(code_matrix(Xa, 400, 1.0, False, 5), code_matrix(Xb, 400, 1.0, False, 5))
    spar = pair(rownorm_csr(sparsify(expand(Xa, 400, 5), 1.0)),
                rownorm_csr(sparsify(expand(Xb, 400, 5), 1.0)))
    assert np.allclose(dens, spar, atol=1e-5), "the dense frac=1.0 path disagrees with the sparse one"
    res["S4b_dense_path_equals_sparse_path_at_frac_1"] = True

    # S5 -- ADDRESSING: an EXACT-KEY cue must address at ~1.0 (known answer) and a RANDOM key must
    # sit at chance (null), and they FAIL INDEPENDENTLY.
    n_a, d = 600, 64
    mat = rng.standard_normal((n_a, d)).astype(np.float32)
    qidx = np.arange(n_a, dtype=np.int64)
    keep = np.ones(n_a, dtype=bool)
    u = addressing_unit(mat, mat, qidx, keep, 512, 0.05, "sym", False, 1, 800, 2)
    assert u["ADDRESSING_ACCURACY"] > 0.99, "exact-key addressing is not at ceiling: %r" % u
    assert u["N1_RANDOM_ADDRESS_control"] < 0.02, "random-address null is not at chance: %r" % u
    # break the KNOWN ANSWER only: an unrelated cue. The null must be unmoved.
    bad = rng.standard_normal((n_a, d)).astype(np.float32)
    u2 = addressing_unit(mat, bad, qidx, keep, 512, 0.05, "sym", False, 1, 800, 2)
    assert u2["ADDRESSING_ACCURACY"] < 0.02, "breaking the cue did not break addressing: %r" % u2
    assert u2["N1_RANDOM_ADDRESS_control"] < 0.02, "breaking the cue moved the null"
    res["S5_addressing_validity_independent"] = {
        "exact_key": u["ADDRESSING_ACCURACY"], "random_address_null": u["N1_RANDOM_ADDRESS_control"],
        "broken_cue": u2["ADDRESSING_ACCURACY"]}

    # S6 -- the read-out scorer: K1 at ceiling, N1 at chance, broken independently.
    n_i = 700
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    g = rng.integers(0, n_a, size=n_i)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    keepm = np.ones(n_i, dtype=bool)
    plant = np.zeros((n_a, n_i), dtype=np.float32)
    plant[g, np.arange(n_i)] = 1.0
    arms = {"A0_FLAT_incumbent": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "F4_CONSTANT_PROTOTYPE_zero_query_information": as_constant_matrix(
                np.linspace(1, 0, n_a).astype(np.float32), n_i),
            "K1_ORACLE_ADDRESS": plant,
            "N1_RANDOM_ADDRESS": rng.standard_normal((n_a, n_i)).astype(np.float32)}
    r = score_readout("S6", E, GOLD, keepm, arms, 1.0 / n_a,
                      ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 1200, 4)
    assert r["VALIDITY"]["KA_PASSES"] and r["VALIDITY"]["NULL_near_chance"]
    b = dict(arms)
    b["K1_ORACLE_ADDRESS"] = arms["N1_RANDOM_ADDRESS"]
    r2 = score_readout("S6b", E, GOLD, keepm, b, 1.0 / n_a,
                       ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 1200, 4)
    assert not r2["VALIDITY"]["KA_PASSES"] and r2["VALIDITY"]["NULL_near_chance"]
    b2 = dict(arms)
    b2["N1_RANDOM_ADDRESS"] = plant
    r3 = score_readout("S6c", E, GOLD, keepm, b2, 1.0 / n_a,
                       ["F4_CONSTANT_PROTOTYPE_zero_query_information"], 1200, 4)
    assert r3["VALIDITY"]["KA_PASSES"] and not r3["VALIDITY"]["NULL_near_chance"]
    res["S6_readout_validity_independent"] = "DEMONSTRATED both ways"

    # S7 -- CODE_VERSION separates smoke from full.
    assert unit_key("P1", CODE_VERSION, "smoke", "x") != unit_key("P1", CODE_VERSION, "full", "x")
    res["S7_checkpoint_key_separates_grids"] = True
    print("[selftest] PASS " + json.dumps(res)[:900], flush=True)
    return res


# =================================================================================================
# main
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    smoke = (grid == "smoke")
    out_dir = OUT_DIR_SMOKE if smoke else OUT_DIR_FULL
    os.makedirs(out_dir, exist_ok=True)
    done = completed_units(out_dir)

    import experiments.exp_task_degeneracy_v1 as DEG
    rep: Dict = {"anchor_name": ANCHOR_NAME, "CODE_VERSION": CODE_VERSION, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "pid": os.getpid(), "RULER_MODE_GATE": DEG.ruler_mode_gate(),
                 "cache": DEG.build_cache_if_missing(), "NO_LLM_IN_FLOW": True,
                 "REGIME_PER_ORGAN": {
                     "VALUE_meaning_store": "DENSE d=256 graded, never sparsified, returned by LINK",
                     "ADDRESS_WRITE_key_dentate_like": "EXPANDED then SPARSE; expansion and active "
                                                       "fraction both SWEPT",
                     "ADDRESS_READ_cue_perforant_like": "DENSER than the key; a_read swept "
                                                        "INDEPENDENTLY of a_write",
                     "REGIME_SWITCH": "a_write != a_read IS the switch; a_write == a_read is the "
                                      "incumbent's single operating point for both write and read"}}
    C = DEG.load_cache()
    aux = DEG.load_aux(C)
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    pos = {a: i for i, a in enumerate(anchors)}
    qidx = np.array([pos.get(w, -1) for w in C["L_words"]], dtype=np.int64)
    keep_addr = keep & (qidx >= 0)
    print("[load] n_anchors=%d n_items=%d keep_addr=%d %.0fs"
          % (n_anchors, n_items, int(keep_addr.sum()), time.time() - t0), flush=True)

    d_keys = (256, 2048) if smoke else D_KEYS
    a_writes = (0.01, 0.20) if smoke else A_WRITE
    a_reads = ("sym", 1.00) if smoke else A_READ
    n_boot = 2000 if smoke else 10000

    # ============================ PART 1 -- ADDRESSING ========================================
    for regime, Q in (("EXACT_KEY", C["Q_exact"]), ("PARTIAL_CUE", C["Q_part"])):
        for D in d_keys:
            for a_w in a_writes:
                for a_r in a_reads:
                    for binary in ((False,) if (D != D_REF or a_r != "sym" or smoke)
                                   else (False, True)):
                        seeds = (PROJ_SEEDS if (D == D_REF and a_r == "sym" and not binary
                                                and not smoke) else (0,))
                        for s in seeds:
                            k = unit_key("P1", CODE_VERSION, grid, regime, str(D), str(a_w),
                                         str(a_r), "bin" if binary else "sgn", str(s))
                            if k in done:
                                continue
                            u = addressing_unit(mat, Q, qidx, keep_addr, D, a_w, a_r, binary,
                                                MASTER_SEED + 1000 * s, n_boot, MASTER_SEED + 3)
                            u["regime"] = regime
                            record_unit(out_dir, k, u)
                            print("[P1] %s D=%d a_w=%s a_r=%s %s s=%d addr=%.4f rand=%.4f %.0fs"
                                  % (regime, D, a_w, a_r, "bin" if binary else "sgn", s,
                                     u["ADDRESSING_ACCURACY"], u["N1_RANDOM_ADDRESS_control"],
                                     time.time() - t0), flush=True)

    units = load_units(out_dir)
    p1 = {k: v for k, v in units.items() if k.startswith("P1|")}

    # BETWEEN-PROJECTION-DRAW SD, reported beside the item bootstrap CI.
    draws: Dict[str, List[float]] = {}
    for k, v in p1.items():
        if v.get("D") == D_REF and v.get("a_read") == "sym" and not v.get("binary_code"):
            tag = "%s|D%d|aw%g" % (v["regime"], v["D"], v["a_write"])
            draws.setdefault(tag, []).append(float(v["ADDRESSING_ACCURACY"]))
    rep["BETWEEN_PROJECTION_DRAW_SD"] = {
        t: {"n_draws": len(x), "mean": round(float(np.mean(x)), 4),
            "sd": round(float(np.std(x, ddof=1)), 5) if len(x) > 1 else None,
            "values": [round(y, 4) for y in sorted(x)]}
        for t, x in sorted(draws.items())}
    rep["NOTE_ON_IMPORTED_NUMBERS"] = (
        "exp_cue_to_store_translation_v1 measured 1.0000 exact / 0.0325 partial at expand-dim 2048 "
        "/ sparsity 0.02 on n=1997 with 41 active units. THAT IS A DIFFERENT POPULATION AND IS NOT "
        "USED AS A COMPARISON HERE. Every number in this cell is computed on this cell's own "
        "population (n=%d addressable items) and the incumbent D=256 rung is measured, not quoted."
        % int(keep_addr.sum()))

    # pick the best addressing config on the PARTIAL CUE -- the operating point -- for PART 2.
    best = None
    for k, v in p1.items():
        if v.get("regime") != "PARTIAL_CUE":
            continue
        if best is None or v["ADDRESSING_ACCURACY"] > best["ADDRESSING_ACCURACY"]:
            best = v
    rep["BEST_ADDRESSING_CONFIG_partial_cue"] = best
    # and the best ASYMMETRIC one (a_read != a_write) -- the REGIME SWITCH arm.
    best_asym = None
    for k, v in p1.items():
        if v.get("regime") != "PARTIAL_CUE" or v.get("a_read") == "sym":
            continue
        if best_asym is None or v["ADDRESSING_ACCURACY"] > best_asym["ADDRESSING_ACCURACY"]:
            best_asym = v
    rep["BEST_ASYMMETRIC_REGIME_SWITCH_CONFIG"] = best_asym

    # ============================ PART 2 -- READ-OUT ==========================================
    GOLD = np.zeros((n_anchors, n_items), dtype=bool)
    E_A = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if not keep[i]:
            continue
        E_A[:, i] = mat_ok
        if len(C["excl"][i]):
            E_A[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD[gi, i] = True
    GOLD &= E_A
    keep_A = keep & GOLD.any(axis=0)
    gold_lists = [np.flatnonzero(GOLD[:, i]) for i in range(n_items)]
    f5 = constant_prototype_floor(mat, mat_ok)
    r5 = np.random.default_rng(MASTER_SEED + 5)
    designated = np.full(n_items, -1, dtype=np.int64)
    for i in np.flatnonzero(keep_A):
        gi = gold_lists[i]
        if gi.size:
            designated[i] = int(gi[r5.integers(0, gi.size)])

    n_elig_A = E_A.sum(axis=0)
    chance_open = float(np.mean(GOLD[:, keep_A].sum(axis=0) / np.maximum(n_elig_A[keep_A], 1)))
    pools: Dict[str, Dict] = {"P1_OPEN": {"E": E_A, "keep": keep_A, "chance": chance_open}}
    orc_open = oracle_constant_scores(n_anchors, gold_lists, None)
    h_orc = hit_at_1_both_tie_conventions(as_constant_matrix(orc_open, n_items), E_A, GOLD)
    pools["P1_OPEN"]["POOL_ORACLE_CHECK"] = {
        "ok": None, "oracle_constant_hit_exp": round(float(h_orc["hit_exp"][keep_A].mean()), 4),
        "chance": round(chance_open, 6),
        "note": "an OPEN pool is not de-biased by construction; the admission is reported."}
    for K in (K_LIST[:1] if smoke else K_LIST):
        cand, _gc = balanced_candidate_sets(designated, gold_lists, C["excl"], keep_A, K,
                                            MASTER_SEED + 17 + K)
        ok = cand[:, 0] >= 0
        E_B = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
        E_B[rows.ravel(), cols.ravel()] = True
        assert int((E_B & GOLD).sum(axis=0)[ok].max()) == 1
        pools["P2_BALANCED_K%d" % K] = {
            "E": E_B, "keep": ok, "chance": 1.0 / (K + 1), "K": K, "cand": cand,
            "POOL_ORACLE_CHECK": pool_admits_a_winning_constant(cand, gold_lists, n_anchors, K)}
    rep["POOLS"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("E", "keep", "cand")}
                    for k, v in pools.items()}

    FLOORS = ["F1_TRIGRAM_orthographic", "F2_PREFIX_orthographic", "F3_FREQUENCY_constant",
              "F4_CONSTANT_PROTOTYPE_zero_query_information",
              "F5_SCRAMBLE_NULL_anchor_map_permuted"]

    def key_scores(Q: np.ndarray, D: int, a_w: float, a_r, binary: bool, s: int) -> np.ndarray:
        sd = MASTER_SEED + 1000 * s
        ar = a_w if a_r == "sym" else float(a_r)
        return pair(code_matrix(mat, D, a_w, binary, sd), code_matrix(Q, D, ar, binary, sd))

    for regime, Q in (("PARTIAL_CUE", C["Q_part"]), ("EXACT_KEY", C["Q_exact"])):
        if smoke and regime == "EXACT_KEY":
            continue
        for pname, P in pools.items():
            k = unit_key("P2", CODE_VERSION, grid, regime, pname)
            if k in done:
                continue
            arms: Dict[str, np.ndarray] = {}
            arms["F1_TRIGRAM_orthographic"] = (aux["t_mat"] @ aux["Tq"].T).astype(np.float32)
            arms["F2_PREFIX_orthographic"] = aux["Pq"].T.astype(np.float32)
            arms["F3_FREQUENCY_constant"] = col(
                frequency_floor(np.expm1(aux["fq"].astype(np.float64))))
            arms["F4_CONSTANT_PROTOTYPE_zero_query_information"] = col(f5)
            arms["F5_SCRAMBLE_NULL_anchor_map_permuted"] = (
                l2n(scramble_null(mat, MASTER_SEED)) @ l2n(Q).T).astype(np.float32)
            arms["A0_FLAT_incumbent"] = (l2n(mat) @ l2n(Q).T).astype(np.float32)
            if best is not None:
                arms["T1_SPARSE_KEY_DENSE_VALUE"] = key_scores(
                    Q, int(best["D"]), float(best["a_write"]), best["a_read"],
                    bool(best["binary_code"]), int(best["proj_seed"]))
            if best_asym is not None:
                arms["T2_REGIME_SWITCH_asym"] = key_scores(
                    Q, int(best_asym["D"]), float(best_asym["a_write"]), best_asym["a_read"],
                    bool(best_asym["binary_code"]), int(best_asym["proj_seed"]))
            # C1: sparsify the VALUE TOO -- the thing we already did, as the control that isolates
            # WHICH OBJECT the sparsification belongs to.
            aw = float(best["a_write"]) if best is not None else 0.05
            arms["C1_SPARSE_BOTH"] = pair(code_matrix(mat, mat.shape[1], aw, False, 0),
                                          code_matrix(Q, Q.shape[1], aw, False, 0))
            # K1_ORACLE_ADDRESS: hand the correct address; LINK returns the value -> must be ~1.0.
            Sk = np.zeros((n_anchors, n_items), dtype=np.float32)
            okd = designated >= 0
            Sk[designated[okd], np.flatnonzero(okd)] = 1.0
            arms["K1_ORACLE_ADDRESS"] = Sk
            rr = np.random.default_rng(MASTER_SEED + 909)
            Sn = np.zeros((n_anchors, n_items), dtype=np.float32)
            Sn[rr.integers(0, n_anchors, size=n_items), np.arange(n_items)] = 1.0
            arms["N1_RANDOM_ADDRESS"] = Sn
            u = score_readout("%s|%s" % (regime, pname), P["E"], GOLD, P["keep"], arms,
                              P["chance"], FLOORS, n_boot, MASTER_SEED + 101)
            u["regime"] = regime
            u["pool"] = pname
            u["POOL_ORACLE_CHECK"] = P["POOL_ORACLE_CHECK"]
            u["T1_config"] = best
            u["T2_config"] = best_asym
            record_unit(out_dir, k, u)
            del arms

    units = load_units(out_dir)
    rep["PART_1_ADDRESSING"] = {k: v for k, v in units.items() if k.startswith("P1|")}
    rep["PART_2_READOUT"] = {k: v for k, v in units.items() if k.startswith("P2|")}
    rep["n_units"] = len(units)
    rep["elapsed_s"] = round(time.time() - t0, 1)
    rep["verdict"] = "COMPUTED"
    rep["verdict_msg"] = "see PART_1_ADDRESSING / PART_2_READOUT; gates are per condition"
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("[done] %s units=%d %.0fs" % (out_dir, len(units), time.time() - t0), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "smoke"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    run(a.grid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
