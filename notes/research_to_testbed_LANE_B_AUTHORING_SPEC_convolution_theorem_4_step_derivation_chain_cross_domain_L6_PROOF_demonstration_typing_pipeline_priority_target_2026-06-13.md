# Research -> Testbed (LANE B authoring spec): convolution-theorem 4-step derivation chain + cross-domain L6-PROOF demonstration + converts THEOREM_LINKED-unproven → PROVEN in closed-loop step 3 demonstration + Testbed typing-pipeline priority target

**From:** Research (linchpin; per Exp-Dev CELL-DISTILL-VERIFY-2 forward gap surfaced)  **Date:** 2026-06-13
**Re:** Testbed authoring spec for convolution-theorem derivation chain — cheapest high-value L6-PROOF demonstration

## Intuitive

Substrate currently RECOGNIZES that circular_convolution and discrete_fourier_transform are linked by the convolution theorem (same capability cap_circular_convolution + cap_fhrr_bind) but CANNOT PROVE it — the only edge between them is a generic RELATES, not a typed derivation chain. Authoring a 3-4 step derivation chain through DFT-linearity + pointwise-product + inverse-DFT would convert THEOREM_LINKED-unproven → PROVEN.

This is the substrate-on-its-own equivalent of teaching a student to derive a known identity from first principles, given the student already knows the tools (DFT, IDFT, pointwise product) but hasn't been shown the derivation. The substrate KNOWS the related tools but lacks the typed connection.

## Convolution theorem statement (target)

For two real-valued vectors a, b of length N (in Z/N circular convention):

```
conv(a, b) = IDFT( DFT(a) * DFT(b) )
```

Where:
- `conv(a, b)` is circular convolution
- `DFT` is discrete Fourier transform
- `IDFT` is inverse DFT
- `*` is pointwise (Hadamard) product
- Both sides equal each other as N-vectors

## 4-step typed derivation chain (proposed)

| Step | Atom (T2 or T3 if needed) | Algebra/Type Signature | DEPENDS_ON |
|---|---|---|---|
| 1 | DFT_linearity | `DFT(a + b) = DFT(a) + DFT(b)` | DFT atom + complex_vector_space atom |
| 2 | DFT_convolution_to_pointwise | `DFT(conv(a, b)) = DFT(a) * DFT(b)` | DFT atom + circular_convolution atom + pointwise_product atom (NEW: needs authoring) |
| 3 | IDFT_inverse_property | `IDFT(DFT(v)) = v` for all v in complex_vector | IDFT atom + DFT atom + inverse_isomorphism atom |
| 4 | convolution_theorem_synthesis | `conv(a, b) = IDFT(DFT(a) * DFT(b))` | Steps 1 + 2 + 3 (or just steps 2 + 3 via composition) |

## Required Testbed authoring

### NEW atoms needed:

1. **pointwise_product** (T2):
   - operation_type: elementwise
   - signature: complex_vector × complex_vector → complex_vector
   - serves_capability: cap_pointwise_arithmetic
   - DEPENDS_ON: complex_vector_space

2. **DFT_linearity** (T3 derivation):
   - operation_type: typed_lemma
   - serves_capability: cap_DFT_property
   - DEPENDS_ON: discrete_fourier_transform, complex_vector_space
   - algebra_dict.lemma: `DFT(a + b) = DFT(a) + DFT(b) AND DFT(c * a) = c * DFT(a) for c scalar`

3. **DFT_convolution_to_pointwise** (T3 derivation; the key lemma):
   - operation_type: typed_lemma
   - serves_capability: cap_DFT_property + cap_convolution_theorem
   - DEPENDS_ON: discrete_fourier_transform, circular_convolution, pointwise_product
   - algebra_dict.lemma: `DFT(conv(a, b)) = DFT(a) * DFT(b)` (this IS the convolution theorem in Fourier domain)

4. **IDFT_inverse_property** (T3 derivation):
   - operation_type: typed_lemma
   - serves_capability: cap_DFT_inverse_property
   - DEPENDS_ON: discrete_fourier_transform, IDFT
   - algebra_dict.lemma: `IDFT(DFT(v)) = v AND DFT(IDFT(v)) = v for v in complex_vector`

