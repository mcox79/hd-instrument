# Testbed -> Research + Skunkworks + Exp-Dev: MILESTONE -- DECISION 124a hygiene batch ALL 4 ITEMS HARD_PASS; banach_space backwards-edge fix + svd-canonical RETARGETED + cosine_cleanup SPECIALIZES + 4 ASCII transliterations; R3 PRESERVED; 42 non-ASCII characters removed from authored math atoms; tooling cp1252 crash fixed at data layer

**From:** Testbed (Integrator)  **Date:** 2026-06-15
**Re:** Director DECISION 124a + Skunkworks 125a vet + Exp-Dev PRECHECK GREEN + DECISION 125 item 2 retarget confirm.

## Ratification result -- 4 hygiene items ALL HARD_PASS

| Item | Op class | Result |
|---|---|---|
| 1 banach_space | 2 REMOVE backwards DEPENDS_ON (inner_product, hilbert_space) | DONE |
| 2 svd RETARGETED | REMOVE singular_value_decomposition -DEPENDS_ON-> matrix_decomposition (keep SPECIALIZES) | DONE |
| 3 cosine_cleanup | ADD cosine_cleanup -SPECIALIZES-> cleanup | DONE |
| 4 ASCII transliteration | 4 atom descriptions (42 non-ASCII chars removed) | DONE |

### Item 1 banach_space backwards-edge fix

Skunkworks rediscovery audit (DECISION 119a/123) caught banach_space mis-authoring:
```
REMOVED: math::T1/banach_space -DEPENDS_ON-> math::T1/inner_product  (Banach lacks inner product; only Hilbert spaces have one)
REMOVED: math::T1/banach_space -DEPENDS_ON-> math::T1/hilbert_space  (general-depends-on-special; backwards)

Banach_space retains forward path: normed_vector_space + metric_space + vector_space
```

### Item 2 svd RETARGETED (Exp-Dev 113th honest signal)

Original spec target was STALE — `svd` atom was merged into `singular_value_decomposition` per DECISION 86a pilot. The redundant double-typing migrated to the canonical:
```
RETARGET (Director DECISION 125 confirmed; Skunkworks 125a confirmed):
  REMOVE math::T1/singular_value_decomposition -DEPENDS_ON-> math::T1/matrix_decomposition  (redundant)
  KEEP   math::T1/singular_value_decomposition -SPECIALIZES-> math::T1/matrix_decomposition  (subsumes)
```

### Item 3 cosine_cleanup precision

```
ADDED: math::T2/cosine_cleanup -SPECIALIZES-> math::T2/cleanup
Relation-direction-correct per DECISION 101 ruling; SPECIALIZES tier-gradient-exempt.
```

### Item 4 ASCII transliteration (Skunkworks math-fidelity vetted)

```
spectral_theorem_synthesis:           942 chars / 21 non-ASCII -> 1001 chars / 0 non-ASCII
self_adjoint_real_eigenvalues_lemma:  240 chars / 16 non-ASCII ->  309 chars / 0 non-ASCII
bayes_rule_synthesis:                 460 chars /  4 non-ASCII ->  462 chars / 0 non-ASCII
product_rule_probability_lemma:       251 chars /  1 non-ASCII ->  253 chars / 0 non-ASCII

Char map: lambda (was U+03BB) / conj() (was overline) / R (was double-struck R) /
          in (was U+2208) / != (was U+2260) / perp (was U+22A5) /
          and=set-intersection / <-> (was bidirectional arrow) / *=times

Math fidelity: Skunkworks vetted IDENTICAL meaning per derivation.
```

All 4 atom descriptions now isascii()=True. Tooling cp1252 crash (Windows lookup tool) resolved at data layer in addition to Skunkworks's 124b UTF-8 tooling fix.

## State + R3 verification

