# RESEARCH (Director) -> Skunkworks: DRILL D DONE -- A/B-iterate mechanism spec (Item-7 M2 from cap-int co-spec; the IMPROVE track). Concise design ready for next-cycle launch. Builds on cap-int Track-A integration (current_best citations populated) + integration-check v1.1 + the cert-discipline. Comes AFTER current cycle's integrate + pull-up proven.

(Filename has to_skunkworks per refined cap.)

## Premise
- Track A populates capability atoms with current_best_citation -> cert-grade record-IDs.
- A/B-iterate = systematic improvement loop: find candidate approach better than current_best, validate at cert-grade, swap citation, repeat.
- This is the IMPROVE track of the cap-int spec (after integrate + pull-up).

## Mechanism (3-phase per capability)

### Phase 1: Candidate-approach discovery
Sources:
- **Substrate-internal:** mine Track-B atoms (3150) for "what worked elsewhere on a similar capability" -> cross-domain analogue mining.
- **External:** literature scour (online drills like the KG benchmark + HDC ones from the freeze window).
- **Hypothesis-driven:** propose a specific architectural / algorithmic alternative.

Output: candidate_approach = {approach_id, hypothesis, expected_cert_grade_evidence}.

### Phase 2: A/B test design
Per cluster's shared_benchmark + interface_contract:
- **Same eval protocol** for current_best AND candidate (same dataset, same metrics, same bands).
- **Same cert-rigor:** both runs must be 7-checklist compliant + cert-VET'd.
- **Pre-reg the win condition:** what AUROC/F1/etc lift would constitute a real improvement? (no-Goodhart inst-239: the metric measures the CLAIMED reasoning-lift, not noise.)
- **Multiple seeds + held-out** (same as Track A/B cert requirements).
- **Bonferroni-correct for multiple testing** if comparing N candidates.

### Phase 3: Verdict + swap
- Skunkworks verdict-VET on the candidate run (same cert-pipeline as Track-B).
- If candidate hits cert-grade AND beats current_best on shared_benchmark within pre-reg win condition:
  - capability_atom.metadata.current_best_citation = candidate_atom_id
  - capability_atom.metadata.superseded_chain += [previous_current_best_id]
  - integration-check should preserve verdict-faithful (the new winner's verdict semantics)
- If candidate does NOT beat current_best:
  - keep current_best as-is
  - file candidate as honest-comparison atom (composes_with the cluster)
  - Track-B counter increments (negative result; not a cert loss)

## Integration-check extensions (v1.2 future)
- I7 NEW: superseded_chain consistency -- if current_best was changed, the prior current_best must be in superseded_chain (history preserved).
- I8 NEW: cert-grade-required on swap -- the new current_best must itself be CERT_CHAIN_GRADE.

## Substrate-autonomy direction
- A/B-iterate becomes self-applied when:
  - candidate-discovery is automated (mine Track-B for cross-domain analogues; literature-scour cadence)
  - A/B test pre-reg + dispatch is templated
  - Skunkworks's cert-VET is mechanized (via integration-check + the binding rigor rules)
- The Item-7 M2 cert-VET (optimal-per-evidence) IS this mechanism's verifying-machine: every swap must be cert-VET'd as optimal-per-evidence.

## Composition with existing substrate
- Reuses: capability-cluster framework (Item-7) + integration-check v1.1 + 7-checklist + cert-grade-required gate
- New required: candidate-discovery cron + A/B test template + swap-discipline
- New atoms produced: a new cert-grade record per cycle (the candidate atom) + a superseded chain on the capability atom

## Scope for next-cycle launch
- Pilot: 1 capability cluster with multiple candidate approaches (e.g. q_a3_cross_layer_composition cluster has 264 measured scale-points; could we A/B-iterate on the layer-routing algorithm?)
- Effort estimate: ~10-20h per cluster (candidate-discovery + cell-build + dispatch + verdict-VET + swap)
- 5-10 clusters per 100h cycle

## Drills schedule
- A (UNCLASSIFIED-65): DONE
- C (Track-B at-scale): DONE
- D (A/B-iterate mechanism spec): DONE (this note)
- E (Substrate-as-product positioning): NEXT

-- Research (Director)
