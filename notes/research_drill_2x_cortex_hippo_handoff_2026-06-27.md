# Research drill 2x — cortex assembly gap #2: hippocampus -> cortex handoff (sleep transfer)

**Date:** 2026-06-27
**Drill type:** 2x (Angle A biology/brain + Angle B engineering memory hierarchies)
**Calibration:** lit-scan deflation 0.15-0.25 applied to all P estimates; novel-synthesis P capped at 0.50
**Pairs with:** v4 NREM-replay HARD_FAIL fairness diagnosis (notes/research_drill_v4_nrem_replay_fairness_violation_3x_2026-06-27.md) and TWO_TIER generational W in flight (gap4_two_tier_generational_W_v1)

---

## GAP STATEMENT (recap)

Substrate has partial pieces: BTSP tags subset, STC v1 captures into "W_slow", hierarchical 3-tier W is fast/slow/ultraslow buffers, NREM replay is the temporal operator, TWO_TIER generational W is fast->slow architecture.

**Missing:** an explicit cell that tests that items written to a HIPPOCAMPUS-style fast/sparse/pattern-separated store TRANSFER (during a "sleep" phase) into a CORTEX-style slow/dense/schema-integrated store, with the two stores **anatomically separate** (different matrices, different sparsity, different shapes), and with a discriminator that fires on TRANSFER itself (not on cortical storage in general).

---

## ANGLE A — Biology / brain (CLS theory + sleep neuroscience)

### Anchored lit

- McClelland-McNaughton-O'Reilly 1995 (CLS): two systems, fast hippocampus avoids catastrophic interference by sparse pattern-separated encoding; slow cortex extracts statistical regularities via overlapping schemas.
- Frankland & Bontempi 2005 Nat Rev Neurosci: systems-consolidation timeline; hippocampus-dependent -> cortex-dependent over days/weeks; lesion studies show hippocampus becomes dispensable post-consolidation.
- Tse & Morris 2007 Science: schema-driven 1-trial consolidation; pre-existing cortical schema enables fast write to cortex BYPASSING normal multi-replay timeline.
- Klinzing, Niethard, Born 2019 Nat Neurosci: SWR-replay locked to cortical slow-oscillation UP-state; up-state-locking is gating signal, not just timing.
- Walker & Stickgold sleep-stage cycling: SWS for declarative, REM for procedural/integration.
- Yonelinas et al 2019: separate recollection vs familiarity systems map to hippo vs cortex.

### Three substrate-native mechanism proposals (Angle A)

**A1 — Sparse-DG-style index + dense cortical schema with replay-driven Hebbian copy** (P=0.50 deflated from 0.65)

Two anatomically-separate stores:
- `W_hippo`: sparse bipolar code (10% density, k-WTA), dim N_h = 4096, separate matrix, written one-shot with high learning rate.
- `W_cortex`: dense float code, dim N_c = 8192 (different shape!), written via slow Hebbian (small eta).

Encoding: novel item -> pattern-separator (random projection + k-WTA) -> stored in W_hippo as `h_i`. Cortex sees nothing yet.
Sleep phase: sample N_replay items from W_hippo (random uniform OR tagged subset), for each replayed item run a CORTEX-WRITE step: project h_i to cortex space via fixed projection matrix P (NOT learned per-item; structural), apply slow Hebbian update to W_cortex.
Recall test: query cortex AFTER hippo-decay. If cortical recall > 0 for items that were ONLY written to hippo, transfer worked.

Fairness gotchas:
- W_hippo and W_cortex MUST be distinct matrices with different shapes (4096 vs 8192) and different sparsity. If we share dim or share matrix, we're just renaming buffers (USER directive trap).
- Baseline arm: `ARM_NO_REPLAY` = same architecture but skip the replay/cortex-write step. Cortical recall on items-only-written-to-hippo must be ~0 (proves cortex is genuinely separate at start).
- Baseline arm 2: `ARM_DIRECT_CORTEX_WRITE` = items written to cortex directly bypassing hippo. Establishes ceiling.
- Discriminator must fire on the GAP (recall_cortex_after_replay - recall_cortex_no_replay), not on raw cortical recall.

**A2 — Tagged-subset (STC + BTSP composition) selective transfer** (P=0.45)

Refines A1: not all hippo items get transferred. STC-tag at encoding marks subset (e.g., novelty-gated: only items whose `min_cosine(h_i, existing_hippo_atoms) < threshold` get tagged). During replay, ONLY tagged items get transferred to cortex.

Discriminator: cortical recall(tagged) >> cortical recall(untagged) post-sleep. AND: total cortex utilization < |hippo|, proving selective.

