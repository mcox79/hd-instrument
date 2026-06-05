# exp_dev hand-off -- research: cf rank-1 substitution as substrate-native RPE (2x depth)

**Filed-by**: research sub-agent, 2026-06-04
**Trigger**: notes/research_drill_cf_rank1_as_substrate_native_rpe_2x_2026-06-04.md -- algebraic chain complete; rank-1 cf substitution IS a TD-style conditional-probability signal; rung-1 probe spec ready with pre-registered HP/MID/HF.

**Pause state**: check data/orchestrator_paused.flag before dispatching. Do not ship if flag present.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep parameters, threshold formulas, queue routing, and pre-reg bands.

---

## Anchor candidates (rank-ordered)

### 1. cf-RPE three-factor vs pure Hebbian bigram retrieval (HIGHEST PRIORITY -- CPU, <60s)

**What**: bipolar associative memory (N=512, M=64 patterns) trained on bigram statistics
from a 10k character corpus. Two learning rules: (a) pure Hebbian outer-product, (b) cf-RPE
three-factor dW = cf_RPE * v_prime * u^T - cf_RPE * v_old * u^T. Measure retrieval accuracy
P(correct next-token | context) on held-out 1k chars. Stale-cache variant: compare retrieval-
time v_hat vs stored-time v_old as the cached prediction.

**Why**: this is the cheapest falsification for the conditional-probability convergence claim.
P_deflated = 0.44 for cf-RPE beating Hebbian on HARD-PASS threshold. If cf-RPE does not
outperform Hebbian on bigrams (simplest conditional structure), the mechanism fails at rung 1.
HARD-PASS: cf-RPE > Hebbian + 15pp accuracy. HARD-FAIL: cf-RPE <= Hebbian accuracy.

**Tier hint**: CPU local, <60s wall. Laptop queue. Zero cloud cost.

**Cap_map pointer**: if HARD-PASS, opens new row for "substrate-native supervised training
via cf-RPE" -- directly de-risks Bet B (Hebbian-trained VSA-LM) theoretical foundation.

**Substrate-product reading**: HARD-PASS means the substrate has a native training signal
that does not require backprop. This enables on-device continual learning with no external
optimizer -- a capability that no current LLM substrate offers.

---

### 2. Stale-cache failure mode quantification (secondary, rides same run)

**What**: same as anchor 1 but systematically vary cache staleness: compare (a) v_old =
retrieved at cf event time, (b) v_old = stored at write time (no re-retrieval), (c) v_old =
noisy cached version (simulate drift). Measure accuracy degradation as staleness increases.

**Why**: FM-1 (stale cache) was identified as the highest-severity failure mode (HIGH).
Quantifying the staleness threshold guides the product engineering requirement: how frequently
must the cache be refreshed for cf-RPE to remain effective?

**Tier hint**: CPU local, <120s wall. Can run in same session as anchor 1.

---

### 3. Joint architecture: Hebbian * cf-RPE multiplicative gating (follow-on, after anchor 1)

**What**: test the unified rule dW = eta * (v * u^T) * cf_RPE_magnitude. Compare against
pure Hebbian, cf-RPE additive (not multiplicative), and cf-RPE three-factor (anchor 1).
Metric: bigram retrieval accuracy + convergence speed (epochs to 80% accuracy).

**Why**: tests whether multiplicative gating strictly improves over additive cf-RPE and
whether the joint architecture dissolves all three META-drill constraints simultaneously.
P_deflated = 0.30 for HARD-PASS. Gate on anchor 1 HARD-PASS or MID.

**Tier hint**: CPU local. Medium wall (~5-10 min, multiple seeds). Laptop queue.

---

### 4. Multi-step TD(lambda) eligibility trace for cf-RPE (follow-on, after anchor 3)

**What**: extend cf-RPE to multi-step error propagation via eligibility traces spanning
k pattern-hop steps. Compare k=1 (current cf-RPE) vs k=2,3 on a chain-retrieval task
(u -> v -> w, predict w from u). Measure whether k>1 traces improve multi-hop accuracy.

**Why**: FM-2 (multi-step error propagation) is the second-highest severity failure mode.
Eligibility trace design is the proposed mitigation. This probe quantifies the gain from
multi-step traces and the optimal lambda for the substrate.

**Tier hint**: CPU or remote CPU. 10-30 min wall. Gate on anchor 3 passing.

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_cf_rank1_as_substrate_native_rpe_2x_2026-06-04.md
- Prior related handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_counterfactual_rpe_training_2026-06-03.md
- Prior related handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_llm_training_2026-06-03.md
- Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md

---

## Contract

- Anchor 1 is the decisive test. Do not skip or combine with anchor 3 before anchor 1 runs.
- Failure modes FM-1 and FM-4 (stale cache, capacity saturation) must be verified as separate
  conditions in anchor 1+2, not assumed away.
- If anchor 1 HARD-FAILs, file a rescue note before dispatching anchor 3 or 4.
- Per [[feedback-per-experiment-timeout-required]]: include --timeout computed from smoke wall.
- Per [[feedback-ascii-only-in-scripts]]: no emoji or em-dash in verdict_msg.
- Per [[feedback-no-label-vs-honest-anchor-names]]: _n<N> suffix convention for N-binding.

## Autonomy declaration

exp_dev owns: anchor names, sweep grids, exact threshold formulas, pre-reg HP/MID/HF
numerical bands, queue routing (laptop/CPU/GPU), ETA estimates, cap_map annotation decisions.
The research agent has provided the algebraic argument and failure-mode analysis. exp_dev
interprets, designs the probe, and ships.
