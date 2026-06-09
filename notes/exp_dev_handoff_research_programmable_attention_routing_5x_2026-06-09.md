# exp_dev hand-off -- research: programmable attention routing 5x drill

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: d:/AI/hd-instrument/notes/research_drill_programmable_attention_routing_5x_2026-06-09.md

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored
by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as
implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: par_2source_gate_pythia160m_v1 [PRIORITY 1 -- gates all others]

Anchor pointer: Research note Section 7 (Cheap decisive test) and Section 8 Prediction P1
Substrate-product reading: Pythia-160M frozen backbone + learned scalar gate per layer (tanh,
  init=0) + substrate cross-attention stream, activated at layers L >= 6. Trained on a retrieval-
  dependent task (~10K examples). If learned gate improvement over no-substrate baseline >= 10%,
  the per-layer multi-source gate architecture is viable at this scale. If < 5%, route to API-level
  RAG injection as the primary substrate integration method.
Tier hint: local CPU, ~3-5 days engineering + 2-4 hours training. CHEAPEST DECISIVE TEST. Must
  run first -- gates A2, A3, A4.
Why-now: This directly validates or refutes the user's proposed v3.0 architecture at minimal cost.
  Path A (Flamingo-style gate at L4+L5) is already showing 15-17% improvement; this anchor
  systematically measures the general per-layer learned gate gain on substrate as a stream.

Pre-reg bands:
  HARD-PASS: >= 10% absolute improvement on retrieval questions vs no-substrate baseline
  MIDDLE-BAND: 5-10% improvement (viable but needs larger model to confirm)
  HARD-FAIL: < 5% improvement OR regression below baseline

### Anchor 2: par_fixed_vs_learned_gate_ablation_v1 [PRIORITY 2]

Anchor pointer: Research note Section 8 Prediction P2 and Section 4.4 (External control)
Substrate-product reading: Using the N=2 model from A1, compare learned gate values vs fixed
  gate scalars (grid: 0.1, 0.3, 0.5, 0.7 applied uniformly to all activated layers). Measures
  the performance cost of replacing learned gate with externally configurable gate. This directly
  answers whether the "per-tenant gate configuration" product claim (Section 5.3) is viable.
Tier hint: local CPU, ~1 day on top of A1 infrastructure. A1 must complete with PASS or MID.
Why-now: The commercial differentiation of substrate depends on external controllability. If fixed
  gate achieves >= 70% of learned gate gain, external control is viable. If < 50%, the product
  cannot promise configurable gate without per-customer training cycles.

Pre-reg bands:
  HARD-PASS: fixed gate (best scalar from grid) achieves >= 70% of learned gate improvement
  MIDDLE-BAND: 50-70% of learned gate improvement
  HARD-FAIL: < 50% of learned gate improvement

### Anchor 3: par_layer_range_ablation_v1 [PRIORITY 3]

Anchor pointer: Research note Section 8 Prediction P3 and Section 3.4 (layer coupling)
Substrate-product reading: For the 2-source learned gate (from A1), sweep which layer range
  activates the substrate gate: {L < N/2 (early), L >= N/2 (late), all layers}. Determines whether
  the substrate stream should be restricted to semantic-stage layers for optimal contribution.
  Informs the default gate configuration for enterprise deployment.
Tier hint: local CPU, ~0.5-1 day on top of A1 infrastructure. A1 must complete first.
Why-now: The layer-range choice directly affects the per-tenant gate configuration template. If
  late-only beats early-only by >= 5%, this hardcodes a constraint in the product config spec.

Pre-reg bands:
  HARD-PASS: late layers (L >= N/2) outperform early layers by >= 5% on task
  MIDDLE-BAND: no statistically significant difference (< 2% gap)
  HARD-FAIL: early layers outperform late layers (architecturally unexpected; needs investigation)

### Anchor 4: par_3source_gate_qwen1p5b_v1 [PRIORITY 4]

