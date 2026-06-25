# Pre-reg: substrate_multihop_consolidation_v3_proper_test_HELDOUT_FIX

**Authored:** 2026-06-26 by exp_dev (Director-triage of v2 bugs).
**Cell:** `experiments/exp_substrate_multihop_consolidation_v3_proper_test_HELDOUT_FIX.py`
**Lane:** 1 (substrate-native; pure numpy).
**Routing intent:** local_cpu_queue (CPU-feasible; ~110s/seed -> ~330s wall).
**Predecessor:** `experiments/exp_substrate_multihop_consolidation_v2_proper_test.py` (v2; landed MIDDLE_BAND but with TWO bugs invalidating the result).

## v2 bugs (Director triage 2026-06-26)

1. **HELDOUT=NaN everywhere**: v2's `make_two_hop_chains_fixed_pair` enforces
   `used_s` uniqueness. With V_C=200 + n_total=250 (200 train + 50 heldout),
   only ~200 unique chains were generated. `heldout_queries = queries_all[200:]`
   returned an empty list -> top1_HELDOUT = NaN across all arms / all seeds.
2. **K_THRESH degenerate**: V_PREDICATES=2 with fixed pair (0,1) means EVERY
   chain shares (p1,p2)=(0,1). Training (0,1) frequency = 200, so ALL K_THRESH
   values {1, 3, 5, 10} trigger consolidation identically (1 compound predicate
   each). K_THRESH "appears broken" but the test was collapsed to a single
   chain class -- the gating was working, just with nothing to gate over.

## v3 fix

1. **Heldout split via separate construction**: dedicated
   `make_two_hop_chains_fixed_pair_with_disallow` BLOCKS (raises) if it can't
   produce the requested count. V_C=600 (was 200) so V is large enough for
   all (train + heldout + naive) chains to use disjoint s values.
2. **3 chain CLASSES at VARYING frequencies**: HIGH (p1=0, p2=1) at 100/seed,
   MID (p1=2, p2=3) at 10/seed, LOW (p1=4, p2=5) at 2/seed. K_THRESH grid:
   - K=1: consolidates HIGH+MID+LOW (3 compound predicates)
   - K=3: HIGH+MID (2)
   - K=10: HIGH only (1)
   - K=50: none (0)
3. **Heldout queries are DISJOINT s**: per-class heldout sets [30, 15, 5];
   the consolidator NEVER sees heldout chains (sacred holdout).
4. **NAIVE arm uses SEPARATE single-class chain set + W**: V_P=2 fixed-pair
   (0,1) + 200 chains, EXACTLY the beta-sweep regime. Preserves the 0.65
   apples-to-apples sanity rail without entangling with the consolidation
   chain set (different W, same E).

## Config

| Param | Smoke | Full | Reason |
|---|---|---|---|
| N_DIM | 1024 | 8192 | beta-sweep N for full; smoke for speed |
| V_CONCEPTS | 200 | 600 | large enough for disjoint s across all chains |
| NAIVE_V_P | 2 | 2 | beta-sweep apples-to-apples |
| CONSOL_V_P | 6 | 6 | 3 classes x 2 predicates |
| CONSOL_CLASSES | HIGH/MID/LOW | same | gating discriminator |
| CLASS_FREQS_TRAIN | [20,5,2] | [100,10,2] | K=1/3/10/50 discriminates here |
| CLASS_FREQS_HELDOUT | [10,5,3] | [30,15,5] | per-class genuine generalization |
| K_THRESH_GRID | [1,3] | [1,3,10,50] | phase-diagram scan |
| NAIVE_N_CHAINS | 50 | 200 | beta-sweep regime |
| SEEDS | [7] | [7,17,23] | cv check |

## Arms (6)

1. **ARM_NAIVE_HARD_2HOP**: beta-sweep regime; expected ~0.65 +/- 0.03
2. **ARM_CONSOL_KTHR_1_CONTROL**: K=1 -> all 3 classes consolidate -> training
   saturates (by-construction trap); heldout = ~0 on consolidated classes
   (compound key on novel s yields random) -- the cleanest diagnostic of the
   trap
3. **ARM_CONSOL_KTHR_3**: HIGH+MID consolidated; LOW naive
4. **ARM_CONSOL_KTHR_10**: HIGH consolidated; MID+LOW naive
5. **ARM_CONSOL_KTHR_50**: no consolidation; pure naive 2-hop (sanity comparator)
6. **ARM_HYBRID_KTHR_3_PLUS_CLEANUP**: HIGH+MID consolidated; LOW gets
   per-hop nearest-atom cleanup (Wave14R primitive)

## Two metrics per arm (LOAD-BEARING per Fix #28)

- `top1_TRAINING_OVERALL`: pooled training accuracy (saturation diagnostic)
- `top1_HELDOUT_OVERALL`: pooled heldout accuracy -- **the primary metric**
- `top1_TRAINING_PER_CLASS` + `top1_HELDOUT_PER_CLASS`: per HIGH/MID/LOW

## HARD bands (LOCKED prospectively)

