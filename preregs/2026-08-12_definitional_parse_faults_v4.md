# PRE-REG -- definitional parse-fault repair (v4), 2026-08-12

Registered BEFORE the v4 build is run and BEFORE any v4 fact is looked at. Author: exp_dev.
Predecessor: `preregs/2026-08-12_definitional_grounding_v3.md` (DEF arm, 1751 facts, director
hand-score 38% MEANINGFUL / 18% RELATED / 44% NOISE, `notes/director_handscore_b3_def_vs_control_2026-08-12.md`).

## Question

Do the six measured parse-fault classes (`notes/definitional_parse_faults_v4_2026-08-12.md` s2)
cap the 38% quality ceiling, and does repairing them ALSO produce a multi-sense set that the
sense-selection eval can actually run on?

## Compute architecture

Class **(b) sequential-CPU with justification**: regex + WordNet lookups over 33k sentences;
v3's identical pipeline ran FULL in 35.7s. No matmul, no seeds, no sweep. GPU batching is
inapplicable. Storage strategy: `no_composition` (facts are banked into HDFactStore sharded, as
v3; nothing is bundled). Runs FOREGROUND to completion inside one call.

## Arms

- **V3_BASELINE** -- the landed 1751-fact set, read-only, for before/after counts.
- **V4_PARSEFIX** -- same corpus, same gates, same PMI floor, same seed-42 sampling, with the
  six fixes below in `hdlab/definitional_extraction.py`.
- No new mechanism is introduced. This is a precision repair, so the comparison is v4-vs-v3 on
  the SAME rubric and the SAME sampling procedure.

## What is fixed vs deliberately left (declared before implementation)

| class | fix | rationale |
|---|---|---|
| F5 head | head must be a WordNet NOUN (or out-of-WordNet); prefer the last NOUN of the lead NP; expand MEASURE/partitive heads (`pair of X`, `group of X`, `kind of X`) into the of-complement ONLY when that complement is indefinite (so `unit of THE kidney` is NOT expanded) | pure precision; no yield cost expected |
| F4 polarity | add exclusion cues (`without`, `lacking`, `no`, `not`, ...) to the NP-boundary set | 2 rows; nearly free |
| F2 lists | enumeration-trigger + coordinate-tail guard on APPOSITIVE; STRIP a leading coordinator from a CALLED definiens (do NOT reject: `arteriole -> vessel` is a GOOD fact whose definiens merely starts with "and then") and reject only when the stripped span is the last item of a comma list | |
| F6 glossary run-on | split a "sentence" on `<=4-word term>:` boundaries before extraction | new class found during verification |
| F3 truncation | store the FULL multiword term as the subject (`transcription bubble`), with the head lemma kept as a separate field; refuse run-on definienda (>4 content tokens or containing a finite verb) | see the identity note below |
| F1 proper nouns | expand contiguous capitalised name tokens (`Fan` -> `Shanhui Fan`, `Technologies` -> `Currie Technologies`) and TYPE the subject `PROPER` with case preserved, so a name can never fold onto a common-noun key. Proper nouns are NOT dropped: `Piraeus -> port`, `Drosophila -> fly`, `Omikron -> game` survive as proper-noun concepts | the collision is the fault, not the proper noun |

**DELIBERATELY LEFT:** (i) `lemma_verb`'s 13 unmigrated call sites (out of scope, flagged in v3);
(ii) inverted hypernymy (`species -> carp`); (iii) role-vs-meaning (`bowie -> act`,
`salmon -> consumer`) -- these are SEMANTIC faults, not parse faults, and no surface rule
separates them honestly.

**IDENTITY NOTE (F3, load-bearing).** Storing `transcription bubble` breaks the
lemma-as-concept-identity assumption used by the sense-selection eval and by
`hdlab/reading_grounding_loop`, which key concepts by single lemma. The v4 row therefore carries
BOTH `subject` (full term, the assertion-bearing key) and `subject_head_lemma` (the old key), so
downstream consumers can choose, and no consumer silently inherits a changed key.

## PRE-REGISTERED BANDS

### (a) FACT QUALITY -- NOT auto-scored, NOT claimed by this agent

A fresh 50-row sample is written UNSCORED to
`data/exp_definitional_grounding_v4/b3_audit_sample_DEF_V4.json`, seed=42, sampling procedure
bit-identical to v2/v3 (asserted in the cell self-test), same field schema, for the DIRECTOR to
hand-score on the same MEANINGFUL/RELATED/NOISE rubric.

