# Testbed post-compaction handoff — 2026-06-13 (Cycle 51 close)

**Purpose:** Pickup point for next Testbed instance after compaction. Read this first.

## TL;DR state

- **MACRO 0.7233** on substrate-self-knowledge benchmark (HP_v1 0.70 HARD-PASS held; HP_v1+ 0.75 LOST after corpus growth from 1844 → 20,820 atoms)
- **Substrate growth this session**: 1844 → 1944 (T1 backfill batches 01-16) → 2944 (OEIS smoke) → ~20,796 (OEIS partial 18,952) → 20,820 (KP P1 + 24)
- **Branch**: `origin/testbed-cycle50-option-b` at commit `e4c0892c` (KP P1 promotion verdict + tool)
- **Macro retention HARD-FAIL** on Research MASTER PLAN T1.3 KPI (0.7518 → 0.7233 = -0.0285); honest verdict in commit e4c0892c

## Branch / worktree state (READ CAREFULLY)

- **D:/AI/hd-instrument** is on `main` branch, 133+ commits ahead of origin/main from LFS migration mess. **DO NOT push from this worktree.**
- **C:/Users/marsh/AppData/Local/Temp/clean-checkout** is on `kp-p1-promotion` branch tracking `origin/testbed-cycle50-option-b`. **USE THIS FOR ALL COMMITS + PUSHES going forward.**
- LFS migration P0.3 attempted twice by Research, failed at 49%. Handed off to Testbed. 525MB substrate_pos_tagger.npz still in HEAD tree. Force-push needs USER explicit auth (classifier blocks all options including --force-with-lease).

## Active in-flight + recent verdicts

| Item | Verdict | Commit |
|---|---|---|
| T1 algebra-dict backfill batches 01-14 + 16 | 100 atoms ingested COMPLETE | 1c211ea5 + b4491050 + f137d1e3 + 424dc1e8 + 56ff427e |
| L6-PROOF PHASE 2 prove subcommand | SHIPPED + EMPIRICALLY VALIDATED depth-2 (PP-376 PROVED via INSTANCE_OF chain) | 60bf3300 |
| HP_v1+ 0.75 HARD-PASS | MACRO 0.7518 hit Day 4 (composite-alias enrichment) | 00073a25 |
| Atomic-write fix (save_atoms + save_relations) per Exp-Dev ATOM_WRITE_RACE | SHIPPED | 56ff427e |
| Common mapper (facts.jsonl → atoms) | SHIPPED + SMOKE PASS (100K wikidata → 111 math atoms at 0.1pct retention with strict math vocab) | 96bcc330 |
| CELL 5 OEIS ingest | smoke 1000 PASS in 12.4s; full **KILLED at 18,952 atoms** (11h projection not worth waiting); download files on disk at data/external/oeis/ for resume | 96bcc330 |
| KP P1 frequency-promotion (24 T3→T2) | EXACT MATCH on atom count KPI; HONEST retention HARD-FAIL on macro KPI | e4c0892c |
| Atomic-write fix shipped to remote | DONE via scp (in-flight OEIS held old code; future writes are atomic) | (loose file) |

## External corpora downloaded on remote (4.37M facts; 29.5GB)

`C:/dev/hd-instrument/data/substrate_state/` on remote desktop:
- `arxiv_2m`: 234,352 facts (117K papers) — 1.83GB
- `conceptnet_8m`: 457,875 facts (8M CN rows) — 3.52GB
- `pubmed_5m`: 99,225 facts (60K abstracts) — 0.77GB
- `wikidata_truthy_50m`: 3,397,252 facts (5.7M triples sharded across 253 npy files) — 21.91GB
- `wikipedia_100k`: 184,354 facts (94K articles) — 1.43GB

All have pre-computed bge embeddings in `keys.npy` (or `keys_partial_NNN.npy`).

## Active unread Research routing notes (in chronological order)

1. `research_to_testbed_T1_ALGEBRA_DEPTH_2_DEPENDS_ON_BATCH_15_*` — depth-2 DEPENDS_ON edges
2. `research_to_testbed_T1_ALGEBRA_BATCH_17_DEEPER_DEPENDS_ON_targeted_62pct_*` — 150 edges targeting authoring-gap leaves
3. `research_to_testbed_exp_dev_RECURSIVE_SELF_IMPROVEMENT_LOOP_Stage_1_2_substrate_query_find_relevant_knowledge_compose_fix_SPEC_*` — substrate_query.py find-relevant-knowledge + compose-fix subcommands (~200 LOC pseudocode)
4. `research_to_testbed_exp_dev_SHARES_MATH_auto_discovery_cell_DESIGN_independent_structural_signals_*` — unblocks KP P3 + Pi/Sigma + CHTV-2
5. `research_to_testbed_exp_dev_CURRY_HOWARD_PI_SIGMA_substrate_query_py_80LOC_EXTENSION_SPEC_*` — Pi/Sigma type-construction subcommands (composes with prove)
6. `research_to_testbed_SMOKE_TO_FULL_CORPUS_DEGRADATION_ROOT_CAUSE_HEAPS_GOOD_TURING_FILTER_THRESHOLD_CURVE_NEW_METHODOLOGY_STACK_*` — new methodology stack
7. `research_to_testbed_exp_dev_MASTER_PLAN_Cycle_51_close_to_USER_vision_4_phase_path_*` — overarching plan
8. `research_to_testbed_exp_dev_USER_VISION_all_knowledge_on_substrate_LLM_class_language_mastery_COMPREHENSIVE_INGEST_ACCELERATION_ROADMAP_plus_recursive_self_improvement_loop_*` — vision doc
9. `research_to_testbed_PRODUCTION_SCALE_EXTERNAL_CORPUS_INGEST_5_CELL_DESIGN_Mizar_Wikidata_nLab_arXiv_Wikipedia_math_subset_USER_GOAL_aligned_*`
10. `research_to_testbed_CELL_1_MIZAR_INGEST_PARSER_SKELETON_*`
11. `research_to_testbed_BATCH_17_INGEST_GAP_recursion_optimal_substructure_absent_from_index_T1_5_ingest_priority_ACK_*`

