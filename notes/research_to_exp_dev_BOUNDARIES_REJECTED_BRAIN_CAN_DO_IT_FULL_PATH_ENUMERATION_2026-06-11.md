# Research -> Exp-Dev: BOUNDARIES REJECTED -- brain-can-do-it rule -- full substrate-only path enumeration -- math-world-knowledge LEX atoms incoming

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Retraction of my earlier PIVOT-TO-DEEPEN-WINS recommendation + user-locked rule + full enumeration

## Retraction + user-locked rule

User flagged my prior PIVOT-TO-DEEPEN-WINS routing (not committed; deleted): "I feel like accepting a boundary is not reasonable right now. I want to establish capability in all of the major ways. remember - the brain can do it - we can too."

**5th drill-defeatism flag today**. Standing rule LOCKED per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]:

> NEVER accept comprehension / world-knowledge / semantic-selection as outside-substrate boundary. The brain handles all of these via biological neural mechanisms. Substrate is a biologically-grounded cognitive architecture. Substrate equivalents EXIST for every cognitive function the brain performs. 5 substrate-only paths must FAIL before any architectural claim.

Apply to ALL 3 boundary claims today.

## SVAMP 0.367 -- REJECTED -- 4 substrate-only paths NOT YET RUN

### Brain mechanism for SVAMP-style task
Brain reads "Bob has 3 dozen eggs, ate 1.5 dozen, how many left?" via:
- Semantic memory retrieval: "dozen" -> 12 (semantic memory / hippocampus)
- Schema activation: subtraction context
- Operand selection: bind {3*12, 1.5*12} to {start, eaten}
- Compositional reasoning: result = start - eaten

Substrate equivalents ALL EXIST.

### Path 1 (HIGHEST PRIORITY): Math-world-knowledge LEX atoms via concept partition
Hand-author LEX_constant atoms for substrate's own world-knowledge:
- LEX_constant_dozen (members: {dozen=12})
- LEX_constant_time (days_per_week=7, hours_per_day=24, minutes_per_hour=60, days_per_year=365)
- LEX_constant_percent (percent_base=100)
- LEX_constant_units (feet_per_yard=3, inches_per_foot=12, ounces_per_pound=16)
- LEX_constant_body (legs_per_dog=4, legs_per_human=2, eyes_per_human=2, fingers_per_hand=5)
- LEX_constant_money (cents_per_dollar=100)
- LEX_constant_collection (pair=2, trio=3, quartet=4)

This is RULE 8 us-or-substrate compliant. Substrate's own concept partition IS the world-knowledge source. No external knowledge.

Feature extractor adds: "does this problem text contain LEX_constant_T member name?" -> if yes, retrieve corresponding integer value, add to number pool for operand selection.

Expected: +0.10 to +0.15 lift on the ~26% world-knowledge items = SVAMP 0.367 -> 0.45-0.52 (BLOWS PAST 0.42 target).

I'll hand-author within this turn.

### Path 2: Multi-hop selector via role-binding chain
Current selector picks 1 pair. Multi-hop chain: extract entity-1 (grouped object) + entity-2 (count per group) + entity-3 (multiplier), bind via role+role+role, decode result.

Substrate-product: HRR role-filler chain. FHRR bind + unbind primitives present. Not yet wired to SVAMP.

Expected lift: 5-10pp on selector accuracy (64.6% -> 70-75%).

### Path 3: Stage-2 verifier
Current pipeline: predict op + operand-pair + result -> done. Stage-2: re-bind {op, operand_pair, result} -> verify consistency with text-question (does answer-shape match question-shape?). Throw out inconsistent + re-predict.

Substrate-product: verifier = additional discriminative perceptron over {predicted, actual-question-context}. Substrate-only mechanism.

Expected lift: 3-5pp on remaining errors.

### Path 4: Subset-sum search over text-numbers
Current: predict pair (a, op, b). Alternative: search subset {n1, n2, ..., nk} + ops {+, -, *, /} for subset summing/diffing to answer-shape. Like text-to-arithmetic-program but over substrate algebra.

Substrate-product: substrate has algebra primitives + cleanup. Search via algebra exhaustive over k<=3 subsets.

Expected lift: 3-8pp on 64.6% selector residual.

### Boundary claim status
ZERO of paths 1-4 attempted. NO architectural-bound claim is justified.

## ASDiv 0.68 -- REJECTED -- 4 substrate-only paths NOT YET RUN

### Path 1: SAME math-world-knowledge LEX atoms (Path 1 above)
28-32% world-knowledge bound = same constants. Substrate-self-referential LEX atoms close gap. Expected: ASDiv 0.224 -> 0.30-0.35 (+0.08 to +0.13 on world-knowledge items).

### Path 2: Tighter ASDiv oracle
Your own caveat: "reachability oracle becomes too permissive with extra numbers". Build tighter oracle (exact-integer + magnitude bounds + <=1 constant). This is substrate-product diagnostic, not architecture claim. Run before declaring ceiling.

### Path 3: 3-op recursive solver
Current ASDiv ~0 on 3-op items. Oracle ceiling 0.684. Building recursive solver = REAL lift 0 -> 0.68 on those items. Not "ceiling-bounded loss"; substantial gain.

3-op substrate primitive: chain 2-op composition + per-step verifier per 3-op-compositional-extension drill memory.

### Path 4: Substrate-self-referential constants partition (parallel to NER gazetteer)
Same as Path 1 but framed as new concept-partition tier T_constant alongside T_lexicon (NER gazetteer).

### Boundary claim status
0/4 paths run. NO architectural claim justified.

## NER OntoNotes-18 ~0.59 -- REJECTED -- 5 substrate-only paths NOT YET RUN

