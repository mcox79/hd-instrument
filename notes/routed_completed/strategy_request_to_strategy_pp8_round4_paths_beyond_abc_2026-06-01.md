# Strategy request: PP-8 Round 4 paths beyond A/B/C (3-drill consolidated routing)

**From**: research
**To**: strategy
**Date**: 2026-06-01
**Source**: `notes/research_pp8_round4_3_drills_synthesis_2026-06-01.md`
**Trigger**: User asked for 2x-deep research on other paths uniquely beneficial vs orchestrator's A/B/C; CPU+GPU queues empty per status update

## TL;DR

3 ADDITIONAL paths uniquely beneficial vs A/B/C identified. Combined Tier-1 cost ~$25-30 Lambda + ~3-4 eng-days. Each answers a qualitatively different question than A/B/C:

1. **D1 mechanism decoupling**: is Phi-3 necessary at all? Frozen-random control ($0.50-1; PIVOT) tests M1 vs M2 dominance.

2. **D2 layer × precision isolation**: is the 98%→35% oscillation architectural (mean-bias) or HP (Option B)? Layer probe + bf16 vs 4-bit ($12-15) resolves before committing to Option B LR-tweak.

3. **D3 production-deployment paths**: does Path 1a extend to KV-cache integration, streaming, multi-LLM, LLM-initiated writes? Path A KV-cache smoke ($10-15) is highest-P production extension.

## TIER 1 DISPATCH RECOMMENDATIONS (cheap diagnostics; cumulative ~$25-30)

| # | Test | Cost | Question | Decision |
|---|---|---|---|---|
| **T1.1** | **D1-1 frozen-random hidden-state control** | **$0.50-1 CPU; <30min** | Is Phi-3 necessary? | If val_random ≈ 38% → M1-dominant → architecture simplifies (any embedding + random projection works; no Phi-3 dependency) |
| **T1.2** | **D2-1 + D2-2 layer × precision** | **$12-15 H100** | Architecture or HP origin of oscillation? | Architectural fix preferred to HP (reproducible, transfers across HP configs) |
| **T1.3** | **D3-Path-A KV-cache integration smoke** | **$10-15 Lambda + 3-4 eng-days** | Does Path 1a extend to audit-grade tool-call cache? | First production-extension validation; GDPR Art 17 deletion-cert differentiator |

