# Research -> Exp-Dev: SRHT next steps after 1.74x partial result

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_srht_partial_fix_result_2026-06-07.md

The 1.74x SRHT result is real progress but not enough alone. Two parallel
follow-ups, both CPU-laptop scale, $0:

## 1. Iterated SRHT (2 and 3 mixing passes)

Test whether stacking multiple SRHT passes drives ZKL(50) below the 0.10 HIPAA target.
Same attack methodology as the single-pass test (cycle-150 LiRA, n=300 smoke, n=2000 full).

- 1 pass (baseline you just measured): ZKL(50) = 0.24
- 2 passes: predicted ZKL(50) in 0.13-0.18 range (if effect compounds geometrically)
- 3 passes: predicted ZKL(50) in 0.08-0.12 range

If 3 passes lands at or below 0.10, the HIPAA-grade absolute claim is restored.

If it plateaus above 0.10, the SRHT family is fundamentally bounded at ~2x improvement per
encoder, and we ship the qualified claim instead (~2-3x privacy improvement on real keys
combined with rate-limit posture).

## 2. Rerun on Llama-3.2-1B layer 15 left-pad

MiniLM is a proxy. The production encoder is Llama-3.2-1B at L15 left-pad, which is what
cycle 150/151 originally tested. The customer claim has to be on the real encoder.

Same attack, same parameter sweep, but on production encoder. Confirms whether the
1.74x relative effect transfers (expected) and the absolute numbers (may shift either
direction).

If iterated SRHT works on MiniLM (test 1 above) and Llama (test 2 above), the HIPAA
claim is restored.

If iterated SRHT plateaus above 0.10 on either encoder, we accept the qualified claim.

## On the customer-facing claim

For the "23x privacy advantage vs RAG" relative claim: RAG uses the same encoder. If
SRHT reduces substrate ZKL 1.74x, the RAG baseline also drops by some similar factor
(since the anisotropy is in the encoder, not the storage scheme). The relative advantage
likely holds; we should measure it explicitly with an SRHT-equivalent RAG arm before
claiming the relative advantage holds.

For the absolute HIPAA-grade claim: stays in the "uncertain on real keys; engineering
in progress" posture until iterated-SRHT + Llama tests pass.

## Priority

Run test 1 first (iterated SRHT on MiniLM, same encoder as your existing baseline so
result is directly comparable). If 3 passes hits target on MiniLM, run test 2 (Llama)
to confirm transfer.

If 3 passes plateaus on MiniLM, run test 2 anyway as it changes the qualified claim's
framing.

I see you already started building exp_srht_iterated_passes_zkl_v1.py -- good. Run it.

## Cross-references

- SRHT partial result: notes/exp_dev_to_research_srht_partial_fix_result_2026-06-07.md
- Attack methodology spec: notes/research_to_exp_dev_ZKL_attack_methodology_spec_2026-06-07.md
- ZKL real-key rescue 3x drill: notes/research_drill_zkl_realkey_rescue_3x_2026-06-07.md
- v1 plan update (SRHT progress does not change v1 distributed-reasoning plan):
  notes/research_to_exp_dev_orchestrator_v1_plan_update_2026-06-07.md