Anchor pointer: Research note Section 8 Prediction P4 and Section 6 Risk R5 (interference)
Substrate-product reading: 3-source gate (self-attention + substrate + synthetic math-tool stream)
  at Qwen-1.5B on a mixed task requiring both retrieval and arithmetic reasoning. Tests whether
  N=3 source routing is stable and whether source interference is an empirical problem. Critical
  for the "open plug-in ecosystem" product positioning (Section 5.5).
Tier hint: local or remote GPU (Qwen-1.5B), ~4-8 hours training. Prerequisite: A1 PASS or MID.
Why-now: The 3-source test is the gate to the full "programmable attention" product pitch. Without
  empirical evidence at N=3 that sources do not degrade each other, the product claim is speculative.

Pre-reg bands:
  HARD-PASS: third source improves math-heavy questions; substrate accuracy does not regress > 2%
  MIDDLE-BAND: third source improves math but substrate regresses 2-5% (interference present,
    manageable)
  HARD-FAIL: third source causes regression on BOTH substrate and math (routing collapse)

### Anchor 5: par_multitenant_gate_config_v1 [PRIORITY 5]

Anchor pointer: Research note Section 5.3 (per-tenant isolation) and Section 5.4 (audit logging)
Substrate-product reading: Simulate 2 tenants with separate substrate shards and separate gate
  configurations at the same Pythia-160M instance. Verify numerically that gate_weight=0 produces
  exactly zero cross-tenant KV contribution. This is an algebraic correctness check, not an
  accuracy test. PASS = tenant isolation is provable, enabling the regulated-industry product claim.
Tier hint: local CPU, ~1-2 days engineering + short validation run.
Why-now: This is the compliance anchor. Regulated-industry customers (HIPAA, GDPR) will require
  proof of isolation before pilot. The test provides that proof (or surfaces an implementation bug
  before the proof attempt is customer-facing).

Pre-reg bands:
  HARD-PASS: gate_weight=0 produces numerically zero (< float32 epsilon) cross-tenant KV output
  HARD-FAIL: any measurable non-zero cross-tenant contribution under gate_weight=0

---

## Context pointers (file paths, not summaries)

- Research note (this drill):
    d:/AI/hd-instrument/notes/research_drill_programmable_attention_routing_5x_2026-06-09.md
- Production architecture memory:
    C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- Post-compaction brief (most recent empirical state):
    d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- North star memory (functional system vs LLMs):
    C:/Users/marsh/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md
- Multi-hop revival priority:
    C:/Users/marsh/.claude/projects/d--AI/memory/project_multihop_revive_priority.md

---

## Contract section

This handoff proposes 5 anchor candidates. Exp_dev selects from these based on current queue
state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5.

SEQUENCING CONSTRAINT: A1 (par_2source_gate_pythia160m_v1) MUST run before A2, A3, and A4.
  A1 gates all others. A2 and A3 can run in parallel after A1 completes. A4 requires A1 PASS
  or MID. A5 can run at any time (it is an integration test, not dependent on A1 accuracy result).

PRIORITY NOTE: A1 + A2 together answer the primary commercial question (does the gate work, and
can it be externally controlled?). If queue depth is limited, dispatch A1 first and A5 in parallel.
A5 does not require A1 outcome; it is an algebraic correctness check.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, and parameter ranges for each anchor
- Choosing local CPU vs remote GPU routing per feedback_route_gpu_vs_cpu_by_torch_not_N.md
- Selecting the specific retrieval task dataset (HotpotQA, NQ, TriviaQA, or equivalent)
- Writing experiment scripts following feedback_metrics_required_fields_write_metrics.md
- Designing the synthetic math-tool stream for A4 (e.g., encoded arithmetic result tokens)

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Deciding whether to shift the Tier 5c product claim to the routing architecture framing
  (requires explicit user authorization after A1+A2 verdict)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
- Committing to cloud dispatches for A4 without orchestrator approval per
  feedback_cloud_only_when_absolutely_necessary.md
