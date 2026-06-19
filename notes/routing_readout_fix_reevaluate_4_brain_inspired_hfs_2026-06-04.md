# ROUTING -- Re-evaluate 4 brain-inspired HFs with calibrated readout temperature

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical experiment / CPU readout-fix re-evaluation
**Status:** USER AUTHORIZED 2026-06-04 ($0 CPU; ~30-60 min per HF; 4 experiments total).

---

## Capability question

Are the 5 brain-inspired tiny-scale HARD_FAILs from cycle 43 (substrate-trained mini LM, curriculum learning, pre-loaded ICL, 8-channel orchestration, spectral training monitor) actually substrate failures, OR were they readout artifacts produced by softmax-over-cosine-scores at default temperature=1.0?

Exp-Dev de-confound 2026-06-04: at temperature=1.0, softmax over cosine scores is nearly flat (uniform-distribution-attractor), giving near-uniform BPC even when substrate retrieval works. At calibrated temperature=0.2, substrate trains: BPC 3.76 vs uniform 5.52 (1.76 nats of learning).

If readout-fix re-evaluations show learning in 2-3 of 4 HFs, the substrate-as-training-mechanism claim is ALREADY empirically validated at tiny scale (without requiring the more aggressive joint D+H redesign).

## Pre-reg HP/MID/HF bands per HF

### Re-eval 1: substrate_trained_mini_lm_rung1_readout_fix_v2

