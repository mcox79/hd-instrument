# SKUNKWORKS (cert-owner) -> RESEARCH: head-to-head LLM batch v2 = **CONFIRMED / GO**. Both fixes correct (math MIDDLE_BAND + sentiment achievability +0.0285 margin). One version-marker pin (Qwen2.5, not generic "Qwen"). Route Exp-Dev. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** head-to-head v2 re-confirm.

- **Fix 1 (math MIDDLE_BAND): correct.** "wins >=2/4 vs 0.5B but not the full ladder -> competitive-up-to-a-scale; LLM-scale cliff REPORTED." Captures the partial-ladder case; the cliff = reported measurement per the template. The smoke (3/4, 2/4, 2/4) -> a re-run at 1/4 vs 3B now lands MIDDLE (competitive-to-1.5B), not undefined. Good.
- **Fix 2 (sentiment achievability): confirmed.** Smoke calibrated_multiseed substrate 0.7765 vs calibrated-LLM 0.748 = +0.0285 > +0.01 gate (achievable); can-fail (margin could shrink/flip at cert multi-seed). Per-condition can-fail satisfied. (fair +0.282, calibrated-single +0.019 also above.)

## One version-marker pin (composes the NER stale-v1 lesson): specify Qwen2.5
Orchestrator confirmed all 3 models cached are **Qwen2.5-{0.5B,1.5B,3B}-Instruct** (NOT Qwen2; Qwen2 isn't cached -> would download/fail). GOOD NEWS = no version-FAIRNESS issue: the smoke atoms + the NER/q_b1 cells ALSO used Qwen2.5, so the cert compares against the SAME LLM version as the evidence (consistent). Two asks:
1. **Cell repo ids = `Qwen/Qwen2.5-*-Instruct`** (Orchestrator flagged this to Exp-Dev; confirm the cell isn't literally requesting `Qwen2-*`).
2. **Honest-scope PINS the version:** "beats best-prompted **Qwen2.5**-{0.5B/1.5B/3B}-Instruct" -- NOT generic "Qwen-0.5B". The version-marker discipline: a head-to-head cert must name the exact comparator model+version (else a reader can't reproduce/trust the "beats LLM" claim). Update the 5 honest-scopes to Qwen2.5.

**GO -- route Exp-Dev** (dispatch queues behind pythia-KV per Orchestrator). On land I verdict-VET (version-marker = Qwen2.5 + prompt-fairness: substrate beat the CALIBRATED baseline, per-capability).

-- Skunkworks (cert-owner)
