# exp_dissociation_score_instrument_human_v3 -- frequency-stratified matcher, FULL landed

**Filed 2026-08-18. exp_dev (cell author).** Cell: `experiments/exp_dissociation_score_instrument_human_v3.py`.
Metrics: `data/exp_dissociation_score_instrument_human_v3/metrics.json` (run_mode=full, elapsed_s=553.4,
size=15674 bytes). Smoke: `data/exp_dissociation_score_instrument_human_v3_reduced/metrics.json`
(run_mode=reduced, elapsed_s=25.0).

## What changed vs v2

v2 (`exp_dissociation_score_instrument_human_v2.py`, uniform per-dimension caliper reused verbatim
from v1) collapsed to n_match=7/cell -- POWER_INSUFFICIENT, no arm scored. The measured cause: SET_P_
HUMAN (human-rated similar, zero-cooccurring) is structurally rarer than SET_S_HUMAN (highly
co-occurring); pre-match SMD(mean_log_freq)=-1.8396; the uniform caliper (0.02 sq on both frequency
covariates, z-scored against the POOLED population's inflated variance) caliper-dropped 429/436
candidates.

v3 changes ONLY the matcher: `frequency_stratified_match_cells()` bins each POS stratum's pooled
P+S `mean_log_freq` into `FREQ_STRAT_N_BINS=3` quantile bins (equal candidate mass), then runs
`DSI.match_cells` UNCHANGED inside each (POS, bin) cell with a looser residual caliper
`[8.0, 1.0, 1.5, 1.5, 1.5]` (mean_log_freq's own per-pair caliper loosened 400x since bin membership
now does that job; abs_freq_diff loosened 50x; length/trigram/prototype loosened 6x). Population
construction (SET_P_HUMAN/SET_S_HUMAN raw candidate build, thresholds) and the license-gate/arm/
rank-correlation machinery are reused verbatim from v2 (imported as READ-ONLY modules, not
copy-pasted). The caliper values were selected by a pre-authoring grid search against the REAL
four-floor AUC bootstrap (not a proxy SMD threshold; disposable scratch scripts, not committed) --
the widest point in that grid at which all four floors still read NOT_SEPARATED_FROM_CHANCE.

## Achieved n and balance

n_matched_P = n_matched_S = **65** per cell (per-POS: a=2, n=9, v=54; candidates a=19P/3S, n=47P/27S,
v=370P/92S; 200 candidates dropped by the residual caliper across all bins).

Post-match SMD, every covariate, before -> after:

| covariate | pre-match SMD | post-match SMD | WordNet instrument's own post-match SMD (for scale) |
|---|---|---|---|
| mean_log_freq | -1.8396 | **-0.4382** | -0.0416 |
| abs_freq_diff | 0.2650 | **0.2466** | 0.0045 |
| mean_length | 1.0581 | **0.3988** | -0.0121 |
| orthographic_trigram_cos | -0.0595 | **-0.0710** | 0.0007 |
| mean_constant_prototype | -1.2561 | **-0.1757** | 0.1574 |

**Disclosed plainly, per the dispatch brief's explicit instruction: this is NOT comparable balance
to the WordNet instrument.** Every covariate's post-match SMD is worse here, mean_log_freq and
mean_length by roughly an order of magnitude. Binning improved mean_log_freq from -1.84 to -0.44 (a
real, large reduction) and mean_length/prototype similarly, but none reach the WordNet instrument's
near-zero residuals. The reason the license gate still passes despite this (see below) is that AUC
bootstrap CIs at n=65 are wide enough (half-width ~0.05-0.09) that these residual SMDs did not
translate into a floor separating from 0.5 -- an empirical outcome, not a claim that the imbalance is
small.

## The four floors (N_BOOT=10000, full scale)

| floor | AUC | 95% CI | band |
|---|---|---|---|
| F_ORTHOGRAPHIC | 0.4920 | [0.4462, 0.5356] | NOT_SEPARATED_FROM_CHANCE |
| F_FREQUENCY | 0.4151 | [0.3167, 0.5131] | NOT_SEPARATED_FROM_CHANCE |
| F_SCRAMBLE | 0.5943 | [0.4961, 0.6899] | NOT_SEPARATED_FROM_CHANCE |
| F_CONSTANT_PROTOTYPE | 0.4125 | [0.3160, 0.5122] | NOT_SEPARATED_FROM_CHANCE |

All four CIs include 0.5. `max(four floors)` = **0.5943** (F_SCRAMBLE) -- notably higher than the
WordNet instrument's own recomputed max-floor (0.5431, F_CONSTANT_PROTOTYPE there); every arm margin
below is reported against BOTH this population's own max-floor and against 0.5, separately, per the
dispatch brief.

Known-answer: the **published human similarity rating itself** (SimLex-999 + SimVerb-3500), NOT
WordNet path similarity -- AUC=1.0000 [1.0, 1.0], tautological by construction (the label IS the
threshold), reported only as a plumbing sanity check per the brief's explicit instruction to escape
the WordNet-known-answer dependency. Random-vector-store control: AUC=0.4578 [0.3579, 0.5574], at
chance.

Positive control (T0/T2 reconstruction re-scored on the ORIGINAL WordNet-licensed population, same
seeds as the landed cells): T0 measured=0.0519 expected=0.0519 delta=0.0 PASS; T2 measured=0.1144
expected=0.1144 delta=0.0 PASS. Confirms the reused PPMI+SVD arms are wired correctly before trusting
them on this population.

**STOP-IF outcome: n=65 >= 60 AND all four floors at chance -> INSTRUMENT_LICENSED = True.**

## Seven-arm scores and rank correlation vs the WordNet instrument

| arm | human-instrument AUC | 95% CI | band | margin vs max-floor (0.5943) | margin vs 0.5 | WordNet-instrument AUC (NOT comparable in absolute terms) |
|---|---|---|---|---|---|---|
| INCUMBENT_LIVE_STORE | 0.2265 | [0.1498, 0.3110] | BELOW_0.5 | -0.3678 | -0.2735 | 0.0710 |
| RAW_COUNT_FULL_ACCUM | 0.1796 | [0.1108, 0.2542] | BELOW_0.5 | -0.4147 | -0.3204 | 0.0510 |
| RAW_COUNT_SINGLE_OCC | 0.4644 | [0.4012, 0.5253] | NOT_SEPARATED | -0.1299 | -0.0356 | 0.4173 |
| PRESENCE_ABSENCE_BINARIZED | 0.1673 | [0.1027, 0.2407] | BELOW_0.5 | -0.4270 | -0.3327 | 0.0294 |
| PARADIGMATIC_PROFILE_WRITE | 0.2788 | [0.1960, 0.3697] | BELOW_0.5 | -0.3155 | -0.2212 | 0.2165 |
| T0_VANILLA_PPMI_SVD | 0.2928 | [0.2045, 0.3865] | BELOW_0.5 | -0.3015 | -0.2072 | 0.0519 |
| T2_SHIFTED_PPMI_K15 | 0.2649 | [0.1808, 0.3555] | BELOW_0.5 | -0.3294 | -0.2351 | 0.1144 |

No arm on the human instrument reads above 0.5, let alone above max-floor -- STOP-IF (vi) does not
fire. Absolute AUCs are NOT compared across instruments (different populations, per pre-reg); only
the ORDERING is.

**Rank correlation (7 arms): Spearman rho = 0.7857.** Exact permutation two-sided p = 0.048.
Bootstrap-of-arms 95% CI = **[-0.0439, 1.0]** -- includes zero. Per the pre-reg's STOP-IF ladder this
lands in the middle branch: **RANK_CORRELATION_CI_INCLUDES_ZERO -- INCONCLUSIVE AT THIS N**, not
STOP-IF (iv) (orderings agree, survives) or (v) (orderings disagree, redirect). The point estimate
(0.7857, and the same RAW_COUNT_SINGLE_OCC > PARADIGMATIC > (T2/INCUMBENT/T0 clustered) > BINARIZED
qualitative shape as the WordNet instrument) is suggestive of agreement, but n=7 arms is too small a
sample for the bootstrap CI to exclude zero -- the exact permutation p=0.048 is right at the
conventional 0.05 line and should not be over-read given how few permutations of 7 items exist.

## Verdict

`DISSOCIATION_INSTRUMENT_HUMAN_V3_LICENSED__RANK_CORRELATION_CI_INCLUDES_ZERO__INCONCLUSIVE_AT_THIS_N__rho=0.7857`

## One-sentence answer to "is Organ A's closure about our store or about WordNet"

**Inconclusive, not "about our store"**: the instrument is licensed and the arm ordering leans the
same direction as the WordNet instrument's (rho=0.79), but the bootstrap CI over only 7 arms includes
zero, so this run cannot certify that plan sec 6.23's conclusion survives independent of WordNet --
it also cannot certify that it was substantially about WordNet; the honest read is that this
particular test lacks the power (7 arms) to decide, despite the population-level licensing gate
(n=65, floors at chance) succeeding.

## Prior-work check

`ls experiments/ | grep dissociation_score_instrument` at authoring time returns exactly `_v1.py`,
`_human_v1.py`, `_human_v2.py` plus this new `_human_v3.py` -- no undisclosed sibling. Per the
dispatch brief this check was already done at Director level (name-level enumeration); this is the
cheap local backstop, not a `tools/substrate_query.sh` call (documented elsewhere as returning zero
bytes under concurrent load) or an `os.walk` over `data/` (157 GB, documented as stalling lanes).
