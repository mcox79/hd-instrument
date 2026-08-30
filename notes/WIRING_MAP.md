# WIRING MAP — the single living "what we built vs what is actually WIRED" burn-down

> **Why this exists (owner, 2026-08-30):** *"Are you actually wiring these in, or just farming out
> problems, getting solutions, and putting them on a shelf? … since you compact context periodically,
> there is a real risk that things get forgotten over time."* This is the compaction-proof answer +
> the focused-address plan. It supersedes the ARC-era `capability_integration_ledger.md` (2026-07-28)
> for the current reasoning-organ wave; that older ledger recorded the SAME concern
> (*"we develop stuff and forget about it"*) — the fact that it keeps being re-discovered IS the risk.
>
> **ROT-PROOF:** regenerate the numbers any time with **`python tools/wiring_debt.py`** (`--full` for
> every item). It derives from `notes/problems/*/SOLVED.md`, `data/capability_registry.jsonl`, and the
> live reader's imports — so this map cannot silently go stale. The registry is the machine source of
> truth for per-organ status.

---

## THE HONEST STATUS (derived 2026-08-30 — `python tools/wiring_debt.py`)

- `hdlab/` holds **179 modules**; the **live reader + substrate import only ~19** of them.
- **80 integrated submissions:** 23 landed, **25 QUEUED** (earned a landing, not confirmed live),
  14 correct-no-landing (rigorous negatives), 18 unclear.
- **Registry: 235 capabilities.** 184 tagged `WIRED` — but that tag means *promoted+registered*, not
  *called at inference*. Strict test: **~9 reach the live reader/substrate; ~111 are island-only**
  (used only by their own experiments/witnesses). Plus 24 explicit `ISLAND`, 25 `TRAPPED_SHARED`, 2 shelved.

**Plain reading:** the *bookkeeping* is durable — organs are promoted, witnessed, registered, and NOT
lost. But "integrate" has been stopping short of "wire into the live reader," so the live substrate is
thin (~19 organs) while ~100 validated organs sit as default-off islands. **That is the debt this map
burns down.**

---

## THE THREE DEBTS (this is the real structure, reconciled against `hdlab/` on disk)

### DEBT 1 — PROMOTION debt (code still only in `experiments/`, never promoted to `hdlab/`)
Cleanest to clear: promote the spaCy-free core `experiments/X.py` → `hdlab/X.py`, default-off, add an
organ witness, register. Each is a self-contained strategy landing (Q111).

| Organ | Source | Wire-step | Note |
|---|---|---|---|
| ~~belief_timeline~~ ✅ **PROMOTED 2026-08-30** | `hdlab/belief_timeline.py` | DONE (default-off organ; witness `test_belief_timeline_organ.py` 11/11; exp file now a re-export shim). **Live-reader wiring still pending** (moves to DEBT 2 / the assembly) | first burn-down |
| ~~state_register~~ ✅ **PROMOTED 2026-08-30** | `hdlab/state_register.py` | DONE (surgical core-only split; witness `test_state_register_organ.py` 14/14; 61/61 unregressed; extraction stays exp-side). **Live-reader wiring pending** (DEBT 2, ENTITIES coref re-rank) | second burn-down |
| **temporal_order_register** | `experiments/_temporal_order_register.py` | multi-module port → hdlab (register + 2 shared modules + tagger dep) | TIME dimension; ~25 importers — careful |
| **perceptual_access_ledger** | `experiments/…perceptual_access…` | promote + extend belief_partition to a sequence ledger; must consume coref/situation organs so hdlab gains NO spaCy dep | the observation-cue front-end (the 0.098 belief-timeline live gap) |
| **CLS keep-both-stores growth** | `experiments/exp_growth_cls_ensemble_v1.py` | promote the keep-both-stores / rate-limited-blend growth mechanism, **default-OFF** | the learner-on roadmap's step-2 (see `LEARNER_ON_ROADMAP.md`) |

### DEBT 2 — WIRING debt / THE ASSEMBLY (promoted to `hdlab/` default-off, but the live reader never calls them)
The **biggest lever and the hard part**: these all edit `situation_reader`'s role/read path, so they
must be wired as ONE coordinated, measured effort (dimension by dimension) — NOT piecemeal. The
who-did-what slice already landed (quotative inversion, Change 1) and PROVED the pattern (0.551→0.798).

| Organ (in hdlab, default-off) | Wire target in the reader | Dimension |
|---|---|---|
| `force_dynamics_typer` | replace `_read_causation`'s untyped link with a TYPED CausalLink — **📦 PACKAGED as p2 `wire_the_causation_typer_into_the_live_reader`** (scoped to the within-clause domain; cross-sentence typing is the known dead lever) | CAUSATION |
| `graded_coref_pick` / graded retrieval + entropy-abstain | the coref resolution stream | ENTITIES(coref) |
| `location_register` | the SPACE serve (deletes the inline spaCy-proxy stopgap) | SPACE |
| `temporal_order_register` (once promoted) | before/after gating in the read | TIME |
| `state_register` (once promoted) | ENTITIES(state) re-rank of the coref pool | ENTITIES(state) |
| `belief_partition` + `perceptual_access_ledger` | per-agent belief + observation gate | GOALS/ToM |
| the register readout lines (`decode_serial`/`decode_gated`/`divnorm`) | the who-did-what event-set decode | ENTITIES |
| `incremental_parser` | replace the batch arc-parse candidate source behind a flag | PARSE |
| the who-did-what mislabel fix (quote-exclusion + speech-verb + core-mention) | `situation_reader`/`thematic_role_labeler` | ROLE |

