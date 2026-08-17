# SELECTION AXIS TEST -- does varying WHICH WORDS get summed (not just WHAT gets summed) close the gap?

Single-cell note. Cell: `experiments/exp_readout_writerule_selection_axis_v1.py`. Full run landed,
64.1s. `data/exp_readout_writerule_selection_axis_v1/metrics.json`. Read alongside
`notes/readout_ceiling_findings_2026-08-17.md` sections 10-11 (the two prior write-rule cells this
one directly follows).

## 0. THE DISPATCH'S CLAIM, AND WHETHER I AGREE

The Director's dispatch argued that the landed `exp_readout_writerule_paradigmatic_v1` cell
(P0/W1_PARADIGMATIC) changed WHAT GETS SUMMED (a neighbour's context profile instead of its identity
draw) but never changed WHICH WORDS GET SUMMED -- selection remained syntagmatic (co-occurrence
based), so the write rule tested so far was a weak version of the paradigmatic idea.

**I AGREE, confirmed by re-reading the code, not by assertion.**
`exp_readout_writerule_paradigmatic_v1.occurrence_vector` (verbatim):

```python
for w in words:                 # words = content_words(sents[sidx]), sidx from buckets[L][:nprof]
    ...
    prof = mat0n[pos[lm]]        # PAYLOAD changed: profile row instead of identity draw
    acc += prof
```

`words` is always `content_words` of a sentence drawn from `buckets[L]` -- sentences in which L
itself appears. A word can only be summed into L's code if it CO-OCCURS with L in one of L's own
profile sentences. The payload changed; the candidate set that gets summed did not. This is a real,
previously-unstated gap in the prior cell, and it is worth testing directly rather than left as a
suspicion -- which is what this cell does.

## 1. THE TEST

Held the payload fixed at EXACTLY P0's own payload (a contributor's own first-order profile row,
`mat0n[contributor]`, L2-unit) and varied ONLY selection:

- **P0_SYNTAGMATIC_SELECTION** -- the landed rule, reused verbatim via
  `exp_readout_writerule_paradigmatic_v1.build_arm(mode="PROFILE")`. REGRESSION GATE against the
  landed 0.02979, tol 5e-4, SystemExit on failure at full grid.
- **P1_PARADIGMATIC_SELECTION** -- a word's code sums the profile rows of its top-K SECOND-ORDER
  NEIGHBOURS (highest cos(mat0n[L], mat0n[M])), with NO REGARD to whether L and M ever co-occur. K
  swept over (10, 30, 100).
- **P2_ZERO_COOCCURRENCE_ONLY** -- as P1, but the candidate pool additionally excludes every anchor
  that co-occurs with L ANYWHERE in the full 34,169-sentence corpus (not just L's capped profile-
  sentence bucket).
- **P3_HYBRID** -- `beta*unit(P0 row) + (1-beta)*unit(P1 row)` at the PRE-REGISTERED K=30 (fixed
  before any number was read), beta swept over (0.25, 0.5, 0.75).
- **N1_NULL / F_FREQ_MATCHED_SELECTION** -- P1's own selected index set, per row, with contributor
  IDENTITY destroyed by a global / frequency-decile-restricted derangement respectively (reusing
  `exp_readout_writerule_paradigmatic_v1.deranged_permutation` verbatim -- the identical construction
  Arm 6 used for its own N1/F_FREQ_MATCHED, applied here at the selection level).
- **K1_KNOWN_ANSWER** -- exact-key self-addressing, gated >=0.95 for every arm before any treatment
  number is computed.

The PARTIAL CUE is IDENTICAL across every arm (P0's own held-out-sentence-context-token profile
cue, reused verbatim) -- a deliberate design choice: the cue is an observational fact (what a reader
sees near the target in one new sentence), so holding it fixed isolates the STORE'S selection rule as
the only thing differing between arms.

## 2. GATES

| gate | value | verdict |
|---|---|---|
| W1 REGRESSION (P0 reproduces the landed 0.02979) | 0.02979 vs 0.02979, tol 5e-4 | PASS |
| K1_KNOWN_ANSWER, all 16 arms | 0.9995-1.0000 (gate 0.95) | PASS |
| ARMS_MUST_DIFFER (16 SHA digests) | 16 distinct | PASS |
| NULL_PERMUTED, all 16 arms | 0.0075-0.0221 (near chance) | PASS |

## 3. ARM-BY-ARM MARGINS, n=3994, N_BOOT=10000, CI half-width and analytic null half-width beside each

Binding floor for every arm here is F_ORTHOGRAPHIC = 0.08731 (all four floors recomputed on this
population; F_CONSTANT_PROTOTYPE and F_SCRAMBLE are lower per-arm and never binding).

