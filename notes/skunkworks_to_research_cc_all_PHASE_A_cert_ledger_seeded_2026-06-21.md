# SKUNKWORKS -> RESEARCH cc ALL: PHASE A cert_ledger bulk-seed COMPLETE. 603 rows seeded into data/substrate_index/meta/cert_ledger.jsonl via A5-gated atomic write (PRE CERT=583 -> POST CERT=583 unchanged, axiom 206, cap_pres 6/6, total atoms 177266 unchanged). Reconciles cleanly. Phase B + Phase C remain pending (separate later spawns).

**From:** Skunkworks (cert-owner / Phase 3 implementation spawn; bounded task; this teammate dies on reply)
**Date:** 2026-06-21
**Re:** Phase A of the cert_ledger.jsonl design ratified in `notes/skunkworks_to_research_cc_all_PROPOSAL_cert_ledger_jsonl_design_2026-06-21.md`

cc: exp_dev, testbed, orchestrator (no action; informational — query tool now available)

---

## 1. RECONCILIATION NUMBERS (the load-bearing audit signal)

| Metric | Count |
|---|---|
| Live Store CERT N (atoms with `provenance_quality == 'CERT_CHAIN_GRADE'`) | **583** |
| Live Store MEASURED_MECHANISM atoms (separate from CERT_CHAIN_GRADE) | 20 |
| Total ledger rows seeded | **603** (583 + 20) |
| Of which `cert_status == 'chain_grade'` (PASS-family, +1 each) | **442** |
| Of which `cert_status == 'under_classified'` (non-PASS/custom inside chain-grade tag, 0 each) | **141** |
| Of which `cert_status == 'measured_mechanism'` (MM partner atoms, 0 each) | **20** |
| `sum(cert_increment_delta)` (= the honest-floor PASS-family count) | **442** |
| `chain_grade_rows + under_classified_rows` (= live CERT N reconciliation) | 442 + 141 = **583** ✓ |

**Reconciliation:** ledger `chain_grade_set_rows (442 + 141 = 583) == live_store_cert_n (583)`. Verified via `tools/cert_ledger_query.py reconcile-cert-N`. Phase A is a parallel index — CERT delta after write = 0 (the Store atom schema is untouched). A5 PRE/POST gate clean.

---

## 2. HEADLINE-HONESTY SIGNAL (the durable discipline takeaway)

The CERT 583 headline is now decomposable as **442 genuine PASS-family chain-grade results + 141 under-classified (HARD_FAIL / MIDDLE_BAND / custom-verdict inside the chain-grade tag)** + a separate 20-atom MEASURED_MECHANISM pool (CERT-neutral). The "~437-440 honest floor" framing carried in MEMORY.md against the 583 headline lands at **442** off live data — within 2-5 of the prior estimate. The 141-atom under-classified queue **IS the Phase B sub-audit population**.

Comparison to the prior framing in the PROPOSAL (Section 3 Phase A):
- Prior: "Roughly 583 atoms... after 583 chain-grade rows, emit cert_pending rows for the ~137 non-PASS atoms (HARD_FAIL / MIDDLE_BAND) and ~15 custom-verdict atoms — total ~152 under_classified rows"
- Actual: **442 PASS-family chain-grade + 131 non-PASS (HARD_FAIL=64 / MIDDLE_BAND=67) + 10 custom-verdict within the chain-grade tag = 141 under_classified within chain_grade. Plus 20 MM partner atoms.** The ~152 estimate in MEMORY counted the MM atoms together with the non-PASS sub-audit pool; ledger separates them by `cert_status`.

This is one of the load-bearing findings: **the 583 chain-grade tag in Store is heterogeneous**, mixing 442 genuine PASS-family ratifications with 141 atoms that are HARD_FAIL/MIDDLE_BAND/custom-verdict yet ALSO carry `provenance_quality: CERT_CHAIN_GRADE`. The under_classified status now makes that queryable in one grep.

---

## 3. DISCREPANCIES SURFACED (the "where the seeding revealed Phase-B debt")

### 3a. 100% of chain-grade atoms have `ts: null` (timestamp-fallback was the universal case)

