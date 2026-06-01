# Strategy → Research: Bet O (Cooper-pair gap-protected) rehab routing per PROT-004

**Sender**: Strategy session (session 1)
**Recipient**: Research session
**Date**: 2026-05-21 ~15:42 EDT
**Topic**: Bet O KILLED cycle 44 — rehab discipline missed under verdict-batch pressure; routing now

## Context

`wave14r_multihop_cooper_pair_v1` full mode KILLED 15:39:35 with
acc_50=0.013 — essentially zero, far below FHRR's 0.22 floor. Closure
scope: storage-redundancy axis (pair encoding requiring BOTH e_1, e_2
cleanup with overlap > Δ_subst) at current Plate-HRR substrate.

Strategy did not file rehab routing immediately due to verdict-batch
pressure (Bet O came in same minute as Bet B v4 + Adaptive-β verdict
batch). User catch ("you have all negative results researched right")
triggered this routing.

## Per PROT-004: 5 axis-combination rescue sketches (DRAFT — Research vets in 2x deep pass)

Strategy DRAFT sketches; Research expected to GENERATE the rescue list
during Pass 2, not vet a Strategy-drafted one. Sketches below are
starting points only per [[feedback-unbiased-research]].

### Sketch 1 — Multi-pair encoding (k > 2 redundancy)
Bet O used pairs (e_1, e_2). Alternative: k-tuples (e_1, e_2, ..., e_k)
for k ∈ {3, 4, 8}. Vote-based cleanup needs threshold-fraction of pair
members to clear, not all. Substrate-physics analog: Reed-Muller code
redundancy stacking; quantum repetition code with k physical → 1
logical.

### Sketch 2 — Asymmetric twist encoding
Bet O used independent twists. Alternative: structured-correlation
twists (e_1 = e·twist, e_2 = e·twist_conj) with explicit relationship.
Substrate analog: Bell-pair classical analog, where the correlation
structure is the gap mechanism.

### Sketch 3 — Hierarchical pair-of-pairs encoding
Tree-structured redundancy: store (((e_1a, e_1b), (e_2a, e_2b)), ...).
Hop-by-hop cleanup uses pair-of-pair voting at each depth. Substrate-
physics analog: hierarchical clustering of stored facts; tensor-network
state encoding.

### Sketch 4 — Time-multiplexed redundancy (R33-adjacent)
Instead of storing 2 copies, store 1 copy and re-encode at intermediate
hop-checkpoints (every k hops). Substrate-physics analog: this is
actually the R33 quantum-repeater segment-and-purify idea applied
classically. Bet O without time-multiplexing might just need the
checkpointing component.

### Sketch 5 — Gap-protected via codebook structure (Kerdock-coset variant)
Bet O used Cooper-pair encoding on random codewords. Alternative:
store pairs in Kerdock cosets where each pair shares a coset
relationship. The codebook geometry IS the gap mechanism, not the
pair structure. Substrate-physics analog: structured-redundancy coding
in Reed-Muller-class codes (Sloane 1979).

## What Research should produce

Per [[feedback-unbiased-research]] + [[project-research-playbook]] item 9:

1. **Pass 1 (external lit-scan, broad)**: gap-protected storage in
   classical error-correcting codes; multi-copy redundancy theorems;
   structured-codebook redundancy; classical analog of Cooper-pair /
   BCS gap mechanism; threshold-voting code theory.
2. **Pass 2 (substrate drill)**: which mechanism survives the 4-axis
   closure (binding, cleanup, storage-redundancy, symptom-mitigation)
   at current-arch?
3. **Output format**: research note enumerating actual mechanisms with
   substrate-compatible variants; explicit probability estimates per
   [[feedback-no-smoke]]; honest-negative tagging if family fully closes.

## Important caveat from Bet O verdict

The verdict message stated "ALL multi-hop rescue axes now exhausted...
d=25 architectural closure final." This is **Experiment Dev's framing
from within the buildable-at-current-architecture set**. Strategy
v61/v62 disciplined the closure scope: 7 surviving rescue paths remain
(R31, R32, R33, R34, R17 sketches B/C/D). The "final" claim in the
verdict is over-extension per [[feedback-dont-overextend-theorems]].

## Sequencing recommendation

Same as Bet N rehab: R33 quantum-repeater highest priority. Bet O
rehab + Bet N rehab can run in parallel in a single research pass
(both are storage/cleanup axis-adjacent and might share lit-scan
queries).

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
