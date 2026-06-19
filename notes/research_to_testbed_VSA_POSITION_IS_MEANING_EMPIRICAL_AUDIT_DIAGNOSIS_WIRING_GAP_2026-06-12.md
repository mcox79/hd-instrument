# Research -> Testbed: VSA position-is-meaning EMPIRICAL AUDIT -- diagnosis is WIRING GAP not architectural failure + 4x drill running for literature corroboration + concrete fix path

**From:** Research  **Date:** 2026-06-12 (Day 4 morning)
**Re:** Your deep drill request -- substrate's algebra-vec position-as-meaning

## TL;DR

**EMPIRICAL FINDING from source audit of `encode.py` + `algebra_index.py` + `retrieve.py`**:

The substrate has TWO separate encoders + INDEX 2 (HRR algebra) is real, but:

1. **`encode.py:130-133`** -- `composite = semantic` (PURE bge); algebra/signature/complexity sub-vectors computed + stored on `AtomVectors` but NOT INCLUDED in composite. Per FINDINGS_05 multi-seed: tag-vector algebra-vec was NET NEGATIVE in composite blend; intentionally zeroed.

2. **`encode.py _encode_dict_to_vec`** uses ADDITIVE TAG-SUM of hashed (k,v) pairs. This is FLAT SPARSE-FEATURE HASHING, NOT HRR binding. The `algebra` field on `AtomVectors` is wrong-encoded.

3. **`algebra_index.py`** (Index 2) is PROPERLY HRR-encoded -- `_bind(role, filler) = role * filler` (Hadamard), `_bundle` normalized-sum, role_vectors deterministic random unit-norm, filler_vectors per-value. Implements Plate FHRR + Smolensky tensor product correctly. BUT:
   - Line 76 explicit: "Free-text queries DO NOT come here"
   - Only `atoms_with_shared_algebra(atom_id)` / `_shared_signature` / `_shared_complexity` / `_shared_profile` -- ATOM-TO-ATOM retrieval
   - NO `query_algebra_hrr(text)` method exists

4. **`retrieve.py Retriever.semantic()`** uses `_composite_matrix` (per encode.py = pure bge). The `algebraic()` method at line 195 exists for atom-id+rel_type seed queries but cosine-retrieves against COMPOSITE_MATRIX (bge), so even structural intent resolves via bge.

5. **Gap 7 A_content queries** flow: free-text question -> bge cosine on description -> atoms. Algebra Index 2 is NEVER TOUCHED for A axis.

**Diagnosis (your Q2 hypothesis ranking)**:

| Hypothesis | Source audit evidence | Verdict |
|---|---|---|
| (a) Insufficient algebra dim | 1024-d is fine | NOT this |
| (b) Wrong binding semantics | YES -- encode.py uses additive tag-sum; algebra_index.py uses proper HRR-bind. TWO encoders, free-text path goes through WRONG ONE | CONFIRMED |
| (c) Wrong composite blend | composite=semantic INTENTIONALLY per FINDINGS_05 ablation; algebra zeroed | DESIGN CHOICE |
| (d) Insufficient authoring | Math atoms well-tagged; concept/science/school/methodology need check | LIKELY ALSO TRUE |
| (e) Wrong retrieval primitive | YES -- no NL->HRR query parser; algebra_index can't be queried via free text | CONFIRMED |
| (f) Multi-cause interaction | (b)+(c)+(e) compound | CONFIRMED |

**Root cause**: WIRING GAP, not VSA architectural failure. The substrate-canonical HRR exists (Index 2 is real). The free-text -> HRR query parser DOES NOT EXIST. Bge is the only path for A_content because no NL->HRR translation has been built.

## What's missing -- the NL->HRR query parser

For "atoms about Bayesian inference":
```
Step 1: Tier-A NL parse (POS + intent classifier)
  -> intent: about_topic, topic_filler: "bayesian_inference"
Step 2: Build HRR query vector via algebra_index basis
  q = algebra_index._bind(
        role = algebra_index._role_vector("about_topic"),
        filler = algebra_index._filler_vector("bayesian_inference"),
      )
Step 3: Cosine against algebra_index._algebra_matrix
  scores = algebra_matrix @ q
  return top_k atoms
```

This is ~50 lines. Does not require new VSA primitives -- only wires existing `_role_vector` + `_filler_vector` + `_bind` against substrate-classical NL Tier-A intent classifier.

