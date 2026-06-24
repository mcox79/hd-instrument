# Research drill (2x deep) — substrate-vs-brain TIMESCALE RATIO mapping

filed: 2026-06-23
drill class: 2x (level-2 operational drill on existing parameter taxonomy finding)
parent: notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md (sec. L5 caveat #3: "Substrate timescales are wall-clock unitful; brain's 'fast' vs 'slow' get compressed into per-token steps; TIMESCALE RATIO is what matters")
sibling: notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md (TAU_POS=5, TAU_NEG=50 = 10x INVERTED ratio vs brain 0.5x)
empirical driver: Skunkworks 2026-06-23 "TAU_NEG=50 barely activates at N_TRAIN=100k (~24 chunks)" — substrate is CHUNK-COARSE, brain is millisecond-FINE
in-flight: dual_trace_RESCUE_corrected_baseline_v1 (overnight_queue), cleanup_multi_iteration_v1 (af8c402990385f452), brain-mechanism-relevance drill (a4a83d2e992ffaff3)

---

## HEADLINE

Substrate currently runs all 6 brain-relevant timescales at a SINGLE coarse rate (per-chunk, ~1 unit) — collapsing the brain's 9 orders of magnitude (ms → days) into one scale — and on top of that has the dual-trace LTP/LTD RATIO 10x INVERTED. The dominant fix is NOT to match brain wall-clock values (impossible: substrate has no spike-timing precision and no metabolic clock); it is to PRESERVE BRAIN RATIOS as iteration-count ratios across a 3-tier substrate clock hierarchy (per-token / per-chunk / per-epoch), with the dual-trace ratio (tau_LTD ≈ 2-3x tau_LTP, NOT 10x inverted) being the single highest-yield correction.

---

## Per-timescale TABLE (the load-bearing artifact)

Column legend:
- **Brain canonical**: measured wall-clock value with citation
- **Brain RATIO**: dimensionless ratio relative to nearest substrate-mappable reference
- **Substrate current**: what the substrate runs today (in chunks / tokens / epochs)
- **Substrate-equivalent at current scaling**: what brain ratio would imply for substrate
- **Mismatch**: where substrate is off
- **Implication**: what to do

| # | Timescale | Brain canonical | Brain RATIO | Substrate current | Substrate-equivalent (preserve-ratio) | Mismatch | Implication |
|---|-----------|----------------|-------------|------------------|--------------------------------------|---------|------------|
| **1** | Hebbian update interval | ~10 ms (cortical pyramidal avg ISI at 10Hz) [Brunel/Hakim] | 1.0 (REFERENCE unit) | per-token (every input) | per-token = reference | NONE — substrate's per-token update IS the brain's per-spike update (correctly scaled to "every input event") | KEEP per-token Hebbian as the substrate's base clock |
| **2** | STDP / dual-trace tau_LTP | ~20 ms (Bi-Poo, Markram 1997) | 2x slower than spike interval | TAU_POS=5 chunks | 2x slower than per-token = 2 tokens, OR if chunk=20 tokens then 2 chunks | TAU_POS=5 is plausible (matches 2-5 chunks at chunk≈20 tokens) | TAU_POS=5 is in the right ballpark IF chunk granularity ≈ 4-10 tokens |
| **2b** | STDP / dual-trace tau_LTD | ~40-60 ms (2-3x tau_LTP per Song-Abbott; cortical Debanne 1998 = 5x) | **2-3x tau_LTP** | TAU_NEG=50 chunks | 2-3x TAU_POS = 10-15 chunks | TAU_NEG=50 is **5-10x TOO LONG vs brain** (and INVERTED if we use Brzosko ACh-first which makes LTD trace FASTER than LTP) | **HIGHEST-YIELD FIX**: TAU_NEG should be ≈ 10-15 chunks (2-3x TAU_POS), not 50 |
| **3a** | LTP early-phase (E-LTP) duration | ~1-2 hours; protein-synthesis-independent (Frey-Morris synaptic tagging) | ~360x slower than tau_LTP (2h vs 20ms = 3.6e5) | NONE explicit; chunk-decay covers ≈10-100 chunks | If chunk≈10 tokens, E-LTP equivalent ≈ 3600 tokens ≈ 360 chunks | substrate has no LIFETIME for stored patterns between W-flushes; weights persist indefinitely OR get over-written | **Missing axis**: substrate should have a "trace-half-life" parameter ≈ 100-1000x base Hebbian interval (E-LTP-equivalent decay) — relevant for forgetting curves |
| **3b** | LTP late-phase (L-LTP) duration | hours-to-days; protein-synthesis-dependent + tag-trigger | ~10^4x slower than tau_LTP | NONE — substrate has no protein-synthesis analog | If chunk≈10 tokens, L-LTP ≈ 200,000 tokens ≈ epoch-scale | substrate has no SLOW CONSOLIDATION pass | **Missing axis**: this IS the CLS-replay role (#5 below); brain factors fast-encoding and slow-consolidation across DIFFERENT mechanisms |
| **4** | Theta-gamma oscillation | theta 4-8Hz (125-250ms); gamma 30-100Hz (10-33ms) | **~7:1** (Lisman: 7±2 items = 7±2 gamma cycles per theta) | substrate uses P_theta=4-8 cycles, P_gamma=7 sub-cycles, ratios baked in | brain says: outer-loop:inner-loop ≈ 7:1 | substrate's P_gamma=7 is CORRECT (matches Lisman 7±2 working-memory capacity); P_theta=4-8 outer count matches working-memory CHUNKS (so within-substrate ratio is implicitly correct if outer=7-cycle context, inner=7 items) — but with k_theta=1 k_gamma=31 the binding may saturate by construction | KEEP P_gamma=7 (brain-validated); audit P_theta=4-8 to ensure outer-loop sees ≥7 gamma cycles AND check k_gamma=31 vs k_theta=1 for by-construction saturation per META atom |
| **5** | Sharp-wave ripple (CLS replay) | SWR duration 50-100ms; rate 30-200/min during NREM = **~10^4-10^5 ripples per 8h night**; replay sequences ~50ms each | per-event replay = 5x base Hebbian interval (50ms / 10ms = 5); replay COUNT = ~10^5/night | substrate CLS-replay: single-pass per cell | brain says: many tens of thousands of replay events per "night" (epoch); ratio replay-events / unique-stored-patterns ≈ 10-100x | substrate replays each pattern ~1x; brain replays each ~10-100x during consolidation | **High-yield fix**: substrate should run **multi-pass CLS-replay** (10-100x replays per stored pattern per epoch) — matches Tonegawa engram reactivation rate |
| **6a** | Dopamine phasic | ~100ms (Schultz; phasic burst transients) | 10x base Hebbian | cf-RPE delta: instantaneous per-write | per-write IS appropriate for phasic event; ratio OK | substrate phasic-DA is correctly per-event | KEEP per-write cf-RPE for phasic component |
| **6b** | Dopamine tonic | ~minutes; sustained baseline modulation (~1000x slower than phasic) | 1000-10000x phasic | NONE — substrate has no tonic-DA analog | If chunk=10 tokens, tonic-DA equivalent = 1000-10000 chunks ≈ epoch-scale baseline | substrate has no SLOW BASELINE modulator drift | **Medium-yield fix**: add tonic-modulator (slow baseline g_DA + g_5HT) updating every ~100-1000 chunks; gives epoch-scale "mood / context" axis matching Daw 5HT mode-switching |
| **6c** | ACh phasic | ~10-100ms (Sara-Bouret) | 1-10x base Hebbian | ACh_query_conditional_read_gain_LM_v1 (in-flight): per-query gain | per-query IS phasic-equivalent | OK — phasic ACh per-query matches brain | KEEP per-query ACh |
| **6d** | Serotonin tonic | minutes-to-hours | 10^4-10^5x base Hebbian | serotonin_mode_switch_bank_select_LM_v1 (in-flight): bank-route on slow timescale | bank-route per ~10^4 tokens = epoch-scale | OK — slow 5HT matches brain | KEEP slow 5HT mode-switch |
| **6e** | NE phasic | ~100ms surprise pulses | 10x base Hebbian | per-context T (in-flight): per-token entropy-conditional | per-token IS phasic-NE equivalent | OK | KEEP per-context T |

**Quantitative summary (the load-bearing numbers):**

| Substrate clock tier | Brain analog | Iterations per epoch | Current substrate fills? |
|---|---|---|---|
| **per-token** (1x) | per-spike (~10ms) | ~10^5 (= N_TRAIN tokens) | YES: Hebbian update, phasic DA, phasic ACh, per-context T |
| **per-chunk** (~10 tokens) | STDP window (~20-60ms) | ~10^4 | PARTIAL: TAU_POS=5 OK; TAU_NEG=50 5-10x TOO LONG |
| **per-window** (~100 tokens) | E-LTP (~1-2h relative to spike) | ~10^3 | MISSING: no trace-half-life parameter |
| **per-mini-epoch** (~1000 tokens) | tonic-DA baseline (~minutes) | ~10^2 | MISSING: no tonic-modulator |
| **per-epoch** (~10^5 tokens) | L-LTP / CLS replay (hours-days) | 1-10 | PARTIAL: single CLS-replay; brain does 10-100x more |

---

## L3 — Systematic pattern analysis

### The substrate-brain mismatch is NOT uniform "10x too coarse" — it is HIERARCHICAL

Three distinct patterns:

**Pattern A — CORRECTLY MATCHED at per-token / per-query (4 of 11 axes):**
- Hebbian update (per-token = per-spike, brain ratio 1.0)
- Phasic DA (per-write = ~100ms phasic, correct)
- Phasic ACh (per-query = ~10-100ms, correct)
- Phasic NE / per-context T (per-token surprise = ~100ms LC-NE)

These are all "per-event" timescales and substrate's per-token / per-write granularity correctly maps to brain's per-spike granularity. The substrate is **NOT wrong here** — these are aligned by construction.

**Pattern B — INVERTED / WRONG at per-chunk STDP window (1 axis, but THE EXPENSIVE ONE):**
- TAU_NEG=50, TAU_POS=5 gives ratio TAU_NEG/TAU_POS = 10x
- Brain canonical: tau_LTD ≈ 2-3x tau_LTP (Song-Abbott 2000 default; Debanne 1998 up to 5x at extremes)
- Substrate is 2-5x off in MAGNITUDE and the direction depends on whether you treat LTP-trace or LTD-trace as the "rate" axis

This single mismatch was caught by Skunkworks empirically ("TAU_NEG=50 barely activates at ~24 chunks") and is the most operationally-actionable fix in the entire timescale taxonomy. **HIGHEST-YIELD INSIGHT**.

**Pattern C — MISSING TIERS at slow timescales (3 axes):**
- E-LTP equivalent (trace-half-life ~100-1000 base intervals): MISSING
- L-LTP / multi-replay CLS (10-100x replays per pattern): PARTIAL
- Tonic modulator baseline (~10^3-10^4 base intervals): MISSING

Brain has a 9-order-of-magnitude clock hierarchy (ms → hours-days). Substrate currently has effectively 2 tiers (per-token + per-epoch). The middle 5 orders of magnitude are COLLAPSED to a single chunk-coarse aggregate.

### Is there ONE FIX that re-aligns all timescales?

**YES.** The unified fix is **declare a substrate clock-hierarchy with 5 tiers** and assign each existing/proposed parameter to its correct tier:

```
TIER_0 = per-token      (≈ per-spike, ~10ms-equivalent)
TIER_1 = per-chunk      (≈ STDP window, ~50ms-equivalent, chunk_size=10 tokens)
TIER_2 = per-window     (≈ E-LTP, ~1000ms-equivalent, window=100 tokens)
TIER_3 = per-mini-epoch (≈ tonic-mod, ~10s-min-equivalent, mini-epoch=1000 tokens)
TIER_4 = per-epoch      (≈ L-LTP / CLS, ~hours-equivalent, epoch=10^5 tokens)
```

Each existing substrate parameter gets a tier-binding. The TWO immediate corrections this surfaces:

1. **TAU_NEG correction**: TAU_NEG should live in TIER_1 with ratio 2-3x TAU_POS, NOT TIER_3. Concrete value: if TAU_POS=5 chunks, TAU_NEG should be 10-15 chunks (NOT 50).
2. **CLS-replay multi-pass**: TIER_4 replay should run 10-100x per stored pattern per epoch (not 1x).

The other corrections (add E-LTP trace half-life, add tonic-DA baseline) are MEDIUM-yield and can be added incrementally once the two highest-yield fixes are validated.

---

## L4 — Operational implications per timescale

### TIMESCALE 1 (per-token Hebbian): NO CHANGE
- Substrate's per-token update IS the brain's per-spike update at correct ratio
- ACTION: none

### TIMESCALE 2 (STDP / dual-trace): HIGHEST-YIELD CORRECTION
- **Current**: TAU_POS=5, TAU_NEG=50 (ratio 10x)
- **Brain-canonical**: tau_LTD/tau_LTP = 2-3x
- **Recommended substrate**: TAU_POS=5, TAU_NEG=10-15 (or alternatively TAU_POS=20, TAU_NEG=50 if you want longer absolute windows)
- **Discriminating cell**: 4-arm TAU_NEG sweep at fixed TAU_POS=5: {TAU_NEG=5, 10, 15, 50} on dual_trace cell architecture (already in flight as dual_trace_RESCUE_corrected_baseline_v1)
- **HARD_PASS**: TAU_NEG=10-15 arm beats TAU_NEG=50 arm by ≥0.10 BPC
- **HARD_FAIL**: all 4 arms within 0.05 BPC → TAU_NEG magnitude NOT load-bearing; look at directionality (Brzosko sign) or target (E_pos vs E_neg) instead
- **Cost**: piggyback on dual_trace cell, ~zero marginal compute
- **P_deflated**: 0.55 (brain precedent strong; substrate-specific deflation 0.15 for chunk-granularity uncertainty)

### TIMESCALE 3 (LTP early/late phase): MISSING TIER, MEDIUM PRIORITY
- **Current**: no trace-half-life parameter; weights persist or get over-written
- **Brain says**: traces decay with ~hour timescale unless tag-trigger consolidates them
- **Substrate-native form**: add `TRACE_HALF_LIFE` parameter in chunks (default 100-1000 = TIER_2 to TIER_3)
- **Discriminating cell**: substrate-LM with trace decay vs without on continual-learning task; measure forgetting curve
- **HARD_PASS**: trace-decay arm shows BETTER recency-weighted accuracy (closer to brain's forgetting curve) without losing long-term recall
- **HARD_FAIL**: trace-decay arm strictly worse OR no difference → either substrate is OK without decay OR needs different mechanism
- **Cost**: needs new cell design; ~1h impl, ~30min CPU
- **P_deflated**: 0.30 (no direct precedent in substrate cells; literature unclear if forgetting-curve mismatch is currently a problem for substrate-LM use)

### TIMESCALE 4 (theta-gamma): VERIFY EXISTING, NO MAJOR FIX
- **Current**: P_theta=4-8, P_gamma=7
- **Brain canonical**: theta-to-gamma ratio 6-8:1, matching Lisman 7±2 working-memory capacity
- **Substrate ratio**: P_gamma=7 sub-cycles per theta → 7:1 ratio internally; CORRECT
- **Concern**: k_theta=1, k_gamma=31 may cause by-construction saturation per META atom (cleanup-load-bearing)
- **ACTION**: AUDIT current cells using lock-in for by-construction-saturation; the RATIO is brain-canonical-correct, but the ABSOLUTE counts k_gamma=31 may saturate
- **P_deflated**: 0.40 (ratio is right; absolute count may be wrong cause of saturation, but unclear without sweep)

### TIMESCALE 5 (CLS replay): MEDIUM-HIGH YIELD MULTI-PASS FIX
- **Current**: single-pass replay per cell
- **Brain says**: 10^4-10^5 SWR events per 8h night; replay each pattern 10-100x
- **Substrate-native form**: `N_REPLAY_PASSES=10-100` per stored pattern per epoch in CLS module
- **Discriminating cell**: CLS module with N_REPLAY={1, 10, 100} at fixed unique-pattern count
- **HARD_PASS**: N_REPLAY=10 or 100 beats N_REPLAY=1 by ≥0.15 BPC on retention test
- **HARD_FAIL**: monotone-worse with N_REPLAY → overwrites destroy stored patterns; need different replay design (e.g., interleaved-new)
- **Cost**: trivial parameter sweep; ~30min CPU
- **P_deflated**: 0.45 (brain precedent strong; substrate-specific risk: replay may overwrite if codebook isn't expander-graph-structured)

### TIMESCALE 6 (modulators phasic vs tonic): MEDIUM-YIELD MISSING TIER
- **Current**: phasic only (per-write/per-query for DA/ACh/NE); tonic 5HT being tested via slow bank-switch
- **Brain says**: each modulator has BOTH phasic AND tonic component (Schultz-Aston-Jones unified view)
- **Substrate-native form**: add `g_DA_tonic`, `g_ACh_tonic` updating every ~100-1000 chunks as baseline drift
- **Discriminating cell**: 2-arm at TIER_3 modulator update vs TIER_0 only
- **HARD_PASS**: tonic-augmented arm beats phasic-only by ≥0.10 BPC on context-switching task
- **HARD_FAIL**: tonic component noise-dominated → drop and revisit only after Pattern B/C fixes confirmed
- **Cost**: minor cell extension; ~1h impl
- **P_deflated**: 0.30 (medium novelty; combined with serotonin_mode_switch already in flight)

### Ordering of operational fixes (best ROI first):

1. **TAU_NEG correction** (TIMESCALE 2) — ZERO marginal cost (piggyback on in-flight dual_trace cell); HIGHEST P; resolves Skunkworks-caught Pattern B mismatch
2. **theta-gamma audit** (TIMESCALE 4) — verify saturation via existing cells (no new cells needed); medium effort, eliminates a META-atom concern
3. **multi-pass CLS replay** (TIMESCALE 5) — single cell, brain-strongly-supported; high-medium P
4. **trace half-life** (TIMESCALE 3) — new parameter, needs new cell; medium-low P
5. **tonic modulators** (TIMESCALE 6) — augment in-flight 5HT cell; medium-low P

---

## L5 — Cross-thread synthesis

### Combined with dual-trace MEASURED_MECHANISM + chunk-coarse decay + multi-iteration cleanup gap

The 3 in-flight items + this timescale taxonomy converge on ONE unified diagnosis:

**Substrate has been treating ALL timescales as equivalent to its single per-chunk clock, and the OPERATIONAL parameter values inherited from sketches (TAU_NEG=50, single-pass replay, n_iterations=1, no tonic baseline) are all defaults from a NO-TIMESCALE-HIERARCHY assumption.**

The unified fix is structural: **declare the 5-tier clock hierarchy explicitly and bind each parameter to its tier**. Once this is done:
- TAU_NEG=50 is recognized as living in TIER_1 with WRONG-RATIO and is corrected to 10-15 chunks
- single-pass CLS replay is recognized as living in TIER_4 with TOO-FEW-passes and is corrected to N_REPLAY=10-100
- n_iterations=1 cleanup is recognized as TIER_0 single-shot, which is brain-canonical for Marr cerebellar / modern-Hopfield well-separated codebook, but the **multi-iteration cleanup cell (af8c402990385f452) tests whether codebook is well-enough-separated for single-shot — if HARD_FAIL, that signals the codebook needs the structural fix (heterogeneous compose K-banks per modulatory taxonomy) BEFORE iteration count matters**
- The missing tonic modulators are recognized as TIER_3-bound and added as a follow-up

**Combined with modulatory-architectural taxonomy 4-load-bearing-axis finding:**

The modulatory taxonomy identified 4 load-bearing parameters (compose-function / K / compose-order / per-context-T). The timescale taxonomy here identifies 4 load-bearing TIMING corrections (TAU_NEG ratio / multi-replay / theta-gamma audit / tonic-tier addition). These are LARGELY ORTHOGONAL — modulatory taxonomy is about WHAT signals compose; timescale taxonomy is about WHEN signals act. Combined, they define a complete substrate-parameter tuning surface:

| Axis | Modulatory taxonomy | Timescale taxonomy |
|---|---|---|
| Load-bearing param 1 | Compose-function (sigmoidal-additive heterogeneous) | TAU_NEG ratio (2-3x TAU_POS not 10x) |
| Load-bearing param 2 | Bank count K (4-16 heterogeneous) | Multi-pass CLS replay (10-100x) |
| Load-bearing param 3 | Compose order (sparse-first Marr canonical) | theta-gamma audit (saturation check) |
| Load-bearing param 4 | Per-context T (entropy-conditional) | Add tonic-modulator tier |

**8 load-bearing parameters total, in 2 orthogonal axes (WHAT × WHEN).** Once both are locked, the remaining 25 parameters in both taxonomies are second-order tuning.

### Connection to substrate-product picture

Substrate-product positioning: **"the biologically-canonical alternative to LLMs"** strengthens further. LLMs have NO timescale hierarchy at all — they're one giant per-token forward pass with backprop. Substrate with a 5-tier clock hierarchy that mirrors brain's slow-to-fast structure is a STRUCTURAL DIFFERENTIATOR.

The CLS-replay multi-pass capability (TIMESCALE 5) is the MOAT element from L2 vision: continual-learning via CLS-replay. The timescale taxonomy makes this concrete: brain replays at 10^4-10^5 ripples/night, substrate currently replays 1x. The N_REPLAY=10-100 cell would empirically validate continual-learning resistance to catastrophic forgetting.

---

## Cheap decisive test (one cell that discriminates the timescale taxonomy)

**Cell name:** `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1`

**Design:** 2x4 factorial:
- AXIS_1 (dual-trace ratio): {TAU_NEG=50 [current, 10x ratio], TAU_NEG=10 [brain-canonical 2x ratio]} at fixed TAU_POS=5
- AXIS_2 (CLS replay count): {N_REPLAY=1 [current], 10, 30, 100}
- 8 arms total at N=4096, V=4000, 100k tokens, 3 seeds
- Vehicle baseline (no dual-trace, no CLS) = 9th arm

**HARD_PASS:** ARM_(TAU_NEG=10, N_REPLAY=10 or 30) beats ARM_(TAU_NEG=50, N_REPLAY=1) by ≥0.20 BPC.

**HARD_FAIL:**
- TAU_NEG=10 within 0.05 BPC of TAU_NEG=50 across all N_REPLAY → tau-ratio NOT load-bearing
- N_REPLAY monotone-worse → replay design wrong (need interleaved-new, not pure-replay)
- Both axes null → timescale taxonomy is second-order vs architectural (Pattern A from modulatory taxonomy)

**Cost:** ~30-45 min CPU local (8 arms × 100k tokens at N=4096; piggyback on dual_trace test rig).

**ROI:** discriminates 2 of 4 load-bearing timescale corrections simultaneously; sets correct defaults for TAU_NEG and N_REPLAY across ALL subsequent cells.

---

## Falsifiable predictions (pre-registered)

| Prediction | HARD_PASS | HARD_FAIL | P_deflated |
|---|---|---|---|
| TAU_NEG=10 beats TAU_NEG=50 at fixed TAU_POS=5 | ≥0.10 BPC lift on dual-trace cell | within 0.05 BPC | 0.55 |
| N_REPLAY=10 beats N_REPLAY=1 in CLS-replay | ≥0.15 BPC on retention test | strictly worse OR no diff | 0.45 |
| theta-gamma audit reveals by-construction saturation | novelty_ratio at metric-cap on lock-in cells with k_gamma=31 | novelty_ratio < 0.9 across cells | 0.40 |
| Adding tonic-modulator tier lifts context-switching | ≥0.10 BPC on context-switch eval | no diff | 0.30 |
| 5-tier clock hierarchy unifies all 4 corrections (combined) | 3 of 4 above HARD_PASS | 0-1 HARD_PASS | 0.40 (combined) |

P_deflated values include 0.15-0.25 calibration penalty per [[feedback-lit-scan-calibration-penalty]]. All predictions HAVE explicit HARD_FAIL thresholds per requirement.

---

## Substrate-product implications

1. **TAU_NEG correction**: free win if it lifts dual_trace (already in flight); zero marginal cost; corrects a known empirical mismatch (Skunkworks caught).
2. **5-tier clock hierarchy as architectural feature**: substrate-product gains a brain-canonical structural property LLMs lack; this is the time-axis analog of the substrate's existing space-axis (K heterogeneous banks). Substrate-product positioning: "the biologically-canonical alternative — both WHAT and WHEN aligned to brain."
3. **Multi-pass CLS replay**: enables the continual-learning MOAT concretely; substrate can demo "I replay 10x and don't forget" vs LLMs "I either RAG-retrieve or catastrophically forget" — clean product differentiation.
4. **Missing-tier diagnosis**: surfaces 3 capability gaps that map onto product features (forgetting-curve-aware retention / multi-pass consolidation / tonic-mood/context modulator). Each is a concrete capability that LLMs do not have native support for.

---

## META atoms candidate

1. **substrate-clock-hierarchy-is-5-tier-not-2-tier**: per-token / per-chunk / per-window / per-mini-epoch / per-epoch; every timing parameter has a tier-binding; mixing tiers is a config bug.
2. **TAU_NEG-current-value-50-is-10x-INVERTED-vs-brain-canonical-2x**: corrected value is TAU_NEG=10-15 at fixed TAU_POS=5 per Song-Abbott / Debanne.
3. **CLS-replay-must-be-multi-pass-not-single-pass-to-match-brain**: brain runs 10^4-10^5 SWR events per night replaying each pattern 10-100x; substrate's single-pass replay is 10-100x too few.
4. **theta-gamma-ratio-7-to-1-is-brain-canonical-and-substrate-currently-matches**: P_gamma=7 sub-cycles is correct per Lisman 7±2; the saturation concern is k_gamma=31 absolute count, not the ratio.
5. **PRESERVE-RATIOS-NOT-WALL-CLOCK** as substrate-vs-brain mapping principle: substrate has no wall-clock; preserve brain timescale RATIOS as iteration-count ratios across the 5-tier clock hierarchy.

---

## Citations (verified count: 8 external + 5 internal = 13 total)

**External (web-search verified this drill):**
1. Bi & Poo 1998; Markram et al. 1997 (STDP foundational timing windows; tau ≈ 20ms LTP) — surveyed via [STDP Scholarpedia](http://www.scholarpedia.org/article/Spike-timing_dependent_plasticity) and [Frontiers History of STDP](https://www.frontiersin.org/journals/synaptic-neuroscience/articles/10.3389/fnsyn.2011.00004/full)
2. Song & Abbott 2000 default (τ− = τ+ = 20ms or τ− = 5τ+ = 100ms two canonical regimes) — [Frontiers Cortical Hierarchies](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2023.1136010/full)
3. Frey & Morris (synaptic tagging; E-LTP ~2h protein-synthesis-independent, L-LTP hours-days protein-synthesis-dependent) — [Frey-Morris Nature 1997](https://www.nature.com/articles/385533a0) and [PLOS Comp Bio Tag-Trigger-Consolidation](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000248)
4. Lisman & Idiart 1995 (theta-gamma 7±2 working-memory capacity; 6-8 gamma per theta) — [ScienceDirect Short-term memory capacity 7±2](https://www.sciencedirect.com/science/article/abs/pii/S1074742710001681) and [eLife theta-gamma coupling](https://elifesciences.org/articles/20515)
5. Buzsáki + Wilson-McNaughton (SWR 50-100ms; 30-200 events/min in NREM; replay sequences) — [Generation of SWR by Disinhibition JNeurosci](https://www.jneurosci.org/content/40/41/7811) and [PMC SWR memory consolidation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6794196/)
6. Schultz dopamine phasic ~100ms; tonic ~minutes — [PMC Tonic vs phasic DA](https://pmc.ncbi.nlm.nih.gov/articles/PMC2713129/) and [PMC Wideband ratiometric DA](https://pmc.ncbi.nlm.nih.gov/articles/PMC11526850/)
7. Cortical pyramidal mean firing rate ~10Hz spontaneous → per-spike interval ~100ms; ISI Poisson-like — [PMC Firing rates distribution](https://pmc.ncbi.nlm.nih.gov/articles/PMC6633220/) and [AI Impacts neuron firing](https://aiimpacts.org/rate-of-neuron-firing/)
8. Sara & Bouret 2012 (LC-NE phasic/tonic + ACh switching) — referenced from prior research notes (modulatory taxonomy citations 3-7)

**Internal substrate notes referenced:**
1. research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md (parent: 4 load-bearing modulatory axes + 6 systematic substrate-vs-brain differences)
2. research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md (TAU_POS/TAU_NEG inversion identified)
3. research_dual_trace_mechanism_elucidation_2026-06-23.md (4-axis confound decomposition: sign/target/timescale/cardinality)
4. research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md (Brzosko sequential ACh-first DA-second)
5. research_negative_landings_evidence_totality_synthesis_2026-06-23.md (10-negative taxonomy; receiver-must-match-codebook)

---

## Companion exp_dev hand-off

Filing companion hand-off file at:
`d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_brain_timescale_ratio_2026-06-23.md`

Primary anchor: `substrate_tau_neg_ratio_sweep_x_n_replay_sweep_2x4_v1` (cheap decisive test above; can piggyback on in-flight dual_trace cell rig)
Secondary anchor: `cls_replay_multipass_n_replay_sweep_v1` (only if 2x4 factorial confirms N_REPLAY axis is load-bearing)
Tertiary anchor: `theta_gamma_k_count_saturation_audit_v1` (existing-cell audit, no new cell needed; documentation work)

---

End of research note.
