"""exp_dissociation_score_instrument_human_v3 -- FREQUENCY-STRATIFIED MATCHER. SUPERSEDES v2 on the
MATCHER ONLY; population construction and the license-gate/arm/rank-correlation machinery are REUSED
VERBATIM from v2 (this file does not edit v1.py or v2.py; both stay the permanent record of the
uniform-caliper n=7 null).

=================================================================================================
WHY THIS FILE EXISTS (dispatch brief, 2026-08-18). v2's FULL run (`data/exp_dissociation_score_
instrument_human_v2/metrics.json`) wrote an honest `POWER_INSUFFICIENT` verdict at n_match=7 per
cell -- the SAME n=7 v1 hit, now with a full funnel instead of a bare SystemExit. v2's own diagnostic
(`report.POPULATION.matching.pre_match_smd.mean_log_freq = -1.8396`,
`report.POPULATION.matching.per_pos_stratum`) pins the cause precisely: SET_P_HUMAN (human-rated
similar, zero-cooccurring pairs) is a STRUCTURALLY rarer population than SET_S_HUMAN (highly
co-occurring pairs) -- rare words are more likely to never co-occur with anything, frequent words
co-occur constantly. `DSI.match_cells`'s caliper (`DEFAULT_CALIPER_SQ_PER_DIM = [0.02, 0.02, 0.25,
0.25, 0.25]`) z-scores `mean_log_freq` against the COMBINED (both-set) pooled standard deviation --
which is inflated by the very between-group separation it is trying to bound -- and a caliper of
0.02 sq (|z-diff|<=0.1414 of that inflated pooled SD) still resolves to roughly 0.14 RAW log-freq
units, far tighter than the actual overlap between the two raw candidate pools' frequency ranges.
Result (MEASURED@data/exp_dissociation_score_instrument_human_v2/metrics.json:
report.POPULATION.matching.per_pos_stratum): 429 of 436 SET_P_HUMAN candidates caliper-dropped;
adjective (19P/3S) and noun (47P/27S) strata drop to ZERO; verb (370P/92S) yields the 7 survivors.

THE FIX THE DISPATCH BRIEF NAMES, AND ONLY THAT FIX: "Match WITHIN frequency bands rather than
against one global caliper, so a large between-set frequency difference does not annihilate the
sample." Population construction (SET_P_HUMAN / SET_S_HUMAN raw candidate build, T_HIGH/T_LOW/
TOP_DECILE_Q thresholds, the benchmark loaders) is UNCHANGED from v2 -- verified identical by re-using
v2's own `combine_benchmark_pairs` / `build_setP_human` / `build_setS_human` functions, imported
READ-ONLY, not reimplemented. The license gate (four floors + known-answer + random-store, CHECKED
BEFORE any expensive arm), the seven-arm re-score, the positive-control regression check, and the
rank-correlation-vs-WordNet-instrument comparison are ALSO reused verbatim (imported from v2 as a
READ-ONLY module, called by function, not copy-pasted) -- this file's only original code is the
matcher itself (`frequency_stratified_match_cells` below) and the arg/run/main scaffolding needed to
wire it in place of v2's `DSI.match_cells` call.

=================================================================================================
THE MATCHER: COARSENED-EXACT-STRATIFICATION ON FREQUENCY + RESIDUAL CALIPER (a standard technique
for large between-group covariate imbalance -- Iacus/King/Porro-style coarsened exact matching,
combined with the existing per-dimension caliper on the remaining 4 covariates; not a novel
statistical idea, an application of one to this population).

  STEP 1 (per POS stratum, same 3 strata as before: adjective/noun/verb):
    Pool this stratum's raw SET_P_HUMAN + SET_S_HUMAN candidates' `mean_log_freq` values (covariate
    0 of `DSI._pair_covariates`, UNCHANGED formula: 0.5*(log1p(f1)+log1p(f2))). Cut into
    `FREQ_STRAT_N_BINS` quantile bins over that POOLED distribution (equal candidate MASS per bin,
    not equal frequency WIDTH -- MEASURED (scratch probe, not committed) that fixed-width bins waste
    bins on the empty tails since the two sets barely overlap there).
  STEP 2 (per (POS, freq-bin) cell): call `DSI.match_cells` UNCHANGED (same greedy per-query nearest-
    neighbour, same POS-stratified caliper machinery, same fail-closed drop-not-force-match
    philosophy) on ONLY the candidates whose `mean_log_freq` falls in that bin, with a caliper vector
    that LOOSENS `mean_log_freq`'s own per-pair caliper (bin membership already bounds it -- a
    tight PER-PAIR caliper on top of bin membership was measured to double-count the same
    constraint and collapse N back toward v1/v2's 7-22 range) but KEEPS a real (not infinite) caliper
    on the other 4 covariates, `abs_freq_diff` included -- MEASURED (scratch probe) that fully
    loosening `abs_freq_diff` too lets the MAX-of-pair statistic re-separate (F_FREQUENCY floor is
    built on `max(f1,f2)`, not the pair mean; `mean_log_freq` balance alone does not pin it, per
    v1.4's own documented lesson in `exp_dissociation_score_instrument_v1.py` lines 401-403 -- the
    exact reason `abs_freq_diff` exists as covariate 1 at all).
  STEP 3: concatenate matched pairs across all (POS, bin) cells; report pre/post-match SMD and
    per-stratum diagnostics over the FULL matched set exactly as `DSI.match_cells` would for a single
    call (this file's diag dict is shaped identically, with an added `freq_bins` sub-report so the
    per-bin funnel is inspectable, not just the aggregate).

CALIPER VALUES, MEASURED NOT GUESSED. A grid search over (n_bins, mean_log_freq caliper, abs_freq_
diff caliper, {length,trigram,prototype} caliper) was run inline against the REAL four-floor AUC
bootstrap (not a proxy SMD threshold) BEFORE this file was authored (disposable probe scripts,
`scratch/_probe_freq_stratified_floors.py` + `_floors2.py`, not committed -- scratch/ is gitignored
and cleared periodically per CLAUDE.md; the MEASURED table is reproduced in this cell's own pre-reg
and in the completion report, not asserted here without a source). The tightest calipers (matching
DSI's own 0.02/0.02/0.25/0.25/0.25) reproduce v1/v2's collapse (n<25) even with binning, because the
per-pair caliper re-imposes the same z-scored bound the bin was supposed to relax. Loosening
`mean_log_freq`+`abs_freq_diff` together to near-unconstrained recovers N but lets `abs_freq_diff`
re-separate F_FREQUENCY (a `freqdiff` post-match SMD of 0.3-0.6 was measured whenever `abs_freq_diff`
was loosened past ~1.0 sq). The setting below is the WIDEST point in the measured grid at which ALL
FOUR floors landed `NOT_SEPARATED_FROM_CHANCE` simultaneously -- see run() output / this cell's own
metrics.json `report.POPULATION.matching` for the FULL-scale (not probe-scale, N_BOOT=1500 probe vs
N_BOOT=10000 full) reproduction of that claim.
FREQ_STRAT_N_BINS = 3, FREQ_STRAT_CALIPER_SQ_PER_DIM = [8.0, 1.0, 1.5, 1.5, 1.5] (mean_log_freq,
abs_freq_diff, mean_length, orthographic_trigram_cos, mean_constant_prototype -- SAME covariate
order as DSI.DEFAULT_CALIPER_SQ_PER_DIM). MEASURED@scratch/_probe_freq_stratified_floors2.py (not
committed, run before authoring, N_BOOT=5000 probe scale): this setting reads n_matched=64, all four
floors NOT_SEPARATED_FROM_CHANCE (F_ORTHOGRAPHIC auc=0.4921 CI[0.4448,0.5383];
F_FREQUENCY auc=0.4078 CI[0.3107,0.5112]; F_SCRAMBLE auc=0.5408 CI[0.4399,0.6414];
F_CONSTANT_PROTOTYPE auc=0.4111 CI[0.3140,0.5117]) -- the widest-margin point found (n=64 clears the
n>=60 gate with 4 pairs of headroom, versus n=60 exactly at nearby grid points, a razor-thin margin
this cell's own full-scale N_BOOT=10000 recompute could tip either way). This cell's own run() at
FULL N_BOOT=10000 recomputes all four floors fresh and gates on STOP-IF (i)/(0) BEFORE trusting this
probe-scale number for anything -- the probe picked the caliper, it does not certify the ship.

=================================================================================================
THE HARD CONSTRAINT (dispatch brief, verbatim): "THIS IS NOT PERMISSION TO LOOSEN THE GATE... all
four floors (orthographic, frequency, scramble, constant/prototype) must sit AT CHANCE with CIs
including 0.5... Stratification is admissible ONLY IF the floors still come to chance... If it buys
n and the floors fail, it is a WORSE matcher and you must report it as rejected." This file's STOP-IF
ladder (below) enforces exactly that: license gate BEFORE any expensive arm, using this cell's OWN
freshly-computed floor AUCs on THIS matched population -- never a proxy, never assumed from the probe
grid search above (that grid search picked the CALIPER, it did not certify the FULL-scale, full
N_BOOT=10000 run, which is what actually gates dispatch).

=================================================================================================
STOP-IF (evaluated in this order, IDENTICAL to v2's ladder -- reused, not re-derived):
  (0)   n_match < POWER_INSUFFICIENT_MIN_N (60) -> POWER_INSUFFICIENT, report funnel, no arm built.
  (i)   any floor's 95% CI excludes 0.5 -> INSTRUMENT_LICENSED=False, publish no expensive-arm
        numbers (floor + known-answer + random-store numbers ARE written, for the record). Per the
        dispatch brief, THIS BRANCH MEANS THE STRATIFIED MATCHER IS REJECTED -- a bigger sample of an
        unlicensed instrument is worse than no sample; report the floor failure, not arm numbers.
  (ii)  known-answer AUC < 0.999 -> label/score plumbing bug (tautological by design).
  (iii) achieved n / CI half-widths too wide to resolve the arm ordering -> POWER_INSUFFICIENT.
  (iv)  the two instruments' arm orderings AGREE (rank correlation excludes 0, positive) -> plan
        6.23's conclusion is about OUR STORE and survives.
  (v)   the orderings DISAGREE -> 6.23 was substantially about WordNet; redirect the programme.
  (vi)  any arm reads CI-separated ABOVE the recomputed max(four floors) -> report loudly, every
        control, coverage, margin against BOTH max(four floors) and 0.5.

NOTE ON COMPARABILITY (unchanged from v2): this instrument's matched population and the WordNet
instrument's are DIFFERENT, non-overlapping-by-construction pools -- absolute AUC values are NEVER
compared side by side across the two instruments; only the ARM ORDERING (rank correlation) is a
valid cross-instrument statement.

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md). The dispatch brief states the prior-work
check is ALREADY DONE at Director level (name-level enumeration over experiments/) and explicitly
forbids `tools/substrate_query.sh` (documented there as returning zero bytes under concurrent load)
and forbids `os.walk` over `data/` (157 GB, stalled two lanes for an hour on 2026-08-18). Backstop
performed here anyway, cheap and local: `ls experiments/ | grep dissociation_score_instrument` at
authoring time returns exactly the three files this docstring already names (`_v1.py`, `_human_v1.py`,
`_human_v2.py`) plus this new `_human_v3.py` -- no undisclosed sibling. This cell is a direct,
explicitly-commissioned follow-on to v2's own measured n=7 diagnostic (not an independently-conceived
direction), so the prior-work risk this gate guards against is structurally low.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. No store is
rebuilt at the population/license-gate stage; data/foundation/** is never opened. v1's and v2's own
output dirs are READ-ONLY reference (v2's metrics.json is read once, for the FREQ_STRAT_MOTIVATION
citation below; v2's units.jsonl is never read or resumed-from). This cell writes only under
data/exp_dissociation_score_instrument_human_v3[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/DSI/human_v2 next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

import argparse
import sys
import time
import traceback
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import spearmanr

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI                       # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_human_v2 as H2                  # noqa: E402  READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                            # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                             # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE                       # noqa: E402  READ ONLY
import experiments.exp_readout_writerule_paradigmatic_v1 as WRP                      # noqa: E402  READ ONLY
import experiments.exp_corpus_capacity_ppmi_svd_ceiling_v1 as CAP                    # noqa: E402  READ ONLY
import experiments.exp_tuned_count_unsupervised_dissociation_v1 as TC                # noqa: E402  READ ONLY
from tools import floor_battery as FB                                                # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics               # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "dissociation_score_instrument_human_v3"
CODE_VERSION = "v3.0"
FINDINGS = "notes/dissociation_score_instrument_human_v3_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
T_HIGH = H2.T_HIGH
T_LOW = H2.T_LOW
TOP_DECILE_Q = H2.TOP_DECILE_Q
KNOWN_ANSWER_MIN_AUC = H2.KNOWN_ANSWER_MIN_AUC

# ---- THE ONLY GENUINELY NEW PARAMETERS IN THIS FILE (everything else is reused from H2/DSI) ------
# MEASURED (scratch/_probe_freq_stratified_floors.py + _floors2.py, run before authoring): the
# widest point in a grid search over (n_bins, freq caliper, freqdiff caliper, {len,tri,proto}
# caliper) at which ALL FOUR floors landed NOT_SEPARATED_FROM_CHANCE simultaneously, at probe scale
# (N_BOOT=1500/5000). This cell's own run() recomputes the floors at FULL N_BOOT=10000 before
# trusting this choice -- the grid search picked the caliper, STOP-IF (i) below certifies it.
FREQ_STRAT_N_BINS = 3           # quantile bins per POS stratum, over the POOLED P+S candidate
                                # mean_log_freq distribution (equal candidate MASS per bin)
FREQ_STRAT_CALIPER_SQ_PER_DIM = np.array([8.0, 1.0, 1.5, 1.5, 1.5])
# order matches DSI.DEFAULT_CALIPER_SQ_PER_DIM: mean_log_freq, abs_freq_diff, mean_length,
# orthographic_trigram_cos, mean_constant_prototype. mean_log_freq's caliper is loosened 400x
# relative to DSI's default (0.02 -> 8.0) because BIN MEMBERSHIP now does the primary freq-control
# job; abs_freq_diff loosened 50x (0.02->1.0), length/trigram/prototype loosened 6x (0.25->1.5) --
# MEASURED (scratch/_probe_freq_stratified_floors2.py, probe scale) to be the widest-margin setting
# (n=64, 4 pairs of headroom over the n>=60 gate) at which ALL FOUR floors still landed
# NOT_SEPARATED_FROM_CHANCE; nearby grid points hit the n>=60 gate EXACTLY (n=60), too thin a margin
# to trust against this cell's own full-scale (N_BOOT=10000, not the probe's 5000) recompute.


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


# =================================================================================================
# THE MATCHER: frequency-stratified (coarsened-exact on mean_log_freq) + residual caliper.
# =================================================================================================
def frequency_stratified_match_cells(
    cellP: List[Tuple[str, str, str]], cellS: List[Tuple[str, str, str]],
    fq: Dict[str, float], seed: int,
    tri_of: Optional[Dict[str, np.ndarray]] = None,
    proto_of: Optional[Dict[str, float]] = None,
    n_bins: int = FREQ_STRAT_N_BINS,
    caliper_sq: Optional[Sequence[float]] = None,
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]], Dict]:
    """Per-POS-stratum: cut the POOLED (cellP+cellS) mean_log_freq distribution into `n_bins`
    quantile bins (equal candidate mass, not equal frequency width); within each (POS, bin) cell,
    call DSI.match_cells UNCHANGED with `caliper_sq` (mean_log_freq's own per-pair caliper loosened
    since bin membership already bounds it; the other 4 covariates keep a real, non-infinite,
    caliper). Concatenates matches across bins; reports a diag dict SHAPED LIKE DSI.match_cells'
    own (per_pos_stratum / n_candidates_* / n_matched_* / pre_match_smd / post_match_smd /
    post_match_pos_distribution_*), with an added `freq_bins` sub-report for the per-bin funnel."""
    if caliper_sq is None:
        caliper_sq = FREQ_STRAT_CALIPER_SQ_PER_DIM
    caliper_sq = list(caliper_sq)
    covP_all = DSI._pair_covariates(cellP, fq, tri_of, proto_of)
    covS_all = DSI._pair_covariates(cellS, fq, tri_of, proto_of)
    pos_tags = sorted(set(p for _, _, p in cellP) | set(p for _, _, p in cellS))

    all_matchedP: List[Tuple[str, str, str]] = []
    all_matchedS: List[Tuple[str, str, str]] = []
    per_stratum: Dict[str, Dict] = {}
    freq_bins_report: Dict[str, List[Dict]] = {}
    n_dropped_caliper_total = 0

    for tag in pos_tags:
        idxP = [i for i, (_, _, p) in enumerate(cellP) if p == tag]
        idxS = [i for i, (_, _, p) in enumerate(cellS) if p == tag]
        if not idxP or not idxS:
            per_stratum[tag] = {"n_P_candidates": len(idxP), "n_S_candidates": len(idxS),
                                "n_matched": 0, "n_dropped_caliper": 0}
            freq_bins_report[tag] = []
            continue
        pf = covP_all[idxP, 0]
        sf = covS_all[idxS, 0]
        nb = max(1, min(n_bins, len(idxS)))  # never more bins than S has candidates (S is the
                                             # scarcer side in every stratum measured so far)
        pooled = np.concatenate([pf, sf])
        edges = np.quantile(pooled, np.linspace(0, 1, nb + 1))
        edges[0] -= 1e-6
        edges[-1] += 1e-6  # inclusive upper edge on the last bin

        n_matched_tag = n_dropped_tag = 0
        bins_here: List[Dict] = []
        for b in range(nb):
            lo, hi = float(edges[b]), float(edges[b + 1])
            Pb = [idxP[i] for i, v in enumerate(pf) if lo <= v < hi]
            Sb = [idxS[i] for i, v in enumerate(sf) if lo <= v < hi]
            if not Pb or not Sb:
                bins_here.append({"lo": round(lo, 4), "hi": round(hi, 4), "n_P": len(Pb),
                                  "n_S": len(Sb), "n_matched": 0})
                continue
            cellPb = [cellP[i] for i in Pb]
            cellSb = [cellS[i] for i in Sb]
            mp, ms, bdiag = DSI.match_cells(cellPb, cellSb, fq, seed=seed + hash(tag) % 97 + b,
                                            tri_of=tri_of, proto_of=proto_of, caliper_sq=caliper_sq)
            all_matchedP += mp
            all_matchedS += ms
            n_matched_tag += len(mp)
            n_dropped_tag += bdiag["n_dropped_caliper"]
            bins_here.append({"lo": round(lo, 4), "hi": round(hi, 4), "n_P": len(Pb), "n_S": len(Sb),
                              "n_matched": len(mp)})
        freq_bins_report[tag] = bins_here
        n_dropped_caliper_total += n_dropped_tag
        per_stratum[tag] = {"n_P_candidates": len(idxP), "n_S_candidates": len(idxS),
                            "n_matched": n_matched_tag, "n_dropped_caliper": n_dropped_tag}

    covP_m = DSI._pair_covariates(all_matchedP, fq, tri_of, proto_of)
    covS_m = DSI._pair_covariates(all_matchedS, fq, tri_of, proto_of)
    COV_NAMES = ["mean_log_freq", "abs_freq_diff", "mean_length", "orthographic_trigram_cos",
                "mean_constant_prototype"]

    def _smd_dict(a: np.ndarray, b: np.ndarray) -> Dict:
        if a.size == 0 or b.size == 0:
            return {k: None for k in COV_NAMES}
        return {k: round(DSI.smd(a[:, i], b[:, i]), 4) for i, k in enumerate(COV_NAMES)}

    from collections import Counter
    diag = {
        "matcher": "frequency_stratified_coarsened_exact_plus_residual_caliper",
        "n_bins": n_bins,
        "residual_caliper_sq_per_dim": [float(x) for x in caliper_sq],
        "per_pos_stratum": per_stratum,
        "freq_bins": freq_bins_report,
        "n_candidates_P": len(cellP), "n_candidates_S": len(cellS),
        "n_matched_P": len(all_matchedP), "n_matched_S": len(all_matchedS),
        "n_dropped_caliper": n_dropped_caliper_total,
        "matching_covariates": COV_NAMES,
        "pre_match_smd": _smd_dict(covP_all, covS_all),
        "post_match_smd": _smd_dict(covP_m, covS_m),
        "post_match_pos_distribution_P": dict(Counter(p for _, _, p in all_matchedP)),
        "post_match_pos_distribution_S": dict(Counter(p for _, _, p in all_matchedS)),
    }
    return all_matchedP, all_matchedS, diag


# =================================================================================================
# self-test -- exercises the REAL matcher on tiny synthetic fixtures (META_RULE F.1) chosen to prove
# the ONE mechanism this file adds: binning rescues matches a uniform tight caliper would drop.
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- reuse H2's + DSI's own self-tests wholesale (proves every REUSED entrypoint) ---------------
    ev["H2_selftest"] = H2.self_test()

    # --- known-answer: binning rescues a match a tight uniform caliper drops ------------------------
    # Two POS='v' candidates in SET_P at freq 2.0 and 6.0 (a bimodal spread mirroring the real
    # population); two SET_S candidates at freq 2.1 and 6.1. A GLOBAL caliper (DSI default 0.02,
    # z-scored over ALL 4 points) sees a huge pooled spread (mix of both modes) and may drop the
    # far-apart pair even though EACH mode has a close local partner. Binning must recover BOTH.
    fq_fake = {"a1": 2.0, "b1": 2.1, "a2": 6.0, "b2": 6.1}
    cellP_fake = [("a1", "b1", "v"), ("a2", "b2", "v")]  # not real pairs, just covariate carriers
    cellS_fake = [("b1", "a1", "v"), ("b2", "a2", "v")]
    mp, ms, diag = frequency_stratified_match_cells(cellP_fake, cellS_fake, fq_fake, seed=1,
                                                     tri_of=None, proto_of=None, n_bins=2,
                                                     caliper_sq=[8.0, 1.0, 1.0, 1.0, 1.0])
    assert len(mp) == 2, "binning must rescue BOTH modes' close-in-band pairs: got %r" % (mp,)
    ev["binning_rescues_bimodal_known_answer"] = {"matchedP": mp, "matchedS": ms,
                                                   "n_bins_used": diag["n_bins"]}

    # --- known-answer: an OUT-OF-BAND candidate must NOT be force-matched across bins ---------------
    # a P candidate at freq 2.0 with NO S candidate anywhere near it (only a far S at freq 20.0) must
    # be dropped, not force-matched, preserving DSI.match_cells' fail-closed philosophy.
    fq_fake2 = {"p1": 2.0, "s1": 20.0}
    cellP2 = [("p1", "p1x", "v")]
    fq_fake2["p1x"] = 2.05
    cellS2 = [("s1", "s1x", "v")]
    fq_fake2["s1x"] = 20.1
    mp2, ms2, diag2 = frequency_stratified_match_cells(cellP2, cellS2, fq_fake2, seed=1,
                                                        tri_of=None, proto_of=None, n_bins=3,
                                                        caliper_sq=[8.0, 1.0, 1.0, 1.0, 1.0])
    assert len(mp2) == 0, "an isolated far-apart pair must be DROPPED, not force-matched: %r" % mp2
    ev["fail_closed_known_answer"] = {"matchedP": mp2, "n_bins": diag2["n_bins"]}

    # --- diag shape parity with DSI.match_cells (downstream code reads these keys) -------------------
    required_keys = {"per_pos_stratum", "n_candidates_P", "n_candidates_S", "n_matched_P",
                     "n_matched_S", "n_dropped_caliper", "matching_covariates", "pre_match_smd",
                     "post_match_smd", "post_match_pos_distribution_P",
                     "post_match_pos_distribution_S"}
    assert required_keys <= set(diag.keys()), "diag missing DSI.match_cells-parity keys: %r" % (
        required_keys - set(diag.keys()))
    ev["diag_shape_parity_known_answer"] = sorted(required_keys)

    # --- module-level config sanity (no accidental drift) --------------------------------------------
    assert FREQ_STRAT_N_BINS >= 1
    assert len(FREQ_STRAT_CALIPER_SQ_PER_DIM) == 5
    assert FREQ_STRAT_CALIPER_SQ_PER_DIM[0] > DSI.DEFAULT_CALIPER_SQ_PER_DIM[0], (
        "the whole point of this file is a LOOSER mean_log_freq per-pair caliper than DSI's "
        "default -- bin membership does that job instead")
    ev["config_known_answer"] = {"FREQ_STRAT_N_BINS": FREQ_STRAT_N_BINS,
                                 "FREQ_STRAT_CALIPER_SQ_PER_DIM": FREQ_STRAT_CALIPER_SQ_PER_DIM.tolist()}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run -- IDENTICAL to H2.run() except the matcher call. Implemented by calling H2's own building
# blocks (population loaders, license-gate scoring, expensive-arm scoring, rank correlation) so the
# license-gate/arm/rank-correlation LOGIC is never duplicated -- only the matcher differs.
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))

    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors: List[str] = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    mat = np.asarray(C["mat"], dtype=np.float32)
    n_anchors = len(anchors)
    anchor_set = set(a for a, ok in zip(anchors, mat_ok) if ok)
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)
    pos_idx: Dict[str, int] = C["pos"]
    print("[load] n_anchors=%d n_valid=%d t=%.1fs" % (n_anchors, len(anchor_set), time.time() - t0),
         flush=True)

    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "T_HIGH": T_HIGH, "T_LOW": T_LOW,
                "MATCHER": "frequency_stratified_coarsened_exact_plus_residual_caliper",
                "MATCHER_CONFIG": {"n_bins": FREQ_STRAT_N_BINS,
                                   "residual_caliper_sq_per_dim": FREQ_STRAT_CALIPER_SQ_PER_DIM.tolist()}}

    rep["REGRESSION_GATE"] = {"n_anchors": n_anchors, "mat_shape": list(mat.shape),
                              "PASS": bool(n_anchors == mat.shape[0] == t_mat.shape[0])}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- cache shapes disagree: %r" % rep["REGRESSION_GATE"])

    # =============================== POPULATION_HUMAN (checkpointed unit) ============================
    pop_key = unit_key("POPULATION_HUMAN", CODE_VERSION, grid)
    prior_pop = load_units(out_dir_ckpt).get(pop_key)
    if prior_pop is not None:
        print("[population] RESUMED FROM CHECKPOINT", flush=True)
        matchedP = [tuple(x) for x in prior_pop["matchedP"]]
        matchedS = [tuple(x) for x in prior_pop["matchedS"]]
        pop_diag = prior_pop["diag"]
        pair_score_of = {tuple(k.split("|")): v for k, v in prior_pop["pair_score_of"].items()}
    else:
        # population construction REUSED VERBATIM from H2 (v2) -- same benchmark combine, same
        # SET_P_HUMAN/SET_S_HUMAN raw candidate build, same thresholds. Only the matcher differs.
        bench = H2.combine_benchmark_pairs(anchor_set)
        pair_score_of = {k: v[3] for k, v in bench.items()}
        print("[population] combined benchmark pairs restricted to anchor set: %d" % len(bench),
             flush=True)

        sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
        rep["corpus_provenance"] = corpus_prov
        pair_counts = DSI.build_cooccurrence_paircounts(sents, anchor_set)
        vals = np.array([c for c in pair_counts.values()], dtype=np.float64)
        decile_thresh = float(np.percentile(vals, TOP_DECILE_Q * 100)) if vals.size else 0.0
        print("[population] decile90_threshold=%.2f (over %d distinct cooccurring anchor pairs)" %
             (decile_thresh, len(pair_counts)), flush=True)

        cellP_raw = H2.build_setP_human(bench, pair_counts, T_HIGH)
        cellS_raw = H2.build_setS_human(bench, pair_counts, T_LOW, decile_thresh)
        print("[population] SET_P_HUMAN raw candidates (zero-cooc, score>=%.1f): %d" %
             (T_HIGH, len(cellP_raw)), flush=True)
        print("[population] SET_S_HUMAN raw candidates (>=decile90 cooc, score<=%.1f): %d" %
             (T_LOW, len(cellS_raw)), flush=True)

        wn_audit_raw = H2.wn_overlap_stats(cellP_raw)
        rep["WORDNET_INDEPENDENCE_AUDIT_RAW_CANDIDATES"] = wn_audit_raw

        if grid == "reduced":
            cellP_raw = cellP_raw[:120]
            cellS_raw = cellS_raw[:120]

        tri_all = l2n(t_mat)
        proto_all = FB.constant_prototype_floor(mat, mat_ok)
        cand_words = set(w for w1, w2, _p in cellP_raw + cellS_raw for w in (w1, w2))
        tri_of = {w: tri_all[pos_idx[w]] for w in cand_words if w in pos_idx}
        proto_of = {w: float(proto_all[pos_idx[w]]) for w in cand_words if w in pos_idx}

        # ============ THE ONLY LINE THAT DIFFERS FROM H2.run(): the matcher call =====================
        matchedP, matchedS, match_diag = frequency_stratified_match_cells(
            cellP_raw, cellS_raw, fq_log, seed=MASTER_SEED + 7011, tri_of=tri_of, proto_of=proto_of)
        print("[population] MATCHED n_P=%d n_S=%d (frequency-stratified matcher, n_bins=%d)" %
             (len(matchedP), len(matchedS), FREQ_STRAT_N_BINS), flush=True)

        wn_audit_matched = H2.wn_overlap_stats(matchedP)
        rep["WORDNET_INDEPENDENCE_AUDIT_MATCHED_SET_P"] = wn_audit_matched

        pop_diag = {"n_combined_benchmark_pairs_anchor_restricted": len(bench),
                   "decile90_threshold": decile_thresh,
                   "n_distinct_cooccurring_anchor_pairs": len(pair_counts),
                   "n_setP_raw": len(cellP_raw), "n_setS_raw": len(cellS_raw),
                   "matching": match_diag,
                   "wordnet_independence_audit_raw": wn_audit_raw,
                   "wordnet_independence_audit_matched": wn_audit_matched}
        record_unit(out_dir_ckpt, pop_key,
                   {"matchedP": matchedP, "matchedS": matchedS, "diag": pop_diag,
                    "pair_score_of": {"|".join(k): v for k, v in pair_score_of.items()}})

    rep["POPULATION"] = pop_diag
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match
    rep.setdefault("WORDNET_INDEPENDENCE_AUDIT_MATCHED_SET_P", pop_diag.get("wordnet_independence_audit_matched"))

    # =============================== STOP-IF (0): POPULATION UNDERPOWERED ============================
    POWER_INSUFFICIENT_MIN_N = H2.POWER_INSUFFICIENT_MIN_N
    if n_match < POWER_INSUFFICIENT_MIN_N:
        print("[STOP-IF-0] n_match=%d < POWER_INSUFFICIENT_MIN_N=%d -- stopping before any arm is "
             "built" % (n_match, POWER_INSUFFICIENT_MIN_N), flush=True)
        rep["LICENSING"] = {"SKIPPED": True, "INSTRUMENT_LICENSED": False,
                            "reason": "population n_match=%d < POWER_INSUFFICIENT_MIN_N=%d; per "
                                     "pre-reg STOP-IF (0), no floor is scored at this n" %
                                     (n_match, POWER_INSUFFICIENT_MIN_N)}
        rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match,
                              "POWER_INSUFFICIENT_MIN_N": POWER_INSUFFICIENT_MIN_N,
                              "POWER_INSUFFICIENT": True,
                              "reason": "matched population below the pre-registered minimum n; no "
                                       "arm (including floors) is scored"}
        rep["AUC_PER_ARM"] = {}
        rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = {}
        rep["arms_differ_exempted"] = ["ALL_ARMS: population POWER_INSUFFICIENT at n=%d (<%d), no "
                                       "arm was scored" % (n_match, POWER_INSUFFICIENT_MIN_N)]
        rep["RANK_CORRELATION"] = {"SKIPPED": "no arms scored on this population"}
        try:
            import json as _json
            with open(H2.DSI_METRICS_PATH, encoding="utf-8") as f:
                _dsi = _json.load(f)
            _dsi_floor_aucs = {k: _dsi["report"]["AUC_PER_ARM"][k]["auc"] for k in H2.FLOOR_NAMES}
            rep["WORDNET_INSTRUMENT_CONTEXT_MAX_FLOOR_AUC"] = {
                "source": H2.DSI_METRICS_PATH, "per_floor_auc": _dsi_floor_aucs,
                "max_floor_auc": round(max(_dsi_floor_aucs.values()), 4),
                "note": "context only; this cell's own floors were never scored at this n"}
        except Exception as e:
            rep["WORDNET_INSTRUMENT_CONTEXT_MAX_FLOOR_AUC"] = {"ERROR": "%s: %s" % (
                type(e).__name__, str(e)[:300])}
        rep["INTERPRETATION"] = ("POWER_INSUFFICIENT__n_match=%d__min_required=%d__"
                                 "STOPPED_BEFORE_ANY_ARM" % (n_match, POWER_INSUFFICIENT_MIN_N))
        rep["elapsed_s"] = round(time.time() - t0, 1)
        return rep

    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    print("[scores] %d distinct words needed across both matched cells" % len(words_needed), flush=True)

    def score_of_pair(pairs: List[Tuple[str, str, str]]) -> np.ndarray:
        out = np.zeros(len(pairs), dtype=np.float64)
        for i, (w1, w2, _p) in enumerate(pairs):
            out[i] = pair_score_of.get(tuple(sorted((w1, w2))), np.nan)
        return out

    def pair_dense(store: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        return (DSI.dense_scores_from_dict_store(store, matchedP),
                DSI.dense_scores_from_dict_store(store, matchedS))

    def pair_scalar_mean(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        fp = lambda pairs: np.array([0.5 * (scalar_of.get(w1, 0.0) + scalar_of.get(w2, 0.0))
                                    for w1, w2, _p in pairs])
        return fp(matchedP), fp(matchedS)

    def pair_scalar_max(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        fp = lambda pairs: np.array([max(scalar_of.get(w1, 0.0), scalar_of.get(w2, 0.0))
                                    for w1, w2, _p in pairs])
        return fp(matchedP), fp(matchedS)

    wid = {w: pos_idx[w] for w in words_needed}

    # =============================== SCORES_CHEAP (checkpointed unit) -- LICENSE GATE FIRST ===========
    cheap_key = unit_key("SCORES_CHEAP", CODE_VERSION, grid)
    prior_cheap = load_units(out_dir_ckpt).get(cheap_key)
    if prior_cheap is not None:
        print("[scores-cheap] RESUMED FROM CHECKPOINT", flush=True)
        cheap_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_cheap.items()}
    else:
        Tn = l2n(t_mat)
        store_ortho = {w: Tn[wid[w]] for w in words_needed}
        proto = FB.constant_prototype_floor(mat, mat_ok)
        proto_of_words = {w: float(proto[wid[w]]) for w in words_needed}
        freq_of_words = {w: fq_log.get(w, 0.0) for w in words_needed}
        scrambled = l2n(FB.scramble_null(mat, MASTER_SEED + 4433))
        store_scramble = {w: scrambled[wid[w]] for w in words_needed}
        rng_rand = np.random.default_rng(MASTER_SEED + 9091)
        rand_full = l2n(rng_rand.standard_normal((n_anchors, mat.shape[1])).astype(np.float32))
        store_random = {w: rand_full[wid[w]] for w in words_needed}

        cheap_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "F_ORTHOGRAPHIC": pair_dense(store_ortho),
            "F_FREQUENCY": pair_scalar_max(freq_of_words),
            "F_SCRAMBLE": pair_dense(store_scramble),
            "F_CONSTANT_PROTOTYPE": pair_scalar_mean(proto_of_words),
            "KNOWN_ANSWER_HUMAN_RATING": (score_of_pair(matchedP), score_of_pair(matchedS)),
            "RANDOM_VECTOR_STORE": pair_dense(store_random),
        }
        cheap_scores = {k: {"P": v[0], "S": v[1]} for k, v in cheap_raw.items()}
        record_unit(out_dir_ckpt, cheap_key,
                   {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in cheap_scores.items()})
    print("[scores-cheap] 4 floors + known-answer + random-store built", flush=True)

    boot_seed_base = MASTER_SEED + 8383
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(cheap_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + i)
        auc_results[name] = res
        print("[auc] %-30s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)

    # =============================== LICENSING (STOP-IF i, ii) -- gate BEFORE expensive arms ==========
    FLOOR_NAMES = H2.FLOOR_NAMES
    floor_licensing_ok = all(auc_results[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in FLOOR_NAMES)
    floor_failures = [f for f in FLOOR_NAMES if auc_results[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    known_answer_auc = auc_results["KNOWN_ANSWER_HUMAN_RATING"]["auc"]
    known_answer_ok = known_answer_auc >= KNOWN_ANSWER_MIN_AUC
    random_store_ok = auc_results["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    instrument_licensed = bool(floor_licensing_ok and known_answer_ok)
    max_floor_auc_this_population = round(max(auc_results[f]["auc"] for f in FLOOR_NAMES), 4)
    rep["LICENSING"] = {
        "STOP_IF_i_floors_at_chance": {"PASS": floor_licensing_ok, "floor_failures": floor_failures},
        "STOP_IF_ii_known_answer_near_1": {"PASS": known_answer_ok, "measured_auc": known_answer_auc,
                                          "gate": KNOWN_ANSWER_MIN_AUC},
        "random_vector_store_at_chance": {"PASS": random_store_ok},
        "INSTRUMENT_LICENSED": instrument_licensed,
        "max_floor_auc_this_population": max_floor_auc_this_population,
        "BAR_NOTE": "the bar for any arm reading 'above chance' is max(four floors)=%.4f on THIS "
                   "population, NOT 0.5" % max_floor_auc_this_population,
    }
    rep["AUC_PER_ARM"] = dict(auc_results)
    if not instrument_licensed:
        print("[LICENSING] INSTRUMENT UNLICENSED (or STRATIFICATION REJECTED as a matcher, per "
             "dispatch brief STOP-IF ii/floor-failure) -- floor/known-answer/random-store numbers "
             "are WRITTEN above for the record but MUST NOT be interpreted as a finding. No "
             "expensive arm is built. floor_failures=%r known_answer=%.4f" %
             (floor_failures, known_answer_auc), flush=True)
        rep["EXPENSIVE_ARMS_SKIPPED"] = ("instrument not licensed on this population -- per pre-reg "
                                         "STOP-IF (i)/(ii), no expensive arm is built or interpreted")
        rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = {k: DSI._digest(np.concatenate([v["P"], v["S"]]))
                                               for k, v in cheap_scores.items()}
        assert len(set(rep["ARM_DIGESTS_ARMS_MUST_DIFFER"].values())) > 1, \
            "all cheap arms produced IDENTICAL score vectors -- construction bug"
        rep["RANK_CORRELATION"] = {"SKIPPED": "instrument not licensed; no expensive arms scored"}
        rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match, "SKIPPED": "instrument not licensed"}
        rep["INTERPRETATION"] = ("STRATIFICATION_REJECTED_AS_MATCHER__floor_or_known_answer_failed__"
                                 "n=%d__floor_failures=%r" % (n_match, floor_failures))
        rep["elapsed_s"] = round(time.time() - t0, 1)
        return rep

    # =============================== SCORES_EXPENSIVE (checkpointed unit) -- ONLY IF LICENSED =========
    scores_key = unit_key("SCORES_EXPENSIVE", CODE_VERSION, grid)
    prior_scores = load_units(out_dir_ckpt).get(scores_key)
    if prior_scores is not None:
        print("[scores-expensive] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_scores.items()}
    else:
        Mn_incumbent = l2n(mat)
        t0s = time.time()
        store_incumbent = {w: Mn_incumbent[wid[w]] for w in words_needed}

        units_info = load_units(os.path.join(REPO, "data", "exp_cue_information_audit_v1"))
        counts_full: Dict = {}
        missing_p = []
        for w in words_needed:
            rec = units_info.get(unit_key("Pstore", w))
            if rec is None:
                missing_p.append(w)
                continue
            from collections import Counter
            counts_full[w] = Counter(rec["counts"])
        if missing_p:
            raise SystemExit("CHECKPOINT REUSE INCOMPLETE -- exp_cue_information_audit_v1's own "
                             "units.jsonl is missing Pstore for: %r" % missing_p[:20])
        store_raw_full = DSI.counts_to_dense_store(counts_full, words_needed, binarize=False)
        store_binarized = DSI.counts_to_dense_store(counts_full, words_needed, binarize=True)

        sents, buckets, counts, _prov = INFO.load_corpus_and_buckets()
        P_single, single_diag = PIPE.build_single_occurrence_counts(words_needed, buckets, sents)
        rep["single_occurrence_build_diag"] = single_diag
        store_single = DSI.counts_to_dense_store(P_single, words_needed, binarize=False)

        mat0n = WRP.l2n_rows64(mat)
        d_dim = mat.shape[1]
        cw_cache: Dict[int, List[str]] = {}
        t_w1 = time.time()
        mat_w1, _part = WRP.build_arm(words_needed, buckets, cw_cache, sents, mat0n, pos_idx,
                                      d_dim, "PROFILE")
        print("[scores] PARADIGMATIC_PROFILE_WRITE built for %d words in %.1fs" % (
            len(words_needed), time.time() - t_w1), flush=True)
        w1n = l2n(mat_w1)
        store_paradigmatic = {w: w1n[i] for i, w in enumerate(words_needed)}

        anchor_words_full = sorted(anchor_set)
        if grid == "reduced":
            anchor_words_full = sorted(set(anchor_words_full[:1200]) | set(words_needed))
        t0m = time.time()
        M, row_idx, matrix_diag = CAP.build_matrix(anchor_words_full)
        rep["MATRIX"] = matrix_diag
        print("[scores] M built shape=%r t=%.1fs" % (M.shape, time.time() - t0m), flush=True)

        Mppmi_vanilla = CAP.ppmi_of(M)
        vecs_t0 = TC.svd_vectors_p(Mppmi_vanilla, 50, 0.5, MASTER_SEED + 7000 + 50)
        Mppmi_t2 = TC.ppmi_tuned(M, alpha=1.0, k_shift=15, subsample_t=None)
        vecs_t2 = TC.svd_vectors_p(Mppmi_t2, 50, 0.5, TC._seed_for("T2:ks15_k50:svd"))
        if vecs_t0 is None or vecs_t2 is None:
            raise SystemExit("SVD_RANK_CEILING -- k=50 exceeded the matrix's rank ceiling "
                             "(shape=%r); cannot build T0/T2 arms." % (M.shape,))
        store_t0 = {w: vecs_t0[row_idx[w]] for w in words_needed if w in row_idx}
        store_t2 = {w: vecs_t2[row_idx[w]] for w in words_needed if w in row_idx}

        pc_key = unit_key("POSITIVE_CONTROL", CODE_VERSION, grid)
        prior_pc = load_units(out_dir_ckpt).get(pc_key)
        if prior_pc is not None:
            print("[positive_control] RESUMED FROM CHECKPOINT", flush=True)
            pos_control = prior_pc
        else:
            gate = CAP.regression_gate()
            origP, origS = gate["matchedP"], gate["matchedS"]
            t0_orig = TC.score_pairs(vecs_t0, row_idx, origP, origS, MASTER_SEED + 9300 + 50)
            t2_orig = TC.score_pairs(vecs_t2, row_idx, origP, origS, TC._seed_for("T2:ks15_k50:ev"))
            t0_delta = round(t0_orig["auc"] - 0.0519, 6)
            t2_delta = round(t2_orig["auc"] - 0.1144, 6)
            pos_control = {
                "T0_orig_population_auc": t0_orig, "T0_expected": 0.0519, "T0_delta": t0_delta,
                "T0_PASS": bool(abs(t0_delta) <= 0.0005),
                "T2_orig_population_auc": t2_orig, "T2_expected": 0.1144, "T2_delta": t2_delta,
                "T2_PASS": bool(abs(t2_delta) <= 0.0005),
            }
            record_unit(out_dir_ckpt, pc_key, pos_control)
        rep["POSITIVE_CONTROL"] = pos_control
        if grid == "full" and not (pos_control["T0_PASS"] and pos_control["T2_PASS"]):
            raise SystemExit("POSITIVE_CONTROL_FAILED -- T0/T2 reconstruction does not reproduce "
                             "the landed cells' own numbers on the ORIGINAL population: %r" %
                             pos_control)

        print("[scores] all expensive arms built, elapsed=%.1fs" % (time.time() - t0s), flush=True)

        arm_scores_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "INCUMBENT_LIVE_STORE": pair_dense(store_incumbent),
            "RAW_COUNT_FULL_ACCUM": pair_dense(store_raw_full),
            "RAW_COUNT_SINGLE_OCC": pair_dense(store_single),
            "PRESENCE_ABSENCE_BINARIZED": pair_dense(store_binarized),
            "PARADIGMATIC_PROFILE_WRITE": pair_dense(store_paradigmatic),
            "T0_VANILLA_PPMI_SVD": pair_dense(store_t0),
            "T2_SHIFTED_PPMI_K15": pair_dense(store_t2),
        }
        arm_scores = {k: {"P": v[0], "S": v[1]} for k, v in arm_scores_raw.items()}
        record_unit(out_dir_ckpt, scores_key,
                   {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in arm_scores.items()})
        rep.setdefault("POSITIVE_CONTROL", pos_control)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) -- ALL 13 arms ===================
    all_scores = dict(cheap_scores)
    all_scores.update(arm_scores)
    digests = {k: DSI._digest(np.concatenate([v["P"], v["S"]])) for k, v in all_scores.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC PER ARM (expensive arms) ====================================
    SEVEN_ARMS = H2.SEVEN_ARMS
    for i, (name, sc) in enumerate(arm_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + 100 + i)
        auc_results[name] = res
        margin_vs_max_floor = round(res["auc"] - max_floor_auc_this_population, 4)
        margin_vs_half = round(res["auc"] - 0.5, 4)
        res["margin_vs_max_floor_this_population"] = margin_vs_max_floor
        res["margin_vs_0.5"] = margin_vs_half
        print("[auc] %-30s AUC=%.4f CI=%r band=%s margin_vs_max_floor=%+.4f margin_vs_0.5=%+.4f" % (
            name, res["auc"], res["ci95"], res["band"], margin_vs_max_floor, margin_vs_half),
             flush=True)
    rep["AUC_PER_ARM"] = auc_results

    # =============================== POWER CHECK (coverage) ==========================================
    seven_ci = {a: auc_results[a]["ci95"] for a in SEVEN_ARMS}
    any_pairwise_separated = False
    for i in range(len(SEVEN_ARMS)):
        for j in range(i + 1, len(SEVEN_ARMS)):
            ai, aj = SEVEN_ARMS[i], SEVEN_ARMS[j]
            if seven_ci[ai][1] < seven_ci[aj][0] or seven_ci[aj][1] < seven_ci[ai][0]:
                any_pairwise_separated = True
    max_halfwidth = max(auc_results[a]["ci_halfwidth"] for a in SEVEN_ARMS)
    power_insufficient = not any_pairwise_separated
    rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match,
                          "max_ci_halfwidth_across_seven_arms": max_halfwidth,
                          "any_pairwise_CI_separated_among_seven_arms": any_pairwise_separated,
                          "POWER_INSUFFICIENT": power_insufficient}

    # =============================== RANK CORRELATION (the decisive comparison) ======================
    wordnet_aucs: Dict[str, Optional[float]] = {}
    rank_corr_diag: Dict = {"source_paths": {"DSI": H2.DSI_METRICS_PATH, "CAP": H2.CAP_METRICS_PATH,
                                             "TC": H2.TC_METRICS_PATH}}
    try:
        import json
        with open(H2.DSI_METRICS_PATH, encoding="utf-8") as f:
            dsi_m = json.load(f)
        dsi_auc = dsi_m["report"]["AUC_PER_ARM"]
        for a in ["INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM", "RAW_COUNT_SINGLE_OCC",
                 "PRESENCE_ABSENCE_BINARIZED", "PARADIGMATIC_PROFILE_WRITE"]:
            wordnet_aucs[a] = dsi_auc[a]["auc"]
        with open(H2.TC_METRICS_PATH, encoding="utf-8") as f:
            tc_m = json.load(f)
        wordnet_aucs["T0_VANILLA_PPMI_SVD"] = tc_m["report"]["T0_VANILLA_PPMI_SVD"]["sweep"]["50"]["auc"]
        wordnet_aucs["T2_SHIFTED_PPMI_K15"] = \
            tc_m["report"]["T2_SHIFTED_PPMI"]["RESULT_held_out_selected_eval_AUC"]["auc"]
        rank_corr_diag["wordnet_instrument_aucs"] = wordnet_aucs
        human_aucs = {a: auc_results[a]["auc"] for a in SEVEN_ARMS}
        rank_corr_diag["human_instrument_aucs"] = human_aucs
        wn_vec = np.array([wordnet_aucs[a] for a in SEVEN_ARMS])
        hu_vec = np.array([human_aucs[a] for a in SEVEN_ARMS])
        rho, _p_asymp = spearmanr(wn_vec, hu_vec)
        import itertools
        n7 = len(SEVEN_ARMS)
        perm_rhos = []
        for perm in itertools.permutations(range(n7)):
            r, _ = spearmanr(wn_vec, hu_vec[list(perm)])
            perm_rhos.append(r if not np.isnan(r) else 0.0)
        perm_rhos = np.array(perm_rhos)
        exact_p_two_sided = float(np.mean(np.abs(perm_rhos) >= abs(rho) - 1e-9))
        rng_bs = np.random.default_rng(MASTER_SEED + 6060)
        boot_rhos = []
        for _ in range(10000):
            idx = rng_bs.integers(0, n7, size=n7)
            r, _ = spearmanr(wn_vec[idx], hu_vec[idx])
            if not np.isnan(r):
                boot_rhos.append(r)
        boot_rhos = np.array(boot_rhos) if boot_rhos else np.array([np.nan])
        rank_corr_diag.update({
            "n_arms": n7, "spearman_rho": None if np.isnan(rho) else round(float(rho), 4),
            "exact_permutation_two_sided_p": round(exact_p_two_sided, 4),
            "bootstrap_of_arms_ci95": [round(float(np.nanpercentile(boot_rhos, 2.5)), 4),
                                      round(float(np.nanpercentile(boot_rhos, 97.5)), 4)],
            "DISCLOSURE": "n=7 arms is a very small sample for a rank correlation; the bootstrap CI "
                          "and exact permutation p-value are both reported so the reader can judge "
                          "resolution directly rather than trust a single point estimate.",
        })
    except Exception as e:
        rank_corr_diag["ERROR"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    rep["RANK_CORRELATION"] = rank_corr_diag
    rep["POPULATIONS_NOT_COMPARABLE"] = (
        "this instrument's matched population and the WordNet instrument's are DIFFERENT, "
        "non-overlapping-by-construction pools -- absolute AUC values are NEVER compared side by "
        "side across the two instruments; only RANK_CORRELATION (the arm ORDERING) is a valid "
        "cross-instrument statement")

    # =============================== INTERPRETATION (STOP-IF iii/iv/v/vi) ============================
    if not instrument_licensed:
        interp = "STRATIFICATION_REJECTED_AS_MATCHER"
    elif power_insufficient:
        interp = "POWER_INSUFFICIENT__n=%d__max_ci_halfwidth=%.4f" % (n_match, max_halfwidth)
    else:
        rho_val = rank_corr_diag.get("spearman_rho")
        boot_ci = rank_corr_diag.get("bootstrap_of_arms_ci95", [None, None])
        any_above_max_floor = any(
            auc_results[a]["ci95"][0] > max_floor_auc_this_population for a in SEVEN_ARMS)
        any_above_half = any(auc_results[a]["band"] == "ABOVE_0.5_SUBSTITUTABILITY" for a in SEVEN_ARMS)
        if rho_val is not None and boot_ci[0] is not None and boot_ci[0] > 0:
            interp = "STOP_IF_iv_ORDERINGS_AGREE__6_23_IS_ABOUT_OUR_STORE__rho=%.4f" % rho_val
        elif rho_val is not None and boot_ci[1] is not None and boot_ci[1] < 0:
            interp = "STOP_IF_v_ORDERINGS_DISAGREE__6_23_WAS_ABOUT_WORDNET__rho=%.4f" % rho_val
        else:
            interp = "RANK_CORRELATION_CI_INCLUDES_ZERO__INCONCLUSIVE_AT_THIS_N__rho=%r" % rho_val
        if any_above_max_floor:
            interp += "__STOP_IF_vi_ARM_CI_SEPARATED_ABOVE_MAX_FLOOR_%.4f" % max_floor_auc_this_population
        elif any_above_half:
            interp += "__ARM_ABOVE_0.5_BUT_NOT_ABOVE_MAX_FLOOR_%.4f__NOT_STOP_IF_vi" % max_floor_auc_this_population
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

    licensed = rep.get("LICENSING", {}).get("INSTRUMENT_LICENSED", False)
    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "DISSOCIATION_INSTRUMENT_HUMAN_V3_%s__%s" % ("LICENSED" if licensed else "UNLICENSED", interp)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Human-label dissociation-score instrument, FREQUENCY-STRATIFIED MATCHER "
                       "(v2 hit n=7 with a uniform caliper; this file matches within frequency "
                       "bands): does agreement with human similarity judgements rank the same 7 "
                       "arms the same way the WordNet-labelled instrument does? -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "T_HIGH": T_HIGH, "T_LOW": T_LOW,
                  "TOP_DECILE_Q": TOP_DECILE_Q, "KNOWN_ANSWER_MIN_AUC": KNOWN_ANSWER_MIN_AUC,
                  "FREQ_STRAT_N_BINS": FREQ_STRAT_N_BINS,
                  "FREQ_STRAT_CALIPER_SQ_PER_DIM": FREQ_STRAT_CALIPER_SQ_PER_DIM.tolist()},
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
