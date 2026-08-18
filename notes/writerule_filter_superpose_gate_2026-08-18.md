# ORGAN A -- FILTER and SUPERPOSE gated (the last two ungated write-rule steps)

`experiments/exp_writerule_filter_superpose_gate_v1.py`, FULL run, 53s,
`data/exp_writerule_filter_superpose_gate_v1/metrics.json`. Verdict:
`FILTER_NOT_LOAD_BEARING__SUPERPOSE_EXONERATED`.

Reused verbatim, not rebuilt: `exp_dissociation_score_instrument_v1`'s licensed matched-pair
population (242 pairs/cell, loaded from its own on-disk POPULATION checkpoint) and its AUC scorer
(`dense_scores_from_dict_store`, `auc_bootstrap`). Regression gates: `F0_INCUMBENT` reproduces DISS's
own `RAW_COUNT_SINGLE_OCC` AUC bit-for-bit (0.4173); `S0_INCUMBENT` reproduces DISS's
`INCUMBENT_LIVE_STORE` AUC bit-for-bit (0.0710). Population regression: 242/242 matched pairs, exact.
K1 (WordNet known-answer) 0.9599 [0.944,0.9742] ABOVE; N0 (random-vector store) 0.4862 [0.435,0.5374]
NOT_SEPARATED -- both reused verbatim from DISS's own checkpoint and re-bootstrapped here, both PASS.
Floors: this cell reuses DISS's population unchanged, so DISS's own floor licensing (all four floors
NOT_SEPARATED from 0.5 at full scale) remains valid without re-derivation -- floors are a property of
the pair set, not of the arm.

## Enumeration correction (STEP 1)

FILTER matches the sketch exactly: `content_words()` (grounding_acquisition_loop.py:106-114).

"SUPERPOSE" does NOT exist as a separate cross-anchor write operation in live code. This is the
result, not a null finding. `ConceptSpace.observe` (`self._sums[lemma] += ctx_vec`,
reading_grounding_loop.py:478-481) reads/writes only the one dict entry named `lemma`; `anchor_matrix()`
is a plain `np.stack` of independently-computed rows. Each row is itself fully reconstructible from
that ONE anchor's own raw counts and a fixed, corpus-independent per-word symbol dictionary
(`INFO.reconstruct_bipolar`, already proven bit-exact against the live cache by
`exp_cue_information_audit_v1.verify_recoverability`). Consequence, stated before running anything:
because building anchor A's vector never reads anchor B's data, `S1_PER_ANCHOR_ISOLATED` must be
mathematically identical to `S0_INCUMBENT` on any scorer that looks at one named pair at a time --
which is exactly what the dissociation AUC computes. Confirmed empirically below, not just argued.

## Gate A -- FILTER

| arm | AUC | CI95 | halfwidth | band |
|---|---|---|---|---|
| F0_INCUMBENT | 0.4173 | [0.3837,0.4506] | 0.0335 | BELOW_0.5 |
| F1_NO_FILTER | 0.4558 | [0.405,0.5075] | 0.0513 | NOT_SEPARATED |
| F2_CONTENT_ONLY_STRICT | 0.4323 | [0.4002,0.4634] | 0.0316 | BELOW_0.5 |
| F3_SYNTACTIC_NEIGHBOURS_ONLY | 0.4876 | [0.4752,0.4979] | 0.0114 | BELOW_0.5 |
| F4_WINDOW_1 | 0.4959 | [0.4897,0.5] | 0.0052 | NOT_SEPARATED |
| F4_WINDOW_2 | 0.4731 | [0.4587,0.4855] | 0.0134 | BELOW_0.5 |
| F4_WINDOW_5 | 0.4561 | [0.4355,0.4751] | 0.0198 | BELOW_0.5 |
| N1_RANDOM_FILTER | 0.5041 | [0.4546,0.554] | 0.0497 | NOT_SEPARATED |

