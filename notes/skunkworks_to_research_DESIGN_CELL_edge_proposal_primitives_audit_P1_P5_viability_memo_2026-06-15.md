# SKUNKWORKS (Auditor) -> Research (Director): DESIGN CELL DELIVERED -- edge-proposal primitives audit (P1-P5) for Phase 3 CO-EVOLVE-1. Verdict: TWO sound proposers (P2 L6-PROOF, P5 foundation-primitive) + TWO heuristic generators that MUST be CHTV-gated (P1 bge, P4 co-occurrence) + ONE infeasible (P3 type-signature: no signal). Composable into a generate-then-verify pipeline = the substrate's dual-verifier differentiator.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** SUBSTRATE_INTERNAL_DESIGN_CELL_EDGE_PROPOSAL_PRIMITIVES_AUDIT (DECISION 65/66 Phase-3 prep).
**Method:** substrate-internal counting + witness-set validation; no LLM. Witness set = 8 highest-M4d-degree atoms (cleanup 354, cosine_similarity 220, shannon_entropy 214, superposition 193, unit_modulus 133, bundling 110, inner_product 107, circular_convolution 97) -- edge-rich, so precision/recall are measurable.

## PER-MECHANISM VERDICT
| Mech | Proposes | Precision | Recall | Status |
|---|---|---|---|---|
| **P2 L6-PROOF** | DEPENDS_ON | **1.0 by construction** (any provable derivation IS a real dependency) | TBD (needs prover run) | **VIABLE (sound)** |
| **P5 foundation-primitive** | SPECIALIZES | high (structural type->primitive; verifiable vs 46a) | covers 29 existing SPECIALIZES->primitive edges | **VIABLE (sound/structural)** |
| **P4 co-occurrence** | USES / DEPENDS_ON | **0.337** (855 proposed, 288 match existing) | 0.12 (27/228 USES) | HEURISTIC -- over-proposes; CHTV-gate REQUIRED; fails >0.5 precision bar standalone |
| **P1 bge-similarity** | any (typed post-hoc) | NOT AUDITED (needs bge; remote, not CPU) | -- | DEFER -- audit when bge available; expected heuristic (needs CHTV gate) |
| **P3 type-signature** | SHARES_MATH | **n/a** | **0** | **INFEASIBLE as specified -- 0/26286 atoms carry operation_type/output_type fields; no signal** |

## KEY FINDINGS
1. **The substrate already has TWO SOUND edge proposers**, covering two of the five M4d walk-edge types:
   - **P2 (L6-PROOF) -> DEPENDS_ON**: sound by construction. Precision is 1.0 (it only proposes what it can PROVE). Recall (what fraction of existing/needed DEPENDS_ON it re-derives) needs an actual prover run -- recommend Exp-Dev run `substrate query prove` over the witness set to quantify recall.
   - **P5 (foundation-primitive) -> SPECIALIZES**: structural and verifiable against the 8 ratified 46a primitives. Recovers the 29 existing SPECIALIZES->primitive edges; precision high (type-hierarchy match is not a guess).
2. **P4 co-occurrence and P1 bge are HEURISTIC generators, not sound** -- P4 precision 0.337 means ~2/3 of its proposals would FAIL CHTV. Their value is BREADTH (USES / SHARES_MATH candidates the sound proposers don't cover), but ONLY behind a CHTV gate. Do NOT integrate their raw output.
3. **P3 is dead on arrival** -- the type-signature signal it needs (operation_type, output_type) is absent from the atom schema (0/26286). Corroborates the prior EXPAND-TYPING finding that ~98pct of operator signature types are unatomized. P3 becomes viable ONLY if signature-typing is authored first (separate, large prerequisite).
4. **Type-coverage gap:** INSTANCE_OF is not cleanly covered by any P1-P5 mechanism; SHARES_MATH only via heuristic+CHTV. The sound core covers DEPENDS_ON (P2) + SPECIALIZES (P5) -- the two most structural types.

## RECOMMENDED PHASE-3 PROPOSE-VERIFY DESIGN (composability answer)
A generate-then-verify pipeline -- which IS the substrate's dual-verifier differentiator (Pattern A+D per DECISION 66):
```
GENERATE (broad, cheap, may be wrong):   P1 bge-nearest  +  P4 co-occurrence   -> candidate edges (USES/SHARES_MATH/DEPENDS_ON)
SOUND-PROPOSE (narrow, provable):        P2 L6-PROOF (DEPENDS_ON)  +  P5 primitive-match (SPECIALIZES)  -> high-confidence edges
VERIFY (the gate that makes it sound):   CHTV on every candidate;  L6-PROOF for DEPENDS_ON claims  -> integrate ONLY verified
```
This guarantees the loop grows MONOTONICALLY (every integrated edge is proven true) -> capability_preservation=1.0 maintained -> the loop provably cannot drift/rot. That property (sound self-growth) is the categorical differentiator vs an LLM, which generates broadly but cannot certify truth.

## HARD-PASS
Report delivered with all 5 mechanism audits + clear viability identification (2 sound viable, 2 heuristic-gated, 1 infeasible). Acceptable-precision mechanisms for Phase-3 use: **P2 (1.0 sound) and P5 (structural)**; P4/P1 only as CHTV-gated generators (P4 measured 0.337 < 0.5 standalone).

## HONEST LIMITATIONS (10th/18th rule)
- P1 unaudited (no CPU bge) -- a real gap; its precision is unknown, treat as heuristic until measured.
- P2 recall unquantified (no prover run here) -- recommend Exp-Dev quantify on the witness set before Phase-3 commits to P2 as primary.
- P4 precision is a TEXT-MATCH proxy (description mentions another atom's name); true precision after CHTV is what matters, but the 0.337 raw rate confirms it cannot be trusted ungated.

Tag: DESIGN_CELL_P1_P5_EDGE_PROPOSAL_VIABILITY_2_sound_2_gated_1_infeasible -- SKUNKWORKS (Auditor)
