# Step-1 re-encode migration plan: vector-space inventory, unique-id fix, BCT procedure, gates

**Date:** 2026-07-04. **Type:** design + scope only (NO re-encode executed). **Author:** Testbed (integrator).
**Parent:** `notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md` (step 1).
**Encoder-independent by construction:** holds for regime-switch v1 (3.125% sparse KEY + isotonic dense
VALUE, band 0.55-0.65) OR a GSBC single-code upgrade if its run clears. Only the TIMING of the bulk
re-encode is fork-sensitive (encode onto the settled ship).

## 0. TL;DR
- **Recommended first step-1 action:** land the qualified-id uniqueness fix (namespace + assert +
  `Store.add_atoms_strict`) in the cache-builder / re-encode path, THEN (re)build and id-assert the
  canonical FULL teacher cache -- which is NOT on local disk right now (see 3.1).
- **Top risk:** mixed-encoder store -- any partial/blind re-encode, a missed external cache, or an
  unresolved cross-lane id collision strands some atoms on BGE and some on the sparse code -> cross-
  retrieval collapses to ~1% SILENTLY (measured, not hypothesized).

---

## 1. VECTOR-SPACE INVENTORY (three spaces; which paths read which; blast radius)

The substrate holds THREE distinct representations. They are NOT interchangeable and the encoder governs
exactly ONE of them. Verified against code + disk.

### Space 1 -- char_trigram_v1 lexical KB index  (OUT OF RE-ENCODE SCOPE)
- **On disk:** `data/substrate_director_kb_v1/` (E.pt ~970k entities x 2048-dim; float16 sidecar
  `E_unit_fp16.npy`).
- **Encoder:** `hdlab/char_trigram_encoder.CharTrigramEncoder` -- a LEXICAL char-trigram hash of raw
  text. NOT learned, NOT distilled from BGE.
- **Query paths that read it:** `hdlab/director_kb_query.DirectorKBQuery.query()` ->
  `tools/director_kb_query.py` CLI -> the SESSION STARTUP RITUAL (POST_COMPACTION backup retrieval;
  `filename_contains` bypass) and Director dogfood KB queries. Also consumed broadly by the language/
  cortex stack: `hdlab/atom_consultation.py`, `intent_classifier.py`, `generation.py`, `vwfa.py`,
  `hippocampal_encoder.py`, `token_vocab.py`, `layer_075_structural_slot_filter.py`, `kg_traversal.py`,
  `substrate_router/api.py`.
- **What breaks if re-encoded blindly:** CATEGORY ERROR. The concept encoder consumes BGE-large teacher
  vectors (1024-dim) as INPUT, not raw text -- it cannot encode char_trigram KB entities (filenames /
  chunk strings). Overwriting E.pt with 4096-dim concept codes trips the dim assert in
  `_load_or_build_e_unit` (`director_kb_query.py:252-255`, n_dim=2048) and breaks every char_trigram
  consumer (dim + encoder mismatch). **Leave this space untouched in step 1.** Its only step-1 relevance
  is the addressability audit (section 4).

### Space 2 -- BGE teacher vectors  (THE RE-ENCODE TARGET)
- **On disk:** `data/substrate_index/cached_indices/bge_large_v2_name_*.npz` (keys: `semantic`,
  `composite`, `id_order_json`). Backing atoms = `backend/substrate_index/partition.PartitionedStore`
  at `data/substrate_index/` across 12 lanes. Disk counts (2026-07-04): math 29043, concept 142219,
  science 5147, verdict_history 247, research_history 449, decision_history 468, findings_history 60,
  results_history 21, meta 375, school 13, methodology 1, memory_history absent -> ~178k atoms, matching
  the canonical `..._177899_...` cache count.
- **Encoder:** `backend/substrate_index/encode.AtomEncoder` (BGE-large; `semantic` dim; `composite`
  additionally binds tier+corpus tags).
- **Query paths that read it:** `backend/substrate_index/retrieve.Retriever.semantic()` / `.hybrid()` /
  `.algebraic()` over the float32 `_semantic_matrix` / `_composite_matrix` (cosine). Downstream consumers
  of `Retriever.semantic`: `self_knowledge.py`, `reason.py`, `meta.py`, `discover.py`, `algebra_index.py`,
  `validate.py`, `cli.py`, `refuse_gated_retriever.py`, plus the `tools/substrate_benchmark*`,
  `substrate_eval_*`, `substrate_evolve_*` ingest/eval tools.
- **What breaks if re-encoded blindly:** THIS is the intended target (the encoder distills BGE), but a
  naive re-encode hits the exact step-0 finding -- the dup-id collapse (section 2) silently drops atoms;
  and the representation dim changes (BGE semantic dim -> 4096 KEY/VALUE), so any consumer hardcoding the
  BGE dim, and the store's cosine metric, must be re-validated (step-0 Gate C already proved float32
  cosine survives -- carry that assertion forward).

