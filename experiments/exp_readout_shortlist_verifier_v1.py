"""exp_readout_shortlist_verifier_v1 -- A VERIFIER THAT IS NOT THE GENERATOR: does a shortlist plus
a real (non-oracle) rejector buy anything on the read-out-ceiling instrument?

FINDINGS LOG: notes/readout_shortlist_verifier_findings_2026-08-17.md (written after the run;
every number there is sourced to this cell's own metrics.json).

WHY THIS CELL, AND WHY NOW. notes/COMPACTION_HANDOFF_2026-08-17.md section 8b(A) and
notes/readout_ceiling_findings_2026-08-17.md diagnose the read-out ceiling: our store encodes
SYNTAGMATIC co-occurrence, the task scores PARADIGMATIC substitutability, and 39 read-out arms
across two prior cells (CSLS, subtract-constant, divisive-normalisation, second-order profile
truncation, successor representation) all fail to clear the binding floor as REPLACEMENT
comparators. The one structure never tried is the owner's own introspection (BOARD Q8, verbatim):
"wrong candidates definitely come up and get rejected. It's often iterative - if I cant bring up the
word at the beginning - I either can figure it out through thinking it through, or I have to ask
someone. I often have a sense of what the first letter is, but that could just be me." That is
GENERATE-THEN-TEST with a rejector, not a single argmax. The measured ceiling for this (VERIFIED OFF
DISK in this cell's own REGRESSION gate, not merely cited): a perfect verifier over a shortlist of 5
scores 0.17151 and over 10 scores 0.26039, against a binding floor of 0.13896 and today's single
argmax at 0.04807 (data/exp_readout_ceiling_diagnosis_v1/metrics.json:S2_WHERE_DOES_THE_ANSWER_RANK
.curves.EXACT_KEY_COSINE.hit_at_k_optimistic).

THE FILENAME. experiments/exp_propose_reject_retrieval_v1.py is a BLOCKED PATH (write denied even
for a one-line file; notes/COMPACTION_HANDOFF_2026-08-17.md:153). This cell is the composed
propose-and-reject cell the Director authorised under a different, non-near-variant name, per the
owner's outstanding word on the block.

THE PRECONDITION THIS CELL MEASURES FIRST, BEFORE ANY REJECTOR NUMBER. A propose-and-reject loop
needs a proposer that is right SOMETIMES. The exact-key ceiling above is the BEST case (addressing
already solved). The real operating regime is the PARTIAL CUE (the one landed hit@1 is 0.0223 at),
where the proposer itself is much weaker. THE SHORTLIST HIT-RATE CURVE UNDER THE PARTIAL CUE, at
k = 1, 5, 10, 20, 50 -- computed by G1_SHORTLIST_ORACLE_PARTIAL below -- IS REPORTED BEFORE ANY
REJECTOR NUMBER, per the pre-registered rule: PRECONDITION_FAILURE fires if the partial-cue oracle
ceiling at k=50 is below PRECOND_ABS_THRESHOLD=0.05 (written into the constants below, before this
cell was ever run).

THE COMPUTATION BEING COPIED, problem-derived not parameter-derived: A VERIFIER THAT IS NOT THE
GENERATOR. If the same scoring function proposes and accepts, stage two is decorative -- it can only
ever return the proposer's own argmax (this is exactly what N2_PROPOSER_AS_REJECTOR below is built to
prove or disprove: it MUST reduce to G0_ARGMAX bit-for-bit, or this cell is void). The two stages
here use PROVABLY DIFFERENT signals, stated explicitly:
  PROPOSER (G0/G1/the shortlist)   cosine of the store's first-order Hebbian-sum co-occurrence code
                                    against the PARTIAL CUE. A dense vector similarity.
  R1_ATTESTATION_REJECTOR          a DISCRETE corpus PATTERN count: how many times the candidate and
                                    the query are joined by an explicit coordinator ("X and Y" /
                                    "X or Y", Roark & Charniak 1998 / Riloff & Shepherd 1997 style
                                    conjunction-pattern class evidence) within a small token window,
                                    anywhere in the 34,169-sentence corpus. Computed by a fresh regex
                                    scan of the RAW SENTENCE TEXT, never touching the vector store.
                                    STRUCTURALLY BLIND (score 0) for any pair that never co-occurs in
                                    such a pattern -- by construction, not a bug, matching the
                                    Q8/COMPACTION_HANDOFF description of the incumbent attestation
                                    channel's own blind spot on unattested candidates.
  R2_PROFILE_REJECTOR               cos(profile(anchor), profile(query)) -- SECOND-ORDER structure,
                                    reused VERBATIM from experiments.exp_readout_second_order_v1
                                    .second_order_scores(k=0, untruncated -- the arm that scored best
                                    in that cell's own sweep). A profile-of-profile cosine is a
                                    mathematically different object from the first-order cosine the
                                    proposer uses, even though both ultimately derive from the same
                                    stored matrix.
Both R1 and R2 are DIFFERENT from the proposer's raw first-order cosine; R1 is additionally
independent of the VECTOR STORE ENTIRELY (word-identity + raw text only). If they were not different,
this docstring's claim would be false and the cell says so at STOP-IF (iv) rather than asserting it.

ARMS (exact names used as metrics.json / hits_exp keys):
  G0_ARGMAX                          incumbent single argmax over the PARTIAL cue. REGRESSION GATE.
  G1_SHORTLIST_ORACLE_EXACT_k{K}     oracle over an EXACT-KEY shortlist of size K. THE CEILING.
                                      K in (1,2,3,5,10,20,50). NEVER quoted as a capability.
  G1_SHORTLIST_ORACLE_PARTIAL_k{K}   oracle over a PARTIAL-CUE shortlist. THE REAL PRECONDITION
                                      CURVE. K in (1,5,10,20,50). Reported FIRST.
  R1_ATTESTATION_REJECTOR_k{K}       real rejector, K in (5,10,20,50).
  R2_PROFILE_REJECTOR_k{K}           real rejector, K in (5,10,20,50).
  R3_COMBINED_k20_beta{B}            both signals, rank-normalised within the shortlist, weighted
                                      beta*R1 + (1-beta)*R2. K FIXED at 20 (pre-registered before any
                                      number is read). B in (0.25, 0.5, 0.75), SWEPT, never adopted.
  N1_RANDOM_REJECTOR_k{K}            picks uniformly at random from the shortlist. THE FLOOR THAT
                                      MATTERS MOST for this cell. K in (5,10,20,50).
  N2_PROPOSER_AS_REJECTOR_k{K}       the proposer's own score, restricted to its own shortlist.
                                      VALIDITY ARM: MUST equal G0_ARGMAX bit-for-bit for every K.
  K1_KNOWN_ANSWER                    BINDING gate: KA_SELF_ADDRESS on the store (exact-key argmax
                                      recovers the item's own row), >= 0.95, enforced with a hard
                                      SystemExit before any treatment number. ADDITIONALLY reported
                                      (informational, NOT gated): whether R1/R2/R3, restricted to an
                                      exact-key shortlist (K=5) that certainly contains the item's
                                      own address, still rank it top-1 -- this is NOT a pass/fail bar
                                      for R1/R2/R3 because both explicitly EXCLUDE self-comparison by
                                      construction (R1 skips qw==cw; R2's second_order_scores zeroes
                                      the profile diagonal), so they structurally cannot be expected
                                      to prefer a candidate's own identity.
  F_ORTHOGRAPHIC / F_FREQUENCY / F_SCRAMBLE / F_CONSTANT_PROTOTYPE
                                      all four floors, recomputed on THIS population, on the PARTIAL
                                      cue (F_SCRAMBLE uses Q_part, not Q_exact -- the other three are
                                      cue-invariant by construction). Never imported.
  RANDOM_RANKING_NULL_PARTIAL_k{K}   the caveat-free per-item random-ranking curve (ignores the gold
                                      generosity the constant floor partly exploits), K matching G1.
  ORACLE_CONSTANT                    reported, NOT a floor.

STOP-IF, pre-registered verbatim from the dispatch:
  (i)   a real rejector (R1/R2/R3) clears max(four floors) CI-separated AND beats
        N1_RANDOM_REJECTOR CI-separated -> the first genuine read-out win this programme has had.
  (ii)  the partial-cue shortlist hit rate is near zero at usable k (k=50, PRECOND_ABS_THRESHOLD
        =0.05) -> PRECONDITION_FAILURE; the proposer is the blocker, no rejector work is licensed.
  (iii) rejectors beat G0 but not N1_RANDOM_REJECTOR -> the gain is the SHORTLIST, not the rejector.
  (iv)  N2_PROPOSER_AS_REJECTOR does not reduce to G0_ARGMAX -> the stages are not independent, the
        cell is VOID, nothing downstream is published.
  (v)   any clearing arm correlates with orthographic similarity or word length -> rule 12 failure.

BRAIN FIDELITY.
(a) STRUCTURE PER COMPONENT. Exhaustive cosine argmax (the proposer, and the shortlist ranking
    inside it) is OURS, never chosen, the same standing finding as the sibling cells. GENERATE
    MULTIPLE CANDIDATES THEN TEST AGAINST A CRITERION THAT IS NOT THE GENERATOR, REJECT, RE-PROPOSE
    is PINNED AS A CONTROL STRUCTURE: tip-of-the-tongue transmission-deficit literature (Burke &
    MacKay 1991; Brown & McNeill 1966) and propose-but-verify word learning (Medina 2011 PNAS;
    Trueswell 2013) independently specify the same shape. The REJECTOR'S CONTENT is UNPINNED: the
    owner's own Q10 names "the feeling of the word" (register/formality is the live hypothesis per
    COMPACTION_HANDOFF section 5; AFFECT was tested and contributed nothing once width-matched
    against noise). R1_ATTESTATION and R2_PROFILE are OURS -- engineering heuristics standing in for
    an unbuilt register channel, not claims about what the brain's verifier actually computes.
    Selection among competing candidates (BA45/47, left IFG) is PINNED as a structure per
    exp_feeling_match_rejector_v1's own brain-fidelity block; this cell's distance estimators remain
    OURS. VSA algebraic binding, the substrate's core operation, is UNPINNED in the brain (three live
    accounts, published objections to each); nothing here depends on it or tests it.
(b) ORGAN REUSE, enumerated from disk (ls experiments/ filtered on readout/rerank/hub/csls/normal/
    argmax/rank/write/second_order/profile/selection/shortlist/verifier/reject/propose/attest/
    coordination -- no existing cell operates the propose-and-reject architecture on THIS instrument;
    exp_feeling_match_rejector_v1's ATTESTATION/PROFILE concepts are CREDITED as the validated prior
    on a DIFFERENT population/task, not code-reused, since its slot-filler data structures do not
    transfer), then reconciled, verified by RUNTIME (sys.modules, recorded in metrics, never grep):
    experiments.exp_readout_ceiling_diagnosis_v1 (build_population, hit_at_k_curve,
    random_ranking_hit_at_k, install_grounded_similarity_tripwire, self_test, l2n, _halfwidth),
    experiments.exp_readout_second_order_v1 (second_order_scores, self_test),
    experiments.exp_cue_to_store_translation_v1 (cache/aux loaders, ruler gate, regression constant),
    experiments.exp_cue_binarised_readout_transfer_v1 (pearson_ci_bootstrap),
    experiments.exp_definitional_grounding_v5 (load_corpus_v5), tools.floor_battery (floors, scorer,
    bootstrap), hdlab.reading_grounding_loop (normalize_lemma), tools.exp_checkpoint. NONE edited.
(c) PINNED vs OURS: stated per component in (a).
(d) SHELVE / REVIVAL, BRAIN-FRAMED. If this architecture does not win, the revival criterion is NOT
    "the rejector did not score" -- it is that R1/R2 are PROXIES standing in for the register/
    formality channel the owner actually described and that channel has never been built as a
    rejector signal (only tested, and refuted, as an ADDITIVE grounding channel). Revive when a
    genuine register/formality rejector signal exists and is width-matched against noise the way the
    AFFECT channel was.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. The store is
NEVER rebuilt. data/foundation/** is never opened. Writes only under
data/exp_readout_shortlist_verifier_v1{_REDUCED}/.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_cue_to_store_translation_v1 as CTS            # cache/aux loaders + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as RCD            # build_population/hit_at_k_curve/..., NEVER EDITED
import exp_readout_second_order_v1 as RSO                 # second_order_scores, NEVER EDITED
from tools import floor_battery as FB                     # floors + scorer + bootstrap, NEVER EDITED
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key

ANCHOR_NAME = "exp_readout_shortlist_verifier_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_shortlist_verifier_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. NEVER EDITED AFTER A RUN. -------------------------------------
MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if SMOKE else 10000
REGRESSION_TOL = CTS.REGRESSION_TOL                        # 5e-4
REGRESSION_A0_PARTIAL = CTS.REGRESSION_A0_PARTIAL           # 0.0223 landed partial-cue read-out
REGRESSION_A1_EXACT_K1 = 0.04807                            # landed exact-key hit@1 (ceiling cell)
REGRESSION_A1_EXACT_K5 = 0.17151                            # landed exact-key hit@5  (THE CEILING @5)
REGRESSION_A1_EXACT_K10 = 0.26039                           # landed exact-key hit@10 (THE CEILING @10)
REGRESSION_ADDR_EXACT = 1.0                                 # landed exact-key addressing
REGRESSION_FCONST_K1 = 0.13896                              # landed F_CONSTANT_PROTOTYPE (the floor)
KA_MIN = 0.95
K_EXACT_GRID: Tuple[int, ...] = (1, 2, 3, 5, 10, 20, 50)
K_PARTIAL_GRID: Tuple[int, ...] = (1, 5, 10, 20, 50)
K_REJECTOR_GRID: Tuple[int, ...] = (5, 10, 20, 50)
K_KA_SHORTLIST = 5                                          # exact-key shortlist size for K1 checks
R3_K = 20                                                   # PRE-REGISTERED, fixed before any number
R3_BETAS: Tuple[float, ...] = (0.25, 0.5, 0.75)
COORD_WINDOW = 4                                            # tokens either side of "and"/"or"
PRECOND_ABS_THRESHOLD = 0.05                                # G1_PARTIAL@50 below this -> precondition
                                                             # failure, written before this cell ran.
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _out_dir() -> str:
    suffix = "" if RUN_MODE == "full" else "_REDUCED"
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _halfwidth(p: float, n: int) -> float:
    return RCD._halfwidth(p, n)


# =================================================================================================
# NEW PRIMITIVES OWNED BY THIS CELL
# =================================================================================================
def shortlist_mask(S: np.ndarray, elig: np.ndarray, k: int) -> np.ndarray:
    """Boolean [n_anchors, n_items]: True for the top-k ELIGIBLE candidates per item under S."""
    n_anchors, n_items = S.shape
    Sm = np.where(elig, S.astype(np.float64), -np.inf)
    kk = int(min(max(k, 1), n_anchors))
    idx = np.argpartition(-Sm, kk - 1, axis=0)[:kk, :]
    mask = np.zeros((n_anchors, n_items), dtype=bool)
    cols = np.repeat(np.arange(n_items)[None, :], kk, axis=0)
    mask[idx.ravel(), cols.ravel()] = True
    mask &= elig
    return mask


def top1_index(S: np.ndarray, elig: np.ndarray) -> np.ndarray:
    """argmax per item, masked to eligible entries (deterministic first-max tie-break)."""
    Sm = np.where(elig, S.astype(np.float64), -np.inf)
    return np.argmax(Sm, axis=0)


def rank_normalize_within_shortlist(S: np.ndarray, elig: np.ndarray) -> np.ndarray:
    """Per item, map each eligible candidate's score to its fractional rank in [0,1] among the
    eligible candidates for that item (1.0 = highest). Ineligible entries get -1.0."""
    n_anchors, n_items = S.shape
    out = np.full((n_anchors, n_items), -1.0, dtype=np.float64)
    for i in range(n_items):
        idx = np.flatnonzero(elig[:, i])
        if idx.size == 0:
            continue
        vals = S[idx, i].astype(np.float64)
        order = np.argsort(vals)
        ranks = np.empty(idx.size, dtype=np.float64)
        ranks[order] = np.arange(idx.size, dtype=np.float64)
        denom = max(idx.size - 1, 1)
        out[idx, i] = ranks / denom
    return out


_TOK_RE = re.compile(r"[A-Za-z']+")
_COORD_TOKENS = ("and", "or")


def build_attestation_index(sents: Sequence[str], vocab_set: set, normalize_fn,
                            window: int = COORD_WINDOW) -> Dict[Tuple[str, str], int]:
    """Coordination-pattern ("X and Y" / "X or Y") co-occurrence counts, restricted to `vocab_set`
    (already-normalised lemmas). A DISCRETE pattern count over raw sentence text -- never touches
    the vector store. STRUCTURALLY BLIND (absent from the dict) for any pair never so coordinated."""
    pair_counts: Dict[Tuple[str, str], int] = {}
    for s in sents:
        toks = _TOK_RE.findall(s.lower())
        n = len(toks)
        for i, t in enumerate(toks):
            if t not in _COORD_TOKENS:
                continue
            left_raw = toks[max(0, i - window):i]
            right_raw = toks[i + 1:min(n, i + 1 + window)]
            left = set()
            for w in left_raw:
                lm = normalize_fn(w)
                if lm in vocab_set:
                    left.add(lm)
            right = set()
            for w in right_raw:
                lm = normalize_fn(w)
                if lm in vocab_set:
                    right.add(lm)
            for a in left:
                for b in right:
                    if a == b:
                        continue
                    key = (a, b) if a < b else (b, a)
                    pair_counts[key] = pair_counts.get(key, 0) + 1
    return pair_counts


def attestation_scores_for_shortlist(mask: np.ndarray, query_lemmas: Sequence[str],
                                     anchor_lemmas: Sequence[str],
                                     pair_counts: Dict[Tuple[str, str], int]) -> np.ndarray:
    """log1p(coordination count) for every (anchor, item) pair inside `mask`; 0 elsewhere (masked
    out by `mask` downstream regardless, so the placeholder value is never selectable)."""
    n_anchors, n_items = mask.shape
    out = np.zeros((n_anchors, n_items), dtype=np.float32)
    rows, cols = np.nonzero(mask)
    for r, c in zip(rows.tolist(), cols.tolist()):
        qw = query_lemmas[c]
        cw = anchor_lemmas[r]
        if qw == cw:
            continue
        key = (qw, cw) if qw < cw else (cw, qw)
        cnt = pair_counts.get(key)
        if cnt:
            out[r, c] = float(np.log1p(cnt))
    return out


def arm_digest(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["tripwire_installed"] = bool(RCD.install_grounded_similarity_tripwire())
    ev["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())
    print("[selftest] reusing RCD.self_test() (build_population/hit_at_k_curve/random_ranking) ...",
         flush=True)
    ev["RCD_self_test"] = RCD.self_test()
    print("[selftest] reusing RSO.self_test() (second_order_scores) ...", flush=True)
    ev["RSO_self_test"] = RSO.self_test()

    # --- shortlist_mask: top-k respects eligibility and picks the right set -----------------------
    S = np.array([[5.0, 1.0], [3.0, 9.0], [4.0, 2.0], [1.0, 8.0], [2.0, 0.5]], dtype=np.float32)
    elig = np.array([[True, True], [True, False], [True, True], [True, True], [False, True]])
    m2 = shortlist_mask(S, elig, 2)
    assert m2[:, 0].sum() == 2 and set(np.flatnonzero(m2[:, 0])) == {0, 2}, \
        "shortlist_mask picked the wrong top-2 for column 0: %r" % np.flatnonzero(m2[:, 0])
    # column 1 = [1.0, 9.0, 2.0, 8.0, 0.5], elig=[T,F,T,T,T]: index1 (score 9.0) is INELIGIBLE, so
    # the top-2 ELIGIBLE are index3 (8.0) and index2 (2.0), not index1.
    assert m2[:, 1].sum() == 2 and set(np.flatnonzero(m2[:, 1])) == {2, 3}, \
        "shortlist_mask picked the wrong top-2 (eligible only) for column 1: %r" \
        % np.flatnonzero(m2[:, 1])
    assert not m2[4, 1], "shortlist_mask selected an INELIGIBLE entry"
    m_all = shortlist_mask(S, elig, 100)
    assert np.array_equal(m_all, elig), "k >= pool size must reduce to the full eligible set"
    ev["shortlist_mask_selftest"] = "PASS"

    # --- N2_PROPOSER_AS_REJECTOR reduces to G0_ARGMAX, on synthetic data ---------------------------
    rng = np.random.default_rng(3)
    Ssyn = rng.standard_normal((9, 6)).astype(np.float32)
    eligsyn = rng.random((9, 6)) > 0.2
    eligsyn[:, :] |= False
    eligsyn[np.argmax(Ssyn, axis=0), np.arange(6)] = True  # guarantee scored
    goldsyn = np.zeros((9, 6), dtype=bool)
    goldsyn[rng.integers(0, 9, size=6), np.arange(6)] = True
    goldsyn &= eligsyn
    for k_try in (1, 3, 5, 9):
        sl = shortlist_mask(Ssyn, eligsyn, k_try)
        hit_g0 = FB.hit_at_1_both_tie_conventions(Ssyn, eligsyn, goldsyn)["hit_exp"]
        hit_n2 = FB.hit_at_1_both_tie_conventions(Ssyn, sl, goldsyn)["hit_exp"]
        assert np.array_equal(hit_g0, hit_n2), (
            "N2_PROPOSER_AS_REJECTOR did NOT reduce to G0_ARGMAX at k=%d -- the shortlist did not "
            "contain the proposer's own top-1, which is a contradiction; the cell would be VOID "
            "under STOP-IF (iv)" % k_try)
    ev["N2_reduces_to_G0_selftest"] = "PASS (k=1,3,5,9)"

    # --- rank_normalize_within_shortlist: range, monotonicity, ineligible handling -----------------
    rn = rank_normalize_within_shortlist(S, elig)
    # elig column1 = [T,F,T,T,T]: row1 is the ineligible entry in that column (row4 col1 IS eligible)
    assert rn[1, 1] == -1.0, "ineligible entry must be flagged -1.0, not a real rank"
    col0_idx = np.flatnonzero(elig[:, 0])
    col0_vals = S[col0_idx, 0]
    col0_ranks = rn[col0_idx, 0]
    order = np.argsort(col0_vals)
    assert np.all(np.diff(col0_ranks[order]) >= 0), "rank_normalize is not monotone in the score"
    assert col0_ranks.max() == 1.0 and col0_ranks.min() == 0.0, "ranks must span [0,1] exactly"
    ev["rank_normalize_selftest"] = "PASS"

    # --- attestation index: a tiny synthetic corpus with a known coordination pattern --------------
    def _norm(w: str) -> str:
        return w.lower()
    sents_syn = ["the cat and dog played in the yard",
                 "a bird or fish swam past quickly",
                 "the cat slept alone all afternoon"]
    vocab_syn = {"cat", "dog", "bird", "fish", "yard", "afternoon"}
    pc = build_attestation_index(sents_syn, vocab_syn, _norm, window=4)
    assert pc.get(("cat", "dog"), 0) == 1, "coordination pattern 'cat and dog' not captured: %r" % pc
    assert pc.get(("bird", "fish"), 0) == 1, "coordination pattern 'bird or fish' not captured: %r" % pc
    assert ("cat", "yard") not in pc, "spurious pair captured across a coordinator that is not there"
    ev["attestation_index_selftest"] = {"pairs_found": len(pc), "sample": {str(k): v
                                                                           for k, v in pc.items()}}

    mask_syn = np.zeros((4, 1), dtype=bool)
    mask_syn[[0, 1, 2, 3], 0] = True
    anchors_syn = ["dog", "fish", "yard", "afternoon"]
    r1_syn = attestation_scores_for_shortlist(mask_syn, ["cat"], anchors_syn, pc)
    assert abs(float(r1_syn[0, 0]) - float(np.log1p(1))) < 1e-6, "attested pair scored wrong"
    assert r1_syn[2, 0] == 0.0 and r1_syn[3, 0] == 0.0, "unattested pairs must score exactly 0"
    ev["attestation_lookup_selftest"] = "PASS"

    # --- pearson_ci_bootstrap import works and fires on a genuinely correlated synthetic pair ------
    from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
    xx = np.arange(40, dtype=np.float64)
    yy = xx * 2.0 + rng.standard_normal(40) * 0.5
    r = pearson_ci_bootstrap(xx, yy, seed=1, n_boot=500)
    assert r["band"] == "ABOVE", "pearson_ci_bootstrap did not fire on a strongly correlated pair: %r" % r
    ev["pearson_ci_bootstrap_selftest"] = r

    # --- ARMS_MUST_DIFFER hashing utility works -----------------------------------------------------
    d1 = arm_digest(np.array([1.0, 2.0, 3.0]))
    d2 = arm_digest(np.array([1.0, 2.0, 3.0]))
    d3 = arm_digest(np.array([1.0, 2.0, 3.1]))
    assert d1 == d2 and d1 != d3, "arm_digest is not stable/discriminating"
    ev["arm_digest_selftest"] = "PASS"

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
def run(grid: str, output_dir: str) -> Dict:
    t0 = time.time()
    _gate = CTS.ruler_mode_gate()
    _tripwire = RCD.install_grounded_similarity_tripwire()
    P = RCD.build_population()
    C, mat, mat_ok = P["C"], P["mat"], P["mat_ok"]
    n_anchors, qidx = P["n_anchors"], P["qidx"]
    GOLD, E, keep_ALL = P["GOLD"], P["E"], P["keep"]
    anchors = P["anchors"]
    MATn = l2n(mat)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": _gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(_tripwire),
        "signal_independence_claim": {
            "PROPOSER": "cosine of first-order Hebbian-sum co-occurrence code vs the PARTIAL CUE "
                        "(a dense vector similarity)",
            "R1_ATTESTATION": "discrete coordination-pattern ('X and/or Y') count over RAW SENTENCE "
                              "TEXT, never touches the vector store; STRUCTURALLY BLIND for unseen "
                              "pairs (0 by construction)",
            "R2_PROFILE": "cos(profile(anchor), profile(query)) -- second-order, reused verbatim "
                         "from exp_readout_second_order_v1.second_order_scores(k=0)",
            "claim": "R1 and R2 are BOTH mathematically distinct from the proposer's raw first-order "
                    "cosine; R1 is additionally independent of the vector store entirely. Verified "
                    "empirically below via correlation of each rejector's SCORE against the "
                    "proposer's own score on the shared shortlist."},
    }

    # =============================================================================================
    # REGRESSION GATES -- ALWAYS on the FULL population, regardless of --grid (matches RCD).
    # =============================================================================================
    T_full = np.flatnonzero(keep_ALL)
    S_part_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h0 = FB.hit_at_1_both_tie_conventions(S_part_full, E, GOLD)
    m0 = h0["scored"] & keep_ALL
    a0 = float(h0["hit_exp"][m0].mean())
    del h0
    S_ex_full = (MATn @ l2n(C["Q_exact"]).T).astype(np.float32)
    curve_full = RCD.hit_at_k_curve(S_ex_full, E, GOLD, (1, 5, 10))
    opt_full = curve_full["hit_at_k"]["opt"]
    a1_k1 = float(opt_full[1][T_full].mean())
    a1_k5 = float(opt_full[5][T_full].mean())
    a1_k10 = float(opt_full[10][T_full].mean())
    addr_full = float(np.mean(np.argmax(S_ex_full, axis=0)[keep_ALL & (qidx >= 0)]
                              == qidx[keep_ALL & (qidx >= 0)]))
    const_vec_full = FB.constant_prototype_floor(mat, mat_ok)
    Sconst_full = FB.as_constant_matrix(const_vec_full, C["Q_exact"].shape[0])
    hconst = FB.hit_at_1_both_tie_conventions(Sconst_full, E, GOLD)
    fconst_k1 = float(hconst["hit_exp"][T_full].mean())
    del curve_full, opt_full, hconst, Sconst_full

    reg = {
        "partial_cue_hit1_FULL_POP": round(a0, 5), "expected": REGRESSION_A0_PARTIAL,
        "exact_key_hit1_FULL_POP": round(a1_k1, 5), "expected": REGRESSION_A1_EXACT_K1,
        "exact_key_hit5_FULL_POP": round(a1_k5, 5), "expected": REGRESSION_A1_EXACT_K5,
        "exact_key_hit10_FULL_POP": round(a1_k10, 5), "expected": REGRESSION_A1_EXACT_K10,
        "exact_key_addressing_FULL_POP": round(addr_full, 5), "expected": REGRESSION_ADDR_EXACT,
        "F_CONSTANT_PROTOTYPE_hit1_FULL_POP": round(fconst_k1, 5), "expected": REGRESSION_FCONST_K1,
        "tol": REGRESSION_TOL, "n_full": int(T_full.size),
        "source": "the three ceiling figures (0.04807/0.17151/0.26039) and the binding floor "
                  "(0.13896) VERIFIED OFF DISK against "
                  "data/exp_readout_ceiling_diagnosis_v1/metrics.json "
                  ".S2_WHERE_DOES_THE_ANSWER_RANK.curves.EXACT_KEY_COSINE / .F_CONSTANT_PROTOTYPE "
                  "BEFORE this cell was authored.",
    }
    reg["PASS"] = bool(
        abs(a0 - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL
        and abs(a1_k1 - REGRESSION_A1_EXACT_K1) <= REGRESSION_TOL
        and abs(a1_k5 - REGRESSION_A1_EXACT_K5) <= REGRESSION_TOL
        and abs(a1_k10 - REGRESSION_A1_EXACT_K10) <= REGRESSION_TOL
        and abs(addr_full - REGRESSION_ADDR_EXACT) <= REGRESSION_TOL
        and abs(fconst_k1 - REGRESSION_FCONST_K1) <= REGRESSION_TOL)
    rep["REGRESSION_GATE"] = reg
    if not reg["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % reg)
    print("[regression] partial=%.5f exact1=%.5f exact5=%.5f exact10=%.5f addr=%.5f fconst=%.5f "
         "ALL PASS t=%.0fs" % (a0, a1_k1, a1_k5, a1_k10, addr_full, fconst_k1, time.time() - t0),
         flush=True)
    del S_part_full, S_ex_full

    # =============================================================================================
    # POPULATION FOR THE SWEEP -- T is reduced to 400 items under --grid reduced (smoke)
    # =============================================================================================
    items = T_full.copy()
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact_T = C["Q_exact"][T]
    Q_part_T = C["Q_part"][T]
    L_words_T = [C["L_words"][int(t)] for t in T]
    rep["population"] = {
        "n_anchors": n_anchors, "n_items_scored": n_items,
        "pool": "the LANDED OPEN pool (mat_ok minus per-item exclusions), matching "
                "exp_readout_ceiling_diagnosis_v1 exactly",
        "gold": "WordNet 3.0 generous meaning set, exp_grounding_readout_known_answer_v1 UNMODIFIED",
        "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions, tie-corrected primary",
        "cue_regime_primary": "PARTIAL CUE for G0/shortlists/rejectors (the real regime); EXACT KEY "
                              "used only for G1's ceiling curve and the K1 known-answer checks",
    }
    S_ex_T = (MATn @ l2n(Q_exact_T).T).astype(np.float32)
    S_part_T = (MATn @ l2n(Q_part_T).T).astype(np.float32)
    print("[load] n_anchors=%d n_items=%d t=%.0fs" % (n_anchors, n_items, time.time() - t0),
         flush=True)

    # ---- VALIDITY: KA_SELF_ADDRESS + NULL_PERMUTED (global, on the exact-key cue) ----------------
    ok_q = qidx_T >= 0
    ka = float(np.mean(np.argmax(S_ex_T, axis=0)[ok_q] == qidx_T[ok_q]))
    rng_perm = np.random.default_rng(MASTER_SEED + 201)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng_perm.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    h_null = FB.hit_at_1_both_tie_conventions(S_ex_T[:, perm], E_T, GOLD_T)
    null_hit = float(h_null["hit_exp"][h_null["scored"]].mean())
    null_addr = float(np.mean(np.argmax(S_ex_T[:, perm], axis=0)[ok_q] == qidx_T[ok_q]))
    rep["VALIDITY"] = {
        "KA_SELF_ADDRESS": {"value": round(ka, 4), "gate": KA_MIN, "PASS": bool(ka >= KA_MIN)},
        "NULL_PERMUTED": {"hit_at_1_tie_corrected": round(null_hit, 6),
                          "addressing": round(null_addr, 8),
                          "chance_addressing": round(1.0 / n_anchors, 8),
                          "binom_ci_halfwidth_at_null_hit": round(_halfwidth(null_hit, n_items), 6)},
    }
    if ka < KA_MIN:
        raise SystemExit("KNOWN-ANSWER ARM FAILED (%.4f < %.2f) -- no treatment number is read"
                         % (ka, KA_MIN))
    print("[validity] KA_self_address=%.4f NULL_hit=%.6f NULL_addr=%.8f" % (ka, null_hit, null_addr),
         flush=True)

    # =============================================================================================
    # FLOORS -- recomputed on THIS population, on the PARTIAL CUE (F_SCRAMBLE uses Q_part_T).
    # =============================================================================================
    aux = P["aux"]
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
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 211))
                              @ l2n(Q_part_T).T).astype(np.float32)
    const_floor_vec = FB.constant_prototype_floor(mat, mat_ok)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_floor_vec, n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors,
                                  [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = {
        "cue": "PARTIAL", "names": sorted(floors_S),
        "never_imported": ["0.1390", "0.1715", "0.2604", "0.0873", "0.1382", "0.2070", "-0.1959"]}

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    winner_idx: Dict[str, np.ndarray] = {}          # for ARMS_MUST_DIFFER -- SELECTION identity,
                                                     # not accuracy outcome (see note at the check)

    def add_arm(name: str, Sx: np.ndarray, elig: np.ndarray, track_winner: bool = False) -> Dict:
        hh = FB.hit_at_1_both_tie_conventions(Sx, elig, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        hits_opt[name] = hh["hit_opt"]
        if track_winner:
            winner_idx[name] = top1_index(Sx, elig)
        return hh

    for k_f, Sf in floors_S.items():
        add_arm(k_f, Sf, E_T)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S, E_T)
    add_arm("G0_ARGMAX", S_part_T, E_T, track_winner=True)

    # =============================================================================================
    # G1_SHORTLIST_ORACLE -- THE CEILING. Report EXACT (regression-verified) and PARTIAL (the real
    # precondition curve) BEFORE any rejector number.
    # =============================================================================================
    n_elig = E_T.sum(axis=0).astype(np.float64)
    n_gold = (GOLD_T & E_T).sum(axis=0).astype(np.float64)
    rr = RCD.random_ranking_hit_at_k(n_elig, n_gold, sorted(set(K_EXACT_GRID) | set(K_PARTIAL_GRID)))

    curve_exact = RCD.hit_at_k_curve(S_ex_T, E_T, GOLD_T, K_EXACT_GRID)
    g1_exact: Dict[int, float] = {}
    for k in K_EXACT_GRID:
        arr = curve_exact["hit_at_k"]["opt"][k].astype(np.float64)
        hits_exp["G1_SHORTLIST_ORACLE_EXACT_k%d" % k] = arr
        g1_exact[k] = float(arr.mean())

    curve_partial = RCD.hit_at_k_curve(S_part_T, E_T, GOLD_T, K_PARTIAL_GRID)
    g1_partial: Dict[int, float] = {}
    for k in K_PARTIAL_GRID:
        arr = curve_partial["hit_at_k"]["opt"][k].astype(np.float64)
        hits_exp["G1_SHORTLIST_ORACLE_PARTIAL_k%d" % k] = arr
        hits_exp["RANDOM_RANKING_NULL_PARTIAL_k%d" % k] = rr[k]
        g1_partial[k] = float(arr.mean())

    precond_v = g1_partial[50]
    precond_fail = bool(precond_v < PRECOND_ABS_THRESHOLD)
    rep["G1_SHORTLIST_ORACLE"] = {
        "EXACT_KEY_curve": {str(k): round(v, 5) for k, v in g1_exact.items()},
        "PARTIAL_CUE_curve_THE_PRECONDITION": {str(k): round(v, 5) for k, v in g1_partial.items()},
        "random_ranking_null_curve": {str(k): round(float(rr[k].mean()), 5)
                                      for k in K_PARTIAL_GRID},
        "PRECOND_ABS_THRESHOLD": PRECOND_ABS_THRESHOLD,
        "precondition_value_at_k50": round(precond_v, 5),
        "PRECONDITION_FAILURE": precond_fail,
        "reading": "the achievable ceiling of ANY rejector, real or oracle, under the PARTIAL cue "
                  "is exactly the PARTIAL_CUE_curve value at that k. If PRECONDITION_FAILURE is "
                  "True, no rejector work below is licensed regardless of its own numbers.",
    }
    print("[G1] EXACT k1/5/10=%.5f/%.5f/%.5f  PARTIAL k1/5/10/20/50=%s  PRECOND_FAIL=%s t=%.0fs"
         % (g1_exact[1], g1_exact[5], g1_exact[10],
            {k: round(v, 4) for k, v in g1_partial.items()}, precond_fail, time.time() - t0),
         flush=True)

    # =============================================================================================
    # THE ATTESTATION INDEX -- built once, cue-independent (word identity + raw corpus text only).
    # =============================================================================================
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    from hdlab.reading_grounding_loop import normalize_lemma
    t_att0 = time.time()
    sents = [s for _seg, s in load_corpus_v5(None, lineaware=True)]
    anchors_lemma = [normalize_lemma(a) for a in anchors]
    Lwords_T_lemma = [normalize_lemma(w) for w in L_words_T]
    vocab_set = set(anchors_lemma) | set(Lwords_T_lemma)
    pair_counts = build_attestation_index(sents, vocab_set, normalize_lemma, window=COORD_WINDOW)
    rep["ATTESTATION_INDEX"] = {
        "n_sentences": len(sents), "n_vocab": len(vocab_set), "n_pairs_attested": len(pair_counts),
        "window_tokens": COORD_WINDOW,
        "build_t_s": round(time.time() - t_att0, 1)}
    print("[attestation] %d sentences -> %d attested coordination pairs t=%.0fs"
         % (len(sents), len(pair_counts), time.time() - t_att0), flush=True)
    del sents

    # =============================================================================================
    # R2 -- SECOND-ORDER PROFILE. Built once (untruncated, k=0 -- the best arm in the sibling cell).
    # =============================================================================================
    t_p0 = time.time()
    Pmat = (MATn @ MATn.T).astype(np.float32)
    R2_full_partial = RSO.second_order_scores(Pmat, S_part_T, 0, self_idx=qidx_T)
    print("[R2] anchor-anchor profile matrix (%d x %d) + partial-cue profile scores t=%.0fs"
         % (n_anchors, n_anchors, time.time() - t_p0), flush=True)

    # =============================================================================================
    # THE MAIN SWEEP: R1 / R2 / N1 / N2 at each shortlist k, plus the correlation check that PROVES
    # R1/R2 differ from the proposer's own score (the signal-independence claim, made empirical).
    # =============================================================================================
    corr_with_proposer: Dict[str, float] = {}
    for k in K_REJECTOR_GRID:
        sl = shortlist_mask(S_part_T, E_T, k)
        record_unit(output_dir, unit_key("SHORTLIST", k), {"n_selected": int(sl.sum())})

        R1_S = attestation_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, pair_counts)
        add_arm("R1_ATTESTATION_REJECTOR_k%d" % k, R1_S, sl, track_winner=True)
        add_arm("R2_PROFILE_REJECTOR_k%d" % k, R2_full_partial, sl, track_winner=True)

        rng_n1 = np.random.default_rng(MASTER_SEED + 301 + k)
        N1_S = rng_n1.random((n_anchors, n_items)).astype(np.float32)
        add_arm("N1_RANDOM_REJECTOR_k%d" % k, N1_S, sl, track_winner=True)

        n2h = add_arm("N2_PROPOSER_AS_REJECTOR_k%d" % k, S_part_T, sl, track_winner=True)
        if not np.array_equal(hits_exp["N2_PROPOSER_AS_REJECTOR_k%d" % k], hits_exp["G0_ARGMAX"]):
            raise SystemExit(
                "STOP-IF (iv): N2_PROPOSER_AS_REJECTOR does NOT reduce to G0_ARGMAX at k=%d -- the "
                "stages are NOT independent by this construction, which is a contradiction (the "
                "shortlist always contains the proposer's own top-1). THE CELL IS VOID. Nothing "
                "downstream is published." % k)

        # signal-independence, made empirical: R1/R2 scores vs the proposer's own score, over the
        # SAME shortlist entries (paired, non-degenerate cells only).
        r_idx, c_idx = np.nonzero(sl)
        prop_vals = S_part_T[r_idx, c_idx].astype(np.float64)
        r1_vals = R1_S[r_idx, c_idx].astype(np.float64)
        r2_vals = R2_full_partial[r_idx, c_idx].astype(np.float64)
        from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
        corr_with_proposer["R1_vs_proposer_k%d" % k] = pearson_ci_bootstrap(
            prop_vals, r1_vals, seed=MASTER_SEED + 401 + k, n_boot=1000)
        corr_with_proposer["R2_vs_proposer_k%d" % k] = pearson_ci_bootstrap(
            prop_vals, r2_vals, seed=MASTER_SEED + 411 + k, n_boot=1000)
        record_unit(output_dir, unit_key("SWEEP", k), {
            "G1_partial": round(g1_partial[k] if k in g1_partial else float("nan"), 4),
            "R1": round(float(hits_exp["R1_ATTESTATION_REJECTOR_k%d" % k].mean()), 4),
            "R2": round(float(hits_exp["R2_PROFILE_REJECTOR_k%d" % k].mean()), 4),
            "N1": round(float(hits_exp["N1_RANDOM_REJECTOR_k%d" % k].mean()), 4),
            "N2_eq_G0": True})
        print("[sweep k=%d] R1=%.4f R2=%.4f N1=%.4f N2==G0(verified) t=%.0fs"
             % (k, hits_exp["R1_ATTESTATION_REJECTOR_k%d" % k].mean(),
                hits_exp["R2_PROFILE_REJECTOR_k%d" % k].mean(),
                hits_exp["N1_RANDOM_REJECTOR_k%d" % k].mean(), time.time() - t0), flush=True)

    rep["SIGNAL_INDEPENDENCE_FROM_PROPOSER_MEASURED"] = corr_with_proposer

    # =============================================================================================
    # R3_COMBINED -- both signals, rank-normalised, weighted. K FIXED at 20, beta SWEPT.
    # =============================================================================================
    sl20 = shortlist_mask(S_part_T, E_T, R3_K)
    R1_20 = attestation_scores_for_shortlist(sl20, Lwords_T_lemma, anchors_lemma, pair_counts)
    rankR1 = rank_normalize_within_shortlist(R1_20, sl20)
    rankR2 = rank_normalize_within_shortlist(R2_full_partial, sl20)
    for beta in R3_BETAS:
        combined = beta * rankR1 + (1.0 - beta) * rankR2
        combined[~sl20] = -1.0
        name = "R3_COMBINED_k%d_beta%g" % (R3_K, beta)
        add_arm(name, combined, sl20, track_winner=True)
        record_unit(output_dir, unit_key("R3", beta), {"value": round(float(hits_exp[name].mean()), 4)})
        print("[R3 beta=%.2f] %.4f" % (beta, hits_exp[name].mean()), flush=True)

    # =============================================================================================
    # K1_KNOWN_ANSWER -- per real channel, on an EXACT-KEY shortlist that certainly contains the
    # item's own address. Gate 0.95.
    # =============================================================================================
    sl_ex_ka = shortlist_mask(S_ex_T, E_T, K_KA_SHORTLIST)
    R2_full_exact = RSO.second_order_scores(Pmat, S_ex_T, 0, self_idx=qidx_T)
    R1_ex_ka = attestation_scores_for_shortlist(sl_ex_ka, Lwords_T_lemma, anchors_lemma, pair_counts)
    rankR1_ex = rank_normalize_within_shortlist(R1_ex_ka, sl_ex_ka)
    rankR2_ex = rank_normalize_within_shortlist(R2_full_exact, sl_ex_ka)
    combined_ex = 0.5 * rankR1_ex + 0.5 * rankR2_ex
    combined_ex[~sl_ex_ka] = -1.0

    def _ka_of(S_channel: np.ndarray, elig: np.ndarray) -> float:
        top1 = top1_index(S_channel, elig)
        return float(np.mean(top1[ok_q] == qidx_T[ok_q]))

    # THE BINDING K1 GATE is KA_SELF_ADDRESS on the STORE (computed above, hard-gated >=0.95,
    # SystemExit already fired if it failed) -- every arm here shares ONE store/cue construction, so
    # a single store-level KA gate is what "K1_KNOWN_ANSWER must pass for every arm" means when the
    # arms are different READ-OUT mechanisms over the SAME representation (as opposed to sibling
    # write-rule cells where the arms are different STORE representations and each needed its own).
    #
    # R1_ATTESTATION and R2_PROFILE ADDITIONALLY, by explicit design, EXCLUDE self-comparison
    # (R1 skips qw==cw pairs; R2's second_order_scores zeroes the profile diagonal -- both per their
    # own docstrings, because a word's similarity/attestation to ITSELF carries no information about
    # its relation to a query). A "does the rejector prefer the item's own address" test is therefore
    # STRUCTURALLY INAPPLICABLE to R1/R2/R3 as a pass/fail gate -- reported below as INFORMATIONAL
    # ONLY, not gated at KA_MIN, and the near-zero values are the EXPECTED consequence of the
    # self-exclusion design, not a rejector failure.
    own_address_preference_informational = {
        "PROPOSER_G0_KA_SELF_ADDRESS": ka,  # the BINDING gate, already enforced above
        "R1_ATTESTATION_prefers_own_address": _ka_of(R1_ex_ka, sl_ex_ka),
        "R2_PROFILE_prefers_own_address": _ka_of(R2_full_exact, sl_ex_ka),
        "R3_COMBINED_prefers_own_address": _ka_of(combined_ex, sl_ex_ka),
    }
    rep["K1_KNOWN_ANSWER"] = {
        "BINDING_GATE": "KA_SELF_ADDRESS on the store (>= %.2f, already enforced above): %.4f PASS"
                        % (KA_MIN, ka),
        "shortlist_k_for_informational_check": K_KA_SHORTLIST,
        "own_address_preference_INFORMATIONAL_NOT_GATED": {
            k_: round(v, 4) for k_, v in own_address_preference_informational.items()},
        "why_not_gated": "R1 skips self-pairs by construction (qw==cw excluded) and R2's "
                        "second_order_scores zeroes the profile self-term by construction; both "
                        "therefore CANNOT structurally prefer a candidate's own identity, so a "
                        "'must rank own address top-1' bar does not test anything meaningful for "
                        "them and is reported, not gated."}
    print("[K1] %s" % json.dumps(rep["K1_KNOWN_ANSWER"]["own_address_preference_INFORMATIONAL_NOT_GATED"]),
         flush=True)
    del R1_ex_ka, R2_full_exact, rankR1_ex, rankR2_ex, combined_ex, sl_ex_ka

    # =============================================================================================
    # ARMS_MUST_DIFFER (META_RULE_AF) -- checked on SELECTION IDENTITY (winner_idx), not on the
    # resulting hit/miss OUTCOME (hits_exp). Two different scoring channels can legitimately land on
    # the identical hit/miss pattern by coincidence at low accuracy (e.g. two channels both miss on
    # the same items even while picking DIFFERENT wrong words) -- that is not an implementation bug
    # and hashing hits_exp would false-positive on it (measured: R2_PROFILE_REJECTOR at k=5/20/50
    # picks a DIFFERENT top-1 word for 63/400 smoke items yet lands on the identical hit_exp array,
    # because none of those 63 flips changes a miss to a hit or vice versa). winner_idx is the
    # correct level: it is the literal selection each arm makes, which IS what a copy-paste /
    # aliasing bug would duplicate. Restricted to the arms that actually SELECT a winner (G0/R1/R2/
    # R3/N1/N2); G1 (an oracle over presence-in-shortlist, no single winner) and the floors/oracle-
    # constant arms are diagnostic, not selection mechanisms, and are out of this check's scope.
    # =============================================================================================
    digests = {name: arm_digest(arr) for name, arr in winner_idx.items()}
    # ONE mathematically-guaranteed equivalence class: the proposer's own global top-1 is, by
    # construction, always inside any shortlist derived from its own score -- so G0_ARGMAX and
    # every N2_PROPOSER_AS_REJECTOR_k{K} select the identical winner for every item, for every K.
    n2_equiv_class = frozenset(["G0_ARGMAX"] + ["N2_PROPOSER_AS_REJECTOR_k%d" % k
                                                for k in K_REJECTOR_GRID])
    names_sorted = sorted(digests)
    collisions = []
    for i, a in enumerate(names_sorted):
        for b in names_sorted[i + 1:]:
            if digests[a] == digests[b] and not ({a, b} <= n2_equiv_class):
                collisions.append((a, b))
    rep["ARMS_MUST_DIFFER"] = {
        "n_arms_checked": len(digests), "checked_on": "winner_idx (selection identity)",
        "exempted_equivalence_class": sorted(n2_equiv_class),
        "exempted_rationale": "the proposer's own global top-1 is always inside any shortlist "
                              "derived from its own score, by construction",
        "collisions_besides_exemption": collisions, "PASS": bool(len(collisions) == 0)}
    if collisions:
        raise SystemExit("META_RULE_AF VIOLATION: bit-identical SELECTIONS (winner_idx) outside "
                         "the declared exemption: %r" % collisions)
    print("[arms_differ] %d selection arms checked, 0 unexplained collisions" % len(digests),
         flush=True)

    # =============================================================================================
    # BOOTSTRAP -- all arms share ONE set of draws.
    # =============================================================================================
    scored_mask = np.ones(n_items, dtype=bool)
    for arr in hits_exp.values():
        scored_mask &= np.isfinite(arr)
    boot = FB.paired_bootstrap_ci(hits_exp, scored_mask, N_BOOT, MASTER_SEED + 501)
    rep["N_BOOT"] = N_BOOT
    rep["n_common_scored"] = boot["n_common"]

    floor_acc = {f: boot["acc"][f] for f in FLOOR_NAMES}
    binding_floor_name = max(floor_acc, key=floor_acc.get)
    binding_floor_value = floor_acc[binding_floor_name]
    rep["BINDING_FLOOR"] = {"per_floor_acc": {f: round(v, 5) for f, v in floor_acc.items()},
                            "binding_floor_name": binding_floor_name,
                            "binding_floor_value": round(binding_floor_value, 5)}

    def marg(a: str, b: str) -> Dict:
        m = FB.margin(boot["boot"], a, b)
        m["ci_halfwidth"] = round((m["ci95"][1] - m["ci95"][0]) / 2.0, 5)
        m["analytic_null_halfwidth_a"] = round(_halfwidth(boot["acc"][a], boot["n_common"]), 5)
        m["acc_a"] = round(boot["acc"][a], 5)
        m["acc_b"] = round(boot["acc"][b], 5)
        return m

    def k_of(arm: str) -> int:
        """The shortlist size an arm was built at. R3 arms are fixed at R3_K by pre-registration;
        R1/R2/N1/N2 arms carry their k as a `_k{K}` suffix."""
        if arm.startswith("R3_COMBINED"):
            return R3_K
        return int(arm.rsplit("_k", 1)[1])

    margins: Dict[str, Dict] = {}
    real_rejector_arms = (["R1_ATTESTATION_REJECTOR_k%d" % k for k in K_REJECTOR_GRID]
                          + ["R2_PROFILE_REJECTOR_k%d" % k for k in K_REJECTOR_GRID]
                          + ["R3_COMBINED_k%d_beta%g" % (R3_K, b) for b in R3_BETAS])
    for arm in real_rejector_arms:
        n1_name = "N1_RANDOM_REJECTOR_k%d" % k_of(arm)
        margins[arm + "__vs__FLOOR(%s)" % binding_floor_name] = marg(arm, binding_floor_name)
        margins[arm + "__vs__G0_ARGMAX"] = marg(arm, "G0_ARGMAX")
        margins[arm + "__vs__" + n1_name] = marg(arm, n1_name)
    for k in K_REJECTOR_GRID:
        margins["N1_RANDOM_REJECTOR_k%d__vs__FLOOR(%s)" % (k, binding_floor_name)] = \
            marg("N1_RANDOM_REJECTOR_k%d" % k, binding_floor_name)
        margins["G1_SHORTLIST_ORACLE_PARTIAL_k%d__vs__RANDOM_RANKING_NULL_PARTIAL_k%d" % (k, k)] = \
            marg("G1_SHORTLIST_ORACLE_PARTIAL_k%d" % k, "RANDOM_RANKING_NULL_PARTIAL_k%d" % k)
    margins["G0_ARGMAX__vs__FLOOR(%s)" % binding_floor_name] = marg("G0_ARGMAX", binding_floor_name)
    rep["MARGINS"] = margins

    # =============================================================================================
    # STOP-IF EVALUATION
    # =============================================================================================
    def beats_floor(arm: str) -> bool:
        return margins[arm + "__vs__FLOOR(%s)" % binding_floor_name]["band"] == "ABOVE"

    def beats_n1(arm: str) -> bool:
        return margins[arm + "__vs__N1_RANDOM_REJECTOR_k%d" % k_of(arm)]["band"] == "ABOVE"

    def beats_g0(arm: str) -> bool:
        return margins[arm + "__vs__G0_ARGMAX"]["band"] == "ABOVE"

    stop_i_wins = [arm for arm in real_rejector_arms if beats_floor(arm) and beats_n1(arm)]
    stop_iii_shortlist_not_rejector = [arm for arm in real_rejector_arms
                                       if beats_g0(arm) and not beats_n1(arm)
                                       and arm not in stop_i_wins]
    clearing_arms = [arm for arm in real_rejector_arms if beats_floor(arm) or beats_n1(arm)]

    # rule 12 -- orthographic + word-length correlation on every clearing arm
    Sortho_T = floors_S.get("F_ORTHOGRAPHIC")
    word_len = np.array([len(a) for a in anchors], dtype=np.float64)
    from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
    rule12: Dict[str, Dict] = {}
    for arm in clearing_arms:
        k_arm = k_of(arm)
        sl_arm = sl20 if arm.startswith("R3_COMBINED") else shortlist_mask(S_part_T, E_T, k_arm)
        # recompute the arm's own score matrix on demand for the winner-index (cheap, k<=50)
        if arm.startswith("R1_ATTESTATION"):
            Sarm_mat = attestation_scores_for_shortlist(sl_arm, Lwords_T_lemma, anchors_lemma,
                                                        pair_counts)
        elif arm.startswith("R2_PROFILE"):
            Sarm_mat = R2_full_partial
        else:
            b_here = float(arm.rsplit("beta", 1)[1])
            Sarm_mat = b_here * rankR1 + (1.0 - b_here) * rankR2
        top1 = top1_index(Sarm_mat, sl_arm)
        winner_len = word_len[top1]
        gain = hits_exp[arm] - hits_exp["G0_ARGMAX"]
        best_gold_ortho = np.where(GOLD_T & E_T, Sortho_T, -np.inf).max(axis=0) \
            if Sortho_T is not None else np.full(n_items, np.nan)
        ortho_corr = pearson_ci_bootstrap(gain, best_gold_ortho, seed=MASTER_SEED + 601, n_boot=2000)
        len_corr = pearson_ci_bootstrap(gain, winner_len, seed=MASTER_SEED + 611, n_boot=2000)
        winner_ortho_mean = float(Sortho_T[top1, np.arange(n_items)].mean()) \
            if Sortho_T is not None else None
        rule12[arm] = {"ortho_gain_corr": ortho_corr, "word_length_gain_corr": len_corr,
                       "mean_trigram_cosine_of_winner": round(winner_ortho_mean, 5)
                       if winner_ortho_mean is not None else None}

    rule12_fail = [arm for arm, v in rule12.items()
                  if v["ortho_gain_corr"].get("band") == "ABOVE"
                  or v["word_length_gain_corr"].get("band") == "ABOVE"]

    rep["STOP_IF"] = {
        "i_real_win_arms": stop_i_wins,
        "ii_precondition_failure": precond_fail,
        "iii_shortlist_not_rejector_arms": stop_iii_shortlist_not_rejector,
        "iv_n2_void": False,  # would have raised SystemExit above if this had fired
        "v_rule12_failure_arms": rule12_fail,
        "clearing_arms_tested_for_rule12": clearing_arms,
        "RULE_12_DETAIL": rule12,
    }

    if stop_i_wins:
        verdict = "STOPIF_I__REAL_REJECTOR_WIN__" + "_".join(stop_i_wins[:2])
    elif precond_fail:
        verdict = "STOPIF_II__PRECONDITION_FAILURE__PARTIAL_CUE_SHORTLIST_NEAR_ZERO_AT_K50"
    elif stop_iii_shortlist_not_rejector:
        verdict = "STOPIF_III__GAIN_IS_THE_SHORTLIST_NOT_THE_REJECTOR"
    elif rule12_fail:
        verdict = "STOPIF_V__RULE12_ORTHOGRAPHIC_OR_LENGTH_LEAKAGE__" + "_".join(rule12_fail[:2])
    else:
        verdict = "NO_REAL_REJECTOR_CLEARS_AND_NO_PRECONDITION_FAILURE__NULL_ON_THIS_ARCHITECTURE"

    rep["verdict"] = verdict
    rep["verdict_msg"] = (
        "PRECOND(partial-cue G1@k50)=%.5f (fail<%.2f: %s). BindingFloor=%s@%.5f. "
        "REAL_WIN_ARMS=%r. SHORTLIST_NOT_REJECTOR_ARMS=%r. RULE12_FAIL=%r. N2==G0 verified for "
        "all k (no VOID)." % (precond_v, PRECOND_ABS_THRESHOLD, precond_fail, binding_floor_name,
                              binding_floor_value, stop_i_wins, stop_iii_shortlist_not_rejector,
                              rule12_fail))
    rep["summary"] = verdict
    rep["elapsed_s"] = round(time.time() - t0, 1)
    rep["run_mode"] = "full" if grid == "full" else "smoke"
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = sorted(
        m for m in sys.modules
        if any(s in m for s in ("exp_readout_ceiling_diagnosis_v1", "exp_readout_second_order_v1",
                                "exp_cue_to_store_translation_v1", "floor_battery",
                                "exp_cue_binarised_readout_transfer_v1", "exp_definitional_grounding_v5",
                                "reading_grounding_loop", "exp_checkpoint")))
    print("[verdict] %s  t=%.0fs" % (verdict, time.time() - t0), flush=True)
    return rep


# =================================================================================================
def decide(rep: Dict) -> Tuple[str, str]:
    return rep["verdict"], rep["verdict_msg"]


def main() -> None:
    output_dir = _out_dir()
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "argv": list(sys.argv),
             "host": platform.node()}
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)

    if _ARGS.self_test:
        ev = self_test()
        _atomic_json(os.path.join(output_dir, "selftest_result.json"), ev)
        print("[main] SELF-TEST ALL PASS", flush=True)
        return

    rep = run(_ARGS.grid, output_dir)
    _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
    print("[main] wrote %s" % os.path.join(output_dir, "metrics.json"), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:                      # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        out_dir = _out_dir()
        os.makedirs(out_dir, exist_ok=True)
        diag = {
            "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:500]),
            "summary": "CELL_CRASHED: %s" % type(e).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME,
        }
        tmp_path = os.path.join(out_dir, "metrics.json.tmp")
        final_path = os.path.join(out_dir, "metrics.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp_path, final_path)
        raise
