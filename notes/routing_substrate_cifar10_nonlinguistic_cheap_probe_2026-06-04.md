# Routing -- Substrate cheap probe on CIFAR-10 (non-linguistic empirical test)

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical cheap probe (1 cell; CPU)
**Source:** User question on "is knowledge mostly non-language; can substrate de-linguistify?" 2026-06-04

---

## Capability question

Can substrate's VSA primitives (binding + bundling + symmetric Hebbian outer-product write) learn a non-linguistic classification task (CIFAR-10 image patch-level) at substrate dimension N=4096? Tests whether substrate's modality-agnostic primitives ACTUALLY transfer to vision data beyond paper-only algebraic claims.

This is the cheapest empirical probe of the "substrate handles non-linguistic data" hypothesis. ALL existing substrate empirical work has been on language tasks (char-LM bigram/trigram). Vision is genuinely untested.

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_cifar10_vsa_binding_v1_n4096`

**Architecture:**
- Image -> 4x4 patches (CIFAR-10 = 32x32 -> 64 patches)
- Each patch flattened to 48-dim vector (4*4*3 RGB)
- Random projection to bipolar 256-dim
- Position-binding: bind(patch_bipolar, position_key) for each patch
- Sum across patches: image_vec = sum_k bind(patch_k, p_k)
- Substrate stores: W += image_vec * label_one_hot^T (Hebbian outer-product write)
- Inference: predicted_label = argmax(W @ query_image_vec)

**Cells:**
- N values: {1024, 4096} (2 N) -- tests N-scaling
- Train size: 10000 CIFAR-10 images
- Test size: 2000 CIFAR-10 images
- Seeds: 3

**HARD-PASS:** test accuracy > 25% at N=4096 (vs 10% chance baseline; 2.5x chance) AND 3/3 seeds. Confirms substrate's VSA primitives transfer to vision empirically.

**MIDDLE:** test accuracy in [13%, 25%] (some signal but weak)

**HARD-FAIL:** test accuracy <= 13% (~chance + noise). Confirms substrate's vision capacity is too weak to provide a non-linguistic learning signal at substrate-class N.

## Resource

Local CPU. CIFAR-10 + simple substrate matmul is matmul-light.

## Cost ceiling

$0 CPU. Per-seed wall ~5-10 min. Total ~30-60 min for 6 measurements.

## P_deflated

Decomposed per today's methodology:

P_algebraic = 0.65 (VSA primitives are modality-agnostic by construction; HDC vision lit precedent at small scale exists)

P_implementation = P_convergence * P_budget * P_no_subsumption * P_task_match
- P_convergence: 0.70 (Hebbian co-occurrence converges quickly on bounded vocabulary)
- P_budget: 0.85 (N=4096 fits CIFAR-10 patch capacity)
- P_no_subsumption: 0.90 (no NESS subsumption; W-modifying)
- P_task_match: 0.60 (CIFAR-10 is at the lower edge of substrate's task complexity; would benefit from larger N)

P_joint = 0.65 * 0.32 ~ **0.21** for HP at >25% accuracy.

This is a CHEAP empirical falsification test. Even MIDDLE is informative (some signal at substrate-class scale).

## Engineering scope

~2-3h. New scaffold needed for:
- CIFAR-10 data loader
- Patch extraction + bipolar projection
- VSA position-binding
- Substrate Hebbian write + inference

Reuses existing substrate primitive code.

## Strategic outcome

### If HP (>25% accuracy)

- Substrate's VSA primitives EMPIRICALLY validated on non-linguistic data
- Opens substrate as multi-modal knowledge representation candidate
- Multi-modal substrate drill cascade gets empirical anchor
- Major cap_map update: substrate not language-only

### If MIDDLE (13-25%)

- Substrate works at some level on vision; needs adaptation
- Inform multi-modal substrate drill: which adaptation primitives needed
- Next-step: test at larger N (16384+); test with learned (not random) projection

### If HF (<=13%)

- Substrate's bipolar quantization + symmetric Hebbian capacity is too constrained for natural-image patches
- Modality-specific encoders may be required (e.g., learned codebook before binding)
- DOES NOT KILL substrate-multi-modal idea; identifies the BARRIER

---

## What this is (plain language)

CIFAR-10 is the simplest non-linguistic benchmark. 32x32 RGB images; 10 classes (airplane, car, cat, dog, etc.). Trivial for CNN-class architectures (modern ResNet ~95%+ accuracy).

Question: can substrate's VSA primitives + Hebbian outer-product write even learn ABOVE CHANCE on CIFAR-10?

- Above-chance result (>10%): substrate has some non-linguistic learning capability; vision transfer is genuine
- At-chance (~10%): substrate cannot extract image features at this configuration; non-linguistic capability requires adaptation

This isn't a competitive benchmark vs CNN. It's a SANITY CHECK: do substrate's modality-agnostic claims survive contact with real non-linguistic data?

CIFAR-10 chosen because:
- Tiny (60K images; 32x32 small)
- Simple (10 classes; standard benchmark)
- Free
- 30-60 min wall on CPU
- Well-characterized chance baseline

---

## Strategic context

If HP: substrate's product narrative expands from "audit primitives for LLM augmentation" to "audit primitives for ANY knowledge representation, including non-linguistic." Bigger product surface.

If HF: confirms substrate's algebraic primitives need modality-specific adaptation. Doesn't kill the multi-modal direction but identifies an empirical barrier.

Either outcome is INFORMATIVE about substrate's true scope.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: cheapest informative probe of "substrate handles non-language"
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU only
- Per [[feedback-small-scale-first-methodology]]: rung-1 sanity check before any multi-modal scale-up
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** small ~30-60 min CPU probe; ~2-3h engineering for new CIFAR-10 + VSA-binding scaffold. Verdict drives substrate-multi-modal feasibility assessment. Bundles trivially with other CPU work if dispatched together.

**Research session:** holds for verdict; 3 multi-modal research drills running in parallel (multi-modal primitives + de-linguistification + unified representation); empirical CIFAR-10 anchors theoretical findings.
