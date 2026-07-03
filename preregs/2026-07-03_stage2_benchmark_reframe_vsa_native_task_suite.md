# Stage 2 Benchmark Reframe — VSA-Native Task Suite (Pre-Registration)

Date: 2026-07-03
Type: **STRATEGIC pre-registration for the benchmark SUITE** — not a cell pre-reg.
Author: hdi_exp_dev (per Director spawn prompt 2026-07-03 evening).
Status: **HOLD** — requires USER approval + Skunkworks SCHEMA-VET-adjacent review before any cell in the roadmap is authored/dispatched.
Concept-query top hits (borderline, cosine 0.33-0.34): `notes/research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md` (already covers COMPOSITION + DECOMPOSITION benchmark protocols; this suite EXTENDS to analogy/multi-hop/episodic/cross-modal/generation).

---

## 1. Motivation

### 1.1 Empirical basis — 5-witness META pattern (2026-07-03)

Five substrate-native structural mechanisms have HF'd on Wikipedia open-domain title→body retrieval:

| # | Witness | Task | Result |
|---|---|---|---|
| 1 | v1 concept_encoder (WordNet) | title→body retrieval | HF |
| 2 | Component C modern-Hopfield readout | title→body retrieval | HF |
| 3 | VWFA multi-scale (Wikipedia) | title→body retrieval | HF |
| 4 | PPMI/SVD (Wikipedia FULL) | title→body retrieval | HF PRELIMINARY (formal 3-seed re-run in flight) |
| 5 | Spoke 3 hippocampal (Wikipedia SMOKE) | title→body retrieval | HF |

Char-trigram bag baseline at N=10K: **r@5 = 0.703** (substrate-native floor). Gap to bge-M3: **+0.289** (bge = 0.992).

Skunkworks META atom `SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE` — MM_STANDARD_5_WITNESS, HELD; CG_META promotion pending PPMI FULL formal confirmation.

### 1.2 Load-bearing Skunkworks meta-insight

Across all 5 witnesses: **ZERO cases of any brain-analog mechanism being tested on the NEUROSCIENCE-DESIGNED task class it was proposed for.**

- Hippocampal CA3 (Marr 1971 / Rolls / Treves): DESIGNED for one-shot episodic pair-binding + partial-cue completion; TESTED on open-domain title→body retrieval — mismatch.
- VWFA (Dehaene): DESIGNED for orthography → morphology → wordform lookup; TESTED on open-domain retrieval — mismatch.
- WordNet-seeded concept_encoder: DESIGNED for taxonomic hyponymy composition; TESTED on retrieval — mismatch.
- PPMI/SVD: DESIGNED for semantic-similarity via distributional co-occurrence; TESTED on retrieval where lexical-overlap baseline (char-trigram) is untouchable — mismatch.
- Modern Hopfield readout: DESIGNED for attractor-based cleanup on stored patterns; TESTED on open-domain cross-partition retrieval — mismatch.

### 1.3 USER-locked framing anchors

- **"Substrate knows almost nothing"** (USER-LOCKED 2026-07-02, `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet`) — every CG is mechanism proof on designer-supplied test; NO general knowledge ingested.
- **"Mechanism analog ≠ task analog"** (USER-LOCKED 2026-07-02, `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime`) — a brain-analog mechanism running on supervised synthetic data is still supervised-regime; the test task must also match the mechanism's design purpose.
- **Functional-requirement-first test design** (USER 2026-06-28, `feedback_functional_requirement_first_test_design_USER_2026-06-28`) — tests must decompose the functional requirement into what each primitive is supposed to do, then measure each primitive on its own designed function; retrieval-benchmark-only tests conflate composition of unmatched primitives.
- **"Concept-query-before-dispatch"** (USER-LOCKED 2026-07-02, `feedback_concept_query_before_dispatch_would_have_predicted_substrate_content_HF`) — 5-witness pattern was predictable from 2026-06-08 notes; the reframe is corrective, not novel.
- **Brain function is best-in-class reference standard** (USER-LOCKED 2026-07-02) — defaults brain-faithful; deviations need justification. This is the anchor for keeping brain-analog mechanisms in play under a task suite that MATCHES their neuroscience design.

### 1.4 Hypothesis to be tested (not a foregone conclusion)

**H_reframe:** substrate-native brain-analog mechanisms, when tested on task classes MATCHED to their neuroscience-designed function (VSA-native operations: bind/unbind/superposition/factorization + brain-analog operations: episodic pair-binding, morphology, semantic-hub composition), will exhibit HP/MB signal above the appropriate (task-class-appropriate, not char-trigram-bag) baseline. USER may reject or scope-modify this hypothesis; the empirical drill is what discriminates.

