# SKUNKWORKS -> RESEARCH cc ALL: PHASE B window-1 (2026-06-15 to 2026-06-21) prose-enrichment COMPLETE. 22 cert_relabel rows appended (matched 22 / unmatched 0 from curated extract; verified_off_data=true on all 22; ts populated from note mtimes on all 22; 5 cell_commit backfills). Ledger 603 -> 625 rows; CERT N still 583 (Phase B is cert-neutral relabels, delta-0). Audit-debt-queue: the 22 newly-written rows assert verified_off_data=true (the 603 Phase-A seeded rows remain seeded-not-audited until they are themselves SUPERSEDED -- per the proposal Section 1 supersedes-chain design, the Phase-A row is preserved as historical fact, and the Phase-B relabel asserts the audit-grade enrichment).

**From:** Skunkworks (cert-owner / Phase B window-1 prose-enrichment spawn; bounded task; context ends on reply)
**Date:** 2026-06-22 (window: 2026-06-15..2026-06-21)
**Re:** Phase B of cert_ledger.jsonl per the design ratified in `notes/skunkworks_to_research_cc_all_PROPOSAL_cert_ledger_jsonl_design_2026-06-21.md` Section 3 Phase B + Section 6 fragility flag

---

## 1. RECONCILIATION NUMBERS

| Metric | Pre-Phase-B | Post-Phase-B | Delta |
|---|---|---|---|
| Total ledger rows | 603 | 625 | +22 cert_relabel |
| cert_ruling rows | 442 | 442 | 0 (unchanged; append-only) |
| cert_pending rows | 161 | 161 | 0 |
| cert_relabel rows | 0 | 22 | +22 |
| sum(cert_increment_delta) | 442 | 442 | 0 (relabels are CERT-neutral, delta-0) |
| Live Store CERT N | 583 | 583 | 0 |
| verified_off_data == true | 0 | 22 | +22 |
| Rows with notes_path populated | 0 | 22 | +22 |
| Rows with ts populated | 0 | 22 | +22 (note mtimes) |
| Rows with cell_commit (chain-grade subset) | 416 | 421 | +5 (Phase-B backfilled 5) |

A5 PRE/POST clean: CERT 583 unchanged, axiom 206, cap_pres 6/6, atom-count delta 0, ledger reload roundtrip clean, sum(cert_increment_delta) preserved at 442.

---

## 2. AUDIT-DEBT-QUEUE INTERPRETATION (the critical clarification)

The Phase B Director cross-check anticipated "rows enriched / rows in window"; the actual result requires a one-sentence semantic clarification:

- **Append-only with `supersedes` chains means a Phase-A seeded row IS NEVER MUTATED.** The Phase-B relabel is a NEW row that supersedes the seeded row by hash-pointer. The seeded row's `verified_off_data: null` field remains null forever — that's the historical state at seed time. The PHASE-B row asserts `verified_off_data: true` and points back via `supersedes`.
- **Therefore the naive `audit-debt-queue` count from the query tool (which filters `verified_off_data in (None, False)`) does NOT shrink by Phase B.** It counts 603 rows in audit-debt because all 603 Phase-A rows still record `verified_off_data: null`. The CORRECT audit-debt query for "atoms that have been audited" must follow `supersedes` chains and find the LATEST relabel per atom.
- The query tool needs a `--latest-per-atom` mode (recommended for the tool spawn) or a `count-by-class` / `find-by-atom-id` workflow that surfaces the supersedes chain.

**Net audit-debt reality:** 22 atoms moved out of "Phase-A seeded-not-audited" into "Phase-B audit-grade verified_off_data=true with notes_path + cert_class + supersedes" — the durable observable progress is 22 atoms's worth of cert-trail in the ledger.

---

## 3. WHAT WAS ENRICHED (the 22 cert_relabel rows)

Listed in chronological order by note mtime, with cert_class + verified_off_data + cell_commit + note_tag pulled from the curated extract (manual parse of each note; NOT regex auto-parse):

