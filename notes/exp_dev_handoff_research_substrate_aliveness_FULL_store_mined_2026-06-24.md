# exp_dev hand-off — research: substrate aliveness FULL Store-mined drill

**Filed-by:** research (Opus 4.7 1M) 2026-06-24
**Trigger:** USER pushback + FULL Store scour at `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

Per [[feedback-no-experiment-design-in-prompts]] — anchor pointers + tier hints only; exp_dev owns the cell-author decision.

---

## Anchor candidates (rank-ordered by leverage)

### A1 — Joint compose cell (5 chain-grade primitives stacked)
- **Anchor:** `compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1`
- **Substrate-product reading:** attacks the 1.5-bit unclaimed gap from current chain-grade rail (fair_harness BPC 7.30) to bigram-floor (~5.5 BPC). If super-additive compose holds, substrate-as-LM clears bigram regime.
- **Tier hint:** **chain-grade-eligible** (combines 5 chain-grade primitives; if BPC ≤ 6.85 and cv ≤ 0.05 and substrate-only=True, qualifies).
- **Why now:** USER asked "have we done the RIGHT tests"; this is the joint-compose cell that's been queued lane-implicit but never shipped. Highest discriminating value: tells us if compose is super-additive (substrate clears bigram floor) or sub-additive (compose-saturation mechanism characterized).
- **HARD-PASS:** joint BPC ≤ 6.85, cv ≤ 0.05, all arms substrate-only.
- **HARD-FAIL:** joint BPC ≥ 7.15 (sub-additive; collapses to single-knob best).
- **P_deflated:** 0.40.

### A2 — Multi-iter cleanup on continuous-codebook E (regime-confound fix)
- **Anchor:** `multi_iter_cleanup_continuous_codebook_LM_v1`
- **Substrate-product reading:** modern-Hopfield cleanup is chain-grade at N=4096 M/N=0.30 = 100% (row 100); multi-iter LM HARD_FAIL was on sign-binarized char-trigram E (primitive-vs-encoder confound). Re-run multi-iter LM with continuous-codebook E (untrampled by sign-binarize) tests whether the primitive truly doesn't transfer to LM regime.
- **Tier hint:** **MEASURED_MECHANISM-eligible** (regime-confound fix; if lift ≥ 0.05 over single-step, demonstrates primitive transfer).
- **Why now:** Recent-arc wrongly closed multi-iter cleanup. USER's "scour Store" finding is the chain-grade modern-Hopfield row 100 — the primitive WORKS. Fixing the encoder confound is cheap and high-information.
- **HARD-PASS:** ARM_MULTI_ITER_CONTINUOUS bpc ≤ ARM_SINGLE_STEP - 0.05.
- **HARD-FAIL:** ARM_MULTI_ITER_CONTINUOUS bpc ≥ ARM_SINGLE_STEP + 0.02.
- **P_deflated:** 0.50.

### A3 — Theta-gamma routing primitive cell (brain-grounded new lane)
- **Anchor:** `theta_gamma_routing_substrate_native_v1`
- **Substrate-product reading:** Brain-grounded mechanism with no chain-grade or MM cell in Store. Per [[feedback-brain-is-existence-proof-higher-prior-for-brain-grounded-mechanisms]] prior 0.65. Closest existing atoms: PC residual gate (MID) and excitability-trace alloc-routing (smoke only).
- **Tier hint:** **MEASURED_MECHANISM-eligible** at smoke; chain-grade-eligible at FULL if brain-prior holds.
- **Why now:** USER explicitly called out "we need to NAIL lower-nervous-system + mid-level processing as baseline." Theta-gamma is mid-level processing primitive. Genuine new lane.
- **HARD-PASS:** theta-modulated routing routing-acc lift ≥ 0.10 over random-gate baseline.
- **HARD-FAIL:** lift ≤ 0.02.
- **P_deflated:** 0.45.

### A4 — K=4, K=8 multi-bank LM extension
- **Anchor:** `K4_K8_multi_bank_LM_fair_harness_v1`
- **Substrate-product reading:** K=2 LM was MIDDLE_BAND (lift=0.101 < +0.10 margin). K=32 modular macrocolumn is chain-grade for COST-path but not LM. Extending K to 4 and 8 tests K-scaling saturation.
- **Tier hint:** MEASURED_MECHANISM-eligible (K-sweep characterization).
- **Why now:** USER's "are we looking at the right thing" K=2 question. K=4 / K=8 are unmeasured.
- **HARD-PASS:** K=4 or K=8 lift ≥ 0.15.
- **HARD-FAIL:** all K-sweep lifts ≤ 0.05.
- **P_deflated:** 0.35.

### A5 — Path A × Path C joint encoder cell
- **Anchor:** `path_A_path_C_joint_encoder_fair_harness_v1`
- **Substrate-product reading:** Per [[project-path-c-substrate-owned-encoder]] USER directive: Path C IS the substrate-product answer. Path A (word2vec) + Path C (substrate-PC-encoder) joint cell at fair_harness scale tests if combination beats either alone.
- **Tier hint:** MEASURED_MECHANISM-eligible.
- **Why now:** Path C currently MIDDLE_BAND (beats unigram on 1 metric); Path A is diagnostic probe per USER feedback.
- **HARD-PASS:** joint encoder BPC ≤ 7.20.
- **HARD-FAIL:** joint BPC ≥ 7.32.
- **P_deflated:** 0.35.

---

## Context pointers (file paths)

- `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` — full research note (master pointer)
- `notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md` — encoder/baseline methodology
- `notes/phase_portrait_v1_inventory_atom_substrate_operating_regime_map_2026-06-22.md` — phase-portrait inventory
- `data/substrate_index/meta/cert_ledger.jsonl` — 707-row cert ledger
- `data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json` — 240x mult-compose chain-grade
- `data/exp_modern_hopfield_n_sweep_v1/metrics.json` — modern-Hopfield chain-grade
- `data/exp_lock_in_amplifier_hd_frequency_v1_FULL/metrics.json` — lock-in amplifier chain-grade
- `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json` — het-plasticity HP
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` — fair_harness chain-grade rail
- `data/exp_substrate_K2_x_cfrpe_compose_LM_v1/metrics.json` — K=2 LM MIDDLE_BAND
- `data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2_smoke/metrics.json` — K=2 word2vec smoke CGB
- `data/exp_m1_modular_macrocolumn_W_v2/metrics.json` — K=32 modular chain-grade
- `data/exp_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu/metrics.json` — K*=12 HP

