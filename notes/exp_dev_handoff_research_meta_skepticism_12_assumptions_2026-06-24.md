# exp_dev hand-off — research: META-SKEPTICISM 12 assumptions drill (2x Store-mined)

**Filed-by:** research (Opus 4.7 1M)
**Date:** 2026-06-24
**Trigger:** USER directive — META-skepticism drill on 12 assumptions; Store-mined full breadth; 4 un-tested or under-tested assumptions surfaced.
**Source research note:** d:/AI/hd-instrument/notes/research_meta_skepticism_12_assumptions_store_mined_2x_drill_2026-06-24.md
**Pause state:** check `data/orchestrator_paused.flag`; routing-handler will gate.

Per [[feedback-no-experiment-design-in-prompts]] — this file is structural hand-off; exp_dev owns mechanism choices, smoke gates, ship sequence.

---

## Anchor candidates (rank-ordered for next 4-5 cycles)

### Anchor 1 — pc_hierarchy_fair_harness_v1
- **Substrate-product reading:** Resolves SUSPENDED METHCONF verdict on PC hierarchy (substrate_pc_hierarchy_text8_lm_v1+v2 HARD_FAIL under wrong-metric trap). Tests A12 contradiction (hierarchy helps 5-corpus aggregation chain-grade BUT degrades capacity 0.25x in feasibility cell).
- **Why now:** Cheapest test (~3-4h GPU); reuses chain-grade fair_harness rail; resolves contradiction blocking A12 decision.
- **Tier hint:** chain-grade-eligible (rank-1 baseline is HARD_PASS; PC arms need lift ≥ 0.05 BPC under selection-mixer per META_HARNESS_RIGGED atom).
- **Key pre-reg:** HP PC arms beat RANK_1 by ≥ +0.05 top-1 OR ≥ +0.05 BPC under selection-mixer. HF PC arms ≤ RANK_1 on ALL metrics under revised harness.

### Anchor 2 — substrate_word_level_lm_v1_FULL
- **Substrate-product reading:** Raises smoke MIDDLE_BAND (`exp_substrate_brain_word_level_prediction_v1_smoke` BPW=6.174 vs word-bigram 6.449) to production scale. Tests A10 grain-mismatch hypothesis (substrate at theta-rate 5Hz word-level vs char-rate 30Hz). This is the **highest-leverage** test — closes A1 product reframe + A10 corpus + answers "what's the actual gap-to-brain."
- **Why now:** Second-cheapest test (~4-6h GPU); smoke already direction-correct (substrate K=5 BPW < word-bigram BPW); production scale will discriminate.
- **Tier hint:** chain-grade-eligible if HP clears; MEASURED_MECHANISM if MIDDLE_BAND.
- **Key pre-reg:** HP word-level substrate K=5 BPW ≤ word-bigram BPW − 0.30 bits AND top1 ≥ word-bigram top1 + 0.05. HF substrate BPW ≥ word-bigram BPW.

### Anchor 3 — cfrpe_per_token_adaptive_lr_v1
- **Substrate-product reading:** Tests A6 un-tested per-token cf-RPE schedule vs coarse-step (5000) cf-RPE. Single-arm cf-RPE @5000 = +0.30 lift (chain-grade border); per-token schedule may push to chain-grade lift.
- **Why now:** ~2-3h GPU; substrate-product extension of in-flight cf-RPE work.
- **Tier hint:** chain-grade-eligible if lift ≥ 0.40.
- **Key pre-reg:** HP lift ≥ 0.40 over Hebbian baseline at N_DIM=8192 fair_harness rail; CV ≤ 0.10. HF lift ≤ 0.20.

### Anchor 4 — dynamic_f_phase_shift_sparsity_v1
- **Substrate-product reading:** Tests UN-TESTED A11 (sparsity as phase-shiftable parameter). Brain phase-shifts cortical sparsity via ACh/NE; substrate could too.
- **Why now:** ~3-4h GPU; substrate-novel feature, brain-existence-proof support.
- **Tier hint:** chain-grade-eligible if any dynamic arm clears HP.
- **Key pre-reg:** HP any dynamic arm gives ≥ +0.10 bits BPC lift over best static arm AND CV ≤ 0.05. HF all dynamic arms ≤ best static arm.

