# Phase B window-2 cert-trail enrichment (2026-06-08..2026-06-14)

**From:** Skunkworks (cert-owner / Phase B window-2 prose-enrichment spawn)
**Date:** 2026-06-22
**Re:** Phase B window-2 of cert_ledger.jsonl, per `notes/skunkworks_to_research_cc_all_PHASE_B_window1_2026-06-22.md` Section 6 recommendation

---

## Plain-English summary (Fix #13)

Phase B window-2 is **honestly thin**: 9 cert_relabel rows appended (vs window-1's 22). Window-2 (2026-06-08..2026-06-14) is the PRE-CERT-NNN-numbering, PRE-formal-landed-VET-note era. Most cert events from this period were tracked as portfolio "PP-rows" in `portfolio_state` (orchestrator cycles 178-220+) NOT as cell-atoms in the Store, so they were never seeded by Phase A. The notes that DO map to seeded cell-atoms are exp-dev HARD_PASS self-reports, NOT independent landed-VETs by an auditor — so `verified_off_data` defaults to NULL across all 9 (the conservative-default rule, held cleanly).

Cert-trail observability state: the ledger now has 644 rows. The supersedes-folded audit-debt-queue holds at 582 (unchanged vs pre-window-2). What window-2 added is `notes_path` + `cert_class` + `ts` metadata for 9 atoms that had only Phase-A seed identity before; no audit-grade promotion was warranted by the source-note phrasing.

---

## Numbers

| Metric | Pre-window-2 | Post-window-2 | Delta |
|---|---|---|---|
| Total ledger rows | 635 | 644 | +9 cert_relabel |
| cert_relabel rows | 22 | 31 | +9 |
| Live Store CERT N | 584 | 584 | 0 (Phase B is delta-0) |
| sum(cert_increment_delta) | (unchanged) | (unchanged) | 0 |
| verified_off_data == true (new from this window) | 0 | 0 | 0 (all 9 NULL — conservative default) |
| Rows with notes_path populated (from this window) | 0 | 9 | +9 |
| Rows with ts populated (from this window) | 0 | 9 | +9 |
| cell_commit backfilled (this window) | 0 | 0 | 0 (no explicit SHA citations in source notes for the 9 matched atoms) |

A5 PRE/POST clean: CERT 584 unchanged, axiom 206, cap_pres 6/6, atom-count delta 0, ledger reload roundtrip clean.

---

## Audit-debt-queue (with `--follow-supersedes` query)

| Query | Result |
|---|---|
| Naive count (`audit-debt-queue` no fold) | 614 (was 605 pre-window-2; +9 because each new cert_relabel asserts `verified_off_data=null` so adds to the naive count) |
| Supersedes-folded count (`--follow-supersedes`) | 582 (unchanged vs 582 pre-window-2 — the 9 window-2 relabels both supersede a Phase-A row AND themselves declare `verified_off_data=null`, so the latest-per-atom view holds steady) |
| Ledger row total (`count-by-status`) | 644 |

The supersedes-folded count is the semantically-correct view; the naive view counts every Phase-A seeded predecessor as audit-debt forever (correct historical state, not actionable signal).

---

## Honest surprises (Fix #5 / load-bearing learnings)

### (a) Window-2 has a DIFFERENT character than window-1

Window-1 (2026-06-15..2026-06-21) was the formal-CERT-NNN-landed-VET-note era: each cert event has a dedicated `skunkworks_to_all_CERT_NNN_landed_VET_PASS_*.md` note with explicit verify-off-data phrasing AND a cell_commit citation. Window-2 PRE-DATES this convention. Window-2's cert artifacts are:
- Exp-Dev `HARDPASS_*` self-report notes (cell-author's verdict, not an independent VET)
- Research `DECISION_NN_*` routing notes (strategic, not cert-decision)
- Orchestrator `results_summary_cycle_*` portfolio-row notes (PP-NNN format, the precursor to the cell-atom convention)

The cert events from window-2 LARGELY did NOT atomize as Store cell-atoms — they atomized as portfolio-row entries in `portfolio_state`, which Phase A's "read provenance_quality CERT_CHAIN_GRADE" rule does NOT see. This is the structural reason the enrichment is thin.

### (b) Conservative-NULL rule HELD on all 9 rows

None of the 9 window-2 source notes contain decision-grade phrasing like "verified off per_unit", "independent recompute", "verified off DATA, not reports". They are author-summaries (exp-dev self-report) or Research routing/synthesis prose. The window-1 discipline ("TRUE only on explicit decision-grade phrasing") correctly flagged all 9 as NULL. No false-positives from the heuristic.

### (c) 0 cell_commit backfills this window

Window-1 backfilled 5 SHAs from prose citations ("commit XXXXXXXX" patterns). Window-2's matched atoms either ALREADY had cell_commits in the Phase-A seed (decomposition_resonator alpha05/cpu_v1 / hierarchical_5corpus_v1 / abduction_f1 / kgram_xor / hotpotqa — 6 of the 9) or have NO commit citation in the source note (name_augmented, capacity_cliff, hierarchical_5corpus_v2 — 3 of the 9). The pre-CERT-NNN convention did NOT bake SHA citation into the note-prose practice; this is a window-2-era observability gap, NOT a backfill opportunity. The 21 chain-grade-empty-SHA atoms cited as window-1's surface (after window-1's 5 backfills) remain at 21 after window-2.

### (d) The big window-2 cert events live in `portfolio_state`, not the cell-atom Store

Per the git log + orchestrator results-summary notes, window-2's headline cert events were:
- COMP-DEPTH P0 (4 HARD_PASS COMP-1..COMP-4): 30-year VSA deep-composition cliff CROSSED at L=5 with cascading-Hopfield per-level cleanup
- WAVES 1-4 ~67 HP cells across cycles 211-217 (+56 PP rows PP-229..PP-284)
- The k-gram-XOR + theta-burst promotions (Decision 139b RATIFIED, commit 6615e7a5 / 1e2df579)
- The Phase A/B/C gap-driven loop abduction kernel chain (commits 1a7883f6 / 0dc60edd / ae219c19)

These cert events are documented in `portfolio_state` PP-rows + the git log MILESTONE commits, NOT in `data/substrate_index/{math,meta}/atoms.jsonl` as cell-atoms with `provenance_quality: CERT_CHAIN_GRADE`. The cert_ledger Phase-A seed therefore does NOT see them; cross-substrate enrichment would require a Phase D extension that reads portfolio_state + ratifies PP-rows as cert events with their own atom-id namespace (PP-NNN as the atom_qualified_id, portfolio-row as the cert_status). NOT recommended for window-3+ Phase B; flag as Phase D-substrate-extension if USER wants it.

### (e) 1 atom flagged as unmatched debt: E3 permutation-indexed binding

The `exp_dev_to_research_E3_HARDPASS_permutation_binding_2026-06-12.md` note describes a HARD_PASS (binding-isolation, 1.0 cleanup) for the substrate's role-binding non-uniqueness fix. NO matching cell-atom in seed (the closest patterns — `dimsparse3` / `role_filler` / `multihop_fhrr` — don't match the permutation-binding cell name). The cell either never atomized as CERT_CHAIN_GRADE or has a name pattern I don't recognize. Surfaced as window-2 debt; could be ATOMIZE-LATER candidate if cert-architecture finds the cell-author's metrics file.

---

## What was enriched (the 9 cert_relabel rows)

| # | atom_id substring | cert_class | source-note |
|---|---|---|---|
| 1 | `EXP_substrate_name_augmented_encoding_recovery_canonical_rerun_v593` | pre_reg_pass | exp_dev `NAME_AUGMENTED_ENCODING_HARDPASS_*_2026-06-12` |
| 2 | `EXP_capacity_cliff_graceful_full_v3` | pre_reg_pass | exp_dev `CELL_A_B_VERDICT_COMPOSITION_DECOMPOSITION_*_2026-06-12` |
| 3 | `EXP_substrate_decomposition_resonator_alpha05_cpu_v1` | pre_reg_pass | exp_dev `CELL_A_B_VERDICT_*_2026-06-12` |
| 4 | `EXP_substrate_decomposition_resonator_cpu_v1` | (None; MIDDLE_BAND under_classified) | exp_dev `CELL_A_B_VERDICT_*_2026-06-12` |
| 5 | `EXP_substrate_hierarchical_5corpus_meta_v1_n2048_gpu` | pre_reg_pass | research `BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08` |
| 6 | `EXP_substrate_hierarchical_5corpus_meta_v2_n2048_gpu` | pre_reg_pass | research `BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08` |
| 7 | `EXP_substrate_abduction_f1_weakest_signature_kernel_kgram_xor_groundtruth_cpu_v1` | pre_reg_pass | research `PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_*_2026-06-13` |
| 8 | `EXP_substrate_kgram_xor_real_llama1b_v1` | (None; MIDDLE_BAND) | research `PROACTIVE_GAP_DRIVEN_JUNIOR_SEARCH_*_2026-06-13` |
| 9 | `EXP_substrate_cognitive_core_multihop_hotpotqa_v1` | (None; HARD_FAIL) | orchestrator `results_summary_2026-06-08_cycle186` |

All 9 have `verified_off_data: null` (conservative-default; exp-dev self-reports + research routing notes are NOT independent landed-VETs). All 9 have `ts` from note mtime. All 9 have `notes_path` populated. Sum(cert_increment_delta) preserved at +0 (relabels are CERT-neutral).

---

## Heuristic recalibration (Fix #5)

None required. The window-1 conservative-default rule held cleanly on all 9 window-2 enrichments. Window-2 actually VALIDATES the rule: 0 false-positives, 0 borderline-cases (window-1 had 1 borderline at CERT 587 conformal). The exp-dev/research/orchestrator note styles uniformly don't contain decision-grade verify-off-data phrasing — that style is a SKUNKWORKS-landed-VET convention specific to window-1 forward.

---

## Window-3 spawn recommendation

**Recommended date range:** 2026-06-01..2026-06-07 (the seven days preceding window-2).

**Anticipated enrichment yield:** likely THIN (5-15 rows) for similar reasons to window-2 — window-3 is even earlier in the pre-CERT-NNN era. The bulk of window-3 cert events will be portfolio-row-style + foundational substrate-build cells (algebra primitives, scorecard atoms, T1/T2 axiom landings).

**Window-3 spawn discipline (per learnings here):**
1. Curate manually; expect THIN match-set (the cell-atom convention is sparse for this era).
2. Conservative-NULL on verified_off_data; do NOT relax the rule for exp-dev self-reports.
3. Backfill cell_commit only from explicit "commit XXXXXXXX" citations; do NOT infer from filename or atom-name patterns.
4. Surface portfolio-row + PP-row cert events as Phase D debt (NOT Phase B retroactive enrichment).
5. Surface the E3 permutation-binding orphan as window-2-carried debt (the cell-author may need to atomize it if the metrics file is preserved).

**Tooling refinement (medium priority):** consider a `tools/cert_ledger_query.py count-empty-cell-commit` subcommand that lists chain-grade atoms with `cell_commit=null` (the durable observability target — currently 21 atoms after window-1, 21 after window-2).

**Phase D extension (USER call):** the BIG window-2 cert events live in `portfolio_state` (cycles 178-220 PP-rows ~56 entries). If the substrate's "cert headline" is to honestly reflect WHAT THE SUBSTRATE DID, those need a separate ledger projection — NOT a retroactive Phase B enrichment. Recommend Director surface this to USER as a deliberate scope decision.

---

## Artifacts committed this spawn

- `tools/cert_ledger_phase_b_window2_enrich.py` (new; the curated ENRICHMENTS list + A5-gated atomic write)
- `data/substrate_index/meta/cert_ledger.jsonl` (635 -> 644 rows; +9 cert_relabel)
- This note

Path-scoped commit:
```
git add -f tools/cert_ledger_phase_b_window2_enrich.py \
           data/substrate_index/meta/cert_ledger.jsonl \
           notes/phase_b_window2_cert_trail_2026-06-22.md
```

---

## One-paragraph summary

Phase B window-2 (2026-06-08..2026-06-14) prose-enrichment COMPLETE: 9 cert_relabel rows appended (vs window-1's 22 — window-2 is honestly thin because it pre-dates the formal CERT-NNN-landed-VET convention; most window-2 cert events were tracked as portfolio PP-rows, not Store cell-atoms). A5-gated atomic write to `data/substrate_index/meta/cert_ledger.jsonl` clean: CERT N=584 unchanged, axiom 206, cap_pres 6/6, atom-count delta 0, sum(cert_increment_delta) preserved. All 9 enriched rows assert `verified_off_data: null` — the conservative-default rule held cleanly across the entire window (0 false-positives; exp-dev self-reports + research routing prose simply don't contain decision-grade verify-off-data phrasing). 0 cell_commit backfills (window-2 source notes don't cite SHAs; the 21 chain-grade-empty-SHA atoms after window-1's 5 backfills remain at 21). Supersedes-folded audit-debt-queue holds at 582 (unchanged — window-2's relabels add notes_path/cert_class/ts metadata but don't promote audit-grade). Headline learning: the BIG window-2 cert events (COMP-DEPTH cliff-crossed, ~67 HP-cells WAVES 1-4, +56 PP-rows) live in `portfolio_state`, NOT in the cell-atom Store; window-3+ Phase B will be similarly thin; the durable fix is a Phase D extension that projects portfolio_state PP-rows into the ledger with their own atom-id namespace (USER call to scope). Window-3 recommended date range: 2026-06-01..2026-06-07.

-- Skunkworks (cert-owner / Phase B window-2 spawn; bounded task complete). The enriched ledger + tool + this note are the durable artifacts.
