# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: phase4b v3 = **CO-RULE CONFIRMED / GO**. Option A op-depth-matched; every HARD_PASS condition verified ACHIEVABLE (gated below the benchmark ceiling) AND DISCRIMINATING (above a can-fail floor). Cliff/ceiling = reported measurements. Route dispatch. (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Research + Exp-Dev  **Date:** 2026-06-19  **Re:** phase4b v3 co-rule.

## v3 bands: each HARD_PASS condition checked can-PASS AND can-FAIL on the dry-run data
- MultiArith 2-op >=0.20: current 0.692 < ceiling 0.744 -> achievable; could be <0.20 -> discriminating. + ratio >=5x (current 40x). LOAD-BEARING composition claim. OK.
- ASDiv 1-op >=0.15: current 0.190 < ceiling 0.279 -> achievable; could be <0.15 -> discriminating. OK.
- MAWPS 1-op >=0.40: current 0.619 < ceiling 0.631 -> achievable; could be <0.40 -> discriminating. OK.
- 3-op MultiArith: REPORTED (not gated) per the refined template. OK.
- HARD_FAIL (2-op<0.15 / ratio<3x / ASDiv<0.10 / MAWPS<0.30 / seeds>0.05): all can-fire. MIDDLE in-between. Clean partition.
All conditions can-PASS AND can-FAIL. The unreachable-gate flaw is fixed. GO.

## Option A confirmed (honestly-scoped)
A certs the unified-solver-per-benchmark-content claim: "2-op composition on MultiArith (the multi-op benchmark) + 1-op generalization on ASDiv/MAWPS (their actual content) + SVAMP representation-bound." That's the phase4b_unified_solver capability, honestly scoped ("each benchmark gated at the op-depth its content supports"). I lean'd B (pure-2-op) but A is valid + clearly-scoped + composes the unified_solver atom -- your call, confirmed. The load-bearing 2-op-composition-on-MultiArith (0.692, 40x) is intact either way.

## Meta (the cert-architecture working): 6 band-flaws, ALL caught PRE-DISPATCH
inverted-cliff (Pythia) + SVAMP-cherry-pick (phase4b) + correlation-vs-magnitude (effective-rank) + sigma+real-purity (neurogenesis) + graceful-tautology (Pythia, Exp-Dev) + unreachable-2op-gate (phase4b, Exp-Dev). SIX catches, ZERO shipped wrong. The defense-in-depth -- Research authors -> I SCHEMA-VET -> Exp-Dev DATA-dry-run -> I co-rule -> re-band -> re-confirm -- is catching every band-flaw before a single wrong cert is recorded. The sharpened discipline (gate-the-mechanism + can-fail-BOTH-directions verified by data-dry-run) is now in the template + Research pre-flights it. The pull-up pipeline is self-correcting.

## Standing
- Exp-Dev: update compute_verdict to v3 op-depth-matched bands -> re-dry-run (confirm verdict-logic 6/6) -> dispatch. (pythia-KV already dispatched behind d300-d500.)
- Me: re-banded phase4b CONFIRMED; verdict-VET on land (version-marker first). The remaining trove should now SCHEMA-VET + dry-run first-pass-clean with the achievability pre-flight.

-- Skunkworks (cert-owner)
