# Research -> Exp-Dev: CCC REVISED -- aggressive relational/analogical evaluation in CCC-1

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-04
**Subject:** REVISION to earlier CCC routing. User correctly flagged that CCC-1 as specified is too narrow (factual recall only). Substrate's distinguishing reasoning capabilities (analogical / counterfactual / compositional / cross-domain transfer) must be tested AGGRESSIVELY. This routing replaces earlier CCC-1 specification with broader evaluation.

---

## Why this revision

User pushed back: substrate is a STRUCTURED REASONING SYSTEM (VSA-native: binding, unbinding, factor recovery, compositional analogy). Earlier CCC-1 specification only tested factual multi-hop Q&A, which underdescribes substrate's actual reasoning capabilities.

**Substrate's distinguishing reasoning capabilities (must be tested aggressively):**
1. **Analogical reasoning via relational evaluation** — VSA-native; structural relations apply to novel entities
2. **Counterfactual reasoning** — cf-RPE mechanism validated; "what if X were different?" queries
3. **Compositional generalization** — chain stored facts to reach conclusions never directly stated
4. **Cross-domain transfer** — hierarchical aggregator validated 5/10/20 domains
5. **Knowledge graph reasoning** — VSA bindings ARE KG triples in vector form
6. **Type-respecting composition** — VSA binding algebra enforces structure

These distinguish substrate from "fancy retrieval system" framing. CCC-1 MUST evaluate them.

---

## CCC-1 REVISED (replaces earlier spec)

**Anchor:** `substrate_cognitive_core_pythia160m_AGGRESSIVE_relational_eval_v1`

### Architecture (PATH A distillation; unchanged)

- Pythia-160M encoder (frozen) -> last-layer activations on training corpus
- VQ codebook V_c=256 -> concept-ID sequences
- Substrate at N=8192 with B2 sparse + position-binding + STDP + B6 D-ECR
- 20 hierarchical domains
- SQ2 iterated retrieval (Mode 4) for multi-hop reasoning
- Pythia-160M decoder (frozen) -> fluent text from substrate output

### EVALUATION SUITE (this is the revision)

CCC-1 must score on FIVE distinct reasoning dimensions, not just one:

**1. Multi-hop factual recall (~25% of eval)**
- Standard NQ multi-hop subset: K>=2 hops required
- Tests basic retrieval + chaining
- Pre-reg: HP at >=55% acc vs baseline <=30%

**2. Analogical reasoning (~25% of eval; MOST DIAGNOSTIC)**
- Use HyperProbe analogy dataset (saturnMars/hyperprobe-dataset-analogy; ALREADY in Pythia extraction)
- Format: "A is to B as C is to ?" where (C, ?) pair was NOT stored directly but the relational structure (A, B) was
- Substrate must apply relational structure to novel entity via VSA binding arithmetic
- This is the strongest test of "reasoning vs retrieval" distinction
- Pre-reg: HP at >=50% acc on analogical completion vs Pythia-160M zero-shot baseline

**3. Counterfactual queries (~15% of eval)**
- Format: "Given context X, what would Y be if we changed Z?"
- Use cf-RPE primitive at inference: compute substrate output WITH context vs WITHOUT, return delta
- Test set: synthetic counterfactual chains built from corpus facts
- Pre-reg: HP at >=40% acc on counterfactual lift vs random baseline

**4. Compositional generalization (~15% of eval)**
- Format: chained reasoning where individual facts A->B, B->C, C->D are stored separately but the full chain A->D was never stated
- Tests whether substrate composes via SQ2 multi-hop into novel conclusions
- Use synthetic graph traversal tasks + held-out paths
- Pre-reg: HP at >=60% acc on novel-chain completion at K=4-8 hops

**5. Cross-domain transfer (~20% of eval)**
- Train on N-1 domains; test on held-out domain with SAME relational structure
- Tests hierarchical aggregator's transfer capability with new content
- Use multi-domain knowledge graph subset
- Pre-reg: HP at >=40% acc on held-out domain vs random + within-domain saturation

### Combined HP/MID/HF (replaces narrow factual-only spec)

- **HARD-PASS:** average accuracy across all 5 dimensions >= 50% AND substrate-led system beats Pythia-160M baseline on at least 3 of 5 dimensions
- **MIDDLE-BAND:** substrate beats baseline on 1-2 dimensions OR average 35-50%
- **HARD-FAIL:** substrate fails to beat baseline on any dimension OR average <35%

### Why this broader eval is more honest

- Narrow factual recall doesn't differentiate substrate from a vector database
- The reasoning dimensions (analogical / counterfactual / compositional / cross-domain) are where substrate's VSA algebra distinguishes from LLM probabilistic approximation
- If substrate beats Pythia-160M on ANY of these reasoning dimensions, that's evidence the architectural claim is real
- If substrate beats Pythia-160M on ALL of them, that's strong evidence for substrate-as-cognitive-core thesis

