"""exp_confidence_calibration_replicate_v1 -- DOES THE READ-OUT KNOW WHEN IT KNOWS? REPLICATE OR KILL.

THE CLAIM UNDER REPLICATION (exp_synonym_substitution_metric_v1, 2026-08-16, section 4B, verbatim):
  "the read-out's top1-minus-top2 margin predicts its own success when NAMING (8 of 8 response rates
   above the random-abstain band, 0.0457 -> 0.0887 at 5% response) and predicts nothing when
   SUBSTITUTING (0 of 8 rates, both criteria)."
That was ONE measurement, ONE signal, produced by a cell built to measure a SUCCESS CRITERION. Its
own author labelled it the least replicated thing in the report. This cell replicates it or kills it.

WHY IT IS WORTH THE COMPUTE EVEN THOUGH OUR ACCURACY IS BELOW THE FLOORS.
BOARD Q12, the owner describing their own word-finding, verbatim:
  "If I can't remember the word, i'll give up basically because it's not worth it - I'll use a word
   that means the same thing instead."
GIVING UP REQUIRES KNOWING YOU HAVE FAILED. A system that knows when it knows is a SEPARATE
capability from a system that is right. THIS CELL MAKES NO ACCURACY CLAIM AND CANNOT CLEAR THE
STANDING BAR: our hit@1 is CI-separated BELOW the spelling floor and this cell does not move it.
Calibration is reported with its OWN floor set and its OWN scope, and NEVER as a capability win.

--------------------------------------------------------------------------------------------------
THE CONFOUND THE SOURCE CELL COULD NOT SEE, AND WHY THIS CELL IS A FACTORIAL
--------------------------------------------------------------------------------------------------
The source compared NAMING against SUBSTITUTING, but those two blocks differ in TWO ways at once:
  (1) THE CRITERION   naming scores {L} only; substituting scores a set of meaning-equivalents.
  (2) THE POOL        naming puts L back in the eligible pool; the landed instrument MASKS L OUT.
With (2) varying, "confidence predicts naming success" may mean nothing more than "a big top1-top2
margin means the argmax is L itself", which is only scorable when L is eligible. That is a statement
about the POOL, not about metacognition. The two must be separated before anything is built.

SIX OPEN-POOL BLOCKS, ONE COMMON ITEM SET, ONE SET OF SCORES. Only the named thing changes.
  A  POOL=SELF   GOLD={L}                  THE SOURCE'S POSITIVE. Name the word.
  B  POOL=SELF   GOLD={L} + synonyms       criterion loosened one rung; SAME scores, SAME pool
  C  POOL=SELF   GOLD={L} + landed closure criterion loosened two rungs; SAME scores, SAME pool
  D  POOL=SELF   GOLD=synonyms ONLY        L is IN the pool but is NOT a correct answer
  E  POOL=MASK   GOLD=synonyms             THE SOURCE'S NULL (tight criterion)
  F  POOL=MASK   GOLD=landed closure       THE SOURCE'S NULL (landed criterion)

  A vs B vs C  isolates THE CRITERION. Identical items, identical eligibility, identical scores and
               therefore an IDENTICAL confidence vector. ONLY the hit label changes. This is the
               single-variable test of the brief's candidate mechanism.
  D vs E       isolates THE POOL. Identical items, identical gold family (synonyms), the only
               difference is whether L is eligible.
  A vs E       is the source's headline comparison, reproduced on ONE COMMON POPULATION rather than
               on the two different populations the source had to use.

--------------------------------------------------------------------------------------------------
MECHANISM HYPOTHESES, STATED BEFORE THE RUN (each makes a different prediction; they can all fail)
--------------------------------------------------------------------------------------------------
H1  MANY-COMPETITORS (the brief's candidate). In naming there is one peak to be confident about; in
    substitution many acceptable answers compete and the top-1 margin stops meaning anything.
    PREDICTS: AUROC falls monotonically A > B > C on identical scores, and an ACCEPTABLE-SET
    confidence recovers selectivity where the top-1 margin does not.
H2  THE POOL, NOT THE CRITERION (this cell's addition). A large margin means "the argmax is L's own
    profile matching L's own context", which is only a HIT while L is eligible.
    PREDICTS: A, B, C all retain selectivity (they all reward argmax==L), D and E and F all lose it.
    DISTINGUISHED FROM H1 because H1 predicts decay ALONG the criterion axis and H2 does not.
H3  FREQUENCY. Confidence tracks common words and common words are answered correctly more often; a
    system confident about common words and right about common words has learned nothing.
    PREDICTS: the frequency-STRATIFIED AUROC collapses to 0.5 while the raw AUROC does not.
H4  CUE FAMILIARITY (the brain's account, see the fidelity block). The feeling of knowing is driven
    by familiarity of the CUE, not by the peakedness of the retrieval output.
    PREDICTS: a cue-familiarity signal selects at least as well as an output-derived one.
A DIRECT DISCRIMINATOR FOR H2 IS ALSO MEASURED: on block B, hit_SUBSTITUTION_ONLY = (a synonym was
returned) AND (the argmax was NOT L). If the margin only ever predicted "the argmax is L", its AUROC
against THAT label sits at or below 0.5.

--------------------------------------------------------------------------------------------------
WHAT THE CONFIDENCE SIGNAL IS, MECHANICALLY. Named exactly, and none of them consults the judge.
--------------------------------------------------------------------------------------------------
Over the ELIGIBLE pool of item i, with s = the arm's own scores (cosine, for the read-out):
  C1_TOP1_ABS        max(s)                              absolute score of the winner
  C2_MARGIN_ABS      max(s) - second(s)                  THE PRIMARY. The source's signal, exactly.
  C3_MARGIN_REL      (max - second) / max(|max|, eps)    scale-free version of C2
  C4_NEG_ENTROPY     -H(softmax(s / T)), T = 0.05        peakedness of the WHOLE distribution
  C5_TOP1_Z          (max - mean(s)) / sd(s)             winner's z-score against its own pool
  C6_SETMARGIN_M10   max(s) - max(s outside the argmax's own top-10 store-neighbourhood)
                     THE ACCEPTABLE-SET CONFIDENCE the brief asks for, built WITHOUT the judge: the
                     "acceptable set" is defined by the SUBSTRATE'S OWN geometry (the argmax's
                     nearest neighbours in the store), never by WordNet. Consulting the gold set at
                     run time would be an oracle and is refused.
  C7_TOPM_COHERENCE  mean pairwise store-cosine among the top-10 scoring anchors
                     "is my top region a coherent meaning cluster, or scattered?"
  C8_CUE_FAMILIARITY cos(query vector, mean anchor direction)
                     THE BRAIN-MOTIVATED ONE. Depends on the CUE alone, not on the retrieval output.
C1..C7 are OUR INVENTION. C8 is motivated by the cue-familiarity account of the feeling of knowing
and is still our operationalisation of it. Nothing here is pinned by a neural measurement.

--------------------------------------------------------------------------------------------------
THE FLOORS FOR A CALIBRATION CLAIM. A random-abstain band is the WEAKEST of them and is not enough.
--------------------------------------------------------------------------------------------------
  X1_RANDOM        decline on a random subset. The band that every curve must exit. WEAKEST FLOOR.
  X2_QUERY_LOGFREQ confidence = log corpus count of the query word. "Confident about common words."
                   THE MANDATORY FREQUENCY CONTROL, run as a standalone competing policy.
  X3_QUERY_LENGTH  confidence = -len(query word). A purely orthographic abstention policy.
  X4_CONSTANT      flat confidence. NEGATIVE CONTROL: must sit inside the band at every rate.
  X5_SCRAMBLED     our own signal, permuted. Second negative control, a different mechanism from X4.
FLOORS ARE GIVEN THEIR BEST ORIENTATION AND WE ARE NOT: X2 and X3 are reported at whichever sign of
the policy is stronger, because a floor should be as strong as it can be. Our signals are reported
at their pre-registered sign only.
AND THE STRONGEST FREQUENCY CONTROL IS NOT A COMPETING ARM AT ALL, IT IS A MATCHED DESIGN:
  FREQUENCY-STRATIFIED AUROC -- concordance computed WITHIN deciles of log corpus count and pooled.
  A signal that is only frequency in disguise scores 0.5 there by construction.

--------------------------------------------------------------------------------------------------
THE CALIBRATION INSTRUMENT NEEDS ITS OWN VALIDITY ARMS, and they are NOT the retrieval ones.
--------------------------------------------------------------------------------------------------
  RETRIEVAL instrument (inherited, imported from exp_task_degeneracy_v1, unmodified):
    KA_QUERY_IS_GOLD_VECTOR   plants the answer  -> near ceiling in every readable block
    NULL_SCRAMBLED_ANCHORS    permutes the map   -> that block's OWN chance
  CALIBRATION instrument (built here, because a KA on retrieval says nothing about calibration):
    KA_CALIB = ORACLE_NOISY_CONFIDENCE   hit + noise. NOT A FLOOR, fitted on the labels. Must beat
               the random band at essentially every rate and reach a high AUROC. If it does not, the
               curve machinery is broken and NO treatment number may be read.
    NULL_CALIB = X4_CONSTANT and X5_SCRAMBLED. Must sit at AUROC 0.5 and beat the band ~never.
  THEY FAIL INDEPENDENTLY: one is built FROM the labels, the other DESTROYS the signal. Self-test S8
  breaks each alone and shows the other unmoved.

--------------------------------------------------------------------------------------------------
PRE-REGISTERED BANDS. Written before the run. PRIMARY = C2_MARGIN_ABS on R0, OPEN pool, PARTIAL_CUE.
--------------------------------------------------------------------------------------------------
  REPLICATES            block A: AUROC CI-separated ABOVE 0.5
                        AND frequency-STRATIFIED AUROC CI-separated ABOVE 0.5
                        AND beats the random-abstain band at >= 8 of 14 response rates
                        AND both split-halves agree in direction
                        AND blocks E and F: AUROC NOT CI-separated above 0.5
                        AND A-minus-E AUROC difference CI-separated ABOVE 0 (paired, one population)
  FAILS_TO_REPLICATE    block A AUROC not CI-separated above 0.5,
                        OR E/F show CI-separated selectivity of comparable size (no dissociation)
  FREQUENCY_EXPLAINED   block A raw AUROC separates but the STRATIFIED AUROC does not
  MECHANISM_IS_THE_POOL blocks B and C retain block A's selectivity (criterion axis flat) while
                        D/E/F lose it -- the effect is eligibility, not the criterion. H2 over H1.
  MECHANISM_IS_THE_SET  AUROC decays A > B > C on identical scores -- H1. Then C6_SETMARGIN is the
                        pre-registered fix and is tested on E and F.
  MIDDLE_BAND           anything else, said plainly rather than picked.
NONE OF THESE OUTCOMES IS A MEETS_BAR CLAIM. hit@1 accuracy is unchanged by this cell.
SECONDARY SIGNALS (C1, C3..C8) FACE 8 signals x 6 blocks = 48 tests; a 95% interval separates by
chance 2-3 times in that many. A secondary claim requires: 99.9% CI separation (reported alongside
the 95%), the same direction in BOTH split-halves, AND survival of frequency stratification.

FRESH SEEDS. MASTER_SEED here is 20260817, NOT the source's 20260816. Every stochastic element --
gold designation, balanced-pool construction, tie-breaking, random-abstain draws, the bootstrap --
is re-drawn, and the primary statistic is recomputed at THREE independent RNG seeds. The OPEN-pool
scores themselves are deterministic given the shared harness cache, so a REGRESSION GATE asserts
this cell reproduces the landed 0.0223 / 0.0481 and the source's 0.0457 naming base exactly; that is
what makes the re-analysis independent rather than a different measurement of a different thing.

POOL LADDER (tools/floor_battery.py, IMPORTED UNMODIFIED): OPEN, balanced K=15 and K=49, and the
spelling-MATCHED pool whose ORACLE constant is RE-READ here and never inherited -- the source cell
measured 0.7262 on it against chance 0.0625 and excluded it, and this cell checks its own.

THE CONSTANT/PROTOTYPE FLOOR IS RECOMPUTED ON THIS POPULATION with its own n under all three tie
conventions. 0.1382 and 0.2070 are floors on OTHER populations and are NOT imported.

NEVER grounded_similarity() as a scorer -- only raw grounded_vector() norms, via the imported landed
channel. RULER MODE gate at exp_task_degeneracy_v1.ruler_mode_gate. Flags are --grid full|reduced so
the token '--smoke' never enters argv. No LLM anywhere in any path. ASCII-only. Nothing under
hdlab/, data/foundation/ or any protected path is written or modified.
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
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402
from tools.floor_battery import (                                               # noqa: E402
    balanced_candidate_sets, constant_prototype_floor, hit_at_1_both_tie_conventions,
    matched_candidate_sets, oracle_constant_scores,
)
# THE ARMS, THE POOL, THE SCORER AND THE CACHE ARE IMPORTED, NOT REBUILT, so the regression gate is
# an IDENTITY check rather than a similarity check.
import experiments.exp_task_degeneracy_v1 as TD                                 # noqa: E402
# THE JUDGE (WordNet synsets, offline, static, read-only) is imported from the source cell so the
# criterion is bit-identical to the one whose result is being replicated.
import experiments.exp_synonym_substitution_metric_v1 as SYN                    # noqa: E402

ANCHOR_NAME = "exp_confidence_calibration_replicate_v1"
OUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)

# ---- FRESH SEEDS. Deliberately NOT the source's 20260816. -----------------------------------
MASTER_SEED = 20260817
RNG_SEEDS = (20260817, 20260818, 20260819)      # the primary statistic is recomputed at all three

RATES = (0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50,
         0.60, 0.70, 0.80, 0.90, 0.95, 1.00)     # 14 points, the FULL curve
N_TIEBREAKS = 20                                 # tie-break sensitivity of the selective accuracy
M_NBR = 10                                       # acceptable-set size for C6 / C7
SOFTMAX_T = 0.05                                 # C4 temperature (OUR INVENTION, reported as such)
N_FREQ_STRATA = 10                               # frequency-matched control: deciles
K_LIST = (15, 49)

FLOORS = ("F1_TRIGRAM_ONLY_orthographic", "F2_PREFIX_ONLY_orthographic",
          "F3_FREQUENCY_ONLY_constant", "F5_CONSTANT_PROTOTYPE_zero_query_information")

SIGNALS = ("C1_TOP1_ABS", "C2_MARGIN_ABS", "C3_MARGIN_REL", "C4_NEG_ENTROPY", "C5_TOP1_Z",
           "C6_SETMARGIN_M%d" % M_NBR, "C7_TOPM_COHERENCE", "C8_CUE_FAMILIARITY")
PRIMARY_SIGNAL = "C2_MARGIN_ABS"
CONF_FLOORS = ("X2_QUERY_LOGFREQ", "X3_QUERY_LENGTH", "X4_CONSTANT", "X5_SCRAMBLED")
CALIB_KA = "KA_CALIB_ORACLE_NOISY_not_a_floor"

# arms whose hit vectors are retained for the calibration analysis
KEEP_ARMS = ("R0_CTX_DENSE_our_read_out",) + FLOORS + ("NULL_SCRAMBLED_ANCHORS",)


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1).encode("utf-8"))
    os.replace(tmp, path)


def _r(x, k=4):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else round(v, k)


# =================================================================================================
# AUROC -- the single pre-registered summary statistic for "does confidence predict success?"
# =================================================================================================
def _auroc_num_den(conf: np.ndarray, h: np.ndarray) -> Tuple[float, float]:
    """EXACT tie-aware weighted concordance, returned as (numerator, denominator) so that strata
    can be pooled.

    h is the TIE-CORRECTED hit and is FRACTIONAL for channels with tie mass, so the ordinary binary
    AUROC does not apply. The generalisation used here is the natural one: item i contributes mass
    h_i to the positive class and (1 - h_i) to the negative class, and
        AUROC = sum_{i != j} h_i (1 - h_j) s(conf_i, conf_j) / sum_{i != j} h_i (1 - h_j),
    with s = 1 / 0.5 / 0 for greater / tied / smaller. Self-pairs are excluded, which is why the
    0.5 * sum h(1-h) correction appears. A signal that ties everything scores EXACTLY 0.5 -- the
    same guard the tie-corrected hit metric applies on the accuracy side.
    """
    conf = np.asarray(conf, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    n = conf.size
    if n < 2:
        return 0.0, 0.0
    neg = 1.0 - h
    corr = float((h * neg).sum())
    den = float(h.sum()) * float(neg.sum()) - corr
    o = np.argsort(conf, kind="stable")
    cs, hs, ns = conf[o], h[o], neg[o]
    cum = np.cumsum(ns)
    ar = np.arange(n)
    diff = cs[1:] != cs[:-1]
    new = np.concatenate([np.ones(1, dtype=bool), diff])
    last = np.concatenate([diff, np.ones(1, dtype=bool)])
    gstart = np.maximum.accumulate(np.where(new, ar, -1))
    gend = np.minimum.accumulate(np.where(last, ar, n)[::-1])[::-1]
    A = np.where(gstart > 0, cum[np.maximum(gstart - 1, 0)], 0.0)
    S = 0.5 * (A + cum[gend])
    num = float((hs * S).sum()) - 0.5 * corr
    return num, den


def _auroc_num_den_batch(confB: np.ndarray, hB: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The same statistic, vectorised over a [B, n] batch of bootstrap resamples."""
    confB = np.asarray(confB, dtype=np.float64)
    hB = np.asarray(hB, dtype=np.float64)
    B, n = confB.shape
    negB = 1.0 - hB
    corr = (hB * negB).sum(axis=1)
    den = hB.sum(axis=1) * negB.sum(axis=1) - corr
    o = np.argsort(confB, axis=1, kind="stable")
    cs = np.take_along_axis(confB, o, 1)
    hs = np.take_along_axis(hB, o, 1)
    ns = np.take_along_axis(negB, o, 1)
    cum = np.cumsum(ns, axis=1)
    ar = np.arange(n)[None, :]
    diff = cs[:, 1:] != cs[:, :-1]
    new = np.concatenate([np.ones((B, 1), dtype=bool), diff], axis=1)
    last = np.concatenate([diff, np.ones((B, 1), dtype=bool)], axis=1)
    gstart = np.maximum.accumulate(np.where(new, ar, -1), axis=1)
    gend = np.minimum.accumulate(np.where(last, ar, n)[:, ::-1], axis=1)[:, ::-1]
    A = np.where(gstart > 0, np.take_along_axis(cum, np.maximum(gstart - 1, 0), 1), 0.0)
    S = 0.5 * (A + np.take_along_axis(cum, gend, 1))
    num = (hs * S).sum(axis=1) - 0.5 * corr
    return num, den


