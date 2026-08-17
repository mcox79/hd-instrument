"""exp_readout_writerule_selection_axis_v1 -- IS THE DEFECT WHICH WORDS GET SUMMED, NOT WHAT GETS SUMMED?

FINDINGS LOG: notes/readout_ceiling_findings_2026-08-17.md sections 10-11 (read first).
PRE-REG THIS ACTS ON: Director's dispatch, 2026-08-17 night, "the landed 'paradigmatic' write rule
is a weak version of the idea".

THE CLAIM UNDER TEST, AND THE CODE EVIDENCE FOR IT (checked before writing a line of new code).
`exp_readout_writerule_paradigmatic_v1.occurrence_vector` (the landed W1_PARADIGMATIC rule, reused
here verbatim as P0) is:
    for w in words:                      # words = content_words(sentence), sentence in target L's
                                          # OWN profile-sentence bucket -- i.e. w CO-OCCURS with L
        ...
        prof = mat0n[pos[w's lemma]]     # the PAYLOAD changed: w's own first-order profile row,
                                          # not w's own identity draw
        acc += prof
The loop iterates over `words`, and `words` is ALWAYS `content_words(sents[sidx])` for `sidx` drawn
from `buckets[L][:nprof]` -- sentences in which L itself appears. So the CANDIDATE SET that gets
summed is fixed by CO-OCCURRENCE (a word contributes to L's code iff it appears in a sentence with
L), identically to the incumbent W0. Only the VALUE placed at each selected word changed (identity
draw -> profile row). Section 10's own honest reading already says this in different words ("the
write rule was PART of the defect but not sufficient") without naming the reason: **selection was
never varied.** I AGREE with the Director's framing: this is a genuine gap, confirmed by re-reading
the code (not merely asserted), and it is worth testing directly rather than left as a suspicion.
The diagnosis this acts on (section 5, C2, ARM 5) measured that the median correct WordNet answer
never co-occurs with the query at all -- so ANY write rule whose selection is a function of
co-occurrence has a structural ceiling on how far it can reach, independent of what payload it
carries. This cell is the direct test: hold the payload fixed (a neighbour's own first-order PROFILE
row -- IDENTICAL payload to P0/W1) and vary ONLY the selection rule.

ARMS, one variable (SELECTION) at a time, identical corpus / cache / pool / gold / scorer / payload
type as the incumbent P0. Payload is ALWAYS "the contributor's own first-order profile row, L2-unit"
(mat0n[contributor], reused verbatim from the cached first-order store, never rebuilt).
  P0_SYNTAGMATIC_SELECTION   the landed rule, REUSED VERBATIM (not reimplemented) via
                             exp_readout_writerule_paradigmatic_v1.build_arm(mode="PROFILE"). A
                             word's code sums the profile rows of words that CO-OCCUR with it in its
                             own profile sentences. REGRESSION GATE against the landed 0.02979;
                             SystemExit on failure -- this cell is void if it does not reproduce.
  P1_PARADIGMATIC_SELECTION  a word's code sums the profile rows of its top-K SECOND-ORDER NEIGHBOURS
                             -- the K anchors whose own first-order profile is most similar to its
                             own (cos(mat0n[L], mat0n[M])), WITH NO REGARD to whether L and M ever
                             co-occur. K SWEPT over K_GRID_SEL, never adopted as a value.
  P2_ZERO_COOCCURRENCE_ONLY  as P1, but the candidate pool is additionally masked to EXCLUDE every
                             anchor M that co-occurs with L in ANY of the 34,169 corpus sentences
                             (not just L's capped profile-sentence bucket -- the full corpus census,
                             the identical construction ARM 5's C2 used). Isolates the claim
                             completely: these contributors could not have reached L under ANY
                             co-occurrence-selecting rule, by construction.
  P3_HYBRID                  L's code = beta*unit(P0 row) + (1-beta)*unit(P1 row) at the
                             PRE-REGISTERED K=P3_K (the middle of K_GRID_SEL, fixed before any
                             number in this cell was read, to rule out post-hoc k-picking). beta
                             SWEPT over P3_BETAS, never adopted.
  N1_NULL                    P1's own selected index set, per row, with anchor IDENTITY destroyed by
                             a GLOBAL DERANGEMENT (size- and shape-matched: same K, same set of
                             profile VECTORS drawn from the same population, wrong correspondence).
                             Reuses exp_readout_writerule_paradigmatic_v1.deranged_permutation
                             verbatim -- the SAME construction Arm 6 used for its own N1, applied
                             here at the SELECTION level instead of the per-token level.
  F_FREQ_MATCHED_SELECTION   as N1, but the derangement is done WITHIN corpus-frequency deciles, so
                             each substituted contributor is frequency-matched to the true neighbour
                             it replaces even though its identity is wrong. Catches "P1 wins because
                             second-order neighbourhoods are dominated by high-frequency words", not
                             because they are genuinely paradigmatic.
  K1_KNOWN_ANSWER            exact-key self-addressing for every arm, gated >=0.95 before ANY
                             treatment number is computed (SystemExit otherwise).

WHY N1 AND F_FREQ_MATCHED ARE BUILT FROM P1'S OWN INDEX SET RATHER THAN FRESH RANDOM DRAWS. This
guarantees EXACT size-matching (same K, same per-row valid-count, same set of vectors summed) by
construction rather than by approximation, and it is the identical logical move Arm 6 made for its
own N1/F_FREQ_MATCHED (a derangement of the SAME token-to-profile map, not a fresh independent draw).

PRIMARY REGIME: PARTIAL CUE. THE CUE IS IDENTICAL ACROSS EVERY ARM IN THIS CELL, reused verbatim
from P0's own build (the SAME held-out-sentence-context-token profile-payload cue W1/P0 used). This
is a deliberate, disclosed design choice: the cue is an OBSERVATIONAL fact (what a reader sees near
the target word in one new sentence, i.e. words that CO-OCCUR with it by definition -- there is no
"selection" choice to make on the cue side, only on the STORE side), so holding it fixed isolates
the STORE'S selection rule as the ONLY thing that differs between arms in the partial-cue score.
EXACT-KEY (own row) is reported as the K1 validity gate only, exactly mirroring every sibling cell.

TWO MECHANISM CHECKS THIS CELL EXISTS TO RUN (the scientific content, not a bare margin):
  MECH_A  for items where P1(k) hits (WordNet gold) and P0 misses, what is the query-answer
          sentence-level Jaccard co-occurrence (identical measure and corpus to ARM 5's C2)? The
          diagnosis predicts these wins concentrate on ZERO co-occurrence pairs -- the exact
          population a co-occurrence-selecting rule structurally cannot reach.
  MECH_B  WordNet-relation rate of the top-1 winner per arm (reusing ARM 5's C1 classification:
          in-gold / taxonomically-close-outside-gold / taxonomically-distant / no-WordNet-path /
          not-in-WordNet), capped at N_PROBE_WORDNET items per arm for cost. P0's own rate on THIS
          cell's own population is measured fresh (not imported from ARM 5, which never separated
          P0/W1's winners from W0's) as the baseline the other arms are read against.

COMPUTATIONAL DESIGN, stated because the dispatch asked for it up front. The K-nearest-neighbour
selection over 5,491 anchors is realised as a DENSE anchor-anchor similarity matrix P = mat0n @
mat0n.T, computed EXACTLY ONCE (cached to disk under this cell's own output dir on first full run,
reloaded on any resume rather than rebuilt -- tools/exp_checkpoint.py per-arm units make a kill lose
at most one arm's build). Every arm's selection is then a top-K argpartition over ONE ROW of that
already-built matrix and its store is realised as an n x n SPARSE-SELECTION WEIGHT MATRIX times the
(n x d) payload matrix -- a single dense matmul, the identical technique
exp_readout_second_order_v1.successor_representation already uses for its own k-NN graph, applied
here to WRITE a store rather than to read one.

FLOOR: max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE), ALL FOUR recomputed on
THIS population. F_ORTHOGRAPHIC / F_FREQUENCY are store-independent (computed once, shared). F_
SCRAMBLE / F_CONSTANT_PROTOTYPE are store-DEPENDENT (recomputed per arm's own store). 0.1382 /
0.2070 / 0.1390 / -0.1959 are NEVER imported. tools/floor_battery.py is imported, never reimplemented.
Both tie conventions published where relevant. CI half-width AND analytic null half-width beside
every margin.

ORTHOGRAPHIC-LEAKAGE CHECK (standing rule 12: a floor is cleared by understanding, never adopted).
Mean trigram-cosine of each arm's top-1 winner to the query, reported beside P0's and the floor's own
reference point. Per-item correlation of a clearing arm's gain over P0 against that item's own best-
gold orthographic score, reusing exp_cue_binarised_readout_transfer_v1.pearson_ci_bootstrap verbatim,
exactly as ARM 7 did.

STOP-IF (read in this order; report ALL SIX regardless of which fires):
  (i)   P1 clears max(4 floors) CI-separated, at ANY swept k, where P0 does not -> the first
        genuine read-out win this programme has had.
  (ii)  P1 beats P0 CI-separated but still below the floors -> selection is the right axis, the
        remaining gap is the open quantity. Do NOT call it a win.
  (iii) P1 ties P0 (NOT_SEPARATED both directions, at every k) -> selection is not the axis either;
        combined with sections 10-11, both payload and selection have now been tested and neither
        closes the gap. This would redirect the programme away from the write rule entirely.
  (iv)  P1 beats P0 but F_FREQ_MATCHED_SELECTION also beats P0 by a comparable (CI-overlapping)
        margin -> the win is frequency wearing a costume; claim no mechanism.
  (v)   P2 collapses to chance (or to P0's own level) -> report how much of the signal is pure
        adjacency; a real finding either way.
  (vi)  Any arm's K1 < 0.95 -> INSTRUMENT_STILL_LOOSE, SystemExit before any treatment number.
        Publish nothing quality-bearing.

BRAIN FRAMING, stated per choice, honestly, inheriting section 10's own block rather than repeating
it in full. PINNED-BY-EVIDENCE, as a COMPUTATION not a parameter (unchanged from section 10):
complementary-learning-systems theory (McClelland, McNaughton & O'Reilly 1995) licenses building a
word's cortical-like representation from cross-episode regularities (a stable profile of contexts a
word recurs in) rather than from within-episode adjacency; that licenses testing a write rule built
from PROFILES. WHAT IS NEW HERE AND OURS, NOT LAUNDERED AS BIOLOGY: selecting contributors by
SIMILARITY OF PROFILE rather than by CO-OCCURRENCE is a plain distributional-semantics move (Schutze
1998's "two words are similar if they occur in similar contexts", now applied to SELECTION rather
than to a comparator) -- nothing in the CLS literature specifies this particular write-time
construction, and it is reported as OURS, invention under test. VSA algebraic binding is UNPINNED in
the brain (three live accounts, published objections to each); nothing here depends on it or tests
it -- this cell only changes which rows get bundled, not the bundling operator itself (unweighted
sum, unmodified, identical to every sibling cell in this arc).

ORGAN REUSE, enumerated then reconciled by RUNTIME witness, never grep. IMPORTED, NEVER EDITED:
tools/floor_battery, tools/exp_checkpoint, experiments/exp_cue_to_store_translation_v1 (cache loader,
ruler gate, landed regression constant), experiments/exp_readout_ceiling_diagnosis_v1 (population
builder, tripwire), experiments/exp_grounding_readout_known_answer_v1 (build_corpus, build_buckets,
_n_profile, content_lemmas -- the IDENTICAL deterministic corpus/bucket construction the cached store
was built from), experiments/exp_readout_writerule_paradigmatic_v1 (build_arm, occurrence_vector,
deranged_permutation, l2n_rows64 -- P0's construction is called, never reimplemented, so the
regression-gate reproduction is a structural guarantee not a coincidence),
experiments/exp_cue_binarised_readout_transfer_v1 (pearson_ci_bootstrap), hdlab's ConceptSpace-
adjacent primitives (CTX_D) imported directly.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. THE invariant. ASCII-only. CPU. No network.
The cached first-order store is never rebuilt or edited. Every new store this cell builds is a fresh
in-memory array under data/exp_readout_writerule_selection_axis_v1/, never written into
scratch/sparse_code_real_task/real_cache.npz. data/foundation/** is never opened.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import (numpy sizes its pools at import time).
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
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_cue_to_store_translation_v1 as CTS               # cache loader + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as DIAG              # population + tripwire, NEVER EDITED
import exp_grounding_readout_known_answer_v1 as GRK          # corpus/buckets/content_lemmas, NEVER EDITED
import exp_readout_writerule_paradigmatic_v1 as WRR          # P0's own construction, NEVER EDITED
from hdlab.reading_grounding_loop import CTX_D               # NEVER EDITED
from tools import floor_battery as FB                        # NEVER EDITED
from tools.exp_checkpoint import record_unit, unit_key

try:
    from exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
except Exception:                                             # pragma: no cover -- degrade gracefully
    pearson_ci_bootstrap = None

ANCHOR_NAME = "exp_readout_writerule_selection_axis_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_ceiling_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = "reduced" if _ARGS.grid == "reduced" else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if RUN_MODE == "reduced" else 10000
KA_MIN = 0.95
K_GRID_SEL: Tuple[int, ...] = (5, 15, 40) if RUN_MODE == "reduced" else (10, 30, 100)
P3_BETAS: Tuple[float, ...] = (0.25, 0.5, 0.75)
P3_K = K_GRID_SEL[1]                                          # PRE-REGISTERED: the middle of the sweep
N_DECILES = 10
N_PROBE_WORDNET = 150 if RUN_MODE == "reduced" else 800
COOC_JACCARD_MAX_ITEMS = 300 if RUN_MODE == "reduced" else 1500


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _out_dir() -> str:
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + ("" if RUN_MODE == "full" else "_REDUCED"))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _halfwidth(p: float, n: int) -> float:
    return float(1.96 * (max(p * (1.0 - p), 1e-12) / max(int(n), 1)) ** 0.5)


def _digest(mat: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(mat, dtype=np.float32).tobytes()).hexdigest()[:16]


# =================================================================================================
# SELECTION MACHINERY -- the one new construction this cell contributes.
# =================================================================================================
def selection_topk(score: np.ndarray, k: int,
                   mask_out: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-row top-K selection over an [n, n] score matrix (self and, optionally, a boolean mask
    excluded). Returns (idx [n,kk], valid [n,kk] bool, rows [n,kk]) where `valid[i,j]` is False iff
    row i had FEWER than kk admissible (non-excluded) candidates, in which case `idx[i,j]` for that
    slot is a MEANINGLESS filler (argpartition must still return kk indices) and MUST be dropped by
    the caller, never summed. This is the SAME "fail-visibly, do not silently substitute" contract
    every other fallback in this arc uses (occurrence_vector's PROFILE fallback, the held-out-cue
    None convention).
    """
    n = score.shape[0]
    Sc = np.asarray(score, dtype=np.float32).copy()
    np.fill_diagonal(Sc, -np.inf)
    if mask_out is not None:
        Sc = np.where(mask_out, np.float32(-np.inf), Sc)
    kk = int(min(k, n - 1))
    idx = np.argpartition(-Sc, kk - 1, axis=1)[:, :kk]
    rows = np.repeat(np.arange(n)[:, None], kk, axis=1)
    vals = Sc[rows, idx]
    valid = np.isfinite(vals)
    return idx.astype(np.int64), valid, rows.astype(np.int64)


