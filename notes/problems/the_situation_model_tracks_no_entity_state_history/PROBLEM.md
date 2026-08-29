---
priority: 6
review:
review_text:
---

# PROBLEM: the situation model tracks entity IDENTITY (coref) and entity ROLES (who-did-what), but NOT entity STATE HISTORY — the prior/resultant STATES that perfect/stative aspect marks ("the house had been grand", "she had been ill", "he had been a soldier"). The just-integrated TIME solver MEASURED that 27% of real-LitBank "had…" pluperfects are copular/stative "had been X" (a prior STATE of an entity, NOT an event), and the extractor CORRECTLY skips them for event-ordering — but NOTHING consumes them: there is no per-entity state register, so the reader drops a large, high-incidence channel that the brain binds to the entity (Ferretti/Kutas/McRae 2007: perfect aspect feeds the ENTITY/state layer, not the order layer). This is a missing facet of Zwaan's ENTITIES dimension. Build a per-entity STATE-HISTORY register — read "had been X" (and resultant states from telic events) into each entity's prior-state record over intervals (reuse the SPACE `location_register`'s interval bookkeeping) — and validate it answers entity-state queries ("what state had X been in?" / "is X in state S here?") on real prose CI-separated over a no-state-history floor with the info-free twin losing.

**slug:** `the_situation_model_tracks_no_entity_state_history` — **opened:** 2026-08-29 by the strategy session (a MEASURED,
high-incidence gap EXPOSED by the integrated `situation_model_has_no_tested_temporal_order_comprehension`, owner-DONE/
EXCELLENT: its extraction-recall measurement found 27% of real pluperfects are stative "had been X" that the situation
model currently drops entirely). **status:** OPEN — a MECHANISM + BUILD problem (the entity-STATE facet of the ENTITIES
dimension). You build + validate in `experiments/`; strategy lands any hdlab change (Q111). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `6` — HIGH value and de-risked: a MEASURED
> high-incidence channel (27% of real "had"-pluperfects) with a PINNED brain basis (aspect→entity-state binding) that is
> currently ABSENT, and it REUSES a proven pattern (the SPACE `location_register`'s entity-interval bookkeeping — the same
> shape, a different attribute). It completes the ENTITIES dimension's state-tracking, which feeds meaning, coref (a
> prior state disambiguates a referent), and QA. Ranked below the in-flight assembly (p3) / parser (p8) / causation (p4)
> because those are the live reader's blockers, but it is the strongest UNPACKAGED dimension gap. **Dependency web:**
> composes with the ENTITY stack (coref supplies the entity key) + the TIME register (states hold over intervals);
> sibling of the SPACE location register. **Re-rank per the owner.**

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
Stories constantly tell you what STATE a character or thing is in or has been in — "the house had been grand," "she had
been ill," "he had been a soldier," "the door was now open." A reader files these as facts about that entity and uses them
later (the once-ill character is fragile; the once-grand house is now faded). Our reader throws them away: it correctly
notices these aren't *events* to be ordered, but it has nowhere to record them as an entity's *state*. And they're not
rare — over a quarter of the "had…" phrases in real books are exactly this kind of state description. Build a per-character
(and per-object) state record that reads these into a small history — what state each entity has been in, over what stretch
of the story — and show the reader can then answer state questions it currently can't.

## 2. WHY THIS ONE
It is a MEASURED, high-incidence gap (27% of real pluperfects), with a PINNED brain basis (perfect/stative aspect binds a
state to an entity — Ferretti/Kutas/McRae 2007), that is currently ABSENT from the substrate — and it is de-risked, because
it reuses a proven pattern: the SPACE `location_register` already tracks per-entity attributes over intervals (where an
entity is, when). State history is the same bookkeeping on a different attribute (what an entity IS/was). It completes the
ENTITIES dimension's state-tracking, which downstream meaning, coreference, and question-answering all lean on.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (the computation):** perfect/stative aspect marks a prior or resultant STATE and binds it to an ENTITY, held
  over an interval in the situation model (Zwaan-Radvansky ENTITIES dimension; Ferretti, Kutas & McRae 2007 — aspect feeds
  the entity/state layer, distinct from the event-order layer; the hippocampal-entorhinal system binds an attribute to an
  entity over a temporal context). A resultant state of a telic event ("the door opened" → the door IS-open thereafter) is
  the same construct from the event side.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the STATE-EXTRACTION rule (which "had been X" / copular / resultant
  patterns yield a state, and its value) and the interval-representation choice. **Copy the COMPUTATION** (bind the
  extracted state to the entity over an interval); **reuse** the `location_register` interval bookkeeping (same shape) and
  the coref entity key; SWEEP the extraction patterns + any confidence threshold.