**Counter-hypothesis H_null:** substrate-native mechanisms may also HF on VSA-native tasks, in which case the substrate architecture (not the test-choice) is the load-bearing weakness and a deeper redesign is warranted. This possibility must remain live throughout the roadmap — the reframe is a hypothesis test, not a hedge.

---

## 2. Task class taxonomy

### (A) Analogy completion — a:b :: c:?

- **VSA-native operation:** bind + unbind + cleanup. `d_hat = c * (b * a_inverse)`; nearest-neighbor cleanup over codebook.
- **Brain-analog:** cortical semantic composition (temporal cortex role-filler binding).
- **Canonical benchmarks:** Google-analogy (Mikolov 2013; ~19K pairs across 14 categories, syntactic + semantic); BATS (Bigger Analogy Test Set, Gladkova 2016; more balanced categories); mimicking small-scale probes with substrate-authored codebooks first before external benchmarks.
- **Metric:** precision@1 and precision@5 against codebook cleanup; sweep codebook size K ∈ {64, 256, 1K, 10K}.
- **Baseline strategy:** vector-arithmetic on word2vec-style random projections (NOT char-trigram); parametrize D so char-trigram bag has NO cleanup mechanism (analogy target is not lexically-adjacent to inputs).

### (B) Compositional generalization — novel role-filler combinations

- **VSA-native operation:** bind (role * filler) + bundle (superposition of role-filler pairs) + unbind by role for filler retrieval.
- **Brain-analog:** frame:slot binding, cortical role-filler compositions (Smolensky TPR-adjacent; Plate HRR).
- **Canonical benchmarks:** held-out (role, filler) combinations never seen at codebook-population; SCAN-adjacent primitives (though SCAN itself is seq2seq, we adapt the compositional-generalization principle to VSA algebra: hold out specific pairs, measure recovery on held-out).
- **Metric:** precision@1 on held-out (role, filler) recovery; recovery-cosine vs seen-pair recovery-cosine gap.
- **Baseline strategy:** random role-filler baseline (unbind against random role vector); positive-control arm reproduces `notes/research_drill_vsa_composition_decomposition_2026-06-12` composition cell HARD_PASS bands at F=1/3/8.

### (C) Multi-hop reasoning — chain over knowledge triples

- **VSA-native operation:** recurrent unbind over composed relation-vectors. `answer = (subject * relation_1 * relation_2 * ... * relation_L)^{-1}` — or shard-storage per SHARDED_STORAGE_DEFAULT META rule (2026-07-02).
- **Brain-analog:** hippocampal-cortical multi-hop retrieval; semantic-hub theory (temporal pole).
- **Canonical benchmarks:** synthetic 2-hop and 3-hop compositions from substrate's existing KB triples (subject-relation-object); WikiHop or ComplexQuestions-adjacent when substrate ingest permits.
- **Metric:** per-hop precision@1; end-to-end (L-hop) precision@1; per-hop failure decomposition (which hop caused failure).
- **Baseline strategy:** bge similarity-search over KB baseline (2-hop = separate retrievals concatenated); NOT char-trigram (multi-hop factually depends on relation-composition, not surface-form).

### (D) One-shot episodic binding

- **VSA-native operation:** pair-binding (cue * target bundled) + partial-cue retrieval (correlate stored superposition with partial cue).
- **Brain-analog:** hippocampal CA3 pattern completion (Marr 1971; Rolls capacity; Treves; Nakazawa 2002 CA3 pattern-completion lesion evidence).
- **Canonical benchmarks:** synthetic paired-associate memory tasks; N-pair storage with partial-cue retrieval at recall; Spoke 3 hippocampal-analog cell (already in flight per Skunkworks recommendation) is the current dispatch under this task class.
- **Metric:** recall@1 vs stored pairs; capacity vs N pairs; partial-cue completion vs cue-completeness sweep.
- **Baseline strategy:** char-trigram bag baseline is NOT natural for this task (pair-binding is not surface-form); use lexical-overlap baseline OR uniform-random cleanup as floor.

### (E) Cross-modal binding

- **VSA-native operation:** role-filler binding across separately-encoded modalities.
- **Brain-analog:** cortical association areas (multi-modal convergence zones).
- **Canonical benchmarks:** DEFERRED — substrate currently has minimal cross-modal content (KB is text-only); reserved for post-M4 if/when substrate ingests image/audio.
- **Status:** noted for completeness; not in current roadmap.

