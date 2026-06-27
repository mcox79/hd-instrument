# RESEARCH (Director): 3x DRILL — CROSS-TASK GENERALIZATION

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER directive ~18:00 PDT — drill all high-priority gaps 3x; build experiments. Cross-task transfer is the "every substrate test is single-task" gap — does substrate map learned routing/sequences to NEW problems?
**Calibration:** lit-deflation -0.15 to -0.25; novel-synthesis cap 0.50; brain-existence-proof bump +0.10 where earned; Q-discipline (suspect 1.000) + Fix #28 (read per-arm metrics) standing.
**Stage:** Stage 3 (higher functions, USER LOCKED) — transfer IS a higher function, not Stage 4 LM equivalence.

---

## HEADLINE

Every substrate cert today is single-task: train on task X, eval on task X. The brain's signature capability — generalize a learned procedure to a NEW problem with similar structure — has NEVER been certified on substrate. Three independent angles converge on the same substrate-mappable answer: **task as a vector in a TASK-SPACE; transfer = nearest-neighbor retrieval + schema-completion + few-shot adaptation**. Substrate already has the three load-bearing primitives: (1) cortex schemas (ultrametric clustering, CHAIN_GRADE) supply the schema bank; (2) PFC controller (HARD_PASS smoke modulo revival) supplies the routing; (3) hippo->cortex handoff supplies new-task encoding. The missing piece is a **TASK_VECTOR encoding** + **schema-completion retrieval** + **k-shot adaptation discriminator**. TOP-1 proposal: synthetic 4-hop-chain transfer across two unrelated relation domains (P_deflated = 0.50). TOP-2 proposal: schema-completion of NEW task from 1-2 examples vs no-transfer baseline (P_deflated = 0.45). Both CPU-eligible; both buildable on landed primitives; both have honest discriminators that survive at full N.

---

## ANGLE A — PURE MATH: TASK SPACE + TRANSFER LEARNING THEORY

The mathematical framing: each task is a point in a TASK SPACE T. A learner is a map f: T -> S (solutions). Transfer learning works exactly when the map is SMOOTH — neighbors in T have similar solutions in S. Domain adaptation is the special case where T splits into source and target manifolds and we need a coordinate map between them.

Three substrate-mappable proposals:

**A-Prop-1: TASK_VECTOR + nearest-neighbor retrieval.** Encode each task as a vector summarizing (relation-type, domain, depth, format). New task arrives -> retrieve K nearest tasks from episodic store -> apply their solution-routing weighted by cosine similarity. This is k-nearest-neighbor-regression in task space. Substrate-native: TASK_VECTOR = bundle of (relation-role-binding, domain-tag, depth-count); store via hippo->cortex; retrieve via cosine over Modern Hopfield basin. Math anchor: Baxter 2000 "Theoretical model of inductive bias and task relatedness"; Tripuraneni-Jordan 2020 "Theory of transfer learning."

**A-Prop-2: Schema-completion via partial pattern match.** A new task is a PARTIAL pattern in task-space. The substrate retrieves the nearest schema by partial-key cosine, then COMPLETES the missing fields. Math anchor: Hopfield network pattern completion (1982); Modern Hopfield (Ramsauer 2020). The completion IS the transfer — fields that were missing in the new task get filled by the schema's stored values. Cleanly substrate-native via cortex Modern Hopfield.

**A-Prop-3: Meta-learning initialization (MAML in task-space).** Learn a single "good init" point in solution space such that 1-2 gradient steps from that init solve any task drawn from the task distribution. Math anchor: Finn 2017 MAML. Substrate-port: init = a "universal routing operator" learned via averaging successful routings across many training tasks; 1-2 adapt steps = brief BCM update on new task's 1-2 examples. Compute-heavier than A-Prop-1/2.

