# ORGAN F -- is the accumulation gradient still climbing at 72 sentences per anchor? (2026-08-17)

Cell: `experiments/exp_organ_f_accumulation_depth_ladder_v1.py`. FULL run: `data/exp_organ_f_
accumulation_depth_ladder_v1/metrics.json`, 56.5s. Smoke (`--grid reduced`): `data/exp_organ_f_
accumulation_depth_ladder_v1_reduced/metrics.json`, 67.7s, same code path at reduced depth/population,
PASS. Self-test PASS (reuses `tools/floor_battery.self_test()` and `experiments/exp_cue_information_
audit_v1.self_test()` wholesale, plus this cell's own checks: profile-pool leak-safety on a hand-built
toy corpus with a real held-out gap, cumulative depth-snapshot construction against real
`raw_counts_for_window` calls, saturation-at-own-capacity, `scatter_rows` row placement, the
monotone-nondecreasing checker on a synthetic real-drop case, and random-occurrence-control
self-exclusion).

Prior-work check: `bash tools/substrate_query.sh "accumulation depth ..."` returned no output within
40s (same documented `hd_director_kb_continuous_ingest` livelock the sibling pipeline-ladder cell
already recorded). Grepped `notes/` for "accumulation depth" / "profile depth" / "depth sweep" /
"ORGAN F": 13 hits, every one a *different* sense of "depth" (chain-hop depth in the 2026-06-03
qb1/pp49 counterfactual-depthband cells), not sentence-accumulation depth. No prior organ-level
accumulation-depth ladder exists; `PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` itself records "LADDER:
NONE" for Organ F. Not a rediscovery.

## Plain-language answer

**Yes -- at the well-powered rung, more reading is still buying real gains well past the current
72-sentence operating point, and it is not a token-count trick or a frequency artifact.** In the
best-powered population (360 words with at least 128 real corpus sentences available), going from
72 to 128 sentences per word bought a further +0.050 [+0.014, +0.086] hit@1 gain -- CI-separated,
the single largest step-to-step jump measured in this ladder. The 90-sentence collection cap that
produced the "~72" figure in the first place turned out to be an arbitrary limit baked into one
function (`K_SENT_TOTAL=90` in `exp_grounding_readout_known_answer_v1.py`), not a corpus limit: the
same already-tokenised corpus supports testing individual high-frequency words out to 512+ real
sentences (one word, "people," has 2,001 available). Past 256 sentences the populations that still
qualify get too small (43 words) to say anything with confidence, so the honest answer has an edge:
still climbing at 128, probably still climbing (but underpowered to confirm) out to 256-512.

## The step (enumerated from live code, not from the brief's sketch)

Read `hdlab/reading_grounding_loop.py` (`ConceptSpace.observe`), `experiments/exp_grounding_readout_
known_answer_v1.py` (`build_buckets`, `_n_profile`, `build_items`), and the pipeline ladder cell's
own runtime-verified encoder identity. Accumulation is ONE step, not several: PLAIN UNWEIGHTED
SUMMATION of per-occurrence raw content-word counts across every profile occurrence of an anchor
(`self._sums[lemma] += ctx_vec`), no decay, no recency weighting, no per-occurrence cap, normalised
only once at read time via cosine. Two corrections to the brief's sketch, both load-bearing:

1. **Which occurrences are collected at all is an arbitrary 90-sentence cap in one function**
   (`build_buckets`, `exp_grounding_readout_known_answer_v1.py:359`), not a corpus property. This
   cell rebuilt buckets from the same already-tokenised 34,169-sentence corpus WITHOUT that cap:
   `k` (total occurrences) goes to 2,019 for the single most frequent anchor; 177 anchors have
   >=257 occurrences; 62 have >=513. "As far beyond 72 as the corpus allows" was a real, answerable
   question, not a ceiling already reached -- the landed +0.0263 number was measured at an
   artificial cap.
