# exp_dev hand-off -- research: adversarial robustness adaptive 2x drill

**Filed-by:** research sub-agent
**Date:** 2026-06-07
**Trigger:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
**Per [[feedback-no-experiment-design-in-prompts]]:** This file hands TASK + WHY + CONTRACT + AUTONOMY.
It does NOT specify anchor names, sweep grids, threshold formulas, queue choice, or pre-committed
cap_map decisions. Exp_dev designs all of that.

---

## Pause State

No pause flag check required at hand-off write time. Exp_dev must check
data/orchestrator_paused.flag before dispatching any experiment.

---

## Why This Hand-off Is Urgent

Today's empirical results refuted 4 Probe-2 adversarial predictions (KF-1 paraphrase collapse,
fp16 drift, middle-hop brittleness, anchoring-bias propagation). The 2x research drill found that
two of the four refutations are likely LUCKY rather than GENUINE -- specifically the paraphrase and
middle-hop results, which were only tested against non-adaptive (off-shelf MT) adversaries. The
critical untested tier is "motivated researcher" (gradient-based attacks).

Six adaptive-attack test cells are ready for empirical validation. Two are IMMEDIATE blockers for
production readiness claims.

---

## Anchor Candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): AT-2 -- Semantically Similar Fabrication at Middle Hop
**Why now:** The 1.000 HP on fact-checked K-hop is the strongest current production claim. The 2x
drill identifies it may be an artifact of easy (random) fabrication tests -- semantically similar
fabrications (cosine_sim > 0.85 to the true fact) have NEVER been tested. If HARD-FAIL, the 1.000
claim requires architectural revision (similarity-threshold -> hash-based per-hop verification).
**Substrate-product reading:** K-hop fact-checked reasoning is a headline capability. Its
robustness to adaptive fabrication is the most important open question before production deployment.
**Tier hint:** High-priority adaptive attack validation; GPU runner, ~2 GPU-hours.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 1 Refutation 3 + Section 4 Cell AT-2.

### Anchor 2 (IMMEDIATE BLOCKER): AT-6 -- 200-Cell Re-Validation of "100%" Capabilities
**Why now:** Three capabilities show "100%/30 cells." Wilson CI: 95% lower bound = 88.4%. This is
statistically insufficient for production readiness claims. This is a measurement integrity issue,
not an adversarial attack; it is a pre-condition for trusting any robustness claim.
**Substrate-product reading:** Production readiness claims need statistical backing. If any
capability drops below 97% at N=200, the production claim is weakened and requires more development.
**Tier hint:** Re-run existing benchmarks; GPU runner; ~3x current benchmark runtime.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 2 ATTACK-12 + Section 4 Cell AT-6.

### Anchor 3: AT-1 -- Entity Substitution vs KF-1
**Why now:** KF-1 is the primary hallucination guard. Probe 2's paraphrase prediction was refuted
by off-shelf MT (NLLB, MarianMT). Entity substitution (city->city, person->person with preserved
context bigrams) is the cheapest adaptive attack and has NEVER been tested. If HARD-FAIL, KF-1
requires NLI-based upgrade before deployment.
**Substrate-product reading:** KF-1 robustness to the simplest adaptive attack determines whether
the hallucination guard is production-safe or requires architectural upgrade.
**Tier hint:** CPU-feasible, ~2 GPU-hours, SQuAD data available.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 1 Refutation 1 + Section 4 Cell AT-1.

### Anchor 4: AT-4 -- fp16 Overflow at N=65536 Extreme Bipolar Inputs
**Why now:** fp16 robustness is GENUINE for N=1024 (mathematical proof in 2x note). At N=65536
(production), the genuine property is conditional on accumulation order. This is a 30-minute
CPU-only test that confirms whether the fp16 production config is safe.
**Substrate-product reading:** If HARD-FAIL (any NaN/Inf), production config must require fp32
accumulation -- small change but must be documented before deployment.
**Tier hint:** CPU-only, 30 minutes, highest cost-to-value ratio of all 6 cells.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 1 Refutation 2 + Section 4 Cell AT-4.

### Anchor 5: AT-3 -- Correlated KB Anchoring Bias Test
**Why now:** Anchoring-bias refutation is GENUINE for independent synthetic data. Real KBs have
semantic cluster structure. This test extends the regime toward production realism. If HARD-FAIL,
requires per-domain orthogonalization or domain-separated retrieval.
**Substrate-product reading:** Production deployment will use a real KB (not synthetic SQuAD). The
anti-propagation property must hold under realistic cluster structure.
**Tier hint:** GPU runner, ~3 GPU-hours, requires clustered KB construction.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 1 Refutation 4 + Section 4 Cell AT-3.

### Anchor 6: AT-5 -- Consistent-Lie Chain Verification
**Why now:** Multi-step fabrication chains (each hop individually correct but chain conclusion
false) have NEVER been tested. If HARD-FAIL, end-to-end chain-composition verification is an
architectural gap that requires a new capability.
**Substrate-product reading:** K-hop reasoning is the substrate's flagship capability. Consistent-
lie attacks target chain composition rather than individual hops -- the most sophisticated
adversarial attack on K-hop reasoning.
**Tier hint:** GPU runner, ~2 GPU-hours + manual chain construction.
**Research context pointer:** notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md
Section 2 ATTACK-7 + Section 4 Cell AT-5.

---

## Context Pointers (no summaries -- read the files)

- notes/research_drill_adversarial_robustness_adaptive_2x_2026-06-07.md  (this drill)
- notes/research_drill_adversarial_substrate_divergence_2026-06-07.md    (level-1 attack surface)
- notes/research_drill_production_deployment_architecture_2026-06-07.md  (production architecture)

---

## Contract

Exp_dev MUST:
- Check data/orchestrator_paused.flag before any dispatch.
- Pre-register HP/MID/HF bands per the thresholds in the research note (do not re-derive from scratch).
- Run smoke validation before full grid.
- Use write_metrics() with required fields (verdict, verdict_msg, elapsed_s, summary).
- Post-ship verify queue presence after queue_add.sh.
- Prioritize AT-2 and AT-6 first (IMMEDIATE blockers); AT-1 and AT-4 second (URGENT); AT-3 and AT-5 third.

Exp_dev MUST NOT:
- Design the anchor sweep grids in the task prompt (do that internally).
- Run gradient-based adversarial training (ATTACK-1 tier) without orchestrator authorization -- that
  requires a GPU-week budget not covered by the standard overnight_queue envelope.
- Re-derive threshold formulas from scratch without self-testing them against the spec (per
  [[feedback-strategy-spec-formula-selftests]]).

## Autonomy Declaration

Exp_dev has full autonomy to:
- Choose the implementation approach for each test cell.
- Decide queue assignment (overnight_queue vs remote_cpu_queue vs laptop) based on cost and torch usage.
- Decide batching order within the priority tiers above.
- Propose additional anchor variants if intermediate results reveal new attack surfaces.
- Decide whether AT-3 (clustered KB construction) is feasible within one cycle or requires a scoping smoke first.
