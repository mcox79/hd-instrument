"""exp_predictive_coding_write_gate_dissociation_v1 -- DOES A PREDICTION-ERROR-GATED WRITE RULE
PRODUCE SUBSTITUTABILITY?

THIS IS A MEASUREMENT OF MACHINERY WE ALREADY OWN, NOT A NEW BUILD. Three things this cell reuses
verbatim and never reimplements: (1) `hdlab/predictive_coding.py` -- the LEARNER MODULE (Rao-Ballard
predict/residual/threshold-gate/proportional-gate), landed 2026-07-02, never scored on the
dissociation instrument; (2) `experiments/exp_surprise_weighted_update_v1.py`'s observation stream
(`build_obs_stream`) -- the exact (lemma, context_vector) sequence `ConceptSpace.observe` consumes,
already cached at `scratch/night/obs_stream_v1.npz` (153,352 occurrences, 5,491 anchors, d=256),
never re-tokenised; (3) `experiments/exp_dissociation_score_instrument_v1.py`'s (DSI) licensed
matched-pair population, scorer (`auc_of`/`auc_bootstrap`) and cached SCORES, never rebuilt.

THE QUESTION (plan sec 6.19, `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md`). 6.18 found EVERY
unsupervised arm this programme has built sits below chance on the dissociation AUC (0.02-0.07)
while a supervised low-rank reweighting of the SAME counts reads 0.8629 under group-disjoint CV --
the missing thing is a LEARNING SIGNAL, not information or representation capacity. The
MISSING-LEARNING rule says REUSE/EXPAND the learner module, never build a parallel one. We own a
prediction-error-gated write rule (`hdlab/predictive_coding.py`, exercised by a landed cell family
scored on a DIFFERENT `gap`/`ck` metric, HARD_PASS there, UNVERIFIED here -- see NUMBER DISCIPLINE
below) that has never been scored on THIS instrument. Does a store written under it read above 0.5?

=================================================================================================
PRIOR-WORK CHECK (mandatory, substrate-KB concept-query BEFORE authoring). Ran:
`tools/director_kb_query.py --schema-version v2 --tau 0.15 --k 5 "predictive coding write gate
surprise gated accumulation dissociation instrument substitutability learning signal"`.
confidence=0.3467 (above the cosine>0.30 read-the-top-2 threshold). Rank 1 (cosine=0.3467,
`notes/research_drill_rmt_beyond_free_probability_2x_2026-06-11.md`) and rank 2 (cosine=0.3418,
a training-speedup note on activation checkpointing) are off-topic vocabulary-overlap false
positives -- neither concerns write rules, prediction error, or the dissociation instrument.
Genuinely on-topic: rank 5 (cosine=0.3301, `notes/research_exogenous_referent_grounding_predictive_
coding_2026-07-09.md`) proposes reusing `predictive_coding.py`'s `residual_magnitude`/
`proportional_gate` for a DIFFERENT, much larger, NEVER-BUILT architecture -- a dedicated `W_pred`
second weight matrix for cross-referent self-play grounding. That note's S2 is a design proposal,
not an implementation, and answers a different question (referent grounding for self-play) than
this cell (does gating `ConceptSpace.observe`'s existing write rule produce substitutability, scored
on the licensed AUC instrument). NOT a rediscovery. Builds on the same module the note also
identifies as the right reuse target, applied to the narrower, already-dispatched question in plan
sec 6.19.

=================================================================================================
NUMBER DISCIPLINE (the trap this project's own docs name, plan sec 6.19). The landed predictive-
coding cell family (`exp_substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_
v1/v2/_v3_D_competitive_hebbian_only/_stress_test_cell1`, 2026-07-02) reported a HARD_PASS (v2:
PRED-only gap 0.566 vs HYBRID 0.517) and a MIDDLE_BAND stress test (v3d ck 0.492 vs softmax 0.461)
on a `gap`/`ck` metric, on a DIFFERENT population. Those numbers say NOTHING about the dissociation
AUC and are cited here for DESIGN ONLY -- they are UNVERIFIED ON THIS INSTRUMENT and are never
imported as evidence below.

=================================================================================================
WHY `predict()` DOES NOT APPLY, AND WHAT DOES (stated precisely per the dispatch brief's "if it
genuinely cannot serve, say precisely why before writing any replacement" instruction).
`predictive_coding.predict(W, key)` assumes a trained HETERO-ASSOCIATIVE matrix W (key -> value
recall via `sign(W @ key)`), which is the landed cell family's task structure (bind a cue to a
retrievable target). `ConceptSpace.observe` has no such structure: `self._sums[lemma] += ctx_vec` is
a single running SELF-accumulator -- a lemma's own profile predicting itself, not a separate key
projecting through a learned matrix. The natural Rao-Ballard reading still applies without `predict`:
the generative model's "current best estimate of the input" IS the lemma's own running accumulated
direction (`acc / ||acc||`), so THAT is used as `predicted` and the incoming occurrence vector as
`observed`, fed directly into the UNCHANGED `residual_magnitude` / `threshold_gate` /
`proportional_gate` calls. `gated_write`'s own outer-product line (`W += strength * outer(value,
key)`) likewise does not apply (no key/value split); its `WriteDecision.write_strength` CONTRACT is
reused exactly -- `acc += write_strength * observed` -- which is the same 0-skip / >0-scaled-add
semantics minus the hetero-associative binding `gated_write` layers on top. This is a scoped
adaptation of the module's own generative-estimate concept to a simpler accumulator, not a
reimplementation of `residual_magnitude`, `threshold_gate`, or `proportional_gate`, all three of
which are called verbatim, unmodified, below.

=================================================================================================
ARMS, identical population / scorer / gold, all in the SAME representational space as the live
store (`CTS.load_cache()["mat"]`, d=256 -- verified byte-identical cache path + MASTER_SEED to
`exp_task_degeneracy_v1`'s `mat_landed`, so `SWU.build_obs_stream()`'s recorded occurrences sum to
the live store exactly, per the STREAM regression gate below):
  A0_INCUMBENT          rebuilt via plain summation of the cached observation stream (verified
                        against the live store and DSI's cached INCUMBENT_LIVE_STORE AUC 0.0710).
  P1_PREDICTION_GATED   `threshold_gate(observed=occurrence, predicted=running_acc_direction,
                        threshold=T)`: write full-strength iff residual_mag >= T. T swept at the
                        MEASURED surprise distribution's own p25/p50/p75/p90 (never a fixed
                        constant blind to the distribution's actual range) -- never adopted as a
                        single value.
  P2_PREDICTION_WEIGHTED `proportional_gate`: write at strength = clipped residual magnitude,
                        every occurrence contributes, weighted continuously instead of thresholded.
  N1_RANDOM_GATE        THE CONTROL THAT CARRIES THE CLAIM. Per threshold T, per lemma: accept
                        EXACTLY the same COUNT of occurrences P1_T accepted for that lemma, chosen
                        uniformly at random (same machinery, same per-lemma effective depth, gate
                        fires at random). If P1 does not beat its OWN rate-matched N1 CI-separated,
                        the effect is the gating RATE, not prediction error.
  N2_ANTI_GATE           `threshold_gate`'s own `residual_mag` field, comparison INVERTED: accept
                        iff residual_mag < T (write the LEAST surprising occurrences). If P1 and N2
                        read the same, the residual is not carrying direction.
  K1 / N0 / four floors  DSI's own cached arms, reused bit-for-bit via the regression gate.

=================================================================================================
STOP-IF (evaluated in this order):
  (v)   any of DSI's 8 regression checks, or the STREAM regression gate, fails -> raise SystemExit,
        INSTRUMENT_NOT_LICENSED, publish nothing but the gate failure (checked FIRST, not last).
  (iii) the surprise (residual_mag) distribution on THIS population (the 617 matched-pair member
        words) is degenerate (PRE-REGISTERED test: median >= 0.80 AND (p90-p10) <= 0.20, the same
        shape `exp_surprise_weighted_update_v1` measured on a different population: median 0.875,
        p10=0.6525, p90=1.0128) -> report the distribution plainly, name the fix (separate predictor
        / warm start), and flag every downstream AUC comparison as NOT a fair mechanism test.
  (i)   P1 (best threshold) CI-separated ABOVE 0.5 AND CI-separated above its rate-matched N1 ->
        the first store this programme has ever built that encodes substitutability; report level,
        margin, composition, controls together.
  (ii)  P1 beats A0 (0.0710) CI-separated but NOT its rate-matched N1 CI-separated -> the gain is
        the gating RATE, not prediction error; report as such, claim no mechanism.
  (iv)  P1 ties A0 (not CI-separated) with a healthy surprise distribution -> real negative about
        the supervision hypothesis: prediction error as a write gate does not produce
        substitutability.
Supplementary (not a STOP-IF, reported alongside): P1 vs N2 (direction-carrying check), P2's AUC.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: STREAM_A0, SURPRISE_DIST, and each arm's store-build as separate
#   tools.exp_checkpoint units so a kill loses at most one arm, not the whole run
# - discriminator survives scale: FULL runs the real 617-word/242-pair-per-cell population; the
#   --grid reduced smoke uses a REAL smaller matched-pair subset (DSI/CAP convention: [:40]), not a
#   synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses DSI's licensed instrument + SWU's cached
#   observation stream unmodified; only the accumulation RULE is new, which is the thing under test)
# - progress_logging: print_flush_true (every phase prints a flushed line, Sec 17)
# - baseline_in_band: n/a -- licensing-gate + dissociation-AUC instrument, not a 0.05-0.95-band
#   baseline cell; declared explicitly
# - crlb_floor_computed: n/a -- an AUC dissociation measurement is not a capacity sweep; declared
#   explicitly
# - tie conventions: DSI's AUC scorer (Mann-Whitney rank-sum) has ONE convention throughout the
#   project (no hit@1 "optimistic/conservative" split applies to a continuous-score AUC instrument);
#   declared explicitly rather than silently omitting an inapplicable requirement.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. NOTHING under
hdlab/ is modified. `data/foundation/** ` is never opened. Writes only under
data/exp_predictive_coding_write_gate_dissociation_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/DSI/CTS/SWU/predictive_coding next -- flushed so a slow import is "
      "never mistaken for a hang)", flush=True)

import argparse
import hashlib
import sys
import time
import traceback
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI              # noqa: E402  READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                   # noqa: E402  READ ONLY
import experiments.exp_surprise_weighted_update_v1 as SWU                   # noqa: E402  READ ONLY
import hdlab.predictive_coding as PC                                        # noqa: E402  THE LEARNER
from experiments._seed_checkpoint import get_output_dir, write_metrics      # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "predictive_coding_write_gate_dissociation_v1"
CODE_VERSION = "v1.1"  # v1.0's smoke run correctly caught a real bug: the STREAM regression gate
                       # compared a SMOKE-truncated ([:40]/[:40]) rebuilt-A0 AUC against DSI's
                       # FULL-population (242/242) cached 0.0710 -- a population mismatch, not a
                       # construction defect (mean_cos was already 1.0, the real geometric check).
                       # v1.1 slices DSI's own cached score arrays to the SAME truncation before
                       # comparing. Bumped so no stale (bad) smoke checkpoint silently resumes.
FINDINGS = "notes/predictive_coding_write_gate_dissociation_2026-08-18.md"

DSI_CODE_VERSION = "v1.7"          # the LICENSED instrument version this cell reproduces + reuses
DSI_GRID = "full"
DSI_OUT_DIR = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
QUANTILES = (0.5,) if SMOKE else (0.25, 0.5, 0.75, 0.9)
DEGENERACY_MEDIAN_MIN = 0.80        # PRE-REGISTERED, before this run's own numbers are seen
DEGENERACY_IQR90_10_MAX = 0.20      # (p90 - p10) <= this AND median >= above -> degenerate

# EXPECTED regression-gate values -- MEASURED@notes/dissociation_score_instrument_2026-08-18.md,
# IDENTICAL dict to exp_corpus_capacity_ppmi_svd_ceiling_v1's own (that cell's own regression gate
# licensed cleanly against these same 8 values). Duplicated here rather than imported so this cell
# is self-contained and does not depend on CAP's own argv-parsing side effects at import time.
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
REGRESSION_TOL = 0.0005
STREAM_COS_GATE = 0.9999


def _digest(v: Sequence[float]) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# REGRESSION GATE -- DSI's licensed floors/K1/N0/incumbent, reproduced from its OWN cached SCORES,
# bit-for-bit, via DSI's OWN auc_bootstrap code. EXITS ON FAILURE (STOP-IF v, checked first).
# =================================================================================================
def dsi_regression_gate() -> Dict:
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
        raise SystemExit("INSTRUMENT_NOT_LICENSED -- DSI regression gate FAILED: %r" %
                         {k: v for k, v in checks.items() if not v["PASS"]})
    print("[gate] DSI INSTRUMENT_LICENSED = True (all %d checks pass)" % len(checks), flush=True)
    return {"matchedP": matchedP, "matchedS": matchedS, "arm_scores": arm_scores,
           "gate_report": gate_report}


# =================================================================================================
# STORE CONSTRUCTION -- reuses SWU.build_obs_stream() verbatim (never re-tokenised) and
# hdlab.predictive_coding's residual_magnitude / threshold_gate / proportional_gate verbatim.
# =================================================================================================
def _predicted_direction(acc: np.ndarray) -> np.ndarray:
    """The running accumulator's own normalised direction -- the generative estimate `predict()`
    would supply if this were a hetero-associative W, adapted to a self-accumulator (see module
    docstring)."""
    na = float(np.linalg.norm(acc))
    if na <= 1e-12:
        return np.zeros_like(acc)
    return acc / na


def build_store(obs: Dict, target_words: Sequence[str], rule: str, param: float,
               rng: np.random.Generator, n_accept_map: Optional[Dict[str, int]] = None
               ) -> Tuple[Dict[str, np.ndarray], Dict]:
    """One arm's {word: raw_accumulated_vector} over `target_words`, built from the SAME cached
    observation stream, differing ONLY in the accumulation rule. `rule` in {A0_UNIFORM, P1_GATE,
    P2_WEIGHTED, N1_RANDOM, N2_ANTI_GATE}. `n_accept_map` (word -> int) is REQUIRED for N1_RANDOM
    (the per-lemma accept COUNT copied from a prior P1 run at the same threshold)."""
    lemmas = obs["lemmas"]
    pos = {w: i for i, w in enumerate(lemmas)}
    V, starts, lens = obs["obs_vec"], obs["starts"], obs["lens"]
    d = V.shape[1]
    store: Dict[str, np.ndarray] = {}
    n_accept_by_word: Dict[str, int] = {}
    n_tok = 0
    for w in target_words:
        k = pos.get(w)
        if k is None or lens[k] == 0:
            store[w] = np.zeros(d, dtype=np.float64)
            n_accept_by_word[w] = 0
            continue
        s0, n = int(starts[k]), int(lens[k])
        Vi = V[s0:s0 + n].astype(np.float64)
        n_tok += n
        if rule == "A0_UNIFORM":
            store[w] = Vi.sum(axis=0)
            n_accept_by_word[w] = n
            continue
        if rule == "N1_RANDOM":
            k_accept = int((n_accept_map or {}).get(w, 0))
            k_accept = max(0, min(k_accept, n))
            if k_accept == 0:
                store[w] = np.zeros(d, dtype=np.float64)
            else:
                sel = np.sort(rng.permutation(n)[:k_accept])
                store[w] = Vi[sel].sum(axis=0)
            n_accept_by_word[w] = k_accept
            continue
        if rule == "P2_WEIGHTED":
            acc = np.zeros(d, dtype=np.float64)
            n_acc = 0
            for i in range(n):
                v = Vi[i]
                pred = _predicted_direction(acc)
                dec = PC.proportional_gate(v, pred)   # verbatim module call
                if not dec.skipped:
                    acc = acc + dec.write_strength * v
                    n_acc += 1
            store[w] = acc
            n_accept_by_word[w] = n_acc
            continue
        if rule in ("P1_GATE", "N2_ANTI_GATE"):
            acc = np.zeros(d, dtype=np.float64)
            n_acc = 0
            for i in range(n):
                v = Vi[i]
                pred = _predicted_direction(acc)
                dec = PC.threshold_gate(v, pred, threshold=param)   # verbatim module call
                if rule == "P1_GATE":
                    accept = not dec.skipped                        # write iff residual_mag >= T
                else:
                    accept = dec.residual_mag < param                # INVERTED: write iff < T
                if accept:
                    acc = acc + v
                    n_acc += 1
            store[w] = acc
            n_accept_by_word[w] = n_acc
            continue
        raise ValueError("unknown rule %r" % rule)
    diag = {"rule": rule, "param": param, "n_words": len(target_words),
           "n_tokens_available": int(n_tok), "n_tokens_accepted": int(sum(n_accept_by_word.values())),
           "acceptance_rate": round(sum(n_accept_by_word.values()) / max(1, n_tok), 4),
           "n_accept_by_word": n_accept_by_word}
    return store, diag


def measure_surprise_distribution(obs: Dict, target_words: Sequence[str]) -> Dict:
    """Per-occurrence residual_mag against the UNGATED (accept-all / A0) running accumulator, for
    EVERY occurrence of EVERY word in `target_words` -- the FULL distribution (not a sample), using
    `hdlab.predictive_coding.residual_magnitude` verbatim. This is the pre-registered diagnostic
    that must be reported BEFORE any AUC (STOP-IF iii)."""
    lemmas = obs["lemmas"]
    pos = {w: i for i, w in enumerate(lemmas)}
    V, starts, lens = obs["obs_vec"], obs["starts"], obs["lens"]
    vals: List[float] = []
    for w in target_words:
        k = pos.get(w)
        if k is None or lens[k] == 0:
            continue
        s0, n = int(starts[k]), int(lens[k])
        Vi = V[s0:s0 + n].astype(np.float64)
        acc = np.zeros(Vi.shape[1], dtype=np.float64)
        for i in range(n):
            v = Vi[i]
            pred = _predicted_direction(acc)
            vals.append(PC.residual_magnitude(v, pred))   # verbatim module call
            acc = acc + v
    arr = np.asarray(vals, dtype=np.float64)
    if arr.size == 0:
        return {"n": 0}
    out = {"n": int(arr.size), "mean": round(float(arr.mean()), 4)}
    for q in (10, 25, 50, 75, 90):
        out["p%d" % q] = round(float(np.percentile(arr, q)), 4)
    out["DEGENERACY_TEST"] = {
        "rule": "median >= %.2f AND (p90-p10) <= %.2f" % (DEGENERACY_MEDIAN_MIN, DEGENERACY_IQR90_10_MAX),
        "median": out["p50"], "p90_minus_p10": round(out["p90"] - out["p10"], 4),
        "SURPRISE_DEGENERATE": bool(out["p50"] >= DEGENERACY_MEDIAN_MIN
                                    and (out["p90"] - out["p10"]) <= DEGENERACY_IQR90_10_MAX),
        "compare_to_exp_surprise_weighted_update_v1_prior": {
            "median": 0.875, "p10": 0.6525, "p90": 1.0128, "population": "KA-pool word set (DIFFERENT population)"}}
    return out


def store_to_scores(store: Dict[str, np.ndarray], matchedP, matchedS) -> Dict[str, np.ndarray]:
    """L2-normalise the store (row-wise, DSI's own convention) and score both cells via DSI's own
    `dense_scores_from_dict_store`, verbatim."""
    words = sorted(store)
    M = np.stack([store[w] for w in words], axis=0)
    Mn = DSI.l2n(M)
    store_n = {w: Mn[i] for i, w in enumerate(words)}
    return {"P": DSI.dense_scores_from_dict_store(store_n, matchedP),
           "S": DSI.dense_scores_from_dict_store(store_n, matchedS)}


def auc_margin_paired(scP_a, scS_a, scP_b, scS_b, n_boot: int, seed: int) -> Dict:
    """Paired bootstrap on AUC(a) - AUC(b): the SAME resampled pair indices feed both arms (they
    share the identical matched-pair population), so the CI is over the difference, not two
    independently-noisy CIs compared by eye. Uses DSI.auc_of verbatim per resample."""
    scP_a, scS_a = np.asarray(scP_a, dtype=np.float64), np.asarray(scS_a, dtype=np.float64)
    scP_b, scS_b = np.asarray(scP_b, dtype=np.float64), np.asarray(scS_b, dtype=np.float64)
    n_p, n_s = scP_a.size, scS_a.size
    point_a, point_b = DSI.auc_of(scP_a, scS_a), DSI.auc_of(scP_b, scS_b)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        ip = rng.integers(0, n_p, size=n_p)
        isv = rng.integers(0, n_s, size=n_s)
        diffs[b] = DSI.auc_of(scP_a[ip], scS_a[isv]) - DSI.auc_of(scP_b[ip], scS_b[isv])
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    band = "A_ABOVE_B" if lo > 0 else ("A_BELOW_B" if hi < 0 else "NOT_SEPARATED")
    return {"auc_a": round(point_a, 4), "auc_b": round(point_b, 4),
           "point_diff": round(point_a - point_b, 4), "ci95_diff": [round(lo, 4), round(hi, 4)],
           "band": band}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- predicted-direction adaptation: zero acc -> zero predicted -> residual_mag 1.0 (PC's own
    # convention for an undefined predictor), matching the "first occurrence is maximally surprising"
    # framing this cell inherits from exp_surprise_weighted_update_v1 ------------------------------
    acc0 = np.zeros(8)
    pred0 = _predicted_direction(acc0)
    assert not np.any(pred0), "zero accumulator must give a zero (undefined) predicted direction"
    obs0 = np.ones(8)
    mag0 = PC.residual_magnitude(obs0, pred0)
    assert abs(mag0 - 1.0) < 1e-9, "undefined predictor must read maximal residual: %.4f" % mag0
    ev["predicted_direction_undefined_case"] = {"residual_mag": mag0}

    # --- known-answer fixture: a lemma whose occurrences are IDENTICAL after the first is perfectly
    # predicted from occurrence 2 on -- P1 at any threshold > 0 must reject them, A0 must not. A
    # THIRD lemma ("vary") has genuinely DIFFERENT bipolar draws per occurrence, so its residual
    # sequence has real spread -- needed to test P2's continuous weighting and the anti-gate split
    # on something other than a degenerate all-or-nothing case ---------------------------------------
    d = 16
    v_rep = np.ones(d)
    v_mix = np.array([1.0] + [-1.0] * (d - 1))
    rng_build = np.random.default_rng(42)
    v_vary = rng_build.choice([-1.0, 1.0], size=(8, d))
    obs_fix = {"lemmas": ["rep", "mix", "vary"],
              "obs_vec": np.concatenate([np.stack([v_rep] * 6), np.stack([v_mix] * 3), v_vary],
                                        axis=0).astype(np.float32),
              "obs_lem": np.array([0] * 6 + [1] * 3 + [2] * 8, dtype=np.int32),
              "starts": np.array([0, 6, 9], dtype=np.int64), "lens": np.array([6, 3, 8], dtype=np.int64)}
    rng_fix = np.random.default_rng(0)
    a0_store, a0_diag = build_store(obs_fix, ["rep"], "A0_UNIFORM", 0.0, rng_fix)
    assert np.allclose(a0_store["rep"], v_rep * 6), "A0 must be the plain sum: %r" % a0_store["rep"]
    p1_store, p1_diag = build_store(obs_fix, ["rep"], "P1_GATE", 0.3, rng_fix)
    assert p1_diag["n_accept_by_word"]["rep"] == 1, (
        "an exactly-repeated occurrence must be perfectly predicted from the 2nd instance on -- "
        "P1 at threshold 0.3 must accept only the first: %r" % p1_diag)
    ev["repeated_occurrence_known_answer"] = {"A0_accept": a0_diag["n_accept_by_word"]["rep"],
                                              "P1_accept": p1_diag["n_accept_by_word"]["rep"]}

    # --- threshold=1.0 (the module's own maximum, residual_mag is capped at 1.0 by construction)
    # must accept ONLY occurrences whose residual is EXACTLY 1.0 -- for "rep" that is just the
    # first occurrence (undefined predictor); every later exact-repeat is perfectly predicted and
    # must be rejected -----------------------------------------------------------------------------
    p1_edge, p1_edge_diag = build_store(obs_fix, ["rep"], "P1_GATE", 1.0, rng_fix)
    assert p1_edge_diag["n_accept_by_word"]["rep"] == 1, (
        "threshold=1.0 (module maximum) must accept only the undefined-predictor first occurrence: "
        "%r" % p1_edge_diag)
    ev["threshold_at_module_max_accepts_only_first"] = p1_edge_diag["n_accept_by_word"]["rep"]

    # --- threshold_gate itself rejects an out-of-range threshold (module's own validation, proving
    # this cell's threshold sweep MUST stay within [0,1] -- which it does, since it is built from
    # residual_mag's own measured percentiles, never a blind constant) ------------------------------
    raised = False
    try:
        PC.threshold_gate(np.ones(4), np.zeros(4), threshold=1.5)
    except ValueError:
        raised = True
    assert raised, "threshold_gate must reject an out-of-[0,1] threshold"
    ev["threshold_gate_rejects_out_of_range"] = True

    # --- N2_ANTI_GATE is the complement of P1_GATE's accept set at the same threshold, per
    # occurrence (proven directly on "vary", whose residual_mag values genuinely differ per
    # occurrence rather than collapsing to 0/1) -- and P1+N2 can never both accept the same
    # occurrence (>= vs < are mutually exclusive at any fixed T) ------------------------------------
    p1_vary, p1_vary_diag = build_store(obs_fix, ["vary"], "P1_GATE", 0.5, rng_fix)
    n2_vary, n2_vary_diag = build_store(obs_fix, ["vary"], "N2_ANTI_GATE", 0.5, rng_fix)
    assert p1_vary_diag["n_accept_by_word"]["vary"] + n2_vary_diag["n_accept_by_word"]["vary"] <= 8, (
        "P1 (>=T) and N2 (<T) must never both accept the same occurrence: %r %r" %
        (p1_vary_diag, n2_vary_diag))
    assert p1_vary_diag["n_accept_by_word"]["vary"] != n2_vary_diag["n_accept_by_word"]["vary"] \
        or not np.allclose(p1_vary["vary"], n2_vary["vary"]), \
        "P1 and N2 must build genuinely different stores on a non-degenerate lemma"
    ev["anti_gate_diagnostic"] = {"P1_accept": p1_vary_diag["n_accept_by_word"]["vary"],
                                  "N2_accept": n2_vary_diag["n_accept_by_word"]["vary"]}

    # --- P2_WEIGHTED: on the "vary" lemma (genuinely differing occurrences, never perfectly
    # predicted) every occurrence contributes SOME weight (min_strength default 0, so only a
    # residual_mag of EXACTLY 0 skips). On the "rep" lemma (exact repeats), P2 collapses to the SAME
    # skip behaviour as P1 -- a perfectly-predicted repeat has residual_mag==0 and proportional_gate's
    # own default min_strength=0.0 skips it too. That collapse is itself a real, reportable property
    # of the module (not a test bug): "weighted" and "gated" only differ when the residual is
    # non-degenerate, which is exactly what the pre-registered surprise-distribution check below is
    # for. ---------------------------------------------------------------------------------------
    a0_vary, _ = build_store(obs_fix, ["vary"], "A0_UNIFORM", 0.0, rng_fix)
    p2_store, p2_diag = build_store(obs_fix, ["vary"], "P2_WEIGHTED", 0.0, rng_fix)
    assert p2_diag["n_accept_by_word"]["vary"] >= 6, "P2 should accept nearly every genuinely-varying occurrence: %r" % p2_diag
    assert not np.allclose(p2_store["vary"], a0_vary["vary"]), "P2 weighting must differ from the uniform sum"
    p2_rep, p2_rep_diag = build_store(obs_fix, ["rep"], "P2_WEIGHTED", 0.0, rng_fix)
    assert p2_rep_diag["n_accept_by_word"]["rep"] == 1, (
        "P2 on an exact-repeat lemma must collapse to accepting only the undefined-predictor first "
        "occurrence, same as P1 -- weighted-by-zero equals skipped: %r" % p2_rep_diag)
    ev["p2_weighted_known_answer"] = {"vary_accept": p2_diag["n_accept_by_word"]["vary"],
                                      "rep_accept_collapses_like_P1": p2_rep_diag["n_accept_by_word"]["rep"]}

    # --- N1_RANDOM consumes EXACTLY the accept COUNT it is given, per word ------------------------
    n1_store, n1_diag = build_store(obs_fix, ["rep", "mix"], "N1_RANDOM", 0.0, rng_fix,
                                    n_accept_map={"rep": 2, "mix": 1})
    assert n1_diag["n_accept_by_word"] == {"rep": 2, "mix": 1}, "N1 must match the given accept map: %r" % n1_diag
    ev["n1_random_token_matched"] = n1_diag["n_accept_by_word"]

    # --- surprise distribution: a lemma with IDENTICAL repeats must show a falling residual, and
    # the aggregate distribution reports the required percentiles -----------------------------------
    sdist = measure_surprise_distribution(obs_fix, ["rep", "mix", "vary"])
    assert sdist["n"] == 17, "must measure every occurrence of every target word: %r" % sdist
    assert sdist["p50"] <= 1.0001 and sdist["mean"] >= 0.0, "residual_mag must stay in [0,1]: %r" % sdist
    ev["surprise_distribution_fixture"] = sdist

    # --- paired AUC margin: identical score arrays must give point_diff==0 and NOT_SEPARATED;
    # a fully-separable A vs a chance-level B must give a positive, CI-separated margin -------------
    rng2 = np.random.default_rng(1)
    scP = rng2.standard_normal(60) + 0.9
    scS = rng2.standard_normal(60)
    same = auc_margin_paired(scP, scS, scP, scS, 500, 2)
    assert same["band"] == "NOT_SEPARATED" and abs(same["point_diff"]) < 1e-9, \
        "identical arms must show zero, unseparated margin: %r" % same
    bP = rng2.standard_normal(60)   # B: P and S drawn from the SAME distribution -> AUC(B)~0.5
    bS = rng2.standard_normal(60)
    diff = auc_margin_paired(scP, scS, bP, bS, 500, 3)
    assert diff["band"] == "A_ABOVE_B", "a genuinely separable A vs a chance B must read A_ABOVE_B: %r" % diff
    ev["auc_margin_paired_known_answers"] = {"identical": same["band"], "separable": diff["band"]}

    # --- arms-must-differ (META_RULE_AF) -----------------------------------------------------------
    a_arr = np.array([0.1, 0.2, 0.3])
    b_arr = np.array([0.1, 0.2, 0.30001])
    assert _digest(a_arr) != _digest(b_arr), "distinct score vectors must produce distinct digests"
    ev["arms_must_differ_digest_sensitivity"] = True

    # --- checkpoint round-trip (tools.exp_checkpoint's own self-test) ------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    # --- real code path: the cached observation stream loads and its shape matches the landed
    # cell's own reported shape (5,491 lemmas, d=256) -- REUSED, never rebuilt --------------------
    obs_real = SWU.build_obs_stream()
    assert obs_real["source"].startswith("reused"), (
        "the observation stream cache is expected to already exist on disk (landed "
        "exp_surprise_weighted_update_v1) -- got source=%r; a rebuild here would re-tokenise the "
        "corpus, which the dispatch brief forbids" % obs_real["source"])
    assert obs_real["obs_vec"].shape[1] == 256, "unexpected context dim: %r" % (obs_real["obs_vec"].shape,)
    ev["real_obs_stream_reused"] = {"source": obs_real["source"], "shape": list(obs_real["obs_vec"].shape)}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True}

    # =============================== STOP-IF (v), checked FIRST: DSI regression gate =================
    gate = dsi_regression_gate()
    rep["DSI_REGRESSION_GATE"] = gate["gate_report"]
    matchedP, matchedS = gate["matchedP"], gate["matchedS"]
    if grid == "reduced":
        matchedP, matchedS = matchedP[:40], matchedS[:40]
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match
    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    rep["N_WORDS_NEEDED"] = len(words_needed)

    # =============================== observation stream (REUSED, never rebuilt) ======================
    obs = SWU.build_obs_stream()
    rep["obs_stream"] = {"source": obs["source"], "n_obs": int(obs["obs_vec"].shape[0]),
                         "n_lemmas": len(obs["lemmas"]), "d": int(obs["obs_vec"].shape[1])}
    print("[obs] %r" % rep["obs_stream"], flush=True)

    # =============================== STOP-IF (v) continued: STREAM regression gate ===================
    C = CTS.load_cache()
    anchors_all, mat, mat_ok = C["anchors"], np.asarray(C["mat"], dtype=np.float64), np.asarray(C["mat_ok"], bool)
    pos_idx = C["pos"]
    valid_anchors = [a for a in anchors_all if mat_ok[pos_idx[a]]]
    stream_key = unit_key("STREAM_A0", CODE_VERSION, grid)
    prior_stream = load_units(out_dir_ckpt).get(stream_key)
    if prior_stream is not None:
        print("[stream_gate] RESUMED FROM CHECKPOINT", flush=True)
        stream_gate = prior_stream
    else:
        a0_full, _d = build_store(obs, valid_anchors, "A0_UNIFORM", 0.0, np.random.default_rng(0))
        coss = []
        for a in valid_anchors:
            landed = mat[pos_idx[a]]
            rebuilt = a0_full[a]
            nl, nr = np.linalg.norm(landed), np.linalg.norm(rebuilt)
            if nl > 1e-12 and nr > 1e-12:
                coss.append(float(np.dot(landed, rebuilt) / (nl * nr)))
        mean_cos = float(np.mean(coss)) if coss else 0.0
        a0_scores = store_to_scores({w: a0_full[w] for w in words_needed}, matchedP, matchedS)
        a0_auc = DSI.auc_of(a0_scores["P"], a0_scores["S"])
        if grid == "full":
            # exact same 242-pair population DSI's own cached number was computed on
            expected_a0 = gate["gate_report"]["recomputed_AUC_PER_ARM"]["INCUMBENT_LIVE_STORE"]["auc"]
            expected_a0_source = "DSI_cached_full_population_INCUMBENT_LIVE_STORE"
        else:
            # SMOKE truncates matchedP/matchedS to [:40] each (DSI/CAP's own reduced-grid
            # convention) -- comparing against the FULL-population cached 0.0710 would be a
            # population mismatch, not a real check. Instead slice DSI's OWN cached
            # INCUMBENT_LIVE_STORE score arrays to the IDENTICAL [:40]/[:40] truncation and
            # recompute AUC on that population via DSI.auc_of verbatim.
            dsi_inc = gate["arm_scores"]["INCUMBENT_LIVE_STORE"]
            expected_a0 = round(float(DSI.auc_of(dsi_inc["P"][:40], dsi_inc["S"][:40])), 4)
            expected_a0_source = "DSI_cached_scores_sliced_to_SAME_[:40]/[:40]_truncation_as_this_grid"
        stream_gate = {"mean_cos_rebuilt_A0_vs_LANDED_anchor_matrix": round(mean_cos, 6),
                       "cos_gate": STREAM_COS_GATE, "n_anchors_compared": len(coss),
                       "rebuilt_A0_AUC_on_matched_pairs": round(a0_auc, 4),
                       "expected_A0_AUC": expected_a0, "expected_A0_AUC_source": expected_a0_source,
                       "auc_delta": round(a0_auc - expected_a0, 6), "auc_tol": REGRESSION_TOL}
        stream_gate["PASSES"] = bool(mean_cos >= STREAM_COS_GATE
                                     and abs(a0_auc - expected_a0) <= REGRESSION_TOL)
        record_unit(out_dir_ckpt, stream_key, stream_gate)
    rep["STREAM_REGRESSION_GATE"] = stream_gate
    print("[stream_gate] %r" % stream_gate, flush=True)
    if not stream_gate["PASSES"]:
        raise SystemExit("INSTRUMENT_NOT_LICENSED -- STREAM regression gate FAILED: %r" % stream_gate)

    # =============================== STOP-IF (iii): surprise distribution, BEFORE any AUC ============
    sdist_key = unit_key("SURPRISE_DIST", CODE_VERSION, grid)
    prior_sdist = load_units(out_dir_ckpt).get(sdist_key)
    if prior_sdist is not None:
        print("[surprise] RESUMED FROM CHECKPOINT", flush=True)
        sdist = prior_sdist
    else:
        sdist = measure_surprise_distribution(obs, words_needed)
        record_unit(out_dir_ckpt, sdist_key, sdist)
    rep["SURPRISE_DISTRIBUTION_ON_THIS_POPULATION"] = sdist
    print("[surprise] n=%d mean=%.4f p10=%.4f p50=%.4f p90=%.4f DEGENERATE=%s" %
         (sdist["n"], sdist["mean"], sdist["p10"], sdist["p50"], sdist["p90"],
          sdist["DEGENERACY_TEST"]["SURPRISE_DEGENERATE"]), flush=True)
    surprise_degenerate = bool(sdist["DEGENERACY_TEST"]["SURPRISE_DEGENERATE"])

    thresholds = sorted(set(sdist[f"p{int(q * 100)}"] for q in QUANTILES))
    rep["GATE_THRESHOLDS_SWEPT"] = thresholds

    # =============================== arm construction (checkpointed per arm) =========================
    def get_or_build(name: str, rule: str, param: float, n_accept_map=None, seed: int = 0) -> Tuple[Dict, Dict]:
        k = unit_key("ARM", CODE_VERSION, grid, name)
        prior = load_units(out_dir_ckpt).get(k)
        if prior is not None:
            return prior["scores"], prior["diag"]
        rng = np.random.default_rng(MASTER_SEED + seed)
        store, diag = build_store(obs, words_needed, rule, param, rng, n_accept_map=n_accept_map)
        scores = store_to_scores(store, matchedP, matchedS)
        record_unit(out_dir_ckpt, k, {"scores": {"P": scores["P"].tolist(), "S": scores["S"].tolist()},
                                      "diag": diag})
        print("[arm] %-28s param=%s accept_rate=%.4f n_tok=%d" %
             (name, param, diag["acceptance_rate"], diag["n_tokens_accepted"]), flush=True)
        return {"P": np.array(scores["P"]), "S": np.array(scores["S"])}, diag

    arm_scores: Dict[str, Dict[str, np.ndarray]] = {}
    arm_diags: Dict[str, Dict] = {}

    arm_scores["A0_INCUMBENT"], arm_diags["A0_INCUMBENT"] = get_or_build(
        "A0_INCUMBENT", "A0_UNIFORM", 0.0, seed=1)
    arm_scores["P2_PREDICTION_WEIGHTED"], arm_diags["P2_PREDICTION_WEIGHTED"] = get_or_build(
        "P2_PREDICTION_WEIGHTED", "P2_WEIGHTED", 0.0, seed=2)

    for ti, T in enumerate(thresholds):
        pname = "P1_PREDICTION_GATED_T%g" % T
        arm_scores[pname], arm_diags[pname] = get_or_build(pname, "P1_GATE", T, seed=10 + ti)
        n2name = "N2_ANTI_GATE_T%g" % T
        arm_scores[n2name], arm_diags[n2name] = get_or_build(n2name, "N2_ANTI_GATE", T, seed=20 + ti)
        n1name = "N1_RANDOM_GATE_T%g" % T
        n_accept_map = dict(arm_diags[pname]["n_accept_by_word"])
        arm_scores[n1name], arm_diags[n1name] = get_or_build(
            n1name, "N1_RANDOM", T, n_accept_map=n_accept_map, seed=30 + ti)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC per arm + composition ========================================
    auc_results: Dict[str, Dict] = {}
    composition: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(arm_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, MASTER_SEED + 9191 + i)
        auc_results[name] = res
        composition[name] = {
            "mean_score_SET_P_paradigmatic_substitutable": round(float(np.mean(sc["P"])), 4),
            "mean_score_SET_S_syntagmatic_cooccurring": round(float(np.mean(sc["S"])), 4),
            "P_minus_S": round(float(np.mean(sc["P"]) - np.mean(sc["S"])), 4),
            "acceptance_rate": arm_diags[name].get("acceptance_rate"),
            "n_tokens_accepted": arm_diags[name].get("n_tokens_accepted"),
            "NOTE": ("'winner/gold co-occurrence share' has no referent on this AUC instrument -- "
                    "there is no per-item argmax 'winner', only a rank-sum AUC over SET P (by "
                    "construction zero corpus co-occurrence) vs SET S (by construction top-decile "
                    "co-occurrence). The adapted, faithful analogue reported here is the arm's own "
                    "mean score on each set and their difference.")}
        print("[auc] %-28s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)
    rep["AUC_PER_ARM"] = auc_results
    rep["COMPOSITION_PER_ARM"] = composition
    rep["DSI_A0_CACHED_AUC"] = EXPECTED_AUC["INCUMBENT_LIVE_STORE"]

    # =============================== paired margins: P1 vs its own N1, and P1 vs N2 (per threshold) ==
    margins: Dict[str, Dict] = {}
    for ti, T in enumerate(thresholds):
        pname, n1name, n2name = "P1_PREDICTION_GATED_T%g" % T, "N1_RANDOM_GATE_T%g" % T, "N2_ANTI_GATE_T%g" % T
        margins["%s_vs_%s" % (pname, n1name)] = auc_margin_paired(
            arm_scores[pname]["P"], arm_scores[pname]["S"], arm_scores[n1name]["P"], arm_scores[n1name]["S"],
            N_BOOT, MASTER_SEED + 40 + ti)
        margins["%s_vs_%s" % (pname, n2name)] = auc_margin_paired(
            arm_scores[pname]["P"], arm_scores[pname]["S"], arm_scores[n2name]["P"], arm_scores[n2name]["S"],
            N_BOOT, MASTER_SEED + 50 + ti)
        margins["%s_vs_A0_INCUMBENT" % pname] = auc_margin_paired(
            arm_scores[pname]["P"], arm_scores[pname]["S"], arm_scores["A0_INCUMBENT"]["P"],
            arm_scores["A0_INCUMBENT"]["S"], N_BOOT, MASTER_SEED + 60 + ti)
    rep["PAIRED_MARGINS"] = margins

    # =============================== INTERPRETATION (STOP-IF i/ii/iv, iii already flagged above) =====
    best_p1_t = max(thresholds, key=lambda T: auc_results["P1_PREDICTION_GATED_T%g" % T]["auc"])
    best_pname = "P1_PREDICTION_GATED_T%g" % best_p1_t
    p1_best = auc_results[best_pname]
    p1_above_half = p1_best["band"] == "ABOVE_0.5_SUBSTITUTABILITY"
    p1_vs_n1 = margins["%s_vs_N1_RANDOM_GATE_T%g" % (best_pname, best_p1_t)]
    p1_vs_a0 = margins["%s_vs_A0_INCUMBENT" % best_pname]
    p1_beats_n1 = p1_vs_n1["band"] == "A_ABOVE_B"
    p1_beats_a0 = p1_vs_a0["band"] == "A_ABOVE_B"

    if p1_above_half and p1_beats_n1:
        interp = "STOP_IF_i_P1_ABOVE_0.5_AND_BEATS_RATE_MATCHED_N1__SUBSTITUTABILITY_STORE"
    elif p1_beats_a0 and not p1_beats_n1:
        interp = "STOP_IF_ii_P1_BEATS_A0_BUT_NOT_N1__GAIN_IS_GATING_RATE_NOT_PREDICTION_ERROR"
    elif (not p1_beats_a0) or margins[
        "%s_vs_A0_INCUMBENT" % best_pname]["band"] == "NOT_SEPARATED":
        interp = "STOP_IF_iv_P1_TIES_A0__PREDICTION_ERROR_WRITE_GATE_DOES_NOT_PRODUCE_SUBSTITUTABILITY"
    else:
        interp = "MIXED_OUTCOME_NOT_CLEANLY_ONE_OF_i_ii_iv__REPORT_RAW_NUMBERS"
    if surprise_degenerate:
        interp = "STOP_IF_iii_SURPRISE_DEGENERATE_MECHANISM_NOT_FAIRLY_TESTED__" + interp
    rep["BEST_P1_THRESHOLD"] = best_p1_t
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
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "PREDICTIVE_CODING_WRITE_GATE__%s" % interp

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Does a store written under hdlab/predictive_coding.py's prediction-error "
                       "write gate read above 0.5 on the licensed dissociation instrument? Surprise "
                       "distribution reported first, then P1 (threshold-gated) / P2 (weighted) vs "
                       "A0 (incumbent) / N1 (rate-matched random gate) / N2 (anti-gate). -> " + interp),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "QUANTILES": list(QUANTILES),
                  "DEGENERACY_MEDIAN_MIN": DEGENERACY_MEDIAN_MIN,
                  "DEGENERACY_IQR90_10_MAX": DEGENERACY_IQR90_10_MAX,
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
