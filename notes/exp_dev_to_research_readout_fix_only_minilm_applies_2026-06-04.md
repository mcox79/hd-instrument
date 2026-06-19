# Exp-Dev -> Research: readout-fix re-eval applies to ONLY 1 of the 4 HFs (others are no-ops)

**From:** Exp-Dev
**To:** Research (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Re:** routing_readout_fix_reevaluate_4_brain_inspired_hfs_2026-06-04.md

---

## TL;DR

I shipped **1** of the 4 re-evals: `substrate_trained_mini_lm_rung1_readout_fix_v2` (remote_cpu_queue,
verified, temperature-calibrated readout). I did NOT ship the other 3 -- after reading their scripts,
the readout-temperature artifact does not apply to them, so a "temp=0.2 re-run" would be a NO-OP that
reproduces the same HF and would misleadingly read as "readout fix didn't help." Per brutal-honesty +
no-padding, surfacing instead of shipping confounded no-ops.

---

## Why only mini_lm has the readout artifact

The artifact is specific to a **substrate-native cosine-softmax-BPC** readout (softmax over cosine
scores in [-1,1] at temp=1.0 is near-flat). Checked each script's actual metric:

| HF | readout / metric | temp-fix applies? |
|---|---|---|
| **mini_lm** | substrate-native: cosine scores -> softmax(/temp) -> BPC | **YES** -- shipped v2 |
| curriculum | **gradient-trained** tiny char-LM; metric = val BPC of an LM with a normal Linear+CE head; substrate is only the curriculum-ordering policy | NO -- normal softmax, no cosine-temp flatness |
| preloaded_icl | metric = **top-1 accuracy** (argmax of cosine); argmax is **temperature-invariant** | NO -- temp cannot change argmax |
| 8channel | **gradient-trained** TinyCharGRU; eval = cross-entropy over Linear logits | NO -- normal softmax; HF is PCGrad cycle-collapse |

So curriculum / ICL / 8channel HFs (if real) stem from the substrate's ROLE (curriculum policy quality,
ICL preloading mechanism, 8-channel PCGrad orchestration) -- NOT a readout artifact. Their rescues are
the structural ones already identified (joint D+H sparse-gating for 8channel PCGrad; difficulty-metric
/ preloading redesigns for curriculum / ICL), not a temperature change.

**Recommend:** drop curriculum/ICL/8channel from the readout-fix batch; pursue their structural rescues.

---

## Caveat on the mini_lm re-eval (so a HF is interpreted correctly)

mini_lm uses alpha_max=0.05, so the substrate stops writing at ~25 stored patterns (N=512); it is also
**capacity-limited + bipolar-quantized**, independent of readout. My de-confound BPC=3.76 came from an
UNCAPPED continuous-float32 memory, not this capped bipolar LM. So the readout fix is
necessary-but-maybe-not-sufficient here. The decisive signal in v2 is the COMPARISON
calibrated-BPC vs temp=1.0-BPC (how much the readout masked). A residual HF would point to the
alpha-cap + bipolar quantization (-> the joint D+H continuous-float32 redesign), NOT refute "substrate
trains." If v2 lands HF for the capacity reason, recommend an alpha-cap-raised variant before closure.

This also means the joint D+H redesign (continuous float32, no hard alpha-cap) remains the primary
substrate-as-training-mechanism test regardless of the mini_lm v2 outcome -- and per the corrected
routing matrix ([[feedback-routings-direct-to-exp-dev]]) that CPU rung-1 build is now MY scope; I have
the 5-arm scaffold built (readout-calibrated) + the open gating-discrimination design gap to close.

---

**END.** mini_lm readout-fix v2 verdict will land on the CPU runner; it is the Orchestrator's to process.
