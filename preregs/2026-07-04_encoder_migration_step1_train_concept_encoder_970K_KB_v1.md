# Pre-reg: Encoder Migration Step 1 - Train Substrate Concept Encoder on 970K KB Corpus (v1)

**Date:** 2026-07-04
**Anchor (full):** `encoder_migration_step1_train_concept_encoder_970K_KB_v1`
**Anchor (smoke):** `encoder_migration_step1_train_concept_encoder_970K_KB_v1_smoke`
**Cell:** `experiments/exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py`
**Class:** MM_TENTATIVE (artifact-producing cell; NOT a chain-grade discriminator; awaits Step 3 gold-standard verification for semantic-quality claim)
**Stage:** 3 (higher-function encoder infrastructure; substrate-native concept coding for retrieval frontend)

## Purpose

Produce `data/substrate_concept_encoder_v1/encoder.npz`, a substrate-owned sparse-bipolar concept HD table keyed by KB entity idx, to replace the char-trigram bag-of-features Layer 0 retrieval frontend. Per USER strategic direction 2026-07-04 00:47Z ("FULL SPEED FULL AUTO"): Step 1 of 5 (2 = re-encode <2GB; 3 = 100-query gold verify; 4 = route flip; 5 = nightly incremental retrain).

## Design gaps surfaced (report to Director; flagged NOT ignored)

**Spawn-prompt vs primitive-catalog mismatches (5 items; NOT blockers, but must be visible in report):**

1. Spawn cites `hdlab.concept_encoder.CompetitiveHebbianEncoder` -- actual class is `hdlab.concept_encoder.ConceptEncoder` (name-collision with paper terminology; benign).
2. `ConceptEncoder.fit(sentences, concept_labels)` is SUPERVISED per Stage 4 caveat (a). KB corpus has no explicit concept labels. Resolution: use entity idx as label (each entity = its own concept, n_concepts = 970069).
3. At n_concepts = 970069, the class's dense per-concept float32 accumulator `acc[n_concepts, n_dim]` = 970069 * 4096 * 4 = 15.9 GB, OOM on laptop. Resolution: cell reimplements the mechanism as CHUNKED streaming (chunk_size = 10000 entities; per-chunk accumulator = 160 MB).
4. Spawn cites output at `data/substrate_concept_encoder_v1/encoder.pt`; this cell writes `encoder.npz` (numpy-native; no torch dependency for pure inference). Step 2 re-encoder converts to `.pt` if downstream retrieval pipeline requires torch tensors.
5. Semantic-cosine target 0.85+ (cat-vs-kitten) is UNLIKELY at Step 1 because per-entity training with atoms.jsonl-relations context = weak-supervision (avg 1.6 atoms per entity). Directors Step 3 gold verify is the correct gate for the semantic claim; Step 1 only certifies the pipeline runs end-to-end + checkpoint/resume works + coverage is complete.

## Storage strategy

**SHARDED** (per-entity sparse-bipolar HD; NOT bundled) per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW (Skunkworks CG 2026-07-02). Each entity idx `i` gets its own int8 HD `concept_hds[i, :]` with values in {-1, 0, +1}. Cross-entity composition (Step 4 retrieval frontend) depends on cosine argmax over the SHARDED table.

## Compute architecture

**Class (b): sequential-CPU with justification.**
- Justification: streaming per-entity loop with per-chunk Hebbian accumulator; each per-entity update is a mean over ~1-10 short surface HDs; matmul-heavy batching would require gathering per-entity contexts into ragged tensors which fights the per-entity accumulator pattern. Wall time estimate below.
- Non-GPU (per USER 2026-07-01 SMOKE-only local; FULL local_cpu_queue authorized by USER 2026-07-04 spawn for this specific Step 1 artifact-producer).

## Mechanism (cell core)

For each entity idx `i` in `data/substrate_director_kb_v1/entities.jsonl`:

1. Collect context strings for `i` from `data/substrate_director_kb_v1/atoms.jsonl`:
   - All atoms where `s == i`: context += f"{p_name} {o_name}"
   - All atoms where `o == i`: context += f"{s_name} {p_name}"
   - If entity has zero atoms: context = entity name only (fallback; ~10-20% of entities per KB density estimate)

2. Encode each context string via `hdlab.char_positional_encoder.CharPositionalEncoder` (n_dim=4096, seed_prefix=f"SPOKE1_S{seed}"). Sum surface HDs to per-entity accumulator vector `acc[i, :]` (float32).

