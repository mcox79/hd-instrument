"""exp_typed_role_selectional_asset_writerule_v1 -- does a word's code, built from the TYPED
grammatical slots (verb+ROLE) it fills, encode substitutability better than the incumbent
bag-of-words store?

Full spec: preregs/2026-08-18_typed_role_selectional_asset_writerule_v1.md. Read that file first;
this docstring summarises, it does not replace it.

=================================================================================================
SCOPE CAVEAT -- CORPUS CONFOUND, disclosed prominently, never hidden. A0_INCUMBENT is DSI's
regression-gated arm, built from the project's own 34,169-sentence corpus
(exp_cue_information_audit_v1). T1/T2/T3's typed-role features are built from
data/selectional_preferences_v1/ -- a DIFFERENT, larger (64MB, 737,488-sentence) SimpleWiki
corpus, extracted 2026-08-16 by this project's own real parser (no WordNet, no LLM). A T1-vs-A0
gap therefore conflates "typed vs bag context" with "which corpus" -- every verdict below states
this caveat, never interprets a T1-vs-A0 gap as a clean single-variable result on its own.

A parallel, same-corpus cell exists: experiments/exp_typed_role_context_write_rule_dissociation_v1.py
(teammate "typed-role-writerule", self-test green as of this cell's authoring, not yet landed)
parses THIS project's own 34,169-sentence corpus directly via hdlab.arc_parser/arc_labeler/
pos_tagger, avoiding the confound entirely -- that is the cell to trust for a clean typed-vs-bag
comparison. THIS cell is a cheaper, confounded, complementary check: does the pre-built,
larger-corpus selectional-slot asset carry substitutability signal at all, independent of corpus.
Overlap disclosed peer-to-peer via SendMessage before authoring; teammate confirmed this is a
genuinely different test (different corpus, different coverage), not a duplicate -- both are more
informative than either alone (does an effect, if any, survive the smaller/matched corpus, or
does it need the bigger asset's coverage?).

=================================================================================================
PRIOR-WORK CHECK -- done by the Director (main session), not repeated here per dispatch brief
("PRIOR-WORK CHECK IS DONE -- DO NOT REPEAT IT... Do NOT use tools/substrate_query.sh: it returns
ZERO BYTES and exits 0"). Prior art credited:
  experiments/exp_dependency_context_codebook_location_artifact_v1.py (+ its
  _weight_sweep_location_artifact_v2.py): "Dependency-context vs window-context PPMI-SVD
  codebook... SAME pipeline, differing ONLY in the co-occurrence feature: window (word, word) vs
  dependency-typed (word, relation+direction)". NEVER RUN (no data/ dir for it) -- unproven, not
  refuted. Cites Levy & Goldberg 2014 (typed relations shift induced similarity from
  "relatedness" toward "similarity/co-type") and Komninos & Manandhar 2016 (window+dependency
  COMBINED beats either alone); both credited here too, first-hand from that cell's own
  docstring. This cell reuses experiments.exp_learned_codebook_generalization_gate_v1.build_ppmi
  (Levy-Goldberg 2015 context-distribution-smoothed PPMI) UNMODIFIED -- the exact same function
  the prior-art cell itself reused, so the PPMI step is byte-identical across both cells.

=================================================================================================
POPULATION / SCORER -- reused verbatim from exp_dissociation_score_instrument_v1 (DSI), NEVER
re-derived, NEVER re-matched:
  checkpoint data/exp_dissociation_score_instrument_v1/units.jsonl, key POPULATION|v1.7|full:
    242 matched (SET P, SET S) NOUN pairs per cell (all 242 pairs are nouns -- the matching
    dropped every non-noun POS stratum; see DSI's own per_pos_stratum diagnostic).
  key SCORES|v1.7|full: the 8 regression-gate raw P/S score arrays, recomputed here via
    DSI.auc_of (deterministic, bootstrap-independent) and asserted delta<=0.0005 against the
    cached values BEFORE anything else in this file runs. Any miss -> SystemExit; this cell then
    publishes ONLY the regression-gate failure.
  DSI.auc_of / DSI.auc_bootstrap (Mann-Whitney AUC + paired bootstrap CI): reused directly, not
    re-implemented. DSI.dense_scores_from_dict_store: reused for pair scoring from any
    word->vector dict. DSI.l2n: reused for row-wise L2 normalisation.
NOTE: exp_selectional_constraint_bridge_v1 already FAILED on data/selectional_preferences_v1
(this SAME asset) for a DIFFERENT task (bridging via Spearman rho, 337 words). Disclosed up
front per the dispatch brief: a mechanism's failure at one job says nothing about another,
shown twice already on this asset (once for bridging, now tested here for dissociation typing).

=================================================================================================
ASSET -- data/selectional_preferences_v1/selectional_slots_v1.pkl: slot_filler dict keyed
(verb, ROLE) -> {filler_word: count}, ROLE in {SUBJ, OBJ, IOBJ, obl:*}. 41,529 slots, 944,990
observations, built by this project's own parser (no WordNet, no LLM) over a 64MB SimpleWiki
corpus. MEASURED (this cell's own pre-authoring probe, scratch, foreground, <1s): 617 distinct
words needed across the 242+242 matched pairs; 555/617 (90.0%) have >=1 slot-filler count in this
asset; 218/242 SET P pairs and 185/242 SET S pairs have BOTH members covered (the N5 artifact
risk the dispatch brief flags explicitly).

=================================================================================================
ARMS (one variable = context TYPE / write rule; T1/T2/N1/N3 share one PPMI+SVD pipeline and rank
so dimensionality never confounds the comparison -- design-gate #4 convention, credited from the
prior-art cell):
  A0_INCUMBENT               DSI's cached INCUMBENT_LIVE_STORE arm, cited not rebuilt.
  T1_TYPED_ROLE               word x (verb,ROLE) count matrix (MEASURED: 101,021 nonzero entries,
                              20,600 distinct columns used, 555/617 rows nonzero) -> build_ppmi
                              -> TruncatedSVD rank 128 -> L2-normalised rows. THE ARM THIS CELL
                              EXISTS FOR.
  T2_UNTYPED_SAME_COVERAGE    T1's matrix with the ROLE axis collapsed to VERB only (MEASURED:
                              5,536 distinct verbs), IDENTICAL contributing words/support, role
                              label stripped. Same pipeline, same rank. Isolates word-selection
                              from typing -- without this a T1 win is uninterpretable.
  T3_COMBINED                 L2norm(T1) concat L2norm(A0), L2-renormalised (Komninos & Manandhar
                              2016 recipe; same combine_method string as the prior-art cell).
  N1_LABEL_PERMUTED            T1's raw count matrix, nonzero entries' COLUMN index permuted
                              (fixed seed; same design pattern as the prior-art cell's
                              build_random_context_cooc -- preserves row mass, destroys
                              word<->slot-type association), then same pipeline. Must-fail
                              identity control.
  N3_MAGNITUDE_PERMUTED        T1's raw count matrix, nonzero entries' DATA (count) values
                              permuted across the SAME (row,col) support (fixed seed) --
                              preserves exactly which word fills which slot, destroys the
                              magnitude/frequency information. New control (not reused from
                              prior art); tests count-weighting vs mere presence.
  N5_COVERAGE_MATCHED          T1's own embeddings, pairs restricted to BOTH-covered members
                              (MEASURED: SET P 218/242, SET S 185/242). Reports n before/after.
  K1 (KNOWN_ANSWER_WORDNET_PATH_SIM), N0 (RANDOM_VECTOR_STORE): cited from the regression gate,
    calibration/null only, never rebuilt.

=================================================================================================
BANDS. Bar = max(4 floor AUCs) = 0.5431 (F_CONSTANT_PROTOTYPE), NOT 0.5. Every margin reported
against BOTH. "CI-separated above X": 95% CI lower bound > X. "A dominates B": A's whole CI is
above B's whole CI (A_lo > B_hi, non-overlapping).

STOP-IF (evaluated in this order):
  0. Regression gate OR DSI's own landed floor-licensing fails -> publish ONLY that.
  1. T1 CI-separated above bar AND dominates T2 AND dominates N1 AND N5 independently
     CI-separates above bar -> HARD_PASS_FIRST_TYPED_WRITE_RULE.
  2. T1 dominates A0 but NOT T2 -> WORD_SELECTION_NOT_TYPE.
  3. T1 dominates A0 but N5 does not independently clear the bar -> COVERAGE_ARTIFACT.
  4. T1 ties A0 (CIs overlap) -> TYPED_STRUCTURE_NO_HELP.
  5. otherwise -> PARTIAL_UNRESOLVED.

PRE-REGISTERED PRIORS (deflated, stated before running): HARD_PASS=0.15, WORD_SELECTION_NOT_TYPE
=0.20, clean negative (COVERAGE_ARTIFACT or TYPED_STRUCTURE_NO_HELP)=0.45, PARTIAL_UNRESOLVED=0.20.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over {T1,T2,T3,N1,N3} + A0-from-checkpoint score vectors
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: SCORES_TYPED (this cell's own new arm scores) as one checkpointed unit;
#   POPULATION/SCORES read-only reused from DSI's own checkpoint, never rewritten
# - discriminator survives scale: full population run, no scale-preview needed (population is
#   fixed/licensed by DSI, not swept by this cell)
# - calibration_check: default_ok_for_this_regime (reuses DSI's licensed instrument unmodified)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - baseline_in_band: n/a -- dissociation-AUC licensing instrument, not a 0.05-0.95-band baseline
# - crlb_floor_computed: n/a -- AUC dissociation measurement, not a capacity sweep
# - deterministic_seeding: true (fixed integer seeds throughout; no hash()/list(set()) ordering)

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. No store is
rebuilt; data/foundation/** is never opened. Writes only under
data/exp_typed_role_selectional_asset_writerule_v1[_reduced]/. Not wired into hdlab/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/sklearn/DSI/CTS next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

import argparse
import hashlib
import pickle
import sys
import time
import traceback
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI               # noqa: E402 READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                    # noqa: E402 READ ONLY
import experiments.exp_learned_codebook_generalization_gate_v1 as CB         # noqa: E402 READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics       # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "typed_role_selectional_asset_writerule_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/typed_role_selectional_asset_writerule_2026-08-18.md"

DSI_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")
DSI_CODE_VERSION = "v1.7"
ASSET_PATH = os.path.join(REPO, "data", "selectional_preferences_v1", "selectional_slots_v1.pkl")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
N_TARGET = 128                       # SVD rank, SAME for T1/T2/N1/N3 (design-gate #4)
REG_GATE_TOL = 0.0005                # POINT-AUC tolerance (bootstrap-independent, deterministic)

# THE BAR (regression-gated, never hardcoded past the assert below without a citation):
# F_ORTHOGRAPHIC=0.5000 F_FREQUENCY=0.4901 F_SCRAMBLE=0.4664 F_CONSTANT_PROTOTYPE=0.5431 (MAX ->
# the bar) K1(KNOWN_ANSWER_WORDNET_PATH_SIM)=0.9599 N0(RANDOM_VECTOR_STORE)=0.4862
# A0(INCUMBENT_LIVE_STORE)=0.0710 RAW_COUNT_FULL_ACCUM=0.0510
# MEASURED@d:/AI/hd-instrument/data/exp_dissociation_score_instrument_v1/metrics.json:
#   report.AUC_PER_ARM.<name>.auc
EXPECTED_CACHED = {
    "F_ORTHOGRAPHIC": 0.5000, "F_FREQUENCY": 0.4901, "F_SCRAMBLE": 0.4664,
    "F_CONSTANT_PROTOTYPE": 0.5431, "KNOWN_ANSWER_WORDNET_PATH_SIM": 0.9599,
    "RANDOM_VECTOR_STORE": 0.4862, "INCUMBENT_LIVE_STORE": 0.0710,
    "RAW_COUNT_FULL_ACCUM": 0.0510,
}
FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


def l2n(A: np.ndarray) -> np.ndarray:
    return DSI.l2n(A)


# =================================================================================================
# DSI CHECKPOINT REUSE (population + the 8 regression-gate score arrays)
# =================================================================================================
def load_dsi_population() -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]], Dict]:
    units = load_units(DSI_DIR)
    key = unit_key("POPULATION", DSI_CODE_VERSION, "full")
    rec = units.get(key)
    if rec is None:
        raise SystemExit("DSI POPULATION CHECKPOINT MISSING: key=%r in %r -- run "
                         "exp_dissociation_score_instrument_v1.py first (never rebuild it here)."
                         % (key, DSI_DIR))
    matchedP = [tuple(x) for x in rec["matchedP"]]
    matchedS = [tuple(x) for x in rec["matchedS"]]
    return matchedP, matchedS, rec["diag"]


def load_dsi_scores() -> Dict[str, Dict[str, np.ndarray]]:
    units = load_units(DSI_DIR)
    key = unit_key("SCORES", DSI_CODE_VERSION, "full")
    rec = units.get(key)
    if rec is None:
        raise SystemExit("DSI SCORES CHECKPOINT MISSING: key=%r in %r." % (key, DSI_DIR))
    return {k: {"P": np.array(v["P"], dtype=np.float64), "S": np.array(v["S"], dtype=np.float64)}
            for k, v in rec.items()}


def dsi_regression_gate(arm_scores: Dict[str, Dict[str, np.ndarray]], expected: Dict[str, float],
                        tol: float) -> Dict:
    """Recompute POINT AUC (DSI.auc_of, deterministic, bootstrap-independent) for the 8 named
    cached checks; a mismatch beyond `tol` means the checkpoint is not the licensed instrument
    this cell was pre-registered against. Returns a diagnostic dict; raises SystemExit on ANY
    miss (per dispatch brief: EXIT ON FAILURE, never loosen the matching)."""
    measured = {}
    failures = []
    for name, exp_val in expected.items():
        sc = arm_scores.get(name)
        if sc is None:
            failures.append({"name": name, "reason": "ARM_MISSING_FROM_CHECKPOINT"})
            continue
        got = DSI.auc_of(sc["P"], sc["S"])
        measured[name] = round(got, 4)
        delta = abs(got - exp_val)
        if delta > tol:
            failures.append({"name": name, "expected": exp_val, "measured": round(got, 6),
                             "delta": round(delta, 6), "tol": tol})
    gate = {"PASS": len(failures) == 0, "measured": measured, "expected": expected,
           "failures": failures, "tol": tol}
    if not gate["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- checkpoint does not reproduce DSI's licensed "
                         "cached values within tol=%.4f: %r" % (tol, failures))
    return gate


# =================================================================================================
# TYPED-ROLE MATRIX CONSTRUCTION
# =================================================================================================
def load_selectional_asset(path: str = ASSET_PATH) -> Dict:
    if not os.path.exists(path):
        raise SystemExit("SELECTIONAL ASSET MISSING: %s" % path)
    with open(path, "rb") as fh:
        return pickle.load(fh)


def build_typed_role_matrix(words_needed: Sequence[str], slot_filler: Dict
                            ) -> Tuple[sp.csr_matrix, List[Tuple[str, str]]]:
    """rows=words_needed (fixed order), cols=(verb,ROLE) slot types that have >=1 nonzero count
    among words_needed. Only slots/fillers ACTUALLY NEEDED are materialised (not the full
    41,529-column asset), so this stays proportional to the population size, not the asset size."""
    wset = set(words_needed)
    widx = {w: i for i, w in enumerate(words_needed)}
    col_index: Dict[Tuple[str, str], int] = {}
    col_names: List[Tuple[str, str]] = []
    rows, cols, data = [], [], []
    for (verb, role), fillers in slot_filler.items():
        for w, c in fillers.items():
            if w not in wset or c <= 0:
                continue
            key = (verb, role)
            ci = col_index.get(key)
            if ci is None:
                ci = len(col_names)
                col_index[key] = ci
                col_names.append(key)
            rows.append(widx[w])
            cols.append(ci)
            data.append(float(c))
    mat = sp.coo_matrix((np.asarray(data, dtype=np.float64), (rows, cols)),
                        shape=(len(words_needed), len(col_names))).tocsr()
    mat.sum_duplicates()
    return mat, col_names


def collapse_roles(mat_typed: sp.csr_matrix, col_names: List[Tuple[str, str]]
                   ) -> Tuple[sp.csr_matrix, List[str]]:
    """T2: collapse the (verb,ROLE) column axis to VERB only. IDENTICAL contributing
    words/support as T1 (same rows, same total mass per row); only the column granularity
    (ROLE LABEL STRIPPED) changes."""
    verb_index: Dict[str, int] = {}
    verb_names: List[str] = []
    col_map = np.zeros(len(col_names), dtype=np.int64)
    for i, (verb, _role) in enumerate(col_names):
        vi = verb_index.get(verb)
        if vi is None:
            vi = len(verb_names)
            verb_index[verb] = vi
            verb_names.append(verb)
        col_map[i] = vi
    coo = mat_typed.tocoo()
    new_cols = col_map[coo.col] if coo.nnz else coo.col
    mat = sp.coo_matrix((coo.data, (coo.row, new_cols)),
                        shape=(mat_typed.shape[0], len(verb_names))).tocsr()
    mat.sum_duplicates()
    return mat, verb_names


def permute_columns(mat: sp.csr_matrix, seed: int) -> sp.csr_matrix:
    """N1_LABEL_PERMUTED: permute the COLUMN index of every nonzero entry (fixed-seed
    rng.permutation). Same design pattern as the prior-art cell's build_random_context_cooc --
    preserves each row's total mass and the overall column-marginal distribution, destroys the
    specific word<->slot-type association. Must-fail identity control."""
    coo = mat.tocoo()
    rng = np.random.default_rng(seed)
    shuffled_cols = rng.permutation(coo.col) if coo.nnz else coo.col
    out = sp.coo_matrix((coo.data, (coo.row, shuffled_cols)), shape=mat.shape).tocsr()
    out.sum_duplicates()
    return out


def permute_magnitudes(mat: sp.csr_matrix, seed: int) -> sp.csr_matrix:
    """N3_MAGNITUDE_PERMUTED: permute the DATA (count) values across the SAME (row,col) support
    (fixed-seed rng.permutation of coo.data only). Preserves EXACTLY which word fills which slot
    (the qualitative structure/support is unchanged); destroys the magnitude/frequency
    information. Tests whether count-weighting carries signal beyond mere presence/absence."""
    coo = mat.tocoo()
    rng = np.random.default_rng(seed)
    shuffled_data = rng.permutation(coo.data) if coo.nnz else coo.data
    out = sp.coo_matrix((shuffled_data, (coo.row, coo.col)), shape=mat.shape).tocsr()
    return out


def ppmi_svd(cooc: sp.csr_matrix, target_rank: int, seed: int) -> Tuple[np.ndarray, int]:
    """build_ppmi (CB.build_ppmi, Levy-Goldberg 2015 smoothed, reused unmodified) -> TruncatedSVD
    -> L2-normalised rows. Shape-generic: n_features = cooc.shape[1], correct for the rectangular
    word x slot-type matrices here (not the square V x V matrix CB's own docstring assumes)."""
    ppmi = CB.build_ppmi(cooc)
    n_samples, n_features = ppmi.shape
    k = max(1, min(target_rank, n_features - 1, n_samples - 1))
    if ppmi.nnz == 0:
        return np.zeros((n_samples, target_rank), dtype=np.float64), 0
    svd = TruncatedSVD(n_components=k, algorithm="randomized", n_iter=5, random_state=seed)
    M = svd.fit_transform(ppmi).astype(np.float64)
    if k < target_rank:
        M = np.concatenate([M, np.zeros((M.shape[0], target_rank - k), dtype=np.float64)], axis=1)
    return l2n(M), k


def store_from_matrix(emb: np.ndarray, words_needed: Sequence[str]) -> Dict[str, np.ndarray]:
    return {w: emb[i] for i, w in enumerate(words_needed)}


def covered_words(mat_typed_raw: sp.csr_matrix, words_needed: Sequence[str]) -> set:
    row_mass = np.asarray(mat_typed_raw.sum(axis=1)).ravel()
    return {w for w, m in zip(words_needed, row_mass) if m > 0}


def restrict_pairs_both_covered(pairs: List[Tuple[str, str, str]], covered: set
                                ) -> List[Tuple[str, str, str]]:
    return [(w1, w2, p) for w1, w2, p in pairs if w1 in covered and w2 in covered]


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- real code path 1: build_typed_role_matrix / collapse_roles / permute_* on a TINY,
    # hand-built slot_filler dict with a known covered/uncovered split -----------------------------
    tiny_slot_filler = {
        ("build", "OBJ"): {"castle": 5, "tower": 3, "chapel": 1},
        ("build", "SUBJ"): {"team": 2, "workers": 4},
        ("live", "obl:in"): {"castle": 4, "forest": 2, "island": 1},
        ("attack", "OBJ"): {"castle": 6, "fort": 2},
    }
    tiny_words = ["castle", "tower", "chapel", "team", "workers", "forest", "island", "fort",
                 "uncovered_word"]
    mat_t1, col_names = build_typed_role_matrix(tiny_words, tiny_slot_filler)
    assert mat_t1.shape == (len(tiny_words), 4), "expected 4 distinct (verb,role) cols "\
        "(build/OBJ, build/SUBJ, live/obl:in, attack/OBJ): %r" % (mat_t1.shape,)
    assert mat_t1[tiny_words.index("castle")].sum() == 15, (
        "castle fills build/OBJ=5 + live/obl:in=4 + attack/OBJ=6 = 15: got %r" %
        mat_t1[tiny_words.index("castle")].sum())
    assert mat_t1[tiny_words.index("uncovered_word")].sum() == 0
    ev["typed_matrix_real_code_path"] = {"shape": list(mat_t1.shape), "n_cols": len(col_names)}

    mat_t2, verb_names = collapse_roles(mat_t1, col_names)
    assert sorted(verb_names) == ["attack", "build", "live"]
    # row mass identical (same total counts, just regrouped columns)
    assert np.allclose(np.asarray(mat_t1.sum(axis=1)).ravel(),
                       np.asarray(mat_t2.sum(axis=1)).ravel()), (
        "collapse_roles must preserve each row's total mass")
    assert mat_t2.shape[1] < mat_t1.shape[1], "role-collapse must reduce column count"
    ev["collapse_roles_preserves_row_mass"] = True

    mat_n1 = permute_columns(mat_t1, seed=0)
    assert abs(mat_n1.sum() - mat_t1.sum()) < 1e-6, "N1 must preserve total mass"
    row_mass_before = np.asarray(mat_t1.sum(axis=1)).ravel()
    row_mass_after = np.asarray(mat_n1.sum(axis=1)).ravel()
    # ROW is untouched by permute_columns (only the col array is shuffled, data/row stay
    # index-aligned), so each row's OWN total mass is preserved EXACTLY -- the invariant this
    # control is designed to hold (same design pattern as the prior-art cell's
    # build_random_context_cooc: "preserves the anchor's own... mass"). What changes is WHICH
    # slot-type column that mass lands in -- i.e. the matrix CONTENT, not the row marginal.
    assert np.allclose(row_mass_before, row_mass_after), (
        "N1 column-permutation must preserve each row's own total mass exactly (row index is "
        "never touched, only col is permuted): before=%r after=%r" %
        (row_mass_before, row_mass_after))
    assert _digest(mat_t1.toarray().ravel()) != _digest(mat_n1.toarray().ravel()), (
        "N1 must actually change the matrix content (word<->slot-type association destroyed)")
    ev["N1_permute_columns_preserves_row_mass_changes_association"] = True

    mat_n3 = permute_magnitudes(mat_t1, seed=0)
    support_before = set(zip(*mat_t1.nonzero()))
    support_after = set(zip(*mat_n3.nonzero()))
    assert support_before == support_after, (
        "N3 magnitude-permutation must preserve the EXACT (row,col) support: %r vs %r" %
        (support_before, support_after))
    assert abs(mat_n3.sum() - mat_t1.sum()) < 1e-6, "N3 must preserve total mass"
    assert not np.allclose(np.sort(mat_t1.data), np.sort(mat_n3.data)) or mat_t1.nnz <= 1 or \
        _digest(mat_t1.toarray().ravel()) != _digest(mat_n3.toarray().ravel()), (
        "N3 must actually permute SOME magnitudes (unless the fixture is degenerate)")
    ev["N3_permute_magnitudes_preserves_support"] = True

    # --- real code path 2: ppmi_svd on both the square-ish typed and the smaller untyped matrix --
    emb_t1, k_t1 = ppmi_svd(mat_t1, target_rank=4, seed=0)
    emb_t2, k_t2 = ppmi_svd(mat_t2, target_rank=4, seed=0)
    assert emb_t1.shape == (len(tiny_words), 4)
    assert emb_t2.shape == (len(tiny_words), 4)
    assert not np.allclose(emb_t1, emb_t2), "T1 and T2 embeddings must differ (arms-must-differ)"
    ev["ppmi_svd_real_code_path"] = {"k_t1": k_t1, "k_t2": k_t2}

    # --- real code path 3: covered_words / restrict_pairs_both_covered ----------------------------
    covered = covered_words(mat_t1, tiny_words)
    assert "uncovered_word" not in covered and "castle" in covered
    fake_pairs = [("castle", "tower", "n"), ("uncovered_word", "castle", "n")]
    restricted = restrict_pairs_both_covered(fake_pairs, covered)
    assert restricted == [("castle", "tower", "n")], "must drop any pair with an uncovered member"
    ev["coverage_restriction_known_answer"] = {"covered": sorted(covered), "restricted": restricted}

    # --- real code path 4: REAL DSI checkpoint + REAL regression-gate function (Gate F.1: the
    # actual substrate objects this cell depends on, not a synthetic stand-in) --------------------
    matchedP, matchedS, pop_diag = load_dsi_population()
    assert len(matchedP) == len(matchedS) == 242, (
        "DSI's licensed population must be 242 pairs per cell: got %d/%d" %
        (len(matchedP), len(matchedS)))
    arm_scores = load_dsi_scores()
    gate = dsi_regression_gate(arm_scores, EXPECTED_CACHED, REG_GATE_TOL)
    assert gate["PASS"], "real regression gate must PASS against the real checkpoint: %r" % gate
    ev["dsi_regression_gate_real_code_path"] = gate["measured"]

    # --- real code path 5: real selectional asset loads and has the expected top-level shape -----
    asset = load_selectional_asset()
    assert "slot_filler" in asset and asset.get("n_slots", 0) > 0
    ev["selectional_asset_real_code_path"] = {"n_slots": asset["n_slots"],
                                              "corpus": asset.get("corpus", "?")}

    # --- arms-must-differ (META_RULE_AF) -----------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr)
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- AUC scorer reuse sanity (DSI owns correctness; this only proves the import/reuse works) --
    sep = DSI.auc_of(np.array([0.9, 0.8, 0.95]), np.array([0.1, 0.2, 0.05]))
    assert abs(sep - 1.0) < 1e-9
    ev["dsi_auc_of_reuse_sanity"] = round(sep, 4)

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test) ------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# AUC helpers
# =================================================================================================
def score_and_auc(store: Dict[str, np.ndarray], matchedP: List[Tuple[str, str, str]],
                  matchedS: List[Tuple[str, str, str]], n_boot: int, seed: int) -> Dict:
    sp_ = DSI.dense_scores_from_dict_store(store, matchedP)
    ss_ = DSI.dense_scores_from_dict_store(store, matchedS)
    return DSI.auc_bootstrap(sp_, ss_, n_boot, seed)