**Pre-reg per item**:
- **T1.1 HARD-PASS** (M1 dominant): val_random ≥ 30% (within 8pp of v1's 38.2%)
- **T1.1 HARD-FAIL** (M2 load-bearing): val_random < 15% (delta from v1 > 23pp)
- **T1.1 MIDDLE-BAND**: val_random 15-30%

- **T1.2 HARD-PASS** (architectural fix viable): bf16 OR layer 16 reduces post-peak oscillation std dev ≥ 30% relative to v1
- **T1.2 HARD-FAIL** (HP-fragile, Option B needed): bf16 AND layer 16 oscillate equally to v1
- **T1.2 MIDDLE-BAND**: partial reduction (10-30%)

- **T1.3 HARD-PASS** (KV-cache viable): hit rate ≥ 60% on paraphrase set; false-positive rate < 2%; cert chain generation + deletion receipt latency within production budget
- **T1.3 HARD-FAIL**: false-positive rate > 5% (semantic hash collision rate too high)

## INTEGRATION WITH ORCHESTRATOR'S A/B/C SEQUENCING

These 3 paths are ORTHOGONAL to A/B/C, not replacements:
- A/B/C validate the EXISTING architecture (generalization / HP / multi-hop)
- D1/D2/D3 test alternative architectures + production extensions
- Combined dispatch: A + T1.1 first (both cheap; ~$1-2 combined). Resolution of both determines remaining sequencing.

**Decision tree post A+T1.1**:
- T1.1 M1-dominant + A held-out PASS: architecture simplifies AND generalizes. Skip Phi-3-specific D2; focus on production extensions (T1.3 + D3-Path-D/B)
- T1.1 M2 load-bearing + A held-out PASS: full architecture validated. Dispatch T1.2 (architecture vs HP) + T1.3 (KV-cache extension)
- T1.1 M2 load-bearing + A held-out FAIL: M2 generalization narrower than predicted; dispatch D1-2 layer ablation + D1-3 embedding-layer to characterize what M2 is doing
- T1.1 M1-dominant + A held-out FAIL: architecture works only on overlapping distributions; pivot to Alt B (trainable projection + ortho-reg from original deliverable)

## TIER 2 / TIER 3 (conditional)

- **D1-2 layer ablation** ($3-6) — if T1.1 M2 load-bearing AND A passes; characterizes M2 depth-dependence
- **D1-3 embedding-layer control** ($1-2) — if T1.1 confirms M2; tests 30-50× inference cost reduction potential
- **D1-4 cross-LLM portability** ($4-8) — if T1.3 path-A PASS; tests M2 portability for multi-LLM strategy
- **D3-Path-B streaming** ($15-20) — if T1.3 path-A PASS; tests production scope
- **D3-Path-D LLM-initiated writes** ($12-18) — if T1.3 path-A PASS; highest strategic leverage if works (active knowledge substrate)
- **D3-Path-C multi-LLM joint calibration** ($20-25) — last; cross-architecture projection collapses across reasoning domains; bonus capability not required for first product

## CAP_MAP IMPLICATIONS

PP-8 row (currently 🔬 0.30-0.45):
- T1.1 + A both PASS → 🟡 0.50-0.65 (validated architecture + simplification optional)
- T1.1 + A + T1.2 PASS → 🟡 0.55-0.70 (validated + architecturally stable)
- T1.1 + A + T1.2 + T1.3 PASS → 🟢 0.60-0.78 (production-extension validated)
- Additional 4 conditional smokes all PASS → ✅ 0.70-0.88

PP-31 calibrated-confidence-temperature-scaling row (just-promoted v316): already validated; intersects with T1.2 D2-4 pooling variant if temperature scaling generalizes.

NEW row candidate: "Audit-grade tool-call result cache (substrate as semantic KV-cache)" if T1.3 PASS — would be cap_map row at 🔬 0.50-0.65, with GDPR Art 17 deletion-cert differentiator as the wedge.

## FRAMEWORK-REFUTATION-AWARE CALIBRATION

Today's v316 swept TWO mean-field framework refutations:
- Percolation N-independence at v312 (my morning 2x-drill predicted depth-composition cliff which empirically validated)
- Free-probability framework at finite-N (3 axes today)

**Implication**: substrate's finite-N regime is unmapped; mean-field equilibrium-class frameworks consistently fail. Substrate sits in non-equilibrium stat-mech territory per [[project-substrate-non-eq-stat-mech-class-2026-05-27]].

For Round 4 calibration: P estimates above include 0.15-0.25 deflation per [[feedback-lit-scan-calibration-penalty]]. Consider ADDITIONAL 0.05-0.10 deflation on production paths (Drill 3) since they assume Path 1a's algebraic structure behaves as design-review predicted (itself uncharted-regime claim).

## CONTRACT FOR STRATEGY

1. **Dispatch T1.1 frozen-random control immediately?** $0.50-1; <30min; PIVOT — highest info-gain per dollar of any test surfaced today
2. **Authorize T1.2 layer × precision in parallel with T1.1?** $12-15; resolves architecture vs HP before Option B commit
3. **Authorize T1.3 KV-cache integration smoke?** $10-15 + 3-4 eng-days; tests first production-extension path
4. **Conditional dispatch tree per decision-tree section above?**
5. **NEW cap_map row for audit-grade tool-call cache?** Pending T1.3

## METHOD NOTES

- Per [[feedback-no-preframe-batch-all-pass]] (saved today): explicit HARD-PASS / MIDDLE-BAND / HARD-FAIL bands per design; no batch-level expectation
- Per [[feedback-2x-means-depth]]: research went DEEPER on existing Path 1a findings; orthogonal to A/B/C validation paths
- Per [[feedback-lit-scan-calibration-penalty]] + today's framework-refutation pattern: P estimates aggressively deflated
- Per [[feedback-no-experiment-design-in-prompts]]: routing hands TASK + WHY + CONTRACT + AUTONOMY; sweep grids and exact thresholds remain exp_dev's call

## CLOSING

Move to `routed_completed/` when strategy decides Tier 1 dispatch (T1.1 + T1.2 + T1.3) and conditional Tier 2/3 sequencing based on outcomes.

---

**ROUTING STATUS**: Acted-on 2026-06-01: Tier 1 D1-1 + Option A AUTHORIZED in parallel via testbed routing; D2+T1.3 pre-authorized conditional on D1-1+A outcomes per research decision tree
