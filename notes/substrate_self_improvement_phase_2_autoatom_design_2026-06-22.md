# Substrate self-improvement Phase 2 — autoatom design

**Date:** 2026-06-22 (Director pre-design while Phase 1 v2c is running on remote_cpu)
**Status:** design draft; refinable when v2c lands with actual cluster structure
**USER strategic vision:** "Phase 1 substrate self-mapping → Phase 2 autoatom → Phase 3 substrate proposes new mathematics"

## What this is

Phase 2 = the substrate autonomously generates candidate new atoms from the clusters produced by Phase 1 (substrate_self_map_v2c). Phase 1 input is the chain-grade atom set (~447); Phase 1 output (when v2c lands) is a set of clusters where related chain-grade atoms group together based on their substrate-native graph proximity in the full ~200k-relation Store.

Phase 2 question: given a cluster of N related chain-grade atoms, can the substrate identify the **common mechanism/mathematical structure** they share and propose it as a NEW atomic claim?

If yes, Phase 2 IS substrate self-improvement: the substrate is now generating atomic claims about its own structure, not just storing claims given to it.

## Concrete substrate-native mechanism (no LLM forward calls)

```
for each cluster C from v2c output:
  # Step 1 — encode each atom's content into substrate-native HD
  atom_vecs = [char_trigram_encoder(atom.verdict_msg + atom.config_version) for atom in C]
  
  # Step 2 — compute cluster centroid HD (mean of normalized HD vectors)
  centroid = normalize(sum(atom_vecs) / len(atom_vecs))
  
  # Step 3 — identify substrate-native "common features" via trigram contribution
  # For each trigram in the encoder's trigram set, compute its alignment with centroid
  trigram_contributions = {
    trigram: cosine(trigram_HD, centroid)
    for trigram in encoder.trigram_set
  }
  top_k_trigrams = top_k_by_value(trigram_contributions, k=20)
  
  # Step 4 — decode top trigrams back into candidate pattern name
  # Use frequency analysis: which n-grams (n=4-12 chars) are most over-represented
  # in atoms of C vs all-other atoms?
  candidate_pattern_name = extract_overrepresented_ngram(C, all_other_atoms)
  
  # Step 5 — novelty check (substrate-native)
  # Does candidate_pattern_name already exist as an atom name? Use KGStore retrieval.
  if KGStore.retrieve(candidate_pattern_name).max_score < refuse_threshold:
    # Novel; propose
    yield CandidateAtom(
      name=candidate_pattern_name,
      kind="META_PATTERN",
      tier="T3",
      cert_status="proposed_by_autoatom",
      pq="PROPOSED_AUTOATOM",
      subsumes=[atom.id for atom in C],
      evidence_count=len(C),
      cluster_id=cluster_id_of(C),
      proposal_ts=now(),
      proposal_provenance="phase_2_autoatom_v1",
    )
```

## Discriminator (Fix #16) — autoatom can't just propose anything

Subsumption strength must be discriminating:
- HARD_PASS: candidate atom name appears in ≥80% of atoms in cluster C AND in ≤5% of atoms outside C (cluster-internal coverage × cluster-external selectivity).
- HARD_FAIL: candidate name in <40% of cluster OR >20% of non-cluster (noise; subsumes nothing meaningful).
- MIDDLE_BAND: in between (autoatom can't subsume confidently; refuse to propose).

## Cert-trail discipline

Proposed atoms go to **PROPOSED_AUTOATOM** pq (NOT chain_grade, NOT axiom). They're candidates pending Skunkworks audit. The Director can then:
1. Inspect the proposed atom + cluster + subsumption evidence
2. Decide whether to dispatch a cell that empirically tests the proposed pattern (the pattern becomes a hypothesis: "if this pattern is real, then cell X should land HARD_PASS")
3. After cell lands, route to Skunkworks for chain-grade adjudication of the PROPOSED_AUTOATOM atom

This keeps autoatom honest: it proposes, doesn't certify. Cert-discipline preserved (A5 strict role separation).

## Phase 3 link

Phase 3 = substrate-proposes-new-mathematics. Activates when autoatom proposals start being chain-grade-promoted. The substrate is then generating atomic claims that, after empirical testing, pass cert-discipline — i.e., the substrate has just produced new mathematics about its own structure.

This is qualitatively different from a human writing the cell + atomizing the result. The substrate identifies the question (autoatom proposal) and answers it (cell tests it). Human is in the loop to dispatch the cell but not to formulate the hypothesis.

## Dependencies & gating

- **v2c HARD_PASS or MIDDLE_BAND with ≥2 clusters**: green-light Phase 2 cell author
- **v2c HARD_FAIL** (full Store ingest gives no meaningful cluster structure): Phase 2 deferred; substrate self-mapping needs further mechanism work before autoatom is plausible
- **v2c chain-grade**: Phase 2 cell becomes immediate next priority

## Implementation cost estimate

Phase 2 cell (autoatom v1):
- ~400-600 lines (smaller than typical because reuses hdlab/ primitives extensively)
- Smoke: ~30s on laptop CPU (small synthetic cluster)
- Full: ~5-15min on remote_cpu (real v2c clusters; depends on N clusters)
- Discriminator-discriminating regime: clusters must have ≥3 atoms (smaller clusters are noise)

## Risks

1. **Char-trigram encoding may be too shallow** — atom verdict_msg + config_version aren't necessarily the right content to encode for pattern identification. Refinement: encode the FULL cert_ledger row for each atom (verdict + cell-source-fragment + atomized_by + pre-reg-bands).
2. **Subsumption test may not discriminate** — clusters may be too similar OR too different on the surface text. Mitigation: HARD bands per discriminator above; refuse to propose if not discriminating.
3. **Phase 2 may not produce novel atoms** — if the substrate's self-map clusters are just "atoms by corpus" or "atoms by date" (mechanical groupings), autoatom proposals will just be tautologies. Mitigation: novelty check (Step 5) refuses tautological proposals.

## Composes with

- hdlab/char_trigram_encoder (encoding step)
- hdlab/kg_traversal.KGStore (novelty retrieval)
- hdlab/multi_hop (chain candidate name expansion to related concepts)
- substrate_self_map_v2c (Phase 1 → Phase 2 input)
- USER strategic vision (Phase 3 path)
- Cert-discipline (A5 strict separation; autoatom proposes, Skunkworks certifies)

## What this does NOT need

- LLM forward calls (substrate-only-decode gate preserved at every step)
- New hdlab/ primitives (uses existing 8/8 backlog-closed primitives)
- Additional research drills (mechanism is concrete + substrate-native; the question is whether v2c clusters HAVE meaningful structure to mine)

— Director (pre-design draft; refinable post-v2c-landing)
