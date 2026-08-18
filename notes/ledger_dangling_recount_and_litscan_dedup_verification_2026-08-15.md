# Ledger-dangling recount (12 vs 29 dispute resolved) + litscan-dedup verification

Covers the 12 `ledger-dangling-*` and 4 `litscan-dedup-*` dispatch-queue items. Both groups
independently verified off disk; no edits made to `notes/RECOVERY_PROGRAM.md` (ownership
unclear per the dispatch briefs — findings below are for the owner to fold in) and no
deletions attempted.

## PART 1 — the dangling count: 12 is right, not 29, and here is why

**RECOVERY_PROGRAM.md sec 5.7 says 12.** `.claude/scan-out/ledger-validity.json`
(agent `skunkworks`, tool `tools/ledger_validity_audit.py`) says `"NO-ARTIFACT": 29`. Both
numbers are real outputs of real passes — they are not in conflict because they are answering
different questions.

**Why they differ, established by reading `tools/ledger_validity_audit.py` and cross-checking
every one of its 29 NO-ARTIFACT rows against RECOVERY_PROGRAM.md's own row text:**

1. **`ledger_validity_audit.py` parses ALL `| # | system | ... |`-shaped tables in the merged
   974-row ledger** (`parse_rows()`, `tools/ledger_validity_audit.py:59`), including RP's
   **Group F** ("capabilities that fell off across the six review renames — module plane") and
   **Group G** ("the index machinery itself"). Its `resolve()` then tries to match every row's
   name to a `data/<dir>/metrics.json`. **17 of the 29 rows are not experiment cells at all** —
   they are citations of `hdlab/*.py` module files, `data/capability_registry.jsonl`,
   `data/substrate_index/meta/cert_ledger.jsonl`, note files, or (F4/F5/F7) rows whose OWN text
   already says "NOT LOCATED" / "no directory under this name" as a finding about missing
   *source code*, not a missing *result*. Applying a metrics.json-directory resolver to these is
   a category error: RECOVERY_PROGRAM's own Group F/G table already resolves and states
   `STATE:VERIFIED` / `FOUND` / `SHELVED` / `WIRED` for every one of them, in-row, with the real
   artifact named (e.g. F1 `glass_box_loop` -> `hdlab/glass_box_loop.py`, **EXISTS 19,174 B**;
   G1 `the cert ledger` -> `data/substrate_index/meta/cert_ledger.jsonl`, **2,031 rows**). None
   of these 17 was ever claiming a `data/*/metrics.json` artifact, so "does not resolve to one"
   is not a defect.
2. **2 more are genuine parser bugs in `ledger_validity_audit.py`, not real absences:**
   - `A14` (resonator peel family siblings): its evidence column cites
     `` `data/exp_resonator_theta_gamma_peel_v1/`, `data/exp_resonator_deflation_lowsnr_v1/` `` —
     **two real, existing directories** (confirmed: both present on disk) — but neither citation
     ends in `metrics.json`, and the parser's regex
     `r'(data/[A-Za-z0-9_./{},-]+metrics[A-Za-z0-9_.-]*\.json)'` requires that literal suffix, so
     it extracts no `evidence_path` and falls through to prose-name matching, which fails.
   - `D8` (heterogeneous plasticity / STDP fair harness): evidence column is
     `` `data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness*/metrics.json` `` —
     the `*` wildcard breaks the same regex's character class (no `*` in it), so the match fails
     entirely even though RECOVERY_PROGRAM's own row already says "(resolved by prefix, 1
     match)" and is `STATE:VERIFIED, HARD_PASS`.
   - `B11` (whitening module) is the third borderline case but is really case (1): its evidence
     is `` `hdlab/whitening.py` `` (**confirmed EXISTS, 5,852 B**), a module citation, not a cell.
