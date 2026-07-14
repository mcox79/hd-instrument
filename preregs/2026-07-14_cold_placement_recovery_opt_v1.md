# Pre-reg: cold_placement_recovery_opt_v1

Cell: `experiments/exp_cold_placement_recovery_opt_v1.py`
Design source: optimize-to-frontier follow-up on `experiments/exp_cold_placement_usefulness_v1.py`, which landed
MIDDLE_BAND (`data/exp_cold_placement_usefulness_v1/metrics.json`: name-transparent exact=0.1488, opaque-gloss
exact=0.0382, both above 0% floors but below the pre-registered HARD-PASS bars). Director task: determine
METHOD-LIMITED (fixable) vs FUNDAMENTAL via (a) a stronger recovery method and (b) a relation-level metric.

Prior-work check (`tools/substrate_query.sh`, mandatory before authoring): query "cold placement optimization
relation-level top-k anchor recovery wordnet sense disambiguation" -> top hit cosine=0.3594 ("disambiguation",
generic-token match on the word "disambiguation" against an unrelated atom/wordnet-cache entry, NOT a prior cell
on this optimization). NONE at cosine>0.30 that is a genuine rediscovery. This cell is NOVEL (first optimize-to-
frontier pass on the base cell's MIDDLE_BAND result).

## Question
Is the base cell's modest recovery magnitude METHOD-LIMITED (a stronger recovery method + a less-strict but
task-relevant metric reveal more signal) or FUNDAMENTAL (the ceiling holds regardless of method)?

## Two optimization axes
1. STRONGER RECOVERY METHOD: beyond WordNet-lemma-match-only, add (a) FULLER lexical content per cold entity --
   WordNet SYNONYMS + HYPERNYMS + full DEFINITION text (not just one cached gloss sentence), pre-computed once
   interactively in .venv (nltk 3.9.4 local corpora) directly over this cell's own ~600-entity population and
   committed at `data/exp_cold_placement_recovery_opt_v1/provenance.json` (568/600 = 94.7% resolved,
   MEASURED@that file, vs the base cell's 68.56% opaque-bucket coverage from a DIFFERENT population's tail
   sample); (b) basic SENSE-DISAMBIGUATION -- WN_-prefixed entities resolve to an EXACT synset via `synset(name)`
   (the id already carries the sense tag); CN_/FN_ entities resolve via `synsets(lemma)` disambiguated against
   the entity's own definition text + ablated-graph-neighbor tokens, falling back to the WordNet-default
   (most-frequent) sense only when no disambiguating signal exists.
2. RELATION-LEVEL METRIC (the key reframe): report, in addition to the base cell's EXACT single-anchor metric,
   whether ANY of the TOP_K=5 nearest anchors (ranked across 5 tiers: name_transparent > wn_synonym >
   wn_hypernym > wn_gloss_definition > old_gloss_fallback) has an edge of the EXACT held relation type to the
   EXACT true target in the ablated graph -- crediting a near-neighborhood concept that carries the same
   relation even when the single nearest anchor missed exactly.

## Mechanism (zero-training, deterministic, network-free AND corpus-free at cell runtime)
Tier-0 (name_transparent) is REUSED VERBATIM from the base cell (`name_transparent_search` + `resolve_candidate`,
imported, not reimplemented). Tiers 1-4 (wn_synonym / wn_hypernym / wn_gloss_definition / old_gloss_fallback)
search the SAME well-connected (ablated degree >= 3) + contentful (len>=3, not stopword) lemma-index lookup
(`candidate_lookup`, imported) over WordNet synonym/hypernym/definition tokens sourced from the committed
lexical cache, then the base cell's original cached gloss as a last-resort fallback. Rank-0 = tier-0 pick if
resolved (polysemy-guard reused verbatim for tier 0 only); else the best (lowest-tier, highest-degree) pick from
tiers 1-4. TOP_K=5 distinct candidates gathered across all tiers, tier-ascending / degree-descending / eid-
ascending, deterministic.

STRATIFICATION NOTE (disclosed, not glossed over): tier-0's candidate SEARCH is identical to the base cell, but
the polysemy-guard's disambiguation signal is richer here (WN definition available where the old cached gloss
was thin/absent), so a handful of previously-abstained ties now resolve -- stratum membership is CLOSE but not
bit-identical to the base cell (MEASURED: name_transparent n=135 here vs n=121 base; name_opaque n=215 here vs
n=229 base). This is itself part of optimization axis 1 (better disambiguation), disclosed rather than claimed
as a bit-identical control.

## Populations
Identical construction to the base cell (imported `build_populations`, SEED=42, TARGET_TAXONOMIC_N=350,
TARGET_ARBITRARY_N=250, same provenance-order priority) -- same 350 taxonomic-cold + 250 arbitrary-cold degree-1
entities from the live substrate graph.

## Must-fail controls (ALL of the base cell's reused; RANDOM generalized to top-K)
(i) SCRAMBLE -- permutes (name_tokens, lexical-cache entry, old gloss) jointly across the taxonomic population
    (same seeded permutation construction as the base cell). Must collapse to floor on BOTH metrics.
(ii) RANDOM -- draws TOP_K=5 distinct random well-connected nodes (not one), so the floor comparison is
     apples-to-apples against the mechanism's own top-K pool width -- guards against "K guesses alone inflate
     the relation-level floor" with zero real content signal.
