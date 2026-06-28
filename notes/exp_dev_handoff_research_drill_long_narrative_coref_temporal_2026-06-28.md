# exp_dev hand-off — research: long-narrative coherence Q2 (coreference) + Q3 (temporal) substrate composition

**Filed by:** research (Opus 4.7 1M ctx) 2026-06-28
**Trigger:** `notes/research_drill_long_narrative_coref_temporal_2026-06-28.md` (full drill rationale + functional-requirement table + brain analog + per-primitive registry coverage)
**Pause state:** check `data/orchestrator_paused.flag` — if present, this hand-off is filed for queue when resume.

Per `[[feedback-no-experiment-design-in-prompts]]`: this file specifies WHAT to test and WHICH chain-grade primitives to wire, NOT the full implementation. exp_dev owns the actual cell.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (TOP, P_deflated=0.55): `exp_substrate_narrative_coref_temporal_composition_v1`

**Substrate-product reading:** today's `stage3_narrative_coherence_100event_5char_full_stack_v1` FULL HARD_FAILed on Q2 (coref) and Q3 (temporal) — both at random-chance floor. Diagnostic shows ARM_FULL_STACK and ARM_NO_SEGMENT produced IDENTICAL per-arm per-seed numbers for Q2/Q3 → the cell wired naive readout paths (`np.argmax magnitude` for Q2; `np.roll(-1)` cosine for Q3) that BYPASS the chain-grade primitives we already have on disk (partition oracle 5-way routing 0.97; c3_compressed_sequence_replay K=20 lossless 1.000). This cell wires the correct readouts and validates the composition.

**Tier hint:** chain-grade-eligible composition test (META_RULE_AM passes — substrate already covers all 6 functional requirements: 3 for Q2, 3 for Q3).

**Why now:** unblocks M3 concern #3 fix path; failing cell already cost ~22s wall + author time today; the fix is fast and the risk is well-bounded.

**Architecture per CHUNKED single-seed-per-cell** (USER 2026-06-28): 3 seeds × 5 arms × 12 Qs = 180 Q-units total; spawn as 15 single-(seed,arm) chunks.

**5 arms (mandatory, arms-must-differ on Q2 + Q3 per META_RULE_AF):**
- ARM_RANDOM_FLOOR (uniform random over candidates; locks floor by construction)
- ARM_NAIVE_MAGNITUDE (today's failing readout — reproduce today's Q2=0.22 Q3=0.11; smoke-at-full-N preview baseline)
- ARM_PARTITION_ORACLE_ONLY (Q2 wired to anchor-projection + biased-Q routing path from `substrate_multihop_partition_oracle_v5_hardened_v1`; Q3 unchanged from naive)
- ARM_SEQUENCE_REPLAY_ONLY (Q3 wired to `c3_compressed_sequence_replay` K=20 decoder path; Q2 unchanged from naive)
- ARM_COMPOSITION (both fixed in same forward pass)

**Discriminator-must-survive-scale gate:** ARM_PARTITION_ORACLE_ONLY must beat ARM_NAIVE_MAGNITUDE by >= 0.30 on Q2 at smoke (e.g. 20 events / 3 chars) AND at full-N (100 events / 5 chars). Same for ARM_SEQUENCE_REPLAY_ONLY on Q3.

**HARD_PASS (all 3 required):**
- ARM_PARTITION_ORACLE_ONLY Q2 >= 0.60 (3x random floor 0.20)
- ARM_SEQUENCE_REPLAY_ONLY Q3 >= 0.60
- ARM_COMPOSITION min_per_q >= 0.50