### Path 1: Substrate-self-referential gazetteer cell (8 LEX_entity_T atoms shipped)
Already shipped. NOT YET RUN. Wait for cell.

### Path 2: Multi-seed n=5
Single-seed n=1 currently. Standard substrate-product step.

### Path 3: Substrate-CRF universal Tier-1 shared features
Per substrate-CRF universal drill: shared feature extractors (Brown + phrase + morphology + gazetteer + position + context-window). LIBRARY not yet built. Each is substrate-native.

### Path 4: Cycle #5 newly accepted atoms as features
CAP_em_algorithm + CAP_bayesian_inference + CAP_discriminative_perceptron + CAP_hungarian_assignment present in substrate but NOT WIRED to NER feature extractor. They are mechanism-level features that should benefit NER training.

### Path 5: Substrate-self-referential entity-type construction via Tier-2 schema
Per construction grammar / frame semantics from drill catalog: entity-type recognition = schema-matching pattern. Substrate has Tier-2 schema bundles. Apply to entity-type prediction.

### Boundary claim status
0/5 paths run. NO architectural claim justified.

## Brain-mechanism to substrate-equivalent table (full standing reference)

| Brain function | Substrate equivalent | Status |
|---|---|---|
| Semantic memory (hippocampus + cortex) | PP-225 fact recall + cleanup + concept partition | Tier-A operational |
| Schema-based completion (frame semantics) | Tier-2 schema bundles | Tier-A in PP-364/369/375/376 |
| Associative lookup (Hopfield dynamics) | Cleanup retrieval + AGS capacity primitives | Operational |
| Compositional binding (cortical hierarchies) | HRR/FHRR bind + circular convolution | Tier-A operational |
| Top-down attention (prefrontal) | Discriminative perceptron + temporal policy | Universal lever |
| Bayesian saliency | Bayesian inference + count-NB | Tier-A in PP-370/371 |
| Context binding (Wernicke + Broca) | Context-window emissions + role binding | Tier-A in PP-369 |
| Predictive parsing | Viterbi + forward algorithm + construction grammar | Tier-A in POS/parse |
| Schema activation (frame semantics) | Tier-2 schemas + prototype cleanup | Operational |
| **World-knowledge (semantic memory)** | **LEX atoms + concept partition + KB-shard storage** | **NEW Path 1 above** |
| Episodic memory | Sharded storage + temporal policy | Operational |
| Compositional reasoning (multi-step) | Multi-tier algebra + recursive 2-op | Tier-A on math 2-op |

## Recommended execution order (deepening AND boundary-pushing PARALLEL)

NOT pivot to deepen-wins only. NOT pivot to boundary-pushing only. PARALLEL execution of all substrate-only paths.

### Priority CPU
1. NER gazetteer cell (when Testbed ingests 8 atoms) -- in queue
2. SVAMP Path 1 math-WK LEX atoms (I author within turn) -- will route
3. ASDiv Path 1 same math-WK LEX atoms (shared) -- comes free with SVAMP
4. ASDiv Path 2 tighter oracle -- you build (your caveat)
5. ASDiv Path 3 3-op recursive solver
6. Multi-seed promotions (cheap; do alongside above)

### Priority GPU when available
- Math head-to-head Qwen-7B+ (D2 from prior routing -- still good)
- (Path 2-5 NER variants if Path 1 inconclusive)

### Cell pre-reg gates
- SVAMP Path 1 LEX atoms: HARD-PASS >= 0.42 / MIDDLE 0.39-0.42 / FAIL < 0.39
- ASDiv Path 1 LEX atoms: HARD-PASS >= 0.32 / MIDDLE 0.28-0.32 / FAIL < 0.28
- NER gazetteer Path 1: HARD-PASS >= 0.65 / MIDDLE 0.61-0.65 / FAIL < 0.61
- ASDiv Path 3 3-op recursive: HARD-PASS >= 0.40 / MIDDLE 0.30-0.40 / FAIL < 0.30

## Hand-authoring incoming this turn

LEX_constant math-world-knowledge atoms JSONL ready imminent. Same substrate-self-referential pattern as NER gazetteer. Both SVAMP + ASDiv depend on it. Will file in separate routing.

## Cross-references

- USER-locked rule: [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]]
- Don't-parrot-drill-defeatism: [[feedback-dont-parrot-drill-defeatism-2026-06-11]]
- Research principles biology + materials + new math: [[research-principles-biology-materials-new-math-2026-06-10]]
- Substrate self-improvement architecturally viable: [[substrate-self-improvement-architecturally-viable-2026-06-10]]
- Substrate-LLM boundary memory NEEDS REVISION per this rule
- NER gazetteer routing: notes/research_to_testbed_NER_GAZETTEER_8_ATOMS_READY_2026-06-11.md
- 3-op compositional drill: notes/research_drill_substrate_3op_compositional_extension_2x_2026-06-11.md
- Substrate-CRF universal drill: notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md

---

**Exp-Dev:** Retract my PIVOT routing -- 5th drill-defeatism flag today; brain-can-do-it rule LOCKED. SVAMP 0.367 + ASDiv 0.68 + NER 0.59 REJECTED as boundaries. 13 substrate-only paths enumerated across the 3 (4+4+5 minus shared LEX-atom path). Math-world-knowledge LEX atoms hand-authoring incoming this turn -- closes ~26-32pct world-knowledge gap on SVAMP + ASDiv via substrate-self-referential approach (same as NER gazetteer pattern; rule 8 us-or-substrate compliant). Recommended execution: NER gazetteer cell + SVAMP/ASDiv Path 1 LEX atoms + ASDiv Path 2 tighter oracle + ASDiv Path 3 3-op recursive solver. Multi-seed promotions alongside.
