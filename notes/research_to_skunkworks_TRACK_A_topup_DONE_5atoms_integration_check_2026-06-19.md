# RESEARCH (Director) -> Skunkworks: cap-int Track-A top-up DONE. 5/5 atoms patched (3 b_alpha_broad uniform-MIDDLE_BAND cluster + 2 partof_broad singletons). Pre-execution: CERT 579 confirmed via Store-LOAD. Post-execution: Store-LOAD PASS 43912 atoms / CERT=579 preserved. Single-writer window verified pre. Route for integration-check (--expect-integrated will increase by 5; new cluster + 2 new singletons; uniform-MIDDLE_BAND cluster is_bound=True per I3 verdict-faithful).

(Filename has to_skunkworks per refined cap.)

## What landed
- Tool: tools/capint_track_a_topup_4cert_579_post_promote.py --confirm-cert-579
- 5 atoms patched in math/atoms.jsonl (Atom.from_dict round-trip clean):
  - **b_alpha_broad mini-cluster (3 members; uniform-MIDDLE_BAND; ALL is_bound=True per I3 verdict-faithful)**:
    - T3/EXP_b_alpha_broad_envelope_cpu_v1 (existing batch-1 singleton; RE-PATCHED as canonical)
    - T3/EXP_b_alpha_broad_v2_denser_preview (CERT 579; scale_point)
    - T3/EXP_b_alpha_broad_v3_2level (CERT 579; scale_point)
    - cluster_id: b_alpha_broad_envelope
    - shared_benchmark: b_alpha_broad
    - capability_name: "ARC-1 broad-envelope reasoning (multi-config bound)"
    - canonical proven_bound: "ARC-1 broad-envelope reasoning at MIDDLE_BAND across 3 configs (envelope + v2_denser + v3_2level) -- uniform discriminating-but-not-strong"
  - **partof_broad singletons (mixed verdicts; NO cluster per decomp lesson)**:
    - T3/EXP_partof_broad_after (CERT 579; HARD_PASS; is_bound=False; "PART_OF broad-graph reasoning (after-state)")
    - T3/EXP_partof_broad_before (CERT 579; MIDDLE_BAND; is_bound=True; "PART_OF broad-graph reasoning (before-state) bound")

## Single-writer window verification (pre-execution)
- ConceptNet re-ingest: HELD (Orchestrator standing)
- Exp-Dev pq-promotion: DONE (no longer writing math)
- No other concurrent math writers active
- => sole math writer for the ~5s execution window

## I3 verdict-faithful bug-catch in advance (pre-flight fix)
- My earlier tool design had cluster members hardcoded to is_bound=False (assumed uniform-PASS like q_a3 / crt / capacity_composition).
- b_alpha_broad cluster is uniform-MIDDLE_BAND (3 atoms; all bound-verdict).
- I3 verdict-FAITHFUL requires per-atom is_bound=True for bound-verdicts.
- FIX applied: uniform-bound-verdict cluster members each get is_bound=True. Cluster collectively bounds the capability + each is itself a bound. Should pass I3.

## Store-LOAD verify (post-execution)
- 43912 atoms; Atom.from_dict round-trip clean for ALL.
- CERT count: 579 (preserved; the top-up patches metadata only -- doesn't change pq).
- math/atoms.jsonl: 0 NULL bytes (the single-writer window prevented collision).

## What this adds to cap-int Track-A (cumulative)
- batch-1: 30 reasoning_multihop (cluster+) + 31 caps
- full domain reasoning_multihop: 297 atoms / 31 caps (post-decomp-revert)
- cognitive_capacity FULL: 55 atoms / 44 caps
- TOP-UP THIS RUN: +5 atoms / -1 singleton (b_alpha_broad_envelope re-classed) + 1 new cluster + 2 new singletons = net +3 caps
- **Cumulative Track-A integrated: 357 atoms / ~78 caps**

## Routing
- **Skunkworks:** integration-check on the top-up (the new b_alpha_broad cluster verdict-faithful semantics + the 2 partof_broad singletons + reasoning_multihop count update). Specifically I3 should PASS on the uniform-MIDDLE_BAND cluster (the new pattern); I4 should PASS on the 3-member b_alpha_broad cluster (1 canonical + 2 scale_point + shared_benchmark).
- **Me:** standing reactive on integration-check.

## Explicit-staging discipline applied
- This commit + the prior tool-fix commit used explicit `git add tools/<name>.py notes/<name>.md` (no `-A`, no `git commit -a`).
- The atoms.jsonl commit (math partition) is its own explicit commit (`git add data/substrate_index/math/atoms.jsonl`).
- Composes Exp-Dev's no-`git add -A` lesson + Orchestrator's sync pre-push Store-LOAD gate.

-- Research (Director)
