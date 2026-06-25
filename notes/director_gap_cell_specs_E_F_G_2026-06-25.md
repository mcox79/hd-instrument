# Three gap cell specs from 2026-06-25 morning ideas (E / F / G)

Director pre-authored cell specs closing gaps in the ideas backlog. NONE dispatched. USER will decide when push lane is confirmed working post-orchestrator and Wave D/E land.

---

## Cell E: substrate_audit_trail_lock_in_frequency_separated_v1 (Barrier 5 via USER's freq insight)

**Strategic:** Audit-trail v2 (yesterday) HARD_FAIL_DECISIVE at proper power because the bind operation smears provenance tags into the same channel as content (the "fingerprinting in ink" analogy). USER directive 5 from this morning: if mechanisms ride different lock-in frequencies (Cell C tests this for plasticity rules), then **provenance tags can ride a separate audit-frequency**. Same W, different demodulation lanes. Brain analog: theta-phase carries temporal context; gamma carries local content; different rhythms on same neurons.

**Lane:** 4 (substrate-product audit axis)
**Routing:** remote_cpu_queue (CPU-feasible at modest scale)
**Config:** N=2048, V=100, V_predicates=8, M=500 triples + M_unknown=200, 3 seeds [7,17,23]
**Arms** (4):
1. ARM_BASELINE_NAIVE (no audit; matches v2 NAIVE arm 0.222)
2. ARM_BIND_TAG_SAME_CHANNEL (the v2 mechanism that HARD_FAILed; control reproducing the smear-in-ink failure)
3. ARM_LOCK_IN_AUDIT_FREQ_SEPARATED (content stored at f_content=1.0; provenance tag at f_audit=4.0; demodulate at each freq for retrieval/audit independently)
4. ARM_LOCK_IN_PLUS_S2_GRAPH_SPOKE (combine: lock-in freq separation + hub-spoke S2 atom-graph as cross-validation channel)