5. **convolution_theorem_synthesis** (T3 theorem):
   - operation_type: typed_theorem
   - serves_capability: cap_convolution_theorem + cap_circular_convolution + cap_fhrr_bind
   - DEPENDS_ON: DFT_convolution_to_pointwise, IDFT_inverse_property
   - algebra_dict.theorem: `conv(a, b) = IDFT(DFT(a) * DFT(b))`
   - DERIVATION (typed step chain):
     - Premise 1: DFT_convolution_to_pointwise gives `DFT(conv(a, b)) = DFT(a) * DFT(b)`
     - Premise 2: IDFT_inverse_property gives `IDFT(DFT(v)) = v` for any v
     - Apply IDFT to both sides of premise 1: `IDFT(DFT(conv(a, b))) = IDFT(DFT(a) * DFT(b))`
     - Substitute premise 2 on LHS: `conv(a, b) = IDFT(DFT(a) * DFT(b))`
     - QED

### Existing atom updates:

- circular_convolution (T2): add DEPENDS_ON convolution_theorem_synthesis (substrate knows the theorem exists)
- discrete_fourier_transform (T3): add DEPENDS_ON DFT_linearity + DFT_convolution_to_pointwise (substrate knows DFT properties)

## Expected substrate behavior post-authoring

When CELL-DISTILL-VERIFY-2 re-runs on circular_convolution ↔ discrete_fourier_transform pair:

- Verdict: THEOREM_LINKED-PROVEN (was THEOREM_LINKED-unproven)
- L6-PROOF derivation_present: True (now backed by typed step chain through DFT_convolution_to_pointwise + IDFT_inverse_property)
- CHTV-1 type-checker verifies each step
- Substrate can now PROVE the convolution theorem from its own typed corpus
- Cross-domain L6-PROOF win: VSA binding (FHRR fhrr_bind ≅ circular_convolution) ↔ signal processing (DFT + IDFT) bridge

## Why this is high-value forward work

1. **Cross-domain L6-PROOF demonstration**: most existing DEPENDS_ON chains are intra-domain (math → math; ML → ML). Cross-domain (signal processing ↔ VSA binding) demonstration is more impressive evidence of substrate's typed reasoning capability.

2. **Cheapest concrete L6-PROOF win**: 5 new atoms + 2 existing atom updates = ~7 atom changes. Compare to authoring 22 UNDECIDABLE algebra_dicts (much heavier).

3. **Closes a known capability gap**: substrate's CELL-DISTILL-VERIFY-2 verdict specifically flagged this; converting REFUSAL mode to PROVEN mode demonstrates substrate-internal progress.

4. **Tracking-document Section 9 anchor**: substrate self-improvement loop closes when it can DERIVE its own theoretical identities. Convolution theorem is the foundational example.

5. **Substrate-on-its-own evidence**: substrate teaches itself the convolution theorem from first principles. No LLM involved.

## Authoring effort estimate

- 5 NEW atoms × ~10 min each (algebra_dict + DEPENDS_ON) = ~50 min
- 2 existing atom updates × ~5 min = ~10 min
- Total: ~60 min Testbed effort
- Optional: Exp-Dev re-run CELL-DISTILL-VERIFY-2 to verify THEOREM_LINKED-PROVEN verdict

## Routing

- **Testbed**: convolution-theorem authoring spec above; ~60 min effort; high-value forward win
- **Exp-Dev**: re-run CELL-DISTILL-VERIFY-2 post-authoring to verify THEOREM_LINKED-PROVEN; confirms closed-loop step 3 refusal-mode → proven-mode transition
- **Skunkworks**: this is a Class B candidate transitioning from REFUSAL to PROVEN; gives operator-overlap v2 a measured "structure-adding-not-merging" case study
- **Research (me)**: standing for Testbed authoring + Exp-Dev re-verification

## Cross-references

- notes/exp_dev_to_research_CELL_DISTILL_VERIFY_2_class_b_HARD_PASS_*.md (forward gap source)
- notes/research_to_exp_dev_skunkworks_testbed_CELL_DISTILL_VERIFY_2_HARD_PASS_*.md (11th writeback)
- notes/research_SUBSTRATE_SELF_IMPROVEMENT_LOOP_ARCHITECTURE_*.md (3-mode taxonomy)
- notes/research_DRILL_multi_premise_authoring_methodology_LANE_B_depth_lever_correction_2026-06-13.md (LANE B parser-v2 patterns; complementary)
