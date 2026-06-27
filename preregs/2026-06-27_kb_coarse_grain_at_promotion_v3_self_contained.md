# Pre-reg: kb_coarse_grain_at_promotion_v3_self_contained (ANCHOR 3 v3 RESCUE; 2026-06-27)

**Anchor:** `kb_coarse_grain_at_promotion_v3_self_contained`
**Cell:** `experiments/exp_kb_coarse_grain_at_promotion_v3_self_contained.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** CHAIN_GRADE candidate (v2 design unchanged; only KB load path patched).
**Wave:** Tier-2 rescue from `notes/research_drill_kb_referent_missing_systemic_3x_2026-06-27.md`.

## Source

v2 cell HARD_FAILed on remote with KB_REFERENT_MISSING (same systemic failure
as ANCHOR 1 v2 + ANCHOR 5 v1). v2's `load_default_kb(REPO)` expects the
canonical `data/substrate_director_kb_v1/manifest.json`, which exists locally
but is not provisioned to the remote_cpu runner. Tier-1 provisioning cell
(`exp_substrate_director_kb_remote_provision_v1.py`) is in flight to address
this; meanwhile, the v3 self-contained rescue pattern unblocks ANCHOR 3 by
building a labeled mini-KB IN-CELL via `hdlab.director_kb_chunk_ingest.run_chunk_ingest`
over notes/+memory/+preregs/.

## Brain-analog rationale (per drill Section "ANGLE 2")

This RESCUE chooses the **hippocampal-encoding** pattern (cell builds its own
scaffold) over the **cortical-retrieval** pattern (cell tests against the
canonical substrate). For coarse-grain-at-promotion the choice is legitimate:
the v2 mechanism tests whether ultrametric clustering respects USER_DIRECTIVE
separation + breaks the recall cap at scale, not whether the canonical
substrate's specific 577k-entity stratification is correctly preserved. A
self-contained labeled corpus over notes/+memory/+preregs/ provides
sufficient USER_DIRECTIVE (chunk_memory) atoms and sufficient stratified
classes for the mechanism to be measurably tested. (Contrast ANCHOR 5
dual-store audit, whose test target IS the canonical substrate - that one
must wait for Tier-1 provision.)

## v3 mechanism (UNCHANGED from v2 chain-grade-path)

Same arms, same RC-1 (n_UD >= 10) + RC-2 (n_atoms >= 10000 cap-break) +
discriminator-must-survive-scale guard. Only the SAMPLE SOURCE changes:

- v2: pulls atoms from `kb.E` (the loaded canonical KB), uses bare
  `source_class='memory'` token.
- v3: pulls atoms from an IN-CELL chunk-ingested mini-KB, uses the
  CHUNK-PREFIXED `source_class='chunk_memory'` token (the chunk_ingest
  module prefixes per Principle 8).

## ARMS (3 mandatory + 1 full-N preview at smoke; identical to v2)

### ARM_NO_COARSE_GRAIN_BASELINE
Sanity rail. recall_unclustered = 1.0 by construction. Unchanged.

### ARM_COARSE_GRAIN_ULTRAMETRIC
Per-source-class ultrametric clustering on the IN-CELL mini-KB. Forces
n_UD >= 10 `chunk_memory` atoms into the sample. USER_DIRECTIVE strictly
separated by construction. `user_directive_mixing_violations` asserted == 0.

### ARM_RANDOM_CLUSTER_COLLAPSE
Same cluster sizes from ARM_ULTRA; assigns RANDOM membership. Tests whether
SEMANTIC clustering matters. Unchanged.

### ARM_FULL_N_PREVIEW (smoke-only)
Single-seed n=10000 (or capped at mini-KB available atoms, whichever is
smaller) ARM_ULTRA run; flags saturation risk. If preview rec_unclst >=
HP_MAX_REC_UNCLUSTERED_NONSAT (0.999), smoke verdict = HARD_FAIL to halt
full dispatch.

## Inline mini-KB build (NEW vs v2; identical to ANCHOR 1 v3 pattern)

- `chunk_classes = ("note", "memory", "prereg")`
- `max_files_per_class = 200` (full) / `50` (smoke)
- `n_dim = 2048`, `seed = 17`
- Output: `data/exp_<anchor>/_inline_kb/`
- Wipes pre-existing inline_kb on each run (deterministic build).

Source-class tokens after ingest are prefixed: `chunk_note`, `chunk_memory`,
`chunk_prereg` (per `hdlab/director_kb_chunk_ingest.py` line 514-518).

Expected ingest cardinality:
- Smoke (50 files/class): n_entities >= 100 minimum; ~1000-3000 typical.
- Full (200 files/class): n_entities >= 500 minimum; ~5000-15000 typical.

The full mini-KB has enough atoms to support the n_atoms=10000 RC-2 scale
target IF total entities >= 10000. If smaller, ARM_FULL_N_PREVIEW caps at
available atom count and reports cardinality_ok=False; verdict honestly
falls to MIDDLE_BAND or HARD_FAIL.

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS; v2 verbatim)

HARD_PASS requires ALL of:
- (a) `user_directive_retention == 1.0` (zero `chunk_memory` atoms clustered
  with non-memory; n_UD >= 10 verified present).
- (b) `recall_unclustered < 1.0` at n_atoms=10000 (cap-breaking evidence).
- (c) `capacity_drop_fraction > 0.20` (mechanism does substantive compression).
- (d) `gap_vs_random > 0.30` (ULTRA - RANDOM recall_clustered).
- (e) `cv_recall_clustered < 0.05` across 3 seeds.

MIDDLE_BAND: any subset of (a)+(b)+(c)+(d) met but (e) fails (0.05 <= cv <=
0.10) OR gap in (0.15, 0.30].

HARD_FAIL: (a) violated, OR (b) rec_unclst still saturates at 1.0 at n=10k,
OR cap_drop < 0.10, OR gap <= 0.05, OR ingest yields fewer entities than
EXPECTED_INGEST_ENTITIES_MIN.

## Cardinality (D4 mandatory; v2 + ingest cardinality)

`summary.cardinality_ok = (n_UD_in_sample >= 10) AND (n_atoms_full >= 10000)
AND (n_seeds_full >= 3) AND (n_ingest_entities >= EXPECTED_INGEST_ENTITIES_MIN)`.

EXPECTED_N_SEED_RESULTS at full = 3. HARD_FAIL on cardinality breach.

## Discriminator-must-survive-scale (D1)

ARM_FULL_N_PREVIEW at smoke runs n=10000 single-seed ARM_ULTRA preview;
saturation_risk_flag set when rec_unclst >= 0.999. Smoke verdict
encapsulates this honestly (SMOKE_PREVIEW_SATURATED HARD_FAIL or
SMOKE_PASS).

## Substrate-only-decode gate

n_llm_calls per arm = 0 (deterministic chunker + char-trigram encoder +
ultrametric clustering primitive; no transformers).

## Real data / synthetic provenance

100% real. The inline mini-KB is built from `notes/ + memory/ + preregs/`
on the runner's git checkout; no synthetic atoms.

## Honest scope

Tests whether per-source-class ultrametric clustering at scale (n=10000)
yields cap-broken recall + non-null mechanism gap vs random + zero
USER_DIRECTIVE mixing. Does NOT re-test the canonical-KB ingest pipeline
correctness (covered by other cells). RESCUE-axis: only the KB load path
changed from v2; mechanism + bands identical.

## Failure (REJECT)

- `user_directive_mixing_violations > 0` (load-bearing invariant violated).
- `n_UD_in_sample == 0` (test vacuously satisfied; v1 failure mode).
- `recall_unclustered == 1.0` AND `recall_clustered == 1.0` at n=10k.
- ARM_RANDOM recall_clustered >= ARM_ULTRA recall_clustered.
- Ingest yields < EXPECTED_INGEST_ENTITIES_MIN entities (sub-cell-level fail).

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `summary.cardinality_ok`,
`summary.inline_kb_manifest`, `summary.seed_results[].ultra.n_user_directive_atoms`,
`summary.seed_results[].ultra.user_directive_mixing_violations`,
`summary.full_n_preview` (smoke only).

## Discipline gates

- Fix #26: pre-dispatch referent check N/A (cell is self-contained).
- PROT-022: no `# KB_REFERENT` declaration (cell builds its own KB; gate
  treats unmarked cells as referent-free, no override needed).
- META_RULE_H: cardinality_ok mandatory.
- META_RULE_J: USER_DIRECTIVE separation enforced as HARD_FAIL invariant.
- META_RULE_K: discriminator-must-survive-scale via ARM_FULL_N_PREVIEW at smoke.
- META_RULE_L: real-data evidence (real repo notes/memory/preregs).
- META_RULE_M: band-floor recall is MIDDLE_BAND; cap_drop > 0.20 AND gap >
  0.30 required for HARD_PASS.

## Estimated cost

Smoke: ~60-120s (chunk_ingest 50 files/class ~30-60s + n=600 + n=10k preview
single seed ~30-60s).
Full: ~8-20min (chunk_ingest 200 files/class ~2-5min + n=10000 x 3 seeds
~5-15min; pairwise dist memory ~400MB peak).

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive).
Push + queue_add via orchestrator (push is harness-DENIED to exp_dev).
