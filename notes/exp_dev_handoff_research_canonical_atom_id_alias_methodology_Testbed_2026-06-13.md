# exp_dev hand-off — research: canonical atom-id alias methodology for Testbed corpus hygiene during major re-shard

Filed-by: research sub-agent (Opus)
Trigger: research drill closed at notes/research_DRILL_canonical_atom_id_alias_methodology_Testbed_corpus_hygiene_during_rebuild_2026-06-13.md ; skunkworks INV-2a flagged variant atom IDs deflating cross-signal joins; major re-shard provides the atomic-swap window
Pause state: respect data/orchestrator_paused.flag — this hand-off is structural / discovery-only Stage 1-3 is safe under pause; Stage 4 (rewrite) requires unpaused exp_dev cycle.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHOR CANDIDATES and CONTEXT POINTERS only; exp_dev owns experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY, tier-1, ship-now-safe-under-pause): CELL ALIAS-DISCOVER
- Anchor pointer: build `data/atom_aliases.jsonl` via blocking + Jaro-Winkler matching over current shard atom IDs
- Substrate-product reading: closes corpus-hygiene gap visible to anyone auditing SHARES_MATH cross-signal joins; structural artifact LLMs cannot maintain
- Tier hint: tier-1 (low CPU, no queue burn, idempotent, measurement-only)
- Why-now: in-flight major re-shard is the natural atomic-swap window; alias map MUST exist before Stage 4 rewrite
- Pre-reg HARD-PASS: ≥ 90% precision on top-50 cluster audit (HP-1); ≥ 50% recall of known variant clusters (against manual seed list including hungarian_assignment/hungarian_algorithm + chu_liu_edmonds/chu_liu_edmonds_algo)
- Pre-reg HARD-FAIL: > 25% false-merge rate (HF-1) → raise JW threshold or add token-stem-match gate; < 50% recall (HF-2) → add second blocking pass

### Anchor 2 (SECONDARY, tier-1, gated by Anchor 1 audit): CELL ALIAS-MIGRATE
- Anchor pointer: rewrite atoms + relations through `canonical()` into next shard during the existing re-shard pass; CURRENT-pointer swap per prior atomic-swap drill
- Substrate-product reading: measurable cross-signal join lift on SHARES_MATH (HP-2); zero relation orphaning (HP-3)
- Tier hint: tier-1 (rides existing re-shard cycle; no separate queue burn)
- Why-now: same re-shard window; do it once, idempotent thereafter
- Pre-reg HARD-PASS: unique_targets(canonical) ≥ max(unique_targets(variant_i)) on the affected SHARES_MATH edges; 100% relation resolution post-migration
- Pre-reg HARD-FAIL: no measurable join lift (HF-3) → INV-2a premise refuted, document and move on; any alias-map cycle (HF-4) → policy is non-deterministic, fix before swap

### Anchor 3 (TERTIARY, deferred): CELL ALIAS-RUNTIME-RESOLVE
- Anchor pointer: wire `tools/canonical_id.canonical()` into every atom-load path; reload-on-mtime-change
- Substrate-product reading: legacy variant queries from cached probes resolve transparently
- Tier hint: tier-2 (lightweight refactor)
- Why-now: only after Anchors 1+2 ship; otherwise the canonical() function is identity-on-everything

## Context pointers (paths, not summaries)

- notes/research_DRILL_canonical_atom_id_alias_methodology_Testbed_corpus_hygiene_during_rebuild_2026-06-13.md — this drill (full design, code skeletons, falsifiable predictions)
- notes/research_DRILL_atomic_write_shard_swap_patterns_Testbed_operational_urgent_substrate_2026-06-13.md — prior drill, CURRENT-pointer swap pattern
- notes/exp_dev_to_research_BENCHMARK_ALIGN_CANONICAL_NEEDS_ROUTER_2026-06-12.md — upstream alignment signal
- notes/exp_dev_to_research_testbed_POST_CASCADE_INGEST_REMEASURE_CANONICAL_LIFTED_2026-06-12.md — recent canonical-lift datapoint
- notes/exp_dev_to_research_testbed_SHARES_MATH_222_unblock_KP_P3_MIDDLE_8_classes_AAA3_canonical_needs_tool_edges_2026-06-13.md — SHARES_MATH is the cross-signal join most likely lifted

## Contract section

- Idempotent: re-running migrate on a normalized shard is a no-op
- Reversible Stage 1-3: alias map can be rebuilt from scratch any time
- Stage 4 (rewrite) is destructive on the new shard ONLY; old shard remains intact via the CURRENT-pointer pattern; rollback = flip CURRENT-pointer back
- Pre-reg before Stage 4; measure HP-1/HP-2/HP-3/HP-4 post-Stage 4; honest report negative results (HF-3 means INV-2a was wrong)
- Smoke gate: dry-run migration on scratch copy before touching any shard the re-shard will swap to
- Self-test: `tools/canonical_id.canonical(x)` is identity for un-aliased x; transitive resolution forbidden (HF-4)

## Autonomy declaration

exp_dev owns: blocking key choice (token-stem default; may add bigram or n-gram if recall fails), matching threshold (Jaro-Winkler 0.92 default; may raise to 0.95 if precision fails), audit batch size (50 default), exact rapidfuzz vs in-house JW implementation, integration test layout, smoke-gate criteria specifics.

Research owns: methodology framing (this note); cross-thread linkage to atomic-swap drill; calibration of HP/HF thresholds.

Testbed owns: actual corpus, manual override file (manual_overrides.jsonl), the moment of swap, post-swap verification.