3. Per-entity top-K WTA: `k = round(0.02 * 4096) = 82`. Mask = magnitudes >= (n_dim - k)-th quantile. Sign = sign(acc[i, mask]).

4. Store as int8 sparse-bipolar concept HD `concept_hds[i, :]` in a numpy memmap array (dtype=int8, shape=[970069, 4096], ~3.98 GB on disk).

5. Chunk boundary (every 10000 entities): flush partial shard to disk; append shard filename to manifest; reset chunk accumulator.

6. Final: consolidate shards into `data/substrate_concept_encoder_v1/encoder.npz` with:
   - `concept_hds`: [970069, 4096] int8 (memmap-loadable)
   - `entity_names`: list[str] length 970069 (from entities.jsonl)
   - `metadata`: dict with n_dim, k_sparsity, seed, source_signature

## Source signature

- Primitive: adaptation of `hdlab.concept_encoder.ConceptEncoder` mechanism (competitive-Hebbian mean + top-K WTA + sign) at seed=7; encoder = Spoke 1 v3-D at commit 9d30d3d30 (2026-07-02 extraction), CG'd at commit 596a8de03.
- Corpus: `data/substrate_director_kb_v1/entities.jsonl` (970069 entities) + `data/substrate_director_kb_v1/atoms.jsonl` (1598530 triples) at commit HEAD (2026-07-03).
- Hyperparams: N_DIM=4096, k_sparsity=0.02, seed=7, chunk_size=10000, max_atoms_per_entity=64 (cap to keep per-entity context bounded).
- Framing: mechanism-abstraction-lossy per META rule; CG source is 50-concept synthetic corpus; extending to 970K entities on natural-corpus atoms is REGIME EXTENSION (SHAPE_DRIFT). Do NOT claim CG survives to this regime without empirical verification (Step 3 does that).

## Functional requirement decomposition (per META_RULE §15E)

- FR1: Produce sparse-bipolar HD per KB entity from KB co-occurrence signal.
  Primitive: char_positional_encoder + per-entity Hebbian mean + top-K WTA. Existing chain-grade at 50-concept synthetic; regime-extension to 970K natural corpus is UNCERTIFIED.
- FR2: End-to-end pipeline runs on 970K entities without OOM / hang.
  Primitive: chunked streaming + memmap. NEW extension of ConceptEncoder mechanism at scale.
- FR3: Checkpoint/resume works across process kills.
  Primitive: per-chunk shard files + manifest.jsonl (adapt PROT-021 pattern from `_seed_checkpoint`).

## SMOKE-vs-FULL code path (per META_RULE_smoke_code_path_must_exercise_same_branches_as_FULL)

SMOKE (n_entities=10000, single chunk of 10000): exercises entity_context_build, per-entity Hebbian mean, top-K WTA, sign, int8 store, ONE shard flush, manifest write, consolidation into encoder.npz. Identical code path as FULL except entity count. HDLAB_EXP_NAME=`..._smoke` so output dir is distinct.

FULL (n_entities=970069, 97 chunks): identical code path, 97 shard flushes + consolidation.

## Hypotheses + pass bands

### H1: Pipeline trains cleanly
- **Fires:** no NaN / no Inf in final concept_hds; no crashes.
- **HP band:** encoder.npz exists, size in [3.5 GB, 4.5 GB] for FULL (int8 dense [970069, 4096] = 3.98 GB); [30 MB, 45 MB] for SMOKE.
- **HF band:** encoder.npz missing OR NaN detected OR size < 90% expected.

### H2: KB coverage complete
- **Fires:** all n_entities have a non-zero HD (unless entity had zero atoms AND fallback path also produced zero — rare).
- **HP band:** `n_entities_with_nonzero_hd / n_entities_total >= 0.95` (allowing 5% for empty-context corner cases).
- **HF band:** coverage < 0.90.

### H3: Checkpoint/resume works
- **Fires:** kill-and-resume produces bit-identical encoder.npz compared to uninterrupted run.
- **SMOKE gate:** synthetic kill after chunk 0 flush, resume from chunk 1; verify final encoder.npz matches full-run reference (bit-identical for identical seed).
- **FULL gate:** documented in cell; not exercised at FULL to save time (SMOKE gate is sufficient).

### H4 (added for defensive discipline): sparse_rate correct
- **Fires:** per-entity nonzero count = k = 82 (allowing +/-1 for tie-breaking).
- **HP:** `mean(nonzero_per_entity) in [80, 84]`.