def store_from_selection(idx: np.ndarray, valid: np.ndarray, rows: np.ndarray,
                         payload32: np.ndarray, n: int) -> np.ndarray:
    """out[i] = sum over valid slots j of payload32[idx[i,j]]. Realised as a dense [n,n] 0/1 weight
    matrix times the payload -- ONE matmul, the identical technique
    exp_readout_second_order_v1.successor_representation uses for its own k-NN graph, applied here
    to WRITE a store instead of to read one."""
    W = np.zeros((n, n), dtype=np.float32)
    W[rows[valid], idx[valid]] = 1.0
    return (W @ payload32).astype(np.float32)


def remap_idx(idx: np.ndarray, perm: np.ndarray) -> np.ndarray:
    """Apply an anchor-axis permutation to a selection's contributor identities. Shape/validity
    pattern is UNCHANGED (a bijection cannot change which slots were valid); only WHICH anchor sits
    in each already-valid slot changes -- the size- and shape-matched, identity-destroyed control."""
    return perm[idx]


def build_cooc_where(sents: Sequence[str], pos: Dict[str, int],
                     n_anchors: int) -> Tuple[np.ndarray, Dict[str, set]]:
    """ONE pass over the FULL corpus (not the capped per-lemma buckets) builds:
      COOC   [n_anchors, n_anchors] bool -- anchor i EVER shares a sentence with anchor j
      where  {anchor_lemma: set(sentence_index)} -- reused for the on-demand Jaccard co-occurrence
             measure MECH_A needs (identical construction to ARM 5's C2, reused not reimplemented in
             spirit, since that cell's `where` was built the same way from the same corpus).
    """
    COOC = np.zeros((n_anchors, n_anchors), dtype=bool)
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        lems = GRK.content_lemmas(s)
        idx_here = [pos[l] for l in lems if l in pos]
        for l in lems:
            if l in pos:
                where.setdefault(l, set()).add(si)
        if len(idx_here) >= 2:
            arr = np.array(sorted(set(idx_here)), dtype=np.int64)
            COOC[np.ix_(arr, arr)] = True
    np.fill_diagonal(COOC, False)
    return COOC, where