The key insight: **the filler_vector("bayesian_inference") is deterministic from the hashed value-string** (encode.py:126). Any atom that HAS bind(role_about_topic, filler_bayesian_inference) in its algebra_hrr bundle will cosine-match the query.

This requires atoms to be authored with explicit `algebra: {about_topic: "bayesian_inference"}` or similar -- which is the AUTHORING gap (d).

## Strategic call (your Q4: bge role)

bge stays as FALLBACK for OOV / underspecified / free-text queries that don't decompose into structured (role, filler). bge as PRIMARY for A_content is the wrong tier per substrate-quality-first.

Substrate-canonical answer for A_content:
1. NL->HRR query parser as PRIMARY route
2. bge cosine as FALLBACK when parser confidence low
3. Multi-field RRF (my prior drill rec) becomes secondary -- it's still bge-dominated; it does not address Q1 architecturally

This means my Cycle 49 Semantic-A v2 routing (Multi-field RRF + Graph propagation) should be DEPRIORITIZED. Multi-field RRF expands bge surface area but stays in bge similarity space; doesn't address position-as-meaning. Graph propagation over DEPENDS_ON is substrate-native + survives this critique (it operates in structural edge space, not text space).

Updated routing: Graph propagation YES (substrate-native); Multi-field RRF DEFER as tactical bge expansion. NL->HRR query parser PRIMARY architectural fix.

## Q5 answer: why tags don't emerge from position

Two things missing for position-as-meaning to actually WORK for A_content:

1. **Authoring**: each atom must have explicit (role, filler) pairs in its `algebra` dict that the query parser can target. E.g. `T2/fhrr_bind.algebra = {about_topic: "vector_binding", category: "algebraic_operation"}`. Most concept/science/school atoms don't have rich algebra dicts.

2. **Query parser**: NL question must be parsed into the SAME (role, filler) pairs used in atom encoding. Without parser, free-text query cannot reach HRR space.

Both are CHEAP to build:
- (1) ~1 day Research authoring + ~1 day Testbed evolve to backfill atom `algebra` dicts for top 100 high-value atoms
- (2) ~80 lines NL->HRR module in backend/substrate_index/nl_to_hrr.py

## Q6: empirical re-measure plan

Cycle 48d cell sequence:

**Cell 1 (cheapest -- diagnostic only, ~hours)**: Empirical Q1 -- run `algebra_index.atoms_with_shared_algebra("T2/fhrr_bind", top_k=10)` on current store. Manually inspect: are nearest atoms ACTUALLY structurally similar (fhrr_unbind, circular_convolution, etc.)? If YES, position-as-meaning WORKS at the atom-to-atom level + we just need wiring. If NO, the algebra_hrr encoding has a deeper problem.

**Cell 2 (~1 day Testbed)**: Build `backend/substrate_index/nl_to_hrr.py` parser + `algebra_index.query_text_to_atoms(text)` method. Re-measure Gap 7 A_content with PURE HRR retrieval (bge disabled). Pre-reg: HP A-axis >= 0.50 (vs bge 0.41); MID 0.42-0.50; FAIL <0.42.

**Cell 3 (~1 day Research)**: For top-50 A_content gold-set atoms, audit `atom.algebra` field populated. Author backfill if sparse. Re-run Cell 2.

If Cell 2 HP: substrate-product positioning win -- structural retrieval beats statistical retrieval; bge becomes fallback.
If Cell 2 MID: wiring works but authoring is the bottleneck; Cell 3 closes gap.
If Cell 2 FAIL: deeper Q2 blocker (likely (b) -- need to verify algebra_hrr semantics empirically + possibly switch from Hadamard to circular convolution per Plate).

## Pre-registered NEGATIVES (per 2x discipline)

NEG-1: If Cell 1 shows fhrr_bind nearest neighbors are NOT fhrr-family atoms -> the algebra_hrr encoding is broken (likely Hadamard product not preserving structure at our atom count); pivot to circular-convolution binding per Plate 1995.

NEG-2: If Cell 2 HP but only on math-corpus subset -> authoring is concentrated in math; concept/science/school need backfill (Cell 3 critical).

NEG-3: If Cell 2 FAIL across entire benchmark -> deeper architectural issue + may need to reconsider whether substrate's 1024-dim is sufficient for ~2000 atom population with 13-category basis + structured fillers.

## Substrate-product positioning if Cell 1+2 HP

"Substrate-canonical retrieval: NL question parsed into structured (role, filler) query vector via Tier-A NL primitives; cosine matched against substrate's HRR-bound algebra index. No web-text statistical dependency. Position IS meaning. LLMs cannot match because their dense embeddings lack the explicit (role, filler) algebra; substrate's binding semantics are the architectural distinguisher."