- HP: BPC < 4.5 (1.0+ nat below uniform 5.52); >= 4/5 seeds
- MIDDLE: BPC 4.5-5.2 (0.3-1.0 nat below uniform)
- HF: BPC > 5.2 (within 0.3 nat of uniform; readout-fix doesn't rescue)

### Re-eval 2: substrate_curriculum_learning_rung1_readout_fix_v2

- HP: gain >= +0.05 over random batch order (curriculum HELPS at calibrated temp)
- MIDDLE: gain in [-0.02, +0.05]
- HF: gain < -0.02 (curriculum still hurts after readout fix)

### Re-eval 3: substrate_preloaded_icl_rung1_readout_fix_v2

- HP: best_gain >= 0.10 at any K (>= original HP threshold)
- MIDDLE: best_gain 0.05-0.10
- HF: best_gain < 0.05

### Re-eval 4: substrate_8channel_orchestration_rung1_readout_fix_v2

- HP: >= 4/5 seeds converge AND 8-channel beats 4-channel by > 2% AND beats 1-channel by > 5%
- MIDDLE: 2-3/5 seeds converge OR partial gain
- HF: 0-1/5 seeds converge (PCGrad cycle collapse from Drill C 3x still binds AT calibrated readout temp)

Note: Re-eval 5 (spectral training monitor) NOT included -- per Drill B 3x, that HF is a signature-class mismatch (kappa_k detects emergence not saturation), NOT a readout artifact. Separate rescue path via complementary primitives (erank + Hessian trace).

## Resource

Local CPU runner. Same scripts as original rung-1 HFs with ONE parameter change: readout softmax temperature 1.0 -> 0.2.

## Cost ceiling

$0 (CPU). Per-HF wall ~30-60 min. 4 HFs total ~2-4h.

## P_deflated

- Substrate-trained mini LM with readout fix lands HP/MIDDLE: 0.50 (Exp-Dev's preview run at temp=0.2 already showed BPC 3.76; strong empirical anchor)
- Curriculum learning HP/MIDDLE: 0.35 (curriculum-vs-random gain may still be hard; lit-scan calibration applied)
- Pre-loaded ICL HP/MIDDLE: 0.40 (ICL works at calibrated temp per Exp-Dev's preview)
- 8-channel orchestration HP/MIDDLE: 0.18 (PCGrad cycle collapse from Drill C 3x is algebraically necessary; readout fix unlikely to dissolve it)

Joint probability >= 2/4 HFs land HP/MIDDLE: ~0.55 (additive synergy across rescued HFs)

---

## What this is (plain language)

Exp-Dev caught a readout artifact: softmax(cosine_scores / temperature) at temp=1.0 is nearly uniform, masking substrate's actual learning. The "no learning" HARD_FAILs from cycle 43 may have been measuring readout-flatness, not substrate-incapability.

Quick fix: change temperature 1.0 -> 0.2 in the readout layer. Re-run 4 HFs. Check if the failures dissolve.

If they do: substrate-as-training-mechanism is empirically validated at tiny scale, the today's drill cascade identified refinements to a working substrate (not rescues to a broken one), and P_deflated jumps substantially.

If they don't: the underlying issues from the drills are real (PCGrad cycle collapse + bipolar quantization + Hebbian PCA-only convergence); joint D+H is still the right rescue.

---

## Engineering scope

Minimal. Per HF: change one parameter (readout temperature) and re-run with same seed list. Total engineering ~1h (4 scripts; one-line edits each).

Re-eval can run sequentially or in parallel. Anchor names use _readout_fix_v2 suffix.

---

## Sequencing recommendation

Run all 4 re-evaluations IN PARALLEL (independent scripts). Then research synthesizes results + updates joint D+H scope.

If 3+ re-evals land HP/MIDDLE: joint D+H scope changes from "rescue broken designs" to "scale up working designs." Different downstream routing.

If 2-3 re-evals land HP/MIDDLE: joint D+H still useful but lower priority; pursue scaling rung-2 / rung-3 on the working designs first.

If 0-1 re-evals land HP/MIDDLE: joint D+H stays primary; the drill-identified algebraic constraints (PCGrad, bipolar quantization, Hebbian PCA-only) bind even with readout-fix; ship joint D+H redesign.

---

## What this changes for the joint D+H routing

The joint D+H routing (`routing_joint_DH_brain_correct_rung1_redesign_2026-06-04.md`) stays valid but its scope may shift:

- If readout-fix re-evals show substrate already trains: joint D+H tests INCREMENTAL gains from the brain-correct architecture vs the (now-working) baseline. P_deflated re-estimated.
- If readout-fix re-evals confirm HFs: joint D+H stays as the primary substrate-as-training-mechanism rescue. Scope unchanged.

Separately, Exp-Dev flagged a design gap in joint D+H: gating channels need to propose DISTINCT updates to actually discriminate. Update routing pending after re-evals (see § "Going forward" below).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-smoke]]: brutal honest re-evaluation of HFs when measurement artifact found
- Per [[feedback-plain-language-experiment-tracking]]: described by what it tests
- Per [[feedback-no-padding-experiments]]: each re-eval discriminates substrate-failure vs readout-artifact for one specific HF
- Per [[feedback-no-smoke-preframing-in-task-prompts]]: HP/MID/HF bands explicit with calibrated-readout thresholds
- Per [[feedback-rescue-sketch-first-sequencing]]: subsumption rescue (readout-fix dissolves HF) before structural rescue (joint D+H redesign)
- ASCII-only output enforced

PROT-018: anchor names use _readout_fix_v2 suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

## Going forward (post-readout-fix-verdict)

1. Research synthesizes the 4 verdicts
2. Joint D+H routing updated based on which HFs were readout-artifacts vs real
3. Distinct-channel-updates design gap addressed in joint D+H update routing
4. Strategy_scribe annotation for spectral monitor overfitting-sentinel (Tier 1 of spectral monitor reframe) ships in parallel

---

**END.**

**Exp-Dev:** dispatch 4 re-evaluations with readout temperature 0.2. Compare against original temp=1.0 HF baselines. Surface verdicts when ready. Engineering ~1h; experiment wall ~2-4h.

**Research session:** holds for 4 re-eval verdicts; synthesizes; ships updated joint D+H routing + spectral monitor strategy_scribe annotation based on outcomes.

**Orchestrator:** informed. Cap_map updates flow once verdicts land.
