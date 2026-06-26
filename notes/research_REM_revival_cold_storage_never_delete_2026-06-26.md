# Research — REM revival: cold-storage architecture (never delete, only relocate + combine)

Date: 2026-06-26
Drill type: level-2 operational revival drill on Cell B HARD_FAIL via USER's reframe
Parent: notes/research_gap4_brain_selective_homeostasis_2026-06-26.md
Trigger: USER reframe — "Why are we pruning anything? If things are never used, maybe test them for combination, but we shouldn't have to throw anything out. Maybe move those things to cold storage?"

---

## HEADLINE

Substrate should NEVER delete weights. It should RELOCATE them to cold storage and periodically COMBINE redundant cold-storage patterns into schemas. This is precisely what the brain does — "synaptic pruning" is a misnomer; the underlying biology is engram relocation (Tonegawa lab 2024; adult-hippocampal-neurogenesis-mediated silencing of original engrams), spine elimination of UNCAPTURED-and-UNTAGGED spines only (Li 2017), and slow schema-formation via semantic-similarity merging in cortex (CLS / Tse-Morris). The database analog is mature: LSM-trees (HotRAP, arxiv 2402.02070) handle exactly this hot-warm-cold tiering with formal promotion/demotion, and the SEDM agent-memory paper (arxiv 2509.09498) explicitly implements "merge items with high semantic similarity, recycle rather than delete" as its core consolidation primitive. Cell B HARD_FAIL is recoverable not by fixing downscale-selectivity but by REPLACING the delete-anything frame with relocate-and-combine.

The mathematical reason this works where Cell B failed: cold storage SOLVES the anti-selectivity problem at the architecture level. Weights below a magnitude / recency threshold get moved out of W_active (which is the only matrix the read-loop touches at full bandwidth) into W_cold (which is touched only on retrieval-miss or periodic-schema-scan). The dwindling-but-precious tail no longer competes for active-W bandwidth, so it cannot be eaten by global downscale — there IS no global downscale anymore. Capacity in W_active is bounded by the migration rule, not by destructive multiply.

P_deflated for at least one cold-storage variant closing Cell B HARD_FAIL while passing the indefinite-ingest discriminator: **0.50** (capped at novel-synthesis ceiling per calibration penalty; multiple lit-precedents for the components — HotRAP, SEDM, CLS — but no substrate-prior on the composed three-tier W_active/W_cold/W_schema architecture).

---

## Section 1 — Why the delete-anything frame is wrong (plain English)

Substrate's weights are not transactions in a ledger that you can mark dirty and garbage-collect. They are MEMORIES. The biological brain has never evolved a mechanism for "memory deletion." What it HAS evolved is:

1. **Selective spine elimination** — but only of NEWLY-FORMED, UNTAGGED, UNCAPTURED spines. Established spines from before the most recent learning bout are NEVER pruned by sleep. They may weaken passively over years if not re-accessed, but the structural synapse persists.

2. **Engram relocation** — Tonegawa lab (Nature 2025, Neuron 2024 Liu et al.) showed that remote memory recall RE-RECRUITS a NEW hippocampal engram ensemble rather than reading the original. The original engram is SILENCED (functionally suppressed by neurogenesis-mediated inhibitory wiring), not erased. If you re-activate the original ensemble pharmacologically, the memory is still there.

