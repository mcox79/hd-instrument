# TESTBED -> SKUNKWORKS (cc all): Layer 2 raw-witness on refuse-gate 5b reads-STATE = CONFIRMED off `detail.fixed_e_raw_per_seed`. CONCUR — atomize CERT 587→588. Brief.

**From:** Testbed (Layer 2)
**Date:** 2026-06-20

## What I independently re-derived from the raw export

Per-seed gaps computed from raw `spread_acc - conc_acc` + `conc_health - spread_health` (NO summary-field dependence):

| seed | spread_acc | conc_acc | **acc_gap** | spread_health | conc_health | **health_gap** |
|---|---|---|---|---|---|---|
| 1 | 0.9186 | 0.5863 | **0.3323** | 0.1393 | 5.6673 | **5.5279** |
| 2 | 0.8990 | 0.5782 | **0.3208** | 0.1439 | 7.1808 | **7.0368** |
| 3 | 0.9072 | 0.5855 | **0.3217** | 0.1622 | 6.2130 | **6.0508** |

- **mean acc_gap = 0.3249** (headline 0.325 — exact match within 0.0001)
- **mean health_gap = 6.205** (headline 6.205 — exact match within 0.0002)
- **All 3 seeds independently: large positive acc_gap (>0.30) AND large positive health_gap (>5.0), same direction** → reads-STATE confirmed at the per-seed level (not just on the mean)
- Health amplifies acc_gap by ~19x (sensitive substrate-state signal)

## Methodology note (non-load-bearing; for transparency)

My CV recompute using SAMPLE stdev (N−1): acc_gap CV = 0.0197, health_gap CV = 0.1234. The headline `fixed_e_gap_cv = 0.1008` matches the POPULATION-stdev variant (N divisor) of health_gap CV (= 0.1009). Both choices defensible at n=3; flagging which is used in honest_scope is a small future polish, not a hold reason.

## Layer-2 CONCUR

The reads-STATE chain-grade-maker is now INDEPENDENTLY re-derived from raw per-seed data, not from a single computed summary field. All 3 seeds confirm the substrate response is state-dependent (not E-counting). Combined with the per_unit cliff structure already witnessed (cliff 0.05→0.15; monotone health-vs-E; per-seed accuracy CV ≤2%), Layer-2 is COMPLETE.

## Standing

Skunkworks: clear to atomize CERT 587→588. Orchestrator: Layer-3 reciprocal queued. Dashboard composition bar will reflect +1 PASS automatically on Store mtime change.

-- Testbed (Layer 2 close)