2. **A naive extension past 72 would leak a real evaluation sentence into the store.** The deployed
   held-out split (`build_items`) reserves the TAIL of the CAPPED (<=90) bucket as each item's real
   cue sentence -- a segment strictly INSIDE the first 90 sentences, not at the very end of the
   corpus. This cell's depth pool is therefore `buckets_capped[a][:n_profile_capped(a)]` (the
   deployed profile, unchanged) CONCATENATED WITH `buckets_uncapped[a][90:]` (fresh material the
   deployed system never saw as anyone's held-out cue), skipping the held-out gap entirely at every
   depth. Verified in `self_test()` against a hand-built toy example with a real gap.

## The four populations (fixed item set per ladder -- this is what makes step-to-step CIs valid)

| population | capacity band | n items (= n anchors) | depths tested |
|---|---|---|---|
| POP_128 | >=128 real sentences | 360 | 1,2,4,8,16,32,72,128 |
| POP_256 | >=256 | 126 | 1,2,4,8,16,32,72,128,256 |
| POP_512 | >=512 | 43 | 1,2,4,8,16,32,72,128,256,512 |
| BAND_72_128 | [72,128) -- a LOWER-frequency stratum | 334 | 1,2,4,8,16,32,72 |

Every rung within one population scores the identical item set (paired bootstrap, N_BOOT=10,000).
Oracle cue (matches the pipeline ladder's own B1/B2 diagnostic: query = the item's own accumulated
store row) and real held-out cue (reused READ ONLY from `exp_cue_information_audit_v1`'s own
checkpoint) both scored at every depth.

## Step-to-step gains, oracle cue, CI-separated only

| population | step | gain | 95% CI |
|---|---|---|---|
| POP_128 | 16 -> 32 | +0.0358 | [+0.0056, +0.0667] |
| POP_128 | **72 -> 128** | **+0.0503** | **[+0.0139, +0.0861]** |
| POP_512 | 72 -> 128 | +0.0936 | [+0.0233, +0.1860] |
| BAND_72_128 | 32 -> 72 | +0.0385 | [+0.0030, +0.0749] |

Every other adjacent step (in every population) is NOT_SEPARATED -- including POP_256's 72->128
step (point +0.0638, but CI [0.0, +0.1349] just touches zero at n=126) and POP_256's 128->256
(-0.0157, NOT_SEPARATED), and POP_512's 128->256 (+0.0236) and 256->512 (-0.0705), both wide and
NOT_SEPARATED at n=43. **The best-powered population (POP_128, n=360) is CI-separated ABOVE at
its own deepest tested step, meaning the curve is confirmed still rising at 128, not saturating.**
Beyond 128 we are underpowered (n<=126) to resolve climbing vs plateau vs reversal -- the point
estimates trend in both directions across POP_256/POP_512's deepest steps, none of it separated.

RANK confirms the same shape independent of the hit@1 threshold effect: median rank of the correct
gold anchor falls from 38 (depth 1) to 9 (deepest tested) in POP_128, 37.5->9 in POP_256, 46->7 in
POP_512, 43.5->13 in BAND_72_128 -- a 4-6x improvement in every population, monotone in the point
estimates. NOISE (d-prime vs the field's own p95, the sharper near-top-competitor separation)
shrinks somewhat over the same range (e.g. POP_128: 2.33->1.38) even as accuracy and rank improve --
the same pattern the pipeline ladder cell found on its cue-degradation axis: the near-top
competitors get relatively closer even while the correct answer's absolute position improves.

## Monotonicity

Three of four populations (POP_128, POP_256, BAND_72_128), both cue kinds, are fully
monotone-nondecreasing -- zero interference drops. POP_512 (n=43, the smallest population) flags
ONE borderline drop at its own D2->D4 step (fall 0.0465 vs combined half-width 0.0291, just over the
1.5-sigma tolerance); its own 95% CI on that step is [-0.1163, 0.0000], touching zero. The SAME
direction (small negative point estimate, NOT CI-separated) appears at the analogous D2->D4 step in
POP_128 (-0.0165) and POP_256 (-0.0241) -- better-powered populations showing the identical sign but
staying inside tolerance. Read plainly: this is very likely small-sample noise in the smallest
population, not a real early-depth interference effect. **No population shows interference at the
deep end** -- stop-if (v) does not fire.

## Controls

**TOKEN-MATCHED** (same total token budget, drawn from fewer/longer occurrences of the SAME
anchor): at D=72, NOT_SEPARATED (natural point +0.0279 above, CI [-0.0056,+0.0639] crosses zero) --
inconclusive at that depth. At D=128, the only clean result, natural is CI-separated ABOVE the
token-matched control: +0.0390 [+0.0028,+0.0750]. **At the one depth where this control resolves,
more real occurrences beat an equal token budget concentrated into fewer, longer ones -- the gain
is not a token-count effect.** Stop-if (iii) does not fire.

**RANDOM-OCCURRENCE** (D occurrence-counts borrowed from OTHER anchors' own profile pools, summed
as if they were the anchor's own): NOT_SEPARATED at D=72, but CI-separated ABOVE at D=128 (natural
beats random-donor by +0.1057 [+0.0667,+0.1472]) -- the largest clean control margin in the cell.
Confirms the gain needs the anchor's OWN relevant material, not just any extra vector. No leak.

**FREQUENCY STRATIFICATION**: BAND_72_128 (a band held deliberately LOWER-frequency than POP_128,
non-overlapping capacity range) shows the same qualitative shape over its matching first seven
depths as POP_128 -- mostly flat/NOT_SEPARATED early, one CI-separated rise near the top of its own
tested range (32->72, +0.0385). A genuinely lower-frequency stratum still shows depth-driven
climbing, which argues against "the depth curve is really a frequency curve in disguise." Not a
formal statistical test of curve-shape equality (that would need a larger, matched design), but the
qualitative pattern is the SAME kind of late rise in both bands, not absent in the lower-frequency
one. Stop-if (iv) does not fire on this evidence, though it is the weakest-tested of the four
stop-ifs and deserves a harder follow-up if this becomes load-bearing.

**K1/N1**: K1 (known-answer, oracle addressing at each population's deepest rung) reads 1.0000 in
all four populations (gate 0.95). N1 (real cue deranged within-population) reads addressing 0.0000
and hit@1 within each population's own chance band in all four. Both pass; nothing here is
published on a loose instrument.

## Floors, and the honest scope limit

Binding floor (max of orthographic/frequency/scramble/constant-prototype, recomputed on each
population's own item set, on the DEPLOYED 256-dim representation): POP_128 0.2333 (constant-
prototype), POP_256 0.2302 (constant-prototype), POP_512 0.2209 (orthographic -- the ONLY population
where a different floor wins, worth noting), BAND_72_128 0.2246 (constant-prototype). These
populations are drawn from frequent, generic words by construction (capacity-selected), so their
floors sit far above the pipeline ladder's full-population floor of 0.139. **Even at maximum
tested depth, the oracle-cue accumulation-only signal (0.116-0.151 across the four populations)
stays BELOW its own population's binding floor** -- POP_128 and BAND_72_128 CI-separated below;
POP_256 and POP_512 NOT_SEPARATED (small-n, could not resolve). This ladder answers the SHAPE
question (still climbing vs saturated), not whether accumulation depth alone ever closes the
representational ceiling gap -- on this evidence it does not, at any depth tested here.

## Answer to each stop-if

- (i) still climbing at the corpus limit -> **confirmed climbing with a CI-separated margin up to
  at least 128** (up from the 72-sentence operating point); underpowered beyond 128 (n<=126) to
  confirm continuation to 256-512, though nothing in the data suggests a plateau either.
- (ii) saturated well before 72 -> **refuted**: BAND_72_128 itself is still climbing at 32->72.
- (iii) token-matched explains the gain -> **does not fire** at the one depth (128) where the
  control cleanly resolves; inconclusive at 72.
- (iv) frequency curve in disguise -> **does not fire** on the qualitative evidence; the lower-
  frequency stratum shows the same shape.
- (v) accuracy falls with depth -> **does not fire**; the one flagged drop is a small, borderline,
  smallest-population (n=43) fluctuation matching the same (not-significant) sign seen in every
  better-powered population at the identical step.
- (vi) K1 fails -> **does not fire**; K1/N1 both clean in all four populations.

## One plain-language sentence

More reading is still buying real, controlled gains at 128 sentences per word (nearly double the
current 72-sentence operating point), the gain is not just more tokens or any-extra-vector noise,
and it survives a genuine attempt to strip out the frequency confound -- but the corpus itself
limits how much further past 128-256 we can currently measure with confidence.

## Files

- Cell: `D:\AI\hd-instrument\experiments\exp_organ_f_accumulation_depth_ladder_v1.py`
- FULL metrics: `D:\AI\hd-instrument\data\exp_organ_f_accumulation_depth_ladder_v1\metrics.json`
- Smoke metrics: `D:\AI\hd-instrument\data\exp_organ_f_accumulation_depth_ladder_v1_reduced\metrics.json`
- Uncapped-bucket cache (gitignored): `scratch\organ_f_accumulation_depth_ladder_v1\buckets_uncapped.npz`
