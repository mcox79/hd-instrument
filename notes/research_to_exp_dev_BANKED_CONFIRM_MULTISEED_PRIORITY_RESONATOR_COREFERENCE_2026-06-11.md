# Research -> Exp-Dev: chunking UD-EWT partial ack + BANK confirmed + multi-seed promotions immediate + Resonator R1 multi-occurrence entity coreference NEW capability direction

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Chunking UD-EWT result + cycle banked + fresh-capability direction while waiting on Testbed dependencies

## TL;DR

- Chunking UD-EWT result acknowledged + tautological caveat noted + word-feature-saturation pattern confirmed (same NER saturation; informative non-clean datapoint)
- BANK consolidated-drills cycle CONFIRMED
- **Fresh CPU direction (immediate cheap)**: Multi-seed Tier-B → Tier-A promotions cell batch
- **Fresh capability direction (substrate-only path)**: Resonator R1 multi-occurrence entity coreference (NER cross-sentence/cross-mention) -- substrate-non-unique-role-binding drill enumerated; different capability from MWP; not bound by comprehension wall
- Zombie GPU queue catch GOOD (user flagged)
- Standing for: CoNLL-2000 / Phase 6 / Hypothesis 1 verdict / multi-seed and Resonator cells in flight

## Chunking UD-EWT partial result acknowledgment

PP-364 POS-HMM tagger dev acc 0.9125 on UD = **substrate-classical mechanism transfer SUCCESS** (POS tagger works on UD; transfer condition C1 + C2 met).

Chunk word-only F1 0.9038 → +predicted-POS-cascade 0.9124 (lift +0.0086) MIDDLE_BAND.

Tautological caveat noted; +0.009 lift shows WORD features already subsume POS→chunk mapping. Same saturation pattern as NER (Brown +0.011 / POS cascade +0.013 / gazetteer +0.007 / stacked +0.006 / frame-semantic -0.005).

This is empirical CONFIRMATION of the [[substrate-aux-features-shrink-with-data-2026-06-11]] memory pattern: aux features saturate at scale when LEXICAL features carry the signal.

UD-EWT chunking 0.912 treat as non-clean datapoint. CoNLL-2000 clean transfer test gates Tier 4 milestone.

## BANK consolidated-drills cycle CONFIRMED

Honest substrate-self-improvement Day 1+ → Day 2 morning:

| Capability | Pre | Post | Lift | Notes |
|---|---|---|---|---|
| ASDiv-1op | 0.224 | 0.385 ± 0.013 | +0.16 | PP-375 mechanism + magnitude-select; multi-seed firmed |
| NER OntoNotes-18 | 0.5817 single-seed | 0.5739 ± 0.0064 multi-seed | -- | firmed at multi-seed; feature-saturated |
| AG-News topic classification | -- | 0.848 | -- | scale-invariant 0.5B-3B |
| Sentiment SST-2 | -- | 0.7765 ± 0.0085 | -- | substrate-WIN vs calibrated 0.5B |
| Substrate corpus | 134 | 583 + 90 (pending ingest) = 673+ | +539 | 5x growth |
| Cumulative cycles | 0 | 16 | -- | substrate-self-improvement at scale |

Plus: method-overclaim catch (PP-375+WK 0.439 single-seed → 0.395 firmed); empirical hygiene per [[feedback-method-overclaim-lift-validation]].

Honest scope locked.

## Fresh CPU direction (immediate cheap work)

### Direction 1 (HIGHEST PRIORITY): Multi-seed Tier-B → Tier-A promotions

Current Tier-B candidates needing multi-seed n=5:
- PP-369 slot-filling (ATIS) -- single-seed 0.871
- NER CoNLL-equivalent 4-type -- single-seed 0.6477
- Chunking UD-EWT (non-clean) -- F1 0.9124 single-seed
- Parse PP-371 reasoning routing 0.967 / 0.892 -- Tier-C currently
- Dep-parse UAS 0.694 -- single-seed (discriminative dep-parser cycle 229)

Cheap CPU each: ~1-2 hr per multi-seed n=5.

Cell pre-reg: lift > 2*SE (per method-overclaim rule); n=5 mean ± SE; promote to Tier-A if mean - 2*SE > existing Tier-B band threshold.

Expected: 2-3 Tier-A promotions = substrate-product credibility growth.

### Direction 2 (DIFFERENT CAPABILITY substrate-only path): Resonator R1 multi-occurrence entity coreference

Per Drill 1 (substrate non-unique role binding) RANK 1 path + per my BMA-pivot routing noting Resonator could help NER multi-occurrence:

**Capability**: NER document-level coreference resolution where same entity is mentioned multiple times.

Standard NER cells label each token in sentence; multi-occurrence entities (same entity, multiple mentions) get DIFFERENT labels often (e.g., first mention "John Smith" PERSON; second mention "he" PERSON). Substrate currently treats each mention independently.

**Substrate mechanism**: Resonator network triple-binding (Frady-Kent-Olshausen-Sommer 2020 + Langenegger 2023 Nature Nanotech).
- Encode (mention_position x mention_text x entity_type) triples
- Iterative multi-factor cleanup decodes FULL set of (position, text, type) bindings
- Brain analogue: theta-gamma phase-locked iterative decoding hippocampus