def ci_separated_above(res: Dict, x: float) -> bool:
    return res["ci95"][0] > x


def ci_dominates(a: Dict, b: Dict) -> bool:
    return a["ci95"][0] > b["ci95"][1]


def ci_ties(a: Dict, b: Dict) -> bool:
    return not ci_dominates(a, b) and not ci_dominates(b, a)


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))

    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "corpus_confound_disclosed": True,
                "overlapping_teammate_cell": "experiments/exp_typed_role_context_write_rule_"
                                             "dissociation_v1.py (typed-role-writerule, "
                                             "same-corpus design, not yet landed as of this run)"}

    # =============================== REGRESSION GATE (EXIT ON FAILURE) ==============================
    matchedP, matchedS, pop_diag = load_dsi_population()
    arm_scores = load_dsi_scores()
    gate = dsi_regression_gate(arm_scores, EXPECTED_CACHED, REG_GATE_TOL)
    rep["REGRESSION_GATE"] = gate
    print("[gate] REGRESSION_GATE PASS=%r measured=%r" % (gate["PASS"], gate["measured"]),
         flush=True)
    if not gate["PASS"]:
        raise SystemExit("unreachable -- dsi_regression_gate already raises on failure")

    n_before_P, n_before_S = len(matchedP), len(matchedS)
    rep["N_MATCHED_PAIRS_BEFORE"] = {"P": n_before_P, "S": n_before_S}
    if grid == "reduced":
        matchedP = matchedP[:40]
        matchedS = matchedS[:40]
        print("[population] REDUCED grid: truncated to %d/%d pairs" %
             (len(matchedP), len(matchedS)), flush=True)

    words_needed = sorted(set(w for w1, w2, _p in matchedP + matchedS for w in (w1, w2)))
    print("[words] %d distinct words needed" % len(words_needed), flush=True)

    # =============================== TYPED-ROLE MATRIX (checkpointed unit) ==========================
    scores_key = unit_key("SCORES_TYPED", CODE_VERSION, grid)
    prior_scores = load_units(out_dir_ckpt).get(scores_key)
    if prior_scores is not None:
        print("[scores] RESUMED FROM CHECKPOINT", flush=True)
        auc_results = prior_scores["auc_results"]
        build_diag = prior_scores["build_diag"]
    else:
        asset = load_selectional_asset()
        slot_filler = asset["slot_filler"]
        print("[asset] n_slots=%d loaded" % asset.get("n_slots", -1), flush=True)

        mat_t1_raw, col_names = build_typed_role_matrix(words_needed, slot_filler)
        mat_t2_raw, verb_names = collapse_roles(mat_t1_raw, col_names)
        mat_n1_raw = permute_columns(mat_t1_raw, seed=MASTER_SEED + 6001)
        mat_n3_raw = permute_magnitudes(mat_t1_raw, seed=MASTER_SEED + 6002)
        covered = covered_words(mat_t1_raw, words_needed)
        n_covered_words = len(covered)
        print("[typed] T1 shape=%r n_cols=%d n_covered_words=%d/%d" %
             (mat_t1_raw.shape, len(col_names), n_covered_words, len(words_needed)), flush=True)
        print("[typed] T2 (role-collapsed) n_verbs=%d" % len(verb_names), flush=True)

        emb_t1, k_t1 = ppmi_svd(mat_t1_raw, N_TARGET, seed=MASTER_SEED + 6101)
        emb_t2, k_t2 = ppmi_svd(mat_t2_raw, N_TARGET, seed=MASTER_SEED + 6102)
        emb_n1, k_n1 = ppmi_svd(mat_n1_raw, N_TARGET, seed=MASTER_SEED + 6103)
        emb_n3, k_n3 = ppmi_svd(mat_n3_raw, N_TARGET, seed=MASTER_SEED + 6104)
        print("[svd] achieved ranks T1=%d T2=%d N1=%d N3=%d" % (k_t1, k_t2, k_n1, k_n3), flush=True)

        # ---- A0 incumbent word vectors (for T3 combination only -- A0's ARM SCORE is cited from
        # the checkpoint, never rebuilt; only the per-word VECTOR is needed here to concatenate) ---
        C = CTS.load_cache()
        anchors = C["anchors"]
        mat_ok = np.asarray(C["mat_ok"], dtype=bool)
        mat = np.asarray(C["mat"], dtype=np.float32)
        pos_idx: Dict[str, int] = C["pos"]
        Mn_incumbent = l2n(mat)
        store_a0 = {w: Mn_incumbent[pos_idx[w]] for w in words_needed
                   if w in pos_idx and mat_ok[pos_idx[w]]}

        store_t1 = store_from_matrix(emb_t1, words_needed)
        store_t2 = store_from_matrix(emb_t2, words_needed)
        store_n1 = store_from_matrix(emb_n1, words_needed)
        store_n3 = store_from_matrix(emb_n3, words_needed)

        def _l2_row(v: np.ndarray) -> np.ndarray:
            n = np.linalg.norm(v)
            return v / n if n > 1e-12 else v

        # combine_method: concatenate_unit_normalized_channels_then_renormalize (prior-art recipe,
        # exp_dependency_context_codebook_location_artifact_v1's "combined" arm)
        store_t3 = {w: _l2_row(np.concatenate([_l2_row(store_t1[w]), _l2_row(
            store_a0.get(w, np.zeros(mat.shape[1], dtype=np.float64)))])) for w in words_needed}

        stores = {"T1_TYPED_ROLE": store_t1, "T2_UNTYPED_SAME_COVERAGE": store_t2,
                 "T3_COMBINED": store_t3, "N1_LABEL_PERMUTED": store_n1,
                 "N3_MAGNITUDE_PERMUTED": store_n3}

        boot_seed_base = MASTER_SEED + 7001
        auc_results = {}
        for i, (name, store) in enumerate(stores.items()):
            res = score_and_auc(store, matchedP, matchedS, N_BOOT, boot_seed_base + i)
            auc_results[name] = res
            print("[auc] %-28s AUC=%.4f CI=%r band=%s" %
                 (name, res["auc"], res["ci95"], res["band"]), flush=True)

        # ---- N5_COVERAGE_MATCHED: T1's OWN embeddings, pairs restricted to both-covered members --
        matchedP_cov = restrict_pairs_both_covered(matchedP, covered)
        matchedS_cov = restrict_pairs_both_covered(matchedS, covered)
        res_n5 = score_and_auc(store_t1, matchedP_cov, matchedS_cov, N_BOOT,
                               boot_seed_base + len(stores))
        auc_results["N5_COVERAGE_MATCHED"] = res_n5
        print("[auc] %-28s AUC=%.4f CI=%r band=%s (n_P=%d n_S=%d, before P=%d S=%d)" %
             ("N5_COVERAGE_MATCHED", res_n5["auc"], res_n5["ci95"], res_n5["band"],
              len(matchedP_cov), len(matchedS_cov), len(matchedP), len(matchedS)), flush=True)

        build_diag = {
            "n_words_needed": len(words_needed), "n_covered_words": n_covered_words,
            "typed_matrix_shape": list(mat_t1_raw.shape), "n_typed_cols": len(col_names),
            "n_verb_cols_untyped": len(verb_names),
            "svd_achieved_ranks": {"T1": k_t1, "T2": k_t2, "N1": k_n1, "N3": k_n3},
            "N5_n_pairs": {"P_before": len(matchedP), "S_before": len(matchedS),
                          "P_after": len(matchedP_cov), "S_after": len(matchedS_cov)},
        }
        record_unit(out_dir_ckpt, scores_key, {"auc_results": auc_results, "build_diag": build_diag})

    rep["TYPED_ROLE_BUILD"] = build_diag

    # =============================== A0 (cited, never rebuilt) ======================================
    a0_res = DSI.auc_bootstrap(arm_scores["INCUMBENT_LIVE_STORE"]["P"],
                               arm_scores["INCUMBENT_LIVE_STORE"]["S"], N_BOOT, MASTER_SEED + 9001)
    auc_results["A0_INCUMBENT"] = a0_res

    rep["AUC_PER_ARM"] = auc_results

    # =============================== ARMS-MUST-DIFFER ================================================
    digest_arms = ["T1_TYPED_ROLE", "T2_UNTYPED_SAME_COVERAGE", "T3_COMBINED",
                  "N1_LABEL_PERMUTED", "N3_MAGNITUDE_PERMUTED", "A0_INCUMBENT"]
    digests = {}
    for name in digest_arms:
        res = auc_results[name]
        digests[name] = _digest([res["auc"]] + res["ci95"])
    assert len(set(digests.values())) > 1, "all arms produced identical AUC/CI -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests
    rep["arms_differ_verified"] = True

    # =============================== BAR + STOP-IF ====================================================
    bar = max(gate["measured"][f] for f in FLOOR_NAMES)
    rep["BAR_MAX_FOUR_FLOORS"] = bar

    t1 = auc_results["T1_TYPED_ROLE"]
    t2 = auc_results["T2_UNTYPED_SAME_COVERAGE"]
    n1 = auc_results["N1_LABEL_PERMUTED"]
    n5 = auc_results["N5_COVERAGE_MATCHED"]
    a0 = auc_results["A0_INCUMBENT"]

    t1_clears_bar = ci_separated_above(t1, bar)
    t1_beats_t2 = ci_dominates(t1, t2)
    t1_beats_n1 = ci_dominates(t1, n1)
    n5_confirms = ci_separated_above(n5, bar)
    t1_dominates_a0 = ci_dominates(t1, a0)
    t1_ties_a0 = ci_ties(t1, a0)

    rep["STOP_IF_CHECKS"] = {
        "t1_clears_bar_ci_separated": t1_clears_bar, "t1_beats_t2": t1_beats_t2,
        "t1_beats_n1": t1_beats_n1, "n5_confirms_above_bar": n5_confirms,
        "t1_dominates_a0": t1_dominates_a0, "t1_ties_a0": t1_ties_a0,
    }

    if t1_clears_bar and t1_beats_t2 and t1_beats_n1 and n5_confirms:
        verdict = "HARD_PASS_FIRST_TYPED_WRITE_RULE"
    elif t1_dominates_a0 and not t1_beats_t2:
        verdict = "WORD_SELECTION_NOT_TYPE"
    elif t1_dominates_a0 and not n5_confirms:
        verdict = "COVERAGE_ARTIFACT"
    elif t1_ties_a0:
        verdict = "TYPED_STRUCTURE_NO_HELP"
    else:
        verdict = "PARTIAL_UNRESOLVED"
    rep["INTERPRETATION"] = verdict

    margin_vs_bar = t1["auc"] - bar
    margin_vs_half = t1["auc"] - 0.5
    rep["MARGINS"] = {"T1_vs_bar_0.5431": round(margin_vs_bar, 4),
                      "T1_vs_chance_0.5": round(margin_vs_half, 4)}

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

    verdict = "TYPED_ROLE_SELECTIONAL_ASSET__%s" % rep.get("INTERPRETATION", "UNKNOWN")
    t1 = rep["AUC_PER_ARM"]["T1_TYPED_ROLE"]
    a0 = rep["AUC_PER_ARM"]["A0_INCUMBENT"]
    bar = rep["BAR_MAX_FOUR_FLOORS"]
    verdict_msg = (
        "T1_TYPED_ROLE AUC=%.4f CI=%r vs bar=%.4f (margin=%.4f) vs chance=0.5 (margin=%.4f) | "
        "A0_INCUMBENT AUC=%.4f (corpus-confounded vs T1, disclosed) | "
        "T2_UNTYPED AUC=%.4f | T3_COMBINED AUC=%.4f | N1 AUC=%.4f | N3 AUC=%.4f | "
        "N5_COVERAGE_MATCHED AUC=%.4f (n_before P=%d S=%d -> n_after P=%d S=%d) | "
        "STOP_IF=%s" % (
            t1["auc"], t1["ci95"], bar, rep["MARGINS"]["T1_vs_bar_0.5431"],
            rep["MARGINS"]["T1_vs_chance_0.5"], a0["auc"],
            rep["AUC_PER_ARM"]["T2_UNTYPED_SAME_COVERAGE"]["auc"],
            rep["AUC_PER_ARM"]["T3_COMBINED"]["auc"],
            rep["AUC_PER_ARM"]["N1_LABEL_PERMUTED"]["auc"],
            rep["AUC_PER_ARM"]["N3_MAGNITUDE_PERMUTED"]["auc"],
            rep["AUC_PER_ARM"]["N5_COVERAGE_MATCHED"]["auc"],
            rep["TYPED_ROLE_BUILD"]["N5_n_pairs"]["P_before"],
            rep["TYPED_ROLE_BUILD"]["N5_n_pairs"]["S_before"],
            rep["TYPED_ROLE_BUILD"]["N5_n_pairs"]["P_after"],
            rep["TYPED_ROLE_BUILD"]["N5_n_pairs"]["S_after"],
            rep["INTERPRETATION"]))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": verdict_msg[:220],
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "N_TARGET": N_TARGET,
                  "REG_GATE_TOL": REG_GATE_TOL},
        "selftest_evidence_keys": sorted(ev.keys()),
        "corpus_confound_disclosed": True,
        "report": rep,
        "REQUIRED_FIELDS": ["verdict", "AUC_PER_ARM", "REGRESSION_GATE", "arms_differ_verified",
                           "BAR_MAX_FOUR_FLOORS", "INTERPRETATION"],
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
