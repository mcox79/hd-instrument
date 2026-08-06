# Pre-reg: n11b_symmetric_pattern_lexical_similarity_v1

**Date:** 2026-08-06
**Anchor:** `n11b_symmetric_pattern_lexical_similarity_v1`
**Script:** `experiments/exp_n11b_symmetric_pattern_lexical_similarity_v1.py`
**Extended primitive:** `hdlab/random_indexing.py` (RandomIndexingEncoder, new `context_mode` param;
"window" default is BYTE-IDENTICAL to pre-2026-08-06 behavior -- verified in `_selftest()`)
**Route:** LOCAL (this turn, in-process, per-arm checkpointed; not queue-dispatched)
**Driver note:** `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` (Section 3/4:
"First buildable increment" + "The can-fail test")
**Prior-work check (SUBSTRATE-KB, mandatory before authoring):** `bash tools/substrate_query.sh
"symmetric pattern context random indexing lexical similarity ATL hub synonym"` -> max cosine
0.2939 (top hit `random_indexing.py` via `notes/brain_component_functional_map_2026-08-04.md`),
BELOW the 0.30 prior-work threshold. NONE at cosine>0.30 -> novel cell, not a rediscovery.

## Mechanism under test

`hdlab/random_indexing.py`'s existing Random Indexing accumulator (Sahlgren 2005, Kanerva
1988), landed FULL on text8 with MIDDLE_BAND signal (`data/exp_n11_random_indexing_semantic_v1/
metrics.json`), is diagnosed by the drill to capture topical RELATEDNESS (vessel~dock) rather
than genuine SIMILARITY (vessel~ferry), because its linear-window context pulls together any
two words that co-occur near a common third word, regardless of whether they are the same KIND
of thing. This cell adds `context_mode="symmetric_pattern"`: accumulate context ONLY from
tokens adjacent to a symmetric coordinator ("and" / "or") -- i.e. "X and Y" / "X or Y" -- pure
surface pattern-matching, no parser (Schwartz, Reichart & Rappoport 2015, CoNLL: SimLex-999
rho=0.517 vs plain skip-gram's 0.462 on the same corpus). Coordination slots co-select words of
the SAME KIND ("ferry and boat" is natural; "ferry and dock" is not), which is predicted to
separate genuine synonymy from mere relatedness where the linear-window arm cannot.

## Arms (single seed=7, single text8 FULL pass per arm)

| Arm | Mechanism | Hypothesis |
|---|---|---|
| WINDOW | Existing linear-window RI (context_mode="window", unchanged) | Plateaus: Tier1~Tier2 (topical relatedness, not similarity) |
| SYMMETRIC_PATTERN | NEW: context_mode="symmetric_pattern" (and/or-adjacency) | Separates Tier1 > Tier2 > Tier3 |
| HASH_RANDOM | Floor control: raw index vectors only, zero accumulation (production `word_vector` shape) | No graded ordering, by construction |
| SYMMETRIC_PATTERN_SCRAMBLED | symmetric_pattern fit on a word-order-shuffled corpus (destroys and/or-adjacency structure, preserves and/or token frequency) | Collapses the SYMMETRIC_PATTERN gain toward chance |

The existing `CONTROL_RANDOM_PERMUTE` result for the WINDOW mechanism is NOT re-run here (would
duplicate ~300-400s of compute for an already-established fact): MEASURED@`data/exp_n11_random_
indexing_semantic_v1/metrics.json:detail.by_arm_agg.CONTROL_RANDOM_PERMUTE.ratio_mean=1.0008`
(collapses to null). This cell's own SCRAMBLED control plays the equivalent earned-not-artifact
role for the NEW symmetric_pattern mechanism specifically.

## Probe set

Hand-authored TRIPLES: `(anchor, tier1_synonym, tier2_related_not_synonym, tier3_unrelated)`.
29 triples (>= the 15-20 contract minimum), all four words per triple MEASURED@ad-hoc text8
frequency check this session to clear `min_count=5` (lowest: "mend" n=15; most triples use
words with n in the hundreds-to-thousands). See `_PROBE_TRIPLES` in the cell script for the
full list (vessel/ship/dock/anger, car/automobile/wheel/passion, happy/glad/love/mountain,
repair/fix/broken/song, angry/mad/rage/lake, fear/terror/afraid/music, etc.).

Per-triple ordered-inequality: `cos(anchor,syn) > cos(anchor,related) > cos(anchor,unrelated)`.
A triple is scored only if all 4 words are in-vocab with nonzero-norm vectors under that arm
(else skipped, counted honestly in `n_skipped_oov_or_zero` / coverage).

## Pre-reg HARD bands

**HARD_PASS (ALL required):**
1. `SYMMETRIC_PATTERN.ordered_inequality_frac >= 0.735` (>= 70% floor + 5% of band width,
   per META_RULE_L strictly-above-floor)
2. `WINDOW.ordered_inequality_frac < 0.50` (baseline fails majority -- the crux differentiator;
   if WINDOW unexpectedly clears 0.50 the Section 2/3 diagnosis is wrong and must be
   investigated before trusting anything built on top of it)
3. `HASH_RANDOM.ordered_inequality_frac < 0.50` (floor control fails by construction)
4. `SYMMETRIC_PATTERN.ordered_inequality_frac - WINDOW.ordered_inequality_frac >= 0.20`
   (material delta, not barely-better)
5. `SYMMETRIC_PATTERN.ordered_inequality_frac - SYMMETRIC_PATTERN_SCRAMBLED.ordered_inequality_frac
   >= 0.30` AND `SYMMETRIC_PATTERN_SCRAMBLED.ordered_inequality_frac <= 0.45` (scramble
   ablation collapses the gain -- earned, not artifact)
6. `n_llm_calls == 0` at every stage

**HARD_FAIL (ANY triggers):**
- `SYMMETRIC_PATTERN.ordered_inequality_frac < 0.50`
- `SYMMETRIC_PATTERN.ordered_inequality_frac - WINDOW.ordered_inequality_frac < 0.10` (does no
  better than the existing linear-window arm)
- `SYMMETRIC_PATTERN.ordered_inequality_frac - SYMMETRIC_PATTERN_SCRAMBLED.ordered_inequality_frac
  < 0.10` (scramble does not collapse -> signal is an artifact, not earned structure)

**MIDDLE_BAND:** everything else (real but partial signal, or a specific gate missed narrowly,
or probe coverage is underpowered -- report `n_skipped_oov_or_zero` honestly per arm).

## Config

- Corpus: text8 (`data/text8_cache/text8.txt`; ~17.0M tokens). FULL text8 REQUIRED (not a
  reduced-token subset) -- see "Smoke-gate deviation" below.
- N_DIM = 8192, sparsity = 10, window = 5 (WINDOW arm only), min_count = 5 -- reused unchanged
  from the landed n11 v1 FULL config so the WINDOW arm here is directly comparable.
- seed = 7 (single seed; matches n11 v1's first seed). Cross-seed variance on this class of
  measurement is empirically tiny: MEASURED@`data/exp_n11_random_indexing_semantic_v1/
  metrics.json:detail.by_arm_agg.RANDOM_INDEXING_ALONE.ratio_cv=0.0005` across 3 seeds in the
  prior cell. Single-seed is compute-proportional for this directional gate; a 3-seed
  replication is a candidate follow-up if this cell lands MIDDLE_BAND/HARD_PASS and gets
  promoted.
- `context_mode="symmetric_pattern"` radius is fixed at 1 (immediate left/right neighbor of
  "and"/"or"). text8 has punctuation stripped entirely (verified this session: first 500 chars
  contain zero commas/periods), so comma-list patterns ("X, Y, and Z") from the full Schwartz
  et al. method are NOT available/attempted here -- an honest, documented scope-narrowing.
  No POS-filtering of pattern hits either (Schwartz et al.'s refined variant POS-filters;
  this implementation is pure surface and/or-adjacency, the cheapest variant, per the drill's
  explicit recommendation to start there).

## Smoke-gate deviation (DISCRIMINATOR-MUST-SURVIVE-SCALE, Option B: analytical justification)

A reduced-token "smoke" text8 pass is NOT run for the FULL arms. Rationale: several probe
words are thin even at full-corpus scale (e.g. "mend" n=15 at 17.0M tokens); a smoke subset
(e.g. 200k tokens, ~1.2% of the corpus) would starve "mend" to ~0.2 expected occurrences and
most Tier1/Tier2 pairs to near-zero coverage, producing a smoke that tests nothing about the
mechanism (would pass or fail on vocabulary noise, not on the symmetric-pattern-vs-window
discrimination this cell exists to measure). Per the exp_dev DISCRIMINATOR-MUST-SURVIVE-SCALE
rule, Option B (analytical justification) is used instead of Option A (smoke-at-full-N is
functionally what --smoke or --self-test would need anyway, so this is honest, not a shortcut
around the gate) or C (preview arm). The cell's `--self-test` / `--smoke` path instead runs a
synthetic in-memory-corpus discriminator-fires check (see `hdlab/random_indexing.py`'s own
`_selftest`: `ferry`+`boat` sharing a "ship" coordination partner reach cosine=1.000 vs
`ferry`-`mathematics` (disjoint clusters) at cosine=0.000, MEASURED@this session's self-test
run) BEFORE the FULL text8 run is dispatched. This is documented explicitly (not silently
skipped) so Skunkworks / Director can audit the judgment call.

## Cost (estimated, HYPOTHESIZED before first FULL run)

- WINDOW arm: ~300-400s (MEASURED@`data/exp_n11_random_indexing_semantic_v1/metrics.json:
  per_unit[0].fit_wall_s_bag` in [268, 396] across the 3 landed seeds; same code path, same
  config, this cell's WINDOW arm should land in the same range).
- SYMMETRIC_PATTERN / SYMMETRIC_PATTERN_SCRAMBLED arms: HYPOTHESIZED much faster than WINDOW
  (~10-60s each) -- the and/or-adjacency loop only accumulates at coordinator positions
  (MEASURED@ad-hoc corpus scan this session: "and"=416629 + "or"=68945 = 485574 trigger
  positions out of 17.0M, i.e. ~350x fewer accumulation events than WINDOW's window-radius
  sweep over every position), though the O(n) single-pass "is this a coordinator" scan itself
  is unavoidable regardless of trigger density.
- HASH_RANDOM arm: near-free (vocab Counter pass + index-vector build only; skips the
  accumulation loop entirely).
- Total estimated wall: ~6-10 min for all 4 arms, single seed. Per-ARM checkpointing
  (`experiments._seed_checkpoint.write_partial_key`, key = arm name) means a run that exceeds
  one foreground call resumes the remaining arms on the next invocation without re-fitting
  completed arms. `--timeout` (if later queue-dispatched) should be set >= 1800s for margin.

## Why this matters (strategic)

Per the drill: general synonym/hypernym resolution ("vessel"~"ferry") is BLOCKED on the
missing ATL learned lexical-semantic hub, which has independently blocked (a) the
outcome-valence synonym-referent coverage wall and (b) context-conditioned sense-resolution.
If this cell HARD_PASSes, the substrate gains a genuinely earned, glass-box, zero-shot graded
lexical-similarity primitive (extends an OWNED, already-validated mechanism -- not a new
mechanism class, not a bigger hand table) that can be WIRED into both blocked capabilities.
This is explicitly scoped as earning the verbal/distributional SPOKE, not the full transmodal
ATL hub (multi-spoke feature-grounded integration remains the longer-term target under the
6yo-grounded-foundation program) -- do not overclaim beyond that scope in the verdict.

## Skunkworks structural blockers (baked into cell)

- `_LLM_CALL_COUNTER = [0]` -- substrate-only at all stages.
- per-ARM checkpoint (single seed; `write_partial_key`/`aggregate_partials` keyed by arm name,
  resumable across process invocations, PROT-021 config-mismatch guard via `run_config`).
- atexit + SIGTERM synthesize a PARTIAL metrics.json from whatever arms completed (never a
  silent hang with zero on-disk evidence).
- `except SystemExit: raise` / `except KeyboardInterrupt: raise` BEFORE `except Exception`
  (META_RULE ordering, no bare `except:` / `except BaseException:` anywhere in the cell).
- ARMS-MUST-DIFFER (META_RULE_AF) hash check in `_selftest()`: WINDOW context vector must be
  bit-different from the raw HASH_RANDOM index vector for the same word.
- structured `gate_claims` (`record_gate`) persisted under `structured_gate_claims` in
  metrics.json -- machine-readable HARD_PASS/HARD_FAIL gates, no verdict-string regex needed.

## CAN-FAIL discriminators

1. WINDOW must FAIL the >=50% ordered-inequality bar (predicted plateau). If WINDOW instead
   clears it, the drill's core relatedness-vs-similarity diagnosis for THIS corpus/config is
   falsified and should be investigated before trusting the SYMMETRIC_PATTERN result.
2. HASH_RANDOM (zero accumulation) must fail by construction -- a sanity floor, not a real
   discriminator; if it somehow clears 0.50 the probe-scoring code has a bug.
3. SYMMETRIC_PATTERN_SCRAMBLED must collapse the SYMMETRIC_PATTERN gain -- if scrambling word
   order does NOT hurt, the "signal" is not earned from real and/or-coordination structure
   (possible bug: e.g. accidentally leaking un-shuffled vocab statistics into the scored
   vectors) and must not be trusted.

## Earned-not-borrowed verification (mandatory)

- `n_llm_calls == 0` at fit and inference time (checked in `compute_verdict`).
- Own, inspectable weights at every stage: sparse-ternary index vectors (`_make_index_vector`),
  accumulated context vectors (`_context_vectors`) -- no black-box distillation step anywhere.
- SCRAMBLED-corpus ablation (see HARD-PASS gate 5 / HARD-FAIL gate 3 above) is the mandatory
  "does the graded structure survive destroying the real corpus structure" check.

## Cites

- `notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md` (Sections 3, 4)
- Schwartz, R., Reichart, R., Rappoport, A. (2015). "Symmetric Pattern Based Word Embeddings
  for Improved Word Similarity Prediction." CoNLL 2015.
- Hill, F., Reichart, R., Korhonen, A. (2015). "SimLex-999: Evaluating Semantic Models with
  (Genuine) Similarity Estimation." Computational Linguistics 41(4).
- Sahlgren, M. (2005). "An Introduction to Random Indexing." TKE 2005.
- Kanerva, P. (1988). "Sparse Distributed Memory." MIT Press.
- `data/exp_n11_random_indexing_semantic_v1/metrics.json` (prior landed WINDOW-only FULL
  result; MIDDLE_BAND; reused config).

## Predispatch / prior-work check

`bash tools/substrate_query.sh "symmetric pattern context random indexing lexical similarity
ATL hub synonym"` -> max cosine 0.2939, below the 0.30 novelty threshold. PROCEED (2026-08-06).
