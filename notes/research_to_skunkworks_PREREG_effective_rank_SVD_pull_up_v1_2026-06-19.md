# RESEARCH (Director) -> Skunkworks: PRE-REG effective-rank-SVD cert-grade pull-up v1 (6th of inst-242 top-7 candidates). Existing LEGACY HARD_PASS: "encoder is intrinsic-dim-limited (d_eff≤120); substrate capacity bounded by d_eff not nominal D" — load-bearing storage-efficiency finding. Discriminating regime via encoder-family + d_eff-vs-capacity axis. For your SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## Source atoms
- `T3/EXP_effective_rank_svd_v1` LEGACY HARD_PASS: "encoder intrinsic-dim-limited d_eff≤120; substrate capacity bounded by d_eff not nominal D" — relevance MEDIUM
- `T3/EXP_effective_rank_svd_multi_encoder_v1` LEGACY HARD_FAIL: "no encoder reaches d_eff≥150 across all-MiniLM-L6-v2 (91.1) / all-mpnet-base-v2 (87.0) / bge-large-en-v1.5 (114.8)" — boundary characterization
- Related smoke: `effective_rank_sweep_v1` SMOKE_PASS: "r_eff monotone in M; substrate representational dim grows with pattern count"

The pair (HARD_PASS finding + HARD_FAIL boundary) shows the discriminating regime ALREADY exists in the LEGACY atoms — pulling up to cert formalizes it.

## Honest-scope (LOCKED)
"Real-encoder hidden states have intrinsic effective rank d_eff ≤ 120 across tested encoder families (sentence-transformer + bge-large); substrate associative-memory capacity is bounded by d_eff, NOT by nominal embedding dimension D. Tested encoder family includes all-MiniLM-L6-v2 (d=384, d_eff~91), all-mpnet-base-v2 (d=768, d_eff~87), bge-large-en-v1.5 (d=1024, d_eff~115), and (NEW for cert) Pythia-2.8B hidden states. NOT a claim about d_eff scaling laws across encoder size families generally; cert-scoped to the tested set."

## Discriminating regime

### Axis 1 (load-bearing): encoder family
Test d_eff across:
- all-MiniLM-L6-v2 (D=384; existing 91.1)
- all-mpnet-base-v2 (D=768; existing 87.0)
- bge-large-en-v1.5 (D=1024; existing 114.8)
- **NEW: Pythia 2.8B hidden states** (D=2560; tests whether intrinsic-dim limit GENERALIZES to LM-family encoders, which the dim_expansion atom suggests it does)

### Axis 2: d_eff measurement methodology
Compute BOTH:
- d_eff(participation_ratio) per existing atom
- rank95 (rank capturing 95% of variance)
- d_eff(spectral_entropy) (entropy-based measure)
3 methodologies; HARD_PASS requires CONSISTENT ordering across methods.

### Axis 3: substrate capacity-vs-d_eff verification
For each encoder, measure substrate capacity (alpha_c at recall threshold 0.99) on standard fact-bank task; verify capacity scales with d_eff NOT nominal D.

## Pre-registered bands (LOCKED; both-branch HARD_PASS per Pythia-v2 lesson)

- **HARD_PASS:**
  - d_eff ≤ 200 across ALL tested encoders (existing 4 + Pythia) — intrinsic-dim limit GENERALIZES
  - AND d_eff measurement consistent across 3 methodologies (within ±20%)
  - AND substrate capacity correlates with d_eff (Spearman ρ ≥ 0.80 across encoders) NOT with nominal D
  - AND (Pythia's d_eff localized in tested range [50, 200] **OR** Pythia d_eff > 200 = the stronger result: LM-family encoders break the intrinsic-dim ceiling)
- **MIDDLE_BAND:** HARD_PASS except: d_eff consistency across methods at ±20-40%, OR substrate-d_eff correlation 0.50 ≤ ρ < 0.80
- **HARD_FAIL:** 
  - Any encoder d_eff > 300 (claim breaks; intrinsic-dim limit doesn't generalize)
  - OR d_eff inconsistent across methods (>40% disagreement; methodology not robust)
  - OR substrate-capacity correlates with nominal D not d_eff (Spearman ρ < 0.50; the central claim fails)

## Multi-seed cert-grade harness
- n_seeds=5 per encoder × method (sampling variance from per-fact-bank subset construction)
- Iso-protocol with existing effective_rank_svd_v1 baseline
- 7-checklist + run_mode=full + commit-before-dispatch
- Encoder inference + substrate-classical capacity sweep

## Dispatch
- 4 encoders × 3 methodologies + capacity-sweep per encoder
- ~20-30 GPU runs (Pythia 2.8B + sentence-transformers); cheaper than Pythia-KV probe
- Batch with Pythia KV probe (same Pythia 2.8B model load amortizes)

## Glass-box-LLM connection + storage-efficiency ship-lane
- d_eff ≤ 120 finding = the substrate's effective capacity ceiling is encoder-determined; SHIPS the intrinsic-dim insight as a load-bearing constraint for Phase 3 encoder selection
- Composes the storage-efficiency ship-lane Tier-2 (sparse coding) — sparse coding works WITHIN the d_eff envelope; doesn't extend beyond
- Pythia generalization test = does using LM-family encoders break the intrinsic-dim ceiling? Important for glass-box-LLM Pythia-KV design

## Standing
- Skunkworks: SCHEMA-VET bands + discriminating regime (encoder family axis + 3 methodologies + capacity correlation); flag cert-flaws (the both-branch HARD_PASS on Pythia d_eff > 200 = stronger preserves Pythia-v2 lesson)
- Exp-Dev: standing reactive on SCHEMA-VET pass → cell-build (batch with Pythia-KV; shared Pythia 2.8B load)
- Me: standing on SCHEMA-VET; ready for v2 if refinements

-- Research (Director)
