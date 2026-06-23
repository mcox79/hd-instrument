# exp_dev hand-off — research: sparse-allocation routing learning

Filed-by: research (Opus 4.7-1M)
Date: 2026-06-23
Trigger: USER drill de-risking top-tier enabling Path #3 (sparse engram allocation). Substrate today uses RANDOM sparse positions per atom; brain sparse coding works because routing is LEARNED. Question: can substrate gain learned routing without breaking forward-only?
Source research note: `d:/AI/hd-instrument/notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md`
Pause state: respect `data/orchestrator_paused.flag` at dispatch time.

**Per [[feedback-no-experiment-design-in-prompts]]:** research does NOT specify cell mechanics, queue choice, smoke parameters, or HARD-band tuning. exp_dev owns those. Below are anchor candidates with substrate-product reading + tier hint + why-now. exp_dev is empowered to re-rank, descope, or substitute mechanism per its own contract.

---

## Anchor candidates (rank-ordered)

### Anchor 1: alloc_routing_excitability_trace_v1 (TOP — substrate-native, forward-only)

- **Pointer:** `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md` (CHEAP DECISIVE TEST section — 3-arm pre-reg)
- **Mechanism class:** 3-arm cell — ARM_RANDOM (baseline, current substrate) vs ARM_EXCITABILITY_TRACE (Tonegawa-CREB analog: per-position scalar trace + softmax allocation + rich-get-richer) vs ARM_KWTA_HEBBIAN (Marr-Albus cerebellar analog: top-K + Hebbian weight update). All forward-only; no backprop.
- **Substrate-product reading:** highest-leverage single-cell test of whether substrate gains anything from learned vs random sparse routing. HARD_PASS unblocks Phase-1 self-mapping (alternative rescue path to encoder upgrade), Phase-2 autoatom, and adds substrate-product moat (no published HD/VSA precedent for forward-only position-trace allocation).
- **Tier hint:** chain-grade-targetable if ARM_EXCITABILITY_TRACE M1 ARI lifts by ≥0.15 over ARM_RANDOM with p<0.05 across 3 seeds AND M3 neighbor-overlap ≥0.25. Discriminator is RELATIVE (between arms), not absolute, so the imperfect v1-lexical-family ground truth (~10% labeled coverage) does not block chain-grade certification.
- **Why-now:** independent of and complementary to the encoder upgrade path (which HARD_FAILED 4-of-4 arms 2026-06-23). Allocation routing operates at the STORAGE LAYER, not the encoder input layer — different mechanism class than the prior null. Cell is ~45-60 min laptop CPU; no encoder retraining needed.
- **Discriminator (load-bearing):** ARI(ARM_EXCITABILITY_TRACE) - ARI(ARM_RANDOM) ≥ 0.15 at p<0.05.
- **HARD_FAIL meaning:** substrate-native learned routing at chain-grade scope is structurally null vs random. META: "random sparse allocation is provably as good as learned at N=4096/M≤1000." Forces pivot to Anchor 2.

### Anchor 2 (conditional): alloc_routing_backprop_minimum_v1 (POST Anchor 1 HARD_FAIL)

- **Pointer:** `notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md` (HONEST ASSESSMENT section)
- **Mechanism class:** single linear projection `W: encoder_output → K-position-logits`, trained via InfoNCE contrastive loss on existing chain-grade KG edges (positive pairs = (atom, KG-neighbor); negatives = (atom, random non-neighbor)). ~50K-200K params. Routing-layer learner, NOT representation-layer (distinct from the USER-2026-06-22 MiniLM/BGE forbid which was on REPRESENTATION encoders).
- **Substrate-product reading:** minimum backprop infrastructure for substrate-native routing. Far less than char-LSTM (~5M params); single Adam-trained linear layer. ~1-2hr CPU.
- **Tier hint:** chain-grade-targetable if M1 ARI lifts ≥0.15 over ARM_RANDOM with p<0.05. Same discriminator as Anchor 1; different mechanism.
- **Why-now:** ONLY conditional on Anchor 1 HARD_FAIL. USER 2026-06-23 explicitly opened to "being wrong here — backprop encoder allowed if needed." Confirm USER acceptance for routing-layer-backprop (distinct from representation-layer) BEFORE dispatch.
- **Discriminator (load-bearing):** identical to Anchor 1 — RELATIVE ARI lift.
- **HARD_FAIL meaning:** even minimum backprop cannot give learned routing lift at substrate's chain-grade scope. META: "substrate's KG-routing problem is REGIME-INVARIANT to learning at production scope." Substrate-product implication: stop investing in routing-layer learning; lift random-allocation to first-class primitive with full envelope characterization.

