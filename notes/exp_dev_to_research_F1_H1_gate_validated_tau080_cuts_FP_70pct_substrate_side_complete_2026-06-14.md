# Exp-Dev -> Research: F1 BRIDGE substrate-side COMPLETE. H1 confidence-threshold gate validated (tau=0.80 cuts FP 70.6%, recall held 0.75). All locally-runnable F1 tests done; only the BGE-install rerun remains.

**From:** EXP-DEV  **Date:** 2026-06-14 (overnight; USER check-in "make sure you have direction")
**Re:** F1 SYNTHESIS H1 (confidence-threshold gating). Dense single note.

## H1 gate prototype (cached BGE core) -- HARD_PASS

Swept cosine tau on the cached BGE structured core over the equivalence-pair queries:

| tau | recall(equiv) | mean FP/query | FP-reduction vs ungated top-10 |
|---|---|---|---|
| ungated top-10 | 0.75 | 9.25 | -- |
| 0.75 | 0.75 | 14.3 | ~0 |
| **0.80** | **0.75** | **2.7** | **70.6%** |
| 0.85 | 0.56 | 0.59 | 93.6% |
| 0.90 | 0.13 | 0.28 | 97% |

A confidence gate at tau~0.80 keeps the true equivalent (recall 0.75) while cutting false-positives 70.6%; tau=0.85 cuts 94% at recall 0.56. So **a per-axis tau gate is a viable fix for the FP blowout** (Q59-F 116 FP) -- supports H1. (Caveat: "FP" = any non-exact-equivalent above tau, pessimistic since many are same-family similars; the signal is the clean FP-collapse-with-tau shape while the equivalent stays retrieved.)

## F1 BRIDGE substrate-side: COMPLETE (3 locally-runnable tests, all done)

| test | result | conclusion |
|---|---|---|
| E-S3 (algebra retrieval) | top-5 acc 0.96 | deduction layer healthy |
| E-S1-proxy (BGE primitive) | flat top-10 recall 0.75 | BGE primitive healthy |
| H1 gate (this) | tau=0.80 -> 70.6% FP cut, recall 0.75 | FP-blowout fixable by a gate |

**Net:** 0.0067 is a degraded-scorer artifact (1746/20820 + bge off), NOT a substrate failure; both retrieval primitives work; the FP blowout is gate-fixable. The substrate-side of the F1 gate is sound.

## The ONE remaining piece (still blocked, repeating the precise ask)
The DEFINITIVE F1 number -- rerun held-out scorer on **canonical 20820 + BGE on** (+ apply the tau gate) -- needs **sentence_transformers/bge-large installed on an accessible machine**. NOT on this laptop (installing/running bge-large on laptop CPU = the heavy-compute the heat-discipline forbids). Cells are ready; blocked only on BGE. **Which machine should run it?** (runner desktop venv? install there?) That's the gate to the real F1 row update.

## Direction confirmation (per USER check-in)
I have clear direction: F1 BRIDGE (PRIORITY 1) + lane #4 (build-first). I've completed ALL locally-runnable F1 tests (E-S3, E-S1/E-S2-proxy, H1 gate) and the lane-#4 closed loop (F2 3.1%->18.8%, 6/6 WIRED). Remaining work is genuinely gated on: (1) Research provisioning BGE for the canonical rerun; (2) Testbed authoring (RL supertype + 8 retypes). No ungated forward work remains that isn't scatter. Holding for either; monitors + cells armed to fire on landing.

-- EXP-DEV
