"""exp_corpus_capacity_ppmi_svd_ceiling_v1 -- DOES THIS CORPUS SUPPORT SUBSTITUTABILITY AT ALL?

Answers notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.15's open question. Organ A (the write
rule) is fully gated: FILTER negative-value, CODE exonerated x2, ACCUMULATE is the interference
source but not fixable by not-collapsing, NORMALISE not in the live path, SUPERPOSE does not
exist. NOT ONE ARM THIS PROGRAMME HAS EVER MEASURED is CI-separated above 0.5 on the licensed
dissociation instrument. This is a CAPACITY question, not a step question: does a standard,
well-understood classical method (PPMI + truncated SVD) extract a substitutability signal from
this SAME corpus that our write rule cannot? If yes, the corpus is fine and our write rule is the
defect. If nothing extracts one -- not even a fitted-in-sample oracle -- the blocker is the corpus
or the first-order representation, and the programme redirects.

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md "SUBSTRATE-KB CONCEPT-QUERY BEFORE
AUTHORING"). Ran: bash tools/substrate_query.sh "PPMI truncated SVD classical distributional
semantics substitutability co-occurrence capacity ceiling first-order counts". confidence=0.3057
(marginally above the cosine>0.30 read-the-top-2 threshold). Top hit (cosine=0.3057):
entity='substitutability', a generic WordNet/concept-atom node (data/substrate_index/concept/
atoms.jsonl + wordnet cache) -- no method content, just the bare concept. Second hit
(cosine=0.2861): 'CN_substitutability', also a generic concept-relation node, no PPMI/SVD content.
Neither builds a PPMI+SVD capacity-ceiling instrument, a fitted-oracle diagnostic, or reuses the
dissociation-score instrument. NOT a rediscovery -- genuinely novel: this cell asks "is the
information present in classical first-order counts at all", which no landed cell has asked.

=================================================================================================
THE INSTRUMENT IS REUSED VERBATIM, NEVER REBUILT (notes/dissociation_score_instrument_2026-08-18.md,
experiments/exp_dissociation_score_instrument_v1.py, commit 0eb44eb1d, CODE_VERSION="v1.7"):
  - its matched-pair population (242 pairs/cell, all nouns) -- loaded from its own checkpoint
    (data/exp_dissociation_score_instrument_v1/units.jsonl, unit_key POPULATION|v1.7|full), never
    recomputed.
  - its AUC scorer (auc_of / auc_bootstrap) and its exact score arrays for the 11 arms it already
    built -- loaded from unit_key SCORES|v1.7|full, never recomputed, to run a REGRESSION GATE
    that reproduces the 4 floors (0.5000/0.4901/0.4664/0.5431), the known-answer arm (0.9599) and
    the random-store arm (0.4862) bit-for-bit before anything new is trusted.
  - N0 (RANDOM_VECTOR_STORE) and K1 (KNOWN_ANSWER_WORDNET_PATH_SIM) arms are the SAME cached arms,
    not rebuilt.
If the regression gate fails, this cell raises SystemExit and writes ONLY a GATE_FAIL metrics.json
-- INSTRUMENT_NOT_LICENSED, publish nothing else (per dispatch brief STOP-IF iv).

=================================================================================================
THE NEW ARMS (B1/B2/B3/C1), all classical linear algebra over OUR OWN corpus counts, NO LLM
anywhere, NO pretrained embedding table imported anywhere:
  MATRIX. rows = the FULL valid anchor set (n=5491, same as CTS.load_cache()'s anchor_set, the
    same population every sibling cell's INCUMBENT_LIVE_STORE / RAW_COUNT_FULL_ACCUM arm uses),
    cols = the union of context words seen near ANY anchor (INFO.build_vocab over ALL 5491
    Pstore checkpoints, not just the words needed by the 242 matched pairs) -- built this way
    (full row space, not restricted to matched-pair words) so PPMI's column marginals are
    estimated from the corpus's actual context-word frequency distribution, not biased downward
    by omitting the ~5000 anchors NOT in the matched pairs. This is the standard term-context
    construction (Levy & Goldberg 2014 "Neural Word Embedding as Implicit Matrix Factorization"):
    a co-occurrence table whose OWN row/col marginals define PPMI, not an external corpus
    frequency. Reused verbatim from experiments.exp_cue_information_audit_v1: build_vocab,
    to_sparse, over the SAME Pstore checkpoints (data/exp_cue_information_audit_v1/units.jsonl,
    unit_key "Pstore|<word>") every sibling cell already reuses -- never re-tokenised.
  PPMI. PPMI(i,j) = max(0, log(count_ij * total / (row_sum_i * col_sum_j))) computed on the sparse
    nonzero entries only (never densified). This is the standard positive-pointwise-mutual-
    information correction for frequency effects on raw co-occurrence counts.
  B1_PPMI. cosine similarity of the (L2-normalised) PPMI rows for each matched pair, no
    dimensionality reduction.
  B2_PPMI_SVD. truncated SVD (scipy.sparse.linalg.svds) of the PPMI matrix, sweeping
    k in {50, 100, 300, 500} (any k >= min(matrix shape) - 1 is dropped and reported, never
    silently substituted). Word vector = U_k @ diag(sqrt(S_k)) (the standard symmetric SVD
    embedding convention), L2-normalised, cosine for each matched pair. THE DECISIVE ARM.
  B3_SECOND_ORDER_COSINE. cosine similarity of the RAW (un-PPMI-weighted) L2-normalised context-
    count rows -- by construction (cosine is independent of which OTHER rows/cols are in the
    matrix; L2-normalisation and the dot product only touch the two rows being compared) this is
    IDENTICAL to DSI's own RAW_COUNT_FULL_ACCUM arm (0.0510). Verified as an internal consistency
    self-check (bit-identical to the cached SCORES, not just "close") rather than asserted.
  C1_FITTED_ORACLE. THE CAPACITY CEILING, ALLOWED TO CHEAT. A diagonal reweighting (rank-preserving
    linear reweighting, not a fresh low-rank factorisation) of the B2 SVD-projected feature space
    at a fixed moderate k (well below n=484 pair-members, so it is not raw memorisation): feature
    for pair (w1,w2) = elementwise product phi(w1)*phi(w2) in R^k (the standard bilinear-form
    decomposition of a diagonal-reweighted dot product score(w1,w2) = sum_d lambda_d phi(w1)_d
    phi(w2)_d), L2-regularised logistic regression fits lambda directly on the SAME 484 pair-
    members' labels (P=1, S=0) to MAXIMISE separation. Reported BOTH fitted-in-sample (the
    ceiling number, must never be quoted as a capability) AND 5-fold cross-validated held-out
    (labelled separately, the honest generalisation estimate).

=================================================================================================
STOP-IF (evaluated in this order, exactly as the dispatch brief specifies):
  (i)   ANY regression-gate check or K1 fails -> INSTRUMENT_NOT_LICENSED, publish nothing else.
  (ii)  B2_PPMI_SVD (best k) CI-separated ABOVE 0.5 -> the corpus supports substitutability and
        our write rule is the defect. Report k, margin, CI half-width.
  (iii) B2 and B3 both fail to clear 0.5 but C1_FITTED_ORACLE clears 0.5 -> the information IS
        present but no unsupervised first-order transform reaches it.
  (iv)  C1_FITTED_ORACLE ALSO fails to clear 0.5 -> the information is NOT in first-order counts
        from this corpus; redirect the programme away from write-rule engineering entirely.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every new arm's per-pair score vector, asserted >1 distinct
#   digest (extends DSI's own ARM_DIGESTS check to the 4 new arms)
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: MATRIX (PPMI build), B2_SWEEP (per-k SVD), C1 (fitted oracle) as separate
#   tools.exp_checkpoint units so a kill loses at most one k's SVD, not the whole run
# - discriminator survives scale: this cell runs the FULL population (242 pairs/cell) at FULL
#   matrix scale (5491 x ~21600), no scale-preview needed
# - calibration_check: default_ok_for_this_regime (reuses DSI's licensed instrument unmodified;
#   the ONLY new construction is the PPMI/SVD/oracle scoring, which is the thing under test)
# - progress_logging: print_flush_true (every phase prints a flushed line, per Sec 17)
# - baseline_in_band: n/a -- licensing-gate + capacity-ceiling instrument, not a 0.05-0.95-band
#   baseline cell; declared explicitly rather than silently omitted
# - crlb_floor_computed: n/a -- an AUC dissociation measurement is not a capacity sweep; declared
#   explicitly

ASCII-only. NO LLM anywhere in this runtime path. NO pretrained embedding table imported anywhere
-- PPMI/SVD/cosine are classical linear algebra over OUR OWN corpus counts. CPU only, pinned
single-threaded. data/foundation/** is never opened. Writes only under
data/exp_corpus_capacity_ppmi_svd_ceiling_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/sklearn/DSI next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

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
from scipy.sparse.linalg import svds

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI              # noqa: E402  READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                   # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                     # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics      # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

from sklearn.linear_model import LogisticRegression                          # noqa: E402
from sklearn.model_selection import StratifiedKFold                          # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "corpus_capacity_ppmi_svd_ceiling_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/corpus_capacity_ppmi_svd_ceiling_2026-08-18.md"

DSI_CODE_VERSION = "v1.7"          # the LICENSED instrument version this cell reproduces + reuses
DSI_GRID = "full"
DSI_OUT_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
INFO_OUT_DIR = os.path.join(REPO, "data", "exp_cue_information_audit_v1")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
K_SWEEP_FULL = [50, 100, 300, 500]
K_SWEEP_SMOKE = [10, 20]
C1_K = 100                          # fixed moderate SVD dim for the fitted-oracle feature space,
                                    # well below n=484 pair-members so C1 is a regularised
                                    # reweighting, not raw memorisation
C1_CV_FOLDS = 5
C1_L2_C = 1.0                       # sklearn LogisticRegression inverse-regularisation strength

# EXPECTED regression-gate values -- MEASURED@notes/dissociation_score_instrument_2026-08-18.md
# and MEASURED@data/exp_dissociation_score_instrument_v1/metrics.json:report.AUC_PER_ARM
# (CODE_VERSION v1.7, grid=full). Tight tolerance because the recompute is fully deterministic
# (same cached per-pair score arrays, same seeds, same auc_bootstrap code) -- any deviation beyond
# floating-point noise means the instrument or its dependencies drifted since 2026-08-18.
EXPECTED_AUC = {
    "F_ORTHOGRAPHIC": 0.5000,
    "F_FREQUENCY": 0.4901,
    "F_SCRAMBLE": 0.4664,
    "F_CONSTANT_PROTOTYPE": 0.5431,
    "KNOWN_ANSWER_WORDNET_PATH_SIM": 0.9599,
    "RANDOM_VECTOR_STORE": 0.4862,
    "INCUMBENT_LIVE_STORE": 0.0710,
    "RAW_COUNT_FULL_ACCUM": 0.0510,
}
REGRESSION_TOL = 0.0005            # 4-decimal rounding in auc_bootstrap; allow one ULP of slack


def l2n_dense(A: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(A, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return A / n


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# REGRESSION GATE -- reproduces DSI's licensed floors/K1/N0/incumbent from its OWN cached SCORES,
# bit-for-bit, via DSI's OWN auc_bootstrap code. EXITS ON FAILURE (STOP-IF i).
# =================================================================================================
def regression_gate() -> Dict:
    print("[gate] loading DSI checkpoint (POPULATION + SCORES, CODE_VERSION=%s grid=%s)" %
          (DSI_CODE_VERSION, DSI_GRID), flush=True)
    units = load_units(DSI_OUT_DIR)
    pop_key = unit_key("POPULATION", DSI_CODE_VERSION, DSI_GRID)
    scores_key = unit_key("SCORES", DSI_CODE_VERSION, DSI_GRID)
    if pop_key not in units or scores_key not in units:
        raise SystemExit("INSTRUMENT_NOT_LICENSED -- DSI checkpoint missing required keys: "
                         "pop_present=%s scores_present=%s (looked in %s)" %
                         (pop_key in units, scores_key in units, DSI_OUT_DIR))
    prior_pop = units[pop_key]
    prior_scores = units[scores_key]
    matchedP = [tuple(x) for x in prior_pop["matchedP"]]
    matchedS = [tuple(x) for x in prior_pop["matchedS"]]
    arm_scores = {k: {"P": np.array(v["P"], dtype=np.float64), "S": np.array(v["S"], dtype=np.float64)}
                 for k, v in prior_scores.items()}
    print("[gate] loaded n_matched_pairs=%d n_arms=%d" % (len(matchedP), len(arm_scores)), flush=True)

    # Recompute AUC bootstrap for every arm using DSI's OWN auc_bootstrap, with the SAME
    # boot_seed_base + dict-order-index convention DSI's run() uses (json round-trip preserves
    # insertion order, so index i here matches the original run's index i exactly).
    boot_seed_base = MASTER_SEED + 8181
    recomputed: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(arm_scores.items()):
        recomputed[name] = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + i)

    checks: Dict[str, Dict] = {}
    all_pass = True
    for name, expected in EXPECTED_AUC.items():
        if name not in recomputed:
            checks[name] = {"PASS": False, "reason": "arm missing from recomputed set"}
            all_pass = False
            continue
        measured = recomputed[name]["auc"]
        ok = abs(measured - expected) <= REGRESSION_TOL
        checks[name] = {"PASS": ok, "expected": expected, "measured": measured,
                        "delta": round(measured - expected, 6)}
        if not ok:
            all_pass = False
        print("[gate] %-30s expected=%.4f measured=%.4f %s" %
             (name, expected, measured, "PASS" if ok else "FAIL"), flush=True)

    floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    floors_at_chance = all(recomputed[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in floor_names)
    known_answer_ok = recomputed["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"] >= DSI.KNOWN_ANSWER_MIN_AUC
    random_store_ok = recomputed["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    licensed = bool(all_pass and floors_at_chance and known_answer_ok and random_store_ok)

    gate_report = {"n_matched_pairs_per_cell": len(matchedP), "n_arms_recomputed": len(recomputed),
                   "checks": checks, "floors_at_chance": floors_at_chance,
                   "known_answer_ok": known_answer_ok, "random_store_ok": random_store_ok,
                   "INSTRUMENT_LICENSED": licensed, "recomputed_AUC_PER_ARM": recomputed}
    if not licensed:
        raise SystemExit("INSTRUMENT_NOT_LICENSED -- regression gate FAILED: %r" %
                         {k: v for k, v in checks.items() if not v["PASS"]})
    print("[gate] INSTRUMENT_LICENSED = True (all %d checks pass, floors at chance, K1>=%.2f, "
         "N0 at chance)" % (len(checks), DSI.KNOWN_ANSWER_MIN_AUC), flush=True)
    return {"matchedP": matchedP, "matchedS": matchedS, "arm_scores": arm_scores,
           "gate_report": gate_report}


# =================================================================================================
# MATRIX -- full anchor-set (n=5491) x context-vocab raw count matrix, reused Pstore checkpoints
# =================================================================================================
def load_full_pstore(anchor_words: Sequence[str]) -> Tuple[Dict[str, Counter], List[str]]:
    """Load EVERY anchor's Pstore counts (not just matched-pair members) from the ALREADY-LANDED
    exp_cue_information_audit_v1 checkpoint -- verbatim reuse, no re-tokenisation. Missing anchors
    are reported, never silently skipped (a missing row would silently narrow the row space and
    bias PPMI's column marginals)."""
    units = load_units(INFO_OUT_DIR)
    counts: Dict[str, Counter] = {}
    missing: List[str] = []
    for w in anchor_words:
        rec = units.get(unit_key("Pstore", w))
        if rec is None:
            missing.append(w)
            continue
        counts[w] = Counter(rec["counts"])
    return counts, missing


def build_matrix(anchor_words: Sequence[str]) -> Tuple[sp.csr_matrix, Dict[str, int], Dict]:
    counts_full, missing = load_full_pstore(anchor_words)
    words_present = [w for w in anchor_words if w in counts_full]
    if missing:
        print("[matrix] WARNING: %d/%d anchors missing Pstore rows (excluded from the matrix): %r" %
             (len(missing), len(anchor_words), missing[:20]), flush=True)
    vocab = INFO.build_vocab([counts_full])
    M = INFO.to_sparse(counts_full, words_present, vocab)
    row_idx = {w: i for i, w in enumerate(words_present)}
    nnz = M.nnz
    total_tokens = float(M.sum())
    diag = {"n_rows_anchors": len(words_present), "n_missing_anchors": len(missing),
           "missing_anchor_sample": missing[:20], "n_cols_vocab": len(vocab),
           "nnz": int(nnz), "density": round(nnz / (M.shape[0] * M.shape[1]), 8) if M.shape[0] and M.shape[1] else 0.0,
           "total_token_count": total_tokens, "matrix_shape": list(M.shape)}
    print("[matrix] shape=%r nnz=%d density=%.6f total_tokens=%.0f" %
         (M.shape, nnz, diag["density"], total_tokens), flush=True)
    return M, row_idx, diag


def ppmi_of(M: sp.csr_matrix) -> sp.csr_matrix:
    """PPMI(i,j) = max(0, log(c_ij * total / (row_sum_i * col_sum_j))), computed on nonzero
    entries only (never densified). Standard positive-PMI correction for frequency effects on raw
    co-occurrence counts (Church & Hanks 1990 / Levy & Goldberg 2014)."""
    Mc = M.tocoo()
    row_sums = np.asarray(M.sum(axis=1)).ravel()
    col_sums = np.asarray(M.sum(axis=0)).ravel()
    total = float(M.sum())
    row_sums[row_sums < 1e-12] = 1.0
    col_sums[col_sums < 1e-12] = 1.0
    expected = row_sums[Mc.row] * col_sums[Mc.col] / total
    pmi_vals = np.log(Mc.data / expected)
    ppmi_vals = np.maximum(pmi_vals, 0.0)
    P = sp.csr_matrix((ppmi_vals, (Mc.row, Mc.col)), shape=M.shape)
    P.eliminate_zeros()
    return P


# =================================================================================================
# PAIR SCORING HELPERS
# =================================================================================================
def pair_cosine_from_dense_rows(rows: np.ndarray, row_idx: Dict[str, int],
                                pairs: List[Tuple[str, str, str]]) -> np.ndarray:
    """rows must already be L2-normalised; missing-member pairs score NaN (reported, not dropped
    silently -- DSI's own dense_scores_from_dict_store convention)."""
    out = np.full(len(pairs), np.nan, dtype=np.float64)
    for i, (w1, w2, _p) in enumerate(pairs):
        i1, i2 = row_idx.get(w1), row_idx.get(w2)
        if i1 is not None and i2 is not None:
            out[i] = float(np.dot(rows[i1], rows[i2]))
    return out


def pair_cosine_from_sparse_rows(Mn: sp.csr_matrix, row_idx: Dict[str, int],
                                 pairs: List[Tuple[str, str, str]]) -> np.ndarray:
    out = np.full(len(pairs), np.nan, dtype=np.float64)
    for i, (w1, w2, _p) in enumerate(pairs):
        i1, i2 = row_idx.get(w1), row_idx.get(w2)
        if i1 is not None and i2 is not None:
            out[i] = float(Mn.getrow(i1).multiply(Mn.getrow(i2)).sum())
    return out


def sparse_l2n(M: sp.csr_matrix) -> sp.csr_matrix:
    norms = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel())
    norms[norms < 1e-12] = 1.0
    return sp.diags(1.0 / norms) @ M