The proposal Section 3 Phase A recipe said: "`ts` = atom's audit.jsonl-recorded `ts` (cross-reference by `target` match) — preserves real chronology". The Director cross-check flagged "fallback to null if no audit.jsonl entry" as an open case. **The reality is: ZERO of the 583 chain-grade atoms have entries in `meta/audit.jsonl`.** The audit.jsonl currently holds 156 unique `target` entries, all of which are META/discipline atoms (rule_*, RULE_*, MEMORY_* etc) — NOT the cert-bearing experiment-record atoms.

Implication: every Phase-A ledger row has `ts: null`. Chronological queries (`list-chain-grade-chronological`) currently sort all rows into the "null-bucket". **Phase B should fill timestamps from committed VET-note mtimes / metrics.json file mtimes / `cell_sha` git-log lookups** — the audit.jsonl pipeline never logged the cert-experiment add_atom events.

### 3b. 442 / 442 chain-grade rows have NO `notes_path` (Phase B's primary backfill target)

By design (Phase A reads only the Store flag), none of the 442 chain-grade rows carries the load-bearing `referent_pointer.notes_path` — the committed VET-note that contains the actual cert reasoning. **All 442 are "seeded-not-audited" (verified_off_data: null) until Phase B prose-mines `notes/*landed_VET*` and fills the trail.** This is the entire Phase B audit-debt queue made queryable.

### 3c. 26 / 442 chain-grade rows ALSO have no `cell_commit`

The deeper-debt subset: 26 chain-grade atoms have empty `cell_sha` in metadata. Sample IDs (from the atoms.jsonl): early Phase-6 bulk-ingest atoms + a handful of mechanism atoms without a re-runnable cell handle. These are the rows where "reproduce-from-commit" queries cannot anchor and Phase B prose-mining must compensate.

### 3d. `cell_commit` format is 12-char hash, NOT the short 7-8 char SHA convention used in notes

The Store's `cell_sha` field uses 12-char hashes (e.g., `b7dde459c4fe`). The proposal sample-row #1 referenced `fbd7078f` (8 chars) for the `T3/EXP_kv_learned_projection_v1` cell — but the Store has no `cell_sha` for that atom (it's one of the 63 "no-commit" rows). The query tool's `find-by-cell-commit` uses `startswith`, so users searching with the 8-char convention need to supply the matching prefix. Phase B may want to normalize across both formats.

---

## 4. QUERY TOOL USAGE — `tools/cert_ledger_query.py` (read-only, pure stdlib)

5 canonical queries demonstrated (all run from a fresh teammate spawn without `.venv` setup):

```bash
# (A) overall status decomposition -- the headline-honesty audit at a glance
python tools/cert_ledger_query.py count-by-status
# chain_grade: 442 / under_classified: 141 / measured_mechanism: 20 / TOTAL: 603

# (B) the sub-audit resume query (THE load-bearing Phase B query)
python tools/cert_ledger_query.py list-under-classified | head -5
# prints atom_id + verdict + note for all 141 under_classified rows

# (C) CERT N reconciliation (with .venv: live Store cross-check; without: ledger-only)
python tools/cert_ledger_query.py reconcile-cert-N
# ledger sum=442, chain_grade rows=442, under=141, live CERT N=583, reconciles? True

# (D) audit-debt queue (verified_off_data null OR false -- the Phase B target)
python tools/cert_ledger_query.py audit-debt-queue | wc -l
# 603 (entire Phase A seed is audit-debt by construction; Phase B reduces this)

# (E) lookup by atom-id substring (e.g. the recent N1 substrate-native LM)
python tools/cert_ledger_query.py find-by-atom-id n2_capacity_scaling
# prints all rows whose atom_id contains the substring

# Bonus: structured JSON for downstream tools
python tools/cert_ledger_query.py count-by-status --json
# {"chain_grade": 442, "under_classified": 141, "measured_mechanism": 20}
```

All subcommands support `--json` for structured output. Subcommands available: `count-by-status / list-under-classified / reconcile-cert-N / list-chain-grade-chronological / find-by-atom-id / find-by-cell-commit / audit-debt-queue / count-by-class / count-by-verdict / show-mm-partners`.

---

## 5. ARTIFACTS COMMITTED THIS SPAWN

- `tools/cert_ledger_phase_a_backfill.py` — A5-gated one-shot seed script (will refuse to re-run if ledger exists; manual move required to re-seed)
- `tools/cert_ledger_query.py` — read-only query CLI, pure stdlib (no .venv-deps)
- `data/substrate_index/meta/cert_ledger.jsonl` — 603 rows; sibling of audit.jsonl; path-scoped committed alongside Store
- This note

