# exp_dev hand-off — research: OPTIMAL Stage-1 substrate encoding design space (2x drill)

**Filed-by:** Research (Opus 4.7 1M context)
**Date:** 2026-06-24
**Trigger:** USER strategic directive — "we choose the optimal encoding — that we start on the right track" (Stage-1 foundational). Research full 2x drill landed at `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`.
**Pause state:** Check `data/orchestrator_paused.flag` before dispatch. If paused, queue for resume.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR POINTERS only. exp_dev owns cell design, schema-vet, smoke gate, and dispatch. Research provides the strategic frame + HARD bands + pre-reg.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 (PRIMARY — ship first): `enc_e2_softhebb_3layer_substrate_owned_v1`

**Pointer:** Section "E2" of `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`
**Tier hint:** Tier-A (chain-grade-eligible if HP; substrate-OWNED encoder per USER 2026-06-23 Path C directive)
**Substrate-product reading:** Stage-1 commit-candidate; closes hierarchical-encoder-depth gap (pc_hierarchy_v2 METHCONF); brain-grounded (V1->V2->V4 hierarchical sparse coding); 1-week shippable
**Why now:** USER explicitly framed Stage-1 as foundational; if E2 HARD-PASSES, Stage-1 committable in 1 week and Stages 2-4 unblocked. If E2 HARD-FAILS, federation (E1) becomes justified investment.
**Cost estimate:** ~1 week build + 2-4 hr cell on local_cpu_queue (laptop-CPU-feasible at N=8192)
**Predecessor:** parent dual-gain drill 2026-06-23 already has SoftHebb design (see `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md`)

**Pre-reg HARD bands (per arm vs fair_harness BPC=7.3065):**
- HARD_PASS: BPC <= 7.10 AND CV <= 0.03 AND top-1 acc >= 0.30
- HARD_FAIL: BPC >= 7.30 (no measurable lift over current default)
- MIDDLE_BAND: 7.10 < BPC < 7.30

### Anchor 2 (FULL DISCRIMINATOR — ship if budget allows): `enc_stage1_optimal_3arm_discriminator_v1`

**Pointer:** Section "Cheap Decisive Test" of `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`
**Tier hint:** Tier-A (3 arms + baseline; settles Stage-1 in ONE cell)
**Substrate-product reading:** Tests E1 / E2 / E3 vs baseline word2vec in single ship; per-arm verdicts determine Stage-1 commit
**Why now:** Full discriminator removes ambiguity; expensive but settles all 3 candidates simultaneously
**Cost estimate:** ~4-6 hr remote_gpu (text8 V=4000 N_DIM=8192 100k tokens 3 seeds)
**Pre-flight:** sigma=0 sanity recall=1.000 all arms; HDLAB_EXP_NAME set; commit-first; REQUIRED_FIELDS schema-vet

**4-arm design (encoder x algebra x sparsity):**
- ARM_BASELINE_W2V_F05: word2vec sparse-bipolar HRR f=0.05 (current default)
- ARM_E2_SOFTHEBB_F02: char-trigram + SoftHebb 3-layer HRR f=0.02 (substrate-OWNED)
- ARM_E1_HUB_3SPOKE: S1+S2+S4 hub-and-spoke federation HRR+FPE f=0.02
- ARM_E3_KWTAVQ_HADAMARD: k-WTA-VQ + Hadamard geometry + cf-RPE adaptive HRR f=0.02

### Anchor 3 (PREREQUISITE for E1 federation): `enc_atom_graph_neighborhood_v1`

**Pointer:** Section "L4 Implementation" of `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
**Tier hint:** Tier-A (S2 spoke isolation; required if E1 federation pursued)
**Substrate-product reading:** Atom-encoder for self-mapping + S2 spoke for E1; closes self-mapping gap
**Why now:** S2 prerequisite for E1 federation; ship in parallel with E2 cheap discriminator
**Cost estimate:** ~3-4 days build + ~2-4 hr full cell on local_cpu_queue

### Anchor 4 (S4 spoke isolation): `enc_relation_rotate_v1`

**Pointer:** Section "L2 winners TIER-B" of `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
**Tier hint:** Tier-B (dispatch if E2 HARD-PASS to justify federation investment)
**Substrate-product reading:** S4 relation spoke for E1 federation; RotatE-style phase encoding via existing FPE primitive
**Cost estimate:** ~3-5 days

### Anchor 5 (full federation — ship only if S1+S2+S4 spokes pass): `enc_hub_4spoke_v1`

**Pointer:** Section "Depth-B" of `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md`
**Tier hint:** Tier-C (dispatch ONLY if Anchors 1-4 collectively justify; high cost, high risk)
**Substrate-product reading:** Full hub-and-spoke federation; Stage-1.5 upgrade if E2 alone insufficient
**Cost estimate:** ~2 weeks impl + ~1 week eval

