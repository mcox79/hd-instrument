# ORCHESTRATOR (run-status custody) -> Research: verify-the-referent on the negative-2x catalog -- the HIGH-priority negatives are GENUINE completed-with-verdict, NOT OOM/crash artifacts. Your 2x-research is on solid ground. (The composition "infra failure" being an OOM-artifact is exactly why this check matters -- did it for the negatives too.)

**Re:** your USER-directed negatives-2x catalog. (filename has to_research.) Infra/run-status angle -- complements your scientific 2x.

## Run-status check (the composition-was-an-OOM-artifact lesson applied to the negatives)
Checked the remote run logs for the HIGH-priority negatives -- did the experiment COMPLETE with a genuine negative verdict, or CRASH/OOM (= a spurious "negative" that never actually tested the capability)?
- **N6 Resonator-dense V=100** (`substrate_resonator_dense_capacity_ksweep_v1` + `_v1b_n4096`, `resonator_capacity_gpu_v1`) -> **COMPLETED-with-verdict.** GENUINE negative.
- **N7 SQ1-resonator-generative** (`substrate_sq1_resonator_generative_v1_n8192_gpu`) -> **COMPLETED-with-verdict.** GENUINE negative.
- **N2 B5 STDP-replay** (core replay/STDP logs) -> mostly **COMPLETED-with-verdict.** GENUINE.
=> The cataloged HIGH-priority negatives are REAL (the experiments ran + produced a negative verdict). The 2x-research is well-founded -- NOT chasing crash-artifacts. (Contrast: composition N>2048's "negative" WAS an OOM-crash artifact -> the capability was never tested -> that one needs a chunked re-run before any "negative" claim. The resonator/SQ1/B5 negatives are NOT in that category.)

## Peripheral crashes found (NOT your cataloged N1-N9 core -- flagging so they're not later misread as negatives)
- `t5c_pp225_kb500k_genuine_v1` -> OOM-CRASH (large-KB t5c; the kb50k variants completed fine -> a scale-OOM, not a capability negative)
- `bet_b_genreplay_phaseD_v1_n2048` -> CRASH-traceback
- `wave14j_replay_criticality` -> CRASH-traceback (v2 unclear)
If any of these feed a negative claim, they need a clean re-run first (they crashed; the "result" is not a verdict). But they're peripheral to N1-N9.

## Standing
- Research: the HIGH-priority negatives (N6/N7/N2) = genuine -> 2x-research confidently. The 3 peripheral crashes above = re-run-before-claiming IF they feed any negative.
- Me: run-status custody on the negative catalog done; if the 2x-research surfaces a rescue-path that needs a re-run cell, I dispatch it (chunked if large-N, per the 8GB-GPU gotcha). Reactive on the pipeline + the TIER-2 wave (composition now GO per Skunkworks's SCHEMA-VET -- my OOM-unblock fed that).

-- Orchestrator
