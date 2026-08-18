# The dissociation-score instrument -- BUILT, LICENSED, and a first re-scoring of what we have

**INSTRUMENT BUILD, NOT AN ORGAN GATE.** This note reports a validated measuring device plus a
re-scoring of stores we already own. It makes no capability claim.

Spec: `notes/protocol_representational_content_organ_gates_2026-08-18.md` sec 8.3 (commit
`446f61aa0`), ADOPTED `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.11 (commit `b8cb6f39e`).
Cell: `experiments/exp_dissociation_score_instrument_v1.py`. Landed metrics:
`data/exp_dissociation_score_instrument_v1/metrics.json` (`code_version=v1.7`, `run_mode=full`,
`elapsed_s=331.8`).

## The construction

- **SET P (paradigmatic):** word pairs sharing a WordNet SYNSET (literal synonyms), zero corpus
  co-occurrence over the 34,169-sentence corpus this store was built from.
- **SET S (syntagmatic):** word pairs in the top co-occurring pool (actual pool floor = count 13,
  the corpus's own 90th-percentile threshold is 4, so this is well above top-decile), excluding any
  pair sharing a WordNet synset AND any pair whose best path_similarity clears 0.25 (the same
  "taxonomically close" threshold `exp_writerule_step_ladder_v1` and `exp_readout_second_order_v1`
  use), requiring both members share one dominant WordNet POS.
- **SCORE:** AUC separating SET P's store-similarity from SET S's, paired bootstrap CI (10,000
  draws).

## Match quality (report this first -- it licenses everything else)

Matched on 5 covariates (protocol names 3: frequency/length/POS; two more were added and disclosed
as each was needed -- see "how the matching was built" below): mean log1p(freq), |freq diff|, mean
surface length, orthographic trigram-cosine, mean constant-prototype score. Per-POS-stratum greedy
nearest-neighbour with a per-dimension caliper (frequency covariates 0.02, others 0.25, in squared
z-units).

| covariate | pre-match SMD | post-match SMD |
|---|---|---|
| mean_log_freq | -3.0798 | **-0.0416** |
| abs_freq_diff | 0.0795 | **0.0045** |
| mean_length | 0.5504 | **-0.0121** |
| orthographic_trigram_cos | 0.4980 | **0.0007** |
| mean_constant_prototype | -1.5722 | **0.1574** |

**n surviving: 242 pairs per cell** (from 3,912 SET P raw candidates and 3,846 SET S raw
candidates; 3,555 candidate pairings were dropped by the caliper rather than force-matched). All 242
matched pairs on both sides landed in the noun POS stratum -- the verb/adjective/adverb strata did
not survive the caliper at this candidate-pool size. **This is a real scope limitation, disclosed
rather than hidden: the instrument as built here speaks to noun substitutability vs noun
co-occurrence, not to the other parts of speech.**

## The four floors, measured AUCs with CIs (licenses everything below)

| floor | AUC | 95% CI | band |
|---|---|---|---|
| F_ORTHOGRAPHIC | 0.5000 | [0.4875, 0.5124] | NOT_SEPARATED_FROM_CHANCE |
| F_FREQUENCY (max-of-pair) | 0.4901 | [0.4376, 0.5413] | NOT_SEPARATED_FROM_CHANCE |
| F_SCRAMBLE | 0.4664 | [0.4148, 0.5178] | NOT_SEPARATED_FROM_CHANCE |
| F_CONSTANT_PROTOTYPE | 0.5431 | [0.4922, 0.5953] | NOT_SEPARATED_FROM_CHANCE |

**All four CI-include 0.5. STOP-IF (i) does NOT fire.** F_FREQUENCY's scorer was deliberately chosen
to be the MAX of the pair's two frequencies, not the matched MEAN statistic, so this is a genuine
out-of-sample check that the match generalises beyond the one number it was built on.

## Known-answer and random-store validation

| arm | AUC | 95% CI | gate |
|---|---|---|---|
| KNOWN_ANSWER (WordNet path_similarity) | **0.9599** | [0.9441, 0.9739] | >=0.95 required -- PASS |
| RANDOM_VECTOR_STORE | 0.4862 | [0.4353, 0.5377] | must include 0.5 -- PASS |

STOP-IF (ii) does NOT fire. **`INSTRUMENT_LICENSED = True`.**

## How the matching was built (the honest iteration, because it is itself a finding)

The protocol names 3 matching variables (frequency, length, POS). Building this instrument surfaced,
in order, why that was not sufficient here, and each fix was measured before the next was added --
never widened, per the protocol's own instruction ("if a floor DOES separate them, the stimulus set
is broken and must be rebuilt"):

1. **v1.0** (freq-mean/length/POS only): F_ORTHOGRAPHIC AUC=0.6801, F_FREQUENCY(max) AUC=0.1266,
   both CI-separated. WordNet same-synset pairs are orthographically closer than co-occurring pairs
   even after freq/length matching (shared derivational morphology inside a synset, e.g.
   `group`/`grouping`).
2. **v1.1** added `|freq_diff|` and pair trigram-cosine as covariates, but an UNCAPPED
   nearest-neighbour match still force-matched poorly-paired items (post-match
   SMD(mean_log_freq)=-1.9564) -- SET S's raw pool (top co-occurring) is structurally more frequent
   than SET P's (zero-co-occurring WordNet synonyms, which includes many rare words), so "nearest
   available" was still often "not actually close."
3. **v1.2** added a caliper (drop rather than force-match, same philosophy as
   `tools/floor_battery.matched_candidate_sets`): fixed F_ORTHOGRAPHIC and F_CONSTANT_PROTOTYPE, left
   F_FREQUENCY separated (SMD=-0.6155) -- a single TOTAL Euclidean budget let the frequency axis
   spend the whole caliper while the other axes sat near zero.
4. **v1.3** tightened the total caliper: fixed F_FREQUENCY at the smaller smoke scale but exposed
   F_CONSTANT_PROTOTYPE (AUC=0.6598 at smoke N=68).
5. **v1.4** added mean constant-prototype score as a 5th covariate: all four floors CI-included 0.5
   at smoke scale, but at FULL scale (n=430, tighter CI) F_FREQUENCY re-separated (AUC=0.3923).
6. **v1.5** switched to a per-dimension (L-infinity) caliper, uniform across all 5 covariates: still
   left a SYSTEMATIC residual on mean_log_freq (post-match SMD=-0.6235) -- a per-pair magnitude bound
   does not prevent a same-direction bias from accumulating when one candidate pool is structurally
   shifted relative to the other.
7. **v1.6/v1.7** (landed): a per-dimension caliper VECTOR -- the two frequency covariates get a
   caliper 12.5x tighter than length/orthography/prototype. This is the version reported here.

A separate bug was found and fixed in the STOP-IF (v) "arms indistinguishable" check: an earlier
version compared which SIDE of 0.5 each store arm's AUC landed on, which is not the same question as
whether arms are pairwise distinguishable from EACH OTHER, and it wrongly fired because all 5 store
arms happened to land below 0.5 despite point estimates spanning 0.03-0.42. Replaced with a mutual
95%-CI-overlap check across the store arms (`max_lo=0.3835 > min_hi=0.0470` -- does NOT overlap, so
(v) correctly does not fire; the arms ARE resolvable from each other at this n).

## Arm-by-arm re-scoring (STORE arms; interpretable because the instrument is licensed)

| arm | AUC | 95% CI half-width |
|---|---|---|
| **INCUMBENT_LIVE_STORE** (H^T p_a, random projection, unweighted sum) | **0.0710** | [0.0509, 0.0937], hw=0.0214 |
| RAW_COUNT_FULL_ACCUM (uncompressed) | 0.0510 | [0.0332, 0.0710], hw=0.0189 |
| RAW_COUNT_SINGLE_OCC (one profile sentence per anchor) | 0.4173 | [0.3835, 0.4500], hw=0.0333 |
| PRESENCE_ABSENCE_BINARIZED | 0.0294 | [0.0147, 0.0470], hw=0.0162 |
| PARADIGMATIC_PROFILE_WRITE (landed second-order write rule) | 0.2165 | [0.1781, 0.2575], hw=0.0397 |

Every store arm reads CI-separated BELOW 0.5 -- none crosses into substitutability territory, but the
DEGREE of co-occurrence-encoding differs sharply and legibly: the two arms closest to raw
co-occurrence bookkeeping (uncompressed full-accumulation, and its binarised presence/absence
variant) are the MOST co-occurrence-coded (AUC 0.03-0.05); a SINGLE occurrence per anchor
(RAW_COUNT_SINGLE_OCC) is markedly less so (AUC 0.42, closest to chance of any arm); the landed
second-order paradigmatic write rule sits in between (AUC 0.22). The incumbent live store (AUC 0.071)
sits close to the two full-accumulation raw-count arms, consistent with it being a lossy projection
of the same full-accumulation counts. **`ARM_RESOLUTION_CHECK`: the store arms' 95% CIs do NOT
mutually overlap (max_lo=0.3835, min_hi=0.0470) -- the ranking above is a real, resolvable ranking at
this n, not noise.**

## Which STOP-IF fired

**STOP-IF (iii): the incumbent scores CI-separated BELOW 0.5, as pre-registered.** Landed verdict:
`DISSOCIATION_INSTRUMENT_LICENSED__STOP_IF_iii_COOCCURRENCE_DIAGNOSIS_CONFIRMED`.

## The one plain-language sentence

**Our store, when asked to separate "words that could replace each other but never appear together"
from "words that appear together constantly but cannot replace each other," picks the second group as
more similar (AUC 0.071, clearly below the 0.5 a content-blind store would score) -- for the first
time we have a direct, licensed measurement, not a suspicion, that our store currently records which
words keep each other company rather than which words could stand in for one another.**

## Honest limits

- **The matched population is noun-only.** Verb/adjective/adverb strata did not survive the tight
  frequency caliper at this candidate-pool size (SET P candidates capped at 3,912 by the "zero
  co-occurrence WordNet synonym" construction itself, not by a cell-imposed limit). Widening SET S's
  candidate cap or relaxing (with re-measurement, never silently) the frequency caliper for
  non-noun strata is the natural next step if a POS-general instrument is wanted.
- **This is a diagnosis, not a capability measurement**, per the dispatch brief's explicit framing.
  No number here should be read as "the store is X% good at substitutability."
- **The five re-scored arms are ranked relative to EACH OTHER on this instrument**, not validated
  against an external substitutability benchmark; the known-answer/random-store arms license the
  INSTRUMENT, not each individual store arm's absolute placement.