### Cost + wall (unchanged from earlier spec)

- ~$10-30 Lambda H100 (Pythia extraction; reuses Testbed's ready script)
- $0 substrate training (local CPU)
- ~6-10 hours total
- 3 seeds; total ~$30-90
- Engineering: ~3-5 eng-days (additional time for 5-dimension eval scaffold)

---

## CCC-1-EXTRA: Knowledge graph relational reasoning (new addition)

**Anchor:** `substrate_cognitive_core_pythia160m_KG_relational_v1`

### Why add this

VSA bindings ARE knowledge graph triples in vector form. This is substrate's natural strength. Adding a KG-specific test makes the evaluation diagnostic.

### Architecture
- Same substrate+Pythia-160M scaffold as CCC-1 REVISED
- Use Wikidata subset (~50k triples) as training corpus
- VQ encode entities + relations as concept-IDs
- Substrate stores subject-predicate-object bindings via VSA

### Test
- Triple completion: given (subject, predicate, ?) where pair was novel
- Multi-hop KG reasoning: chains across stored triples
- Analogical KG queries: (A, R, B) and (C, R, ?) -> retrieve D via relational structure

### Pre-reg
- HP: >=60% triple completion on held-out triples (analogical structure preserved)
- HP: >=70% multi-hop KG accuracy at K=3-5
- HF: <30% triple completion (substrate not using relational structure)

### Cost + wall
- $0 (reuses CCC-1's Pythia extraction; just different downstream eval)
- ~30-60 min substrate training
- ~30 min eval
- 3 seeds

---

## CCC-smoke REVISED (adds counterfactual + analogical sanity)

**Anchor:** `substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE_v1`

Add to earlier CCC-smoke synthetic test:

- Synthetic analogical chains: 100 (A, R, B) (C, R, ?) test pairs; check substrate completes via VSA
- Synthetic counterfactual queries: 100 "without pattern X what changes" deltas
- Cross-domain transfer: 5 synthetic domains; train on 4, test on 5th

Pre-reg unchanged on basic pattern recall; ADD:
- HP: analogical completion >=80% on synthetic; counterfactual delta correctly computed >=80%; cross-domain transfer >=70%
- HF: any of these <50%

Cost: still $0 CPU; ~15-20 min wall

---

## Priority order (revised)

1. **CCC-smoke REVISED** ($0; today; ~15-20 min): validates ALL reasoning mechanisms at smallest scale
2. **CCC-1 REVISED** ($10-30; Day 2-4): 5-dimensional eval at Pythia-160M tier
3. **CCC-1-EXTRA KG reasoning** ($0; Day 4-5): substrate's strongest natural test
4. **CCC-2** ($0; substrate-only ceiling test)
5. **CCC-3** ($20-100; PATH C continual)
6. **CCC-4** ($50-200; head-to-head)

---

## What's NOT changing

- Cost estimates (~$100-400 total budget)
- Timeline (~10 eng-days for complete validation)
- Architecture (PATH A distillation; same substrate config)
- Pythia-160M extraction is still the bottleneck on CCC-1 (Testbed script READY; needs queue)

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per [[feedback-no-padding-experiments]]: 5 eval dimensions each discriminate distinct reasoning capability
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: explicit HP/MID/HF per dimension
- Per [[feedback-cloud-only-when-absolutely-necessary]]: CCC-smoke + CCC-1-EXTRA + CCC-2 all $0; CCC-1 cheap cloud
- Per [[feedback-pressure-test-negative-findings]]: 5-dimension eval reveals WHERE substrate fails if it does
- Per [[feedback-drill-prompt-bodies-must-be-generic]]: standing for all future drills
- ASCII-only

PROT-018: anchors per cell above (`_AGGRESSIVE_relational_eval_v1`; `_KG_relational_v1`; `_AGGRESSIVE_v1`)
PROT-021: source=CPU + Lambda, run_mode=smoke/full, n_seeds=3

---

**END.**

**Exp-Dev:** CCC-1 evaluation broadened from narrow factual recall to 5-dimension reasoning test (multi-hop factual + analogical + counterfactual + compositional + cross-domain transfer). Plus CCC-1-EXTRA tests substrate's natural KG strength. Plus CCC-smoke broadened with analogical + counterfactual + cross-domain sanity tests.

This is the more honest test of substrate-as-cognitive-core. If substrate beats Pythia-160M on the reasoning dimensions specifically (not just retrieval), that's evidence the architectural claim is real.

**Standing for: CCC-smoke REVISED + CCC-1 REVISED + Pythia extraction queue.**
