"""exp_readout_independent_verifier_signals_v1 -- given a shortlist that contains the answer 37.6%
of the time (PARTIAL cue, k=50), how much of that 37.6% can a rejector built from signals
INDEPENDENT OF THE PROPOSER actually recover?

FINDINGS LOG: notes/readout_independent_verifier_signals_findings_2026-08-17.md
INCUMBENT / LIBRARY (imported, NEVER edited): experiments/exp_readout_shortlist_verifier_v1.py (RSV)
  -- this cell REUSES RSV's shortlist construction (shortlist_mask, top1_index,
  rank_normalize_within_shortlist), its S1_ATTESTATION mechanism (build_attestation_index,
  attestation_scores_for_shortlist) verbatim, its floor/arm harness pattern (FB calls, add_arm,
  paired bootstrap, margin dict shape, ARMS_MUST_DIFFER via arm_digest), and its regression
  constants. A divergent reimplementation would make the regression gate meaningless -- so it isn't
  one. NEW in this cell: S2_TYPE_VIOLATION, S3_REGISTER, the frequency/length-matched controls, and
  the SIGNAL-INDEPENDENCE-FIRST reporting order.

FILENAME NOTE: experiments/exp_propose_reject_retrieval_v1.py is a BLOCKED PATH and is not touched.
This is a distinct, descriptive name for the follow-on cell to RSV.

WHAT RSV ESTABLISHED (data/exp_readout_shortlist_verifier_v1/metrics.json, verified off disk before
writing a line of this cell, and RE-VERIFIED here by this cell's own regression gate):
  - PARTIAL-cue shortlist hit rate (the achievable ceiling of ANY rejector): 0.02228 / 0.08838 /
    0.14171 / 0.22183 / 0.37581 at k=1/5/10/20/50, against a random-ranking null of 0.01009 /
    0.04779 / 0.08972 / 0.16002 / 0.30406. The binding floor is F_CONSTANT_PROTOTYPE = 0.13896.
    At k=50 a PERFECT chooser scores 0.37581, 2.7x the binding floor -- the PROPOSER is not the
    blocker; the CHOOSER is.
  - R1_ATTESTATION (an incumbent coordination-pattern ("X and/or Y") rejector) beat BOTH the
    incumbent argmax and a random-shortlist pick, CI-separated at every k (+0.0083 to +0.0187 vs
    incumbent; +0.0058 to +0.0274 vs random pick), clean on orthographic/length controls, but at
    accuracy 0.041 vs the floor's 0.139 -- nowhere near the floor.
  - R2_PROFILE (a second-order profile cosine built from the SAME store the proposer scores)
    mostly tied the incumbent and barely beat random pick.
  - THE MEASURED EXPLANATION, this cell's organising principle, carried forward: SIGNAL
    INDEPENDENCE FROM THE PROPOSER predicts whether a rejector works. R1 correlated with the
    proposer's own score at r~0.11 and worked (weakly); R2 correlated at r~0.59-0.61 and did not.

THE QUESTION THIS CELL ANSWERS: of that 37.6%, how much can a rejector built from signals
INDEPENDENT of the proposer actually recover -- and does the independence-predicts-performance
story hold up against a genuinely different kind of independent signal (selectional/type
compatibility) rather than another lexical-association channel?

THE ORDER OF WORK IS NOT OPTIONAL. For every candidate signal, correlation with the proposer's own
score is measured and reported FIRST (SIGNAL_INDEPENDENCE_TABLE, in `run()` immediately after the
per-k score matrices are built, physically before MARGINS/RECOVERY_FRACTION in both the dict and the
console log). PRE-REGISTERED PREDICTION, written before any number is read: signals with
|r| >= INDEP_R_THRESHOLD=0.4 will not act as verifiers (S4_COMBINED's membership rule below is keyed
off this same threshold, fixed before the run).

CANDIDATE SIGNALS, enumerated from what is actually on disk (not substituted for convenience):
  S1_ATTESTATION      the incumbent rejector, carried forward UNCHANGED (imported from RSV) as the
                       arm to beat.
  S2_TYPE_VIOLATION    THE OWNER'S OWN Q11 MECHANISM ("kettle apologized" is rejected immediately
                       because kettles aren't sentient -- a SELECTIONAL/TYPE compatibility check
                       that generalises to unseen pairs, which is exactly where attestation is
                       structurally blind). Built from experiments/selectional_preference_extractor_v1
                       .build_or_load() -- the SAME slot-filler tables exp_selectional_constraint_
                       bridge_v1 used (8.6 slots / 145 fillers per word, verified real supply even
                       though that cell's BUILD-mode use of them failed, DO-NOT-REDO 43). This cell
                       does NOT import exp_selectional_constraint_bridge_v1's SelectionalSource class
                       (it is coupled to a different instrument's Bridger/hidden-code machinery and a
                       12-dim SimLex-norms target space that has nothing to do with this cell's
                       5,491-anchor store); it DOES reuse the underlying slot_filler DATA via
                       selectional_preference_extractor_v1.build_or_load() (cached pickle, not
                       re-extracted -- the extraction already ran and is on disk at
                       data/selectional_preferences_v1/selectional_slots_v1.pkl, 41,529 slots /
                       944,990 observations over 64MB of simplewiki, a DIFFERENT corpus from both the
                       store and S1's attestation corpus). NEW SCORER, OURS: cos(slot-membership
                       profile(anchor), slot-membership profile(query)), PMI-weighted, positive-PMI
                       only, top TYPE_PROFILE_TOPK=64 slots per word -- "does this candidate tend to
                       fill the same verb-argument slots as the query", i.e. does it belong to the
                       same selectional TYPE. Never touches the vector store.
                       CRITICAL FRAMING: exp_selectional_constraint_bridge_v1 measured selectional
                       constraints used to BUILD a meaning vector (mean-code-of-fillers as a
                       replacement code) and that failed (rho 0.0270 [-0.0737,0.1251] vs a 0.0900
                       scramble p95, NOT_SEPARATED, DO-NOT-REDO 43). Using the SAME data to REJECT a
                       candidate from an existing shortlist is a different job -- a low-dimensional
                       compatibility check, not a full meaning reconstruction -- and that null does
                       NOT mechanically transfer to this use. Whether it turns out to behave the same
                       here anyway is an empirical question this cell answers, not an assumption.
  S3_REGISTER          the owner's Q10 mechanism ("think" vs "contemplate" -- register/formality).
                       AFFECT (Lancaster sensorimotor + Brysbaert concreteness + Warriner VAD) was
                       already measured to contribute nothing once width-matched -- REGISTER IS NOT
                       VALENCE, so this does not re-run that null. Sourced from
                       data/grounding_testbed/AoA_51715_words.csv (Kuperman age-of-acquisition norms,
                       51,715 words, on disk, unused elsewhere in this family) as the register/
                       formality proxy: later-acquired words skew toward the same "purposeful,
                       formal" register the owner described. RESIDUALISED against word length AND
                       log-frequency (both taken from the SAME AoA table's own Nletters-equivalent
                       len() and Freq_pm columns) via OLS BEFORE this arm is scored, per the
                       dispatch's explicit requirement -- an unresidualised register channel is a
                       spelling channel, and length alone orders the owner's own 30 validation pairs
                       29 of 30. F_LENGTH_MATCHED and F_FREQUENCY_MATCHED (below) are the raw,
                       unresidualised ablation controls that isolate whether residualisation bought
                       anything.
  S4_COMBINED          rank-normalised EQUAL-weight sum of whichever of S1/S2/S3 measure independent
                       of the proposer (|r| < INDEP_R_THRESHOLD at k=20) -- the membership RULE is
                       pre-registered before the run; which signals qualify is empirical. If exactly
                       two qualify, an additional pairwise beta sweep (0.25/0.5/0.75, matching RSV's
                       R3 convention) is run SECONDARY and never adopted.
  FURTHER SIGNALS SOUGHT AND NOT ADDED: sensorimotor/concreteness (Lancaster+Brysbaert) and VAD
  (Warriner valence/arousal/dominance) are on disk (data/grounding_testbed/) but constitute the same
  AFFECT channel already measured to contribute nothing once width-matched (exp_feeling_match_
  rejector_v1) -- re-running it under a new name would reproduce a known null, not source a new
  signal, and is the "no padding experiments" rule applied to signal choice. No fifth signal is added.

MANDATORY CONTROL ARMS: N1_RANDOM_REJECTOR (the floor that matters most), N2_PROPOSER_AS_REJECTOR
(validity arm, MUST reduce to G0_ARGMAX bit-for-bit or the cell is VOID), G1_SHORTLIST_ORACLE (ceiling
diagnostic ONLY, never a headline), K1_KNOWN_ANSWER (BINDING gate = KA_SELF_ADDRESS on the store,
>=0.95, hard SystemExit before any treatment number), F_FREQUENCY_MATCHED (query/candidate
log-frequency-distance rejector, general control) and, for S3 specifically, F_LENGTH_MATCHED
(query/candidate length-distance rejector).

FLOORS: all four (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE) recomputed fresh on
THIS cell's own population, on the PARTIAL cue. REGRESSION-CHECKED (not adopted) against RSV's landed
values as a same-instrument consistency check, exactly as RSV itself checked against
exp_readout_ceiling_diagnosis_v1's values. NEVER IMPORTED AS THIS CELL'S OWN RESULT: 0.1390, 0.1715,
0.2604, 0.3758, 0.0873, 0.1382, 0.2070, -0.1959 -- every one of these is recomputed from scratch
inside run() below; the historical values appear ONLY as regression-check constants, labelled as such.

STOP-IF, pre-registered verbatim from the dispatch:
  (i)   an independent-signal rejector (S1/S2/S3/S4) clears max(four floors) CI-separated AND beats
        N1_RANDOM_REJECTOR CI-separated -> THE FIRST GENUINE READ-OUT WIN.
  (ii)  S2_TYPE_VIOLATION is independent (low r) but does NOT lift -> independence is necessary but
        not sufficient; the organising principle needs qualifying.
  (iii) every independent signal ties N1_RANDOM -> the rejector road is measured and closed; the
        programme's remaining problem is the PROPOSER after all.
  (iv)  N2_PROPOSER_AS_REJECTOR does not reduce to G0_ARGMAX -> the stages are not independent, the
        cell is VOID, nothing downstream is published.
  (v)   any win correlates with orthographic similarity or word length -> rule 12 failure.

BRAIN FIDELITY.
(a) STRUCTURE PER COMPONENT. Generate-then-test with a rejector is PINNED as a control structure
    (same citations as RSV's docstring: Burke & MacKay 1991, Brown & McNeill 1966 tip-of-the-tongue;
    Medina 2011 PNAS, Trueswell 2013 propose-but-verify word learning). The REJECTOR'S CONTENT
    remains UNPINNED for S1/S3 (engineering heuristics standing in for an unbuilt register channel).
    S2 is different: selectional/type compatibility as a REJECTION criterion is the owner's OWN
    verbatim described mechanism (BOARD Q11), and verb-argument selectional restriction is carried
    by temporo-parietal cortex (posterior middle temporal gyrus + angular gyrus), PINNED by the same
    literature exp_selectional_constraint_bridge_v1 and selectional_preference_extractor_v1 cite
    (Schwartz 2011 PNAS; Mirman 2017; J Neurosci 36(16):4405; Neuropsychologia PMID 30735675) -- so
    S2's SOURCE STRUCTURE is pinned even though its use as a REJECTION SCORE (a slot-profile cosine)
    is OURS, invention under test, same as everywhere else in this family.
(b) ORGAN REUSE, enumerated from disk then reconciled, verified by RUNTIME (sys.modules), never grep:
    experiments.exp_readout_shortlist_verifier_v1 (shortlist_mask, top1_index,
    rank_normalize_within_shortlist, build_attestation_index, attestation_scores_for_shortlist,
    arm_digest -- NONE edited), experiments.exp_readout_ceiling_diagnosis_v1 (build_population,
    hit_at_k_curve, random_ranking_hit_at_k, install_grounded_similarity_tripwire, self_test,
    _halfwidth), experiments.exp_cue_to_store_translation_v1 (cache/aux loaders, ruler gate),
    experiments.exp_cue_binarised_readout_transfer_v1 (pearson_ci_bootstrap),
    experiments.exp_definitional_grounding_v5 (load_corpus_v5), experiments.
    selectional_preference_extractor_v1 (build_or_load -- the slot_filler DATA asset),
    tools.floor_battery (floors, scorer, bootstrap), hdlab.reading_grounding_loop (normalize_lemma),
    tools.exp_checkpoint.
(c) SHELVE/REVIVAL, BRAIN-FRAMED, carried forward from RSV: if this architecture does not win, the
    revival criterion is not "the rejector did not score" -- S1/S3 are still proxies for an unbuilt
    register channel. S2 is the one arm here where the SOURCE is already brain-pinned; if S2 fails,
    the honest reading is that the SCORER (a slot-profile cosine) is the wrong estimator over pinned
    data, not that selectional rejection itself is unmotivated.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. The store is
NEVER rebuilt. data/foundation/** is never opened. Writes only under
data/exp_readout_independent_verifier_signals_v1{_REDUCED}/.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import csv
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_readout_shortlist_verifier_v1 as RSV           # THE LIBRARY, NEVER EDITED
import exp_cue_to_store_translation_v1 as CTS              # cache/aux loaders + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as RCD              # build_population/hit_at_k_curve, NEVER EDITED
import selectional_preference_extractor_v1 as SEL          # slot_filler DATA asset, NEVER EDITED
from tools import floor_battery as FB                       # floors + scorer + bootstrap, NEVER EDITED
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key

ANCHOR_NAME = "exp_readout_independent_verifier_signals_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_independent_verifier_signals_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. NEVER EDITED AFTER A RUN. -------------------------------------
MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if SMOKE else 10000
REGRESSION_TOL = RSV.REGRESSION_TOL
KA_MIN = RSV.KA_MIN
K_REJECTOR_GRID: Tuple[int, ...] = RSV.K_REJECTOR_GRID       # (5, 10, 20, 50)
K_PARTIAL_GRID: Tuple[int, ...] = RSV.K_PARTIAL_GRID         # (1, 5, 10, 20, 50)
K_EXACT_GRID: Tuple[int, ...] = RSV.K_EXACT_GRID
K_KA_SHORTLIST = RSV.K_KA_SHORTLIST
S4_K = 20                                                     # PRE-REGISTERED, fixed before any number
FLOOR_NAMES = RSV.FLOOR_NAMES
INDEP_R_THRESHOLD = 0.4                                       # pre-registered per the dispatch's own
                                                               # language "above ~0.4"
TYPE_MIN_FILLER_COUNT = 2                                     # same convention as exp_selectional_
                                                               # constraint_bridge_v1.WSLOT_MIN_COUNT=2
TYPE_PROFILE_TOPK = 64                                        # OURS, a fixed parameter (not swept in
                                                               # this cell; analogous to RSV's fixed
                                                               # R3_K=20)
AOA_CSV = os.path.join(REPO_ROOT, "data", "grounding_testbed", "AoA_51715_words.csv")

# ---- REGRESSION-CHECK constants (consistency checks, NEVER adopted as this cell's own numbers) ----
REG_A0_PARTIAL = RSV.REGRESSION_A0_PARTIAL
REG_A1_EXACT_K1 = RSV.REGRESSION_A1_EXACT_K1
REG_A1_EXACT_K5 = RSV.REGRESSION_A1_EXACT_K5
REG_A1_EXACT_K10 = RSV.REGRESSION_A1_EXACT_K10
REG_ADDR_EXACT = RSV.REGRESSION_ADDR_EXACT
REG_FCONST_K1 = RSV.REGRESSION_FCONST_K1
REG_G1_PARTIAL = {1: 0.02228, 5: 0.08838, 10: 0.14171, 20: 0.22183, 50: 0.37581}   # RSV landed, cited
                                                                                    # for consistency
                                                                                    # ONLY, recomputed
                                                                                    # fresh below


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
def build_type_profile(slot_filler: Dict[Tuple[str, str], Dict[str, int]], target_vocab: Set[str],
                       min_count: int = TYPE_MIN_FILLER_COUNT, topk: int = TYPE_PROFILE_TOPK
                       ) -> Tuple[Dict[str, Dict[Tuple[str, str], float]], Dict[str, float], Dict]:
    """S2_TYPE_VIOLATION's data structure: for every word in `target_vocab`, its SELECTIONAL profile
    -- the (verb, role) slots it fills as an argument corpus-wide, PMI-weighted (positive PMI only,
    top `topk` by weight). Two words with similar profiles tend to fill the SAME verb argument slots,
    i.e. belong to the same selectional TYPE -- "kettle" and "person" both potentially fill many
    slots, but only "person" fills communication-verb SUBJ slots the way "clerk" does.

    PMI is computed against the word's and slot's TRUE marginal frequency over the WHOLE table (not
    just target_vocab), so a rare word that strongly prefers a slot is not swamped by common fillers.
    """
    slot_total: Dict[Tuple[str, str], float] = {}
    word_total: Dict[str, float] = {}
    for s, fillers in slot_filler.items():
        st = 0.0
        for f, c in fillers.items():
            st += c
            word_total[f] = word_total.get(f, 0.0) + c
        slot_total[s] = st
    N = float(sum(slot_total.values()))
    raw_profile: Dict[str, List[Tuple[Tuple[str, str], float]]] = {}
    if N > 0:
        for s, fillers in slot_filler.items():
            st = slot_total[s]
            if st <= 0:
                continue
            for f, c in fillers.items():
                if f not in target_vocab or c < min_count:
                    continue
                wt = word_total.get(f, 0.0)
                if wt <= 0:
                    continue
                pmi = math.log((c * N) / (wt * st), 2.0)
                if pmi > 0:
                    raw_profile.setdefault(f, []).append((s, pmi))
    profile: Dict[str, Dict[Tuple[str, str], float]] = {}
    norm: Dict[str, float] = {}
    for w, lst in raw_profile.items():
        lst.sort(key=lambda t: -t[1])
        lst = lst[:topk]
        d = dict(lst)
        profile[w] = d
        norm[w] = math.sqrt(sum(v * v for v in d.values()))
    n_prof = len(profile)
    stats = {
        "n_target_vocab": len(target_vocab), "n_target_words_with_profile": n_prof,
        "coverage_frac": round(n_prof / max(len(target_vocab), 1), 4),
        "mean_slots_per_profiled_word": round(float(np.mean([len(d) for d in profile.values()])), 3)
        if profile else 0.0,
        "N_total_slot_observations": N, "n_slots_in_table": len(slot_filler),
        "min_filler_count": min_count, "topk": topk}
    return profile, norm, stats


def type_violation_scores_for_shortlist(mask: np.ndarray, query_lemmas: Sequence[str],
                                        anchor_lemmas: Sequence[str],
                                        profile: Dict[str, Dict[Tuple[str, str], float]],
                                        norm: Dict[str, float]) -> np.ndarray:
    """cos(slot-profile(anchor), slot-profile(query)) for every (anchor, item) pair inside `mask`;
    0 elsewhere. STRUCTURALLY BLIND (0) for any word with no eligible selectional profile -- same
    convention as RSV.attestation_scores_for_shortlist."""
    n_anchors, n_items = mask.shape
    out = np.zeros((n_anchors, n_items), dtype=np.float32)
    rows, cols = np.nonzero(mask)
    for r, c in zip(rows.tolist(), cols.tolist()):
        qw = query_lemmas[c]
        cw = anchor_lemmas[r]
        if qw == cw:
            continue
        pq, pc = profile.get(qw), profile.get(cw)
        if not pq or not pc:
            continue
        nq, nc = norm.get(qw, 0.0), norm.get(cw, 0.0)
        if nq <= 0 or nc <= 0:
            continue
        a, b = (pq, pc) if len(pq) <= len(pc) else (pc, pq)
        dot = 0.0
        for k, v in a.items():
            v2 = b.get(k)
            if v2:
                dot += v * v2
        if dot:
            out[r, c] = dot / (nq * nc)
    return out


def load_aoa_and_freq(path: str) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Kuperman AoA (register/formality proxy) and SUBTLEX Freq_pm, both keyed by lowercased Word."""
    aoa: Dict[str, float] = {}
    freq: Dict[str, float] = {}
    # latin-1: the source CSV carries a handful of non-UTF-8 bytes (measured); latin-1 never raises
    # (every byte maps to a codepoint) and the words this cell actually looks up are ASCII anyway.
    with open(path, encoding="latin-1") as f:
        rd = csv.DictReader(f)
        for row in rd:
            w = (row.get("Word") or "").strip().lower()
            if not w:
                continue
            av = (row.get("AoA_Kup") or "").strip()
            fv = (row.get("Freq_pm") or "").strip()
            if av:
                try:
                    aoa[w] = float(av)
                except ValueError:
                    pass
            if fv:
                try:
                    freq[w] = float(fv)
                except ValueError:
                    pass
    return aoa, freq


