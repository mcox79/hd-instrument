# Pre-registration: name-augmented encoding recovery (constructive validation of the encoding-discriminability fix)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_name_augmented_encoding_recovery_gpu_v1.py
**Routing:** follow-on to near-duplicate diagnostic (encoding-discriminability fix). Substrate-quality-first; NO LLM frame.
**Lane:** overnight_queue (GPU).

## Purpose
Constructively test the recommended fix using data ALREADY PRESENT (atom id/name tokens; no bge, no content authoring):
augment the algebra-HRR codebook aug = normalize(algebra_hrr + alpha * name_vec) where name_vec = HRR bundle of hashed
name+id tokens, and re-measure composition/decode cleanup capacity vs the plain algebra_hrr codebook (which collides ~32
atoms at cos=1.0). If augmentation separates the collisions, cleanup recovers toward the uniform-codebook 1.0.

## Design
Sweep alpha in {0,0.5,1.0,2.0} (alpha=0 reproduces the deficit); cleanup@1 at F in {1,3,10}; 3 seeds x 20 trials. Canonical
hdlab bind/bundle/unbind; unitary roles.

## Pre-registered verdict bands (decode metric = cleanup@1)
- **HARD-PASS:** name-augmented cleanup@1 at F=3 >= 0.97 at some alpha (existing name field recovers decode near-uniform).
- **MIDDLE:** best augmented F3 cleanup 0.92-0.97 (partial; name tokens break most collisions, residual needs authored fields).
- **HARD-FAIL:** < 0.92 (name insufficient; needs authored signature/complexity semantic fields).
- **UNKNOWN:** corpus load fails.

## Substrate-product artifact (stands alone, no LLM frame)
Demonstrates whether the substrate's composition/decode ceiling is fixable TODAY by folding the existing name field into the
algebra-HRR encoding -- de-risking the encoding-discriminability change before Testbed invests, and quantifying the alpha that
recovers decode without destroying categorical structure.