def auroc(conf: np.ndarray, h: np.ndarray) -> float:
    num, den = _auroc_num_den(conf, h)
    return float(num / den) if den > 0 else float("nan")


def auroc_with_ci(conf: np.ndarray, h: np.ndarray, strata: Optional[np.ndarray], n_boot: int,
                  seed: int, batch: int = 400) -> Dict:
    """AUROC plus a bootstrap CI at 95% AND 99.9% (the second is the multiplicity-aware level for
    the 48 secondary signal x block tests). When `strata` is given the statistic is the POOLED
    WITHIN-STRATUM concordance -- the frequency-matched control -- and the bootstrap is stratified,
    which is the resampling scheme that statistic requires."""
    conf = np.asarray(conf, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    ok = np.isfinite(conf) & np.isfinite(h)
    conf, h = conf[ok], h[ok]
    n = conf.size
    if n < 50:
        return {"n": int(n), "insufficient": True}
    if strata is None:
        groups = [np.arange(n)]
    else:
        st = np.asarray(strata)[ok]
        groups = [np.flatnonzero(st == s) for s in np.unique(st)]
        groups = [g for g in groups if g.size >= 10]
    num0 = den0 = 0.0
    for g in groups:
        a, b = _auroc_num_den(conf[g], h[g])
        num0 += a
        den0 += b
    point = float(num0 / den0) if den0 > 0 else float("nan")
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, dtype=np.float64)
    done = 0
    while done < n_boot:
        b = min(batch, n_boot - done)
        num = np.zeros(b, dtype=np.float64)
        den = np.zeros(b, dtype=np.float64)
        for g in groups:
            ng = g.size
            IDX = g[rng.integers(0, ng, size=(b, ng))]
            a2, b2 = _auroc_num_den_batch(conf[IDX], h[IDX])
            num += a2
            den += b2
        draws[done:done + b] = np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)
        done += b
    d = draws[np.isfinite(draws)]
    if d.size < 10:
        return {"n": int(n), "auroc": _r(point), "insufficient_bootstrap": True}
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    lo999, hi999 = float(np.percentile(d, 0.05)), float(np.percentile(d, 99.95))
    # POWER. AN ABSENCE CLAIM NEEDS POWER, AND ON THIS INSTRUMENT SOME BLOCKS HAVE ALMOST NONE.
    # The tight-synonym blocks carry a base accuracy of ~0.002, i.e. about FIVE effective positive
    # items in 2471, and a 95% interval on their AUROC spans more than half the possible range. A
    # "NOT_SEPARATED" there is NOT evidence that the signal is uninformative; it is evidence that
    # the block cannot answer the question. Flagged here so no reader, and no verdict rule, can
    # quietly read no-power as a null.
    npos = float(h.sum())
    width = hi - lo
    return {"n": int(n), "n_strata": len(groups), "auroc": _r(point),
            "ci95": [_r(lo), _r(hi)],
            "band_vs_0.5": "ABOVE" if lo > 0.5 else ("BELOW" if hi < 0.5 else "NOT_SEPARATED"),
            "ci999": [_r(lo999), _r(hi999)],
            "band999_vs_0.5": ("ABOVE" if lo999 > 0.5 else
                               ("BELOW" if hi999 < 0.5 else "NOT_SEPARATED")),
            "n_effective_positives": _r(npos, 2), "ci95_width": _r(width),
            "UNDERPOWERED": bool(npos < 20.0 or width > 0.25),
            "power_note": ("a NOT_SEPARATED result in an UNDERPOWERED block is NO MEASUREMENT, "
                           "not a null." if (npos < 20.0 or width > 0.25) else "adequately powered")}