def residualize_aoa(target_vocab: Set[str], aoa: Dict[str, float], freq: Dict[str, float]
                    ) -> Tuple[Dict[str, float], Dict]:
    """OLS: AoA ~ 1 + length + log1p(Freq_pm), over target-vocab words with both AoA and frequency
    data. Returns the RESIDUAL per word -- the register/formality signal with length and frequency
    partialled out. An unresidualised AoA channel is a spelling+frequency channel; this is why S3 is
    never scored on raw AoA."""
    words = sorted(w for w in target_vocab if w in aoa and w in freq)
    if len(words) < 20:
        return {}, {"status": "INSUFFICIENT_AOA_COVERAGE", "n": len(words)}
    length = np.array([len(w) for w in words], dtype=np.float64)
    logfreq = np.log1p(np.array([freq[w] for w in words], dtype=np.float64))
    y = np.array([aoa[w] for w in words], dtype=np.float64)
    X = np.stack([np.ones_like(length), length, logfreq], axis=1)
    beta, _res, _rank, _sv = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    resid_map = {w: float(r) for w, r in zip(words, resid)}
    stats = {"status": "OK", "n_words_residualized": len(words),
             "beta_intercept_length_logfreq": [round(float(b), 5) for b in beta],
             "r2_of_length_freq_predicting_aoa": round(r2, 4),
             "resid_std": round(float(np.std(resid)), 5)}
    return resid_map, stats


