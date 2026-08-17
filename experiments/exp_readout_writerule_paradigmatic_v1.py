"""exp_readout_writerule_paradigmatic_v1 -- DOES THE WRITE RULE, NOT THE COMPARATOR, CAP READ-OUT?

FINDINGS LOG: notes/readout_ceiling_findings_2026-08-17.md
PRE-REG / DIAGNOSIS THIS ACTS ON: notes/COMPACTION_HANDOFF_2026-08-17.md sec 8b(A);
notes/cue_information_audit_v1_findings_2026-08-17.md.

THE DIAGNOSIS, ALREADY MEASURED, NOT IN QUESTION HERE. Our store's write rule is
`self._sums[lemma] += ctx_vec` (hdlab.reading_grounding_loop.ConceptSpace.observe), where ctx_vec
sums IDENTITY vectors of the words physically near the target in a sentence
(context_vector_masked -> context_vector: one hashlib-seeded bipolar draw per SURFACE TOKEN,
summed). That is a FIRST-ORDER CO-OCCURRENCE (syntagmatic, "appears near") statistic by
construction. The task scores SUBSTITUTABILITY (paradigmatic, "could replace"): for most items the
correct WordNet answer's median co-occurrence with the query is EXACTLY ZERO (C2, measured, n=3994,
notes/readout_ceiling_findings_2026-08-17.md ARM 5). 39 read-out (COMPARATOR) arms across two prior
cells all failed because every one of them changed HOW WE READ a first-order store; none changed
WHAT RELATION GETS WRITTEN. This cell changes the write rule instead. THIS IS THE 40TH ARM'S SIBLING
QUESTION, NOT A 40TH COMPARATOR ARM: nothing here re-ranks scores from an unmodified store.

EXACTLY HOW THIS DIFFERS FROM exp_readout_second_order_v1 (read first; it already ran).
That cell (ARM 5, C3) took the EXISTING first-order store `mat` (anchors x anchors' raw
context-identity sums, unmodified) and replaced the COMPARATOR: instead of cos(query, anchor) it
scored cos(profile(query), profile(anchor)) where profile(x) = row x of the first-order
anchor-anchor cosine matrix P = MATn @ MATn.T. That is second-order structure applied AT READ TIME,
downstream of an unmodified first-order WRITE. It lost (best +0.0055 NOT_SEPARATED at k=0/untruncated,
worse at every truncation k<250) and the log's own reading is that "a second-order READ of a
first-order store cannot manufacture a distinction the WRITE never encoded."

THIS CELL applies second-order structure AT WRITE TIME instead. A NEW store is built: for a target
lemma L's each profile-sentence occurrence, every context TOKEN w in the window contributes -- not
its own hashlib identity draw (first-order) -- but the PROFILE VECTOR of w's lemma, i.e. w's own row
in the EXISTING first-order store (reused verbatim from data cache, never rebuilt: mat0). Two words
that never co-occur but are surrounded by the SAME (or similarly-profiled) neighbours now draw
correlated contributions into their own accumulated sums -- the classic second-order distributional
construction (Schutze 1998), applied at the point where the store is WRITTEN, not read. A context
token whose lemma never reached anchor status (no profile exists) falls back to its own first-order
identity draw, under the IDENTICAL rule in every arm that uses a fallback, so no arm gets a bigger
vocabulary than another by construction.

ARMS, one variable at a time (WHAT gets summed into a word's code), identical corpus / buckets /
profile-sentence selection / held-out cue sentence / pool / gold / scorer as the incumbent:
  W0_SYNTAGMATIC        the incumbent. REUSED VERBATIM from data/exp_cue_to_store_translation_v1's
                        cache (scratch/sparse_code_real_task/real_cache.npz) -- never rebuilt.
  W1_PARADIGMATIC       the second-order write: context contribution = neighbour's OWN first-order
                        profile row (L2-unit), reused/mat0-derived, fallback = identity for
                        non-anchor tokens.
  W2_HYBRID_alpha{.25,.5,.75}  per-token contribution = (1-a)*identity + a*profile. a SWEPT, never
                        adopted as a value.
  N1_NULL               context contribution = a FIXED, DERANGED-RANDOM OTHER anchor's profile row
                        (same set of profile vectors, same magnitude/shape distribution as W1 --
                        "size-matched" -- but the token-to-profile correspondence is destroyed).
                        Catches "any second-order smoothing helps" regardless of content.
  F_FREQ_MATCHED_PROFILE  same construction as N1 but the derangement is done WITHIN corpus-frequency
                        DECILES, so the assigned profile is frequency-matched to the true neighbour
                        even though its IDENTITY is wrong. Catches "the win is really a frequency
                        effect wearing a second-order costume" (second-order profiles are dominated
                        by high-frequency contexts).
  K1_KNOWN_ANSWER        exact-key addressing (query = an arm's own stored row) for EVERY arm. Must
                        pass >=0.95 for ALL arms or the run stops before any treatment number.

PRIMARY REGIME: the PARTIAL CUE (a held-out sentence's context vector, built with the SAME per-arm
write transformation as that arm's store) -- this is the operational regime the dispatch asks about.
EXACT-KEY (an item's own stored row) is reported as a secondary diagnostic and as the K1 validity
gate, exactly mirroring the sibling cells' split of addressing (KA) from WordNet-gold quality.

BRAIN FRAMING, stated per choice, honestly.
  PINNED-BY-EVIDENCE, as a COMPUTATION not a parameter: cortical semantic representation is organised
  by similarity of EXPERIENCE (regularities across episodes) rather than by raw temporal/spatial
  adjacency within one episode; complementary-learning-systems theory has neocortex extracting
  cross-episode regularities while hippocampus retains the single episode (McClelland, McNaughton &
  O'Reilly 1995). Adjacency-in-a-sentence is an episodic fact; a word's stable profile of contexts
  it recurs in across many episodes is closer to the cross-episode regularity CLS assigns to cortex.
  That is the licence for testing a write rule built from PROFILES rather than raw tokens.
  OURS, INVENTION UNDER TEST, NOT LAUNDERED AS BIOLOGY: nothing in the cited literature specifies
  "sum neighbour first-order profile rows into a bipolar HD vector" as the mechanism -- no anatomical
  structure is claimed to compute second-order co-occurrence. The specific write-time construction,
  the L2-unit-norm balancing between identity and profile contributions, the fallback rule for
  non-anchor tokens, and the hybrid mixing weight are all OURS and are reported as such.
  VSA algebraic binding is UNPINNED in the brain (three live accounts, published objections to each);
  nothing here depends on it and nothing here tests it -- this cell only changes what scalar/vector
  quantity gets bundled, not the bundling operator itself (bipolar sum, unmodified).

STOP-IF (read in this order, first one that fires is the answer; report ALL FOUR regardless):
  (i)   W1 clears max(4 floors) CI-separated where W0 does not -> the write rule was the defect.
  (ii)  W1 ties W0 (NOT_SEPARATED, both directions) -> the relation is not the limiter here.
  (iii) W1 beats W0 but F_FREQ_MATCHED_PROFILE ALSO beats W0 by a comparable, CI-overlapping margin
        -> the win is frequency wearing a costume; do not claim the mechanism.
  (iv)  Any arm's K1 (KA_SELF_ADDRESS) < 0.95 -> INSTRUMENT_STILL_LOOSE, SystemExit BEFORE any
        treatment number is computed. Publish nothing quality-bearing.

FLOOR: max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE), ALL FOUR recomputed on
THIS population. F_ORTHOGRAPHIC and F_FREQUENCY are store-independent (spelling / corpus count) and
computed ONCE, shared across arms. F_SCRAMBLE and F_CONSTANT_PROTOTYPE are store-DEPENDENT and
recomputed on EACH ARM'S OWN store, never borrowed from another arm or another population.
0.1382 / 0.2070 / 0.1390 / -0.1959 are NEVER imported. tools/floor_battery.py is imported, not
reimplemented. Both tie conventions published. CI half-width and analytic null p95 beside every
margin (a width is not an effect).

ORTHOGRAPHIC-LEAKAGE CHECK (standing rule 12: a floor is cleared by understanding, never adopted).
If W1 clears a floor, its winners' mean orthographic (trigram) similarity to the query is reported
beside W0's and F_ORTHOGRAPHIC's own, using the SAME aux trigram vectors every sibling cell uses
(tools/floor_battery / aux_v2.npz, never rebuilt). A second-order write that happened to encode
spelling similarity (e.g. via shared short function-word neighbours) would show up here and would be
reported as a failure dressed as a win, not as a clearing.

ORGAN REUSE, enumerated then reconciled by RUNTIME witness, never grep. IMPORTED, NEVER EDITED:
tools/floor_battery, experiments/exp_cue_to_store_translation_v1 (cache loader, ruler gate, landed
regression constant), experiments/exp_readout_ceiling_diagnosis_v1 (population builder, tripwire),
experiments/exp_grounding_readout_known_answer_v1 (build_corpus, build_buckets, _n_profile -- the
IDENTICAL deterministic corpus/bucket construction the cached store was built from; VERIFIED before
this cell was written that re-running it reproduces the cached anchor set exactly, 5491/5491, and
reproduces C["Q_part"] to cosine > 0.999 on a 200-item spot check with 0 mismatches), hdlab's
ConceptSpace-adjacent primitives (content_words, normalize_lemma, symbol_vector, CTX_D) imported
directly rather than reimplemented, tools/exp_checkpoint.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. THE invariant. ASCII-only. CPU. No network.
The INCUMBENT store (W0) is never rebuilt or edited; every NEW store this cell builds is a fresh
in-memory array under data/exp_readout_writerule_paradigmatic_v1/, never written into
scratch/sparse_code_real_task/real_cache.npz. data/foundation/** is never opened.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import (numpy sizes its pools at import time).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
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

import exp_cue_to_store_translation_v1 as CTS               # cache loader + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as DIAG              # population + tripwire, NEVER EDITED
import exp_grounding_readout_known_answer_v1 as GRK          # corpus/buckets, NEVER EDITED
from hdlab.reading_grounding_loop import (                   # NEVER EDITED
    CTX_D, content_words, normalize_lemma, symbol_vector,
)
from tools import floor_battery as FB                        # NEVER EDITED
from tools.exp_checkpoint import record_unit, unit_key

ANCHOR_NAME = "exp_readout_writerule_paradigmatic_v1"
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
HYBRID_ALPHAS = (0.25, 0.5, 0.75)
N_DECILES = 10


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


def l2n_rows64(A: np.ndarray) -> np.ndarray:
    A = np.asarray(A, dtype=np.float64)
    n = np.linalg.norm(A, axis=1, keepdims=True)
    n[n < 1e-12] = 1.0
    return A / n


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else v


def deranged_permutation(n: int, seed: int, groups: Optional[np.ndarray] = None) -> np.ndarray:
    """A permutation of range(n) with NO fixed points, optionally restricted WITHIN each group
    (groups[i] = group id of item i, e.g. a frequency decile). If a group has size 1 the item maps
    to itself (unavoidable) and is flagged in the return via -1 sentinel handling by the caller;
    such items are rare (only whichever decile boundary lands on a singleton) and are reported.
    """
    rng = np.random.default_rng(seed)
    perm = np.arange(n)
    if groups is None:
        groups = np.zeros(n, dtype=np.int64)
    for g in np.unique(groups):
        idx = np.flatnonzero(groups == g)
        if idx.size <= 1:
            continue
        p = rng.permutation(idx)
        tries = 0
        while np.any(p == idx) and tries < 50:
            p = rng.permutation(idx)
            tries += 1
        if np.any(p == idx):                                  # extremely unlikely; rotate as fallback
            p = np.roll(idx, 1)
        perm[idx] = p
    return perm


# =================================================================================================
# THE WRITE RULE. One function, one variable (`mode`), reused for BOTH the store build (accumulate
# over a lemma's profile sentences) and the held-out cue build (a single sentence, no accumulation).
# =================================================================================================
def occurrence_vector(words: Sequence[str], target_lemma: str, pos: Dict[str, int],
                      mat0n: np.ndarray, d: int, mode: str, alpha: float = 0.0,
                      perm: Optional[np.ndarray] = None) -> np.ndarray:
    """Sum, over every context TOKEN w in `words` whose LEMMA != target_lemma (the no-leak mask,
    identical convention to hdlab.reading_grounding_loop.context_vector_masked), of a per-token
    contribution selected by `mode`:
      IDENTITY  -- w's own hashlib symbol vector, L2-unit (the INCUMBENT unit).
      PROFILE   -- the L2-unit first-order profile row of w's LEMMA (mat0n), if w's lemma is an
                  anchor; else falls back to IDENTITY (documented, not silent -- see module
                  docstring: the SAME fallback rule applies to every mode that uses PROFILE, so no
                  arm gets a larger effective vocabulary than another by construction).
      PROFILE_PERM -- as PROFILE, but the profile is read through `perm` (a size- and
                  shape-preserving DERANGEMENT of anchor rows): same set of vectors, wrong identity
                  correspondence. Used for N1_NULL and F_FREQ_MATCHED_PROFILE (only `perm` differs).
      HYBRID    -- (1-alpha)*IDENTITY + alpha*PROFILE, per token, alpha swept by the caller.
    Every per-token contribution is normalised to unit L2 norm BEFORE being combined, so no arm's
    per-token weighting is dominated by an incidental magnitude difference between an identity draw
    (norm sqrt(d) before normalising) and a profile row (norm = sum of many occurrences before
    normalising) -- this is an explicit, disclosed OURS choice, not a brain-pinned one.
    """
    acc = np.zeros(d, dtype=np.float64)
    for w in words:
        lm = normalize_lemma(w)
        if lm == target_lemma:
            continue
        ident = None
        if mode in ("IDENTITY", "HYBRID"):
            ident = _unit(symbol_vector(w, d))
        if mode == "IDENTITY":
            acc += ident
            continue
        idx = pos.get(lm)
        if idx is None:
            prof = _unit(symbol_vector(w, d))                 # fallback = identity, SAME rule always
        else:
            ridx = int(perm[idx]) if (mode == "PROFILE_PERM" and perm is not None) else idx
            prof = mat0n[ridx]
        if mode == "HYBRID":
            acc += (1.0 - alpha) * ident + alpha * prof
        else:
            acc += prof
    return acc


def build_arm(anchors: List[str], buckets: Dict[str, List[int]], cw_cache: Dict[int, List[str]],
             sents: List[str], mat0n: np.ndarray, pos: Dict[str, int], d: int, mode: str,
             alpha: float = 0.0, perm: Optional[np.ndarray] = None,
             heldout_of: Optional[Dict[str, Optional[int]]] = None) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Returns (mat_arm [n_anchors, d] raw accumulated store, {L: partial-cue vector or None}).
    `heldout_of` maps lemma -> its held-out eval sentence index (or None); if not supplied it is
    derived here with the IDENTICAL rule the cached store was built with (verified byte-for-byte
    against the cache before this cell was written -- see module docstring)."""
    def cw(i: int) -> List[str]:
        v = cw_cache.get(i)
        if v is None:
            v = content_words(sents[i])
            cw_cache[i] = v
        return v

    n = len(anchors)
    mat_arm = np.zeros((n, d), dtype=np.float64)
    part = {}
    for i, L in enumerate(anchors):
        b = buckets.get(L, [])
        nprof = GRK._n_profile(len(b))
        acc = np.zeros(d, dtype=np.float64)
        for sidx in b[:nprof]:
            acc += occurrence_vector(cw(sidx), L, pos, mat0n, d, mode, alpha, perm)
        mat_arm[i] = acc
        if heldout_of is not None:
            sidx = heldout_of.get(L)
        else:
            ev = b[nprof:]
            sidx = ev[0] if ev else None
        if sidx is None:
            part[L] = None
        else:
            q = occurrence_vector(cw(sidx), L, pos, mat0n, d, mode, alpha, perm)
            part[L] = q if float(np.linalg.norm(q)) > 1e-9 else None
    return mat_arm.astype(np.float32), part


