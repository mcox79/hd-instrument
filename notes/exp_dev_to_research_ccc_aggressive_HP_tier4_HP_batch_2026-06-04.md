# Exp-Dev -> Research: CCC-smoke REVISED HARD_PASS + Tier-4 HARD_PASS + batch verdicts

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + Testbed  **Date:** 2026-06-04 ~22:50

## CCC-smoke REVISED (your relational/analogical revision) -- HARD_PASS (smoke; full queued)
substrate_cognitive_core_smoke_pythia70m_AGGRESSIVE: recall=1.00 analogical=1.00 counterfactual=0.94
cross_domain=1.00 -> HARD_PASS. The substrate's VSA-native REASONING (not retrieval) is validated at the scaffold:
- ANALOGICAL: relation R=A*B learned from pairs applies to NOVEL entities (A:B::C:?) via binding arithmetic -> 1.00.
- COUNTERFACTUAL: B6 deletion of a fact correctly removes its object from the query (delta computed) -> 0.94.
- CROSS-DOMAIN: relation learned on 4 domains transfers to held-out 5th (shared structure) -> 1.00.
- RECALL: B2 sparse noisy-cue -> 1.00.
This is the "reasoning vs retrieval" distinction the user demanded -- empirically grounded at smallest scale.

## Tier-4 (substrate-attention IN Pythia-160M) -- HARD_PASS (FULL confirmed)
ppl_ratio 1.06x, entropy_ratio ~3, grad_ratio <1 -> substrate-Hebbian attention is TRAINING-STABLE inside a real
pretrained LLM. Substrate-as-intrinsic-LLM-component empirically validated. (Path A's attention-substitution leg.)

## Stage-A training-speed: MIDDLE_BAND (full). My earlier CCC attempt (whole-sentence-VQ->transition): HARD_FAIL
-- superseded; the correct CCC design is your synthetic-VSA-reasoning scaffold (above) + CCC-1 PATH-A distillation.

## CCC-1 REVISED (5-dim eval) + CCC-1-EXTRA KG: need the Pythia-160M residual npz. Testbed shipped the extraction
SCRIPT (per your note 22:10) but NO npz on disk yet. When the npz lands I build CCC-1 REVISED (multi-hop + analogical
+ counterfactual + compositional + cross-domain, 5-dim) + CCC-1-EXTRA (KG triple completion) + EX-CONCEPT-1 real.

## Still running: Tier-6 Phase D, capacity-4096/8192. Next CPU: R1 4-modulator, R2 sparse-resonator K=26.
**END.**
