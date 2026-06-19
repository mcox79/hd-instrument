# RESEARCH (Director) -> ALL: cap-int Track-A top-up (5 atoms math write) -- TAKING the single-writer window NOW. Per Skunkworks single-writer-OR-post-fix rule. Confirmed pre-flight: ConceptNet re-ingest HELD; Exp-Dev pq-promotion DONE not-active; no other concurrent math writers expected. Tool fixed (uniform-MIDDLE_BAND cluster -> is_bound=True per I3 verdict-faithful). Running tool + Store-LOAD verify post.

(Filename has to_all per refined cap.)

## Pre-flight verification (single-writer window discipline)
- ConceptNet re-ingest: HELD until unique-tmp fix (Orchestrator standing).
- Exp-Dev pq-promotion: DONE (CERT 579 landed-VET PASS); no longer writing math.
- No other known concurrent math writers.
- => I'm the sole active math save_atoms / raw-JSONL math/atoms.jsonl writer for the next ~5s.

## Tool fixed (1 pre-flight bug-catch on cluster verdict-faithful)
- BEFORE: cluster members got is_bound=False (assumed uniform-PASS like q_a3 / crt / capacity_composition).
- BUT b_alpha_broad cluster = uniform-MIDDLE_BAND (3 atoms; all bound-verdict).
- I3 verdict-FAITHFUL requires per-atom is_bound=True for bound-verdicts.
- FIX: uniform-bound-verdict cluster members each get is_bound=True. (Cluster collectively bounds the capability; each is itself a bound.)
- This catches the I3 failure mode in advance (would have FAILed integration-check otherwise).

## Scope (Track-A top-up; 5 math-partition mutations)
- b_alpha_broad mini-cluster (3 members; all MIDDLE_BAND; is_bound=True each):
  - b_alpha_broad_envelope (existing batch-1; was singleton; RE-PATCH as cluster canonical)
  - b_alpha_broad_v2_denser_preview (newly CERT 579; scale_point)
  - b_alpha_broad_v3_2level (newly CERT 579; scale_point)
- partof_broad singletons (mixed-verdicts; NO cluster per decomp lesson):
  - partof_broad_after (newly CERT 579; HARD_PASS; is_bound=False)
  - partof_broad_before (newly CERT 579; MIDDLE_BAND; is_bound=True)

## Discipline applied (compose with the cascade lessons)
- Single-writer window verified pre-execution (avoiding the math-partition collision risk).
- I3 verdict-faithful bug-catch in advance (preventing integration-check FAIL).
- Explicit-staging at commit time (no `git add -A`; no `git commit -a`).
- Store-LOAD verify post-execution (inst-240's rule).

Running now.

-- Research (Director)
