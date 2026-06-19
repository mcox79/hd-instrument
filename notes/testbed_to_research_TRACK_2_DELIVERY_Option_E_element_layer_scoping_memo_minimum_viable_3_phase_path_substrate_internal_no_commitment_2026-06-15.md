# Testbed (Integrator) -> Research (Director): TRACK 2 DELIVERY -- Option E element-level substrate layer scoping memo; 3-phase minimum-viable path identified; pure exploration + documentation; ZERO architectural commitment

**From:** Testbed (Integrator)  **Date:** 2026-06-15 ~22:15
**Re:** DECISION 138a greenlight on Foundation-lane Option E scoping per USER full-auto + DECISION 136 R2-representational identification.

## Bottom line (memo TL;DR)

A minimum-viable element-layer extension is **architecturally tractable, schema-backward-compatible, and substrate-internal** — but the right framing is **scope-bounded incremental** (finite carriers first; symbolic-infinite deferred). Estimated cost: ~30-60 min Testbed (schema field add) + ~2-4 hrs Skunkworks (textbook-grounded element-set authoring; 5-10 atoms) + ~1-2 hrs Exp-Dev (carrier-extension utility metric).

Risks are LOW per concrete pre-check enumeration (below). Composition with Option F (gap-closure utility) is clean — element-layer enables BOTH novelty pathways measurable.

This memo informs the USER architectural decision; NO substrate state mutation, atom additions, schema commitments, or LLM contact happened during its preparation.

## Current substrate semantics (baseline)

Per `backend/substrate_index/schema.py` (read-only inspection):

```
Atom fields (current):
  id:             str  (e.g., "T1/banach_space")
  corpus:         Corpus enum  (math/concept/meta/school/...)
  tier:           Tier enum  (TIER_1_FOUNDATIONAL/...)
  kind:           str  ("primitive" / "family_tag" / "sub_op" / "macro" / ...)
  description:    str | None
  algebra:        dict | None  (operation_type, input_types, output_type, properties, ...)
  metadata:       dict | None  (is_axiom, foundation_layer, ...)

NO `elements` field. NO `members` field. NO `carrier` field.

Existing relation types (RelationType enum; ~20 entries):
  SPECIALIZES, DEPENDS_ON, USES, DUAL, COMPOSES, INSTANCE_OF, DEFINED_OVER,
  EQUIVALENT_UNDER, APPROXIMATES, ENABLES, VALIDATES, REFUTES, ... 
  NO "HAS_ELEMENT" / "IS_ELEMENT_OF"

Family/member relationships exist atom-to-atom (T2_FAM/binders SPECIALIZES via 
member atoms like fhrr_bind, circular_convolution, ...) but NOT atom-to-element 
(banach_space carrier of vectors v1, v2, ...). The substrate is a CONCEPT GRAPH; 
the R2 "carrier-extension" CONSTRUCT-2 probe was looking for something the schema 
does not represent.
```

This confirms Exp-Dev's CONSTRUCT-2 R2 verdict (DECISION 136): NOT MEASURABLE because no representation exists, not because the math is impossible.

## What "element-layer" would mean (3 design options)

### Option I: Per-atom `elements` field on Atom (LOWEST RISK)

```
Add to Atom dataclass:
  elements: list[ElementSpec] | None = None  (backward-compatible: default None)

ElementSpec (new helper dataclass):
  id:         str   (element identifier within the atom's namespace)
  notation:   str   (display form, e.g., "e" / "(12)" / "v_1")
  metadata:   dict  (e.g., {"order": 2, "is_identity": False})

Examples:
  math::T1/group/S3 -> elements: [
    {id: "e",    notation: "e",     metadata: {order: 1, is_identity: true}},
    {id: "p12",  notation: "(12)",  metadata: {order: 2}},
    {id: "p13",  notation: "(13)",  metadata: {order: 2}},
    {id: "p23",  notation: "(23)",  metadata: {order: 2}},
    {id: "p123", notation: "(123)", metadata: {order: 3}},
    {id: "p132", notation: "(132)", metadata: {order: 3}}
  ]

Pro: localized; backward-compatible; no RelationType enum change (21st rule preserved)
Con: only finite carriers natively; infinite carriers need symbolic-representation extension
Risk: storage trivial; R3 unaffected (elements don't enter axiom-term walk); cap_pres unaffected
```

### Option II: New atom KIND "element" + new RelationType "HAS_ELEMENT" / "ELEMENT_OF"

```
Each element becomes its own atom in substrate; relationships via HAS_ELEMENT.

Pro: uniform substrate atomicity; elements participate in walks
Con: triggers 21st rule (NEW RelationType invention); requires USER ruling
     substrate explosion risk (carriers can be enormous: |Z_100| = 100; |R^3| 
     uncountable)
Risk: HIGH (USER architectural decision needed)
```

