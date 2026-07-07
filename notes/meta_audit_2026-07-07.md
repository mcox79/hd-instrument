# meta_audit 2026-07-07 — Integrity of the "what's-implemented" tracking system

**Scope**: XHIGH integrity audit, triggered by a real near-miss — a forward-map
drill flagged the refuse-gate 1D->2D controller as an OPEN load-bearing gap when
`cortex_refuse_gate_v9_joint_alpha_sigma` had already landed HARD_PASS on 2026-07-02.
exp_dev's mandatory concept-query-before-authoring caught the rediscovery before a
duplicate shipped. Question settled here: how reliable is our record of "what's
implemented," and are we at risk of forgetting/duplicating things?

**Prior audit**: `notes/meta_audit_2026-05-24.md` (6 weeks ago). No overlap with this
scope. Process note: meta_audit cadence has lapsed — this is the first audit in 44 days.

**Verification stance**: all numbers below are off-disk. Where a number could NOT be
verified I say so explicitly — the summary docs are the thing under audit, so they are
not treated as ground truth.

---

## 1. Source of truth — CONFIRMED

The canonical, append-only record is the cert store:
- `data/substrate_index/meta/cert_ledger.jsonl` — 1492 atoms, live: latest `ts_iso`
  `2026-07-07T22:02:37Z` (written today, during this audit window).
- `data/substrate_index/<partition>/atoms.jsonl` — math, concept, meta, verdict_history,
  results_history, decision_history, findings_history, research_history, methodology.

`PROGRESS.md` (91 lines, mtime 2026-07-04) and `notes/substrate_capability_map.md`
(29,618 lines) are **hand-maintained, lagging, curated snapshots** — not the record.
Confirmed by construction: a 91-line PROGRESS.md cannot carry 1492 atom-level results;
it is prose curation, and prose curation drifts.

### Worked example — the refuse-gate (as requested)
- **In the store since 07-02**: `refuse_gate_v9_joint_alpha_sigma_surface_controller_v1`
  present in `data/substrate_index/math/atoms.jsonl` (seeds 7/13/19) and in
  `cert_ledger.jsonl` (distinctive token `joint_alpha_sigma`: 1 hit).
- **PROGRESS.md**: Stage-1 line still reads "refuse-gate V_REL=256" (the OLD 1D gate).
  Zero mentions of v9 / joint_alpha_sigma. LAGGING.
- **cap_map**: 0 mentions of `joint_alpha_sigma` or `refuse_gate_v9`. It references
  "refuse-gate" only as a generic non-cosine-mechanism concept (v314 rows). LAGGING.

So **both** human-facing summaries missed the v9 controller; the store had it. The
near-miss was not a store failure — it was (a) a stale summary the drill trusted, and
(b) the drill not querying the store first.

### Drift magnitude
- **645 atoms** added to `cert_ledger.jsonl` in the last 14 days. None are individually
  traceable in the 91-line PROGRESS.md.
- PROGRESS.md's headline "Live Store CERT count: ~633 (floor, not re-counted)" is stale:
  structured query gives chain_grade=533, measured_mechanism=191 (=724 in the two
  headline tiers alone), plus null=183, under_classified=149, honest_negative=83, etc.
  The "~633" is a hand-carried number that has decoupled from the store.
- Drift is **architectural, not incidental**: summaries are curated prose; the store is
  the atom-level truth. There is currently no mechanism keeping them in sync, so drift
  is the default state, not an error.

---

## 2. Invisible-result risk — THE HEADLINE: currently UNMEASURABLE (and that is the finding)

The real forgetting-risk is a cell that LANDED + PASSED but never got a ledger atom.
I tried to measure it mechanically and hit a hard wall:

**The anchor->atom join is broken. 1382 of 1492 ledger atoms (92%) carry NO `anchor`
field.** Only 110 atoms (8%) record which experiment produced them. cert_ledger atom_ids
are long descriptive prose strings, not anchor-keyed. So there is **no reliable automated
way** to reconcile landed cells (`data/*/metrics.json`, keyed by anchor) against the
ledger.

Naive mechanical counts (reported for honesty, NOT trustworthy):
- Passed `metrics.json` dirs, mtime<14d: 2386; non-smoke: 1460; naive "no ledger atom": 877.
- After collapsing per-seed dirs + excluding selftest: 1823 distinct, 1247 "no atom",
  1245 of them >2d old.

These numbers are **inflated and not credible** as a forgetting-count. They are dominated
by (a) per-seed directory fan-out (`_seed7/_s13/_s19` each counted), (b) iterative
encoder-dev / migration runs that legitimately should NOT each earn a cert atom (only the
milestone atomizes), and (c) the broken join above.

**Honest measurement — hand spot-check on the consequential named landed HARD_PASS cells**
(distinctive-token search in the ledger):

| Landed cell (HARD_PASS, last 2wk) | ledger token | present? |
|---|---|---|
| refuse_gate **v9** joint_alpha_sigma | joint_alpha_sigma | YES (1) |
| probe_18 storage_advantage_boundary | storage_advantage_boundary / probe18 | YES (1/1) |
| encoder v11 gsbc graded-sparse | gsbc_graded | YES (3) |
| cortex2 provenance_faithfulness | provenance_faithfulness | YES (2) |
| calibrated refuse | calibrated_refuse | YES (2) |
| probe_4 storage_x_n | storage_x_n | YES (3) |

