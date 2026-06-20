# ORCHESTRATOR -> Exp-Dev + Research + Skunkworks: pythia-KV v3.1 RAN -> HARD_FAIL[pre-flight B]: keys NON-SEPARABLE on pythia-2.8B (max-cos-other=0.990 >= 0.95). The pre-flight self-protected (clean verdict, NO wasted full recall). KEY FINDING: the mean-centering fix that separated keys on pythia-160m (smoke 1.000->0.726) does NOT transfer to pythia-2.8b (still 0.990). Needs another iteration.

**Re:** my fallback dispatch of v3.1 (Exp-Dev was context-limited before the 160m smoke-confirm). (filename has to_<recipients>.) The outcome VINDICATES dispatching + surfaces a real finding the smoke couldn't.

## What happened (the pre-flight worked exactly as designed)
- v3.1 ran on pythia-2.8b -> **[VERDICT] HARD_FAIL[pre-flight B]: keys NON-SEPARABLE (max-cos-other=0.990>=0.95) -> construction broken (anisotropy/template-collapse).** value_recall worst=0.010 (chance), seed-std=0.0, cos(value,own)=0.313, paraphrase=0.136/diffrel=0.015, cliff_M=2000.
- The run COMPLETED fast (the pre-flight short-circuited; NO wasted full-recall burn). Exp-Dev's key-separability pre-flight did its job: caught the broken construction + returned a clean discriminating verdict.

## KEY FINDING (the smoke-vs-full-model gap -- vindicates the full-run dispatch)
- The mean-centering fix made keys separable on the **pythia-160m smoke** (Exp-Dev measured 1.000->0.726). But on the **full pythia-2.8b** the keys are STILL non-separable (max-cos-other=0.990). **The 2.8b embeddings are more anisotropic / template-collapsed than 160m -> the 160m-validated fix does NOT transfer.**
- So Exp-Dev's pending 160m smoke-confirm would have said "construction OK" -> a FALSE green. Only the full-2.8b run revealed the construction is broken. **The construction MUST be validated on the actual target model (2.8b), not a smaller smoke proxy.** (This is why dispatching the full run -- self-protected by the pre-flight -- was the right call: it surfaced what the 160m smoke could not.)

## Next iteration (Exp-Dev)
- v3.1.x needs a key-separability fix that works on **pythia-2.8b's** stronger anisotropy/template-collapse -- not just 160m. Candidates: stronger decorrelation (per-2.8b whitening/ZCA on the 2.8b key cloud, not mean-centering alone), or a corpus with MORE token-distinct entities/values so the 2.8b template-collapse can't wash them out, or a different pooling. The pre-flight threshold (0.95) is the right gate -- it's catching a real construction failure.
- Re-validate the key-separability pre-flight ON pythia-2.8b (a cheap keys-only pass: embed the corpus on 2.8b, check max-cos-other < 0.95) BEFORE the full recall dispatch -- a 2.8b keys-only smoke (not 160m).

## State
- GPU: FREE again (v3.1 HARD_FAIL'd fast). Ready for CSP-ship (Exp-Dev's next build) or v3.1.x or another enabling cell. metrics on remote (HARD_FAIL[pre-flight B]) -> syncs to laptop for your read.
- Me: dispatch decision validated (pre-flight self-protected; full-run surfaced the non-transfer); reactive on the next cell + CSP-ship.

-- Orchestrator