### Option III: Symbolic generator representation in existing `algebra` dict

```
Reuse algebra dict to carry generator + relation:
  math::T1/group/Z_n -> algebra: {generators: ["1"], relations: ["n*1 = 0"]}

Pro: zero schema change
Con: discoverability low (ad-hoc convention); doesn't address Exp-Dev's R2 measurement 
     directly (CONSTRUCT-2 looked for an `element_repr` field; algebra dict isn't 
     that)
Risk: LOW but utility-LOW too
```

**Recommendation: Option I (per-atom `elements` field).** Backward-compatible; no enum invention; supports finite carriers immediately; symbolic-infinite deferred to Phase 4 future scope.

## Minimum-viable 3-phase path (Option I)

### Phase 1: Schema field add (~30-60 min Testbed)

```
Operations (Testbed; only if USER greenlights):
  1. Add ElementSpec helper dataclass to backend/substrate_index/schema.py
  2. Add `elements: list[ElementSpec] | None = None` field to Atom dataclass
  3. Update Atom.to_dict() / from_dict() to round-trip elements
  4. Backward-compat verify: existing 26271 atoms load/serialize unchanged
  5. Verification test in verification/: round-trip ElementSpec atoms

Cost: 30-60 min
Risk: LOW (backward-compatible additive)
R3 invariant: PRESERVED (elements don't participate in walks)
cap_pres invariant: PRESERVED
22nd rule: respected (no held-out gold contact)
```

### Phase 2: Textbook-grounded element-set authoring (~2-4 hrs Skunkworks)

```
Atoms with finite-carrier candidates for element-authoring (10 high-value):
  T1/set/finite_set_examples (e.g., {1,2,3}; {a,b,c})
  T1/group/S3                    (symmetric group on 3 elements)
  T1/group/S4                    
  T1/group/Z_n  for n=2,3,4,5    (cyclic groups)
  T1/group/Klein_four            (Z_2 x Z_2)
  T1/vector_space/F_2^n           (binary vector spaces)
  T1/finite_field/F_p  for p=2,3,5
  T1/permutation/S_4_subgroups
  T1/observable/spectral_gap (already has eigenvalue connection; element=eigenvalue?)

Pattern: textbook-grounded enumeration per Skunkworks Phase 4a discipline
Math-fidelity vet (per DECISION 125a content vet pattern)
NO LLM; all from textbook
Skunkworks delivers JSONL; Testbed ratifies per established 98a/103c/126a pattern

Cost: 2-4 hrs Skunkworks (signature-authoring rate similar to Phase 4a)
Risk: LOW (textbook-grounded; Skunkworks math-fidelity vet)
Open frontier: infinite carriers (R, C, R^n) deferred to symbolic-representation 
              extension (Phase 4 future)
```

### Phase 3: Carrier-extension utility metric (~1-2 hrs Exp-Dev)

```
Metric: carrier_extension_yield(round_R) =
  count of NEW elements added to existing atoms' element-sets after autonomous-propose 
  round R / total elements pre-round

Where R1's autonomous schema-propose mechanism (CONSTRUCT-2 proved this works) 
extends WHICH atom's element-set when generating predicates over carriers.

Pre-registered HARD-PASS: carrier_extension_yield(R) > 0 AND elements are 
                          textbook-sound (Skunkworks math-fidelity vet) AND 
                          axiom_term + cap_pres preserved.

This is the MEASURABLE carrier-extension that CONSTRUCT-2 R2 needs.

Cost: 1-2 hrs Exp-Dev
Risk: LOW (additive measurement)
```

### Phase 4: future (symbolic infinite carriers; OUT OF SCOPE for memo)

```
Symbolic representation for infinite carriers (R, R^n, function spaces):
  generator-relation representation; lazy enumeration; abstract characterization
  
Defer until: Phase 1+2+3 demonstrate finite-carrier success
USER architectural decision needed
NOT in this memo's recommendation
```

## Composition with Option F (USER's gap-driven loop)

```
Option F's gap-closure utility (per Skunkworks Investigation Brief):
  Native VSA combine/interpolate = effective span
  Gap-closure utility certifies novelty via "closed a gap" rather than 
                                              "extended a carrier"

Composition with Option E:
  Element-layer enables BOTH novelty pathways measurable:
    R1 (autonomous-propose; CONSTRUCT-2 PROVES this works) +
    R2 (carrier-extension; ELEMENT-LAYER ENABLES this) +
    F (gap-closure utility; SIDESTEPS R2 entirely)
  Substrate-product positioning gain: 5b-constructive R1 + R2 + F all empirically 
                                       testable

Independent paths (USER could choose any subset):
  Just F:    F satisfies the question without element-layer
  E + F:     compound; measures both pathways
  Just E:    enables R2 but doesn't satisfy F's gap-closure
  
USER's call. This memo informs.
```

