# The typed-context arms on the HUMAN instrument -- 6.39's pre-committed test, run as written

**Cell:** `experiments/exp_typed_role_context_human_instrument_v1.py`
**Metrics:** `data/exp_typed_role_context_human_instrument_v1/metrics.json`
**Smoke:** `data/exp_typed_role_context_human_instrument_v1_reduced/metrics.json` (12 pairs/cell)
**Pre-commitment:** `notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.39, committed `fa5da1d2c`
BEFORE this cell existed. Branches (A)/(B)/(C) were not renegotiated and no band was adjusted.

RESULTS SECTION IS WRITTEN BELOW ONLY AFTER THE RUN LANDED; every number in it is read off the
landed `metrics.json`, none is carried over from another population or another instrument.

## What was asked

`U1_TYPED_CONTEXT` read **0.6669 [0.6184, 0.7136]** on the WordNet instrument (DSI, n=242/cell,
bar 0.5431), CI-separated above its bar with its coverage control unmoved -- the only arm in this
programme ever to do that. It landed after `exp_dissociation_score_instrument_human_v4`'s 24-arm
harvest was built, so it had **never been scored against human judgement**. This cell scores it,
plus `U3_ROLE_ONLY` and `T2_UNTYPED_SAME_COVERAGE`, on the human instrument.

## How the two `T2_UNTYPED_SAME_COVERAGE` arms were kept apart

Two different cells own an arm with that name, and v4's `T1_TYPED_ROLE` is *not* `U1`:

| name in v4's 24-arm table | actual cell | construction | WordNet AUC |
|---|---|---|---|
| `T1_TYPED_ROLE` | `exp_typed_role_selectional_asset_writerule_v1` (SimpleWiki) | `TR.build_typed_role_matrix` + `TR.ppmi_svd` over the 737,488-slot persisted selectional asset | 0.5802 |
| `T2_UNTYPED_SAME_COVERAGE` | same SimpleWiki cell | `TR.collapse_roles` + `TR.ppmi_svd` | 0.5900 |

| name scored HERE | actual cell | construction | WordNet AUC |
|---|---|---|---|
| `U1_TYPED_CONTEXT` | `exp_typed_role_context_write_rule_dissociation_v1` | `URC.store_from_arc_events(mode="typed")` over arcs re-parsed from the 34,169-sentence corpus | 0.6669 |
| `U3_ROLE_ONLY` | same context cell | `URC.store_from_arc_events(mode="role_only")` | 0.6466 |
| `T2_UNTYPED_SAME_COVERAGE` | same context cell | `URC.store_from_arc_events(mode="neighbour_only")` | (context cell's own) |

Mechanically enforced, not merely asserted: this cell **never imports** the SimpleWiki typed-role
module, and its self-test asserts no `TR` alias exists in the module namespace. Every arm carries an
`ARM_PROVENANCE` entry in `metrics.json` naming its source cell, function and mode, and
`NAME_COLLISION_DISCLOSURE` states the trap in the metrics file itself.

## Method (no construction was reimplemented)

- Population: v3's own human population, loaded verbatim through v4's `v3_regression_gate()`. This
  cell contains zero matching, caliper or binning code.
- Arms: `URC.build_occurrence_data` (real persisted `pos_tagger`/`arc_parser`/`arc_labeler`
  front-end) -> `URC.flatten_arc_events` -> `URC.store_from_arc_events`, all called verbatim, on the
  human population's own `words_needed`. Scored with `DSI.dense_scores_from_dict_store` +
  `DSI.auc_bootstrap` -- the same scorer both instruments use.
- Context arm `A0_INCUMBENT_HUMAN` is v3's own cached `RAW_COUNT_FULL_ACCUM` score arrays on this
  identical population, reused bit-for-bit, never rebuilt.
- Both regression gates re-run through v4's own functions before any arm is built.
- Every floor recomputed on this population; the bar **derived** here as max(four floors), then
  cross-checked against 6.39's 0.5943 as a known answer.
- CI half-width and permutation-null p95 at this n reported beside every margin.
- `U1` vs `U3` read from the paired-difference bootstrap CI, never from CI overlap.

Gates, run before any arm was built, both PASS: GATE A (DSI's 8 cached checks, tol 0.0005) and
GATE B (v3's floors, tol 0.0005, `n_match == 65`). Bar **derived** on this population as
max(4 floors) = **0.5943** (owner `F_SCRAMBLE`), delta from 6.39's pre-registered 0.5943 = **0.0**.
Population: 65 pairs/cell, 180 distinct words, all 180 with corpus occurrences; 10,215 profile
occurrences, 28,832 arc events, 10.9% of occurrences carry a verb slot. No duplicate arm digests.

## RESULT -- pre-committed branch **(B)** fired

> **(B) `U1` LANDS AT OR BELOW CHANCE ON HUMAN JUDGEMENT** -> the 0.6669 was **WORDNET-SPECIFIC**,
> and rho 0.9034 was carried by agreement about the POOR arms while the instruments **DISAGREE at
> the top of the range** -- which is where it matters. **THIS IS THE INFORMATIVE CASE. IT MUST NOT
> BE REPORTED AS "MIXED", AND IT PARTIALLY RE-OPENS 6.24** *for the only region of the scale anyone
> cares about.*

| arm | AUC | CI95 | CI half-width | null p95 at n=65 | p (1-sided) | vs bar 0.5943 |
|---|---|---|---|---|---|---|
| `U3_ROLE_ONLY` | 0.5037 | [0.4026, 0.6026] | 0.1000 | 0.5846 | 0.4774 | NOT_SEPARATED |
| `U1_TYPED_CONTEXT` | **0.4125** | [0.3148, 0.5138] | 0.0995 | 0.5853 | 0.9570 | **BELOW_BAR** |
| `T2_UNTYPED_SAME_COVERAGE` | 0.3567 | [0.2613, 0.4533] | 0.0960 | 0.5841 | 0.9973 | BELOW_BAR |
| `A0_INCUMBENT_HUMAN` (reused) | 0.1796 | [0.1112, 0.2561] | 0.0724 | 0.5832 | 1.0000 | BELOW_BAR |

Floors recomputed on this population: `F_SCRAMBLE` 0.5943 [0.4937, 0.6911], `F_FREQUENCY` 0.4151
[0.3174, 0.5154], `F_CONSTANT_PROTOTYPE` 0.4125 [0.3164, 0.5153], `F_ORTHOGRAPHIC` 0.4920 [0.4466,
0.5359]; all four NOT_SEPARATED_FROM_CHANCE. `KNOWN_ANSWER_HUMAN_RATING` 1.0000.

**Precise, deflated statement of what U1 did.** Its point AUC is **below chance** but its CI
**includes** chance (hi 0.5138), so "below chance" is a point reading, not a CI-separated fact. It
**is** CI-separated **below the bar** (hi 0.5138 < 0.5943). It does not exceed its own permutation
null p95 (0.5853) in the substitutability direction.

**Power, stated because a width is not an effect.** n=65 vs the WordNet instrument's n=242 is 3.72x
smaller. `U1`'s CI half-width 0.0995 is **wider than the entire chance-to-bar interval**
(0.5943 - 0.5 = 0.0943). An effect sitting exactly at the bar could not have been CI-separated from
chance at this n. That cuts both ways and is why (C) existed as a pre-committed option -- (C) did
not fire only because U1 is not above chance.

## Paired margins (read from the difference CI, never from CI overlap)

| comparison | diff | CI95 of diff | half-width | null p95 abs | p (2-sided) | band |
|---|---|---|---|---|---|---|
| `U1` - `U3` | -0.0911 | [-0.2014, 0.0192] | 0.1103 | 0.1696 | 0.2924 | NOT_SEPARATED |
| `U1` - `T2` | +0.0559 | [0.0080, 0.1051] | 0.0485 | 0.0708 | 0.1258 | A_ABOVE_B |
| `U3` - `T2` | +0.1470 | [0.0372, 0.2575] | 0.1101 | 0.1662 | 0.0852 | A_ABOVE_B |
| `U1` - `A0` | +0.2329 | [0.1295, 0.3368] | 0.1036 | 0.1191 | 0.0000 | A_ABOVE_B |
| `T2` - `A0` | +0.1770 | [0.0821, 0.2724] | 0.0951 | 0.1077 | 0.0008 | A_ABOVE_B |

**Where the two tests disagree, both are reported.** `U1`-`T2` and `U3`-`T2` have bootstrap CIs that
exclude zero **while the observed difference does NOT exceed the arm-exchangeability null's p95**
(0.0559 vs 0.0708; 0.1470 vs 0.1662). Those two margins are therefore **not claimed**. Only
`U1`-`A0` and `T2`-`A0` clear both tests.

## The mandatory 6.39 clause: STOPIF3 is confirmed on BOTH sticks

`U1` - `U3` = **-0.0911 [-0.2014, 0.0192]**, NOT_SEPARATED (null p95 abs 0.1696). On the WordNet
instrument it was +0.0203 [-0.0185, 0.0591], also NOT_SEPARATED. *(The two numbers are reported side
by side as verdicts, never pooled or numerically compared -- different populations, different gold.)*
So: a **58-column role-only profile** matches a **10,121-column typed lexical profile** on both
instruments. 6.39's condition is met -- **the which-kind-of-slot reading stops being a
one-instrument caveat.** Here `U3` is nominally the HIGHER of the two.

## Beating `A0` is not a capability claim

`U1` is CI-separated above the incumbent bag-of-words (+0.2329, exceeding its null) -- but `A0` reads
**0.1796**, far *below* chance. Beating a strong co-occurrence detector while still sitting below
chance yourself buys no substitutability claim. Recorded so the +0.2329 is never quoted alone.

## CONFOUND THAT MUST BE NAMED BEFORE (B) IS READ AS MECHANISM

**The two instruments differ in PART OF SPEECH as well as in gold standard.** This human population
is **108 verb / 18 noun / 4 adjective** pair-slots (of 130) -- **83% verbs**. DSI's WordNet
population is **nouns only**. So "WordNet-specific" and "noun-specific" are not separated by this
run, and 6.39's branch-(B) mechanism (instruments disagreeing at the top of the range) is one of two
live readings.

Suggestive, **hypothesis-pending-VET, not a result**: the smoke run scored the first 12 pairs/cell,
which happen to be the population's entire non-verb stratum (18 n + 4 a + 2 v of 24 slots), and read
`U1` = **0.6458** there -- but with a CI half-width of **0.2326** ([0.3958, 0.8611]), which is a
width, not an effect, and nothing may be concluded from it. **The obvious next cell is a
POS-stratified re-read of `U1` at adequate n per stratum.** It is named here and deliberately NOT
run as part of this dispatch.

## Files

- cell `experiments/exp_typed_role_context_human_instrument_v1.py`
- FULL `data/exp_typed_role_context_human_instrument_v1/metrics.json` (326 s, `run_mode=full`)
- smoke `data/exp_typed_role_context_human_instrument_v1_reduced/metrics.json`
- logs `scratch/typed_role_human_full.out.log` / `.err.log` (stderr contains only benign
  `[SH-4]/[SH-5]` output-path banners from a sibling module import; no error)
