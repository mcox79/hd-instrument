# USER Decision Memo — bge Scope Refinement (§6 A/B/C)

**Filed:** 2026-07-03 ~03:45 UTC (Director main-thread; Skunkworks-endorsed neutral framing)
**Referenced pre-reg:** `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` §6
**Framing discipline:** neutral evidence presentation; NO pre-framing per Skunkworks explicit instruction. USER decision is load-bearing gate for entire Stage 2 benchmark reframe.

## Purpose

Present atomic evidence for each of three scope-refinement options on the USER-locked directive "bge NEVER in substrate." Empirical evidence tonight has surfaced task-class fit as a load-bearing consideration that the original lock did not anticipate.

## Options (verbatim from prereg §6)

- **(A) Refined:** bge stays for KB CONTENT INDEXING (retrieval task class); substrate is brain-analog for M3/M4 CORTICAL/EPISODIC/COMPOSITIONAL tasks (its natural home).
- **(B) Nuclear:** DELETE bge-indexed 970K entities + 1.6M triples; re-ingest substrate-native on the new benchmark suite.
- **(C) Unchanged:** substrate must eventually retire bge everywhere; keep pushing brain-analog mechanisms until they beat bge or Stage 4 language architecture emerges.

## Shared Empirical Evidence (applies to all 3 options)

**Substrate-native mechanisms tested on Wikipedia open-domain title→body retrieval:**
- Char-trigram bag (VWFA-adjacent surface): SMOKE r@5=0.854 at N=500 → FULL r@5=0.703 at N=10K (`CG_MEASURED_BOUND` filed)
- PPMI/SVD (ATL-hub semantic): SMOKE r@5=0.906 at N=500 → FULL PRELIMINARY r@5=0.679 at N=10K (`PRELIMINARY_CG_HONEST_NEGATIVE`; formal re-dispatch in flight)
- VWFA multi-scale (position-bound char): Wikipedia SMOKE r@5=0.776 (underperforms char-trigram at N=500)
- Modern-Hopfield readout (Component C): SMOKE r@5=0.05 (attenuation floor; readout dead-end confirmed by drills)
- Spoke 3 hippocampal (DG+CA3+CLS): Wikipedia SMOKE r@5=0.145 (loses to char-trigram by 0.709)
- v3-composed (VWFA+PPMI equal-α): Wikipedia SMOKE r@5=0.914 (+0.008 above best-single; sub-discriminator)

**bge reference:** r@5=0.992 at N=100K (2026-06-19 landing via `backend/llm/bge_encoder.py`).

**Gap to bge (substrate-native best vs bge at scale):** char-trigram r@5=0.703 at N=10K vs bge r@5=0.992 at N=100K = **+0.289** gap. Not closed by any tested substrate-native mechanism.

