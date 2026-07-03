# Pre-reg: substrate_concept_encoder_component_C_modern_hopfield_readout

Date: 2026-07-03
Anchor: `substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03`
Cell file: `experiments/exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026-07-03.py`
Module: `hdlab/modern_hopfield_readout.py`

## Strategic framing

Component C in the brain-neocortex 3-analog set identified by 6-drill convergence 2026-07-02:
- Component A = VWFA-analog (hashed char-2/3/4-gram bank; dense; ventral fusiform gyrus). In flight as v2 P1 (commit `abe8e2ba`).
- Component B = ATL-hub-analog (dense amodal semantic hub; PPMI/SVD; NO k-WTA; anterior temporal lobe). In flight as V2-A (commit `a78a7f53`).
- **Component C = Semantic control / softmax retrieval** (modern-Hopfield readout; pMTG + IFG). THIS CELL.

**Rationale (per USER 2026-07-02 late night "if we need to develop those brain analogs we can" + "keep moving"):** current substrate mechanism (sparse-competitive-Hebbian k=2%) is HIPPOCAMPAL (DG-CA3 regime) architecturally. All 3 candidate rescues are NEOCORTEX. Component C tests whether the READOUT GEOMETRY was the single load-bearing lever — the encoder is fine but the argmax readout throws away the interpolation-between-stored-patterns behaviour that pMTG-IFG semantic control uses.

Reference notes:
- `notes/research_5x_drill_3_neuroscience_substrate_content_HF_2026-07-02.md` — neuroscience prescription
- `notes/research_5x_drill_4_physics_stat_mech_substrate_content_HF_2026-07-02.md` — physics-informed softmax attention over sparse-bipolar storage

Cited prior art:
- Ramsauer H, Schafl B, Lehner J, Seidl P, Widrich M, Adler T, Gruber L, Holzleitner M, Pavlovic M, Sandve GK, Greiff V, Kreil D, Kopp M, Klambauer G, Brandstetter J, Hochreiter S. Hopfield networks is all you need. ICLR 2021. arXiv:2008.02217.
- Krotov D, Hopfield J. Dense associative memory for pattern recognition. NeurIPS 2016.
- Prior substrate research reference: `notes/research_drill_tier_1_to_5_integration_architecture_deep_dive_2026-06-03.md` (Modern Hopfield identity as attention <-> Hopfield-update bridge; substrate-KB cosine 0.33).

## Task + corpus

**Task:** SUPERVISED held-out-synonym retrieval on substrate WordNet lexicon atoms.

- Corpus: `data/substrate_index/concept/atoms.jsonl` filtered to `kind=lexicon`, `pos in {n,v,a,r}`, `len(description) >= 20`, `len(synonyms) >= 3`, `lemma_freq_semcor >= 1`.
- Per atom training sentences: `[description, synonyms[0], synonyms[1], "related to <hypernym0>"]`.
- Held-out query: `synonyms[-1]` (never in training).
- Recall metric: `recall@{1, 5, 10}`.

**Regime:**
- SMOKE: N=100 atoms, seeds `[11, 17, 23]`, `n_dim=2048`. Expected wall ~5-15 min on local CPU.
- FULL: N=500 atoms, seeds `[11, 17, 23]`, `n_dim=2048`. Expected wall ~30-60 min.

## Arms (5 x 3 seeds = 15 units expected)

1. **`ARM_V1_CONCEPT_ENCODER_COSINE`** (baseline reproducer).
   - Fitted `ConceptEncoder(k_sparsity=0.02, max_pos=24)`.
   - Query encoded via `enc._surface_encoder.encode_sentence(q_word)`.
   - Readout: `top_k = argsort_desc(cos(surface(q), concept_hds))`.
   - HP_SCOPE: HP3 baseline recovery.
   - MEASURED reference: r@5=0.16 at N=100 seeds[11,17,23] n_dim=2048 MEASURED@`data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_concept_encoder_recall_at_5_mean`.

2. **`ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD`** (LOAD-BEARING; beta=4).
   - Same fitted `ConceptEncoder`; same surface query encoding.
   - Readout via `ModernHopfieldReadout(beta=4, normalize_query_and_store=True).top_k_by_retrieved`.
   - One-step Hopfield update: `y = softmax(beta * cos(q,K) / sqrt(N)) @ K`; then rank by `cos(y, K_i)`.
   - HP_SCOPE: HP1 rescue lift + HP2 beats bag.

3. **`ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD_HIGH_BETA`** (beta=8; sharper attention).
   - Same as arm 2 but `beta=8`.
   - HP_SCOPE: HP1 + HP2 (verdict computed on `max(hop_lo, hop_hi)`).