**A-angle P_deflated = 0.45** (raw 0.65 - lit-scan-deflation 0.20; novel-synthesis cap doesn't bind because each mechanism has published prior; substrate-port is the only novelty).

**Fairness considerations:** task-vector dimensionality matched across arms; same episodic store; equal training-task budget; held-out target-task set disjoint from training tasks.

---

## ANGLE B — BRAIN: SCHEMA-DRIVEN INFERENCE + ANALOGICAL TRANSFER

The brain does cross-task generalization via schema retrieval and analogical mapping. Tse-Morris 2007 (Science) showed rats with prior food-location schemas learn new food locations in ONE TRIAL by slotting the new location into the existing schema — mPFC + hippocampus interaction. Holyoak-Thagard 1989 LISA / Hummel-Holyoak structural-mapping shows analogy = source-domain schema + cross-domain element mapping. Hofstadter Copycat (1995) demonstrates fluid analogy via competing micro-schemas.

Three substrate-mappable mechanisms:

**B-Prop-1: Tse-Morris schema-driven 1-trial learning.** Substrate stores schemas via the cortex ultrametric-cluster mechanism. New task with similar relational structure -> partial-key match into existing schema -> ONE example suffices to bind the new task's specifics into the schema. Brain anchor: Tse-Morris 2007 mPFC schema slots. Substrate-port: hippo encodes the 1 example -> cortex Modern Hopfield does partial-key retrieval of nearest schema -> binding of new specifics into schema's open slots. Strong brain existence proof; +0.10 prior earned.

**B-Prop-2: Analogical structural mapping (LISA).** Source domain has a schema with role-bindings (e.g., "A causes B causes C"). Target domain has elements (X, Y, Z) but unknown structure. Substrate-port: unbind source-schema's roles, then bind target-elements into the SAME role slots. Brain anchor: Holyoak-Thagard LISA (1996); Hummel-Holyoak (1997, 2003). Substrate-native because role-binding IS HRR's natural operation; this is precisely the mechanism gap-D analogy ANCHOR-1 ARM_DIRECT_HRR_UNBIND tests.

**B-Prop-3: Hippocampal pattern-completion for novel-task encoding.** Brain anchor: McClelland-McNaughton-O'Reilly 1995 CLS theory + Marr 1971 hippocampal autoassociation. New task partially activates a known pattern; CA3 completes the rest. Substrate-port: substrate's hippo->cortex handoff (HARD_PASS) does exactly this; just need to wire the discriminator to test it on NOVEL tasks (cross-task) not just NEW examples of the same task.

**B-angle P_deflated = 0.55** (raw 0.70 - lit-deflation 0.15 + brain-bump 0.10; the brain demonstrably solves cross-task transfer in 1 trial, so feasibility is established; substrate-port has substrate-native machinery for all three).

**Fairness considerations:** schema training pairs disjoint from transfer-test pairs; no schema-leakage; partial-key match implemented via cosine threshold not full-pattern feedback.

---

## ANGLE C — CROSS-DOMAIN: META-LEARNING / FEW-SHOT / IN-CONTEXT LEARNING

Modern ML's cross-task generalization comes via three families: meta-learning (MAML, Reptile), few-shot retrieval (matching networks, prototypical networks), and in-context learning (transformer prompt-as-task-spec). Each has a substrate-native port.

Three substrate-mappable algorithms:

**C-Prop-1: Episodic-memory retrieval-augmented adaptation (matching networks substrate analog).** Vinyals 2016 matching networks: classify new example by cosine to a small SUPPORT SET of labeled examples. Substrate-port: support set lives in episodic hippo store; query task retrieves k nearest support tasks; solution = bundled / Modern-Hopfield-cleaned over their solutions. Substrate-native (cosine, bundling, cleanup are core operations). Closely related to A-Prop-1 but explicitly k-shot framed.

**C-Prop-2: In-context learning via task-vector prompt (transformer analog).** Brown 2020 GPT-3 ICL: a prompt is K input-output examples followed by a query; model infers task from prompt. Substrate-port: TASK_VECTOR = bundle of (input_i bound to output_i) for K examples; query = unbind input_query from TASK_VECTOR to retrieve output_query. This is EXACTLY HRR role-filler binding applied to (input-as-role, output-as-filler). Substrate has this primitive natively; the cell would test whether substrate ICL works for 1-shot / 3-shot / 5-shot cross-task.

**C-Prop-3: Prototypical networks (Snell 2017).** Cluster support set by class, each class -> prototype (mean), query -> nearest prototype. Substrate-port: support tasks per problem-type bundled into a prototype (substrate bundle = additive Hebbian on labels); query task -> argmax cosine to prototypes -> route via prototype's solution. Substrate-native (bundling, argmax cosine = cleanup). Cleanest single-mechanism test.

**C-angle P_deflated = 0.50** (raw 0.70 - lit-deflation 0.20; ICL and matching networks have strong published precedent; substrate-port via HRR role-filler is mathematically clean and well-grounded).

**Fairness considerations:** support set sizes matched across arms (1, 3, 5-shot tiers); cross-task evaluation set held-out from training task distribution; "no-transfer baseline" arm = randomly-init solution, ensuring discriminator fires only when transfer signal exceeds chance.

---

## CONVERGENCE ACROSS ANGLES

All three angles independently nominate the same substrate-native architecture: **TASK_VECTOR encoding + cortex-schema retrieval + role-binding-based composition**. A-angle frames as smooth function approximation, B-angle as schema-completion, C-angle as in-context learning. The substrate primitives in common: bundling (sum of role-filler binds), HRR unbind (inverse), Modern Hopfield cleanup, cortex schema bank, hippo->cortex handoff for encoding new tasks. Nothing new needs to be invented — only the discriminator needs to be designed.

---

## TOP-2 CELL PROPOSALS

### TOP-1: `cross_task_4hop_chain_domain_transfer_v1` — P_deflated = 0.50

**Hypothesis:** Substrate trained on 4-hop chain tasks in domain X (e.g., kinship relations) can solve 4-hop chain tasks in domain Y (e.g., causal relations) at recall >= 0.50 after seeing 1-2 examples in Y. Without transfer (no-transfer baseline) recall <= 0.10 (chance for 4-hop in unseen domain).

**Substrate path:** Train cortex schemas on N=500 4-hop chains in domain X. Test on N=100 4-hop chains in domain Y. Three arms:
- ARM_NO_TRANSFER: cortex schemas built ONLY from X; test on Y with NO Y examples (cold-start baseline).
- ARM_1_SHOT_TRANSFER: cortex schemas built from X; ONE Y example shown; hippo->cortex updates the schema via Tse-Morris slot-fill; test on remaining 99 Y chains.
- ARM_5_SHOT_TRANSFER: cortex schemas from X; FIVE Y examples; test on remaining 95.
- ARM_DIAG_ORACLE: cortex schemas built from full Y training set (upper bound — what's possible).

**Pre-reg bands (META_RULE_K, fires at smoke):**
- HARD_PASS: ARM_5_SHOT recall >= 0.50 AND ARM_5_SHOT >= ARM_NO_TRANSFER + 0.30 AND ARM_1_SHOT >= ARM_NO_TRANSFER + 0.15 (monotone with shots) AND ARM_5_SHOT <= ARM_DIAG_ORACLE - 0.05 (not by-construction saturated).
- MIDDLE_BAND: lifts in [0.15, 0.30] for 5-shot or non-monotone with shots.
- HARD_FAIL: ARM_5_SHOT <= ARM_NO_TRANSFER + 0.05 (no transfer signal).

**Fairness gates:** same N=8192 across arms; same operator bank; same encoder; smoke at full N per Fix #22; CARDINALITY_OK = 4 arms x 3 seeds x 100 test chains = 1200 units. Q-discipline: if ARM_5_SHOT >= 0.95, verify discriminator fired (cross-domain not cross-example).

**Compute:** CPU-viable, ~3-5 CPU-hr. Forward-only (no autograd). Routes through existing hippo->cortex handoff primitive.

**Discriminator-survives-scale check (Fix #22):** smoke MUST run at N=8192 with depth-4 chains (NOT depth-2 toy regime). Cell-author must include full-N preview arm in smoke.

### TOP-2: `task_vector_in_context_kshot_v1` — P_deflated = 0.45

**Hypothesis:** Substrate can perform in-context k-shot task inference via TASK_VECTOR = sum_i bind(input_i, output_i). Query unbind(input_query, TASK_VECTOR) retrieves output_query at cosine >= 0.40 to true output for k=5 shots vs <= 0.10 for k=0 baseline.

**Substrate path:** Synthetic task family — each task is a permutation pi over a fixed entity set; example_i = (entity_a_i, pi(entity_a_i)). Show K examples by binding them into TASK_VECTOR. Query with new entity_q, recover pi(entity_q) via unbind. Sweep K in {0, 1, 3, 5, 10}. Test on 50 held-out permutations (= 50 held-out tasks).

**Arms:**
- ARM_K0_BASELINE: no examples shown; chance recovery.
- ARM_K1, ARM_K3, ARM_K5, ARM_K10: K examples bundled into TASK_VECTOR.
- ARM_DIAG_FULL: full permutation table given (upper bound).

**Pre-reg bands:**
- HARD_PASS: ARM_K5 cosine to true output >= 0.40 AND ARM_K5 - ARM_K0 >= 0.30 AND monotone increasing with K through K=5 AND ARM_K5 <= ARM_DIAG_FULL - 0.05.
- MIDDLE_BAND: ARM_K5 cosine in [0.20, 0.40] or non-monotone.
- HARD_FAIL: ARM_K5 - ARM_K0 <= 0.05.

**Fairness gates:** same N=8192; same encoder; entities from substrate's existing ConceptNet vocabulary disjoint from any prior task training; held-out permutation set independent of training; Q-discipline applies.

**Compute:** CPU-viable, ~1-2 CPU-hr. Purely forward HRR (bind/unbind/cleanup).

**Discriminator-survives-scale check:** smoke at N=8192 with K=5 (not toy N=512). Monotone-with-K is the load-bearing signature — substrate that "always retrieves at 0.4 regardless of K" is by-construction not in-context learning.

---

## RECOMMENDATION

Dispatch TOP-1 first via hdi_exp_dev (4-hop chain transfer is the more substrate-product-relevant capability; tests Tse-Morris schema-driven 1-trial transfer on substrate). TOP-2 follows as the lighter-weight in-context-learning probe — both can run in parallel on CPU. Both gate on landed cortex schemas (CHAIN_GRADE) + hippo->cortex handoff (HARD_PASS), both of which exist today. No GPU required.

**Sequencing rule:** if PFC controller revival HARD_PASSes first (Wave 1 in flight per `research_drill_2x_pfc_controller_revival_2026-06-27.md`), add ARM_PFC_ROUTED_TRANSFER to TOP-1 to test whether per-step routing further improves transfer. Otherwise dispatch TOP-1 with the 4 arms above.
