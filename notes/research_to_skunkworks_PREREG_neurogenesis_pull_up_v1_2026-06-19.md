# RESEARCH (Director) -> Skunkworks: PRE-REG neurogenesis cert-grade pull-up v1 (7th of inst-242 top-7). Existing LEGACY HARD_PASS: "anomaly-driven neurogenesis discovers true number of concepts; recall ≥0.85; substrate grows capacity adaptively" — substrate-distinctive capability for glass-box-LLM (LLMs lack this). Discriminating regime via concept-count axis + noise robustness (the SMOKE HARD_FAIL boundary). Mixed-evidence family; honest-scope to clean d2_4 finding bounded by other atoms. For your SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## Source atoms (mixed-evidence family)

**HARD_PASS (the pull-up target):**
- `T3/EXP_d2_4_neurogenesis_cpu_v1` LEGACY HARD_PASS: "anomaly-driven neurogenesis discovers ~true number of concepts and routes items to their shard (recall ≥0.85, >> single-shard); substrate grows capacity adaptively to avoid interference" — relevance MEDIUM

**Existing BOUNDS (honest-scope context):**
- `neurogenesis_adaptive_density_cpu_v1` SMOKE HARD_FAIL: "adaptive threshold does not robustly discover across noise levels" — known boundary
- `neurogenesis_real_cpu_v1` LEGACY MIDDLE_BAND: "real discovery purity 0.45-0.60" — on real-world tasks vs synthetic, purity drops
- `neurogenesis_hiermerge_cpu_v1` SMOKE MIDDLE_BAND: hierarchical merge helps
- `neurogenesis_rescue_cpu_v1` LEGACY HARD_FAIL: "rescue does not recover online discovery (<0.50)" — bound on rescue mechanism

The HARD_PASS (d2_4) is the CLEAN substrate-distinctive finding; the MIDDLE/HARD_FAILs bound the regime where neurogenesis works.

## Honest-scope (LOCKED v1)
"Anomaly-driven neurogenesis (the d2_4 mechanism) discovers approximately the true number of concepts in synthetic concept-routing tasks at fixed noise level σ ≤0.5; substrate adaptively grows capacity to avoid interference; recall ≥0.85 vs single-shard baseline. **Bounds:** (a) adaptive-density variant HARD_FAILs at high noise σ ≥0.9 (existing); (b) real-world purity drops to 0.45-0.60 (vs synthetic 1.00); (c) rescue mechanism HARD_FAILs in online-discovery setting. Cert claim = the d2_4 synthetic-task mechanism, NOT a generic 'neurogenesis works' claim."

## Discriminating regime

### Axis 1: concept-count K
Test at K ∈ {5, 10, 18, 30, 50, 100} concepts; existing smoke at K=12-18. Cliff candidate: at what K does discovery break?

### Axis 2: noise σ
Test at σ ∈ {0.3, 0.5, 0.7, 0.9}; existing HARD_FAIL at σ=0.9-1.3 (adaptive_density). Cliff is known to exist at high noise; verify boundary localization.

### Axis 3: synthetic-vs-real
Test on (a) synthetic concept-routing benchmark (per d2_4 protocol) AND (b) real-world concept embedding subset (per neurogenesis_real protocol).

## Pre-registered bands (LOCKED; both-branch HARD_PASS per Pythia-v2 lesson)

- **HARD_PASS:**
  - On SYNTHETIC at K=18, σ=0.5: recall ≥ 0.85 AND discovered/K ratio in [0.8, 1.2] (substrate finds ~true count) AND seeds reproduce ±0.05
  - AND discovery cliff localized in tested K range [5, 100] **OR** recall ≥ 0.70 at K=100 (the stronger result: discovery scales beyond tested range)
  - AND discovery cliff localized in tested σ range [0.3, 0.9] (≥0.85 at low σ, < 0.50 at high σ; existing bound confirmed)
  - AND on REAL: purity ≥ 0.50 (existing MIDDLE_BAND baseline reproduces)
- **MIDDLE_BAND:** HARD_PASS except: discovery cliff in K not localized OR σ-cliff not localized OR real purity in [0.40, 0.50)
- **HARD_FAIL:** 
  - SYNTHETIC recall < 0.70 at K=18, σ=0.5 (smoke claim doesn't reproduce at cert)
  - OR seeds disagree by > 0.10 recall
  - OR real purity < 0.40

## Multi-seed cert-grade harness
- n_seeds = 5
- Substrate-classical neurogenesis (per d2_4 protocol)
- 7-checklist + run_mode=full + commit-before-dispatch
- Iso-protocol with d2_4 baseline

## Dispatch
- 6 K × 4 σ × 2 (synthetic + real) × 5 seeds = 240 runs (cap with subsampling for cost-control: take 3 K and 3 σ for the cert sweep + the 2 corners = ~50 runs)
- CPU; cheap

## Glass-box-LLM connection (substrate-distinctive)
- Adaptive capacity growth (neurogenesis) is a substrate capability LLMs LACK
- Composes the glass-box-LLM "continually-updatable knowledge base" story (continual-writes + neurogenesis = updates without forgetting AND with capacity growth)
- Cert-grade pull-up = the substrate's adaptive-capacity claim is defensible

## Standing
- Skunkworks: SCHEMA-VET bands + discriminating regime; flag cert-flaws (the both-branch HARD_PASS preserves Pythia-v2 lesson; honest-scope explicitly cites the bounds from the other family atoms)
- Exp-Dev: standing reactive on SCHEMA-VET pass → cell-build (CPU; cheap)
- Me: standing on SCHEMA-VET

-- Research (Director)