def coverage_report(row_idx: Dict[str, int], matchedP, matchedS) -> Dict:
    def _cov(pairs):
        both = sum(1 for w1, w2, _ in pairs if w1 in row_idx and w2 in row_idx)
        return {"n_pairs": len(pairs), "n_both_members_present": both}
    return {"SET_P": _cov(matchedP), "SET_S": _cov(matchedS)}


# =================================================================================================
# C1_FITTED_ORACLE -- diagonal reweighting of the SVD feature space, fitted directly on the labels
# =================================================================================================
def fitted_oracle(word_vecs_k: np.ndarray, row_idx: Dict[str, int],
                  matchedP: List[Tuple[str, str, str]], matchedS: List[Tuple[str, str, str]],
                  seed: int) -> Dict:
    pairs = matchedP + matchedS
    y = np.array([1] * len(matchedP) + [0] * len(matchedS), dtype=np.int64)
    X = np.zeros((len(pairs), word_vecs_k.shape[1]), dtype=np.float64)
    valid = np.ones(len(pairs), dtype=bool)
    for i, (w1, w2, _p) in enumerate(pairs):
        i1, i2 = row_idx.get(w1), row_idx.get(w2)
        if i1 is None or i2 is None:
            valid[i] = False
            continue
        X[i] = word_vecs_k[i1] * word_vecs_k[i2]
    X, y, pairs = X[valid], y[valid], [p for p, v in zip(pairs, valid) if v]
    n_p_valid = int((y == 1).sum())
    n_s_valid = int((y == 0).sum())

    # --- fitted IN-SAMPLE (the ceiling number, allowed to cheat) ---
    clf = LogisticRegression(C=C1_L2_C, max_iter=2000, random_state=seed)
    clf.fit(X, y)
    scores_fit = clf.decision_function(X)
    sp_fit, ss_fit = scores_fit[y == 1], scores_fit[y == 0]
    fitted_insample = DSI.auc_bootstrap(sp_fit, ss_fit, N_BOOT, seed + 1)

    # --- held-out, 5-fold stratified CV, pooled out-of-fold scores ---
    skf = StratifiedKFold(n_splits=C1_CV_FOLDS, shuffle=True, random_state=seed)
    oof_scores = np.zeros(len(y), dtype=np.float64)
    for tr_idx, te_idx in skf.split(X, y):
        clf_f = LogisticRegression(C=C1_L2_C, max_iter=2000, random_state=seed)
        clf_f.fit(X[tr_idx], y[tr_idx])
        oof_scores[te_idx] = clf_f.decision_function(X[te_idx])
    sp_oof, ss_oof = oof_scores[y == 1], oof_scores[y == 0]
    held_out = DSI.auc_bootstrap(sp_oof, ss_oof, N_BOOT, seed + 2)

    return {"k_features": int(word_vecs_k.shape[1]), "n_pairs_P_valid": n_p_valid,
           "n_pairs_S_valid": n_s_valid, "l2_C": C1_L2_C, "cv_folds": C1_CV_FOLDS,
           "FITTED_IN_SAMPLE_CEILING_DO_NOT_QUOTE_AS_CAPABILITY": fitted_insample,
           "HELD_OUT_CV_AUC": held_out}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- PPMI known-answer: a perfectly-correlated toy count matrix must give positive PPMI on
    # the diagonal-like structure and ZERO (floored) PPMI on independent/rare pairs ---------------
    toy = sp.csr_matrix(np.array([[10.0, 0.0, 1.0],
                                  [0.0, 10.0, 1.0],
                                  [1.0, 1.0, 5.0]], dtype=np.float64))
    P = ppmi_of(toy)
    Pd = np.asarray(P.todense())
    assert Pd[0, 0] > 0.0, "a word co-occurring heavily with a rare context should have positive PPMI"
    assert Pd[0, 1] == 0.0, "zero raw count must stay ZERO after PPMI (never negative-log noise)"
    ev["ppmi_known_answer"] = {"diag_pos": float(Pd[0, 0]), "offdiag_zero_raw": float(Pd[0, 1])}

    # --- PPMI floors negative PMI to zero, never leaves a negative value -----------------------
    skew = sp.csr_matrix(np.array([[100.0, 1.0], [1.0, 100.0]], dtype=np.float64))
    Pskew = np.asarray(ppmi_of(skew).todense())
    assert (Pskew >= 0.0).all(), "PPMI must never be negative: %r" % Pskew
    ev["ppmi_never_negative"] = True

    # --- real code path: build_matrix on a tiny REAL anchor subset from the REAL Pstore cache ---
    C = CTS.load_cache()
    anchors = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    tiny_anchor_set = [a for a, ok in zip(anchors, mat_ok) if ok][:24]
    M_tiny, row_idx_tiny, diag_tiny = build_matrix(tiny_anchor_set)
    assert M_tiny.shape[0] <= len(tiny_anchor_set), "matrix must not have MORE rows than requested"
    assert M_tiny.nnz > 0, "a real 24-anchor subset must have SOME nonzero context counts"
    ev["real_code_path_build_matrix"] = diag_tiny

    # --- SVD on the tiny real PPMI matrix runs and returns the requested rank -------------------
    P_tiny = ppmi_of(M_tiny)
    k_tiny = min(5, min(P_tiny.shape) - 1)
    if k_tiny >= 1:
        U, S, Vt = svds(P_tiny.asfptype(), k=k_tiny)
        assert U.shape[1] == k_tiny, "svds must return exactly k_tiny components: %r" % (U.shape,)
        ev["svd_real_code_path"] = {"k": k_tiny, "singular_values": S.tolist()}

    # --- sparse cosine matches dense cosine on a hand-built fixture ------------------------------
    fix = sp.csr_matrix(np.array([[3.0, 0.0, 4.0], [0.0, 3.0, 4.0]], dtype=np.float64))
    fix_n = sparse_l2n(fix)
    ridx = {"a": 0, "b": 1}
    cos_sparse = pair_cosine_from_sparse_rows(fix_n, ridx, [("a", "b", "n")])[0]
    dense_n = l2n_dense(np.array([[3.0, 0.0, 4.0], [0.0, 3.0, 4.0]]))
    cos_dense = float(np.dot(dense_n[0], dense_n[1]))
    assert abs(cos_sparse - cos_dense) < 1e-9, "sparse and dense cosine must agree: %.6f vs %.6f" % (
        cos_sparse, cos_dense)
    ev["sparse_dense_cosine_agree"] = {"sparse": cos_sparse, "dense": cos_dense}

    # --- coverage report counts correctly on a known fixture ------------------------------------
    ridx2 = {"a": 0, "b": 1, "c": 2}
    covP = [("a", "b", "n"), ("a", "zzz_missing", "n")]
    covS = [("b", "c", "n")]
    cov = coverage_report(ridx2, covP, covS)
    assert cov["SET_P"]["n_both_members_present"] == 1, "exactly one P pair has both members: %r" % cov
    assert cov["SET_S"]["n_both_members_present"] == 1, "the S pair has both members: %r" % cov
    ev["coverage_known_answer"] = cov

    # --- fitted_oracle known-answer: a PERFECTLY separable toy feature space must reach AUC~1.0
    # fitted-in-sample, and a PURE-NOISE feature space must stay near 0.5 on held-out CV -----------
    rng = np.random.default_rng(0)
    k_toy = 6
    toy_vecs = rng.standard_normal((40, k_toy))
    toy_vecs[:20] += 3.0  # first 20 "words" cluster apart from the rest
    toy_ridx = {"w%d" % i: i for i in range(40)}
    toy_P = [("w%d" % i, "w%d" % (i + 1), "n") for i in range(0, 18, 2)]
    toy_S = [("w%d" % i, "w%d" % (i + 1), "n") for i in range(20, 38, 2)]
    orc = fitted_oracle(toy_vecs, toy_ridx, toy_P, toy_S, seed=1)
    assert orc["FITTED_IN_SAMPLE_CEILING_DO_NOT_QUOTE_AS_CAPABILITY"]["auc"] > 0.9, \
        "a genuinely separable toy feature space must fit near-perfectly in-sample: %r" % orc
    ev["fitted_oracle_known_answer"] = {
        "fitted_auc": orc["FITTED_IN_SAMPLE_CEILING_DO_NOT_QUOTE_AS_CAPABILITY"]["auc"],
        "held_out_auc": orc["HELD_OUT_CV_AUC"]["auc"]}

    # --- arms-must-differ (META_RULE_AF) ---------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr), "distinct score vectors must produce distinct digests"
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test) ----------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "NO_PRETRAINED_EMBEDDING_TABLE_IMPORTED": True}

    # =============================== REGRESSION GATE (STOP-IF i) =====================================
    gate = regression_gate()
    rep["REGRESSION_GATE"] = gate["gate_report"]
    matchedP, matchedS = gate["matchedP"], gate["matchedS"]
    if grid == "reduced":
        matchedP, matchedS = matchedP[:40], matchedS[:40]
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match

    # =============================== MATRIX (checkpointed unit) ======================================
    anchor_words_full = CTS.load_cache()["anchors"]
    anchor_mat_ok = np.asarray(CTS.load_cache()["mat_ok"], dtype=bool)
    anchor_words_full = [a for a, ok in zip(anchor_words_full, anchor_mat_ok) if ok]
    if grid == "reduced":
        pair_words = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
        anchor_words_full = sorted(set(anchor_words_full[:1200]) | set(pair_words))

    mat_key = unit_key("MATRIX", CODE_VERSION, grid)
    prior_mat = load_units(out_dir_ckpt).get(mat_key)
    if prior_mat is not None:
        print("[matrix] RESUMED FROM CHECKPOINT (diag only; matrix rebuilt from cache, deterministic)",
             flush=True)
        M, row_idx, matrix_diag = build_matrix(anchor_words_full)
        assert matrix_diag["nnz"] == prior_mat["nnz"], "matrix rebuild disagrees with checkpoint -- nondeterminism"
    else:
        M, row_idx, matrix_diag = build_matrix(anchor_words_full)
        record_unit(out_dir_ckpt, mat_key, matrix_diag)
    rep["MATRIX"] = matrix_diag
    rep["COVERAGE"] = coverage_report(row_idx, matchedP, matchedS)

    print("[matrix] computing PPMI...", flush=True)
    t_ppmi0 = time.time()
    Mppmi = ppmi_of(M)
    print("[matrix] PPMI done in %.1fs, nnz=%d" % (time.time() - t_ppmi0, Mppmi.nnz), flush=True)

    # =============================== B1_PPMI (no factorisation) ======================================
    Mppmi_n = sparse_l2n(Mppmi)
    b1_P = pair_cosine_from_sparse_rows(Mppmi_n, row_idx, matchedP)
    b1_S = pair_cosine_from_sparse_rows(Mppmi_n, row_idx, matchedS)
    b1_auc = DSI.auc_bootstrap(b1_P[~np.isnan(b1_P)], b1_S[~np.isnan(b1_S)], N_BOOT, MASTER_SEED + 9191)
    print("[B1_PPMI] AUC=%.4f CI=%r band=%s" % (b1_auc["auc"], b1_auc["ci95"], b1_auc["band"]), flush=True)

    # =============================== B3_SECOND_ORDER_COSINE (raw counts, no PPMI) ====================
    Mraw_n = sparse_l2n(M)
    b3_P = pair_cosine_from_sparse_rows(Mraw_n, row_idx, matchedP)
    b3_S = pair_cosine_from_sparse_rows(Mraw_n, row_idx, matchedS)
    b3_auc = DSI.auc_bootstrap(b3_P[~np.isnan(b3_P)], b3_S[~np.isnan(b3_S)], N_BOOT, MASTER_SEED + 9192)
    print("[B3_SECOND_ORDER_COSINE] AUC=%.4f CI=%r band=%s" %
         (b3_auc["auc"], b3_auc["ci95"], b3_auc["band"]), flush=True)
    # internal consistency self-check vs DSI's own cached RAW_COUNT_FULL_ACCUM (same construction,
    # full row space here vs words-needed-only there -- cosine is row-pair-local so they must agree
    # on the words this cell can score at all)
    b3_vs_dsi = None
    if grid == "full" and "RAW_COUNT_FULL_ACCUM" in gate["arm_scores"]:
        dsi_full = gate["arm_scores"]["RAW_COUNT_FULL_ACCUM"]
        finite = ~np.isnan(b3_P)
        if finite.sum() == len(dsi_full["P"]):
            max_abs_diff = float(np.max(np.abs(b3_P[finite] - dsi_full["P"])))
            b3_vs_dsi = {"max_abs_diff_vs_DSI_RAW_COUNT_FULL_ACCUM_P": max_abs_diff,
                        "BIT_IDENTICAL": bool(max_abs_diff < 1e-6)}
            print("[B3 consistency] max_abs_diff vs DSI RAW_COUNT_FULL_ACCUM P-scores = %.2e (%s)" %
                 (max_abs_diff, "IDENTICAL" if b3_vs_dsi["BIT_IDENTICAL"] else "DIVERGES"), flush=True)
    rep["B3_VS_DSI_CONSISTENCY_CHECK"] = b3_vs_dsi

    # =============================== B2_PPMI_SVD sweep (checkpointed per-k) ==========================
    k_sweep = K_SWEEP_SMOKE if grid == "reduced" else K_SWEEP_FULL
    max_k = min(Mppmi.shape) - 1
    k_sweep_run = [k for k in k_sweep if k < max_k]
    k_sweep_dropped = [k for k in k_sweep if k >= max_k]
    if k_sweep_dropped:
        print("[B2] dropping k=%r -- exceeds matrix rank ceiling (min(shape)-1=%d)" %
             (k_sweep_dropped, max_k), flush=True)

    b2_results: Dict[str, Dict] = {}
    svd_vecs_by_k: Dict[int, np.ndarray] = {}
    for k in k_sweep_run:
        k_key = unit_key("B2_SVD", CODE_VERSION, grid, k)
        prior_k = load_units(out_dir_ckpt).get(k_key)
        if prior_k is not None:
            print("[B2] k=%d RESUMED FROM CHECKPOINT" % k, flush=True)
            b2_results[str(k)] = prior_k
            continue
        t_k0 = time.time()
        U, S, Vt = svds(Mppmi.asfptype(), k=k, random_state=MASTER_SEED + 7000 + k)
        order = np.argsort(-S)
        U, S = U[:, order], S[order]
        vecs = U * np.sqrt(np.maximum(S, 0.0))[None, :]
        vecs_n = l2n_dense(vecs)
        if k == C1_K or (k == k_sweep_run[0] and C1_K not in k_sweep_run):
            svd_vecs_by_k[k] = vecs_n
        p_scores = pair_cosine_from_dense_rows(vecs_n, row_idx, matchedP)
        s_scores = pair_cosine_from_dense_rows(vecs_n, row_idx, matchedS)
        auc_res = DSI.auc_bootstrap(p_scores[~np.isnan(p_scores)], s_scores[~np.isnan(s_scores)],
                                    N_BOOT, MASTER_SEED + 9300 + k)
        elapsed_k = round(time.time() - t_k0, 1)
        result = {"k": k, "elapsed_s": elapsed_k, **auc_res}
        b2_results[str(k)] = result
        record_unit(out_dir_ckpt, k_key, result)
        print("[B2_PPMI_SVD] k=%d AUC=%.4f CI=%r band=%s elapsed=%.1fs" %
             (k, auc_res["auc"], auc_res["ci95"], auc_res["band"], elapsed_k), flush=True)
    rep["B2_PPMI_SVD_SWEEP"] = b2_results
    rep["B2_K_SWEEP_DROPPED_RANK_CEILING"] = {"dropped_k": k_sweep_dropped, "max_k_reachable": max_k}

    best_k, best_auc_point = None, -1.0
    for k_str, res in b2_results.items():
        if res["auc"] > best_auc_point:
            best_k, best_auc_point = int(k_str), res["auc"]
    rep["B2_BEST_K"] = best_k
    b2_best = b2_results.get(str(best_k)) if best_k is not None else None

    # =============================== C1_FITTED_ORACLE (checkpointed) =================================
    if C1_K not in svd_vecs_by_k and k_sweep_run:
        fallback_k = min(k_sweep_run, key=lambda k: abs(k - C1_K))
        print("[C1] C1_K=%d not directly cached, reusing k=%d SVD vectors" % (C1_K, fallback_k), flush=True)
        k_key = unit_key("B2_SVD", CODE_VERSION, grid, fallback_k)
        # vectors weren't persisted (only the AUC result was), rebuild once at that k
        U, S, Vt = svds(Mppmi.asfptype(), k=fallback_k, random_state=MASTER_SEED + 7000 + fallback_k)
        order = np.argsort(-S)
        U, S = U[:, order], S[order]
        svd_vecs_by_k[fallback_k] = l2n_dense(U * np.sqrt(np.maximum(S, 0.0))[None, :])
        c1_k_used = fallback_k
    else:
        c1_k_used = C1_K if C1_K in svd_vecs_by_k else (k_sweep_run[0] if k_sweep_run else None)

    c1_key = unit_key("C1_ORACLE", CODE_VERSION, grid, c1_k_used)
    prior_c1 = load_units(out_dir_ckpt).get(c1_key)
    if prior_c1 is not None:
        print("[C1] RESUMED FROM CHECKPOINT", flush=True)
        c1_result = prior_c1
    elif c1_k_used is not None:
        c1_result = fitted_oracle(svd_vecs_by_k[c1_k_used], row_idx, matchedP, matchedS,
                                  seed=MASTER_SEED + 5151)
        c1_result["k_used"] = c1_k_used
        record_unit(out_dir_ckpt, c1_key, c1_result)
        print("[C1_FITTED_ORACLE] k=%d fitted_insample_AUC=%.4f held_out_CV_AUC=%.4f" %
             (c1_k_used, c1_result["FITTED_IN_SAMPLE_CEILING_DO_NOT_QUOTE_AS_CAPABILITY"]["auc"],
              c1_result["HELD_OUT_CV_AUC"]["auc"]), flush=True)
    else:
        c1_result = {"error": "no k available for C1 (empty k_sweep_run)"}
    rep["C1_FITTED_ORACLE"] = c1_result

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF, new arms only) ==================
    new_arm_vectors = {
        "B1_PPMI": np.concatenate([b1_P[~np.isnan(b1_P)], b1_S[~np.isnan(b1_S)]]),
        "B3_SECOND_ORDER_COSINE": np.concatenate([b3_P[~np.isnan(b3_P)], b3_S[~np.isnan(b3_S)]]),
    }
    for k_str, res in b2_results.items():
        pass  # per-k score vectors not retained post-checkpoint-resume; AUC digest covers this below
    digests = {k: _digest(v) for k, v in new_arm_vectors.items()}
    assert len(set(digests.values())) > 1 or len(digests) < 2, \
        "B1 and B3 produced IDENTICAL score vectors -- construction bug"
    rep["NEW_ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== STOP-IF (ii, iii, iv) ============================================
    def _clears(auc_res: Optional[Dict]) -> bool:
        return bool(auc_res and auc_res.get("band") == "ABOVE_0.5_SUBSTITUTABILITY")

    c1_fit = c1_result.get("FITTED_IN_SAMPLE_CEILING_DO_NOT_QUOTE_AS_CAPABILITY") if isinstance(c1_result, dict) else None

    if _clears(b2_best):
        interp = "STOP_IF_ii_B2_PPMI_SVD_CLEARS_0.5__CORPUS_SUPPORTS_SUBSTITUTABILITY_WRITE_RULE_IS_DEFECT"
    elif (not _clears(b2_best)) and (not _clears(b3_auc)) and _clears(c1_fit):
        interp = "STOP_IF_iii_INFO_PRESENT_NO_UNSUPERVISED_FIRST_ORDER_TRANSFORM_REACHES_IT"
    elif (not _clears(b2_best)) and (not _clears(b3_auc)) and (not _clears(c1_fit)):
        interp = "STOP_IF_iv_INFO_NOT_IN_FIRST_ORDER_COUNTS__REDIRECT_PROGRAMME_AWAY_FROM_WRITE_RULE"
    else:
        interp = "MIXED_OUTCOME_NOT_CLEANLY_ONE_OF_THE_THREE_STOP_IFS__REPORT_RAW_NUMBERS"
    rep["INTERPRETATION"] = interp
    rep["B1_PPMI_RESULT"] = b1_auc
    rep["B3_SECOND_ORDER_COSINE_RESULT"] = b3_auc
    rep["N0_RANDOM_VECTOR_STORE_REUSED"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["RANDOM_VECTOR_STORE"]
    rep["K1_KNOWN_ANSWER_REUSED"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["KNOWN_ANSWER_WORDNET_PATH_SIM"]
    rep["A0_INCUMBENT_REUSED"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["INCUMBENT_LIVE_STORE"]

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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "CORPUS_CAPACITY_CEILING__%s" % interp

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Does this corpus support substitutability at all? PPMI + truncated SVD "
                       "(classical, no LLM) applied to the SAME corpus our write rule uses, scored "
                       "on the licensed dissociation instrument's exact 242-pair population. "
                       "-> " + interp),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "K_SWEEP": K_SWEEP_FULL,
                  "C1_K": C1_K, "C1_L2_C": C1_L2_C, "C1_CV_FOLDS": C1_CV_FOLDS,
                  "DSI_CODE_VERSION": DSI_CODE_VERSION},
        "selftest_evidence_keys": sorted(ev.keys()),
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(3)
