# Pre-reg: causal_link_comprehension_pilot_v1 (2026-08-02)

## Question (one sentence)
Can a passage-level CAUSE/EFFECT link register -- built from the SAME bind/unbind/bundle/
cleanup-argmax primitives as the VET'd accumulate situation-model organ (atom 29609) -- decode
`query_cause_of` / `query_effect_of` correctly on real, mostly non-adjacent, cross-chapter
causal facts from Anne of Green Gables, beating a most-recent-event (adjacency) baseline and a
random-link baseline?

## Prior-work check (substrate_query.sh, USER-locked 2026-07-01)
`bash tools/substrate_query.sh "causal link register passage level cause effect binding decode
narrative comprehension"` -> top hit cosine=0.2861 (VerbNet entity 'Cause' / 'cause' -- lexical
resource, not a cell), next `notes/research_drill_substrate_composition_operators_5x_2026-06-08.md`
cosine=0.2764 (design-level P10/P12 causal-chain COMPOSITION SKETCH, never built) and
`notes/multi_sentence_situation_model_plan_2026-07-24.md` cosine=0.2744 (DIMENSION 4 causation
design note, dispatch-pending, never run). All hits below the 0.30 dedup threshold and all are
DESIGN/LEXICAL, not a built-and-run cell. **Verdict: genuinely novel as a built/measured cell**
-- concretizes design ideas already on file (credited above), does not rediscover a landed
result. Also see `notes/inference_leap_scoping_beyond_role_decode_2026-08-02.md` (this cell's
direct design source, Director scoping note, no dispatch).

## Hypothesis
Trabasso & van den Broek's causal-network model of narrative comprehension: readers link
CAUSE->EFFECT across non-adjacent events via explicit connectives, causal plausibility, and
force-dynamics; causal connectivity (not textual adjacency) predicts recall/importance
(Trabasso & Sperry 1985; Trabasso & van den Broek 1985). If our FHRR bind/unbind/bundle organ
is a genuine glass-box implementation of that causal-network edge, it should recover the
correct linked event via structural bind/unbind (which does not care about textual distance)
where a recency/adjacency heuristic structurally CANNOT (by construction, on non-adjacent
gold).

## Data
`data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v1.jsonl` (14 items):
10 `cross_chapter_multi_event` / `same_chapter_multi_fact_integration` (require-integration,
non-adjacent-by-construction per the fair-test gate that landed commit d1ad81ad7) + 4
`local_adjacent_control` (cause/effect are the immediately-adjacent excerpt). Each item has
`cause_event` / `effect_event` as `{chapter, line_range, verbatim}`. **GOLD-ISOLATION**: this
pilot feeds the GOLD cause/effect event spans directly as the event vocabulary -- it does NOT
run role/coref extraction on raw text. This isolates the causal-link organ from the known
~14.5% coref extraction error, mirroring how the atom-29609 accumulate-vs-overwrite cell
isolated the register-form question from routing (its own "Honest scope" section).

## Architecture (assemble PROVEN organs, no new mechanism class)
- Uses `hdlab.situation_model_accumulate.CausalLinkRegister` (new class added this session,
  subclasses `AccumulateRegister` verbatim; see docstring) -- the REAL module, not a
  reimplementation (real_code_path gate).
- **Global unique-event vocabulary**: dedupe all 28 `(cause_event, effect_event)` spans across
  the 14 items by exact `(chapter, line_start, line_end)` tuple match. Two genuine collisions
  exist BY CONSTRUCTION in this gold (not engineered): `anne_causal_001`/`002` share the same
  cause event (the ch15 slate-breaking incident has TWO later effects -- ch38 thank-you and
  ch28 refusal); `anne_causal_010`/`011` share the same effect event (Matthew's death has TWO
  causes bound into one register -- the immediate shock and the bank-failure backstory).
  `anne_causal_013`'s effect == `anne_causal_005`'s cause (a genuine 2-hop chain: oculist-warns
  -> Marilla-tells-Anne -> Anne-gives-up-scholarship). These collisions mean the register is
  NOT one-link-per-entity everywhere -- some entities accumulate >1 CAUSE or >1 EFFECT fact via
  bundle, giving genuine (if small) bundling-interference signal, not just isolated exact-
  inverse decodes.
- ONE shared `CausalLinkRegister(d=1024, max_event_slots=N_unique_events)` for the whole book
  (passage-level, per the design doc), all 14 `add_causal_link(cause_idx, effect_idx)` calls
  written into it, THEN all 14 items queried against the same register (genuine shared-vocab
  test, not per-item fresh registers -- the harder, more honest condition).
- Vectors: FHRR unit-phase complex64, d=1024, torch.Generator fixed seed (MEANING=ASSIGNMENT,
  no borrowed embeddings, matches project convention).

