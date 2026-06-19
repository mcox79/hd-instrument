# exp_dev hand-off -- research: codebook capacity structural 3x

Filed-by: research sub-agent (claude-sonnet-4-6)
Filed: 2026-06-10
Trigger: d:/AI/hd-instrument/notes/research_drill_codebook_capacity_structural_3x_2026-06-10.md

## Pause state block

exp_dev MUST check data/orchestrator_paused.flag before any queue_add.sh calls.
These candidates are queued for when experiments are active.

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides TASK + WHY + CONTRACT + AUTONOMY to exp_dev.
It does NOT specify anchor names, sweep grids, threshold formulas, or pre-committed
cap_map decisions. exp_dev designs the experiment; research provides the framing.

---

## Anchor candidates (rank-ordered)

### Candidate 1 (HIGHEST PRIORITY): Softmax cleanup vs argmax capacity comparison

Anchor pointer: From research note Level 12.3 / Level 11.2, "MODERN-HOPFIELD-CLEANUP"
Substrate-product reading: The 2x drill confirmed the FHRR dot-product + argmax regime
is structurally limited to N/(2 ln N). The 3x drill identifies softmax cleanup
(one-step modern Hopfield update) as the highest-leverage capacity improvement with
the lowest implementation risk. If softmax cleanup at well-chosen beta gives K* > 1000
(vs 246 baseline) at P_correct > 0.9, this authorizes replacing argmax with softmax
in the production cleanup step -- a 2-3 day code change with 4-50x capacity benefit.
The mechanism is mathematically validated (Ramsauer 2020, 298 citations) and requires
only switching from argmax(dot_product) to softmax(beta * dot_product) in retrieval.
Tier hint: CPU smoke (N=4096, K varies from 100 to 5000), then CPU full (larger K).
Why-now: This is the single most actionable finding from the 3x drill. It directly
addresses the mandate that 2x WAS WRONG about codebook capacity -- the real lever is
cleanup architecture, not codebook design. Pre-test: 2-3 hours on local CPU.

### Candidate 2 (HIGH): Sparse Willshaw codebook capacity measurement

Anchor pointer: From research note Level 11.1 "SPARSE-FHRR" and Level 2.1 Willshaw model.
Substrate-product reading: Sparse binary patterns with k=log(N) active bits achieve
N^2/(log N)^2 capacity (Willshaw 1969, Palm 1982) -- approximately 116,000 at N=4096 vs
246 for dense FHRR. This is a ~500x gain using the same N-dimensional vector space but
with binary sparse atoms and threshold cleanup instead of complex FHRR + dot-product.
The experiment tests whether this theoretical gain materializes empirically at production N.
This is a different codebook entirely (not chirp/QR optimization); it breaks the bound
via the sparsity mechanism, not coherence optimization.
Tier hint: CPU smoke (N=4096, k=12, K in {100, 500, 2000, 10000, 50000}), binary vectors.
Why-now: If confirmed, sparse Willshaw replaces (or augments) the rare-entity storage tier
in production, giving effectively unlimited capacity for low-frequency entities.
HARD-PASS: K* > 5000. HARD-FAIL: K* < 500. Middle band: 500-5000 (investigate k sensitivity).

### Candidate 3 (HIGH): Softmax beta sensitivity sweep

Anchor pointer: From research note Level 6.3 "Energy Function Shaping" and Level 11.2.
Substrate-product reading: The beta (inverse temperature) parameter in softmax cleanup
determines the basin sharpness. Too low (beta ~ 1/sqrt(N)): all patterns blend.
Too high (beta ~ sqrt(N)): nearest-neighbor, same as argmax. Optimal beta: log(K)/N.
The capacity vs beta curve is the key empirical characterization needed to guide
production parameter selection. This experiment maps the (K, beta) -> P_correct surface.
Tier hint: CPU full sweep (N=4096, K=500, beta in {0.5, 1, 2, 4, 8, 16, 32} / sqrt(N)).
Why-now: Required before authorizing softmax cleanup in production -- need to know
whether the gain is robust to beta miscalibration or brittle.

