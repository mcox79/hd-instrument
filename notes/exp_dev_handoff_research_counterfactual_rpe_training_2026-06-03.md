# exp_dev hand-off -- research: counterfactual associative memory as dopamine RPE training channel

**Filed-by**: research sub-agent, 2026-06-03
**Trigger**: notes/research_drill_counterfactual_dopamine_rpe_training_channel_2026-06-03.md — CPE-as-RPE algebraic grounding complete; minimum viable probe spec ready.

**Pause state**: check data/orchestrator_paused.flag before dispatching. Do not ship if flag present.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep parameters, threshold formulas, queue routing, and pre-reg bands.

---

## Anchor candidates (rank-ordered)

### 1. CPE-attribution correlation probe (HIGHEST PRIORITY — CPU, <10 min)

**What**: train a small transformer LM (~1M params) on a synthetic corpus with known per-example influence structure (5 influence groups, 100 examples each). Attach an associative memory substrate post-hoc. Compute counterfactual prediction error (CPE) per training example via rank-1 weight substitution. Measure Spearman rho between CPE ranking and ground-truth influence-group ranking.

**Why**: this is the minimum viable falsification test for the counterfactual-as-RPE credit-assignment mechanism. P_deflated=0.38. rho > 0.80 = HARD-PASS; rho < 0.30 = HARD-FAIL. Result closes or opens a new cap_map row for substrate-native data attribution.

**Tier hint**: CPU local, <10 min wall. Zero cloud cost. Should run in laptop queue.

**Cap_map pointer**: opens new row for "substrate-native training-signal channel (CPE-as-RPE)" — currently no row exists; HARD-PASS would warrant a new 🔬 row.

**Substrate-product reading**: if CPE correlates with ground-truth influence (rho > 0.5), the substrate exposes a data attribution API that is 10-100x cheaper than TracIn (no per-example backward passes). Directly supports the Audit+Compliance killer-feature narrative.

---

### 2. CPE-vs-TracIn compute cost comparison (secondary, can ride same run as anchor 1)

**What**: on the same synthetic corpus used in anchor 1, run TracIn (gradient-dot attribution) as a baseline. Record wall time for CPE (K AM forward passes) vs. TracIn (K gradient computations). Compute rho for both. Compare accuracy + cost.

**Why**: demonstrates the compute advantage of the CPE pathway vs. the current best alternative. This is the product-differentiation data point.

**Tier hint**: CPU local. Runs alongside anchor 1 with negligible extra cost.

---

### 3. CPE-driven curriculum controller (follow-on, after anchor 1 HARD-PASS)

**What**: train a small LM on a structured corpus with high-CPE examples presented at higher frequency in early training. Compare final loss against random curriculum and loss-magnitude curriculum. Measure whether CPE curriculum accelerates convergence.

**Why**: tests the curriculum-via-counterfactual-difficulty capability gain. Separate question from attribution correlation — this probes whether CPE is a useful active training signal, not just a post-hoc attribution tool.

**Tier hint**: CPU or remote CPU. Medium wall (~30-60 min). Gate on anchor 1 HARD-PASS.

---

## Context pointers (file paths, not summaries)

- Research note: d:/AI/hd-instrument/notes/research_drill_counterfactual_dopamine_rpe_training_channel_2026-06-03.md
- Substrate-LLM integration context: d:/AI/hd-instrument/notes/research_substrate_llm_deep_integration_v1_2026-05-31.md
- Substrate killer features: d:/AI/hd-instrument/memory/project_substrate_killer_features_2026-05-26.md (Audit+Compliance narrative)
- Cap_map current state: d:/AI/hd-instrument/data/substrate_capability_map.md

---

## Contract

exp_dev designs all anchor specs with pre-reg per envelope-fail-bands. No inline sweep grids, no pre-committed cap_map decisions, no fixed threshold formulas in this file. Dispatch via queue_add.sh with per-experiment --timeout. Post-ship REMOTE VERIFY required.

## Autonomy declaration

exp_dev decides: anchor naming, exact N/d_model/K sweep values, whether anchors 1+2 combine into one queue entry, pre-reg HP/MID/HF numerical bounds, queue routing (CPU local vs. remote CPU vs. GPU), and sequencing of anchor 3 relative to anchor 1 result.
