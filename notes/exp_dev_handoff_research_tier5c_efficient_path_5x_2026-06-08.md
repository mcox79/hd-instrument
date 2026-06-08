# exp_dev hand-off -- research: Tier 5c efficient path (engineering specifics)

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
Prior handoffs:
  notes/exp_dev_handoff_research_tier5c_substrate_intrinsic_aggressive_5x_2026-06-08.md
  notes/exp_dev_handoff_research_tier5c_architecture_speed_routing_5x_2026-06-08.md
  notes/exp_dev_to_research_flamingo_pretest_adapter_required_2026-06-08.md (adapter-entropy trigger)

---

## Pause state block

Before dispatching any anchor below: verify data/orchestrator_paused.flag does NOT exist.
Do not ship if paused. Check with orchestrator if unclear.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Pre-reg bands below are
RESEARCH recommendations -- exp_dev validates and may refine before queue dispatch.

---

## Context

Tier 5b HF (5 attempts; single-position inject fails; fact-transmission zero). Flamingo
pretest confirmed: raw substrate HD vectors as K/V give attention entropy 0.996 (uniform;
useless); a brief adapter training drops to 0.809 (sharpens). Adapter is mandatory.

The research note provides the full 5-phase sequence. This handoff names the first three
phases as actionable anchors, in cheapest-decisive-first order.

---

## Anchor candidates (rank-ordered)

### Anchor 1: t5c_wirtinger_gradient_smoke_v1

Anchor pointer: Research note Level 5 Sections 5.1-5.4 (interface API) + Level 6 Phase A sub-phase A1.
Substrate-product reading: Before any GPU budget is committed, confirm that the
SubstrateCrossAttention module has valid gradient flow (gate.grad not None; adapter grads
not None; no NaN; backbone frozen params have grad=None). This is a 5-minute CPU check
that eliminates implementation bugs. If this fails, nothing else in the Flamingo path works.
Tier hint: CPU laptop; < 5 min; no data needed (random inputs).
Why-now: gates every subsequent anchor; costs nothing; should be the very first anchor.

Pre-reg bands:
  HARD-PASS: all adapter parameter gradients finite and non-None after backward(); gate.grad
    finite; no backbone parameter has non-None gradient (backbone is frozen).
  HARD-FAIL: any NaN/Inf gradient in adapter or gate; or any backbone parameter has non-None
    gradient (freeze is broken).

### Anchor 2: t5c_codebook_init_quality_v1

Anchor pointer: Research note Level 2 Section 2.1 (Option A: seed from LLM hiddens) +
  Level 2 Section 2.2 (codebook size 32k) + Level 6 Phase A sub-phase A2.
Substrate-product reading: Determines whether the LLM-hidden-state codebook initialization
produces a non-degenerate codebook (diverse atoms covering the representation space). If
utilization > 30%, the codebook initialization strategy is validated and Phase B training
will not start from a collapsed codebook. If < 5%, switch to random init before Phase B.
Tier hint: CPU or local GPU; < 10 min.
Why-now: codebook quality check gates Phase B. A collapsed codebook makes Phase B
un-interpretable.

Pre-reg bands:
  HARD-PASS: > 30% of atoms are nearest-neighbor to at least one token from the 1k held-out set.
  MIDDLE-BAND: 10-30% utilization (partial collapse; increase seed data or run atom reset).
  HARD-FAIL: < 5% utilization (degenerate; switch to random complex unit-circle init Option B).

### Anchor 3: t5c_flamingo_single_layer_pythia160m_v1

Anchor pointer: Research note Level 3 Sections 3.1-3.6 (Flamingo training schedule) + Level 6
  Phase B + Level 7 Phase B anchor.
Substrate-product reading: The primary decisive Tier 5c gate. Frozen Pythia-160M backbone +
single SubstrateCrossAttention insert at layer L4 + bottleneck adapter (substrate 8192-dim x2
-> 256 -> head-dim) + sigmoid gate initialized at -4.0. Train 5k steps on factual QA pairs.
If top-1 accuracy > 40% on held-out set: Flamingo gated cross-attention works for substrate
fact-transmission. This result unblocks Phases C and D (demo-quality scaling). If FAIL:
diagnostic via gate trajectory and attention entropy determines whether the failure is adapter
size, retrieval quality, or training data quality.
Tier hint: single A100 or equivalent; < 1 GPU-hour for Phase B.
Why-now: this is the cheapest decisive answer to "does the approach work." After 5 Tier 5b
failures (single-position inject), Phase B with proper Flamingo architecture (cross-attention
not prefix injection) is the correct next test.