3. **The remaining 12 of the 29 are exactly RECOVERY_PROGRAM's own sec 5.7 list** (F1/F4/F16/F17
   from the chain-graded Group CG-F table, R25/R166/R167/R168/R170 from the reading-tier Group R
   table, F11/G3/G5 from RP's own Group F/G — confirmed by rid cross-reference). The 29-row
   audit is a **strict superset** of the 12; it finds zero new genuine dangling rows and 17 false
   positives from asking a directory-resolver a question about rows that were never directory
   claims.

**Conclusion: 12 is the correct count of rows citing an experiment-cell artifact that does not
resolve to a `data/` directory. The 29 figure should not be quoted as a corrected or larger
dangling count — it conflates 12 real dangling-or-recoverable rows with 17 category-mismatched
module/infrastructure citations that were already resolved in their own row text, plus 2 rows
lost to two narrow regex misses in the newer script.** (Non-blocking, for whoever owns
`ledger_validity_audit.py`: fixing the `metrics` requirement in the evidence-path regex to also
accept a bare directory ref, and excluding Group F/G's `| # | system |` tables — or better,
tagging rows by whether their `system`/`evidence` column names a `data/` artifact at all before
resolving — would make the two counts agree without any change to RECOVERY_PROGRAM.md.)

## PART 2 — the 12 rows themselves, re-triaged (enumeration method stated)

**Method:** for each row, pulled the fuller verdict/date text from the pre-merge source ledgers
(`notes/recovery_ledger_chaingraded_tier_2026-08-14.md`,
`notes/recovery_ledger_reading_tier_2026-08-14.md`), then (a) searched `data/` for directories
matching the cited name under progressively looser rules (case-insensitive, no `exp_` prefix,
content-fingerprint match against the verdict string embedded in the cited name), and (b) for
rows citing an atom, pulled the atom's full record from
`data/substrate_index/meta/cert_ledger.jsonl` (4.55 MB, one JSON object per line) to read its
`referent_pointer.per_seed_metrics_paths` / `per_seed_atoms` fields directly. Every existence
claim below was opened and read with `.venv/Scripts/python.exe`, not inferred from a name match.

