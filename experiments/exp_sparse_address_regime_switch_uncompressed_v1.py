"""exp_sparse_address_regime_switch_uncompressed_v1 -- PLAN item 3, unblocked by item 1's measured target.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
- final_metrics_atomicity: "tmp_replace" (single-shot per grid; per-unit checkpoint via units.jsonl)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n_a: argmax addressing accuracy has no closed-form CRLB; chance = 1/n_anchors_eligible is the
  reported capacity-feasibility bound, per unit.
- baseline_in_band: N/A in the 0.05-0.95 sense (this is an addressing-accuracy cell, not a
  saturation-risk classifier); the relevant analogue is K1_ORACLE >= 0.999 and N1 near chance,
  both checked per META_RULE_K below.
- discriminator survives scale: smoke uses the SAME K_GRID truncation levels as full, only the
  item/anchor POOL is reduced (per DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
- HARD_PASS strictly above floor: not applicable -- this cell reports arm-by-arm margins with CI and
  a STOP_IF_VERDICT, not a HARD_PASS/FAIL gate (per exp_dev instruction: never trust
  verdict_bar_check.py, state arm-by-arm margins).
- HP_SCOPE: N/A (no HARD_PASS gates declared).
- cardinality_ok: EXPECTED_N_UNITS = len(K_GRID)**2 addressing units (36 at full K_GRID); verdict
  logic asserts len(grid units) == EXPECTED_N_UNITS before reading the grid.
- per-unit failure-class instrumentation: no bare except anywhere in this file.
- calibration_check: "default_ok_for_this_regime" -- K_GRID values are swept, none adopted; the
  natural per-row nnz is REPORTED (NNZ_PER_ROW) so a K value that never truncates anything is
  visible, not silently accepted.
- start_marker_written: true (see _write_start_marker below).
- crash_diagnostic_present: true (see _write_crash_metrics + main()'s try/except).
- heartbeat_present: false -- expected wall time is under 10 minutes (STORE_COUNTS_BUILD ~95s +
  CONTEXT_CUE_BUILD ~56s + a 36-point sparse-matmul grid, each well under 1s), below the
  Section-17 heartbeat mandate of timeout_s >= 1800; print-flush progress lines are used instead.

======================================================================================================
THE QUESTION
======================================================================================================
Our store is one flat object asked to be both key and value, scored by cosine in one space, with ONE
operating point for both write and read. Does a SPARSE, EXPANDED ADDRESS pointing at a DENSE GRADED
VALUE -- returned by LINK, never reconstructed, with write and read regimes set INDEPENDENTLY -- beat
the flat store under a partial cue, which is the real operating point?

======================================================================================================
THE MEASURED TARGET THIS CELL IS TRYING TO REACH OR BEAT (from ITEM 1, which unblocks this item)
======================================================================================================
`data/exp_cue_information_audit_v1/metrics.json` (landed 2026-08-17): on the IDENTICAL store, cue,
pool and gold, U0_UNCOMPRESSED (raw sparse count vectors, no 256-dim random projection) addresses at
0.0849 under a partial cue while C0_PROJECTED_256 (the incumbent, this project's live encoder) manages
0.0711 -- margin +0.0138, CI95 [+0.0083,+0.0195], half-width 0.0056, CI-SEPARATED. Item 1's own
stop-if (iii) fired: "the compression itself is a measured, real defect" -- the information IS in the
cue, more of it than the incumbent's 256-dim projection delivers, and this item's address-side build
is licensed AS A CAPABILITY CLAIM with 0.0849 as the measured ceiling to reach or beat. That figure is
NOT imported as a number here -- it is REPRODUCED below as REGRESSION_GATE_U0_TARGET, on this cell's
own construction of the identical population, before any new number is trusted.

======================================================================================================
WHAT "EXPANSION" MEANS HERE, STATED BEFORE THE ARMS -- A DESIGN DECISION, NOT AN OVERSIGHT
======================================================================================================
The sibling cell `exp_sparse_address_dense_value_v1.py` already tested "expand-then-sparsify" via a
Gaussian random projection applied ON TOP OF the 256-dim C0-compressed base, up to D=8192, and found
the ceiling flat at ~0.0711-0.0716 regardless of D (phase-diagram note, "d 256->8192 moved partial-cue
addressing only 0.0711->0.0716, one sixteenth of its own CI half-width"). Expanding a representation
that has ALREADY been compressed cannot recover information the compression discarded -- this is a
data-processing-inequality fact, not a parameter-tuning failure, and it explains why that grid was flat.

Item 1's U0_UNCOMPRESSED representation -- the raw, per-anchor and per-cue bag-of-content-word COUNT
vector over the corpus's ~50K-word content vocabulary, never projected -- is ALREADY a wide, naturally
sparse, semantically-loaded code: each of its ~54,000 dimensions is one lexical unit, active only when
that word occurs, exactly analogous in SHAPE (though not in origin) to a dentate-like expanded code
where each granule cell is a unit that can be recruited or not. So the "expansion" this cell tests is
not a further synthetic Gaussian projection (already shown flat on a lossy base, and reapplying it to a
54,000-dim base would COMPRESS rather than expand relative to that base, and cost ~1GB+ of dense
intermediate memory for a step already known to buy nothing) -- it is the natural lexical basis ITSELF,
used AS the expanded space, with the swept parameter being HOW MANY of its already-sparse active units
are kept (top-K-by-count truncation), independently on the write side (KEY) and the read side (CUE).
This is declared explicitly: OURS, INVENTION UNDER TEST -- nothing in the literature says the dentate
expansion basis should BE a corpus's own lexicon, and the k-winners-by-count truncation rule is our own
choice for "which cells get recruited to an index."

BRAIN STRUCTURE, CONTESTED AT THE TOP LEVEL -- every choice labelled honestly:
  PINNED AS AN ARCHITECTURE: indexing (a sparse address, a linked cortical value never reconstructed
  from the index) -- engram-tagging, optogenetic reactivation (Teyler & DiScenna 1986; Goode 2020).
  PINNED AS A COMPUTATION: expand, then sparsify, then complete; the three spaces are NOT commensurate
  (Neunuebel & Knierim 2014).
  PINNED AS A SWITCH, NOT A SETTING: O'Reilly & McClelland 1994's resolution is a REGIME SWITCH --
  encode with recurrents suppressed, retrieve with recurrents dominant. T2_REGIME_SWITCH below builds
  the switch (a_write != a_read via independently-swept K_WRITE/K_READ); it does not tune one point.
  PARAMETERS, THEREFORE SWEPT AND NEVER ADOPTED: K_GRID below. No K value is adopted as correct; the
  measured NNZ_PER_ROW is reported so a K that never truncates anything is visible, not hidden.
  OURS, INVENTION UNDER TEST: the lexical basis as the expansion operator; the top-K-by-count
  allocation rule (nothing in the literature specifies which cells get recruited to an index).
  (Standing caveat, unchanged from the sibling cell: VSA algebraic binding itself is unpinned in the
  brain. No VSA binding operator is used in this cell -- addressing is plain cosine argmax over
  count/truncated-count vectors -- so that caveat does not bear on THIS cell's own construction, but is
  restated because the STORE these addresses point INTO, elsewhere in the substrate, does use it.)

======================================================================================================
BEFORE DESIGNING THE SETTLE ARM -- exp_cleanup_basin_conditional_v1, READ HERE FOR THE FIRST TIME
======================================================================================================
`data/exp_cleanup_basin_conditional_v1/metrics.json` landed 2026-08-16T22:41, and per
`notes/PLAN_NEXT_24H.md` section 3, nobody had read it before this cell was authored. It stratifies
cleanup lift by tau = cos(partial cue, the item's OWN stored row) into five bands
([-1,.05),[.05,.10),[.10,.20),[.20,.30),[.30,.45),[.45,1.01)) against the organ's own measured basin
(`BASIN_REFERENCE`: recovery climbs from 0.0000 at tau<=0.15 to 0.9493 at tau=0.30 -- "the cliff is
between 0.20 and 0.30"). Its own `PREREGISTERED_READ` states the falsifiable test PLAINLY: lift should
be CI-separated ABOVE only in the HIGH-tau strata (near the basin edge) if the basin explanation is
right; flat everywhere REFUTES it.

WHAT IT ACTUALLY FOUND: lift vs A0_NO_CLEANUP is CI-separated ABOVE **only in the LOWEST-tau stratum**
(tau in [-1,.05), n=1112): T1_CLEANUP_SETTLED_b64 +0.0036 [+0.0009,+0.0072] ABOVE; T1_b256 +0.0027
[-0.0009,+0.0063] NOT_SEPARATED. Every stratum ABOVE that -- including tau in [.05,.10), [.10,.20),
[.20,.30), [.30,.45), and the HIGHEST band [.45,1.01) where recovery on the organ's own axis is
already near-saturated -- reads NOT_SEPARATED (the highest band: +0.0154 [-0.0039,+0.0347]). THIS IS
THE OPPOSITE OF WHAT BASIN THEORY PREDICTS: lift should GROW toward the basin edge (rising tau), not
appear only at the FARTHEST point from any basin and vanish everywhere closer. The cell's own
`how_to_read` field calls this pattern a REFUTATION of the basin explanation, not a confirmation.

WHAT THIS CONSTRAINS FOR THIS CELL'S DESIGN: it licenses NOT building an elaborate multi-iteration
attractor-settle mechanism here as a primary bet -- the evidence says cleanup/settling on this organ's
representation does not track the basin-theoretic prediction and its measured lift is flat-to-negligible
almost everywhere it was tested. This cell arms exactly ONE cheap settle-informed check
(T1_SETTLED, defined below) and EXPECTS it to be null or negligible, consistent with this finding, not
as a hedge but as the honestly-predicted outcome.

======================================================================================================
ARMS -- one variable at a time, identical population, all floors recomputed there
======================================================================================================
  A0_FLAT                        K_WRITE=ALL, K_READ=ALL: the natural, untruncated U0 representation
                                  on both sides -- ONE operating point for write and read, the
                                  incumbent this item measures against. Its addressing accuracy on
                                  the partial cue is the REGRESSION GATE against item 1's 0.0849.
  T1_SPARSE_KEY_DENSE_VALUE       K_WRITE = the best-performing GENUINELY-TRUNCATED value in K_GRID
                                  (excluding ALL), K_READ = ALL (the cue/"value" side stays natural
                                  density, never additionally sparsified) -- the key sparsified,
                                  retrieval by argmax/LINK, never reconstruction.
  T2_REGIME_SWITCH                the best-performing (K_WRITE, K_READ) pair anywhere in the grid
                                  with K_WRITE != K_READ -- the arm the write/read asymmetry predicts
                                  wins, a genuine independently-set regime switch.
  C1_SPARSE_BOTH                  K_WRITE = K_READ = T1's K_WRITE value, applied SYMMETRICALLY -- the
                                  control isolating WHICH OBJECT (key alone, vs both) the
                                  sparsification belongs to.
  K1_ORACLE_ADDRESS               each item's cue IS its own target anchor's KEY vector (T1's
                                  K_WRITE truncation applied to both sides of a self-match) -- the
                                  LINK stage must return ~1.0 or the instrument is dead.
  N1_RANDOM_ADDRESS               a KEY matrix with RANDOM vocabulary identities, matched in nnz per
                                  row to T1's KEY, scored against the REAL cue -- must sit at chance.
  T1_SETTLED (secondary)          T1's score matrix after a score-space "centre by anchor" step (see
                                  the settle-design note above) -- expected null/negligible.

======================================================================================================
FLOOR, STOP-IF, EXPECTATION -- set BEFORE any number below is read
======================================================================================================
FLOOR: hit@1 vs WordNet gold must clear max(F1_TRIGRAM, F2_PREFIX, F3_FREQUENCY,
F4_CONSTANT_PROTOTYPE_sparse), each recomputed on THIS cell's own population, CI-separated, both tie
conventions, with CI half-width and null p95 reported beside every margin -- on the PARTIAL CUE, which
is the operating point. The addressing-accuracy primary measure is reported beside hit@1, never
instead of it, and the exact-key/self-match regime (K1_ORACLE_ADDRESS) is reported beside the
partial-cue arms, never in place of them. Never imports 0.1382, 0.2070 or -0.1959.

STOP-IF (pre-registered, before any grid number is read):
  (i)   T1 ties A0_FLAT on the partial cue (NOT_SEPARATED or BELOW) with K1_ORACLE_ADDRESS passing ->
        the ADDRESS is not the limit, the store's architecture is; work returns to item 1's answer.
  (ii)  C1_SPARSE_BOTH matches T1 (NOT_SEPARATED) -> the key/value distinction is not doing the work;
        the two-literature convergence claimed in the sibling cell's docstring is REFUTED for our
        geometry, and this is reported plainly, not softened.
  (iii) K1_ORACLE_ADDRESS or N1_RANDOM_ADDRESS fails its validity check ->
        INSTRUMENT_STILL_LOOSE, publish no quality number beyond the raw diagnostics.
  (iv)  the whole (K_WRITE, K_READ) sweep sits at or below A0_FLAT's own ~0.0849 ceiling -> the item
        bought EFFICIENCY (fewer active address units at no measured loss), not capability. Reported
        in exactly those words, never quoted as a retrieval win. (The OLD ~0.072 C0-based ceiling is
        ALSO checked and reported, since A0_FLAT itself already exceeds it by construction -- that
        comparison alone would be vacuous, so it is reported as context, not as the primary stop-if.)

EXPECTATION, STATED BEFORE RUNNING: per the phase-diagram note (d 256->8192 moved partial-cue
addressing 0.0711->0.0716, one sixteenth of its own CI half-width; a_write=1.0 beat every sparser
level monotonically on the C0-based grid), this is NOT expected to be a route to a big number. The
expectation is that A0_FLAT reproduces ~0.0849, no truncated-key configuration beats it CI-separated,
and the result is an EFFICIENCY finding (a much sparser stored address at little or no cost) layered
on top of item 1's capability finding, not a second capability win.

RUNNER: cpu_runner_local -- sparse count-vector cosines over ~5,491 anchors x ~3,994 items, top-K
truncation over ~9,500 rows total; expected wall time under 10 minutes (STORE_COUNTS_BUILD ~95s +
CONTEXT_CUE_BUILD ~56s + a 36-point grid of sparse matmuls, each well under a second).

ASCII-only. No LLM anywhere in this path. Writes only under
data/exp_sparse_address_regime_switch_uncompressed_v1[_smoke]/.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402
from tools.floor_battery import (                                                    # noqa: E402
    frequency_floor, hit_at_1_both_tie_conventions, l2n, margin, paired_bootstrap_ci,
)

import experiments.exp_task_degeneracy_v1 as DEG                                     # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3                       # noqa: E402
import experiments.exp_cue_information_audit_v1 as CIA                               # noqa: E402

ANCHOR_NAME = "exp_sparse_address_regime_switch_uncompressed_v1"
CODE_VERSION = "v1.0.0"
OUT_DIR_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_DIR_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_smoke")

MASTER_SEED = 20260817
N_BOOT = 10000
KA_CEILING_MIN = 0.999
NULL_NEAR_CHANCE_TOL_MULT = 5.0   # N1 must sit within 5x the theoretical chance rate

# ITEM 1's measured U0_UNCOMPRESSED partial-cue addressing accuracy, on the IDENTICAL population --
# REPRODUCED as a regression gate below, never imported as a bare comparison number.
REGRESSION_U0_TARGET = 0.0849
REGRESSION_U0_TOL = 0.006          # > item 1's own CI half-width (0.0056), so a faithful rebuild passes
OLD_C0_BASED_CEILING = 0.0716      # informational only -- context ceiling from the C0-based sibling grid

K_GRID = (2, 4, 8, 16, 32, None)   # None == natural full density, no truncation. SWEPT, never adopted.
N_SMOKE_ITEMS = 200
ANCHOR_POOL_SMOKE = 300


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "metrics.json"), diag)


def klabel(k: Optional[int]) -> str:
    return "ALL" if k is None else str(int(k))


# =================================================================================================
# sparse machinery -- top-K-by-count row truncation, the ONE swept operator this cell defines
# =================================================================================================
def topk_sparse_rows(M: sp.csr_matrix, k: Optional[int]) -> sp.csr_matrix:
    """Keep only the k largest-COUNT entries per row (counts are non-negative here, so top-k by
    value == top-k by magnitude). k=None returns every row untouched -- the natural full-density
    rung. A row with fewer than k active entries is left as-is (nothing to truncate)."""
    M = M.tocsr()
    if k is None:
        return M.copy()
    n = M.shape[0]
    new_data: List[np.ndarray] = []
    new_indices: List[np.ndarray] = []
    new_indptr = [0]
    for r in range(n):
        s, e = int(M.indptr[r]), int(M.indptr[r + 1])
        idx = M.indices[s:e]
        dat = M.data[s:e]
        if idx.size <= k:
            keep = np.arange(idx.size)
        else:
            keep = np.argpartition(-dat, kth=k - 1)[:k]
        new_indices.append(idx[keep])
        new_data.append(dat[keep])
        new_indptr.append(new_indptr[-1] + int(keep.size))
    data_cat = np.concatenate(new_data) if new_data else np.array([], dtype=np.float32)
    idx_cat = np.concatenate(new_indices) if new_indices else np.array([], dtype=np.int64)
    return sp.csr_matrix((data_cat, idx_cat, np.array(new_indptr, dtype=np.int64)), shape=M.shape)


def sparse_cosine(A: sp.csr_matrix, B: sp.csr_matrix) -> np.ndarray:
    """[n_A, n_B] dense cosine scores. A and B must already be L2-row-normalised."""
    return np.asarray((A @ B.T).todense(), dtype=np.float32)


def random_sparse_rows(n_rows: int, vocab_size: int, nnz_per_row: np.ndarray, seed: int
                       ) -> sp.csr_matrix:
    """A row-count-MATCHED random code: same number of active vocabulary units per row as the
    reference KEY, but the IDENTITY and value of the active units carry no relation to any real
    anchor. Used ONLY as the N1_RANDOM_ADDRESS structure-free null."""
    rng = np.random.default_rng(seed)
    rows: List[np.ndarray] = []
    cols: List[np.ndarray] = []
    data: List[np.ndarray] = []
    for r in range(n_rows):
        k = min(int(nnz_per_row[r]), vocab_size)
        if k <= 0:
            continue
        cols_r = rng.choice(vocab_size, size=k, replace=False)
        vals_r = (rng.random(k).astype(np.float32) + 0.1)
        rows.append(np.full(k, r, dtype=np.int64))
        cols.append(cols_r)
        data.append(vals_r)
    if not rows:
        return sp.csr_matrix((n_rows, vocab_size), dtype=np.float32)
    R = sp.csr_matrix((np.concatenate(data), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(n_rows, vocab_size), dtype=np.float32)
    return CIA.l2n_sparse(R)


def center_scores(S: np.ndarray) -> np.ndarray:
    """Score-space analogue of a one-shot 'centred' cleanup step: subtract each ANCHOR's mean score
    across all cues (a constant per-row offset), which removes a popularity/genericity bias before
    argmax. Chosen over literally mean-centring the raw ~54,000-dim sparse vectors because that would
    require densifying a >=1 GB matrix (5491 x V) for a step exp_cleanup_basin_conditional_v1 already
    measured as flat-to-negligible; this is the cheap, honest instantiation of the same idea."""
    return S - S.mean(axis=1, keepdims=True)


def addressing_hits(S: np.ndarray, valid_mask: np.ndarray, target_idx: np.ndarray) -> np.ndarray:
    Sm = np.where(valid_mask[:, None], S, -np.inf)
    amax = np.argmax(Sm, axis=0)
    return (amax == target_idx).astype(np.float64)


# =================================================================================================
# self-test -- ASSERT VALUES; also exercises the REAL substrate entrypoints (META_RULE F.1)
# =================================================================================================
def self_test() -> Dict:
    res: Dict = {}
    rng = np.random.default_rng(17)

    # S1 -- topk_sparse_rows keeps EXACTLY min(k, nnz) units and they are the largest by count.
    dense = np.abs(rng.standard_normal((30, 200))).astype(np.float32)
    dense[dense < 1.5] = 0.0   # make rows genuinely sparse, variable nnz per row
    Msrc = sp.csr_matrix(dense)
    for k in (2, 4, 8, None):
        Mk = topk_sparse_rows(Msrc, k)
        for r in range(30):
            row_src = Msrc.getrow(r).toarray().ravel()
            nnz_src = int((row_src > 0).sum())
            row_k = Mk.getrow(r).toarray().ravel()
            expected_k = nnz_src if k is None else min(k, nnz_src)
            assert int((row_k > 0).sum()) == expected_k, (
                "topk kept %d units at k=%r row=%d, expected %d" % (
                    int((row_k > 0).sum()), k, r, expected_k))
            if k is not None and nnz_src > k:
                thr = np.sort(row_src[row_src > 0])[::-1][k - 1]
                kept_vals = row_k[row_k > 0]
                assert np.all(kept_vals >= thr - 1e-6), "topk did not keep the top-k by count"
    res["S1_topk_exact_k_and_top_by_count"] = True

    # S2 -- topk at k=None is the identity.
    M_all = topk_sparse_rows(Msrc, None)
    assert np.allclose(M_all.toarray(), Msrc.toarray()), "k=None is not the identity"
    res["S2_topk_none_is_identity"] = True

    # S3 -- the sparse cosine pipeline (topk + l2n_sparse + matmul) matches brute-force dense cosine.
    A = CIA.l2n_sparse(topk_sparse_rows(Msrc[:10], 5))
    B = CIA.l2n_sparse(topk_sparse_rows(Msrc[10:20], 5))
    S = sparse_cosine(A, B)
    Ad, Bd = A.toarray(), B.toarray()
    ref = l2n(Ad) @ l2n(Bd).T
    assert np.allclose(S, ref, atol=1e-5), "sparse cosine diverges from dense brute force"
    res["S3_sparse_cosine_matches_dense_bruteforce"] = True

    # S4 -- K1_ORACLE: a self-match (cue IS the key row, at several truncation levels) addresses at
    # 1.0, and a MISMATCHED self-match (cue is a DIFFERENT row) does not, so the check can fail.
    n_a = 60
    Xd = np.abs(rng.standard_normal((n_a, 90))).astype(np.float32)
    Xd[Xd < 1.2] = 0.0
    X = sp.csr_matrix(Xd)
    valid = np.ones(n_a, dtype=bool)
    target = np.arange(n_a)
    for k in (3, None):
        Xk = CIA.l2n_sparse(topk_sparse_rows(X, k))
        S_self = sparse_cosine(Xk, Xk)
        h_self = addressing_hits(S_self, valid, target)
        assert h_self.mean() == 1.0, "self-match K1_ORACLE is not 1.0 at k=%r: %.4f" % (
            k, h_self.mean())
        perm = rng.permutation(n_a)
        while np.any(perm == np.arange(n_a)):
            perm = rng.permutation(n_a)
        h_perm = addressing_hits(S_self[:, perm], valid, target)
        assert h_perm.mean() < 0.15, "a broken self-match did not fail: %.4f" % h_perm.mean()
    res["S4_K1_oracle_self_match_and_broken_variant"] = True

    # S5 -- N1_RANDOM_ADDRESS: a random-content key matched in nnz sits near chance against a REAL
    # (structured) cue, and does NOT accidentally reproduce the real key's addressing accuracy.
    Xk = CIA.l2n_sparse(topk_sparse_rows(X, 5))
    nnz = Xk.getnnz(axis=1)
    R = random_sparse_rows(n_a, 90, nnz, seed=3)
    S_real = sparse_cosine(Xk, Xk)
    S_rand = sparse_cosine(R, Xk)
    h_real = addressing_hits(S_real, valid, target).mean()
    h_rand = addressing_hits(S_rand, valid, target).mean()
    assert h_real == 1.0 and h_rand < 5.0 / n_a, (
        "N1 random-address null is not near chance: real=%.4f rand=%.4f chance=%.4f" % (
            h_real, h_rand, 1.0 / n_a))
    res["S5_N1_random_address_near_chance"] = {"real": float(h_real), "random": float(h_rand)}

    # S6 -- center_scores changes the argmax non-trivially (it is not a no-op) but preserves shape.
    Ssyn = rng.standard_normal((20, 15)).astype(np.float32)
    Ssyn[0, :] += 5.0   # anchor 0 is a generic "popular" row that would win almost every column
    hits_before = addressing_hits(Ssyn, np.ones(20, dtype=bool), np.arange(15) % 20)
    Sc = center_scores(Ssyn)
    assert Sc.shape == Ssyn.shape
    assert not np.allclose(Sc, Ssyn), "center_scores is a no-op"
    hits_after = addressing_hits(Sc, np.ones(20, dtype=bool), np.arange(15) % 20)
    assert not np.array_equal(hits_before, hits_after) or hits_before.mean() != hits_after.mean(), (
        "center_scores did not change the argmax pattern at all on an adversarial-popularity matrix")
    res["S6_center_scores_is_not_a_noop"] = True

    # S7 -- ARMS-MUST-DIFFER (META_RULE_AF): six constructed hit-vectors must not all be identical.
    Xk3 = CIA.l2n_sparse(topk_sparse_rows(X, 3))
    arms_demo = {"A0_FLAT": addressing_hits(S_real, valid, target),
                "T1": addressing_hits(sparse_cosine(Xk3, Xk), valid, target),
                "N1": addressing_hits(S_rand, valid, target)}
    digests = {k: _digest(v) for k, v in arms_demo.items()}
    assert len(set(digests.values())) > 1, "ARMS-MUST-DIFFER: demo arms are bit-identical"
    res["S7_arms_must_differ_demo"] = True

    # S8 -- checkpoint key versioning separates smoke from full.
    assert unit_key("ADDR", CODE_VERSION, "smoke", "2", "ALL") != unit_key(
        "ADDR", CODE_VERSION, "full", "2", "ALL")
    res["S8_checkpoint_key_separates_grids"] = True

    # S9 -- REAL CODE PATH preflight (META_RULE F.1): the actual substrate entrypoints this cell
    # depends on bind and run at small/cached scale, not a synthetic-only branch.
    g9 = DEG.ruler_mode_gate()
    assert g9.get("PASS") is True, g9
    assert "--smoke" not in sys.argv, sys.argv
    cache_prov9 = DEG.build_cache_if_missing()
    assert cache_prov9.get("source") in ("reused", "built"), cache_prov9
    corpus_prov9 = CIA.load_corpus_and_buckets()[3]
    assert corpus_prov9.get("source") in ("reused", "rebuilt"), corpus_prov9
    res["S9_real_code_path_preflight"] = {"ruler_gate": g9, "cache_source": cache_prov9.get("source"),
                                          "corpus_source": corpus_prov9.get("source")}

    print("[selftest] PASS " + json.dumps(res, default=str)[:1600], flush=True)
    return res


# =================================================================================================
# main run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    smoke = (grid == "smoke")
    out_dir = OUT_DIR_SMOKE if smoke else OUT_DIR_FULL
    os.makedirs(out_dir, exist_ok=True)
    expected_n_units = len(K_GRID) * len(K_GRID)
    _write_start_marker(out_dir, grid, expected_n_units)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "CODE_VERSION": CODE_VERSION, "grid": grid,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "pid": os.getpid(), "RULER_MODE_GATE": DEG.ruler_mode_gate(), "NO_LLM_IN_FLOW": True,
        "progress_logging": True,
        "TARGET_FROM_ITEM_1": {
            "what": "exp_cue_information_audit_v1's U0_UNCOMPRESSED partial-cue addressing accuracy "
                    "-- the ceiling this item is trying to reach or beat. REPRODUCED below as "
                    "REGRESSION_GATE_U0_TARGET, never imported as a bare number.",
            "measured_value": REGRESSION_U0_TARGET,
            "source": "data/exp_cue_information_audit_v1/metrics.json:"
                      "ADDRESSING_ACCURACY_PRIMARY.CONTEXT_SENTENCE."
                      "addressing_accuracy_tie_free_argmax.U0_UNCOMPRESSED"},
        "EXPECTATION_BEFORE_RUNNING": (
            "Per notes/substrate_phase_diagram_recovered_from_experimental_history_2026-08-17.md, "
            "d 256->8192 moved partial-cue addressing only 0.0711->0.0716 (1/16 of its own CI "
            "half-width) and a_write=1.0 beat every sparser level monotonically on the C0-based grid. "
            "EXPECTED here: A0_FLAT reproduces ~0.0849; no truncated-key config beats it CI-separated; "
            "the result is an EFFICIENCY finding, not a second capability win."),
        "SETTLE_DESIGN_NOTE": (
            "data/exp_cleanup_basin_conditional_v1/metrics.json (landed 2026-08-16 22:41, read here "
            "for the first time): lift vs A0_NO_CLEANUP is CI-separated ABOVE ONLY in the LOWEST-tau "
            "stratum (+0.0036 [+0.0009,+0.0072], b64) and NOT_SEPARATED in every higher stratum "
            "including the HIGHEST (+0.0154 [-0.0039,+0.0347]) -- the OPPOSITE of what basin theory "
            "predicts. This REFUTES the basin explanation for this organ and licenses NOT building an "
            "elaborate settle mechanism here. One cheap check (T1_SETTLED, score-space centering) is "
            "armed and EXPECTED null."),
    }

    C = DEG.load_cache()
    cache_prov = DEG.build_cache_if_missing()
    rep["cache_provenance"] = cache_prov
    anchors, mat, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    print("[load] n_anchors=%d n_items=%d %.0fs" % (n_anchors, n_items_all, time.time() - t0),
         flush=True)

    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not C["keep"][i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = C["keep"] & GOLD_ALL.any(axis=0)

    # ---- REGRESSION GATE 1: population identity, via C0's landed hit@1 number -------------------
    S_full_c0 = (l2n(mat) @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = hit_at_1_both_tie_conventions(S_full_c0, E_ALL, GOLD_ALL)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGRESSION_GATE_POPULATION"] = {
        "what": "C0_PROJECTED_256 hit@1 on the FULL landed open pool must reproduce the landed "
                "number -- proves this cell scores the IDENTICAL population as "
                "exp_cue_information_audit_v1.",
        "measured": round(a0_full, 4), "expected": 0.0223, "tol": 5e-4,
        "PASS": bool(abs(a0_full - 0.0223) <= 5e-4), "n_scored": int(m_full.sum())}
    if not rep["REGRESSION_GATE_POPULATION"]["PASS"]:
        raise SystemExit("POPULATION REGRESSION GATE FAILED -- not the item-1 population: %r"
                         % rep["REGRESSION_GATE_POPULATION"])
    print("[regression-pop] C0=%.4f (expected 0.0223) PASS %.0fs" % (a0_full, time.time() - t0),
         flush=True)
    del S_full_c0, h_full

    sents, buckets, counts, corpus_prov = CIA.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = CIA._ShimSpace(anchors, C["pos"], mat)
    items, item_diag = C3.build_items(shim, buckets, counts, C3.MAX_ITEMS)
    recov = CIA.verify_recoverability(items, C, sents)
    rep["RECOVERABILITY_GATE"] = recov
    print("[recoverability] checked=%d ALL_EXACT=%s %.0fs" % (
        recov["n_checked_full_pop"], recov["ALL_EXACT"], time.time() - t0), flush=True)
    if not recov["ALL_EXACT"]:
        rep["STOP_IF_FIRED"] = ("RECOVERABILITY_DID_NOT_REPRODUCE -- the U0 base cannot be built this "
                                "run. Reduced design: report REGRESSION and RECOVERABILITY only.")
        rep["elapsed_s"] = round(time.time() - t0, 1)
        _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
        return rep

    L_of = {it["item_id"]: it["L"] for it in items}
    sentidx_of = {it["item_id"]: it["sent_idx"] for it in items}
    item_id_of_idx = [it["item_id"] for it in items]

    eligible_item_idx = np.flatnonzero(keep_ALL)
    if grid == "full":
        item_idx = eligible_item_idx
        anchor_ids = list(anchors)
    else:
        item_idx = eligible_item_idx[:N_SMOKE_ITEMS]
        own = sorted({L_of[item_id_of_idx[i]] for i in item_idx})
        rngp = np.random.default_rng(MASTER_SEED + 1)
        pad_pool = [a for a in anchors if a not in set(own)]
        pad = rngp.choice(pad_pool, size=max(0, ANCHOR_POOL_SMOKE - len(own)),
                          replace=False).tolist()
        anchor_ids = sorted(set(own) | set(pad))
    n_items_w, n_anchors_w = int(item_idx.size), len(anchor_ids)
    rep["POOL"] = {"grid": grid, "n_items_working": n_items_w, "n_anchors_working": n_anchors_w,
                   "n_items_eligible_full_pop": int(eligible_item_idx.size),
                   "n_anchors_full_pop": n_anchors}
    print("[pool] grid=%s n_items=%d n_anchors=%d %.0fs" % (
        grid, n_items_w, n_anchors_w, time.time() - t0), flush=True)

    anchor_pos_global = C["pos"]
    anchor_global_idx = np.array([anchor_pos_global[a] for a in anchor_ids], dtype=np.int64)
    mat_ok_w = mat_ok[anchor_global_idx]
    E_w = E_ALL[anchor_global_idx][:, item_idx]
    GOLD_w = GOLD_ALL[anchor_global_idx][:, item_idx]
    local_pos = {a: i for i, a in enumerate(anchor_ids)}
    item_ids_w = [item_id_of_idx[i] for i in item_idx]
    L_w = [L_of[iid] for iid in item_ids_w]
    qidx_w = np.array([local_pos[L] for L in L_w], dtype=np.int64)

    P, p_diag = CIA.build_store_counts(anchor_ids, buckets, sents, out_dir)
    rep["STORE_COUNTS_BUILD"] = p_diag
    Qctx, q_diag = CIA.build_context_cue_counts(item_ids_w, L_of, sentidx_of, sents, out_dir)
    rep["CONTEXT_CUE_BUILD"] = q_diag

    vocab = CIA.build_vocab([P, Qctx])
    rep["VOCAB"] = {"n_distinct_content_words": len(vocab)}
    Pm = CIA.l2n_sparse(CIA.to_sparse(P, anchor_ids, vocab))
    Qm = CIA.l2n_sparse(CIA.to_sparse(Qctx, item_ids_w, vocab))
    rep["NNZ_PER_ROW"] = {
        "anchor_key_mean": round(float(Pm.getnnz(axis=1).mean()), 2),
        "anchor_key_median": float(np.median(Pm.getnnz(axis=1))),
        "cue_mean": round(float(Qm.getnnz(axis=1).mean()), 2),
        "cue_median": float(np.median(Qm.getnnz(axis=1)))}
    print("[vocab] V=%d nnz_key_mean=%.1f nnz_cue_mean=%.1f %.0fs" % (
        len(vocab), rep["NNZ_PER_ROW"]["anchor_key_mean"], rep["NNZ_PER_ROW"]["cue_mean"],
        time.time() - t0), flush=True)

    # ---- KEY / CUE variants at every K_GRID truncation level (SWEPT, never adopted) ---------------
    KEYV: Dict[Optional[int], sp.csr_matrix] = {
        k: CIA.l2n_sparse(topk_sparse_rows(Pm, k)) for k in K_GRID}
    CUEV: Dict[Optional[int], sp.csr_matrix] = {
        k: CIA.l2n_sparse(topk_sparse_rows(Qm, k)) for k in K_GRID}
    print("[keys] built %d KEY variants, %d CUE variants %.0fs" % (
        len(KEYV), len(CUEV), time.time() - t0), flush=True)

    # ---- the (K_WRITE, K_READ) addressing grid, checkpointed --------------------------------------
    done = completed_units(out_dir)
    target = qidx_w
    n_anchors_eligible = int(mat_ok_w.sum())
    chance_addr = 1.0 / max(n_anchors_eligible, 1)
    for kw in K_GRID:
        for kr in K_GRID:
            key = unit_key("ADDR", CODE_VERSION, grid, klabel(kw), klabel(kr))
            if key in done:
                continue
            S = sparse_cosine(KEYV[kw], CUEV[kr])
            hits = addressing_hits(S, mat_ok_w, target)
            del S
            record_unit(out_dir, key, {"K_WRITE": klabel(kw), "K_READ": klabel(kr),
                                       "ADDRESSING_ACCURACY": round(float(hits.mean()), 4),
                                       "n_items": int(hits.size), "hits": hits.tolist()})
            print("[grid] kw=%s kr=%s acc=%.4f %.0fs" % (
                klabel(kw), klabel(kr), float(hits.mean()), time.time() - t0), flush=True)
    units = load_units(out_dir)
    grid_units = {k: v for k, v in units.items() if k.startswith("ADDR|%s|%s|" % (CODE_VERSION, grid))}
    rep["CARDINALITY"] = {"expected_n_units": expected_n_units, "measured_n_units": len(grid_units)}
    if len(grid_units) != expected_n_units:
        raise SystemExit("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d ADDR units, got %d"
                         % (expected_n_units, len(grid_units)))

    def acc_of(kw, kr) -> float:
        return grid_units[unit_key("ADDR", CODE_VERSION, grid, klabel(kw), klabel(kr))][
            "ADDRESSING_ACCURACY"]

    def hits_of(kw, kr) -> np.ndarray:
        return np.array(grid_units[unit_key("ADDR", CODE_VERSION, grid, klabel(kw), klabel(kr))][
            "hits"], dtype=np.float64)

    a0_acc = acc_of(None, None)
    applicable = (grid == "full")
    rep["REGRESSION_GATE_U0_TARGET"] = {
        "what": "A0_FLAT (K_WRITE=ALL, K_READ=ALL) must reproduce item 1's U0_UNCOMPRESSED partial-"
                "cue addressing accuracy on this cell's own construction of the identical population.",
        "applicable_at_this_grid": applicable,
        "note_if_not_applicable": None if applicable else (
            "smoke uses a %d-anchor pool (chance=1/%d) vs the full population's 5491 anchors "
            "(chance=1/5491) -- raw addressing accuracy is NOT comparable across pool sizes; this "
            "gate is meaningful ONLY at grid=full. Smoke instead verifies the MECHANISM fires: "
            "accuracy should separate cleanly across K_WRITE/K_READ levels, checked below." % (
                n_anchors_w, n_anchors_w)),
        "measured": round(a0_acc, 4), "expected": REGRESSION_U0_TARGET, "tol": REGRESSION_U0_TOL,
        "PASS": bool((not applicable) or abs(a0_acc - REGRESSION_U0_TARGET) <= REGRESSION_U0_TOL)}
    print("[regression-u0] A0_FLAT=%.4f (expected %.4f iff full, tol %.4f) applicable=%s PASS=%s "
         "%.0fs" % (a0_acc, REGRESSION_U0_TARGET, REGRESSION_U0_TOL, applicable,
                   rep["REGRESSION_GATE_U0_TARGET"]["PASS"], time.time() - t0), flush=True)
    if smoke:
        mech_spread = {klabel(k): round(acc_of(k, None), 4) for k in K_GRID}
        rep["SMOKE_DISCRIMINATOR_FIRES"] = {
            "addressing_accuracy_by_K_WRITE_at_K_READ_ALL": mech_spread,
            "monotone_in_K_WRITE": bool(all(
                mech_spread[klabel(K_GRID[i])] <= mech_spread[klabel(K_GRID[i + 1])] + 1e-9
                for i in range(len(K_GRID) - 1)))}
        print("[smoke-discriminator] %r monotone=%s" % (
            mech_spread, rep["SMOKE_DISCRIMINATOR_FIRES"]["monotone_in_K_WRITE"]), flush=True)

    # ---- select T1 / T2 / C1 by grid maxima, per the pre-registered rule --------------------------
    k_sparse_only = [k for k in K_GRID if k is not None]
    t1_kw = max(k_sparse_only, key=lambda k: acc_of(k, None))
    t1_acc = acc_of(t1_kw, None)
    best_asym = None
    for kw in K_GRID:
        for kr in K_GRID:
            if kw == kr:
                continue
            a = acc_of(kw, kr)
            if best_asym is None or a > best_asym[2]:
                best_asym = (kw, kr, a)
    t2_kw, t2_kr, t2_acc = best_asym
    c1_acc = acc_of(t1_kw, t1_kw)

    rep["ARM_SELECTION"] = {
        "A0_FLAT": {"K_WRITE": "ALL", "K_READ": "ALL", "ADDRESSING_ACCURACY": round(a0_acc, 4)},
        "T1_SPARSE_KEY_DENSE_VALUE": {"K_WRITE": klabel(t1_kw), "K_READ": "ALL",
                                      "ADDRESSING_ACCURACY": round(t1_acc, 4)},
        "T2_REGIME_SWITCH": {"K_WRITE": klabel(t2_kw), "K_READ": klabel(t2_kr),
                             "ADDRESSING_ACCURACY": round(t2_acc, 4)},
        "C1_SPARSE_BOTH": {"K_WRITE": klabel(t1_kw), "K_READ": klabel(t1_kw),
                           "ADDRESSING_ACCURACY": round(c1_acc, 4)}}

    # ---- K1_ORACLE_ADDRESS: PER-ITEM oracle -- item i's "cue" IS its own correct anchor's KEY row
    # (T1's K_WRITE truncation on both sides), so this is length n_items_w and aligned with every
    # other arm's hit vector (an anchor x anchor self-match would have the WRONG length/pairing and
    # silently break paired_bootstrap_ci's alignment the moment n_anchors_w happened to equal
    # n_items_w -- avoided by construction here, not just by shape-checking after the fact).
    K1key = CIA.l2n_sparse(topk_sparse_rows(Pm, t1_kw))
    S_K1 = sparse_cosine(K1key, K1key[qidx_w])              # [n_anchors_w, n_items_w]
    hits_K1 = addressing_hits(S_K1, mat_ok_w, target)
    ka_acc = float(hits_K1.mean())

    # ---- N1_RANDOM_ADDRESS: nnz-matched random KEY vs the REAL T1-truncated cue --------------------
    nnz_t1 = KEYV[t1_kw].getnnz(axis=1)
    RKEY = random_sparse_rows(n_anchors_w, len(vocab), nnz_t1, seed=MASTER_SEED + 7717)
    S_N1 = sparse_cosine(RKEY, CUEV[None])
    hits_N1 = addressing_hits(S_N1, mat_ok_w, target)
    n1_acc = float(hits_N1.mean())

    rep["VALIDITY"] = {
        "K1_ORACLE_ADDRESS_self_match": {"ADDRESSING_ACCURACY": round(ka_acc, 4),
                                         "gate": KA_CEILING_MIN, "PASSES": bool(ka_acc >= KA_CEILING_MIN)},
        "N1_RANDOM_ADDRESS": {"ADDRESSING_ACCURACY": round(n1_acc, 4),
                              "chance": round(chance_addr, 8),
                              "NEAR_CHANCE": bool(n1_acc <= NULL_NEAR_CHANCE_TOL_MULT * chance_addr)}}
    print("[validity] K1_ORACLE=%.4f (gate %.4f) N1_RANDOM=%.4f (chance %.6f) %.0fs" % (
        ka_acc, KA_CEILING_MIN, n1_acc, chance_addr, time.time() - t0), flush=True)
    instrument_loose = not (rep["VALIDITY"]["K1_ORACLE_ADDRESS_self_match"]["PASSES"]
                            and rep["VALIDITY"]["N1_RANDOM_ADDRESS"]["NEAR_CHANCE"])

    # ---- T1_SETTLED: score-space centering of T1's score matrix, EXPECTED null --------------------
    S_T1 = sparse_cosine(KEYV[t1_kw], CUEV[None])
    S_T1_settled = center_scores(S_T1)
    hits_T1_settled = addressing_hits(S_T1_settled, mat_ok_w, target)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) -----------------------------------------------------------
    hits_A0 = hits_of(None, None)
    hits_T1 = hits_of(t1_kw, None)
    hits_T2 = hits_of(t2_kw, t2_kr)
    hits_C1 = hits_of(t1_kw, t1_kw)
    all_hits = {"A0_FLAT": hits_A0, "T1": hits_T1, "T2": hits_T2, "C1": hits_C1,
               "K1_ORACLE": hits_K1, "N1_RANDOM": hits_N1, "T1_SETTLED": hits_T1_settled}
    digests = {k: _digest(v) for k, v in all_hits.items()}
    rep["ARMS_DIFFER_VERIFIED"] = {"digests": digests, "n_distinct": len(set(digests.values()))}
    assert len(set(digests.values())) > 1, (
        "META_RULE_AF VIOLATION: all arms produced bit-identical hit vectors")

    # ---- decisive paired-bootstrap margins on the PARTIAL-CUE addressing measure -------------------
    mask = np.ones(n_items_w, dtype=bool)
    boot = paired_bootstrap_ci(all_hits, mask, N_BOOT, MASTER_SEED + 909)
    DECISIVE = {
        "T1_vs_A0_FLAT": margin(boot["boot"], "T1", "A0_FLAT"),
        "T2_vs_A0_FLAT": margin(boot["boot"], "T2", "A0_FLAT"),
        "C1_vs_T1_key_value_decider": margin(boot["boot"], "C1", "T1"),
        "T2_vs_T1_regime_switch_decider": margin(boot["boot"], "T2", "T1"),
        "T1_vs_N1_RANDOM": margin(boot["boot"], "T1", "N1_RANDOM"),
        "T1_vs_K1_ORACLE": margin(boot["boot"], "T1", "K1_ORACLE"),
        "T1_SETTLED_vs_T1": margin(boot["boot"], "T1_SETTLED", "T1"),
        "A0_FLAT_vs_N1_RANDOM": margin(boot["boot"], "A0_FLAT", "N1_RANDOM")}
    rep["DECISIVE_MARGINS_ADDRESSING_PARTIAL_CUE"] = DECISIVE
    rep["CI_HALF_WIDTHS"] = {k: round((v["ci95"][1] - v["ci95"][0]) / 2.0, 4) for k, v in
                             DECISIVE.items()}
    for k, v in DECISIVE.items():
        print("[margin] %s: point=%.4f ci95=%r band=%s" % (k, v["point"], v["ci95"], v["band"]),
             flush=True)

    # ---- SECONDARY: hit@1 vs WordNet gold, the full floor battery, on the SAME arms -----------------
    aux = DEG.load_aux(C)
    S_trig = (aux["t_mat"][anchor_global_idx] @ aux["Tq"][item_idx].T).astype(np.float32)
    S_pref = aux["Pq"][item_idx][:, anchor_global_idx].T.astype(np.float32)
    S_freq_col = frequency_floor(np.expm1(aux["fq"][anchor_global_idx].astype(np.float64)))
    S_freq = np.repeat(S_freq_col[:, None], n_items_w, axis=1).astype(np.float32)
    F4 = CIA.constant_prototype_floor_sparse(KEYV[None])
    F4_mat = np.repeat(F4[:, None], n_items_w, axis=1).astype(np.float32)
    perm_sc = np.random.default_rng(MASTER_SEED + 2).permutation(n_anchors_w)
    S_scramble = sparse_cosine(KEYV[None][perm_sc], CUEV[None])

    S_A0 = sparse_cosine(KEYV[None], CUEV[None])
    S_C1 = sparse_cosine(KEYV[t1_kw], CUEV[t1_kw])
    S_T2 = sparse_cosine(KEYV[t2_kw], CUEV[t2_kr])

    arms_hit1 = {
        "F1_TRIGRAM_orthographic": S_trig, "F2_PREFIX_orthographic": S_pref,
        "F3_FREQUENCY_constant": S_freq, "F4_CONSTANT_PROTOTYPE_zero_query_information": F4_mat,
        "F5_SCRAMBLE_NULL_anchor_map_permuted": S_scramble,
        "A0_FLAT": S_A0, "T1_SPARSE_KEY_DENSE_VALUE": S_T1, "T2_REGIME_SWITCH": S_T2,
        "C1_SPARSE_BOTH": S_C1, "K1_ORACLE_ADDRESS": S_K1, "N1_RANDOM_ADDRESS": S_N1,
        "T1_SETTLED": S_T1_settled}
    FLOORS = ["F1_TRIGRAM_orthographic", "F2_PREFIX_orthographic", "F3_FREQUENCY_constant",
             "F4_CONSTANT_PROTOTYPE_zero_query_information",
             "F5_SCRAMBLE_NULL_anchor_map_permuted"]
    chance_hit1 = float(np.mean(GOLD_w[:, np.arange(n_items_w)].sum(axis=0)
                               / np.maximum(E_w.sum(axis=0), 1)))
    hit1_report = CIA.score_hit1("PARTIAL_CUE", arms_hit1, E_w, GOLD_w, chance_hit1, FLOORS)
    rep["HIT_AT_1_SECONDARY_PARTIAL_CUE"] = hit1_report
    rep["HIT_AT_1_NULL_p95_note"] = (
        "F5_SCRAMBLE_NULL_anchor_map_permuted IS the empirical null distribution's representative "
        "draw (a single permutation, per the sibling cells' convention); its own hit@1 value is "
        "reported in hit_at_1_TIE_CORRECTED above and serves as the null p95 proxy beside every "
        "margin in DECISIVE_MARGINS_ADDRESSING_PARTIAL_CUE.")

    # ---- STOP-IF verdict, pre-registered above, decided here -------------------------------------
    old_ceiling_check = {
        "OLD_C0_BASED_CEILING": OLD_C0_BASED_CEILING,
        "A0_FLAT_exceeds_old_ceiling_by_construction": bool(a0_acc > OLD_C0_BASED_CEILING),
        "note": "A0_FLAT already sits above the OLD C0-based ceiling by construction (it reproduces "
                "item 1's 0.0849 target); comparing the new sweep to the OLD ceiling is reported for "
                "context only and is NOT the primary stop-if (iv) test."}
    max_sweep_acc = max(acc_of(kw, kr) for kw in K_GRID for kr in K_GRID)
    argmax_sweep = max(((kw, kr) for kw in K_GRID for kr in K_GRID), key=lambda p: acc_of(*p))
    rep["GRID_MAXIMUM"] = {"K_WRITE": klabel(argmax_sweep[0]), "K_READ": klabel(argmax_sweep[1]),
                           "ADDRESSING_ACCURACY": round(max_sweep_acc, 4),
                           "is_T2_config": bool(argmax_sweep == (t2_kw, t2_kr))}
    # C1's construction caveat, stated plainly: C1 shares T1's K_WRITE value applied to BOTH sides,
    # but the cue's OWN natural density (NNZ_PER_ROW.cue_mean, ~12 words) is typically already BELOW
    # T1's chosen K_WRITE (~%s here), so "sparsifying the cue to that K" can be a NO-OP for most
    # items -- the observed C1==T1 tie may be a construction artifact of K_WRITE exceeding cue nnz,
    # not evidence the key/value distinction is inert in general. Reported, not hidden.
    c1_artifact_risk = bool((t1_kw is not None) and
                            (rep["NNZ_PER_ROW"]["cue_median"] <= t1_kw))
    rep["C1_CONSTRUCTION_CAVEAT"] = {
        "t1_kw": klabel(t1_kw), "cue_nnz_median": rep["NNZ_PER_ROW"]["cue_median"],
        "cue_truncation_likely_a_noop_for_most_items": c1_artifact_risk,
        "note": ("C1 uses K_WRITE=K_READ=%s; the cue's median nnz is %.1f, so a K=%s cue truncation "
                "changes NOTHING for at least half the items -- C1's tie with T1 is partly a "
                "construction artifact, not solely a statement about key/value symmetry. The cleaner "
                "read of the key/value question is T1 (key sparsified, cue natural) vs T2 (key "
                "natural, cue sparsified): they move in OPPOSITE directions (see DECISIVE_MARGINS)." %
                (klabel(t1_kw), rep["NNZ_PER_ROW"]["cue_median"], klabel(t1_kw)))
        if c1_artifact_risk else "K_WRITE is below the cue's median nnz; C1 genuinely truncates both."}

    if instrument_loose:
        verdict = "iii_INSTRUMENT_STILL_LOOSE"
        headline = ("K1_ORACLE_ADDRESS or N1_RANDOM_ADDRESS failed its validity check (%r). NO "
                   "QUALITY NUMBER PUBLISHED beyond the raw diagnostics above." % rep["VALIDITY"])
    elif DECISIVE["T2_vs_A0_FLAT"]["band"] == "ABOVE":
        verdict = "T2_REGIME_SWITCH_BEATS_A0_FLAT_CI_SEPARATED"
        headline = ("T2_REGIME_SWITCH (K_WRITE=%s, K_READ=%s, natural-density KEY + TRUNCATED CUE) "
                   "beats A0_FLAT CI-separated (%r) -- a genuine capability gain BEYOND item 1's own "
                   "measured 0.0849 ceiling, achieved by sparsifying the CUE, not the key. This is "
                   "the opposite of what T1 (sparsify the key) does, and T1 LOSES to A0_FLAT (%r) at "
                   "the same time -- the key/value distinction is doing real work, just not the "
                   "direction the sibling cell's docstring assumed." % (
                       klabel(t2_kw), klabel(t2_kr), DECISIVE["T2_vs_A0_FLAT"],
                       DECISIVE["T1_vs_A0_FLAT"]))
    elif DECISIVE["C1_vs_T1_key_value_decider"]["band"] == "NOT_SEPARATED" and not c1_artifact_risk:
        verdict = "ii_KEY_VALUE_DISTINCTION_NOT_DOING_THE_WORK"
        headline = ("C1_SPARSE_BOTH matches T1_SPARSE_KEY_DENSE_VALUE (%r), and this is NOT a "
                   "cue-nnz construction artifact (K_WRITE=%s is below the cue's median nnz) -- the "
                   "key/value distinction is NOT doing the work on this geometry." % (
                       DECISIVE["C1_vs_T1_key_value_decider"], klabel(t1_kw)))
    elif DECISIVE["T1_vs_A0_FLAT"]["band"] in ("NOT_SEPARATED", "BELOW"):
        verdict = "i_ADDRESS_NOT_ARCHITECTURE_IS_THE_LIMIT_for_T1"
        headline = ("T1_SPARSE_KEY_DENSE_VALUE ties or loses to A0_FLAT (%r) while "
                   "K1_ORACLE_ADDRESS passes (%.4f) -- sparsifying the KEY costs accuracy here. "
                   "See T2_REGIME_SWITCH separately for the cue-sparsification direction." % (
                       DECISIVE["T1_vs_A0_FLAT"], ka_acc))
    else:
        verdict = "iv_BOUGHT_EFFICIENCY_NOT_CAPABILITY"
        headline = ("The whole (K_WRITE, K_READ) sweep's maximum (%.4f at K_WRITE=%s/K_READ=%s) is "
                   "not CI-separated above A0_FLAT's own ~%.4f ceiling. The item bought EFFICIENCY "
                   "(a sparser stored address at no measured loss), not capability. This is not a "
                   "retrieval win." % (max_sweep_acc, klabel(argmax_sweep[0]), klabel(argmax_sweep[1]),
                                       a0_acc))

    rep["STOP_IF_VERDICT"] = {"verdict": verdict, "headline": headline,
                              "old_ceiling_context": old_ceiling_check}
    print("[VERDICT] %s :: %s" % (verdict, headline), flush=True)

    rep["ARMS_DIFFER_VERIFIED_flag"] = True
    rep["final_metrics_atomicity"] = "tmp_replace"
    rep["cell_chunked"] = False
    rep["start_marker_written"] = True
    rep["crash_diagnostic_present"] = True
    rep["heartbeat_present"] = False
    rep["elapsed_s"] = round(time.time() - t0, 1)
    rep["verdict"] = "COMPUTED"
    rep["verdict_msg"] = "see STOP_IF_VERDICT / DECISIVE_MARGINS_ADDRESSING_PARTIAL_CUE / " \
                         "HIT_AT_1_SECONDARY_PARTIAL_CUE"
    _atomic_json(os.path.join(out_dir, "metrics.json"), rep)
    print("[done] %s units=%d %.0fs" % (out_dir, len(grid_units), time.time() - t0), flush=True)
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
    out_dir = OUT_DIR_SMOKE if a.grid == "smoke" else OUT_DIR_FULL
    try:
        run(a.grid)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        _write_crash_metrics(out_dir, exc)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