def paired_auroc_delta(conf_a, h_a, conf_b, h_b, n_boot: int, seed: int,
                       batch: int = 400) -> Dict:
    """AUROC(A) - AUROC(B) on ONE COMMON ITEM SET with the SAME resample indices, so the difference
    is genuinely paired. Both inputs must be aligned to the same item ordering; the caller
    guarantees that by building every block on the same common population."""
    conf_a = np.asarray(conf_a, np.float64); h_a = np.asarray(h_a, np.float64)
    conf_b = np.asarray(conf_b, np.float64); h_b = np.asarray(h_b, np.float64)
    ok = (np.isfinite(conf_a) & np.isfinite(h_a) & np.isfinite(conf_b) & np.isfinite(h_b))
    conf_a, h_a, conf_b, h_b = conf_a[ok], h_a[ok], conf_b[ok], h_b[ok]
    n = conf_a.size
    if n < 50:
        return {"n": int(n), "insufficient": True}
    pa, pb = auroc(conf_a, h_a), auroc(conf_b, h_b)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, dtype=np.float64)
    done = 0
    while done < n_boot:
        b = min(batch, n_boot - done)
        IDX = rng.integers(0, n, size=(b, n))
        na, da = _auroc_num_den_batch(conf_a[IDX], h_a[IDX])
        nb, db = _auroc_num_den_batch(conf_b[IDX], h_b[IDX])
        draws[done:done + b] = (np.where(da > 0, na / np.maximum(da, 1e-12), np.nan)
                                - np.where(db > 0, nb / np.maximum(db, 1e-12), np.nan))
        done += b
    d = draws[np.isfinite(draws)]
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"n": int(n), "auroc_A": _r(pa), "auroc_B": _r(pb), "delta": _r(pa - pb),
            "ci95": [_r(lo), _r(hi)],
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}