| row | was (sec 5.7) | now | evidence |
|---|---|---|---|
| RP-F11 | not a cell | **NOT-A-CELL, confirmed** | `data/capability_registry.jsonl` exists; this is F11 in RECOVERY_PROGRAM's own Group F table, `STATE:VERIFIED` |
| RP-G3 | not a cell | **NOT-A-CELL, confirmed** | `data/capability_registry.jsonl`, 127 rows, exists |
| RP-G5 | not a cell | **NOT-A-CELL, confirmed** | `data/_archaeology_*` files exist; no result dir was ever claimed |
| CG-F1 | genuinely absent (1 token match) | **ARTIFACT-EXISTS — fix the link** | Full atom `math::T3/EXP_chain_grade_barrier1_..._2026-06-28` in cert_ledger.jsonl carries a *populated* `per_seed_metrics_paths`: `data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_{11,13,19}_v1/metrics.json`. Opened all 3: verdict `MIDDLE_BAND` on every seed, matching the atom's own per-seed names exactly |
| CG-F4 | genuinely absent; 1 candidate flagged "not a match" | **still UNRESOLVED, now for a documented reason** | The atom (`math::T3/EXP_narrative_q3_temporal_sequence_replay_K20_3seed_HP_CG_Q15_1.000_2026-07-01`) was created by `back_fill_cert_ledger` at commit `a8dfb00b7` with **`referent_pointer.metrics_path: null`** — never populated, not a prose bug. That same backfill batch (5 sibling atoms, commit `a8dfb00b7`, "batch atomize +2 CG +2 MM +1 HF") left **4 of its other 5 atoms with `metrics_path: null` too** — this is a batch-wide gap, not a one-off, and worth flagging as its own cluster. The one directory-name candidate RECOVERY_PROGRAM flagged (`exp_narrative_q3_v2_q15_seed{7,13,19}_full`) is now **ruled OUT, not just uncertain**: its 3 seeds read `MIDDLE_BAND` / `HARD_FAIL` / `HARD_FAIL`, contradicting the row's cited `HARD_PASS` |
| CG-F16 | write-path bug (`"metrics.json (ssh pulled)"`) | **ARTIFACT-EXISTS — fix the link** | Content-fingerprint match: the cited verdict text embeds `n_disc_20_21_20_of_27_cv_0p028_disc_frac_0p7407_0p7778_0p7`. `data/exp_cross_modal_binding_4_5_modality_v1_seed_{7,13,19}/metrics.json` read `n_discriminating_points` 20/21/20 of 27, `discriminating_fraction` 0.7407/0.7778/0.7407 — exact match, all 3 `HARD_PASS` |
| CG-F17 | write-path bug (`"see per_seed_metrics_paths in atom metadata"`) | **ARTIFACT-EXISTS — fix the link** | The atom's own `per_seed_metrics_paths` field does not actually exist (the pointer prose was aspirational), but the atom_id itself names the real cell: `EXP_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_..._dom_rate_min_0p911_max_0p929...`. `data/exp_substrate_time_decay_eviction_phase_diagram_v2_Pareto_AUC_seed_{7,13,19}/metrics.json` all read `HARD_PASS`, verdict text "TIME_DECAY_EVICTION dominates RANDOM ... NET dominance >= 70%" — matches |
| RD-R25 | genuinely absent (2 token match) | **ARTIFACT-EXISTS — fix the link** | `data/dependency_context_codebook_weight_sweep_location_artifact_v2_smoke/metrics.json` exists, mtime 2026-07-20 matching the ledger's cited date exactly, verdict `HARD_PASS_BORDERLINE_SWEET_SPOT_FOUND_W_0.9`. **Missed by every resolver because the directory has no `exp_` prefix** — the same blind spot sec 5.7 already documented for 4 of the old "53 dangling links" ("4 are literal directory names the join's `exp_`-prefix alias rule cannot see"), here recurring in the 12-row list itself. Caveat: `run_mode=smoke`, not full |
| RD-R166 | genuinely absent (1 token match) | **GENUINELY-ABSENT, confirmed by wider search** | Searched with and without `exp_` prefix for `perceptual_grounding`, `grounding_gap`, `grounding_gap_audit`: nothing on disk |
| RD-R167 | genuinely absent (2 token match) | **ARTIFACT-EXISTS — fix the link** | `data/derived_filler_typing_single_edge_grounding_v1_smoke/metrics.json`, mtime 2026-07-20 matching cited date, verdict `MIDDLE_BAND_DERIVED_TYPING_PARTIAL`. Same no-`exp_`-prefix blind spot as R25. Caveat: `run_mode=smoke` |
| RD-R168 | genuinely absent (1 token match) | **GENUINELY-ABSENT, confirmed by wider search** | Searched with and without `exp_` prefix for `af43a6dd`, `atomic2019`, `grounding_feasibility`: nothing on disk. Closest is `exp_goal_intention_feasibility_probe_v1`, a different topic (shares only the token `feasibility_probe`) |
| RD-R170 | genuinely absent (2 token match) | **ARTIFACT-EXISTS — fix the link, different SHAPE** | Not a `data/<dir>/metrics.json` at all — a loose top-level file, `data/probe_fix_tier_verb_semantic_ceiling_v1_summary.json`, whose own `probe_name` field reads `"probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_2026-08-02"` (near-exact match to the cited name) and which self-declares `"cross_check_matches_metrics_json": true`. Verdict `REDIRECT`. Every resolver (RECOVERY_PROGRAM's 4-stage and `ledger_validity_audit.py`'s) only scans `data/<dir>/metrics.json`, so a loose top-level `.json` artifact is invisible to both by construction |