---

## Contract

- Pause-gated for dispatch. Honor `data/orchestrator_paused.flag`.
- Pre-reg per envelope-fail-bands; smoke gate before FULL.
- Smoke on local_cpu OR remote_cpu (per Fix #22 cell-author smoke routing).
- FULL on overnight_queue for heavy compose (5 arms × 3 seeds at N=8192 V=4000).
- Per Fix #28: read per-arm metrics, NOT summary verdict text, before cross-arm framing.
- Per Fix #26: pre-dispatch verify-the-referent check via `tools/predispatch_check.py` to catch duplicates.
- Per Fix #20: file-redirect + mtime polling, NOT pipe-tail subprocess monitoring.
- Per Fix #24: GPU dispatch must use GPU (torch.cuda + batched ops); confirm gpu_util ≥ 50% in smoke.

---

## Autonomy declaration

exp_dev decides:
- Which anchor to take first (A1-A5 ranked by leverage; A1 is highest)
- Cell-author scope (single anchor or multi-anchor cell)
- Smoke vs FULL sequencing
- Queue routing (local_cpu / remote_cpu / overnight_queue)
- Pre-reg fail-bands (suggested above; exp_dev can tighten/loosen)

Research is hands-off on cell-design per [[feedback-no-experiment-design-in-prompts]].

— Research (Opus); hand-off filed for exp_dev emergency-refill discovery; commit pending.