def distance_sim_scores_for_shortlist(mask: np.ndarray, query_lemmas: Sequence[str],
                                      anchor_lemmas: Sequence[str], value: Dict[str, float],
                                      scale: float) -> np.ndarray:
    """exp(-|value[candidate] - value[query]| / scale) for every (anchor, item) pair inside `mask`;
    0 for missing data or non-positive scale. Used for S3_REGISTER (value=residualised AoA) and for
    the F_LENGTH_MATCHED / F_FREQUENCY_MATCHED ablation controls (value=raw length / raw log-freq)."""
    n_anchors, n_items = mask.shape
    out = np.zeros((n_anchors, n_items), dtype=np.float32)
    if scale <= 0 or not np.isfinite(scale):
        return out
    rows, cols = np.nonzero(mask)
    for r, c in zip(rows.tolist(), cols.tolist()):
        qw = query_lemmas[c]
        cw = anchor_lemmas[r]
        if qw == cw:
            continue
        vq, vc = value.get(qw), value.get(cw)
        if vq is None or vc is None:
            continue
        out[r, c] = float(np.exp(-abs(vc - vq) / scale))
    return out


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["tripwire_installed"] = bool(RCD.install_grounded_similarity_tripwire())
    print("[selftest] reusing RSV.self_test() wholesale -- validates every REUSED primitive "
         "(shortlist_mask, N2 reduces to G0, rank_normalize, attestation index/lookup, "
         "pearson_ci_bootstrap, arm_digest, RCD/RSO self-tests it wraps) ...", flush=True)
    ev["RSV_self_test"] = RSV.self_test()

    # --- build_type_profile: KNOWN ANSWER, directly modelling the owner's Q11 example -------------
    # "person" fills apologize/SUBJ AND run/SUBJ; "clerk" fills apologize/SUBJ; "kettle" fills ONLY
    # boil/SUBJ. A candidate that shares the query's selectional slots must score HIGHER than one
    # that does not -- this is the formal version of "kettle apologized" being rejectable.
    slot_filler = {
        ("apologize", "SUBJ"): {"person": 5, "clerk": 4, "robot": 1},
        ("boil", "SUBJ"): {"kettle": 8, "water": 6, "pot": 3},
        ("run", "SUBJ"): {"dog": 4, "person": 3, "rabbit": 2},
    }
    target = {"person", "clerk", "robot", "kettle", "water", "pot", "dog", "rabbit"}
    profile, norm, stats = build_type_profile(slot_filler, target, min_count=1, topk=64)
    assert ("apologize", "SUBJ") in profile.get("person", {}), "person must fill apologize/SUBJ"
    assert ("boil", "SUBJ") not in profile.get("person", {}), "person never fills boil/SUBJ"
    assert ("apologize", "SUBJ") not in profile.get("kettle", {}), "kettle never fills apologize/SUBJ"
    mask = np.ones((8, 1), dtype=bool)
    anchors_syn = ["person", "clerk", "robot", "kettle", "water", "pot", "dog", "rabbit"]
    idx = {w: i for i, w in enumerate(anchors_syn)}
    S2 = type_violation_scores_for_shortlist(mask, ["person"], anchors_syn, profile, norm)
    s_clerk = float(S2[idx["clerk"], 0])
    s_kettle = float(S2[idx["kettle"], 0])
    assert s_clerk > s_kettle, ("S2 must score clerk (shares apologize/SUBJ with person) ABOVE "
                                "kettle (shares no slot): clerk=%.4f kettle=%.4f" % (s_clerk, s_kettle))
    assert s_kettle == 0.0, "kettle shares no slot with person and must score exactly 0"
    ev["S2_known_answer_kettle_vs_clerk"] = {"person_vs_clerk": round(s_clerk, 4),
                                             "person_vs_kettle": round(s_kettle, 4),
                                             "profile_stats": stats}

    # --- residualize_aoa: KNOWN ANSWER. AoA is a near-perfect linear function of length+logfreq for
    # 19 filler words, plus ONE word carries an injected +6.0 residual bump on top of that trend.
    # residualize_aoa's length covariate is len(word_string) itself (matching rule-12's own
    # word_len=len(anchor) convention), so the fixture words MUST actually vary in string length --
    # an earlier draft of this fixture used fixed-length placeholder names ("w00".."w19") and always
    # measured a spurious r2=0.0, which is exactly the kind of silent covariate mismatch this
    # known-answer check exists to catch.
    base_letters = "abcdefghijklmnopqrstuvwxyz"
    words = []
    lengths: Dict[str, int] = {}
    for i in range(20):
        L = 3 + (i % 8)                       # 3..10 chars
        w = base_letters[i] + "x" * (L - 1)
        words.append(w)
        lengths[w] = L
    assert len(set(words)) == 20, "fixture word strings collided"
    freqs = {w: float(5 + 3 * (i % 5)) for i, w in enumerate(words)}
    aoa = {w: 2.0 * lengths[w] + 0.05 * math.log1p(freqs[w]) for w in words}
    bumped = words[7]
    aoa[bumped] += 6.0
    resid_map, rstats = residualize_aoa(set(words), aoa, freqs)
    assert rstats["status"] == "OK", rstats
    assert rstats["r2_of_length_freq_predicting_aoa"] > 0.9, (
        "the synthetic fixture is not length/freq-dominated: r2=%.4f" % rstats[
            "r2_of_length_freq_predicting_aoa"])
    # tolerance is wide on purpose: with n=20 and p=3 OLS parameters, a single outlier's own leverage
    # (~p/n) pulls the fitted line toward it, so the RECOVERED residual is expected to undershoot the
    # true 6.0 bump by roughly that fraction -- the check is "most of the bump survived and no other
    # word absorbed it", not "OLS recovers an injected outlier exactly", which it structurally cannot.
    assert 2.5 < resid_map[bumped] <= 6.0, (
        "residualize_aoa did not recover most of the injected +6.0 residual bump on %s: got %.4f"
        % (bumped, resid_map[bumped]))
    others = [w for w in words if w != bumped]
    assert max(abs(resid_map[w]) for w in others) < 3.0, "unbumped words carry a spurious residual"
    ev["residualize_aoa_known_answer"] = {"bumped_word_residual": round(resid_map[bumped], 3),
                                          "max_abs_other_residual": round(
                                              max(abs(resid_map[w]) for w in others), 3),
                                          "stats": rstats}

    # --- distance_sim_scores_for_shortlist: monotone in |diff|, missing data -> 0 ------------------
    value = {"a": 0.0, "b": 1.0, "c": 5.0}
    mask2 = np.ones((3, 1), dtype=bool)
    anchors2 = ["a", "b", "c"]
    S3 = distance_sim_scores_for_shortlist(mask2, ["a"], anchors2, value, scale=1.0)
    assert S3[0, 0] == 0.0, "self-comparison (a vs a) must be excluded (score 0)"
    assert S3[1, 0] > S3[2, 0] > 0.0, "score must be strictly decreasing in |value diff|"
    S3_missing = distance_sim_scores_for_shortlist(mask2, ["a"], ["a", "b", "unknown_word"],
                                                    value, scale=1.0)
    assert S3_missing[2, 0] == 0.0, "a word absent from `value` must score exactly 0"
    ev["distance_sim_selftest"] = {"score_b": round(float(S3[1, 0]), 4),
                                   "score_c": round(float(S3[2, 0]), 4)}

    # --- the AoA CSV is really on disk and has the columns this cell depends on --------------------
    assert os.path.isfile(AOA_CSV), "AOA_CSV missing: %s" % AOA_CSV
    aoa_real, freq_real = load_aoa_and_freq(AOA_CSV)
    assert len(aoa_real) > 30000, "AoA table loaded too few words: %d" % len(aoa_real)
    assert "kettle" in aoa_real or "think" in aoa_real, "sanity words absent from AoA table"
    ev["AOA_CSV_selftest"] = {"n_aoa": len(aoa_real), "n_freq": len(freq_real)}

    # --- the selectional slot_filler cache is really on disk and loads without re-extraction -------
    t0 = time.time()
    d = SEL.build_or_load(verbose=False)
    dt = time.time() - t0
    assert d.get("n_slots", 0) > 1000, "selectional slot table implausibly small: %r" % d.get("n_slots")
    assert dt < 60.0, ("build_or_load() took %.1fs -- the cache did not hit, this would re-extract "
                       "for ~38 minutes inside the full run" % dt)
    ev["SEL_build_or_load_selftest"] = {"n_slots": d["n_slots"], "load_t_s": round(dt, 2),
                                        "cache_hit": True}

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
        "signal_sourcing": {
            "S1_ATTESTATION": "REUSED VERBATIM from RSV: discrete coordination-pattern count over "
                              "raw sentence text, never touches the vector store.",
            "S2_TYPE_VIOLATION": "NEW: PMI-weighted cosine over verb-argument SLOT-MEMBERSHIP "
                                 "profiles, built from selectional_preference_extractor_v1's cached "
                                 "slot_filler table (64MB simplewiki corpus, POS-tagged + dependency "
                                 "parsed -- a DIFFERENT corpus from both the store and S1's "
                                 "attestation corpus, and never touches the vector store).",
            "S3_REGISTER": "NEW: Kuperman AoA, RESIDUALISED against word length and log-frequency "
                          "(both from the same AoA table) via OLS, then scored as a distance "
                          "similarity between candidate and query residuals.",
            "F_LENGTH_MATCHED / F_FREQUENCY_MATCHED": "NEW: the same distance-similarity scorer over "
                                                      "RAW (unresidualised) length / log-frequency -- "
                                                      "the ablation baselines S3 must beat.",
        },
    }

    # =============================================================================================
    # REGRESSION GATES -- ALWAYS on the FULL population, regardless of --grid (matches RSV/RCD).
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
        "partial_cue_hit1_FULL_POP": round(a0, 5), "expected": REG_A0_PARTIAL,
        "exact_key_hit1_FULL_POP": round(a1_k1, 5), "expected_k1": REG_A1_EXACT_K1,
        "exact_key_hit5_FULL_POP": round(a1_k5, 5), "expected_k5": REG_A1_EXACT_K5,
        "exact_key_hit10_FULL_POP": round(a1_k10, 5), "expected_k10": REG_A1_EXACT_K10,
        "exact_key_addressing_FULL_POP": round(addr_full, 5), "expected_addr": REG_ADDR_EXACT,
        "F_CONSTANT_PROTOTYPE_hit1_FULL_POP": round(fconst_k1, 5), "expected_fconst": REG_FCONST_K1,
        "tol": REGRESSION_TOL, "n_full": int(T_full.size),
        "source": "VERIFIED against data/exp_readout_shortlist_verifier_v1/metrics.json BEFORE this "
                  "cell was authored; regression constants imported from RSV's own module, not "
                  "retyped.",
    }
    reg["PASS"] = bool(
        abs(a0 - REG_A0_PARTIAL) <= REGRESSION_TOL
        and abs(a1_k1 - REG_A1_EXACT_K1) <= REGRESSION_TOL
        and abs(a1_k5 - REG_A1_EXACT_K5) <= REGRESSION_TOL
        and abs(a1_k10 - REG_A1_EXACT_K10) <= REGRESSION_TOL
        and abs(addr_full - REG_ADDR_EXACT) <= REGRESSION_TOL
        and abs(fconst_k1 - REG_FCONST_K1) <= REGRESSION_TOL)
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
        "pool": "the LANDED OPEN pool, identical to RSV",
        "gold": "WordNet 3.0 generous meaning set, exp_grounding_readout_known_answer_v1 UNMODIFIED",
        "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions, tie-corrected primary",
        "cue_regime_primary": "PARTIAL CUE (the real regime)",
    }
    S_ex_T = (MATn @ l2n(Q_exact_T).T).astype(np.float32)
    S_part_T = (MATn @ l2n(Q_part_T).T).astype(np.float32)
    print("[load] n_anchors=%d n_items=%d t=%.0fs" % (n_anchors, n_items, time.time() - t0),
         flush=True)

    # ---- VALIDITY: KA_SELF_ADDRESS + NULL_PERMUTED (global, on the exact-key cue) ----------------
    ok_q = qidx_T >= 0
    ka = float(np.mean(np.argmax(S_ex_T, axis=0)[ok_q] == qidx_T[ok_q]))
    rng_perm = np.random.default_rng(MASTER_SEED + 1201)
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
        raise SystemExit("KNOWN-ANSWER ARM (K1, BINDING) FAILED (%.4f < %.2f) -- no treatment "
                         "number is read" % (ka, KA_MIN))
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
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 1211))
                              @ l2n(Q_part_T).T).astype(np.float32)
    const_floor_vec = FB.constant_prototype_floor(mat, mat_ok)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_floor_vec, n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors,
                                  [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = {
        "cue": "PARTIAL", "names": sorted(floors_S),
        "never_imported_as_this_cells_own_result":
            ["0.1390", "0.1715", "0.2604", "0.3758", "0.0873", "0.1382", "0.2070", "-0.1959"]}

    hits_exp: Dict[str, np.ndarray] = {}
    winner_idx: Dict[str, np.ndarray] = {}

    def add_arm(name: str, Sx: np.ndarray, elig: np.ndarray, track_winner: bool = False) -> Dict:
        hh = FB.hit_at_1_both_tie_conventions(Sx, elig, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        if track_winner:
            winner_idx[name] = RSV.top1_index(Sx, elig)
        return hh

    for k_f, Sf in floors_S.items():
        add_arm(k_f, Sf, E_T)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S, E_T)
    add_arm("G0_ARGMAX", S_part_T, E_T, track_winner=True)

    # =============================================================================================
    # G1_SHORTLIST_ORACLE -- THE CEILING. Recomputed fresh (never imported), regression-checked.
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
    g1_partial_hit: Dict[int, np.ndarray] = {}
    for k in K_PARTIAL_GRID:
        arr = curve_partial["hit_at_k"]["opt"][k].astype(np.float64)
        hits_exp["G1_SHORTLIST_ORACLE_PARTIAL_k%d" % k] = arr
        hits_exp["RANDOM_RANKING_NULL_PARTIAL_k%d" % k] = rr[k]
        g1_partial[k] = float(arr.mean())
        g1_partial_hit[k] = arr > 0.5

    precond_v = g1_partial[50]
    precond_fail = bool(precond_v < RSV.PRECOND_ABS_THRESHOLD)
    g1_regression_check = {k: {"got": round(g1_partial[k], 5), "landed_reference": v,
                               "delta": round(g1_partial[k] - v, 5)}
                           for k, v in REG_G1_PARTIAL.items()}
    rep["G1_SHORTLIST_ORACLE"] = {
        "EXACT_KEY_curve": {str(k): round(v, 5) for k, v in g1_exact.items()},
        "PARTIAL_CUE_curve_THE_PRECONDITION": {str(k): round(v, 5) for k, v in g1_partial.items()},
        "random_ranking_null_curve": {str(k): round(float(rr[k].mean()), 5)
                                      for k in K_PARTIAL_GRID},
        "PRECOND_ABS_THRESHOLD": RSV.PRECOND_ABS_THRESHOLD,
        "precondition_value_at_k50": round(precond_v, 5),
        "PRECONDITION_FAILURE": precond_fail,
        "g1_partial_vs_RSV_landed_consistency_check": g1_regression_check,
        "reading": "recomputed fresh on this cell's own population; the RSV-landed values appear "
                  "only as a same-instrument consistency check, never adopted.",
    }
    print("[G1] EXACT k1/5/10=%.5f/%.5f/%.5f  PARTIAL k1/5/10/20/50=%s  PRECOND_FAIL=%s t=%.0fs"
         % (g1_exact[1], g1_exact[5], g1_exact[10],
            {k: round(v, 4) for k, v in g1_partial.items()}, precond_fail, time.time() - t0),
         flush=True)
    if precond_fail:
        rep["verdict"] = "STOPIF_II__PRECONDITION_FAILURE__PARTIAL_CUE_SHORTLIST_NEAR_ZERO_AT_K50"
        rep["verdict_msg"] = "G1_PARTIAL@k50=%.5f < %.2f -- no rejector work licensed." % (
            precond_v, RSV.PRECOND_ABS_THRESHOLD)
        rep["summary"] = rep["verdict"]
        rep["elapsed_s"] = round(time.time() - t0, 1)
        rep["run_mode"] = "full" if grid == "full" else "smoke"
        return rep

    # =============================================================================================
    # BUILD THE THREE SIGNAL SOURCES, ONCE.
    # =============================================================================================
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    from hdlab.reading_grounding_loop import normalize_lemma
    anchors_lemma = [normalize_lemma(a) for a in anchors]
    Lwords_T_lemma = [normalize_lemma(w) for w in L_words_T]
    vocab_set = set(anchors_lemma) | set(Lwords_T_lemma)

    # ---- S1_ATTESTATION source: REUSED VERBATIM from RSV -----------------------------------------
    t_s1 = time.time()
    sents = [s for _seg, s in load_corpus_v5(None, lineaware=True)]
    pair_counts = RSV.build_attestation_index(sents, vocab_set, normalize_lemma,
                                              window=RSV.COORD_WINDOW)
    rep["S1_ATTESTATION_INDEX"] = {"n_sentences": len(sents), "n_vocab": len(vocab_set),
                                   "n_pairs_attested": len(pair_counts),
                                   "window_tokens": RSV.COORD_WINDOW,
                                   "build_t_s": round(time.time() - t_s1, 1)}
    print("[S1] %d sentences -> %d attested coordination pairs t=%.0fs"
         % (len(sents), len(pair_counts), time.time() - t_s1), flush=True)
    del sents

    # ---- S2_TYPE_VIOLATION source: selectional_preference_extractor_v1's CACHED slot table --------
    t_s2 = time.time()
    sel_data = SEL.build_or_load(verbose=False)
    type_profile, type_norm, type_stats = build_type_profile(sel_data["slot_filler"], vocab_set)
    rep["S2_TYPE_PROFILE_SUPPLY"] = dict(type_stats, build_t_s=round(time.time() - t_s2, 1),
                                         source="experiments/selectional_preference_extractor_v1"
                                                ".build_or_load() -- cached, NOT re-extracted",
                                         corpus_bytes=sel_data.get("corpus_bytes"),
                                         corpus=sel_data.get("corpus"))
    print("[S2] slot table: %d slots, %d/%d target words profiled (%.1f%%), mean %.1f slots/word "
         "t=%.0fs" % (type_stats["n_slots_in_table"], type_stats["n_target_words_with_profile"],
                      type_stats["n_target_vocab"], 100 * type_stats["coverage_frac"],
                      type_stats["mean_slots_per_profiled_word"], time.time() - t_s2), flush=True)
    del sel_data

    # ---- S3_REGISTER source: Kuperman AoA, residualised against length + log-frequency ------------
    t_s3 = time.time()
    aoa_table, freq_table = load_aoa_and_freq(AOA_CSV)
    resid_aoa, resid_stats = residualize_aoa(vocab_set, aoa_table, freq_table)
    resid_std = resid_stats.get("resid_std", 0.0) or 1.0
    length_map = {w: float(len(w)) for w in vocab_set}
    length_std = float(np.std(list(length_map.values()))) or 1.0
    freq_map = {w: math.log1p(freq_table[w]) for w in vocab_set if w in freq_table}
    freq_std = float(np.std(list(freq_map.values()))) if freq_map else 0.0
    rep["S3_REGISTER_SUPPLY"] = dict(resid_stats, coverage_frac=round(
        resid_stats.get("n_words_residualized", 0) / max(len(vocab_set), 1), 4),
        n_target_vocab=len(vocab_set), source=AOA_CSV, build_t_s=round(time.time() - t_s3, 1))
    print("[S3] AoA coverage %d/%d words (%.1f%%), r2(length,freq->AoA)=%.4f, resid_std=%.4f t=%.0fs"
         % (resid_stats.get("n_words_residualized", 0), len(vocab_set),
            100 * rep["S3_REGISTER_SUPPLY"]["coverage_frac"],
            resid_stats.get("r2_of_length_freq_predicting_aoa", float("nan")), resid_std,
            time.time() - t_s3), flush=True)

    # =============================================================================================
    # THE MAIN SWEEP: S1 / S2 / S3 / N1 / N2 / F_LENGTH_MATCHED / F_FREQUENCY_MATCHED at each k,
    # PLUS the correlation-vs-proposer check computed IN THE SAME PASS (matches RSV's own ordering:
    # the SIGNAL_INDEPENDENCE table is assembled here and stored into `rep` BEFORE the MARGINS /
    # RECOVERY_FRACTION section below, so it precedes every lift number both in the dict and in the
    # console log).
    # =============================================================================================
    corr_with_proposer: Dict[str, Dict] = {}
    sig_scores_at_S4K: Dict[str, np.ndarray] = {}
    sl_at_k: Dict[int, np.ndarray] = {}
    for k in K_REJECTOR_GRID:
        sl = RSV.shortlist_mask(S_part_T, E_T, k)
        sl_at_k[k] = sl
        record_unit(output_dir, unit_key("SHORTLIST", k), {"n_selected": int(sl.sum())})

        S1_S = RSV.attestation_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, pair_counts)
        S2_S = type_violation_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, type_profile,
                                                    type_norm)
        S3_S = distance_sim_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, resid_aoa,
                                                  resid_std)
        FL_S = distance_sim_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, length_map,
                                                  length_std)
        FF_S = distance_sim_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, freq_map,
                                                  freq_std) if freq_map else np.zeros_like(S3_S)

        add_arm("S1_ATTESTATION_k%d" % k, S1_S, sl, track_winner=True)
        add_arm("S2_TYPE_VIOLATION_k%d" % k, S2_S, sl, track_winner=True)
        add_arm("S3_REGISTER_k%d" % k, S3_S, sl, track_winner=True)
        add_arm("F_LENGTH_MATCHED_k%d" % k, FL_S, sl, track_winner=True)
        add_arm("F_FREQUENCY_MATCHED_k%d" % k, FF_S, sl, track_winner=True)

        rng_n1 = np.random.default_rng(MASTER_SEED + 1301 + k)
        N1_S = rng_n1.random((n_anchors, n_items)).astype(np.float32)
        add_arm("N1_RANDOM_REJECTOR_k%d" % k, N1_S, sl, track_winner=True)

        add_arm("N2_PROPOSER_AS_REJECTOR_k%d" % k, S_part_T, sl, track_winner=True)
        if not np.array_equal(hits_exp["N2_PROPOSER_AS_REJECTOR_k%d" % k], hits_exp["G0_ARGMAX"]):
            raise SystemExit(
                "STOP-IF (iv): N2_PROPOSER_AS_REJECTOR does NOT reduce to G0_ARGMAX at k=%d -- the "
                "stages are NOT independent by this construction. THE CELL IS VOID. Nothing "
                "downstream is published." % k)

        # SIGNAL INDEPENDENCE FROM THE PROPOSER, made empirical -- computed and stored HERE, before
        # any margin/accuracy number is assembled below.
        r_idx, c_idx = np.nonzero(sl)
        prop_vals = S_part_T[r_idx, c_idx].astype(np.float64)
        from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
        corr_with_proposer["S1_ATTESTATION_k%d" % k] = pearson_ci_bootstrap(
            prop_vals, S1_S[r_idx, c_idx].astype(np.float64), seed=MASTER_SEED + 1401 + k,
            n_boot=1000)
        corr_with_proposer["S2_TYPE_VIOLATION_k%d" % k] = pearson_ci_bootstrap(
            prop_vals, S2_S[r_idx, c_idx].astype(np.float64), seed=MASTER_SEED + 1411 + k,
            n_boot=1000)
        corr_with_proposer["S3_REGISTER_k%d" % k] = pearson_ci_bootstrap(
            prop_vals, S3_S[r_idx, c_idx].astype(np.float64), seed=MASTER_SEED + 1421 + k,
            n_boot=1000)

        if k == S4_K:
            sig_scores_at_S4K["S1_ATTESTATION"] = S1_S
            sig_scores_at_S4K["S2_TYPE_VIOLATION"] = S2_S
            sig_scores_at_S4K["S3_REGISTER"] = S3_S

        record_unit(output_dir, unit_key("SWEEP", k), {
            "G1_partial": round(g1_partial.get(k, float("nan")), 4),
            "S1": round(float(hits_exp["S1_ATTESTATION_k%d" % k].mean()), 4),
            "S2": round(float(hits_exp["S2_TYPE_VIOLATION_k%d" % k].mean()), 4),
            "S3": round(float(hits_exp["S3_REGISTER_k%d" % k].mean()), 4),
            "N1": round(float(hits_exp["N1_RANDOM_REJECTOR_k%d" % k].mean()), 4),
            "N2_eq_G0": True})
        print("[sweep k=%d] S1=%.4f S2=%.4f S3=%.4f FL=%.4f FF=%.4f N1=%.4f N2==G0(verified) t=%.0fs"
             % (k, hits_exp["S1_ATTESTATION_k%d" % k].mean(),
                hits_exp["S2_TYPE_VIOLATION_k%d" % k].mean(),
                hits_exp["S3_REGISTER_k%d" % k].mean(),
                hits_exp["F_LENGTH_MATCHED_k%d" % k].mean(),
                hits_exp["F_FREQUENCY_MATCHED_k%d" % k].mean(),
                hits_exp["N1_RANDOM_REJECTOR_k%d" % k].mean(), time.time() - t0), flush=True)

    rep["SIGNAL_INDEPENDENCE_TABLE_r_vs_proposer"] = corr_with_proposer
    print("[independence] " + json.dumps({k: v.get("r") for k, v in corr_with_proposer.items()}),
         flush=True)

    # =============================================================================================
    # S4_COMBINED -- rank-normalised sum of whichever signals measured independent at k=S4_K.
    # Pre-registered rule: member iff |r| < INDEP_R_THRESHOLD at k=S4_K. Primary = equal weight.
    # Secondary (never adopted) = beta sweep, ONLY if exactly 2 signals qualify.
    # =============================================================================================
    r_at_s4k = {name: corr_with_proposer["%s_k%d" % (name, S4_K)].get("r")
               for name in ("S1_ATTESTATION", "S2_TYPE_VIOLATION", "S3_REGISTER")}
    independent_signals = sorted(name for name, r in r_at_s4k.items()
                                 if r is not None and abs(r) < INDEP_R_THRESHOLD)
    rep["S4_MEMBERSHIP_DECISION"] = {
        "INDEP_R_THRESHOLD": INDEP_R_THRESHOLD, "r_at_k%d" % S4_K: r_at_s4k,
        "independent_signals": independent_signals,
        "rule": "member iff |r vs proposer| < %.2f at k=%d; pre-registered before this run"
               % (INDEP_R_THRESHOLD, S4_K)}
    sl20 = sl_at_k[S4_K]
    s4_names: List[str] = []
    if independent_signals:
        ranks = {name: RSV.rank_normalize_within_shortlist(sig_scores_at_S4K[name], sl20)
                for name in independent_signals}
        combined_equal = sum(ranks[name] for name in independent_signals) / len(independent_signals)
        combined_equal[~sl20] = -1.0
        name_eq = "S4_COMBINED_k%d_equal_%s" % (S4_K, "_".join(independent_signals))
        add_arm(name_eq, combined_equal, sl20, track_winner=True)
        s4_names.append(name_eq)
        record_unit(output_dir, unit_key("S4", "equal"),
                   {"members": independent_signals, "value": round(
                       float(hits_exp[name_eq].mean()), 4)})
        print("[S4 equal] members=%r acc=%.4f" % (independent_signals, hits_exp[name_eq].mean()),
             flush=True)
        if len(independent_signals) == 2:
            a_name, b_name = independent_signals
            for beta in (0.25, 0.5, 0.75):
                combo = beta * ranks[a_name] + (1.0 - beta) * ranks[b_name]
                combo[~sl20] = -1.0
                nm = "S4_COMBINED_k%d_beta%g_%s_vs_%s" % (S4_K, beta, a_name, b_name)
                add_arm(nm, combo, sl20, track_winner=True)
                s4_names.append(nm)
                record_unit(output_dir, unit_key("S4", "beta%g" % beta),
                           {"value": round(float(hits_exp[nm].mean()), 4)})
                print("[S4 beta=%.2f] %.4f" % (beta, hits_exp[nm].mean()), flush=True)
    else:
        rep["S4_MEMBERSHIP_DECISION"]["status"] = (
            "S4_COMBINED_NOT_CONSTRUCTIBLE: no candidate signal measured independent of the "
            "proposer at k=%d" % S4_K)
        print("[S4] NOT CONSTRUCTIBLE -- no independent signal at k=%d" % S4_K, flush=True)

    # =============================================================================================
    # K1_KNOWN_ANSWER -- per-channel INFORMATIONAL check (own-address preference), on an EXACT-KEY
    # shortlist that certainly contains the item's own address. NOT gated for S1/S2/S3/S4 (all
    # explicitly exclude self-comparison by construction), matching RSV's rationale exactly.
    # =============================================================================================
    sl_ex_ka = RSV.shortlist_mask(S_ex_T, E_T, K_KA_SHORTLIST)
    S1_ex = RSV.attestation_scores_for_shortlist(sl_ex_ka, Lwords_T_lemma, anchors_lemma, pair_counts)
    S2_ex = type_violation_scores_for_shortlist(sl_ex_ka, Lwords_T_lemma, anchors_lemma, type_profile,
                                                type_norm)
    S3_ex = distance_sim_scores_for_shortlist(sl_ex_ka, Lwords_T_lemma, anchors_lemma, resid_aoa,
                                              resid_std)

    def _ka_of(S_channel: np.ndarray, elig: np.ndarray) -> float:
        top1 = RSV.top1_index(S_channel, elig)
        return float(np.mean(top1[ok_q] == qidx_T[ok_q]))

    own_address_preference_informational = {
        "PROPOSER_G0_KA_SELF_ADDRESS": ka,
        "S1_ATTESTATION_prefers_own_address": _ka_of(S1_ex, sl_ex_ka),
        "S2_TYPE_VIOLATION_prefers_own_address": _ka_of(S2_ex, sl_ex_ka),
        "S3_REGISTER_prefers_own_address": _ka_of(S3_ex, sl_ex_ka),
    }
    rep["K1_KNOWN_ANSWER"] = {
        "BINDING_GATE": "KA_SELF_ADDRESS on the store (>= %.2f, already enforced above): %.4f PASS"
                        % (KA_MIN, ka),
        "shortlist_k_for_informational_check": K_KA_SHORTLIST,
        "own_address_preference_INFORMATIONAL_NOT_GATED": {
            k_: round(v, 4) for k_, v in own_address_preference_informational.items()},
        "why_not_gated": "S1/S2/S3 all explicitly exclude self-comparison (qw==cw skipped) by "
                        "construction; a 'must prefer own identity' bar does not test anything "
                        "meaningful for them and is reported, not gated -- same rationale as RSV.",
    }
    del S1_ex, S2_ex, S3_ex, sl_ex_ka

    # =============================================================================================
    # ARMS_MUST_DIFFER (winner_idx selection identity, N2==G0 exempted -- same rationale as RSV)
    # =============================================================================================
    digests = {name: RSV.arm_digest(arr) for name, arr in winner_idx.items()}
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
        "collisions_besides_exemption": collisions, "PASS": bool(len(collisions) == 0)}
    if collisions:
        raise SystemExit("META_RULE_AF VIOLATION: bit-identical SELECTIONS outside the declared "
                         "exemption: %r" % collisions)
    print("[arms_differ] %d selection arms checked, 0 unexplained collisions" % len(digests),
         flush=True)

    # =============================================================================================
    # BOOTSTRAP -- all arms share ONE set of draws.
    # =============================================================================================
    scored_mask = np.ones(n_items, dtype=bool)
    for arr in hits_exp.values():
        scored_mask &= np.isfinite(arr)
    boot = FB.paired_bootstrap_ci(hits_exp, scored_mask, N_BOOT, MASTER_SEED + 1501)
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
        if arm.startswith("S4_COMBINED"):
            return S4_K
        return int(arm.rsplit("_k", 1)[1])

    margins: Dict[str, Dict] = {}
    real_rejector_arms = (["S1_ATTESTATION_k%d" % k for k in K_REJECTOR_GRID]
                          + ["S2_TYPE_VIOLATION_k%d" % k for k in K_REJECTOR_GRID]
                          + ["S3_REGISTER_k%d" % k for k in K_REJECTOR_GRID]
                          + s4_names)
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
        # S3-specific: does residualised register beat its own raw ablation controls?
        margins["S3_REGISTER_k%d__vs__F_LENGTH_MATCHED_k%d" % (k, k)] = \
            marg("S3_REGISTER_k%d" % k, "F_LENGTH_MATCHED_k%d" % k)
        margins["S3_REGISTER_k%d__vs__F_FREQUENCY_MATCHED_k%d" % (k, k)] = \
            marg("S3_REGISTER_k%d" % k, "F_FREQUENCY_MATCHED_k%d" % k)
    margins["G0_ARGMAX__vs__FLOOR(%s)" % binding_floor_name] = marg("G0_ARGMAX", binding_floor_name)
    rep["MARGINS"] = margins

    # ---- RECOVERY FRACTION: of the items where the gold IS in the shortlist (oracle succeeds at
    # that k), what fraction does each arm actually select? A hit for the arm is only possible when
    # the oracle also succeeds (asserted, not merely stated), so recovery_fraction = acc(arm) /
    # G1_partial_ceiling(k).
    recovery: Dict[str, Dict] = {}
    for arm in real_rejector_arms + ["N1_RANDOM_REJECTOR_k%d" % k for k in K_REJECTOR_GRID]:
        k = k_of(arm)
        oracle_mask = g1_partial_hit[k]
        arm_hits = hits_exp[arm] > 0.5
        assert not np.any(arm_hits & ~oracle_mask), (
            "%s hit on an item where the k=%d oracle did not -- shortlist construction is broken"
            % (arm, k))
        ceiling = g1_partial[k]
        acc = float(boot["acc"].get(arm, float(hits_exp[arm].mean())))
        recovery[arm] = {"k": k, "acc": round(acc, 5), "oracle_ceiling_at_k": round(ceiling, 5),
                         "recovery_fraction": round(acc / ceiling, 5) if ceiling > 0 else None}
    rep["RECOVERY_FRACTION"] = recovery

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

    # STOP-IF (ii): S2 independent-but-does-not-lift, checked explicitly regardless of the others.
    s2_r_at_s4k = r_at_s4k.get("S2_TYPE_VIOLATION")
    s2_independent = s2_r_at_s4k is not None and abs(s2_r_at_s4k) < INDEP_R_THRESHOLD
    s2_arms = ["S2_TYPE_VIOLATION_k%d" % k for k in K_REJECTOR_GRID]
    s2_lifts = any(beats_n1(a) for a in s2_arms)
    stop_ii_fired = bool(s2_independent and not s2_lifts)

    # rule 12 -- orthographic + word-length correlation on every clearing arm
    Sortho_T = floors_S.get("F_ORTHOGRAPHIC")
    word_len = np.array([len(a) for a in anchors], dtype=np.float64)
    from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
    rule12: Dict[str, Dict] = {}
    for arm in clearing_arms:
        k_arm = k_of(arm)
        sl_arm = sl_at_k.get(k_arm, sl20)
        if arm.startswith("S1_ATTESTATION"):
            Sarm_mat = RSV.attestation_scores_for_shortlist(sl_arm, Lwords_T_lemma, anchors_lemma,
                                                             pair_counts)
        elif arm.startswith("S2_TYPE_VIOLATION"):
            Sarm_mat = type_violation_scores_for_shortlist(sl_arm, Lwords_T_lemma, anchors_lemma,
                                                            type_profile, type_norm)
        elif arm.startswith("S3_REGISTER"):
            Sarm_mat = distance_sim_scores_for_shortlist(sl_arm, Lwords_T_lemma, anchors_lemma,
                                                          resid_aoa, resid_std)
        else:  # S4_COMBINED
            Sarm_mat = None
            for name in independent_signals:
                r_i = RSV.rank_normalize_within_shortlist(sig_scores_at_S4K[name], sl20)
                if "beta" in arm:
                    beta_here = float(arm.split("beta", 1)[1].split("_", 1)[0])
                    a_name, b_name = independent_signals
                    Sarm_mat = beta_here * RSV.rank_normalize_within_shortlist(
                        sig_scores_at_S4K[a_name], sl20) + (1.0 - beta_here) * \
                        RSV.rank_normalize_within_shortlist(sig_scores_at_S4K[b_name], sl20)
                    break
            if Sarm_mat is None:
                Sarm_mat = sum(RSV.rank_normalize_within_shortlist(sig_scores_at_S4K[name], sl20)
                              for name in independent_signals) / max(len(independent_signals), 1)
        top1 = RSV.top1_index(Sarm_mat, sl_arm)
        winner_len = word_len[top1]
        gain = hits_exp[arm] - hits_exp["G0_ARGMAX"]
        best_gold_ortho = np.where(GOLD_T & E_T, Sortho_T, -np.inf).max(axis=0) \
            if Sortho_T is not None else np.full(n_items, np.nan)
        ortho_corr = pearson_ci_bootstrap(gain, best_gold_ortho, seed=MASTER_SEED + 1601, n_boot=2000)
        len_corr = pearson_ci_bootstrap(gain, winner_len, seed=MASTER_SEED + 1611, n_boot=2000)
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
        "ii_S2_independent_but_no_lift": stop_ii_fired,
        "ii_detail": {"S2_r_at_k%d" % S4_K: s2_r_at_s4k, "S2_independent": s2_independent,
                     "S2_lifts_any_k": s2_lifts},
        "iii_shortlist_not_rejector_arms": stop_iii_shortlist_not_rejector,
        "iv_n2_void": False,  # would have raised SystemExit above if this had fired
        "v_rule12_failure_arms": rule12_fail,
        "clearing_arms_tested_for_rule12": clearing_arms,
        "RULE_12_DETAIL": rule12,
    }

    if stop_i_wins:
        verdict = "STOPIF_I__INDEPENDENT_REJECTOR_WIN__" + "_".join(stop_i_wins[:2])
    elif rule12_fail:
        verdict = "STOPIF_V__RULE12_ORTHOGRAPHIC_OR_LENGTH_LEAKAGE__" + "_".join(rule12_fail[:2])
    elif stop_iii_shortlist_not_rejector:
        verdict = "STOPIF_III__GAIN_IS_THE_SHORTLIST_NOT_THE_REJECTOR"
    elif stop_ii_fired:
        verdict = "STOPIF_II__S2_INDEPENDENT_BUT_NO_LIFT__INDEPENDENCE_NECESSARY_NOT_SUFFICIENT"
    else:
        verdict = "NO_INDEPENDENT_REJECTOR_CLEARS__REJECTOR_ROAD_MEASURED_AND_CLOSED"

    rep["verdict"] = verdict
    rep["verdict_msg"] = (
        "PRECOND(partial-cue G1@k50)=%.5f. BindingFloor=%s@%.5f. REAL_WIN_ARMS=%r. "
        "S2_independent=%s S2_lifts=%s. SHORTLIST_NOT_REJECTOR_ARMS=%r. RULE12_FAIL=%r. "
        "N2==G0 verified for all k (no VOID). S4 members=%r." % (
            precond_v, binding_floor_name, binding_floor_value, stop_i_wins, s2_independent,
            s2_lifts, stop_iii_shortlist_not_rejector, rule12_fail, independent_signals))
    rep["summary"] = verdict
    rep["elapsed_s"] = round(time.time() - t0, 1)
    rep["run_mode"] = "full" if grid == "full" else "smoke"
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = sorted(
        m for m in sys.modules
        if any(s in m for s in ("exp_readout_shortlist_verifier_v1", "exp_readout_ceiling_diagnosis_v1",
                                "exp_cue_to_store_translation_v1", "floor_battery",
                                "exp_cue_binarised_readout_transfer_v1", "exp_definitional_grounding_v5",
                                "reading_grounding_loop", "exp_checkpoint",
                                "selectional_preference_extractor_v1")))
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
