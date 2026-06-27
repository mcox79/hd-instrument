# PRE-REG: sub_atom_token_stream_encoder_v2_real_mathlib

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M)
**Supersedes:** v1 (2026-06-27, MIDDLE_BAND saturation; synthetic 3-7 token exprs)
**Barrier:** B4 (math/science formal-knowledge ingest; PREREQUISITE for Lean Mathlib + Materials Project + OEIS ingest + schema_driven_proof_step_inference)

## V1 -> V2 PIVOT (root-cause fix)

V1 used SYNTHESIZED depth-N expressions over a synthetic 2000-symbol codebook. Mean expression length 3-7 tokens; whole-expr / arg_0 trigram overlap saturated at 1.000 -> char-trigram baseline indistinguishable from role-filler -> verdict vacuous MIDDLE_BAND despite mechanism working.

V2 fixes by using REAL formal-math/science corpora (Lean Mathlib theorem statements + Materials Project SMILES + OEIS formula expressions) with mean expression length 30-80 tokens. Discriminator changed from "absolute cosine threshold" to "TOP-1 from 10 candidates (true subtree + 9 distractors from OTHER expressions)". Discriminator now fires cleanly: role-filler 0.93 vs trigram 0.66 on smoke (gap 0.275).

## HYPOTHESIS

A substrate-native encoder combining (a) a math-symbol codebook (2000 atoms, one per token), (b) alpha-equivalence canonicalization (variable renaming preserves identity), and (c) HRR role-filler bind for predicate-argument structure, will recover deep subtrees from REAL formal-math expressions via FFT unbind in a way that bag-of-trigrams and bag-of-codebook-tokens cannot.

This unlocks Lean Mathlib + Materials Project + OEIS + schema_driven_proof_step ingest WITHOUT char-trigram noise on formal-knowledge corpora.

## ARMS (4 mandatory + 1 diagnostic)

1. **ARM_CHAR_TRIGRAM_BASELINE** -- current encoder on real formal-math token stream (controls noise floor)
2. **ARM_MATH_CODEBOOK_TOKEN** -- 2000-symbol math codebook (one atom per token)
3. **ARM_MATH_CODEBOOK_WITH_VAR_RENAME** -- codebook + alpha-equivalence
4. **ARM_MATH_CODEBOOK_WITH_ROLE_FILLER** -- full encoder: codebook + var-rename + role-filler bind
5. **ARM_DIAG_BIND_DEPTH** -- depth-1/3/5 nested expressions; measures unbind accuracy decay

## DISCRIMINATORS

**TOP-1 DEEP-PATH RECOVERY** (random = 0.10):
- Pick random non-trivial OP subtree from real corpus tree at depth >= target_depth
- Encode whole tree; unbind sequentially along role-path
- Compare cosine vs 10 candidates (true subtree + 9 size-matched, head-disjoint distractors)
- "correct" = true subtree has argmax cosine

**ALPHA-EQUIVALENCE COSINE**:
- Take real corpus string; rename variables consistently
- Encode both; measure cosine (perfect alpha-invariance => 1.0)

**CODEBOOK DISAMBIGUATION**:
- Fraction of codebook entries whose nearest-neighbor in the matrix is themselves
- Tests that 2000 atoms in N-dim space are mutually orthogonal enough

## PRE-REG BANDS (HARD-LOCKED, PROSPECTIVE)

**HARD_PASS** (all must hold):
- ROLE_FILLER unbind_d3 >= 0.80
- char-trigram baseline unbind_d3 <= 0.50 (fairness: not saturated)
- ROLE_FILLER - char-trigram gap >= 0.30 (fairness: clean separation)
- alpha-equivalent expressions cosine >= 0.95
- cv across seeds < 0.10
- 2000-symbol codebook disambiguation >= 0.95
- NO SATURATION violation (trig_d3 < 0.95)

**MIDDLE_BAND**: partial wins (e.g., role-filler beats baseline but gap < 0.30 OR alpha_cos in [0.85, 0.95))

