# Pre-reg: exp_read_grow_relation_identity_v3_richness_sweep (CORPUS-SCALE TIER-1 vs GENUINE TIER-3)

Cell: `experiments/exp_read_grow_relation_identity_v3_richness_sweep.py`
Trigger: Skunkworks landed-VET on v2 (commit d232a06ab), explicit expansion criterion (verbatim): "vary
corpus richness (more known relations / more co-occurrence opportunities) while holding the same defeat-pair
construction, to test whether the ~27% failure rate is genuinely corpus-scale-sensitive (supporting the 'not
yet Tier-3' read) or persists even as the corpus grows (which would start to look more like the Tier-3
bound)." Also per the VET note that ORDER_PAIR separates via two co-varying axes (order+co-occurrence), not
order alone -- v3 keeps COOCCUR_PAIR-style single-axis isolation for the richness axis (co-occurrence only;
DEFEAT_PAIR's argtype and order-consistency stay fixed=True throughout, held identical to v2).

## Prior-work check
`bash tools/substrate_query.sh "relation identity corpus richness co-occurrence context sweep failure rate"`
-> top hits at cosine 0.30-0.32: (1) a mycorrhizal-drill prediction about LLM context-richness correlating
with contradiction-rate (different domain, LLM prompting not structural-signature grounding); (2) same doc
chunk; (3) generic WordNet "co-occurrence" term. None concern the read-grow relation-identity structural
mechanism. NOT a rediscovery. This cell is also a direct, Skunkworks-VET-mandated expansion of
`exp_read_grow_relation_identity_v2` (commit d232a06ab), which itself carries v1's already-established
novelty verdict (cosine 0.31-0.33, genuinely novel) -- same mechanism class, no fresh substrate-KB query
needed beyond the one just run (per the same discipline v2's own pre-reg used).

## Design (richness axis, verified empirically via self-test against the REAL FoundationStore before
authoring the pre-reg's decisive-read claims -- see module docstring for the full derivation)

Holds v2's DEFEAT_PAIR construction (vorbs, dringles) BYTE-IDENTICAL: same argument pairs, same sentences,
same fixed-order pattern, same initially-empty co-occurrence. Sweeps ONLY the surrounding corpus richness.

**Richness operationalization:** a neutral, pair-identity-INDEPENDENT rule -- canonical ALPHABETICAL
enumeration of all C(5,2)=10 unordered pairs over the fixed 5-animal vocabulary (bird,cat,cow,dog,frog),
decided before any richness-specific tuning. At richness level N, the first N pairs of this list each get a
dedicated background relation (`bg_p1..bg_pN`), grown via the SAME CONFIRM_K=3 pipeline as every population
relation (no special-cased shortcut -- ordinary single-pair fixed-order new relations, same style as
krendles/shleps).

5 levels (cumulative N out of 10): NONE(0, byte-identical to v2) / MINIMAL(1) / SPARSE(3) / MODERATE(6) /
RICH(10, full pair-space coverage -- both of vorbs's and both of dringles's argument pairs are covered by
RICH, satisfying the HONEST GUARD that neither defeat-pair relation is permanently excluded from a fair
chance to separate).

## Bands (pre-committed BEFORE running -- dual-hypothesis contract; MEASURED results below are the actual
landed numbers, verified via self-test first, then smoke, then full, all three landing identically since the
discriminator is deterministic given the corpus)

- **BASE CONTROLS** (required at ALL 5 richness levels): ablation_population_separated_frac==0.0 always
  (required negative control never fires); all population + background relations legitimately grow, facts
  land in store; violation-reject + K=3-threshold (trelps) regression controls hold; richness=NONE
  reproduces v2 EXACTLY (Gate D positive control: 11/15 separated_full, 0.0 ablation, ORDER_PAIR and
  COOCCUR_PAIR separate, DEFEAT_PAIR collides); failure_rate is monotonically NON-INCREASING across the 5
  ordered levels; interleave-order robustness holds at every level. Any violation -> HARD_FAIL
  (result_class=BROKEN_OR_REGRESSED).
- **HARD-PASS / result_class=CORPUS_SCALE_TIER1_FIXABLE:** base controls hold AND failure_rate(RICH) <
  failure_rate(NONE) (strict decrease) AND DEFEAT_PAIR separates under FULL by RICH on every seed. Supports
  "not yet Tier-3 -- a corpus-scale identity gap the SAME structural mechanism closes with more
  differentiating co-occurrence evidence."
- **HARD-PASS / result_class=GENUINE_TIER3_MEANING_WALL:** base controls hold AND failure_rate(RICH) ==
  failure_rate(NONE) (zero improvement across the full sweep, including at 100% pair-space coverage) AND
  DEFEAT_PAIR does NOT separate under FULL at RICH on any seed. Supports "structure is categorically
  insufficient no matter how much differentiating evidence accumulates."
- **MIDDLE_BAND / result_class=AMBIGUOUS_PARTIAL_RESOLUTION:** base controls hold but the curve is neither a
  clean strict-decrease-with-DEFEAT_PAIR-resolution nor a clean flat-plateau-with-DEFEAT_PAIR-persistence
  (e.g. other pairs resolve but DEFEAT_PAIR specifically does not, or seeds disagree on DEFEAT_PAIR's fate at
  RICH). Reported descriptively -- a genuinely interesting partial result per the dispatching contract.
- Neither the exact richness thresholds (1/3/6/10) nor the exact failure-rate values at each level are gated
  to a pre-committed number -- that would be circular (same discipline as v2's population-fraction
  reporting). The curve-SHAPE claims above are the real pre-registered bands.

## Schema-vet fields
- compute_architecture: sequential-CPU. wall < 1s (MEASURED 0.23s smoke, 0.59s full -- discrete logic, tiny
  corpus per level, 5 richness levels x seeds).
- storage_strategy: sharded (one VSA vector per accepted fact, via imported FoundationStore).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true. deterministic_seeding: true
  (fixed int seeds; sorted() vocab; per-seed interleave-shuffle RNG offset by +9000, matching v2; no
  hash()/list(set())).
- real_code_path (F.1): self_test constructs the REAL imported objects (`ie_extract_openvocab`,
  `run_richness_loop` -> `FoundationStore`, `_relation_args_coherent`, `_order_consistency`,
  `_co_occurrence_with_known`) at full-tiny scale and asserts against a hand-derived curve BEFORE any
  dispatch (genuine empirical check, not a tautology -- verified match on first run).
- crlb_n/a: no quantitative noise floor -- discriminator is discrete structural-signature comparison.
  relation_query_acc MEASURED 1.00 at every richness level.
- discriminator-fires gate: verified at self-test, smoke, AND full (identical curve at all three scales,
  since the discriminator is deterministic given the corpus -- DISCRIMINATOR-MUST-SURVIVE-SCALE satisfied by
  path (B), analytical: full = smoke construction with more seeds, no regime change with N).
- arms_differ (META_RULE_AF): FULL vs ABLATION population-signature hashes differ at richness=NONE (verified
  at self-test).
- HONEST GUARD (explicit): RICH level (N=10) covers 100% of the canonical pair space, including BOTH of
  vorbs's and BOTH of dringles's argument pairs -- verified in `all_facts_in_store` / `all_grown_bg` checks
  at every level; neither defeat-pair relation is permanently excluded from a fair chance to separate.

## Result (MEASURED @ data/exp_read_grow_relation_identity_v3_richness_sweep/metrics.json, 5 seeds
[11,23,37,41,53], run_mode=full; IDENTICAL curve at self-test 2-seed, smoke 2-seed, and full 5-seed scales)

