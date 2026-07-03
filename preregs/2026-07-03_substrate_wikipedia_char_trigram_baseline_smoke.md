# PRE-REG: substrate-native char-trigram Wikipedia retrieval floor-check (SMOKE)

**Anchor:** `substrate_wikipedia_char_trigram_baseline_smoke_2026_07_03`
**Cell file:** `experiments/exp_substrate_wikipedia_char_trigram_baseline_smoke_2026-07-03.py`
**Filed:** 2026-07-03 (USER-directed: fork wikipedia_ingest infra with substrate-native surface encoder)
**Author:** hdi_exp_dev
**Run mode:** SMOKE-only (no FULL variant filed).

## Question

What does a NON-bge substrate ingest achieve on real-corpus Wikipedia title -> article retrieval, using only substrate-native primitives (bag-of-char-trigram HD)?

USER-locked directive: bge is NEVER a substrate primitive. `backend/kb/wikipedia_ingest.py` (line 115) uses `from backend.llm.bge_encoder import get_encoder`. This cell is a FORK/parallel probe (does NOT modify the production ingest); it establishes what a substrate-native surface encoder can do on the same held-out retrieval task.

## Framing discipline (LOAD-BEARING)

- Substrate has no general knowledge ingested (`feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`). Char-trigram bag is a MECHANISM PROBE, not a capability claim.
- Char-trigram is a trivial VWFA-analog surface reader (bag of overlapping character 3-grams with a per-trigram bipolar HD codebook, sum-bundled and signed). It captures character-overlap only; no positional structure, no semantics.
- bge reference is a FLOOR-CHECK number, not a fair-contest target:
  - If char-trigram approaches bge, the task is bag-favorable (title-body word overlap dominates) and doesn't need a fancy encoder.
  - If it falls far short, brain-analog composition (VWFA + ATL + Spoke 3 hippocampal consolidation) is genuinely load-bearing.
- Result feeds into strategic decision: is Spoke 1 v3-D + Spoke 2 Foldiak composition ready to replace bge for the substrate ingest, or does Spoke 3 need to land first?

## Prior work check

Substrate-KB concept-query (2026-07-03) for "char trigram wikipedia retrieval real corpus":
- Top hit `entity='Real-corpus retrieval'` cosine=0.4121 (source `notes/exp_dev_to_testbed_benchmark_suite_results_2026-06-08.md`).
- Rank 2 `entity='retrieval'` cosine=0.3828 (wordnet cache; generic).
- Rank 3 `entity='Retrieval'` cosine=0.3828 (`notes/research_to_exp_dev_storage_test_multidim_criteria_2026-06-07.md`).
- Rank 4 chunk of `research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md` cosine=0.3311 (NQ/DPR/Wikipedia benchmark discussion).
- Rank 5 `entity='Anchor 1: substrate_wikipedia_nq_triviaqa_retrieval_v1'` cosine=0.3301 (`notes/exp_dev_handoff_research_substrate_pretraining_2026-06-07.md`).
- **Prior-work check: NONE at cosine > 0.30 for the specific substrate-native char-trigram-on-real-Wikipedia probe** (top hit at 0.4121 is a note on the multi-arm benchmark harness, not a prior char-trigram Wikipedia probe). Cell is genuinely novel as a substrate-native NON-bge floor-check on real Wikipedia.

Related prior cells consulted:
- `experiments/exp_wikipedia_ingest_100k_gpu_v1.py` -- prior HP bge-large + Wikipedia 100K (recall@5=0.992). Reference target for the substrate-native gap.
- `experiments/exp_substrate_concept_encoder_wikipedia_10k_apples_to_apples_v1_2026-07-02.py` -- 4-arm apples-to-apples cell (bge + ConceptEncoder + char_positional + char_trigram). Uses the same char_trigram arm as one of four; this cell probes it in isolation as a SMOKE-only floor-check + explicit random-baseline control.
- `hdlab/char_trigram_encoder.py` -- CharTrigramEncoder substrate-native surface encoder.

## Test protocol

Held-out title -> article retrieval on `data/datasets/wikipedia_smoke_500.jsonl`:

1. Load 500 articles (`{title, text}` per row).
2. Truncate each body to 800 chars (fast + comparable across arms).
3. For each arm, encode each article body -> body HD; encode each title -> title HD.
4. Compute cosine similarity matrix `S[i, j] = cos(title[i], body[j])`.
5. For each title i, sort articles by `S[i, :]` descending.
6. `recall@k` = fraction of titles whose correct body index i is in top-k.

Regime:
- N articles: 500 (all of `wikipedia_smoke_500.jsonl`; the requested 1K is not present on local disk -- MEASURED@ `wc -l data/datasets/wikipedia_smoke_500.jsonl = 500`).
- N_DIM: 2048.
- Seeds: [11, 17, 23]. Char-trigram encoder is deterministic w.r.t. seed by design (per-trigram codebook seeded from blake2b(trigram)); the random arm depends on seed. Running 3 seeds gives mean+std for the random arm and demonstrates char-trigram determinism (std ~ 0).
- Chance recall@5 = 5/500 = 0.01. THEORETICAL@.

## Arms

| Arm | Encoder | Training | HD dim | Compute |
|-----|---------|----------|--------|---------|
| ARM_CHAR_TRIGRAM_WIKIPEDIA | `hdlab.char_trigram_encoder.CharTrigramEncoder` | none (deterministic trigram-hash HDs) | 2048 | Sequential CPU per text |
| ARM_RANDOM_BASELINE | Random bipolar HDs (`rng.integers(0,2)*2-1`) | none | 2048 | numpy in-process |

