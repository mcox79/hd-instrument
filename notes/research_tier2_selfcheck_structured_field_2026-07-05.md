# Research — strengthening the Tier-2 self-check loop (structured-field fix, retrieval diagnosis, sequencing)

Date: 2026-07-05
Trigger: Director scoping request on `exp_cert_ledger_numeric_entailment_v1`
(SMOKE HARD_PASS, `data/exp_cert_ledger_numeric_entailment_v1/metrics.json`, commit `065260c57`)
— the loop mechanically closes (op_agreement 1.0, injected-flip recall 1.0) but VET
surfaced two named limitations: retrieval_hit_rate=0.145 (weak) and a near-vacuous
free-text audit leg (0 clean candidates). Notes-only drill per instruction — no cell
built. Field advisor run at cycle start (below, same disposition as the same-session
sibling notes). Generic-term external queries only (query-privacy); lit-scan
calibration applied (deflate 0.15-0.25; novel-synthesis cap 0.50); HARD-FAIL
thresholds mandatory. NO routing files emitted (ferry mechanism deprecated;
everything actionable — including the infra/cell spec the Director asked for — is
delivered in this note).

---

## HEADLINE

**Both named limitations are real, but they are NOT the same kind of problem, and
direct re-measurement this drill (re-running the cell's own harvest/range_filter
code, unc-apped, against the FULL corpus rather than the smoke's 200-triple sample)
shows the retrieval number is actually WORSE than reported (0.10-0.11 true full-
corpus rate vs 0.145 smoke) and, more importantly, reveals retrieval_hit_rate does
not currently gate the audit at all — the comparison pipeline already reads each
metrics.json's own embedded verdict directly, bypassing the ledger. The two
limitations have two DIFFERENT fixes: (1) the audit-leg weakness is a
representation problem (free-text vs structured) — YES, build the structured-field
fix, it is cheap, backward-compatible, and (per external lit-scan on log-parsing
ceilings) the only way to make automated numeric self-audit fully reliable rather
than best-effort. (2) the retrieval weakness is NOT a matching-algorithm problem —
it is a coverage/indexing problem (only 950 of 5744 on-disk experiment directories
ever got a cert_ledger.jsonl row at all; external lit-scan on record-linkage
"blocking recall vs matching recall" confirms this is a well-known, distinct failure
mode that no smarter matcher — fuzzy, embedding, or the substrate's own proven
KGStore multi-hop mechanism — can fix.** Recommend building the structured-field
fix now, in the smoke/local lane, ahead of the parked FULL (cheap, orthogonal to the
USER-auth blocker); recommend the ledger-coverage question be settled by a single
already-tooled, near-zero-cost audit before investing further.

---

## Field advisor (run at cycle start, per role discipline)

`python tools/orchestrator/research_field_advisor.py` was run. All 22 tracked fields
are physics/stat-mech adjacencies (thermodynamics, spin-glass, free-probability,
semiconductor, coding-theory, etc.); none map to "self-audit / structured-logging /
record-linkage." Same honest gap the two same-day sibling entailment notes flagged —
noted, not acted on; this drill correctly draws on direct on-disk re-measurement plus
two targeted generic-term external lit-scans instead.

---

## Q1 — The structured-field fix (highest leverage)

**Recommendation: YES, build it.** Design (minimal, opt-in, backward-compatible):

- Add a small helper to `experiments/_seed_checkpoint.py` — the SAME module already
  imported by 3485 of 4656 cells on disk (MEASURED this drill, `grep`-verified) via
  its `write_metrics()` call, which is already the de facto mandatory final-write
  path. This is the single highest-leverage insertion point: touch one shared helper,
  not 4656 cell files.
  - `record_gate(gate_name, measured, threshold, op, note=None) -> dict`: builds one
    normalized claim `{"gate_name", "measured", "threshold", "op", "gate_verdict"}`,
    computing `gate_verdict` itself via the same 5-line `eval_op`-style logic already
    proven twice this session (`exp_math_rns_subtract_compare_v1`'s
    `decode_then_compare`, and this cell's own `eval_op`) — so the stored verdict is
    COMPUTED at write-time from the cell's own local variables, never re-derived from
    a string later.
  - Extend `write_metrics(out_dir, metrics, results=None, gate_claims=None)`: if a
    list of such claims is passed, validate schema (op in
    `{">=","<=","==",">","<"}`, measured/threshold numeric) and store under a NEW
    top-level key `metrics["structured_gate_claims"]`. Fully opt-in — cells that pass
    nothing are unaffected; no migration required for any existing cell.
  - Adoption path: add ONE bullet to the CELL-TEMPLATE MANDATORY checklist (the same
    convention list already enforced per-cell as inline header comments —
    `cardinality_ok`, `arms_differ_verified`, `final_metrics_atomicity`, etc.):
    "structured_gate_claims populated for every named HARD-PASS/HARD-FAIL band."
    Recommend also writing this once centrally (e.g. a short new section under
    CLAUDE.md's "When implementing a new feature," or a small
    `docs/cell_template_checklist.md`) rather than leaving it to be re-derived
    per-cell-header, since no single canonical checklist file currently exists
    (verified: the MANDATORY block is copy-pasted per-cell as a comment, not
    `include`d from one source).

**Why this fixes BOTH named limitations at once, for future cells:**
- Retrieval becomes an exact JSON-field lookup, not a regex scan — trivially at or
  near 100% precision by construction. External lit-scan (below) confirms even the
  best-in-class automated free-text log-parser (Drain, He et al. ICWS 2017) tops out
  at 0.92-1.00 GROUP accuracy across benchmark datasets, never fully reliable — this
  cell's own regex (already hardened TWICE this session per its docstring's Fix#28
  catches) is in exactly that same "best-effort, not exact" class by nature of
  parsing free text at all.
- The audit leg becomes non-vacuous because `gate_verdict` is computed at the SOURCE
  cell's own runtime from its own in-scope `measured`/`threshold` locals — zero
  parsing ambiguity, by construction, for any cell that adopts it.

**Backfill feasibility for the EXISTING 654 files (MEASURED this drill, read-only,
no cell, no writes — re-ran the cell's own `harvest_triples`/`range_filter` against
the live corpus):**

| Measurement | Value |
|---|---|
| Files citing >=1 parseable `NUM op NUM` inequality | 654 (matches prereg) |
| Raw triples / in-dynamic-range triples | 948 / 915 |
| Triples carrying a captured metric NAME (`name=` prefix) | 750/948 = **79.1%** |
| Files with >=1 named triple | 518/654 = **79.2%** |
| Files where ALL cited triples are named | 476/654 = **72.8%** |
| Files with an existing structured `bands` dict at all | 112 (but only 28 of those also cite an inequality — bands and free-text citation rarely co-occur, so bands-cross-reference is NOT a viable backfill shortcut) |

Recommend a ONE-TIME, non-destructive backfill script (same convention as the
existing `tools/audit_full_coverage.py`, whose own docstring reads "NOT a permanent
tool — audit-spawn artifact") that reuses the cell's already-hardened `_INEQ` regex
VERBATIM (import, don't re-derive) and writes to a SEPARATE sidecar file per
experiment dir — `data/<exp_dir>/structured_gate_claims_backfill.json` — rather than
touching any existing `metrics.json` (many of which are frozen post-VET records).
Populate the sidecar only for the ~476 cleanly-all-named files at
`confidence: "parser_assisted_unreviewed"`; route the remaining ~178
(654-476, files with any unnamed or ambiguous triple) to a flat human-review queue
list rather than auto-populating them. This is the "parser-assisted,
human-review-gated" backfill the Director asked about, and it is honestly bounded:
it improves ~73-79% of the existing corpus, it does not claim to clean 100% of it.

**Does this move Tier-2 from demonstration toward reliable self-audit?** For future
cells: yes, structurally (near-zero marginal cost per cell, reuses proven logic,
backward-compatible). For the existing backlog: partially — a real, bounded,
honestly-scoped improvement (majority-coverage backfill at unreviewed-parser
confidence), not a claim of a fully clean historical corpus.

---

## Q2 — Retrieval, re-measured: this is a coverage problem, not a matching problem

**Re-measurement (this drill, read-only, direct re-run of the cell's own harvest +
range_filter + ledger-index code against the FULL corpus, not the smoke's 200-triple
cap):**

| Measurement | Value |
|---|---|
| `cert_ledger.jsonl` rows / unique exp-keys indexed | 1446 / 950 |
| Total `exp_*` directories on disk with a `metrics.json` | 5744 (of 5785 total `exp_*` dirs) |
| In-range triples citing an inequality, full corpus (uncapped) | 915, spanning 629 unique exp-keys |
| **TRUE full-corpus retrieval_hit_rate** (by exp-key) | 63/629 = **0.100** |
| **TRUE full-corpus retrieval_hit_rate** (by triple, matches the cell's own metric definition) | 99/915 = **0.108** |

The smoke's reported 0.145 was a mildly favorable draw from its first-200-triples
cap; the honest full-corpus number is slightly worse (0.10-0.11), not better.

**Why a smarter retrieval mechanism (fuzzy match, embedding similarity, or pointing
the substrate's own proven KGStore multi-hop retrieval — as in
`exp_cert_ledger_self_query_v1`, which gets Task-A currency accuracy = 1.000 on real
+ constructed ledger data — at this problem) would NOT help:** the missing records
are not present in `cert_ledger.jsonl` UNDER ANY SPELLING — they are simply absent.
`cert_ledger.jsonl` only gains a row when `hdi_skunkworks` atomizes+lands a cell (or
the existing `tools/back_fill_cert_ledger.py` orphan-backfill tool is run for it).
Of 5744 `exp_*` dirs with a `metrics.json` on disk, only 950 (16.5%) have EVER been
atomized into the ledger. A prior 2026-06-28 one-shot audit
(`tools/audit_full_coverage.py`, confirmed on disk, docstring: "enumerate all
full-mode exp_* dirs, check coverage in cert_ledger.jsonl") already characterized
this exact gap independently — this is a known, previously-scoped systemic property
of the pipeline, not a fresh discovery, and it already has tooling
(`back_fill_cert_ledger.py`, `audit_backup_vs_atoms.py`) built around it.

External lit-scan confirms this is a well-established, NAMED distinction in
record-linkage/entity-resolution literature: **"blocking recall" (does the
candidate-generation/indexing stage even retain the true record as a candidate) vs
"matching recall" (given it IS a candidate, does the classifier/similarity function
correctly link it)** — Fellegi & Sunter (1969), *A Theory for Record Linkage*, JASA
64(328):1183-1210; Christen (2012), *Data Matching: Concepts and Techniques for
Record Linkage, Entity Resolution, and Duplicate Detection*, Springer; Binette &
Steorts (2022), *(Almost) All of Entity Resolution*, Science Advances 8(12),
arXiv:2008.04473. A record missed at the blocking/indexing stage can never be
recovered by a smarter matcher downstream — exactly the substrate's situation.

**A second finding this re-measurement surfaced, not previously in the cell's own
metrics:** as currently wired, `retrieval_hit_rate` does not actually GATE or feed
the comparison pipeline at all. `run_seed()`'s `op_hits`/`audit` computation uses
`t["verdict"]`, which `harvest_triples()` reads directly from each `metrics.json`'s
OWN embedded `"verdict"` field — independent of whether that `exp_key` also appears
in `ledger_idx`. `retrieval_hit_rate` is measured and reported as a side statistic,
not a dependency. So today, low `retrieval_hit_rate` does not limit the loop's
ability to catch a real inconsistency in any GIVEN `metrics.json` — it only
quantifies how much of the specifically CURATED/VET'd ledger record (as opposed to
the raw on-disk corpus) gets cross-referenced, which matters only insofar as
"self-check" is meant, per the "canon-1st" discipline, to mean "check the
substrate's VETTED canonical record" rather than "grep every raw file on disk."

**Recommendation:** do not chase a smarter retrieval algorithm. Two independent,
orthogonal levers, matched to what each actually fixes:
- (a) **Ledger-coverage growth** — a testbed/skunkworks infra lever (existing tool,
  see Q3's cheap decisive test below), independent of this cell, valuable in its own
  right for the "canon-1st" discipline generally, not gating this cell's next
  iteration.
- (b) **Reframe the metric** — on this cell's NEXT revision, point the retrieval leg
  at `metrics.json` directly (which the comparison leg already implicitly does) and
  rename/re-document the statistic accordingly (e.g. split into
  `ledger_coverage_rate` [reported, not gated] vs a new, close-to-100%-by-construction
  `source_claim_found_rate` over the raw corpus) rather than reporting one number
  that conflates two different questions. This is a documentation/wording fix, not a
  new mechanism, and it is the one this drill recommends prioritizing (cheap, honest,
  immediate).

---

## Q3 — Sequencing vs the parked FULL

**Recommendation: build the strengthened version NOW, in the smoke/local lane,
before the USER-auth remote FULL deploy unblocks — do not wait.**

- The FULL is parked on an entirely unrelated blocker (USER-auth for reading the
  live self-record referent on the autonomous remote pipeline). Nothing about the
  structured-field fix or the retrieval reframe touches that blocker; they are
  orthogonal.
- The structured-field fix is cheap (one shared-helper extension, opt-in,
  SMOKE-only-local iteration already covers it under the standing USER lock) and
  strengthening now means that whenever the USER-auth FULL dispatch does happen, it
  exercises the BETTER design — not the current one with both known weaknesses
  baked in, which would likely need a second FULL iteration anyway.
- Concrete order (none of these require GPU or queue dispatch):
  1. Land the `write_metrics(..., gate_claims=None)` extension + `record_gate()`
     helper in `experiments/_seed_checkpoint.py` (testbed/exp_dev infra change, no
     compute).
  2. Run the ONE cheap decisive audit that discriminates Q2's two candidate
     explanations before investing further: re-run the EXISTING
     `tools/back_fill_cert_ledger.py --audit-commit` machinery (already built,
     already used for exactly this purpose per its own docstring) as a SWEEP across
     the historical atomize-commit list, to measure how much of the 5744-vs-950 gap
     is genuine unprocessed backlog (recoverable by running the existing tool
     further) vs legitimately-never-atomized SMOKE-only/negative-result cells
     (structural, not a backlog). This is <1hr, read-only-equivalent (dry-run mode
     exists per the tool's own `--dry-run` flag), zero compute, zero risk.
  3. Run the backfill sidecar script for the 476 cleanly-named existing files (Q1).
  4. Re-run `exp_cert_ledger_numeric_entailment_v1 --smoke` locally (same anchor, no
     new cell) against the now-available structured claims + reframed retrieval
     metric, to get a genuinely stronger smoke result.
  5. Only then dispatch the FULL, whenever the USER-auth blocker clears.

---

## Q4 — Brain grounding: metacognitive monitoring / source memory for self-audit

Honest analog, not task-analog (per standing discipline). External lit-scan (3
sub-agents' worth of citations, verified via WebSearch/WebFetch this drill, not
asserted from training memory):

- **Nelson & Narens (1990), monitoring/control framework** (*Metamemory: A
  Theoretical Framework and New Findings*, Psychology of Learning and Motivation 26)
  — splits cognition into an object-level (doing the task) and a meta-level (holding
  a model of it), linked by two DISSOCIABLE flows: monitoring (object -> meta) and
  control (meta -> object). This maps cleanly onto the USER-locked scope boundary
  itself: this cell's loop MONITORS (retrieves + compares) but explicitly does not
  CONTROL (it never rewrites the ledger or the cells it checks) — the
  monitoring/control dissociation is the literature's own name for exactly the
  boundary the USER wants preserved between "narrow self-check" and "self-rewriting."
- **Fleming, Weil, Nagy, Dolan, Rees (2010), *Science* 329(5998):1541-1543** —
  metacognitive accuracy about one's own decisions correlates with gray/white-matter
  structure in ANTERIOR (rostral) prefrontal cortex, anatomically distinct from
  regions supporting the first-order task itself. Analog: the audit loop is separate
  code/infra from the cells it checks, not a property of the cells' own computation.
- **Johnson & Raye (1981) *reality monitoring*, Johnson/Hashtroudi/Lindsay (1993)
  *source monitoring*** — the brain attributes a memory to its source via an
  INFERENTIAL judgment on trace qualities, and can misattribute when traces are
  insufficiently differentiated. Honest disanalogy: the substrate's retrieval leg
  does exact-key lookup, not inferential source-attribution; the free-text parse
  failures (cross-clause number joins, garbled shorthand) are structurally closer to
  a source-monitoring-style misattribution (the right number, wrongly bound to the
  wrong metric's threshold) than to an exact-lookup miss — a useful vocabulary for
  classifying WHY the audit leg's residual 16/915 false-parses occur, not a claim
  that the substrate implements anything like source monitoring.
- **Botvinick, Braver, Barch, Carter, Cohen (2001), *Psychological Review*
  108(3):624-652** and the 2004 TICS update — dorsal ACC signals response conflict
  (co-activated incompatible representations), triggering compensatory control; the
  closest functional analog to "op_agreement mismatch fires a flag." Caveat: ACC
  conflict-monitoring operates over competing CONTINUOUS/graded internal
  representations, evolved for effort/control allocation, not discrete symbolic
  ledger-consistency checking — mechanism-analog, not task-analog.
- **Koriat (1993), accessibility model of feeling-of-knowing, *Psychological
  Review* 100(4):609-639** — directly useful vocabulary for Q2: memory failures
  split into UNAVAILABLE (never stored — maps to the ledger-coverage/"blocking" gap)
  vs AVAILABLE-BUT-INACCESSIBLE (stored, retrieval blocked) vs a third,
  separately-documented failure mode of successful retrieval followed by faulty
  evaluation (maps to the audit leg's free-text misparse class). This
  three-way taxonomy (indexing/access failure, matching/evaluation failure,
  conflict-detection) is a genuinely useful, literature-grounded frame for exactly
  the two named limitations in the task — even though the underlying brain
  mechanisms are analog, graded, and evolved for effort-allocation under
  uncertainty, not discrete symbolic consistency-checking. That caveat is the
  honest boundary of the analogy; it is not claimed to transfer further.

---

## Cheap decisive test

Re-run the EXISTING `tools/back_fill_cert_ledger.py --audit-commit` (or a small,
same-pattern sweep extension iterating all historical atomize-commit shas) to
produce ONE number: what fraction of the 5744-950=4794 non-ledgered `exp_*` dirs are
genuine unprocessed atomize-backlog (recoverable by running the tool further) vs
legitimately-never-atomized (SMOKE-only / non-landed / negative-result cells that
were never meant to reach the ledger). This single, already-tooled, <1hr, zero-risk
audit discriminates between Q2's two candidate explanations (recoverable backlog vs
structural ceiling) before any further coverage-growth investment is made, and its
outcome directly determines whether lever (a) (grow ledger coverage) or lever (b)
(reframe the metric to query `metrics.json` directly) is the right next move.

---

## Falsifiable predictions

**HARD-PASS (the structured-field recommendation holds):**
- `structured_gate_claims` retrieval is exact (100% by construction; no regex) once
  `write_metrics(..., gate_claims=...)` is adopted by >=1 new cell.
- The backfill sidecar cleanly tags >=70% of the 654 existing files with >=1 named
  gate claim (measured this drill: 79.2% qualify — comfortably above this bar).
- Re-running the entailment cell's audit leg against the backfilled clean subset
  yields either 0 candidate-miscited claims (consistent with the current honest
  finding) or, if >0, every flagged case is inspectable via the structured field
  with zero "parse artifact" explanations required.

**HARD-FAIL (would falsify / rescope the recommendation):**
- If close per-file semantic review of a sample of the "named" 79.2% shows a
  material fraction (>30%) are STILL mis-bound (a captured `name=` that denotes the
  wrong metric, not just an unnamed number) — free-text is noisier than this drill's
  name-capture heuristic suggests, and the backfill portion (not the forward-going
  structured-field fix itself) should be abandoned or shrunk to a much smaller,
  manually-curated subset.
- If adopting `record_gate()`/`gate_claims` costs materially more than a few lines
  per cell (e.g. requires restructuring existing `classify()`-style verdict
  functions in ways that conflict with the CELL-TEMPLATE MANDATORY discipline) —
  the cost/benefit reverses and a lighter-weight convention should be sought instead.
- If the cheap decisive test (above) shows ledger non-coverage is structural (most
  of the 4794 gap is legitimately-never-atomized, not backlog) — lever (a)
  (coverage growth) is capped by design, not recoverable by running existing tooling
  further, and lever (b) (reframe the metric to query `metrics.json` directly)
  becomes the ONLY viable fix, not merely the prioritized one.

---

## THE INFRA SPEC (ready for exp_dev/testbed/skunkworks pickup — NOT a compute cell; no queue, no GPU)

1. **`experiments/_seed_checkpoint.py`** — add `record_gate(gate_name, measured,
   threshold, op, note=None)` helper (~15-20 lines, reuses the `eval_op` pattern
   already proven twice this session) + extend `write_metrics(out_dir, metrics,
   results=None, gate_claims=None)` to validate + store
   `metrics["structured_gate_claims"]` when supplied. Opt-in; zero migration cost
   for existing cells. Owner: `hdi_testbed` (shared infra) or `hdi_exp_dev` (cell
   authoring convention).
2. **CELL-TEMPLATE MANDATORY checklist** — add one bullet (structured_gate_claims
   convention). Recommend documenting once centrally (no single canonical checklist
   file currently exists — verified; it is copy-pasted per-cell as header comments)
   rather than leaving it to be re-derived per cell.
3. **`tools/backfill_structured_gate_claims.py`** (one-off, non-permanent, same
   convention as `tools/audit_full_coverage.py`) — read-only scan using the
   entailment cell's existing `_INEQ` regex (import verbatim, DRY), writes a
   SEPARATE sidecar `data/<exp_dir>/structured_gate_claims_backfill.json` per
   cleanly-all-named file (476 candidates measured this drill), routes the rest to a
   flat human-review list. Never touches existing `metrics.json`. Owner:
   `hdi_skunkworks` (audit-only role fits the human-review-gated framing) or
   `hdi_testbed`.
4. **Ledger-coverage sweep audit** (the cheap decisive test) — extend or re-run
   `tools/back_fill_cert_ledger.py --audit-commit` across the historical
   atomize-commit list. Owner: `hdi_skunkworks` (owns atomization) or `hdi_testbed`.
5. **Re-run, not a new cell**: `python experiments/exp_cert_ledger_numeric_entailment_v1.py --smoke`
   locally, after 1-3 land, to measure the strengthened smoke's audit-leg yield and
   the reframed retrieval metric (Q2). Same anchor; no new dispatch.

None of steps 1-5 require GPU/queue dispatch or propose the substrate rewriting its
own ledger, cells, or code — all are human/audit-run tooling that supplies BETTER
source data to the EXISTING narrow self-check loop. This preserves the USER-LOCKED
scope guardrail (narrow glass-box self-CHECK, NOT self-improvement or
self-rewriting) exactly as strictly as the landed cell itself does.

---

## CROSS-THREAD SYNTHESIS

- **With `notes/research_entailment_self_check_first_cell_2026-07-05.md`**: that
  note scoped Tier 0/1/2 and the comparator primitive that made this cell possible;
  this note picks up exactly where its "Tier 2, OPEN" section left off, now that
  Tier 2 has landed SMOKE HARD_PASS, and answers the two concrete weaknesses that
  note's own honest-limitation framing anticipated ("a reliable Tier-2 audit would
  need a STRUCTURED field").
- **With `exp_cert_ledger_self_query_v1`**: confirmed via direct metrics read
  (`data/exp_cert_ledger_self_query_v1_smoke/metrics.json`) that its KGStore
  multi-hop mechanism gets Task-A currency accuracy 1.000 when the target data IS in
  its graph — i.e., the substrate's own proven retrieval primitive is not the
  bottleneck anywhere in this picture; the bottleneck is upstream (ledger
  population), a distinction this drill's re-measurement makes explicit.
- **With `tools/audit_full_coverage.py`** (2026-06-28, verified on disk): the
  ledger-coverage gap this drill quantifies (950/5744 = 16.5%) is a previously
  audited, known systemic property, not a fresh finding — this drill's contribution
  is connecting it explicitly to THIS cell's `retrieval_hit_rate` metric and
  diagnosing (via external record-linkage literature) why no retrieval-algorithm
  swap can fix it.
- **With [[feedback-research-every-finding-for-mechanism-and-envelope-push]]**: the
  "weak retrieval" and "vacuous audit" findings are treated as mechanism clues
  (coverage vs representation) rather than a single undifferentiated complaint,
  each routed to its own fix.
- **With the "canon-1st" USER-locked discipline**: this drill's finding that the
  comparison pipeline currently bypasses the ledger entirely (reads `metrics.json`
  directly) is in mild tension with "substrate as canonical query first" — flagged
  as a documentation/design choice for the cell's next revision (Q2), not silently
  left as an undocumented discrepancy.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

- If the structured-field fix lands: every FUTURE cell's HARD-PASS/HARD-FAIL claims
  become machine-auditable by construction, with zero incremental parsing risk —
  directly reduces reliance on `hdi_skunkworks` manually re-reading
  `metric >= threshold -> verdict` bands by hand, the same product-facing value the
  sibling comparator note already identified for the underlying primitive.
- If the ledger-coverage cheap-decisive-test shows recoverable backlog: a bounded,
  already-tooled sweep meaningfully raises how much of the substrate's OWN certified
  history the self-check loop can exercise — a concrete, low-risk win independent of
  this cell.
- If the cheap-decisive-test instead shows the gap is structural: the honest product
  framing becomes "the self-check loop audits the substrate's raw computational
  record comprehensively; it audits the specifically-curated canonical ledger only
  partially, by design" — still a genuinely useful capability, just precisely scoped.
- Neither outcome reopens self-improvement/self-rewriting (USER-LOCKED): all
  recommended work is either (a) a metrics-writer convention future cells opt into,
  (b) a read-only/sidecar backfill script, or (c) an audit sweep using existing
  tooling — none propose the substrate modifying its own ledger, cells, or code.

---

## CITATIONS (verified external count = 18, plus substrate-internal artifacts)

**Brain / metacognition lit-scan (7 verified sources):**
1. Nelson, T.O. & Narens, L. (1990). "Metamemory: A Theoretical Framework and New
   Findings." *Psychology of Learning and Motivation*, 26, 125-173.
2. Fleming, S.M., Weil, R.S., Nagy, Z., Dolan, R.J., & Rees, G. (2010). "Relating
   Introspective Accuracy to Individual Differences in Brain Structure." *Science*,
   329(5998), 1541-1543.
3. Johnson, M.K. & Raye, C.L. (1981). "Reality Monitoring." *Psychological Review*,
   88(1), 67-85.
4. Johnson, M.K., Hashtroudi, S., & Lindsay, D.S. (1993). "Source Monitoring."
   *Psychological Bulletin*, 114(1), 3-28.
5. Botvinick, M.M., Braver, T.S., Barch, D.M., Carter, C.S., & Cohen, J.D. (2001).
   "Conflict Monitoring and Cognitive Control." *Psychological Review*, 108(3),
   624-652 (+ 2004 TICS update, Botvinick/Cohen/Carter, 8(12):539-546).
6. Koriat, A. (1993). "How Do We Know That We Know? The Accessibility Model of the
   Feeling of Knowing." *Psychological Review*, 100(4), 609-639.
7. Supporting: "don't remember" vs. "don't know" as behavioral markers distinguishing
   accessibility- from availability-based retrieval failure (PMC9813323, 2022/2023).

**Structured-logging / record-linkage lit-scan (11 verified sources):**
8. Zhu, J. et al. (2018/2019). "Tools and Benchmarks for Automated Log Parsing."
   arXiv:1811.03509.
9. He, P. et al. (2017). "Drain: An Online Log Parsing Approach with Fixed Depth
   Tree." ICWS 2017.
10. OpenTelemetry, "Logs Data Model" specification.
11. OpenTelemetry, "General logs attributes" semantic conventions.
12. Better Stack Community, "Why Structured Logging is Fundamental to Observability."
13. Fellegi, I.P. & Sunter, A.B. (1969). "A Theory for Record Linkage." *JASA*,
    64(328), 1183-1210.
14. Christen, P. (2012). *Data Matching: Concepts and Techniques for Record
    Linkage, Entity Resolution, and Duplicate Detection*. Springer.
15. Binette, O. & Steorts, R.C. (2022). "(Almost) All of Entity Resolution."
    *Science Advances*, 8(12), arXiv:2008.04643.
16. Christophides, V. et al. "End-to-End Entity Resolution for Big Data: A Survey."
    arXiv:1905.06397.
17. "Retrieval Metrics Tutorial: Recall@k and MRR Explained" (practitioner source,
    corroborating the general IR framing).
18. "Beyond Relevance: On the Relationship Between Retrieval and RAG Information
    Coverage." arXiv:2603.08819.

(Not verified / explicitly flagged by the lit-scan agents rather than asserted: an
author combination "Botvinick, Yeung, Cohen" for the ERN/ACC papers — the verified
Botvinick/Braver/Barch/Carter/Cohen and Botvinick/Cohen/Carter author lists were used
instead; and no single canonical term-of-art "index coverage recall" — the finding
is well-supported descriptively across items 13-16 but not under one exact phrase.)

**Substrate-internal (verified on disk this drill, not counted toward external
total but load-bearing):**
- `data/exp_cert_ledger_numeric_entailment_v1/metrics.json` (SMOKE, HARD_PASS,
  verified this drill: op_agreement=1.0, flag_recall=1.0, retrieval_hit_rate=0.145
  smoke-capped).
- `preregs/cert_ledger_numeric_entailment_v1_2026-07-05.md` (MEASURED corpus survey:
  654 files / 948 triples / 915 in-range).
- `data/exp_cert_ledger_self_query_v1_smoke/metrics.json` (SMOKE, HARD_PASS,
  Task A acc=1.000 — confirms the substrate's own retrieval mechanism is not the
  bottleneck).
- `data/substrate_index/meta/cert_ledger.jsonl` (1446 rows, 950 unique exp-keys —
  measured directly this drill).
- Direct re-measurement this drill (read-only scratch scripts, no repo writes):
  full-corpus retrieval_hit_rate = 0.100-0.108 (uncapped); 5744 `exp_*` dirs with
  `metrics.json` vs 950 ledgered; 79.1%/79.2%/72.8% named-triple/file statistics.
- `tools/audit_full_coverage.py` (2026-06-28 one-shot audit artifact, confirms the
  ledger-coverage gap was already characterized independently before this drill).
- `tools/back_fill_cert_ledger.py` (existing orphan-backfill tool; the recommended
  cheap decisive test reuses its `--audit-commit`/`--dry-run` machinery).
- `experiments/_seed_checkpoint.py` (the `write_metrics()` shared metrics-writer;
  MEASURED this drill: imported by 3485/4656 cells on disk).
- `experiments/exp_cert_ledger_numeric_entailment_v1.py`,
  `experiments/exp_cert_ledger_self_query_v1.py` (both read in full this drill).

---

*Research complete 2026-07-05. Field advisor run (no matching tracked field; noted,
consistent with sibling notes). Direct on-disk re-measurement performed via
read-only scratch scripts (no repo writes) before any external dispatch. 2 parallel
Sonnet lit-scans (metacognition/source-memory brain grounding; structured-logging
and record-linkage coverage-vs-matching distinction), generic terms only, no
substrate-novel mechanism names off-platform. Lit-scan calibration applied (deflate
0.15-0.25; novel-synthesis cap 0.50 — not invoked here since this drill's core
claims rest on direct on-disk re-measurement, not novel external synthesis).
HARD-FAIL thresholds specified. Design/recommendation only per Director instruction
— no cell built, no routing files (USER-locked ferry-deprecation override; all
actionable content, including the infra spec, delivered in this note).*
