# Pre-registration: algebra-HRR codebook near-duplicate diagnostic (CSLS follow-on)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1.py
**Routing:** follow-on to CSLS HARD_FAIL (deficit = genuine near-duplicates). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (CPU).

## Purpose
Turn the "fix is finer encoding / de-duplication" recommendation into an actionable spec: quantify the near-duplicate
structure of the 280-atom algebra_hrr codebook, identify WHICH atoms collide, the F=1 cleanup floor (irreducible near-dup
confusion), and whether de-duplication recovers cleanup toward the uniform-codebook 1.0.

## Pre-registered bands (de-dup@cos>0.95 F=3 cleanup lift)
- **HARD-PASS:** de-dup lifts F=3 cleanup >= +0.05 (mergeable duplicates are a real chunk of the deficit; de-dup is a mitigation).
- **MIDDLE:** lift +0.01-0.05 (some duplicates; most deficit is distinct-but-close atoms needing finer encoding).
- **HARD-FAIL:** lift < +0.01 (not mergeable duplicates; finer ENCODING needed, not merging).
- **UNKNOWN:** corpus load fails.
Reports: near-dup pair counts at cos {0.90,0.95,0.99}, atoms-with-near-twin counts, top colliding pairs (atom ids), F=1 floor,
de-dup K reduction, cleanup recovery. Structural counts/pairs are exact (Gram matrix); cleanup numbers are 3 seeds x 30 trials.

## Substrate-product artifact (stands alone, no LLM frame)
A concrete, actionable map of which substrate atoms the algebra-HRR encoding fails to distinguish (cos~1.0 collisions of
distinct concepts, e.g. role atoms sharing an algebra_category with 0-populated signature/complexity), and how much of the
composition/decode cleanup deficit is recoverable by de-duplication vs requires finer encoding.
