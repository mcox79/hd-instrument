# Exp-Dev -> Testbed/Research: PATH-TO-0.70 increment VALIDATED full-stack -- combined A=bge-top5 + E=bge-threshold-0.70 route fixes lift qa_self_knowledge macro 0.5204 -> 0.5711 (+0.0506), zero regression on B/C/D/G. E-route alone +0.272 (keyword-only -> bge-threshold). Biggest single increment this session.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: path-to-0.70 route mechanics. bge = embedding model (NO generative LLM). GPU.
**Cell:** exp_qa_self_knowledge_full_stack_AE_combined_gpu_v1.py (all 53 Qs; route_B v3 + 10 candidate edges held fixed; E tau=0.70 FIXED).

## Result (all 53 Qs; B/C/D/G held fixed)
| config | A | E | MACRO |
|---|---|---|---|
| production (A=keyword-UNION-bge-top3, E=keyword-only) | 0.2386 | 0.4950 | 0.5204 |
| **combined fix (A=bge-top5, E=bge-cosine-threshold-0.70)** | 0.2706 | **0.7667** | **0.5711** |
| delta | +0.0320 | **+0.2717** | **+0.0506** |
- B=0.6985 C=0.6217 D=0.75 G=0.6667 IDENTICAL in both -> the two route changes are isolated, zero regression.

## What this delivers
- A SUBSTANTIAL, shippable path-to-0.70 increment: macro 0.5204 -> 0.5711 (+0.0506) from TWO simple route fixes, no encoder
  change, no corpus change:
  - **A-route:** drop the keyword union, use bge-top-5 (A +0.032). The keyword matcher added false positives.
  - **E-route:** replace keyword-only with a bge cosine-threshold (~0.70) over the meta/methodology corpus (E +0.272). route_E
    was keyword-only and left E-gold (at bge rank ~0.0, cos ~0.81) on the table; the threshold recovers it.
- Both levers were predicted by the cue-alignment diagnoses (both weak axes are cue-aligned -> the lever is SELECTION, not the
  encoder) and validated here at full-stack.

## Honest caveats
- E tau=0.70 was FIXED here (not re-tuned at full-stack) -- good -- but it was originally chosen on the same 8 E-Qs, so the E
  result is in-sample (not held-out). The robust tau band [0.65,0.75] all beat keyword, so the lift is real; the exact +0.272
  may be slightly optimistic. Recommend Testbed pick tau on a held-out split. The earlier E-subset reported +0.307; the honest
  full-stack number with fixed tau is +0.272.
- Small benchmark (53 Qs; A n=12, E n=8). Magnitudes will firm up with more questions.

## Path-to-0.70 ledger (route mechanics, this session)
- B-axis: route_B v3 (accept-all-reltypes bidirectional) + 10 candidate edges -> B 0.325 -> 0.6985 (banked earlier).
- A-route: keyword-UNION-top3 -> bge-top5: +0.032 A / +0.0096 macro.
- E-route: keyword-only -> bge-threshold-0.70: +0.272 E / ~+0.045 macro.
- **Combined macro now 0.5711** (from ~0.4684 v1). Remaining gap to 0.70 is corpus-bound (B corpus gaps, Phase-6 ingest) --
  Research's domain, not route-fixable.

## Routing
- **Testbed:** SHIP-candidate -- both route fixes (A=bge-top5; E=bge-cosine-threshold over meta/methodology). +0.0506 macro,
  zero other-axis regression. Pick E-tau on a held-out split. Encoder/index unchanged; only A + E selection policies.
- **Research:** the route-mechanics levers are now near-exhausted (A + B + E done); the remaining path-to-0.70 gap is corpus/
  ingest-bound (Phase 6 + the 144 T1 algebra backfill + B-axis corpus edges). Route R&D has delivered ~+0.10 macro.
- **Exp-Dev:** path-to-0.70 route-mechanics thread CLOSED -- macro 0.5204 -> 0.5711 validated full-stack. Holding.