## Baselines (must-fail on non-adjacent items, per-design-doc requirement)
- **most_recent (adjacency)**: chronological order of all unique events by `(chapter,
  line_start)`. `query_effect_of(cause_idx)` guesses the NEXT event in that order;
  `query_cause_of(effect_idx)` guesses the PREVIOUS event in that order. On
  `cross_chapter_multi_event` / `same_chapter_multi_fact_integration` items (non-adjacent BY
  CONSTRUCTION -- that was the fair-test gate's finding, commit d1ad81ad7) this baseline is
  expected near floor; on `local_adjacent_control` items it is expected to do well (it is
  LITERALLY the right heuristic there -- these are the discriminating-band control, not a
  second can-fail arm).
- **random_link**: deterministic seeded RNG picks a uniformly random OTHER event (excluding
  self) as the guess, same query directions as above.
- **chance level**: `1 / (N_unique_events - 1)` (uniform guess over all other events).

## Bands / gates (TAGS per META_RULE_AC)
1. **CAN-FAIL -- most_recent baseline near floor on the require-integration subset.**
   `most_recent_accuracy_integration <= chance + 0.15`. If this does NOT hold, the "non-
   adjacent by construction" premise from the fair-test gate is not actually reflected in THIS
   vocabulary construction (e.g. dedup collapsed too much of the intervening event history) --
   investigate before trusting the organ's win.
2. **CAN-FAIL -- most_recent baseline clears the discriminating band on the 4 local_adjacent
   controls.** `most_recent_accuracy_control >= 0.50` (4 items only; exact value is noisy at
   this N, so the gate is a sanity floor not a tight bound) -- confirms adjacency is a REAL,
   non-degenerate heuristic here, not just a strawman that fails everywhere.
3. **CAN-FAIL -- random_link stays near chance on both subsets.** `abs(random_link_accuracy -
   chance) <= 0.20` (loose given N=10 / N=4). If random beats chance by a wide margin, the
   vocabulary/query construction has a structural leak.
4. **PRIMARY -- organ beats both baselines on the require-integration subset (N=10).**
   HARD_PASS: `organ_accuracy_integration - max(most_recent_accuracy_integration,
   random_link_accuracy_integration) >= 0.30` AND `organ_accuracy_integration >= 0.50`.
   MIDDLE_BAND: gap in [0.10, 0.30) or organ in [chance+0.05, 0.50).
   HARD_FAIL (of the organ, not the harness): gap < 0.10 or organ <= baseline-adjacent.
5. **Honest N-too-small flag (mandatory in report regardless of gate outcome).** N=10
   require-integration items is a PILOT per the design doc's own recommendation ("mine more to
   25-40 for a scored cell") -- this cell reports a PILOT verdict, never a scored/HARD_PASS
   claim standing alone as sufficient evidence; recommend fuller gold mining as next step
   regardless of which gate fires.

## Compute architecture
- Class: (b) sequential-CPU with justification -- N=14 items, ~22-25 unique events, d=1024;
  wall time is milliseconds. This IS the substrate-primitive-extension being validated at tiny
  scale (bind/bundle/unbind/cleanup-argmax bit-identical to the promoted hdlab module), not a
  batching candidate.
- Storage strategy: bundled, declared -- explicitly testing the ACCUMULATE-via-bundle organ as
  the discriminator's positive arm (same exemption class as atom 29609's ARM B).

## Capacity note (explicit ask from spawn prompt)
`max_event_slots` is set to `N_unique_events` (~22-25, computed in-code from the dedup pass),
NOT the `AccumulateRegister` class default of 8 -- the cross-chapter gold (chapter_gap up to 23)
needs a vocabulary that spans the whole book's sampled events, which exceeds 8. At d=1024 and
~25 vocabulary vectors with at most 2 bundled facts per entity (the two genuine collisions
above), this is far below FHRR's empirically-observed cleanup capacity ceiling (prior organ:
recall still 0.66 at bundle load 4, atom `situation_model_event_bundle_focus_v1`) -- the
existing single-bank `AccumulateRegister`/`CausalLinkRegister` chain is sufficient for THIS
pilot's scale. A full-scale build spanning many books / hundreds-to-thousands of events would
plausibly need the multi-bank `hdlab.working_memory` backend a sibling agent is building this
session for capacity -- flagged here as a forward note, not needed for this pilot.