# =================================================================================================
# THE FULL RESPONSE-RATE CURVE, with the RANDOM-ABSTENTION BAND DRAWN AT EVERY RATE
# =================================================================================================
def random_abstain_band(h: np.ndarray, rates: Sequence[float], n_draws: int,
                        seed: int) -> Dict[float, Dict]:
    """THE CONTROL THAT MATTERS. Declining to answer on a RANDOM subset also raises accuracy on the
    remainder whenever the remainder happens to be easier, so only separation from THIS band is
    evidence of selectivity. Computed once per hit vector and reused by every signal.

    One matrix of random permutations gives every rate at once: the cumulative mean of the permuted
    hit vector at position k IS the random-abstain accuracy at response rate k/n. The analytic band
    (sampling without replacement, normal approximation) is reported beside the empirical one so a
    reader can see they agree."""
    h = np.asarray(h, dtype=np.float64)
    n = h.size
    rng = np.random.default_rng(seed)
    cm = np.empty((n_draws, n), dtype=np.float32)
    step = max(1, int(2_000_000 // max(n, 1)))
    done = 0
    denom = np.arange(1, n + 1, dtype=np.float64)
    while done < n_draws:
        b = min(step, n_draws - done)
        perm = np.argsort(rng.random((b, n)), axis=1)
        cm[done:done + b] = (np.cumsum(h[perm], axis=1) / denom).astype(np.float32)
        done += b
    p = float(h.mean())
    out: Dict[float, Dict] = {}
    for r in rates:
        k = min(n, max(10, int(round(r * n))))
        col = cm[:, k - 1].astype(np.float64)
        if k >= n:
            sd = 0.0
        else:
            sd = float(np.sqrt(max(p * (1.0 - p), 0.0) / k * (n - k) / max(n - 1, 1)))
        out[r] = {"k": int(k), "response_rate": round(k / n, 4),
                  "band95": [_r(np.percentile(col, 2.5)), _r(np.percentile(col, 97.5))],
                  "band999_hi": _r(np.percentile(col, 99.95)),
                  "analytic_band95": [_r(p - 1.96 * sd), _r(p + 1.96 * sd)],
                  "mean_of_draws": _r(col.mean())}
    del cm
    return out


def rate_curve(h: np.ndarray, conf: np.ndarray, band: Dict[float, Dict], rates: Sequence[float],
               seed: int, n_tiebreaks: int = N_TIEBREAKS) -> Dict:
    """Accuracy against RESPONSE RATE. At rate r the arm answers the r-fraction of items on which
    its own confidence is highest.

    TIES ARE BROKEN AT RANDOM, N_TIEBREAKS TIMES. The source cell found that a stable argsort on a
    tied confidence vector silently returns items in POOL ORDER, manufacturing a fake curve with a
    real slope; that defect is designed out here, and the SPREAD across tie-breaks is reported so a
    reader can see whether any conclusion depends on the tie-break at all."""
    h = np.asarray(h, dtype=np.float64)
    conf = np.asarray(conf, dtype=np.float64)
    n = h.size
    rng = np.random.default_rng(seed)
    denom = np.arange(1, n + 1, dtype=np.float64)
    cum = np.empty((n_tiebreaks, n), dtype=np.float64)
    for t in range(n_tiebreaks):
        order = np.lexsort((rng.random(n), -np.nan_to_num(conf, nan=-np.inf)))
        cum[t] = np.cumsum(h[order]) / denom
    u, c = np.unique(conf[np.isfinite(conf)], return_counts=True)
    tie_mass = float((c[c > 1].sum() - int((c > 1).sum())) / max(n, 1))
    base = float(h.mean())
    pts, n_beat, n_beat_worst = [], 0, 0
    for r in rates:
        bd = band[r]
        k = bd["k"]
        col = cum[:, k - 1]
        med, lo_t, hi_t = float(np.median(col)), float(col.min()), float(col.max())
        beats = bool(med > bd["band95"][1])
        beats_worst = bool(lo_t > bd["band95"][1])
        n_beat += int(beats)
        n_beat_worst += int(beats_worst)
        pts.append({"response_rate": bd["response_rate"], "n_answered": k,
                    "accuracy_median_tiebreak": _r(med),
                    "accuracy_tiebreak_range": [_r(lo_t), _r(hi_t)],
                    "random_abstain_band95": bd["band95"],
                    "beats_random": beats, "beats_random_worst_tiebreak": beats_worst,
                    "lift_over_base": _r(med - base)})
    return {"n_scored": int(n), "accuracy_at_full_response": _r(base),
            "confidence_tie_mass": _r(tie_mass),
            "AURC_mean_accuracy_over_all_response_rates": _r(float(np.median(cum, axis=0).mean())),
            "n_rates_beating_random": int(n_beat), "n_rates": len(rates),
            "n_rates_beating_random_even_on_the_worst_tiebreak": int(n_beat_worst),
            "points": pts}


# =================================================================================================
# THE CONFIDENCE SIGNALS
# =================================================================================================
def store_neighbours(mat: np.ndarray, m: int, chunk: int = 512) -> np.ndarray:
    """Top-m nearest anchors to each anchor IN THE STORE'S OWN GEOMETRY (excluding self). This is
    what makes C6 / C7 judge-free: the 'acceptable set' is the substrate's own neighbourhood, never
    WordNet's."""
    from tools.floor_battery import l2n
    N = l2n(mat)
    n = N.shape[0]
    out = np.zeros((n, m), dtype=np.int64)
    for a in range(0, n, chunk):
        b = min(n, a + chunk)
        S = (N[a:b] @ N.T).astype(np.float32)
        S[np.arange(b - a), np.arange(a, b)] = -np.inf
        idx = np.argpartition(-S, m, axis=1)[:, :m]
        rows = np.arange(b - a)[:, None]
        ordr = np.argsort(-S[rows, idx], axis=1)
        out[a:b] = idx[rows, ordr]
        del S
    return out


def confidence_signals(S: np.ndarray, E: np.ndarray, mat_n: np.ndarray, nbr: np.ndarray,
                       cue_fam: np.ndarray) -> Dict[str, np.ndarray]:
    """Every signal is computed from the ARM'S OWN SCORES over the ELIGIBLE POOL, plus (for C6/C7)
    the STORE'S OWN geometry and (for C8) the CUE. No gold, no judge, no lookup: all of them are
    computable at run time by the system itself."""
    S = np.asarray(S, dtype=np.float32)
    if S.shape[1] == 1:                       # a CONSTANT arm broadcast as one column
        S = np.repeat(S, E.shape[1], axis=1)
    n_a, n_i = S.shape
    Sm = np.where(E, S, -np.inf).astype(np.float32)
    part = np.partition(Sm, n_a - 2, axis=0)[n_a - 2:, :]
    second, top1 = part[0].astype(np.float64), part[1].astype(np.float64)
    top_idx = np.argmax(Sm, axis=0)
    fin = np.isfinite(top1)
    marg = np.where(fin & np.isfinite(second), top1 - second, np.nan)

    n_el = np.maximum(E.sum(axis=0), 1).astype(np.float64)
    Z = np.where(E, S, 0.0).astype(np.float32)
    s1 = Z.sum(axis=0, dtype=np.float64)
    s2 = np.einsum("ij,ij->j", Z, Z).astype(np.float64)
    del Z
    mu = s1 / n_el
    var = np.maximum(s2 / n_el - mu * mu, 0.0)
    sd = np.sqrt(var) + 1e-12

    D = np.where(E, S - top1[None, :].astype(np.float32), np.float32(-1e30))
    W = np.exp(D / np.float32(SOFTMAX_T))
    Zs = W.sum(axis=0, dtype=np.float64)
    U = np.einsum("ij,ij->j", W, D).astype(np.float64)
    del W
    H = np.log(np.maximum(Zs, 1e-300)) - U / (SOFTMAX_T * np.maximum(Zs, 1e-300))

    # C6 -- ACCEPTABLE-SET MARGIN. Suppress the argmax AND its own store-neighbourhood, then take
    # the best score that remains. "How sure am I that the answer is in THIS region", rather than
    # "how sure am I that it is THIS word".
    D[:] = Sm
    cols = np.repeat(np.arange(n_i)[None, :], nbr.shape[1], axis=0)
    D[nbr[top_idx].T.ravel(), cols.ravel()] = -np.inf
    D[top_idx, np.arange(n_i)] = -np.inf
    out_best = D.max(axis=0).astype(np.float64)
    setmarg = np.where(fin & np.isfinite(out_best), top1 - out_best, np.nan)
    del D

    # C7 -- COHERENCE of the top-m scoring anchors in the store's own geometry.
    m = nbr.shape[1]
    topm = np.argpartition(-Sm, m, axis=0)[:m, :]            # [m, n_i]
    V = mat_n[topm]                                          # [m, n_i, d]
    G = np.einsum("aid,bid->iab", V, V)
    del V
    iu = np.triu_indices(m, k=1)
    coh = G[:, iu[0], iu[1]].mean(axis=1).astype(np.float64)
    del G, Sm
    return {"C1_TOP1_ABS": np.where(fin, top1, np.nan),
            "C2_MARGIN_ABS": marg,
            "C3_MARGIN_REL": np.where(fin, marg / np.maximum(np.abs(top1), 1e-6), np.nan),
            "C4_NEG_ENTROPY": np.where(fin, -H, np.nan),
            "C5_TOP1_Z": np.where(fin, (top1 - mu) / sd, np.nan),
            "C6_SETMARGIN_M%d" % m: setmarg,
            "C7_TOPM_COHERENCE": np.where(fin, coh, np.nan),
            "C8_CUE_FAMILIARITY": np.asarray(cue_fam, dtype=np.float64),
            "_argmax_index": top_idx.astype(np.int64)}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    rng = np.random.default_rng(17)

    # S1 -- AUROC against a BRUTE-FORCE O(n^2) definition, including fractional labels and heavy
    # ties. If the summary statistic is wrong every number in the cell is wrong.
    def brute(conf, h):
        n = conf.size
        num = den = 0.0
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                w = h[i] * (1.0 - h[j])
                den += w
                s = 1.0 if conf[i] > conf[j] else (0.5 if conf[i] == conf[j] else 0.0)
                num += w * s
        return num / den
    for lab, (c, h) in {
            "binary_no_ties": (rng.random(120), (rng.random(120) < 0.3).astype(float)),
            "fractional": (rng.random(120), rng.random(120)),
            "heavy_ties": (np.round(rng.random(120) * 3) / 3.0, (rng.random(120) < 0.4).astype(float)),
            "all_tied": (np.full(120, 0.7), (rng.random(120) < 0.4).astype(float))}.items():
        a, b = auroc(c, h), brute(c, h)
        assert abs(a - b) < 1e-9, "AUROC disagrees with brute force on %s: %.12f vs %.12f" % (lab, a, b)
    assert abs(auroc(np.full(200, 1.0), (rng.random(200) < 0.3).astype(float)) - 0.5) < 1e-12, (
        "a CONSTANT confidence did not score exactly 0.5 -- the tie guard is broken")
    # and the batched version must agree with the scalar one
    C4 = rng.random((7, 120)); H4 = (rng.random((7, 120)) < 0.35).astype(float)
    nb, db = _auroc_num_den_batch(C4, H4)
    for i in range(7):
        na, da = _auroc_num_den(C4[i], H4[i])
        assert abs(na - nb[i]) < 1e-8 and abs(da - db[i]) < 1e-8, "batched AUROC != scalar AUROC"
    res["S1_auroc_matches_brute_force"] = True

    # S2 -- AUROC IS DIRECTIONAL AND CAN FAIL. An informative signal must land above 0.5 with a
    # separated CI; an uninformative one must not. Both halves are required.
    n = 3000
    truth = (rng.random(n) < 0.15).astype(float)
    good = truth + 0.5 * rng.standard_normal(n)
    junk = rng.standard_normal(n)
    ag = auroc_with_ci(good, truth, None, 800, 1)
    aj = auroc_with_ci(junk, truth, None, 800, 1)
    assert ag["band_vs_0.5"] == "ABOVE" and ag["auroc"] > 0.6, "informative signal missed: %r" % ag
    assert aj["band_vs_0.5"] == "NOT_SEPARATED", "junk signal manufactured selectivity: %r" % aj
    res["S2_auroc_can_fail"] = {"informative": ag["auroc"], "junk": aj["auroc"]}

    # S3 -- THE FREQUENCY CONTROL ACTUALLY CONTROLS. Build a signal that is PURE FREQUENCY and a
    # label that is PURE FREQUENCY: the raw AUROC must be high and the STRATIFIED AUROC must
    # collapse to 0.5. If it does not, the mandatory frequency control is decorative.
    f = rng.random(n)
    lab_f = (rng.random(n) < f * 0.4).astype(float)          # only frequency drives the label
    strata = np.minimum((f * N_FREQ_STRATA).astype(int), N_FREQ_STRATA - 1)
    raw = auroc_with_ci(f, lab_f, None, 800, 2)
    strat = auroc_with_ci(f, lab_f, strata, 800, 2)
    assert raw["auroc"] > 0.62, "the pure-frequency probe did not fire: %r" % raw
    assert abs(strat["auroc"] - 0.5) < 0.06, (
        "stratification failed to remove a pure-frequency effect: %r" % strat)
    # and it must NOT destroy a real effect that is independent of frequency
    lab_g = (rng.random(n) < 0.15).astype(float)
    sig_g = lab_g + 0.5 * rng.standard_normal(n)
    strat_g = auroc_with_ci(sig_g, lab_g, strata, 800, 2)
    assert strat_g["band_vs_0.5"] == "ABOVE", (
        "stratification destroyed a frequency-independent effect: %r" % strat_g)
    res["S3_frequency_stratification"] = {"pure_frequency_raw": raw["auroc"],
                                          "pure_frequency_stratified": strat["auroc"],
                                          "independent_effect_stratified": strat_g["auroc"]}

    # S4 -- THE RANDOM-ABSTAIN BAND IS CALIBRATED. A random signal must fall inside it about 95% of
    # the time, and a CONSTANT signal must essentially never beat it. This is the control the whole
    # cell rests on, so it is measured rather than trusted.
    band = random_abstain_band(truth, RATES, 800, 3)
    flat = rate_curve(truth, np.full(n, 0.5), band, RATES, 4)
    noisy = rate_curve(truth, np.random.default_rng(9).random(n), band, RATES, 5)
    strong = rate_curve(truth, good, band, RATES, 6)
    assert flat["n_rates_beating_random"] <= 1, (
        "a CONSTANT confidence beat the random band at %d of %d rates -- the control is broken: %r"
        % (flat["n_rates_beating_random"], flat["n_rates"], flat["points"][:3]))
    assert abs(flat["AURC_mean_accuracy_over_all_response_rates"]
               - flat["accuracy_at_full_response"]) < 0.03, "a CONSTANT confidence sloped: %r" % flat
    assert flat["confidence_tie_mass"] > 0.99, "tie mass not detected on an all-ties signal"
    assert noisy["n_rates_beating_random"] <= 2, (
        "a RANDOM confidence beat the band at %d rates" % noisy["n_rates_beating_random"])
    assert strong["n_rates_beating_random"] >= 10, (
        "an informative confidence failed the band: %r" % strong["n_rates_beating_random"])
    assert strong["points"][0]["accuracy_median_tiebreak"] > 2.0 * strong[
        "accuracy_at_full_response"], "informative confidence did not lift selective accuracy"
    res["S4_random_abstain_band_calibrated"] = {
        "constant_beats": flat["n_rates_beating_random"], "random_beats": noisy["n_rates_beating_random"],
        "informative_beats": strong["n_rates_beating_random"],
        "informative_at_lowest_rate": strong["points"][0]["accuracy_median_tiebreak"],
        "base": strong["accuracy_at_full_response"]}

    # S5 -- the signal extractor. top1/top2/z/entropy/setmargin computed on a hand-checkable case.
    S = np.array([[5.0, 1.0], [3.0, 9.0], [4.0, 2.0], [0.0, 0.0]], dtype=np.float32)
    E = np.array([[True, True], [False, True], [True, True], [True, True]], dtype=bool)
    matn = np.eye(4, dtype=np.float32)
    nbr_t = np.array([[2, 3], [0, 3], [0, 3], [0, 2]], dtype=np.int64)
    cs = confidence_signals(S, E, matn, nbr_t, np.array([0.1, 0.2]))
    assert list(cs["C1_TOP1_ABS"]) == [5.0, 9.0], "top1 ignored the eligibility mask: %r" % cs["C1_TOP1_ABS"]
    assert list(cs["C2_MARGIN_ABS"]) == [1.0, 7.0], "margin wrong: %r" % cs["C2_MARGIN_ABS"]
    assert list(cs["_argmax_index"]) == [0, 1], "argmax wrong"
    # item 0: argmax=anchor0, its neighbours are {2,3}; eligible are {0,2,3}; suppressing 0,2,3
    # leaves NOTHING eligible, so the set-margin is NOT FINITE. That is the correct behaviour and
    # is asserted rather than papered over -- a silent 0.0 there would be a fake confidence value.
    assert not np.isfinite(cs["C6_SETMARGIN_M2"][0]), (
        "set margin should be undefined when the whole eligible pool is inside the winner's own "
        "neighbourhood: %r" % cs["C6_SETMARGIN_M2"])
    assert abs(float(cs["C6_SETMARGIN_M2"][1]) - 7.0) < 1e-6, "set margin wrong on item 1"
    assert abs(float(cs["C5_TOP1_Z"][0]) - (5.0 - 3.0) / (np.std([5.0, 4.0, 0.0]) + 1e-12)) < 1e-3, (
        "top1 z-score wrong: %r" % cs["C5_TOP1_Z"][0])
    assert list(cs["C8_CUE_FAMILIARITY"]) == [0.1, 0.2]
    res["S5_confidence_signals"] = True

    # S6 -- the ACCEPTABLE-SET margin is genuinely different from the top-1 margin, and behaves the
    # way its motivation requires: when the runner-up is a STORE NEIGHBOUR of the winner, the
    # top-1 margin is small but the set margin is large.
    S2 = np.zeros((6, 1), dtype=np.float32)
    S2[:, 0] = [0.9, 0.88, 0.2, 0.1, 0.05, 0.0]
    E2 = np.ones((6, 1), dtype=bool)
    nb2 = np.array([[1, 2], [0, 2], [0, 1], [4, 5], [3, 5], [3, 4]], dtype=np.int64)
    c2 = confidence_signals(S2, E2, np.eye(6, dtype=np.float32), nb2, np.array([0.0]))
    assert abs(float(c2["C2_MARGIN_ABS"][0]) - 0.02) < 1e-6, "top1 margin wrong"
    assert abs(float(c2["C6_SETMARGIN_M2"][0]) - 0.8) < 1e-6, (
        "set margin did not suppress the winner's own neighbourhood: %r" % c2["C6_SETMARGIN_M2"])
    res["S6_setmargin_differs_from_top1_margin"] = True

    # S7 -- store_neighbours returns real nearest neighbours, self excluded, sorted.
    M = np.array([[1, 0], [0.99, 0.14], [0, 1], [-1, 0]], dtype=np.float32)
    nb = store_neighbours(M, 2)
    assert 0 not in nb[0].tolist(), "store_neighbours returned self"
    assert nb[0][0] == 1, "nearest neighbour of anchor 0 should be anchor 1: %r" % nb[0]
    res["S7_store_neighbours"] = True

    # S8 -- THE CALIBRATION INSTRUMENT'S OWN VALIDITY ARMS FAIL INDEPENDENTLY. One is built FROM
    # the labels, the other DESTROYS the signal; breaking one must leave the other unmoved.
    ka = truth + 0.6 * rng.standard_normal(n)                  # ORACLE noisy confidence
    nl = np.full(n, 0.5)                                       # constant
    ka_ok = rate_curve(truth, ka, band, RATES, 7)["n_rates_beating_random"] >= 10
    nl_ok = rate_curve(truth, nl, band, RATES, 7)["n_rates_beating_random"] <= 1
    ka_broken = rate_curve(truth, rng.standard_normal(n), band, RATES, 7)["n_rates_beating_random"]
    assert ka_ok and nl_ok, "calibration validity arms did not both pass"
    assert ka_broken <= 2 and nl_ok, (
        "breaking the calibration KA moved the NULL as well -- they are not independent")
    res["S8_calibration_validity_arms_independent"] = {"KA_passes": ka_ok, "NULL_passes": nl_ok,
                                                       "broken_KA_beats": int(ka_broken)}

    # S9 -- the paired AUROC delta is ZERO when the two blocks are identical, and separates when
    # they are genuinely different.
    d0 = paired_auroc_delta(good, truth, good, truth, 600, 8)
    assert abs(d0["delta"]) < 1e-9 and d0["band"] == "NOT_SEPARATED", (
        "identical blocks produced a delta: %r" % d0)
    d1 = paired_auroc_delta(good, truth, junk, truth, 600, 8)
    assert d1["band"] == "ABOVE", "paired delta missed a real dissociation: %r" % d1
    res["S9_paired_delta"] = {"identical": d0["delta"], "real": d1["delta"]}

    # S10 -- the imported harnesses' own suites, including the judge, the morphology guard, the
    # saturation guard and the balanced-pool construction. Not restated; run.
    res["reused_selftest_exp_task_degeneracy_v1"] = TD.self_test()
    res["reused_selftest_exp_synonym_substitution_metric_v1_judge"] = {
        "n_syn_dog": len(SYN.synset_colemmas("dog")),
        "nested_in_landed_closure": bool(SYN.synset_colemmas("dog") <= SYN.landed_closure("dog"))}
    assert res["reused_selftest_exp_synonym_substitution_metric_v1_judge"][
        "nested_in_landed_closure"], "the criterion ladder is not nested"

    print("[selftest] PASS " + json.dumps({k: v for k, v in res.items()
                                           if not k.startswith("reused_")})[:2000], flush=True)
    return res


# =================================================================================================
# main run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    full = (grid == "full")
    n_boot = 4000 if full else 1000
    n_draws = 2000 if full else 500
    TD.N_BOOT = 10000 if full else 2000        # affects score_condition CI width only, not points
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "MASTER_SEED_FRESH_not_the_sources": MASTER_SEED,
                 "SOURCE_CELL_SEED_for_contrast": SYN.MASTER_SEED,
                 "RULER_MODE_GATE": TD.ruler_mode_gate(),
                 "cache": TD.build_cache_if_missing()}
    rep["PER_UNIT_SHARD"] = {
        "path": os.path.join(OUT_DIR, "units.jsonl"),
        "units_already_present_at_start": sorted(completed_units(OUT_DIR)),
        "SEMANTICS_STATED_HONESTLY": "one (block, regime) scoring unit is appended the moment it "
                                     "finishes, so a killed run shows exactly how far it got and "
                                     "which block was in flight. It is a PROGRESS RECORD, not a "
                                     "skip-list: the calibration analysis needs the per-item hit "
                                     "and confidence VECTORS in memory and those are not JSON, so "
                                     "a resumed run recomputes the scoring rather than pretending "
                                     "to reuse it. Claiming resume-skip here would be a lie about "
                                     "what is durable."}
    C = TD.load_cache()
    aux = TD.load_aux(C)
    rep["aux_source"] = aux.get("source", "?")
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    C["qidx"] = np.array([C["pos"].get(w, 0) for w in C["L_words"]], dtype=np.int64)
    pos = C["pos"]
    print("[load] n_anchors=%d n_items=%d keep=%d d=%d  %.0fs"
          % (n_anchors, n_items, int(keep.sum()), mat.shape[1], time.time() - t0), flush=True)

    from tools.floor_battery import l2n
    mat_n = l2n(mat)
    nbr = store_neighbours(mat, M_NBR)
    print("[store] %d-NN neighbourhoods built  %.0fs" % (M_NBR, time.time() - t0), flush=True)

    # ---- eligibility: L masked out (the LANDED instrument) vs L eligible ------------------------
    E_EXCL = np.zeros((n_anchors, n_items), dtype=bool)
    E_SELF = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if keep[i]:
            E_EXCL[:, i] = mat_ok
            E_SELF[:, i] = mat_ok
            if len(C["excl"][i]):
                E_EXCL[C["excl"][i], i] = False

    # ---- the criterion ladder, from the SOURCE CELL'S OWN judge (imported, not reimplemented) ---
    self_idx = np.full(n_items, -1, dtype=np.int64)
    g_syn: List[np.ndarray] = []
    g_land: List[np.ndarray] = []
    for i, w in enumerate(C["L_words"]):
        if not keep[i]:
            g_syn.append(np.zeros(0, np.int64)); g_land.append(np.zeros(0, np.int64))
            continue
        L = str(w).lower()
        self_idx[i] = pos.get(L, -1)
        s_all, s_land = SYN.synset_colemmas(L), SYN.landed_closure(L)
        g_syn.append(np.array(sorted(pos[g] for g in s_all if g in pos), dtype=np.int64))
        g_land.append(np.array(sorted(pos[g] for g in s_land if g in pos), dtype=np.int64))
    print("[judge] criterion ladder built  %.0fs" % (time.time() - t0), flush=True)

    G_SYN_EXCL = SYN.gold_matrix(g_syn, n_anchors, n_items, E_EXCL)
    G_LAND_EXCL = SYN.gold_matrix(g_land, n_anchors, n_items, E_EXCL)
    SELFM = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if keep[i] and self_idx[i] >= 0:
            SELFM[self_idx[i], i] = True
    SELFM &= E_SELF
    G_EXACT_SELF = SELFM.copy()
    G_SYN_SELF_ONLY = SYN.gold_matrix(g_syn, n_anchors, n_items, E_SELF)
    G_SELF_PLUS_SYN = G_SYN_SELF_ONLY | SELFM
    G_SELF_PLUS_LAND = SYN.gold_matrix(g_land, n_anchors, n_items, E_SELF) | SELFM

    POP_ALL = keep & G_LAND_EXCL.any(axis=0)
    POP_SYN = POP_ALL & G_SYN_EXCL.any(axis=0)
    POP_SELF = keep & G_EXACT_SELF.any(axis=0)
    POP_SELF_SYN = POP_SELF & G_SYN_EXCL.any(axis=0)        # the SOURCE CELL'S naming population
    # THE ONE COMMON ITEM SET for every cross-block comparison in this cell: an item is in it only
    # if ALL SIX blocks are scorable on it, so no number ever crosses a population.
    POP_COMMON = (POP_SELF & G_SYN_EXCL.any(axis=0) & G_LAND_EXCL.any(axis=0)
                  & G_SYN_SELF_ONLY.any(axis=0))
    rep["POPULATIONS"] = {
        "POP_ALL_landed": int(POP_ALL.sum()), "POP_SYN": int(POP_SYN.sum()),
        "POP_SELF": int(POP_SELF.sum()),
        "POP_SELF_SYN_the_source_cells_naming_population": int(POP_SELF_SYN.sum()),
        "POP_COMMON_used_for_every_cross_block_comparison": int(POP_COMMON.sum()),
        "why": "the criterion and the pool both move the scorable population. Every cross-block "
               "AUROC difference in this cell is computed on POP_COMMON, in one item ordering, so "
               "no number crosses a population, a pool or a criterion."}
    print("[pop] COMMON=%d SELF_SYN=%d ALL=%d  %.0fs"
          % (POP_COMMON.sum(), POP_SELF_SYN.sum(), POP_ALL.sum(), time.time() - t0), flush=True)

    # ---- arms, imported wholesale ---------------------------------------------------------------
    f5 = constant_prototype_floor(mat, mat_ok)
    from experiments import exp_meaning_lift_population_code_v1 as LIFT
    X, cov = TD.norms_for(anchors, TD.NORM_SEED)
    grd = LIFT.lift_kcap(X, 1024, TD.NORM_SEED, TD.GRD_FRAC, True, True).astype(np.float32)
    ST = TD.static_arms(C, aux, f5, grd)
    rep["CONSTANT_FLOOR_RECOMPUTED_HERE_not_imported"] = {
        "source": "tools.floor_battery.constant_prototype_floor(mat, mat_ok) on THIS population",
        "top_anchor_by_constant_score": anchors[int(np.argmax(np.where(np.isfinite(f5), f5, -np.inf)))],
        "note": "0.1382 and 0.2070 are floors on OTHER populations and are deliberately NOT "
                "imported. Every constant-floor number in this cell is computed here, on this "
                "population, with its own n, under all three tie conventions."}

    # ---- query-word features for the FREQUENCY-MATCHED CONTROL ----------------------------------
    q_logfreq = np.array([float(aux["fq"][pos[str(w).lower()]]) if str(w).lower() in pos else np.nan
                          for w in C["L_words"]], dtype=np.float64)
    q_len = np.array([float(len(str(w))) for w in C["L_words"]], dtype=np.float64)
    cue_fam_part = (l2n(C["Q_part"]) @ l2n(mat[mat_ok].mean(axis=0)[None, :])[0]).astype(np.float64)
    cue_fam_exact = (l2n(C["Q_exact"]) @ l2n(mat[mat_ok].mean(axis=0)[None, :])[0]).astype(np.float64)

    # ---- BLOCKS ---------------------------------------------------------------------------------
    blocks: Dict[str, Dict] = {}

    def add(name: str, E, G, km, chance, rank, des, what):
        blocks[name] = {"E": E, "GOLD": G, "keep": km, "chance": float(chance), "rank": rank,
                        "designated": des, "what": what}

    def designate(G: np.ndarray, km: np.ndarray, seed: int) -> np.ndarray:
        r = np.random.default_rng(seed)
        d = np.full(n_items, -1, dtype=np.int64)
        for i in np.flatnonzero(km):
            gi = np.flatnonzero(G[:, i])
            if gi.size:
                d[i] = int(gi[r.integers(0, gi.size)])
        return d

    def chance_of(G, E, km):
        return float(np.mean(G[:, km].sum(axis=0) / np.maximum(E.sum(axis=0)[km], 1)))

    OPEN_BLOCKS = [
        ("A_POOLSELF_GOLD_EXACT", E_SELF, G_EXACT_SELF,
         "THE SOURCE'S POSITIVE. L is IN the pool and only L is correct: NAME THE WORD."),
        ("B_POOLSELF_GOLD_SELF_PLUS_SYN", E_SELF, G_SELF_PLUS_SYN,
         "criterion loosened ONE rung. IDENTICAL pool, items and scores as A -- and therefore an "
         "IDENTICAL confidence vector. Only the hit label changes."),
        ("C_POOLSELF_GOLD_SELF_PLUS_LANDED", E_SELF, G_SELF_PLUS_LAND,
         "criterion loosened TWO rungs, to the landed closure. Identical pool, items, scores."),
        ("D_POOLSELF_GOLD_SYNONLY", E_SELF, G_SYN_SELF_ONLY,
         "L is IN the pool but is NOT a correct answer. Paired with E this isolates THE POOL: same "
         "items, same gold family, the only difference is whether L is eligible."),
        ("E_POOLMASK_GOLD_SYN", E_EXCL, G_SYN_EXCL,
         "THE SOURCE'S NULL, tight criterion. The LANDED eligibility: L masked out, so substitution "
         "is FORCED and only a true synset synonym counts."),
        ("F_POOLMASK_GOLD_LANDED", E_EXCL, G_LAND_EXCL,
         "THE SOURCE'S NULL, landed criterion. The landed instrument exactly, restricted to the "
         "common population. REGRESSION GATE against 0.0223 partial-cue / 0.0481 exact-key."),
    ]
    for nm, E, G, what in OPEN_BLOCKS:
        add(nm, E, G, POP_COMMON, chance_of(G, E, POP_COMMON), True,
            designate(G, POP_COMMON, MASTER_SEED + 5), what)
    # the LANDED block on its OWN landed population, for the regression gate only
    add("REG_LANDED_POPALL", E_EXCL, G_LAND_EXCL, POP_ALL, chance_of(G_LAND_EXCL, E_EXCL, POP_ALL),
        True, designate(G_LAND_EXCL, POP_ALL, MASTER_SEED + 5),
        "REGRESSION GATE ONLY: the landed instrument on the landed population (n~3994).")
    add("REG_NAMING_POPSELFSYN", E_SELF, G_EXACT_SELF, POP_SELF_SYN,
        chance_of(G_EXACT_SELF, E_SELF, POP_SELF_SYN), True,
        designate(G_EXACT_SELF, POP_SELF_SYN, MASTER_SEED + 5),
        "REGRESSION GATE ONLY: the naming block on the SOURCE CELL'S OWN population (n~2471), so "
        "the source's 0.0457 base is reproduced before anything is re-analysed.")

    # ---- DE-BIASED pools: a constant ranking is dead by construction ----------------------------
    def _elig_from_cand(cand, ok, K):
        E = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
        E[rows.ravel(), cols.ravel()] = True
        return E

    ks = K_LIST if full else K_LIST[:1]
    gl_exact = [np.flatnonzero(G_EXACT_SELF[:, i]) for i in range(n_items)]
    gl_syn = [np.flatnonzero(G_SYN_EXCL[:, i]) for i in range(n_items)]
    des_exact = designate(G_EXACT_SELF, POP_COMMON, MASTER_SEED + 5)
    des_syn = designate(G_SYN_EXCL, POP_COMMON, MASTER_SEED + 5)
    no_excl = [np.zeros(0, dtype=np.int64) for _ in range(n_items)]
    for K in ks:
        cnd, _gb = balanced_candidate_sets(des_exact, gl_exact, no_excl, POP_COMMON, K,
                                           MASTER_SEED + 17 + K)
        ok = cnd[:, 0] >= 0
        EB = _elig_from_cand(cnd, ok, K)
        assert int((EB & G_EXACT_SELF).sum(axis=0)[ok].max()) == 1, "naming balanced pool has 2 golds"
        add("BALK%d_A_NAMING" % K, EB, G_EXACT_SELF, ok, 1.0 / (K + 1), False, des_exact,
            "DE-BIASED naming pool: gold + %d distractors drawn from the gold marginal, so NO "
            "constant ranking can beat chance %.4f. If the confidence still selects here, the "
            "selectivity is not prototypicality or popularity." % (K, 1.0 / (K + 1)))
        cnd2, _gb2 = balanced_candidate_sets(des_syn, gl_syn, C["excl"], POP_COMMON, K,
                                             MASTER_SEED + 17 + K)
        ok2 = cnd2[:, 0] >= 0
        EB2 = _elig_from_cand(cnd2, ok2, K)
        assert int((EB2 & G_SYN_EXCL).sum(axis=0)[ok2].max()) == 1, "sub balanced pool has 2 golds"
        add("BALK%d_E_SUBSTITUTING" % K, EB2, G_SYN_EXCL, ok2, 1.0 / (K + 1), False, des_syn,
            "DE-BIASED substitution pool, same construction, chance %.4f." % (1.0 / (K + 1)))

    K_D = ks[0]
    cand_d, _gd, dmatch = matched_candidate_sets(des_syn, gl_syn, C["excl"], POP_COMMON, K_D,
                                                 MASTER_SEED + 31, ST["F1_TRIGRAM_ONLY_orthographic"])
    okd = cand_d[:, 0] >= 0
    add("MATCHEDK%d_E_SUBSTITUTING" % K_D, _elig_from_cand(cand_d, okd, K_D), G_SYN_EXCL, okd,
        1.0 / (K_D + 1), False, des_syn,
        "SECONDARY, STRICTER: balanced plus distractors matched to the gold on trigram similarity. "
        "ITS OWN ORACLE CONSTANT IS RE-READ HERE, NEVER INHERITED -- the source cell measured 0.7262 "
        "against chance 0.0625 on its matched pool and excluded it from every claim.")
    rep["matched_pool_match_diagnostics"] = dmatch
    print("[blocks] %d built  %.0fs" % (len(blocks), time.time() - t0), flush=True)

    # ---- score every block ----------------------------------------------------------------------
    results: Dict[str, Dict] = {}
    hits: Dict[Tuple[str, str, str], np.ndarray] = {}
    scored: Dict[Tuple[str, str, str], np.ndarray] = {}
    confs: Dict[Tuple[str, str], Dict[str, np.ndarray]] = {}
    ORACLE = {}
    for bname, cfg in blocks.items():
        kk = np.flatnonzero(cfg["keep"])
        restricted = bname.startswith(("BALK", "MATCHEDK"))
        ORACLE[bname] = TD.col(oracle_constant_scores(
            n_anchors, [np.flatnonzero(cfg["GOLD"][:, i]) for i in kk],
            ([np.flatnonzero(cfg["E"][:, i]) for i in kk] if restricted else None)))
    print("[oracle] %d oracle columns built  %.0fs" % (len(ORACLE), time.time() - t0), flush=True)

    # WHICH (block, regime) PAIRS GET A CONFIDENCE VECTOR. EXACT_KEY is not the operating point and
    # is computed only for the two blocks that carry the source's headline comparison.
    def wants_conf(bn: str, rg: str) -> bool:
        return rg == "PARTIAL_CUE" or bn.startswith(("A_", "E_"))

    for regime in ("EXACT_KEY", "PARTIAL_CUE"):
        arms_base = TD.build_arms(C, ST, regime)
        for dead in ("FUSE_ctx_SPELL", "FUSE_ctx_SPELL_GRD", "G_GROUNDED_KCAP_f0.100_lexical"):
            arms_base.pop(dead, None)          # not needed here; 87 MB each
        cue = cue_fam_exact if regime == "EXACT_KEY" else cue_fam_part
        for bname, cfg in sorted(blocks.items()):
            uk = unit_key(bname, regime, grid)
            arms = dict(arms_base)
            # THE KNOWN-ANSWER ARM IS BUILT PER BLOCK AND DISCARDED. Caching one dense
            # [n_anchors, n_items] matrix per distinct designation costs ~0.7 GB across this
            # block set; recomputing costs a few seconds. Memory, not cleverness.
            arms["KA_QUERY_IS_GOLD_VECTOR"] = TD.known_answer_arm(C, cfg["designated"])
            arms["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"] = ORACLE[bname]
            key = "%s|%s" % (bname, regime)
            r = TD.score_condition(key, cfg["E"], cfg["GOLD"], cfg["keep"], arms, cfg["chance"],
                                   bool(cfg["rank"]), FLOORS)
            r["condition_note"] = cfg["what"]
            r["POPULATION"] = int(np.asarray(cfg["keep"]).sum())
            # CEILING / IDENTITY GUARD, inherited in spirit from the source cell: on a pool where L
            # is eligible, every LEXICAL channel compares L to ITSELF and pins at 1.0. Those arms
            # are NOT floors there, they are identity lookups, and no floor comparison is read from
            # such a block. It does not touch the calibration analysis, whose control is the arm's
            # OWN random-abstain band and the no-understanding CONFIDENCE policies.
            A = r["hit_at_1_TIE_CORRECTED_primary"]
            pinned = sorted(k for k, v in A.items() if v >= 0.99 and not k.startswith("KA_"))
            if pinned:
                r["VOID_IDENTITY_LOOKUP_ARMS"] = pinned
                r["NO_FLOOR_COMPARISON_MAY_BE_READ_FROM_THIS_BLOCK"] = (
                    "L is IN the eligible pool and these arms' queries are built from L itself, so "
                    "they are self-matches, not floors. The calibration result in this block does "
                    "NOT depend on them: its control is the RANDOM-ABSTAIN band plus the "
                    "no-understanding confidence policies X2/X3/X4/X5.")
            results[key] = r
            record_unit(OUT_DIR, uk, {"block": bname, "regime": regime,
                                      "R0": A.get("R0_CTX_DENSE_our_read_out"),
                                      "KA": r["VALIDITY"]["KNOWN_ANSWER_hit_at_1"],
                                      "NULL": r["VALIDITY"]["NULL_hit_at_1"],
                                      "n": r["n_common_scored"]})
            for a in KEEP_ARMS:
                if a not in arms:
                    continue
                h = hit_at_1_both_tie_conventions(arms[a], cfg["E"], cfg["GOLD"])
                hits[(bname, regime, a)] = h["hit_exp"]
                scored[(bname, regime, a)] = h["scored"] & np.asarray(cfg["keep"], bool)
            if wants_conf(bname, regime) and (bname, regime) not in confs:
                confs[(bname, regime)] = confidence_signals(
                    arms["R0_CTX_DENSE_our_read_out"], cfg["E"], mat_n, nbr, cue)
            del arms
        del arms_base
    rep["RESULTS_BY_BLOCK"] = results
    print("[score] all %d blocks x 2 regimes scored  %.0fs" % (len(blocks), time.time() - t0),
          flush=True)

    # ---- REGRESSION GATE: the arms are PROVABLY the landed ones ---------------------------------
    def _acc(bn, rg, arm):
        return results["%s|%s" % (bn, rg)]["hit_at_1_TIE_CORRECTED_primary"].get(arm)
    gate = {
        "R0_partial_cue_landed_instrument": _acc("REG_LANDED_POPALL", "PARTIAL_CUE",
                                                 "R0_CTX_DENSE_our_read_out"),
        "R0_exact_key_landed_instrument": _acc("REG_LANDED_POPALL", "EXACT_KEY",
                                               "R0_CTX_DENSE_our_read_out"),
        "F1_trigram_landed": _acc("REG_LANDED_POPALL", "PARTIAL_CUE", "F1_TRIGRAM_ONLY_orthographic"),
        "F5_constant_landed": _acc("REG_LANDED_POPALL", "PARTIAL_CUE",
                                   "F5_CONSTANT_PROTOTYPE_zero_query_information"),
        "R0_naming_base_on_the_SOURCE_population": _acc("REG_NAMING_POPSELFSYN", "PARTIAL_CUE",
                                                        "R0_CTX_DENSE_our_read_out"),
        "expected": {"R0_partial": 0.0223, "R0_exact": 0.0481, "F1": 0.0871, "F5": 0.1390,
                     "naming_base": 0.0457},
        "n_landed": results["REG_LANDED_POPALL|PARTIAL_CUE"]["n_common_scored"],
        "n_naming_source_population": results["REG_NAMING_POPSELFSYN|PARTIAL_CUE"]["n_common_scored"]}
    gate["ALL_REPRODUCE"] = bool(
        abs((gate["R0_partial_cue_landed_instrument"] or -9) - 0.0223) < 5e-4
        and abs((gate["R0_exact_key_landed_instrument"] or -9) - 0.0481) < 5e-4
        and abs((gate["F1_trigram_landed"] or -9) - 0.0871) < 5e-4
        and abs((gate["F5_constant_landed"] or -9) - 0.1390) < 5e-4
        and abs((gate["R0_naming_base_on_the_SOURCE_population"] or -9) - 0.0457) < 5e-4)
    gate["what_it_proves"] = (
        "the arms, pool, scorer and cache are IMPORTED from the landed cells rather than rebuilt, "
        "so this is an IDENTITY check. If it holds, any difference from the source cell's "
        "abstention result is a difference in the ANALYSIS, not in the measurement.")
    rep["REGRESSION_GATE"] = gate
    assert gate["ALL_REPRODUCE"], "REGRESSION GATE FAILED -- this is not the landed instrument: %r" % gate
    print("[gate] regression gate PASSES  %.0fs" % (time.time() - t0), flush=True)

    # ---- THE CALIBRATION ANALYSIS ----------------------------------------------------------------
    # THE FREQUENCY-MATCHED CONTROL. Deciles of log corpus count of the QUERY WORD, cut over every
    # scorable item (not over one block's subset) so that the strata are the same object in every
    # block and a stratified number in one block is comparable to a stratified number in another.
    strata_all = np.full(n_items, -1, dtype=np.int64)
    fin_f = np.isfinite(q_logfreq) & keep
    qs = np.quantile(q_logfreq[fin_f], np.linspace(0, 1, N_FREQ_STRATA + 1)[1:-1])
    strata_all[fin_f] = np.searchsorted(qs, q_logfreq[fin_f])
    rep["FREQUENCY_STRATA"] = {
        "n_strata": N_FREQ_STRATA, "cut_on": "log1p(corpus count) of the QUERY WORD L",
        "cut_points": [_r(x) for x in qs],
        "sizes": [int((strata_all[POP_COMMON] == s).sum()) for s in range(N_FREQ_STRATA)],
        "why": "a system confident about common words and right about common words has learned "
               "nothing. The stratified AUROC is concordance computed WITHIN a decile and pooled, "
               "so a signal that is only frequency in disguise scores 0.5 there by construction "
               "(verified on a synthetic pure-frequency probe in self-test S3)."}
    rng_half = np.random.default_rng(MASTER_SEED + 991)
    half = rng_half.random(n_items) < 0.5

    def conf_floor_vectors(bname: str, regime: str, sub: np.ndarray, seed: int,
                           h: np.ndarray) -> Dict[str, np.ndarray]:
        r = np.random.default_rng(seed)
        cs = confs[(bname, regime)]
        return {"X2_QUERY_LOGFREQ": q_logfreq[sub],
                "X3_QUERY_LENGTH": -q_len[sub],
                "X4_CONSTANT": np.full(sub.size, 0.5),
                "X5_SCRAMBLED": r.permutation(cs[PRIMARY_SIGNAL][sub]),
                CALIB_KA: np.asarray(h, np.float64) + 0.6 * r.standard_normal(sub.size)}

    calib: Dict[str, Dict] = {}
    for bname in sorted(blocks):
        for regime in ("PARTIAL_CUE", "EXACT_KEY"):
            if (bname, regime) not in confs:
                continue                                   # EXACT_KEY is not the operating point
            arm = "R0_CTX_DENSE_our_read_out"
            k = (bname, regime, arm)
            if k not in hits:
                continue
            sub = np.flatnonzero(scored[k] & np.asarray(blocks[bname]["keep"], bool))
            if sub.size < 100:
                calib["%s|%s" % (bname, regime)] = {"n": int(sub.size), "insufficient": True}
                continue
            h = np.asarray(hits[k], np.float64)[sub]
            band = random_abstain_band(h, RATES, n_draws, MASTER_SEED + 71)
            cs = confs[(bname, regime)]
            sigvec = {s: cs[s][sub] for s in SIGNALS}
            sigvec.update(conf_floor_vectors(bname, regime, sub, MASTER_SEED + 73, h))
            per: Dict[str, Dict] = {}
            for sname, cv in sigvec.items():
                cv = np.asarray(cv, np.float64)
                ok = np.isfinite(cv)
                if ok.sum() < 100:
                    per[sname] = {"n_finite": int(ok.sum()), "insufficient": True}
                    continue
                entry = {
                    "AUROC": auroc_with_ci(cv, h, None, n_boot, MASTER_SEED + 101),
                    "AUROC_FREQUENCY_STRATIFIED": auroc_with_ci(
                        cv, h, strata_all[sub], n_boot, MASTER_SEED + 103),
                    "curve": rate_curve(h, cv, band, RATES, MASTER_SEED + 107),
                    "spearman_rho_with_query_logfreq": _r(_spearman(cv, q_logfreq[sub])),
                }
                if sname in CONF_FLOORS[:2]:
                    # FLOORS GET THEIR BEST ORIENTATION AND WE DO NOT.
                    entry["AUROC_reversed_policy"] = auroc_with_ci(-cv, h, None, n_boot,
                                                                  MASTER_SEED + 101)
                    entry["curve_reversed_policy"] = rate_curve(h, -cv, band, RATES,
                                                                MASTER_SEED + 107)
                    entry["note"] = ("a FLOOR is reported at whichever sign of the policy is "
                                     "stronger, because a floor should be as strong as it can be. "
                                     "Our own signals are reported at their pre-registered sign.")
                if sname == PRIMARY_SIGNAL:
                    entry["SEED_REPLICATES"] = [
                        {"seed": int(s),
                         "AUROC": auroc_with_ci(cv, h, None, max(n_boot // 2, 500), s)["auroc"],
                         "n_rates_beating_random": rate_curve(
                             h, cv, random_abstain_band(h, RATES, max(n_draws // 2, 250), s),
                             RATES, s)["n_rates_beating_random"]}
                        for s in RNG_SEEDS]
                    hh = half[sub]
                    entry["SPLIT_HALF"] = {
                        "half_1": auroc_with_ci(cv[hh], h[hh], None, max(n_boot // 2, 500),
                                                MASTER_SEED + 111),
                        "half_2": auroc_with_ci(cv[~hh], h[~hh], None, max(n_boot // 2, 500),
                                                MASTER_SEED + 113)}
                per[sname] = entry
            # THE STRONGEST NO-UNDERSTANDING CONFIDENCE POLICY IN THIS BLOCK, at its best
            # orientation, and OUR PRIMARY SIGNAL MEASURED AGAINST IT, PAIRED. A random-abstain
            # band is the weakest floor a calibration claim faces; this is the strongest one we
            # can build without understanding, and the standing rule is that a gate is a margin
            # over the STRONGEST such floor, never over the most convenient one.
            best_floor, best_v, best_au = None, -1.0, None
            for fname in CONF_FLOORS:
                e = per.get(fname, {})
                for fld, orient in (("AUROC", 1.0), ("AUROC_reversed_policy", -1.0)):
                    a = (e.get(fld) or {}).get("auroc")
                    if a is not None and a > best_v:
                        best_floor, best_v, best_au = (fname, orient), a, e.get(fld)
            head = {}
            if best_floor is not None:
                fv = np.asarray(sigvec[best_floor[0]], np.float64) * best_floor[1]
                head = {
                    "strongest_confidence_floor": best_floor[0],
                    "orientation": "as-is" if best_floor[1] > 0 else "REVERSED (floors get their "
                                   "best orientation; our signals do not)",
                    "floor_AUROC": _r(best_v),
                    "PRIMARY_MINUS_FLOOR_paired": paired_auroc_delta(
                        np.asarray(sigvec[PRIMARY_SIGNAL], np.float64), h, fv, h, n_boot,
                        MASTER_SEED + 141),
                    "rule": "a calibration claim clears its bar only if this delta is CI-separated "
                            "ABOVE 0. Beating the random-abstain band is necessary and NOT "
                            "sufficient."}
            calib["%s|%s" % (bname, regime)] = {
                "n": int(sub.size), "base_accuracy": _r(float(h.mean())),
                "n_effective_positive_items": _r(float(h.sum()), 2),
                "chance": _r(blocks[bname]["chance"], 6),
                "CALIBRATION_KA_PASSES": bool(
                    (per.get(CALIB_KA, {}).get("AUROC", {}) or {}).get("band_vs_0.5") == "ABOVE"),
                "CALIBRATION_NULLS_PASS": bool(
                    (per.get("X4_CONSTANT", {}).get("curve", {}) or {}).get(
                        "n_rates_beating_random", 99) <= 2),
                "what": blocks[bname]["what"], "per_signal": per,
                "PRIMARY_vs_STRONGEST_CONFIDENCE_FLOOR": head,
                "frac_argmax_is_the_target_word": _r(float(
                    (confs[(bname, regime)]["_argmax_index"][sub] == self_idx[sub]).mean()))}
            print("[calib] %s|%s n=%d base=%.4f primary_AUROC=%s beats=%s  %.0fs" % (
                bname, regime, sub.size, float(h.mean()),
                per.get(PRIMARY_SIGNAL, {}).get("AUROC", {}).get("auroc"),
                per.get(PRIMARY_SIGNAL, {}).get("curve", {}).get("n_rates_beating_random"),
                time.time() - t0), flush=True)
    rep["CALIBRATION_BY_BLOCK"] = calib

    # ---- THE MECHANISM DISCRIMINATOR: does the margin only ever predict "the argmax is L"? ------
    kB = ("B_POOLSELF_GOLD_SELF_PLUS_SYN", "PARTIAL_CUE", "R0_CTX_DENSE_our_read_out")
    mech: Dict = {}
    if kB in hits:
        sub = np.flatnonzero(scored[kB] & POP_COMMON)
        hB = np.asarray(hits[kB], np.float64)[sub]
        am = confs[("B_POOLSELF_GOLD_SELF_PLUS_SYN", "PARTIAL_CUE")]["_argmax_index"][sub]
        is_L = (am == self_idx[sub])
        h_sub_only = hB * (~is_L).astype(np.float64)
        cv = confs[("B_POOLSELF_GOLD_SELF_PLUS_SYN", "PARTIAL_CUE")][PRIMARY_SIGNAL][sub]
        mech = {
            "construction": "on block B (L eligible, gold = L or a synonym) the hit is split. "
                            "hit_SUBSTITUTION_ONLY = a gold was returned AND the argmax was NOT L. "
                            "If the margin only ever predicted 'the argmax is L', its AUROC against "
                            "THAT label sits at or below 0.5.",
            "frac_argmax_is_L": _r(float(is_L.mean())),
            "frac_of_all_hits_that_are_argmax_equals_L": _r(
                float((hB * is_L).sum() / max(hB.sum(), 1e-9))),
            "AUROC_vs_ANY_hit": auroc_with_ci(cv, hB, None, n_boot, MASTER_SEED + 121),
            "AUROC_vs_SUBSTITUTION_ONLY_hit": auroc_with_ci(cv, h_sub_only, None, n_boot,
                                                            MASTER_SEED + 123),
            "AUROC_vs_ARGMAX_IS_L": auroc_with_ci(cv, is_L.astype(np.float64), None, n_boot,
                                                  MASTER_SEED + 125)}
    rep["MECHANISM_DISCRIMINATOR_argmax_is_L"] = mech

    # ---- THE DISSOCIATION, PAIRED, ON ONE POPULATION --------------------------------------------
    def _pair(b1: str, b2: str, sig: str) -> Dict:
        k1 = (b1, "PARTIAL_CUE", "R0_CTX_DENSE_our_read_out")
        k2 = (b2, "PARTIAL_CUE", "R0_CTX_DENSE_our_read_out")
        if k1 not in hits or k2 not in hits:
            return {}
        m = scored[k1] & scored[k2] & POP_COMMON
        sub = np.flatnonzero(m)
        return paired_auroc_delta(confs[(b1, "PARTIAL_CUE")][sig][sub],
                                  np.asarray(hits[k1], np.float64)[sub],
                                  confs[(b2, "PARTIAL_CUE")][sig][sub],
                                  np.asarray(hits[k2], np.float64)[sub], n_boot, MASTER_SEED + 131)

    contrasts = {
        "THE_SOURCES_HEADLINE__A_naming_MINUS_E_substituting": _pair(
            "A_POOLSELF_GOLD_EXACT", "E_POOLMASK_GOLD_SYN", PRIMARY_SIGNAL),
        "CRITERION_AXIS__A_MINUS_B_same_pool_same_scores": _pair(
            "A_POOLSELF_GOLD_EXACT", "B_POOLSELF_GOLD_SELF_PLUS_SYN", PRIMARY_SIGNAL),
        "CRITERION_AXIS__A_MINUS_C_same_pool_same_scores": _pair(
            "A_POOLSELF_GOLD_EXACT", "C_POOLSELF_GOLD_SELF_PLUS_LANDED", PRIMARY_SIGNAL),
        "POOL_AXIS__D_MINUS_E_same_gold_family": _pair(
            "D_POOLSELF_GOLD_SYNONLY", "E_POOLMASK_GOLD_SYN", PRIMARY_SIGNAL),
        "SETMARGIN_ON_THE_SUBSTITUTION_BLOCK__E_setmargin_MINUS_E_top1margin": None,
    }
    kE = ("E_POOLMASK_GOLD_SYN", "PARTIAL_CUE", "R0_CTX_DENSE_our_read_out")
    if kE in hits:
        sub = np.flatnonzero(scored[kE] & POP_COMMON)
        hE = np.asarray(hits[kE], np.float64)[sub]
        cE = confs[("E_POOLMASK_GOLD_SYN", "PARTIAL_CUE")]
        contrasts["SETMARGIN_ON_THE_SUBSTITUTION_BLOCK__E_setmargin_MINUS_E_top1margin"] = (
            paired_auroc_delta(cE["C6_SETMARGIN_M%d" % M_NBR][sub], hE,
                               cE[PRIMARY_SIGNAL][sub], hE, n_boot, MASTER_SEED + 133))
    rep["CONTRASTS_PAIRED_ON_POP_COMMON"] = {
        "rule": "every contrast below is computed on ONE item ordering over POP_COMMON with the "
                "SAME bootstrap resample indices for both sides, so the difference is genuinely "
                "paired and no number crosses a population, a pool or a criterion.",
        "contrasts": contrasts}

    # ---- VERDICT, computed from the measured numbers, not written in advance ---------------------
    def _g(b, sig=PRIMARY_SIGNAL, field="AUROC"):
        return (calib.get("%s|PARTIAL_CUE" % b, {}).get("per_signal", {})
                .get(sig, {}).get(field, {}) or {})

    A_au, A_st = _g("A_POOLSELF_GOLD_EXACT"), _g("A_POOLSELF_GOLD_EXACT",
                                                 field="AUROC_FREQUENCY_STRATIFIED")
    A_cv = (calib.get("A_POOLSELF_GOLD_EXACT|PARTIAL_CUE", {}).get("per_signal", {})
            .get(PRIMARY_SIGNAL, {}).get("curve", {}) or {})
    E_au, F_au = _g("E_POOLMASK_GOLD_SYN"), _g("F_POOLMASK_GOLD_LANDED")
    sh = (calib.get("A_POOLSELF_GOLD_EXACT|PARTIAL_CUE", {}).get("per_signal", {})
          .get(PRIMARY_SIGNAL, {}).get("SPLIT_HALF", {}) or {})
    naming_fires = (A_au.get("band_vs_0.5") == "ABOVE"
                    and A_cv.get("n_rates_beating_random", 0) >= 8)
    strat_holds = A_st.get("band_vs_0.5") == "ABOVE"
    halves_agree = (sh.get("half_1", {}).get("auroc") or 0) > 0.5 and (
        sh.get("half_2", {}).get("auroc") or 0) > 0.5
    # AN ABSENCE CLAIM ONLY COUNTS FROM AN ADEQUATELY POWERED BLOCK. The tight-synonym blocks
    # (D and E) carry ~5 effective positive items; their intervals span half the range, so
    # "NOT_SEPARATED" there is no measurement. Only F (landed criterion, masked pool) and the
    # landed instrument on its own population carry enough positives to support a null.
    powered_subs = {bn: _g(bn) for bn in ("F_POOLMASK_GOLD_LANDED", "REG_LANDED_POPALL")}
    powered_subs = {k: v for k, v in powered_subs.items() if v and not v.get("UNDERPOWERED")}
    sub_silent = bool(powered_subs) and all(v.get("band_vs_0.5") != "ABOVE"
                                            for v in powered_subs.values())
    underpowered_subs = {bn: (_g(bn).get("UNDERPOWERED"), _g(bn).get("ci95"))
                         for bn in ("D_POOLSELF_GOLD_SYNONLY", "E_POOLMASK_GOLD_SYN")}
    dissoc = (contrasts.get("THE_SOURCES_HEADLINE__A_naming_MINUS_E_substituting") or {}
              ).get("band") == "ABOVE"
    crit_flat = ((contrasts.get("CRITERION_AXIS__A_MINUS_B_same_pool_same_scores") or {}
                  ).get("band") == "NOT_SEPARATED")
    pool_flat = ((contrasts.get("POOL_AXIS__D_MINUS_E_same_gold_family") or {}
                  ).get("band") == "NOT_SEPARATED")
    floor_head = (calib.get("A_POOLSELF_GOLD_EXACT|PARTIAL_CUE", {})
                  .get("PRIMARY_vs_STRONGEST_CONFIDENCE_FLOOR", {}) or {})
    clears_conf_floor = (floor_head.get("PRIMARY_MINUS_FLOOR_paired", {}) or {}
                         ).get("band") == "ABOVE"
    sub_only = (mech.get("AUROC_vs_SUBSTITUTION_ONLY_hit") or {})
    argmax_lab = (mech.get("AUROC_vs_ARGMAX_IS_L") or {})
    mech_is_argmax = bool(argmax_lab.get("band_vs_0.5") == "ABOVE"
                          and sub_only.get("band_vs_0.5") != "ABOVE")
    if not naming_fires:
        verdict = "FAILS_TO_REPLICATE"
    elif not strat_holds:
        verdict = "FREQUENCY_EXPLAINED"
    elif naming_fires and strat_holds and halves_agree:
        base = "REPLICATES"
        if mech_is_argmax:
            base += "__MECHANISM_IS_ARGMAX_IS_THE_TARGET_WORD"
        elif crit_flat and not pool_flat:
            base += "__MECHANISM_IS_THE_POOL"
        elif not crit_flat:
            base += "__MECHANISM_IS_THE_CRITERION"
        else:
            base += "__MECHANISM_UNRESOLVED"
        verdict = base + ("" if clears_conf_floor
                          else "__BUT_DOES_NOT_CLEAR_ITS_STRONGEST_CONFIDENCE_FLOOR")
    else:
        verdict = "MIDDLE_BAND"
    rep["PRE_REGISTERED_BANDS"] = {
        "PRIMARY": "%s on R0_CTX_DENSE_our_read_out, OPEN pool, PARTIAL_CUE" % PRIMARY_SIGNAL,
        "REPLICATES": "block A AUROC CI-ABOVE 0.5 AND frequency-stratified AUROC CI-ABOVE 0.5 AND "
                      ">= 8 of 14 rates beat the random band AND both split-halves agree in "
                      "direction AND blocks E and F NOT CI-above 0.5 AND the paired A-minus-E "
                      "delta CI-ABOVE 0.",
        "FAILS_TO_REPLICATE": "block A AUROC not CI-above 0.5, or E/F show comparable selectivity.",
        "FREQUENCY_EXPLAINED": "block A raw AUROC separates but the stratified one does not.",
        "MECHANISM_IS_THE_POOL": "the criterion axis (A minus B) is flat while the pool axis is not.",
        "MIDDLE_BAND": "anything else, said plainly.",
        "NOT_A_MEETS_BAR_CLAIM": "no outcome here is an accuracy claim. hit@1 is unchanged."}
    rep["PRE_REGISTERED_BANDS"]["ADDED_AFTER_THE_SMOKE_GATE_AND_BEFORE_THE_FULL_RUN"] = (
        "TWO amendments, both made because the smoke exposed a defect in the ORIGINAL pre-reg and "
        "both stated rather than folded in silently. (1) A POWER GATE: the tight-synonym blocks "
        "carry about five effective positive items and 95% intervals wider than half the range, so "
        "their 'NOT_SEPARATED' cannot support the absence half of the pre-registered band. The "
        "absence claim is now read only from ADEQUATELY POWERED substitution blocks. This also "
        "means the SOURCE CELL'S synonym-criterion null (its 0 of 8 rates, same ~0.002 base) was "
        "UNDERPOWERED and should not have been read as a null either. (2) A FLOOR GATE: the "
        "primary signal is now measured PAIRED against the STRONGEST no-understanding confidence "
        "policy at its best orientation, not only against the random-abstain band, because the "
        "smoke showed a reversed query-frequency policy scoring well above our margin on the "
        "naming block. Beating the random band is necessary and NOT sufficient.")
    rep["VERDICT_INPUTS"] = {"naming_fires": bool(naming_fires), "stratified_holds": bool(strat_holds),
                             "split_halves_agree": bool(halves_agree),
                             "substitution_silent_on_ADEQUATELY_POWERED_blocks": bool(sub_silent),
                             "powered_substitution_blocks_used": sorted(powered_subs),
                             "substitution_blocks_EXCLUDED_for_no_power": underpowered_subs,
                             "paired_dissociation_vs_the_underpowered_E": bool(dissoc),
                             "criterion_axis_flat": bool(crit_flat),
                             "pool_axis_flat": bool(pool_flat),
                             "mechanism_is_argmax_is_the_target_word": bool(mech_is_argmax),
                             "clears_its_strongest_confidence_floor": bool(clears_conf_floor)}
    rep["verdict"] = verdict
    rep["verdict_msg"] = (
        "%s. NAMING block A (L eligible, gold={L}, POP_COMMON n=%d, PARTIAL_CUE): AUROC %s %s, "
        "frequency-stratified %s %s, beats the random-abstain band at %s of %s rates, base %s. "
        "BUT the strongest no-understanding CONFIDENCE policy in that same block (%s) scores %s and "
        "our paired margin over it is %s %s. MECHANISM: %s%% of block B's hits are the target word "
        "itself; AUROC against 'the argmax is the target word' is %s %s while AUROC against "
        "SUBSTITUTION-ONLY hits is %s %s. On the ADEQUATELY POWERED substitution block "
        "(landed criterion, landed instrument) AUROC is %s %s, beating the band at %s of %s rates. "
        "NO ACCURACY CLAIM AND NO MEETS_BAR CLAIM -- hit@1 is unchanged and remains below the "
        "floor set."
        % (verdict, int(POP_COMMON.sum()), A_au.get("auroc"), A_au.get("band_vs_0.5"),
           A_st.get("auroc"), A_st.get("band_vs_0.5"), A_cv.get("n_rates_beating_random"),
           len(RATES), A_cv.get("accuracy_at_full_response"),
           floor_head.get("strongest_confidence_floor"), floor_head.get("floor_AUROC"),
           (floor_head.get("PRIMARY_MINUS_FLOOR_paired", {}) or {}).get("delta"),
           (floor_head.get("PRIMARY_MINUS_FLOOR_paired", {}) or {}).get("band"),
           _r(100.0 * (mech.get("frac_of_all_hits_that_are_argmax_equals_L") or 0.0), 1),
           argmax_lab.get("auroc"), argmax_lab.get("band_vs_0.5"),
           sub_only.get("auroc"), sub_only.get("band_vs_0.5"),
           (_g("REG_LANDED_POPALL") or {}).get("auroc"),
           (_g("REG_LANDED_POPALL") or {}).get("band_vs_0.5"),
           ((calib.get("REG_LANDED_POPALL|PARTIAL_CUE", {}).get("per_signal", {})
             .get(PRIMARY_SIGNAL, {}).get("curve", {}) or {}).get("n_rates_beating_random")),
           len(RATES)))
    rep["units_recorded"] = len(load_units(OUT_DIR))
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, np.float64); b = np.asarray(b, np.float64)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 10:
        return float("nan")
    ra = np.argsort(np.argsort(a[m])).astype(np.float64)
    rb = np.argsort(np.argsort(b[m])).astype(np.float64)
    if ra.std() < 1e-12 or rb.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    with open(os.path.join(OUT_DIR, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(a.grid)
        _atomic_json(os.path.join(OUT_DIR, "metrics.json"), rep)
        print("WROTE " + os.path.join(OUT_DIR, "metrics.json"), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(OUT_DIR, "_crash_diagnostic.json"),
                     {"error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
