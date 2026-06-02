# exp_dev hand-off -- research: program execution memory with audited rollback

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on substrate as program-execution audit memory. Algebraic deletion certificate identified as the one axis where substrate is provably superior to event sourcing, blockchain, and Codebat-style hash-chain evidence structures (arXiv:2511.17118). Cheap decisive test pre-registered: T=500 steps at N=4096, retrieval + deletion isolation + intersection query.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, encoding details, pre-reg bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

**Source note:** `notes/research_program_execution_memory_audit_substrate_2026-06-01.md`

---

## Anchor candidates (rank-ordered)

### 1. Execution-trace retrieval below capacity (cheapest decisive test)

- **Anchor pointer:** Research note Section 6 cheap decisive test. Encode T synthetic execution steps as bipolar patterns, store in W, retrieve from partial cues (instruction field only). Measure retrieval accuracy vs T as fraction of M_max.
- **Substrate-product reading:** If accuracy > 0.85 at T = 0.5 * M_max, substrate is viable as a content-addressable index over sampled execution checkpoints. This directly supports the "forensic audit query in O(1) vs O(T) log scan" product narrative for regulated software (21 CFR Part 11, FINRA 17a-4).
- **Tier hint:** CPU smoke; T <= 1000 steps, N = 4096, < 60s wall. Local CPU.
- **Why now:** No empirical anchor exists for execution-trace encoding in substrate. This is the first anchor for a new application domain (compliance-systems). Cheapest entry point.

### 2. Deletion isolation property: delta_W rollback with cross-pattern verification

- **Anchor pointer:** Research note Section 2c, falsifiable predictions HF2. Delete patterns xi_{200}...xi_{220} via exact delta_W subtraction. Verify: (a) deleted-pattern retrieval falls to chance, (b) non-deleted patterns are unaffected (delta_acc < 0.05). This is the "audited rollback" capability claim.
- **Substrate-product reading:** If isolation holds (deleted patterns unrecoverable, non-deleted patterns unaffected), substrate generates a verifiable deletion certificate that is structurally superior to GDPR key-erasure or event-log re-replay. This is the regulatory niche anchor for the product. If HF2 fires (deletion of xi_t corrupts xi_{t+1} by > 20%), the GDPR niche collapses.
- **Tier hint:** CPU; can attach to Anchor 1 as a second test cell in the same script. Zero additional wall time overhead.
- **Why now:** Deletion isolation is the central product claim. One test either validates or falsifies it. This is the binary gate for the execution-log product framing.

### 3. Set-intersection query: multi-attribute cue retrieval

- **Anchor pointer:** Research note Section 4, HARD PASS threshold HP4 (precision > 0.70). Construct compound cue from two attributes (e.g., instruction type + result sign). Query W. Measure precision of returned pattern against ground truth.
- **Substrate-product reading:** If precision > 0.70, substrate enables "what was the system state when instruction I produced result R?" queries in O(1) — directly applicable to autonomous vehicle black-box queries (NHTSA), financial trade decision audits (FINRA), and medical device decision logging (FDA). If precision < 0.50 (MID3 lower bound), queries are not product-grade without ranking/top-k post-processing.
- **Tier hint:** CPU, same synthetic trace as Anchors 1+2. Third test cell, negligible overhead.
- **Why now:** Distinguishes substrate's content-addressable advantage from indexed SQL. The question is whether compound-attribute queries work at all in bipolar AM, not how well they scale. Binary gate, cheap.

---

## Context pointers

- Research note: `notes/research_program_execution_memory_audit_substrate_2026-06-01.md`
- Deletion certificate (TCFT) row: `notes/substrate_capability_map.md` (current state -- TCFT row status)
- ZK-primitive drill (inner-product membership): status log 2026-06-01 (prior research delivery, inner-product as membership query)
- Deletion-counterfactual-semantics drill: status log 2026-06-01 (W-deletion = Pearl do-operator, same algebraic property)
- SEB write-proof floor: status log 2026-06-01 (q_EA retention floor sets reliable retrieval window)
- Codebat competitor: arXiv:2511.17118 (constant-size cryptographic evidence, Nov 2025 -- the industrial benchmark)
- VSA Lisp precedent: arXiv:2511.08767 (execution encoding in HD vector space, established)
- Field advisor: `tools/orchestrator/research_field_advisor.py`

---

## Contract

exp_dev is authorized to:
- Design and queue execution-trace retrieval smoke (Anchor 1) as local CPU anchor
- Attach deletion-isolation test (Anchor 2) as a second cell in the same experiment script
- Attach set-intersection query test (Anchor 3) as a third cell
- Ship all three as a single CPU smoke (one queue entry, three test cells)
- Sequence cheapest first per PROT-004: all three anchors are cheap enough to run together

exp_dev is NOT authorized to:
- Commit cap_map changes (those go to orchestrator after verdict)
- Claim product position without a HARD PASS verdict event through verdict_handler
- Add regulatory-compliance framing to experiment scripts (product implications are for orchestrator/product layer only)

## Autonomy declaration

exp_dev has full autonomy to determine: anchor names, N (suggested 4096 but exp_dev decides), T sweep range, seeds, encoding details (random projection vs hash), pre-reg HP/MID/HF numerical bands, queue assignment, wall_s estimate, and whether to run as single combined smoke or separate anchors. No further approval needed for any anchor in this list.

<!-- routing-completed: Acted-on 2026-06-01: handoff to Round 10 dispatch -->
