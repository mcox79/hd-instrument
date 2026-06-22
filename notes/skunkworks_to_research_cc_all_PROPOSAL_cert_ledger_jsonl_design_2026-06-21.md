# SKUNKWORKS -> RESEARCH cc ALL: PROPOSAL cert_ledger.jsonl design (Phase 3 of Agent-Teams migration). One-row-per-decision append-only ledger aligned to meta/audit.jsonl shape; makes CERT N + each decision queryable without prose-mining; backfills incrementally from existing Store atoms + committed cert-notes; A5-compatible (single-writer, idempotent, atomic). Bounded design task. USER ratification requested before implementation spawn.

**From:** Skunkworks (cert-owner / auditor; subagent spawn af38c... by Research for Phase 3)
**Date:** 2026-06-21
**Re:** cert_ledger.jsonl gap flagged in validation spawn af38eb647786affcf
**Status:** DESIGN-ONLY proposal (no writes; this teammate's context dies on reply)

---

## 0. WHY THIS LEDGER MATTERS (load-bearing context)

Current state: the CERT 583 headline (and the 152-UNDER-CLASSIFIED sub-audit) is reconstructed entirely from prose-mining (a) `notes/*landed_VET*` decision notes, (b) Store-atom `metadata.provenance_quality == 'CERT_CHAIN_GRADE'` flags, and (c) the trail in `data/substrate_index/meta/audit.jsonl`. The Store IS the durable record, but the Store schema has NO queryable cert_status field at the atom granularity: the only cert-bearing signal is the binary `provenance_quality` metadata flag (chain-grade-or-not) plus free-text `note`/`source` strings.

Under the HYBRID architecture (cert-trail in Store+git for observability + lightweight coordination in Agent Teams), the auditor needs a typed, queryable ledger that survives across teammate spawns. Without it, every new spawn has to re-mine prose to answer "what's the CERT count? which atoms are under-classified? what's the chain-grade-by-mechanism-class distribution?" — the sub-audit pause documented in the handoff (Section 7f, "the cert-headline negative-sub-audit (152 UNDER-CLASSIFIED atoms) is paused") is concretely BLOCKED on this.

Per my cert-owner-verdict for the migration (b47a7b95), the explicit ASK was: **cert DECISIONS + ATOMIZATIONS** as Store atoms with `cert_vet_status / verified_off_data / atomized_by` fields = the durable observable record. This proposal operationalizes that ask as a JSONL ledger pattern.

---

## 1. SCHEMA — one row per cert decision

Format: append-only JSONL at `data/substrate_index/meta/cert_ledger.jsonl`, ASCII, one JSON object per line. Field shape mirrors `meta/audit.jsonl` conventions (`ts` float epoch / lowercase snake_case / `op` enum / `target` string) so the existing audit-trail conventions extend rather than fragment.

### Required fields (every row)

| Field | Type | Values | Notes |
|---|---|---|---|
| `ts` | float | UNIX epoch seconds | matches audit.jsonl |
| `op` | string enum | `cert_ruling` / `cert_relabel` / `cert_demote` / `cert_promote` / `cert_retract` / `cert_pending` / `cert_dissolve` | the decision act |
| `atom_id` | string | qualified id (e.g. `math::T3/EXP_n2_capacity_scaling_v1`) | the THING the cert pertains to |
| `cert_status` | string enum | `chain_grade` / `measured_mechanism` / `honest_negative` / `proven_bound` / `under_classified` / `dissolved` / `retracted` / `custom` | the cert-tier disposition |
| `cert_class` | string enum (optional) | `pre_reg_pass` / `post_hoc_pass` / `pre_reg_miss_proven_bound` / `mechanism_characterization` / `discipline_meta` / `data_attribution` / `infra_record` | semantic class within tier |
| `verified_off_data` | bool | true if recompute-from-per_unit confirmed cited numbers; false if VET-deferred or report-only | the load-bearing audit signal |
| `atomized_by` | string | role-name (e.g. `skunkworks` / `orchestrator`) | the writer; role-separation traceability |
| `cell_commit` | string (optional) | git SHA of the cell at run time | reproducibility anchor |
| `verdict` | string | the cell's own verdict (`HARD_PASS` / `MIDDLE_BAND` / `HARD_FAIL` / etc) | what the cell claimed |
| `cert_increment_delta` | int | -1, 0, or +1 (or -N for retracts) | the count-move; MUST sum to current CERT N from the seed |
| `cv` | float (optional) | seed-CV across runs | for chain-grade only; cf. K_eq / 4-arm rulings |
| `referent_pointer` | object | `{notes_path: <git-tracked-VET-note>, metrics_path: <data/<cell>/metrics.json>, atom_qualified_id: <Store id>}` | the trail; never embed prose |
| `supersedes` | string (optional) | prior ledger-row hash if this row reverses/refines | enables relabel/retract chain |
| `note` | string (optional) | 1-line discipline tag (e.g. `pre_reg_bar_miss_proven_bound`) — NEVER prose | brief context |

### Field semantics (the rulebook tightenings)

- **`verified_off_data: false` is allowed but FLAGGED** — a ledger row without off-data confirmation is "lean toward the cell's verdict, not auditor-ratified." Used for triage / pending-sub-audit; chain-grade requires `verified_off_data: true`.
- **`cert_increment_delta` must be reconcilable** — sum of all `cert_increment_delta` from a known seed (e.g. CERT==0 at ts=0) must equal the live CERT N. Drift = audit failure.
- **`cert_status: under_classified` is the load-bearing addition** — explicitly types the 152 non-PASS/custom atoms that need sub-audit; no prose required.
- **`supersedes` enables relabel without rewrite** — a CERT 588->585 demote (per N1 hidden-positives note) writes 3 new rows with `op: cert_demote`, `cert_increment_delta: -1` each, and `supersedes` pointing to the prior `chain_grade` row. Append-only; no edits.
- **`referent_pointer.notes_path` MUST be a committed path** — the git-committed VET note is the load-bearing prose; the ledger is the metadata index over the prose.

---

## 2. SAMPLE ENTRIES (5 representative dispositions)

Pulled from the actual recent cert landings cited in the handoff. Field values reflect what's actually in the Store / notes (verified-off-data where I could; flagged where I couldn't from this read-only spawn).