**Same primitives tested on brain-analog task class (Spoke 3 CLS episodic binding, N=50 pairs, 4.8% of Tsodyks-Feigelman capacity 1047):**
- ARM_HIPPOCAMPAL_ONE_SHOT r@1=1.000 (existence proof; MM_STANDARD)
- ARM_COSINE_BASELINE r@1=1.000 (regime-too-easy; discriminator-doesn't-fire caveat)
- Discriminating-regime probe in flight (N=500 approach capacity + adversarial + high corruption)

**Skunkworks META atoms:**
- `META_TASK_CLASS_MISMATCH_HIPPOCAMPAL_MECHANISM` — MM_STANDARD (2 witnesses: episodic HP + Wikipedia HF)
- `META_SUBSTRATE_NATIVE_STRUCTURAL_MECHANISMS_LOSE_TO_CHAR_TRIGRAM_BAG_ON_REAL_CONTENT_RETRIEVAL_AT_SCALE` — MM_STANDARD_5_WITNESS (parent; annotated with reframe "on retrieval task class specifically")

## Option A — Refined scope: bge for KB retrieval, substrate for cortex

**Evidence supporting A:**
- 5-witness META pattern: substrate-native structural mechanisms lose ON RETRIEVAL specifically
- Skunkworks task-class-mismatch META (MM_STANDARD 2-witness) — same primitives WORK on brain-analog task classes; TASK CLASS determines fit
- Spoke 3 episodic-binding r@1=1.000 (existence proof for mechanism-appropriate task)
- Retrieval is char-trigram-native; VSA-native tasks (analogy/composition/multi-hop/episodic/generation) are where brain-analog mechanisms belong
- Pragmatic: two-encoder system leverages each mechanism's strengths
- KB retrieval quality preserved (bge 0.992)
- Substrate development can focus on VSA-native benchmarks without retrieval as a blocker

**Evidence AGAINST A:**
- Two-encoder system violates substrate-purity principle
- bge is opaque transformer — some KB atoms carry non-substrate-native provenance forever
- Requires clear boundary between "bge-indexed retrieval content" and "substrate-native cortical/episodic content" — how do they interact?
- Could create long-term architectural debt if substrate M3+ needs to reason over bge-indexed content
- Cell 5 (Generation) M3 cortex-layer arc may need to interface with bge-indexed content — coupling issue

**Downstream implications if A chosen:**
- Stage 2 benchmark reframe (preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md) proceeds with VSA-native task suite
- bge stays in `backend/kb/*_ingest.py`; substrate-native encoders not re-attempted for retrieval
- Spoke 3 discriminating-regime probe (in flight) informs episodic-mechanism strength
- Stage 3-4 language architecture is separate concern from KB retrieval

## Option B — Nuclear scope: DELETE bge KB, re-ingest substrate-native

**Evidence supporting B:**
- Cleanest substrate-native property — no bge in substrate at all
- Original USER-locked directive (2026-07-01 glass_box_LLM_substrate_native_language_no_external_LLM) explicit
- Forcing function: substrate must develop brain-analog encoders capable of real-corpus content
- Removes architectural debt of two-encoder system
- Aligns with M3/M4/M5 milestones (glass-box conversational, agentic) requiring substrate-native throughout

**Evidence AGAINST B:**
- Substrate-native retrieval quality significantly below bge (r@5=0.703 vs 0.992 = 29% degradation)
- 5-witness META pattern predicts no current mechanism closes the gap
- Delete + re-ingest cost: 970K entities + 1.6M triples; hours-to-days operational work
- Risk: post-nuclear substrate KB retrieval performance may not support downstream M3/M4 tasks
- Task-class-mismatch evidence suggests the SOLUTION is not "better substrate-native retrieval mechanism" but "different task class" — nuclear delete-and-retry may not solve underlying issue
- Risk of substrate KB regression during transition period

**Downstream implications if B chosen:**
- Substrate-native encoder development becomes highest priority
- Spoke 3 discriminating-regime probe becomes decisive (if mechanism-vs-baseline separation strong, hippocampal may compose with surface for improved retrieval)
- Stage 2 benchmark reframe proceeds BUT retrieval also stays as a substrate benchmark
- Higher risk that Stage 4 language architecture needs redesign

## Option C — Unchanged: substrate must eventually retire bge everywhere

**Evidence supporting C:**
- Maintains original USER-locked directive as-is; no scope drift
- Forces continued brain-analog mechanism development
- Retrieval may become closeable at Stage 4 (language architecture) — premature to abandon
- USER 2026-06-30 M3 cortex layer note suggests fundamental architectural additions ahead
- Insufficient evidence yet: only ~1 day of Wikipedia FULL scale evidence; V2-A precedent shows discriminators sometimes narrow

**Evidence AGAINST C:**
- 5-witness META pattern: 5 heterogeneous mechanism classes all fail on retrieval — strong empirical signal
- Skunkworks 4-witness→5-witness pattern promotion path suggests architectural class-scope
- No brain evidence that hippocampus retrieves open-domain content — brain doesn't do this task class
- Keeping the lock as-is delays Stage 2 progress; substrate has 5+ CG'd primitives waiting for VSA-native benchmark deployment
- Substrate research time is finite — indefinite pursuit of retrieval closure has opportunity cost

**Downstream implications if C chosen:**
- Continued substrate-native encoder development for retrieval
- Stage 2 benchmark reframe (preregs/...vsa_native_task_suite.md) held pending retrieval-closure attempt
- Spoke 3 discriminating-regime probe becomes intermediate result; retrieval-focused rescue continues
- Higher risk substrate arc stalls on retrieval task class

## Cross-cutting considerations

**Fix#28 discipline note:** Skunkworks explicitly refused to pre-frame this decision. Every option has both supporting and refuting evidence. This memo is neutral by construction.

**META pattern promotion trigger:** parent 5-witness META `promotion_criterion_to_CG_META` now has TWO GATES per Skunkworks 2026-07-03 03:40Z guidance:
- Gate 1: Wikipedia FULL 10K formal 3-seed landing confirming preliminary within ±0.02
- Gate 2: Spoke 3 N=500 discriminating-regime witness (mechanism-vs-baseline separation)
- USER §6 decision timing: BEFORE promotion is optimal (informs whether the pattern reframes Stage 2 direction); AFTER promotion is acceptable (evidence-heavier decision)

**Substrate-KB state preserves optionality:**
- Current substrate KB is bge-indexed; nothing changes structurally if USER picks A or C
- Only Option B requires active substrate-KB destruction/re-ingest
- All 3 options compatible with Spoke 3 discriminating-regime probe result
- All 3 options compatible with PPMI FULL 10K formal landing

## Questions Director does not answer (USER decides)

1. Is bge acceptable as an opaque transformer for CONTENT INDEXING task class where substrate mechanisms empirically underperform, given USER-lock intent was avoiding external LLM in substrate reasoning path (not necessarily content indexing)?
2. Is the cost of Option B (delete + re-ingest 1.6M triples) worth the substrate-purity property?
3. Is Option C sustainable given 5-witness META pattern likely to promote to CG_META?
4. Does the reframe of USER-lock (bge NEVER → bge SCOPED-TO-RETRIEVAL) violate the intent behind the original lock, or does it honor the SPIRIT of the lock (brain-analog everywhere BRAIN operates)?

## Companion in-flight work (does not affect A/B/C decision)

- PPMI FULL 10K re-run: formal landing informs META CG_META promotion
- Spoke 3 discriminating-regime probe: informs mechanism validity independent of task class
- Stage 2 benchmark reframe pre-reg: authored + HELD; cell dispatch requires USER decision