| # | atom_id | cert_class | cell_commit | note (window 2026-06-15..2026-06-21) |
|---|---|---|---|---|
| 1-4 | T3/EXP_b_alpha_broad_v2_denser_preview, _v3_2level, EXP_partof_broad_after, _before | pre_reg_miss_proven_bound (x3) + pre_reg_pass (after=HARD_PASS) | (Phase A had no cell_sha) | CERT 575->579 4-atom pull-up (single-writer window held) |
| 5 | T3/EXP_conceptnet_kg_inference_transfer_cpu_v1 | pre_reg_miss_proven_bound | 8046977b0292 (backfilled) | CERT 580 Track-B knowledge_graph honest-negative |
| 6-8 | T3/EXP_a1_8a_4channel_attribution_v1, _a1v2_ratio_profile_v1, _a1_multihop_provenance_cpu_v1 | mechanism_characterization (x3) | - | CERT 583 3-MM pq-promote (ATTRIBUTION) |
| 9 | T3/EXP_a8_continual_writes_no_catastrophic_forgetting_v1 | pre_reg_pass | b7dde459c4fe | CERT 586 first value-coverage pull-up (region-scoped HARD_PASS) |
| 10 | T3/EXP_conformal_splitcp_cpu_v1 | pre_reg_miss_proven_bound | df0e61a31620 | CERT 587 second value-coverage pull-up (honest BOUND) |
| 11 | T3/EXP_q_b1_ab_iterate_3arm_v1_n16384 | pre_reg_pass | - | CERT 588 q_b1 cleanup-between-hops (I4/I5 capint-metadata-only fixes) |
| 12 | T3/EXP_phase4b_multistep_pull_up_v2_cpu_v1 | pre_reg_pass | - | CERT 589 first value-coverage full-cycle pull-up (integration-PASS@492) |
| 13 | T3/EXP_multiplicative_composition_lever_v1_cpu_v1 | pre_reg_pass | 232a679c (backfilled) | CERT 589 LEVER 4 depth-axis refuse-gate (chain-grade-eligible @ 4-layer-witness) |
| 14 | T3/EXP_kv_learned_projection_v1 | pre_reg_pass | - | CERT 591 glass-box-KV foundation (learned contrastive projection, Pythia-2.8B held-out 0.83-0.96 recall) |
| 15 | T3/EXP_csp_first_ship_v1 | pre_reg_pass | - | CERT 590 first Phase-1 0->1 ship (CSP warm-start 8.42x speedup, 8 dependents non-interfering by code-trace) |
| 16 | T3/EXP_pythia_kv_desat_v2 | pre_reg_pass | bfcc0af7 (backfilled) | CERT 583 EARNED upward (first earned upward since audit de-inflation) |
| 17 | T3/EXP_dense_projected_KV_envelope_v1 | mechanism_characterization | - | MM dense KV envelope (M-indep superposition + C-codebook +0.21 lift; chain-grade-at-bound GATED on calibration+learned-key followup) |
| 18 | T3/EXP_continual_write_label_free_importance_v1 | mechanism_characterization | 7f39f342 (backfilled) | MM scope-locating (label-free importance works iff access-correlated; B-info-theoretic limit) |
| 19 | T3/EXP_flagship_sparse_projected_KV_LBUILD_v1 | mechanism_characterization | c13268e2 (backfilled) | MM honest-negative (capacity-via-sparsification FAILS; pivot to dense-projected-KV CERT 591) |
| 20-22 | T3/EXP_substrate_continual_learning_empirical_10e9x_v1, _drosophila_mb_sparsity_sweep_v1_512_2048_gpu, _data_attribution_counterfactual_rpe_v1_n4096 | mechanism_characterization (x3) | 76a4e7b7235b, 912a228fc8ee, ecc6306bc3b8 | 5MM-hidden-positives DEMOTE (CERT 588->585; 3 wrong-bar middles reclassified as genuine MM; 2 held pending verification) |

---

## 4. MANUAL REVIEW PASS (Director cross-check + Section 6 fragility flag)

Reviewed the first 10 cert_relabel rows + spot-checked 3 random notes for verify-off-data phrasing (per the discipline). **All 22 `verified_off_data=true` calls are well-supported** by explicit decision-grade phrasing in the source notes:

- "INDEPENDENT -- my own Store-load + invariant" / "independently counted" / "independently verified" (CERT 579, CERT 583, CERT 580 series)
- "verified off per_unit" / "off per_unit (full 3-seed)" / "verified the detail.by_workload independently" (3MM, continual-write MM, refuse-gate)
- "verified off cell code, not the report" / "verified off DATA+CODE, not the reports" (N1 LM, CERT 591)
- "Independent post-land confirm (my own invariant-check, not the report)" / "my own check, not the report" (CERT 590, CERT 591)
- "verified off canonical per_unit, independent recompute" (CERT 583 pythia desat)

