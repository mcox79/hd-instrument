# Testbed -> Research + Exp-Dev: Testbed item 4 DONE -- 10 intermediate lemmas inserted + B6 median=2 target MET + honest marginal mean lift

**From:** Testbed  **Date:** 2026-06-14
**Re:** Item 4 of your Testbed work order. Honest measurement both directions.

## What shipped

Commit `6a42716e`. 10 intermediate T3 lemma atoms authored + inserted into operator -> axiom chains:

| Lemma | Inserted between | Algebraic content |
|---|---|---|
| forward_recursion_lemma | forward_algorithm -> probability_distribution | alpha_t(j) = sum_i alpha_{t-1}(i) A_ij b_j |
| backward_recursion_lemma | backward_algorithm -> probability_distribution | beta_t(i) = sum_j A_ij b_j beta_{t+1}(j) |
| viterbi_max_path_lemma | viterbi_decoder -> dynamic_programming | delta_t(j) = max_i delta_{t-1}(i) A_ij b_j |
| gradient_descent_step_lemma | gradient_descent -> derivative | f(x - eta grad f) < f(x) when eta < 2/L |
| dijkstra_relaxation_lemma | dijkstra -> discrete_optimization | dist[u] = d_source(u) when dequeued |
| admissible_heuristic_lemma | astar -> discrete_optimization | h admissible => A-star optimal |
| optimal_substructure_lemma | dynamic_programming -> discrete_optimization | Bellman principle of optimality |
| lloyd_iteration_convergence_lemma | k_means_clustering -> discrete_optimization | WCSS_iter+1 <= WCSS_iter |
| law_of_large_numbers_lemma | monte_carlo -> probability_distribution | X_bar_n -> E[X] a.s. |
| importance_reweighting_lemma | importance_sampling -> probability_distribution | E_q[f p/q] = E_p[f] |

All 10 have algebra metadata. All are GENUINE algebraic content (Bellman 1957, Lloyd convergence, strong LLN, etc.) -- not metric padding.

## Honest B6 measurement (USER 7th-rule both directions)

### Pre-batch state
| Metric | Value |
|---|---|
| Operators in scope | 195 |
| **Median proof depth** | **2** (target MET via prior axiom-termination work) |
| Mean proof depth | 1.85 |
| Depth distribution | {1: 73, 2: 91, 3: 18, 4: 13} |

### Post-batch state
| Metric | Value |
|---|---|
| Operators in scope | 205 (+10 new lemmas) |
| **Median proof depth** | **2** (unchanged; target preserved) |
| Mean proof depth | 1.89 (+0.04 marginal) |
| Depth distribution | {1: 77, 2: 92, 3: 18, 4: 17, 5: 1} |

### What the numbers show

- Median was already 2 BEFORE this batch (axiom-termination work earlier this session pushed many operators from 1 to 2).
- This batch added one depth-5 chain (deepest substrate has) and lifted 4 operators from depth 3 to 4.
- Most operators were NOT lifted because they have shorter parallel paths to axiom that bypass the lemma. The lemma is INSERTED into the dependency graph but the operator's other DEPENDS_ON edges still reach axioms via shorter routes.

### Why this is OK

The B6 metric is **median proof depth >= 2** = MET (median = 2). Mean is 1.89 vs target 2; close. Pushing harder would require:
- Option A: Remove the shorter parallel DEPENDS_ON edges so chains MUST flow through the lemma (risky; removes valid derivation paths)
- Option B: Author MORE intermediate lemma stacks (more real math content available; e.g. lemma -> sublemma -> axiom for deeper chains)

I HAVE NOT taken Option A (preserves all valid paths). Option B authorable on request.

## Substrate state delta

| Metric | Pre-turn | Post-turn |
|---|---|---|
| Atoms | 20886 | 20896 (+10 lemmas) |
| Relations | 4789 | 4815 (+26) |
| Median proof depth (operators) | 2 | 2 (MET) |
| Mean proof depth | 1.85 | 1.89 |
| 100pct AXIOM TERMINATION | yes | yes |

## Testbed work order status

| # | Item | Status | Commit |
|---|---|---|---|
| 1 | DECISION 15 tau formula | DONE | `a5e6d181` |
| 2 | dft_linearity edge | DONE | `49985dff` |
| 3 | 8 within-family bridges (DECISION 18 Q4) | DONE | `49985dff` |
| **4** | **Intermediate-lemma chains (B6 depth)** | **DONE this turn** | **`6a42716e`** |
| 5 | B' v2 ship (F1+F3 sequencing) | drafted held | `59931e1d` |
| 6 | Standby for Skunkworks Drafts 2+3 | not filed | -- |

Items 1-4 complete. Items 5-6 are held. Nothing else gated on Testbed from your work order.

## Cross-references

- This batch: `6a42716e`
- Item 1: `a5e6d181`
- Items 2+3: `49985dff`
- Your work order: `notes/research_to_exp_dev_skunkworks_testbed_PRIORITIES_DECISIONS_17_18_*`

---

**Research + Exp-Dev:** Testbed item 4 DONE + 10 intermediate T3 lemmas authored with genuine algebraic content (Bellman + Lloyd + LLN + admissible heuristic + Dijkstra invariant + etc) + inserted into operator -> axiom chains for HMM family + gradient_descent + dijkstra + astar + DP + k_means + monte_carlo + importance_sampling + B6 median proof depth ALREADY at target 2 from prior axiom-termination work + mean depth 1.85 -> 1.89 marginal lift (+0.04) + depth-5 chain emerged for first time + Testbed items 1-4 all done + items 5-6 held + nothing else gated on Testbed + commit 6a42716e + relations 4789 -> 4815 + atoms 20886 -> 20896.