ARM_SPECS: List[Tuple[str, str, float]] = [
    ("W1_PARADIGMATIC", "PROFILE", 0.0),
    ("W2_HYBRID_alpha0.25", "HYBRID", 0.25),
    ("W2_HYBRID_alpha0.5", "HYBRID", 0.5),
    ("W2_HYBRID_alpha0.75", "HYBRID", 0.75),
    ("N1_NULL", "PROFILE_PERM", 0.0),                      # perm supplied at call time (global derangement)
    ("F_FREQ_MATCHED_PROFILE", "PROFILE_PERM", 0.0),       # perm supplied at call time (decile derangement)
]


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    DIAG.install_grounded_similarity_tripwire()
    ev["floor_battery_selftest_ok"] = sorted(FB.self_test().keys())

    d = 128
    # ---- FIXTURE: A and B share NO context tokens AT ALL (first-order identity sums are built from
    # DISJOINT token sets by construction), but A's tokens {c1..ck} and B's tokens {d1..dk} are
    # themselves ANCHORS whose first-order profiles (mat0n) are made highly correlated (a
    # shared-mediator construction, mirroring exp_readout_second_order_v1's T1 fixture, but applied
    # at WRITE time here). d=128 (not the production 256) keeps the accidental-orthogonality noise
    # floor of a handful of summed +-1 draws comfortably below the T1/T2 assertion gap.
    # NOTE: hdlab.reading_grounding_loop.content_words extracts only alphabetic runs of length > 2
    # via regex `[a-z']+` on the LOWERCASED text -- a fixture token like "c0" or single-letter "A"
    # is silently stripped to nothing or filtered by the length gate. Caught by this self-test on
    # its first run (T2 read cos_P=0.0000 because every synthetic token vanished at tokenization);
    # fixed by using letters-only, length>=3, non-stopword tokens throughout, matching the real
    # pipeline's own contract instead of assuming it.
    # SECOND BUG CAUGHT BY THIS SELF-TEST: the first fixture drew BOTH targets' fillers from ONE
    # shared 40-word pool, so cos_I read 0.2414 (not "unrelated") -- real literal token overlap from
    # the shared filler pool, not sampling noise. Fixed by giving each target its OWN disjoint
    # filler pool, so A and B's context-token sets are disjoint by construction, not by chance.
    rng = np.random.default_rng(11)
    k_ctx = 6
    n_extra = 40
    c_words = ["cctx%s" % chr(97 + i) for i in range(k_ctx)]
    d_words = ["ddtx%s" % chr(97 + i) for i in range(k_ctx)]

    def _letters_only(words: List[str]) -> List[str]:
        return [w.translate(str.maketrans("0123456789", "qrstuvwxyz")) for w in words]

    extra_a = _letters_only(["exfilaa%03d" % i for i in range(n_extra)])
    extra_b = _letters_only(["exfilbb%03d" % i for i in range(n_extra)])
    TA, TB = "trgaaa", "trgbbb"
    anchors = [TA, TB] + c_words + d_words + extra_a + extra_b
    pos = {a: i for i, a in enumerate(anchors)}
    n_a = len(anchors)
    # build mat0n directly: c_i and d_i get NEARLY IDENTICAL profile rows (a shared mediator
    # direction + small private noise); A, B, extras get independent random rows.
    base = rng.standard_normal(d)
    mat0 = np.zeros((n_a, d))
    for i in range(k_ctx):
        priv = 0.15 * rng.standard_normal(d)
        mat0[pos[c_words[i]]] = base + priv + 0.05 * rng.standard_normal(d)
        mat0[pos[d_words[i]]] = base + priv + 0.05 * rng.standard_normal(d)
    mat0[pos[TA]] = rng.standard_normal(d)
    mat0[pos[TB]] = rng.standard_normal(d)
    for e in extra_a + extra_b:
        mat0[pos[e]] = rng.standard_normal(d)
    mat0n = l2n_rows64(mat0)
    # sentences: A always co-occurs with c_words + its OWN filler pool; B with d_words + its OWN
    # DISJOINT filler pool. A and B NEVER share a sentence AND never share a context token.
    sents_local = []
    buckets: Dict[str, List[int]] = {TA: [], TB: []}
    for _ in range(30):
        fa = list(rng.choice(extra_a, size=3, replace=False))
        fb = list(rng.choice(extra_b, size=3, replace=False))
        sents_local.append(" ".join([TA] + c_words + fa))
        buckets[TA].append(len(sents_local) - 1)
        sents_local.append(" ".join([TB] + d_words + fb))
        buckets[TB].append(len(sents_local) - 1)
    cw_cache: Dict[int, List[str]] = {}
    # sanity: the fixture tokens must actually survive content_words() or the whole test is vacuous
    _probe = content_words(sents_local[0])
    assert len(_probe) == 1 + k_ctx + 3 and TA in _probe, (
        "fixture tokens do not survive content_words() tokenization: %r" % (_probe,))

    # T1. FIRST-ORDER (mode=IDENTITY) must show A, B as UNRELATED (their token sets are disjoint).
    matI, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0n, pos, d, "IDENTITY")
    cos_I = float(np.dot(l2n(matI[0:1])[0], l2n(matI[1:2])[0]))
    assert abs(cos_I) < 0.15, ("fixture is not first-order-orthogonal (cos=%.4f) -- a second-order "
                               "win on it would prove nothing" % cos_I)

    # T2. SECOND-ORDER (mode=PROFILE) must recover A~B via their shared-profile mediators.
    matP, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0n, pos, d, "PROFILE")
    cos_P = float(np.dot(l2n(matP[0:1])[0], l2n(matP[1:2])[0]))
    assert cos_P > cos_I + 0.5, ("the second-order WRITE does not recover a shared-neighbour "
                                 "relation first-order misses: first=%.4f second=%.4f"
                                 % (cos_I, cos_P))
    ev["T1_T2_second_order_write_recovers_what_first_order_misses"] = {
        "first_order_cos_A_B": round(cos_I, 4), "second_order_cos_A_B": round(cos_P, 4)}

    # T3. PROFILE_PERM (N1) with a DERANGEMENT covering c_words/d_words rows must DESTROY the T2
    # win -- it is a real identity-scrambling control, not accidentally equal to PROFILE.
    perm = deranged_permutation(n_a, seed=3)
    assert np.all(perm != np.arange(n_a)), "derangement has a fixed point"
    matN, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0n, pos, d, "PROFILE_PERM",
                        perm=perm)
    cos_N = float(np.dot(l2n(matN[0:1])[0], l2n(matN[1:2])[0]))
    assert cos_N < cos_P - 0.3, ("N1's derangement did not destroy the second-order win: "
                                 "second=%.4f null=%.4f" % (cos_P, cos_N))
    ev["T3_null_permutation_destroys_the_win"] = {"second_order": round(cos_P, 4),
                                                   "null_permuted": round(cos_N, 4)}

    # T4. HYBRID interpolates monotonically-ish and alpha is a REAL parameter (changes the output).
    vals = {}
    for a in (0.0, 0.25, 0.5, 0.75, 1.0):
        mh, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0n, pos, d, "HYBRID",
                          alpha=a)
        vals[a] = float(np.dot(l2n(mh[0:1])[0], l2n(mh[1:2])[0]))
    assert abs(vals[0.0] - cos_I) < 1e-6, "HYBRID alpha=0 does not equal pure IDENTITY"
    assert abs(vals[1.0] - cos_P) < 1e-6, "HYBRID alpha=1 does not equal pure PROFILE"
    assert len(set(round(v, 6) for v in vals.values())) == len(vals), \
        "hybrid alpha does nothing -- it is not a parameter, it is decoration"
    ev["T4_hybrid_alpha_is_a_real_parameter"] = {str(k): round(v, 4) for k, v in vals.items()}

    # T5. MASKING: removing A's own token from the window is load-bearing. If A's own token were
    # left in (not masked), it would inject an extra identity/profile term absent from a masked
    # build -- assert the masked and "leaky" (unmasked) builds differ.
    words_with_self = [TA] + c_words
    v_masked = occurrence_vector(words_with_self, TA, pos, mat0n, d, "IDENTITY")
    v_leaky = occurrence_vector(words_with_self, "__nonexistent_target__", pos, mat0n, d, "IDENTITY")
    assert not np.allclose(v_masked, v_leaky), "masking has no effect -- the no-leak rule is dead"
    ev["T5_masking_is_load_bearing"] = True

    # T6. FALSIFIABILITY: on a fixture with NO shared-mediator structure (independent random
    # profiles), PROFILE must NOT manufacture a spurious win over IDENTITY for an UNRELATED pair.
    mat0_flat = l2n_rows64(rng.standard_normal((n_a, d)))
    matI2, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0_flat, pos, d, "IDENTITY")
    matP2, _ = build_arm([TA, TB], buckets, cw_cache, sents_local, mat0_flat, pos, d, "PROFILE")
    cI2 = float(np.dot(l2n(matI2[0:1])[0], l2n(matI2[1:2])[0]))
    cP2 = float(np.dot(l2n(matP2[0:1])[0], l2n(matP2[1:2])[0]))
    assert cP2 < cos_I + 0.5, ("PROFILE fires on a fixture with NO mediator structure: flat_first=%.4f "
                               "flat_second=%.4f (should stay near the first-order baseline)"
                               % (cI2, cP2))
    ev["T6_falsifiable_no_spurious_win_without_mediator_structure"] = {
        "flat_first_order": round(cI2, 4), "flat_second_order": round(cP2, 4)}

    # T7. deranged_permutation actually respects group boundaries (frequency-decile use case).
    groups = np.array([0] * 20 + [1] * 20)
    pg = deranged_permutation(40, seed=9, groups=groups)
    assert np.all(groups[pg] == groups), "grouped derangement crosses group boundaries"
    assert np.all(pg != np.arange(40)), "grouped derangement has a fixed point"
    ev["T7_grouped_derangement_respects_groups_and_has_no_fixed_points"] = True

    # T8. THE CORPUS/BUCKET RECONSTRUCTION REPRODUCES THE CACHED STORE'S POPULATION -- verified as
    # a hard assertion here (not just a pre-authoring probe), on a SMALL slice for selftest speed.
    C = CTS.load_cache()
    sents = GRK.build_corpus(RUN_MODE if RUN_MODE == "reduced" else "full")
    if RUN_MODE == "full":
        buckets_full, _counts = GRK.build_buckets(sents)
        b_anchors = sorted(buckets_full)
        assert b_anchors == C["anchors"], (
            "rebuilt buckets do NOT reproduce the cached anchor set -- the write-side pipeline is "
            "no longer reproducible from the cached population; STOP, do not silently proceed "
            "(len rebuilt=%d len cached=%d)" % (len(b_anchors), len(C["anchors"])))
        ev["T8_corpus_reconstruction_matches_cache"] = {"n_anchors_rebuilt": len(b_anchors),
                                                        "n_anchors_cached": len(C["anchors"]),
                                                        "exact_match": True}
    else:
        ev["T8_corpus_reconstruction_matches_cache"] = "SKIPPED in reduced grid (checked in full only)"

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1400], flush=True)
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
    mat0n = l2n_rows64(mat0_raw)
    d = CTX_D
    print("[load] cache n_anchors=%d t=%.0fs" % (n_anchors, time.time() - t0), flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(tripwire),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "DIFFERENCE_FROM_exp_readout_second_order_v1":
            "that cell applied second-order structure AT READ TIME to an unmodified first-order "
            "store (comparator = cos of similarity PROFILES over the existing store). This cell "
            "applies second-order structure AT WRITE TIME: the store itself is rebuilt so a word's "
            "code is a sum of its neighbours' first-order PROFILE rows rather than a sum of "
            "neighbours' IDENTITY draws. The comparator (plain cosine argmax) is unchanged in every "
            "arm here.",
    }

    # ---- W0 REGRESSION GATE -- the incumbent must still reproduce the landed numbers -------------
    Q_exact0, Q_part0 = C["Q_exact"].astype(np.float32), C["Q_part"].astype(np.float32)
    L_words = C["L_words"]
    n_items_all = len(L_words)
    qidx_all = np.array([pos.get(w, -1) for w in L_words], dtype=np.int64)
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

    MAT0n32 = l2n(mat0_raw)
    S0_part_full = (MAT0n32 @ l2n(Q_part0).T).astype(np.float32)
    h0p = FB.hit_at_1_both_tie_conventions(S0_part_full, E_ALL, GOLD_ALL)
    a0_part = float(h0p["hit_exp"][h0p["scored"] & keep_ALL].mean())
    S0_exact_full = (MAT0n32 @ l2n(Q_exact0).T).astype(np.float32)
    h0e = FB.hit_at_1_both_tie_conventions(S0_exact_full, E_ALL, GOLD_ALL)
    a0_exact = float(h0e["hit_exp"][h0e["scored"] & keep_ALL].mean())
    rep["W0_REGRESSION_GATE"] = {
        "partial_cue_FULL_POP": round(a0_part, 4), "expected": CTS.REGRESSION_A0_PARTIAL,
        "exact_key_FULL_POP": round(a0_exact, 4), "expected_exact": 0.0481,
        "PASS": bool(abs(a0_part - CTS.REGRESSION_A0_PARTIAL) <= CTS.REGRESSION_TOL
                     and abs(a0_exact - 0.0481) <= 5e-4)}
    if not rep["W0_REGRESSION_GATE"]["PASS"]:
        raise SystemExit("W0 REGRESSION GATE FAILED -- not the landed instrument: %r"
                         % rep["W0_REGRESSION_GATE"])
    del S0_part_full, h0p, S0_exact_full, h0e
    print("[regression] W0 partial=%.4f exact=%.4f PASS" % (a0_part, a0_exact), flush=True)

    # ---- items scored (same landed OPEN pool every sibling cell uses) ---------------------------
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

    # ---- REBUILD THE CORPUS/BUCKET PIPELINE (deterministic; verified byte-for-byte against the
    #      cache before this cell was authored -- see module docstring) --------------------------
    sents = GRK.build_corpus("full")
    buckets, counts = GRK.build_buckets(sents)
    b_anchors = sorted(buckets)
    if b_anchors != anchors:
        raise SystemExit("CORPUS/BUCKET RECONSTRUCTION NO LONGER MATCHES THE CACHED ANCHOR SET -- "
                         "the write-side pipeline is not reproducible from the cache; STOPPING "
                         "rather than silently building on a divergent population "
                         "(rebuilt=%d cached=%d)" % (len(b_anchors), len(anchors)))
    print("[corpus] n_sentences=%d n_anchors_matches_cache=True t=%.0fs"
          % (len(sents), time.time() - t0), flush=True)
    cw_cache: Dict[int, List[str]] = {}

    # ---- PERMUTATIONS for N1_NULL and F_FREQ_MATCHED_PROFILE, built ONCE -------------------------
    perm_global = deranged_permutation(n_anchors, seed=MASTER_SEED + 501)
    freq = np.array([counts.get(a, 0) for a in anchors], dtype=np.float64)
    deciles = np.floor(np.argsort(np.argsort(freq)) / max(1.0, n_anchors / N_DECILES)).astype(np.int64)
    deciles = np.clip(deciles, 0, N_DECILES - 1)
    perm_freq = deranged_permutation(n_anchors, seed=MASTER_SEED + 502, groups=deciles)
    rep["PERMUTATION_CONTROLS"] = {
        "n1_global_derangement_no_fixed_points": bool(np.all(perm_global != np.arange(n_anchors))),
        "freq_matched_decile_derangement_no_fixed_points":
            bool(np.all(perm_freq != np.arange(n_anchors))),
        "freq_matched_groups_respected": bool(np.all(deciles[perm_freq] == deciles)),
        "n_deciles": N_DECILES}

    # ---- BUILD EVERY NEW ARM'S STORE + PARTIAL-CUE VECTORS ----------------------------------------
    mats: Dict[str, np.ndarray] = {"W0_SYNTAGMATIC": mat0_raw}
    partial_cue: Dict[str, np.ndarray] = {}
    # W0's own partial cue vector, per item, already in cache order (L_words, may repeat lemmas);
    # build a lookup by lemma for uniformity with the other arms (first occurrence wins -- identical
    # lemma across items shares the same stored row/cue by construction of ConceptSpace anyway).
    part0_by_L: Dict[str, Optional[np.ndarray]] = {}
    for i, L in enumerate(L_words):
        if L not in part0_by_L:
            part0_by_L[L] = Q_part0[i]
    partial_cue["W0_SYNTAGMATIC"] = part0_by_L

    for name, mode, alpha in ARM_SPECS:
        t1 = time.time()
        perm = perm_freq if name == "F_FREQ_MATCHED_PROFILE" else (
            perm_global if name == "N1_NULL" else None)
        mat_arm, part_arm = build_arm(anchors, buckets, cw_cache, sents, mat0n, pos, d, mode,
                                      alpha=alpha, perm=perm)
        mats[name] = mat_arm
        partial_cue[name] = part_arm
        n_null_part = sum(1 for v in part_arm.values() if v is None)
        print("[build] %-28s t=%.1fs n_no_heldout_cue=%d" % (name, time.time() - t1, n_null_part),
              flush=True)
        record_unit(output_dir, unit_key("build", name),
                    {"n_no_heldout_cue": n_null_part, "elapsed_s": round(time.time() - t1, 2)})

    # ---- ASSEMBLE PER-ITEM PARTIAL-CUE MATRICES [n_items, d], zero-filled where no held-out cue --
    Qpart_by_arm: Dict[str, np.ndarray] = {}
    for name in mats:
        src = partial_cue[name]
        Q = np.zeros((n_items, d), dtype=np.float32)
        for j, L in enumerate(L_test):
            v = src.get(L)
            if v is not None:
                Q[j] = v.astype(np.float32)
        Qpart_by_arm[name] = Q

    # ---- K1_KNOWN_ANSWER (exact-key self-addressing), EVERY ARM, GATED BEFORE ANY TREATMENT NUMBER
    ka_by_arm: Dict[str, float] = {}
    for name, mat_arm in mats.items():
        MATn = l2n(mat_arm)
        Sk = (MATn @ MATn[qidx_T[ok_q]].T).astype(np.float32) if ok_q.any() else None
        # KA = argmax over the FULL anchor set of query=own-row equals the item's own anchor index
        Sfull = (MATn @ MATn.T).astype(np.float32)
        pred = np.argmax(Sfull[:, qidx_T[ok_q]], axis=0)
        ka = float(np.mean(pred == qidx_T[ok_q])) if ok_q.any() else float("nan")
        ka_by_arm[name] = ka
        del Sfull
    rep["K1_KNOWN_ANSWER_addressing"] = {k: round(v, 4) for k, v in ka_by_arm.items()}
    rep["K1_GATE"] = KA_MIN
    k1_fail = {k: v for k, v in ka_by_arm.items() if v < KA_MIN}
    print("[K1] " + json.dumps(rep["K1_KNOWN_ANSWER_addressing"]), flush=True)
    if k1_fail:
        rep["STOP_IF_VERDICT"] = {"verdict": "iv_INSTRUMENT_STILL_LOOSE",
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
        Sp = (MATn @ l2n(Qpart_by_arm[name]).T).astype(np.float32)
        hn = FB.hit_at_1_both_tie_conventions(Sp[:, itperm], E_T, GOLD_T)
        null_by_arm[name] = float(hn["hit_exp"][hn["scored"]].mean())
    rep["NULL_PERMUTED_partial_cue"] = {k: round(v, 6) for k, v in null_by_arm.items()}

    # ---- FLOORS: F_ORTHOGRAPHIC / F_FREQUENCY once (store-independent); F_SCRAMBLE /
    #      F_CONSTANT_PROTOTYPE per arm (store-dependent, recomputed on THAT arm's own store) ------
    F_ORTHO = (l2n(aux["t_mat"]) @ l2n(aux["Tq"][T]).T).astype(np.float32)
    F_FREQ = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)),
                                   n_items)
    rep["FLOORS_SHARED_STORE_INDEPENDENT"] = ["F_ORTHOGRAPHIC", "F_FREQUENCY"]
    rep["FLOORS_PER_ARM_STORE_DEPENDENT"] = ["F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "0.1390", "-0.1959"]

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add(name: str, Sx: np.ndarray) -> None:
        nonlocal scored_all
        hh = FB.hit_at_1_both_tie_conventions(Sx, E_T, GOLD_T)
        hits_exp[name] = hh["hit_exp"]; hits_opt[name] = hh["hit_opt"]; hits_cons[name] = hh["hit_cons"]
        scored_all = scored_all & hh["scored"]

    add("F_ORTHOGRAPHIC", F_ORTHO)
    add("F_FREQUENCY", F_FREQ)

    exact_hit1: Dict[str, float] = {}
    ortho_leak: Dict[str, float] = {}
    Tqn = l2n(aux["Tq"][T])
    for name, mat_arm in mats.items():
        MATn = l2n(mat_arm)
        Sscr = (l2n(FB.scramble_null(mat_arm, MASTER_SEED + 91)) @ l2n(Qpart_by_arm[name]).T
               ).astype(np.float32)
        add("F_SCRAMBLE__%s" % name, Sscr)
        cfv = FB.constant_prototype_floor(mat_arm, mat_ok)
        add("F_CONSTANT_PROTOTYPE__%s" % name, FB.as_constant_matrix(cfv, n_items))
        Spart = (MATn @ l2n(Qpart_by_arm[name]).T).astype(np.float32)
        add(name, Spart)
        # secondary: exact-key hit@1 vs WordNet gold (own row as cue)
        Sexact = (MATn @ MATn[qidx_T[ok_q]].T).astype(np.float32) if ok_q.any() else None
        if Sexact is not None:
            full = np.zeros((n_anchors, n_items), dtype=np.float32)
            full[:, ok_q] = Sexact
            he = FB.hit_at_1_both_tie_conventions(full, E_T, GOLD_T)
            exact_hit1[name] = float(he["hit_exp"][ok_q & he["scored"]].mean())
        # orthographic-leakage diagnostic: mean trigram-cosine of the arm's top-1 winner to the query
        Sm = np.where(E_T, Spart, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        ortho_leak[name] = float(np.mean(np.sum(l2n(aux["t_mat"])[top1] * Tqn, axis=1)))
        del MATn, Sscr, Spart, Sm

    rep["EXACT_KEY_hit_at_1_secondary"] = {k: round(v, 4) for k, v in exact_hit1.items()}
    rep["ORTHOGRAPHIC_LEAKAGE_CHECK"] = {
        "what": "mean trigram-cosine(top-1 winner, query), PARTIAL-CUE regime. If an arm's write "
                "rule secretly encodes spelling similarity, this rises relative to W0 and the "
                "orthographic floor's own value -- a floor cleared this way is a failure, not a win.",
        "values": {k: round(v, 5) for k, v in ortho_leak.items()},
        "F_ORTHOGRAPHIC_floor_own_reference":
            round(float(np.mean(np.sum(l2n(aux["t_mat"])[np.argmax(F_ORTHO, axis=0)] * Tqn, axis=1))),
                  5)}

    # ---- SCORING: one paired bootstrap over EVERYTHING (namespaced floors + arms) ----------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]

    arm_names = ["W0_SYNTAGMATIC"] + [nm for nm, _, _ in ARM_SPECS]
    per_arm_report: Dict[str, Dict] = {}
    for name in arm_names:
        floor_keys = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE__%s" % name,
                     "F_CONSTANT_PROTOTYPE__%s" % name]
        present = [f for f in floor_keys if f in acc]
        binding = max(present, key=lambda f: acc[f]) if present else None
        mg_floor = FB.margin(boot, name, binding) if binding else None
        mg_w0 = FB.margin(boot, name, "W0_SYNTAGMATIC") if name != "W0_SYNTAGMATIC" else None
        entry = {
            "value_tie_corrected": round(acc[name], 5),
            "K1_addressing": round(ka_by_arm[name], 4),
            "NULL_PERMUTED": round(null_by_arm[name], 6),
            "EXACT_KEY_hit_at_1": round(exact_hit1.get(name, float("nan")), 4),
            "orthographic_leakage": round(ortho_leak[name], 5),
            "binding_floor_name": binding,
            "binding_floor_value": round(acc[binding], 5) if binding else None,
            "all_four_floors": {f: round(acc[f], 5) for f in present},
        }
        if mg_floor:
            mg_floor["ci_halfwidth"] = round((mg_floor["ci95"][1] - mg_floor["ci95"][0]) / 2.0, 5)
            mg_floor["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc[binding], nc), 5)
            entry["margin_vs_binding_floor"] = mg_floor
        if mg_w0:
            mg_w0["ci_halfwidth"] = round((mg_w0["ci95"][1] - mg_w0["ci95"][0]) / 2.0, 5)
            mg_w0["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc["W0_SYNTAGMATIC"], nc), 5)
            entry["margin_vs_W0"] = mg_w0
        per_arm_report[name] = entry
        print("[score] %-24s val=%.4f floor(%s)=%s K1=%.4f NULL=%.5f"
              % (name, acc[name], binding, entry["binding_floor_value"], ka_by_arm[name],
                 null_by_arm[name]), flush=True)

    rep["HIT_AT_1_PARTIAL_CUE_PRIMARY"] = {
        "n_common_scored": nc, "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED, PARTIAL-CUE regime",
        "per_arm": per_arm_report,
        "ALL_VALUES_tie_corrected": {k: round(v, 5) for k, v in acc.items()},
    }

    # ---- STOP-IF, evaluated in order, ALL FOUR reported -------------------------------------------
    w1_clears = (per_arm_report["W1_PARADIGMATIC"]["margin_vs_binding_floor"]
                and per_arm_report["W1_PARADIGMATIC"]["margin_vs_binding_floor"]["band"] == "ABOVE")
    w0_floor_entry = per_arm_report["W0_SYNTAGMATIC"]
    w0_clears = (w0_floor_entry["margin_vs_binding_floor"]
                and w0_floor_entry["margin_vs_binding_floor"]["band"] == "ABOVE")
    w1_vs_w0 = per_arm_report["W1_PARADIGMATIC"].get("margin_vs_W0")
    w1_beats_w0 = bool(w1_vs_w0 and w1_vs_w0["band"] == "ABOVE")
    w1_ties_w0 = bool(w1_vs_w0 and w1_vs_w0["band"] == "NOT_SEPARATED")
    freq_vs_w0 = per_arm_report["F_FREQ_MATCHED_PROFILE"].get("margin_vs_W0")
    freq_beats_w0 = bool(freq_vs_w0 and freq_vs_w0["band"] == "ABOVE")
    freq_comparable = False
    if w1_beats_w0 and freq_beats_w0 and w1_vs_w0 and freq_vs_w0:
        # "comparable" = the two margins' CIs overlap (cannot CI-separate the write-rule's lift from
        # the frequency-matched control's lift)
        w1_lo, w1_hi = w1_vs_w0["ci95"]
        fr_lo, fr_hi = freq_vs_w0["ci95"]
        freq_comparable = not (w1_hi < fr_lo or fr_hi < w1_lo)

    if bool(w1_clears) and not bool(w0_clears):
        stop_if = "i_WRITE_RULE_WAS_THE_DEFECT_FIRST_REAL_READOUT_WIN"
    elif w1_ties_w0:
        stop_if = "ii_RELATION_NOT_THE_LIMITER_CEILING_ELSEWHERE"
    elif w1_beats_w0 and freq_beats_w0 and freq_comparable:
        stop_if = "iii_WIN_IS_FREQUENCY_NOT_SUBSTITUTABILITY"
    elif w1_beats_w0:
        stop_if = "w1_beats_w0_but_does_not_clear_a_floor_W0_also_misses"
    else:
        stop_if = "w1_does_not_beat_w0_and_does_not_tie_within_NOT_SEPARATED_band"
    rep["STOP_IF_VERDICT"] = {
        "verdict": stop_if,
        "w1_clears_its_own_binding_floor": bool(w1_clears),
        "w0_clears_its_own_binding_floor": bool(w0_clears),
        "w1_beats_w0_CI_separated": w1_beats_w0,
        "w1_ties_w0_NOT_SEPARATED": w1_ties_w0,
        "freq_matched_also_beats_w0_CI_separated": freq_beats_w0,
        "freq_matched_margin_CI_overlaps_w1_margin": freq_comparable,
    }
    print("[STOP_IF] " + stop_if, flush=True)

    rep["POWER"] = {"n_common_scored": nc,
                    "reading": "A WIDTH IS NOT AN EFFECT. Every margin carries its own ci_halfwidth "
                               "and analytic_null_halfwidth_at_this_n."}
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = {
        "loaded": sorted(m for m in sys.modules if m.startswith(("hdlab", "tools.", "exp_"))),
        "edited_by_this_cell": [],
        "cache_never_rebuilt": True}
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def decide(rep: Dict) -> Tuple[str, str]:
    sv = rep.get("STOP_IF_VERDICT", {})
    v = sv.get("verdict", "NO_ARM_RUN")
    h = rep.get("HIT_AT_1_PARTIAL_CUE_PRIMARY", {}).get("per_arm", {})
    w1 = h.get("W1_PARADIGMATIC", {})
    w0 = h.get("W0_SYNTAGMATIC", {})
    fr = h.get("F_FREQ_MATCHED_PROFILE", {})
    msg = ("STOP_IF=%s || W0=%.4f (floor %s) W1=%.4f (floor %s) FREQ_MATCHED=%.4f || "
          "w1_vs_w0=%s freq_vs_w0=%s" % (
              v, w0.get("value_tie_corrected", float("nan")), w0.get("binding_floor_value"),
              w1.get("value_tie_corrected", float("nan")), w1.get("binding_floor_value"),
              fr.get("value_tie_corrected", float("nan")),
              (w1.get("margin_vs_W0") or {}).get("band"), (fr.get("margin_vs_W0") or {}).get("band")))
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