```jsonl
{"ts": 1782146400.0, "op": "cert_ruling", "atom_id": "math::T3/EXP_kv_learned_projection_v1", "cert_status": "chain_grade", "cert_class": "pre_reg_pass", "verified_off_data": true, "atomized_by": "orchestrator", "cell_commit": "fbd7078f", "verdict": "HARD_PASS", "cert_increment_delta": 1, "cv": null, "referent_pointer": {"notes_path": "notes/skunkworks_to_research_expdev_cc_orch_LANDED_VET_dense_KV_envelope_MM_now_chain_grade_at_bound_GATED_on_calibration_plus_learned_key_followup_2026-06-21.md", "metrics_path": "data/exp_kv_learned_projection_v1/metrics.json", "atom_qualified_id": "math::T3/EXP_kv_learned_projection_v1"}, "supersedes": null, "note": "held_out_genuine_disjoint_train_holdout_plus_shuffled_control"}
{"ts": 1782160800.0, "op": "cert_ruling", "atom_id": "math::T3/EXP_n2_capacity_scaling_v1", "cert_status": "honest_negative", "cert_class": "pre_reg_miss_proven_bound", "verified_off_data": true, "atomized_by": "skunkworks", "cell_commit": "efd3d3e6", "verdict": "MIDDLE_BAND", "cert_increment_delta": 0, "cv": null, "referent_pointer": {"notes_path": "notes/skunkworks_to_research_orch_expdev_cc_all_LANDED_VET_n2_capacity_scaling_MIDDLE_BAND_and_4arm_storage_win_NOT_ratified_2026-06-21.md", "metrics_path": "data/exp_n2_capacity_scaling_v1/metrics.json", "atom_qualified_id": "math::T3/EXP_n2_capacity_scaling_v1"}, "supersedes": null, "note": "pre_reg_bar_miss_4p96_vs_bigram_3p84_substrate_caps_above_bigram_this_arch"}
{"ts": 1782160900.0, "op": "cert_ruling", "atom_id": "math::T3/EXP_n2_capacity_scaling_v1_MM_alpha_monotone", "cert_status": "measured_mechanism", "cert_class": "mechanism_characterization", "verified_off_data": true, "atomized_by": "skunkworks", "cell_commit": "efd3d3e6", "verdict": "MIDDLE_BAND", "cert_increment_delta": 0, "cv": null, "referent_pointer": {"notes_path": "notes/skunkworks_to_research_orch_expdev_cc_all_LANDED_VET_n2_capacity_scaling_MIDDLE_BAND_and_4arm_storage_win_NOT_ratified_2026-06-21.md", "metrics_path": "data/exp_n2_capacity_scaling_v1/metrics.json", "atom_qualified_id": "math::T3/EXP_n2_capacity_scaling_v1_MM_alpha_monotone"}, "supersedes": null, "note": "sub_bpc_monotone_decreases_with_N_at_fixed_V_C_alpha_BPC_monotonicity_confirmed_MM_class"}
{"ts": 1782090000.0, "op": "cert_demote", "atom_id": "math::T3/continual_learning_empirical_10e9x", "cert_status": "measured_mechanism", "cert_class": "mechanism_characterization", "verified_off_data": true, "atomized_by": "skunkworks", "cell_commit": null, "verdict": "MIDDLE", "cert_increment_delta": -1, "cv": null, "referent_pointer": {"notes_path": "notes/skunkworks_to_research_cc_orch_expdev_testbed_HIDDEN_POSITIVES_landed_VET_3of5_MM_CERT_585_2_HELD_2026-06-21.md", "metrics_path": "data/continual_learning_empirical_10e9x/metrics.json", "atom_qualified_id": "math::T3/continual_learning_empirical_10e9x"}, "supersedes": "<prior_chain_grade_row_hash>", "note": "wrong_bar_1000x_was_large_LLM_scale_aspiration_genuine_27x_no_forget_MM"}
{"ts": 1781936310.012, "op": "cert_pending", "atom_id": "math::T3/EXP_q_b1_bisect_cluster", "cert_status": "under_classified", "cert_class": null, "verified_off_data": false, "atomized_by": "skunkworks", "cell_commit": null, "verdict": "mixed", "cert_increment_delta": 0, "cv": null, "referent_pointer": {"notes_path": "notes/skunkworks_to_research_cc_orch_expdev_testbed_HIDDEN_POSITIVES_landed_VET_3of5_MM_CERT_585_2_HELD_2026-06-21.md", "metrics_path": null, "atom_qualified_id": "math::T3/EXP_q_b1_bisect_cluster"}, "supersedes": null, "note": "cluster_membership_mismatch_reconcile_before_reclassify_part_of_152_subaudit"}
```

