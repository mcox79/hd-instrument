# exp_dev hand-off — research: HRR context-bind Q2 coreference (mechanism-class 4)

**Filed-by:** research (Opus 4.7 1M ctx)
**Trigger:** `d:/AI/hd-instrument/notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md` (this drill)
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before dispatch.

Per `[[feedback-no-experiment-design-in-prompts]]`: exp_dev OWNS pre-reg fields, smoke gate, ship path. This hand-off provides anchor candidates, context pointers, and the why-now — not the cell file itself.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (TOP-RANKED) — `substrate_narrative_q2_recency_sequence_log_v1`

**Pointer:** new cell; reuses `c3_compressed_sequence_replay_v1` (HARD_PASS K=20 N=4096 chain-grade) as entity-mention recency log + HRR role-bind (gender/number/role tag) + `pc_cleanup_attractor_v1` (HARD_PASS d5/d10=1.000 chain-grade).

**Substrate-product reading:** mechanism-class 4 attempt for Q2 coreference; if HARD_PASS, M3 concern #3 (narrative tracking by hour 2) resolved by reusing existing chain-grade primitive in its native signal-shape.

**Tier hint:** Stage 3 (compositional understanding). Composition cell on existing chain-grade primitives — not a new mechanism cell. Smoke at ~5 min CPU; full at ~30 min CPU.

**Why-now:** today's V_C sweep (`substrate_narrative_partition_oracle_V_C_sweep_v1` HARD_FAIL) falsified partition-routing class for Q2 across V_C ∈ {50, 200, 1000, 4000}. Composition_v1 had silent pred_sha collision (META_RULE_AF trip). Mechanism-class 4 is the prescribed next step before capability-box closure protocol activates. 3 prior failures put Q2 close to closure threshold — if this also fails, dispatch drill 2 for closure-confirmation.

