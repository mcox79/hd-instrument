# exp_dev hand-off — research: predicate evaluation primitives (5-op minimum set)

**Filed-by:** Research (Director)
**Date (UTC):** 2026-06-23
**Trigger:** Strategy drill de-risking top-tier enabling path #2 (substrate composition operator). HotpotQA comparison-em=0.07 (vs bridge-em=0.28) reveals substrate has STRUCTURAL composition (bind/bundle/permute = HRR) but is structurally blind to PREDICATE evaluation. This drill identifies the minimum 5-operator predicate-primitive set substrate needs to express comparison/temporal/negation/conjunction/existential predicates on retrieved facts.
**Trigger note:** `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md`
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If paused, queue and surface to USER.

**Per [[feedback-no-experiment-design-in-prompts]]:** anchor + bands + arms below; exp_dev owns the cell-author + smoke + dispatch + REMOTE VERIFY + per-primitive wrapper authorship.

---

## Anchor candidates (rank-ordered)

### 1. PRIMARY: `substrate_predicate_primitive_set_v1`

**Anchor pointer:** new anchor; first cell to test the FULL 5-primitive set (ORDINAL_COMPARATOR + TEMPORAL_PRECEDES + LOGICAL_NOT + LOGICAL_AND + QUANTIFIER_EXISTS) on a real-corpus discriminating split.
**Substrate-product reading:** establishes whether the substrate has predicate-evaluation expressivity beyond structural composition. Cell is the structural complement to the v3 QA cell — v3 tests the COMPARATOR primitive on full HotpotQA dev; this cell tests the FULL primitive set on a stratified question-class breakdown to identify which primitives carry the load and which are decorative.
**Tier hint:** SMOKE-to-PRODUCTION (start with 10 Q × 1 seed smoke; production at 30 Q × 3 seeds; ~30 min CPU; LOCAL_CPU_QUEUE).
**Why-now:** parent 5x drill identified comparator gap (in flight via v3); smoke 2x revival confirmed comparator math sound; THIS drill extends to the FULL primitive set. The LOGICAL_NOT primitive is free in bipolar substrate (zero-cost sign-flip; unlocks ~20% of HotpotQA comparison subset that current substrate outputs noise on). Per USER 2026-06-23 substrate-only product direction, this is the next-frontier expressivity test before any LLM positioning.

**Pre-reg HARD bands (verbatim from research note L4):**

**HARD_PASS (chain-grade predicate-evaluation composition):**
- A6 (FULL 5-PRIMITIVE SET) mean across 5 subsets ≥ FREQ_BIAS_BASELINE + **0.05**
- AND TEMPORAL subset: A4 − A3 ≥ +0.08 (temporal primitive does real work)
- AND NEGATION subset: A5 − A4 ≥ +0.05 (NOT primitive does real work)
- AND no primitive arm degrades baseline (A3..A6 each ≥ A2 − 0.03)
- AND CV across 3 seeds ≤ 0.10

**HARD_FAIL (predicate-evaluation class refuted at this substrate):**
- A6 mean ≤ FREQ_BIAS_BASELINE on aggregate
- OR TEMPORAL subset A4 − A3 < +0.03 (TEMPORAL_PRECEDES does not work)
- OR ANY primitive arm DEGRADES vs A2 by ≥ 0.05 (primitive is anti-informative; refute the primitive)
- → ROUTE to glass-box-LLM L2 closure for predicate evaluation; substrate-native predicate-eval lane structurally closed at N_DIM=8192 regime

**MIDDLE_BAND:**
- A6 mean in [FREQ_BIAS, FREQ_BIAS + 0.05] (matches or modestly above frequency)
- OR LOGICAL_NOT works but TEMPORAL_PRECEDES does not (partial closure; negation-grade)
- → MEASURED_MECHANISM (per-primitive grade); queue per-primitive redesign for failing primitives

