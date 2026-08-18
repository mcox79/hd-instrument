"""exp_writerule_learned_basis_denominator_gate_v1 -- ORGAN A CODE GATE: does a LEARNED basis or a
WRITE-TIME DENOMINATOR move the RELATION, where the random projection moved nothing?

THE QUESTION (notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.7/6.9/6.10, and notes/drill_what_
cortex_computes_across_episodes_write_rule_equations_2026-08-18.md, read in full before this cell was
written, not re-derived here). The store is `H^T p_a` -- a Johnson-Lindenstrauss random rotation of
the raw word-context co-occurrence matrix `Sigma_yx`. JL is a near-isometry: it is PROVABLY incapable
of creating similarity structure that was not already present in what it was handed. Landed measurement
(data/exp_writerule_step_ladder_v1/metrics.json COMPOSITION_DELTA_TABLE, CODE_PROJECT row):
composition delta +0.0031 [-0.0243,+0.0300] NOT_SEPARATED -- CODE moves the relation not at all, exactly
as "preserves geometry" predicts. The drill's theory (Saxe/McClelland/Ganguli 2019, sec 5.2): the rule
that converts adjacency into substitutability is `Sigma_yx Sigma_xx^-1` -- the co-occurrence matrix
FACTORISED against the input correlation structure. We built `Sigma_yx` (= our raw count matrix) and
stopped; there is no factorisation and no `Sigma_xx^-1` term anywhere in the live write rule.

THIS CELL TESTS: does replacing the random basis H with a LEARNED one (closed-form equivalent of
Oja/Sanger, i.e. truncated SVD of the count matrix -- drill sec 9, candidate C1), or normalising the
write with a denominator (Carandini-Heeger divisive form / PPMI -- drill sec 9, candidate C2), move
the winner COMPOSITION (WordNet-relation rate, co-occurrence ratio) -- not merely the hit@1 score?

=================================================================================================
ARMS (one variable at a time, identical population/scorer/gold/cue regime throughout):
  A0_RANDOM_PROJECTION        the incumbent construction, self-row oracle-key cue (matches WR's own
                               R3/R4 construction: query = the arm's own row for the query's target
                               anchor). REGRESSION GATE against the OFFICIAL cached store (mat,
                               C["Q_part"]) must reproduce PIPE.REGRESSION_A0_PARTIAL or EXIT.
  C1_LEARNED_BASIS             truncated SVD of the raw anchor x context-word count matrix (the
                               drill's own stated closed-form equivalent of the online Oja/Sanger
                               update at its converged fixed point under the whitened-input limit --
                               "no new mathematics has to be written"). k SWEPT over
                               {64,128,256,512,1024,2048} -- BOTH below and above the incumbent's 256,
                               because the drill's point is that cortex EXPANDS where we compress.
                               Representation = U_k * sqrt(S_k) (same convention as the owned
                               hdlab/ppmi_sparse_encoder.py SVD step). The WINNING k (by hit@1 on the
                               cheap sweep) is the one carried into the full composition analysis --
                               this is the discriminating design the brief asks for: pick the winner
                               by accuracy, then ask whether ITS composition moved.
  C1_CTRL_MATCHED_RANK_RANDOM   a random Gaussian projection at the SAME rank as C1's winning k.
                               Must not help; if it matches C1, the win is dimensionality not learning.
  C1_CTRL_FREQUENCY_SHUFFLED    the SAME truncated-SVD pipeline run on a matrix that preserves each
                               anchor's total context mass and the corpus's word-frequency marginal
                               EXACTLY, drawn i.i.d. from the global frequency distribution --
                               destroying every anchor-specific co-occurrence signal while leaving
                               unigram frequency intact (drill: "a corpus shuffled ... so unigram
                               frequencies are exactly preserved and co-occurrence structure is
                               destroyed"). Must not help.
  C2_WRITE_TIME_DIVISIVE_NORM   Carandini-Heeger divisive normalisation over the CONTEXT-WORD pool,
                               `P~_aj = P_aj^n / (sigma^n + SUM_a' P_a'j^n)` (pool='col'), plus 'row'
                               and 'both' (='both' = full PPMI, reusing the exact PPMI formula and
                               context-distribution-smoothing convention already implemented in
                               hdlab/ppmi_sparse_encoder.py, credited not reimplemented from scratch).
                               sigma, n, pool all SWEPT, never adopted. The winning (sigma,n,pool) is
                               then projected through a random basis at k=256 (matching the incumbent
                               dimensionality) so C2 isolates the DENOMINATOR alone, holding the CODE
                               step's basis-learning question out of scope for this arm.
  C2_CTRL_WRONGPOOL             identical normalisation, denominator computed from a PERMUTED column
                               assignment (the exact control that caught the read-side divisive-norm
                               cell reproducing its effect from the wrong pool, sec 3.3 of the drill).
                               Must not help.
  C2_CTRL_PURE_IDF              divide by document frequency alone (no divisive form): separates "any
                               frequency suppression" from "this normalisation".
  K1_KNOWN_ANSWER / N1_NULL     oracle self-address (~1.0) on every named arm; derangement null on A0.
  ONLINE_SANGER_ETA_CONFIRMATION  a SEPARATE, explicitly scoped, small-scale (n_sub anchors, d_sub
                               top-frequency context words, k=16) streaming Sanger/GHA fit swept over
                               eta, reported as SUBSPACE ALIGNMENT to the SVD solution at the same
                               scale -- NOT part of the main retrieval sweep. Disclosed reason: running
                               the true online update at full scale for every k is not tractable in
                               this cell's time budget; the drill itself sanctions the closed-form
                               substitution for the PRIMARY result ("no new mathematics has to be
                               written") but the brief also says "sweep eta, never adopt a value" and
                               this satisfies that without silently dropping it.

THE PRIMARY MEASUREMENT IS WINNER COMPOSITION: for every named arm, the fraction of top-1 winners with
NO close WordNet relation to the query (REUSED, byte-identical construction and 0.25 threshold from
experiments.exp_writerule_step_ladder_v1.wordnet_relation_composition -- not reimplemented), and the
sentence-level Jaccard co-occurrence WINNER SHARE, GOLD SHARE, and the RATIO of their means (REUSED
from the same cell's syntagmatic_jaccard_composition), all reported together, per the standing rule
that quoting a share alone without the ratio produced a false causal story once already in this arc
(6.10's correction). hit@1 is reported beside composition, never instead of it.

FLOORS. All four (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE) recomputed on THIS
cell's own population via tools.floor_battery, both tie conventions, CI half-width and analytic null
half-width beside every margin. 0.1390/0.0873/0.2291/0.1073/0.1382/0.2070/-0.1959 are NEVER imported.

BRAIN FRAMING, labelled per choice (drill sec 2, 3, 9, 10 -- not re-argued here, cited).
  PINNED AS A PHENOMENON: heterosynaptic normalisation is measured in tissue and is algebraically the
    same family as Oja (drill sec 2.5). Divisive normalisation's FORM is measured across many cortical
    areas (Carandini & Heeger); its sigma, n and POOL are fitted per area/preparation -- parameters to
    sweep, never constants to adopt.
  PROPOSED, NOT PINNED: Oja/Sanger has no direct synaptic demonstration; the adjacency-to-
    substitutability result (sec 5.2) is a theorem about an artificial linear network, and it is the
    ONLY equation for that transition found anywhere in this drill's literature search. Said plainly,
    not dressed as biology.
  OUR INVENTION UNDER TEST: every specific choice of k, eta, sigma, n, pool, and the random-projection
    constructions used in the controls. No anatomical claim is made for the sha256/Gaussian random
    bases either -- both A0 and its controls are OUR INVENTION, exactly as the incumbent already is.

PRIOR-WORK CHECK. `bash tools/substrate_query.sh "learned basis Oja Sanger divisive normalization PPMI
write rule cortex"` was RUN before this cell was written and returned NO OUTPUT within 60s -- consistent
with the STANDING STALE status recorded in notes/STATUS.md (hd_director_kb_continuous_ingest livelock)
and the SAME exemption notes/drill_what_cortex_computes_across_episodes_write_rule_equations_2026-08-18.md
sec 1 records for itself. Substitute: that drill note's own enumeration (its sec 1 "PRIOR-WORK CHECK",
sec 11 "HOW I ENUMERATED", sec 12 "SOURCES CONSULTED") is READ IN FULL and is the prior-work check this
cell relies on; it is not re-derived here. Additionally, on-disk prior negatives directly relevant to
these arms are carried forward from the drill rather than re-discovered: divisive normalisation on the
READ side (different pool, different stage) measured NULL / HARD_FAIL_GAIN_HURTS twice
(exp_graded_divisive_comparator_v1, exp_task_local_normalisation_pool_v1); the pseudoinverse write rule
(closed-form limit of the same Oja/heterosynaptic family) measured HARD_FAIL_WRITE_RULE_NOT_THE_LEVER
on the KG store (exp_kg_store_write_rule_decorrelated_ceiling_v1, oracle MRR 1.04x against a 2.0x bar) --
attributed to near-orthogonal KG keys, a DIFFERENT input regime from this cell's Zipf-distributed word
counts, so not imported as a verdict here, only as context. Neither prior negative touched the WRITE-
side basis or a context-word-pool denominator, which is what this cell measures.

ORGAN REUSE, enumerated then reconciled -- no pipeline stage or instrument is reimplemented:
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)  build_population, load_full_accum_from_
                                                           checkpoint, dprime_stats/summary, rank_
                                                           summary, l2n, MASTER_SEED, REGRESSION_A0_
                                                           PARTIAL, REGRESSION_TOL
  experiments.exp_cue_information_audit_v1 (INFO)         load_corpus_and_buckets, build_vocab,
                                                           to_sparse, l2n_sparse, _ShimSpace, C3
  experiments.exp_writerule_step_ladder_v1 (WR)            wordnet_relation_composition,
                                                           syntagmatic_jaccard_composition (REUSED
                                                           verbatim, not reimplemented -- these ARE
                                                           the composition instrument this cell needs)
  tools.floor_battery (FB)                                 hit_at_1_both_tie_conventions, the four
                                                           floors, paired_bootstrap_ci, margin,
                                                           oracle_constant_scores, as_constant_matrix
  hdlab.reading_grounding_loop                              content_lemmas (for the syntagmatic
                                                           co-occurrence index, identical to WR)
  hdlab.ppmi_sparse_encoder                                 READ for its PPMI formula and context-
                                                           distribution-smoothing convention (credited,
                                                           the C2 'both'-pool transform follows it);
                                                           not directly callable here because it is
                                                           fit for (sentence, concept_label) supervised
                                                           char-trigram data, a different input shape
                                                           from this cell's anchor x context-word count
                                                           matrix -- so the FORMULA is reused, the class
                                                           is not instantiated.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every named arm's hit-vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics), out_dir is a
#   Path object throughout (get_output_dir returns Path; never str()'d before the call)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: tools.exp_checkpoint for JSON-safe per-arm composition units (mirrors WR);
#   large deterministic SVD embeddings additionally cached as .npz under this cell's own scratch dir
#   (same convention exp_cue_information_audit_v1 uses for its corpus cache) since they are too large
#   for the JSON-line checkpoint store -- both are resumable, neither silently swallows a partial run
# - discriminator survives scale: C1/C2 winners are selected on the FULL grid's own accuracy sweep,
#   not previewed on a smaller regime and assumed to transfer
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated cache and the
#   landed exp_cue_information_audit_v1 checkpoint unmodified; no new calibration introduced)
# - progress_logging: print_flush_true (every phase prints a flushed line); mandatory here since
#   several units (SVD at k=2048) run long enough to fall under Sec 17's timeout_s>=1800 rule for the
#   FULL grid's overall elapsed time
# - baseline_in_band: n/a -- every scored arm is oracle self-address by construction (~1.0); the gate
#   is K1/N1 (addressing), not a 0.05-0.95 baseline band, matching WR's own declared exemption
# - crlb_floor_computed: n/a -- this is a composition/margin measurement over representations of an
#   existing store, not a capacity-sweep; declared explicitly rather than silently omitted

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. The live store is
NEVER rebuilt or modified. data/foundation/** is never opened. Writes only under
data/exp_writerule_learned_basis_denominator_gate_v1[_reduced]/ and this cell's own scratch subdir.
DO NOT WIRE ANYTHING INTO hdlab/ -- this cell measures a gate; promotion is the Director's call.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/hdlab next -- flushed so a slow transitive import, e.g. "
      "the unguarded top-level `import torch` chain some sibling cells pull in, is never mistaken for "
      "a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE          # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
import experiments.exp_writerule_step_ladder_v1 as WR                   # noqa: E402  READ ONLY (composition instrument)
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "writerule_learned_basis_denominator_gate_v1"
CODE_VERSION = "v1.1"  # v1.0's smoke run exposed a real bug: divisive_normalize(pool='both') silently
                       # ignored wrongpool_seed, so C2_CTRL_WRONGPOOL was numerically IDENTICAL to C2
                       # whenever C2's winning pool was 'both' (=PPMI) -- not a control at all. Fixed in
                       # ppmi_transform + divisive_normalize (both now route wrongpool_seed through) and
                       # pinned by two new self-test assertions. Version bumped so no cached MAIN/
                       # COMPOSITION checkpoint unit can silently resume the pre-fix logic.
FINDINGS = "notes/writerule_learned_basis_denominator_gate_v1_findings_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"
assert "--smoke" not in sys.argv, ("this cell's flag is --grid full|reduced; '--smoke' anywhere in "
                                   "argv silently downgrades an unrelated imported ruler -- see brief")

MASTER_SEED = PIPE.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
ADDRESS_EXACT_MIN = 0.95
N_PROBE_COMPOSITION = 60 if SMOKE else 700
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")

K_GRID_C1 = (16, 32, 64) if SMOKE else (64, 128, 256, 512, 1024, 2048)
C2_SIGMA_GRID = (1.0, 8.0) if SMOKE else (1.0, 4.0, 16.0)
C2_N_GRID = (1,) if SMOKE else (1, 2)
C2_POOL_GRID = ("col", "both") if SMOKE else ("col", "row", "both")
C2_PROJECT_K = 256          # matches the incumbent A0 dimensionality, isolates the denominator alone
PPMI_SMOOTHING_ALPHA = 0.75  # Levy/Goldberg context-distribution smoothing; SAME value hdlab/ppmi_
                             # sparse_encoder.py defaults to (its `smoothing` kwarg) -- credited, not
                             # independently invented, and NOT swept (the brief asks sigma/n/pool swept,
                             # not this classical constant)

SCRATCH = os.path.join(REPO, "scratch", "writerule_learned_basis_denominator_gate_v1")
os.makedirs(SCRATCH, exist_ok=True)


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _sp_axis_sum(M: sp.spmatrix, axis: int) -> np.ndarray:
    return np.asarray(M.sum(axis=axis)).ravel()


# =================================================================================================
# ARM CONSTRUCTIONS -- every function below returns a DENSE [n_anchors, k] representation matrix
# from the SAME raw sparse anchor x context-word count matrix P [n_anchors, V]. Scoring downstream is
# always the SAME construction: Mn = l2n(M); S = Mn @ Mn[qidx_T].T (self-row oracle-key cue, matching
# experiments.exp_writerule_step_ladder_v1's own R3/R4 construction for the unprojected/projected
# rungs) -- so changing ONLY the representation is the single variable across every arm below.
# =================================================================================================
def random_project(P: sp.spmatrix, k: int, seed: int) -> np.ndarray:
    """OUR INVENTION, same family as the incumbent's own sha256-seeded bipolar H: a fixed random
    basis, here a Gaussian iid matrix (near-isometry, same JL guarantee as the incumbent's bipolar
    basis) scaled by 1/sqrt(k) so the projected norm is roughly preserved in expectation."""
    V = P.shape[1]
    rng = np.random.default_rng(seed)
    R = (rng.standard_normal((V, k)).astype(np.float32) / np.sqrt(float(k)))
    M = P @ R
    return np.asarray(M, dtype=np.float32)


def svd_embed(P: sp.spmatrix, k: int, seed: int, cache_tag: str) -> Tuple[np.ndarray, Dict]:
    """Closed-form equivalent of Oja/Sanger's converged fixed point (drill sec 9, C1): truncated SVD
    of the count matrix. Representation = U_k * sqrt(S_k), the SAME convention hdlab/ppmi_sparse_
    encoder.py already uses for its own SVD step. Cached to .npz (deterministic given P/k/seed) since
    an embedding matrix is too large for the JSON-line checkpoint store; resumable across restarts."""
    cache_path = os.path.join(SCRATCH, "svd_%s_k%d.npz" % (cache_tag, k))
    if os.path.exists(cache_path):
        z = np.load(cache_path)
        return z["M"].astype(np.float32), {"source": "cached", "path": cache_path,
                                           "singvals_top5": z["s_top5"].tolist()}
    t0 = time.time()
    k_eff = min(k, min(P.shape) - 1)
    u, s, vt = spla.svds(P.astype(np.float64), k=k_eff, rng=seed)
    order = np.argsort(-s)
    u, s = u[:, order], s[order]
    M = (u * np.sqrt(np.maximum(s, 0.0))[None, :]).astype(np.float32)
    if k_eff < k:
        M = np.concatenate([M, np.zeros((M.shape[0], k - k_eff), dtype=np.float32)], axis=1)
    elapsed = round(time.time() - t0, 1)
    tmp = cache_path + ".tmp.npz"
    np.savez_compressed(tmp, M=M, s_top5=np.asarray(sorted(s)[-5:], dtype=np.float64))
    os.replace(tmp, cache_path)
    print("[svd_embed] tag=%s k=%d (eff=%d) elapsed=%.1fs top_singval=%.2f" % (
        cache_tag, k, k_eff, elapsed, float(s.max()) if s.size else -1.0), flush=True)
    return M, {"source": "computed", "elapsed_s": elapsed, "k_eff": k_eff,
               "singvals_top5": sorted(s)[-5:] if hasattr(s, "__iter__") else []}


def build_frequency_shuffled(P: sp.spmatrix, seed: int) -> sp.spmatrix:
    """The drill's C1 control (sec 9): a matrix that preserves each anchor's total context mass
    EXACTLY and the corpus word-frequency marginal IN EXPECTATION, drawn i.i.d. per anchor from the
    GLOBAL frequency distribution -- destroying every anchor-specific co-occurrence signal while
    leaving unigram frequency intact. Vectorised categorical sampling via inverse-CDF search, not a
    per-anchor Python loop over the vocabulary (would be too slow at V~20k)."""
    row_sum = _sp_axis_sum(P, axis=1)
    col_sum = _sp_axis_sum(P, axis=0)
    col_probs = col_sum / max(float(col_sum.sum()), 1e-12)
    cdf = np.cumsum(col_probs)
    cdf[-1] = 1.0
    n_anchors = P.shape[0]
    draws_per_anchor = np.maximum(np.round(row_sum).astype(np.int64), 0)
    total_draws = int(draws_per_anchor.sum())
    rng = np.random.default_rng(seed)
    if total_draws == 0:
        return sp.csr_matrix(P.shape, dtype=np.float32)
    u = rng.random(total_draws)
    col_idx = np.searchsorted(cdf, u, side="right")
    col_idx = np.clip(col_idx, 0, P.shape[1] - 1)
    row_idx = np.repeat(np.arange(n_anchors), draws_per_anchor)
    data = np.ones(total_draws, dtype=np.float32)
    M = sp.csr_matrix((data, (row_idx, col_idx)), shape=P.shape)
    M.sum_duplicates()
    return M


def ppmi_transform(P: sp.spmatrix, alpha: float = PPMI_SMOOTHING_ALPHA,
                   wrongpool_seed: Optional[int] = None) -> sp.spmatrix:
    """PPMI(a,j) = max(0, log(P(a,j) / (P(a) * P_alpha(j)))), context-distribution-smoothed on the
    column marginal -- the EXACT formula and alpha convention of hdlab/ppmi_sparse_encoder.py's own
    fit() (its 'PPMI transform' section, Levy/Goldberg 2015), reused sparse-native (only nonzero
    entries are touched, matching that module's own 'pmi[cooc==0]=0' semantics) rather than densified,
    since V~20k x n_anchors~5.5k would be ~470MB dense float64 for no reason. wrongpool_seed, if given,
    permutes the column-marginal assignment (SAME control as divisive_normalize's col/row branches) --
    required here too, not just there: C2's winning pool is frequently 'both' (=PPMI), and a WRONGPOOL
    control that silently no-ops on that branch is not a control at all (caught by this cell's own
    smoke run, where C2_CTRL_WRONGPOOL was numerically IDENTICAL to C2 before this fix)."""
    row_sum = _sp_axis_sum(P, axis=1) + 1e-12
    col_sum = _sp_axis_sum(P, axis=0) + 1e-12
    col_sum_sm = col_sum ** alpha
    col_sm_total = float(col_sum_sm.sum()) + 1e-12
    if wrongpool_seed is not None:
        col_sum_sm = col_sum_sm[np.random.default_rng(wrongpool_seed).permutation(col_sum_sm.size)]
    Pc = P.tocoo()
    numer = Pc.data.astype(np.float64) * col_sm_total
    denom = row_sum[Pc.row] * col_sum_sm[Pc.col]
    ratio = numer / np.maximum(denom, 1e-30)
    pmi = np.log(np.maximum(ratio, 1e-30))
    ppmi_data = np.maximum(pmi, 0.0).astype(np.float32)
    return sp.csr_matrix((ppmi_data, (Pc.row, Pc.col)), shape=P.shape)


def divisive_normalize(P: sp.spmatrix, sigma: float, n: int, pool: str,
                       wrongpool_seed: Optional[int] = None) -> sp.spmatrix:
    """Carandini-Heeger divisive form P~_aj = P_aj^n / (sigma^n + SUM_pool P^n) (drill sec 3/9, C2).
    pool='col' sums over anchors for fixed context word j (corpus frequency of word j -- suppresses
    high-frequency collocates); pool='row' sums over context words for fixed anchor a (the anchor's
    own total mass); pool='both' is full PPMI (see ppmi_transform), sigma/n unused in that branch
    (the log form has no additive semi-saturation term in the classical PPMI definition -- disclosed,
    not silently ignored). wrongpool_seed, if given, permutes the denominator's column/row assignment
    -- the exact control that caught the read-side divisive-norm cell reproducing its effect from the
    wrong pool (drill sec 3.3)."""
    if pool == "both":
        return ppmi_transform(P, wrongpool_seed=wrongpool_seed)
    Pn_sparse = P.power(n) if n != 1 else P
    if pool == "col":
        denom = (sigma ** n) + _sp_axis_sum(Pn_sparse, axis=0)
    elif pool == "row":
        denom = (sigma ** n) + _sp_axis_sum(Pn_sparse, axis=1)
    else:
        raise ValueError("unknown pool %r" % pool)
    if wrongpool_seed is not None:
        denom = denom[np.random.default_rng(wrongpool_seed).permutation(denom.size)]
    Pn = Pn_sparse.tocoo()
    vals = Pn.data / (denom[Pn.col] if pool == "col" else denom[Pn.row])
    return sp.csr_matrix((vals, (Pn.row, Pn.col)), shape=P.shape)


def pure_idf_normalize(P: sp.spmatrix, sigma: float) -> sp.spmatrix:
    """C2_CTRL_PURE_IDF: divide by document frequency alone (no divisive form) -- separates 'any
    frequency suppression' from 'this normalisation'."""
    df = _sp_axis_sum((P > 0).astype(np.float32), axis=0)
    Pc = P.tocoo()
    vals = Pc.data / (sigma + df[Pc.col])
    return sp.csr_matrix((vals, (Pc.row, Pc.col)), shape=P.shape)


# =================================================================================================
# ONLINE SANGER/GHA -- the small-scale, explicitly-scoped eta confirmation (see module docstring).
# =================================================================================================
def sanger_fit(X: np.ndarray, k: int, eta: float, n_epochs: int, seed: int) -> np.ndarray:
    """Streaming Generalized Hebbian Algorithm (Sanger 1989): dW = eta*(y x^T - LT[y y^T] W), one
    row of X per update. Returns W [k, d]; its rows converge toward the top-k principal directions of
    X's covariance (Sanger's own convergence theorem)."""
    n, d = X.shape
    rng = np.random.default_rng(seed)
    W = (rng.standard_normal((k, d)).astype(np.float64) * 0.01)
    order = np.arange(n)
    for _ in range(n_epochs):
        rng.shuffle(order)
        for i in order:
            x = X[i]
            y = W @ x
            LT = np.tril(np.outer(y, y))
            W = W + eta * (np.outer(y, x) - LT @ W)
    return W


def subspace_alignment(W: np.ndarray, V_ref: np.ndarray) -> float:
    """Mean cosine of the principal angles between the row-space of W [k,d] and the column-space of
    V_ref [d,k] (right singular vectors of the same subsampled matrix) -- 1.0 = identical subspaces."""
    Wn = l2n(W)
    sing = np.linalg.svd(Wn @ V_ref, compute_uv=False)
    sing = np.clip(sing, 0.0, 1.0)
    return float(np.mean(sing))


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- random_project: shape, determinism, and near-isometry sanity (JL-style norm preservation) --
    rng = np.random.default_rng(3)
    Pfix = sp.csr_matrix(rng.poisson(1.5, size=(12, 40)).astype(np.float32))
    M1 = random_project(Pfix, k=8, seed=5)
    M2 = random_project(Pfix, k=8, seed=5)
    M3 = random_project(Pfix, k=8, seed=6)
    assert M1.shape == (12, 8)
    assert np.allclose(M1, M2), "random_project must be deterministic given the same seed"
    assert not np.allclose(M1, M3), "different seeds must give different bases"
    ev["random_project_determinism"] = True

    # --- svd_embed: reconstructs a KNOWN low-rank structure (two well-separated clusters) ------------
    a = np.array([1.0, 0.0, 1.0, 0.0, 0.9])
    b = np.array([0.0, 1.0, 0.0, 1.0, 0.1])
    rows = []
    for _ in range(6):
        rows.append(a + rng.normal(0, 0.01, size=5))
    for _ in range(6):
        rows.append(b + rng.normal(0, 0.01, size=5))
    Ptoy = sp.csr_matrix(np.maximum(np.array(rows), 0.0).astype(np.float32))
    Mtoy, diag_toy = svd_embed(Ptoy, k=2, seed=1, cache_tag="selftest_toy")
    cos_within_a = float((l2n(Mtoy[0:1]) @ l2n(Mtoy[1:2]).T).item())
    cos_across = float((l2n(Mtoy[0:1]) @ l2n(Mtoy[6:7]).T).item())
    assert cos_within_a > cos_across + 0.3, (
        "svd_embed failed to separate two known clusters: within=%r across=%r" % (cos_within_a, cos_across))
    ev["svd_embed_known_cluster_separation"] = {"cos_within": round(cos_within_a, 4),
                                                "cos_across": round(cos_across, 4)}
    # cache round-trip
    Mtoy_cached, diag_cached = svd_embed(Ptoy, k=2, seed=1, cache_tag="selftest_toy")
    assert diag_cached["source"] == "cached" and np.allclose(Mtoy, Mtoy_cached, atol=1e-4), \
        "svd_embed cache round-trip mismatch"
    ev["svd_embed_cache_roundtrip"] = True

    # --- build_frequency_shuffled: EXACT row-sum preservation, marginal-only column structure --------
    Pfs = build_frequency_shuffled(Ptoy, seed=9)
    row_orig = _sp_axis_sum(Ptoy, axis=1)
    row_shuf = _sp_axis_sum(Pfs, axis=1)
    assert np.allclose(np.round(row_orig), row_shuf, atol=1.0), (
        "frequency-shuffled must preserve each anchor's row sum: %r vs %r" % (row_orig, row_shuf))
    # co-occurrence identity destroyed: the two original clusters must NOT be separable any more
    Mfs, _ = svd_embed(Pfs, k=2, seed=1, cache_tag="selftest_toy_shuffled")
    cos_within_a_fs = float((l2n(Mfs[0:1]) @ l2n(Mfs[1:2]).T).item())
    cos_across_fs = float((l2n(Mfs[0:1]) @ l2n(Mfs[6:7]).T).item())
    assert abs(cos_within_a_fs - cos_across_fs) < abs(cos_within_a - cos_across), (
        "frequency-shuffled must be LESS cluster-separated than the real structure: "
        "shuffled diff=%.4f real diff=%.4f" % (abs(cos_within_a_fs - cos_across_fs),
                                               abs(cos_within_a - cos_across)))
    ev["frequency_shuffled_row_sum_preserved_and_structure_destroyed"] = True

    # --- ppmi_transform: known answer -- a word that co-occurs ONLY with one anchor and is globally
    # rare must score a HIGH ppmi with that anchor; a word present in every anchor's row (no signal)
    # must score LOW ppmi everywhere it appears --------------------------------------------------------
    # col sums DELIBERATELY ALL DISTINCT (5, 8, 15) so the wrongpool control below is guaranteed to
    # differ under any non-identity permutation, not just under a lucky seed.
    dense = np.array([[5.0, 0.0, 3.0],   # col0 = distinctive-to-anchor0, col2 = ubiquitous+frequent
                      [0.0, 8.0, 3.0],
                      [0.0, 0.0, 3.0],
                      [0.0, 0.0, 3.0],
                      [0.0, 0.0, 3.0]], dtype=np.float32)
    Pk = sp.csr_matrix(dense)
    ppmi = ppmi_transform(Pk).toarray()
    assert ppmi[0, 0] > ppmi[0, 2], "distinctive word must out-score the ubiquitous word under PPMI, " \
                                    "same row (WITHIN-anchor comparison, the pool='col' equation's job)"
    assert ppmi[1, 2] <= ppmi[0, 0], (
        "the ubiquitous/frequent word's ppmi (row1,col2) must not exceed the distinctive word's ppmi "
        "(row0,col0): %r vs %r" % (ppmi[1, 2], ppmi[0, 0]))
    ev["ppmi_transform_known_answer"] = {"distinctive": round(float(ppmi[0, 0]), 4),
                                         "ubiquitous_same_row": round(float(ppmi[0, 2]), 4),
                                         "ubiquitous_matched_row_mass": round(float(ppmi[1, 2]), 4)}

    # --- ppmi_transform wrongpool must ALSO differ (regression: caught by this cell's own smoke run,
    # where divisive_normalize(pool='both') silently ignored wrongpool_seed and C2_CTRL_WRONGPOOL was
    # numerically identical to C2 itself -- fixed, and pinned here so it cannot recur silently) --------
    ppmi_wrong = ppmi_transform(Pk, wrongpool_seed=0).toarray()
    assert not np.allclose(ppmi, ppmi_wrong), \
        "ppmi_transform's wrongpool_seed must produce a DIFFERENT transform, not a silent no-op"
    dn_both_wrong = divisive_normalize(Pk, sigma=1.0, n=1, pool="both", wrongpool_seed=0).toarray()
    dn_both = divisive_normalize(Pk, sigma=1.0, n=1, pool="both").toarray()
    assert not np.allclose(dn_both, dn_both_wrong), (
        "divisive_normalize(pool='both') must route wrongpool_seed into ppmi_transform, not drop it")
    ev["ppmi_wrongpool_not_a_noop"] = True

    # --- divisive_normalize: col-pool suppresses a high-frequency column relative to a rare one ------
    dn = divisive_normalize(Pk, sigma=1.0, n=1, pool="col").toarray()
    assert dn[0, 0] > dn[0, 2], "col-pool divisive norm must suppress the high-frequency column"
    dn_row = divisive_normalize(Pk, sigma=1.0, n=1, pool="row")
    assert dn_row.shape == Pk.shape
    dn_wrong = divisive_normalize(Pk, sigma=1.0, n=1, pool="col", wrongpool_seed=0).toarray()
    assert not np.allclose(dn, dn_wrong), "wrongpool must produce a DIFFERENT normalisation"
    ev["divisive_normalize_known_answer_and_wrongpool_differs"] = True

    # --- pure_idf_normalize: a word in every row must be suppressed relative to a word in one row ----
    idf = pure_idf_normalize(Pk, sigma=0.0).toarray()
    assert idf[0, 0] > idf[0, 2], "pure-idf must suppress the word present in every row"
    ev["pure_idf_known_answer"] = True

    # --- sanger_fit / subspace_alignment: recovers a KNOWN dominant direction on tiny synthetic data -
    rng2 = np.random.default_rng(42)
    direction = np.array([3.0, 4.0]) / 5.0
    Xs = np.outer(rng2.normal(1.0, 0.3, size=200), direction) + rng2.normal(0, 0.02, size=(200, 2))
    Wfit = sanger_fit(Xs, k=1, eta=0.05, n_epochs=4, seed=7)
    cos_to_true = abs(float((l2n(Wfit) @ direction).item()))
    assert cos_to_true > 0.9, "sanger_fit failed to recover the known dominant direction: cos=%.4f" % cos_to_true
    u_ref, s_ref, vt_ref = np.linalg.svd(Xs - Xs.mean(axis=0), full_matrices=False)
    align = subspace_alignment(Wfit, vt_ref[:1].T)
    assert align > 0.85, "subspace_alignment sanity check failed: %.4f" % align
    ev["sanger_fit_known_direction"] = {"cos_to_true": round(cos_to_true, 4), "svd_alignment": round(align, 4)}

    # --- composition instrument REUSED from WR, byte-identical call pattern proven here too ----------
    qw_ = ["dog", "dog", "dog"]
    ww_ = ["canine", "carburetor", "dog"]
    ig_ = np.array([False, False, True])
    idxp = np.array([0, 1, 2])
    comp = WR.wordnet_relation_composition(qw_, ww_, ig_, idxp)
    assert comp["counts"].get("IN_THE_GENEROUS_GOLD", 0) == 1, comp
    ev["WR_wordnet_relation_composition_reused"] = comp["counts"]
    where_ = {"a": {0, 1}, "b": {0, 1}, "c": {5}, "d": set()}
    comp2 = WR.syntagmatic_jaccard_composition(["a", "a"], ["b", "c"], ["b", None], where_, np.array([0, 1]))
    assert abs(comp2["TOP1_WINNER"]["mean"] - 0.5) < 1e-9, comp2
    ev["WR_syntagmatic_jaccard_composition_reused"] = comp2["TOP1_WINNER"]

    # --- arms-must-differ digest sensitivity ---------------------------------------------------------
    a1 = np.array([1.0, 2.0, 3.0])
    a2 = np.array([1.0, 2.0, 3.0001])
    assert _digest(a1) != _digest(a2)
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test) ---------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    P_ = PIPE.build_population()
    C, mat, mat_ok = P_["C"], P_["mat"], P_["mat_ok"]
    n_anchors, qidx = P_["n_anchors"], P_["qidx"]
    GOLD, E, keep_ALL = P_["GOLD"], P_["E"], P_["keep"]
    aux = P_["aux"]

    items = np.flatnonzero(keep_ALL)
    anchors = list(C["anchors"])

    print("[load] full population n_anchors=%d n_items_keep=%d t=%.0fs" % (
        n_anchors, items.size, time.time() - t0), flush=True)

    # =============================== REGRESSION GATE (against the OFFICIAL cached store) ============
    MATn = l2n(mat)
    S_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E, GOLD)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    regression = {"measured": round(a0_full, 4), "expected": PIPE.REGRESSION_A0_PARTIAL,
                 "tol": PIPE.REGRESSION_TOL,
                 "PASS": bool(abs(a0_full - PIPE.REGRESSION_A0_PARTIAL) <= PIPE.REGRESSION_TOL)}
    if not regression["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % regression)
    print("[regression] PASS %.4f (expected %.4f)" % (a0_full, PIPE.REGRESSION_A0_PARTIAL), flush=True)
    del S_full, h_full

    # =============================== ITEM SUBSET FOR THIS CELL's SCORING ============================
    T = items[:300] if grid == "reduced" else items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    query_words = [C["L_words"][int(t)] for t in T]
    print("[load] scored subset n_items=%d t=%.0fs" % (n_items, time.time() - t0), flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": PIPE.CTS.ruler_mode_gate(),
        "REGRESSION_GATE": regression,
        "population": {"n_anchors": n_anchors, "n_items_scored": n_items},
    }

    # =============================== FLOORS, recomputed on THIS population ==========================
    floors_S: Dict[str, np.ndarray] = {}
    Tq = aux["Tq"][T]
    floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(Tq).T).astype(np.float32)
    floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
        FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 8811))
                              @ l2n(mat[qidx_T]).T).astype(np.float32)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(
        FB.constant_prototype_floor(mat, mat_ok), n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]),
        n_items)

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    S_cache: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add_arm(name: str, S: np.ndarray, addressing_target: Optional[np.ndarray] = None) -> None:
        nonlocal scored_all
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        hits_exp[name] = h["hit_exp"]; hits_opt[name] = h["hit_opt"]; hits_cons[name] = h["hit_cons"]
        scored_all = scored_all & h["scored"]
        noise_of[name] = PIPE.dprime_summary(PIPE.dprime_stats(S, E_T, GOLD_T))
        rs, _, _ = PIPE.rank_summary(S, E_T, GOLD_T)
        rank_of[name] = rs
        if addressing_target is not None:
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = addressing_target >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == addressing_target[ok])), 6)
        S_cache[name] = S
        print("[%s] hit@1=%.4f n_scored=%d" % (name, h["hit_exp"][h["scored"]].mean(),
                                               int(h["scored"].sum())), flush=True)

    for k, S in floors_S.items():
        add_arm(k, S)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)

    # =============================== WRITE-SIDE RAW COUNT MATRIX (reused checkpoint) ================
    print("[corpus] loading (cached; instant if scratch/cue_information_audit_v1/buckets_full.npz "
         "exists)", flush=True)
    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, item_diag = INFO.C3.build_items(shim, buckets, counts, INFO.C3.MAX_ITEMS)
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in items]     # FULL keep_ALL set -- required for the
                                                              # checkpoint reuse to find every Qcue_
                                                              # context unit even under --grid reduced
    anchor_ids = anchors
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    P_full, _Q_ctx, reuse_diag = PIPE.load_full_accum_from_checkpoint(info_out_dir, anchor_ids, item_ids_T)
    rep["checkpoint_reuse_P_full"] = reuse_diag
    vocab_f = INFO.build_vocab([P_full])
    P_raw = INFO.to_sparse(P_full, anchor_ids, vocab_f)
    rep["P_raw_shape"] = list(P_raw.shape)
    rep["P_raw_nnz"] = int(P_raw.nnz)
    print("[P_raw] shape=%r nnz=%d t=%.0fs" % (P_raw.shape, P_raw.nnz, time.time() - t0), flush=True)

    def score_M(M: np.ndarray) -> np.ndarray:
        Mn = l2n(M)
        return (Mn @ Mn[qidx_T].T).astype(np.float32)

    def quick_hit(M: np.ndarray) -> Tuple[float, np.ndarray]:
        S = score_M(M)
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        sc = h["scored"]
        acc = float(h["hit_exp"][sc].mean()) if sc.any() else 0.0
        return acc, S

    # =============================== A0 -- the incumbent, self-row construction =====================
    S_A0 = score_M(mat)
    add_arm("A0_RANDOM_PROJECTION", S_A0, addressing_target=qidx_T)
    h_selfrow = FB.hit_at_1_both_tie_conventions(S_A0, E_T, GOLD_T)
    acc_selfrow = float(h_selfrow["hit_exp"][h_selfrow["scored"]].mean())
    # official-cue cross-check (NOT the compared arm -- a consistency check that the self-row
    # construction used uniformly for every OTHER arm agrees with the officially cached exact-key cue)
    S_A0_official = (MATn @ l2n(C["Q_exact"][T]).T).astype(np.float32)
    h_off = FB.hit_at_1_both_tie_conventions(S_A0_official, E_T, GOLD_T)
    acc_official = float(h_off["hit_exp"][h_off["scored"]].mean())
    rep["A0_SELFROW_VS_OFFICIAL_QEXACT_CONSISTENCY_CHECK"] = {
        "selfrow_hit_at_1": round(acc_selfrow, 4),
        "official_qexact_hit_at_1": round(acc_official, 4),
        "agree_within_0.02": bool(abs(acc_selfrow - acc_official) < 0.02),
    }

    # =============================== C1 -- cheap sweep, pick the winner by accuracy =================
    c1_sweep = []
    for k in K_GRID_C1:
        M_k, diag_k = svd_embed(P_raw, k, seed=MASTER_SEED + 1001, cache_tag="C1")
        acc_k, _S = quick_hit(M_k)
        c1_sweep.append({"k": k, "hit_at_1": round(acc_k, 4), "svd_diag": diag_k})
        print("[C1_sweep] k=%d hit@1=%.4f" % (k, acc_k), flush=True)
    rep["C1_SWEEP"] = c1_sweep
    K_WIN = max(c1_sweep, key=lambda r: r["hit_at_1"])["k"]
    rep["C1_WINNING_K"] = K_WIN
    print("[C1_sweep] winning k=%d" % K_WIN, flush=True)

    # =============================== C2 -- cheap sweep, pick the winner by accuracy =================
    c2_sweep = []
    for sigma in C2_SIGMA_GRID:
        for n_exp in C2_N_GRID:
            for pool in C2_POOL_GRID:
                if pool == "both" and (sigma != C2_SIGMA_GRID[0] or n_exp != C2_N_GRID[0]):
                    continue   # 'both'=PPMI ignores sigma/n; do not repeat identical work
                Pn = divisive_normalize(P_raw, sigma, n_exp, pool)
                M_c2 = random_project(Pn, C2_PROJECT_K, seed=MASTER_SEED + 2002)
                acc_c2, _S = quick_hit(M_c2)
                c2_sweep.append({"sigma": sigma, "n": n_exp, "pool": pool, "hit_at_1": round(acc_c2, 4)})
                print("[C2_sweep] sigma=%.1f n=%d pool=%s hit@1=%.4f" % (sigma, n_exp, pool, acc_c2),
                     flush=True)
    rep["C2_SWEEP"] = c2_sweep
    c2_win = max(c2_sweep, key=lambda r: r["hit_at_1"])
    rep["C2_WINNING_CONFIG"] = c2_win
    print("[C2_sweep] winning config=%r" % c2_win, flush=True)

    # =============================== NAMED ARMS -- full analysis ====================================
    M_C1, c1_win_diag = svd_embed(P_raw, K_WIN, seed=MASTER_SEED + 1001, cache_tag="C1")
    add_arm("C1_LEARNED_BASIS", score_M(M_C1), addressing_target=qidx_T)

    M_C1_RAND = random_project(P_raw, K_WIN, seed=MASTER_SEED + 3003)
    add_arm("C1_CTRL_MATCHED_RANK_RANDOM", score_M(M_C1_RAND), addressing_target=qidx_T)

    P_freqshuf = build_frequency_shuffled(P_raw, seed=MASTER_SEED + 4004)
    M_C1_FREQ, _ = svd_embed(P_freqshuf, K_WIN, seed=MASTER_SEED + 1001, cache_tag="C1_freqshuffled")
    add_arm("C1_CTRL_FREQUENCY_SHUFFLED", score_M(M_C1_FREQ), addressing_target=qidx_T)

    P_c2win = divisive_normalize(P_raw, c2_win["sigma"], c2_win["n"], c2_win["pool"])
    M_C2 = random_project(P_c2win, C2_PROJECT_K, seed=MASTER_SEED + 2002)
    add_arm("C2_WRITE_TIME_DIVISIVE_NORM", score_M(M_C2), addressing_target=qidx_T)

    P_c2wrong = divisive_normalize(P_raw, c2_win["sigma"], c2_win["n"], c2_win["pool"],
                                   wrongpool_seed=MASTER_SEED + 5005)
    M_C2_WRONG = random_project(P_c2wrong, C2_PROJECT_K, seed=MASTER_SEED + 2002)
    add_arm("C2_CTRL_WRONGPOOL", score_M(M_C2_WRONG), addressing_target=qidx_T)

    P_c2idf = pure_idf_normalize(P_raw, sigma=c2_win["sigma"])
    M_C2_IDF = random_project(P_c2idf, C2_PROJECT_K, seed=MASTER_SEED + 2002)
    add_arm("C2_CTRL_PURE_IDF", score_M(M_C2_IDF), addressing_target=qidx_T)

    named_arms = ["A0_RANDOM_PROJECTION", "C1_LEARNED_BASIS", "C1_CTRL_MATCHED_RANK_RANDOM",
                 "C1_CTRL_FREQUENCY_SHUFFLED", "C2_WRITE_TIME_DIVISIVE_NORM", "C2_CTRL_WRONGPOOL",
                 "C2_CTRL_PURE_IDF"]

    # ---- N1 NULL: derangement of A0's query assignment ----------------------------------------------
    rng_n = np.random.default_rng(MASTER_SEED + 9009)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng_n.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    S_null = (MATn @ l2n(mat[qidx_T][perm]).T).astype(np.float32)
    add_arm("N1_RANDOM_NULL", S_null, addressing_target=qidx_T)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== K1/N1 GATES -- BEFORE anything else is published ================
    k1 = {name: addressing_of.get(name) for name in named_arms}
    k1_pass = all((v is not None and v >= ADDRESS_EXACT_MIN) for v in k1.values())
    n1_addr = addressing_of.get("N1_RANDOM_NULL")
    n1_addr = 1.0 if n1_addr is None else n1_addr
    n1_pass = bool(n1_addr < max(0.02, 20.0 / n_anchors))
    rep["K1_KNOWN_ANSWER"] = {"addressing_per_arm": k1, "gate": ADDRESS_EXACT_MIN, "PASS": bool(k1_pass)}
    rep["N1_NULL"] = {"addressing_RANDOM_NULL": n1_addr, "chance_addressing": round(1.0 / n_anchors, 8),
                      "PASS": n1_pass}
    if not (k1_pass and n1_pass):
        raise SystemExit("INSTRUMENT_STILL_LOOSE -- K1/N1 gate failed, publishing nothing: K1=%r N1=%r"
                         % (rep["K1_KNOWN_ANSWER"], rep["N1_NULL"]))
    print("[gates] K1 PASS (%r) N1 PASS (%.6f)" % (k1, n1_addr), flush=True)

    # =============================== BOOTSTRAP ========================================================
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    ci_halfwidth = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
                    for k, v in boot.items()}
    analytic_null_hw = round(float(1.645 / np.sqrt(max(nc - 1, 1))), 5)
    rep["POWER"] = {"n_common_scored": nc, "analytic_null_halfwidth": analytic_null_hw}
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1390", "0.0873", "0.2291", "0.1073", "0.1382", "0.2070", "-0.1959"]
    rep["BINDING_FLOOR"] = binding
    rep["BINDING_FLOOR_VALUE"] = round(acc[binding], 4) if binding else None
    rep["ACCURACY_TABLE"] = {name: {"hit_at_1": round(acc[name], 4),
                                    "ci_halfwidth": ci_halfwidth[name],
                                    "addressing": addressing_of.get(name),
                                    "dprime": noise_of[name], "rank": rank_of[name]}
                             for name in list(floors_S) + ["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"]
                             + named_arms + ["N1_RANDOM_NULL"]}

    # ---- margins vs A0 for every named challenger ----------------------------------------------------
    margins_vs_a0 = {}
    for name in named_arms:
        if name == "A0_RANDOM_PROJECTION":
            continue
        margins_vs_a0[name] = FB.margin(boot, name, "A0_RANDOM_PROJECTION")
    rep["ACCURACY_MARGIN_VS_A0"] = margins_vs_a0

    # =============================== WINNER COMPOSITION -- the scientific core ======================
    print("[composition] building sentence co-occurrence index (content_lemmas over %d sentences, "
         "REUSED corpus, store never rebuilt)" % len(sents), flush=True)
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in content_lemmas(s):
            where.setdefault(w, set()).add(si)

    rng_probe = np.random.default_rng(MASTER_SEED + 8181)
    common_idx = np.flatnonzero(scored_all)
    idx_probe = rng_probe.choice(common_idx, size=min(N_PROBE_COMPOSITION, common_idx.size), replace=False)
    idx_probe = np.sort(idx_probe)
    rep["COMPOSITION_N_PROBE"] = int(idx_probe.size)

    composition_per_arm: Dict[str, Dict] = {}
    no_relation_bool_of: Dict[str, np.ndarray] = {}
    out_dir_ckpt = os.path.join(REPO, "data", ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    for name in named_arms:
        S = S_cache[name]
        ck_key = unit_key("COMPOSITION", CODE_VERSION, grid, name)
        prior = load_units(out_dir_ckpt).get(ck_key)
        if prior is not None:
            print("[composition] %s RESUMED FROM CHECKPOINT" % name, flush=True)
            composition_per_arm[name] = prior
            no_relation_bool_of[name] = np.array(prior["wordnet"]["no_relation_bool"], dtype=bool)
            continue
        Sm = np.where(E_T, S, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        winner_words = [anchors[int(w)] for w in top1]
        in_gold = np.array([bool(GOLD_T[int(top1[i]), i]) for i in range(n_items)])
        gbest = np.where(GOLD_T & E_T, Sm, -np.inf)
        gtop = np.argmax(gbest, axis=0)
        has_gold = (GOLD_T & E_T).any(axis=0)
        gold_words: List[Optional[str]] = [anchors[int(gtop[i])] if has_gold[i] else None
                                           for i in range(n_items)]
        wn_comp = WR.wordnet_relation_composition(query_words, winner_words, in_gold, idx_probe)
        jac_comp = WR.syntagmatic_jaccard_composition(query_words, winner_words, gold_words, where,
                                                       idx_probe)
        rec = {"wordnet": wn_comp, "syntagmatic": jac_comp}
        composition_per_arm[name] = rec
        no_relation_bool_of[name] = np.array(wn_comp["no_relation_bool"], dtype=bool)
        record_unit(out_dir_ckpt, ck_key, rec)
        print("[composition] %s no_relation=%.3f winner_share=%s gold_share=%s winner_mean=%s "
             "gold_mean=%s ratio=%s" % (
                 name, wn_comp["fraction_no_close_relation"] or -1,
                 jac_comp["TOP1_WINNER"]["frac_ever_co_occurring"],
                 jac_comp["BEST_GOLD_SYNONYM"]["frac_ever_co_occurring"],
                 jac_comp["TOP1_WINNER"]["mean"], jac_comp["BEST_GOLD_SYNONYM"]["mean"],
                 jac_comp["winner_over_gold_ratio_of_means"]), flush=True)
    rep["WINNER_COMPOSITION_PER_ARM"] = composition_per_arm

    # ---- paired composition deltas: every named challenger vs A0, bootstrap over idx_probe ----------
    comp_vs_a0 = []
    rng_cb = np.random.default_rng(MASTER_SEED + 5151)
    n_probe = idx_probe.size
    xa0 = no_relation_bool_of["A0_RANDOM_PROJECTION"].astype(np.float64)
    boot_idx = rng_cb.integers(0, n_probe, size=(2000, n_probe))
    for name in named_arms:
        if name == "A0_RANDOM_PROJECTION":
            continue
        xb = no_relation_bool_of[name].astype(np.float64)
        diff = xb[boot_idx].mean(axis=1) - xa0[boot_idx].mean(axis=1)
        lo, hi = float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))
        band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
        jw = composition_per_arm[name]["syntagmatic"]["TOP1_WINNER"]
        jg = composition_per_arm[name]["syntagmatic"]["BEST_GOLD_SYNONYM"]
        comp_vs_a0.append({
            "arm": name,
            "no_relation_rate_A0": round(float(xa0.mean()), 4),
            "no_relation_rate_arm": round(float(xb.mean()), 4),
            "delta_point": round(float(np.mean(diff)), 4),
            "delta_ci95": [round(lo, 4), round(hi, 4)], "band": band,
            "winner_share": jw["frac_ever_co_occurring"], "gold_share": jg["frac_ever_co_occurring"],
            "winner_mean": jw["mean"], "gold_mean": jg["mean"],
            "winner_over_gold_ratio_of_means": composition_per_arm[name]["syntagmatic"][
                "winner_over_gold_ratio_of_means"],
        })
    rep["COMPOSITION_DELTA_VS_A0"] = comp_vs_a0
    # A0's own composition row, for reference alongside the deltas
    a0_jw = composition_per_arm["A0_RANDOM_PROJECTION"]["syntagmatic"]["TOP1_WINNER"]
    a0_jg = composition_per_arm["A0_RANDOM_PROJECTION"]["syntagmatic"]["BEST_GOLD_SYNONYM"]
    rep["A0_COMPOSITION_REFERENCE"] = {
        "no_relation_rate": round(float(xa0.mean()), 4),
        "winner_share": a0_jw["frac_ever_co_occurring"], "gold_share": a0_jg["frac_ever_co_occurring"],
        "winner_mean": a0_jw["mean"], "gold_mean": a0_jg["mean"],
        "winner_over_gold_ratio_of_means": composition_per_arm["A0_RANDOM_PROJECTION"]["syntagmatic"][
            "winner_over_gold_ratio_of_means"],
        "LANDED_BASELINE_exp_writerule_step_ladder_v1_CODE_PROJECT_row":
            "composition delta +0.0031 [-0.0243,+0.0300] NOT_SEPARATED (R3->R4); this cell's A0 is a "
            "SELF-ROW construction, not byte-identical to R4's official-Q_exact construction -- see "
            "A0_SELFROW_VS_OFFICIAL_QEXACT_CONSISTENCY_CHECK for how closely they agree here.",
    }

    # =============================== ONLINE SANGER ETA CONFIRMATION (scoped, secondary) ==============
    print("[sanger] building the small-scale subsample for the eta confirmation", flush=True)
    n_sub = min(500, P_raw.shape[0])
    d_sub = min(2000, P_raw.shape[1])
    col_sum_full = _sp_axis_sum(P_raw, axis=0)
    top_cols = np.argsort(-col_sum_full)[:d_sub]
    rng_sub = np.random.default_rng(MASTER_SEED + 6006)
    sub_rows = rng_sub.choice(P_raw.shape[0], size=n_sub, replace=False)
    X_sub = np.asarray(P_raw[sub_rows][:, top_cols].todense(), dtype=np.float64)
    X_sub = l2n(X_sub.astype(np.float32)).astype(np.float64)
    u_sub, s_sub, vt_sub = np.linalg.svd(X_sub, full_matrices=False)
    K_SANGER = 16
    V_ref = vt_sub[:K_SANGER].T   # [d_sub, K_SANGER]
    ETA_GRID = (0.001, 0.01, 0.05) if grid == "full" else (0.01,)
    sanger_results = []
    for eta in ETA_GRID:
        t_s = time.time()
        W = sanger_fit(X_sub, k=K_SANGER, eta=eta, n_epochs=3 if grid == "full" else 1,
                       seed=MASTER_SEED + 7007)
        align = subspace_alignment(W, V_ref)
        sanger_results.append({"eta": eta, "subspace_alignment_to_svd": round(align, 4),
                               "elapsed_s": round(time.time() - t_s, 1)})
        print("[sanger] eta=%.4f alignment=%.4f elapsed=%.1fs" % (eta, align, time.time() - t_s),
             flush=True)
    rep["ONLINE_SANGER_ETA_CONFIRMATION"] = {
        "scope": "n_sub=%d anchors, d_sub=%d top-frequency context words, k=%d -- a SMALL-SCALE "
                "confirmatory check that the closed-form truncated-SVD used for the PRIMARY C1 result "
                "is the correct fixed point of the streaming Oja/Sanger update swept over eta, NOT a "
                "replacement for the full-scale sweep. Never adopted as a value; sanity range only." % (
                    n_sub, d_sub, K_SANGER),
        "results": sanger_results,
    }

    # =============================== STOP-IF EVALUATION (per the pre-reg, verbatim conditions) ========
    def band_of(arm: str) -> str:
        return next(d["band"] for d in comp_vs_a0 if d["arm"] == arm)

    def delta_of(arm: str) -> float:
        return next(d["delta_point"] for d in comp_vs_a0 if d["arm"] == arm)

    c1_band = band_of("C1_LEARNED_BASIS")
    c1_moves = c1_band != "NOT_SEPARATED" and delta_of("C1_LEARNED_BASIS") < 0   # BELOW = no-relation FALLS
    c1_rand_ctrl_band = band_of("C1_CTRL_MATCHED_RANK_RANDOM")
    c1_freq_ctrl_band = band_of("C1_CTRL_FREQUENCY_SHUFFLED")
    c1_beats_rand_ctrl = c1_moves and c1_rand_ctrl_band == "NOT_SEPARATED"
    c1_beats_freq_ctrl = c1_moves and c1_freq_ctrl_band == "NOT_SEPARATED"
    c1_beats_both_controls = c1_beats_rand_ctrl and c1_beats_freq_ctrl

    c1_acc_margin = margins_vs_a0["C1_LEARNED_BASIS"]
    c1_accuracy_wins = c1_acc_margin["band"] == "ABOVE"
    c1_rand_ctrl_acc_margin = margins_vs_a0["C1_CTRL_MATCHED_RANK_RANDOM"]
    matched_rank_matches_c1_accuracy = c1_rand_ctrl_acc_margin["band"] != "BELOW" and abs(
        c1_rand_ctrl_acc_margin["point"] - c1_acc_margin["point"]) < 2 * max(
        ci_halfwidth.get("C1_CTRL_MATCHED_RANK_RANDOM", 0.02), ci_halfwidth.get("C1_LEARNED_BASIS", 0.02))

    c2_band = band_of("C2_WRITE_TIME_DIVISIVE_NORM")
    c2_moves = c2_band != "NOT_SEPARATED" and delta_of("C2_WRITE_TIME_DIVISIVE_NORM") < 0
    c2_wrongpool_band = band_of("C2_CTRL_WRONGPOOL")
    c2_idf_band = band_of("C2_CTRL_PURE_IDF")
    c2_beats_controls = c2_moves and c2_wrongpool_band == "NOT_SEPARATED" and c2_idf_band == "NOT_SEPARATED"

    stop_if: List[str] = []
    if c1_moves and c1_beats_both_controls:
        stop_if.append("(i) C1_LEARNED_BASIS moves composition CI-separated AND beats both its "
                       "controls -- THE LEARNED BASIS IS THE MISSING OPERATION.")
    if c1_accuracy_wins and (not c1_moves or matched_rank_matches_c1_accuracy):
        stop_if.append("(ii) C1_LEARNED_BASIS beats A0 on accuracy but NOT on composition, or the "
                       "matched-rank random control matches its accuracy gain -- A DIMENSIONALITY OR "
                       "RANKING RESULT, NOT A RELATION RESULT. Claim no mechanism.")
    if c2_moves and c2_beats_controls and not (c1_moves and c1_beats_both_controls):
        stop_if.append("(iii) C2 moves composition where C1 does not -- THE MISSING INGREDIENT IS THE "
                       "DENOMINATOR, NOT THE LEARNED BASIS. Winning config: %r. PPMI is a known "
                       "classical result being RE-DERIVED here, not invented; credited to Church & "
                       "Hanks / Levy & Goldberg." % c2_win)
    if not c1_moves and not c2_moves:
        stop_if.append("(iv) NEITHER C1 nor C2 moves composition -- CODE IS EXONERATED AS THE PRIME "
                       "SUSPECT; the organ's defect is elsewhere. This is a valuable negative.")
    rep["STOP_IF_FIRED"] = stop_if if stop_if else ["NONE of (i)-(iv) fired on the strict bands above "
                                                     "-- see COMPOSITION_DELTA_VS_A0 for the raw numbers"]
    rep["STOP_IF_DIAGNOSTIC_FLAGS"] = {
        "c1_moves_composition_toward_relation": c1_moves, "c1_band": c1_band,
        "c1_beats_matched_rank_random_control": c1_beats_rand_ctrl,
        "c1_beats_frequency_shuffled_control": c1_beats_freq_ctrl,
        "c1_accuracy_margin_vs_a0": c1_acc_margin,
        "matched_rank_random_matches_c1_accuracy": matched_rank_matches_c1_accuracy,
        "c2_moves_composition_toward_relation": c2_moves, "c2_band": c2_band,
        "c2_beats_wrongpool_and_pureidf_controls": c2_beats_controls,
        "c2_accuracy_margin_vs_a0": margins_vs_a0["C2_WRITE_TIME_DIVISIVE_NORM"],
    }

    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print("[cfg] mode=%s N_BOOT=%d K_GRID_C1=%r C2_SIGMA=%r C2_N=%r C2_POOL=%r out=%s" % (
        RUN_MODE, N_BOOT, K_GRID_C1, C2_SIGMA_GRID, C2_N_GRID, C2_POOL_GRID, out_dir), flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    flags = rep.get("STOP_IF_DIAGNOSTIC_FLAGS", {})
    if flags.get("c1_moves_composition_toward_relation") and flags.get(
            "c1_beats_matched_rank_random_control") and flags.get("c1_beats_frequency_shuffled_control"):
        verdict_tag = "C1_LEARNED_BASIS_IS_THE_MISSING_OPERATION"
    elif flags.get("c2_moves_composition_toward_relation") and flags.get(
            "c2_beats_wrongpool_and_pureidf_controls"):
        verdict_tag = "C2_DENOMINATOR_IS_THE_MISSING_INGREDIENT"
    elif not flags.get("c1_moves_composition_toward_relation") and not flags.get(
            "c2_moves_composition_toward_relation"):
        verdict_tag = "CODE_EXONERATED__NEITHER_ARM_MOVES_COMPOSITION"
    else:
        verdict_tag = "MIXED__SEE_STOP_IF_FIRED"
    verdict = "WRITERULE_CODE_GATE__%s__C1_WIN_K_%s__C2_WIN_%s" % (
        verdict_tag, rep.get("C1_WINNING_K"), rep.get("C2_WINNING_CONFIG", {}).get("pool"))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ORGAN A CODE gate: does a LEARNED basis (Oja/Sanger closed-form = truncated SVD) or a "
            "WRITE-TIME DENOMINATOR (Carandini-Heeger divisive / PPMI) move winner COMPOSITION where "
            "the incumbent random projection measured +0.0031 NOT_SEPARATED. -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT,
                  "N_PROBE_COMPOSITION": N_PROBE_COMPOSITION, "ADDRESS_EXACT_MIN": ADDRESS_EXACT_MIN,
                  "K_GRID_C1": list(K_GRID_C1), "C2_SIGMA_GRID": list(C2_SIGMA_GRID),
                  "C2_N_GRID": list(C2_N_GRID), "C2_POOL_GRID": list(C2_POOL_GRID),
                  "C2_PROJECT_K": C2_PROJECT_K},
        "selftest_evidence_keys": sorted(ev.keys()),
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print("[verdict] %s" % verdict, flush=True)
    print("[done] %.0fs -> %s/metrics.json" % (time.time() - t_start, out_dir), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(3)