4. **`ARM_CHAR_TRIGRAM_UNSUP_REFERENCE`** (bag-word reference).
   - Char-trigram bundle prototypes; cosine argmax readout.
   - MEASURED reference: r@5=0.28 MEASURED@`data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_char_trigram_recall_at_5_mean`.
   - HP_SCOPE: HP2 reference target.

5. **`ARM_RANDOM_BASELINE`** (chance ceiling).
   - Uniform random permutation over N atoms; top-k = first k.
   - CHANCE @ N=100, k=5: 5/100 = 0.05.
   - HP_SCOPE: HP4 chance-band verification.

## HP / HF bands

**HARD_PASS (all 4 must fire on `max(HOPFIELD_lo, HOPFIELD_hi)` variant):**
- HP1 rescue lift: `HOPFIELD_r5 - COSINE_r5 > 0.10` (strict-above per META_RULE_L)
- HP2 beats bag: `HOPFIELD_r5 >= TRIGRAM_r5 + 0.05`
- HP3 baseline recovery: `|COSINE_r5 - 0.16| <= 0.03`
- HP4 chance floor: `RANDOM_r5 <= 0.10`

**HARD_FAIL priority order:**
- HF_ARMS_IDENTICAL: any seed has top-k stacks bit-identical across arms (structural readout bug or degenerate corpus).
- HF2 no bag beat: `HOPFIELD_r5 < TRIGRAM_r5` (MAJOR REFRAME — softmax readout doesn't reach char-trigram bag).
- HF1 no lift: `HOPFIELD_r5 - COSINE_r5 <= 0.03` (readout geometry didn't matter under equal-norm sparse-bipolar storage).

**MIDDLE_BAND:**
- `0.05 < HOPFIELD_r5 - COSINE_r5 <= 0.10` and one or more HP gates missed. Partial rescue; likely needs A+B composition.

## SCHEMA-VET gates (§15 A-E)

**A) `effective_vs_nominal_parameter_audit` — sweep_alignment_verdict:** ALIGNED
- No sweep axis on parameters that reroute through composition. beta is a per-arm hyperparameter, not a swept axis; two beta arms cover coarse variance. HP-relevant metric operates on `max(hop_lo, hop_hi)` so HP1 fires if either variant lifts.

**B) `bracket_includes_discriminating_band` — discriminating_fraction:** N/A for beta (2 discrete choices per arm), but HP1 discriminator = `HOPFIELD - COSINE` gap. Predicted range under equal-norm sparse-bipolar storage:
- Attention-weight ranking is IDENTICAL to cosine argmax (softmax is monotone in cosines when norms are equal).
- Retrieved-cosine ranking DIFFERS from cosine argmax when the query is a blend of concept HDs and the softmax has non-negligible mass on >1 prototype.
- Predicted lift: 0.02-0.15 range across beta = {4, 8} (HYPOTHESIZED@this prereg — no substrate MEASURED comparable at N=100 WordNet retrieval; will operationalize + report).
- Discriminator band centered on HP1=0.10; MIDDLE_BAND [0.05, 0.10]; HF1 [<= 0.03]. Predicted P(HP1) = 0.30-0.45 based on drill-4 physics prior that softmax over sparse-bipolar concentrates mass on 3-5 patterns when query is a blend, giving retrieved-HD interpolation but small cos-re-rank effect. Predicted P(MB) = 0.35-0.50. Predicted P(HF1) = 0.20-0.30.

**C) `signal_shape_compatibility_audit` — composition_edges:**
- `ConceptEncoder.surface_encoder.encode_sentence` -> `float32 [N_DIM]` -> `ModernHopfieldReadout.top_k_by_retrieved` -> `int64 [k]`. SHAPE_MATCH.
- `concept_hds` -> `int8 [n_atoms, N_DIM]` (sparse-bipolar) -> ModernHopfieldReadout casts to float32 on `_prep`. SHAPE_MATCH.
- ConceptEncoder's `_surface_encoder` is the identical path used by `ARM_V1_CONCEPT_ENCODER_COSINE` in `exp_substrate_concept_encoder_substrate_content_v1_2026-07-02`. Bit-for-bit reproducer.

**D) `reproduce_prior_chain_grade_result_as_positive_control` — positive_control_arms:**
- Positive control: `ARM_V1_CONCEPT_ENCODER_COSINE` at N=100 seeds[11,17,23] MUST reproduce prior MEASURED 0.16 r@5 within `|delta| <= 0.03` (HP3). Same encoder, same corpus filter, same n_dim=2048, same K_SPARSITY=0.02, same max_pos=24. If HP3 fails, cell's downstream HOPFIELD comparison is UNRELIABLE (encoder invocation mismatch).
- `ARM_CHAR_TRIGRAM_UNSUP_REFERENCE`: prior MEASURED 0.28 r@5. Not gated but reported.

