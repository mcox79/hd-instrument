# Pre-reg: kb_coarse_grain_at_promotion_v4_with_ud_detection (ANCHOR 3 v4 RESCUE; 2026-06-27)

**Anchor:** `kb_coarse_grain_at_promotion_v4_with_ud_detection`
**Cell:** `experiments/exp_kb_coarse_grain_at_promotion_v4_with_ud_detection.py`
**Queue:** `remote_cpu_queue` (NO LOCAL per USER 2026-06-27)
**Tier hint:** CHAIN_GRADE candidate (v3 design unchanged; only KB-population path widened).
**Wave:** Tier-2 rescue from `notes/skunkworks_landed_vet_5cell_batch8_2026-06-27.md` Cell 3.

## Parent (v3) finding being rescued

Skunkworks batch 8 (Cell 3) re-tiered parent v3 as
`HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO`. RC-1 invariant
(n_UD >= 10) halted CORRECTLY in protective direction: v3 was designed to
refuse vacuous mechanism (unlike v1 which silently passed at n_UD=0).
The cell-author design improvement is right; only the path-scope of the
self-contained build was wrong (USER directives live in
`~/.claude/projects/d--AI/memory/` cross-profile, not `<repo>/memory/`).

Per-class manifest from parent v3 run (filesystem-verified):
- `memory: n_files=0 n_chunks=0` (discovery succeeded; directory empty in repo)
- `note: n_files=200 n_chunks=1138`
- `prereg: n_files=200 n_chunks=1061`

Skunkworks's v4 recommendation: (a) pull memory from cross-profile dir
fallback + (b) content-based UD detection over notes/+preregs/. v4
implements BOTH.

## v4 mechanism (UNCHANGED from v3 chain-grade-path)

Same arms, same RC-1 (n_UD >= 10) + RC-2 (n_atoms >= 10000 cap-break) +
discriminator-must-survive-scale guard. Only the UD-population PATH
changed.

## v4 changes vs v3 (two; both behind selftest)

### Change 1: External-dir fallback (recommendation a)

If repo-relative `memory/` enumerates 0 files via the chunk_ingest plan,
splice in `~/.claude/projects/d--AI/memory/` files under the `memory`
class.

- Windows-portable path: `Path.home() / '.claude' / 'projects' / 'd--AI' / 'memory'`
- Glob: `*.md` (markdown only)
- Limit: same `max_files_per_class` as in-repo path (200 full / 50 smoke)
- Logged: `manifest._v4_external_memory_used`, `_v4_external_memory_dir`,
  `_v4_external_memory_files`
- On remote runner where the external dir doesn't exist, fallback silently
  produces 0 external files; recommendation (b) still catches in-content
  UDs via notes/+preregs/.

### Change 2: Content-based UD detection re-label (recommendation b)

After base chunk-ingest, post-pass walks each unique `source_path` in
`atoms.jsonl`, reads the original file content (REPO-relative -> external
fallback -> chunk content_tag), and if it contains any of:

- `USER:`
- `USER directive`
- `USER-locked`
- `USER LOCKED`
- `USER 2026-`
- `USER 2025-`

then all atoms with that source_path are re-labeled
`source_class='user_directive'`. Original class preserved as
`_ud_relabel_from`.

The detection regex is conservative (case-sensitive, explicit USER token)
to avoid mass-relabeling ordinary notes that mention "user" lowercased.

### UD class predicate widened

v4 `_is_ud_class(c)` returns True if `c in {'chunk_memory', 'user_directive'}`.
Sampler force-includes from BOTH; mixing invariant treats BOTH as the UD class.

## ARMS (4; identical to v3)

### ARM_NO_COARSE_GRAIN_BASELINE
Sanity rail. recall_unclustered = 1.0 by construction.

### ARM_COARSE_GRAIN_ULTRAMETRIC
Per-source-class ultrametric clustering. Forces n_UD >= 10 atoms (either
chunk_memory or user_directive) into the sample. USER_DIRECTIVE strictly
separated by construction.

### ARM_RANDOM_CLUSTER_COLLAPSE
Same cluster sizes from ARM_ULTRA; random membership. Tests whether
SEMANTIC clustering matters.

### ARM_FULL_N_PREVIEW (smoke-only; not relevant for NO_LOCAL dispatch)
Single-seed n=10000 ARM_ULTRA; flags saturation risk.