| arm | value | margin vs floor (0.08731) | margin vs P0 |
|---|---|---|---|
| P0_SYNTAGMATIC_SELECTION | 0.02979 | -0.0575 [-0.0673,-0.0478] hw=0.00975, BELOW | -- |
| P1_k10 | 0.03055 | -0.0568 hw=0.0099, BELOW | +0.0008 [-0.0063,+0.0078] hw=0.00705, **NOT_SEPARATED** |
| P1_k30 | 0.02829 | -0.0590 hw=0.0097, BELOW | -0.0015 [-0.0078,+0.0048] hw=0.0063, **NOT_SEPARATED** |
| P1_k100 | 0.03230 | -0.0550 hw=0.0098, BELOW | +0.0026 [-0.0035,+0.0085] hw=0.006, **NOT_SEPARATED** |
| P2_k10 | 0.02153 | -0.0657 hw=0.00955, BELOW | -0.0082 [-0.0148,-0.0015] hw=0.00665, **BELOW** |
| P2_k30 | 0.02479 | -0.0625 hw=0.00965, BELOW | -0.0050 [-0.0113,+0.0013] hw=0.0063, NOT_SEPARATED |
| P2_k100 | 0.03055 | -0.0567 hw=0.0098, BELOW | +0.0008 [-0.0050,+0.0068] hw=0.0059, NOT_SEPARATED |
| N1_k10 | 0.01202 | -0.0753 hw=0.00905, BELOW | -0.0177 [-0.0240,-0.0115] hw=0.00625, **BELOW** |
| N1_k30 | 0.00951 | -0.0778 hw=0.00905, BELOW | -0.0203 [-0.0263,-0.0143] hw=0.006, **BELOW** |
| N1_k100 | 0.00776 | -0.0795 hw=0.00895, BELOW | -0.0220 [-0.0280,-0.0163] hw=0.00585, **BELOW** |
| F_FREQ_MATCHED_k10 | 0.01627 | -0.0710 hw=0.00925, BELOW | -0.0135 [-0.0200,-0.0070] hw=0.0065, **BELOW** |
| F_FREQ_MATCHED_k30 | 0.02028 | -0.0670 hw=0.0096, BELOW | -0.0095 [-0.0163,-0.0028] hw=0.00675, **BELOW** |
| F_FREQ_MATCHED_k100 | 0.01127 | -0.0761 hw=0.0091, BELOW | -0.0185 [-0.0248,-0.0123] hw=0.00625, **BELOW** |
| P3_HYBRID_beta0.25 | 0.03030 | -0.0570 hw=0.0098, BELOW | +0.0005 [-0.0055,+0.0065] hw=0.006, NOT_SEPARATED |
| P3_HYBRID_beta0.5 | 0.02879 | -0.0585 hw=0.00975, BELOW | -0.0010 [-0.0065,+0.0043] hw=0.0054, NOT_SEPARATED |
| P3_HYBRID_beta0.75 | 0.03280 | -0.0545 hw=0.00995, BELOW | +0.0030 [-0.0013,+0.0073] hw=0.0043, NOT_SEPARATED |

Analytic null half-widths at n=3994 are 0.0053-0.0088, close to the CI half-widths above -- these are
real, well-powered comparisons, not underpowered noise.

## 4. WHICH STOP-IF FIRED

**(iii), cleanly, at every swept k.** P1 TIES P0 (NOT_SEPARATED both directions) at k=10, k=30 and
k=100 -- none of the three clears P0 CI-separated, none is CI-separated below it either. (i) did not
fire (P1 never clears the floor at any k). (ii) did not fire (there is no CI-separated beat to have a
gap). (iv) did not fire (there is no beat for a frequency-matched control to explain away). (v)
partially informative: P2 does NOT collapse to the scramble floor (it stays close to P0's own level,
ties it at k30/k100) but IS CI-separated BELOW P0 at k=10. (vi) did not fire -- K1 held on all 16
arms.

**Combined with sections 10-11: both PAYLOAD (Arm 6) and SELECTION (this cell) have now been tested
on this write rule, independently, and neither closes the gap to the floor.** Selection is not the
axis either. This is the honest fourth reading the dispatch itself anticipated as branch (iii) and it
is what happened.

## 5. THE TWO MECHANISM CHECKS -- THE SCIENTIFIC CONTENT, NOT A BARE MARGIN

### MECH_A -- co-occurrence of P1's new wins (items where P1 hits and P0 misses)