**Net: of the 12, 3 are correctly not-cells (unchanged), 6 recover to a real, opened, read
artifact (CG-F1, CG-F16, CG-F17, RD-R25, RD-R167, RD-R170), and 3 remain genuinely absent after
a wider search that also tried dropping the `exp_` prefix and searching loose top-level files
(CG-F4, RD-R166, RD-R168).** None dropped; CG-F4 is now flagged as part of a larger 5-atom
backfill-orphan cluster from commit `a8dfb00b7` worth a dedicated pass. Per every dispatch
brief's instruction, `notes/RECOVERY_PROGRAM.md` was **not edited** — this note names the exact
paths so the owner can fold the 6 link-fixes and the CG-F4 cluster note in without re-deriving
them.

## PART 3 — litscan-dedup: all 4 pairs confirmed genuine duplicates, safe to remove

**Re-verified independently (did not trust the prior agent's claim) by diffing both files in
each pair and grepping for citations across `notes/` and `preregs/`.**

For every one of the 4 pairs:
- `diff` produces exactly 3 hunks, all confined to the first ~15-30 lines (title/header/
  provenance framing). `diff <(tail -30 A) <(tail -30 B)` is **empty for all 4 pairs** — the
  scan bodies are byte-identical.
- The **longer-named file in each pair is committed** (`git log -1` on all 4 returns commit
  `39f3fe2a1`, "Graded path does NOT clear the orthographic floor..."), `git status --porcelain`
  is clean for all 4.
- The **shorter-named file in each pair is untracked** (`??` in `git status --porcelain`).
- The longer-named files are the ones actually **cited** — by
  `notes/brain_drill_how_meaning_is_stored_and_separated_2026-08-14.md` (as the "4 rescued
  `lit_scan_*_2026-08-14.md`" scans STATUS.md's TOP ITEM references),
  `notes/graded_path_does_not_clear_the_orthographic_floor_2026-08-14.md` (with per-file char
  counts), and `notes/scan_out_assembled_2026-08-14.md`.
- The shorter-named files appear in exactly one place in `notes/` —
  `notes/scan_out_assembled_2026-08-14.md` line 283, which already names all 4 as "four
  redundant duplicate lit-scan notes... on disk, uncommitted and unreferenced" (this is the
  `rm`-denied-and-disclosed agent the dispatch brief refers to). No hit in `preregs/` for any of
  the 4 short names.

| pair | canonical (committed, cited) | redundant (untracked, uncited except the disclosure note) |
|---|---|---|
| perirhinal-conjunction | `notes/lit_scan_perirhinal_conjunctive_coding_operation_2026-08-14.md` | `notes/lit_scan_perirhinal_conjunction_operation_2026-08-14.md` |
| feature-ambiguity | `notes/lit_scan_feature_ambiguity_hypothesis_lesion_evidence_2026-08-14.md` | `notes/lit_scan_feature_ambiguity_lesion_evidence_2026-08-14.md` |
| purely-mnemonic-counterposition | `notes/lit_scan_perirhinal_purely_mnemonic_counter_position_2026-08-14.md` | `notes/lit_scan_purely_mnemonic_counterposition_2026-08-14.md` |
| vvs-mtl | `notes/lit_scan_vvs_to_mtl_representational_hierarchy_interference_2026-08-14.md` | `notes/lit_scan_vvs_mtl_hierarchy_interference_2026-08-14.md` |

**Recommendation: all 4 shorter-named files are confirmed SAFE TO REMOVE** — genuinely
duplicate content, canonical committed+cited replacement exists for each, nothing else
references the redundant filename. **Not deleted here per this session's own rule** (never
bundle a deletion with real work; deletion is a separate maintenance-pass call). A human or a
deletion-only call can `git rm` — no, these are untracked, so a plain `rm` — the 4 paths in the
right-hand column above with no further verification needed.

## Disclosure

No tool call was denied during this task. One `ripgrep`/`grep -r` search over all of `notes/`
(10,552 files) timed out repeatedly under concurrent load from other active agents; worked
around by scoping every search to `notes/*2026-08-1[3-5]*.md` or by using targeted Python
`os.scandir` passes over `data/` instead of a blind recursive grep — not a denial, a timeout,
disclosed per the "state what you checked" discipline.
