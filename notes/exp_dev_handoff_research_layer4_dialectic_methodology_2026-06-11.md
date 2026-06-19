# exp_dev hand-off -- research: Layer 4 dialectic methodology

Filed-by: research (Opus 2x DEEP drill)
Trigger: notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md
Pause state: respected. Pause-gated. If data/orchestrator_paused.flag exists, do not ship; pre-stage anchors only.

Per [[feedback-no-experiment-design-in-prompts]] -- this hand-off lists ANCHOR pointers, not engineering recipes. exp_dev owns implementation autonomy.

## Anchor candidates (rank-ordered)

### Anchor 1 -- LAYER4-RETRO (cheap decisive test)
Pointer: research note section "Cheap decisive test"
Substrate-product reading: substrate-introspection differentiator -- retrospective classifier validated on 8 weeks of cap_map findings
Tier hint: Tier-1 cheap CPU pilot (2-4 CPU-hr)
Why-now: validates the entire Layer 4 stack BEFORE building cycle-time integration; HARD-PASS/HARD-FAIL pre-registered in note (>=60% recovery on surprise; >=75% on expected; FDR<25%)
Pause-policy: cheap CPU, allowed if pause-flag is structural-only

### Anchor 2 -- LAYER4-SUBSTRATE-NATIVE (substrate-on-substrate validation)
Pointer: research note section "Substrate-native implementation" + P5 prediction
Substrate-product reading: substrate algebra IS the metacognitive mechanism; substrate-cosine tracks external KL surprise
Tier hint: Tier-1 cheap CPU pilot (1-2 CPU-hr after Anchor 1's retrospective data is built)
Why-now: this is the substrate-on-substrate piece -- demonstrates the metacognitive layer is itself substrate-native, not an external add-on
HF threshold: Spearman rho <0.30 between substrate-native score and external KL

### Anchor 3 -- LAYER4-BOCPD-SUSTAINING (sustaining-rate measurement)
Pointer: research note section "Sustaining-rate measurement via BOCPD + BH-FDR"
Substrate-product reading: defensible Tier 1->2 gate criterion with statistical backing
Tier hint: Tier-2 (depends on Anchor 1 producing genuine-surprise time series)
Why-now: this is the actual gate; need to validate BOCPD stabilization within 4-8 weeks of synthetic data
Cost: 1 CPU-hr (BOCPD wrapper + BH on simulated weekly counts)

### Anchor 4 -- LAYER4-OOD-FILTER (Stage 3 adversarial filter)
Pointer: research note Stage 3 (replication + evaluator + context-shift)
Substrate-product reading: noise-control on introspection; prevents inflated sustaining-rate
Tier hint: Tier-2 (depends on Anchor 1's retrospective + at least one re-measurement pass)
Why-now: prediction P4 says filter must drop >=15% of raw surprises; if <5% the system over-counts
Cost: 1-2 CPU-hr

### Anchor 5 -- LAYER4-PREREG-TEMPLATE (operational integration)
Pointer: research note section "Pre-registered hypothesis template"
Substrate-product reading: routing-file-grade integration into cycle protocol
Tier hint: Tier-3 (engineering integration after Anchors 1-3 land)
Why-now: this is the operational machinery; needed to run Layer 4 on live cycles, not retrospective only
Cost: 1 engineering day (template + routing-file glue)

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md
- d:/AI/hd-instrument/notes/substrate_capability_map.md (cap_map row history; needed for retrospective sample)
- d:/AI/hd-instrument/notes/research_drill_substrate_algebra_encoding_shared_basis_2x_2026-06-11.md (shared orthogonal-subspace algebra used by classifier)
- d:/AI/hd-instrument/notes/research_drill_substrate_memory_llm_frontend_hybrid_2x_2026-06-11.md (conformal-margin routing = same family as Stage 3 filter)
- d:/AI/hd-instrument/data/orchestrator_status_log.jsonl (research_delivery history; raw surprise candidates)

## Contract

- exp_dev MUST honor pause flag.
- Anchors are rank-ordered; LAYER4-RETRO first (cheapest decisive test).
- HARD-PASS / HARD-FAIL thresholds pre-registered in the research note. exp_dev does NOT redefine them.
- Per query-privacy: external lit-scans inside experiments must use generic terms (Itti-Baldi, BOCPD, BH-FDR are public concepts; never reference substrate-novel mechanism names in any external API call).
- Self-test: the retrospective decisive test IS the self-test. Re-run quarterly.

## Autonomy declaration

exp_dev owns: implementation language (numpy preferred per project conventions), exact prior-family choice per row type, BOCPD hyperpriors, threshold calibration procedure, when to escalate to GPU (not needed for these anchors), how to integrate with cycle protocol.

research owns: anchor selection rationale, HARD-PASS/HARD-FAIL thresholds, prior-family rationale, cross-thread linkage.