| arm | n new wins | mean Jaccard | median Jaccard | fraction ever co-occurring |
|---|---|---|---|---|
| P1_k10 | 104 | 0.01704 | 0.00435 | 0.6058 |
| P1_k30 | 79 | 0.02107 | 0.00833 | 0.6835 |
| P1_k100 | 79 | 0.03134 | 0.02174 | 0.8354 |
| **P0 baseline (general population, top-1 vs query)** | 1500 probed | **0.04622** | **0.02469** | **0.8373** |

**The prediction was that P1's new wins would concentrate on ZERO-co-occurrence pairs -- the exact
population a co-occurrence-selecting write rule cannot reach. That is NOT what is measured.** P1's
new wins have LOWER mean/median co-occurrence than P0's general-population winners (a modest
direction consistent with the story) but the fraction that EVER co-occur (61-84%, rising with k) is
close to P0's own baseline (84%), not concentrated at zero. Most of P1's "new" wins are NOT
zero-co-occurrence items the co-occurrence-selecting rule structurally could not have reached; they
look similar in co-occurrence profile to P0's own winners. This directly undercuts the mechanism
story: if P1 were winning by reaching genuinely paradigmatic, non-co-occurring answers, this
distribution should have concentrated near zero. It did not.

### MECH_B -- WordNet-relation rate of the top-1 winner, per arm (n_probe=800, capped for cost)

Reference: the landed W0 (pre-Arm-6 incumbent) measured 79.3% "no close WordNet relation" at full
scale (n=3994) in ARM 5/C1. On THIS cell's own population (n_probe=800 per arm, freshly measured,
never imported):

| arm | fraction no close WordNet relation |
|---|---|
| P0_SYNTAGMATIC_SELECTION | 0.9225 |
| P1_k10 / k30 / k100 | 0.9325 / 0.9200 / 0.9200 |
| P2_k10 / k30 / k100 | 0.9325 / 0.9275 / 0.9287 |
| P3_HYBRID_beta0.5 | 0.9337 |
| F_FREQ_MATCHED_k30 | 0.9200 |
| N1_k30 | 0.9575 |

**All arms sit in a tight 0.92-0.96 band. None of the selection-axis variants moves this number in
any direction that would indicate a real shift toward taxonomic/paradigmatic winners.** (Note this
cell's own P0 rate, 0.9225, is measured on its own n_probe=800 subset and is not directly comparable
in n to ARM 5's 79.3% at n=3994 -- both point the same direction, a large majority of winners have no
close WordNet relation, and selection does not change that fraction.)

**Both mechanism checks say the same thing: P1's marginal (statistically null) difference from P0 is
not coming from the mechanism the diagnosis predicted.** Whatever small numeric wobble exists across
arms is not concentrated on zero-co-occurrence pairs and does not shift the WordNet-relation profile.

## 6. THE FREQUENCY-MATCHED AND NULL CONTROLS -- WORSE THAN P0, NOT COMPARABLE TO IT

N1_NULL and F_FREQ_MATCHED_SELECTION are CI-separated BELOW P0 at every k (margins -0.0095 to
-0.0220). This did not need to be true -- P0 itself is already far below its own floor, so a control
could plausibly have tied it. Instead, destroying contributor identity (via either derangement)
measurably HURTS relative to P0, meaning P0's own co-occurrence-selected contributors are not
interchangeable noise; there is real, if small, information in WHICH specific words P0 selects. This
is a genuine (if secondary) finding: the "selection doesn't matter" reading of section 3 is not the
same as "any selection is as good as any other" -- P1's similarity-based selection ties P0, but a
degraded/randomised selection is measurably worse than either.

## 7. P2 (ZERO-COOCCURRENCE-ONLY) -- THE SHARPEST ARM, AND WHAT IT SAYS

The co-occurrence census (full 34,169-sentence corpus): mean anchor degree 259 of 5491 (~4.7%), so
the zero-co-occurrence candidate pool is large and never runs short -- `fraction_rows_with_zero_admissible
= 0.0` and `fraction_rows_full_k = 1.0` at every swept k (10/30/100). P2 is therefore a clean test:
every one of its contributors is, by construction, a word that has NEVER shared a sentence with the
target anywhere in the corpus.

**P2 does not collapse to the scramble floor.** It sits close to P0's own level (ties it at k=30 and
k=100, is CI-separated BELOW it only at k=10). Read plainly: contributors chosen purely by profile
similarity, with co-occurrence information entirely and provably excluded, recover essentially as
much of the read-out's (very small) signal as P0's co-occurrence-selected contributors do. **This is
itself informative** -- it says the read-out's signal is not concentrated in the co-occurring
neighbourhood the way the diagnosis's syntagmatic-selection story implied; a completely disjoint,
never-co-occurring contributor pool carries a comparable amount of it.