**These are the coupled reader-wiring items behind ~10 of the 25 QUEUED landings.** They are the
substance of "an ever more complete substrate": each one measurably grows what the live reader can do.

### DEBT 3 — STANDALONE meaning/memory islands (promoted; the reader *could* consult them but doesn't)
Wire into the reader's meaning / entity read-out (some gated on the assembly landing first).

`scalar_adjective_operation` + `meaning_operation_router` + `fractional_power_encoding` (the p1 magnitude
channel) · `conceptual_meaning` · `convergent_cue_reader` (log-Bayes cue product) · `factorized_entity_store`
+ `graded_temporal_context` (the two-system store) · `n400_coherence_monitor` · `transitive_ordering`.

### NON-DEBT — correct no-landing (14 rigorous negatives; DO NOT re-attempt)
Recorded so they are never re-packaged. Newest: `causation_is_typed_per_clause_not_across_the_causal_network`
(discourse causal-network typing = a dead real-text lever); `the_discourse_fact_reasoner…` (world
knowledge net-zero on competitive coref); `teach_the_self_built_space…` (teaching does not rescue
retrieval). Full list: `python tools/wiring_debt.py --full`.

---

## THE FOCUSED-ADDRESS PLAN (sequenced by leverage × risk)

1. **Verify what we have still WORKS** (the owner's "make sure all the work is incorporated and working
   properly"). Run the organ-witness sweep (`verification/test_*_organ.py`); any FAIL = bit-rot to fix
   first (precedent: the `floor_battery` filename collision silently broke ~7 cells). Do this before
   building on top.
2. **Clear DEBT 1 (promotion) — cheap, safe, high-count.** Promote the ~5 experiments-only cores to
   `hdlab/` default-off + witness + register. Shrinks the debt fast and makes the code durable. Start
   with belief_timeline (fresh, clean, standalone).
3. **Land DEBT 2 (the assembly) — the real completion.** Wire the promoted role/dimension organs into
   the live reader, ONE dimension at a time, each measured end-to-end vs the positional/counting floor
   (the who-did-what slice is the template). This is a coordinated build = the natural next big PROBLEM,
   not a piecemeal strategy edit. **Highest leverage for "a more complete substrate."**
4. **Wire DEBT 3 (standalone meaning/memory)** into the meaning/entity read-out as the assembly opens
   the read points.
5. **Learner-on step-2** (DEBT 1's CLS growth) lands default-off in parallel (verdict-independent).

**Standing rule going forward (anti-forget):** every integration's `INTEGRATED_BY_STRATEGY` block must
say the landing STATE in these terms (promoted? live-wired? or QUEUED-with-target), and any QUEUED item
lands in this map. Re-derive with `tools/wiring_debt.py` on the maintenance cadence; a new island is a
tracked burn-down item, not a silent park.

---

## BURN-DOWN LOG (newest first)
- **2026-08-30** — **ASSEMBLY (DEBT 2) started:** packaged p2 `wire_the_causation_typer_into_the_live_reader` — the first
  "wire a promoted organ into the live reader" problem (CAUSATION), scoped to the typer's within-clause domain and respecting
  the integrated cross-sentence negative. Follows the who-did-what assembly template.
- **2026-08-30** — **PROMOTION debt −1 (#2):** state_register CORE promoted `experiments/` → `hdlab/state_register.py`
  (surgical core-only split matching hdlab/location_register.py; organ witness 14/14; 61/61 unregressed;
  spaCy extraction stays exp-side as a shim). Live-reader wiring pending (ENTITIES coref re-rank).
- **2026-08-30** — **verification sweep** of all 35 organ witnesses: **34 PASS, 0 FAIL, 1 TIMEOUT**
  (the parse-frontend witness needs >90s; not a failure). No bit-rot — the incorporated work runs.
- **2026-08-30** — **PROMOTION debt −1:** belief_timeline promoted `experiments/` → `hdlab/belief_timeline.py`
  (default-off, organ witness 11/11, exp file → re-export shim, registered). Live-reader wiring still pending.

## POINTERS (so this is never lost)
- **Refresh:** `python tools/wiring_debt.py [--full]`
- **Machine truth:** `data/capability_registry.jsonl` (per-organ `integration_status` + `gate_decision_target`)
- **Live path:** `hdlab/situation_reader.py` imports (the ~19 live organs)
- **Learner chain:** `notes/LEARNER_ON_ROADMAP.md` · **Brain fidelity:** `notes/BRAIN_FOUNDATIONAL_AUDIT.md`
- STATUS `POSITION` links here; MEMORY `[[wiring-map-burn-down]]` links here.
