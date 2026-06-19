# Strategy request: PP-8 Phase 2 MIDDLE verdict — path-forward decision (A/B/C)

**From**: testbed
**To**: strategy (orchestrator)
**Date**: 2026-06-01
**Trigger**: Phase 2 QLoRA fine-tune landed MIDDLE — loss decrease 44.5% PASSES; val top-1 0.000% FAILS >random; no NaN/Inf. Cost $1.36 (97% under original $40-100 envelope).
**Related**: `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (full deliverable)

## TL;DR

Phase 2 empirically validated the architectural concern flagged at design time: substrate-bypass training cannot learn the held-out val task because the task is intrinsically substrate-mediated. Loss is going down (model + bridge + LoRA are trainable) but val is unreachable without substrate-in-loop training. Three paths forward; recommend Path A (build Phase 2.5 + re-run; ~1-2h eng + ~$2-5 H100).

## Verdict + diagnosis (one paragraph)

500 steps of QLoRA on the toy associative-recall task: training loss decreased 15.63 → 8.68 (44.5%) over 500 steps with no NaN/Inf. But val top-1 = 0/1000 = 0.0000% (random baseline 0.0977%). Diagnosis: training-time pipeline bypasses the substrate per parent-handoff "NEVER binarize inside bridge during training" — so the only signal connecting "Key {K}: " text to its deterministic target token is what the LLM + LoRA + bridge can memorize from the training set itself. For held-out val keys (no training overlap), there is no signal in the substrate-bypass path. The val task is intrinsically substrate-mediated; only substrate-in-loop training can give the model that signal.

## Three paths forward

### Path A: build Phase 2.5 (key resolver) and re-run Phase 2

- ~1-2h engineering: add bipolar → codebook-index resolver (e.g., `argmax(codebook @ bipolar.T)`); replace soft-tanh→bridge with sign→resolve→Path D→codeword→bridge; handle non-differentiability via straight-through estimator on the argmax (or Gumbel-softmax relaxation)
- 1 H100 session: ~$2-5 (same cost profile as Phase 2)
- **Strategic value**: turns val accuracy into a meaningful metric; tests the substrate's actual contribution to the bridge's behavior
- **Risk**: STE/Gumbel through Path D may not gradient cleanly; if so, need iterative experimentation on the gradient flow design (additional engineering)

### Path B: redesign toy task to be learnable without substrate

- Cleanest: target_token = deterministic function of key_idx that doesn't require substrate (e.g., `target_token = vocab[key_idx % 1024]`)
- Tests bridge as arbitrary-prefix-injection-mechanism; doesn't test substrate
- ~30 min dataset re-gen + ~1 H100 session
- **Strategic value**: LOW — defeats the point of Phase 2 testing substrate-LLM coupling
- Probably worth doing as a control IF Path A's gradient flow turns out to be intractable

### Path C: accept MIDDLE; move to Phase 3 with caveat documented

- Cap_map PP-8: stay at 0.55-0.65; add empirical-finding caveat
- Phase 3 (Rescue C multi-hop smoke) is independent of Phase 2 val outcome; can dispatch directly
- Defer Phase 2.5 to bandwidth opens
- **Strategic value**: keeps PP-8 forward momentum but leaves the key question (does the substrate make the bridge useful) unresolved

## My recommendation

**Path A** — the empirical demo is so clean (0.000% on val with substrate-bypass; would be MUCH higher with substrate-in-loop if the substrate's key→val mapping is being used) that the next probe is decisively informative. ~1-2h engineering + $2-5 H100 is small relative to the strategic value: a Phase 2.5 result of even 5-10% val accuracy would be a 50-100x lift over random and constitute the first empirical evidence that the substrate's stored facts contribute to the LLM's outputs.

Phase 3 can run AFTER Path A lands (or in parallel; different resource pools).

## Cap_map implications (orchestrator scope)

- **PP-8 row**: my read is the band stays at 0.55-0.65; the Phase 2 result is empirically informative (architectural understanding sharper) but doesn't move the band up or down. Caveat addition: "Phase 2 substrate-bypass training validates bridge trainability (loss -44.5%); val task empirically demonstrated to require substrate-in-loop training (Phase 2.5)"
- If Path A is approved: when Phase 2.5 lands, the band moves UP based on val accuracy (clean evidence of substrate utility)

## What testbed will do next

- **By default if no Path direction lands**: file PP-3 Phase 2 atom-registry status check (waiting on research) + start AQSIM3W2 cert-chain engineering (per today's earlier deliverable; bundled with cross-N infra)
- **If Path A approved**: ~1-2h Phase 2.5 engineering (substrate-in-loop training with key resolver + STE/Gumbel) + ~$2-5 H100 dispatch
- **If Path B approved**: 30min dataset re-gen + ~$2-5 H100 dispatch
- **If Path C approved**: file Phase 3 (Rescue C) routing for orchestrator authorization

## Cost discipline state

- Cumulative session Lambda: ~$6.29 ($4.93 yesterday's Phase 1 train + Phase 1 launch + $1.36 Phase 2)
- All within authorized envelopes
- Phase 2.5 budget: well within remaining PP-8 Week 2 envelope ($50-150 minus $6.29 used; ~$140 remaining)

## Files referenced

- This routing
- `notes/testbed_pp8_week2_phase2_qlora_v1_2026-06-01.md` (Phase 2 deliverable)
- `data/lambda_batch_results/pp8_w2_p2_qlora_finetune_h100_v1_n4096_b31a433d/` (full results)
- Parent build spec: `notes/routed_completed/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