**Sketch (research-suggested arms; exp_dev tunes):**
- ARM_RANDOM_FLOOR (pins floor 0.20)
- ARM_NAIVE_MAGNITUDE (reproduces today's failing readout)
- ARM_RECENCY_ONLY (sequence-replay K-th most recent, no role filter)
- ARM_ROLE_FILTER_ONLY (gender/number filter, no recency)
- ARM_RECENCY_PLUS_ROLE (the mechanism)
- ARM_ORACLE (pins ceiling)

**Research-suggested HARD_PASS:** Q2 ≥ 0.60 + lift_over_naive ≥ 0.20 + arms_differ ≥ 3 distinct pred_sha + cv ≤ 0.10.
**Research-suggested HARD_FAIL:** Q2 ≤ 0.30 OR lift_over_naive ≤ 0.05 OR pred_sha collision between RECENCY+ROLE and NAIVE.

**Pre-reg additions (mandatory per recent META_RULE drift):**
- `EXPECTED_N_UNITS = 6` (smoke) / `EXPECTED_N_UNITS = 18` (full 3-seed)
- `CARDINALITY_OK` checked
- per-arm declare: which chain-grade primitive's exact API call invoked (line# + method name) — prevents silent META_RULE_AF
- `Q_per_type = 8` (mandatory ≥ 8; composition_v1 used 3 and hit N=3 noise)

**Known failure modes (parked for cell-author to address):**
1. Narrative corpus generator does NOT yet have gender/number/role tag per entity-mention. Cell-author must ADD this (~50 LOC in the existing `stage3_narrative_coherence_100event_5char_full_stack_v1` corpus generator).
2. Sequence-binding K=20 means narratives > 20 entity-mentions per character will saturate (4-char × 100-event with ~80 mentions/char will EXCEED K=20). Mitigation: log most-recent-K-distinct-mentions (sliding window per entity), not all mentions.
3. If role-tag generator broken, RECENCY+ROLE will collapse to RECENCY_ONLY — discriminator stays valid (ARM_RECENCY_ONLY is its own arm), so this is observable not silent.

---

### Anchor 2 (FALLBACK if Anchor 1 HARD_FAILs) — `substrate_q2_kroneker_linearithmic_cleanup_v1`

**Pointer:** new cell; arxiv:2506.15793 Kroneker-rotation linearithmic cleanup as v2 cleanup upgrade over PC attractor. Pairs with Anchor 1 readout pipeline but swaps cleanup stage.

**Substrate-product reading:** mechanism-class 5 — only dispatch if Anchor 1 HARD_FAILs and capability-box closure protocol activates (need drill 2 confirmation per `feedback_2x_drill_negatives_before_capability_closure`).

**Tier hint:** Stage 3. Higher complexity (~150 LOC for Kroneker block ops + signal-shape audit needed).

**Why-now:** parked for now. Dispatch only on HARD_FAIL of Anchor 1.

---

### Anchor 3 (FALLBACK if both 1+2 HARD_FAIL) — `substrate_q2_attention_as_binding_v1`

**Pointer:** new cell; arxiv:2512.14709 "Attention as Binding" — softmax-attention reframed as VSA binding. Substrate has refuse-gate nonlinear-readout HARD_PASS (alpha=1.0 3-seed chain-grade); attention-as-binding extends this to scored argmax.

**Substrate-product reading:** mechanism-class 6 — last-resort before Q2 capability-box closure.

**Tier hint:** Stage 3 / Stage 4 boundary. Highest novelty cap (~0.40 pure-novel).

---

## Context pointers (file paths, not summaries)

- This drill: `d:/AI/hd-instrument/notes/research_drill_hrr_context_bind_disambiguator_Q2_coreference_2026-06-28.md`
- Prior drill (composition prescription): `d:/AI/hd-instrument/notes/research_drill_long_narrative_coref_temporal_2026-06-28.md`
- V_C sweep HARD_FAIL: `d:/AI/hd-instrument/data/exp_substrate_narrative_partition_oracle_V_C_sweep_v1_smoke/metrics.json`
- Composition_v1 MIDDLE_BAND with pred_sha collision: `d:/AI/hd-instrument/data/exp_substrate_narrative_coref_temporal_composition_v1_smoke/metrics.json` (compare ARM_PARTITION_ORACLE_ONLY.pred_sha vs ARM_NAIVE_MAGNITUDE.pred_sha)
- Chain-grade primitive evidence: `d:/AI/hd-instrument/data/exp_c3_compressed_sequence_replay_v1/metrics.json` (Q3 sequence-binding) + `d:/AI/hd-instrument/data/exp_pc_cleanup_attractor_v1/metrics.json` (PC cleanup) + `d:/AI/hd-instrument/data/exp_contextual_encoding_hrr_binding_smoke_v1_smoketest/metrics.json` (HRR sentence bind)
- Original narrative corpus generator (needs role-tag extension): cells/`exp_stage3_narrative_coherence_100event_5char_full_stack_v1.py`
- Substrate capability registry: `python d:/AI/hd-instrument/tools/substrate_capability_registry.py --family sequence_binding --limit 10`

---

## Contract

- exp_dev owns: pre-reg fields, smoke gate, dispatch path, post-ship REMOTE VERIFY (or local CPU verify for small cells), self-test per formula-selftests.
- research owns: mechanism class + signal-shape audit + HARD_PASS/FAIL bands + cross-cell evidence pattern. Already filed above.
- cell-author owns: arm wiring + cardinality_ok + arms_differ verification + role-tag corpus generator addition.

## Autonomy declaration

exp_dev is authorized to:
- Modify the HARD_PASS/FAIL band thresholds within ±0.05 of research recommendation if smoke evidence suggests calibration drift.
- Refactor arm names for clarity.
- Add additional ablation arms beyond the 6 listed.
- Decline this anchor and pick Anchor 2/3 directly IF cell-author smoke shows Anchor 1's role-tag generator extension is > 3 hours work (escalate as DEFER notice if so).
- NOT authorized to: skip the arms_differ pred_sha verification (mandatory per META_RULE_AF discipline today).

-- research (Opus 4.7 1M ctx) 2026-06-28