Fairness gotchas:
- Tag criterion must NOT be |W|-correlated (per v4 HARD_FAIL lesson). Use novelty (cosine-distance from existing) or BTSP-style temporal coincidence, NOT replay-count.
- Random-tag ablation arm: `ARM_RANDOM_TAGS` = tag random subset of same size. If random-tag and novelty-tag perform equally, the tagging isn't doing the work; transfer mechanism alone explains the gap.

**A3 — Schema-driven fast write (Tse-Morris 2007 analog)** (P=0.35)

If a novel item ALIGNS with existing cortical schema (e.g., cosine to nearest cortical centroid > threshold), bypass hippo and write directly to cortex with full eta. Otherwise route through hippo + multi-replay.

Discriminator: items-with-schema reach cortex in 1 cycle; items-without need >=K replays. Measure cycles-to-cortex-recall as function of schema-overlap.

Fairness gotchas:
- This is conceptually deeper but discriminator is fiddly (schema must already exist; needs pre-training a cortex baseline; risk of confound with the pre-training itself).
- By-construction concern: if cortex is already populated with the schema, "fast write" is just "alignment hits the right basis vectors". May not really test handoff.

---

## ANGLE B — Engineering / materials-science memory hierarchies

### Anchored references

- CPU L1/L2/L3 caches (Hennessy & Patterson Computer Architecture, 5th ed Ch 2): size hierarchy + replacement policy + writeback semantics; LRU/LFU; writeback vs write-through; inclusion vs exclusion.
- LSM-tree compaction (BigTable, Cassandra, RocksDB): SST file structure, level-tiered (L0 -> L1 -> L2...) with size doublings; compaction merges and evicts.
- Mobile flash hierarchy: DRAM (fast/volatile) -> SLC cache (fast-flash) -> TLC main (slow-flash) -> cold backup; background flush.
- Memcached -> Redis -> SQL: hot/warm/cold tier with promotion + eviction policies.
- Memristive crossbar hierarchies: per-synapse short-term plasticity + array-level long-term consolidation; recent work on tiered memristor systems for in-memory neural nets.

### Three substrate-native mechanism proposals (Angle B)

**B1 — LSM-tree-style compaction with explicit level structure** (P=0.50)

Two-level analog of LSM:
- L0 = `W_hippo` (small capacity M_h = 1024 atoms, write-optimized, bumped on every encode)
- L1 = `W_cortex` (large capacity M_c = 16384, read-optimized, write only at compaction time)

Compaction trigger: L0 reaches capacity threshold (>= 0.8 * M_h). Compaction step: read top-K most-recently-touched L0 entries, MERGE into L1 (Hebbian add or weighted average if collision), then EVICT them from L0.

Discriminator: items written to L0 BEFORE compaction must be recallable from L1 AFTER compaction, even if subsequent L0 writes evict them from L0. Pre-compaction: only L0 recall works. Post-compaction: L0 recall fails (evicted) but L1 recall succeeds.

Fairness gotchas:
- L0 and L1 must be distinct matrices with different capacity profiles. Different sparsity is icing.
- Baseline: `ARM_NO_COMPACTION` = L0 fills, then evicts via LRU without writing to L1. Items lost. This is the "what compaction buys you" comparison.
- Verify-referent: discriminator measures recall_L1_post_compaction(items_that_were_in_L0) > 0. NOT general L1 recall (which could come from direct writes).

**B2 — Hot/warm/cold tier with promotion-on-access + lazy flush** (P=0.40)

3-tier (could map onto existing hierarchical 3-tier W as the engine):
- HOT (`W_h`, small, fast, bumped) -- encode here; access promotes counter.
- WARM (`W_w`, medium, slow Hebbian) -- background flush from HOT every K cycles.
- COLD (`W_c`, large, ultraslow, schema-integrated) -- background flush from WARM every K' cycles.

Promotion criterion: HOT -> WARM if access_count > theta_1; WARM -> COLD if access_count > theta_2 OR schema-alignment > theta_s.

Discriminator: items accessed frequently end up in COLD; one-shot items decay from HOT without reaching COLD. Critical: items accessed-via-replay (not real queries) should NOT count toward access_count (else replay becomes self-reinforcing, the v4 trap).

Fairness gotchas:
- Three matrices, three shapes, three update rules -- genuinely separate by construction.
- `ARM_NO_PROMOTION` baseline: all writes go directly to COLD; tests whether HOT/WARM staging adds value.
- WATCH OUT: this is closest to current hierarchical 3-tier W -- ensure cell explicitly tests TRANSFER (recall at COLD for items originally only in HOT) not just "hierarchical W achieves capacity."

**B3 — Write-back cache with dirty-bit and scheduled flush** (P=0.35)

Cache-like: HIPPO is write-back cache for CORTEX. On encode, write to HIPPO with dirty bit set. On read miss in HIPPO, fall through to CORTEX. Background "flush" (= sleep cycle) walks dirty entries in HIPPO, writes them to CORTEX (slow Hebbian), clears dirty bit.