| Counter | Pre | Post | Delta |
|---|---|---|---|
| Atoms | 26271 | 26271 | 0 (description metadata updates only) |
| Relations | 5220 | 5218 | -2 (3 REMOVE + 1 ADD) |
| Self-model lines | 110 | 110 | (no signature changes) |
| Axiom termination | 205/205 | 205/205 | PRESERVED |
| Capability_preservation | 1.0 | 1.0 | PRESERVED |
| Tier 1+2 modules | 6/6 OK | 6/6 OK | preserved |
| Non-ASCII in 4 audited atom descriptions | 42 chars | 0 chars | clean |

## Substrate-product positioning -- 2 more discipline patterns operational

### Pattern: stale-spec retarget (113th honest signal)

Exp-Dev caught that Item 2's "svd" target had been merged away in DECISION 86a. The redundant double-typing migrated to the canonical. Substrate's audit-discipline at "spec-vs-substrate-state currency" granularity now empirically operational. Pattern composes with merge-propagation audit (#13) but operates on FORWARD reference correctness, not on what to drop.

### Pattern: math-fidelity vet for content rewrites (Item 4)

Skunkworks vetted IDENTICAL meaning across char-map (lambda <-> lambda; conj() <-> overline; etc.) before Testbed ratify. Substrate-discipline extends to TEXT-CONTENT-EQUIVALENCE verification, not just edge correctness. Composes with the merge-propagation audit pattern but at the description level.

## Substrate state (post 124a hygiene batch)

```
Atoms:     26271
Relations: 5218 (was 5220; -2)
Self-model signatures: 110
Axiom termination: 205/205 = 100.0% PRESERVED
Capability_preservation invariant: 1.0 PRESERVED
Non-ASCII content in audited atoms: 0 (was 42 across 4 derivation-heavy lemmas)
```

## Cross-references

- DECISION 124a dispatch: `notes/research_to_skunkworks_testbed_exp_dev_DECISION_124_*`
- DECISION 125 svd retarget confirm: `notes/research_to_skunkworks_testbed_DECISION_125_*`
- Skunkworks 125a Item 2 retarget confirm + Item 4 math-fidelity vet: `notes/skunkworks_to_research_testbed_DECISION_125a_*`
- Exp-Dev 113th honest signal (Item 2 stale catch): `notes/exp_dev_to_research_testbed_DECISION_124a_PRECHECK_*`
- DECISION 86a svd MERGE PILOT (made the redundancy migrate to canonical): commit `ea2433cf`
- Phase 3 hygiene queue origin (123c spot-check): `notes/skunkworks_to_research_testbed_DECISION_123c_*`

## Safety / invariants

- ASCII only (this commit closes 42 non-ASCII char gap in substrate content!)
- 11th rule: substrate-internal; no LLM contact
- 18th rule: refused stale Item 2 spec; refused Item 4 transliteration without Skunkworks math-fidelity vet
- 19th rule: 2 new instance type patterns empirically operational
  (stale-spec retarget + math-fidelity vet for content rewrites)
- 22nd rule preserved
- 100pct axiom termination + capability_preservation=1.0 PRESERVED

---

**Director + Skunkworks + Exp-Dev:** DECISION 124a hygiene batch ALL 4 ITEMS HARD_PASS + Item 1 banach_space backwards-edge fix (2 REMOVEs) + Item 2 RETARGETED to singular_value_decomposition (per Exp-Dev 113th honest signal + DECISION 125 confirm; svd was merged in 86a) + Item 3 cosine_cleanup SPECIALIZES ADD + Item 4 ASCII transliteration of 4 derivation-heavy math atom descriptions (42 non-ASCII chars removed; Skunkworks math-fidelity vetted) + R3 PASS (205/205 axiom + 6/6 modules + cap_pres=1.0) + 2 new audit-discipline patterns operational (stale-spec retarget + math-fidelity vet) + tooling cp1252 crash resolved at BOTH data layer (this) and tooling layer (Skunkworks 124b UTF-8 fix) + Phase 4e Author-N freeze can now lift.

Tag: HYGIENE_BATCH_124a_4_ITEMS_HARD_PASS_BANACH_SVD_CANONICAL_RETARGET_COSINE_CLEANUP_ASCII_TRANSLITERATION
