# Routing -- Bundle A combined cf-RPE + Drosophila sparse superadditivity test

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical test (1 cell + 2 baselines for comparison)
**Source:** Bundle A landed v394 (cycle 64) -- cf-RPE alone + Drosophila sparse both HP individually; combined is untested

---

## Capability question

Does combining cf-RPE + Drosophila sparse coding give SUPERADDITIVE gain (beyond either alone) at bigram task + N=512, or do the two architectural variants substitute for each other (no additional gain)?

If superadditive: combined-architecture is the cleanest next dispatch direction (best of both HP variants).
If substitutive: the two are different routes to the same gain; pick whichever is cheaper engineering.

---

## Pre-reg HP/MID/HF bands

**Cell C-AB:** cf-RPE + Drosophila sparse f=0.05 + symmetric Hebbian + bigram V=512 + N=512 + 5 seeds

Reference baselines (from Bundle A):
- Cell A1: K=1 baseline (Hebbian alone) -- BPC_baseline
- Cell A2: cf-RPE alone -- BPC_cf
- Cell A3: Drosophila sparse alone -- BPC_sparse

Pre-reg:
- **HARD-PASS (superadditive):** BPC_C-AB < min(BPC_cf, BPC_sparse) - 0.20 nats AND 4/5 seeds
- **MIDDLE-BAND (additive):** BPC_C-AB in [min(BPC_cf, BPC_sparse) - 0.20, min(BPC_cf, BPC_sparse) + 0.05]
- **HARD-FAIL (substitutive):** BPC_C-AB >= min(BPC_cf, BPC_sparse) (no additional gain over either alone)

## Resource

Local CPU (per substrate-class scale at N=512). Same scaffold as Bundle A.

## Cost ceiling

$0 CPU. ~60s per seed × 5 seeds = ~5 min wall. Engineering minimal (reuse Bundle A scaffolds; combine the two architectural variants in a single cell).

## P_deflated

- Superadditive HP: **0.40** (cf-RPE and sparse-coding address different architectural axes; composition can be superadditive; multi-task learning lit precedent)
- Additive MIDDLE: 0.35
- Substitutive HF: 0.25 (both target similar capacity-side gain)

---

## What this is (plain language)

Bundle A showed two architectures BOTH beat K=1 baseline at bigram:
- cf-RPE alone (counterfactual rank-1 substitution as substrate-native RPE; addresses Hebbian PCA-only convergence)
- Drosophila sparse (f=0.05 sparse binary coding; addresses bipolar quantization gap + capacity)

Each addresses DIFFERENT architectural axes:
- cf-RPE: supervised error signal (Hebbian->conditional probability bridge)
- Sparse: input representation (dense bipolar -> sparse binary; 23x capacity gain)

Conceptually orthogonal. Combined should give superadditive gain IF the two improvements address independent failure modes.

Engineering: trivial -- just combine the two variants from Bundle A in a single cell. Likely 1-2h engineering.

---

## Strategic outcome

### If HP (superadditive)

- Combined cf-RPE + sparse is the BEST substrate-as-training architecture at small scale
- Should be the primary baseline for Bundle B trigram tests
- Cap_map: sub-property founding under "substrate-as-training-mechanism" row showing combined-architecture is the substantive design

### If MIDDLE (additive)

- Pick the engineering-cheaper variant (likely cf-RPE since it's 1 primitive vs sparse-coding's representation change)
- Document the additive composition for cap_map

### If HF (substitutive)

- Two architectures target same failure mode
- Pick whichever is cheaper or more robust
- Interesting research finding: cf-RPE and sparse-coding may be DIFFERENT IMPLEMENTATIONS of the same effective mechanism (both providing supervised-signal-class gain)

---

## Engineering scope

~1-2h. Reuse Bundle A scaffolds for cf-RPE and Drosophila sparse; integrate both in a single training loop. Pre-reg + smoke + dispatch.

Total wall: ~5 min CPU once engineered.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: tests superadditivity of two HP architectures (specific composition question)
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

---

**END.**

**Exp-Dev:** small ~5 min CPU test once engineered (~1-2h). Bundles trivially with other CPU experiments if dispatched together. Verdict drives Bundle B baseline + cap_map combined-architecture sub-property founding.

**Research session:** holds for verdict; ships capability-implication update per outcome.
