# exp_dev hand-off -- research: multiagent coordination substrate

**Filed:** 2026-06-01 by research sub-agent.

**Trigger:** Research delivery on substrate as multi-agent coordination infrastructure -- GO on compliance-sidecar position. Five-property algebraic bundle confirmed absent from all reviewed coordination primitives. Cheap decisive tests identified. See source note: `notes/research_multiagent_coordination_substrate_2026-06-01.md`.

**Pause state:** check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, seeds, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke/FULL profiles. Orchestrator does NOT specify numerical parameters beyond what is structurally required for the question.

---

## Anchor candidates (rank-ordered)

### 1. Commutative write correctness -- 4-agent permutation verification

- **Anchor pointer:** Research note 2026-06-01, Cheap decisive test section. Four agents write distinct HD patterns to a shared W; verify all 24 orderings of write produce identical W and that all 4 patterns are retrievable from each resulting W.
- **Substrate-product reading:** If HP, confirms the "no locks required" claim algebraically (implementation-level, not just mathematically). This is the foundational demo for the agent-HSM product story. Commutative write correctness is required before any multi-agent product framing is used externally. If HF (Frobenius norm difference > 1e-4 across orderings), float32 accumulation order is not numerically neutral and the product claim needs qualification.
- **Tier hint:** Local CPU smoke. Trivial compute: no GPU needed. Standard W += x x^T accumulation. Likely <5 min wall.
- **Why now:** Cheapest and most foundational anchor. Algebraically guaranteed but never explicitly tested as a multi-agent simulation. Needed to move from theory to demonstrated capability.

### 2. Per-agent isolation under concurrent write -- multi-agent zero-leakage

- **Anchor pointer:** Research note 2026-06-01, Cheap decisive test section (second test). Agent A writes p_A to W_A; agent B writes p_B to W_B; verify W_global = W_A + W_B retrieves both p_A and p_B; verify W_A does not retrieve p_B and vice versa. Extension of existing multi-tenancy zero-leakage result, cast in multi-agent framing.
- **Substrate-product reading:** If HP (cross-agent cosine < 0.05 at p99), the per-agent isolation claim is verified in the blackboard framing. This directly supports the compliance-sidecar product story: each agent's writes are algebraically separated. If HF (cross-agent cosine > 0.15), the operating envelope is narrower than multi-tenancy results suggest -- needs characterization before product framing.
- **Tier hint:** Local CPU smoke, ridable with Anchor 1. Same experiment infrastructure.
- **Why now:** Second cheapest. Already supported by multi-tenancy results but the multi-agent framing (two agents writing to a shared-plus-isolated W simultaneously) has not been explicitly exercised.

### 3. Deletion persistence under multi-agent write pressure

- **Anchor pointer:** Research note 2026-06-01, HARD PASS/FAIL section HP3/HF3. After agent A deletes pattern p (algebraic deletion + active repulsion), 10 subsequent writes by agent B of random patterns must not cause p to reemerge. Key differentiator vs. CRDTs (which cannot delete by construction) and Redis TTL (probabilistic, no certificate).
- **Substrate-product reading:** If HP (p cosine < 0.10 after active repulsion + 10 random rewrites), this is the hardest coordination property to replicate anywhere, and it validates the deletion-certificate claim in the multi-agent adversarial setting. If HF (p cosine > 0.20), the active repulsion force is insufficient against multi-agent write pressure -- this is a qualitatively new failure mode not tested in single-agent deletion experiments.
- **Tier hint:** Local CPU, slightly heavier than Anchor 1+2. May warrant 5-seed sweep to characterize stochastic behavior. Still sub-GPU.
- **Why now:** The deletion-certificate row (PP-9) is a shared primitive across 5 product stories; testing it under multi-agent adversarial pressure closes the most important open question for the compliance-sidecar product framing.

---

## Context pointers

- Source research note: `notes/research_multiagent_coordination_substrate_2026-06-01.md`
- Multi-tenancy zero-leakage prior results: cap_map rows PP-14, PP-15; existing multi-tenancy experiments in dashboard
- Deletion certificate row: PP-9; also feeds PP-24, PP-22, PP-25, PP-20 per cap_map DELETION CERTIFICATE SHARED PRIMITIVE section
- Spectral AI introspection drill (correlated-write Z-statistic): `notes/exp_dev_handoff_research_spectral_ai_introspection_2026-06-01.md`
- CRDT comparison: arXiv:1805.06358; substrate additive structure is join-semilattice over PSD cone
- Missing primitives survey: arXiv:2603.10062 (names exactly substrate's five properties as absent from current frameworks)
- Product narrative v315: cap_map `notes/substrate_capability_map.md` PRIMARY PRODUCT NARRATIVE section
- Field advisor: `tools/orchestrator/research_field_advisor.py` (next-drill: network-science/graph-theory Tier-1b)

---

## Contract

exp_dev is authorized to:
- Design and queue Anchor 1 (commutative write permutation) as a local CPU smoke anchor
- Design and queue Anchor 2 (per-agent isolation) riding the same experiment as Anchor 1
- Design and queue Anchor 3 (deletion persistence under write pressure) as a separate local CPU anchor
- Sequence as: Anchor 1+2 combined (same infrastructure), then Anchor 3 as follow-on
- Promote to remote CPU if seed sweeps require >30 min wall

exp_dev is NOT authorized to:
- Modify cap_map rows without orchestrator approval
- Pre-specify HP/MID/HF numerical bounds (exp_dev derives from research note predictions + formula-selftests)
- Frame results as "multi-agent product demo" -- frame as capability characterization only

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]]: all anchor specifications (N, M, K, seeds, thresholds, queue routing, anchor names, ETAs) are exp_dev's design decisions. This hand-off provides the WHAT and WHY; exp_dev provides the HOW.

<!-- routing-completed: Acted-on 2026-06-01: handoff absorbed into exp_dev Round 10 dispatch; multiagent_coord_full_v3 also ran v324 reclassification -->