### Candidate 4 (MEDIUM): Per-shard capacity scaling with shard count

Anchor pointer: From research note Level 10.1 / 10.4 "Cortical Column Parallel" and Level 4.5.
Substrate-product reading: Per-predicate sharding already achieves linear capacity scaling
(C shards * K per shard). The open question is the ROUTING OVERHEAD as C grows from
current ~20-50 shards to C=200-500. If routing overhead is sub-linear in C, large-scale
sharding is the fastest path to LLM-competitive structured storage.
Tier hint: CPU full (measure retrieval latency as C scales from 10 to 500 shards,
K=200 per shard, N=4096). Profile routing vs retrieval time separately.
Why-now: Informs the production sharding architecture before v1 demo deployment.

### Candidate 5 (MEDIUM): Adaptive sparsity two-tier storage proof of concept

Anchor pointer: From research note Level 11.7 "ADAPTIVE-SPARSITY" and Level 8.3.
Substrate-product reading: Dense FHRR for top-1000 frequent entities (fast dot-product
retrieval), sparse Willshaw for remaining (slower threshold retrieval). The combined
system achieves >1000x capacity vs pure FHRR. This experiment validates the two-tier
routing logic: dense lookup first, sparse threshold fallback if no match.
Tier hint: CPU medium (N=4096, 1000 dense + 5000 sparse entities, 200 test queries).
Why-now: Requires Candidate 2 (sparse Willshaw) to HARD-PASS first.
Do not run this until Candidate 2 result is known.

---

## Context pointers (file paths, not summaries)

Research note (this drill): d:/AI/hd-instrument/notes/research_drill_codebook_capacity_structural_3x_2026-06-10.md
Prior 2x drill: d:/AI/hd-instrument/notes/research_drill_bundle_capacity_limits_2x_2026-06-09.md
Modern Hopfield 5x DEEPER: d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_DEEPER_5x_2026-06-07.md
Modern Hopfield upgrade 3x: d:/AI/hd-instrument/notes/research_drill_modern_hopfield_upgrade_path_3x_2026-06-04.md
Modern Hopfield handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_modern_hopfield_upgrade_2026-06-04.md

---

## Contract section

This handoff is triggered by a 3x capacity drill that found 3 mechanisms genuinely breaking
the sqrt(N/K) FHRR bundle superposition barrier: (1) modern Hopfield softmax cleanup,
(2) sparse Willshaw codebook, (3) adaptive sparsity hybrid.

The priority ranking is: Candidate 1 (softmax) > Candidate 2 (sparse Willshaw) >
Candidate 3 (beta sweep, depends on 1) > Candidate 4 (shard scaling) > Candidate 5
(two-tier, depends on 2).

If Candidate 1 HARD-PASSES (K* > 1000): immediately authorize softmax cleanup in
production retrieval. This does not require a new anchor -- it is a cleanup change.

If Candidate 2 HARD-PASSES (K* > 5000): authorize sparse Willshaw as the rare-entity
storage tier. Design a separate sparse codebook alongside the existing FHRR codebook.

If both HARD-FAIL: the structural barrier is confirmed for ALL practical mechanisms at
production N, and the only capacity path is increased sharding (Candidate 4).

Research does NOT authorize specific implementation choices -- those are exp_dev's domain.

## Autonomy declaration

exp_dev has full autonomy over:
- Exact anchor names and parameter grids
- Pre-registration bands (use the guidance in the research note as starting point)
- Implementation details of softmax cleanup (e.g., whether to use complex or real softmax)
- Choice of K values in the sweep
- Whether to run Candidates 1 and 2 in parallel or sequentially
- Whether to use existing FHRR infrastructure or a standalone test harness