Null p95 at n=242/242 (analytic, matching DISS's own convention): ~0.045 half-width order; every
half-width above is consistent with that scale, none of these are underpowered-null artifacts at the
n reported.

**Stop-if (i) did NOT fire**: no filter arm clears both F0 AND N1 CI-separated above.
**Stop-if (ii) FIRED**: `F1_NO_FILTER` (every token kept, including function words) does NOT read
worse than `F0_INCUMBENT` -- its point estimate (0.4558) is numerically HIGHER than F0's (0.4173),
CIs overlapping. The predicted "must lose" arm did not lose. Filtering out stopwords, on this
instrument, is not doing the job the incumbent's design assumes.

**The headline finding is `N1_RANDOM_FILTER` itself.** `N1` (drop the same NUMBER of tokens F0 drops,
but at random) reads 0.5041 [0.4546,0.554] -- essentially at chance, and its CI lower bound (0.4546)
sits narrowly above `F0`'s CI upper bound (0.4506): a real but thin CI-separation, `N1` ABOVE `F0`.
**An equally-sized random subsample beats the incumbent's specific stopword-removal selection rule,
CI-separated.** Per the brief's own framing ("if a filter arm does not beat this control, its gain is
attrition, not selection"): here it is sharper than that -- the incumbent's selection is measurably
WORSE than pure attrition at this instrument. Filtering helps mainly (here, entirely) by reducing
token COUNT, not by choosing the RIGHT tokens.

One directionally real secondary signal: `F3_SYNTACTIC_NEIGHBOURS_ONLY` (0.4876) is CI-separated ABOVE
`F0` (lower bound 0.4752 > F0's upper bound 0.4506) -- restricting to 1-hop dependency neighbours does
measurably reduce co-occurrence bias relative to the incumbent. It does NOT clear N1's CI, so per the
pre-registered bar it does not count as "load-bearing", but it is the only real selection rule (as
opposed to attrition) that moved the needle in the predicted direction at all, and it is real construction
(the UD parser already on disk, 614/617 targets found, 477 sentences actually parsed, F4-whole-sentence
internally regression-checked to reproduce F0 exactly).

Secondary measure (restricted-field hit@1 + composition, n_pool ~600-617, NOT the historical
~5,491-anchor population): hit@1 is **0.0 for every arm, both gates** -- the true paradigmatic partner
is never the #1 nearest neighbour even in this much smaller field. No-close-WordNet-relation rate
among winners sits 0.92-0.94 across arms, materially flat. Both corroborate the primary AUC direction
(co-occurrence-biased throughout) without adding a positive signal of their own.

**Plain reading: FILTER is not guilty in the way the brief's sketch predicted.** It is not exonerated
either -- N1 beating F0 is a real, if narrow, negative finding about the CURRENT filter's specific
selection rule, not a clean pass. The step is measurably doing LESS than mere attrition would.

## Gate B -- SUPERPOSE (as corrected)

| arm | AUC | CI95 | halfwidth | band |
|---|---|---|---|---|
| S0_INCUMBENT | 0.0710 | [0.0507,0.0934] | 0.0214 | BELOW_0.5 |
| S1_PER_ANCHOR_ISOLATED | 0.0710 | [0.0508,0.0934] | 0.0213 | BELOW_0.5 |
| S2_DISJOINT_SUBSPACES | 0.5000 | [0.5,0.5] | 0.0 | NOT_SEPARATED (tautology) |
| N2_SHUFFLED_ASSIGNMENT | 0.4632 | [0.4125,0.5146] | 0.0511 | NOT_SEPARATED |

**S1 == S0, and it is PROVEN, not just measured**: rebuilding all 617 matched-pair words' vectors
using ONLY each word's own Pstore counts (no reference to the other 5,489 anchors, no reference to a
"store" object at all) gives `max_abs_error_vs_S0 = 1.76e-08` across all 617 words -- floating-point
noise, not a real difference. AUC values match to 4 decimal places. **Stop-if (iii) FIRED: SUPERPOSE
IS EXONERATED.** The interference the ACCUMULATE gate measured (mean pairwise anchor cosine
0.0127->0.272, `exp_organ_f_accumulate_interference_diagnosis_v1`, `b6cad69ca`) is real but is not a
storage/superposition effect -- it is independently-computed records resembling each other more as
each one individually accumulates more shared high-frequency context, which is squarely inside
ACCUMULATE (already gated).

**S2_DISJOINT_SUBSPACES is structurally UNMEASURABLE on a pairwise scorer, and this is reported
honestly rather than forced.** Any two anchors given non-overlapping coordinate blocks have cosine
EXACTLY 0 by construction, for every possible pair, both SET P and SET S -- AUC is the tautological
0.5 with a zero-width CI. Confirmed on the real 617-word population, not just a toy fixture. Capacity
arithmetic (`S2_capacity`): at the incumbent's own D=256 budget and n_pop=617, dims-per-anchor rounds
to **0** -- disjoint allocation is infeasible at parity dimensionality. A non-degenerate version at 8
dims/anchor (our invention, declared, not derived) needs D=4,936, a **19.3x** capacity multiplier over
the incumbent. Reported as a diagnostic capacity cost, per the brief, not proposed as a fix -- and
genuine retrieval evaluation of a disjoint store would additionally require redesigning cue
construction (a query needs SOME shared coordinate system to find the right block), which is out of
this gate's scope and is stated rather than glossed over.

**N2_SHUFFLED_ASSIGNMENT destroys the effect**: 0.4632 [0.4125,0.5146], NOT_SEPARATED from chance,
CI-separated below S0's own band (S0 stays BELOW_0.5 CI-separated; N2 does not). Confirms the
instrument responds to genuine anchor-content identity, not to gross structure.

**Plain reading: SUPERPOSE, as a write-time operation, does not exist and is fully exonerated.**

## Stop-ifs fired, summary

- Gate A (i) no; (ii) YES (F1 not worse than F0); Gate A resolution: NOT all-tied (F3 vs F0 separates).
- Gate B (iii) YES (S1==S0, proven); (iv) no; S2 tautological by construction, reported as such.
- (v) both-gates-blanket-exoneration did NOT fire (Gate A shows real, if modest and non-load-bearing,
  structure: N1>F0 and F3>F0). (vi) K1 passed -- instrument stays licensed, findings publishable.

## Net for the organ

CODE exonerated twice, ACCUMULATE gated as the interference source, SUPERPOSE now exonerated (this
cell), FILTER is real but working WORSE than pure attrition at its one job (this cell). The organ's
defect is not "distributed across all four steps" in the way earlier framing suggested: ACCUMULATE
remains the only step gated as a positive interference source; FILTER is a real but negative-value
step (its selection rule underperforms a size-matched random draw); CODE and SUPERPOSE are both
structurally clean. The build target the ladder points to is still ACCUMULATE-WITHOUT-COLLAPSING,
unchanged by this cell -- but this cell adds a second, smaller target: the incumbent's stopword filter
itself is worth revisiting, since a matched-size random subsample beats it, CI-separated, on the one
instrument this programme trusts.