**HARD_FAIL (any one kills):**
- ARM_PARTITION_ORACLE_ONLY Q2 <= 0.30 (composition broken even with correct readout)
- ARM_SEQUENCE_REPLAY_ONLY Q3 <= 0.20 (sequence-replay decoder doesn't survive narrative regime)
- ARM_COMPOSITION any Q < 0.30 (single point of failure persists)

**Pre-reg functional-requirement table mandatory** (per `META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md` and USER 2026-06-28 directive): each Q must cite the primitive's chain-grade anchor AND specify which readout path is wired.

**Expected wall:** smoke ~5 min, full ~30 min local CPU. Single-seed chunking → 15 spawn units.

---

### ANCHOR 2 (FALLBACK, P=0.30): `exp_substrate_narrative_partition_oracle_capacity_V_C_sweep_v1`

**Only spawn if ANCHOR 1 ARM_PARTITION_ORACLE_ONLY collapses (Q2 < 0.30 with correct readout).** Tests whether partition oracle's V_C-scale was the binding constraint — current narrative cell has V_C ≈ 50 (N_JOBS + N_OBJ); oracle was validated at V_C=4000. Sweep V_C in {50, 200, 1000, 4000} on the 100-event narrative; expected curve = monotone Q2 lift with V_C.

---

### ANCHOR 3 (FALLBACK, P=0.30): `exp_substrate_narrative_sequence_replay_K_scene_alignment_v1`

**Only spawn if ANCHOR 1 ARM_SEQUENCE_REPLAY_ONLY collapses (Q3 < 0.20 with correct readout).** Tests whether K_SCENE_BOUNDARY (currently 10) misaligns with replay-K=20. Sweep K_SCENE in {5, 10, 20}; expected Q3 peaks where K_SCENE == replay-K.

---

## Context pointers (file paths, not summaries)

- **Driving research drill:** `d:/AI/hd-instrument/notes/research_drill_long_narrative_coref_temporal_2026-06-28.md`
- **Failing cell source (the one to fix):** `d:/AI/hd-instrument/experiments/exp_stage3_narrative_coherence_100event_5char_full_stack_v1.py` lines 621-686 (`_answer_coreference` + `_answer_temporal`)
- **Failing cell metrics:** `d:/AI/hd-instrument/data/exp_stage3_narrative_coherence_100event_5char_full_stack_v1/metrics.json`
- **Prior drill that designed the failing cell:** `d:/AI/hd-instrument/notes/research_drill_2x_long_context_narrative_coherence_stage3_2026-06-27.md`
- **Prior exp_dev handoff:** `d:/AI/hd-instrument/notes/exp_dev_handoff_research_long_context_narrative_coherence_stage3_2026-06-27.md`

**Chain-grade primitives to wire (registry MEASURED@):**
- Partition oracle Q2 readout: `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_v1_smoke/metrics.json` (anchor projection + biased-Q routing path)
- Sequence-replay Q3 readout: `d:/AI/hd-instrument/data/exp_c3_compressed_sequence_replay_v1/metrics.json` (compressed-replay K=20 decoder; HARD_PASS B_d5=1.000 order_delta=0.983)
- PC cleanup fallback (if magnitude voting still needed): `d:/AI/hd-instrument/data/exp_pc_cleanup_attractor_v1/metrics.json` (HARD_PASS d5/d10=1.000)
- Permutation binding (multi-occurrence): `d:/AI/hd-instrument/data/exp_substrate_permutation_binding_multiocc_v2_full/metrics.json` (HARD_PASS_CHAIN_GRADE perm=1.000)

**Test-design discipline references:**
- `d:/AI/hd-instrument/notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md` (META_RULE_AA fairness-before-tier; baselines must not implicitly do the mechanism)
- META_RULE_AF arms-must-differ (today's cell had identical FULL_STACK == NO_SEGMENT for Q2/Q3 — that's the structural symptom this cell must guard against)
- DISCRIMINATOR-MUST-SURVIVE-SCALE per `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`

---

## Contract section

- exp_dev DECIDES: cell file name, N_h/N_c/N_part dims (suggest reuse 512/1024/1024 from today), exact arm-fork wiring, smoke vs full schedule, queue routing (local CPU likely fine; smoke first then full).
- research DECIDES: which primitives are functional-requirement-MEASURED@ on disk (above); HARD_PASS/HARD_FAIL thresholds (above); composition-test vs new-mechanism classification (this IS composition-test).
- exp_dev DOES NOT need to re-design the narrative generator — reuse the function from `exp_stage3_narrative_coherence_100event_5char_full_stack_v1.py` so per-seed comparison is direct.

## Autonomy declaration

exp_dev: author the cell per ANCHOR 1 above; do not wait for further research input. If ARM_PARTITION_ORACLE_ONLY or ARM_SEQUENCE_REPLAY_ONLY collapses, spawn ANCHOR 2 / ANCHOR 3 autonomously (the drill already covers their rationale).

Pause-state respected (per `data/orchestrator_paused.flag`).

-- research (Opus 4.7 1M ctx) 2026-06-28