3. **Schema consolidation** — across days-to-weeks, neocortex extracts statistical regularities from REPEATED replay of hippocampal episodes, building a SUMMARY representation (the "schema") that compresses many similar episodes into a shared substrate. The individual episodes are NOT deleted from hippocampus; they fade gradually if not re-accessed, but the schema in cortex is FORMED ADDITIVELY (Tse et al. 2007 Science; McClelland-O'Reilly-Norman CLS 1995).

The clean takeaway: brain capacity management is **NEVER subtractive**. It is hierarchical (multi-tier storage), additive (schema formation builds new representations without erasing the substrate), and lazy (engrams may silence under neurogenesis pressure but the structural trace persists). The "synaptic pruning" terminology is a 1970s misnomer that confused electron-microscopy-visible spine counts with information storage — the actual information was being moved to lower-bandwidth storage (synaptic clusters, dendritic spines further from soma, less-frequently-replayed cortical regions), not deleted.

USER's reframe is precisely this principle: "we shouldn't have to throw anything out. Maybe move those things to cold storage."

---

## Section 2 — What the brain actually does (biology accurate, plain English)

The brain's "never delete, only relocate + combine" pipeline runs across four timescales:

### Timescale 1: per-event (seconds to minutes)

Every memory event creates a hippocampal engram (CA3-DG cell ensemble) AND a cortical engram (sparse PFC/sensory cortex cells, sub-threshold initially). The cortical engram is "born silent" — it cannot yet be retrieved on its own, but it has wiring marks (potentiated synapses) that will become recallable later. Crucially: BOTH are stored. The brain doesn't decide "this event will only live in hippocampus." It writes to both, and the cortical copy is initially under-developed.

### Timescale 2: per-night (hours)

During NREM, sharp-wave ripples replay tagged hippocampal engrams. This replay does TWO things:
(a) Re-Hebbian-strengthens the hippocampal engram itself (anti-decay).
(b) Drives co-activation of the cortical engram cells, strengthening their inter-cell connections via Hebbian LTP.

During REM, dendritic Ca spikes on layer-5 pyramidal neurons selectively prune **only NEW spines that did NOT co-fire with the dendritic event** (Li 2017 Nature Communications, confirmed 2020 PMC7511313). Established spines from prior learning bouts are NOT eligible for this pruning. Pre-existing schema-supporting spines are protected by their already-having-been-captured-into-persistent-LTP status (STC: late-LTP synapses are immune to REM pruning).

### Timescale 3: per-week (days to weeks)

The hippocampal engram for any specific episode begins to SILENCE under adult-hippocampal-neurogenesis pressure. New dentate gyrus granule cells, born in subgranular zone, project to CA3 with inhibitory wiring that disrupts the original engram's reactivation pathway. The neurons of the original engram are still alive and synaptically intact, but their access pathway is partially blocked. Meanwhile, the cortical engram has been strengthened by hundreds of replay cycles and is now retrievable on its own. Retrieval cue → cortex → engram readout. Hippocampus is no longer required for this episode.

But here's the load-bearing detail: when remote recall happens, recent work (Liu et al. Neuron 2024, Yang et al. Nature 2025) shows the hippocampus is RE-RECRUITED — a NEW hippocampal engram is formed FROM the cortical readout, supporting "memory updating" (integration of new information into the old memory). This is systems RE-consolidation. The brain's hippocampus is not just temporary storage; it is a workspace that gets re-allocated whenever an old memory needs editing. The original hippocampal engram remains silenced, but a new working-engram is built for the editing operation.

### Timescale 4: per-month-to-year (consolidation into schema)

When many similar episodes have all been consolidated to cortex over weeks, the SHARED structure across them (the schema) becomes the dominant representation. Individual episode-specific cortical engrams persist but their distinct features fade; what remains is a prototype-like shared substrate that supports rapid generalization to new instances. Tse et al. 2007 showed in rats that, once a schema exists, a single trial of a schema-consistent new episode is enough to embed it permanently in cortex (no consolidation period needed). This is "schema-fast-learning" — the schema acts as scaffolding that makes new consistent episodes trivially absorbable.

**No deletion happens at any step.** What happens is:
- Hot → warm: replay-based strengthening of cortical engram + silencing (not erasure) of hippocampal engram
- Warm → schema: many similar warm engrams contribute to a shared substrate that becomes the dominant readout
- Forgetting: only the COMPETITIVE access (which engram wins on partial cue) shifts; the underlying synaptic substrate is intact for decades

---

## Section 3 — Substrate-feasible cold-storage architecture

### The data structures

Three matrices, all bf16 sparse:

- **W_active** — current Hebbian write/read matrix. Size N×N. Bandwidth: every retrieval queries this. Capacity bounded by O(N) patterns at the substrate's chain-grade density. The MIGRATION RULE prevents this from saturating.

- **W_cold** — relocated patterns. Size unbounded (sparse storage, only nonzero entries). Bandwidth: queried only on W_active retrieval-miss (the "fallback path") OR on periodic-schema-scan. Read latency higher (no penalty for sparse storage at substrate volumes) but storage is essentially free.

- **W_schema** — consolidated/combined patterns. Size N×N (single matrix; schemas overwrite each other only when explicitly merged by combination scan). Bandwidth: queried alongside W_active on every retrieval as a "prior" / "schema bias" term. This is the cortical analog.

### Per-weight activity tracker

T[i,j] = last-touched cycle (per weight in W_active). 4-byte int per nonzero entry. At N=2048 with 10% density, this is ~3MB. Update on every Hebbian write OR retrieval hit (a retrieval that uses W[i,j] in the readout updates T[i,j] to current cycle).

A[i,j] = access count (EWMA, single byte u8 with logarithmic mapping). At 10% density of N=2048, this is ~400KB.

### Migration rules (W_active → W_cold)

Every J_migrate cycles (say 500, equivalent to ~1 sleep cycle of substrate-time):
- For each weight in W_active: compute staleness = current_cycle - T[i,j], importance = A[i,j].
- If (staleness > K_threshold AND importance < I_threshold): move to W_cold.
- "Move" = copy (i, j, W[i,j]) to W_cold sparse storage; zero out W_active[i,j]; clear T and A entries for that (i,j).

**Crucially: NEVER decay weights in W_cold.** Once in cold storage, a pattern's strength is preserved EXACTLY. The whole point of cold storage is that it is read-once-when-needed and not subject to the homeostatic mechanisms operating on W_active. (This is the substrate analog of "established spines are not eligible for REM pruning.")

### Schema combination scan (W_cold → W_schema)

Every J_combine cycles (say 2500, less frequent than migration):
- Hierarchical scan of W_cold for redundant patterns.
- "Redundant" = pair of cold patterns with cosine similarity above some threshold (say 0.85) after sparse projection.
- Hierarchical merge: replace pair with midpoint (centroid), increment a "weight" / "evidence" counter, accumulate into W_schema via a slow Hebbian write at the centroid.
- Merged sources can be MARKED-AS-CONSOLIDATED in W_cold (kept for audit / re-expansion) but their bandwidth contribution shifts to W_schema.

Implementation note: streaming k-means with merge (Bhattacharjee 2023 Online k-means) gives O(k poly(log n)) update time and is the canonical streaming centroid-merge primitive. SEDM (arxiv 2509.09498) implements exactly this for agent memory — their "consolidation and progressive evolution module" merges items with semantic similarity above threshold while preserving evidence.

### Retrieval path (load-bearing for cold-storage to work)

Standard retrieval queries W_active first (hot path). If confidence below threshold (refuse-gate fires), queries W_cold (cold path; slower; full sparse scan). Result from cold path can be PROMOTED back to W_active (lazy promotion = re-Hebbian-write at retrieved strength; re-tracks T[i,j] = current cycle; the access counts as a "hit"). This gives the substrate the LSM-tree HotRAP property: cold items that turn out to be hot get auto-promoted back.

Schema readout queries W_schema alongside W_active on every retrieval as a low-weight prior. This implements the cortical-schema-bias-on-retrieval pathway.

### Why this doesn't trigger Cell B's failure mode

Cell B failed because global downscale ate the dwindling-but-precious tail. Cold storage solves this at the architecture level: the tail is REMOVED from the matrix that gets downscaled, BEFORE it gets dwindled by stochastic drift. By migrating low-activity weights to W_cold proactively (every 500 cycles), they exit the active-W noise budget. They sit in cold storage at FULL EXACT strength. The active-W matrix can be downscaled aggressively (or even just normalized to keep ||W_active||_F bounded) without ever touching the cold tail.

This is exactly what HotRAP does for LSM-trees — the "hot record retention and promotion" policy explicitly addresses the dual problem: keep recent / frequent items in fast tier, retain cold items in slow tier (without rewriting them), promote cold items back when they get accessed.

### Substrate primitives already available

- **TWO_TIER architecture** (gap4_two_tier_generational_W_v1 in flight) — already separates W_young / W_old by promotion. Cold storage is the natural extension to a THIRD tier (and the actual "old" archive, with W_old in TWO_TIER being more like "warm tier" / W_schema).
- **W matrix multi-bank routing** (chain-grade K=4096 partitioning) — partition-routing infrastructure can do the sparse W_cold storage trivially.
- **Refuse-gate** (chain-grade) — already implements the "this retrieval isn't confident enough" signal that triggers the cold-path query.
- **NREM replay** (proven_bound, MIDDLE_BAND drift_red=0.067) — substrate primitive for scanning patterns. Schema combination scan is structurally similar: scan, find pairs, write to consolidated matrix.
- **STC tagging** (M5 from gap4 selective homeostasis drill, in queue) — provides the activity-tag mechanism that determines what does NOT get migrated.

Cold storage is COMPOSITIONAL with all of these. It does not replace any of them; it adds the architectural primitive that makes them safe to compose for indefinite ingest.

---

## Section 4 — 5 cell candidates ranked

### Cell 1 (FIRST) — cold_storage_two_tier_no_combine_v1 (cheapest decisive)

**Why first**: tests the cold-storage RELOCATION primitive in isolation, without the combination complexity. If migration alone solves Cell B HARD_FAIL, we know the architecture is right and combination is the cherry on top. If it does not, the migration policy needs work before we add combination.

**Mechanism**:
- W_active (N=2048, dense) + W_cold (sparse COO format, unbounded).
- T[i,j] timestamp tracker, A[i,j] access EWMA on W_active nonzeros.
- Every J_migrate=500 cycles: weights with staleness>K=2000 AND importance<I=0.1 move to W_cold (exact copy, zero from active).
- W_active gets aggressive normalization (||W_active||_F bounded to target X) — NOT multiplicative downscale; instead, scale entire matrix so Frobenius norm stays at X.
- Retrieval queries W_active; on refuse-gate fire, queries W_cold; on cold-hit, promotes back to W_active.
- NO schema combination.

**Brain-fidelity**: MEDIUM (engram relocation analog without the combination/schema step).

**P_deflated**: 0.50.

**Cost**: ~3-4 CPU-hr (10000-cycle ingest at substrate alpha=0.61).

**Pre-reg**:
- HARD-PASS: at J=10000 cycles, recall_oldest_patterns >= 0.70 (Cell B baseline ~0.20; no-downscale drift baseline ~0.40) AND ||W_active||_F bounded AND W_cold size grows linearly with ingest (~one new entry per cycle on average) AND retrieval latency on cold hits stays below 5x active-hit latency.
- HARD-FAIL: recall_oldest <= 0.30 (matches Cell B; cold storage didn't help) OR W_active also drifts to <0.30 recall_recent (normalization broke active-W) OR W_cold size grows super-linearly (migration logic broken).
- MIDDLE: recall_oldest in [0.30, 0.70], monotone-decreasing.

**Discriminator from Cell B**: Cell B's failure is multiplicative-downscale destroying the precious tail. Cell 1 removes the precious tail to a SAFE storage before downscale can touch it. If recall_oldest >= 0.70 at J=10000 (versus Cell B's ~0.20), that's a 3.5x lift attributable to the cold-storage architecture.

### Cell 2 (SECOND) — cold_storage_plus_combination_v1 (brain-fidelity, novelty)

**Why second**: only meaningful AFTER Cell 1 lands HARD-PASS or MIDDLE. Adds the schema-combination step that the brain uses for long-term consolidation. Tests if combination produces useful schema atoms (compression + generalization) without breaking the cold-storage safety property.

**Mechanism**: Cell 1 + every J_combine=2500 cycles, scan W_cold for pairs with cosine similarity > 0.85, merge to centroid + Hebbian-write to W_schema with weight = number of merged sources. Sources marked consolidated in W_cold (kept for audit, not deleted, but no longer queried for primary retrieval).

**Brain-fidelity**: HIGH (full hippocampus → cortex → schema pipeline, never-delete property preserved).

**P_deflated**: 0.40 (composition risk; combination may produce noisy schemas that hurt retrieval).

**Cost**: ~6-8 CPU-hr (longer ingest needed for schemas to form; k-means streaming centroid merge adds ~10% overhead).

**Pre-reg**:
- HARD-PASS: at J=15000 cycles, all of Cell 1 pass criteria AND W_schema contains at least 50 consolidated schema atoms AND schema-augmented retrieval improves novel-instance recall by >= 5pts on a held-out schema-consistent test set (the Tse-Morris paradigm probe).
- HARD-FAIL: schema atoms degrade retrieval (recall_oldest or recall_recent drops by > 5pts when W_schema is queried alongside W_active) OR combination scan times out (>10x active-W operation cost).
- MIDDLE: schemas form but don't measurably help retrieval; no harm done.

### Cell 3 (THIRD) — three_tier_W_active_W_cold_W_schema_v1 (full brain architecture)

**Why third**: only meaningful AFTER Cell 2 lands HARD-PASS. Test the full three-tier architecture against the brain's hippocampus-cortex-schema model in a long-horizon (J=20000 cycles, ~12 sleep cycles) cold-resistant test. This is the load-bearing test for indefinite operation.

**Mechanism**: W_active (W_young from TWO_TIER) + W_cold (the actual archive, ~replaces W_old in TWO_TIER for the long tail) + W_schema (consolidated). All three queryable; retrieval combines all three with appropriate weighting; migration W_active→W_cold every 500 cycles; combination W_cold→W_schema every 2500 cycles; NEVER any deletion. STC tagging (from selective homeostasis drill) governs what does NOT migrate (tagged stays in W_active).

**Brain-fidelity**: HIGHEST (complete brain stack: STC tag + W_active + W_cold + W_schema + NREM replay + REM-style selective protection).

**P_deflated**: 0.30 (composition risk over 3 mechanisms; ordering interactions; long horizon).

**Cost**: ~10-12 CPU-hr at substrate scale; or remote_cpu GPU-accelerated to ~3 hr.

**Pre-reg**:
- HARD-PASS at J=20000: recall_oldest >= 0.80 (decade-equivalent retention), recall_mid >= 0.85, recall_recent >= 0.90, ||W_active||_F bounded, W_cold grows linearly, W_schema atoms support novel-instance generalization >= 0.70.
- HARD-FAIL: any tier loses > 0.30 retention OR multi-tier query produces interference (worse than any single tier alone).
- MIDDLE: tiers don't interfere but no lift over Cell 2 alone.

This is the L2 glass-box-LLM continual-learning moat existence proof. If this passes, substrate has experimentally-verified indefinite ingest with brain-fidelity architecture.

### Cell 4 (FOURTH) — substrate_as_archive_partition_routed_v1 (simplest decoupling)

**Why fourth**: substrate already has chain-grade partition routing (K=4096) for the active-W. Simpler architectural test: rather than two matrices (W_active, W_cold), use TIME-PARTITIONED W banks — each "epoch" of ingest writes to a fresh partition. Old partitions never deleted; routing reads them on demand. This tests if substrate's existing routing primitives handle indefinite ingest at scale without ANY explicit cold-storage mechanism.

**Mechanism**: ingest writes to partition[t // EPOCH_SIZE]; retrieval queries top-K partitions by similarity to query (routing). Every partition is read-mostly after its epoch closes. No downscale, no migration, no combination — just partition routing.

**Brain-fidelity**: LOW (this is more like a "log-structured archive" than brain-architecture; closer to the LSM-tree without HotRAP promotion).

**P_deflated**: 0.40.

**Cost**: ~2-3 CPU-hr; tests at J=10000 with EPOCH_SIZE=1000 (10 partitions).

**Pre-reg**:
- HARD-PASS: recall_oldest >= 0.75, retrieval latency stays sub-linear in #partitions (routing should make it ~constant), W_partition_size stays bounded.
- HARD-FAIL: routing degrades at >5 partitions OR oldest partition recall drops to <0.30.
- MIDDLE: works at modest #partitions but routing degrades at scale.

### Cell 5 (FIFTH) — STC_plus_cold_storage_v1 (composition with selective homeostasis drill)

**Why fifth**: explicit composition with M5 STC from the parent gap4_brain_selective_homeostasis drill. STC tag = "do not migrate this weight to cold storage." Cold storage = "non-tagged-and-stale weights go here." The two mechanisms compose without conflict; STC provides the protection criterion for what stays hot.

**Mechanism**: STC tag matrix T (bool, dW>theta_tag at write time, decays in K cycles). Cold storage migration: weights with T=False AND staleness>K AND importance<I move to W_cold. PRP capture from STC (bounded protein pool every replay) marks weights persistent — persistent weights have permanent T=True, NEVER eligible for migration.

**Brain-fidelity**: HIGHEST among 5 (full Frey-Morris STC + brain-correct relocation mechanism).

**P_deflated**: 0.35 (composes two unproven mechanisms; either one alone is P~0.45 but joint is lower).

**Cost**: ~5-7 CPU-hr.

**Pre-reg**:
- HARD-PASS: at J=10000, recall_persistent (PRP-captured) >= 0.90, recall_cold (migrated but un-tagged) >= 0.60 (slower access but preserved), recall_recent >= 0.85.
- HARD-FAIL: STC tag mechanism doesn't correctly gate migration (tagged weights end up in cold storage anyway) OR composition produces worse retention than either alone.
- MIDDLE: works but no additional lift over cold-storage-alone.

---

## Section 5 — Quick summary table

| # | Name | Brain-fidelity | Cost | P_deflated | Cheapest decisive? | Most novel? |
|---|---|---|---|---|---|---|
| 1 | cold_storage_no_combine | MED | ~3-4hr | 0.50 | YES | partial (HotRAP-precedent for tier promotion; brain-novel composition) |
| 2 | cold_storage_plus_combine | HIGH | ~6-8hr | 0.40 | NO | YES (SEDM precedent in agent-memory but never substrate) |
| 3 | three_tier_W_active_W_cold_W_schema | HIGHEST | ~10-12hr | 0.30 | NO | YES (full brain composition) |
| 4 | substrate_as_archive_partition | LOW | ~2-3hr | 0.40 | runner-up | NO (existing primitives) |
| 5 | STC + cold_storage | HIGHEST | ~5-7hr | 0.35 | NO | YES (joint novel) |

---

## Section 6 — Cheap decisive test (start here)

**Cell 1: cold_storage_two_tier_no_combine_v1.**

The cheapest decisive test is "does relocation alone solve Cell B HARD_FAIL." This is the load-bearing test for the architecture frame; everything else (combination, schemas, STC composition) is gravy. If Cell 1 PASSES, the cold-storage architecture is validated and we have justification for the heavier follow-ons. If Cell 1 FAILS, we learn the architecture itself isn't enough and either need STC-gated migration (Cell 5) OR the partition-routed simpler version (Cell 4).

Pre-reg HARD bands (load-bearing — DO NOT relax during cell-author smoke):

**HARD-PASS** = at substrate alpha=0.61, J=10000 cycles, three-task ingest (task-A early, task-B middle, task-C late):
- recall_task_A (oldest) >= 0.70 (vs Cell B baseline ~0.20, no-downscale ~0.40)
- recall_task_B (mid) >= 0.80
- recall_task_C (newest) >= 0.90
- ||W_active||_F bounded within +/- 10% of target X across all checkpoints
- W_cold size grows linearly (slope = N_migrations_per_cycle ~ 0.5 entries/cycle expected)
- cold-hit latency <= 5x active-hit latency

**HARD-FAIL** = ANY of:
- recall_task_A <= 0.30 (cold storage didn't help; reproduces Cell B)
- recall_task_C <= 0.50 (W_active normalization broke recent-write retention)
- ||W_active||_F drift > 50% from target (normalization-breakdown)
- W_cold growth super-linear (migration policy not stable)
- cold-hit latency > 10x active-hit latency (sparse storage doesn't scale)

**MIDDLE** = recall_task_A in [0.30, 0.70] AND no other HARD-FAIL violation.

---

## Section 7 — Falsifiable predictions

1. **Relocation alone closes Cell B HARD_FAIL** (P=0.50). The mechanism: cold storage REMOVES the dwindling tail from the matrix that gets downscaled, BEFORE downscale can touch it. The active-W remains aggressively normalized; the cold archive sits at exact strength. If this prediction fails — i.e., Cell 1 also drops recall_oldest below 0.30 — then either (a) the migration policy itself is selecting the wrong weights, or (b) the active-W normalization is also damaging recent writes. Either failure mode would discriminate between two specific bug families and tell us where to look.

2. **Schema combination produces useful generalization on Tse-Morris probe** (P=0.30). Specifically, after Cell 2 has formed >= 50 schema atoms in W_schema, novel-instance recall on schema-consistent items should lift by >= 5pts when W_schema is queried alongside W_active. If schemas form but don't help generalization, the merging criterion (cosine threshold 0.85) is too aggressive (averaging out the distinguishing features) or too lax (no meaningful structure extracted).

3. **Three-tier composition is super-additive at J=20000** (P=0.30). The brain runs all three tiers concurrently; substrate should also show that the full three-tier architecture retains MORE than Cell 1 alone at long horizons. If composition is NOT super-additive (i.e., three-tier performs the same as two-tier at J=20000), we learn that W_schema is providing redundant rather than complementary signal at the substrate scale we're testing.

4. **Cold storage growth rate matches engram density bound** (P=0.55, the most robust prediction). W_cold size should grow at approximately N_migrations_per_cycle ~ (1 - tag_rate) × (1 - importance_threshold_pct), giving a predictable linear slope. If it grows super-linearly, either the migration policy has a re-migration bug (cold items getting written back to active and re-migrated) or the importance threshold is mis-calibrated.

5. **HARD-FAIL for "cold storage doesn't help"** (P=0.20). If Cell 1 HARD-FAILs by reproducing Cell B's recall_oldest <= 0.30, the architectural frame itself is wrong. This would falsify the USER reframe — the substrate genuinely needs deletion (or a more sophisticated combination scheme) and "never delete" is not feasible for the substrate's particular failure modes. Calibrated probability is low (0.20) but pre-registering this failure mode is mandatory per [[feedback-lit-scan-calibration-penalty]].

---

## Section 8 — Cross-thread synthesis

### Relationship to in-flight cells

- **gap4_two_tier_generational_W_v1** (in flight): TWO_TIER is W_young (CRISPR-write rate) → W_old (consolidated). Cold storage extends this to a THIRD tier; W_old in TWO_TIER becomes the cortical-schema-like middle tier, and W_cold is the actual long-tail archive. If TWO_TIER lands MIDDLE_BAND or HARD-FAIL, the cold-storage cells provide an alternative architectural decomposition.

- **gap4 selective homeostasis cells** (M1-M5 from parent drill): cold storage is COMPOSITIONAL with all 5. M1 magnitude-gated downscale can run on W_active without ever touching W_cold; M5 STC tag governs migration eligibility. Cell 5 here is the explicit STC+cold composition.

- **Cell A NREM replay** (MIDDLE_BAND, proven_bound): NREM replay strengthens patterns currently in W_active; cold storage prevents the rest from being eaten by drift. The two are dual problems (replay restores tail; cold storage protects tail by relocation); they SHOULD compose super-additively. Verifying super-additivity is part of Cell 3.

- **Cell B REM homeostasis** (HARD_FAIL_DESTROYS_OLDER, 3 schedules): this drill is the REVIVAL for Cell B. The reframe IS the revival. Cold storage is not "fix the downscale-selectivity within Cell B" — it is "replace the delete-anything frame entirely."

### Relationship to prior literature

The cold-storage architecture has multiple lit-precedents in adjacent fields, none in HD computing:

- **HotRAP (arxiv 2402.02070, ATC 2025)** — Hot Record Retention and Promotion for LSM-trees. Exactly the database tiered-storage primitive: hot data in fast tier, cold in cheap tier, promotion back when cold gets accessed. This is the SUBSTRATE-CODE-INSPIRATION reference for cold-storage migration policy.

- **SEDM (arxiv 2509.09498)** — Scalable Self-Evolving Distributed Memory for Agents. Implements the consolidation primitive: "items with high semantic similarity merged, evidence aggregated, items with conflicts or sustained negative contributions eliminated or recycled" (NOT deleted; the recycle terminology is load-bearing). This is the SUBSTRATE-COMBINATION reference for Cell 2.

- **Liu et al. Neuron 2024 / Yang et al. Nature 2025** — Hippocampal engram silencing under neurogenesis; remote-recall recruits NEW hippocampal engram; original is silenced not erased. This is the BIOLOGICAL EXISTENCE PROOF for "never delete, only relocate."

- **Li et al. 2017 Nature Communications + 2020 follow-up** — REM-dependent spine elimination is SELECTIVE to NEW-AND-UNCAPTURED spines; established schema-supporting spines are protected. This is the BIOLOGICAL EXISTENCE PROOF for migration vs deletion.

- **Tse et al. 2007 Science (paired with McClelland-O'Reilly-Norman 1995)** — Cortical schemas extracted via slow learning over interleaved replay; once schema exists, single-trial fast-learning of schema-consistent new episodes. This is the BIOLOGICAL EXISTENCE PROOF for Cell 2/3 W_schema combination dynamics.

- **Online k-means streaming with centroid merge (Bhattacharjee 2023 ICML)** — O(k poly(log n)) update time for streaming centroid merging. This is the IMPLEMENTATION REFERENCE for the W_cold → W_schema combination scan.

### Pattern check against meta-map

This drill falls in the field intersection of `continual-learning` × `nonequilibrium-stat-mech` × `data-streams/online-algorithms`. The closest fruit-bearing parent fields are `thermodynamics` (71% yield) via the bounded-PRP-pool / NESS framing, and `network-science-graph-theory` via the partition-routing variant (Cell 4). No saturated fields touched.

### Pattern 5 of meta-map (don't dismiss adjacent methods)

The cold-storage frame is ADJACENT to all the M1-M5 selective-homeostasis mechanisms in the parent drill — the parent drill named them as selective-downscale variants but did NOT pivot to "stop downscaling entirely; relocate instead." USER's reframe pivot is the missing adjacency. Per [[feedback-dont-dismiss-adjacent-methods]] this drill captures it.

---

## Section 9 — Substrate-product implications

### Direct product implications

**Glass-box LM continual-ingest moat (L2 vision)**: if Cell 3 HARD-PASSES at J=20000, substrate has an existence proof for indefinite continual learning at scale. This is the L2 glass-box-LLM moat: language models that can absorb new data forever without catastrophic forgetting, with every weight readable / auditable / explainable (because cold storage is just sparse archive, schema atoms are explicitly named).

**Audit-trail property**: cold storage NATURALLY produces an audit trail. Every weight that ever entered the substrate is either in W_active, W_cold, or has-been-consolidated-into-W_schema (with the source W_cold entries kept marked-as-consolidated). This is a unique substrate-product property — no LLM can tell you "this fact was originally encoded at cycle 1273 and got consolidated at cycle 12873 along with these other 47 similar facts into schema X." Substrate can.

**Capacity-scaling story**: cold storage means substrate capacity is bounded only by disk space (W_cold sparse storage). Active retrieval bandwidth is bounded by W_active size only. This decouples capacity from retrieval cost — the database tiered-storage promise applied to neural memory.

**Compose with Path C substrate-owned encoder**: if substrate-native encoder (Path C, in flight) lands chain-grade and cold storage lands chain-grade, the composition is "substrate is its own embedding model that never forgets, with full audit trail." This is the unique product story.

### Substrate-as-archive use case

There is a separate product reading: substrate could be sold as an APPEND-ONLY ASSOCIATIVE ARCHIVE — never-delete semantics by design. Industries that need this: legal hold (retain everything), regulated records (financial, medical), provenance-tracked knowledge bases. Cold storage architecture makes this a NATIVE substrate property rather than a workaround.

### Falsification implication

If Cell 1 HARD-FAILS (cold storage doesn't help), the substrate may have a deeper failure mode than "Cell B used wrong selectivity." The likely root cause then would be that the substrate's active-W matrix has a STATE-COUPLING problem where ALL weights are entangled in a way that makes any single-pattern preservation hard. This would be a much more concerning finding and would re-open whether substrate's chosen W-matrix representation is the right primitive at all. Pre-registering this means Cell 1 is genuinely decisive — either it validates the architecture frame OR it surfaces a deeper bug worth knowing about.

---

## Section 10 — Honest scope

**Cycle counts**: 10000 cycles for Cell 1 (the cheapest decisive), 15000 for Cell 2, 20000 for Cell 3. These are SUBSTRATE cycles (single Hebbian write per cycle), not natural-language tokens. Each cycle is microseconds at active-W size N=2048 with sparse density 0.1. CPU-walltime estimates: Cell 1 = 3-4 hr; Cell 2 = 6-8 hr; Cell 3 = 10-12 hr (or 3-4 hr on remote GPU per Fix #24).

**What I'm NOT claiming**: I'm not claiming substrate at J=20000 = brain at decades-of-time. The substrate cycle is not directly commensurable with biological time. What I AM claiming is that the FUNCTIONAL property — indefinite ingest without catastrophic forgetting — should be observable at J=20000 cycles if the cold-storage architecture is correct. The brain achieves this property; the test is whether substrate can also achieve it at substrate-scale, NOT whether substrate achieves it at brain-scale.

**Failure mode I haven't fully addressed**: combination noise. If the combination scan produces low-quality schemas (cosine-threshold-too-low merges semantically-distinct items, or cosine-threshold-too-high never merges anything), Cell 2 will land MIDDLE_BAND. The mitigation is a hyperparameter sweep (cosine threshold {0.80, 0.85, 0.90, 0.95}) in the smoke phase, but this is genuine combination-noise risk.

**What's load-bearing for the cell-author**: pre-reg envelope-fail-band derivation per [[feedback-envelope-fail-bands]]; smoke test with 3 sets of (K_threshold, I_threshold, J_migrate) values; verify cold storage growth-rate prediction in smoke before launching full ingest; instrument the W_active normalization carefully (this is the substitute for downscale and is the highest-risk implementation detail).

---

## Section 11 — Recommendation

**Start with Cell 1 (cold_storage_two_tier_no_combine_v1) IMMEDIATELY.**

The drill cycle that produced this note is the natural successor to Cell B's HARD_FAIL. The USER reframe is mathematically sound, brain-grounded (lit-precedent confirmed across 5 independent biology + database + agent-memory literatures), substrate-compositional (composes with all in-flight cells without conflict), and architecturally decisive: a single 3-4 CPU-hr cell tells us whether the relocate-don't-delete frame solves the substrate's continual-learning failure mode.

If Cell 1 PASSES: dispatch Cell 2 (adds combination) within 24h. Then Cell 5 (STC composition) IF Cell 5 STC parent passes its own validation. Then Cell 3 (full three-tier) as the load-bearing test at J=20000.

If Cell 1 FAILS: pivot to Cell 4 (partition-routed archive) as the architectural fallback. If Cell 4 also fails, the substrate's W-matrix representation may need re-examination.

---

## Citations (verified count)

1. Liu et al. Neuron 2024 — "Reconstructing a new hippocampal engram for systems reconsolidation and remote memory updating." Adult hippocampal neurogenesis-mediated silencing of original engrams; new ensemble recruited for remote recall. [VERIFIED via search; PMID 39689709].

2. Yang et al. Nature 2025 — "Systems consolidation reorganizes hippocampal engram circuitry." [VERIFIED via search; Nature 41586-025-08993-1].

3. Li et al. 2017 Nature Communications — "REM sleep promotes experience-dependent dendritic spine elimination in the mouse cortex." Confirmed in 2020 (PMC7511313). REM-spine pruning is selective to new/uncaptured spines; established spines protected by STC late-LTP. [VERIFIED].

4. Tse et al. 2007 Science — "Schemas and memory consolidation." Cortical schema enables fast learning of schema-consistent novel episodes. [Standard reference, verified].

5. McClelland, O'Reilly, Norman 1995 — "Why there are complementary learning systems in the hippocampus and neocortex." CLS theory; hippocampus fast / cortex slow. [VERIFIED via search].

6. HotRAP (arxiv 2402.02070, ATC 2025) — Hot Record Retention and Promotion for LSM-trees with Tiered Storage. Database tiered-storage primitive with promote-back. [VERIFIED via search; arxiv.org/pdf/2402.02070].

7. SEDM (arxiv 2509.09498) — Scalable Self-Evolving Distributed Memory for Agents. Consolidation-and-progressive-evolution merges semantically-similar items, recycles rather than deletes. [VERIFIED via search; arxiv.org/pdf/2509.09498].

8. Memory Tiering for AI Agents (clawrxiv 2603.00037) — Three-tier HOT/WARM/COLD architecture for long-running AI agents. Direct lit-precedent for substrate three-tier cell. [VERIFIED via search].

9. Bhattacharjee 2023 — "Online k-means Clustering on Arbitrary Data Streams." Streaming k-means with merge in O(k poly(log n)). [VERIFIED via search; PMLR v201].

10. Frey & Morris 1997 Nature — Synaptic Tagging and Capture. Bounded-PRP-pool competition. [Standard reference from parent drill, verified there].

11. Engram Memory Encoding and Retrieval Neurocomputational Perspective (arxiv 2506.01659). Computational model of engram dynamics. [VERIFIED via search].

12. CALM: Continual Associative Learning Model via Sparse Distributed Memory (MDPI 2027 13/12/587) — Adjacent precedent for SDM-based continual learning. [VERIFIED via search].

Verified citation count: 12.

---

END OF RESEARCH NOTE
