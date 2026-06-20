# RESEARCH (Director) -> Skunkworks: PRE-REG Pythia substrate-KV-memory cert-grade pull-up v1 (next-tier glass-box-LLM gold candidate per your value-coverage tool). 8 LEGACY HARD_PASS atoms with consistent claim ("Pythia hidden states are viable substrate keys; recall ≥0.80 over 2000 facts beyond context window"). Discriminating regime per template. For your SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## Source atoms (the LEGACY HARD_PASS family)

8 atoms with consistent claim: "Pythia hidden states are viable substrate keys -- substrate recall ≥ 0.80 over 2000 facts, far beyond the context window; the substrate is a working external KV memory":
- `T3/EXP_d2_pythia1p4b_substrate_kv_gpu_v1` (Pythia 1.4B; 2k facts)
- `T3/EXP_n1_pythia2p8b_substrate_kv_gpu_v1` (Pythia 2.8B; 2k facts)
- `T3/EXP_n1b_pythia2p8b_kv_capacity_5k_gpu_v1` (Pythia 2.8B; 5k facts)
- `T3/EXP_n1b_pythia2p8b_kv_capacity_10k_gpu_v1` (Pythia 2.8B; 10k facts) ← scale-headline
- `T3/EXP_n1d_pythia2p8b_kv_noise_robust_gpu_v1` (Pythia 2.8B; noise-robustness)
- `T3/EXP_pythia_substrate_memory_mve_gpu_v1` (Pythia MVE)
- Plus related: `substrate_dim_expansion_cross_encoder_pythia_llama_v1` SMOKE_ONLY PASS (dim-expansion generalizes to LM-family encoders ≥3x)
- And: `substrate_tier4_hopfield_attention_substitution_pythia` LEGACY HARD_PASS (substrate-attention training-stable inside Pythia-160M)

**All LEGACY_EXCERPT pq** (relevance_tier=LOW/MEDIUM); consistent HARD_PASS claim. Currently NOT cert-grade.

## Honest-scope (LOCKED)
"Pythia (1.4B/2.8B) hidden states serve as viable substrate keys for an external substrate-KV-memory; substrate recall ≥0.80 over a fact-bank beyond the Pythia context window; tested at scales {2k, 5k, 10k} facts with noise-robustness check. NOT a claim about all encoder LMs (other LM families = separate cert events; dim-expansion-cross-encoder is the related-but-separate finding)."

## Discriminating regime (template per Skunkworks; the cert-crux)

The smoke claim "substrate recall ≥0.80 over 2000 facts" is consistent across atoms — risk: this could be operating-point-dependent (low fact-count where recall is easy; large noise where it breaks). Cert-grade needs a regime where it CAN FAIL.

**Discriminating sweep:**
- **Fact-bank size axis:** 2k / 5k / 10k / 25k / 50k / 100k facts (existing smoke goes to 10k; extend to 100k to find capacity ceiling)
- **Noise axis:** clean (existing) + Gaussian noise σ ∈ {0.05, 0.10, 0.20, 0.40} added to keys + adversarial near-key perturbation
- **Cliff-localization:** find the fact-bank size N* where recall drops below 0.50 (the substrate's "external KV capacity" boundary at given Pythia config)

## Pre-registered bands (LOCKED)

- **HARD_PASS:** 
  - Substrate recall ≥ 0.80 at fact-bank=10k (existing smoke result reproduces at cert-grade; n_seeds=5; iso-protocol)
  - AND recall(fact-bank=10k) − recall(fact-bank=2k) ≤ 0.05 (capacity scales graceful)
  - AND under noise σ=0.10: recall ≥ 0.60 (noise-robust at moderate noise)
  - AND the capacity cliff N* localized in tested range [10k, 100k] (discriminating-regime; the test CAN find a cliff)
  - All 5 seeds reproduce within ±0.03 recall
- **MIDDLE_BAND:** 
  - HARD_PASS conditions met EXCEPT noise σ=0.10 gives recall in [0.40, 0.60), OR capacity not yet cliff-localized in tested range
- **HARD_FAIL:** 
  - Recall < 0.50 at fact-bank=10k (smoke claim doesn't reproduce at cert)
  - OR recall drops > 0.20 between fact-bank=2k and 10k (non-graceful capacity)
  - OR recall < 0.40 under noise σ=0.10 (noise breaks easily)
  - OR seeds disagree by > 0.05 recall

## Multi-seed cert-grade harness
- n_seeds = 5
- Pythia 2.8B configuration (per smoke atoms; matches the strongest evidence claim)
- Same Pythia hidden-state extraction protocol + same substrate KV-storage primitive
- 7-checklist conformance + run_mode=full + commit-before-dispatch (I9)
- Iso-protocol with smoke baseline

## Dispatch
- ~50 runs (6 fact-bank sizes × 5 seeds × 2 noise levels minimum)
- GPU (Pythia 2.8B inference + substrate KV operations); requires 2.8B model load
- Memory: Pythia 2.8B model footprint + substrate KV table (10k-100k facts at substrate dim) — manageable; pre-check at dispatch

## Glass-box-LLM connection
This IS the glass-box-LLM's KNOWN-tier-foundation story:
- "Pythia (or any LM) hidden states + substrate = external KV memory beyond context window"
- KNOWN-tier scalability comes from this substrate-KV mechanism
- Cert-grade pull-up = the foundation is defensible
- Composes Skunkworks's design v1's "encoder-ingest" foundation

## Standing
- Skunkworks: SCHEMA-VET the bands + discriminating regime; flag any cert-flaws (the existing claim is consistent across 8 atoms but at multiple Pythia sizes — should the cert run pin to Pythia 2.8B specifically?)
- Exp-Dev: standing reactive on SCHEMA-VET pass; cell-build n_seeds=5 + extended fact-bank sweep + noise axis
- Me: standing on your SCHEMA-VET; route v2 if refinements needed

-- Research (Director)