## PER-ARM HP-SCOPE (SCHEMA-VET 5b)

| Arm | HP gate | Scope |
|-----|---------|-------|
| ULTRA | cap_drop > 0.20 AND gap > 0.30 AND cv < 0.05 AND n_UD >= 10 AND mixing=0 | 3 seeds at n_atoms >= 10000 |
| BASELINE | sanity rail; no HP gate | per-seed |
| RANDOM | gap discriminator; no HP gate (used in ULTRA verdict) | per-seed |

## Pre-reg bands (HARD-LOCKED; v3 verbatim)

HARD_PASS requires ALL of:
- (a) `user_directive_retention == 1.0` (zero UD-class atoms clustered with
  non-UD; n_UD >= 10 verified present).
- (b) `recall_unclustered < 1.0` at n_atoms=10000 (cap-broken).
- (c) `capacity_drop_fraction > 0.20`.
- (d) `gap_vs_random > 0.30`.
- (e) `cv_recall_clustered < 0.05` across 3 seeds.

MIDDLE_BAND: cap_drop >= 0.10 AND gap >= 0.15 AND cv <= 0.10; one or more HP
bars not met.

HARD_FAIL: (a) violated, OR (b) saturated at 1.0 at n=10k, OR cap_drop <
0.10, OR gap <= 0.05, OR n_UD < 10 (RC-1 invariant), OR ingest yields
fewer entities than EXPECTED_INGEST_ENTITIES_MIN.

## Cardinality

`summary.cardinality_ok = (n_UD_in_sample >= 10) AND (n_atoms_full >=
10000) AND (n_seeds_full >= 3) AND (n_ingest_entities >=
EXPECTED_INGEST_ENTITIES_MIN_FULL)`.

EXPECTED_N_SEED_RESULTS at full = 3. HARD_FAIL on cardinality breach.

## Substrate-only-decode gate

n_llm_calls per arm = 0 (deterministic chunker + char-trigram encoder +
ultrametric clustering primitive; no transformers).

## Real data / synthetic provenance

100% real. Inline mini-KB built from notes/ + memory/ + preregs/ on the
runner's git checkout, with optional cross-profile memory dir fallback.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`, `summary.cardinality_ok`,
`summary.inline_kb_manifest`, `summary.seed_results[].ultra.n_user_directive_atoms`,
`summary.seed_results[].ultra.user_directive_mixing_violations`,
`summary.full_n_preview` (smoke only),
`summary.inline_kb_manifest._v4_external_memory_used`,
`summary.inline_kb_manifest._v4_n_atoms_relabeled_to_user_directive`.

## Discipline gates

- Fix #26 predispatch: v3 in atoms.jsonl as
  HONEST_NEGATIVE_INFRA_DEP_MEMORY_DIR_NOT_IN_REPO; v4 anchor differs (no
  duplicate flag).
- PROT-022: no `# KB_REFERENT` declaration (self-contained build).
- META_RULE_H: cardinality_ok mandatory.
- META_RULE_J: USER_DIRECTIVE separation enforced as HARD_FAIL invariant.
- META_RULE_K: discriminator-must-survive-scale via ARM_FULL_N_PREVIEW at smoke.
- META_RULE_L: real-data evidence (real repo + optional cross-profile memory).
- META_RULE_M: band-floor recall is MIDDLE_BAND; cap_drop > 0.20 AND gap >
  0.30 required for HARD_PASS.
- SCHEMA-VET 5b: per-arm HP scope declared.

## Estimated cost

Full at n=10000 + 3 seeds:
- chunk_ingest 200 files/class x 3 classes (+ external memory dir splice)
  ~2-5 min
- post-ingest UD relabel pass ~30-60s (reads ~600 unique source files)
- 3 seeds x (ULTRA + RANDOM) at n=10000 ~5-15 min total
- pairwise dist memory ~400MB peak

Total wall: ~10-25 min on remote_cpu.

## Routing

`remote_cpu_queue` on marsh@home (per USER 2026-06-27 NO LOCAL directive).
Push + queue_add via orchestrator (push harness-DENIED to exp_dev).

## Suggested --timeout

2700s (45 min) for ~10-25 min expected + 50% buffer + Windows-vs-Linux path
fallback overhead. Per queue_add formula: ceil(1.5 * 1500s) = 2250s; round
to 2700s for fallback edge cases.
