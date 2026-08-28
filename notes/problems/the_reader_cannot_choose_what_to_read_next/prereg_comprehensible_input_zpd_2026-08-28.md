# PREREG: comprehensible-input / ZPD reading-foraging policy + graded anti-starvation

**Problem:** `the_reader_cannot_choose_what_to_read_next`. **Date:** 2026-08-28. **Author:** solver (opus).
**Cell:** `experiments/exp_reading_comprehensible_input_zpd_v1.py`. **Queue:** remote_cpu_queue (CPU-bound;
no CUDA in the cell -- the reading/grounding pipeline is sequential numpy; remote is for OFF-laptop
execution, not GPU acceleration, per owner standing rule "any heavy run goes to the remote desktop").

## Hypothesis
The brief's MVT-forager-with-value/gap/learning-progress mechanism is REFUTED on disk (neighbouring
`aimed_reading_is_built...`, REFUTED: the forager loses to FROZEN register-controlled, LP carries no
between-source information). The brain-faithful mechanism that works is COMPREHENSIBLE INPUT / ZPD
(Krashen i+1; Vygotsky; Metcalfe ROPL): choose the source with the most NEW learnable words in
comprehensible context. This is CONFIRMED at 3 seeds x 6000 sentences (CI_050 register-controlled
coverage 0.081 vs FROZEN 0.031 / RANDOM 0.029, CI-separated all seeds; info-free twin 0.015 loses).

## The pre-registered ADDITION being tested here (finer fidelity)
A high/adaptive-threshold reader STARVED (CI_085 0.012, CI_ADAPTIVE 0.011, grounding ~60 words). Finer
brain research (research_comprehensible_input_starvation_mechanism_2026-08-28.md) diagnosed a
GRANULARITY + COMPARATOR bug: a binary WHOLE-SENTENCE gate should be GRADED PER-WORD partial credit
(Yu & Smith 2007 -- humans learn from 6.25%-informative contexts by accumulating weak evidence), and an
ABSOLUTE threshold should be RELATIVE/ordinal (Florensa 2018; POET; PAIRED -- a fixed filter can return
an empty set and starve, a relative one cannot). New arm CI_GRADED implements graded per-word partial
credit (credit = max over a new word's sentences of g(local_known_fraction), g linear) -- no binary
sentence gate, so the selection score is never zero and never starves.

## Arms (register-controlled coverage metric; 3 seeds; per-(arm,seed) resumable)
FROZEN [floor], RANDOM [floor/info-free], CI_050 [proven], CI_085 & CI_ADAPTIVE [starved controls],
CI_GRADED [treatment], CI_SHUFFLED [info-free twin: comprehensibility scores permuted].

## Bar (falsifiable, from the research note Prediction 1)
- HARD-PASS: CI_GRADED reaches >= 80% of CI_050's grounded-word count with NO plateau (does not starve),
  and its register-controlled coverage is >= CI_085 / CI_ADAPTIVE CI-separated (starvation cured). Ideally
  CI_GRADED >= CI_050 (graded partial credit is a strictly more brain-faithful, principled selector than
  an arbitrary 0.5 cutoff).
- HARD-FAIL: CI_GRADED still plateaus near the ~60-word starved level (the bottleneck is candidate-word
  EXTRACTION from low-comprehensibility sentences, not evidence-weighting) -> localises the next drill.
- Info-free twin (CI_SHUFFLED) must LOSE CI-separated. Register-controlled, bootstrap CI, no number
  crosses populations/scorers.

## Controls
Info-free twin (shuffled comprehensibility); register stratification (probe split on FROZEN-reachability,
equal-weighted); RANDOM (choosing vs not-choosing); the starved CI_085/CI_ADAPTIVE arms as can-fail
references. Population (grounded subjects) saved per (arm, seed).

## Determinism / hygiene
Fixed integer seeds; sorted(set(...)); no Python hash(); ASCII-only; per-(arm,seed) resumable via
units.jsonl; final metrics.json written atomically (tmp-replace). Self-test + smoke both exit 0.
