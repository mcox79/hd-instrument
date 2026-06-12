# Research -> Exp-Dev: UNROUTED experiments inventory + prioritized + 6 candidate cells routed + 6 deferred-with-rationale

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Routing inventory check per USER question "have you routed all experiments?"

## TL;DR

Honest answer: NOT all enumerated experiments routed. Per USER question:
- **Routed Day 1+ → Day 2 morning**: 18+ cells (multi-seed Tier-A promotions + chunking richfeat + GPU head-to-head P1-P3 + math/NER drill paths executed)
- **Enumerated in drills but NOT YET explicitly routed**: ~12 experiments
- This routing inventory: 6 ranked HIGHEST PRIORITY + 6 deferred with rationale

## Already-routed experiments (Day 2 morning state)

### Exp-Dev CPU (active)
- Chunking richfeat v2 (POS-trigram + capitalization-run; HARD-PASS 0.93+ target)
- Slot-filling ATIS multi-seed n=5
- Dep-parse UAS multi-seed n=5

### Exp-Dev GPU (authorized just now)
- P1 POS-v2 head-to-head fix (timeout fix + 500-sent subset)
- P2 NER 4-type head-to-head vs LLM 0.5B+1.5B+3B 5-shot
- P3 Chunking head-to-head (AFTER richfeat v2 lands; clean comparison)

### Exp-Dev pending optional
- Resonator R1 multi-occurrence entity coreference (Direction 2; substrate-only path Drill 1 RANK 1)
- Substrate-self-knowledge QA (Direction 3; Tier 5 prep)

### Testbed (active)
- Phase 2-5 evolve.py auto-ingest (running background)
- Hypothesis 1 validator running
- Phase 6 parameterized evolve.py BUILD
- Option E day-1 fix + Option B+H architectural + Option G sequence (per Drill 1)
- CoNLL-2000 bundle (delivered)
- Phase 6a math batch 03 Phase A1 (30 atoms) ingest
- Phase 6b 4 retrieval histories ingest

## UNROUTED ENUMERATED experiments (~12)

### HIGHEST PRIORITY (6 to route now)

**E1. NER Path 2 substrate-CRF Tier-1 shared feature library** (Drill 4 NER co-equal 2nd)
- Build shared feature extractors: Brown clusters + phrase clusters + morphology + gazetteer + position + context-window
- Reusable across NER + chunking + slot-filling + parse
- Substrate-product lever beyond single-capability
- Cell pre-reg HARD-PASS NER OntoNotes-18 F1 lift >=+0.03 / MIDDLE 0-+0.03 / FAIL <=0
- Cost: 4-6 hr CPU build + 1 hr cell

**E2. Transfer prediction P2: substrate-CRF Tier-1 -> CoNLL-2003 NER** (Drill 2 transfer-conditions framework discriminator)
- Validates transfer-conditions framework + substrate-CRF library
- HARD-PASS F1 >=0.85 (transfer framework P=0.42)
- Cell pre-reg per Drill 2
- Cost: 2-3 hr CPU (depends on E1)

**E3. Permutation-indexed binding P^k** (Drill 1 RANK 2 non-unique role binding)
- Alternative to FHRR vector binding for multi-occurrence roles
- Recchia-Jones 2015 random-permutation ~3x convolution paired-associate capacity
- Brain analogue: bump-attractor desynchronization (Wei-Wang-Wang 2012)
- Cell pre-reg HARD-PASS ASDiv multi-occurrence subset +10 abs pts / MIDDLE +5-10 / FAIL <+5
- Cost: ~1 CPU day

**E4. World-model simulation MWP solver** (Drill 3 beyond-discriminative RANK 1)
- Substrate-simulation of described scenario + observes state changes
- Brain analogue: prefrontal model-based reasoning
- Different mechanism class from discriminative-perceptron family
- Cell pre-reg HARD-PASS ASDiv-1op >= +0.05 over discriminative ceiling 0.385
- Cost: 1-2 CPU days build

**E5. Transfer prediction P5: PP-225 fact-recall -> KB-fact-from-MWP-text** (Drill 2 framework discriminator HARD-FAIL predicted)
- Tests transfer-conditions framework: predicted HARD-FAIL (P=0.012)
- Cell pre-reg HARD-PASS F1 >=0.50 / MIDDLE 0.30-0.50 / FAIL <0.30
- If HARD-FAIL as predicted: framework validated discriminatively
- Cost: 2-3 hr CPU (cheap framework test)

**E6. NER Path 5 discourse cross-sentence retrieval** (Drill 4 NER co-equal 2nd)
- Document-level coreference + cross-sentence integration
- Substrate retrieval primitives (not feature-based)
- Cell pre-reg HARD-PASS NER document-level F1 >=+0.05 vs single-sentence baseline
- Cost: 1 CPU day

### DEFERRED with rationale (6)

**D1. GHRR noncommutative matrix bind** (Drill 1 RANK 3)
- Already-filed GHRR-1 pilot per substrate v4.0 lineage memory
- Sequence after E3 permutation binding lands (similar mechanism class; defer to avoid duplication)

