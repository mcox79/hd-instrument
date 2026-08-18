# Director hand-score: v5 term-boundary B3 sample (2026-08-12)

**Scorer:** Director, single judge. Same rubric, same seed-42 sampling as the v2/v3/v4 scores, so
directly comparable. Sample: `data/exp_definitional_grounding_v5/b3_audit_sample_DEF_V5.json`
(n=50, arm n=2092). Prior scores: `director_handscore_b3_def_vs_control_2026-08-12.md`,
`director_handscore_b3_v4_parsefix_2026-08-12.md`.

## RESULT: HARD_PASS

| arm | MEANINGFUL | RELATED | NOISE | facts |
|---|---|---|---|---|
| v2 DIST baseline | 8% | 26% | 66% | 634 |
| v3 DEF | 38% | 18% | 44% | 1751 |
| v4 DEF parse-fixed | 40% | 16% | 44% | 1956 |
| **v5 DEF term-boundary** | **64%** (32/50) | 12% (6/50) | **24%** (12/50) | 2092 |

Pre-registered (`preregs/2026-08-12_definitional_term_boundary_v5.md`): HARD_PASS >=52%,
PASS >=47%, MIDDLE_BAND 42-47%, FAIL <=42% (= term-boundary theory wrong). **Landed 64%.**
The theory was right and the fix was binding.

## THE DIRECTOR'S "CEILING" READ WAS WRONG -- RECORDED SO IT IS NOT REPEATED

After v4 landed flat (38 -> 40), the director wrote that surface-pattern definitional extraction
"has reached its ceiling" and that the residual was structural. **That was wrong.** The plateau
was TERM CORRUPTION, not the approach: the v5 agent measured 314/1956 (16.1%) corrupted terms,
including 292/363 (80.4%) of all glossary facts carrying a term that is not a term of the
textbook. Fixing the boundary took corruption to 1.0% and quality 40% -> 64% in one step.

Lesson: a flat quality number across two passes is NOT evidence of a ceiling while a measured
defect of that size is still in the pipeline. Deflate ceiling claims until the known faults are
exhausted.

## WHAT DROVE THE JUMP

Glossary rows are now clean definitions rather than run-on garbage:
`ecology -> study`, `sarcolemma -> membrane`, `boreal forest -> biome`,
`extinction -> disappearance`, `oxidative phosphorylation -> production`,
`lateral line -> organ`, `club moss -> plant`, `natural science -> field`,
`genetic map -> outline`, `anthropoid -> clade`, `fat -> molecule`,
`noncompetitive inhibition -> mechanism`, `s-shaped growth curve -> shape`.
Thirteen clean glossary entries in the sample; in v4 that band was corrupted terms.

Proper-noun handling continues to hold: `Ban Ki-moon -> secretary-general`, `Harper -> politician`,
`Zimarco Jones -> founder`, `Levita -> producer`, `Williams -> officer`, `Gaustatoppen -> mountain`.

## RESIDUAL NOISE (12/50) -- all named, none mysterious

- proper-noun head errors: `Glazer -> manchester`, `label -> riveter`
- list read as appositive: `wings -> foreleg` ("Bat and bird wings, the foreleg of a horse, ...")
- adjectival head: `phylum mollusca -> large` (should be "group")
- CALLED firing on ordinary usage: `forward -> maria` ("Maria is called forward"), `forward -> step`
- term truncation still biting where the modifier is load-bearing: `Hyde Park -> block`
  (the term is "One Hyde Park", a building; "Hyde Park" is a park), `age -> indicator`
- contextual-not-definitional copula: `switch -> tragedy`, `start -> minimum`
- verb-participle head: `extremophiles -> belonging`
- partonomy read as definition: `filament -> stamen` (a filament is PART of a stamen)

## LIMITS

Single judge. Borderline calls: `Solspeil -> idea`, `cell cycle -> event` (head should be
"sequence"), `outermost layer -> mater`, `injury -> stab`, `belt -> zone` (term truncated from
"Kuiper belt"). The v3/v4/v5 comparison is internally consistent (same scorer, rubric, sampling);
the absolute level carries the director's judgement.

## SCOPE

This licenses: "surface definitional extraction supplies clean genus facts at 64% precision on
this corpus." It does NOT license any claim about the substrate LEARNING word meanings -- this is
a hand-written parser SUPPLYING facts, not a brain-faithful acquisition mechanism. See
`notes/brain_fidelity_audit_word_learning_2026-08-12.md` for that question.