### (F) Generation quality

- **VSA-native operation:** substrate produces a substrate-native vector as answer; readout to text via cortex layer (planned M3/M4).
- **Brain-analog:** cortical generation (M3 cortex above substrate per project memory).
- **Canonical benchmarks:** BLEU-N against reference; semantic-similarity to reference (embed answer + reference, cosine); mechanism-appropriate scoring per USER 2026-06-28 test-design.
- **Metric:** BLEU-4, ROUGE-L, semantic-cosine to reference; NOT perplexity (substrate does not produce token distributions natively).
- **Baseline strategy:** char-trigram bag has no natural baseline here (no generation mechanism); NO bag-of-words baseline exists — this is precisely the reason to include this task class as a discriminator escape from lexical-overlap dominance.
- **Note:** requires M3/M4 cortex layer scaffolding; DEFERRED until cortex-boundary primitives are operational (per project memory: M3 architecture needs cortex above substrate).

### Additional VSA/HDC literature task classes (Kanerva / Rachkovskij / Kleyko)

- **Set membership + cardinality** (VSA-native superposition-count via norm).
- **Sequence encoding + recall** (positional binding; MEASURED in prior CG-grade cells).
- **Analogical proportion 4-term extension** (2:1 :: 8:? algebra proportions on abstract sequences).

These are noted for taxonomy completeness; not all fit the current M3 arc.

---

## 3. Per-task-class mechanism-fit prediction

Prediction table — **HYPOTHESIZED@ this pre-reg; each cell in the roadmap must measure per Gate D reproduce-primitive-at-test-regime.**

| Mechanism | (A) Analogy | (B) Composition | (C) Multi-hop | (D) Episodic | (F) Generation |
|---|---|---|---|---|---|
| Spoke 1 competitive-Hebbian | HP | HP | MB | MB | (needs cortex) |
| Spoke 2 Foldiak trace | MB | HP (temporal invariance sub-tasks HP) | MB | MB | (needs cortex) |
| Spoke 3 hippocampal-analog | MB | MB | HP | **HP (in flight)** | (needs cortex) |
| VWFA multi-scale | HP (morphology/inflection subclass) | MB | (n/a) | (n/a) | (needs cortex) |
| PPMI/SVD | MB | MB | HP (semantic-hub matters) | (n/a) | (needs cortex) |
| Modern Hopfield readout | (n/a; is READOUT, not mechanism) | (n/a) | (n/a) | HP (attractor cleanup) | (n/a) |

**Reading:** predictions are STRONG PRIORS to be tested, not conclusions. Any HP prediction that MB's or HF's on measurement carries meta-signal about the mechanism's actual design fit; MB predictions that HF also carry meta-signal.

**Per META_RULE_AC:** all cells inheriting these predictions must tag them HYPOTHESIZED@ in cell notes; only per-cell MEASURED@ metrics.json paths can be cited as MEASURED.

---

## 4. Baseline strategy per task class

Central principle: **char-trigram bag is a natural baseline for RETRIEVAL because retrieval reduces to lexical-overlap in the open-domain case. It is NOT a natural baseline for tasks where VSA operations are load-bearing.** Each task class needs its own honest baseline that isn't bag-of-words-favoring.

| Task | Load-bearing operation | Char-trigram natural? | Proposed baseline |
|---|---|---|---|
| (A) Analogy | bind/unbind + cleanup | NO (analogy target is not lexically-adjacent to inputs) | Random-projection cleanup + word2vec-style vector arithmetic |
| (B) Composition | superposition + role-unbind | NO (composition target is a novel binding) | Random codebook + random role vectors (VSA-primitive baseline: does the substrate BEAT random VSA?) |
| (C) Multi-hop | relation-composition + cleanup | NO (multi-hop conclusion is not surface-form of inputs) | bge similarity-search + concatenation baseline (2 sequential retrievals) |
| (D) Episodic | pair-binding + partial-cue completion | NO (partial-cue completion is not surface-form) | Uniform-random floor + lexical-overlap floor |
| (F) Generation | vector → text readout | NO (no generation from bag) | Copy-input baseline; retrieval-from-KB baseline (return most-similar KB item) |

**Sanity check on each cell:** if the char-trigram bag baseline is UNTOUCHABLE on the task, that's diagnostic that the task is still retrieval-shaped and needs re-scoping.

---

## 5. Cell dispatch roadmap (2-4 week horizon)

**Cells are NOT authored now.** This is planning; each cell will be pre-registered separately per §7 (SCHEMA-VET-adjacent review).

