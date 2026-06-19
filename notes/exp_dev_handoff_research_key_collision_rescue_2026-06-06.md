# exp_dev hand-off -- research: key-collision real-encoder rescue (2x drill)

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_key_collision_real_encoder_rescue_2x_2026-06-06.md
Date: 2026-06-06

Pause state block: check data/orchestrator_paused.flag before dispatching any anchor.
Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT + AUTONOMY.
exp_dev decides anchor names, sweep grids, threshold formulas, queue assignments, and pre-reg bands.

---

## Anchor candidates (rank-ordered, cheapest decisive first)

### Rank 1: EFFECTIVE-RANK DIAGNOSTIC (5-10 min CPU, PREREQUISITE)
Anchor pointer: compute SVD of whitened real-encoder (Pythia-160m) key matrix K (P x N), compute
effective_rank = (sum_i s_i)^2 / (sum_i s_i^2) as a function of P in [100, 2000].
Substrate-product reading: if effective_rank plateaus below 100 for P > 500, confirms key-collision
is intrinsic-dimensionality-limited (d_eff ~ 50-80). This is the algebraic framework test -- all other
anchors depend on this being true.
Tier hint: diagnostic / prerequisite; should run before any capacity anchor in this batch.
Why now: 5 min CPU; gates interpretation of all subsequent DIMSPARSE2 + MULTIHEAD results.

### Rank 2: DIMSPARSE2 real-encoder (CPU ~30 min, already authorized)
Anchor pointer: sparse substrate-state on real Pythia-160m keys, varying state sparsity f_state.
Substrate-product reading: tests whether sparse substrate STATE reduces key-overlap (Tsodyks mechanism
on the correct side of the bottleneck). Prior sparse-VALUES result was zero gain; sparse STATE is
mechanistically distinct and algebraically predicted to give 3-6x.
Tier hint: Tier 1 (authorized, mechanism-decisive, cheap).
Why now: completes the Tsodyks-Feigelman test. If HARD-PASS, compound stacking is viable.

### Rank 3: MULTIHEAD-4 (CPU ~20 min, novel mechanism)
Anchor pointer: 4-head substrate with independent Hadamard/random projections of whitened real-encoder keys.
Substrate-product reading: multi-head subspace decomposition gives statistically independent retrieval
attempts; error-correction across heads; predicted 1.5-2.5x compound at matched compute.
Tier hint: Tier 1 (novel, CPU-feasible, clean compound hypothesis).
Why now: if DIMSPARSE2 passes, this is the next independent attack. If DIMSPARSE2 fails, this test
is even more important (it is the backup rescue path for key-collision).

### Rank 4: DIM-EXPANSION D=2048 + ETF codebook compound (CPU ~30 min)
Anchor pointer: dim-expansion to D=2048 with ETF-initialized codebook (compounds G8 + Slot 9).
Substrate-product reading: tests whether two known single-lever gains (dim-expansion 6.68x + ETF 2.75x)
compound multiplicatively. Algebraic prediction: ~10-15x over baseline at this cell.
Tier hint: Tier 2 (compound of two known results; still CPU-feasible at D=2048).
Why now: the 2026-06-06 drill predicts ceiling ~8-15x for dim-expansion at D=4096; D=2048 + ETF may
already hit that ceiling. Decisive for understanding the dim-expansion + ETF interaction.

### Rank 5: HIER-VQ-v1 (CPU ~30 min, hierarchical retrieval)
Anchor pointer: two-stage retrieval with coarse VQ B=64 buckets on real-encoder keys, fine retrieval within bucket.
Substrate-product reading: hierarchical indexing reduces effective collision set from P to P/B.
Algebraic prediction: sqrt(B) gain ~ 8x for B=64. Dependent on cluster quality.
Tier hint: Tier 2 (dependent on cluster separation; need DIAGNOSTIC result to assess viability).
Why now: if EFFECTIVE-RANK diagnostic shows d_eff clustering is strong, HVQ is viable; if not, skip.

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_key_collision_real_encoder_rescue_2x_2026-06-06.md
- G8 dim-expansion finding: check cap_map / experiment notes for G8 anchor
- Slot 9 ETF finding: check cap_map / experiment notes for Slot-9 anchor
- Prior sparse-values result (zero gain): check cap_map for DIMSPARSE or sparse_values anchor
- DIMSPARSE2 authorization: check exp_dev handoff / strategy files for DIMSPARSE2

---

## Contract

exp_dev is autonomous on: anchor names, sweep grid, threshold bands, queue assignment, timeout formula,
smoke vs full sequencing, whether to batch or serial.
exp_dev is NOT autonomous on: pausing or resuming the runner, changing the substrate architecture
beyond what anchors above specify, committing cap_map changes (orchestrator/verdict_handler owns that).

## Autonomy declaration

exp_dev has full autonomy to sequence, batch, skip, or reorder anchors above based on current queue state,
runner availability, and findings from the diagnostic anchor. The rank ordering above is research-advisory;
exp_dev should apply the rung-ladder (small-scale-first) methodology and its own judgment.