**Anchor reproduction (Fix #16 discriminator-regime):**
- A1 (FREQ_BIAS_BASELINE) reproduces parent-drill measurement em=0.42 ± 0.03 on comparison subset (note: comparison-subset FREQ_BIAS may differ from full-dev FREQ_BIAS; pre-reg whichever is measured)
- A2 (GENERATION_ONLY) reproduces v1 em=0.07 ± 0.03 on comparison subset
- If either anchor fails: INCONCLUSIVE not HARD_FAIL

**6 arms × 5 question-class subsets:**
- A1: FREQ_BIAS (top-100 most-frequent answers; by-construction baseline per parent META)
- A2: GENERATION_ONLY (v1 substrate; no predicate primitive)
- A3: COMPARATOR_ONLY (lift from smoke; tests generalization from synthetic to real)
- A4: COMPARATOR + TEMPORAL_PRECEDES (FPE phase encoding of dates; OR ordinal-on-year if FPE deferred)
- A5: COMPARATOR + TEMPORAL + LOGICAL_NOT (sign-flip on negation queries)
- A6: FULL 5-PRIMITIVE SET (+ LOGICAL_AND + QUANTIFIER_EXISTS)

**5 question-class subsets (each N_q=30, balanced):**
- TEMPORAL ("X born before Y" / "X founded after Y")
- ORDINAL ("X taller than Y" / "X older than Y")
- NEGATION ("X is NOT a Y" / "X did NOT do Y")
- CONJUNCTION ("X AND Y both did Z")
- EXISTENTIAL ("Did any of {X1,X2,X3} do Z?")

**Plus synthetic-corpus discriminator control** (well-quantized, retrieval-perfect equivalent of each subset) — if primitives work on synthetic but fail on real HotpotQA, failure-mode is encoder/retrieval (parent diagnosis confirmed), not primitive design. Recommend M=200 entities, N_DIM=4096, α=0.05.

**Resources:**
- N_DIM=8192 (production) / N_DIM=4096 (smoke)
- 5 subsets × 6 arms × 30 Qs × 3 seeds = 2,700 Q-evaluations per run
- ~10ms/q estimated → ~5 min CPU per run; +5 min synthetic discriminator
- Total: ~10–30 min CPU on local
- Routing: **local_cpu_queue** (cheap; no GPU needed; matmul-bound at small N is fine on laptop)
- Smoke: 10 Q × 1 seed × 6 arms × 5 subsets = 300 Qs × ~10ms ≈ 3 min total

**Pre-conditions (exp_dev owns):**
1. Lift COMPARATOR from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` into `hdlab/comparator.py` (already specified in v3 handoff).
2. Author NEW `hdlab/predicates.py` (~200 lines) with: `temporal_precedes`, `logical_not`, `logical_and`, `quantifier_exists`. See research-note L2/L3 for primitive specifications. ALL primitives forward-only (no W modification); ALL L2-norm preserving (within ε); ALL composable with existing bind/bundle/permute.
3. Author cell `experiments/exp_substrate_predicate_primitive_set_v1.py` with:
   - 6-arm dispatch over 5 question-class subsets
   - Synthetic-corpus discriminator control
   - Per-arm + per-subset metrics in metrics.json (including per-seed breakdown)
   - FREQ_BIAS reproduction check (must match parent-drill comparison-subset FREQ_BIAS within ±0.03)
   - Selftest: each primitive has a synthetic-input deterministic-output unit test (5/5 pattern)

**Hand-off complete. Exp_dev: author primitives, author cell, smoke 10×1, dispatch 30×3, REMOTE VERIFY, return verdict.**

---

### 2. SECONDARY (conditional on PRIMARY HARD_PASS): `substrate_predicate_temporal_fpe_musique_v1`

**Anchor pointer:** v2 of predicate-primitive arc; first corpus where TEMPORAL_PRECEDES with FPE phase-encoding adds value BEYOND ORDINAL_COMPARATOR-on-year (HotpotQA's temporal queries are mostly scalar-year; MuSiQue has relative/periodic temporal queries).
**Substrate-product reading:** validates FPE phase-encoding as a substrate-native primitive (USER lock-in amp directive alignment). Cross-corpus generalization test.
**Tier hint:** PRODUCTION (full MuSiQue temporal subset; ~1 hr CPU).
**Why-now:** if PRIMARY HARD_PASSes, the next-frontier test is FPE-distinct value (vs ORDINAL_COMPARATOR collapse). DEFER until PRIMARY result lands.

---

### 3. TERTIARY (conditional on PRIMARY HARD_PASS): `substrate_predicate_composition_depth_2_v1`

**Anchor pointer:** v3 of predicate-primitive arc; tests noise-accumulation prediction at predicate composition depth 2 ("X happened before Y AND X caused Z").
**Substrate-product reading:** validates the 1/sqrt(k) composition-noise prediction (USER HRR derivation); establishes substrate's predicate-depth ceiling.
**Tier hint:** PRODUCTION; requires custom multi-predicate question corpus.
**Why-now:** depth-2 composition is the next-leverage test after single-primitive validation. DEFER until PRIMARY result lands.

---

## Context pointers (paths, not summaries)

- `notes/research_drill_predicate_evaluation_primitives_2026-06-23.md` (this drill; primitive spec + composition cost analysis + per-primitive build cost)
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` (parent drill; FREQ_BIAS baseline discipline)
- `notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md` (smoke 2x revival; comparator math sound; discrimination-floor diagnosis)
- `notes/exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` (v3 QA handoff; complementary cell)
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` (per-arm metrics confirmed; COMPARATOR base implementation source)
- `experiments/exp_comparator_resonator_primitive_smoke_v1.py` (COMPARATOR + FPE selftest implementations to lift)
- `hdlab/binding.py` + `hdlab/bundling.py` + `hdlab/random_indexing.py` + `hdlab/whitening.py` + `hdlab/atoms.py` (existing primitives to compose)
- `hdlab/refuse_gate.py` (refuse-threshold primitive for AND/EXISTS construction)
- `hdlab/comparator.py` (NEW; per v3 handoff; lifted from smoke experiment)
- `hdlab/predicates.py` (NEW; this handoff; ~200 lines for the 4 new primitives)

---

## Contract section

**Exp_dev responsibilities:**
1. Author `hdlab/comparator.py` (per v3 handoff) and `hdlab/predicates.py` (per this handoff L2 specs).
2. Author cell `experiments/exp_substrate_predicate_primitive_set_v1.py` with 6 arms × 5 subsets + synthetic discriminator.
3. Selftest: each primitive has a synthetic-input deterministic-output unit test (5/5 sanity).
4. Smoke gate: 10 Q × 1 seed × 6 arms × 5 subsets; ~3 min CPU; verify FREQ_BIAS reproduction + no exceptions in primitive code paths.
5. Production dispatch: 30 Q × 3 seeds; ~30 min CPU; LOCAL_CPU_QUEUE.
6. REMOTE VERIFY (per Fix #21): poll for landing; surface to Research + Skunkworks on landing.
7. Return verdict per pre-reg HARD bands; Skunkworks classifies tier.

**Research (Director) responsibilities (done in this drill):**
1. Primitive set spec — DONE (L2 of research note)
2. Brain analog + lit references — DONE (Streams A+B+C)
3. Substrate-native build spec per primitive — DONE (L2 column 5)
4. Composition cost analysis — DONE (L2 last column + L3)
5. Pre-reg HARD bands — DONE (L4)
6. Hand-off file — DONE (this file)

**Cert-owner (Skunkworks) responsibilities (on verdict):**
1. Per-arm metrics honest re-read (Fix #28)
2. Tier classification (CHAIN_GRADE / MEASURED_MECHANISM / by-construction)
3. Per-primitive disposition: which primitives load-bearing / which decorative
4. Atomization: 3 META atoms (per L5 research-note SUBSTRATE-PRODUCT) + per-primitive results

---

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns experimental design within the pre-reg HARD bands. Exp_dev MAY:
- Adjust per-subset N_q for compute budget (must be ≥ 20 per subset for CV stability)
- Choose smoke regime (10–20 Q × 1 seed) — must pass before production dispatch
- Choose FPE encoding scheme (complex64 / qFHRR / scalar-fallback if FPE infrastructure not ready — fallback documented in cell)
- Defer TEMPORAL_PRECEDES FPE if blocking; substitute ORDINAL_COMPARATOR-on-year (Note L3: TEMPORAL collapses to ORDINAL on HotpotQA scalar-year subset; this is a documented degeneracy, not a regression)
- Choose negation-parser strategy (regex deterministic vs g1b-native vs hybrid)

Exp_dev MUST NOT:
- Skip FREQ_BIAS_BASELINE reproduction check
- Skip the per-primitive synthetic-discriminator control
- Claim HARD_PASS without all 4 HARD_PASS conditions met
- Modify the pre-reg HARD bands (they are sacrosanct per [[feedback-negativity-bias-symmetric-verify]])

Per [[feedback-substrate-mine-capacity-before-extrapolating]]: before dispatching, check whether any existing substrate cell already covers part of the primitive set. The COMPARATOR is covered by smoke + v3 handoff; the OTHER FOUR primitives have NO prior substrate evidence (verified via Grep on hdlab/ + experiments/). Do not duplicate.

---

*Hand-off file for substrate_predicate_primitive_set_v1 ready. Exp_dev: pick up at next refill / next exp_dev cycle / explicit hand-off invocation. CPU-cheap (~30 min total); no GPU required; LOCAL_CPU_QUEUE routing.*