| band | condition (MEANINGFUL rate on the director's hand-score) |
|---|---|
| HARD_PASS | **>= 50%** AND >= 900 v4 facts |
| PASS | **>= 44%** AND >= 700 facts |
| MIDDLE_BAND | 38-44% (inside the plausible one-judge disagreement band of v3's 38%) |
| **FAIL** | **< 38%** -- the repair did not improve quality |
| **FAIL (yield)** | fact count < 500, whatever the rate -- precision bought by collapsing the set |

Basis for 50%: 8 of the 22 NOISE rows in the director's sample are attributable to the six
classes (fan, technology, kidney->ureter, system->locomotion, structure->function,
cancer->collective, effect->magnification, kidney->pair overlap), and 4 RELATED rows are
truncation/head cases that the fix should promote. If every one converted, 19/50 -> ~29/50 = 58%;
50% is that estimate discounted for the fixes that will misfire. All HYPOTHESIZED@this prereg.

### (b) MULTI-SENSE YIELD -- auto-reported (counts, not judgements)

BEFORE, MEASURED@`data/analysis_definitional_parse_faults_v1/metrics.json`: 288 multi-sense
words / 723 facts in them / **102 senses with >1 source sentence** / 83 words with ANY such sense
/ **7 words with EVERY sense >1 sentence**.

| band | condition |
|---|---|
| YIELD_IMPROVED | senses with >1 source sentence **>= 150** AND words-with-every-sense-multi-sentence >= 12 |
| YIELD_HELD | >= 102 senses (non-regression) |
| **YIELD_REGRESSED** | **< 102 senses with >1 sentence** -- the sense eval gets WEAKER, and the two goals are in genuine tension |

**PRE-DECLARED EXPECTATION, so it cannot be spun after the fact:** the F3 fix pushes this number
DOWN (specialising `bubble` -> `transcription bubble` splits keys, so fewer facts merge), while
the F5 fix pushes it UP (normalising adjectival/partitive heads onto canonical genus nouns makes
more sentences merge into the same (subject, object) sense). **I do not know the sign of the
net.** If YIELD_REGRESSED fires, that is a REAL TENSION between fact quality and sense-eval power
and will be reported as such, NOT averaged away. Secondary, non-band change: the per-fact
`source_sentences` cap is raised 3 -> 10 (pure evidence retention; it cannot change the count of
senses that HAVE >1 sentence, only how many are kept for a downstream eval).

## FAILURE CONDITION (the cell's own, machine-checked)

- `HARD_FAIL_YIELD_COLLAPSE` if v4 facts < 500.
- `HARD_FAIL_SAMPLING_DRIFT` if the seed-42 sampling procedure is not bit-identical to v2/v3
  (self-test asserts on a 634-length synthetic list).
- `HARD_FAIL_REGRESSION` if any of the 6 confirmed fault rows still reproduces after the fix
  (each is a named regression test in `hdlab/definitional_extraction._self_test`).
- `HARD_FAIL_CONTROL_ROWS` if any of the known-good rows (`aorta -> artery`,
  `cholesterol -> lipid`, `arthropoda -> phylum`, `Piraeus -> port`, `Drosophila -> fly`,
  `arteriole -> vessel`) is lost. Precision fixes that also kill good facts are not a win.

## Discipline fields

- `arms_differ_verified`: v3 vs v4 fact sets are hash-compared; identical sets = the fix did not
  fire = BLOCK.
- `final_metrics_atomicity`: `tmp_replace`.
- `crlb_n/a`: no noise floor -- this is a deterministic symbolic extraction, not an estimator.
- `baseline_in_band`: n/a (the baseline is a hand-scored rate of 0.38, inside (0.05, 0.95)).
- `calibration_check`: `default_ok_for_this_regime` -- the PMI floor, closed-class gate and
  n_dim are carried over UNCHANGED from v3 so the only moving part is the parser.
- `cell_chunked`: false (single deterministic pass, no seed axis).
- `defensive_error_checking`: start marker + crash metrics + no bare except; heartbeat n/a
  (35s run).
- **WIRE STATUS: `VET_PENDING`.** No fix in this pre-reg may be promoted to WIRE until the
  director's hand-score exists. The evidence for these repairs is mechanism-level (each fault
  reproduces, each fix has a regression test); that justifies landing them, NOT promoting them.