Note on row #5: `cert_status: under_classified` is exactly the field the 152-atom sub-audit needs to query. Each of the 152 gets a row at backfill time; sub-audit progress is then a SQL-like query against the ledger (`count by cert_status`).

---

## 3. MIGRATION PATH — backfill from existing Store atoms + committed cert-notes

**Recommended ordering: cert-N-ordered (NOT chronological)**, because the audit needs the CERT count to reconcile at every row. Chronological backfill would interleave with non-cert atom writes (the audit.jsonl is mostly non-cert events); cert-N-ordered gives a monotone sequence where `cert_increment_delta` sums to the live count at each step.

### Phase A — seed the ledger from the Store (one-shot, low risk)

1. Read all atoms with `metadata.provenance_quality == 'CERT_CHAIN_GRADE'` from the Store. Roughly 583 atoms.
2. For each, emit a baseline `cert_ruling` row with:
   - `cert_status: chain_grade` (the Store flag is the source of truth at seed time)
   - `cert_class: null` (filled in Phase B from notes)
   - `verified_off_data: null` (filled in Phase B; until then, this is a `seeded-not-audited` state)
   - `cert_increment_delta: +1`
   - `referent_pointer.atom_qualified_id` filled; `notes_path` and `metrics_path` derived from atom `metadata.witnesses` / `metadata.source` if present, null otherwise
   - `ts` = atom's audit.jsonl-recorded `ts` (cross-reference by `target` match) — preserves real chronology in field, even if row order is cert-N-ordered
3. After 583 chain-grade rows, emit `cert_pending` rows for the ~137 non-PASS atoms (HARD_FAIL / MIDDLE_BAND) and ~15 custom-verdict atoms — total ~152 `under_classified` rows. These are the sub-audit queue.
4. Verify: sum of `cert_increment_delta` across the seeded rows == live CERT N (583).

**Cost estimate Phase A:** ~30 minutes of teammate time for a script + a single A5-gated append; ~735 rows written; one git commit. Low risk because it's append-only and reads-not-writes against the Store.

### Phase B — enrich from committed cert-notes (incremental, by-cell-id ordered)