**HARD_PASS, result_class=CORPUS_SCALE_TIER1_FIXABLE (claim, VET-pending).**

failure_rate_curve (fraction of 15 population pairs still COLLIDED, NONE->MINIMAL->SPARSE->MODERATE->RICH):
**[0.267, 0.200, 0.000, 0.000, 0.000]** -- i.e. 4/15 -> 3/15 -> 0/15 -> 0/15 -> 0/15 collided pairs.

- richness=NONE (N=0, byte-identical to v2): separated_full=0.733 (11/15), ablation=0.000. Reproduces v2
  EXACTLY (Gate D positive control PASSED). DEFEAT_PAIR (vorbs,dringles) collides, as required.
- richness=MINIMAL (N=1, covers only krendles's pair): separated_full=0.800 (12/15). grims-krendles
  resolves first (krendles's sole argument pair sits at canonical position 1). DEFEAT_PAIR still collides.
- richness=SPARSE (N=3, covers krendles's + shleps's + one of vorbs's two pairs): separated_full=1.000
  (15/15, FULL resolution). DEFEAT_PAIR (vorbs,dringles) SEPARATES here, on every seed -- vorbs's
  co-occurrence set becomes non-empty (touches the newly-added position-3 background relation) while
  dringles's remains empty (its own pairs sit at positions 5 and 10, not yet reached) -- genuinely different
  signatures, not a coincidence of construction.
- richness=MODERATE (N=6) and RICH (N=10, full pair-space coverage): separated_full stays 1.000 (plateau,
  no regression). DEFEAT_PAIR remains separated even once dringles's OWN pairs are also covered (positions 5
  and 10) -- the separation is not an artifact of dringles staying under-covered; by RICH, dringles's
  co-occurrence set is ALSO populated ({bg_p5, bg_p10}), and it remains structurally distinct from vorbs's
  ({bg_p3, bg_p7}) because the specific covering relations differ.

ablation_population_separated_frac_mean == 0.000 at EVERY richness level (required negative control fired
population-wide, all 5 levels -- richness never leaked into arg-type coherence). all_grown_pop_all,
all_grown_bg_all, all_facts_in_store_all, violation_rejected_all, trelps_not_confirmed_all all True at every
level. relation_query_acc_mean = 1.00 at every level. interleave_robust_across_seeds = True at every level,
with interleave_orders_genuinely_differ = True (genuine per-seed variance, not fake determinism, same
discipline as v1/v2). monotonic_non_increasing = True (no richness step made things worse).

**Decisive read: the defeat-pair (and the broader same-arg-type failure cluster) SEPARATES as corpus
richness grows via the SAME structural mechanism (widened arg-type + order-consistency + co-occurrence
signature) -- this is the corpus-scale Tier-1 reading, not the genuine Tier-3 meaning-wall reading. The
mechanism was never structurally incapable of separating vorbs from dringles; it simply had not yet been
given differentiating evidence at v2's corpus scale. A modest richness increment (SPARSE, N=3 out of 10
possible background relations) was sufficient to fully resolve the entire population, including the
specifically-engineered defeat case.**
