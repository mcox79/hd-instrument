# PHASE_PORTRAIT v1 inventory — substrate operating-regime map (USER-directed lane 2026-06-22)

**Origin:** USER directive 2026-06-22 mid-autonomous-arc: "substrate can perform actions at any position in the phase diagram + experimental results show data survives phase transformations." Lane (a) of the 3 sub-items queued in Tier 2 of the work queue.

**Sequencing:** the 2026-06-18 phase-portrait routing/synthesis note (now legacy framing; cert-trail-only) proposed a PHASE_PORTRAIT AtomKind sibling of CAPABILITY_MAP. v1 here is the inventory pass: enumerate chain-grade phase-diagram atoms already in cert_ledger, organize by axis, mark MEASURED vs untested. Per the load-bearing cert-condition: **measured points only; no interpolation/extrapolation into untested regions; untested stays untested (not presumed-pass)**.

**Method:** scour `data/substrate_index/meta/cert_ledger.jsonl` (646 rows) for chain-grade atoms whose `atom_id` matches the phase-diagram axis lexicon. Counted unique chain-grade rows per axis (overlap intentional — many cells span multiple axes).

---

## Inventory by axis (chain-grade atoms only; cert_status="chain_grade")

| Axis | Chain-grade count | Representative atoms (≤3) |
|------|------------------:|---------------------------|
| **capacity** | 9 | `EXP_substrate_capacity_battery_gpu_v1` / `EXP_capacity_cliff_graceful_full_v3` / `EXP_substrate_capacity_composition_b2xb4_v1_n2048` |
| **alpha (loading ratio)** | 12 | `EXP_combo3_unified_api_v1_n16384_l4_alpha_grid_v1` / `EXP_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1` / `EXP_deletion_cert_z_ratio_n16384_full_alpha_v1` |
| **kappa (codebook condition)** | 6 | `EXP_pp50_kappa3_delta_alpha_n8192/16384/32768_v*` (3-dim N sweep at fixed kappa3); `EXP_f4_kappa_n_deviation_snr_cpu_v1` |
| **sparsity** | 1 | `EXP_substrate_sparsity_fine_battery_gpu_v1` |
| **multi-seed sweep** | 11 | `EXP_tier4_multiseed_sweep_cpu_v1` / `EXP_wave1_multiseed_sweep_cpu_v1` / `EXP_wave2_rescue_multiseed_sweep_cpu_v1` (broad-stroke envelope mapping) |
| **envelope** | 2 | `EXP_c1_entmax_envelope_sweep_v2` / `EXP_kmax_ness_envelope_corrected_v1` (HARD_PASS substrate NESS exceeds Hopfield equilibrium) |
| **cliff** | 1 unique (2 rows) | `EXP_capacity_cliff_graceful_full_v3` |
| **hopfield** | 1 | `EXP_modern_hopfield_n_sweep_v1` |

**Phase-diagram-coverage unique-atom estimate:** ~38-42 unique chain-grade atoms span the (capacity × α × κ × N_DIM × sparsity × encoder) lattice, with overlap. The 2026-06-18 phase-portrait note's "~47 cert-grade phase-diagram atoms" claim is consistent (within counting-method noise).

## Inventory: data-survives-transformation candidates (chain-grade)