**Confirmed invisible-result count on the consequential sample: 0.** Every load-bearing
landed HARD_PASS I could name was atomized — just under a prose atom_id, not its anchor.

**But this cannot be certified system-wide.** With 92% of atoms lacking an anchor, I can
confirm presence for cells I already know to look for; I cannot enumerate what SHOULD be
there and isn't. The invisible-result rate is **unmeasurable with current metadata** — and
that unmeasurability, not any specific missing atom, is the genuine risk. Fix #1 below
exists precisely to make this measurable.

---

## 3. Semantic-query recall — FUNCTIONAL but thin-margin / lexical

Concept-query-before-dispatch/authoring uses `tools/director_kb_query.py`, encoder
`char_trigram_v1` (schema v2). Dispatch threshold cosine>0.30. Spot-test, known-built
capabilities:

| query (known-built) | top cosine | above 0.30? |
|---|---|---|
| refuse gate calibrated abstention 2D controller alpha sigma surface | 0.444 | YES |
| concept encoder sparse block code distillation BGE | 0.424 | YES |
| storage advantage boundary scales with N paired probe | 0.337 | YES (barely) |

**3/3 surfaced above threshold** — the safeguard that caught the refuse-gate rediscovery
is working (0.444 for that capability, comfortably clear).

**Caveat (silent-duplication risk)**: the encoder is `char_trigram_v1` — **lexical**
(character-trigram overlap), NOT semantic. Recall depends on the query sharing vocabulary
with the stored atom. Margins are thin (storage-boundary at 0.337, only +0.037 over the
gate). A capability queried with **paraphrased** vocabulary can drop below 0.30 and
silently miss. The safeguard is real but brittle to wording; it is not a semantic recall
guarantee.

---

## 4. Ranked durable fixes

**Fix 1 (HIGHEST LEVERAGE — unblocks everything else): anchor-key every atomization.**
Require `anchor` + `cell_commit` on EVERY `cert_ledger.jsonl` atom at write time (skunkworks
atomization step). Currently 8% coverage. Until this is fixed, landed-vs-ledger
reconciliation (Fix 4) is impossible and the invisible-result rate stays unmeasurable.
This is the root structural gap. Enforceable: atomization tool rejects an atom with no
`anchor`/`cell_commit`. Encoded as PROT-023 clause (a).

**Fix 2: auto-regenerate summary docs FROM the store on a cadence.** Make PROGRESS.md's
"current CERT count / Stage-N maturity" header and cap_map's tier tallies a **read-only
projection** generated nightly from `cert_ledger.jsonl` (a `tools/regen_progress_from_store.py`
job). Kills hand-maintained drift at its source — the refuse-gate-in-PROGRESS miss becomes
structurally impossible. Curated prose narrative can stay hand-written; the *counts and
capability-state rows* must be generated.

**Fix 3: elevate concept-query-before-dispatch to a Director hard gate.** Today the query
is enforced at exp_dev authoring (which caught this near-miss). Add it as a gate BEFORE
the Director dispatches any new load-bearing capability build: run the store query; if a
matching atom exists above cosine 0.30, reconcile (build-on / supersede / skip) before
shipping. Encoded as PROT-023 clause (b). Note the Fix-3 gate inherits the char-trigram
brittleness from Section 3 — pair it with a grep fallback on distinctive mechanism tokens.

**Fix 4: periodic landed-cells-vs-ledger reconciliation** (weekly meta_audit job): diff
passed `metrics.json` anchors against ledger `anchor` fields, list unmatched aged cells.
**Blocked on Fix 1** — worthless at 8% anchor coverage; becomes a clean tripwire once Fix 1
lands.

---

## 5. PROT change

**PROT-023 (NEW)** appended to active_protocols.md — anchor-keyed atomization (clause a) +
store-query-before-dispatch Director gate (clause b). Warranted: plugs a demonstrated
recurring failure mode (forgetting/duplication) with no existing PROT coverage, evidenced
by a real near-miss. Fixes 2 and 4 are tooling recommendations, not protocol rules, and
are left for exp_dev/skunkworks to implement.

## 6. Brief updates recommended
- `orchestrator_post_compaction_brief.md`: add "store is the ONLY source of truth;
  PROGRESS.md and cap_map are lagging snapshots — never trust their capability-state for a
  build/no-build decision, query the store" to the hard-rules / known-failure-modes section.

---

## What I could NOT verify
- The exact system-wide invisible-result count (Section 2) — blocked by the 92% missing-anchor
  join. Confirmed 0 on the consequential named sample; cannot certify beyond it.
- Whether every one of the 645 recent atoms is *correctly* tiered — out of scope; this audit
  checked presence/reconciliability, not per-atom tier correctness.
- Semantic recall across paraphrased queries — tested only vocabulary-overlapping phrasings;
  paraphrase-robustness (Section 3 caveat) is asserted from the encoder type, not swept.