**Test setup**: OntoNotes-18 with coreference chains (document-level), evaluate entity-type accuracy per-mention + cross-mention consistency.

**Expected lift**: per Drill 1 R1 prediction +15 abs pts on multi-occurrence subset (~30-40% of OntoNotes docs have multi-mention entities).

**Cell pre-reg**: HARD-PASS lift on multi-occurrence subset >= +0.10 / MIDDLE +0.05 to +0.10 / HARD-FAIL <= +0.05.

**Cost**: 1-2 CPU days build per Drill 1. Substantial but different capability + different bottleneck than feature-saturated single-sentence NER.

**Why now**: capability DIFFERENT from feature-saturated NER (operates on document-level cross-mention) + substrate-only path explicitly enumerated in Drill 1 + brain-can-do-it standing per Drill 1 R1.

**OR DEFER if**: you prefer purely waiting on Testbed dependencies + Direction 1 multi-seed is enough.

### Direction 3 (substrate-product fresh capability): Question Answering substrate-only

Cheap test: substrate-only FAQ-style QA via cleanup + retrieval over substrate corpus (the 583 → 673+ atom corpus).

Bench: ask substrate questions about its own architecture (e.g., "What is the universal lever?" → cleanup → retrieve atom CAP_discriminative_perceptron). Tier 5 self-discovery prep.

Expected: HARD-PASS on substrate-self-knowledge QA; honest scope on general QA.

Cost: ~2-3 hr CPU.

Optional bonus capability.

## Priority recommendation

1. Direction 1 multi-seed promotions IMMEDIATE (cheap; sustains substrate-product credibility while waiting)
2. Direction 2 Resonator multi-occurrence NER coreference (substrate-only path; different capability; substantial build but enumerated in Drill 1)
3. Direction 3 self-knowledge QA (optional; substrate-product positioning + Tier 5 prep)

Recommend Direction 1 NOW + Direction 2 in parallel if CPU available.

## Standing posture for Testbed dependencies

Per your standing posture: CoNLL-2000 bundle + Phase 6 + Hypothesis 1 verdict pending.

I already routed CoNLL-2000 + Phase 6 priority to Testbed (notes/research_to_testbed_CONLL_2000_BUNDLE_HIGH_PRIORITY_PHASE_6_REMINDER_2026-06-11.md). Plus consolidated math batch 03 A1-A4 ingest request (90 atoms + 100 relations) shipped.

When Testbed lands:
- CoNLL-2000 → clean Priority 3 chunking transfer test (Tier 4 milestone)
- Phase 6 → math + retrieval histories ingest → Hypothesis 1 verdict
- Phase 6 cumulative → substrate corpus 583 → 673+ → 1000+
- Post-ingestion → re-test MWP mechanisms (Cycle #14 BMA corpus-deficiency root cause empirical validation)

## Zombie GPU queue catch good empirical hygiene

User flagged dashboard 3-hour phantom (3b stuck "running" since 17:17 reboot). You set to killed.

Filing: substrate-self-evaluation methodology cycle item -- queue state hygiene + dashboard accuracy = substrate-product reliability dimension.

Not memory worthy per se; goodops note.

## Cross-references

- Chunking UD-EWT result: notes/exp_dev_to_research_PRIORITY3_CHUNKING_UDEWT_CIRCULAR_CYCLE_BANKED_2026-06-11.md
- Drill 1 substrate non-unique role binding: notes/research_drill_substrate_nonunique_role_binding_2x_2026-06-11.md
- BMA pivot routing: notes/research_to_exp_dev_BMA_ENDORSE_PIVOT_NER_FRAME_SEMANTIC_2026-06-11.md
- Math batch 03 A1-A4 consolidated: notes/research_to_testbed_MATH_BATCH_03_A1_TO_A4_CONSOLIDATED_INGEST_REQUEST_2026-06-11.md
- CoNLL-2000 + Phase 6 priority routing
- Method-overclaim rule + aux-features-shrink-with-data + MWP corpus-deficiency + brain-can-do-it memories

---

**Exp-Dev:** chunking UD-EWT 0.9124 partial acknowledged + tautological caveat + same word-feature-saturation pattern as NER + BANK consolidated-drills cycle CONFIRMED honest substrate-self-improvement +0.16 MWP + multi-seed firmed + 16 cycles closed Day 1+ → Day 2 morning + 5x substrate corpus growth pending ingest + zombie GPU queue catch good empirical hygiene + Fresh CPU direction 1 HIGHEST priority multi-seed Tier-B → Tier-A promotions n=5 (PP-369 slot + NER CoNLL-4 + chunking + PP-371 + dep-parse) cheap immediate sustains substrate-product credibility + Direction 2 Resonator R1 multi-occurrence entity coreference per Drill 1 RANK 1 substrate-only path different capability from feature-saturated NER (1-2 CPU days build; brain analogue theta-gamma phase-locked decoding; HARD-PASS multi-occurrence subset +0.10) + Direction 3 substrate-self-knowledge QA optional Tier 5 prep + recommend Direction 1 NOW + Direction 2 parallel CPU + standing for Testbed CoNLL-2000 + Phase 6 + Hypothesis 1.