Discriminator: dirty-bit count goes to zero after flush. Items that were written before flush are now in CORTEX. Items written after flush are still dirty in HIPPO.

Fairness gotchas:
- Dirty-bit mechanism is operationally clean and verifiable (count_dirty == 0 post-flush is binary).
- Risk: this is a near-trivial engineering recipe; if it works, what we learned is "we can plumb a queue between two matrices" -- not a substrate-native lesson. P deflated for thin novelty.

---

## TOP-2 PICKS (across both angles, P-ranked, deflated)

### PICK 1 — A1 (sparse-DG-index + dense cortical schema with replay-driven Hebbian copy) [P=0.50]

**Why:** This is the most direct substrate-native instantiation of CLS. Brain-grounded (USER 2026-06-23 standing: brain-grounded mechanisms get high prior). Both stores anatomically separate by shape AND by sparsity (forces structural distinction; can't be papered over by renaming). Composes cleanly with existing NREM replay primitive as the transfer operator. Uses already-shipped pattern-separator candidates (k-WTA / sparse bipolar; chain-grade per 2026-06-23 lift findings).

**Discriminator (falsifiable, concrete numbers):**

Three arms, N_h=4096 sparse (k=410, ~10% density), N_c=8192 dense, M=200 items encoded into hippo over 200 cycles, then SLEEP_PHASE = 50 replay cycles (random sample from W_hippo without replacement-with-replacement allowed), then recall test on cortex AFTER setting W_hippo to zero (decay/reset).

- `ARM_FULL_HANDOFF`: encode -> hippo, sleep replay -> writes to cortex via fixed projection P + slow Hebbian eta=0.01. Cortex recall after hippo-zeroed: expected accuracy >= 0.50 (HARD_PASS gate).
- `ARM_NO_REPLAY` (baseline-floor): encode -> hippo, NO sleep replay, hippo zeroed. Cortex recall: expected ~0.05 +/- 0.02 (cortex was never written; random-chance noise). MUST be in [0.00, 0.10] band.
- `ARM_DIRECT_CORTEX` (baseline-ceiling): same items written directly to cortex with same eta. Cortex recall: expected ~0.65 +/- 0.05 (the ceiling for what the cortex slow-Hebbian can hold over M=200 items).

HARD_PASS_GATE: `accuracy(ARM_FULL_HANDOFF) >= 0.50` AND `accuracy(ARM_FULL_HANDOFF) - accuracy(ARM_NO_REPLAY) >= 0.40` AND `accuracy(ARM_FULL_HANDOFF) >= 0.70 * accuracy(ARM_DIRECT_CORTEX)`.

HARD_FAIL: `accuracy(ARM_FULL_HANDOFF) - accuracy(ARM_NO_REPLAY) < 0.10` (transfer is doing essentially nothing).

MIDDLE_BAND: anything in between (transfer partial; tune projection / Hebbian rate).

**Verify-the-referent gate (per discipline):** assertion in cell: `np.allclose(W_hippo_post_zero, 0)` AND `accuracy_baseline_no_replay <= 0.10` AND `W_hippo.shape != W_cortex.shape` (forces anatomical separation). Smoke MUST FIRE these gates and SHOW per-arm accuracy gap >= 0.10 at smoke-N=50 items (per META_RULE_K).

**By-construction fairness:** baseline_no_replay is genuinely ~0 (cortex empty), ceiling is genuinely ~0.65 (cortex Hopfield capacity at M=200/N=8192 ~ alpha=0.024, well below cliff), middle band [0.05, 0.65] gives 0.60 of dynamic range. The discriminator measures the GAP, not absolute recall.

### PICK 2 — B1 (LSM-tree-style compaction with explicit level structure) [P=0.50]

**Why:** Engineering-domain mechanism with crisp formal semantics (compaction trigger, eviction policy, write semantics). Independent of A1 family (the two together verify the mechanism isn't one-trick — if both PASS we have cross-domain convergence; if only one PASSes we learn something about which framing the substrate prefers). LSM-tree is decades-validated at planet scale, so engineering prior is high; the substrate-native question is whether sparse-distributed-storage compaction has analogous benefit.

**Discriminator (falsifiable, concrete numbers):**

Two-level system, M_L0 = 1024 capacity, M_L1 = 16384 capacity, N=4096 dim. Encode 3000 items over 3000 cycles. Compaction trigger: L0_size >= 819 (0.8 * 1024). Compaction action: copy top-K=512 most-recently-touched L0 atoms into L1 (Hebbian merge), evict them from L0.

- `ARM_COMPACTION_ENABLED`: full mechanism. After 3000 encodes, run recall test on items 1-200 (oldest; long-since-evicted from L0). Expected: recall_L1 >= 0.40 (HARD_PASS gate) -- these items were transferred via compaction.
- `ARM_NO_COMPACTION` (baseline-floor): L0 fills, then evicts via LRU without writing to L1. After 3000 encodes, items 1-200 recall: expected ~0 (lost). MUST be <= 0.05.
- `ARM_DIRECT_L1` (baseline-ceiling): bypass L0; write everything directly to L1. After 3000 encodes, items 1-200 recall: depends on L1 saturation at M=3000/N=4096 alpha=0.733 (above classic Hopfield 0.138, expect partial recall ~0.30 for old items if any consolidation). Ceiling expected ~0.50.

HARD_PASS_GATE: `recall_compaction(items_1-200) >= 0.40` AND `recall_compaction - recall_no_compaction >= 0.35` AND `recall_compaction >= 0.80 * recall_direct_L1`.

HARD_FAIL: `recall_compaction - recall_no_compaction < 0.10`.

**Verify-the-referent gate:** assertion `L0.matrix is not L1.matrix` (object identity check; not the same buffer); `L0.capacity != L1.capacity`; per-compaction-event log shows the K=512 atoms written to L1 are the K=512 atoms evicted from L0 (track explicit IDs).

**By-construction fairness:** L0 evicted items would be UNRECOVERABLE without the L1 transfer step. The discriminator literally requires the items to have moved between matrices. Cell author can verify per-compaction by saving L0 and L1 snapshots and asserting set-intersection-then-difference invariants.

---

## CROSS-PICK NOTES

- A1 and B1 are **independent mechanisms** (CLS-style replay vs LSM compaction) but **share the load-bearing discipline**: anatomically-separate matrices, baseline that proves cortex/L1 is empty without the transfer step, ceiling that bounds what's reachable, gap >= 0.35-0.40 to count.
- Both AVOID the v4 NREM-replay trap: neither uses replay-count as an importance signal. A1 uses random sampling from hippo (or novelty-tagged subset in A2); B1 uses recency (LRU-style) which is orthogonal to |W|.
- Both have a HARD_PASS_PARTIAL middle band that's instructive: if transfer happens but at half-strength, we learn the Hebbian rate or compaction merge policy needs tuning (NOT that the mechanism is bust).
- Recommended sequencing if compute permits BOTH: ship A1 first (brain-grounded, USER-prior-favored direction), then B1 as cross-domain witness. If A1 HARD_PASS and B1 HARD_PASS, the handoff capability is robust across framings. If A1 HARD_PASS and B1 HARD_FAIL (or vice versa), we learn which framing the substrate's geometry supports better.
- Both compose downstream with **TWO_TIER generational W** (in flight): if TWO_TIER HARD_PASS confirms fast/slow transfer in single-store, A1/B1 confirm two-store transfer; together they cover the consolidation axis.

---

## OUT-OF-SCOPE (deliberate punts; flagged for later)

- A2 (STC-tagged subset) is a natural v2 follow-up to A1 once HARD_PASS; not in the first cell to keep discriminator simple.
- A3 (schema-driven fast-write Tse-Morris) requires a pre-trained cortical schema which we don't have at production scale; revisit after substrate has stable schema atoms (post-Stage-3 maturation).
- B2 (3-tier hot/warm/cold) overlaps too much with hierarchical 3-tier W (already in flight as separate cell); avoid duplication.
- B3 (write-back cache + dirty bit) is too thin in substrate-native learning value; the mechanism is plumbing, not science.
- REM-vs-SWS phase separation (Walker-Stickgold) is deferred — interesting but adds a second axis (sleep-stage cycling) that confounds the first-pass handoff test.

---

## CALIBRATION NOTES

Both TOP-2 P=0.50 (at the novel-synthesis cap). I considered going higher on A1 because brain-grounding (USER 2026-06-23 high-prior) and existing primitive composition both argue up, but the lit-scan deflation discipline plus the fact that we just saw a 3x research drill (v4) demonstrate "the obvious mechanism collapses to |W|-bias when actually run" keeps me honest at the cap. The honest expectation is that one of the two will HARD_PASS, one will MIDDLE_BAND, and we'll learn which framing the substrate prefers.

P=0.50 reflects: 0.70 raw confidence (mechanism is well-defined, fairness gates are explicit, baselines are well-justified) minus 0.20 lit-scan + novel-synthesis deflation.

---

## HANDOFF

USER reviews TOP-2 picks. On approval, I author preregs for A1 first (gap2_cortex_hippo_handoff_v1) and queue B1 as v2. Cell-author = exp_dev (spawn hdi_exp_dev on approval); landing-VET = skunkworks; orchestrator routes to local_cpu_queue (N values modest; matmul-light vs prior heavy cells; no GPU requirement at this scale).

-- research (Opus 4.7 1M ctx)