## Discriminator-fires / scale
N=14 total items is the entire currently-available gold; this pilot cell run is itself the full
run (no separate smoke-then-full split -- matches the atom-29609 precedent's "tiny-N is the
whole regime" exemption). The `--self-test` flag runs ONLY the fixture correctness check
(3-event planted-link fixture) before any full-run logic, satisfying the smoke gate without a
second regime.

## SCHEMA-VET checklist declarations
- `cardinality_ok`: n/a (no sweep axis; EXPECTED_N_UNITS=14, one seed, one regime).
- `arms_differ_verified`: true (hash-compare organ/most_recent/random_link per-item guess
  arrays at the smoke gate -- guesses are ints not tensors, so the "arm" comparison is over the
  three prediction-index arrays, declared exempt from the tensor-hash form of META_RULE_AF and
  checked via a plain not-all-identical assertion instead; see cell comment).
- `final_metrics_atomicity`: "tmp_replace" (single-shot).
- except-ordering: `except SystemExit: raise` / `except KeyboardInterrupt: raise` /
  `except Exception as e:` (write CELL_CRASHED, re-raise) -- no bare/BaseException except.
- `crlb_n/a`: "closed-form structural can-fail (chance = 1/(N_unique-1)), not a CRLB noise
  floor; discriminator_reachability: true by construction (0.50 HARD_PASS target is far below
  the deterministic single-link exact-inverse ceiling and far above chance ~0.04-0.05 at
  N_unique~22-25)".
- `baseline_in_band` (META_RULE_AG): most_recent is EXPECTED near-floor on the integration
  subset BY DESIGN (Gate 1 supersedes AG there) and EXPECTED higher on the control subset
  (Gate 2) -- declared exemption, not a violation.
- `defensive_error_checking`: "passed_all_4_patterns_heartbeat_exempt_lt10s" (start marker,
  crash diagnostic; heartbeat/chunking exempted -- single seed, single pass, wall time <10s).
- `progress_logging`: n/a (`timeout_s` far below the 1800s / 30min threshold that triggers the
  mandate).
- `real_code_path_and_signature_preflight`: exercises `hdlab.situation_model_accumulate.
  CausalLinkRegister` (the REAL promoted module, not a reimplementation) directly inside
  `main()`, at the ACTUAL scale (this IS full scale) -- self-test additionally constructs a
  tiny 3-event `CausalLinkRegister` and exercises `add_causal_link` / `query_effect_of` /
  `query_cause_of` before any full-run logic (real_code_path exercised in self-test too).

## Addendum: CORRECTED after first-run investigation (2026-08-02, before trusting the organ)
First pass used ONLY the 25 real gold cause/effect events (deduped) as the `most_recent`
baseline's candidate pool. Result: `HARD_FAIL_CANFAIL_VIOLATION` -- `most_recent_accuracy_
integration = 0.60`, far above the near-floor gate (`<= chance+0.15 = 0.19`).
MEASURED@data/exp_causal_link_comprehension_pilot_v1/metrics.json (pre-fix run, not the
committed one) showed the sparse 25-event pool let the adjacency baseline trivially win on
several cross-chapter items: with only 25 curated causal events spread across 10,574 lines /
38 chapters, a genuinely-distant cross-chapter pair can still land "next to each other" in the
CURATED pool purely because nothing else in the pool falls between them -- the exact risk the
design doc flagged ("must explicitly count adjacency distance... if the pool is recency-
dominated, either (a) deliberately oversample non-adjacent... or (b) report honestly"). This
was a discriminator-CONSTRUCTION bug (unfair baseline), not a mechanism finding -- correctly
caught by Gate 1 before any organ claim was trusted, exactly as the can-fail discipline
intends.

**Fix applied (option (a)):** `mine_distractor_events` densifies the vocabulary with REAL
raw-text spans from `data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt`
(the line numbers in gold `line_range` are GLOBAL file line numbers, confirmed by direct
inspection -- line 3867-3870 matches the ch.15 slate-breaking excerpt verbatim) at a fixed
200-line stride, skipping any candidate within 20 lines of a real gold event. This adds 50
distractor events (n_unique_events 25 -> 75) that carry ZERO causal facts (pure
cleanup-competition / adjacency-competition mass, never targets of `add_causal_link`) -- a
legitimate, in-scope fix (not scope creep: it directly implements the design doc's own
pre-specified remedy for this exact risk), re-run with the SAME seed, deterministic.
**Result after fix:** `gate_mr_near_floor_integration = True` (most_recent_integration =
0.10, chance = 0.0135), `gate_mr_clears_control = True` (most_recent_control = 1.00),
`gate_random_near_chance = True` both subsets -> `canfail_ok = True` -> verdict HARD_PASS.
This addendum is reported per META_RULE_AC (numbers tagged, correction documented) rather
than silently re-running and reporting only the final pass.

## Honest scope (declare before running)
- This is a PILOT (N=10 require-integration items), explicitly undersized for a scored claim
  per the design doc's own recommendation. A WORKS-pilot verdict recommends mining the fuller
  gold set (25-40 items) before treating any number here as a landed capability claim.
- GOLD-ISOLATED: coref/extraction is NOT exercised; this cell isolates the causal-LINK organ
  from the separate (already-measured, ~14.5% error) extraction competency. Do not over-claim
  end-to-end comprehension from this cell alone -- it is one organ-correctness pilot.
- The two/three genuine multi-fact collisions in the gold (shared cause, shared effect, 2-hop
  chain) are a small amount of real bundling stress, not a designed capacity sweep -- do not
  read a capacity CURVE out of N=3 collision cases; report them as qualitative confirmation
  the organ handles >1 fact per entity, not a capacity ceiling measurement.