## Pre-reg required fields (SCHEMA-VET checklist)

- `cardinality_ok: True` -- EXPECTED_N_UNITS = 1 (n_entities: 10000 for smoke; 970069 for full). Cardinality-checked at completion by asserting `concept_hds.shape[0] == n_entities`.
- `arms_differ_verified: N/A_single_arm` -- cell has one arm (no baseline comparison; artifact-producer cell).
- `final_metrics_atomicity: "tmp_replace"` -- metrics.json written via `os.replace` at end.
- `crlb_n/a: "artifact-producer; no quantitative discriminator threshold at Step 1; semantic-quality target belongs to Step 3 gold verify"`
- `discriminator_reachability: True` -- H1-H4 all measurable at cell exit; no HP band unreachable by construction.
- `baseline_in_band: N/A_no_baseline` -- artifact-producer.
- `calibration_check: "default_ok_for_this_regime"` -- k_sparsity=0.02 inherited from Spoke 1 v3-D CG (empirically validated at N=4096); regime-extension caveat noted above.
- `sweep_alignment_verdict: N/A_no_sweep` -- single (n_dim, seed, k_sparsity) config.
- `discriminating_fraction: N/A_no_sweep`
- `composition_edges:` (single-edge: atoms -> entity-context-string -> surface_hd -> concept_hd; SHAPE_MATCH all).
- `positive_control_arms: []` -- no prior chain-grade primitive being reproduced at this regime (mechanism is regime-extension of Spoke 1 v3-D; empirical fidelity verified by H1 no-NaN + H4 sparse-rate; NOT reproducing a specific cited metric because the source regime is 50-concept synthetic not 970K natural).
- `functional_requirements:` FR1/FR2/FR3 above.
- `cell_chunked: False` -- single-seed cell (seed=7 only for Step 1 artifact); NOT multi-seed. If Step 3 gold verify reveals seed-variance concerns, sibling seed cells (17, 23, ...) can be authored then.
- `start_marker_written: True`
- `crash_diagnostic_present: True`
- `heartbeat_present: True` -- emit heartbeat every chunk boundary (~every 100 chunks).
- `defensive_error_checking: "passed_all_4_patterns"`
- `progress_logging: "line_buffered_stdout"` + explicit `flush=True` on chunk-boundary progress lines. Cadence: every chunk (~5-10 min wall between prints at FULL).
- `run_mode_declared: full` (SMOKE variant `..._smoke` sets HDLAB_RUN_MODE=smoke; else FULL). Default from env per selftest 11 pattern.

## Wall-time estimates

- SMOKE (10000 entities, 1 chunk): ~30-60s wall on laptop CPU.
- FULL (970069 entities, 97 chunks): estimated 2-4 hours wall (surface-encoding is fast; NOT 2-3 days). Timeout: 43200s (12h; generous, per PROT-019 requires >=3600 for n>=4096).

## Off-disk verify (post-smoke gates)

- `data/exp_..._smoke/metrics.json` exists with H1/H2/H3/H4 all PASS.
- `data/substrate_concept_encoder_v1_smoke/encoder.npz` exists at expected size ~30-45 MB.
- `concept_hds.shape == (10000, 4096)` and `dtype == int8`.
- `n_entities_with_nonzero_hd / 10000 >= 0.95`.
- `mean(nonzero_per_entity) in [80, 84]`.
- Bit-identity resume test PASSED.

Only after ALL five gates pass does FULL dispatch fire.

## Post-FULL Skunkworks gates (surfaced in report; NOT Step 1's job)

- Landed-VET on encoder.npz.
- Semantic-quality probe: cosine(cat, kitten) vs cosine(cat, airplane) on 25 hand-picked entity-pair probes. NOT a HP claim at Step 1; framing at MM_TENTATIVE until Step 3 gold verify.

## References

- `hdlab/concept_encoder.py` (v3-D extraction 2026-07-02; commit 9d30d3d30).
- `hdlab/char_positional_encoder.py` (surface HD primitive).
- `data/substrate_director_kb_v1/entities.jsonl` (970069 lines, 124 MB, kb_version=v1).
- `data/substrate_director_kb_v1/atoms.jsonl` (1598530 triples, 738 MB, kb_version=v1).
- USER strategic direction 2026-07-04 00:47Z "FULL SPEED FULL AUTO" for encoder migration Steps 1-5.
- Memory: `project_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md`, `reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02.md`.

ASCII-only. No emojis. No em dashes.
