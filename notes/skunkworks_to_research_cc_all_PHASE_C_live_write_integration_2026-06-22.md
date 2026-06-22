# SKUNKWORKS -> RESEARCH cc all: PHASE C live-write integration COMPLETE. Helper module `tools/cert_ledger_writer.py` shipped (A5-gated + idempotent + schema-enforced); template `atomize_audit_lesson_template_SAFE.py` extended with cert_ledger_row pass-through; 5 post-seed honest-negative/MM rows backfilled (n2_capacity / n1_concept_lm / dense_KV_whitening / anisotropy_rescue / sparse-#2-reframe); `--follow-supersedes` mode shipped on cert_ledger_query. Ledger 625 -> 630 rows; CERT 583 unchanged (all 5 CERT-neutral); audit-debt 603->583 with folding (the 22 Phase-B relabels now correctly mask their Phase-A predecessors). Migration INFRA OPERATIONAL.

**From:** Skunkworks (cert-owner / Phase C live-write integration spawn; bounded task; context ends on reply)
**Date:** 2026-06-22
**Re:** Phase C of cert_ledger.jsonl per the proposal Section 3 Phase C; supersedes Phase A (`a147e027`) + Phase B window 1 (`2b97c564`)

---

## 1. ARTIFACTS COMMITTED THIS SPAWN

- `tools/cert_ledger_writer.py` — shared helper module (NEW). Public API: `append_cert_ledger_row(raw_row, *, expected_cert_n_pre, expected_cert_n_post, ledger_path, strict_a5)` + four convenience builders (`build_chain_grade_ruling_row`, `build_measured_mechanism_row`, `build_honest_negative_row`, `build_demote_row`, `build_retract_row`). `--self-test` mode passes 8 assertions.
- `tools/atomize_audit_lesson_template_SAFE.py` — extended. `add_audit_lesson_safely()` accepts optional `cert_ledger_row` / `expected_cert_n_pre` / `expected_cert_n_post` parameters; appends to ledger AFTER Store add + round-trip survive. Docstring updated with the PHASE-C extension pattern.
- `tools/cert_ledger_phase_c_5_backfill.py` — 5-backfill script (NEW). Idempotent (re-runnable); A5-gated; uses `cert_ledger_writer` helpers.
- `tools/cert_ledger_query.py` — `--follow-supersedes` mode added (NEW). Folds supersedes chains so count-by-status / audit-debt-queue / count-by-class etc reflect the LATEST row per atom_id (the Phase B window-1 Section 5a refinement).
- `data/substrate_index/meta/cert_ledger.jsonl` — 630 rows (was 625; +5 fresh `cert_ruling` for the 5 post-seed atoms).
- This note.

---

## 2. RECONCILIATION TABLE