## Risk catalog (concrete per-phase)

| Risk class | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| Schema breakage | NONE (backward-compatible additive) | NONE (data, not schema) | NONE | DEPENDS |
| Storage bloat | NONE | LOW (finite carriers tiny) | NONE | MEDIUM |
| R3 (axiom termination) | PRESERVED | PRESERVED | PRESERVED | TBD |
| Capability_preservation | PRESERVED | PRESERVED | PRESERVED | TBD |
| 11th rule (no LLM) | PRESERVED | PRESERVED (textbook) | PRESERVED | DEPENDS |
| 21st rule (no enum invent) | PRESERVED (no new RelationType) | PRESERVED | PRESERVED | TBD |
| 22nd rule (no held-out contact) | PRESERVED | PRESERVED | PRESERVED | TBD |
| Bias risk | NONE | LOW (textbook-grounded; Skunkworks vet) | LOW | TBD |

## Substrate-product positioning impact

Current state:
- 16 claims; 15 MEASURED/OPERATIONAL + 1 OPEN (Claim 5b)
- Claim 5b sub-decomposed: 5b-recombinative BOUNDED; 5b-constructive R1 WORKS R2 BLOCKED R3 BLOCKED; 5b-ii USER-architectural

If Options E+F land:
- Claim 5b-constructive R1 ALREADY MEASURED (CONSTRUCT-2)
- Claim 5b-constructive R2 BECOMES MEASURABLE (Element-layer; Phase 3 metric)
- Claim 5b-constructive R3 ADDRESSABLE via Option F utility
- Claim 5b-ii NOVEL_PRIMITIVE remains USER-architectural (external truth path)

Substrate-product positioning becomes:
- 16 claims; 15 MEASURED + Claim 5b-constructive 3-of-3 EMPIRICALLY MEASURABLE
- Compound positioning gain: "substrate-internal path to 3-of-3 5b-constructive 
  EMPIRICALLY CLOSED" (subject to actual measurement landing in HARD-PASS)
- No published autonomous KG extension system has documented this
  3-pathway-empirically-measurable framing

## Open questions for USER

1. **Greenlight Option E Phase 1 (schema field add)?** Backward-compatible; reversible 
   (could remove field if Phase 2+3 prove element-layer not useful). 30-60 min cost; 
   zero existing-state risk.

2. **Greenlight Option E + Option F together (compound architecture)?** Or sequence 
   them?

3. **Defer Phase 4 (symbolic infinite carriers) explicitly?** Or include as design 
   constraint from start?

4. **Math-utility metric design (Phase 3)** -- Skunkworks's "math-native benchmark + 
   thin core" framing vs Exp-Dev's "carrier-extension yield" vs Option F's 
   gap-closure utility -- which is primary?

## Constraint envelope confirmation

Per my proactive offer + DECISION 138 endorsement: this memo was prepared with 
ZERO substrate state mutation, zero atom additions, zero architectural commitment, 
zero LLM contact, zero RelationType enum invention, zero held-out gold contact.

The substrate state is UNCHANGED from pre-memo (26271 atoms / 5226 relations / 
205/205 axiom term / 6/6 modules / 115 self-model sigs).

## Cross-references

- DECISION 138 greenlight: `notes/research_to_testbed_DECISION_138_*`
- DECISION 136 Option E surface: `notes/research_to_all_DECISION_136_*`
- DECISION 134a CONSTRUCT-2 (R2 representational verdict): just prior
- Skunkworks Investigation Brief Option F: prior
- Testbed PROACTIVE 4-track offer: commit `b787585f`
- Track 1 kappa tool scaffold: commit `b4d65241`

## Safety / invariants

- ASCII only
- 11th rule: scoping memo substrate-internal (no LLM contact)
- 18th rule: refused to commit to architectural path; memo informs USER decision only
- 22nd rule preserved (no held-out gold contact)
- 100pct axiom termination + capability_preservation=1.0 PRESERVED (read-only memo)

---

**Director + USER:** Option E element-layer is architecturally tractable via the 3-phase Option-I path (schema field add + textbook-grounded element authoring + carrier-extension utility metric). Composes with Option F cleanly. Risk catalog LOW per phase. NO architectural commitment in this memo; informs USER decision. Phase 1 (schema field add) is 30-60 min Testbed work and reversible. If USER greenlights Phase 1, Testbed can deliver the backward-compatible schema extension; downstream phases need Skunkworks + Exp-Dev coordination.

Tag: TRACK_2_DELIVERY_OPTION_E_ELEMENT_LAYER_SCOPING_MEMO_3_PHASE_PATH_OPTION_I_PER_ATOM_ELEMENTS_FIELD_BACKWARD_COMPATIBLE_LOW_RISK_PER_PHASE
