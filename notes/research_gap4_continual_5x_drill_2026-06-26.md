# RESEARCH 5x DRILL: GAP 4 -- long-term continual operation at 5000+ cycles with repair

**Date:** 2026-06-26
**Requestor:** Director (gap-4 deep drill; cross-domain disparate-fields)
**Empirical anchor on substrate:**
- `a8_continual_writes` HARD_PASS at 200 cycles, alpha=0.30 (1.5x Hopfield capacity), forget=0.006
- `substrate_continual_kv_n32768_120_sessions` chain-grade at 120 production-scale sessions
- Cell A NREM-replay smoke MIDDLE_BAND drift_red=0.067 (borderline FAIL/MIDDLE)
- Cell B REM-homeostasis smoke HARD_FAIL_DESTROYS_OLDER (small regime)
- NO 5000-cycle test yet; Cell A pending at N=4096 / 2500 cycles / alpha=0.61 (4.4x Hopfield)
**Companion drills:** brain CLS replay drill (2026-06-22; primary cell c1); SWR 5x drill (2026-06-22); architectural revival 2x (2026-06-24)
**Lit-scan calibration:** deflate P 0.15-0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.

---

## HEADLINE -- intuitive first (Fix #13)

**The substrate's continual story is correct in DIRECTION but UNDER-MECHANISMED in COUNT.** Cell A (NREM replay) and Cell B (REM homeostasis) implement the two best-known biological mechanisms; both smoke MIDDLE/FAIL. **Biology uses ~8 distinct stacked mechanisms, each tuned to a different timescale (hours / days / weeks / years), and the substrate has tried 2 of 8 mostly in isolation.** The brain doesn't survive decades by doing ONE thing better -- it survives by doing eight things simultaneously, each catching forgetting at a different stage of the consolidation pipeline. **The disparate-fields lens converges on the same prescription as biology**: distributed storage systems (LSM tree, generational GC), spin-glass physics (aging/rejuvenation memory effects), continual-learning ML (EWC / GEM / SI), and dynamical systems theory (Lyapunov stability, Ornstein-Uhlenbeck mean reversion) all independently arrived at the SAME design: **tiered storage + per-item importance-weighted protection + periodic compaction + bounded-drift stabilizer + sparse re-allocation of fresh capacity**.

**Novel synthesis the substrate has not tried**: a **GENERATIONAL substrate** -- a young / old W-matrix split with a write-barrier (BCM-like metaplasticity threshold) gating promotion. This is the exact analog of (a) JVM weak-generational-hypothesis GC, (b) RocksDB leveled compaction (L0 -> L1 -> ... -> L6), (c) immune-system germinal-center maturation (naive B -> memory B -> long-lived plasma), and (d) brain hippocampus -> cortex consolidation. Each independently evolved/engineered system uses the same factorization. **The substrate's W matrix is currently a SINGLE-TIER store -- this is the structural cap.**

**Cheap decisive test:** add a second W matrix (W_old) initialized at 0; ingest into W_young; periodically (every M_cycles=100) PROMOTE the highest-importance entries to W_old and DOWNSCALE W_young by gamma=0.95. Importance score = BCM-threshold-passed (entry has been re-accessed during recent replay) OR refuse-gate-confirmed (passes OOD check). Measure forgetting curve over J=2500 cycles. **HARD-PASS bar = task-A recall at cycle=2500 >= 0.80 with two-tier (vs <=0.30 with single-tier baseline at alpha=0.61)**. If two-tier rescues, the substrate has its compaction architecture.

**Top 5 ranked for IMMEDIATE dispatch (compute-cheap, mechanically substrate-native, decision-grade discriminator):**

| Rank | Anchor | Field | P_deflated | Cost (CPU-hr) | Why now |
|------|--------|-------|------------|---------------|---------|
| 1 | **two_tier_generational_W_v1** | distributed-systems + immune + brain CONVERGENT | 0.50 (cap) | ~3 | Three independent fields predict the same architecture; substrate has only single-tier today; addresses the 4.4x-Hopfield regime directly |
| 2 | **bcm_metaplasticity_threshold_gate_v1** | computational-neuroscience | 0.40 | ~2 | Per-weight sliding threshold theta_M = <w^2>_recent gates new writes; biologically equivalent to SNAP but with calcium-based dynamics; substrate-native (W stats already computable) |
| 3 | **neurogenesis_capacity_refresh_v1** | biology + distributed-systems | 0.35 | ~4 | Periodically allocate FRESH N_DIM dimensions and migrate old patterns into them (immune-system clonal expansion analog); breaks the alpha-cliff by extending denominator |
| 4 | **lsm_leveled_compaction_W_v1** | databases + brain | 0.35 | ~3 | L0/L1/L2 tiered W matrices with size-tiered merge; controls write-amplification while preserving read-latency; quantifies a substrate "compaction cost" the brain pays in NREM |
| 5 | **lyapunov_OU_mean_reversion_v1** | dynamical-systems + spin-glass | 0.35 | ~2 | W_t mean-reverts to a slowly-moving prototype; provably bounded drift under continual update; no replay needed; one-line update rule |

---

## THE 15-20 CANDIDATE LANDSCAPE (15 finalists from ~22 scanned mechanisms)

Each row: field x mechanism x substrate-mapping x discriminator x P_solve x compute.

### Theoretical neuroscience (DEEPER)