### Space 3 -- new sparse concept code (regime-switch v1)  (WHAT WE INSTALL)
- 3.125%-sparse HARD block KEY (KB=128, BLK_L=32 -> 4096-dim) for storage / addressing / bind-unbind
  ALGEBRA; isotonic-calibrated dense sign VALUE (4096-dim) for RETRIEVAL. Retrieval band 0.55-0.65.
- Not yet wired to any operational path; only exercised by step-0 integration-verify
  (`exp_regime_switch_encoder_instore_integration_verify_v1`, HARD_PASS on smoke ckpt). Step 1 installs
  it as the replacement for Space 2.

**Net scope:** step-1 re-encode = replace Space 2 (BGE teacher vectors backing the `substrate_index`
PartitionedStore + Retriever) with Space 3. Space 1 (char_trigram KB) is untouched.

---

## 2. UNIQUE-ID FIX (exact mechanism + where it goes)

### Root cause (structural, confirmed in code)
`PartitionedStore.all_atoms()` (`partition.py:143-147`) flattens atoms across all 12 partitions using
the BARE LOCAL id (`[a.id for a in atoms]`). Each partition Store is INDEPENDENTLY id-keyed on the local
id (`store.py:137-138` `_by_id[atom.id]=atom`), so the SAME local-id string legitimately exists in more
than one lane (e.g. `math::PP-364` and `concept::PP-364`). When that flattened list becomes atom ids in a
single id-keyed target Store, `Store.add_atom` treats the second as an UPDATE (`store.py:143`
`is_update = atom.id in self._by_id`) and silently overwrites. Step-0 measured it: 1500 submitted ->
1497 stored, 3 collisions, teacher cache `bge_large_v2_name_1742_49029a5d.npz`.

`PartitionedStore.all_qualified_ids()` (`partition.py:149-154`) already emits collision-free
`corpus::local_id` ids -- the fix is to route the aggregate through THAT, not `all_atoms()`.

### Fix -- 3 layers of defense (namespace + assert + strict add)
1. **Namespace (root):** build the aggregate id list as qualified ids
   `f"{corpus.value}::{atom.id}"` (iterate `PartitionedStore._stores.items()`), never bare `a.id`.
   Collision-free by construction. Apply in `tools/substrate_prebuild_bge_index_cache_2026-06-18.py:49`
   (`id_order = [a.id for a in atoms]`) and in the new re-encode driver.
2. **Pre-write assert (guard):** before any store write,
   `dups = [i for i,c in Counter(ids).items() if c>1]; assert not dups, f"{len(dups)} id collisions: {dups[:20]}"`.
   Surfaces cross-lane collisions (including the wikipedia-in-math-lane class, section 4) instead of
   losing them.
3. **Strict bulk add (belt+suspenders):** add `Store.add_atoms_strict(atoms)` in
   `backend/substrate_index/store.py` that RAISES on `atom.id in self._by_id` (a re-encode is a fresh
   rebuild, never a legitimate update). Follow with a post-write completeness assert
   `atoms_written == atoms_submitted == len(set(ids))`.

Additional read-side guard: add a dup-id raise in `_load_teacher`
(`exp_encoder_migration_step1b_v3_..._core.py:294`) so no downstream cell silently proceeds on a
collapsing cache.

**Placement summary:** builder `tools/substrate_prebuild_bge_index_cache_2026-06-18.py`;
`backend/substrate_index/store.py` (new strict add); `_load_teacher` in the v3 core (read guard);
NEW `tools/substrate_reencode_concept_encoder_v1.py` (qualified ids + pre/post asserts) -- authored via
hdi_exp_dev / hdi_orchestrator, single-writer, NOT hand-rolled in main thread.

---

## 3. BCT RE-ENCODE PROCEDURE (ordered; parity check; rollback)

Reuse `encode_key_value()` from the integration-verify cell (loads `_ckpt_HARD_STE.pt` KEY +
`_ckpt_ANNEAL_STE.pt` VALUE, no retrain).

### 3.0 Precondition gate (entry)
- Step-0 integration-verify PASS (HARD_PASS on smoke; re-run on the FULL checkpoint at ship).
- Encoder fork SETTLED (do NOT re-encode onto a checkpoint about to be superseded by lever B / GSBC).
- BCT status known: shipped checkpoint trained WITH the BCT compat loss (w=0.15, anchored to prior rep;
  `exp_encoder_bct_compatibility_loss_v1` HARD_PASS restores cross-version min_ratio 0.0->0.887) OR, if
  first-encode into a fresh concept space (no comparable learned prior), plan an ATOMIC full rebuild of
  every consumer so no old cached vector survives mixed.

### 3.1 Build + id-assert the canonical FULL teacher cache  (**precondition, currently BLOCKING**)
`data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz` (the FULL teacher the v6
certify/probe tools point at) is **NOT on local disk** (largest present = `..._43905_...`, 2026-06-19).
(Re)build it via the fixed `substrate_prebuild_bge_index_cache` (qualified ids + uniqueness assert) or
fetch from remote. The re-encode reads teacher vectors from it; do not proceed without it.

