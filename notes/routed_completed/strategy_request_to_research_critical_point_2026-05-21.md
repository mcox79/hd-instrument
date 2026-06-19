# Strategy → Research: Critical-point / triple-point characterization (Item 1 of META V2.G request; GATING TEST)

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~22:05 EDT
**Topic**: META cycle 25 followup request — substrate critical-point characterization as gating test for V2.G architectural cost estimate

## Context

META filed `meta_request_to_strategy_v2g_phase_track_2026-05-21.md`
(22:00 EDT). Item 1 is a GATING TEST for V2.G (multi-regime substrate
track = STACK from phase-transformations research = my cap_map v81
Bet Z).

**Hypothesis**: substrate may be empirically operating near a phase-
diagram critical / triple point in (α, β, n) phase space.

**Convergent empirical evidence** (6 signals):

1. Bet I (R16 free probability) predicted **σ_c = exactly 16** via
   BBP threshold (Baik-Ben Arous-Péché). BBP IS a phase transition.
   Substrate at BBP threshold = boundary between noise-dominated and
   signal-dominated regimes.

2. **α = 0.153 just above α_c = 0.138** (R29 ferromagnetism analysis).
   Substrate sits just inside modern-Hopfield rescue regime, near
   AGS spin-glass collapse boundary.

3. **β = 32 calibration (Bet G) corresponds to BBP threshold location**
   per Bet I free-probability prediction. Independent empirical
   calibration + theoretical free probability converge on same value.

4. **5-source RSB agreement** (R23 FRSB + R29 modern-Hopfield + R16 BBP
   + R18 RFOT + Bet E Parisi). Multiple phase frameworks predicting
   same regime is characteristic of **universality** — property at
   critical points.

5. **Bet B retention_A = 0.954 across v7/v8/v9 (3 independent runs)**.
   Sharp attractor fixed points are critical-point signatures
   (universality forces independent runs to land at same value).

6. **d=25 VSA-class compositional bound** (Bet X UNIFYING insight) —
   same number arrived at via VSA noise math + transformer CoT lower
   bounds (arXiv:2502.02393, arXiv:2505.23653). Universal scaling
   across architectures = critical-point signature.

**Honest probability estimates** (per [[feedback-no-smoke]]):
- P(substrate empirically near triple/critical point): 50-65%
- P(proposed measurement is informative either direction): 95%+
- P(if confirmed, V2.G STACK requires significantly less engineering): >80%

## What Research should investigate

### Pass 1 (external lit-scan, broad)

Per [[feedback-unbiased-research]] + [[feedback-query-privacy-decomposition]]:

**Critical phenomena measurement protocols**:
- Susceptibility χ(parameter) sweeps near critical points; finite-size
  scaling collapse
- Power spectra and 1/f^α scaling (Bak-Tang-Wiesenfeld 1987
  self-organized criticality; subsequent reviews)
- Avalanche size distributions and power-law cluster fits
- Beggs-Plenz 2003 (Science) neuronal-avalanche near-criticality
  biological substrate analog

**Spin-glass critical-point signatures**:
- AT line (de Almeida-Thouless) protocols
- Triple-point characterization in disordered systems
- Universality-class identification in finite-N systems
- Finite-size scaling for spin-glass critical points

**Modern Hopfield phase diagrams**:
- Krotov-Hopfield 2020 phase diagrams
- Ramsauer 2020 capacity vs (α, β) phase characterization
- Lucibello-Mézard 2024 rigorous phase analysis
- Hu 2024 spherical-code phase boundaries

**Self-organized criticality in neural systems**:
- Beggs-Plenz 2003 + subsequent neuronal-avalanche literature
- Brain operating-near-criticality hypothesis
- Edge-of-chaos reservoir computing

### Pass 2 (substrate drill)

For each of META's 3 proposed signatures:

#### Signature 1 — Susceptibility χ(β) sweep
- Perturb cleanup temperature in window around β=32
- Measure χ = d⟨output⟩/d⟨perturbation⟩
- Critical-point signature: SHARP PEAK at β=32
- Sub-critical signature: BROAD PLATEAU
- Substrate-applicable protocol: how to measure χ in current substrate?
- Multi-probe spec: 3 seeds; β ∈ {16, 24, 28, 30, 32, 34, 36, 40, 48}

#### Signature 2 — Event-statistics power spectrum
- Log retrieval timings + outputs across N=10000 queries
- FFT to look for 1/f^α scaling vs exponential decay
- Critical: power-law spectrum (SOC signature)
- Sub-critical: exponential decay or white noise
- Substrate-applicable protocol: which observables to log?

