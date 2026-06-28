# Strategic framework: phase-diagram characterization of all chain-grade capabilities

**Date:** 2026-06-28 ~00:05Z (16:05 PDT post-compaction)
**Directive:** USER 2026-06-27: "we want to understand how all our load bearing capabilities perform across the phase diagram. Then we'll want to consider, once all are chain grade and we're ready to progress, if we want to designate phase operations for each characteristics which determines a phase shift for certain procedures"
**Connects to:** USER 2026-06-22 latent-capability directive (substrate acts at any phase position + data survives phase transformations); 38-42 phase-diagram atoms + 11 transform-survival atoms already banked

---

## Two-layer architecture USER outlined

**Layer 1 (now):** for each chain-grade primitive, characterize WHERE IN PARAMETER SPACE it works vs fails. The phase diagram.

**Layer 2 (when all Layer 1 done):** designate phase operations — substrate detects its phase position and TRIGGERS the right procedure. e.g. "when we cross into the high-interference phase, switch from per-hop cleanup to bidirectional meet-in-middle."

This is the substrate-as-phase-aware-system vision. Like a transmission shifting gears based on speed + load.

---

## CHAIN-GRADE PRIMITIVES INVENTORY (per BACKUP + today's additions)

### Stage 1 (base) — phase-diagram axes per capability

| Primitive | Phase-diagram axes | Status |
|---|---|---|
| Storage M=500/N=8192 top1=1.0 | N × M × bind-noise × readout-method | Partial atoms exist; need consolidated sweep |
| Pattern completion top1=1.0 from 50% corruption | N × corruption-fraction × cleanup-iterations | Partial; need cliff localization |
| WM K=4096 multi-bank | K × bank-size × intra-bank interference × routing-noise | Some atoms (capacity_v2c); needs phase map |
| Sequence binding K=20 | K × N × position-noise × tag-density | Need full sweep |
| Continual learning CRISPR forget=0.006 | append rate × N × forget mechanism | Partial; need cliff |
| KG ingest FB15k/ConceptNet/HotpotQA | M atoms × V relations × K hops × encoder choice | Per-corpus atoms exist; need cross-corpus phase map |
| Refuse-gate V_REL=256 | V_REL × tau × cosine-distribution shape | Some atoms; need tau-sensitivity sweep |
| Intent classifier n=100 | n classes × N × confusion-density | Need scaling sweep |
| Capacity v2c GPU multi-bank K=4 α=4 | α (M/N) × K-sharding × bank-overlap | Best characterized; α phase map exists |

### Stage 2 (optimization) — phase-diagram axes

| Primitive | Phase-diagram axes | Status |
|---|---|---|
| Ultrametric clustering (cortex content extraction) | M items × cluster-overlap × ultrametric-depth | Needs phase map |
| TWO_TIER generational W | promotion-criterion × tier-1 vs tier-2 capacity | Partial |
| NREM replay | replay rate × consolidation duration × interference | Partial |
| Partition routing M=10M | M × N_partitions × balance × per-partition encoder | Partial |
| ANCHOR 1 v4 partition-by-source-class | tau (0.15 default) × N_files × class-overlap | Validated at chain-grade default; needs phase sweep |
| Lock-in amp | SNR × carrier-frequency × harmonic-content | Partial |
| Bidirectional meet-in-middle | depth × meeting-radius (regime-narrowed; need broader phase) | v2 chain-grade at d=5; v3 GPU showed regime-specificity |
| ANCHOR 3 coarse-grain promotion | cap_drop × ULTRA-gap × USER_DIRECTIVE-preservation | Validated at default; needs sweep |
| ANCHOR 4 time-decay eviction | eviction_frac × reingest-rate × USER_DIRECTIVE | Validated at default; needs sweep |

### Stage 3 (higher functions) — phase-diagram axes

| Primitive | Phase-diagram axes | Status |
|---|---|---|
| Multi-hop depth-15 at 0.808 | depth × V_C × N_chains × cleanup-mechanism | Some atoms; needs depth-sensitivity full map |
| Compositional generation +0.724 | composition depth × variance × baseline strength | Partial |
| SEMANTIC battery 5/6 arms | task class × concept count × variance | Partial |
| **Substrate compositional reasoning at depth=5 (NEW today)** | depth × V_C × N_chains × per-step cleanup mechanism | Cycle 1 v3 + v4 explore N_chains; needs depth-extension to 8/10/15 (v5 dispatched) |
| **Parietal MOVABLE-rebind (NEW today)** | grid_size × n_objects × move-frequency × position-noise | Smoke-only; needs full phase sweep |
| **Parietal RELATIONAL-spatial (NEW today)** | n_distractors × grid × n_relations × relational-distance | v2 smoke HARD_PASS; needs distractor-sweep phase map |
| **task_vector HRR ICL (NEW today)** | K-shot × N_tasks × task-overlap × bundle-density | Smoke chain-grade; needs K-sweep up to capacity cliff |
| **Engram density-matched methodology (NEW today)** | density × alignment-tolerance × N | Methodology atom; methodology phase: where does alignment break down? |
| Order-sensitive sequence binding | alpha (M/N) × position-noise × tag-density × N_pairs | BTSP arc gave smoke chain-grade at alpha=0.049; needs alpha-cliff sweep |
| Hippo→cortex handoff (FULL pending) | N_h × N_c × M × N_replay × sparse density | Smoke chain-grade-quality; full landing pending |