## Blockers requiring USER decision

1. **LFS migration P0.3** — `git lfs migrate import --include="*.npz" --everything --yes` + `git push --force origin testbed-cycle50-option-b`. Research attempted twice (failed at 49% on gitobj error). Classifier blocks me on force-push without USER explicit message. NO progress until USER says go.
2. **Macro retention path** — Should we continue corpus growth (accept macro regression as cost) OR mitigate via mapper dedupe + bench partition isolation OR pause growth and recover macro first?
3. **LFS shared infra reset** — `git reset --hard origin/testbed-cycle50-option-b` on remote also blocked (shared infra); current remote diverged with duplicate-content commits.

## Next-turn priorities (per Research MASTER PLAN Phase 1+2)

In order of leverage:

- **R1.1 batch 17 ingest** — 150 DEPENDS_ON edges author-ready (corpus precondition for L6-PROOF FINDER depth jump 1.3 → 2.5+). Pure code, no blockers. **HIGHEST LEVERAGE: substrate self-math + L6-PROOF depth**.
- **R2.2 SHARES_MATH auto-discovery cell** — unblocks KP P3 + Pi/Sigma + CHTV-2 (multiple downstream).
- **T2.1 wikidata mapper full run** — needs vocab refinement first (smoke retention 0.1%); 3.4M facts → est 100K-340K math atoms. Wait for LFS unblock or bench-isolation strategy.
- **RECURSIVE_LOOP Stage 1+2** — substrate_query.py find-relevant-knowledge + compose-fix (~200-400 LOC).
- **Pi/Sigma extension** — composes with prove subcommand (~80 LOC per Research spec).

## Reusable infrastructure shipped

- **substrate_query.py prove** — 5-edge typing context backward-chaining proof unfolder; works at depth-2+ on existing INSTANCE_OF edges. Future: SHARES_MATH integration when RelationType extended.
- **substrate_facts_jsonl_to_atoms_v1.py** — common mapper for arxiv/conceptnet/pubmed/wikidata/wikipedia. Math/science vocab filter. Output: shard JSONL for phase6 ingest.
- **substrate_ingest_oeis_v1.py** — OEIS download + parse + ingest; --smoke (1000) or --full (370K); resumable via skip-existing.
- **substrate_promote_kp_p1_t3_to_t2.py** — KP P1 promotion via dataclass.replace(tier=T2) + SUPERSEDES edge.
- **Atomic-write save_atoms/save_relations** — temp + os.replace pattern; no more concurrent-reader races.

## Operational notes

- Event-bus Monitor `bi5d7ftfn` is running on local laptop (lightweight `tail -F data/events/testbed.log`). Don't restart unless it dies.
- Remote desktop runners (gpu_runner_0 + cpu_runner_0) were dead earlier; Exp-Dev restarted with `--idle-exit-minutes` raised.
- ALL CPU compute on remote desktop per memory `feedback-all-cpu-compute-on-remote-desktop-2026-06-11`. Local laptop = git + file IO only.
- Bench: `experiments/exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1.py` is the production bench (UNIFIED tuned-A + v3-B + bge-threshold-E + G-axis refined). ~3-15 min depending on bge cache state.

## Branch sync recipe (for next instance)

To pick up from a clean state:

```bash
# Use the clean-checkout worktree (has my latest work)
cd C:/Users/marsh/AppData/Local/Temp/clean-checkout
git fetch origin
git checkout testbed-cycle50-option-b
# or: git reset --hard origin/testbed-cycle50-option-b  (CLASSIFIER MAY BLOCK)

# Verify
git log --oneline origin/testbed-cycle50-option-b -3
# Should show e4c0892c (KP P1) at top
```

For pushing new commits: cherry-pick onto fresh branch from `origin/testbed-cycle50-option-b` then push to `testbed-cycle50-option-b` (fast-forward). This pattern avoided rebase conflicts from LFS hash divergence.

---

**Compaction is happening; this note is the pickup point.** Read TodoWrite todo list + this note to resume cleanly.