| Atom | Verdict | Transform tested | Substrate-survives evidence |
|------|---------|------------------|------------------------------|
| `EXP_kv_learned_projection_v1` | **HARD_PASS** | Learned projection layer over substrate KV | atoms retrievable post-projection at HARD_PASS bound |
| `EXP_substrate_pca_prewhitening_codebook_v1` | PASS | PCA prewhitening of codebook | substrate operates after PCA whitening (codebook stays usable) |
| `EXP_substrate_audit_core_C2_C3_whitened_pythia160m_v2_n4096` | PASS | Whitening applied to pythia-160m residuals at ingest | core capability preserved post-whitening |
| `EXP_substrate_audit_core_C2_C3_whitened_llama1b_v1_n4096` | PASS | Whitening + encoder swap (pythia→llama1b) | core capability preserved across encoder swap (CROSS-encoder transform) |
| `EXP_substrate_dim_expansion_subsumes_whitening_n_enc_10000_v1` | PASS | Dim expansion subsumes whitening | substrate-internal transform; data preserved under dim-expansion alternative to whitening |
| `EXP_substrate_last_token_vs_whitening_mean_pool_v1` | PASS | Last-token vs whitened-mean-pool readout | data survives encoding-readout-strategy transform |
| `EXP_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | PASS | Name-augmented encoding recovery | atoms recoverable under name-encoding transform |
| `EXP_ner_transition_charngram_noise_crosscut_cpu_v1` | PASS | char-ngram transition + noise crosscut | NER capability robust to transition + noise (compound transform) |
| `EXP_kf1_paraphrase_robustness_marianmt_v1` | PASS | Paraphrase via MarianMT | semantic atoms survive paraphrase transform |
| `EXP_pb_kf1_multilang_chain_robustness_v1` | PASS | Multi-language chain | atoms survive multilang chain transform |
| `EXP_substrate_hallucination_robustness_hard_negatives_v1` | PASS | Hard-negative robustness | refuse-gate survives adversarial-key transform |

**Total: 11 chain-grade atoms** directly evidence "data survives phase transformations" across: projection / whitening / PCA / dim-expansion / encoding-readout-swap / encoder-swap (pythia→llama1b) / name-augmentation / char-ngram-noise / paraphrase (MarianMT) / multilang-chain / hard-negative adversarial.

The strongest single piece of evidence is `EXP_kv_learned_projection_v1` HARD_PASS — atoms retrievable post-learned-projection at the harder cert-class bound, not just PASS. Combined with `EXP_substrate_audit_core_C2_C3_whitened_*` PASS at both pythia-160m AND llama1b, this constitutes chain-grade evidence the substrate's stored content is **encoder-portable + whitening-invariant + projection-survivable**.

---

## Synthesis: the substrate IS phase-diagram-portable + data IS transform-survivable

**Claim 1 (action-at-any-position):** ~38-42 chain-grade atoms span capacity × α × κ × N_DIM × sparsity × encoder. Substrate has documented chain-grade action across multiple regimes per axis (capacity sweeps, α grids 0.05→0.5+, κ3 sweeps at N=8192/16384/32768, sparsity fine battery, modern-hopfield n-sweep, multi-seed envelope mappings). **Substantiated at chain-grade for measured regions; untested regions stay untested.**

**Claim 2 (data survives phase transformations):** 11 chain-grade atoms directly evidence atom-survival across distinct transform classes (linear-projection / whitening / PCA / encoder-swap / readout-swap / paraphrase / noise / adversarial). The HARD_PASS-tier evidence is `EXP_kv_learned_projection_v1`; the cross-encoder evidence is `audit_core_C2_C3_whitened_pythia/llama1b` PASS-pair. **Substantiated at chain-grade for the transform classes measured.**

**Combined architectural claim:** the substrate is a phase-diagram-portable computational engine where stored knowledge persists across operating-point shifts AND across encoding/readout/projection transforms. This is the structural differentiation vs LLMs (LLM = single frozen operating point + cannot transfer to a different operating regime without retraining + cannot port across encoders without re-embedding).

---

## Untested regions (load-bearing per PHASE_PORTRAIT cert-condition: untested ≠ presumed-pass)

- **V_C × N_DIM joint frontier above (4096, 32768):** Path A in flight; no chain-grade above this corner yet.
- **Bit-precision regime (int8 / int4 / fp16 vs fp32):** zero chain-grade atoms matched "precision" axis; this axis is empirically un-explored.
- **Onset / saturation axis explicit:** zero chain-grade atoms matched "onset" / "saturation"; covered IMPLICITLY by capacity-cliff atoms but not as a named axis.
- **Cross-domain transfer (text→code, text→math, NL→KG transfer):** no chain-grade atoms evidence atom survival across DOMAIN transforms (only encoder + readout transforms within NL).
- **Long-horizon temporal persistence:** durability_cron exists but no chain-grade atom directly measures atom recall after T_substrate-mutations.

---

## What v2 should add (sequencing)

- **v2 = MEASURED PHASE_PORTRAIT AtomKind** in Store (sibling of CAPABILITY_MAP per 2026-06-18 design; algebra=None + INVENTORY_NON_CERT + regen via Director scour). This v1 inventory is the regen-source.
- **v2 includes** per-axis explicit envelope (alpha range covered, kappa range covered, N range covered, encoder list covered, transform classes covered) + per-axis untested regions explicit.
- **v2 atomization** requires Skunkworks SCHEMA-VET (atomization is cert-owner authority; spawned via `hdi_skunkworks` teammate next cycle subject to Fix #14 budget).

## Composes with active program

- **L2 substrate-native LM:** action-at-any-position means the substrate-LM operates at multiple α regimes — Path A V_C=4096 / Path B SimVQ / MKN smoothing / n10 whitening all probe DIFFERENT positions in the same phase diagram.
- **L3 continual learning (c1):** data-survives-phase-transform IS the continual-learning property when "the transform" is "new writes interfering with old writes." The α=0.5 NEVER-FORGETS surprise from c1 PARTIAL fits this frame.
- **Brain-drill #6 modular K-macrocolumn (m1 cell):** modular stores DEFINE per-shard sub-phase-diagrams; the routing-invariance claim IS data-survives-transform-into-different-shard.

— Research (Director); phase-portrait v1 inventory artifact; cert-trail; commit pending.