Sequence (subject to USER + Skunkworks approval; USER may re-order or drop):

- **Cell 1 — Analogy completion baseline probe** (task class A)
  - Small-scale synthetic first (K=256 codebook, F=1 analogy); scale to K=10K Google-analogy subset if smoke passes.
  - Arms: substrate atoms (algebra-encoded) vs random VSA codebook vs char-trigram cleanup (expected to FAIL here — this IS the discriminator).
  - Compute class: batched-GPU (cleanup is matmul-heavy).
  - Pre-reg: separate.

- **Cell 2 — Compositional generalization probe** (task class B)
  - Held-out (role, filler) pairs; measures generalization on unseen bindings.
  - Reproduces `research_drill_vsa_composition_decomposition_2026-06-12` composition cell HARD_PASS bands as positive control (Gate D).
  - Substrate vs random-VSA vs bge-similarity baseline.

- **Cell 3 — Multi-hop reasoning probe** (task class C)
  - 2-hop synthetic KB triples first; 3-hop only after 2-hop HP.
  - SHARDED storage per SHARDED_STORAGE_DEFAULT (chain composition L≥2 = physics law rule).
  - Substrate PPMI/SVD arm vs bge-2-hop-concatenation baseline; substrate should HP or the mechanism has no home on multi-hop.

- **Cell 4 — Episodic pair-binding** (task class D)
  - Spoke 3 hippocampal-analog cell (already in flight per Skunkworks recommendation).
  - Task-designed test: N pair storage → partial-cue retrieval; SWEEP N (capacity) + cue-completeness ∈ {0.3, 0.5, 0.7, 0.9}.
  - NOT retrieval-shaped; this is the first task-designed reframe cell.

- **Cell 5 — Generation quality** (task class F)
  - DEFERRED until M3/M4 cortex-boundary primitives operational.
  - Placeholder; will re-visit when cortex-above-substrate arc has a candidate readout mechanism.

**Not in scope for current 2-4wk:** Task class E cross-modal (deferred until substrate ingests multi-modal content).

---

## 6. Scope-refinement on USER-locked "bge NEVER in substrate" — USER decision required

**Original locked directive:** bge NEVER in substrate. (`feedback_no_llm_comparisons`; substrate-quality-first per `feedback_substrate_standalone_capability_first_before_LLM_positioning_USER_LOCKED_2026-06-13`.)

**Empirical evidence 2026-07-03:** bge SUBSTANTIALLY beats substrate-native on open-domain title→body retrieval — r@5 = 0.992 vs substrate best = 0.703 at N=10K.

**Proposed refinement A (subject to USER decision, NOT auto-applied):**
- bge stays for **KB CONTENT INDEXING** (retrieval task class — where lexical/semantic-similarity is the load-bearing operation and bge is measurably superior).
- Substrate remains brain-analog for **M3/M4 CORTICAL / EPISODIC / COMPOSITIONAL** tasks (its natural home — the task classes matched to its designed function).
- Interpretation: two tools with distinct domains, not a rejection of substrate.

**Proposed refinement B (alternative, higher-cost, cleaner):**
- Retire bge from KB entirely.
- **DELETE the bge-indexed 970K entities + 1.6M triples.**
- Re-ingest fresh with substrate-native encoding on the NEW benchmark suite.
- Higher cost (re-ingest + re-eval); cleaner substrate-native property (no bge dependency anywhere).

**Proposed refinement C (do-nothing null):**
- Keep locked directive intact.
- Accept substrate-native only for KB + benchmarks; substrate will have to close the r@5 gap via mechanism improvement.
- Retrieval task class remains a permanent HF domain until substrate architecture is redesigned.

**This IS NOT an obviously-right decision.** Each refinement has legitimate cost/benefit; the reframe hypothesis (§1.4) can be tested under any of A/B/C. Refinement A minimally alters strategic posture; B is the maximally substrate-native pathway; C is status quo. USER decides.

**Framing discipline:** do NOT frame refinement A as "obvious" — it is a substantive scope change of a USER-LOCKED directive, requires explicit USER acknowledgement, and Skunkworks-adjacent second-witness review before enactment.

---

## 7. Skunkworks pre-VET flag + cell-dispatch gating

This pre-reg is **STRATEGIC**, not a cell pre-reg. It proposes a benchmark-suite reframe and cell roadmap; it does NOT dispatch cells.

**Gating for downstream cell authoring:**