(iii) GRAPH_SELF_REFERENCE_CONTROL -- reused verbatim (empty name_tokens + a "gloss" built ONLY from the
      entity's own remaining ablated-graph-neighbor names, no lexical-cache entry substituted); provably empty
      for degree-1 cold entities; must stay at 0 on BOTH metrics.
POP (fixed highest-ablated-degree node, degenerate top-K of identical picks) is an additional sanity baseline.

## Pre-registered bands (fixed in the cell BEFORE the FULL run; autonomy per CONTRACT)
- `MIN_STRATUM_N` = 20.
- EXACT-DELTA-VS-BASE (method-limited-vs-fundamental read): `EXACT_DELTA_HP_MIN`=0.05 absolute lift over the
  base cell's OWN landed stratum exact-match rate -> `METHOD_LIMITED_CONFIRMED_LIFT`. `EXACT_DELTA_HF_MAX`=0.02
  -> `FUNDAMENTAL_NO_LIFT_FROM_METHOD`. Applied to name_transparent (base=0.1488) and name_opaque-all
  (base=0.0262, the FULL 229-entity opaque bucket, not just the base's old-gloss-sourced sub-slice -- the fair,
  population-matched comparison basis since tier-0 membership only shifts by disambiguation, not by definition).
- RELATION-LEVEL (top-K) vs RANDOM(topK) floor, banded like the base cell's PRED1: `RELLEVEL_TRANS_HP_MIN`=0.30,
  ratio>=5x, scramble_frac<=0.35 -> HARD_PASS. ratio<2x or scramble_frac>0.50 -> HARD_FAIL.
  `RELLEVEL_OPAQUE_HP_MIN`=0.10, ratio>=4x -> HARD_PASS; ratio<1.5x -> HARD_FAIL.
  Arbitrary (name-transparent primary): `RELLEVEL_ARB_MARGIN_HP_MIN`=0.05 vs RANDOM(topK); <=0.02 -> HARD_FAIL.
- Overall `overall_read` combines both axes: any confirmed EXACT-delta lift OR any relation-level HARD_PASS ->
  `METHOD_LIMITED_PARTIALLY_FIXABLE`; all EXACT-deltas fundamental AND relation-level not passing ->
  `FUNDAMENTAL_CEILING_METHOD_DID_NOT_MOVE_IT`; else `MIDDLE_BAND_INCONCLUSIVE_METHOD_READ`.

## SCHEMA-VET declarations
Same discipline set as the base cell (cardinality_ok, arms_differ_verified with POP exempted,
final_metrics_atomicity=tmp_replace, except-SystemExit-before-Exception, crlb_n/a, baseline_in_band,
discriminator-survives-scale via self-test + real-slice, HP_SCOPE per-arm, calibration_check=
adaptive_with_discriminator_gate, cell_chunked=false, progress_logging=print_flush_true). Additionally: self-test
extends the base cell's planted arena with hypernym-only-recoverable and synonym-only-recoverable planted cases
(proving the WN tiers recover cases the base cell's gloss-only mechanism could NOT) and a decoy-name case proving
`topk_relation_match` genuinely exceeds `rank0_exact_match` on at least one controlled case.

## Self-test (verified locally before FULL)
`data/exp_cold_placement_recovery_opt_v1_selftest/metrics.json`: SELFTEST_PASS. mech_trans_exact=0.944,
hypernym_only_recovery=1.0, synonym_only_recovery=1.0, topk_beats_exact_case=True, SCRAMBLE/RANDOM/POP/GSR
collapse (RANDOM's absolute topk-relation floor is margin-gated, not capped, per the SAME tiny-synthetic-pool
caveat as the base cell's SELFTEST_MIN_ARBITRARY_MARGIN precedent), 8 validity-preflight checks pass.

## FULL run (landed locally, deterministic CPU; dispatched to remote_cpu_queue for canonical provenance per
CONTRACT -- network-free/corpus-free at runtime, no nltk import in the cell itself)
`data/exp_cold_placement_recovery_opt_v1/metrics.json`. Verdict:
`COLD_PLACEMENT_RECOVERY_OPT__exact_trans=FUNDAMENTAL_NO_LIFT_FROM_METHOD__exact_opaque=METHOD_LIMITED_CONFIRMED_LIFT__rel_trans=HARD_PASS_RELATION_LEVEL_USEFUL__rel_opaque=HARD_PASS_RELATION_LEVEL_USEFUL__rel_arb=HARD_PASS_PARTIAL_GENERALIZATION__read=METHOD_LIMITED_PARTIALLY_FIXABLE`
See the exp_dev completion report for full measured numbers and interpretation.

## Remote-CPU canonical-provenance dispatch (exp_dev cannot SCP; orchestrator ships)
```
bash tools/orchestrator/queue_add.sh remote_cpu_queue cold_placement_recovery_opt_v1 experiments/exp_cold_placement_recovery_opt_v1.py preregs/2026-07-14_cold_placement_recovery_opt_v1.md 600
```
timeout_s=600: FULL measured wall time locally = 8.0s (same graph load as the base cell + ~4x per-entity tiered
lookup work); 600s is a >75x safety margin for remote host variance (pure-CPU, zero-training, zero-GPU cell; no
scaling risk from N since population sizes are fixed constants). Requires `data/exp_cold_placement_recovery_opt_v1
/provenance.json` to be present on the remote checkout (committed to the repo alongside the cell).
