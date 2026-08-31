# FORWARD BACKLOG — the whole remaining body of work, sequenced + packageable

> **What this is (created 2026-08-31 on owner ask: "what is the body of work we need to complete, and
> have you mapped how it should be packaged for solvers?").** The single consolidated forward view. It
> POINTS to the living detail docs rather than duplicating them (which would rot):
> - **owed WIRINGS + islands** → `notes/WIRING_MAP.md` (the three debts; re-derive with `tools/wiring_debt.py`)
> - **the learner-on chain** → `notes/LEARNER_ON_ROADMAP.md`
> - **per-organ fidelity (PINNED vs INVENTED)** → `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (§1 headline, §2b log)
> - **the current assignable queue** → `notes/problems/*/PROBLEM.md` (a `priority:` line = live)
>
> Supersedes the STALE `notes/backlog.md` (an earlier native-reader/chain-drift phase — do not use it).
> Update IN PLACE: strike done, add discovered work, re-sequence on owner steer.

---

## THE ARC (one line)
`reader (built) → clean foundation (mostly done) → LEARNER-ON (in flight) → deeper brain-fidelity
(prediction-error, meaning) → PRODUCTION / converse (the long-horizon mission goal, barely started).`

The ultimate mission (CHARTER §1): a glass-box VSA/HDC substrate you can **CONVERSE** with that genuinely
**REASONS**, earning meaning + knowledge the brain's way. We have built the RECEPTIVE (reading) side deeply;
the EXPRESSIVE (speaking) side is essentially one file. So the body of work is: (1) finish + turn on
learning on a clean foundation [NOW], (2) close the biggest brain-fidelity gaps [NEXT], (3) build the
production side [the horizon].

---

## THE CRITICAL PATH (phases, sequenced by what blocks what)

### PHASE A — LEARNER-ON (the North Star). STATUS: IN FLIGHT.
The one thing that outranks everything. Detail: `LEARNER_ON_ROADMAP.md`.
- **p1 `turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation`** — the capstone. WIP (assigned).
- **OWED (mine, part of p1): the CLS keep-both-stores safe-growth switch** landed default-off (the safety
  mechanism that cuts corruption ~25.6%→7.85%). Specified but a coordinated program (see roadmap NEXT-STEP #2).
- **PACKAGEABLE (un-worked, roadmap-flagged): "define the foundation-cleanliness metric"** — the gate that
  decides WHEN growth may flip on. We have no single agreed "clean enough" measure. *Frame:* PINNED = a
  consolidation-eligibility / schema-congruence signal (p4's consistency score is a candidate); BAR = the
  metric separates a hand-seeded clean vs dirty store CI-sep, and its info-free twin does not. **Verify it
  isn't already covered before packaging.**

### PHASE B — FINISH THE ASSEMBLY (wire validated dimensions into the live reader). STATUS: ~half done.
The reader's situation model gains a dimension at a time, each additive/default-off. Detail: `WIRING_MAP.md`
DEBT 2. **Landed this arc:** who-did-what (quotative), CAUSATION, TIME, tense-preserving, verb_subcat
PRESENCE; IDENTITY (`graded_role_assigner`) is assembly-wired. **Remaining:**
- **p6 `the_reader_has_no_spatial_location_dimension_end_to_end` (SPACE)** — WIP. `sm.locations`; needs the
  motion-event parse adapter driving the promoted `location_register`.
- **PACKAGEABLE: ENTITIES(state)** — wire the (HOLDER,PROPERTY) entity-state dimension `state_register`
  (promoted) + the copular consumption p3 built (validated 0.94) into `sm.entity_states`. Modifies the coref
  re-rank → needs a no-regression witness.
- **PACKAGEABLE: BELIEF / ToM** — `belief_timeline` + `perceptual_access_ledger` (both promoted) → per-agent
  belief + observation gate; needs the observation-cue extraction adapter wired (spaCy-lazy). Additive,
  validated end-to-end (0.902 vs 0.463). *Note: the audit's "ToM absent" is now stale — it is BUILT, UNWIRED.*
- **OWED (mine): the GRADED verb_subcat gate** (the brain-faithful Competition-Model version, 0.30→0.49) —
  needs the reader to expose POS + the patient token index at role-assignment (mid-`_read_events` plumbing).
- **OWED (mine): the copular/nominal detector wiring** (offline WordNet event-noun asset + cop-arc front-end +
  `sm.entity_states`).
- **p4 `the_assembled_reader…all_flags_on`** — WIP. The VALIDATION GATE: run everything ON together, measure
  no-regression + aggregate gain + an interaction matrix. Gates trusting the whole.

### PHASE C — PREDICTION-ERROR HIERARCHY (the biggest fidelity-vs-wiring gap). STATUS: built, INERT. OWNER-DIRECTION-PENDING.
The brain's universal control signal (write-when-surprised, segment-at-surprise, predict-the-next-argument).
BUILT at 4 levels, but 3 are inert islands + the 1 wired node is ablation-ambiguous (audit §2b, 2026-08-31):
forward = `predictive_reader` (PINNED, held-out-validated, PURE INERT ISLAND — surprisal never computed live);
backward = `n400_coherence_monitor` (island); WM-gate = `slot_attention_wm` (island); novelty = `gap_detector`
(WIRED but does not demonstrably fire a decision — and it is the LEARN-GATE, so it is partly ON the Phase-A
critical path). *A COORDINATED program, not one brief.* **FIRST PACKAGEABLE STEP (can-fail):** wire the forward
surprisal into ONE downstream decision (write-gating or the relcl route-conflict) and PROVE the decision fires
CI-sep vs a shuffled-surprisal twin (a positive control that the gate actually gates). Needs owner DIRECTION
before packaging the rest.

### PHASE D — DEEPEN MEANING (the semantic read-out + control). STATUS: partial, mostly ISLANDS.
Detail: `WIRING_MAP.md` DEBT 3.
- **PACKAGEABLE/OWED: wire `meaning_fusion` into the live reader** — it now holds both meaning systems
  (associative + ATL identity, conceptual channel landed) but the live reader has NO word-meaning read-out at
  all. Landing the composed read-out is the remaining step.
- **OWED (mine): the p4 knowledge-store consistency-cleanup organ** over `hd_fact_store` (LOO-clean scorer +
  confidence tier + WordNet-densified). Clean-foundation store organ.
- **PACKAGEABLE: dedicated semantic control / meaning-selection** — the audit flags this "thin." Frame:
  context-conditioned sense selection is the brain's semantic-control (LIFG/ATL); a real gap on real prose.
- **OWED landings: the DEBT-3 meaning/memory islands** — scalar-magnitude channel, convergent-cue reader,
  the two-system factorized store, n400 monitor, transitive ordering.

### PHASE E — PRODUCTION / CONVERSE (the mission's expressive half). STATUS: barely started. THE HORIZON.
"A reader, not a speaker" (audit §1). To CONVERSE, the substrate needs an EXPRESSIVE side: generate an answer /
explanation from the situation model + knowledge store, glass-box, no LLM. This is a MAJOR multi-problem theme
(question→situation-model query is proven by `the_reader_cannot_answer_a_question_over_its_situation_model`, the
receptive end of it; production is the open end). **Sequence AFTER the learner + a trustworthy assembled reader
(you cannot speak faithfully from a foundation you have not validated).** Not packaged; a future phase.

### PHASE F — FOUNDATIONAL FIDELITY (ongoing, opportunistic).
- **The core binding operator** (FHRR) is UNPINNED-at-implementation but KEPT (owner 08-26, a defensible
  SEM/Franklin 2020 model). The live fidelity lever is STORE ORGANIZATION (dense→sparse/indexed), FHRR-compatible
  — an optimization theme, not a rebuild.
- **Corpus-age confound** (McGuffey→modern) — largely migrated; keep new evals on modern gold.
- These are opportunistic — surfaced by heartbeat scans, packaged when leverage is clear.

---

## HOW EACH SLICE GETS PACKAGED (the discipline)
Every solver brief is the 8-section format (README template) with: PINNED (the brain's operation to COPY) vs
OUR-INVENTION (the parameter to SWEEP); a can-fail BAR = CI-separated over the strongest REAL floor with the
info-free twin LOSING; the corpus-age + generalization checks; the `SOLVER OPERATING PROTOCOL` block verbatim;
and the `DO NOT QUOTE / DO NOT REDO` guard. A landing (my Q111 work) is NOT a solver brief — it is a witness +
default-off flag + registry row + WIRING_MAP fold.

**Solver-brief candidates vs my-landings (the split):** solver briefs = new mechanism / measurement (foundation-
cleanliness metric; ENTITIES-state; BELIEF/ToM adapter; prediction-error first step; semantic control;
production). My landings = wire an already-validated organ (graded verb_subcat; copular/nominal; meaning_fusion;
the DEBT-3 islands; the consistency-cleanup organ). The rule (owner, WIRE-DON'T-ISLAND): a validated organ is my
landing; a genuinely NEW capability or measurement is a solver problem.

---

## PRIORITY ORDER (my recommendation; owner re-ranks)
1. **Land the learner (Phase A)** — in flight; integrate on owner-DONE; land the CLS switch.
2. **Finish the assembly (Phase B)** — the owed who-did-what/extraction landings + SPACE/ENTITIES/BELIEF +
   the all-flags-on validation. This is the "clean, complete, trustworthy reader" the learner grows on.
3. **Prediction-error (Phase C)** — the highest-leverage FIDELITY gap; its `gap_detector` slice is already on
   the learner's path. Package the can-fail first step **on owner direction**.
4. **Deepen meaning (Phase D)** — wire the meaning read-out; semantic control.
5. **Production / converse (Phase E)** — the mission's second half; after a trustworthy reader + learner.

The queue is intentionally SMALL (3 live, all WIP) — over-filling is a failure mode. New briefs get packaged as
slots open or the owner opens a phase, not pre-emptively.