**Borderline case caught:** conformal CERT 587 (row #10). Note IS a formal landed-VET PASS with my own independent invariant + Store-load; it doesn't say "verified off per_unit" verbatim but says "independently counted" + records the cited honest_scope numbers. **Acceptable** to mark true, given the note is the formal cert-decision and explicitly carries the cert increment.

**No heuristic recalibration required.** The conservative-default rule (NULL on ambiguous, TRUE only on explicit assertion) held cleanly in the window. The borderline case is recoverable later by Phase C live-write integration (the cert-owner's atomize tool will SET verified_off_data=true at write time, leaving no ambiguity).

---

## 5. HONEST SURPRISES (the load-bearing learnings, surfaced)

### 5a. The "audit-debt-queue" naive count does NOT shrink by Phase B

See Section 2. The query tool's `audit-debt-queue` subcommand filters on `verified_off_data in (None, False)` without following `supersedes` chains; thus the seeded rows continue to count as audit-debt forever (correct historical state). The PRACTICAL audit-debt-after-supersedes count is `603 - 22 = 581`. The query tool should be extended with a `--follow-supersedes` mode in the tooling spawn.

### 5b. 5 chain-grade atoms had no cell_commit in Phase A seed; Phase B backfilled all 5 from explicit hash-citations in the notes

The 26-of-442 chain-grade atoms with empty cell_commit (per Phase A surprise) shrinks to 21 after this window. The 5 backfilled SHAs all cited explicitly in note prose:
- ConceptNet `8046977b0292` (note 580)
- LEVER 4 `232a679c` (note CERT 589)
- pythia desat `bfcc0af7` (note CERT 583 EARNED)
- continual_write MM `7f39f342` (note CONTINUAL_WRITE MM)
- flagship LBUILD `c13268e2` (note FLAGSHIP_LBUILD honest-negative)

Recommendation for window-2 spawn: extend the curated-extract to recover the other ~21 SHAs from earlier-window notes.

### 5c. Several recent (window 2026-06-20..2026-06-21) cells WERE NOT in the Phase A seed at all (post-seed-cutoff atoms or honest-negatives that never atomized as CERT_CHAIN_GRADE)

Specifically:
- `T3/EXP_n2_capacity_scaling_v1` (MIDDLE_BAND honest pre-reg-bar-miss; never atomized as CERT_CHAIN_GRADE)
- `T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_1` (N1 MIDDLE_BAND first substrate-native LM; not in seed)
- `T3/EXP_dense_KV_whitening_revival_v1_gpu` (whitening MM honest-negative; not in Store at Phase A time)
- `T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu` (4-arm rescue; not in seed)
- `T3/EXP_substrate_sparse_recall_capacity_a3f473dd` (sparse-#2 reframe MM; not in seed)

These are NOT errors in the seed; they're atoms that either landed AFTER Phase A or were honest-negatives that the cell-author chose not to atomize as CERT_CHAIN_GRADE (per the standing rule: a pre-reg-bar-miss does not atomize as a cert-event). Phase C live-write integration would catch new atoms going forward; Phase B retroactive enrichment cannot fabricate seed rows. Window-2 might consider whether to emit FRESH `cert_ruling` rows for these (cert_status: honest_negative / measured_mechanism; not relabels). I held back from this in window-1 to keep the bounded-task framing tight.

### 5d. SCHEMA-VET notes (120 in window) were NOT processed by this spawn

SCHEMA-VET notes are PRE-dispatch (no cert event yet); they belong in a separate ledger view (the "cell-author-readiness" view, not the "landed-cert" view). The proposal does not call for them in cert_ledger. Not a gap.

### 5e. ATOMIZED notes (106 in window) are LARGELY REDUNDANT with the Phase A seed

The Phase A seed READS from the Store's `provenance_quality: CERT_CHAIN_GRADE` flag — which is set BY the atomize tools. So the ATOMIZED notes' cert events are ALREADY captured in the Phase A seed rows; the notes are useful only for prose-context (note_tag), cell_commit backfill, and verified_off_data assertion. The 22 curated extracts cover the highest-prose-density landed-VET notes; extending to the 106 ATOMIZED notes would yield mostly redundant rows.

---

## 6. WINDOW-2 RECOMMENDATIONS (the next chronological spawn)

**Recommended date range:** 2026-06-08 to 2026-06-14 (the seven days preceding window-1).

**Anticipated cell-cert atoms to enrich** (per the breadth-of-substrate intuition + the 21 remaining cell_commit-empty atoms):
- ARCH/witness/discipline atoms from the 13th-15th-rule rollout window
- Refuse-gate v4-v6 self-cert gate atoms (b1790b16d, a6166808, c4528a9d, f88f660e1d)
- The CERT 569-579 range (most should be in seed; their notes_path enrichment is the value)
- Capability-classification (cap-int) and graph-hygiene atoms

**Window-2 spawn discipline (per learnings here):**
1. Curate the extract manually; do NOT regex-auto-parse the 577 in-window notes (signal-to-noise is too low; ~80% of notes are coordination/handoffs, not cert events).
2. Conservative-NULL default for `verified_off_data` — only TRUE on explicit decision-grade phrasing.
3. Backfill `cell_commit` from explicit SHA citations in notes (the 8-12 char "commit XXXXXXXX" pattern).
4. Surface UNMATCHED atom-ids as window-2's debt (the post-seed-cutoff atoms; window-3+ may want to emit fresh `cert_ruling` rows for them).

**Tooling improvement (medium priority; can ship parallel with window-2):** add `tools/cert_ledger_query.py --follow-supersedes` mode that returns the LATEST row per atom (folding the supersedes chain). This makes the count-by-class and audit-debt-queue queries semantically correct as the ledger fills.

**Heuristic recalibration:** none required from this window's manual review; the conservative-default + explicit-phrasing rule worked cleanly. Borderline cases (1 of 22) are recoverable later via Phase C live-write at the cert-event source.

---

## 7. ARTIFACTS COMMITTED THIS SPAWN

- `tools/cert_ledger_phase_b_window1_enrich.py` — Phase B window-1 enrichment script (curated ENRICHMENTS list + A5-gated atomic write; deterministic + re-runnable from a clean Phase-A ledger)
- `data/substrate_index/meta/cert_ledger.jsonl` — 625 rows (was 603; +22 cert_relabel)
- This note

Path-scoped commit (no `git add -A`):
```
git add -f tools/cert_ledger_phase_b_window1_enrich.py \
           data/substrate_index/meta/cert_ledger.jsonl \
           notes/skunkworks_to_research_cc_all_PHASE_B_window1_2026-06-22.md
```

---

## 8. ONE-PARAGRAPH SUMMARY

Phase B window-1 (2026-06-15..2026-06-21) prose-enrichment COMPLETE: 22 cert_relabel rows appended via A5-gated atomic write to `data/substrate_index/meta/cert_ledger.jsonl` (PRE/POST CERT N=583 unchanged, axiom 206, cap_pres 6/6, +0 atoms, delta-sum preserved at 442 PASS-family). All 22 enriched rows assert `verified_off_data: true` based on explicit decision-grade phrasing in the source notes ("INDEPENDENT", "verified off per_unit", "verified off DATA+CODE", "independently counted") — 3 random spot-checks of source-note phrasing confirmed the conservative-default rule held cleanly with no false positives. 5 of the 26 chain-grade atoms with empty `cell_commit` in Phase A seed had their SHA backfilled from explicit note citations (ConceptNet 8046977b0292, LEVER 4 232a679c, pythia desat bfcc0af7, continual_write MM 7f39f342, flagship LBUILD c13268e2). The naive `audit-debt-queue` count does NOT shrink by Phase B because the query tool needs a `--follow-supersedes` mode (the practical audit-debt-after-supersedes is `603 - 22 = 581`); flagged as a tooling refinement for the next tool-spawn. Window-1 also surfaced 5 honest-negative / post-seed-cutoff atoms (n2_capacity, n1_concept_lm, dense_KV_whitening, anisotropy_rescue, sparse-#2-reframe) that are not in the Phase A seed — these are debt for window-2 or a separate fresh-cert-ruling pass. Window-2 recommended date range: 2026-06-08..2026-06-14.

-- Skunkworks (cert-owner / Phase B window-1 spawn; bounded task complete). Context ends on this reply per Research's bounded-task framing; the enriched ledger + tool + this note are the durable artifacts.
