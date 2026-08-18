# Director hand-score: v4 parse-fix B3 sample (2026-08-12)

**Scorer:** Director, single judge. Same rubric and seed-42 sampling as
`notes/director_handscore_b3_def_vs_control_2026-08-12.md`, so numbers are directly comparable.
Sample: `data/exp_definitional_grounding_v4/b3_audit_sample_DEF_V4.json` (n=50, arm n=1956).

## RESULT: MIDDLE_BAND -- essentially FLAT vs v3

| arm | MEANINGFUL | RELATED | NOISE | facts |
|---|---|---|---|---|
| v2 DIST baseline | 8% | 26% | 66% | 634 |
| v3 DEF | 38% | 18% | 44% | 1751 |
| **v4 DEF parse-fixed** | **40%** (20/50) | 16% (8/50) | 44% (22/50) | 1956 |

Pre-registered (`preregs/2026-08-12_definitional_parse_faults_v4.md`): HARD_PASS >=50%,
FAIL <38%. **40% = MIDDLE_BAND.** A +2pp move at n=50 is inside sampling noise (se ~7pp).
**The parse fixes did NOT measurably improve fact quality.** Noise is unchanged at 44%.

## WHY -- the F3 fix traded one fault for another

F1 (proper nouns) clearly WORKED: `Chon->counsellor`, `Naeem->campaigner`, `Olkin->scientist`,
`Rajagopalan->student` are all correct now, and the v3 collisions (`fan->expert`,
`technology->seller`) are gone.

But F3 (store the full multiword term instead of the head) introduced a NEW dominant failure:
**corrupted multiword terms harvested out of glossary blocks.** 8 of the 22 NOISE rows are this:
`abiotic environment equili... -> state`, `apex consumers biome -> community`,
`cell centrosome cleavage f... -> constriction`, `photosynthesis place thyla... -> chloroplast`,
`postsynaptic membranes tem... -> memory`, `secretes digestive juices ... -> enzyme`,
`population -> allele`, `body temperature endotherm -> organism`.
Plus 3 more term-merge corruptions outside glossaries: `DNA RNA -> polymer`,
`Mars Bas Lansdorp -> founder`, `Wembley Stadium Bowie -> performer`.

So v3's truncated-subject fault became v4's corrupted-subject fault. The F6 glossary split fires,
but the term BUILDER still runs across entry boundaries inside those blocks. **That is the single
highest-value next fix and it is well localized.**

Residual faults NOT addressed by any fix so far, unchanged from v3:
- inverted hypernymy: `bacteria -> fixation`, `cell -> lymphocyte`, `pellucida -> event`
- adjectival/list heads still slipping: `Margaret Thatcher -> best`, `dominant phase -> short`,
  `quadrat -> wood` (first item of "a wood, plastic, or metal square")
- role-not-meaning: `predecessor -> warner`, `Lodge -> scene`

## HONEST NOTE ON THE FACT COUNT

1751 -> 1956 (+205) is NOT evidence of improvement. The agent reported 974 old pairs dropped,
1179 new, only 777 kept -- 44% of the set was replaced. Quality is flat; composition changed.

## LIMITS

Single judge; borderline calls include `oil->liquid`, `growth curve->shape`,
`final electron acceptor->molecule`. The v3-vs-v4 comparison is internally consistent
(same scorer, same rubric, same sampling), but +2pp is not a result.
