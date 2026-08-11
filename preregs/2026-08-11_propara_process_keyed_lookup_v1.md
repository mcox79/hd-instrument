# Pre-registration: exp_propara_process_keyed_lookup_v1

**Filed by:** exp_dev, 2026-08-11. **Task source:** director spawn -- validate the FOUNDATION FORM
(per-(entity,process)-keyed EXACT lookup) with ZERO LLM, before any Rubicon crossing. Audit finding:
the binding wall is STRUCTURAL -- the hand-vetted KB
(`data/benchmark_trap_check/propara_process_physics_kb_v1.json`) is a FLAT, UNKEYED bag per role
(`{combustion: consumes:[wood,oxygen,coal...], produces:[ash,smoke...]}`), so `water` recurs across
many processes' lists and no fuzzy/graded/completion operator disambiguates (v1 completion HARD_FAIL
e97a1437b; learned binder HARD_FAIL 50b8d8751 -- both hit the promiscuity wall, pair-precision 0.079).
HYPOTHESIS: the fix is PER-(entity,process)-KEYED facts + process-conditioned EXACT lookup.

## Prior-work check (SUBSTRATE-KB)
Inherits the arc's checks (v1 prereg: `pattern_completion` registry + "Partial Slot Filling" design
note, both < 0.35). `hd_fact_store` (`hdlab/hd_fact_store.py`) is WIRED (banked, substrate-native
fact store + source-trust ingest-vet). Novel: re-keying the flat process KB into per-(entity,process)
fate triples in hd_fact_store + process-conditioned exact lookup as the ProPara binder. Not a
rediscovery; also validates hd_fact_store for this content (wire-don't-island).

## THE ONE VARIABLE
Same KB CONTENT, no new knowledge, no LLM. Swap ONLY the binder OPERATOR: fuzzy graded/completion
matching over the flat role-bag (v1's promiscuous arm = the ABLATION) -> EXACT per-(entity,process)
keyed lookup. Selection (which process is cued) stays the SAME validated convergence gate (26x).

## Re-keying (deterministic, no LLM, no new facts)
For each process P and each entity e: e in P.consumes -> (e, P) -> DESTROY; P.produces -> CREATE;
P.moves -> MOVE. Stored as triples (subject=e, relation=`fate_in_<P>`, obj=FATE, source=
`propara_physics_kb_v1`, trust=TRUST_HIGH) in the owned `hdlab.hd_fact_store.HDFactStore` (all
`fate_in_<P>` relations MULTIVALUED, since an entity can be both produced and moved in a process,
e.g. heat/smoke in combustion). The arm's lookups go THROUGH the store (query(e, `fate_in_<P>`)) so
the store is genuinely load-bearing/validated, not decoration; a plain re-keyed dict mirror is kept
for the structural coverage/residual questions and cross-checked bit-equal to the store in self-test.
Entity keys are normalized identically to the promiscuous arm (`_norm_toks` singular/plural variants)
so the ONLY difference is exact-vs-graded, not normalization.

## NEW ARM `with_keyed_lookup`
Per paragraph, the convergence gate selects process(es); for each NAMED participant, for each
selected process P, EXACT keyed lookup (participant-token, P) -> FATE(s) via the store; bind that
fate into the bridge dict (effect + its `_ROLE_EFFECT` trigger-verb-classes -- bit-identical
downstream `_grids` contract to every other arm). Fuzzy/graded/completion binding is REPLACED by
discrete process-keyed lookup.

## Compare (per-arm, VET-hard, do NOT aggregate)
`with_keyed_lookup` vs `with_promiscuous_completion` (v1 flat-KB graded/completion, pair-precision
0.079 = the ablation) vs `with_oracle` (ceiling +0.075) vs `without_knowledge` (floor), on the
ProPara unmentioned subset: official-metric F1 + pair-precision/recall.

## Controls (all load-bearing)
- SCRAMBLE: per-process permutation of the entity->fate keying (each entity gets a WRONG entity's
  fate within the same process, deterministic hashlib-seeded via `_deterministic_perm`; coverage +
  process-selection held identical so the scramble isolates the KEYING signal). Keyed lookup MUST
  collapse toward the floor -> the entity->fate keying carries the signal.
- ABLATION = the promiscuous flat arm (`with_promiscuous_completion`).
- NO-LEAK: only the hand-vetted KB + paragraph text/participant list are read; gold fates are NEVER
  read to build or query the store.
- HELD-OUT ENTITIES: DEV participants whose surface is NOT in the KB entity vocabulary -> keyed
  lookup cannot fire by construction -> measures the COVERAGE GAP honestly (report keyed precision/
  recall on in-KB vs held-out subsets).

## Residual decomposition (the key diagnostic; over DEV oracle-fact participants)
Classify each participant with a gold unmentioned fact as RECOVERED, or error-type:
- COVERAGE: none of the participant's tokens is in the KB entity vocabulary (entity NOT in KB).
- GATE: entity IS in the KB but not under any GATE-selected process (wrong process selected).
- FORM: entity IS present under a selected process (lookup returns a fate) but the fate is WRONG vs
  gold (the per-entity-keyed FORM itself is insufficient).
Report the fractions + the KB-coverage fraction of dev-fact participants (= seed-size / growth signal).

## Pre-registered bands
- `KEYED_BEATS_PROMISCUOUS_MARGIN = 0.05`: HARD-PASS requires keyed pair-precision >= promiscuous
  pair-precision + 0.05 (a real margin toward oracle), measured live (promiscuous ~0.079).
- `SCRAMBLE_MAX_RETAINED_FRACTION = 0.50` and scramble pair-precision <= 0.5 * keyed pair-precision.
- Residual COVERAGE-dominated: among non-recovered oracle-fact participants, COVERAGE fraction >
  FORM fraction.
- `LEAK_CEILING = 0.95`, `LEAK_ORACLE_MARGIN = 0.02`, `WITHOUT_COLLAPSE_CEILING = 0.60` (reused).
- HARD_PASS = beats promiscuous meaningfully AND scramble collapses AND residual COVERAGE-dominated
  (form validated, remaining problem is coverage the LLM-seed + reading-growth fill). HARD_FAIL =
  keyed does NOT beat promiscuous even for in-KB entities, OR scramble does not collapse (form fix is
  not the answer) -- report precisely, with the decomposition. MIDDLE_BAND = beats + scramble-clean
  but FORM-dominated residual (form only partially validated).

## Cell-template mandates (declared)
arms_differ_verified (6 arms hash-differ); final_metrics_atomicity: tmp_replace; except SystemExit
before except Exception (no bare/BaseException); crlb_n/a (F1 over fixed corpus + exact dict/HD-store
lookup, no noise-floor); HP_SCOPE {with_keyed_lookup: [beats_promiscuous_margin, scramble_collapses,
residual_coverage_dominated, no_leak, arms_differ, decode_ok]}; cardinality_ok (single split, fixed 6
arms); per-unit failure-class (no bare except); calibration_check: default_ok_for_this_regime (exact
lookup + pre-registered bands, no tuned threshold); numbers tagged MEASURED@/HYPOTHESIZED@/
THEORETICAL@/CITED@; self-test builds the REAL re-keyed store over the REAL KB + validates store==dict
+ exercises the arm + residual decomposition; progress_logging: print_flush_true; deterministic_
seeding: true (HDFactStore seeded; scramble via hashlib `_deterministic_perm`; no python hash()).

## Scope discipline
self-test PASS -> the measurement (DEV smoke) -> STOP + report. No --full. No edits to the
frame-activation/MAVEN cells (import only). Targeted commit; branch dataprep/mcguffey-graded-corpus;
no origin push.