---

## Phase-diagram cell template (proposed)

Each chain-grade primitive gets a **`exp_<primitive>_phase_diagram_v1.py`** cell:

**Inputs:** chain-grade-validated cell + axes to sweep
**Sweep:** N points along 2-3 most informative axes (per Bayesian/Fisher-information picks)
**Output:** verdict tier per point → phase map matrix
**Discriminator:** chain-grade region (verdict=HARD_PASS) vs MIDDLE_BAND vs HARD_FAIL
**Cliff localization:** Bayesian active sampling for cliff edges
**Deliverable:** atomized `<primitive>_phase_diagram` atom with stored phase map (load-bearing for Layer 2)

**Discipline (per today's locked rules):**
- META_RULE_AC: each point cited with MEASURED metrics.json path
- META_RULE_AG: sweep MUST include points where baseline lands in discriminating band [0.30, 0.70] (don't only test default regimes)
- META_RULE_AE: phase map data structure should reference absolute paths per cell
- META_RULE_AH: atomic write per-point metrics
- META_RULE_AF: arms-must-differ throughout sweep
- CRLB pre-validation: for each axis, confirm HP threshold is reachable given chosen scale

---

## STAGING — when to do this

**NOT NOW** — current state:
- Multiple Stage 3 gaps still pending (TOM, schema-driven, counterfactual, temporal — drills in flight)
- Many in-flight cells (Cycle 1 v5 depth=10, M-CFU v7B, parietal v2 FULL, hippo handoff, pfc_goal v3, tip_of_tongue v2, Wave 3B cells)
- Skunkworks batch atomizing 14 atoms (some of which may become new chain-grade)
- Remote queue saturated (12 cells deep behind cortex_hippo_handoff)

**WHEN TO START PHASE-DIAGRAM WORK** (USER's "once all chain-grade"):
- After current Stage 3 gap-filling wave returns + atomizations complete
- After remote queue clears (next 12-24h likely)
- Priority order: most load-bearing primitives first (multi-hop depth / partition routing / parietal / WM-cap)

**RIGHT NOW:** continue full-auto Stage 3 gap-filling (TOM + schema-driven + counterfactual + temporal drills + cell-author follow-throughs). Phase-diagram work is the NEXT-NEXT wave.

---

## LAYER 2 — phase operations (when Layer 1 complete)

Once all chain-grade primitives have phase maps, substrate becomes phase-aware:

**Example phase operations:**
- Multi-hop reasoning: "if depth>=8 AND V_C<=500, switch from baseline cleanup to bidirectional meet-in-middle" (use Layer 1 cliff data)
- Importance signaling: "if d≥16384 AND M<d, TRACE channel only (PCA below CRLB)" (use M-CFU v7B Layer 1 result)
- Schema-driven inference: "if cluster_cos<0.3 AND target_familiarity>0.7 → TOT detection criterion" (per tip_of_tongue Option C ratio)
- Partition routing: "if tau<0.15 AND query-class-overlap>0.5 → use partition-then-set semantics" (per ANCHOR 1 v4)

This requires:
1. Layer 1: characterize where each primitive's phase boundaries are (~10-20 phase-diagram cells)
2. Layer 2: substrate-level controller that detects current phase from substrate state + queries → selects appropriate procedure
3. Atomize phase-operation rules as `phase_op_<primitive>` atoms

**Brain analog:** thalamus / basal ganglia for procedure selection; prefrontal for context-sensitive control; cerebellum for forward-model selection. Substrate analog: a small phase-classifier module + procedure-router.

---

## INTEGRATION WITH M3 GOAL

For glass-box conversational AI (12-18mo target), Layer 2 phase-operations are the engine that lets substrate handle conversation:
- Different conversational regimes (factual / reasoning / introspective / TOM-heavy / abstract) require different procedure mixes
- Phase-aware substrate can route conversation through right procedures
- Without Layer 2, substrate is a fixed-procedure system (can't adapt)

This is consistent with USER's M3 vision. Layer 2 is the "operating system" of conversation.

---

## NEXT ACTIONS

1. Stage this framework in BACKUP UPDATE #19 (concise reference)
2. Continue current full-auto wave (4 in-flight + 3 drills returning)
3. When current wave completes + queue clears, dispatch FIRST phase-diagram cell (recommend: **multi-hop depth-sensitivity** — highest leverage; many open questions)
4. Atomize this framework as `phase_diagram_layer1_layer2_strategic_framework` atom in next Skunkworks batch

-- Research (Opus 4.7-1M)
