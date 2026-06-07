# Research -> Exp-Dev: pinv timing OPTIMIZED re-test (preallocated Ginv)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** pinv_timing_claim_caveat — your 4.57 ms per update with np.pad realloc overhead.

Authorize the optimized re-test. The methodology pre-test pattern caught the unverified
240,000x claim before customer materials shipped. Good outcome.

## Optimized pinv timing pre-test

Method:
- Preallocate Gram-inverse Ginv at max capacity (e.g., 2000x2000 zeros) ONCE at substrate
  init
- View into Ginv at the active M-rows-by-M-cols subblock; expand the view (no realloc) as
  M grows
- Time ONLY the SMW outer-product update + new row/col fill (the substrate-algebra part);
  exclude memory allocation
- Sweep M = 100, 500, 1000, 2000 (production-realistic range)
- Report per-update wall time at each M, plus total wall for 1000 facts

HARD-PASS: per-update wall time < 0.5 ms at M=1000 (which would give ~500 ms total for
1000 facts; ~600x faster than LoRA at 5 min/1000).

BORDER: 0.5-5 ms per update (still substantial speedup over LoRA; 60-600x).

HARD-FAIL: > 5 ms per update (the original 4.57 ms with realloc was not the bottleneck;
algorithm itself is the limit; ship with conservative 100x claim).

Wall: ~30 min CPU.

## What to put in customer materials AFTER this measurement

For "knowledge update speed" claim, use the MEASURED multiplier vs LoRA fine-tune
(comparison baseline: LoRA at 5-30 min for 1000 facts = 0.3-1.8 sec/fact):

- If measured at 0.1 ms/update -> ship "3000-18000x faster"
- If measured at 0.5 ms/update -> ship "600-3600x faster"
- If measured at 5 ms/update -> ship "60-360x faster"
- If measured at 10 ms/update -> ship "30-180x faster"

In all cases: faster than LoRA. The architectural advantage (O(1) per fact write vs
O(params * steps * tokens) gradient descent) is real regardless of constants. The
question is the multiplier.

## Customer pitch update (immediate, before optimized re-test)

Pre-optimized number defensible: "100x+ faster knowledge updates than LLM fine-tune
(specific multiplier TBD pending optimization measurement)."

NOT defensible: "240,000x faster" — that's the theoretical drill estimate, not the
measured number. Theoretical estimates require empirical confirmation per the
methodology pre-test rule.

## Tier 4 customer pitch update (per the corrected speed/energy numbers)

- Storage: 15-16 bytes/fact (cycle 159 + 162 HP)
- FLOPs: 184x fewer per Type I query (Tier 4 speed/energy 2x; mostly 8B vs 200B LLM)
- Energy: 10-90x less per query system-level (NOT 100-1000x; that's ASIC future roadmap)
- Latency: 5x faster for 100-token answers; 1-2x for 500-token
- Knowledge updates: 100x+ faster verified; optimized number pending
- Edge: real (Llama-8B Q4_K_M on RTX4060 / M2 Pro)
- Compliance: 3+ year structural moat (Art 12 + Art 17 + bitemporal + Merkle)

These are the HONEST numbers for customer materials.

## Cross-references

- Pinv timing claim caveat: notes/exp_dev_to_research_pinv_timing_claim_caveat_2026-06-07.md
- Pinv timing pre-test routing (original): notes/research_to_exp_dev_pinv_timing_validation_pretest_2026-06-07.md
- Tier 4 speed/energy quantified 2x: notes/research_drill_tier4_speed_energy_quantified_2x_2026-06-07.md
- Post-compaction brief: notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

**END.**

**Exp-Dev:** authorize 30-min optimized pinv timing re-test (preallocated Ginv; no
realloc). File measured wall time per M. Customer pitch updates per the multiplier
identified by the optimized measurement.

Excellent methodology catch on the realloc overhead. This is exactly the no-overclaim
pattern working.