## 8. STANDING RULE 12 -- ORTHOGRAPHIC LEAKAGE

Mean trigram-cosine of top-1 winners: all 16 arms cluster in 0.0198-0.0296, far from the orthographic
floor's own reference (1.0) -- no arm cleared anything via a disguised spelling channel.

**But the per-item correlation check on the best-scoring P1 arm (k100) is NOT clean, and it is
reported because rule 12 says a floor (or here, a numeric edge) is understood, never adopted.**
Correlation of (P1_k100's per-item gain over P0) against that item's own best-gold orthographic
score: **r=0.0474, CI [0.0197,0.0744], ABOVE zero** over all 3994 items, and **r=0.2611, CI
[0.1026,0.4081], ABOVE zero** among the 148 items where the gain is nonzero. P1_k100 does not
CI-separate above P0 overall, so this is a correlation on a null margin, not a claim of a floor
cleared by spelling -- but it means the tiny nonzero component of P1's per-item variation is not
orthography-free the way Arm 6's own W1 was reported clean. Flagged, not swept under the "ties P0"
headline.

## 9. WHAT THIS DOES AND DOES NOT LICENSE

- It does NOT license "selection was the missing piece" -- P1 ties P0 CI-separated at every swept k,
  and neither clears any of the four floors (recomputed on this population: F_ORTHOGRAPHIC 0.08731 is
  binding throughout; the read-out sits at roughly 0.35x it, essentially unchanged from the landed
  incumbent's own 0.35x-the-floor reading in the sibling diagnosis cell).
- It DOES license retiring "selection is untested" -- selection has now been varied, one variable at
  a time, with the identical payload, cue, pool, gold and scorer as the payload test, and it produces
  no CI-separated change in either direction (except the two controls, which are worse, and P2_k10,
  which is also worse).
- **Combined with section 10-11's payload result, this write rule has now been tested on BOTH axes
  the dispatch could name (what gets summed, which words get summed) and neither moves the read-out
  meaningfully.** The remaining ~3x gap to the floor is not explained by either axis of this
  particular write-rule family (sum of first-order profile rows, whichever candidates supply them).
  This is evidence for redirecting the programme away from further write-rule variants of THIS family
  specifically, not evidence that no write rule could ever help -- the standing rule against
  generalising a narrow implementation failure to "impossible" still applies; what is retired is one
  family (unweighted sums of first-order profile rows), not the broader write-rule axis.

## 10. WHAT THIS RUN DOES NOT CLAIM

- No number here crosses scorers, pools or populations; everything is hit@1 tie-corrected over 5491
  anchors, n=3994, the landed OPEN pool, WordNet generous gold.
- MECH_A/MECH_B are measured on capped subsets (COOC_JACCARD_MAX_ITEMS=1500 for the P0 baseline,
  n_new_wins for P1's own subsets which are all below the cap; N_PROBE_WORDNET=800 for MECH_B) --
  cost-bounded, not full-population, and reported with their own n.
- `verdict_bar_check.py` was not additionally invoked by this cell (the STOP_IF logic here is native
  to the cell, evaluated arm-by-arm and reported in full in `STOP_IF_VERDICT`, not delegated).
- This cell does not wire anything into `hdlab/` -- promotion is the Director's decision.

## Organ reuse, runtime-witnessed

`exp_readout_writerule_paradigmatic_v1.build_arm` / `.deranged_permutation` / `.l2n_rows64` were
IMPORTED AND CALLED, never reimplemented -- P0 is built by the literal same function as the landed
W1, so the regression-gate reproduction is a structural guarantee. `tools/floor_battery` supplies
every floor and the scorer, never edited. `exp_cue_binarised_readout_transfer_v1.pearson_ci_bootstrap`
reused for the rule-12 correlation. `exp_grounding_readout_known_answer_v1.content_lemmas` /
`.build_corpus` / `.build_buckets` reused for the corpus/co-occurrence census. None of these files
were edited by this cell (`ORGAN_REUSE_RUNTIME_WITNESS` in the metrics, `sys.modules`-witnessed).

## Prior-work check (standing rule)

Enumerated via the same `experiments/` filter as sections 1 and 10's own prior-work checks
(readout / rerank / hub / csls / normal / argmax / rank / write / second_order / profile / selection):
no other cell in this repo varies the WRITE-SIDE SELECTION rule (as opposed to payload or read-time
comparator). This is the first selection-axis write-rule cell in the arc; it is not a rediscovery.
