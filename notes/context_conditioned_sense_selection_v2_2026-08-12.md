# Context-conditioned sense selection v2 -- re-run on v5 term-boundary-repaired facts

Re-run of `notes/context_conditioned_sense_selection_2026-08-12.md` (v1), aimed at the ONE
question v1 could not answer at adequate power: does the sense-from-own-sentences positive
control (C3) survive TOPIC CONTROL (same-segment) once v1's data-scarcity blocker
(621/723 v3 senses had exactly one source sentence) is eased by the v5 term-boundary fix.

Pre-reg: `preregs/2026-08-12_context_conditioned_sense_selection_v2.md`, filed before any v5
accuracy number existed. Cell: `experiments/exp_context_conditioned_sense_selection_v2.py`,
importing (not copying) v1's selectors, masking, `evaluate`/`run_c3`/`analyse_tail` -- the
three leakage mechanisms (L1 fit-corpus exclusion, L2 symmetric masking, L3 no metadata) and
the C1/C2/C3 controls are the SAME code, re-asserted fresh, not weakened.

## Prior-work check
`substrate_query.sh "context conditioned sense selection multi-sense word disambiguation floor
topic control"` top hit cosine 0.3965 (`control condition`), next relevant hit 0.3916
(`notes/research_context_conditioned_grounding_and_extraction_2026-08-07.md`, this arc's own
prior research note). No hit is an unrelated rediscovery -- this is a continuation of the
v1 cell in this same arc, not new territory.

## V5 yield -- verified off disk myself, twice
First pass (standalone recompute, pooling `source_sentences` across distinct literal-subject
rows that share a `subject_head_lemma`): `subject` 288/96/3 (exact match to the v5 note),
`subject_head_lemma` 379/**167**/**6** (NOT the note's 379/145/4). Second pass -- the cell's
own census function, which counts `senses_with_gt1_source_sentence` and
`words_with_ALL_senses_gt1` PER STORED ROW without pooling (the convention that actually
governs C3's power, since C3 builds each candidate's vector from that row's own sentences) --
reproduces the v5 note's numbers EXACTLY: `subject` 288/96/3, `subject_head_lemma` 379/145/4.
The two counting conventions differ only in whether sentences from two different literal
spellings sharing one head lemma get merged; unpooled (row-level) is correct for this cell and
is what ships in `metrics.json`. Both indexes are up from v3/v4 either way.

## Floor -- recomputed for v5, NOT v1's 0.4316
v3's k-distribution does not apply to v5 (term-boundary repair changed k). Recomputed and
asserted at runtime against the pre-registered values:
- `subject` (PRIMARY): mean k 2.2431, k-dist {2:230,3:49,4:7,5:1,6:1}, **floor 0.4634**
  (analytic), 0.4636 empirical (1000-seed sim).
- `subject_head_lemma` (SECONDARY, eval-only per the v5 note's own caution against using it as
  a stored-fact key): mean k 2.4538, k-dist {2:264,3:83,4:22,5:4,6:3,8:2,11:1},
  **floor 0.4401** analytic, 0.4402 empirical.

## MAIN ARM (sense = bare stored object word): HARD_FAIL on BOTH indexes, replicates v1

| index | best selector | acc | floor | C1 (swap) | C1 drop | C2 (lesion) |
|---|---|---|---|---|---|---|
| subject (PRIMARY) | S2_PERC | 0.4809 | 0.4634 | 0.4709 | 0.0100 | 0.4564 |
| subject_head_lemma | S2_PERC | 0.4449 | 0.4401 | 0.4228 | 0.0221 | 0.4316 |

All three pre-registered failure conditions fire independently on both indexes: both selectors
sit within 0.03 of their own floor (S1 0.4685/0.4293, S2 0.4809/0.4449 vs floors
0.4634/0.4401); the C1 swap drop (0.010, 0.022) is far below the required 0.05 (the "right"
and a "wrong" context produce nearly the same accuracy); C2 lesion sits within 0.03 of primary
on both. This is the same dissociation v1 found on v3 -- the collapse mechanism is not what is
missing, the stored object word alone carries no context-matchable signal -- reproduced
independently on a materially different, term-boundary-repaired fact set.

## MAIN QUESTION -- does C3 same-segment survive topic control at adequate power? NO.

| index | C3-SEG acc | n | 95% CI | floor | CI lower bound above floor? |
|---|---|---|---|---|---|
| subject (PRIMARY) | 0.5714 | 49 | [0.4327, 0.6998] | 0.4634 | **NO** (0.4327 < 0.4634) |
| subject_head_lemma | 0.5303 | 66 | [0.4116, 0.6457] | 0.4401 | **NO** (0.4116 < 0.4401) |

n rose modestly (v1's 45 -> 49 on `subject`; 66 on the larger `subject_head_lemma` index) but
not enough: on both indexes the CI lower bound still sits below the floor. **This is the
answer this re-run was built to get, and it is a negative.** With the eased data constraint,
context-conditioned sense selection, once topic/segment identity is controlled for, still
cannot be statistically separated from the floor at this corpus size. Report it plainly: it is
not established, and hunting a further slice that clears would be exactly the move the pre-reg
forbade.

For context, C3-SEG's own query-swap control: subject 0.4928 (n=69), head_lemma 0.4149 (n=94)
-- on `subject` the swap control itself sits close to the primary same-segment number (lift
only 0.0786), on `subject_head_lemma` the swap drops further (lift 0.1154) but the primary
number's own CI still touches the floor, so neither index earns a clean read.

## Raw C3 (uncontrolled for topic) -- still a genuine, swap-separated positive, both indexes
`subject`: 0.6606 (n=109, CI [0.5675,0.7426]) vs query-swap 0.5116 (lift 0.149) vs
count-matched 0.5652. `subject_head_lemma`: 0.6792 (n=159, CI [0.6032,0.7468]) vs swap 0.4368
(lift 0.242) vs count-matched 0.5918. Both replicate v1's dissociation (query-driven, not a
token-count/hub artifact) -- but per the pre-reg's stated purpose, raw C3 was never the open
question; same-segment was, and same-segment does not clear.

## Removed control re-verified fresh (not assumed)
Self-test re-runs v1's word-order-scramble invariance proof against the IMPORTED (unchanged)
`DistSelector`/`PercSelector` classes this run actually calls: max float delta 1e-9 across
reversed token order, incapable of changing an argmax. `python
experiments/exp_context_conditioned_sense_selection_v2.py --self-test` -> `SELF-TEST OK`.

## Verdict on both indexes
`subject` (PRIMARY, full term, the index the v5 term-boundary fix targets):
**HARD_FAIL_context_conditioned_sense_selection_DOES_NOT_WORK**. This is the index I consider
the honest primary, per the v5 note's own warning that `subject_head_lemma` reproduces the
over-generality F8 corrects and is defensible only as an eval convenience, never a stored key.
`subject_head_lemma` (SECONDARY): same verdict, same pattern, larger n throughout -- included
for power comparison and because C3-SEG's n is larger there (66 vs 49), and it still does not
clear. Final cell verdict recorded in `metrics.json` is keyed off the primary index per the
pre-reg.

## Artifacts
- Pre-reg: `preregs/2026-08-12_context_conditioned_sense_selection_v2.md`
- Cell: `experiments/exp_context_conditioned_sense_selection_v2.py`
- Metrics: `data/exp_context_conditioned_sense_selection_v2/metrics.json` (full run, 47.7s;
  `metrics_smoke.json` is the smoke gate, not a scored result)