**E) `functional_requirement_decomposition_present`:**
- FR1 (surface encoding query -> HD): satisfied by `ConceptEncoder.surface_encoder.encode_sentence` (chain-grade primitive, CG'd via char_positional_encoder).
- FR2 (fitted per-concept HD table): satisfied by `ConceptEncoder.fit` -> `concept_hds` (chain-grade, CG'd via Spoke 1 v3-D FULL 2026-07-02 competitive-Hebbian).
- FR3 (softmax attention retrieval over stored HDs): NEW primitive — `hdlab/modern_hopfield_readout.ModernHopfieldReadout`. Selftests: 10 tests passing (shape, exact retrieval, interpolation, beta effect, sparse-bipolar compat, N=8192 scale sentinel, attention-vs-retrieved ranking divergence under equal-norm, dim-mismatch guard, determinism, zero-K fallback).
- FR4 (verdict logic HP/HF band interpretation): satisfied by `_compute_verdict` with 4-way priority (HF_ARMS -> HF2 -> HF1 -> HP or MB).

## Cell-template mandates

- `arms_differ_verified: bool` at smoke gate via `_hash_topk_array` over per-arm top-k index stacks. Five arms must hash-distinct.
- `final_metrics_atomicity: "tmp_replace"` via `os.replace`.
- `except SystemExit: raise` BEFORE `except Exception`; no `except BaseException`.
- CRLB: N/A (supervised retrieval; chance floor k/N documented via ARM_RANDOM).
- `baseline_in_band`: at smoke, COSINE and TRIGRAM r@5 in `[0.05, 0.80]`. Both prior MEASURED (0.16, 0.28) satisfy this by construction; still gate-checked.
- Discriminator = `HOPFIELD - COSINE` gap; must be non-degenerate (i.e. |lift| > 1e-6) at smoke; if exactly zero, mechanism didn't fire (readout collapsed to identical top-k stacks).
- `HP_SCOPE`: HP3 on COSINE arm only; HP1+HP2 on HOPFIELD arms (`max` variant); HP4 on RANDOM arm.
- Number tagging: HP3_COSINE_MEASURED=0.16 MEASURED@`data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_concept_encoder_recall_at_5_mean`; TRIGRAM_REF=0.28 MEASURED@same:`arm_char_trigram_recall_at_5_mean`; RANDOM chance k/N=0.05 THEORETICAL@k=5,N=100 uniform sampling.
- `cardinality_ok`: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15; smoke gates on `landed_n_units == expected_n_units`.
- `calibration_check: "default_ok_for_this_regime"` — beta values (4, 8) chosen from Ramsauer 2020 typical range for scaled-dot-product attention with `/sqrt(N)` normalization; discriminator-fires gate verifies non-degenerate lift at smoke.

## Compute architecture

- **Class: (b) sequential-CPU with justification.** Cell is composed of tight numpy inner loops over ~100 queries at n_dim=2048; per-query cost dominated by concept_hds matmul (dense N_atoms x N_DIM = 100 x 2048 = ~200K float multiplies). Total FLOPs per seed = 5 arms * 100 queries * 200K = 100M multiplies; expected wall <60s per seed on CPU. GPU batching not justified at smoke scale.
- If FULL at N=500 exceeds 15 min wall per seed, upgrade to batched GPU matmul in v2.

## Storage strategy

- SHARDED per-atom concept HD table (`concept_hds[atom_idx]` addressed independently). No composition depth beyond L=1 (readout eval). Storage strategy inherited from ConceptEncoder (chain-grade).

## Progress logging

- `progress_logging: "print_flush_true"` — every arm log line has `flush=True`. `sys.stdout.reconfigure(line_buffering=True)` at main() entry for defense-in-depth. `CellHeartbeat(interval_s=30, every_n_units=1)` for external watchdog.

## Dispatch plan

1. `python -m hdlab.modern_hopfield_readout` selftests — DONE, 10/10 PASS.
2. Cell `--self-test` on `.venv` — MUST PASS.
3. Cell `--smoke` on `local_cpu_queue` (USER 2026-07-01 LOCK: smoke on local; FULL only remote).
4. Report smoke per-arm metrics + HP verdict to Director + USER.
5. **HOLD BEFORE FULL** — Director + USER weigh outcome. Full dispatched only after review.

## Meta-rules touched

`AC_hypothesized_measured_tagging`, `AF_arms_differ`, `AG_baseline_in_band`, `AH_atomic_final_metrics`, `H_cardinality_ok`, `K_discriminator_fires`, `L_strict_above_floor`, `M_calibration_default_ok`, `run_mode_verification_16`, `smoke_only_local_cpu_2026-07-01`.