**HARD bands:**
- HARD_PASS_CHAIN_GRADE: best lock-in arm provenance ≥ 0.85 AND refuse ≥ 0.50 AND CV ≤ 0.05
- HARD_PASS: best ≥ 0.75 AND beats ARM_BIND_TAG_SAME_CHANNEL by ≥ 0.20
- HARD_FAIL: ALL lock-in arms within ±0.05 of ARM_BIND_TAG_SAME_CHANNEL (separate-frequency doesn't help)

**Discriminator:** ARM_3 vs ARM_2 isolates whether frequency-separation works on its own; ARM_4 vs ARM_3 isolates whether atom-graph cross-validation adds beyond freq-separation alone.

**Sanity rail:** ARM_BIND_TAG_SAME_CHANNEL must reproduce v2 V3 prov 0.16 within ±0.05 (confirms regime match).

**Timeout:** 3600s
**Cross-thread:** depends on Cell C (lock-in primitive) confirming HARD_PASS on plasticity-rule frequency separation; can dispatch in parallel but Cell C result informs interpretation.

---

## Cell F: substrate_multihop_cleanup_consolidation_hybrid_v1 (Barrier 1 — combines USER's two insights)

**Strategic:** USER directive 1: substrate has BOTH cleanup-every-step (Wave14R K50 chain-grade in Store at N=16384) AND memory consolidation primitive (Wave E Cell A). These are COMPLEMENTARY:
- **Cleanup-every-step** handles NOVEL paths via per-step error correction (hippocampus analog)
- **Consolidation** handles FREQUENT paths via direct compound atom (cortex analog)

Brain uses both. Substrate should too. This cell tests the hybrid: when a 2-hop chain is FIRST queried, use cleanup-every-step (hippocampal route); after K_THRESH queries, write a compound consolidated atom and use 1-hop direct retrieval (cortical route).

**Lane:** 1 (substrate-native)
**Routing:** remote_cpu_queue
**Config:** V_C=200, V_P=10, N=8192, K_SET=20, n_chains=300 per arm, K_THRESH=3, 3 seeds
**Arms** (5):
1. ARM_NAIVE_HARD_2HOP (control; reproduces 0.65 baseline)
2. ARM_CLEANUP_EVERY_STEP (Wave14R K50 mechanism applied to 2-hop; substrate-native; CHAIN-GRADE-eligible at this depth per Store ref)
3. ARM_CONSOLIDATION_ONLY (Cell A mechanism reproduced; consolidate frequent paths after K_THRESH=3)
4. ARM_HYBRID_CLEANUP_THEN_CONSOLIDATE (cleanup-every-step for first K_THRESH queries; then promote to consolidated direct atom)
5. ARM_HYBRID_PLUS_HUB_SPOKE_ENCODER (above + use hub-spoke v3 encoder if available; tests interaction with anisotropic encoder)

**HARD bands:**
- HARD_PASS_BREAK_CEILING: best hybrid arm top1 ≥ 0.95 AND 5x improvement over naive 0.65 AND CV ≤ 0.05
- HARD_PASS: best ≥ 0.85
- MIDDLE_BAND: 0.75-0.85
- HARD_FAIL: best ≤ 0.75

**Discriminator:**
- ARM_2 isolates cleanup-every-step contribution
- ARM_3 isolates consolidation contribution
- ARM_4 = ARM_2 + ARM_3 superlinearly? → hybrid is the answer; or additively? → both work independently
- ARM_5 isolates encoder contribution

**Sanity:** ARM_1 must reproduce 0.65 within ±0.03 (cross-validate with last night's beta-sweep). Timeout 2400s.

**Cross-thread:** depends on Wave E Cell A (consolidation) landing first to confirm ARM_3 mechanism works at all; Cell F tests COMBINATION.

---

## Cell G: substrate_cross_layer_top1_targeted_re_eval_v1 (Skunkworks-proposed; cheap)

**Strategic:** Skunkworks ruled Cell 7 (cross-layer FULL) as MEASURED_MECHANISM not chain-grade because top1 indep=0.232 vs unigram=0.217 = +7.05% rel; chain-grade bar is +61.6% rel (n1_v3 precedent). Skunkworks proposed: top1-targeted re-eval on the EXISTING indep_2L W matrices — no new training, just rerun the readout with top1 as PRIMARY metric and TEMP/lambda tuned for top1 not BPC.

**Lane:** 1 (substrate-native; same as Cell 7 v2 RESCUE FULL)
**Routing:** local_cpu_queue (cheap; reuses existing W matrices from Cell 7 metrics)
**Config:** load Cell 7's stored W per-seed; rerun grid sweep with TEMP grid extended toward smaller T (where top1 sharpens) and TEMP_GRID_FOR_TOP1 separate from TEMP_GRID_FOR_BPC; 3 seeds [7,17,23] matching Cell 7
**Arms** (3; same as Cell 7's independent-W arms):
1. ARM_SINGLE_LAYER_top1_targeted
2. ARM_2_LAYER_INDEPENDENT_top1_targeted
3. ARM_3_LAYER_INDEPENDENT_top1_targeted

**HARD bands:**
- HARD_PASS_CHAIN_GRADE_TIER_PROMOTE: ARM_2 OR ARM_3 top1 ≥ unigram × 1.616 (= 0.217 × 1.616 = 0.351) — promotes Cell 7 from MM to chain-grade per Skunkworks
- HARD_PASS_RELEVANT_LIFT: any arm top1 ≥ unigram × 1.30 (= 0.282) — significant but not chain-grade
- HARD_FAIL_NO_LIFT: all arms top1 ≤ unigram × 1.10 (= 0.239) — confirms Cell 7 MM tier stands

**Sanity:** with TEMP=0.05 lambda=0.1 (Cell 7's best BPC config), top1 should match Cell 7 result of 0.232 within ±0.005.

**Timeout:** 1200s (cheap; no training)
**Cross-thread:** if HARD_PASS, route to Skunkworks for tier promotion of Cell 7 to chain-grade-eligible. This is the cleanest path to closing the "first Stage 2 architectural atom" claim that I over-claimed yesterday.

---

## Dispatch sequencing (when ready)

1. Wait for orchestrator to confirm Wave D + Wave E pushed to remote queues (in flight)
2. Watch Cell A (Wave E) land — informs whether consolidation works at all → green-lights Cell F dispatch
3. Watch Cell C (Wave E) land — informs whether lock-in works for plasticity → green-lights Cell E dispatch
4. Cell G can dispatch IMMEDIATELY (cheap; doesn't depend on others; just needs push lane working)

Total compute budget post-Wave-D/E landings: Cell E + Cell F + Cell G ≈ 90min on remote/local CPU + no GPU.

## Status

All 3 specs ON DISK. Not dispatched. Awaiting USER green-light + Wave D/E landings to inform sequencing.
