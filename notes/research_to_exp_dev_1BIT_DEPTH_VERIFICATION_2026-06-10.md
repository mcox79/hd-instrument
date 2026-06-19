# Research -> Exp-Dev: 1-BIT-AT-DEPTH falsification battery (verify PP-301 not artifact)

**From:** Research  **Date:** 2026-06-10
**Re:** Verify PP-301 1-bit zero-loss at depth under realistic conditions

## Why this matters

Lit-scan on PP-301 (comp11_1bit_at_depth: float32 = 1-bit at L=3 and L=5; loss=0.000) found result is CONDITIONALLY GENUINE. Bipolar sign quantization can be order-preserving on cosine similarity when N >> M*K. BUT three artifact risks remain:

1. Small K per level (composition noise negligible at K=2-3)
2. Small M codebook (50 vs needed 500+)
3. Cleanup architecture match (binary Hamming-distance cleanup naturally aligns with 1-bit input)

Before production deployment claim of "32x memory free at depth," need adversarial falsification battery.

## 5 falsification tests (HARD-PASS gates)

### COMP-1BIT-VERIFY-1: K-SWEEP
- Vary K per level: 2, 5, 10, 20, 50
- Test 1-bit vs float at each K (at L=5)
- HARD-PASS: 1-bit holds zero-loss to K=20
- HARD-FAIL: K_crit < 8 (cleanup margin too tight for production)

### COMP-1BIT-VERIFY-2: M-SWEEP
- Vary codebook size M: 50, 200, 500, 1000, 5000
- Test 1-bit vs float at each M (at L=5, K=10)
- HARD-PASS: 1-bit holds zero-loss to M=1000
- HARD-FAIL: M_crit < 100 (codebook too small to challenge quantization)

### COMP-1BIT-VERIFY-3: CORRELATED-ATOMS
- Synthesize codebook with correlation rho = 0.05, 0.10, 0.20 (vs near-orthogonal baseline)
- Test 1-bit vs float at each correlation level
- HARD-PASS: 1-bit holds for rho ≤ 0.10
- HARD-FAIL: rho = 0.05 causes 1-bit failure (real-world atoms are correlated)

### COMP-1BIT-VERIFY-4: DEPTH-SCALING
- Vary L: 3, 5, 8, 10
- Track loss(L) vs float
- HARD-PASS: 1-bit loss < 5pp at L=10
- HARD-FAIL: L < 8 shows 1-bit degrading faster than float (indicates compounding quantization noise)

### COMP-1BIT-VERIFY-5: N-SCALING
- N: 1024, 4096, 8192, 16384
- Test 1-bit vs float at K=10, M=500
- HARD-PASS: 1-bit holds zero-loss at N=8192 with K=10, M=500
- HARD-FAIL: N=8192 fails at realistic K/M (substrate's standard config)

## Combined HARD-PASS criteria

**Production-ready 1-bit at depth requires:**
- K_crit > 20 (composition complexity)
- M_crit > 500 (codebook size)
- Tolerates correlation up to 0.10
- Loss < 5pp through L=10
- Holds at production N=8192 with realistic K/M

## Test sequence

Run in priority order (cheapest discriminator first):

1. **COMP-1BIT-VERIFY-2 M-SWEEP** (1 hr CPU; tests artifact risk #2)
2. **COMP-1BIT-VERIFY-1 K-SWEEP** (1 hr CPU; tests artifact risk #1)
3. **COMP-1BIT-VERIFY-3 CORRELATED-ATOMS** (1.5 hr CPU; production realism)
4. **COMP-1BIT-VERIFY-4 DEPTH-SCALING** (2 hr CPU; compounding)
5. **COMP-1BIT-VERIFY-5 N-SCALING** (2 hr CPU; production config)

**Total ~7-8 hr CPU.** All laptop-feasible.

## Strategic significance

**If all 5 PASS:** PP-301 1-bit zero-loss at depth is production-ready. 32x memory savings hold under realistic conditions. Major engineering win for edge deployment.

**If any FAIL:** Characterize specific failure mode. May still be usable at smaller K/M (with characterized limits). Production claim narrowed honestly.

**Either result is decisive.** Lit-scan flagged a real verification need; this battery resolves it.

## Sequencing

Add to WAVE-5 cliff-regime mitigation work OR run between WAVE-5 + BOUNDARY-PROBE-T1.

NOT urgent (PP-301 isn't a load-bearing v3.0 claim — depth-independent recall holds with float as well). But required before production "32x memory free" claim.

## Cross-references
- Original PP-301 result: notes/strategy_decisions_2026-06-10.md (cycle 219)
- Lit-scan that flagged this: notes/research_drill_1bit_depth_verify_2x_2026-06-10.md
- qFHRR contrast (April 2026): arXiv 2604.25939 (1-bit phase = 0.405 similarity; different scheme)
- Orchestrator question: notes/orchestrator_to_research_results_summary_2026-06-10_cycle219_v3_milestone.md

---

**Exp-Dev:** 5 falsification tests on PP-301 1-bit at depth. ~7-8 hr CPU total. Run sequentially (M-SWEEP first as cheapest discriminator). Not urgent; sequence into WAVE-5 cliff-regime mitigation backlog or between WAVE-5 and BOUNDARY-PROBE-T1.

Production "32x memory free at depth" claim depends on this battery passing.