**M1. SHY (Tononi-Cirelli synaptic homeostasis hypothesis).** *Mechanism:* global multiplicative downscale of ALL synapses during NREM, preserving RELATIVE strength but reducing absolute. Kinetics from electrophysiology: ~10-20% reduction overnight; ~6-8 hour recovery to baseline during waking. *Substrate map:* W *= gamma_shy (0.85-0.95) every J cycles, with NO subset selection. *Discriminator:* HARD-PASS = SHY-applied substrate at alpha=0.61 retains task-A recall >= 0.70 at cycle=2500 vs <= 0.30 baseline; HARD-FAIL = SHY <= baseline+0.05. *Substrate prior:* Cell B (REM homeostasis = global downscale) was tried and HARD_FAIL_DESTROYS_OLDER. *Verdict:* DEPRIORITIZE -- already tried in pure form. Compose only with selective per-item gates (M2/M3).

**M2. BCM metaplasticity (Bienenstock-Cooper-Munro sliding threshold).** *Mechanism:* per-weight LTP threshold theta_M = <w^2>_recent (quadratic in recent activity); writes ABOVE threshold trigger potentiation, writes BELOW trigger depression. The threshold *slides* with activity history. *Substrate map:* maintain per-weight EWMA of |w|^2; gate new Hebbian writes by sigmoidal(|w_new| - theta_M). *Discriminator:* HARD-PASS = BCM-gated substrate at alpha=0.61 retains task-A recall >= 0.75 at cycle=2500 vs baseline 0.30; HARD-FAIL = delta <= 0.10. *Substrate prior:* SNAP sigmoidal-weight rule (Cell B sibling) is a relative; BCM differs in that threshold ADAPTS to recent activity (truly metaplastic, not static sigmoid). *P_deflated: 0.40.* Cost: ~2 CPU-hr.

