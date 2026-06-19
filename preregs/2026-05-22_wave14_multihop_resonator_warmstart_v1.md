# Pre-reg: Wave 14 Multi-hop Resonator with VAMP-Backward Warm-Start v1

**Filed:** 2026-05-22
**Source:** `research_multihop_mechanism_3rd_attempt_2026-05-22.md` (Research 20:23 EDT) — Test 4.

## Question

Does initializing Resonator iteration with VAMP-backward smoothed posteriors (instead of bare argmax warm-start) restore chain composition at N=65536?

Cycle 127 results: Resonator (forward-only loopy iteration) failed; VAMP-on-chain (tree-exact forward-backward) PERFECT. Two possible causes for Resonator failure:
- (a) Loopy within-hop dynamics fundamentally fail.
- (b) Resonator failed only because it lacked cross-hop backward evidence.

Test discriminates: if warm-start RESCUES Resonator → (b); if Resonator still fails → (a) loopy-BP-cycle independent failure mode.

## Hypothesis

H_rescues: acc_50hop ≥ 0.70 — backward evidence was the missing ingredient; loopy dynamics work given right starting point.

H_insufficient: acc_50hop < 0.30 — Resonator's loopy dynamics fail regardless of evidence availability.

## Pre-declared verdicts

- `WARMSTART_RESCUES` — acc_50hop ≥ 0.70.
- `WARMSTART_PARTIAL` — 0.30 ≤ acc < 0.70.
- `WARMSTART_INSUFFICIENT` — acc < 0.30.
- `WARMSTART_INCONCLUSIVE` — metric collection error.

## Method

Per chain at d=50:
1. Run VAMP forward-backward to compute per-hop smoothed log-posteriors smoothed[t].
2. For each hop:
   - Initialize Resonator state from x_hat = Σ exp(smoothed[t+1])·entity_atoms (warm-start from backward-informed prior).
   - Run T_inner=20 resonator iterations with τ-annealing.
   - For commit: use scores = entity_atoms @ probe + smoothed[t+1] (combine measurement + prior).
3. Compare final to target.

20 trials × 2 seeds.

## Acceptance thresholds

- 0.70 RESCUES = "clearly above argmax (0.22) and approaching VAMP (1.0)".

## Config

- N=8192 smoke, 65536 full.
- depth=50 full, T_inner=20.
- 20 trials × 2 seeds full.

## Pre-declared interpretation

- **RESCUES**: Resonator failed because of missing cross-hop info, not loopy dynamics per se. Implication: backward-informed iteration can work; but VAMP single-pass already achieves PERFECT so this is theoretical not practical.
- **PARTIAL**: backward evidence helps Resonator but loopy dynamics still degrade. Hybrid approach plausible.
- **INSUFFICIENT**: Resonator's loopy dynamics fail independently. Ihler 2005 loopy-BP-cycle failure confirmed on substrate.

## Not in scope

- T_inner sweep.
- Tau-anneal variants.
- Comparison vs pure VAMP-on-chain (already PERFECT — would only show parity).