1. **USER approval required** before any Cell 1-5 authoring begins. USER may reject reframe entirely (in which case: 5-witness HF pattern stands as CG_META finding without a cure path), scope-modify the task taxonomy, re-order the roadmap, or select bge-scope refinement A/B/C from §6.
2. **Skunkworks SCHEMA-VET-adjacent review** — each Cell 1-5 pre-reg will require SCHEMA-VET review per canonical §15 gates (sweep_alignment, discriminating_fraction, composition_edges, positive_control_arms, functional_requirements) before dispatch.
3. **Concept-query-before-dispatch** — each cell pre-reg must run `tools/substrate_query.sh` per its topic and report top hits, per USER-LOCKED 2026-07-02 discipline. Prior work on VSA benchmark methodology (2026-06-12 drill) will be re-cited in Cells 1-2 pre-regs.
4. **Cells 1-5 will be pre-registered SEPARATELY** — this pre-reg does NOT authorize any cell to dispatch; each roadmap cell is a distinct pre-reg + smoke gate + SCHEMA-VET pass.

---

## 8. Framing discipline (USER-locked; explicit)

- **Substrate knows almost nothing** — this pre-reg proposes Stage 2 benchmark reframe; it does NOT claim substrate can do the tasks. Every measurement in the roadmap is empirical, per-cell.
- **Brain-analog task classes for brain-analog mechanisms is a HYPOTHESIS to be tested, not a foregone conclusion.** H_null (§1.4) remains live.
- **No "physics law" language.** Composition physics-law atoms exist for chain-composition L≥2 (SHARDED_STORAGE_DEFAULT) but nothing in this pre-reg claims physics-law status.
- **No "first" or novelty claims.** The reframe is corrective; VSA-native benchmarks are well-documented in literature (Frady-Sommer 2020 Resonator; Schlegel 2022 survey gap; Plate 1995 capacity theory).
- **5 witnesses are cited as EMPIRICAL BASIS**, not as proof-by-count. The pattern MAY be over-generalized; two more (planned Spoke 3 FULL + PPMI FULL 3-seed) will confirm/refute the META atom's HELD status.

---

## 9. Open questions for Director/USER

1. **USER decision on bge scope refinement §6** — A / B / C / hybrid? What is USER's tolerance for altering the "bge NEVER" lock given empirical retrieval gap?
2. **Task-class prioritization** — should Cell 1 be Analogy (VSA-canonical, mature literature methodology) or Cell 4 Episodic (already in flight, hippocampal-designed)? Recommendation: dispatch Cell 4 FULL first (in flight); Cell 1 Analogy is the natural next new-authoring.
3. **Baseline codebook source** — for Cells 1-2, do we use substrate's existing algebra-encoded atoms as codebook, or generate fresh random-VSA codebook? Prior drill 2026-06-12 predicts substrate-clustered atoms may HELP or HURT relative to random-VSA — this is a discriminator worth measuring but requires deliberate arm design.
4. **Roadmap horizon adjustment** — 2-4 weeks may be optimistic; if PPMI FULL 3-seed re-run confirms HF (5th witness firms), and Spoke 3 FULL lands MB/HF, the META becomes CG_META and the reframe becomes higher-priority. Roadmap timeline is contingent on those two landings.
5. **Cortex-layer M3 dependency for Cell 5** — Generation quality cell requires cortex-above-substrate primitives (per project memory); is that arc alive enough in the next 4 weeks to author Cell 5, or is Cell 5 permanently deferred until M3 arc opens?

---

## References

- USER-LOCKED memories (§1.3): `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`; `feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_is_supervised_regime_USER_LOCKED_2026-07-02.md`; `feedback_functional_requirement_first_test_design_USER_2026-06-28.md`; `feedback_concept_query_before_dispatch_would_have_predicted_substrate_content_HF_2026-07-02.md`; `project_brain_function_is_best_in_class_reference_standard_USER_LOCKED_2026-07-02.md`.
- Prior methodology drill: `notes/research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md` (composition + decomposition benchmark protocols; pre-registered thresholds; 12 citations).
- Physics law referenced: SHARDED_STORAGE_DEFAULT for compositional cells (Skunkworks CG_META 2026-07-02).
- Canonical VSA literature: Plate 1995 (IEEE TNN); Frady-Sommer 2020a/b (Neural Comp Resonator Networks); Schlegel 2022 (AI Review survey); Kanerva 1988/2009; Smolensky 1990 TPR; Ganesan 2021 (NeurIPS projected HRR).
- Skunkworks META atom: `SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE` (HELD; MM_STANDARD_5_WITNESS).