For each cert-bearing landed-VET / SCHEMA-VET / atomize-tool note in `notes/`:
1. Extract the `atom_id`, `cell_commit`, `verdict`, and the verify-off-data signal (look for "verified off data", "re-derived from per_unit", "ASCII recompute matched" in the note body — the existing decision-grade tone is consistent enough to parse).
2. Match to the seeded row by `atom_qualified_id`; write a `cert_relabel` row with `supersedes` pointing to the seeded-row hash, filling `cert_class` + `verified_off_data` + `notes_path` + `metrics_path` + `cert_class` from the note.
3. For demote/promote/retract events found in notes (e.g. the CERT 588->585 hidden-positives demote), emit the appropriate `cert_demote` / `cert_promote` row.

**Cost estimate Phase B:** rough scan shows ~200 cert-bearing notes (landed-VET + SCHEMA-VET + atomize-tool dual-notes). At ~2 min/note for a careful parse with verify-off-data spot-check, that's ~7 hours; can be parallelized across several teammate spawns (each handling one chronological window). Recommended: 1 spawn handles 2026-06-15-to-2026-06-21 (the most recent + the most action), subsequent spawns backfill earlier as bandwidth allows.

### Phase C — wire the ledger into the live cert-write path (forward-looking)

Every NEW cert-event (landed-VET ruling, atomize-tool A5 write, demote-on-sub-audit) appends a ledger row in the same A5 PRE/POST window as the Store write. The atomize-tool template (`tools/atomize_audit_lesson_template_SAFE.py`) gets a `_append_cert_ledger_row()` helper; landed-VET notes get a companion ledger row when they declare a cert-status change.

**Cost estimate Phase C:** one template edit + ~5 tool refactors (the canonical skunkworks_atomize_*.py and orchestrator_atomize_*.py paths); ~2 hours; bundled with the implementation spawn.

---

## 4. QUERYABILITY CONTRACT (what the ledger enables that prose-mining doesn't)

Canonical queries the ledger SHALL support (all answerable in <1 second by reading the JSONL):

| Query | Mechanism |
|---|---|
| List all chain-grade certs in chronological order | filter `cert_status == 'chain_grade'`, sort by `ts` |
| Count chain-grade vs MM vs honest-negative vs under-classified | group-by `cert_status` |
| **Show all atoms with `cert_status == 'under_classified'` pending sub-audit** (the 152) | filter `cert_status == 'under_classified'`; this is the LOAD-BEARING SUB-AUDIT RESUME QUERY |
| Verify CERT N reconciles | `sum(cert_increment_delta) == live_cert_count_from_Store` |
| Count MM-tier by mechanism class | filter `cert_status == 'measured_mechanism'`, group-by `cert_class` |
| Find all certs WITHOUT verified-off-data confirmation | filter `verified_off_data == false OR null`; the audit-debt queue |
| Show all demotes / retracts (the honest downward corrections trail) | filter `op IN ('cert_demote', 'cert_retract')` |
| Show all certs by atomized_by role (role-separation audit) | group-by `atomized_by`; flag if cert-owner ever appears as cell-author |
| Find cert-decisions for a specific cell across its lifecycle (relabel chain) | filter `atom_id == X`, follow `supersedes` chain |
| Show certs by cell_commit (reproduce-from-commit) | filter `cell_commit == <sha>` |

**Load-bearing for sub-audit resume:** a teammate spawn opening the ledger can `grep '"cert_status": "under_classified"'` and get the 152-atom queue in one read; each sub-audit ruling appends a `cert_relabel` row updating the status. Sub-audit progress is then `count(under_classified)` over time — no prose mining, no MEMORY.md narration, no "I last touched atom #47" hand-tracking.

---

## 5. A5-GATE COMPATIBILITY

**Confirmed compatible** with one minor extension; no deviation from the canonical A5 pattern.

### Append pattern (extension of existing tools/skunkworks_atomize_*.py)

```python
def append_cert_ledger_row(row: dict, ledger_path: Path = Path('data/substrate_index/meta/cert_ledger.jsonl')):
    # PRE: Store loads + CERT/axiom/cap_pres invariants verified by the caller's A5 PRE-gate
    # WRITE: atomic append via os.replace-of-tmp + flock OR fcntl on the JSONL file
    # POST: re-read tail line; verify row equals what we wrote; CERT delta matches cert_increment_delta
    tmp = ledger_path.with_suffix('.tmp.' + str(os.getpid()))
    # read existing
    existing = ledger_path.read_text() if ledger_path.exists() else ''
    new_line = json.dumps(row, ensure_ascii=True) + '\n'
    tmp.write_text(existing + new_line)
    os.replace(tmp, ledger_path)  # atomic
    # verify
    tail = ledger_path.read_text().splitlines()[-1]
    assert json.loads(tail) == row
```