**D2. Frame-retrieval MWP solver** (Drill 3)
- Hofstadter slipnet / Gentner structure-mapping
- Per BMA finding (comprehension corpus-deficiency root cause): defer until post math+science ingest
- Re-test after Phase 6 lands

**D3. Analogy-retrieval MWP solver** (Drill 3)
- Same rationale as D2: defer until corpus-richer
- Cross-domain analogical transfer needs broader corpus

**D4. Transfer prediction P3: PP-371 reasoning routing -> SVAMP role-disambiguation** (Drill 2)
- MIDDLE predicted (P=0.024)
- Per BMA finding: MWP comprehension-bound; defer until corpus expansion
- Re-test after Phase 6

**D5. Transfer prediction P4: PP-364 POS HMM -> CoNLL chunking** (Drill 2)
- ALREADY DONE empirically (chunking 0.923 = transfer-validated; lift +0.0147)
- No new cell needed; already routed and run

**D6. Substrate-self-knowledge QA** (Direction 3; my prior routing)
- Substrate-only QA over own corpus
- Tier 5 prep
- Optional; defer if CPU budget tight

## Routing inventory honest summary

| Category | Count | Status |
|---|---|---|
| Routed Day 1+ → Day 2 morning | 18+ | Active or completed |
| HIGHEST priority routed NOW (E1-E6) | 6 | NEW this routing |
| Deferred with rationale (D1-D6) | 6 | Sequenced after E1-E6 + corpus expansion |
| Total enumerated experiments | 30+ | substantial substrate-product research backlog |

## Per brain-can-do-it standing rule

- 6 ROUTED now extend substrate-only mechanism exploration across MWP comprehension + NER feature-saturation + transfer-framework discrimination
- 6 DEFERRED have honest rationale (post-corpus-expansion re-test OR avoided duplication OR optional)
- NO ceiling claims; all substrate-only paths remain in inventory
- Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]: substantial untested path inventory

## Recommended execution order

CPU stream (parallel to GPU head-to-heads):
1. **E1 NER Path 2 substrate-CRF Tier-1 library** (build first; reusable)
2. **E2 transfer P2** (depends on E1)
3. **E5 transfer P5** (cheap framework test; HARD-FAIL discriminator)
4. **E3 permutation binding P^k** (substrate-only non-unique role binding)
5. **E6 NER Path 5 discourse** (after E1+E2 NER feature work)
6. **E4 world-model MWP** (1-2 CPU days; longest; sequence last)

Plus continuing Direction 1 multi-seed promotions + chunking richfeat v2.

## Cycle progression

This routing inventory closes the "are all experiments routed" question per USER. Multi-cycle execution Day 1+ → Day 2 morning:
- 18+ routed experiments
- 6 NEW priority routings (this note)
- 6 deferred with rationale

Substantial substrate-product empirical execution + honest scope.

## Cross-references

- Drill 1 output: notes/research_drill_substrate_eval_recall_gap_alternatives_2x_2026-06-11.md (Option B+H ranking)
- Drill 2 output: notes/research_drill_substrate_classical_mechanism_transfer_conditions_2x_2026-06-11.md (5 transfer predictions)
- Drill 3 substrate-non-unique-role-binding: notes/research_drill_substrate_nonunique_role_binding_2x_2026-06-11.md (6 paths)
- Drill 3 beyond-discriminative MWP: notes/research_drill_beyond_discriminative_mwp_mechanism_classes_2x_2026-06-11.md (8 classes)
- Drill 4 NER substrate paths: notes/research_drill_ner_substrate_paths_remaining_2x_2026-06-11.md (5 paths)
- Drill substrate Tier 5: notes/research_drill_substrate_tier_5_self_discovery_pathway_2x_2026-06-11.md
- Drill methodology rule calibration: notes/research_drill_substrate_methodology_rule_calibration_2x_2026-06-11.md
- Brain-can-do-it + literature-is-not-oracle + drill-defeatism memories

---

**Exp-Dev:** Routing inventory honest check per USER 18+ experiments routed Day 1+ → Day 2 morning + 6 NEW HIGHEST priority routings E1-E6 (NER Path 2 substrate-CRF Tier-1 library + Transfer P2 substrate-CRF -> CoNLL-2003 NER + Transfer P5 PP-225 -> KB-fact-from-MWP framework discriminator HARD-FAIL predicted + Permutation-indexed binding P^k Drill 1 RANK 2 non-unique role + World-model simulation MWP Drill 3 RANK 1 beyond-discriminative + NER Path 5 discourse cross-sentence) + 6 DEFERRED with rationale (GHRR after permutation lands + Frame-retrieval/Analogy-retrieval post Phase 6 corpus expansion + Transfer P3 reasoning routing -> SVAMP post-ingestion + Transfer P4 PP-364 -> chunking ALREADY DONE empirically + Substrate-self-knowledge QA optional) + Recommended execution order CPU stream E1 -> E2 -> E5 -> E3 -> E6 -> E4 parallel to GPU head-to-heads + per brain-can-do-it 6 routed extend substrate-only paths + 6 deferred have honest rationale + substantial substrate-product research backlog visible.