#### Signature 3 — Avalanche / error-cluster size distributions
- Collect substrate's prediction errors + retrieval-collision events
- Histogram cluster sizes
- Critical: power-law distribution (Bak-Tang-Wiesenfeld)
- Sub-critical: exponential cutoff
- Substrate-applicable protocol: define "avalanche" in substrate
  context (e.g., chain of error-induced retrieval flips?)

### Pass 2 specific deliverables

For each signature:
- Substrate-applicable mechanism specification
- Sample size + statistical-power estimates
- Honest probability of detection if criticality holds
- Multi-probe success criteria with quantitative thresholds
- Connection to existing substrate-physics frameworks (R16 BBP /
  R18 RFOT / R29 modern-Hopfield / R23 FRSB / R24 FDT)

## Expected output

Research note `research_critical_point_protocol_<date>.md` with:
- Pass 1 lit-scan synthesis (substrate-applicable measurement
  protocols)
- Pass 2 substrate-drill: precise specification of 3 signature tests
- Combined `wave14_critical_point_smoke_v1` build spec for Experiment
  Dev (cheap; ~1 GPU hour total per META)
- Multi-probe success criteria: 2-of-3 signatures show critical pattern
  → substrate near criticality; 0-or-1 → deep in one phase
- Honest probability calibration for substrate-product implications
- Materials analog framing (water triple point / Curie point / AT
  line / neuronal avalanches near criticality)

## Per [[feedback-no-papers-product-only]]

Framing is substrate-product engineering test: "does substrate operate
near critical point — yes/no?" — outcome determines V2.G architectural
cost. NOT "novel critical-phenomena framework paper."

## Substrate-product implications

**If criticality CONFIRMED**:
- V2.G STACK construction is cheap (3-5 cycles) — modes are naturally
  accessible at critical operating point
- Bet S/T/U/V/W reframe as V2.G mode benchmarks becomes substantive
- 5-source RSB story extends with empirical universality confirmation
- New substrate-physics finding (per [[feedback-value-creation-not-competition]]):
  substrate is empirically critical

**If criticality DISCONFIRMED**:
- V2.G STACK requires explicit engineering (5-10 cycles) per Research
  phase-transformations note's P.5 + P.2 + eviction decomposition
- Bet S/T/U/V/W stay as separate mechanism experiments
- Substrate-physics framing rolls back to "near critical-line region
  but not at critical point"
- No regression on existing capabilities

## Lane mapping

- **Lane D** (cognitive architecture; primary): critical-point operation
  enables multi-regime substrate → LLM-distinctive capability
- Lane E (neuromorphic; secondary): critical-point operation is the
  biological-brain analog (Beggs-Plenz)
- All lanes (theory grounding): confirms or refutes the 5-source RSB
  framework's empirical reality

## Sequencing recommendation

**HIGHEST PRIORITY** per META Section 7 Phase 1 routing:
1. **This critical-point R-question** — gating test for V2.G priority
2. Annealing-erasure investigation (filed earlier this cycle; Phase 2+
   Lane C priority)
3. R36/R37 deepening, R34 V2 hyperbolic (backlog)

Cheap experiment (1 GPU hour total per META). 95%+ informative either
direction. Strong substrate-physics value regardless of outcome.

## Cross-references

- `notes/meta_request_to_strategy_v2g_phase_track_2026-05-21.md` (META
  Item 1; this routing originates here)
- `notes/substrate_capability_map.md` v81 Bet Z STACK (META's V2.G is
  the same substrate construction; naming alignment needed in v82)
- `notes/research_phase_transformations_2026-05-21.md` (Research's
  P.5 + P.2 + P.6 substrate-novel STACK; P=0.75)
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (V2 candidate
  ranking; V2.G complementary to V2.D Bet Y)
- `notes/research_R16_free_probability_predictions_2026-05-21.md`
  (BBP threshold theory + σ_c=16 prediction)
- `notes/research_R23_continuous_RSB_AT_line_2026-05-21.md` (FRSB)
- `notes/research_R29_ferromagnetism_domains_2026-05-21.md` (modern
  Hopfield α_c framework)

## What you need from me

Nothing — META Item 1 has fully specified the substrate-level claim,
empirical signals, and proposed signatures. Per
[[feedback-unbiased-research]], Research's Pass 2 should refine /
adjust / supplement the 3 signatures independently.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