### Anti-anchor: DO NOT re-run encoder-side learning (SoftHebb / FPE / Foldiak) variants

The prior `exp_encoder_dual_gain_softhebb_v1` HARD_FAILed ALL 4 forward-only encoder arms at sigma=1.5 cleanup + Path-A BPC. The mechanism class (weight-based forward-only learning at N=4096 with limited data) is structurally exhausted for ENCODER REPRESENTATION. This drill explicitly tests a DIFFERENT layer (allocation routing, not encoder representation) — do not collapse the distinction. Dispatching another SoftHebb-on-encoder variant would burn CPU confirming a null already established. Per [[feedback-substrate-mine-capacity-before-extrapolating]] and [[feedback-fix26-predispatch-verify-the-referent-gate]].

### Anti-anchor: DO NOT dispatch Anchor 2 before Anchor 1 resolves

Anchor 2 is conditional on Anchor 1 HARD_FAIL. Pre-queueing both wastes spawn budget (per [[feedback-fix14-spawn-budget]]) and ignores the discriminator outcome. Sequence the dispatch.

---

## Context pointers (paths only, not summaries)

- `d:/AI/hd-instrument/notes/research_drill_sparse_allocation_routing_learning_2026-06-23.md` — this drill (full L1-L5 + 3-arm pre-reg)
- `d:/AI/hd-instrument/notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` — prior encoder-upgrade drill (all 4 arms HARD_FAILed; mechanism distinction noted in anti-anchor above)
- `d:/AI/hd-instrument/data/exp_encoder_dual_gain_softhebb_v1/metrics.json` — load-bearing HARD_FAIL data
- `d:/AI/hd-instrument/notes/research_2x_revival_v2e_self_mapping_HF_2026-06-23.md` — v2e encoder-bound diagnosis (allocation-routing is alternative rescue path)
- `d:/AI/hd-instrument/notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` — parent self-mapping drill
- `d:/AI/hd-instrument/notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` — hub-and-spoke architecture context (allocation-trace composes at hub level)
- `d:/AI/hd-instrument/hdlab/kg_traversal.py` — KGStore primitive (existing allocation interface)
- `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py` — encoder (unchanged in this cell)
- `d:/AI/hd-instrument/hdlab/iterative_attractor.py` — cleanup primitive (composes with excitability-trace)
- `d:/AI/hd-instrument/data/substrate_index/` — chain-grade KG with v1-lexical-family labels for M1 discriminator

---

## Contract

- exp_dev owns cell mechanics, smoke parameters, queue choice (laptop CPU for Anchor 1 ~45-60 min; laptop CPU for Anchor 2 ~1-2hr if conditional dispatch fires), schema-vet, formula-selftests, and HARD-band tuning.
- exp_dev MAY descope or substitute mechanism per its own contract (e.g., test only 2 arms initially if budget tight; drop ARM_KWTA_HEBBIAN if SoftHebb prior is sufficient evidence).
- exp_dev MUST honor `data/orchestrator_paused.flag` at dispatch time.
- exp_dev MUST commit prereg notes to origin/main BEFORE any remote dispatch (per [[feedback-commit-prereg-notes-before-remote-dispatch]]).
- exp_dev MUST run `tools/predispatch_check.py alloc_routing_excitability_trace_v1` to verify no prior cell with overlapping referent (per [[feedback-fix26-predispatch-verify-the-referent-gate]]).
- exp_dev MUST verify Anchor 1 HARD_FAIL verdict BEFORE dispatching Anchor 2 (sequence dependency) AND confirm USER acceptance for routing-layer-backprop (distinct category from representation-layer MiniLM/BGE forbid).

## Autonomy declaration

Research dispatches THIS hand-off as advisory. exp_dev is empowered to:
- Re-rank anchors per its own pre-dispatch verify-the-referent gate
- Substitute discriminator metric per cert-owner consultation (e.g., use modularity-Z from v2e infrastructure instead of ARI vs v1-families)
- Descope Anchor 1 to 2-arm (RANDOM vs EXCITABILITY_TRACE) if K-WTA-Hebbian is deemed redundant with prior SoftHebb HARD_FAIL
- Defer if pipeline is at the ≤3-in-flight ceiling (per [[feedback-fix14-spawn-budget]])
- Hold Anchor 2 pending USER confirmation on routing-layer-backprop acceptability

Return-of-finding contract: post-dispatch metrics flow to verdict_handler; verdict_handler updates cap_map; research consumes verdict via monitor and decides whether to file a follow-on drill (Anchor 2 conditional dispatch + ablation sweep on HARD_PASS).
