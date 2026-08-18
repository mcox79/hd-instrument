"""exp_tuned_count_unsupervised_dissociation_v1 -- DOES A PROPERLY TUNED, FULLY UNSUPERVISED COUNT
METHOD CLEAR 0.5 ON THE LICENSED DISSOCIATION INSTRUMENT?

THIS CELL EXISTS TO TRY TO FALSIFY THE DIRECTOR'S OWN HEADLINE (plan sec 6.18), not to confirm it.

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md "SUBSTRATE-KB CONCEPT-QUERY BEFORE
AUTHORING"). Ran (live, `tools/substrate_query.sh`, `tools/director_kb_query.py --schema-version v2
--tau 0.15 --k 5`) with the query "tuned count PPMI shifted SVD context distribution smoothing
subsampling SGNS matches unsupervised". The query is currently very slow on this machine (multiple
concurrent sibling agents in this session -- corpus-capacity, predcoding-on-dissociation,
supervision-drill -- were independently consuming 200MB-5GB+ RSS python processes at query time,
confirmed via `Get-Process python*`), taking 181.4s wall to answer instead of the usual few seconds.
It DID complete and return a real result: confidence=0.2725, BELOW the cosine>0.30 "read-the-top-2"
threshold this project uses. Top hit (cosine=0.2725): entity='unsupervised', a bare WordNet
antonym-of-supervised node, no method content. Hit 2 (0.2676): an unrelated math MEASURED_MECHANISM
about a learned directional-PP/subcat verb-class rule (motion/aspectual patient suppression) -- not
about word embeddings. Hit 3 (0.2676): notes/research_decode_side_lm_improvements_substrate_native_
2026-06-22.md, a chunk on Modified Kneser-Ney discounting for a DIFFERENT substrate (decode-side
concept-token LM smoothing), tangential (both are "count-based frequency correction") but not this
construction. Hits 4-5: an unrelated replay-prioritization math atom and "shifted Gompertz
distribution" (a keyword false-positive on "shifted"). NONE build a context-distribution-smoothed /
shifted-PMI / subsampled count arm on this dissociation instrument. NOT a rediscovery.

SECOND, STRONGER check: this cell is the literal, explicitly-prescribed follow-on to
`notes/what_supervision_the_brain_has_that_we_do_not_error_driven_learning_drill_2026-08-18.md`
(commit 96caca8de), whose section 6 already ran a disk-wide enumeration (148 hdlab/ modules by `ls`,
90/200 capability_registry.jsonl rows by substring, every predictive/contrastive/word2vec-named
data/ directory) specifically hunting for prior tuned-count-method work and found none; its section
8.2 T1_TUNED_COUNT arm is what this cell implements (split into T1/T2/T3/T4 here per the dispatch
brief's finer-grained arm breakdown). `experiments/exp_corpus_capacity_ppmi_svd_ceiling_v1.py` (the
cell whose vanilla PPMI+SVD numbers this cell's T0 regression-gates against) ran its OWN prior-work
check at cosine=0.3057 and found the same absence. Two independent checks, same answer: this
construction has not been built before in this repo.
=================================================================================================

THE OBJECTION UNDER TEST. Levy & Goldberg (2014) proved SGNS implicitly factorises a matrix of PMI
shifted by log(k); Levy, Goldberg & Dagan (2015, TACL) showed a TUNED count method (context-
distribution smoothing alpha=0.75, the shift, eigenvalue weighting p, frequent-word subsampling)
matches SGNS on similarity tasks. The Director's plan sec 6.18 ran ONLY the vanilla, untuned PPMI+SVD
(no smoothing, no shift, no subsampling) and concluded "the classical method fails on our corpus" --
that conclusion is licensed only for the vanilla construction. If a HELD-OUT-SELECTED tuned count
arm clears 0.5 here, the missing thing was hyperparameters, not supervision, and 6.18's headline is
wrong. If tuning helps but nothing clears 0.5, 6.18 survives a fairer test. If tuning does not even
beat vanilla, the tuning literature (established at 1M-100M-token scales) does not transfer to this
corpus (~1.8M tokens).

=================================================================================================
INSTRUMENT -- REUSE VERBATIM, NEVER REBUILT. Same as `exp_corpus_capacity_ppmi_svd_ceiling_v1`
("CAP" below): population from `data/exp_dissociation_score_instrument_v1/units.jsonl`
POPULATION|v1.7|full, scores from SCORES|v1.7|full, `DSI.auc_of`/`auc_bootstrap` reused unmodified.
REGRESSION GATE (exits on failure, publishes ONLY a GATE_FAIL metrics.json): reuses CAP's OWN
`regression_gate()` function verbatim (imported, not copied) -- reproduces DSI's 8 checks (4 floors,
K1=0.9599, N0=0.4862, A0_INCUMBENT=0.0710, RAW_COUNT_FULL_ACCUM=0.0510) to CAP's own tolerance.
ADDITIONALLY, T0 below reproduces CAP's own B2_PPMI_SVD sweep (0.0519/0.0285/0.0230/0.0278 at
k=50/100/300/500) via CAP's OWN `ppmi_of` and CAP's OWN exact seed convention (MASTER_SEED+7000+k
for svds, MASTER_SEED+9300+k for the AUC bootstrap) -- genuine bit-level reproduction, not merely a
cached-value comparison.

ARMS, all UNSUPERVISED (no labels, no fitting on the evaluation pairs), all classical linear algebra
over OUR OWN corpus counts, NO LLM anywhere, NO pretrained embedding table imported:

  T0_VANILLA_PPMI_SVD   Exactly what 6.18 ran (CAP.ppmi_of, k in {50,100,300,500}, U*sqrt(S)).
                        REGRESSION GATE: must match 0.0519/0.0285/0.0230/0.0278 within CAP's own
                        tolerance (0.0005).
  T1_CONTEXT_DISTRIBUTION_SMOOTHING   Raise context marginals to alpha in {0.5, 0.75, 1.0} (1.0 =
                        no smoothing, the internal control that must reduce PMI_alpha to vanilla PMI
                        -- asserted in self_test). alpha=0.75 is Levy et al.'s reported default;
                        SWEPT, never adopted.
  T2_SHIFTED_PPMI       Subtract log(k_shift) before the positive clip, k_shift in {1, 5, 15}
                        (k_shift=1 -> log(1)=0, reduces to vanilla PPMI's floor-at-zero).
  T3_SUBSAMPLING        Frequent-context-word subsampling, approximated at the (already-aggregated)
                        count-matrix level: each column c is scaled by p_keep(c) = min(1,
                        sqrt(t / f_c)), f_c = the column's share of total corpus mass -- this is the
                        matrix-level EXPECTATION of independently subsampling each token occurrence
                        of c in the underlying stream (disclosed approximation; we only have the
                        already-aggregated Pstore counts, not the raw token stream, for this
                        corpus). Marginals (row/col sums, total) are RECOMPUTED on the subsampled
                        matrix before PPMI, not on the raw one. t in {1e-3, 1e-5} plus t=None (off,
                        the internal control).
  T4_BEST_COMBINED      alpha*, k_shift*, t* held-out-selected from T1-T3 respectively, THEN sweep
                        eigenvalue weighting p in {0, 0.5, 1} (vecs = U * S**p; p=0.5 is what T0/CAP
                        already use) x SVD rank k in {50, 300}.
  T5_SGNS_FROM_SCRATCH  ONLY IF CHEAP (guarded, disclosed if skipped). gensim Word2Vec(sg=1,
                        negative=5, sample=1e-5, window=5, min_count=1, epochs=5), vector_size=100
                        (fixed a priori, standard default, never tuned on the 242 pairs), random
                        init, trained on OUR OWN corpus sentences (INFO.load_corpus_and_buckets(),
                        cached, the SAME sentence pool the Pstore counts came from -- NOT restricted
                        to each anchor's profile-only split; disclosed simplification, still 100%
                        within-corpus text). Frozen static table read by cosine lookup at scoring
                        time -- no forward pass at read time, admissible per the owner's Q3 ruling.
                        Reports T5_IN_IN (cue-vector cosine, the primary number) and T5_IN_OUT
                        (cue-vs-outcome geometry, a free bonus diagnostic per drill sec 4.2, not
                        required by this brief but cheap once the model exists).

  K1 / N0                Reused byte-identical from DSI's own cache via CAP.regression_gate()
                        (KNOWN_ANSWER_WORDNET_PATH_SIM=0.9599, RANDOM_VECTOR_STORE=0.4862), never
                        recomputed.

=================================================================================================
HYPERPARAMETER SELECTION WITHOUT TOUCHING THE 242 EVALUATION PAIRS (the trap this cell exists to
avoid: sweeping and reporting the best number ON the eval pairs silently reproduces the fitted
oracle and looks like an unsupervised win).

A HELD-OUT VALIDATION PAIR POPULATION is built by reusing DSI's OWN population-construction
pipeline verbatim (`build_wordnet_synonym_candidates`, `build_cooccurrence_paircounts`,
`build_syntagmatic_candidates`, `match_cells`) -- but restricted to an anchor pool that EXCLUDES
every one of the ~617 distinct words appearing anywhere in the licensed 242-pair evaluation
population (matchedP + matchedS). This is WORD-level disjointness, strictly stronger than pair-level
disjointness (guards against the same word-identity leakage the group-disjoint oracle recompute
found in 6.18). Every hyperparameter (alpha, k_shift, subsample t, eigenvalue weighting p, SVD rank
k) is selected by maximising AUC on this held-out set ONLY. The selected configuration's AUC on the
REAL 242-pair evaluation population is then read ONCE and reported as THE RESULT. The best AUC over
the SAME grid scored DIRECTLY on the evaluation pairs is ALSO reported, clearly labelled
CEILING_NOT_A_RESULT_DO_NOT_QUOTE_AS_CAPABILITY (both numbers come from the SAME already-computed
SVD vectors -- scoring against a second pair set costs nothing extra, so there is no reason to skip
either report).

If the held-out population cannot be built (too few matched pairs after the covariate-matching
caliper on the restricted pool), this is disclosed explicitly and only the eval-pair sweep ceiling
is reported for the affected arm, per the brief's own escape hatch.

=================================================================================================
WINNER COMPOSITION -- operational definition invented for this cell (verified: grep for the exact
phrase across notes/experiments/tools returns zero hits anywhere in this codebase; there is no
prior definition to reuse). For each arm, for each index i in the (matchedP[i], matchedS[i])
covariate-matched comparison: winner = whichever of the two this arm scored higher; co_occurs(w1,w2)
= nonzero raw corpus count in either direction (CAP.load_full_pstore's Pstore counts, the SAME
counts M is built from). Reports: no_relation_rate_overall (fraction of ALL matched pairs, P+S
combined, with zero co-occurrence -- an empirical re-check of SET P's own zero-co-occurrence
construction guarantee, expected ~0.5 by design since SET S is constructed to be top-co-occurring),
gold_SET_P_cooccurrence_share (SET P's own co-occurrence share, ~0.0 by construction, the reference
point), SET_S_cooccurrence_share (~1.0 by construction, the other reference point), and
winner_cooccurrence_share (the arm-dependent, informative number: how often the arm's own
higher-scored member happens to be the corpus-co-occurring one). The ratio reported is
winner_cooccurrence_share / SET_S_cooccurrence_share -- 1.0 means the arm behaves exactly like a
naive always-prefer-the-collocate rule (the incumbent's documented failure mode), 0.0 means it never
does. (A literal winner/gold ratio is mathematically degenerate: gold's own share is ~0 by
construction, so dividing by it blows up; this is disclosed rather than silently avoided.)

=================================================================================================
STOP-IF (evaluated in this order):
  (i)   ANY regression-gate check or K1 fails -> INSTRUMENT_NOT_LICENSED, publish nothing but that.
  (ii)  A held-out-selected arm (T1/T2/T3/T4 RESULT, not ceiling) is CI-separated ABOVE 0.5 ->
        THE DIRECTOR'S SUPERVISION CONCLUSION IS WRONG; what was missing was hyperparameters, not a
        learning signal. Name the winning configuration.
  (iii) Tuned arms improve on T0 (held-out-selected RESULT's point estimate CI-separated above T0's
        best-k point estimate) but stay below 0.5 -> tuning is real but insufficient; supervision
        conclusion SURVIVES a fairer test.
  (iv)  Tuned arms do not beat T0 at all -> the tuning literature does not transfer to this
        ~1.8M-token corpus (vs. the 1M-100M-token scales where LGD2015 established it).

ASCII-only. NO LLM anywhere in this runtime path (T5 trains offline, freezes to a static table, and
reads by lookup only -- no forward pass at read time). NO pretrained embedding table imported
anywhere. CPU only, pinned single-threaded. data/foundation/** is never opened. Writes only under
data/exp_tuned_count_unsupervised_dissociation_v1[_reduced]/. Does not edit hdlab/predictive_coding.py
or any file the concurrent predcoding-on-dissociation agent owns.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/sklearn/DSI/CAP next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
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
import experiments.exp_corpus_capacity_ppmi_svd_ceiling_v1 as CAP           # noqa: E402  READ ONLY
from tools import floor_battery as FB                                       # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics      # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "tuned_count_unsupervised_dissociation_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/tuned_count_unsupervised_dissociation_2026-08-18.md"

MASTER_SEED = CTS.MASTER_SEED

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"
N_BOOT = 1500 if SMOKE else 10000

# --- grids. Sweep, never adopt a value. ----------------------------------------------------------
K_SWEEP_FULL = [50, 100, 300, 500]                 # T0 regression + T1-T3 diagnostic reporting
SEL_K = [10, 20] if SMOKE else [50, 300]           # small grid used for held-out selection
ALPHA_GRID = [0.5, 0.75, 1.0]                       # 1.0 = no smoothing (internal control)
KSHIFT_GRID = [1, 5, 15]                            # 1 = no shift (internal control)
SUBSAMPLE_T_GRID = [None, 1e-3, 1e-5]               # None = off (internal control)
P_GRID = [0.0, 0.5, 1.0]                            # eigenvalue weighting exponent
T4_K_GRID = [10, 20] if SMOKE else [50, 300]

# EXPECTED regression-gate values for T0 -- MEASURED@data/exp_corpus_capacity_ppmi_svd_ceiling_v1/
# metrics.json (run_mode=full, INSTRUMENT_LICENSED=true), plan sec 6.18.
EXPECTED_T0 = {50: 0.0519, 100: 0.0285, 300: 0.0230, 500: 0.0278}
T0_TOL = 0.0005   # CAP's own REGRESSION_TOL

SGNS_VECTOR_SIZE = 100
SGNS_WINDOW = 5
SGNS_EPOCHS = 5
SGNS_NEGATIVE = 5
SGNS_SAMPLE = 1e-5
SGNS_MAX_SENTENCES_FOR_CHEAP = 200000   # guard: if the cached corpus is somehow far larger than
                                        # expected, skip T5 rather than silently run something slow


def l2n_dense(A: np.ndarray) -> np.ndarray:
    return CAP.l2n_dense(A)


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def _seed_for(tag: str) -> int:
    """Deterministic seed from a human-readable tag, distinct from CAP's / DSI's own seed offsets."""
    h = int(hashlib.sha256(tag.encode("utf-8")).hexdigest()[:8], 16)
    return MASTER_SEED + 500000 + (h % 400000)


# =================================================================================================
# TUNED PPMI -- generalises CAP.ppmi_of. At (alpha=1.0, k_shift=1, subsample_t=None) this must
# reduce to CAP.ppmi_of(M) bit-for-bit (asserted in self_test): the internal control.
# =================================================================================================
def ppmi_tuned(M: sp.csr_matrix, alpha: float = 1.0, k_shift: float = 1.0,
              subsample_t: Optional[float] = None) -> sp.csr_matrix:
    """PMI_alpha(w,c) = log( c_wc * sum(col_sums^alpha) / (row_sum_w * col_sum_c^alpha) ),
    PPMI_shifted = max(0, PMI_alpha - log(k_shift)). subsample_t, if not None, first scales EVERY
    column c of M by p_keep(c) = min(1, sqrt(t / f_c)) (f_c = c's share of total corpus mass) --
    the count-matrix-level EXPECTATION of independently subsampling each token occurrence of c in
    the underlying stream (Mikolov et al. 2013's subsampling formula), since only the already-
    aggregated counts are available here, not the raw token stream. Marginals used for PMI are
    RECOMPUTED on the (possibly subsampled) matrix, never on the raw M."""
    Mc = M
    if subsample_t is not None:
        col_sums_raw = np.asarray(M.sum(axis=0)).ravel()
        total_raw = float(M.sum())
        freq = col_sums_raw / max(total_raw, 1e-12)
        p_keep = np.minimum(1.0, np.sqrt(float(subsample_t) / np.maximum(freq, 1e-12)))
        Mc = (M @ sp.diags(p_keep)).tocsr()
    Mco = Mc.tocoo()
    row_sums = np.asarray(Mc.sum(axis=1)).ravel()
    col_sums = np.asarray(Mc.sum(axis=0)).ravel()
    row_sums = np.where(row_sums < 1e-12, 1.0, row_sums)
    col_sums_safe = np.where(col_sums < 1e-12, 1.0, col_sums)
    col_sums_alpha = np.power(col_sums_safe, float(alpha))
    total_alpha = float(col_sums_alpha.sum())
    expected = row_sums[Mco.row] * col_sums_alpha[Mco.col] / max(total_alpha, 1e-300)
    pmi_vals = np.log(np.maximum(Mco.data, 1e-300) / np.maximum(expected, 1e-300))
    ppmi_vals = np.maximum(pmi_vals - np.log(float(k_shift)), 0.0)
    P = sp.csr_matrix((ppmi_vals, (Mco.row, Mco.col)), shape=Mc.shape)
    P.eliminate_zeros()
    return P


def svd_vectors_p(Mppmi: sp.csr_matrix, k: int, p: float, svd_seed: int) -> Optional[np.ndarray]:
    """U * S**p (p=0.5 == CAP's own U*sqrt(S) convention), L2-normalised rows. None if k exceeds
    the matrix's rank ceiling."""
    max_k = min(Mppmi.shape) - 1
    if k >= max_k:
        return None
    U, S, Vt = svds(Mppmi.asfptype(), k=k, random_state=svd_seed)
    order = np.argsort(-S)
    U, S = U[:, order], S[order]
    weight = np.power(np.maximum(S, 1e-12), float(p))
    vecs = U * weight[None, :]
    return l2n_dense(vecs)


def score_pairs(vecs: Optional[np.ndarray], row_idx: Dict[str, int],
               pairsP: List[Tuple[str, str, str]], pairsS: List[Tuple[str, str, str]],
               boot_seed: int) -> Optional[Dict]:
    if vecs is None:
        return None
    pP = CAP.pair_cosine_from_dense_rows(vecs, row_idx, pairsP)
    pS = CAP.pair_cosine_from_dense_rows(vecs, row_idx, pairsS)
    return DSI.auc_bootstrap(pP[~np.isnan(pP)], pS[~np.isnan(pS)], N_BOOT, boot_seed)


# =================================================================================================
# WINNER COMPOSITION (operational definition invented for this cell -- see module docstring)
# =================================================================================================
def co_occurs(w1: str, w2: str, counts_full: Dict) -> bool:
    return bool(counts_full.get(w1, {}).get(w2, 0) > 0 or counts_full.get(w2, {}).get(w1, 0) > 0)


def winner_composition(vecs_or_store, row_idx_or_none, matchedP, matchedS, counts_full: Dict,
                       score_fn) -> Dict:
    """score_fn(w1, w2) -> float score for this arm; NaN if unscorable. Reports the invented
    WINNER COMPOSITION metric defined in the module docstring."""
    n = len(matchedP)
    p_cooc = [co_occurs(w1, w2, counts_full) for w1, w2, _ in matchedP]
    s_cooc = [co_occurs(w1, w2, counts_full) for w1, w2, _ in matchedS]
    n_ties = 0
    n_unscored = 0
    winner_cooc_flags: List[bool] = []
    for i in range(n):
        w1p, w2p, _ = matchedP[i]
        w1s, w2s, _ = matchedS[i]
        sp_ = score_fn(w1p, w2p)
        ss_ = score_fn(w1s, w2s)
        if sp_ is None or ss_ is None or (isinstance(sp_, float) and np.isnan(sp_)) or \
                (isinstance(ss_, float) and np.isnan(ss_)):
            n_unscored += 1
            continue
        if sp_ > ss_:
            winner_cooc_flags.append(p_cooc[i])
        elif ss_ > sp_:
            winner_cooc_flags.append(s_cooc[i])
        else:
            n_ties += 1
    p_share = float(np.mean(p_cooc)) if p_cooc else float("nan")
    s_share = float(np.mean(s_cooc)) if s_cooc else float("nan")
    combined = p_cooc + s_cooc
    no_relation_rate = float(np.mean([not c for c in combined])) if combined else float("nan")
    winner_share = float(np.mean(winner_cooc_flags)) if winner_cooc_flags else float("nan")
    ratio = (winner_share / s_share) if (s_share and s_share > 1e-9 and not np.isnan(winner_share)) \
        else None
    return {
        "n_pairs_compared": n, "n_ties_excluded": n_ties, "n_unscored_excluded": n_unscored,
        "no_relation_rate_overall": no_relation_rate,
        "gold_SET_P_cooccurrence_share": p_share,
        "SET_S_cooccurrence_share": s_share,
        "winner_cooccurrence_share": winner_share,
        "ratio_winner_over_SET_S_share": ratio,
    }


def score_fn_from_dense(vecs: np.ndarray, row_idx: Dict[str, int]):
    def _f(w1, w2):
        i1, i2 = row_idx.get(w1), row_idx.get(w2)
        if i1 is None or i2 is None:
            return float("nan")
        return float(np.dot(vecs[i1], vecs[i2]))
    return _f


def score_fn_from_arrays(matchedP, matchedS, P_arr, S_arr):
    """DSI's cached arm_scores are index-aligned to matchedP/matchedS in ORDER, not keyed by word --
    build a (w1,w2)->score lookup from that alignment."""
    lut: Dict[Tuple[str, str], float] = {}
    for (w1, w2, _), s in zip(matchedP, P_arr):
        lut[(w1, w2)] = float(s)
    for (w1, w2, _), s in zip(matchedS, S_arr):
        lut[(w1, w2)] = float(s)

    def _f(w1, w2):
        return lut.get((w1, w2), lut.get((w2, w1), float("nan")))
    return _f


# =================================================================================================
# HELD-OUT VALIDATION POPULATION -- DSI's own pipeline, restricted to an anchor pool WORD-DISJOINT
# from the evaluation population. Never touches matchedP/matchedS's own words.
# =================================================================================================
def build_heldout_population(anchor_set_pop: Sequence[str], out_dir_ckpt: str
                             ) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]], Dict]:
    key = unit_key("HELDOUT_POPULATION", CODE_VERSION, RUN_MODE)
    prior = load_units(out_dir_ckpt).get(key)
    if prior is not None:
        print("[heldout] RESUMED FROM CHECKPOINT", flush=True)
        return ([tuple(x) for x in prior["matchedP"]], [tuple(x) for x in prior["matchedS"]],
                prior["diag"])

    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    mat = np.asarray(C["mat"], dtype=np.float32)
    pos_idx = C["pos"]
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)

    aset = set(anchor_set_pop)
    print("[heldout] building WordNet candidates over %d word-disjoint anchors" % len(aset),
         flush=True)
    wn_pairs = DSI.build_wordnet_synonym_candidates(aset)
    wn_pair_set = set(tuple(sorted((a, b))) for a, b, _ in wn_pairs)
    print("[heldout] %d WordNet same-synset candidate pairs" % len(wn_pairs), flush=True)

    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    pair_counts = DSI.build_cooccurrence_paircounts(sents, aset)
    cellP = [(w1, w2, p) for (w1, w2, p) in wn_pairs if pair_counts.get((w1, w2), 0) == 0]
    cellS, candS_diag = DSI.build_syntagmatic_candidates(pair_counts, wn_pair_set,
                                                         cap=DSI.CELL_S_CAND_CAP)
    print("[heldout] SET P raw=%d, SET S raw=%d" % (len(cellP), len(cellS)), flush=True)

    tri_all = DSI.l2n(t_mat)
    proto_all = FB.constant_prototype_floor(mat, mat_ok)
    cand_words = set(w for w1, w2, _p in cellP + cellS for w in (w1, w2))
    tri_of = {w: tri_all[pos_idx[w]] for w in cand_words if w in pos_idx}
    proto_of = {w: float(proto_all[pos_idx[w]]) for w in cand_words if w in pos_idx}
    matchedP, matchedS, match_diag = DSI.match_cells(cellP, cellS, fq_log, seed=MASTER_SEED + 31415,
                                                     tri_of=tri_of, proto_of=proto_of)
    print("[heldout] MATCHED n_P=%d n_S=%d" % (len(matchedP), len(matchedS)), flush=True)

    diag = {"n_pool_anchors_word_disjoint_from_eval": len(aset), "n_wn_candidates": len(wn_pairs),
           "n_setP_raw_zero_cooccurrence": len(cellP), "setS_construction": candS_diag,
           "matching": match_diag, "n_matched": len(matchedP)}
    record_unit(out_dir_ckpt, key, {"matchedP": matchedP, "matchedS": matchedS, "diag": diag})
    return matchedP, matchedS, diag