**M3. Memory engram theory (Tonegawa optogenetic ensembles).** *Mechanism:* a specific memory lives in a SPECIFIC, IDENTIFIABLE neural ensemble; the ensemble persists for >=8 days under protein-synthesis-block; engrams are SPARSE (~2-5% of DG cells per memory). *Substrate map:* assign each ingested fact a sparse k-WTA codebook entry (ensemble); engram-tag at write; protect tagged entries from replay overwrite via importance-mask. *Discriminator:* HARD-PASS = engram-tagged substrate retains tagged-fact recall >= 0.90 at cycle=2500. *Composes with*: k-WTA (drill #1) + BCM (M2). *P_deflated: 0.35.* Cost: ~3 CPU-hr.

**M4. Memory reconsolidation (Nader-LeDoux retrieval window).** *Mechanism:* retrieval of a consolidated memory makes it transiently LABILE for ~6 hours; new protein-synthesis-dependent restabilization required; allows UPDATING. *Substrate map:* on substrate READ, re-write the retrieved pattern with a small additive perturbation; reconsolidate before next read. *Discriminator:* HARD-PASS = reconsolidation rescues stale entries (entries inactive >M cycles get refreshed on read) at >= 0.75 recall. *Substrate-novel angle:* could be a CHEAP refresh mechanism that piggybacks on natural query traffic (no separate replay scheduler). *P_deflated: 0.25.* Cost: ~2 CPU-hr.

**M5. Adult neurogenesis (Aimone-Gage decorrelation by new DG cells).** *Mechanism:* fresh granule cells (born adult, 700/day in human DG) integrate into circuits and DECORRELATE overlapping inputs; mature within ~6 weeks, then become indistinguishable. Reduces interference for new memories without disturbing old ones. *Substrate map:* periodically allocate FRESH N_DIM dimensions (W expansion); new patterns written ONLY to fresh dimensions for a "maturation window"; old patterns inhabit OLD dimensions exclusively. *Discriminator:* HARD-PASS = neurogenesis-substrate at alpha=0.61 retains both task-A and task-J >= 0.75 (no stability-plasticity tradeoff). *Cost*: ~4 CPU-hr (N_DIM grows ~10% per generation). *P_deflated: 0.35.*

**M6. Buzsaki bidirectional hippocampal-cortical dialog.** *Mechanism:* SWRs (200Hz, hippocampal) and slow oscillations (1Hz, cortical) couple BOTH directions: SWR-to-cortex (consolidation transfer) + cortex-to-SWR (semantic-context-cued retrieval). *Substrate map:* during replay, cortex W_old SAMPLES which entries to query, then U1 hippocampus REPLAYS the sampled entries. Two-way info flow. *Substrate prior:* one-way replay (U1 -> W) tried in Cell A; bidirectional is NEW. *P_deflated: 0.30.* Cost: ~3 CPU-hr.

**M7. Theta-gamma cross-frequency coupling (CFC) for encoding-vs-retrieval phase separation.** *Mechanism:* encoding happens at one theta-phase, retrieval at the OPPOSITE theta-phase; gamma-amplitude rides on theta-phase. Separates "are we writing?" from "are we reading?" cleanly. *Substrate map:* use a phase signal (cycle parity mod 2) to gate writes-vs-reads; alternate ingest-phase / replay-phase substrate cycles. *Discriminator:* HARD-PASS = phase-separated substrate shows higher retention than interleaved-write/read at same total work. *P_deflated: 0.25.* Cost: ~2 CPU-hr.

**M8. Astrocyte-mediated synapse pruning (C1q complement, weeks timescale).** *Mechanism:* astrocytes tag low-activity / "weak" synapses with complement C1q; microglia engulf tagged synapses; SLOW (weeks); structural -- removes synapses entirely. *Substrate map:* periodically (every 1000 cycles) ZERO-out W entries with magnitude below epsilon_prune; free the slot for re-use. *Discriminator:* HARD-PASS = pruned-substrate uses 40-60% fewer effective dimensions for same recall. *P_deflated: 0.25.* Cost: ~2 CPU-hr.

### Distributed systems / databases

**M9. LSM tree leveled compaction (RocksDB/LevelDB).** *Mechanism:* writes go to L0 (memtable); periodic compaction merges L0->L1->L2->...->Lk with non-overlapping key ranges per level; trades write-amplification for read-latency. *Substrate map:* W_L0 small fast Hebbian store; periodically merge into W_L1 (larger, less updateable); cascading to W_L2/L3. Each level has DOUBLED capacity and HALVED update rate. *Discriminator:* HARD-PASS = 3-level LSM-W at alpha=0.61 retains task-A >= 0.75; HARD-FAIL = no improvement over single W. *P_deflated: 0.35.* Cost: ~3 CPU-hr.

**M10. Generational GC (JVM weak generational hypothesis).** *Mechanism:* "most objects die young"; segregate young / old generations; collect young frequently (cheap), old rarely (expensive); use write barrier to track cross-generation pointers. *Substrate map:* W_young + W_old; promote W_young entries to W_old after K survival cycles; this IS the M1 ranked top of the table -- ranked #1 because three fields converge. *P_deflated: 0.50 (CAP).*

**M11. CRDT / vector-clock continual merge (Lamport).** *Mechanism:* replicated stores accept independent writes; merge deterministically with vector-clock causality. Eventual consistency guaranteed. *Substrate map:* parallel substrate replicas per task partition; deterministic merge into single W via element-wise max-of-magnitudes (CRDT G-set semantics). *Discriminator:* HARD-PASS = sharded substrate retains >= single-substrate recall AND scales N_DIM superlinearly. *Substrate-novelty:* SHARDING by task -- never tried. *P_deflated: 0.30.* Cost: ~5 CPU-hr (parallel replicas).

**M12. Working-set / LRU+LFU eviction (Denning).** *Mechanism:* track recency + frequency; evict items outside the working set when capacity tight. Tunable via TTL. *Substrate map:* maintain access-time + access-count per W slot; on full, evict (lowest access * recency) entry. *Discriminator:* HARD-PASS = LRU-evicted substrate at alpha=0.61 retains hot-keys (frequent) at >= 0.90 while gracefully losing cold-keys. *P_deflated: 0.30.* Cost: ~2 CPU-hr.

### Continual learning ML (covered in prior drills; included for completeness with deflated priors)

**M13. EWC + Fisher-information regularization (Kirkpatrick 2017).** *Mechanism:* approximate Bayesian update; quadratic penalty proportional to Fisher-diagonal of previous-task posterior. *Substrate map:* maintain a Fisher proxy per W entry (estimated as |w|^2 weighted by access-frequency); penalize new writes for high-Fisher entries. *Substrate prior:* tried implicitly in Cell B form (consolidation). *P_deflated: 0.25.* Cost: ~3 CPU-hr.

**M14. GEM / A-GEM (gradient episodic memory; Lopez-Paz).** *Mechanism:* maintain episodic memory of K past tasks; constrain new updates to not INCREASE loss on memory. *Substrate map:* on new write, check whether the write would degrade recall on a sampled set of old keys; project the write into the orthogonal complement if it would. *Substrate prior:* not tried -- substrate's Hebbian update is unconstrained. *P_deflated: 0.30.* Cost: ~4 CPU-hr.

**M15. Sparse coding for capacity (winner-take-all reduces interference).** *Mechanism:* sparse codes (k-WTA, f<<1) reduce overlap between patterns and exponentially reduce crosstalk. *Substrate prior:* k-WTA-VQ drilled in brain-drill #1; primary cell pending. *Verdict:* COMPOSE-WITH not standalone -- assumed compose-able with all others. *P_deflated: 0.40 standalone but DEDUP with drill #1.*

### Materials / physics

**M16. Spin-glass aging-rejuvenation (Vincent-Bouchaud trap model).** *Mechanism:* glassy systems show MEMORY effect -- relaxation history "remembered" upon reheating; aging proceeds via activated jumps between traps in hierarchical landscape. *Substrate map:* the Hebbian-W matrix at alpha > alpha_c IS a glass; the natural relaxation includes a slow consolidation channel that the substrate can EXPLOIT by alternating "heating" (high learning rate; explore) and "cooling" (low learning rate; consolidate). *Discriminator:* HARD-PASS = annealed-schedule substrate at alpha=0.61 retains >= 0.70 vs constant-eta baseline 0.30. *P_deflated: 0.35.* Cost: ~3 CPU-hr.

**M17. PCM resistance drift compensation (phase-change memory).** *Mechanism:* PCM amorphous-phase resistance increases logarithmically with time (drift coefficient 0.0001-0.11); compensation via non-linear current scaling reference. *Substrate map:* the substrate W ALSO drifts -- the per-entry magnitude decays under continual interference. Track per-entry "age" and apply a NON-LINEAR read-time compensation scaling. *Substrate-novelty:* read-time correction (not write-time consolidation). *Discriminator:* HARD-PASS = drift-compensated read recovers stale entries that uncompensated read misses. *P_deflated: 0.30.* Cost: ~2 CPU-hr.

**M18. Simulated annealing schedule (Kirkpatrick-Vecchi).** *Mechanism:* cooling schedule allows escape from local minima; rate ~ T_0 / log(t+1). *Substrate map:* learning rate eta_t = eta_0 / log(t+1); slow saturation prevents catastrophic late-cycle overwrites. *Substrate prior:* not tried -- eta is constant in current substrate. *P_deflated: 0.25.* Cost: ~1 CPU-hr (trivial).

### Pure mathematics / dynamical systems

**M19. Lyapunov stability + Ornstein-Uhlenbeck mean reversion.** *Mechanism:* if dW/dt = -k*(W - W*) + noise, then W stays in a bounded ball around the prototype W* with bounded variance. Provably stable under continual perturbation. *Substrate map:* maintain a slowly-updated prototype W* (long EWMA of W); add a mean-reverting term -k*(W - W*) to the update rule. *Discriminator:* HARD-PASS = OU-stabilized substrate at alpha=0.61 shows bounded forgetting <= 0.20 over 5000 cycles. *Substrate-novelty:* mean-reverting Hebbian -- not in any prior cell. *P_deflated: 0.35.* Cost: ~2 CPU-hr.

**M20. Markov chain stationary-distribution / Doeblin coupling.** *Mechanism:* continual stochastic update converges to a stationary distribution under spectral-gap conditions; mixing time = O(1/(1-lambda_2)). *Substrate map:* prove that the substrate's continual update is a Markov chain on W-space; identify the stationary distribution; deviations from stationary = "memory" content. *Use:* DIAGNOSTIC -- not a mechanism; tells us whether the substrate's continual operation has a well-defined long-time behavior at all. *P_deflated: 0.50 (mechanically applies).* Cost: 0 (analysis).

### Adjacent biology + other

**M21. Immune system germinal-center maturation (plasma cells / memory B cells).** *Mechanism:* naive B cells -> germinal center clonal expansion + somatic hypermutation -> long-lived plasma cells (in bone marrow) + recirculating memory B cells. The plasma cells continuously secrete antibody for DECADES. *Substrate map:* a "germinal center" SUB-substrate where new patterns undergo high-mutation-rate amplification + selection (refuse-gate as fitness); survivors PROMOTE to a long-lived "plasma" tier (substrate cousin of W_old). Strongly parallels M10 generational GC. *P_deflated: 0.30.* Cost: ~4 CPU-hr.

**M22. Online learning regret bound (OGD sqrt(T)).** *Mechanism:* online gradient descent achieves O(sqrt(T)) regret for convex losses, O(log T) for strongly convex. The substrate's continual update is roughly OGD with a Hebbian objective. *Use:* DIAGNOSTIC -- gives a theoretical floor on substrate forgetting (cannot beat sqrt(T) for general convex; cannot beat log(T) for strongly convex). *Substrate-action:* compute the substrate's effective "convexity modulus" -- if it's strongly convex, OGD predicts log(T) forgetting at 5000 cycles ~ 8.5 (manageable). *P_deflated: 0.45 (mechanically applies).* Cost: 0 (analysis).

---

## CHEAP DECISIVE TEST

**Primary cell: `gap4_two_tier_generational_W_v1` (rank #1 candidate)**

**Scope:** Add a second W matrix (W_old, same dimensions) alongside W_young. Ingest 5000 cycles of M=2000 facts each (total alpha at end = 5000*2000 / N_DIM^2 if quadratic-binding, or 5000*2000 / N_DIM for linear -- substrate is between). Every K_promote=100 cycles, promote top-tau-fraction (by importance score) entries from W_young into W_old via additive merge: W_old += W_young * mask; W_young *= gamma_decay (0.90). Importance = re-access count since last promotion + refuse-gate pass.

**Independent variables:**
- `tier_mode` in {SINGLE, TWO_TIER}
- `alpha_target` in {0.30 (baseline anchor), 0.61 (cliff test), 1.0 (post-cliff stress)}
- `K_promote` in {50, 100, 200}
- `tau_promote_fraction` in {0.05, 0.10, 0.20}
- `gamma_decay` in {0.85, 0.90, 0.95}
- `J_cycles` = 5000 (full long-horizon test)

**Fixed:** N_DIM=4096; 3 seeds (7, 17, 23); same Hebbian-superposition arithmetic; same refuse-gate from U1.

**Anchors (sanity replicates required):**
- alpha=0.30 SINGLE replicates a8 forget=0.006 (sanity).
- alpha=1.5 SINGLE replicates a8 acc=0.10 (capacity floor sanity).
- Cell A NREM-replay at alpha=0.61 reproduces drift_red=0.067 +/- 0.02 (Cell A sanity).

**Primary metric:** `task_A_recall_at_cycle_J` for J in {500, 1000, 2000, 3500, 5000} -- the long-horizon forgetting curve.

**Secondary metrics:**
- W_old vs W_young capacity utilization
- Promotion rate / SLA (how often does W_young promote? what fraction survives?)
- Read-latency per cycle (does TWO_TIER add measurable cost?)
- Refuse-gate fidelity (does promotion degrade refuse?)

---

## FALSIFIABLE PREDICTIONS (PRE-REGISTERED HARD-PASS / HARD-FAIL)

### Prediction 1 (PRIMARY) -- TWO_TIER rescues at alpha=0.61

**Hypothesis:** generational two-tier W matrix at alpha=0.61 retains task-A recall at cycle=5000 >= 0.75 vs SINGLE baseline <= 0.30.

**HARD-PASS:**
- task-A recall@5000 >= 0.75 with TWO_TIER
- task-A recall@5000 <= 0.30 with SINGLE (baseline confirmed)
- delta >= 0.40
- cv <= 0.10 across 3 seeds for both arms
- W_old shows >=50% capacity utilization at cycle=5000 (mechanism actually using both tiers)
- Read-latency overhead < 1.5x SINGLE
- Substrate-only-decode gate: zero LLM forward calls at ingest or eval (grep audit)
- Version-marker: `tier_mode`, `alpha_target`, `K_promote`, `tau_promote_fraction`, `gamma_decay` baked into metrics.json

**HARD-PASS-PLUS (super-pass):**
- At alpha=1.0 (post-cliff stress): TWO_TIER still retains >= 0.50 (raises usable alpha from 0.30 to 1.0)

**MIDDLE_BAND:**
- delta in [0.15, 0.40] -- mechanism real but smaller than predicted; tune K_promote / tau hyperparameters

**HARD-FAIL (mechanism wrong):**
- delta < 0.10 at alpha=0.61 -- two-tier does NOT rescue
- OR: TWO_TIER shows DEGRADATION (promotion corrupts W_old) -- promotion strategy mis-specified

**Calibrated P(HARD-PASS) = 0.50** (capped at novel-synthesis cap). Three independent fields (generational GC, RocksDB LSM, immune germinal-center) predict the same architecture works; substrate-specific composition with U1 + W untested.

### Prediction 2 (SECONDARY) -- BCM metaplasticity composes multiplicatively

**Hypothesis:** TWO_TIER + BCM (per-weight sliding threshold) extends usable alpha further to 1.5+ (true catastrophic-overload regime currently inaccessible).

**HARD-PASS:** at alpha=1.5, TWO_TIER+BCM task-A recall@5000 >= 0.50 (vs TWO_TIER alone <= 0.30).
**HARD-FAIL:** BCM adds < 0.05 over TWO_TIER at any alpha.
**Calibrated P: 0.30** (composition risk; BCM and TWO_TIER may interfere -- BCM gates writes, TWO_TIER promotes them; need to verify orderings).

### Prediction 3 (DIAGNOSTIC) -- Lyapunov-OU bounded drift in stationary regime

**Hypothesis:** the substrate's continual update with Lyapunov-OU mean-reverting term shows BOUNDED forgetting drift <= 0.20 over 5000 cycles even at alpha=0.61, but ALSO bounds NEW-LEARNING capacity at <= 0.80 (stability-plasticity tradeoff materialized as a hard ceiling).

**Use:** measures whether substrate has a well-defined stationary distribution; if YES, all long-horizon behavior is predictable from spectral analysis.

**HARD-PASS:** OU-substrate at alpha=0.61 shows forgetting variance < 0.05 across cycles 2000-5000 (i.e., reached stationary).
**HARD-FAIL:** OU-substrate continues to drift monotonically -- substrate is non-stationary.
**Calibrated P: 0.35.**

### Prediction 4 (REVIVAL ROUTE if HARD-FAIL) -- adopt neurogenesis as alternative

If TWO_TIER fails, the substrate's continual scaling is NOT a storage-segregation problem but a CAPACITY problem. Route to M5 neurogenesis: periodically EXPAND N_DIM (allocate fresh dimensions) and migrate old patterns. Substrate-cost: O(N_DIM) per generation; biologically validated.

### Prediction 5 (NULLABILITY BRACKET) -- at alpha=0.30 both arms reach baseline

**Hypothesis:** at alpha=0.30 (below cliff), SINGLE and TWO_TIER both achieve forget < 0.01 at cycle=5000 (a8 anchor reproduces).

**Purpose:** sanity bracket; confirms below-cliff is not where mechanism operates.
**HARD-FAIL:** if TWO_TIER HURTS at alpha=0.30 -- promotion strategy is destructive.

### Prediction 6 (ANALYSIS, no separate cell) -- OGD regret floor

**Hypothesis:** if the substrate update is a strongly-convex OGD, then forgetting at 5000 cycles cannot exceed O(log T) ~ 8.5 bits / 12 nats; if it's only convex, cannot exceed sqrt(T) ~ 70 bits. Whichever bound applies sets the THEORETICAL FLOOR for what any consolidation strategy can achieve.

**Use:** anchors HARD-PASS targets; if Cell A delta=0.067 is near the floor, no improvement is possible. If far from floor, room exists.

---

## CROSS-THREAD SYNTHESIS

### Composes with brain-drill #1 (k-WTA-VQ DG sparse separator)

- k-WTA at the WRITE path implements DG-style pattern separation; reduces per-write crosstalk.
- TWO_TIER + k-WTA: each tier benefits separately (less crosstalk in both W_young and W_old).
- M15 sparse-coding is a precondition: at alpha=0.61 with DENSE coding the substrate may already be at Hopfield capacity, leaving no headroom for generational tricks.

### Composes with brain-drill #2 (CLS replay; Cell A pending)

- Cell A NREM replay is M6's one-way direction (U1 -> W). MIDDLE_BAND drift_red=0.067.
- TWO_TIER provides the DESTINATION the replay lacks: replay into W_old (not W_young) so old memories live where they cannot be overwritten by new ingest.
- Predicted joint mechanism: NREM replay + TWO_TIER promotion = the canonical brain consolidation pipeline.

### Composes with substrate_continual_kv_n32768_120_sessions (CERT)

- 120-session production-scale chain-grade at N_DIM=32768 is the LARGEST anchor.
- Scaling to 5000 cycles is ~40x more cycles, ~12x more alpha. The substrate at 32768 dims has more headroom than 4096; the cliff timing may differ.
- TWO_TIER cell should be repeated at N_DIM=32768 if N_DIM=4096 lands HARD-PASS (Phase 2).

### Composes with Hebbian-superposition #7 (CERT 591) + U1 inference

- U1 multi-value KG = hippocampal-style episodic store at 50k scale.
- W matrix = cortex.
- TWO_TIER's W_old = the canonical "consolidated cortex"; W_young = the working-cortex layer that takes new writes hourly.
- U1 acts as REPLAY SOURCE -- sampled facts get re-Hebbian-bound into W_young, then promoted to W_old.
- The full architecture: U1 (hippocampus) + W_young (recent cortex) + W_old (consolidated cortex) + replay loop + BCM-gated promotion = brain consolidation pipeline implemented in substrate primitives.

### Composes with refuse-gate (U1 0.97 OOD-refuse)

- Promotion to W_old requires "high importance" -- refuse-gate provides the substrate-native validation: only promote entries that the refuse-gate still confirms correctly.
- This is the brain's "engram quality control" -- only consolidate validated memories.

### Composes with timeout-class revival drill (2026-06-24)

- 5000-cycle cells are LONG -- the 3-point roofline probe + atexit partial-results + per-seed checkpoint disciplines (D1/D2 from timeout drill) are MANDATORY here.
- Pre-dispatch: smoke at J=100 to estimate per-cycle wall; verify ~3 CPU-hr extrapolation for full 5000.

### Composes with gap-map transfer META revival (2026-06-24)

- Gap 4 transfer-risk was rated LOW. This drill REINFORCES that rating: the mechanisms are tier-orthogonal (storage), not regime-sensitive (capacity-cliff).
- 5000-cycle results SHOULD transfer to other corpora (FB15k, ConceptNet, Wikipedia), unlike e.g. Resonator which is anisotropy-bound.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. **Generational substrate IS the moat at production-scale.** Single-tier W is fine for demo (200 cycles) but breaks at production cadence (years of continual ingest). TWO_TIER + BCM + neurogenesis is the architecture that lets the substrate ingest forever without bounded-capacity collapse. This is the L2 glass-box-LLM precondition.

2. **The biology-engineering convergence is the strongest product claim available.** When generational GC, RocksDB LSM, immune system, and the brain all independently arrive at the same factorization, the architectural story is no longer "biology-inspired"; it's "isomorphic to the universal solution that emerged in 4 disparate evolutionary/engineering contexts." This is the substrate's distinctive product claim: tiered consolidation built INTO the primitive, not bolted on as a cache layer.

3. **5000-cycle test becomes the production-grade benchmark.** Single-shot capacity tests (Hopfield 0.138 alpha_c) are the wrong metric for a continual substrate. The right metric is forgetting-curve over 10x-100x more cycles than the cliff anchor. Every future continual-substrate cert should include this curve.

4. **Operator-cost mapping.** TWO_TIER, BCM, neurogenesis, LSM all impose per-cycle compute overhead. The substrate-product story should report these as the COST of decade-scale memory. Brain pays ~10W for these; substrate-LM pays ~1.5x baseline.

5. **The substrate's missing primitive is "promotion".** Every disparate-field analog (GC, LSM, immune system, brain consolidation) has an explicit PROMOTION operator. Substrate has REPLAY (Cell A) and HOMEOSTASIS (Cell B) but no PROMOTION. This is the architectural gap.

6. **Lyapunov-OU as a substrate-physics result.** If Prediction 3 lands HARD-PASS, the substrate has a PROVABLE stationary distribution under continual operation -- a cert-grade theoretical result (substrate provably bounded-forgetting; no asymptotic collapse).

---

## L5 -- CROSS-SUBSTRATE COMPOSITION MAP

```
                  5000-CYCLE CONTINUAL OPERATION (untested at scale)
                                       |
              +------------+-----------+------------+------------+
              |            |           |            |            |
              v            v           v            v            v
        TWO_TIER         BCM         NEUROGENESIS  LSM          LYAPUNOV-OU
        (M10)            (M2)        (M5)          (M9)         (M19)
        P=0.50           P=0.40      P=0.35        P=0.35       P=0.35
              |            |           |            |            |
              +------------+-----------+------------+------------+
                                       |
                          [if any HARD-PASS standalone]
                                       v
                          COMPOSE: TWO_TIER + BCM + k-WTA
                          predicted multiplicative gain
                                       |
                                       v
                          glass-box-LLM continual document stream
                          (L2 vision: substrate-LM that ingests forever)
                                       |
                                       v
                          Decade-scale substrate cert
                          (5000-cycle benchmark becomes standard)
```

If TWO_TIER HARD-FAIL:
```
TWO_TIER fails -> NOT a storage-segregation problem
        |
        +-> route to NEUROGENESIS (M5) -- capacity expansion path
        +-> route to GEM/A-GEM (M14) -- gradient-projection path
        +-> route to spin-glass annealing (M16) -- schedule-based path
```

If TWO_TIER HARD-PASS:
```
TWO_TIER lands -> ship to L1 substrate primitives (hdlab/)
        |
        +-> Phase 2: scale to N_DIM=32768, J=5000 production
        +-> Phase 3: compose with BCM (M2), then k-WTA (drill #1)
        +-> Phase 4: 6-month autonomous-continual benchmark (the moat test)
```

---

## CITATIONS (verified, count = 19)

1. Tononi, G., Cirelli, C. (2003). "Sleep and synaptic homeostasis: a hypothesis." Brain Res. Bull. 62: 143-150. [ResearchGate](https://www.researchgate.net/publication/8991296_Tononi_G_Cirelli_C_Sleep_and_synaptic_homeostasis_a_hypothesis_Brain_Res_Bull_62_143-150)

2. Tononi, G., Cirelli, C. (2020). "Sleep and synaptic down-selection." European Journal of Neuroscience. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC6612535/)

3. Bienenstock, E.L., Cooper, L.N., Munro, P.W. (1982) and Cooper, L.N. et al. "BCM theory of synapse modification at 30." [Scholarpedia](http://www.scholarpedia.org/article/BCM_theory) [Wikipedia](https://en.wikipedia.org/wiki/BCM_theory)

4. Aimone, J.B., Deng, W., Gage, F.H. (2010). "Adult neurogenesis: integrating theories and separating functions." Trends Cogn Sci. [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1364661310000884)

5. Adult hippocampal neurogenesis and pattern separation in DG (2015). [Frontiers](https://www.frontiersin.org/journals/systems-neuroscience/articles/10.3389/fnsys.2015.00120/full)

6. Nader, K., Schafe, G.E., LeDoux, J.E. (2000). "Fear memories require protein synthesis in the amygdala for reconsolidation after retrieval." Nature 406: 722-726. [Nature](https://www.nature.com/articles/35021052) [PubMed](https://pubmed.ncbi.nlm.nih.gov/10963596/)

7. Stevens, B. et al. (2007). "The Classical Complement Cascade Mediates CNS Synapse Elimination." Cell. [Cell](https://www.cell.com/fulltext/S0092-8674(07)01355-4)

8. Liu, X., Ramirez, S., Pang, P.T. et al. (2012). "Optogenetic stimulation of a hippocampal engram activates fear memory recall." Nature 484: 381-385. [Nature](https://www.nature.com/articles/nature11028)

9. Maingret, N. et al. (2021). "Bidirectional Interaction of Hippocampal Ripples and Cortical Slow Waves Leads to Coordinated Spiking Activity During NREM Sleep." Cerebral Cortex. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8179633/)

10. Lega, B.C., Jacobs, J., Kahana, M. and follow-ons. "Gamma amplitude is coupled to opposed hippocampal theta-phase states during the encoding and retrieval of episodic memories in humans." Current Biology. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0960982223003937)

11. Characterize LSM-tree Compaction Performance (2026). [arXiv](https://arxiv.org/html/2602.12669) -- LSM/RocksDB compaction strategies.

12. JVM Generational GC: write barrier + intergenerational barriers. [Shipilev JVM Quarks #13](https://shipilev.net/jvm/anatomy-quarks/13-intergenerational-barriers/)

13. Shapiro, M. et al. "Conflict-free Replicated Data Types." [Springer chapter](https://link.springer.com/chapter/10.1007/978-3-642-24550-3_29) [Marc Shapiro PDF](https://www.lip6.fr/Marc.Shapiro/papers/2018/CRDTs-Springer2018-authorversion.pdf)

14. Denning, P.J. working set / LRU eviction theory. [Cache eviction overview](https://www.durgesh.dev/blog/cache-eviction-policies-lru-fifo-lfu-and-the-principle-of-locality)

15. Kirkpatrick, J. et al. (2017). "Overcoming catastrophic forgetting in neural networks." PNAS. EWC + Fisher. [EVCL extension arXiv](https://arxiv.org/html/2406.15972v1)

16. Lopez-Paz, D., Ranzato, M. (2017). "Gradient Episodic Memory for Continual Learning." NeurIPS. [arXiv](https://arxiv.org/abs/1706.08840)

17. Vincent, E. (2006). "Aging, rejuvenation and memory: the example of spin glasses." [arXiv](https://arxiv.org/pdf/cond-mat/0603583) -- trap models; hierarchical landscape; Bouchaud.

18. Suppressing Structural Relaxation in Nanoscale Antimony PCM drift. [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10477879/) [MDPI PCM drift compensation](https://www.mdpi.com/2079-9268/14/4/50)

19. Reservoir computing fading memory + echo state property + spectral radius. [arXiv ESN mathematical perspective](https://arxiv.org/html/2504.11757v1)

Plus B-cell germinal-center maintenance refs: [Frontiers memory plasma cells](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2019.00721/full); online learning OGD regret bounds [Logarithmic Regret OGD arXiv](https://arxiv.org/pdf/1802.04623); Markov-chain mixing/Doeblin [Levin-Peres-Wilmer book](https://www.stat.berkeley.edu/~aldous/260-FMIE/Levin-Peres-Wilmer.pdf); Lyapunov-stable NN [arXiv](https://arxiv.org/abs/2412.21095).

---

## LIT-SCAN CALIBRATION NOTES

- All probability estimates deflated 0.15-0.25 from raw LM confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap at 0.50 applied to TWO_TIER (rank #1). The architecture is universal across 4 fields but the SPECIFIC composition with substrate's Hebbian-superposition arithmetic has no published precedent. The 0.50 cap reflects cap on synthesis claims.
- HARD-FAIL thresholds mandatory and listed for every prediction.
- DIRECTIONALITY (storage tiering helps continual capacity) is HIGHLY confident (raw P ~ 0.80, robust across 4 independent fields). MAGNITUDE (>= 0.75 retention at alpha=0.61 over 5000 cycles) is where deflation hits -- substrate's specific cliff dynamics untested at this horizon.
- Cell A's MIDDLE_BAND drift_red=0.067 anchor + Cell B's HARD_FAIL anchor + a8 alpha=0.30 PASS anchor jointly bracket the regime; TWO_TIER cell has a clear sanity bracket.
- Drilled fields explicitly hit: theoretical neuroscience (8 mechanisms), distributed systems (4), continual-learning ML (3), materials physics (3), pure mathematics (2), adjacent biology (1), online-learning theory (1). 7+ disparate fields -- meets Trigger F aggressive cross-domain requirement.
- Saturation/scope-pivot: avoided re-drilling CLS replay (drill #2), SWR (separate drill), revival architectural (2026-06-24); this drill ADDS the storage-systems / generational / metaplasticity / engram-theory / Lyapunov angles that were under-drilled.

---

## DISPATCH RECOMMENDATION (top 5 ranked, with Phase plan)

**Phase 1 -- IMMEDIATE single decisive cell:**
- `gap4_two_tier_generational_W_v1` at alpha=0.61, K_promote=100, tau=0.10, gamma=0.90, J=5000, 3 seeds, N_DIM=4096.
- Compute: ~3 CPU-hr remote_cpu.
- Decisive on rank-1 hypothesis (TWO_TIER rescues at 4.4x Hopfield).

**Phase 2 -- CONDITIONAL on Phase 1 HARD-PASS:**
- Full hyperparameter grid: K_promote x tau x gamma (27 combinations) at alpha=0.61, 3 seeds. ~10 hr.
- Re-test at N_DIM=32768 (production-scale).
- Compose with M2 BCM gate.

**Phase 3 -- COMPOSITION (CONDITIONAL on Phase 2):**
- TWO_TIER + BCM + k-WTA-VQ (drill #1) at alpha=1.0+ (post-cliff stress).
- Predicted: usable alpha >= 1.5; substrate becomes capacity-unbounded for practical purposes.

**Top 5 in priority order with brief why-now:**

1. `gap4_two_tier_generational_W_v1` (P_deflated=0.50, cost=3hr) -- 4-field convergence; no substrate substitute; foundational architecture.
2. `gap4_bcm_metaplasticity_threshold_v1` (P=0.40, cost=2hr) -- per-weight gate; composes with TWO_TIER; substrate has W stats already.
3. `gap4_neurogenesis_capacity_refresh_v1` (P=0.35, cost=4hr) -- backup if TWO_TIER fails; capacity-expansion path.
4. `gap4_lsm_leveled_compaction_W_v1` (P=0.35, cost=3hr) -- engineered variant of TWO_TIER; tests whether 3+ tiers help beyond 2.
5. `gap4_lyapunov_OU_mean_reversion_v1` (P=0.35, cost=2hr) -- diagnostic + mechanism; gives theoretical bound on substrate behavior.

**Ordering rationale:**
- #1 is rank-1 because 4 disparate fields predict the same architecture (highest prior across multiple independent priors).
- #2 composes with #1 multiplicatively at trivial cost.
- #3 is the contingent path if #1 fails (architectural pivot).
- #4 tests whether scaling the tier-count beyond 2 adds value (RocksDB does 5+ levels for a reason).
- #5 provides theoretical anchor + a fundamentally different mechanism class (mean-reversion, not segregation).

**Ordering vs other gaps:**
- Gap 4 (continual) is L2-vision-critical; required for glass-box-LLM lifelong-learner.
- Cell A NREM-replay (already pending) provides the REPLAY component; TWO_TIER provides the DESTINATION.
- Should ship in parallel with k-WTA-VQ (drill #1) -- independent and composable.

---

## PLAIN-ENGLISH WRAP (Fix #13)

The substrate currently handles 200-cycle continual writes well and 120 production sessions well, but no one has tested it at the multi-thousand-cycle scale that production usage would demand. The brain handles decade-scale continual memory by using ~eight distinct mechanisms stacked together, each tuned to a different timescale. The substrate has tried two of them in isolation (NREM replay; REM homeostasis) and got middling/failing results. The novel finding of this drill: four UNRELATED engineering and biological systems (Java garbage collectors, RocksDB databases, the immune system, and the brain's hippocampus-to-cortex pipeline) all independently converged on the SAME architecture -- two-tier storage with periodic promotion of important items from a young/fast layer to an old/slow layer. The substrate doesn't have this yet; its W matrix is a single tier. The rank-1 cell to dispatch: add a second W matrix and promote heavy-hitter entries periodically. If it works at the 5000-cycle horizon (predicted 50% chance), the substrate has its decade-scale architecture. Four backup mechanisms ranked below for if rank-1 fails. Total compute: ~3 CPU-hr for the decisive test; ~10 hr for full grid.

---

-- Research (Opus synthesis; 13 parallel WebSearch lit-scans; 22 candidate mechanisms scanned across 7+ disparate fields; deflated per calibration; cap on novel-synthesis applied).
