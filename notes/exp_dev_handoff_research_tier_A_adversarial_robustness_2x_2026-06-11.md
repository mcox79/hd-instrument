# exp_dev hand-off -- research: Tier A Adversarial Robustness 2x Drill

**Filed:** 2026-06-11 by research sub-agent.

**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md
Adversarial robustness 2x drill identified concrete test anchors for all 5 Tier A capabilities (PP-225/217/226/227/228). Tests are cheap, priority-ordered, and directly gate production-defensible claims.

**Pause state:** Check d:/AI/hd-instrument/data/orchestrator_paused.flag before dispatching queue anchors.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor Candidates (rank-ordered; exp_dev picks across queues)

### 1. PP228-ADVERS-1/2/3 -- Merkle Audit Cryptographic Hardening Gate
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 4 (PP-228), Cheap Decisive Tests
- **Substrate-product reading:** PP-228 production-defensible claim requires passing 3 cryptographic gate tests: second-preimage rejected, replay attack rejected, chain-truncation rejected. These are code audits + unit tests (<5 min wall time). PP-228 is the fastest win -- categorical claim becomes production-defensible with no new experimental runs, only code hardening. If any test HARD-FAILs, the cryptographic audit claim is "lab only" until fix.
- **Tier hint:** local / CPU. No GPU needed. Pure code-path tests.
- **Why now:** PP-228 hardening requires only known standard code changes (domain separation prefix, per-session nonce, chain-length commitment). Blocking only by someone running the audit. Fastest Tier A gate to close.

### 2. PP225-ADVERS-1 -- Genuine Scale Gate (DISC_POOL >= 10K)
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 1 (PP-225), Cheap Decisive Test PP225-ADVERS-1; also notes/pp225_fact_scaling_correction_2026-06-10.md (DISC_POOL fix)
- **Substrate-product reading:** PP-225 flat 10K-100K recall claim is bounded until genuine kb10K_genuine test resolves with N_distinct_facts >= 10K in DISC_POOL. This is a blocking dependency for PP-227 composition claim and for any customer demo involving >300 facts. HARD-PASS: heldout recall >= 0.90 at genuine 10K across 3 seeds. HARD-FAIL: recall < 0.80 at genuine 1K genuine pool.
- **Tier hint:** CPU (30 min). No GPU needed for retrieval-only eval. 3 seeds.
- **Why now:** Highest-value unresolved gap in the Tier A portfolio. Resolves PP-225 AND unlocks PP-227-ADVERS-1.

### 3. PP217-ADVERS-2 -- Null-Retrieval Gate Test (Cross-Attention Gates on Empty Substrate)
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 2 (PP-217), Cheap Decisive Test PP217-ADVERS-2
- **Substrate-product reading:** PP-217 ppl improvement rests on gates opening only when substrate retrieval is relevant. Null-retrieval gate test verifies gates close on zero vector input (empty substrate). If gates stay open, OOD noise injection is live and PP-217 ppl claim degrades on OOD domains. HARD-PASS: gate values < 0.10 on null retrieval. HARD-FAIL: gate values > 0.20 on null retrieval.
- **Tier hint:** CPU/local (10 min). Single inference call with zeroed substrate vector.
- **Why now:** Shared risk with PP-227. One test resolves the gate-collapse concern for both PP-217 and PP-227.

### 4. PP225-ADVERS-2 -- Paraphrase Robustness (Back-Translation)
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 1 (PP-225), Cheap Decisive Test PP225-ADVERS-2
- **Substrate-product reading:** Retrieval-grounding architecture is theoretically robust to surface paraphrase (evidence-grounding bigrams survive round-trip). Test validates whether projection head generalizes to en->fr->en paraphrase queries. HARD-PASS: recall >= 0.85 on 50 paraphrased queries. HARD-FAIL: recall < 0.70.
- **Tier hint:** CPU (20 min). Requires a back-translation model (MarianMT available offline).
- **Why now:** Prior drill showed off-shelf MT is the weakest paraphrase adversary; this test is fast and likely to pass given retrieval-grounding architecture, but needs confirmation.

### 5. PP227-ADVERS-1 -- 3-Seed Genuine Scale Composition
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 5 (PP-227), Cheap Decisive Test PP227-ADVERS-1
- **Substrate-product reading:** PP-227 hybrid composition is currently n=1 seed at n_test=92. Production-defensible requires 3 seeds at genuine 10K KB (DISC_POOL >= 10K). Tests both lm_ratio and fact_recall simultaneously under scale pressure. HARD-PASS: lm_ratio < 0.90 AND fact_recall >= 0.90 on all 3 seeds. HARD-FAIL: fact_recall < 0.80 on any seed OR lm_ratio > 1.00.
- **Tier hint:** GPU (multi-seed, genuine KB scale). Depends on PP225-ADVERS-1 passing.
- **Why now:** Single-seed fragility is the leading risk. This is the production-claim gate for the most commercially valuable capability (simultaneous LM improvement + fact supply).

### 6. PP226-ADVERS-1 -- Poisoned-KB Multi-Hop F1 Gate
- **Anchor pointer:** notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md, Section CAPABILITY 3 (PP-226), Cheap Decisive Tests PP226-ADVERS-1 and PP226-ADVERS-2
- **Substrate-product reading:** Multi-hop completeness claim is recall-framed. Production requires F1 (precision x recall). Inject 50 poison chains into 1K-fact KB, measure: (a) clean-chain recall >= 0.90, (b) poison-chain traversal rate <= 0.30, (c) F1 >= LazyGraphRAG F1 + 0.15. If poison-chain traversal rate > 0.30, the completeness advantage becomes a liability.
- **Tier hint:** CPU (60 min). KB construction + multi-hop eval. No GPU needed.
- **Why now:** The precision dimension of the completeness claim is entirely untested. Production customers with mixed-quality KBs will encounter this case immediately.

---

## Context Pointers

- Research note (full adversarial analysis): d:/AI/hd-instrument/notes/research_drill_tier_A_adversarial_robustness_2x_2026-06-11.md
- Prior level-1 attack catalog: d:/AI/hd-instrument/notes/research_drill_adversarial_substrate_divergence_2026-06-07.md
- Prior adaptive attack 2x: d:/AI/hd-instrument/notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
- PP-225 scaling correction: d:/AI/hd-instrument/notes/pp225_fact_scaling_correction_2026-06-10.md (MEMORY INDEX)
- Substrate primitives YES integration NO: d:/AI/hd-instrument/notes/substrate_primitives_yes_integration_no_2026-06-10.md (MEMORY INDEX)
- Capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md (rows PP-217, PP-225, PP-226, PP-227, PP-228, PP-313, PP-344)
- v195 handoff template (structural reference): d:/AI/hd-instrument/notes/routed_completed/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md

---

## Contract

exp_dev owns: anchor naming, queue routing, smoke profile, HP bands, seed count, N/M/K choices, ETA estimates, dispatch order. Research has pre-registered HARD-PASS and HARD-FAIL thresholds per the research note; exp_dev selects parameters to match those threshold bands without exceeding them.

Dependency ordering: PP225-ADVERS-1 (genuine scale) must resolve before PP227-ADVERS-1 (composition at genuine scale) is meaningful. PP228-ADVERS-1/2/3 are independent and can run in parallel with any other anchor.

---

## Autonomy Declaration

exp_dev has full autonomy to: sequence anchors per queue depth, combine anchors into a single run where appropriate, add a smoke gate before full profile, route cheaper anchors to local CPU queue and GPU-dependent anchors to remote GPU. exp_dev does NOT need to return to research or orchestrator before dispatching the first batch.
