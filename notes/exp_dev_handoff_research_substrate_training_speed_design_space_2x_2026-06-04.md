# exp_dev hand-off -- research: substrate training-speed full design space 2x drill

## Filed-by
research sub-agent, 2026-06-04

## Trigger
Research note: d:/AI/hd-instrument/notes/research_drill_substrate_training_speed_design_space_2x_2026-06-04.md
Prior hierarchical 2x drill: d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md

## Pause state
Check data/orchestrator_paused.flag before acting on any queue-add items.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off task + why + contract + autonomy. It does NOT specify anchor names, sweep grids, threshold formulas, HF1/HF2/HF3 numerical bounds, queue choice + ETA, or pre-committed cap_map decisions.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY): Composition-axis orthogonality test
- Research pointer: Sub-question 4, Cheap Decisive Test Part C in the research note above.
- Substrate-product reading: validates whether tricks T1 (no-backprop), T8 (adaptive sparsity), and T5 (streaming parallel writes) compose near-multiplicatively (>= 0.72 * product) or sub-multiplicatively at substrate-class N=4096-8192.
- Tier hint: Tier-1 (laptop CPU smoke; < 60s; validates the compound speedup claim's algebraic foundation).
- Why-now: the entire compound speedup narrative depends on axis orthogonality. If T1+T8 compose sub-multiplicatively (e.g., only 2x not 7x combined), the downstream speedup estimates must be revised by 3-5x. This is the cheapest falsification test for the most load-bearing assumption.

### Anchor 2: Adaptive sparse Hopfield capacity validation (T8)
- Research pointer: Sub-question 1 Tier A T8; Falsifiable Prediction HP2.
- Substrate-product reading: if sparse coding at f=0.05 achieves alpha_c ~ 6.7 (vs 0.138 dense), this unlocks ~49x capacity gain at the same N. This directly determines whether the substrate can hold enough patterns to be useful at concept-level LLM integration (N=8192 sufficient for V_c=5K concepts vs needing N=65K for dense).
- Tier hint: Tier-1 CPU smoke; estimated < 60s.
- Why-now: f=0.05 sparse has never been empirically tested in the substrate's specific codeword geometry. Prior drills used dense codes. This is a new regime.

### Anchor 3: Modern Hopfield p=4 kernel retrieval at substrate-class (T6)
- Research pointer: Sub-question 1 Tier B T6; Falsifiable Prediction HF2.
- Substrate-product reading: if p=4 polynomial kernel achieves the theoretical 6x capacity increase at N=4096 with the substrate's actual concept vector geometry, this extends the substrate's usable range from ~565 to ~3400 patterns -- enough to cover a meaningful concept vocabulary at a single substrate without going to N=16384.
- Tier hint: Tier-1 CPU smoke; estimated < 60s.
- Why-now: NeurIPS 2024 capacity paper proves optimal capacity under data manifold hypothesis; the open question is whether substrate's bipolar pattern geometry satisfies the manifold condition. Cheapest test: generate bipolar concept vectors, compare Hebbian vs p=4 kernel retrieval accuracy at matched M.

### Anchor 4: Per-layer independent update speedup in substrate-residual hybrid (T13)
- Research pointer: Sub-question 3, Tier-emergent at Pythia-160M+; Sub-question 6 Tier 2 validation design.
- Substrate-product reading: if substrate layers in a hybrid update without waiting for backprop chain (T2 + T13 combined), the update latency for those layers is O(N^2) vs O(L * K * D^2) for backprop layers. At 25% substrate layers, this predicts measurable throughput improvement. Validates the hybrid architecture path to Pythia-160M tier.
- Tier hint: Tier-2 (requires Pythia-160M pre-trained checkpoint; fine-tuning only; < 30 min on A100).
- Why-now: this is the next-tier empirical validation step. Substrate-class is validated; hybrid integration at 160M is the first cross-tier test.

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_substrate_training_speed_design_space_2x_2026-06-04.md
- Prior hierarchical drill: d:/AI/hd-instrument/notes/research_drill_training_speed_hierarchical_architecture_2x_2026-06-04.md
- Tier-specific validation designs: Sub-question 6 in research note above (all four tiers).
- Trick catalog with scale-extension verdicts: Sub-question 1 and Sub-question 2 in research note above.
- Cap_map: d:/AI/hd-instrument/data/cap_map.md (rows Q-B1, PP-45/46, PP-50 are directly relevant).

---

## Contract

exp_dev decides: anchor selection from the ranked list, anchor naming, sweep grid design, pre-reg threshold formulas, queue assignment, and ETA estimate. All of these are within exp_dev autonomy.

Orchestrator decides: whether to act on this handoff (pause gate), prioritization relative to other open handoffs.

## Autonomy declaration

exp_dev has full autonomy to select any subset of the above anchors, re-rank them based on current queue state and runner availability, combine them into a single batch where appropriate, and design the specific experiment geometry. The research note provides algebraic grounding; empirical design is entirely exp_dev's domain.
