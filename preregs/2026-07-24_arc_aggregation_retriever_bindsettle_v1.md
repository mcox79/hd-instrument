# Pre-reg: arc_aggregation_retriever_bindsettle_v1

**Date:** 2026-07-24. **Author:** exp_dev (hdi_exp_dev). **Cell:**
`experiments/exp_arc_aggregation_retriever_bindsettle_v1.py`. **Contract:** INLINE-LOCAL foreground-to-
completion; no push/remote-persist; NOT remote-portable (GloVe cache + WorldTree git-ignored/large);
VET-PENDING. Runs in repo `.venv`.

## Question (can-fail)
ARC is a MULTI-FACT task (WorldTree gold: mean ~2.37 CENTRAL facts/Q). A single-fact retriever fetches
ONE fact when the task needs several. Does a BRAIN-FAITHFUL aggregator that COMBINES the candidate central
facts beat the single-fact floor AND a plain score-sum contrast, on ARC-Easy AND ARC-Challenge?

Two brain-faithful aggregators are tested (the research drill
`notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md` prescribes both):
1. **SPA-bundle** (Eliasmith SPA/Spaun): relevance-weighted HD superposition of the facts (accumulation),
   cosine to each choice. Facts sharing a semantic direction ADD constructively (convergence).
2. **Kintsch CI-settle**: bipartite signed-graph Construction-Integration relaxation (fact-choice signed
   support + fact-fact contradiction edges = raw signed cosine + choice-choice inhibition; clip-negatives
   + renormalize per Kintsch, converge at eps=1e-3; choice-node readout). Thagard-ECHO family.

## Pools
- **ORACLE** (gold CENTRAL+LEXGLUE facts as the candidate pool) -- isolates AGGREGATION from retrieval
  (AI2's ARC diagnosis: retrieval bias is the bottleneck, not combination -> this arm is THE critical
  measurement). PRIMARY discriminator lives here.
- **RETRIEVAL** (top-K=10 facts from the ingested tablestore, with the test question's OWN gold support
  UIDs HELD OUT) -- fair end-to-end (retrieval + aggregation). No answer-leak.

## Knowledge source + held-out guardrail
WorldTree V2.1 tablestore (~9720 typed science facts) = domain-matched science CURRICULUM. The ingested
store EXCLUDES every gold support UID of the test questions -> the RETRIEVAL number is fair, not leaked
(the 29530 test-targeting lesson). ORACLE uses the gold facts explicitly (it is the upper bound).

## Bands (HARD-PASS / HARD-FAIL) -- PRE-REGISTERED
Primary = ORACLE pool, ARC-Easy (best brain-faithful aggregator = max(bundle, settle)):
- **MINIMUM BAR (mechanism real):** `best_agg_easy - single_easy >= 0.05` AND `best_agg_easy - sum_easy >= 0.0`
  -> verdict `AGG_BEATS_FLOOR`. (best aggregator beats the single-fact FLOOR and at least ties the score-sum
  contrast; the winner must be a genuine VSA bundle / signed-graph relaxation, NOT a plain score-sum.)
- `best_agg - single >= 0.05` but `< sum` -> `AGG_BEATS_SINGLE_NOT_SUM` (aggregation helps; brain-faithful
  aggregator does not decisively add over score-sum -- honest partial).
- `|best_agg - single| < 0.05` -> `AGG_FLAT` (presume impl-bug until proven structural).
- `best_agg < single - 0.05` -> `AGG_BELOW_SINGLE`.
- **THE TARGET (coordinator 2026-07-24):** ARC-CHALLENGE best aggregator above chance, reported PROMINENTLY
  (`challenge_oracle_best_minus_chance`, `challenge_retr_best_minus_chance`). Challenge-flat is NOT a
  pass-by-default -- it is DIAGNOSED per-item (retrieval-fail vs aggregation-fail vs surface-lure).
- CI-faithfulness (Kintsch): `settle - sum >= 0.05` AND `settle - pos_only >= 0.02` -> negatives + settling
  load-bearing. (Reported honestly; the smoke shows this does NOT hold at this encoder -> spreading-style.)

Integrity gates (any breach overrides the accuracy verdict):
- `leak_flag`: scramble_easy >= chance + 0.05 -> LEAK_FLAG.
- `mustfail_breach`: shuffled-matrix arm NOT < chance+0.05 OR inverted-readout arm NOT < chance -> readout
  is a construction artifact.
- `baseline_in_band`: 0.05 < empty_easy < 0.95.

## Feasibility / discriminator-survives-scale
- Discriminator = aggregation-vs-single gap on gold. NOT saturated: single-fact gold Easy ~0.73 (< 0.90
  AG_SATURATION), leaving headroom. VERIFIED at smoke (n=250, 186 gold Easy): bundle 0.833 > sum 0.807 >
  single 0.727 > CI-settle 0.647; must-fail shuffled 0.24 (~chance) + inverted 0.113 (<chance) collapse;
  no leak (scramble 0.233); baseline_in_band (empty 0.30). CRLB n/a: discriminator is an accuracy GAP over
  categorical argmax choices, no analytic noise floor; feasibility shown empirically by the in-band single.

## SCHEMA-VET fields
- `arms_differ_verified`: true (single / sum / bundle / settle predicted-choice digests differ).
- `final_metrics_atomicity`: tmp_replace (os.replace at end).
- `except SystemExit: raise` before `except Exception` (no BaseException / bare except): confirmed.
- `deterministic_seeding`: true (fixed int seeds, numpy default_rng, sorted iteration; no hash()/list(set())).
- `cell_chunked`: false (single-process; no seed axis; INLINE-LOCAL foreground).
- `start_marker_written`: true. `crash_diagnostic_present`: true. `heartbeat_present`: true.
- `progress_logging`: print_flush_true (line_buffered stdout + per-arm flush prints + heartbeat).
- `calibration_check`: default_ok_for_this_regime (bands are accuracy gaps, no primitive-default inheritance).
- `crlb_n/a`: "discriminator is a categorical-accuracy gap; no analytic noise floor applies".
- `storage_strategy`: sharded (each fact its own embedding vector; composed via aggregation, per META_STORAGE).
- `compute_architecture`: mixed (batched retrieval matmul + per-question bundle + signed-graph relaxation;
  CPU numpy; wall < 10 min at smoke n=250 = 144s). Sequential per-question settling justified: the settle
  IS the substrate primitive under test; small K<=10 graphs; total wall well under budget; not a batching
  candidate (GPU batching would not materially help small per-question relaxations).
- `discriminator_fires`: settle iterates >= 2 (mean ~17 iters oracle); must-fail controls collapse;
  arms differ. Verified at smoke.

## Functional requirements (gate E)
- FR1 combine several facts -> SPA-bundle superposition + Kintsch CI relaxation (both mapped).
- FR2 resist surface lure (Challenge) -> Kintsch contradiction edges + choice inhibition (measured via
  pos-only ablation + lure detection in miss_diagnosis).
- FR3 separate retrieval failure from aggregation failure -> ORACLE pool + miss_diagnosis (per-item).

## Honest positioning (status_log framing, coordinator 2026-07-24)
The win is matching the ~55-65% structured-solver tier on ARC-Easy (and, given gold facts, on Challenge)
via a GLASS-BOX VSA + brain-faithful aggregation route (NO LLM at inference) -- inspectability +
brain-faithfulness -- NOT beating LLM SOTA (~90%+). Challenge is THE TARGET; every Challenge miss is
diagnosed (retrieval-fail vs aggregation-fail vs surface-lure).