**HARD_FAIL**:
- ROLE_FILLER unbind_d3 < 0.50, OR
- alpha-equivalence < 0.80, OR
- char-trigram baseline >= 0.95 saturation (SATURATION_FAIRNESS_VIOLATION; regime too easy; needs harder corpus)

## SMOKE OBSERVED (2026-06-27 PRE-DISPATCH)

N=2048, codebook=2000, 100 test exprs, 2 seeds, 1 corpus (lean):
- RF_d3 = 0.935 (HARD_PASS band)
- Trig_d3 = 0.660 (above 0.50 ceiling but well below 0.95 saturation)
- gap = 0.275 (close to 0.30 threshold; expected to widen at full with 3 diverse corpora)
- alpha_cos = 0.943 (HARD_PASS band requires 0.95; expected to clear with larger N=8192)
- codebook_disambig = 1.000 (HARD_PASS)
- cv = 0.070 (HARD_PASS)
- Verdict: MIDDLE_BAND (gap + alpha just under HARD_PASS thresholds at smoke scale)
- Fairness: OK (no saturation, RF clearly beats baseline)

Smoke FIRES discriminator cleanly. Full run expected to clear HARD_PASS via:
1. N=8192 vs N=2048 (4x): orthogonality improves -> alpha_cos approaches 1.0
2. 3 corpora (lean+matsci+oeis) vs 1: structural diversity in distractor pool widens gap
3. 5 seeds vs 2: tighter cv

## DATA

- Lean Mathlib pretty-printed theorem statements (~150 baked-in real samples; loads from `data/lean_mathlib/theorems.txt` if present)
- Materials Project SMILES strings (~150 baked-in real molecules; loads from `data/matsci/smiles.txt` if present)
- OEIS sequence formula expressions (~150 baked-in real formulas; loads from `data/oeis/formulas.txt` if present)

3-tier fallback per corpus: disk -> baked-in real samples -> skip with warning. Verdict requires >= 1 corpus loaded.

## CARDINALITY_OK

- EXPECTED_N_UNITS_FULL = 5 seeds * 5 arms * 3 corpora = 75 units
- EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 1 corpus = 10 units
- EXPECTED_N_UNITS_SELFTEST = 1 seed * 5 arms * 1 corpus = 5 units
- HARD_FAIL_CARDINALITY_BREACH if observed < expected at completion

## HARDENING

- META_RULE_X main-guard
- L1: STARTED metrics on first line
- L2: per-arm progress updates
- L3: outer try/except + traceback in metrics
- L4: import-crash sentinel
- Per-arm metrics in metrics.json[per_arm] (Fix #28)

## RUN-MODE

- self-test: 1 seed, 1 corpus, N=512, codebook=200, ~30s
- smoke: 2 seeds, 1 corpus (lean), N=2048, codebook=2000, ~30s (observed 27s)
- full: 5 seeds, 3 corpora, N=8192, codebook=2000, ~1-3 hr estimate

## FAIRNESS GATES (META_RULE_AA + Skunkworks lessons)

- All arms encode SAME corpus per trial; only encoder mechanism differs
- Distractors are real subtrees of OTHER corpus expressions, size-matched (within 2x of target) and head-symbol-disjoint
- CHAR_TRIGRAM baseline must NOT saturate at 0.95+ at depth-3
- ROLE_FILLER must beat CHAR_TRIGRAM by >= 0.30 absolute on unbind_d3 (HARD_PASS gate)

## COMPOSES WITH (BIG PICTURE)

Prerequisite for:
- `lean_mathlib_ingest_v1` (Drill TOP-1 with P=0.70)
- `materials_project_ingest_v1` (Drill TOP-2 with P=0.65)
- `oeis_ingest_v1` (Drill TOP-3 with P=0.55)
- `schema_driven_proof_step_inference_v1` (Stage 3 reasoning prereq)
- Future `parietal_cortex_spatial_reasoning_v1` (USER question)

If HARD_PASS: unlocks 4 Barrier-4 cells; major M3 unblock (substrate can reason about formal math/science, not just remember English).