---

## CONTEXT POINTERS (file paths, not summaries)

**Strategic frame:**
- `notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md` (THIS DRILL — strategic frame + HARD bands + cross-thread synthesis)
- `notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md` (6 chain-grade primitives; Joint compose cell as parallel highest-leverage)
- `notes/director_bit_density_store_mine_inventory_2026-06-24.md` (f=0.02 chain-grade optimal; 1-bit bipolar ship-ready)

**Parent drills:**
- `notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md` (SoftHebb + FPE candidates; E2 ancestor)
- `notes/research_5x_deeper_path_c_universal_encoder_architecture_2026-06-23.md` (S1+S2+S4 hub-spoke federation; E1 ancestor)
- `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md` (RI + BEAGLE distributional semantics)
- `notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md` (zero-product cascade diagnosis + Rachkovskij CDT fix)

**Substrate primitives:**
- `hdlab/char_trigram_encoder.py` (existing baseline; ARM_BASELINE)
- `hdlab/kg_traversal.py` (KGStore; S2 graph primitive)
- `hdlab/binding.py` (FHRR/HRR bind; reused for S2 + S4 spokes)
- `hdlab/bundling.py` (majority-rule; reused for hub composition)
- `hdlab/whitening.py` (existing; composes for E1 hub alignment)

**Cert evidence:**
- `data/substrate_index/meta/cert_ledger.jsonl` (707 rows; chain-grade rail at BPC=7.3065)
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` (baseline rail)
- `data/exp_substrate_sparsity_fine_battery_gpu_v1/metrics.json` (f=0.02 chain-grade)
- `data/exp_pp55_vsa_binding_n131072_v6_n131072/metrics.json` (HRR N=131072 envelope)
- `data/exp_bipolar_quantization_quality_cpu_v1/metrics.json` (1-bit bipolar ship-ready)

---

## CONTRACT SECTION

**Research provides:**
- Strategic frame: optimal Stage-1 encoding decision (E1 / E2 / E3 candidates)
- Pre-registered HARD bands per arm (HARD_PASS / HARD_FAIL / MIDDLE_BAND)
- Brain-existence-proof grounding (Patterson-Rogers ATL; Olshausen-Field V1; drosophila MB)
- Calibration penalty applied (0.20 deflation; novel-synthesis cap 0.50)
- Cross-thread synthesis with parent drills + bit-density + aliveness map

**exp_dev owns:**
- Cell wiring (4-arm sweep for full discriminator OR single-arm E2 for cheap test)
- Schema-vet via `tools/exp_dev/formula_selftests.py`
- Smoke gate (sigma=0 sanity recall=1.000 all arms)
- Pre-flight checklist (--self-test on .venv; HDLAB_EXP_NAME; REQUIRED_FIELDS; run_mode='full'; commit-first)
- Dispatch via queue_add.sh (route per Fix #24 GPU dispatch rules)
- Post-ship REMOTE VERIFY (mtime check + per-arm metrics.json read)
- Self-test per formula-selftests
- Atomize result + cap_map bump per verdict (route via verdict_handler)

**Skunkworks owns:**
- Cert ruling per Skunkworks methodology
- By-construction-saturation tiering (Fix #28 — verify per-arm metrics not summary verdict text)
- Override Director framings as needed

**Director / orchestrator owns:**
- Routing decisions (ship Anchor 1 first; pivot based on verdict)
- cap_map bump per verdict
- Cross-session coordination

---

## AUTONOMY DECLARATION

exp_dev has FULL autonomy over:
- Cell design details (arm internals, codebook generation, training schedule)
- Smoke vs full-mode budget allocation
- Dispatch ordering (Anchor 1 alone first vs Anchor 2 full discriminator)
- Routing to local_cpu_queue vs remote_gpu vs overnight_queue per Fix #24
- Schema-vet failures: HALT and re-coordinate; do NOT push uncommitted notes to remote per [[feedback-commit-prereg-notes-before-remote-dispatch]]

Research will NOT override exp_dev's cell-design choices. Research provides anchor pointers + HARD bands; exp_dev owns mechanical work.

Per [[feedback-no-inter-session-routing-notes-deprecate-ferry-mechanism]]: this is a hand-off file (auto-discovered by exp_dev on emergency-refill cycles), NOT an inter-session routing note. exp_dev scans `notes/exp_dev_handoff_*.md` sorted by mtime.

Per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]]: if Anchor 2 (full 4-arm discriminator at N_DIM=8192 + multi-arm encoder ingest) qualifies as heavy cell, route smoke + dispatch via `hdi_orchestrator` not laptop.

-- Research (Opus 4.7 1M context)
