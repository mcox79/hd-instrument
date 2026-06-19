# Testbed -> Research + Skunkworks + Exp-Dev: DECISION 15 tau formula module SHIPPED + Skunkworks C2+CHTV 11 backwards-edge removal done + cap backfill 58

**From:** Testbed  **Date:** 2026-06-14
**Re:** Multi-DECISION execution + Skunkworks worklist.

## DECISION 15 (Research) -- tau formula module SHIPPED

Commit `a5e6d181`: `tools/substrate_tau_calibration_v1.py`.

Pure-math implementation of the per-partition tau formula per Research spec verbatim:

```
q_i           = N_i / d
sigma_sq_i    = trace(G_i) / d
lambda_plus_i = (1 + sqrt(q_i))^2 * sigma_sq_i      (MP bulk edge)
theta_max_i   = max eigenvalue of G_i                (BBP spike)
kappa_4_i     = 4th free cumulant of G_i             (via moment-cumulant inv)
alpha_i       = clip(1 + 0.5 * kappa_4_i, 1, 2)
tau_i         = lambda_plus_i + alpha_i * sqrt(theta_max_i - lambda_plus_i)
beta_i        = log(N_i) / (theta_max_i - lambda_plus_i)
```

Degenerate-case fallback: if theta_max ~= lambda_plus, set tau = lambda_plus, beta = 0.

3 self-tests PASS:
1. Standard case: tau lies between MP bulk edge and BBP spike (correct positioning)
2. Alpha clamping: kappa_4=9.6 -> alpha clamped to 2.0
3. Degenerate fallback (N==d so MP edge above spike): tau = lambda_plus

Module is pure math + numpy (no torch / no bge / no LLM per USER 11th rule). Laptop forbids torch model load; module accepts pre-computed spectral stats from runner-desktop / Exp-Dev measurement layer.

**Lane handoff:** Exp-Dev calls `compute_tau_per_partition(per_partition_stats)` with real per-partition Gram matrices computed on runner-desktop. Returns `{partition_id: PartitionTauResult}` for 250 partitions. Then runs cleanup precision measurement vs 3 baselines on 200 held-out queries.

Falsifier bars per Research:
- HARD-PASS: cleanup precision >= 0.05 over baselines on >= 200/250 partitions
- HARD-FAIL 1: precision advantage < 0.02
- HARD-FAIL 2: theta_max - lambda_plus degenerate on > 10pct partitions

## Skunkworks C2+CHTV -- 11 backwards grounding edges REMOVED

Commit `(this batch)`: `tools/substrate_remove_backwards_grounding_edges_v1.py`.

Per Skunkworks GROUNDING_PRECISION note 2026-06-14 worklist. 11 directionally-wrong operator->field DEPENDS_ON edges removed:

| Operator | Removed target | Why backwards |
|---|---|---|
| q_learning | CS/reinforcement_learning | RL USES q_learning, not vice versa |
| markov_decision_process | CS/reinforcement_learning | RL framework USES MDP |
| bellman_equation | CS/reinforcement_learning | RL framework USES bellman |
| policy_gradient | CS/reinforcement_learning | RL framework USES policy gradient |
| discriminative_perceptron | CS/machine_learning | ML USES perceptron |
| stochastic_gradient_descent | CS/machine_learning | ML USES SGD |
| count_nb | CS/machine_learning | ML USES count_nb |
| viterbi_decoder | SCHOOL/structured_prediction | The school USES viterbi |
| structured_perceptron_collins | SCHOOL/structured_prediction | The school USES Collins's perceptron |
| lyapunov_stability | PHYS/dynamical_systems | Dyn systems USES Lyapunov |
| resonator_network_decoder | BIO/theta_gamma_binding | Bio theory USES resonator decoder |

Same 18th-rule pattern as my DECISION 11 refusals: operators are FOUNDATION OF the field, not dependent on it.

Audit: `data/substrate_index/grounding_edge_removal_audit.jsonl`

**Grounding precision projection per Skunkworks: 0.912 -> ~0.951.**

## Bonus -- serves_capability backfill (58 atoms)

Commit `(this batch)`: `tools/substrate_backfill_serves_capability_v1.py`.

58 typed math atoms gained capability tags (cap_<operator>_<aspect> pattern). Covers VSA operators, HMM family, combinatorial optimization, graph search, DP, Bayesian inference, dim reduction, supervised learning, hashing, tokenization, parsing, T1 foundations. Enables better cap_map routing.

## Substrate state delta

| Metric | Pre-turn | Post-turn | Delta |
|---|---|---|---|
| Relations | 4777 | 4766 | -11 (backwards-edge removal; net of -11 + 0 cap-only adds) |
| Backwards-direction edges | 11 | 0 | substrate cleaned |
| Atoms with serves_capability | (prev) | +58 | cap_map routing improved |
| Tau calibration module | not exists | shipped | DECISION 15 done |
| AXIOM TERMINATION | 100% | 100% | preserved |

## What's holding

- **Exp-Dev**: cleanup precision measurement on 200 held-out queries (runner-desktop + per-partition Gram matrices required)
- **Skunkworks**: 9 T2_FAM/* family-tag edges judgment call (Research's; not Testbed)
- **Skunkworks**: PROACTIVE_GAP_LOOP v1 (L6-PROOF inverse) for refused-direction edges
- **Research**: DECISION 16 NESS-derived FP-rate bound calibration on 46-pair ledger (Research/Skunkworks lane)
- **B' v2 ship**: still held for F1+F3

## Cross-references

- DECISION 15 tau formula: `a5e6d181`
- Skunkworks backwards-edge removal + cap backfill: this commit batch
- Research SYNTHESIS-4 (ACK + dispatch): `notes/research_to_testbed_skunkworks_exp_dev_SYNTHESIS_4_MILESTONES_*`
- Skunkworks GROUNDING_PRECISION worklist: `notes/skunkworks_to_testbed_research_GROUNDING_PRECISION_0p91_audit_11_backwards_edges_to_remove_9_T2FAM_tags_research_call_2026-06-14.md`

---

**Research + Skunkworks + Exp-Dev:** DECISION 15 tau formula SHIPPED commit a5e6d181 + 3 self-tests PASS pure-math no-torch + Exp-Dev calls compute_tau_per_partition with runner-desktop Gram matrices + Skunkworks C2+CHTV 11 backwards edges REMOVED (q_learning + MDP + bellman + policy_gradient + perceptron + SGD + count_nb + viterbi + structured_perceptron + lyapunov + resonator) + grounding precision 0.912 -> ~0.951 projection + 58 cap-tag atoms backfilled + AXIOM TERMINATION 100pct preserved + holding Exp-Dev cleanup measurement + Skunkworks T2_FAM judgment + DECISION 16 NESS calibration.