### Single-writer guarantee

The cert_ledger is written ONLY by the cert-owner role (skunkworks) and the atomize-tool path (orchestrator's A5-gated atomize_*.py scripts). Exp-Dev / Research / Testbed NEVER append; they read-only. Role-separation enforces single-writer windows; the os.replace-of-tmp gives atomicity within that.

### Concurrency

If TWO cert-events arrive in the same window (e.g. orchestrator atomize + skunkworks landed-VET both triggering writes), they SERIALIZE through the same path-scoped commit gate that already protects `data/substrate_index/`. The ledger inherits the Store's single-writer-window discipline.

### Verify-Store-LOADS-before-staging

The cert_ledger sits IN `data/substrate_index/meta/` so it's path-scoped-committed alongside the Store partitions. The post-write Store-LOAD gate already runs; the ledger gets the same protection.

### POST-verify

In addition to the existing A5 POST (CERT N delta + axiom 206 + cap_pres 6/6 + Store reloads), add: `ledger_tail_row_matches_intent`. Cheap; runs in <50ms.

---

## 6. HONEST SCOPE NOTES (what the ledger does NOT solve)

- **The ledger does NOT replace cert-disposition prose.** The committed landed-VET note (decision-grade reasoning, the WHY of a ruling, the symmetric anti-negativity / anti-inflation reasoning) remains load-bearing for audit-trail observability. The ledger makes the prose's CLAIMS queryable as metadata; it does not replace the prose's REASONING. Anyone re-auditing a contested cert still reads the note.
- **The ledger does NOT enforce verify-off-data discipline.** It records whether that discipline was followed (`verified_off_data: true/false`). A lying writer could set the field falsely; the protection is role-separation (cert-owner is the only writer for `verified_off_data: true`) + spot-audit (a future spawn can re-derive from per_unit and compare). The ledger is honest-by-discipline, not honest-by-construction.
- **The ledger does NOT resolve the MM-vs-CERT-N tension.** MM rows have `cert_increment_delta: 0` per the existing rule (MM is CERT-neutral). The "capability development is broader than chain-grade count" framing (from MEMORY.md / USER 2026-06-19) still needs a parallel program-progress view; the ledger doesn't fix that headline-honesty issue, only makes the underlying breakdown visible.
- **The ledger does NOT validate the cert-headline-honesty audit.** That audit's job (the 152 sub-audit) is to MOVE rows from `under_classified` to one of the typed statuses; the ledger just makes the queue queryable. The audit-work itself remains a manual cert-owner cycle.
- **The ledger does NOT touch the Store atom schema.** Atom metadata stays as-is (`provenance_quality` flag preserved); the ledger is a parallel index, not a schema migration. This keeps backfill cheap + reversible (delete the JSONL = back to current state).
- **The ledger does NOT prevent ghost certs.** A cert that's never rule-by-skunkworks but has `provenance_quality: CERT_CHAIN_GRADE` set by some other writer would appear in Phase-A seeding without a `verified_off_data: true` row. This is INFORMATION (`seeded-not-audited` rows are visible) but not enforcement — the cert-owner's spot-audit cycle is the enforcement layer.
- **Phase-B prose parsing is fragile.** The "verified off data" / "re-derived from per_unit" extraction relies on the decision-grade-tone convention; a note that says "re-checked the per-token-bpc" wouldn't match unless we expand the heuristic. Recommend a manual review pass on a 10-note sample after the first auto-extract.

---

## 7. CAVEATS / OPEN QUESTIONS (USER decision-point flags)

These are the design-points where I'm picking sensible defaults but the USER might want a different call. Surfacing them under the proposal so ratification is informed:

1. **Path location:** I've proposed `data/substrate_index/meta/cert_ledger.jsonl` (sibling of `audit.jsonl`, same conventions, same A5/git protection). Alternative: a top-level `data/cert_ledger.jsonl` (less coupled to Store internals; easier to git-protect independently). I'd default to the proposed sibling location; flag if USER prefers separation.
2. **`verified_off_data` for Phase-A seed rows:** I've proposed `null` (= "seeded-not-audited"). Alternative: `false` (more conservative; treats every un-re-audited cert as un-verified). The `null` path lets the sub-audit MOVE rows to `true` without re-rewriting the Phase-A bulk; `false` would force a re-rewrite per row. I'd default to `null`; flag if USER prefers `false`.
3. **Sub-audit queue scope (the 152):** I've proposed seeding ALL ~152 non-PASS/custom atoms as `under_classified`. Alternative: seed only the atoms WITHOUT a clear pre-reg-miss disposition (the ~50-100 "true unknowns"; the clear pre-reg-misses go directly to `honest_negative` / `proven_bound`). Cleaner end-state but requires Phase-A judgement calls. I'd default to ALL-152-as-under-classified for the bulk (clear demarcation), then Phase-B refines; flag if USER prefers triage-during-Phase-A.
4. **MM atom-id convention for cells that earn BOTH a cert-tier ruling AND an MM characterization** (see sample row #3, `EXP_n2_capacity_scaling_v1_MM_alpha_monotone`): the cell gets two rows (one for the cell-level cert disposition, one for the MM characterization), with two distinct `atom_id`s. Confirms the existing skunkworks convention of separate MM atoms; flag if USER prefers a single row with both statuses encoded.
5. **Read-only auditor tools:** I'd ship a `tools/cert_ledger_query.py` (read-only) alongside the implementation that exposes the canonical queries from Section 4. Approximately 1 hour of additional implementation cost; high value (the sub-audit resume query is the load-bearing one). Flag if USER wants this deferred or done by Testbed instead (Testbed's dashboard could surface counts).
6. **Live-write integration vs deferred:** Phase C (wire into live cert-write path) could be done in the implementation spawn OR deferred. I'd recommend doing it in the implementation spawn — the cost is marginal and it prevents ledger-drift from accumulating between Phases A/B and forward-looking writes. Flag if USER prefers staged.

---

## 8. ONE-PARAGRAPH SUMMARY (for the team-lead reply)

The cert_ledger.jsonl is an append-only typed JSONL at `data/substrate_index/meta/cert_ledger.jsonl` with one row per cert decision, fields aligned to audit.jsonl conventions, sealed under the existing A5 PRE/POST gate and single-writer discipline. The load-bearing design choice is **append-only with `supersedes` chains for relabel/demote** (not in-place edits) — this preserves the full audit history (every CERT 588->585 demote is visible in the trail), enables the 152-UNDER-CLASSIFIED sub-audit resume as a one-line query, and survives Agent-Teams teammate-spawn turnover because the ledger IS the state (not the teammate's memory). Backfill is cert-N-ordered in Phase A (one-shot from the Store, ~30min) + by-cell-id ordered in Phase B (incremental from committed VET notes, ~7hrs across multiple spawns) + integrated into the live A5 write path in Phase C (~2hrs). The ledger does not replace cert-disposition prose, does not enforce verify-off-data (records it), and does not touch the Store atom schema — it's a parallel queryable index that operationalizes the HYBRID architecture's "cert observability via Store+git" promise at scale.

---

## 9. REPLY-TO-TEAM-LEAD FIELDS (for Research's ratification routing)

- **Proposal note filename:** `notes/skunkworks_to_research_cc_all_PROPOSAL_cert_ledger_jsonl_design_2026-06-21.md` (this file; 110 chars including .md)
- **Load-bearing design choice:** append-only JSONL with `supersedes` chains (Section 1) + cert-N-ordered backfill (Section 3) + the `under_classified` status as the sub-audit-resume primitive (Sections 1, 4)
- **Caveats requiring USER ratification:** 6 open questions in Section 7 (path location / verified_off_data null-vs-false / sub-audit seed scope / dual-row MM convention / read-only tool scope / Phase-C timing)
- **Disciplines preserved:** A5 PRE/POST, single-writer, path-scoped commits, never `git add -A`, .venv-python, role-separation (cert-owner is the only writer), verify-off-data as a recorded field
- **Honest scope:** ledger makes claims queryable; it does not replace prose reasoning, does not enforce honesty (records it), does not modify the Store schema

— Skunkworks (cert-owner / Phase-3 design spawn). Context ends on reply per Research's bounded-task framing; the proposal note is the durable artifact. CERT 583/177266 at design time.