- **NOT brain-faithful:** treating "had been X" as an EVENT to be time-ordered (the TIME organ correctly skips it — do NOT
  re-add it there); a global bag of states with no entity binding or interval (loses the "whose state, when"); an external
  LLM state extractor (the invariant).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE — do not re-derive):** `exp_temporal_order_extraction_recall_v1` (from the integrated TIME
  problem): of 139 spaCy-reference pluperfects on real LitBank, **27% are copular/stative "had been X"** (prior states),
  correctly skipped for ordering and currently consumed by NOTHING. The SPACE `location_register` (owner-DONE, EXCELLENT)
  is the proven per-entity interval-register pattern to reuse. Coref supplies the entity key.
- **INFERRED (to prove):** that a per-entity state-history register recovers entity-STATE queries on real prose ("what
  state had X been in?" / "is entity X in state S at this point?") CI-separated over a no-state-history floor (the reader
  without the register, e.g. nearest-mention/most-recent-adjective guess), with the info-free twin (shuffled state→entity
  or state→interval bindings) LOSING — OR a rigorous reason the states are too sparse/noisy to recover on real prose
  (quantified extraction coverage).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-order these as events (the TIME organ correctly SKIPS them — they are states, not events). Do NOT rebuild coref
  or the entity nodes (REUSE them for the entity key). Do NOT rebuild the interval bookkeeping — REUSE the SPACE
  `location_register` pattern (same interval shape, different attribute). Do NOT use an external LLM extractor.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `situation_model_has_no_tested_temporal_order_comprehension/adjacent_components_brain_fidelity_map_2026-08-29.md`
  (gap #1, the resultant/prior-STATE channel) + `experiments/exp_temporal_order_extraction_recall_v1.py` (the 27%
  measurement) + `hdlab/location_register.py` (the entity-interval pattern to reuse) + the ENTITY stack (coref → the entity
  key). Run `tools/experiment_index.py query "state"` / `"aspect"` / `"resultant"` / `"entity"` (SINGLE keywords). Audit:
  the newest §2b TIME entry (deviation (b): the dropped resultant-state channel). **Mind the CORPUS-AGE confound** — archaic
  copular constructions may parse differently; attribute extraction coverage honestly.

## 7. THE BAR
PASSES only with ALL of:
1. **A per-entity STATE-HISTORY register** (built in `experiments/`): reads "had been X" (and resultant states of telic
   events) into each entity's prior/current-state record over INTERVALS, keyed by the coref entity, reusing the
   `location_register` interval bookkeeping. Copy the computation; SWEEP the extraction patterns + threshold. NO external LLM.
2. **Answers entity-STATE queries on real prose CI-separated over a no-state-history floor** — a real-narrative population
   of state-decisive queries ("what state had X been in?" / "is X in state S here?"); the floor = the reader WITHOUT the
   register (nearest-mention / most-recent-adjective guess) recomputed on the same population. The **info-free twin**
   (shuffled state→entity or state→interval bindings) LOSES CI-separated; report CI half-width + null p95; no number crosses
   populations. A **POSITIVE control** the metric can move (a state-decisive case the register gets and the floor cannot).
3. **Isolates the state register from coref** (hold the entity clustering fixed, as the SPACE organ did) so the measured
   lift is the state-history register, not the entity linking.
4. **One-screen summary:** extraction coverage → floor → twin → state-query lift → verdict. Heavy → REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "a faithful state register recovers X% of state-decisive queries where the state
IS extracted, but real-prose extraction coverage is Y%, so the population lift is Z — a measured coverage bound, with the
positive control confirming the mechanism").

## 8. FILES AND ENTRY POINTS
- **Motivation + measurement (REUSE):** `situation_model_has_no_tested_temporal_order_comprehension/{adjacent_components_brain_fidelity_map_2026-08-29.md,
  SOLVED.md}`; `experiments/exp_temporal_order_extraction_recall_v1.py` (the 27% figure).
- **Reuse the pattern:** `hdlab/location_register.py` (per-entity interval bookkeeping — the same shape). **Compose:** the
  coref entity key; the TIME register (states hold over intervals). Audit + heavy→REMOTE (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`).

## DO NOT QUOTE / DO NOT REDO
The 27% figure is the MOTIVATION, not your result — build the register and measure entity-state recovery on real prose over
a no-state-history floor. Do NOT re-order states as events, rebuild coref, or rebuild the interval bookkeeping (reuse the
SPACE register). Strategy owns any hdlab landing.