### Anchor 5 (parallel meta-work) — fair_harness_f_002_default_v1
- **Substrate-product reading:** Replicator to corroborate A5 finding that f=0.02 (not f=0.05) is production optimum. Set baseline to switch substrate default once replicated.
- **Why now:** ~3h GPU; verify-the-referent on default-switch.
- **Tier hint:** infra-replicator, not chain-grade-claim.
- **Key pre-reg:** HP f=0.02 BPC ≤ f=0.05 BPC by ≥ 0.05 across 3 seeds. HF f=0.02 BPC ≥ f=0.05 BPC.

---

## Context pointers (file paths, not summaries)

- **Source research note:** d:/AI/hd-instrument/notes/research_meta_skepticism_12_assumptions_store_mined_2x_drill_2026-06-24.md
- **METHCONF reclassification atom:** d:/AI/hd-instrument/notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md
- **Methodology audit drill:** d:/AI/hd-instrument/notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md
- **Brain mechanisms NOT-yet-tested drill:** d:/AI/hd-instrument/notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md
- **Substrate aliveness map:** d:/AI/hd-instrument/notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md
- **Surprise baseline 7.22 vs 7.30 drill:** d:/AI/hd-instrument/notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
- **PC hierarchy METHCONF cell:** d:/AI/hd-instrument/data/exp_substrate_pc_hierarchy_text8_lm_v1/metrics.json (smoke; bpc 8.10 vs rank1 7.80 — verdict SUSPENDED)
- **Working memory chain-grade-eligible:** d:/AI/hd-instrument/data/exp_working_memory_hrr_slots_PRODUCTION_v1/metrics.json (K=32 at sigma=1.0 recall=1.000)
- **Drosophila MB sparsity sweep:** d:/AI/hd-instrument/data/exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu/metrics.json (f=0.02 best at N=2048)
- **Sparsity fine battery:** d:/AI/hd-instrument/data/exp_substrate_sparsity_fine_battery_gpu_v1/metrics.json (f=0.02/0.05 → 25x dense capacity at N=16384)
- **fair_harness chain-grade rail:** d:/AI/hd-instrument/data/exp_fair_harness_substrate_as_lm_v1/metrics.json (HARD_PASS bpc 7.3065 SPARSE_BIPOLAR)
- **Word-level smoke:** d:/AI/hd-instrument/data/exp_substrate_brain_word_level_prediction_v1_smoke/metrics.json (MIDDLE_BAND; direction-correct K=5)
- **n1_v3 top-1 chain-grade:** d:/AI/hd-instrument/data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json (top1=0.445 vs unigram 0.276)
- **GHRR vs FHRR comparison:** d:/AI/hd-instrument/data/exp_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1/metrics.json (MIDDLE_BAND; GHRR wins directionality)

---

## Contract section

Per [[feedback-no-experiment-design-in-prompts]]:
- Pre-reg per envelope-fail-bands (see anchor pre-regs above; tighten as needed during smoke).
- Smoke gate mandatory (Fix #17 strict measurement).
- Ship via queue_add.sh per usual dispatch rules.
- Post-ship REMOTE VERIFY per landing notifier.
- Self-test per formula-selftests.
- Pause-gated by data/orchestrator_paused.flag.
- Routing rule (Fix #24 GPU dispatch must actually use GPU; route via hdi_orchestrator for N_DIM≥8192 / multi-seed encoder ingest / matmul-bound).
- Default-switch (Anchor 5) requires explicit cross-check with Skunkworks before substrate-default change ships.

---

## Autonomy declaration

exp_dev decides:
- Which anchor to ship FIRST in the sequence (default: Anchor 1 PC hierarchy fair_harness, then Anchor 2 word-level).
- Smoke vs FULL routing per queue capacity.
- Whether to bundle parallel-cell ships (Anchor 3 + Anchor 4 can run in parallel on separate GPU slots).
- Cell-author smoke + Fix #17 measurement on remote_cpu for heavy cells.
- Exact arm names, exact pre-reg numeric tightening within stated bands.
- Whether to atomize Anchor 5 as `infra-replicator` vs `META_DEFAULT_SWITCH_REPLICATOR`.

Research-lane disengaged from sequencing decisions per Phase 3 Agent Teams role-separation.