# =================================================================================================
# T5 -- SGNS from scratch, admissible under Q3 (offline train, frozen table, lookup at read time)
# =================================================================================================
def run_sgns_arm(row_idx: Dict[str, int], matchedP, matchedS) -> Dict:
    try:
        import gensim
        from gensim.models import Word2Vec
    except ImportError as exc:
        return {"SKIPPED": True, "reason": "gensim not importable: %r" % exc}

    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    if len(sents) > SGNS_MAX_SENTENCES_FOR_CHEAP:
        return {"SKIPPED": True,
               "reason": "corpus has %d sentences, exceeds the %d cheap-guard; not run." %
                         (len(sents), SGNS_MAX_SENTENCES_FOR_CHEAP)}

    from hdlab.reading_grounding_loop import content_words
    t0 = time.time()
    tokenised = [content_words(s) for s in sents]
    tokenised = [t for t in tokenised if t]
    print("[T5] tokenised %d/%d non-empty sentences in %.1fs" %
         (len(tokenised), len(sents), time.time() - t0), flush=True)

    t1 = time.time()
    model = Word2Vec(sentences=tokenised, vector_size=SGNS_VECTOR_SIZE, window=SGNS_WINDOW,
                     min_count=1, sg=1, negative=SGNS_NEGATIVE, sample=SGNS_SAMPLE,
                     epochs=SGNS_EPOCHS, workers=1, seed=MASTER_SEED % (2 ** 31))
    elapsed_train = round(time.time() - t1, 1)
    print("[T5] gensim Word2Vec trained in %.1fs, vocab=%d" %
         (elapsed_train, len(model.wv.key_to_index)), flush=True)

    def in_in(w1, w2):
        if w1 not in model.wv.key_to_index or w2 not in model.wv.key_to_index:
            return float("nan")
        return float(model.wv.similarity(w1, w2))

    syn1neg = getattr(model, "syn1neg", None)

    def in_out(w1, w2):
        if syn1neg is None:
            return float("nan")
        idx = model.wv.key_to_index
        if w1 not in idx or w2 not in idx:
            return float("nan")
        v1_in = model.wv.get_vector(w1, norm=True)
        v2_in = model.wv.get_vector(w2, norm=True)
        o1 = syn1neg[idx[w1]]
        o2 = syn1neg[idx[w2]]
        n_o1 = o1 / max(float(np.linalg.norm(o1)), 1e-12)
        n_o2 = o2 / max(float(np.linalg.norm(o2)), 1e-12)
        return float(0.5 * (np.dot(v1_in, n_o2) + np.dot(v2_in, n_o1)))

    inin_P = np.array([in_in(w1, w2) for w1, w2, _ in matchedP])
    inin_S = np.array([in_in(w1, w2) for w1, w2, _ in matchedS])
    inout_P = np.array([in_out(w1, w2) for w1, w2, _ in matchedP])
    inout_S = np.array([in_out(w1, w2) for w1, w2, _ in matchedS])

    inin_auc = DSI.auc_bootstrap(inin_P[~np.isnan(inin_P)], inin_S[~np.isnan(inin_S)], N_BOOT,
                                 _seed_for("T5:inin"))
    inout_auc = None
    if syn1neg is not None and not np.all(np.isnan(inout_P)):
        inout_auc = DSI.auc_bootstrap(inout_P[~np.isnan(inout_P)], inout_S[~np.isnan(inout_S)],
                                      N_BOOT, _seed_for("T5:inout"))

    n1_vecs = {w: np.random.default_rng(MASTER_SEED + 999).standard_normal(SGNS_VECTOR_SIZE)
              for w in set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2))}
    for w in n1_vecs:
        n1_vecs[w] = n1_vecs[w] / max(float(np.linalg.norm(n1_vecs[w])), 1e-12)
    n1_P = np.array([float(np.dot(n1_vecs[w1], n1_vecs[w2])) for w1, w2, _ in matchedP])
    n1_S = np.array([float(np.dot(n1_vecs[w1], n1_vecs[w2])) for w1, w2, _ in matchedS])
    n1_auc = DSI.auc_bootstrap(n1_P, n1_S, N_BOOT, _seed_for("T5:N1_untrained_control"))

    return {
        "SKIPPED": False, "elapsed_train_s": elapsed_train, "vocab_size": len(model.wv.key_to_index),
        "n_sentences_trained_on": len(tokenised),
        "NO_PRETRAINED_EMBEDDING_TABLE_IMPORTED": True,
        "T5_IN_IN": inin_auc, "T5_IN_OUT_bonus_diagnostic": inout_auc,
        "N1_UNTRAINED_RANDOM_INIT_CONTROL": n1_auc,
        "in_in_score_fn_note": "cue-vector cosine (model.wv.similarity), the primary/required number",
    }


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- ppmi_tuned at defaults must reduce to CAP.ppmi_of bit-for-bit (the internal control) ----
    toy = sp.csr_matrix(np.array([[10.0, 0.0, 1.0, 4.0],
                                  [0.0, 10.0, 1.0, 2.0],
                                  [1.0, 1.0, 5.0, 0.0],
                                  [3.0, 2.0, 0.0, 8.0]], dtype=np.float64))
    Pa = np.asarray(ppmi_tuned(toy, alpha=1.0, k_shift=1.0, subsample_t=None).todense())
    Pb = np.asarray(CAP.ppmi_of(toy).todense())
    max_diff = float(np.max(np.abs(Pa - Pb)))
    assert max_diff < 1e-9, "ppmi_tuned at defaults must equal CAP.ppmi_of: max_diff=%.2e" % max_diff
    ev["ppmi_tuned_reduces_to_CAP_vanilla"] = {"max_abs_diff": max_diff}

    # --- shift k_shift=1 (log(1)=0) leaves PMI unchanged pre-floor; k_shift>1 only lowers ---------
    P_noshift = np.asarray(ppmi_tuned(toy, k_shift=1.0).todense())
    P_shift5 = np.asarray(ppmi_tuned(toy, k_shift=5.0).todense())
    assert (P_shift5 <= P_noshift + 1e-9).all(), "a bigger shift must never INCREASE PPMI"
    ev["shift_monotone"] = True

    # --- alpha=1.0 leaves PMI unchanged (context smoothing off); alpha<1 flattens the marginal ---
    P_alpha1 = np.asarray(ppmi_tuned(toy, alpha=1.0).todense())
    assert np.max(np.abs(P_alpha1 - Pb)) < 1e-9, "alpha=1.0 must equal vanilla PPMI"
    ev["alpha_1_is_vanilla"] = True

    # --- subsample_t=None leaves the matrix unchanged; a tiny t must shrink frequent-column mass -
    P_nosub = np.asarray(ppmi_tuned(toy, subsample_t=None).todense())
    assert np.max(np.abs(P_nosub - Pb)) < 1e-9, "subsample_t=None must equal vanilla PPMI"
    P_sub = ppmi_tuned(toy, subsample_t=1e-6)
    assert P_sub.shape == toy.shape, "subsampled PPMI must keep the same shape"
    ev["subsample_off_is_vanilla"] = True

    # --- svd_vectors_p at p=0.5 matches CAP's own U*sqrt(S) convention on a real tiny fixture ----
    C = CTS.load_cache()
    anchors = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    tiny_anchor_set = [a for a, ok in zip(anchors, mat_ok) if ok][:30]
    M_tiny, row_idx_tiny, diag_tiny = CAP.build_matrix(tiny_anchor_set)
    Pppmi_tiny = CAP.ppmi_of(M_tiny)
    k_tiny = min(5, min(Pppmi_tiny.shape) - 1)
    if k_tiny >= 1:
        vecs_mine = svd_vectors_p(Pppmi_tiny, k_tiny, 0.5, MASTER_SEED + 7000 + k_tiny)
        U, S, Vt = svds(Pppmi_tiny.asfptype(), k=k_tiny, random_state=MASTER_SEED + 7000 + k_tiny)
        order = np.argsort(-S)
        U, S = U[:, order], S[order]
        vecs_cap = l2n_dense(U * np.sqrt(np.maximum(S, 0.0))[None, :])
        assert vecs_mine is not None
        assert np.max(np.abs(vecs_mine - vecs_cap)) < 1e-6, \
            "svd_vectors_p(p=0.5) must match CAP's own U*sqrt(S) convention"
        ev["svd_vectors_p_matches_CAP_convention"] = {"k": k_tiny}

    # --- svd_vectors_p returns None when k exceeds the rank ceiling, never silently substitutes --
    huge_k = min(Pppmi_tiny.shape)
    assert svd_vectors_p(Pppmi_tiny, huge_k, 0.5, 1) is None, \
        "k >= min(shape) must be dropped (None), never silently clamped"
    ev["svd_rank_ceiling_dropped"] = True

    # --- winner_composition known-answer: a perfect P>S arm reads winner_share == SET_S's own,
    # since a perfect arm ALWAYS prefers P (non-cooccurring), so ratio should be 0.0 -------------
    toy_matchedP = [("a", "b", "n"), ("c", "d", "n")]
    toy_matchedS = [("e", "f", "n"), ("g", "h", "n")]
    toy_counts = {"a": {}, "b": {}, "c": {}, "d": {}, "e": {"f": 5}, "f": {"e": 5},
                 "g": {"h": 3}, "h": {"g": 3}}

    def perfect_fn(w1, w2):
        # P-pairs always score higher (1.0) than S-pairs (0.0), matching auc=1.0 behaviour
        pset = {("a", "b"), ("c", "d")}
        return 1.0 if (w1, w2) in pset or (w2, w1) in pset else 0.0
    wc = winner_composition(None, None, toy_matchedP, toy_matchedS, toy_counts, perfect_fn)
    assert wc["gold_SET_P_cooccurrence_share"] == 0.0, "toy fixture SET P must be 0%% co-occurring"
    assert wc["SET_S_cooccurrence_share"] == 1.0, "toy fixture SET S must be 100%% co-occurring"
    assert wc["winner_cooccurrence_share"] == 0.0, \
        "a perfect substitutability arm must NEVER pick the co-occurring winner: %r" % wc
    assert wc["ratio_winner_over_SET_S_share"] == 0.0
    ev["winner_composition_perfect_arm_known_answer"] = wc

    # --- winner_composition known-answer: an incumbent-like arm that ALWAYS prefers the co-
    # occurring member must read ratio 1.0 ----------------------------------------------------
    def collocate_fn(w1, w2):
        sset = {("e", "f"), ("g", "h")}
        return 1.0 if (w1, w2) in sset or (w2, w1) in sset else 0.0
    wc2 = winner_composition(None, None, toy_matchedP, toy_matchedS, toy_counts, collocate_fn)
    assert wc2["winner_cooccurrence_share"] == 1.0
    assert wc2["ratio_winner_over_SET_S_share"] == 1.0
    ev["winner_composition_collocate_arm_known_answer"] = wc2

    # --- _seed_for is deterministic and distinct per tag ------------------------------------------
    assert _seed_for("x") == _seed_for("x")
    assert _seed_for("x") != _seed_for("y")
    ev["seed_for_deterministic"] = True

    # --- score_fn_from_arrays reproduces a known lookup ---------------------------------------------
    fn = score_fn_from_arrays([("a", "b", "n")], [("c", "d", "n")], np.array([0.7]), np.array([0.2]))
    assert abs(fn("a", "b") - 0.7) < 1e-9 and abs(fn("c", "d") - 0.2) < 1e-9
    assert abs(fn("b", "a") - 0.7) < 1e-9, "lookup must be direction-agnostic"
    ev["score_fn_from_arrays_known_answer"] = True

    # --- arms-must-differ (META_RULE_AF) -----------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr)
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip -----------------------------------------------------------------------
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

    # =============================== REGRESSION GATE (STOP-IF i), reused from CAP ====================
    print("[gate] running CAP.regression_gate() (reuses DSI's own cached checks)", flush=True)
    gate = CAP.regression_gate()   # raises SystemExit on failure -- caught in main()
    rep["REGRESSION_GATE"] = gate["gate_report"]
    matchedP, matchedS = gate["matchedP"], gate["matchedS"]
    if grid == "reduced":
        matchedP, matchedS = matchedP[:40], matchedS[:40]
    rep["N_MATCHED_PAIRS_PER_CELL"] = len(matchedP)
    eval_words = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    rep["N_DISTINCT_EVAL_WORDS"] = len(eval_words)

    # =============================== MATRIX (reused from CAP) ========================================
    anchor_words_full = CTS.load_cache()["anchors"]
    anchor_mat_ok = np.asarray(CTS.load_cache()["mat_ok"], dtype=bool)
    anchor_words_full = [a for a, ok in zip(anchor_words_full, anchor_mat_ok) if ok]
    if grid == "reduced":
        pair_words = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
        anchor_words_full = sorted(set(anchor_words_full[:1200]) | set(pair_words))

    M, row_idx, matrix_diag = CAP.build_matrix(anchor_words_full)
    rep["MATRIX"] = matrix_diag
    rep["COVERAGE"] = CAP.coverage_report(row_idx, matchedP, matchedS)
    counts_full, _missing = CAP.load_full_pstore(anchor_words_full)

    # =============================== HELD-OUT VALIDATION POPULATION (word-disjoint) ==================
    heldout_pool = [a for a in anchor_words_full if a not in set(eval_words)]
    print("[heldout] pool size=%d (excludes %d eval words)" % (len(heldout_pool), len(eval_words)),
         flush=True)
    if grid == "reduced":
        heldout_pool = heldout_pool[:800]
    heldoutP, heldoutS, heldout_diag = build_heldout_population(heldout_pool, out_dir_ckpt)
    rep["HELDOUT_POPULATION"] = heldout_diag
    heldout_usable = len(heldoutP) >= 20
    if not heldout_usable:
        print("[heldout] UNUSABLE (n=%d < 20) -- falling back to sweep-ceiling-only reporting for "
             "every tuned arm, per the brief's own escape hatch" % len(heldoutP), flush=True)

    # =============================== T0_VANILLA_PPMI_SVD (regression check) =========================
    print("[T0] building vanilla PPMI (CAP.ppmi_of) and reproducing CAP's own B2 sweep", flush=True)
    Mppmi_vanilla = CAP.ppmi_of(M)
    t0_results: Dict[str, Dict] = {}
    t0_checks: Dict[str, Dict] = {}
    for k in K_SWEEP_FULL:
        vecs = svd_vectors_p(Mppmi_vanilla, k, 0.5, MASTER_SEED + 7000 + k)
        if vecs is None:
            continue
        auc_res = score_pairs(vecs, row_idx, matchedP, matchedS, MASTER_SEED + 9300 + k)
        t0_results[str(k)] = auc_res
        expected = EXPECTED_T0.get(k)
        if expected is not None and grid == "full":
            delta = round(auc_res["auc"] - expected, 6)
            ok = abs(delta) <= T0_TOL
            t0_checks[str(k)] = {"expected": expected, "measured": auc_res["auc"], "delta": delta,
                                 "PASS": ok}
            print("[T0] k=%d expected=%.4f measured=%.4f delta=%.4f %s" %
                 (k, expected, auc_res["auc"], delta, "PASS" if ok else "FAIL"), flush=True)
    rep["T0_VANILLA_PPMI_SVD"] = {"sweep": t0_results, "regression_checks": t0_checks}
    if grid == "full" and t0_checks and not all(c["PASS"] for c in t0_checks.values()):
        raise SystemExit("T0_REGRESSION_GATE_FAILED -- vanilla PPMI+SVD sweep does not reproduce "
                         "CAP's own landed numbers: %r" % t0_checks)
    t0_best_k = max(t0_results, key=lambda k: t0_results[k]["auc"]) if t0_results else None
    t0_best_auc = t0_results[t0_best_k]["auc"] if t0_best_k else float("nan")
    rep["T0_BEST_K"] = t0_best_k
    t0_winner_comp = None
    if t0_best_k is not None:
        vecs_t0 = svd_vectors_p(Mppmi_vanilla, int(t0_best_k), 0.5, MASTER_SEED + 7000 + int(t0_best_k))
        t0_winner_comp = winner_composition(None, None, matchedP, matchedS, counts_full,
                                            score_fn_from_dense(vecs_t0, row_idx))
    rep["T0_WINNER_COMPOSITION"] = t0_winner_comp

    # =============================== generic single-knob arm runner ==================================
    def run_knob_arm(name: str, configs: List[Tuple], cfg_labeler) -> Dict:
        """configs: list of (alpha, k_shift, subsample_t, k, p) tuples. Scores each on HELD-OUT
        (if usable) and on EVAL. Selects by max held-out AUC point estimate (or, if held-out is
        unusable, reports sweep-ceiling-only, disclosed)."""
        rows = []
        for (alpha, k_shift, subsample_t, k, p) in configs:
            tag = "%s:%s" % (name, cfg_labeler(alpha, k_shift, subsample_t, k, p))
            Mppmi = ppmi_tuned(M, alpha=alpha, k_shift=k_shift, subsample_t=subsample_t)
            vecs = svd_vectors_p(Mppmi, k, p, _seed_for(tag + ":svd"))
            if vecs is None:
                continue
            ho_auc = (score_pairs(vecs, row_idx, heldoutP, heldoutS, _seed_for(tag + ":ho"))
                     if heldout_usable else None)
            ev_auc = score_pairs(vecs, row_idx, matchedP, matchedS, _seed_for(tag + ":ev"))
            rows.append({"alpha": alpha, "k_shift": k_shift, "subsample_t": subsample_t, "k": k,
                        "p": p, "held_out_auc": ho_auc, "eval_auc": ev_auc, "tag": tag})
        if not rows:
            return {"ERROR": "no config in %s's grid produced a valid SVD (rank ceiling?)" % name}

        ceiling_row = max(rows, key=lambda r: r["eval_auc"]["auc"])
        if heldout_usable:
            selected_row = max(rows, key=lambda r: r["held_out_auc"]["auc"])
        else:
            selected_row = ceiling_row  # disclosed fallback, per brief's escape hatch

        return {
            "SWEEP": rows,
            "HELDOUT_USABLE": heldout_usable,
            "SELECTED_CONFIG": {k_: v for k_, v in selected_row.items() if k_ != "tag"},
            "RESULT_held_out_selected_eval_AUC": selected_row["eval_auc"],
            "CEILING_NOT_A_RESULT_DO_NOT_QUOTE_AS_CAPABILITY": {
                k_: v for k_, v in ceiling_row.items() if k_ != "tag"},
            "CEILING_eval_AUC": ceiling_row["eval_auc"],
        }

    # =============================== T1_CONTEXT_DISTRIBUTION_SMOOTHING ===============================
    print("[T1] alpha sweep=%r x k=%r (held-out selection, eval scored in parallel)" %
         (ALPHA_GRID, SEL_K), flush=True)
    t1_configs = [(alpha, 1.0, None, k, 0.5) for alpha in ALPHA_GRID for k in SEL_K]
    t1 = run_knob_arm("T1", t1_configs, lambda a, ks, t, k, p: "a%.2f_k%d" % (a, k))
    rep["T1_CONTEXT_DISTRIBUTION_SMOOTHING"] = t1

    # =============================== T2_SHIFTED_PPMI ================================================
    print("[T2] k_shift sweep=%r x k=%r" % (KSHIFT_GRID, SEL_K), flush=True)
    t2_configs = [(1.0, ks, None, k, 0.5) for ks in KSHIFT_GRID for k in SEL_K]
    t2 = run_knob_arm("T2", t2_configs, lambda a, ks, t, k, p: "ks%d_k%d" % (ks, k))
    rep["T2_SHIFTED_PPMI"] = t2

    # =============================== T3_SUBSAMPLING ==================================================
    print("[T3] subsample_t sweep=%r x k=%r" % (SUBSAMPLE_T_GRID, SEL_K), flush=True)
    t3_configs = [(1.0, 1.0, t, k, 0.5) for t in SUBSAMPLE_T_GRID for k in SEL_K]
    t3 = run_knob_arm("T3", t3_configs, lambda a, ks, t, k, p: "t%s_k%d" % (t, k))
    rep["T3_SUBSAMPLING"] = t3

    # =============================== T4_BEST_COMBINED ================================================
    def _selected(arm_rep, key, default):
        sc = arm_rep.get("SELECTED_CONFIG")
        return sc[key] if sc and key in sc else default
    alpha_star = _selected(t1, "alpha", 1.0)
    kshift_star = _selected(t2, "k_shift", 1.0)
    tsub_star = _selected(t3, "subsample_t", None)
    print("[T4] combining alpha*=%r k_shift*=%r subsample_t*=%r, sweeping p=%r x k=%r" %
         (alpha_star, kshift_star, tsub_star, P_GRID, T4_K_GRID), flush=True)
    t4_configs = [(alpha_star, kshift_star, tsub_star, k, p) for p in P_GRID for k in T4_K_GRID]
    t4 = run_knob_arm("T4", t4_configs, lambda a, ks, t, k, p: "p%.2f_k%d" % (p, k))
    t4["COMBINED_FROM"] = {"alpha_star": alpha_star, "k_shift_star": kshift_star,
                          "subsample_t_star": tsub_star}
    rep["T4_BEST_COMBINED"] = t4

    # winner composition for each arm's RESULT (held-out-selected) config -----------------------------
    def winner_comp_for_arm(arm_rep):
        sc = arm_rep.get("SELECTED_CONFIG")
        if not sc:
            return None
        Mppmi = ppmi_tuned(M, alpha=sc["alpha"], k_shift=sc["k_shift"], subsample_t=sc["subsample_t"])
        vecs = svd_vectors_p(Mppmi, sc["k"], sc["p"], _seed_for("wc:%r" % sc))
        if vecs is None:
            return None
        return winner_composition(None, None, matchedP, matchedS, counts_full,
                                  score_fn_from_dense(vecs, row_idx))
    rep["T1_WINNER_COMPOSITION"] = winner_comp_for_arm(t1)
    rep["T2_WINNER_COMPOSITION"] = winner_comp_for_arm(t2)
    rep["T3_WINNER_COMPOSITION"] = winner_comp_for_arm(t3)
    rep["T4_WINNER_COMPOSITION"] = winner_comp_for_arm(t4)

    # =============================== diagnostic full-k table for T1/T2/T3's selected knob value ------
    def diagnostic_k_sweep(name, alpha, k_shift, subsample_t):
        Mppmi = ppmi_tuned(M, alpha=alpha, k_shift=k_shift, subsample_t=subsample_t)
        out = {}
        for k in K_SWEEP_FULL:
            vecs = svd_vectors_p(Mppmi, k, 0.5, _seed_for("%s:diag:k%d" % (name, k)))
            if vecs is None:
                continue
            out[str(k)] = score_pairs(vecs, row_idx, matchedP, matchedS,
                                      _seed_for("%s:diag:ev:k%d" % (name, k)))
        return out
    if grid == "full":
        rep["T1_DIAGNOSTIC_FULL_K_SWEEP_at_selected_alpha_EVAL_ONLY_NOT_SELECTION"] = \
            diagnostic_k_sweep("T1", alpha_star, 1.0, None)
        rep["T2_DIAGNOSTIC_FULL_K_SWEEP_at_selected_kshift_EVAL_ONLY_NOT_SELECTION"] = \
            diagnostic_k_sweep("T2", 1.0, kshift_star, None)
        rep["T3_DIAGNOSTIC_FULL_K_SWEEP_at_selected_t_EVAL_ONLY_NOT_SELECTION"] = \
            diagnostic_k_sweep("T3", 1.0, 1.0, tsub_star)

    # =============================== T5_SGNS_FROM_SCRATCH =============================================
    print("[T5] attempting SGNS-from-scratch (skipped if not cheap)", flush=True)
    t5 = run_sgns_arm(row_idx, matchedP, matchedS)
    rep["T5_SGNS_FROM_SCRATCH"] = t5
    if t5.get("SKIPPED"):
        print("[T5] SKIPPED: %s" % t5.get("reason"), flush=True)
    else:
        print("[T5] IN_IN AUC=%.4f" % t5["T5_IN_IN"]["auc"], flush=True)
        rep["T5_WINNER_COMPOSITION"] = None  # requires model closures unavailable post-return;
        # disclosed: T5's winner composition is not computed (would need the trained model kept
        # alive outside run_sgns_arm's scope); the AUC numbers above are the required result.

    # =============================== K1 / N0 / A0 -- reused verbatim, winner composition added -------
    arm_scores = gate["arm_scores"]
    rep["K1_KNOWN_ANSWER"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["KNOWN_ANSWER_WORDNET_PATH_SIM"]
    rep["N0_RANDOM_VECTOR_STORE"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["RANDOM_VECTOR_STORE"]
    rep["A0_INCUMBENT"] = gate["gate_report"]["recomputed_AUC_PER_ARM"]["INCUMBENT_LIVE_STORE"]
    if "KNOWN_ANSWER_WORDNET_PATH_SIM" in arm_scores:
        sc = arm_scores["KNOWN_ANSWER_WORDNET_PATH_SIM"]
        rep["K1_WINNER_COMPOSITION"] = winner_composition(
            None, None, matchedP, matchedS, counts_full,
            score_fn_from_arrays(matchedP, matchedS, sc["P"], sc["S"]))
    if "RANDOM_VECTOR_STORE" in arm_scores:
        sc = arm_scores["RANDOM_VECTOR_STORE"]
        rep["N0_WINNER_COMPOSITION"] = winner_composition(
            None, None, matchedP, matchedS, counts_full,
            score_fn_from_arrays(matchedP, matchedS, sc["P"], sc["S"]))
    if "INCUMBENT_LIVE_STORE" in arm_scores:
        sc = arm_scores["INCUMBENT_LIVE_STORE"]
        rep["A0_WINNER_COMPOSITION"] = winner_composition(
            None, None, matchedP, matchedS, counts_full,
            score_fn_from_arrays(matchedP, matchedS, sc["P"], sc["S"]))

    # four floors, carried through from CAP's regression gate (this population's own recompute) -----
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = {
        name: gate["gate_report"]["recomputed_AUC_PER_ARM"][name]
        for name in ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
    }
    rep["TIE_CONVENTION_NOTE"] = ("This instrument's scorer is DSI.auc_of, a Mann-Whitney-U-style "
        "AUC with ties credited 0.5 each (P(P>S) + 0.5*P(tie)) -- ONE well-defined tie handling "
        "built into the formula itself. Unlike the hit@1 metric elsewhere in this project, there is "
        "no second tie convention applicable to an AUC scorer; stated explicitly rather than "
        "silently omitted.")

    # =============================== ARMS-MUST-DIFFER (new arms only) ================================
    def _eval_vec(arm_rep):
        sc = arm_rep.get("SELECTED_CONFIG")
        if not sc:
            return None
        return (sc["alpha"], sc["k_shift"], sc["subsample_t"], sc["k"], sc["p"],
               round(arm_rep["RESULT_held_out_selected_eval_AUC"]["auc"], 6))
    def _cfg_digest(v) -> str:
        return hashlib.sha256(repr(v).encode("utf-8")).hexdigest()[:16]
    digest_inputs = {"T0": t0_best_auc, "T1": _eval_vec(t1), "T2": _eval_vec(t2), "T3": _eval_vec(t3),
                     "T4": _eval_vec(t4)}
    digests = {k: _cfg_digest(v) for k, v in digest_inputs.items() if v is not None}
    rep["NEW_ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests
    assert len(set(digests.values())) > 1 or len(digests) < 2, \
        "T0-T4 produced IDENTICAL selected configs -- construction bug"

    # =============================== STOP-IF (ii, iii, iv) ============================================
    def _above_0p5(auc_res: Optional[Dict]) -> bool:
        return bool(auc_res and auc_res.get("band") == "ABOVE_0.5_SUBSTITUTABILITY")

    tuned_results = {"T1": t1, "T2": t2, "T3": t3, "T4": t4}
    winning_arms = [name for name, arm in tuned_results.items()
                    if _above_0p5(arm.get("RESULT_held_out_selected_eval_AUC"))]

    def _improves_over_t0(arm_rep) -> bool:
        res = arm_rep.get("RESULT_held_out_selected_eval_AUC")
        if not res or np.isnan(t0_best_auc):
            return False
        return res["ci95"][0] > t0_best_auc   # CI-separated above T0's best point estimate

    improving_arms = [name for name, arm in tuned_results.items() if _improves_over_t0(arm)]

    if winning_arms:
        interp = ("STOP_IF_ii_HELDOUT_SELECTED_ARM_CLEARS_0.5__DIRECTORS_SUPERVISION_CONCLUSION_IS_"
                  "WRONG__WINNING_ARMS=%s" % ",".join(winning_arms))
    elif improving_arms:
        interp = ("STOP_IF_iii_TUNING_IMPROVES_ON_VANILLA_BUT_STAYS_BELOW_0.5__SUPERVISION_"
                  "CONCLUSION_SURVIVES_A_FAIRER_TEST__IMPROVING_ARMS=%s" % ",".join(improving_arms))
    else:
        interp = ("STOP_IF_iv_TUNING_LITERATURE_DOES_NOT_TRANSFER_TO_THIS_CORPUS__NO_TUNED_ARM_"
                  "BEATS_VANILLA_T0")
    rep["WINNING_ARMS_CI_SEPARATED_ABOVE_0.5"] = winning_arms
    rep["ARMS_IMPROVING_OVER_T0_CI_SEPARATED"] = improving_arms
    rep["INTERPRETATION"] = interp

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
    try:
        if key in done and key in units:
            rep = units[key]
            print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
        else:
            rep = run(RUN_MODE)
            record_unit(str(out_dir), key, rep)
    except SystemExit as e:
        gate_metrics = {
            "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
            "findings_log": FINDINGS, "verdict": "INSTRUMENT_NOT_LICENSED",
            "verdict_msg": "GATE_FAIL: %s" % str(e),
            "elapsed_s": round(time.time() - t_start, 1),
        }
        write_metrics(out_dir, gate_metrics)
        print("[gate] INSTRUMENT_NOT_LICENSED -- %s" % str(e), flush=True)
        return 3

    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "TUNED_COUNT_UNSUPERVISED__%s" % interp

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Does a properly tuned, fully unsupervised count method (context-"
                       "distribution smoothing + shifted PPMI + subsampling + eigenvalue "
                       "weighting, all held-out-selected, never tuned on the 242 eval pairs) "
                       "clear 0.5 on the licensed dissociation instrument, falsifying the "
                       "Director's plan sec 6.18 supervision conclusion? -> " + interp),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "K_SWEEP_FULL": K_SWEEP_FULL,
                  "SEL_K": SEL_K, "ALPHA_GRID": ALPHA_GRID, "KSHIFT_GRID": KSHIFT_GRID,
                  "SUBSAMPLE_T_GRID": [str(t) for t in SUBSAMPLE_T_GRID], "P_GRID": P_GRID,
                  "T4_K_GRID": T4_K_GRID, "SGNS_VECTOR_SIZE": SGNS_VECTOR_SIZE},
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