### 3.2 Snapshot (rollback anchor)
Copy `data/substrate_index/` (all 12 partition dirs + `cached_indices/`) to a timestamped snapshot dir.

### 3.3 Pre-re-encode retrieval-parity BASELINE
On a FIXED held probe set (500-2000 atoms), run the CURRENT path (`Retriever.semantic` over BGE) and
record top-10 neighbor sets + self-rank1. This is the parity reference for 3.6.

### 3.4 Re-encode (single-writer, atomic)
(a) load teacher cache (qualified ids, uniqueness asserted); (b) `encode_key_value` -> KEY (sparse) +
VALUE (dense), both float32 (M,4096); (c) if a version swap, confirm BCT anchoring (target cross-version
min_ratio >= 0.5); (d) write via `Store.add_atoms_strict` into a `.tmp` store, then `os.replace` swap
(partition writes are NOT concurrency-safe -- single writer only); (e) rebuild the Retriever
`_semantic_matrix`/`_composite_matrix` AND the npz cache over the NEW vectors (never leave the index
pointing at stale vectors).

### 3.5 Completeness assert
`atoms_reencoded == atoms_in_store == n_unique_qualified_ids`; ZERO atoms stranded in the old BGE space.

### 3.6 Post-re-encode parity + acceptance
Re-run the 3.3 probe through the NEW path: ret_agree10 within +/-0.03 of the step-0 in-situ level,
self-rank1 >= 0.95. If a version swap: re-run `exp_encoder_cross_checkpoint_retrieval_compat` as the
acceptance gate -> cross-version min_ratio >= 0.5 (BCT floor). Carry step-0 Gate C forward (float32,
unit-norm rows, dim 4096, cosine metric intact).

### 3.7 Rollback
Any gate fails -> `os.replace` the 3.2 snapshot back (atomic restore). BCT is the deeper insurance:
because every version is anchored, re-encoding again when the encoder improves (v1->v2) is non-breaking,
so a premature or failed re-encode is recoverable, not fatal.

---

## 4. ADDRESSABILITY-BREACH AUDIT (fix-or-defer per breach)

- **5000-line KB cap** (Space 1, char_trigram director_kb): **FIXED on disk.**
  `config/director_kb_schema.json:76` `jsonl_max_lines_per_file: 200000` (was 5000); `director_kb.py:260`
  `hard_cap = 2000000` (was 50000); comment cites the 2026-07-03 fix for math-atoms-unqueryable.
  -> **DEFER / NO-OP for step-1 re-encode** (it governs Space 1, out of scope). Residual, tracked under
  step-2 ingest not step-1: re-confirm the canonical char_trigram KB was REBUILT after the cap bump so
  previously-truncated math atoms are actually present (a director_kb rebuild, not a Space-2 re-encode).

- **wikipedia-in-math-lane** (Space 2, `math` partition = 29043 atoms; ~17 mis-filed wikipedia atoms):
  a lane-assignment (corpus-routing) breach. Interaction with re-encode: a mis-filed atom re-encodes
  FINE under its qualified id `math::<id>` -- lane mis-assignment is NOT a re-encode blocker BY ITSELF.
  BUT it is the exact cross-lane collision vector the section-2 assert guards: if the same wikipedia atom
  also exists in another lane with the same local id, that is the dup-id collapse.
  -> **DEFER the re-filing** (data-quality cleanup; low count; not a retrieval-correctness blocker under
  qualified-id addressing) UNLESS the 3.4 pre-write qualified-id uniqueness assert flags a
  `math::X` vs `<other>::X` collision -- then **FIX** (re-file / dedup) before re-encode, because a
  flattened consumer would otherwise silently overwrite one with the other. The pre-write assert is the
  detector; wire the audit into it rather than a separate scan.

---

## 5. THE GATE -- step 1 succeeded iff ALL of

1. **Completeness:** `atoms_reencoded == atoms_in_store == n_unique_qualified_ids`; zero stranded atoms.
2. **No id collisions:** pre-write qualified-id uniqueness assert clean (0); post-write store count ==
   submitted count.
3. **Retrieval parity:** post-re-encode known-item ret_agree10 within +/-0.03 of the step-0 in-situ
   level; self-rank1 >= 0.95; (version swap) cross-version min_ratio >= 0.5 with
   `cross_checkpoint_retrieval_compat` re-run as acceptance gate.
4. **Index consistency:** Retriever matrix + npz cache rebuilt over the NEW vectors (float32, unit-norm
   rows, dim 4096, cosine metric intact -- step-0 Gate C forward); no stale-index pointer.
5. **Rollback available:** snapshot exists and the `os.replace`-back restore is dry-run verified.

Bounded scope: this memo is inventory + procedure + gates. No re-encode is executed here.