Pre-reg bands:
  HARD-PASS: top-1 accuracy > 40% on held-out factual QA pairs at step 5000.
  MIDDLE-BAND: accuracy 20-40% AND gate_scalar has moved (< -3.0 by step 1000). Partial
    transmission; increase training steps or QA set size before concluding failure.
  HARD-FAIL: accuracy < 20% at step 5000 AND/OR gate_scalar has not moved from init range
    (> -3.5 at step 1000). Mechanism broken; diagnose gate, adapter, or retrieval.

### Anchor 4 (conditional on Anchor 3 PASS): t5c_flamingo_qwen05b_v1

Anchor pointer: Research note Level 1 Section 1.3 (Qwen-0.5B config) + Level 6 Phase C.
Substrate-product reading: Test whether the adapter design is architecture-agnostic (works
on Qwen GQA architecture, not just Pythia). Uses config: hidden=896, heads=14, head_dim=64;
check num_key_value_heads for GQA before wiring K/V adapter output.
Tier hint: same as Anchor 3 (single A100, < 1 GPU-hour).
Why-now: conditional on Anchor 3 PASS. Architecture generality is needed before Phase D
(Qwen-2.5-3B is the demo model).

Pre-reg bands:
  HARD-PASS: top-1 accuracy > 40% (matches Anchor 3 benchmark on same QA set).
  HARD-FAIL: accuracy < 20% (Qwen architecture-specific failure; adapter wiring incorrect).

---

## Context pointers

- d:/AI/hd-instrument/notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
  (primary source: all 7 levels, full pre-reg bands, adapter/gate design specs)
- d:/AI/hd-instrument/notes/exp_dev_to_research_flamingo_pretest_adapter_required_2026-06-08.md
  (adapter-entropy empirical finding: entropy 0.996 -> 0.809; Qwen-0.5B config)
- d:/AI/hd-instrument/notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
  (differentiability analysis; engineering paths; 14 citations)
- d:/AI/hd-instrument/notes/research_drill_tier5_substrate_intrinsic_llm_3x_2026-06-07.md
  (Tier 5 architecture evaluations; Arch 8 Hopfield path; precedents)

---

## Contract section

Research has completed the engineering-specifics drill: layer insertion (L4 Pythia, L8-L12
Qwen), codebook training (EMA + commitment loss + entropy reg; Option A seeded init; 32k
atoms start), Flamingo schedule (gate=-4.0 sigmoid; Xavier adapter; frozen backbone; 5k steps
AdamW lr=2e-4), continued pretraining cost (frozen backbone = 0 tokens; Phase A cost < 10
GPU-minutes), interface API (SubstrateCrossAttention nn.Module; bottleneck adapter 8192*2->256->head_dim;
Wirtinger gradient flow confirmed algebraically), and 5-phase sequence with HARD-PASS/HARD-FAIL bands.

Tier 5b diagnosis: single-position injection fails because a single prefix token cannot guide
the LLM to selectively use a substrate fact. Flamingo cross-attention provides K/V at every
position at the insertion layer, structurally addressing the Tier 5b failure mode.

The decisive test is Anchor 3 (Phase B fact-transmission, < 1 GPU-hour). Anchors 1-2 cost < 15
minutes and gate Anchor 3.

---

## Autonomy declaration

exp_dev has full autonomy to:
- Design the SubstrateCrossAttention nn.Module architecture within the constraints named above.
- Choose specific QA training data construction method (template-based from substrate bindings).
- Select between real+imaginary concatenation vs complex-valued linear adapter (either is correct).
- Adjust batch size and step count within the HARD-PASS bands.
- Schedule anchors in the queue (all three Phase A anchors can run in parallel; Anchor 3
  requires both A1 and A2 to PASS first).

exp_dev does NOT have autonomy to:
- Skip the gradient smoke (Anchor 1) before the GPU Phase B run.
- Insert at layers outside the L3-L5 zone for Pythia-160M without escalating to research.
- Use a codebook larger than 100k atoms in Phase A-B without escalating (memory budget risk).