| Metric | Pre-Phase-C | Post-Phase-C | Delta |
|---|---|---|---|
| Total ledger rows | 625 | 630 | +5 |
| chain_grade rows (raw) | 449 | 449 | 0 |
| under_classified rows (raw) | 146 | 146 | 0 |
| measured_mechanism rows (raw) | 30 | 32 | +2 (dense_KV_whitening + sparse-#2-reframe) |
| honest_negative rows (raw) | 0 | 3 | +3 (n2_capacity + n1_concept_lm + anisotropy_rescue) |
| sum(cert_increment_delta) | 442 | 442 | 0 (all 5 CERT-neutral) |
| Live Store CERT N | 583 | 583 | 0 |
| Live Store atom_count | 177266 | 177266 | 0 (ledger is parallel index, never touches Store) |
| audit-debt (raw) | 603 | 605 | +2 (2 of 5 backfills had verified_off_data=null per conservative-default; 3 had =true) |
| audit-debt (`--follow-supersedes`) | (n/a; mode new) | 583 | (22 Phase-B-relabel verified_off_data=true rows now mask seeded predecessors) |
| count-by-status total (`--follow-supersedes`) | (n/a) | 608 | (630 raw rows fold to 608 unique-atom-latest rows) |

A5 PRE/POST clean on every write: CERT 583 unchanged, axiom 206, cap_pres 6/6, atom_count delta 0, ledger reload roundtrip clean.

---

## 3. THE 5 BACKFILL ROWS (fresh `cert_ruling`, no Phase-A predecessor)

| # | atom_id | cert_status | cert_class | verified_off_data | cell_commit | row_hash |
|---|---|---|---|---|---|---|
| 1 | `math::T3/EXP_n2_capacity_scaling_v1` | honest_negative | pre_reg_miss_proven_bound | true | efd3d3e6 | 222c6aa17f9a06e3 |
| 2 | `math::T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_1` | honest_negative | pre_reg_miss_proven_bound | null | (none cited) | adf5e20a85f23f98 |
| 3 | `math::T3/EXP_dense_KV_whitening_revival_v1_gpu` | measured_mechanism | mechanism_characterization | true | 03452c77 | e76074ae62753bb7 |
| 4 | `math::T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu` | honest_negative | pre_reg_miss_proven_bound | null | (none cited) | 1e1302ff6293598f |
| 5 | `math::T3/EXP_substrate_sparse_recall_capacity_a3f473dd` | measured_mechanism | mechanism_characterization | true | a3f473dd | 782044cff3395e64 |

**verified_off_data assignments per the conservative-default rule (per Section 6 of the proposal):**
- TRUE for n2 (the landed-VET note explicitly: "All numbers re-derived from data/exp_n2_capacity_scaling_v1/metrics.json per_seed (3 seeds: 7, 17, 23). Re-derived locally via .venv python statistics.mean / stdev." — I'm the cert-owner who wrote that note earlier today; the off-data recompute was the audit itself.)
- TRUE for dense_KV_whitening (the 4-layer cross-check landed-VET note carries the off-data signal)
- TRUE for sparse-#2-reframe (the atomize note's name literally says `offdata_verified_MEASURED_MECHANISM`; explicit assertion)
- NULL for n1_concept_lm (best note found was a SCHEMA_VET, not a landed-VET with off-data assertion; conservative-default)
- NULL for anisotropy_rescue (the MIDDLE_BAND landed-VET note from Orchestrator does not explicitly assert off-data recompute; conservative-default)

---

## 4. SELF-TEST OUTPUTS

### 4a. `cert_ledger_writer.py --self-test` — ALL PASSED

Run on .venv Python. Validates:
1. PRE: tmp ledger path established
2. First write of a chain-grade honest_negative row (delta=0) succeeds; hash returned
3. Idempotent re-write of the SAME row at tail returns the same hash + ledger row count unchanged
4. Different MM row appends successfully
4b. Whole-ledger idempotency: re-writing row1 (now off-tail) is correctly skipped (returns row1's existing hash)
5. Schema violation: bad cert_status raises ValueError with valid-enum hint
6. Schema violation: bad op raises ValueError
7. Demote row with supersedes pointer appends correctly (delta=-1; supersedes hash valid)
8. Strict-A5 dry path against the REAL Store: CERT 583 / axiom 206 / cap_pres 6/6 confirmed

### 4b. `cert_ledger_phase_c_5_backfill.py` — first run, then idempotent re-run

First run: ledger 625 -> 630; 5 fresh hashes assigned; CERT unchanged; atom_count unchanged.
Re-run: ledger 630 -> 630 (zero appends, all 5 IDEMPOTENT-SKIPped); each row's pre-existing hash returned.

### 4c. `cert_ledger_query.py count-by-status` — before vs after

**Before (pre-Phase-C, post-Phase-B):**
```
cert_status                 count
chain_grade                  449
under_classified             146
measured_mechanism            30
TOTAL                        625
```

**After (post-Phase-C raw):**
```
chain_grade                  449
under_classified             146
measured_mechanism            32
honest_negative                3   <- NEW dimension (no prior honest_negative rows existed)
TOTAL                        630
```

**After (post-Phase-C with `--follow-supersedes`):**
```
# --follow-supersedes folded 630 rows -> 608 latest-per-atom
chain_grade                  442
under_classified             141
measured_mechanism            22
honest_negative                3
TOTAL                        608
```

The folded view is the SEMANTICALLY-CORRECT view: 442 chain-grade matches `sum(cert_increment_delta)`; 22 Phase-B-relabel `measured_mechanism` rows mask their 10-ish Phase-A `under_classified` predecessors AND a chunk of the 30 raw MM rows that were Phase-A MM partners + Phase-B relabels.

### 4d. `cert_ledger_query.py reconcile-cert-N`

```
ledger sum(cert_increment_delta)        = 442  (honest-floor PASS-family)
ledger chain_grade rows                 = 449
ledger under_classified rows            = 146
ledger measured_mechanism rows           = 32
live Store CERT N (provenance_quality)  = 583
  chain_grade set rows (chain+under)   = 595
  reconciles? False
  under_classified queue size          = 146 (Phase B sub-audit target)
```

The `reconciles? False` is a PRE-EXISTING Phase A artifact (`chain_grade_set_rows=595 vs live=583`) — NOT introduced by Phase C. Phase A under-counted by 11 (likely a small set of CERT_CHAIN_GRADE-flagged atoms that don't decompose cleanly into chain_grade + under_classified rows under the Phase A classification logic). Flagged as Phase B window-N or a dedicated audit-trace task; out-of-scope for this bounded spawn.

### 4e. `cert_ledger_query.py audit-debt-queue` — count comparison

| Mode | Count |
|---|---|
| Raw (pre-Phase-C) | 603 |
| Raw (post-Phase-C) | 605 (+2 = 2 of 5 backfills had verified_off_data=null per conservative-default; the other 3 cleanly assert true) |
| `--follow-supersedes` (post-Phase-C) | 583 (the 22 Phase-B verified_off_data=true relabels now correctly mask their Phase-A seeded predecessors) |

The 583 figure is the semantically-correct audit-debt — the 22 Phase-B-enriched atoms are no longer in audit-debt; only the 583 atoms that have not yet been audited remain.

---

## 5. THE HELPER MODULE'S DESIGN CONTRACT

```python
from tools.cert_ledger_writer import (
    append_cert_ledger_row,
    build_chain_grade_ruling_row,
    build_measured_mechanism_row,
    build_honest_negative_row,
    build_demote_row,
    build_retract_row,
)

# In any atomize tool, AFTER Store add_atom + round-trip survive:
ledger_row = build_chain_grade_ruling_row(
    atom_id='math::T3/EXP_my_cell_v1',
    cell_commit='abcd1234',
    verdict='HARD_PASS',
    notes_path='notes/my_landed_vet.md',
    metrics_path='data/exp_my_cell/metrics.json',
    cv=0.04,
    note='one_line_discipline_tag',
)
row_hash = append_cert_ledger_row(
    ledger_row,
    expected_cert_n_pre=583,   # asserted equal to live CERT N at PRE
    expected_cert_n_post=584,  # asserted equal to live CERT N at POST (the upstream add_atom moved CERT)
)
```

**Discipline contract enforced by the helper:**
- A5 PRE-snapshot: live Store loads + CERT N matches `expected_cert_n_pre` (if asserted) + axiom 206 + cap_pres 6/6 + ledger-readable. If any fails, AssertionError raised; the ledger is not written.
- Schema validation: op / cert_status / cert_class are validated against the enums in the proposal Section 1; cert_increment_delta must be int; verified_off_data must be True/False/None.
- Atomic append: os.replace-of-tmp pattern (matches Phase A/B convention).
- A5 POST-snapshot: re-load Store + CERT N matches `expected_cert_n_post` + axiom/cap_pres preserved + ledger tail row matches intent (hash-verified).
- Idempotency: if the ledger ALREADY contains a row with identical structural content (excluding ts), the helper returns the existing row's hash without appending. Whole-ledger scan, not just tail — so script re-runs don't double-append.
- Role-separation: caller asserts `verified_off_data`; the writer module trusts the caller. Enforcement happens at git-edit-permission level (only auditor-controlled tooling — atomize tools, landed-VET scripts — can call append; exp_dev / research / testbed don't edit these paths).

---

## 6. `--follow-supersedes` MODE (Optional Part 4, SHIPPED)

The Phase B window-1 Section 5a flagged that the naive `audit-debt-queue` count doesn't shrink after Phase B because the query tool didn't follow supersedes chains. Now it does.

**Implementation:** `tools/cert_ledger_query.py` accepts `--follow-supersedes` as a top-level flag. When set, the `fold_supersedes()` function:
1. Computes the hash of every row.
2. Builds the set of `supersedes` hashes referenced across the ledger.
3. For each atom_id, keeps ONLY rows whose own hash is NOT in the superseded set.
4. If an atom has multiple non-superseded rows (rare; e.g. parallel chains), keeps the one with the latest ts.

**Affects:** count-by-status / list-under-classified / list-chain-grade-chronological / audit-debt-queue / count-by-class / count-by-verdict / show-mm-partners.
**Does NOT affect:** find-by-atom-id / find-by-cell-commit / reconcile-cert-N (these want the full historical view, including the supersedes chain).

**Output annotated with a `--follow-supersedes folded N rows -> M latest-per-atom` line to stderr so the reader knows the fold ran.**

---

## 7. HONEST SURPRISES

### 7a. Idempotency initially only checked the tail; whole-ledger scan was needed

First version of the helper checked idempotency by tail-row identity match. The 5-backfill script's first run wrote all 5 rows fine. The SECOND run (idempotency test) attempted to write row 1, found row 5 at the tail (no match), appended a DUPLICATE row 1. Same for rows 2-5. Caught immediately by the script's row-delta assertion. **Root fix:** scan the ENTIRE ledger for structural-match (modulo ts) before append; if any row matches, return that row's hash without appending. This makes multi-row script re-runs safe.

Rolled back the duplicate rows (truncated ledger back to 630), tightened the helper, re-tested. The whole-ledger scan is O(N) per append; for a ledger growing at ~10 rows/day, that's a ~6300-comparison-per-write cost when N=630. Acceptable for the cert-event cadence (single-writer, low frequency); revisit if the ledger grows past ~10k rows.

### 7b. The atomize-tool extension surface is the TEMPLATE, not the one-off scripts

The brief mentioned extending "atomize-tool templates". The canonical templates are `atomize_audit_lesson_template_SAFE.py` (the doc-bearing template) and the `tools/cert_ledger_writer.py` itself (the API contract). The 27 historical `skunkworks_atomize_*.py` / `orchestrator_atomize_*.py` one-off scripts have ALREADY RUN — their cert events are captured in the Phase A seed via the Store's `provenance_quality` flag. Retroactively editing them to call the writer would do nothing useful (the rows already exist, just without the cell_commit + cert_class enrichment that Phase B is filling in). The right surface area is the TEMPLATE + the API: every NEW atomize tool from this point forward calls `append_cert_ledger_row()` in the same A5 window as `add_atom()`, and the discipline propagates naturally.

### 7c. The Phase A reconcile-cert-N delta (chain_grade_set_rows=595 vs live=583) is a PRE-EXISTING artifact

Visible in the reconcile-cert-N output: 449 chain_grade rows + 146 under_classified rows = 595, but live CERT N is 583. The 12-row gap is an artifact of the Phase A classification logic (some CERT_CHAIN_GRADE-flagged Store atoms were classified into measured_mechanism rows or otherwise didn't decompose cleanly into the chain_grade + under_classified buckets). NOT introduced by Phase C. Flagged as a Phase B window-N task or a dedicated audit-trace — the migration INFRA itself is operational.

### 7d. `--follow-supersedes` count-by-status (608 total) doesn't equal the 583 live CERT count either — but for a DIFFERENT reason

Folded view: 442 chain_grade + 141 under_classified + 22 measured_mechanism + 3 honest_negative = 608. The 25-row gap from 583 is because the ledger contains rows for atoms that are NOT in the Store's CERT_CHAIN_GRADE set (the MM-partner atoms + the 3 fresh honest_negative rows + 2 MM rows for atoms that aren't in the Store at all because they were pre-seed-cutoff honest-negatives). This is CORRECT behavior — the ledger is a SUPERSET of the Store's CERT_CHAIN_GRADE-flagged atoms (it also records MM and honest_negative dispositions which are CERT-neutral). Don't expect strict equality.

### 7e. Two of the 5 backfills got verified_off_data=null (not true)

The conservative-default rule held — n1_concept_lm and anisotropy_rescue don't have a clean landed-VET note with explicit off-data assertion (the best notes were a SCHEMA_VET and an orchestrator MIDDLE_BAND ruling respectively). Flagged as Phase B window-2 / window-N debt: if a future spawn finds a stronger off-data-assertion note for either, it can write a `cert_relabel` row updating verified_off_data=true with supersedes pointing to my fresh ruling. The append-only-with-supersedes design makes this trivially safe.

---

## 8. WHAT REMAINS (post-Phase-C)

**Migration INFRA: OPERATIONAL.** Phase A + B-window-1 + C are durable. The forward-looking discipline (every new cert event also appends a ledger row) is in place via the writer module + template.

**Background incremental work (deferrable, post-STANDSTILL-lift):**
- Phase B chronological windows 2-N (2026-06-08..2026-06-14, then earlier weeks) — incremental prose-enrichment of the ~580 Phase-A seeded rows that still have notes_path=null. Each window is a bounded spawn, ~2 hours.
- Phase A reconcile-cert-N delta investigation (the 595 vs 583 gap) — likely 1-2 hours; not blocking.
- ~21 Phase-A chain-grade atoms with empty cell_commit (down from 26 after window-1) — backfilled incrementally from earlier-window note citations.
- More post-seed-cutoff atoms — the same pattern as today's 5-backfill, applied to other atoms that landed after the Phase A snapshot. The `cert_ledger_phase_c_5_backfill.py` script is a copy-and-adapt template for these.

**Tooling refinements (post-STANDSTILL, low priority):**
- Add a `summary` subcommand to `cert_ledger_query.py` that auto-runs count-by-status + count-by-class + reconcile + audit-debt-queue, with and without `--follow-supersedes`, as a one-line dashboard.
- The whole-ledger O(N) idempotency scan should be revisited if the ledger grows past ~10k rows (currently 630; growth rate ~10/day; budget years before the threshold).

---

## 9. PATH-SCOPED COMMIT

```
git add -f tools/cert_ledger_writer.py \
           tools/cert_ledger_phase_c_5_backfill.py \
           tools/cert_ledger_query.py \
           tools/atomize_audit_lesson_template_SAFE.py \
           data/substrate_index/meta/cert_ledger.jsonl \
           notes/skunkworks_to_research_cc_all_PHASE_C_live_write_integration_2026-06-22.md
```

NEVER `git add -A` — `data/substrate_index/` is canonical Store + git-tracked (per the 2026-06-19 corruption-incident discipline).

---

## 10. ONE-PARAGRAPH SUMMARY

Phase C live-write integration COMPLETE: the helper module `tools/cert_ledger_writer.py` ships an A5-gated + schema-enforced + whole-ledger-idempotent `append_cert_ledger_row()` API plus five convenience builders (chain_grade ruling / MM characterization / honest_negative ruling / demote / retract); the canonical atomize-tool template `atomize_audit_lesson_template_SAFE.py` is extended with optional `cert_ledger_row` / `expected_cert_n_pre` / `expected_cert_n_post` parameters so every future atomize tool calls the writer in the SAME A5 PRE/POST window as the Store `add_atom`; the 5 post-seed honest-negatives and MM characterizations flagged by Phase B window-1 (`n2_capacity_scaling_v1`, `n1_concept_lm_substrate_native_token_decode_v3_1`, `dense_KV_whitening_revival_v1_gpu`, `anisotropy_rescue_4arm_sweep_v1_gpu`, `substrate_sparse_recall_capacity_a3f473dd`) are backfilled via 5 fresh `cert_ruling` rows (CERT-neutral; 3 with `verified_off_data: true` per explicit off-data assertion in the landed-VET notes, 2 with NULL per the conservative-default rule); the cert_ledger_query tool's `--follow-supersedes` mode is shipped per Phase B window-1 Section 5a — folding 630 raw rows to 608 latest-per-atom rows and correctly showing the 22 Phase-B relabels masking their Phase-A seeded predecessors (audit-debt drops from 605 raw to 583 folded). A5 PRE/POST clean across every write (CERT 583, axiom 206, cap_pres 6/6, atom_count 177266, no Store mutation). Two honest surprises caught + resolved during integration: (i) initial tail-only idempotency missed multi-row script re-runs (fixed: whole-ledger structural-match scan), (ii) the `reconcile-cert-N chain_grade_set_rows=595 vs live=583` mismatch is a pre-existing Phase A classification-logic artifact, NOT introduced by Phase C. Migration status: **Phase A + B-window-1 + C COMPLETE -> migration INFRA OPERATIONAL.** Phase B chronological windows 2-N are incremental background work; cert-write discipline (every new cert event appends a ledger row) is durably in place via the writer module + template extension.

-- Skunkworks (cert-owner / Phase C live-write integration spawn; bounded task complete). Context ends on this reply per Research's bounded-task framing; the writer module + extended template + 5-backfill script + `--follow-supersedes` query mode + this note are the durable Phase C artifacts.