Per-arm retrieval:
- **ARM_CHAR_TRIGRAM_WIKIPEDIA:** `body_HD[i] = encoder.encode(article_body[:800])`; `title_HD[i] = encoder.encode(title)`. Cosine on unit-normalized bipolar HDs.
- **ARM_RANDOM_BASELINE:** `body_HD[i], title_HD[i]` are independent random bipolar HDs from a seeded `np.random.default_rng`. Sanity floor: expected r@5 ~ 5/N (chance).

## Metrics (per arm x seed)

- `recall_at_1`, `recall_at_5`, `recall_at_10`
- `mean_reciprocal_rank`
- `intra_article_body_title_cos` (mean cos(title_i, correct_body_i))
- `inter_article_title_body_cos` (mean cos over a seed-derived permutation with i != perm[i])
- `signal_to_noise_ratio` = intra / max(|inter|, 1e-6)
- `n_dim`, `encoding_wall_s`, `throughput_articles_per_sec`

Aggregate across seeds: mean + std for each of the above.

## HP bands

`HP_SCOPE: LOAD_BEARING on ARM_CHAR_TRIGRAM_WIKIPEDIA (substrate-native floor-check); ARM_RANDOM_BASELINE is a sanity control (META_RULE_AG baseline_in_band).`

### HARD_PASS

| # | Metric | Threshold | Applies to |
|---|--------|-----------|------------|
| HP1 | recall@5 | >= 0.60 | ARM_CHAR_TRIGRAM_WIKIPEDIA |

Meaning: substrate-native surface encoder alone gets meaningful signal that a substrate-native ingest is viable (bge does 0.992 in the 100K reference; the 0.60 floor at 500 articles states we're well above chance and 60% of titles find their body in top-5).

### HARD_FAIL

| # | Condition | Implication |
|---|-----------|-------------|
| HF1 | ARM_CHAR_TRIGRAM_WIKIPEDIA recall@5 < 0.30 | Surface encoder alone insufficient; brain-analog composition (VWFA + ATL + Spoke 3) is LOAD_BEARING for substrate-native ingest. |
| HF2 | ARM_RANDOM_BASELINE recall@5 > 0.05 | META_RULE_AG baseline_in_band violation; retrieval-implementation bug; all r@5 numbers untrustworthy. |
| HFcard | actual_n_units < expected_n_units (2 arms x 3 seeds = 6) | META_RULE_H cardinality breach; one or more (seed, arm) units failed. |

### MIDDLE_BAND

char-trigram recall@5 in [0.30, 0.60). Partial signal but below CG floor: non-trivial title-body character overlap exists but a substrate-native surface encoder alone is not sufficient to hit CG. Route to Spoke 3 / concept-composition arc.

## Envelope-fail bands (per baseline_in_band)

- ARM_RANDOM_BASELINE recall@5 expected band: [0.0, 0.05]. Chance = 5/500 = 0.01. Band cap of 0.05 (5x chance) allows for 3-seed variance while catching implementation bugs.
- HF2 fires if observed > 0.05.

## Dispatch plan

- SMOKE via `local_cpu_queue` per USER-locked SMOKE-only-on-local discipline (`feedback_smoke_only_local_cpu_no_full_dispatches_USER_LOCKED_2026-07-01.md`).
- No FULL variant filed. If HP or MIDDLE_BAND at smoke: file a separate v1 cell scaling N -> 10K on remote/GPU as follow-up.
- No push required (local cell). Uncommitted-notes-invisible-to-runner does not apply here; local runner reads the working tree.

## Cell-template compliance

- `arms_differ_verified` at smoke gate (META_RULE_AF; hash-check on first-article body HD prefix).
- `final_metrics_atomicity: tmp_replace` (META_RULE_AH).
- `except SystemExit: raise` before `except Exception` in per-arm driver + `__main__`.
- `baseline_in_band` verified in verdict logic (META_RULE_AG).
- `cardinality_ok` = actual_n_units >= expected_n_units.
- Per-unit `failure_class` instrumentation (META_RULE_J).
- `start_marker_written`, `_heartbeat.jsonl`, crash-diagnostic write.
- Numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ (META_RULE_AC).
- Default `_parse_args()` mode is `smoke` (SMOKE-only cell): prevents accidental FULL invocation.

## Selftests (`--self-test`)

1. `retrieval_metrics_identity`: body=title gives r@1=1.0 (correctness).
2. `random_chance_at_scale`: random bipolar HDs at N=200 x n_dim=2048 -> r@5 in [0, 5*chance] band (baseline_in_band sanity).
3. `mini_arms_differ`: on the 5-article in-code mini corpus, char-trigram r@1 >= 0.20; random r@5 = 1.0 (all in top-5 of N=5); arm hashes distinct.
4. `arg_parse_default_is_smoke`: `_parse_args()` returns `"smoke"` when no flag/env is provided (SMOKE-only cell discipline).

## Post-smoke gating

Report per-arm r@5 mean, per-arm std, wall-time, throughput, and the honest gap-to-bge. Do NOT dispatch a FULL variant. HOLD status; the verdict feeds a strategic decision (is v3-composed ready to replace bge, or does Spoke 3 hippocampal consolidation need to land first).