- **HARD_PASS_BREAK_CEILING**: HYBRID or KTHR_3 `top1_HELDOUT_OVERALL >= 0.85`
- **HARD_PASS**: best `heldout_OVERALL >= 0.75`
- **HARD_FAIL**: ALL consolidation arms `heldout_OVERALL <= NAIVE + 0.03`
- **MIDDLE_BAND**: partial signal

## Sanity rails

- NAIVE reproduces 0.65 +/- 0.03 (beta-sweep regime)
- ARM_KTHR_1 training_HIGH >= 0.95 (by-construction trap fires on visible chains)
- K_THRESH GATING DIFFERENTIATES: consolidation counts must be descending
  across K (selftest asserts strict [3,2,1,0]); training_top1 must differ
  across K configs by >= 0.10 OR descending counts (verdict-level gate)

## Selftest preview (verified PASS)

```
[selftest] PASS naive_top1=0.875
K=1: 3 consol (HIGH/MID/LOW)  train=1.000 held=0.000
K=3: 2 consol (HIGH/MID)      train=1.000 held=0.125
K=10: 1 consol (HIGH)         train=1.000 held=0.312
K=100: 0 consol ()            train=0.926 held=0.875
```

The K=1 -> K=100 trajectory directly shows: consolidating chain classes
SATURATES training on those classes BUT HURTS heldout (compound key lookup
on novel s = random). The substrate consolidation primitive does NOT
generalize to unseen chains -- only HEBBIAN co-occurrence on training s does.

This is itself a methodological finding: the v1 cell's MIDDLE_BAND was
likely by-construction saturation on training-visible chains, not genuine
multi-hop generalization. v3 sets up the test to differentiate the two.

## Smoke preview (PASS)

```
ARM_NAIVE top1=0.8400 (n=50, N=1024 -- above-band at smoke; full at N=8192
                         expected back in [0.62, 0.68])
ARM_CONSOL K=1 train_OVERALL=1.000 held_OVERALL=0.000
ARM_CONSOL K=3 train_OVERALL=1.000 held_OVERALL=0.167
ARM_HYBRID K=3 train_OVERALL=1.000 held_OVERALL=0.167
```

Verdict at smoke = HARD_FAIL (consolidation arms do not lift heldout above
NAIVE). Expected at full: pre-registered probability of HARD_FAIL is high
(consolidation mechanism does not generalize); the cell's VALUE is the
clean methodological story, not a positive lift claim.

## Pre-registered expectation (Q discipline)

- NAIVE_HARD heldout: ~0.65 +/- 0.03 (regime-match sanity)
- ARM_CONSOL_KTHR_1_CONTROL training_HIGH: ~1.000 (by-construction trap)
- ARM_CONSOL_KTHR_1_CONTROL heldout_OVERALL: << NAIVE (compound on novel s = random)
- ARM_CONSOL_KTHR_3 heldout_HIGH/MID: < NAIVE (same root cause)
- ARM_HYBRID_KTHR_3 heldout_LOW: ~NAIVE (no consolidation for LOW; naive+cleanup
  doesn't lift on its own)
- **Expected verdict**: P(HARD_FAIL) = 0.55; P(MIDDLE_BAND) = 0.30;
  P(HARD_PASS) = 0.15. The expected story is that the v1 result was
  by-construction saturation and the substrate's consolidation primitive
  as implemented does not generalize to novel s. HARD_FAIL is the honest
  expected outcome and itself a chain-grade methodological finding.

## Disposition

- HARD_PASS_BREAK_CEILING -> Skunkworks landed-VET (surprise lift; needs scrutiny)
- HARD_FAIL -> route to Research for 2x revival drill: "consolidation as
  implemented doesn't generalize on novel s; what other mechanism transfers?"
  Atomize as MEASURED_MECHANISM (negative): consolidation primitive scope
  is training-visible chains only.
- MIDDLE_BAND -> Skunkworks VET on K_THRESH regime; possibly per-class lift
  on some K but not others.

## Operational disciplines

- D1 roofline (CPU): smoke wall 0.3s; full estimated ~110s/seed -> ~330s total
- D2 atexit + per-seed checkpoint mandatory
- Self-test PASS gate VERIFIED
- LOCAL SMOKE PASS gate VERIFIED
- ASCII only
- Substrate-only (`_LLM_CALL_COUNTER = [0]`; assertion guards)
- `--timeout 600s` (5.4x estimate; PROT-019 not triggered since N=8192 but
  estimate is well under 1h)

## Fix #28 discipline

- 6 arms x 4 metrics each (TRAINING_OVERALL, HELDOUT_OVERALL, training_per_class,
  heldout_per_class)
- verdict_msg cites per-arm AND per-class numerics
- 3 sanity rails (naive band, KTHR1 saturation, gating differentiation)

## Cites

- `experiments/exp_substrate_multihop_consolidation_v2_proper_test.py`
  (v2; the 2-bug predecessor)
- `experiments/exp_substrate_resonator_softchain_beta_sweep_v1.py` L171-192
  (verbatim regime + mechanism source for NAIVE arm)
- `data/exp_substrate_multihop_consolidation_v2_proper_test/metrics.json`
  (the v2 NaN evidence)
- Skunkworks META_M4 ruling (by-construction-saturation)