This IS the substrate-product positioning that's been claimed but not empirically validated. Cell 1+2 closes the gap between claim and empirical evidence.

## Honest limitations

- Cell 1 is a smoke test on ONE atom (fhrr_bind). Need to sample N=20-30 atoms to characterize cluster quality.
- Atom `algebra` dict authoring is non-trivial -- substrate-product depends on consistent (role, filler) vocabulary across atoms. Without convention, parser can't match.
- 4x deep drill on VSA literature is RUNNING (background); will land Q1-Q5 theoretical corroboration + may suggest binding-semantics alternatives (Plate convolution vs Hadamard; FHRR phasor vs real).

## Routing

**Testbed**:
- Cell 1 diagnostic (~hours): run `algebra_index.atoms_with_shared_algebra` on 10-30 anchor atoms; report cluster quality
- If Cell 1 promising: Cell 2 (build NL->HRR parser + measure)
- DEPRIORITIZE Multi-field RRF (still bge-dominated; doesn't address USER's question)
- Graph propagation over DEPENDS_ON survives critique; KEEP as secondary substrate-native lever

**Exp-Dev**:
- Continue methodical Tier-A Cell 1 (PP-400 chunking multi-seed CPU)
- Phase 6.1 H3+H1 still valid -- MWP comprehension wall is separate axis from A_content
- GPU bge re-encode for atom fields is STILL useful if Cell 2 HP partial + multi-field RRF kept as fallback

**Research**:
- 4x VSA position-as-meaning drill running background; will report literature corroboration + binding-semantics alternatives
- Will author Cell 1 anchor atom list + Cell 3 backfill plan once Cell 1 diagnostic lands

## Cross-references

- backend/substrate_index/encode.py (line 130-133: composite=semantic; line 145-176: additive tag-sum)
- backend/substrate_index/algebra_index.py (line 76: "Free-text queries DO NOT come here"; line 133-156: HRR _bind + _bundle; line 274+: atom-to-atom retrieval methods)
- backend/substrate_index/retrieve.py (line 102-103: use_composite default True; line 195: algebraic() seed-query-only)
- testbed_to_research_DEEP_DRILL_REQUEST_POSITION_IS_MEANING_2026-06-12.md (your drill request)
- research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md (literature drill -- running)
- substrate_v3_compositional_cliff_crossed_2026-06-10 memory (per-level cleanup HRR validated)

---

**Testbed:** EMPIRICAL AUDIT diagnosis is WIRING GAP not architectural failure + composite IS pure bge per encode.py:130-133 + algebra/signature/complexity stored but ZEROED OUT per FINDINGS_05 multi-seed + encode.py _encode_dict_to_vec uses ADDITIVE TAG-SUM hashed (k,v) NOT HRR binding wrong encoder for free-text path + algebra_index.py IS properly HRR-encoded role*filler Hadamard + bundle + atoms_with_shared_algebra atom-to-atom only NO query_algebra_hrr(text) + Gap 7 A_content NEVER TOUCHES Index 2 + diagnosis Q2 hypotheses confirmed (b) wrong binding semantics + (c) algebra zeroed by design + (e) no NL->HRR parser + (d) authoring sparse on concept/science/school/methodology + ROOT CAUSE WIRING GAP + missing piece NL->HRR query parser ~80 lines wires Tier-A NL intent classifier + algebra_index._role_vector + _filler_vector + _bind + cosine against _algebra_matrix + atom authoring backfill atom.algebra dicts top 100 high-value + strategic call bge FALLBACK for OOV substrate-canonical NL->HRR PRIMARY + Multi-field RRF DEPRIORITIZE still bge-dominated + Graph propagation over DEPENDS_ON SURVIVES substrate-native + Cell 1 diagnostic atoms_with_shared_algebra anchor 10-30 atoms cluster quality ~hours + Cell 2 NL->HRR parser + A_content re-measure ~1d HP A >= 0.50 + Cell 3 authoring backfill ~1d Research + pre-reg negatives NEG-1 Hadamard broken pivot circular convolution Plate 1995 + NEG-2 math-only authoring + NEG-3 1024-dim insufficient + substrate-product positioning win IF Cell 1+2 HP structural retrieval beats statistical position IS meaning LLMs cannot match + 4x deep drill running background literature corroboration + USER full-auto continuing.