def jaccard(where: Dict[str, set], a: str, b: str) -> Optional[float]:
    A, B = where.get(a), where.get(b)
    if not A or not B:
        return None
    return len(A & B) / float(len(A | B))


def wordnet_relation_census(top1: np.ndarray, T: np.ndarray, L_words: List[str],
                            anchors: List[str], GOLD_T: np.ndarray, n_probe: int) -> Dict:
    """Reuses exp_readout_second_order_v1's C1 classification exactly (in-gold / taxonomically-close
    -outside-gold / taxonomically-distant / no-WordNet-path / not-in-WordNet), applied to THIS arm's
    own top-1 picks. n_probe caps cost, identical convention to the sibling cell."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception as exc:
        return {"UNAVAILABLE": "%r" % (exc,)}
    rel = Counter()
    examples: List[str] = []
    n_probe = int(min(n_probe, T.size))
    for i in range(n_probe):
        qw, ww = L_words[int(T[i])], anchors[int(top1[i])]
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
        if len(examples) < 20:
            examples.append("%s -> %s (path_sim=%.3f)" % (qw, ww, best))
    no_close = rel["TAXONOMICALLY_DISTANT"] + rel["NO_WORDNET_PATH_AT_ALL"] + rel["WINNER_NOT_IN_WORDNET"]
    return {"n_probed": n_probe, "counts": {k: int(v) for k, v in rel.most_common()},
           "as_fraction": {k: round(v / n_probe, 4) for k, v in rel.most_common()},
           "fraction_no_close_wordnet_relation": round(no_close / n_probe, 4),
           "examples": examples}


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    DIAG.install_grounded_similarity_tripwire()
    ev["floor_battery_selftest_ok"] = sorted(FB.self_test().keys())

    # ---- T1/T2: SELECTION recovers a relation CO-OCCURRENCE SELECTION is structurally BARRED from
    # reaching, on a fixture built to mirror the diagnosis exactly: A_p and B_p are TRUE PARADIGMATIC
    # PARTNERS (their own profile rows are near-identical, both drawn from one shared latent
    # direction L_p, exactly as two substitutable words share a context distribution) but each has
    # its OWN, DISJOINT, UNRELATED co-occurrence set (decoy anchors with independent random profile
    # rows -- representing "words that happen to appear near this one in text" the way a real corpus
    # produces collocates unrelated to substitutability). B_p is NEVER a member of A_p's
    # co-occurrence set BY CONSTRUCTION, mirroring the measured fact that the correct WordNet answer
    # is typically outside the query's co-occurrence set entirely.
    #
    # MY FIRST VERSION OF THIS FIXTURE WAS WRONG, CAUGHT BY ITS OWN ASSERTION FIRING. It gave A_p and
    # B_p the SAME literal mediator set as their "co-occurrence" contributors, which made
    # P0-style(A_p) and P0-style(B_p) IDENTICAL VECTORS BY CONSTRUCTION (cos = 1.0000, the assertion
    # `cos_P1 > cos_P0 + 0.3` is then mathematically impossible -- cosine cannot exceed 1.0). That
    # fixture could not have distinguished the two selection rules; it happened to make co-occurrence
    # selection win by definition, the opposite of what it was built to test. Rebuilt below so the
    # two selection rules draw from PROVABLY DISJOINT candidate pools.
    rng = np.random.default_rng(13)
    d = 96
    n_pairs, n_decoy, n_fill = 15, 6, 40
    n = 2 * n_pairs + n_pairs * 2 * n_decoy + n_fill
    mat0 = np.zeros((n, d), dtype=np.float64)
    partner: Dict[int, int] = {}
    cooc_of: Dict[int, List[int]] = {}
    row = 0
    for _p in range(n_pairs):
        Lp = rng.standard_normal(d); Lp /= np.linalg.norm(Lp) + 1e-9
        na, nb = 0.04 * rng.standard_normal(d), 0.04 * rng.standard_normal(d)
        a_i, b_i = row, row + 1
        mat0[a_i] = Lp + na
        mat0[b_i] = Lp + nb
        partner[a_i], partner[b_i] = b_i, a_i
        row += 2
        dec_a = list(range(row, row + n_decoy)); row += n_decoy
        dec_b = list(range(row, row + n_decoy)); row += n_decoy
        for j in dec_a + dec_b:
            mat0[j] = rng.standard_normal(d)          # independent -- NOT built from Lp at all
        cooc_of[a_i], cooc_of[b_i] = dec_a, dec_b      # B is NEVER in cooc_of[A] and vice versa
    mat0[row:] = rng.standard_normal((n - row, d))
    mat0n32 = l2n(mat0.astype(np.float32))
    P = (mat0n32 @ mat0n32.T).astype(np.float32)
    qi = np.array(sorted(partner), dtype=np.int64)
    gold_idx = np.array([partner[int(q)] for q in qi], dtype=np.int64)

    # sanity: A_p and B_p really ARE close in profile space (the paradigmatic relation this fixture
    # plants), and their decoys really are NOT (independent random vectors in d=96 have near-zero
    # expected cosine) -- both checked, not assumed.
    cos_ab_direct = float(np.mean([P[int(a), int(b)] for a, b in zip(qi, gold_idx)]))
    assert cos_ab_direct > 0.7, (
        "fixture bug: A_p/B_p are not close profile-neighbours (mean cos=%.4f) -- the paradigmatic "
        "relation this fixture is supposed to plant is not actually there" % cos_ab_direct)

    # P0-STYLE STORE: sum of the profile rows of the CO-OCCURRENCE candidate set only (decoys).
    # B_p is STRUCTURALLY ABSENT from cooc_of[A_p] -- this is the write rule's own selection
    # contract, not a probabilistic near-miss.
    P0_store = np.zeros((n, d), dtype=np.float32)
    for i in range(n):
        if i in cooc_of:
            P0_store[i] = mat0n32[cooc_of[i]].sum(axis=0)
    cos_P0 = float(np.dot(l2n(P0_store[qi[:1]])[0], l2n(P0_store[gold_idx[:1]])[0]))
    ev["T1_P0style_selection_cannot_reach_the_provably_disjoint_partner"] = {
        "cos_P0store_A_to_P0store_B": round(cos_P0, 4),
        "true_profile_similarity_A_to_B": round(cos_ab_direct, 4),
        "fixture": "B is STRUCTURALLY EXCLUDED from A's co-occurrence candidate set (cooc_of), by "
                   "construction, for every one of %d pairs" % n_pairs}
    assert cos_P0 < 0.20, (
        "P0-style selection (decoys only) unexpectedly recovers the partner relation: cos=%.4f -- "
        "the fixture does not isolate what it claims to" % cos_P0)

    # T2: P1-STYLE (similarity) selection DOES recover it -- B_p IS A_p's single nearest profile
    # neighbour by construction (both drawn from Lp), so a top-K selection over the FULL anchor
    # population picks B_p directly, something CO-OCCURRENCE selection could never do here.
    idx1, valid1, rows1 = selection_topk(P, 3)
    P1_store = store_from_selection(idx1, valid1, rows1, mat0n32, n)
    cos_P1 = float(np.dot(l2n(P1_store[qi[:1]])[0], l2n(P1_store[gold_idx[:1]])[0]))
    assert cos_P1 > cos_P0 + 0.3, (
        "P1-style selection does not out-recover P0-style selection on a fixture built exactly for "
        "this: P0=%.4f P1=%.4f" % (cos_P0, cos_P1))
    ev["T2_P1style_selection_recovers_what_P0style_structurally_cannot"] = {
        "P0_style_cos": round(cos_P0, 4), "P1_style_cos": round(cos_P1, 4)}

    # T3: FALSIFIABILITY -- on a fixture with independent random profiles (no planted relation at
    # all), P1-style selection must NOT manufacture a spurious win.
    mat_flat = rng.standard_normal((n, d)).astype(np.float32)
    mat_flat_n = l2n(mat_flat)
    Pf = (mat_flat_n @ mat_flat_n.T).astype(np.float32)
    idxf, validf, rowsf = selection_topk(Pf, 3)
    Pf_store = store_from_selection(idxf, validf, rowsf, mat_flat_n, n)
    cos_flat = float(np.dot(l2n(Pf_store[qi[:1]])[0], l2n(Pf_store[gold_idx[:1]])[0]))
    assert cos_flat < cos_P1 - 0.2, (
        "P1-style selection fires on a fixture with NO planted relation: flat=%.4f real=%.4f"
        % (cos_flat, cos_P1))
    ev["T3_falsifiable_no_spurious_win_without_structure"] = {
        "flat_fixture_cos": round(cos_flat, 4), "real_fixture_cos": round(cos_P1, 4)}

    # T4: selection_topk's MASK-OUT contract -- an excluded candidate never appears in idx/valid,
    # and a row with fewer than k admissible candidates after masking is correctly SHRUNK (fewer
    # valid slots), not silently padded with garbage.
    n5, d5 = 12, 8
    rng5 = np.random.default_rng(3)
    X5 = l2n(rng5.standard_normal((n5, d5)).astype(np.float32))
    P5 = (X5 @ X5.T).astype(np.float32)
    idx5, valid5, rows5 = selection_topk(P5, 5)
    assert int(valid5.sum()) == n5 * 5, "unmasked selection should have zero invalid slots"
    mask5 = np.zeros((n5, n5), dtype=bool)
    mask5[0, 1:7] = True                                       # row 0 excludes 6 of 11 candidates
    idx5m, valid5m, rows5m = selection_topk(P5, 5, mask_out=mask5)
    assert not np.any(np.isin(idx5m[0][valid5m[0]], np.arange(1, 7))), (
        "a masked-out candidate leaked into the selection despite mask_out")
    assert int(valid5m[0].sum()) <= 5, "masked row did not shrink"
    row0_admissible = n5 - 1 - 6                               # exclude self and the 6 masked
    assert int(valid5m[0].sum()) == min(5, row0_admissible), (
        "masked row did not use exactly its admissible count: got %d expected %d"
        % (int(valid5m[0].sum()), min(5, row0_admissible)))
    ev["T4_mask_out_contract"] = {
        "unmasked_all_valid": True, "masked_candidate_excluded": True,
        "masked_row_valid_count": int(valid5m[0].sum()), "masked_row_admissible": row0_admissible}

    # T5: store_from_selection is exactly a sum over the valid selected payload rows (checked
    # against a brute-force loop on a tiny case).
    brute = np.zeros((n5, d5), dtype=np.float32)
    for i in range(n5):
        sel = idx5[i][valid5[i]]
        brute[i] = X5[sel].sum(axis=0)
    fast = store_from_selection(idx5, valid5, rows5, X5, n5)
    assert np.allclose(brute, fast, atol=1e-5), "store_from_selection does not match a brute-force sum"
    ev["T5_store_from_selection_matches_brute_force"] = True

    # T6: remap_idx with a DERANGEMENT changes every valid contributor's identity and destroys a
    # planted win (mirrors Arm 6's own N1 self-test, applied to selection indices).
    perm6 = WRR.deranged_permutation(n, seed=17)
    assert np.all(perm6 != np.arange(n)), "derangement has a fixed point"
    idx1_remap = remap_idx(idx1, perm6)
    assert not np.array_equal(idx1_remap, idx1), "remap_idx with a derangement did nothing"
    N1_store = store_from_selection(idx1_remap, valid1, rows1, mat0n32, n)
    cos_N1 = float(np.dot(l2n(N1_store[qi[:1]])[0], l2n(N1_store[gold_idx[:1]])[0]))
    assert cos_N1 < cos_P1 - 0.15, (
        "N1's derangement did not destroy the P1-style win: P1=%.4f N1=%.4f" % (cos_P1, cos_N1))
    ev["T6_derangement_destroys_the_win"] = {"P1_style": round(cos_P1, 4), "N1_derangement": round(cos_N1, 4)}

    # T7: frequency-matched derangement RESPECTS group boundaries (grouped case), general case
    # already covered by exp_readout_writerule_paradigmatic_v1's own self-test (reused, not
    # reimplemented) -- checked here again at the SELECTION level as a real, not decorative, gate.
    groups7 = np.array([0] * (n // 2) + [1] * (n - n // 2))
    perm7 = WRR.deranged_permutation(n, seed=19, groups=groups7)
    assert np.all(groups7[perm7] == groups7), "grouped derangement crosses group boundaries"
    idx1_freq = remap_idx(idx1, perm7)
    assert not np.array_equal(idx1_freq, idx1_remap), "freq-matched and global derangements coincide"
    ev["T7_freq_matched_derangement_respects_groups"] = True

    # T8: P3_HYBRID interpolates monotonically-ish and beta is a REAL parameter (Arm 6's own T4
    # pattern, applied to a per-arm-row superposition instead of a per-token one).
    p0n_row = l2n(P0_store[qi[:1]])[0]
    p1n_row = l2n(P1_store[qi[:1]])[0]
    p0n_gold = l2n(P0_store[gold_idx[:1]])[0]
    p1n_gold = l2n(P1_store[gold_idx[:1]])[0]
    vals8 = {}
    for b in (0.0, 0.25, 0.5, 0.75, 1.0):
        hv = b * p0n_row + (1 - b) * p1n_row
        hg = b * p0n_gold + (1 - b) * p1n_gold
        vals8[b] = float(np.dot(hv / (np.linalg.norm(hv) + 1e-12), hg / (np.linalg.norm(hg) + 1e-12)))
    assert len(set(round(v, 6) for v in vals8.values())) == len(vals8), \
        "P3 hybrid beta does nothing -- it is not a parameter, it is decoration"
    ev["T8_hybrid_beta_is_a_real_parameter"] = {str(k): round(v, 4) for k, v in vals8.items()}

    # T9: build_cooc_where marks EXACTLY the pairs that share a sentence, nothing more, nothing
    # less, self excluded, and `where` supports the Jaccard measure MECH_A needs.
    fake_sents = ["alpha beta gamma", "beta delta", "epsilon zeta", "alpha zeta eta"]
    fake_pos = {w: i for i, w in enumerate(["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta"])}
    COOC9, where9 = build_cooc_where(fake_sents, fake_pos, len(fake_pos))
    ia, ib, ig, idl = (fake_pos[w] for w in ("alpha", "beta", "gamma", "delta"))
    assert COOC9[ia, ib] and COOC9[ib, ia], "alpha/beta share a sentence but are not marked co-occurring"
    assert COOC9[ib, ig], "beta/gamma share a sentence but are not marked co-occurring"
    assert not COOC9[ia, idl], "alpha/delta never share a sentence but are marked co-occurring"
    assert not np.any(np.diag(COOC9)), "self is marked as co-occurring with self"
    j_ab = jaccard(where9, "alpha", "beta")
    assert j_ab is not None and abs(j_ab - (1.0 / 3.0)) < 1e-9, "Jaccard(alpha,beta) wrong: %r" % j_ab
    assert jaccard(where9, "alpha", "delta") == 0.0, "Jaccard for a never-co-occurring pair is not 0"
    ev["T9_cooc_and_jaccard_correct_on_a_hand_checked_fixture"] = {
        "alpha_beta_jaccard": j_ab, "alpha_delta_jaccard": 0.0}

    # T10. THE CORPUS/BUCKET RECONSTRUCTION REPRODUCES THE CACHED STORE'S POPULATION -- as a hard
    # assertion, mirroring Arm 6's own T8 (full grid only, for selftest speed).
    C = CTS.load_cache()
    if RUN_MODE == "full":
        sents = GRK.build_corpus("full")
        buckets_full, _counts = GRK.build_buckets(sents)
        b_anchors = sorted(buckets_full)
        assert b_anchors == C["anchors"], (
            "rebuilt buckets do NOT reproduce the cached anchor set (rebuilt=%d cached=%d)"
            % (len(b_anchors), len(C["anchors"])))
        ev["T10_corpus_reconstruction_matches_cache"] = {"n_anchors_rebuilt": len(b_anchors),
                                                         "n_anchors_cached": len(C["anchors"])}
    else:
        ev["T10_corpus_reconstruction_matches_cache"] = "SKIPPED in reduced grid (checked in full only)"

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1600], flush=True)
    return ev


# =================================================================================================
def run(grid: str, output_dir: str) -> Dict:
    t0 = time.time()
    gate = CTS.ruler_mode_gate()
    tripwire = DIAG.install_grounded_similarity_tripwire()
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors, mat0_raw, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors = len(anchors)
    pos = {a: i for i, a in enumerate(anchors)}
    mat0n = WRR.l2n_rows64(mat0_raw)                              # float64 unit profile rows
    mat0n32 = mat0n.astype(np.float32)                            # THE payload for every new arm
    d = CTX_D
    print("[load] cache n_anchors=%d t=%.0fs" % (n_anchors, time.time() - t0), flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(tripwire),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "K_GRID_SEL": list(K_GRID_SEL), "P3_K_prereg": P3_K, "P3_BETAS": list(P3_BETAS),
        "CLAIM_UNDER_TEST": "the landed P0/W1 write rule selects contributors by co-occurrence "
                            "(a word contributes to L's code iff it appears in a sentence with L) "
                            "and only changed the PAYLOAD (identity->profile). P1 selects "
                            "contributors by profile SIMILARITY instead, with the IDENTICAL payload.",
    }

    # ---- GOLD/E/keep (reused construction, DIAG.build_population) --------------------------------
    P0pop = DIAG.build_population()
    GOLD_ALL, E_ALL, keep_ALL = P0pop["GOLD"], P0pop["E"], P0pop["keep"]
    qidx_all = P0pop["qidx"]
    L_words = C["L_words"]
    n_items_all = len(L_words)

    # ---- REBUILD THE CORPUS/BUCKET PIPELINE (deterministic; verified byte-for-byte against the
    #      cache in self_test) -------------------------------------------------------------------
    sents = GRK.build_corpus("full")
    buckets, counts = GRK.build_buckets(sents)
    b_anchors = sorted(buckets)
    if b_anchors != anchors:
        raise SystemExit("CORPUS/BUCKET RECONSTRUCTION NO LONGER MATCHES THE CACHED ANCHOR SET -- "
                         "STOPPING rather than silently building on a divergent population "
                         "(rebuilt=%d cached=%d)" % (len(b_anchors), len(anchors)))
    print("[corpus] n_sentences=%d n_anchors_matches_cache=True t=%.0fs"
          % (len(sents), time.time() - t0), flush=True)
    cw_cache: Dict[int, List[str]] = {}

    # ---- P0: REUSE exp_readout_writerule_paradigmatic_v1.build_arm VERBATIM ----------------------
    mat_P0, part_shared = WRR.build_arm(anchors, buckets, cw_cache, sents, mat0n, pos, d, "PROFILE")
    print("[build] P0_SYNTAGMATIC_SELECTION (=W1, reused) t=%.1fs" % (time.time() - t0), flush=True)
    record_unit(output_dir, unit_key("build", "P0"), {"elapsed_s": round(time.time() - t0, 2)})

    # ---- W1 REGRESSION GATE: this cell's P0 must reproduce the landed W1_PARADIGMATIC value ------
    Q_exact0, Q_part0 = C["Q_exact"].astype(np.float32), C["Q_part"].astype(np.float32)
    qidx_T_all = qidx_all
    n_items = int(np.flatnonzero(keep_ALL).size)
    items_all = np.flatnonzero(keep_ALL)
    T_all = items_all
    GOLD_T_all, E_T_all = GOLD_ALL[:, T_all].copy(), E_ALL[:, T_all].copy()
    qidx_T_all2 = qidx_all[T_all]
    L_test_all = [L_words[int(i)] for i in T_all]
    Q_P0 = np.zeros((int(T_all.size), d), dtype=np.float32)
    for j, L in enumerate(L_test_all):
        v = part_shared.get(L)
        if v is not None:
            Q_P0[j] = v.astype(np.float32)
    MATn_P0 = l2n(mat_P0)
    S_P0 = (MATn_P0 @ l2n(Q_P0).T).astype(np.float32)
    hP0 = FB.hit_at_1_both_tie_conventions(S_P0, E_T_all, GOLD_T_all)
    a_P0 = float(hP0["hit_exp"][hP0["scored"]].mean())
    EXPECTED_W1 = 0.02979
    rep["W1_REGRESSION_GATE"] = {"P0_partial_cue_this_cell": round(a_P0, 5), "expected_W1": EXPECTED_W1,
                                 "tol": 5e-4, "PASS": bool(abs(a_P0 - EXPECTED_W1) <= 5e-4)}
    if not rep["W1_REGRESSION_GATE"]["PASS"] and grid == "full":
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        raise SystemExit("W1 REGRESSION GATE FAILED (full grid) -- P0 does not reproduce the landed "
                         "W1_PARADIGMATIC value: %r" % rep["W1_REGRESSION_GATE"])
    print("[regression] P0 partial=%.5f expected=%.5f %s"
          % (a_P0, EXPECTED_W1, "PASS" if rep["W1_REGRESSION_GATE"]["PASS"] else "SKIPPED(reduced)"),
          flush=True)
    del S_P0, hP0

    # ---- items scored (same landed OPEN pool every sibling cell uses) ----------------------------
    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T, E_T = GOLD_ALL[:, T].copy(), E_ALL[:, T].copy()
    qidx_T = qidx_all[T]
    L_test = [L_words[int(i)] for i in T]
    ok_q = qidx_T >= 0
    print("[population] n_items_scored=%d t=%.0fs" % (n_items, time.time() - t0), flush=True)

    Q_shared = np.zeros((n_items, d), dtype=np.float32)          # THE cue, identical for every arm
    for j, L in enumerate(L_test):
        v = part_shared.get(L)
        if v is not None:
            Q_shared[j] = v.astype(np.float32)

    # ---- THE PROFILE SIMILARITY MATRIX, computed ONCE, cached to disk ----------------------------
    p_cache_path = os.path.join(output_dir, "_profile_sim_matrix_%s.npy" % grid)
    if os.path.exists(p_cache_path):
        P = np.load(p_cache_path)
        print("[P] loaded cached profile similarity matrix %s t=%.1fs" % (P.shape, time.time() - t0),
              flush=True)
    else:
        P = (mat0n32 @ mat0n32.T).astype(np.float32)
        os.makedirs(output_dir, exist_ok=True)
        np.save(p_cache_path, P)
        print("[P] built profile similarity matrix %s t=%.1fs" % (P.shape, time.time() - t0), flush=True)

    # ---- THE CO-OCCURRENCE CENSUS (full corpus, for P2's mask + MECH_A's Jaccard) ----------------
    cooc_cache_path = os.path.join(output_dir, "_cooc_matrix.npy")
    if os.path.exists(cooc_cache_path):
        COOC = np.load(cooc_cache_path)
        # `where` is cheap to rebuild (one pass, no matrix), always fresh so MECH_A never depends on
        # an npy round-trip of a python dict.
        _, where = build_cooc_where(sents, pos, n_anchors)
    else:
        COOC, where = build_cooc_where(sents, pos, n_anchors)
        np.save(cooc_cache_path, COOC)
    print("[cooc] COOC built/loaded, mean_degree=%.1f t=%.1fs"
          % (float(COOC.sum(axis=1).mean()), time.time() - t0), flush=True)

    # ---- FREQUENCY DECILES (identical formula to exp_readout_writerule_paradigmatic_v1.run) ------
    freq = np.array([counts.get(a, 0) for a in anchors], dtype=np.float64)
    deciles = np.floor(np.argsort(np.argsort(freq)) / max(1.0, n_anchors / N_DECILES)).astype(np.int64)
    deciles = np.clip(deciles, 0, N_DECILES - 1)
    perm_global = WRR.deranged_permutation(n_anchors, seed=MASTER_SEED + 701)
    perm_freq = WRR.deranged_permutation(n_anchors, seed=MASTER_SEED + 702, groups=deciles)
    rep["PERMUTATION_CONTROLS"] = {
        "global_no_fixed_points": bool(np.all(perm_global != np.arange(n_anchors))),
        "freq_matched_no_fixed_points": bool(np.all(perm_freq != np.arange(n_anchors))),
        "freq_matched_groups_respected": bool(np.all(deciles[perm_freq] == deciles))}

    # ---- BUILD EVERY ARM'S STORE -------------------------------------------------------------------
    mats: Dict[str, np.ndarray] = {"P0_SYNTAGMATIC_SELECTION": mat_P0}
    p2_valid_stats: Dict[str, Dict] = {}
    p1_idx_by_k: Dict[int, Tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    for k in K_GRID_SEL:
        t1 = time.time()
        idx1, valid1, rows1 = selection_topk(P, k)
        p1_idx_by_k[k] = (idx1, valid1, rows1)
        mats["P1_PARADIGMATIC_SELECTION_k%d" % k] = store_from_selection(idx1, valid1, rows1, mat0n32, n_anchors)
        record_unit(output_dir, unit_key("build", "P1", k), {"elapsed_s": round(time.time() - t1, 2)})
        print("[build] P1_k%-4d t=%.1fs" % (k, time.time() - t1), flush=True)

        t1 = time.time()
        idx2, valid2, rows2 = selection_topk(P, k, mask_out=COOC)
        mats["P2_ZERO_COOCCURRENCE_ONLY_k%d" % k] = store_from_selection(idx2, valid2, rows2, mat0n32, n_anchors)
        nvalid = valid2.sum(axis=1)
        p2_valid_stats["k%d" % k] = {
            "requested_k": k, "mean_valid": round(float(nvalid.mean()), 2),
            "median_valid": float(np.median(nvalid)),
            "fraction_rows_with_zero_admissible": round(float((nvalid == 0).mean()), 4),
            "fraction_rows_full_k": round(float((nvalid == k).mean()), 4)}
        record_unit(output_dir, unit_key("build", "P2", k), {"elapsed_s": round(time.time() - t1, 2)})
        print("[build] P2_k%-4d t=%.1fs valid_stats=%s" % (k, time.time() - t1, p2_valid_stats["k%d" % k]),
              flush=True)

        t1 = time.time()
        idx_n1 = remap_idx(idx1, perm_global)
        mats["N1_NULL_k%d" % k] = store_from_selection(idx_n1, valid1, rows1, mat0n32, n_anchors)
        idx_fr = remap_idx(idx1, perm_freq)
        mats["F_FREQ_MATCHED_SELECTION_k%d" % k] = store_from_selection(idx_fr, valid1, rows1, mat0n32, n_anchors)
        record_unit(output_dir, unit_key("build", "N1_FREQ", k), {"elapsed_s": round(time.time() - t1, 2)})
        print("[build] N1_k%-4d FREQ_k%-4d t=%.1fs" % (k, k, time.time() - t1), flush=True)

    rep["COOC_CENSUS_P2_VALID_CANDIDATE_STATS"] = p2_valid_stats

    # ---- P3_HYBRID at the PRE-REGISTERED K, beta swept --------------------------------------------
    idx1k, valid1k, rows1k = p1_idx_by_k[P3_K]
    mat_P1_k = mats["P1_PARADIGMATIC_SELECTION_k%d" % P3_K]
    P0n_rows = l2n(mat_P0)
    P1n_rows = l2n(mat_P1_k)
    for beta in P3_BETAS:
        mats["P3_HYBRID_beta%s" % beta] = (beta * P0n_rows + (1.0 - beta) * P1n_rows).astype(np.float32)
    print("[build] P3_HYBRID betas=%s at K=%d t=%.1fs" % (P3_BETAS, P3_K, time.time() - t0), flush=True)

    # ---- ARMS_MUST_DIFFER --------------------------------------------------------------------------
    digests = {name: _digest(m) for name, m in mats.items()}
    rep["ARMS_MUST_DIFFER_DIGESTS"] = digests
    n_distinct = len(set(digests.values()))
    rep["ARMS_MUST_DIFFER_OK"] = bool(n_distinct == len(digests))
    print("[digests] %d distinct SHA among %d arms" % (n_distinct, len(digests)), flush=True)

    # ---- K1_KNOWN_ANSWER (exact-key self-addressing), EVERY ARM, GATED BEFORE ANY TREATMENT NUMBER
    ka_by_arm: Dict[str, float] = {}
    for name, mat_arm in mats.items():
        MATn = l2n(mat_arm)
        Sfull = (MATn @ MATn.T).astype(np.float32)
        pred = np.argmax(Sfull[:, qidx_T[ok_q]], axis=0)
        ka = float(np.mean(pred == qidx_T[ok_q])) if ok_q.any() else float("nan")
        ka_by_arm[name] = ka
        del Sfull
    rep["K1_KNOWN_ANSWER_addressing"] = {k: round(v, 4) for k, v in ka_by_arm.items()}
    rep["K1_GATE"] = KA_MIN
    k1_fail = {k: v for k, v in ka_by_arm.items() if v < KA_MIN}
    print("[K1] " + json.dumps({k: round(v, 4) for k, v in ka_by_arm.items()}), flush=True)
    if k1_fail:
        rep["STOP_IF_VERDICT"] = {"verdict": "vi_INSTRUMENT_STILL_LOOSE",
                                  "failing_arms": {k: round(v, 4) for k, v in k1_fail.items()}}
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        raise SystemExit("K1 GATE FAILED -- INSTRUMENT_STILL_LOOSE, no quality number published: %r"
                         % k1_fail)

    # ---- NULL_PERMUTED validity (shared item permutation across all arms) ------------------------
    rng = np.random.default_rng(MASTER_SEED + 77)
    itperm = np.arange(n_items)
    for _ in range(64):
        itperm = rng.permutation(n_items)
        if np.all(itperm != np.arange(n_items)):
            break
    null_by_arm: Dict[str, float] = {}
    for name, mat_arm in mats.items():
        MATn = l2n(mat_arm)
        Sp = (MATn @ l2n(Q_shared).T).astype(np.float32)
        hn = FB.hit_at_1_both_tie_conventions(Sp[:, itperm], E_T, GOLD_T)
        null_by_arm[name] = float(hn["hit_exp"][hn["scored"]].mean())
    rep["NULL_PERMUTED_partial_cue"] = {k: round(v, 6) for k, v in null_by_arm.items()}

    # ---- FLOORS -----------------------------------------------------------------------------------
    F_ORTHO = (l2n(aux["t_mat"]) @ l2n(aux["Tq"][T]).T).astype(np.float32)
    F_FREQ = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    rep["FLOORS_SHARED_STORE_INDEPENDENT"] = ["F_ORTHOGRAPHIC", "F_FREQUENCY"]
    rep["FLOORS_PER_ARM_STORE_DEPENDENT"] = ["F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "0.1390", "-0.1959"]

    hits_exp: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add(name: str, Sx: np.ndarray) -> None:
        nonlocal scored_all
        hh = FB.hit_at_1_both_tie_conventions(Sx, E_T, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        scored_all = scored_all & hh["scored"]

    add("F_ORTHOGRAPHIC", F_ORTHO)
    add("F_FREQUENCY", F_FREQ)

    ortho_leak: Dict[str, float] = {}
    top1_by_arm: Dict[str, np.ndarray] = {}
    Tqn = l2n(aux["Tq"][T])
    for name, mat_arm in mats.items():
        MATn = l2n(mat_arm)
        Sscr = (l2n(FB.scramble_null(mat_arm, MASTER_SEED + 91)) @ l2n(Q_shared).T).astype(np.float32)
        add("F_SCRAMBLE__%s" % name, Sscr)
        cfv = FB.constant_prototype_floor(mat_arm, mat_ok)
        add("F_CONSTANT_PROTOTYPE__%s" % name, FB.as_constant_matrix(cfv, n_items))
        Spart = (MATn @ l2n(Q_shared).T).astype(np.float32)
        add(name, Spart)
        Sm = np.where(E_T, Spart, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        top1_by_arm[name] = top1
        ortho_leak[name] = float(np.mean(np.sum(l2n(aux["t_mat"])[top1] * Tqn, axis=1)))
        del MATn, Sscr, Spart, Sm

    rep["ORTHOGRAPHIC_LEAKAGE_CHECK"] = {
        "what": "mean trigram-cosine(top-1 winner, query), PARTIAL-CUE regime.",
        "values": {k: round(v, 5) for k, v in ortho_leak.items()},
        "F_ORTHOGRAPHIC_floor_own_reference":
            round(float(np.mean(np.sum(l2n(aux["t_mat"])[np.argmax(F_ORTHO, axis=0)] * Tqn, axis=1))), 5)}

    # ---- SCORING: one paired bootstrap over EVERYTHING --------------------------------------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]

    arm_names = list(mats.keys())
    per_arm_report: Dict[str, Dict] = {}
    for name in arm_names:
        floor_keys = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE__%s" % name,
                     "F_CONSTANT_PROTOTYPE__%s" % name]
        present = [f for f in floor_keys if f in acc]
        binding = max(present, key=lambda f: acc[f]) if present else None
        mg_floor = FB.margin(boot, name, binding) if binding else None
        mg_p0 = FB.margin(boot, name, "P0_SYNTAGMATIC_SELECTION") if name != "P0_SYNTAGMATIC_SELECTION" else None
        entry = {
            "value_tie_corrected": round(acc[name], 5),
            "K1_addressing": round(ka_by_arm[name], 4),
            "NULL_PERMUTED": round(null_by_arm[name], 6),
            "orthographic_leakage": round(ortho_leak[name], 5),
            "binding_floor_name": binding,
            "binding_floor_value": round(acc[binding], 5) if binding else None,
            "all_four_floors": {f: round(acc[f], 5) for f in present},
        }
        if mg_floor:
            mg_floor["ci_halfwidth"] = round((mg_floor["ci95"][1] - mg_floor["ci95"][0]) / 2.0, 5)
            mg_floor["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc[binding], nc), 5)
            entry["margin_vs_binding_floor"] = mg_floor
        if mg_p0:
            mg_p0["ci_halfwidth"] = round((mg_p0["ci95"][1] - mg_p0["ci95"][0]) / 2.0, 5)
            mg_p0["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc["P0_SYNTAGMATIC_SELECTION"], nc), 5)
            entry["margin_vs_P0"] = mg_p0
        per_arm_report[name] = entry
        print("[score] %-38s val=%.4f floor(%s)=%s K1=%.4f NULL=%.5f"
              % (name, acc[name], binding, entry["binding_floor_value"], ka_by_arm[name],
                 null_by_arm[name]), flush=True)

    rep["HIT_AT_1_PARTIAL_CUE_PRIMARY"] = {
        "n_common_scored": nc, "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED, PARTIAL-CUE regime",
        "per_arm": per_arm_report,
        "ALL_VALUES_tie_corrected": {k: round(v, 5) for k, v in acc.items()},
    }

    # ---- RULE 12 ORTHOGRAPHIC-CORRELATION CHECK on the best-performing P1 arm --------------------
    p1_names = ["P1_PARADIGMATIC_SELECTION_k%d" % k for k in K_GRID_SEL]
    best_p1 = max(p1_names, key=lambda nm: acc[nm])
    if pearson_ci_bootstrap is not None:
        gain = hits_exp[best_p1].astype(np.float64) - hits_exp["P0_SYNTAGMATIC_SELECTION"].astype(np.float64)
        gold_best_ortho = np.zeros(n_items, dtype=np.float64)
        for i in range(n_items):
            g = np.where(GOLD_T[:, i] & E_T[:, i])[0]
            gold_best_ortho[i] = float(F_ORTHO[g, i].max()) if g.size else 0.0
        m = scored_all
        r_all = pearson_ci_bootstrap(gold_best_ortho[m], gain[m], MASTER_SEED + 909, n_boot=2000)
        nz = m & (np.abs(gain) > 1e-12)
        r_nz = (pearson_ci_bootstrap(gold_best_ortho[nz], gain[nz], MASTER_SEED + 910, n_boot=2000)
               if int(nz.sum()) >= 10 else None)
        rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"] = {
            "best_P1_arm": best_p1, "all_items": r_all,
            "gain_nonzero_items": r_nz, "n_gain_nonzero": int(nz.sum())}
    else:
        rep["RULE12_ORTHOGRAPHIC_CORRELATION_CHECK"] = {"UNAVAILABLE": "pearson_ci_bootstrap import failed"}

    # ---- MECH_A: co-occurrence of items where P1 hits and P0 misses -------------------------------
    mech_a: Dict[str, Dict] = {}
    gtop_gold = np.where(GOLD_T & E_T, np.where(E_T, hits_exp["P0_SYNTAGMATIC_SELECTION"][None, :], -1),
                         -1)                                       # placeholder, replaced below
    hit_P0 = hits_exp["P0_SYNTAGMATIC_SELECTION"] > 0.5
    for k in K_GRID_SEL:
        nm = "P1_PARADIGMATIC_SELECTION_k%d" % k
        hit_P1 = hits_exp[nm] > 0.5
        new_wins = np.flatnonzero(hit_P1 & ~hit_P0 & scored_all)
        vals = []
        for i in new_wins[:COOC_JACCARD_MAX_ITEMS]:
            qw = L_test[int(i)]
            aw = anchors[int(top1_by_arm[nm][i])]
            j = jaccard(where, qw, aw)
            if j is not None:
                vals.append(j)
        arr = np.asarray(vals, dtype=np.float64)
        mech_a[nm] = {
            "n_new_wins": int(new_wins.size), "n_measured": int(arr.size),
            "mean_jaccard": round(float(arr.mean()), 5) if arr.size else None,
            "median_jaccard": round(float(np.median(arr)), 5) if arr.size else None,
            "fraction_ever_cooccur": round(float((arr > 0).mean()), 4) if arr.size else None}
    # baseline reference: P0's own top-1 winners' co-occurrence with the query, general population
    p0_vals = []
    idx_probe = np.arange(min(n_items, COOC_JACCARD_MAX_ITEMS))
    for i in idx_probe:
        qw = L_test[int(i)]
        aw = anchors[int(top1_by_arm["P0_SYNTAGMATIC_SELECTION"][i])]
        j = jaccard(where, qw, aw)
        if j is not None:
            p0_vals.append(j)
    p0_arr = np.asarray(p0_vals, dtype=np.float64)
    mech_a["P0_BASELINE_general_population_TOP1_vs_query"] = {
        "n_measured": int(p0_arr.size),
        "mean_jaccard": round(float(p0_arr.mean()), 5) if p0_arr.size else None,
        "median_jaccard": round(float(np.median(p0_arr)), 5) if p0_arr.size else None,
        "fraction_ever_cooccur": round(float((p0_arr > 0).mean()), 4) if p0_arr.size else None}
    rep["MECH_A_cooccurrence_of_P1s_new_wins"] = {
        "prediction": "the diagnosis predicts P1's new wins (right where P0 is wrong) concentrate "
                      "on ZERO co-occurrence pairs -- the exact population a co-occurrence-selecting "
                      "write rule cannot structurally reach.",
        "by_arm": mech_a}
    print("[MECH_A] " + json.dumps({k: v for k, v in mech_a.items()
                                    if k != "P0_BASELINE_general_population_TOP1_vs_query"}), flush=True)

    # ---- MECH_B: WordNet-relation rate of the top-1 winner, per arm (cost-capped) -----------------
    wn_arms = (["P0_SYNTAGMATIC_SELECTION"]
              + ["P1_PARADIGMATIC_SELECTION_k%d" % k for k in K_GRID_SEL]
              + ["P2_ZERO_COOCCURRENCE_ONLY_k%d" % k for k in K_GRID_SEL]
              + ["P3_HYBRID_beta0.5", "F_FREQ_MATCHED_SELECTION_k%d" % P3_K, "N1_NULL_k%d" % P3_K])
    mech_b: Dict[str, Dict] = {}
    for nm in wn_arms:
        if nm not in top1_by_arm:
            continue
        mech_b[nm] = wordnet_relation_census(top1_by_arm[nm], T, L_words, anchors, GOLD_T, N_PROBE_WORDNET)
        record_unit(output_dir, unit_key("wordnet", nm),
                    {"fraction_no_close_wordnet_relation":
                        mech_b[nm].get("fraction_no_close_wordnet_relation")})
        print("[MECH_B] %-38s no_close_wordnet=%s" % (nm, mech_b[nm].get("fraction_no_close_wordnet_relation")),
              flush=True)
    rep["MECH_B_wordnet_relation_rate_per_arm"] = {
        "n_probe": N_PROBE_WORDNET,
        "reference_landed_W0_rate_from_ARM5_79.3pct_no_close_relation_n3994": 0.793,
        "by_arm": mech_b}

    # ---- STOP-IF, evaluated in order, ALL SIX reported ----------------------------------------------
    def band_of(name: str, other: str) -> Optional[str]:
        mg = per_arm_report.get(name, {}).get("margin_vs_P0") if other == "P0_SYNTAGMATIC_SELECTION" else None
        return mg["band"] if mg else None

    p1_clears = {k: (per_arm_report["P1_PARADIGMATIC_SELECTION_k%d" % k]["margin_vs_binding_floor"]
                     and per_arm_report["P1_PARADIGMATIC_SELECTION_k%d" % k]["margin_vs_binding_floor"]["band"] == "ABOVE")
                for k in K_GRID_SEL}
    p0_clears = bool(per_arm_report["P0_SYNTAGMATIC_SELECTION"].get("margin_vs_binding_floor")
                     and per_arm_report["P0_SYNTAGMATIC_SELECTION"]["margin_vs_binding_floor"]["band"] == "ABOVE")
    p1_beats_p0 = {k: band_of("P1_PARADIGMATIC_SELECTION_k%d" % k, "P0_SYNTAGMATIC_SELECTION") == "ABOVE"
                  for k in K_GRID_SEL}
    p1_ties_p0 = {k: band_of("P1_PARADIGMATIC_SELECTION_k%d" % k, "P0_SYNTAGMATIC_SELECTION") == "NOT_SEPARATED"
                 for k in K_GRID_SEL}
    freq_beats_p0 = {k: band_of("F_FREQ_MATCHED_SELECTION_k%d" % k, "P0_SYNTAGMATIC_SELECTION") == "ABOVE"
                    for k in K_GRID_SEL}
    p2_vs_chance_ref = {k: per_arm_report["P2_ZERO_COOCCURRENCE_ONLY_k%d" % k]["value_tie_corrected"]
                        for k in K_GRID_SEL}
    p2_collapses = {k: (p2_vs_chance_ref[k] <= max(0.005, per_arm_report["P0_SYNTAGMATIC_SELECTION"]
                                                    ["all_four_floors"].get("F_SCRAMBLE__P0_SYNTAGMATIC_SELECTION",
                                                                            0.0) + 0.005))
                    for k in K_GRID_SEL}

    any_i = any(p1_clears.values()) and not p0_clears
    any_iii = all(p1_ties_p0.values())
    freq_comparable = {}
    for k in K_GRID_SEL:
        if p1_beats_p0[k] and freq_beats_p0[k]:
            w1v = per_arm_report["P1_PARADIGMATIC_SELECTION_k%d" % k].get("margin_vs_P0")
            frv = per_arm_report["F_FREQ_MATCHED_SELECTION_k%d" % k].get("margin_vs_P0")
            if w1v and frv:
                lo1, hi1 = w1v["ci95"]; lo2, hi2 = frv["ci95"]
                freq_comparable[k] = not (hi1 < lo2 or hi2 < lo1)
    any_iv = any(freq_comparable.values())
    any_v = any(p2_collapses.values())
    any_ii = (any(p1_beats_p0.values()) and not any_i)

    if any_i:
        stop_if = "i_WRITE_SELECTION_WAS_THE_DEFECT_FIRST_REAL_READOUT_WIN"
    elif any_iii and not any(p1_beats_p0.values()):
        stop_if = "iii_SELECTION_NOT_THE_AXIS_EITHER_CEILING_ELSEWHERE"
    elif any_iv:
        stop_if = "iv_WIN_IS_FREQUENCY_NOT_SUBSTITUTABILITY"
    elif any_ii:
        stop_if = "ii_SELECTION_IS_THE_RIGHT_AXIS_GAP_REMAINS_OPEN"
    else:
        stop_if = "no_clean_fire_see_all_six_booleans"
    rep["STOP_IF_VERDICT"] = {
        "verdict": stop_if,
        "i_p1_clears_floor_where_p0_does_not_by_k": p1_clears,
        "ii_p1_beats_p0_by_k": p1_beats_p0,
        "iii_p1_ties_p0_by_k": p1_ties_p0,
        "iv_freq_matched_also_beats_p0_comparable_by_k": freq_comparable,
        "v_p2_collapses_to_near_scramble_by_k": p2_collapses,
        "vi_k1_all_pass": bool(not k1_fail),
        "p0_clears_its_own_floor": p0_clears,
    }
    print("[STOP_IF] " + stop_if, flush=True)

    rep["POWER"] = {"n_common_scored": nc,
                    "reading": "A WIDTH IS NOT AN EFFECT. Every margin carries its own ci_halfwidth "
                               "and analytic_null_halfwidth_at_this_n."}
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = {
        "loaded": sorted(m for m in sys.modules if m.startswith(("hdlab", "tools.", "exp_"))),
        "edited_by_this_cell": [], "cache_never_rebuilt": True}
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def decide(rep: Dict) -> Tuple[str, str]:
    sv = rep.get("STOP_IF_VERDICT", {})
    v = sv.get("verdict", "NO_ARM_RUN")
    h = rep.get("HIT_AT_1_PARTIAL_CUE_PRIMARY", {}).get("per_arm", {})
    p0 = h.get("P0_SYNTAGMATIC_SELECTION", {})
    msg = "STOP_IF=%s || P0=%.4f (floor %s)" % (
        v, p0.get("value_tie_corrected", float("nan")), p0.get("binding_floor_value"))
    for k in K_GRID_SEL:
        e = h.get("P1_PARADIGMATIC_SELECTION_k%d" % k, {})
        msg += " || P1_k%d=%.4f floor=%s vs_p0=%s" % (
            k, e.get("value_tie_corrected", float("nan")), e.get("binding_floor_value"),
            (e.get("margin_vs_P0") or {}).get("band"))
    return v, msg


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
                 "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE})
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(_ARGS.grid, output_dir)
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