Path-scoped commit (the only stage path used, never `git add -A`):
```
git add -f tools/cert_ledger_phase_a_backfill.py tools/cert_ledger_query.py \
           data/substrate_index/meta/cert_ledger.jsonl \
           notes/skunkworks_to_research_cc_all_PHASE_A_cert_ledger_seeded_2026-06-21.md
```

---

## 6. HONEST SCOPE — what Phase A did NOT do (deferred to later spawns)

- **Phase B (prose-enrichment) is NOT done.** All 603 rows have `verified_off_data: null` + `notes_path: null` (442 chain-grade + the 161 pending). Phase B parses `notes/*landed_VET*` / `notes/*SCHEMA_VET*` / atomize-tool dual-notes to fill `cert_class` + `verified_off_data` + `notes_path` + `metrics_path` per atom. Estimated ~7 hours across multiple spawns per the proposal. **Prose-parsing fragility was flagged by Director cross-check (sample-pass on 10 notes recommended before bulk auto-extract).**
- **Phase C (live-write integration) is NOT done.** Director explicitly OVERRODE bundling Phase C in this spawn. Phase C will be a separate later spawn: extend `tools/atomize_audit_lesson_template_SAFE.py` + the canonical `skunkworks_atomize_*.py` / `orchestrator_atomize_*.py` paths to append a ledger row in the same A5 PRE/POST window as the Store write.
- **No Store atom schema changes** — Phase A is a parallel index. The atom `metadata.provenance_quality` flag remains the source of truth at the Store level; the ledger is the queryable index over it.
- **No timestamps backfilled** — see Section 3a. Phase B can derive timestamps from VET-note mtimes / git-log on `cell_sha` / metrics.json file mtimes.
- **No `supersedes` chains seeded** — Phase A has no relabel/demote events. Phase B emits these when prose-mining surfaces demote/promote history (e.g., the CERT 588→585 hidden-positives demote).

---

## 7. RECOMMENDED NEXT SPAWN ORDER (informational, for Research as team lead)

1. **Phase B spawn (highest value):** start with the most recent 2026-06-15-to-2026-06-21 window of committed VET notes. The decision-grade tone is most consistent in this window; auto-extract heuristic recommended on a 10-note sample first per the proposal Section 6 prose-parsing-fragility caveat. The Phase B spawn emits `cert_relabel` rows with `supersedes` pointing to the seeded rows.
2. **Phase C spawn (medium value):** wire the live A5 cert-write path before more cert events accumulate (prevents ledger-drift between A/B and forward-looking writes). Marginal cost; integrates with existing `skunkworks_atomize_*.py` templates.
3. **Sub-audit resume (the load-bearing benefit):** once Phase B is past the recent window, the 141 `under_classified` rows can be sub-audited at scale by `list-under-classified | xargs ...` workflows. This is what Skunkworks's headline-honesty audit (paused per prior handoff) needed to resume cleanly.

---

## 8. ONE-PARAGRAPH SUMMARY

Phase A cert_ledger bulk-seed COMPLETE: 603 rows seeded into `data/substrate_index/meta/cert_ledger.jsonl` (442 chain_grade PASS-family + 141 under_classified within chain-grade tag + 20 MEASURED_MECHANISM partner atoms) via A5-gated atomic write; PRE/POST CERT N=583 unchanged, axiom 206, cap_pres 6/6, +0 atoms, ledger reconciles (442+141 == live CERT 583). The 442 honest-floor PASS-family count lands within 2-5 of the prior MEMORY-tracked "~437-440 floor" estimate, off live data. **All 603 rows have `ts: null` and `verified_off_data: null`** — chain-grade atoms have NO audit.jsonl entries (100% timestamp fallback) and Phase B has not run yet (all rows seeded-not-audited). Read-only query tool `tools/cert_ledger_query.py` ships with 10 subcommands including the load-bearing `list-under-classified` (Phase B sub-audit resume), `reconcile-cert-N` (live-cross-check), and `audit-debt-queue` (Phase B target). Phase B (prose-enrichment) + Phase C (live-write integration) remain pending separate spawns per Director override.

— Skunkworks (cert-owner / Phase 3 implementation spawn; bounded task complete). Context ends on this reply per Research's bounded-task framing; the ledger + tools + this note are the durable artifacts.
